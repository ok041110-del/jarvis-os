# E4 — Workflow Adapter Reversibility v2 in-repo 통합 테스트 Evidence

검증일: 2026-09-03

## 문서 성격

이 문서는 **Evidence 기록이다. Governance 문서가 아니다.** Architecture
Decision을 포함하지 않는다. RFC/ADC/ADR/Baseline을 수정하지 않는다.
LangGraph 채택을 승인하지 않는다. `ADC-0021` §8 Gate **(C)**(Reversibility
필수 불변조건의 v2 맥락 in-repo 통합 테스트)의 설계
(`docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md`)를
구현·실행한 결과를 기록하고, 그 결과가 (C)를 어느 수준까지 discharge하는지
과장 없이 판정한다.

## Summary

- **결과: IN-1 ~ IN-5, 22개 테스트 전부 PASS** (Python 3.12.14, `langgraph==1.2.11`, `langchain-core==1.6.1`, `langgraph-checkpoint==4.2.0` — E2/E3와 동일 계보·버전).
- Sequential Reference 어댑터와 LangGraph 대조 어댑터가 동일 caller-facing seam 뒤에서 (a) 도메인 그래프 2+1 시나리오에 대해 **최종 State 동치**, (b) 노드 예외 포함 **경계 밖 예외 비전파(값으로 인코딩)**, (c) **caller-owned JSON checkpoint를 별도 프로세스에서 재개**해 단발 실행과 동일 도달, (d) 어댑터 교체 시 **caller/도메인 파일 해시 불변** + `core/`·`hqs/`에 `langgraph`/`langchain` import 0, (e) **`langgraph` import가 어댑터 1개 파일로 격리**됨을 in-repo 실행으로 확인했다.
- 저장소 Production 경로(`core/`·`hqs/`·`dashboard/`·`docs/architecture/`·`docs/decisions/`) 무변경. 변경은 `projects/workflow-adapter-reversibility-v2/`에 한정. `.venv`는 git-ignored.
- **(C) discharge 수준(과장 없이)**: E4는 (C)를 **v2 맥락·in-repo·A-IN 범위에서 재현했다**. 다만 (i) 노드가 결정론적 stub이고, (ii) 대조 어댑터가 여전히 LangGraph 단일 계보이며, (iii) seam이 harness 로컬 관례라는 세 한계가 있다. 따라서 E4가 `ADC-0019` 조건 4를 **완전히 discharge하는지 / E1처럼 부분 할인인지**는 이 문서가 선언하지 않는다 — 후속 ADR이 판정한다. E4는 `ADC-0019` 재검토 조건 (c)(다른 계보/프로덕션 관찰 = Gate (B))를 **진전시키지 않는다**.

## 1. 검증 환경

| 항목 | 값 |
|---|---|
| 실행 위치 | `projects/workflow-adapter-reversibility-v2/` (저장소 안, 격리 venv) |
| Python | 3.12.14 (uv 관리, `projects/.../.venv`) |
| langgraph | 1.2.11 (전이: `langchain-core` 1.6.1, `langgraph-checkpoint` 4.2.0, `langgraph-prebuilt` 1.1.0, `langgraph-sdk` 0.4.4) — E2/E3와 동일 |
| pytest | 9.1.1 |
| 저장소 의존성 매니페스트 | 무변경 (`langgraph`는 격리 venv에만) |
| Production 경로 변경 | 없음 (`git status`: `projects/workflow-adapter-reversibility-v2/` 신규만) |

재현: `README.md` "재현" 절.

## 2. 검증 대상 구성

- **도메인**(langgraph 무의존): 13-node 그래프 — `dispatch` → 5-way 병렬 분석가 fan-out → `collect` fan-in → `bull_case`/`bear_case`/`judge` 토론 Loop(값 기반 수렴, 3라운드) → `trader` 조건부 결정 → `route_after_decision` 조건부 라우팅 → `final_report` / `escalate_data_gap`. 의미 출처 = `hqs/investment/teams/stock_team.py`·`trader.py`(참조만, import·수정 없음).
- **시나리오**(결정론적 stub): `clean`(정합 → BUY → COMPLETED), `data_gap`(sentiment 충돌 → HOLD → ESCALATED_DATA_GAP), `node_error`(`analyst_fundamental` 예외 raise → catch-and-encode → COMPLETED + `NODE_ERROR` flag).
- **어댑터**: `sequential`(Reference — 조건문/반복문/`ThreadPoolExecutor`/명시적 merge, 외부 의존 0), `langgraph`(대조 — `StateGraph`/`add_conditional_edges`/`compile`, reducer = `Annotated[list, operator.add]`, 노드 wrap으로 catch-and-encode).
- **seam**: `caller.run_full(adapter, inputs)` / `caller.phase1_and_save(adapter, inputs, path)` / `caller.load_and_phase2(adapter, path)`. `caller.py`·`domain/*`는 `adapters`를 import하지 않으며 교체점은 `adapter` 인자 한 곳. **이 시그니처는 harness 로컬 관례이며 `ADC-0020` §Q-C가 규정한 구현체 내부 의무 계약의 확정 시그니처가 아니다.**
- phase 경계 = `collect` fan-in 직후 (E3 §6-a와 동일, fixture 선택 — `ADC-0020` §Q-E-2 Defer를 결정하지 않음).

