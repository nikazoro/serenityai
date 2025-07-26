import os
import json
from pathlib import Path
from datetime import datetime
import httpx

from ..utils.embedder import Embedder
from ..vectorstore.qdrant_client import QdrantVectorStore
from ..db.database import SessionLocal
from ..db.crud import add_entry
from ..llm.ollama_client import generate_response as clean_text_with_ollama
from ..llm.tagger import auto_generate_tags
from ..llm.mood_labeler import detect_mood 
from .whisper_transcriber import transcribe_audio 
from .ocr_reader import extract_text_from_image

VALID_IMAGE_TYPES = [".jpg", ".jpeg", ".png"]
VALID_AUDIO_TYPES = [".mp3", ".wav", ".m4a"]

def is_online() -> bool:
    try:
        httpx.get("https://stablehorde.net/api/v2/status", timeout=2.0)
        return True
    except httpx.RequestError:
        return False

async def import_file(file_path: str):
    embedder = Embedder()
    vector_store = QdrantVectorStore()
    path = Path(file_path)

    if not path.exists():
        print(f"File not found: {file_path}")
        return

    ext = path.suffix.lower()
    online = is_online()

    with SessionLocal() as db:

        # === JSON ===
        if ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                entries = json.load(f)

            for entry in entries:
                raw_date = entry.get("date")
                text = entry.get("text")

                # Convert string to datetime.date safely
                try:
                    date = datetime.strptime(raw_date, "%Y-%m-%d").date() if raw_date else None
                except ValueError:
                    date = datetime.today().date()

                if date and text and text.strip():
                    tags = await auto_generate_tags(text.strip())
                    mood = await detect_mood(text.strip())
                    db_entry = add_entry(db, text=text.strip(), date=date, tags=tags, mood_label=mood)

                    vector = embedder.embed(text)
                    vector_store.add_entry(
                        vector,
                        {
                            "date": db_entry.date.isoformat(),
                            "tags": tags,
                            "mood": mood,
                            "text": text.strip()
                        }
                    )
                    print(f"Imported JSON entry with date: {date}, tags: {tags}, mood: {mood}")
                else:
                    raw_text = json.dumps(entry)
                    fallback_date = raw_date or datetime.today().strftime("%Y-%m-%d")
                    prompt = f"Clean this journal entry and add context if needed. Date: {fallback_date}\n\n{raw_text}"
                    cleaned = clean_text_with_ollama(prompt)

                    if cleaned:
                        tags = await auto_generate_tags(cleaned)
                        mood = await detect_mood(cleaned)
                        db_entry = add_entry(db, text=cleaned, date=datetime.today().date(), tags=tags, mood_label=mood)

                        vector = embedder.embed(cleaned)
                        vector_store.add_entry(
                            vector,
                            {
                                "date": db_entry.date.isoformat(),
                                "tags": tags,
                                "mood": mood,
                                "text": cleaned
                            }
                        )
                        print(f"Cleaned malformed JSON entry via Ollama: {db_entry.date}, tags: {tags}, mood: {mood}")
                    else:
                        print("Skipped invalid JSON object.")

        # === Audio ===
        elif ext in VALID_AUDIO_TYPES:
            print("Transcribing audio...")
            raw_text = transcribe_audio(str(path))
            await handle_raw_entry(raw_text, db, embedder, vector_store, source="audio", file_path=str(path), online=online)

        # === Image ===
        elif ext in VALID_IMAGE_TYPES:
            print("Extracting text from image...")
            raw_text = extract_text_from_image(str(path))
            await handle_raw_entry(raw_text, db, embedder, vector_store, source="image", file_path=str(path), online=online)

        # === Plain text ===
        else:
            print("Importing raw text...")
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read().strip()
            await handle_raw_entry(raw_text, db, embedder, vector_store, source="text", file_path=str(path), online=online)

async def handle_raw_entry(raw_text, db, embedder, vector_store, source="text", file_path=None, online=True):
    if not raw_text or not raw_text.strip():
        print("No content to process.")
        return

    today = datetime.today().strftime("%Y-%m-%d")
    cleaned = None
    
    prompt = f"Clean this journal entry and output a readable reflection with date {today}:\n\n{raw_text.strip()}"
    cleaned = clean_text_with_ollama(prompt)

    if not cleaned:
        print("Cleaning failed.")
        return

    tags = await auto_generate_tags(cleaned)
    mood = await detect_mood(cleaned)

    db_entry = add_entry(
        db,
        text=cleaned,
        date=today,
        source_type=source,
        tags=tags,
        mood_label=mood
    )

    vector = embedder.embed(cleaned)
    vector_store.add_entry(
        vector,
        {
            "date": db_entry.date.isoformat(),
            "source": source,
            "tags": tags,
            "mood": mood,
            "text": cleaned
        }
    )

    print(f"Imported {source} entry for {today} with tags: {tags}, mood: {mood}")
