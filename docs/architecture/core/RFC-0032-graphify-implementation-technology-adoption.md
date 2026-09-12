# RFC-0032: Graphify를 승인된 비강제 Implementation Technology 후보로 확정할 것인가 (향후 Graph 기반 Memory/Knowledge/Relationship 요구 대비)

**Status**: Resolved — `docs/architecture/core/ADC-0035-graphify-implementation-technology-adoption.md`로
종결됨(Accept, Conditional·Non-Mandatory, Architecture 무연동). 후속
`docs/architecture/core/ADR-0020-graphify-implementation-technology-adoption.md`
참고.
**Author**: Claude Code (사용자 요청 "Graphify 도입 재검토"에 대한
Governance 절차 적용)
**대상**: 특정 Kernel Module의 존재·경계가 **아니다.** 이 RFC는
`ADC-02`/`ADC-09`처럼 아직 결정되지 않은 Kernel Boundary도,
Memory Kernel Module(Defer, `ADC-0001-core-baseline.md` Module 3)의
존재 여부도 재론하지 않는다. 이 RFC가 다루는 유일한 대상은 "**Graphify라는
기술을, Architecture가 아직 요구하지도 않은 미래 필요에 대비해 승인된
후보 목록에 미리 올려둘 것인가**"라는 순수 Implementation Technology
질문이다 — `RFC-0031`(LangGraph)이 이미 Accept된 §16.6 Workflow
Adapter 책임의 구현 전략을 다뤘던 것과 달리, 이번에는 대응하는
Kernel 책임 자체가 아직 Accept되지 않았다는 점이 핵심 차이다(§2
Boundary Question에서 이 차이를 정확히 반영한다).
**Evidence 범위**: `.claude/docs/integrations/graphify.md`(2026-08-30
검증, 이 저장소 대상 실제 CLI 실행: `update`/`query`/`path`/`explain`
전부 PASS, 1524 files / 14231 nodes / 17988 edges), `ADR-0011`
(Implementation Freedom), `ADC-0001-core-baseline.md` Module 3
(Memory, Defer — 인용만, 재조사 아님). 이 RFC는 새 실험을 하지
않는다 — 기존 CLI 검증을 재실행하지 않는다(사용자 지시 2번).

> 본 RFC는 Memory Kernel Module을 Accept하거나 재개설하지 않는다.
> `ADC-0001` Module 3의 Defer 판정, `BASELINE.md` §16.7의 Defer 목록,
> §10 Out of Scope, §11 Kernel 정의는 이 RFC로 전혀 변경되지 않는다.
> Graphify의 즉시 Production 적용이나 실제 코드/Claude Code 정식
> 연결(`graphify claude install`, CLAUDE.md 자동 수정 동반)도 이
> RFC의 승인 대상이 아니다.

## 0. 이 RFC가 열린 이유

`.claude/docs/integrations/graphify.md`는 이미 Graphify의 CLI
기능(코드/문서를 tree-sitter 기반 knowledge graph로 변환, `query`/
`path`/`explain` 질의)을 이 저장소 전체(1524개 파일)에 대해 실제로
검증했다(PASS) — 역할 중복도 없음을 확인했다. 그러나 이 검증은
**실행환경 채택 evidence**일 뿐 Governance Decision Record가 아니며
(그 문서 자신의 성격 선언), Graphify를 저장소의 공식 Implementation
Technology 후보로 기록하지 않았다.

사용자는 이제 두 가지를 동시에 요구한다: (1) 현재 실제 Jarvis
사용처가 부족하다는 사실을 그대로 인정하고, (2) 그럼에도 향후
Graph 기반 Memory/Knowledge/Relationship 요구가 생겼을 때를 대비해
공식 후보로 미리 Adoption한다. 이는 `ADR-0011`(Implementation
Freedom)이 이미 확립한 원칙 — "Evidence의 부재 자체는 구현 기술
선택을 금지하는 사전 허가 조건이 아니다" — 을 정확히 반대 방향에서도
적용하는 것이다: Evidence 부족이 **금지**의 근거가 아니듯,
**Adoption**의 필수 전제도 아니다. 다만 Adoption이 Architecture를
바꾸는 형태가 되어서는 안 되므로(사용자 지시 7번), 그 경계를 정확히
긋는 것이 이 RFC의 목적이다.

## 1. Observation — 기존 Evidence와 현재 사용처 상태

