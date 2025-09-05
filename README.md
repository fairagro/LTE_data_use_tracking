# 📄 LTE Metadata Extraction Tool

This repository provides a Python-based application for extracting structured metadata from scientific publications related to **Long-Term Experiments (LTEs)** in agriculture. It uses PDF parsing and a language model (LLM) to generate standardized metadata following [Schema.org](http://schema.org/) and agricultural domain standards.

---

## 🚀 Features

- 📚 Extracts bibliographic metadata from scholarly articles
- 🌱 Captures detailed LTE metadata including trial design, soil info, crop species, and variables measured
- 🧠 Uses LLM (e.g., OpenAI) for intelligent metadata extraction
- 📄 Converts PDF content to markdown for preprocessing
- 🔗 Outputs structured JSON metadata for integration with knowledge libraries or FAIR data systems

---

## 🧩 Repository Structure

xxx

## **⚙️ Requirements**

- Python 3.8+
- `fitz` (PyMuPDF)
- `fastapi`
- `httpx`
- `openai`
- `pydantic`
- `python-dotenv`

Install dependencies:

```bash
pip install -r requirements.txt
```

## **🔐 Environment Setup**

Create a `.env` file with the following variables:

```bash

LLM_API_KEY=your_api_key_here
LLM_API_ENDPOINT=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4

```

## **🧪 Usage**

### **1. Start the FastAPI server**

```bash
uvicorn modules_metadata_instructor:app --reload --port 8080
```

### **2. Run the extraction script**

```bash
python run_metadata_extraction.py
```

Make sure to update the `pdf_file_path` in `run_metadata_extraction.py` to point to your input PDF.

## **📦 Output**

- `extracted_markdown.md`: Intermediate markdown version of the PDF
- `llm_response_<timestamp>.json`: Final structured metadata
- `llm_debug_log.txt`: Raw LLM responses for debugging

## **📘 Metadata Standards**

The tool follows:

- Schema.org
- AGROVOC
- FAIR principles for agricultural data

---

## **🧠 Use Case**

This tool is part of a broader initiative to build a **knowledge library for LTEs**, supporting FAIR data practices and metadata standardization in agricultural research.

---

## **📬 Contact**

For questions or collaboration, please reach out to **Susanne Lachmuth (susanne.lachmuth@zalf.de)**.
