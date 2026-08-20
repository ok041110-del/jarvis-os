# ADC-0006: `docs/01_architecture/BASELINE.md` 재배치 여부

## 목적

Migration 후 Reference Audit(이 세션, 승인됨)이 발견한 항목 하나만
판단한다: `docs/01_architecture/BASELINE.md`를 Structure v1.0 Target
(`docs/architecture/baseline/BASELINE.md`)으로 옮길지, 현재 위치에
유지할지. 근거는 `docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md`,
`docs/decisions/adr/ADR-0006-structure-v1-migration.md`, 그리고 이
세션에서 수행한 Reference Audit(승인됨)으로 한정한다. 새 실험을
하지 않았다.

## 이 ADC가 다루지 않는 것

- BASELINE.md의 실제 Architecture 내용(Meta Architecture, Concept
  Model, Kernel 정의 등) — 이번 판단은 **위치**에 대한 것이지 **내용**에
  대한 것이 아니다. 어느 Option을 택하든 BASELINE.md의 문장 하나도
  바뀌지 않는다(단, §5에서 다루는 "내부 인용 경로 13건"은 예외 — 이는
  Architecture 판단이 아니라 Migration 정합성 문제로 별도 취급한다).
- `docs/` taxonomy의 나머지 140개 불명확 문서(Phase 3 §2에서 이미
  이연) — 이번 ADC는 확대하지 않는다.
- `hqs/`, `core/`의 나머지 ACTIVE 참조(Reference Audit §2의 7개 파일
  중 BASELINE.md 자신을 제외한 6개) — 별도 판단 대상으로 남긴다.

## Context — 현재 문제 (Reference Audit 인용)

- `docs/01_architecture/BASELINE.md`는 Phase 3에서 "명확 대응"
  목록에 포함되어 있었으나(`ADR-0006` §2), "BASELINE.md 변경 금지"
  지시로 이동하지 않고 BLOCKED 상태로 남았다.
- BASELINE.md 자신이 이미 이동한 `docs/02_rfc/`, `docs/03_adc/`,
  `docs/04_adr/`, 그리고 `development-hq/BOUNDARY.md`를 인용하는
  **13곳**이 깨져 있다(86, 129, 159, 211, 339, 367, 412, 548, 779,
  780, 798, 805, 816행).
- BASELINE.md를 가리키는 외부 ACTIVE 참조는 4곳뿐이다: `README.md`
  2곳(7행, 58행), `CLAUDE.md` 1곳(55행), `.claude/skills/branch-lifecycle/SKILL.md`
  1곳(71행). 나머지는 `docs/`(59개, 대부분 historical), `hqs/`(3개,
  이미 BLOCKED), `VALIDATION_REPORT.md`(Historical Snapshot 자체
  선언, 수정 대상 아님)에 분산되어 있다.
- 코드(`.py`) 어디에도 `docs/01_architecture` 경로에 대한 하드코딩
  의존이 없다(전수 grep 확인) — 이동이 code import를 깨뜨릴 위험은
  없다.

## Option A — `docs/architecture/baseline/BASELINE.md`로 이동

### Architecture 영향
없음. 내용 무변경. BASELINE.md가 여전히 Jarvis OS Architecture의
유일한 원본이라는 지위(Single Source of Truth)도 그대로 유지된다 —
위치만 바뀐다.

### Governance 영향
Structure v1.0의 "명확 대응" 목록을 완결한다(ADR-0006 §2가 원래
포함했던 항목). `docs/03_adc/ADC.md`가 명시한 "Baseline 갱신은 RFC →
ADC → ADR 경로로만" 원칙과 충돌하지 않는다 — 이 ADC는 내용을
갱신하지 않고 위치만 다룬다. 단, BASELINE.md 자신의 13개 내부 인용을
같이 고치지 않으면 "위치는 맞았지만 내용은 여전히 깨진" 상태가
남는다(§5에서 별도 다룸).

