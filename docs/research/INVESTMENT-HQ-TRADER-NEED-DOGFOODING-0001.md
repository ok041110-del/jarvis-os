# INVESTMENT-HQ-TRADER-NEED-DOGFOODING-0001

**문서 성격**: Dogfooding Evidence 문서. **RFC/ADC/ADR이 아니고, Architecture
설계도 아니다.** `INVESTMENT-HQ-V2.0-ARCHITECTURE-FREEZE-REVIEW-0001.md`
(판정: C. NOT READY)가 지목한 선행조건 중 2번("최소 1건의 실제 Trader
Dogfooding")을 실행한 결과다. 이 문서는:

- TradingDecision Contract를 확정하지 않는다.
- Portfolio/Risk Architecture를 설계하지 않는다.
- LangGraph를 Production에 도입하지 않는다.
- Core Architecture, Governance 문서, `hqs/investment/` 코드를 수정하지
  않는다.
- Trader Component를 구현하지 않는다.

**방법론 참고**: `call_engine()`을 새로 호출(자동화된 Engine 실행)하지
않았다 — 대신 §3 방법 4단계("해당 결과를 Trader 관점에서 검토")를
그대로 따라, 이미 v1.0 Freeze Evidence로 확정된 실제 산출물을
**Trader 역할로 직접 검토(manual review)**했다. 이는 코드 구현이
아니라 관찰 행위이며, 새 프롬프트/코드를 작성하지 않았다.

---

## 1. 사용한 Dogfooding 사례

**`hqs/investment/dogfooding/aapl-hq-verify`**(Stock Team, `run.py`
경로, `EVIDENCE.md`로 이미 v1.0 Freeze 근거의 일부로 확정된 사례)를
사용했다.

**선정 근거**: 사용자 지시대로 Stock을 우선 사용했다. `aapl-hq-verify`를
같은 Stock Team의 다른 사례(`aapl-hq-verify-run2`, `projects/
stock-analysis-*`)보다 우선한 이유:

1. `run.py` HQ-level 경로로 실행된 사례이며 `EVIDENCE.md`로 콘텐츠
   품질(19/19 핵심 수치 보존)이 이미 검증돼 있어, 이번 Dogfooding이
   "품질이 의심스러운 산출물을 놓고 헛수고하는" 위험이 없다.
2. Bull/Bear가 정면으로 부딪히면서도 데이터 자체는 다투지 않는 사례라
   (§2), Synthesis만으로 충분한지 Trader가 더 필요한지를 판별하기에
   좋은 시험대다 — 만약 Bull/Bear가 애초에 사실관계로 갈렸다면
   "Trader가 아니라 데이터 정합성 문제"로 오염됐을 것이다.
3. 인위적으로 복잡한 실패 상황을 만들지 않는다는 원칙(§3)에 따라,
   추가 실행 없이 기존 Frozen Evidence를 그대로 재사용했다.

---

## 2. Analysis → Bull/Bear → Synthesis 결과 요약

실제 파일(`fundamental_analysis.md`, `technical_analysis.md`,
`industry_analysis.md`, `news_event_analysis.md`, `sentiment_analysis.md`,
`bull_case.md`, `bear_case.md`, `synthesis.md`)을 전부 직접 읽었다.

| 단계 | 핵심 내용 |
|---|---|
| Fundamental | 매출 +16%/EPS +29% 서프라이즈(단, EPS 중 $0.11은 관세 환급 일회성), iPhone/Mac 서프라이즈, Services 미스, 차분기 가이던스 둔화(+9~11%, 사유: FX+공급제약) |
| Technical | 이평선·RSI 수치가 **소스 간 불일치**(50일 이평 $295.9 vs $312.33, RSI 37.7 vs 53.5), "bullish outlook, bearish momentum" 자체 모순 표현, **현재가 미제공**(이 섹션 한정) |
| Industry | 미국 58.2% 지배적 vs 글로벌 3파전(20~21%), 중국 시장 경쟁사 명단에 Apple 부재(share 수치 자체 없음) |
| News/Event | Siri AI 출시했으나 "anticlimactic" 반응, EU/중국 규제로 롤아웃 제외, 실적 후 시간외 하락이 Services 미스와 연관 보도 |
| Sentiment | 목표주가 컨센서스 $322.7~322.8(두 소스 수렴), **현재가 $308.63 명시**(이 섹션에만 등장), 목표 범위 $215~$400(현재가 대비 -31%~+28%, 매우 넓음) |
| Bull Case | 7개 논거(어닝 서프라이즈, 프랜차이즈 재가속, 가이던스 둔화는 일시적 요인, 미국 프리미엄 지배력, Siri 출시, 셀사이드 우호적, 기술적 상승 추세) + **"이 케이스가 약한 지점" 섹션을 자체 명시**(Services 미스, Siri 근시일 매출 기여 제한, EPS 품질, 기술적 지표 불일치, 목표주가 분산, 중국 지위 불명) |
| Bear Case | 8개 논거(가이던스 자체가 회사의 감속 예측, Services 미스, EPS 일회성, Siri 반응 미온+2대 시장 제외, 시간외 하락, 미국 편중된 지배력, 기술적 혼재, 목표가 분산이 red flag) + **"이 케이스가 데이터로 제약되는 지점" 섹션을 자체 명시** |
| Synthesis | Bull/Bear는 **사실관계에서 다투지 않는다**(모든 수치 인용 일치) — 차이는 **동일 사실의 해석/가중치**뿐. 5개 해석 분기점을 정리하고, 마지막에 명시적으로 **"이 데이터만으로는 확신 있는 방향 결론에 도달할 수 없다"**고 선언하며 방향(BUY/SELL/HOLD)을 제시하지 않는다 |

**결정적 관찰**: Synthesis는 결론을 내리지 않는 것을 **실수로 빠뜨린
것이 아니라 지시문("This is not a trade order")대로 정확히 수행한
것**이다 — 그리고 Synthesis 스스로 "무엇이 있으면 결론을 내릴 수
있는지"(다음 분기 Services 추세, 공급 정상화 여부, 중국 점유율,
Siri 참여 지표, 관세 제외 EPS)를 5개 항목으로 구체적으로 나열했다.

