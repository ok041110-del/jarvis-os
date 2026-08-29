# Dashboard Backend Data Inventory 0001 — Read-Only 조사

## 문서 성격

이 문서는 **Dashboard가 요구하는 정보 전체에 대해 실제 Backend/Evidence
Source가 존재하는지 read-only로 조사한 결과**다. 새로운 Architecture
결정이나 Contract를 만들지 않는다. `BASELINE.md`, `ADC.md`, Development
HQ/Investment HQ Freeze 문서, Production Code(`hqs/*`, `core/`,
`projects/unified-dashboard/*.py`), Frontend(`projects/unified-dashboard/frontend/`)
어느 것도 수정하지 않았다. RFC/ADC/ADR을 생성하지 않는다 — 필요 여부와
근거만 §7에 기록한다.

**조사 시점**: 2026-08-29, `claude/dashboard-backend-inventory-dqa8t7`
브랜치(`origin/main` 기준, diff 없음 — main HEAD와 동일 커밋).

## 조사 범위의 한계 — Notion 미접근

이 세션은 **Notion에 접근할 수 있는 도구를 갖고 있지 않다**(MCP Notion
커넥터 미탑재, 이번 조사에서 `ToolSearch`로 확인). 따라서 사용자가
언급한 "Notion의 Dashboard Architecture Implementation Status" 페이지
원문은 이 조사에서 직접 읽지 못했다. 대신 저장소에 커밋된, 같은 주제를
다루는 3개 문서를 대체 Source of Truth로 사용했다:

- `docs/research/ARTIFACT-DASHBOARD-TRIAL-0001.md` — Notion/Artifact
  기반 "Artifact Dashboard"의 현재 사용 방식(Claude Code가 `/sync`로
  Verified Project State를 만들어 Dashboard가 그 결과만 렌더링하는
  구조)을 기록한 문서.
- `docs/research/ARTIFACT-DASHBOARD-SOURCE-OF-TRUTH-0001.md` — 위
  Artifact Dashboard가 표시해야 할 실제 값을 저장소 기준으로 검증한
  과거 조사(2026-08-15 시점, 이후 구조 변경으로 일부 경로는 stale).
- `docs/research/JARVIS-OS-V2.0-UNIFIED-DASHBOARD-PROTOTYPE-0001.md`
  + `projects/unified-dashboard/` — Notion 설계 노트를 참고해 실제
  코드로 구현된 격리 Prototype.

**결론적으로 저장소에는 서로 다른 두 개의 "Dashboard"가 존재한다**:

| 이름 | 실체 | 데이터 흐름 |
|---|---|---|
| Artifact Dashboard | Notion/Claude Artifact 위에 존재(저장소에 코드 없음) | Repository → Claude Code(수동 `/sync`, 사람이 트리거) → Verified Project State → Artifact(Read-only 렌더링) |
| Unified Dashboard (Prototype) | `projects/unified-dashboard/`에 실제 코드로 존재 | Repository 내 Evidence 파일 → `snapshot.py`(자동, 코드 실행) → HTML(`render.py`) 또는 JSON(`export_snapshot_json.py`) → React Frontend |

이 조사는 이후 전부 **후자(Unified Dashboard Prototype)의 실제 코드**를
근거로 삼는다 — Notion 페이지 원문을 확인하지 못한 채 그 내용을 추정하지
않는다. Notion 페이지 원문 대조가 필요하면 그 내용을 텍스트로 제공받아야
한다(이전 조사 `ARTIFACT-DASHBOARD-SOURCE-OF-TRUTH-0001.md` §13과 동일한
제약).

---

## 1. Dashboard가 요구하는 전체 정보 목록

사용자 지시 §1·§2가 나열한 항목 + 저장소 문서가 실제로 언급하는 항목을
합쳐 12개 범주로 정리한다.

Status, Phase, Current Task, Progress, Metrics, Tasks, Events, Alerts,
Usage/Budget, Execution, History, Agent/Engine

---

## 2~4. HQ별 Backend/Evidence Source 조사

### 범례

- **Fully Exposed**: `snapshot.py`가 이미 읽어 Frontend까지 노출.
- **Partially Exposed**: Source는 있으나 일부만 읽히거나 구조화가 약함.
- **Source 있음, 미노출**: 파일에 데이터가 있으나 `snapshot.py`가 읽지
  않음.
- **Source 없음**: 저장소 어디에도 해당 데이터를 만드는 코드/파일이 없음.

### Development HQ

