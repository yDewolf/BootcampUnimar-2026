from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        size = random.randint(10, 40)
        nums = [random.randint(-50, 50) for _ in range(size)]
        return {"nums": nums}

    def solver(self, nums: list[int]) -> int:
        max_so_far = nums[0]
        curr_max = nums[0]
        for x in nums[1:]:
            curr_max = max(x, curr_max + x)
            max_so_far = max(max_so_far, curr_max)
        return max_so_far
