# E5 — Workflow Adapter 비-LangGraph 독립 계보 in-repo 통합 테스트 Evidence

검증일: 2026-09-04

## 문서 성격

이 문서는 **Evidence 기록이다. Governance 문서가 아니다.** Architecture
Decision을 포함하지 않는다. RFC/ADC/ADR/Baseline을 수정하지 않는다.
LangGraph 채택을 승인하지 않는다. `ADC-0021` §8 Gate **(B)**(`ADC-0019`
재검토 조건 (c) — LangGraph와 다른 계보의 조건부 분기·Loop 실행 관찰)와
Gate **(C) 잔여 한계 (ii)**(E4 대조 어댑터가 LangGraph 단일 계보)에 대해
비-LangGraph 독립 실행 계보(L-A = worklist 인터프리터)를 구현·실행한
결과를 기록하고, 그 결과가 두 gate에 무엇을 기여하는지 과장 없이
판정한다.

## Summary

- **결과: IN-1 ~ IN-6, 25개 테스트 전부 PASS** (Python 3.12.14,
  `langgraph==1.2.11`, `pytest==9.1.1` — E4 `projects/workflow-adapter-reversibility-v2/.venv`
  재사용, E2/E3/E4와 동일 계보·버전).
- **L-A(`adapters/worklist.py`, 170 LOC, 표준 라이브러리 + `domain.graph_spec`만
  의존)** 가 E4의 도메인 형태 그래프(5-way 병렬 fan-out → 토론 수렴 Loop
  3라운드 → 조건부 라우팅, 3 시나리오)에서 LangGraph 대조 어댑터(L-LG)와
  **최종 State dict deep-equal**, **노드 예외 값 인코딩(비전파)**,
  **caller-owned JSON checkpoint의 별도 프로세스 재개 == 단발 실행**,
  **계보 교체 시 caller/domain 파일 해시 불변** + `core/`·`hqs/`에
  `langgraph`/`langchain` import 0, **`langgraph` import가 L-LG 1개
  파일에 격리**됨을 in-repo 실행으로 확인.
- **계보 독립성(IN-6, 신규)**: L-A의 import는 `{__future__, collections,
  copy, domain}` 뿐 — `langgraph`/`langchain`/서드파티 0, `sequential.py`
  import 0. L-A docstring이 (a) E4 `sequential.py`(하드코딩 절차)와
  (b) `langgraph.py`(`StateGraph.compile()` + superstep)와의 실행 모델
  차이를 명문화하고, 테스트가 이를 강제.
- 저장소 Production 경로(`core/`·`hqs/`·`dashboard/`·`docs/architecture/`·
  `docs/decisions/`)·`IMPLEMENTATION_RULES.md`·의존성 매니페스트 무변경.
  변경은 `projects/workflow-adapter-nonlanggraph-lineage-v1/`에 한정.
- **Gate 기여(과장 없이)**: E5는 §16.6 A-IN 5항목 + Reversibility 필수
  불변조건을 **LangGraph 아닌 독립 계보에서 재현**했다. 다만 (i) 노드가
  여전히 결정론적 stub이고, (ii) 비-LangGraph 계보가 **1개(L-A)** 이며,
  (iii) seam이 harness 로컬 관례라는 한계가 있다. 따라서 E5가 Gate (B)
  재검토 조건 (c)를 **충족시키는지 / 독립 관찰이 몇 건으로 카운트되는지**는
  이 문서가 선언하지 않는다 — 후속 ADC가 판정한다. E5는 Gate (C)의 잔여
  한계 (i)·(iii)를 **해소하지 않는다**.

## 1. 검증 환경

| 항목 | 값 |
|---|---|
| 실행 위치 | `projects/workflow-adapter-nonlanggraph-lineage-v1/` (저장소 안) |
| Python | 3.12.14 (E4 격리 venv `projects/workflow-adapter-reversibility-v2/.venv` 재사용) |
| langgraph | 1.2.11 (L-LG 대조 레그에만 필요 — E2/E3/E4와 동일) |
| pytest | 9.1.1 |
| 저장소 의존성 매니페스트 | 무변경 (`langgraph`는 재사용 격리 venv에만) |
| Production 경로 변경 | 없음 (`git status`: `projects/workflow-adapter-nonlanggraph-lineage-v1/` 신규만) |

재현: `README.md` "재현" 절.

## 2. 검증 대상 구성

