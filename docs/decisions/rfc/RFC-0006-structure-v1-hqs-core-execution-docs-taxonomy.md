# RFC-0006: Structure v1.0 — hqs/, core/execution/ 재배치 및 docs Taxonomy 정리

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (사용자 요청, Target Architecture 문서 검토에 따른 RFC)
**대상**: `development-hq/`, `investment-hq/`, `core/execution_layer/`의 물리적 재배치와 `docs/` taxonomy 정리 — Migration 실행은 포함하지 않는다.
**Target Architecture 근거**: 사용자가 첨부한 `Jarvis OS Structure v1.0 — Frozen.pdf`(이하 "Structure v1.0"). 이 문서는 이 저장소의 기존 Governance 산출물이 아니라 외부에서 반입된 Target Architecture 문서다 — RFC → ADC → ADR 절차를 거치기 전까지는 이 저장소의 Baseline이 아니다.
**선행 Repository Intelligence**: 이 세션에서 수행한 Current Structure ↔ Target Structure 비교(승인됨) — `core/`, `development-hq/`, `investment-hq/`, `docs/`, `archive/` 실측 결과를 그대로 인용한다.

> 본 RFC는 어떤 파일도 이동·삭제·수정하지 않는다. `core/registry/`,
> `core/communication/{events,context,memory,observability}`,
> `dashboard/`, `integrations/`, `hqs/shared/` 등 미구현 영역의 실제
> 구현을 다루지 않는다. `projects/`의 HQ별 분류를 결정하지 않는다.
> 새 Capability/Feature를 제안하지 않는다.

---

## 1. Problem

### 1.1 현재 Repository와 Structure v1.0 Target의 차이

Repository Intelligence 실측 결과(승인됨), 세 층위에서 구조적 차이가 있다.

| 영역 | 현재 | Target(Structure v1.0) | 성격 |
|---|---|---|---|
| Development HQ | `development-hq/` (repo root) | `hqs/development/` | 물리적 이동 |
| Development HQ Workflow | `development-hq/stages/01_repository_intelligence`~`06_devops_release` | `hqs/development/workflows/software-development/01~06` (이름은 이미 일치) | 계층 이동 |
| Investment HQ | `investment-hq/` (repo root) | `hqs/investment/` | 물리적 이동 |
| Execution Layer | `core/execution_layer/` | `core/execution/` (Target에서는 `core/communication/execution/` 하위) | 이름 변경 + 계층 이동 |
| 문서 Taxonomy | `docs/{00_governance, 01_architecture, 01_mvp, 02_rfc, 03_adc, 04_adr, architecture, core, governance, research}`(9개 병렬 디렉터리, 190개 파일) | `docs/{architecture, decisions/{rfc,adc,adr}, specifications, validation, research}`(5개 계층 구조) | 대규모 재배치 |

### 1.2 현재 구조가 장기 Architecture와 불일치하는 이유

- `hqs/` 상위 디렉터리가 없어 Multi-HQ 확장(Development HQ, Investment HQ, 향후 추가 HQ)이 repo root에 평면적으로 나열되고 있다 — Structure v1.0의 "여러 업무 영역을 HQ 단위로 운영"이라는 경계가 물리적으로 드러나지 않는다.
- `core/execution_layer/`는 이름이 Kernel의 `communication/execution` 개념과 분리되어 있어, `docs/architecture/core/`가 정의한 Kernel 구조(Registry/Communication 2대 축)와 실제 디렉터리 배치가 대응하지 않는다.
- `docs/`의 9개 병렬 디렉터리는 이 저장소가 성장하며 순차적으로 추가된 것(`00_governance`, `01_architecture`, `01_mvp`는 Development HQ 초기, `architecture/core`·`core/execution-layer`는 Kernel RFC 도입 시점, `governance/`는 그 이후 재정리 시도)으로, 서로 다른 시점의 명명 규칙이 공존한다 — 신규 기여자나 Agent가 "Kernel RFC가 어디 있는가"를 문서 트리만으로 파악하기 어렵다.

---

## 2. Motivation

