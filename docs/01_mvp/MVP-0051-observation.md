# MVP-0051 Observation (Phase 10 Prototype #2)

**문서 성격**: 실제 실행 기록(Evidence). `MVP-0050`(Prototype #1, Failure)
실패 원인을 분석한 뒤, 그 원인을 겨냥한 두 번째 Capability 지시문 최소
수정을 real Engine으로 검증한 기록이다. Prompt Specification을 도입하지
않았다. Architecture/Contract는 바꾸지 않았다.

## 1. Prototype #1(MVP-0050) 실패 원인 분석

`MVP-0050`은 지시문에 "minor/style-level observation도 이슈로 취급하라"는
문장을 추가했다. 결과는 CLEAN_CODE marker 등장률 1/3 → 0/3으로 악화했다.

원인:

- `backend_agent_code_review()`의 원래 지시문은 처음부터 "Review the
  following code and describe issues in prose **(bugs, risks, style)**"
  라고 style까지 적극적으로 언급하라고 요청한다 — 즉 어떤 코드를 줘도
  프로세스 자체가 사소한 관찰(타입 강제 없음, 테스트 없음 등)을 텍스트로
  적게 되어 있다.
- 그런데 "이슈 없음" 판정(`NO_ISSUES_MARKER`)은 그 style 언급들을
  빼고 "정말 문제가 있는가"만 봐야 하는 **별도 기준**이 필요한데,
  원래 지시문에는 그 두 기준을 나누는 문장이 없었다 — "no real
  issues"라는 표현만으로는 style 언급을 했으면서도 "issue는 없다"고
  판단해야 하는지 모호했다.
- Prototype #1은 이 모호함을 "issue의 범위를 넓히는" 방향(style도
  issue로 취급)으로 풀었다 — 결과적으로 이미 style을 습관적으로
  적던 Engine이 그 style 언급을 "issue 있음"으로 더 적극적으로
  귀결시켰다. **방향이 반대였다**: 필요했던 것은 "issue의 정의를
  좁혀 style/제안을 issue에서 제외하는 것"이었는데, Prototype #1은
  반대로 넓혔다.

## 2. Prototype #2 — 판정 조건 명시 (marker 강제 아님)

marker 자체를 더 강하게 요구하는 대신, **"real issue"가 무엇인지를
명확히 정의**하는 문장 하나로 instruction을 최소 수정했다(기존 문장
순서·나머지 지시·함수 시그니처는 무변경):

```
"A real issue is a concrete defect that would cause wrong output, a "
"crash, or a violation of the function's own stated behavior — "
"improvement ideas (add validation, add tests, add docs, style "
"preferences) are not real issues by themselves. "
```

그리고 마지막 문장을 "no real issues" → "no real issues **by that
definition**"으로 바꿔, 방금 정의한 기준을 명시적으로 참조하게 했다.
Prompt Specification/Contract를 설계하지 않았다 — 여전히 단일 지시문
문장 추가/수정 1회, `call_engine()` 1회 호출 그대로다.

## 3. Baseline — 기존 Use Case/입력 유지

`PHASE10-PROMPT-SPECIFICATION-AUDIT-0001.md`·`MVP-0050`과 동일한 입력을
그대로 재사용했다: `CLEAN_CODE`(`MVP-0027-observation.md` 원 출처),
`SAMPLE_CODE`(`test_mvp_0001.py`).

## 4. BEFORE (원 Baseline, 기존 Evidence 재사용 — 재실행 안 함)

Prototype #1의 AFTER(0/3, 이미 악화된 상태)가 아니라, **원래 지시문의
Baseline**(`PHASE10-PROMPT-SPECIFICATION-AUDIT-0001.md` §3)을 BEFORE로
쓴다:

| 입력 | 기대 | BEFORE |
|---|---|---|
| CLEAN_CODE | marker 등장 | **1/3** |
| SAMPLE_CODE | marker 미등장 | 3/3 (정상) |

## 5. AFTER — 동일 조건 재실행 (real Engine, 3+3회)

| 입력 | 기대 | run 1 | run 2 | run 3 | AFTER |
|---|---|---|---|---|---|
| CLEAN_CODE | marker 등장 | True | True | True | **3/3** |
| SAMPLE_CODE | marker 미등장 | False | False | False | 3/3 (정상 유지) |

## 6. BEFORE/AFTER 비교

| | BEFORE | AFTER | 변화 |
|---|---|---|---|
| CLEAN_CODE marker 등장률 | 1/3 | 3/3 | **개선** |
| SAMPLE_CODE marker 미등장률(정상) | 3/3 | 3/3 | 유지(위양성 없음) |

## 7. 회귀 확인

```
$ python3 -m pytest development-hq/mvp/tests -q
36 passed in 66.03s
```

## 8. 판정 (사전 정의 기준)

| 기준 | 결과 |
|---|---|
| **Success**: AFTER CLEAN_CODE marker 등장률이 BEFORE보다 개선되고, SAMPLE_CODE 위양성 없음, 회귀 없음 | **충족** |
| **Failure**: AFTER가 BEFORE보다 악화되거나 위양성/회귀 발생 | 해당 없음 |
| **Inconclusive**: BEFORE/AFTER 차이를 판단할 수 없음 | 해당 없음 |

**Success.** 지시문에서 marker 자체를 더 강하게 요구하지 않고 "real
issue"의 판정 기준만 명확히 정의하는 것으로, 이번 표본(n=3)에서
반복성이 1/3 → 3/3으로 개선됐다. 변경을 그대로 채택했다(되돌리지
않음).

## 9. 한계 (억지로 확대 해석하지 않음)

- 표본이 각 3회로 작다 — "완전히 결정적(deterministic)"이 됐다고
  확정하지 않는다. 3/3은 이번 표본에서의 결과일 뿐이다.
- CLEAN_CODE/SAMPLE_CODE 2개 입력에서만 검증했다 — "실이슈"와
  "제안"의 경계가 더 모호한 제3의 입력(예: 이슈인지 스타일인지
  경계에 걸친 코드)에서는 재검증되지 않았다.
- Investment 도메인 등 다른 Capability에는 이 변경을 적용하지
  않았다(범위 밖).

## Architecture/Contract 변경 여부

**없음.** 함수 시그니처, 반환 타입, 호출 형태(`call_engine()` 1회)
전부 무변경. Prompt Specification을 설계·도입하지 않았다. 새
Capability/Agent를 추가하지 않았다.

## Governance

RFC/ADC/ADR 불필요 — Capability Logic Improvement이며 `MVP-0025/0027/
0047/0049`와 동일한 성격(지시문 최소 수정)의 Capability Loop 범위
안에서 수행했다. Prompt Specification 필요성은 이번 성공으로 오히려
약화된다 — marker 반복성 문제가 입력 구조화 없이 지시문 정의 명확화
만으로 해결됐다.

## Self Review

- Architecture/Contract를 변경했는가 — **아니오**.
- Prompt Specification을 도입했는가 — **아니오**.
- 완결된 project를 수정했는가 — **아니오** — Development HQ Platform
  Capability(`agents.py`)만 대상으로 했다.
- 실패한 검증을 성공으로 표현했는가 — **아니오** — 실제로 개선됐고,
  §9에서 한계를 별도로 명시했다.
- 실패 시 추가 Prompt 반복을 시도했는가 — **아니오, 해당 없음**
  (이번 시도가 Success로 판정됨).
- RFC/ADC/ADR을 작성했는가 — **아니오**.
