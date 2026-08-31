# ADR-0009: Development HQ Stage Data Contract — Public Scope Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | ADR-0009 |
| 제목 | RFC-0009(Stage Data Contract)의 ADC Scoped Accept 판단을 실제 문서 반영으로 옮기기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/decisions/rfc/RFC-0009-stage-data-contract.md` B-1/B-2/B-3 Decision + `docs/governance/adc/ADC-0007.md` Scoped Accept 판단(§3 Public/Hidden 표) |
| 관련 RFC | `docs/decisions/rfc/RFC-0009-stage-data-contract.md` |
| 관련 ADC | `docs/governance/adc/ADC-0007.md` |
| 선례 | ADR-0004(Kernel Public Contract Baseline) — Public/Hidden 구분·변경 규칙 형식만 재사용, 5분류(PR/G/H/X/N) 전체는 재사용하지 않음 |

이 ADR은 ADC-0007이 이미 내린 Scoped Accept 판단을 다시 논의하지
않는다. 새로운 철학이나 Architecture를 제안하지 않는다. ADC-0007이
승인한 Public Scope만 실제 문서 변경으로 옮기기 위한 **구현 결정**만
기록한다. dc879e5의 코드는 이 ADR로 수정되지 않는다 — 이미 구현되어
있는 상태를 Governance 관점에서 추인·문서화할 뿐이다.

## Out of Scope (이 ADR이 다루지 않는 것)

| 항목 | 근거 |
|---|---|
| candidate_index 재사용/중복 계산 제거 | FREEZE-0001 §5 사전 승인, RFC-0009 범위 밖 |
| Stage 순서 / Static Workflow(`workflow.py`)의 호출 배선 | Contract는 "무엇을 주고받는가"만 규정 — RFC-0009 §4 |
| Dynamic Workflow / Scheduler / Parser / Runtime | RFC-0009가 채택·설계하지 않음, 별도 RFC 대상 |
| Agent Routing | 이 Contract의 규정 대상 아님 |
| Security/Data-API 검사 신설 | `KNOWN_CHECK_NAMES` 확장에 해당 — §4 별도 RFC 대상으로 명시 |
| Kernel Public Contract(Baseline §14) | 이 ADR이 재론·수정하지 않음. Stage Data Contract는 그와 별개의 HQ-level Contract(RFC-0009 B-2) |
| 각 검사의 내부 판정 로직, `code_review` 생성 방식 | Hidden으로 분류(§3) — 이 ADR이 계약 대상으로 다루지 않음 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `hqs/development/BASELINE.md` | "Stage Data Contract" 절 신설 — 아래 §3 Public 표와 §5 변경 규칙만 등재 |
| `hqs/development/stages/01_context_analysis/CONTEXT.md` 외 4건(`SPECIFICATION.md`/`DESIGN.md`/`IMPLEMENTATION.md`/`VALIDATION.md`) | "새 Contract를 만들지 않는다" 문구를, "이 Stage의 반환 형태는 ADR-0009가 정의하는 Stage Data Contract의 Public Scope다"로 정정 |

그 외 어떤 파일도 변경하지 않는다. **코드 파일(`contracts.py`,
`stage_0N.py`, `workflow.py` 등)은 이 ADR로 일절 수정하지 않는다** —
이미 구현되어 있으며 152개 테스트로 검증된 상태를 그대로 인정한다.

### 2. `hqs/development/BASELINE.md` 절 위치

기존 절을 재배치하지 않고, "Open Decisions" 절 다음·"Governance"
절 이전에 새 절을 추가한다. Kernel Public Contract(Jarvis OS
Architecture Baseline §14)와 절 번호 체계를 공유하지 않는다 — 서로
다른 문서, 서로 다른 소유 범위(RFC-0009 B-2).

### 3. Public Contract (신설) — Stage Data Contract의 계약 범위

> 이 절은 Kernel Public Contract(§14)를 확장하거나 대체하지 않는다.
> Development HQ 내부 Stage 01~05 사이에서만 성립하는, 별개의
> HQ-level Contract다(RFC-0009 B-2). 이 계약의 **개정 절차**는
> Development HQ가 독자 소유하지 않고 상위 Jarvis OS Governance
> (RFC → ADC → ADR)가 관리한다.

| Public 항목 | 내용 | 근거 |
|---|---|---|
| **5개 Stage Contract 필수 키** | `ContextAnalysisResult`/`SpecificationResult`/`DesignResult`/`ImplementationResult`/`VerificationResult` 각각의 `*_REQUIRED_KEYS`(`contracts.py`에 구현된 값 그대로) | RFC-0009 B-1 |
| **`KNOWN_CHECK_NAMES`** | `("structural", "specification_scope", "design_scope", "test_execution")` — 이 4개로 **고정**. 추가/삭제는 아래 §5 규칙 대상 | RFC-0009 §3.1 |
| **`required_checks`** | Stage 05가 실제로 실행·판정에 반영할 검사 이름의 부분집합 파라미터. 비어 있거나 `KNOWN_CHECK_NAMES` 밖의 이름을 포함하면 `ContractViolation` | RFC-0009 §3, B-3 |
| **`check_results`** | `[{name, status, blocking, detail}, ...]` 스키마, 항상 `KNOWN_CHECK_NAMES` 전체를 이름 기준으로 나열 | RFC-0009 §3 |
| **`status` 집합** | `{"PASS", "FAIL", "INCONCLUSIVE", "SKIPPED"}` | RFC-0009 §3 |
| **`blocking` 규칙** | `structural`/`design_scope`/`test_execution` = blocking, `specification_scope` = non-blocking(`_BLOCKING_CHECKS`) | RFC-0009 §3 |

### 4. Hidden (Public Contract 아님, 절차 없이 자유 변경)

| Hidden 항목 | 근거 |
|---|---|
| 각 검사의 내부 판정 로직(`_check_structural`/`_check_specification_scope`/`_check_design_scope`/`_run_pytest_with_applied_implementation`, `_CHECK_EVALUATORS`의 개별 함수 본문) | 결과값만 계약이고 계산 방법은 Capability 함수 재사용 원칙상 원래도 계약 대상이 아니었음(RFC-0009 §3) |
| `code_review` 필드 생성 방식(`backend_agent_code_review()` 호출 여부/게이팅 조건) | Evidence 보조 필드, 이전부터 계약 대상 아님 |

**단서**: Hidden 항목의 변경이 §3 Public 표가 규정한
`status`/`blocking`의 **의미**를 바꾸는 경우(예: `test_execution`의
PASS 판정 기준 자체를 바꾸는 경우) 그 변경은 Hidden이 아니라 Public
변경으로 재분류하고 §5 규칙을 따른다.

### 5. 계약의 변경 규칙

| 변경 대상 | 절차 |
|---|---|
| §3 Public 표의 어떤 항목이든(키 추가/삭제, `KNOWN_CHECK_NAMES` 확장/축소, `status`/`blocking` 의미 변경 포함) | **RFC → ADC → ADR** |
| §4 Hidden 항목(Public 의미를 바꾸지 않는 범위) | **절차 없이 자유 변경** |

특히 **Security/Data-API 등 새 검사 종류를 `KNOWN_CHECK_NAMES`에
추가하는 것은 이 표의 첫 항목(Public)에 해당하며, 예외 없이 별도
RFC→ADC→ADR 대상**이다 — FREEZE-0001의 기존 범위 제약("Security/
Data-API Capability는 이번 PR 범위 밖")과도 일치한다.

### 6. Development HQ Baseline 불변 확인

- `hqs/development/stages/01~05/*.py`, `workflow.py`, `cli.py`,
  `mvp/` 이하 어떤 코드 파일도 이 ADR로 변경하지 않는다.
- 152개 테스트는 이 ADR로 영향받지 않는다(문서만 변경, §8에서
  재확인).
- Stage 개수·순서·Capability·Agent는 무변경(FREEZE-0001 §3 그대로
  유지).
- Kernel Public Contract(Baseline §14)는 한 글자도 변경하지 않는다.

### 7. 기존 RFC/ADC/ADR/Baseline과의 충돌 확인

- **ADR-0004(Kernel Public Contract Baseline)**: 충돌 없음 — 서로
  다른 레이어(Kernel vs Dev HQ)의 Contract이며, 이 ADR은 §14를
  인용만 하고 수정하지 않는다. Public/Hidden 구분·변경 규칙 **형식**
  만 재사용하며, ADR-0004의 PR/G/H/X/N 5분류 전체를 요구하지
  않는다(비례성 판단, ADC-0007 판단 1 근거).
- **`docs/decisions/adc/ADC.md`(Kernel 수준 ADC-01~12)**: 충돌 없음 —
  ADC-09(Workflow 그래프의 의미론적 경계)는 OS/Kernel 수준 Workflow
  스키마를 다루며 레이어가 다르다. 이 ADR이 그 Open Decision을
  해소·침해하지 않는다.
- **`hqs/development/BASELINE.md`**: 충돌 없음 — "Not Included"
  목록(Kernel Design/Scheduler/Engine Gateway/Registry/Runtime 등)에
  Stage Data Contract는 포함되지 않는다. 이 ADR이 신설하는 절은
  "Development HQ는 Architecture Decision을 소유하지 않는다"는 기존
  원칙과도 모순되지 않는다 — 계약의 **내용**은 이 Baseline에
  등재되지만, **개정 권한**은 상위 Governance 체인에 그대로
  남는다(§3 서두 인용문).
- **RFC-0007 / ADC-0005 / ADR-0008**: 충돌 없음 — 이 세 문서 중
  어느 것도 Stage 05 검사 부분집합 실행이나 형식적 Contract 계층을
  이미 규정·금지하지 않았다. RFC-0007 §3의 "Design 출력 구조화는 이
  RFC 밖의 판단"이라는 이월을 이 ADR이 이어받아 처리한다(선례).
- **FREEZE-0001**: §4/§7이 요구한 절차(Contract 변경 =
  RFC→ADC→ADR)를 정확히 이 ADR로 충족한다. §3("Validation Result는
  결정적 규칙으로 산출") 문언은 RFC-0009 B-3에서 확정한 해석("주어진
  `required_checks`에 대해 결정적")과 일치하며 위반하지 않는다.

### 8. 검증

- `hqs/development/BASELINE.md` §Stage Data Contract 반영 확인.
- Stage `*.md` 5건의 "새 Contract를 만들지 않는다" 문구 정정 확인.
- `git diff`로 코드 파일(`*.py`)에 변경이 없는지 확인.
- `pytest hqs/development/mvp/tests -q` 152 passed 재확인(문서만
  변경했으므로 회귀 없음이 당연하나 절차상 재확인).

---

## Consequences

- `hqs/development/BASELINE.md`에 "Stage Data Contract" 절이 신설되고,
  **Development HQ가 외부(Workflow/향후 Dynamic Workflow)에 무엇을
  보장하는가**가 처음으로 문서화된다.
- **계약의 실질적 효력이 생긴다**: §3 Public 항목의 변경은
  RFC→ADC→ADR 절차를 거쳐야 하고, §4 Hidden 항목은 자유롭게 바뀔 수
  있다.
- **`KNOWN_CHECK_NAMES` 확장(Security/Data-API 포함)의 판단 기준이
  생긴다** — 향후 어떤 검사가 제안되든 "이 표에 새 이름을
  추가하는가"로 즉시 절차 필요 여부를 판별할 수 있다.
- **Dynamic Workflow는 이 ADR이 결정하지 않는다** — 다만 §3 Public
  표가 Stage 순서·Workflow·Scheduler·Agent Routing을 규정하지 않는다는
  사실(RFC-0009 §4) 자체가, 향후 Dynamic Workflow RFC가 이 Contract를
  재검토 없이 재사용할 수 있는 근거로 남는다. 이 재사용 가능성은 이
  ADR이 보증하지 않으며, 그 별도 RFC가 스스로 검증해야 한다.
- **Kernel Public Contract는 한 글자도 변경되지 않는다.**
- 남는 절차 부채: `contracts.py`가 실제로 Public 표를 위반하는 값을
  반환하지 않는지 지속 검증하는 메커니즘(현재는 테스트 커버리지에
  의존, 별도의 강제 도구는 Defer)은 이 ADR이 다루지 않는다.
