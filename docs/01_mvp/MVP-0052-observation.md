# MVP-0052 Observation (Phase 10 Boundary Validation)

**문서 성격**: 실제 실행 기록(Evidence). `MVP-0051`이 채택한 기준("real
issue = 정답 동작을 깨는 결함, 개선 제안은 issue 아님")을 그대로 유지한
채(agents.py 무수정), 기존 `CLEAN_CODE`/`SAMPLE_CODE`보다 더 모호한 경계
입력으로 그 기준이 실제로 유지되는지 검증한 기록이다. Prompt Specification
을 설계하지 않았다. Architecture/Contract를 바꾸지 않았다.

## 목적

`MVP-0051`은 명백한 두 입력(실이슈 있음/없음)에서만 검증됐다. 이번
문서는 "실이슈"와 "제안"의 경계가 더 모호한 입력에서도 그 기준이
안정적으로 유지되는지 real Engine으로 확인한다.

## 1. 경계 입력 설계와 실제 결과

### BOUNDARY_CRASH — 명백한 crash, 스타일상 문제 없어 보이는 코드

```python
def average(numbers):
    return sum(numbers) / len(numbers)
```

빈 리스트를 주면 `ZeroDivisionError`가 난다 — MVP-0051 정의상 명백한
"crash"이므로 marker가 나오면 안 된다. 코드 자체는 짧고 스타일상
흠잡을 데 없어 보여, Engine이 이를 style 문제로 착각하고 마커를 낼
위험을 테스트했다.

**결과(3회): marker 미등장 3/3 — 기대와 정확히 일치.** 짧고 깔끔해
보이는 코드에서도 실제 crash 위험은 놓치지 않았다.

### "안전해 보이는 lookalike" — 3회 시도, 매번 실제 결함이 발견됨

두 번째 경계축("실이슈 없어 보이지만 알려진 버그 패턴과 표면적으로
비슷한 코드")을 테스트하려고 3개 입력을 순서대로 시도했다. **셋
다, 설계 의도와 달리 Engine이 실제로 유효한 잠재 결함을 찾아냈다** —
아래에 있는 그대로 기록한다(실패한 시도를 성공으로 재포장하지 않음).

| 입력 | 설계 의도 | 실제 결과 | Engine이 찾은 것 |
|---|---|---|---|
| `tags(name, extra=None): extra = extra or []; return [name] + extra` | mutable-default 버그의 "고쳐진" 버전 → marker 기대 | marker 1/3 | `extra`가 list가 아닌 iterable(tuple 등)이면 `[name] + extra`가 실제로 `TypeError` — 진짜 crash 경로 |
| `tags(name, extra=None): if extra is None: extra = []; return [name, *extra]` | 표준 안전 idiom → marker 기대 | marker 2/3 | `extra`가 문자열이면 `*extra`가 문자 단위로 풀려 **wrong output**(설계자도 놓친 실결함) |
| `safe_divide(a, b): try: return a/b except ZeroDivisionError: return None` | bare-except(SAMPLE_CODE)와 달리 특정 예외만 잡는 정상 패턴 → marker 기대 | marker 1/3 | 함수 이름 `safe_divide`가 "모든 나눗셈 실패를 안전하게 처리"를 암시하는데 `TypeError`(비숫자 입력)는 안 잡힘 — 이름이 암시하는 계약과 실제 동작의 불일치 |

세 입력 모두 필자가 "실이슈 없음"으로 설계했으나, 매번 Engine이 실제로
유효한 결함(진짜 crash 경로 또는 진짜 wrong output 또는 이름-계약
불일치)을 지적했다 — **필자의 "안전하다"는 판단 자체가 틀렸다.**
이는 짧은 코드에서도 진짜 잠재 결함 없이 만들기가 생각보다 어렵다는
방증이며, MVP-0051 기준의 결함이 아니다.

## 2. 핵심 관찰 — 기준 자체는 15회 전부 자기모순 없음

`MVP-0050`·`MVP-0051`·이번 문서를 통틀어 실제 Engine 호출 15회
(MVP-0051 6회 + 이번 9회) 중, **"review 본문에 real issue를 적어
놓고도 동시에 `NO_ISSUES_MARKER`를 낸" 자기모순 사례는 단 한 번도
없었다.** 마커가 등장하지 않은 모든 회차에서, 그 회차의 review
본문은 실제로 유효한 결함(짜 위 표, 또는 CLEAN_CODE의 이전 관찰)을
근거로 들었다 — "정의 자체가 잘못 적용된" 사례는 관찰되지 않았다.

**대신 관찰된 것은 다른 종류의 편차다**: 같은 입력을 반복하면
Engine이 그 잠재 결함을 **매번 알아채는 것은 아니다**(예: `safe_divide`
run 3은 이름-계약 불일치를 놓치고 marker를 냄). 이는 "무엇이
issue인가"의 정의 문제가 아니라, Engine이 한 번의 호출에서 얼마나
꼼꼼히 코드를 살피는지의 **탐지 재현율(detection recall) 편차**다 —
MVP-0051이 겨냥한 문제(정의 모호성)와는 다른 층위의 원인이다.

## 3. 판정 (사전 정의 기준)

| 기준 | 결과 |
|---|---|
| **Success**: 기준이 자기모순 없이 유지되고(마커+실이슈 동시 등장 없음), 명백한 crash 경계에서 안정적으로 유지됨 | **충족** — 15/15 자기모순 없음, BOUNDARY_CRASH 3/3 |
| **Failure**: 기준이 실제로 뒤집히는 사례(실이슈 명시했는데 마커 등장, 또는 그 반대의 판정 오류) 발견 | 해당 없음 |
| **Inconclusive**: 경계 입력 설계 자체가 검증 목적에 부합하지 않음 | "안전해 보이는 lookalike" 3개 입력 자체는 설계 실패(모두 진짜 결함 포함)로 그 개별 축은 Inconclusive |

**전체 판정: Success.** MVP-0051이 채택한 기준("crash/wrong output만
issue")은 이번 경계 검증에서 단 한 번도 자기모순을 보이지 않았다.
"이슈 없어 보이는 코드"를 만드는 시도 자체가 매번 실패했다는 사실은
기준의 결함이 아니라 — 오히려 그 기준이 실제로 엄격하게 적용되고
있다는 간접 증거다. 다만 탐지 재현율 편차(같은 잠재 결함을 매번
알아채지는 못함)라는 **별개의, 더 근본적인 한계**가 이번 관찰로
새로 확인됐다 — 이는 지시문 정의를 아무리 다듬어도(추가 Prompt
반복) 해결되는 종류가 아니라고 판단해, 이번 문서에서는 추가 지시문
수정을 시도하지 않는다(사용자 지시 7항).

## 4. 회귀 확인

```
$ python3 -m pytest development-hq/mvp/tests -q
36 passed in 72.76s
```

`agents.py`는 이번 문서에서 전혀 수정하지 않았다(MVP-0051 상태 그대로).

## Architecture/Contract 변경 여부

**없음.** Prompt Specification을 설계·도입하지 않았다. 새 Capability/
Agent를 추가하지 않았다. `agents.py` 무수정.

## Governance

RFC/ADC/ADR 불필요. 탐지 재현율 편차는 "Prompt 지시문 개선"이 아니라
"단일 stochastic Engine 호출의 본질적 특성"으로 판단한다 — 지금
Specification/Contract를 설계할 근거로 쓰지 않는다(NEED-DRIVEN DEFER,
아래).

## Self Review

- Architecture/Contract를 변경했는가 — **아니오**.
- Prompt Specification을 도입/설계했는가 — **아니오**.
- `agents.py`를 수정했는가 — **아니오**.
- 실패한 검증을 성공으로 표현했는가 — **아니오** — "안전해 보이는
  lookalike" 3개 입력의 설계 실패를 있는 그대로 기록했다(§1).
- 실패(또는 설계 실패) 후 임의로 추가 Prompt 수정을 시도했는가 —
  **아니오** — 원인만 분석했다(§2, §3).
- RFC/ADC/ADR을 작성했는가 — **아니오**.
