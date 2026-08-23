# Multi-Module AST Dependency Research

**문서 성격**: Research/Dogfooding. Context 시스템/Component/Interface를
구현하지 않는다. Production 코드를 수정하지 않는다. Architecture/
Contract를 변경하지 않는다.

## 1. T11 Evidence (재인용)

`DEV-HQ-V2.0-LITERAL-EXCERPT-AUTO-DETECTION-0001.md`가 확인한 사실:
단일 모듈(`project_intelligence.py`) 안에서는 `ast` 기반 전이적 폐쇄
자동 추출이 사람이 직접 고른 발췌와 동등하거나 더 완비된 결과를 냈다
(3/3 pass, Full Source 대비 52% 크기). T11 §11-1은 "대상이 여러
파일/모듈에 걸쳐 있을 때도 같은 알고리즘이 통하는지"를 Open Issue로
남겼다. T12는 그 질문을 검증한다.

## 2. 실험 Task(T11과 성격이 다른 실제 개발 Task)

`hqs/development/mvp/workflow_0008.py::run_pipeline()`은 5개 sibling
모듈(`agents.py`, `engine.py`, `project_intelligence.py`, `workflow.py`,
`workflow_project_intelligence.py`)에 걸친 파이프라인이다. 기존
`test_workflow_0008.py`(4개 테스트)는 전부 monkeypatch로 Engine 호출
자체를 대체해, 5개 모듈이 실제 Engine과 함께 끝까지 연결되는지 한
번도 검증한 적이 없다 — `test_mvp_0001.py`만이 유일한 real-Engine
테스트다. 이 실제 Gap을 Issue로 사용했다.

```
Issue: workflow_0008.run_pipeline()에 대한 real-Engine E2E 테스트 부재
— test_mvp_0001.py처럼 실제 Engine을 호출하는 최소 1개의 E2E 테스트
함수만 추가해 달라. 정확히 1개 함수, 텍스트 내용이 아니라 dict 키
구성과 비어있지 않음만 assert한다.
```

T09~T11과 달리 **Design도 이번 Task용으로 새로 실행**했다(Stage 01→
02→03, real Engine, 총 69.1초) — T11까지는 Build만 비교하기 위해 T08의
Design을 재사용했으나, 이번 Task는 성격이 달라(monkeypatch 기반 단위
테스트가 아니라 real-Engine 블랙박스 E2E 테스트) 별도 Design이
필요했다. Design은 "키 스키마를 짐작하지 말고 실제 코드를 먼저 읽어
확정하라"고 스스로 명시했다(§7 참조).

## 3. 실험 조건 (A/B/C)

| 조건 | 구성 방법 |
|---|---|
| **A. Manual** | 이 문서 작성자가 "이 Task에 필요하다고 판단한" 1단계 의존성만 직접 발췌: `run_pipeline()` 전체, `_engine_failure_message()` 전체, 기존 테스트 파일의 import 관례. `agents.py`/`engine.py`/`project_intelligence.py`는 "블랙박스로 호출만 하면 되니 불필요하다"고 판단해 **의도적으로 제외** |
| **B. Automatic** | T11의 단일 모듈 AST 폐쇄 알고리즘을 **모듈 경계를 넘어 재귀하도록 확장**(아래 §4) — `run_pipeline`에서 시작해 5개 sibling 모듈 전체를 자동으로 추적 |
| **C. Full Source** | 관련 6개 파일(5개 production 모듈 + 기존 테스트 파일) 전문 |

## 4. 다중 모듈 자동 추출 알고리즘(코드 분석, LLM 미사용)

T11의 단일 모듈 알고리즘을 다음과 같이 확장했다(연구용 스크립트,
저장소에 커밋하지 않음 — 로직만 기록).

1. 대상 `(모듈, 함수)` 쌍을 시작점으로 둔다: `(workflow_0008, run_pipeline)`.
2. 각 모듈을 처음 방문할 때만 `ast.parse()`하고 결과를 캐시한다.
3. 각 모듈의 `from .X import Y` 형태(상대 import, `level == 1`)를
   `로컬 이름 → (대상 모듈, 원래 이름)` 매핑으로 미리 인덱싱한다.
4. 대상 함수의 Load-context `Name` 참조를 수집해, 그 이름이 **같은
   모듈의 최상위 정의**인지, **다른 모듈에서 import된 것**인지
   구분한다. 후자면 그 이름이 정의된 실제 모듈로 전이(frontier에
   `(대상 모듈, 원래 이름)` 추가)한다.
