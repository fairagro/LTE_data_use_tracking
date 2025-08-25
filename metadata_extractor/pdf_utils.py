import fitz
import re

def extract_and_format_pdf_to_markdown(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    markdown_lines = []

    for page in doc:
        text = page.get_text("text")
        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            if re.search(r'(CC[- ]BY|Creative Commons|License|Copyright)', line, re.IGNORECASE):
                markdown_lines.append(line)
                continue

            if re.match(r'^\s*(Page\s+\d+|All rights reserved.*)$', line, re.IGNORECASE):
                continue

            if re.match(r'^\s*(Figure|Fig\.|Table)\s*\d+[:.]?', line, re.IGNORECASE):
                continue

            if re.match(r'^\d+\s*$', line):
                continue

            if re.match(r'^[A-Z][A-Z\s\-]{3,}$', line):
                markdown_lines.append(f"\n## {line.title()}\n")
            else:
                markdown_lines.append(line)

    markdown_text = ' '.join(markdown_lines)
    markdown_text = re.sub(r'\s{2,}', ' ', markdown_text)
    return markdown_text.strip()
