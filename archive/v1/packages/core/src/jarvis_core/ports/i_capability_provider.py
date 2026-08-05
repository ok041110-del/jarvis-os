"""i_capability_provider.py — Port(Interface) 정의.
Core는 이 Interface만 알고, 실제 구현(YAML/DB/Remote Registry/Marketplace/...)은 모른다.
adapters/ 아래 패키지가 이 Interface를 implements 한다.

ADR-0004 결정 2: 이 Port의 책임은 Capability를 발견(discover)하고 파싱(parse)하여
Capability 객체로 만드는 것까지다. Registry 등록, HQ 생성, Lifecycle 전이, Kernel
로직에는 관여하지 않는다 — 그 조립은 jarvis_core.application.hq_provisioner.HQProvisioner
(Application Service)와 Composition Root의 책임이다.

이 Port는 jarvis_core.ports.i_capability_store(영속 저장/조회를 위한 별도 개념,
아직 미구현)와 다른 개념이다 — 혼동하지 않는다.
"""
from abc import ABC, abstractmethod

from jarvis_core.capability_registry.models import Capability


class ICapabilityProvider(ABC):
    """부팅 시점에 Capability 선언을 어디서 가져올지를 추상화하는 도메인 인터페이스."""

    @abstractmethod
    def load(self) -> list[Capability]:
        """발견 가능한 모든 Capability를 구조적으로 유효한 것만 반환한다.
        구조적으로 무효한 항목(스키마 누락, 소유 식별자 불일치 등)은 조용히
        포함시키지 않는다 — 구현체는 그 사유를 로그로 남겨야 한다(No Silent Failure).
        """
        ...
