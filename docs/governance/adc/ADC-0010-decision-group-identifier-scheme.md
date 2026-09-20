# ADC-0010 — RFC·ADC·ADR 통합 식별자 체계 도입 여부 판단 (Issue #206 후속)

## 1. Identity & Status

| Field | Value |
|---|---|
| ID | ADC-0010 |
| Status | Resolved (Scoped Accept) |
| Owner / Scope | Governance 절차(문서 색인) — Architecture Decision 아님 |
| Context | Issue #206이 요청한 "RFC·ADC·ADR을 의사결정 단위로 추적 가능하게 하는 통합 식별자 체계" 설계. 선행 근거는 `docs/research/RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md`(PR #208)이며, 이 ADC는 그 조사 결과를 인용하고 재조사하지 않는다 |

> 별도 선행 RFC 없이 Issue #206의 직접 요청으로 연다 — `ADR-0008`(Architecture
> Owner 직접 지시, ADC 경유 없음)과 같은 성격의 선례이며, 대상이 Kernel
> Boundary가 아니라 문서 식별자 체계라는 Governance 절차 자체이므로 RFC의
> 전통적 대상(Boundary Question)에 해당하지 않는다.

## 2. Decision Scope & Context

| Item | Description |
|---|---|
| Decision Scope | RFC·ADC·ADR 통합 식별자 체계 채택 여부와 형태 |
| Context | 사전 조사 결과(investigation 문서 전체 근거 참조): 3개 트리(Dev HQ/Kernel/Execution Layer) 약 141개 파일, 제목-파일명 불일치 0건. **1 RFC → 다수 ADC/ADR 분기(fan-out)** 확인(Dev HQ RFC-0006 → ADC-0005+ADC-0006 → ADR-0006+ADR-0007). **다수 RFC → 1 ADC 집약(fan-in)** 확인(Kernel RFC-0024~0030 → ADC-0032/ADC-0033). **1 ADC 내 부분 종결(partial closure)** 확인(`docs/decisions/adr/ADR-0001`은 `ADC-0003`의 "판단 1"만 종결). ADR 채번은 3개 트리 전부에서 RFC/ADC 번호와 무관하게 작성 순서로 독립 증가(일관된 컨벤션). 기존 번호·링크에 README/ADC.md/다수 ADR "관련 ADC/RFC" 필드·`project_intelligence.py`(실행 코드)가 실제 의존 |
| Constraints | Issue #206 §7: 사전 승인 없는 전체 재번호화, 기존 링크 일괄 변경, Architecture Baseline 소급 수정 금지. Issue #206 §4: 기존 번호를 보존하면서 통합 식별자를 병기할 수 있는가를 반드시 검토 |
| Non-Goals | 기존 RFC/ADC/ADR 파일의 재번호화·이름 변경·내용 수정, Architecture Baseline 소급 수정, PR #207 템플릿의 임의 변경, ADR 신규 생성(이 ADC는 규칙만 확정, Baseline 반영은 후속 ADR 대상) |

**핵심 결론(재확인)**: RFC=ADC=ADR 단일 번호 강제는 fan-out·fan-in·partial-closure 세 실제 관측 패턴과 구조적으로 양립 불가능하다 — "번호를 맞추는" 접근이 아니라 "관계를 명시적으로 기록하는" 접근이 필요하다.

## 3. Candidates / Options

