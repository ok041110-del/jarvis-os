# MVP-0029 Observation

**문서 성격**: 재현 재검증 기록(Evidence). **코드를 변경하지 않았다.**

## 목적

MVP-0026이 (cwd 수정 이전 엔진으로) 4회 반복 재현을 시도해 0/4으로
재현하지 못했던 `run_hello_sdlc()` "implementation placeholder"
현상을, MVP-0028의 `call_engine()` cwd 수정(Engine이 이 저장소의
`CLAUDE.md`/Skill을 더 이상 읽지 않도록 격리) 이후 다시 검증한다.
MVP-0028에서 발견한 cwd 오염이 원래 MVP-0025 Observation이 기록한
1회의 placeholder 현상의 실제 원인이었을 가능성이 있었기 때문이다 —
그 가설을 실제 재실행으로 확인/기각한다.

## 실행 방법

MVP-0026과 동일한 조건으로 재현 시도했다: 동일 Issue("Add input
validation to divide()")로 `run_hello_sdlc()`를 **4회 연속 실제
실행**(mock 없음, 매 회 새 `claude -p` 프로세스, cwd 수정이 반영된
`engine.py` 사용).

## 실행 결과 (4회 전수)

| Run | 소요 시간(초) | status | implementation 길이(문자) | Placeholder 여부 |
|---|---|---|---|---|
| 0 | 82.8 | Complete | 204 | 아니오 — 실제 `divide()` 코드 (docstring 포함) |
| 1 | 86.4 | Complete | 129 | 아니오 — 실제 `divide()` 코드 |
| 2 | 85.6 | Complete | 139 | 아니오 — 실제 `divide()` 코드 |
| 3 | 72.6 | Complete | 126 | 아니오 — 실제 `divide()` 코드 |

4회 모두 `implementation`이 실제 동작하는 `divide()` 코드를
반환했고, `test_execution`도 4회 모두 구체적인 테스트 케이스 목록을
정상 반환했다. Placeholder는 **4회 중 0회** 재현됐다 — MVP-0026과
동일한 0/4 결과다.

### 부수 관찰 — 소요 시간

MVP-0026(cwd 수정 전)의 4회 평균 소요 시간은 133.2초(92.1~171.3초)
였고, 이번(cwd 수정 후) 4회 평균은 81.9초(72.6~86.4초)였다. 매회
독립된 실제 Engine 호출이라 엄밀한 A/B 비교는 아니지만, MVP-0028이
기록한 관찰(cwd 오염 시 Engine이 저장소 Skill을 추가로 읽고 그
Skill의 형식을 따라 훨씬 긴 메타 응답을 만들던 것)과 방향이
일치한다 — 저장소 밖 중립 cwd에서는 각 호출이 더 짧고 더 빠르게
끝난다.

## 판단

**여전히 재현되지 않았다.** MVP-0028의 cwd 수정이 이 특정 placeholder
현상의 원인이었다는 가설은 이번 재현 시도로는 **확인도 기각도 명확히
되지 않는다** — 애초에 cwd 수정 전에도 재현 비율이 0/4(MVP-0026)였기
때문에, cwd 수정 후 다시 0/4가 나온 것은 "고쳐져서 재현이 안 된다"와
"원래도 산발적이라 이번에도 우연히 재현이 안 됐다"를 구분할 근거가
되지 못한다. 다만 cwd 오염이 실제로 존재했고(MVP-0028) 그것이
Requirement Analysis 단계에서 관찰 가능한 형태로 나타난 것은 별개
사실로 이미 확인·수정됐다.

## 후속 처리 (지시에 따름)

"재현되지 않으면 수정하지 말고 Evidence만 기록한다"는 지시에 따라,
`agents.py`/`engine.py`/`workflow*.py` 어디에도 코드 변경을 하지
않았다. `git status`가 클린 상태임을 확인했다.

## Self Review

- 코드를 변경했는가 — **아니오**. `git status` 클린.
- Architecture를 설계했는가 — **아니오**.
- 실제 Engine으로 확인했는가 — **예**. 4회 모두 실제 `claude -p`
  호출(mock 없음), cwd 수정이 반영된 `engine.py` 사용.
- 재현되지 않은 사실을 재현된 것처럼, 또는 원인이 확인된 것처럼
  과장했는가 — **아니오**. "cwd 수정이 원인이었는지는 이번
  재현으로 확인도 기각도 안 된다"는 사실을 그대로 기록했다.
- 추측했는가 — **아니오**. 소요 시간 차이는 "부수 관찰"로만
  기록했고, 이를 근거로 인과관계를 단정하지 않았다.
