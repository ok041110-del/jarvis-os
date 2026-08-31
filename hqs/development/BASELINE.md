# Development HQ Baseline v1.0

## Version

| 항목 | 내용 |
|---|---|
| Version | 1.0.0 |
| Status | Active |
| Architecture State | Frozen |

## Scope

Development HQ는 Jarvis OS Architecture Baseline 위에서 동작하는 첫 번째 Reference HQ이다.

Development HQ는 Architecture를 변경하지 않는다. Development HQ는 Architecture를 검증한다.

## Included Documents

- `README.md`
- `MISSION.md`
- `RESPONSIBILITY.md`
- `BOUNDARY.md`
- `STRUCTURE.md`

## Not Included

- Kernel Design
- Scheduler
- Engine Gateway
- Registry Implementation
- Communication Implementation
- Runtime
- MVP Implementation (별도 `MVP.md` 참조)
- Connector Implementation

## Open Decisions

Development HQ에는 Architecture Open Decision이 존재하지 않는다. Architecture Open Decision은 Jarvis OS의 `docs/decisions/adc/ADC.md`를 참조한다. Development HQ는 Architecture Decision을 소유하지 않는다.

## Stage Data Contract (ADR-0009)

Development HQ Stage 01~05는 서로 데이터를 주고받기 위한 **HQ-level
Public Contract**를 갖는다(`hqs/development/stages/contracts.py`).
이 Contract는 Kernel Public Contract(Jarvis OS Architecture Baseline
§14)와 별개다 — Kernel 전체가 아니라 Development HQ 내부 Stage
사이에서만 성립하며, Kernel Baseline을 확장하거나 대체하지 않는다.

이 Contract의 **내용**(무엇이 Public/Hidden인지)은 이 문서가 소유하지만,
그 **개정 절차**는 Development HQ가 독자 소유하지 않는다 — "Open
Decisions" 절이 명시하는 대로 상위 Jarvis OS Governance(`RFC → ADC →
ADR`)가 관리한다.

**Public**(변경 시 RFC → ADC → ADR 필요):

- 5개 Stage Contract(`ContextAnalysisResult`/`SpecificationResult`/
  `DesignResult`/`ImplementationResult`/`VerificationResult`)의
  필수 키 집합
- `KNOWN_CHECK_NAMES` = `("structural", "specification_scope",
  "design_scope", "test_execution")` — 이 4개로 고정. 이름 추가·삭제
  (Security/Data-API 등 새 검사 종류 포함)는 이 목록의 확장이므로
  예외 없이 별도 RFC → ADC → ADR 대상이다.
- `required_checks` — Stage 05가 실행·판정에 반영할 검사 이름의
  부분집합을 지정하는 파라미터. 빈 값이거나 `KNOWN_CHECK_NAMES` 밖의
  이름을 포함하면 `ContractViolation`으로 거부된다.
- `check_results` 스키마 — `{name, status, blocking, detail}` 형태로
  `KNOWN_CHECK_NAMES` 전체를 항상 나열한다.
- `status` 집합 — `{"PASS", "FAIL", "INCONCLUSIVE", "SKIPPED"}`.
- `blocking` 규칙 — `structural`/`design_scope`/`test_execution`은
  blocking, `specification_scope`는 non-blocking.

**Hidden**(Public 의미를 바꾸지 않는 범위에서 절차 없이 자유 변경):

- 각 검사의 내부 판정 로직(Stage 05 `_check_*`/`_CHECK_EVALUATORS`의
  개별 함수 본문)
- `code_review` 필드의 생성 방식

이 Contract는 Stage 간 **"무엇을 주고받는가"만** 정의한다. Stage
순서, Workflow, Dynamic Workflow, Scheduler, Runtime, Agent Routing은
이 Contract가 규정하지 않으며, 이 절도 이를 정의하지 않는다 — 그
결정은 별도 RFC 대상이다.

근거: `docs/decisions/rfc/RFC-0009-stage-data-contract.md`,
`docs/decisions/adr/ADR-0009-stage-data-contract-baseline.md`.

## Governance

Development HQ 변경은 Jarvis OS Governance를 그대로 따른다.

```
RFC
↓
ADC
↓
ADR
↓
Architecture Baseline Update
↓
Development HQ Baseline Update
↓
Implementation
```

## Final Declaration

> Development HQ Baseline v1.0은 Jarvis OS 위에서 동작하는 첫 번째 공식 Reference HQ이다.
>
> 이 Baseline은 Development HQ의 Mission, Responsibility, Boundary, Structure를 정의한다.
>
> 구현, Kernel, Runtime, MVP는 본 Baseline의 범위가 아니다.
>
> Development HQ는 Jarvis OS Architecture를 수정하기 위해 존재하는 것이 아니라, Jarvis OS Architecture를 현실에서 검증하기 위해 존재한다.
