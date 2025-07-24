# text_parsing_batch.py
import os
import re
from datetime import datetime
from pdfminer.high_level import extract_text

# === CONFIGURATION ===
input_root = "C:\\Users\\Lachmuth\\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\input"
output_root = "C:\\Users\\Lachmuth\\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\output"
log_file_path = os.path.join(output_root, "processing_log.txt")

# === FUNCTIONS ===
def clean_text(text):
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if re.match(r'^\s*(Figure|Fig\.|Table)\s+\d+', line, re.IGNORECASE):
            continue
        if re.match(r'^\s*Page\s+\d+', line, re.IGNORECASE):
            continue
        if re.match(r'^\s*\d+\s*$', line):
            continue
        cleaned_lines.append(line)

    cleaned_text = '\n'.join(cleaned_lines)
    cleaned_text = re.sub(r'\n{2,}', '\n\n', cleaned_text)
    cleaned_text = re.sub(r'(?<!\n)\n(?!\n)', ' ', cleaned_text)
    cleaned_text = re.sub(r'\s{2,}', ' ', cleaned_text)
    return cleaned_text.strip()

def extract_and_clean_pdf_text(pdf_path):
    try:
        raw_text = extract_text(pdf_path)
        return clean_text(raw_text), None
    except Exception as e:
        return None, str(e)

# === MAIN SCRIPT ===
if __name__ == "__main__":
    os.makedirs(output_root, exist_ok=True)

    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"\n=== Script run at {datetime.now()} ===\n")

        for subfolder in os.listdir(input_root):
            input_folder = os.path.join(input_root, subfolder)
            if not os.path.isdir(input_folder):
                continue

            output_folder = os.path.join(output_root, subfolder)
            os.makedirs(output_folder, exist_ok=True)

            log_file.write(f"\nProcessing input folder: {input_folder}\n")

            for filename in os.listdir(input_folder):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(input_folder, filename)
                    text, error = extract_and_clean_pdf_text(pdf_path)

                    if text:
                        base_name = os.path.splitext(filename)[0]
                        output_path = os.path.join(output_folder, f"{base_name}.txt")
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write(text)
                        log_file.write(f"SUCCESS: Processed {filename} → {output_path}\n")
                    else:
                        log_file.write(f"ERROR: Failed to process {filename} - {error}\n")

            # Log completion
            log_file.write(f"\nProcessing completed at {datetime.now()}\n")
            log_file.write(f"Total files processed: {len([f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')])}\n")
            log_file.write(f"Output folder: {output_folder}\n")
            log_file.write("=" * 40 + "\n")
            log_file.flush()
        print(f"Processing completed. Log saved to {log_file_path}")




