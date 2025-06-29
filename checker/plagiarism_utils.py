from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import docx
import os

# Function 1: Calculate similarity
def calculate_similarity(user_text):
    sample_text = "This is a reference text to compare for plagiarism."
    documents = [user_text, sample_text]
    tfidf = TfidfVectorizer().fit_transform(documents)
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])
    return round(score[0][0] * 100, 2)

# Function 2: Extract text from uploaded file
def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1]

    try:
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif ext == '.docx':
            doc = docx.Document(file_path)
            return '\n'.join([p.text for p in doc.paragraphs])

        elif ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
    except Exception as e:
        print("Error reading file:", e)
    
    return ""
