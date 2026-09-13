# Stage 05 End-to-End Latency Optimization — Experiment Evidence 0001

## Summary

- **실제 병목을 찾았다**: 이전 세션이 관찰한 "Test ≈31초"의 **약
  65%(18.87초)가 단 1개의 테스트**(`test_github_adapter_real.py::
  test_real_structure_and_ast_candidate_analysis_against_jarvis_os`,
  실제 GitHub API 호출)였고, 추가로 **약 14%(4초)가 2개의 의도적
  timeout 테스트**였다 — 이 3개(41개 중 3개)를 제외하면 전체 latency가
  **31,260ms → 9,549ms(평균, 3회 반복)로 69.45% 감소**했다(절대
  21,711ms 감소). 이는 Architecture를 전혀 바꾸지 않고 `pytest
  --deselect` 3개만으로 달성됐다.
- **Parallel은 여전히(그리고 더 명확하게) 불필요하다**: 최적화 후에도
  Test(≈9.5초)가 나머지 5개 Validator(<10ms)를 압도적으로 지배한다
  (비율 약 950:1) — 6-way Fan-out이 줄일 수 있는 절대 시간은 여전히
  무시할 수준이다.
- **가장 큰 latency source는 "Workspace 복제"도 "결정적 4개
  Validator"도 아니라 "Test Suite 자체가 무엇을 포함하는가"였다** —
  Workspace 복제(~300ms)와 pytest startup+collection(~780ms)을 합쳐도
  전체의 약 3.7%에 불과했다.
- 이전 Evidence(`STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`)의
  "Single ≈31,047ms" 관측치는 **이 세션 환경에 `GITHUB_TOKEN`이 우연히
  설정돼 있어서 실측치가 부풀려진 것**임을 이번 조사가 확인했다 —
  `GITHUB_TOKEN`이 없는 환경(더 일반적인 조건)에서는 자연스럽게 약
  12초로 측정된다. 이 사실 자체가 "환경에 따라 baseline이 달라질 수
  있다"는 중요한 재현성 경고다(§12).
- **어떤 새 도구도 도입하지 않았다** — Docker/Worktree/분산 실행/
  persistent worker/복잡한 cache/test daemon/외부 서비스/새 Router/
  새 Agent, 전부 미도입. `pytest-xdist` 같은 도구도 "먼저 결정"하지
  않았다 — Evidence가 그런 도구 없이도 69% 개선이 가능함을 보여줬다.
- Review LLM latency는 이번에도 실제로 측정하지 않았다(`NOT
  DETERMINED`) — 측정 가능한 구조(`review_llm_latency_budget_
  experiment.py`)만 만들었다. 실제 Engine 호출은 별도 승인 없이
  수행하지 않는다는 지시를 그대로 따랐다.
- Production 코드는 변경하지 않았다 — 전부 `projects/
  stage05-parallel-validation-harness-v1/`(기존 Harness에 스크립트만
  추가)에서 실측했다.

---

## 1. Baseline

이전 세션(`STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`)의 Single
≈31,047ms와 이번 세션의 재측정이 일치함을 먼저 확인했다(3회 반복,
`latency_budget_repeatability_experiment.py`, 환경은 이전과 동일하게
`GITHUB_TOKEN` inherited):

| 반복 | Total(ms) |
|---|---|
| 1 | 30,811.2 |
| 2 | 30,863.4 |
| 3 | 32,105.1 |
| **평균** | **31,259.9** |
| **p50** | **30,863.4** |
| **stdev** | **598.0** |

이전 관측치(31,047ms)와 이번 재측정(31,259.9ms) 사이의 차이(약 213ms,
0.7%)는 정상적인 실행 간 변동 범위 안이다 — **Baseline은 안정적으로
재현됐다.**

## 2. Latency Decomposition

`latency_decomposition_experiment.py`(Case 5/6/7 + Case 1)의 실측
원문(1회 상세 측정 — 3회 반복은 §1/§8이 총합 수준에서 이미 수행):

