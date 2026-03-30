from agent.tools import retrieve_context, compare_quarters
from agent.sentiment import compare_sentiment

def run_agent(user_question: str, company: str, quarter_a: str, quarter_b: str) -> dict:
    print(f"\nAgent starting...")
    print(f"Question: {user_question}")
    print(f"Company: {company} | Comparing: {quarter_a} vs {quarter_b}")

    print("\n[ACT] Retrieving context for both quarters...")
    comparison = compare_quarters(company, user_question, quarter_a, quarter_b)
    chunks_a = comparison["quarter_a"]["chunks"]
    chunks_b = comparison["quarter_b"]["chunks"]

    print("\n[ACT] Scoring sentiment...")
    sentiment = compare_sentiment(
        company=company,
        quarter_a_chunks=chunks_a,
        quarter_b_chunks=chunks_b,
        quarter_a_label=quarter_a,
        quarter_b_label=quarter_b
    )

    print("\n[ACT] Synthesizing final answer...")
    score_a = sentiment["quarter_a"]["scores"]
    score_b = sentiment["quarter_b"]["scores"]
    delta = sentiment["delta"]

    opt_change = "improved" if delta["optimism"] > 0 else "declined"
    cau_change = "increased" if delta["caution"] > 0 else "decreased"

    sources_a = [f"[{quarter_a} source {i+1}]: {c['text'][:150]}..." for i, c in enumerate(chunks_a[:2])]
    sources_b = [f"[{quarter_b} source {i+1}]: {c['text'][:150]}..." for i, c in enumerate(chunks_b[:2])]

    answer = f"""Analysis for {company} — {quarter_a} vs {quarter_b}

{quarter_a} tone: {score_a['summary']}
{quarter_b} tone: {score_b['summary']}

Sentiment shift: Optimism {opt_change} by {abs(delta['optimism'])} points. Caution {cau_change} by {abs(delta['caution'])} points.
Growth confidence moved from {score_a['growth_confidence']} to {score_b['growth_confidence']}.

Key passages from {quarter_a}:
{sources_a[0]}

Key passages from {quarter_b}:
{sources_b[0]}

Verdict: Management tone {'strengthened' if delta['optimism'] > 0 else 'weakened'} between {quarter_a} and {quarter_b}."""

    return {
        "question": user_question,
        "company": company,
        "quarter_a": quarter_a,
        "quarter_b": quarter_b,
        "sentiment": sentiment,
        "answer": answer,
        "sources": {quarter_a: chunks_a, quarter_b: chunks_b}
    }

if __name__ == "__main__":
    result = run_agent(
        user_question="How did management discuss revenue growth and future outlook?",
        company="AAPL",
        quarter_a="Q1",
        quarter_b="Q3"
    )

    print("\n" + "="*50)
    print("FINAL ANSWER")
    print("="*50)
    print(result["answer"])
    print("\nSentiment Delta:")
    for dim, val in result["sentiment"]["delta"].items():
        direction = "↑" if val > 0 else "↓"
        print(f"  {dim}: {direction} {abs(val)} points")
