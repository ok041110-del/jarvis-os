# ADC-0018: 자연어 요청 → Multi-HQ Task 분해 공통 책임 존재 여부 판단 (RFC-0018 후속)

## 목적

`docs/architecture/core/RFC-0018-natural-language-request-multi-hq-task-decomposition.md`
§6이 연 Boundary Question을 판단한다.

> 하나의 자연어 사용자 요청에서 복수 HQ와 독립 Task를 식별하고, 이를 실행 가능한
> 구조화 요청으로 변환하는 공통 책임이 필요한가?

이 ADC는 RFC-0018의 결론을 반복하지 않는다 — RFC-0018은 Decision을 내리지 않았으므로
반복할 결론 자체가 없다. 이 ADC는 RFC-0018이 수집한 Evidence를 독립적으로 재평가해
Accept/Defer/Reject 중 하나를 스스로 판단한다.

### 이 ADC가 답하지 않는 것

- Conversation Layer라는 이름·Component의 확정
- HQ Router/Task Planner Component의 확정
- Agent Assignment 자동화(동적 Task→Agent 할당) 여부
- Scheduler/우선순위/Workflow orchestration 도입 여부
- Retry/Recovery 정책
- 새로운 Public Contract/Interface
- Dashboard UI
- `docs/decisions/adc/ADC.md`의 ADC-02(Runtime 개념의 존폐) 자체의 재판단

---

## Q0. Architecture Intent만으로 지금 판단할 수 있는가

### Evidence

`BASELINE.md` §6 Concept Model은 "Runtime은 Workflow를 참조하여 Task를 Agent에게
배분한다"고 이미 기술하고 있다. 이 문장만 보면 "자연어 요청 → Task 배분"까지 이미
Architecture Intent에 포함된 것처럼 읽힐 수 있다.

그러나 §6의 이 문장은 **Task가 이미 존재한다는 것을 전제**로 "그 Task를 누구에게
배분하는가"만 다룬다 — "자연어 요청에서 Task 자체를 어떻게 만들어내는가"는 다루지
않는다. 그리고 ADC-02(Runtime 존폐)가 Open인 이상, §6의 이 문장 자체가 아직 Kernel
수준에서 확정된 책임이 아니다.

### Q0 결론

Architecture Intent만으로는 판단할 수 없다. RFC-0018 §5의 실제 코드 Evidence와
결합해야 한다.

---

## Q1. 실제 필요성 — RFC-0018 §5 Evidence를 독립적으로 재검토

### 검토

RFC-0018 §5는 다음을 "사실"로 기록했다:

- `cli.py`는 원문을 그대로 `run_mvp_0001(code)`에 전달한다.
- `run_comparison()`은 이미 고정된 두 Task를 병렬 실행할 뿐, 자연어에서 Task를
  만들어내지 않는다.
- `hqs/investment/run.py`는 `team`을 호출자가 CLI 인자로 직접 지정해야 한다.
- 자연어 → Multi-HQ → Task 공통 계층은 조사 범위에서 확인되지 않았다.

이 ADC는 이 Evidence를 그대로 받아들이되, **그 의미를 RFC와 다르게 평가한다**.
RFC-0018의 Evidence는 전부 "부재 증명"(이런 코드가 없다)이지 "필요 증명"(이게 없어서
실제로 문제가 생겼다)이 아니다. 지금까지의 Governance Chain에서 Accept로 이어진
모든 사례는 반드시 **실제 필요가 발생한 사건**을 근거로 삼았다:

- ADC-0013(Execution Host): 5개 Prototype·Vertical Slice에서 부재 시 실제
  정확성 결함이 **재현**됐다.
- ADC-0016(Multi-Task): `workflow_0009.py`의 `run_comparison`이 **실제로 merge된
  Production Code**로 이미 존재했다(관찰 1건이지만 "이미 일어난 일"이다).
- ADC-0017(Result Store): `pg-hq-verify` 등에서 손상된 결과 저장이 **4회 재현**됐다.

