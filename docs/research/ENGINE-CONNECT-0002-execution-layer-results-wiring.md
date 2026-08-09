# ENGINE-CONNECT-0002: 외부 caller → `call_engine()` → 실제 Engine → `results:list[str]` → ExecutionResult — Runtime Evidence

이 문서는 사용 후기가 아니다. 실제로 수행한 배선 실험 하나의 기록이다.
`ENGINE-CONNECT-0001`(Development HQ 범위, `call_engine()` 자체의 실제
배선)의 후속으로, 이번에는 **Execution Layer의 `results`까지** 그
값이 실제로 도달하는지를 관찰한다. Execution Result Contract를 새로
설계하지 않는다. Engine Gateway/Adapter를 만들지 않는다. Baseline을
수정하지 않는다. RFC/ADC/ADR을 작성하지 않는다. ADC-01·ADC-02·Engine
Caller 위치(ADC-0010)를 재조사하지 않는다. **이 문서 자체가 코드
변경이 아니다** — 실험 코드는 격리된 worktree에만 존재했고 tracked
브랜치에는 반영되지 않았다.

## 왜 이 실험이 필요했는가

- `ADC-0005-engine-connection-boundary.md` Q0가 "caller가 Execution
  Layer 밖에서 `call_engine()`을 호출하고 그 결과를 caller-supplied
  `results`로 주입하는 것"을 Evidence 기반으로 Accept했다 — 그러나
  그 Accept는 **문서 인용에 근거한 판단**이었고, 실제로 그 흐름을
  실행해 관찰한 적은 없었다.
- `ADC-0010-engine-caller-location-boundary.md`는 그 caller가
  **어디에 위치해야 하는가**(production 후보 6개)는 전부 Not
  Accepted로 남겼다 — 즉 "caller가 존재할 수 있다"는 것과 "caller가
  어디 있어야 한다"는 것은 서로 다른 질문이며, 이 실험은 후자를
  다루지 않는다.
- 이 실험은 그 사이의 공백 — "허용은 됐지만 실제로 실행해 관찰된
  적은 없다" — 을 메우기 위한 것이다. caller의 production 위치는
  결정하지 않는다. 이 실험의 caller는 worktree에만 존재하는 임시
  스크립트다.

## Experiment

- **격리**: `git worktree add`로 별도 worktree를 만들어(`experiment-engine-connect-0002-seed`
  브랜치, base `origin/main` = `83d9685`) 그 안에서만 실행했다. tracked
  브랜치(`claude/jarvis-os-hq-mvp-0001-2fcqvd`)는 실험 전후 변경 없음.
- **caller**: worktree 루트의 `experiment_0002_engine_connection.py`
  (신규 임시 파일, tracked 브랜치에 반영하지 않음). Execution Layer도
  Development HQ도 아니다 — 두 영역의 기존 공개 함수(`call_engine()`,
  `build_execution_result()`)를 그대로 import해서 순서대로 호출할
  뿐이다. 새 Gateway/Adapter/Registry는 만들지 않았다.
- **입력 재사용**: 새 Fixture를 만들지 않고, 이미 저장소에 있는
  `core/execution_layer/mvp_0006/dogfooding/output/toy_issue.*`
  (MVP-0006 Dogfooding이 이미 생성해 둔 산출물)를 그대로 읽었다 —
  `toy_issue.implementation_specification.md`(prompt로 사용),
  `toy_issue.execution_state.md`(`build_execution_result()`의 입력으로
  사용).
- **6개 Builder 전체를 다시 태우지 않은 이유**: `build_execution_result()`
  는 Execution State(문자열)만 입력으로 받는다 — 그 앞단 5개 Builder는
  MVP-0001~0005 Dogfooding이 이미 실측 검증했다. 이 실험은 "`results`가
  실제 Engine 산출물로 채워질 수 있는가"만 보므로, `ExecutionResultBuilder`
  1개만 직접 호출했다. 이는 검증 방법 선택이며 Contract 변경이 아니다.
- **실제 Engine 호출 횟수**: **1회.** Phase 1(Fake Engine)로 구조를
  먼저 검증한 뒤, Phase 2에서만 `development-hq/mvp/engine.py`의
  실제 `call_engine()`(`claude -p`, `--disallowedTools`로 파일/셸
  도구 차단)을 1회 호출했다.

## Phase 1: Fake Engine (구조 검증, 실제 Engine 호출 0회)

`fake_call_engine(prompt) -> "FAKE_ENGINE_OUTPUT_MARKER::" + len(prompt)`
로 `call_engine()`을 대체해 배선 구조만 확인했다.

| 확인 항목 | 관찰 결과 |
|---|---|
| prompt 타입 | `str`, 길이 502 |
| caller → 함수 호출 | 예외 없이 성공 |
| 반환값 타입 | `str`, 길이 30 |
| `results: list[str]` 변환 | `[raw_output]` — 예외 없음 |
| `build_execution_result()` 반환 | 예외 없음, 길이 1423자 |
| `raw_output`이 ExecutionResult 안에 verbatim 보존 | **True** |

