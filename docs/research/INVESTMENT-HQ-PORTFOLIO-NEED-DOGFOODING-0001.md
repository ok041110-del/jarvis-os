# INVESTMENT-HQ-PORTFOLIO-NEED-DOGFOODING-0001

**문서 성격**: Experimental Dogfooding Evidence 문서. **Portfolio
Architecture/Contract 설계가 아니다.** RFC/ADC/ADR을 생성하지 않고,
`hqs/investment/`·Structure v1.0·Architecture Baseline·Phase 7 상태를
수정하지 않는다(`git diff --stat hqs/investment/` 빈 결과로 재확인).
`Portfolio`/`Portfolio Manager`/`Portfolio Decision`이라는 이름도
확정하지 않는다 — 이 문서 전체에서 "Portfolio-level 책임"이라는
중립적 표현을 쓴다.

**핵심 결론**: 판정 A. PORTFOLIO NEED VALIDATED(조건부) — 집중도 +
정책 부재 + 자산군 간 상관관계가 함께 성립할 때만 필요하다(Negative
Control로 확인). QQQ의 실제 공시 보유 종목이 직접 보유 Stock 포지션과
겹치는 사례가 핵심 근거였다.

**방법론**: 격리된 `projects/synthesis-trader-expansion-prototype/
portfolio_prototype.py`(신규 파일)로 **실제 Engine 호출 4회**를
수행했다 — 기존 실제 Trader Decision(`results/*_trader_expanded.md`,
이전 두 Dogfooding 문서에서 이미 생성된 것)을 입력으로 재사용하고,
**가상의 Portfolio State**(실제 계좌 데이터가 아님, 이 실험을 위해
명시적으로 표시된 설정값)를 추가해 STEP1~3을 검증했다. 새로운
시장/종목 데이터는 생성하지 않았다 — QQQ의 "NVDA~8.5%, AAPL~7.1%"
같은 수치도 기존 `bull_case.md`에 이미 존재하던 실제 산출물을
그대로 인용했을 뿐이다.

---

## 1. 사용한 실제 Dogfooding 사례

| 실험 | 사용한 실제 Trader Decision | Team 구성 |
|---|---|---|
| STEP2 (단일 자산) | AAPL(HOLD) | Stock |
| STEP2 negative control | CAT(HOLD) | Stock |
| STEP3 (Cross-Team, 중복 노출) | AAPL(HOLD) + NVDA(HOLD) + QQQ(HOLD) | Stock ×2 + ETF |
| STEP3b (Cross-Team, 동일 위험군) | PG(HOLD) + JNJ(HOLD) | Dividend Stock ×2 |

Stock/Dividend Stock/ETF 3개 Team 전부 포함(사용자 지시 §3 준수).
전부 이전 두 Dogfooding 문서에서 이미 실제 Engine 호출로 생성된
Trader Decision을 재사용했다 — 이번 세션에서 Trader Decision을 다시
만들지 않았다. 전부 HOLD 사례이며, 사용자 지시(§3)대로 그대로
사용했다(BUY/SELL discrimination은 이번 범위가 아님).

---

## 2. STEP1 — Trader Decision만으로 가능한 판단

이전 세 Dogfooding 문서(Trader Need/Revalidation/Boundary/Discrimination)
에서 이미 반복 확인된 사실을 재확인한다: 6개 Trader Decision 전부
"no portfolio context... was provided or assumed"를 스스로 명시했다
— **position size/allocation 판단은 STEP1 단계(Trader Decision만)
에서 원천적으로 불가능**하다는 것이 이번에도 자명하게 재확인됐다.
이번 실험은 여기서 멈추지 않고 STEP2/3로 실제로 Portfolio State를
추가해 무엇이 달라지는지 확인했다.

---

## 3. STEP2 — Portfolio State 추가 후 변화

### 3-1. AAPL(15% 비중, 정책 없음)

실제 응답(발췌): *"15% single-name concentration in AAPL — sitting
on top of unresolved directional uncertainty — [is this] an
appropriate amount of risk to be carrying right now? That's not
answerable by a fixed calculation... there's no stated policy to
apply... Someone has to judge whether a HOLD rationale... justifies
leaving a top-3 position at its current weight."*

**판정: Case C**(§5 기준) — 계산도 정책도 아닌 새로운 판단.

### 3-2. CAT(2% 비중, 명시적 정책 "최대 5%" 있음) — Negative Control

