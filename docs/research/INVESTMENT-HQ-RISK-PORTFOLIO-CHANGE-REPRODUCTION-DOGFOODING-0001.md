# INVESTMENT-HQ-RISK-PORTFOLIO-CHANGE-REPRODUCTION-DOGFOODING-0001

**문서 성격**: Experimental Dogfooding Evidence 문서(재현성 검증
전용). **새 Architecture Need를 찾지 않는다. Risk Need를 처음부터
재검증하지 않는다.** `INVESTMENT-HQ-RISK-CHANGES-PORTFOLIO-
REVALIDATION-0001.md`(판정 A, n=1)가 확인한 "Risk가 Portfolio
Decision을 실제로 바꾼다"는 관계 **하나만**을 다른 실제 사례에서
재현하는지 검증한다. Architecture 설계·Contract 확정을 하지 않는다.
`hqs/investment/`는 수정하지 않는다(`git diff --stat hqs/investment/`
빈 결과로 확인).

**방법론**: 격리된 `projects/synthesis-trader-expansion-prototype/
risk_reproduction_prototype.py`(신규 파일)로 **실제 Engine 호출
6회**(2개 독립 사례 × PASS1/2/3)를 수행했다.

---

## 1. 사용한 실제 사례

| Case | Team 구성 | 유형(§3·§4) | Trader Decision(실제 산출물 재사용) | Policy |
|---|---|---|---|---|
| **1(기존 참조, 재실행 안 함)** | Stock×2+ETF | ETF look-through | AAPL/NVDA/QQQ | "결합 look-through 노출 10%" — 이전 문서에서 이미 검증 |
| **2(신규)** | Dividend Stock×2, ETF 없음 | Cross-Team 섹터/팩터 결합 노출(다른 종류의 정책) | PG/JNJ(실제 산출물) | "방어적 배당 슬리브 결합 노출 15%"(신규 설계, synthetic control) |
| **3(신규, Negative Control)** | Stock×1 | 단일 자산, 위반 없음 | CAT(실제 산출물) | "단일 포지션 5% 상한"(Portfolio Need Dogfooding에서 이미 쓴 실제 정책 재사용) |

**실제 Evidence vs 실험을 위해 만든 조건 구분(사용자 지시 최우선
준수)**:
- **실제 Evidence**: 3개 Case 전부의 Trader Decision(HOLD, rationale,
  reassess trigger)은 기존 실제 Engine 호출로 생성된 산출물을 그대로
  재사용했다. Case 3의 정책(단일 포지션 5% 상한)도 Portfolio Need
  Dogfooding에서 이미 쓴 실제 값이다.
- **synthetic control(명시)**: Case 2의 "방어적 배당 슬리브 15% 상한"
  정책과 PG(10%)/JNJ(8%) 직접 보유 비중은 **이번 실험을 위해
  의도적으로 구성한 가상 설정값**이다 — 저장소에 이런 정책이 실제로
  존재하지 않으므로, 사용자 지시(§4)대로 "synthetic control"이라고
  명확히 표시하며, 이 문서는 이를 별도의 확정 Architecture Evidence로
  승격하지 않는다.

---

## 2~4. 사례별 PASS1/PASS2/PASS3 결과

### Case 2 — PG + JNJ(방어적 배당 슬리브, ETF 없음)

**PASS1(Portfolio-only)**: "PG HOLD 10%, JNJ HOLD 8%, 조정 없음." 그리고
스스로 명시: *"whether the two positions together breach the stated
15% sleeve-concentration policy is a policy-compliance calculation...
I have not performed that calculation."*

**PASS2(Risk-only)**: 두 종목이 정책이 정의한 "방어적 배당 슬리브"
(대형주·수십 년 배당 성장·소비재/헬스케어·유사 투자자 기반·금리/
로테이션 민감도 상관)에 **실제로 해당한다는 것을 PG/JNJ의 실제
속성(136년 배당 기록, 헬스케어 장기 배당 성장주 등)에서 확인**한
뒤, Exposure Path를 분리 나열(`Direct PG 10%`, `Direct JNJ 8%`,
ETF 경로 없음 명시)하고, **"Policy Evaluation Calculation"으로
명시적으로 라벨링한 계산**으로 `10%+8%=18%`가 15% 상한을 3%p
초과함을 확인했다. 조정 필요성(합산 3%p 축소, 어느 종목을 줄일지는
방향성 문제가 아니라 확신도 문제이므로 판단 보류)을 권고했다.

