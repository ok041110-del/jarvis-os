"""ICapabilityProvider(jarvis_core)의 YAML + Python Entry Point 기반 구현.

ADR-0004 결정 2: 이 어댑터의 책임은 Capability를 발견(discover)하고 파싱(parse)
하는 것까지다. Registry 등록/HQ 생성/Lifecycle 전이는 하지 않는다(그건
jarvis_core.application.hq_provisioner.HQProvisioner의 몫이다).

ADR-0004 결정 7: HQ Discovery 방식은 Architecture가 아니라 PoC의 구현 선택이다.
여기서는 Python Entry Point(group="jarvis.hq_capability_source")를 사용한다.
각 HQ 패키지는 자신의 pyproject.toml에 다음과 같이 선언한다:

    [project.entry-points."jarvis.hq_capability_source"]
    <hq-id> = "<모듈명>"

entry point의 name이 곧 그 HQ의 정식 식별자(owner)이며, value는 capabilities.yaml을
담고 있는 패키지 모듈명이다. 새 HQ 패키지가 uv workspace(`hqs/*`)에 추가되기만
하면 `uv sync`가 이를 공유 가상환경에 설치하고, 이 어댑터가 entry point를 통해
자동으로 발견한다 — apps/poc-runner, Kernel, Core, Registry 어느 것도 새 HQ를
알 필요가 없다.

구조적으로 무효한 항목(YAML 파싱 실패, 필수 필드 누락, owner가 entry point
name과 불일치)은 반환 목록에서 제외하되, 반드시 self.errors에 사유를 남기고
표준 에러 출력으로도 알린다(No Silent Failure) — 단, 이 정보가 Core에 전달되는
공식 계약은 아니다(ICapabilityProvider Port는 load() 반환값만 약속한다).
"""
from __future__ import annotations

import sys
from importlib import resources
from importlib.metadata import entry_points

import yaml

from jarvis_core.capability_registry.models import Capability
from jarvis_core.ports.i_capability_provider import ICapabilityProvider

_ENTRY_POINT_GROUP = "jarvis.hq_capability_source"
_CAPABILITY_FILENAME = "capabilities.yaml"
_MANDATORY_FIELDS = {
    "capability_id", "domain", "description", "input_profile", "output_profile", "owner",
}


class YamlCapabilityProvider(ICapabilityProvider):
    """entry point로 발견한 각 HQ 패키지의 capabilities.yaml을 읽어 Capability로 파싱한다."""

    def __init__(self) -> None:
        self.errors: list[tuple[str, str]] = []

    def load(self) -> list[Capability]:
        self.errors = []
        capabilities: list[Capability] = []
        for ep in entry_points(group=_ENTRY_POINT_GROUP):
            capability = self._load_one(ep.name, ep.value)
            if capability is not None:
                capabilities.append(capability)
        return capabilities

    def _load_one(self, hq_id: str, module_name: str) -> Capability | None:
        try:
            text = resources.files(module_name).joinpath(_CAPABILITY_FILENAME).read_text(encoding="utf-8")
            data = yaml.safe_load(text)
        except Exception as e:
            self._reject(hq_id, f"capabilities.yaml 파싱 실패: {e}")
            return None

        if not isinstance(data, dict):
            self._reject(hq_id, "capabilities.yaml이 매핑(dict) 형식이 아님")
            return None

        missing = _MANDATORY_FIELDS - data.keys()
        if missing:
            self._reject(hq_id, f"필수 필드 누락: {sorted(missing)}")
            return None

        try:
            capability = Capability(**data)
        except TypeError as e:
            self._reject(hq_id, f"스키마 불일치: {e}")
            return None

        if capability.owner != hq_id:
            self._reject(
                hq_id,
                f"owner 불일치: capabilities.yaml의 owner={capability.owner!r}가 "
                f"entry point 식별자={hq_id!r}와 다름",
            )
            return None

        return capability

    def _reject(self, hq_id: str, reason: str) -> None:
        self.errors.append((hq_id, reason))
        print(f"[YamlCapabilityProvider] '{hq_id}' 로드 거부: {reason}", file=sys.stderr)
