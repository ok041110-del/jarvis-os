# JARVIS-OS-V2.0-FUTURE-ARCHITECTURE-PROMOTION-POLICY-0001: Future Architecture Promotion Policy Review

**문서 성격**: Policy/Governance Review(Candidate Policy 문서).
Production Code·Dashboard·Global Chat·Orchestrator·Runtime·Kernel
Component를 구현하지 않는다. `BASELINE.md`를 직접 수정하지 않는다.
기존 Freeze 문서를 수정하지 않는다.

**핵심 결론(선반영)**: 사용자가 제안한 "Evidence-first → Evidence-guided"
전환과 그 하위 원칙(Architecture/Kernel Promotion 분리, Deferred는
실패가 아님, Anti-pattern 5종)은 **이미 `docs/00_governance/
ARCHITECTURE_GOVERNANCE.md`의 "Experimental Implementation"(2026-08-22
03:11 커밋)과 "Architecture Need"(같은 날 06:11 커밋) 절로 대부분
실질적으로 존재한다.** 이는 이번 세션이 처음 만드는 정책이 아니라
**이미 채택된 Governance v2를 재확인·명명·Gap 식별하는 작업**이다.
판정: **A. 기존 Governance 해석으로 충분**(대부분) + 일부 **문서
정리 후보**(신규 Rule 아님). 신규 RFC/ADC/ADR 불필요.

---

## 1. Problem

Evidence-first 원칙(Evidence → Architecture → Implementation)을
문자 그대로 적용하면, Architecture Candidate 자체를 설계·Prototype
조차 못 하게 되어 Dashboard/Global Chat/Task/Context/Orchestration
같은 OS-level Architecture 발전이 지연된다는 것이 사용자의 문제
제기다. 이 Review는 그 문제를 Repository 실제 Governance에 대조해
검증한다.

---

## 2. Current Governance

Repository 조사 결과, 다음 문서 3개가 이미 이 문제를 다루고 있다.

### 2.1 `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`

