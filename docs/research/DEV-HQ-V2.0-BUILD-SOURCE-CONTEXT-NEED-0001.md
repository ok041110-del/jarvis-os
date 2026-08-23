# Build Source Context Need Research

**문서 성격**: Research/Dogfooding. Context 시스템을 구현하지 않는다.
Architecture/Contract를 변경하지 않는다. 신규 Component/Interface를
추가하지 않는다. 이 문서는 "Source Context가 Build 품질을 개선하는가"
라는 질문에 Evidence로만 답한다.

## 1. T08 Evidence (재인용)

`DEV-HQ-V2.0-01-05-WORKFLOW-DOGFOODING-0002.md` §7이 확인한 사실:
Stage 04(Build)가 실제 저장소와 무관한 모듈 이름(`myproject`)과 함수
시그니처(문자열 query)로 코드를 생성했다 — Planning/Design/Build 중
어느 Capability도 실제 소스 파일 내용을 받지 않고, 파일 경로 목록과
자연어 Design 텍스트만 받기 때문이라고 분석했다(§7 근본 원인 분석).
이번 T09는 그 분석이 **실제로 Build 오류를 줄이는지**를 실험으로
검증한다.

## 2. 실험 Task

T08과 **동일한 Design 산출물**(T08 Stage 03의 실제 출력, 2,831자)을
그대로 재사용해, Build 단계에만 서로 다른 Context를 주고 결과를
비교했다 — Design 품질 차이를 통제 변수로 제거하기 위함이다.

## 3. Context 조건 (A/B/C)

| 조건 | 내용 | Prompt 크기(문자) |
|---|---|---|
| **A. 기존 Context**(T08 그대로 재사용) | Design 텍스트만 | 2,831 |
| **B. 전체 소스 파일** | Design + `project_intelligence.py` 전문(7,939자) + `test_workflow_project_intelligence.py` 전문(5,191자, 실제 import 관례 예시) | 15,141(A 대비 약 5.3배) |
| **C. 선택적 사실**(코드 일부가 아니라 검증된 사실 요약) | Design + "실제 import 경로는 `from mvp.project_intelligence import ...`다", "실제 시그니처는 `collect_relevant_context(issue: dict) -> dict`다(문자열 query 아님)", "테스트는 `sys.path.insert(...)`로 repo root를 추가한다" 3문장 | 3,483(A 대비 약 1.2배) |

