# ADR-0005: Kernel Logical Reference Architecture의 Baseline 반영과 §10 범위 한정

| 필드 | 내용 |
|---|---|
| ID | ADR-0005 |
| 제목 | Kernel Logical Reference Architecture를 Architecture Baseline에 반영하고, §10 Out of Scope의 "Kernel Architecture"를 "Kernel Component Architecture"로 한정하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/architecture/core/ADC-0005-kernel-logical-reference-architecture.md` 판단 1(Gating, Accept·조건 4건)~판단 8 (전부 Accept, 5건 조건부) |
| 관련 RFC | `docs/architecture/core/RFC-0005-kernel-logical-reference-architecture.md` |
| 관련 ADC | `docs/architecture/core/ADC-0005-kernel-logical-reference-architecture.md` |
| 선행 ADR | ADR-0002(절 번호 정책·Freeze 해석), ADR-0003(§13 신설), ADR-0004(§14 신설·인용 방식) |

이 ADR은 ADC-0005가 이미 내린 결정을 다시 논의하지 않는다. ADC-0005의
Accept 판단을 실제 문서 변경으로 옮기기 위한 **구현 결정**만 기록한다.

**이 ADR은 선행 3건과 성격이 다르다.** ADR-0002·0003·0004는 전부
**새 절 추가**만 수행했으나, 이 ADR은 **기존 절(§10)의 문언을
변경**한다. 그 특수성을 §2에서 별도로 다룬다.

## Out of Scope (이 ADR이 다루지 않는 것)

| 항목 | 근거 |
|---|---|
| **Kernel Component Architecture** | ADC-0005 판단 1 조건 1 — §10에 **남긴다** |
| Kernel API·클래스 구조·DI·Runtime 구현 | RFC-0005 §8 — 다음 단계. **이번 Accept를 선례로 삼지 않는다**(판단 1 조건 3) |
| 배선도의 ②Merge → ③Validate 구체 배치 | ADC-0005 판단 2b — 예시로만 |
| Execution Layer 기존 Builder에 대한 RR-4 적용 | ADC-0005 판단 5b 조건 2 |
| R-3의 상태 변경 | ADC-0005 판단 5b 조건 3 — ADC-0003 판단 5 그대로 |
| 확장 메커니즘(등록·발견·로딩·검증) | ADC-0004 판단 5b Defer |
| §13.6·§14.7의 Defer 8건 | ADC-0005 기준선 B-2 — 그대로 유지 |
| RFC-0002 §15의 미결 3개 책임 | ADC-0005 기준선 B-1 |
| Development HQ·Execution Layer의 문서·코드 | §6에서 충족을 확인한다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/01_architecture/BASELINE.md` | **§10 문언 변경**, §15 Kernel Reference Architecture 신설, 기존 §15 Version → §16, v1.3 → v1.4 |
| `docs/00_governance/GLOSSARY.md` | Reference Architecture 용어 추가 |

그 외 어떤 파일도 변경하지 않는다. **§10을 인용하는 5건의 처리는
§2.3에서 별도로 판단한다.**

### 2. §10 문언 변경 — 이 ADR의 가장 민감한 부분

#### 2.1 변경 내용

| 변경 전 | 변경 후 |
|---|---|
| `- Kernel Architecture` | `- Kernel Component Architecture (Component의 존재·설계·상호작용 구조)` |

**나머지 4개 항목(Component Design / Workflow Runtime 내부 구조 /
Development HQ 내부 설계 / Implementation)은 한 글자도 바꾸지
않는다.**

그리고 §10에 **무엇이 더 이상 Out of Scope가 아닌지**를 명시하는 한
문단을 추가한다. 이것이 없으면 §10을 읽는 사람이 무엇이 열렸는지 알
수 없다.

#### 2.2 이 변경이 넘지 않는 선

ADC-0005 판단 1의 조건 4건을 문서 변경으로 옮긴다.

| 조건 | 반영 방법 |
|---|---|
| 조건 1: Component Architecture는 계속 Out of Scope | §10 항목명에 **"Component"**를 남긴다. 괄호로 그 범위(존재·설계·상호작용 구조)를 명시한다 |
| 조건 2: 여는 범위는 "이미 결정된 책임들의 논리적 연결"로 한정 | §10 추가 문단에 이 한정 문구를 그대로 적는다 |
| 조건 3: 다음 단계(API)의 선례로 삼지 않는다 | §10 추가 문단과 §15 말미 양쪽에 명시한다 |
| 조건 4: C-1~C-3 충족 확인 | ADC-0005 판단 2·4·5가 확인 완료. §15 서두에 "이 절은 새 책임·Model 요소·Component를 만들지 않는다"를 명시한다 |