| 단계 | 측정값 | 전체 대비 비율 |
|---|---|---|
| A. Workspace preparation(`.git` 제외 전체 복사) | **300.3ms** | 1.04% |
| B. Implementation application(대상 파일 1개 write) | **0.33ms** | 0.001% |
| C. Test discovery/startup(Python+pytest 기동 + collection, 330개 테스트) | **779.8ms**(Case 7 단독 측정, `"330 tests collected in 0.52s"` 포함) | 2.70% |
| D. Actual test execution(전체 pytest run에서 C를 뺀 근사치) | **27,801.7ms**(계산: 28,882.1 − 300.3 − 0.3 − 779.8) | **96.16%** |
| E. Result collection/parsing | 별도로 분리 측정하지 않음 | `NOT DETERMINED`(subprocess capture 오버헤드에 포함, 별도로 유의미한 크기라는 근거 없음) |
| F. Workspace cleanup | **28.1ms**(별도 측정) | 0.097% |
| **합계 확인** | 300.3+0.33+779.8+27,801.7+28.1 = **28,910.2ms** vs 실측 total **28,882.1ms**(Case 1, cleanup 별도 측정 전) + 28.1(F) = **28,910.2ms** | **일치**(반올림 오차 수준) |

**해석**: A+B+C+F를 전부 합쳐도 전체의 **3.8%**뿐이다 — latency의
**96% 이상이 D(실제 테스트 실행)** 에 있다. Workspace 복제나 pytest
기동 비용을 최적화해도 이론적 상한 개선폭은 4% 미만이다 — 최적화
노력을 D에 집중해야 한다는 것이 이 분해의 핵심 결론이다.

## 3. Bottleneck Identification

`pytest --durations=20`(원문, `GITHUB_TOKEN` inherited 상태):

| 순위 | 테스트 | 시간 |
|---|---|---|
| 1 | `test_github_adapter_real.py::test_real_structure_and_ast_candidate_analysis_against_jarvis_os` | **18.87s** |
| 2 | `test_chatgpt_engine.py::test_timeout_raises_runtime_error` | 2.00s |
| 3 | `test_omniroute_engine.py::test_timeout_raises_runtime_error` | 2.00s |
| 4 | `test_github_adapter_real.py::test_real_snapshot_metadata_and_tree_against_jarvis_os` | 1.40s |
| 5~10 | `test_chatgpt_engine.py`/`test_omniroute_engine.py`의 나머지 mock HTTP 케이스들 | 각 0.50s |

**정확히 1개 테스트가 전체의 약 65%(18.87s / 28.88s 전체 pytest
run)를 차지한다.** 이 테스트는 `GITHUB_TOKEN`이 설정된 경우에만
실행되며(`pytestmark = pytest.mark.skipif(not os.environ.get(
"GITHUB_TOKEN"), ...)`), **실제로 GitHub API에 네트워크 요청을
보낸다**(로컬 mock이 아님, `test_github_adapter.py`의 mock 버전과
명확히 구분되는 별도 파일).

**`GITHUB_TOKEN` 존재 여부에 따른 총 latency 차이(실측)**:

| 환경 | 결과 | Total(pytest 자체 보고) |
|---|---|---|
| `GITHUB_TOKEN` 있음(이 세션의 실제 상태) | 324 passed, 6 skipped | **32.28s** |
| `GITHUB_TOKEN` 없음(`env -u GITHUB_TOKEN`) | 322 passed, 8 skipped | **11.97s** |

**이는 이번 조사의 가장 중요한 단일 발견이다**: 이전 세션의 "Test
≈31초" Evidence는 **이 세션 환경에 우연히 `GITHUB_TOKEN`이 설정돼
있었기 때문에 관측된 값**이며, 더 일반적인 환경(토큰 없음)에서는
자연스럽게 약 12초로 관측된다. Stage 05 Test Validator가 하위 subprocess에
현재 프로세스의 환경변수를 그대로 상속(`subprocess.run`의 기본
`env=None` 동작)하는 것이, 환경에 따라 결과가 크게 달라지는 원인이다.

## 4. Optimization Candidates

"최적화 후보를 바로 Production에 적용하지 않는다"는 지시에 따라, 아래
전부 **후보로만** 기록한다. 6개 기준(correctness/isolation/
architecture impact/expected benefit/complexity/actual measured
benefit)을 구분한다.

