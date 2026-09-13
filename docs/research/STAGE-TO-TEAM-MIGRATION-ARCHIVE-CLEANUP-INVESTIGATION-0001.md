# Stage → Team Migration — Archive/Obsolete File Cleanup Investigation

## Summary

- 조사만 수행했다. **파일을 하나도 삭제하지 않았다.** Production
  코드/Governance 문서/Architecture 문서 무수정.
- `hqs/development/`, `projects/`, `docs/`, `.claude/`, repo 루트 전체를
  대상으로 archived/deprecated/obsolete/superseded/legacy/old/MVP/
  prototype 패턴을 검색하고, 각 후보의 실제 참조 관계를 전수 확인했다.
- **핵심 결론**: 이번 조사에서 "지금 바로 삭제해도 안전한 파일"은
  **0건**이다. 겉보기에 Stage/MVP/prototype 이름을 가진 파일들은
  전부 다음 중 하나였다: (a) 여전히 Production runtime에서 실제로
  import되는 코드, (b) 자체 characterization test로 보존되는 동시에
  Accepted ADC(`ADC-0001`/`ADC-0014`/`ADC-0016`)가 **실제 Decision
  근거로 인용**하는 Historical Evidence, (c) 아직 열려 있는 Governance
  Decision(`ADC-0040`)의 지정된 Evidence 수집 도구, (d) 다른 실험
  프로젝트가 `sys.path`/`importlib`로 실제로 import하는 재사용
  대상이라 지우면 즉시 깨지는 코드.
- 루트의 `archive/v1/`(146개 파일, git-tracked)은 **이미 프로젝트
  자신이 "archive"로 명명해 분리해 둔 상태**이며, 현재 `BASELINE.md`가
  여러 곳에서 직접 인용하는 활성 Historical Evidence다 — 이번 조사가
  다루는 "정리 대상"이 아니라 이미 올바르게 보관된 참고 자료다.
- `docs/decisions/{rfc,adc,adr}/`는 `docs/architecture/core/`의
  하위 호환/구버전이 **아니라**, "Structure v1.0 Migration"(현재
  `hqs/` 구조 자체를 만든 결정)을 기록한 **별개의, 여전히 유효한
  Governance 트랙**이다 — 삭제/이동 대상이 아니다.
- `projects/` 45개 디렉터리 중 **DELETE 후보 0건** — 27개는 1회성
  Dogfooding/Evidence로 이미 완결됐지만 `docs/research/`가 여전히
  인용 중이고, 5개는 다른 실험 프로젝트가 실제로 import해서 재사용
  중이다.

---

## 1. ARCHIVED FILE DISCOVERY(패턴 검색 결과)

패턴(archived/archive/deprecated/obsolete/superseded/legacy/old/
stage_01~05/MVP/prototype)으로 검색한 결과, 이름만으로 삭제를
판단하지 않고 아래 §2~§5에서 전부 실제 참조 관계를 확인했다. 발견된
주요 후보군:

- `hqs/development/mvp/workflow_0002.py`, `workflow_0008.py`,
  `workflow_0009.py`, `workflow_hello_sdlc.py`,
  `workflow_project_intelligence.py`, `workflow_artifact_flow.py`
  (MVP-0002~0009 프로토타입 계열)
- `hqs/development/mvp/workflow.py::run_mvp_0001` + `hqs/development/mvp/cli.py`
  (MVP-0001 구 진입점)
- `hqs/development/stages/04_implementation/architecture_validation/`
  (Ponytail 실험 harness, 9개 파일)
- `hqs/development/stages/06_devops_release/`(README만 존재)
- 루트 `archive/v1/`(146개 파일, 이미 명명된 archive)
- `docs/decisions/{rfc,adc,adr}/`(구버전으로 보이는 별도 번호 체계)
- `projects/` 내 27개 "1회성 Dogfooding/Evidence" 프로젝트(주식/ETF/
  배당주 분석, 각종 PoC)

