# GOVERNANCE-REVIEW-0005: C6("별도 스크립트/함수") 구체화 RFC의 필요성 판단

**문서 성격**: Governance Review. **Decision 문서가 아니다.** 새 RFC/ADC/ADR을
작성하지 않는다. 새 Architecture/Concept을 설계하지 않는다. Production
caller를 임의로 설계하거나 Accept하지 않는다. Runtime/Kernel Component
Architecture에 착수하지 않는다. `ADC-0010`을 임의로 Accept하지 않는다.
새 MVP 실험을 만들지 않는다. **이번 검토에서 코드는 한 줄도 작성하지
않았다.**

## 목적

`GOVERNANCE-REVIEW-0004`가 "다음 단 하나의 작업"으로 제시한 **"C6를
구체화하는 새 RFC 착수 여부 판단"**을 실제로 수행한다. 결론이 "필요"면
그 RFC를 작성하고, "불필요"면 이유와 실제 다음 작업을 제시한다. 기존
Evidence(`ADC-0010`, `ADC-0011`, `RFC-0010`, `RFC-0011`,
`GOVERNANCE-REVIEW-0003·0004`, `ENGINE-CONNECT-0002~0006`)와
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준을 한 번에
종합해서 판단한다.

---

## 0. 선결 확인 — "C6를 구체화하는 RFC"는 이미 존재하는가

`GOVERNANCE-REVIEW-0004`를 작성할 때는 `ADC-0010` §부족한 Evidence 6("C6
자체를 구체화하는 새 RFC가 필요하다")만 인용하고, 그 RFC가 이미
작성되었는지를 재확인하지 않았다. 이번 검토에서 `RFC-0011`과 `ADC-0011`
원문을 다시 읽은 결과, **이미 존재한다.**

`RFC-0011-standalone-execution-location-boundary.md` §0가 스스로 밝힌
목적:

> *"C6가 막힌 이유는 C6 자체의 결함이 아니라, C6가 요구하는 더 상위의
> 질문(그런 위치가 Architecture적으로 존재할 수 있는가)이 아직 한 번도
> 열린 적이 없기 때문이다. 이 RFC는 그 상위 질문을 연다 — `ADC-0010`
> §부족한 Evidence 6번("C6 자체를 구체화하는 새 RFC가 필요하다")이 이미
> 요구한 절차다."*

즉 `RFC-0011`은 **정확히 이번 작업이 다시 열려는 것과 같은 RFC**다. 그
후속인 `ADC-0011`은 Boundary Question("Kernel/HQ에 속하지 않는 별도
실행 위치를 공식 Concept으로 둘 수 있는가")에 **Not Accepted (based on
current evidence)**로 답했고, §부족한 Evidence 1~3을 남겼다(재조사하지
않고 그대로 인용):

1. `BASELINE.md` §6 Concept Model이 확장 가능한 분류 체계인지 고정된
   10개인지를 명시하는 문장/Governance 판단 — 없음.
2. `projects/development-hq-devkit` 같은 "Kernel/HQ 밖" 위치가
   Architecture Governance 절차로 공식 검토된 기록 — 없음(Dogfooding
   Testbed로 자기 한정된 상태로만 존재).
3. `BASELINE.md` §7 System Boundary가 두 범주로 책임을 완전히
   소진(exhaustive)하는지, 아니면 "지금까지 정의된 두 범주"일 뿐인지를
   확인할 원 저작 의도 기록(Vision/Principles 단계 문서) — `ADC-0011`
   당시 Evidence 범위 밖으로 남겨짐.

**결론**: "C6를 구체화하는 새 RFC"는 이미 작성되어 ADC까지 완결됐다.
이번 작업이 다시 "C6 RFC"라는 이름으로 새 문서를 쓴다면, 그것은 새
RFC가 아니라 `RFC-0011`/`ADC-0011`의 **재작성**이다 — 이는 이번 작업
지침("ADC-0010을 임의로 Accept하지 말 것", 그리고 일반 원칙인 "이미
Not Accepted로 종결된 판단은 새 Evidence 없이 재론하지 않는다",
`GOVERNANCE-REVIEW-0003`·`ADC-0011` 자신이 반복적으로 적용한 원칙)과
정면으로 충돌한다.

`GOVERNANCE-REVIEW-0004` §④가 "제3 실행 위치 Concept 자체의 존립 여부
| 새 RFC"를 별도 항목으로 나열한 것은 이 사실(RFC-0011이 이미 그 RFC라는
것)을 명시적으로 반영하지 못한 부정확한 서술이었다 — 이 문서에서
정정한다.

