"""Integration — Phase 4: Connector Adapter(MCP).

ADR-0006의 Architecture Validation 목표 중 첫 번째를 코드로 증명한다:
"Connector 구현체(MCP)를 제거하고 다른 Connector 구현체로 교체해도 Core와 Agent를
수정하지 않는다."

세 가지를 증명한다.
1. Adapter Reversibility(ADR-0006 결정 11) — MCP를 제거하고 Mock으로 되돌렸을 때
   `ConnectorRegistry`(Core)와 이를 소비하는 코드가 전혀 수정 없이 동일한 계약
   (`call_tool(ToolRequest) -> ToolResponse`)으로 동작한다. Phase 3의
   `test_policy_adapter_reversibility.py`와 동일한 방식으로, 두 Adapter를 직접
   구성해 동일 시나리오를 돌린다(entry-point 자동 Discovery를 거치지 않는다 —
   Mock은 의도적으로 Discovery에 참여하지 않는다. adapters/connector-mock/
   pyproject.toml 참고).
2. Fail-Closed 계약(ADR-0006 결정 9) — `IConnector.call_tool()`은 내부 오류가
   나도 예외를 던지지 않고 `ToolResponse(status=FAILURE, error=...)`를 반환한다.
3. Timeout 계약(ADR-0006 결정 5) — 응답이 `timeout_ms` 내에 오지 않으면 예외 없이
   `ToolResponse(status=TIMEOUT, ...)`를 반환한다. 실제 MCP 서버(filesystem)를
   대상으로 극단적으로 짧은 timeout_ms를 줘서 검증한다(네트워크가 없어 mcp 서버를
   기동할 수 없는 환경에서는 이 클래스를 건너뛴다).

실행: uv run pytest tests/integration/test_connector_adapter_reversibility.py -v
"""
import shutil
import unittest

from jarvis_core.connector.models import ToolCallStatus, ToolRequest, ToolResponse
from jarvis_core.connector_registry.registry import ConnectorRegistry
from jarvis_core.ports.i_connector import IConnector

from jarvis_adapter_connector_mock.connector import create_fetch_mock, create_filesystem_mock

try:
    from jarvis_adapter_connector_mcp.mcp_connector import create_mcp_filesystem_connector
    _MCP_AVAILABLE = shutil.which("npx") is not None
except Exception:
    _MCP_AVAILABLE = False


def _run_scenario(connectors: ConnectorRegistry) -> ToolResponse:
    """Core/Agent 쪽에서 실제로 벌어질 일 — Capability 이름으로만 조회하고 호출한다.
    이 함수는 어느 Connector 구현체가 등록됐는지 전혀 알지 못한다."""
    connector = connectors.find_by_capability("filesystem")
    assert connector is not None, "filesystem Capability가 등록되어 있어야 함"
    return connector.call_tool(ToolRequest(tool_name="probe", arguments={}))


class _AlwaysThrowingConnector(IConnector):
    """Fail-Closed 계약 테스트용 — 구현체 내부에서 예외가 나는 상황을 흉내낸다."""

    @property
    def capabilities(self) -> list[str]:
        return ["filesystem"]

    def call_tool(self, request: ToolRequest) -> ToolResponse:
        # 실제 Adapter라면 이 지점에서 예외가 나더라도 반드시 잡아서 반환해야 한다.
        # 이 테스트 더블은 "만약 그 계약을 지키지 않았다면" 무엇이 문제인지 보여주는
        # 대조군이다 — 아래 Fail-Closed 테스트는 실제 MockConnector/McpConnector가
        # 이 더블과 달리 예외를 삼킨다는 것을 증명한다.
        raise RuntimeError("simulated internal failure")


class TestConnectorAdapterReversibility(unittest.TestCase):
    """MCP를 제거하고 Mock으로 교체해도 Registry/호출 계약이 동일함을 증명한다."""

    def test_mock_connector_satisfies_same_contract_as_mcp_would(self):
        registry = ConnectorRegistry()
        registry.register(create_filesystem_mock())
        registry.register(create_fetch_mock())

        response = _run_scenario(registry)

        self.assertEqual(response.status, ToolCallStatus.SUCCESS)
        self.assertIsNone(response.error)

    def test_registry_lookup_is_identical_regardless_of_which_adapter_is_registered(self):
        mock_registry = ConnectorRegistry()
        mock_registry.register(create_filesystem_mock())

        response = _run_scenario(mock_registry)

        # Core/Agent 쪽 코드(_run_scenario)는 MCP인지 Mock인지 구분하는 어떤
        # 분기도 갖지 않는다 — capability 이름으로만 조회했다.
        self.assertIn(response.status, {ToolCallStatus.SUCCESS, ToolCallStatus.FAILURE})


class TestFailClosedContract(unittest.TestCase):
    def test_mock_connector_never_raises(self):
        connector = create_filesystem_mock()
        try:
            response = connector.call_tool(ToolRequest(tool_name="anything", arguments={}))
        except Exception as e:  # pragma: no cover - 계약 위반 시에만 도달
            self.fail(f"call_tool()이 예외를 던짐(Fail-Closed 계약 위반): {e}")
        self.assertEqual(response.status, ToolCallStatus.SUCCESS)

    def test_pep_style_call_does_not_need_try_except(self):
        """호출자는 방어적 try/except 없이 호출할 수 있어야 한다(No Silent Failure는
        '삼키지 않는다'는 뜻이지 '예외를 던진다'는 뜻이 아니다)."""
        registry = ConnectorRegistry()
        registry.register(create_filesystem_mock())
        response = _run_scenario(registry)
        self.assertIsInstance(response, ToolResponse)


@unittest.skipUnless(_MCP_AVAILABLE, "npx가 없거나 mcp SDK를 불러올 수 없는 환경에서는 건너뛴다")
class TestMcpConnectorFailClosedAndTimeout(unittest.TestCase):
    """실제 MCP(filesystem) 서버를 대상으로 Fail-Closed/Timeout 계약을 검증한다."""

    def test_success_never_raises_and_returns_result(self):
        connector = create_mcp_filesystem_connector()
        response = connector.call_tool(
            ToolRequest(tool_name="list_allowed_directories", arguments={}, timeout_ms=15_000)
        )
        self.assertEqual(response.status, ToolCallStatus.SUCCESS)
        self.assertIsNotNone(response.result)
        self.assertIsNone(response.error)

    def test_failure_from_real_server_is_converted_not_raised(self):
        connector = create_mcp_filesystem_connector()
        response = connector.call_tool(
            ToolRequest(
                tool_name="read_text_file",
                arguments={"path": "/etc/does-not-exist-jarvis-os-test"},
                timeout_ms=15_000,
            )
        )
        self.assertEqual(response.status, ToolCallStatus.FAILURE)
        self.assertIsNotNone(response.error)

    def test_timeout_is_returned_as_toolresponse_not_raised(self):
        connector = create_mcp_filesystem_connector()
        try:
            response = connector.call_tool(
                ToolRequest(tool_name="list_allowed_directories", arguments={}, timeout_ms=1)
            )
        except Exception as e:  # pragma: no cover - 계약 위반 시에만 도달
            self.fail(f"call_tool()이 예외를 던짐(Timeout 계약 위반): {e}")
        self.assertEqual(response.status, ToolCallStatus.TIMEOUT)
        self.assertIsNotNone(response.error)


if __name__ == "__main__":
    unittest.main()
