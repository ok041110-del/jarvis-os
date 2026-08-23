# Literal Code Excerpt Research

**문서 성격**: Research/Dogfooding. Context 시스템을 구현하지 않는다.
Production 코드를 수정하지 않는다. Architecture/Contract를 변경하지
않는다. 신규 Component/Interface를 추가하지 않는다.

## 1. 목적

T09가 "전체 소스 파일(B)은 Build 오류를 없애지만, 자연어 사실 요약
(T09의 C, 본 문서의 D)은 불충분하다"는 것을 실증했다. T09 §11-1은
"코드 일부(리터럴 발췌)"를 별도로 시험하지 않았다는 것을 Open Issue로
남겼다. T10은 그 빈틈을 메운다 — **전체 소스와 최소 리터럴 발췌
사이에 실제로 차이가 있는지**를 검증한다.

## 2. 실험 조건 (A/B/C/D)

T09와 **동일한 Design 산출물**(T08 Stage 03 출력, 2,831자)을 그대로
재사용해 통제 변수를 없앴다. A/B/D는 T09에서 이미 실행한 결과를
재사용(재실행 없음), **C만 이번에 신규로 real Engine 실행**했다.

| 조건 | 내용 | 출처 |
|---|---|---|
| **A. 기존 경로/메타데이터** | Design 텍스트만 | T09 재사용(T08 원본) |
| **B. Full Source(Reference Control)** | Design + `project_intelligence.py` 전문(7,939자) + 기존 테스트 파일 전문(5,191자) | T09 재사용 |
| **C. Literal Excerpt(신규)** | Design + 저장소에서 **그대로 복사한**(재작성·요약 없음) 코드 조각: `ROOT`/`_KERNEL_CORE`/`_EXECUTION_LAYER`/`CATEGORY_PATHS`(전역·상수, 8행), `_relevant_files()`(직접 의존 함수, 20행), `collect_relevant_context()`(대상 함수, 6행), 기존 테스트 파일의 import 관례(6행) | 이번 실행 |
| **D. Fact Summary** | Design + 자연어 사실 요약 3문장(모듈 경로, 최상위 시그니처, sys.path 관례) | T09 재사용(T09의 "조건 C") |

C에 포함한 최소 후보 5종(요청 문서가 명시한 목록)과 실제 매핑:

| 요청 최소 후보 | C에 포함된 실제 발췌 |
|---|---|
| module/import | 기존 테스트 파일의 `sys.path.insert(...)` + `from mvp import ...` 6행(그대로 복사) |
| 대상 function/class | `collect_relevant_context()` 전체 6행(그대로 복사) |
| 실제 signature | 위 함수 정의 줄에 포함(`def collect_relevant_context(issue: dict) -> dict:`) |
| 관련 전역/상수 | `ROOT`, `_KERNEL_CORE`, `_EXECUTION_LAYER`, `CATEGORY_PATHS` 전체 dict(그대로 복사, T07이 수정한 3-tuple 구조 포함) |
| 직접 의존 자료구조 | `_relevant_files()` 전체 정의(그대로 복사, `directories`가 `Path` 또는 tuple을 받는다는 T07의 방어 로직 포함) |

## 3. Build 결과 — 실제 pytest 실행으로 비교

T09와 동일한 절차(생성 코드를 `hqs/development/mvp/tests/`에 임시
배치 → `pytest` 직접 실행 → 결과 기록 → 즉시 삭제 → `git status`로
원상 복구 확인)를 따랐다.

```
$ cp <조건 C 산출물> hqs/development/mvp/tests/_t10_condition_c.py
$ python3 -m pytest hqs/development/mvp/tests/_t10_condition_c.py -q
3 passed in 0.02s
$ rm hqs/development/mvp/tests/_t10_condition_c.py
$ git status --porcelain   # 출력 없음, 원상 복구 확인
$ python3 -m pytest hqs/development/mvp/tests/ -q   # 기존 36건 재확인
36 passed in 49.78s
```

