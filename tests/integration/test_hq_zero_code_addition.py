"""Integration — Phase 2 Architecture Validation (사용자 지정 최종 검증 기준).

"새 HQ를 코드 수정 없이 추가하여 자동 인식 및 자동 Routing이 가능함"을 증명한다.

이 테스트는 실제로 새로운 HQ 패키지(hqs/legal-hq)를 저장소에 물리적으로 추가하고
`uv sync`로 workspace에 설치한 뒤, 다음 파일들 중 어느 것도 수정하지 않은 상태로:
  - packages/core (Kernel 포함)
  - packages/core/src/jarvis_core/capability_registry
  - apps/poc-runner/src/jarvis_poc_runner/main.py
  - apps/poc-runner/pyproject.toml (legal-hq를 의존성으로 선언하지 않는다!)
다음을 증명한다.
  1. Development HQ / Investment HQ / Legal HQ 3개가 동시에 자동 Discovery된다
     (ADR-0004 결정 7, 사용자 지정 "복수 HQ 자동 Discovery" DoD 항목).
  2. 각 Capability가 올바른 HQ로 Routing된다(Kernel Stage 2~5 실사용).
  3. Legal HQ 패키지를 제거하면(uv sync 재실행) Core/Kernel 수정 없이 나머지
     2개 HQ가 정상적으로 계속 동작한다(HQ 제거 DoD 항목).

주의: 이 테스트는 실제로 hqs/legal-hq/ 디렉터리를 생성했다가 제거하고, 그 때마다
`uv sync`를 실행한다 — 네트워크가 없는 환경에서도 로컬 workspace 멤버 추가/제거는
동작해야 하므로 원칙적으로 네트워크 접근이 필요하지 않다(이미 resolve된 의존성).

Discovery/Routing 검증은 반드시 `uv run python -c "..."`으로 새 서브프로세스를
띄워 수행한다 — editable install은 site-packages에 `.pth` 파일을 추가하는 방식이라,
이미 떠 있는(현재 pytest를 실행 중인) 인터프리터는 `uv sync`가 새로 설치한 패키지를
재시작 없이는 보지 못한다(Python의 site 모듈이 .pth를 인터프리터 시작 시점에만
읽기 때문). 이는 실제 운용에서도 동일하다 — 새 HQ 추가 후에는 Composition Root
프로세스를 재시작하는 것이 당연히 전제된다.
"""
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEGAL_HQ_DIR = REPO_ROOT / "hqs" / "legal-hq"
POC_RUNNER_PYPROJECT = REPO_ROOT / "apps" / "poc-runner" / "pyproject.toml"