세 조건 모두 `backend_agent_code_generation()`과 **동일한 instruction
문구**("Based on the following design, write the implementation code.
Return only the code, with no surrounding commentary.")로
`call_engine()`을 직접 호출했다(실제 `claude` CLI subprocess, Mock
없음). A는 T08에서 이미 실행한 결과를 재사용했고(재실행 없음), B·C만
이번에 새로 실행했다.

## 4. Build 결과 비교 — 생성된 코드를 실제로 실행

생성된 코드 3건을 **실제 `hqs/development/mvp/tests/`에 임시로
배치해 `pytest`로 직접 실행**했다(비교 직후 삭제, `git status`로 원상
복구 확인 — §8). 추측이 아니라 실행 결과로 판정했다.

| 조건 | pytest 결과 | 실패 원인 |
|---|---|---|
| **A** | **수집 단계에서 즉시 에러**(0/3) | `ModuleNotFoundError: No module named 'myproject'` — 존재하지 않는 패키지 이름 |
| **B** | **3 passed** | 없음 |
| **C** | **3 failed**(0/3) | `TypeError: cannot unpack non-iterable PosixPath object` — `CATEGORY_PATHS`의 실제 값이 `(directory, pattern, exclude_dirs)` 3-tuple이라는 사실을 전달받지 못해, 코드가 `{category: 단일 Path}` 형태로 잘못 가정함 |

## 5. 오류 비교 (T09 확인 항목별)

| 오류 유형 | A(기존) | B(전체 소스) | C(선택적 사실) |
|---|---|---|---|
| Module name 오류 | **있음**(`myproject`) | 없음 | 없음 |
| Function/class name 오류 | 없음 | 없음 | 없음 |
| Function signature 오류 | **있음**(문자열 query로 가정) | 없음 | 없음(이 부분은 사실로 명시했으므로 정확) |
| Import 오류 | **있음**(패키지 자체가 없음) | 없음 | 없음(import 경로는 정확) |
| 기존 코드 구조 오인 | **있음**(반환 타입까지 틀림) | 없음 | **있음**(`CATEGORY_PATHS` 내부 값 shape — 전달되지 않은 세부사항) |
| Design→Build 정보 손실 | **있음**(T08에서 이미 확인) | **관찰되지 않음** | **부분적으로 있음**(전달한 사실은 반영, 전달하지 않은 세부는 스스로 알아내지 못함) |

**핵심 관찰**: B는 A가 겪은 모든 오류를 없앴을 뿐 아니라, **B가
스스로 알아낸 세부사항**(`CATEGORY_PATHS`의 3-tuple 구조,
`_relevant_files()`가 `ROOT` 모듈 전역을 참조해 상대 경로를 계산하므로
`monkeypatch.setattr(pi, "ROOT", tmp_path)`도 함께 해야 한다는 점)까지
정확히 반영했다 — 이는 Design 텍스트나 C의 "선택적 사실" 어디에도
언급되지 않은 내용이며, **전체 소스 파일을 실제로 읽었을 때만 얻을 수
있는 정보**였다. C는 내가 사실로 명시한 3가지(모듈 경로, 최상위
시그니처, sys.path 관례)는 정확히 반영했지만, 명시하지 않은 내부
자료구조(3-tuple)는 여전히 잘못 가정했다 — **부분적 사실 제공은
언급되지 않은 오류를 막지 못한다**는 것을 실증했다.

## 6. Context/Token 비용

- B는 A 대비 프롬프트 크기 약 5.3배(2,831→15,141자, 대략 700→3,800
  토큰 추정치), C는 약 1.2배(2,831→3,483자).
- **실행 시간은 오히려 B가 가장 짧았다**(B 22.1초 < C 26.8초 < A
  31.9초, T08 원본) — 이번 3개 표본만으로는 "Context가 커지면 느려진다"
  는 관계가 성립하지 않았다. 표본이 작아(각 조건 1회) 일반화하지
  않는다.
- **불필요한 정보 유입 징후**: B의 생성 결과(§8 전체 코드, 3개 함수
  73줄)는 A(3개 함수, 유사 길이)·C(3개 함수, 유사 길이)와 산출물
  규모가 비슷했다 — 소스 전문을 넣었다고 산출물이 불필요하게
  길어지거나 관련 없는 내용이 섞여 들어간 정후는 관찰되지 않았다.

## 7. 실행 가능성 (§4의 재정리)

- A: 실행 불가(Import 단계에서 즉시 실패).
- B: **완전히 실행 가능**(3/3 pass, 실제 pytest로 확인).
- C: 실행 불가(3/3 fail, 그러나 A와 다른 지점에서 실패 — import는
  성공하고 런타임 로직에서 실패).

## 8. 재현 절차(투명성을 위해 기록)

```
$ cp <조건 A/B/C 산출물> hqs/development/mvp/tests/_t09_condition_{a,b,c}.py
$ python3 -m pytest hqs/development/mvp/tests/_t09_condition_a.py -q
# ModuleNotFoundError: No module named 'myproject'
$ python3 -m pytest hqs/development/mvp/tests/_t09_condition_b.py -q
# 3 passed in 0.03s
$ python3 -m pytest hqs/development/mvp/tests/_t09_condition_c.py -q
# 3 failed — TypeError: cannot unpack non-iterable PosixPath object
$ rm hqs/development/mvp/tests/_t09_condition_{a,b,c}.py   # 임시 파일 즉시 삭제
$ git status --porcelain   # 변경 없음 확인
$ python3 -m pytest hqs/development/mvp/tests/ -q   # 기존 36건 재확인, 회귀 없음
```

## 9. 세 가지 가능성에 대한 판단

1. **필요한 파일 전체(조건 B)**: 이번 실험에서 유일하게 완전히
   성공했다. 다만 실험이 다룬 대상 파일이 작아(약 8KB) 대규모 파일에도
   같은 결론이 적용되는지는 확인하지 못했다.
2. **필요한 코드 일부(선택적)**: 이번에 **정확히 이 조건을 테스트하지
   않았다** — 조건 C는 "코드 일부(리터럴 코드 조각)"가 아니라 "코드에
   대한 자연어 사실 요약"이었다. C의 실패(§4, §5)는 "선택적 정보
   자체가 무의미하다"는 근거가 아니라 "내가 선택한 사실 목록이
   불완전했다"는 근거에 가깝다 — 예를 들어 `CATEGORY_PATHS`의 실제
   3-tuple 정의를 리터럴 코드로 한 줄 포함했다면 결과가 달라졌을
   가능성이 있다. **이 구분은 다음 실험에서 검증이 필요하다**(§10).
3. **기존 경로 + 선택적 Source Context(조건 A)**: 이번 실험에서
   가장 나쁜 결과(즉시 Import 실패)를 냈다 — 현재 상태 그대로는
   불충분함이 재확인됐다.

**결론**: "전체 파일을 무조건 넣어야 하는가"는 이번 실험만으로
확정할 수 없지만("코드 일부"를 제대로 시험하지 않았으므로), "지금처럼
경로 목록과 자연어 사실 몇 개만으로는 부족하다"는 것과 "실제 소스
전문을 주면 확실히 해결된다"는 것은 실증됐다.

## 10. 최종 판정

### A. Source Context Need Validated

근거: 조건 B(전체 소스)가 조건 A(기존, 현재 Pipeline 상태)에서
관찰된 **모든 오류 유형**(module name, import, function signature,
기존 코드 구조 오인, Design→Build 정보 손실)을 제거했고, 실제
`pytest` 실행으로 3/3 pass를 확인했다. 이는 추정이 아니라 실행
결과다.

**단서(Case 판정에 영향 없는 보충 관찰)**: 조건 C(선택적 사실)는
전달한 정보에 한해서만 정확했고 전달하지 않은 세부(내부 자료구조
shape)에서는 여전히 실패했다 — 즉 "약간의 Context"로는 부족했다.
이것이 "선택적 Context 자체가 무효"라는 뜻은 아니다(§9-2) — "이번에
고른 선택 기준이 불충분했다"는 뜻이다. 따라서 **B. Partial Need로
격하하지 않는다** — Evidence는 명확히 "Source Context가 오류를
줄인다"는 방향을 가리키며, 다만 "어느 만큼의 Source Context가
최소 충분선인가"는 별도 실험이 필요한 열린 질문으로 남긴다.

## 11. Open Issues

1. "코드 일부(리터럴 발췌)"를 실제로 시험하지 않았다 — 예를 들어
   `CATEGORY_PATHS` 정의 5줄 + `collect_relevant_context()` 시그니처와
   loop 1줄만 발췌해 제공하는 조건을 시험하면, "전체 파일 대 선택적
   발췌"의 실제 손익분기점을 더 정확히 알 수 있다.
2. 이번 실험은 대상 파일이 작다(8KB, 183줄) — 훨씬 큰 파일(수백~수천
   줄)에서도 "전체 소스 제공"이 같은 효과를 내는지, 아니면 Token
   비용이 실질적 제약이 되는지는 확인하지 못했다.
3. 표본이 조건당 1회뿐이다 — Engine 응답의 비결정성(T01/T04가 이미
   기록한 출력 언어 비결정성 등)을 고려하면, 반복 실행으로 결과가
   안정적인지 확인이 필요하다.
4. 이번 실험은 Build(Stage 04) 1개 지점만 다뤘다 — Design(Stage 03),
   Planning(Stage 02)에도 소스 Context를 주면 어떤 효과가 있는지는
   다루지 않았다.

## 12. Next Task (구현 아님 — Evidence 기반 제안)

Source Context가 Build 오류를 줄인다는 것이 실증됐으므로, 다음 단계로
고려할 수 있는 것은(이번 Task에서 구현하지 않음):

1. §11-1의 "코드 일부 발췌" 조건을 별도로 실험해 최소 충분 Context의
   경계를 더 좁히는 것.
2. 만약 실제로 Context 전달 방식을 바꾸기로 결정한다면, 이는 기존
   `[Relevant Context]` 텍스트 블록(이미 `_enrich_issue`가 하는 일)의
   **내용**을 확장하는 것으로 충분해 보인다는 점(Architecture Drift
   아님) — 단, 이 결정 자체는 RFC/ADC 절차 또는 최소한 별도 Task
   승인을 거쳐야 하며, 이 문서가 그 결정을 내리지 않는다.

---

## 최종 보고

1. **무엇을 검증했는가** — T08과 동일한 Design 산출물을 재사용해,
   Build에 주는 Context를 3가지(A: 기존/경로만, B: 전체 소스 파일,
   C: 선택적 사실 요약)로 바꿔가며 생성된 코드를 **실제 pytest
   실행**으로 비교했다.
2. **어떤 Context가 효과적이었는가** — **전체 소스 파일(B)**이 유일하게
   완전히 효과적이었다(3/3 pass). 선택적 사실(C)은 명시한 정보에서만
   효과가 있었고, 명시하지 않은 내부 자료구조 정보에서는 여전히
   실패했다.
3. **Build 오류가 얼마나 달라졌는가** — A는 Import 단계에서 즉시 실패
   (0/3, 수집 자체 불가), C는 런타임 로직에서 실패(0/3, 다른 지점의
   실패), B는 오류 없음(3/3 pass) — 오류의 **종류**가 아니라 **존재
   여부** 자체가 B에서만 명확히 해소됐다.
4. **비용/부작용은 무엇인가** — B는 프롬프트 크기가 A 대비 약 5.3배
   컸으나, 실행 시간은 오히려 더 짧았고 산출물이 불필요하게 길어지거나
   무관한 내용이 섞이는 징후는 없었다.
5. **최종 판정** — **A. Source Context Need Validated.**
6. **다음 Task** — "코드 일부 발췌"(리터럴 코드, 사실 요약이 아닌)
   조건을 별도로 실험해 최소 충분 Context의 경계를 좁히는 것을
   제안한다(구현 아님, §12).

---

Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: 36 passed(기존 스위트, 회귀 없음 — 비교용 임시 파일 3개는 실험
직후 삭제하고 `git status`로 원상 복구 확인)
E2E: PASS(비교 실험 자체가 실제 Engine 호출 2건 + 기존 T08 결과 재사용
1건으로 완결됨; Pipeline 전체 재실행은 아님 — Build 단일 지점 비교가
목적)
PR: NOT CREATED
Commit: (아래 참조)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: (아래 참조)
Next Implementation Candidate: "코드 일부 발췌"(리터럴 코드 조각) 조건을
별도로 실험해 전체 소스 제공과 선택적 요약 사이의 손익분기점을 좁히는
Research Task(§12, 구현 아님)
