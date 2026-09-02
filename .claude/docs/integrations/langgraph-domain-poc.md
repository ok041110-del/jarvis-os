# LangGraph Domain PoC — Jarvis Workflow 기반 검증 (E3)

검증일: 2026-09-02

## Summary

- E2(`langgraph.md`)의 toy 카운터 대신, **Investment HQ Stock Team**(`hqs/investment/teams/stock_team.py`)의 실제 Workflow 의미(5-way 병렬 분석 → Bull/Bear 토론 → Trader Decision → 조건부 라우팅)를 반영한 Domain State/Node로 LangGraph 1.2.11의 Conditional Edge·Loop·Checkpoint·Reversibility·Parallel 상호작용을 검증했다 — **26/26 check PASS**.
- 저장소 밖 격리 venv(Python 3.12.14, `langgraph==1.2.11`)에서 수행. 노드 본문은 엔진 호출 없는 결정론적 stub이며, **검증 대상은 그래프 구조·경계·checkpoint 소유 모델·Reversibility**이지 분석 품질이 아니다.
- 저장소(`core/`·`hqs/`·Production workflow) 무변경. `langgraph` import는 PoC 내 Workflow Adapter 1개 파일에만 존재.
- 이 문서는 E3 Evidence의 자립 기록이다. `ADC-0019`/`RFC-0019`/`ADR-0008`/`BASELINE.md`/`IMPLEMENTATION_RULES.md`는 이 검증으로 **변경되지 않으며**, LangGraph 채택을 승인하지 않는다. `ADC-0019 §Q8`·§Decision 조건 6이 여는 후속 ADC의 입력 자료다.
- **핵심 Findings 3건**: (a) phase-boundary caller-owned checkpoint ≠ mid-graph resume, (b) 예외→상태값 변환이 어댑터 필수 불변조건, (c) 병렬 State는 disjoint key 또는 reducer 필수. (§6)

## 1. E2와의 구분

| | E2 (`langgraph.md`) | E3 (이 문서) |
|---|---|---|
| State/Node | toy integer counter | Investment HQ Stock Team 도메인(분석가·연구원·트레이더 역할, Decision 파싱) |
| Conditional Edge | `value < target` | `action==HOLD AND 데이터 불일치 → 에스컬레이션`, 토론 수렴 판정 |
| Loop | 3씩 더하기 반복 | Bull/Bear 토론 라운드(수렴 또는 max 3라운드까지) |
| Checkpoint | LangGraph 소유 `MemorySaver` + `thread_id` | **caller-owned 값 모델**(ADC-0019 A-IN(e))과 E2 방식을 나란히 대조 |
| Reversibility | v1 결론이 API 수준 유효함만 재확인 | 도메인 그래프에서 LangGraph↔순차 함수 **최종 State 동치** 실측 |
| Parallel | 미검증 | fan-out 병합 규칙·실패 전파·wall-clock 동시성 실측 |

## 2. 검증 환경·출처

- 실행: 저장소 밖 격리 venv. **Python 3.12.14**, `langgraph==1.2.11` (전이 의존: `langchain-core 1.6.1`, `langgraph-checkpoint 4.2.0`, `langgraph-prebuilt 1.1.0`, `langgraph-sdk 0.4.4`) — E2와 동일 계보. 전체 `langchain`·`langgraph-api`·Server/Cloud 미설치.
- PoC 소스(원본, 세션 scratchpad — 저장소 미포함): `domain/nodes.py`·`domain/fixtures.py`(도메인 계층, langgraph 무의존), `adapter_langgraph.py`(Workflow Adapter, langgraph import 유일), `adapter_sequential.py`(순차 대체 어댑터), `caller.py`(호출자 = HQ 역할, checkpoint 영속화 소유), `run_poc.py`(검증 harness, 26 check).
- 노드 본문은 fixture 기반 순수 함수 — 2개 시나리오(`clean`, `data_gap`) 모두 결정론적. 재현: 위 환경에서 `run_poc.py` 실행 시 `26/26 checks passed`.
- 도메인 의미 출처: `hqs/investment/teams/stock_team.py`(Wave 병렬 구조), `hqs/investment/checkpoint.py`(caller-owned named-step 캐시), `hqs/investment/trader.py`(REPORT/DECISION 분리·`parse_decision`), `archive/v1` LangGraph adapter(Adapter Reversibility 경계 패턴).

## 3. Domain 시나리오 · Graph 구조

**State**(TypedDict): `ticker` / 섹션별 분석 5키(`fundamental`·`technical`·`industry`·`news_event`·`sentiment`) / `data_flags`(reducer 누적) / 토론(`bull`·`bear`·`debate_round`·`debate_log`·`converged`) / `decision`(action·rationale·reassessment_trigger·warnings) / `route` / `final_report` / `outcome` / `escalation`.

