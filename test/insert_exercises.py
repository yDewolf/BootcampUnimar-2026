from leety.common.database.models.exercise_model import ExerciseModel
from leety.server.server import Server


server = Server()
admin_user = server.user_controller.get_user_by_username("Google Gemini")
assert admin_user
assert admin_user.id

exercise_controller = server.exercise_controller

# Esses exercícios foram gerados pelo gemini porque já é o último dia e não vai dar tempo de
# criar exercícios customizados. Peço perdão caso algum deles não esteja funcionando corretamente

# ==========================================
# EASY (1 a 5)
# ==========================================
exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="easy",
        title="Soma de Dois Números",
        context="Dado dois números inteiros `n0` e `n1`, retorne a soma entre eles.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        return {"n0": random.randint(-100, 100), "n1": random.randint(-100, 100)}

    def solver(self, n0: int, n1: int) -> int:
        return n0 + n1
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="easy",
        title="Par ou Ímpar",
        context="Receba um número inteiro `n` e retorne `True` se for par ou `False` caso contrário.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        return {"n": random.randint(-1000, 1000)}

    def solver(self, n: int) -> bool:
        return n % 2 == 0
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="easy",
        title="Contagem de Vogais",
        context="Dada uma string `text`, retorne a quantidade total de vogais (a, e, i, o, u) presentes nela (ignorando case).",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
import random
import string

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        chars = string.ascii_letters + " "
        s = "".join(random.choice(chars) for _ in range(random.randint(5, 30)))
        return {"text": s}

    def solver(self, text: str) -> int:
        return sum(1 for char in text.lower() if char in "aeiou")
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="easy",
        title="Inverter String",
        context="Dada uma string `text`, retorne a string invertida.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
import random
import string

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        chars = string.ascii_letters
        s = "".join(random.choice(chars) for _ in range(random.randint(3, 20)))
        return {"text": s}

    def solver(self, text: str) -> str:
        return text[::-1]
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="easy",
        title="Maior Elemento da Lista",
        context="Dada uma lista não vazia de inteiros `nums`, retorne o maior valor presente nela.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
import random

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        size = random.randint(1, 20)
        nums = [random.randint(-100, 100) for _ in range(size)]
        return {"nums": nums}

    def solver(self, nums: list[int]) -> int:
        return max(nums)
""",
    ),
)

# ==========================================
# MEDIUM (6 a 10)
# ==========================================
exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="medium",
        title="Two Sum",
        context="Dada uma lista de inteiros `nums` e um inteiro `target`, retorne os índices dos dois números cuja soma seja igual a `target`.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
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
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="medium",
        title="Verificar Anagrama",
        context="Dadas duas strings `s1` e `s2`, retorne `True` se uma for anagrama da outra.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
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
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="medium",
        title="Número Faltante",
        context="Dada uma lista `nums` de tamanho `n` contendo números distintos no intervalo de `0` a `n`, retorne o único número do intervalo que está faltando.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
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
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="medium",
        title="Compactação de String (Run-Length Encoding)",
        context="Dada uma string `s`, retorne uma versão compactada substituindo repetições consecutivas de um caractere pelo caractere seguido da quantidade de repetições. Ex: 'aab' -> 'a2b1'.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
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
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="medium",
        title="Fatorial com Memoização/Iterativo",
        context="Receba um número inteiro `n` (0 <= n <= 20) e retorne o valor do seu fatorial (`n!`).",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
import random
import math

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        return {"n": random.randint(0, 20)}

    def solver(self, n: int) -> int:
        return math.factorial(n)
""",
    ),
)

# ==========================================
# HARD (11 a 15)
# ==========================================
exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="hard",
        title="Maior Substring sem Repetição",
        context="Dada uma string `s`, encontre o comprimento da maior substring sem caracteres repetidos.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
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
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="hard",
        title="Subarray com Maior Soma (Kadane)",
        context="Dada uma lista de inteiros `nums`, encontre a soma do subarray contíguo que possui a maior soma.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
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
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="hard",
        title="Mesclar Intervalos Sobrepostos",
        context="Dada uma lista de intervalos `intervals` onde `intervals[i] = [start, end]`, mescle todos os intervalos sobrepostos e retorne a lista final.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
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
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="hard",
        title="Validador de Parênteses / Expressão",
        context="Dada uma string `s` contendo apenas os caracteres '(', ')', '{', '}', '[' e ']', determine se a sequência de parênteses é válida.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
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
""",
    ),
)

exercise_controller.create_exercise(
    admin_user.id,
    ExerciseModel(
        id=None,
        diff_id="hard",
        title="Menor Número de Saltos (Jump Game II)",
        context="Dada uma lista de inteiros não negativos `nums` onde cada elemento representa o número máximo de passos que você pode saltar a partir daquela posição, retorne o número mínimo de saltos para atingir o último índice.",
        time_limit=90,
        memory_limit=16,
        _sample_gen_code="""from base_generator import BaseSampleGenerator, Any
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
""",
    ),
)

server.database.save()