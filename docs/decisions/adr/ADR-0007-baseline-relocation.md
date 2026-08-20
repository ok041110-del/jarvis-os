# ADR-0007: `docs/01_architecture/BASELINE.md` → `docs/architecture/baseline/BASELINE.md` 확정

| 필드 | 내용 |
|---|---|
| ID | ADR-0007 |
| 제목| Architecture Baseline 문서의 Structure v1.0 위치 확정 |
| 상태 | **Accepted** — 위치·Reference 정합성만 확정한다. 이 ADR 자체는 이동을 실행하지 않는다. |
| Context | `docs/decisions/adc/ADC-0006-baseline-relocation-decision.md` |
| 관련 RFC | `docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md` |
| 관련 ADC | `docs/decisions/adc/ADC-0006-baseline-relocation-decision.md` (Option A/B 판단 종결) |
| 선행 ADR | `docs/decisions/adr/ADR-0006-structure-v1-migration.md` §2 (BASELINE.md를 "명확 대응"에 포함시켰으나 실행 지시로 제외됨) |

이 ADR은 ADC-0006이 이미 비교한 Option A/B를 다시 논의하지 않는다.
ADC-0006의 Recommendation(Option A)을 그대로 확정하고, ADC-0006이
스스로 결정하지 않고 남긴 한 가지 — "BASELINE.md 내부 Reference
수정이 Architecture 내용 수정인가, Migration 정합성 유지인가" —
만 이 ADR에서 확정한다.

**이 ADR은 이동을 실행하지 않는다.** ADR 파일 생성만 이번 작업의
범위이며, `docs/01_architecture/BASELINE.md`는 이동·수정하지
않았다(§9 참조).

## Out of Scope (이 ADR이 다루지 않는 것)

- BASELINE.md의 Architecture 내용(Meta Architecture, Concept Model,
  Kernel 정의 등) — §7에서 명시적으로 불변임을 재확인한다.
- Reference Audit(이 세션, 승인됨)이 발견한 나머지 6개 ACTIVE
  참조(`hqs/development/*` 5곳, `core/execution/pipeline.py` 1곳) —
  이 ADR의 범위가 아니다. 별도 판단 대상으로 남긴다.
- `docs/` taxonomy의 나머지 140개 불명확 문서 — 확대하지 않는다.
- `ADR-0006` 본문 수정 — 하지 않는다(§2).

---

## Decision

### 1. Option A 채택

`docs/01_architecture/BASELINE.md`를 `docs/architecture/baseline/BASELINE.md`로
이동하기로 **확정**한다. ADC-0006의 비교(§Architecture/Governance/
Migration/Reference 영향, Structure v1.0 정합성, 장기 유지보수성)를
근거로 삼는다 — 이동 자체의 추가 비용(외부 Active Reference 4곳)이
작고, 코드 의존이 전혀 없어(전수 grep으로 확인됨, ADC-0006 Context
참조) 위험이 낮으며, 내부 Reference 13곳 수정은 Option B를 택해도
어차피 필요한 작업이므로 Structure v1.0 정합성까지 함께 얻는 쪽이
합리적이다.

### 2. ADR-0006과의 관계

**ADR-0006을 수정하지 않는다.** `ADR-0006` §2는 BASELINE.md를 원래
"명확 대응 16(18)개" 목록에 포함시켰으나, Phase 3 실행 지시가
명시적으로 "BASELINE.md 변경 금지"를 요구해 그 항목만 제외하고
나머지 18개만 실행되었다. 이는 `ADR-0006` Consequences가 예정해 둔
"재검토 조건"에 정확히 해당한다.

이 ADR은 `ADR-0006`이 미뤄둔 그 한 항목(BASELINE.md)에 대한 **후속
확정 결정**이다 — `ADR-0006`의 3단계 Migration Phase 구조(Phase
1~3)나 다른 어떤 결정도 뒤집지 않는다. `ADR-0006` 파일 자체(본문,
Consequences, 관련 ADC 절)는 한 글자도 수정하지 않는다. 이후
`docs/decisions/adr/README.md`의 등록 표를 갱신할 때(이 ADR의 실행
범위 밖) "ADR-0006 §2의 BASELINE.md 항목을 ADR-0007이 확정 실행함"으로
기록되어야 한다.

### 3. Migration 범위

승인된 실행 범위는 다음 세 가지로 한정한다(실행은 이 ADR 이후 별도
작업):

1. **`git mv` 1건**: `docs/01_architecture/BASELINE.md` →
   `docs/architecture/baseline/BASELINE.md`. Git history 보존
   (`git log --follow`로 확인).
2. **외부 Active Reference 4곳 갱신**:
   - `README.md` 7행("Architecture 자체에 대한 설명은... `docs/01_architecture/BASELINE.md`가 유일한 Architecture 원본이다")
   - `README.md` 58행("`docs/01_architecture/BASELINE.md` — Jarvis OS 전체 기준")
   - `CLAUDE.md` 55행("Architecture → `docs/01_architecture/BASELINE.md`")
   - `.claude/skills/branch-lifecycle/SKILL.md` 71행("`docs/01_architecture/BASELINE.md`, `hqs/development/BASELINE.md`")
3. **BASELINE.md 내부 Reference 13곳 갱신**(§4 참조): 86, 129, 159,
   211, 339, 367, 412, 548, 779, 780, 798, 805, 816행 — `docs/03_adc/`
   (4곳) → `docs/decisions/adc/`, `docs/04_adr/`(5곳) →
   `docs/decisions/adr/`, `docs/02_rfc/`(1곳) → `docs/decisions/rfc/`,
   `development-hq/BOUNDARY.md`(3곳) → `hqs/development/BOUNDARY.md`.

