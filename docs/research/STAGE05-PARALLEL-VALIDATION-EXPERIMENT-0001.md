# Stage 05 Parallel Validation Architecture — Experiment Evidence 0001

## Summary

- `projects/stage05-parallel-validation-harness-v1/`를 새로 구현해
  Experiment A(Single vs 6-way Parallel, 3회 반복)와 Experiment B
  (Review Case A/B/C)를 **실제로 실행**했다. 아직 측정하지 않은 항목은
  전부 `NOT DETERMINED`로 표시하며 숫자를 추정하지 않는다.
- **Performance Evidence(실측)**: 3회 반복에서 Parallel이 Single보다
  빠르다는 근거는 **나타나지 않았다** — 평균 total wall-clock이
  Single 31,047ms, Parallel 31,236ms로 오히려 Parallel이 189ms(약
  0.6%) 더 느렸다. Test Validator(평균 약 31초)가 전체 latency를
  압도적으로 지배하고, 나머지 5개는 전부 10ms 미만이었다.
- **Reliability Evidence(실측)**: Failure Isolation 6개 시나리오(6/6
  success ~ all failure) 전부에서, 한 Validator의 실패가 다른
  Validator의 실행을 막지 않음을 확인했다.
- **Review Quality Evidence**: Case A(disabled)/B(deterministic)는
  실행했다. Case C(LLM)는 **실행하지 않았다**(`engine_call` 미주입 —
  OpenRouter 등 실제 호출은 이번 작업의 필수 조건이 아니라는 지시를
  그대로 따름) — 따라서 LLM Review의 품질/false positive/negative는
  전부 `NOT DETERMINED`다.
- **Cost Evidence**: `NOT DETERMINED` — 실제 Engine 비용이 발생하는
  호출을 하지 않았다(Structure/Scope/AST/Dependency/Test는 원래
  Engine을 호출하지 않고, Review는 deterministic/disabled만
  실행했다).
- **Final Architecture Decision**: 이 문서는 결정을 내리지 않는다 —
  `ADR-0025`가 이 실측을 근거로 Independence/Isolation/Aggregation은
  확정(Scoped Accept)하고, Parallel Production Adoption과 Review LLM
  Adoption은 `NOT YET DETERMINED`로 유보했다.
- Production 코드는 변경하지 않았다 — 모든 실측은 `projects/
  stage05-parallel-validation-harness-v1/`(신규, 격리된 위치)에서
  수행했고, 원본 저장소는 매 실행 후 `git diff --stat -- hqs/`로
  무변화를 확인했다.

---

## 1. Architecture Independence Evidence

`RFC-0039`/`ADC-0042`가 추론으로 확정한 독립성 판정을, 이번 세션은
**코드 수준으로 고정**했다(`domain/validators.py`, `domain/review.py`)
— 각 Validator 함수의 시그니처 자체가 `ValidationContext`(또는 +
`ReviewConfig`)만 받도록 만들어, 다른 Validator의 `ValidatorResult`를
인자로 받을 수 없게 했다. `tests/test_harness.py`의
`test_structure_scope_ast_dependency_do_not_read_each_others_results`/
`test_review_does_not_require_other_validator_results`가 이를
`inspect.signature`로 실제로 검증한다(19개 빠른 테스트 중 2개,
전부 PASS).

이는 새로운 Independence 판정이 아니라, `RFC-0039`/`ADR-0025` §5·§9의
판정을 **코드로 강제한 것**이다.

## 2. Test Isolation Evidence

`domain/workspace.py::TestWorkspace`가 `STAGE05-TEST-ISOLATION-
VALIDATION-0001.md`가 확인한 방식(`.git` 제외 전체 복사)을 그대로
구현했다. 실측 확인(`tests/test_harness.py`):

