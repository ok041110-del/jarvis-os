# Development HQ v2.0 — 01→05 Full Workflow Dogfooding (2회차)

**문서 성격**: Dogfooding Evidence 기록. Architecture/Contract를 변경하지
않는다. 새 Component/Interface를 추가하지 않는다. 발견된 Gap은 구현하지
않고 Evidence와 Next Task로만 기록한다.

## 1. 목적

T06(1회차 Dogfooding)이 검증한 01→05 E2E가 **다른 실제 Task에서도
반복 가능한지** 확인한다. 특히 T06이 발견한 Design→Build 정보 손실이
다시 나타나는지를 핵심적으로 관찰한다. T06과 달리 단순 버그 수정이
아니라 **테스트 커버리지 보강(품질 개선) Task**를 선정했다.

## 2. Test Task (실제 Issue)

`hqs/development/mvp/project_intelligence.py::collect_relevant_context()`
/`CATEGORY_PATHS`는 실제 파일 시스템을 스캔하는 핵심 로직인데,
`hqs/development/mvp/tests/`의 모든 테스트가 이 함수를 monkeypatch로
대체해 실제 스캔 동작 자체를 한 번도 자동 검증한 적이 없다(**T02·T07이
이미 반복 확인한 실제 사실** — 가공하지 않은 진짜 Gap을 Issue로 사용).

```python
ISSUE = {
    "title": "collect_relevant_context()/CATEGORY_PATHS에 대한 자동화 회귀 테스트 부재",
    "description": (
        "... 실제 임시 디렉토리(tmp_path 등)를 이용해 _relevant_files()와 "
        "collect_relevant_context()의 핵심 동작(키워드 매칭, 여러 디렉토리 검색, "
        "존재하지 않는 디렉토리 처리)을 검증하는 최소한의 자동화 테스트를 새로 "
        "추가해 달라. 기존 collect_relevant_context()나 CATEGORY_PATHS 자체의 "
        "시그니처/동작은 바꾸지 않는다."
    ),
    "status": "Open",
}
```

## 3. 실행 방식

T06과 동일하게 6개 함수(`collect_relevant_context`,
`requirements_agent_requirement_analysis`, `design_agent_design`,
`backend_agent_code_generation`, `backend_agent_code_review`,
`qa_agent_test_execution`)를 Mock 없이 실제 `call_engine()`(→ 실제
`claude` CLI subprocess) 호출로 순서대로 실행했다. 총 소요 205.6초.

## 4. Stage 01 — Repository Intelligence (Define)

**실행**: 1.0초(Engine 호출 없음).
**Output**(발췌): `rfc_documents`: `docs/architecture/core/RFC-0003...`,
`RFC-0004...`, `docs/decisions/rfc/RFC-0005...`; `adc_documents`:
전부 `docs/architecture/core/ADC-000{3,5,7}...`.

**T07 Fix 회귀 검증**: T07에서 고친 `CATEGORY_PATHS`(Kernel/Execution
Layer 트리 포함)가 **전혀 다른 새 Issue에서도 정상 동작**했다 — Kernel
트리 RFC/ADC/ADR이 실제로 반환됨을 재확인(회귀 없음).

**T06과 동일하게 유지되는 결함**: `directory_structure`는 이번에도
`docs/architecture/`, `docs/core/`까지만 나열한다 — T07은 `rfc_
documents`/`adc_documents`/`adr_documents` 3개 카테고리만 고쳤고
`_directory_structure()` 자체(T06이 발견한 원 버그, 아직 미적용)는
건드리지 않았으므로 이 결과는 **예상된 그대로**다.

## 5. Stage 02 — Planning & Specification (Plan)

**실행**: 58.6초(T06의 22.3초보다 훨씬 김 — 아래 §9 비교 참조).
**Output**: Goal/Scope(In/Out)/Risks 절 구성은 T06과 동일한 품질.
특히 "핵심 모순 지점"이라는 절을 스스로 만들어, Issue 설명이 요구한
"과거 실제 발생한 경로 오류 재현"과 "tmp_path 기반 화이트박스
테스트"가 **서로 다른 종류의 테스트**임을 정확히 짚어내고, 사용자
확인이 필요하다고 명시했다(사람이 확인 없이 다음 Stage로 넘어가는
현재 Pipeline 구조와 대비되는 지점 — §8 참조).

## 6. Stage 03 — Architecture & Design (Design)

