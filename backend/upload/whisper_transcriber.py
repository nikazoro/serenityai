from faster_whisper import WhisperModel

# Use "base", "small", "medium", "large-v2" etc.
model = WhisperModel("base",device="cpu", compute_type="int8")

def transcribe_audio(file_path: str) -> str:
    segments, _ = model.transcribe(file_path, beam_size=5)
    transcript = " ".join([segment.text for segment in segments])
    return transcript.strip()
