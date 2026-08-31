# RFC-0009: Development HQ Stage Data Contract 공식화

**Status**: Resolved (Decision: 후보 C, Scoped Accept — 후속 `docs/governance/adc/ADC-0007.md` 참고)
**Author**: Claude Code (dc879e5 — Stage 01~05 Data Contract 정리 사후
Governance 조사에 대한 RFC)
**대상**: `hqs/development/stages/contracts.py` 및
`required_checks`/`SKIPPED`/`ContractViolation`(dc879e5)을 Frozen
Development HQ v2.0 위에서 Development HQ 수준 Data Contract로
공식화할지 여부와, 공식화한다면 그 Public/Hidden 경계와 Governance
소유 구조를 결정한다.
**Evidence 범위**: `dc879e5`/`ba2890c` diff 전체,
`DEVELOPMENT-HQ-V2.0-FREEZE-0001.md`, Stage 01~05 `*.md` 5건,
`IMPLEMENTATION_RULES.md`, `hqs/development/BASELINE.md`,
`ADR-0004-kernel-public-contract-baseline.md`,
`RFC-0007-ast-context-build-integration.md`. 이 RFC는 새 실험을 하지
않는다.

> 본 RFC는 Dynamic Workflow/Runtime/Scheduler/Parser/Agent Routing을
> 설계하거나 채택하지 않는다 — 그 결정은 별도 RFC 대상으로 남긴다.
> candidate_index 재사용은 `FREEZE-0001` §5가 이미 SHOULD FIX/DEFER로
> 승인한 별개 사안이라 이 RFC의 범위에서 제외한다. 본 RFC 자체는
> 코드/Baseline을 변경하지 않는다 — 결정이 필요하면 별도 ADC → ADR
> 단계로 넘긴다.

## 0. 이 RFC가 열린 이유

