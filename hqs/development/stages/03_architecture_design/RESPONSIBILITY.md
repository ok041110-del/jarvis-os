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
- AST 폐쇄 시작점 자동 식별 — `workflow_ast_context.identify_target()`
  이 이미 구현하며, 그 호출은 Stage 04(Build 직전)의 책임이다. Stage 03
  은 Design **텍스트**까지만 만든다
- 코드 생성/수정(→ Stage 04), 코드 리뷰/테스트 실행(→ Stage 05)
- 신규 Capability/Agent 추가 — 기존 `design_agent_design()` 1개
  재사용만으로 9개 관점을 모두 다룬다(`CAPABILITIES.md` Capability 2).
  `IMPLEMENTATION_RULES.md`와 ADR-0008 §4를 모두 만족한다 — 골격 추출은
  Engine 미호출 순수 함수라 이 판단 대상이 아니다
- Multi-Engine 호출 — Design 생성은 정확히 1회의 `call_engine()` 호출로
  끝난다(기존 `design_agent_design` 그대로)

## Kernel/Architecture 경계

Development HQ MVP Implementation 범위 — Kernel Architecture/Baseline
변경 없음, 새 Interface/Contract 미추가, `agents/`/`engine.py`/
`workflow_ast_context.py` 무수정.