Fake Engine 단계에서 구조상 문제가 없음을 먼저 확인한 뒤에만 실제
Engine을 호출했다.

## Phase 2: 실제 Engine (`claude -p`, 1회)

### 입력

`toy_issue.implementation_specification.md` 전체(502자)를 그대로
`call_engine()`의 `prompt` 인자로 전달했다. 새 프롬프트 포맷을 만들지
않았다 — `call_engine()`의 계약(`str -> str`)을 그대로 썼다.

### 출력 (실제 Raw Output, 263자)

````text
```python
def reverse_string(*args, **kwargs):
    """문자열을 뒤집는다"""
    if args:
        s = args[0]
    elif kwargs:
        s = next(iter(kwargs.values()))
    else:
        raise TypeError("reverse_string() requires one string argument")
    return s[::-1]
```
````

실제 Python 코드 블록(마크다운 fenced code)이 반환됐다 —
`ENGINE-CONNECT-0001`이 관찰한 "자유 서술형 산문 + 코드 블록"과
같은 계열(구조화되지 않은 텍스트, 고정 스키마 없음)이지만, 이번
프롬프트(Implementation Specification, "코드를 작성하라"는 취지)에
대해서는 산문 없이 코드 블록만 반환됐다 — 프롬프트에 따라 형태가
달라진다는 사실이 이번에도 재확인됐다(1회 관찰).

### 관찰 결과

| 확인 항목 | 관찰 결과 |
|---|---|
| `call_engine()` 호출 가능 여부 | **가능** — 예외 없음 |
| 반환값 타입 | `str` |
| `results: list[str]` 변환 | `[raw_output]` (1개 항목) — 예외 없음, 새 변환 규칙 불필요(그대로 리스트로 감싸는 것으로 충분했다) |
| `build_execution_result()` 반환 | 예외 없음, 최종 ExecutionResult 길이 1656자 |
| `raw_output`이 ExecutionResult `## Results` 절 안에 **verbatim**으로 보존됨 | **True** (Python `in` 연산자로 정확히 확인) |
| 기존 Contract/불변식 위반 | 없음 — `results`는 `ADC-0002`·`ADC-0003`이 이미 확정한 `list[str]` 그대로이며, `build_execution_result()`는 항목 개수·의미를 검증하지 않는다(기존 동작 그대로) |

### ExecutionResult 실제 출력 (`## Results` 절 발췌)

```markdown
## Results
- ```python
def reverse_string(*args, **kwargs):
    ...
    return s[::-1]
```
```

**부작용 관찰(Architecture 판단 아님, 관찰된 사실만)**: `results`의
단일 항목이 여러 줄(fenced code block)을 포함하면, `build_execution_result()`
가 `f"- {item}"`으로 한 줄 bullet을 만드는 방식 때문에 실제로는 마크다운
list item 하나가 아니라 원본 코드 블록의 줄바꿈이 그대로 이어져,
결과 마크다운에서 "- " 뒤에 여러 줄이 들여쓰기 없이 붙는 형태가 된다.
이것이 마크다운 렌더러에서 올바른 list item으로 보일지는 이 실험에서
검증하지 않았다(렌더링 여부는 관찰 대상이 아니었다). 이 관찰은 결함
판단이나 변환 규칙 결정이 아니다 — 있는 그대로의 사실만 기록한다.

## 7개 검증 항목 요약

| # | 검증 대상 | 관찰 결과 |
|---|---|---|
| 1 | Implementation Specification → caller 입력 호환성 | 호환됨 — `str` 그대로 `call_engine(prompt: str)`에 전달 가능, 예외 없음 |
| 2 | caller → `call_engine()` 호출 가능 여부 | 가능 — Fake/Real 둘 다 예외 없이 성공 |
| 3 | 실제 Engine 반환값 형태 | `str`, 이번 관찰에서는 산문 없이 fenced code block 1개(263자) |
| 4 | 반환값 → `results:list[str]` 변환 가능 여부 | 가능 — 단순히 `[raw_output]`으로 감싸는 것으로 충분했다(추가 파싱/분할 불필요) |
| 5 | ExecutionResult에서 결과 보존 여부 | 보존됨 — `raw_output`이 최종 ExecutionResult 문자열 안에 정확히(verbatim) 포함됨을 확인 |
| 6 | 기존 Contract/불변식과 충돌 여부 | 충돌 없음 — `ADC-0002`·`ADC-0003`·`ADC-0005` Q0가 이미 허용한 caller-supplied `results` 그대로 사용, `build_execution_result()` 코드/테스트 변경 없음 |
| 7 | 새로운 Architecture Blocking Evidence 발생 여부 | 발생하지 않음 — 아래 Stop Trigger 대조 참고 |

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| 새 Component/Layer/Service 필요 | 미발동 |
| Engine Gateway/Adapter 필요 | 미발동 — 두 기존 공개 함수를 그대로 호출 |
| Registry/Scheduler/Runtime 필요 | 미발동 |
| Engine Routing 필요 | 미발동 — Engine 선택 로직 없음, 단일 함수 |
| `results` 변환 규칙 신설 필요 | 미발동 — `[raw_output]` 그대로 충분했다(이번 1회 관찰) |
| Execution Layer 내부 수정 필요 | 미발동 — `execution_result_builder.py` 코드 변경 없음, "AI 호출 없음" 불변식(Builder 소스 코드 범위) 그대로 유지 |
| Baseline 변경 필요 | 미발동 |
| Execution Result Consumer 설계 필요 | 미발동 — Consumer 쪽은 다루지 않았다 |

