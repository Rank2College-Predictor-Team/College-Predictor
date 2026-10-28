import re
from functools import lru_cache

import pandas as pd

from config import Config


SUBCATEGORY_OPTIONS = [
    {"value": "AF", "label": "Armed Forces (AF)"},
    {"value": "FF", "label": "Freedom Fighter (FF)"},
    {"value": "GIRL", "label": "Girl"},
    {"value": "PH", "label": "PH"},
    {"value": "TF", "label": "Tuition Fee Waiver (TF)"},
    {"value": "GL", "label": "GL"},
]


def normalize_rank(value):
    """Convert rank text like '1,23,456' into an integer."""
    cleaned = str(value).strip().replace(",", "")
    return int(cleaned)


def normalize_user_category(category):
    """Map user-facing categories to dataset base categories."""
    category = str(category).strip().upper()
    if category == "OBC":
        return "BC"
    return category


def extract_base_category(category_text):
    """Return the base category from values such as OPEN(AF) or EWS(OPEN)."""
    category_text = str(category_text).strip().upper()
    return category_text.split("(")[0].strip()


def extract_subcategory(category_text):
    """Return the bracketed subcategory, normalized for filtering."""
    category_text = str(category_text).strip()
    match = re.search(r"\((.*?)\)", category_text)
    if not match:
        return ""

    subcategory = match.group(1).strip().upper()
    if subcategory == "OPEN":
        return ""
    if subcategory == "GIRL":
        return "GIRL"
    return subcategory


def format_subcategory(category_text):
    """Return a readable subcategory label for UI display."""
    subcategory = extract_subcategory(category_text)
    if not subcategory:
        return "General"
    if subcategory == "GIRL":
        return "Girl"
    return subcategory


def normalize_gender(gender):
    return str(gender).strip().lower()


def normalize_home_state(home_state):
    return str(home_state).strip().upper()


def expected_quota(home_state):
    """Map the form input to the dataset quota."""
    return "Home State" if normalize_home_state(home_state) == "UP" else "All India"


def allowed_gender_values(user_gender):
    """Male can use only both-seat rows; female can use female or both-seat rows."""
    normalized_gender = normalize_gender(user_gender)
    if normalized_gender == "female":
        return {"Female Seats", "Both Male and Female Seats"}
    return {"Both Male and Female Seats"}


def validate_candidate_input(form_data):
    """Validate the submitted form and return cleaned session-safe data."""
    allowed_categories = {"OPEN", "OBC", "SC", "ST", "EWS"}
    allowed_genders = {"Male", "Female"}
    allowed_home_states = {"UP", "Other"}

    try:
        rank = normalize_rank(form_data.get("rank", ""))
    except (TypeError, ValueError):
        return False, None, "Please enter a valid numeric rank."

    if rank <= 0:
        return False, None, "Rank must be greater than zero."

    category = str(form_data.get("category", "")).strip().upper()
    gender = str(form_data.get("gender", "")).strip().title()
    raw_home_state = str(form_data.get("home_state", "")).strip()
    home_state = "UP" if raw_home_state.upper() == "UP" else "Other"

    if category not in allowed_categories:
        return False, None, "Please choose a valid category."
    if gender not in allowed_genders:
        return False, None, "Please choose a valid gender."
    if home_state not in allowed_home_states:
        return False, None, "Please choose a valid home state option."

    return True, {
        "rank": rank,
        "category": category,
        "gender": gender,
        "home_state": home_state,
    }, None


