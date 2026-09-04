from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        brackets = ["()", "{}", "[]"]
        if random.choice([True, False]):
            s = "".join(random.choice(brackets) for _ in range(random.randint(2, 8)))
        else:
            invalid_chars = "({[" if random.choice([True, False]) else ")}]"
            s = "".join(random.choice(invalid_chars) for _ in range(random.randint(3, 9)))
        return {"s": s}

    def solver(self, s: str) -> bool:
        stack = []
        mapping = {")": "(", "}": "{", "]": "["}
        for char in s:
            if char in mapping:
                top_element = stack.pop() if stack else '#'
                if mapping[char] != top_element:
                    return False
            else:
                stack.append(char)
        return not stack