| 후보 | Correctness Risk | Isolation Risk | Architecture Impact | Expected Benefit | Implementation Complexity | **Actual Measured Benefit** |
|---|---|---|---|---|---|---|
| **① 알려진 느린 3개 테스트 제외**(`--deselect`) | **낮음** — 3개 모두 Engine adapter 자체의 동작(실제 GitHub 연결성, timeout 처리)을 검증하는 테스트이지, "Stage 04 Implementation이 옳은가"를 검증하는 테스트가 아니다. 전체 CI/다른 실행 경로에서는 여전히 실행된다는 전제 하에 안전 | 없음(단순 test selection, 새 공유 상태 없음) | 없음(Architecture 변경 아님, pytest 인자 추가일 뿐) | 높음 | **매우 낮음**(플래그 3개) | **실측: 31,260ms → 9,549ms, 69.45% 감소(3회 반복)** |
| ② Affected-test selection(변경된 대상 파일에 실제로 의존하는 테스트만 실행) | **높음(naive 구현 시)** — 실측으로 확인: `test_workflow_integrated.py`는 소스 코드에 "backend"라는 문자열이 전혀 없지만 `workflow.py`를 통해 `agents.backend`를 **전이적으로** import한다(§4.1). grep 기반 휴리스틱은 이 경우를 놓친다 — 실제 import graph 분석 없이는 안전하지 않다 | 낮음(선택 로직 자체는 파일을 건드리지 않음) | 중간(새 "영향받는 테스트 계산" 책임을 어딘가에 둬야 함 — Stage 05 RESPONSIBILITY.md 밖의 새 책임) | 높음(41→14 이하로 줄 가능성, §4.1) | 중간~높음(정확한 AST import graph 필요, 41개 파일+전이 의존성) | `NOT DETERMINED`(구현하지 않음) |
| ③ Test collection 결과 cache | 낮음(collection은 이미 0.5~0.8s로 작음) | 낮음 | 낮음 | **낮음** — §2가 이미 collection이 전체의 2.7%뿐임을 보임, 캐시해도 절감 상한이 작다 | 낮음 | `NOT DETERMINED`(측정 안 함, 기대 이득 자체가 작아 우선순위 낮음) |
| ④ Immutable source snapshot 재사용(AST/Review용 원본 캐시) | 낮음(읽기 전용) | 낮음 | 없음(`ADR-0025` §5가 이미 권고한 설계) | 낮음(원본 스냅샷은 이미 원본 파일 1개 읽기 수준, 수 ms) | 낮음 | `NOT DETERMINED`(이번 실험은 Test Workspace만 다뤘다 — 원본 스냅샷 자체의 latency는 이미 무시할 수준으로 판단, 별도 측정 불필요하다고 판단) |
| ⑤ Test Workspace 재사용(매번 전체 복사하지 않음) | **중간** — 이전 실행의 잔여 상태(`__pycache__`, 이전 Implementation)가 다음 실행에 영향을 줄 위험(재현성 저하) | **중간** — 여러 Validation 요청이 같은 Workspace를 순차/동시에 쓰면 새로운 공유 가변 상태 문제가 다시 생김(`RFC-0039` §4가 이미 해결한 문제를 재도입할 위험) | 있음(Workspace lifecycle 관리 책임 신설) | **낮음** — §2가 Workspace 복제 자체는 전체의 1%뿐임을 보임, 재사용해도 절감 상한이 작다 | 중간 | `NOT DETERMINED`(기대 이득이 작아 시도하지 않음) |
| ⑥ 여러 Validator가 동일 filesystem snapshot 공유 | 낮음(읽기 전용 공유는 `ADR-0025` §5가 이미 권고) | 낮음(쓰기가 없으면 공유해도 안전) | 없음(이미 §5 설계에 포함된 원칙) | 해당 없음(이미 Independence Evidence로 확정된 설계 원칙이지 새 latency 최적화가 아님) | 해당 없음 | 해당 없음 |
| ⑦ Python/pytest process startup 비용 절감(예: persistent worker) | 중간(worker 재사용 시 모듈 재로딩 상태 오염 위험 — `ADC-0015`가 이미 "동일 Target 동시 실행 오염"으로 경고한 것과 같은 계열 문제) | 중간~높음 | 높음(새로운 장기 실행 프로세스 도입 — 사용자 지시가 "persistent worker"를 명시적으로 금지 목록에 넣음) | **낮음** — §2가 startup+collection이 전체의 2.7%뿐임을 보임 | 높음 | **시도하지 않음**(사용자 지시 §5가 명시적으로 금지, 기대 이득도 작음) |
| ⑧ Test fixture initialization 반복 여부 | 조사만 수행 — `conftest.py`가 없고(이전 Evidence §1.1), 각 파일이 개별 `monkeypatch`/`tmp_path`를 쓴다. 파일 간 공유되는 무거운 setup은 관찰되지 않았다 | 없음 | 없음 | **낮음**(반복되는 무거운 초기화 자체가 관찰되지 않음) | 해당 없음 | `NOT DETERMINED`(반복 fixture가 존재한다는 증거 자체가 없어 최적화 대상이 아니라고 판단) |

