"""Stage 4 — Task Router. Classification -> ExecutionPlan."""
from .models import TaskClassification, ExecutionPlan
from jarvis_core.capability_registry.registry import CapabilityRegistry


def route(classification: TaskClassification, registry: CapabilityRegistry) -> ExecutionPlan:
    target_owners = []
    for capability_id, _score in classification.domain_candidates:
        cap = registry.get(capability_id)
        if cap and cap.owner not in target_owners:
            target_owners.append(cap.owner)
    return ExecutionPlan(
        target_hq_candidates=target_owners,
        execution_mode="single",
        estimated_cost_tier="standard",
    )