## 3. 실행 결과 — 22/22 PASS

```
$ .venv/bin/pytest tests/ -p no:cacheprovider
platform darwin -- Python 3.12.14, pytest-9.1.1
collected 22 items
tests/test_reversibility_v2.py ......................                    [100%]
============================== 22 passed in 1.08s ==============================
```

| 불변조건 | 테스트 | n | 결과 | 검증 내용 |
|---|---|---|---|---|
| **IN-1** 최종 State 동치 | `test_IN1_final_state_equivalence[clean/data_gap/node_error]` | 3 | PASS | `run_full(sequential)`의 직렬화 State == `run_full(langgraph)` (dict deep-equal). Conditional 분기·Loop 3라운드가 두 어댑터에서 동일 결과 |
| (IN-1 전제 기록) | `test_IN1_behavior_record[...]` | 3 | PASS | `clean`→COMPLETED·BUY, `data_gap`→ESCALATED_DATA_GAP·HOLD·INCONSISTENT, `node_error`→COMPLETED + `NODE_ERROR:analyst_fundamental` flag·`fundamental` 키 부재. `debate_log`에 `BULL r0/r1/r2` — Loop 본문 3회 실제 반복 |
| **IN-2** 실행 결과의 값 표현(예외 비전파) | `test_IN2_result_as_value_no_exception[3 시나리오 × 2 어댑터]` | 6 | PASS | `run_full`·`run_phase1`·`run_phase2` 어느 것도 경계 밖으로 예외 전파 안 함. `node_error`에서도 두 어댑터 모두 예외를 `NODE_ERROR:` State 값으로 인코딩(어댑터 책임 — `ADC-0020` §Q-D (b)). terminal outcome이 항상 State 값 |
| **IN-3** caller-owned checkpoint의 phase-boundary resume | `test_IN3_caller_owned_checkpoint_resume[2 시나리오 × 2 어댑터]` | 4 | PASS | `run_phase1` 반환값이 JSON round-trip 성공·라이브러리 타입 0. caller가 파일에 저장 → **별도 프로세스**(`_resume_subprocess.py`)가 로드해 `run_phase2` → 결과 State == 단발 `run_full`. adapter 객체·in-memory saver 폐기 후에도 성립 |
| | `test_IN3_adapter_does_no_persistence_io` | 1 | PASS | 두 어댑터 소스에 `open(`/`json.dump`/`json.load`/`pickle` 등 영속화 호출 0 — 값 '생산'만, 저장은 caller |
| **IN-4** 교체 시 Kernel/HQ 코드 0 변경 | `test_IN4_swap_zero_kernel_hq_change` | 1 | PASS | `caller.py`·`domain/*` 4파일에 `import adapters`/`langgraph`/`langchain` 0. seam = `adapter` 인자 1개. `git grep -nE 'langgraph|langchain' core/ hqs/` == 0건 |
| | `test_IN4_hashes_identical_across_adapters` | 1 | PASS | sequential·langgraph로 각각 `run_full`+`phase1_and_save` 실행해도 `caller.py`+`domain/*` SHA-256 5개 전부 불변 |
| **IN-5** 라이브러리 경계 격리 | `test_IN5_langgraph_import_single_module` | 1 | PASS | `langgraph` import가 `adapters/langgraph.py` 정확히 1개 모듈. `adapters/sequential.py`·`caller.py`·`domain/*`에 0 |
| | `test_IN5_domain_imports_without_langgraph` | 1 | PASS | `sys.modules['langgraph']=None`으로 차단한 별도 프로세스에서 `domain.*`·`adapters.sequential`·`caller` 정상 import + 전체 sequential 실행 → COMPLETED. (별도 확인: 같은 차단 하 `adapters.langgraph` import는 `ModuleNotFoundError` — 차단이 실효) |
| | `test_IN5_no_library_types_in_state` | 1 | PASS | 두 어댑터의 최종 State에 `langgraph`/`langchain_core` 타입 인스턴스 0 (전부 `dict`/`str`/`int`/`bool`/`list`) |

## 4. 이 Evidence가 보이는 것 / 보이지 않는 것

