"""Policy Engine v1의 도메인 모델. Tier 정의를 코드로 고정."""
from dataclasses import dataclass
from enum import IntEnum


class PolicyTier(IntEnum):
    TIER1_ABSOLUTE = 1   # Permission, Security — 거부 시 즉시 중단
    TIER2_RESOURCE = 2   # Budget, Wake-up, Isolation — 거부 시 축소안 우선
    TIER3_OPTIMIZE = 3   # Priority, Retry — 논블로킹


@dataclass
class PolicyRequest:
    subject: str            # 누가 (session id 등)
    action: str              # 무엇을 하려는지 (예: "invoke_capability")
    resource: str             # 무엇에 대해 (capability_id 등)
    required_permission: str  # Capability.required_permission


@dataclass
class PolicyDecision:
    allow: bool
    tier: PolicyTier
    reason: str
