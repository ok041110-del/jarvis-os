# Investment HQ Minimal Structure Review 0001 — 최소 조직 구조 검증

## 문서 성격

이 문서는 Stock/ETF/Dividend Stock Team이 모두 Promoted된 시점에서,
이 세 Team을 묶는 최소 조직 구조(Investment HQ → Investment Division →
3 Team)를 **문서 수준에서만** 검증한다. `docs/research/`에 놓인
Governance Review와 동일한 성격이며, `development-hq/`와 같은 무게의
새 HQ Baseline 문서 세트(MISSION.md/BOUNDARY.md/RESPONSIBILITY.md/
STRUCTURE.md 등)를 만들지 않는다 — 그 수준의 작업은 §5에서 판단하듯
RFC 대상이며, 이번 작업 범위가 아니다.

**핵심 결론**: §6의 권고 구조(Investment HQ → Investment Division →
Stock/ETF/Dividend Stock 3 Team)는 기존 Architecture와 충돌하지 않으며
채택됐다. RFC 대상은 아니다 — 전체 Investment HQ Architecture 설계는
Blocking/지연 비용 조건 미충족으로 의도적으로 열지 않았다.

이 문서가 하지 않는 것:
- Investment HQ를 Registry에 등록하거나 Lifecycle State를 부여 —
  Registry/Lifecycle 관리는 Jarvis OS(Kernel)의 책임이며
  (`docs/01_architecture/BASELINE.md` §7), 그 Kernel 기능 자체가 아직
  구현되지 않았다. Development HQ도 현재 이 상태(비-live)로 존재한다.
- 새 Agent, Capability, Kernel Component, Runtime 추가.
- Stock/ETF/Dividend Stock Team의 실제 코드를 이동·통합.
- Investment HQ의 Mission/Boundary/Responsibility를 Development HQ와
  같은 상세도로 확정하는 전체 Architecture 설계.

## 1. 조사한 것

- `docs/01_architecture/BASELINE.md` §5(Meta Architecture), §6(Concept
  Model), §7(System Boundary)
- `development-hq/{MISSION,BOUNDARY,RESPONSIBILITY,STRUCTURE}.md`
- `docs/research/{STOCK,ETF,DIVIDEND-STOCK}-TEAM-DEFINITION-0001.md`,
  `DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001.md`
- `docs/architecture/core/GOVERNANCE-REVIEW-0006·0007`
- `development-hq/HANDOVER.md`, `README.md`
- `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`(ADC 채택 기준)

---

## 2. 기존 Architecture와의 충돌 여부

### 2-1. Meta Architecture — 충돌 없음

