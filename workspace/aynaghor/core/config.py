import os
from dotenv import load_dotenv

load_dotenv()

settings = {
    "USE_GEMINI": os.getenv("USE_GEMINI", "false").lower() == "true",
    "GEMINI_KEY": os.getenv("GEMINI_KEY", ""),
    "LLM_HOST": os.getenv("LLM_HOST", "http://localhost:8000"),
    "LLM_MODEL": os.getenv("LLM_MODEL", "llama2"),
}