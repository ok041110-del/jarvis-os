# ENGINE-CONNECT-0006: `results: list[str]` 2개 이상 항목 — Runtime Evidence

이 문서는 사용 후기가 아니다. 실제로 수행한 배선 실험 하나의 기록이다.
`ENGINE-CONNECT-0002`와 `ENGINE-CONNECT-0005`가 공통으로 남긴 Unknown —
"`results` 항목이 2개 이상일 때의 동작은 여전히 미관찰" — 을 실제
Engine 2회 호출로 메운다. Execution Result Contract를 새로 설계하지
않는다. Engine Gateway/Adapter를 만들지 않는다. Baseline을 수정하지
않는다. RFC/ADC/ADR을 작성하지 않는다. ADC-0002·ADC-0003·ADC-0005·
ADC-0010(Engine Caller 위치)·ADC-0011을 재조사하지 않는다 — 이 실험은
그 Not Accepted/Accept 결론을 바꾸지 않는다. **이 문서 자체가 코드
변경이 아니다** — 실험 코드는 이 세션의 scratchpad에만 존재했고
tracked 브랜치에는 반영되지 않았다(`ENGINE-CONNECT-0002`/`0005`와
동일한 격리 원칙).

## 왜 이 실험이 필요했는가

- `run_execution_layer_pipeline()`/`build_execution_result()`의
  `results` Contract는 타입이 `list[str]`(복수형)이고, 함수 docstring도
  "Engine을 여러 번 호출해 여러 산출물을 각각 담을 때" 같은 실제 사용을
  전제한다. 그러나 `ENGINE-CONNECT-0002`, `ENGINE-CONNECT-0005` 둘 다
  실제 Engine 호출을 **1회**만 해서 `results=[raw_output]`(단일 항목)만
  관찰했다 — "허용됨"과 "실제로 여러 항목일 때 깨지지 않음"은 다른
  질문이며, 후자는 지금까지 한 번도 실측되지 않았다.
- `ADC-0003-execution-result-item-schema.md`가 항목 개수를 명시적으로
  범위 밖에 뒀고, `build_execution_result()` 소스(§docstring)도 "항목
  개수도 검증하지 않는다"고 말하지만, 이는 **정적 코드 읽기로 확인한
  의도**이지 실제 여러 줄짜리 real Engine raw output(마크다운 fenced
  code block 포함) 2개를 넣었을 때 `f"- {item}"` join 로직이 실제로
  각 항목을 서로 침범 없이, 순서대로, verbatim으로 보존하는지는 여전히
  미관찰이었다.

## Experiment

- **격리**: 실험 스크립트(`experiment_engine_connect_0006.py`)는 이
  세션의 scratchpad 디렉터리에만 존재한다 — tracked 브랜치
  (`claude/engine-connect-0006-multi-item-results`)에는 이 문서 하나만
  추가된다. `git status --porcelain`이 실험 전후 비어 있음을 확인했다.
- **입력 재사용**: 새 Fixture를 만들지 않고, `ENGINE-CONNECT-0002`가
  이미 쓴 `core/execution_layer/mvp_0006/dogfooding/output/toy_issue.*`
  (MVP-0006 Dogfooding 산출물)를 그대로 재사용했다 —
  `toy_issue.implementation_specification.md`(`run_execution_layer_pipeline()`의
  `implementation_specification` 인자로 사용), `toy_issue.prompt_specification.md`
  (실제 Engine에 넘길 prompt로 사용, `ENGINE-CONNECT-0005`가 Implementation
  Specification 대신 Prompt Specification을 프롬프트로 쓴 것과 동일한
  선택).
- **6개 Builder 전체를 다시 태운 이유**: 이번 실험의 관찰 대상은
  Pipeline의 앞단(Implementation Specification → Prompt Specification
  렌더링, 이미 `ENGINE-CONNECT-0005`가 검증)이 아니라 `results`가 여러
  항목일 때의 뒷단(`ExecutionResultBuilder`) 동작이다. 그래도
  `run_execution_layer_pipeline()` 하나를 그대로 호출했다 — 개별
  Builder를 다시 조립하는 새 경로를 만들지 않기 위함이다(기존 공개
  함수 재사용 원칙).
- **실제 Engine 호출 횟수**: **2회, 독립적으로.** 동일한 Prompt
  Specification(`toy_issue.prompt_specification.md`, "문자열을
  뒤집는 함수" 요청)으로 `development-hq/mvp/engine.py`의 실제
  `call_engine()`을 두 번 별도로 호출했다 — "Engine을 여러 번 호출해
  여러 산출물을 각각 담는" 실제 시나리오(동일 Task에 대한 독립적인
  두 번의 시도)를 그대로 재현한 것이다. 새 프롬프트 포맷을 만들지
  않았다.

## 실행 결과 (실제 Engine 2회, 총 elapsed 86.4초)

