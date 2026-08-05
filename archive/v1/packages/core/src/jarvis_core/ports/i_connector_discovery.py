"""IConnectorDiscovery — Port(Interface) 정의.

ADR-0006 결정 12: Connector도 Jarvis OS의 Plugin이며, 이름이 아니라 Capability로
발견(discover)된다. Core는 이 Interface만 알고, 실제 발견 메커니즘(Python Entry
Point/Config 파일/원격 Registry 등)은 모른다 — adapters/ 아래 패키지가 구현한다.

이 Port는 `jarvis_core.ports.i_capability_provider.ICapabilityProvider`(HQ Capability
발견)와 **의도적으로 분리된 별개의 Domain**이다. HQ Capability는 Kernel이 요청을
라우팅할 대상(HQ)을 찾기 위한 것이고, Connector Capability는 Agent가 실행할 도구를
찾기 위한 것이다 — 두 개념을 같은 코드 경로로 섞지 않는다.

이 Port의 책임은 발견(discover)까지다. 발견된 Connector들을 등록/조회하는 것은
`jarvis_core.connector_registry.registry.ConnectorRegistry`의 몫이다.
"""
from abc import ABC, abstractmethod

from jarvis_core.ports.i_connector import IConnector


class IConnectorDiscovery(ABC):
    """부팅 시점에 사용 가능한 Connector 구현체를 어디서 찾을지 추상화하는 인터페이스."""

    @abstractmethod
    def discover(self) -> list[IConnector]:
        """발견 가능한 모든 Connector 인스턴스를 반환한다.

        구조적으로 무효한 항목(로드 실패 등)은 조용히 포함시키지 않는다 — 구현체는
        그 사유를 로그로 남겨야 한다(No Silent Failure).
        """
        ...
