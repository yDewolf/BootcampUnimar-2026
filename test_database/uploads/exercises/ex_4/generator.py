from base_generator import BaseSampleGenerator, Any
import random
import string

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        chars = string.ascii_letters + " "
        s = "".join(random.choice(chars) for _ in range(random.randint(5, 30)))
        return {"text": s}

    def solver(self, text: str) -> int:
        return sum(1 for char in text.lower() if char in "aeiou")
