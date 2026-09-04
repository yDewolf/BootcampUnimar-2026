from base_generator import BaseSampleGenerator, Any
import random
import math

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        return {"n": random.randint(0, 20)}

    def solver(self, n: int) -> int:
        return math.factorial(n)
