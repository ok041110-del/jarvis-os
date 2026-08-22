# INVESTMENT-HQ-ETF-LOOKTHROUGH-EXPOSURE-DOGFOODING-0001

**문서 성격**: Experimental Dogfooding Evidence 문서. **Portfolio/
Exposure Architecture나 Contract를 설계·확정하지 않는다.** RFC/ADC/
ADR을 생성하지 않고, `hqs/investment/`·Structure v1.0·Architecture
Baseline·Phase 7 상태를 수정하지 않는다(`git diff --stat hqs/
investment/` 빈 결과로 확인). `Exposure schema`/`DirectExposure`/
`IndirectExposure`/`LookThroughExposure` 등 어떤 이름도 Contract로
확정하지 않는다.

**방법론**: 격리된 `projects/synthesis-trader-expansion-prototype/
lookthrough_prototype.py`(신규 파일)로 **실제 Engine 호출 4회**를
수행했다. 새로운 시장/종목/구성종목 데이터는 만들지 않았다 — ETF
구성비중은 전부 기존 실제 ETF Team 산출물(`bull_case.md` 등)에서
그대로 인용했다. Portfolio State(직접 보유 여부)만 이 실험을 위한
가상 설정값이며, 매 프롬프트에 "합산 금지" 규칙을 명시적으로
포함시켜 사용자의 핵심 원칙(§1)을 강제했다.

---

## 1. 사용한 실제 ETF 사례

| ETF | 유형 | 실제 근거 산출물 | 이번 사례 구분 |
|---|---|---|---|
| **QQQ** | Broad Market/Index(Nasdaq-100) | `projects/etf-analysis-qqq/.../bull_case.md`(기존, Portfolio Need Dogfooding에서 이미 확인) | Case C(직접+ETF 중복), Case B(ETF만) 둘 다에 사용 |
| **GLD** | Commodity(실물 금, 비주식) | `projects/etf-analysis-gld/.../bull_case.md`(신규 확인) | Case A(구조적으로 look-through 불가능) |
| **SCHD** | Sector/Dividend Thematic | `projects/etf-analysis-schd/.../bull_case.md`(신규 확인) | Case B 변형(구성종목 존재하나 중복 없음) |

**사전 조사**: 사용자 지시(§3)대로 저장소의 모든 ETF 사례
(QQQ/SCHD/AGG/GLD/VNQ/UUP)의 `bull_case.md`를 확인해 각 ETF의 실제
공개 구성종목을 대조했다. 결과:

- **QQQ**: AAPL(~7.1–7.3%), NVDA(~8.5–8.9%) 등 — 기존 Stock Team이
  이미 분석한 종목과 **실제로 겹침**(Portfolio Need Dogfooding에서
  확인한 사실 재확인).
- **VNQ**: Welltower/Prologis/Equinix/American Tower/Digital Realty
  — 기존 Dividend Stock Team 사례(Realty Income 등)와 **겹치지
  않음**(직접 대조 확인, Digital Realty ≠ Realty Income, 서로 다른
  회사).
- **SCHD**: Abbott Laboratories/UnitedHealth/Merck(2026년 3월
  리밸런싱 후) — 기존 Dividend Stock Team 사례(JNJ/KO/PG 등)와
  **겹치지 않음**(직접 대조 확인).
- **GLD/AGG/UUP**: 각각 실물 금/채권/통화 선물 — **주식 구성종목
  자체가 없음**(비주식 자산군, look-through 대상 자체가 성립하지
  않음).

이 사전 조사 자체가 §7의 A/B/C Negative Control 요구를 **인위적
설계 없이 실제 저장소 데이터로 자연스럽게 충족**시켰다 — QQQ가
Case C, SCHD/VNQ가 Case B, GLD/AGG/UUP가 Case A에 해당하는 실제
사례로 이미 존재했다.

---

## 2. ETF별 Exposure Tree

**QQQ**(실제 데이터, `bull_case.md`):
```
QQQ
├── AAPL          ~7.1–7.3%
├── NVDA          ~8.5–8.9%
└── Top-5 합계     ~30–33%(개별 종목 미분해)
```

