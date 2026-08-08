# IMPL-ENTRY-0001: Implementation 진입 가능성 검토

**문서 성격**: Entry Review. **Architecture 문서가 아니다.**
**목적**: 현재 Architecture를 **변경하지 않고** Implementation 단계에
진입할 수 있는지 검토한다.

이 문서는 Architecture·Concept·Layer·Component를 설계하지 않는다.
RFC·ADC·ADR을 작성하지 않는다. Baseline을 수정하지 않는다. 어떤 코드도
작성하지 않는다. **무엇을 구현할 수 있는지 판단만 한다.**

**읽은 문서**: `BASELINE.md` v1.4 / `development-hq/BASELINE.md` v1.0 ·
`MVP.md` · `IMPLEMENTATION_RULES.md` · `BOUNDARY.md` /
`ARCHITECTURE_GOVERNANCE.md` / `BASELINE.md` §15 /
`VALIDATION-0001` / `STABILITY-0001` / `EVIDENCE-INVENTORY-0001` /
`ARTIFACT-STANDARD-v1.md` / `core/execution_layer/**` /
`development-hq/mvp/engine.py`

---

# 1. Implementation Entry Assessment

## **진입 가능하다. 단 범위가 좁고, 그 좁음의 원인이 Architecture가 아니다.**

### 근거

| ID | Evidence | 출처 |
|---|---|---|
| E-1 | `ARCHITECTURE_GOVERNANCE.md`의 변경 절차가 `RFC → ADC → ADR → Baseline Update → Implementation`으로 **Implementation을 마지막 단계로 이미 정의**한다 | 원문 |
| E-2 | 그 사슬의 앞 4단계가 완료되었다 — Kernel RFC 7건 전부 후속 ADC로 종결, Baseline v1.4 반영 완료 | `STABILITY-0001` §1.2·§6.2 |
| E-3 | Baseline 마지막 변경(v1.4) 이후 **6개 커밋·2회 RFC→ADC 사이클이 Baseline을 한 글자도 바꾸지 않았다** | `STABILITY-0001` S-1·S-2 |
| E-4 | Documentation Issue 12건 전부 "Architecture 영향 없음 / Implementation 차단 없음" | `DOC-TRIAGE-0001` §4 |
| E-5 | 남은 Architecture 재개 Trigger가 **전부 "관찰"**이며, 문서 작업으로 열리는 것이 없다 | `STABILITY-0001` §6.5 |

**E-5가 결정적이다.** Architecture를 더 진행하려면 관찰이 필요하고,
관찰은 구현에서만 나온다. 진입하지 않으면 진행이 멈춘다.

### 진입의 성격을 한정한다

> **"Architecture가 충분해서 진입 가능"이 아니라, "Architecture가 지금
> 결정할 수 있는 데까지 갔고 그 다음이 Implementation이어서 진입
> 가능"이다.**

---

# 2. 현재 구현 가능한 범위

**판별 기준**: (a) Baseline이 이미 결정한 것만 사용하는가,
(b) §10 Out of Scope를 침범하지 않는가, (c) `IMPLEMENTATION_RULES.md`
금지 항목에 해당하지 않는가.

## 2.1 구현 가능 — Execution Layer의 여섯 번째 Artifact

| 항목 | 내용 |
|---|---|
| **대상** | Execution Result (`core/execution_layer/`의 6번째 Artifact) |
| **Baseline 근거** | Kernel ADC-0001이 **Execution Layer를 Kernel Module로 Accept**했다(9개 MVP 전부 일관, Phase 1 이전부터 Frozen 경계) |
| **선행 정의** | `ARTIFACT-STANDARD-v1.md`가 Artifact Chain 도식에 *"(미구현 — Execution Result, 이 문서의 범위 밖)"*으로 **자리를 이미 예고**했고, Artifact 5의 "Consumer" 칸을 *"아직 없음"*으로 비워 두었다 |
| **따를 패턴** | 5개 Builder가 확립하고 테스트로 고정한 것 — Wrap not rewrite / caller-supplied identity / 결정론 / 고정 구조 오버헤드 |
| **새 Architecture인가** | **아니다.** 5개 Builder의 확립된 Contract를 여섯 번째에 적용하는 것이며, 새 Layer·Component·Concept를 만들지 않는다 |
| **§10 침범 여부** | **없음.** Execution Layer는 Kernel Component Architecture가 아니라 이미 Accept된 Module이다 |
| **금지 항목 해당** | **없음.** Scheduler·Registry·Runtime·Gateway·Policy·Memory·Event Bus·Parser·Routing 어느 것도 아니다 |

