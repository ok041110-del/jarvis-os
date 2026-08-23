# Literal Excerpt 자동 판별 Research

**문서 성격**: Research/Dogfooding. Context 시스템/Component/Interface를
구현하지 않는다. Production 코드를 수정하지 않는다. Architecture/
Contract를 변경하지 않는다.

## 1. T10 Evidence (재인용)

`DEV-HQ-V2.0-LITERAL-CODE-EXCERPT-RESEARCH-0001.md`가 확인한 사실:
사람이 직접 고른 리터럴 발췌(대상 함수 + `CATEGORY_PATHS`/`ROOT` 등
전역 + `_relevant_files` + import 관례)만으로도 전체 소스 파일(Full
Source)과 동일한 Build 정확성(3/3 pass, 오류 없음)을 얻었다. 다만
"발췌 범위를 어떻게 자동으로 정할 것인가"는 그 문서 스스로 사람이
사전에 코드를 읽고 판단했다고 명시하며 Open Issue로 남겼다. T11은 이
자동화 가능성을 검증한다.

## 2. 실험 조건 (A/B/C)

동일한 Design(T08 Stage 03 산출물, 재사용)을 유지하고, Build에 주는
Context만 바꿨다.

| 조건 | 구성 방법 | 사람 개입 |
|---|---|---|
| **A. Manual**(T10 재사용) | 이 문서 작성자가 소스를 읽고 직접 선택 | 전체 판단을 사람이 수행 |
| **B. Automatic(신규)** | `ast` 모듈로 정적 분석 — 아래 §3 알고리즘 | 대상 함수 이름 지정 1건만 |
| **C. Full Source**(T09/T10 재사용) | 관련 파일 전문 | 파일 선택만 사람이 수행 |

## 3. 자동 추출 방법(코드 분석, LLM 미사용)

`hqs/development/mvp/project_intelligence.py`를 `ast.parse()`로
파싱하고, 순수 Python 표준 라이브러리(`ast`)만으로 다음을 계산했다
(스크립트 자체는 연구용 스크립트이며 저장소에 커밋하지 않았다 —
아래에 재현 가능하도록 로직만 기록한다).

1. **대상 함수 지정**(유일한 인간 입력): `collect_relevant_context`.
2. **직접 참조 수집**: 대상 함수 AST 서브트리를 순회해 Load-context
   `Name` 노드를 전부 모으고, 모듈 최상위 정의(함수/클래스/할당)
   이름과 교집합을 구한다.
3. **고정점까지 재귀**: 새로 발견된 각 이름의 정의도 같은 방식으로
   순회해, 더 이상 새 이름이 나오지 않을 때까지 반복한다(직접 호출
   → 그 함수가 참조하는 것 → ... 전이적 폐쇄).
4. **필요한 import만 선별**: 폐쇄 집합 전체에서 실제로 쓰인 이름과
   원본 `import`/`from import` 문의 바인딩 이름을 대조해 실제로
   필요한 import문만 골라낸다.
5. **import 관례**: 별도로, 기존 테스트 파일 하나(`test_workflow_
   project_intelligence.py`)를 같은 방식으로 파싱해 "docstring 이후
   첫 non-import 문 이전까지"의 import 블록만 추출한다(휴리스틱이지만
   AST 기반이며 LLM 추측이 아니다).

## 4. Manual vs Automatic — 실제로 무엇을 판별했는가

| 최상위 이름 | Manual(T10) 포함 | Automatic(신규) 포함 | 실제로 필요한가(직접 확인) |
|---|---|---|---|
| `ROOT` | 포함 | 포함 | 필요(`CATEGORY_PATHS`, `_relevant_files`가 참조) |
| `_KERNEL_CORE`/`_EXECUTION_LAYER` | 포함 | 포함 | 필요(`CATEGORY_PATHS` 정의에 사용) |
| `CATEGORY_PATHS` | 포함 | 포함 | 필요(대상 함수가 직접 순회) |
| `_relevant_files` | 포함 | 포함 | 필요(대상 함수가 직접 호출) |
| `collect_relevant_context` | 포함(대상) | 포함(대상) | 대상 자체 |
| `validate_issue` | **누락** | 포함 | **필요**(대상 함수 1번째 줄에서 직접 호출) |
| `_keywords` | **누락** | 포함 | **필요**(대상 함수가 직접 호출) |
| `_directory_structure` | **누락** | 포함 | **필요**(대상 함수가 직접 호출) |
| `IssueValidationError` | 누락 | 포함 | 필요(`validate_issue`가 raise) |
| `_score` | 누락 | 포함 | 필요(`_relevant_files`가 호출 — 2단계 전이) |
| `_STOPWORDS` | 누락 | 포함 | 필요(`_keywords`가 참조 — 2단계 전이) |
| `_NOISE_DIR_NAMES` | 누락 | 포함 | 필요(`_directory_structure`가 참조 — 2단계 전이) |

