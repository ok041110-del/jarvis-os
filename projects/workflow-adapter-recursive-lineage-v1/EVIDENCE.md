# E6 — Workflow Adapter L-B(재귀 조합자) 독립 계보 in-repo 통합 테스트 Evidence

검증일: 2026-09-05

## 문서 성격

이 문서는 **Evidence 기록이다. Governance 문서가 아니다.** Architecture
Decision을 포함하지 않는다. RFC/ADC/ADR/Baseline을 수정하지 않는다.
LangGraph 채택을 승인하지 않는다. `ADC-0021` §8 Gate **(B)**(`ADC-0019`
재검토 조건 (c))에 대해 `ADC-0024` §D-B4가 이름 붙인 완전 완화 후속조건
(i) "2번째 비-LangGraph 독립 계보(L-B)"를 구현·실행한 결과를 기록하고,
그 결과가 Gate (B)에 무엇을 기여하는지 과장 없이 판정한다. **Gate (B)
완전 완화나 새 Governance 결정을 이 문서는 선언하지 않는다** — 그 판정은
후속 ADC의 몫이다(`ADC-0024` D-B3·D-B4 계승).

## Summary

- **결과: IN-1′ ~ IN-6′, 31개 테스트 전부 PASS** (Python 3.12.14,
  `langgraph==1.2.11`, `pytest==9.1.1` — E4/E5 격리 venv 재사용, 동일
  계보·버전).
- **L-B(`adapters/recursive.py`, 재귀 조합자, 표준 라이브러리 + `domain.graph_spec`만
  의존)**이 E4/E5와 동일한 도메인 형태 그래프(5-way 병렬 fan-out → 토론
  수렴 Loop 3라운드 → 조건부 라우팅, 3 시나리오)에서 LangGraph 대조
  어댑터(L-LG)와 **최종 State dict deep-equal**, **노드 예외 값 인코딩
  (비전파)**, **caller-owned JSON checkpoint의 별도 프로세스 재개 == 단발
  실행**, **계보 교체 시 caller/domain 파일 해시 불변** + `core/`·`hqs/`에
  `langgraph`/`langchain` import 0, **`langgraph` import가 L-LG 1개 파일에
  격리**됨을 in-repo 실행으로 확인.
- **계보 독립성(IN-6′, 재설계 — E5 IN-6의 기계적 복제 아님)**: (1) 정적
  의존성 — L-B의 import는 `{__future__, copy, domain}` 뿐. (2) **자료구조
  부재** — `class` 정의 0, `collections`(`deque`) import 0 — L-A류
  "인터프리터 인스턴스 + 큐" 패턴이 이름만 바뀐 재구현이 아님을 소스
  구조로 강제. (3) **실행 메커니즘 실측** — `_advance`가 자기 자신을
  재귀 호출함을 AST로 검출하고, 3 시나리오 전부에서 실행 중 최대 콜스택
  깊이 **14**(그래프 실행 경로 길이에 비례)를 실측 — L-A의 `run()`은
  동일 검사에서 `while` 루프 기반이며 자기 재귀 호출이 없음을 대조 확인
  (sibling 파일 소스 텍스트 읽기, **import 없음** — 두 프로젝트는 런타임
  결합 없이 독립적으로 폐기 가능).
- 저장소 Production 경로(`core/`·`hqs/`·`dashboard/`·`docs/architecture/`·
  `docs/decisions/`)·`IMPLEMENTATION_RULES.md`·의존성 매니페스트 무변경.
  변경은 `projects/workflow-adapter-recursive-lineage-v1/`에 한정.
- **Gate 기여(과장 없이)**: E6(L-B)은 §16.6 A-IN 5항목 + Reversibility
  필수 불변조건을 **LangGraph도 L-A도 아닌 세 번째 독립 실행 메커니즘**에서
  재현했다. 다만 (i) 노드가 여전히 결정론적 stub이고, (ii) 세 계보(L-A,
  L-B, L-LG) 전부 단일 프로세스·단일 언어(Python) 구현이며, (iii) seam이
  harness 로컬 관례라는 한계가 있다. E6이 Gate (B) 재검토 조건 (c)의
  "독립 관찰 3건" 카운팅에 몇 건으로 반영되는지, 완전 완화에 이르는지는
  이 문서가 선언하지 않는다 — 후속 ADC가 판정한다. E6은 Gate (C) 잔여
  한계 (i)·(iii)을 **해소하지 않는다**.