> **이 항목이 특별한 이유**: `GOVERNANCE-REVIEW-0001` §5의 **6개 차단
> 근거 중 하나가 "Execution Result(6번째 Artifact) 미설계"**다.
> 구현하면 그 근거 1건이 직접 해소된다.

## 2.2 조건부 — 실제 Engine 호출

**이 항목은 판단이 갈리므로 사실만 먼저 제시한다.**

### 관찰된 사실

| ID | Observation | 출처 |
|---|---|---|
| O-1 | `call_engine(prompt: str) -> str`이 **이미 단일 함수로 존재**한다. docstring: *"단일 Engine 호출 지점. **지금은** 규칙 기반 응답을 반환한다"* | `development-hq/mvp/engine.py:15-17` |
| O-2 | `IMPLEMENTATION_RULES.md`에 **LLM/ML/모델 호출을 금지하는 조항이 없다.** 전수 검색으로 확인 | 원문 |
| O-3 | 같은 문서의 금지 항목은 **추상화**에 대한 것이다 — Engine Gateway(Port/Adapter), Engine Routing, Multi Engine |
| O-4 | 그 문서 14행: *"Engine Gateway(Port/Adapter 추상화) 구현 금지 \| **단일 함수로 Engine을 호출하는 것으로 충분하다**"*, 15행: *"MVP는 **Engine을 호출하는 함수 하나만 가진다**"* | 원문 |
| O-5 | `MVP.md` Out of Scope 9개 항목에 **"Engine 호출"이나 "LLM"이 없다.** "Multi Engine"만 있다 | 원문 |

### 상충하는 사실

| ID | Observation | 출처 |
|---|---|---|
| O-6 | `RFC-0005`(Dev HQ) 52행이 *"LLM/ML 호출은 한 번도 추가되지 않았다(**`IMPLEMENTATION_RULES.md`의 금지 사항**이자…)"*라고 진술한다. **그러나 그 문서에 해당 조항이 없다**(O-2) | RFC-0005 원문 대조 |
| O-7 | `RFC-0005`는 **후속 ADC가 없는 유일한 Open RFC**다. 그 진술은 판단된 적이 없다 | `STABILITY-0001` §1.2 |
| O-8 | `RFC-0001-jarvis-os-core-baseline.md` 전제: *"Development HQ는 Phase 1을 완료한 것으로 간주하며, **더 이상 수정하지 않는다**"* — ADR-0002~0005가 각각 "Development HQ를 수정하지 않았다"를 반복 확인했다 | 원문 |
| O-9 | 그러나 O-8의 "더 이상 수정하지 않는다"를 **결정으로 확정한 ADR은 없다.** RFC의 전제이자 이후 ADR들이 자기 작업 범위를 서술한 문장이다 | 전수 확인 |

### 판정

> **이 항목은 "구현 가능"으로도 "금지"로도 판정하지 않는다.**
>
> `call_engine`을 실제 호출로 바꾸는 것은 **Development HQ 코드
> 수정**을 수반하며, 그 가부는 O-8·O-9가 보여주듯 **확정된 결정이
> 아니라 확정된 적 없는 전제**에 걸려 있다.
>
> **이 문서는 그것을 판단할 권한이 없다** — 사용자 결정 사항이다.

## 2.3 구현 불가