**이것은 Frozen 절의 기존 문장을 바꾸는 첫 사례다**(ADC-0005 판단 8
Risks). 그 선례가 오용되지 않도록, 이 ADR은 변경 범위를 **한 항목의
문언 한정 + 설명 문단 추가**로 제한하며, §10의 다른 항목·다른 절의
문장은 건드리지 않는다.

#### 2.3 §10을 인용하는 5건의 처리

조사 결과 `BASELINE.md` §10을 인용하는 문서는 다음과 같다.

| 문서 | 인용 내용 | 처리 |
|---|---|---|
| `RFC-0001-jarvis-os-core-baseline.md` (2건) | "§10: Kernel Architecture, ..." | **갱신하지 않음** — 당시 문언에 대한 역사적 기록 |
| `GOVERNANCE-REVIEW-0001-post-adc-0001.md` (1건) | "§10은 Kernel Architecture와 Component Design을 Out of Scope로 남겨 두었다" | **갱신하지 않음** — 그 시점의 평가 근거이며, ADC-0005 판단 1이 이 문장을 그대로 인용해 판단했다. 바꾸면 판단의 근거가 사라진다 |
| `ADC-0002-kernel-definition.md` (2건) | "§10 Out of Scope(Kernel Architecture)" | **갱신하지 않음** — 판단 당시의 근거 기록 |
| `RFC-0003`·`RFC-0004`·`ADC-0003`·`ADC-0004` | "§10 Out of Scope 그대로 유지" | **갱신하지 않음** — 각 문서 작성 시점의 사실 |

**5건 전부 갱신하지 않는다.** 이유는 하나다 — 이들은 **각 문서가
작성된 시점의 §10을 근거로 삼은 기록**이며, 소급 수정하면 그 판단들이
무엇을 근거로 내려졌는지 추적할 수 없게 된다. 과거 기록을 소급
수정하지 않는다는 이 프로젝트의 원칙(ADR-0002 §1 Category C,
ADR-0003 §2, ADR-0004 §2.3)을 따른다.

대신 **§10의 변경 이력을 §Version 절의 v1.4 항목에 남겨**, 과거 인용을
읽는 사람이 문언이 언제 왜 바뀌었는지 찾을 수 있게 한다.

### 3. §15 Kernel Reference Architecture (신설) — 반영 내용과 조건 배치

ADC-0005가 Accept한 것만 옮긴다. 조건의 반영 위치를 지정한다.

#### 3.1 서두 — 이 절의 성격 (판단 1 조건 4)

**"이 절은 새 책임·새 Model 요소·새 Component를 만들지 않는다.
이미 §13·§14가 결정한 것들이 어떻게 연결되는지를 기록한다."**
그리고 §10과의 관계(무엇이 열렸고 무엇이 닫혀 있는가)를 명시한다.

#### 3.2 Responsibility Flow (판단 2·2b·3)

배선도와 6개 단계의 책임표를 옮긴다.

| 조건 | 반영 위치 |
|---|---|
| 순서 최소 진술만 Accept — "검증은 Assemble 이전에 완료" | 배선도 **아래 별도 문단**. 배선도의 ②→③ 배치는 **"가능한 배치 하나의 예시"**임을 같은 문단에 명시 |
| 구체 배치는 H-2(Hidden) | 위 문단에 함께 기록 |
| Kernel 경계선 배치(판단 3) | 배선도의 경계선 + 경계 배치표 |

#### 3.3 Data Flow (판단 4 + 조건 2건)

| 조건 | 반영 위치 |
|---|---|
| 5개 중간 상태는 §13.1의 Model 요소가 아니다 | Data Flow 표 **앞**의 인용 블록. 표 각주로 축소하지 않는다 |
| Render의 Content 불변은 "Content를 쓰지 않는다"는 뜻이며 R-4의 고정 구조 틀 추가를 금지하지 않는다 | Data Flow 표 아래 문단 |

#### 3.4 Responsibility Relationship (판단 5·5b)

