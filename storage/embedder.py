from sentence_transformers import SentenceTransformer
import json

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks: list) -> list:
    print(f"Embedding {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i].tolist()
    print("Done.")
    return chunks

if __name__ == "__main__":
    with open("data/chunks/all_chunks.json", "r") as f:
        chunks = json.load(f)

    # Only keep chunks with real content
    chunks = [c for c in chunks if c["word_count"] > 100]
    print(f"Filtered to {len(chunks)} quality chunks")

    embedded = embed_chunks(chunks)

    with open("data/chunks/embedded_chunks.json", "w") as f:
        json.dump(embedded, f)

    print(f"Saved {len(embedded)} embedded chunks")