- **Multi-HQ 구조 정렬**: `hqs/development/`, `hqs/investment/`를 같은 부모 아래 두어, Investment HQ가 이미 증명한 "Dev HQ Reference Architecture 재사용" 원칙(`investment-hq/STRUCTURE.md`)을 디렉터리 배치에서도 드러낸다.
- **Development HQ의 `hqs/development/` 통합**: Development HQ가 관리하는 `agents/`, `runtime/`, `scripts/`, `tests/`, `config/`, `artifacts/`를 한 위치로 모아 "Root에 별도 scripts/tests/config를 두지 않는다"는 Structure v1.0 원칙을 충족한다.
- **Kernel 구조 정렬**: `core/execution/`을 Kernel의 `communication/` 개념 아래 위치시켜, 향후 `events/`, `context/`, `memory/`, `observability/`(모두 Deferred)가 추가될 때 `execution/`과 같은 층위에서 자연스럽게 확장되도록 한다.
- **docs taxonomy 정리**: RFC/ADC/ADR을 `decisions/`로, Baseline/Kernel 정의를 `architecture/`로, MVP/Dogfooding Evidence를 `validation/`으로 모아 "공식 기록"과 "연구 중 내용"(`research/`)의 경계를 명확히 한다.

---

## 3. In Scope

1. `development-hq/` → `hqs/development/` (문서 8개 + `mvp/` 코드 + `stages/` 전체)
2. `development-hq/stages/01~06` → `hqs/development/workflows/software-development/01~06`
3. `investment-hq/` → `hqs/investment/`
4. `core/execution_layer/` → `core/execution/`
5. 위 4개 이동에 연동되는 Python `import`/`sys.path` 참조 갱신(실측 57건의 `sys.path.insert` 참조, 14건의 `execution_layer` import, 11건의 Development HQ 내부 상대 import, Investment HQ의 `DEV_HQ_ROOT` 기반 경로 3건)
6. 문서 내부 경로 참조 갱신(190개 `docs/` 파일 + `README.md`/`CLAUDE.md`가 인용하는 구 경로)
7. `docs/` taxonomy Migration(§6에서 상세)
8. Migration이 실제로 필요로 하는 Target directory skeleton만 구성 — Structure v1.0에 나열된 모든 디렉터리를 무조건 생성하지 않는다.

## 4. Out of Scope / Deferred

- `projects/`를 HQ별로 물리적으로 분류할지 여부
- `hqs/shared/`의 실제 도입 시점과 범위
- `core/registry/`(runtime/scheduler/policy) 신규 구현
- `core/communication/`의 `events/`, `context/`, `memory/`, `observability/` 신규 구현
- `dashboard/` 신규 구현
- `integrations/` 신규 구현
- `AGENTS.md`, `LICENSE`, `.env.example`, `pyproject.toml`, `examples/` 등 신규 파일/디렉터리 도입
- 신규 Feature 개발 일체

이 항목들은 Structure v1.0 PDF 자신이 "Deferred Decisions"로 명시했거나, PDF의 "Current Implementation Rule"("문서에 존재하는 모든 디렉터리를 현재 Repository에 즉시 생성하지 않는다")에 해당한다. 이번 RFC는 이 항목들을 Target Boundary로만 유지하며, 실제 구현 여부는 각각 별도 RFC 대상이다.

---

## 5. Migration Strategy

- **보존 우선**: 기존 기능과 Artifact(18건 완료 Dogfooding, `archive/v1/`, 51개 `docs/01_mvp/` Observation, Investment HQ 실행 산출물 등)를 이동 대상에서 제외하거나, 이동하더라도 내용을 변경하지 않는다 — `git mv`에 준하는 이동만 수행하고 재작성하지 않는다.
- **이동 후 참조 갱신**: 디렉터리를 먼저 옮기고, 그다음 단계로 import/`sys.path`/문서 경로 참조를 갱신한다(ADR-0002 §6 Migration Strategy가 채택한 순서 원칙 재사용 — "한 번에 모두 바꾸지 않고 순서대로 적용하며, 각 단계 후 검증한다").
- **즉시 삭제 금지**: 이동 후 남는 옛 경로의 빈 디렉터리나, Migration 과정에서 "더 이상 필요 없어 보이는" 파일이 발견되더라도 이번 RFC의 Migration 단계에서는 삭제하지 않는다 — 삭제는 이번 RFC의 범위가 아니다.
- **Audit 이후 결정**: 무엇을 유지·통합·삭제할지는 이번 Migration이 완료되고 Development HQ/Investment HQ Dogfooding이 새 경로에서 안정적으로 재현된 이후, 별도 Audit에서 결정한다 — 이는 이 세션에서 이미 수행한 "Docstring/Comment Audit → History→Evidence Canonicalization Audit" 패턴(Evidence → 필요성 판단 → 실행)과 동일한 절차를 구조 Migration에도 적용하는 것이다.
- **추적 가능성 보존**: `git mv` 기반 이동은 Git 이력상 파일 이동으로 추적되므로, 향후 Audit에서 "이 파일이 어디서 왔는가"를 `git log --follow`로 복원할 수 있다. 이 추적 가능성이 깨지는 방식(재작성 후 새 파일로 커밋 등)은 피한다.