---

## 3. Trader 단계에서 관찰된 실제 Need

Synthesis 산출물을 그대로 입력 삼아, **실제로 Trader 역할을 수행**해
"이 종목을 지금 사겠다/팔겠다/보유하겠다"는 판단을 시도했다. 시도
과정에서 실제로 부딪힌 것을 그대로 기록한다.

### 3-1. Analysis 결과만으로 판단 가능한가 — **아니오, 실제로 막혔다**

Synthesis가 나열한 5개 미해결 질문(§2) 중 어느 것도 이번 raw_data에
답이 없다 — 이는 추측이 아니라 raw_data.md와 8개 산출물을 전부
대조해서 확인한 사실이다. Trader 역할을 하려는 시도 자체가, Synthesis가
이미 문서화한 정보 공백에 그대로 부딪혔다. **다만** 이 공백이 "Trader가
없어서" 생긴 것인지 "raw_data 수집이 이 시점엔 원래 불완전해서" 생긴
것인지는 이 1건만으로 구분할 수 없다(§10 Evidence Gap).

### 3-2. 서로 충돌하는 분석 결과가 발생하는가 — **부분적으로, 그리고 흥미로운 형태로**

- **사실 충돌**: Analysis 섹션 내부에 이미 존재한다 — Technical
  Analysis 안에서 50일 이평($295.9 vs $312.33), RSI(37.7 vs 53.5)가
  소스마다 다르다. 이는 Bull/Bear 사이의 충돌이 아니라 **Analysis
  단계 내부의 데이터 정합성 문제**다 — Trader가 해결할 문제가
  아니라 Technical Analyst/데이터 수집 단계의 문제로 분류해야 한다.
- **해석 충돌**: Bull/Bear는 사실을 다투지 않고 가중치만 다르게 준다
  (Synthesis가 이미 명시). 이 "사실 vs 해석 충돌"의 구분 자체가
  Trader/Research Manager 판단에 필요한 입력이라는 것이 이번에
  실제로 관찰됐다 — Synthesis가 이 구분을 이미 정확히 해내고 있다는
  점도 확인됐다(§7).
- **섹션 간 데이터 불일치(신규 관찰)**: Technical Analysis는 "현재가가
  명시적으로 제공되지 않았다"고 명시하는데, Sentiment Analysis에는
  현재가 $308.63이 명시돼 있다. **같은 raw_data.md 안에 있는 정보를
  Analyst마다 자신의 섹션 태그로만 나눠 받기 때문에, 한 Analyst가
  가진 정보를 다른 Analyst는 못 보는 구조적 공백이 실제로 존재한다**
  (§1의 `_extract_section`이 섹션 태그 단위로만 데이터를 잘라 전달하는
  것과 정확히 일치, `stock_team.py` 코드로 재확인). 이는 Trader
  Need라기보다 **Analysis 단계의 Context 전달 방식 문제**로 분류해야
  한다(§10).

