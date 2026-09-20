# ADR-0007 — Architecture Baseline 문서의 Structure v1.0 위치 확정

> `docs/01_architecture/BASELINE.md` → `docs/architecture/baseline/BASELINE.md`
> 확정. 이 ADR은 ADC-0006이 이미 비교한 Option A/B를 다시 논의하지 않고,
> **이동을 실행하지도 않는다** — 위치·Reference 정합성 확정만 이 문서의
> 범위다.

## 1. Identity & Status

| Field | Value |
|---|---|
| ID | ADR-0007 |
| Status | Accepted — 위치·Reference 정합성만 확정한다. 이 ADR 자체는 이동을 실행하지 않는다 |
| Owner / Scope | Architecture Baseline 문서의 Structure v1.0 위치 확정 |
| Context | `docs/decisions/adc/ADC-0006-baseline-relocation-decision.md` |

## 2. Context & Decision Drivers

| Item | Description |
|---|---|
| Context | ADC-0006이 Option A(이동)를 Recommend했고, 이 ADR이 그 Recommendation을 확정한다. ADC-0006이 스스로 결정하지 않고 남긴 한 가지 — "BASELINE.md 내부 Reference 수정이 Architecture 내용 수정인가, Migration 정합성 유지인가" — 만 이 ADR에서 추가로 확정한다 |
| Decision Drivers | 이동 자체의 추가 비용(외부 Active Reference 4곳)이 작고 코드 의존이 전혀 없어 위험이 낮다(전수 grep 확인, ADC-0006 Context). 내부 Reference 13곳 수정은 Option B를 택해도 어차피 필요한 작업 |
| Constraints | `ADR-0006` 본문은 수정하지 않는다. `docs/` taxonomy의 나머지 140개 불명확 문서는 확대하지 않는다 |
| Out of Scope | BASELINE.md의 Architecture 내용(Meta Architecture/Concept Model/Kernel 정의 등) — §7에서 불변임을 재확인. Reference Audit가 발견한 나머지 6개 ACTIVE 참조(`hqs/development/*` 5곳, `core/execution/pipeline.py` 1곳) — 별도 판단 대상 |

## 3. Decision

**이 ADR은 이동을 실행하지 않는다.** ADR 파일 생성만 이번 작업의 범위이며, `docs/01_architecture/BASELINE.md`는 이동·수정하지 않았다.

1. **Option A 채택**: `docs/01_architecture/BASELINE.md`를 `docs/architecture/baseline/BASELINE.md`로 이동하기로 확정한다(ADC-0006의 비교 근거를 그대로 채택).
2. **ADR-0006과의 관계**: ADR-0006을 수정하지 않는다. ADR-0006 §2는 BASELINE.md를 원래 "명확 대응" 목록에 포함시켰으나 실행 지시가 "BASELINE.md 변경 금지"를 요구해 그 항목만 제외됐다 — 이는 ADR-0006 Consequences가 예정해 둔 "재검토 조건"에 해당한다. 이 ADR은 그 미뤄둔 한 항목에 대한 후속 확정 결정이며, ADR-0006의 3단계 Migration Phase 구조나 다른 결정은 뒤집지 않는다.
3. **Migration 범위**(실행은 이 ADR 이후 별도 작업):
   - `git mv` 1건: `docs/01_architecture/BASELINE.md` → `docs/architecture/baseline/BASELINE.md`(Git history 보존, `git log --follow`로 확인).
   - 외부 Active Reference 4곳 갱신: `README.md` 7행·58행, `CLAUDE.md` 55행, `.claude/skills/branch-lifecycle/SKILL.md` 71행.
   - BASELINE.md 내부 Reference 13곳 갱신(86/129/159/211/339/367/412/548/779/780/798/805/816행): `docs/03_adc/`(4곳)→`docs/decisions/adc/`, `docs/04_adr/`(5곳)→`docs/decisions/adr/`, `docs/02_rfc/`(1곳)→`docs/decisions/rfc/`, `development-hq/BOUNDARY.md`(3곳)→`hqs/development/BOUNDARY.md`.
   - Reference Audit가 발견한 나머지 6개 파일(`hqs/development/*` 5곳, `core/execution/pipeline.py` 1곳)은 이 범위에 포함하지 않는다 — hqs/·core/ 수정 금지가 유효하며 별도 판단 대상.
