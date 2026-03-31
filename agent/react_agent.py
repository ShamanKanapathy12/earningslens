import os
from groq import Groq
from dotenv import load_dotenv
from agent.tools import retrieve_context, compare_quarters
from agent.sentiment import compare_sentiment

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

    context_a = "\n".join([f"[{quarter_a} source {i+1}]: {c['text'][:300]}"
                           for i, c in enumerate(chunks_a)])
    context_b = "\n".join([f"[{quarter_b} source {i+1}]: {c['text'][:300]}"
                           for i, c in enumerate(chunks_b)])

    prompt = f"""You are a senior financial analyst. A user asked:
"{user_question}"

You are comparing {company}'s earnings calls from {quarter_a} and {quarter_b}.

{quarter_a} sentiment scores: optimism={score_a['optimism']}, caution={score_a['caution']}, growth_confidence={score_a['growth_confidence']}, uncertainty={score_a['uncertainty']}
{quarter_a} summary: {score_a['summary']}

{quarter_b} sentiment scores: optimism={score_b['optimism']}, caution={score_b['caution']}, growth_confidence={score_b['growth_confidence']}, uncertainty={score_b['uncertainty']}
{quarter_b} summary: {score_b['summary']}

{quarter_a} transcript excerpts:
{context_a}

{quarter_b} transcript excerpts:
{context_b}

Write a clear 4-5 sentence analyst-style response that:
1. Directly answers the user's question
2. Compares the tone and content between the two quarters
3. References specific sources like [Q1 source 1] as evidence
4. Ends with a one-line verdict on how management tone shifted

Be specific and analytical, not generic."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    final_answer = response.choices[0].message.content.strip()

    return {
        "question": user_question,
        "company": company,
        "quarter_a": quarter_a,
        "quarter_b": quarter_b,
        "sentiment": sentiment,
        "answer": final_answer,
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
