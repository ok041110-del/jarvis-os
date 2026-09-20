# RFC-0045: Context Segment Identifier·Metadata Contract — H-5/H-6 설계 쟁점

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (KV-04 Engine Trigger 조사 후속)
**상위 근거**: `docs/architecture/baseline/BASELINE.md` §13(Kernel
Context Model)·§14(Kernel Public Contract) — H-5, H-6, X-3, X-4
**직접 계기**: `docs/architecture/core/EVIDENCE-INVENTORY-0001-validation-v1.md`
V-1 GAP-1(Context 수준 Identifier·Metadata 입력 경로 부재), 및 이
세션이 확인한 사실 — Owner Amendment의 A(Re-review 개시 조건: 실제
Engine 호출 관찰)는 이미 충족됐으나(`ADC-0026`, `ENGINE-CONNECT-0001`),
B(Context Boundary 판정 종결 조건: Stable Prefix 실측)는 **Context
Segment 구조 자체가 코드에 존재하지 않아 원천적으로 검증 불가능**하다는
점이 코드 조사로 확인됨.

> 이 RFC는 **H-5(Identifier 파생 규칙)와 H-6(Segment 자료구조·직렬화
> 형식)의 설계 선택지를 나열하고 trade-off를 정리할 뿐, 어느 것도
> 확정하지 않는다.** Kernel Context Builder·Renderer를 구현하지
> 않는다. Stable Prefix가 관찰됐다고 주장하지 않는다. 이 RFC 자체는
> Architecture 결정이 아니며, 결정은 후속 ADC → ADR로 넘긴다.

---

## 0. 선행 문서와의 관계 — 중복 방지

이 주제와 인접한 두 RFC가 이미 **Resolved** 상태로 존재한다. 이 RFC는
그 결론을 재론하지 않고 그 위에서만 시작한다.

| 선행 문서 | 다룬 질문 | 결론 | 이 RFC와의 관계 |
|---|---|---|---|
| `RFC-0006-kernel-context-ownership.md` → `ADC-0006` | Kernel이 Kernel Context를 어디까지 소유하는가 | 판단 5("Ownership" 어휘 승격) **Defer**, 판단 8: "V-1은 이 ADC로 닫히지 않는다 — OQ-1(Identifier 주입인가 파생인가)은 H-5 Defer와 맞물려 있다" | 이 RFC는 **바로 그 OQ-1**을 정면으로 다룬다. "Ownership" 어휘는 여전히 쓰지 않는다(§0.2 아래). |
| `RFC-0007-kernel-context-identity.md` → `ADC-0007` | Identity가 Reference Layer 문제인가 Component Layer 문제인가 | 판단 1 **Reject**("Identity가 V-1의 원인"이라는 주장), 판단 4 **Defer**(Identity를 Architecture Vocabulary로 승격하지 않음), 재검토 조건: "이중성으로 인한 실제 문제가 1회 이상 관찰되거나, 두 번째 문서에서 기존 어휘로 표현하려다 실패하는 사례가 나타날 때" | 이 RFC는 Identity를 새 어휘로 승격하려는 시도가 **아니다** — §13.1의 기존 어휘(Context Identifier, Context Source, Order Key)만 사용한다. 다만 아래 §2에서 확인한 "8개 이상의 독립 재발명 패턴"이 위 재검토 조건의 후半("기존 어휘로 표현하려다 실패하는 사례")에 해당할 가능성을 사실로만 기록한다 — **이 RFC는 그 재검토 조건이 충족됐다고 확정하지 않는다.** |

**이 RFC가 어휘로 쓰지 않는 것**: "Ownership", "Identity"(고유 개념으로서). **이 RFC가 쓰는 것**: `BASELINE.md` §13.1의 기존 5개 요소(Context/Segment/Source/Metadata/Identifier)와 §13.2~§13.4의 기존 책임·불변식 어휘뿐이다.

### 0.1 이 RFC가 새로 여는 이유

