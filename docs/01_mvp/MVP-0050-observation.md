# MVP-0050 Observation

**문서 성격**: 실제 실행 기록(Evidence). `PHASE10-PROMPT-SPECIFICATION-AUDIT-0001.md`
가 발견한 `NO_ISSUES_MARKER` 반복성 한계를, Prompt Specification 없이
Capability 지시문 최소 수정만으로 해결할 수 있는지 실제로 Prototype한
기록이다. Architecture/Contract는 바꾸지 않았다.

## 목적

`backend_agent_code_review()`의 "이슈 없음" 판단 기준에 "minor/style-level
observation도 이슈로 취급하라"는 한 문장만 추가했을 때, 실제로
`NO_ISSUES_MARKER`의 반복성(같은 입력에 매번 안정적으로 등장하는가)이
개선되는지 real Engine 실행으로 확인한다.

## 1. Baseline — 기존 Use Case/입력 재사용

`PHASE10-PROMPT-SPECIFICATION-AUDIT-0001.md`와 동일한 입력을 그대로
재사용했다(신규 입력 생성 안 함): `CLEAN_CODE`(`MVP-0027-observation.md`
원 출처), `SAMPLE_CODE`(`test_mvp_0001.py`).

## 2. BEFORE — 기존 Evidence에서 확인 (재실행 안 함)

`PHASE10-PROMPT-SPECIFICATION-AUDIT-0001.md` §3이 이미 실제 Engine 3회
반복으로 측정한 값을 그대로 Baseline으로 쓴다:

| 입력 | 기대 | BEFORE 결과 |
|---|---|---|
| CLEAN_CODE (실이슈 없음) | marker 등장 | **1/3** |
| SAMPLE_CODE (실이슈 있음) | marker 미등장 | 3/3 (정상) |

## 3. 변경 — Capability 지시문 최소 수정

`backend_agent_code_review()`의 instruction에 다음 한 문장을 추가했다
(그 외 문장·순서·함수 시그니처는 무변경):

```
"Treat minor or style-level observations as issues too — there is no "
"separate 'not a real issue' category. "
```

그리고 마지막 문장을 "no real issues" → "no issues of any kind"로
바꿔 기준을 일치시켰다. Prompt Specification을 도입하지 않았다 — 여전히
`call_engine()` 1회, `code: str` 입력 그대로다.

## 4. AFTER — 동일 조건 재실행 (real Engine, 3+3회)

| 입력 | 기대 | run 1 | run 2 | run 3 | AFTER 결과 |
|---|---|---|---|---|---|
| CLEAN_CODE | marker 등장 | False | False | False | **0/3** |
| SAMPLE_CODE | marker 미등장 | False | False | False | 3/3 (정상 유지) |

CLEAN_CODE run 1~3 응답 말미(발췌)를 직접 확인 — 셋 다 여전히 사소한
관찰(타입 강제 없음, 오버플로 우려 없음 — "documentation/clarity
point, not a functional bug" 등)을 "issue"로 나열한 채 마커 없이
끝났다. 지시문이 요구한 방향(사소한 관찰도 issue로 취급)대로
Engine이 더 적극적으로 반응해, 오히려 마커가 한 번도 등장하지 않게
됐다.

## 5. BEFORE/AFTER 비교

| | BEFORE | AFTER | 변화 |
|---|---|---|---|
| CLEAN_CODE marker 등장률 | 1/3 | 0/3 | **악화** |
| SAMPLE_CODE marker 미등장률(정상) | 3/3 | 3/3 | 유지 |

## 6. 회귀 확인

```
$ python3 -m pytest development-hq/mvp/tests -q
36 passed in 75.68s
```

mock 기반 테스트는 `call_engine()`을 stub하므로 이번 지시문 변경과
무관하게 항상 통과한다(회귀 없음 확인 목적으로만 재실행).

## 7. 판정 (사전 정의 기준)

| 기준 | 결과 |
|---|---|
| **Success**: AFTER의 CLEAN_CODE marker 등장률이 BEFORE보다 개선 | 미충족 |
| **Failure**: AFTER의 marker 등장률이 BEFORE보다 악화되거나 회귀 발생 | **충족 — marker 등장률 1/3 → 0/3** |
| **Inconclusive**: BEFORE/AFTER 차이를 판단할 수 없음 | 해당 없음 |

**Failure.** 지시문 개선만으로는 이번 시도에서 반복성이 개선되지
않았다 — 오히려 악화됐다. 이를 성공으로 표현하지 않는다.

## 8. 조치 — 변경 되돌림

Failure로 판정된 지시문 변경(§3의 두 문장)을 되돌렸다.
`backend_agent_code_review()`의 실제 instruction은 `MVP-0047` 이후
원문과 동일하다 — `git diff` 확인 결과 코드 동작에는 최종적으로
변화가 없고, 이 시도와 결과만 함수 docstring에 한 문단으로 남았다.
시도 자체는 이 커밋의 git 이력에 보존된다.

## Architecture/Contract 변경 여부

**없음.** 함수 시그니처, 반환 타입, 호출 형태(`call_engine()` 1회)
전부 무변경. Prompt Specification을 설계·도입하지 않았다. 새
Capability/Agent를 추가하지 않았다.

## Governance

RFC/ADC/ADR 불필요 — Capability Logic 실험이며 결과 Failure로 코드는
원상 복구됐다. Prompt Specification 필요성도 이번 실험으로 새로
확보되지 않았다(§7, §8) — `PHASE10-PROMPT-SPECIFICATION-AUDIT-0001.md`의
분류 B(Capability Prototype으로 해결 시도) 자체는 유효했으나, 이번
구체적 시도는 실패했다.

## 다음 관찰 조건

- "minor/style-level observation을 이슈로 취급하라"는 방향이 실패했으므로,
  반대 방향(오히려 "이슈 없음" 기준을 더 관대하게 명시)이나 다른
  형태의 지시문 조정이 필요할 수 있다 — 이번 문서는 그 다음 시도를
  선제적으로 설계하지 않는다.
- 반복 횟수 3회(n=3)는 최소 표본이다.

## Self Review

- Architecture/Contract를 변경했는가 — **아니오**.
- Prompt Specification을 도입했는가 — **아니오**.
- 완결된 project를 수정했는가 — **아니오** — Development HQ Platform
  Capability(`agents.py`)만 대상으로 했고, 최종적으로 원상 복구했다.
- 실패한 검증을 성공으로 표현했는가 — **아니오** — §7에서 Failure로
  명시했다.
- RFC/ADC/ADR을 작성했는가 — **아니오**.
