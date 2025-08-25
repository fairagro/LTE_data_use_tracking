# -----------------------------# PDF Text Extraction Functionality
# This section provides a utility to read and extract text from PDF
# Function to read PDF text using PyPDF2
import re

def clean_text(text: str) -> str:
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue
        # Preserve license/copyright info
        if re.search(r'(CC[- ]BY|Creative Commons|License|Copyright)', line, re.IGNORECASE):
            cleaned_lines.append(line)
            continue

        # Remove common headers/footers
        if re.match(r'^\s*(Page\s+\d+|All rights reserved.*)$', line, re.IGNORECASE):
            continue

        # Remove figure/table captions
        if re.match(r'^\s*(Figure|Fig\.|Table)\s*\d+[:.]?', line, re.IGNORECASE):
            continue

        # Remove lines that are just numbers (e.g., page numbers)
        if re.match(r'^\d+\s*$', line):
            continue

        # Remove lines that are likely section headings (optional)
        if re.match(r'^[A-Z][A-Z\s\-]{3,}$', line):
            continue

        cleaned_lines.append(line)

    # Join lines and normalize whitespace
    cleaned_text = ' '.join(cleaned_lines)
    cleaned_text = re.sub(r'\s{2,}', ' ', cleaned_text)

    return cleaned_text.strip()
def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        # Use PyPDF2 to read the PDF file
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path}: {e}")
        return ""

def extract_and_clean_pdf_text(pdf_path: str) -> (Optional[str], Optional[str]):
    try:
        raw_text = extract_text_from_pdf(pdf_path)
        if not raw_text:
            return None, "No text extracted from PDF."
        return clean_text(raw_text), None
    except Exception as e:
        return None, str(e)



pdf_path = "path/to/your/file.pdf"
pdf_text = extract_and_clean_pdf_text(pdf_path)