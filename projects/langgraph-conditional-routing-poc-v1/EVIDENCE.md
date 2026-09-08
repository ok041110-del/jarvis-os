# LangGraph Conditional Routing Prototype — Evidence

검증일: 2026-09-08

이 문서는 이 Prototype의 실제 실행 기록이다. `README.md`가 범위·재사용
대상·Engine 호출 경로의 불가피한 차이를 설명하며, 이 문서는 그 실행
결과만 기록한다. **이 문서는 LangGraph 채택을 승인하지 않는다** — Formal
Adoption 여부는 이 저장소의 RFC → ADC → ADR 절차 대상이며, 이 Prototype
결과는 그 절차의 입력 자료 후보일 뿐이다.

## 0. 실행 환경 확인

- `langgraph==1.2.11`을 저장소 밖 격리 venv에 설치(저장소 의존성 파일
  변경 없음, `pip show langgraph` 확인).
- OmniRoute 서버 연결 시도 → `Connection refused`(실측):

  ```
  $ python3 -c "from hqs.development.mvp.omniroute_engine import call_engine_via_omniroute; call_engine_via_omniroute('Say PING_OK')"
  FAILED: OmniRoute connection failed: [Errno 111] Connection refused
  ```

  → README가 설명한 대로 `agents.backend.call_engine`/
  `agents.qa.call_engine`을 이 실행 프로세스 안에서만
  `engine.py::call_engine`(Claude CLI 직접 호출)로 교체했다. 실제로
  Claude CLI가 이 환경에 설치·동작함을 별도로 확인:

  ```
  $ claude -p "Say exactly: PING_OK" --output-format text --disallowedTools "..."
  PING_OK
  ```

- 실행 후 `git status --short` — `projects/langgraph-conditional-routing-poc-v1/`
  외 어떤 파일도 변경되지 않음(신규 파일만, 수정/삭제 0건).

## 1. 실행 결과 (실제 Engine 호출, 2 입력 × 2 구현 = 4회 real call)

| Case | 구현 | 소요 시간 | test_execution 생략 여부 | baseline과 분기 일치 |
|---|---|---|---|---|
| CLEAN_CODE | baseline(`run_mvp_0002`) | 8.0s | **True**(생략) | — |
| CLEAN_CODE | LangGraph | 5.0s | **True**(생략) | **일치** |
| SAMPLE_CODE | baseline(`run_mvp_0002`) | 25.8s | False(실행) | — |
| SAMPLE_CODE | LangGraph | 43.1s | False(실행) | **일치** |

전체 원본 응답(`code_review`/`test_execution` 전문)은
`run_results.json`에 그대로 보존했다.

### 1.1 CLEAN_CODE — 분기 판정 실제 로그

- baseline `code_review`(marker 제거 후): *"This function has no relative
  imports to flag. Reviewing the code itself: the implementation is
  correct for its stated purpose..."* → `test_execution`: *"(생략됨:
  code_review에서 이슈가 발견되지 않아 test_execution을 건너뜀)"*
- LangGraph `code_review`(marker 제거 후): **빈 문자열(`""`)** →
  `test_execution`: *"(생략됨: ...)"* (동일)

**빈 문자열에 대한 원인 분석(중요, LangGraph 결함 아님)**: 이번
LangGraph 실행에서 실제 Engine이 반환한 원문이 `NO_ISSUES_FOUND`
한 줄뿐이었던 것으로 보인다 — `_strip_trailing_marker`가 baseline과
LangGraph 양쪽에 **동일하게** 구현돼 있고(README §"동일하게 적용"),
마지막 줄이 marker와 정확히 일치하면 그 줄만 제거하는데 원문이 그
한 줄뿐이면 결과가 빈 문자열이 된다. 이는 두 구현이 **공유하는 기존
Capability 계약**(`backend_agent_code_review`의 지시문·marker 후처리
로직, MVP-0027/0051/0052가 이미 다룬 것과 같은 종류)의 기존 취약점이지,
LangGraph가 새로 만든 결함이 아니다 — 같은 조건이면 baseline도 동일하게
빈 문자열을 반환했을 것이다(baseline이 이번 실행에서는 우연히 더 긴
응답을 받아 드러나지 않았을 뿐).

### 1.2 SAMPLE_CODE — 분기 판정 실제 로그

두 구현 모두 실제 버그(mutable default argument, bare `except:`, 암묵적
`None` 반환)를 정확히 식별했고, 둘 다 `test_execution`으로 라우팅했다
(전문은 `run_results.json` 참고). 응답 문구는 서로 다르지만(Engine
비결정성), **지적한 결함의 종류(3가지 핵심 이슈)는 두 구현이 사실상
동일**했다.

## 2. 비교 — 무엇이 실제로 달라졌는가

