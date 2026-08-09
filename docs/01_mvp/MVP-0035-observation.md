# MVP-0035 Observation

**문서 성격**: 실제 실행 기록(Evidence). **코드를 변경하지 않았다** —
정상 동작해 수정할 문제가 없었다.

## 목적

`development-hq/mvp/workflow_0009.py`(`run_comparison()` — MVP-0005
방식 flat Context와 MVP-0009 방식 Context Bundle을 같은 Issue로 나란히
실행)는 `run_comparison()` 자체는 MVP-0009/MVP-0028에서 실제 Engine으로
반복 검증됐지만, 이 파일이 가진 `if __name__ == "__main__":` 진입점은
지금까지 어떤 MVP에서도 독립된 프로세스로 직접 실행된 적이 없었다 —
MVP-0034가 `cli.py`에 대해 지적한 것과 같은 이유로, 내부 함수가
검증됐다고 해서 이 진입점 자체가 검증된 것은 아니다. 이번 MVP는 이
미검증 진입점을 실제 서브프로세스로 실행했다. `caller 위치`
결정(ADC-0010)과 무관한, 기존 dev 진입점의 Evidence 축적이다
(GOVERNANCE-REVIEW-0003의 Hold 결론이 허용하는 범주).

## 실행 및 발견한 사실

먼저 `cli.py`와 같은 방식(`python3 development-hq/mvp/workflow_0009.py`)으로
직접 실행을 시도했다:

```
$ python3 development-hq/mvp/workflow_0009.py
Traceback (most recent call last):
  ...
ImportError: attempted relative import with no known parent package
```

`workflow_0009.py`는 `from .agents import ...` 등 패키지 상대 import를
쓰는데, `cli.py`와 달리 `sys.path` 조정이나 절대 import로의 전환이
없다. 이 파일은 애초에 `python3 file.py` 직접 실행용으로 문서화된
적이 없다(`cli.py`만 "MVP-0001 실행 진입점"으로 명시됨) — 패키지
상대 import를 쓰는 모듈의 정상적인 실행 방식은 `python3 -m
package.module`이므로, 이 방식으로 다시 실행했다:

```
$ python3 -m development-hq.mvp.workflow_0009
```

- 정상 종료, 예외 없음.
- `=== Flat Context Planning ===`, `=== Context Bundle Planning ===`
  두 섹션이 순서대로 출력됐고, 각각 실제 Engine이 생성한 서로 다른
  분량·구조의 요구사항 분석 결과였다(flat 쪽은 "다음 단계 제안"으로
  마무리, bundle 쪽은 "미결 사항(Open Question)"으로 마무리 — 같은
  Issue에 다른 Context 구조를 준 결과가 실제로 다르게 나타남을
  재확인).
- 최초 1회 실행 시 Engine이 "You've hit your session limit · resets
  9:10am (UTC)"를 반환했다 — 이는 `claude -p` Engine 자체의 세션
  한도이며 코드 결함이 아니다. 한도 리셋 시각 이후 동일 커맨드를
  재실행해 정상적인 실제 Engine 출력을 확인했다.
- `__main__` 블록의 `print()` 포맷팅(`=== ... ===` 헤더, 두 섹션 순서)
  자체가 이번에 처음으로 실제 서브프로세스 실행에서 검증됐다.

## 코드 변경 여부

없음. `python3 -m development-hq.mvp.workflow_0009`가 이 파일의 상대
import 구조에 맞는 정상적인 실행 방법이며, 이 방식으로 실제 Engine
호출까지 문제없이 완료됐다. `cli.py`처럼 `sys.path` 조정을 추가해
`python3 file.py` 직접 실행을 지원하게 만드는 것은 이 파일이 요구한
적 없는 새 진입점 계약을 임의로 추가하는 것이므로 하지 않았다.

## 회귀 확인

- `python3 -m pytest development-hq/mvp/tests -q` — 3건 모두 통과.
- `git status --porcelain` — 클린. 이번 관찰은 코드를 변경하지
  않았다.

## Self Review

- 코드를 변경했는가 — **아니오**. `git status` 클린.
- Architecture를 설계했는가 — **아니오**.
- 실제 Engine으로 확인했는가 — **예**. `workflow_0009.py`의
  `__main__` 진입점을 실제 서브프로세스로 실행(mock 없음), 내부적으로
  real `claude -p`를 2회 호출(flat/bundle 각 1회).
- 문제가 없는데 있다고, 또는 있는데 없다고 표현했는가 — **아니오**.
  `python3 file.py` 직접 실행은 상대 import 구조상 실패하는 것이
  정상이며, 이 파일의 실제 진입 방식(`python3 -m ...`)으로는 정상
  동작함을 구분해 기록했다. Engine 세션 한도는 별도로 명시했다.
- caller 위치 결정을 시도했는가 — **아니오**. 이 실행은 기존
  `run_comparison()`의 로컬 dev 진입점을 검증한 것으로, Execution
  Layer caller 위치(`ADC-0010`)와 무관하다.
