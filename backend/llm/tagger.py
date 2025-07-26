from .prompts import tagging_prompt
from ..llm.ollama_client import generate_response as local_llm
import asyncio

async def auto_generate_tags(text: str) -> str:
    prompt = tagging_prompt(text)

    try:
        response = await asyncio.to_thread(local_llm, prompt)
    except Exception:
        raise ValueError("Error occurred while processing the request.")
    
    return response.replace("\n", "").strip().strip(",")