**SCHD**(실제 데이터, `bull_case.md`):
```
SCHD (103개 종목, 최대 단일 비중 4.42%)
├── Abbott Laboratories   (2026-03 리밸런싱 후 상위)
├── UnitedHealth          (상위)
├── Merck                 (상위, 리밸런싱 전후 불변)
└── JNJ                   불명(상위 목록에 없음, 정확한 비중 데이터 자체가 없음)
```

**GLD**(실제 데이터, `bull_case.md`):
```
GLD
└── 실물 금 현물(grantor trust)  100%
    (파생상품/선물/채권/주식 없음)
```

---

## 3. Direct / Indirect Exposure Path(실제 산출, 합산 없음)

Engine이 실제로 산출한 결과를 그대로 옮긴다(수치 재계산 없음):

**Case C(QQQ + 직접 AAPL/NVDA)**:
```
Direct  → AAPL                          10%
Direct  → NVDA                          10%
ETF     → QQQ                           10%
Indirect(QQQ) → AAPL   10%×~7.1–7.3% ≈ ~0.71–0.73%
Indirect(QQQ) → NVDA   10%×~8.5–8.9% ≈ ~0.85–0.89%
Indirect(QQQ) → Top-5  10%×~30–33%  ≈ ~3.0–3.3%
```
**6개 독립 라인, 어디에도 "AAPL 총 10.71%" 같은 합산이 없음**(직접
출력 재확인) — AAPL/NVDA 각각 Direct 라인과 Indirect 라인을 **분리
유지**했다.

**Case B(QQQ만 보유)**:
```
Direct → QQQ                            10%
Indirect(QQQ) → AAPL   ~7.1–7.3%(QQQ 자산 대비, 포트폴리오 대비 값 미산출)
Indirect(QQQ) → NVDA   ~8.5–8.9%(QQQ 자산 대비, 포트폴리오 대비 값 미산출)
Indirect(QQQ) → Top-5  ~30–33%(QQQ 자산 대비)
```
**흥미로운 자기 절제**: 이번엔 Engine이 스스로 "QQQ 대비 비중을
포트폴리오 대비 비중으로 환산하는 것 자체가 금지된 합산과 같은
성격"이라고 판단해 **환산조차 하지 않았다** — Case C에서는 (Direct
보유가 있어 대조가 필요했으므로) 환산했지만, Case B에서는 환산할
필요가 없다고 판단해 원 단위(QQQ 자산 대비)를 그대로 유지했다.

**Case A(GLD)**:
```
Direct  → (없음)
ETF     → GLD                           10%
Indirect(GLD) → 실물 금                  100%(GLD 자산 대비)
```

**Case B 변형(SCHD, JNJ 직접 보유 + SCHD 보유, 중복 없음)**:
```
Direct  → JNJ                           8%
ETF     → SCHD                          10%
Indirect(SCHD) → JNJ    산출 불가(구성종목 목록에 JNJ 없음, 추정 거부)
```
**중요한 발견**: Engine이 "SCHD→JNJ 노출이 0%"라고 **임의로 채우지
않고**, "데이터에 없다 = 0%가 아니다"라며 **산출 불가 상태를 그대로
보존**했다 — 이는 사용자가 우려한 "숫자가 없으면 대충 채워 넣는"
실패 모드가 발생하지 않았다는 근거다.

---

## 4. 각 Exposure의 독립 수치(§3에서 이미 제시, 요약)

4개 사례 전부에서 **합산 위반이 0건**이었다(수작업으로 전수 재확인
— "Total", "combined %", "AAPL 총" 같은 표현이 어디에도 등장하지
않음). Case B에서는 오히려 **모델 스스로 단위(포트폴리오 대비 vs
ETF 자산 대비) 혼동 가능성까지 지적**하며 Direct/Indirect 라인을
같은 척도로 나열하는 것조차 "오독의 위험이 있다"고 명시했다 — 이는
사용자가 §1에서 요구한 원칙보다 한 단계 더 엄격하게 지켜진 사례다.

---

## 5. Negative Control 결과

