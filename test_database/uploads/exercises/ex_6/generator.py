from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        size = random.randint(1, 20)
        nums = [random.randint(-100, 100) for _ in range(size)]
        return {"nums": nums}

    def solver(self, nums: list[int]) -> int:
        return max(nums)
