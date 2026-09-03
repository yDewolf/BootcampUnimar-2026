from base_generator import BaseSampleGenerator, Any

class SampleGenerator(BaseSampleGenerator):
    def generate_inputs(self) -> dict[str, Any]:
        # Implemente essa funÃ§Ã£o para gerar os valores a serem passados para o solver
        raise NotImplementedError

    def solver(self, **kwargs: Any) -> Any:
        # Implemente essa funÃ§Ã£o para gerar os resultados para uma determinada entrada
        raise NotImplementedError
