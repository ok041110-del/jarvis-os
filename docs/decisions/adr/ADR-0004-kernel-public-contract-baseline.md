# ADR-0004: Kernel Public Contract(Context 영역)의 Architecture Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | ADR-0004 |
| 제목 | Kernel Public Contract(범위·책임·보장·은닉·확장점·Non-Goal·변경 규칙)를 Architecture Baseline에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/architecture/core/ADC-0004-kernel-public-contract.md` 판단 1·2·3·4·5a·6·7(전반부)·8 (전부 Accept, 조건부) |
| 관련 RFC | `docs/architecture/core/RFC-0004-kernel-public-contract.md` |
| 관련 ADC | `docs/architecture/core/ADC-0004-kernel-public-contract.md` |
| 선행 ADR | `docs/04_adr/ADR-0002`(절 번호 정책·Freeze 해석), `docs/04_adr/ADR-0003`(§13 신설) |

이 ADR은 ADC-0004가 이미 내린 결정을 다시 논의하지 않는다. 새로운
철학이나 Architecture를 제안하지 않는다. ADC-0004의 Accept 판단을
실제 문서 변경으로 옮기기 위한 **구현 결정**만 기록한다.

**ADC-0004가 붙인 조건은 전부 Baseline 본문에 반영한다.** 조건이 빠진
채 항목만 옮기면 그 조건이 보호하던 기준선(B-1·B-2·B-3)이 무너진다 —
이 ADR은 각 조건의 반영 위치를 §3에서 개별 지정한다.

## Out of Scope (이 ADR이 다루지 않는 것)

| 항목 | 근거 |
|---|---|
| Kernel API(함수·자료형·프로토콜·직렬화) | RFC-0004 §8 — 다음 단계 |
| Extension Point의 메커니즘(등록·발견·로딩·검증) | ADC-0004 판단 5b **Defer** |
| Contract Versioning 체계 | ADC-0004 판단 7 후반부 **Defer** |
| RFC-0002 §15의 미결 3개 책임(Task 전달·Capability 탐색·Engine 호출) | ADC-0004 기준선 B-1 |
| `BASELINE.md` §13.6의 Defer 6건 | ADC-0004 기준선 B-2 — **그대로 유지** |
| Kernel ADC-0001의 Module 판단 5건 | ADC-0004 기준선 B-3 |
| Kernel Architecture 및 Component Design | `BASELINE.md` §10 Out of Scope **유지** |
| Development HQ·Execution Layer의 문서·코드 | ADR-0001·0002·0003 선례. §5에서 충족을 확인한다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/01_architecture/BASELINE.md` | §14 Kernel Public Contract 신설, 기존 §14 Version → §15, v1.2 → v1.3 |
| `docs/00_governance/GLOSSARY.md` | Public Contract 용어 5건 추가, §13 인용 방식 수정(§2.2) |
| `docs/architecture/core/ADC-0002-kernel-definition.md` | Baseline Version 절 인용 방식 수정(§2.2) |

그 외 어떤 파일도 변경하지 않는다.

### 2. `BASELINE.md` 절 번호 정책

ADR-0002 §2.1이 확립하고 ADR-0003 §2가 따른 정책을 그대로 유지한다 —
**기존 절 번호를 재배치하지 않고, 새 절을 Version 앞에 삽입한 뒤
Version을 마지막으로 민다.**

| 절 | 변경 전 | 변경 후 |
|---|---|---|
| §1 ~ §13 | 그대로 | **그대로** |
| Kernel Public Contract | (없음) | **§14 (신설)** |
| Version | §14 | **§15** |

#### 2.1 §13을 인용하는 문서는 전부 그대로 유효하다

조사 결과 `BASELINE.md` §13(Kernel Context Model)을 인용하는 문서는
`GLOSSARY.md` 3건, `ADR-0003` 다수, `ADC-0003` 1건이며, §13의 번호는
바뀌지 않으므로 **전부 갱신이 불필요하다.**

#### 2.2 Version 절 인용 방식을 번호에서 이름으로 바꾼다

Version 절은 **문서 관례상 항상 마지막**이므로, 새 절이 추가될 때마다
번호가 밀린다. 실제로 같은 인용 1건이 ADR-0002(§11→§13)와
ADR-0003(§13→§14)에서 두 번 갱신되었고, 이번에 세 번째 갱신 대상이
된다.

