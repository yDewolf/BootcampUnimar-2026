from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        count = random.randint(5, 15)
        intervals = []
        for _ in range(count):
            start = random.randint(0, 50)
            end = start + random.randint(1, 15)
            intervals.append([start, end])
        return {"intervals": intervals}

    def solver(self, intervals: list[list[int]]) -> list[list[int]]:
        if not intervals:
            return []
        intervals.sort(key=lambda x: x[0])
        merged = [intervals[0]]
        for current in intervals[1:]:
            prev = merged[-1]
            if current[0] <= prev[1]:
                prev[1] = max(prev[1], current[1])
            else:
                merged.append(current)
        return merged
