# ADR-0002: Core → Kernel 용어 통합 및 Kernel 정의의 Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | ADR-0002 |
| 제목 | Core → Kernel 용어 통합과 Kernel 정의·Design Principles를 Architecture Baseline에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| 승인 경로 | Kernel Consistency Review 7개 항목 통과(Major 0건, Minor 3건 — 2건 수정 완료, 1건은 KP-4·Architecture 명칭 변경으로 반영) 후 승인 |
| Context | `docs/architecture/core/ADC-0002-kernel-definition.md` 판단 1(KP 채택, Accept), 판단 3(용어 통합, Accept), 판단 4(Baseline Proposal, Accept·범위 한정) |
| 관련 RFC | `docs/architecture/core/RFC-0002-kernel-definition.md` |
| 관련 ADC | `docs/architecture/core/ADC-0002-kernel-definition.md` |

이 ADR은 ADC-0002가 이미 내린 결정을 다시 논의하지 않는다. 새로운
철학이나 Architecture를 제안하지 않는다. ADC-0002의 판단 1·3·4를 실제
문서 변경으로 옮기기 위한 **구현 결정**만 기록한다.

이 ADR은 **승인되었다.** §6 Migration Strategy에 정의된 변경은 이
승인에 따라 실행된다.

## Out of Scope (이 ADR이 다루지 않는 것)

- 4-Layer Context Model — ADC-0002 판단 2b에서 **Defer**되었다.
  Baseline에 반영하지 않는다.
- Kernel Architecture 및 Component Design(Scheduler, Engine Gateway,
  Registry, Communication, Memory, Policy 등) — `BASELINE.md` §10 Out
  of Scope에 **그대로 유지**한다(ADC-0002 판단 4가 명시한 한정).
- RFC-0002 §14 Roadmap — 순서 제안이며 확정 계획이 아니다. Baseline에
  반영하지 않는다.
- Development HQ의 어떤 문서·코드 — Phase 1 완료 후 수정하지 않는다
  (§1이 이 제약을 실제로 만족함을 확인한다).
- 디렉토리 경로·파일명·코드 식별자 변경 — §5에서 별도 Phase로
  분리한다.

---

## Decision

### 1. 용어 통합 범위 — 무엇을 바꾸고 무엇을 바꾸지 않는가

저장소 전체에서 "Core" 사용처를 조사한 결과, 세 범주로 나뉜다. **이
중 A만 변경한다.**

#### Category A — "Core"가 Kernel 개념을 가리키는 경우 (변경 대상)

| 파일 | 출현 수 | 비고 |
|---|---|---|
| `docs/architecture/core/RFC-0001-jarvis-os-core-baseline.md` | 36 | Jarvis OS Core Baseline — 전면 |
| `docs/architecture/core/ADC-0001-core-baseline.md` | 17 | Core Module 판단 — 전면 |
| `docs/core/execution-layer/MVP-0001-plan.md` | 7 | "Core에서 Accept된 Module" 등 |
| `docs/core/execution-layer/MVP-0001-observation.md` | 1 | "Core RFC-0001, Core ADC-0001" 문서 참조 |
| `docs/core/execution-layer/MVP-0002-observation.md` | 1 | 동일 |

여기에 더해, 아직 커밋되지 않은 다음 문서도 동일 규칙을 적용한다:
`docs/architecture/core/RFC-0002-kernel-definition.md`,
`docs/architecture/core/ADC-0002-kernel-definition.md`,
`docs/architecture/core/GOVERNANCE-REVIEW-0001-post-adc-0001.md`,
`docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md`,
`docs/core/execution-layer/ADC-0001-artifact-drift-boundary.md`,
`docs/core/execution-layer/ARTIFACT-STANDARD-v1.md`.

**치환 규칙**: "Core" → "Kernel", "Core Module" → "Kernel Module",
"Core Baseline" → "Kernel Baseline", "Core Artifact Standard" →
"Kernel Artifact Standard". 문서 제목(`# ...`)도 동일하게 바꾼다.

**과거 기록(Observation/Plan/ADC) 수정에 대한 근거**: Category A에는
이미 커밋된 Observation·Plan·ADC 문서가 포함된다(`MVP-0001-plan.md`,
`MVP-0001-observation.md`, `MVP-0002-observation.md`,
`ADC-0001-core-baseline.md`). 이는 §1 Category C에서 "과거 기록을
소급 수정하지 않는다"고 한 것과 충돌하는 것처럼 보이므로, 구분 근거를
명시한다.