관계표와 RR-1~RR-4를 옮긴다. 명칭이 "Component"가 아니라
"Responsibility"인 이유(KP-1)를 함께 기록한다.

| 조건 (RR-4) | 반영 위치 |
|---|---|
| RR-4는 Kernel Reference Architecture의 ⑥Render에만 적용된다 | RR-4 항목 본문 |
| Execution Layer 기존 Builder를 판정하지 않는다 | RR-4 아래 인용 블록 |
| R-3의 상태를 변경하지 않는다 | 같은 인용 블록. §13.4의 R-3 각주를 참조하도록 연결 |

#### 3.5 Extension Flow (판단 6)

4개 확장 지점의 위치표와 **"확장 지점은 단계의 개수나 순서를 바꾸지
않는다"**는 진술을 옮긴다. X-4가 흐름 밖에 있다는 사실과 4-Layer가
여전히 Defer라는 사실을 함께 기록한다.

#### 3.6 Implementation Neutrality (판단 7)

IN-1~IN-5와 3형태 시험을 옮긴다. **3형태 시험은 판정 기준이며 구현
계획이 아니고, 세 형태 중 어느 것도 채택되지 않았다**를 명시한다.

#### 3.7 말미 — 다음 단계와 미결

- 다음 단계는 Kernel API이며, **이 절의 Accept가 그 단계를 미리
  허가하지 않는다**(판단 1 조건 3).
- §13.6·§14.7의 Defer는 여기서 다시 나열하지 않고 참조한다(Single
  Source of Truth).
- **Kernel Component Architecture는 여전히 §10 Out of Scope다.**

### 4. `GLOSSARY.md` 갱신

"Kernel Reference Architecture" 항목을 추가하고, 6개 단계 이름과
RR/IN의 존재를 `BASELINE.md` §15 참조로 등재한다. 상세를 중복 기록하지
않는다.

**"Component"라는 단어를 이 항목에 쓰지 않는다** — KP-1과 ADC-0005
판단 5의 명칭 결정을 GLOSSARY에서도 지킨다.

### 5. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.3 | **v1.4** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: Freeze 원칙은 "변경 불가"가 아니라 "절차를
거치지 않은 변경이 반영되지 않는 상태"다. 이번 변경은 RFC-0005 →
ADC-0005 → ADR-0005 절차를 거쳤다.

**Minor 증가(v1.4)를 택한 이유 — 그리고 그 판단의 한계**: 이번 변경은
새 절 추가에 더해 **기존 절(§10)의 문언 변경**을 포함하므로, 선행
3건보다 무겁다. 그럼에도 Minor로 두는 이유는 (a) §10의 변경이 배제
범위를 **한정**할 뿐 다른 4개 항목과 다른 절을 건드리지 않고,
(b) 이 저장소에 Major 증가를 정의한 규칙이 없기 때문이다. **버전
증가 규칙 자체가 정의된 적이 없다는 사실을 한계로 기록한다** — 필요해
지면 별도로 다뤄야 한다.

### 6. Development HQ · Execution Layer 불변 확인

ADC-0005는 어떤 코드 변경도 지시하지 않았다. 특히 판단 5b 조건 2가
Execution Layer 기존 Builder에 대한 판정을 명시적으로 배제했다.

- `development-hq/` 이하 어떤 파일도 변경하지 않는다.
- `core/execution_layer/` 이하 어떤 파일도 변경하지 않는다.
- 42개 테스트는 이번 변경으로 영향을 받지 않는다(문서만 변경).

### 7. `docs/03_adc/ADC.md` 갱신 여부

**갱신하지 않는다.** ADC-0005의 판단은 전부 Accept이며 새 Open
Decision을 만들지 않는다. ADC-02(Runtime 개념의 존폐)는 **Open 상태
그대로 둔다** — §10 변경은 Component Architecture를 열지 않으므로
ADC-02에 영향이 없다(ADC-0005 판단 1 조건 1).

### 8. Migration Strategy

1. `BASELINE.md` §10 — 항목 문언 변경 + 설명 문단 추가(§2).
2. `BASELINE.md` — §15 Kernel Reference Architecture 삽입, 기존 §15
   Version → §16 이동 및 v1.4 갱신, 변경 이력 추가(§3·§5).