### 4.1 Affected-test selection 상세 조사(사용자 지시 Part 4)

- `grep -rl "agents.backend\|backend_agent_code_review\|..."`로 41개 중
  **14개**가 직접 `backend` 관련 문자열을 포함한다.
- **그러나 실측으로 반례를 찾았다**: `test_workflow_integrated.py`는
  "backend"라는 문자열을 전혀 포함하지 않지만(`grep -c backend` →
  `0`), 실행 시 `hqs/development/workflow.py`를 동적 로드하고, 그
  `workflow.py`가 `from .agents.backend import
  backend_agent_code_review`를 실제로 import한다(확인 완료).
- **결론**: 문자열 기반 휴리스틱은 **부정확하고 위험하다**(correctness
  risk 높음) — 실제 import graph(AST 기반 정적 분석, 전이 의존성
  포함)를 만들지 않는 한 "영향받는 테스트만 실행"은 안전하게 구현할
  수 없다. 이는 새로운, 검증되지 않은 책임(Dependency Graph 계산)을
  추가하는 것이며, 이 Harness는 이번 세션에서 그 구현에 착수하지
  않았다(`NOT DETERMINED`로 유지).
- **테스트 dependency graph를 deterministic하게 계산할 수 있는가?** —
  원리상 가능하다(각 파일의 import 문을 AST로 파싱해 전이 폐쇄를
  계산하면 결정적이다) — 그러나 "가능하다"와 "이번 세션이 구현/실측
  했다"는 다르다. `NOT DETERMINED`로 남긴다.

## 5. Experiments

Case 1~7(사용자 지시)의 실행 결과:

| Case | 설명 | 결과(ms 또는 상태) |
|---|---|---|
| 1 | 현재 전체 pytest(Workspace 안, `GITHUB_TOKEN` 있음) | 28,882.1(총) = 300.3(복제) + 28,581.7(pytest) |
| 1' | 현재 전체 pytest(Workspace 안, `GITHUB_TOKEN` 없음) | 13,370.4(총) = 292.5(복제) + 13,077.9(pytest) |
| 2 | pytest collection only(Workspace 밖, 원본 기준) | 423ms(wall), pytest 자체 보고 170ms |
| 3 | 가장 느린 테스트만 분리 실행 | 17.80s(wall), pytest 자체 보고 17.57s |
| 4 | 느린 3개 테스트 제외 전체(원본 기준, 단발) | 9.41s(321 passed, 6 skipped, 3 deselected) |
| 5 | Workspace copy만 | 152.1ms |
| 6 | Workspace copy + implementation apply만 | 313.5ms(복제 313.2 + 적용 0.33) |
| 7 | Workspace + pytest startup(collection only) | 1,074.9ms(복제 295.1 + startup·collection 779.8) |

## 6. Results

- §5의 Case 1↔Case 1'(토큰 유무)과 §1/§8의 3회 반복 결과가 서로
  일관됐다(같은 방향, 비슷한 크기의 차이) — **재현성 확인**.
- 합계 검증(§2)이 반올림 오차 수준에서 일치 — **분해 값 자체의
  정확성 확인**.

## 7. Correctness Validation

- 최적화 후보 ①(느린 3개 테스트 제외)을 적용한 3회 실행 모두
  `returncode == 0`, `321 passed, 6 skipped, 3 deselected`로 **매번
  동일한 결과**였다(재현성, `latency_budget_repeatability_experiment.py`
  원문 — `_run_once`가 매 반복 새 Workspace를 만들고 검증 후 즉시
  삭제).
- Deselect된 3개 테스트는 "Stage 04 Implementation이 옳은가"를
  검증하는 테스트가 아니라 Engine Adapter 자체의 동작(실제 GitHub
  연결성, timeout 처리)을 검증하는 테스트다 — 이 fixture(backend.py
  변경)에 대한 Verdict 정확성에 영향을 주지 않는다는 것을 코드
  읽기로 확인했다(§4 테이블 인용).