## 2. ACTIVE REFERENCE CHECK + 3. STAGE→TEAM MIGRATION CHECK(통합 결과)

### `hqs/development/` 판정표(A/B/C/D/E 분류 — 사용자 지시 §3 그대로 사용)

| File/Directory | 분류 | 근거 |
|---|---|---|
| `mvp/workflow_ast_context.py` | **A**(현재 Team runtime에서 사용) | `stages/04_implementation/stage_04.py:12`가 `_EXPOSURE_POLICY_INSTRUCTION`/`identify_target`를 직접 import해 Production Stage 04 조립 로직에 사용 — "workflow_XXXX 프로토타입"이라는 이름과 달리 실제 살아있는 의존성 |
| `mvp/workflow_0002.py` | **C**(Historical Evidence) | `test_workflow_0002.py`로 보존 + `agents/backend.py` 주석이 `NO_ISSUES_MARKER` 용도를 이 파일 기준으로 설명 |
| `mvp/workflow_0008.py` | **C** | `test_workflow_0008.py`로 보존, `workflow_0009.py`가 이 파일의 `REAL_ISSUE`를 재사용(형제 파일 간 참조) |
| `mvp/workflow_0009.py` | **C** | `test_workflow_0009.py`로 보존, `ADC-0016` §Q1이 "MVP-0009가 보여주는 것"을 **실제 Decision 근거**로 직접 인용 |
| `mvp/workflow_hello_sdlc.py` | **C** | `test_workflow_hello_sdlc.py`로 보존 |
| `mvp/workflow_project_intelligence.py` | **C** | `test_workflow_project_intelligence.py` + `test_ast_context.py`(AST 유틸리티 테스트의 실제 예제 대상)로 보존, 형제 프로토타입들의 허브 |
| `mvp/workflow_artifact_flow.py` | **C** | `test_workflow_artifact_flow.py`로 보존 |
| `mvp/workflow.py::run_mvp_0001` | **C** | `test_mvp_0001.py` + `mvp/cli.py`(독립 실행 스크립트)로 여전히 살아있음, `HANDOVER.md`가 "MVP-0001 완료(원 구현)"로 명시적 기록 |
| `mvp/cli.py` | **C** | `hqs/development/cli.py`(현재 진입점)와 자기 docstring으로 명시적으로 구분된 별개의 구 진입점, 폐기 선언 없음 |
| `stages/04_implementation/architecture_validation/`(9개 파일) | **C**(단, 폐기 불가 — ADC-0040이 명시적으로 "재사용 대상"으로 지정) | `RFC-0037`/`ADC-0040`이 직접 governing, `ADC-0040` Decision: "NOT DETERMINED — Real Engine Evidence Required", "새 Harness를 다시 만들 필요 없음"으로 이 harness 자체를 향후 재사용 대상으로 지정 |
| `stages/06_devops_release/README.md` | **B**(현재 Architecture에서 사용 — 의도된 placeholder) | 코드 자체가 없으므로 "폐기"가 아니라 "아직 구현 안 된 미래 Stage"(`ADC-0003` 판단 2가 의도적으로 유보) |
| `stages/0N_*/stage_0N.py`(01~05) | **A** | `teams/*/team.py`가 importlib로 로드 + `test_stage_0N.py`가 직접 테스트, `HANDOVER.md` §11이 "제거하지 않음"을 명시 |

**어느 것도 D(Superseded implementation, 대체됨)나 E(Obsolete,
삭제 가능)로 분류되지 않았다.**

### 루트 `archive/v1/` — 별도 확인(사용자 지시 대상 목록에는 없었으나
"archive"라는 이름으로 직접 매칭되어 확인 필요)

- 146개 파일, 전부 git-tracked.
- `docs/architecture/core/ADR-0006-structure-v1-migration.md`가
  "Migration 범위에서 `archive/` 전체를 제외한다"고 명시 — 즉 이
  디렉터리는 Migration 대상이 아니라 **이미 격리·보존된 이전 Architecture
  버전**이다.