### Migration 영향
`git mv` 1건, Git history 보존. 코드 의존 없음(위 Context 확인)이므로
`pytest`/`py_compile`에 영향 없음. 외부 ACTIVE 참조 4곳(README.md 2,
CLAUDE.md 1, branch-lifecycle SKILL.md 1) 갱신 필요 — Phase 2/3에서
이미 반복된 작은 규모의 작업과 동일한 패턴.

### Reference 영향
- 외부: 4곳(작음, 이미 파악됨).
- 내부(BASELINE.md 자신의 13개 인용): 이동과 별개로 존재하는 문제이지만,
  이동을 승인하는 김에 같이 고치지 않으면 "옮겨진 채로 계속 깨져 있는"
  BASELINE.md가 된다. 이동 후에도 §5 승인 없이는 내용을 고칠 수 없다는
  점에 유의.

### Structure v1.0 정합성
완전 일치.

### 장기 유지보수성
Target과의 불일치가 영구히 남지 않는다. 향후 `docs/architecture/`
전체가 정리될 때(불명확 140개 중 `docs/architecture/core/`,
`docs/core/execution-layer/` 등) BASELINE.md가 이미 올바른 위치에
있어 재작업이 없다.

## Option B — 현재 위치 유지, 내부 인용 13건만 최소 수정

### Architecture 영향
없음. 내용은 인용 경로 13건만 바뀐다(§5와 동일한 쟁점).

### Governance 영향
Structure v1.0과의 불일치가 남지만, `ADR-0006` Consequences가 이미
"Target Boundary로만 유지되는 항목이 있을 수 있다"고 전제했다 — 이
불일치는 감수 가능한 절차 부채로 명시적으로 기록 가능하다(ADR-0002
§5가 `core/execution_layer/` 미이동 결정에 쓴 것과 같은 표현).

### Migration 영향
가장 작다 — 디렉터리 이동 없음, 외부 ACTIVE 참조 4곳 전부 이미
올바른 경로를 가리키고 있어 손댈 필요가 없다.

### Reference 영향
- 외부: 0곳(이미 정확함).
- 내부: 13곳 수정 필요(Option A와 동일한 작업량 — 위치와 무관하게
  발생하는 작업).

### Structure v1.0 정합성
부분 불일치 — `docs/01_architecture/`가 Target에 없는 디렉터리로
영구히(또는 다음 재검토까지) 남는다.

### 장기 유지보수성
지금 당장은 더 간단하지만, `docs/architecture/`가 다른 이유로
정리될 때(Kernel RFC/ADC/ADR 재배치 등) BASELINE.md만 별도로 다시
옮겨야 할 가능성이 남는다 — 작업이 나뉘어 두 번 발생할 수 있다.

## 비교 요약

| 기준 | Option A(이동) | Option B(유지) |
|---|---|---|
| Architecture 영향 | 없음 | 없음 |
| Governance 영향 | 목록 완결 | 불일치 기록으로 남김(감수 가능) |
| Migration 영향 | `git mv` 1건 + 외부 4곳 | 없음 |
| Reference 영향(외부) | 4곳 | 0곳 |
| Reference 영향(내부, 공통) | 13곳 | 13곳 |
| Structure v1.0 정합성 | 완전 일치 | 부분 불일치 |
| 장기 유지보수성 | 재작업 없음 | 추후 재이동 가능성 |

내부 인용 13건 수정은 **두 Option 모두에서 동일하게 필요**하다 —
Option 선택이 좌우하는 것은 오직 "외부 참조 4곳을 갱신하느냐"와
"Structure v1.0과의 정합성"뿐이다.

## Recommendation

**Option A(이동)를 권고한다.** 이동 자체의 추가 비용(외부 참조 4곳)이
작고, 코드 의존이 전혀 없어 위험이 낮으며, RFC-0006/ADR-0006이 이미
이 이동을 "명확 대응"으로 판단해 둔 상태다. 내부 인용 13건 수정은
Option B를 택해도 어차피 필요한 작업이므로, 그 비용을 감수하는 김에
Structure v1.0 정합성까지 함께 얻는 Option A가 더 효율적이다.

