# INVESTMENT-HQ-REPOSITORY-POLICY-RISK-PORTFOLIO-REPRODUCTION-0001

**문서 성격**: Experimental Dogfooding Evidence 문서(재현성 검증
전용, Repository Audit 우선). Architecture 설계·Contract 확정·Risk
Architecture Freeze를 하지 않는다. `hqs/investment/`는 수정하지
않았다(이번 문서는 코드 실행조차 하지 않았다 — 이유는 §5에서
설명).

**핵심 결론(선반영)**: **저장소에 이번 실험이 요구하는 종류의 실제
Risk/Portfolio Policy(수치 기반 노출 상한·집중도 제한 등)가 존재하지
않는다.** 사용자 지시(§2·§12·§18)가 명시적으로 요구한 원칙 —
"Repository Evidence가 없으면 실험자가 조건을 만들지 않고 '현재
Repository Evidence로는 검증 불가능'으로 기록한다" — 를 그대로
따른다. 이번 문서는 **Repository Audit 결과와 그 결론만** 기록하며,
PASS1/2/3 Engine 호출은 수행하지 않았다(수행할 실제 입력이 없다).

---

## 1. 실제 Repository Policy(감사 결과)

**검색 범위**(사용자 지시 §2 준수): `hqs/investment/`(전체 `.py`/
`.md`), `docs/architecture/`(Baseline, Core), `docs/decisions/`,
`docs/research/`(이번 세션 이전 문서 포함, 단 이번 세션 자체가 만든
실험 문서는 "저장소 Policy"로 인정하지 않음 — 아래 §1-3 참조),
`CLAUDE.md`, `roadmap.md`, `hqs/development/IMPLEMENTATION_RULES.md`.

**검색 키워드**: limit, policy, exposure, concentration, allocation,
position, risk, portfolio, overlap, constraint, diversification.

### 1-1. 발견된 것 — Category C(단순 설명/개념 정의, 실행에 쓰이지 않음)

| 발견 | 위치 | 분류 |
|---|---|---|
| `Policy`가 Kernel의 PDP/PEP(정책 결정점/집행점) 개념으로 정의됨 | `docs/architecture/baseline/BASELINE.md` §L63·79·97 | **C** — Kernel Policy는 "모든 Task/Event에 대해 승인/거부 판정"이라는 **일반 개념**일 뿐, Portfolio/Risk Exposure에 특화된 정의가 아니다. 게다가 이 Policy 자체가 **Component Design 단계에서 여전히 Out of Scope**(BASELINE.md §L134·185: "Kernel Architecture와 Component Design(Scheduler, Engine Gateway, Registry, Communication, Memory, Policy 등)은 여전히 §10 Out of Scope")로 명시돼 있다 — 실행되는 실제 규칙이 아니다. |
| "Policy/Memory Service/Event Bus 구현 금지" | `hqs/investment/STRUCTURE.md` §금지 사항 | **C** — 이는 "Policy를 만들지 말라"는 **금지 규칙**이지, Portfolio/Risk가 참조할 Policy 자체가 아니다. |

### 1-2. 발견된 것 — 관련 도메인이지만 대상이 다름(제외)

