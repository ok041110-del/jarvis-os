# Dev HQ Command Center — UI Prototype v0.1

**Summary**

- `projects/dashboard-shell-mvp/`(Experimental Prototype) 안의 독립된
  하위 Prototype이다 — 기존 `index.html`/`app.js`/`render.js`/`data.js`는
  전혀 수정하지 않았다(regression 없음, 14 passed 유지).
- "VS Code Workspace + AI Agent Control Center + Jarvis Evidence Layer"
  UX를 검증하는 화면이며, 새 Runtime/Orchestrator/Scheduler/Workflow
  Engine은 구현하지 않았다.
- Task(#042 등)를 선택하면 Chat/Overview/Plan/Activity/Code/Terminal/
  Changes/Tests/Evidence/Report 탭이 모두 같은 Task를 바라본다.
- 모든 데이터는 `data/mock/*.json`의 Mock Data이고, UI는 이를 직접
  읽지 않는다 — `data/adapters/adapters.js`(Data Adapter)만 거친다.
  화면에는 `MOCK` 배지가 붙어 실제 Evidence로 오인되지 않는다.
- **Progress ≠ Success**를 데이터 모델 수준에서 분리했다 — Task
  `#040`은 Progress 46%에 `FAILED`, `#043`(Chat으로 즉석 생성한
  Task)은 Progress 0%에 `WAITING`이다.

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
| `data/adapters/adapters.js` | **Data Adapter** — UI가 유일하게 호출하는 데이터 접근 지점. 지금은 `data/mock/*.json`을 fetch하지만, 실제 연결 시 이 파일의 함수 내부만 교체하면 된다(UI/렌더 변경 불필요) |
| `data/mock/*.json` | Task/Conversation/Activity/Changes/Tests/Evidence/Terminal/File Tree Mock Fixture. 각 파일에 `_source: "mock"` 명시 |

## Task Lifecycle / State

`CREATED → PLANNING → RUNNING → VERIFYING → COMPLETED`(예외:
`FAILED`/`CANCELLED`/`BLOCKED`)를 Mock Task의 `status` 필드로 표현한다.
Progress(%)와 Status는 항상 독립된 필드다 — Progress 100%가 자동으로
`SUCCESS`/`COMPLETED`를 의미하지 않는다(Task `#040` 참조).

## Mock Data Architecture

```
UI (render.js / app.js)
  ↓ (직접 참조하지 않음)
data/adapters/adapters.js   ← UI가 호출하는 유일한 지점
  ↓
data/mock/*.json            ← 지금은 이것만 존재
  ↓ (교체 지점)
실제 Dev HQ Task/Evidence 데이터 소스
```

Chat에서 알려진 Task 제목과 일치하지 않는 입력을 보내면, Adapter가
세션 메모리에만 존재하는 새 Mock Task(`WAITING`, Progress 0%)를 만든다
— 실제 Task Runtime이 시작된 것처럼 보이는 문구를 쓰지 않는다
(`_synthetic: true`로 표시, 새로고침하면 사라짐).

## Boundary — 이번 Prototype이 구현하지 않은 것

- Task Runtime, Conversation Runtime, Agent Orchestrator, Scheduler,
  Registry, Workflow Parser/Engine, Engine Gateway, Policy Layer,
  Memory Service, Event Bus, 신규 Agent/Capability, 신규 LLM
  Gateway/OpenRouter Client.
- 실제 `git status`/`git diff`, 실제 pytest 결과 파싱, 실제 shell
  execution(Terminal은 입력을 echo만 한다) — 전부 P1/P2 후보로
  남겨둔다. Adapter 구조는 이 교체를 가로막지 않는다.
- Production `dashboard/`는 이 Prototype과 무관하며 건드리지 않았다.

## 검증

- `python3 -m pytest projects/dashboard-shell-mvp/tests -q` — 14 passed
  (기존 Dashboard Shell 테스트, regression 없음, 이 Prototype은 별도
  테스트를 추가하지 않았다 — Python 코드가 없다).
- 모든 `data/mock/*.json`을 `python3 -m json.tool`로 syntax 검증
  — 8개 파일 전부 OK.
- Playwright(Chromium)로 UI Smoke/Interaction Test 수행: Task #042
  로드 → 전체 탭(Plan/Activity/Code/Terminal/Changes/Tests/Evidence/
  Report/Chat) 렌더링 → Editor 파일 열기 → Changes Diff 선택 →
  Terminal 명령 echo → Report Copy All → Conversation 목록에서
  Task #041로 전환 → Chat으로 새 Task(#043) 생성까지 전 구간 콘솔
  에러 없이 통과.
