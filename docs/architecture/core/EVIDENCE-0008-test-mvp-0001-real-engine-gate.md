# EVIDENCE-0008: `test_mvp_0001.py` 무게이트 실제 Engine 호출 — 재설계·검증·해결

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. `EVIDENCE-0007`이 OmniRoute Call-Site Conversion의 차단
사유로 기록한 문제 하나만 다루고, 그 문제의 재설계·실행·검증
결과만 기록한다.

## 1. 문제 — 정확한 분석

### 1.1 대상 테스트와 그것이 검증하는 것

`hqs/development/mvp/tests/test_mvp_0001.py`(수정 전, `EVIDENCE-0007`
§3.1 인용)의 두 테스트.

| 테스트 | 검증 대상 | `call_engine()` mock 여부 |
|---|---|---|
| `test_returns_review_then_test_cases_without_manual_intervention` | `MVP.md` Exit Criteria 원문 그대로 — "입력 코드가 주어지면, 수동 개입 없이 Code Review 결과와 Test Case 제안이 순서대로 반환된다"(반환 dict의 key 순서·비어있지 않음) | **없음** — `run_mvp_0001()`을 mock 전혀 없이 그대로 호출 |
| `test_review_content_reaches_test_execution_as_context` | `workflow.py`의 context 전달 메커니즘(`code_review` 출력이 `test_execution` 프롬프트에 포함되는지) | **spy만** — `backend.call_engine`/`qa.call_engine`을 원본을 그대로 호출하는 wrapper로 감싼다(호출 여부·순서만 관찰, 응답 내용은 조작하지 않음) |

### 1.2 원인

두 테스트 모두 **실제로 `call_engine()`의 현재 backend(`claude` CLI
subprocess)를 호출한다** — `EVIDENCE-0007` §3.1이 실측으로 확인했다
(46~63초 소요, 실제 subprocess 왕복 시간과 일치). 이 관행 자체는
지금까지 안전했다 — `claude` CLI는 이미 이 저장소 전체가 신뢰하고
일상적으로 호출하는 로컬 대상이었기 때문이다. 문제는 이 안전성이
**"`call_engine()`의 backend가 항상 `claude` CLI"라는 암묵적 전제**
위에 있다는 것 — `EVIDENCE-0006`의 OmniRoute Production Engine
Adapter Integration 이후, `hqs/development/mvp/`에는 이제
`call_engine_via_omniroute()`라는 대안 backend도 real path로
존재한다. 향후 `EVIDENCE-0007`이 보류한 Call-Site Conversion이
실제로 승인되면, 이 게이트 없는 테스트가 매 `pytest` 실행마다
**실제 OmniRoute 호출**(최악의 경우 zero-config egress로 실제
외부 provider 호출까지)을 일으키게 된다 — Call-Site Conversion을
가로막는 직접적 차단 사유였다(`EVIDENCE-0007` §6.1 항목1).

**중요**: 이 문서는 Call-Site Conversion 자체를 재개하지 않는다.
`call_engine()`은 여전히 `claude` CLI만 호출하며(무수정),
`agents/*.py`·`workflow_ast_context.py`도 무수정이다 — 이 문서가
고치는 것은 오직 **테스트의 게이팅 방식**뿐이다.

---

## 2. 재설계

### 2.1 Gate 설계 원칙(사용자 지침 2~5 그대로 적용)

- **단순하고 명확한 방식**: 단일 환경변수 `RUN_REAL_ENGINE_TESTS`
  하나만 사용한다(`OmniRoute` 트랙의 이중 게이트와 달리, 여기서는
  이중 게이트가 필요하지 않다 — 대상이 여전히 이미 신뢰된 로컬
  `claude` CLI이며, 이 Gate 자체는 미래에 backend가 무엇으로
  바뀌어도 그대로 유효한 **일반적** on/off 스위치이기 때문이다).
- **기본값은 SKIP, FAIL 아님**: `pytest.mark.skipif`로 구현 —
  환경변수 미설정 시 두 테스트는 명시적으로 SKIP되고, 나머지
  테스트(엔진을 부르지 않는 `test_agent_capability_map_...`)는
  영향받지 않는다.
