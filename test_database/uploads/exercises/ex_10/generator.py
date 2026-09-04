from base_generator import BaseSampleGenerator, Any
import random
import string

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        chars = random.sample(string.ascii_lowercase, random.randint(3, 8))
        res = []
        for c in chars:
            res.append(c * random.randint(1, 4))
        return {"s": "".join(res)}

    def solver(self, s: str) -> str:
        if not s:
            return ""
        res = []
        count = 1
        for i in range(1, len(s)):
            if s[i] == s[i - 1]:
                count += 1
            else:
                res.append(f"{s[i-1]}{count}")
                count = 1
        res.append(f"{s[-1]}{count}")
        return "".join(res)
