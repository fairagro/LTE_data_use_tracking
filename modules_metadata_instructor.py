# config.py
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
API_ENDPOINT = os.getenv("LLM_API_ENDPOINT")
MODEL_NAME = os.getenv("LLM_MODEL_NAME")

if not API_KEY or not API_ENDPOINT or not MODEL_NAME:
    raise RuntimeError("LLM_API_KEY, LLM_API_ENDPOINT, and LLM_MODEL_NAME must be set in the environment variables.")

# main.py
# Standard library imports
import os
from datetime import datetime
from json import loads, JSONDecodeError

# Third-party imports
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Local module imports
from .models import MetadataExtractionResponse
from .llm_client import call_llm_with_prompt
from .prompts import SYSTEM_PROMPT

# Initialize FastAPI app
app = FastAPI()

# Dummy JSON response for testing (does not work because it lacks required fields)
DUMMY_JSON_RESPONSE = '''```json
{
  "citation": {
    "title": "Test",
    "authors": [],
    "journal": {
      "name": "Test Journal",
      "issn": "1234-5678"
    },
    "keywords": [],
    "subject_classifications": [],
    "year": 2025,
    "abstract": "This is a test abstract.",
    "language": "en"
  },
  "LTE_metadata_OverviewMap": {}
}
```'''


def clean_llm_response(raw_response: str) -> str:
    """Remove Markdown-style code fencing from LLM response."""
    if raw_response.startswith("```json"):
        raw_response = raw_response[len("```json"):].strip()
    if raw_response.endswith("```"):
        raw_response = raw_response[:-len("```")].strip()
    return raw_response

@app.post("/extract_metadata", response_model=MetadataExtractionResponse)
async def extract_metadata(request: Request):
    print("🚀 extract_metadata endpoint called")
    body = await request.json()
    article_text = body.get("text")

    if not article_text:
        return JSONResponse(status_code=400, content={"error": "Missing 'text' in request body."})

    # Uncomment this to use the real LLM call
    extracted_json = call_llm_with_prompt(SYSTEM_PROMPT, article_text)

    #print("🧪 Skipping LLM call — using dummy response")
    #extracted_json = DUMMY_JSON_RESPONSE

    if not extracted_json:
        print("⚠️ LLM returned no content.")
    else:
        print(f"🧠 Raw LLM response: {extracted_json}")

    # Log the raw LLM response to a file for debugging
    with open("llm_debug_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.now().isoformat()}] Raw LLM response:\n{extracted_json or '[EMPTY]'}\n")

    if not extracted_json or extracted_json.strip() == "":
        return JSONResponse(status_code=500, content={"error": "LLM returned empty response."})

    try:
        cleaned_json = clean_llm_response(extracted_json)
        parsed_json = loads(cleaned_json)
    except JSONDecodeError as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to parse JSON: {str(e)}"})

    # Save the cleaned JSON to a file
    filename = f"llm_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned_json)

    return parsed_json

# llm_client.py
from openai import OpenAI
from .config import API_KEY, API_ENDPOINT, MODEL_NAME
from datetime import datetime
import httpx

print(API_ENDPOINT)
print("📦 llm_client module loaded")

def call_llm_with_prompt(prompt: str, text: str) -> str:
    print("🛠️ Preparing to initialize OpenAI client...")
    print("🔑 API_KEY:", API_KEY)
    print("🌐 API_ENDPOINT:", API_ENDPOINT)
    print("🧠 MODEL_NAME:", MODEL_NAME)

    try:
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_ENDPOINT,
            timeout=httpx.Timeout(500.0, connect=60.0, read=500.0, write=500.0, pool=500.0),
            max_retries=2
        )
        print("📤 Sending request to LLM...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
        )
        print("✅ LLM responded.")
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return ""

# models.py
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel
from pydantic import BaseModel, Field, HttpUrl, EmailStr

class StrictBaseModel(PydanticBaseModel):
    model_config = {
        "str_strip_whitespace": True,
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
        },
        "validate_assignment": True,
        "extra": "forbid",
        "validate_by_name": True,
    }

# Publication metadata models
class Author(StrictBaseModel):
    """Author of the scientific publication information is extracted from, Schema.org Person object"""
    name: str
    affiliation: Optional[str]

class Journal(StrictBaseModel):
    """Journal information of the scientific publication information is extracted from, Schema.org Periodical object"""
    name: str
    issn: Optional[str]
    publisher: Optional[str]

class CitationMetadata(StrictBaseModel):
    """Metadata about the scientific publication the information is extracted from, Schema.org ScholarlyArticle object"""
    title: str
    authors: List[Author]
    journal: Journal
    volume: Optional[str]
    issue: Optional[str]
    pages: Optional[str]
    doi: Optional[str]
    url: Optional[str]
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




# Metadata models for LTE Overview Map
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List

class TrialDesign(StrictBaseModel):
    """Detailed information about the experimental design of the LTE."""
    randomization: Optional[bool]
    replication: Optional[int]
    number_plots: Optional[int]
    size_plots: Optional[float]

class SoilInfo(StrictBaseModel):
    """Detailed information about the soil at the LTE site."""
    soil_group_wrb: Optional[str]
    soil_type_other: Optional[str]
    parental_material: Optional[str]
    texture: Optional[str]
    texture_sand: Optional[float]
    texture_silt: Optional[float]
    texture_clay: Optional[float]
    bulk_density: Optional[float]
    organic_carbon_prc: Optional[float]
    further_soil_info: Optional[str]

