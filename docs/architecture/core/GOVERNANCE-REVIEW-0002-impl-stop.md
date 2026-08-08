# GOVERNANCE-REVIEW-0002: IMPL-STOP-0001 Governance 검토

**문서 성격**: Governance Review. **Decision 문서가 아니다.**
**대상**: `docs/core/execution-layer/IMPL-STOP-0001-execution-result.md`
의 Stop Trigger
**목적**: 이 Stop이 Governance에서 무엇에 해당하는지 판정한다.

이 문서는 Execution Result의 Contract를 설계하지 않는다. Artifact
schema·Component·Gateway·Adapter·Runtime·Registry·Scheduler·Routing을
만들지 않는다. Development HQ를 수정하지 않는다. Engine을 호출하지
않는다. RFC·ADC·ADR을 작성하지 않는다. Baseline을 수정하지 않는다.

**이번 검토에서 코드는 한 줄도 작성하지 않았다.**

---

# 0. 검토 중 확인한 사실 정정

**선행 문서들이 사용한 "Engine 호출 0회"라는 표현이 두 가지 서로 다른
사실을 뭉개고 있었다.** 원문 대조로 확인한 결과는 다음과 같다.

| 사실 | 값 | 출처 |
|---|---|---|
| **코드 경로 안의 실제 Engine 호출** | **0회** — `call_engine()`은 규칙 기반 응답을 반환한다 | `development-hq/mvp/engine.py:15-17` |
| **관찰된 실제 Engine 실행** | **3회** | `GOVERNANCE-REVIEW-0001` 133행: *"(ENGINE-INTEGRATION-0001~0003, **실제 Claude Code Engine 3회 실험**)"* |

**둘은 다르다.** 실제 Engine 실행 결과는 **이미 세 번 관찰되었다.**
관찰되지 않은 것은 "Engine 실행" 자체가 아니라 **그 산출물을 하나의
Artifact로 묶는 방식**이다.

이 정정은 §2·§5의 판정을 직접 바꾼다.

---

# 1. Stop Trigger Assessment

## 1.1 발동한 Trigger

`IMPLEMENTATION_RULES.md`가 아니라 이번 작업 지시가 정의한 Stop
Trigger 6개 중 **2번(주 사유)과 1번**이 발동했다.

| # | Trigger | 발동 | 근거 |
|---|---|---|---|
| 1 | 새 Architecture 결정 필요 | 발동 | Contract 후보 3개가 서로 다른 구조를 만든다 |
| **2** | **Standard만으로 Contract 결정 불가** | **발동(주)** | 아래 §1.2 |
| 3 | Registry/Gateway/Scheduler/Runtime 요구 | 미발동 | — |
| 4 | Agent-Capability 매핑 일반화 | 미발동 | 코드 미작성 |
| 5 | Task 호출 일반화 | 미발동 | 코드 미작성 |
| 6 | Dev HQ Boundary 변경 필요 | 미발동 | — |

## 1.2 발동 근거 (기존 Evidence만)

| ID | Evidence | 출처 |
|---|---|---|
| G-1 | 5개 Builder의 metadata 필드 13개가 예외 없이 identity/time/상수/상류재사용/enum이며 **content 필드 0건** | `mvp_0003~0005` 소스 |
| G-2 | `ARTIFACT-STANDARD-v1.md`가 *"그 자리를 예고만 할 뿐 설계하지 않는다"* | 8·149행 |
| G-3 | 세 실험이 *"하나의 Execution Result로 묶는 방식 — Unknown"*을 각각 기록 | ENGINE-INTEGRATION-0001·0002·0003 |
| G-4 | 저장소 어떤 문서도 Contract를 정한 적 없음(32개 지점 전수) | `IMPL-STOP-0001` N-4 |

## 1.3 분류 — Architecture / Evidence / Documentation

| 후보 | 판정 | 근거 |
|---|---|---|
| **Documentation** | **아니다** | 거짓 진술도, 색인 불일치도, 누락된 기록도 없다. G-2·G-3은 **의도적으로 남긴 미결**이며 정직하게 기록되어 있다 |
| **Architecture** | **아니다(아직)** | Architecture 문제라면 "결정이 필요한데 구조가 모순되거나 비어 있다"여야 한다. 여기서는 **결정의 입력**(실행 산출물의 형태)이 관찰되지 않았을 뿐, 기존 구조와 모순되는 것이 없다 |
| **Evidence 부족** | **그렇다** | G-3이 그 부족을 이름으로 지목한다 — 세 번 관찰하고도 관찰되지 않은 것이 있다 |

> ## 판정: **Implementation Evidence 부족.**

