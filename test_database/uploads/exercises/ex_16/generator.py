from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        size = random.randint(5, 20)
        nums = [random.randint(1, 4) for _ in range(size)]
        return {"nums": nums}

    def solver(self, nums: list[int]) -> int:
        if len(nums) <= 1:
            return 0
        jumps = 0
        current_end = 0
        farthest = 0
        for i in range(len(nums) - 1):
            farthest = max(farthest, i + nums[i])
            if i == current_end:
                jumps += 1
                current_end = farthest
                if current_end >= len(nums) - 1:
                    break
        return jumps