**Node 13개 · Edge**:

```
START → dispatch → {analyst_fundamental, analyst_technical, analyst_industry,
                    analyst_news_event, analyst_sentiment}   ← 병렬 fan-out
                 → collect (fan-in)
       → bull_case → bear_case → judge
            judge  ──[Conditional + Loop]──▶ bull_case   (미수렴 & round<3)
            judge  ──────────────────────▶ trader       (수렴)
            trader ──[Conditional]──▶ final_report        (그 외)
            trader ──[Conditional]──▶ escalate_data_gap   (HOLD & 데이터 불일치)
       final_report → END      escalate_data_gap → END
```

**조건부 술어(도메인 의미)**:
- `debate_should_loop(state)`: `converged`(= bear가 새 논점 0개 **또는** `debate_round >= 3`) → `trader`, 아니면 `bull_case`로 되돌아감.
- `route_after_decision(state)`: `decision.action == "HOLD"` **AND** `data_flags`에 `INCONSISTENT` 존재 → `escalate_data_gap`, 아니면 `final_report`.
- 종료는 값 기반: `outcome ∈ {COMPLETED, ESCALATED_DATA_GAP}`, 예외 없음(ADC-0019 §Q3, §14.3 G-6).

**시나리오 결과**:

| 시나리오 | 입력 특성 | 토론 Loop | Decision | Conditional 라우팅 | outcome |
|---|---|---|---|---|---|
| `clean` | 정합 데이터 | 3라운드 후 수렴 | BUY | → `final_report` | `COMPLETED` |
| `data_gap` | sentiment 소스 target 2× 충돌 | 3라운드 후 수렴 | HOLD | → `escalate_data_gap` | `ESCALATED_DATA_GAP` |

Loop 실증: `debate_log`에 `BULL r0`/`BULL r1`/`BULL r2` — 본문 3회 실제 반복. Conditional 실증: 두 시나리오가 서로 다른 terminal 노드로 도달.

## 4. 실행 결과 — 26/26 PASS

| 블록 | 검증 항목(요약) | 결과 |
|---|---|---|
| 1. Domain·Graph | 13개 도메인 노드 존재 / `judge`·`trader`에 conditional edge / `clean`→3라운드·BUY·COMPLETED / `data_gap`→HOLD·INCONSISTENT→escalate / Loop 본문 3회 반복 | 5/5 |
| 2. Checkpoint ownership | caller-owned resume == 단발 실행 / checkpoint 값이 호출자 디스크의 plain JSON / adapter 파일 I/O 없음 / E2 방식 resume 동일 도달 / **in-memory saver 소멸 시 `thread_id`만으로 재개 불가** / 순차 어댑터로도 동일 | 6/6 |
| 3. Adapter 격리 | `langgraph` import가 Workflow Adapter로 한정 / adapter_langgraph.py가 유일한 non-harness importer / `langgraph` 차단 프로세스에서 domain·sequential·caller 정상 import / State 값에 langgraph 타입 누출 0 | 4/4 |
| 4. Reversibility | `clean`·`data_gap` 모두 LangGraph `run_full` == 순차 `run_full` / caller-owned resume가 두 어댑터에서 동일 도달 / 어댑터 교체 시 caller·domain 파일 해시 불변 | 5/5 |
| 5. Parallel + Conditional | (a) disjoint 키 병합 OK / (b) reducer 없는 공유 키 병렬 쓰기 → `InvalidUpdateError` / (c) `Annotated[list, operator.add]` → 결정론적 병합 / (d) 병렬 분기 실패를 값으로 → 하위 conditional 반영, 값 기반 종료 / (e) 병렬 노드 예외 → `graph.invoke` 밖 전파 / (f) fan-out 5노드×0.4s → wall ~0.4s(순차 2.0s) | 6/6 |

## 5. Checkpoint ownership 대조 (ADC-0019 A-IN(e))

A-IN(e): "진행 상태를 **값으로 표현**하고, **호출자가 그 값을 보관했다 반환하면** 이어서 진행. Adapter는 값을 **생산**만, 영속화는 호출자 몫."