- **Gate가 하는 일은 on/off뿐**: `call_engine()`이 무엇을 호출할지,
  어떤 provider/model을 쓸지 판단·분기하는 코드는 전혀 추가하지
  않았다 — `os.environ.get(...) != "1"`라는 단일 조건 하나만 있다.
  Routing/Fallback/Budget/Policy에 해당하는 로직은 0줄이다.
- **테스트 자체의 의미는 유지**: Gate 활성화 시 테스트 본문은
  **한 글자도 바뀌지 않았다** — 여전히 `run_mvp_0001()`을 그대로
  호출하고 동일한 assertion을 수행한다. Exit Criteria 검증 의도가
  그대로 보존된다.
- **실제 external provider egress는 기본 금지**: Gate 활성화 시에도
  이 테스트는 `call_engine()`(현재 `claude` CLI)만 호출한다 —
  OmniRoute를 전혀 거치지 않으므로 이 문서의 검증 범위 안에서
  "external provider egress"에 해당하는 새로운 위험은 없다. 이
  Gate가 막으려는 것은 정확히 "**미래에 backend가 바뀌었을 때**
  게이트 없이 그 위험을 물려받는 것"이다(§1.2).

### 2.2 실제 코드 변경

`hqs/development/mvp/tests/test_mvp_0001.py`에 다음만 추가했다.

```python
RUN_REAL_ENGINE_FLAG = "RUN_REAL_ENGINE_TESTS"
_skip_unless_real_engine_gate = pytest.mark.skipif(
    os.environ.get(RUN_REAL_ENGINE_FLAG) != "1",
    reason=(...),
)
```

그리고 두 테스트 함수에 `@_skip_unless_real_engine_gate` 데코레이터를
붙였다. `import os`, `import pytest` 두 줄과 모듈 docstring에 Gate
설명 문단을 추가한 것 외에는 **아무것도 바꾸지 않았다** — 테스트
본문 로직, assertion, `SAMPLE_CODE`, 세 번째 테스트
(`test_agent_capability_map_is_a_literal_dict_with_exactly_mvp_scope`)
모두 무수정.

---

## 3. 검증

### 3.1 Gate 미설정(기본) — SKIP 확인

```
python3 -m pytest hqs/development/mvp/tests/test_mvp_0001.py -v
```

```
test_returns_review_then_test_cases_without_manual_intervention SKIPPED
test_review_content_reaches_test_execution_as_context SKIPPED
test_agent_capability_map_is_a_literal_dict_with_exactly_mvp_scope PASSED

1 passed, 2 skipped in 0.02s
```

**FAIL이 아니라 명시적 SKIP**(사용자 지침 3), 실행 시간 0.02초 —
실제 Engine 호출이 전혀 일어나지 않았음을 시간으로도 확인.

### 3.2 Gate 활성화 — 실제 Engine 경로 검증

```
RUN_REAL_ENGINE_TESTS=1 python3 -m pytest hqs/development/mvp/tests/test_mvp_0001.py -v --durations=5
```

```
test_returns_review_then_test_cases_without_manual_intervention PASSED  (63.25s)
test_review_content_reaches_test_execution_as_context PASSED            (62.33s)
test_agent_capability_map_is_a_literal_dict_with_exactly_mvp_scope PASSED

3 passed in 125.59s
```

**전부 PASS**, 소요 시간(62~63초)이 실제 `claude` CLI subprocess
왕복과 일치 — Gate 활성화 시 여전히 실제 Engine 경로가 온전히
검증됨을 확인(사용자 지침 4).

### 3.3 Development HQ 전체 회귀

| 실행 | 결과 |
|---|---|
| `hqs/development/mvp/tests/`(Python 3.9 비호환 기존 5개 파일 제외, Gate 전부 OFF) | **151 passed, 5 skipped**(이번에 새로 SKIP되는 2개 + 기존 OmniRoute 실제 서버 3개 = 5) |
| 동일 범위, Gate 전부 ON(`RUN_REAL_ENGINE_TESTS=1 RUN_REAL_OMNIROUTE_TESTS=1 I_UNDERSTAND_REAL_EGRESS_RISK=1`) | **156 passed, 0 skipped** |

