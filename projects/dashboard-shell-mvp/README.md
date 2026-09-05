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

## 실행

```
cd projects/dashboard-shell-mvp
python3 -m http.server 8765
```

브라우저에서 `http://localhost:8765` 접속. `index.html`을 직접
더블클릭해서 열어도 동작한다(외부 모듈 로더 없이 일반 `<script>`
태그만 사용).

## 구조

| 파일 | 책임 |
|---|---|
| `index.html` | Header / Nav / Main / Chat 4개 영역의 정적 骨格만 정의 |
| `css/dashboard.css` | Dark Professional Dashboard 스타일, CSS Grid 레이아웃, Responsive 대응 |
| `js/data.js` | Mock Data 단일 저장소 — `get*` 함수가 유일한 조회 지점. 실제 데이터로 교체 시 이 파일의 함수 내부만 바꾸면 된다 |
| `js/render.js` | 데이터를 입력받아 DOM 문자열을 만드는 순수 렌더 함수. Mock 여부를 모른다 |
| `js/app.js` | 상태(activeHQ/messages) 보관 + 이벤트 처리 + 부분 렌더링 오케스트레이션. Navigation 선택을 `location.hash`와 동기화(새로고침/뒤로가기·앞으로가기에서도 선택된 HQ 유지) |

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

- Backend/Core/HQ Python 코드에 연결하지 않는다 — 모든 데이터는
  `js/data.js`의 Mock 객체다.
- 외부 UI Framework(React/Vue 등)나 신규 npm/Python dependency를
  추가하지 않는다 — 순수 HTML/CSS/Vanilla JS.
- LangGraph/Runtime/Scheduler/Event Bus 등 Kernel Module을 끌어들이지
  않는다 — 이 Prototype에 그런 개념 자체가 없다.
- Trading HQ는 실제로 구현된 HQ가 아니므로 데이터 없이 "PLANNED"
  상태로만 표시한다. Investment HQ의 Portfolio/Risk/Execution은
  Freeze 범위 밖이므로 "Deferred"로 명시 분리한다.
- Chat은 로컬 메시지 배열 상태 관리만 한다 — 어떤 LLM/Engine도
  호출하지 않는다.

## Next Step 후보 (우선순위 미확정)

- `js/data.js`의 `get*` 함수 중 하나를 `projects/unified-dashboard/`가
  이미 만든 실제 Evidence 기반 Snapshot Builder로 교체해보는 실험
  (Mock → 실제 데이터 1개 필드 치환 검증)