**보이는 것** — `BASELINE.md` v1.13 §16.6 A-IN 5항목(State·Node·Conditional Edge·Loop·값 기반 Checkpoint/Resume) + Adapter Contract 부속 명세 (a)(b)(d)가, 도메인 형태 그래프에서 Sequential Reference와 LangGraph 두 구현체로 **동일하게** 성립하며, 교체가 Kernel·HQ 코드 0 변경으로 이뤄지고, 구현체 고유 문법이 어댑터 경계 안에 갇힘을 **저장소 안의 실행 가능한 통합 테스트**로 확인.

**보이지 않는 것 (E4의 한계 — 후속 ADR이 충분성 판정 시 고려)**:

1. **결정론적 stub** — 노드가 fixture 기반 순수 함수다. 실제 엔진 호출의 비결정성·부분 실패율 하에서 IN-1 동치가 유지되는지는 검증하지 않았다(E3 §9-5와 동일 한계). Test Design §2.3에 명시한 의도적 범위 제한.
2. **LangGraph 단일 계보** — 대조 어댑터가 여전히 LangGraph다. E1(v1 실사용) + E2(toy) + E3(도메인 PoC) + E4(이 테스트) = 4건이나 전부 LangGraph 계보이고 프로덕션 트래픽이 아니다. `ADC-0019` 재검토 조건 (c)(다른 계보 또는 v2 프로덕션 관찰) = `ADC-0021` §8 Gate **(B)**는 이 Evidence로 **진전되지 않는다**.
3. **seam이 harness 로컬 관례** — `run_full`/`run_phase1`/`run_phase2`는 이 프로토타입의 테스트 관례이지 `ADC-0020` §Q-C가 규정한 구현체 내부 의무 계약의 확정 시그니처가 아니다. 후속 Implementation Strategy 세부 ADC가 계약 시그니처를 별도 판정한다.
4. **재컴파일 오버헤드 미측정** — `run_full`마다 `StateGraph` 재조립·`compile()`(v1·E3 known gap 그대로). Reversibility 불변조건이 아니므로 gate로 삼지 않았다(Test Design §2.3).
5. **mid-node resume 미검증** — IN-3는 phase 경계(C1)만. 임의 지점 재개(C2)는 `ADC-0020` §Q-E-1 판정대로 범위 밖.

## 5. 판정 — (C) discharge 수준

| 질문 | 판정 |
|---|---|
| (C) "v2 맥락 in-repo 통합 테스트"를 재현했는가 | **예** — IN-1~IN-5 22개 PASS, 저장소 안에서 실행 가능, v2 A-IN 범위·도메인 형태 그래프 |
| E4가 `ADC-0019` 조건 4를 **완전히** discharge하는가 | **이 문서가 선언하지 않음** — §4의 한계 1·3으로 "부분 할인" 판정 여지 존재(E1이 cross-arch 부분 할인, E3가 저장소 밖이었던 것과 유사한 성격). 충분성 판정은 후속 ADR의 몫 |
| E4가 Gate (B)(재검토 조건 (c))를 진전시키는가 | **아니오** — LangGraph 단일 계보(§4 한계 2) |
| E4가 Gate (A)(v1 결정 2/5/9/11)를 진전시키는가 | **아니오** — 별도 축, 이 테스트 범위 밖 |
| E4가 LangGraph 채택·구현 착수·`IMPLEMENTATION_RULES` 해제·§14 승격 중 무엇이든 발생시키는가 | **아니오** — `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ADC Accept를 발생시키지 않는다". 전부 후속 절차 |

## 6. Traceability

| 문서 / 절 | 관계 |
|---|---|
| `docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md` | 이 Evidence가 구현·실행한 설계. §10에 이 결과를 반영 |
| `ADC-0021` §8 (C) / §D1·§D2·§D4 | (C) 수행. D1(Sequential=Reference)·D2(LangGraph=대조 후보)·D4(교체점 1곳) 반영 |
| `ADC-0019` §Q6·조건 4·Next Step 4 | 조건 4의 재현 검증. 조건 5·재검토 조건 (c)는 미충족 유지 |
| `ADC-0020` §Q-C·§Q-D (a)(b)(d)·§Q-E-1 C1 | IN-3/IN-2/IN-1·IN-4가 (a)(b)(d)에 대응. (c) Defer·C2·§14 미접촉 |
| `BASELINE.md` v1.13 §16.6 | 검증 대상 문언, 무변경 |
| `ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" | 위치·격리 근거. §2.4(Test Design) 대조 항목 준수 |
| E1 `archive/v1/tests/integration/test_workflow_adapter_reversibility.py` | template — 3-assertion 구조(Contract Parity/Reversibility/Fail-Closed) 이식 + IN-3 신설, v1 Port 의존 제거 |
| E2 `.claude/docs/integrations/langgraph.md` / E3 `.claude/docs/integrations/langgraph-domain-poc.md` | 동일 계보·버전. E3 §9-7("저장소 내 통합 테스트 승격은 별도 결정")을 이 E4가 수행 |