`RFC-0006`/`RFC-0007`은 모두 "질문의 성격"(누가 소유하는가, 어느
계층의 문제인가)만 다뤘고, 스스로 명시적으로 "Identifier 생성 방법 /
Metadata 구조는 이 RFC의 범위가 아니다"라고 선을 그었다. **H-5/H-6은
그 두 RFC 이후에도 계속 미결로 남아 있었다.** 이 RFC를 지금 여는
근거는 새로운 사실 하나다 — Owner Amendment의 A(실제 Engine 호출
관찰)가 이미 충족된 상태에서, B(Stable Prefix 실측)를 검증하려면
"무엇을 Segment로 볼 것인가"가 먼저 정의돼야 하는데, 그 정의 자체가
H-6이 미결로 남겨둔 것이기 때문이다. 즉 이 RFC는 **B 검증의 선행
조건**으로 열린다.

---

## 1. Problem Statement

`BASELINE.md` §13.1은 Kernel Context를 Identifier + Metadata +
Segment[ordered]로 정의했지만, 다음 두 가지는 의도적으로 미결(Hidden/
미결)로 남아 있다.

- **H-5**: "Context Identifier 파생 규칙 — Defer 상태다. 미결을
  Public에 두면 외부가 미결에 의존하게 된다."(§14.4)
- **H-6**: "Segment의 자료구조·직렬화 형식 — 미결 사항이다."(§14.4)

이 미결 상태 자체는 지금까지 문제가 되지 않았다 — Kernel Context
Builder가 구현된 적이 없으므로 소비자가 없었다(`EVIDENCE-INVENTORY-0001`
GAP-1). 그러나 이번 KV-04 Engine Trigger 조사에서 다음 사실이
확인됐다.

1. Owner Amendment의 A(실제 Engine 호출 관찰)는 이미 충족됐다
   (`ADC-0026` §2·§4.1·§5, `ENGINE-CONNECT-0001`).
2. B(Stable Prefix 실측 확인)를 검증하려면 "여러 실제 Engine 호출에
   걸쳐 재사용되는, 식별 가능한 Segment"가 있어야 하는데, **현재
   코드에는 그런 재사용 지점 자체가 없다** — 4개 Engine 호출 함수
   전부 매번 새로 조립되는 단일 flat string만 받는다.
3. 저장소 전역에 **8개 이상의 독립적으로 재발명된 ad hoc 텍스트
   조립 패턴**이 존재하지만, 어느 것도 §13.1의 Segment 정의(Kernel이
   독립적으로 식별·정렬·포함/제외할 수 있는 단위)를 만족하지 않는다.

**따라서 B는 H-6(Segment 자료구조)이 정의되기 전까지는 원천적으로
검증 불가능하다.** 이 RFC는 이 막힘을 풀기 위해 H-5/H-6의 설계
선택지를 정리한다.

---

## 2. Scope / Non-Goals

### 다루는 것

- H-5: Context Identifier의 생성·파생·주입·검증 책임의 **선택지**.
- H-6: Context Segment의 자료구조·직렬화·순서·경계 표현의 **선택지**.
- 위 둘이 V-1 GAP-1, B(Stable Prefix) 검증과 맺는 관계.
- 기존 Contract(§13, §14)와의 정합성·충돌 가능성.

### Non-Goals (명시적으로 다루지 않음)

- Kernel Context Builder·Renderer의 **구현**.
- H-5/H-6의 **확정**(이것은 후속 ADC/ADR의 몫이다).
- "Ownership"·"Identity"를 새 Architecture Vocabulary로 승격하는 것
  (`ADC-0006` 판단 5, `ADC-0007` 판단 4의 Defer를 그대로 존중한다).
- Stable Prefix가 실제로 관찰됐다는 주장 — 이 RFC는 **B를 검증
  가능하게 만들기 위한 선행 설계 논의**일 뿐, B 자체를 다루지 않는다.
- Memory Module, Runtime, Scheduler, Registry, Event Bus — 전부
  기존 Defer 상태 그대로 둔다.
- Development HQ/Investment HQ의 기존 ad hoc 프롬프트 조립 코드
  (`workflow_ast_context.py` 등)의 **수정**.
- Engine별 Renderer 설계(판단 5b, 별도 Defer).

---

## 3. Existing Evidence