**이 반복 비용을 없애기 위해, Version 절은 번호가 아니라 이름으로
인용한다.**

| 파일 | 변경 전 | 변경 후 |
|---|---|---|
| `docs/architecture/core/ADC-0002-kernel-definition.md` | "§14(판단 당시 §11 → v1.1에서 §13 → v1.2에서 §14)" | "**§Version 절**(당시 §11, v1.2 기준 §14)" |
| `docs/architecture/core/ADC-0003-kernel-context-model.md` | "§13 Version(판단 당시. ADR-0003 반영 후 §14로 이동한다)" | "**§Version 절**(판단 당시 §13)" |

**이것은 과거 기록의 소급 수정이 아니다.** 두 문서가 기록한 사실
(당시 Version·Status·Architecture State 값)은 그대로 두고, **현재
Baseline을 가리키는 포인터의 표기 방식만** 바꾼다. 당시 절 번호는
괄호 안에 보존해 추적 사슬이 끊기지 않게 한다.

**이후 모든 신규 문서는 Version 절을 이름으로 인용한다.**

#### 2.3 ADR-0002·ADR-0003 본문은 갱신하지 않는다

두 문서의 "§13 Version", "§14" 언급은 **각 ADR이 당시 수행한 변경의
기록**이지 현재 Baseline에 대한 참조가 아니다. 과거 기록을 소급
수정하지 않는다는 원칙을 따른다(ADR-0003 §2와 동일한 판단).

### 3. §14 Kernel Public Contract (신설) — 반영할 내용과 조건 배치

ADC-0004가 Accept한 것만 옮긴다. **각 Accept에 붙은 조건의 반영
위치를 여기서 지정한다.**

#### 3.1 계약의 범위 (판단 1)

절 서두에 **"이 계약은 Kernel 전체가 아니라 Context 영역에
한정된다"**를 명시하고, RFC-0002 §15의 8개 책임 중 무엇이 결정되고
무엇이 미결인지를 표로 남긴다. 계약의 수신자(Development HQ,
Execution Layer, 미래 HQ)도 함께 기록한다.

#### 3.2 Public Responsibilities (판단 2 + 조건 3건)

PR-1 ~ PR-4를 옮긴다. 조건 반영:

| 조건 | 반영 위치 |
|---|---|
| PR-1의 "제공 ≠ 내용 마련" 구분 | PR 표 **직후의 별도 문단**으로 배치. 표 각주로 축소하지 않는다 |
| PR-4 명칭을 "Context Rendering **계약 제공**"으로 고정 | 표의 항목명 자체 |
| Public Surface(4개)와 Kernel 책임(§13.2의 4개)은 다른 목록 | PR 표 직후 문단에 명시. §13.2를 대체하지 않는다는 문장 포함 |

#### 3.3 Public Guarantees (판단 3 + 조건 2건)

G-1 ~ G-7을 **"외부의 확인 방법" 열과 함께** 옮긴다 — 그 열이 이
표를 선언이 아니라 계약으로 만든다.

| 조건 | 반영 위치 |
|---|---|
| G-7의 적용 범위를 "Context 경로"로 한정 | G-7 항목 본문에 직접 기입 + 표 아래에 근거(KP-6의 문언, Governance Module Accept와의 관계) 명시 |
| G-4는 관찰로 확인할 수 없다 | G-4의 "확인 방법" 칸과 표 아래 문단 양쪽 |

#### 3.4 Hidden Responsibilities (판단 4 + 효력 문장)

H-1 ~ H-6을 옮기고, **효력 문장을 표 앞에 배치한다**: *"Hidden에
의존한 코드가 Kernel 변경으로 깨지는 것은 계약 위반이 아니다."*
이 문장이 없으면 목록이 아무 일도 하지 않는다.

Hidden과 Extension Point의 3층 구분(교체 가능성 = Public / 계약 =
Public / 구현 = Hidden)도 함께 옮긴다 — 두 목록에 같은 항목이 나오는
이유를 읽는 사람이 알 수 없으면 모순으로 읽힌다.

#### 3.5 Extension Points (판단 5a + 조건 2건)

X-1 ~ X-4를 옮긴다.