**하나도 발동하지 않았다.**

## 회귀 확인

- 실행 범위: `python3 -m pytest core/execution_layer development-hq/mvp -q`
- 결과: **58 passed**(실험 전후 동일 worktree에서 재확인). 지시문의
  "기존 55 passed"라는 기준과는 실제 관측치가 다르다 — 실패로
  표현하지 않고 실제 관측치(58)를 그대로 기록한다. 실험 전 tracked
  `origin/main` 기준으로도 동일 범위에서 58 passed였다(실험으로 인한
  변화 없음).
- `git status --porcelain`(worktree): 신규 untracked 파일 3개만
  존재(`experiment_0002_engine_connection.py`,
  `experiment_0002_fake_execution_result.md`,
  `experiment_0002_real_execution_result.md`) — 기존 파일 수정 0건.
- `git status --porcelain`(tracked 브랜치, 메인 체크아웃): 실험
  전후 변경 없음(worktree는 별도 디렉터리).

## 이 문서가 하지 않는 것

- `results: list[str]`로의 변환 규칙을 정식 Contract로 확정하지
  않았다 — `[raw_output]` 1개 항목이 유일하게 가능한 방법이라는
  뜻이 아니다(1회만 관찰).
- caller의 production 위치를 결정하지 않았다 — `ADC-0010`의 Not
  Accepted 상태를 바꾸지 않는다. 이 실험의 caller는 worktree에만
  존재하며 어떤 tracked 위치로도 승격하지 않는다.
- Execution Layer 내부(`Builder`/`Pipeline`)에서 `call_engine()`을
  호출하도록 바꾸지 않았다 — `ADC-0005` Q1(Not Accepted)을 재론하지
  않는다. 이 실험은 Q0(caller 수준, Accept)만 실행했다.
- Execution Result Consumer를 설계하지 않았다.
- 마크다운 list item 렌더링 문제(§Phase 2 부작용 관찰)를 고치지
  않았다 — 관찰만 했다.

## Unknowns

- `results`에 항목이 2개 이상일 때(예: Engine을 여러 번 호출해 여러
  산출물을 각각 담을 때)도 같은 방식(그대로 리스트에 추가)이 통하는지
  — 1개 항목만 관찰했다.
- 이번 프롬프트(Implementation Specification)가 항상 fenced code
  block만 반환하는지, 다른 입력에서는 산문이 섞이는지 —
  `ENGINE-CONNECT-0001`(다른 프롬프트 포맷)은 산문+코드 혼합을
  관찰했다. 이번 1회 관찰만으로 일반화하지 않는다.
- 실제 Engine 반환값에 마크다운 특수문자(`## `, list 마커 등)가
  포함될 때 `build_execution_result()`의 `## Results` 절 구조를
  깨뜨릴 수 있는지 — 이번 관찰에서는 fenced code block(```` ``` ````)
  자체가 마크다운 구조에 영향을 줬으나(§Phase 2 부작용 관찰), 그 외
  특수 케이스(중첩 `## ` 헤더 등)는 시험하지 않았다.
- 반복 실행 시 Raw Output이 안정적으로 코드 블록만 반환하는지 — 1회만
  관찰했다.

## Conclusion

외부 caller → `call_engine()` → 실제 Engine(Claude Code CLI) →
`results:list[str]` → `ExecutionResult`로 이어지는 흐름 전체가, 기존
Contract·불변식을 수정하지 않고 1회 실행으로 실제 관찰됐다. 어떤 Stop
Trigger도 발동하지 않았다. `results`로의 변환은 이번 관찰에서는 반환값을
그대로 단일 항목 리스트에 담는 것으로 충분했고, 그 값은 최종
ExecutionResult 안에 verbatim으로 보존됐다. 다만 이 결과는 caller의
production 위치(`ADC-0010`), 다중 항목 `results`, 다른 입력에 대한
재현성 등은 다루지 않았다 — 이 문서는 그 판단들을 내리지 않는다.