### 3.1 Baseline이 이미 기록한 미결 상태 (재인용, 원문 변경 없음)

- H-5(§14.4): "Context Identifier 파생 규칙 — **Defer 상태다**(§13.6).
  미결을 Public에 두면 외부가 미결에 의존하게 된다."
- H-6(§14.4): "Segment의 자료구조·직렬화 형식 — **미결 사항이다.**"
- X-3(§14.5): "Context Source — 무엇이 Context에 들어가는가.
  **플러그인이 아니라 계약의 입력 경계다.**"
- X-4(§14.5): "Future Context Model — Context 구성 요소의 확장.
  **확장이 들어올 자리의 표시이며, 확장이 일어난다는 예고가 아니다.**"

### 3.2 ADC-0003 판단 1b — H-5의 두 후보 (재인용)

`ADC-0003` 판단 1b는 Identifier 파생 규칙을 Defer하면서, 관찰된 유일한
실사례와 함께 두 후보를 기록했다.

- **호출자 주입**: "관찰된 사실은 호출자 주입 하나뿐이다(MVP-0003~0005)."
- **내용 해시로부터 파생**: "내용 해시로 식별자를 만든 사례는 이
  저장소에 존재하지 않는다."
- (세 번째 후보 "Kernel이 생성"은 CM-3/KP-6에 의해 이미 배제됨 —
  이 RFC도 이 배제를 재론하지 않는다.)

### 3.3 코드 조사 결과 (이 세션, read-only 조사, 미변경)

- **Context Segment/Identifier/Metadata를 구조화된 타입으로 정의한
  코드는 저장소 전체에 0건**(`hqs/`, `core/`, `projects/` 전수 grep).
- **4개 Engine 호출 함수**(`engine.py::call_engine`,
  `chatgpt_engine.py::call_engine_via_chatgpt`,
  `openrouter_engine.py::call_engine_via_openrouter`,
  `omniroute_engine.py::call_engine_via_omniroute`)는 전부 단일
  `prompt: str` 인자만 받는다 — Segment 배열이나 다중 필드 입력은
  없다.
- **가장 가까운 기존 구조**는
  `core/execution/mvp_0002/prompt_specification_builder.py`
  (9개 Source 섹션 → 5개 Prompt 섹션 고정 매핑)이나, `BASELINE.md`
  (line 723-724)가 이미 "Kernel Context를 입력으로 받지 않으므로
  Kernel Renderer가 아니다"라고 명시했다 — **이 RFC는 이것을 Kernel
  Context Segment의 선행 구현으로 간주하지 않는다.**
- **8개 이상의 독립 재발명 ad hoc 조립 패턴**이 Development HQ와
  Investment HQ에 흩어져 있다(`workflow_ast_context.py`,
  `stage_03.py`, `stage_04.py`, `prd_synthesis.py`, `reasoning.py`,
  `workflow_0009.py`, `hqs/investment/teams/{stock,etf,dividend_stock}_team.py`).
  전부 `---LABEL---`/`[LABEL]` 마커로 여러 텍스트 블록을 이어붙인
  flat string이며, 공유 코드·공통 타입·순서 불변식이 없다. **이
  RFC는 이들 중 어느 것도 "이미 Segment 요구사항을 만족하는 구현"으로
  간주하지 않는다** — §13.1의 정의(Kernel이 독립적으로 식별·정렬·
  포함/제외할 수 있는 단위)를 만족하는 것은 하나도 없다.
- **`ADC-0026`/`ENGINE-CONNECT-0001/0002/0005`에는 Segment 유사
  구조에 대한 언급이 없다**(전수 grep 0건) — 실제 완결된 Engine
  호출(2건의 완결 응답 + 1건의 실제 timeout, `ADC-0026` §2)이
  존재하지만, 그 호출들의 입력은 전부 단일 flat string이었다.

**확인되지 않은 것으로 명시**: 위 어떤 조사도 "실제 운영 환경에서
Segment 재사용이 필요하다는 요구"를 관찰하지 못했다 — 이 RFC가 여는
근거는 "요구가 관찰돼서"가 아니라 "B를 검증하려면 정의가 선행돼야
해서"이다. 이 구분은 `ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준
("지금 결정하지 않으면 진행 불가" / "늦어질수록 비용이 커진다")을
적용할 때 중요하다 — 아래 §9에서 다시 다룬다.