- **"Experimental Implementation"** 절(L25-43): Formal Architecture
  Decision 없이 `projects/` 기반 격리 Prototype을 허용한다 — 명확한
  목적/제한된 scope/명시적 owner/테스트 수행/기존 Contract 보호/
  Frozen Boundary 보호/HQ production path 무단 연결 금지/성공-실패-
  폐기 기준 기록. **RFC 없이 즉시 폐기 가능**, Formal Promotion만
  기존 RFC→ADC→ADR을 따른다. **"Experimental Evidence는 그 존재만으로
  Formal Architecture Decision이나 ADC Accept를 발생시키지 않는다"**
  (L43) — 이는 사용자 §13 Anti-pattern 2("Prototype 성공 → 즉시
  Kernel 승격")를 정확히 금지하는 기존 문구다.
- **"Architecture Need"** 절(L45-87): 사전 정의된 Trigger(RT-0001)가
  없어도 실제 Need가 관찰되면 재검토를 시작할 수 있다. 진입 흐름
  (L53-67)이 정확히 사용자 §2가 제안한 확장 Lifecycle과 같은 형태다:
  `실제 Need 발생 → 기존 Architecture로 해결 가능? → (NO) →
  Experimental 가능? → Experimental → 가치 있으면 Formal Review →
  RFC → ADC → ADR`. "반드시 구분할 것"(L69-75)이 사용자 §13
  Anti-pattern 2·3을 이미 명문화했다.

### 2.2 `docs/decisions/adc/README.md`, `docs/decisions/adc/ADC.md`

- ADC는 **Formal Architecture Decision만** 판단하며 Experimental
  단계 자체는 ADC Accept를 요구하지 않는다(README.md).
- **"Experimental Implementation과의 관계"**(ADC.md L7): Experimental
  Evidence는 Observation으로 기록될 수 있으나, **그 존재만으로 기존
  Open/Deferred Decision이 자동 재개되지 않는다** — 이는 사용자
  §5·§6이 제안한 "Kernel Promotion Deferred" 상태와 **의미상 동일한
  기존 규칙**이다. 각 Decision의 기존 재개 Trigger(RT-0001 등)는
  그대로 유지된다.

### 2.3 `docs/governance/observations/README.md`(Governance v2 Observation Layer, Baseline 채택됨)

- OBS(Observation) 문서를 MVP와 RFC 사이에 두어, RFC가 매번
  반사적으로 열리지 않게 한다. Rule A(RT-0001 Trigger 충족) 또는
  Rule B(동일 Tag Observation 3회+)일 때만 RFC를 연다 — 이는 사용자
  §6의 "Evidence 단계화" 아이디어가 **이미 부분적으로 구현된 형태**
  다(다만 Kernel Cross-HQ 전용 E0-E5 척도로 명명되지는 않았다).

### 2.4 실제 적용 사례(Repository Evidence로 검증됨)

- `projects/kernel-parallel-execution-prototype/`(Phase 6) — 정확히
  "Experimental Implementation" 절의 규정대로 격리 실행됨(`hqs/`
  production path 미연결, `IMPLEMENTATION_RULES.md` 금지 준수),
  성공했지만 **Kernel 승격되지 않고 RFC-0012→ADC-0012 DEFER**로
  귀결됨(`PHASE7-RESUME-REVIEW-0001.md`) — 이는 사용자가 제안한
  "Kernel Promotion Deferred"(§5) 상태가 **이미 실제로 발생하고
  정상 운영되고 있음**을 보여준다.
- Investment HQ의 Risk Architecture(`RISK-ARCHITECTURE-FREEZE-REVIEW-0001.md`)도
  같은 패턴 — Responsibility Boundary만 "Working Hypothesis로 Freeze"
  하고 Contract/Policy/Implementation은 전부 DEFER — 이는 사용자
  §14 최종 정책 문구("Kernel 승격에 필요한 Evidence가 부족한 경우
  해당 Architecture를 폐기하지 않고 Deferred 상태로 유지")와 이미
  일치한다.

---

## 3. Architecture Lifecycle

사용자가 제안한 6단계(FUTURE→CANDIDATE→EXPERIMENTAL→IMPLEMENTED→
VALIDATED→FROZEN)를 기존 Governance 용어와 대조한다.

| 사용자 제안 | 기존 Governance 대응 | 신규 여부 |
|---|---|---|
| FUTURE | Architecture Need 진입 흐름의 "실제 Need 발생" 이전 단계(문서화만, RFC_CANDIDATES.md 선례) | **기존 개념, 이름만 다름** |
| CANDIDATE | "Architecture Need" 절의 "Experimental Implementation으로 검증 가능한가?" 진입점 | **기존 개념** |
| EXPERIMENTAL | "Experimental Implementation" 절 그 자체(L25-43) | **완전히 기존 규칙과 일치** |
| IMPLEMENTED | Experimental이 `hqs/` production path로 승격된 상태 — 단, 이 승격 자체가 이미 RFC→ADC→ADR을 거쳐야 함(기존 "변경 절차") | **기존 개념** |
| VALIDATED | 기존 각 Freeze Review 문서들의 Validation Evidence 축적 방식(Dev HQ v2.0/Investment HQ v2.0 Freeze가 실제로 이렇게 진행됨) | **기존 실무, 이름만 다름** |
| FROZEN | 기존 "변경 절차"의 "Architecture Baseline Update" 종착점 | **완전히 기존 규칙과 일치** |

**판정**: 6단계 Lifecycle은 **새 규칙을 추가하지 않는다** — 기존
"Experimental Implementation → 변경 절차(RFC→ADC→ADR→Baseline
Update)"의 각 단계에 이름을 붙인 것에 가깝다. 유일한 차이는 기존
문서가 "Experimental"과 "Formal(RFC 이후)"을 2단계로만 구분하는
반면, 사용자 제안은 그 사이(IMPLEMENTED/VALIDATED)를 세분화한다는
점이다 — 이는 실질적 Governance 규칙 변경이 아니라 **문서 표현의
정밀도** 문제다.

---

## 4. Evidence Lifecycle

사용자의 E0~E5 분류를 기존 Governance/실제 Repository 관행과 대조한다.

| 사용자 제안 | 기존 대응 |
|---|---|
| E0 Design Evidence | RFC 문서, `RFC_CANDIDATES.md` |
| E1 Prototype Evidence | "Experimental Implementation" 절의 `projects/` Prototype |
| E2 Local Validation | 기존 Freeze Review들의 Unit/Integration/E2E Evidence(Dev HQ v2.0, Investment HQ v2.0 Trader) |
| E3 Real Usage Evidence | 기존 Dogfooding 관행(`docs/01_mvp/`, `docs/research/*-DOGFOODING-*`) |
| E4 Cross-HQ Evidence | Phase 4 "Common/HQ-Specific/Uncertain" 3분류, Phase 5 Kernel Candidate 5기준 |
| E5 Stable Contract Evidence | ADC 채택 기준("지금 결정하지 않으면 진행 불가" 또는 "지연 비용 큼") 충족 직전 단계 |

**판정**: E0~E5가 가리키는 실체는 전부 기존 Repository 관행에 이미
존재한다(등급 표기 방식도 Investment HQ Risk Freeze Review가
A/B/C/D 등급으로 이미 사용 중). **다만 이를 Kernel Cross-HQ Evidence
전용의 통일된 5단계 척도로 명문화한 문서는 아직 없다.** 작업
지시(§6) 자체가 "임의의 숫자를 확정하지 않는다"고 명시했고, 기존
ADC 채택 기준(§2.1)도 숫자 임계값이 아니라 정성적 조건(2개 중
1개 충족) 방식을 일관되게 써왔다 — 이 Review는 E0~E5를 **공식
숫자 척도로 채택하도록 권고하지 않는다.** 필요하다면 §9 Open
Question으로만 남긴다.

---

## 5. Kernel Promotion Boundary

사용자 §7 "Architecture 질문 vs Kernel 질문" 분리는 기존 문서와
이미 일치한다:

- **Architecture 질문**("실제 문제 해결?", "Boundary 명확?",
  "Prototype 가능?")은 "Experimental Implementation" 절의 허용
  조건과 대응.
- **Kernel 질문**("2개 이상 HQ에서 필요?", "공통 Responsibility?",
  "Contract 안정적?")은 `BASELINE.md` §11 Kernel 정의("모든 HQ가
  공통으로 필요로 하지만 어느 HQ에도 속하지 않는 책임")와 Phase 5
  Kernel Candidate 5기준(공통성/도메인 독립성/반복성/안정성/재사용성)
  에 이미 명문화돼 있다.

**"Architecture Frozen ≠ Kernel"** 원칙도 기존 사례로 이미 실증됨 —
Investment HQ의 Trader는 A. FREEZE(Architecture)됐지만 Kernel
Candidate로 승격 시도조차 되지 않았다(단일 HQ 책임이므로 Kernel
질문 자체가 적용 대상 아님). 이는 사용자가 원하는 분리가 이미
Repository에서 실천되고 있다는 증거다.

---

## 6. Kernel Promotion Deferred

사용자 §5가 제안한 상태(구현됨 + 일부 Validation 존재 + Kernel
Evidence 부족 → 기존 유지, Kernel 미승격, 재평가 대기, **실패 아님**)는
`ADC.md`의 "Experimental Implementation과의 관계" 문단과 실제 운영
사례(§2.4) 양쪽에서 **이미 정확히 이 의미로 쓰이고 있다.** 기존
문서는 이를 "DEFER"(ADC-0012), "Not Accepted"(ADC-0008/0010),
"CONDITIONAL FREEZE"(Risk Architecture)로 사안마다 다르게 표기해왔다
— **개념은 동일하나 이름이 사안마다 다르다.**

**판정**: "Kernel Promotion Deferred"를 이 세 표기의 **공통 상위
라벨**로 문서에 정리하는 것은 새 규칙 추가가 아니라 **기존에 이미
일관되게 적용되고 있는 원칙의 명명**이다.

---

## 7. Governance Interaction

- Architecture Promotion(Candidate→...→Frozen)과 Kernel Promotion
  (Implemented→Cross-HQ Evidence→RFC→ADC→ADR→Kernel Frozen)을 별도
  경로로 문서화하는 것 — 이미 §2.1·§2.2에서 확인한 대로 **실질적으로
  분리되어 있다**(Experimental Evidence가 자동으로 ADC Open Decision을
  재개하지 않는다는 문구가 이 분리를 명시적으로 보장).
- Phase 7과의 관계(사용자 §10): 이 Policy는 Phase 7을 재개하지
  않는다 — `PHASE7-RESUME-REVIEW-0001.md`의 6개 재개 근거(Engine 수
  ≥2 등)는 이 Review로 전혀 영향받지 않는다. Experimental Implementation을
  통한 Evidence 축적도 §2.2에서 확인했듯 자동 재개 근거가 되지
  않는다.

---

## 8. Jarvis OS v2.0 Application

이전 Review(`JARVIS-OS-V2.0-UNIFIED-DASHBOARD-ARCHITECTURE-0001.md`)의
Candidate 3건에 이 정책(=기존 Governance)을 그대로 적용한다.

| Candidate | 기존 Governance 적용 결과 |
|---|---|
| Unified Dashboard(내부 구조·Contract) | "Experimental Implementation" 절 조건을 만족하면 `projects/` 격리 Prototype으로 검증 **가능** — 단 `hqs/` production path 연결 금지, Structure v1.0 변경 금지(이미 §4의 CANDIDATE 판정과 일치) |
| Global Jarvis Chat(Command Contract, Task 모델) | 동일 — Experimental Prototype 가능, Formal Contract 확정은 RFC→ADC→ADR 필요 |
| Multi-HQ Orchestration | 동일 — Experimental Prototype은 가능하나, Kernel Component(Task Scheduler 등)로 직접 연결 금지("Experimental이라는 명목으로 기존 Frozen/Deferred Boundary 우회 금지"가 정확히 이 위험을 막음) |

**새로 발견된 것은 없다** — 세 Candidate 모두 이미 §2.1의
Experimental Implementation 허용/금지 목록이 그대로 적용된다. 이번
Review가 발견한 것은 "새 정책이 필요하다"가 아니라 **"필요한
정책이 이미 있으나 아직 인용되지 않았다"**는 사실이다.

---

## 9. Open Questions

새 RFC/ADC/ADR 대상이 아닌, 문서 정리 수준의 질문만 남긴다.

1. `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 "Experimental
   Implementation"/"Architecture Need"를 사용자가 제안한 6단계
   Lifecycle 이름(FUTURE/CANDIDATE/.../FROZEN)으로 재서술할
   가치가 있는가 — Governance 실질 변경이 아니므로 이번 Review는
   결정하지 않는다.
2. E0~E5 Evidence 척도를 공식 채택할 필요가 있는가 — §4에서 판단한
   대로 기존 정성적 방식(2조건 중 1개 충족)과 비교해 실익이 아직
   불명확하다.
3. "Kernel Promotion Deferred"를 `DEFER`/`Not Accepted`/`CONDITIONAL
   FREEZE`의 공식 상위 라벨로 통일할 것인가 — §6에서 확인한 대로
   개념은 이미 동일, 표기 통일 여부만 남음.
4. `docs/decisions/adc/ADC.md` L7이 이미 "Experimental Evidence는
   Observation으로 기록될 수 있다"고 명시했으나, 실제 Observation
   문서(`docs/governance/observations/`) 계열과 Experimental
   Implementation 결과물의 연결 방식이 문서상 명확히 예시돼 있지
   않다.

이 4개는 전부 **표현/명명 정리 수준**이며, 어느 것도 Architecture
Baseline 변경이나 신규 Governance Rule을 요구하지 않는다.

---

## 10. Recommendation

**A. 기존 Governance 해석으로 충분.** 사용자가 제안한 정책의
실질적 내용(Evidence-first→Evidence-guided, Architecture/Kernel
Promotion 분리, Deferred는 실패 아님, 5개 Anti-pattern)은 이미
`ARCHITECTURE_GOVERNANCE.md`의 "Experimental Implementation"과
"Architecture Need" 두 절, 그리고 `ADC.md`의 "Experimental
Implementation과의 관계" 문단으로 **오늘 이전에 이미 Baseline으로
채택돼 있다.** BASELINE.md v1.6 직접 수정 불필요, 신규 RFC/ADC/ADR
불필요.

**남은 작업은 정책을 새로 만드는 것이 아니라 적용하는 것이다** —
Unified Dashboard/Global Chat/Orchestration Candidate에 이 기존
정책(Experimental Implementation)을 실제로 적용해 `projects/`
격리 Prototype을 시작할 수 있는 상태다(단, 이번 Review는 그
Prototype 자체를 만들지 않는다 — 작업 지시 §16 금지 목록 준수).

§9 Open Question 4건은 문서 명명·표현 정리 수준으로, 필요하면 별도
세션에서 `ARCHITECTURE_GOVERNANCE.md`를 **추가적으로**(대체가 아니라)
보강하는 것을 검토할 수 있으나, 이는 Governance 절차상 RFC 대상이
아니라 — 기존 문서가 이미 "이 Governance는 설계·문서화 단계에도
동일 적용"이라고 선언한 범위 안의 **문서 명확화**다.

---

## Self Review

- Production Code/Dashboard/Global Chat/Orchestrator/Runtime/Kernel
  Component를 구현했는가 — **아니오**.
- `BASELINE.md`를 직접 수정했는가 — **아니오**.
- 기존 Freeze 문서를 수정했는가 — **아니오**.
- 새 RFC/ADC/ADR을 작성했는가 — **아니오**.
- 사용자 제안 정책을 검증 없이 그대로 채택했는가 — **아니오**(§3~§6에서
  기존 문서와 항목별 대조).
- 이미 존재하는 Governance를 새로 만드는 것처럼 서술했는가 —
  **아니오** — 오히려 이 Review의 핵심 결론이 "이미 존재한다"는 것.
- Phase 7을 재개했는가 — **아니오**(§7).
- 임의의 Evidence 숫자 척도(E0~E5)를 확정했는가 — **아니오**(§4,
  Open Question으로만 남김).

---

## 최종 보고

1. **현재 Governance가 가진 문제**: 표면적으로는 "Evidence 없이는
   Architecture를 설계할 수 없다"처럼 보일 위험이 있었으나, 실제
   문서(`ARCHITECTURE_GOVERNANCE.md`)는 이미 이를 해결하는 절 2개
   (Experimental Implementation, Architecture Need)를 갖고 있었다 —
   문제는 Governance 부재가 아니라 **인지/인용 부재**였다.
2. **왜 Evidence-first만으로는 개발 속도가 제한되는지**: 사용자
   지적이 원칙적으로는 맞지만, Repository의 실제 Governance는 이미
   "Evidence-first"를 Formal Promotion에만 적용하고 Experimental
   단계는 Evidence 없이 허용하도록 설계돼 있었다.
3. **Future Architecture 허용 필요성**: 이미 충족됨 — `projects/`
   기반 Experimental Implementation이 정확히 이 역할을 한다(Phase 6
   Kernel Parallel Execution Prototype이 실제 선례).
4. **Architecture Lifecycle**: 사용자의 6단계는 기존 2단계
   (Experimental/Formal)를 더 세분화한 표현이며 새 규칙이 아니다.
5. **Evidence Lifecycle**: E0~E5가 가리키는 실체는 이미 Repository
   관행(등급 A/B/C/D, Dogfooding, Cross-HQ 3분류)에 존재. 숫자
   척도 공식화는 권고하지 않음.
6. **Kernel Promotion 조건**: 기존 `BASELINE.md` §11 Kernel 정의 +
   Phase 5 5기준 + ADC 채택 기준(2조건 중 1개)이 이미 이 역할을
   수행 중.
7. **Kernel Promotion Deferred 처리**: `DEFER`/`Not Accepted`/
   `CONDITIONAL FREEZE`로 이미 반복 적용되고 있는 기존 원칙과
   개념적으로 동일 — 실패로 취급된 적 없음(모든 사례가 재검토 조건을
   명시).
8. **BASELINE 영향**: 없음.
9. **RFC/ADC/ADR 필요 여부**: 불필요(A 판정). §9의 4개 Open
   Question은 문서 명명 정리 수준.
10. **Jarvis OS v2.0 적용 가능 여부**: 가능 — Unified Dashboard/
    Global Chat/Orchestration Candidate 전부 기존 Experimental
    Implementation 절 조건 안에서 Prototype 착수 가능(이번 Review는
    착수하지 않음).
11. **최종 Recommendation**: 기존 Governance(Experimental
    Implementation + Architecture Need)를 그대로 적용한다. 신규
    정책 제정이 아니라 **기존 정책의 재확인 및 명시적 인용**으로
    충분하다.

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음
Tests: 미실행(코드 변경 없어 불필요)
E2E: 미실행
RFC: 없음(신규 작성 안 함 — 기존 Governance로 충분, A 판정)
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: (본 문서 커밋 예정)
Branch: `claude/future-architecture-promotion-policy`
Next Implementation Candidate: 없음(정책 작업) — 실제 다음 단계는
Unified Dashboard Candidate 중 하나를 기존 "Experimental
Implementation" 절 조건에 따라 `projects/` 격리 Prototype으로
착수할지 여부를 사용자가 결정하는 것
