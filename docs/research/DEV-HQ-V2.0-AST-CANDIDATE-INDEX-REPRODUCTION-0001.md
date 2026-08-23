# DEV-HQ-V2.0 — AST Function Candidate Index 재현성 Research

## 목적

T17에서 "Design 원문만으로는 AST Context 시작점을 식별할 수 없지만,
AST 기반 함수 후보 인덱스(이름+시그니처+docstring 첫 줄)를 추가하면
식별 가능하다"는 결과가 1건 확인됐다. 이 문서는 **T17과 다른 실제
Task 2건**으로 이 결과가 재현되는지 확인해, RFC-0007의 첫 번째
선행조건(시작점 자동 식별)에 대한 Start-Point Research를 종료할 수
있는지 판단한다.

## 실험 설계

T17과 동일한 방법론(Design은 실제 소스를 보지 못한 상태로 blind
실행, 이후 동일한 AST 함수 후보 인덱스를 real Engine에 제공해 식별
질의)을 서로 다른 성격의 Task 2건에 적용했다. 각 Task의 issue/
description에는 실제 파일명·함수명을 전혀 언급하지 않았다.

- **Task 1(fence)**: "Backend Agent가 생성한 코드의 마크다운 코드펜스
  처리에서, 시작 펜스만 있고 닫는 펜스가 없는 경우와 펜스가 아예
  없는 경우의 경계 테스트가 부족하다." — 실제 대상:
  `agents._strip_code_fence`.
- **Task 2(context reuse)**: "Issue로부터 수집한 Context를 Planning과
  Design 양쪽에 재사용하는 파이프라인이, Context를 두 번 따로
  수집하지 않는지 확인하는 테스트가 없다." — 실제 대상:
  `workflow_project_intelligence.run_issue_to_design`.

두 Task 모두 T12~T18 전체에서 Build 대상으로 다뤄진 적이 없는 함수다.

## 결과

| Task | 식별 결과 | 정답과 일치 |
|---|---|---|
| Task 1(fence) | `FILE: agents.py` / `FUNCTION: _strip_code_fence` | **일치** |
| Task 2(context reuse) | `FILE: workflow_project_intelligence.py` / `FUNCTION: run_issue_to_design` | **일치** |

T17 1건을 포함하면 **3/3(100%)** 식별 성공이다.

### AST 폐쇄 + Build + pytest 검증

식별된 시작점으로 AST 폐쇄를 계산해 실제 Build를 실행하고 pytest로
검증했다.

- Task 1: 폐쇄 1개 모듈(`agents`), 334자. Build가 경계 케이스 7개를
  검증하는 테스트 함수를 반환, import 경로만 보정 후 pytest 통과.
- Task 2: 폐쇄 5개 모듈(`agents`, `engine`, `project_intelligence`,
  `workflow`, `workflow_project_intelligence`), 7,643자. Build가
  `run_issue_to_design`을 mock으로 감싼 계약 테스트를 반환, import
  경로만 보정 후 pytest 통과.

```
2 passed in 0.02s
```

### 관찰(식별 정확도와 별개, Build 내용 품질 관련)

Task 2의 생성된 테스트는 실제로는 "두 개의 서로 다른 Issue를 연속
호출해도 상태가 섞이지 않는다"만 검증했고, Design이 의도한 "**한
번의 호출 안에서** Context를 두 번 수집하지 않고 재사용한다"는
계약(`collect_relevant_context`가 호출 1회로 그치고 그 결과가 Planning/
Design 양쪽에 재사용되는지)은 직접 assert하지 않았다. 이는 식별
정확도의 문제가 아니라(대상 함수/파일은 정확히 찾았다) T06 이래
반복 관찰된 Design→Build 의미 손실의 또 다른 사례로, 이 Research의
판정 대상은 아니므로 Evidence로만 기록한다.

## 재현성

3/3(T17 1건 + 이번 2건) 전부 AST 함수 후보 인덱스로 정확히
식별됐다. 표본이 작지만(3건), 서로 다른 성격의 Task(공백 검증 로직 /
문자열 후처리 경계 케이스 / Context 재사용 계약)에서 실패 없이
재현됐다 — 종료 기준의 "대부분의 실제 사례에서 정확히 식별"에
해당한다.

## 최종 판정

**Start-Point Research 종료** — AST 함수 후보 인덱스(이름+시그니처+
docstring 첫 줄, 본문 없음) + Design 원문 조합으로 시작점을 자동
식별하는 방법이 3건의 서로 다른 실제 Task에서 재현됐다. 실패 사례가
없어 "최소 입력 조건 재정의"나 "혼합 결과 추가 검증"은 필요하지
않다.

## RFC-0007 영향

RFC-0007 §Decision의 첫 번째 선행조건("시작점 식별 방법이 검증된 적
없다")은 이제 **"AST 함수 후보 인덱스를 추가하면 안정적으로 해결된다"**는
근거(3/3)로 대체할 수 있다. RFC-0007의 두 번째 선행조건(Target File
Exposure 완화 정책, T13~T16)은 이 Research의 범위 밖으로 여전히
남아 있다 — 두 선행조건 중 하나만 해결됐다는 뜻이며, RFC-0007의
Decision(B. CONDITIONAL)을 A(INTEGRATION JUSTIFIED)로 승격하려면
두 번째 선행조건도 별도로 검증되어야 한다.

## 다음 Task

1. RFC-0007의 두 번째 선행조건(Target File Exposure 완화 정책)을
   별도로 검증하거나 정책화하는 작업 — 이것이 해결되면 RFC-0007
   전체 Decision을 재평가할 수 있다.
2. AST 함수 후보 인덱스가 저장소 규모가 커질 때(수십~수백 개 함수)도
   같은 정확도를 유지하는지는 이번 Research에서 다루지 않았다 —
   필요 시 별도 Research(이번 Research는 여기서 확장하지 않는다).

```text
Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: 36 passed (mvp 전체), 임시 비교 파일(_t18_task1.py/_t18_task2.py)은 검증 후 삭제, git status clean 확인
E2E: PASS (식별 2건 모두 정답과 일치, Build+pytest 2건 모두 통과, 전부 real Engine 호출)
PR: NOT CREATED
Commit: (아래 커밋 해시)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: YES
Next Implementation Candidate: RFC-0007의 두 번째 선행조건(Target File Exposure 완화 정책) 검증 — 해결되면 RFC-0007 Decision 재평가(B → A 승격 여부)
```
