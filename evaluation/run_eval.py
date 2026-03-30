import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from evaluation.evaluator import run_single_test

def run_full_eval():
    with open("evaluation/test_cases.json", "r") as f:
        test_cases = json.load(f)

    print(f"Running evaluation on {len(test_cases)} test cases...\n")

    results = []
    for tc in test_cases:
        print(f"  [{tc['id']}/20] {tc['company']} {tc['quarter']}: {tc['question'][:50]}...")
        result = run_single_test(tc)
        results.append(result)

    # Summary stats
    passed = sum(1 for r in results if r["passed"])
    avg_faithfulness = round(sum(r["faithfulness_score"] for r in results) / len(results), 2)
    avg_recall = round(sum(r["recall"]["recall_score"] for r in results) / len(results), 2)
    avg_precision = round(sum(r["precision"]["precision_score"] for r in results) / len(results), 2)

    # Failure analysis
    failure_modes = {}
    for r in results:
        if r["failure_mode"]:
            fm = r["failure_mode"]
            failure_modes[fm] = failure_modes.get(fm, 0) + 1

    summary = {
        "total_tests": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": f"{round(passed/len(results)*100)}%",
        "avg_faithfulness": avg_faithfulness,
        "avg_recall": avg_recall,
        "avg_precision": avg_precision,
        "failure_modes": failure_modes
    }

    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    print(f"Pass rate:         {summary['pass_rate']} ({passed}/{len(results)})")
    print(f"Avg faithfulness:  {avg_faithfulness}")
    print(f"Avg recall:        {avg_recall}")
    print(f"Avg precision:     {avg_precision}")
    print(f"\nFailure modes:")
    for mode, count in failure_modes.items():
        print(f"  {mode}: {count} cases")

    # Save results
    with open("evaluation/results.json", "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    print(f"\nFull results saved to evaluation/results.json")
    return summary

if __name__ == "__main__":
    run_full_eval()
