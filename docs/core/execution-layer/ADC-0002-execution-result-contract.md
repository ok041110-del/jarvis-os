# ADC-0002: Execution Result Contract — 3개 후보 판단 (RFC-0002 후속)

## 목적

`docs/core/execution-layer/RFC-0002-execution-result-contract.md`가
제기한 Boundary Question — "여러 Engine 산출물을 하나의 Execution
Result로 어떻게 묶는가?" — 에 대해, RFC-0002가 인용한 3개 후보(단일
불투명 문자열 / 산출물 목록 / 참조만 담고 내용은 밖) 중 무엇을 채택할지
판단한다.

근거는 RFC-0002와 그것이 인용한 Evidence(`IMPL-STOP-0001`,
`ARTIFACT-STANDARD-v1.md`, `ENGINE-INTEGRATION-0001~0003`)로만
한정한다. 새로운 Evidence를 만들지 않는다.

### 이 ADC가 답하지 않는 것

이 ADC는 다음을 판단하지 않는다.

- 채택된 후보의 실제 필드 구성(이름, 타입, 개수).
- 산출물 항목의 타입 스키마(파일/로그/텍스트 보고를 어떻게 구분하는지).
- Execution Result Builder의 구현 방법.
- Candidate 3이 요구하는 저장 위치(Memory 영역)의 설계.
- `call_engine()`의 실제 Engine 배선 여부(별도 사안,
  `ENGINE-CONNECT-0001`).
- Execution State의 상태 전이 규칙(별도 사안).

이 ADC가 판단하는 것은 오직 하나다: **RFC-0002의 3개 후보 중 현재
확보된 Evidence로 무엇을 채택할 수 있는가?**

---

## Q0. Candidate 1(단일 불투명 문자열)은 Evidence로 지지되는가?

### Evidence

- `ENGINE-INTEGRATION-0001~0003` 세 실험 모두 Engine이 만들어내는
  산출물을 **"여러 개별 산출물"**(신규 파일, 로그, 텍스트 보고, diff,
  파일 수정)로 관찰했다(RFC-0002 §2 Evidence Summary).
  `ENGINE-INTEGRATION-0001` 157~160행: *"이번 실험은 '여러 개별
  산출물'(신규 파일, 로그, 텍스트 보고)만 만들었을 뿐, 그것을 하나의
  단일 Execution Result Artifact로 묶는 방식은 관찰되지 않았다."*
- 세 실험 중 어디에서도 Engine의 산출물이 이미 단일 텍스트로
  자연스럽게 환원된 사례는 관찰되지 않았다 — 세 문서 모두 산출물을
  복수형("여러", "각각")으로 기술했다(RFC-0002 §2, §3 Pattern).

### Q0 결론(Evidence 기반)

세 실험이 공통으로 관찰한 사실은 산출물의 **복수성**이다. Candidate
1(단일 불투명 문자열)은 "산출물이 하나의 텍스트로 환원 가능하다는
결정"(RFC-0002 §4 인용)을 전제하는데, 이 전제를 지지하는 관찰이 세
실험 어디에도 없다. **Not Accepted** — 현재 Evidence는 이 후보와
직접 배치된다.

---

## Q1. Candidate 3(참조만 담고 내용은 밖)은 Evidence로 지지되는가?

### Evidence

- RFC-0002 §4가 인용한 `IMPL-STOP-0001` §2 E-4 표: Candidate 3을
  선택하면 *"저장 위치가 필요해진다 → Memory 영역(Defer)"*이라고
  명시했다.
- RFC-0002·`IMPL-STOP-0001`·`ARTIFACT-STANDARD-v1.md`·
  `ENGINE-INTEGRATION-0001~0003` 중 어디에도 Memory 영역의 저장 위치
  설계, 참조 형식(ID, 경로, URI 등), 또는 그 영역이 현재 결정 가능한
  상태라는 관찰이 없다.

### Q1 결론(Evidence 기반)

