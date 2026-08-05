# Observation: Stage Capability Quality Improvement (Before/After)

**대상**: Development HQ DevKit Issue 0001("Development HQ DevKit 최소
기능")을 동일하게 재실행해, Planning/Design/Validation Capability
개선 전후를 비교한다.

**변경 파일**: `development-hq/mvp/engine.py`만 수정했다. Pipeline
(`runner.py`, `workflow_project_intelligence.py`), Task Dispatcher
(하드코딩된 순차 호출 구조), Project Intelligence
(`project_intelligence.py`)는 수정하지 않았다. 새 Capability는
추가하지 않았다 — `agents.py`의 `AGENT_CAPABILITY_MAP`/
`HELLO_SDLC_CAPABILITY_MAP`도 그대로다.

> 이 문서는 사실만 기록한다. 판단, 설계, Architecture 제안, Decision을
> 하지 않는다.

## Before/After 산출물 위치

- Before: `issues/0001-devkit-minimal-feature/before/{planning,design,validation}.md`
  (`engine.py` 수정 전 실행 결과, 원본 그대로 보존)
- After: `issues/0001-devkit-minimal-feature/{planning,design,validation}.md`
  (`engine.py` 수정 후 동일 Issue 재실행 결과)

## 1. Planning Capability

**Before**: 1문장 템플릿 — `요구사항: '{title}' 기능이 필요하다. 상세:
{description}`.

**After**: 6개 절로 구성된 Requirement Specification — Goal /
Description / In Scope / Out of Scope / Acceptance Criteria (Draft) /
Reference Context. 문장 분리(마침표 기준)와 부정 표현 마커(`않는다`,
`제외`, `범위 밖`, `아니다`) 매칭만으로 Issue의 두 문장을 실제로
In Scope 1건("...Markdown 파일로 저장한다")과 Out of Scope 1건
("Implementation(Code Generation)은 이번 기능에 포함하지 않는다")으로
정확히 분리했다. Project Intelligence가 덧붙인 `[Relevant Context]`
블록은 별도 "Reference Context" 절로 분리되어, In/Out of Scope 분류
대상에서 제외되었다(직접 확인).

**일반화 확인**: DevKit Issue 0001 외에 MVP-0005에서 쓰인 두 Issue
("Task Dispatcher", "reverse string" — 둘 다 마침표 없는 단문)로도
재실행했다. 두 Issue 모두 문장이 1개뿐이라 In Scope 1건, Out of
Scope 0건("감지된 Out of Scope 문장 없음")으로 처리되었다 — 예외 없이
동작했지만, 부정 마커가 없는 단문 Issue에서는 Out of Scope 절이 항상
비게 된다는 사실도 함께 관찰되었다.

## 2. Design Capability

**Before**: `설계: 함수 \`{slug}(*args, **kwargs)\`를 추가한다. 요구사항:
{requirement 전체}` — 1문장 + Requirement 전체 이어붙이기.

**After**: 5개 절로 구성된 Architecture 초안 — Component /
Responsibility / Constraints / Open Questions / Reference Requirement.
Requirement의 "In Scope" 절 문장은 "책임:"으로, "Out of Scope" 절
문장은 "제약:"으로 그대로 재서술되어 각각 Responsibility/Constraints
절에 나타났다(직접 확인: Responsibility에 "책임: ...Markdown 파일로
저장한다", Constraints에 "제약: Implementation(Code Generation)은 이번
기능에 포함하지 않는다"). Requirement 전체는 "Reference Requirement"
절에 그대로 보존되어, 기존에 관찰된 Artifact Flow 성질
(`requirement in design`)이 여전히 유지되는지 확인했다 — **유지됨**
(직접 문자열 포함 검사로 확인).

`_extract_slug()`가 참조하는 `` `{slug}(*args, **kwargs)` `` 패턴은
Component 절에 그대로 남겨, MVP-0004(Implementation Stage,
`workflow_hello_sdlc.py`)와의 호환성도 깨지지 않았다(별도 확인 —
이번 작업 범위는 아니지만 회귀를 만들지 않기 위해 패턴을 유지했다).

## 3. Validation Capability (코드가 아닌 Design 입력에 대한 평가)

**Before**(`OBS-0004`에 기록된 사실과 동일): `code_review`가 Design
텍스트를 Python 코드처럼 검사해 8건 findings(1건 "docstring 없음" +
7건 "줄이 100자를 초과합니다" — 전부 `[Relevant Context]` 목록 줄에서
발생)를 반환했다. `test_execution`은 `"def "` 줄을 찾지 못해 범용
fallback "스크립트 최상위 로직에 대한 실행 결과 검증" 1건만 반환했다.

**After**: `_looks_like_code()`(정규식 `^\s*(def |class |import |from )`)
로 입력이 Python 코드가 아님을 판별해, `code_review`는 `_review_design()`
으로, `test_execution`은 `_suggest_design_checks()`로 분기했다.

- `code_review` 결과: findings 8건 → **1건**("Architecture 초안에 필수
  섹션(Component/Responsibility/Constraints)이 모두 포함되어 있습니다")
  으로 줄었다. `[Relevant Context]` 블록의 줄 길이로 인한 오탐(7건)과
  Design 문서에 무의미한 "docstring 없음" 오탐(1건)이 모두
  사라졌다(직접 확인).
- `test_execution` 결과: 범용 fallback 1건 → **Design 구조 기반 검증
  항목 2건**("Responsibility에 나열된 각 항목이 Requirement의 In
  Scope와 실제로 일치하는지 확인", "Constraints에 나열된 각 항목이
  Implementation 단계에서 실제로 지켜지는지 확인")으로 바뀌었다.

**일반화 확인**: 기존 MVP-0001 회귀 테스트(`test_mvp_0001.py`, 실제
Python 코드 `SAMPLE_CODE` 입력)는 `_looks_like_code()`가 `True`를
반환해 기존 코드 전용 로직(`_review_code`의 원본 분기)을 그대로
타는 것을 확인했다 — 3건 테스트 모두 통과, 회귀 없음.

## Artifact Flow / Information Flow (개선 후 재확인)

- `requirement in design` == True — 유지됨(개선 후에도 Requirement
  전체가 Design 산출물에 그대로 포함).
- `[Relevant Context]`는 이제 Planning 산출물의 "Reference Context"
  절 안에서만 나타나고, Design의 "Reference Requirement" 절을 통해
  구조는 유지한 채로 하위 Stage까지 전달된다. Validation은 여전히
  Design 텍스트 전체(Context 포함)를 입력받지만, 개선된 `_review_design`/
  `_suggest_design_checks`는 특정 절(`## Component` 등) 존재 여부만
  검사하므로 Context 블록의 줄 길이가 더 이상 findings에 영향을 주지
  않았다(직접 확인).

## Success Criteria 재확인

개선 후에도 세 Issue(DevKit Issue 0001, Task Dispatcher, reverse
string) 모두 예외 없이 Planning → Design → Validation까지 끝까지
실행되었다.

## 범위 밖 (이번 개선에서 하지 않은 것)

- Pipeline(`runner.py`, `workflow_project_intelligence.py`,
  `workflow_artifact_flow.py`, `workflow_0008.py`), Task Dispatcher
  구조, Project Intelligence(`project_intelligence.py`) 수정.
- 새 Capability 추가.
- Implementation(Code Generation) Capability 품질 개선 — 이번 우선순위
  목록에 포함되지 않았다.
- "감지된 Out of Scope 문장 없음"처럼 부정 마커가 없는 단문 Issue에서
  Out of Scope가 항상 비게 되는 현상을 고치는 것 — 사실만 기록하고
  고치지 않았다.
- Architecture 판단(이 개선이 충분한지, 다음에 무엇을 더 개선해야
  하는지).
