import sys
import json
import importlib.util

def run():
    gen_code_file = sys.argv[1] # ex: exercise_0.py
    class_name = sys.argv[2] # ex: SampleGenerator
    total_cases = int(sys.argv[3])

    # import do módulo de geração de samples
    spec = importlib.util.spec_from_file_location("gen_module", gen_code_file)
    assert spec
    assert spec.loader
    gen_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen_module)

    # instanciação da classe que gera os samples (baseada no BaseSampleGenerator)
    generator_class = getattr(gen_module, class_name)
    generator = generator_class()

    test_suite = []
    try:
        for _ in range(total_cases):
            test_case = generator.generate_test_case()
            test_suite.append(test_case)
    except Exception as e:
        print("Failed to generate samples ", e)
        return

    print(json.dumps(test_suite))

if __name__ == "__main__":
    run()
