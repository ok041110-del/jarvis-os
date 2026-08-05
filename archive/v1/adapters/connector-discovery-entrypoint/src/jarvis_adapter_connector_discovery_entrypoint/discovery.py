"""IConnectorDiscovery(jarvis_core)의 Python Entry Point 기반 구현.

ADR-0006 결정 12: Connector Discovery 방식은 Architecture가 아니라 PoC의 구현
선택이다(ADR-0004 결정 7이 HQ Discovery에 대해 확립한 것과 동일 원칙). 여기서는
Python Entry Point(group="jarvis.connector")를 사용한다.

각 Connector 어댑터 패키지는 자신의 pyproject.toml에 다음과 같이 선언한다:

    [project.entry-points."jarvis.connector"]
    <connector-id> = "<모듈경로>:<factory 함수명>"

entry point의 value는 인자 없이 호출하면 `IConnector` 인스턴스를 반환하는 factory
callable이어야 한다. 새 Connector 패키지가 uv workspace(`adapters/connector-*`)에
추가되고 `apps/poc-runner`의 의존성에 더해지기만 하면, `uv sync`가 이를 공유
가상환경에 설치하고 이 어댑터가 entry point를 통해 자동으로 발견한다 — Core,
Agent, `ConnectorRegistry` 어느 것도 새 Connector의 이름을 알 필요가 없다.

factory 호출이 실패하면(의존 라이브러리 미설치, 외부 서버 기동 실패 등) 그
Connector는 조용히 제외하지 않고 사유를 표준 에러로 남긴 뒤 발견 목록에서
제외한다(No Silent Failure) — 단, 이 정보가 Core에 전달되는 공식 계약은 아니다
(IConnectorDiscovery Port는 discover() 반환값만 약속한다).
"""
from __future__ import annotations

import sys
from importlib.metadata import entry_points

from jarvis_core.ports.i_connector import IConnector
from jarvis_core.ports.i_connector_discovery import IConnectorDiscovery

_ENTRY_POINT_GROUP = "jarvis.connector"


class EntryPointConnectorDiscovery(IConnectorDiscovery):
    """entry point로 선언된 각 Connector 패키지의 factory를 호출해 발견한다."""

    def __init__(self) -> None:
        self.errors: list[tuple[str, str]] = []

    def discover(self) -> list[IConnector]:
        self.errors = []
        connectors: list[IConnector] = []
        for ep in entry_points(group=_ENTRY_POINT_GROUP):
            connector = self._load_one(ep.name, ep)
            if connector is not None:
                connectors.append(connector)
        return connectors

    def _load_one(self, connector_id: str, ep) -> IConnector | None:
        try:
            factory = ep.load()
        except Exception as e:
            self._reject(connector_id, f"entry point 로드 실패: {e}")
            return None

        try:
            connector = factory()
        except Exception as e:
            self._reject(connector_id, f"factory 호출 실패: {e}")
            return None

        if not isinstance(connector, IConnector):
            self._reject(
                connector_id,
                f"factory가 IConnector 인스턴스를 반환하지 않음: {type(connector)!r}",
            )
            return None

        return connector

    def _reject(self, connector_id: str, reason: str) -> None:
        self.errors.append((connector_id, reason))
        print(f"[EntryPointConnectorDiscovery] '{connector_id}' 발견 거부: {reason}", file=sys.stderr)