| 항목 | 상태 |
|---|---|
| CLI 기능 실사용 검증 | **완료(PASS)** — `graphify update .`(1524 files, 14231 nodes, 17988 edges), `query`/`path`/`explain` 3개 기능 전부 실제 그래프에 대해 정상 동작 확인(`.claude/docs/integrations/graphify.md`) |
| 역할 중복 | 없음 — Claude-Mem(세션 요약)/Task Observer(skill 관찰)/OmniRoute(Provider 라우팅) 어느 것도 코드/문서 구조를 그래프로 만들어 질의하는 기능이 없음(기존 검증 인용) |
| Claude Code 정식 연결(`graphify claude install`) | **미실행** — CLAUDE.md 자동 수정을 동반해 의도적으로 보류(기존 검증 인용, 재실행하지 않음) |
| **현재 실제 Jarvis 사용처** | **없음** — Development HQ/Investment HQ 어떤 코드도 Graphify를 참조하지 않는다. 이 사실을 그대로 인정한다(사용자 지시 3번) |
| 대응하는 Kernel Module | 없음 — Memory(Context/Knowledge 저장·전달 후보)는 `ADC-0001` Module 3에서 **Defer**됐고, 이 RFC는 그 상태를 재론하지 않는다 |

## 2. Boundary Question

### Q-1. Graphify를 승인된 비강제 Implementation Technology 후보로 확정할 것인가

- **Question**: 현재 실제 사용처가 없다는 사실을 그대로 인정한
  채로, "향후 Graph 기반 Memory/Knowledge/Relationship 요구가 실제로
  발생하면 재검토 없이 곧바로 후보로 쓸 수 있도록" Graphify를 지금
  공식 목록에 등재할 것인가?
- **Evidence**: §1 표 전체. 특히 CLI 기능 자체는 이미 이 저장소를
  대상으로 실측 검증되어 "기술적으로 동작하는가"라는 질문에는 이미
  답이 나와 있다 — 남은 것은 "지금 쓰임새가 없는데도 미리 승인해
  두는 것이 정당한가"이다.
- **Constraint**: `ADR-0011`(Implementation Freedom) — Evidence
  부재가 사전 금지 조건이 아니라는 원칙은, 뒤집어 보면 "쓰임새가
  아직 없다"는 사실도 **Adoption 자체를 막는 근거가 아니라는 뜻**
  이지 "Architecture가 그 필요를 인정했다"는 뜻은 아니다. 이 Adoption은
  Memory Kernel Module의 존재를 조금이라도 앞당기거나 암시해서는
  안 된다 — `ADC-0001` Module 3(Defer)의 판단 근거("실제 반복 관찰이
  아직 필요하지 않았다는 방향으로 일관되게 나타남")는 이 RFC로
  전혀 흔들리지 않는다.
- **Options**:
  - (a) 승인된 비강제 후보로 확정 — Architecture Module Accept와
    완전히 분리된, 순수 Technology 층위의 사전 등재.
  - (b) 지금은 Adoption하지 않고 `.claude/docs/integrations/
    graphify.md`의 기존 "실행환경 채택 evidence" 상태로만 유지.
  - (c) Memory Kernel Module Defer를 재개설해 Graphify를 그 구현
    전략으로 묶는다 — **기각 후보**: 사용자 지시 7번(Architecture/
    Kernel Boundary 변경 금지)에 정면으로 위배된다.
- **ADC에서 결정할 사항**: (a)와 (b) 중 채택안, (a) 채택 시 "비강제"
  범위와 Memory Module Defer 상태와의 명시적 분리 서술.

## 3. Architecture Impact

- **없음(NONE)** — 이 RFC는 어떤 Kernel Module도 Accept/Defer
  상태를 바꾸지 않는다. `ADC-02`/`ADC-09`를 포함해 어떤 Open
  Decision도 재개설하지 않는다. §6 Concept Model, §10 Out of Scope,
  §11 Kernel 정의, §16.7 Defer 목록 — 전부 무변경 대상이다.

## 4. Contract Impact

- 없음 — Public Contract를 변경하지 않는다.

## 5. 이 RFC가 정의하지 않는 것 (경계)

- Memory(또는 별도 Knowledge/Relationship) Kernel Module의 Accept
  여부 — `ADC-0001` Module 3의 Defer는 이 RFC의 범위 밖이며 그대로
  유지된다.
- Graphify의 Claude Code 정식 연결(`graphify claude install`)이나
  실제 코드/CLAUDE.md 배선 — 이 RFC는 승인 목록 등재 여부만 다룬다.
- Production 적용 시점·방식.

## Decision

**Accept (Conditional·Non-Mandatory, Architecture 무연동)** —
`docs/architecture/core/ADC-0035-graphify-implementation-technology-adoption.md`
판정을 그대로 따른다. Graphify는 향후 Graph 기반 Memory/Knowledge/
Relationship 요구에 대한 승인된 비강제 구현 후보로 확정되며, Memory
Kernel Module(`ADC-0001` Module 3, Defer)과는 명시적으로 분리된다.
즉시 Production 적용·Claude Code 정식 연결은 이 Decision으로 승인되지
않는다.
