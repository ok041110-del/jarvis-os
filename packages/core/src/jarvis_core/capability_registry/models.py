"""Capability 스키마. Capability_Registry_v1.md 참고."""
from dataclasses import dataclass, field


@dataclass
class Capability:
    capability_id: str
    domain: str
    description: str
    input_profile: str
    output_profile: str
    owner: str                    # 소유 HQ/Division id
    cost_tier: str = "standard"
    latency_tier: str = "standard"
    required_permission: str = "standard"
    version: int = 1
    status: str = "active"        # "active" | "deprecated"
    keywords: list[str] = field(default_factory=list)  # 매칭용 최소 힌트 (PoC 한정 단순 구현)
