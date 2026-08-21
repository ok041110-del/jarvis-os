# Jarvis OS Roadmap

**Source of Truth**: `Jarvis OS Structure v1.0 — Frozen`(사용자 첨부 PDF, `RFC-0006`→`ADC-0005`→`ADC-0006`→`ADR-0006`→`ADR-0007`로 승인·실행됨), `docs/architecture/baseline/BASELINE.md`(v1.6), `docs/architecture/core/DEVELOPMENT-HQ-V1.0-FREEZE-0001.md`, main 브랜치 실제 구조, `docs/decisions/{rfc,adc,adr}/`.

이 문서는 새 Architecture를 결정하지 않는다. 이미 완료된 것과 이미 승인된 절차(RFC → ADC → ADR)를 그대로 따를 다음 단계를 순서대로 나열할 뿐이다.

---

## Current Position

**Phase 2 완료** — Investment HQ Dogfooding. Phase 0(Structure v1.0 Freeze)과 Phase 1(Development HQ v1.0 Freeze)에 이어 완료되어 main 반영 대기 중이다. Phase 3(Investment HQ v1.0 Freeze) 이후는 전부 미착수 상태이며, Kernel(Phase 5~8)은 필요성이 아직 증명되지 않았으므로 어떤 설계도 시작하지 않는다.

## Next Action

Phase 2가 완료 조건(3개 Team 전부 `hqs/investment/run.py` 경로 EVIDENCE.md 검증)을 충족했다 — `aapl-hq-verify`(Stock Team), `pg-hq-verify`(Dividend Stock Team) EVIDENCE.md 작성 완료(`efa-2026-08`(ETF Team)와 함께 3건). Phase 3(Investment HQ v1.0 Freeze) 착수는 이 세션의 범위가 아니며, 사용자 승인 이후 별도로 시작한다.

---

## Phase 0 — Structure v1.0 Freeze

