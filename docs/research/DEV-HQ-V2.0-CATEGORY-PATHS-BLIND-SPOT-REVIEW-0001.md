# CATEGORY_PATHS Blind Spot Review

**문서 성격**: 원인 확인 + 최소 수정 여부 판단. Architecture/Contract를
변경하지 않는다. 신규 Component/Interface를 추가하지 않는다.

## 1. T06 Evidence (재인용)

`DEV-HQ-V2.0-01-05-WORKFLOW-DOGFOODING-0001.md` §4가 실제 Issue
실행으로 확인한 사실: Issue가 `docs/architecture/core/`,
`docs/core/execution-layer/`를 명시적으로 예시로 들었음에도, Stage 01
(`collect_relevant_context`)의 `rfc_documents`/`adc_documents`/
`adr_documents`는 두 트리를 전혀 검색하지 못했다 — `directory_structure`
출력도 `docs/architecture/`, `docs/core/`까지만 나열하고 하위를
전개하지 않아 Issue가 지적한 버그를 Stage 01 스스로 재현했다.

## 2. 조사

### 2.1 수정 전 `CATEGORY_PATHS`(전체 8개 카테고리)

```python
CATEGORY_PATHS = {
    "source_code": (ROOT/"hqs"/"development"/"mvp", "*.py", {"tests","__pycache__"}),
    "existing_workflow": (ROOT/"hqs"/"development"/"mvp", "workflow*.py", {"__pycache__"}),
    "mvp_documents": (ROOT/"docs"/"01_mvp", "*.md", set()),
    "obs_documents": (ROOT/"docs"/"governance"/"observations", "OBS-*.md", set()),
    "rfc_documents": (ROOT/"docs"/"decisions"/"rfc", "RFC-*.md", set()),
    "adc_documents": (ROOT/"docs"/"governance"/"adc", "ADC-*.md", set()),
    "adr_documents": (ROOT/"docs"/"decisions"/"adr", "ADR-*.md", set()),
    "rt_documents": (ROOT/"docs"/"governance"/"rt", "RT-*.md", set()),
}
```

8개 카테고리 모두 **디렉토리 1개**만 검색 대상으로 갖는다.
`docs/architecture/core/`(Kernel RFC/ADC/ADR 12+2건), `docs/core/
execution-layer/`(Execution Layer RFC/ADC/ADR 5+2건) — T04
Governance Tree Investigation이 확인한 4개 RFC/ADC/ADR 트리 중
2개 — 는 어느 카테고리에도 등록되어 있지 않았다.

### 2.2 실제 문서 존재 확인

```
$ ls docs/architecture/core/{RFC,ADC,ADR}-*.md | wc -l   # 12 + 12 + 2 = 26
$ ls docs/core/execution-layer/{RFC,ADC,ADR}-*.md | wc -l # 5 + 5 + 2 = 12
```

두 트리 모두 실제로 존재하며 비어 있지 않다(T04에서 이미 개별 파일명
전수 확인, 본 조사에서 존재 자체를 재확인).

### 2.3 `collect_relevant_context()`와의 관계

`collect_relevant_context()`는 `CATEGORY_PATHS.items()`를 그대로
순회해 `_relevant_files()`를 호출할 뿐이다 — 카테고리 목록이 곧
검색 범위이므로, 등록되지 않은 트리는 어떤 Issue에도 절대 노출될 수
없는 구조다(런타임 조건이 아니라 정적 설정 누락).

### 2.4 기존 테스트가 해당 경로를 검증하는가

`hqs/development/mvp/tests/*.py` 전체를 확인한 결과, `CATEGORY_PATHS`
또는 `collect_relevant_context`의 실제 파일 시스템 동작을 검증하는
테스트는 **없다** — `test_workflow_0008.py`, `test_workflow_artifact_
flow.py`, `test_workflow_project_intelligence.py` 전부
`collect_relevant_context`를 `monkeypatch`로 대체해 고정된
`SAMPLE_CONTEXT`만 사용한다(T02에서도 동일하게 확인된 사실). 즉 이번
수정이 기존 테스트를 깨뜨릴 가능성 자체가 구조적으로 없다.

### 2.5 누락이 의도적 설계인가 — 근거 문서 전수 확인

- **`hqs/development/BOUNDARY.md`**: "Development HQ가 절대 책임지지
  않는 것"은 Engine 호출·Task 실행·Policy 판정 등 **실행 메커니즘**을
  말하며, "어떤 문서를 Context로 읽을 수 있는가"는 다루지 않는다 —
  Repository Intelligence가 Kernel/Execution Layer 문서를 읽는 것을
  금지하는 문구가 없다.
