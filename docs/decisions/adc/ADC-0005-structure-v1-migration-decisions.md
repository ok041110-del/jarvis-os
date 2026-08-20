# ADC-0005: Structure v1.0 Migration — RFC-0006 후속 Decision 4건

## 목적

`docs/02_rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md`
§9(Decision Required)가 등록한 4개 항목을 판단한다. 근거는 RFC-0006
자체, 이 세션에서 승인된 Repository Intelligence 실측, 그리고 기존
Governance 문서(`docs/04_adr/ADR-0001`, `ADR-0002`, `CLAUDE.md`,
`docs/03_adc/README.md`, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`)
로 한정한다.

## 이 문서의 위치에 대한 메모

`docs/03_adc/ADC.md`는 스스로 "Jarvis OS(Kernel) 수준 Open
Decision(ADC-01~12)만 다룬다"고 명시하고 있어, RFC-0006처럼 Development
HQ·Investment HQ·Kernel(`core/execution_layer/`)·`docs/` 거버넌스 자체를
동시에 가로지르는 결정은 그 파일의 선언된 범위에 정확히 들어맞지
않는다. Development HQ 수준 ADC는 `docs/governance/adc/`에 개별
파일(`ADC-0001`~`ADC-0004`)로 등록되는 관례가 있으나, 이 결정은 Development
HQ 단독 사안도 아니다. 사용자가 명시적으로 지정한 `docs/03_adc/`
위치를 따르되, `ADC.md`의 번호 체계(ADC-01~12)와 혼동되지 않도록 별도
파일(`ADC-0005-*.md`)로 분리한다 — `ADC.md`, `README.md`는 이번 작업에서
수정하지 않는다.

## 판단 대상에서 제외

- Migration의 실제 실행(이동/삭제/코드 수정) — 이 ADC는 결정만 하며, 실행은 ADR 승인 이후.
- RFC-0006 §4(Out of Scope)에 이미 열거된 항목(`projects/` 분류, `hqs/shared/`, `core/registry/`, `dashboard/`, `integrations/` 등) — 범위를 확대하지 않는다.
- RFC-0006 §6.1의 "불명확" 문서 매핑 표에서 개별 파일 단위 배치(어느 Observation이 `validation/`인지 `research/`인지 등) — 이는 Decision 2(taxonomy 단계적 처리)가 "결정"으로 넘어간 뒤 별도 후속 ADC/ADR에서 파일 단위로 판단한다.

---

## Decision 1. 전체 Migration vs 단계적 Migration

### Context
RFC-0006 In Scope는 `development-hq/`, `investment-hq/`, `core/execution_layer/` 3개 디렉터리 이동과 그에 연동된 참조 갱신, 그리고 `docs/` taxonomy 정리까지 포함한다. 이 넷을 한 번에 실행할지, 순서를 나눠 실행할지 결정이 필요하다.

### Current State
- 아직 어떤 이동도 실행되지 않았다.
- `core/execution_layer/`는 이미 별도 ADR(`ADR-0002` §5)에서 "코드 변경, 별도 ADR 대상"으로 명시적으로 분리된 이력이 있다 — 즉 이 영역만 독립적으로 판단된 선례가 있다.
- `development-hq/`, `investment-hq/`는 RFC-0006에서 처음으로 함께 논의된 대상이며, 별도로 분리된 선례는 없다.
- 실측 의존성 규모: `sys.path.insert` 57건, `execution_layer` import 14건, Development HQ 내부 상대 import 11건, `docs/` 190개 파일의 상호 경로 참조.

### Options
- **A. 전체 일괄(Atomic) Migration**: 4개 대상을 한 PR/한 커밋 단위로 동시에 이동·갱신.
- **B. 단계적(Phased) Migration**: 영역별로 분리해 순서대로 실행하고 각 단계마다 검증(`pytest`, `git status`)을 거친 뒤 다음 단계로 진행.

### 장점/단점

| | A. 일괄 | B. 단계적 |
|---|---|---|
| 장점 | 전환 기간이 짧다. "일부만 이동된 어중간한 상태"가 존재하지 않는다. | 각 단계마다 회귀를 즉시 격리해 원인 파악이 쉽다. 문제 발생 시 되돌릴 범위가 좁다. `core/execution_layer/`처럼 이미 독립적으로 판단된 영역을 그 판단 그대로 먼저 처리할 수 있다. |
| 단점 | 57+14+11건의 참조 갱신이 한 번에 겹쳐, 실패 시 원인이 어느 영역에서 왔는지 구분하기 어렵다. 리뷰 범위가 매우 커진다. | 중간 상태(예: `hqs/development/`는 존재하지만 `investment-hq/`는 아직 구 경로)가 일시적으로 존재해, 그 기간 동안 문서·CLAUDE.md가 두 경로 체계를 동시에 설명해야 할 수 있다. |

### Repository 영향
`core/execution_layer/`는 Development HQ와 결합도가 낮다(Development HQ의 `run_pipeline()`을 선택적으로만 참조하며, MVP-0006 Dogfooding처럼 아예 참조하지 않는 경로도 있음 — RFC-0006 §7 Impact Analysis). 반면 `development-hq/` ↔ `investment-hq/`는 `investment-hq/engine_client.py`가 `development-hq/mvp/engine.py`를 직접 import하는 강한 결합이 있다 — 이 둘은 분리해서 옮기면 한쪽만 이동된 상태에서 다른 쪽의 import 경로가 깨질 수 있어, 최소한 이 둘은 같은 단계에서 함께 처리해야 한다.

### Risk
일괄 Migration은 "42개(현재는 182개) 테스트 전부를 재검증해야 한다"는 `ADR-0002` §5의 우려가 4개 영역에 동시에 겹쳐 나타나는 시나리오다 — 실패 시 어느 참조 갱신이 문제인지 특정하기 어려워 롤백 범위가 저장소 전체가 된다.

### Recommendation
**B. 단계적 Migration.** `ADR-0002` §6("한 번에 모두 바꾸지 않고 순서대로 적용하며, 각 단계 후 검증한다")이 이미 이 저장소의 채택된 관례다. 제안 순서:
1. `core/execution_layer/` → `core/execution/` (가장 독립적, 이미 별도 판단된 이력)
2. `development-hq/` + `investment-hq/` → `hqs/development/` + `hqs/investment/` (강한 결합이 있으므로 함께)
3. `docs/` taxonomy(Decision 2의 결과에 따름)

### Decision Required
ADR에서 위 3단계 순서를 그대로 채택할지, 아니면 다른 순서(예: `docs/` taxonomy를 먼저)를 확정할지.

---

## Decision 2. docs taxonomy 일괄 Migration vs 단계적 Migration

### Context
RFC-0006 §6.1은 현재 `docs/`의 9개 병렬 디렉터리(190개 파일)를 Target의 5-계층 구조로 매핑하는 표를 제시했고, 그중 일부는 "명확"(1:1 대응), 일부는 "불명확"(파일 단위 판단 필요)으로 분류했다.

### Current State
- 명확: `docs/01_architecture/BASELINE.md`(1개) → `architecture/baseline/`, `docs/02_rfc/*`(7개) → `decisions/rfc/`, `docs/03_adc/*`(2개, 이 ADC 포함 시 3개) → `decisions/adc/`, `docs/04_adr/*`(6개) → `decisions/adr/`.
- 불명확: `docs/01_mvp/*`(53개), `docs/governance/*`(14개), `docs/core/execution-layer/*`(27개, RFC/ADC/ADR/observation/artifact-mapping 혼재), `docs/research/*`(44개, Target이 요구하는 `ai/architecture/infrastructure` 3분류 기준이 현재 없음), `docs/00_governance/*`(2개, Target에 대응 위치가 아예 없음).
- 불명확 항목의 합계(53+14+27+44+2 = 140개)가 명확 항목(약 16개)보다 압도적으로 많다 — 즉 taxonomy 정리의 대부분은 "불명확" 영역이다.

### Options
- **A. 일괄**: 명확·불명확 구분 없이 모든 190개 파일을 한 번에 Target taxonomy로 재배치.
- **B. 단계적**: 명확한 항목(약 16개)만 우선 이동하고, 불명확한 140개 항목은 파일 단위 판단을 위한 후속 ADC로 미룬다.

### 장점/단점

| | A. 일괄 | B. 단계적 |
|---|---|---|
| 장점 | `docs/`가 한 번의 작업으로 완전히 Target과 일치한다. | 명확한 항목만 먼저 옮겨 즉시 가치를 얻으면서, 리스크가 큰 140개 항목(임의 분류 시 RFC-0006이 금지한 "1:1 대응이 불명확한 문서를 임의 분류"에 해당할 위험)은 신중하게 처리한다. |
| 단점 | 140개 불명확 항목을 이번에 분류하려면 각 파일을 개별 판단해야 하는데, 이는 RFC-0006이 이미 "임의로 분류하지 않는다"고 명시한 것과 정면으로 충돌한다. | `docs/`가 한동안 신구 taxonomy가 섞인 상태로 남는다. |

### Repository 영향
`docs/01_mvp/`의 53개 Observation은 `development-hq/mvp/*.py`의 여러 docstring이 직접 인용하는 canonical Evidence다(이 세션의 History→Evidence Canonicalization Audit에서 확인). 이 파일들의 경로가 바뀌면 코드 docstring의 인용 경로도 함께 갱신해야 하므로, taxonomy 결정은 Decision 1의 코드 Migration과 순서 의존성이 있다.

### Risk
불명확 항목을 서둘러 일괄 분류하면, RFC-0006 §6.2가 이미 경고한 "임의 분류" 위험이 현실화된다 — 특히 `docs/core/execution-layer/`처럼 RFC/ADC/ADR과 observation이 한 디렉터리에 혼재된 영역은 `decisions/`와 `validation/`으로 쪼개는 기준 자체가 아직 없다.

### Recommendation
**B. 단계적.** 명확한 16개 항목만 우선 이동하고, 나머지 140개는 "불명확" 상태 그대로 후속 ADC(파일 단위 매핑 기준을 정하는 전용 ADC)로 넘긴다. 이는 Decision 1의 3단계 순서와도 맞물린다 — taxonomy Migration은 코드 Migration이 안정화된 이후, 그리고 명확한 부분부터 처리한다.

### Decision Required
ADR에서 "명확 16개"의 정확한 목록을 확정하고, "불명확 140개"를 다룰 후속 ADC의 트리거 조건(예: Development HQ/Investment HQ가 새 경로에서 안정적으로 재현된 이후)을 명시할지.

---

## Decision 3. Development HQ 자체 문서 구조를 Target의 "HQ README 중심 모델"에 맞출지

### Context
Structure v1.0 Target은 각 HQ 아래 `README.md` 1개만 명시한다(`hqs/development/README.md`). 현재 `development-hq/`는 `README.md` 외에 `BASELINE.md`, `BOUNDARY.md`, `CONSTITUTION.md`, `HANDOVER.md`, `IMPLEMENTATION_RULES.md`, `MISSION.md`, `MVP.md`, `RESPONSIBILITY.md`, `STRUCTURE.md` — 9개의 개별 최상위 문서를 갖는다.

### Current State
`CLAUDE.md`의 "Context Loading" 섹션이 이 9개 파일을 **개별 파일명으로 직접 인용**한다:
```
현재 작업 상태 → development-hq/HANDOVER.md
Development HQ 규칙 → development-hq/IMPLEMENTATION_RULES.md
Development HQ 구조 → development-hq/BASELINE.md
MVP → development-hq/MVP.md
```
이는 CLAUDE.md 자신의 "전체 문서를 작업마다 일괄 로드하지 않는다"는 원칙을 지탱하는 구조다 — Progressive Disclosure를 위해 문서를 목적별로 쪼개 놓은 것이며, 우연히 여러 파일이 된 것이 아니다. 반면 `investment-hq/`는 이미 `README.md` + `STRUCTURE.md` 2개뿐으로, Target 모델에 훨씬 가깝다(Investment HQ는 나중에 만들어졌고, Development HQ의 9-문서 구조를 그대로 답습하지 않기로 이 세션에서 이미 판단한 바 있다 — `investment-hq/STRUCTURE.md` 자체가 이 결정을 기록).

### Options
- **A. Target 모델에 맞춤**: 9개 문서를 `README.md` 1개로 통합(또는 대폭 축약)하고 세부 내용은 하위 디렉터리로 재배치.
- **B. 현행 유지**: Development HQ의 9-문서 구조를 그대로 이동만 하고 통합하지 않는다.
- **C. 혼합**: 새로 만들어지는 HQ(Investment HQ 등)는 Target의 단일 README 모델을 따르되, Development HQ처럼 이미 성숙한 9-문서 구조는 예외로 유지.

### 장점/단점

| | A. 통합 | B. 현행 유지 | C. 혼합(신규 HQ만 Target 모델) |
|---|---|---|---|
| 장점 | Target과 완전히 일치. | CLAUDE.md의 9개 직접 인용이 전혀 깨지지 않는다. Governance 문서(CONSTITUTION 등)의 개별 식별성이 유지된다. | 기존 안정 구조를 보존하면서, 신규 HQ에는 더 가벼운 모델을 적용할 수 있다 — Investment HQ가 이미 실제로 이렇게 하고 있다(Evidence 있음). |
| 단점 | CLAUDE.md의 9개 경로 인용을 전부 갱신해야 하고, "Constitution"·"Implementation Rules" 같은 개별 문서의 성격(하나는 원칙, 하나는 규칙)이 통합 시 흐려질 위험. 이는 문서 재작성이지 단순 이동이 아니다 — RFC-0006이 In Scope로 규정한 "경로 이동"의 범위를 넘어선다. | Target과 형식적으로 불일치하는 상태가 영구히 남는다. | 저장소 안에 두 가지 HQ 문서 모델이 공존 — 신규 기여자가 "어느 모델을 따라야 하는가" 혼란 가능. |

### Repository 영향
9개 문서를 1개로 통합하는 것은 파일 이동이 아니라 **문서 재작성**이다 — RFC-0006 §5(Migration Strategy)는 "이동 후 import/path/reference를 갱신"이라고만 규정했지, 문서 통합·재작성은 In Scope로 명시하지 않았다. Option A는 RFC-0006의 범위를 벗어난다.

### Risk
Option A를 이번 Migration에서 시도하면, CLAUDE.md의 "불필요한 상세 내용을 추가하지 않음" 원칙과 별개로 **기존 Governance 문서의 내용을 손실 없이 재배치했는지 검증하기 어려운 대규모 재작성**이 된다 — RFC-0006이 "삭제보다 Migration/Archive를 우선한다"고 명시한 원칙과 충돌할 위험이 크다.

### Recommendation
**C. 혼합.** Development HQ는 9-문서 구조를 그대로 이동만 하고(내용 재작성 없음), Investment HQ처럼 이미 단일/소수 문서로 구성된 HQ는 그대로 유지한다. Target의 "HQ당 README 1개" 표기는 최소 골격의 예시로 해석하고, 기존에 이미 성숙한 세분화 문서를 강제로 축소하는 지시로 해석하지 않는다 — 이는 RFC-0006 §6.2가 이미 "HQ 자체 문서 배치는 ADC Decision 대상"이라고 유보한 것과 일치한다.

### Decision Required
ADR에서 Option C를 공식 채택할지, 그리고 향후 신규 HQ(Investment HQ 이후)에 대해 "단일/소수 문서" 관례를 명문화할지(신규 RFC/ADC 없이 관례로만 둘지, 별도 규칙으로 남길지).

---

## Decision 4. `archive/v1/` 재정리를 이번 Migration에 포함할지

### Context
Target Structure는 `archive/{architecture/, development-hq/, validation/, deprecated/}` 4개 하위 디렉터리를 명시한다. 현재 `archive/v1/`은 `adapters/`, `apps/`, `docs/`, `hqs/`, `packages/`, `scripts/`, `tests/`, `CHANGELOG.md`, `VERSION` 등 완전히 다른 이름 체계(v1 스켈레톤 자체의 구조를 그대로 보존)를 갖는다.

### Current State
`archive/v1/`은 이미 "과거 Version" 그 자체로 동결되어 있다(`archive/` 완전 제외 원칙이 이 세션의 모든 Audit·Migration 작업에서 일관되게 적용됨 — Docstring Audit, History→Evidence Audit, 이번 RFC-0006 §4 Out of Scope 모두 `archive/`를 손대지 않았다). RFC-0006 §7(Impact Analysis)은 이 항목을 "이번 RFC In Scope에 포함하지 않았다"고 명시했다.

### Options
- **A. 포함**: 이번 Migration에서 `archive/v1/`을 Target의 4-디렉터리 이름 체계로 재정리.
- **B. 제외(Deferred)**: `archive/v1/`은 그대로 두고, 별도 시점에 별도로 판단.

### 장점/단점

| | A. 포함 | B. 제외 |
|---|---|---|
| 장점 | `archive/`까지 Target과 완전히 일치. | `archive/`의 "과거 그대로 보존"이라는 목적 자체와 충돌하지 않는다. 이번 Migration 범위가 커지지 않는다. |
| 단점 | `archive/v1/`은 이미 그 자체로 하나의 완결된 과거 스냅샷(v1 Starter Kit 전체 구조)이다 — 이름을 Target 체계로 바꾸면 "그 시점에 실제로 어떤 구조였는가"라는 Archive 본연의 기록성이 훼손된다. | `archive/`가 Target Structure와 형식적으로 불일치하는 상태가 남는다(다만 Archive는애초에 "현재 구조"가 아니므로 이 불일치는 Structure Drift로 취급하지 않을 수 있다). |

### Repository 영향
없음 — `archive/v1/`은 어떤 현재 코드/문서에서도 import되거나 참조되지 않는다(이 세션 전체에서 `archive/`는 조사 대상에서 항상 제외됐고, 실제 의존성도 확인된 바 없다).

### Risk
Option A의 리스크는 기능적이지 않고 **기록적**이다 — Archive는 "그 시점의 실제 상태"를 보존하는 것이 목적이므로, 이름을 현재 기준으로 바꾸는 것 자체가 목적에 반할 수 있다.

### Recommendation
**B. 제외(Deferred).** RFC-0006 §4·§7이 이미 이렇게 취급했고, 이 ADC도 그 판단을 재확인한다. `archive/v1/`의 재정리가 필요하다고 판단되면, 이번 Migration과 무관한 별도 RFC/ADC로 다룬다 — Archive 재정리는 "구조 정렬"이 아니라 "과거 기록을 어떻게 표시할 것인가"라는 다른 성격의 결정이기 때문이다.

### Decision Required
ADR에서 이 Deferred 판단을 그대로 확정할지, 아니면 향후 별도 RFC를 위한 최소 조건(예: Development HQ/Investment HQ Migration이 완료되고 안정화된 이후)을 명시할지.

---

## 요약

| Decision | Recommendation |
|---|---|
| 1. Migration 순서 | 단계적 — `core/execution/` → `hqs/{development,investment}/` → `docs/` taxonomy |
| 2. docs taxonomy | 단계적 — 명확한 16개 항목 우선, 불명확한 140개는 후속 ADC |
| 3. HQ 문서 구조 | 혼합 — Development HQ 9-문서 구조 유지, 신규/소규모 HQ는 Target의 단일 README 모델 |
| 4. `archive/v1/` | Deferred — 이번 Migration에서 제외 |

## 기존 ADR과의 관계

이 ADC의 어떤 권고안도 기존 ADR(`ADR-0001`, `ADR-0002`)과 충돌하지 않는다 — 오히려 Decision 1의 권고(단계적 Migration, `core/execution_layer/` 우선)는 `ADR-0002` §5·§6이 이미 채택한 원칙(코드 디렉토리 변경은 별도로 신중하게, 단계별 검증)을 그대로 계승한다. 이 ADC가 승인되어 ADR로 확정되면, 그 ADR은 `ADR-0002` §5(경로 변경을 이번 ADR에서 다루지 않음)를 supersede해야 한다 — RFC-0006 §10에서 이미 이 관계를 예고했다.

## Baseline/Architecture 직접 수정 여부

**없음.** 이 ADC는 어떤 Baseline 문서(`docs/01_architecture/BASELINE.md`, `development-hq/BASELINE.md` 등)도 수정하지 않았다. `docs/03_adc/ADC.md`, `docs/03_adc/README.md`도 수정하지 않았다.
