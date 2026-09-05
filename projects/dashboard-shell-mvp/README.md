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

Development HQ 한 경로만 예외다 — 아래 "Development HQ Evidence
연결" 참조.

## 실행

```
python3 projects/dashboard-shell-mvp/generate_development_snapshot.py
cd projects/dashboard-shell-mvp
python3 -m http.server 8765
```

브라우저에서 `http://localhost:8765` 접속. **`index.html`을 직접
더블클릭해서 여는 방식은 더 이상 완전히 동작하지 않는다** — Development
탭이 `fetch()`로 `data/development-snapshot.json`을 읽는데, `file://`
프로토콜에서는 이 요청이 CORS로 차단된다(Investment/Trading/Header/
Chat은 여전히 순수 Mock이라 더블클릭으로도 동작). 이 경우에도 Mock로
조용히 대체되지 않고 Development 화면에 "Evidence 연결 실패"가
그대로 표시된다 — 반드시 위 `http.server`로 접속해야 한다.

## 구조

| 파일 | 책임 |
|---|---|
| `index.html` | Header / Nav / Main / Chat 4개 영역의 정적 骨格만 정의 |
| `css/dashboard.css` | Dark Professional Dashboard 스타일, CSS Grid 레이아웃, Responsive 대응 |
| `js/data.js` | 데이터 조회 단일 지점(`get*`). Investment/Trading은 Mock 객체, `getHQSnapshot('development')`만 실제 생성된 JSON을 `fetch()`한다 |
| `js/render.js` | 데이터를 입력받아 DOM 문자열을 만드는 순수 렌더 함수. Mock/Evidence 여부를 모른다. `errorPanel`은 fetch 실패를 명시적으로 표시한다 |
| `js/app.js` | 상태(activeHQ/messages) 보관 + 이벤트 처리 + 부분 렌더링 오케스트레이션. Navigation 선택을 `location.hash`와 동기화(새로고침/뒤로가기·앞으로가기에서도 선택된 HQ 유지). `renderMain()`은 동기 Mock 반환값과 fetch Promise를 모두 처리한다 |
| `generate_development_snapshot.py` | `projects/unified-dashboard/snapshot.py`의 `build_dev_hq_snapshot()`을 재사용해 `data/development-snapshot.json`을 생성하는 CLI |
| `data/development-snapshot.json` | 생성된 Development HQ Evidence Snapshot(커밋 대상 — `unified-dashboard`의 `output/`·`frontend/public/data/` 선례와 동일) |

## Development HQ Evidence 연결 (실험)

Development HQ 탭 하나만 Mock Data 대신 실제 Evidence 기반
Snapshot을 표시한다:

```
raw fetch("data/development-snapshot.json")
  ← generate_development_snapshot.py
  ← projects/unified-dashboard/snapshot.py의 build_dev_hq_snapshot()
    (DEVELOPMENT-HQ-V2.0-FREEZE-0001.md, hqs/development/mvp/agents/*.py만 읽음)
```

- 새 Evidence 수집 로직을 만들지 않았다 — `unified-dashboard`가 이미
  검증한 `build_dev_hq_snapshot()`을 그대로 import해서 재사용한다
  (`tests/test_generate_development_snapshot.py`가 같은 함수 객체인지
  검증).
- `progressPercent`는 항상 `null`이다 — Development HQ에는 진행률(%)
  Evidence 자체가 없다(상시 Runtime 없음, ADC-02 Open). Mock이 쓰던
  58%~ 같은 숫자를 지어내지 않고, 화면에 "Evidence 없음"을 그대로
  드러낸다.
- fetch가 실패하면(파일 없음/서버 미기동/JSON 손상) Mock으로 조용히
  대체하지 않는다 — `Render.errorPanel`이 실패 원인(HTTP 상태/예외
  메시지)을 그대로 표시한다.
- Investment/Trading/Header/Chat/Mock Refresh는 전혀 변경되지 않았다 —
  여전히 100% Mock이다.

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

- Investment/Trading/Header/Chat/Mock Refresh는 Backend/Core/HQ
  Python 코드에 연결하지 않는다 — 모든 데이터는 `js/data.js`의 Mock
  객체다. Development HQ만 위 "Evidence 연결" 절 범위에서 예외다.
- `generate_development_snapshot.py`는 `hqs/development`의 Python
  코드를 import하지 않는다(재사용하는 `build_dev_hq_snapshot()`
  자체가 이미 이 Boundary를 지킨다). Engine/Agent를 호출하지 않는다.
- 외부 UI Framework(React/Vue 등)나 신규 npm/Python dependency를
  추가하지 않는다 — 순수 HTML/CSS/Vanilla JS(+ 표준 라이브러리 Python).
- LangGraph/Runtime/Scheduler/Event Bus 등 Kernel Module을 끌어들이지
  않는다 — 이 Prototype에 그런 개념 자체가 없다.
- Trading HQ는 실제로 구현된 HQ가 아니므로 데이터 없이 "PLANNED"
  상태로만 표시한다. Investment HQ의 Portfolio/Risk/Execution은
  Freeze 범위 밖이므로 "Deferred"로 명시 분리한다.
- Chat은 로컬 메시지 배열 상태 관리만 한다 — 어떤 LLM/Engine도
  호출하지 않는다.

## Next Step 후보 (우선순위 미확정)

- Investment HQ에도 같은 방식(`build_investment_hq_snapshot()` 재사용)
  적용해보는 실험.
- Command Resolution(`projects/command-contract/`)을 경유하는 경로로
  전환 — 지금은 정적 JSON을 직접 fetch하지만, 향후 Command/Task 필요
  여부는 비동기·장시간 Engine 호출이 대상이 될 때 재검증 대상이다.