### 3-3. BUY/SELL/HOLD 같은 명시적 결정이 실제로 필요한가 — **A. 실제 Need로 관찰됨**

Trader 관점에서 검토를 시도해보니, "다음에 뭘 해야 하는가"라는 질문에
Synthesis는 의도적으로 답하지 않는다. 만약 이 산출물을 실제 투자
판단의 입력으로 쓰려는 사람이 있다면, Synthesis를 읽은 다음 반드시
스스로 "그래서 사나 마나"를 결정해야 한다 — 이 결정 자체를 시스템이
만들지 않으면, 결국 사람이 Synthesis+Bull+Bear 전체(약 90줄)를 다시
읽고 암묵적으로 이 판단을 매번 반복해야 한다는 뜻이다. **이는
추측("필요해 보인다")이 아니라, 실제로 그 판단을 이번에 직접
시도했을 때 반드시 거쳐야 했던 단계였다는 것으로 확인된 관찰이다.**

---

## 4. 필요한 Input

Trader 역할을 실제로 수행하며 "이게 있었으면 판단이 더 쉬웠을 것"이라고
확인된 것만 기록한다(사전 가정 아님):

| Input | 현재 존재 여부 | 관찰 |
|---|---|---|
| 현재가 | **존재하나 위치가 틀렸다** — Sentiment 섹션에만 있고 Technical 섹션엔 없음(§3-2) | Trader가 지지선($246.24)/저항선($315.2)/이평선 대비 현재가 위치를 판단하려면 이 값이 필요한데, Technical 산출물 자체에는 없어서 **다른 산출물(Sentiment)을 가로질러 찾아야 했다** — 실제로 이번 검토에서 그렇게 했다 |
| 결론을 흔들 다음 이벤트/시점 | Synthesis에 5개 질문으로 이미 존재(§2) | Trader가 "언제 재평가해야 하는가"를 정하려면 이 5개 질문 중 어느 것이 가장 먼저 답을 얻을지(예: 다음 분기 실적 발표일)가 필요 — raw_data.md에는 다음 실적 발표일이 명시돼 있지 않음(확인) |
| 포트폴리오 컨텍스트(기존 보유량, 다른 종목 비중) | **전혀 없음** | Position Size를 판단하려는 시도 자체가 이 정보 없이는 원천적으로 불가능했다(§5) — Team-level 산출물 어디에도 포트폴리오 정보가 없다 |
| Bull/Bear가 이미 명시한 약점(무효화 조건) | **이미 존재** | Bull Case의 "Where this case is thin", Bear Case의 "Where constrained by the data" 섹션이 사실상 risk_notes에 해당하는 내용을 **이미 담고 있다**(§7에서 상세) |

---

## 5. 필요한 Output

실제로 판단을 시도한 결과, Trader가 산출해야 하는 것으로 관찰된 것:

1. **방향(BUY/SELL/HOLD에 해당하는 무언가)** — §3-3에서 확인된 실제
   Need.
2. **그 방향을 뒷받침하는 근거의 축약** — Synthesis 전체(약 35줄)를
   매번 다시 읽지 않고 판단 근거를 확인할 수 있어야 한다는 필요가
   검토 중 실제로 느껴졌다. 다만 이것이 새 필드(`rationale`)가
   필요하다는 뜻인지, Synthesis를 그대로 인용하면 되는지는 이번
   1건으로 확정할 수 없다.
3. **재평가 시점/조건** — "다음에 뭘 보면 이 판단이 바뀌는가"에 대한
   답은 Synthesis가 이미 5개 질문으로 갖고 있다(§2) — Trader가 이걸
   그대로 넘겨받아 "Q4 실적 발표(Services 추세 확인) 시 재평가"처럼
   구체화하는 것이 실제로 가능해 보였다. 이것이 사용자 초안의
   `time_horizon`과 같은 개념인지는 불명확하다 — 오히려 "보유 기간"이
   아니라 "재평가 트리거"에 가까운 성격으로 관찰됐다(§8에서 재검토).
4. **Position Size — 이번 사례에서는 산출 불가능함이 확인됨**(§4).
   이는 "Trader Output에서 빠졌다"가 아니라 **"Team/Trader 레벨
   정보로는 원천적으로 답할 수 없는 질문"**이라는 것이 실제로
   확인된 것이다 — Portfolio Need 관찰로 별도 기록한다(§9).