| 정보 | 상태 | 실제 Source | 노출 여부 |
|---|---|---|---|
| Status | Partially Exposed | `docs/architecture/core/DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` 파일 존재 여부만 확인 → `NORMAL`/`UNKNOWN` 이진 판정(`snapshot.py:63-92` `build_dev_hq_snapshot`) | Fully Exposed(단, 판정 로직 자체가 "파일 존재=NORMAL"이라는 매우 약한 대리 지표) |
| Phase | 구조화 부족 | 없음 — `detail` 리스트의 문자열 하나가 `"Phase: Stable v2.0 Freeze (RFC-0007 -> ... -> CLI)"`로 **코드에 하드코딩된 리터럴**(`snapshot.py:80`), 파일에서 동적으로 읽은 값이 아님 | 노출은 되나 Evidence 기반이 아님(Freeze 완료 시점의 사실을 문자열로 박아 넣은 것) |
| Current Task | Source 없음 | 없음 — `"Current Task: None (idle — 상시 Runtime 없음...)"`도 하드코딩 리터럴(`snapshot.py:84`). Dev HQ는애초에 상시 Runtime이 없어(ADC-02 Open) "현재 Task"라는 개념을 만들 근거 있는 파일이 없음 | 노출되나 Evidence 아님 |
| Progress | Source 없음 | 없음 — Dev HQ MVP 실행은 `hqs/development/mvp/agents/*.py` 함수 호출 1회성이며, 진행률을 기록하는 checkpoint/manifest 구조 자체가 없음(Investment HQ의 `checkpoints/manifest.json`에 대응하는 파일이 Dev HQ에는 없음) | 미노출 |
| Metrics | Partially Exposed | `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` 본문의 `"109 passed"` 같은 회귀 테스트 문자열을 정규식(`_passed_match`)으로 추출(`snapshot.py:73-74`) | Fully Exposed(단, "최근 1회 정적 문서 스냅샷"일 뿐 실시간 테스트 실행 결과 아님) |
| Tasks | Source 없음 | 없음 — MVP-0001~0052는 `docs/01_mvp/` 등 Markdown 보고서로 존재하지만, 각 항목을 "Task(id/status/timestamp)" 구조로 표현하는 파일/API가 없음 | 미노출 |
| Events | Source 없음 | 없음 — `hqs/development/IMPLEMENTATION_RULES.md`가 "Policy/Memory Service/Event Bus 구현 금지"를 명시(§7 근거) | 미노출(구현 자체가 금지됨) |
| Alerts | Source 없음 | 없음 — 위와 동일, Fault/Alert를 구조화해 기록하는 파일 없음 | 미노출 |
| Usage/Budget | Source 없음 | 없음 — `ARTIFACT-DASHBOARD-TRIAL-0001.md` §5가 "5H usage, weekly usage, context percentage 등 실제 API/Runtime 사용량 데이터에 접근할 수단이 없다"고 이미 명시 | 미노출(N/A로 명시 처리 중) |
| Execution | Source 없음 | 없음 — Investment HQ의 `checkpoints/manifest.json`의 `call_log`에 대응하는 파일이 Dev HQ 실행 경로에는 없음(`call_engine()`이 호출별 기록을 남기지 않음) | 미노출(`HQSnapshot.execution=[]` 고정) |
| History | Source 없음 | 없음 — Dev HQ에는 Investment HQ `dogfooding/{prefix}-*` 같은 반복 실행 디렉터리 구조가 없음 | 미노출(`HQSnapshot.history=[]` 고정, `snapshot.py` 주석이 이를 명시) |
| Agent/Engine | Partially Exposed | `hqs/development/mvp/agents/*.py` 파일명 나열(`snapshot.py:76-77`) | Fully Exposed(단, "파일이 존재한다"는 사실뿐 — 각 Agent의 실행 상태·마지막 호출 시각 등은 없음) |

### Investment HQ