dc879e5는 Stage 05 `required_checks`의 causal-wiring 결함을 해소하는
과정에서 `contracts.py`(TypedDict 기반 Stage I/O 명세 +
`require_keys()`/`ContractViolation` 런타임 검증)를 신설하고,
`required_checks` 선택 실행·`SKIPPED` 상태를 Stage 05에 추가했다. 사후
PR Review에서 이 변경이 `FREEZE-0001` §4("보호 대상 무변경:
Architecture/Contract/Engine Prompt/Runtime Logic")와 §7("Freeze
이후 Architecture/Contract 변경은 RFC→ADC→ADR로만")이 지정하는 "Contract
변경"에 해당할 가능성이 확인되어, 사후 절차로 이 RFC를 연다.

## 1. Evidence 요약 (인용만, 새 조사 없음)

| 항목 | 확인 내용 | 근거 |
|---|---|---|
| Stage 01~05 원본 문서 5건 전부 "새 Contract를 만들지 않는다" 명시 | `CONTEXT.md`/`SPECIFICATION.md`/`DESIGN.md`/`IMPLEMENTATION.md`/`VALIDATION.md` 각 서두 | Stage `*.md` 5건 |
| `FREEZE-0001` §4가 "Contract"를 Architecture/Engine Prompt/Runtime Logic과 동일한 보호 대상으로 명시 | "보호 대상 무변경" 표 | `DEVELOPMENT-HQ-V2.0-FREEZE-0001.md` §4 |
| `FREEZE-0001` §7이 "Contract 변경"을 RFC→ADC→ADR 대상으로 명문화 | "Freeze 이후 Architecture/Contract 변경은 기존 RFC → ADC → ADR Governance 절차를 통해서만 진행한다" | 同 §7 |
| `FREEZE-0001` §5가 candidate_index 중복 제거만 사전 승인(DEFER) | "Freeze 영향: 없음 — 이미 검증된 코드를 건드리는 별도 세션 과제로 DEFER" | 同 §5 |
| `IMPLEMENTATION_RULES.md`가 인정하는 유일한 공식 Contract는 Kernel Public Contract(§14) | "새 Public Interface/Contract를 정의하지 않는다 — Kernel Public Contract(§14)는 이 허용과 무관하게 무변경이다" (2곳) | `hqs/development/IMPLEMENTATION_RULES.md` |
| `hqs/development/BASELINE.md`가 Development HQ의 Architecture Decision 비소유를 명시 | "Development HQ는 Architecture Decision을 소유하지 않는다. Architecture Open Decision은 Jarvis OS의 `docs/decisions/adc/ADC.md`를 참조한다" | `hqs/development/BASELINE.md` "Open Decisions" |
| `ADR-0004`가 Public/Hidden/Extension Point/Non-Goal 5분류와 "Public 변경은 RFC→ADC→ADR, Hidden 변경은 절차 없음" 규칙을 확립 | §3, Consequences | `ADR-0004-kernel-public-contract-baseline.md` |
| `RFC-0007` §3이 "Design 출력을 구조화할지 여부는 이 RFC 밖의 판단"이라며 Stage 출력 구조화를 미해결로 명시적으로 이월 | "Contract Impact" | `RFC-0007-ast-context-build-integration.md` §3, Contract Impact |

## 2. Decision Boundary와 Decision

### B-1. "Contract 없음" 선언의 정확한 범위는 무엇인가

**논의**: 원본 Stage 01~05 문서 5건은 반환 dict의 키·타입·생성
Capability를 이미 표로 상세히 서술하고 있었다. 따라서 "새 Contract를
만들지 않는다"는 "설명하지 않는다"는 뜻일 수 없다. 이 문구가 실제로
금지한 것은 **그 서술 위에 런타임으로 강제되는 형식적 스키마·검증
계층(TypedDict, 필수 키 검사, 위반 시 예외)을 두는 것**이다.
`contracts.py`는 정확히 이 계층을 신설했다.

> **Decision B-1**: "새 Contract를 만들지 않는다"는 각 Stage 반환
> dict의 형태를 문서로 서술하는 것 자체를 금지한 것이 아니라, 그
> 서술을 **런타임에 강제하는 형식적 계층(스키마 타입, key-presence
> 검증, 위반 시 예외)의 부재**를 뜻했다. `contracts.py`는 이 부재를
> 종료시키는 변경이며, 따라서 `FREEZE-0001` §4/§7이 규정하는
> "Contract 변경"에 해당한다 — RFC→ADC→ADR 절차 대상이다.

### B-2. 이 Contract 개념의 Governance 소유 위치는 어디인가

**논의**: 현재 Governance상 유일한 공식 Contract는 Kernel Public
Contract(Jarvis OS Architecture Baseline §14, ADR-0004)이며, 그
소유·개정 절차는 Kernel 수준(전체 Jarvis OS Architecture Baseline)에
있다. Development HQ Stage Data Contract는 이것과 **범위가 다르다** —
Kernel이 아니라 Development HQ 내부의 5개 Stage 사이에서만 성립하는
데이터 교환 계약이다. 그러나 `hqs/development/BASELINE.md`는
Development HQ가 스스로 Architecture Decision을 소유하지 않는다고
선언했으므로, 이 Contract를 Development HQ가 독자적으로 개정할 수 있는
로컬 규칙으로 둘 수 없다.

> **Decision B-2**: Stage Data Contract는 **Kernel Public
> Contract와 별개의, Development HQ 수준(HQ-level) Contract**로
> 정의한다 — Kernel Baseline §14를 확장하거나 재해석하지 않는다.
> 다만 그 **개정 절차(변경 시 RFC→ADC→ADR을 거쳐야 한다는 규칙,
> Public/Hidden 구분 원칙)는 Development HQ가 독자 소유하지 않고
> 상위 Jarvis OS Governance(`docs/decisions/rfc/` →
> `docs/decisions/adc/` → `docs/decisions/adr/`, `ADC.md`가
> Open Decision을 추적)가 관리한다**. 즉 "이 Contract가 무엇을
> 규정하는가"는 Development HQ 문서(`hqs/development/BASELINE.md`
> 또는 Stage 문서)에 등재하되, "이 Contract를 바꾸려면 무엇을
> 거쳐야 하는가"는 `hqs/development/BASELINE.md` §Governance에 이미
> 명시된 `RFC → ADC → ADR → Architecture Baseline Update →
> Development HQ Baseline Update` 절차를 그대로 따른다. 이는
> Development HQ가 Architecture Decision을 소유하지 않는다는 기존
> 원칙과 모순되지 않는다 — Contract의 **존재와 내용**은 HQ
> 문서에 등재되지만, 그 **개정 권한**은 여전히 상위 Governance에
> 있다.