**이 판정은 이 프로젝트가 반복 사용한 형태와 같다** — ADC-0002 판단
2b(4-Layer), ADC-0003 판단 1b(파생 규칙), ADC-0007 판단 4(어휘 승격)가
전부 *"관찰된 적이 없어서 지금 확정하지 않는다"*로 처리되었다.

---

# 2. Contract Decision Readiness

## 2.1 세 후보 각각 — **어느 것도 채택하지 않는다**

각 후보를 **선택하려면 무엇이 관찰되어야 하는가**만 판단한다.

### 후보 1 — 단일 불투명 결과

| 항목 | 내용 |
|---|---|
| 선택에 필요한 관찰 | 실행 산출물이 **하나의 텍스트로 환원 가능하다**는 사실 |
| 현재 존재하는가 | **아니다.** ENGINE-INTEGRATION-0001이 관찰한 출력은 *"신규 파일 2개 + 수동 검증 로그 + pytest 결과 + git status 확인 + 구조화된 텍스트 보고"* — **이질적 복수 산출물**이었다 |
| 상태 | 관찰이 오히려 **반대 방향**을 가리키나, 환원 불가를 확정하는 관찰도 아니다 |

### 후보 2 — 산출물 목록

| 항목 | 내용 |
|---|---|
| 선택에 필요한 관찰 | 항목의 **종류와 경계가 안정적**이라는 사실 |
| 현재 존재하는가 | **아니다.** 세 실험의 산출물 구성이 서로 달랐다(0001: 신규 파일 / 0002·0003: 파일 수정·diff·진단 로그·텍스트 보고) |
| 추가 부담 | 채택 시 **5개 Builder의 단일 텍스트 구조를 벗어나는 첫 사례**가 된다(G-1) |

### 후보 3 — 결과 Reference

| 항목 | 내용 |
|---|---|
| 선택에 필요한 관찰 | 참조 대상을 **어디에 두는가**가 결정되어 있을 것 |
| 현재 존재하는가 | **아니다.** 저장 위치는 Memory 영역이며 Kernel ADC-0001에서 **Defer**되었다 |
| 추가 부담 | 채택 시 **Defer된 항목을 여는 것**이 된다 |

## 2.2 판정

> **현재 Evidence로는 세 후보 중 어느 것도 선택할 수 없다.**
> 부족한 Evidence는 **"실행 산출물이 어떤 단위로 묶이는가"** 하나이며,
> 세 실험이 그것을 이름으로 지목해 남겨 두었다.

---

# 3. Governance Assessment

**세 절차를 독립적으로 판단한다. "RFC가 필요하다"를 자동으로 내리지
않는다.**

| 절차 | 필요 여부 | 근거 |
|---|---|---|
| **RFC** | **불필요** | (a) Rule A·Rule B 어느 것도 충족되지 않았다(§4). (b) Governance 핵심 원칙 *"Re-evaluate Only After New Observation"*, *"Accumulate Before Escalate"*에 반한다. (c) **선례가 있다** — RFC-0006·RFC-0007이 관찰 없이 문서 작업으로 시도되어 각각 정정·Reject되었다. 세 번째 시도가 다른 결과를 낼 근거가 없다 |
| **ADC** | **불필요** | `ARCHITECTURE_GOVERNANCE.md`의 채택 기준 2개 중 **어느 것도 만족하지 않는다.** 기준 1(지금 결정하지 않으면 상위 Architecture 진행 불가): Execution Result 미구현으로 막히는 것은 `GOVERNANCE-REVIEW-0001` §5의 근거 6번 하나이며, 그것만 해소해도 Component는 열리지 않는다(`IMPL-STOP-0001` §8). 기준 2(늦어질수록 되돌리는 비용 증가): 관찰 없이 고른 Contract를 나중에 바꾸는 비용이 더 크다 |
| **ADR** | **불필요** | ADR은 ADC의 결정을 문서 변경으로 옮기는 단계다. 선행 ADC가 없으므로 옮길 결정이 없다 |

## 3.1 그렇다면 현재 상태는

> **Evidence 부족 상태로 유지한다.**

**이 프로젝트에는 그 상태를 위한 계층이 이미 있다** — Governance v2의
Observation(OBS) 계층이며, 그 원칙이 *"Observe First, Decide Later /
Accumulate Before Escalate"*다.

**다만 이 문서는 OBS를 작성하지 않는다** — §4.3이 기록하듯 그 판단은
이 검토의 범위가 아니다.

---

# 4. Existing Re-entry Trigger

**기존 Rule A / Rule B / ADC 재검토 조건만 사용한다. 새 Trigger를 만들지
않는다.**

## 4.1 Rule A — RT Trigger 충족 → RFC

