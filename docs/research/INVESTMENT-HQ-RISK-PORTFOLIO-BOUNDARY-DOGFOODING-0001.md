# INVESTMENT-HQ-RISK-PORTFOLIO-BOUNDARY-DOGFOODING-0001

**문서 성격**: Experimental Dogfooding Evidence 문서. **Risk
Architecture를 설계·확정하지 않는다.** RFC/ADC/ADR을 생성하지 않고,
`hqs/investment/`·Structure v1.0·Architecture Baseline·Phase 7 상태를
수정하지 않는다(`git diff --stat hqs/investment/` 빈 결과로 확인).
`RiskDecision`/`RiskScore`/`RiskLevel`/`RiskLimit` 등 어떤 이름·필드도
Contract로 확정하지 않는다.

**방법론**: 격리된 `projects/synthesis-trader-expansion-prototype/
risk_boundary_prototype.py`(신규 파일)로 **실제 Engine 호출 6회**를
수행했다. 새로운 시장 데이터를 만들지 않았다 — Portfolio State는
이전 두 Dogfooding 문서(Portfolio Need, ETF Look-through)에서 이미
쓴 값을 그대로 재사용했다. Portfolio 질문과 Risk 질문을 **의도적으로
분리된 프롬프트**로 던지고, 각 프롬프트에서 상대측 언어(Portfolio
프롬프트에서 "위험/tolerable" 사용 금지, Risk 프롬프트에서
"매수/매도/조정 추천" 금지)를 명시적으로 금지해 교차 오염을
차단했다.

**방법론 한계(정직하게 기록)**: 이전 ETF Look-through Dogfooding에서
썼던 "서로 다른 Exposure Path를 합산 금지"라는 명시적 규칙을 이번
프롬프트에 다시 넣는 것을 빠뜨렸다. 그 결과 실제로 Risk-only/STEP3
프롬프트에서는 모델이 Direct+Indirect를 "10.71%" 같은 **단일 합산
수치로 계산**했다(§3). 이는 계획된 실험이 아니라 실수였지만, 아래
§6에서 설명하듯 이 우연한 차이 자체가 **Portfolio와 Risk의 실제
입출력 차이를 보여주는 예상 밖의 Evidence**가 되어 그대로 기록하고
분석했다.

---

## 1. 사용한 실제 사례

| 실험 | Portfolio State(재사용, 신규 생성 없음) | Trader Decision(재사용) |
|---|---|---|
| STEP1/2/3(기술주+ETF 중복) | AAPL 10%+NVDA 10%+QQQ 10%(ETF Look-through Dogfooding과 동일) | AAPL/NVDA/QQQ(전부 HOLD, 실제 산출물) |
| Negative Control | CAT 2%, 5% 정책 있음(Portfolio Need Dogfooding과 동일) | CAT(HOLD, 실제 산출물) |
| Cross-Team(비-ETF) | PG 10%+JNJ 8%(Portfolio Need Dogfooding과 동일) | PG/JNJ(전부 HOLD, 실제 산출물) |

Stock(AAPL/NVDA/CAT) + Dividend Stock(PG/JNJ) + ETF(QQQ) 전부
포함(사용자 지시 §13 준수).

---

## 2. STEP 1 — Portfolio-only 결과

**질문**: "이 Portfolio를 어떻게 구성/조정해야 하는가?"(Risk 언어
명시적 금지)

**실제 응답 요약**: "세 포지션 모두 HOLD 유지." 근거로 QQQ의 실제
공개 구성(AAPL~7.1–7.3%, NVDA~8.5–8.9%)이 "두 개의 다른 항목 아래
같은 자산이 존재한다는 사실"이라고 언급했지만, **"이것이 받아들일
만한지"는 명시적으로 판단하지 않았다** — "This is a factual overlap
... not a judgment about whether that overlap is acceptable"라고
스스로 선을 그었다. 정책이 없다는 것도 "판단할 기준이 없다"는
사실로만 언급했다.

**관찰**: Risk 언어 없이도 Portfolio 판단(HOLD 유지)은 완결됐다 —
다만 "재평가 시 QQQ/AAPL/NVDA를 같이 볼 필요가 있다"는 **관찰**을
자연스럽게 포함시켰다(지시받지 않았음에도).

