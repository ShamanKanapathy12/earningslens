import chromadb
import json

def load_into_chromadb(embedded_path: str = "data/chunks/embedded_chunks.json"):
    
    client = chromadb.PersistentClient(path="data/chroma")
    
    # Delete collection if it exists so we start fresh
    try:
        client.delete_collection("earnings")
    except:
        pass
    
    collection = client.create_collection("earnings")
    
    with open(embedded_path, "r") as f:
        chunks = json.load(f)
    
    print(f"Loading {len(chunks)} chunks into ChromaDB...")
    
    # Load in batches of 100
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        
        collection.add(
            ids=[c["chunk_id"] for c in batch],
            embeddings=[c["embedding"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[{
                "company": c["company"],
                "date": c["date"],
                "quarter_label": c.get("quarter_label", ""),
                "chunk_index": c["chunk_index"]
            } for c in batch]
        )
        print(f"  Loaded batch {i//batch_size + 1}")
    
    print(f"\nDone. {collection.count()} chunks in ChromaDB.")
    return collection

def query(question: str, company: str = None, quarter: str = None, top_k: int = 5):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    client = chromadb.PersistentClient(path="data/chroma")
    collection = client.get_collection("earnings")
    
    embedding = model.encode(question).tolist()
    
    where = {}
    if company:
        where["company"] = company
    if quarter:
        where["quarter_label"] = quarter
    
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where if where else None
    )
    
    return results

if __name__ == "__main__":
    load_into_chromadb()
    
    print("\nTesting retrieval...")
    results = query("iPhone demand and revenue", company="AAPL")
    
    print(f"\nTop result:")
    print(results["documents"][0][0][:300])