- `docs/architecture/baseline/BASELINE.md`가 3곳 이상에서 "v1
  `archive/v1` `ADR-0007`"류로 **현재도 직접 인용**한다.
- **판정: KEEP(Historical Evidence, 이미 올바르게 보관됨).** 이번
  조사가 "정리해야 할 방치된 잔재"로 다룰 대상이 아니다.

### `docs/decisions/{rfc,adc,adr}/` — 별도 확인(오래된 번호 체계로
오인하기 쉬움)

- `docs/decisions/adr/ADR-0006`이 실제로 `development-hq/` →
  `hqs/development/` 재배치(현재 구조 자체)를 결정한 문서다 —
  `docs/architecture/core/`(별도로 RFC-0001부터 다시 시작하는 Kernel
  Architecture 연구 트랙)와는 **다른 트랙**이지 그 구버전이 아니다.
- 여전히 `docs/architecture/baseline/BASELINE.md`,
  `docs/architecture/core/RFC-0029`/`RFC-0030` 등 현재 활성 문서들이
  이 트랙을 인용한다.
- **판정: KEEP(별개의, 여전히 유효한 Governance 기록).** 삭제/이동
  대상 아님.

### `core/`(repo 루트, `hqs/`와 별개) — 범위 확인

- `hqs/development/`가 이 디렉터리를 전혀 import하지 않음(0건, 직접
  grep 확인) — 이는 `ADR-0006` 자신이 이미 "MVP-0006 Dogfooding처럼
  `run_pipeline()`을 아예 참조하지 않는 경로도 있음"이라고 예견한
  낮은 결합도 그대로다.
- 별도의 Kernel/Execution Layer Governance 트랙(`ADR-0002-execution-layer-module-baseline.md`
  등)이 관리하는 영역 — **Stage→Team Migration과 무관**, 이번 조사의
  대상이 아니다.

### `.claude/` — 전수 확인

- skills 7개 + docs/integrations 15개 파일 전부 확인 — Stage/Team/MVP
  관련 문자열 **0건**. 이번 Migration과 무관한 영역이며 archived/
  deprecated 패턴도 발견되지 않았다.

## 4. MVP / PROTOTYPE CHECK(종합)

| 확인 항목 | 결과 |
|---|---|
| 현재 Production에 흡수됐는가 | 일부(`workflow_ast_context.py`)는 실제로 흡수돼 활성 상태. 나머지는 흡수되지 않고 별개 역사적 스냅샷으로 남음 |
| 새로운 Team implementation으로 대체됐는가 | 아니오 — Team은 이 MVP 프로토타입들을 대체한 것이 아니라, 이들이 진화해 만들어진 현재 Stage 01~05를 감싼 것이다(대체 관계가 아니라 계보 관계) |
| 별도 Evidence가 존재하는가 | 그렇다 — 각 파일 자체가 Evidence다(`docs/01_mvp/MVP-0001~0052`), 그리고 `ADC-0001`/`ADC-0014`/`ADC-0016`이 이들을 실제로 인용 |
| Governance에서 역사적 근거로 사용되는가 | **그렇다, 적극적으로** — "MVP-0009가 보여주는 것을 핵심 근거로 사용"(`ADC-0016` Self Review)처럼 결정문 본문에 직접 인용됨 |
| active import가 존재하는가 | `workflow_ast_context.py`만 Production 활성 import, 나머지는 자체 테스트 + 형제 파일 상호 참조만 |

**결론(사용자 지시 §4 마지막 조건 대조)**: "대체되었고 active
reference가 없으면 DELETE CANDIDATE"라는 조건에서, 이 파일들은
"active reference가 없다"는 절반만 맞고 "대체됐다"는 틀렸다 —
Team으로 대체된 것이 아니라 Governance Decision의 근거 자료로
계속 살아있다. **DELETE CANDIDATE 아님.**

## 5. DUPLICATE / SUPERSEDED CHECK