---

## 3. STEP 2 — Risk-only 결과

**질문**: "이 Portfolio에 어떤 위험이 있고, 그 위험이 허용 가능한가?"
(매수/매도/조정 추천 명시적 금지)

**실제 응답 요약**: 4가지 위험을 나열 — (1) 명목 집중도(3개 10%
포지션), (2) **look-through 집중도**("AAPL total look-through
exposure ≈ 10%+10%×7.2% ≈ **10.7%**"로 **실제로 합산 계산**),
(3) "다양화의 착시"(QQQ가 사실 같은 대형 기술주에 집중돼 있어
독립적 베팅이 아니라는 지적), (4) **상관된 촉발 조건 위험**(세
Decision의 재평가 조건이 서로 독립이 아니라 구조적으로 연결됨).
마지막에 "완전한 허용 가능성 판단은 정책 기준이 없어 유보하지만,
위험 자체는 실재하고 사소하지 않다"는 **명시적 tolerability
판단**을 시도했다.

**핵심 차이(계획 밖 발견, §0 한계 참조)**: STEP1은 Direct/Indirect를
별도로 유지했는데, STEP2는 **자발적으로 "10.7%"라는 합산 수치를
계산**했다. 이는 프롬프트 실수(합산 금지 규칙 누락) 때문에
가능해진 것이지만, 결과적으로 **Portfolio 질문과 Risk 질문이
"동일 데이터를 다루는 방식" 자체에서 실제로 다르다는 것**을
드러냈다(§6에서 상세 해석).

---

## 4. STEP 3 — Portfolio + Risk 결과

**STEP3-A**(Portfolio, Risk 언어 금지): §3처럼 **합산 계산을
수행**("10.71%–10.73%", "10.85%–10.89%")했다 — 이는 이번 STEP3
프롬프트가 "Composition conclusion"이라는 계산적 성격의 질문이었기
때문으로 보인다(STEP1의 "어떻게 조정할 것인가"라는 행동 질문과는
다른 하위 질문 성격).

**STEP3-B**(Risk, 구성 추천 금지): STEP3-A의 수치를 그대로 받아
"단일 종목 충격이 두 줄(직접+QQQ 경유)을 동시에 움직인다", "AAPL/
NVDA는 마침 결론이 아직 열려 있는 이름들"이라는 **위험의 성격**을
설명했다. 구성 추천은 하지 않았다(지시 준수 확인).

**STEP3-C**(Risk가 Portfolio를 바꾸는가 — 가장 중요한 질문): **실제
답: "No — 수치·구조 결론(구성 자체)은 바뀌지 않는다. STEP3-B는
STEP3-A를 대체(revise)하는 것이 아니라 그 의미를 보강(refine)한다."**
모델은 명시적으로 "두 STEP은 상호보완적 렌즈(구성이 무엇인지 vs.
그 구성이 무엇을 의미하는지)이지, 같은 결론의 순차적 수정이
아니다"라고 답했다.

---

## 5. Portfolio / Risk 입력 차이

| 입력 | Portfolio-only(STEP1) | Risk-only(STEP2) |
|---|---|---|
| Trader Decision 방향(HOLD 등) | 그대로 사용(구성 유지/조정의 직접 근거) | 배경으로만 참조("HOLD인 이유가 미해결 촉발조건") |
| Exposure Path(Direct/Indirect) | 별도 라인 유지, 합산 안 함(자체적으로) | **합산해서 재계산**(0.7~0.9pp를 direct에 더함, §0 한계와 결합된 관찰) |
| QQQ의 top-5 집중도(~30–33%) | "관찰"로만 언급 | "다양화 착시"라는 **해석**으로 사용 |
| 정책 부재 | "판단 기준이 없다"(사실 서술) | "허용 가능성을 확정할 수 없는 이유"(판단의 한계로 명시) |

**결론**: 입력 데이터 자체(Trader Decision, Portfolio State, Exposure
정보)는 동일했지만, **그 데이터를 다루는 방식과 최종적으로 도출하는
것의 성격이 실제로 달랐다** — Portfolio는 "무엇을 유지/조정할
것인가"라는 행동 결론에서 멈췄고, Risk는 "그 구성이 만드는 위험의
성격과 정도"라는 평가 결론까지 나아갔다.

