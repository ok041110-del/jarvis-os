"""IConnector를 MCP(Model Context Protocol) SDK로 구현한다(ADR-0006 결정 2).

PoC 연결 대상: 공식 filesystem 레퍼런스 서버(`@modelcontextprotocol/server-filesystem`,
npx로 실행). fetch 레퍼런스 서버(`mcp-server-fetch`)는 이 환경에 설치된 `mcp` SDK
버전과 호환되지 않아(업스트림 버전 불일치, `McpError` import 실패) 이번 Phase에서는
실제 연결 대상에서 제외한다 — 이는 MCP 구현 세부사항의 문제이지 Architecture 문제가
아니다(ADR-0006 결정 2·11). fetch 자리를 채우는 대체 구현이 필요하면
`adapters/connector-mock`의 fetch-mock을 계속 이용할 수 있다.

이 파일이 담당하는 것(ADR-0006 결정 2):
- ToolRequest(Domain Model)를 MCP `call_tool()` 인자로 변환
- MCP 서버 프로세스(stdio)와의 실제 통신 수행(호출마다 프로세스를 새로 기동하고
  종료 — 세션을 재사용하지 않는 가장 단순한 관리 방식을 PoC 범위로 선택했다)
- MCP 응답/오류/타임아웃을 ToolResponse(Domain Model)로 변환 — 예외를 던지지 않음
  (Fail-Closed, ADR-0006 결정 9)

Core와 Agent는 이 파일 안의 어떤 것도(MCP SDK, stdio, JSON-RPC) 알지 못한다.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from jarvis_core.connector.models import ToolCallStatus, ToolRequest, ToolResponse
from jarvis_core.ports.i_connector import IConnector

_SANDBOX_DIR = Path(__file__).resolve().parent.parent.parent / "sandbox"


class McpConnector(IConnector):
    def __init__(self, name: str, capabilities: list[str], command: str, args: list[str]) -> None:
        self.name = name
        self._capabilities = list(capabilities)
        self._command = command
        self._args = args

    @property
    def capabilities(self) -> list[str]:
        return self._capabilities

    def call_tool(self, request: ToolRequest) -> ToolResponse:
        """Fail-Closed 계약(ADR-0006 결정 9): 어떤 예외든 여기서 잡아 ToolResponse로
        변환한다. 이 메서드는 절대 예외를 밖으로 던지지 않는다."""
        try:
            return asyncio.run(self._call_with_timeout(request))
        except Exception as e:
            return ToolResponse(
                status=ToolCallStatus.FAILURE,
                error=f"mcp connector internal error: {e}",
            )

    async def _call_with_timeout(self, request: ToolRequest) -> ToolResponse:
        timeout_s = request.timeout_ms / 1000
        try:
            return await asyncio.wait_for(self._run(request), timeout=timeout_s)
        except asyncio.TimeoutError:
            return ToolResponse(
                status=ToolCallStatus.TIMEOUT,
                error=f"'{request.tool_name}' 호출이 {request.timeout_ms}ms 내에 응답하지 않음",
            )
        except Exception as e:
            return ToolResponse(status=ToolCallStatus.FAILURE, error=f"MCP 호출 실패: {e}")

    async def _run(self, request: ToolRequest) -> ToolResponse:
        params = StdioServerParameters(command=self._command, args=self._args)
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(request.tool_name, request.arguments)
                text = _extract_text(result)
                if getattr(result, "is_error", False):
                    return ToolResponse(
                        status=ToolCallStatus.FAILURE,
                        error=text or "MCP 도구가 실패 응답을 반환함",
                    )
                return ToolResponse(status=ToolCallStatus.SUCCESS, result=text)


def _extract_text(result) -> str | None:
    content = getattr(result, "content", None) or []
    texts = [c.text for c in content if getattr(c, "type", None) == "text"]
    return "\n".join(texts) if texts else None


def create_mcp_filesystem_connector() -> McpConnector:
    _SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    return McpConnector(
        name="mcp-filesystem",
        capabilities=["filesystem"],
        command="npx",
        # --offline: 매 호출마다 새 프로세스를 기동하는 이 Adapter의 특성상(세션을
        # 재사용하지 않음), npm 레지스트리에 매번 재확인하면 호출당 60초 이상
        # 걸린다(네트워크 프록시 왕복 비용). 패키지가 이미 로컬 캐시에 있다는
        # 전제로 --offline을 사용해 호출당 지연을 1~2초 수준으로 낮춘다 — 이는
        # MCP 실행 세부사항(구현 선택)이며 Architecture 결정이 아니다.
        args=["--offline", "-y", "@modelcontextprotocol/server-filesystem", str(_SANDBOX_DIR)],
    )
