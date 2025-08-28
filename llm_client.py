
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
