from datasets import load_dataset
import os
import json

def load_earnings_transcripts(output_dir: str = "data/raw", max_per_company: int = 3):
    os.makedirs(output_dir, exist_ok=True)

    print("Loading dataset...")
    dataset = load_dataset("lamini/earnings-calls-qa", split="train")

    # Group by company + date to get distinct quarters
    by_company = {}
    for item in dataset:
        ticker = item.get("ticker", "UNKNOWN")
        date = item.get("date", "unknown")
        key = f"{ticker}_{date}"
        
        if ticker not in by_company:
            by_company[ticker] = {}
        if date not in by_company[ticker]:
            by_company[ticker][date] = []
        
        by_company[ticker][date].append(item.get("transcript", ""))

    manifest = []
    target_companies = ["AAPL", "NVDA"]

    for ticker in target_companies:
        if ticker not in by_company:
            print(f"{ticker} not found")
            continue

        # Get 3 distinct quarters
        quarters = list(by_company[ticker].items())[:max_per_company]

        for i, (date, chunks) in enumerate(quarters):
            # Join all chunks for this quarter into one document
            full_text = "\n\n".join(chunks)
            
            # Clean date for filename
            clean_date = date.replace(",", "").replace(" ", "_").replace(":", "")
            filename = f"{ticker}_Q{i+1}_{clean_date}.txt"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(full_text)

            manifest.append({
                "company": ticker,
                "date": date,
                "quarter_label": f"Q{i+1}",
                "local_path": filepath,
                "char_count": len(full_text)
            })

            print(f"  Saved: {filename} ({len(full_text):,} chars)")

    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nDone. {len(manifest)} transcripts saved.")
    return manifest

if __name__ == "__main__":
    load_earnings_transcripts()