---

## 6. Documentation Migration

### 6.1 현재 → Target 매핑 초안

| 현재 | 대응 관계 | Target | 확실성 |
|---|---|---|---|
| `docs/01_architecture/BASELINE.md` | 1:1 | `docs/architecture/baseline/` | 명확 |
| `docs/architecture/core/*` (Kernel RFC/ADC/ADR/GOVERNANCE-REVIEW) | 1:1 | `docs/architecture/kernel/` | 명확 |
| `docs/02_rfc/*` (Development HQ 수준 RFC) | 1:1 | `docs/decisions/rfc/` | 명확 |
| `docs/03_adc/*` | 1:1 | `docs/decisions/adc/` | 명확 |
| `docs/04_adr/*` | 1:1 | `docs/decisions/adr/` | 명확 |
| `docs/governance/adc/*`, `docs/governance/rt/*` | 부분 1:1 | `docs/decisions/adc/` (RT는 대응 항목 없음) | **불명확** |
| `docs/governance/observations/*` | ? | `docs/validation/mvp/` 또는 별도 | **불명확** |
| `docs/01_mvp/*`(53개 Observation) | ? | `docs/validation/mvp/` | 대체로 명확하나 일부는 `research/`에 더 가까움 |
| `docs/core/execution-layer/*`(RFC/ADC/ADR/observation/artifact-mapping 혼재, 27개) | ? | `decisions/`와 `validation/`으로 분리 필요 | **불명확 — 파일 단위 판단 필요** |
| `docs/research/*`(44개, ENGINE-CONNECT/PHASE9~12/Team Definition 등) | 부분 1:1 | `docs/research/{ai,architecture,infrastructure}` | Target이 3개 하위분류를 요구하나 현재 파일들의 분류 기준 없음 — **불명확** |
| `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`, `GLOSSARY.md` | ? | Target에 대응 디렉터리 없음(Target은 이 둘을 어디에 두는지 명시하지 않음) | **불명확** |
| `investment-hq/STRUCTURE.md`, `development-hq/STRUCTURE.md`/`BASELINE.md`/`CONSTITUTION.md` 등 HQ 자체 문서 | 이동만(HQ와 함께) | `hqs/development/README.md` 등 | Target은 HQ당 `README.md` 1개만 명시 — 현재 8개 문서(BASELINE/BOUNDARY/CONSTITUTION/HANDOVER/IMPLEMENTATION_RULES/MISSION/MVP/RESPONSIBILITY/STRUCTURE)를 어떻게 배치할지 **불명확** |

### 6.2 처리 원칙

- 위 표에서 "명확"으로 표시된 항목은 ADC에서 기계적으로 승인 가능한 매핑이다.
- "불명확"으로 표시된 항목은 **이번 RFC가 임의로 분류하지 않는다** — ADC의 Decision Candidate로 등록해, 다음 중 하나를 ADC 단계에서 결정한다: (a) Target taxonomy를 그대로 따르되 판단 기준을 ADC가 정의, (b) 현재 9-디렉터리 구조를 유지하되 Target에 대응 주석만 추가, (c) 일부 문서군(`docs/00_governance/` 등)을 위해 Target에 없는 디렉터리를 추가 제안.
- Development HQ의 8개 자체 문서(BASELINE/BOUNDARY/CONSTITUTION/...)를 Target의 "HQ당 README.md 1개" 모델에 맞출지, 그대로 유지할지도 ADC Decision 대상이다 — 이 RFC는 어느 쪽도 선택하지 않는다.
- 기존 Governance 문서(RFC/ADC/ADR)의 **역사적 의미는 보존**한다 — 파일을 재배치하더라도 문서 내용(승인 경로, Context, Evidence 인용)은 수정하지 않으며, ID(RFC-0001 등)도 유지한다. Migration은 위치만 바꾸는 것이지 결정 이력을 다시 쓰는 것이 아니다.