---

## 6. 반복적으로 관찰된 정보

**주의**: 이번 Dogfooding은 **1건**이다. "반복 관찰"이라고 부를 수
있는 것은 엄밀히는 없다 — 아래는 이 1건 안에서 **여러 단계(Bull,
Bear, Synthesis, raw analysis)에 걸쳐 일관되게 나타난 패턴**이며,
Team 간 반복(예: ETF/Dividend Stock에서도 동일 패턴이 나오는지)은
확인되지 않았다.

- **자기 한계 인정 패턴**: 5개 Analysis, Bull, Bear, Synthesis
  전부가 "데이터 한계"를 명시적으로 서술한다 — 이는 v1.0 Freeze
  Evidence(`aapl-hq-verify/EVIDENCE.md`)가 이미 기록한 패턴의
  재확인이며, Trader 검토 중에도 동일하게 관찰됐다.
- **Bull/Bear가 이미 자체 risk_notes를 갖고 있다는 패턴**(§7) — 이번
  1건에서 최초로 포착됐다.
- **섹션 경계를 넘는 정보(현재가)가 한쪽에만 존재하는 패턴**(§3-2) —
  이번 1건에서 최초로 포착됐다. 다른 종목에서도 나타나는지는 미확인.

---

## 7. TradingDecision 후보 필드 (사전 정의 아님, 관찰에서 도출)

사용자 지시(§4)대로 필드를 미리 확정하지 않는다. 이번 1건의 실제
검토에서 **반복적으로 필요가 느껴진 것만** 후보로 기록하고, 각각에
Evidence 강도를 명시한다.

| 후보 필드 | 이번 1건에서 관찰된 근거 | Evidence 강도 |
|---|---|---|
| `action`(방향) | §3-3 — 실제로 판단을 시도했고 Synthesis가 의도적으로 비워둔 자리임을 확인 | **가장 강함** — 그러나 n=1 |
| `rationale`(근거 축약) | §5-2 — 필요가 느껴졌으나 새 필드인지 기존 Synthesis 인용인지 불명 | 약함, 형태 미정 |
| `reassessment_trigger`(재평가 시점/조건) | §5-3 — Synthesis의 5개 질문에서 자연스럽게 도출 가능해 보였음. **사용자 초안의 `time_horizon`과 다른 개념일 가능성**(보유 기간이 아니라 "무엇을 보면 바뀌는가") | 약함, n=1, 그리고 `time_horizon`과 개념이 다를 수 있다는 의문 자체가 이번 관찰의 성과 |
| `confidence` | 이번 검토에서 판단의 확신도가 실제로 낮았다("두 논거가 동일 데이터를 다르게 해석"할 뿐이라 방향을 정해도 확신은 낮음) — 그러나 이걸 수치/범주로 표현해야 할 필요를 **직접 느끼지는 못했다**. Synthesis의 서술("이 데이터만으로는 확신 있는 결론에 도달할 수 없다") 자체가 이미 confidence 정보를 정성적으로 담고 있어서, 별도 필드가 추가로 필요한지 불확실 | **약함 — 이전 Audit(§5, TradingAgents에도 근거 없음)과 일치, 이번에도 근거를 새로 만들지 못함** |
| `risk_notes` | §7 상세 — Bull/Bear의 "thin"/"constrained" 섹션이 이미 이 내용을 담고 있음. **새 필드보다는 기존 Bull/Bear 산출물에서 발췌/재사용하는 방식이 더 근거 있어 보인다** | 중간 — Need는 있으나 "새 필드"가 아니라 "기존 산출물 재사용"으로 해결될 가능성 |
| `position_size` | §4·§5-4·§9 — **이번 사례에서 명확히 산출 불가능**(포트폴리오 컨텍스트 부재) | Trader 필드 후보에서 **제외** — Portfolio Need로 재분류 |
| `expected_direction` | `action`과 실질적으로 같은 개념으로 관찰됨(둘을 구분해야 할 실제 사례를 못 찾음) | 근거 없음, 별도 필드 불필요해 보임 |

**중요한 발견**: 이전 Freeze Review(§Trading Decision Contract)가
지적한 `time_horizon`의 계층 불일치(Team-level vs Portfolio-level)가
이번 실제 검토로 **더 구체화됐다** — 이번 관찰은 `time_horizon`이
"얼마나 오래 들고 있을지"가 아니라 "무엇을 확인하면 판단이 바뀌는지"
(재평가 트리거)에 가깝다는 것을 시사한다. 이는 사용자 초안에도,
TradingAgents 스키마에도 없던 **제3의 후보 개념**이며, 아직 후보일
뿐 확정이 아니다.

