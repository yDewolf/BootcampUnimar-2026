from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        n = random.randint(5, 50)
        full_set = list(range(n + 1))
        missing = random.choice(full_set)
        full_set.remove(missing)
        random.shuffle(full_set)
        return {"nums": full_set}

    def solver(self, nums: list[int]) -> int:
        n = len(nums)
        expected_sum = n * (n + 1) // 2
        return expected_sum - sum(nums)