---

## 4. H-5 설계 쟁점과 선택지 (Identifier 생성·파생·주입·검증 책임)

**쟁점**: Context Identifier(및 Segment Identifier)의 값은 어디서
오는가? CM-3("Kernel은 Identifier와 시각을 스스로 생성하지 않는다")은
이미 Accept되어 있으므로, 후보는 "Kernel이 생성"을 제외한 나머지다.

| 옵션 | 내용 | 장점 | 단점 / 위험 |
|---|---|---|---|
| **H5-A. 호출자 주입(Caller-Injected)** | HQ가 Segment/Context를 만들 때 Identifier 값을 직접 부여해 Kernel에 전달한다. | 관찰된 유일한 실사례(MVP-0003~0005)와 일치. Kernel은 검증(존재·유일성)만 하면 되어 §13.2 책임과 정확히 맞물린다. CM-3과 가장 자연스럽게 정합. | 호출자마다 다른 Identifier 체계를 쓰면 G-2(Stable Ordering의 tie-break)의 유일성 보장이 호출자 규율에 의존하게 된다 — Kernel이 강제할 수 없다. |
| **H5-B. 내용 기반 결정론적 파생(Content-Derived Hash)** | Segment Content(및 Source)로부터 결정론적 해시를 계산해 Identifier로 쓴다. | 호출자 규율에 의존하지 않음 — 같은 Content는 항상 같은 Identifier(A-5 "같은 입력 → 같은 Context"와 자연스럽게 정합). 병합 규칙("같은 Identifier + 다른 Content는 오류")과의 상호작용이 자명해진다(해시가 다르면애초에 "같은 Identifier"가 아님). | CM-4("Kernel은 Content를 해석하지 않는다")와의 경계가 미묘하다 — 해시 계산이 "해석"에 해당하는지 별도 판단이 필요하다. 저장소에 관찰된 실사례가 0건(§3.2)이므로 순수 설계 추정이다. |
| **H5-C. 하이브리드(주입 우선, 미지정 시 파생으로 fallback)** | 호출자가 Identifier를 주면 그것을 쓰고, 없으면 H5-B 방식으로 파생시킨다. | 기존 유일한 실사례(주입)를 깨지 않으면서 유일성 보장을 강화. | 두 경로가 공존하면 "같은 Content, 다른 경로로 만든 Identifier"가 우연히 다를 수 있어 오히려 새로운 결정론 위반 사례를 만들 수 있다 — 별도의 tie-break/우선순위 규칙이 필요해진다. |