두 경우 모두 이전(`EVIDENCE-0006`) 기준선인 **156개 테스트 총합과
정확히 일치**한다 — 새로 추가되거나 사라진 테스트가 없다(순수하게
2개 테스트의 기본 상태만 pass→skip으로 바뀌었을 뿐).

### 3.4 회귀 확인 — 기존 안전조건·경계 무손상

| 대상 | 결과 |
|---|---|
| `test_engine.py`(`call_engine()` 자체, 3개) | **PASS**(무변경 재확인) |
| Experimental Thin Caller 프로토타입(`projects/omniroute-thin-engine-caller-v1/tests/`, 이중 게이트) | **27 passed**(무변경 재확인) |
| Case A Boundary + RT-0001 non-trigger(`test_omniroute_engine_boundary.py`, production 모듈) | **7 passed**(무변경 재확인 — 5개 기존 호출부 중 어느 것도 "omniroute" 미참조 포함) |
| `omniroute_engine.py`, `engine.py`, 5개 기존 호출부 | **무수정**(git diff 0) |

### 3.5 안전 조건

- 실제 external provider(OmniRoute 경유) egress: **0건** — Gate
  활성화 실행은 `claude` CLI만 호출했다(§2.1).
- 실제 `~/.omniroute/storage.sqlite`: 이번 작업 전체(재설계+3.1~3.4
  전체 실행)에서 mtime(`1788605986`)·size(`2547712`) 완전 동일
  유지 확인.
- 잔여 프로세스/포트 점유: 확인 결과 없음.

### 3.6 별도 Issue 유지 확인(사용자 지침 6)

`test_workflow_ast_context.py`는 이번 작업 전후 동일하게 Python
3.9 환경에서 `TypeError: unsupported operand type(s) for |: 'type'
and 'NoneType'`로 collection 오류를 낸다(`workflow_ast_context.py`
git diff 0 — 이 문서가 건드리지 않았다). 이 문제는 `EVIDENCE-0007`
§2.1이 이미 별도로 기록한 것과 **동일한, 무관한 기존 조건**이며,
이번 Gate 재설계와 혼동하지 않는다 — 별도 Issue로 유지한다(§4).

---

## 4. Open Issue 재분류

### 4.1 이번 작업으로 해소된 것

| 항목(`EVIDENCE-0007` §8.1) | 상태 |
|---|---|
| `test_mvp_0001.py`의 두 테스트가 이중/단일 게이트 없이 실제 Engine을 호출한다 | **해결** — `RUN_REAL_ENGINE_TESTS` 단일 opt-in Gate로 기본 SKIP, 활성화 시 실제 경로 그대로 검증(§2·§3) |

### 4.2 무변경으로 유지되는 것(새 Issue 아님, 혼동 방지)

| 항목 | 상태 |
|---|---|
| `workflow_ast_context.py` Python 3.9 collection 오류 | **무변경**, 별도 Issue(§3.6) — 이 문서의 해결 대상이 아니다 |
| `EVIDENCE-0007` §6.2가 나열한 Call-Site Conversion 재검토 선행조건(운영자의 실제 OmniRoute 구성 확인 등) | **무변경** — 이번 문서는 그 선행조건 중 "게이트 재설계"(§6.2 항목2) **하나만** 충족시켰다. 나머지(실제 OmniRoute 가용성 확인, Python 3.10+ 환경, Governance 절차 필요 여부 결정)는 여전히 미충족이며, Call-Site Conversion 자체는 이 문서로 재개되지 않는다 |

---

## 5. Governance / Architecture 영향

- Architecture 변경: **없음**. Contract 변경: **없음**. Freeze 변경:
  **없음**.
- `omniroute_engine.py`, `engine.py`, 5개 기존 호출부: **무수정**.
- `ADC-0027`~`ADC-0031`, `ADR-0015`~`ADR-0017`, `EVIDENCE-0001`~
  `EVIDENCE-0007`: **무수정**.