| | E2 방식 (LangGraph-owned `MemorySaver`) | A-IN(e) (caller-owned) — 이 PoC |
|---|---|---|
| checkpoint 값 위치 | `MemorySaver` 객체 내부(그래프 소유) | adapter가 **plain dict 반환** → 호출자가 `checkpoint.json` 저장 |
| 호출자 보유물 | `thread_id` 문자열 | 직렬화 가능한 State 값 전체(13키 JSON) |
| adapter의 파일 I/O | 없음(saver가 메모리 보관) | **전혀 없음** — 호출자만 파일 씀 |
| resume | `invoke(None, {thread_id})` | 호출자가 값 로드 → `adapter.run_phase2(value)` |
| 프로세스 종료(in-memory saver 소멸) | **재개 불가**(fresh saver로 `thread_id` 조회 시 빈 State) | **재개됨**(값이 디스크에 있음) |
| 순차 어댑터로도 | 해당 없음 | **동일 동작** — langgraph 없이 값 반환만으로 성립 |

## 6. Findings (별도 명시)

### (a) phase-boundary caller-owned checkpoint ≠ mid-graph resume

이 PoC의 caller-owned checkpoint는 **phase 경계**(`collect` 직후)에서만 재개한다 — adapter가 `run_phase1`으로 State 값을 반환하고 호출자가 그 값을 보관했다가 `run_phase2`로 넘긴다. adapter는 파일 I/O를 전혀 하지 않으며 순차 어댑터로도 동일하게 성립한다(A-IN(e)에 그대로 부합).

**임의 mid-node 재개**(예: 토론 2라운드 도중)는 LangGraph의 checkpointer(그래프 소유, `thread_id` 키)를 써야 하고, 그건 "그래프 소유" 모델로 되돌아간다. LangGraph의 native checkpoint로 A-IN(e)를 만족시키려면 `get_state().values` 추출 + fresh saver + `update_state` 주입이라는 **비관용적 shim**을 어댑터가 얹어야 한다.

→ **후속 ADC 판단 필요**: Public Contract의 재개 입도를 (i) phase 경계 caller-owned, (ii) LangGraph checkpointer + 직렬화 shim, (iii) 순차 어댑터(값 반환만) 중 무엇으로 할지. PoC상 (i)·(iii)가 A-IN(e)에 자연 부합.

### (b) exception → state 변환 필요성

병렬 노드가 **예외를 raise**하면 `graph.invoke` 밖으로 그대로 전파된다(PoC 블록 5-(e) 실측: `RuntimeError` propagated). ADC-0019 §Q3는 "출력은 성공/실패/취소에 준하는 상태를 **값으로** 표현하며 예외를 던지지 않는다(§14.3 G-6 No Silent Failure)"를 요구한다.

즉 LangGraph를 A-IN 구현체로 쓰려면 **어댑터가 모든 노드에서 catch-and-encode**(예외를 잡아 `data_flags`/`outcome` 같은 State 값으로 변환)를 강제해야 한다. 이는 어댑터 계약으로 못박을 수 있는 것이지 LangGraph가 보장하는 것이 아니다. 실패를 **값으로** 반환한 경우(블록 5-(d), `NO_DATA`)는 하위 conditional이 정상 반영하고 그래프도 값 기반 outcome으로 종료했다 — 규칙은 성립 가능하나 어댑터 책임이다.

→ **후속 ADC 판단 필요**: "예외→상태값 변환"을 이 책임의 필수 불변조건으로 명문화할지.

### (c) parallel State의 disjoint key / reducer 조건

- 병렬 fan-out 노드가 **reducer 없는 동일 키**에 동시에 쓰면 `InvalidUpdateError` (블록 5-(b) 실측).
- **disjoint 키**(분석가별 자기 섹션 키)면 안전하게 병합(블록 5-(a)).
- 공유 누적이 필요하면 `Annotated[list, operator.add]` 같은 reducer로 결정론적 병합(블록 5-(c), `data_flags`·`debate_log`에 적용).

Jarvis 도메인(분석가마다 자기 섹션 산출)은 disjoint 키 모델에 자연 적합하나, State 스키마 설계가 병렬 안전성을 좌우한다.

→ **후속 ADC 판단 필요**: "병렬 노드는 disjoint 키 또는 reducer 필수"를 A-IN 부속 스키마 규약으로 둘지.

### (d) 병렬 fan-out은 실제 wall-clock 병렬

LangGraph 1.2.11은 super-step 내 동기 노드를 **내부 thread pool로 실제 동시 실행**한다 — fan-out 5노드 × 0.4s sleep이 wall ~0.4s(순차면 2.0s)에 완료(블록 5-(f) 실측). `stock_team.py`의 `ThreadPoolExecutor` wave 모델과 일치. 단 threads/GIL이므로 **I/O 바운드 노드**(Jarvis 엔진 호출)에만 유효하고 CPU 바운드 노드는 이득 없다. 이는 v1 `ADR-0007` known gap("병렬 fan-out 동시성 미검증 — 구조만 검증")을 실측으로 갱신한다.