| 테스트 | 확인한 것 | 결과 |
|---|---|---|
| `test_workspace_creates_isolated_copy_outside_source_repo` | Workspace 경로가 원본과 물리적으로 다르고, 복사본 안에 `hqs/development/mvp/tests`가 실제로 존재 | PASS |
| `test_workspace_mutation_does_not_touch_original_repository` | Workspace에 파일을 "오염"시켜도 원본 `hqs/development/mvp/agents/backend.py`와 `git diff --stat -- hqs/`가 무변화 | PASS |
| `test_workspace_cleanup_failure_does_not_raise_and_original_stays_safe` | cleanup 실패(Workspace를 미리 지워 재현)를 구조화된 `WorkspaceCleanupResult`로 흡수, 원본은 여전히 무변화 | PASS |
| `test_apply_implementation_rejects_path_outside_workspace` | `../../etc/passwd` 같은 탈출 경로를 명시적으로 거부 | PASS |
| `test_real_fixture_single_and_parallel_agree_and_repository_untouched`(slow, 63.4초) | 실제 `backend.py` 대상으로 Single/Parallel 각 1회 실행 후 Verdict 일치 + 원본 무변화 | PASS |

**Workspace 생성/Implementation 적용/pytest 실행/cleanup 4단계를
각각 구분**한 것도 실측으로 확인했다 —
`test_run_test_validator_reports_structured_error_on_bad_repo_root`가
Workspace 생성 실패를 `ERROR` + `detail.workspace_creation.succeeded
== False`로 구분해 반환함을 확인했다(다른 3단계와 섞이지 않음).

## 3. Performance Evidence

**Experiment A 실측 결과(3회 반복, `experiment_a.py` 실행 원문)**:

| Run | Mode | Total Wall-Clock(ms) | Test Validator(ms) | 나머지 5개 합(ms, 근사) |
|---|---|---|---|---|
| 1 | Single | 31,409.7 | 31,404.1 | ~5.5 |
| 2 | Single | 30,652.4 | 30,647.2 | ~5.2 |
| 3 | Single | 31,080.3 | 31,076.1 | ~4.2 |
| 1 | Parallel | 33,593.8 | 33,577.5 | ~4.4(중첩 실행) |
| 2 | Parallel | 30,362.9 | 30,345.3 | ~7.3(중첩 실행) |
| 3 | Parallel | 29,753.7 | 29,736.9 | ~5.5(중첩 실행) |

- **평균 Total Wall-Clock**: Single **31,047.5ms**, Parallel
  **31,236.8ms** — Parallel이 오히려 **189.4ms(약 0.6%) 더 느렸다.**
- **결론(실측 그대로)**: 이 3회 반복에서 **"Parallel이 더 빠르다"는
  근거가 나타나지 않았다.** Test Validator(약 30~34초)가 전체
  latency의 99% 이상을 차지해, 나머지 5개(Structure/Scope/AST/
  Dependency/Review, 전부 10ms 미만)를 병렬로 겹쳐 실행해도 절대
  절약 시간이 무시할 수준이었다. Parallel run 1이 오히려 Single의
  모든 run보다 느렸던 것은 `ThreadPoolExecutor`/`ProcessPoolExecutor`
  생성 오버헤드로 추정되나, **원인 자체는 이 문서가 확정하지
  않는다**(`NOT DETERMINED`, 반복 측정 부족).
- **각 Validator latency(개별, 3회 평균, Single 기준)**: Structure
  ≈0.02ms, Scope ≈0.00ms, AST ≈4.4ms, Dependency ≈0.5ms, Test
  ≈31,042ms, Review(SKIPPED) ≈0.00ms.
- **Test Workspace creation latency**: 별도 필드로 측정하지 않았다
  (`detail.workspace_creation.latency_ms`가 각 실행마다 기록되지만,
  이번 실험 결과 JSON에는 요약 latency만 남겼다) — **정확한 평균값은
  `NOT DETERMINED`**(원 raw 데이터는 `/tmp/experiment_a_output.json`
  에 남아있었으나 이 문서 작성 시점 이후 세션 종료 시 소실되므로,
  숫자를 추정해 채우지 않는다. §1.4 별도 측정(`STAGE05-TEST-
  ISOLATION-VALIDATION-0001.md`)에서 tar 복사 자체는 251ms로
  측정된 바 있다 — 이는 별도 실험의 값이며 이번 Experiment A 실행의
  구성요소별 값과 동일시하지 않는다).