| Case | 예상(사용자 §7 정의) | 실제 결과 |
|---|---|---|
| **A**(GLD, 직접 보유 없음+ETF도 비주식) | Look-through 문제 없음 | **일치** — "No — Data Join case", 유일하게 4개 중 판단 불필요로 나온 사례 |
| **B**(QQQ만 보유, AAPL/NVDA 직접 보유 없음) | ETF 내부 구성은 있으나 직접/간접 중복은 없음 | **부분 일치, 그러나 예상 밖 발견** — "중복은 없지만" 단위 혼동 위험과 정책 부재로 여전히 판단 필요(Case C에 가까운 결론) — §7 원 정의가 암시한 것보다 판단 Need가 더 넓게 나타남 |
| **C**(직접 AAPL/NVDA + QQQ 중복) | Direct/Indirect Path 중복 발생 | **일치** — 중복 자체를 "correlation risk" 판단 필요 근거로 명시 |

**Case A가 유일하게 "판단 불필요"로 나왔다는 것 자체가 핵심
Negative Control**이다 — 이는 "ETF를 보면 무조건 Portfolio 판단이
필요하다"는 편향이 아니라, **비주식 ETF(구성종목 자체가 없음)에서는
정확히 판단이 불필요하다고 구분**했다는 뜻이다. 4개 중 3개(B, B2,
C)에서 판단이 필요하다고 나온 것은 편향이 아니라, **이 3개 모두
실제로 "주식 구성종목이 존재하는 ETF"였기 때문**이라는 것이
Case A와의 대조로 뒷받침된다.

---

## 6. Stock Team / ETF Team Boundary

코드 재확인(`hqs/investment/run.py`, `teams/{stock,etf}_team.py`):
Team은 `run.py`에서 **하나씩 독립 실행**되며, Team 간 공유 State나
서로의 존재를 참조하는 코드가 없다(리터럴 딕셔너리 `TEAMS`로 선택될
뿐).

- **Q1(Stock Team이 QQQ 보유 여부를 몰라도 되는가)**: **예, 문제
  없다.** AAPL 분석(Fundamental/Technical/... /Bull/Bear/Synthesis)
  은 QQQ의 존재와 무관하게 완결된다 — 실제로 AAPL Trader Decision
  (이전 Dogfooding 문서에서 생성)은 QQQ를 전혀 언급하지 않고도
  유효했다.
- **Q2(ETF Team이 Portfolio의 AAPL 직접 보유 여부를 몰라도 되는가)**:
  **예, 문제 없다.** QQQ 분석도 동일한 방식으로 완결된다.
- **문제가 발생하는 지점**: Q1·Q2 각각은 문제가 아니지만, **이
  둘을 "동시에" 알아야 하는 시점(Portfolio-level)에서만 문제가
  발생한다**(§3 Case C) — 이는 사용자가 §8에서 예상한 구조와
  정확히 일치한다.

---

## 7. Data Join vs Portfolio Decision

| Case | Data Join으로 충분한가 | 판정 |
|---|---|---|
| A(GLD) | **예** | Data Join(§9 A) |
| B(QQQ만) | 아니오 — 단위 혼동 위험 + 정책 부재 | Portfolio Decision(§9 B) |
| B2(SCHD, 중복 없음) | 아니오 — 데이터 결측 처리 판단 + 정책 부재 | Portfolio Decision(§9 B) |
| C(QQQ+직접 중복) | 아니오 — 상관관계 인식 + 중요도 판단 | Portfolio Decision(§9 B) |

**핵심 발견**: 사용자가 §9에서 예상한 구도(A=Data Join만 필요,
B=Portfolio Decision 필요)와 달리, **실제로는 "중복이 없어도"(Case
B, B2) 여전히 Portfolio Decision이 필요하다는 결과가 나왔다.** 그
이유는 중복 자체가 아니라 **(1) 서로 다른 단위/분모를 가진 수치를
나란히 놓을 때 발생하는 오독 위험**과 **(2) 결측 데이터를 0으로
채우지 않고 어떻게 표시할지 결정하는 것** — 이 두 가지가 "구성종목
데이터 존재" 자체에서 이미 발생하는 판단이었다. 즉 판단 Need의
**원인이 사용자의 원래 가설(직접/간접 중복)보다 한 단계 더
근본적인 곳**(서로 다른 척도의 데이터를 다루는 것 자체)에 있다는
것이 이번 조사의 가장 중요한 수정 사항이다.

