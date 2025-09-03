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
    # extracted_json = call_llm_with_prompt(SYSTEM_PROMPT, article_text)

    print("🧪 Skipping LLM call — using dummy response")
    extracted_json = '''```json
{
  "citation": {
    "title": "Test",
    "authors": [],
    "journal": { "name": "Test Journal" },
    "keywords": [],
    "subject_classifications": []
  },
  "datasets": [],
  "reasoning": "Test reasoning"
}
```'''

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