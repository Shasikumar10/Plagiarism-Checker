import os
import docx
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Function 1: Calculate similarity between user text and a reference text
def calculate_similarity(user_text):
    reference_text = "This is a reference text to compare for plagiarism."
    documents = [user_text, reference_text]
    tfidf = TfidfVectorizer().fit_transform(documents)
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])
    return round(score[0][0] * 100, 2)

# Function 2: Extract text from uploaded file (.txt, .docx, .pdf)
def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

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
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted
                return text

    except Exception as e:
        print("Error reading file:", e)

    return ""

# Function 3: Highlight words in user_text that match the reference text
def highlight_matches(user_text, ref_text):
    user_words = user_text.split()
    ref_words = set(ref_text.split())

    highlighted_text = []
    for word in user_words:
        if word in ref_words:
            highlighted_text.append(f"<mark>{word}</mark>")
        else:
            highlighted_text.append(word)

    return ' '.join(highlighted_text)
