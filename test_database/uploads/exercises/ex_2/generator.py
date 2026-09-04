from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        return {"n0": random.randint(-100, 100), "n1": random.randint(-100, 100)}

    def solver(self, n0: int, n1: int) -> int:
        return n0 + n1