| 항목 | 판정 | 근거 |
|---|---|---|
| old Agent(구 `agents.py` 단일 모듈) | 확인 결과 이미 부재 — `mvp/agents/{requirements,design,backend,qa}.py`로 리팩터링 완료된 상태만 존재, 구버전 흔적 파일 없음 | N/A(이미 정리됨, 추가 조치 불필요) |
| old Stage implementation | 없음 — `stages/0N_*/stage_0N.py`가 유일한 구현이며 여전히 Production | KEEP |
| prototype(`workflow_XXXX.py` 계열) | §2/§4 참조 | KEEP(Historical Evidence) |
| runner(`mvp/parallel_runner.py`) | 구버전 없음, 현재도 Team01이 실제 사용 중인 유일한 병렬 실행 인프라 | KEEP |
| duplicate adapter(Engine 모듈) | `chatgpt_engine.py`/`engine.py`/`omniroute_engine.py`/`openrouter_engine.py` 4개 — 중복이 아니라 각자 다른 목적(2-Engine 구조 + 미사용 독립 실험 모듈 + 3번째 Engine). `omniroute_engine.py`는 어떤 호출부도 참조하지 않지만 `ADC-0031`/`ADR-0017`이 governing하는 별도 트랙(Thin Engine Caller 실험) — Stage→Team Migration과 무관 | KEEP(각각 별도 근거) |
| obsolete tests | 발견되지 않음 — 모든 `test_workflow_XXXX.py`가 대응하는 살아있는 소스 파일을 가짐 | KEEP |
| obsolete fixtures | 발견되지 않음 | KEEP |

## 6. GOVERNANCE / EVIDENCE 보호 확인

RFC/ADC/ADR/Baseline/Validation Evidence/Architecture Evidence/
Governance Review/historical experiment 결과 — 이번 조사 대상 중
이 범주에 속하는 문서는 전부 **읽기만 했고 수정하지 않았다.** 문서
내부에서 obsolete implementation(예: MVP-0002~0009)을 참조하는 것을
이유로 그 문서(ADC-0001/0014/0016 등) 자체를 삭제 후보로 고려하지
않았다 — 오히려 이 참조 관계가 그 obsolete-처럼-보이는 구현 파일을
"삭제하면 안 되는 이유"가 됐다.

## 7. DELETE CANDIDATE MATRIX

| File/Directory | Current Role | Active Reference | Historical Value | Replacement | Verdict |
|---|---|---|---|---|---|
| `mvp/workflow_ast_context.py` | Stage04 조립 로직에 실제 사용되는 유틸리티 | Production import(`stage_04.py`) | — | 없음(대체 안 됨, 현재도 사용) | **KEEP** |
| `mvp/workflow_0002/0008/0009/hello_sdlc/project_intelligence/artifact_flow.py`(6개) | MVP 프로토타입 계보 | 자체 테스트만 | 높음(`ADC-0001`/`0014`/`0016`이 Decision 근거로 인용) | 없음 | **KEEP** |
| `mvp/workflow.py::run_mvp_0001` + `mvp/cli.py` | MVP-0001 원 구현·구 진입점 | 자체 테스트 + 독립 실행 스크립트 | 높음(HANDOVER.md 공식 기록) | `hqs/development/cli.py`가 사실상 후속 진입점이나 공식 폐기 선언 없음 | **KEEP** |
| `stages/04_implementation/architecture_validation/`(9개 파일) | Ponytail Multi-Agent 실험 harness | 전용 테스트 2개 | 매우 높음 — 열려 있는 `ADC-0040` NOT DETERMINED의 지정 Evidence 도구 | 없음(향후 재사용 예정) | **KEEP** |
| `stages/06_devops_release/README.md` | 미구현 placeholder | 문서만 | 있음(Architecture 스코프 정의) | N/A(애초에 구현이 없음, 삭제할 코드 자체가 없음) | **KEEP** |
| `archive/v1/`(146개 파일) | v1 Architecture 전체 스냅샷 | `BASELINE.md`가 직접 인용 | 매우 높음 | v2(`hqs/`) | **KEEP**(이미 올바르게 보관됨) |
| `docs/decisions/{rfc,adc,adr}/` | Structure v1.0 Migration 결정 기록 | `BASELINE.md`/`RFC-0029`/`RFC-0030`이 인용 | 매우 높음 | 없음(별개 트랙, 대체 관계 아님) | **KEEP** |
| `core/`(execution layer) | Kernel/Execution Layer 별도 트랙 | Governance 트랙 존재, `hqs/`와 무관 | 있음 | N/A | **KEEP(범위 밖)** |
| `projects/`(sibling-import 5개: `openrouter-auto-selection-v1`, `stage05-parallel-validation-harness-v1`, `runtime-boundary`, `command-contract`, `unified-dashboard`) | 다른 실험 프로젝트가 실제 import 중 | 다른 project의 `sys.path`/`importlib` 참조 | 있음 | 없음(삭제 시 즉시 import 오류) | **KEEP** |
| `projects/`(1회성 Dogfooding/PoC 27개: 주식/ETF/배당주 분석, `dev-hq-timeout-recovery-prototype` 등) | 완결된 실험, 코드 활동 없음(단일 커밋 이후 무변경) | `docs/research/`가 여전히 인용 | 있음(Evidence 원본) | 없음 | **ARCHIVE 후보**(삭제 아님 — 물리적 재배치만 검토 가능, §10) |
| `.claude/` 전체 | Skill/설정 정의 | 활성 사용 중 | N/A | N/A | **KEEP(범위 밖, 관련 없음)** |
| 미추적 `__pycache__`/`.pyc` | 빌드 산출물 | git 미추적(0건) | 없음 | N/A | **삭제 대상 아님**(버전 관리 대상이 아니므로 "삭제 후보" 자체가 성립하지 않음) |

