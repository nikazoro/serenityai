from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional, Union
from .models import JournalEntry
from sqlalchemy import func

def add_entry(
    db: Session,
    text: str,
    date: Optional[Union[str, date]] = None,
    source_type: str = "text",
    tags: Optional[str] = "",
    mood_label: Optional[str] = ""
):
    if not text or not text.strip():
        raise ValueError("Journal entry text cannot be empty.")

    if not date:
        latest_date = db.query(func.max(JournalEntry.date)).scalar()
        date = latest_date or datetime.today().date()
    elif isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d").date()
        
    elif isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d").date()

    entry = JournalEntry(
        date=date,
        text=text,
        source_type=source_type,
        tags=tags or "",
        mood_label=mood_label or ""
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_all_entries_grouped_by_date(db: Session):
    return db.query(JournalEntry).order_by(JournalEntry.date.asc()).all()


def get_entry_by_id(db: Session, entry_id: int):
    return db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()


def reset_database(db: Session):
    db.query(JournalEntry).delete()
    db.commit()
