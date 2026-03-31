import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def score_sentiment(chunks: list, company: str, quarter: str) -> dict:
    combined_text = "\n\n".join([c["text"] for c in chunks])[:4000]

    prompt = f"""You are a financial analyst reading an earnings call transcript.

Below is an excerpt from {company}'s {quarter} earnings call:

{combined_text}

Score the management's tone on these 4 dimensions from 0 to 100:
- optimism: how positive and confident is the tone? (0=very pessimistic, 100=very optimistic)
- caution: how cautious or hedging is the language? (0=no caution, 100=extremely cautious)
- growth_confidence: how confident are they about future growth? (0=no confidence, 100=very confident)
- uncertainty: how much uncertainty do they express? (0=no uncertainty, 100=very uncertain)

Respond ONLY with a JSON object, no explanation, no markdown backticks:
{{
  "optimism": 75,
  "caution": 30,
  "growth_confidence": 70,
  "uncertainty": 25,
  "summary": "One sentence summary of the overall tone"
}}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def compare_sentiment(company: str, quarter_a_chunks: list, quarter_b_chunks: list,
                      quarter_a_label: str, quarter_b_label: str) -> dict:
    print(f"Scoring {quarter_a_label}...")
    score_a = score_sentiment(quarter_a_chunks, company, quarter_a_label)

    print(f"Scoring {quarter_b_label}...")
    score_b = score_sentiment(quarter_b_chunks, company, quarter_b_label)

    dimensions = ["optimism", "caution", "growth_confidence", "uncertainty"]
    delta = {}
    for dim in dimensions:
        delta[dim] = score_b[dim] - score_a[dim]

    return {
        "company": company,
        "quarter_a": {"label": quarter_a_label, "scores": score_a},
        "quarter_b": {"label": quarter_b_label, "scores": score_b},
        "delta": delta
    }