RFC-0018의 Evidence는 이 세 사례 중 어느 것과도 같은 성격이 아니다 — "이런 요청을
실제로 시도했다가 실패했다"는 사건이 하나도 없다. §3의 Prototype Scenario("AAPL
투자 분석과 개발 상태 분석을 각각 수행해줘")는 RFC 자신도 "실제로 실행하지 않았다"고
명시한 가설이다.

이 ADC는 추가로 `docs/research/` 전체와 양 HQ의 `dogfooding/` 디렉터리를 검색해,
Multi-HQ 자연어 요청 라우팅/분해가 실제로 시도되거나 논의된 기록이 있는지
확인했다 — **일치하는 기록이 없다**. Investment HQ와 Development HQ는 지금까지
완전히 독립적으로 dogfooding됐고, 하나의 요청이 두 HQ에 걸쳐 처리된 사례가
Repository 어디에도 없다.

### Q1 결론

책임의 **구조적 공백**(gap)은 Evidence로 확인된다 — 이 부분은 RFC-0018과 같은
결론이다. 그러나 그 공백을 메워야 할 **필요성**은 아직 실제 사건으로 뒷받침되지
않는다. "코드가 없다"는 "필요가 없다"의 증거도 아니지만 "필요가 있다"의 증거도
아니다 — 이 ADC는 이 둘을 명확히 구분한다.

---

## Q2. Evidence 수량 — Rule B(3건 이상 독립 관찰) 충족 여부, 그리고 이번 사례의 특수성

### 검토

Governance v2 Rule B는 정상적으로 3건 이상의 독립 관찰을 Accept의 기본 조건으로
요구한다. ADC-0016은 1건뿐이었지만 Scope를 극도로 좁혀 Accept를 정당화했다 — 그러나
그 1건은 **이미 merge된 실제 코드**였다는 점에서, 이번 사례와 근본적으로 다르다.

