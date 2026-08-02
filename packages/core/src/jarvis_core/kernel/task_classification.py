"""Stage 3 — Task Classification. Capability Registry 매칭 결과로 도메인 후보를 산출."""
from .models import Intent, TaskClassification
from jarvis_core.capability_registry.registry import CapabilityRegistry


def classify(intent: Intent, registry: CapabilityRegistry) -> TaskClassification:
    matches = registry.match(intent.raw_text)
    domain_candidates = [(cap.capability_id, score) for cap, score in matches]
    return TaskClassification(
        domain_candidates=domain_candidates,
        requires_multi_hq=False,  # PoC 범위에서는 항상 단일 HQ (Direct Channel 등은 v1.1)
        urgency="normal",
        complexity_tier="simple",
    )


def is_unclassified(classification: TaskClassification) -> bool:
    return len(classification.domain_candidates) == 0
