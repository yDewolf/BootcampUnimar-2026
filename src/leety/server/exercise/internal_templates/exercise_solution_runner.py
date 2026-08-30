import sys
import json

def main():
    test_suite_json = sys.argv[1]
    test_cases = json.loads(test_suite_json)

    try:
        from solution import Solution
    
        solution_instance = Solution()
        for idx, test in enumerate(test_cases):
            inputs = test["inputs"]
            expected = test["expected"]

            try:
                # TODO: talvez calcular o tempo de execução aqui e não no servidor
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
    except ImportError as e:
        print(json.dumps({
            "status": "RUNTIME_ERROR",
            "test_case": 0,
            "error": str(e)
        }))
        sys.exit(0)

if __name__ == "__main__":
    main()