| 조건 | 반영 위치 |
|---|---|
| "플러그인 메커니즘이 아니라 계약상의 선언" | 표 **앞**의 인용 블록 |
| X-4는 "확장이 들어올 자리의 표시"이며 확장의 예고가 아니다 | X-4 항목 본문 + 표 아래 문단 |
| X-3은 플러그인이 아니라 입력 경계 | X-3 항목 본문 |

잘못된 확장이 G-1을 깨뜨릴 수 있다는 사실(RFC-0004 §5.3)도 함께
기록하고, 그 강제 메커니즘은 Defer임을 명시한다.

#### 3.6 Explicit Non-Goals (판단 6 + 조건 2건)

N-1 ~ N-6을 옮긴다.

| 조건 | 반영 위치 |
|---|---|
| 6개 전부 Component 수준 서술 | 표의 서술 자체 + 표 **앞**의 인용 블록("Non-Goal은 그 책임이 Kernel에 속하지 않는다는 뜻이 아니다") |
| **"이것이 닫지 않는 질문" 열 유지** | 표의 **필수 열**. 이 열이 B-1·B-3을 보호하는 유일한 장치이므로 축약·삭제하지 않는다 |

#### 3.7 계약의 변경 규칙 (판단 7 전반부)

Public(PR·G·X의 존재와 계약) 변경은 `RFC → ADC → ADR → Baseline`
절차를 따르고, Hidden 변경은 절차 없이 가능하다는 규칙을 옮긴다.
Contract Versioning 체계는 **반영하지 않는다**(Defer).

#### 3.8 미결 항목 표기

§14 말미에 **Defer 2건(확장 메커니즘, Contract Versioning)과 다음
단계(Kernel API)**를 명시한다. §13.6과 동일한 방식이며, Freeze
원칙("미결정 사항이 정직하게 드러나 추적되는 것이 목표")을 따른다.

`BASELINE.md` §13.6의 Defer 6건은 §14에서 **다시 나열하지 않는다** —
Single Source of Truth. 대신 §13.6을 참조한다.

### 4. `GLOSSARY.md` 갱신

"Kernel Public Contract" 절을 신설하고 5개 용어(Public Contract,
Public Responsibility, Public Guarantee, Hidden Responsibility,
Extension Point)를 등재한다. 각 항목은 `BASELINE.md` §14를 정의
출처로 가리킨다 — 상세를 중복 기록하지 않는다.

§2.2에 따라 Version 절을 인용하는 표기가 GLOSSARY에 새로 생기지
않도록 한다.

### 5. Development HQ · Execution Layer 불변 확인

ADC-0004는 어떤 코드 변경도 지시하지 않았다. 이 ADR은 다음을 확인하고
유지한다.

- `development-hq/` 이하 어떤 파일도 변경하지 않는다.
- `core/execution_layer/` 이하 어떤 파일도 변경하지 않는다.
- 42개 테스트는 이번 변경으로 영향을 받지 않는다(문서만 변경).

### 6. `docs/03_adc/ADC.md` 갱신 여부

**갱신하지 않는다.** ADC-0004의 Accept 판단은 전부 결정이며, Defer
2건은 `BASELINE.md` §14 말미와 ADC-0004 자체에 추적 가능한 형태로
기록된다. ADR-0002 §4·ADR-0003 §5와 동일한 판단이다.

**단, ADC-02(Runtime 개념의 존폐)는 Open 상태 그대로 둔다** —
N-1(Runtime 관리 Non-Goal)은 Component 제공 여부만 말하므로 ADC-02를
해소하지 않는다(ADC-0004 판단 6에서 확인).

### 7. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.2 | **v1.3** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: Freeze 원칙은 "변경 불가"가 아니라 "절차를
거치지 않은 변경이 반영되지 않는 상태"를 뜻한다. 이번 변경은
RFC-0004 → ADC-0004 → ADR-0004 절차를 그대로 거쳤다. ADR-0001·0002·
0003의 선례와 동일하다.

**Minor 증가(v1.3)**: 기존 §1~§13의 어떤 문장도 수정하지 않고 새 절
하나를 추가하는 형태이므로, v1.1·v1.2와 같은 규모다.

### 8. Migration Strategy

1. `BASELINE.md` — §14 Kernel Public Contract 삽입, 기존 §14 Version
   → §15 이동 및 v1.3 갱신, 변경 이력 한 줄 추가.
