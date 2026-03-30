# EarningsLens

An agentic RAG system for earnings call intelligence. Compares management tone quarter-over-quarter using semantic retrieval and structured sentiment analysis.

## What it does

- Ingests real earnings call transcripts (Apple, Nvidia)
- Chunks and embeds transcripts into a vector database (ChromaDB)
- Uses a ReAct agent to retrieve relevant passages per quarter
- Scores sentiment across 4 dimensions: optimism, caution, growth confidence, uncertainty
- Computes quarter-over-quarter sentiment delta with cited evidence
- Presents results in a live Streamlit UI

## Why it's different

Most RAG demos use static PDFs. This system:
1. Sources real financial transcripts programmatically
2. Uses an agent that decides how many retrievals to make based on the question
3. Produces structured sentiment deltas — not just summaries
4. Cites exact transcript passages for every claim

## Tech stack

- LangChain · ChromaDB · sentence-transformers · Streamlit
- SEC EDGAR APugging Face Datasets
- Python 3.14

## How to run
```bash
git clone https://github.com/ShamanKanapathy12/earningslens.git
cd earningslens
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 ingestion/hf_loader.py
python3 ingestion/parser.py
python3 ingestion/chunker.py
python3 storage/embedder.py
python3 storage/vectorstore.py
streamlit run app/streamlit_app.py
```

## What I'd build next

- LLM-based sentiment scorer (swap in when API credits available)
- Faithfulness evaluation harness with 20 hand-labeled test cases
- Failure analysis documenting 4 retrieval failure modes
- Support for more companies and longer date ranges