- **도메인**(E4에서 byte-identical 복제, `langgraph` 무의존): 13-node
  그래프 — `dispatch` → 5-way 병렬 분석가 fan-out → `collect` fan-in →
  `bull_case`/`bear_case`/`judge` 토론 Loop(값 기반 수렴, 3라운드) →
  `trader` 조건부 결정 → `route_after_decision` 조건부 라우팅 →
  `final_report` / `escalate_data_gap`. 의미 출처 =
  `hqs/investment/teams/stock_team.py`·`trader.py`(참조만).
- **시나리오**(결정론적 stub, E4 복제): `clean`(정합 → BUY →
  `final_report` → COMPLETED), `data_gap`(sentiment 충돌 → HOLD →
  `escalate_data_gap` → ESCALATED_DATA_GAP), `node_error`
  (`analyst_fundamental` 예외 → catch-and-encode → COMPLETED +
  `NODE_ERROR` flag + `fundamental` 키 부재).
- **계보 어댑터**:
  - **L-A `adapters/worklist.py`** (신규, 비-LangGraph 독립 계보):
    `graph_spec` 선언을 데이터로 해석하는 **ready-queue worklist
    인터프리터**. 정적 edge 표 + predecessor 집합을 `graph_spec`에서
    파생하고, 각 노드 완료 시 후속 edge(정적 + `debate_should_loop`·
    `route_after_decision` predicate 평가)를 런타임에 계산해 enqueue한다.
    수렴 Loop는 `judge`가 "loop" 라우팅 시 토론 하위 영역을 미완료로
    되돌려 재실행. 컴파일 단계·superstep·외부 그래프 런타임 없음. 단일
    스레드. catch-and-encode·reducer 명시적 merge는 어댑터 책임.
  - **L-LG `adapters/langgraph.py`** (E4 복제, 대조): `StateGraph` +
    `add_conditional_edges` + `compile()`. `Annotated[list, operator.add]`
    reducer. 노드 wrap으로 catch-and-encode.
- **seam**: `caller.run_full(adapter, inputs)` / `caller.phase1_and_save(adapter, inputs, path)`
  / `caller.load_and_phase2(adapter, path)` (E4 복제, byte-identical).
  `caller.py`·`domain/*`는 `adapters`를 import하지 않으며 교체점은
  `adapter` 인자 한 곳. **이 시그니처는 harness 로컬 관례이며 확정 계약
  시그니처가 아니다**(E4 EVIDENCE §2 계승).
- phase 경계 = `collect` fan-in 직후 (E4와 동일 fixture 선택).

## 3. 실행 결과 — 25/25 PASS

```
$ .venv/bin/pytest tests/ -p no:cacheprovider
platform darwin -- Python 3.12.14, pytest-9.1.1
collected 25 items
tests/test_lineage_v1.py .........................                       [100%]
============================== 25 passed in 1.04s ==============================
```