5. 고정점까지 반복 — 새 모듈로 넘어갈 때마다 그 모듈도 같은 방식으로
   파싱·캐시하고, 계속 재귀한다.
6. 각 모듈에서 실제로 쓰인 절대 import(`level == 0`, 예: `re`,
   `subprocess`)만 선별한다. 모듈 간 상대 import(`from .agents import
   ...`)는 "경계 정보"로만 쓰고 발췌 텍스트에는 넣지 않는다(발췌
   자체가 이미 여러 모듈의 코드를 한 텍스트에 이어붙이므로).
7. 모듈별로 원본 정의 순서를 유지해 발췌를 조립한다.

## 5. Manual vs Automatic — 실제로 무엇을 판별했는가

| 모듈 | Manual 포함 | Automatic 포함 |
|---|---|---|
| `workflow_0008`(`run_pipeline`) | 포함 | 포함(대상) |
| `workflow`(`_engine_failure_message`) | 포함 | 포함 |
| `workflow_project_intelligence`(`_enrich_issue`, `_summarize_context`) | **누락** | 포함 |
| `project_intelligence`(`collect_relevant_context` + 전이적 의존 12개) | **누락**(의도적 판단) | 포함 |
| `agents`(5개 Capability 함수 + `NO_ISSUES_MARKER`/`_strip_code_fence`) | **누락**(의도적 판단) | 포함 |
| `engine`(`call_engine` + `ENGINE_CLI`/`DISALLOWED_TOOLS`/`STATELESS_CALL_NOTICE`/`ENGINE_TIMEOUT_SECONDS`) | **누락**(의도적 판단) | 포함 |

Manual의 누락은 이번에는 **실수가 아니라 의도적 판단**이었다 — "블랙
박스로 함수 하나만 호출하면 되니 내부 구현은 몰라도 된다"는
가정이었다. 이 가정은 **assert 로직 자체에는** 맞았지만(§6 확인),
**환경 실행 조건(스킵 가드) 판단에는 틀렸다** — `engine.py`를 보지
않았기 때문에 Engine이 실제로 어떻게 호출되는지(API 키가 아니라
`claude` CLI subprocess) 알 수 없었다.

## 6. Build/Test 결과 — 실제로 실행

동일 절차(생성 코드를 기존 `test_workflow_0008.py`에 병합 →
`pytest`로 직접 실행 → 결과 기록 → 즉시 삭제 → `git status`로 원상
복구 확인)를 따랐다. A/B는 "기존 파일에 함수 1개 추가"라는 Design
지시를 따라 함수 본문만 반환했으므로, 기존 파일에 필요한 import(A:
`os`+`pytest`, B: `shutil`+`pytest`)를 사람이 병합하는 통상적인 PR
통합 단계를 거쳤다(이 병합 자체는 기계적 삽입이며 Build의 정확성
판정에 포함하지 않는다).

| 조건 | pytest 결과 | 원인/비고 |
|---|---|---|
| **A** | **SKIPPED**(1 skipped) | 가드 조건이 `os.environ.get("ANTHROPIC_API_KEY")`인데, 이 환경은 그 환경변수를 쓰지 않고 이미 인증된 `claude` CLI로 Engine을 호출한다(`engine.py` 실측: `ENGINE_CLI = "claude"`, `subprocess.run(["claude", "-p", ...])`) — 실제로는 Engine이 사용 가능한데도 "사용 불가"로 잘못 판정해 건너뛰었다 |
| (A, 가드 우회 후 assert 로직만 별도 실행) | **PASS** | 가드 조건만 틀렸을 뿐, assert 로직 자체는 정확했다(§7 재현 절차) — Manual의 "블랙박스로 충분하다"는 판단은 assert 설계에는 맞았다 |
| **B** | **1 passed**(109.19초) | Engine 실행까지 포함해 완전히 정상 동작 |
| **C** | **1 passed**(305.69초) | 정상 동작했으나, **기존 4개 테스트 전부를 다시 작성해 파일 전체를 재생성**했다 — Design이 지시한 "정확히 1개 함수만 추가"라는 스코프를 벗어난 부작용(§8) |

## 7. 재현 절차(투명성을 위해 기록)