| 축 | baseline(plain Python) | LangGraph |
|---|---|---|
| 분기 정확성 | 2/2 case 정확 | 2/2 case 정확, **baseline과 100% 일치** |
| 코드 길이 | `workflow_0002.py` 39줄(if/else 5줄) | `graph_langgraph.py` 84줄(StateGraph 정의 14줄 + TypedDict 6줄 + node wrapper 4개) |
| 새로 요구되는 개념 | 없음(순수 함수 호출) | `TypedDict` State, `StateGraph`, `add_conditional_edges`, `compile()` |
| 실행 속도 | 8.0s / 25.8s | 5.0s / 43.1s (표본 2개, Engine 응답 변동성이 지배적 — 통계적으로 무의미한 차이) |
| 실패 처리 | `try/except` 1곳, 반환 계약 유지 | 동일한 `try/except`를 `run_via_langgraph()` 래퍼에 별도로 작성해야 함(LangGraph의 `app.invoke()`는 이 계약을 대신 제공하지 않음) |
| 미사용 LangGraph 기능 | — | Checkpoint/Resume, Loop, 병렬 fan-out — 이번 시나리오(if/else 1회 분기)에는 전혀 필요 없음 |

**핵심 관찰**: 이 시나리오(단순 2지 분기, 상태 없음, 순차 실행)에서
LangGraph는 baseline의 5줄 `if/else`가 이미 완벽히 처리하는 문제를
`TypedDict` + `StateGraph` + 조건부 엣지 딕셔너리로 다시 표현한 것이며,
**분기 정확성 면에서 얻은 것은 없다**(둘 다 100% 정확, 100% 일치)
— LangGraph가 제공하는 나머지 기능(Checkpoint/Resume, Loop)은 이번
시나리오가 요구하지 않아 전부 미사용으로 남는다.

## 3. Architecture/Contract 변경 필요성 검토

- `hqs/development/`, `core/`, `docs/architecture/`, `docs/decisions/`
  어떤 파일도 이 Prototype으로 변경되지 않았다(§0 `git status` 확인).
- `agents/backend.py`·`agents/qa.py`·`omniroute_engine.py`의 `call_engine`
  전역 교체는 이 Prototype 프로세스 메모리 안에서만 유효했다 — 파일
  자체는 무변경.
- ADC-02(Runtime 존폐)·ADC-09(Workflow 그래프 의미 경계)를 재개설할
  근거를 발견하지 못했다 — 이 Prototype은 State/Node/Conditional Edge만
  썼고(Loop/Checkpoint 미사용), 그 결과가 이미 §16.6(Workflow Adapter,
  Scoped Conditional Accept)이 다루는 범위를 벗어나지 않는다. **Stop
  하지 않는다** — Architecture 변경 필요성이 발견되지 않았으므로 지시
  8·11번에 따라 이 Prototype은 계속 진행해 최종 판단까지 도달했다.

## 4. 최종 판단

| 축 | 판단 |
|---|---|
| 실제 적용 가능성 | 가능(기술적으로 동작함, 분기 결과 100% 일치) — 그러나 "가능하다"가 "이점이 있다"를 뜻하지 않음 |
| 기존 방식 대비 이점 | **이 시나리오에서는 없음** — 정확성·속도 어느 축에서도 baseline을 능가하지 못했고, 추가로 얻은 기능(Checkpoint/Loop)은 전부 미사용 |
| 추가 복잡성 | 있음 — State 스키마 정의, 그래프 조립, 조건부 엣지 딕셔너리, 별도 예외 처리 래퍼까지 4개 개념이 추가로 필요했던 반면 baseline은 `if/else` 5줄 |
| Architecture 영향 | 없음(§3) |
| 운영/유지보수 영향 | LangGraph 의존성(`langchain-core` 포함) 추가, 그래프 구조를 이해해야 하는 진입 장벽 추가 — 이 시나리오 규모에서는 이득 없이 비용만 추가 |
| **최종 Adoption 후보 여부** | **후보 아님(이 시나리오 한정).** 단순 2지 조건부 분기에는 LangGraph가 가치를 더하지 못한다 — 이는 "LangGraph가 나쁘다"가 아니라 "이 문제가 LangGraph의 강점(Loop/Checkpoint/복잡한 State 관리)을 요구하지 않는다"는 뜻이다. `ADR-0018`이 이미 결론지은 "Deferred/Not Adopted"를 이 Prototype이 뒤집을 근거는 나오지 않았다 — 오히려 같은 방향의 실측 Evidence를 하나 더 추가했다. |

## 5. 다음에 이 결론을 뒤집을 수 있는 것

이 Prototype은 **단순 2지 분기**만 시험했다. LangGraph가 실제로
가치를 낼 가능성이 있는 시나리오(다중 라운드 Loop, 여러 단계에 걸친
Checkpoint/Resume, 3개 이상 분기가 얽힌 State)는 이번에 다루지 않았고
— 그 시나리오들은 이미 v1 archive·E2·E3(toy/Domain PoC)·Phase E/F가
검증 범위에 포함했다(README "재검증 안 함" 목록). 이 Prototype이
새로 추가한 것은 "실제 프로덕션 Capability + 실제 Engine 호출 + 단순
분기"라는 **가장 작은** 조합에서도 LangGraph가 이점을 만들지 못한다는
사실 하나뿐이다.
