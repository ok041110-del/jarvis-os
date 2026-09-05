# Dashboard Shell MVP — Experimental Prototype

**성격**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 "Experimental
Implementation" 절이 허용하는 격리 Prototype. Formal Architecture
Decision이 아니다. Production `dashboard/`(Structure v1.0 Frozen 위치,
`docs/architecture/baseline/STRUCTURE-V1.0-FROZEN.md`)에 구현하지
않는다 — 그 위치의 실제 구현 구조는 여전히 Deferred Decision이다.

**목적**: "Global Dashboard가 Navigation에 따라 Main Content를 reload
없이 동적으로 전환하고, Mock Data 변경이 실제로 UI 재렌더링을
유발하는 Shell 구조"를 실제 브라우저에서 검증한다. Production
Dashboard 완성이 목적이 아니다 — 기존 `projects/unified-dashboard/`
(실제 Evidence 파일 기반 정적 스냅샷)와 목적이 다르다: 이 Prototype은
순수 Mock Data와 client-side 동적 상태 전환 자체를 검증 대상으로
삼는다.

Development/Investment HQ Evidence 표시와 Chat → Command Resolution
연결만 예외다 — 아래 두 절 참조.

## 실행

가장 간단한 방법:

```
python3 projects/dashboard-shell-mvp/serve_dashboard.py
```

실행하면 접속할 Dashboard URL(기본 `http://localhost:8765/index.html`)을
바로 출력한다 — 그 주소를 브라우저에서 열면 된다. 8765번 포트가 이미
사용 중이면 자동으로 다음 포트를 찾아 알려준다. 표준 라이브러리
(`http.server`)만 쓰고, 실행 자체가 Dashboard 코드(`index.html`/
`css`/`js`)를 건드리지 않는다 — 개발 편의용 실행 스크립트일 뿐이다.

Evidence Snapshot을 먼저 최신화하려면(선택):

```
python3 projects/dashboard-shell-mvp/generate_development_snapshot.py
python3 projects/dashboard-shell-mvp/generate_investment_snapshot.py
```

수동으로 직접 서버를 띄우고 싶다면 기존 방식도 Evidence 표시는 그대로
동작한다 — 단 **Chat → Command Resolution은 `serve_dashboard.py`로만
동작한다**(아래 참조, `python3 -m http.server`는 `POST /api/command`를
지원하지 않아 `501 Not Implemented`를 반환한다):

```
cd projects/dashboard-shell-mvp
python3 -m http.server 8765
```

두 방법 모두 `http://localhost:8765` 접속. **`index.html`을 직접
더블클릭해서 여는 방식은 더 이상 완전히 동작하지 않는다** — Development/
Investment 탭이 각각 `fetch()`로 `data/development-snapshot.json`/
`data/investment-snapshot.json`을 읽는데, `file://` 프로토콜에서는 이
요청이 CORS로 차단된다(Trading/Header/Chat은 여전히 순수 Mock이라
더블클릭으로도 동작). 이 경우에도 Mock로 조용히 대체되지 않고 해당
HQ 화면에 "Evidence 연결 실패"가 그대로 표시된다 — 반드시 위
`http.server`로 접속해야 한다.

## 구조

| 파일 | 책임 |
|---|---|
| `index.html` | Header / Nav / Main / Chat 4개 영역의 정적 骨格만 정의 |
| `css/dashboard.css` | Dark Professional Dashboard 스타일, CSS Grid 레이아웃, Responsive 대응 |
| `js/data.js` | 데이터 조회 단일 지점(`get*`). Trading은 Mock 객체, `getHQSnapshot('development'\|'investment')`는 `EVIDENCE_SNAPSHOT_FILES`에 매핑된 JSON을 `fetch()`한다. `runCommand(rawInput)`은 `POST /api/command`를 호출한다 |
| `js/render.js` | 데이터를 입력받아 DOM 문자열을 만드는 순수 렌더 함수. Mock/Evidence 여부를 모른다. `errorPanel`은 fetch 실패를 명시적으로 표시한다 |
| `js/app.js` | 상태(activeHQ/messages) 보관 + 이벤트 처리 + 부분 렌더링 오케스트레이션. Navigation 선택을 `location.hash`와 동기화(새로고침/뒤로가기·앞으로가기에서도 선택된 HQ 유지). `renderMain()`은 동기 Mock 반환값과 fetch Promise를 모두 처리한다. Chat 제출 시 `runCommand()`를 호출하고 결과를 그대로 표시한다 |
| `generate_development_snapshot.py` | `projects/unified-dashboard/snapshot.py`의 `build_dev_hq_snapshot()`을 재사용해 `data/development-snapshot.json`을 생성하는 CLI |
| `generate_investment_snapshot.py` | 같은 `snapshot.py`의 `build_investment_hq_snapshot()`을 재사용해 `data/investment-snapshot.json`을 생성하는 CLI |
| `data/development-snapshot.json`, `data/investment-snapshot.json` | 생성된 Evidence Snapshot(커밋 대상 — `unified-dashboard`의 `output/`·`frontend/public/data/` 선례와 동일) |
| `serve_dashboard.py` | 로컬 실행 편의 스크립트 — 클릭 한 번으로 열어볼 수 있게 서버를 띄우고 접속 URL을 출력한다. `POST /api/command`만 예외로, `projects/command-contract/resolver.py`의 `parse_command()`/`resolve()`를 그대로 호출해 중계한다(로직 복제 없음) |

