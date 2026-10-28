from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_counselling_report(candidate, predictions, choice_order):
    """Create a downloadable PDF report as bytes."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SmallMuted",
            parent=styles["BodyText"],
            fontSize=9,
            textColor=colors.HexColor("#4b5563"),
            leading=13,
        )
    )

    story = []
    story.append(Paragraph("AKTU College Predictor - Counselling Report", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))

    candidate_rows = [
        ["Rank", str(candidate["rank"])],
        ["Category", candidate["category"]],
        ["Gender", candidate["gender"]],
        ["Home State", candidate["home_state"]],
    ]
    candidate_table = Table(candidate_rows, colWidths=[1.8 * inch, 4.7 * inch])
    candidate_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#d1d5db")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(Paragraph("Candidate Details", styles["Heading2"]))
    story.append(candidate_table)
    story.append(Spacer(1, 0.2 * inch))

    prediction_rows = [["College", "Branch", "Closing Rank", "Status", "Probability"]]
    for item in predictions[:20]:
        prediction_rows.append(
            [
                item["college_name"],
                item["branch"],
                str(item["closing_rank"]),
                item["status"],
                item["probability"],
            ]
        )

    prediction_table = Table(
        prediction_rows,
        colWidths=[2.15 * inch, 2.25 * inch, 0.9 * inch, 0.7 * inch, 0.8 * inch],
        repeatRows=1,
    )
    prediction_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(Paragraph("Predicted Colleges", styles["Heading2"]))
    story.append(prediction_table)
    story.append(Spacer(1, 0.2 * inch))

    choice_rows = [["Order", "College", "Branch", "Probability"]]
    for item in choice_order[:15]:
        choice_rows.append(
            [
                str(item["choice_number"]),
                item["college_name"],
                item["branch"],
                item["probability"],
            ]
        )

    choice_table = Table(choice_rows, colWidths=[0.6 * inch, 2.55 * inch, 2.55 * inch, 1.0 * inch], repeatRows=1)
    choice_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(Paragraph("Suggested Choice Filling Order", styles["Heading2"]))
    story.append(choice_table)
    story.append(Spacer(1, 0.2 * inch))

    disclaimer = (
        "Disclaimer: This report is a prediction based on historical cutoff data and user inputs. "
        "Actual counselling outcomes can change because of seat availability, round progression, "
        "policy updates, and candidate preferences."
    )
    story.append(Paragraph(disclaimer, styles["SmallMuted"]))

    document.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