---

## 8. Cross-Team Need

- Case C(QQQ+AAPL+NVDA)는 Stock Team(AAPL, NVDA)과 ETF Team(QQQ)의
  결과를 **동시에** 참조해야만 나오는 판단이었다 — 이는 이전
  Portfolio Need Dogfooding 문서에서 이미 확인한 것을 "합산 금지"
  원칙 아래서 다시 확인한 것이다.
- Case B(QQQ만)와 Case B2(SCHD, JNJ 직접 보유)도 **Cross-Team**
  성격이다 — Case B는 ETF Team(QQQ) 결과 하나만으로도 판단이
  필요했다는 점에서, Cross-Team Need가 "여러 Team의 결과가 충돌할
  때"뿐 아니라 **"ETF Team의 결과 하나만 있어도, 그 안에 담긴
  구성종목 정보의 척도 자체가 Portfolio 레벨에서 다뤄져야 한다"**는
  더 넓은 형태로도 나타난다는 것을 보여준다.

---

## 9. Portfolio / Risk Boundary

사용자 지시(§10)대로 Risk Architecture를 설계하지 않고 관찰만
기록한다.

- Case C 응답의 "correlation risk"·"risk-materiality judgment" 표현,
  Case B/B2 응답의 "정책이 없어 acceptable 여부를 판단할 근거가
  없다"는 표현 — 4개 중 3개 응답 전부가 **"Exposure Path를 어떻게
  관리할 것인가"(Portfolio)와 "그 결과가 위험한가"(Risk)의 경계에서
  자연스럽게 Risk 쪽 언어를 끌어왔다.**
- 이는 이전 Portfolio Need Dogfooding 문서(§8)에서 이미 관찰한
  "경계 흐려짐"이 이번에도 **3/4로 반복**됐다는 뜻이다 — 우연이
  아닐 가능성이 높아졌다.
- **여전히 확정하지 않는다**: 이 문서도 Risk Architecture를 설계하지
  않고, 이 반복 관찰만 별도 선행조건(§12)으로 이관한다.

---

## 10. Contract 후보 Evidence(확정 아님)

사용자 지시(§11)대로 Schema/필드명을 확정하지 않는다. 반복 관찰된
**정보/처리 요구사항**만 기록한다:

| 관찰된 요구사항 | 근거 |
|---|---|
| Direct Path와 Indirect Path를 별도 라인으로 유지하는 표현 방식 | 4/4 전부에서 성공적으로 유지됨(합산 위반 0건) |
| Indirect Path의 분모(ETF 자산 대비 vs 포트폴리오 대비)를 구분 표시 | Case B에서 발견 — 반복 확인 필요(n=1) |
| 구성종목 데이터 결측을 0이 아닌 "산출 불가"로 유지 | Case B2에서 발견 — 반복 확인 필요(n=1) |
| 정책(포지션 상한 등) 부재 시 "판단 불가"를 명시적으로 표시 | 3/4(B, B2, C)에서 공통 관찰 |

이 중 어느 것도 필드명(`IndirectExposure` 등)으로 확정하지 않는다
— "이런 정보/처리가 반복적으로 필요했다"는 사실만 기록한다.

---

## 11. 최종 판정

## **A. LOOK-THROUGH PORTFOLIO NEED VALIDATED**(조건부, §11 하위 발견 포함)

**판정 이유**:

- 여러 실제 사례(QQQ 2개 시나리오 + SCHD 1개 + GLD 1개, 서로 다른
  ETF 유형 3종)에서 반복됨 — §1·§5.
- Direct/Indirect Exposure Path가 동시에 존재하는 사례(Case C)와,
  Indirect Path만 있어도 판단이 필요한 사례(Case B, B2)가 둘 다
  실제로 관찰됨 — §3·§7.
- 단순 Data Join으로 끝나지 않음 — 4개 중 3개(§7).
- 실제 Portfolio-level 판단이 반복 필요함 — §7, 매번 다른 구체적
  이유(상관관계 인식, 단위 혼동 위험, 결측 처리)로 나타나 정형화된
  응답이 아님을 뒷받침.
