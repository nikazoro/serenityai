import requests
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = os.getenv("MODEL_NAME", "mistral")

def generate_response(prompt: str, model: str = DEFAULT_MODEL) -> str:
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    response.raise_for_status()
    return response.json()["response"].strip()
