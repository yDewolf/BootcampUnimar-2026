from typing import Any, Protocol, TypedDict

class TestCase(TypedDict):
    inputs: dict
    expected: Any

class ISampleGenerator(Protocol):
    def generate_inputs(self) -> dict[str, Any]: 
        """Gera os argumentos que serão passados para o Solver"""
        ...

    def solver(self, *args: Any) -> Any: 
        """Gera um resultado a partir dos argumentos"""
        ...

    def generate_test_case(self) -> tuple[str, str]: 
        ...

class BaseSampleGenerator(ISampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        raise NotImplementedError

    def solver(self, **kwargs: Any) -> Any:
        raise NotImplementedError
    
    def generate_test_case(self) -> TestCase:
        sample = self.generate_inputs()
        result = self.solver(**sample)

        return {"inputs": sample, "expected": result}