| 확인 항목 | 관찰 결과 |
|---|---|
| Engine 호출 1회차 | 예외 없음, 73.94초, 반환 `str` 길이 76 |
| Engine 호출 2회차 | 예외 없음, 12.51초, 반환 `str` 길이 188 |
| 두 응답이 서로 다른가 | **예** — `output_1 == output_2` → `False`. 같은 prompt에 대해 real Engine이 매번 다른(길이도 다른) 코드를 생성함을 실측 확인(비결정성 재확인) |
| `results=[output_1, output_2]`로 `run_execution_layer_pipeline()` 호출 | 예외 없음, 최종 ExecutionResult 길이 1684자 |
| `output_1`이 ExecutionResult 안에 verbatim 보존됨 | **True** |
| `output_2`가 ExecutionResult 안에 verbatim 보존됨 | **True** |
| `## Results` 절이 정확히 `f"- {output_1}\n- {output_2}"`(코드의 `"\n".join(f"- {item}" for item in results)`가 만드는 그대로의 문자열)와 일치하는가 | **True** — 두 항목이 서로 잘리거나 섞이지 않고, 순서대로, 정확히 그 구분자로 이어졌다 |

### `## Results` 절 실제 출력 (발췌)

```markdown
## Results
- ```python
def reverse_string(*args, **kwargs):
    return args[0][::-1]
```

- ```python
def reverse_string(*args, **kwargs):
    if args:
        s = args[0]
    else:
        s = kwargs.get("s") or kwargs.get("string") or kwargs.get("text")

    return s[::-1]
```
```

두 항목 모두 여러 줄짜리 fenced code block인데도, `f"- {item}"` join이
각 항목을 정확히 구분해 순서대로 이어붙였다 — `ENGINE-CONNECT-0002`가
단일 항목에서 관찰한 "부작용"(fenced code block이 마크다운 list item
구조를 깨는 형태)은 이번에도 그대로 나타나지만(항목마다 "- " 뒤에
들여쓰기 없이 여러 줄이 붙음), **항목 2개 사이의 경계 자체는 깨지지
않았다** — `results` 리스트의 각 원소가 서로 침범하거나 잘리지 않고
정확히 그 순서로 보존됨을 이번에 처음 실측 확인했다.

## Stop Trigger 대조

| Trigger | 발동 여부 |
|---|---|
| 새 Component/Layer/Service 필요 | 미발동 |
| Engine Gateway/Adapter 필요 | 미발동 — 기존 공개 함수(`call_engine`, `run_execution_layer_pipeline`)를 그대로 순서대로 호출 |
| Registry/Scheduler/Runtime 필요 | 미발동 |
| Engine Routing 필요 | 미발동 — 단일 Engine, 단일 호출 지점, 2회 순차 호출 |
| `results` 변환 규칙 신설 필요 | 미발동 — 리스트에 그대로 추가하는 것으로 2개 항목도 충분했다 |
| Execution Layer 내부(Builder/Pipeline) 수정 필요 | 미발동 — 코드 변경 0건 |
| Baseline 변경 필요 | 미발동 |

**하나도 발동하지 않았다.**

## 회귀 확인

- 실행 범위: `python3 -m pytest core/execution_layer development-hq/mvp -q`
- 결과: **58 passed** — `ENGINE-CONNECT-0002`/`0005`가 관찰한 것과
  동일한 수. 이번 실험으로 인한 코드 변경이 없으므로 회귀도 없다.
- `git status --porcelain`: 실험 전후 빈 상태 — 실험 스크립트는 이
  세션의 scratchpad(tracked 브랜치 밖)에만 존재했다.

## 이 문서가 하지 않는 것

- caller의 production 위치를 결정하지 않았다 — `ADC-0010`의 Not
  Accepted 상태(C1~C6 전부)를 바꾸지 않는다.
- `results: list[str]`로의 변환 규칙을 정식 Contract로 확정하지
  않았다 — 이번에도 "그대로 리스트에 추가"가 통했을 뿐이다.
- `## Results` 절의 마크다운 list item 렌더링 문제(fenced code block이
  list 구조를 깨는 부분, `ENGINE-CONNECT-0002`가 이미 관찰)를 고치지
  않았다 — 이번에도 관찰만 했다. 항목 경계 자체(서로 침범하지 않음)와
  마크다운 렌더링 적합성(별도 문제)을 구분해서 기록한다.
- Execution Result Consumer를 설계하지 않았다.

## Unknowns

- 3개 이상의 항목, 또는 빈 문자열/공백만 있는 항목이 섞였을 때의 동작은
  이번에도 관찰하지 않았다.
- 두 Engine 응답 중 하나가 개행이 없는 단순 텍스트이고 다른 하나가
  fenced code block인 것처럼 **형태가 서로 다른** 항목이 섞였을 때도
  경계가 유지되는지는 관찰하지 않았다(이번 관찰은 둘 다 fenced code
  block인 경우만 다룸).

## Conclusion

동일한 실제 Prompt Specification으로 real Engine(`claude -p`)을 독립적으로
2회 호출해 서로 다른 두 개의 실제 산출물을 얻고, 그 둘을
`results=[output_1, output_2]`로 `run_execution_layer_pipeline()`에
전달했다 — 기존 Contract·불변식을 하나도 수정하지 않고, 두 항목이
`## Results` 절 안에서 순서대로, verbatim으로, 서로 침범 없이 보존됨을
실제로 확인했다. `ENGINE-CONNECT-0002`/`0005`가 공통으로 남겼던 "2개
이상 항목 미관찰" Unknown이 이번 관찰로 해소됐다. 어떤 Stop Trigger도
발동하지 않았다. 다만 3개 이상의 항목, 서로 다른 형태의 항목 혼합,
caller의 production 위치는 이번에도 다루지 않았다 — 이 문서는 그
판단들을 내리지 않는다.
