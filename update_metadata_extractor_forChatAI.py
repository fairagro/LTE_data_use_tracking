from openai import OpenAI
import os
from pathlib import Path


folder = Path("C:/Users/Lachmuth/OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V/Dokumente/FAIRagro/Use Case 4/LTE_text_processing/metadata_extractor/")

# Update config.py
with open(folder / "config.py", "w") as f:
    f.write(
        """
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
API_ENDPOINT = os.getenv("LLM_API_ENDPOINT")
MODEL_NAME = os.getenv("LLM_MODEL_NAME")

if not API_KEY or not API_ENDPOINT or not MODEL_NAME:
    raise RuntimeError("LLM_API_KEY, LLM_API_ENDPOINT, and LLM_MODEL_NAME must be set in the environment variables.")
"""
    )

# Update llm_client.py
with open(folder / "llm_client.py", "w") as f:
    f.write(
        """
from openai import OpenAI
from .config import API_KEY, API_ENDPOINT, MODEL_NAME

def call_llm_with_prompt(prompt: str, text: str) -> dict:
    client = OpenAI(
        api_key=API_KEY,
        base_url=API_ENDPOINT
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        model=MODEL_NAME
    )

    return chat_completion.choices[0].message.content
"""
    )

# Update main.py to handle string response from LLM
with open(folder / "main.py", "r") as f:
    main_content = f.read()

main_content = main_content.replace(
    "return MetadataExtractionResponse(**extracted_json)",
    "from json import loads\n    return MetadataExtractionResponse(**loads(extracted_json))"
)

with open(folder / "main.py", "w") as f:
    f.write(main_content)

print("All files have been updated to use the OpenAI client with ChatAI's API format.")