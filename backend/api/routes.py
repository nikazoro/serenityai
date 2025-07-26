from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import traceback
from fastapi import Query
from typing import List, Optional, Set, Dict
from collections import Counter, defaultdict
import re
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import text
from ..db.database import engine
from ..db.models import Base
from ..utils.embedder import Embedder
from ..vectorstore.qdrant_client import QdrantVectorStore
from ..llm.ollama_client import generate_response as local_llm
from ..db.models import JournalEntry
from ..upload.processor import import_file
from ..db.database import SessionLocal
from ..db.crud import get_all_entries_grouped_by_date, get_entry_by_id

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/upload/")
async def upload_journal(file: UploadFile = File(...)):
    """Upload a journal file (txt, json, audio, image)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    filename = file.filename
    ext = Path(filename).suffix.lower()
    temp_path = UPLOAD_DIR / filename

    SUPPORTED_EXTS = [".txt", ".json", ".mp3", ".wav", ".m4a", ".jpg", ".jpeg", ".png"]
    if ext not in SUPPORTED_EXTS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    try:
        await import_file(str(temp_path))
        return {
            "message": f"File '{filename}' (type: {ext}) imported successfully.",
            "filename": filename,
            "type": ext
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


# ===== MODELS =====

class QueryRequest(BaseModel):
    question: str

class ReflectionRequest(BaseModel):
    entry_id: int

class CreateEntryRequest(BaseModel):
    text: str
    date: str  # Format: YYYY-MM-DD
    tags: Optional[str] = None
    mood_label: Optional[str] = None
    source_type: Optional[str] = "text"


def clean_tags(llm_response: str) -> str:
    """Clean and normalize LLM-generated tags."""
    tags = re.findall(r"\b[a-zA-Z][a-zA-Z\s\-]{1,}\b", llm_response)
    clean = list({tag.strip().title() for tag in tags if tag.strip()})
    return ", ".join(clean[:7])


# --- API Route ---
@router.post("/create_entry/")
def create_entry(entry: CreateEntryRequest, db: Session = Depends(get_db)):
    try:
        try:
            parsed_date = datetime.strptime(entry.date, "%Y-%m-%d").date()
        except ValueError:
            return {"success": False, "message": "Invalid date format. Use YYYY-MM-DD."}

        if not entry.tags or not entry.tags.strip():
            llm_prompt = f"""Extract up to 7 relevant tags that best describe the following journal entry. 
            Respond only with a comma-separated list of tags. Do not include any extra explanation or introductory text.

            Journal Entry:
            \"\"\"{entry.text}\"\"\"
            Tags:"""

            llm_response = local_llm(llm_prompt)
            auto_tags = clean_tags(llm_response)
        else:
            auto_tags = entry.tags
        
        mood = entry.mood_label or "reflective"
        
        # Duplicate check
        existing = db.query(JournalEntry).filter(
            JournalEntry.text == entry.text.strip(),
            JournalEntry.date == parsed_date
        ).first()

        if existing:
            return {
                "success": False,
                "message": f"Duplicate entry already exists for {entry.date}.",
                "entry_id": existing.id
            }

        # Save if unique
        new_entry = JournalEntry(
            text=entry.text.strip(),
            date=parsed_date,
            tags=auto_tags,
            mood_label=mood,
            source_type=entry.source_type or "text"
        )


        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        return {
            "success": True,
            "message": "Entry created successfully.",
            "entry_id": new_entry.id,
            "tags": new_entry.tags,
            "mood_label": new_entry.mood_label
        }

    except Exception as e:
        return {"success": False, "message": f"Failed to create entry: {str(e)}"}

# ===== LIST ALL ENTRIES =====
@router.get("/entries/")
def list_entries():
    """List all journal entries grouped by date."""
    db = SessionLocal()
    grouped = get_all_entries_grouped_by_date(db)
    return grouped


# ===== GET SINGLE ENTRY =====

@router.get("/entry/{entry_id}")
def get_entry(entry_id: int):
    """Get a specific journal entry by ID."""
    db = SessionLocal()
    entry = get_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


# ===== REFLECTION USING LLM =====

@router.post("/reflect/")
def reflect_on_entry(payload: ReflectionRequest):
    """Get reflection on a specific journal entry."""
    db = SessionLocal()
    entry: JournalEntry = get_entry_by_id(db, payload.entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    prompt = f"""You are a reflective journaling assistant.
Read the following journal entry and respond with a short reflection.

Journal Entry:
\"\"\"{entry.text}\"\"\"

