# Dev HQ Command Center — UI Prototype v0.1 + Real Data Adapter v0.1

**Summary**

- `projects/dashboard-shell-mvp/`(Experimental Prototype) 안의 독립된
  하위 Prototype이다 — 기존 `index.html`/`js/app.js`/`js/render.js`/
  `data.js`(Dashboard Shell 최상위)는 수정하지 않았다(regression 없음).
- "VS Code Workspace + AI Agent Control Center + Jarvis Evidence Layer"
  UX를 검증하는 화면이며, 새 Runtime/Orchestrator/Scheduler/Workflow
  Engine/서버 API는 구현하지 않았다.
- Task(#042 등)를 선택하면 Chat/Overview/Plan/Activity/Code/Terminal/
  Changes/Tests/Evidence/Report 탭이 모두 같은 Task를 바라본다.
- 데이터는 `data/adapters/adapters.js`(Data Adapter)만 거쳐 읽는다 —
  UI는 Mock/Real JSON을 직접 참조하지 않는다. 화면에는 실제 사용된
  출처에 따라 `MOCK`/`REAL`/`UNAVAILABLE` 배지가 붙는다.
- **Progress ≠ Success**를 데이터 모델 수준에서 분리했다 — Task
  `#040`은 Progress 46%에 `FAILED`, `#043`(Chat으로 즉석 생성한
  Task)은 Progress 0%에 `WAITING`이다.

## Real Data Adapter v0.1 — 무엇이 실제로 연결됐는가

조사 결과(`hqs/development/workflow.py`가 영속 저장소 없이 on-demand로만
실행됨 확인) Task ID(#039~042 등)에 대응하는 실제 실행 기록은 존재하지
않는다 — 그래서 Task 종속 데이터(Changes/Tests/Evidence)는 이번 단계에서
연결 대상이 아니다(Mock 그대로 유지). 대신 Task와 무관한 저장소 전역
상태를 연결했다.

| 영역 | Adapter 함수 | 상태 |
|---|---|---|
| Repository File Tree | `getFileTree()` | **REAL** — 실제 저장소 구조(`hqs/development`, `projects/dashboard-shell-mvp`, `docs/architecture`, `docs/decisions`) |
| File Content | `getFileContent()` | **REAL** — `projects/dashboard-shell-mvp/*`는 기존 정적 서버가 직접 서빙, 그 외는 export 스냅샷에서 로드. 둘 다 없으면 Mock Tree 대응 fallback(회귀 방지), 최종 실패 시 `unavailable` |
| Git Branch/Status | `getRepoStatus()`(신규) | **REAL** — 실제 `git status`/`git diff` 스냅샷 |
| Dev HQ Workflow 상태 | `getWorkflowStatus()`(신규) | **REAL** — 기존 `unified-dashboard/snapshot.py::build_dev_hq_snapshot()` 재사용(재구현 없음) |
| Task별 Changes/Tests/Evidence/Activity/Terminal/Conversations/Task 목록 | 기존 함수 | **MOCK 유지** — Task 종속 실제 실행 기록 없음(무변경) |

**연결 방식 — 새 서버 API 없음**: `data/real/export_real_snapshot.py`를
수동 실행하면(`unified-dashboard/export_snapshot_json.py`와 동일 패턴)
`data/real/*.json` + `data/real/content/*.json`을 생성한다. `adapters.js`는
이 정적 파일을 fetch만 한다 — `serve_dashboard.py`는 무수정, 새 Runtime/
Scheduler 없음.

```text
python3 data/real/export_real_snapshot.py

실행 후 생성된 data/real/*.json을 Command Center가 읽는다.
Snapshot은 실행 시점 기준이며 실시간 데이터가 아니다.
```

`data/real/*.json`(및 `data/real/content/*.json`)은 실행 시점 스냅샷인
generated artifact이므로 Git에 커밋하지 않는다(`.gitignore`에 명시,
`export_real_snapshot.py` 자체는 ignore 대상이 아니다). Snapshot이 없는
상태에서도 Prototype은 깨지지 않는다 — 이 경우 Adapter가 해당 데이터를
`source: "unavailable"`으로 반환한다(Mock을 Real로 위장하지 않는다).

## 실행

```
python3 projects/dashboard-shell-mvp/serve_dashboard.py
```

브라우저에서 `http://localhost:8765/devhq-command-center/index.html`
(또는 출력된 포트 번호로 접속). 기존 Dashboard Shell(`index.html`)의
`../css/dashboard.css` 토큰(`--bg`/`--panel`/`--accent` 등)을 그대로
재사용한다 — 별도 서버 경로 추가 없이 정적 파일로만 동작한다.

## 구조

| 경로 | 책임 |
|---|---|
| `index.html` | Topbar / Sidebar / Workspace(Task Header+Tabs) / Inspector / Statusbar 골격 |
| `css/command-center.css` | Dark IDE 스타일 Grid 레이아웃, 기존 `dashboard.css` 토큰 재사용 |
| `js/render.js` | 데이터를 입력받아 DOM 문자열을 만드는 순수 렌더 함수. Mock 여부를 모른다 — Adapter가 넘긴 `source`만 보고 배지를 붙인다 |
| `js/app.js` | 상태(activeTaskId/activeTab/editor/chat 등) 보관 + 이벤트 처리 + Adapter 호출 오케스트레이션 |
| `data/adapters/adapters.js` | **Data Adapter** — UI가 유일하게 호출하는 데이터 접근 지점. File Tree/Content/Git/Workflow는 `data/real/*.json`을 우선 시도하고, Task 종속 데이터(Changes/Tests/Evidence 등)는 `data/mock/*.json`을 그대로 쓴다 |
| `data/mock/*.json` | Task/Conversation/Activity/Changes/Tests/Evidence/Terminal Mock Fixture. 각 파일에 `_source: "mock"` 명시 |
| `data/real/export_real_snapshot.py` | Real Data Snapshot Exporter(수동 실행, 새 서버 API 없음) — 실제 File Tree/Git/Dev HQ Workflow 상태/기존 테스트 결과를 `data/real/*.json`으로 내보낸다 |

## Task Lifecycle / State

`CREATED → PLANNING → RUNNING → VERIFYING → COMPLETED`(예외:
`FAILED`/`CANCELLED`/`BLOCKED`)를 Mock Task의 `status` 필드로 표현한다.
Progress(%)와 Status는 항상 독립된 필드다 — Progress 100%가 자동으로
`SUCCESS`/`COMPLETED`를 의미하지 않는다(Task `#040` 참조).

## Data Architecture

```
UI (render.js / app.js)
  ↓ (직접 참조하지 않음)
data/adapters/adapters.js   ← UI가 호출하는 유일한 지점
  ↓                    ↓
data/real/*.json     data/mock/*.json
(File Tree/Content/   (Task/Conversation/Activity/
 Git/Workflow)         Changes/Tests/Evidence/Terminal)
  ↑
export_real_snapshot.py(수동 실행) ← 실제 저장소(git/파일시스템/
                                      build_dev_hq_snapshot())
```

Chat에서 알려진 Task 제목과 일치하지 않는 입력을 보내면, Adapter가
세션 메모리에만 존재하는 새 Mock Task(`WAITING`, Progress 0%)를 만든다
— 실제 Task Runtime이 시작된 것처럼 보이는 문구를 쓰지 않는다
(`_synthetic: true`로 표시, 새로고침하면 사라짐).

## Boundary — 이번 Prototype이 구현하지 않은 것

- Task Runtime, Conversation Runtime, Agent Orchestrator, Scheduler,
  Registry, Workflow Parser/Engine, Engine Gateway, Policy Layer,
  Memory Service, Event Bus, 신규 Agent/Capability, 신규 LLM
  Gateway/OpenRouter Client, 새 서버 API(`serve_dashboard.py` 무수정).
- Task별 실행 기록(Changes/Tests/Evidence per task) — `workflow.py`가
  영속 저장소 없이 on-demand로만 실행되어 Task ID(#039~042 등)에
  대응하는 실제 기록이 존재하지 않는다(조사로 확인, Real Data Adapter
  v0.1 범위 밖으로 명시적으로 남겨둠).
- 실제 shell execution(Terminal은 입력을 echo만 한다) — P2 후보로
  남겨둔다.
- Production `dashboard/`는 이 Prototype과 무관하며 건드리지 않았다.

## 검증

- `python3 -m pytest projects/dashboard-shell-mvp/tests hqs/development/mvp/tests -q`
  — 370 passed, 6 skipped(회귀 없음, Real Data Adapter 코드는 JS/Python
  스크립트뿐이라 이 Prototype 자체의 신규 Python 테스트는 없음).
- 모든 `data/mock/*.json` + `data/real/*.json`(+ `data/real/content/*.json`
  211개)을 `python3 -m json.tool`로 syntax 검증 — 전부 OK.
- `node --check`로 `adapters.js`/`app.js`/`render.js` 문법 검증 — 전부 OK.
- `python3 -m py_compile`로 `export_real_snapshot.py` 문법 검증 — OK.
- Playwright(Chromium)로 Real Data Adapter 포함 UI Smoke Test 수행:
  Sidebar Repository 블록에 실제 Branch/변경 파일 수/Dev HQ Workflow
  Phase 표시(REAL 배지) → Explorer가 실제 저장소 구조 표시(REAL 배지)
  → Code 탭에서 실제 `hqs/development/HANDOVER.md`(export 스냅샷 경유)
  및 `projects/dashboard-shell-mvp/serve_dashboard.py`(기존 정적 서버
  직접 fetch) 내용이 실제로 렌더링됨(REAL 배지, 실제 파일 텍스트 확인)
  → Terminal/Changes/Tests/Evidence/Report 탭 정상 렌더(Changes/Tests는
  의도대로 MOCK 배지 유지) → Task #041로 전환 → Chat으로 새 Task 생성
  까지 전 구간 콘솔 에러 없이 통과.
  — 8개 파일 전부 OK.
- Playwright(Chromium)로 UI Smoke/Interaction Test 수행: Task #042
  로드 → 전체 탭(Plan/Activity/Code/Terminal/Changes/Tests/Evidence/
  Report/Chat) 렌더링 → Editor 파일 열기 → Changes Diff 선택 →
  Terminal 명령 echo → Report Copy All → Conversation 목록에서
  Task #041로 전환 → Chat으로 새 Task(#043) 생성까지 전 구간 콘솔
  에러 없이 통과.
