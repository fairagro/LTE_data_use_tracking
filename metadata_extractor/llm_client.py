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
