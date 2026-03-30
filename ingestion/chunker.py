import os
import json

def sliding_window_chunks(text: str, chunk_size: int = 512, overlap: int = 50) -> list:
    """
    Split text into overlapping chunks by word count.
    chunk_size = words per chunk
    overlap = words shared between consecutive chunks
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        
        chunks.append({
            "text": chunk_text,
            "word_count": len(chunk_words),
            "start_word": start,
            "end_word": end
        })
        
        # Move forward by (chunk_size - overlap) so chunks share 50 words
        start += chunk_size - overlap
        
        if start >= len(words):
            break

    return chunks

def chunk_filing(parsed_path: str, metadata: dict) -> list:
    """Chunk a single parsed filing and attach metadata to each chunk."""
    
    with open(parsed_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    raw_chunks = sliding_window_chunks(text)
    
    enriched = []
    for i, chunk in enumerate(raw_chunks):
        enriched.append({
            "chunk_id": f"{metadata['company']}_{metadata['date']}_{i}",
            "company": metadata["company"],
            "date": metadata["date"],
            "chunk_index": i,
            "total_chunks": len(raw_chunks),
            "text": chunk["text"],
            "word_count": chunk["word_count"]
        })
    
    return enriched

def chunk_all(parsed_dir: str = "data/parsed", output_dir: str = "data/chunks"):
    """Chunk all parsed filings and save."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load manifest to get metadata
    manifest_path = os.path.join(parsed_dir, "manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    all_chunks = []
    
    for filing in manifest:
        print(f"Chunking {filing['company']} {filing['date']}...")
        
        chunks = chunk_filing(filing["parsed_path"], filing)
        all_chunks.extend(chunks)
        
        print(f"  {len(chunks)} chunks created")
    
    # Save all chunks to one file
    out_path = os.path.join(output_dir, "all_chunks.json")
    with open(out_path, "w") as f:
        json.dump(all_chunks, f, indent=2)
    
    print(f"\nDone. {len(all_chunks)} total chunks saved to {out_path}")
    return all_chunks

if __name__ == "__main__":
    chunk_all()