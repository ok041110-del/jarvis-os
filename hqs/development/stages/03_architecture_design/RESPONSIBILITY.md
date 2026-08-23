# Stage 03: Responsibility

## 책임진다

- Stage 01 Output(특히 `candidate_index`)과 Stage 02 Output(`skeleton`의
  `scope_candidates`/`constraints`/`risks`, `specification`)에서 Design
  골격을 결정적으로(Engine 호출 없이) 추출
- 위 골격을 Stage 02 Specification에 결합해 Design Capability를 호출,
  Architecture Definition/Component Identification/Responsibility
  Allocation/Interface·Contract Identification/Data Flow/Implementation
  Strategy를 포함한 하나의 Design 텍스트로 구조화
- Design을 Stage 04(Implementation)가 바로 소비할 수 있는 고정된
  스키마(`DESIGN.md`)로 반환

## 책임지지 않는다

- Repository/파일 탐색, AST 분석, Specification 생성(→ Stage 01/02.
  이 Stage는 두 Stage의 Output을 그대로 Input으로 받을 뿐, 다시
  수집·생성하지 않는다)
- Design으로부터 AST Dependency Closure의 시작점(target module/function)을
  자동 식별하는 것 — `workflow_ast_context.identify_target()`이 이미
  이 식별을 수행하며, 그 호출은 Stage 04(Implementation, Build 직전
  단계)의 책임이다. Stage 03은 Design **텍스트**까지만 만들고, 그
  텍스트를 소비해 실제 코드 생성 대상을 찾는 것은 다루지 않는다
- 코드 생성/수정(→ Stage 04), 코드 리뷰/테스트 실행(→ Stage 05)
- 신규 Capability/Agent 추가 — `design_agent_design()` 1개 Capability
  재사용만으로 9개 관점을 모두 다룬다(`CAPABILITIES.md` Capability 2
  참고). `IMPLEMENTATION_RULES.md`의 "구현 중 새 Capability/Agent 추가
  금지" 원칙과 ADR-0008 §4(신규 Capability는 실제 필요성이 확인된
  경우에만)를 모두 만족하는 범위로 판단했다 — 골격 추출은 새 Engine
  호출이 아니라 순수 함수이므로 이 판단에 포함되지 않는다
- Multi-Engine 호출 — Design 생성은 정확히 1회의 `call_engine()` 호출로
  끝난다(`design_agent_design` 내부, 기존 구현 그대로)

## Kernel/Architecture 경계

Stage 03은 Development HQ MVP Implementation 범위이며, Jarvis OS Kernel
Architecture나 Development HQ Baseline을 변경하지 않는다. 새 Interface/
Contract를 추가하지 않았고, `agents.py`/`engine.py`/`workflow_ast_
context.py`는 수정하지 않았다.