## Development/Investment HQ Evidence 연결 (실험)

Development·Investment HQ 탭은 Mock Data 대신 실제 Evidence 기반
Snapshot을 표시한다(둘 다 같은 방식):

```
raw fetch("data/development-snapshot.json")
  ← generate_development_snapshot.py
  ← projects/unified-dashboard/snapshot.py의 build_dev_hq_snapshot()
    (DEVELOPMENT-HQ-V2.0-FREEZE-0001.md, hqs/development/mvp/agents/*.py만 읽음)

raw fetch("data/investment-snapshot.json")
  ← generate_investment_snapshot.py
  ← projects/unified-dashboard/snapshot.py의 build_investment_hq_snapshot()
    (hqs/investment/dogfooding/*-trader-verify의 checkpoints/manifest.json·
    trader_decision.md만 읽음)
```

- 새 Evidence 수집 로직을 만들지 않았다 — `unified-dashboard`가 이미
  검증한 `build_dev_hq_snapshot()`/`build_investment_hq_snapshot()`을
  그대로 import해서 재사용한다(`tests/test_generate_*_snapshot.py`가
  각각 같은 함수 객체인지 검증).
- `progressPercent`는 항상 `null`이다 — Development HQ에는 진행률(%)
  Evidence 자체가 없다(상시 Runtime 없음, ADC-02 Open). Mock이 쓰던
  58%~ 같은 숫자를 지어내지 않고, 화면에 "Evidence 없음"을 그대로
  드러낸다.
- Investment HQ의 팀별 `status`/`lastDecision`은 대표 run
  (`_TEAM_RUNS`, trader-verify 계열) 1개의 완료 단계 수·Trader
  Decision을 그대로 옮긴 것이다 — Mock이 쓰던 "Promoted" 같은 조직
  상태는 이 Evidence 파이프라인이 읽는 범위 밖이라 지어내지 않고
  뺐다. 대표 run이 없는 팀은 "UNKNOWN(실행 기록 없음)"을 그대로
  노출한다.
- `deferred`는 `build_investment_hq_snapshot()`이 이미 만든 값
  (`["Portfolio", "Risk", "Execution (Trade Execution)"]`)을 그대로
  쓴다 — render.js가 각 항목 뒤에 "(Deferred)"를 붙이는 기존 방식은
  그대로 둬서 "Execution (Trade Execution) (Deferred)"처럼 다소
  중복된 표현이 나온다(내용은 정확하다 — 표현만 다음 정리 대상).
- fetch가 실패하면(파일 없음/서버 미기동/JSON 손상) Mock으로 조용히
  대체하지 않는다 — `Render.errorPanel`이 실패 원인(HTTP 상태/예외
  메시지)을 그대로 표시한다.
- Trading/Header/Mock Refresh는 전혀 변경되지 않았다 — 여전히 100%
  Mock이다. Chat은 아래 "Chat → Command Resolution 연결" 절 범위에서
  예외다(LLM/Engine은 여전히 미연결).

## Chat → Command Resolution 연결 (실험)

Dashboard Chat에 입력한 문장은 그대로 기존 `projects/command-
contract/` Prototype의 `resolver.py`로 전달된다 — 새 Command Layer를
만들지 않았다:

```
Chat 입력(raw_input)
  → fetch("/api/command")                              [js/data.js: runCommand]
  → serve_dashboard.py의 POST /api/command 핸들러       [로직 없음, 그대로 중계]
  → projects/command-contract/resolver.py
      parse_command(raw_input) → Command(intent, target_hq)
      resolve(command) → CommandResult
        ← projects/unified-dashboard/snapshot.py의
          build_dev_hq_snapshot() / build_investment_hq_snapshot()
  → Chat에 intent/target_hq/status/hq_identity/detail 그대로 표시
```

- `command.py`/`resolver.py`/`task_case.py`는 전혀 수정하지 않았다 —
  이미 검증된 Case A(Command → HQ Target → Snapshot, Task 없음) 경로를
  그대로 재사용한다. `serve_dashboard.py`는 이 두 함수를 호출만 하고
  로직을 복제하지 않는다.