---

## 6. Portfolio / Risk 판단 차이

**Calculation/Policy/Portfolio/Risk 구분(§9 기준) 적용**:

| 사례 | 분류 |
|---|---|
| STEP1(HOLD 유지 결론) | **C. Portfolio Decision** — Trader Decision을 그대로 조합했을 뿐 새 계산은 아니지만, "재평가 시 세 종목을 같이 볼 필요"라는 종합은 단순 계산이 아님 |
| STEP2(위험 나열+tolerability 판단) | **D. Risk Decision** — 집중도/상관관계라는 Portfolio에는 없던 관점, "위험이 사소하지 않다"는 명시적 평가적 결론 |
| STEP3-C(Risk가 구성 결론을 바꾸지 않음) | 이번 사례에서는 D가 C를 **바꾸지 않고 보강**했다 — 이는 §16 판정에서 "C와 D가 항상 다른 결론을 낳는다"는 강한 형태의 Evidence는 아니라는 뜻 |

**핵심 관찰**: C와 D는 **같은 사실에서 출발**하지만 **다른 질문에
답한다** — C는 "무엇을 할 것인가", D는 "그것이 어떤 위험인가"라는
점에서 사용자의 원 가설(§2)과 일치한다. 다만 이번 사례에서는 D의
답이 C의 답을 뒤집지 않았다(§7에서 상세).

---

## 7. Risk → Portfolio 영향

**STEP3-C가 이 질문에 대한 가장 직접적인 답이다**: 이번 실험
1건에서는 **Risk 판단이 Portfolio 판단을 바꾸지 않았다**(HOLD
유지 결론 그대로) — Risk는 "왜 이 구성이 신경 쓸 만한지"를
설명했을 뿐, "그러니 QQQ를 줄여라" 같은 새로운 행동으로 이어지지
않았다(애초에 그렇게 하지 말라고 지시했기 때문이기도 하다 — 이
결과가 "Risk는 원래 Portfolio를 못 바꾼다"를 증명하는 것은 아니다,
프롬프트가 애초에 Risk에게 행동 추천을 금지했으므로 이 질문에
답하도록 설계되지 않았다).

**사용자가 §7에서 제시한 "강한 Evidence" 형태**(Risk 결과가 Portfolio
판단을 실제로 바꾸는 사례)는 **이번 실험에서 관찰되지 않았다** —
정직하게 기록한다. 이는:

1. 실제로 이 정도 크기의 위험(10.7~10.9%, 정책 상한 없음)이 행동
   변경을 정당화할 만큼 크지 않았을 수도 있고,
2. 프롬프트 설계상 Risk-only 단계에 애초에 "행동을 바꿔라"고 말할
   권한을 주지 않았기 때문일 수도 있다(§8 선행조건에서 재설계
   필요성 기록).

---

## 8. Trader / Risk 경계

Negative Control(CAT) Risk-only 응답이 이 경계를 가장 명확하게
보여줬다: *"This uncertainty is real but is a company-specific/
fundamental risk, not a portfolio-structural one — its impact on the
overall portfolio is bounded by the position's 2% weight."*

기술주 사례(STEP2)도 동일한 구분을 했다: 집중도/상관관계/다양화
착시는 **Portfolio-structural risk**로, CAT/AAPL/NVDA 각각의 가이던스
불확실성 같은 것은 **개별 종목(name-level) risk**로 구분했다 —
후자는 이미 Trader Decision의 rationale에 담겨 있던 것이고, Risk는
그것을 반복하지 않고 "여러 종목에 걸친 구조" 쪽만 다뤘다.

**결론**: 2/3 Risk-only 실험(CAT negative control, 기술주)에서 **Risk가
Trader의 개별 종목 판단을 반복하지 않고, Trader가 원천적으로 볼 수
없는 구조(여러 포지션에 걸친 집중도·상관관계)만 다뤘다** — 이는
Trader↔Risk 경계가 실제로 존재한다는 근거이며, Risk를 Trader의
연장으로 볼 근거는 이번 실험에서 나오지 않았다.

---

## 9. Cross-Team Risk Need