3. `GLOSSARY.md` — Reference Architecture 항목 추가(§4).
4. 검증:
   - `BASELINE.md`의 절 번호가 §1~§16으로 연속하는지 확인.
   - §10을 인용하는 5건이 **변경되지 않았는지** 확인(§2.3).
   - §13·§14를 인용하는 문서가 그대로 유효한지 확인(번호 불변).
   - ADC-0005의 조건 14건이 §10·§15 본문에 실제로 반영되었는지 §2.2·
     §3의 배치표와 대조.
   - `BASELINE.md`에 Scheduler/Registry/Runtime/Memory/Event Bus/
     Engine Gateway가 §15 안에 등장하지 않는지 확인(C-3).
   - `git status`로 `development-hq/`·`core/` 이하에 변경이 없는지
     확인.
   - `python3 -m pytest development-hq/mvp/tests/ core/execution_layer/*/tests/ -q`
     42건 통과 확인.
5. 커밋 — RFC-0005, ADC-0005, ADR-0005와 위 변경을 함께 커밋한다.

---

## Consequences

- `docs/01_architecture/BASELINE.md`가 v1.3 → v1.4가 되고, **Kernel
  내부의 논리적 배선도**가 Baseline의 일부가 된다.

  | 절 | 답하는 질문 |
  |---|---|
  | §11 | Kernel은 무엇인가 (정의) |
  | §12 | 어떻게 설계되어야 하는가 (원칙) |
  | §13 | 무엇을 관리하는가 (대상) |
  | §14 | 외부에 무엇을 보장하는가 (계약) |
  | **§15** | **그 책임들이 내부에서 어떻게 연결되는가 (배선)** |

- **§10의 배제 범위가 처음으로 한정된다.** v1.0부터 유지되던
  "Kernel Architecture"가 "Kernel Component Architecture"가 되고,
  이미 결정된 책임들의 논리적 연결만 열린다. **Component Architecture는
  그대로 닫혀 있다.**
- **다음 단계(Kernel API)의 판단 기준이 완성된다.** 어떤 API가
  제안되든 §14(무엇을 보장하는가)와 §15(어떻게 연결되는가) 양쪽으로
  검토할 수 있다. 배선이 인터페이스에서 역산되는 일이 방지된다(KP-1).
- **구현 중립성이 판정 가능해진다.** 3형태 시험(순수 함수 파이프라인
  / 메시지 전달 / 서비스 체인)이 §14.3에서 "관찰로 확인할 수 없다"고
  기록된 G-4에 부분적 실질을 준다. Python 외의 구현체도 같은 기준으로
  검토된다.
- **Development HQ와 Execution Layer는 한 글자도 변경되지 않는다.**
  특히 `prompt_specification_builder.py`는 RR-4의 적용 대상이 아니다.
- 남는 절차 부채를 정직하게 기록한다.
  1. **Frozen 절의 문장을 바꾼 첫 사례가 생겼다.** 이 선례가 "Frozen
     문장도 바꿀 수 있다"는 논거로 오용될 수 있다. 이 ADR은 변경을
     한 항목의 문언 한정으로 제한했으나, 그 제한은 문서 관행으로만
     지켜진다.
  2. **경계 조정의 선례가 생겼다.** 다음 단계(API)는 §10의
     "Implementation"과 맞닿으며, "ADR-0005도 §10을 조정했다"는 논거가
     나올 수 있다. ADC-0005 판단 1 조건 3이 이를 막는 유일한 장치다.
  3. **버전 증가 규칙이 정의된 적이 없다**(§5). 이번처럼 성격이 다른
     변경에도 Minor를 적용할지 판단할 기준이 없다.
  4. **R-3 질문이 미해결로 남는다.** Execution Layer가 훗날 Kernel
     Context를 사용하도록 정렬되면, `RENDERING_MAP`이 RR-4와 충돌하는지
     판단해야 한다. 이 ADR은 그 시점을 정하지 않는다.
  5. `GOVERNANCE-REVIEW-0001` §5의 근거 6개는 **전부 유효한 상태로
     남는다.** Component Architecture를 열려면 그 6개가 해소되어야
     한다.
  6. 선행 ADR들이 남긴 부채(디렉토리·파일명의 `core/`, Kernel
     ADC-0001의 미작성 ADR 2건, ADC-0003·ADC-0004의 Defer 6건)는 이
     ADR이 해소하지 않는다.
- 이 ADR은 **승인되었으며**, §8에 정의된 실제 파일 변경이 이 승인에
  따라 실행된다.