실제 응답(발췌): *"there is no position-size or allocation judgment
to make here at all, because the Decision is HOLD... If the Decision
had instead been BUY, sizing would only need (a) a simple calculation
... pure arithmetic against a configured cap... there is no (c) new
judgment required, since nothing here... forces a discretionary call
the stated policy and math can't resolve on their own."*

**판정: Case A**(§5 기준) — 순수 계산, 심지어 이번 사례는 HOLD라
계산조차 발동하지 않음.

**핵심 발견**: 동일한 질문 형식, 동일한 프롬프트 구조로 두 사례를
테스트했는데 **정반대 답**이 나왔다 — 이는 "무조건 Portfolio 판단이
필요하다고 답하는 편향"이 아니라, **입력(포지션 비중, 정책 존재
여부)에 따라 실제로 다르게 판단한다**는 것을 보여주는 negative
control이다(§9에서 신뢰도 평가에 활용).

---

## 4. STEP3 — Multiple Team Decision 통합 결과

### 4-1. AAPL + NVDA + QQQ(Stock ×2 + ETF, 실제 중복 노출)

**입력 근거(실제 데이터, 신규 생성 아님)**: QQQ의 기존 `bull_case.md`
가 이미 "NVIDIA ~8.5–8.9%, Apple ~7.1–7.3%"를 QQQ의 실제 보유
종목으로 명시하고 있었다 — 즉 가상 Portfolio State가 "AAPL/NVDA를
개별 보유 + QQQ도 보유"로 설정한 순간, **QQQ 안에 이미 AAPL/NVDA가
포함돼 있다는 것은 가상이 아니라 기존 실제 산출물의 사실**이다.

실제 응답(발췌): *"AAPL (15%) and NVDA (12%) are each
individually-sized positions, but QQQ (18%) itself holds both AAPL
and NVDA as top constituents. None of the three Decisions could see
this, because each was produced 'in isolation, per-security, with no
knowledge of each other.'... Summed, the account's effective exposure
to AAPL and to large-cap tech/AI names is materially higher than the
15%/12%/18% headline numbers suggest — this is a fact only visible by
looking at all three Decisions plus the portfolio state together."*

추가로 "Reassess when" 조건 세 개(AAPL: Services 추세, NVDA: China
라이선스, QQQ: Fed 경로)가 **서로 독립이 아니라 상관될 수 있다**는
점도 지적했다 — AAPL/NVDA의 실적 충격이 QQQ 수익률에도 영향을
주므로, 세 재평가 조건이 동시에 촉발될 위험이 개별 Decision에서는
보이지 않는다는 것이다.

**판정: Case C**(강함) — 실제 look-through 노출 계산 자체가 불가능
(QQQ의 정확한 AAPL/NVDA 지분 가중치가 주어지지 않음)했고, 정책도
없었으며, **세 Decision을 종합해야만 보이는 사실**이었다.

### 4-2. PG + JNJ(Dividend Stock ×2, 표면적으로는 무관)

이 조합은 사전에 "중복 노출이 없을 것"으로 예상하고 설계한
대조군에 가까웠으나, 실제 응답은 예상 밖의 결과를 냈다.

실제 응답(발췌): *"PG: whether the ~$1B commodity/tariff/energy
headwind is already absorbed into FY2027 guidance. JNJ: whether the
$5.5B talc settlement... is already reserved for versus an
incremental future charge... both 'dividend-safety' positions...
are both sitting on unresolved downside catalysts that could land in
the same window (FY2027)... If both unresolved items resolve
unfavorably around the same period, the portfolio's dividend-sleeve
exposure moves together rather than independently."*

**판정: Case C**(중간 강도) — 종목 자체는 무관하지만(다른 업종),
**두 Decision의 "재평가 조건"이 같은 시기(FY2027)에 수렴한다는
상관관계**를 발견했다. 이는 사용자가 예시로 든 "동일 Sector 노출"
보다는 미묘하지만, "여러 자산의 Decision을 종합해야 보이는 사실"
이라는 핵심 조건(§5 C)은 동일하게 충족한다.

---

## 5. Calculation / Policy / Portfolio Decision 구분