```
$ cp <A 산출물, 기존 파일 import 병합 후> hqs/development/mvp/tests/_t12_condition_a.py
$ pytest hqs/development/mvp/tests/_t12_condition_a.py -k test_run_pipeline_real_engine_e2e -q -rs
1 skipped — requires ANTHROPIC_API_KEY for real Engine calls

$ cp <B 산출물, 병합 후> hqs/development/mvp/tests/_t12_condition_b.py
$ pytest hqs/development/mvp/tests/_t12_condition_b.py -k test_run_pipeline_real_engine_e2e -q
1 passed in 109.19s

$ cp <C 산출물, 자체 완결 파일> hqs/development/mvp/tests/_t12_condition_c.py
$ pytest hqs/development/mvp/tests/_t12_condition_c.py -k test_run_pipeline_real_engine_e2e -q
1 passed in 305.69s

# A의 가드 조건만 틀렸는지, assert 로직 자체가 틀렸는지 분리 확인
$ python3 -c "... (A의 assert 블록만 발췌해 가드 없이 직접 실행) ..."
A logic (guard bypassed): PASS

$ rm hqs/development/mvp/tests/_t12_condition_{a,b,c}.py
$ git status --porcelain   # 출력 없음
$ python3 -m pytest hqs/development/mvp/tests/ -q   # 기존 36건 재확인
36 passed in 52.45s
```

## 8. 누락/과잉 포함

- **Automatic의 과잉 포함**: 없다고 판정한다 — `engine.py`(및 그
  상수)는 Manual이 "불필요"로 판단했지만, 실제로는 **정확한 스킵
  가드를 위해 필요했다**(§6). `agents.py`의 5개 함수도 `run_pipeline`
  이 직접 호출하는 진짜 의존성이다. Automatic이 포함한 6개 모듈 전부
  대상 함수의 실제(직접 또는 전이적) 의존성이었다.
- **Full Source의 과잉 포함(부작용)**: 있다 — 기존 테스트 파일
  **전체 내용**을 프롬프트에 넣었더니, Build가 "기존 4개 테스트 +
  신규 1개"를 전부 다시 작성해 반환했다. 내용 자체는 정확했지만
  (기존 4개 테스트 로직이 그대로 재현됨), Design이 명시한 "정확히
  1개 함수만 추가"라는 스코프를 벗어났다 — **Full Source가 오히려
  스코프 오염을 유발**한 사례다.

## 9. Context 크기·실행 비용

| 조건 | Prompt 크기(문자) | Build 시간 | 실행(pytest) 시간 |
|---|---|---|---|
| A | 4,316 | 21.0초 | (가드 오류로 스킵, 로직만 별도 확인) |
| **B** | **14,564**(C 대비 55%) | 20.1초 | **109.19초** |
| C | 26,580 | 41.1초 | 305.69초(가장 오래 걸림 — 아래 참고) |

**참고**: C의 실행 시간이 B보다 3배 가까이 긴 것은, C가 생성한
E2E 테스트가 `workflow_0008.REAL_ISSUE`(길고 상세한 실제 Issue 텍스트)
를 썼고 B/A가 만든 짧은 `SAMPLE_ISSUE`보다 Engine 응답이 길어졌을
가능성이 있다 — 조건 자체(Full Source 여부)가 아니라 각 조건이 고른
입력 데이터 차이일 수 있다(표본 1회, 원인 미분리 — Open Issue).

## 10. 최종 판정

### A. Multi-Module Automatic Excerpt Validated

근거:
1. Automatic(B)이 Full Source(C)와 동일하게 실제로 통과했다(1 passed,
   real Engine 포함) — 크기는 C의 55%.
2. Automatic은 모듈 경계를 넘나드는 진짜 의존성(5개 모듈)을 빠짐없이
   추적했고, **과잉 포함이 없었다**(§8) — 오히려 Full Source 쪽에서
   스코프 오염(전체 파일 재작성)이라는 부작용이 나타났다.
3. Manual(A)은 "블랙박스로 충분하다"는 사람의 판단이 assert 로직에는
   맞았지만, `engine.py`를 보지 못해 **환경 실행 조건(스킵 가드)을
   실제와 다르게 추정**했다 — 다중 모듈 상황에서는 "직접 호출되는
   함수만 알면 된다"는 사람의 직관이 놓치는 지점(간접적으로만
   관련된 모듈의 실행 방식)이 있음을 보여준다.

**한정 조건**: 이번 실험은 5개 모듈, 비교적 얕은 호출 그래프(대부분
1~2단계 깊이) 안에서 검증됐다. 순환 참조, 조건부 import, 동적 임포트
(`importlib`) 등이 있는 코드베이스에서도 같은 알고리즘이 안전한지는
확인하지 못했다.

## 11. Open Issues

1. C의 실행 시간이 유독 길었던 원인(Full Source 자체의 특성인지, 그
   조건이 우연히 고른 입력 데이터의 차이인지)을 분리하지 못했다.
