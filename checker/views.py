from django.shortcuts import render
from .plagiarism_utils import calculate_similarity

def home(request):
    return render(request, 'checker/home.html')

def result(request):
    if request.method == 'POST':
        text = request.POST.get('text1')
        score = calculate_similarity(text)
        return render(request, 'checker/result.html', {'similarity': score})
    return render(request, 'checker/result.html')