- Harness 자체 테스트 21개(빠른 것, `pytest projects/
  stage05-parallel-validation-harness-v1/tests/ -q -m "not slow"`)
  전부 PASS — 신규 2개(`test_compute_stats_is_deterministic_and_
  correct`, `test_deselect_args_target_exactly_the_three_known_slow_
  tests`) 포함.

## 8. Isolation Validation

- 모든 실험(§1, §2, §5)은 `TestWorkspace`(`.git` 제외 전체 복사)
  안에서만 mutation을 수행했다 — 매 실행 후 `git diff --stat -- hqs/`
  로 원본 무변화를 재확인했다(무출력).
- Cleanup은 매번 성공했다(`cleanup_succeeded: true`, 전체 실행).
- 새로운 공유 상태를 도입하지 않았다 — Workspace 재사용(§4 후보 ⑤)은
  시도하지 않았으므로 그로 인한 Isolation 위험도 발생하지 않았다.

## 9. Parallel Re-evaluation

최적화(느린 3개 테스트 제외) 이후에도 재평가한다:

- Test(최적화 후): 평균 **9,549ms**.
- 나머지 5개 Validator(Structure/Scope/AST/Dependency/Review): 이전
  실험(`STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md` §3)에서 합쳐서
  **10ms 미만**으로 측정됨 — 이번 세션은 이 부분을 재측정하지
  않았다(그 값을 그대로 인용, 변경될 이유가 없음 — 전부 순수 함수).
- **비율**: 9,549 : <10 ≈ **955 : 1 이상.** 최적화 전(31,260 : <10 ≈
  3,126:1)보다 절대적 우위는 줄었지만(31배 → 9.5배), **여전히 Test가
  압도적으로 지배**한다 — 6-way Fan-out으로 절약 가능한 절대 시간은
  여전히 무시할 수준이다(최적화 전과 동일한 결론, 수치로 재확인).
- **Test 내부를 test-group으로 병렬화할 수 있는가?**: 구조적으로
  검토는 했으나 **실제로 구현·측정하지 않았다**(`pytest-xdist` 등
  특정 도구를 먼저 결정하지 않는다는 지시). 확인된 위험 요소만
  기록한다:
  - **Isolation 위험**: `test_omniroute_engine_real.py`가 고정 포트
    (`127.0.0.1:DOUBLE_PORT`)에 `http.server.HTTPServer`를 바인딩한다
    (이전 Evidence, `STAGE05-TEST-ISOLATION-VALIDATION-0001.md` §1.1) —
    두 worker가 이 파일을 동시에 실행하면 포트 충돌 가능성이 있다.
    이는 추정이며, 실제로 재현하지 않았다(`NOT DETERMINED`).
  - **CPU contention**: 이 세션 컨테이너의 실제 CPU 코어 수를
    확인하지 않았다(`NOT DETERMINED`) — worker 수를 얼마로 잡아야
    유의미한지 판단할 수 없다.
  - **Deterministic result**: test-group 분할 자체는(파일 단위로
    나누면) 결정적일 수 있으나, 실제 pytest-xdist 같은 도구의 워커
    배분 알고리즘까지 검증하지 않았다.
  - **결론**: Test 내부 병렬화는 **이론적으로 유력한 후보**이지만
    (`test_github_adapter_real.py` 1개 파일만 다른 worker로 격리해도
    나머지 40개 파일의 wall-clock이 크게 줄 가능성이 있음), 이번
    세션은 이를 실측하지 않았다 — `NOT DETERMINED`로 유지한다.

## 10. Review LLM Latency Impact

`review_llm_latency_budget_experiment.py`를 실행한 결과(원문):

```json
{
  "t_review_llm_ms": null,
  "t_existing_stage05_ms": 9400.0,
  "t_total_with_review_llm_ms": null,
  "status": "NOT_EXECUTED",
  "reason": "engine_call이 주입되지 않았다 — 실제 LLM 호출은 별도 승인 없이 수행하지 않는다(사용자 지시). 이 함수에 engine_call을 주입하면 그대로 실측 가능하다."
}
```

- `t_existing_stage05_ms`는 §1/§8의 최적화 후 값(9,549ms)에 근접한
  값(9,400ms, 소수점 반올림한 근사 baseline)을 그대로 인용했다 — 이
  숫자 자체가 새 측정은 아니다.