| 정보 | 상태 | 실제 Source | 노출 여부 |
|---|---|---|---|
| Status | Partially Exposed | `hqs/investment/dogfooding/{aapl,pg,efa}-trader-verify/` 디렉터리 존재 여부(`snapshot.py:152-198`) | Fully Exposed(단, "실행 기록 디렉터리가 있다"는 대리 지표) |
| Phase | 구조화 부족 | 없음 — 별도 Phase 필드 없이 `detail` 문자열(`"{team}: Analysis/Bull-Bear/Trader {N}단계 완료..."`)에 섞여 있음 | 부분 노출(자유 텍스트, 구조화 안 됨) |
| Current Task | Source 없음 | 없음 — 3개 Team 모두 dogfooding 완료 후 정적 상태이며, "지금 실행 중인 Task"를 나타내는 파일이 없음(Registry/Lifecycle 자체가 미구현) | 미노출 |
| Progress | Partially Exposed | `checkpoints/manifest.json`의 `completed_steps` 배열 길이(`snapshot.py:170`) | Fully Exposed하나 "완료 단계 개수"만 있고 전체 단계 대비 비율(%)은 계산되지 않음 |
| Metrics | Fully Exposed(Execution Evidence Vertical Slice) | `checkpoints/manifest.json`의 `call_log`(`role`, `input_chars`, `output_chars`, `elapsed_sec`) — `hqs/investment/checkpoint.py`의 `Checkpointer`가 기록 | `HQSnapshot.execution`으로 Fully Exposed, Frontend `ExecutionEvidence.tsx`가 표로 렌더링 |
| Tasks | Source 있음, 미노출 | `manifest.json.completed_steps`는 리스트 전체가 존재하지만, `snapshot.py`는 `len(completed_steps)`(개수)만 쓰고 리스트 자체(각 단계 이름)는 버림(`snapshot.py:170,217`) | 부분 미노출(개수는 노출, 개별 항목은 미노출) |
| Events | Source 없음 | 없음 — Investment HQ도 동일하게 Event Bus 구현 금지(`hqs/investment/STRUCTURE.md` "Policy/Memory Service/Event Bus 구현 금지") | 미노출 |
| Alerts | Source 있음, 미노출 | `hqs/investment/checkpoint.py`의 `ContentFailureError`(Result Store 저장 전 검증 실패 시 발생, `BASELINE.md` §16.5 근거) — 예외로만 존재하고 구조화된 Alert 레코드로 저장되지 않음 | 미노출(예외가 발생해도 파일로 남지 않으면 `snapshot.py`가 읽을 대상 자체가 없음) |
| Usage/Budget | Source 없음 | 없음 — Dev HQ와 동일(`ARTIFACT-DASHBOARD-TRIAL-0001.md` §5) | 미노출 |
| Execution | Fully Exposed | 위 Metrics와 동일 Source(`call_log`) | Fully Exposed |
| History | Fully Exposed(History Vertical Slice) | `hqs/investment/dogfooding/{prefix}-*` 전체 run 디렉터리(팀당 3개, 총 9개) 스캔 + 각 run의 `manifest.json`/`trader_decision.md`(`snapshot.py:201-222`) | Fully Exposed, Frontend `HistoryEvidence.tsx`가 표로 렌더링 |
| Agent/Engine | Partially Exposed | `call_log`의 `role` 필드(호출된 역할명)만 존재 — Agent 자체를 나타내는 별도 파일/Registry는 없음(Registry 자체가 미구현, `HANDOVER.md` "Investment HQ 자체" 행) | 부분 노출(역할명 문자열뿐, Agent Identity/상태 없음) |

### Trading HQ

**저장소에 존재하지 않는다.** `hqs/`, `docs/architecture/`, `docs/decisions/`
어디에도 Trading HQ 디렉터리·Baseline·Team Definition 문서가 없다. 유일한
언급은 `JARVIS-OS-V2.0-COMMAND-CONTRACT-PROTOTYPE-0001.md`와
`JARVIS-OS-V2.0-DEV-HQ-VERTICAL-SLICE-PROTOTYPE-0001.md`가 Command
Prototype의 **"알 수 없는 HQ" 테스트 케이스**로 `"Trading HQ 상태를
보여줘"` → `reason=unknown_hq`를 검증한 것뿐이다(실제 HQ 구현이 아니라
"모르는 입력을 안전하게 거부하는지"를 확인하기 위한 가상의 이름).

**결론**: Trading HQ의 12개 정보 범주는 전부 **Source 없음**이다 — 이는
"구현이 부족하다"가 아니라 **HQ 자체가 아직 개념적으로도 존재하지
않는다**는 뜻이다. `JARVIS-OS-V2.0-UNIFIED-DASHBOARD-PROTOTYPE-0001.md`
§12가 이미 "Trading HQ가 실제로 생기면 3-HQ 표본으로 재검증"을 다음
Prototype 후보로 남겨 두었을 뿐, 그 조건(Trading HQ 등장)이 아직
충족되지 않았다.

---

## 5. 구조화 부족 / Backend 구현 부족 / Evidence 부족 구분

