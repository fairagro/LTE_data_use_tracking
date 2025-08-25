import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
API_ENDPOINT = os.getenv("LLM_API_ENDPOINT")

if not API_KEY or not API_ENDPOINT:
    raise RuntimeError("LLM_API_KEY and LLM_API_ENDPOINT must be set in the environment variables.")