| 대상 | 근거 |
|---|---|
| Kernel Component 전부 (Scheduler / Registry / Runtime / Engine Gateway / Policy / Memory Service / Event Bus / Workflow Parser / Engine Routing) | `BASELINE.md` §10 + `IMPLEMENTATION_RULES.md` 금지 항목 + 이번 검토의 명시 금지 |
| Kernel 자체의 구현 | §10이 Component Architecture를 Out of Scope로 유지. Kernel Renderer 0개, Kernel 구현 코드 0건 |
| Kernel Context Model의 코드화 | §13은 Model을 정의했으나 그것을 담을 Component가 §10에 막혀 있다 |
| Multi-Engine / Multi-HQ | `MVP.md` Out of Scope, `IMPLEMENTATION_RULES.md` 금지 |

---

# 3. 구현을 통해 확보할 Observation

**현재 존재하지 않는 Observation을 추측하지 않는다.** 무엇이 **처음으로
관찰 가능해지는지**만 적고, 그 관찰이 **무엇을 보여줄지는 적지
않는다.**

## 3.1 Execution Result 구현 시

| Observation | 현재 존재하지 않는 이유 |
|---|---|
| 여섯 번째 Artifact의 실제 Contract | `ARTIFACT-STANDARD-v1.md`가 자리만 예고하고 설계하지 않았다 |
| Artifact Chain이 끝까지 이어졌을 때의 형태 | Artifact 5의 Consumer 칸이 *"아직 없음"*이다 — 체인이 완결된 적이 없다 |
| 5개 Builder 패턴이 여섯 번째에도 유지되는지 | 6번째 적용 사례가 존재한 적이 없다 |

**이 관찰은 `GOVERNANCE-REVIEW-0001` §5의 6개 차단 근거 중 1건
("Execution Result 미설계")에 직접 대응한다.**

## 3.2 실제 Engine 호출이 이루어질 경우 (§2.2 판정 보류 상태)

| Observation | 현재 존재하지 않는 이유 |
|---|---|
| 실제 Engine 호출이 1회 발생했다는 사실 | 저장소 전 구간에서 Engine 호출 **0회** |
| 호출 시점에 Context가 실제로 어떤 경로로 전달되는지 | 지금까지 Context는 `issue["description"]` 문자열 덧붙이기 단일 경로였다(EVIDENCE-REVIEW-0001, 4건 반복) |

