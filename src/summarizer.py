import pathlib
from tqdm import tqdm
from llama_client import call_llama

def load_chunks(chunks_folder):
    """Reads all chunk files from the folder."""
    chunks = []
    for chunk_file in sorted(chunks_folder.glob("*.txt")):
        text = chunk_file.read_text(encoding="utf-8")
        chunks.append((chunk_file.name, text))
    return chunks

def summarize_chunks(chunks):
    """Summarizes each text chunk using LLaMA (via Ollama)."""
    summaries = []

    for filename, text in tqdm(chunks, desc="Summarizing chunks"):
        prompt = f"""
Summarize the following text clearly and concisely:

{text}

### SUMMARY:
"""
        try:
            summary = call_llama(prompt)
            summaries.append((filename, summary))
        except Exception as e:
            summaries.append((filename, f"Error summarizing {filename}: {e}"))

    return summaries

def save_summaries(summaries, output_folder):
    """Saves each summary to a text file."""
    output_folder.mkdir(parents=True, exist_ok=True)
    for filename, summary in summaries:
        summary_file = output_folder / f"summary_{filename}"
        summary_file.write_text(summary, encoding="utf-8")

def main():
    project_root = pathlib.Path(__file__).resolve().parents[1]
    chunks_folder = project_root / "data" / "chunks"
    summaries_folder = project_root / "data" / "summaries"

    print("📂 Loading chunks...")
    chunks = load_chunks(chunks_folder)

    print("🧠 Summarizing chunks using LLaMA...")
    summaries = summarize_chunks(chunks)

    print("💾 Saving summaries...")
    save_summaries(summaries, summaries_folder)

    print("✅ Done! Summaries saved in /data/summaries/")

if __name__ == "__main__":
    main()