- **Test execution(pytest 자체) latency**: Test Validator 전체
  latency(~31초)에서 Workspace 생성(수백 ms 수준으로 추정)을 제외한
  나머지 대부분 — 정확한 분리값은 `NOT DETERMINED`(위와 동일 이유).
- **Process/Thread count**: Single 실행은 순차 함수 호출뿐(추가
  Process/Thread 0개). Parallel 실행은 `ThreadPoolExecutor(max_workers=5)`
  + `ProcessPoolExecutor(max_workers=1)` — 5개 Thread + 1개 Worker
  Process(그 안에서 pytest가 다시 1개 subprocess를 낳음).
- **Memory/CPU 측정**: 수행하지 않았다(선택 사항으로 명시됐던 항목) —
  `NOT DETERMINED`.
- **결과 순서 일관성**: `order_consistent_across_all_runs: true` — 6회
  실행(Single 3 + Parallel 3) 전부 `("structure", "scope", "ast",
  "dependency", "test", "review")` 순서로 정렬됐다(실행/완료 순서와
  무관).

## 4. Reliability Evidence

`failure_isolation_experiment.py` 실행 결과(원문 그대로):

| 시나리오 | Verdict | 관찰 |
|---|---|---|
| 6/6 success | PASS | 6개 전부 실행·수집됨 |
| Review FAIL, 5개 blocking PASS(5/6 success 성격) | **PASS** | Review FAIL이 Verdict를 바꾸지 않음(advisory 정책 실측 확인) |
| Scope만 FAIL(1 validator failure) | FAIL | Structure/AST/Dependency는 정상 실행(차단되지 않음) |
| Test만 실제로 FAIL(깨진 문법, 진짜 pytest collection 실패 재현) | FAIL | 나머지 5개 전부 실행됨(`other_5_still_ran: true`) — 단, 같은 깨진 입력이 AST/Dependency도 함께 FAIL시킴(같은 원인이 여러 결정적 검사에 동시에 걸린 것이지, Test의 실패가 다른 Validator를 막은 것이 아님 — 원인 분리는 아래 §4 해석 참고) |
| 여러 Validator 동시 FAIL(Scope+AST+Dependency, multiple validator failure) | FAIL | 3개 이상 독립적으로 FAIL 검출(`at_least_2_failed_independently: true`) |
| all validator failure(결정적 4개 + Test 전부 깨진 입력) | FAIL | Structure만 PASS(Structure는 "비어있지 않음/Engine 실패 신호 아님"만 보므로 문법 오류를 잡지 못하는 것이 정상 동작 — AST가 문법 오류를 잡는 책임) |

**해석(과장 방지)**: "Test만 FAIL" 시나리오에서 AST/Dependency도
함께 FAIL한 것은 Test의 실패가 그들을 "막아서"가 아니라, **같은 깨진
Implementation을 모든 Validator에게 동일하게 공급했기 때문**이다 —
각 Validator는 독립적으로 그 입력을 보고 각자 판단했을 뿐이다(진짜
Independence의 증거이지 반례가 아니다). Structure가 문법 오류를
잡지 못한 것도 결함이 아니라 설계된 책임 분리다(Structure는 형태만,
AST는 파싱 가능성/Scope 무결성을 본다, `RFC-0039` §2.1/§2.3).

## 5. Review Quality Evidence

`experiment_b.py` 실행 결과(원문):

| Case | 상태 | 추가 latency | 새 defect 발견 | deterministic과 중복 | false positive | false negative |
|---|---|---|---|---|---|---|
| A(disabled) | SKIPPED | 0.001ms | 해당 없음 | 해당 없음 | 해당 없음 | 해당 없음 |
| B(deterministic) | PASS(findings 0건) | 0.509ms | 없음(이번 fixture는 bare except/TODO/no-docstring 없음) | 해당 없음(비교 대상 없음, findings 0건) | 관찰되지 않음(0건) | `NOT DETERMINED`(deterministic 검사가 놓칠 수 있는 결함이 실제로 있는지는 별도 known-bad 샘플 없이는 확인 불가) |
| C(llm) | **NOT_EXECUTED** | `NOT DETERMINED` | `NOT DETERMINED` | `NOT DETERMINED` | `NOT DETERMINED` | `NOT DETERMINED` |

