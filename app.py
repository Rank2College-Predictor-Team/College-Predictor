from utils.pdf_generator import generate_pdf
from flask import send_file
import os
from flask import Flask, render_template, request
from utils.predictor import predict_colleges, premium_prediction
from flask import Flask, render_template, request, session, send_file
from flask import redirect, url_for

app = Flask(__name__)
app.secret_key = "aktu-secret-key-change-later"

# -----------------------------
# Configuration
# -----------------------------
PREMIUM_ENABLED = True


# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        rank = int(request.form.get("rank"))
    except:
        return "Invalid rank input", 400

    session["rank"] = rank
    session["category"] = request.form.get("category")
    session["gender"] = request.form.get("gender")
    session["home_state"] = request.form.get("home_state")

    return redirect(url_for("free_results"))

@app.route("/free-results")
def free_results():
    if "rank" not in session:
        return redirect(url_for("home"))

    # Read all prediction results first, then apply UI filters.
    all_results = predict_colleges(
        session["rank"],
        session["category"],
        session["gender"],
        session["home_state"]
    )

    # Filters
    selected_round = request.args.get("round", "").strip()
    selected_college = request.args.get("college", "").strip()
    selected_branch = request.args.get("branch", "").strip()
    selected_subcat = request.args.get("subcat", "").strip()

    filtered_results = all_results

    if selected_round:
        filtered_results = [
            r for r in filtered_results
            if r["round"].lower() == selected_round.lower()
        ]

    if selected_college:
        filtered_results = [
            r for r in filtered_results
            if r["college"] == selected_college
        ]

    if selected_branch:
        filtered_results = [
            r for r in filtered_results
            if r["branch"] == selected_branch
        ]

    if selected_subcat:
        filtered_results = [
            r for r in filtered_results
            if selected_subcat.lower() in r["subcategory"].lower()
        ]

    # Filter options are generated from the prediction result set, so users
    # only see values that are actually relevant to their rank/category.
    rounds = sorted(
        {r["round"] for r in all_results if r["round"]},
        key=lambda x: int(x.lower().replace("round", "").strip())
        if x.lower().replace("round", "").strip().isdigit() else x
    )
    colleges = sorted({r["college"] for r in all_results if r["college"]})
    branches = sorted({r["branch"] for r in all_results if r["branch"]})

    # Pagination: 20 result cards per page.
    per_page = 20
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1

    total_results = len(filtered_results)
    total_pages = max(1, (total_results + per_page - 1) // per_page)
    page = min(page, total_pages)

    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = filtered_results[start:end]

    # Keep filters while moving between pages.
    filter_params = {
        "round": selected_round,
        "college": selected_college,
        "branch": selected_branch,
        "subcat": selected_subcat,
    }

    return render_template(
        "results_free.html",
        results=paginated_results,
        selected_round=selected_round,
        selected_college=selected_college,
        selected_branch=selected_branch,
        selected_subcat=selected_subcat,
        rounds=rounds,
        colleges=colleges,
        branches=branches,
        page=page,
        total_pages=total_pages,
        total_results=total_results,
        showing_start=start + 1 if total_results else 0,
        showing_end=min(end, total_results),
        filter_params=filter_params,
    )


@app.route("/premium-results")
def premium_results():
    if not PREMIUM_ENABLED:
        return "Premium locked", 403

    # ✅ Get from session
    if "rank" not in session:
        return "Session expired. Please predict again."

    results = premium_prediction(
        session["rank"],
        session["category"],
        session["gender"],
        session["home_state"]
    )

    return render_template("results_premium.html", results=results)

@app.route("/download-pdf")
def download_pdf():
    if "rank" not in session:
        return "Session expired. Please predict again."

    user_data = {
        "rank": session["rank"],
        "category": session["category"],
        "gender": session["gender"],
        "home_state": session["home_state"]
    }

    results = premium_prediction(
        user_data["rank"],
        user_data["category"],
        user_data["gender"],
        user_data["home_state"]
    )

    file_path = "aktu_counselling_report.pdf"
    generate_pdf(user_data, results, file_path)

    return send_file(
        file_path,
        as_attachment=True,
        attachment_filename="AKTU_Counselling_Report.pdf"
    )

@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)