### B-3. required_checks/SKIPPED와 "결정적 Verdict" 원칙의 관계

**논의**: `FREEZE-0001` §3은 "Validation Result(Stage 05 `verdict`)는
결정적 규칙으로 산출되며, Workflow/CLI 어느 층에서도 재해석되지
않는다"고 규정한다. `required_checks`는 Verdict 산출 **이후**의
재해석이 아니라 산출 **이전**의 입력(어떤 검사를 포함할지)을
바꾸므로, 동일한 `required_checks` 값이 주어지면 Verdict는 여전히
결정적으로(같은 입력 → 항상 같은 출력) 계산된다 — `Workflow`/`CLI`
어느 층도 Stage 05가 반환한 `verdict` 값을 다시 판정하지 않는다.

> **Decision B-3**: "결정적 규칙으로 산출된다"는 원칙은 **"고정된
> 4개 검사 전체"가 아니라 "주어진 `required_checks` 값에 대해"
> 결정적임을 뜻하는 것으로 확정한다.** `required_checks`는 Verdict
> 산출 규칙 자체를 바꾸는 것이 아니라 그 규칙이 적용되는 입력
> 범위를 바꾸는 것이며, 이는 §3이 금지하는 "재해석"에 해당하지
> 않는다. 단, 이 확정은 `required_checks`가 **Public Contract의
> 일부로 명시적으로 계약화된다는 것을 전제**로 한다(§3 참고) — 계약화
> 없이 임의 호출자가 검사 집합을 바꿀 수 있는 상태로 남겨두는 것은
> 이 Decision의 범위 밖이다.

## 3. Public/Hidden 경계 (ADR-0004 형식 재사용)

| 구분 | 대상 | 근거 |
|---|---|---|
| **Public** | `contracts.KNOWN_CHECK_NAMES`(Stage 05가 표현 가능한 검사 이름의 전체 집합) | B-1 — 이 집합의 추가/삭제는 Stage 05가 무엇을 검증할 수 있다고 외부에 보장하는지를 바꾼다 |
| **Public** | 5개 Contract TypedDict(`ContextAnalysisResult`/`SpecificationResult`/`DesignResult`/`ImplementationResult`/`VerificationResult`)의 필수 키 집합과 타입 | B-1 — Stage 간 실제로 주고받는 데이터의 형태 |
| **Public** | `required_checks`/`check_results`의 스키마(`{name, status, blocking, detail}`, `status ∈ {PASS, FAIL, INCONCLUSIVE, SKIPPED}`) | B-3 — Verdict 결정성의 전제가 되는 계약 |
| **Public** | 각 검사 이름의 `blocking` 여부(`_BLOCKING_CHECKS`) | Verdict FAIL 여부를 결정하는 외부에서 관찰 가능한 규칙 |
| **Hidden** | 각 검사의 내부 계산 로직(`_check_structural`/`_check_specification_scope`/`_check_design_scope`/`_run_pytest_with_applied_implementation`, `_CHECK_EVALUATORS`의 개별 함수 본문) | 결과값(PASS/FAIL/SKIPPED)만 계약이고, 그 값을 만드는 방법은 Capability 함수 재사용 원칙상 원래도 계약 대상이 아니었음 |
| **Hidden** | `code_review` 필드의 생성 방식(`backend_agent_code_review()` 호출 여부/게이팅 조건) | Evidence 보조 필드로, 이전부터 계약 대상이 아니었고 이번 PR도 이를 계약으로 승격하지 않음 |

> **변경 규칙(ADR-0004 §3.7 재사용)**: Public 항목의 변경(검사 이름
> 추가/삭제, 스키마 필드 추가/삭제/의미 변경, blocking 분류 변경)은
> **RFC → ADC → ADR** 절차를 거친다. Hidden 항목의 변경(개별 검사의
> 판정 로직 개선, 버그 수정, 내부 리팩토링)은 **절차 없이** 가능하다
> — 단, 그 변경이 Public 스키마의 관찰 가능한 출력(반환되는
> `status`/`blocking` 값)을 바꾸지 않는 한에서다.

