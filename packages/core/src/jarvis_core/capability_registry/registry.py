"""저장소 비의존적인 순수 매칭 로직.

PoC 규모의 매칭 알고리즘: Intent 원문과 Capability의 keywords/description을
겹치는 단어 수 기준으로 점수화하는 매우 단순한 방식이다. 실제 의미 기반 매칭
(임베딩 등)은 기술 스택 논의 대상이며 여기서 다루지 않는다 — 이 함수의
인터페이스(텍스트 -> 순위 있는 Capability 목록)만 지금 확정한다.
"""
from .models import Capability


class CapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        self._capabilities[capability.capability_id] = capability

    def is_registered(self, capability_id: str) -> bool:
        return capability_id in self._capabilities

    def get(self, capability_id: str) -> Capability | None:
        return self._capabilities.get(capability_id)

    def get_by_owner(self, owner: str) -> list[Capability]:
        return [c for c in self._capabilities.values() if c.owner == owner]

    def match(self, text: str, only_active: bool = True) -> list[tuple[Capability, float]]:
        """text와 매칭되는 Capability를 점수 내림차순으로 반환."""
        tokens = set(text.replace(",", " ").split())
        scored: list[tuple[Capability, float]] = []
        for cap in self._capabilities.values():
            if only_active and cap.status != "active":
                continue
            haystack = set(cap.keywords) | set(cap.description.split()) | set(cap.domain.split("."))
            overlap = tokens & haystack
            if not overlap:
                continue
            score = len(overlap) / max(len(tokens), 1)
            scored.append((cap, score))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored
