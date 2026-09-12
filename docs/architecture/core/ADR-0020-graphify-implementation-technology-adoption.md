# ADR-0020: Graphify — 승인된 비강제 Implementation Technology 확정 (향후 Graph 기반 Memory/Knowledge/Relationship 요구 대비)

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0020` |
| 제목 | RFC-0032(Boundary Question) → ADC-0035(Q-1 Final Judgment)의 판단을 Decision Record로 확정한다 — Graphify를 향후 Graph 기반 Memory/Knowledge/Relationship 요구의 승인된 비강제 Implementation Technology 후보로 등재한다 |
| 상태 | **Accepted.** |
| Context | `docs/architecture/core/RFC-0032-graphify-implementation-technology-adoption.md`(Q-1 Boundary Question) + `docs/architecture/core/ADC-0035-graphify-implementation-technology-adoption.md`(Accept, Conditional·Non-Mandatory, Architecture 무연동) |
| 관련 RFC | `RFC-0032` |
| 관련 ADC | `ADC-0035` |
| Supersede 대상 | 없음 — 기존에 Graphify를 다룬 Decision Record가 없다(`.claude/docs/integrations/graphify.md`는 실행환경 채택 evidence이지 Decision Record가 아님) |
| 명시적으로 건드리지 않는 기존 Decision | `ADC-0001-core-baseline.md` Module 3(Memory, Defer) — 이 ADR로 재개설·전복되지 않는다 |
| Evidence | `.claude/docs/integrations/graphify.md`(2026-08-30, 이 저장소 대상 실제 CLI 검증: `update`/`query`/`path`/`explain` PASS, 1524 files/14231 nodes/17988 edges), `ADR-0011`(Implementation Freedom) |

이 ADR은 `ADC-0035`가 이미 내린 Q-1 Final Judgment를 다시 논의하지
않는다. 이 ADR이 하는 일은 그 판단을 어디에 어떤 형태로 기록할지
구체화하는 것뿐이다.

## Out of Scope (이 ADR이 다루지 않는 것)

| 항목 | 근거 |
|---|---|
| Memory(또는 Knowledge/Relationship) Kernel Module Accept | `ADC-0035` 판단 — `ADC-0001` Module 3 Defer 무변경, 이 ADR의 범위 밖 |
| 즉시 Production 적용·실제 코드 배선 | 사용자 지시 6번 — 승인하지 않는다 |
| Claude Code 정식 연결(`graphify claude install`) | CLAUDE.md 자동 수정 동반 — 별도 승인 대상, 무변경 |
| `ADC-02`/`ADC-09` 재개설 | 무관, 하지 않는다 |
| `BASELINE.md` 수정 | 대응하는 Accepted Kernel 책임이 없어 수정 대상 자체가 없음(§16.6 Workflow Adapter/LangGraph 사례와의 핵심 차이, §2 참고) |
| 코드 변경 | 없음 |

---

## Decision

### 1. Graphify Adoption 확정 (ADC-0035 Q-1 Final Judgment 반영)

**Graphify는 향후 Graph 기반 Memory/Knowledge/Relationship
요구(코드/문서/개념 간 관계를 그래프로 표현·조회해야 하는 필요
일반)가 실제로 발생했을 때 사용할 수 있는, 승인된 비강제
Implementation Technology 후보로 확정된다.**

- **근거로 확정된 사실**: CLI 기능(`update`/`query`/`path`/`explain`)이
  이 저장소 전체(1524 files, 14231 nodes, 17988 edges)를 대상으로
  실제 실행되어 PASS했고, 기존 도구(Claude-Mem/Task Observer/
  OmniRoute)와 역할 중복이 없다(`.claude/docs/integrations/
  graphify.md`, 재검증하지 않고 그대로 인용).
- **현재 실제 사용처 부재를 그대로 인정한다**: Development HQ/
  Investment HQ 어떤 코드도 Graphify를 참조하지 않는다. 이 사실은
  Adoption 여부와 무관하며, 왜곡하거나 감추지 않는다.
- **Non-Mandatory**: 이 Accept는 사용을 강제하지 않는다. 다른 도구나
  직접 구현을 배제하지도 않는다.

### 2. Architecture와의 관계 — `ADR-0019`(LangGraph)와의 핵심 차이

`ADR-0019`는 이미 Accept된 Kernel 책임(§16.6 Workflow Adapter)의
**구현 전략**을 확정했으므로 `BASELINE.md` §16.6에 상태 갱신 노트를
추가할 대상이 있었다. 이번 Graphify Adoption은 그런 대상이 없다 —
Memory(Context/Knowledge 저장·전달 후보)는 `ADC-0001` Module 3에서
**Defer**된 채로 남아 있고, 이 ADR은 그 상태를 조금도 바꾸지 않는다.
그러므로:

- `BASELINE.md`의 어떤 절(§6, §10, §11, §16.x, §17)도 이 ADR로
  수정하지 않는다.
- 이 Adoption은 "Memory Module이 언젠가 Accept될 것"을 전제하거나
  암시하지 않는다 — Memory Module Accept 여부와 독립적으로 유효한
  순수 Technology 층위 기록이다.
- Baseline에 대한 "반영"은 이 Decision Record(RFC-0032/ADC-0035/
  ADR-0020) 자체가 전부다 — Architecture 문서를 건드리는 형태의
  반영은 존재하지 않는다.

### 3. 실제 반영 범위

| 대상 파일 | 반영 내용 |
|---|---|
| `docs/architecture/core/RFC-0032-*.md` | Status/Decision을 Resolved·Accept로 갱신(완료) |
| `.claude/docs/integrations/graphify.md` | "도입 판단" 절 말미에 이 ADR을 인용하는 append-only 갱신 노트 추가 — 기존 CLI 검증 기록·미실행 사유는 무변경 |
| `docs/architecture/baseline/BASELINE.md` | **수정 없음**(§2 근거) |
| `hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md` | **수정 없음** — 대상 아님 |
| 코드 | **수정 없음** |

## 4. Architecture/Contract/Kernel Boundary 불변 확인

- `BASELINE.md` 전체(§6 Concept Model, §10 Out of Scope, §11 Kernel
  정의, §16 Kernel Modules, §17 Version) — **한 글자도 변경하지
  않는다.**
- `ADC-0001` Module 3(Memory, Defer) — 재개설·전복하지 않는다.
- Kernel Public Contract(§14) — 대상 아님, 무변경.
- 코드 파일 — 이 ADR로 일절 수정하지 않는다.

## 5. 기존 RFC/ADC/ADR/Freeze와의 충돌 확인

- **`ADC-0001` Module 3(Memory, Defer)**: 충돌 없음 — 이 ADR은 그
  판정을 인용만 하고 재론하지 않는다. Graphify(코드/문서 구조 조회
  도구)와 Memory Module(Task 간 Context 전달 경로)은 별개 대상으로
  명시적으로 구분했다(RFC-0032 §1, `ADC-0035` §Evidence).
- **`ADR-0011`(Implementation Freedom)**: 충돌 없음 — 이 ADR은 그
  원칙("Evidence 부재가 사전 금지 조건도, Adoption의 필수 전제도
  아니다")을 실제로 적용한 두 번째 사례다(`ADR-0019`가 첫 번째).
- **`ADR-0019`/`ADC-0034`(LangGraph)**: 충돌 없음 — 같은 절차 형식을
  재사용했으나 Architecture 연동 여부가 다르다는 점을 §2에서
  명시적으로 구분했다.
- **`ADC-02`/`ADC-09`**: 무관, 재개설되지 않았다.

---

## Consequences

- Graphify는 이제 "실행환경 채택 evidence"(비공식 tooling 기록)
  단계를 넘어, **정식 Decision Record(RFC-0032/ADC-0035/ADR-0020)로
  승인된 비강제 Implementation Technology 후보** 지위를 갖는다.
- 향후 Graph 기반 Memory/Knowledge/Relationship 필요가 실제로
  관찰되면, 이미 끝난 CLI 적합성 검증을 다시 논쟁하지 않고 곧바로
  이 ADR을 인용해 구현 검토를 시작할 수 있다.
- `ADC-0001` Module 3(Memory, Defer)은 이 ADR로 인해 어떤 상태
  변화도 겪지 않는다 — Memory Module Accept는 여전히 그 자신의
  재평가 조건(반복 관찰)이 충족될 때만 별도로 논의된다.
- `BASELINE.md`는 이 ADR로 전혀 변경되지 않는다 — Architecture
  Baseline에 새로운 Concept·Component·Layer가 추가되지 않는다.
- 남는 절차: Graphify의 Claude Code 정식 연결이나 실제 코드 배선은
  각각 별도 승인이 필요하며, 이 ADR은 그 절차를 대신하거나
  앞당기지 않는다.