**실행**: 33.6초.
**Output**: "로직은 진짜, 데이터는 가짜"라는 명확한 원칙 아래 3개
테스트(키워드 매칭/다중 디렉토리/존재하지 않는 디렉토리)를 설계했다.
"monkeypatch 지점은 함수 시그니처를 먼저 읽어 정확히 잡아야 한다",
"구현에 들어가기 전에 실제 코드(`_relevant_files`/
`collect_relevant_context`/`CATEGORY_PATHS`/conftest.py)를 읽고
확정하는 단계를 먼저 거치는 것을 권장합니다"라고 **스스로 명시적으로
요구**했다.

## 7. Stage 04 — Implementation (Build)

**실행**: 31.9초.
**Output**: 3개 테스트 함수를 생성했으나 다음 두 가지 **명백한 오류**를
포함한다.

1. `from myproject import project_intelligence` /
   `from myproject.project_intelligence import collect_relevant_context`
   — 실제 패키지 이름은 `myproject`가 아니라 `mvp`다(독립 검증:
   `hqs/development/mvp/tests/test_workflow_project_intelligence.py:13`
   `from mvp import workflow_project_intelligence as wpi`). 이 코드를
   그대로 저장하면 `ModuleNotFoundError: No module named 'myproject'`로
   즉시 실패한다.
2. `collect_relevant_context("database schema")` — 문자열 하나를
   query로 받는 함수로 가정했으나, 실제 시그니처는
   `collect_relevant_context(issue: dict) -> dict`다(독립 검증:
   `project_intelligence.py:126`). 반환값도 파일 경로 `list`가 아니라
   8개 카테고리 키를 가진 `dict`다.

**Design→Build 정보 손실(T06과 동일 패턴의 재발, 더 심각한 형태)**:
Design이 스스로 "실제 코드를 먼저 읽어야 한다"고 명시했음에도, Build는
그 확인 없이 곧바로 **완전히 가상의 모듈 이름과 시그니처**로 코드를
작성했다. T06에서는 생성된 코드가 실제 파일과 같은 이름 공간에서
동작은 했으나 내부 로직에 버그가 있었던 반면, 이번에는 **생성된
코드가 실제 저장소와 아예 연결될 수 없는 수준**이다 — 정보 손실의
심각도가 T06보다 크다.

**근본 원인(구조적으로 확인)**: `agents.py`의 파이프라인 어디에서도
Planning/Design/Build Capability에 **실제 소스 파일의 내용**이 전달된
적이 없다 — Stage 01이 넘기는 것은 파일 **경로 목록**(문자열)뿐이고,
`design_agent_design(issue, requirement)`는 원본 Issue와 Requirement
텍스트만 받으며, `backend_agent_code_generation(design)`은 Design
텍스트만 받는다(모두 `agents.py` 실측). 게다가 `call_engine()`
(`engine.py`)은 `DISALLOWED_TOOLS = "Write,Edit,Bash,Read,Glob,Grep,
..."`로 **Engine 자체의 모든 파일시스템 도구를 차단**한다 — 이는
MVP-0001부터 유지된 명시적 설계("stateless text-in/text-out")이며,
이번에 처음 발견된 사고가 아니라 **Capability Loop의 근본 계약** 자체가
실제 코드 내용을 어떤 Stage에도 노출하지 않는다는 사실을 이번 실행이
구체적으로 드러낸 것이다.

## 8. Stage 05 — Validation (Prove)

### 05a. Review