| 사례 | 분류(§5 A~D) | 근거 |
|---|---|---|
| CAT(2%, 정책 있음) | **A. Calculation Need**(사실상 미발동, HOLD라 계산 자체가 필요 없음) | 명시적 정책 + 낮은 비중 + 상관관계 없음 → 산술만으로 충분하다고 모델 스스로 판단 |
| AAPL(15%, 정책 없음) | **C. Portfolio Decision Need** | 계산식도 정책도 없고, "이 정도 집중도가 이 불확실성 수준에서 감내할 만한가"라는 판단이 필요 |
| AAPL+NVDA+QQQ(중복 노출) | **C. Portfolio Decision Need**(가장 강함) | look-through 노출이 세 Decision을 종합해야만 드러남, 계산 불가능(가중치 미제공), 정책 없음 |
| PG+JNJ(시점 상관) | **C. Portfolio Decision Need** | 종목 자체 무관하지만 재평가 조건의 시점 상관관계가 종합해야 보임 |

**Risk와의 경계(§7 D 카테고리)**: AAPL 단독 응답이 "risk to be
carrying"라는 표현을 썼다는 점은 주의할 필요가 있다 — 이는 "얼마나
보유할까"(Portfolio 질문)와 "이 위험 수준이 감당 가능한가"(Risk
질문)의 **경계가 실제 응답에서 이미 흐려지기 시작했다**는 것을
보여준다. 이번 문서는 이 흐려짐을 **관찰로만 기록**하고 Risk
Architecture로 확장하지 않는다(사용자 지시 §7 준수) — Portfolio와
Risk의 정확한 경계는 별도 Dogfooding 대상으로 남긴다(§12).

---

## 6. Portfolio Need 반복성

4개 실험(STEP2 ×2, STEP3 ×2) 중 **3개에서 Case C가 관찰**됐다(AAPL
단독, AAPL+NVDA+QQQ, PG+JNJ) — 나머지 1개(CAT)는 Case A로 정확히
구분됐다. 이는 "항상 Yes로 답하는 편향"이 아니라 **조건부로 발동하는
패턴**이라는 것이 negative control(§3-2)로 뒷받침된다. 3/4라는
반복 수는 아직 많지 않지만, 서로 다른 성격의 3개 시나리오(단일
고비중 자산, 명시적 종목 중복, 비종목적 시점 상관)에서 **매번 다른
구체적 이유로** Case C가 나왔다는 점이 우연이 아님을 시사한다.

---

## 7. Cross-Team Portfolio Need

사용자 지시(§6)의 단계적 질문에 실제 근거로 답한다:

- **Stock Team 결과만 사용했을 때 Portfolio 판단이 필요한가**: 예
  — AAPL 단독(§3-1)에서도 Case C가 나왔다(단, Cross-Team이 아니라
  Single-Team/Single-Asset 수준의 필요성).
- **Stock + ETF를 함께 고려해야 하는가**: **예, 그리고 이것이 가장
  강한 Evidence다**(§4-1) — QQQ(ETF Team)가 AAPL/NVDA(Stock Team)를
  내부에 이미 포함하고 있다는 사실은 **Team 경계를 넘어야만 보이는
  구조적 사실**이다. Stock Team의 Trader도, ETF Team의 Trader도
  이 사실을 알 방법이 없다(각자 자기 Team의 종목만 본다, 코드
  구조상으로도 확인됨 — `run.py`가 Team을 하나씩 독립 실행).
- **Stock + Dividend Stock을 함께 고려해야 하는가**: **예**(§4-2)
  — 종목 자체의 업종 중복은 없었지만 재평가 조건의 시점 상관관계가
  발견됐다.

**결론**: Portfolio-level 책임은 **단일 Team 내부에서도 일부
발생**(AAPL 단독 사례)하지만, **Team 경계를 넘을 때 가장 강하고
명확한 형태로 나타난다**(QQQ의 실제 보유 종목 중복) — 이는
Cross-Team/Shared 성격의 책임 후보로 볼 근거가 된다.

---

## 8. Risk와 Portfolio 책임 경계

사용자 지시(§7)대로 Portfolio와 Risk를 하나로 묶지 않고 관찰한다.

- 이번 4개 실험에서 나온 응답은 전부 **"무엇을 보유할지/얼마나
  보유할지"**(Portfolio 질문)에 답하려 했다.
- 그러나 AAPL 단독 응답이 위험 감내 여부("risk to be carrying")를
  언급한 것(§5)은, Portfolio 판단이 실제로는 **Risk 판단과 완전히
  분리되지 않고 맞닿아 있을 가능성**을 시사한다 — "이 비중이
  적절한가"를 판단하려면 결국 "이 비중이 만드는 위험이 감당
  가능한가"를 어느 정도 전제해야 하기 때문으로 보인다.