**상태**: ✅ 완료 (PR #87, main merge 확인됨)

- **목표**: Repository 물리 구조를 Structure v1.0 Target과 정렬하고 문서 taxonomy·Governance 경로를 정리한다.
- **핵심 작업**: `core/execution_layer/` → `core/execution/`, `development-hq/`/`investment-hq/` → `hqs/development/`/`hqs/investment/`, `docs/{01_architecture,02_rfc,03_adc,04_adr}/` → `docs/{architecture/baseline,decisions/{rfc,adc,adr}}/`(명확 대응 항목만; 불명확 140개 문서는 이연).
- **완료 조건**: `RFC-0006`→`ADC-0005`→`ADC-0006`→`ADR-0006`→`ADR-0007` Governance chain 승인, Migration 실행, PR merge.
- **검증 방법**: `pytest --ignore=archive` 182 passed, BASELINE.md 이동 전후 SHA-256 해시 일치, 기존 RFC/ADC/ADR 본문 byte-identical 확인, Pre-Commit Audit(Scope Consistency).
- **다음 Phase로 넘어가는 조건**: 이미 충족(완료).
- **Architecture/Governance 주의사항**: 이 Phase는 물리적 위치 이동만 다뤘다 — Architecture 내용(Meta Architecture, Concept Model, Kernel 정의)은 어느 것도 바뀌지 않았음을 ADR-0007이 명시적으로 확정했다. `docs/00_governance/GLOSSARY.md` 등 140개 불명확 문서의 taxonomy 정리는 **별도 후속 ADC 대상으로 이연된 상태**이며 이 Roadmap이 그 시점을 확정하지 않는다.

---

## Phase 1 — Development HQ v1.0 Freeze

**상태**: ✅ 완료 (`GOVERNANCE-REVIEW-0007` 권고 → `DEVELOPMENT-HQ-V1.0-FREEZE-0001.md`로 승인·확정)

- **목표**: Development HQ를 Jarvis OS 최초의 Reference HQ로 확정하고, 이후 모든 HQ(Investment HQ 등)와 향후 Kernel 후보 판단의 검증 기준선으로 삼는다.
- **핵심 작업**: Vision → Principles → Meta Architecture → Concept Model → System Boundary → Core Component 검토 → Baseline Freeze → Development HQ Reference Architecture → MVP 정의, MVP-0001~0052 Dogfooding·결함 수정.
- **완료 조건**: Development HQ MVP Validation 종료 확정(Stable v1.0 Freeze).
- **검증 방법**: `docs/architecture/core/DEVELOPMENT-HQ-V1.0-FREEZE-0001.md`에 기록된 승인, `pytest`(Development HQ 관련 스위트) 통과 이력.
- **다음 Phase로 넘어가는 조건**: 이미 충족(완료) — Development HQ가 다른 HQ(Investment HQ)에 재사용 가능한 Reference Architecture임이 실증됨(Investment HQ가 이미 이 패턴을 재사용해 구축됨, `hqs/investment/STRUCTURE.md`).
- **Architecture/Governance 주의사항**: "Production 진입 Blocking"은 이 Freeze와 별개로 여전히 Open 상태다 — Development HQ v1.0 Freeze는 "MVP Validation 완료"를 의미하지 "Production 배포 승인"을 의미하지 않는다. 이 구분을 향후 Phase에서도 유지한다.

---

## Phase 2 — Investment HQ Dogfooding

**상태**: ✅ 완료

- **목표**: Investment HQ(Stock/ETF/Dividend Stock Team)가 Development HQ Reference Architecture를 재사용해 실제로 동작함을 반복 실행으로 증명한다.
- **핵심 작업**:
  - 기존 Evidence 정리: Stock Team(5종목), ETF Team(6종목), Dividend Stock Team(7종목) — `docs/research/INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001.md`에 이미 Closure 기록됨.
  - `hqs/investment/run.py` 경로를 통한 HQ-level 실행 검증 — `efa-2026-08`(ETF Team), `aapl-hq-verify`(Stock Team), `pg-hq-verify`(Dividend Stock Team) 3건 전부 EVIDENCE.md 작성 완료.
- **완료 조건**: 3개 Team(Stock/ETF/Dividend Stock) 전부가 `hqs/investment/run.py` 경로에서 최소 1건 이상 EVIDENCE.md와 함께 검증 완료 — **충족**.
- **검증 방법**: 각 실행의 EVIDENCE.md(품질 대조, 핵심 사실 보존율, call_log 계측), `pytest --ignore=archive` 회귀 없음(182 passed, 실행 전/후 동일).
- **다음 Phase로 넘어가는 조건**: `aapl-hq-verify`, `pg-hq-verify` EVIDENCE.md 작성 완료 + 3개 Team 전부 HQ-level 실행 증명 — **충족, Phase 3 착수 가능 상태**(착수 자체는 별도 세션/사용자 승인 대상).
- **Architecture/Governance 주의사항**: 이 Phase에서 발견되는 문제는 "Investment HQ 문제"와 "Dev HQ 문제"로 분리 기록한다(기존 세션 관행). Dev HQ 문제는 반복 Evidence(누적 재현) 없이 수정하지 않는다 — `call_engine()` 콘텐츠 레벨 실패 미검출 문제가 `pg-hq-verify` 실행에서 **4회째 재현**되어 Dev HQ 개선 후보 격상 판정이 재확인됐다(아직 Prototype 미실행, 이번 Phase에서도 구현하지 않음). `hqs/investment/checkpoint.py`가 콘텐츠 레벨 실패를 자동 스킵하지 못해 수동 manifest 편집으로 재개한 사실도 별도 Invest HQ 문제로 기록됨(`pg-hq-verify/EVIDENCE.md` 참조).

---

## Phase 3 — Investment HQ v1.0 Freeze

**상태**: ⬜ 미착수

- **목표**: Investment HQ를 Development HQ와 동등한 수준으로 Freeze해, Jarvis OS가 "Reference HQ 1개"가 아니라 "서로 다른 도메인의 HQ 2개"에서 검증된 상태임을 확정한다.
- **핵심 작업**: Phase 2 Dogfooding 결과 종합 → Governance Review(Development HQ의 `GOVERNANCE-REVIEW-0007` 선례를 참조하되 새로 작성) → Investment HQ Freeze 문서 작성.
- **완료 조건**: Investment HQ Freeze 문서가 RFC → ADC → ADR 절차 없이(Freeze는 새 Architecture 결정이 아니라 기존 검증 결과의 확정이므로, Development HQ Freeze와 동일한 성격) 승인·기록됨.
- **검증 방법**: 3개 Team 전체의 Evidence 재확인, `pytest --ignore=archive` 통과, Investment HQ가 `IMPLEMENTATION_RULES.md` 금지 사항(Registry/Scheduler/Runtime 등 미구현)을 계속 준수하는지 재확인.
- **다음 Phase로 넘어가는 조건**: Investment HQ Freeze 문서 승인.
- **Architecture/Governance 주의사항**: Freeze는 "지금 있는 것을 확정"하는 것이지 "새로 무엇을 만드는" 것이 아니다. Freeze 과정에서 Investment HQ 구조를 개선하고 싶은 유혹이 생기더라도, 그 개선이 Architecture Boundary에 영향을 주면 RFC → ADC → ADR로 분리한다.

---

## Phase 4 — HQ Cross-Validation

**상태**: ⬜ 미착수 (Phase 3 완료 후)

- **목표**: Development HQ와 Investment HQ 두 Freeze된 HQ를 나란히 비교해, 어떤 부분이 우연히 같은 것이 아니라 구조적으로 공통인지 실측한다.
- **핵심 작업**: 두 HQ의 실행 패턴(Wave 구조, Checkpointing, Engine 호출 방식, Agent-Capability 매핑, 병렬화 전략)을 항목별로 대조해 **Common / HQ-Specific / Uncertain** 3분류표를 작성한다.
- **완료 조건**: 3분류표가 실제 코드·Evidence 인용과 함께 문서화됨(추측이 아니라 두 HQ의 실제 코드를 직접 비교한 결과).
- **검증 방법**: 분류표의 "Common" 항목이 실제로 두 HQ에서 동일한 문제를 동일한 방식으로 해결했는지(우연한 유사성이 아닌지) 코드 diff 수준으로 재확인.
- **다음 Phase로 넘어가는 조건**: "Common"으로 분류된 항목이 최소 1개 이상 존재하고, 그 항목이 Kernel 후보의 최소 조건(§Phase 5)을 만족할 가능성이 있다고 판단됨.
- **Architecture/Governance 주의사항**: 이 Phase는 비교와 분류만 한다 — Kernel을 설계하지 않는다. "Common"이 하나도 없다면 Kernel Candidate 도출 없이 이 Phase에서 멈추고, 그 결과 자체를 기록한다(강제로 공통점을 만들어내지 않는다).

---

## Phase 5 — Kernel Candidate

**상태**: ⬜ 미착수 (Phase 4 완료 후, 조건부)

- **목표**: Phase 4의 "Common" 항목 중 실제로 Kernel로 추출할 가치가 있는 후보만 정의한다. **구현하지 않는다.**
- **핵심 작업**: 각 Common 항목을 다음 5개 기준으로 판단한다 — 공통성(두 HQ 모두에서 실제로 나타나는가), 도메인 독립성(Stock/ETF/Dividend Stock이나 코드 리뷰 같은 특정 도메인 지식에 의존하지 않는가), 반복성(여러 HQ에서 반복 관찰되는가, 1회성이 아닌가), 안정성(요구사항이 자주 바뀌지 않는가), 재사용성(그대로 재사용 가능한가, HQ마다 재작성이 필요하지 않은가).
- **완료 조건**: Kernel Candidate 목록(0개일 수도 있음)과 각 후보의 5기준 판단 근거가 문서화됨.
- **검증 방법**: 각 후보가 실제로 도메인 로직을 포함하지 않는지 코드 검토(Kernel에 도메인 로직이 들어가면 이미 Candidate 자격 상실).
- **다음 Phase로 넘어가는 조건**: Kernel Candidate가 1개 이상 존재.
- **Architecture/Governance 주의사항**: **이 Phase에서 코드를 작성하지 않는다.** Structure v1.0의 `core/registry/`, `core/communication/{events,context,memory,observability}` 등은 Target Boundary일 뿐이며, Candidate가 이 카테고리 중 어디에 해당하는지 판단하는 것도 이 Phase가 아니라 Phase 7(Kernel Governance)의 RFC에서 다룬다.

---

## Phase 6 — Kernel Prototype & Validation

**상태**: ⬜ 미착수 (Phase 5에서 Candidate 발생 시)

- **목표**: Kernel Candidate가 실제로 두 HQ에서 독립적으로 동작하는지, Architecture Boundary(Kernel이 도메인을 모르고, HQ가 Kernel 내부를 몰라도 되는지)를 실측한다.
- **핵심 작업**: 격리된 Prototype 디렉터리(기존 세션 관행: `projects/*-prototype/` 패턴)에서 Candidate를 구현 → Development HQ에 적용해보고 Regression 확인 → Investment HQ에 동일하게 적용해보고 Regression 확인.
- **완료 조건**: 두 HQ 모두에서 기존 기능·Evidence가 깨지지 않고, Prototype이 실제로 중복 코드를 제거하거나 실질적 가치를 만들어냄이 실측됨.
- **검증 방법**: 각 HQ의 기존 `pytest` 스위트 전체 재실행(회귀 0건), Prototype 적용 전후 비교 Evidence.
- **다음 Phase로 넘어가는 조건**: Prototype이 두 HQ 모두에서 성공(회귀 없음 + 가치 실증). 실패 시 Phase 5로 돌아가 Candidate를 기각하거나 재정의한다 — Phase 7로 강행하지 않는다.
- **Architecture/Governance 주의사항**: Prototype은 `development-hq/IMPLEMENTATION_RULES.md`·`hqs/investment/STRUCTURE.md`의 금지 사항(Registry/Scheduler/Runtime 등)을 이 단계에서도 그대로 준수한다 — "Prototype이니까 예외"는 없다. Prototype 코드는 tracked 브랜치에 반영하지 않거나(기존 `ENGINE-CONNECT-0005` 격리 원칙), 반영하더라도 명확히 실험용임을 문서화한다.

---

## Phase 7 — Kernel Governance

**상태**: ⬜ 미착수 (Phase 6 성공 시)

- **목표**: Phase 6에서 필요성이 실증된 Kernel Candidate만 정식 Architecture Decision으로 확정한다.
- **핵심 작업**: RFC 작성(Kernel Candidate의 책임·경계 제안) → ADC(대안 비교, 예: `core/registry/`와 `core/communication/` 중 어느 축에 속하는지) → ADR(확정).
- **완료 조건**: ADR 승인, `docs/architecture/baseline/BASELINE.md` 갱신(버전 증가).
- **검증 방법**: `docs/decisions/adc/README.md`의 채택 기준("지금 결정하지 않으면 상위 Architecture를 진행할 수 없다" 또는 "결정이 늦어질수록 되돌리는 비용이 매우 커진다")을 실제로 충족하는지 재확인.
- **다음 Phase로 넘어가는 조건**: ADR Accepted.
- **Architecture/Governance 주의사항**: 이 Phase가 이번 Roadmap에서 유일하게 "새 Architecture 결정"을 만드는 지점이다 — 그 외 모든 Phase는 기존 결정의 실행이거나 검증이다. ADR은 Kernel의 최소 책임만 확정하고, "혹시 필요할지 모르는" 기능을 미리 넣지 않는다(YAGNI를 Governance 절차 안에서 지킨다).

---

## Phase 8 — Kernel Implementation

**상태**: ⬜ 미착수 (Phase 7 ADR 승인 시)

- **목표**: ADR에서 확정된 범위만 실제로 구현한다.
- **핵심 작업**: ADR이 지정한 최소 Kernel 코드 작성(예: `core/registry/` 또는 `core/communication/` 하위 특정 모듈 1개).
- **완료 조건**: ADR 범위와 실제 구현 diff가 1:1로 일치(초과 구현 없음).
- **검증 방법**: 구현 후 `pytest --ignore=archive` 전체 통과, 코드 리뷰로 ADR 범위 초과 여부 확인.
- **다음 Phase로 넘어가는 조건**: Kernel 최소 구현이 독립적으로 테스트를 통과(아직 HQ에 연결되지 않은 상태).
- **Architecture/Governance 주의사항**: **Structure v1.0에 나열된 모든 디렉터리(`core/registry/{runtime,scheduler,policy}`, `core/communication/{events,context,memory,observability}` 등)를 한꺼번에 만들지 않는다** — ADR이 확정한 것만 만든다. 나머지는 여전히 Target Boundary로만 존재한다.

---

## Phase 9 — HQ Migration & Cross-HQ Regression

**상태**: ⬜ 미착수 (Phase 8 완료 후)

- **목표**: Development HQ와 Investment HQ가 새로 구현된 Kernel을 실제로 사용하도록 전환하고, 전환 후에도 기존 기능이 깨지지 않음을 증명한다.
- **핵심 작업**: 각 HQ의 중복 코드(Kernel로 추출된 부분)를 Kernel 호출로 교체 — 순서는 Phase 1(core/execution) Migration이 세운 선례(한 번에 모두 바꾸지 않고 단계적으로, 각 단계 후 검증)를 따른다.
- **완료 조건**: 두 HQ 모두 Kernel을 통해 동작하며, 기존 Evidence(18건 Dogfooding 등)가 재현됨.
- **검증 방법**: 각 HQ의 `pytest` 전체 재실행 + 기존 Dogfooding 산출물과 신규 실행 결과의 핵심 사실 보존율 대조.
- **다음 Phase로 넘어가는 조건**: Cross-HQ Regression 0건.
- **Architecture/Governance 주의사항**: 기존 완료된 Dogfooding 프로젝트(`projects/*`)는 소급 수정하지 않는다(기존 세션 관행 유지) — 새 Kernel 경로는 신규 실행부터 적용한다.

---

## Phase 10 — Runtime

**상태**: ⬜ 미착수, 필요성 미증명

- **목표**: HQ가 2개를 넘어서거나 실행 스케줄링·재시도·동시성 관리가 반복적으로 필요해질 때만 Runtime을 도입한다.
- **핵심 작업**: (착수 시점 미정) Runtime이 실제로 해결해야 하는 문제가 Phase 2~9 과정에서 반복 관찰된 이후에만 정의.
- **완료 조건**: 미정 — Runtime 필요성이 아직 실증되지 않음.
- **검증 방법**: 미정.
- **다음 Phase로 넘어가는 조건**: Phase 9까지의 과정에서 "Task Dispatcher 승격"과 유사한 반복 신호(RFC-0004가 이미 이 질문을 열어둔 바 있음, 현재 `docs/decisions/rfc/RFC-0005-development-hq-execution-boundary.md` Open)가 재현될 것.
- **Architecture/Governance 주의사항**: **Runtime을 "언젠가 필요할 것 같아서" 먼저 만들지 않는다.** 지금까지 모든 HQ가 하드코딩된 순차 호출로 충분히 동작해왔다는 사실(`IMPLEMENTATION_RULES.md` 금지 사항)이 계속 재확인되면, 이 Phase는 무기한 보류될 수 있다 — 그것이 실패가 아니라 올바른 결과다.

---

## Phase 11 — Control Plane / Dashboard

**상태**: ⬜ 미착수, 필요성 미증명

- **목표**: HQ/Agent/Task/Workflow/Execution/State/Artifact를 사람이 외부에서 관찰·관리할 필요가 실제로 생겼을 때 Dashboard를 만든다.
- **핵심 작업**: (착수 시점 미정) 현재는 CLI 실행(`hqs/development/mvp/cli.py`, `hqs/investment/run.py`)만으로 충분한지 계속 관찰한다.
- **완료 조건**: 미정.
- **검증 방법**: 미정.
- **다음 Phase로 넘어가는 조건**: HQ 수 증가 또는 실행 빈도 증가로 CLI 개별 실행이 실제로 병목이 됨이 관찰될 것.
- **Architecture/Governance 주의사항**: Structure v1.0의 `dashboard/{web,api,events,components,views,auth}`는 전부 Target Boundary다 — 지금 어떤 하위 디렉터리도 미리 만들지 않는다.

---

## Phase 12 — Automation / Integration

**상태**: ⬜ 미착수, 필요성 미증명

- **목표**: 반복 업무(예: PR 생성·Merge·CI 대응)를 자동화하고, GitHub/Notion/외부 Engine 등과의 통합을 정리한다. **새로 만들기(Build)보다 이미 있는 것을 연결하기(Integrate)를 우선한다.**
- **핵심 작업**: (착수 시점 미정) 현재 세션에서 이미 GitHub PR/Merge 워크플로우는 MCP 도구로 연결되어 있음 — 이를 정식 `integrations/` 구조로 옮길 필요가 실제로 생기는지 관찰.
- **완료 조건**: 미정.
- **검증 방법**: 미정.
- **다음 Phase로 넘어가는 조건**: 현재 세션 내에서 반복되는 수작업 패턴(예: 매번 동일한 Governance chain 문서 작성)이 자동화 없이는 감당 안 될 정도로 반복될 것.
- **Architecture/Governance 주의사항**: `integrations/mcp/{github,notion,providers}`도 Target Boundary다 — 지금 있는 GitHub MCP 연동을 이 구조로 강제 이전하지 않는다(이미 동작하는 것을 이유 없이 재구성하지 않는다).

---

## Phase 13 — New HQ Expansion

**상태**: ⬜ 미착수, 필요성 미증명

- **목표**: Kernel을 재사용해 세 번째 HQ를 추가한다.
- **핵심 작업**: (착수 시점 미정) 신규 HQ는 Investment HQ가 이미 증명한 방식(Development HQ 문서 구조를 강제 답습하지 않고, README/STRUCTURE 중심의 경량 모델 채택 — ADR-0007 §3 관례)을 따른다.
- **완료 조건**: 미정.
- **검증 방법**: 신규 HQ가 Kernel을 통해 동작하고, HQ-specific 도메인 로직이 Kernel에 유출되지 않았음을 코드 검토로 확인.
- **다음 Phase로 넘어가는 조건**: 없음(Roadmap의 마지막 Phase) — 이후는 Phase 4(Cross-Validation)로 되돌아가 3개 HQ 기준으로 반복.
- **Architecture/Governance 주의사항**: 신규 HQ 추가 자체는 RFC 대상이 아니다(Investment HQ 선례 — `hqs/investment/STRUCTURE.md`가 이미 이 판단 근거를 기록함, Dev HQ Reference Architecture 재사용). 단, 그 HQ가 기존 Kernel 경계를 벗어나는 요구를 하면 그 지점만 RFC 대상이다.

---

## 원칙 요약 (모든 Phase에 공통 적용)

- Freeze된 Structure v1.0은 임의 변경하지 않는다 — 변경이 필요하면 RFC → ADC → ADR.
- Kernel은 Phase 7(Governance) 이전에 선제 설계·구현하지 않는다.
- 모든 Kernel Candidate는 실제 Dogfooding/Evidence로 필요성이 증명되어야 한다(Phase 4~6).
- Kernel에는 도메인 로직을 넣지 않는다 — HQ-specific 책임과 Kernel 책임을 항상 분리한다.
- Dashboard/Runtime/Registry/Communication/Memory 등은 Structure v1.0에 이름이 있다는 이유만으로 선제 구현하지 않는다 — 각 Phase의 "다음 Phase로 넘어가는 조건"이 실제로 충족될 때만 착수한다.
- `scripts/` 등 보조 디렉터리는 반복 필요성이 실제로 발생했을 때만 유연하게 추가/삭제한다 — Structure v1.0 문서 자신이 "모든 디렉터리를 즉시 생성하지 않는다"고 명시했다.
- Historical Evidence와 기존 Governance 문서(RFC/ADC/ADR/Observation)는 어떤 Phase에서도 소급 수정하지 않는다.
- 현재 Repository 상태가 이 Roadmap의 전제(Source of Truth)와 충돌하는 것이 발견되면, 임의로 둘 중 하나를 고쳐 맞추지 말고 BLOCKED로 보고한다.
