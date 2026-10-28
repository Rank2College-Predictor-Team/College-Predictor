from io import BytesIO
from uuid import uuid4

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from config import Config
from utils.analytics import (
    get_category_distribution,
    get_rank_distribution,
    get_recent_predictions,
    get_top_colleges,
    get_total_predictions,
    get_total_users,
    track_prediction,
)
from utils.pdf_generator import build_counselling_report
from utils.predictor import (
    SUBCATEGORY_OPTIONS,
    build_premium_results,
    get_free_results,
    validate_candidate_input,
)


app = Flask(__name__)
app.config.from_object(Config)


def get_or_create_user_id():
    """Ensure each browser session has a lightweight analytics id."""
    if "user_id" not in session:
        session["user_id"] = str(uuid4())
    return session["user_id"]


def get_candidate_session_data():
    """Return saved candidate inputs from the session."""
    return session.get("candidate")


@app.route("/", methods=["GET"])
def index():
    """Render the homepage form."""
    get_or_create_user_id()
    return render_template("index.html")


@app.route("/disclaimer", methods=["GET"])
def disclaimer():
    """Render the public disclaimer page."""
    return render_template("disclaimer.html")


@app.route("/privacy", methods=["GET"])
def privacy():
    """Render the public privacy page."""
    return render_template("privacy.html")


@app.route("/results", methods=["GET", "POST"])
def results():
    """
    Handle the prediction form flow.

    POST validates and stores form inputs in the session, then redirects to GET
    so the results page can also support GET-based subcategory filtering.
    """
    if request.method == "POST":
        form_data = {
            "rank": request.form.get("rank", "").strip(),
            "category": request.form.get("category", "").strip(),
            "gender": request.form.get("gender", "").strip(),
            "home_state": request.form.get("home_state", "").strip(),
        }

        is_valid, cleaned_data, error_message = validate_candidate_input(form_data)
        if not is_valid:
            flash(error_message, "error")
            return render_template("index.html", form_data=form_data), 400

        user_id = get_or_create_user_id()
        preview_results = get_free_results(cleaned_data)
        session["candidate"] = cleaned_data
        track_prediction(user_id, cleaned_data, preview_results["results"])
        return redirect(url_for("results"))

    candidate = get_candidate_session_data()
    if not candidate:
        flash("Please submit your details first to view predictions.", "error")
        return redirect(url_for("index"))

    subcategory = request.args.get("subcategory", "").strip().upper()
    results_data = get_free_results(candidate, subcategory_filter=subcategory)

    return render_template(
        "results.html",
        candidate=candidate,
        predictions=results_data["results"],
        subcategory=subcategory,
        subcategory_options=SUBCATEGORY_OPTIONS,
        available_subcategories=results_data["available_subcategories"],
        total_results=results_data["total_results"],
    )


@app.route("/premium-results", methods=["GET"])
def premium_results():
    """Show advanced predictions using the same stored session data."""
    candidate = get_candidate_session_data()
    if not candidate:
        flash("Premium prediction requires candidate details from the homepage.", "error")
        return redirect(url_for("index"))

    premium_data = build_premium_results(candidate)
    return render_template(
        "premium_results.html",
        candidate=candidate,
        predictions=premium_data["results"],
        choice_order=premium_data["choice_order"],
    )


@app.route("/download-pdf", methods=["GET"])
def download_pdf():
    """Generate a downloadable counselling report PDF."""
    candidate = get_candidate_session_data()
    if not candidate:
        flash("Please submit your details before downloading the report.", "error")
        return redirect(url_for("index"))

    premium_data = build_premium_results(candidate)
    pdf_bytes = build_counselling_report(
        candidate=candidate,
        predictions=premium_data["results"],
        choice_order=premium_data["choice_order"],
    )

    file_buffer = BytesIO(pdf_bytes)

    try:
        return send_file(
            file_buffer,
            as_attachment=True,
            download_name="aktu_college_predictor_report.pdf",
            mimetype="application/pdf",
        )
    except TypeError:
        return send_file(
            file_buffer,
            as_attachment=True,
            attachment_filename="aktu_college_predictor_report.pdf",
            mimetype="application/pdf",
        )


@app.route("/admin", methods=["GET"])
def admin_dashboard():
    """Render a simple password-protected admin analytics dashboard."""
    provided_key = request.args.get("key", "").strip()
    if provided_key != app.config["ADMIN_KEY"]:
        return render_template("admin_unauthorized.html"), 403

    category_distribution = get_category_distribution()
    most_selected_category = category_distribution[0] if category_distribution else ("N/A", 0)

    return render_template(
        "admin.html",
        total_users=get_total_users(),
        total_predictions=get_total_predictions(),
        top_colleges=get_top_colleges(),
        rank_distribution=get_rank_distribution(),
        category_distribution=category_distribution,
        most_selected_category=most_selected_category,
        recent_predictions=get_recent_predictions(),
    )


if __name__ == "__main__":
    app.run(debug=True)
