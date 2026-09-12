"""Stage 01 Multi-Agent Reasoning — Intent/Goal/Requirement/Ambiguity Agent +
Reasoning Aggregator(RFC-0033/ADC-0036/ADR-0021). 각 Agent는 독립적인
reasoning 책임만 가지며 repository의 파일/함수를 직접 선택하지 않는다.
Multi-Engine Architecture(`ADR-0024`) 이후 Reasoning 목적 호출은 3번째
Engine인 OpenRouter Free Model Selection(`ADR-0027`,
`mvp/openrouter_engine.py::call_engine_via_openrouter`)을 사용한다 — 이
모듈은 Engine routing/provider 선택/policy를 소유하지 않는다(어떤 free
모델이 실제로 쓰이는지 이 모듈은 모른다)."""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mvp.openrouter_engine import call_engine_via_openrouter as call_engine  # noqa: E402

AGENT_TASK_IDS = ("intent", "goal", "requirement", "ambiguity")

INTENT_REQUIRED_KEYS = ("action", "target", "domain", "explicit_intent", "confidence")
GOAL_REQUIRED_KEYS = ("desired_outcome", "success_direction", "underlying_goal", "confidence")
REQUIREMENT_REQUIRED_KEYS = (
    "functional_requirements", "non_functional_requirements", "constraints",
    "scope_candidates", "confidence",
)
AMBIGUITY_REQUIRED_KEYS = (
    "ambiguous_points", "missing_information", "conflicting_interpretations",
    "unresolved_questions", "confidence",
)


