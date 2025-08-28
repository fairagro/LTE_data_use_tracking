# Standard library imports
import os
from datetime import datetime
from json import loads, JSONDecodeError
import re

# Third-party imports
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Local module imports
from .models import MetadataExtractionResponse
from .llm_client import call_llm_with_prompt
from .prompts import SYSTEM_PROMPT

# Initialize FastAPI app
app = FastAPI()

def extract_json_from_response(text: str) -> str:
    try:
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        return match.group(1) if match else ""
    except Exception as e:
        print(f"❌ Error during regex extraction: {e}")
        return ""

@app.post("/extract_metadata", response_model=MetadataExtractionResponse)
async def extract_metadata(request: Request):
    print("🚀 extract_metadata endpoint called")
    
    body = await request.json()
    article_text = body.get("text")

    if not article_text:
        return JSONResponse(status_code=400, content={"error": "Missing 'text' in request body."})

    print("📡 Calling LLM now...")
    extracted_json = call_llm_with_prompt(SYSTEM_PROMPT, article_text)

    if not extracted_json:
        print("⚠️ LLM returned no content.")
        return JSONResponse(status_code=500, content={"error": "LLM returned empty response."})

    print(f"🧠 Raw LLM response: {extracted_json}")

    # Log the raw LLM response to a file for debugging
    with open("llm_debug_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.now().isoformat()}] Raw LLM response:\n{extracted_json or '[EMPTY]'}\n")

    try:
        json_str = extract_json_from_response(extracted_json)
        if not json_str:
            raise ValueError("No valid JSON found in LLM response.")

        parsed_json = loads(json_str)
        print("✅ Successfully parsed JSON from LLM response.")

        # Save the extracted_json to a file 
        filename = f"llm_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(extracted_json)

        return parsed_json

    except Exception as e:
        print(f"❌ Exception during metadata extraction: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})