| 조건 | pytest 결과 | 비고 |
|---|---|---|
| A | 0/3(수집 자체 실패) | `ModuleNotFoundError: No module named 'myproject'`(T09) |
| B | **3/3 pass** | 회귀 없음(T09) |
| **C(신규)** | **3/3 pass** | 회귀 없음. `pi.ROOT`/`pi.CATEGORY_PATHS`를 정확히 monkeypatch하고, `pi._relevant_files()`를 실제 시그니처(`keywords, directories, pattern, exclude_dirs`)로 직접 호출까지 했다 |
| D | 0/3 fail | `TypeError: cannot unpack non-iterable PosixPath object`(T09) |

## 4. Context 크기·실행 시간

| 조건 | Prompt 크기(문자) | 실행 시간 |
|---|---|---|
| A | 2,831 | 31.9초 |
| B | 15,141(A 대비 5.3배) | 22.1초 |
| **C** | **5,625(A 대비 2.0배, B 대비 37%)** | **50.0초** |
| D | 3,483(A 대비 1.2배) | 26.8초 |

**관찰**: C는 B 대비 프롬프트 크기를 63% 줄이면서도 동일하게 3/3
pass를 냈다 — 크기 면에서는 "최소 충분 Context"에 근접한 후보다.
다만 **실행 시간은 4개 조건 중 C가 가장 길었다**(50.0초, B의 2.3배) —
표본이 조건당 1회뿐이라 이것이 "발췌 자체의 특성"인지 "이번 실행의
우연한 변동"인지는 이번 실험만으로 분리할 수 없다(§7 Open Issue).

## 5. 오류 비교

| 오류 유형 | A | B | C | D |
|---|---|---|---|---|
| Module name 오류 | 있음 | 없음 | 없음 | 없음 |
| Import 오류 | 있음 | 없음 | 없음 | 없음 |
| Function signature 오류 | 있음 | 없음 | 없음 | 없음(전달한 사실 범위 내) |
| 기존 코드 구조 오인(`CATEGORY_PATHS` shape 등) | 있음 | 없음 | **없음** | 있음 |
| Design→Build 정보 손실 | 있음 | 관찰되지 않음 | **관찰되지 않음** | 부분적으로 있음 |