---

## 7. Impact Analysis

| 영역 | 영향 | 실측 근거 |
|---|---|---|
| Python import | `core/execution_layer/` → `core/execution/`: `from execution_layer.*` 형태 import 14건 갱신 필요. `development-hq/mvp/` 내부: 상대 import(`from .agents`, `from mvp.workflow` 등) 11건은 패키지 이동 시 자동 유지되나, 외부에서 이 패키지를 참조하는 지점(`investment-hq/engine_client.py`의 `DEV_HQ_ROOT` 등) 갱신 필요 | grep 실측 |
| sys.path | 저장소 전체에서 `sys.path.insert` 57건 — 대부분 `Path(__file__).resolve().parents[N] / "development-hq"` 또는 `"core"` 형태의 상대 경로 계산이라, 디렉터리 깊이가 바뀌면(`hqs/development/`는 `development-hq/`보다 1단계 깊음) `parents[N]`의 N 값도 함께 바뀌어야 한다 | grep 실측 |
| pytest | `pytest.ini`의 testpaths/설정이 현재 경로를 전제로 하지 않는지 확인 필요(현재 `python3 -m pytest --ignore=archive`로 전역 discovery하므로 경로 이동 자체는 discovery를 깨지 않을 가능성이 높으나, 개별 테스트 파일의 `sys.path.insert`는 위와 동일하게 영향받는다) | `pytest.ini` 확인 필요(Migration 단계에서) |
| 문서 내부 경로 | `docs/` 190개 파일이 서로를 `docs/01_mvp/MVP-00XX-observation.md` 같은 상대/절대 경로 문자열로 인용 — taxonomy 변경 시 전수 grep 후 치환 필요 | 파일 수 실측 |
| CI/CD | `.github/`가 현재 존재하지 않음 — 이동 대상 CI 설정 자체가 없으므로 이 항목은 영향 없음(Target의 `.github/`는 신규 도입이며 Out of Scope) | `ls .github` 확인 |
| Claude Code workflow | `.claude/skills/*/SKILL.md`, `CLAUDE.md`의 Context Loading 섹션이 `development-hq/`, `investment-hq/`, `docs/01_architecture/` 등 구 경로를 직접 언급 — 갱신 필요 | `CLAUDE.md` 실측(이전 Audit에서 이미 stale로 확인된 부분과 일부 중복) |
| 기존 Dogfooding artifact | `projects/` 18건, `investment-hq/dogfooding/`(4건: efa-2026-08 등 tracked, aapl-hq-verify/pg-hq-verify는 untracked) — 이번 RFC In Scope는 `investment-hq/` 디렉터리 자체의 이동이므로, 그 안의 `dogfooding/` 산출물도 함께 이동하되 내용은 변경하지 않는다. `projects/`는 Out of Scope(§4)이므로 이동하지 않는다 | 실측 |
| archive 및 historical reference | `archive/v1/`은 Target의 `archive/{architecture,development-hq,validation,deprecated}`와 이름이 다르나, 이번 RFC In Scope에 `archive/` 재정리를 포함하지 않았다 — 별도 판단(§4에 명시적으로 포함되지 않았으므로 Out of Scope로 취급, ADC에서 명확히 재확인 필요) | PDF §Structure v1.0, 실측 |

---

## 8. Validation Plan

Migration이 실제로 승인·실행될 때 적용할 검증 순서(이번 RFC 단계에서는 실행하지 않는다):

1. `python3 -m pytest --ignore=archive` — 전체 통과(현재 182건) 확인, 회귀 없음.
2. `python3 -m py_compile`(이동된 모든 `.py` 파일) — 문법 오류 없음 확인.
3. import/path reference 검색 — `grep -rn "development-hq\|investment-hq\|execution_layer"` 잔존 여부 전수 확인(옛 경로 문자열이 새 경로 갱신에서 누락되지 않았는지).
4. `docs/` 내부 링크 검증 — 이동된 문서가 서로를 가리키는 경로 문자열이 실제 파일 위치와 일치하는지 확인.
5. `git status` 확인 — 의도한 이동/갱신 외 파일이 변경되지 않았는지, `archive/`와 완료된 18건 Dogfooding 프로젝트가 무변경인지 확인.
6. 기존 기능 regression 확인 — `development-hq/mvp/cli.py`, `investment-hq/run.py`가 이동 후에도 동일하게 실행되는지(스모크 실행).
7. 최종 Structure Drift 검사 — Migration 후 남은 차이(이번 RFC In Scope에 포함되지 않은 항목들)를 다시 표로 기록해, "완료된 것"과 "여전히 Target Boundary로만 남은 것"을 구분한다.