## 1. 검증 환경

| 항목 | 값 |
|---|---|
| 실행 위치 | `projects/workflow-adapter-recursive-lineage-v1/` (저장소 안) |
| Python | 3.12.14 (E4 격리 venv `projects/workflow-adapter-reversibility-v2/.venv` 재사용) |
| langgraph | 1.2.11 (L-LG 대조 레그에만 필요 — E2/E3/E4/E5와 동일) |
| pytest | 9.1.1 |
| 저장소 의존성 매니페스트 | 무변경 (`langgraph`는 재사용 격리 venv에만) |
| Production 경로 변경 | 없음 (`git status`: `projects/workflow-adapter-recursive-lineage-v1/` 신규만) |

재현: `README.md` "재현" 절.

## 2. 검증 대상 구성

- **도메인**(E4/E5에서 byte-identical 복제, `langgraph` 무의존): 13-node
  그래프 — `dispatch` → 5-way 병렬 분석가 fan-out → `collect` fan-in →
  `bull_case`/`bear_case`/`judge` 토론 Loop(값 기반 수렴, 3라운드) →
  `trader` 조건부 결정 → `route_after_decision` 조건부 라우팅 →
  `final_report` / `escalate_data_gap`.
- **시나리오**(결정론적 stub, E4/E5 복제): `clean`(정합 → BUY →
  COMPLETED), `data_gap`(sentiment 충돌 → HOLD → ESCALATED_DATA_GAP),
  `node_error`(`analyst_fundamental` 예외 → catch-and-encode → COMPLETED
  + `NODE_ERROR` flag).