**중요한 발견**: T10의 "Manual"은 실제로는 **불완전한 발췌**였다 —
대상 함수가 직접 호출하는 `validate_issue`/`_keywords`/
`_directory_structure` 3개를 빠뜨리고도 3/3 pass를 냈을 뿐이다(생성된
테스트들이 우연히 그 3개 함수의 내부 동작에 의존하지 않는 경로만
검증했기 때문으로 보인다 — 근본적으로 안전하게 완비된 발췌는
아니었다). **Automatic은 정적 분석으로 이 3개 + 전이적으로 필요한
3개까지, 대상 함수의 실제 의존성 전체(12개 이름 + 2개 import)를
빠짐없이 포함했다** — 사람이 놓친 것을 기계적 분석이 놓치지 않았다.

## 5. 누락/과잉 포함

- **누락**: Automatic에서는 발견되지 않았다 — 대상 함수의 전이적
  의존성 폐쇄를 전부 포함했다.
- **과잉 포함**: 엄밀히 없다 — §4에서 확인했듯 Automatic이 Manual보다
  더 많이 포함한 7개 이름 전부가 실제로 대상 함수의 직접 또는
  전이적 의존성이었다(불필요한 것을 끼워 넣지 않았다). 다만 원본
  파일 전체(183줄) 대비로는 여전히 발췌이며, `agents.py`처럼 완전히
  무관한 다른 파일은 가져오지 않았다.

## 6. Build/Test 결과

동일 절차(생성 코드를 `hqs/development/mvp/tests/`에 임시 배치 →
`pytest` 직접 실행 → 결과 기록 → 즉시 삭제 → `git status`로 원상
복구 확인)로 검증했다.

```
$ cp <Automatic 산출물> hqs/development/mvp/tests/_t11_condition_b.py
$ python3 -m pytest hqs/development/mvp/tests/_t11_condition_b.py -q
3 passed in 0.02s
$ rm hqs/development/mvp/tests/_t11_condition_b.py
$ git status --porcelain   # 출력 없음
$ python3 -m pytest hqs/development/mvp/tests/ -q   # 기존 36건 재확인
36 passed in 43.98s
```

| 조건 | pytest 결과 | 비고 |
|---|---|---|
| A(Manual) | 3/3 pass | T10 |
| **B(Automatic, 신규)** | **3/3 pass** | 이번 실행. `ROOT`를 `CATEGORY_PATHS`와 함께 patch해야 하는 이유까지 스스로 정확히 설명(docstring에 "`_relevant_files()` calls `path.relative_to(ROOT)`..." 명시) |
| C(Full Source) | 3/3 pass | T09/T10 |
| (참고) D(Fact Summary) | 0/3 fail | T09/T10 |
| (참고) 기존 없음(A0) | 0/3 fail(Import 실패) | T08/T09 |

## 7. Context 크기·실행 시간

| 조건 | Prompt 크기(문자) | 실행 시간 |
|---|---|---|
| Manual | 5,625 | 50.0초 |
| **Automatic** | **7,904**(Manual 대비 1.4배, Full Source 대비 52%) | **51.2초** |
| Full Source | 15,141 | 22.1초 |

Automatic은 Manual보다 커졌다(더 완비된 의존성을 포함했으므로 당연한
결과) — 그래도 Full Source의 절반 수준이다. 실행 시간은 이번
표본에서도 Manual/Automatic 두 "발췌형" 조건이 Full Source보다 오래
걸렸다(T10에서 관찰된 패턴이 재현됨) — 표본이 조건당 1회뿐이라
일반화하지 않는다(Open Issue로 재기록).

## 8. 사람 개입 필요 여부

- **Manual(T10)**: 사람이 전체 파일을 읽고 "무엇이 직접 의존인지"를
  판단 — 그 결과 실제로는 불완전했다(§4).
- **Automatic(이번)**: 사람이 필요한 것은 **대상 함수 이름 1개
  지정**뿐이었다. 그 외 전이적 폐쇄 계산, import 선별, 발췌 조립은
  전부 기계적(AST 순회)으로 이뤄졌다 — 코드 이해나 판단이 필요
  없었다.

## 9. 최종 판정

### A. Validated — Automatic이 Manual과 동등(이번 대상에서는 더 완비됨)

근거: 자동 추출(B)이 수동 발췌(A/Manual)와 동일하게 3/3 pass, 동일한
오류 프로파일(전 오류 유형 없음)을 냈다. 게다가 자동 추출은 Manual이
실수로 빠뜨린 3개의 직접 의존 함수(`validate_issue`, `_keywords`,
`_directory_structure`)와 그 전이적 의존 3개를 빠짐없이 포함해,
**단순 동등이 아니라 더 원칙적으로 완비된 결과**를 냈다. 사람 개입은
"대상 함수 이름 지정" 1건으로 줄었다.

