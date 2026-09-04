from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        size = random.randint(5, 30)
        nums = random.sample(range(-100, 100), size)
        i, j = random.sample(range(size), 2)
        target = nums[i] + nums[j]
        return {"nums": nums, "target": target}

    def solver(self, nums: list[int], target: int) -> list[int]:
        seen = {}
        for idx, num in enumerate(nums):
            diff = target - num
            if diff in seen:
                return [seen[diff], idx]
            seen[num] = idx
        return []