이번 ADC-0018의 관찰 수량은 **0건**이다 — 실제로 발생한 Multi-HQ 자연어 요청
처리 시도가 하나도 없다. ADC-0016의 "관찰 1건"과 ADC-0018의 "관찰 0건"을 같은
논리로 다뤄 Accept를 정당화하면, Rule B의 취지("실제로 반복 관찰된 필요만
Kernel 책임으로 승격한다")를 무너뜨린다.

Scope를 아무리 좁혀도, 좁힐 대상이 되는 실제 사례 자체가 없다는 것은 ADC-0016의
논리(Scope를 좁혀 1건으로도 Accept)를 그대로 적용할 수 없게 만든다 — 무엇을 위해
Scope를 좁히는지 판단할 실제 사례가 없기 때문이다.

### Q2 결론

Rule B를 충족하지 못하며, 이번에는 ADC-0016처럼 Scope를 좁혀 예외적으로 Accept할
근거도 없다(예외를 정당화했던 "실제 merge된 코드"라는 전제 자체가 없다). **관찰
0건은 Accept의 근거가 되지 못한다.**

---

## Q3. Request Interpretation / HQ Routing / Task Decomposition / Agent Assignment — 책임 경계 개별 검토

RFC-0018 §4의 매핑을 이 ADC가 독립적으로 재검토한다. 이 네 책임을 하나로
뭉뚱그리지 않고 각각 판단한다.

### Request Interpretation (자연어 → 의도 구조화)

**검토**: 조사 범위에서 어떤 형태로도 발견되지 않았다. Dev HQ CLI, Investment HQ
`run.py` 모두 이미 구조화된 입력(코드 문자열, 명시적 CLI 인자)을 전제한다. 이
책임이 필요한지 자체가 이 ADC의 판단 대상이 아니라 — **필요성을 판단할 실제 사례가
없다**는 것이 Q1·Q2의 결론이다.

### HQ Routing (어느 HQ가 담당하는지 식별)

**검토**: `hqs/investment/run.py`의 `TEAMS` 딕셔너리는 **HQ 내부** Team 선택
패턴(리터럴 매핑)의 실제 사례이지, **HQ 간** 선택 사례가 아니다. 이 패턴이
HQ Routing에도 적용 가능한 구조라는 것(리터럴 매핑으로 시작할 수 있다는 것)은
참고할 만하지만, HQ 간 선택이 실제로 필요했던 사례는 없다.

### Task Decomposition (요청 → Task 단위 분해)

**검토**: `run_comparison()`은 이미 고정된 Task 2개를 병렬 실행할 뿐, 어떤 입력을
Task로 "분해"하는 로직이 없다. 이 책임의 부재는 명확하지만, Multi-Task(§16.4)가
이미 "이미 코드/설계에 고정된 Task"를 전제로 Accept됐다는 것과 정합적이다 — 즉
지금까지 필요했던 모든 실제 사례에서 Task는 사람이 미리 고정해 왔고, 그것으로
충분했다.

### Agent Assignment (Task → 기존 Agent/Team 연결)

**검토**: `TEAMS` 딕셔너리, `hqs/development/mvp/agents/`의 함수 매핑 모두 **정적
리터럴 매핑**으로 이미 존재한다. 동적 할당(자연어에서 어떤 Agent인지 자동 판단)은
어디에도 없으며, `IMPLEMENTATION_RULES.md`의 "Registry 일반화 금지"와도 상충한다.

### Q3 결론

네 책임 모두 부재가 확인되나, **Agent Assignment는 정적 매핑으로 이미 충분히
대응 가능한 형태**(호출자가 HQ/Task를 알고 있으면 그 다음은 기존 리터럴 매핑으로
연결된다)라는 것이 다른 세 책임과 구별되는 지점이다. 이 ADC는 이 구별을 §8
Implementation Boundary에 반영한다 — 단, 이번 Decision이 Defer이므로 실제 구현
전제조건으로서의 효력은 이 책임이 실제로 Accept될 때까지 유보된다.

---

## Q4. Conversation Layer 등 명칭·Component를 지금 확정해야 하는가

### 검토

RFC-0018과 마찬가지로 이 ADC도 "Conversation Layer"라는 이름이나 그 밑에 속할
Component 구조를 전제하지 않는다. Q1~Q3에서 확인했듯 이 책임의 **필요성 자체**가
아직 실제 사례로 뒷받침되지 않으므로, 이름·구조를 지금 정하는 것은 판단의 순서가
뒤바뀐 것이다 — 필요성이 확정되지 않은 책임에 이름부터 붙이는 것은 "미래의
가상 요구사항에 대비해 설계하지 않는다"는 일반 원칙과도 맞지 않는다.

### Q4 결론

이름·Component 확정은 이 ADC의 판단 대상이 아니며, Decision이 Defer인 이상 더더욱
지금 결정할 이유가 없다.

---

## Q5. Dev HQ Context Analysis, Multi-Task, Execution Host, §6 Runtime과의 경계

### 검토

- **Dev HQ Context Analysis(`build_context_bundle`)**: 입력이 이미 구조화된
  `issue`라는 점에서 Conversation-level 책임과 층위가 다르다(RFC-0018 §5.C·§7
  확인 사항을 그대로 채택). 이 ADC가 어떤 새 책임을 Accept하더라도
  `build_context_bundle()`의 책임·구현에는 영향을 주지 않는다.
- **Multi-Task(§16.4)**: "이미 고정된 Task"를 전제로 하는 §16.4의 범위는 이
  ADC로 전혀 넓어지지 않는다. 이 ADC가 다루는 책임은 §16.4의 **입력을 만드는
  단계**이지 §16.4 자체가 아니다.
- **Execution Host(§16.3)**: 단일 실행 단위의 dispatch·격리라는 §16.3의 범위와
  이 ADC의 대상은 겹치지 않는다 — §16.3은 Task 확정 이후 단계만 다룬다.
- **§6 Runtime / ADC-02**: ADC-02(Runtime 존폐)는 Open 상태 그대로 유지된다. 이
  ADC는 그 넓은 질문을 대신 판단하지 않으며, §6 Concept Model 표도 변경하지 않는다.

### Q5 결론

네 책임 모두와 명확히 분리된다. 이 ADC의 Decision이 무엇이든 §16.3·§16.4·
`build_context_bundle()`·ADC-02는 전혀 갱신되지 않는다.

---

## Q6. Out of Scope 재확인 — 동적 Agent 할당, Scheduler, Workflow orchestration, Retry/Recovery, 새 Public Contract

### 검토

이 ADC는 다음을 이번 Decision에 포함하지 않는다(RFC-0018 §8과 동일 범위를
유지하며, 이 ADC가 새로 넓히지 않는다):

- Task→Agent **동적** 할당(정적 리터럴 매핑 재사용 여부만 Q3·Q8에서 다룬다)
- Scheduler·우선순위
- Workflow orchestration
- Retry/Recovery 정책
- 새로운 Public Contract/Interface
- Dashboard UI

이들은 `IMPLEMENTATION_RULES.md`의 기존 금지 사항(Scheduler 구현 금지, Registry
일반화 금지, Multi-HQ 지원 코드 작성 금지 등)과도 이미 정합적이다.

### Q6 결론

전부 Out of Scope로 유지한다. Decision이 Defer이므로 이 절은 실질적으로
"Accept됐더라도 포함하지 않았을 것"을 미리 밝혀 두는 의미를 가진다 — 향후 재검토
시에도 동일 경계가 적용된다.

---

## Q7. 이 ADC가 Reject가 아니라 Defer인 이유

### 검토

Reject는 "이 책임은 필요 없다"는 적극적 판단이다. 그러나 RFC-0018 §1의 Problem
Statement(자연어 요청이 실제로 여러 HQ에 걸친 의도를 담을 수 있다는 것)는 논리적으로
타당하며, §6 Concept Model의 "Runtime은 Task를 Agent에게 배분한다"는 Architecture
Intent와도 방향이 어긋나지 않는다. 즉 이 책임이 **영구히** 불필요하다고 볼 근거는
없다 — 단지 **지금** Accept할 만큼의 실제 필요 증거가 없을 뿐이다.

Accept는 "지금 이 범위에서 구현에 착수해도 좋다"는 판단이다. 그러나 Q1·Q2에서
확인했듯 관찰 0건 상태에서 Accept하면, Governance Chain 전체가 지금까지 지켜온
"실제 필요가 검증된 뒤에만 Kernel 책임으로 승격한다"는 원칙(Rule B, ADC-0013/
0016/0017 모두 최소 1건 이상의 실제 사건을 근거로 삼음)과 어긋난다.

### Q7 결론

Defer가 유일하게 정합적인 판단이다 — Reject할 만큼 불필요하다는 근거도 없고,
Accept할 만큼 필요하다는 근거도 없다.

---

## Decision

**C. Defer (Scoped) — 실제 Multi-HQ 자연어 요청 처리 필요가 관찰될 때까지 보류**

### Reason

1. **구조적 공백은 실재하나 필요성 Evidence가 없다(Q1)**: RFC-0018 §5가 확인한
   "자연어 → Multi-HQ → Task 공통 계층 부재"는 사실이다. 그러나 이 부재로 인해
   실제 작업이 막히거나, 손상되거나, 비효율이 발생한 사건은 이 Repository 어디에도
   기록돼 있지 않다.
2. **관찰 수량이 이전 모든 Accept 사례보다 근본적으로 적다(Q2)**: ADC-0013(5건),
   ADC-0016(1건, 실제 merge된 코드), ADC-0017(4건, 실제 재현)과 달리, 이번은
   관찰 **0건**이다. ADC-0016의 "1건도 Scope를 좁혀 Accept" 논리는 그 1건이
   실제 사건이었기에 성립했다 — 사건 자체가 없는 이번에는 적용할 수 없다.
3. **Task Decomposition/Agent Assignment 등 4개 책임 각각의 실제 필요 사례도
   없다(Q3)**: 다만 Agent Assignment는 기존 정적 매핑 패턴(`TEAMS`, Dev HQ
   `agents/`)으로 이미 대응 가능한 구조라는 것은 향후 재검토 시 참고할 만한
   Evidence로 남긴다.
4. **Reject할 근거도 없다(Q7)**: Architecture Intent(§6)와 방향이 어긋나지
   않으며, 향후 실제 Multi-HQ 요청이 반복 관찰되면 재검토 대상이 된다.

### Decision Rationale

- Governance v2 Rule B(3건 이상 독립 관찰)를 충족하지 못했고, 예외적 Accept를
  정당화했던 ADC-0016의 전제(실제 merge된 Production Code 1건)도 이번에는
  성립하지 않는다.
- "미래에 필요할 수 있다"는 가능성만으로 Component를 설계하지 않는다는 일반
  원칙(CLAUDE.md 및 시스템 전반의 원칙: 가상의 미래 요구사항에 대비한 설계 금지)과
  정합적이다.
- RFC-0018 자신도 §3 Scenario를 "가설"이라고 명시했고, 실제로 실행하지 않았다 —
  이 ADC는 그 가설을 실제 관찰로 격상시키지 않는다.

---

## Implementation Boundary (다음 Production 구현을 위한 최소 범위)

**이번 Decision은 Defer이므로 어떤 Production 구현 착수도 승인하지 않는다.**
아래는 향후 재관찰 시 참고할 최소 범위를 미리 기록해 두는 것이며, 지금 구현을
허용하는 것이 아니다.

**재검토를 촉발하는 조건(재관찰 기준)**:
- 실제 dogfooding 또는 Production 사용 중, 하나의 자연어 요청이 복수 HQ에 걸친
  의도를 담고 있어 사람이 수작업으로 나눠 처리해야 했던 사례가 **3건 이상**
  독립적으로 관찰되거나(Rule B), 또는 ADC-0016 수준의 명확한 단일 실제 구현
  사례(사람이 직접 만든 실험적 코드가 이미 존재하고 유효성이 검증된 경우)가
  나타날 때.

**재관찰 시에도 유지해야 할 경계(Q3·Q5·Q6에서 확정)**:
- Agent Assignment는 기존 정적 리터럴 매핑(`TEAMS`류) 재사용을 우선 검토한다 —
  동적 할당을 전제하지 않는다.
- Task Decomposition은 Multi-Task(§16.4)의 "이미 고정된 Task" 전제를 바꾸지
  않는다 — 분해된 결과가 §16.4에 전달될 뿐, §16.4 자체의 조건(Data/Artifact
  Isolation 등)은 그대로 적용된다.
- Dev HQ Context Analysis(`build_context_bundle`)는 Conversation-level 책임과
  분리된 채로 유지한다.
- Execution Host(§16.3)·ADC-02(Runtime 존폐)는 건드리지 않는다.
- Scheduler/우선순위/Workflow orchestration/Retry/Recovery/새 Public Contract는
  포함하지 않는다.

---

## Risks

| 위험 | 설명 | 완화 |
|---|---|---|
| 재관찰 누락 | Defer 상태에서 실제 필요 사례가 반복돼도 별도로 추적되지 않으면 재검토가 지연될 수 있다 | 다음 dogfooding에서 Multi-HQ 요청이 시도될 때 `EVIDENCE.md` 등에 명시적으로 기록하는 관행을 권장(이 ADC가 강제하지는 않는다) |
| Defer의 과도한 장기화 | "필요성 없음"과 "판단 보류"가 실무에서 혼동돼, 실제 필요가 쌓여도 아무도 재검토하지 않을 수 있다 | 이 문서의 "재검토를 촉발하는 조건"을 재관찰 시 인용 기준으로 사용한다 |
| RFC-0018의 문제의식 자체가 희석될 위험 | Defer로 인해 "자연어 요청은 항상 이미 구조화돼 들어온다"는 암묵적 가정이 굳어질 수 있다 | 이 ADC는 그 가정을 채택하지 않는다 — 단지 지금 Accept할 근거가 없다고 판단할 뿐, 가정을 확정하지 않는다(§Decision Rationale) |

---

## Next Step

1. 이 ADC는 BASELINE.md·IMPLEMENTATION_RULES.md·ADC.md 어느 것도 갱신하지 않는다
   — Defer는 Baseline 반영 대상이 아니다.
2. **ADR 작성 불필요**: Accept가 아니므로 Baseline에 반영할 Decision이 없다.
3. 향후 실제 Multi-HQ 자연어 요청 필요가 반복 관찰되면, 새 RFC(또는 이 RFC-0018의
   재오픈)로 다시 절차를 시작한다 — 이 ADC의 Decision을 자동으로 뒤집지 않는다.
4. Production Code는 이번에도 수정하지 않는다.

---

## Governance Chain 검증

| 문서 | 관계 | 정합성 |
|---|---|---|
| RFC-0018 | 이 ADC가 판단하는 Boundary Question의 출처 | RFC의 Evidence(§4·§5)를 그대로 인용하되, §9 Open Question(Q1~Q7)에 대해 RFC가 열어둔 판단을 이 ADC가 독립적으로 완료함 |
| RFC-0013→ADC-0013→ADR-0003 (Execution Host) | §16.3 경계 | 변경 없음(Q5) |
| RFC-0014→ADC-0014→ADR-0004 (명칭) | Execution Host 명칭 | 변경 없음 |
| RFC-0015→ADC-0015→ADR-0005 (구현 전략) | Execution Host 구현 전략 | 변경 없음 |
| RFC-0016→ADC-0016→ADR-0006 (Multi-Task) | §16.4 경계, "이미 고정된 Task" 전제 | 변경 없음(Q5) — 이 ADC의 Decision은 §16.4에 전달될 입력을 다루려 했으나 Defer로 인해 그 논의 자체가 보류됨 |
| RFC-0017→ADC-0017→ADR-0007 (Result Store) | §16.5 경계 | 변경 없음(Q5) |
| `docs/decisions/adc/ADC.md` ADC-02 | Runtime 개념의 존폐, Open | 변경 없음(Q0·Q5) — 이 ADC는 그 넓은 질문에 답하지 않는다 |
| `BASELINE.md` §6 Concept Model | Runtime 정의 | 변경 없음 |
| `hqs/development/IMPLEMENTATION_RULES.md` | Multi-HQ 지원 코드 작성 금지 등 | 변경 없음 — 이번 Decision(Defer)과 기존 금지 사항은 이미 정합적이다 |

---

## Architecture Governance Review

- 이 ADC는 RFC-0018이 연 Boundary Question 하나에만 답했다 — 다른 질문을
  추가로 열지 않았다.
- Decision(Defer)은 RFC-0018의 결론(RFC는 결론을 내리지 않음)을 단순 반복한
  것이 아니라, RFC의 Evidence를 Governance v2 Rule B와 기존 Accept 사례들의
  전제(실제 사건 존재 여부)에 비추어 독립적으로 재평가한 결과다.
- Conversation Layer 등 어떤 이름·Component도 확정하지 않았다.
- Request Interpretation/HQ Routing/Task Decomposition/Agent Assignment 네
  책임을 각각 검토했고, 하나로 묶는 판단을 내리지 않았다(Defer이므로 그 판단
  자체가 필요 없어졌다).
- Execution Host(§16.3)·Multi-Task(§16.4)·Dev HQ Context Analysis·§6
  Runtime(ADC-02)의 기존 경계를 전혀 변경하지 않았다.
- 동적 Agent 할당, Scheduler, Workflow orchestration, Retry/Recovery, 새
  Public Contract는 모두 Out of Scope로 유지했다.

---

## Self Review

- [x] RFC-0018 §5 Evidence를 그대로 인용하되, 그 의미(필요성 증거인지 부재
      증거인지)는 독립적으로 재평가했다(Q1).
- [x] Rule B 충족 여부를 ADC-0013/0016/0017과 수량·성격 모두 비교해 판단했다(Q2).
- [x] Request Interpretation/HQ Routing/Task Decomposition/Agent Assignment를
      섞지 않고 각각 검토했다(Q3).
- [x] Conversation Layer라는 이름·Component를 선결정하지 않았다(Q4).
- [x] Dev HQ Context Analysis, Multi-Task(§16.4), Execution Host(§16.3), §6
      Runtime(ADC-02)과의 경계를 각각 명시적으로 분리했다(Q5).
- [x] 동적 Agent 할당·Scheduler·Workflow orchestration·Retry/Recovery·새 Public
      Contract를 Out of Scope로 유지했다(Q6).
- [x] Defer를 선택한 이유(Reject도 Accept도 아닌 이유)를 별도로 검토했다(Q7).
- [x] BASELINE.md·IMPLEMENTATION_RULES.md·ADC.md·Production Code 어느 것도
      수정하지 않았다.
- [x] Defer이므로 ADR 작성이 불필요함을 §Next Step에 명시했다.
