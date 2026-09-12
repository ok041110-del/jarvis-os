# EVIDENCE — Stage 04/05 Agent Team Experimental PoC

## 목적

`docs/architecture/core/RFC-0030`·Phase F-2 확장(`projects/dev-hq-agent-responsibility-decomposition-v1/`)이
선정한 최소 PoC 구조 — Stage 04(Target Identification Agent →
Implementation Agent, 순차 Handoff), Stage 05(Review Agent ∥ QA Agent
→ deterministic Aggregator/Verdict, 병렬+종합) — 를 격리된 실행으로
검증한다. Runtime/Event Bus/Message Contract를 새로 만들지 않는다.

## Scope / 격리 확인

- `projects/dev-hq-stage04-05-agent-team-poc-v1/`에만 존재.
  `hqs/development/`·`core/`·`dashboard/` production path 무단 연결
  없음(IN-13).
- 표준 라이브러리(`concurrent.futures.ThreadPoolExecutor`, `time`)만
  의존. `langgraph`/`langchain`/`hqs.*` import 0건, `Message`/`Event`
  클래스 미정의(IN-14).
- 4개 Agent 함수(`target_identification_agent`/`implementation_agent`/
  `review_agent`/`qa_agent`)는 Production `mvp/agents/`·
  `workflow_ast_context.identify_target`의 실제 Engine 호출 **구조만**
  재현한 결정적 mock — 실제 Engine을 호출하지 않는다.

## 실행 결과 (IN-1 ~ IN-14, 전부 PASS)

`/root/.local/bin/pytest projects/dev-hq-stage04-05-agent-team-poc-v1/tests/ -v`
→ **14 passed**.

### Stage 04 — Target Identification → Implementation(순차)

| ID | 검증 대상 | 결과 |
|---|---|---|
| IN-1 | 전체 성공 경로 | PASS — target 식별 결과가 implementation 입력으로 그대로 전달 |
| IN-2 | Target 실패 시 Implementation 미호출(단축) | PASS — spy로 호출 횟수 0건 확인 |
| IN-3 | Implementation 실패 시 상류(target) 성공 결과 보존 | PASS |
| IN-4 | **부분 재실행** — Target을 재계산하지 않고 캐시 재사용, Implementation만 재시도 | PASS — 재사용 객체 동일성(`is`)까지 확인 |
| IN-5 | 순차 구간에 `ThreadPoolExecutor` 없음(병렬화 불가능한 진짜 의존) | PASS |

### Stage 05 — Review ∥ QA → deterministic Aggregator

| ID | 검증 대상 | 결과 |
|---|---|---|
| IN-6 | 전체 성공, Verdict PASS | PASS |
| IN-7 | Review 실패가 QA를 막지 않음(독립 실행) | PASS |
| IN-8 | **Verdict가 Agent 내용을 참조하지 않음** — Review·QA 둘 다 실패해도 결정적 검사가 PASS면 Verdict PASS | PASS — Policy 구현 금지 경계 재확인 |
| IN-9 | 결정적 검사(syntax) 실패 시 Verdict FAIL | PASS |
| IN-10 | **실제 병렬 실행(벽시계 측정)** — 각 0.2s 지연 2개 Agent 동시 실행 시 총 소요 <0.35s(순차라면 ≥0.4s) | PASS — 실측 병렬성 증거 |
| IN-11 | **부분 재실행** — QA만 실패 시 QA만 재시도, Review는 캐시 재사용, Verdict 재종합 값 불변 | PASS |
| IN-12 | 실패가 예외가 아닌 값으로 전파 | PASS |

### 격리 검증

| ID | 결과 |
|---|---|
| IN-13 | PASS — Production 경로 밖에 위치 |
| IN-14 | PASS — LangGraph·Kernel/HQ·Runtime/EventBus/Message/Event 클래스 정의 없음 |

## Plain Python Orchestration 복잡도 측정