| 구분 | 의미 | 해당 항목 |
|---|---|---|
| **구조화 부족** | Evidence 파일에 데이터가 이미 있으나 구조가 약해(자유 텍스트 혼재, 리스트 대신 개수만) 그대로 쓰기 어려움 | Investment HQ Phase(자유 텍스트), Investment HQ Tasks(개수만 추출, 개별 항목 버림) |
| **Backend 구현 부족** | 데이터를 만드는 실행 코드 자체가 그 형태로 기록하지 않음(파일을 만들지 않음) | Dev HQ Progress/Tasks/Execution/History(대응하는 checkpoint/manifest 구조 자체가 없음), Investment HQ Alerts(예외는 발생하나 파일로 영속화 안 됨), Dev HQ Current Task/Phase(하드코딩 리터럴로 대체됨 — 실제로 상태를 계산하는 코드가 없음) |
| **Evidence 부족(Kernel/Governance 미결)** | 코드를 당장 짜더라도 그 책임이 어느 계층(Kernel/HQ/Engine) 소속인지 자체가 미결이라 구현 착수가 금지됨 | Events/Alerts(구조화된 형태) — §16.6 Workflow/Memory/Event Bus Defer, ADC-05(Fault Event 배달 보장) Open, ADC-08(Task/Event Flow 배달 보장 차등화) Open. Usage/Budget — ADC-07(Resource/Token 예산 이중 소속) Open |

---

## 6. 데이터 자체가 없는 항목 — 책임 계층 조사

| 정보 | 현재 어느 계층 책임인가(BASELINE.md 기준) | 근거 |
|---|---|---|
| Events(구조화된 Fault/State Event) | **미결(Open)** — Kernel Module로 다룰지 자체가 결정되지 않음 | `BASELINE.md` §16.6 "Workflow, Memory, Event Bus는 Kernel Module 후보로 검토됐으나 Defer"; `docs/decisions/adc/ADC.md` ADC-05, ADC-08 Open |
| Alerts | **미결(Open)** | 위와 동일 + `hqs/investment/checkpoint.py`의 `ContentFailureError`는 §16.5(Multi-Task Result Store 저장 전 검증 게이트)의 봉쇄 책임일 뿐, "Alert를 사용자에게 통지"하는 책임은 어디에도 Accept되지 않음 |
| Usage/Budget(Token/API 사용량) | **미결(Open)** | `docs/decisions/adc/ADC.md` ADC-07 "Resource(Token 예산) 이중 소속" Open — Kernel 소속인지 Engine Adapter 소속인지조차 결정 안 됨 |
| Dev HQ Progress/Tasks/Execution/History | **Development HQ(HQ 내부) 책임** — Kernel이 아니라 HQ가 스스로 결정할 수 있는 구현 선택 | `hqs/investment/checkpoint.py`의 `Checkpointer`/`run_step` 패턴이 이미 §16.5에서 Kernel 수준으로 Accept됐으므로, Dev HQ가 동일 패턴을 채택하는 것은 새 Architecture Decision 없이도 가능(§16.5 "Development HQ를 포함한 다른 HQ에 동일한 컴포넌트를 새로 만들 것을 요구하지 않는다"는 문구는 "만들면 안 된다"가 아니라 "강제하지 않는다"는 뜻) |
| Trading HQ 전체 | **아직 계층 자체가 없음** | HQ가 존재해야 그 아래 Team/Agent/Registry 책임 분배가 의미를 가짐(Meta Architecture `Jarvis OS → HQ → Agent → Connector`) — Trading HQ가 문서 수준으로도 정의되지 않았으므로 이 질문 자체가 아직 성립하지 않음 |

---

## 7. RFC/ADC/ADR 필요 여부

**새로운 Architecture Decision을 지금 열 것을 권고하지 않는다.** 이유:

1. Events/Alerts/Usage-Budget은 이미 각각 ADC-05/08/07로 **Open 상태로
   존재**한다 — 새 RFC를 여는 대신 기존 Open ADC의 재검토 조건(실제
   반복 관찰)이 충족되는지를 먼저 봐야 한다. `docs/architecture/core/`
   Governance Chain 전체가 반복 확인한 원칙(Rule B: 3건 이상 독립
   관찰, 또는 ADC-0016 수준의 실제 merge된 코드 1건)에 따르면, 이번
   조사는 "Dashboard가 이 데이터를 보여주고 싶다"는 **요구**만
   확인했을 뿐 "실제로 필요해서 막힌 사건"을 확인하지 못했다 —
   ADC-0018이 Multi-HQ Task 분해를 Defer한 것과 정확히 같은 논리
   구조다.
