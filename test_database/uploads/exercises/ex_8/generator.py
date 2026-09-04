from base_generator import BaseSampleGenerator, Any
import random
import string

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        length = random.randint(4, 15)
        base = [random.choice(string.ascii_lowercase) for _ in range(length)]
        if random.choice([True, False]):
            s1 = "".join(base)
            s2 = "".join(random.sample(base, len(base)))
        else:
            s1 = "".join(base)
            s2 = "".join(random.choice(string.ascii_lowercase) for _ in range(length))
        return {"s1": s1, "s2": s2}

    def solver(self, s1: str, s2: str) -> bool:
        return sorted(s1) == sorted(s2)