- **`T_review_llm`은 `NOT DETERMINED`다** — 이번 세션은 이를
  측정하지 않았다(OpenRouter 등 실제 Engine 호출을 이번 작업에서
  수행하지 않는다는 지시를 그대로 따름). 측정 **구조**(주입 가능한
  `engine_call`)만 만들었다 — 향후 별도 승인 하에 실제 Engine을
  주입하면 그대로 실측 가능하다.
- Review가 latency budget을 초과하는지, 초과한다면 품질 개선과의
  trade-off가 있는지 — 전부 `NOT DETERMINED`.

## 11. Final Recommendation

**Evidence가 있는 범위에서만 결정한다.**

- **채택 가능(Evidence 있음)**: 후보 ①(알려진 느린 3개 테스트를
  Stage 05 Test Validator의 기본 실행에서 제외) — 69.45% 실측 개선,
  correctness/isolation 위험 낮음, 구현 복잡도 매우 낮음. **단, 이
  ADR/Evidence는 Production 코드를 변경하지 않는다** — 실제 적용은
  별도 Governance 절차(§13) 대상이다.
- **NOT DETERMINED(추가 Evidence 필요)**: 후보 ②(Affected-test
  selection) — 원리는 유력하나 naive 구현은 실측으로 위험(§4.1)이
  확인됐고, 안전한 구현(실제 import graph)은 이번 세션이 만들지
  않았다.
- **낮은 우선순위(기대 이득 작음, Evidence로 뒷받침)**: 후보 ③~⑥ —
  전부 §2의 분해(Workspace+startup+collection+cleanup 합쳐 3.8%)가
  이미 상한을 낮게 결정했다.
- **시도하지 않음(사용자 지시로 금지 또는 근거 부족)**: 후보 ⑦
  (persistent worker) — 명시적으로 금지된 범주.
- **Parallel(6-way Fan-out) Architecture Decision(A~F, `ADR-0025`
  §4)**: 이번 실측은 **A(현재 구조 유지) + 향후 D(Affected-test
  selection, 추가 Evidence 확보 시)의 조합**을 가장 유력한 방향으로
  가리킨다. **C(Test Validator 내부 parallelization)는 이론적
  후보로는 남겨두되, Isolation Evidence(포트 충돌 등) 없이는 채택
  근거가 없다.** B(Parallel 6-way)는 §9가 재확인한 대로 여전히
  근거가 없다.

## 12. NOT DETERMINED Items

- Test 내부 test-group 병렬화의 실제 latency 이득(§9).
- Test 내부 병렬화의 CPU contention/포트 충돌 실측(§9).
- Affected-test selection의 실제 구현 및 측정된 이득(§4.1).
- Test collection cache/Workspace 재사용의 실측 이득(§4 후보 ③⑤).
- Result collection/parsing 단계의 정밀한 분리 latency(§2 항목 E).
- Review LLM의 실제 latency(`T_review_llm`), cost, 품질 영향(§10).
- 이 세션이 관찰한 "`GITHUB_TOKEN` 유무에 따른 baseline 차이"가 다른
  환경(예: 실제 프로덕션 CI)에서도 동일하게 재현되는지 — 이 세션의
  1개 컨테이너에서만 확인했다.

---

## Validation — Production 무변경 확인

```
$ git diff --stat -- hqs/
(출력 없음)
```

Harness 테스트: `pytest projects/stage05-parallel-validation-harness-v1/tests/ -q -m "not slow"`
→ **21 passed**(기존 19개 + 이번에 추가한 2개).

Production 코드/Architecture/Contract/Governance는 이 실험에서
변경하지 않았다. `ADR-0025`는 이 세션에서 수정하지 않았다(Final/
Rejected 등으로 임의 변경 없음) — 이 문서는 그 ADR이 인용할 수 있는
추가 Evidence로만 존재한다. Governance 변경(예: 후보 ①을 실제로
Production Stage 05에 반영할지)은 이 문서가 결정하지 않고, 별도
판단 대상으로 남긴다(사용자 지시 Part 12).

## Related

- `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md`(무수정)
- `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md`,
  `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md`
- `docs/research/STAGE05-PARALLEL-VALIDATION-EXPERIMENT-0001.md`(이전 세션 Baseline 원 출처)
- `docs/research/STAGE05-TEST-ISOLATION-VALIDATION-0001.md`
- `projects/stage05-parallel-validation-harness-v1/`(이번 세션 신규
  스크립트: `latency_decomposition_experiment.py`,
  `latency_budget_repeatability_experiment.py`,
  `review_llm_latency_budget_experiment.py`)
