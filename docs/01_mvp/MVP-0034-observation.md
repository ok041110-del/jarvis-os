# MVP-0034 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 변경하지 않았다** —
정상 동작해 수정할 문제가 없었다.

## 목적

`development-hq/mvp/cli.py`(MVP-0001 실행 진입점)는 지금까지 어떤
MVP에서도 **실제 CLI 프로세스로 직접 실행된 적이 없다** — 지금까지의
모든 검증(MVP-0001 테스트, MVP-0025~0033)은 `run_mvp_0001()` 등 내부
함수를 Python에서 직접 import해서 호출하는 방식이었다. `cli.py`는
파일 경로 인자 파싱, 파일 읽기, 출력 포맷팅(`## Code Review`/
`## Test Case Suggestions` 헤더)이라는 자신만의 추가 코드를 갖고
있어, 내부 함수가 검증됐다고 해서 이 진입점 자체가 검증된 것은
아니다. 이번 MVP는 이 미검증 경로를 실제 서브프로세스로 실행한다.

## 실행

```
python3 development-hq/mvp/cli.py <sample_cli_input.py 경로>
```

입력 파일은 기존 `test_mvp_0001.py`의 `SAMPLE_CODE`와 동일한 내용
(bare except, mutable default가 있는 `add()` 함수)을 별도 파일로
저장한 것이다. 실제 서브프로세스로 실행했다(mock 없음, `subprocess`가
아니라 셸에서 직접 `python3 cli.py <file>` 커맨드를 실행).

## 관찰 결과

- 정상 종료, 예외 없음.
- 출력이 `cli.py`가 정의한 형식 그대로 나타났다: `## Code Review`
  섹션(실제 리뷰 5건 — mutable default, bare except, silent
  failure, 계약 모호성, 타입 힌트 부재) 다음에 `## Test Case
  Suggestions` 섹션(실제 테스트 케이스 23건 — happy path, mutable
  default 회귀, 예외 삼킴, 반환값 모호성, 경계 조건까지).
- 인자 파싱(`sys.argv[1]`로 파일 경로 받기), 파일 읽기(`open(...,
  encoding="utf-8")`), 두 섹션을 순서대로 print하는 로직 — 이 세
  가지가 이번에 처음으로 실제 서브프로세스 실행에서 검증됐다.
- `run_mvp_0001()` 자체의 동작(내부 함수 호출)은 MVP-0025~0027에서
  이미 실제 Engine으로 반복 검증된 부분이며, 이번 관찰의 새로운
  대상이 아니다 — 새로 검증된 것은 `cli.py`가 그 함수를 감싸는
  **진입점 코드**뿐이다.

## 회귀 확인

- `python3 -m pytest development-hq/mvp/tests -q` — 3건 모두 통과.
- `git status --porcelain` — 클린. 이번 관찰은 코드를 변경하지
  않았다.

## 부수 관찰 — 대기 스크립트의 자기 매칭 버그 (Architecture와 무관)

실행 자체와는 무관하지만, 이 MVP를 진행하는 동안 세션 쪽에서 실제
Engine 완료 여부를 폴링하던 보조 스크립트가 `pgrep -f "cli.py
/tmp/claude-0"`로 대기 조건을 확인했는데, 그 패턴 문자열이 **폴링
루프 자기 자신의 셸 명령어 텍스트**와 우연히 일치해 종료 조건이
영원히 참이 되지 못했다 — `cli.py` 프로세스 자체는 정상적으로
완료됐고 결과도 온전했다. 이는 Development HQ/Execution Layer의
Architecture나 Contract와 무관한, 세션 진행 중 보조 스크립트의
버그였다 — 발견 즉시 그 폴링 프로세스만 종료했고, `cli.py` 실행
결과나 저장소 코드에는 영향이 없었다. 별도 조치가 필요하지 않아
기록만 남긴다.

## Self Review

- 코드를 변경했는가 — **아니오**. `git status` 클린.
- Architecture를 설계했는가 — **아니오**.
- 실제 Engine으로 확인했는가 — **예**. `cli.py`를 실제 서브프로세스로
  1회 실행(mock 없음), 내부적으로 real `claude -p` 1회 호출.
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  진입점 자체는 정상 동작했고, 무관한 세션 스크립트 버그는 별도로
  구분해 기록했다.
- caller 위치 결정을 시도했는가 — **아니오**. 이 실행은 기존
  `run_mvp_0001()` Capability의 CLI 진입점을 검증한 것으로,
  Execution Layer caller 위치(`ADC-0010`)와 무관하다.
