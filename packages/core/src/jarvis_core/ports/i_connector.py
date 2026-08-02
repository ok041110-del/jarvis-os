"""IConnector — Port. MCP 등 외부 도구 연결의 추상 인터페이스."""
from abc import ABC, abstractmethod
from typing import Any


class IConnector(ABC):
    @abstractmethod
    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        raise NotImplementedError
