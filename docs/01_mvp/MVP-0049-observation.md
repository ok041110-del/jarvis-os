# MVP-0049 Observation

**문서 성격**: 실제 실행 기록(Evidence). `GOVERNANCE-REVIEW-0007` §5·
`STOCK-DOGFOODING-REVIEW-0001`(AAPL/NVDA/MSFT, 3/3 재현)이 남긴
"출력 언어 비결정성" Capability 개선 후보를 실제로 Prototype한
Capability Loop 실행 기록이다. Architecture/Contract는 바꾸지 않았다.

## 목적

Capability 지시문에 출력 언어를 강제하는 한 문장을 추가했을 때 실제로
효과가 있는지, 또 기존 동작을 깨지 않는지를 real Engine 실행으로
확인한다. Baseline은 보존하고(git 이력), 최소 변경만 적용한다.

## 1. 대상 선정 — Investment project가 아니라 Development HQ Platform Capability

원 관찰(AAPL/NVDA/MSFT)은 `projects/stock-analysis-*`의 project-local
`agents.py`에서 나왔다. 그러나 이 3개 project는 이미 **Promoted·
완결된 point-in-time Evidence**다(`REFACTORING-TRACK-CLOSURE-0001`
P2-3가 이미 "완결된 Evidence 산출에 쓰인 코드를 사후 변경하지 않는다"
원칙을 확인한 바 있다). 이번 Prototype은 그 대신 **Development HQ
Platform**(`development-hq/mvp/agents.py`)의 `backend_agent_code_review`
Capability를 대상으로 삼았다 — 이미 MVP-0025·MVP-0047이 같은 방식
(지시 문장 1개 최소 추가)으로 반복 개선해 온 대상이며, project-local
완결 Evidence를 건드리지 않는다.

## 2. BEFORE — 재현 시도 (real Engine, 2회)

수정 전 `backend_agent_code_review()`에 `development-hq/mvp/engine.py`
전체(한국어 주석 + 영어 코드 혼재)를 입력으로 2회 독립 호출했다.

| 실행 | 출력 언어 |
|---|---|
| 1회 | 영어 |
| 2회 | 영어 |

**결과: 2/2 일관 — 이 Capability/입력 조합에서는 비결정성이
재현되지 않았다.** 원 관찰(AAPL 한국어 vs NVDA 영어)은 2인칭
역할극 지시문("You are a Fundamental Analyst...") + Investment
도메인 데이터 조합에서 나온 것이며, `code_review`의 3인칭 지시문
("Review the following code...")과는 지시문 스타일이 다르다 — 이
차이가 재현 실패의 원인일 가능성이 있으나, 이번 실행 범위에서는
추정으로 남기고 확정하지 않는다.

## 3. 변경 — 최소 프롬프트 추가

`backend_agent_code_review()`의 지시문에 한 문장만 추가했다:

```
"Respond entirely in English, regardless of the language used in the "
"code's comments or identifiers. "
```

기존 문장 순서·`NO_ISSUES_MARKER` 처리·함수 시그니처(`code: str`)는
전혀 바꾸지 않았다. `git diff` 확인 결과 이 한 문장 삽입 외 다른
변경 없음.

## 4. AFTER — 재검증 (real Engine, 2회)

동일 입력(`engine.py`)으로 수정 후 2회 독립 호출했다.

| 실행 | 출력 언어 |
|---|---|
| 1회 | 영어 |
| 2회 | 영어 |

**결과: 2/2 일관 — 변경 전후 동일(영어).**

## 5. 회귀 확인

```
$ python3 -m pytest development-hq/mvp/tests -q
36 passed in 72.64s
```

기존 36건 테스트 전부 통과 — mock 기반 테스트는 `call_engine()`을
stub하므로 이번 프롬프트 변경과 무관하게 항상 통과하는 것이 맞다
(회귀 없음 확인 목적으로만 재실행).

## 6. 판정

**Before가 이미 일관됐으므로(2/2 영어), 이 Capability/입력 조합에서는
"개선 효과"를 증명할 수 없다.** 그러나:

- 변경이 기존 동작을 깨지 않음을 확인했다(AFTER도 2/2 영어, 테스트
  36건 무회귀) — **최소 침습적이며 안전하다.**
- 원 관찰(Investment 도메인, 역할극 지시문)은 이번 실행으로 재현·
  반증 어느 쪽도 되지 않았다 — **원 현상은 여전히 Investment 도메인
  Capability에 국한된 미해결 관찰로 남는다.**
- 표본이 각 2회로 작음(원 관찰의 3회보다 적음) — 이는 비용을 이유로
  이번 세션이 의도적으로 줄인 표본이며, "비결정성이 없다"를 확정하지
  않는다.

## 7. Success / Failure 기준 (사전 정의)

| 기준 | 결과 |
|---|---|
| **Success**: AFTER 실행에서 출력 언어가 일관되고, 회귀 테스트 전부 통과 | **충족** |
| **Failure**: AFTER 실행에서도 언어가 비일관이거나, 회귀 테스트 실패 | 해당 없음 |
| **Inconclusive**: BEFORE 자체가 이미 일관되어 개선 여부를 판단할 수 없음 | **해당 — 이번 실행의 실제 결과** |

## Architecture/Contract 변경 여부

**없음.** 함수 시그니처, 반환 타입, 호출 형태(`call_engine()` 1회)
전부 무변경. 새 Capability/Agent를 추가하지 않았다. Engine/Execution
Layer를 변경하지 않았다.

## Governance

RFC/ADC/ADR 불필요 — Capability Logic Improvement이며
`development-hq/CONSTITUTION.md`의 Capability Loop(Governance 없음)
범위 안에서 수행했다.

## 다음 관찰 조건

원 현상(Investment 도메인 비결정성)을 실제로 검증하려면, 완결된
project를 사후 수정하는 대신 **다음 Investment Dogfooding 라운드가
실제로 열릴 때** 동일한 언어 고정 문장을 새 project의 지시문에
처음부터 포함시켜 관찰하는 것이 적절하다 — 이번 문서는 그 라운드를
선제적으로 만들지 않는다.

## Self Review

- Architecture/Contract를 변경했는가 — **아니오**.
- Engine/Execution Layer를 변경했는가 — **아니오**.
- 완결된 Investment project(point-in-time Evidence)를 수정했는가 —
  **아니오** — Development HQ Platform Capability만 대상으로 했다.
- 실패한 검증을 성공으로 표현했는가 — **아니오** — §6에서
  "Inconclusive"임을 명시했다.
- 불필요한 리팩터링을 했는가 — **아니오** — 지시문 한 문장 추가 외
  다른 변경 없음(`git diff` 확인).
- RFC/ADC/ADR을 작성했는가 — **아니오**.