@lru_cache(maxsize=1)
def load_cutoff_data():
    """Load and clean the CSV once, then reuse it across requests."""
    dataframe = pd.read_csv(Config.DATA_FILE)
    dataframe.columns = [column.strip() for column in dataframe.columns]

    text_columns = ["Round", "Institute", "Program", "Stream", "Quota", "Category", "Gender", "Remark"]
    for column in text_columns:
        if column in dataframe.columns:
            dataframe[column] = dataframe[column].fillna("").astype(str).str.strip()

    dataframe["Opening Rank"] = dataframe["Opening Rank"].astype(str).str.replace(",", "", regex=False).str.strip()
    dataframe["Closing Rank"] = dataframe["Closing Rank"].astype(str).str.replace(",", "", regex=False).str.strip()
    dataframe["Opening Rank"] = pd.to_numeric(dataframe["Opening Rank"], errors="coerce")
    dataframe["Closing Rank"] = pd.to_numeric(dataframe["Closing Rank"], errors="coerce")
    dataframe = dataframe.dropna(subset=["Closing Rank"]).copy()

    dataframe["Closing Rank"] = dataframe["Closing Rank"].astype(int)
    dataframe["Opening Rank"] = dataframe["Opening Rank"].fillna(0).astype(int)
    dataframe["Base Category"] = dataframe["Category"].apply(extract_base_category)
    dataframe["Subcategory Code"] = dataframe["Category"].apply(extract_subcategory)
    dataframe["Subcategory Label"] = dataframe["Category"].apply(format_subcategory)

    return dataframe


def classify_status(user_rank, closing_rank):
    """Classify the chance as Safe, Moderate, or Dream."""
    if user_rank <= 0.8 * closing_rank:
        return "Safe"
    if user_rank <= closing_rank:
        return "Moderate"
    return "Dream"


def probability_from_rank(user_rank, closing_rank):
    """Convert rank comparison into a premium probability label."""
    if closing_rank <= 0:
        return "Low", 1

    ratio = user_rank / closing_rank
    if ratio <= 0.65:
        return "Very High", 4
    if ratio <= 0.8:
        return "High", 3
    if ratio <= 1.0:
        return "Medium", 2
    return "Low", 1


def filter_cutoff_rows(candidate):
    """Apply category, gender, and quota filters to the cleaned dataset."""
    dataframe = load_cutoff_data()
    category = normalize_user_category(candidate["category"])
    quota = expected_quota(candidate["home_state"])
    gender_values = allowed_gender_values(candidate["gender"])

    filtered = dataframe[
        (dataframe["Base Category"] == category)
        & (dataframe["Quota"] == quota)
        & (dataframe["Gender"].isin(gender_values))
    ].copy()

    return filtered.sort_values(by=["Closing Rank", "Institute", "Program"], ascending=[False, True, True])


def build_result_record(row, user_rank):
    """Convert a dataframe row into a render-ready prediction record."""
    status = classify_status(user_rank, int(row["Closing Rank"]))
    probability, probability_score = probability_from_rank(user_rank, int(row["Closing Rank"]))

    return {
        "college_name": row["Institute"],
        "branch": row["Program"],
        "quota": row["Quota"],
        "closing_rank": int(row["Closing Rank"]),
        "opening_rank": int(row["Opening Rank"]),
        "category": row["Category"],
        "subcategory_code": row["Subcategory Code"],
        "subcategory_label": row["Subcategory Label"],
        "seat_gender": row["Gender"],
        "round": row["Round"],
        "status": status,
        "probability": probability,
        "probability_score": probability_score,
    }


def get_free_results(candidate, subcategory_filter=""):
    """Return free prediction results with optional GET-based subcategory filtering."""
    user_rank = int(candidate["rank"])
    filtered_rows = filter_cutoff_rows(candidate)
    results = [build_result_record(row, user_rank) for _, row in filtered_rows.iterrows()]
    total_results = len(results)

    available_subcategories = sorted({result["subcategory_code"] for result in results if result["subcategory_code"]})

    if subcategory_filter:
        results = [result for result in results if result["subcategory_code"] == subcategory_filter]

    return {
        "results": results,
        "available_subcategories": available_subcategories,
        "total_results": total_results,
    }


def build_premium_results(candidate):
    """Return enhanced predictions and a counselling-friendly choice order."""
    free_results = get_free_results(candidate)
    ranked_results = sorted(
        free_results["results"],
        key=lambda item: (
            -item["probability_score"],
            -item["closing_rank"],
            item["college_name"],
            item["branch"],
        ),
    )

    choice_order = []
    for index, item in enumerate(ranked_results, start=1):
        choice_item = item.copy()
        choice_item["choice_number"] = index
        choice_order.append(choice_item)

    return {
        "results": ranked_results,
        "choice_order": choice_order,
    }
