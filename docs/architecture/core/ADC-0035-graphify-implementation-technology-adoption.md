# ADC-0035: Graphify 승인된 비강제 Implementation Technology 확정 판단 (RFC-0032 후속)

## 목적

RFC-0032가 제기한 Q-1 Boundary Question을 판단한다. 근거는 RFC-0032
원문과 그것이 인용하는 `.claude/docs/integrations/graphify.md`,
`ADR-0011`(Implementation Freedom), `ADC-0001-core-baseline.md`
Module 3(Memory, Defer)로 한정한다. 이 문서 자체는 새로운 조사를
하지 않는다.

이 ADC는 `ADC-0034`(LangGraph)와 같은 절차적 성격이나, 결정적으로
다른 전제 위에 있다 — `ADC-0034`는 이미 Accept된 Kernel 책임
(Workflow Adapter, §16.6)의 구현 전략을 판단했지만, 이 ADC는
**대응하는 Kernel 책임 자체가 아직 존재하지 않는(Memory, Defer)**
상태에서 순수 Technology 사전 등재만 판단한다.

## 판단 대상에서 제외

- Memory(또는 Knowledge/Relationship) Kernel Module의 Accept 여부 —
  `ADC-0001` Module 3의 Defer 판정을 재론하지 않는다.
- `ADC-02`/`ADC-09` 재개설 — 하지 않는다.
- Graphify의 Claude Code 정식 연결(`graphify claude install`)이나
  실제 코드 배선 — 다루지 않는다.
- Production 적용 — 이 ADC는 승인 목록 등재 여부만 판단한다.

---

## 판단 (Q-1). Graphify를 승인된 비강제 Implementation Technology 후보로 확정할 것인가

### Evidence

- CLI 기능(코드/문서 knowledge graph 생성 + `query`/`path`/`explain`)은
  이 저장소 전체(1524 files, 14231 nodes, 17988 edges)를 대상으로
  실제 실행되어 PASS했다(`.claude/docs/integrations/graphify.md`).
  역할 중복 없음도 확인됐다.
- **현재 실제 Jarvis 사용처는 없다** — Development HQ/Investment HQ
  어느 코드도 Graphify를 참조하지 않는다. 이 사실은 그대로 인정한다
  (사용자 지시 3번, RFC-0032 §1).
- `ADR-0011`(Implementation Freedom): "Evidence의 부재 자체는 구현
  기술 선택을 금지하는 사전 허가 조건이 아니다... Governance는 구현
  선호 자체가 아니라 실제 Invariant, Contract, Boundary 및 위험을
  통제한다." 사용처 부재는 Invariant/Contract/Boundary 위반이
  아니므로 이 원칙이 그대로 적용된다.
- `ADC-0001` Module 3(Memory, Defer)의 근거는 "Context 전달의 단일
  경로가 반복 관찰에서 실패한 적이 없다"는, **이 RFC/ADC가 전혀
  건드리지 않는 별개의 사실**이다 — Graphify는 Context 전달
  메커니즘이 아니라 코드/문서 구조를 조회하는 도구이며, 이 ADC는
  둘을 같은 것으로 취급하지 않는다.

### Constraint / Boundary

- 이 Accept는 Memory Kernel Module의 존재를 암시하거나 앞당기지
  않는다 — `ADC-0001` Module 3 Defer, `BASELINE.md` §16.7 Defer
  목록, §10 Out of Scope, §11 Kernel 정의는 이 ADC로 전혀 변경되지
  않는다.
- Graphify를 승인 목록에 올리는 것과 "지금 배선해야 한다"는 전혀
  다른 문장이다 — 이 ADC는 전자만 판단한다.
- 사용자 지시 6·7번: 즉시 Production 적용·실제 코드 배선 승인 안
  함, Architecture/Public Contract/Kernel Boundary 변경 안 함.

### Options

- (a) 승인된 비강제 후보로 확정 — Architecture Module Accept와
  완전히 분리된 순수 Technology 층위 등재. 향후 Memory/Knowledge/
  Relationship 관련 Kernel Module이 **별도 절차로** Accept될 경우,
  그 구현 전략 후보 목록에 Graphify가 이미 올라 있다.
- (b) Adoption하지 않고 기존 tooling-integration-doc 상태 유지.
- (c) Memory Module Defer를 재개설해 결합 — **기각**(사용자 지시
  7번 위반).

### Recommendation

(a). 도구의 기술적 적합성(§Evidence)은 이미 실측됐고, 사용처 부재는
`ADR-0011` 기준으로 Adoption을 막는 근거가 아니다. (b)를 유지하면
향후 실제 필요가 생겼을 때 이미 끝난 CLI 검증을 다시 논쟁해야 하는
비용이 반복된다(Governance v2 P17 — 반복되는 비용은 상위 절차 개선
신호). (a)는 그 비용을 지금 한 번의 명시적 기록으로 없앤다 — 단,
Memory Module Defer와는 철저히 분리해 Architecture Drift를 만들지
않는다.

### Final Judgment

**Accept (a), Conditional·Non-Mandatory, Architecture 무연동.**

1. Graphify는 **향후 Graph 기반 Memory/Knowledge/Relationship
   요구**(코드/문서/개념 간 관계를 그래프로 표현·조회해야 하는
   경우 일반)가 실제로 발생했을 때, 그 구현을 위한 **승인된
   비강제 Implementation Technology 후보**로 확정된다.
2. **Non-Mandatory**: 이 Accept는 Graphify 사용을 강제하지 않으며,
   다른 도구(또는 직접 구현)를 배제하지도 않는다.
3. **즉시 Production 적용·실제 코드 배선은 이 Accept로 승인되지
   않는다** — Claude Code 정식 연결(`graphify claude install`,
   CLAUDE.md 자동 수정 동반)을 포함해 어떤 실제 배선도 별도 승인
   대상이다.
4. **Memory Kernel Module과 명시적으로 분리** — `ADC-0001` Module 3
   Defer는 이 Accept로 재개설되지 않는다. 이 Accept는 "Memory
   Module이 언젠가 Accept될 것이다"를 전제하지 않으며, Memory
   Module Accept 여부와 무관하게 유효한 순수 Technology 사전
   등재다.
5. `BASELINE.md`는 이 Accept로 **수정하지 않는다** — Workflow
   Adapter(`ADC-0034`/`ADR-0019`)와 달리, 이 Accept가 붙을 기존
   Accepted 책임(§16.x)이 없기 때문이다. Baseline 반영은 이
   ADC와 후속 ADR(Decision Record) 자체로 충분하다.
6. `ADC-02`/`ADC-09`는 무관, 재개설하지 않는다.

---

## 종합 Decision

**Accept (Conditional·Non-Mandatory, Architecture 무연동).**

| 대상 | Governance 변경 필요 | 처리 |
|---|---|---|
| Graphify 승인된 비강제 후보 확정 | 필요 | 후속 ADR(ADR-0020)에서 Decision Record로 확정 |
| Memory Kernel Module Accept | 불필요(이 ADC 범위 아님) | `ADC-0001` Module 3 Defer 무변경 |
| `BASELINE.md` 수정 | **불필요** | 대응하는 Accepted 책임이 없어 수정 대상 자체가 없음 |
| Production 적용·Claude Code 정식 연결 | 불필요 | 별도 승인 대상, 무변경 |
| `ADC-02`/`ADC-09` 재개설 | 불필요 | 무변경 |

RFC-0032의 Status/Decision 절은 이 ADC의 결과를 반영해 Resolved로
갱신한다. **후속 ADR**: `docs/architecture/core/
ADR-0020-graphify-implementation-technology-adoption.md`.