Reference Audit가 발견한 나머지 6개 파일(`hqs/development/*` 5곳,
`core/execution/pipeline.py` 1곳)은 이 Migration 범위에 **포함하지
않는다** — hqs/·core/ 수정 금지가 이 ADR 실행 시점에도 유효하며,
그 항목들은 별도 판단·별도 실행 대상이다.

### 4. BASELINE 내부 Reference 수정의 성격 확정

ADC-0006이 "별도로 판단할 것"으로 남긴 질문에 답한다:

**BASELINE.md 내부의 13개 경로 인용을 갱신하는 행위는 CLAUDE.md
"Architecture Baseline은 직접 수정하지 않는다"는 Frozen Architecture
원칙이 금지하는 "내용 수정"이 아니다.** 그 원칙이 막는 것은
Architecture의 **결정 내용**(Meta Architecture 정의, Concept Model,
Kernel 경계, System Boundary 등)을 RFC → ADC → ADR 절차 없이 바꾸는
행위다. 반면 13개 인용은 전부 "이 문장의 근거·상세는 `문서 X`를
참조하라"는 **포인터 문자열**이며, 그 문서들이 가리키는 대상(ADC.md,
ADR-0002~0005, RFC-0005, BOUNDARY.md)의 정체성이나 그 문서가 담은
결정은 전혀 바뀌지 않는다 — 오직 그 문서들이 물리적으로 어디로
이동했는지에 대한 문자열만 최신화된다.

이는 정확히 `ADR-0002` §5·§6이 이미 사용한 구분과 같다: "디렉토리
경로·파일명·코드 식별자 변경"은 "문서 내용의 용어 통합"과 별개로
취급되었다. 이 ADR은 그 구분을 인용 경로 수정에도 동일하게
적용한다 — **인용 경로 갱신 = Migration에 따른 Reference Integrity
유지 작업**이며, Architecture 내용 변경이 아니다. 따라서 §3.3의
13곳 수정은 CLAUDE.md의 RFC → ADC → ADR 게이트를 요구하지 않는
Migration 실행 세부사항으로 확정한다(단, 이 ADR 자체가 그 실행을
승인하는 Governance 문서 역할을 한다).

### 5. `docs/01_architecture/` 빈 디렉터리 정리

BASELINE.md 이동 후 `docs/01_architecture/`에는 다른 파일이
없으므로(전수 확인됨 — 이 디렉터리는 BASELINE.md 단독 디렉터리),
`rmdir`로 제거한다. 이는 Phase 3에서 `docs/02_rfc/`, `docs/03_adc/`,
`docs/04_adr/`에 적용한 것과 동일한 절차다.

### 6. pytest 및 Reference Validation 계획

Migration 실행 시(이 ADR 이후 별도 작업) 다음을 검증한다:

1. `git mv` 전후 `git log --follow docs/architecture/baseline/BASELINE.md`로
   history 보존 확인.
2. `python3 -m pytest --ignore=archive -q` — 182건 유지 확인(코드
   의존이 없으므로 결과가 달라지면 안 된다 — 달라지면 이 Migration과
   무관한 회귀이므로 원인을 별도로 규명해야 한다).
3. 전수 grep `docs/01_architecture/BASELINE.md` — historical(문서
   59개, `VALIDATION_REPORT.md`) 잔존은 정상(의도적 보존), 그 외
   ACTIVE 파일에서는 0건이어야 한다.
4. 전수 grep `docs/03_adc/`, `docs/04_adr/`, `docs/02_rfc/`,
   `development-hq/BOUNDARY.md` — BASELINE.md 자신의 13곳이 전부
   `docs/decisions/{adc,adr,rfc}/`, `hqs/development/BOUNDARY.md`로
   갱신됐는지 확인.
5. `git status`로 `hqs/`, `core/`, `archive/`, `projects/`,
   기존 RFC/ADC/ADR, 기존 untracked 산출물(`hqs/investment/dogfooding/{aapl-hq-verify,pg-hq-verify}`)
   무변경 확인.

### 7. BASELINE 내용 자체는 변경하지 않음

Migration 완료 후에도 BASELINE.md의 Architecture 내용 — Meta
Architecture, Concept Model, System Boundary, Kernel 정의·원칙·
Context Model·Public Contract·Logical Reference Architecture, 버전
번호(v1.6), 그 어떤 결정 문장도 — 한 글자도 바뀌지 않는다. §4에서
확정한 13곳은 전부 인용 경로 문자열이며, 그 문자열이 가리키는
문장·표·헤더 구조는 그대로 유지된다.

---

## Consequences

- **후속 실행 필요**: 이 ADR은 결정만 확정했다. §3의 Migration 범위
  실행(BASELINE.md 이동 + 4개 외부 참조 + 13개 내부 참조 + 빈 디렉터리
  제거)은 별도 작업으로 진행한다.
- **남는 BLOCKED 항목**: Reference Audit가 발견한 나머지 6개
  파일(`hqs/development/*` 5곳, `core/execution/pipeline.py` 1곳)은
  이 ADR의 범위 밖으로 남는다 — hqs/·core/ 수정 금지가 유지되는 한
  별도 승인이 필요하다.
- **선례 확정**: §4의 "인용 경로 갱신 ≠ Architecture 내용 변경"
  구분은 이후 유사한 Migration 상황(예: `hqs/development/`,
  `core/execution/` 내부의 깨진 인용을 고칠 때)에도 재사용 가능한
  선례로 남는다 — 다만 그 적용은 각 상황에서 별도로 재확인한다(이
  ADR이 자동으로 다른 파일까지 승인하지 않는다).

## 관련 ADC

`docs/decisions/adc/ADC-0006-baseline-relocation-decision.md` — Option
A/B 판단과 "내부 Reference 수정의 성격" 질문 전부 이 ADR로
종결(Resolved)한다.
