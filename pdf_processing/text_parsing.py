# Text parsing script
import os
import re
from pdfminer.high_level import extract_text

# === CONFIGURATION ===
input_folder = "C:\\Users\\Lachmuth\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\input\\Westerfeld_documented"         # Folder containing input PDFs
output_folder = "C:\\Users\\Lachmuth\\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\output"       # Folder to save cleaned text files

# === FUNCTIONS ===
def clean_text(text):
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def extract_and_clean_pdf_text(pdf_path):
    try:
        raw_text = extract_text(pdf_path)
        return clean_text(raw_text)
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

# === MAIN SCRIPT ===
if __name__ == "__main__":
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            text = extract_and_clean_pdf_text(pdf_path)
            if text:
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_folder, f"{base_name}.txt")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Processed: {filename} → {output_path}")
            else:
                print(f"Skipped: {filename}")