### 3.1 `KNOWN_CHECK_NAMES` 확장의 명시적 취급

> 향후 새로운 검사 종류(예: Security/Data-API Capability)를
> `KNOWN_CHECK_NAMES`에 추가하는 것은 **Public Contract 변경**이며,
> **RFC → ADC → ADR 대상**이다. 이는 §3 Public 표의 첫 항목에서 직접
> 도출되는 결론이며, 별도 판단 없이 이 RFC가 확정한 규칙을 그대로
> 적용한다(`FREEZE-0001`의 "Security/Data-API Capability는 이번 PR
> 범위 밖"이라는 기존 제약과도 일치).

### 3.2 기존 검사 내부 구현 변경의 명시적 취급

> 기존 4개 검사(`structural`/`specification_scope`/`design_scope`/
> `test_execution`) 각각의 내부 판정 로직을 개선·수정하는 것은
> **Hidden 변경**이며, 그 결과 반환되는 `status`/`blocking` 값의
> 의미가 바뀌지 않는 한 RFC/ADC/ADR 없이 진행할 수 있다. 단, 판정
> 로직 변경이 기존 `status` 값의 **의미**를 바꾸는 경우(예:
> `test_execution`의 `PASS` 기준을 "returncode 0"에서 다른 기준으로
> 바꾸는 경우)는 Public 스키마의 실질적 변경으로 취급하고 §3의 변경
> 규칙을 따른다.

## 4. Contract가 정의하지 않는 것 (경계)

이 Contract는 Stage 간 **"무엇을 주고받는가"만** 정의한다. 다음은
이 Contract의 범위 밖이며, 이 RFC가 규정하지 않는다:

- **Stage 순서** — `contracts.py`의 `validate_*` 함수는 키 존재만
  검사하며 Stage 호출 순서에 대한 어떤 가정도 코드에 없다(01→05
  하드코딩은 `workflow.py`에만 있음, 재확인 완료).
- **Workflow** — 누가 어떤 순서로 Stage를 호출하는지는 Contract가
  아니라 Workflow(현재는 Static, 향후는 Dynamic일 수 있음)의 책임이다.
- **Scheduler/Runtime** — 이 RFC는 어떤 형태로도 Scheduler/Runtime을
  설계하거나 전제하지 않는다(`IMPLEMENTATION_RULES.md` 구현 금지
  목록과 일치).
- **Agent Routing** — 어떤 Agent/Capability가 어떤 Stage를 실행하는지는
  이 Contract가 규정하지 않는다.

> 이 경계 덕분에 Stage Data Contract는 현재의 Static Workflow에도,
> 향후 설계될 어떤 Dynamic Workflow에도 **재검토 없이 재사용
> 가능**하다는 것이 이 RFC의 핵심 주장이다 — 단, 이는 향후 Dynamic
> Workflow RFC가 이 주장을 실제로 검증해야 성립하며, 이 RFC가
> 미리 보증하지 않는다.

## 5. Architecture Impact

- **없음(NONE)** — Runtime/Scheduler/Engine Gateway/Registry/Event
  Bus 등 Frozen 금지 목록에 해당하는 어떤 개념도 요구하지 않는다.
  Stage 01~05의 개수·순서·Capability·Agent는 변경하지 않는다.
- Development HQ Stage Data Contract라는 **새로운 HQ-level Governance
  범주**가 생긴다는 것 자체가 이 RFC의 유일한 Architecture급 결정이며,
  그 소유 구조는 B-2가 규정한다.

## 6. Contract Impact

- **함수 시그니처 변경 없음** — dc879e5가 이미 변경한 시그니처
  (`run_stage_04(stage_01_context, stage_03_output, ...)`,
  `run_stage_05(stage_02_output, stage_04_output, required_checks=None)`)
  는 이 RFC가 사후 승인 대상으로 삼는 기정 사실이며, 이 RFC 자체가
  추가로 시그니처를 바꾸지 않는다.
- **명시적 Public Contract 신설** — §3의 표가 이번 RFC의 실질적
  산출물이다. 신설 전에는 "새 Contract 없음"이 원칙이었고, 신설
  후에는 §3 Public 표가 유일하고 명시적인 계약이 된다.

## 7. Governance 변경 범위 (승인 시)

| 대상 | 변경 내용 |
|---|---|
| 신규 ADC 1건 | 이 RFC의 B-1/B-2/B-3 Decision과 §3 Public/Hidden 경계를 Accept/Not Accepted로 판정 |
| 신규 ADR 1건(ADR-0004 축소 재사용 형식) | §3 Public 표(KNOWN_CHECK_NAMES, 5개 TypedDict 필수 키, required_checks/check_results 스키마, blocking 분류)만 계약으로 문서화. §3의 Hidden 목록과 변경 규칙(§3, §3.1, §3.2)을 그대로 포함 |
| Baseline 신설 절 | B-2에 따라 `hqs/development/BASELINE.md`에 "Stage Data Contract" 절 신설(Development HQ가 소유하는 것은 Contract의 **내용**, 그 **개정 절차**는 상위 Governance가 관리한다는 점을 명시) — 이는 Kernel Public Contract(§14)를 재론하거나 수정하지 않는다 |
| Stage `*.md` 5건 | (문서 정정, 코드 아님) "새 Contract를 만들지 않는다" 문구를 §3의 Public/Hidden 구분을 반영해 갱신 |
| candidate_index 관련 문서/코드 | **변경 없음** — `FREEZE-0001` §5 사전 승인 범위, 이 RFC 밖 |
| Dynamic Workflow/Scheduler/Parser/Agent Routing | **이 RFC에서 설계·채택하지 않음** — §4에서 정의한 "Stage 간 데이터 교환만 규정" 경계만 기록하고, 실제 채택은 별도 RFC 대상으로 남긴다 |

## 8. 기존 RFC/ADC/ADR와의 충돌 검토

- **충돌 없음** — RFC-0007/ADC-0005/ADR-0008 중 어느 것도 Stage 05의
  검사 부분집합 실행이나 형식적 Contract 계층을 이미 규정하거나
  금지하지 않는다. `FREEZE-0001`만이 이번 변경을 절차 대상으로
  지정한다(§4/§7) — 이 RFC는 그 지정에 따른 후속 절차다.
- **재사용 선례**: ADR-0004의 Public/Hidden 5분류·변경 규칙 문언,
  RFC-0007 §3의 "Contract Impact" 서술 형식과 "Stage 출력 구조화는 이
  RFC 밖의 판단"이라는 명시적 이월(이번 RFC가 그 이월을 이어받아
  처리함), ADR-0001~0003의 Baseline 절 번호 삽입 정책(이번 Baseline
  신설 절에도 동일 적용).

## 9. Open Issues (이 RFC가 닫지 않는 질문)

- Hidden으로 분류된 개별 검사 로직이 "판정 기준 자체"를 바꾸는
  경우와 "구현 방식만" 바꾸는 경우의 세부 경계는 후속 ADR 본문에서
  사례별로 추가 확정이 필요할 수 있다.
- Dynamic Workflow가 실제로 이 Contract를 재검토 없이 재사용할 수
  있는지는 별도 RFC가 실증해야 하며, 이 RFC는 가능성만 주장한다.
- Stage Data Contract의 Baseline 신설 절 정확한 절 번호·배치는 ADR
  단계에서 `hqs/development/BASELINE.md` 현재본을 기준으로 확정한다.

## Decision

**후보 C — 분리 승격(Public만 ADR 대상, Hidden은 절차 없이 자유
변경)을 채택한다.** B-1/B-2/B-3 Decision과 §3의 Public/Hidden 경계를
후속 ADC의 판정 대상으로 제출한다 — 결과는
`docs/governance/adc/ADC-0007.md`(Scoped Accept), 후속 반영은
`docs/decisions/adr/ADR-0009-stage-data-contract-baseline.md`.
