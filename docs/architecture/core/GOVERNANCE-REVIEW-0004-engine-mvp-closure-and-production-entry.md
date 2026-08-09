# GOVERNANCE-REVIEW-0004: Engine MVP Validation 종료 판정 및 Production 단계 진입 가능 영역 전수 점검

**문서 성격**: Governance Review. **Decision 문서가 아니다.** 새 RFC/ADC/ADR을
작성하지 않는다. 새 Architecture/Concept을 설계하지 않는다. Production
caller를 임의로 설계하거나 Accept하지 않는다. Runtime/Kernel Component
Architecture를 근거 없이 착수하지 않는다. ADC-0010·ADC-0011의 기존 판단을
재조사하거나 변경하지 않는다 — 있는 그대로 인용하고 종합한다. **이번 검토에서
코드는 한 줄도 작성하지 않았다.**

## 목적

기존 문서(`docs/architecture/core/ADC-0010`, `ADC-0011`,
`GOVERNANCE-REVIEW-0003`, `docs/research/ENGINE-CONNECT-0001~0006`,
`docs/01_mvp/MVP-0026~0037`, `docs/03_adc/ADC.md`)와 실제 MVP Evidence를
한 번에 종합해, 다음 두 질문에 답한다.

1. Engine MVP 검증을 종료 대상으로 분류할 수 있는가?
2. 현재 Architecture/Governance에서 Production 단계로 넘어가기 위해 실제로
   착수 가능한 작업은 무엇인가 — Implementation 가능한 것, Governance가
   필요한 것, HOLD해야 하는 것, 선행조건이 되는 것을 구분한다.

새 Evidence·실험을 만들지 않는다. 기존 문서가 이미 내린 판단(특히 ADC-0010
C1~C6 전부 Not Accepted, ADC-0011 Not Accepted)은 그대로 인용만 한다.

---

## ① Engine MVP 종료 여부

**종료 대상으로 분류한다.**

Engine MVP 범위(단일 Engine 호출, caller 수준 연결, `ExecutionResult`
단일/다중 결과, 주요 workflow의 실패 처리)에서 실제 Evidence로 검증되지
않은 항목을 찾지 못했다.

| 검증 항목 | Evidence | 상태 |
|---|---|---|
| Engine success path (caller → `call_engine()` → 실제 Engine → `results` → `ExecutionResult`) | `ENGINE-CONNECT-0002`(단일 Builder), `ENGINE-CONNECT-0005`(6개 Builder 전체 Pipeline, 실제 Implementation Specification, 실제 Prompt Specification) | 완료 |
| `results: list[str]` 단일 항목 | `ENGINE-CONNECT-0002`, `ENGINE-CONNECT-0005` (2회 재현) | 완료 |
| `results: list[str]` 다중 항목(2개) | `ENGINE-CONNECT-0006` (실제 Engine 2회 독립 호출, verbatim 보존·순서·경계 확인) | 완료 |
| Engine timeout 실패 경로 — `run_mvp_0001()` | `MVP-0036` (real forced timeout 2초, uncaught crash 재현 → 수정 → 재검증) | 완료 |
| Engine timeout 실패 경로 — 나머지 5개 주요 workflow 진입점(`run_mvp_0002`, `run_pipeline`, `run_comparison`/`run_issue_to_planning_with_bundle`, `run_issue_to_implementation`, `run_issue_to_planning`, `run_issue_to_design`) | `MVP-0037` (동일 방법으로 6개 전부 재현·수정·재검증) | 완료 |
| CLI/`__main__` 진입점 real subprocess 실행 | `MVP-0034`(`cli.py`), `MVP-0035`(`workflow_0009.py __main__`) | 완료 |
| Production 승격 시도(caller 위치 확보 여부) | `ENGINE-CONNECT-0003`(Blocked), `ENGINE-CONNECT-0004`(C6 조사, 근거 부족) | 조사 완료 — **Blocked라는 결론 자체가 Engine MVP 범위 밖의 질문**(Q3 참조) |

회귀 확인: `python3 -m pytest development-hq/mvp/tests core/execution_layer -q`
— 이번 검토에서 재실행, **58 passed**, `git status --porcelain` 무변경.
기존 Evidence 문서가 기록한 값과 일치.