2. `ADC-0002`·`ADC-0003` — Version 절 인용을 이름 기반으로 수정(§2.2).
3. `GLOSSARY.md` — Kernel Public Contract 절 추가(§4).
4. 검증:
   - `BASELINE.md`의 절 번호가 §1~§15로 연속하는지 확인.
   - §13을 인용하는 문서가 그대로 유효한지 확인(§2.1).
   - Version 절을 번호로 인용하는 문서가 남아 있지 않은지 확인
     (ADR-0002·ADR-0003 본문의 역사적 기록은 제외 — §2.3).
   - ADC-0004의 조건 12건이 §14 본문에 실제로 반영되었는지 §3의
     배치표와 대조.
   - `git status`로 `development-hq/`·`core/` 이하에 변경이 없는지
     확인.
   - `python3 -m pytest development-hq/mvp/tests/ core/execution_layer/*/tests/ -q`
     42건 통과 확인.
5. 커밋 — RFC-0004, ADC-0004, ADR-0004와 위 변경을 함께 커밋한다.

---

## Consequences

- `docs/01_architecture/BASELINE.md`가 v1.2 → v1.3이 되고, **Kernel이
  외부에 무엇을 보장하는가**가 Baseline의 일부가 된다.

  | 절 | 답하는 질문 |
  |---|---|
  | §11 | Kernel은 무엇인가 (정의) |
  | §12 | Kernel은 어떻게 설계되어야 하는가 (원칙) |
  | §13 | Kernel은 무엇을 관리하는가 (대상) |
  | **§14** | **Kernel은 외부에 무엇을 보장하는가 (계약)** |

- **계약의 실질적 효력이 생긴다.** Public 항목(PR·G·X)의 변경은
  `ARCHITECTURE_GOVERNANCE.md`의 절차를 거쳐야 하고, Hidden 항목은
  자유롭게 바뀔 수 있다. Baseline 밖에 있는 계약은 이 효력을 갖지
  못하므로, 계약을 Baseline에 두는 것 자체가 결정의 핵심이다.
- **다음 단계(Kernel API)의 판단 기준이 생긴다.** 어떤 API가
  제안되든 "PR-1~PR-4를 제공하는가", "G-1~G-7을 지키는가",
  "H-1~H-6을 노출하지 않는가"로 검토할 수 있다.
- **미결 사안은 전부 미결로 남는다.** RFC-0002 §15의 3개 책임,
  §13.6의 Defer 6건, Kernel ADC-0001의 Defer 3개 Module 어느 것도
  이 ADR이 닫지 않는다. §3.6의 "닫지 않는 질문" 열이 그 사실을
  Baseline 본문에 남긴다.
- **Kernel Architecture는 여전히 설계되지 않는다** — §10 Out of
  Scope가 유지되고, §14는 Component를 하나도 정의하지 않는다(KP-1).
- **Development HQ와 Execution Layer는 한 글자도 변경되지 않는다.**
- Version 절 인용이 이름 기반으로 바뀌어, 이후 Baseline에 절이
  추가될 때마다 발생하던 인용 갱신 비용이 사라진다(§2.2).
- 남는 절차 부채를 정직하게 기록한다.
  1. ADC-0004 Defer 2건(확장 메커니즘, Contract Versioning). 전자의
     재검토 조건은 **두 번째 Renderer 또는 두 번째 Ordering Policy가
     실제로 필요해지는 시점**이다.
  2. **계약은 있으나 그것을 구현하는 Kernel은 아직 없다.** "보장은
     있으나 보장하는 주체가 없는" 상태가 API 설계·구현 단계까지
     지속된다. 이것이 이번 결정이 만드는 가장 큰 부채다.
  3. ADC-0004 판단 6의 Risks: "닫지 않는 질문" 열이 향후 편집에서
     소실되면 이 표는 미결 사안을 조용히 닫는 문서가 된다. 문서
     관행으로만 막을 수 있으며 구조적으로 해소되지 않는다.
  4. ADR-0002·ADR-0003이 남긴 부채(디렉토리·파일명의 `core/`,
     Kernel ADC-0001의 미작성 ADR 2건, ADC-0003 Defer 4건)는 이
     ADR이 해소하지 않는다.
- 이 ADR은 **승인되었으며**, §8에 정의된 실제 파일 변경이 이 승인에
  따라 실행된다.