## 별도로 판단할 것 — 내부 인용 13건 수정의 성격

Option A/B 어느 쪽을 택하든, BASELINE.md 자신의 13개 인용 경로를
고치는 행위가 CLAUDE.md의 "Architecture Baseline은 직접 수정하지
않는다"는 Frozen Architecture 원칙에 저촉되는 "내용 수정"인지,
아니면 Migration에 따르는 순수 경로 정합성 유지(문장·결정·구조는
그대로, 인용 문자열만 최신화)인지를 이 ADC는 스스로 결정하지 않는다.
후속 ADR이 이 구분을 명시적으로 확정해야 한다 — 그래야 "BASELINE.md
수정 금지" 원칙과 "Migration으로 인한 참조 정합성 유지" 사이의
경계가 향후 세션에서도 반복적으로 재해석되지 않는다.

## 별도 ADC로 충분한가

**충분하다.** 이 결정은 RFC-0006이 이미 스코프한 Migration
위치(§6.1 매핑 표)의 재확인일 뿐, 새로운 Architecture Concept이나
Kernel Boundary 질문을 제기하지 않는다. ADC-0005가 다룬 4개
Decision과 동일한 성격(Migration 순서·범위 판단)이다.

## RFC가 필요한 Architecture 변경인가

**아니다.** BASELINE.md의 Architecture 내용, Meta Architecture,
Concept Model, Kernel 정의 어느 것도 바뀌지 않는다. RFC-0006이 이미
이 이동을 다뤘으므로 새 RFC를 열 필요가 없다.

## 기존 ADR-0006과의 관계

충돌하지 않는다. `ADR-0006` §2는 BASELINE.md를 "명확 16(18)개"에
원래 포함시켰으나, 실행 지시(Phase 3 turn)가 "BASELINE.md 변경
금지"를 명시적으로 요구해 그 항목만 제외하고 나머지 18개를
실행했다 — `ADR-0006` Consequences가 "재검토 조건"을 예정해 둔 바로
그 지점이다. 이 ADC는 ADR-0006을 뒤집지 않고, ADR-0006이 미뤄둔
마지막 한 항목(BASELINE.md)에 대한 판단을 마무리한다. 승인되면
후속 ADR이 "ADR-0006 §2의 BASELINE.md 항목을 이 ADR이 확정 실행한다"고
기록해야 한다 — ADR-0006 자체를 수정하지 않는다.

## BASELINE 이동 시 필요한 Validation (Option A 채택 시)

1. `git mv docs/01_architecture/BASELINE.md docs/architecture/baseline/BASELINE.md`
   — Git history 보존 확인(`git log --follow`).
2. 외부 ACTIVE 참조 4곳 갱신: `README.md`(7행, 58행), `CLAUDE.md`(55행),
   `.claude/skills/branch-lifecycle/SKILL.md`(71행).
3. BASELINE.md 내부 인용 13곳 갱신 — 이 ADC가 §5에서 표시한 대로
   후속 ADR의 명시적 승인 필요.
4. `docs/01_architecture/` 빈 디렉터리 제거.
5. `python3 -m pytest --ignore=archive -q` — 182건 유지 확인(코드
   의존이 없으므로 영향 없어야 함).
6. 전수 grep으로 `docs/01_architecture/BASELINE.md` 잔존 여부
   재확인 — historical(59개 docs, `VALIDATION_REPORT.md`)은 의도적
   보존이므로 남아 있어야 정상.
7. `hqs/development/{BASELINE.md,BOUNDARY.md,HANDOVER.md}` 등이
   가리키는 `docs/03_adc/`, `docs/04_adr/`, `docs/02_rfc/` 참조(Reference
   Audit §2의 나머지 6개 파일)는 이 ADC의 범위가 아니다 — 별도 승인
   필요.