| 불변조건 | 테스트 | n | 결과 | 검증 내용 |
|---|---|---|---|---|
| **IN-1** 최종 State 동치 (A-IN a·b·c·d) | `test_IN1_final_state_equivalence_worklist_vs_langgraph[clean/data_gap/node_error]` | 3 | PASS | `run_full(worklist)`의 직렬화 State == `run_full(langgraph)` (dict deep-equal). 독립 계보가 fan-out·fan-in·조건부 분기·수렴 Loop를 LangGraph와 동일 결과로 진행 |
| (IN-1 전제 기록) | `test_IN1_worklist_actually_walks_conditional_and_loop[...]` | 3 | PASS | worklist 계보가 실제로: Loop 본문 3회(`BULL r0/r1/r2`, `debate_round==3`), 조건부 분기 두 갈래(`clean`→`final_report`·`escalation` 부재 / `data_gap`→`escalation`·`final_report` 부재), `node_error`→`NODE_ERROR:analyst_fundamental` flag + `fundamental` 키 부재 |
| **IN-2** 실행 결과의 값 표현(예외 비전파) | `test_IN2_result_as_value_no_exception[3 시나리오 × 2 계보]` | 6 | PASS | `run_full`·`run_phase1`·`run_phase2` 어느 것도 경계 밖으로 예외 전파 안 함. `node_error`에서 두 계보 모두 예외를 `NODE_ERROR:` State 값으로 인코딩. terminal outcome이 항상 State 값 |
| **IN-3** caller-owned checkpoint의 phase-boundary resume (A-IN e) | `test_IN3_caller_owned_checkpoint_resume[2 시나리오 × 2 계보]` | 4 | PASS | `run_phase1` 반환값이 JSON round-trip 성공·라이브러리 타입 0. caller가 파일에 저장 → **별도 프로세스**(`_resume_subprocess.py`)가 로드해 `run_phase2` → 결과 State == 단발 `run_full`. adapter 객체 폐기 후에도 성립 |
| | `test_IN3_adapter_does_no_persistence_io` | 1 | PASS | 두 계보 소스에 `open(`/`json.dump`/`json.load`/`pickle` 등 0 — 값 '생산'만 |
| **IN-4** 교체 시 Kernel/HQ 코드 0 변경 | `test_IN4_swap_zero_kernel_hq_change` | 1 | PASS | `caller.py`·`domain/*` 5파일에 `import adapters`/`langgraph`/`langchain` 0. seam = `adapter` 인자 1개. `git grep -nE 'langgraph\|langchain' -- core/ hqs/` == 0건 |
| | `test_IN4_hashes_identical_across_lineages` | 1 | PASS | worklist·langgraph로 각각 `run_full`+`phase1_and_save` 실행해도 `caller.py`+`domain/*` SHA-256 5개 전부 불변 |
| **IN-5** 라이브러리 경계 격리 | `test_IN5_langgraph_import_single_module` | 1 | PASS | `langgraph` import가 `adapters/langgraph.py` 정확히 1개 모듈. `adapters/worklist.py`·`caller.py`·`domain/*`에 0 |
| | `test_IN5_domain_and_worklist_import_without_langgraph` | 1 | PASS | `sys.modules['langgraph']=None`으로 차단한 별도 프로세스에서 `domain.*`·`adapters.worklist`·`caller` 정상 import + 전체 worklist 실행 → COMPLETED |
| | `test_IN5_no_library_types_in_state` | 1 | PASS | 두 계보의 최종 State에 `langgraph`/`langchain_core` 타입 인스턴스 0 (전부 `dict`/`str`/`int`/`bool`/`list`) |
| **IN-6** 계보 독립성 (신규) | `test_IN6_worklist_stdlib_and_domain_only` | 1 | PASS | AST 파싱 — L-A의 import root ⊆ `{__future__, copy, collections, domain}`. `langgraph`/`langchain`/서드파티 0 |
| | `test_IN6_worklist_documents_independent_execution_model` | 1 | PASS | L-A docstring에 "실행 모델" 명문화 + `sequential.py`·`langgraph.py` 두 대조 계보와의 구분 서술 존재 |
| | `test_IN6_lineages_do_not_share_code` | 1 | PASS | `worklist.py` ↔ `langgraph.py` 상호 import 0. 공유는 `domain.*` 한 곳 |

## 4. 이 Evidence가 보이는 것 / 보이지 않는 것

**보이는 것** — `BASELINE.md` §16.6 A-IN 5항목(State·Node·Conditional
Edge·Loop·값 기반 Checkpoint/Resume) + Adapter Contract 부속 명세
(a)(b)(d) + Reversibility 필수 불변조건이, **LangGraph 계보에서 파생되지
않은 독립 실행 메커니즘**(worklist 인터프리터, 표준 라이브러리만)에서도
도메인 형태 그래프에 대해 LangGraph와 **동일하게** 성립하며, 계보 교체가
Kernel·HQ 코드 0 변경으로 이뤄지고, 각 계보의 구현 문법이 어댑터 경계
안에 갇힘을 **저장소 안의 실행 가능한 통합 테스트**로 확인. E4가
"Sequential Reference(대조와 co-design된 floor) ↔ LangGraph"로 보인 것을,
E5는 "구조적으로 독립인 비-LangGraph 계보 ↔ LangGraph"로 강화.

**보이지 않는 것 (E5의 한계 — 후속 ADC가 gate 충족 판정 시 고려)**:

1. **결정론적 stub** — 노드가 fixture 기반 순수 함수다(E4 §4 한계 1과
   동일). Gate (C) 잔여 한계 (i)를 E5는 **해소하지 않는다**. 실엔진
   비결정성·부분 실패율 하 동치는 미검증.
