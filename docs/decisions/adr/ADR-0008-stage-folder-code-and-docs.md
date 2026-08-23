# ADR-0008: Stage 폴더의 문서+실행 코드 공존 허용 (ADR-0001 §2/§6 Supersede)

| 필드 | 내용 |
|---|---|
| ID | ADR-0008 |
| 제목 | Stage 폴더가 Stage 전용 문서와 실행 코드를 함께 관리하도록 허용 |
| 상태 | Accepted |
| Context | Architecture Owner가 세션 중 명시적으로 결정(아래 "결정 경위" 참고) |
| 관련 ADC | 없음 — 이 ADR은 RFC → ADC → ADR 표준 경로가 아니라 Architecture
Owner의 직접 지시로 작성됐다(예외 경위는 아래 참고). ADC-0003 판단 2
(Capability Catalog 확장, Defer)에 대해서는 §4에서 범위를 한정해
언급한다. |

## 결정 경위

DEV-HQ-V2.0 세션 중 "Stage 01 Context Analysis"를 `stage_01.py`
실행 코드로 구현해 달라는 요청이 있었다. 이는 ADR-0001 §2("stages/는
문서 전용, 코드 없음")·§6(Migration Strategy)과 직접 충돌해, 이
세션은 구현 전 `AskUserQuestion`으로 충돌을 보고했다. Architecture
Owner는 직접 다음을 결정했다: ADR-0001 §2/§6을 이 ADR로 Supersede하고,
ADR-0001의 나머지 결정(§1 STRUCTURE.md 문구, §3 Domain Model, §4 Stage
정의, §5 기존 MVP 코드 비이동)은 그대로 유지한다. **ADR-0001 문서
자체는 삭제하거나 직접 수정하지 않는다** — 이 ADR이 별도로 그 일부를
Supersede한다.

## Out of Scope (이 ADR이 다루지 않는 것)

- ADR-0001 §1(STRUCTURE.md Stage 문구), §3(Domain Model), §4(Stage
  정의 6개), §5(기존 MVP 코드 비이동) — 그대로 유지, 재논의 없음.
- Stage 02~06의 실제 구현 — 이 ADR은 구조 규칙만 정하며, 각 Stage
  구현은 별도 세션/Task다.
- `workflow.py`(01~05 통합 Workflow) — Stage 01~05가 각각 완성된
  후에만 작성한다(§5).
- Jarvis OS Layer(Concept Model, Meta Architecture, System Boundary),
  Model Routing/Engine Adapter/Multi Model — 변경하지 않는다(ADR-0001과
  동일하게 범위 밖).

## Decision

### 1. Stage 폴더 구조 — 문서 + 실행 코드 공존

ADR-0001 §2("stages/는 문서 전용, 코드 없음")를 Supersede한다. 각
Stage 폴더는 해당 Stage의 문서와 실행 파일을 함께 관리한다.

```
hqs/development/
├── stages/
│   ├── 01_context_analysis/
│   │   ├── README.md
│   │   ├── RESPONSIBILITY.md
│   │   ├── CAPABILITIES.md
│   │   ├── CONTEXT.md
│   │   ├── VALIDATION.md
│   │   └── stage_01.py
│   ├── 02_.../ ~ 05_.../   (각 Stage 구현 시점에 동일 패턴으로 생성)
│   └── 06_devops_release/README.md   (아직 문서 전용 유지 — 구현 범위 밖)
├── mvp/                     (기존 그대로, 이동 없음 — ADR-0001 §5 유지)
└── ...
```

- `01_repository_intelligence/`는 `01_context_analysis/`로 이름을
  바꾼다 — Responsibility가 "프로젝트를 이해한다"(Repository
  Intelligence, ADR-0001 §4)에서 "후속 Stage가 쓸 수 있는 Context를
  생성한다"(Context Analysis)로 넓어졌기 때문이다(§2 참고). ADR-0001
  §4가 정의한 6개 Stage의 목적·순서 자체는 바뀌지 않는다 — 이름과
  Responsibility 서술만 갱신한다.
- `capabilities/`, `tests/`는 Stage 하위가 아닌 기존 공통 구조를
  그대로 유지한다. 이 ADR 시점에는 별도 `capabilities/` 디렉토리를
  신설하지 않는다 — Stage 01은 기존 `mvp/project_intelligence.py`,
  `mvp/ast_context.py`의 함수를 그대로 재사용하며, 새 Capability가
  실제로 필요해질 때만(§4) 신설한다.

### 2. Stage 01 Responsibility 갱신

ADR-0001 §4의 Stage 01("Repository Intelligence", "프로젝트를
이해한다")을 다음으로 대체한다:

| Stage | 목적 |
|---|---|
| 01. Context Analysis | Repository, 문서, 코드 구조, AST, Dependency를 분석해 후속 Stage가 사용할 수 있는 Context를 생성한다 |

Stage 02~06의 이름·목적(ADR-0001 §4 표의 나머지 5행)은 변경하지
않는다.

### 3. Stage 01 Capability 5종

RFC-0007/ADC-0005 Evidence로 이미 검증된 5개를 Stage 01의
Capability로 귀속한다(전부 기존 `mvp/` 함수 재사용, 신규 구현 없음):

| Capability | 재사용 함수 | Evidence |
|---|---|---|
| Repository Structure Analysis | `project_intelligence._directory_structure()` | MVP-0005 이래 운용 |
| Relevant File / Document Discovery | `project_intelligence.collect_relevant_context()` | MVP-0005~0007, T07 |
| Project Context Analysis | `project_intelligence.build_context_bundle()` | MVP-0005~0006 |
| AST Function Candidate Index | `ast_context.build_function_candidate_index()` | T17~T19, ADC-0005 판단 1 |
| AST Dependency Closure | `ast_context.build_dependency_closure()` | T09~T19, ADC-0005 판단 2 |

이 5개는 이미 RFC-0007 → ADC-0005 경로로 승인된 것(AST 2종)이거나
기존 MVP 범위에서 이미 운용 중인 것(나머지 3종)이며, 이 ADR이 새로
결정하는 것은 이들의 **Stage 01 소속**뿐이다 — 함수 자체를 재구현하지
않는다.

### 4. 신규 Capability 추가 기준 (ADC-0003 판단 2 범위 한정 수정)

ADC-0003 판단 2(Capability Catalog 확장, Defer)는 "신규 Capability
후보가 어떤 MVP에서도 실행·관찰된 적이 없다"는 근거로 유보됐다.
Architecture Owner는 Stage 구현이라는 새로운 맥락에서 이 유보를
다음과 같이 한정 수정한다: **Stage 01~05 구현 과정에서 실제 필요성이
관찰로 확인된 경우에만, 그 Stage 구현 Task 안에서 신규 Capability를
추가할 수 있다.** ADC-0003 판단 2의 원 취지("Observation 없이 목록을
확장하지 않는다")는 그대로 유지된다 — 달라지는 것은 "RFC 재개를
기다리지 않고 Stage 구현 시점에 바로 추가할 수 있다"는 절차뿐이다.
Stage 01은 §3의 5개 모두 기존 함수 재사용으로 충족되므로, 이 ADR
시점에 신규 Capability를 추가하지 않는다.

### 5. Migration Strategy (ADR-0001 §6 Supersede)

1. `stages/01_repository_intelligence/` → `stages/01_context_analysis/`
   이름 변경, 기존 README 내용을 5개 문서(README/RESPONSIBILITY/
   CAPABILITIES/CONTEXT/VALIDATION)로 재구성.
2. `stage_01.py` 추가 — §3의 5개 Capability 함수를 호출만 하는 얇은
   진입점. `mvp/` 코드는 이동·수정하지 않는다(ADR-0001 §5 유지).
3. Stage 01 검증(기존 pytest 회귀 + 신규 Stage 01 테스트) 통과 후에만
   완료로 간주한다.
4. Stage 02~05는 각각 별도 세션/Task에서 동일 패턴(문서 5종 + 실행
   파일 1개)으로 진행한다 — 이 ADR이 미리 만들지 않는다.
5. `workflow.py`(01~05 통합)는 Stage 01~05가 각각 완성된 뒤 별도로
   작성한다 — 이 ADR의 범위가 아니다.

## Consequences

- `hqs/development/stages/01_context_analysis/`에 실행 코드
  (`stage_01.py`)가 생긴다 — ADR-0001 §2의 "코드 없음" 전제가 이
  ADR 이후로는 Stage 01에 대해 더 이상 성립하지 않는다. ADR-0001
  문서 자체는 수정하지 않으므로, 두 문서를 함께 읽는 사람은 이
  ADR-0008이 §2/§6을 Supersede했음을 알아야 한다(`docs/decisions/
  adr/README.md`에 명시).
- Stage 02~06에도 동일 패턴이 적용될 것을 전제하지만, 이 ADR은 Stage
  01만 실제로 승인한다 — Stage 02~05 구현 시점에 이 ADR을 그대로
  참조하되, 다시 별도 승인을 받을 필요는 없다(패턴 자체가 이미
  Accepted).
- 신규 Capability 추가 문턱이 낮아졌다(§4) — 남용 방지를 위해, 추가할
  때마다 그 Task의 최종 보고에 "왜 기존 5종 재사용으로 부족했는지"를
  Evidence로 기록해야 한다(이 ADR이 강제).
- Jarvis OS Architecture Baseline, Development HQ Baseline 문서는
  변경되지 않는다 — 이 ADR은 `hqs/development/STRUCTURE.md`의 Stage
  참조 문구 1곳만 갱신한다(ADR-0001이 이미 그 문구를 추가했으므로,
  이 ADR은 참조 대상만 ADR-0001+ADR-0008 둘로 갱신한다).