C는 B와 **동일한 오류 프로파일**(전 항목 없음)을 보였다 — D가 실패한
바로 그 지점(`CATEGORY_PATHS`의 3-tuple 내부 구조)을 C는 리터럴로
포함했기 때문에 정확히 맞혔다. 이는 T09가 제기한 가설("D의 실패는
선택 기준이 불완전했기 때문이지, 선택적 접근 자체의 문제가 아니다")을
직접 뒷받침하는 결과다.

## 6. 최종 판정

### A. Minimal Context Validated — Excerpt만으로 Full Source와 동등

근거: C(리터럴 발췌, B 대비 37% 크기)가 B(전체 소스)와 **동일하게**
3/3 pass, 동일한 오류 프로파일(전 항목 없음)을 냈다. 이번 대상
파일(`project_intelligence.py`, 183줄) 규모에서는, "관련 전역/상수 +
대상 함수 + 직접 의존 함수 + 실제 import 관례"만 그대로 발췌해도
전체 파일을 넣은 것과 동등한 결과를 얻었다.

**한정 조건**: 이 판정은 "이번 실험이 다룬 대상과 발췌 범위"에
한정된다 — 발췌에 무엇을 포함해야 하는지(예: `_relevant_files`처럼
직접 의존하는 함수까지 포함해야 함)는 **사전에 코드를 읽고 판단해야
확정 가능**했다(§7 Open Issue 1). "아무 3~5줄이나 발췌해도 된다"는
뜻이 아니다.

## 7. Open Issues

1. **발췌 범위를 어떻게 자동으로 정할 것인가**는 이번 실험이 다루지
   않았다 — 이번 발췌는 이 문서 작성자가 실제 코드를 미리 읽고
   "무엇이 직접 의존 관계인지"를 수동으로 판단해 구성했다. 자동으로
   최소 발췌 범위를 판별하는 방법(예: 정적 분석으로 호출 그래프
   추적)은 검증하지 않았다.
2. C의 실행 시간(50.0초)이 4개 조건 중 가장 길었던 것이 발췌
   자체의 특성인지 우연인지 — 표본 1회로는 분리 불가.
3. 대상 파일 규모(183줄)가 작다 — 훨씬 큰 파일/여러 파일에 걸친
   의존성이 있는 경우에도 "발췌만으로 충분"이 유지되는지는
   확인하지 못했다.
4. 이번에도 조건당 표본이 1회뿐이다(Engine 응답 비결정성 미반영).

## 8. Next Task (구현 아님 — Evidence 기반 제안)

T09+T10 종합 결론: Design→Build 정보 손실을 줄이는 데 **전체 소스
파일 전송이 필수는 아니며, 신중하게 고른 리터럴 발췌로도 충분함**이
이번 대상에서 실증됐다. 다음으로 고려할 수 있는 것(구현 아님):

1. §7-1의 "발췌 범위 자동 판별"을 별도로 연구 — 예를 들어 Stage 01
   (`collect_relevant_context`)이 이미 반환하는 `source_code`/
   `existing_workflow` 카테고리의 파일 **경로**를, 그 파일들의
   **내용**으로 확장하는 것이 실질적으로 이번 실험의 "C 조건"에
   해당하는지 검토.
2. 만약 실제로 Context 전달 방식을 바꾸기로 결정한다면 RFC/ADC
   또는 최소 별도 Task 승인이 선행되어야 한다 — 이 문서는 그 결정을
   내리지 않는다.

---

## 최종 보고

1. **무엇을 실험했는가** — T09의 A/B/D(재사용)에 더해, 저장소 코드를
   그대로 복사한 **리터럴 발췌(C)**를 신규로 real Engine 실행하고,
   생성된 테스트 코드를 실제 pytest로 실행해 4개 조건을 비교했다.
2. **최소 충분 Context는 무엇인가** — 대상 함수(`collect_relevant_
   context`), 그 함수가 직접 참조하는 전역·상수(`ROOT`,
   `CATEGORY_PATHS` 등), 직접 의존하는 헬퍼 함수(`_relevant_files`),
   실제 import 관례 — 이 4가지를 **그대로 발췌**하면 충분했다.
3. **Full Source 대비 차이** — 오류 프로파일은 동일(3/3 pass, 전
   오류 유형 없음)했고 프롬프트 크기는 37%(B 대비)로 줄었다. 다만
   실행 시간은 이번 표본에서 오히려 더 길었다(50.0초 vs 22.1초).
4. **비용/부작용** — 발췌 구성 자체에 사전 코드 파악이 필요했다(자동화
   아님). 크기 절감 효과는 확인됐으나 실행 시간 이점은 이번 실험에서
   나타나지 않았다.
5. **최종 판정** — **A. Minimal Context Validated**(단, 발췌 범위
   선정에 사전 코드 이해가 필요하다는 한정 조건 포함).
6. **다음 Task** — 발췌 범위를 자동으로 판별하는 방법을 검토하는
   별도 Research Task를 제안한다(구현 아님).

---

Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: 36 passed(기존 스위트, 비교용 임시 파일은 실험 직후 삭제하고
`git status`로 원상 복구 확인)
E2E: PASS(비교 실험 목적 — real Engine 신규 호출 1건 + T09 결과 3건
재사용으로 4-조건 비교 완결)
PR: NOT CREATED
Commit: (아래 참조)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: (아래 참조)
Next Implementation Candidate: 발췌 범위(대상 함수 + 직접 의존 전역/
함수)를 자동으로 판별하는 방법을 검토하는 Research Task(§8, 구현 아님)