**이 관찰은 ADC-0003 판단 4·5b·6b의 재검토 조건("실제 Engine 호출 1회
관찰")에 직접 대응한다.**

## 3.3 관찰되지 않는 것 — 명시한다

다음은 위 두 구현으로도 **관찰되지 않는다.**

| 미충족 조건 | 이유 |
|---|---|
| Engine 수 ≥ 2 (RT-0001 Candidate 2) | 단일 Engine 호출로는 두 번째 Engine이 생기지 않는다. Multi Engine은 금지 항목이다 |
| HQ 수 ≥ 2 (Candidate 3) | Multi-HQ는 금지 항목이다 |
| Context 전달 경로 ≥ 2 (Candidate 4) | 경로를 늘리는 것은 별도 설계를 수반한다 |
| Kernel Component 관련 관찰 | Kernel 구현이 §10에 막혀 있다 |

> **즉 §2의 두 항목을 전부 구현해도 `GOVERNANCE-REVIEW-0001` §5의 6개
> 근거 중 해소되는 것은 최대 1건(Execution Result)이다.**

---

# 4. Architecture Re-entry Trigger

**기존 Rule A / Rule B / 각 ADC 재검토 조건만 정리한다. 새 Trigger를
만들지 않는다.**

## 4.1 Rule A — RT Trigger 충족 → RFC

| Candidate | Trigger | 구현 중 발동 가능성 |
|---|---|---|
| 1. Task Dispatcher | Workflow Branch 발생, 또는 하드코딩 체인 ≥ 2 | ADC-0004에서 재판단 완료(Keep) |
| 2. Engine Gateway | Engine 수 ≥ 2 | **§2 범위에서 발동하지 않는다**(Multi Engine 금지) |
| 3. Agent Registry | HQ 수 ≥ 2 또는 Registry 중복 관리 | 발동하지 않는다(Multi-HQ 금지) |
| 4. Context 전달 메커니즘 | Context 전달 경로 ≥ 2 | 발동하지 않는다 |

## 4.2 Rule B — 동일 Tag Observation 3회 → RFC

현재 축적 중인 Tag 없음. 구현이 재개되면 Observation이 다시 쌓이기
시작한다.

## 4.3 `IMPLEMENTATION_RULES.md`의 구현 중단 트리거 (기존)

**이것이 구현 단계에서 가장 먼저 작동할 Trigger다.**

> 1. Agent-Capability 매핑이 리터럴 딕셔너리를 넘어서는 클래스/서비스로
>    발전하려는 순간
> 2. Task 1→Task 2 호출이 조건문·설정 파일·파서로 대체되려는 순간
>
> → 구현을 즉시 중단하고 `docs/02_rfc` → `docs/03_adc` → `docs/04_adr`
> 절차로 넘긴다. 직접 고치지 않는다.

그리고 같은 문서의 "Architecture 문제 발견 시 절차": 구현 중 Concept
누락·Boundary 모순을 발견하면 **코드로 메우지 않고** RFC로 기록한다.

## 4.4 각 ADC의 재검토 조건 (기존)

| 조건 | 열리는 항목 |
|---|---|
| 실제 Engine 호출 1회 관찰 | Context Boundary / Engine별 Renderer / 활용 사례·HQ 통합 |
| 두 번째 Renderer 또는 Ordering Policy 필요 | 확장 메커니즘 |
| 계약 변경으로 호환성 문제 발생 | Contract Versioning |
| 어휘가 두 번째 문서에서 필요해짐 | Ownership 어휘 / 3층 명명 |
| Identifier 이중성으로 실제 오류 1회 | Identity 구분 / Boundary 판정 / 어휘 승격 |
| Context 재사용·비교 사례 발생 | Identifier 파생 규칙 |
| §5의 6개 근거 해소 | Kernel Component Architecture (§10) |

---

# 5. Kernel Component Architecture

## **보류.**

### Evidence

`ADC-0005` 판단 1이 확인하고 `CLOSURE-0001` §4가 성격별로 분류한
`GOVERNANCE-REVIEW-0001` §5의 6개 근거 — **전부 지금도 유효하다.**

| # | 근거 | 부족한 것 | §2 구현으로 해소되는가 |
|---|---|---|---|
| 1 | §10 Out of Scope 유지 | 절차 | 아니다 |
| 2 | Kernel Module 3개 Defer | 관찰 | 아니다 |
| 3 | ADC-02(Runtime 존폐) Open | Architecture 결정 | 아니다 |
| 4 | Kernel 방향 승격 대상 없음 | 관찰 | 아니다 |
| 5 | Engine Gateway Trigger 미충족 | 관찰 | **아니다**(§3.3) |
| 6 | **Execution Result 미설계** | 관찰·구현 | **그렇다**(§2.1) |

**6건 중 §2 범위로 해소되는 것은 1건이다.**

### 판정 근거

- 지금 설계하면 §5의 근거 5건이 유효한 상태에서 여는 것이 되며,
  `ADC-0005` 판단 1 조건 3(*"이번 Accept를 다음 단계의 선례로 삼지
  않는다"*)이 그것을 막는다.
- 최근 2회의 RFC→ADC 사이클(RFC-0006·RFC-0007)이 **둘 다 문서
  작업이었고 둘 다 "관찰 없음"으로 정정·Reject**되었다. 세 번째
  문서 시도가 다른 결과를 낼 근거가 없다.

> **Implementation을 먼저 진행하며 Observation을 확보하는 것이
> Evidence가 가리키는 방향이다.** 다만 §3.3이 보여주듯 **§2 범위의
> 구현만으로는 Component 착수 조건이 충족되지 않는다** — 이 사실을
> 낙관적으로 서술하지 않는다.

---

# 6. Open Issues

**현재 존재하는 것만 기록한다. 새 Issue를 만들지 않는다.**

## 6.1 이번 검토에서 확인된 사실 충돌 1건

| 항목 | 내용 |
|---|---|
| **대상** | `docs/02_rfc/RFC-0005-development-hq-execution-boundary.md:52` |
| **진술** | *"LLM/ML 호출은 한 번도 추가되지 않았다(**`IMPLEMENTATION_RULES.md`의 금지 사항**이자…)"* |
| **확인 결과** | `IMPLEMENTATION_RULES.md`에 **LLM/ML/모델 호출을 금지하는 조항이 없다**(전수 검색). 금지 항목은 Gateway·Routing·Multi Engine 등 **추상화**에 대한 것이다 |
| **성격** | RFC 본문의 근거 인용 부정확. **RFC-0005는 후속 ADC가 없는 Open RFC**이므로 이 진술은 판단된 적이 없다 |
| **이 문서의 조치** | **기록만 한다.** RFC 본문 수정도, 이를 근거로 한 구현 허용 판단도 하지 않는다 |

> **이 항목을 "Engine 호출이 허용된다"는 결론으로 사용하지 않는다.**
> §2.2가 판정을 보류한 이유는 이 충돌이 아니라 **Development HQ 코드
> 수정 가부(O-8·O-9)가 확정된 적 없다는 사실** 때문이다.

## 6.2 기존 Open Issue (상태 변화 없음)

| 구분 | 항목 |
|---|---|
| **Architecture** | ADC.md 12건(NOW 3 / NEXT 6 / LATER 3), Kernel Module Defer 3건, Dev HQ RFC-0005 후속 ADC 미작성 |
| **Documentation** | D-6a(RFC 등록 표, D-9 의존) / D-9(RFC 상태 의미 미정의) / D-7(ADC namespace, 별도 절차 필요) / D-8(미작성 ADR 2건) / D-10(findings 미집계, 보류) / D-1·D-2·D-3·D-4(T3 보류) |
| **관찰 대기** | ADC-0003 Defer 4건, ADC-0004 Defer 2건, ADC-0006 Defer 2건, ADC-0007 Defer 3건, 4-Layer Context Model |
| **잔여 표기** | `development-hq/` 4곳의 "Architecture Baseline v1.0" — Phase 1 불변 제약 때문에 미정정 |

---

## Self Review

- 새 Architecture·Concept·Layer·Component 구조를 제안했는가 —
  **아니오**. §2는 이미 결정된 것(Execution Layer Accept,
  ARTIFACT-STANDARD가 예고한 자리) 안에서만 판단했다.
- 금지된 Component를 구현 가능으로 분류했는가 — **아니오**. §2.3에
  전부 구현 불가로 명시했다.
- 코드를 작성했는가 — **아니오**.
- RFC·ADC·ADR을 작성했는가 — **아니오**. §6.1의 사실 충돌도 기록만
  했다.
- Baseline을 수정했는가 — **아니오**.
- **권한 밖 판단을 했는가** — **아니오**. §2.2(Engine 호출)는 판정을
  보류하고 그 이유(확정된 적 없는 전제)를 명시했다.
- Observation을 추측했는가 — **아니오**. §3은 무엇이 **관찰 가능해지는지**
  만 적고 그 결과를 적지 않았다. §3.3에서 관찰되지 **않는** 것도
  명시했다.
- 낙관적으로 서술했는가 — **아니오**. §5가 "§2 구현으로 6개 중 1건만
  해소된다"를 명시했다.
- 새 Trigger를 만들었는가 — **아니오**. §4는 Rule A·B와
  `IMPLEMENTATION_RULES.md`의 기존 중단 트리거, 각 ADC의 기존 조건만
  정리했다.
- 새 Issue를 만들었는가 — **아니오**. §6.1은 문서 대조로 **발견된
  사실**이며 새 Issue 생성이 아니다.
