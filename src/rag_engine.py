import pathlib
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
from llama_client import call_llama
from tqdm import tqdm

# --------- 1. Load Chunks ----------
def load_chunks(chunks_folder):
    chunks = []
    chunk_files = sorted(chunks_folder.glob("*.txt"))
    for f in chunk_files:
        text = f.read_text(encoding="utf-8")
        chunks.append((f.name, text))
    return chunks

# --------- 2. Create / Load Vector DB ----------
def create_vector_db(chunks, db_path):
    print("🔍 Initializing embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    client = chromadb.PersistentClient(path=str(db_path))
    collection = client.get_or_create_collection(name="pdf_chunks")

    if collection.count() == 0:
        print("📦 Creating new vector database...")
        ids = []
        docs = []

        for name, text in tqdm(chunks, desc="Embedding chunks"):
            ids.append(name)
            docs.append(text)

        collection.add(documents=docs, ids=ids)
        print("✅ Vector database created!")
    else:
        print("📂 Using existing vector database...")

    return collection

# --------- 3. Ask a question using RAG ----------
def ask_question(question, collection):
    # Retrieve relevant chunks
    results = collection.query(
        query_texts=[question],
        n_results=3
    )
    
    retrieved_text = "\n\n".join(results["documents"][0])

    # Create prompt for LLaMA
    prompt = f"""
You are an intelligent assistant. Answer the question using ONLY the context below.

### CONTEXT:
{retrieved_text}

### QUESTION:
{question}

### ANSWER:
"""

    answer = call_llama(prompt)
    return answer.strip()

# --------- 4. Main runner ----------
def main():
    project_root = pathlib.Path(__file__).resolve().parents[1]
    chunks_folder = project_root / "data" / "chunks"
    db_path = project_root / "data" / "vector_db"

    print("📂 Loading chunks...")
    chunks = load_chunks(chunks_folder)

    print("🧠 Creating / Loading vector DB...")
    collection = create_vector_db(chunks, db_path)

    print("\n🧠 Ask anything about your PDF (type 'exit' to quit):\n")
    while True:
        q = input("> ")
        if q.lower() in ("exit", "quit"):
            print("👋 Exiting RAG engine.")
            break
        answer = ask_question(q, collection)
        print("\n💬 Answer:", answer, "\n")

if __name__ == "__main__":
    main()