- Cross-Team 책임 경계가 명확함 — §6·§8(코드 구조로도 확인).

**조건**: Case A(GLD, 비주식 ETF)에서는 이 Need가 **발동하지
않는다** — "ETF라면 무조건 Portfolio 판단이 필요하다"가 아니라,
**"ETF가 개별 주식 구성종목을 가질 때"라는 조건이 성립해야 발동**
한다. 이는 이전 Portfolio Need Dogfooding 문서의 "조건부 VALIDATED"
와 같은 성격이다.

**수정 사항(중요)**: 사용자의 원래 가설(§7 A/B/C 구도, "중복이
있어야 판단이 필요하다")은 **부분적으로 반박됐다** — Case B(중복
없음)도 실제로는 판단이 필요했다. 판단 Need의 진짜 원인은 "중복"
보다 **"서로 다른 척도/분모를 가진 정보를 Portfolio 레벨에서
다루는 것 자체"**에 더 가깝다는 것이 이번 조사의 핵심 수정이다.

---

## 12. 다음 선행조건

1. **Case B의 "단위 혼동" 발견을 다른 ETF로 재현** — 이번엔 QQQ
   1건에서만 나왔다(n=1). VNQ 등 다른 지수/섹터 ETF로 동일 패턴이
   나오는지 확인해야 한다.
2. **Case B2의 "결측 처리" 발견을 재현** — SCHD 1건에서만
   나왔다(n=1). 구성종목 데이터가 불완전한 다른 ETF(VNQ의 "Vanguard
   Real Estate II Index Fund" 항목처럼 원본 자체가 모호한 사례,
   §1에서 이미 발견됨)로 재확인 가치가 있다.
3. **Risk/Portfolio 경계 흐려짐(§9)이 3/4로 반복됨** — 이전 문서와
   합쳐 총 7/8 관찰 중 상당수에서 반복되고 있다 — 이제는 우연으로
   보기 어렵다. 별도의 전용 Dogfooding(Risk-Portfolio Boundary만
   따로 검증)이 필요한 시점일 수 있다는 것을 다음 세션에 명시적으로
   전달한다.
4. **정책(position limit 등)이 있을 때 이 Need가 얼마나 줄어드는지
   재검증** — Portfolio Need Dogfooding 문서의 CAT negative
   control(정책 있음→Case A)과 이번 GLD negative control(비주식→
   Case A)은 서로 다른 이유로 Case A였다. "정책이 있는 look-through
   사례"(예: QQQ 보유 + "ETF look-through 포함 종목당 최대 15%"
   같은 정책)를 아직 테스트하지 않았다 — 이것까지 확인해야 "정책
   추가만으로 Case B/C가 Case A로 내려가는지"를 알 수 있다.
5. 이번 판정(A, 조건부+수정됨)도 Architecture 설계를 허가하지
   않는다 — Freeze Review는 별도 문서에서, 그리고 위 선행조건들이
   충분히 쌓인 뒤에 판단한다.

---

## Self Review

- 서로 다른 Exposure Path를 하나의 숫자로 합산했는가 — **아니오**
  (§3·§4, 전수 확인, Case B에서는 모델 스스로 환산조차 거부하며
  더 엄격하게 지킴).
- Exposure schema나 필드명을 확정했는가 — **아니오**(§10, 요구사항만
  기록).
- 새로운 시장/구성종목 데이터를 생성했는가 — **아니오**(전부 기존
  ETF Team 실제 산출물 인용, Portfolio State만 가상).
- 실제 사례가 부족한 상태에서 억지로 사례를 만들었는가 — **아니오**
  (§1 사전 조사로 저장소에 이미 존재하는 A/B/C 성격의 실제 ETF를
  찾아 사용).
- Risk Architecture를 설계했는가 — **아니오**(§9, 경계 흐려짐 관찰만
  기록).
- `hqs/investment/`, Structure v1.0, RFC/ADC/ADR, Phase 7을
  수정했는가 — **아니오**(`git diff --stat hqs/investment/` 빈 결과
  재확인).