`BASELINE.md` §5: `Jarvis OS → HQ → Agent → Connector`. 이 계층은 HQ가
**여러 개** 존재할 수 있다는 것을 이미 전제한다
(`development-hq/HANDOVER.md`: "여러 HQ(업무 영역)를 실행하고 관리하는
운영체제"). 두 번째 HQ를 추가하는 것은 이 계층 구조를 바꾸는 것이
아니라, 이미 승인된 패턴을 한 번 더 쓰는 것이다. Development HQ의
Mission(`MISSION.md`) 자체가 "이 패턴이 다른 HQ에도 그대로 재사용
가능함을 보인다"를 목표로 명시하고 있으므로, Investment HQ는 그
목표가 실제로 검증되는 첫 사례에 해당한다.

### 2-2. Division/Team — 충돌 없음

`BASELINE.md` §5: "Division과 Team은 이 계층에 포함되지 않는다...
Jarvis OS는 그 존재 여부를 알지 못한다." `development-hq/BOUNDARY.md`:
"내부 조직 구조 사용 여부"는 **HQ의 책임**이다. 즉 Investment HQ가
Division/Team을 어떻게 쓸지는 Investment HQ 자신이 결정할 문제이며,
Kernel/Architecture Governance의 승인 대상이 아니다.

### 2-3. HQ 자체의 "실재" — 충돌 없음, 그러나 지금은 "Live"가 될 수 없다

`BASELINE.md` §6 Concept Model은 HQ를 "HQ는 Capability를 Registry에
등록한다", "HQ는 Lifecycle State를 가진다"는 관계로 정의한다. §7은
"HQ/Agent의 등록과 발견(Registry)", "HQ의 생명주기 관리"를 **Jarvis
OS(Kernel)의 책임**으로 규정한다. Registry/Lifecycle 관리 기능은
`IMPLEMENTATION_RULES.md`에 의해 아직 구현되지 않았고
(`docs/03_adc/ADC.md` ADC-11: Capability 신뢰 검증 책임도 Open),
`development-hq/mvp/`도 이 기능을 구현하지 않는다.

**결론**: Investment HQ를 문서 수준에서 정의하는 것은 Development HQ가
지금까지 존재해 온 것과 정확히 같은 방식(문서화된 개념, Registry에
등록되지 않은 비-live 상태)이며, 새로운 Kernel 기능을 요구하지 않는다.
Architecture와 충돌하지 않는다.

---

## 3. 원칙 적용 결과

| 원칙 | 적용 결과 |
|---|---|
| Investment HQ는 Development HQ의 복제본이 아니다 | Mission이 다르다 — Development HQ는 "Jarvis OS가 SDLC 도메인에서 성립하는지 검증", Investment HQ는 "개별 종목/ETF/배당주 리서치 업무 수행". `MISSION.md`/`BOUNDARY.md` 같은 상세 문서 세트를 이번에 복제하지 않는다(§5에서 판단하듯 RFC 대상) |
| 현재는 Investment Division 1개로 시작 | §4-2에서 판단 |
| Division을 추가하지 않는다 | Investment Division 외 추가 Division 없음(예: "Real Estate Division" 등 미제안) |
| Stock/ETF/Dividend Stock을 Team으로 귀속 | §4-3에서 판단 |
| 새 Agent/Kernel/Runtime/Capability 없음 | 이 문서는 코드를 전혀 만들지 않는다 — 순수 문서 |
| 실제 Evidence 없는 조직을 추가하지 않는다 | Investment HQ/Division/3개 Team 외 어떤 조직도 이 문서에서 제안하지 않는다 |

---

## 4. 개별 판단

### 4-1. Investment HQ가 별도 HQ로 존재해야 하는가

**그렇다 — 개념/문서 수준에서.** Development HQ의 Boundary
(`development-hq/BOUNDARY.md`, `MISSION.md`)는 명시적으로 "소프트웨어
개발"이라는 도메인에 한정된다. Stock/ETF/Dividend Stock의 업무(재무/
기술적 분석, Bull/Bear 리서치, 배당 분석)는 이 Boundary 안에 속하지
않는다 — Development HQ 안에 "Investment"를 하나의 Capability나
Division으로 끼워 넣는 것은 Development HQ 자신의 Mission("Jarvis OS
Architecture Baseline이 **소프트웨어 개발** 도메인에서 성립하는지
검증")과 직접 충돌한다. 별도 HQ로 문서화하는 것이 기존 Boundary
정의와 일치한다.

**단, 지금 "Live"(Registry 등록, Lifecycle State 보유) HQ로 만들지는
않는다** — §2-3의 이유로 그럴 수 없고, 그럴 필요도 없다(Development
HQ도 지금 그 상태가 아니다).

### 4-2. Investment Division이 필요한가

**엄격한 Evidence 기준으로는, 지금 당장 필요하지 않다.** 3개 Team
모두 "개별 유가증권 리서치"라는 동일 성격의 업무를 수행하며, 이들을
서로 다른 Division으로 나눠야 할 만한 두 번째 하위 도메인(예: 부동산,
원자재, 사모, 포트폴리오 관리)이 관찰된 적이 없다. `development-hq/
STRUCTURE.md` 자신도 Division을 정의만 해두고 실제로는 **쓰지
않는다**(Team/Capability를 HQ에 직접 나열) — Development HQ가 이미
같은 상황(Division 불필요)에서 그 관례를 스스로 생략한 선례다.

**그럼에도 사용자가 명시적으로 요청한 "Investment Division 1개"는
채택한다.** 이유:
1. Division/Team은 순수 문서/명명 계층이며(§2-2), 코드나 Kernel에
   영향을 주지 않는다 — 채택 비용이 사실상 0이다.
2. 향후 Investment HQ가 실제로 다른 성격의 하위 도메인(예: 대체투자,
   포트폴리오 관리)을 다루게 될 경우, 지금 "Investment Division"이라는
   이름을 붙여 두면 그 시점에 두 번째 Division을 나란히 추가하기
   쉬워진다 — 지금 그 구조를 미리 설계하지 않으면서도, 나중에 자연스러운
   확장 지점이 된다.
3. 사용자가 이 구조를 명시적 원칙으로 지시했다.

**결론**: Division 1개 채택을 권고하되, 이는 "지금 반드시 필요해서"가
아니라 "비용이 없고 사용자가 명시적으로 원해서"라는 점을 정직하게
기록한다.

### 4-3. 현재 3개 Team의 귀속이 적절한가

**적절하다.** Stock/ETF/Dividend Stock Team 모두:
- `docs/research/{STOCK,ETF,DIVIDEND-STOCK}-TEAM-DEFINITION-0001.md`로
  **이미 Promoted** — 승격 자체가 재검토 대상이 아니다.
- 셋 다 "개별 유가증권/펀드에 대한 다관점 리서치(Fundamental/
  Technical/Industry/News/Sentiment ± 자산군별 고유 역할) → Bull/Bear →
  Synthesis → Final Report"라는 동일한 업무 패턴을 공유한다 — 서로
  다른 HQ/Division에 흩어 놓을 근거가 없다.
