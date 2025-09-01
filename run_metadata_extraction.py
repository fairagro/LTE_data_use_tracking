import sys
import os
import requests

# Add the project directory to Python path
project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_dir)

from metadata_extractor.pdf_utils import extract_and_format_pdf_to_markdown

def analyze_pdf(pdf_path):
    # Extract and format the PDF content
    markdown_text = extract_and_format_pdf_to_markdown(pdf_path)

    # Save the markdown to a file for inspection
    with open("extracted_markdown.md", "w", encoding="utf-8") as f:
        f.write(markdown_text)

    print("📄 Extracted markdown saved to 'extracted_markdown.md'")

    # Send the extracted text to the FastAPI endpoint
    response = requests.post(
        "http://127.0.0.1:8080/extract_metadata",
        json={"text": markdown_text}
    )

    # Print the JSON response
    if response.status_code == 200:
        print("✅ Metadata extraction successful:")
        print(response.json())
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

# Example usage
if __name__ == "__main__":
    pdf_file_path = "C:\\Users\\Lachmuth\\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\input\\Westerfeld_documented\\Raab&al_ScientificData_2025_CCBY4-0.pdf" 
    analyze_pdf(pdf_file_path)