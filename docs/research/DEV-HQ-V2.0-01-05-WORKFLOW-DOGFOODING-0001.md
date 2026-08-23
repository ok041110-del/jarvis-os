# Development HQ v2.0 — 01→05 Full Workflow Dogfooding

**문서 성격**: Dogfooding Evidence 기록. Architecture/Contract를 변경하지
않는다. 새 Component/Interface를 추가하지 않는다. 발견된 Gap은 구현하지
않고 Evidence와 Next Task로만 기록한다.

## 1. 목적

T01~T05가 완료한 Audit/Alignment/Governance 정리 이후, 실제 개발 Task
1건을 01(Repository Intelligence) → 02(Planning) → 03(Design) →
04(Implementation) → 05(Validation) 전체 Workflow로 real Engine 호출을
통해 끝까지 실행해, 01→05가 실제로 관통하는지 증명한다.

## 2. Test Task (실제 Issue)

`hqs/development/mvp/project_intelligence.py::_directory_structure()`가
`max_depth=2`로 고정되어 있어 `docs/architecture/core/`,
`docs/core/execution-layer/`처럼 깊이 3에 개별 RFC/ADC/ADR 파일이
있는 문서 트리는 파일명이 디렉토리 구조 목록에 노출되지 않는다(예:
`docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md`는 depth
3이라 목록에서 빠진다). 이 Issue는 **T04 Governance Tree Investigation
작업 중 실제로 관찰된 사실**이며 가공하지 않았다 — CONSTITUTION.md의
Dogfooding Policy("실제 Issue를 이용하여 검증한다")와 MVP-0008 선례
(Project Intelligence 자기 개선을 실제 Issue로 사용)를 그대로 따른다.

```python
ISSUE = {
    "title": "project_intelligence._directory_structure()의 max_depth=2 제한 완화",
    "description": (
        "hqs/development/mvp/project_intelligence.py의 _directory_structure()는 "
        "max_depth=2로 고정되어 있어 docs/architecture/core/, docs/core/execution-layer/ "
        "처럼 깊이 2를 넘는 문서 트리 안의 개별 RFC/ADC/ADR 파일 이름이 디렉토리 구조 목록에 "
        "노출되지 않는다. ... 기존 함수 시그니처(max_depth: int = 2)는 유지하고, "
        "새 매개변수나 설정 파일은 추가하지 않는 것을 선호한다."
    ),
    "status": "Open",
}
```

## 3. 실행 방식

기존 `workflow_0008.py::run_pipeline()`이 내부적으로 호출하는 것과
동일한 5개 함수(`collect_relevant_context`,
`requirements_agent_requirement_analysis`, `design_agent_design`,
`backend_agent_code_generation`, `backend_agent_code_review`,
`qa_agent_test_execution`)를 **Mock 없이, 실제 `call_engine()`
subprocess(→ 실제 `claude` CLI) 호출로** 순서대로 실행했다. 각 Stage의
Input/Output/소요시간을 개별적으로 기록해, 기존 pipeline 코드보다
세밀한 관찰 단위를 확보했다. 총 소요 시간 약 222초(6회 호출 중
Repository Intelligence 1회는 Engine 호출 없음).

## 4. Stage 01 — Repository Intelligence (Define)

**Input**: 위 Issue dict.
**실행**: `collect_relevant_context(issue)` — Engine 호출 없음(순수
키워드 매칭), 0.4초.
**Output**(8개 카테고리 중 발췌):

```
directory_structure: docs/00_governance/, docs/01_mvp/, docs/architecture/,
                      docs/core/, docs/decisions/, docs/governance/, docs/research/
source_code:         project_intelligence.py, workflow_artifact_flow.py, agents.py
existing_workflow:   workflow_artifact_flow.py, workflow.py, workflow_project_intelligence.py
mvp_documents:       MVP-0044, MVP-0004-plan, MVP-0047
obs_documents:       OBS-0002, OBS-0001, OBS-0005
rfc_documents:       RFC-0006(구조/Taxonomy), RFC-0005(Execution Boundary), RFC-0003(SDLC Pivot)
adc_documents:       ADC-0003, ADC-0004, ADC-0001 (모두 docs/governance/adc/)
adr_documents:       ADR-0002, ADR-0003, ADR-0005 (모두 docs/decisions/adr/)
rt_documents:        RT-0001
```

