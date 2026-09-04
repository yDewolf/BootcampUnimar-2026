from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        return {"n": random.randint(-1000, 1000)}

    def solver(self, n: int) -> bool:
        return n % 2 == 0
