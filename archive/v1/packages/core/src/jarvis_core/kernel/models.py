"""Kernel 전 단계에서 공유하는 데이터 모델.
Request_Processing_Kernel_v1.md의 각 Stage Input/Output을 그대로 dataclass로 옮김.
"""
from dataclasses import dataclass, field


@dataclass
class Intent:
    raw_text: str
    primary_intent: str
    entities: list[str]
    confidence: float  # 0.0~1.0


@dataclass
class TaskClassification:
    domain_candidates: list[tuple[str, float]]  # (capability_id, match_score) 내림차순
    requires_multi_hq: bool
    urgency: str          # "normal" | "high"
    complexity_tier: str  # "simple" | "standard" | "complex"


@dataclass
class ExecutionPlan:
    target_hq_candidates: list[str]  # capability.owner 순서 (1순위부터)
    execution_mode: str              # "single" | "parallel" | "sequential"
    estimated_cost_tier: str


@dataclass
class TaskDispatch:
    selected_hq: str
    capability_id: str
    intent: Intent
    wake_up_required: bool = False


@dataclass
class KernelOutcome:
    """Kernel(Stage1~5)의 최종 산출물. 성공이든 실패든 반드시 이 형태로 귀결된다.
    No Silent Failure 원칙: ok=False인 경우 reason이 비어있으면 안 된다.
    """
    ok: bool
    dispatch: TaskDispatch | None = None
    reason: str = ""
    audit_trail: list[str] = field(default_factory=list)