**H-5가 결정하지 않아도 되는 것**: 어느 옵션이든 §13.1의 Model("값
하나")과 CM-3을 그대로 유지한다(`ADC-0003` 판단 1b 판단 근거 재인용).
**즉 이 RFC의 어떤 옵션도 §13 Model 자체를 변경하지 않는다.**

---

## 5. H-6 설계 쟁점과 선택지 (Segment 자료구조·직렬화·순서·경계)

**쟁점**: "Kernel이 독립적으로 식별·정렬·포함/제외할 수 있는 최소
단위"(§13.1)를 코드/직렬화 수준에서 어떻게 표현하는가?

| 옵션 | 내용 | 장점 | 단점 / 위험 |
|---|---|---|---|
| **H6-A. 명시적 구조체(named fields)** | `{identifier, source, content, metadata, order_key}` 형태의 명시적 구조(dataclass/dict schema 등 — 구체적 자료형은 Implementation이므로 이 RFC가 정하지 않음). | §13.1 Model을 코드에 1:1로 반영 — 검증(PR-3)·병합(§13.2)·정렬(O-1~O-4)이 필드 단위로 명확해진다. | 기존 8개 ad hoc 패턴 전부를 이 구조로 마이그레이션해야 실질적 효용이 생긴다 — 마이그레이션 비용(아래 §8)이 발생. |
| **H6-B. 마커 기반 델리미터(현재 관행의 표준화)** | 현재 관행(`---LABEL---`, `[LABEL]`)을 그대로 두되, 델리미터 문법 하나로 통일하고 파싱 규칙만 Contract화한다. | 기존 8개 패턴과 충돌이 적어 마이그레이션 비용이 낮다. | 델리미터는 Content 안의 우발적 문자열과 충돌할 수 있어 A-1("Content는 조립 과정에서 한 글자도 바뀌지 않는다")·PR-3(구조 불변식 검증)을 코드 수준에서 보장하기 어렵다 — Kernel이 Content를 "해석"하게 될 위험(CM-4). |
| **H6-C. 이중 표현(Structured Model + Rendered String)** | Kernel 내부에서는 H6-A(구조체)로 유지하고, ⑥Render 단계에서만 Engine이 요구하는 flat string으로 변환한다(§13.4 "Kernel Context가 정본, Prompt는 파생물"과 정확히 일치). | 기존 §13.4 Prompt=Output Format 원칙과 완전히 정합 — 별도의 새 원칙이 필요 없다. Renderer 계약(R-1·R-2·R-4·R-5)을 그대로 재사용 가능. | 사실상 H6-A를 전제로 하므로 마이그레이션 비용은 H6-A와 동일하게 발생한다. |

**H-6이 결정하지 않아도 되는 것**: 직렬화 **형식**(JSON/dataclass/
protobuf 등)은 Implementation 수준이며 §10 Out of Scope다 — 이 RFC는
"Segment가 무엇을 필드로 가져야 하는가"까지만 다루고, 그것을 어떤
포맷으로 저장·전송할지는 다루지 않는다.

---

## 6. 책임 경계 (Builder / Renderer / Engine Adapter)

기존 §13.5("HQ는 무엇이 들어가는지 정하고, Kernel은 어떻게 식별·검증·
병합·정렬·조립·표현되는지 담당한다")를 그대로 적용하면, H-5/H-6이
확정되더라도 다음 경계는 바뀌지 않는다.

| 주체 | H-5/H-6 확정 후에도 유지되는 책임 |
|---|---|
| **HQ (호출자)** | Segment의 Content·Source를 제공(§13.5). H5-A를 채택하면 Identifier도 HQ가 제공. |
| **Builder** | 제공된 Segment를 §13.2(수집·검증·병합·정렬) 그대로 처리. H-6이 정의한 구조를 **입력 형식**으로 받을 뿐, 새 책임이 추가되지 않는다. |
| **Renderer** | Kernel Context(H-6 구조)를 Engine이 요구하는 flat string으로 변환(§13.4, R-1·R-2·R-4·R-5). **H-6이 H6-C를 채택하면 이 경계가 정확히 지금의 §13.4 원칙과 일치한다.** |
| **Engine Adapter**(`call_engine*` 4개 함수) | 여전히 `prompt: str` 하나만 받는다 — H-5/H-6 확정이 Engine Adapter의 시그니처를 바꾸지 않는다. Renderer가 그 앞에서 flat string을 만들어 넘긴다. |

**결론**: H-5/H-6을 확정해도 기존 책임 배치(§13.5)와 Engine 호출
경계(4개 Adapter 함수의 `str` 계약)는 바뀌지 않는다 — 이것은 새
Architecture 책임을 추가하지 않는다는 근거다(§9).

---

## 7. 기존 Contract와의 충돌 가능성

| 기존 항목 | 충돌 가능성 | 비고 |
|---|---|---|
| H-5(§14.4) | **직접 충돌** — 이 RFC의 목적이 H-5를 다루는 것 자체다. 확정은 후속 ADC/ADR의 몫이며, 이 RFC는 옵션만 나열한다. | 임의 확정 금지 |
| H-6(§14.4) | **직접 충돌** — 동일 | 임의 확정 금지 |
| CM-3(Kernel은 Identifier를 스스로 생성하지 않음) | H5-B(해시 파생)를 채택할 경우, "파생"이 "생성"과 어떻게 다른지 명확히 해야 한다 — `ADC-0003` 판단 1b가 이미 "호출자가 주입하거나 **결정론적으로 파생**한다"고 CM-3 문언에 파생을 포함시켰으므로 문언상 충돌은 아니나, 해석 정합성을 후속 ADC가 확인해야 한다. | 잠재적 해석 쟁점 |
| CM-4(Kernel은 Content를 해석하지 않음) | H5-B와 H6-B 모두 "Content를 읽어 Identifier를 계산"하거나 "Content 안의 델리미터를 파싱"하는 동작을 포함할 수 있어, 이것이 "해석"에 해당하는지 경계가 불분명하다. | 후속 ADC에서 반드시 다뤄야 할 쟁점 |
| §13.6 Defer 목록(4-Layer Context Model 등) | 충돌 없음 — 이 RFC의 어떤 옵션도 계층 분류를 Segment/Model에 넣지 않는다(CM-1 유지). | — |
| `ADC-0006` 판단 5, `ADC-0007` 판단 4(어휘 승격 Defer) | 충돌 없음 — §0에서 확인한 대로 이 RFC는 새 어휘를 도입하지 않는다. | — |

---

## 8. 검증 가능성 및 Evidence 요구사항

H-5/H-6이 어떤 옵션으로 확정되든, 다음 Evidence가 없으면 그 확정은
"관찰 없는 설계"가 된다(`ARCHITECTURE_GOVERNANCE.md`의 Experimental
Evidence 원칙과 동일한 기준).

- **H-5 확정에 필요한 Evidence**: Context를 실제로 **비교·재사용하는
  사례**가 최소 1회 관찰되어야 한다(`ADC-0003` 판단 1b 재검토 조건과
  동일). 현재 0건.
- **H-6 확정에 필요한 Evidence**: 기존 8개 ad hoc 패턴 중 최소
  하나가 실제로 §13.1 정의(독립 식별·정렬·포함/제외 가능)를 요구하는
  상황에 부딪힌 사례, 또는 여러 Engine 호출에 걸쳐 동일 Segment가
  재사용되어야 하는 실제 필요가 관찰되어야 한다. 현재 0건.
- **B(Stable Prefix) 검증에 필요한 관찰 지점**: H-6이 확정되어
  Segment 구조가 코드에 존재해야만, "동일 Segment 집합이 여러 실제
  Engine 호출에 걸쳐 앞쪽에 반복 배치되는지"를 관찰할 지점이 생긴다.
  **지금은 이 지점 자체가 없다** — 이것이 이 RFC의 핵심 동기다(§1).

---

## 9. Migration 대상 선정 기준

H-6이 확정된 이후, 기존 8개 ad hoc 패턴 중 어느 것을 새 구조로
전환할지 선정하는 기준(제안, 확정 아님):

1. **재사용 빈도** — 동일 패턴이 여러 호출 지점에서 반복되는가
   (예: Investment HQ 3개 team 파일이 동일 패턴을 3중 재발명).
2. **Engine 호출 완결성** — 이미 실제 완결된 Engine 호출 경로 위에
   있는가(`ADC-0026`의 `analyst_sentiment` 경로처럼 실측 가능한
   지점).
3. **격리 가능성** — Migration이 `hqs/development/`·`hqs/investment/`
   production path에 즉시 영향을 주지 않고 Experimental
   Implementation(`ARCHITECTURE_GOVERNANCE.md` "Experimental
   Implementation" 절)으로 먼저 검증 가능한가.

**이 RFC는 특정 패턴을 Migration 대상으로 지목하지 않는다** — 위
기준의 적용은 후속 ADC의 몫이다.

---

## 10. Open Questions

- **OQ-1**: H-5는 H5-A/H5-B/H5-C 중 하나로 확정돼야 하는가, 아니면
  §13.1처럼 "값 하나"로만 규정한 채 계속 Defer해도 상위 설계가
  막히지 않는가? (`ADC-0003` 판단 1b의 논리가 지금도 유효한지
  재확인 필요.)
- **OQ-2**: H-6을 확정하지 않고도 B(Stable Prefix)를 다른 방식으로
  검증할 방법이 있는가 — 예를 들어 Segment 구조 없이 "flat string의
  반복되는 접두 substring"만으로 B를 판정하는 것이 §13.1의 취지에
  부합하는가, 아니면 반드시 Segment 단위 식별이 필요한가?
- **OQ-3**: H5-B/CM-4, H6-B/CM-4의 "해석" 경계(§7)를 어떻게 명확히
  할 것인가?
- **OQ-4**: `ADC-0007` 판단 4의 재검토 조건("두 번째 문서에서 기존
  어휘로 표현하려다 실패하는 사례")이 §3.3의 8개 ad hoc 패턴으로
  이미 충족된 것으로 볼 수 있는가? (이 RFC는 이 질문에 답하지 않고
  Owner에게 남긴다.)
- **OQ-5**: 어느 옵션을 채택하든, `BASELINE.md` §14.4의 H-5/H-6
  문언을 "Defer/미결"에서 "Accept(선택된 옵션)"로 바꾸는 것 자체가
  Baseline 개정(ADR 필요)인가, 아니면 Hidden 항목이므로 ADR 없이
  ADC만으로 충분한가?

---

## 11. Architecture Owner에게 요청할 결정 사항

이 RFC는 스스로 결정하지 않는다. 다음은 Architecture Owner가 후속
ADC 단계에서 판단해야 할 사항이다.

1. 이 RFC를 **ADC로 승격**할지 여부 — 승격한다면 §4(H-5)와
   §5(H-6)를 하나의 ADC로 묶을지, 별도 ADC 두 개로 분리할지
   (`ADC-0016` §16.3~§16.6 선례처럼 단일 Boundary Question 원칙을
   따를지 결정 필요).
2. §8이 요구하는 Evidence(비교·재사용 사례, 실제 필요 관찰)가
   **지금 시점에 이미 충분한지, 아니면 더 기다려야 하는지**
   (`ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준 두 조건 적용).
3. OQ-1: H-5/H-6을 지금 확정할지, 계속 Defer할지.
4. OQ-4: `ADC-0007` 판단 4의 재검토 조건 충족 여부.
5. 승격 시 ADR 필요 여부(OQ-5).

**이 결정 전까지는 다음이 진행되지 않는다**: H-5/H-6의 확정,
Kernel Context Builder/Renderer 설계 착수, 8개 ad hoc 패턴의 실제
Migration, B(Stable Prefix)의 실제 검증.

---

## 12. Self Review

- 특정 설계를 선택했는가 — **아니오**. §4·§5 모두 옵션과 trade-off만
  나열했다.
- H-5/H-6을 확정된 Contract로 바꿨는가 — **아니오**. `BASELINE.md`
  §14.4는 이 RFC로 수정되지 않았다.
- ADC/ADR을 선행 작성했거나 승인된 것으로 처리했는가 — **아니오**.
  §11은 "요청할 결정 사항"으로만 남겼다.
- Stable Prefix가 관찰됐다고 주장했는가 — **아니오**(§8, §1).
- Kernel Context Builder/Renderer를 구현했는가 — **아니오**.
- `ADC-0006`/`ADC-0007`이 이미 Defer/Reject한 것을 재론했는가 —
  **아니오**(§0) — "Ownership"/"Identity" 어휘를 쓰지 않았고, Identity가
  V-1의 원인이라는 주장을 반복하지 않았다.
- 기존 8개 ad hoc 패턴이나 `prompt_specification_builder.py`를
  Kernel Context Segment의 기존 구현으로 취급했는가 — **아니오**(§3.3).
- 확인되지 않은 것을 사실처럼 썼는가 — **아니오** — §3.3 마지막
  문단에서 "실제 운영 요구가 관찰된 바 없다"를 명시했다.
- Development HQ/Investment HQ 코드를 수정했는가 — **아니오**.

---

Architecture Change: 없음 (이 RFC 자체가 변경이 아니라 옵션 정리
문서)
Contract Change: 없음 — H-5/H-6은 여전히 Defer/미결 상태 그대로다
Implementation: 없음 — Builder/Renderer/코드 변경 전부 미수행
RFC: `RFC-0045`(본 문서, Proposed)
ADC: 없음 (열리지 않음 — 후속 ADC는 이 RFC가 결정하지 않는다)
ADR: 없음
PR: 없음