- 수정한 파일: `hqs/development/mvp/tests/test_mvp_0001.py` 1개
  (Gate 추가만, 테스트 로직 무변경). 신규 파일: 이 Evidence 문서
  1개.
- 새 Jarvis측 Routing/Fallback/Gateway/Policy: **구현하지 않았다**
  (§2.1).

---

## 6. Provenance / Reproducibility

- Gate OFF: `python3 -m pytest hqs/development/mvp/tests/test_mvp_0001.py -v`
  → `1 passed, 2 skipped in 0.02s`.
- Gate ON: `RUN_REAL_ENGINE_TESTS=1 python3 -m pytest
  hqs/development/mvp/tests/test_mvp_0001.py -v --durations=5` →
  `3 passed in 125.59s`(62~63초 두 건).
- 전체 회귀(Gate 전부 OFF): `python3 -m pytest hqs/development/mvp/tests/ -q
  --ignore=.../test_cli_integrated.py --ignore=.../test_stage_01.py
  --ignore=.../test_stage_04.py --ignore=.../test_workflow_ast_context.py
  --ignore=.../test_workflow_integrated.py` → `151 passed, 5 skipped`.
- 전체 회귀(Gate 전부 ON): 위와 동일 커맨드에
  `RUN_REAL_ENGINE_TESTS=1 RUN_REAL_OMNIROUTE_TESTS=1
  I_UNDERSTAND_REAL_EGRESS_RISK=1` 추가 → `156 passed`.
- Experimental 프로토타입: `RUN_REAL_OMNIROUTE_TESTS=1
  I_UNDERSTAND_REAL_EGRESS_RISK=1 python3 -m pytest
  projects/omniroute-thin-engine-caller-v1/tests/ -q` → `27 passed`.
- Case A/RT-0001 경계: `python3 -m pytest
  hqs/development/mvp/tests/test_omniroute_engine_boundary.py -v` →
  `7 passed`.
- 실제 `~/.omniroute` 확인: 작업 전후 `stat -f "mtime=%m size=%z"
  ~/.omniroute/storage.sqlite` 동일값(`1788605986`/`2547712`) 반복
  확인.

## Self Review

- 2개 테스트와 그것이 검증하는 Exit Criteria를 정확히 분석했는가 —
  **Pass**(§1.1).
- 기존 테스트 의미를 유지하며 기본 실행에서 실제 Engine/egress를
  막았는가 — **Pass**(§2.1, §3.1 — 테스트 본문 무변경, 기본
  SKIP 확인).
- Gate를 단순하고 명확하게(환경변수) 구현했는가, 미설정 시 FAIL이
  아니라 SKIP인가 — **Pass**(§2.2, §3.1).
- Gate 활성화 시 실제 Engine 경로를 검증할 수 있는가, 테스트 코드에
  Routing/Fallback/Budget/Policy를 추가했는가 — **Pass**(실제 경로
  검증됨, §3.2) / **아니오**(§2.1 — 추가 로직 0줄).
- 실제 external provider egress가 발생했는가 — **아니오**(§3.5 —
  `claude` CLI만 호출, OmniRoute 미경유).
- Python 3.9/`workflow_ast_context.py` 문제와 혼동했는가 —
  **아니오**(§3.6, §4.2에서 명시적으로 분리).
- Gate OFF/ON 각각 실제 실행해 기대 동작을 확인했는가 — **Pass**
  (§3.1, §3.2).
- Development HQ 전체 회귀를 수행했는가 — **Pass**(§3.3, 156개
  총합 일치 확인).
- `test_engine.py`, 27/27, Case A Boundary, RT-0001 non-trigger가
  깨지지 않았는가 — **Pass**(§3.4).
- 문제를 "해결"로 판정할 근거가 있는가 — **있다**(§4.1 — 재설계·
  실행·검증 전부 완료, 회귀 없음).
- Architecture/Contract를 변경했는가 — **아니오**(§5).
- Call-Site Conversion 자체를 재개했는가 — **아니오**(§4.2에서
  명시적으로 구분).
- commit/push/PR을 수행했는가 — **아니오**.