| 지표 | Stage 04(순차) | Stage 05(병렬+종합) |
|---|---|---|
| Orchestration 코드량(주석/빈 줄 제외 실질 라인) | **23줄**(`run_stage04_pipeline` + `retry_stage04_implementation_only`) | **39줄**(`run_stage05_pipeline` + `retry_stage05_agent_only`) |
| 상태관리 | caller 지역 변수(dict)뿐 — Kernel/Runtime이 보유하는 공유 State 없음 | 동일 — `ThreadPoolExecutor.submit()` 결과(Future)만 지역 변수로 보관 |
| 오류 전파 | 예외 미사용, `{"status": "error", "failed_at": ...}` 값 반환(IN-2, IN-3) | 동일 패턴(IN-7, IN-12) |
| 재실행 복잡도 | 캐시된 성공 dict를 인자로 넘기는 별도 함수 1개(`retry_stage04_implementation_only`, 6줄) | 캐시된 성공 dict에서 필요한 필드만 재사용하는 별도 함수 1개(`retry_stage05_agent_only`, 12줄) — 분기(`agent == "review"`/`"qa"`) 1개 추가 |
| 새 추상화(클래스/프로토콜/State 스키마) 도입 여부 | **없음** | **없음** |

`caller.py` 전체 101줄(주석·docstring 포함)로 두 Stage의 순차·병렬·
부분 재실행 6가지 시나리오를 전부 표현했다 — Agent 수가 늘어난 것은
새 오케스트레이션 패턴이 아니라 기존 Phase E(`multi-agent-handoff-mvp-v1`)
패턴(직접 호출 + `ThreadPoolExecutor`)의 **단순 반복 적용**이었다.

## Graph Runtime이 필요한 복잡도가 발생했는가 — Evidence 중심 판단

**발생하지 않았다.** 근거:

- 상태관리: 재실행(IN-4, IN-11)이 필요로 한 것은 "이전 성공 결과를
  담은 dict를 다음 호출의 인자로 넘기는 것"뿐이었다 — Checkpoint
  직렬화·복원 메커니즘이 전혀 필요하지 않았다.
- 오류 전파: 값 기반 실패(IN-2, IN-3, IN-7, IN-12)가 별도 예외 처리
  프레임워크 없이 일반 `if` 분기만으로 완전히 표현됐다.
- 병렬성: `ThreadPoolExecutor` 9줄(`with` 블록)만으로 Fan-out/Fan-in을
  구현했고 IN-10이 실제 동시 실행을 시간으로 증명했다 — 별도 Graph
  compile·superstep 개념이 필요하지 않았다.
- 조건부 분기·Loop: 이 PoC 어디에도 없다(Stage 04/05 원본 코드 조사
  결과와 일치, `RFC-0030` §4).

## Production Regression Baseline

`/root/.local/bin/pytest hqs/development/mvp/tests/ -q` (이 PoC 작성
전후 동일 명령 재실행) → **186 passed, 6 skipped** — 변경 없음. 이
PoC가 `hqs/development/` 어떤 파일도 건드리지 않았음을 재확인한다.

## 임시 산출물 정리

`__pycache__`(이 PoC 실행 중 생성) 삭제 완료. 저장소 루트
`.pytest_cache`는 git 추적 대상이 아니며(`.gitignore` 대상,
`git status --porcelain`에 나타나지 않음) 별도 정리가 필요 없다.

## 성공/실패/폐기 기준

- **성공 기준**: IN-1~IN-14 전부 PASS, Production 회귀 기준선 무영향
  — **충족**.
- **Architecture 승격 기준**: ADC 채택 기준(①·②) — 이 PoC가 보여준
  복잡도(순차 23줄, 병렬+종합 39줄, 새 추상화 0개)는 오히려 **Graph
  Runtime 도입의 근거를 약화**시킨다. §"Graph Runtime이 필요한 복잡도"
  절이 그 근거다.
- **폐기 기준**: 이 Experimental Component는 반복적 가치가 추가로
  확인되지 않는 한 RFC 없이 즉시 제거 가능하다(`ARCHITECTURE_GOVERNANCE.md`
  "Experimental Implementation"). 이 Evidence는 그 존재만으로 Formal
  Architecture Decision이나 ADC Accept를 발생시키지 않는다.