**DELETE 조건(active reference=0 & architecture dependency=0 &
governance dependency=0 & historical value 없음/별도 보존)을 전부
만족하는 항목은 이번 조사에서 발견되지 않았다.**

## 8. SIZE / SCOPE

- **삭제 후보 파일 수**: **0개**
- **삭제 후보 디렉터리 수**: **0개**
- **예상 제거 LOC**: **0**
- **보존해야 할 Archive/Evidence 수**: `archive/v1/`(146 파일) +
  `docs/decisions/`(3개 하위 디렉터리, 다수 파일) + `hqs/development/mvp/`
  MVP 프로토타입 6개 파일 + `architecture_validation/` 9개 파일 +
  `projects/` 45개 디렉터리 전부(그중 27개는 "물리적 재배치 검토
  가능" 상태, §10 DEFER) — **총 200개 이상의 파일이 "삭제하면 안 되는
  Historical/Active Evidence"로 확인됨**.
- **삭제 전 필요한 추가 확인**: 이번 조사 결론상 "삭제 전 확인"이
  아니라 **"애초에 삭제 대상이 없다"**가 결론이다. 다만 §10 DEFER
  항목(27개 1회성 `projects/` 실험)을 물리적으로 `projects/archive/`
  같은 하위 폴더로 재배치하는 것을 고려한다면, 그 전에 (a) 각
  `docs/research/*.md`의 경로 참조가 상대 경로인지 절대 경로인지
  확인, (b) 이동이 `docs/research/` 문서들의 링크를 깨뜨리지 않는지
  확인, (c) 사용자의 명시적 승인이 필요하다.

## 9. SAFETY CHECK

Python AST/import 기반 확인(직접 실행):

- `hqs/development/` 전체에서 `mvp.workflow_0002` 등 6개 MVP
  프로토타입 모듈을 import하는 코드는 **자기 자신의 테스트 파일과
  형제 프로토타입 파일들뿐**임을 grep으로 확인 — 삭제 시 깨지는
  것은 `mvp/tests/test_workflow_0002.py` 등 6개 테스트 파일과
  형제 파일 간 참조(`workflow_0009.py`가 `workflow_0008.py`를 참조)
  뿐, Production entrypoint(`cli.py`/`workflow.py` 최상위)는 영향
  없음.
- `stages/04_implementation/architecture_validation/`을 삭제하면
  `test_stage04_arch_validation_harness.py`/`_extended.py` 2개 테스트
  파일이 즉시 깨진다(import 실패) — Production `stage_04.py`는
  영향 없음.
- `projects/openrouter-auto-selection-v1/`을 삭제하면
  `projects/openrouter-free-model-selection-architecture-experiment-v1/`
  의 `domain/_sibling_import.py`가 `importlib.util.spec_from_file_location`
  호출 시점에 `FileNotFoundError`를 던진다(경로 확인, 실제 실행은
  하지 않음) — 이 프로젝트의 offline 테스트 24개 전부 즉시 깨짐.
- `projects/runtime-boundary/`를 삭제하면 `process-runtime-strategy`/
  `dev-hq-vertical-slice`의 `sys.path.insert()` 대상 경로가 사라져
  두 프로젝트의 스크립트 실행이 `ModuleNotFoundError`로 즉시 실패.
- `projects/command-contract/`, `projects/unified-dashboard/` 삭제
  시 각각 2~3개 프로젝트의 import가 깨짐(§2 projects 조사 인용).
- Package discovery(예: `setup.py`/`pyproject.toml`의 자동 탐색)는
  이 저장소에 존재하지 않음(각 `projects/*`는 독립 `sys.path` 조작
  기반) — 따라서 "패키지 탐색이 깨진다"는 유형의 위험은 없음, 대신
  "하드코딩된 상대 경로 문자열이 깨진다"는 위험이 실제 위험이다.
- Documentation link: `docs/research/*.md`가 `projects/<name>/` 경로를
  텍스트로 인용하는 경우가 다수 확인됨 — 실제 삭제/이동 시 이 링크들이
  깨진다(단, 이는 실행이 깨지는 것이 아니라 문서 탐색성 저하).

## 10. FINAL RESULT

### DELETE NOW

**없음.** 이번 조사 범위 전체(hqs/development/, projects/, docs/,
tests/, .claude/, archive/, core/, docs/decisions/) 에서 즉시 삭제해도
안전한 파일/디렉터리를 찾지 못했다.

### KEEP

- `hqs/development/` 내 모든 확인 대상(§7 표 상단 5개 행) — 전부
  Active 또는 Historical-cited-by-Governance.
- `archive/v1/`(146개 파일) — 이미 올바르게 보관된 Historical Evidence.
- `docs/decisions/{rfc,adc,adr}/` — 별개의 유효한 Governance 트랙.
- `core/`(Kernel/Execution Layer) — 범위 밖, 별도 트랙.
- `projects/`의 sibling-import 5개 프로젝트(`openrouter-auto-selection-v1`,
  `stage05-parallel-validation-harness-v1`, `runtime-boundary`,
  `command-contract`, `unified-dashboard`) — 삭제 시 즉시 다른 프로젝트
  깨짐.
- `.claude/` 전체 — 범위 밖, 무관.

### DEFER(삭제 가능성은 있으나 추가 Governance/Architecture 판단 필요)

- `projects/`의 27개 1회성 Dogfooding/PoC 프로젝트(주식/ETF/배당주
  분석 22개 + `dev-hq-timeout-recovery-prototype`/
  `synthesis-trader-expansion-prototype`/
  `kernel-parallel-execution-prototype`/
  `investment-hq-checkpoint-detection-prototype`/
  `dev-hq-agent-responsibility-decomposition-v1`/일부
  `workflow-adapter-*`) — **코드 활동은 완전히 종료됐고
  `docs/research/`가 여전히 인용하지만, 삭제가 아니라 "물리적
  재배치(예: `projects/archive/` 하위로 이동, 내용은 그대로 보존)"
  검토가 가능한 유일한 후보군**이다. 다만 이는 (a) Stage→Team
  Migration과 직접 관련 없는 별개 정리 작업(Investment HQ Dogfooding
  포함)이고, (b) 문서 링크 파급 범위를 먼저 확인해야 하며, (c) 삭제가
  아닌 재배치조차 사용자의 명시적 승인이 필요하다고 판단해 이번
  조사는 실행하지 않았다.
- `mvp/workflow.py::run_mvp_0001` + `mvp/cli.py` — 공식적으로 폐기
  선언된 적은 없으나, `hqs/development/cli.py`가 사실상 후속
  진입점 역할을 하고 있어 "이 구 진입점을 공식적으로 Deprecated로
  문서화할지"는 Governance 판단이 필요하다(삭제가 아니라 상태
  명시화 수준의 낮은 리스크 결정).