## 7. Reversibility 결과

- `adapter_sequential.py`가 동일 호출자 계약(`run_full`/`run_phase1`/`run_phase2`)을 **langgraph 없이** 제공: Conditional = `if/elif`, Loop = `while`, 병렬 = `ThreadPoolExecutor`(= `stock_team.py` 동일 패턴), reducer 규칙(`data_flags`/`debate_log` 누적)은 `_merge()`로 재현.
- 두 어댑터의 `run_full` 최종 State **동치**(`clean`·`data_gap`). caller-owned checkpoint resume도 두 어댑터에서 동일(`ESCALATED_DATA_GAP`).
- 어댑터 교체 시 `caller.py`·`domain/*` **변경 0**(파일 해시 동일 — 같은 파일을 두 어댑터가 공유). 교체점은 "어느 adapter 모듈을 넘기느냐" 한 곳(호출자가 adapter를 인자로 받음).
- → v1 `ADR-0007` 결정 4(Adapter Reversibility)가 **도메인 형태 그래프 + v2 A-IN 범위에서도** 성립. Core/HQ 수정 불필요.

## 8. Architecture 침투 여부

- **저장소**: `core/`·`hqs/` 활성 `*.py`에 `langgraph`/`langchain` import **0건**(PoC가 저장소를 건드리지 않음). `git status` 클린.
- **PoC 내부**: `langgraph` import = `adapter_langgraph.py` **1개 파일(2줄: `langgraph.graph`, `langgraph.checkpoint.memory`)**. `domain/`·`caller.py`·`adapter_sequential.py`는 0 — `__import__`로 `langgraph`를 차단한 별도 프로세스에서 정상 import 확인. domain State 값에 `langgraph`/`langchain_core` 타입 누출 0(전부 `dict`/`str`/`list`).

## 9. 발견된 한계

1. **caller-owned mid-graph 재개 불가** — 임의 지점 재개는 LangGraph checkpointer(그래프 소유) 요구. A-IN(e) 순수 준수는 phase 경계 재개 또는 별도 직렬화 계층에 한정(§6-a).
2. **예외 전파가 기본** — §Q3 "값 표현·예외 없음"과 반대. 어댑터가 전 노드 catch-and-encode 책임(§6-b).
3. **reducer 미지정 시 병렬 쓰기 크래시** — State 스키마 설계가 병렬 안전성을 좌우(§6-c).
4. **동시성은 threads/GIL** — CPU 바운드 노드는 병렬 이득 없음(현재 Jarvis 엔진 호출은 I/O 바운드라 무관).
5. **노드는 결정론적 stub** — 실제 엔진 비결정성·부분 실패율은 미검증(E2/E3 공통). 그래프 구조·경계·Reversibility·checkpoint 소유 모델만 검증 대상.
6. **재컴파일 오버헤드 미측정** — `run_full`마다 `StateGraph` 재조립·`compile()`(v1 known gap 그대로).
7. **PoC는 저장소 밖 실행** — 이 문서가 결과·구조·출처의 기록이며, 저장소 내 통합 테스트로의 승격은 별도 결정(ADC-0019 Next Step 4).

## 10. ADC-0019 후속 Governance 판단 입력 (발견사항 기록 — 문서 수정 없음)

- `ADC-0019 §Decision 조건 6` / `§Q8`이 여는 후속 ADC(구현체 선택·명칭·Public Port·구현 전략)에서:
  - **A-IN(e) 준수 방식 확정**: §6-(a)의 (i)/(ii)/(iii) 중 Public Contract 선택.
  - **"예외 → 상태 값" 변환을 어댑터 필수 불변조건으로 명문화** 여부(§6-b).
  - **State 스키마 규약**(disjoint 키 + reducer)을 A-IN 부속 조건으로 둘지(§6-c).
- **Reversibility 통합 테스트 재현**(`ADC-0019` Next Step 4): 이 PoC가 v2 A-IN 범위·도메인 그래프에서 LangGraph↔순차 동치를 보였으므로, 저장소 내 통합 테스트로 승격할지가 다음 결정 대상.
- **Rule B**: E1(v1 실사용) + E2(toy API) + **E3(이 PoC, 도메인 그래프)** = 3건이나 여전히 **전부 LangGraph 계보**·프로덕션 트래픽 아님. 다른 계보 또는 v2 프로덕션 관찰은 미확보(`ADC-0019` 재검토 조건 c).
- 이 문서의 존재는 LangGraph 채택 승인이 아니며 `ADC-0019`/`RFC-0019`/`ADR-0008`/`BASELINE.md` v1.12/`IMPLEMENTATION_RULES.md`를 변경하지 않는다.
