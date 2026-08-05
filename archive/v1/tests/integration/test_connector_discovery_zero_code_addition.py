"""Integration — Phase 4 Architecture Validation (사용자 지정 추가 검증 기준).

"새 Connector를 코드 수정 없이 추가하여 자동 Discovery 및 선택이 가능하다."를 증명한다.

Phase 2의 `test_hq_zero_code_addition.py`(legal-hq를 실제로 추가/제거)와 동일한
방법론을 Connector에 적용한다: 새 Connector 패키지(`adapters/connector-http-stub`)를
저장소에 물리적으로 추가하고 `uv sync`로 workspace에 설치한 뒤, 다음 파일들 중
어느 것도 수정하지 않은 상태로:
  - packages/core (connector_registry, ports/i_connector_discovery 포함)
  - apps/poc-runner/src/jarvis_poc_runner/main.py
  - apps/poc-runner/pyproject.toml (http-stub을 의존성으로 선언하지 않는다!)
다음을 증명한다.
  1. 기존 filesystem Connector(MCP)와 신규 http Connector가 동시에 자동
     Discovery된다(ADR-0006 결정 12).
  2. http-stub 패키지를 제거하면(uv sync 재실행) Core 무수정으로 filesystem
     Connector는 계속 정상 Discovery된다(Connector 제거 DoD 항목).

주의: HQ 테스트와 동일하게 Discovery 검증은 `uv run python -c "..."`으로 새
서브프로세스에서 수행한다(editable install의 .pth는 인터프리터 시작 시점에만
읽히므로, 이미 떠 있는 프로세스는 새로 설치된 패키지를 보지 못한다).
"""
import shutil
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HTTP_STUB_DIR = REPO_ROOT / "adapters" / "connector-http-stub"
POC_RUNNER_PYPROJECT = REPO_ROOT / "apps" / "poc-runner" / "pyproject.toml"

