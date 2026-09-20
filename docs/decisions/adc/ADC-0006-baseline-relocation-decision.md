# ADC-0006 — `docs/01_architecture/BASELINE.md` 재배치 여부

## 1. Identity & Status

| Field | Value |
|---|---|
| ID | ADC-0006 |
| Status | Resolved (Accept — Option A) |
| Owner / Scope | BASELINE.md의 **위치**(내용 아님) |
| Context | Migration 후 Reference Audit(승인됨)이 발견한 항목 — `docs/01_architecture/BASELINE.md`를 Structure v1.0 Target(`docs/architecture/baseline/BASELINE.md`)으로 옮길지, 현재 위치에 유지할지 |

## 2. Decision Scope & Context

| Item | Description |
|---|---|
| Decision Scope | BASELINE.md 파일 위치 결정. 내부 인용 경로 13건 수정은 위치와 무관하게 두 Option 모두에서 동일하게 필요하므로 별도 취급 |
| Context | `docs/01_architecture/BASELINE.md`는 Phase 3 "명확 대응" 목록에 포함됐으나(ADR-0006 §2) "BASELINE.md 변경 금지" 지시로 BLOCKED 상태로 남았다. BASELINE.md 자신이 이미 이동한 `docs/02_rfc/`·`docs/03_adc/`·`docs/04_adr/`·`development-hq/BOUNDARY.md`를 인용하는 13곳(86/129/159/211/339/367/412/548/779/780/798/805/816행)이 깨져 있다. 외부 ACTIVE 참조는 4곳뿐(README.md 2, CLAUDE.md 1, branch-lifecycle SKILL.md 1). 코드(`.py`)에 이 경로 하드코딩 의존 없음(전수 grep 확인) |
| Constraints | BASELINE.md의 실제 Architecture 내용(Meta Architecture/Concept Model/Kernel 정의)은 이 판단 대상이 아니다 |
| Non-Goals | `docs/` taxonomy 나머지 140개 불명확 문서(Phase 3에서 이미 이연), `hqs/`/`core/`의 나머지 ACTIVE 참조 6개(Reference Audit §2) — 별도 판단 대상 |

## 3. Candidates / Options

| ID | Candidate | Description | Evidence | Advantages | Risks / Trade-offs |
|---|---|---|---|---|---|
| A | `docs/architecture/baseline/BASELINE.md`로 이동 | `git mv` 1건 + 외부 참조 4곳 갱신 | 코드 의존 없음(전수 grep), RFC-0006/ADR-0006이 이미 "명확 대응"으로 판단 | Structure v1.0 완전 일치, 향후 재작업 없음, Architecture 영향 없음(내용 무변경) | 외부 참조 4곳 갱신 필요(작은 규모) |
| B | 현재 위치 유지, 내부 인용 13건만 최소 수정 | 디렉터리 이동 없음 | ADR-0006 Consequences가 "Target Boundary로만 유지되는 항목이 있을 수 있다"고 이미 전제 | Migration 영향 최소(외부 참조 갱신 불필요) | Structure v1.0과 부분 불일치가 영구히(또는 재검토까지) 남음, 향후 재이동 가능성 |

## 4. Evaluation

| Criterion | Weight / Priority | A | B | Notes |
|---|---|---|---|---|
| Architecture 영향 | — | 없음 | 없음 | 동일 |
| Governance 영향 | 높음 | 목록 완결 | 불일치 기록으로 남김(감수 가능) | |
| Migration 영향 | 중간 | `git mv` 1건 + 외부 4곳 | 없음 | |
| Reference 영향(외부) | 낮음 | 4곳 | 0곳 | |
| Reference 영향(내부, 공통) | — | 13곳 | 13곳 | Option 무관 동일 작업 |
| Structure v1.0 정합성 | 높음 | 완전 일치 | 부분 불일치 | |
| 장기 유지보수성 | 중간 | 재작업 없음 | 추후 재이동 가능성 | |

## 5. Recommendation & Decision Boundary