- Trading은 Command 대상이 아니다 — `resolver.py`의 `_HQ_KEYWORDS`/
  `_SNAPSHOT_BUILDERS`에 Trading이 없으므로 "Trading HQ 상태를
  보여줘" 같은 입력은 `status=invalid reason=unknown_hq`로 그대로
  실패 표시된다(새로 막은 것이 아니라 기존 resolver의 동작 그대로).
- Command Resolution이 실패하면(서버 미기동, JSON 손상, `/api/command`
  네트워크 오류) Mock 응답으로 대체하지 않는다 — Chat에 "Command
  Resolution 실패 — Mock으로 대체하지 않음"과 실제 에러 메시지가
  그대로 표시된다.
- `python3 -m http.server`로 띄운 경우 `POST /api/command`가 `501`을
  반환한다 — 이때도 Mock 응답이 아니라 실패가 그대로 드러난다(다만
  이 경우 위 실험 목적대로 쓰려면 `serve_dashboard.py`가 필요하다).
- 이번 단계에서 연결하지 않은 것: 실제 LLM Provider, Engine 호출,
  Task/Conversation Layer(ADC-0018 Defer 상태 그대로 유지, 새 Kernel
  Component를 만들지 않았다).

## Responsive

Desktop(1440x900 안팎)을 기준 디자인으로 삼되 고정 비율로 강제하지
않는다 — 유동 폭(1fr)과 뷰포트 단위만 사용한다.

| 구간 | 폭 | 동작 |
|---|---|---|
| Desktop | 1025px~ | Sidebar Nav(220px) + Main(2열 카드) + 하단 Chat |
| Tablet | 641~1024px | Sidebar Nav 폭 축소(176px) + Main 1열 카드 |
| Mobile | ~640px | Grid를 버리고 DOM 순서 그대로 세로 스택: Header → Nav(가로 스크롤 가능한 탭) → Main Cards → Chat |

가로 스크롤은 페이지 레벨에서 발생하지 않는다 — Investment HQ의
Team 표만 내용이 넓어질 가능성에 대비해 `.table-scroll`로 개별
스크롤을 허용한다(정상 폭에서는 발생하지 않음).

## Boundary

- Trading/Header/Chat/Mock Refresh는 Backend/Core/HQ Python 코드에
  연결하지 않는다 — 모든 데이터는 `js/data.js`의 Mock 객체다.
  Development/Investment HQ만 위 "Evidence 연결" 절 범위에서 예외다.
- `generate_development_snapshot.py`/`generate_investment_snapshot.py`
  는 각각 `hqs/development`/`hqs/investment`의 Python 코드를 import
  하지 않는다(재사용하는 `build_dev_hq_snapshot()`/
  `build_investment_hq_snapshot()` 자체가 이미 이 Boundary를 지킨다).
  Engine/Agent(trader.py 등)를 호출하지 않는다.
- 외부 UI Framework(React/Vue 등)나 신규 npm/Python dependency를
  추가하지 않는다 — 순수 HTML/CSS/Vanilla JS(+ 표준 라이브러리 Python).
- LangGraph/Runtime/Scheduler/Event Bus 등 Kernel Module을 끌어들이지
  않는다 — 이 Prototype에 그런 개념 자체가 없다.
- Trading HQ는 실제로 구현된 HQ가 아니므로 데이터 없이 "PLANNED"
  상태로만 표시하고, Command 대상에도 포함되지 않는다(위 "Chat →
  Command Resolution 연결" 참조). Investment HQ의 Portfolio/Risk/
  Execution은 Freeze 범위 밖이므로 "Deferred"로 명시 분리한다(이제
  Mock이 아니라 `build_investment_hq_snapshot()`이 실제로 반환하는
  값이다).
- Chat은 로컬 메시지 상태 관리 + Command Resolution 호출까지만
  한다 — 어떤 LLM도 호출하지 않는다(`serve_dashboard.py`/
  `resolver.py` 모두 Engine/Agent 호출 코드가 없다).
- `serve_dashboard.py`의 `/api/command` 핸들러는 `hqs/`·`core/`를
  직접 import하지 않는다 — `resolver.py`/`snapshot.py`를 그대로
  호출할 뿐이다.

## Next Step 후보 (우선순위 미확정)

- Investment HQ Team Status 표의 "(Deferred)" 중복 표현 정리
  (`js/render.js`의 접미사 vs Evidence 값 자체의 문구 겹침).
- 실제 LLM Provider 연결 — 단, Command가 비동기·장시간 Engine 호출을
  대상으로 하게 되는 순간 `command-contract`의 "Task NOT REQUIRED"
  결론(read-only 동기 명령 범위 한정)을 재검증해야 한다(Architecture/
  Contract 변경 가능성 있음, 별도 보고 대상).
