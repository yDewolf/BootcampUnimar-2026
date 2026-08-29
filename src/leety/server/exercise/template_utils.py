import ast

from leety.common.utils.str_utils import split_in_lines

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
    def create_exercise_header(title: str, id: str, context: str, difficulty: str, max_width: int = 75) -> str:
        context_lines = split_in_lines(context, max_width)

        return (
f"""# Exercício - {title} #{id}
# Dificuldade: {difficulty}

# Contextualização:
#{"\n#".join(context_lines)}"""
        )