| ID | Candidate | Description | Evidence | Advantages | Risks / Trade-offs |
|---|---|---|---|---|---|
| A | 단순 공통 번호(`RFC-006`/`ADC-006`/`ADR-006`) | 세 문서 종류가 같은 번호 공유 | fan-out/fan-in 실증 사례와 비교 | 가시성 높음 | fan-out/fan-in 발생 시 번호 하나로 표현 불가. 기존 141개 문서 전체 재번호 필요(Issue #206 §7 위반) |
| B | 분기 접미사(`ADC-006-A`/`ADR-006-A`) | 분기마다 접미사 부여 | 상동 | 1:N 분기는 표현 | fan-in(다수 RFC→1 ADC) 소속 모호, 중첩 분기 시 접미사 폭발. 소급 적용 시 파일명 변경 불가피(Issue #206 §7 위반 위험) |
| C | Decision Group + 점 표기(`D-006`/`ADC-006.1`) | Group이 N:M 관계를 수용 | 상동 | fan-out/fan-in/partial-closure 모두 Group 하위 항목으로 표현 가능, 기존 파일명·ID 변경 없이 신규 Registry로 병기(변경 범위 0) | Group ID 별도 조회 필요 |

## 4. Evaluation

| Criterion | Weight / Priority | A | B | C | Notes |
|---|---|---|---|---|---|
| 추적성 | 높음 | 낮음 | 중간 | 높음 | fan-out/fan-in/partial-closure 표현력 기준 |
| 기존 문서와의 호환성 | 필수(Issue #206 §7) | 불가 | 낮음 | 높음 | C만 기존 파일 무변경으로 병기 가능 |
| Governance 적용 난이도 | 높음 | 매우 높음 | 높음 | 낮음 | C는 추가 전용 |

## 5. Recommendation & Decision Boundary

| Item | Description |
|---|---|
| Recommendation | 후보 C의 "논리적 그룹" 개념만 채택하고, 점(`.`) 표기를 기존 파일명에 소급 적용하지 않는다 — 별도 Registry 문서로 구현(Scoped Accept) |
| Decision Boundary | `docs/governance/DECISION-GROUP-REGISTRY.md`(공식 전역 `DG-NNNN` 네임스페이스)의 설계 규칙만 확정한다. 이 ADC는 그 문서를 직접 생성하지 않는다 — 후속 구현 작업으로 지정 |
| Out of Authority | 기존 RFC/ADC/ADR 파일 수정, Architecture Baseline 반영(이 결정은 Governance 절차 변경이며 Architecture Decision이 아니므로 ADR 대상이 아님) |
| ADR Requirement | 불필요 — Registry 신설은 Baseline 변경이 아니라 순수 추가 문서 작업이므로 "ADR은 ADC에서 Accept/Promote로 판단된 사항을 Baseline 문서 변경 결정으로 기록"하는 정의에 해당하지 않는다 |
| Re-evaluation Trigger | 신규 fan-out/fan-in 사례 발생 시 Registry에 행 추가(재번호 불필요) |

## 6. Open Questions

| ID | Question | Required Evidence | Owner |
|---|---|---|---|
| Q-1 | 원장(Ledger)의 `Decision Group` 필드(`DG-<도메인>-NNNN`)와 이 ADC가 정한 공식 Registry(`DG-NNNN`)의 관계 | 두 네임스페이스가 실제로 별개인지, 병존 가능한지 | `docs/decisions/open_decision.md` OD-0001(5차 라운드에서 Reconsidered로 종결 — 별개 네임스페이스로 병존 확정) |

## Decision 세부 내용 — Decision Group Registry (추가 전용, 비파괴적)

- **Decision Group ID**: `DG-NNNN` 형식의 신규 전역 순차 번호. RFC/ADC/ADR/OD 어느 것과도 번호 체계를 공유하지 않는 독립 네임스페이스.
- **Decision Group Registry**: 신규 문서 1개(`docs/governance/DECISION-GROUP-REGISTRY.md`)가 각 `DG-NNNN`에 대해 DG ID/Title/Domain/Member RFCs/Member ADCs/Member ADRs/Status(Open/Partially Resolved/Resolved/Superseded)/Evidence를 기록한다. 기존 파일은 전혀 수정하지 않는다 — Registry는 순수 색인이다. 신규 문서는 선택적으로 Related Documents 표에 `Decision Group: DG-NNNN`을 추가할 수 있다(fan-out/fan-in 발생 시에만, 의무 아님).
- **분기·보류·대체·폐기 규칙**: RFC 1건→ADC 여러 건은 동일 `DG-NNNN`에 전부 Member 등록. ADC 1건→ADR 여러 건(부분 종결)은 "ADC-XXXX 판단 N"으로 명시. ADR 미작성은 "Reserved — 번호 미정"(사전 확정하지 않음). Deferred/Not Accepted는 Status "Resolved(Not Accepted)", 식별자 유지. 대체(Superseded)는 기존 문서·번호를 삭제하지 않고 Status만 "Superseded by DG-MMMM"으로 갱신.
- **기존 문서 마이그레이션**: 전면 마이그레이션 수행하지 않는다(141개 전체 매핑은 근거 검증 비용·오류 위험 큼). 점진적·근거 기반 등록만 — 이미 확인된 fan-out/fan-in 사례(Dev HQ RFC-0006 그룹, Kernel RFC-0024~0030 그룹)부터 등록하고, 나머지는 "미등록 = 여전히 독립 문서"로 남긴다.
- **Open Decision 처리**: Issue #206 §5 원칙 그대로 — OD는 `OD-XX` 독자 번호 체계를 유지하며 RFC/ADC/ADR 번호로 변경하지 않는다. `DG-NNNN`과의 관계는 선택적 연결(Related Documents 표 기재)로 한정 — OD 자체 번호나 Baseline 포함 여부에 영향 없음.

## 후속 구현 작업 목록

1. `docs/governance/DECISION-GROUP-REGISTRY.md` 신규 생성(빈 표 + Field 정의).
2. 이미 근거가 확인된 2개 그룹(Dev HQ RFC-0006 계열, Kernel RFC-0024~0030 계열)을 최초 등록.
3. `docs/decisions/{rfc,adc,adr}/README.md`, `docs/governance/README.md` "Document Numbering" 절에 Decision Group 안내 문단 추가(선택).
4. 신규 RFC/ADC/ADR 작성 가이드에 "Decision Group 선택적 기재" 안내 추가 여부 검토(선택).

이 4개 항목 중 어느 것도 이 ADC가 직접 실행하지 않는다 — Governance 승인 이후 별도 구현 세션에서 진행한다.

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| Investigation | `docs/research/RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md` | 이 ADC의 조사 근거(PR #208) |
| Registry | `docs/governance/DECISION-GROUP-REGISTRY.md` | 이 ADC가 설계를 확정한 공식 Registry(후속 구현으로 생성됨, DG-0001·DG-0002 등록) |
| Ledger | `docs/decisions/{rfc,adc,adr}.md` | 원장 내부 `Decision Group`(`DG-<도메인>-NNNN`) 필드 — 이 Registry와 별개 네임스페이스(OD-0001 Resolution 참조) |
| Open Decision | `docs/decisions/open_decision.md` OD-0001 | Registry-Ledger 네임스페이스 관계를 재확인·종결(Reconsidered) |
| Precedent | `docs/decisions/adr/ADR-0008-stage-folder-code-and-docs.md` | "Architecture Owner 직접 지시, ADC 경유 없음" 선례 |
| Precedent | `docs/governance/adc/ADC-0009.md` | ADC 문서 형식(판단/Evidence/Options/Recommendation) 참조 |

## Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | Issue #206 통합 식별자 체계 판단 |
