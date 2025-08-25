import requests
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
