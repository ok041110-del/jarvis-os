# INVESTMENT-HQ-RISK-CHANGES-PORTFOLIO-REVALIDATION-0001

**문서 성격**: Experimental Dogfooding Evidence 문서(추가 검증).
`INVESTMENT-HQ-RISK-PORTFOLIO-BOUNDARY-DOGFOODING-0001.md`(판정 B —
RISK NEED PARTIALLY VALIDATED)가 §13에 남긴 선행조건 중 가장 핵심인
두 가지 — **(2) Risk가 실제로 Portfolio 결론을 바꾸는 사례를
의도적으로 설계**, **(4) Risk에 행동 추천 권한을 부여했을 때의
차이 확인** — 를 이번에 검증한다. Architecture 설계·Contract 확정을
하지 않는다. `hqs/investment/`는 수정하지 않는다(`git diff --stat
hqs/investment/` 빈 결과로 확인).

**방법론**: 격리된 `projects/synthesis-trader-expansion-prototype/
risk_changes_portfolio_prototype.py`(신규 파일)로 **실제 Engine
호출 3회(PASS1→PASS2→PASS3 순차)**를 수행했다. 새로운 시장/종목
데이터는 만들지 않았다 — QQQ의 AAPL(~7.1–7.3%)/NVDA(~8.5–8.9%)
구성비중은 기존 실제 ETF Team 산출물을 그대로 인용했다. **직접 보유
비중(8%/8%)과 QQQ 비중(30%), 그리고 "결합 look-through 노출 10%
상한" 정책은 이번 실험을 위해 의도적으로 구성한 가상 설정값**이다
— 정책을 명백히 위반하는 상황을 만들어야 "Risk가 실제로 Portfolio를
바꾸는지" 테스트할 수 있기 때문에, 위반이 발생하도록 숫자를
설계했다는 점을 정직하게 밝힌다(사용자의 재검증 요청 자체가 이런
설계를 요구함).

**이전 실험의 방법론 한계를 이번에 교정**: 이전 문서(§0)는 "Exposure
Path 합산 금지" 규칙을 실수로 누락해 Risk-only가 자체적으로 합산
계산을 했다. 이번에는 이를 **의도적으로 구분**했다 — "보고 시에는
Direct/Indirect를 분리 유지"하되, "정책 준수 여부를 확인하기 위한
목적에 한해 명시적으로 labeling된 합산 계산은 허용"하는 규칙을
프롬프트에 명시했다.

---

## 1. 실험 설계

| Pass | 역할 | 입력 | 권한 |
|---|---|---|---|
| PASS1 | Portfolio-only(최초) | Portfolio State + Trader Decision 3건 | 정책 위반 여부를 명시적으로 계산하지 않아도 됨(일반 구성 추론만) |
| PASS2 | Risk-only(행동 추천 권한 부여, 이전과 반대) | 동일 Portfolio State | Exposure Path를 분리 나열 + 정책 준수 여부를 **명시적으로 라벨링된 계산**으로 확인 + 위반 시 구체적 완화 조치 추천 |
| PASS3 | Portfolio-재고 | PASS1 결론 + PASS2 결과만 제공(원본 데이터 재제공 안 함) | PASS2가 PASS1을 실제로 바꾸는지, 아니면 같은 결론의 재서술일 뿐인지 명시적으로 답하도록 요구 |

**Portfolio State**(가상 설정, §0 명시):
```
Direct AAPL 8% (HOLD) / Direct NVDA 8% (HOLD) / QQQ 30% (HOLD)
QQQ 내부: AAPL ~7.1-7.3%, NVDA ~8.5-8.9%(실제 기존 산출물 인용)
정책: "개별 종목에 대한 결합 look-through 노출(직접+ETF 경유)은
포트폴리오 가치의 10%를 초과할 수 없다"
```

---

## 2. PASS1 — Portfolio-only(최초 결론)

**실제 응답 요약**: "세 포지션 전부 HOLD → 변경 없음(AAPL 8%/NVDA
8%/QQQ 30% 유지)." 그리고 **스스로 다음을 명시적으로 범위 밖으로
표시**했다: *"whether AAPL's and NVDA's look-through exposure via QQQ
pushes their combined single-name exposure past the stated 10% policy
cap is a cross-holding compliance calculation, not ordinary
composition reasoning — flagged as a candidate for a dedicated
policy-compliance check, not resolved here."*