| RT-0001 Candidate | Trigger | 충족 |
|---|---|---|
| 1. Task Dispatcher | Workflow Branch 발생 또는 체인 ≥ 2 | ADC-0004에서 재판단 완료(Keep) |
| 2. Engine Gateway | **Engine 수 ≥ 2** | **미충족** — 세 실험 모두 Claude Code 하나 |
| 3. Agent Registry | HQ 수 ≥ 2 | **미충족** |
| 4. Context 전달 메커니즘 | Context 전달 경로 ≥ 2 | **미충족** |

## 4.2 Rule B — 동일 Tag OBS 3회 → RFC

**Rule B의 판정 단위는 `Tag`를 가진 OBS 문서다**(`docs/governance/
observations/README.md`: *"동일한 `Tag`를 가진 **OBS 문서**가 3개 이상
존재하고 서로 모순되지 않을 때"*).

| 확인 | 결과 |
|---|---|
| ENGINE-INTEGRATION-0001~0003은 OBS 문서인가 | **아니다.** `docs/research/` 소재이며 `Tag` 필드가 없다 |
| Execution Result 주제의 OBS가 존재하는가 | **없다.** 기존 OBS 6건의 Tag는 Task Dispatcher(2) / Context 전달 메커니즘(1) / Other(3) |
| **판정** | **Rule B는 이 주제에 대해 충족되지 않았다** |

### 4.2.1 별건으로 확인된 사실 (Execution Result와 무관)

**Tag `Other`를 가진 OBS가 3건 존재한다**(OBS-0004·0005·0006, 전부
Status `Open`). Rule B의 수치 조건은 문언상 충족된다.

다만 그 셋은 Validation Capability(0004·0005)와 Planning/Design
Capability 구조화(0006)로 **주제가 다르며**, `Other`는 포괄
Tag다. **이 사실은 Execution Result와 무관하며, 이 문서는 그것을
판단하지 않는다** — 사실로만 기록한다.

## 4.3 Rule A·B 공통 사실

**두 Rule 모두 입력이 OBS 문서다.** Rule A조차 *"하나 이상의 **OBS
문서**가 … Trigger가 실제로 충족되었다는 사실을 기록하면"*으로
정의되어 있다.

`IMPL-STOP-0001`은 OBS 문서가 아니다. 따라서 **그 문서의 존재만으로는
어떤 Rule도 발동시키지 않는다.** 이는 결함이 아니라 형식의 문제이며,
**이 검토는 OBS 작성 여부를 판단하지 않는다.**

## 4.4 ADC 재검토 조건 7종

| 조건 | 충족 |
|---|---|
| **실제 Engine 호출 1회 관찰** | **부분 충족.** §0이 확인했듯 실제 Engine 실행은 3회 관찰되었다. 그러나 ADC-0003 판단 4의 조건은 *"실제 Engine 호출이 최소 1회 관찰되고, **그 호출에서 '매번 동일하게 앞에 놓이는 Context 구간'이 실측으로 확인되면**"*이며, **뒤 절이 충족되지 않았다** — ENGINE-INTEGRATION-0001이 *"Model Request, Execution Handle, Execution State가 실제로 Claude Code에 입력된 적은 없다"*고 기록했다 |
| 두 번째 Renderer / Ordering Policy 필요 | 미충족 |
| 계약 변경으로 호환성 문제 발생 | 미충족 |
| 어휘가 두 번째 문서에서 필요해짐 | 미충족 |
| Identifier 이중성으로 실제 오류 1회 | 미충족 |
| Context 재사용·비교 사례 발생 | 미충족 |
| §5의 6개 근거 해소 | 미충족 |

> ## 판정: **기존 Trigger 중 이 Stop으로 충족된 것은 없다.**
> ADC-0003 판단 4의 조건만 **부분 충족**이며, 그 미충족 부분이 이번
> Stop이 드러낸 것과 같은 영역이다.

---

# 5. Engine Observation Requirement

**기존 문서에 기록된 것만 정리한다. 구현하지 않는다.**

§0의 정정에 따라, 필요한 것은 "Engine 실행"이 아니다 — 그것은 이미 3회
관찰되었다. 기존 문서가 **아직 관찰되지 않았다고 명시한 것**은 다음
둘이다.

| ID | 기존 문서가 기록한 미관찰 항목 | 출처 |
|---|---|---|
| **R-1** | *"**Model Request, Execution Handle, Execution State를 Claude Code에 직접 입력했을 때** 어떤 입력/출력이 관찰될지 — 이번 실험은 **Prompt Specification만** 시험했다"* | ENGINE-INTEGRATION-0001 Unknowns |
| **R-2** | *"여러 개별 산출물을 **하나의 Execution Result로 묶는 방식**이 무엇이어야 하는지 — Unknown이며 이 문서는 답하지 않는다"* | ENGINE-INTEGRATION-0001·0002·0003 |

## 5.1 두 항목의 관계

**R-1이 충족되지 않으면 R-2를 관찰할 수 없다.** 체인의 뒤 세 Artifact가
한 번도 Engine 입력이 된 적이 없으므로, 그 경로에서 무엇이 산출되는지가
관찰될 기회 자체가 없었다.

## 5.2 이 절이 정하지 않는 것

- R-1을 **어떻게** 충족할 것인가 — 실험 설계는 이 문서의 범위가 아니다.
- Engine 호출·Adapter·Gateway — **금지 사항이며 다루지 않는다.**
- Development HQ 수정 가부 — `IMPL-ENTRY-0001` §2.2가 판정을 보류했고
  이 문서도 판정하지 않는다.

---

# 6. A / B / C 구분

| 문장 | 현재 Evidence가 말하는 것 |
|---|---|
| **A. "Execution Result가 필요하다"** | **미확정.** `ARTIFACT-STANDARD-v1`이 자리를 예고하고 Artifact 5의 Consumer 칸을 비워 두었으며, `RFC-0001-jarvis-os-core-baseline` 86행이 Execution Result를 Kernel 공통 Artifact의 예로 들었다. 그러나 **필요 여부를 판단한 ADC가 없다.** "자리가 예고되어 있다"와 "필요하다고 결정되었다"는 다르다 |
| **B. "Contract를 지금 결정할 수 있다"** | **아니다.** §2 — 세 후보 어느 것도 선택 근거가 없다 |
| **C. "관찰을 위한 실제 Engine 실행이 필요하다"** | **부분적으로 이미 충족.** 실제 Engine 실행은 **3회 관찰되었다**(§0). 미관찰인 것은 더 좁다 — R-1(뒤 세 Artifact를 입력으로 한 실행)과 R-2(산출물 묶음 방식) |

**C의 정정이 이번 검토의 실질적 결과다.** "Engine을 한 번 돌리면
된다"가 아니라, **"체인의 뒤쪽 Artifact를 입력으로 한 실행이 관찰된 적
없다"**가 정확한 상태다.

---

# 7. Final State

> ## **Hold for Evidence**

| 후보 | 판정 | 근거 |
|---|---|---|
| Continue Implementation | **아니다** | Contract를 결정할 수 없으므로 코드를 이어 쓰면 §2의 후보 중 하나를 암묵적으로 선택하게 된다 |
| **Hold for Evidence** | **그렇다** | §1.3(Evidence 부족), §3(RFC·ADC·ADR 전부 불필요), §4(기존 Trigger 미충족) |
| Re-enter Architecture Governance | **아니다** | Rule A·B 미충족(§4), ADC 채택 기준 미충족(§3). 관찰 없이 재진입하면 RFC-0006·0007의 반복이 된다 |

## 7.1 이 판정이 뜻하지 않는 것

- *"Execution Result 설계에 실패했다"* — 아니다. 설계를 시도하지
  않았고, 시도할 수 없다는 사실을 **구현 착수 과정에서 확인**했다.
- *"Architecture가 부족하다"* — 아니다(§1.3).
- *"영구히 막혔다"* — 아니다. R-1·R-2가 관찰되면 §2의 세 후보를 판단할
  근거가 생긴다.

---

## Self Review

- Execution Result의 Contract를 설계했는가 — **아니오**. §2는 세 후보에
  대해 **필요한 관찰이 존재하는지**만 판단했고 어느 것도 채택하지
  않았다.
- 새 Artifact schema·Component·Gateway·Adapter·Runtime·Registry·
  Scheduler·Routing을 만들었는가 — **아니오**.
- Development HQ를 수정했는가 — **아니오**. Engine을 호출했는가 —
  **아니오**. 코드를 작성했는가 — **아니오**.
- RFC·ADC·ADR을 작성했는가 — **아니오**. §3이 셋 다 불필요로
  판정했다.
- Baseline을 수정했는가 — **아니오**.
- 새 Trigger를 만들었는가 — **아니오**. §4는 Rule A·B와 RT-0001,
  각 ADC의 기존 조건만 대조했다.
- "RFC가 필요하다"를 자동으로 내렸는가 — **아니오**. 세 절차를 각각
  독립 판단했고 셋 다 불필요다.
- 선행 문서의 부정확을 발견했는가 — **발견했고 정정했다**(§0).
  "Engine 호출 0회"가 코드 경로(0회)와 관찰된 실행(3회)을 뭉개고
  있었다. 이 정정이 §2·§5·§6 C의 판정을 바꿨다.
- 새 해석을 만들었는가 — **아니오**. §1.3의 분류는 ADC-0002 판단 2b·
  ADC-0003 판단 1b·ADC-0007 판단 4가 이미 쓴 형태를 그대로 적용했다.
