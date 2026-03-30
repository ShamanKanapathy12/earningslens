import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/chroma")
collection = client.get_collection("earnings")

def retrieve_context(question: str, company: str = None, quarter: str = None, top_k: int = 5) -> list:
    embedding = model.encode(question).tolist()

    if company and quarter:
        where = {
            "$and": [
                {"company": {"$eq": company}},
                {"date": {"$eq": quarter}}
            ]
        }
    elif company:
        where = {"company": {"$eq": company}}
    elif quarter:
        where = {"date": {"$eq": quarter}}
    else:
        where = None

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where
    )

    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        chunks.append({
            "text": doc,
            "company": results["metadatas"][0][i]["company"],
            "quarter": results["metadatas"][0][i]["date"],
            "date": results["metadatas"][0][i]["date"],
        })

    return chunks

def compare_quarters(company: str, question: str, quarter_a: str, quarter_b: str) -> dict:
    print(f"Retrieving {quarter_a} for {company}...")
    chunks_a = retrieve_context(question, company=company, quarter=quarter_a)

    print(f"Retrieving {quarter_b} for {company}...")
    chunks_b = retrieve_context(question, company=company, quarter=quarter_b)

    return {
        "company": company,
        "question": question,
        "quarter_a": {"label": quarter_a, "chunks": chunks_a},
        "quarter_b": {"label": quarter_b, "chunks": chunks_b}
    }

if __name__ == "__main__":
    print("Testing retrieve_context...")
    results = retrieve_context("iPhone demand", company="AAPL", quarter="Q1")
    print(f"Got {len(results)} chunks")
    print(f"First chunk preview: {results[0]['text'][:200]}")

    print("\nTesting compare_quarters...")
    comparison = compare_quarters("AAPL", "revenue and demand outlook", "Q1", "Q3")
    print(f"Q1 chunks: {len(comparison['quarter_a']['chunks'])}")
    print(f"Q3 chunks: {len(comparison['quarter_b']['chunks'])}")
    print("Tools working.")