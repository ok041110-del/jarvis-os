# KERNEL-BOUNDARY-RESPONSIBILITY-OBSERVATION-0001: Development HQ v2.0 이후 Kernel Responsibility 관찰

**문서 성격**: Observation(관찰 기록). Kernel Component를 찾는
작업이 아니라 Kernel Component가 필요한지 판단할 Evidence를 정리하는
작업이다. Production Code·Architecture·Contract·BASELINE을 변경하지
않는다. RFC/ADC/ADR을 작성하지 않는다. Phase 7/8을 구현·착수하지
않는다. ADC-02·ADC-09·ADC-10·Production Blocking·AGG Data Boundary의
기존 상태를 변경하지 않는다.

---

## 1. Observation Scope

**질문**: "현재까지 실제로 구현/검증된 HQ 및 Workflow 사례에서
기존 HQ-specific Boundary를 넘어서는 반복적이고 공통적인 Kernel
Responsibility가 나타났는가?"

대상: Development HQ v2.0(Freeze, Stage 01~05, Integrated Workflow,
CLI, Agent Definition 0001, Agent Package Refactoring, AST Context,
기존 MVP Workflow), Investment HQ(현재 Repository의 실제 코드/문서:
`hqs/investment/{run.py,checkpoint.py,engine_client.py,trader.py,
teams/,STRUCTURE.md}`, Stock/ETF/Dividend Stock Team Definition),
기존 Kernel Validation Evidence(Phase 4~7, `GOVERNANCE-TRIGGER-OBSERVATION-0001`),
`BASELINE.md`(v1.6), `HANDOVER.md`. 존재하지 않는 구현/문서는
추측해서 추가하지 않았다.

---

## 2. Existing Boundary

- `BASELINE.md` §10: Kernel Component Architecture/Component
  Design/Development HQ 내부 설계는 Out of Scope.
- `BASELINE.md` §16: Kernel Module Accept 2건(Governance, Execution
  Layer), Defer 3건(Workflow, Memory, Event Bus).
- Phase 5(`PHASE5-KERNEL-CANDIDATE-0001.md`) 확정 Candidate: **Parallel
  Execution(원시 기법)** 1건. Checkpointing은 공통성 기준부터
  미충족해 Investment-specific 유지(재확인 대상, 새로 판단하지 않음).
- Phase 4(`PHASE4-HQ-CROSS-VALIDATION-0001.md`) Common 판정: Engine
  호출 방식(`call_engine()`), Parallel Execution. Agent-Capability
  매핑(아티팩트)은 **Uncertain**(두 HQ의 자료구조·용도가 다름).
- Phase 7(`ADC-0012` DEFER, `PHASE7-RESUME-REVIEW-0001.md` BLOCKED):
  6개 재개 근거 중 5개 미충족(Engine 수 ≥2 포함) — 본 Observation
  시점에도 재확인 대상.

이번 Observation은 이 기존 경계를 뒤집지 않는다 — Dev HQ v2.0 이후
**새로 나타난** Responsibility만 찾는다.

---

## 3. Observed Responsibilities