## 최종 보고

1. **발견된 Archive/Legacy**: `archive/v1/`(이미 정상 보관), MVP
   프로토타입 6개 + 구 진입점 2개(Historical Evidence로 활성 인용),
   `architecture_validation/` 실험 harness(열린 ADC의 지정 도구),
   `projects/` 45개 중 27개가 코드 활동 종료 상태.
2. **DELETE NOW**: 없음(0개).
3. **KEEP**: `hqs/development/`의 조사 대상 전부, `archive/v1/`,
   `docs/decisions/`, `core/`, `projects/`의 sibling-import 5개,
   `.claude/` 전체.
4. **DEFER**: `projects/`의 1회성 Dogfooding/PoC 27개(재배치만 검토
   가능, 삭제 아님), 구 MVP-0001 진입점의 공식 Deprecated 문서화 여부.
5. **삭제 규모**: 파일 0개, 디렉터리 0개, LOC 0.
6. **의존성/안전성**: §9 참조 — 5개의 실제 sibling-import 체인과
   다수의 test-import 체인을 확인, 어느 것도 깨뜨리지 않았다(읽기
   전용 조사).
7. **다음 삭제 작업 순서**: 해당 없음(삭제 작업 자체가 없음). 굳이
   다음 단계를 제시한다면: (a) 27개 DEFER 대상의 재배치 여부를 사용자가
   별도로 판단, (b) `mvp/cli.py`/`run_mvp_0001`의 공식 상태 문서화
   여부를 사용자가 판단 — 둘 다 이번 조사의 범위를 벗어난 별개
   결정이다.

