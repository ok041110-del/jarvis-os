# ADR-0006: Structure v1.0 Migration Decision 확정

| 필드 | 내용 |
|---|---|
| ID | ADR-0006 |
| 제목 | `hqs/`, `core/execution/` 재배치 및 `docs/` Taxonomy 정리를 위한 Migration Decision 확정 |
| 상태 | **Accepted** — Decision만 확정한다. Migration 실행은 이 ADR의 범위가 아니다. |
| Context | `docs/03_adc/ADC-0005-structure-v1-migration-decisions.md`의 4개 Decision Candidate |
| 관련 RFC | `docs/02_rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md` |
| 관련 ADC | `docs/03_adc/ADC-0005-structure-v1-migration-decisions.md` (Decision 1~4 전부 종결) |
| Target Architecture 근거 | 사용자 첨부 `Jarvis OS Structure v1.0 — Frozen.pdf` |

이 ADR은 ADC-0005가 이미 제시한 4개 Decision과 그 Recommendation을
다시 논의하지 않는다. ADC-0005의 근거(RFC-0006, Repository Intelligence
실측, `ADR-0001`, `ADR-0002`, `CLAUDE.md`)를 그대로 인용해 **결정만
확정**한다. 이 ADR은 **Migration을 실행하지 않는다** — 실행은 이 ADR
승인 이후 별도 작업으로 진행되며, `docs/01_architecture/BASELINE.md`
갱신도 그 실행·검증이 끝난 뒤에 별도로 이루어진다(§6 Consequences 참고).

## Out of Scope (이 ADR이 다루지 않는 것)

- 실제 디렉터리 이동, 코드 수정, import/경로 갱신 — Migration 실행은 이 ADR 이후 단계다.
- RFC-0006 §4가 이미 Out of Scope로 못박은 항목(`projects/` 분류, `hqs/shared/`, `core/registry/`, `core/communication/{events,context,memory,observability}`, `dashboard/`, `integrations/`, `AGENTS.md`/`LICENSE`/`.env.example`/`pyproject.toml`/`examples/` 신규 도입).
- `docs/` taxonomy의 "불명확 140개" 항목 개별 파일 배치 — Decision 3(아래 §4)에서 후속 ADC 대상으로만 확정한다.
- `docs/03_adc/ADC.md`, `docs/03_adc/README.md`, RFC-0006, ADC-0005 문서 자체의 수정.
- `archive/` 전체.

---

## Decision

### 1. Migration Phase — 단계적으로 3단계 수행

ADC-0005 Decision 1의 권고를 그대로 확정한다.

- **Phase 1**: `core/execution_layer/` → `core/execution/`
- **Phase 2**: `development-hq/` → `hqs/development/`, `investment-hq/` → `hqs/investment/` (동일 Phase — `investment-hq/engine_client.py`가 `development-hq/mvp/engine.py`를 직접 import하는 강결합이 있어 분리 시 한쪽만 이동된 상태에서 import가 깨지므로, ADC-0005 Decision 1 "Repository 영향" 절이 이미 이 둘을 같은 단계로 묶어야 한다고 판단했다.)
- **Phase 3**: `docs/` taxonomy Migration (아래 §2)

Phase 순서의 근거: `core/execution_layer/`는 `ADR-0002` §5에서 이미 독립적으로 판단된 이력이 있고 Development HQ와의 결합도가 낮다(RFC-0006 §7 Impact Analysis: MVP-0006 Dogfooding처럼 `run_pipeline()`을 아예 참조하지 않는 경로도 있음) — 가장 안전하게 먼저 옮길 수 있는 영역이다. 각 Phase 종료 시 RFC-0006 §8 Validation Plan(`pytest --ignore=archive`, `py_compile`, 참조 grep, `git status`)을 전부 수행한 뒤 다음 Phase로 진행한다 — `ADR-0002` §6이 채택한 "한 번에 모두 바꾸지 않고 순서대로 적용하며, 각 단계 후 검증한다" 원칙을 그대로 계승한다.

### 2. docs Taxonomy — 단계적으로 수행, 명확한 16개만 우선

ADC-0005 Decision 2의 권고를 확정한다.

**우선 Migration 대상(명확, 16개 파일)**:

| 현재 | 개수 | Target |
|---|---|---|
| `docs/01_architecture/BASELINE.md` | 1 | `docs/architecture/baseline/` |
| `docs/02_rfc/*` (RFC-0001~0006 + README + RFC_CANDIDATES) | 9 | `docs/decisions/rfc/` |
| `docs/03_adc/*` (ADC.md + README + ADC-0005) | 3 | `docs/decisions/adc/` |
| `docs/04_adr/*` (ADR-0001~0006 + README) | 7 → 실측 시 정확한 개수 재확인 | `docs/decisions/adr/` |

