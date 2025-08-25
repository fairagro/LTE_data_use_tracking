import os

# Create directory structure
os.makedirs("metadata_extractor", exist_ok=True)

# Create config.py
with open("metadata_extractor/config.py", "w") as f:
    f.write('''import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
API_ENDPOINT = os.getenv("LLM_API_ENDPOINT")

if not API_KEY or not API_ENDPOINT:
    raise RuntimeError("LLM_API_KEY and LLM_API_ENDPOINT must be set in the environment variables.")
''')

# Create models.py
with open("metadata_extractor/models.py", "w") as f:
    f.write('''from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel

class StrictBaseModel(PydanticBaseModel):
    class Config:
        anystr_strip_whitespace = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "forbid"

class Author(StrictBaseModel):
    name: str
    affiliation: Optional[str]

class Journal(StrictBaseModel):
    name: str
    issn: Optional[str]
    publisher: Optional[str]

class CitationMetadata(StrictBaseModel):
    title: str
    authors: List[Author]
    journal: Journal
    volume: Optional[str]
    issue: Optional[str]
    pages: Optional[str]
    doi: Optional[str]
    pubmed_id: Optional[str]
    publication_date: Optional[str]
    year: Optional[int]
    abstract: Optional[str]
    keywords: List[str]
    subject_classifications: List[str]
    language: Optional[str]
    license: Optional[str]
    open_access: Optional[bool]
    funding: Optional[str]
    formatted_citation: Optional[str]

class GeoCoverage(StrictBaseModel):
    lat1: float
    lon1: float
    lat2: Optional[float]
    lon2: Optional[float]

class Variable(StrictBaseModel):
    name: str
    description: str
    unit: Optional[str]
    vocabulary: Optional[str] = "AGROVOC"

class LTEDataMetadata(StrictBaseModel):
    name: str
    description: Optional[str]
    geographic_coverage: Optional[GeoCoverage]
    temporal_coverage: Optional[str]
    variables: List[Variable]
    dataset_doi: Optional[str]
    format: Optional[str]
    size: Optional[str]
    access_conditions: Optional[str]
    trial_status: Optional[str]
    experimental_setup: Optional[str]
    research_objectives: Optional[str]

class MetadataExtractionResponse(StrictBaseModel):
    citation: CitationMetadata
    datasets: List[LTEDataMetadata]
    reasoning: Optional[str]
''')

# Create pdf_utils.py
with open("metadata_extractor/pdf_utils.py", "w") as f:
    f.write('''import fitz
import re

def extract_and_format_pdf_to_markdown(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    markdown_lines = []

    for page in doc:
        text = page.get_text("text")
        lines = text.split('\\n')

        for line in lines:
            line = line.strip()

            if re.search(r'(CC[- ]BY|Creative Commons|License|Copyright)', line, re.IGNORECASE):
                markdown_lines.append(line)
                continue

            if re.match(r'^\\s*(Page\\s+\\d+|All rights reserved.*)$', line, re.IGNORECASE):
                continue

            if re.match(r'^\\s*(Figure|Fig\\.|Table)\\s*\\d+[:.]?', line, re.IGNORECASE):
                continue

            if re.match(r'^\\d+\\s*$', line):
                continue

            if re.match(r'^[A-Z][A-Z\\s\\-]{3,}$', line):
                markdown_lines.append(f"\\n## {line.title()}\\n")
            else:
                markdown_lines.append(line)

    markdown_text = ' '.join(markdown_lines)
    markdown_text = re.sub(r'\\s{2,}', ' ', markdown_text)
    return markdown_text.strip()
''')

# Create llm_client.py
with open("metadata_extractor/llm_client.py", "w") as f:
    f.write('''import requests
from .config import API_KEY, API_ENDPOINT

def call_llm_with_prompt(prompt: str, text: str) -> dict:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {
        "prompt": prompt,
        "input": text,
        "output_format": "json"
    }
    response = requests.post(API_ENDPOINT, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
''')