---

## 9. Decision Required (ADC 대상)

1. **범위 순서**: 전체 Migration(`hqs/`, `core/execution/`, `docs/` taxonomy)을 한 번에 수행할지, 영역별로 단계적으로 수행할지(예: `core/execution_layer/` 먼저 — ADR-0002 §5가 이미 이 영역을 별도 취급하도록 예견함 → `development-hq/`/`investment-hq/` → `docs/` taxonomy 순).
2. **docs taxonomy 처리 방식**: §6.1의 "불명확" 항목들을 한 번에 전부 결정할지, 명확한 항목(`01_architecture`, `02_rfc`, `03_adc`, `04_adr`)만 먼저 옮기고 불명확한 항목(`01_mvp`, `governance/`, `core/execution-layer/`, `research/` 세부분류, `00_governance/`)은 별도 후속 ADC로 미룰지.
3. **HQ 자체 문서 배치**: Development HQ의 8개 문서(BASELINE/BOUNDARY/CONSTITUTION/HANDOVER/IMPLEMENTATION_RULES/MISSION/MVP/RESPONSIBILITY/STRUCTURE)를 Target의 "HQ당 README.md 1개" 모델에 맞출지, 현행 유지할지.
4. **`archive/v1/` 재정리 포함 여부**: 이번 Migration 범위에 `archive/` 이름 정리를 포함할지, 완전히 별도 사안으로 분리할지.

---

## 관련 문서

- Target Architecture: 사용자 첨부 `Jarvis OS Structure v1.0 — Frozen.pdf`(저장소 외부 문서, 이 RFC가 최초로 저장소 Governance에 반입)
- 선행 Repository Intelligence: 이 세션에서 수행·승인된 Current/Target 비교(별도 문서화되지 않음 — 세션 기록)
- 충돌·정합성: `docs/04_adr/ADR-0002-core-to-kernel-terminology-unification.md` §5(§10 참조)
- Baseline: `docs/01_architecture/BASELINE.md`
- Development HQ 경계: `development-hq/IMPLEMENTATION_RULES.md`, `docs/04_adr/ADR-0001-development-hq-stage-baseline-update.md`

## 10. 기존 ADR과의 관계 (충돌 명시)

**충돌이 아니라 선례다.** `docs/04_adr/ADR-0002-core-to-kernel-terminology-unification.md` §5는 정확히 `core/execution_layer/`의 경로 변경을 다루며 다음과 같이 판단했다:

> "`core/execution_layer/`는 실제 Python 패키지이며, 5개 테스트 파일과 5개 dogfooding 스크립트가 `sys.path` 조작과 `execution_layer.*` import로 이 경로에 의존한다. 경로 변경은 문서 작업이 아니라 **코드 변경**이며, 42개 테스트 전부를 재검증해야 한다... 별도 ADR로 다룰 후보로 남긴다."

그리고 §5는 `docs/04_adr/ADR-0001-development-hq-stage-baseline-update.md`의 동일 판단("코드 디렉토리(`development-hq/mvp/`)는 변경하지 않는다... 기존 코드는 이동하거나 수정하지 않는다")을 인용해 같은 원칙을 재확인했다.

**이 RFC는 ADR-0001·ADR-0002를 무시하거나 뒤집지 않는다.** 오히려 두 ADR이 "지금 하지 않는다"고 명시적으로 미뤄둔 바로 그 후속 결정을 이번에 정식으로 여는 것이다 — ADR-0002 §5의 표현을 빌리면, 이 RFC가 그 "절차 부채"를 상환하는 절차의 시작이다. 이 RFC가 ADC → ADR로 이어져 승인되면, ADR-0002 §5는 그 후속 ADR에 의해 대체(supersede)된 것으로 기록되어야 한다 — 이번 RFC 문서 자체는 ADR-0002를 수정하지 않는다.

---
