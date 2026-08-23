# DEV-HQ-V2.0 — Design → AST Context Start-Point Research

## 목적

RFC-0007(§2, §Decision)의 첫 번째 선행조건 — "Design의 자유 서술에서
AST Context의 시작점(대상 모듈/함수)을 자동으로 얻는 방법이 검증된
적이 없다" — 을 실제 Repository와 real Engine으로 검증한다. T12~T17
전체와 다른 실제 Build Task를 사용한다.

## 실험 설계

### 실제 Task

"Project Intelligence의 Issue 검증 로직이 title/description이
공백 문자열만 있는 경우에도 예외를 발생시키는지 확인하는 테스트를
추가한다." — issue/requirement 어디에도 실제 파일명(`project_intelligence.py`)
이나 함수명(`validate_issue`)을 직접 언급하지 않았다. Design은
평소와 동일하게 실제 소스를 보지 못한 상태로 실행했다(T06~T16과
동일한 Design 방법론).

### Design 결과의 특이점

Design은 이 Task를 **TypeScript/Jest 프로젝트로 오인**했다 —
`issue.test.ts`, `IssueValidator.spec.ts`, `expect(() =>
...).toThrow(...)`, `describe`/`it` 블록 등 이 저장소에 전혀 존재하지
않는 언어/프레임워크를 가정한 설계를 반환했다. 이는 인위적으로
유도한 것이 아니라, 실제 Design 호출의 자연스러운 결과다 — Design이
"어느 파일을 봐야 하는지" 정보를 전혀 갖고 있지 않을 때 실제로 이
정도까지 빗나갈 수 있다는 것을 보여주는 강력한 실증 사례다.

### 3개 식별 조건

같은 Design 텍스트를 입력으로, "대상 파일과 함수를 정확히 하나씩
식별하라"는 지시와 함께 real Engine(`call_engine`)에 3가지 조건으로
질의했다:

- **A. Design 원문만**: 추가 정보 없음.
- **B. Design + 저장소 구조/파일 목록**: `hqs/development/mvp/*.py`
  파일명 11개(내용 없음, 이름만).
- **C. Design + AST 기반 후보 탐색**: 전체 `mvp/*.py`에서 top-level
  함수/클래스 이름 + 매개변수 시그니처 + docstring 첫 줄만 추출한
  가벼운 인덱스(바디 없음, 3,094자 — AST 폐쇄 알고리즘 자체가 아니라
  그 전 단계의 저비용 목록).

## 결과

| 조건 | prompt_chars | elapsed | 응답 |
|---|---|---|---|
| A. Design만 | 2,026 | 5.6s | `FILE: UNKNOWN` / `FUNCTION: UNKNOWN` |
| B. Design + 파일 목록 | 2,297 | 4.1s | `FILE: UNKNOWN` / `FUNCTION: UNKNOWN` |
| C. Design + AST 후보 인덱스 | 5,231 | 4.3s | `FILE: project_intelligence.py` / `FUNCTION: validate_issue` — **정답과 정확히 일치** |

A와 B는 "모른다"를 정직하게 답했다(틀린 파일을 억지로 지어내지
않았다는 점은 안전한 실패 모드다). 파일 이름만으로는 "Issue 검증"이라는
서술을 특정 함수에 연결할 근거가 부족했다. C는 함수 시그니처와
docstring 첫 줄이 주어지자 `validate_issue(issue: dict) -- title/
description만 필수 Issue 필드로 검사한다`라는 항목을 정확히 짚어냈다.

### Build 검증

C에서 식별된 시작점(`project_intelligence.validate_issue`)으로 AST
폐쇄를 계산(1개 모듈, 621자 — `validate_issue` + `IssueValidationError`만
필요, 다른 모듈 의존성 없음)하고, 이 Context로 Build를 실행했다.
Design의 TypeScript 오인을 정정하는 지시를 함께 주자, 실제 pytest
코드(5개 공백 케이스를 parametrize)를 정확히 반환했다. import 경로만
저장소 관례에 맞게 보정(harness가 수행, 모델 로직 자체는 수정 없음)한
뒤 새 테스트 파일로 실행:

```
5 passed in 0.01s
```

`validate_issue`가 실제로 공백 문자열 필드를 트리밍 후 빈 값으로
판정해 예외를 발생시킨다는 것을 real 코드로 확인했다(Design이
우려했던 "트리밍 미구현" 리스크는 실제로는 해당하지 않았다).

## 최소 필요 입력

**파일 이름만으로는 불충분하고, 함수 단위 시그니처 + 한 줄 설명이
필요하다.** 조건 B(파일명만)와 조건 C(함수명+시그니처+docstring
첫 줄)의 차이가 성패를 갈랐다 — 폐쇄 계산에 필요한 전체 소스나 본문은
전혀 필요 없었고, AST로 이름/시그니처/docstring 한 줄만 뽑은 가벼운
인덱스(3,094자, 파일 내용 대비 매우 작음)로 충분했다.

## 최종 판정

**B. MINIMAL INPUT REQUIRED** — Design 원문만으로는 시작점을 안정적으로
식별할 수 없다(A: 실패, B: 실패). 그러나 AST 기반 함수 후보 인덱스
(이름 + 시그니처 + docstring 첫 줄, 본문 없음)를 추가로 제공하면 실제
Task 1건에서 정확히 식별되고, 그 식별 결과로 이어진 Context 추출과
Build가 실제로 올바르게 동작하는 것까지 확인했다(1건, 일반화 아님).

## RFC-0007에 미치는 영향

RFC-0007 §2/§Decision이 지적한 첫 번째 선행조건("시작점 식별 방법이
검증된 적 없다")에 대해, **"Design 원문만으로는 불가능하지만, 저비용
AST 함수 후보 인덱스를 추가하면 가능하다"**는 최소 1건의 긍정적
Evidence가 생겼다. 이는 RFC-0007의 Decision을 뒤집지 않는다 —
표본이 1개뿐이고, 후보 인덱스 자체를 만드는 로직(전체 저장소를 AST로
스캔해 함수 인덱스를 만드는 것)이 여전히 새로 추가해야 할 구현
대상이라는 점은 동일하다. 다만 "이 문제가 원칙적으로 풀 수 없는
문제"는 아니라는 것을 보여준다 — RFC-0007의 Implementation
Candidate §1이 제안한 "Design 출력 구조화" 대신, **"저장소 전체의
AST 함수 인덱스를 만들어 식별 질의에 함께 제공"**하는 것이 더
간단한 대안일 수 있다는 새로운 방향을 제시한다(Design 자체를 건드릴
필요가 없다는 장점).

## 다음 Task

1. 이 식별 방법(AST 함수 후보 인덱스 + Design)을 여러 사례에서
   반복 검증해 재현율을 확인한다(이번엔 표본 1개, 100% 성공이지만
   일반화할 수 없다) — 특히 후보가 여러 개로 헷갈리는 Task(여러
   모듈에 비슷한 이름의 함수가 있는 경우)에서도 안정적인지 확인
   필요.
2. 후보 인덱스가 저장소 규모가 커질수록(수십~수백 개 함수) 얼마나
   길어지는지, 그 경우에도 식별 정확도가 유지되는지 확인한다.
   (둘 다 구현 아님, Research)

```text
Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: 36 passed (mvp 전체), 검증용 임시 파일(_t17_new_test.py)은 검증 후 삭제, git status clean 확인
E2E: PASS (식별→AST 폐쇄→Build→pytest 전체 체인이 실제로 동작함을 확인, Engine 호출 3회(식별) + 1회(Build) 모두 real Engine)
PR: NOT CREATED
Commit: (아래 커밋 해시)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: YES
Next Implementation Candidate: AST 함수 후보 인덱스 기반 시작점 식별 방법을 여러 사례에서 반복 검증하는 Research, 저장소 규모 확장 시 식별 정확도를 확인하는 Research (둘 다 구현 아님 — RFC-0007의 나머지 선행조건인 Target File Exposure 완화 정책도 별도로 남아 있음)
```