Reflection:"""

    try:
        response = local_llm(prompt)
    except Exception:
        response = "Error occurred while processing the request."

    return {"reflection": response}


# ===== QUERY WITH VECTOR SEARCH + LLM =====

@router.post("/ask/")
def ask_question(payload: QueryRequest):
    """Ask a question based on all journal entries."""
    embedder = Embedder()
    vector_store = QdrantVectorStore()
    query_vector = embedder.embed(payload.question)
    results = vector_store.search(query_vector)

    context = "\n\n".join([
    point.payload.get("text", "") 
    for point in results 
    if point.payload is not None and "text" in point.payload
    ])

    if not context:
        return {"answer": "No relevant context found."}

    prompt = f"""You are an AI assistant helping the user reflect on their journal.

Based on the following past context, answer the question.

Context:
\"\"\"{context}\"\"\"

Question: {payload.question}
Answer:"""

    try:
        answer = local_llm(prompt)
    except Exception:
        answer = "Error occurred while processing the request."

    return {"answer": answer}


@router.get("/tags", response_model=List[str])
def list_all_tags():
    """List all unique tags from journal entries."""
    db = SessionLocal()
    entries = db.query(JournalEntry).all()

    tag_set: Set[str] = set()
    for entry in entries:
        # if entry.tags:
        if entry.tags is not None and entry.tags.strip():
            tag_list = [tag.strip().lower() for tag in entry.tags.split(",")]
            tag_set.update(tag_list)

    return sorted(tag_set)


# ===== FILTER ENTRIES BY TAG =====

@router.get("/filter")
def filter_entries_by_tag(tag: str = Query(..., description="Tag to filter by")):
    """Get all entries that include a specific tag."""
    db = SessionLocal()
    entries = db.query(JournalEntry).all()

    matching_entries = []
    for entry in entries:
        # if entry.tags:
        if entry.tags is not None and entry.tags.strip():
            tag_list = [t.strip().lower() for t in entry.tags.split(",")]
            if tag.lower() in tag_list:
                matching_entries.append(entry)

    if not matching_entries:
        raise HTTPException(status_code=404, detail=f"No entries found with tag '{tag}'")

    return matching_entries



# ===== RESET DB & VECTORS =====

@router.post("/reset/")
def reset_all():
    """Reset SQLite and Qdrant (dangerous)."""
    
    # --- SQLite Reset (Safe, no file delete) ---
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("SQLite tables dropped and recreated")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"SQLite reset failed: {str(e)}")

    # --- Qdrant Reset ---
    try:
        vector_store = QdrantVectorStore()
        vector_store.reset()
        print("Qdrant collection reset")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Qdrant reset failed: {str(e)}")

    return {"message": "All data reset (SQLite & Qdrant)."}

#Color map for mood labels
MOOD_COLOR_MAP = {
    "joy": "#FFE066",
    "happy": "#FFD700",
    "excited": "#FFA500",
    "calm": "#A0E7E5",
    "reflective": "#B0C4DE",
    "anxious": "#FF6F61",
    "sad": "#778899",
    "angry": "#FF4500",
    "stress": "#B22222",
    "grateful": "#98FB98",
    "motivated": "#00CED1",
}

@router.get("/insights/")
def get_insights():
    """Return analytics about journal entries."""
    db: Session = SessionLocal()
    entries: list[JournalEntry] = db.query(JournalEntry).all()
    if not entries:
        return {"message": "No journal entries found."}

    daily_counts = defaultdict(int)
    weekly_counts = defaultdict(int)
    tag_counter = Counter()
    mood_counter = Counter()
    total_words = 0
    total_entries = 0

    for entry in entries:
        total_entries += 1
        entry_date = entry.date
        date_str = entry_date.strftime("%Y-%m-%d")
        week_str = entry_date.strftime("%Y-W%U")
        daily_counts[date_str] += 1
        weekly_counts[week_str] += 1

        # Word count
        text_value = str(entry.text or "")
        words = re.findall(r"\w+", text_value)
        total_words += len(words)

        # Tags
        tags_value = str(entry.tags or "")
        tags = [t.strip().lower() for t in tags_value.split(",") if t.strip()]
        tag_counter.update(tags)

        # Mood label
        mood = str(entry.mood_label or "").strip().lower()
        if mood:
            mood_counter.update([mood])
        
        # Group by day and week
        date_str = entry.date.strftime("%Y-%m-%d")
        daily_counts[date_str] += 1
        iso_year, iso_week, _ = entry.date.isocalendar()
        weekly_key = f"{iso_year}-W{iso_week:02d}"
        weekly_counts[weekly_key] += 1

    avg_word_count = total_words // total_entries if total_entries else 0
    mood_distribution = [
        {
            "mood": mood,
            "count": count,
            "color": MOOD_COLOR_MAP.get(mood, "#CCCCCC")
        }
        for mood, count in mood_counter.most_common()
    ]
    return {
        "total_entries": total_entries,
        "average_word_count": avg_word_count,
        "entries_per_day": dict(daily_counts),
        "entries_per_week": dict(weekly_counts),
        "top_tags": tag_counter.most_common(10),
        "mood_distribution": mood_distribution,
        "moods": mood_counter.most_common(10)
    }