| 사례 | Responsibility | Owner | 반복 여부 | 분류 |
|---|---|---|---|---|
| `call_engine()` (`hqs/development/mvp/engine.py`) | Engine 호출 | Dev HQ 원 소유, Investment HQ가 live import(`hqs/investment/engine_client.py`) | 반복(기존 Phase 4 Common, 변화 없음) | CROSS-HQ PATTERN(기존, 재확인) |
| Parallel Execution(`ThreadPoolExecutor`) | 독립 Task 동시 실행 | Dev HQ(PR #60/61)·Investment HQ(PR #77/80) 각각 독립 구현, Phase 6 Prototype으로 도메인 독립성 검증 완료 | 반복(기존 Phase 5/6 Candidate, 변화 없음) | EXTRACTION CANDIDATE(기존, Phase 7에서 이미 RFC-0012로 다룸 — 신규 아님) |
| Checkpointing(`hqs/investment/checkpoint.py`) | 단계 완료 저장·재개 | Investment HQ만 | Dev HQ v2.0(Stage 01~05/`workflow.py`)에 동등 기능 없음 | HQ-SPECIFIC |
| Content-level 실패 미검출(`call_engine()`이 API 성공 응답 안의 콘텐츠 레벨 실패를 구분하지 못함) | Engine 호출 결과 검증 | `checkpoint.py`의 `ContentFailureError`/`_is_known_content_failure`가 Investment HQ 단에서 사후 보정; Dev HQ `engine.py`는 이 검증 없음(원본 그대로) | Investment HQ 실행에서 4회 재현(roadmap.md Phase 2 기록, 기존 관찰) — Dev HQ v2.0도 이 결함을 수정하지 않음(engine.py 무변경 확인) | CROSS-HQ PATTERN(기존, HANDOVER가 이미 "COMMON, Dev HQ 소관"으로 분류 — 신규 Evidence 아님) |
| Agent Package 물리 분리(`hqs/development/mvp/agents/{requirements,design,backend,qa}.py`) | 역할별 코드 분리 | Dev HQ v2.0 | Investment HQ `teams/{stock,etf,dividend_stock}_team.py`가 표면적으로 유사한 "역할/도메인별 파일 분리" 패턴을 보이나, 이는 코드 조직 관례이지 Kernel 책임이 아님 | HQ-SPECIFIC(표면적 유사성만, §5 기준 3 미충족 — 이름이 비슷하다는 이유로 승격하지 않음) |
| AST Context(`hqs/development/mvp/ast_context.py`) | 소스 코드 정적 분석 기반 Context 추출 | Dev HQ v2.0 | Investment HQ에 대응 개념 없음(Investment는 시장 데이터/API 기반, 코드베이스 정적 분석 대상 아님) | HQ-SPECIFIC |
| Project Intelligence(`hqs/development/mvp/project_intelligence.py`) | Planning 단계 파일 경로 수집 | Dev HQ | Investment HQ에 대응 개념 없음 | HQ-SPECIFIC |
| Integrated Workflow(`workflow.py`, Stage 1→5 하드코딩 호출) | Task 순서 실행 | Dev HQ v2.0 | Investment HQ `run.py`도 Wave 순서를 하드코딩 호출 — 두 HQ 모두 "Workflow Parser/Scheduler 없이 직접 호출"이라는 **원칙**(IMPLEMENTATION_RULES 금지 사항 준수)을 공유하지만, 이는 "무엇을 만들지 않았는가"에 대한 합의이지 추출할 공통 **코드/Responsibility**가 아님 | HQ-SPECIFIC(원칙 준수는 Governance 차원에서 이미 공유됨, 새 Responsibility 아님) |
| CLI(`hqs/development/mvp/cli.py`) | 실행 진입점 | Dev HQ v2.0 | Investment HQ `run.py`가 유사 역할이나 별도 CLI 프레임워크 없이 각자 스크립트 진입점 — 통합 CLI 계층 Evidence 없음 | HQ-SPECIFIC |
| Agent Definition 0001(Requirements/Design/Backend/QA) | Capability별 Agent 역할 정의 | Dev HQ v2.0 | Investment HQ의 Team Role(Bull/Bear/Trader 등, 5/6/7개)은 §7 "Agent 구성 및 역할 결정"이 이미 HQ 책임으로 확정한 개념 수준의 Common Domain(Phase 4 기 확인) — 구현 아티팩트 수준에서는 여전히 서로 다른 구조 | HQ-SPECIFIC(구현 수준), 개념 수준은 기존 Common Domain 판정 유지(신규 아님) |

---

## 4. Cross-HQ Patterns

실제로 반복되는 Responsibility는 §3에서 확인된 3건뿐이며, 전부
**기존에 이미 식별·판정된 항목**이다. Dev HQ v2.0이 새로 추가한
어떤 코드/문서에서도 새로운 반복 사례는 발견되지 않았다.

1. **Engine 호출**(`call_engine`) — 기존 Phase 4 Common, 변화 없음.
2. **Parallel Execution** — 기존 Phase 5/6 Candidate, Phase 7에서
   이미 RFC-0012/ADC-0012로 다뤄짐(DEFER). 신규 판단 아님.
3. **Content-level 실패 미검출** — 기존에 `roadmap.md`(Phase 2
   기록)와 `HANDOVER.md`가 "COMMON, Dev HQ 소관"으로 이미 분류.
   Dev HQ v2.0이 이를 수정하지 않았으므로 상태 변화 없음 — 신규
   Evidence 아님, 재확인일 뿐.

---

## 5. Extraction Candidates

**No New Extraction Candidate identified.**

§4의 3건 모두 이미 기존 문서(Phase 4/5/6/7, HANDOVER, roadmap.md)가
식별·판정을 완료한 항목이며, 이번 Observation이 그 상태를 바꿀
근거를 추가하지 않았다. §5 판정 기준(1~6 전부 충족 필요) 적용 결과:

- Parallel Execution: 기준 1~4는 충족(Phase 5/6에서 이미 확인)하나,
  기준 6("Kernel로 추출했을 때 Architecture Boundary가 더 명확해진다")의
  실제 Governance 진행은 `ADC-0012`가 이미 DEFER로 판정 — **이번
  Observation은 이 판정을 재론하지 않는다**(§9 보존 규칙과 동일한
  원칙 — 기존 Governance Decision 임의 변경 금지). RFC Candidate로
  다시 기록하지 않음(RFC-0012가 이미 Proposed 상태로 존재).
- Content-level 실패 미검출: 기준 2(반복, 4회)는 충족하나 기준
  4("특정 HQ에 종속되지 않는다")가 애매하다 — 결함은 공유 함수
  (`call_engine`) 안에 있지만 **관측**은 Investment HQ의 Checkpointing
  경로에서만 이뤄졌다(Dev HQ는 이 실패 유형을 별도로 검증한 Evidence
  없음). 기준 5("기존 BASELINE Boundary만으로 설명하기 어렵다")도
  미충족 — `PHASE9-CLOSURE-0001.md`가 이미 Engine Adapter를
  NEED-DRIVEN DEFER로 판정했고 그 판정의 재검토 조건(Engine 수 ≥2
  등)도 그대로 미충족 상태다. **Kernel Extraction Candidate로
  승격하지 않는다** — 기존 "Dev HQ 개선 후보"(Kernel 아님) 판정을
  유지.

---

## 6. Final Verdict

**NO NEW KERNEL RESPONSIBILITY**

Dev HQ v2.0 완료 이후 실제 Evidence를 재검토한 결과, 기존
HQ-specific Boundary를 넘어서는 새로운 반복적·공통적 Kernel
Responsibility는 발견되지 않았다. 관찰된 3건의 Cross-HQ Pattern은
전부 기존 문서가 이미 식별·판정을 완료한 것이며, 이번 Observation은
그 상태를 재확인했을 뿐이다.

---

## Phase 7 상태

**BLOCKED 유지.** 새로운 Evidence가 발견되지 않았으므로
`PHASE7-RESUME-REVIEW-0001.md`의 판정을 변경할 근거가 없다. Phase 7을
구현하지 않는다.

## 기존 Open Issue 보존 확인

ADC-02, ADC-09, ADC-10, Production Blocking, AGG Data Boundary 중
어느 것도 이번 Observation에서 재판정·수정하지 않았다 — 전부 상태만
인용했다(§2, §5).

---

## 최종 보고

1. **무엇을 관찰했는가**: Dev HQ v2.0(Stage/Workflow/CLI/Agent
   Definition/Agent Package/AST Context)과 Investment HQ(run.py,
   checkpoint.py, engine_client.py, teams/) 실제 코드·문서를
   Responsibility 단위로 대조.
2. **확인한 실제 Evidence**: `hqs/development/mvp/`,
   `hqs/investment/`의 실제 파일 구조·함수, 기존 Phase 4~7 문서,
   `HANDOVER.md`, `roadmap.md` Phase 2 기록.
3. **반복되는 공통 Responsibility**: 3건 — Engine 호출, Parallel
   Execution, Content-level 실패 미검출. **전부 기존에 이미
   식별된 항목**(신규 없음).
4. **현재 Boundary 유지 여부**: 유지된다. Dev HQ v2.0의 신규 코드
   (AST Context, Agent Package, Project Intelligence, CLI)는 전부
   HQ-SPECIFIC — Investment HQ에 대응 사례가 없거나 표면적 유사성만
   있을 뿐 Responsibility 수준의 반복이 아니다.
5. **Extraction Candidate**: 없음(§5, No New Extraction Candidate).
6. **Phase 7 상태**: BLOCKED 유지.
7. **Governance 영향**: 없음 — RFC/ADC/ADR 미작성, 기존 Decision
   무변경, ADC-02/09/10·Production Blocking·AGG Data Boundary 무변경.
8. **남은 관찰 대상**: `GOVERNANCE-TRIGGER-OBSERVATION-0001`이 이미
   정리한 자연 관찰 대기 항목(두 번째 Engine 등장, Workflow/Memory/
   Event Bus 실제 필요 사례)과 동일 — 인위적으로 만들지 않는다.
9. **다음 Action**: 신규 Kernel Component 설계 착수 없음. Dev HQ의
   Content-level 실패 미검출은 기존 판정대로 "Dev HQ 개선 후보"로만
   남겨둔다(Kernel 대상 아님).

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음
Tests: 미실행(Production Code 변경 없어 불필요)
E2E: 미실행
RFC: 없음(신규 작성 안 함, RFC Candidate도 신규 없음)
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: (본 문서 커밋 예정)
Branch: `claude/kernel-boundary-responsibility-observation`
Next Implementation Candidate: 없음(Kernel Component 착수 근거 없음, 자연 관찰 대기만 유효)
