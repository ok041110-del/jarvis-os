# Stage 02: Capabilities

**RFC-0034/ADC-0037/ADR-0022로 이전 Capability 2(Requirement &
Specification 생성)는 Stage 01(`prd_synthesis.py`)로 이동했다.** Stage
02에 남은 Capability는 1개뿐이다 — 신규 Capability나 신규 Engine 호출을
추가하지 않는다(`RESPONSIBILITY.md` 참고).

## 1. PRD/Specification Passthrough (Engine 미호출)

| 항목 | 내용 |
|---|---|
| Input | Stage 01 Output(`stage_01_context["prd"]`, 이미 `{skeleton, specification}` 형태) |
| Analysis | `stage_02.run_stage_02()` — `stage_01_context["prd"]`를 재해석·재생성 없이 그대로 반환한다(dict 복사만). Task Decomposition/Acceptance Criteria는 이미 Stage 01의 PRD Synthesis(`prd_synthesis.py`)에서 지시문으로 포함되어 생성됐다 |
| Output | `dict`(`skeleton`, `specification` 2개 키 — `SpecificationResult`와 동일, Stage 01의 `prd`와 동일 값) |
| Validation | 순수 함수 — `test_stage_02.py`에서 passthrough 동작(입력 변형 없음, 원본 불변)을 직접 단위 테스트. PRD Synthesis 자체의 검증은 `test_stage01_prd_synthesis.py` 참조 |

## 폐기됨: Requirement & Specification 생성 (Stage 01로 이동)

과거 이 Stage가 `agents.requirements.requirements_agent_requirement_
analysis(issue)`를 직접 호출해 Specification을 생성했다 — 이제 그
호출은 Stage 01의 `prd_synthesis.py`에서 이루어진다(같은 함수, 호출
위치만 이동). Stage 02는 더 이상 Engine을 호출하지 않는다.
