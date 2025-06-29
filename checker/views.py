import os
from django.shortcuts import render
from django.core.files.storage import default_storage
from .plagiarism_utils import calculate_similarity, extract_text_from_file

# Home page view
def home(request):
    return render(request, 'checker/home.html')

# Result page view
def result(request):
    if request.method == 'POST':
        user_text = request.POST.get('text1')
        full_path = None  # Initialize path for cleanup

        try:
            # If file is uploaded, extract text from it
            if 'uploaded_file' in request.FILES:
                uploaded_file = request.FILES['uploaded_file']
                file_path = default_storage.save(uploaded_file.name, uploaded_file)
                full_path = os.path.join(default_storage.location, file_path)
                user_text = extract_text_from_file(full_path)

            # If text exists (either from paste or file)
            if user_text:
                similarity_score = calculate_similarity(user_text)
                return render(request, 'checker/result.html', {'similarity': similarity_score})

        finally:
            # Delete the uploaded file after processing
            if full_path and os.path.exists(full_path):
                os.remove(full_path)

    # For GET requests or empty input
    return render(request, 'checker/result.html', {'similarity': None})
