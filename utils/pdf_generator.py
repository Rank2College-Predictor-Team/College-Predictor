from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def generate_pdf(user_data, results, file_path):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "AKTU Counselling Report")

    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%d-%m-%Y')}")

    y -= 30

    # User Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Candidate Details")
    y -= 15

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Rank: {user_data['rank']}")
    y -= 15
    c.drawString(50, y, f"Category: {user_data['category']}")
    y -= 15
    c.drawString(50, y, f"Gender: {user_data['gender']}")
    y -= 15
    c.drawString(50, y, f"Home State: {user_data['home_state']}")

    y -= 30

    # Results Table Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Predicted Choices")
    y -= 20

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Choice")
    c.drawString(100, y, "College")
    c.drawString(260, y, "Branch")
    c.drawString(420, y, "Probability")

    y -= 15
    c.setFont("Helvetica", 10)

    for index, item in enumerate(results, start=1):
        if y < 50:
            c.showPage()
            y = height - 50

        c.drawString(50, y, str(index))
        c.drawString(100, y, item["college"][:25])
        c.drawString(260, y, item["branch"][:25])
        c.drawString(420, y, item["probability"])
        y -= 15

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(50, 30, "Disclaimer: Predictions are based on previous year AKTU data.")

    c.save()