class AgentOutputError(ValueError):
    """Agent 응답이 유효한 JSON Structured Output이 아닐 때 발생한다 —
    ParallelRunner가 INVALID_OUTPUT으로 분류하는 신호(재시도 대상 아님)."""


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_structured_output(raw: str) -> dict:
    """Engine 응답에서 JSON 객체 하나를 추출한다(markdown fence로 감싸는
    경우까지 관대하게 처리) — 파싱/키 검증 실패는 `AgentOutputError`."""
    match = _JSON_OBJECT_RE.search(raw or "")
    if not match:
        raise AgentOutputError(f"no JSON object found in agent output: {(raw or '')[:200]}")
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise AgentOutputError(f"agent output is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise AgentOutputError("agent output JSON is not an object")
    return parsed


def _run_agent(instruction: str, issue: dict, required_keys: tuple) -> dict:
    prompt = (
        f"{instruction}\n\n"
        "Respond with a single JSON object only (no prose, no markdown fences) "
        f"containing exactly these keys: {list(required_keys)}. "
        "\"confidence\" must be a number between 0 and 1.\n\n"
        f"Title: {issue['title']}\nDescription: {issue['description']}"
    )
    raw = call_engine(prompt)
    parsed = parse_structured_output(raw)
    missing = [key for key in required_keys if key not in parsed]
    if missing:
        raise AgentOutputError(f"agent output missing required keys: {missing}")
    return parsed


def intent_agent(issue: dict) -> dict:
    """사용자 요청의 action/target/domain/explicit intent를 구조화한다 —
    repository 파일/함수를 직접 선택하지 않는다."""
    instruction = (
        "You are the Intent Agent in a software development request analysis "
        "pipeline. Extract the user's action, target, domain, and explicit "
        "intent from the request below. Do not reference specific repository "
        "files or functions — describe intent in general terms only."
    )
    return _run_agent(instruction, issue, INTENT_REQUIRED_KEYS)


def goal_agent(issue: dict) -> dict:
    """desired outcome/success direction/underlying goal을 추론한다."""
    instruction = (
        "You are the Goal Agent. Infer the desired outcome, success direction, "
        "and underlying goal behind the request below. Do not reference "
        "specific repository files or functions."
    )
    return _run_agent(instruction, issue, GOAL_REQUIRED_KEYS)


def requirement_agent(issue: dict) -> dict:
    """functional/non-functional requirement, constraint, scope candidate를
    구조화한다(scope candidate는 일반 주제/키워드 문자열이며 repository 경로가
    아니다)."""
    instruction = (
        "You are the Requirement Agent. Extract functional requirements, "
        "non-functional requirements, constraints, and scope candidates (as "
        "general topic/keyword strings, NOT repository file paths) from the "
        "request below."
    )
    return _run_agent(instruction, issue, REQUIREMENT_REQUIRED_KEYS)


def ambiguity_agent(issue: dict) -> dict:
    """ambiguous point/missing information/conflicting interpretation/미해결
    질문을 식별한다."""
    instruction = (
        "You are the Ambiguity/Gap Agent. Identify ambiguous points, missing "
        "information, conflicting interpretations, and unresolved questions "
        "in the request below."
    )
    return _run_agent(instruction, issue, AMBIGUITY_REQUIRED_KEYS)


AGENT_FUNCTIONS = {
    "intent": intent_agent,
    "goal": goal_agent,
    "requirement": requirement_agent,
    "ambiguity": ambiguity_agent,
}


# --- Reasoning Aggregator ----------------------------------------------------


def _dedup(items: list) -> list:
    seen = set()
    result = []
    for item in items or []:
        key = item.strip().lower() if isinstance(item, str) else item
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _detect_conflicts(intent: dict, requirement: dict) -> list:
    """intent.action과 requirement.constraints 사이의 명백한 부정 모순만
    표면화한다 — 임의 해석으로 승자를 정하지 않는다."""
    conflicts = []
    if not intent or not requirement:
        return conflicts
    action = (intent.get("action") or "").strip().lower()
    if not action:
        return conflicts
    for constraint in requirement.get("constraints") or []:
        if isinstance(constraint, str) and f"no {action}" in constraint.lower():
            conflicts.append(f"intent.action={action!r} conflicts with constraint: {constraint!r}")
    return conflicts


def aggregate_reasoning(batch_result) -> dict:
    """4개 Agent Task 결과(`ParallelBatchResult`)를 StructuredUnderstanding
    으로 통합한다. schema validation은 각 Agent가 이미 수행했으므로(SUCCESS만
    통과), 여기서는 normalization/dedup/conflict detection/confidence
    aggregation/search specification 생성만 담당한다. Agent 간 충돌이 있으면
    임의로 하나를 선택하지 않고 `CONFLICT`로 표시한다."""
    from mvp.parallel_runner import TaskStatus  # 지연 import — 순환 의존 회피

    by_id = {result.task_id: result for result in batch_result.results}

    outputs = {}
    for task_id in AGENT_TASK_IDS:
        result = by_id.get(task_id)
        outputs[task_id] = result.output if result and result.status == TaskStatus.SUCCESS else None

    intent, goal, requirement, ambiguity = (outputs[t] for t in AGENT_TASK_IDS)

    missing_agents = [task_id for task_id in AGENT_TASK_IDS if outputs[task_id] is None]

    if requirement:
        requirement = dict(requirement)
        for key in ("functional_requirements", "non_functional_requirements", "constraints", "scope_candidates"):
            requirement[key] = _dedup(requirement.get(key))
    if ambiguity:
        ambiguity = dict(ambiguity)
        for key in ("ambiguous_points", "missing_information", "conflicting_interpretations", "unresolved_questions"):
            ambiguity[key] = _dedup(ambiguity.get(key))

    conflicts = _detect_conflicts(intent, requirement)

    confidences = [
        result.get("confidence")
        for result in (intent, goal, requirement, ambiguity)
        if result and isinstance(result.get("confidence"), (int, float))
    ]
    overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    if conflicts:
        status = "CONFLICT"
    elif len(missing_agents) >= 2:
        status = "INSUFFICIENT"
    elif missing_agents:
        status = "PARTIAL"
    else:
        status = "OK"

    keywords = set()
    for source, keys in (
        (intent, ("action", "target", "domain", "explicit_intent")),
        (goal, ("desired_outcome", "success_direction", "underlying_goal")),
    ):
        if not source:
            continue
        for key in keys:
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                keywords.add(value.strip())

    scope_candidates = list(requirement.get("scope_candidates") or []) if requirement else []

    search_specification = {
        "keywords": sorted(keywords),
        "scope_candidates": scope_candidates,
    }

    return {
        "intent": intent,
        "goal": goal,
        "requirement": requirement,
        "ambiguity": ambiguity,
        "status": status,
        "conflicts": conflicts,
        "missing_agents": missing_agents,
        "overall_confidence": overall_confidence,
        "search_specification": search_specification,
    }
