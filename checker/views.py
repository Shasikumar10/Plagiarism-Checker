import os
from io import BytesIO
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import default_storage
from reportlab.pdfgen import canvas

from .plagiarism_utils import (
    calculate_similarity,
    extract_text_from_file,
    highlight_matches
)
import textstat


# Home page view
def home(request):
    return render(request, 'checker/home.html')


# Function to calculate readability score
def calculate_readability(text):
    return round(textstat.flesch_reading_ease(text), 2)


# Function to provide feedback based on similarity score
def get_feedback(score):
    if score >= 70:
        return "⚠️ High similarity – consider paraphrasing major parts."
    elif score >= 40:
        return "⚠️ Moderate similarity – reword similar sections."
    else:
        return "✅ Low similarity – your text looks original."


# Result view after plagiarism check
def result(request):
    ref_text = "This is a reference text to compare for plagiarism."
    full_path = None

    if request.method == "POST":
        user_text = request.POST.get("text1")

        try:
            # If file uploaded
            if 'uploaded_file' in request.FILES:
                uploaded_file = request.FILES['uploaded_file']
                file_path = default_storage.save(uploaded_file.name, uploaded_file)
                full_path = os.path.join(default_storage.location, file_path)
                user_text = extract_text_from_file(full_path)

            if user_text:
                similarity = calculate_similarity(user_text)
                highlighted = highlight_matches(user_text, ref_text)
                unique_score = round(100 - similarity, 2)
                readability = calculate_readability(user_text)
                feedback = get_feedback(similarity)

                return render(request, "checker/result.html", {
                    "similarity": similarity,
                    "highlighted": highlighted,
                    "unique_score": unique_score,
                    "readability": readability,
                    "feedback": feedback
                })

        finally:
            # Cleanup temporary uploaded file
            if full_path and os.path.exists(full_path):
                os.remove(full_path)

    return render(request, "checker/home.html")


# View to generate PDF report
def download_pdf_report(request):
    if request.method == 'POST':
        score = request.POST.get('score')
        text = request.POST.get('highlighted_text')

        # Prepare PDF buffer
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, "Plagiarism Report")

        # Score and timestamp
        p.setFont("Helvetica", 12)
        p.drawString(100, 770, f"Similarity Score: {score}%")
        p.drawString(100, 750, f"Checked On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Clean and add snippet
        cleaned_text = text.replace("<mark>", "").replace("</mark>", "")
        snippet = cleaned_text[:500]
        lines = [snippet[i:i+80] for i in range(0, len(snippet), 80)]

        y = 720
        p.setFont("Helvetica", 10)
        for line in lines:
            y -= 15
            if y < 50:
                p.showPage()
                y = 800
                p.setFont("Helvetica", 10)
            p.drawString(100, y, line)

        # Finalize and return response
        p.showPage()
        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf', headers={
            'Content-Disposition': 'attachment; filename="plagiarism_report.pdf"',
        })

    return HttpResponse("Invalid request method", status=405)