PG(Dividend Stock)+JNJ(Dividend Stock) 조합으로 **ETF 없이도**
Cross-position Risk Need가 발생하는지 확인했다 — 결과: **예**, 그리고
이전 Portfolio Need Dogfooding이 발견한 것("재평가 조건이 같은
시기에 수렴")과 **다른 각도의 새 관찰**을 추가로 냈다: "PG와 JNJ는
둘 다 '퀄리티 컴파운더/배당귀족'류로 투자자 기반이 겹치고 금리·
디펜시브 로테이션 같은 거시 요인에 유사하게 반응한다"는 **팩터
상관관계**를 언급했다 — 이는 종목 간 직접적 사업 중복(같은 업종)이
아니라 **거시 민감도 상관관계**라는, 이전 Portfolio 관점의 분석에서는
나오지 않았던 새로운 정보였다.

**결론**: Cross-Team Risk Need는 ETF의 실제 구성종목 중복(QQQ 사례)
뿐 아니라, **업종이 다른 두 Dividend Stock 사이에서도(비-ETF)** 별도
형태로 나타났다 — Risk 관점이 Portfolio 관점과 다른 종류의 정보
(팩터/거시 상관관계)를 추가로 끌어낸다는 근거다.

---

## 10. Negative Control

CAT(2%, 정책 5% 있음, 중복 없음) 사례:

- **Portfolio-only**: "Hold unchanged." 명확하고 간단, 위험 언어
  없음.
- **Risk-only**: 집중도·상관관계·개별 불확실성을 각각 짚은 뒤,
  **"the current risk level appears tolerable at the portfolio
  level"**이라고 **명확하고 확정적인 결론**을 냈다 — 기술주/배당주
  사례가 "정책이 없어 확정할 수 없다"며 판단을 유보한 것과 **정반대**
  다.

**이 대조가 핵심 Negative Control이다**: 동일한 질문 형식(Risk-only
프롬프트)에 대해, 조건(정책 유무, 중복 유무)에 따라 **"확정 가능한
tolerable" vs "정책 부재로 유보"**라는 서로 다른 결론이 실제로
나왔다 — Risk 판단이 정형화된 고정 응답이 아니라 입력에 실제로
반응한다는 근거다.

---

## 11. Contract 후보 Evidence(확정 아님)

사용자 지시(§14)대로 필드명을 확정하지 않는다. 반복 관찰된 **정보/
판단 요구사항**만 기록한다:

| 관찰 | 근거 |
|---|---|
| 위험 판단은 종종 Direct+Indirect를 하나의 magnitude로 합산해서 다룬다(Portfolio는 분리 유지) | STEP2/STEP3-A/B에서 반복(단, §0에서 밝힌 프롬프트 누락과 결합된 관찰 — 확증 아님, 재검증 필요) |
| Tolerability 판단은 명시적 정책(상한 등)이 있을 때만 확정적으로 나온다 | §10 negative control과 §3·§9의 대조 |
| "상관관계"는 업종 중복(JNJ/PG 사례)과 팩터/거시 민감도(같은 사례에서 추가 발견) 두 형태로 나타난다 | §9 |
| 개별 종목 위험(name-level)과 구조적 위험(portfolio-structural)을 구분하는 표현이 반복됨 | §8, 2/3 |

---

## 12. 최종 판정

## **B. RISK NEED PARTIALLY VALIDATED**

**판정 이유**:

- Risk가 Portfolio와 **다른 질문**에 답한다는 것은 명확히 확인됐다
  (§2·§3·§6 — "무엇을 할 것인가" vs "그것이 어떤 위험인가").
- Risk가 Trader와도 다른 관점(구조적 위험 vs 개별 종목 위험)을
  가진다는 것도 확인됐다(§8).
- Negative Control이 정확히 구분됐다(§10) — 편향이 아니다.
- Cross-Team에서 Risk 고유의 새로운 정보(팩터 상관관계)가 추가로
  나왔다(§9).

**A(VALIDATED)로 완전히 올리지 않는 이유**:

1. **"Risk 결과가 Portfolio 판단을 바꾼다"는 가장 강한 형태의
   Evidence(§7, 사용자 §11)가 이번 1건(STEP3-C)에서는 관찰되지
   않았다** — Risk는 Portfolio 결론을 "보강"했을 뿐 "변경"하지
   않았다. 사용자 스스로도 이 관계가 반복 확인돼야 강한 Boundary
   근거가 된다고 명시했다(§11) — 이번엔 n=1이고, 그마저 "바뀌지
   않음"으로 나왔다.
2. **Direct/Indirect 합산 여부의 차이(§3, §4)가 계획된 통제
   실험이 아니라 프롬프트 누락에서 우연히 발견됐다** — 흥미로운
   단서이지만, 의도적으로 재현하지 않는 한 확증된 Evidence로 쓸 수
   없다(§0에서 정직하게 기록).
3. Risk와 Trader의 경계(§8)는 2/3 사례에서만 확인됐다 — 반복성이
   완전하지 않다.

**C(불필요)로 판정하지 않는 이유**: Risk-only 응답이 Portfolio-only
응답과 실질적으로 다른 정보(팩터 상관관계, 다양화 착시, tolerability
판단)를 반복적으로 냈다 — "이름만 다르고 결론은 같다"는 근거는
나오지 않았다.

**D(Evidence 부족)로 판정하지 않는 이유**: 6개 실험이 negative
control을 포함해 뚜렷한 대조를 만들어냈다 — 관찰 방법 자체는
잘 작동했다.

---

## 13. 다음 선행조건

1. **§0의 프롬프트 누락을 의도적으로 재현** — "합산 금지" 규칙을
   Risk-only 프롬프트에도 명시적으로 넣은 상태와, 넣지 않은 상태를
   나란히 비교해, §3~4에서 관찰된 "Risk는 합산하는 경향"이 우연이
   아니라 실제 패턴인지 확정해야 한다.
2. **"Risk가 Portfolio 결론을 실제로 바꾸는" 사례를 의도적으로
   설계** — 이번 STEP3-C는 "바뀌지 않음"이 나왔다. 정책이 있는
   상태에서 정책을 위반하는 수준의 노출(예: 정책 "종목당 최대
   10%"인데 look-through 포함 15% 노출)을 가진 Portfolio State로
   재시도해, Risk가 실제로 Portfolio 결론(HOLD→trim 등)을 바꾸는지
   확인해야 한다 — 이것이 §16 A 판정으로 올라가기 위한 핵심
   선행조건이다.
3. **Trader/Risk 경계를 3/3으로 확장** — 현재 2/3(CAT negative
   control, 기술주)만 명확했다. Dividend 사례에서도 이 구분이
   명시적으로 나오는지 재확인.
4. **Risk-only 프롬프트에 "행동 변경 권한"을 부여한 버전도 시도** —
   이번엔 의도적으로 Risk가 행동을 추천하지 못하게 막았다. Risk가
   행동까지 말할 수 있게 허용했을 때 Portfolio-only 결론과 실제로
   달라지는지 별도로 확인해야, "권한이 없어서 못 바꾼 것"과 "권한이
   있어도 안 바꾸는 것"을 구분할 수 있다.
5. 이번 판정(B)은 Risk Component를 만들 근거로 쓰지 않는다 —
   Architecture Freeze Review는 위 선행조건들이 쌓인 뒤 별도
   문서에서 판단한다.

---

## Self Review

- Risk Architecture나 Contract를 설계했는가 — **아니오**(§11, 요구
  사항만 기록, 필드명 미확정).
- "Risk라는 개념이 존재한다 → Risk Component가 필요하다"는 논리를
  썼는가 — **아니오**(§12 — Input→판단→Output→다른 판단에의 영향을
  실제 Evidence로 제시, 그리고 그 Evidence가 "완전히 강하지는
  않다"는 것도 정직하게 기록해 B로 낮춤).
- 새로운 시장 데이터를 생성했는가 — **아니오**(Portfolio State
  전부 재사용).
- 방법론 실수(합산 금지 규칙 누락)를 숨겼는가 — **아니오**(§0,
  §12에서 명시적으로 한계로 기록하고 확증 Evidence로 취급하지
  않음).
- `hqs/investment/`, Structure v1.0, RFC/ADC/ADR, Phase 7을
  수정했는가 — **아니오**(`git diff --stat hqs/investment/` 빈
  결과로 재확인).
