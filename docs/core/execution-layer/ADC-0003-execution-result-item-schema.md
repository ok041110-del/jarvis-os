# ADC-0003: Execution Result Item Schema — 항목 타입 판단 (RFC-0003 후속)

## 목적

`docs/core/execution-layer/RFC-0003-execution-result-item-schema.md`가
제기한 Boundary Question — "Execution Result 목록의 각 항목은 어떤
타입인가?" — 에 대해, RFC-0003이 인용한 2개 후보(`list[str]` /
`list[dict]`) 중 무엇을 채택할지 판단한다.

근거는 RFC-0003과 그것이 인용한 Evidence(`IMPL-STOP-0002`,
`ADC-0002`, `ADR-0001`, `ARTIFACT-STANDARD-v1.md`, 기존 5개 Builder
소스)로만 한정한다. 새로운 Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

이 ADC는 다음을 판단하지 않는다.

- `list[dict]`을 채택할 경우의 실제 필드 이름·타입.
- 목록의 빈 목록 허용 여부, 최소/최대 개수.
- 산출물의 의미론적 종류(파일/로그/텍스트 보고 등)를 어떻게
  구분할지 — 항목이 문자열이라는 것과, 그 문자열이 무엇을
  의미하는지는 다른 질문이다.
- Execution Result Builder의 실제 구현.
- `call_engine()`의 실제 Engine 배선 여부, Execution State의 상태
  전이 규칙(별도 사안).

이 ADC가 판단하는 것은 오직 하나다: **RFC-0003의 2개 후보 중 현재
확보된 Evidence로 무엇을 채택할 수 있는가?**

---

## Q0. Candidate `list[dict]`(구조화 레코드)는 Evidence로 지지되는가?

### Evidence

- `core/execution_layer/mvp_0001~0005/*.py` 전수 확인 결과, 5개
  Builder의 입력·출력·모든 keyword 메타데이터 인자가 예외 없이
  `str`이다(RFC-0003 §2 표). 구조화(dict/list/객체) 타입의 필드는
  5개 Builder 전체에서 한 건도 관찰되지 않았다.
