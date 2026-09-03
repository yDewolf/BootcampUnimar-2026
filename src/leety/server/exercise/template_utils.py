import ast
from enum import Enum
from typing import Optional

from leety.common.utils.str_utils import split_in_lines
from leety.server.exercise.base_generator import TestCase

class TemplateUtils:
    @staticmethod
    def extract_solution_annotations(generator_code: str, target_method: str = "solver") -> tuple[dict[str, str], str]:
        # Talvez isso não seja tão seguro, mas pelo menos assim eu não teria
        # que compilar o código e usar um inspect para pegar os parâmetros
        # e depois ter que repassar esses parâmetros para gerar o template
        tree = ast.parse(generator_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == target_method:
                params: dict[str, str] = {}
                for arg in node.args.args:
                    if arg.arg == "self":
                        continue
                    
                    if arg.annotation:
                        params[arg.arg] = ast.unparse(arg.annotation)
                        continue
                    params[arg.arg] = "Any"

                return_type: str = "Any"
                if node.returns:
                    return_type = ast.unparse(node.returns)

                return (params, return_type)

        raise ValueError(f"Couldn't find {target_method}")

    @staticmethod
    def create_solution_template(solve_annotations: tuple[dict[str, str], str], template_header: str = "", function_comments: str = "") -> str:
        args, return_type = solve_annotations
        arg_def_str: list[str] = [
            f"{arg}: {type_hint}" for arg, type_hint in args.items()
        ]

        return (
f"""from typing import Any

{template_header}

class Solution:
    def solve(self, {", ".join(arg_def_str)}) -> {return_type}:
        {function_comments}
        pass
"""
        )

    @staticmethod
    def create_exercise_header(title: str, id: str, context: str, difficulty: str, example_cases: Optional[list[TestCase]], authors: list[str], max_width: int = 75) -> str:
        context_lines = split_in_lines(context, max_width)
        case_strs: list[str] = []
        for sample in example_cases or []:
            inputs = sample["inputs"]
            expected = sample["expected"]
            input_list: list[str] = [
                f"{key}={value}" for key, value in inputs.items()
            ]

            case_strs.append(
                f"solve({", ".join(input_list)}) -> {expected}"
            )
        
        return (
f"""# Exercício - {title} #{id}
# Dificuldade: {difficulty}
# Autores: {",".join(authors)}

# Contextualização:
#{"\n#".join(context_lines)}

# Exemplos de Input / Output
#{"\n#".join(case_strs)}
"""
        )

    @staticmethod
    def create_function_comments(comment: str, max_width: int = 75) -> str:
        comment_lines = split_in_lines(comment, max_width)
        return f"#{"\n#".join(comment_lines)}"
    