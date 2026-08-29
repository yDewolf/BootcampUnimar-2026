from typing import Any, Protocol, TypedDict

class TestCase(TypedDict):
    inputs: list[Any]
    expected: Any

class ISampleGenerator(Protocol):
    def generate_sample(self) -> list[Any]: 
        """Gera os argumentos que serão passados para o Solver"""
        ...

    def generate_result(self, *args: Any) -> Any: 
        """Gera um resultado a partir dos argumentos"""
        ...

    def generate_test_case(self) -> tuple[str, str]: 
        ...

class BaseSampleGenerator(ISampleGenerator):
    def generate_inputs(self) -> list[Any]:
        raise NotImplementedError

    def solver(self, *args: Any) -> Any:
        raise NotImplementedError
    
    def generate_test_case(self) -> TestCase:
        sample = self.generate_sample()
        result = self.generate_result(sample)

        return TestCase(inputs=sample, expected=result)
