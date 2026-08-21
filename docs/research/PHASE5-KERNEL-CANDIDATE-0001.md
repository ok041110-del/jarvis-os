# PHASE5-KERNEL-CANDIDATE-0001: Kernel Candidate 판단

**문서 성격**: Governance 판단이 아니라 후보 도출 기록이다. **이 Phase는 코드를 작성하지 않는다.** Structure v1.0 / Architecture Baseline / Development HQ v1.0 Freeze / Investment HQ v1.0 Freeze 어느 것도 수정하지 않는다. Candidate가 `core/` 어느 하위 영역에 해당하는지는 Phase 7(Kernel Governance)의 RFC에서 다룬다 — 이 문서가 결정하지 않는다.

## 목적

`roadmap.md` Phase 5 완료 조건("Kernel Candidate 목록과 각 후보의 5기준 판단 근거가 문서화됨")을 충족한다. 입력은 `PHASE4-HQ-CROSS-VALIDATION-0001.md`의 "Common" 판정 2건(Engine 호출 방식, Parallel Execution)이다.

## Kernel 책임 정의(Structure v1.0 원문 인용, 추측 없음)

`docs/architecture/baseline/STRUCTURE-V1.0-FROZEN.md`의 `core/` 하위 10개 영역(`registry/runtime/scheduler/policy/communication/execution/events/context/memory/observability`)과 Core Domain Model(`HQ→Project→Workflow→Stage→Task→Agent→Capability→Execution→Provider/Tool/MCP`)을 판단 기준으로 그대로 사용했다.

## 5기준 판단

### Candidate 1 — Parallel Execution(원시 기법): `ThreadPoolExecutor.submit()`+`.result()`로 독립 Task를 동시에 `call_engine()` 호출)

| 기준 | 판단 | 근거 |
|---|---|---|
| 공통성 | 충족 | Dev HQ 자체 연구(`ENGINE-USECASE-0001/0002`, PR #60/#61, 2026-08-15)와 Investment HQ 프로덕션(PR #77/#80 계보 + 실제 HQ 실행 6건)이 **서로 독립적으로** 동일 기법에 도달·반복 사용 |
| 도메인 독립성 | 충족 | 원시 기법 자체(스레드로 `call_engine()` N회 동시 호출)는 Stock/ETF/Dividend Stock이나 code_review 같은 도메인 지식을 전혀 참조하지 않음. Dev HQ 실험도 Backend/QA Agent 호출로 도메인 중립적이었음 |
| 반복성 | 충족 | Dev HQ 3회 실측(2-way/3-way/4-way), Investment HQ 6건 프로덕션 실행 — 1회성 아님 |
| 안정성 | 충족(잠정) | 2026-08-15 최초 검증 이후 요구사항 변경 없음(짧은 관찰 기간이므로 "충족"이되 장기 안정성은 추가 관찰 필요) |
| 재사용성 | 충족 | 두 HQ가 동일한 `ThreadPoolExecutor.submit(fn, ...)`+`.result()` 호출 패턴을 코드 수정 없이 그대로 재사용(diff 수준 확인) |

**판정: Kernel Candidate로 확정.** 단, Wave 구조(4단계 하드코딩 + Bull/Bear/Synthesis 등 도메인 명명)와 Checkpointing 통합체는 이 Candidate에서 **명시적으로 제외**한다 — 그 부분은 도메인 독립성 기준을 충족하지 못한다(`PHASE4-HQ-CROSS-VALIDATION-0001.md` "Wave 구조" 항목 참조).

### Checkpointing — Kernel Candidate 아님(유지)

| 기준 | 판단 | 근거 |
|---|---|---|
| 공통성 | 미충족 | `hqs/development/mvp/`에 Checkpointer가 존재한 적이 없음(전수 grep 0건). Dev HQ가 독립적으로 필요로 한 사례 자체가 없다 — Dev HQ MVP는 180초 이내 2-Task 선형 파이프라인이라 재개가 필요했던 적이 없음(실측) |

**판정: 5기준의 첫 번째(공통성)부터 미충족 — Kernel Candidate로 승격하지 않는다.** Investment-specific 상태를 유지한다. Dev HQ가 실제로 재개가 필요한 사례를 겪기 전까지는 추측으로 공통성을 부여하지 않는다.

### Engine 호출 방식(`call_engine()`) — Common이나 Kernel 추출 신규 검토 대상 아님

공통성 자체는 `PHASE4-HQ-CROSS-VALIDATION-0001.md`에서 이미 확인됐으나(동일 함수 live import), Kernel 추출(Engine Adapter/Gateway) 여부는 `docs/research/PHASE9-CLOSURE-0001.md`가 이미 "Adapter/Gateway 불필요, 2번째 Engine이 실제로 등장할 때만 재검토"로 **명시적으로 판정·종료**했다(`ADC-0010`/`ADC-0011`도 Not Accepted로 동일 결론). 현재 Engine 수는 여전히 1. 이 문서는 기존 Governance 판정을 재론하지 않는다 — 새 Candidate로 다루지 않는다.

## Kernel Candidate 목록(최종)

| Candidate | 상태 |
|---|---|
| Parallel Execution(원시 기법, Wave/Checkpointing 제외) | **확정 — 1건** |
| Checkpointing | 미승격(Investment-specific 유지) |
| `call_engine()` | Common이나 기존 Governance가 이미 추출 Defer(재검토 대상 아님) |

**Phase 5 완료 조건 충족**: Kernel Candidate 1개 이상 존재(Parallel Execution).

## Phase 6로 넘어가는 조건과 범위(제안, 이번 Phase에서 착수하지 않음)

Phase 6(Kernel Prototype & Validation)에서 검증할 범위를 다음으로 좁혀 제안한다 — **이번 문서/PR에서는 구현하지 않는다**:

- `core/execution/`(기존 MVP-0001~0006 Builder 파이프라인)과 완전히 무관한, 두 HQ 어디에도 속하지 않는 **3번째 도메인 중립 맥락**(예: 순수 텍스트 요약 2-Task 동시 호출)으로 Parallel Execution 기법을 재현.
- Registry/Scheduler/Gateway를 만들지 않는다.
- `core/execution/`의 기존 미사용 Builder 파이프라인과의 관계 정리(같은 이름 "Execution"이 가리키는 두 개의 분리된 계보를 어떻게 다룰지)는 Phase 6 착수 시점에 별도로 판단한다 — 이번 문서가 결정하지 않는다.
- RFC/ADC/ADR 착수 여부는 Phase 6 Prototype 결과를 본 뒤 판단한다 — 이번에 결정하지 않는다.

## 관찰되지 않은 것(명시적으로 기록)

- Parallel Execution이 두 HQ 외의 세 번째 독립 맥락에서도 재현되는지 — 아직 관찰 안 됨.
- Checkpointing이 Dev HQ에서 실제로 필요해지는 시점 — 아직 도래하지 않음.
- Agent-Capability 매핑(Uncertain)의 추가 판단 — 이번 Phase가 다루지 않음(Phase 4의 Uncertain 상태 그대로 유지).

---

## Architecture/Governance 영향

**없음.** Structure v1.0 / Architecture Baseline / Development HQ v1.0 Freeze / Investment HQ v1.0 Freeze 어느 것도 수정하지 않았다. 새 RFC/ADC/ADR을 작성하지 않았다. Kernel Component/코드를 만들지 않았다(판단·문서화만 수행). `PHASE9-CLOSURE-0001`의 기존 판정을 재론하지 않았다.
