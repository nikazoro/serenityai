def reflection_prompt(journal_text: str) -> str:
    return f"""You are a reflective journaling assistant.
Read the user's journal entry and respond with a short reflection that helps them process their thoughts.

Journal Entry:
\"\"\"
{journal_text}
\"\"\"

Reflection:"""

def qa_prompt(context: str, question: str) -> str:
    return f"""You are an insightful AI journaling assistant.
Use the provided journal context to help the user reflect on or answer questions about their past experiences.

Context:
\"\"\"{context}\"\"\"

Question:
\"\"\"{question}\"\"\"

Thoughtful Answer:"""


def tagging_prompt(journal_text: str) -> str:
    return f"""You are a tagging assistant for journal entries.
Read the entry and generate 3 to 5 relevant, comma-separated tags (single-word if possible).

Journal Entry:
\"\"\"{journal_text}\"\"\"

Tags:"""