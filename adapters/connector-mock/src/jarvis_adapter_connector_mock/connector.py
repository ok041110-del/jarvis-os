"""IConnector의 Walking Skeleton 구현. 실제 외부 서버 대신 고정된 응답을 반환해
Adapter Reversibility(ADR-0006 결정 11)를 값싸게 증명하는 데 쓰인다 — 실제 MCP
Connector(`adapters/connector-mcp`)를 제거하고 이 Adapter로 되돌려도 Core/Agent가
무수정으로 동일하게 동작해야 한다.
"""
from __future__ import annotations

from jarvis_core.connector.models import ToolCallStatus, ToolResponse, ToolRequest
from jarvis_core.ports.i_connector import IConnector


class MockConnector(IConnector):
    def __init__(self, name: str, capabilities: list[str]) -> None:
        self.name = name
        self._capabilities = list(capabilities)
        self.call_log: list[ToolRequest] = []

    @property
    def capabilities(self) -> list[str]:
        return self._capabilities

    def call_tool(self, request: ToolRequest) -> ToolResponse:
        self.call_log.append(request)
        return ToolResponse(
            status=ToolCallStatus.SUCCESS,
            result={
                "connector": self.name,
                "tool": request.tool_name,
                "result": f"[mock] {request.tool_name} 호출 성공",
            },
        )


def create_filesystem_mock() -> MockConnector:
    return MockConnector("filesystem-mock", ["filesystem"])


def create_fetch_mock() -> MockConnector:
    return MockConnector("fetch-mock", ["fetch"])