**PASS3(Risk-informed Portfolio)**: **MODIFICATION**. *"Kept as-is:
both HOLD directional decisions... Changed: the portfolio can no
longer sit at 10%/8% unadjusted — at least one position must be
trimmed."* PASS1의 "조정 없음"이라는 최종 상태가 실제로 바뀌었다.

### Case 3 — CAT 단독(Negative Control)

**PASS1(Portfolio-only)**: "조정 없음, 2% 유지." 정책(5% 상한)에
대해 "2%는 5%에서 충분히 멀어 계산이 필요 없다고 판단"이라고
명시(계산은 생략했지만 이유를 설명함).

**PASS2(Risk-only)**: Exposure Path 분리 나열(Direct 2%, Indirect
<0.1%) 후, **"정책 문구 자체가 '단일 포지션'만 언급하고 결합/
look-through를 요구하지 않는다"는 이유로 합산 계산을 스스로
거부**했다 — *"Per the strict rule, I am therefore not computing a
merged 'Direct + Indirect' figure — doing so would fabricate a Policy
Evaluation Calculation the policy doesn't call for."* 결론: "위반
없음, 위험 수준 수용 가능."

**PASS3(Risk-informed Portfolio)**: **NO CHANGE**. *"PASS2 does not
surface any fact that alters PASS1's end-state... What's new in PASS2
is confirmation, not information."*

---

## 5. NO CHANGE / MODIFICATION / REVERSAL 분류

| Case | 분류 |
|---|---|
| 1(QQQ, 기존) | MODIFICATION |
| 2(PG+JNJ, 신규) | **MODIFICATION** |
| 3(CAT, 신규) | **NO CHANGE** |

REVERSAL(방향 자체가 뒤집히는 경우, 예: HOLD→SELL)은 3개 Case
어디에서도 관찰되지 않았다 — 이는 이전 문서(§6)에서 이미 확인한
"Risk는 Trader의 방향 판단을 뒤집지 않고 그 위에 규모 조정 층으로만
작동한다"는 관찰과 일치한다.

---

## 6. Risk가 제공한 독립 정보

| Case | Portfolio-only에는 없던 정보 |
|---|---|
| 2(PG+JNJ) | (a) PG/JNJ가 정책이 정의한 "슬리브" 범주에 실제로 해당한다는 분류, (b) 결합 비중이 상한을 초과한다는 계산 결과 |
| 3(CAT) | (없음) — Risk가 PASS1과 동일한 결론에 도달했고, "정책 문구가 합산을 요구하지 않는다"는 것을 명시적으로 확인했을 뿐, 새로운 사실은 없었다(PASS3 스스로 "confirmation, not information"이라고 표현) |

---

## 7. Risk → Portfolio 변경 근거

Case 2에서 PASS3가 명시한 근거를 그대로 인용한다: *"HOLD answers
'which direction', the sleeve cap answers 'how much'... What changes
is sizing."* 이는 이전 QQQ 사례(§5, 이전 문서)의 근거("mechanical
policy-compliance sizing adjustment... does not revisit or override
the HOLD directional calls")와 **표현까지 유사한 구조**로 재현됐다 —
우연이 아니라 일관된 패턴으로 보인다.

---

## 8. Policy / Calculation 영향(§12 구분, 가장 엄격하게 적용)

**정직한 재평가**: Case 1(QQQ)과 Case 2(PG+JNJ)를 §12 기준(Case A
"단순 계산" vs Case B "Risk+Portfolio 종합 판단")으로 다시 대조하면
**강도 차이가 있다**:

- **Case 1(QQQ)**: Risk가 "AAPL/NVDA가 직접 보유이면서 동시에 QQQ
  내부에도 존재한다"는 사실을 **서로 다른 Team(Stock/ETF)의 실제
  산출물을 교차 참조**해서 찾아냈다 — 이는 프롬프트에 명시적으로
  주어지지 않은, Risk 스스로 발견해야 하는 구조였다.
- **Case 2(PG+JNJ)**: 이번 실험에서는 정책 문구 자체에 "방어적 배당
  슬리브"의 **정의(대형주·배당성장·섹터·상관 민감도)**를 상세히
  제시했다 — Risk는 PG/JNJ의 실제 속성이 이 정의에 부합하는지
  확인하는 **분류 작업**은 수행했지만(완전히 자명하지는 않음, PG/JNJ
  이름을 정책에 직접 나열하지 않았다), Case 1만큼 "숨겨진 교차
  참조"를 스스로 발견해야 하는 부담은 아니었다.