**Final Verdict 변화 여부**: `NOT_APPLICABLE` — Aggregator 정책상
Review는 어떤 Case든 Verdict 계산에 전혀 참여하지 않는다(§Aggregation
Boundary, `ADR-0025` §7). 이는 실측이 아니라 설계상 불변 조건이며,
`tests/test_harness.py::test_aggregator_review_fail_does_not_force_
deterministic_pass_to_fail`/`test_aggregator_review_pass_does_not_
override_deterministic_fail`가 코드로 고정해 두었다(둘 다 PASS).

**LLM Review에 대해 절대 주장하지 않는 것(사용자 지시 재확인)**:
"LLM Review가 필요하다", "LLM Review가 품질을 향상시킨다" — 이번
세션은 LLM Review를 한 번도 실행하지 않았으므로 이 두 주장에 대한
근거가 **전혀 없다.** `domain/review.py`의 LLM Mode는 구조(Adapter,
`engine_call: Callable[[str], str]`)만 실제로 구현·테스트했다
(`test_review_llm_mode_without_engine_call_fails_explicitly_not_
silently`가 미주입 시 조용히 넘어가지 않고 명시적 ERROR를 냄을
확인).

## 6. Cost Evidence

**`NOT DETERMINED`(전체).** 이번 세션의 모든 실행에서 실제 Engine
비용이 발생하는 호출은 0건이다:

- Structure/Scope/AST/Dependency: 원래 Engine을 호출하지 않는
  책임(정적 분석)이므로 비용 개념 자체가 없다.
- Test: pytest subprocess 실행 비용(CPU 시간)은 있으나, 이는 Engine
  비용이 아니라 로컬 컴퓨트 비용이며 이 문서는 이를 "Cost Evidence"로
  집계하지 않는다(사용자 지시의 Cost Evidence는 Review Experiment B의
  맥락 — Engine 호출 비용을 의미하는 것으로 해석).
- Review: Case A/B는 Engine 미호출, Case C는 실행하지 않음(§5).

## 7. Final Architecture Decision

**이 문서는 Final Architecture Decision을 내리지 않는다** — 그것은
`ADR-0025`의 역할이다. 이 문서가 제공하는 것은 그 ADR의 §11(Parallel
Production Adoption Decision Status)·§10(LLM Review Decision Status)
·§12(Validation Required)가 인용하는 **실측 Evidence 원문**뿐이다.

이 문서가 뒷받침하는 결론(ADR-0025와 동일, 재확인):

- Independence/Isolation/Aggregation/Failure Isolation/Review
  Boundary — **실측으로 뒷받침됨**(§1, §2, §4).
- Parallel이 더 빠르다 — **뒷받침되지 않음**(§3, 오히려 반대 방향 관찰).
- Parallel이 비용 효율적이다 — **`NOT DETERMINED`**(§6, 측정 자체가 없음).
- LLM Review가 필요하다/품질을 향상시킨다 — **`NOT DETERMINED`**(§5, 실행 자체가 없음).

---

## Validation — Production 무변경 확인

```
$ git diff --stat -- hqs/
(출력 없음)
$ pytest hqs/development/mvp/tests/ -q     # 기존 Production 테스트 재실행
324 passed, 6 skipped in 29.06s            # 기존 baseline과 동일
```

Harness 자체 테스트: `pytest projects/stage05-parallel-validation-harness-v1/tests/ -q`
— 빠른 19개 PASS(약 2초) + 느린 E2E 1개 PASS(약 63초), 총 20개 전부
PASS.

Production 코드/Architecture/Contract/Governance는 이 실험에서
변경하지 않았다 — 변경 범위는 `docs/architecture/core/ADR-0025`,
이 Evidence 문서, `projects/stage05-parallel-validation-harness-v1/`
(신규 experimental 위치)로 제한된다.

## Related

- `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md`
- `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md`,
  `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md`
- `docs/research/STAGE05-TEST-ISOLATION-VALIDATION-0001.md`
- `projects/stage05-parallel-validation-harness-v1/`
