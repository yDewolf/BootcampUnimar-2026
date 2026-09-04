from base_generator import BaseSampleGenerator, Any
import random
import string

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        chars = string.ascii_lowercase[:10]
        s = "".join(random.choice(chars) for _ in range(random.randint(15, 60)))
        return {"s": s}

    def solver(self, s: str) -> int:
        char_map = {}
        left = 0
        max_len = 0
        for right, char in enumerate(s):
            if char in char_map and char_map[char] >= left:
                left = char_map[char] + 1
            char_map[char] = right
            max_len = max(max_len, right - left + 1)
        return max_len