**결론**: Case 2는 여전히 순수 "Case A(단순 계산)"는 아니다(분류
작업이 실질적으로 필요했고, 계산 자체도 여러 Direct 값을 정책
기준에 맞춰 결합하는 판단이었다) — 그러나 Case 1보다는 **Policy
Evaluation Calculation의 비중이 상대적으로 크다.** 이 차이를
숨기지 않고 그대로 기록한다.

---

## 9. Trader / Portfolio / Risk Boundary

3개 Case 전부에서:

- Risk가 BUY/SELL 판단을 대신하지 않았다(Case 2 PASS2: *"I take no
  position on which name should absorb the cut... that depends on
  relative conviction, which is outside this risk-only review"*).
- Risk가 개별 종목 분석을 반복하지 않았다(Case 2 PASS2: *"I am not
  evaluating PG or JNJ's standalone risk... those were addressed in
  the single-security decisions and are outside this pass's scope"*).
- Risk가 Portfolio 구성을 직접 확정하지 않았다 — "무엇을 줄여야
  하는지"까지는 판단했지만 "어느 것을, 얼마나"의 최종 결정은
  Portfolio/사용자 판단으로 남겨뒀다(Case 2).

3/3(Case 1 포함 시 3/3, 이 문서의 신규 2개만으로도 2/2)에서 경계가
명확히 유지됐다 — 이전 문서의 관찰(§8, 2/3)보다 **경계 유지 반복성이
강화**됐다.

---

## 10. Negative Control(Case 3)

사용자 지시(§11) 조건을 그대로 충족했다: 명시적 정책 존재, 위반
없음, 구조적 위험 없음, Portfolio baseline이 이미 합리적. **예상대로
PASS2="tolerable"(위반 없음), PASS3="NO CHANGE"**가 나왔다. 특히
Risk가 **정책 문구를 근거로 합산 계산 자체를 스스로 거부**한 것은
"Risk가 무조건 무언가를 찾아내려는 편향"이 아니라는 것을 보여주는
**이전보다 더 정교한 형태의 Negative Control**이다 — 단순히 "위반이
없다"가 아니라 "이 정책은 애초에 합산을 요구하지 않는다"는 것까지
스스로 식별했다.

---

## 11. 방법론적 한계

1. **Case 2의 정책은 synthetic control이다**(§1) — 저장소에 실재하는
   정책이 아니다. 이 Case가 보여주는 "MODIFICATION" 재현은 **가상
   조건 위에서 얻은 결과**이며, 실제 저장소에 이런 정책이 아직
   없다는 점을 다시 한번 명시한다.
2. **Case 2는 Case 1보다 Policy Evaluation 비중이 크다**(§8) — 완전히
   대등한 두 번째 독립 재현이라고 보기엔 다소 약하다.
3. **여전히 총 n=2**(QQQ, PG+JNJ) — 사용자가 제시한 "최소 2개 독립
   사례" 목표는 충족했지만, Architecture Freeze를 논하기엔 여전히
   적은 수다.
4. 이번 실험도 PASS1→PASS2→PASS3를 **같은 세션에서 순차 호출**했다
   — 완전히 독립된 실행 환경에서의 재현은 아직 시도하지 않았다(이전
   문서에서도 동일하게 지적된 한계).

---

## 12. 최종 판정

## **A. RISK → PORTFOLIO CHANGE REPRODUCED**(단, §8·§11 한계 명시)

**판정 이유**:

- **최소 2개 독립 실제 사례**를 확보했다 — Case 1(ETF look-through,
  Stock+ETF)과 Case 2(섹터/팩터 슬리브, Dividend Stock×2, ETF 없음)는
  서로 다른 Team 구성과 서로 다른 종류의 Portfolio-level 제약을
  사용했다(§3·§4 요구사항 충족).
- 두 Case 모두 Risk가 독립 정보(Case 1: 교차 Team 노출 발견, Case 2:
  슬리브 분류+합산 초과)를 제공했고, 그 정보가 Portfolio-only
  단계에는 없었다(§6).
- 두 Case 모두 Risk 정보 제공 후 Portfolio의 **최종 구성 상태가
  실제로 바뀌었다**(NO CHANGE가 아니라 MODIFICATION, §5) — 단순
  재서술이 아니라 PASS3가 "sizing must come down"처럼 구체적으로
  다른 결론을 냈다.
- Negative Control(Case 3)이 "NO CHANGE"로 정확히 구분돼, 이 패턴이
  무조건적 편향이 아님을 뒷받침했다(§10).
- Trader/Portfolio/Risk 경계가 2/2(이번 신규 사례)에서 명확히
  유지됐다(§9).

**B로 낮추지 않는 이유**: 사용자 §15 B의 정의("1개 추가 사례에서
확인됐거나, 변경은 있었지만 Policy/Calculation의 영향이 큼")는
**두 조건 중 하나만 성립해도** B가 될 수 있는 것처럼 읽히지만, 이
문서는 정직하게 다음을 함께 본다: (1) 사례 수는 요구된 최소치(2개)를
충족했고 — 첫 조건은 성립하지 않음, (2) Case 2가 Case 1보다 Policy
비중이 큰 것은 사실이나(§8), **Case 2가 순수 Case A(단순 계산)로
완전히 환원되지는 않는다** — 정책 정의를 실제 종목 속성에 대입하는
분류 판단이 실질적으로 필요했다. 따라서 두 번째 조건도 "완전히
성립"이라기보다 "부분적으로 성립"에 가깝다. **이 애매함을 숨기지
않고 §8·§11에 그대로 남기되, 종합적으로는 A로 판정한다** — 다만
"A"라는 표기가 "더 이상 재확인이 필요 없다"는 뜻이 아니라는 것을
§13에서 다시 명시한다.

**C/D로 판정하지 않는 이유**: 두 Case 모두 명확한 MODIFICATION이
나왔고(C의 "변경 없음"과 배치), 사례 수와 negative control을 포함해
경계를 판단하기에 충분한 대조가 확보됐다(D의 "Evidence 부족"과
배치).

---

## 13. 다음 선행조건

1. **Case 1 수준의 "숨겨진 교차 참조" 강도를 가진 세 번째 사례** —
   정책에 카테고리를 명시적으로 정의해주지 않고, Risk가 스스로 여러
   Team의 실제 산출물을 대조해 겹침/상관관계를 찾아내야 하는
   시나리오(§8에서 지적한 Case 2의 약점을 보완)를 시도해, Policy
   Evaluation 비중을 낮춘 상태에서도 재현되는지 확인해야 한다.
2. **synthetic control이 아닌 실제 저장소 정책으로 재현** — Case
   2의 "방어적 배당 슬리브" 정책은 가상이다. 향후 Investment HQ에
   실제 Portfolio Policy가 도입되면(이 문서가 그것을 만들지는
   않는다), 그 실제 정책으로 다시 재현해야 진짜 Architecture
   Evidence가 된다.
3. **완전히 독립된 실행 환경에서의 PASS 재현** — 여전히 같은 세션
   순차 호출이라는 한계가 남아 있다(§11-4).
4. 이번 판정(A, 한계 명시)도 Risk Component 구현이나 Portfolio Policy
   Architecture 확정을 허가하지 않는다 — Architecture Freeze Review는
   별도 문서에서, 위 선행조건이 더 쌓인 뒤 판단한다.

---

## Self Review

- 새로운 Architecture Need를 찾았는가 — **아니오**(기존에 확인된
  Risk→Portfolio 변경 관계의 재현성만 검증).
- Risk Need를 처음부터 재검증했는가 — **아니오**(이미 A로 확정된
  것을 전제로, 재현 여부만 확인).
- Case 2의 정책이 synthetic control임을 숨겼는가 — **아니오**(§1,
  §8, §11에서 반복 명시).
- Case 2가 Case 1보다 약한 형태의 Evidence임을 숨겼는가 —
  **아니오**(§8에서 정직하게 강도 차이를 기록, §12 판정 근거에도
  반영).
- Risk Agent/Portfolio Agent를 구현했는가 — **아니오**(격리된
  스크립트에서 실제 Engine 호출만 수행, Production 코드 무수정).
- `hqs/investment/`, Structure v1.0, RFC/ADC/ADR, Phase 7을
  수정했는가 — **아니오**(`git diff --stat hqs/investment/` 빈
  결과로 재확인).