**남은 것은 있는가 — 있으나 Engine MVP Exit Criteria와 무관하다.**

- `ENGINE-CONNECT-0006` §Unknowns: `results` 3개 이상 항목, 또는 서로
  다른 형태(fenced code block ↔ 단순 텍스트)가 섞인 경우는 미관찰.
  그러나 `development-hq/MVP.md` Exit Criteria(수동 개입 없이 Code
  Review → Test Case 순서 반환)도, 현재 어떤 workflow도 3개 이상의
  `results` 항목을 실제로 생성하지 않는다 — 이 Unknown을 메우는 것은
  존재하지 않는 시나리오를 위한 선제적 Evidence 수집이며, 이번 작업
  지침("단순 Evidence 수집을 위해 RFC/ADC를 잘게 쪼개지 않는다")과도
  맞지 않는다. **Non-blocking Open 항목으로 기록하고 종료 판정에서
  제외한다** — 실제로 3개 이상 항목을 만드는 workflow가 생길 때 다시
  열릴 항목이다.

**결론**: Engine MVP는 success path, failure path(전 workflow), 단일/다중
`results` 모두 real Engine으로 검증되었고, 검증되지 않은 유일한 항목은
현재 존재하지 않는 시나리오다. **Engine MVP Validation 종료 대상으로
분류한다.**

---

## ② 현재 Production 단계의 Blocking

**단 하나 — Production caller의 배치 위치가 없다.**

`ADC-0010`(RFC-0010 후속)이 caller 후보 6개(C1~C6)를 전수 조사해 전부
Not Accepted로 판단했고, `GOVERNANCE-REVIEW-0003`이 `ENGINE-CONNECT-0005`
Evidence로 재평가했으나 6개 후보 중 재검토 조건을 충족한 것은 없었다(§부족한
Evidence 1~6, 미충족 확인). `ADC-0011`은 "Kernel/HQ에 속하지 않는 별도
실행 위치"를 공식 Concept으로 둘 수 있는지 자체도 Not Accepted로 남겼다 —
C6("별도 스크립트/함수")의 존립 근거가 되는 상위 질문조차 아직 답이 없다.

`ENGINE-CONNECT-0003`이 명시적으로 확인한 대로, 기술적 배선(Q1·Q2)에는
문제가 없다 — 문제는 오직 "어디에 두는가"(Q3)다. 이 공백이 메워지지 않는 한
caller 위치가 필요한 모든 작업(Production 승격)은 진행할 수 없다.

이번 검토는 이 Blocking을 재조사하지 않았다 — 기존 판단(ADC-0010,
ADC-0011, GOVERNANCE-REVIEW-0003)을 그대로 인용했다. **판단을 임의로
변경하지 않는다는 지침을 그대로 따랐다.**

---

## ③ 지금 즉시 구현 가능한 작업

**Production caller 위치가 필요 없는 작업만 해당된다.**

| 후보 | 근거 | 비고 |
|---|---|---|
| Development HQ Capability Engineering 계속 (`development-hq/CONSTITUTION.md`: Architecture < Capability < Dogfooding < Observation < Evidence) | Engine MVP·Production caller와 무관하게 계속 가능. `projects/development-hq-devkit`류의 Dogfooding 확장이 여기 해당 | caller 위치 결정 불필요 |
| `OBS-0003~0006`(Open 상태, Context 전달/Capability 확장 관련 Fact)을 근거로 한 추가 Dogfooding 관찰 축적 | 기존에 이미 진행 중이던 트랙, 새 Architecture 결정 불필요 | Governance로 전환할지는 Evidence가 쌓인 뒤 별도 판단 |
| Engine MVP 자체의 신규 Implementation | 없음 — ①에서 확인한 대로 Engine MVP 범위는 이미 종료 대상 | 추가 구현 여지 없음 |