| Item | Description |
|---|---|
| Recommendation | Option A(이동) — 추가 비용(외부 참조 4곳)이 작고 코드 의존이 없어 위험이 낮으며, RFC-0006/ADR-0006이 이미 이 이동을 "명확 대응"으로 판단해 둔 상태. 내부 인용 13건 수정은 B를 택해도 어차피 필요하므로, 그 비용을 감수하는 김에 Structure v1.0 정합성까지 함께 얻는 A가 더 효율적 |
| Decision Boundary | 이 ADC는 위치만 판단한다 — 내부 인용 13건 수정이 CLAUDE.md "Architecture Baseline 직접 수정 금지" 원칙에 저촉되는 "내용 수정"인지, Migration에 따르는 순수 경로 정합성 유지인지는 이 ADC가 결정하지 않는다. 후속 ADR이 이 구분을 명시적으로 확정해야 한다 |
| Out of Authority | BASELINE.md 내용 자체의 Architecture 판단 |
| ADR Requirement | 필요 — 후속 ADR이 "ADR-0006 §2의 BASELINE.md 항목을 이 ADR이 확정 실행한다"고 기록해야 한다(ADR-0006 자체는 수정하지 않음). 후속 ADR이 내부 인용 13곳 수정의 성격도 함께 확정한다 |
| Re-evaluation Trigger | 없음(단회성 위치 판단) |

## 6. Open Questions

| ID | Question | Required Evidence | Owner |
|---|---|---|---|
| Q-1 | 내부 인용 13건 수정이 "내용 수정"인지 "경로 정합성 유지"인지 | Frozen Architecture 원칙과의 관계 판단 | 후속 ADR |

## Decision

**Option A 채택.** 별도 ADC로 충분하다 — RFC-0006이 이미 스코프한 Migration 위치(§6.1 매핑 표)의 재확인일 뿐, 새로운 Architecture Concept이나 Kernel Boundary 질문을 제기하지 않는다(ADC-0005가 다룬 4개 Decision과 동일 성격). RFC는 불필요하다 — BASELINE.md의 Architecture 내용/Meta Architecture/Concept Model/Kernel 정의 어느 것도 바뀌지 않으며, RFC-0006이 이미 이 이동을 다뤘다.

**기존 ADR-0006과의 관계**: 충돌하지 않는다. ADR-0006 §2는 BASELINE.md를 "명확 16(18)개"에 포함시켰으나 실행 지시가 "BASELINE.md 변경 금지"를 요구해 그 항목만 제외했다 — ADR-0006 Consequences가 예정해 둔 "재검토 조건"이 바로 이 지점이다. 이 ADC는 ADR-0006을 뒤집지 않고, 미뤄둔 마지막 한 항목(BASELINE.md)의 판단을 마무리한다.

**이동 시 필요 Validation**: `git mv` + Git history 보존 확인 → 외부 ACTIVE 참조 4곳 갱신 → 내부 인용 13곳은 후속 ADR의 명시적 승인 필요 → `docs/01_architecture/` 빈 디렉터리 제거 → `pytest --ignore=archive` 182건 유지 확인 → 전수 grep으로 잔존 여부 재확인(historical 59개 문서는 의도적 보존이므로 남아 있어야 정상) → `hqs/development/{BASELINE.md,BOUNDARY.md,HANDOVER.md}` 등의 나머지 6개 참조는 이 ADC 범위 밖(별도 승인 필요).

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| RFC | `docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md` | Migration 위치 매핑(§6.1)의 출처 |
| ADR | `docs/decisions/adr/ADR-0006-structure-v1-migration.md` | §2가 BASELINE.md를 원래 포함 — 이 ADC가 그 미뤄둔 항목을 마무리 |
| ADC | `docs/decisions/adc/ADC-0005-structure-v1-migration-decisions.md` | 동일 성격(Migration 순서·범위 판단)의 선례 |
| Open Decision | — | Q-1(내부 인용 13건 수정의 성격)은 후속 ADR이 확정 |

## Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | Reference Audit 발견 항목 판단 |