`hqs/development/mvp/engine.py`의 `ENGINE_TIMEOUT_SECONDS = 180`,
Report Writer 지시문의 "800-1200 words" 같은 값들은 **실제로
실행에 쓰이는 진짜 Policy**(Category A에 해당하는 성격)이지만,
**Engine 호출/리포트 형식에 관한 것이지 Portfolio Exposure/Risk와
무관**하다 — 이번 실험의 대상(§목표: "저장소에 실제로 존재하는
Policy와 서로 다른 Team의 실제 산출물을 교차 참조")에 해당하지
않는다.

### 1-3. 이번 세션이 생성한 실험 문서는 Repository Policy로 인정하지 않음

이전 세 Dogfooding 문서(`...RISK-PORTFOLIO-BOUNDARY...`,
`...RISK-CHANGES-PORTFOLIO-REVALIDATION...`,
`...RISK-PORTFOLIO-CHANGE-REPRODUCTION...`)에 등장한 "10% look-through
cap", "15% defensive dividend sleeve cap", "5% single-position cap"은
**전부 이번 세션이 실험을 위해 문서에 기록한 가상 설정값**이다.
Portfolio Need Dogfooding 문서가 재사용한 "CAT 5% 정책"조차, 그
정책의 원천을 거슬러 올라가면 **Portfolio Need Dogfooding 세션이
"가상 Portfolio State"로 처음 구성한 것**이지(`hypothetical, for
this exercise only`라고 각 문서에 명시돼 있음), `hqs/investment/`
Production 코드나 저장소의 공식 설정 파일에서 온 것이 아니다 —
문서에 "실제 사례"라고 반복 인용됐다고 해서 저장소 원본 Policy로
승격되지 않는다. 사용자 지시(§18 "Repository Evidence와 실험자가
추가한 조건을 구분")를 엄격히 적용해, 이 세 값 전부를 **Category
D(새로 만들어야 하는 Policy, 사용 금지)**로 재분류한다.

### 1-4. Category A(실제 실행/검증에 사용된 Portfolio/Risk Policy) — **없음**

전수 검색 결과, `hqs/investment/`에는 Registry/Scheduler/Runtime/
Policy 컴포넌트가 **의도적으로 구현되지 않은 상태**(`STRUCTURE.md`
금지 사항, v1.0 Freeze 문서에서 반복 확인된 사실)이며, Portfolio
개념 자체가 코드에 존재하지 않는다(이전 여러 Dogfooding 문서가 이미
확인: `run.py`는 Team 하나를 실행하고 끝나는 스크립트, Portfolio
State를 저장·참조하는 코드가 없음). **Portfolio Exposure/Risk에 대한
수치 기반 Policy가 저장소에 실행 가능한 형태로 존재한 적이 없다.**

---

## 2. 검증 진행 여부

사용자 지시(§12) "실제 저장소에 없는 조건이 필요하다면 '현재
Repository Evidence로는 검증 불가능'으로 기록한다"를 그대로
적용한다. §1의 감사 결과, 이번 실험이 요구하는 유형의 Policy
(Category A)가 저장소에 없으므로:

- **Policy 선정(§3) 불가능** — Category A 후보가 0건.
- **Team 산출물 선정(§4) 진행 불가능** — 연결할 Policy가 없어
  "Policy와 관계있는 실제 Team 산출물"을 고를 수 없다.
- **PASS1/2/3(§6~9) 실행하지 않음** — 유효한 입력이 없는 상태에서
  Engine을 호출하는 것은 결과 없는 실험이며, 사용자가 금지한
  "실험자가 임의로 조건을 삽입"하는 것과 실질적으로 같아진다.
  따라서 **이번 문서는 실제 Engine 호출을 하지 않았다** — 이는
  게으름이 아니라 §12의 원칙을 지키기 위한 의도적 중단이다.

---

## 3. Negative Control / Synthetic Control 여부

- **Negative Control(§11)**: 시도하지 않음 — Positive 사례 자체가
  성립하지 않는데 Negative Control만 따로 만드는 것은 의미가 없다.
- **Synthetic Control(§12)**: 이번 문서는 **어떤 Synthetic Control도
  생성하지 않았다** — 이것이 이전 세 문서와의 핵심 차이다. 이전
  Reproduction 문서(Case 2, PG+JNJ)는 synthetic control임을 명시하며
  진행했지만, 이번 문서는 사용자가 이번 단계에서 그것조차 엄격히
  금지했으므로(§12 "Synthetic Control 엄격 금지") 실행하지 않고
  멈췄다.

---

## 4. 방법론적 한계

1. **저장소가 아직 Portfolio/Risk Policy를 가질 단계가 아니다** —
   이는 이번 감사의 "실패"가 아니라 **Investment HQ의 현재 실제
   상태를 정확히 반영한 결과**다. `Portfolio Need Dogfooding` 문서
   이래 일관되게 확인된 사실(Portfolio 개념 자체가 코드에 없음,
   Registry/Policy 컴포넌트가 의도적으로 미구현)과 완전히 일치한다.
2. 이 감사는 저장소의 **현재 스냅샷**(이 세션 시점)을 기준으로
   한다 — 향후 Portfolio Policy가 실제로 도입되면(코드 또는 공식
   설정으로) 재감사가 필요하다.

---

## 5. 최종 판정

## **D. EVIDENCE INSUFFICIENT**

**판정 이유**: 사용자가 이번 실험의 성공 조건(§10) 10개 중 첫
번째 — "Repository에 실제 존재하는 Policy" — 부터 충족되지 않는다.
이는 실험 설계나 실행의 문제가 아니라, **Investment HQ 저장소가
아직 이런 종류의 Policy를 가진 적이 없다는 사실 자체**다. 이전
Reproduction 문서(§8, 이전 문서)가 이미 정직하게 표시했던 "Case
2는 synthetic control"이라는 한계가, 이번 감사를 통해 **"synthetic
control이 아닌 대안 자체가 현재 저장소에 없다"**는 것으로
확인됐다 — 즉 이전 문서의 한계는 실험자의 선택이 아니라 저장소의
현재 상태에서 비롯된 불가피한 제약이었다는 것이 이번에 재확인된
것이다.

**A/B/C로 판정하지 않는 이유**: A(강한 재현)·B(제한적 재현
확인)·C(재현 안 됨, Risk 판단은 있으나 Portfolio 변경 없음)는
전부 **PASS1~3이 실제로 실행됐다는 것을 전제**로 한다. 이번엔
실행 자체를 하지 않았으므로 이 세 판정 중 어느 것도 적용할 수
없다.

---

## 6. 다음 선행조건

1. **Risk Architecture Freeze Review로 넘어가기 전, 이 Gap을
   명시적으로 알린다** — 지금까지 이 세션이 쌓은 "Risk → Portfolio
   Change" Evidence(QQQ 사례, PG+JNJ 사례)는 **전부 synthetic
   control 위에서 얻은 것**이며, 저장소에 실제로 존재하는 Policy로
   재현된 사례는 **아직 0건**이라는 것을 다음 Freeze Review 문서에
   명시적으로 전달해야 한다.
2. **실제 Policy 도입은 이번 문서의 범위가 아니다** — Policy를
   만드는 것 자체가 Portfolio/Risk Architecture 설계에 해당하며,
   이는 RFC → ADC → ADR 절차 또는 최소한 별도의 명시적 사용자
   승인을 거쳐야 한다(사용자 지시 §17 "Architecture/Contract 금지"
   준수). 이번 문서는 그 절차를 시작하지 않는다.
3. **대안 경로 제안(설계 아님, 관찰만)**: 만약 향후 실제 Policy
   Evidence를 확보하고 싶다면, (a) 최소 규모의 project-local
   실험에서 사용자가 명시적으로 "이 정책을 실제로 적용해보자"고
   승인한 뒤 그 결과를 저장소에 실제 Evidence로 남기는 방법, 또는
   (b) 이번 세션이 이미 3회 반복한 synthetic control 방식을
   계속하되 그 한계(§1-3)를 모든 후속 문서에 지금처럼 명시적으로
   표시하는 방법이 있다 — 어느 쪽을 택할지는 이 문서가 결정하지
   않는다.
4. 지금까지 확보된 Evidence 총괄(변경 없음, 재확인만): Trader
   Need — VALIDATED. Portfolio Need — VALIDATED(조건부). Look-through
   Portfolio Need — VALIDATED(조건부). Risk/Portfolio Boundary —
   PARTIALLY VALIDATED. Risk Need — VALIDATED(n=1). Risk→Portfolio
   Change — REPRODUCED(2개 사례, 전부 synthetic control 의존).
   **저장소 실제 Policy 기반 재현 — EVIDENCE INSUFFICIENT(이번
   문서, 0개 사례).**

---

## Self Review

- 저장소에 없는 Policy를 만들어서 실험을 진행했는가 — **아니오**
  (§2·§3, 실행 자체를 중단).
- Engine을 호출했는가 — **아니오**(입력이 성립하지 않아 호출하지
  않음, §2).
- 이전 세션들이 쓴 synthetic policy를 이번에 "저장소 Policy"로
  재포장했는가 — **아니오**(§1-3에서 명시적으로 재분류해 배제).
- Risk Architecture Freeze Review로 결과를 넘겼는가 — **아니오**
  (이 문서 자체가 Freeze Review가 아니며, §6-1에서 Gap을 다음
  단계에 알리라고만 기록).
- `hqs/investment/`, Structure v1.0, RFC/ADC/ADR, Phase 7을
  수정했는가 — **아니오**.