- `list[dict]`을 채택하려면 `type`/`source`/`content` 같은 **필드
  이름**과, 그 필드가 구분해야 할 **산출물 종류의 닫힌 집합**(예:
  파일/로그/텍스트 보고)을 정해야 한다(`IMPL-STOP-0002` §2 E-3:
  "명백한 새 스키마 결정 — '파일/로그/텍스트 보고를 어떻게
  구분하는지' 그 자체"). 인용된 Evidence 어디에도 이 필드 이름이나
  종류 집합을 뒷받침하는 관찰이 없다 — `ADC-0002`·`ADR-0001` 둘 다
  이를 명시적으로 판단 범위 밖에 두었을 뿐(RFC-0003 §2), 어떤
  구체적 필드나 종류도 제시한 적이 없다.
- Execution State의 `state` 필드가 5개 허용값의 닫힌 집합
  (PENDING/RUNNING/COMPLETED/FAILED/CANCELLED)으로 검증되는 선례가
  있으나(`ARTIFACT-STANDARD-v1.md` Artifact 5), 이 선례는 "상태"라는
  이미 정의된 도메인에 한정된 것이며, "산출물 종류"라는 다른
  도메인에 그대로 옮길 수 있다는 근거가 없다.

### Q0 결론(Evidence 기반)

`list[dict]`을 채택하려면 필드 이름과 산출물 종류의 닫힌 집합이라는
최소 두 가지 새 사실을 확정해야 하는데, 인용된 Evidence 안에는 그
근거가 전혀 없다. **Not Accepted** — 현재 Evidence로는 이 후보를
채택할 수 없다.

---

## Q1. Candidate `list[str]`(opaque 문자열)은 Evidence로 지지되는가?

### Evidence

- 5개 Builder의 입력·출력·메타데이터 인자 전부가 예외 없이 `str`
  이다(Q0와 동일 Evidence, RFC-0003 §2 표). `list[str]`은 이 100%
  일관된 패턴에 "목록"이라는, `ADC-0002`가 **이미 결정한** 컨테이너
  형태 하나만 결합한 것이다.
- `IMPL-STOP-0002` §2 E-3은 `list[str]`이 요구하는 결정을 "항목은
  문자열이다"라는 **단일 사실**로 명시했다 — `list[dict]`이 요구하는
  복수의 새 사실(필드 이름, 종류 집합)과 대비된다.
- `list[str]`을 채택해도 "그 문자열이 의미론적으로 무엇을 나타내는지
  (파일/로그/텍스트 보고 구분)"는 여전히 결정되지 않는다 — opaque
  문자열은 내용을 해석하지 않으며, 이는 기존 5개 Builder의 "Wrap,
  not rewrite"(입력 내용을 해석하지 않음) 원칙과 정확히 같은
  성격이다(`ARTIFACT-STANDARD-v1.md` "공통 패턴").

### Q1 결론(Evidence 기반)

`list[str]`은 이미 Accepted된 사실(5개 Builder의 str-only 패턴,
`ADC-0002`의 list 형태 결정) 두 가지를 결합하는 것 외에 어떤 새
사실도 요구하지 않는다. Q0에서 유일한 대안이 배제된 뒤 남는 후보이며,
Evidence와 직접 부합한다. **Accepted (based on current evidence)**.

---

## Decision

**Accepted (based on current evidence): `list[str]` — Execution
Result는 opaque 문자열의 목록을 담는다. 각 문자열의 의미론적 종류
(파일/로그/텍스트 보고 등 구분)는 이 Decision이 다루지 않는다.**

### Reason

`list[dict]`은 필드 이름과 산출물 종류의 닫힌 집합이라는, 인용된
Evidence가 전혀 뒷받침하지 않는 두 가지 새 사실을 요구해 배제된다
(Q0). `list[str]`은 이미 Accepted된 두 사실(5개 Builder의 str-only
패턴, ADC-0002의 list 형태)을 결합하는 것 외에 추가 결정을 요구하지
않는다(Q1).

## Decision Rationale

Q0은 `list[dict]`이 요구하는 필드 스키마·종류 분류가 Evidence
안에서 전혀 근거를 갖지 못함을 확인했다. Q1은 `list[str]`이 기존에
이미 결정된 두 사실(str-only 패턴, list 형태)의 단순 결합이며 추가
불확실성을 도입하지 않음을 확인했다. 두 판단 모두
`ARCHITECTURE_GOVERNANCE.md`의 Good Architecture Principle("필요한
것만 적절한 시점에 결정한 Architecture")과 일치한다 — 필요 이상의
구조(닫힌 종류 집합, 필드 스키마)를 지금 결정하지 않는다.

## Risks

- 이 Decision은 "opaque 문자열"이라는 최소 결정이며, 산출물의
  의미론적 종류를 구분해야 하는 실제 필요가 나타나면 Contract를
  다시 열어야 한다. 이는 새 결정이 아니라 이 Decision이 처음부터
  다루지 않기로 한 것을 재확인한 것이다.
- `list[dict]`을 배제한 근거(§Q0)는 "현재 Evidence 안에 근거가
  없다"는 것이지, "구조화 레코드가 틀렸다"는 적극적 반증이 아니다
  — `ADC-0002` Q1(Candidate 3 배제)과 같은 종류의 판단이다.
- Q0·Q1이 근거로 삼은 5개 Builder의 str-only 패턴은 Execution
  Request~Execution State(요청 계열 Artifact)에서 관찰된 것이며,
  Execution Result(산출물 계열 Artifact)에 그대로 적용될 수 있다는
  것은 유추이지 직접 관찰이 아니다.

**재검토 조건**: 산출물의 종류를 실제로 구분해야 하는 필요가
관찰되거나(예: 파일/로그/텍스트 보고를 다르게 처리해야 하는 Consumer
가 나타남), `list[str]`이 실제 사용에서 부족하다는 Evidence가
확보되면, 이 Decision은 기존 Governance 절차(`ARCHITECTURE_GOVERNANCE.md`:
RFC → ADC → ADR → Baseline Update)를 통해 재검토 대상이 된다.

## Next Step

**ADR 필요** — 이 Decision은 Execution Result의 목록 항목이
`str`이라는 것을 채택했으며, `ARTIFACT-STANDARD-v1.md` "Artifact 6:
Execution Result" 절의 "Canonical Fields: 미정(ADC-0002 범위 밖)"을
`list[str]`로 구체화한다. 이 ADC는 ADR을 작성하지 않는다 — 별도
단계로 진행한다.

`results`의 빈 목록 허용 여부·개수 제한, 문자열의 의미론적 종류
구분은 이 ADC의 권한 범위가 아니며, ADR 또는 후속 구현 단계에서
다뤄야 한다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**. 이 ADC는 기존
  RFC-0003이 한정한 2개 후보 중 하나를 선택했을 뿐이다.
- 새로운 Layer가 추가되었는가 — **아니오**.
- 새로운 Component가 추가되었는가 — **아니오**.
- 새로운 Concept이 추가되었는가 — **아니오**. `list[str]`은
  RFC-0003이 이미 제시한 후보이며 이 ADC가 새로 만든 개념이 아니다.
- Baseline 문서(`ARTIFACT-STANDARD-v1.md`)를 변경했는가 — **아니오**.
  이 ADC는 Baseline을 직접 수정하지 않는다.
- ADR이 필요한가 — **예**. §Next Step 참고. 이 ADC 자체는 ADR을
  작성하지 않는다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0003과 그것이 인용한
  `IMPL-STOP-0002`, `ADC-0002`, `ADR-0001`, `ARTIFACT-STANDARD-v1.md`,
  5개 Builder 소스만 인용했다. 새 실험은 하지 않았다.
- 새 후보를 만들었는가 — **아니오**. RFC-0003의 2개 후보만
  비교했다.
- Q0 → Q1 순서를 지켰는가 — **Pass**. Candidate `list[dict]` 배제
  → 남은 Candidate `list[str]` 확인 순으로 진행했다.
- 필드 이름이나 산출물 종류를 설계했는가 — **아니오**(§목적 "이
  ADC가 답하지 않는 것").
- ADR을 작성했는가 — **아니오**.
- Baseline(`ARTIFACT-STANDARD-v1.md`)을 수정했는가 — **아니오**.
- 구현을 제안했는가 — **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**. Q0·Q1에서
  다룬 두 후보는 RFC-0003·IMPL-STOP-0002가 이미 식별한 것이며,
  이 ADC가 새로 발견한 문제가 아니다.