2. Dev HQ Progress/Tasks/Execution/History는 Kernel Governance 대상이
   아니라 **HQ 내부 구현 선택**이다 — §16.5가 이미 "필요한 곳에서는
   같은 패턴(Checkpointer)을 다시 만들어도 된다"는 여지를 열어
   두었으므로, RFC 없이 Dev HQ 자체 판단(및 `IMPLEMENTATION_RULES.md`
   금지 목록 재확인)으로 구현 착수가 가능하다.
3. Trading HQ는 HQ 자체가 없으므로 "Dashboard가 그 데이터를 어떻게
   보여줄까"를 논할 근거 자체가 없다 — RFC를 열 대상이 아니다.

---

## 8. 종합 표

| Dashboard 정보 | 실제 Source | 현재 노출 | 구현 가능 여부 | Architecture/Governance 필요 여부 | 다음 단계 |
|---|---|---|---|---|---|
| Dev HQ Status | `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` 존재 여부 | Fully Exposed | 가능(대리 지표 개선만 필요) | 불필요 | 판정 로직을 "파일 존재"보다 정밀하게(예: 최신 회귀 테스트 통과 여부) 개선 검토 |
| Dev HQ Phase/Current Task | 없음(하드코딩 리터럴) | 노출(비-Evidence) | 가능(HQ 내부 구현) | 불필요 | Freeze 문서에 구조화된 Phase 필드를 추가하거나, 리터럴임을 문서/코드에 명시 유지 |
| Dev HQ Progress/Tasks/Execution/History | 없음 | 미노출 | 가능(§16.5 패턴 재사용, HQ 내부 선택) | 불필요(단, 실제 도입 전 §16.5 조건 재확인) | Dev HQ에 Investment HQ `Checkpointer` 수준의 실행 기록 구조 도입 여부를 Dev HQ 팀이 결정 |
| Dev HQ Metrics | `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` 정규식 추출 | Fully Exposed | 가능 | 불필요 | 정적 문서 대신 실제 pytest 실행 결과를 읽는 방식 검토(단, `call_engine()`/subprocess 확장은 Boundary Review 대상) |
| Dev HQ Agent/Engine | `hqs/development/mvp/agents/*.py` 파일명 | Partially Exposed | 가능 | 불필요 | 파일명 나열 이상(실행 이력)이 필요하면 §16.5 패턴과 함께 검토 |
| Investment HQ Status/Progress | `checkpoints/manifest.json` | Fully Exposed | 이미 구현됨 | 불필요 | 비율(%) 계산 등 표현 개선만 검토 |
| Investment HQ Phase/Tasks(개별) | `manifest.json.completed_steps` | 구조화 부족(개수만) | 가능(이미 있는 리스트를 그대로 넘기면 됨) | 불필요 | `snapshot.py`가 `completed_steps` 리스트 전체를 노출하도록 확장(Boundary 위반 없음 — 이미 읽는 파일) |
| Investment HQ Metrics/Execution | `checkpoints/manifest.json.call_log` | 이미 구현됨(Execution Evidence Vertical Slice) | 이미 구현됨 | 불필요 | 없음(추가 확장 시에도 §16.5 범위 유지) |
| Investment HQ Alerts | `ContentFailureError`(예외, 미영속화) | Source 있음, 미노출 | 부분 가능 — 예외를 파일로 영속화하는 코드가 먼저 필요(HQ 내부 구현) | **필요 여부 판단 대상**: "예외를 구조화된 Alert로 승격"이 §16.5 범위를 넘는지 확인 필요 | 실제로 `ContentFailureError`가 반복 발생하는지 먼저 관찰(현재 Evidence는 §16.5 근거였던 과거 4회뿐) — 반복되면 HQ 내부에서 로그 파일화, Kernel 수준 Alert 개념은 그 다음 |
| Investment HQ History | `dogfooding/{prefix}-*` 9개 run | 이미 구현됨(History Vertical Slice) | 이미 구현됨 | 불필요 | 없음 |
| Events(전 HQ 공통) | 없음 | 미노출 | **불가능**(Kernel 미결) | **필요** — 단, 지금 RFC를 여는 것은 시기상조(§7) | 실제 반복 필요 사례 관찰 대기(ADC-05/08 재검토 조건) |
| Usage/Budget(전 HQ 공통) | 없음(API/Runtime 사용량 접근 수단 자체 없음) | 미노출(N/A로 명시 처리 중, `ARTIFACT-DASHBOARD-TRIAL-0001.md`) | **불가능**(Kernel 미결 + 접근 수단 자체 없음) | **필요** — 단, 지금 RFC를 여는 것은 시기상조(§7) | 접근 수단(API) 자체가 생기기 전까지 N/A 유지가 정답 |
| Trading HQ 전체 | 없음 | 미노출 | 불가능(HQ 자체 미존재) | Trading HQ 등장 자체가 먼저 RFC/ADC 대상(Investment HQ와 동일 절차) | Trading HQ 개념이 실제로 필요해지기 전까지 보류 |

