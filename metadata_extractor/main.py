from fastapi import FastAPI, Request
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
