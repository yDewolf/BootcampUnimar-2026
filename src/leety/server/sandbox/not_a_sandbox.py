import subprocess
import json

def run_sample_generation(code_path: str, class_name: str, num_cases: int = 80):
    result = subprocess.run(
        ["python3", "exercise_sample_runner.py", code_path, class_name, str(num_cases)],
        capture_output=True,
        text=True,
        timeout=10.0
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    
    raise Exception(f"Erro no gerador: {result.stderr}")

def run_solution(solution_path: str, tests: list[dict]):
    tests_json = json.dumps(tests)
    result = subprocess.run(
        ["python3", "exercise_solution_runner.py", tests_json],
        capture_output=True,
        text=True,
        timeout=3.0
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return {"status": "ERROR", "stderr": result.stderr}