---

## 8. Trader Component 필요성

Synthesis에서 곧바로 Trader로 넘어가려 했을 때, 실제로는 **두 개의
서로 다른 조작이 필요했다**는 것을 시도 중에 발견했다:

1. **방향을 정하는 조작**(어느 해석이 더 설득력 있는지 판단) — 이는
   TradingAgents의 Research Manager가 하는 일과 유사하다(§2-3 이전
   Audit).
2. **그 방향을 실행 가능한 형태로 바꾸는 조작**(재평가 트리거를
   구체화, 근거를 축약) — 이는 TradingAgents의 Trader가 하는 일과
   유사하다.

**이 두 조작이 실제로 다르게 느껴졌다는 것 자체가 이번 Dogfooding의
핵심 발견이다** — 그러나 이것은 **n=1의 단일 관찰**이며, "Research
Manager와 Trader를 분리해야 한다"는 결론을 내리기엔 반복 검증이
없다. 현재로선 "Synthesis 이후에 최소 하나의 새 단계가 필요해
보인다"까지만 말할 수 있고, 그 단계가 하나(Trader만)인지 둘(Research
Manager + Trader)인지는 **Evidence 부족**이다.

---

## 9. Risk / Portfolio Need의 관찰 여부

**Risk**: 이번 1건에서 "HQ-level Risk"에 대한 직접적 Need는 관찰되지
않았다 — Bull/Bear가 이미 각자의 리스크(무효화 조건)를 서술하고
있어서, 종목 하나만 보는 한 별도 Risk 단계의 부재가 판단을 막지
않았다.