**실행**: 63.2초.
**Output**: `myproject` 패키지 존재 자체를 "unverified assumption"으로
정확히 플래그했다(Review 지시문의 "관련 import를 검증되지 않은
가정으로 지목하라"는 원칙이 여기서도 작동). 단, **"이 이름이 틀렸다"고
확정하지는 못했다** — Review 역시 Build와 동일하게 실제 저장소를 볼
수 없기 때문이다(같은 `DISALLOWED_TOOLS` 제약). 추가로 `CATEGORY_PATHS`
바인딩 방식(모듈 전역 vs. 기본 인자 캡처), 중복 항목 검증 누락(`set`
비교의 함정)도 정확히 짚었다 — **Review 자체의 품질은 매우 높다.**

### 05b. Test Execution(제안)

**실행**: 17.3초.
**Output**: 14개 추가 테스트 케이스 제안. Review가 지적한 리스크(바인딩
방식, 중복 방지, 대소문자 구분, 부분 문자열 매칭 등)를 정확히 계승해
구체적 테스트로 변환했다 — T06과 동일하게 Review→Test Execution
Handover는 **매번 정상 작동**했다.

**재확인된 기존 Gap**: 이번에도 `test_execution`은 제안만 하고 실행하지
않았다 — T06과 동일.

## 9. T06/T07과의 비교

| 항목 | T06 | T08(본 문서) |
|---|---|---|
| Task 유형 | 기존 함수의 동작 제한 완화(버그성) | 테스트 커버리지 신규 추가(품질 개선) |
| 총 소요 시간 | 222초 | 206초(비슷한 규모) |
| Stage 02 소요 | 22.3초 | 58.6초(Issue의 모순 지점을 스스로 발견하느라 더 김 — Requirement 품질과 시간이 비례하는 것으로 보임, 반복 관찰 필요) |
| Stage 01→05 관통 | PASS | PASS |
| Design→Build 정보 손실 | 있음(Design의 유보 조건이 Build에서 확인 없이 스킵) | **다시 발생, 더 심각**(모듈 이름·함수 시그니처 자체를 가상으로 생성) |
| Review 품질 | 실제 논리 버그 정확히 검출 | 검증 불가능한 가정을 정확히 플래그(단, 확정은 못함 — 구조적 한계) |
| Test Execution | 제안만, 실행 안 함 | 제안만, 실행 안 함(동일) |
| Engine 호출 실패 | 0/6 | 0/6(이번에도 전부 성공) |
| 신규 발견 | — | **Build/Review 모두 실제 소스 파일 내용에 접근할 수 없다는 구조적 원인**(`DISALLOWED_TOOLS`) 확인 |

**핵심 결론**: Design→Build 정보 손실은 **1회성이 아니라 반복되는
패턴**이며, 그 근본 원인(Capability가 실제 소스 코드 내용을 한 번도
전달받지 않음, Engine의 파일시스템 도구 완전 차단)까지 이번에
구조적으로 확인했다. 이는 국소적 코드 버그가 아니라 **Context 전달
설계(무엇을 Context로 넘기는가)에 관한 반복 관찰**이다.

## 10. 발견된 Gap (구현하지 않음 — Evidence만)

1. **(재확인, 심화) Design→Build 정보 손실**: Design의 명시적 확인
   요구가 Build에서 무시됨(§7). T06보다 심각한 형태로 재발.
2. **(신규) 소스 코드 내용 미전달**: Planning/Design/Build 어느
   Capability도 실제 소스 파일의 내용을 Context로 받지 않는다 —
   파일 경로 목록만 받는다(§7 근본 원인 분석).
3. **(신규 관찰) Requirement의 자기 모순 발견 능력**: Stage 02가
   Issue 설명 안의 두 요구사항(재현 테스트 vs. 화이트박스 테스트)이
   실제로 다른 종류임을 스스로 발견하고 "확인 필요"를 명시했다 —
   그러나 Pipeline에는 이 확인을 사람에게 되묻는 경로가 없어, 다음
   Stage(Design)가 그 모순을 자체적으로 다시 절충해야 했다. 이는
   Handover 지점에 확인/승인 단계가 없다는 사실을 보여준다.
4. **(재확인) Validation Gap**: `test_execution`이 실행하지 않고
   제안만 함 — T01, T06에 이어 3번째 독립 관찰.

## 11. Open Issues

1. Stage 02 소요 시간이 T06(22.3초) 대비 T08(58.6초)로 크게 늘어난
   원인이 Task 복잡도 차이인지, 우연한 변동인지는 2회 관찰만으로
   확정할 수 없다.
2. "소스 코드 내용 미전달"이 Design→Build 정보 손실의 **유일한**
   원인인지, 아니면 다른 요인(프롬프트 길이, Engine의 코드 생성
   경향 등)도 함께 작용하는지는 이번 2회 관찰로 완전히 분리하지
   못했다.
3. Requirement 단계의 자기 모순 발견을 사람에게 되묻는 경로가
   필요한지(Handover에 확인 단계 추가)는 Architecture Decision
   영역일 수 있어 이번 Task 범위에서 판단하지 않는다.

## 12. Case 판정

**Case C(반복되는 구조적 Gap)** — T06과 동일/유사한 문제(Design→Build
정보 손실)가 2회 연속 관찰되었고, 그 근본 원인(Engine의 파일시스템
도구 완전 차단, 소스 코드 내용 미전달)이 우연이 아니라 Capability
Loop의 설계 자체(`DISALLOWED_TOOLS`, `agents.py`의 함수 시그니처)에
있음을 확인했다. 다만 이 Gap은 **Architecture/Contract 변경 없이도**
검토 가능하다 — Case C는 "Workflow 개선 Need를 검토"하라고만 요구하며
즉시 구현을 요구하지 않는다. Case D(Boundary 자체의 충돌)로 격상할
근거(Stage 간 책임 소재 자체가 모순된다는 Evidence)는 없다 — 오히려
Engine의 무도구 원칙은 MVP-0001부터 의도적으로 유지된 설계이며, 이번
관찰은 그 설계가 낳는 **알려진 결과**를 실증했을 뿐이다.

## 13. Next Task

**Next Implementation Candidate(Evidence 기반, 구현 아님 — 검토
Task)**: Planning/Design/Build Capability에 전달되는 Context에
**관련 소스 파일의 실제 내용**(현재는 경로 목록뿐)을 추가하는 것이
Design→Build 정보 손실을 줄이는지 검토하는 별도 Research Task를
제안한다. 이는:
- 새 Component/Interface가 아니라 기존 `[Relevant Context]` 텍스트
  블록의 내용을 확장하는 것(이미 `_enrich_issue`가 하는 일의 연장)
  이므로 Architecture Drift가 아니다.
- 다만 프롬프트 길이 증가(Stage 01이 이미 여러 카테고리에서 파일을
  찾으므로 전체 내용을 넣으면 Token 비용이 커질 수 있음)와 Engine의
  코드 생성 방식(전체 파일을 읽고 patch를 내는 방식으로 바뀌어야
  하는지) 등 검토할 점이 있어 **즉시 구현하지 않고 별도 Task로
  분리**한다.

---

## 최종 보고

1. **무엇을 실행했는가** — T06과 다른 실제 Task("`collect_relevant_
   context()`/`CATEGORY_PATHS`에 대한 자동화 회귀 테스트 추가")를
   01→05 전 Stage, 전부 real Engine 호출로 실행했다(약 206초).
2. **무엇이 정상 작동했는가** — 01→05가 다시 한번 끝까지 관통했다.
   T07의 CATEGORY_PATHS 수정이 새 Issue에서도 회귀 없이 동작함을
   재확인했고, Review→Test Execution Handover는 이번에도 정상이었다.
3. **무엇이 문제였는가** — Stage 04가 실제 저장소와 무관한 모듈 이름
   (`myproject`)과 함수 시그니처(문자열 query)로 코드를 생성했다 —
   독립 검증 결과 이 코드는 실행 시 즉시 `ModuleNotFoundError`로
   실패한다.
4. **T06/T07과 무엇이 달랐는가** — T06의 Design→Build 정보 손실이
   더 심각한 형태(모듈/시그니처 자체가 허구)로 재발했고, 그 근본
   원인이 Engine의 파일시스템 도구 완전 차단(`DISALLOWED_TOOLS`)과
   소스 코드 내용 미전달에 있음을 처음으로 구조적으로 확인했다.
5. **무엇이 새롭게 확인됐는가** — Design→Build 정보 손실이 1회성이
   아니라 반복 패턴이라는 것, 그리고 Requirement 단계가 Issue의
   자기모순을 스스로 발견하고도 이를 사람에게 되묻는 경로가
   Pipeline에 없다는 것.
6. **다음 Task** — Case C 판정. Architecture 변경 없이, 소스 파일
   실제 내용을 Context에 포함하는 것이 도움이 되는지 검토하는 별도
   Research Task를 다음 후보로 제안한다(구현은 하지 않음).

---

Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO (Stage 04가 생성한 코드는 검증 결과 실행
불가능한 상태였으며, Evidence로만 기록하고 저장소에 적용하지 않았다)
Tests: 36 passed(코드 미변경 확인 목적)
E2E: **PASS**(01→05 전 Stage가 실패 없이 관통했다는 의미의 PASS이며,
Stage 04 산출물의 품질 문제와는 별개 — Pipeline 자체는 끝까지 실행됨)
PR: NOT CREATED
Commit: (아래 참조)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: (아래 참조)
Next Implementation Candidate: Planning/Design/Build Capability에 실제
소스 파일 내용을 Context로 포함하는 것이 Design→Build 정보 손실을
줄이는지 검토하는 Research Task(§13, Case C — 검토만, 구현 아님)
