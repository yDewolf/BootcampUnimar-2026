import sys
import json
from solution import Solution

def main():
    test_suite_json = sys.argv[1]
    test_cases = json.loads(test_suite_json)

    solution_instance = Solution()
    for idx, test in enumerate(test_cases):
        inputs = test["inputs"]
        expected = test["expected"]

        try:
            user_output = solution_instance.solve(**inputs)

        except Exception as e:
            print(json.dumps({
                "status": "RUNTIME_ERROR",
                "test_case": idx + 1,
                "error": str(e)
            }))
            sys.exit(1)

        if user_output != expected:
            print(json.dumps({
                "status": "WRONG_ANSWER",
                "test_case": idx + 1,
                "input": inputs,
                "expected": expected,
                "actual": user_output
            }))
            sys.exit(0)

    print(json.dumps({"status": "ACCEPTED"}))

if __name__ == "__main__":
    main()