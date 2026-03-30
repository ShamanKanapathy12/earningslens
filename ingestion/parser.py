import os
import re
from bs4 import BeautifulSoup
import json

def clean_html(text: str) -> str:
    """Strip HTML tags and clean whitespace."""
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ")
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def extract_earnings_section(text: str) -> str:
    """Try to isolate the actual earnings call content."""
    
    # Look for common earnings call markers
    markers = [
        "earnings conference call",
        "earnings call transcript",
        "question and answer",
        "operator:",
        "good morning",
        "good afternoon",
        "good evening"
    ]
    
    text_lower = text.lower()
    start_pos = 0
    
    for marker in markers:
        pos = text_lower.find(marker)
        if pos != -1:
            start_pos = pos
            break
    
    return text[start_pos:] if start_pos > 0 else text

def parse_filing(filepath: str) -> dict:
    """Parse a raw SEC filing into clean text + metadata."""
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    
    # Clean HTML
    cleaned = clean_html(raw)
    
    # Try to extract earnings section
    content = extract_earnings_section(cleaned)
    
    # Pull metadata from filename
    filename = os.path.basename(filepath)
    parts = filename.replace(".txt", "").split("_")
    company = parts[0]
    date = parts[1]
    
    return {
        "company": company,
        "date": date,
        "filepath": filepath,
        "char_count": len(content),
        "content": content
    }

def parse_all(raw_dir: str = "data/raw", output_dir: str = "data/parsed"):
    """Parse all raw filings and save cleaned versions."""
    
    os.makedirs(output_dir, exist_ok=True)
    parsed = []
    
    for filename in os.listdir(raw_dir):
        if not filename.endswith(".txt"):
            continue
        
        filepath = os.path.join(raw_dir, filename)
        print(f"Parsing {filename}...")
        
        result = parse_filing(filepath)
        
        # Save cleaned text
        out_filename = filename.replace(".txt", "_parsed.txt")
        out_path = os.path.join(output_dir, out_filename)
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result["content"])
        
        result["parsed_path"] = out_path
        result.pop("content")  # don't store in manifest, it's in the file
        parsed.append(result)
        print(f"  {result['char_count']:,} chars → {out_filename}")
    
    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        json.dump(parsed, f, indent=2)
    
    print(f"\nDone. {len(parsed)} files parsed.")
    return parsed

if __name__ == "__main__":
    parse_all()