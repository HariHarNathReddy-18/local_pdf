# FILE: src/text_preprocessor.py

import re

def clean_text(text: str) -> str:
    """Cleans extracted PDF text."""
    text = re.sub(r'-\n', '', text)          # remove hyphen line breaks
    text = re.sub(r'\n+', '\n', text)        # collapse newlines
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # remove non-ASCII
    text = re.sub(r'\s+', ' ', text)         # collapse spaces
    return text.strip()

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    """Splits text into overlapping chunks of approx chunk_size words."""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i : i + chunk_size])
        chunks.append(chunk)

    return chunks
