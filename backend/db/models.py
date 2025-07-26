from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    text = Column(Text, nullable=False)
    source_type = Column(String, default="text")  # "text", "audio", "image"
    tags = Column(String, nullable=True)          
    mood_label = Column(String, default="")