---

### 별도 확인 항목

- **Architecture**: 변경 없음(이번 조사는 읽기 전용).
- **Contract**: 변경 없음.
- **Governance**: 어떤 RFC/ADC/ADR/Baseline도 수정하지 않았다.
- **Production Code**: 변경 없음(파일 삭제 0건).
- **Validation Gate**: 이 조사와 무관(`ADR-0027` §9는 그대로 OPEN
  상태 — 이번 작업에서 건드리지 않음).
- **Branch**: `claude/jarvis-openrouter-validation-bin9aj`
- **Commit**: 이 Evidence 문서 추가가 새 commit(코드 변경 없음).
- **PR**: 없음(생성하지 않음).

## Related

- `hqs/development/HANDOVER.md`
- `hqs/development/teams/README.md`
- `docs/architecture/core/ADC-0001-core-baseline.md`,
  `ADC-0014-execution-responsibility-naming.md`,
  `ADC-0016-multi-task-minimal-responsibility.md`(MVP 프로토타입을
  Decision 근거로 직접 인용)
- `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md`,
  `ADC-0040-stage04-multi-agent-ponytail-decision.md`(architecture_validation/
  harness governing)
- `docs/architecture/core/ADR-0006-structure-v1-migration.md`(archive/
  제외 명시)
- `docs/architecture/baseline/BASELINE.md`(archive/v1 직접 인용)
- `docs/decisions/rfc/README.md`, `docs/decisions/adr/README.md`
- `docs/research/STAGE-TO-TEAM-OPENROUTER-MIGRATION-COMPREHENSIVE-REVIEW-0001.md`
- `docs/research/TEAM-ARCHITECTURE-DESIGN-VS-IMPLEMENTATION-GAP-ANALYSIS-0001.md`