4. **`docs/01_architecture/` 빈 디렉터리 정리**: BASELINE.md 이동 후 다른 파일이 없으므로(전수 확인) `rmdir`로 제거한다.
5. **검증 계획**(Migration 실행 시): `git log --follow`로 history 보존 확인 → `pytest --ignore=archive -q` 182건 유지 확인 → 전수 grep으로 `docs/01_architecture/BASELINE.md` 잔존 여부(historical 59개 문서 잔존은 정상) → 전수 grep으로 `docs/03_adc/`·`docs/04_adr/`·`docs/02_rfc/`·`development-hq/BOUNDARY.md`가 전부 갱신됐는지 확인 → `git status`로 `hqs/`·`core/`·`archive/`·`projects/`·기존 RFC/ADC/ADR 무변경 확인.
6. **BASELINE 내용 자체는 변경하지 않음**: Migration 완료 후에도 Meta Architecture/Concept Model/System Boundary/Kernel 정의·원칙·Context Model/Public Contract/Logical Reference Architecture, 버전 번호(v1.6), 어떤 결정 문장도 바뀌지 않는다 — 13곳은 전부 인용 경로 문자열이며 그 문자열이 가리키는 문장·표·헤더 구조는 그대로 유지된다.

## 4. Rationale & Alternatives

### Rationale

| Reason | Explanation | Evidence |
|---|---|---|
| BASELINE.md 내부 Reference 수정의 성격 확정 | **13개 경로 인용 갱신은 CLAUDE.md "Architecture Baseline은 직접 수정하지 않는다"는 Frozen Architecture 원칙이 금지하는 "내용 수정"이 아니다.** 그 원칙이 막는 것은 Architecture의 결정 내용(Meta Architecture 정의, Concept Model, Kernel 경계, System Boundary 등)을 RFC→ADC→ADR 없이 바꾸는 행위다. 13개 인용은 전부 "이 문장의 근거·상세는 문서 X를 참조하라"는 포인터 문자열이며, 그 문서들이 가리키는 대상의 정체성·결정은 전혀 바뀌지 않는다 — 오직 물리적 위치 문자열만 최신화된다 | `ADR-0002` §5·§6이 이미 사용한 "디렉토리 경로·파일명·코드 식별자 변경"과 "문서 내용의 용어 통합"의 구분을 인용 경로 수정에도 동일 적용 |
| Option A가 Option B보다 효율적 | 내부 Reference 13건 수정은 두 Option 모두에서 동일하게 필요하므로, 그 비용을 감수하는 김에 Structure v1.0 정합성까지 함께 얻는 쪽이 합리적 | ADC-0006 §비교 요약 |

### Rejected Alternatives

| Alternative | Reason for Rejection | Evidence |
|---|---|---|
| Option B(현재 위치 유지, 내부 인용만 수정) | Structure v1.0과의 불일치가 영구히(또는 재검토까지) 남고, 향후 `docs/architecture/` 정리 시 재작업 가능성이 생긴다 | ADC-0006 §비교 요약 |

## 5. Consequences & Impact

| Category | Impact |
|---|---|
| Positive Consequences | "인용 경로 갱신 ≠ Architecture 내용 변경" 구분이 이후 유사한 Migration 상황에도 재사용 가능한 선례로 남는다(단, 그 적용은 각 상황에서 별도로 재확인 — 이 ADR이 자동으로 다른 파일까지 승인하지 않는다) |
| Negative Consequences / Trade-offs | 없음 |
| Risks | 없음으로 평가 — 코드 의존 없음(전수 grep 확인) |
| Operational Impact | **후속 실행 필요**: 이 ADR은 결정만 확정했다. §3의 Migration 범위 실행은 별도 작업으로 진행한다. **남는 BLOCKED 항목**: Reference Audit가 발견한 나머지 6개 파일(`hqs/development/*` 5곳, `core/execution/pipeline.py` 1곳)은 이 ADR 범위 밖 — hqs/·core/ 수정 금지가 유지되는 한 별도 승인 필요 |

## 6. Architecture Baseline & Implementation

| Item | Description |
|---|---|
| Architecture Baseline Impact | 없음(내용) / 위치만 변경 — Migration 실행은 별도 작업 |
| Public Contract Impact | 없음 |
| Implementation Scope | §3의 Migration 범위(`git mv` 1건 + 외부 참조 4곳 + 내부 참조 13곳 + 빈 디렉터리 제거) |
| Follow-up Work | Reference Audit 잔여 6개 파일(`hqs/development/*` 5곳, `core/execution/pipeline.py` 1곳)의 별도 판단·승인 |

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| RFC | `docs/decisions/rfc/RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy.md` | Migration 위치 매핑의 출처 |
| ADC | `docs/decisions/adc/ADC-0006-baseline-relocation-decision.md` | Option A/B 판단과 "내부 Reference 수정의 성격" 질문 전부 이 ADR로 종결(Resolved) |
| ADR | `docs/decisions/adr/ADR-0006-structure-v1-migration.md` | §2가 BASELINE.md를 원래 "명확 대응"에 포함시켰으나 실행 지시로 제외 — 이 ADR이 그 미뤄둔 항목을 후속 확정 |
| Open Decision | — | 없음 |

## Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | ADC-0006 Option A/B 판단 확정 |
