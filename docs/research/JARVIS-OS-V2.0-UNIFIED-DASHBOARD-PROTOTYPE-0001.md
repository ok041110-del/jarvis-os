# JARVIS-OS-V2.0-UNIFIED-DASHBOARD-PROTOTYPE-0001: Unified Dashboard Experimental Prototype — Evidence

**문서 성격**: Experimental Implementation 완료 보고서
(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
Implementation" 절 준수). Formal Architecture Decision이 아니다.
Production `dashboard/`, `BASELINE.md`, Dev HQ/Investment HQ Freeze
문서, Kernel Architecture를 수정하지 않는다.

**핵심 결론**: `projects/unified-dashboard/`에 격리된 Prototype으로
Global/HQ Dashboard의 "Observe" 원칙을 실증했다 — Dev HQ/Investment
HQ의 실제 Evidence 파일(Freeze 문서, `checkpoints/manifest.json`,
`trader_decision.md`)만 읽어 상태를 표시하고, `hqs/*`의 어떤 Python
코드도 import하지 않고도 Global Dashboard가 동작함을 확인했다.

---

## 1. Prototype Objective

Production Dashboard 완성이 아니라, Dev HQ/Investment HQ 상태를
하나의 화면에서 관찰함으로써 향후 Dashboard Architecture Evidence를
생성하는 것. `JARVIS-OS-V2.0-FUTURE-ARCHITECTURE-PROMOTION-POLICY-0001.md`가
결론 내린 "기존 Experimental Implementation 절로 착수 가능"을
실제로 적용한 최초 사례다.

---

## 2. Implementation Boundary

- 위치: `projects/unified-dashboard/`(격리, `hqs/`·Production
  `dashboard/`에 미연결).
- 신규 dependency: **0개**(Python stdlib만 사용 — `json`, `re`,
  `pathlib`, `dataclasses`, `html`, `datetime`). `pyproject.toml`이
  저장소에 존재하지 않아 새 Framework(Flask/FastAPI/Streamlit 등)
  도입 여부를 검토했으나, 정적 HTML 생성만으로 목표를 달성할 수
  있어 도입하지 않았다.
- `hqs/development/`, `hqs/investment/` Production Code: **무수정**
  (`git status`로 확인, 이번 커밋에 해당 경로 diff 없음).

---

## 3. Actual UI / Structure

```
projects/unified-dashboard/
├── README.md
├── snapshot.py            # Data Acquisition(hqs/* import 없음)
├── render.py               # Global Shell 렌더링
├── generate_dashboard.py   # CLI 진입점
├── output/dashboard.html   # 생성된 정적 HTML(실제 데이터 반영)
└── tests/test_snapshot.py  # Functional + Boundary Validation
```

실행: `python3 projects/unified-dashboard/generate_dashboard.py` →
`output/dashboard.html` 생성(가로형 Sidebar Navigation + HQ Card,
Notion 설계 노트 §9 레이아웃 방향과 정합).

---

## 4. Data Sources

| HQ | 실제 소스 | 방식 |
|---|---|---|
| Dev HQ | `docs/architecture/core/DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`(정규식으로 "109 passed" 추출), `hqs/development/mvp/agents/*.py`(파일명 나열) | 텍스트/파일시스템 읽기 |
| Investment HQ | `hqs/investment/dogfooding/{aapl,pg,efa}-trader-verify/checkpoints/manifest.json`(`completed_steps`), `trader_decision.md`(정규식으로 `Direction:` 추출) | JSON 파싱 + 정규식 |

새로운 HQ Runtime API·Event Bus·Orchestrator·Memory Layer·Kernel
Component는 만들지 않았다 — 전부 기존에 이미 존재하는 파일을
읽었을 뿐이다.

---

## 5. Global / HQ Boundary

- Global Shell(`render.py`의 `render_dashboard`)은 `HQSnapshot.detail`
  문자열을 그대로 나열할 뿐, "Trader Decision"이 무엇인지 해석하지
  않는다 — HQ-specific 의미는 각 `build_*_hq_snapshot()` 함수(HQ
  View 책임)에 있다.
- `test_snapshot_module_does_not_import_hq_code`(AST 기반)가 `snapshot.py`
  가 `hqs`/`mvp`/`trader` 모듈을 import하지 않음을 자동 검증한다 —
  Boundary가 "설계상 의도"가 아니라 **테스트로 강제됨**.

---

## 6. Validation

### Functional
- `python3 generate_dashboard.py` 실행 → `dashboard.html` 생성 성공.
- Global View: Dev HQ/Investment HQ 상태·최근 업데이트 시각 표시.
- Dev HQ View: Phase/Workflow/Agent Roles/Latest Validation/Current
  Task 표시 — 전부 실제 파일에서 읽은 값(§4).
- Investment HQ View: Stock/Dividend Stock/ETF 3개 Team의 실제
  `manifest.json` 기반 단계 수·Trader Decision(HOLD 3/3, 실제
  Evidence와 일치)·Final Report 존재 여부 표시.
- Navigation: Sidebar에 HQ 목록 + 상태 배지 표시.
- 실제 Repository 상태와 일치: `109 passed`는 `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`
  원문 그대로, Trader Decision 3건 모두 실제 `trader_decision.md`
  원문(`Direction: HOLD`)과 일치.

### Boundary
- `pytest.ini` 실행 결과 5개 테스트 전부 PASS(§Test 실행 결과).
- Dashboard가 HQ Business Logic을 실행하지 않음 — **PASS**(파일
  읽기만 수행, 코드 실행 없음).
- Engine 직접 호출 없음 — **PASS**(`grep call_engine` 소스 0건).
- Agent 직접 호출 없음 — **PASS**.
- Kernel 의존성 없음 — **PASS**(`core/` import 0건).
- HQ 간 직접 의존성 없음 — **PASS**(`build_dev_hq_snapshot`과
  `build_investment_hq_snapshot`은 서로를 참조하지 않음).

### Regression
Prototype이 `projects/`에 완전히 격리되고 `hqs/`·`core/`를 건드리지
않았으므로(§2), 전체 회귀는 최소 검증으로 충분하다고 판단해
`pytest --ignore=archive` 전체를 1회 실행했다: **287 passed**
(기존 282 + 신규 5, 0 failed) — 회귀 없음.

---

## 7. Evidence Generated

작업 지시 §13의 6개 질문에 대한 답.

| 질문 | 답 |
|---|---|
| Q1. Global Dashboard 최소 공통 HQ 상태는? | `identity`, `status`(NORMAL/WORKING/BLOCKED/DEFERRED/UNKNOWN), `detail`(HQ가 소유하는 서술 목록), `source_files`(추적 가능성) 4개면 Global Shell을 구성하기에 충분했다 — `alerts`/`latest_event`를 별도 필드로 분리할 필요를 이번 Prototype에서는 관찰하지 못했다(2개 HQ, 정적 스냅샷 범위 안에서는). |
| Q2. 공통화 가능한 정보와 HQ-specific 정보의 경계는? | `identity`/`status`/`source_files`는 두 HQ에서 동일한 구조로 재사용 가능했다(공통). `detail`의 **내용**(Stage/Agent Roles vs Team/Trader Decision)은 완전히 달라 공통화가 불가능했다 — Notion 제안의 "공통 骨格 vs HQ-specific metrics" 구분(§6 Dashboard Architecture Review)이 실제 구현에서도 그대로 재현됐다. |
| Q3. Dashboard가 HQ 내부 Logic 없이 상태를 표현할 수 있는가? | **예, 가능했다.** `hqs/*` Python 모듈을 전혀 import하지 않고도 Freeze 문서 텍스트 + JSON manifest + Markdown 정규식 추출만으로 2개 HQ 상태를 전부 표현했다(§4~§6). |
| Q4. 새로운 공통 Contract가 실제로 필요한가? | 이번 Prototype 범위(정적 스냅샷 2개)에서는 **필요하지 않았다** — Python `dataclass`(`HQSnapshot`) 하나로 충분했다. 다만 이는 "HQ가 늘어나거나 실시간 갱신이 필요해질 때도 충분하다"는 뜻은 아니다(§9). |
| Q5. Dev HQ와 Investment HQ를 동시에 표현하면서 Context/Domain Boundary가 깨지지 않는가? | 깨지지 않았다 — Global Shell이 두 HQ의 `detail` 문자열을 각각 별도 Card로 격리해 나열했을 뿐, 교차 참조·병합 로직이 없었다. |
| Q6. 현재 Dashboard 구현만으로 충분한가, Command/Task/Context 계층이 실제로 필요한가? | 이번 Prototype은 **Observe만** 다뤘고 Command/Task/Context 계층은 전혀 필요하지 않았다(정적 파일 읽기로 충분) — Command Contract 필요성은 **여전히 미검증**(다음 Prototype 대상, §12). |

---

## 8. Architecture Findings

- **Dashboard = Observe 원칙**이 실제 코드 수준에서 성립함을 확인 —
  HQ Business Logic/Engine/Agent 호출 없이 상태 표현이 가능했다.
- **Global/HQ 책임 분리**가 실제로 구현 가능하고, AST 기반 테스트로
  강제할 수 있음을 확인(§5) — 이는 향후 Formal Dashboard Contract가
  생기더라도 "Dashboard가 HQ 코드를 import하지 않는다"는 규칙을
  자동 검증할 수 있다는 실질적 Evidence다.
- Investment HQ의 "Deferred" 표시(Portfolio/Risk/Execution)가
  Global Shell 코드 변경 없이 HQ View 데이터만으로 표현 가능했다 —
  Global Shell은 "Deferred가 있는 HQ"라는 사실조차 몰라도 된다.

---

## 9. New Component Candidates

**No New Kernel Component Candidate identified.** 이번 Prototype에서
발견된 반복 책임 후보는 다음 1건뿐이며, Kernel이 아니라 Dashboard
자체의 후속 Architecture Candidate로만 기록한다.

- `HQSnapshot`(identity/status/detail/deferred/source_files) 구조가
  2개 HQ 모두에서 동일하게 재사용됐다 — 이는 §7 Q1·Q4의 "공통 骨格"
  가설을 뒷받침하는 **1차 Evidence**다. 다만 HQ가 2개뿐이고 실시간
  갱신 요구가 없는 정적 Prototype 범위이므로, `HQDashboardSnapshot`
  (Architecture Review 문서가 제안한 공식 Contract)을 지금 Freeze할
  근거로는 **아직 부족하다** — Trading HQ가 추가되거나 실시간 갱신
  Need가 관찰될 때 재검토 대상.

---

## 10. Kernel Impact

**없음.** `core/` 어디에도 의존하지 않았고(§6 Boundary Validation),
Task Scheduler/Orchestrator/Event Bus/Runtime/Memory Engine 중
어느 것도 만들지 않았다(작업 지시 §11 금지 목록 준수). Cross-HQ
공통 Responsibility가 실제로 확인된 바 없으므로 **KERNEL CANDIDATE는
임의로 생성하지 않는다**(작업 지시 §18 원칙 준수). Phase 7은 이
Prototype으로 재개되지 않는다.

---

## 11. Governance Impact

- RFC/ADC/ADR: **불필요** — Experimental Implementation 절의 허용
  범위(격리 Prototype, HQ production path 무단 연결 금지, 성공/실패
  기준 기록) 안에서 진행됐다.
- Experimental Evidence(이번 Prototype)는 그 존재만으로 Formal
  Architecture Decision이나 Kernel 승격을 발생시키지 않는다
  (`ARCHITECTURE_GOVERNANCE.md` L43 그대로 적용) — §9의 발견은
  Architecture Candidate 기록일 뿐 승격이 아니다.
- `BASELINE.md`, Dev HQ/Investment HQ Freeze 문서, Structure v1.0:
  **무수정**.

---

## 12. Next Step

**Production `dashboard/`로 즉시 이동하지 않는다**(작업 지시 §20).
다음 질문이 아직 미해결이다.

- Architecture Boundary가 안정됐는가 — HQ가 2개뿐인 표본으로는
  부족(§9).
- Dashboard Contract가 안정됐는가 — `HQSnapshot`은 Experimental
  Prototype Contract일 뿐, 실시간 갱신·3번째 HQ(Trading)·Command
  Contract 요구를 아직 반영하지 않았다.
- 실제 HQ 데이터 경계가 검증됐는가 — 이번엔 정적 스냅샷(1회 파일
  읽기)만 검증했다. 반복 실행/실시간 관찰은 미검증.

**후보(우선순위 미확정, 다음 Prototype 대상)**:
1. Trading HQ가 실제로 생기면 3-HQ 표본으로 `HQSnapshot` 공통성
   재검증(Kernel Candidate 여부 재판단의 최소 조건인 Cross-HQ
   반복성에 더 가까워짐).
2. Command Contract Prototype(이번엔 다루지 않음, Q6 Open).
3. `docs/research/JARVIS-OS-V2.0-UNIFIED-DASHBOARD-ARCHITECTURE-0001.md`
   §12 RFC Candidate 5건 중 어느 것도 이번 Evidence만으로 RFC
   승격 근거가 되지 않는다 — 계속 Candidate로 유지.

---

## Self Review

- Production Code(`hqs/`, `dashboard/`)를 변경했는가 — **아니오**.
- 신규 dependency를 추가했는가 — **아니오**(stdlib만 사용).
- Global Jarvis Chat/Command Contract/Orchestrator/Scheduler/Event
  Bus/Runtime/Memory Engine/Kernel Component를 만들었는가 — **아니오**.
- Portfolio/Risk/Execution을 Production 기능처럼 표시했는가 —
  **아니오**(Deferred로 명시 분리, 테스트로 강제 검증).
- HQ 내부 코드(`hqs/*`)를 import했는가 — **아니오**(AST 테스트로
  자동 검증).
- Prototype Contract(`HQSnapshot`)를 Production Contract로
  문서화했는가 — **아니오**(README/코드 docstring에 Experimental
  명시).
- Kernel Candidate를 임의로 만들었는가 — **아니오**(§9·§10).
- 전체 회귀 테스트를 실제로 실행했는가 — **예**(287 passed, §6).

---

## 최종 보고

1. **무엇을 구현했는가**: `projects/unified-dashboard/` 격리
   Prototype — Dev HQ/Investment HQ 상태를 정적 HTML로 관찰하는
   최소 Global Dashboard.
2. **어떤 실제 데이터를 사용했는가**: `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`
   (109 passed), `hqs/investment/dogfooding/*-trader-verify/checkpoints/manifest.json`
   + `trader_decision.md`(실제 Trader Decision HOLD 3/3).
3. **Global/HQ Boundary는 어떻게 동작하는가**: Global Shell은 HQ
   `detail` 문자열을 해석 없이 나열, HQ View는 각자의 데이터 읽기
   책임만 가짐 — AST 기반 테스트로 "HQ 코드 import 금지"를 자동
   강제.
4. **무엇이 해결됐는가**: "Dashboard가 HQ 내부 Logic 없이 상태를
   표현할 수 있는가"(Q3)가 **가능하다**로 실증됨.
5. **무엇이 새롭게 확인됐는가**: `HQSnapshot` 공통 骨격이 2개
   HQ에서 재사용 가능했다는 1차 Evidence(§9) — Kernel 승격 근거는
   아직 아님.
6. **어떤 Evidence가 생성됐는가**: §7의 Q1~Q6 답변 전체, §6의
   Functional/Boundary/Regression Validation 결과.
7. **무엇이 아직 부족한가**: 표본 2개 HQ, 정적 1회 스냅샷,
   Command/Task/Context 계층 미검증(§12).
8. **Architecture Candidate가 발생했는가**: 약한 후보 1건
   (`HQSnapshot` 공통 骨格) — RFC 승격 근거는 아직 부족.
9. **Kernel Impact**: 없음.
10. **Governance Impact**: 없음(Experimental Implementation 절
    범위 안에서 진행, 신규 RFC/ADC/ADR 불필요).
11. **Production 승격 가능 여부**: **아니오** — §12의 3개 질문
    미해결.
12. **다음 Implementation**: Command Contract Prototype 또는
    Trading HQ 등장 시 3-HQ 재검증(우선순위 미확정).

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음(`projects/unified-dashboard/`만 신규 추가, `hqs/`·`core/`·`dashboard/` 무수정)
Tests: `projects/unified-dashboard/tests/` 5 passed(신규), 전체 저장소 287 passed(기존 282 + 신규 5, 0 failed, 회귀 없음)
E2E: 해당 없음(정적 파일 기반 Prototype, Engine 호출 없음)
RFC: 없음(Experimental Implementation 범위 — 불필요)
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: (본 작업 커밋 예정)
Branch: `claude/unified-dashboard-prototype`
Next Implementation Candidate: Command Contract Prototype(Q6 Open) 또는 Trading HQ 등장 시 `HQSnapshot` 3-HQ 재검증 — 우선순위 미확정, 다음 세션에서 결정
