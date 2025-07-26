from typing import List

def split_text_into_chunks(text: str, max_tokens: int = 1024) -> List[str]:
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        # Conservative estimate: 1 word ≈ 1.33 tokens
        word_token_length = int(len(word) / 4) + 1
        if current_length + word_token_length > max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_token_length
        else:
            current_chunk.append(word)
            current_length += word_token_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