---

## 1. 새로 추가된 Evidence가 있는가

`ADC-0011`이 §부족한 Evidence 1~3을 남긴 이후(`ENGINE-CONNECT-0005`,
`ENGINE-CONNECT-0006`, `MVP-0026~0037`, `GOVERNANCE-REVIEW-0004`)
어느 것도 이 세 항목을 충족시키지 않았다 — `GOVERNANCE-REVIEW-0003`이
`ENGINE-CONNECT-0005`에 대해 이미 같은 방식으로 확인한 것과 동일한
결과다.

| 부족한 Evidence(ADC-0011) | 이후 문서가 건드렸는가 | 확인 |
|---|---|---|
| 1. Concept Model 확장 가능성 명시 문장 | 아니오 | `BASELINE.md` §6 어디에도 "10개로 고정" 또는 "확장 가능"이라는 문장이 없음 — 이번 검토에서 재확인(`grep`으로 "확장"/"고정"/"Concept Model" 키워드 대조, 새 판단 추가하지 않음) |
| 2. `projects/development-hq-devkit` 위치의 공식 Governance 검토 기록 | 아니오 | 그런 검토가 열린 기록 없음(`docs/governance/`, `docs/architecture/core/` 전수 확인, 새로 발견된 것 없음) |
| 3. 원 저작 의도(Vision/Principles 문서) | 조건부 — 존재하나 인용 불가 | `archive/v1/Vision.md`가 저장소에 있으나 **Frozen v1.0/v1.4 Baseline 이전의 archive된 v1 설계**다. `CLAUDE.md`·`README.md`가 지정한 유일한 Architecture 원본은 `docs/01_architecture/BASELINE.md`이며, archive 문서를 현재 Baseline의 "원 저작 의도"로 끌어오는 것은 새 Evidence 해석(archive 문서를 현재 Governance 판단에 원용 가능하다는 판단)을 만드는 것 — 이번 작업 권한 밖. 인용하지 않는다 |

**세 항목 모두 미충족.** `ADC-0011`을 재판단할 새 Evidence가 없다.

---

## 2. ADC 채택 기준 대조 — "C6 RFC(재작성)"를 지금 여는 것이 정당한가

`ARCHITECTURE_GOVERNANCE.md` "ADC 채택 기준"을 RFC 재개 여부에도 동일하게
적용한다(RFC는 ADC의 선행 단계이며, 이미 한 번 완결된 RFC를 재개하려면
최소한 ADC 채택 기준과 동등한 근거가 있어야 한다 — 그렇지 않으면 그냥
반복이다).

| 기준 | 충족 여부 | 근거 |
|---|---|---|
| 1. 지금 결정하지 않으면 상위 Architecture를 진행할 수 없다 | **아니오** | Production Implementation은 이번 작업 지침으로도 이미 금지되어 있다("Production 구현은 아직 금지"). Engine MVP는 종료됐고(`GOVERNANCE-REVIEW-0004` §①), caller 위치가 필요 없는 Development HQ Capability Engineering(`GOVERNANCE-REVIEW-0004` §③)은 이 결정과 무관하게 계속 진행 가능하다 — 아무 것도 이 결정을 "기다리며 멈춰" 있지 않다 |
| 2. 결정이 늦어질수록 되돌리는 비용이 매우 커진다 | **아니오** | 아직 어떤 caller도 구현되지 않았다(`ENGINE-CONNECT-0003`·`0004`: Production 코드 변경 0건). 되돌릴 대상 자체가 없으므로 "지연 비용"이 발생하지 않는다 |

**두 조건 모두 불충족.** `ARCHITECTURE_GOVERNANCE.md`: *"두 조건을 만족하지
않으면 해당 사안은 현재 단계에서 다루지 않는다."* — 이 원칙을 그대로
적용하면, 지금 새 RFC를 여는 것은 정당화되지 않는다.

---

## 3. Stop Trigger / 조사 범위 대조

| 확인 항목 | 결과 |
|---|---|
| `ADC-0010`(C1~C6) 재조사 | **없음** — 상태만 인용 |
| `ADC-0011` 재조사 | **없음** — §부족한 Evidence 미충족만 확인, 판단 자체는 그대로 인용 |
| Production 코드 변경 | **없음** |
| 새 RFC/ADC/ADR 작성 | **없음** |
| 새 Architecture/Concept/Component 도입 | **없음** |
| Production caller 위치를 임의로 선택 | **없음** |
| Kernel/Runtime Component Architecture 착수 | **없음** |
| 새 MVP 실험(Evidence 반복 수집) | **없음** — archive 문서 인용 여부도 실험이 아니라 존재 확인만 했다 |