- **이번 문서는 이 경계를 확정하지 않는다.** Risk가 필요하지 않다고
  단정하지도, Portfolio를 Risk까지 확장하지도 않는다 — 관찰만
  기록하고(§12 선행조건으로 이관).

---

## 9. Portfolio Contract 후보 Evidence(확정 아님)

사용자 지시(§9)대로 Schema/필드명을 확정하지 않는다. 반복 관찰된
**정보 요구사항**만 기록한다:

| 관찰된 정보 요구 | 근거 |
|---|---|
| 현재 보유 비중(포지션 크기) | 4/4 실험 전부에서 판단의 출발점으로 쓰임 |
| 종목 간/자산 간 look-through 노출 관계 | §4-1 — QQQ 사례에서 결정적 |
| 재평가 조건(reassessment trigger) 간의 상관관계 | §4-1, §4-2 — 두 STEP3 실험 모두에서 독립적으로 관찰됨(반복) |
| 정책 존재 여부(포지션 상한 등) | §3 negative control에서 판단을 완전히 바꾼 핵심 변수 |

이 중 "재평가 조건 간 상관관계"는 이전 Dogfooding 문서들이 이미
Team-level에서 A로 분류한 `reassessment_trigger`(Synthesis 산출물
재사용 가능성)와 자연스럽게 연결된다 — Team-level에서 만들어지는
정보가 Portfolio-level에서 **다시 한번, 다른 방식으로**(개별
트리거가 아니라 트리거 간의 상관관계로) 쓰일 수 있다는 것을 보여준다.
필드로 확정하지 않는다.

---

## 10. Architecture Need 여부

- 별도의 **책임**(누가 이 판단을 하는가)이 실제로 관찰됐다 — 4개
  실험 중 3개에서, Team-level Trader가 접근할 수 없는 정보(다른
  Team의 보유 종목, 다른 자산의 재평가 조건)를 종합해야만 하는
  판단이 나왔다.
- 그러나 이 책임이 **별도 Kernel Component**여야 하는지, **HQ
  내부의 얇은 종합 단계**로 충분한지는 이번 실험이 답하지 않는다
  — 이는 Architecture 설계 질문이며 이번 범위 밖이다(사용자 지시
  §9·§10 준수).
- CAT 사례(Case A)가 보여주듯, **모든 경우에 이 책임이 필요한 것은
  아니다** — 정책이 있고 집중도가 낮으면 단순 계산으로 충분하다.
  이는 향후 설계 시 "항상 Portfolio 판단을 거쳐야 한다"가 아니라
  "조건부로 필요하다"는 형태의 Architecture를 시사한다(설계는
  하지 않음, 관찰만 기록).

---

## 11. 최종 판정

## **A. PORTFOLIO NEED VALIDATED**(조건부)

**판정 이유**:

- Trader Decision만으로 Portfolio 판단이 불가능함 — §2에서 재확인
  (6/6 Decision이 스스로 이를 명시).
- Portfolio State가 실제 판단에 영향을 줌 — §3에서 실증(CAT vs
  AAPL의 정반대 결과).
- 여러 자산/Team의 결과를 종합해야 하는 실제 사례가 존재함 — §4-1
  (QQQ의 실제 보유 종목과 개별 포지션의 중복, 신규 데이터 생성
  없이 기존 실제 산출물만으로 발견).
- 단순 계산/Configuration만으로 설명되지 않는 사례가 반복 관찰됨 —
  §4-1, §4-2(서로 다른 두 시나리오에서 각각 다른 이유로 Case C).
- 새로운 Portfolio-level 판단 책임이 반복 확인됨 — 4개 실험 중
  3개(§6).

**"VALIDATED"에 붙는 조건**: 이 Need는 **보편적이지 않고 조건부**다
— CAT처럼 집중도가 낮고 정책이 있으면 Case A(계산)로 충분하다는
것이 negative control로 명확히 구분됐다(§3-2, §6). 따라서 "Portfolio
책임이 항상 필요하다"가 아니라 **"포지션 집중도·자산 간 중복·정책
부재라는 조건이 성립할 때 Portfolio-level의 새로운 판단이 필요하다"**
는 조건부 형태로 VALIDATED됐다.