**Portfolio Need 관찰 (기록, 설계 아님)**: §4·§5-4에서 이미 확인한
대로, **Position Size를 판단하려는 시도가 실제로 막혔다** — "이
종목을 얼마나 사야 하는가"는 이 종목 하나의 분석만으로는 원천적으로
답할 수 없다(기존 보유 비중, 다른 자산과의 상관관계, 가용 현금 등이
전부 Team 밖의 정보). 이는 사용자가 예시로 제시한 문장("Trader
결과만으로는 전체 Portfolio 판단이 불가능하다")과 정확히 일치하는
형태로 **실제 관찰됐다**. Portfolio Architecture는 설계하지
않는다 — 이 관찰만 기록한다.

---

## 10. Evidence Gap

| 항목 | 분류(사용자 §8 기준) |
|---|---|
| Trader가 Synthesis 이후에 필요하다(방향 결정 미해결) | **실제 Need** — 이번 1건에서 직접 확인 |
| Position Size는 Trader/Team 레벨에서 해결 불가 | **실제 Need 없음(Trader 레벨에서는)** — 대신 Portfolio Need로 전이 관찰 |
| risk_notes | **기존 Architecture(Bull/Bear 산출물)로 해결 가능할 가능성** — 새 필드보다 발췌/재사용 우선 검토 필요 |
| confidence | **Evidence 부족** — 정성적 서술(Synthesis 문장)이 이미 이 역할을 하고 있어, 별도 필드의 필요성을 이번 검토로 확인하지 못했다 |
| time_horizon(원안) vs reassessment_trigger(신규 후보) | **Architecture Need 후보** — 개념 자체가 사용자 초안과 다를 수 있다는 것이 이번 발견. 추가 Dogfooding 필요 |
| Research Manager/Trader 2단계 분리 | **추가 Dogfooding 필요** — n=1로는 결론 불가 |
| 섹션 간 정보 공백(현재가가 Technical에 없음) | **Analysis 단계 문제**(Trader Need 아님) — `_extract_section`의 태그 기반 분리 방식이 원인. Trader Contract와 무관하게 별도 관찰로 기록만 함, 이번 문서 범위 밖 |
| Technical 소스 간 수치 불일치(이평선/RSI) | **Analysis 단계 데이터 품질 문제**(Trader Need 아님) — 별도 관찰로만 기록 |

---

## 11. 최종 판정

## **B. Trader Need는 있으나 Contract 정의에는 Evidence 부족 → 추가 Dogfooding 필요**

**판정 이유**: §3-3·§8이 보여주듯, "Synthesis 다음에 무언가가 더
필요하다"는 것은 이번 실제 검토로 **분명하게 관찰**됐다 — Synthesis가
의도적으로 방향 결정을 비워두고 그 사실을 스스로 명시하기 때문에,
Trader(또는 그와 유사한 무언가)의 부재가 실제 사용 흐름의 빈틈으로
드러났다. 그러나:

- 필드 후보(§7) 중 `action` 외에는 전부 Evidence가 약하거나(n=1),
  다른 방식(기존 Bull/Bear 재사용)으로 해결될 가능성이 있거나
  (`risk_notes`), 개념 자체가 사용자 초안과 달라 보인다
  (`time_horizon` → `reassessment_trigger` 의문).
- Research Manager/Trader 분리 여부도 미결.
- `position_size`는 Trader 범위에서 아예 제외되고 Portfolio Need로
  전이됐다 — Contract의 범위(Trader가 무엇을 책임지는가) 자체가
  이번 1건으로 다시 흔들렸다.

**A(명확한 Need)로 판정하지 않은 이유**: "Trader라는 개념이 필요하다"는
방향성은 명확하지만, "그 Trader가 구체적으로 무엇을 입출력하는가"는
1건의 관찰만으로 고정할 수 없다. **C(불필요)로 판정하지 않은 이유**:
기존 Synthesis/Report 구조가 충분하다고 볼 근거는 없다 — 오히려
Synthesis 자체가 스스로 결론을 못 낸다고 명시한다. **D(관찰 방법
부적합)로 판정하지 않은 이유**: 이번 방법(기존 Frozen Evidence를
Trader 관점에서 재검토)으로 구체적이고 반복 가능한 관찰(§3-2 현재가
공백, §7 risk_notes 발견, §8 2단계 조작 등)이 여러 건 나왔다 —
방법 자체는 유효했고, 부족한 것은 **반복 횟수(n)**이지 방법이 아니다.

---

## 12. 다음 Dogfooding 조건

1. **같은 방법을 최소 2건 더 반복**한다 — 이번 Contract 후보 필드
   (§7)가 다른 종목/다른 Team에서도 같은 형태로 나타나는지 확인해야
   "반복 관찰"이라 부를 수 있다. 우선순위: (a) Bull/Bear가 사실관계
   자체로 충돌하는 사례(이번 AAPL은 해석만 충돌했다 — 사실 충돌
   사례에서 Trader Need가 다르게 나타나는지 확인), (b) ETF/Dividend
   Stock에서도 동일한 "Synthesis가 결론을 비워둔다" 패턴이 나타나는지.
2. **Research Manager/Trader 분리 여부**를 판별하려면, 이번처럼
   한 번에 두 조작을 섞어 시도하지 말고 **의도적으로 두 단계로
   나눠 시도**해 실제로 다른 정보/다른 실패 모드가 나오는지 관찰한다.
3. **risk_notes를 별도 필드로 만들지, Bull/Bear에서 발췌할지**를
   판별하려면, 실제로 발췌 방식을 한 번 시도해보고(코드 없이 수작업
   발췌) 정보 손실이 있는지 확인한다.
4. **`reassessment_trigger` 개념**이 실제로 `time_horizon`과 다른지
   확인하려면, 재평가 트리거가 명확한 이벤트(다음 실적 발표)가 있는
   사례와, 그런 이벤트가 불명확한 사례(예: 배당주처럼 트리거가
   분기 실적보다는 장기 추세인 경우)를 대조해야 한다 — Dividend
   Stock Team이 이 대조에 적합할 수 있다.
5. 이 모든 후속 Dogfooding도 **코드 구현 없이** 기존 Frozen Evidence
   재검토 또는 최소 규모 project-local 실행으로 수행한다 — Contract를
   먼저 만들고 거기에 맞춰 실행하지 않는다(§4 순서 유지).

---

## Self Review

- TradingDecision Contract를 확정했는가 — **아니오**(후보만 기록,
  Evidence 강도를 전부 "약함"으로 명시).
- Portfolio/Risk Architecture를 설계했는가 — **아니오**(관찰만 기록).
- LangGraph를 도입했는가 — **아니오**.
- Trader Component를 구현했는가 — **아니오**(코드 변경 없음).
- `hqs/investment/`, `core/` 코드를 수정했는가 — **아니오**.
- "필요해 보인다"를 Evidence로 취급했는가 — **아니오**(§7의 모든
  후보 필드에 Evidence 강도와 n=1이라는 한계를 명시).
- 사전에 Contract 필드를 가정했는가 — **아니오**(§4 순서: 실제 시도
  → 관찰된 것만 §7에 후보로 기록).