**Production 트랙에서 지금 즉시 구현 가능한 작업은 없다.** caller 위치가
없는 상태에서 무엇을 구현하든 그 배치 자체가 새 Architecture 결정(caller
위치 확정)이 되므로, 이번 작업 지침("Production caller를 임의로 설계하거나
Accept하지 않는다")과 충돌한다.

---

## ④ Governance가 필요한 작업

| 작업 | 필요한 절차 | 근거 |
|---|---|---|
| C6("별도 스크립트/함수") 구체화 | 새 RFC — 이름·소속 네임스페이스·Engine Adapter 배제 원칙과의 관계 | `ADC-0010` §부족한 Evidence 6, `ENGINE-CONNECT-0004` §Q4 |
| "Kernel/HQ 밖 제3의 실행 위치" Concept 자체의 존립 여부 | 새 RFC — Concept Model 확장 가능성(닫힌 분류인지), System Boundary가 exhaustive인지에 대한 원 저작 의도 확인 | `ADC-0011` §부족한 Evidence 1·3 |
| C1(Kernel Engine Port/Adapter) | Kernel Component Architecture 설계 착수 — Kernel Module Defer 3건, ADC-01·ADC-02, Engine 수 ≥2 등 다수 선행조건 | `ADC-0010` §부족한 Evidence 1 |
| C2(Runtime) | `ADC-0008`(ADC-02, Runtime 존폐) 재검토 조건 충족 | `ADC-0010` §부족한 Evidence 2 |
| C3(Session) | Session을 Kernel Concept Model에 등재하는 새 RFC | `ADC-0010` §부족한 Evidence 3 |
| ADC-01·ADC-02·ADC-09·ADC-10(Kernel ADC, 우선순위 NOW) | 각각 별도 RFC → ADC → ADR | `docs/03_adc/ADC.md` — 여전히 Open, 이번 검토로 진전 없음(범위 밖) |

C4(Development HQ)는 Freeze 목록 자체를 재론해야 하며 Phase 1 종료 후
불변 원칙과 충돌 — 사실상 Governance 경로가 막혀 있다. C5(Dogfooding
스크립트)는 "승격 시도가 실제로 관찰·제안되어야" 하는데 현재 그런 시도가
없다 — 새 RFC보다는 실제 제안이 선행되어야 열리는 항목이다.

---

## ⑤ HOLD 작업

| 항목 | HOLD 이유 |
|---|---|
| `results` 3개 이상 항목 / 서로 다른 형태 혼합 Evidence 수집 (`ENGINE-CONNECT-0006` Unknowns) | 실제로 그런 시나리오를 만드는 workflow가 없다 — 선제적 Evidence 수집 금지 지침과 충돌 |
| C1(Kernel Engine Port/Adapter) 착수 | 다수 선행조건(Kernel Module Defer 3건, ADC-01·02, Engine 수 ≥2) 미충족 |
| C2(Runtime)를 caller로 지정 | Runtime 존재 자체가 Open(ADC-02) |
| C4(Development HQ)를 caller로 지정 | Architecture Freeze 목록(Engine Adapter, Model Routing)과 정면 충돌 |
| C5(Dogfooding 스크립트) production 승격 | 승격 시도 자체가 관찰된 적 없음 |
| Kernel Component Architecture 전반 | `BASELINE.md` §10 Out of Scope, 근거 없이 착수 금지 지침 |

---

## ⑥ 전체 Dependency 순서

```
[완료] Engine MVP 검증
  (success path / failure path 전 workflow / results 단일·다중 / CLI 진입점)
        │
        ▼
[Blocking] Production caller 위치 미확정 (ADC-0010 C1~C6 전부 Not Accepted)
        │
        ├── C6 구체화 RFC (이름·네임스페이스·Engine Adapter 관계)  ─┐
        │                                                          ├─→ ADC 재검토 → (Accept 시) ADR → Baseline Update
        └── "제3의 실행 위치" Concept 존립 RFC (ADC-0011 선행질문)  ─┘        │
                                                                              ▼
                                                                  Production caller 구현
                                                                  (위치 확정 후에만 가능)
                                                                              │
                                                                              ▼
                                                        C1(Kernel Engine Port/Adapter) 등
                                                        더 큰 Kernel Component 결정은
                                                        그 이후, 별도 선행조건 충족 후에만
```

C1(Kernel Port/Adapter)이 원칙적으로 "가장 올바른" 위치라는 점은 `BASELINE.md`
§7에 책임이 귀속되어 있다는 사실로 이미 드러나 있지만, 그 실체(설계)를
지금 만드는 것은 §10 Out of Scope이자 다수 선행조건 미충족이므로 순서상
가장 나중이다. C6·ADC-0011 경로가 유일하게 "새 RFC 하나"만으로 진입
가능한 지점이라는 점에서 실질적인 다음 관문이다.

---

## ⑦ 다음 단 하나의 작업

**C6("별도 스크립트/함수") 후보를 구체화하는 새 RFC 착수 여부를 판단한다.**

이유: ②~⑥에서 확인한 대로, Production 단계로 나아가는 유일한 경로는
caller 위치 확정이고, 6개 후보 중 C6만이 "새 RFC 하나"라는 단일하고 구체적인
선행조건을 갖는다(`ADC-0010` §부족한 Evidence 6). 나머지 후보(C1·C2·C3)는
Kernel Component Architecture 착수·ADC-02 재검토·새 Concept 등재처럼 이번
작업 지침이 금지한 더 무거운 선행조건에 걸려 있고, C4·C5는 사실상 근거가
없다. 이 RFC는 ADC-0011이 남긴 "제3의 실행 위치가 Concept으로 성립
가능한가"라는 선행 질문(§부족한 Evidence 1·3)도 함께 다뤄야 완결된다 —
두 질문이 서로 다른 문서(ADC-0010/ADC-0011)에 흩어져 있지만 동일한 caller
위치 문제의 앞뒤 절반이기 때문이다.

**이 RFC는 이번 검토의 범위가 아니다** — 이번 검토는 이 RFC의 필요성만
식별했을 뿐, 작성하지 않았다(작업 지침: "Production caller를 임의로
설계하거나 Accept하지 않는다", "새 Architecture 결정이 실제로 필요할
때만 Governance로 전환한다"). RFC 작성 여부와 시점은 별도 세션에서
결정한다.

---

## Stop Trigger / 조사 범위 대조

| 확인 항목 | 결과 |
|---|---|
| Production 코드 변경 | **없음** |
| ADC-0010 C1~C6 재조사 | **없음** — 상태만 인용 |
| ADC-0011 재조사 | **없음** — 상태만 인용 |
| ADC-01·ADC-02(Kernel ADC.md) 재조사 | **없음** — Open 상태만 인용 |
| 새 RFC/ADC/ADR 작성 | **없음** |
| 새 Architecture/Concept/Component 도입 | **없음** |
| Production caller 위치를 임의로 선택 | **없음** |
| Kernel/Runtime Component Architecture 착수 | **없음** |

## Self Review

- Evidence만 사용했는가 — **Pass**. `ADC-0010`, `ADC-0011`,
  `GOVERNANCE-REVIEW-0003`, `ENGINE-CONNECT-0002~0006`,
  `MVP-0026~0037`, `docs/03_adc/ADC.md`, `development-hq/CONSTITUTION.md`
  만 인용했다. 이번 검토에서 새로 실행한 것은 기존 테스트 스위트
  재실행(`pytest`, 58 passed, 회귀 확인 목적)뿐이다.
- ADC-0010·ADC-0011의 기존 판단을 임의로 변경했는가 — **아니오**.
  전부 그대로 인용했다.
- Production caller를 설계하거나 Accept했는가 — **아니오**.
- Kernel/Runtime Component Architecture에 착수했는가 — **아니오**.
- Engine MVP 종료를 근거 없이 선언했는가 — **아니오**. 검증 항목별
  Evidence 표(§①)로 근거를 남겼고, 남은 Unknown(3개 이상 results
  항목)도 숨기지 않고 Non-blocking으로 명시했다.
- 새 RFC/ADC/ADR을 작성했는가 — **아니오**. 다음 단계로 필요성만
  식별했다.
- 불필요한 변경을 확인했는가 — **예**. 이 문서 추가 외 다른 파일은
  수정하지 않았다(`git status --porcelain` 확인).