**한정 조건**: 이번 검증은 단일 대상 함수(`collect_relevant_context`,
183줄 파일 내)에 한정된다. 더 복잡한 의존 그래프(다중 모듈에 걸친
호출, 동적 디스패치, 데코레이터로 가려진 참조 등)에서도 같은 정적
분석 방식이 통하는지는 확인하지 못했다 — 아래 Open Issues 참조.

## 10. Open Issues

1. 대상이 여러 파일/모듈에 걸쳐 있을 때(예: `workflow_0008.py`처럼
   다른 모듈의 함수를 import해서 쓰는 경우)도 같은 AST 폐쇄 알고리즘이
   모듈 경계를 넘어 올바르게 동작하는지 확인하지 않았다.
2. import 관례 추출 휴리스틱("docstring 이후 첫 non-import 문 이전")이
   모든 기존 테스트 파일에 대해 안정적으로 동작하는지는 1개 파일로만
   확인했다.
3. Automatic/Manual 두 "발췌형" 조건에서 반복적으로 관찰된 "Full
   Source보다 실행 시간이 긴" 현상의 원인은 여전히 밝히지 못했다
   (표본 수 부족).
4. 이번 대상은 클래스 상속, 데코레이터, 조건부 정의(`if TYPE_CHECKING`
   등)가 없는 비교적 단순한 모듈이다 — 그런 패턴이 있는 코드에서도
   같은 폐쇄 알고리즘이 안전한지 확인하지 않았다.

## 11. Next Task (구현 아님 — Evidence 기반 제안)

T09~T11 종합: Source Context는 Build 오류를 실질적으로 줄이고(T09),
전체 파일이 아니라 신중하게 고른 발췌로도 충분하며(T10), 그 발췌를
사람이 아니라 정적 분석(AST 전이적 폐쇄)으로 자동 구성해도 최소한
동등한(이번 사례에서는 더 완비된) 결과를 얻는다(T11)는 것이 실증됐다.
다음으로 고려할 수 있는 것(구현 아님, RFC/ADC 등 별도 절차 필요):

1. 여러 모듈에 걸친 의존성에서도 같은 방식이 통하는지 별도로 검증.
2. 만약 실제로 Pipeline에 반영하기로 결정한다면, 이는 기존
   `collect_relevant_context()`가 이미 반환하는 `source_code`/
   `existing_workflow` 카테고리의 파일 경로를, "파일 전체 내용"이
   아니라 "그 파일에서 실제로 필요한 최소 발췌"로 대체하는 형태가
   될 것이라는 방향성만 기록한다 — 결정은 이 문서의 범위가 아니다.

---

## 최종 보고

1. **무엇을 실험했는가** — T10의 Manual 발췌를, 순수 `ast` 정적 분석
   기반 자동 추출(대상 함수의 전이적 의존성 폐쇄 + import 관례
   추출)로 대체할 수 있는지 real Engine으로 검증했다.
2. **무엇을 자동 판별했는가** — 대상 함수가 직접·전이적으로 참조하는
   전역/상수/함수/import 전부(12개 이름 + 2개 import)를 기계적으로
   판별했다. 사람 개입은 대상 함수 이름 지정 1건뿐이었다.
3. **무엇을 놓쳤는가** — Automatic 자체는 놓친 것이 없었다(§5). 오히려
   **Manual(T10, 사람이 직접 선택)이** 대상 함수의 직접 호출 3개
   (`validate_issue`, `_keywords`, `_directory_structure`)를 놓쳤다는
   사실이 이번에 드러났다.
4. **Manual 대비 결과** — 동일하게 3/3 pass, 동일한 오류 프로파일.
   Automatic이 더 완비됐다(§4). 크기는 Manual보다 1.4배 컸으나 Full
   Source의 52%에 그쳤다.
5. **최종 판정** — **A. Validated**(이번 대상 규모에서는 Automatic이
   Manual과 동등하거나 더 신뢰할 수 있음 — 단일 모듈, 단순 구조라는
   한정 조건 포함).
6. **다음 Task** — 다중 모듈에 걸친 의존성에서도 같은 정적 분석
   방식이 통하는지 검증하는 별도 Research Task를 제안한다(구현 아님).

---

Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: 36 passed(기존 스위트, 비교용 임시 파일은 실험 직후 삭제하고
`git status`로 원상 복구 확인)
E2E: PASS(비교 실험 목적 — real Engine 신규 호출 1건 + T09/T10 결과
재사용으로 3-조건 비교 완결)
PR: NOT CREATED
Commit: (아래 참조)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: (아래 참조)
Next Implementation Candidate: 다중 모듈에 걸친 의존성에서도 AST 기반
전이적 폐쇄 자동 추출이 통하는지 검증하는 Research Task(§11, 구현 아님)