- 이 문서들의 "Core" 출현을 전수 확인한 결과, **관찰된 사실을 서술한
  문장은 하나도 없다** — 전부 (a) 문서명 참조("Core RFC-0001, Core
  ADC-0001 문서 — 모두 수정하지 않았다"), (b) 개념 참조("Core에서
  Accept된 Module은…", "Core Module 책임은…")다.
- 따라서 이 치환은 **관찰 내용을 바꾸지 않고 참조 대상의 이름만
  갱신**한다. 오히려 치환하지 않으면 대상 문서가 Kernel로 개명된 뒤
  참조가 해소되지 않아 기록의 정확성이 떨어진다.
- 반면 `archive/v1/**`은 superseded된 이전 버전의 문서 집합으로,
  현재 문서와 상호 참조 관계가 없다. 갱신할 참조가 없으므로 그대로
  둔다.
- **판별 기준**: 치환 전 각 출현을 확인해, 관찰 사실을 서술하는
  문장 안의 "Core"가 발견되면 그 건은 치환 대상에서 제외하고 이
  ADR에 예외로 기록한다.

#### Category B — "Core"가 Kernel과 무관한 일반 용어 (변경하지 않음)

| 파일 | 출현 | 이유 |
|---|---|---|
| `docs/01_architecture/BASELINE.md` §3 | "Core Principles" | "핵심 원칙"이라는 뜻이며 Kernel과 무관하다. |
| `development-hq/CONSTITUTION.md` | "Core Philosophy" | 동일. |
| `development-hq/HANDOVER.md` | "Core Principles" ×2 | 동일. |
| `docs/03_adc/ADC.md` ADC-02 | "Core Component 검토" | 과거에 실제로 수행된 **검토 단계의 고유 명칭**이다. 역사적 사건 이름이므로 바꾸면 기록이 훼손된다. |
| `docs/02_rfc/RFC-0004-...md`, `docs/02_rfc/README.md`, `development-hq/HANDOVER.md` | "Core Component 검토" | 위 명칭의 인용. 동일 이유로 유지. |

**중요 확인**: `development-hq/` 이하의 "Core" 출현은 **전부 Category
B**다. 따라서 이번 용어 통합은 Frozen 상태인 Development HQ 문서를
**한 글자도 수정하지 않는다** — Development HQ Phase 1 종료 후
"더 이상 수정하지 않는다"는 제약과 충돌하지 않는다.

#### Category C — `archive/v1/**` (변경하지 않음)

아카이브된 v1 문서(약 25개 파일)는 그 시점의 기록이므로 변경하지
않는다. 과거 기록을 소급 수정하지 않는다는 이 프로젝트의 원칙을
따른다.

### 2. Architecture Baseline 문서 변경 방법

변경 대상은 `docs/01_architecture/BASELINE.md` 하나다.

#### 2.1 절 번호 정책 — 기존 §1~§10을 건드리지 않는다

`BASELINE.md`의 절 번호는 다른 문서에서 다수 인용되고 있다(조사
결과: §3 4건, §5 1건, §6 6건, §7 7건, §10 4건, §11 1건). 기존 절을
재번호하면 이 인용들이 전부 깨진다.

따라서 다음 방식을 채택한다.

- **§1~§10은 번호와 내용을 그대로 둔다.** (단 §3 "Core Principles"
  제목도 §1 Category B에 따라 유지한다.)
- 새 절 **§11 Kernel**, **§12 Kernel Design Principles**를 §10 뒤에
  삽입한다.
- 기존 §11 Version → **§13 Version**으로 이동한다(문서 관례상 Version은
  마지막에 둔다).

**이 방식의 비용**: 깨지는 외부 인용은 "§11 Version" 1건뿐이며, 그
1건은 아직 커밋되지 않은 `ADC-0002-kernel-definition.md` 내부 참조이므로
같은 작업에서 함께 수정된다. §6·§7·§10 등 다수 인용은 전부 그대로
유효하다.

**검토했으나 채택하지 않은 대안**: Kernel 절을 §8에 삽입하고 이후를
재번호하는 방식 — §10 Out of Scope(4건), §11 Version(1건) 총 5건의
인용을 수정해야 하고 그중 3건이 이미 커밋된 문서다. 얻는 것은 문서
내 배치의 자연스러움뿐이므로 비용이 크다고 판단했다.

#### 2.2 §11 Kernel (신설) — 반영할 내용

RFC-0002 §8·§9·§10의 내용만 옮긴다. 새 문장을 만들지 않는다.

- Kernel은 Component가 아니다. Framework가 아니다. Runtime/Scheduler/
  Registry/Event Bus가 아니다.
- Kernel은 **모든 HQ가 공통으로 필요로 하지만 어느 HQ에도 속하지 않는
  책임(Common Responsibility)을 담당하는 계층**이다.
- Kernel은 책임을 가지고, Component는 그 책임을 구현하는 방법이다.
  (RFC-0002 §9의 대응표를 **"예시이며 채택 여부는 미결"**이라는 단서와
  함께 그대로 옮긴다.)
- Kernel은 구현으로 정의하지 않고 책임으로 정의한다.
- **Kernel Architecture와 Component Design은 여전히 §10 Out of
  Scope다**라는 문장을 명시적으로 포함한다 — 정의를 추가하는 것이
  설계를 허용하는 것으로 오해되지 않도록 한다.

#### 2.3 §12 Kernel Design Principles (신설) — 반영할 내용

ADC-0002 판단 1에서 Accept된 KP-1~KP-6을 그대로 옮긴다.

| ID | 원칙 |
|---|---|
| KP-1 | Responsibility over Component |
| KP-2 | Deterministic Context Assembly |
| KP-3 | Stable Context Ordering |
| KP-4 | Stable Context by Design |
| KP-5 | Implementation Agnostic |
| KP-6 | Stateless Responsibility Boundary |

각 원칙의 본문은 RFC-0002 §11의 진술을 그대로 사용한다. RFC-0002가
각 원칙에 붙인 *근거(기존 사실)* / *성격(신규)* 표시는 Baseline에
옮기지 않는다 — Baseline은 결정을 기록하는 문서이고, 그 결정에 이르게
한 근거는 RFC-0002와 ADC-0002에 남는다. 대신 §12 서두에 근거 문서
포인터(RFC-0002 §11, ADC-0002 판단 1)를 명시한다.

§12에는 "이 원칙들은 Development HQ, Runtime, Memory, Agent 등 모든
하위 설계가 공통으로 참조하는 최상위 설계 원칙이다"라는 적용 범위
문장을 포함한다.

#### 2.4 §13 Version 갱신

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.0 | **v1.1** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen을 유지하는 이유**: `ARCHITECTURE_GOVERNANCE.md`의 Freeze
원칙은 "변경 불가"가 아니라 "절차를 거치지 않은 변경이 반영되지
않는 상태"를 뜻한다. 이번 변경은 RFC-0002 → ADC-0002 → ADR-0002
절차를 그대로 거쳤으므로 Freeze를 위반하지 않는다. ADR-0001이 Frozen
상태의 Development HQ Baseline을 같은 방식으로 갱신한 선례가 있다.

버전 이력을 추적할 수 있도록 §13에 다음 한 줄을 추가한다:
`v1.1 — Kernel 정의(§11)와 Kernel Design Principles(§12) 추가. 근거:
ADR-0002.`

### 3. Glossary 갱신

`docs/00_governance/GLOSSARY.md`에 다음 항목을 추가한다.

| 용어 | 정의 |
|---|---|
| Kernel | 모든 HQ가 공통으로 필요로 하지만 어느 HQ에도 속하지 않는 책임을 담당하는 계층. Component가 아니라 책임 경계다. *(정의: BASELINE.md §11)* |

그리고 **"Core는 Kernel의 이전 명칭이며, 문서에서 Kernel과 동일한
것을 가리킨다"**는 한 줄을 함께 남긴다 — 과거 커밋 이력이나
`archive/v1/`을 읽는 사람이 두 용어를 연결할 수 있어야 하기 때문이다.

### 4. `docs/03_adc/ADC.md` 갱신 여부

**갱신하지 않는다.** ADC.md는 Jarvis OS 수준 Open Decision의 Single
Source of Truth이며, 이번 ADR은 새 Open Decision을 만들지 않는다
(KP 채택·용어 통합·Kernel 정의는 모두 **결정**이지 미결 사항이 아니다).
ADC-02(Runtime 개념의 존폐) 등 기존 12개 항목의 상태도 이번 변경으로
바뀌지 않는다.

### 5. 경로·파일명·코드 식별자 — 이번 ADR에서 변경하지 않음

다음은 여전히 "core"를 포함하지만, 이번 ADR의 범위 밖으로 둔다.

- 디렉토리: `core/execution_layer/`, `docs/architecture/core/`,
  `docs/core/execution-layer/`
- 파일명: `RFC-0001-jarvis-os-core-baseline.md`,
  `ADC-0001-core-baseline.md`

**이유**:

1. `core/execution_layer/`는 실제 Python 패키지이며, 5개 테스트 파일과
   5개 dogfooding 스크립트가 `sys.path` 조작과 `execution_layer.*`
   import로 이 경로에 의존한다. 경로 변경은 문서 작업이 아니라 **코드
   변경**이며, 42개 테스트 전부를 재검증해야 한다.
2. ADR-0001이 같은 상황에서 동일하게 판단했다 — "코드 디렉토리
   (`development-hq/mvp/`)는 변경하지 않는다... 기존 코드는 이동하거나
   수정하지 않는다."
3. 문서 내용의 용어 통합만으로 ADC-0002 판단 3의 목적(같은 개념이 두
   이름으로 추적되는 상태의 해소)은 달성된다.

**남는 불일치를 정직하게 기록한다**: 이 결정을 유지하면 "문서는
Kernel이라 부르는데 디렉토리는 `core/`"인 상태가 남는다. 이는 이번
ADR이 만든 절차 부채이며, 별도 ADR로 다룰 후보로 남긴다. 이 ADR은 그
후속 ADR의 시점을 정하지 않는다.

### 6. Migration Strategy

한 번에 모두 바꾸지 않고 순서대로 적용하며, 각 단계 후 검증한다.

1. **BASELINE.md 갱신** — §11 Kernel, §12 Kernel Design Principles
   삽입, §11 Version → §13으로 이동 및 v1.1 갱신(§2).
2. **Baseline 절 번호 인용 1건 수정** —
   `ADC-0002-kernel-definition.md`의 "§11: Architecture State" 참조를
   "§13"으로 수정(§2.1).
3. **GLOSSARY.md에 Kernel 항목 추가**(§3).
4. **Category A 문서 용어 치환**(§1) — 커밋된 5개 파일과 미커밋 6개
   파일. 치환 후 각 문서를 읽어 문맥상 어색한 곳(예: 인용문 안의
   "Core")이 없는지 확인한다.
5. **검증**:
   - `git ls-files '*.md' | grep -v '^archive/' | xargs grep -n "Core"`
     결과가 Category B 항목만 남는지 확인한다.
   - `python3 -m pytest development-hq/mvp/tests/ core/execution_layer/*/tests/ -q`
     42건이 그대로 통과하는지 확인한다(이번 변경은 코드를 건드리지
     않으므로 결과가 달라지면 안 된다).
   - `development-hq/` 이하에 변경이 없는지 `git status`로 확인한다.
6. **커밋** — RFC-0002, ADC-0002, ADR-0002와 위 변경, 그리고 그동안
   보류해 온 Research/Execution Layer 문서를 함께 커밋한다(사용자가
   "RFC, ADC, ADR이 모두 검토 완료된 이후 한 번에 커밋"으로 정한
   시점).

---

## Consequences

- `docs/01_architecture/BASELINE.md`가 v1.0 → v1.1이 되고, Kernel의
  정의와 KP-1~KP-6이 Architecture Baseline의 일부가 된다. 이후 모든
  하위 설계(Development HQ, Runtime, Memory, Agent 등)는 이 원칙을
  참조 기준으로 삼는다.
- "Kernel"이 공식 용어가 되고, 활성 문서에서 Kernel 개념을 가리키는
  "Core"는 사라진다. Category B(일반 용어로서의 "Core")와
  `archive/v1/`은 그대로 남으며, GLOSSARY의 연결 문장이 두 용어를
  잇는다.
- **Development HQ는 한 글자도 변경되지 않는다**(§1 Category B 확인).
- **Kernel Architecture는 여전히 설계되지 않는다** — `BASELINE.md`
  §10 Out of Scope가 그대로 유지되고, §11이 그 사실을 명시적으로
  다시 기록한다.
- 4-Layer Context Model은 Baseline에 들어가지 않는다(ADC-0002 판단
  2b, Defer). RFC-0002 §12.2에 후보로 남아 Kernel Context Model RFC의
  출발점이 된다.
- 남는 절차 부채 2건을 기록한다.
  1. 디렉토리·파일명의 `core/`는 그대로 남는다(§5).
  2. `GOVERNANCE-REVIEW-0001-post-adc-0001.md` §1이 이미 지적한,
     Kernel ADC-0001의 미작성 ADR 2건(Governance Module, Execution Layer
     Module)은 이 ADR이 해소하지 않는다. 이 ADR은 ADC-0002의 판단만
     다룬다.
- 이 ADR은 **승인되었으며**, §6에 정의된 실제 파일 변경이 이 승인에
  따라 실행된다.
