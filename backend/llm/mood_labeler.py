import re
import asyncio
from .ollama_client import generate_response as local_llm

def extract_mood_label(raw: str) -> str:
    # Lowercase, remove surrounding whitespace
    raw = raw.lower().strip()

    # Remove anything in parentheses
    raw = re.sub(r"\(.*?\)", "", raw).strip()

    # Split on common separators and take the first valid label
    for part in re.split(r"[;,/]|but|and", raw):
        label = part.strip()
        if label:
            return label

    return "neutral"  # Fallback if parsing fails

async def detect_mood(text: str) -> str:
    prompt = f"""Based on the journal entry below, label the overall emotional tone using one word.
Examples: joy, anxious, reflective, sad, excited and also only from these joy,happy,excited,calm,reflective,anxious,sad,angry,stress,grateful,motivated


Entry:
\"\"\"{text}\"\"\"

Mood:"""

    try:
        response = await asyncio.to_thread(local_llm, prompt)
        clean = extract_mood_label(response)
        return clean
    except:
        return "neutral"