class ContactInfo(StrictBaseModel):
    """Contact information for the LTE dataset or experiment."""
    contact_name: Optional[str]
    contact_email: Optional[EmailStr]
    doi: Optional[str]

class TrialTypes(StrictBaseModel): 
    """Types of trials conducted in the LTE."""
    tillage_trial: Optional[bool] # yes/no
    fertilization_trial: Optional[bool] # yes/no
    crop_rotation_trial: Optional[bool] # yes/no
    cover_crop_trial: Optional[bool] # yes/no
    irrigation_trial: Optional[bool] # yes/no
    pest_weed_trial: Optional[bool] # yes/no
    grazing_trial: Optional[bool] # yes/no
    other_trial: Optional[bool] # yes/no


class AGROVOCConcept(StrictBaseModel):
    """AGROVOC concept for crop species, following Schema.org DefinedTerm object"""
    type: str = Field(default="DefinedTerm", alias="@type")
    inDefinedTermSet: str = Field(default="https://www.fao.org/agrovoc/en/", alias="inDefinedTermSet")
    label: str
    uri: Optional[str]

class CropSpecies(StrictBaseModel):
    """Crop species grown in the LTE, represented as AGROVOC concept."""
    type: str = Field(default="CropSpecies", alias="@type")
    name: AGROVOCConcept
    schema_org_type: Optional[str] = "Plant"

class Variable(StrictBaseModel):
    """Variables or research parameters measured in the LTE experiment, following Schema.org PropertyValue object"""
    type: str = Field(default="PropertyValue", alias="@type")
    name: str
    description: str
    unit: Optional[str]
    vocabulary: Optional[str] = "AGROVOC"

class LTEEntry(StrictBaseModel): 
    """Metadata model for the LTE overview map, containing detailed information about the LTE itself, not necessarily reported in the publication text. If not reported in the text, the attribute should be set to null."""
    #id: Optional[int] #
    #index: Optional[int]
    name: Optional[str] # 
    site: Optional[str] 
    country: Optional[str]
    start_date: Optional[int]
    status: Optional[str] # binary: on-going / finished
    trial_duration: Optional[int] # in years
    trial_status: Optional[str] # Ongoing / finished (with year it finished)
    trial_institution: Optional[str]
    landuse_type: Optional[str] # 
    research_theme: Optional[str] # free text
    trial_types: TrialTypes
    trial_category: Optional[str]
    #holder_category: Optional[str]
    website: Optional[HttpUrl]
    #networks: Optional[List[str]]
    research_parameters: List[Variable] #  with units if applicable
    farming_category: Optional[str] 
    #position_exactness: Optional[str]
    size_hectares: Optional[float]
    longitude: Optional[float]
    latitude: Optional[float]
    experimental_setup: Optional[str]
    tillage_levels: Optional[str] 
    fertilization_levels: Optional[str]
    crop_rotation_levels: Optional[List[CropSpecies]]
    cover_crop_levels: Optional[List[CropSpecies]]
    irrigation_levels: Optional[str]
    pest_weed_levels: Optional[str] # Pest and weed management levels
    grazing_levels: Optional[str]
    other_levels: Optional[str]
    one_factorial_lte: Optional[bool]
    two_factorial_lte: Optional[bool]
    multifactorial_lte: Optional[bool]
    trial_design: TrialDesign
    soil_info: SoilInfo
    miscellaneous: Optional[str]
    #literature: Optional[str] # Citation of study at hand, taken form CitationMetadata
    sources: ContactInfo
    #agrovoc_keywords: Optional[str]


class MetadataExtractionResponse(StrictBaseModel):
    citation: CitationMetadata
    #LTE_metadata: LTEDataMetadata
    LTE_metadata_OverviewMap: LTEEntry 
    #reasoning: Optional[str]

# pdf_utils.py
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



# prompts.py
SYSTEM_PROMPT = """You are an expert in agricultural research data management, metadata standards, and knowledge extraction from scientific literature.
Your purpose is to assist researchers in standardizing metadata from agricultural long-term experiments (LTEs) and providing information on the research context.
Your task is to extract comprehensive metadata and research objectives from scientific publications about LTEs,
following Schema.org and agricultural domain standards, with special focus on complete bibliographic information for the publication at hand and the descriptions of LTE experimental setup, data collected, and research objectives.

CRITICAL INSTRUCTIONS:
1. Focus ONLY on LTE datasets (e.g., long-term trials of fertilization, crop rotation, pest management, irrigation practices)
2. Ignore non-LTE data (unless directly specifing the environmental conditions at the LTE location)
3. Extract COMPLETE bibliographic metadata for the scholarly article
4. For each LTE dataset, provide detailed Schema.org-compliant metadata
    a) Schema.org Dataset metadata: Include dataset title, description, variables measured (with units), geographic and temporal coverage, persistent identifiers (DOI, etc) if available (according to provided models). If not available, leave the respective fields empty.
    b) Metadata for LTE Overview Map: Include trial design, soil information, contact details, and trial types etc (according to provided models)
5. Include a metadata field that can store the research objectives
6. Use controlled vocabularies where possible (AGROVOC for agricultural terms)
7. Generate accurate geographic and temporal coverage information
8. Assess data accessibility and licensing information of both the publication and datasets.
    Data set distribution and license information should be included if available in the methods section or data availability statement of the publication. If not available, leave these fields empty.
9. Return only raw JSON, without Markdown formatting or code block markers.

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

Return only raw JSON, without Markdown formatting or code block markers.
"""