---

## 9. Backend 구현 우선순위 제안(Evidence 기반)

Governance 원칙(가상 미래 요구사항 대비 설계 금지, 실제 관찰된 필요만
착수)에 따라, **이미 Source가 존재하고 Boundary Review를 새로 통과할
필요가 없는 항목**을 우선한다.

1. **Investment HQ Tasks(개별 completed_steps 노출)** — 이미 읽고 있는
   `manifest.json`의 리스트를 그대로 넘기기만 하면 된다(신규 파일 접근
   없음, Boundary 확장 없음). 비용 최소·Evidence 최다.
2. **Investment HQ Progress 비율(%) 계산** — 역시 이미 있는 `completed_steps`
   길이를 총 단계 수(4-Wave 패턴, `hqs/investment/STRUCTURE.md`가 문서화)로
   나누기만 하면 된다.
3. **Investment HQ Alert 영속화 여부 재관찰** — 코드를 먼저 짜지 말고,
   다음 dogfooding에서 `ContentFailureError`가 다시 발생하는지 `EVIDENCE.md`에
   기록하는 관행부터 시작(ADC-0017 Risks 절이 이미 권고한 방식과 동일).
4. **Dev HQ 실행 기록 구조 도입 여부 결정** — Investment HQ의
   `Checkpointer` 패턴을 재사용할지 Dev HQ 팀이 먼저 결정해야 Progress/
   Tasks/Execution/History가 채워진다. 코드 작성보다 **결정**이 먼저다.
5. **Events/Alerts/Usage-Budget 신규 구현은 보류** — Kernel 수준 Open
   Decision(ADC-05/07/08)이 남아 있는 한 Dashboard가 먼저 나서서
   구조를 만들면 나중에 Kernel 결정과 충돌할 위험이 있다. Dashboard는
   계속 "없음"을 정직하게 표시한다(`ARTIFACT-DASHBOARD-TRIAL-0001.md`
   §5의 N/A 원칙과 동일).
6. **Trading HQ 대응은 미착수** — HQ 자체가 생기기 전까지 Dashboard
   쪽에서 할 일이 없다.

---

## Self Review

- [x] Notion 원문 미접근을 명시하고, 대체 Source(저장소 문서)로만
      판단했음을 표기했다.
- [x] Development HQ / Investment HQ를 모든 표에서 분리했다.
- [x] Trading HQ는 "미존재"를 사실대로 기록했고 가상 구현을 제안하지
      않았다.
- [x] "구조화 부족/Backend 구현 부족/Evidence 부족"을 §5에서 명확히
      구분했다.
- [x] 데이터가 없는 항목에 대해 Frontend 임의 구현을 제안하지 않고
      책임 계층만 조사했다(§6).
- [x] 기존 RFC/ADC/ADR(§16.3~16.6, ADC-05/07/08/0018)과 대조해 이미
      결정된 것과 미결인 것을 구분했다(§6~§7).
- [x] 새 RFC/ADC/ADR 착수를 제안하지 않고 필요 여부·근거만 기록했다(§7).
- [x] Production Code(`hqs/*`, `core/`, `projects/unified-dashboard/*.py`)와
      Frontend를 수정하지 않았다(읽기만 수행).
- [x] 최종 표(§8)와 Evidence 기반 우선순위(§9)를 제공했다.

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음(read-only 조사)
Frontend Change: 없음
Tests: 실행하지 않음(코드 변경이 없어 회귀 검증 대상 없음)
RFC: 없음(§7 — 필요 여부만 기록, 착수 권고 없음)
ADC: 없음
ADR: 없음
PR: 불필요(READ-ONLY Audit, CLAUDE.md PR Creation Criteria)
Branch: `claude/dashboard-backend-inventory-dqa8t7`