- **`CLAUDE.md`**: "Kernel Architecture 연구 → `docs/architecture/
  core/`", "Execution Layer → `docs/core/execution-layer/`"를
  Governance와 나란히 정상적인 Context Loading 대상으로 명시한다 —
  접근 금지 영역으로 표시하지 않았다.
- **`docs/01_mvp/MVP-0005-observation.md`**(원 구현 문서): "Project
  내 8개 카테고리"를 정의할 당시의 예시 실행(Task Dispatcher Issue)이
  찾아낸 문서는 `RFC-0001, RFC-0002, RFC-0004`(Dev HQ 트리)뿐이다 —
  **이 시점에는 `docs/architecture/core/`, `docs/core/execution-
  layer/` Kernel/Execution Layer 트리 자체가 아직 존재하지 않았다**
  (두 트리는 이후 별도 세션에서 Kernel Architecture 연구가 시작되며
  생겼다 — T04가 확인한 RFC-0001~0012/ADC-0001~0012 등). 즉 8개
  카테고리는 "그 시점에 존재하는 문서 전부"를 반영한 설계였고, 이후
  두 트리가 새로 생겼을 때 `CATEGORY_PATHS`를 갱신하는 후속 작업이
  없었을 뿐이다.
- **모순되는 선례**: `adr_documents`가 가리키는 `docs/decisions/adr/`
  자체가 이미 Dev HQ ADR-0001과 **Kernel ADR-0002~0007을 한 디렉터리
  안에 섞어** 담고 있다(T04 §6). Development HQ Project Intelligence가
  "Kernel 문서는 원천적으로 배제해야 한다"는 원칙을 지키고 있었다면
  이 상황 자체가 이미 모순이었을 것이다 — 즉 트리 분리는 "경계
  보호"가 아니라 단순히 "새 트리가 생긴 뒤 갱신을 안 한 것"이다.

**결론**: 의도적 설계라는 근거를 찾지 못했다. 오히려 반대 근거
(CLAUDE.md가 정상 참조 대상으로 명시, docs/decisions/adr가 이미
Kernel 문서를 포함, MVP-0005 시점에 해당 트리가 아예 없었다는 시점
증거)만 확인됐다.

## 3. 판정

### A. 실제 Blind Spot → 최소 수정 필요

근거: (1) T06이 실제 Issue 실행으로 기능적 결손을 직접 관찰, (2) 두
트리 모두 실재하고 비어 있지 않음, (3) 배제를 뒷받침하는 Boundary
문서·Governance 결정이 없음, (4) 시점 증거(MVP-0005 당시 두 트리
부재)가 "설계"가 아니라 "이후 갱신 누락"임을 보여줌, (5) 이미
`docs/decisions/adr/`가 Kernel 문서를 포함하고 있어 "경계 보호"
가설과 모순됨.

## 4. 실제 영향

- 영향 범위: Stage 01(Repository Intelligence)의 `rfc_documents`/
  `adc_documents`/`adr_documents` 3개 카테고리 한정. `source_code`/
  `existing_workflow`/`mvp_documents`/`obs_documents`/`rt_documents`
  5개는 영향 없음(해당 트리에 그런 문서가 없음).
- 영향 규모: 최대 26+12=38개 문서 파일이 어떤 Issue에도 노출될 수
  없었다(RFC 17 + ADC 17 + ADR 4, 정확히는 이미 등록된 것 제외 순증분).
- 실사용 영향: Kernel/Execution Layer 경계를 다루는 실제 Issue(T06의
  Test Task가 정확히 이런 사례)에서 Requirement/Design 단계가 관련
  Governance 결정을 Context로 받지 못해 **부정확하거나 근거가 얕은
  산출물**을 낼 위험이 있다 — T06에서 직접 관찰된 실제 결과다.

## 5. 수정 여부 및 내용

**수정함.** `hqs/development/mvp/project_intelligence.py` 2곳만
변경했다.

1. `_relevant_files()`가 디렉토리 1개(`Path`) 또는 여러 개
   (`tuple[Path, ...]`)를 모두 받도록 확장(`isinstance(directories,
   Path)`로 단일 경로를 1-tuple로 정규화, 그 외 로직은 동일).
2. `CATEGORY_PATHS`의 `rfc_documents`/`adc_documents`/
   `adr_documents` 3개 항목만 디렉토리를 `(기존 Dev HQ 경로,
   docs/architecture/core, docs/core/execution-layer)` 3중 tuple로
   확장. 나머지 5개 카테고리, glob 패턴, exclude_dirs, 반환 dict의
   키 이름·개수는 **변경하지 않았다** — `collect_relevant_context()`/
   `build_context_bundle()`의 반환 Contract(키 목록)는 그대로다.

새 Capability/Component/Interface를 추가하지 않았다 — 기존 함수의
내부 데이터(딕셔너리 값)만 확장했다. Stage Workflow, State/Recovery,
Architecture/Contract 어느 것도 건드리지 않았다.

## 6. 테스트 결과

```
$ pytest hqs/development/mvp/tests/ -q
....................................                                     [100%]
36 passed in 50.69s
```

회귀 없음(기존 36건 전부 `collect_relevant_context`를 monkeypatch로
대체하므로 애초에 이번 변경에 영향받지 않는다 — §2.4).

**수동 기능 확인**(자동 테스트가 원래 없어 T02 선례와 동일하게 수동
확인으로 대체):

```python
issue = {"title": "project_intelligence._directory_structure()의 max_depth=2 제한 완화", ...}  # T06과 동일 Issue
ctx = collect_relevant_context(issue)
# 수정 전: rfc_documents/adc_documents/adr_documents 전부 Dev HQ 트리만 반환
# 수정 후:
#   rfc_documents: RFC-0006(Dev HQ), RFC-0003(Kernel), RFC-0005(Execution Layer)
#   adc_documents: ADC-0002, ADC-0003, ADC-0005 (전부 Kernel)
#   adr_documents: ADR-0006(Dev HQ), ADR-0003(Kernel), ADR-0004(Kernel)
```

T06이 지적한 Blind Spot이 동일 Issue 재실행으로 닫혔음을 확인했다.

## 7. Open Issues

1. `docs/decisions/adr/`가 Dev HQ·Kernel ADR을 한 디렉터리에 섞어
   담는 비대칭(T04 §6, §9)은 이번 수정으로 해소되지 않는다 — 이번
   Task 범위 밖.
2. `_directory_structure()` 자체의 `max_depth=2` 제한(T06 Test Task의
   원래 주제)은 이번 Task에서 다루지 않았다 — T06은 그 문제의
   실행체(생성된 코드에 실제 버그 있음)만 Evidence로 남겼고 적용하지
   않기로 했다(T06 §12); 이번 T07은 `CATEGORY_PATHS`만 다룬다.
3. 이번 확장으로 `docs/architecture/core/`, `docs/core/execution-
   layer/`가 3개 카테고리 모두에서 반복 스캔된다(디렉토리 자체는
   작아 성능 영향 없음을 확인했으나, 파일 수가 크게 늘어날 경우
   재검토 여지가 있다는 점만 기록).

## 8. Next Task

**Case B(국소적 구현 문제)의 연장선**으로, 이번 수정 자체가 T06이
제안한 Next Implementation Candidate를 완결한다. 다음 후보는 T06
§12가 이미 기록한 `_directory_structure()`의 실제 버그(생성된 코드,
아직 미적용) 처리 여부를 판단하는 것 — 단, 이는 별도 Task이며 이번
T07이 임의로 착수하지 않는다.

---

## 최종 보고

1. **무엇을 확인했는가** — `CATEGORY_PATHS` 8개 카테고리 전체,
   `docs/architecture/core/`·`docs/core/execution-layer/`의 실제
   파일 존재, `collect_relevant_context()`와의 결합 방식, 기존
   테스트의 커버리지 여부, 누락이 의도적 설계인지를 BOUNDARY.md·
   CLAUDE.md·MVP-0005-observation.md·T04 조사 결과로 대조했다.
2. **실제 Blind Spot인가** — **그렇다(A)**. 배제를 뒷받침하는
   문서 근거가 없고, MVP-0005 작성 시점에 두 트리가 아직 존재하지
   않았다는 시점 증거로 "설계"가 아니라 "갱신 누락"임을 확인했다.
3. **무엇을 수정했는가** — `_relevant_files()`가 디렉토리 tuple을
   받도록 확장하고, `rfc_documents`/`adc_documents`/`adr_documents`
   3개 카테고리에 Kernel·Execution Layer 트리를 추가했다. 다른 5개
   카테고리와 반환 Contract는 그대로 유지했다.
4. **무엇이 확인됐는가** — pytest 36건 전부 통과(회귀 없음), T06과
   동일한 Issue를 재실행해 이전에 비어 있던 Kernel/Execution Layer
   RFC/ADC/ADR이 실제로 노출됨을 수동으로 확인했다.
5. **무엇이 남았는가** — `docs/decisions/adr/`의 Dev HQ·Kernel 혼재
   비대칭, `_directory_structure()` 자체의 버그 처리 여부는 이번
   범위 밖으로 남겼다.
6. **v2.0에서의 의미** — T06이 실제 실행으로 발견한 구체적 결손을
   Architecture 변경 없이 최소 범위로 닫았다 — Case B(국소적 구현
   문제)가 실제로 "발견 → 최소 수정 → 재검증"까지 완결된 첫 사례다.

---

Architecture Change: NONE
Contract Change: NONE
Production Code Change: YES (`hqs/development/mvp/project_intelligence.py`,
`_relevant_files()` 시그니처 내부 확장 + `CATEGORY_PATHS` 3개 항목만)
Tests: 36 passed
E2E: N/A(이번 Task는 개별 함수 수정 확인이며 5-Stage 전체 재실행은
하지 않았다 — T06이 이미 E2E를 검증했고, 이번 변경은 Stage 01 내부
데이터 확장에 한정된다)
PR: NOT CREATED
Commit: (아래 참조)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: (아래 참조)
Next Implementation Candidate: `_directory_structure()`의 `max_depth=2`
제한 자체 처리 여부 판단(T06 §12, 별도 Task)