**관찰**: PASS1은 정책 위반 여부를 **알아서 계산하지 않았다** — 이는
프롬프트가 유도한 것이기도 하지만(§1 "명시적으로 계산하지 않아도
됨"), 동시에 "이건 일반 구성 추론의 범위가 아니다"라고 **스스로
판단해서 넘긴 것**이기도 하다. 이는 Portfolio 단독 관점이 이런 종류의
교차보유 계산을 자연스러운 자기 업무로 여기지 않는다는 것을 보여준다.

---

## 3. PASS2 — Risk-only(행동 추천 권한 부여)

**(1) Exposure Path — 분리 유지(합산 없음)**:
```
AAPL: Direct 8% / Indirect(QQQ) 2.13-2.19%  [별도 라인 유지]
NVDA: Direct 8% / Indirect(QQQ) 2.55-2.67%  [별도 라인 유지]
```

**(2) 정책 준수 계산(명시적으로 라벨링, "true exposure" 주장이
아님을 스스로 명기)**:
```
AAPL: 8% + 2.13-2.19% = 10.13-10.19%  → 10% 상한 위반, 약 0.13-0.19%p 초과
NVDA: 8% + 2.55-2.67% = 10.55-10.67%  → 10% 상한 위반, 약 0.55-0.67%p 초과(AAPL의 3-4배)
```

**(3) 실제 추천 행동**: QQQ 자체를 줄이는 것("무차별적, 파급 범위가
더 큰 수단")보다 **직접 보유분을 각각 정밀하게 트림**하는 것을
권고 — AAPL 8%→~7.8%, NVDA 8%→~7.3–7.4%. 그리고 이 조정이 **"HOLD
방향 판단을 뒤집는 것이 아니라, 그 위에 얹는 정책 규모 조정일
뿐"**이라고 명시적으로 구분했다(Trader의 방향 판단과 Risk의 정책
준수 조정을 혼동하지 않음).

---

## 4. PASS3 — Portfolio 재고(가장 중요한 질문)

**실제 응답(전문 발췌)**: *"Different actions, not a restatement.
PASS1's conclusion was 'no changes' as an unqualified end-state...
PASS2 doesn't dispute the HOLD directional calls — it adds a
constraint PASS1 didn't evaluate... 'No changes' and 'trim AAPL/NVDA
to restore compliance' are materially different portfolio end-states,
not two phrasings of the same one."*

**핵심 결론**: PASS2는 PASS1의 최종 결론을 **실제로 대체(supersede)
했다** — PASS1의 방향성 추론(HOLD는 방향 신호가 아니다)을 무효화한
것은 아니지만, **최종 포트폴리오 상태(AAPL/NVDA의 실제 비중)는
PASS1이 아니라 PASS2를 반영해 바뀐다**는 것을 PASS3가 명시적으로
확인했다.

---

## 5. 이전 문서 대비 무엇이 달라졌는가

| 항목 | 이전 문서(Boundary Dogfooding) | 이번 재검증 |
|---|---|---|
| Risk가 Portfolio 결론을 바꾸는가 | STEP3-C: **아니오**(보강만, 정책 위반 없는 시나리오) | PASS3: **예**(정책을 명백히 위반하는 시나리오로 설계) |
| Exposure Path 합산 처리 | 실수로 규칙 누락, Risk가 임의로 합산 | 의도적으로 "보고는 분리, 정책 확인용 계산은 명시적 라벨링" 규칙을 부여 — Risk가 규칙을 정확히 따름(§3) |
| Risk의 권한 | 행동 추천 금지 | 행동 추천 허용(이번엔 명시적으로 부여) |

**해석**: 이전 문서의 STEP3-C가 "바뀌지 않음"으로 나온 것은 Risk가
무력해서가 아니라, **그 시나리오 자체가 정책 위반 수준이 아니었기
때문**(look-through 초과분이 0.7~0.9%p에 불과, 명시적 정책 자체가
없었음)이라는 것이 이번 재검증으로 확인됐다. 정책이 있고 실제로
위반되는 시나리오에서는 **Risk가 실제로, 구체적으로 Portfolio의
최종 구성을 바꿨다.**

---

## 6. Trader ↔ Risk 경계(재확인)

PASS2가 스스로 구분한 문장(§3)이 이전 문서(§8)의 관찰을 다시
뒷받침한다 — Trader의 HOLD(방향 판단)와 Risk의 트림 권고(정책 규모
조정)는 **서로 다른 종류의 결정**이며, Risk는 Trader의 방향 판단을
"틀렸다"고 말하지 않고 그 위에 별도 층으로 작동했다.

---

## 7. Contract 후보 Evidence(확정 아님, 갱신)

| 관찰 | 근거 |
|---|---|
| "보고용 분리 표기"와 "정책 확인용 명시적 합산"은 공존 가능하다 | §3 — Risk가 두 형식을 혼동 없이 둘 다 정확히 수행 |
| 정책 위반 시 Risk의 권고는 방향 판단(HOLD/BUY/SELL)이 아니라 "같은 방향 유지 + 규모 조정"의 형태로 나타났다 | §3, §6 |
| Risk의 권고는 ETF 자체를 건드리기보다 개별 직접 보유분을 정밀 조정하는 쪽을 우선했다("파급 범위가 더 큰 수단"이라는 이유로 QQQ 트림을 대안으로만 남김) | §3 — n=1, 반복 확인 필요 |

여전히 필드명(`RiskLimit` 등)이나 Schema를 확정하지 않는다.

---

## 8. 최종 판정

## **A. RISK NEED VALIDATED**(단, n=1 재확인 필요 명시)

**이전 판정(B)에서 A로 올리는 이유**: 이전 문서가 A로 올리지 못한
핵심 이유(§12 "Risk가 Portfolio 판단을 바꾸는 가장 강한 형태의
Evidence가 없었다")가 이번 실험으로 **직접, 구체적으로 해소**됐다
— PASS3가 "다른 행동이다, 재서술이 아니다"라고 명시적으로 확인했고,
그 차이(AAPL 8%→7.8%, NVDA 8%→7.3–7.4%)가 수치로도 명확했다.

**그럼에도 완전히 확정하지 않는 이유**: 이번 실험도 **n=1**이다 —
정책 위반이 설계된 단 하나의 시나리오에서만 확인됐다. 사용자
지시(§8 재확인)와 이 세션 전체의 원칙("절대 단일 사례만으로 확정하지
않는다")에 따라, **이 판정은 재현 가능성이 아직 완전히 검증되지
않은 A**로 기록한다.

---

## 9. 다음 선행조건

1. **다른 정책 위반 시나리오로 1~2회 반복** — 예: Dividend Stock
   조합(PG+JNJ)에 "동일 섹터 결합 노출 15% 상한" 같은 정책을 주고
   동일 PASS1→PASS2→PASS3 구조로 재현되는지 확인.
2. **위반이 아주 근소한 경우와 아주 큰 경우를 대조** — 이번 사례는
   위반폭이 작았다(AAPL 0.13~0.19%p, NVDA 0.55~0.67%p). 위반폭이
   커질수록 PASS3의 "바뀐다"는 결론이 더 강하게 나오는지, 아니면
   문턱 효과가 있는지 확인.
3. 이번 판정(A, n=1 명시)은 여전히 Risk Component 구현이나
   Architecture 확정을 허가하지 않는다 — Architecture Freeze Review는
   위 반복 검증 이후 별도 문서에서 판단한다.

---

## Self Review

- Risk Architecture나 Contract를 설계했는가 — **아니오**(§7, 요구
  사항만 기록).
- 정책 위반이 발생하도록 숫자를 의도적으로 설계했음을 숨겼는가 —
  **아니오**(§0에서 명시적으로 밝힘, 이는 사용자가 요청한 재검증의
  목적 자체).
- n=1이라는 한계를 숨기고 A로 확정 발표했는가 — **아니오**(§8·§9에서
  명시).
- `hqs/investment/`, Structure v1.0, RFC/ADC/ADR, Phase 7을
  수정했는가 — **아니오**(`git diff --stat hqs/investment/` 빈
  결과로 재확인).