_LEGAL_HQ_PYPROJECT = """[project]
name = "jarvis-hq-legal"
version = "0.1.0"
description = "legal HQ — Phase 2 Zero-Code-Addition 검증용 임시 픽스처(테스트 종료 후 제거됨)."
requires-python = ">=3.12"
dependencies = [
    "jarvis-core",
]

[project.entry-points."jarvis.hq_capability_source"]
legal-hq = "jarvis_hq_legal"

[tool.uv.sources]
jarvis-core = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

_LEGAL_HQ_CAPABILITIES_YAML = """capability_id: legal-hq.contract-review.v1
domain: legal.general
description: 계약서 검토 및 법률 자문 관련 작업을 처리한다.
input_profile: 계약/법률/규정 관련 자연어 요청
output_profile: 계약서 검토 의견, 법률 리스크 요약
owner: legal-hq
required_permission: standard
keywords: [계약, 법률, 검토, 자문, 규정]
"""


def _run_uv_sync() -> None:
    result = subprocess.run(
        ["uv", "sync"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, f"uv sync 실패:\n{result.stdout}\n{result.stderr}"


@unittest.skipUnless(shutil.which("uv"), "uv가 설치되어 있지 않은 환경에서는 이 검증을 건너뛴다")
class TestHQZeroCodeAddition(unittest.TestCase):
    """사용자 지정 Phase 2 Architecture Validation을 실증하는 테스트."""

    @classmethod
    def setUpClass(cls) -> None:
        # 사전 조건: legal-hq가 Composition Root의 명시적 의존성으로 선언되어
        # 있지 않음을 먼저 확인한다 — 이것이 "무수정" 증명의 핵심이다.
        pyproject_text = POC_RUNNER_PYPROJECT.read_text(encoding="utf-8")
        assert "jarvis-hq-legal" not in pyproject_text, (
            "이 테스트는 apps/poc-runner/pyproject.toml이 legal-hq를 전혀 모르는 "
            "상태에서 자동 Discovery가 되는지를 증명해야 한다."
        )

        (LEGAL_HQ_DIR / "src" / "jarvis_hq_legal").mkdir(parents=True, exist_ok=True)
        (LEGAL_HQ_DIR / "pyproject.toml").write_text(_LEGAL_HQ_PYPROJECT, encoding="utf-8")
        (LEGAL_HQ_DIR / "src" / "jarvis_hq_legal" / "__init__.py").write_text("", encoding="utf-8")
        (LEGAL_HQ_DIR / "src" / "jarvis_hq_legal" / "capabilities.yaml").write_text(
            _LEGAL_HQ_CAPABILITIES_YAML, encoding="utf-8"
        )
        _run_uv_sync()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(LEGAL_HQ_DIR, ignore_errors=True)
        _run_uv_sync()

    @staticmethod
    def _run_in_fresh_subprocess(script: str) -> subprocess.CompletedProcess:
        """새 인터프리터에서 실행한다 — editable install의 .pth는 프로세스 시작
        시점에만 site 모듈이 읽으므로, 이미 떠 있는 프로세스에서는 uv sync로 새로
        설치된 패키지가 보이지 않는다(실제 운용에서도 재시작이 전제되는 것과 동일)."""
        return subprocess.run(
            ["uv", "run", "python", "-c", script],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
        )

    def test_three_hqs_are_discovered_simultaneously(self):
        script = (
            "from jarvis_adapter_capability_provider_yaml.provider import YamlCapabilityProvider\n"
            "provider = YamlCapabilityProvider()\n"
            "capabilities = provider.load()\n"
            "owners = sorted(c.owner for c in capabilities)\n"
            "assert provider.errors == [], provider.errors\n"
            "assert owners == ['development-hq', 'investment-hq', 'legal-hq'], owners\n"
            "print('OK:three-hqs-discovered')\n"
        )
        result = self._run_in_fresh_subprocess(script)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK:three-hqs-discovered", result.stdout)

    def test_legal_hq_is_provisioned_and_becomes_routable(self):
        script = (
            "from jarvis_core.application.hq_provisioner import HQProvisioner\n"
            "from jarvis_core.capability_registry.registry import CapabilityRegistry\n"
            "from jarvis_adapter_capability_provider_yaml.provider import YamlCapabilityProvider\n"
            "from jarvis_adapter_lifecycle_statemachine.hq_state_machine import HQStateMachineRuntime\n"
            "from jarvis_core.kernel import intent_recognition, task_classification, task_router, hq_selection\n"
            "from jarvis_adapter_policy_inmemory.engine import InMemoryPolicyEngine\n"
            "\n"
            "registry = CapabilityRegistry()\n"
            "provisioner = HQProvisioner(YamlCapabilityProvider(), registry, HQStateMachineRuntime)\n"
            "provisioned = provisioner.provision_all()\n"
            "assert len(provisioned) == 3, provisioned\n"
            "for owner, r in provisioned.items():\n"
            "    assert r.ok, (owner, r.reason)\n"
            "\n"
            "hqs = {owner: r.hq for owner, r in provisioned.items()}\n"
            "policy_engine = InMemoryPolicyEngine(session_permissions={'user-A': 'standard'})\n"
            "intent = intent_recognition.recognize('계약서 검토 좀 해줘')\n"
            "classification = task_classification.classify(intent, registry)\n"
            "plan = task_router.route(classification, registry)\n"
            "outcome = hq_selection.select(plan, intent, registry, hqs, policy_engine, 'user-A')\n"
            "assert outcome.ok, outcome.reason\n"
            "assert outcome.dispatch.selected_hq == 'legal-hq', outcome.dispatch.selected_hq\n"
            "print('OK:legal-hq-routed')\n"
        )
        result = self._run_in_fresh_subprocess(script)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK:legal-hq-routed", result.stdout)

    def test_dev_and_investment_capability_ids_unaffected_by_legal_hq(self):
        script = (
            "from jarvis_core.capability_registry.registry import CapabilityRegistry\n"
            "from jarvis_core.application.hq_provisioner import HQProvisioner\n"
            "from jarvis_adapter_capability_provider_yaml.provider import YamlCapabilityProvider\n"
            "from jarvis_adapter_lifecycle_statemachine.hq_state_machine import HQStateMachineRuntime\n"
            "\n"
            "registry = CapabilityRegistry()\n"
            "provisioner = HQProvisioner(YamlCapabilityProvider(), registry, HQStateMachineRuntime)\n"
            "provisioner.provision_all()\n"
            "assert registry.get('dev-hq.code-task.v1') is not None\n"
            "assert registry.get('invest-hq.market-task.v1') is not None\n"
            "assert registry.get('legal-hq.contract-review.v1') is not None\n"
            "print('OK:all-three-registered')\n"
        )
        result = self._run_in_fresh_subprocess(script)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK:all-three-registered", result.stdout)


class TestHQRemovalRestoresPriorBehavior(unittest.TestCase):
    """legal-hq 제거 후(uv sync 재실행) Core/Kernel 무수정으로 나머지 2개 HQ가
    정상 동작하는지 확인한다(사용자 지정 'HQ 제거' DoD 항목).
    이 클래스는 legal-hq를 별도로 추가/제거하여 위 클래스와 독립적으로 검증한다.
    """

    @classmethod
    def setUpClass(cls) -> None:
        (LEGAL_HQ_DIR / "src" / "jarvis_hq_legal").mkdir(parents=True, exist_ok=True)
        (LEGAL_HQ_DIR / "pyproject.toml").write_text(_LEGAL_HQ_PYPROJECT, encoding="utf-8")
        (LEGAL_HQ_DIR / "src" / "jarvis_hq_legal" / "__init__.py").write_text("", encoding="utf-8")
        (LEGAL_HQ_DIR / "src" / "jarvis_hq_legal" / "capabilities.yaml").write_text(
            _LEGAL_HQ_CAPABILITIES_YAML, encoding="utf-8"
        )
        _run_uv_sync()
        # 이제 legal-hq를 다시 제거한다 — "추가했다가 제거" 시나리오
        shutil.rmtree(LEGAL_HQ_DIR, ignore_errors=True)
        _run_uv_sync()

    def test_dev_and_investment_still_work_after_legal_hq_removed(self):
        script = (
            "from jarvis_adapter_capability_provider_yaml.provider import YamlCapabilityProvider\n"
            "provider = YamlCapabilityProvider()\n"
            "capabilities = provider.load()\n"
            "owners = sorted(c.owner for c in capabilities)\n"
            "assert provider.errors == [], provider.errors\n"
            "assert owners == ['development-hq', 'investment-hq'], owners\n"
            "print('OK:legal-hq-removed-others-intact')\n"
        )
        result = TestHQZeroCodeAddition._run_in_fresh_subprocess(script)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK:legal-hq-removed-others-intact", result.stdout)


if __name__ == "__main__":
    unittest.main()
