# Update llm call
from openai import OpenAI
from .config import API_KEY, API_ENDPOINT, MODEL_NAME
from datetime import datetime
import httpx

def call_llm_with_prompt(prompt: str, text: str) -> str:
    print("🧪 Inside call_llm_with_prompt()")

    try:
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_ENDPOINT,
            timeout=httpx.Timeout(30.0, connect=10.0, read=20.0, write=10.0, pool=5.0),
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
        with open("llm_error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now().isoformat()}] LLM call failed: {str(e)}\n")
        return ""