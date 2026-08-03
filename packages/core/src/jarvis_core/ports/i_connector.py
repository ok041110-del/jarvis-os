"""IConnector — Port. MCP 등 외부 도구 연결의 추상 인터페이스.

ADR-0006 결정 1·9: Connector는 단일 Tool 호출의 실행만 책임진다 — 무엇을 호출할지
결정하지 않고, 결과를 해석하지 않고, 허용 여부를 판단하지 않는다.

Fail-Closed 계약(ADR-0006 결정 9, ADR-0005 결정 4와 동일 패턴): `call_tool()`은
절대 예외를 던지지 않는다. 연결 실패·프로토콜 오류·타임아웃 등 어떤 원인이든
`ToolResponse`로 변환해 반환해야 하며, `status != SUCCESS`인 경우 `error`가 반드시
채워져야 한다(No Silent Failure). 호출자는 이 메서드를 try/except로 방어하지 않는다.
"""
from abc import ABC, abstractmethod

from jarvis_core.connector.models import ToolRequest, ToolResponse


class IConnector(ABC):
    @property
    @abstractmethod
    def capabilities(self) -> list[str]:
        """이 Connector가 제공하는 Capability 이름 목록(ADR-0006 결정 12).

        Agent는 이 이름을 통해서만 Connector를 필요로 한다 — 어떤 구현체(MCP/Mock/
        HTTP)가 이 Capability를 제공하는지는 알지 못한다. 실제 선택은 Connector
        Discovery/Registry의 책임이다.
        """
        ...

    @abstractmethod
    def call_tool(self, request: ToolRequest) -> ToolResponse:
        """단일 Tool 호출을 실행하고 결과를 반환한다. 절대 예외를 던지지 않는다."""
        raise NotImplementedError