**B로 낮추지 않는 이유**: B("단순 Policy/Calculation으로 해결
가능성이 있음")는 이번 실험에서 오히려 **명확히 배제된 사례들이
있다**(§4-1의 look-through 노출은 정책만으로 해결 불가능 — 계산할
가중치 자체가 주어지지 않는다). CAT는 실제로 B/A에 해당하지만, 이는
"항상 그렇다"가 아니라 "조건에 따라 그럴 수도 있다"는 뜻이므로
전체 판정을 B로 낮출 근거는 아니다.

**C로 판정하지 않는 이유**: 기존 Architecture(Team-level Trader +
정책 설정)만으로 §4-1의 look-through 노출 문제를 풀 수 있다는
근거가 없다 — 오히려 실제 응답이 "이건 어느 개별 Decision도 볼 수
없는 사실"이라고 명시적으로 이유를 댔다.

**D로 판정하지 않는 이유**: n=4로 많지 않지만, 관찰 방법 자체는
negative control까지 포함해 판단 근거를 명확히 구분해냈다(§3) —
"방법으로 판단할 수 없다"는 근거가 아니라 오히려 방법이 잘 작동한
사례다.

---

## 12. 다음 선행조건

1. **반복 횟수 확대** — 이번 실험은 n=4(1 negative + 3 positive)다.
   Case C가 나온 3개 시나리오 성격이 서로 달라(단일 고비중, 명시적
   종목 중복, 비종목적 시점 상관) 우연이 아닐 가능성이 높지만,
   같은 유형(특히 §4-1의 ETF look-through 유형)을 다른 ETF/종목
   조합으로 최소 1~2회 더 재현해야 한다.
2. **Risk/Portfolio 경계를 별도 Dogfooding으로 분리 검증** — §8에서
   발견한 흐려짐("risk to be carrying")이 실제 응답 패턴에서
   반복되는지, 아니면 이번 1건의 우연인지 확인해야 한다. Risk
   Architecture를 설계하지 않은 채로 이 경계만 별도로 관찰하는
   Dogfooding이 필요하다.
3. **BUY/SELL 사례가 발생하면 재검증** — 이번 실험은 전부 HOLD
   Decision을 썼다(사용자 지시 준수). 이전 Discrimination Dogfooding
   문서의 결론(D. UNTESTABLE, BUY/SELL 사례 없음)이 해소되면, 실제
   BUY 상황에서 Position Size 판단이 CAT의 negative control처럼
   "정책만으로 충분"한지, AAPL처럼 "새 판단이 필요"한지 다시
   확인해야 한다 — HOLD에서는 애초에 sizing이 발동하지 않는
   경우(§3-2)가 있어 완전한 검증이 아니었다.
4. **"조건부 발동"의 조건 자체를 더 구체화** — 이번 실험은 "집중도
   +정책 부재+상관관계"가 Case C를 유발한다는 가설을 세웠지만,
   이를 정밀하게 검증(예: 정책이 있어도 집중도가 매우 높으면
   여전히 Case C인지, 낮은 집중도라도 상관관계가 극단적이면 Case C
   인지)하지 않았다.
5. 이번 판정(A, 조건부)은 Portfolio Architecture 설계를 허가하는
   것이 아니다 — Architecture Freeze Review는 위 선행조건들과 별도
   문서에서 판단한다.

---

## Self Review

- Portfolio Architecture나 Contract를 설계했는가 — **아니오**(§9,
  정보 요구사항만 기록, Schema/필드명 미확정).
- `Portfolio`/`Portfolio Manager`/`Portfolio Decision`이라는 이름을
  확정했는가 — **아니오**(중립적 "Portfolio-level 책임" 표현 사용).
- Risk Architecture를 설계했는가 — **아니오**(§8, 경계 흐려짐을
  관찰만 하고 확장하지 않음).
- 새로운 시장/종목 데이터를 생성했는가 — **아니오**(QQQ 보유
  종목 비중은 기존 실제 산출물 인용, Portfolio State만 가상으로
  표시해 추가).
- `hqs/investment/`, Structure v1.0, RFC/ADC/ADR, Phase 7을
  수정했는가 — **아니오**(`git diff --stat hqs/investment/` 빈
  결과로 재확인).
- 결과를 사후 수정하거나 원하는 답이 나올 때까지 반복 실행했는가 —
  **아니오**(각 실험 1회씩, negative control은 사전에 "Case A가
  나와야 정상"이라는 가설을 세우고 검증 목적으로 설계함).
