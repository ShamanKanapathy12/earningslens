# EarningsLens — Retrieval Failure Analysis

## Evaluation Summary
- 20 hand-labeled test cases across AAPL and NVDA
- Pass rate: 95% (19/20)
- Avg faithfulness: 0.90
- Avg recall: 0.80
- Avg precision: 1.00

---

## Failure Mode 1 — Missing Relevant Content (3 cases)

**Root cause**: The 512-word chunk size occasionally splits financial tables
and margin discussions across chunk boundaries. When a CFO discusses gross
margin percentages mid-paragraph, the number appears in one chunk while the
context appears in the adjacent chunk. Neither chunk alone scores high enough
on semantic similarity to be retrieved.

**Example**: ID 14 — NVDA Q2 "How did Nvidia discuss gross margins?"
- Expected keywords: margin, gross, percent
- All 3 missing from top-5 retrieved chunks
- The margin discussion was split across chunk boundary at word 489

**Fix**: Reduce chunk size to 384 words with 100-word overlap, or use
sentence-aware chunking that never splits mid-sentence.

---

## Failure Mode 2 — Fiscal vs Calendar Quarter Mismatch

**Root cause**: Some companies report on fiscal quarters that don't align
with calendar quarters. A filing labeled Q1 in our system may correspond
to a different period than the user expects.

**Fix**: Store fiscal quarter end dates as metadata and expose them in the UI.

---

## Failure Mode 3 — Sparse Quarters

**Root cause**: NVDA Q1 has only 7 chunks vs AAPL Q2's 1284 chunks.
Sparse quarters have less coverage so niche questions may miss relevant
content entirely.

**Fix**: Flag quarters with fewer than 20 chunks as limited coverage
in the UI and warn the user.

---

## Failure Mode 4 — Keyword Abstraction Gap

**Root cause**: The rule-based sentiment scorer uses exact keyword matching.
Synonyms and paraphrases are missed.

**Fix**: Replace rule-based scorer with LLM-based scoring (planned for v2).

---

## What This Means for Production

A 95% pass rate on hand-labeled data is strong for a v1 system. The primary
failure mode is well understood and fixable with a one-line change to chunk
size. The evaluation harness can be re-run after any change to measure
regression.
