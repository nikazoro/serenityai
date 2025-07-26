# 🧘 SerenityAI - Your Private Journaling Therapist

**SerenityAI** is a free, open-source, AI-powered journaling therapist that helps you reflect, analyze, and gain insight from your daily thoughts — entirely offline and private. Upload, transcribe, and analyze journal entries in text, audio, or image form and get smart, mood-aware insights to guide your self-discovery.

Designed with mental wellness in mind, SerenityAI combines local language models, embeddings, and semantic search to become your AI-powered reflection companion.

---

## ✨ Features

- 📝 Upload journal entries (text / image / audio)
- 🧠 Automatic transcription (Whisper) & OCR (Tesseract)
- 🏷️ Auto-tagging and mood detection using LLMs
- 🔍 Semantic search using local embeddings + vector DB
- 📅 Organize entries by original date, not upload time
- 📊 Smart insights: mood trends, word count, emotional patterns
- 💾 Draft saving, entry clearing, and tag-based filtering
- 🧠 RAG support for natural language questions on your own journals

---

## 🧱 Tech Stack

| Component     | Technology Used                          |
|---------------|-------------------------------------------|
| Backend       | FastAPI                                   |
| Embeddings    | SentenceTransformers                      |
| Vector DB     | Qdrant (Docker container)                 |
| Metadata DB   | SQLite (via SQLAlchemy)                   |
| LLMs          | Ollama (local) + Stable Horde (fallback)  |
| Audio         | faster-whisper (transcription)            |
| Image OCR     | pytesseract                               |
| Frontend      | Streamlit (minimal UI)           |

---

## 📁 Project Structure


## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/serenityai.git
cd serenityai
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start Required Services

Start **Qdrant** with Docker:

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

Start **Ollama** and load your model:

```bash
ollama serve
ollama run mistral
```

### 4. Launch Backend

```bash
uvicorn backend.api.main:app --reload
```

### 5. Launch Frontend

```bash
streamlit run frontend/app.py
```

---

## 🧠 Insights API (`/insights/`)

Returns daily/weekly analysis:
- Number of entries
- Word counts
- Common moods, emotions, and keywords
- Thematic analysis for UI coloring and filtering

---

## 🗃 Draft Management

- ✍️ Save entry drafts before submission
- 🧹 Clear saved drafts easily

---

## 🕵️ RAG Support

Ask natural questions like:

> *"What were my happiest journal entries last week?"*

SerenityAI uses a **Retrieval-Augmented Generation** pipeline:

- Embeds entries with **SentenceTransformers**
- Stores & retrieves via **Qdrant**
- Generates responses using **Ollama** or **Stable Horde**

You get meaningful reflections, powered entirely by your past writing.

---

## 🔐 Privacy First

- 🔒 No internet required (unless fallback enabled)
- 🧩 Modular and local-first design
- 👤 Your data stays with you

---

## 🛠 Configuration

Create a `.env`:

```env
QDRANT_HOST=localhost
QDRANT_PORT=6333
SQLITE_DB_PATH=./data/journal.db
MODEL_NAME=mistral  # Or any supported Ollama model
```

---

## 📦 Packaging & Deployment

To bundle frontend:

```bash
pyinstaller --onefile frontend/app.py
```

Or Dockerize backend and Qdrant together.

---

## 💡 Future Additions

- Mood-based journaling themes
- Prompted reflection goals
- Entry export (PDF/CSV)
- Smart reminders & timeline playback

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.com)
- [Stable Horde](https://stablehorde.net/)
- [Qdrant](https://qdrant.tech/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [SentenceTransformers](https://www.sbert.net/)
- [Tesseract OCR](https://github.com/tesseract-ocr)
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper)

---

## 🧠 License

MIT License — free for personal or commercial use. Contributions welcome!

---
