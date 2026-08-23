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
- 신규 Capability/Agent 추가 — 기존 `requirements_agent_requirement_
  analysis()` 1개 재사용만으로 7개 관점을 모두 다룬다(`CAPABILITIES.md`
  Capability 2). `IMPLEMENTATION_RULES.md`("새 Capability/Agent 추가
  금지")와 ADR-0008 §4(신규는 실제 필요성 확인 시에만)를 모두 만족한다
  — 골격 추출은 Engine 미호출 순수 함수라 이 판단 대상이 아니다
- Multi-Engine 호출 — Specification 생성은 정확히 1회의 `call_engine()`
  호출로 끝난다(기존 `requirements_agent_requirement_analysis` 그대로)

## Kernel/Architecture 경계

Development HQ MVP Implementation 범위 — Kernel Architecture/Baseline
변경 없음, 새 Interface/Contract 미추가, `agents.py`/`engine.py` 무수정.
