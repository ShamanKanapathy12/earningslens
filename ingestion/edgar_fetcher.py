import requests
import os
import json
import time
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "EarningsLens research@earningslens.com"}

COMPANIES = {
    "AAPL": "320193",
    "NVDA": "1045810"
}

def get_8k_filings(cik: str, company: str, max_filings: int = 3):
    url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    filings = data["filings"]["recent"]

    results = []
    for i, form in enumerate(filings["form"]):
        if form == "8-K" and len(results) < max_filings:
            results.append({
                "company": company,
                "cik": cik,
                "accession": filings["accessionNumber"][i],
                "date": filings["filingDate"][i],
            })
    return results

def get_transcript_url(cik: str, accession: str):
    acc_clean = accession.replace("-", "")
    index_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_clean}/{accession}-index.htm"
    
    r = requests.get(index_url, headers=HEADERS)
    time.sleep(0.5)
    
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    
    skip_keywords = ["index", "headers", "R1", "R2", "FilingSummary"]
    
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        
        doc_type = cells[0].text.strip()
        link_tag = cells[2].find("a") if len(cells) > 2 else None
        
        if not link_tag:
            continue
            
        href = link_tag.get("href", "")
        filename = href.split("/")[-1].lower()
        
        # Skip files we don't want
        if any(k.lower() in filename for k in skip_keywords):
            continue
        
        # Target exhibit 99.1 — that's always the transcript
        if "ex" in doc_type.lower() and "99" in doc_type:
            return f"https://www.sec.gov{href}"
        
        if href.endswith(".htm") or href.endswith(".html"):
            if any(k in filename for k in ["ex99", "ex-99", "exhibit", "transcript", "earnings"]):
                return f"https://www.sec.gov{href}"

    return None

def fetch_and_save(output_dir: str = "data/raw"):
    os.makedirs(output_dir, exist_ok=True)
    manifest = []

    for ticker, cik in COMPANIES.items():
        print(f"\nFetching {ticker}...")
        filings = get_8k_filings(cik, ticker)

        for filing in filings:
            print(f"  Checking {filing['date']} ({filing['accession']})...")
            
            transcript_url = get_transcript_url(filing["cik"], filing["accession"])
            
            if not transcript_url:
                print(f"    No transcript found — skipping")
                continue
            
            print(f"    Found: {transcript_url.split('/')[-1]}")
            
            r = requests.get(transcript_url, headers=HEADERS)
            time.sleep(0.5)
            
            if r.status_code != 200:
                print(f"    Could not download — skipping")
                continue

            filename = f"{ticker}_{filing['date']}_{filing['accession']}.txt"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(r.text)

            filing["local_path"] = filepath
            filing["char_count"] = len(r.text)
            manifest.append(filing)
            print(f"    Saved ({len(r.text):,} chars)")

    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nDone. {len(manifest)} transcripts saved.")
    return manifest

if __name__ == "__main__":
    fetch_and_save()