"""IConnector의 Walking Skeleton 구현. 실제 MCP 서버 대신 고정된 응답을 반환해
Agent -> MCP 경로 자체(호출이 실제로 발생하는지)만 증명한다.
"""
from typing import Any
from jarvis_core.ports.i_connector import IConnector


class MockConnector(IConnector):
    def __init__(self, name: str) -> None:
        self.name = name
        self.call_log: list[tuple[str, dict]] = []

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        self.call_log.append((tool_name, arguments))
        return {"connector": self.name, "tool": tool_name, "result": f"[mock] {tool_name} 호출 성공"}