- Dividend Stock Team은 Stock Team의 역할을 지시문 변경 없이 3/3
  재사용했다(`DIVIDEND-STOCK-TEAM-DEFINITION-0001.md`) — 같은
  Division 안에 있는 것이 그 관계를 자연스럽게 반영한다.
- ETF Team은 Stock과 역할을 공유하지 않지만(완전 독립 역할군), 다루는
  대상(유가증권 리서치)의 성격 자체는 동일 Division 범주에 속한다.

### 4-4. 향후 Division 분리가 필요한 조건은 무엇인가

다음 중 하나가 **실제로** 관찰되면 두 번째 Division을 검토한다(지금
트리거하지 않는다):

- 개별 유가증권/펀드 리서치가 아닌 성격의 실제 Investment 업무가
  Dogfooding으로 검증될 때(예: 포트폴리오 구성/리밸런싱 자체를 수행하는
  Team, 대체투자(부동산/사모/원자재) 리서치 Team).
- 리서치 Team들과 실행/집행 성격의 Team(예: Trade Execution) 사이에
  책임 분리가 실제로 필요해질 때 — 이는 Stock/ETF/Dividend Stock Team
  정의 문서들이 이미 반복적으로 "실거래 실행은 범위 밖"으로 명시해 온
  경계와 일치한다.
- 3개 Team이 실제로 서로 다른 Governance/Capability Contract를 요구하게
  되어, 하나의 Division 아래 묶는 것이 오히려 관리를 어렵게 만드는
  사례가 관찰될 때.

---

## 5. Governance 필요 여부 판단

### 5-1. ADC 채택 기준 대조 — "Investment HQ 전체 Architecture 설계"를 지금 RFC로 열어야 하는가

