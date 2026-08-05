# Execution Layer MVP-0001 Plan: Implementation Specification → Execution Request

## 목적

Jarvis OS Core 최초의 구현 Module로 Execution Layer를 시작한다. 이번
MVP의 목적은 실행이 아니라, `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`와
`docs/architecture/core/ADC-0001-core-baseline.md`가 이미 정리한 경계 —
Development HQ의 Implementation Specification이 끝나는 지점에서 Execution
Layer가 시작된다는 경계 — 위에서, 가장 작은 단위 하나를 실제로 관찰하는
것이다: Implementation Specification을 입력으로 받아 Execution Request를
생성하는 것.

이 문서는 계획 문서다. **이번 작업에서는 구현하지 않는다.**

## 전제

- Development HQ는 Phase 1을 완료한 것으로 간주하며, 이 MVP는 Development
  HQ의 어떤 코드·문서도 수정하지 않는다.
- `ADC-0001-core-baseline.md`에 따라 Core에서 Accept된 Module은 Governance와
  Execution Layer 둘뿐이다. Workflow, Memory, Event Bus는 Defer 상태이므로,
  이 MVP는 그것들을 전제하거나 사용하지 않는다.
- Governance는 이미 반복 검증되어 Accept된 절차(RFC → ADC → ADR)이며, 이
  문서 자체가 그 절차를 따르는 산출물이다. Governance Module 자체를
  구현하는 것은 이번 MVP의 대상이 아니다.

## 근거

- `docs/02_rfc/RFC-0005-development-hq-execution-boundary.md` §2, §3:
  Execution Layer는 Implementation Specification을 입력으로 받아 Code
  Generation부터 시작한다. §3이 정리한 8개 항목(Target File / Public
  Interface / Functions / Classes / Dependencies / Algorithm Outline /
  Edge Cases / Validation Notes)을 이 MVP의 Input Artifact 정의로 그대로
  채택한다 — 새 형식을 설계하지 않는다.
- `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md` §4.4:
  Execution Layer의 Core Module 책임은 "Specification 기반 AI 실행"이다.
- `docs/architecture/core/ADC-0001-core-baseline.md` Module 4: Execution
  Layer는 **Accept**되었고 Next Step은 ADR Required다. 이 MVP는 그 Accept
  이후 Execution Layer의 첫 구현 단계이며, Core Baseline 문서 자체를
  변경하지 않는다.
- `docs/01_mvp/MVP-0013-observation.md`: `_generate_code()`가 실제로
  생성하는 8개 항목의 정확한 형태(각 항목이 무엇을 담는지, 값이 비었을
  때 어떤 고정 문구가 나오는지, 반환 형식이 `str`이라는 사실)를 실측으로
  확인했다. 이 MVP는 그 관찰된 형태를 Input Artifact 스키마로 그대로
  사용한다.

## Scope

### Input Artifact

Implementation Specification — MVP-0013 Observation에서 실제로 관찰된
형태 그대로, 8개 항목으로 구성된 텍스트(`str`) 문서.

1. Target File
2. Public Interface
3. Functions
4. Classes
5. Dependencies
6. Algorithm Outline
7. Edge Cases
8. Validation Notes

MVP-0013 Observation은 이 문서가 관례적으로 "Reference Design"이라는
추가 절(Design 전체를 verbatim으로 품음)을 포함한다는 사실도 관찰했다.
이 MVP는 이 관례를 부정하거나 걷어내지 않는다 — Input Artifact를 있는
그대로 받아들인다. Reference Design 절을 해석·파싱·요약하는 것은 이
MVP의 책임이 아니다(Prompt Builder의 몫이며 Out of Scope).

Input Artifact의 형식은 MVP-0013이 실측한 대로 `str` 하나다. 이 MVP는
새로운 입력 형식(dict, JSON, 별도 객체)을 요구하지 않는다.

### Output Artifact

Execution Request — Implementation Specification의 8개 항목을 내용 손실·
재해석 없이 그대로 보존하면서, "이 Specification이 지금부터 실행 대상이
되었다"는 사실만 표시하는 최소 구조.

- 8개 항목은 순서와 내용을 그대로 유지한다. 요약하거나 재구성하지 않는다.
- Execution Request임을 식별할 수 있는 최소 표지(예: 문서 최상단에 명시적
  머리말) 하나만 추가한다.