_HTTP_STUB_PYPROJECT = """[project]
name = "jarvis-adapter-connector-http-stub"
version = "0.1.0"
description = "Phase 4 Discovery Architecture Validation 검증용 임시 픽스처(테스트 종료 후 제거됨)."
requires-python = ">=3.12"
dependencies = [
    "jarvis-core",
]

[project.entry-points."jarvis.connector"]
http-stub = "jarvis_adapter_connector_http_stub.connector:create_http_stub_connector"

[tool.uv.sources]
jarvis-core = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

_HTTP_STUB_CONNECTOR_PY = '''"""Discovery Architecture Validation 전용 최소 Connector. 실제 HTTP 호출을 하지 않는다."""
from jarvis_core.connector.models import ToolCallStatus, ToolRequest, ToolResponse
from jarvis_core.ports.i_connector import IConnector


class HttpStubConnector(IConnector):
    @property
    def capabilities(self) -> list[str]:
        return ["http"]

    def call_tool(self, request: ToolRequest) -> ToolResponse:
        return ToolResponse(status=ToolCallStatus.SUCCESS, result="[stub] 고정 응답")


def create_http_stub_connector() -> HttpStubConnector:
    return HttpStubConnector()
'''


def _run_uv_sync() -> None:
    result = subprocess.run(
        ["uv", "sync"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, f"uv sync 실패:\n{result.stdout}\n{result.stderr}"


def _run_in_fresh_subprocess(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "python", "-c", script],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
    )


@unittest.skipUnless(shutil.which("uv"), "uv가 설치되어 있지 않은 환경에서는 이 검증을 건너뛴다")
class TestConnectorZeroCodeAddition(unittest.TestCase):
    """새 Connector 패키지 추가만으로 자동 Discovery되는지 증명한다."""

    @classmethod
    def setUpClass(cls) -> None:
        pyproject_text = POC_RUNNER_PYPROJECT.read_text(encoding="utf-8")
        assert "jarvis-adapter-connector-http-stub" not in pyproject_text, (
            "이 테스트는 apps/poc-runner/pyproject.toml이 http-stub을 전혀 모르는 "
            "상태에서 자동 Discovery가 되는지를 증명해야 한다."
        )

        (HTTP_STUB_DIR / "src" / "jarvis_adapter_connector_http_stub").mkdir(parents=True, exist_ok=True)
        (HTTP_STUB_DIR / "pyproject.toml").write_text(_HTTP_STUB_PYPROJECT, encoding="utf-8")
        (HTTP_STUB_DIR / "src" / "jarvis_adapter_connector_http_stub" / "__init__.py").write_text(
            "", encoding="utf-8"
        )
        (HTTP_STUB_DIR / "src" / "jarvis_adapter_connector_http_stub" / "connector.py").write_text(
            _HTTP_STUB_CONNECTOR_PY, encoding="utf-8"
        )
        _run_uv_sync()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(HTTP_STUB_DIR, ignore_errors=True)
        _run_uv_sync()

    def test_filesystem_and_http_are_discovered_simultaneously(self):
        script = (
            "from jarvis_adapter_connector_discovery_entrypoint.discovery import EntryPointConnectorDiscovery\n"
            "d = EntryPointConnectorDiscovery()\n"
            "connectors = d.discover()\n"
            "assert d.errors == [], d.errors\n"
            "found = sorted(cap for c in connectors for cap in c.capabilities)\n"
            "assert found == ['filesystem', 'http'], found\n"
            "print('OK:filesystem-and-http-discovered')\n"
        )
        result = _run_in_fresh_subprocess(script)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK:filesystem-and-http-discovered", result.stdout)

    def test_http_capability_is_selectable_via_registry_without_naming_the_adapter(self):
        script = (
            "from jarvis_core.connector_registry.registry import ConnectorRegistry\n"
            "from jarvis_core.connector.models import ToolRequest, ToolCallStatus\n"
            "from jarvis_adapter_connector_discovery_entrypoint.discovery import EntryPointConnectorDiscovery\n"
            "\n"
            "registry = ConnectorRegistry()\n"
            "for c in EntryPointConnectorDiscovery().discover():\n"
            "    registry.register(c)\n"
            "\n"
            "connector = registry.find_by_capability('http')\n"
            "assert connector is not None\n"
            "response = connector.call_tool(ToolRequest(tool_name='ping', arguments={}))\n"
            "assert response.status == ToolCallStatus.SUCCESS, response\n"
            "print('OK:http-capability-selected-and-called')\n"
        )
        result = _run_in_fresh_subprocess(script)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK:http-capability-selected-and-called", result.stdout)


class TestConnectorRemovalRestoresPriorBehavior(unittest.TestCase):
    """http-stub 제거 후(uv sync 재실행) Core 무수정으로 filesystem Connector가
    정상 동작하는지 확인한다(사용자 지정 'Connector 제거' DoD 항목).
    """

    @classmethod
    def setUpClass(cls) -> None:
        (HTTP_STUB_DIR / "src" / "jarvis_adapter_connector_http_stub").mkdir(parents=True, exist_ok=True)
        (HTTP_STUB_DIR / "pyproject.toml").write_text(_HTTP_STUB_PYPROJECT, encoding="utf-8")
        (HTTP_STUB_DIR / "src" / "jarvis_adapter_connector_http_stub" / "__init__.py").write_text(
            "", encoding="utf-8"
        )
        (HTTP_STUB_DIR / "src" / "jarvis_adapter_connector_http_stub" / "connector.py").write_text(
            _HTTP_STUB_CONNECTOR_PY, encoding="utf-8"
        )
        _run_uv_sync()
        # 이제 http-stub을 다시 제거한다 — "추가했다가 제거" 시나리오
        shutil.rmtree(HTTP_STUB_DIR, ignore_errors=True)
        _run_uv_sync()

    def test_filesystem_still_discovered_after_http_stub_removed(self):
        script = (
            "from jarvis_adapter_connector_discovery_entrypoint.discovery import EntryPointConnectorDiscovery\n"
            "d = EntryPointConnectorDiscovery()\n"
            "connectors = d.discover()\n"
            "assert d.errors == [], d.errors\n"
            "found = sorted(cap for c in connectors for cap in c.capabilities)\n"
            "assert found == ['filesystem'], found\n"
            "print('OK:http-stub-removed-filesystem-intact')\n"
        )
        result = _run_in_fresh_subprocess(script)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK:http-stub-removed-filesystem-intact", result.stdout)


if __name__ == "__main__":
    unittest.main()