# Create prompts.py
with open("metadata_extractor/prompts.py", "w") as f:
    f.write('''SYSTEM_PROMPT = """You are an expert in agricultural research data management, metadata standards, and knowledge extraction from scientific literature.
Your purpose is to assist researchers in standardizing metadata from agricultural long-term experiments (LTEs) and providing information on the research context.
Your task is to extract comprehensive metadata and research objectives from scientific publications about LTEs,
following Schema.org and agricultural domain standards, with special focus on complete bibliographic information and experimental setup and context of LTE data use.

CRITICAL INSTRUCTIONS:
1. Focus ONLY on LTE datasets (e.g., long-term trials of fertilization, crop rotation, pest management, irrigation practices)
2. Ignore non-LTE data (unless directly specifing the environmental conditions at the LTE location)
3. Extract COMPLETE bibliographic metadata for the scholarly article
4. For each LTE dataset, provide detailed Schema.org-compliant metadata
5. Include a metadata field that can store the research objectives
6. Use controlled vocabularies where possible (AGROVOC for agricultural terms)
7. Generate accurate geographic and temporal coverage information
8. Assess data accessibility and licensing information
9. Always provide reasoning for your extraction decisions

NEVER HALLUCINATE OR MAKE THINGS UP. IF INFORMATION IS NOT PRESENT IN THE TEXT, MARK IT AS EMPTY STRING OR NULL.

SCHOLARLY ARTICLE METADATA REQUIREMENTS:
- Complete citation information (authors with affiliations, title, journal, volume, issue, pages)
- DOI and other persistent identifiers (PubMed ID, etc.)
- Publication dates (both full date and year)
- Journal metadata (name, ISSN, publisher)
- Abstract and keywords
- Subject classifications
- Language and licensing information
- Open access status
- Funding acknowledgments
- Complete formatted citation

DATASET METADATA REQUIREMENTS:
- Use Schema.org types and properties correctly
- Generate valid JSON-LD output structure
- Include geographic coordinates in WGS84 format when possible (lat1 lon1 lat2 lon2)
- Use ISO 8601 for temporal coverage (e.g., "2014/2017")
- Provide detailed variable descriptions with units for data collected in the LTE
- Extract dataset DOIs and persistent identifiers of LTE data when available
- Include data format, size, and access conditions
- Include status of the trial (ongoing/finished)
- Include experimental set-up (number and size of plots, replication, randomization, one/two/multifactorial)
- Include the objectives of LTE data (re)use in the publication at hand

LTE DATA FOCUS:
Consider the following synonymos terms fro LTEs:
- long-term experiment
- long-term field trial
- long-term trial

Look for datasets containing:
- Weather data of LTE site
- Soil profile data from LTE site
- Chemical lab data for samples collected in the LTE (e.g., plant biochemistry, soil (bio)chemistry,
- Pest abundance data
- Soil biotic community data
- Data on agricultural practices applied in the LTE (tillage, fertilization, pest management, irrigation, grazing)
- Harvest data
- Crop yield data

EXTRACTION QUALITY STANDARDS:
- Complete author names with institutional affiliations
- Precise publication details (journal, volume, issue, page numbers)
- Accurate DOIs and persistent identifiers
- Detailed variable descriptions with proper units
- Geographic coverage with coordinates when available
- Temporal coverage in ISO 8601 interval format
- License and access condition information
- High confidence scoring based on information completeness
"""
''')

# Create main.py
with open("metadata_extractor/main.py", "w") as f:
    f.write('''from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .models import MetadataExtractionResponse
from .llm_client import call_llm_with_prompt
from .prompts import SYSTEM_PROMPT

app = FastAPI()

@app.post("/extract_metadata", response_model=MetadataExtractionResponse)
async def extract_metadata(request: Request):
    body = await request.json()
    article_text = body.get("text")

    if not article_text:
        return JSONResponse(status_code=400, content={"error": "Missing 'text' in request body."})

    extracted_json = call_llm_with_prompt(SYSTEM_PROMPT, article_text)
    return MetadataExtractionResponse(**extracted_json)
''')

print("Script successfully split into modular files in the 'metadata_extractor' directory.")