2. Automatic이 대형 프로젝트(수십~수백 개 모듈)에서도 폐쇄 계산이
   합리적인 시간 내에 끝나는지(알고리즘 자체는 각 모듈을 최대 1회만
   파싱하므로 이론상 선형이지만, 실측하지 않았다) 확인하지 않았다.
3. Full Source의 "스코프 오염"(기존 파일 전체 재작성) 현상이 이번
   1회 관찰인지, Full Source 조건에서 반복되는 패턴인지 추가 실험이
   필요하다 — Design의 "정확히 1개 함수만 추가하라"는 제약이 있을 때
   Full Source가 구조적으로 더 위험한 선택일 수 있다는 가설만
   기록한다.
4. 순환 참조·동적 import가 있는 모듈에서 이 알고리즘이 무한 루프나
   누락 없이 동작하는지 검증하지 않았다.

## 12. Next Task (구현 아님 — Evidence 기반 제안)

T09~T12 종합: Source Context는 Build 오류를 줄이고(T09), 전체 파일이
아니라 신중히 고른 발췌로도 충분하며(T10), 그 발췌를 AST 정적 분석
으로 자동화해도 단일 모듈(T11)과 다중 모듈(T12) 모두에서 최소
동등하거나 더 신뢰할 수 있는 결과를 얻는다는 것이 실증됐다. 다음으로
고려할 수 있는 것(구현 아님):

1. §11-3의 가설(Full Source가 "함수 1개만 추가" 같은 좁은 스코프
   Task에서 오히려 스코프 오염을 유발하기 쉬운지)을 별도로 검증.
2. 순환 참조·동적 import가 있는 실제 모듈에 대해 같은 알고리즘의
   안전성을 검증.
3. 만약 실제로 Pipeline에 반영하기로 결정한다면 RFC/ADC 등 별도
   절차가 선행되어야 한다 — 이 문서는 그 결정을 내리지 않는다.

---

## 최종 보고

1. **무엇을 실험했는가** — T11의 단일 모듈 AST 폐쇄 알고리즘을 5개
   sibling 모듈에 걸친 실제 Task(`workflow_0008.run_pipeline()`
   real-Engine E2E 테스트 추가)로 확장해, Manual/Automatic/Full
   Source 3개 조건의 Build 결과를 real Engine로 실행·검증했다.
2. **무엇을 자동 판별했는가** — 대상 함수에서 시작해 상대 import를
   따라 모듈 경계를 넘나드는 전이적 의존성 전체(6개 모듈: 대상
   모듈 포함 `workflow_0008`/`agents`/`engine`/`project_intelligence`/
   `workflow`/`workflow_project_intelligence`)를 기계적으로 추적했다.
3. **무엇을 놓쳤는가** — Automatic 자체는 놓치지 않았다. **Manual(사람의
   의도적 판단)이** `engine.py`를 제외해, 실제 Engine 호출 방식(API
   키가 아니라 `claude` CLI)을 몰라 잘못된 스킵 가드를 생성했다 —
   assert 로직 자체는 맞았지만 실행 조건 판단이 틀렸다.
4. **Manual 대비 결과** — Automatic은 real Engine 포함 실제 실행에서
   통과했고(109.19초), Manual은 잘못된 가드로 스킵됐다(가드를
   우회하면 로직 자체는 통과). Full Source도 통과했으나 스코프를
   벗어나 파일 전체를 재작성하는 부작용을 보였다.
5. **최종 판정** — **A. Multi-Module Automatic Excerpt Validated**
   (5개 모듈, 얕은 호출 그래프라는 한정 조건 포함).
6. **다음 Task** — Full Source의 스코프 오염 가설을 별도로 검증하고,
   순환 참조/동적 import가 있는 코드에서도 같은 알고리즘이 안전한지
   확인하는 Research Task를 제안한다(구현 아님).

---

Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: 36 passed(기존 스위트, 비교용 임시 파일 3개는 실험 직후 삭제
하고 `git status`로 원상 복구 확인)
E2E: PASS(비교 실험 목적 — real Engine 신규 호출 다수: Design 1회 +
Build 3조건 + 검증 실행 3회 + 가드 우회 재확인 1회, 전부 완결)
PR: NOT CREATED
Commit: (아래 참조)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: (아래 참조)
Next Implementation Candidate: Full Source의 "스코프 오염"(좁은 범위
Task에서 파일 전체 재작성 유발) 가설을 별도로 검증하는 Research
Task(§12, 구현 아님)
