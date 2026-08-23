# DEV-HQ-V2.0-T14 — Scope Pollution 3rd Data Point Research

## 목적

T12에서 Full Source 조건이 좁은 Task(테스트 함수 1개 추가)에서 기존
테스트 파일 전체(기존 4개 + 신규 1개)를 재작성하는 "Scope Pollution"을
보였다. T13은 대상 파일을 Automatic/Full Source 양쪽에 모두 보여주자
둘 다 전체 파일을 재작성했지만 기존 내용은 손상되지 않았다는 것을
확인했고, 이 현상이 "Full Source 자체"가 아니라 **"대상 파일이
Context에 노출됐는가"** 와 상관관계가 있다는 가설을 세웠다.

이 문서는 T12·T13과 다른 실제 Task로 **세 번째 데이터 포인트**를
확보해 그 가설을 검증한다. 이번에는 T13의 가설을 직접 통제 실험으로
검증하기 위해, **기존 테스트 파일 내용을 Automatic·Full Source 양쪽
모두에 보여주지 않는다** — 그 결과 Context 크기(발췌 vs 전체 소스)만이
유일한 변수가 되도록 설계했다.

## 실험 대상

`workflow_artifact_flow.run_issue_to_implementation()` — T12
(`workflow_0008`), T13(`workflow_0009`)과 다른 모듈. 기존
`test_workflow_artifact_flow.py`에는 mock 기반 테스트 4개만 있고
real-Engine E2E 테스트가 없다. Design은 새로 실행했다(대상 함수가
다르므로 T12/T13 Design을 재사용하지 않음).

### Design 결과의 특이점

Design은 실제 함수 시그니처를 보지 못한 상태에서 작성되어, `tmp_path`
fixture와 "throwaway git 워크스페이스" 같은 존재하지 않는 파일시스템
스캐폴딩을 제안했다 — `run_issue_to_implementation(issue: dict)`은
실제로는 딕셔너리 하나만 받는 순수 함수이고 파일시스템을 건드리지
않는다. 이는 이전 Task들에서 반복 관찰된 Design→Build 정보 손실의
또 다른 사례다(별도 대응 없이 Evidence로만 기록).

### AST 자동 폐쇄 결과

`run_issue_to_implementation`을 시작점으로 한 전이적 의존성: 6개 모듈
(`workflow_artifact_flow`, `agents`, `engine`, `project_intelligence`,
`workflow`, `workflow_project_intelligence`), 발췌 8,676자.

Full Source: 같은 6개 모듈 전문, 21,954자.

## Build 비교 (기존 테스트 파일 미노출, 통제됨)

| 조건 | prompt_chars | elapsed | 반환 코드 |
|---|---|---|---|
| A. Automatic (8,676자 발췌) | 12,539 | 17.3s | 704자, 함수 1개만 |
| B. Full Source (21,954자 전문) | 22,749 | 6.9s | 631자, 함수 1개만 |

두 조건 모두:

- **정확히 새 함수 1개만** 반환했다. 기존 코드 재작성, 기존 테스트
  언급, production 코드 수정 제안, 파일 전체 출력 등 어떤 형태의
  Scope 확장도 없었다.
- Design의 잘못된 "workspace/tmp_path" 가정을 실제 함수 시그니처
  (Context로 제공된 실제 `run_issue_to_implementation(issue: dict)`)로
  스스로 정정해 `issue` 딕셔너리를 직접 전달했다 — `tmp_path`는 A에서
  미사용 부작용(불필요한 `monkeypatch.chdir`)으로 남았지만, 실제
  호출 로직 자체는 두 조건 모두 정확했다.
- import 문은 두 조건 모두 실제 저장소 관례(`from mvp import
  workflow_artifact_flow`, `sys.path.insert`)와 달랐다 — 기존 테스트
  파일을 보여주지 않았으므로 예상된 결과이며, harness가 이 부분만
  실제 관례에 맞게 보정해 기존 파일에 append했다(모델이 생성한 함수
  본문·assertion은 수정하지 않음).

### pytest 검증

수정된 import만 보정한 뒤 실제 `test_workflow_artifact_flow.py`에
append하여 실행(기존 4개 + 신규 1개, real Engine 포함):

```
10 passed in 57.62s
```

(A조건 파일 5개, B조건 파일 5개 — 각각 별도 임시 파일에서 검증 후
즉시 삭제.) 두 조건 모두 신규 E2E 테스트가 실제 `claude` CLI 호출을
거쳐 `{"context", "planning", "design", "implementation"}` 키 집합을
정확히 반환했다.

