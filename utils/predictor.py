import pandas as pd


def clean_rank(value):
    """Convert rank values such as '5,84,580' to 584580."""
    if pd.isna(value):
        return None
    try:
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def predict_colleges(rank, category, gender, home_state):
    df = pd.read_csv("data/aktu_cutoff.csv")

    # Clean column names first because the CSV contains spaces around some names.
    df.columns = df.columns.str.strip()

    df["Opening Rank"] = df["Opening Rank"].apply(clean_rank)
    df["Closing Rank"] = df["Closing Rank"].apply(clean_rank)

    # Quota filter
    quota = "Home State" if home_state == "UP" else "All India"
    df = df[df["Quota"].astype(str).str.strip() == quota]

    # Category filter
    category = str(category or "").strip()
    if category:
        df = df[df["Category"].astype(str).str.startswith(category)]

    # Gender filter
    gender = str(gender or "").strip()
    if gender == "Male":
        df = df[df["Gender"].astype(str).str.contains("Both", case=False, na=False)]
    elif gender == "Female":
        df = df[df["Gender"].astype(str).str.contains("Female|Both", case=False, regex=True, na=False)]

    results = []

    for _, row in df.iterrows():
        closing = row["Closing Rank"]
        if closing is None or pd.isna(closing) or closing <= 0:
            continue

        if rank <= closing * 0.8:
            tag = "Safe"
        elif rank <= closing:
            tag = "Moderate"
        else:
            tag = "Dream"

        results.append({
            "round": _clean_text(row["Round"]),
            "college": _clean_text(row["Institute"]),
            "branch": _clean_text(row["Program"]),
            "closing_rank": int(closing),
            "tag": tag,
            "subcategory": _clean_text(row["Category"]),
        })

    return results


# ---------- PREMIUM LOGIC (SEPARATE FUNCTIONS) ----------

def calculate_probability(rank, closing_rank):
    ratio = rank / closing_rank

    if ratio <= 0.7:
        return "Very High"
    elif ratio <= 0.85:
        return "High"
    elif ratio <= 1.0:
        return "Medium"
    else:
        return "Low"


def premium_prediction(rank, category, gender, home_state):
    basic_results = predict_colleges(rank, category, gender, home_state)

    for item in basic_results:
        item["probability"] = calculate_probability(
            rank, item["closing_rank"]
        )

    basic_results.sort(
        key=lambda x: ["Very High", "High", "Medium", "Low"].index(x["probability"])
    )

    return basic_results
