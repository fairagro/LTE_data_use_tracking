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

    # Send the extracted text to the FastAPI endpoint
    response = requests.post(
        "http://127.0.0.1:8000/extract_metadata",
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
    pdf_file_path = "C:\\Users\\Lachmuth\\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\input\\V140_documented\\Thai&al_Agronomy_2020_MDPI.pdf" 
    analyze_pdf(pdf_file_path)