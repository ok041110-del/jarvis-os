# Stage 02: Responsibility

## 책임진다

- Stage 01 Output(Context Bundle)에서 Problem Definition/Constraints/
  Risk/Implementation Scope 후보를 결정적으로(Engine 호출 없이) 추출
- 위 골격을 Issue에 결합해 Requirement Analysis Capability를 호출,
  Task Decomposition/Acceptance Criteria를 포함한 하나의 Specification
  텍스트로 구조화
- Specification을 Stage 03(Architecture & Design)이 바로 소비할 수 있는
  고정된 스키마(`SPECIFICATION.md`)로 반환

## 책임지지 않는다

- Repository/파일 탐색, AST 분석(→ Stage 01. 이 Stage는 Stage 01의
  Output을 그대로 Input으로 받을 뿐, Context를 다시 수집하지 않는다)
- Architecture/Design 산출(→ Stage 03) — Specification은 "무엇을 만들지"
  까지만 다루고 "어떻게 구현할지"는 다루지 않는다
- 코드 생성/수정(→ Stage 04), 코드 리뷰/테스트 실행(→ Stage 05)
- 신규 Capability/Agent 추가 — `requirements_agent_requirement_analysis()`
  1개 Capability 재사용만으로 7개 관점을 모두 다룬다(`CAPABILITIES.md`
  Capability 2 참고). `IMPLEMENTATION_RULES.md`의 "구현 중 새 Capability/
  Agent 추가 금지" 원칙과 ADR-0008 §4(신규 Capability는 실제 필요성이
  확인된 경우에만)를 모두 만족하는 범위로 판단했다 — 골격 추출은 새
  Engine 호출이 아니라 순수 함수이므로 이 판단에 포함되지 않는다
- Multi-Engine 호출 — Specification 생성은 정확히 1회의 `call_engine()`
  호출로 끝난다(`requirements_agent_requirement_analysis` 내부, 기존
  구현 그대로)

## Kernel/Architecture 경계

Stage 02는 Development HQ MVP Implementation 범위이며, Jarvis OS Kernel
Architecture나 Development HQ Baseline을 변경하지 않는다. 새 Interface/
Contract를 추가하지 않았고, `agents.py`/`engine.py`는 수정하지 않았다.
