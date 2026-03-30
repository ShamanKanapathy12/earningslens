import json

POSITIVE_WORDS = [
    "growth", "record", "strong", "exceeded", "beat", "momentum", "confident",
    "optimistic", "opportunity", "expanded", "increased", "gained", "robust",
    "outperformed", "accelerating", "raised", "upside", "demand", "innovation"
]

NEGATIVE_WORDS = [
    "decline", "weak", "challenging", "headwind", "uncertain", "cautious",
    "slowdown", "missed", "pressure", "risk", "concern", "volatile", "reduced",
    "difficult", "lower", "soft", "macro", "uncertainty", "disappointed"
]

CAUTION_WORDS = [
    "may", "might", "could", "potentially", "possible", "expect", "anticipate",
    "approximately", "roughly", "subject to", "depending", "if", "assuming",
    "cautious", "monitor", "watch", "careful", "prudent", "conservative"
]

def score_sentiment(chunks: list, company: str, quarter: str) -> dict:
    combined_text = " ".join([c["text"] for c in chunks]).lower()
    words = combined_text.split()
    total_words = len(words)

    pos_count = sum(1 for w in words if w.strip(".,!?") in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w.strip(".,!?") in NEGATIVE_WORDS)
    cau_count = sum(1 for w in words if w.strip(".,!?") in CAUTION_WORDS)

    # Normalize to 0-100
    pos_ratio = min(pos_count / max(total_words, 1) * 500, 100)
    neg_ratio = min(neg_count / max(total_words, 1) * 500, 100)
    cau_ratio = min(cau_count / max(total_words, 1) * 500, 100)

    optimism = round(max(0, min(100, 50 + pos_ratio - neg_ratio)))
    caution = round(min(100, cau_ratio * 2))
    growth_confidence = round(max(0, min(100, optimism - caution * 0.3)))
    uncertainty = round(min(100, caution * 0.8 + neg_ratio * 0.5))

    # Simple summary
    if optimism > 60:
        tone = "positive and confident"
    elif optimism < 40:
        tone = "cautious and concerned"
    else:
        tone = "neutral with mixed signals"

    return {
        "optimism": optimism,
        "caution": caution,
        "growth_confidence": growth_confidence,
        "uncertainty": uncertainty,
        "summary": f"Management tone was {tone} in {quarter} ({pos_count} positive, {neg_count} negative signals)"
    }

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