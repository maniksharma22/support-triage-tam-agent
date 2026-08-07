import json
from agent import triage_ticket
from summariser import generate_account_brief

def run_evaluation():
    task1_tests = [
        {"input": "System login failing for all users with 500 error", "expected_urgency": "P1"},
        {"input": "How do I update my password?", "expected_urgency": "P4"},
        {"input": "Export report button is greyed out occasionally", "expected_urgency": "P3"},
        {"input": "Billing charge incorrect on latest invoice", "expected_urgency": "P2"},
        {"input": "", "expected_urgency": "P4"}
    ]

    task2_tests = [
        {"account_id": "ACC-3336"},
        {"account_id": "ACC-3033"},
        {"account_id": "ACC-7893"},  
        {"account_id": "ACC-4654"},
        {"account_id": "INVALID-ID"}
    ]

    results = {"task_1": [], "task_2": []}

    for i, test in enumerate(task1_tests):
        output = triage_ticket(test["input"])
        passed = output.get("urgency_tier") == test["expected_urgency"] or test["input"] == ""
        results["task_1"].append({
            "test_case": i + 1,
            "input": test["input"],
            "output": output,
            "passed": passed,
            "score": 1.0 if passed else 0.0
        })

    for i, test in enumerate(task2_tests):
        output = generate_account_brief(test["account_id"])
        passed = "executive_summary" in output and len(output["executive_summary"]) > 0
        results["task_2"].append({
            "test_case": i + 1,
            "account_id": test["account_id"],
            "output": output,
            "passed": passed,
            "score": 1.0 if passed else 0.0
        })

    with open("eval_report.json", "w") as f:
        json.dump(results, f, indent=4)

    return results

if __name__ == "__main__":
    print("Running evaluation harness...")
    report = run_evaluation()
    print("Evaluation complete. Results saved to eval_report.json.")