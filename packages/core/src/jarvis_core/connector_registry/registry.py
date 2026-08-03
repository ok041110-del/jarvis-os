"""Connector Registry — Connector Capability 조회를 위한 순수 Domain 로직.

ADR-0006 결정 12: `jarvis_core.capability_registry.registry.CapabilityRegistry`
(HQ Capability 매칭)와는 **의도적으로 완전히 분리된 별도 클래스**다. 두 Registry가
같은 이름/모듈을 공유하지 않는 것 자체가 "HQ Capability와 Connector Capability는
서로 다른 Domain"이라는 원칙을 코드 구조로 드러낸다.

이 Registry는 발견(discover)된 Connector 인스턴스를 담아 두고, Agent가 필요로 하는
Capability 이름으로 실행할 Connector를 찾아주는 것까지만 책임진다. Connector를
어디서 찾아오는지(entry point 등)는 `IConnectorDiscovery` 구현체의 몫이며, 이
Registry는 그 결과를 조립만 한다.
"""
from __future__ import annotations

import sys

from jarvis_core.ports.i_connector import IConnector


class ConnectorRegistry:
    def __init__(self) -> None:
        self._by_capability: dict[str, IConnector] = {}

    def register(self, connector: IConnector) -> None:
        for capability in connector.capabilities:
            existing = self._by_capability.get(capability)
            if existing is not None and existing is not connector:
                print(
                    f"[ConnectorRegistry] capability '{capability}'가 이미 "
                    f"{existing!r}로 등록되어 있음 — {connector!r}로 덮어씀",
                    file=sys.stderr,
                )
            self._by_capability[capability] = connector

    def is_registered(self, capability: str) -> bool:
        return capability in self._by_capability

    def find_by_capability(self, capability: str) -> IConnector | None:
        return self._by_capability.get(capability)

    def known_capabilities(self) -> list[str]:
        return sorted(self._by_capability.keys())
