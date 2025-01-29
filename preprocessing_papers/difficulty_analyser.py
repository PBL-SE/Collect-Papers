import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import requests
import PyPDF2
from io import BytesIO

def download_and_extract_text(pdf_url):
    """Downloads a PDF from a URL and extracts its text."""
    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()
        
        with BytesIO(response.content) as pdf_buffer:
            reader = PyPDF2.PdfReader(pdf_buffer)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text.strip()
    except Exception as e:
        print(f"Error downloading/extracting PDF: {e}")
        return ""

def classify_paper(text):
    """Classifies a research paper's readability level using a Transformer model."""
    model_name = "  "
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=4)
    
    inputs = tokenizer(text, truncation=True, padding=True, max_length=512, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
        prediction = torch.argmax(logits, dim=1).item()
    
    labels = {0: "Beginner", 1: "Intermediate", 2: "Pro", 3: "Expert"}
    return labels[prediction]

# Example usage
pdf_url = "http://arxiv.org/pdf/cs/0607110v1"  # Replace with an actual PDF link
text = download_and_extract_text(pdf_url)
if text:
    category = classify_paper(text)
    print(f"Predicted Readability Level: {category}")
