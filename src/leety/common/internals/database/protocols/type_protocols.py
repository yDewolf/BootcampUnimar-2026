from typing import Any, Protocol


class TableProtocol(Protocol):
    def _swap_unique_value(self, field_name: str, old_value: Any, new_value: Any) -> None:
        pass