(참고: ADC-0005 작성 시점 집계는 RFC-0006 §6.1 기준 16개였다. 이후 ADC-0005·이 ADR 자체가 `docs/02_rfc/`, `docs/03_adc/`, `docs/04_adr/`에 각각 1개씩 추가되어, Phase 3 실행 시점의 정확한 개수는 실행 직전 재실측한다 — 이 ADR은 "무엇이 명확 대응인가"라는 **기준**만 확정하며, 정확한 파일 목록은 Phase 3 실행 시점에 다시 열거한다.)

**후속 ADC로 이연하는 대상(불명확, ADC-0005 집계 140개)**: `docs/01_mvp/*`(53), `docs/governance/*`(14), `docs/core/execution-layer/*`(27), `docs/research/*`(44), `docs/00_governance/*`(2). 이번 ADR에서 임의로 분류하지 않는다.

**후속 ADC의 Trigger 조건**: Phase 1·2(코드 Migration)가 완료되고 `pytest --ignore=archive`가 전체 통과하는 안정 상태에 도달한 이후에만 후속 ADC를 착수한다. 이는 RFC-0006 §6.2가 지적한 순서 의존성(`docs/01_mvp/*`의 경로를 `development-hq/mvp/*.py`의 docstring이 직접 인용하므로, 코드 쪽 경로가 먼저 안정화되어야 문서 쪽 인용 갱신 대상이 확정된다)을 그대로 따른 것이다. 후속 ADC의 대상: `docs/core/execution-layer/*`(RFC/ADC/ADR과 observation이 혼재되어 `decisions/`·`validation/` 분리 기준이 없는 영역), `docs/research/*`(Target이 요구하는 `ai/architecture/infrastructure` 3분류 기준 부재), `docs/01_mvp/*`·`docs/governance/*`·`docs/00_governance/*`(Target에 대응 위치가 불명확).

### 3. Development HQ 문서 구조 — 현행 유지, 신규/소규모 HQ는 관례로 명문화

ADC-0005 Decision 3의 Option C(혼합)를 확정한다.

- Development HQ의 9개 최상위 문서(`README.md`, `BASELINE.md`, `BOUNDARY.md`, `CONSTITUTION.md`, `HANDOVER.md`, `IMPLEMENTATION_RULES.md`, `MISSION.md`, `MVP.md`, `RESPONSIBILITY.md`, `STRUCTURE.md`)는 이번 Migration(Phase 2)에서 **통합·재작성하지 않는다** — `hqs/development/` 아래로 그대로 이동만 한다.
- `CLAUDE.md`의 "Context Loading" 섹션이 이 9개 파일을 개별 파일명으로 직접 인용하는 구조(예: `development-hq/HANDOVER.md`, `development-hq/IMPLEMENTATION_RULES.md`)는 Phase 2에서 경로 접두사만 `hqs/development/`로 갱신하고, 인용 대상 파일명과 구조는 그대로 유지한다 — 이는 CLAUDE.md 자신의 "전체 문서를 작업마다 일괄 로드하지 않는다"는 Progressive Disclosure 원칙을 지탱하는 구조이므로, 통합은 이 원칙과 직접 충돌한다.
- **공식 관례로 명문화한다**: 신규 HQ(Investment HQ 및 향후 추가될 HQ)는 Target Structure의 "HQ당 README.md 1개" 모델을 기본으로 따른다. Investment HQ가 이미 `README.md` + `STRUCTURE.md` 2개 문서로 이 모델에 가깝게 운영되고 있다는 사실(`investment-hq/STRUCTURE.md` 자체가 Dev HQ의 9-문서 구조를 그대로 답습하지 않기로 한 판단을 기록)이 이 관례의 실증 근거다. 이 관례는 새 RFC/ADC를 요구하지 않는다 — Structure v1.0 PDF의 "Current Implementation Rule"(모든 디렉터리를 즉시 생성하지 않는다, 구현과 Target의 차이는 별도 Migration 계획으로 관리한다)과 동일한 성격의 운영 지침으로 취급한다. 다만 Development HQ처럼 이미 성숙한 다중 문서 구조를 가진 기존 HQ에 소급 적용하지 않는다.

### 4. `archive/v1/` — 이번 Migration에서 제외

ADC-0005 Decision 4를 확정한다. `archive/v1/`은 Phase 1~3 어디에도 포함하지 않는다. 재정리가 필요하다고 판단되면 이번 Migration과 무관한 별도 RFC를 새로 연다 — 최소 조건은 Phase 1·2(Development HQ/Investment HQ Migration)가 완료되고 안정화된 이후로 한다(§2의 후속 ADC Trigger 조건과 동일한 순서 원칙).