- Prompt 텍스트, Model 이름/선택, 실행 순서, 재시도 정책, 세션 정보는
  포함하지 않는다 — 이 시점에는 아직 "무엇을 실행할 것인가"만 정의되고,
  "어떻게 실행할 것인가"는 정의되지 않는다.
- Output Artifact도 Input Artifact와 동일하게 텍스트 기반 구조로 정의한다.
  새로운 직렬화 형식(JSON Schema, 별도 클래스 계층 등)을 발명하지 않는다.

### Responsibility

Execution Layer MVP-0001이 책임지는 것은 다음 하나뿐이다.

> Implementation Specification(8개 항목)을 입력으로 받아, 내용을 변경하지
> 않고 Execution Request로 재포장한다.

다음은 이 MVP가 책임지지 않는다(Out of Scope 절에서 다시 나열한다).

- Execution Request로부터 실제 Prompt를 구성하는 것
- Execution Request를 어떤 Model에 보낼지 결정하는 것
- Execution Request를 실제로 실행하는 것
- Execution Request의 실행 결과를 파싱하는 것

### Success Criteria

- MVP-0013이 실제로 생성한 형태의 Implementation Specification을 입력으로
  받았을 때, 8개 항목이 모두 손실 없이 Execution Request에 포함되는지
  확인할 수 있어야 한다(항목별 verbatim 포함 여부를 직접 대조 가능해야
  한다).
- Execution Request는 원본 Implementation Specification과 구별 가능해야
  한다(최소 식별 표지 존재 여부로 판별 가능).
- 코드 경로 전체에서 AI/LLM/Model 호출이 없어야 한다 — RFC-0005 §2가
  Development HQ에 적용한 것과 동일한 검증 방식(`call_engine()`류 호출의
  부재 확인)을 이 MVP에도 그대로 적용한다.
- `development-hq/mvp/*` 이하 어떤 파일도 수정되지 않아야 한다.
- 기존 Development HQ 테스트(`development-hq/mvp/tests/*`)는 영향받지
  않아야 한다 — 이 MVP는 별도 디렉토리(`core/execution-layer/` 등, 구현
  시점에 결정)에서만 동작한다.

### Out of Scope

- Claude Code 호출
- GPT 호출
- Codex 호출
- Runtime
- Scheduler
- Retry
- Cost
- Parallel
- Session
- Result Parser
- Prompt Builder 구현
- Model Routing / Engine Adapter 구현

## Non-goals

- 이 MVP는 Execution Layer를 완성하지 않는다. Execution Request 생성까지만
  다룬다.
- 이 MVP는 Governance, Workflow, Memory, Event Bus Module을 다루지 않는다
  (ADC-0001에서 Workflow/Memory/Event Bus는 Defer됨).
- 이 MVP는 Core Baseline 문서(RFC-0001, ADC-0001)를 변경하지 않는다.
- 이 MVP는 Development HQ의 어떤 문서·코드도 수정하지 않는다.
- 이 MVP는 새 Architecture, 새 Layer, 새 Concept을 발명하지 않는다 —
  Execution Request는 RFC-0005 §3이 이미 "Execution Layer가 사용하는
  방식"으로 정리해 둔 8개 항목을 재포장한 것일 뿐이다.
- 이 MVP는 구현하지 않는다. 계획만 작성한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0005, Core RFC-0001, Core
  ADC-0001, MVP-0013 Observation에 실제로 기록된 내용만 인용했다.
- AI 호출(Claude Code/GPT/Codex)을 다뤘는가 — **아니오**. Out of Scope에
  명시했고 본문에서 다루지 않았다.
- Prompt Builder를 다뤘는가 — **아니오**. Responsibility·Out of Scope
  양쪽에서 명시적으로 제외했다.
- Runtime/Scheduler/Retry/Cost/Parallel/Session/Result Parser를 다뤘는가 —
  **아니오**. Out of Scope 목록에 그대로 나열했다.
- Development HQ를 수정했는가 — **아니오**. 읽기 근거로만 인용했다.
- 새 Architecture를 발명했는가 — **아니오**. Execution Request의 8개
  항목·형식은 모두 RFC-0005·MVP-0013에서 이미 관찰된 것을 그대로
  재사용했다.
- Core Baseline(ADC-0001)의 Decision과 모순되지 않는가 — **Pass**. Accept된
  Module(Governance, Execution Layer)만 전제했고, Defer된 Module
  (Workflow, Memory, Event Bus)은 사용하지 않았다.
- 구현했는가 — **아니오**. 계획 문서 하나만 작성했다.