- **계보 어댑터**:
  - **L-B `adapters/recursive.py`** (신규, 비-LangGraph 독립 계보 #2):
    재귀 조합자. `_advance(name, state, visited, depth, stop_after,
    starts)`가 predecessor 충족 시 노드를 적용하고 후속 노드로 직접
    재귀한다. `visited`는 매 단계 새 `frozenset`, `state`는 매 단계 새
    `dict`(불변 갱신 스타일) — 어떤 기존 객체도 mutate하지 않는다. 수렴
    Loop는 `visited - _DEBATE`로 새 frozenset을 만들어 다음 라운드
    재귀에 넘긴다. 컴파일 단계·큐·인터프리터 인스턴스 없음. 단일 스레드.
  - **L-LG `adapters/langgraph.py`** (E4/E5 복제, 대조): `StateGraph` +
    `add_conditional_edges` + `compile()`.
- **seam**: `caller.run_full(adapter, inputs)` /
  `caller.phase1_and_save(adapter, inputs, path)` /
  `caller.load_and_phase2(adapter, path)` (E4/E5 복제, byte-identical).
  교체점은 `adapter` 인자 한 곳. 이 시그니처는 harness 로컬 관례이며 확정
  계약 시그니처가 아니다(E4/E5 계승).
- phase 경계 = `collect` fan-in 직후 (E4/E5와 동일 fixture 선택).

## 3. 실행 결과 — 31/31 PASS

```
$ .venv/bin/pytest tests/ -v -p no:cacheprovider
platform darwin -- Python 3.12.14, pytest-9.1.1
collected 31 items
tests/test_recursive_lineage_v1.py ...............................  [100%]
============================== 31 passed in 1.26s ==============================
```

| 불변조건 | 테스트 | n | 결과 | 검증 내용 |
|---|---|---|---|---|
| **IN-1′** 최종 State 동치 (A-IN a·b·c·d) | `test_IN1p_final_state_equivalence_recursive_vs_langgraph[clean/data_gap/node_error]` | 3 | PASS | `run_full(recursive) == run_full(langgraph)` (dict deep-equal). 조건부 분기·Loop 3라운드가 재귀 계보에서 LangGraph와 동일 결과 |
| (IN-1′ 전제 기록) | `test_IN1p_recursive_actually_walks_conditional_and_loop[...]` | 3 | PASS | `clean`→COMPLETED·BUY, `data_gap`→ESCALATED_DATA_GAP·HOLD, `node_error`→COMPLETED+`NODE_ERROR:analyst_fundamental`. `debate_log`에 `BULL r0/r1/r2` — Loop 본문 3회 실제 반복 |
| **IN-2′** 실행 결과의 값 표현(예외 비전파) | `test_IN2p_result_as_value_no_exception[3 시나리오 × 2 어댑터]` | 6 | PASS | `run_full`·`run_phase1`·`run_phase2` 어느 것도 경계 밖 예외 전파 없음. `node_error`에서 두 어댑터 모두 `NODE_ERROR:` State 값으로 인코딩 |
| **IN-3′** caller-owned checkpoint의 phase-boundary resume | `test_IN3p_caller_owned_checkpoint_resume[2 시나리오 × 2 어댑터]` | 4 | PASS | checkpoint 값이 JSON round-trip 성공·`visited`/`depth` 등 실행기 내부 표현 누출 0. 별도 프로세스가 로드해 `run_phase2` → 결과 == 단발 `run_full`. **이전 재귀 호출 스택을 전혀 복원하지 않고 완전히 새 재귀로 재개**됨을 확인 |
| | `test_IN3p_adapter_does_no_persistence_io` | 1 | PASS | 두 어댑터 소스에 영속화 호출 0 |
| **IN-4′** 교체 시 Kernel/HQ 코드 0 변경 | `test_IN4p_swap_zero_kernel_hq_change` | 1 | PASS | `caller.py`·`domain/*`에 `adapters`/`langgraph`/`langchain` import 0. `git grep` core/hqs 0건 |
| | `test_IN4p_hashes_identical_across_lineages` | 1 | PASS | recursive·langgraph 실행 후에도 `caller.py`+`domain/*` SHA-256 불변 |
| **IN-5′** 라이브러리 경계 격리 | `test_IN5p_langgraph_import_single_module` | 1 | PASS | `langgraph` import는 `adapters/langgraph.py` 1개 모듈 |
| | `test_IN5p_domain_and_recursive_import_without_langgraph` | 1 | PASS | `sys.modules['langgraph']=None` 차단 하에서도 recursive 전체 실행 성공 |
| | `test_IN5p_no_library_types_in_state` | 1 | PASS | 최종 State에 라이브러리 타입 인스턴스 0 |
| | `test_IN5p_recursive_and_langgraph_do_not_share_code` | 1 | PASS | 두 어댑터 상호 import 0, 공유는 `domain.*` 한 곳 |
| **IN-6′-1** 정적 의존성 | `test_IN6p_1_recursive_stdlib_and_domain_only` | 1 | PASS | import root ⊆ `{__future__, copy, domain}` |
| **IN-6′-2** 구조 부재(신설) | `test_IN6p_2_recursive_has_no_class_or_queue` | 1 | PASS | `class` 정의 0, `collections` import 0, 코드 바디에 `deque` 사용 0 |
| | `test_IN6p_2_worklist_sibling_has_class_and_queue_for_contrast` | 1 | PASS | 대조 — L-A(`worklist.py`)는 실제로 `class`+`deque`를 씀(소스 텍스트 읽기, import 없음) |
| **IN-6′-3** 실행 메커니즘 실측(신설) | `test_IN6p_3_advance_is_self_recursive_by_source` | 1 | PASS | `_advance` 함수 바디 안에 자기 자신을 호출하는 `Call` 노드 존재(AST) |
| | `test_IN6p_3_recursion_depth_is_deep_not_constant[clean/data_gap/node_error]` | 3 | PASS | 실측 최대 콜스택 깊이 = **14**(임계값 ≥12) — 그래프 실행 경로 길이에 비례하는 다층 재귀 |
| | `test_IN6p_3_worklist_run_is_iterative_not_self_recursive` | 1 | PASS | 대조 — L-A `run()`은 `while` 루프를 포함하고 자기 자신(`self.run`)을 재귀 호출하지 않음 |

## 4. 구현 중 발견·수정된 결함 (투명성 기록)

초기 구현에서 `run_phase2`(checkpoint 재개) 경로에 결함이 있었다: 수렴
Loop의 재진입(`_advance`가 `judge`에서 `bull_case`로 되돌아가는 재귀
호출)이 predecessor 검사를 매 호출마다 다시 통과해야 했는데, phase2는
`visited`가 빈 `frozenset()`에서 시작하므로 `bull_case`의 유일한 정적
predecessor(`collect`)가 그 실행 안에서 한 번도 `visited`에 들지
않는다 — `run_full`에서는 `collect`가 이미 `visited`에 남아 있어 우연히
가려졌던 문제다. `IN-3′`(checkpoint resume, `[clean-recursive]`/
`[data_gap-recursive]`)가 이를 **FAIL로 정확히 잡아냈다**(재개 결과가
1라운드에서 멈추고 단발 실행의 3라운드 결과와 불일치). 원인은 L-A의
`self.start`가 인스턴스 생애 전체에 걸쳐 매 pop마다 무조건 실행 가능
처리되는 것과 동등한 장치가 L-B에는 최초 진입 1회에만 적용돼 있었기
때문 — `starts: frozenset`을 재귀 전체에 스레딩해 "이 `_run` 호출의
시작 노드는 매 재진입마다 predecessor 검사를 생략한다"로 수정해
해소했다(현재 코드에 반영, §3 IN-3′ 전부 PASS로 재검증됨). 이 결함은
L-B 계보의 **독립성 자체를 부정하지 않는다** — 오히려 L-B가 L-A와
다른 스케줄링 표현(재귀 인자 vs 인스턴스 속성)을 쓴다는 것을 보여주는
사례이며, 그 표현 차이 때문에 "시작점 영속 우회"라는 동일한 의미론을
다른 메커니즘으로 재구현해야 했다.

또한 정적 검사 설계 초안에서 `deque` 문자열을 소스 텍스트 전체(모듈
docstring 포함)에서 검색해 오탐(모듈 docstring이 L-A와의 대조 설명을
위해 "collections.deque"라는 단어를 인용)이 발생했다 — 검사 범위를
docstring을 제외한 AST 코드 바디로 좁혀 해소했다(`test_IN6p_2_recursive_has_no_class_or_queue`).

## 5. 이 Evidence가 보이는 것 / 보이지 않는 것

**보이는 것** — `BASELINE.md` v1.17 §16.6 A-IN 5항목 + Reversibility
필수 불변조건이, **worklist(L-A)와도 LangGraph와도 다른 세 번째 실행
메커니즘**(재귀 조합자, 인스턴스·큐 없이 콜스택과 함수 인자만으로 진행)
에서도 도메인 형태 그래프에 대해 동일하게 성립하며, 계보 교체가
Kernel·HQ 코드 0 변경으로 이뤄지고, 각 계보의 구현 문법이 어댑터 경계
안에 갇힘을 **저장소 안의 실행 가능한 통합 테스트**로 확인. 계보
독립성은 정적 import 목록뿐 아니라 **자료구조 부재**(class/큐 없음)와
**실행 메커니즘 자체의 계측**(자기 재귀 호출 + 실측 콜스택 깊이)으로
실증했다 — E5 IN-6의 기계적 복제가 아니다.

**보이지 않는 것 (E6의 한계 — 후속 ADC가 gate 충족 판정 시 고려)**:

1. **결정론적 stub** — 노드가 fixture 기반 순수 함수다(E4/E5와 동일
   한계). Gate (C) 잔여 한계 (i)를 E6은 **해소하지 않는다**.
2. **세 계보 전부 단일 프로세스·단일 언어(Python)** — L-A·L-B·L-LG
   모두 같은 프로세스·같은 인터프리터 안에서 실행된다. "다른 계보"의
   독립성은 실행 메커니즘(자료구조·제어 흐름) 층위에서 실증됐지만,
   프로세스·언어·런타임 경계를 넘는 독립성은 아니다.
3. **seam이 harness 로컬 관례** — `run_full`/`run_phase1`/`run_phase2`는
   프로토타입 테스트 관례이지 확정 계약 시그니처가 아니다(E4/E5 계승).
4. **프로덕션 트래픽 미검증** — Gate (C) 잔여 한계 (iii)를 E6은 해소하지
   않는다.
5. **mid-node resume 미검증** — IN-3′는 phase 경계(C1)만(E4/E5 계승).
6. **독립 관찰 카운팅 미판정** — E6(L-B)이 Gate (B) "독립 관찰 3건"에
   몇 건째로 반영되는지, 비-LangGraph 계보 2개 확보가 완전 완화에
   충분한지는 이 문서가 선언하지 않는다(`ADC-0024` §D-B3·§D-B4의
   판단 몫).

## 6. 판정 — Gate (B) 기여 (선언 아님, 사실 기록만)

| 질문 | 판정 |
|---|---|
| E6이 §16.6 A-IN 5항목 + Reversibility 필수 불변조건을 **세 번째 독립 실행 메커니즘**에서 재현했는가 | **예** — IN-1′~IN-6′ 31개 PASS. L-B는 `langgraph`/서드파티 무의존, 자체 실행 모델(재귀 조합자), L-A·L-LG와 자료구조·실행 메커니즘 모두에서 구조적으로 구분(IN-6′-2·6′-3) |
| E6이 Gate **(B)** `ADC-0019` 재검토 조건 (c)를 **충족**시키는가 | **이 문서가 선언하지 않음** — 비-LangGraph 조건부 분기·Loop 실행 관찰 **2번째 독립 계보(L-B)**를 추가한다. E5(L-A)에 이 관찰을 더하면 비-LangGraph 계보가 2개가 되나, 이것이 `ADC-0024` §D-B4의 "완전 완화" 후속조건 (i)를 충족시키는지는 후속 ADC의 몫 |
| E6이 Gate **(C)** 잔여 한계를 진전시키는가 | **아니오** — (i) 결정론적 stub·(iii) 프로덕션 트래픽 모두 미해소. E6은 Gate (C)를 겨냥하지 않음(승인된 Test Design 범위) |
| E6이 Gate **(A)**(v1 결정 2/5/9/11)를 진전시키는가 | **무관** — Gate (A)는 `ADC-0022`/`ADC-0023`으로 이미 Resolved(BASELINE v1.16) |
| E6이 LangGraph 채택·구현 착수·`IMPLEMENTATION_RULES` 해제·§14 승격 중 무엇이든 발생시키는가 | **아니오** — 전부 후속 절차. E6은 Evidence 기록일 뿐 |

## 7. Traceability

| 문서 / 절 | 관계 |
|---|---|
| `ADC-0024` §D-B4 | (i) "2번째 비-LangGraph 독립 계보(L-B)" 대상. 이 프로젝트가 그 후속조건을 구현·실행 |
| `ADC-0021` §8 Gate (B) | 관찰 1건 추가(비-LangGraph 계보 2개째). 충족/완전 완화 판정은 후속 ADC |
| `RFC-0020` §8.2 Q-I | "직접 구현 최소 그래프 실행기"의 두 번째 사례 |
| E5 `projects/workflow-adapter-nonlanggraph-lineage-v1/EVIDENCE.md` §4 한계 2 | E6이 겨냥한 한계("비-LangGraph 계보 1개뿐"). `domain/*`·`caller.py`·`adapters/langgraph.py` byte-identical 복제 출처 |
| E4 `projects/workflow-adapter-reversibility-v2/EVIDENCE.md` | 도메인·seam·IN-1~IN-5 하네스 구조의 원 출처(E5를 거쳐 계승) |
| `BASELINE.md` v1.17 §16.6 | 검증 대상 문언, 무변경 |
| `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" | 위치·격리 근거 |
| 승인된 Test Design(세션 2026-09-05) | IN-1′~IN-6′(6′-1/2/3 포함) 항목·PASS 기준의 원 설계. 정식 문서 파일로는 미커밋 |