---

## ADR-0002 §5와의 관계 (정확한 문구 검토 결과)

`ADR-0002` §5 원문을 다시 확인한 결과, §5는 다음을 결정했다:

> "다음은 여전히 'core'를 포함하지만, 이번 ADR의 범위 밖으로 둔다... **이유**: 1. `core/execution_layer/`는 실제 Python 패키지이며... 경로 변경은 문서 작업이 아니라 코드 변경이며... 2. ADR-0001이 같은 상황에서 동일하게 판단했다... 3. 문서 내용의 용어 통합만으로 ADC-0002 판단 3의 목적은 달성된다."
>
> "**남는 불일치를 정직하게 기록한다**: 이 결정을 유지하면 '문서는 Kernel이라 부르는데 디렉토리는 core/'인 상태가 남는다. 이는 이번 ADR이 만든 절차 부채이며, **별도 ADR로 다룰 후보로 남긴다. 이 ADR은 그 후속 ADR의 시점을 정하지 않는다.**"

이 문구를 정확히 읽으면, §5는 "경로를 바꾸지 않는다"는 영구 결정이 아니라 **"이번 ADR의 범위 밖"이라는 Scope 판단**이며, 스스로 후속 ADR의 존재를 예고하되 그 시점이나 결론을 전혀 구속하지 않았다.

**따라서 이 ADR은 `ADR-0002` §5를 supersede하지 않는다.** Supersede는 기존 결정을 뒤집거나 무효화할 때 쓰는 표현인데, §5에는 뒤집을 "경로를 바꾸지 않는다"는 실체적 결정이 없다 — §5의 실제 결정은 "지금은 범위 밖"이었고, 이 ADR은 바로 그 범위 밖으로 남겨둔 사안을 다루는, §5가 예고한 **후속 ADR 그 자체**다. `RFC-0006` §10이 "ADR-0002 §5는 그 후속 ADR에 의해 대체(supersede)된 것으로 기록되어야 한다"고 쓴 표현은 부정확했다 — 이 ADR은 그 문구를 정정한다: **§5는 대체(supersede)되는 것이 아니라 이행(fulfill)된다.** §5가 기록한 이유("42개 테스트 재검증 필요", "ADR-0001과 동일 판단")는 여전히 유효한 역사적 사실이며, 삭제하거나 덮어쓰지 않는다 — 이 ADR은 다만 §5가 열어둔 다음 단계(경로 변경을 실제로 언제·어떻게 할지)를 확정할 뿐이다. `ADR-0002` 문서 자체는 이 ADR에서 수정하지 않는다.

---

## Consequences

- **BASELINE.md 갱신 시점**: `docs/04_adr/README.md`의 일반 관례는 "ADR 작성 시 결정 내용이 BASELINE.md에 반영된다"이나, 이번 ADR은 사용자 지시("ADR 작성 외 어떤 코드/디렉터리/기존 문서도 수정하지 않는다", "Migration 실행 금지")에 따라 `docs/01_architecture/BASELINE.md`를 이 문서에서 갱신하지 않는다. BASELINE.md 갱신은 Phase 1~3 Migration이 실행되고 RFC-0006 §8 Validation Plan을 통과한 이후, 별도 작업으로 수행한다.
- **일시적 불일치 감수**: Phase 1과 Phase 2 사이, Phase 2와 Phase 3 사이에 저장소가 "일부는 새 경로, 일부는 옛 경로"인 중간 상태를 거친다 — 이는 ADC-0005 Decision 1이 이미 감수하기로 한 트레이드오프다.
- **재검토 조건**: §2의 "명확 16개" 목록은 Phase 3 실행 직전 재실측이 필요하다(RFC-0002~0006, ADC/ADR 문서가 이 세션 동안 계속 늘어나고 있으므로). §3의 신규 HQ 관례는 세 번째 HQ가 생길 때 다시 검토한다.
- **다음 ADC 예고**: §2가 이연한 "불명확 140개" 문서 taxonomy는 Phase 1·2 완료 후 별도 ADC(가칭 "docs taxonomy Phase 2 매핑")를 새로 연다. 이 ADR은 그 ADC의 번호나 시점을 지금 확정하지 않는다.

## 관련 ADC

`docs/03_adc/ADC-0005-structure-v1-migration-decisions.md` — Decision 1, 2, 3, 4 전부 이 ADR로 종결(Resolved)한다. (`ADC-0005` 문서 자체는 이 ADR에서 수정하지 않는다 — 상태 갱신은 `docs/03_adc/ADC.md` 관례와 달리 `docs/03_adc/ADC-0005-*.md`가 독립 파일이므로, 별도 파일 수정 없이 이 ADR이 종결 사실의 기록으로 대신한다.)