Candidate 3은 그 자체로 "저장 위치"라는 새로운 Architecture 결정을
전제하며, 이 전제는 인용된 Evidence 안에서 이미 **Defer**로
표시되어 있다(`IMPL-STOP-0001` §2 E-4 자체 인용). 이 ADC는 RFC-0002가
인용한 Evidence만 사용하므로, Defer 상태인 전제 위에 결정을 내릴
근거가 없다. **Not Accepted** — 현재 Evidence로는 이 후보를 채택할
수 없다(Memory 영역 결정이 선행되어야 하며, 그 결정은 이 ADC의 범위
밖이다).

---

## Q2. Candidate 2(산출물 목록)는 Evidence로 지지되는가?

### Evidence

- Q0에서 확인한 바와 같이, 세 실험 모두 산출물을 **복수** 항목(신규
  파일, 로그, 텍스트 보고, diff, 파일 수정)으로 관찰했다. Candidate
  2("산출물 목록")는 이 관찰과 형태상 직접 대응한다 — 관찰된 산출물의
  복수성을 압축·환원하지 않고 그대로 반영한다.
- RFC-0002 §4 인용: Candidate 2를 선택하면 "Artifact가 복수 항목을
  담는 첫 사례 — 5개 Builder의 단일 텍스트 구조를 벗어난다." 이는
  기존 Contract 패턴(`ARTIFACT-STANDARD-v1.md`의 "Wrap, not
  rewrite", 5개 Builder 모두 `str -> str`)과의 구조적 차이를
  스스로 인정한 조건이며, 이 ADC는 그 차이를 숨기지 않는다.
- 이 구조적 차이가 Kernel 수준의 새 Layer/Component/Concept을
  요구한다는 관찰은 Evidence 안에 없다 — `IMPL-STOP-0001` §3
  Stop Trigger 대조표에서 Trigger 3(새 Registry/Gateway/Scheduler/
  Runtime 요구)은 미발동으로 기록되어 있다. Candidate 2는 Execution
  Result라는 기존에 예고된 여섯 번째 Artifact 내부의 필드 형태
  결정이며, 새 Registry/Gateway/Scheduler/Runtime을 요구하지 않는다.

### Q2 결론(Evidence 기반)

Candidate 2는 세 실험이 공통으로 관찰한 산출물의 복수성과 직접
대응하며, Q0(Candidate 1 배제)·Q1(Candidate 3 배제) 이후 RFC-0002가
한정한 3개 후보 중 유일하게 남는다. 이 구조는 기존 5개 Builder의
단일 텍스트 패턴과 다르지만, 그 차이가 Kernel 수준의 새 Architecture
(Layer/Component/Concept)를 요구한다는 관찰은 없다.

---

## Decision

**Accepted (based on current evidence): Candidate 2 — 산출물 목록
(Execution Result는 복수 산출물의 목록을 담는다).**

### Reason

세 실험(`ENGINE-INTEGRATION-0001~0003`)이 공통으로 관찰한 산출물의
복수성을 가장 직접적으로 반영하는 후보이며, Candidate 1은 그 관찰과
배치되고 Candidate 3은 Evidence 안에서 이미 Defer로 표시된 전제
(Memory 영역)를 필요로 한다.

## Decision Rationale

Q0은 Candidate 1이 "산출물이 하나의 텍스트로 환원 가능하다"는
전제를 요구하지만 세 실험 모두 복수 산출물을 관찰했다는 점에서 이
전제가 성립하지 않음을 확인했다. Q1은 Candidate 3이 요구하는 저장
위치 결정이 인용 Evidence 안에서 이미 Defer 상태로 표시돼 있어, 이
ADC의 Evidence 범위 안에서는 채택할 수 없음을 확인했다. Q2는 남은
Candidate 2가 세 실험의 공통 관찰(복수 산출물)과 형태상 직접
대응하고, 그 구조적 차이(첫 목록형 Artifact)가 Kernel 수준의 새
Architecture를 요구한다는 관찰이 없음을 확인했다.

## Risks

- 이 Decision은 RFC-0002가 이미 한정한 3개 후보(단일 문자열/목록/
  참조) 안에서의 배제법(elimination)에 근거한다 — Candidate 2가
  "최선"이라는 적극적 증거라기보다, 나머지 두 후보가 각각 직접
  반증(Q0)·전제 미충족(Q1)으로 배제된 결과다.
- Q0·Q1·Q2가 근거로 삼은 관찰은 세 실험 모두 **동일 계열의 작업**
  (코드 리뷰/생성형 작업, 새 파일·로그·텍스트 보고)에서 나온
  것이다(RFC-0001 Risks 절과 동일한 종류의 제약). 다른 성격의 작업
  (예: 순수 조회, 실패로 끝난 실행)에서도 "복수 산출물" 관찰이
  재현되는지는 확인되지 않았다.
- Candidate 2가 실제 필드 구조(목록 항목의 타입, 최소/최대 개수,
  빈 목록 처리)로 구체화될 때 새로운 Architecture 질문이 나타날 수
  있다 — 이 ADC는 그 구체화를 다루지 않았다.

**재검토 조건**: 위 Risks에서 언급한 상황(다른 성격의 작업에서 산출물이
단일 텍스트로 관찰되는 경우, 또는 목록 항목 구체화 과정에서 Kernel
수준 Architecture가 필요해지는 경우)이 실제로 관찰되면, 이 Decision은
기존 Governance 절차(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`:
RFC → ADC → ADR → Baseline Update)를 통해 재검토 대상이 된다.

## Next Step

**ADR 필요** — 이 Decision은 Execution Result가 기존 5개 Builder의
단일 텍스트(`str -> str`) 패턴과 다른 구조(목록)를 갖는다는 것을
채택했으며, 이는 `ARTIFACT-STANDARD-v1.md`가 "예고만 하고 설계하지
않는다"고 남겨둔 여섯 번째 Artifact의 자리에 처음으로 형태를
부여한다. `ARTIFACT-STANDARD-v1.md`를 Baseline으로 갱신하려면 ADR이
필요하다. 이 ADC는 ADR을 작성하지 않는다 — 별도 단계로 진행한다.

Candidate 2의 실제 필드 구성(목록 항목의 타입 스키마 등)은 이 ADC의
권한 범위가 아니며, ADR 또는 후속 구현 단계에서 다뤄야 한다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**. 이 ADC는 기존
  RFC-0002가 한정한 3개 후보 중 하나를 선택했을 뿐이다.
- 새로운 Layer가 추가되었는가 — **아니오**.
- 새로운 Component가 추가되었는가 — **아니오**.
- 새로운 Concept이 추가되었는가 — **아니오**. "산출물 목록"은
  RFC-0002가 이미 제시한 후보이며 이 ADC가 새로 만든 개념이 아니다.
- Baseline 문서(`ARTIFACT-STANDARD-v1.md`)를 변경했는가 — **아니오**.
  이 ADC는 Baseline을 직접 수정하지 않는다.
- ADR이 필요한가 — **예**. §Next Step 참고. 이 ADC 자체는 ADR을
  작성하지 않는다.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0002와 그것이 인용한
  `IMPL-STOP-0001`, `ARTIFACT-STANDARD-v1.md`,
  `ENGINE-INTEGRATION-0001~0003`만 인용했다. 새 실험은 하지 않았다.
- 새 후보를 만들었는가 — **아니오**. RFC-0002의 3개 후보만
  비교했다.
- Q0 → Q1 → Q2 순서를 지켰는가 — **Pass**. Candidate 1 배제 →
  Candidate 3 배제 → 남은 Candidate 2 확인 순으로 진행했다.
- 필드 구조를 설계했는가 — **아니오**. 목록이라는 형태만 채택했고,
  항목 스키마는 다루지 않았다(§목적 "이 ADC가 답하지 않는 것").
- Memory 영역을 설계했는가 — **아니오**. Candidate 3을 배제하는
  근거로만 인용했다.
- ADR을 작성했는가 — **아니오**.
- Baseline(`ARTIFACT-STANDARD-v1.md`)을 수정했는가 — **아니오**.
- 구현을 제안했는가 — **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**. Q2에서 확인한
  구조적 차이(목록형 Artifact)는 RFC-0002가 이미 인지하고 인용한
  것(§4 표)이며, 이 ADC가 새로 발견한 문제가 아니다.