## 핵심 질문에 대한 답

> 대상 파일의 전체 Source를 Build Context에 제공할 경우, 좁은 Task에서도
> 기존 코드의 불필요한 재작성 또는 Scope 확장이 반복되는가?

**아니다 — 이번 통제 실험에서는 재현되지 않았다.** Full Source(생산
코드 6개 모듈 전문)를 제공해도, **대상 테스트 파일 자체를 보여주지
않은 이상** Scope 확장이나 불필요한 재작성은 발생하지 않았다.

T12·T13·T14를 종합하면:

| Task | 대상 파일이 Context에 노출됨? | 관찰된 동작 |
|---|---|---|
| T12 Manual/Automatic | 아니오(import 관례 헤더만) | 함수 1개만 반환 |
| T12 Full Source | 예(전체 파일 포함) | 파일 전체 재작성(내용은 정확) |
| T13 Automatic | 예(전체 파일 포함) | 파일 전체 재작성(내용은 정확) |
| T13 Full Source | 예(전체 파일 포함) | 파일 전체 재작성(내용은 정확) |
| T14 Automatic | 아니오 | 함수 1개만 반환 |
| T14 Full Source | 아니오 | 함수 1개만 반환 |

"파일 전체 재작성"이라는 형식적 현상은 **Full Source 여부가 아니라
대상 파일 자체가 Context에 노출됐는지 여부와 100% 일치**한다(4개 관측
전부 일치). 그리고 재작성이 일어난 T12/T13의 경우에도 기존 코드
내용은 항상 정확히 보존됐다 — "Scope Pollution"이 실제 코드 손상이나
요구사항 확장으로 이어진 사례는 지금까지 4개 Task, 6개 조건 중
**한 번도 없었다**.

## Automatic과의 차이

이번 실험에서 Automatic과 Full Source의 유일한 실질적 차이는 크기와
속도였다(prompt_chars 12,539 vs 22,749, elapsed 17.3s vs 6.9s — elapsed
차이는 방향이 일관되지 않아 Context 크기의 함수로 보기 어렵다).
결과물의 정확성·Scope 준수는 동일했다.

## 최종 판정

**B. Not Reproduced** — 세 번째 사례에서도 "Full Source가 원인이 되어"
Scope Pollution이 발생하지 않았다. T12에서 관찰된 현상은 Full Source
자체의 속성이 아니라 "대상 파일이 Context에 노출되는가"라는 별개
변수에 기인한 것으로 보이며, 이번 통제 실험이 그 설명과 일치하는
세 번째 데이터 포인트를 제공한다.

단, "재작성 형식"이 나타나더라도 지금까지 내용 손상 사례가 없었다는
점에서, Full Source 자체를 위험 요인으로 볼 근거는 약하다 — 오히려
"기존 파일을 Context로 보여줄 때는 출력이 전체 파일 형태가 될 수
있다"는 것은 Build 단계의 별도 처리 규칙(예: diff 적용 방식)이 필요할
수 있다는 시사점으로 남긴다(구현 아님).

## 다음 Research

1. "대상 파일 노출 여부"를 독립 변수로 명시적으로 조작하는 2x2 실험
   (노출 유/무 × Automatic/Full Source)으로 이 설명을 직접 검증한다
   (지금까지는 조건이 우연히 일치했을 뿐, 의도적으로 4개 셀을 모두
   채운 적은 없다).
2. Design이 실제 함수 시그니처를 보지 못해 존재하지 않는
   파일시스템 스캐폴딩(tmp_path/git workspace)을 제안한 사례가 이번에도
   재현됨 — Design 단계에 최소한의 시그니처 정보를 주는 것이 Build
   품질에 미치는 영향을 별도로 검증할 가치가 있다(구현 아님).

```text
Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: 36 passed (mvp 전체), 임시 비교 파일(_t14_condition_a.py/_t14_condition_b.py)은 검증 후 삭제, git status clean 확인
E2E: PASS (A, B 모두 real Engine E2E 통과)
PR: NOT CREATED
Commit: (아래 커밋 해시)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: YES
Next Implementation Candidate: (1) "대상 파일 노출 여부 × Automatic/Full Source" 2x2 통제 실험으로 이 설명을 직접 검증하는 Research, (2) Design 단계에 최소 함수 시그니처를 제공했을 때 파일시스템 스캐폴딩 오판이 줄어드는지 검증하는 Research (둘 다 구현 아님)
```
