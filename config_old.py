
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
API_ENDPOINT = os.getenv("LLM_API_ENDPOINT")
MODEL_NAME = os.getenv("LLM_MODEL_NAME")

if not API_KEY or not API_ENDPOINT or not MODEL_NAME:
    raise RuntimeError("LLM_API_KEY, LLM_API_ENDPOINT, and LLM_MODEL_NAME must be set in the environment variables.")
