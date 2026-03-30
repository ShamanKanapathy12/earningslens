import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from agent.tools import retrieve_context

def evaluate_context_recall(test_case: dict, retrieved_chunks: list) -> dict:
    """
    Check if retrieved chunks contain expected keywords.
    This measures whether retrieval actually found relevant content.
    """
    combined_text = " ".join([c["text"] for c in retrieved_chunks]).lower()
    expected_keywords = test_case["expected_keywords"]

    matched = [kw for kw in expected_keywords if kw.lower() in combined_text]
    recall_score = len(matched) / len(expected_keywords)

    return {
        "matched_keywords": matched,
        "missing_keywords": [kw for kw in expected_keywords if kw.lower() not in combined_text],
        "recall_score": round(recall_score, 2)
    }

def evaluate_quarter_precision(test_case: dict, retrieved_chunks: list) -> dict:
    """
    Check if retrieved chunks are from the correct quarter.
    This measures whether metadata filtering worked correctly.
    """
    expected_quarter = test_case["expected_quarter"]
    correct = sum(1 for c in retrieved_chunks if c["quarter"] == expected_quarter)
    precision = correct / len(retrieved_chunks) if retrieved_chunks else 0

    return {
        "expected_quarter": expected_quarter,
        "correct_chunks": correct,
        "total_chunks": len(retrieved_chunks),
        "precision_score": round(precision, 2)
    }

def run_single_test(test_case: dict) -> dict:
    """Run evaluation for a single test case."""
    chunks = retrieve_context(
        question=test_case["question"],
        company=test_case["company"],
        quarter=test_case["quarter"],
        top_k=5
    )

    recall = evaluate_context_recall(test_case, chunks)
    precision = evaluate_quarter_precision(test_case, chunks)

    # Faithfulness = average of recall and precision
    faithfulness = round((recall["recall_score"] + precision["precision_score"]) / 2, 2)

    # Classify failure mode
    if precision["precision_score"] < 0.5:
        failure_mode = "wrong_quarter_retrieved"
    elif recall["recall_score"] < 0.5:
        failure_mode = "missing_relevant_content"
    elif faithfulness >= 0.8:
        failure_mode = None
    else:
        failure_mode = "partial_retrieval"

    return {
        "id": test_case["id"],
        "company": test_case["company"],
        "quarter": test_case["quarter"],
        "question": test_case["question"],
        "recall": recall,
        "precision": precision,
        "faithfulness_score": faithfulness,
        "failure_mode": failure_mode,
        "passed": faithfulness >= 0.6
    }
