import json
from eval_harness import run_evaluation

def test_evaluation_execution():
    results = run_evaluation()
    assert "task_1" in results
    assert "task_2" in results
    assert len(results["task_1"]) == 5
    assert len(results["task_2"]) == 5
    
    with open("eval_report.json", "r") as f:
        data = json.load(f)
        assert data == results