---

## 4. 판단

### C6를 구체화하는 RFC는 필요하지 않다 — 이미 존재하고(`RFC-0011`), 이미 완결됐다(`ADC-0011` Not Accepted)

`GOVERNANCE-REVIEW-0004`가 제안했던 "다음 단 하나의 작업"(C6 구체화 RFC
착수)은, 이번 검토로 **이미 완료된 절차의 재실행 제안이었음이 밝혀졌다.**
새 Evidence 없이 `RFC-0011`/`ADC-0011`을 다시 쓰는 것은 이번 작업
지침(ADC-0010 임의 Accept 금지, 의미 없는 Evidence 반복 금지)과
`ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준(§2) 둘 다에 위배된다.
**RFC를 작성하지 않는다.**

### 실제 다음 작업

Production caller 위치 문제는 지금 **결정할 재료도, 결정해야 할 압력도
없는 상태**다 — `ADC-0011` §부족한 Evidence 1·2·3 중 어느 것도 이번
검토로 채워지지 않았고, 강제로 채울 명분(ADC 채택 기준 §2)도 없다. 이
상태에서 실제로 진행 가능한 것은 `GOVERNANCE-REVIEW-0004` §③이 이미
식별한 것과 같다 — **caller 위치가 필요 없는 트랙**:

- Development HQ Capability Engineering 계속(`development-hq/CONSTITUTION.md`:
  Architecture < Capability < Dogfooding < Observation < Evidence).
- `OBS-0003~0006`(Open) 기반 추가 Dogfooding 관찰 축적.

Production caller 위치 문제는 다음 **둘 중 하나가 실제로 발생할 때만**
다시 열린다(새로 만드는 조건이 아니라, `ADC-0011`이 이미 남긴 조건을
그대로 인용):

1. `ADC-0011` §부족한 Evidence 1~3 중 하나가 **다른 작업의 부산물로
   실제로** 채워질 때(예: Concept Model 확장성에 대한 판단이 다른
   목적의 RFC에서 우연히 다뤄지는 경우) — 이번 작업처럼 그 자체를
   목적으로 삼아 만들지 않는다.
2. `projects/development-hq-devkit`류의 실행이 Dogfooding 목적을
   넘어서려는 시도가 실제로 관찰될 때(`ADC-0010` §부족한 Evidence
   5·C6 판단과 동일한 조건) — 그때 그 관찰 자체가 새 RFC의 근거가
   된다.

**이번 작업에서는 코드도, RFC도, ADC도 추가하지 않는다.** 이 판단
자체(§4)가 이번 작업의 산출물이다.

---

## Self Review

- Evidence만 사용했는가 — **Pass**. `ADC-0010`, `ADC-0011`, `RFC-0010`,
  `RFC-0011`, `GOVERNANCE-REVIEW-0003·0004`, `ARCHITECTURE_GOVERNANCE.md`,
  `BASELINE.md`만 인용했다. `archive/v1/Vision.md`는 존재를 확인만
  했을 뿐 Evidence로 인용하지 않았다(§1, 이유 명시).
- `ADC-0010`을 임의로 Accept했는가 — **아니오**. C1~C6 전부 Not
  Accepted 상태를 그대로 유지했다.
- Production caller를 설계·선정했는가 — **아니오**.
- Kernel/Runtime Component Architecture에 착수했는가 — **아니오**.
- 다른 후보(C1~C5)를 우회하거나 Accept했는가 — **아니오**. 이번
  검토는 C6/ADC-0011 경로만 다뤘고, 그 결과도 "재작성 불필요"였다 —
  다른 후보로 우회하지 않았다.
- 새 RFC를 작성했는가 — **아니오**. §0~§2에서 그 이유를 근거로 남겼다.
- 의미 없는 Evidence 반복을 했는가 — **아니오**. 새 MVP/실험을 만들지
  않았고, `pytest`도 재실행하지 않았다(코드 변경이 없어 회귀 확인
  대상 자체가 없음).
- `GOVERNANCE-REVIEW-0004`의 이전 제안을 정직하게 정정했는가 — **예**.
  §0에서 그 제안이 이미 완료된 절차의 재실행 제안이었음을 명시했다.
- 불필요한 변경을 확인했는가 — **예**. 이 문서 추가 외 다른 파일은
  수정하지 않았다(`git status --porcelain` 확인).