2. **비-LangGraph 계보 1개** — L-A뿐이다. `ADC-0019` Risks 표는 "다른
   계보 또는 v2 프로덕션 맥락의 독립 관찰 추가"를 요구하며, 독립 관찰
   3건이 **비-LangGraph 몇 건으로 구성돼야 견고한지**(1건이면 충분한지,
   L-B가 필요한지)는 이 문서가 판단하지 않는다. L-B(2번째 비-LangGraph
   계보)는 L-A 결과 확인 후 별도 결정(`README.md`).
3. **seam이 harness 로컬 관례** — `run_full`/`run_phase1`/`run_phase2`는
   이 프로토타입의 테스트 관례이지 `ADC-0020` §Q-C가 규정한 확정 계약
   시그니처가 아니다(E4 §4 한계 3 계승).
4. **프로덕션 트래픽 미검증** — Gate (C) 잔여 한계 (iii)를 E5는 해소하지
   않는다.
5. **mid-node resume 미검증** — IN-3는 phase 경계(C1)만(E4 §4 한계 5 계승).

## 5. 판정 — Gate (B) / Gate (C) 기여

| 질문 | 판정 |
|---|---|
| E5가 §16.6 A-IN 5항목 + Reversibility 필수 불변조건을 **비-LangGraph 독립 계보**에서 재현했는가 | **예** — IN-1~IN-6 25개 PASS. L-A는 `langgraph`/서드파티 무의존, 자체 실행 모델(worklist), E4 sequential·LangGraph 두 계보와 구조적으로 구분(IN-6) |
| E5가 Gate **(B)** `ADC-0019` 재검토 조건 (c)를 **충족**시키는가 | **이 문서가 선언하지 않음** — 비-LangGraph 조건부 분기·Loop 실행 관찰 **1건(L-A)** 을 추가한다. 기존 관찰(E1 v1 실사용 + E2 PoC, LangGraph 2건)에 이 1건을 더하면 "독립 관찰 3건"에 도달하고 "동일 계보" 우려가 부분 해소되나, 3건 카운팅·1건으로 충분한지의 판정은 후속 ADC의 몫(`ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ADC Accept를 발생시키지 않는다") |
| E5가 Gate **(C)** 잔여 한계 (ii)(대조 어댑터 LangGraph 단일 계보)를 진전시키는가 | **예 — 부분** — E4의 대조를 "비-LangGraph 독립 계보 ↔ LangGraph"로 강화. IN-1~IN-5를 이 쌍으로 재현. 단 잔여 한계 (i)(결정론적 stub)·(iii)(프로덕션 트래픽)은 **해소하지 않음** → Gate (C) 완전 discharge 아님 |
| E5가 Gate **(A)**(v1 결정 2/5/9/11)를 진전시키는가 | **무관** — Gate (A)는 `ADC-0022`/`ADC-0023`으로 이미 Resolved(BASELINE v1.16) |
| E5가 LangGraph 채택·구현 착수·`IMPLEMENTATION_RULES` 해제·§14 승격 중 무엇이든 발생시키는가 | **아니오** — 전부 후속 절차. E5는 Evidence 기록일 뿐 |

## 6. Traceability

| 문서 / 절 | 관계 |
|---|---|
| `ADC-0019` §Risks·재검토 조건 (c) | (c)의 "LangGraph와 다른 계보 ... 관찰 추가" 대상. E5가 비-LangGraph 계보 1건 제공. 충족 판정은 후속 ADC |
| `ADC-0021` §8 Gate (B)/(C) | (B) 진전(관찰 1건 추가) / (C) 잔여 한계 (ii) 부분 진전. (A)는 무관(Resolved) |
| `RFC-0020` §8.2 Q-I | "직접 구현 최소 그래프 실행기" — L-A(worklist 인터프리터, 170 LOC)가 그 형태 |
| E4 `projects/workflow-adapter-reversibility-v2/` EVIDENCE.md §4 한계 2, §5 | E5가 그 한계("대조 어댑터 LangGraph 단일 계보")를 겨냥. E4 IN-1~IN-5 구조 계승 + IN-6 신설 |
| E4 Test Design `docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md` §205 | "(B) 미착수 — 별도 관찰 확보 또는 직접 구현 최소 그래프 실행기". E5가 후자 수행 |
| `BASELINE.md` v1.16 §16.6 | 검증 대상 문언, 무변경. §16.6 "명칭" 문단의 "Workflow Adapter ≠ §16.2 Engine Adapter" 구분과 무관(별도 축) |
| `ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" | 위치·격리 근거. Formal Contract·Frozen Boundary 무변경 |