**Evidence(자기 실증)**: `directory_structure`가 `docs/architecture/`,
`docs/core/`까지만 나열하고 그 하위(`architecture/core/`,
`core/execution-layer/`)를 전개하지 않는다 — **Issue가 지적한 버그를
Stage 01의 실제 출력 자체가 그대로 재현했다.**

**Gap(관찰, 구현하지 않음)**: `rfc_documents`/`adc_documents`/
`adr_documents`는 `CATEGORY_PATHS`(T02에서 경로만 수정) 구조상
Development HQ 트리(`docs/decisions/rfc`, `docs/decisions/adr`)와
`docs/governance/adc`만 검색한다. `docs/architecture/core/`,
`docs/core/execution-layer/`(T04가 확인한 Kernel/Execution Layer
트리)는 이 세 카테고리 어디에서도 검색 대상이 아니다 — Issue가 그
트리의 파일을 예시로 들었음에도, Stage 01은 구조적으로 그 트리를
한 번도 들여다보지 않는다.

## 5. Stage 02 — Planning & Specification (Plan)

**Input**: Stage 01의 `context`를 Issue description에 `[Relevant
Context]` 블록으로 덧붙인 enriched issue(`_enrich_issue`).
**실행**: `requirements_agent_requirement_analysis()`, real Engine,
22.3초.
**Output**: Goal / Scope(In/Out) / Risks 5개 항목을 갖춘 완결된
Requirement Analysis. 특히 Risk 1("하드코딩된 경로 결합 — RFC-0006이
Taxonomy가 진화 중임을 시사하므로 유지보수 부채")은 Stage 01이 전달한
Context(RFC-0006 인용)를 실제로 활용해 도출됐다.

**Handover 평가**: Stage 01 → 02 전달은 **정상**. Context가 Requirement
의 Risk 도출에 실제로 반영됨을 확인했다(정보가 그냥 버려지지 않음).

## 6. Stage 03 — Architecture & Design (Design)

**Input**: 원본 Issue + Stage 02의 Requirement.
**실행**: `design_agent_design()`, real Engine, 23.5초.
**Output**: `_effective_max_depth(rel_path, max_depth)` 헬퍼 + 경로
컴포넌트 기반 allowlist 방식을 제안. Risk를 4개로 구체화(Taxonomy
결합, 출력 크기, 소비자 가정, 테스트 필요성) — 특히 "실제 파일 깊이를
확인한 뒤 +1 여부를 확정하라"는 검증 지시를 명시적으로 남겼다.

## 7. Stage 04 — Implementation (Build)

**Input**: Stage 03의 Design 전체 텍스트.
**실행**: `backend_agent_code_generation()`, real Engine, 8.5초.
**Output**: `_DEEP_ALLOWLIST` 튜플 2개 + `_effective_max_depth()` +
수정된 `_directory_structure()` 전체 함수.

**Handover 문제(발견)**: Design이 §Risk에서 명시적으로 요구한 "실제
파일 깊이를 먼저 확인하라"는 지시가 Build 단계 산출물에 반영된
흔적이 없다 — Build는 Design의 결론(+1, 경로 컴포넌트 비교)만 그대로
코드화했고, Design이 스스로 남긴 "확인 후 확정" 유보 조건은 이행되지
않았다. **Design의 텍스트 전체가 다음 Engine 호출의 프롬프트로
그대로 전달됨에도, 산출물 전체가 실제로 소비되는 것은 아니다** — 이는
Stage 간 전달이 "텍스트 재사용"이지 "이행 확인"이 아님을 보여준다.

## 8. Stage 05 — Validation (Prove)

### 05a. Review

**Input**: Stage 04의 코드.
**실행**: `backend_agent_code_review()`, real Engine, **124.1초**(6개
Stage 중 가장 오래 걸림).
**Output**: **실제 결함 발견** — `_effective_max_depth`의 allowlist
확장이 함수 자신의 기본값(`max_depth=2`)에서는 **절대 발동하지
않는 죽은 코드**라는 지적. 재귀가 `docs/architecture/core`(3-세그먼트)
에 도달하기 전에 `docs/architecture`(2-세그먼트) 단계에서 이미
`depth(3) > effective_max_depth(2)`로 걸려 반환되므로, "core" 자체가
한 번도 `lines`에 추가되지 않는다.

**독립 검증(이 문서 작성자가 직접 코드를 추적)**: 위 지적을 코드를
직접 손으로 추적해 재확인했다 — **사실이다.** `walk(root, "", 1)` →
`walk(docs, "docs", 2)` → `walk(architecture, "docs/architecture", 3)`
단계에서 `_effective_max_depth("docs/architecture", 2)`는
`("docs","architecture")`(2-tuple)가 `("docs","architecture","core")`
(3-tuple)와 같을 수 없어 `2`를 반환하고, `depth(3) > 2`가 참이 되어
`core`의 `iterdir()` 자체가 실행되지 않는다. **Grade A급 Evidence**:
LLM 산출물을 맹신하지 않고 직접 코드 추적으로 검증했다.

### 05b. Test Execution(제안)

**Input**: Stage 04의 코드 + 05a의 Review.
**실행**: `qa_agent_test_execution()`, real Engine, 43.3초.
**Output**: 20개 테스트 케이스 제안 — `_effective_max_depth` 단위
테스트 9개(경계 케이스 포함) + `_directory_structure` 통합 테스트
11개. 10번 케이스는 "현재는 실패하고, 버그가 수정되면 통과해야
한다"는 형태로 Review의 발견을 정확히 반영했다.

**중요 재확인(기존 Gap의 재관찰)**: 이번에도 `test_execution`은 코드를
**실행하지 않았다** — 제안된 20개 테스트 중 어느 것도 실제로 파일을
만들어 pytest로 돌려보지 않았다. T01/T02가 이미 기록한 이름-행동
불일치가 실제 Dogfooding에서 다시 한번 확인됐다 — 이번엔 **제안의
품질 자체는 매우 높았다**(구체적 실패 재현 케이스 포함)는 점에서
"기능이 나쁘다"가 아니라 "이름이 하는 일을 정확히 반영하지 않는다"는
점이 재확인됐다.

## 9. 관찰 요약 (T06이 요구한 8개 항목)

| 항목 | 관찰 |
|---|---|
| 정보 손실/중복 | **손실**: Design의 "확인 후 확정" 유보 조건이 Build에서 이행 안 됨(§7). **중복 아님**: Stage 01 Context는 실제로 Requirement에 반영됨(§5) |
| Handover 문제 | Design→Build 간 "제안 이행 여부 확인" 메커니즘 없음(§7). 그 외 4개 Handover는 정상 |
| Task Decomposition Need | **관찰되지 않음** — Task가 작아 5-Capability 선형 호출로 충분했다. 분해 필요성의 Evidence 없음 |
| Validation Gap | **재확인**: `test_execution`은 제안만 하고 실행하지 않는다(§8b). 신규 발견 아님, 실제 Task로 재관찰됨 |
| Context/State 부족 | 전체 실행이 단일 Python 스크립트의 지역 변수로만 연결됐다 — 중간 상태 저장 없음. 이번 실행에서 실패가 없어 부족이 문제가 되지는 않았다 |
| Recovery/Retry Need | **이번 실행에서는 관찰되지 않음** — 6회 Engine 호출 전부 성공(실패 유도 실험은 이번 범위 밖) |
| Engine Boundary 문제 | **없음** — `call_engine()` 6회 모두 동일한 단일 함수로 성공했다 |
| Architecture Gap | **없음** — 발견된 문제(§7, §8b)는 모두 Stage-local 구현 수준이며 Architecture 변경을 요구하는 Evidence가 아니다 |

## 10. Gap (구현하지 않음 — Evidence만)

1. **Stage 01 Category Blind Spot**: `CATEGORY_PATHS`가
   `docs/architecture/core/`, `docs/core/execution-layer/`를 전혀
   검색하지 않는다(§4). T04가 문서 수준에서 확인한 4-트리 병존을
   Repository Intelligence 코드가 실제로 놓치는 구체적 사례.
2. **Design→Build 이행 확인 부재**: Design이 남긴 유보 조건이 Build
   단계에서 검증되지 않고 그대로 넘어간다(§7). Task Dispatcher나
   State Machine을 새로 만들 근거는 아니다 — 1회 관찰이며 반복 여부
   미확인.
3. **`_directory_structure()`의 실제 로직 결함**(§8a): Development
   HQ Platform 코드가 아니라 **이번 실행이 만들어낸 산출물**의
   결함이다 — 실제 저장소 코드(`project_intelligence.py`)는 이 결함
   있는 코드로 아직 교체되지 않았다(§12 참조, 이번 Task는 적용하지
   않음).

## 11. Open Issues

1. Design→Build 정보 손실(§7)이 이번 1회 관찰만으로 반복 패턴인지,
   우연인지 판단할 근거가 부족하다 — 추가 Dogfooding 라운드 필요.
2. Recovery/Retry, State 부족은 이번 실행에서 실패가 없어 실제로
   시험되지 않았다 — 의도적 실패 유도 실험은 별도 Task로 남긴다.
3. `_directory_structure()`의 실제 수정(§8a에서 발견된 결함 수정)은
   이번 Task의 산출물이 아니라 **다음 Task의 재료**로만 남긴다.

## 12. Next Task (Evidence 기반)

**Case 판단**: 01→05가 실제 Issue를 처음부터 끝까지 real Engine으로
관통했고(§2~§8), Engine Boundary 문제나 Architecture급 결함은
발견되지 않았다(§9). 발견된 문제(Stage 01 Category Blind Spot,
Design→Build 이행 확인 부재, 생성 코드의 실제 버그)는 전부
**Stage-local 구현 수준**이다 → **Case B(국소적 구현 문제)**로
판정한다. Case C/D로 격상할 근거(반복 관찰, 기존 Architecture로 해결
불가 증거)는 이번 1회 실행만으로는 없다.

**Next Implementation Candidate**: `hqs/development/mvp/
project_intelligence.py::CATEGORY_PATHS`에 Kernel/Execution Layer
트리(`docs/architecture/core/`, `docs/core/execution-layer/`)를
포함할지 검토하는 최소 Task. 근거: 이번 실행이 실제 Issue로 그 Blind
Spot을 직접 재현했고(§4 Evidence), 수정 범위가 딕셔너리 항목 추가
수준으로 작아 국소적 구현 수정(Case B)에 부합한다. 단, Capability
Catalog 확장이 아니라 기존 Capability(`repository_analysis`류) 내부
로직 개선이므로 ADC-0003 판단 2(Defer)와 충돌하지 않는지 먼저 확인이
필요하다.

---

## 최종 보고

1. **무엇을 실행했는가** — 실제 Issue 1건("`_directory_structure()`
   max_depth 제한 완화")을 `collect_relevant_context` →
   `requirements_agent_requirement_analysis` → `design_agent_design`
   → `backend_agent_code_generation` → `backend_agent_code_review` →
   `qa_agent_test_execution` 순서로, 전부 real Engine(`claude` CLI
   subprocess) 호출로 실행했다(총 약 222초).
2. **무엇이 정상 작동했는가** — 01→05 전체가 중단 없이 관통했다.
   Stage 01→02 Handover(Context가 Requirement Risk에 실제 반영),
   Engine 호출 6회 전부 성공, Review가 실제 코드 결함을 정확히
   짚었고 그 결함을 이 문서 작성자가 직접 코드 추적으로 재검증했다.
3. **무엇이 문제였는가** — (a) Stage 01이 Issue가 예시로 든 두
   문서 트리를 애초에 검색 대상에 넣지 않는다는 구조적 Blind Spot,
   (b) Design의 유보 조건이 Build에서 이행 확인 없이 스킵된 것,
   (c) `test_execution`이 이번에도 테스트를 실행하지 않고 제안만
   했다(기존 Gap 재확인).
4. **무엇이 새롭게 확인됐는가** — Stage 01의 실제 출력이 Issue가
   지적한 버그를 그대로 재현하는 자기 실증적 Evidence를 얻었고,
   Design→Build 사이에 "제안 이행"을 강제하는 장치가 없다는
   구체적 사례를 처음으로 관찰했다.
5. **다음 Task** — Case B로 판정, `CATEGORY_PATHS`에 Kernel/Execution
   Layer 트리를 포함할지 검토하는 국소적 Task를 Next Implementation
   Candidate로 제안한다(§12).

---

Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO (Stage 04가 생성한 코드는 이 문서에 Evidence로만
기록했고 `project_intelligence.py`에 적용하지 않았다 — Gap은 구현하지
않고 기록만 한다는 지시에 따름)
Tests: 36 passed(코드 미변경 확인 목적, `pytest hqs/development/mvp/tests/`)
E2E: **PASS** — 01→05 전 Stage가 real Engine으로 끝까지 관통, 실패 없음
PR: NOT CREATED
Commit: (아래 참조)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: (아래 참조)
Next Implementation Candidate: `project_intelligence.py::CATEGORY_PATHS`에
`docs/architecture/core/`, `docs/core/execution-layer/`를 포함할지 검토
(§12, Case B — 국소적 구현 문제)
