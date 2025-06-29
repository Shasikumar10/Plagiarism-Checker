import os
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import default_storage
from .plagiarism_utils import (
    calculate_similarity,
    extract_text_from_file,
    highlight_matches
)

# Home page view
def home(request):
    return render(request, 'checker/home.html')


# Result page view
def result(request):
    ref_text = "This is a reference text to compare for plagiarism."
    full_path = None  # For cleanup

    if request.method == 'POST':
        user_text = request.POST.get('text1')

        try:
            # Handle uploaded file
            if 'uploaded_file' in request.FILES:
                uploaded_file = request.FILES['uploaded_file']
                file_path = default_storage.save(uploaded_file.name, uploaded_file)
                full_path = os.path.join(default_storage.location, file_path)
                user_text = extract_text_from_file(full_path)

            if user_text:
                score = calculate_similarity(user_text)
                highlighted = highlight_matches(user_text, ref_text)
                unique_score = round(100 - score, 2)

                return render(request, 'checker/result.html', {
                    'similarity': score,
                    'highlighted': highlighted,
                    'unique_score': unique_score
                })

        finally:
            # Clean up uploaded file
            if full_path and os.path.exists(full_path):
                os.remove(full_path)

    return render(request, 'checker/result.html', {'similarity': None})


# Report download view
def download_report(request):
    if request.method == 'POST':
        score = request.POST.get('score')
        highlighted = request.POST.get('highlighted_text')

        content = f"Plagiarism Report\n\nSimilarity Score: {score}%\n\nHighlighted Text:\n\n{highlighted}"
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=\"plagiarism_report.txt\"'
        return response

    return HttpResponse("Invalid request method", status=405)