`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준을
그대로 적용한다(`GOVERNANCE-REVIEW-0005`가 C6 RFC 필요성을 판단할 때
쓴 것과 동일한 방식).

| 기준 | 충족 여부 | 근거 |
|---|---|---|
| (1) 지금 결정하지 않으면 상위 Architecture를 진행할 수 없다 | **아니오** | 3개 Team은 이미 project-local Dogfooding으로 정상 동작하며, HQ 수준 그룹핑 없이도 Promotion과 Evidence 축적이 계속 진행돼 왔다. 아무 것도 이 결정을 기다리며 멈춰 있지 않다 |
| (2) 결정이 늦어질수록 되돌리는 비용이 매우 커진다 | **아니오** | Registry/Lifecycle이 구현되지 않아 "되돌릴" 실제 상태(등록·배선)가 존재하지 않는다 |

**두 조건 모두 불충족.** `ARCHITECTURE_GOVERNANCE.md`: "두 조건을
만족하지 않으면 해당 사안은 현재 단계에서 다루지 않는다." —
**Investment HQ 전체 Architecture 설계(RFC → ADC → ADR)는 지금 열지
않는다.** 이는 `docs/research/{STOCK,ETF,DIVIDEND-STOCK}-TEAM-DEFINITION-0001.md`
가 반복적으로 "Investment HQ Architecture 설계는 RFC 대상"이라고
남겨 둔 판단과 일치하며, 이번 검토가 그 판단을 뒤집지 않는다 — 다만
"RFC를 열 조건 자체가 아직 충족되지 않았다"는 이유를 처음으로
명시했다.

### 5-2. 이번 문서(순수 명명/그룹핑)에 필요한 절차

| 항목 | 필요한 절차 |
|---|---|
| Investment HQ/Investment Division이라는 이름으로 3개 Team을 문서 상 그룹핑 | **불필요(RFC 없음)** — Division/Team은 Architecture가 아니며(§2-2), HQ 자체도 Registry 등록 없이 문서로만 존재하는 한 Kernel에 영향을 주지 않는다(§2-3) |
| Investment HQ의 전체 Baseline(Mission/Boundary/Responsibility/Capability 등록 등, Development HQ와 같은 무게) 확정 | **RFC → ADC → ADR 필요, 지금 미충족(§5-1)** |
| Investment HQ를 Jarvis OS Registry에 실제로 등록 | **불가능** — Registry 자체가 미구현. Kernel Component Architecture 착수가 선행돼야 함(Out of Scope) |

---

## 6. 권장 구조

```
Jarvis OS
└── Investment HQ (개념/문서 수준, Registry 미등록 — Development HQ와 동일한 비-live 상태)
    └── Investment Division (선택적 관례, 현재 1개)
        ├── Stock Team (Promoted)
        ├── ETF Team (Promoted)
        └── Dividend Stock Team (Promoted, Stock Team 확장으로 문서화)
```

사용자가 제시한 기본 가설과 동일하다 — 이번 검토는 이 구조가 기존
Architecture와 충돌하지 않고, Evidence(3개 Team Promotion + 14회
Dogfooding)로 뒷받침됨을 확인했다.

**이 구조가 아직 갖지 않는 것**: Mission/Boundary/Responsibility 문서,
Capability 목록, Registry 등록, Lifecycle State, Agent 이름. 이들은
Investment HQ의 전체 Architecture 설계(§5-1, RFC 대상)가 실제로
열릴 때 다뤄진다.

---

## 7. 다음 작업

1. 사용자가 이 구조(§6)를 최소 문서 반영으로 승인할지 판단.
2. 승인 시, `development-hq/HANDOVER.md`/`README.md`의 "Investment HQ
   자체" 행을 이 문서를 인용하는 최소 갱신(순수 문서 동기화, Architecture
   변경 아님)으로 반영 — 이 문서 자체가 그 갱신을 수행한다(§Architecture
   변경 여부 참조).
3. Investment HQ 전체 Architecture 설계(RFC)는 §5-1의 조건(블로킹 또는
   높은 지연 비용)이 실제로 발생할 때까지 열지 않는다.
4. 두 번째 Division이 필요해지는 조건(§4-4)이 실제로 관찰되면 그때
   재검토한다.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/`(Platform), `docs/03_adc/ADC.md`, 기존
TEAM-DEFINITION 문서, `docs/01_architecture/BASELINE.md` 어느 것도
수정하지 않았다. 새 Agent, Capability, Kernel Component, Runtime을
만들지 않았다. Investment HQ를 Registry에 등록하지 않았다(등록 기능
자체가 없음). Stop Trigger 미발동.
