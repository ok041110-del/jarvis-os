# INVESTMENT-HQ-TRADER-DECISION-DISCRIMINATION-DOGFOODING-0001

**문서 성격**: Experimental Prototype + Dogfooding Evidence 문서.
**Architecture Freeze/Contract 확정이 아니다.** RFC/ADC/ADR을 생성하지
않고, `hqs/investment/`·`core/`·Governance 문서를 수정하지 않는다.
이전 문서(`...SYNTHESIS-TRADER-EXPANSION-PROTOTYPE-0001.md`)에서 사용한
동일 프롬프트 템플릿(`trader_prototype.py`의 `trader_expanded()`)을
**한 글자도 바꾸지 않고** 재사용했다 — 사례별 Prompt 수정 없음(§4
준수). 실제 Engine 호출을 이번에 **2회 추가**(NVDA, JNJ) 실행했다
— `git diff --stat hqs/investment/`는 여전히 빈 결과로 확인됐다.

---

## 1. 사용한 실제 사례

사용자 지시(§2)에 따라 새 시장 데이터를 만들지 않고, **기존
Investment HQ Dogfooding 전체 데이터셋을 먼저 조사**해 BUY/SELL이
합리적으로 나올 만한 후보를 찾았다.

**사전 조사**: `find`로 저장소 안의 모든 `synthesis.md`(project-local
+ HQ-level, 중복 checkpoint 제외 시 **17개**)를 확인하고, 각 파일의
"Bottom line" 문단을 전수 확인했다(§1 조사 로그 참조 — AAPL/AAPL-run2/
CAT/PG/PG-run2/EFA/EFA-run2/QQQ/AGG/GLD/SCHD/UUP/VNQ/JNJ/KO/MSFT/NVDA/
JPM/Nestle/Toyota/Realty Income/EPD 등). **17개 전부**가 "데이터가
불충분해 확신 있는 방향을 판정할 수 없다"는 취지의 결론으로 끝나고
있었다 — 명백히 한쪽으로 기운 결론을 가진 사례는 **단 한 건도
발견되지 않았다.**

이 조사 결과를 근거로, **가장 편향된 것으로 보이는 두 사례**를 추가로
선정해 실제 Trader 실행까지 확인했다:

| # | Team | 종목 | 선정 근거 |
|---|---|---|---|
| 5(신규) | Stock | **NVDA** | 조사한 사례 중 Bull 논거가 가장 강한 후보 — Q1 매출 +85% YoY, 12-0/7-0 기술적 매수 신호, AI 수요 서사가 뚜렷함(원본 `bull_case.md` 직접 확인) |
| 6(신규) | Dividend Stock | **JNJ** | 조사한 사례 중 Bear 논거가 가장 강한 후보 — $5.5B 탈크 소송 합의, 파산보호 전략 기각, 현재가가 모든 공시된 애널리스트 목표가 상단($240)을 상회 |

기존 4개 사례(AAPL/CAT/PG/QQQ, 이전 Prototype 문서에서 재사용)에
NVDA/JNJ를 더해 **총 6개 사례, 3개 Team**을 이번 판정의 근거로 쓴다.

**동일 Trader Template 유지**: `trader_prototype.py`의
`trader_expanded()` 함수를 코드 diff로 재확인 — 이전 문서 작성 이후
**한 글자도 수정하지 않았다.** `CASES` 딕셔너리에 두 항목만
추가했을 뿐이다.

---

## 2. 사례별 Input Evidence

| 사례 | Bull 핵심 논거 | Bear 핵심 논거 | Synthesis 결론 |
|---|---|---|---|
| AAPL | 매출/EPS 서프라이즈, 미국 시장 지배력, Siri 출시 | 가이던스 자체가 회사의 둔화 예측, Services 미스 | 확신 있는 방향 불가 |
| CAT | 이익률 확대, 사상 최대 백로그, 관세 흡수 | 가이던스 문구 불일치, 관세 netting 미확인 | 확신 있는 방향 불가 |
| PG | 136년 배당 기록, 완만한 성장 지속 | Q4 EPS -15%, FCF 배당 커버리지 데이터 부재 | 확신 있는 방향 불가 |
| QQQ | AI 사이클 집중 노출, 초과수익률 | 집중도=단일 실패점, 리스크조정 지표 부재 | 확신 있는 방향 불가 |
| **NVDA** | 매출 +85% YoY, Data Center +21% QoQ, 12-0/7-0 기술적 매수 신호 | China 매출 0 반영, GAAP>Non-GAAP EPS 역전(미설명), 목표가 $180~$500(2.8배 스프레드) | **확신 있는 방향 불가**(양측 동일 사실, 해석만 반대) |
| **JNJ** | 어닝 서프라이즈+가이던스 상향, payout ratio 84%→46% 개선 | 현재가가 모든 공시 목표가 상회, $5.5B 탈크 합의, GAAP/조정 EPS 22% 갭 미설명 | **확신 있는 방향 불가**(동일 결론) |

**결정적 관찰**: NVDA(가장 강한 Bull 후보)와 JNJ(가장 강한 Bear
후보)를 의도적으로 선정했음에도, 원본 `synthesis.md` 자체가 **이미
둘 다** "동일한 사실에 대한 해석 차이일 뿐, 데이터 자체가 확신 있는
결론을 지지하지 않는다"는 결론으로 끝나 있었다(원본 파일 재확인,
이번 세션에서 새로 생성하지 않음).

---

## 3. 사례별 Trader Decision(실제 Engine 호출 결과)

| 사례 | Direction | Reassess when(요약) |
|---|---|---|
| AAPL | **HOLD** | Services 미스가 일시적인지 추세인지 |
| CAT | **HOLD** | $2.2~2.4B 관세가 가이던스에 이미 반영됐는지 |
| PG | **HOLD** | ~$1B 관세/원자재 헤드윈드가 가이던스에 반영됐는지 |
| QQQ | **HOLD** | Fed가 실제로 매파적 경로를 따르는지 |
| **NVDA** | **HOLD** | Blackwell 대중국 수출 라이선스 해소 시점 |
| **JNJ** | **HOLD** | $5.5B 탈크 합의가 이미 충당됐는지, 추가 부담인지 |

**6/6 전부 HOLD.** BUY 또는 SELL은 이번까지 포함해 **단 한 건도
관찰되지 않았다.**

---

## 4. BUY / SELL / HOLD 분포

```
HOLD: 6 / 6 (100%)
BUY : 0 / 6 (0%)
SELL: 0 / 6 (0%)
```

가장 편향된 두 후보(NVDA=Bull, JNJ=Bear)를 의도적으로 추가했음에도
분포가 바뀌지 않았다.

---

## 5. Evidence ↔ Action 관계

**Direction은 6/6 동일(HOLD)했지만, Rationale과 Reassess when은
사례마다 명확히 다른 내용을 담았다** — §5 검증 항목(C. Decision
Consistency) 기준을 적용한다:

- **입력 Evidence와 Action이 논리적으로 연결되는가**: 예 — 6개 Rationale
  전부가 해당 사례 고유의 구체적 사실(NVDA는 China 라이선스, JNJ는
  탈크 합의 충당 여부, PG는 관세 헤드윈드, QQQ는 Fed 경로)을 근거로
  들었다. 일반화된 정형 문구를 복사-붙여넣기한 흔적은 없었다(직접
  대조 확인).
- **반대 Evidence를 무시하지 않았는가**: 예 — NVDA Rationale은 Bull의
  강한 논거(매출 성장, 기술적 신호)를 그대로 인정하면서도 Bear가
  제기한 미해결 항목(EPS 역전, China)을 근거로 방향을 유보했다. JNJ도
  동일 패턴(어닝 서프라이즈 인정 + 소송/밸류에이션 리스크로 유보).
- **불확실성이 높은데 과도한 Action을 선택하지 않았는가**: 6/6 전부
  해당 없음(전부 HOLD, 과도한 Action 자체가 발생하지 않음 — 이
  질문은 오히려 §6 HOLD 편향 분석과 연결된다).

**결론**: Action(방향) 자체는 6/6 동일했지만, **그 방향에 도달하는
논증 경로는 사례마다 실제로 달랐다** — 이는 완전한 무구별력은
아니지만, 사용자가 요구한 "Evidence에 따른 실제 함수적 차이"(§6)를
Direction 필드 자체에서는 확인하지 못했다는 뜻이다.

---

## 6. HOLD 편향 분석

사용자가 제시한 5가지 가능성(§7)을 실제 근거로 구분한다.

| 가능성 | 채택 여부 | 근거 |
|---|---|---|
| **A. 실제 사례들이 모두 HOLD가 합리적이었음** | **채택** | §1에서 확인한 대로, 저장소 안의 **17개 원본 Synthesis 전부**가 이 Prototype 이전부터, 이 작업과 무관하게 독립적으로 "확신 있는 방향 불가"로 끝나 있었다. 이는 Trader/Decision 로직이 생기기 전부터 존재하던 사실이다 — Trader가 원본 데이터를 왜곡해서 HOLD로 유도한 것이 아니라, **원본 데이터 자체가 이미 그렇게 생성돼 있었다.** |
| B. Trader가 불확실성을 과도하게 보수적으로 처리 | **판별 불가(반증할 대조군 없음)** | 이를 확정하려면 "실제로 한쪽이 우세한 입력"을 Trader에 줘서 그래도 HOLD를 내는지 봐야 하는데, 그런 입력 자체가 데이터셋에 없다(§1). NVDA/JNJ가 "가장 편향된 후보"였지만 원본 자체가 이미 균형 상태였으므로, 이 두 사례로도 B를 반증하거나 확증할 수 없다. |
| C. Prompt가 행동 결정을 충분히 허용하지 않음 | **기각** | 프롬프트(`trader_expanded()`)는 BUY/SELL/HOLD를 대등한 선택지로 제시하며, 특정 방향을 유도하는 문구가 없다(코드 재확인, §1 이전 문서에서도 동일 결론). |
| D. Synthesis 결과가 Decision에 필요한 정보를 충분히 전달하지 못함 | **기각** | REPORT 섹션은 6/6 전부 상세하고 사례별로 구체적인 정보(§2, §5)를 담고 있었다 — 정보 전달 자체는 문제가 없었다. |
| E. Decision Logic 자체의 문제 | **기각** | Rationale이 사례마다 실제로 다른 근거를 인용했다(§5) — "무조건 HOLD를 출력하는 고정 로직"이었다면 Rationale도 정형화됐을 텐데, 실제로는 매번 그 사례 고유의 사실을 인용했다. |

**결론**: HOLD 편향의 원인은 **A(원본 데이터/Evidence 생성 방식 자체가
이미 균형 상태)** — 그리고 그 근본 원인은 Trader보다 상위 단계에
있다: Bull/Bear가 "제공된 데이터에만 근거해 최선의 선의의 주장을
구성하라"는 동일한 지시문으로 만들어지고, `raw_data.md`가 매번
"특정 시점의 웹서치 스냅샷"(실시간 아님, 종종 소스 간 수치 불일치
포함)으로 수집되기 때문에, Bull/Bear가 구조적으로 "동일 사실, 다른
해석"의 형태로 수렴하는 것으로 보인다 — **이는 이번 작업 범위 밖의
관찰**(Bull/Bear/Analysis 단계의 데이터 수집 방법론)이며, Trader
Decision Logic 자체의 결함이 아니다.

**B(과도한 보수성)를 완전히 배제하지 못한다는 점은 정직하게 남긴다**
— 진짜 비대칭 입력이 없는 한 이 질문에 최종 답을 할 수 없다(§11
선행조건).

---

## 7. Portfolio / Risk Boundary

6/6 전부에서 Trader는:

- position size를 결정하지 않았다.
- capital allocation을 하지 않았다.
- 전체 Portfolio를 가정하지 않았다.

6개 Rationale 전부가 "no portfolio context, existing position, or
sizing was provided or assumed" 류의 문장을 **스스로** 포함했다(직접
재확인, NVDA/JNJ도 동일 패턴) — 이전 Prototype 문서의 결론(4/4)이
NVDA/JNJ 추가로 **6/6까지 확장 재확인**됐다.

---

## 8. Report 정보 보존 결과

| 사례 | 원본 Synthesis 단어 수 | 새 REPORT 단어 수 | 변화율 |
|---|---|---|---|
| AAPL | 854 | 842 | −1.4% |
| CAT | 853 | 702 | −17.7% |
| PG | 1220 | 876 | −28.2% |
| QQQ | 965 | 702 | −27.2% |
| **NVDA** | 951 | 641 | **−32.6%** |
| **JNJ** | 1133 | 803 | **−29.1%** |

**추가 관찰**: NVDA/JNJ도 이전 4개 사례와 동일한 범위(약 −18~−33%)로
길이가 감소했다 — 이번 2개 사례로 "REPORT 길이 감소"가 우연이
아니라 **일관된 패턴(6/6 중 5/6에서 발생, AAPL만 예외)**임이 더
분명해졌다. 핵심 정보 범주(사실 합의/해석 분기점/데이터 공백/미해결
질문)는 NVDA/JNJ 둘 다 유지됐다(직접 대조 — 예: JNJ의 탈크 소송
축, NVDA의 China 라이선스 축 모두 REPORT에 온전히 남아있음). 이
문제는 여전히 **별도 분석 대상으로 유지**한다(사용자 지시 §9 준수,
이번 작업의 주 판정 기준으로 삼지 않음).

---

## 9. Contract 후보 Evidence

새 필드를 발견하지 않았다. 기존 후보에 대한 갱신만 기록한다:

- `action`: 6/6 산출됐으나 **6/6 전부 동일값(HOLD)** — 필드 자체의
  구조는 검증됐지만(파싱 가능, 3단계 중 하나를 선택), **구별력**은
  이번에도 입증하지 못했다.
- `rationale`/`reassessment_trigger`: 6/6 전부 사례별로 실질적으로
  다른 내용 산출(§5, §3) — 이 두 필드는 Direction과 달리 **실제
  구별력이 확인됐다.**
- `confidence`/`risk_notes`/`position_size`: 여전히 요청하지 않았고
  자발적으로 등장하지 않음(기존 판정 유지).

---

## 10. 최종 판정

## **D. UNTESTABLE**

**판정 이유**: 사용자 지시(§2)가 명시한 조건 — "실제 Evidence가
BUY/SELL 사례를 제공하지 못하면 억지로 사례를 만들지 않는다. 그
경우 'BUY/SELL 구별력은 현재 데이터셋으로 검증 불가'라고 판정한다"
— 이 정확히 이번 조사 결과와 일치한다.

- 저장소 안의 **모든 기존 Synthesis 산출물(17개)**을 조사했고, 명백히
  한쪽으로 기운 결론을 가진 사례가 **하나도 없었다.**
- 그중 가장 편향된 것으로 보이는 두 후보(NVDA=Bull 최강, JNJ=Bear
  최강)를 골라 실제로 Trader를 실행했으나, **둘 다 HOLD**였다 —
  원본 Synthesis 자체가 이미 두 후보 모두 균형 상태로 판정하고
  있었기 때문이다(§1, §2).
- 인위적으로 불균형한 사례를 만드는 것은 금지됐다(§3) — 그리고
  이번 조사는 그런 금지 없이도 "존재하지 않는다"는 결론에 정직하게
  도달했다.

**A/B/C로 판정하지 않는 이유**: A(VALIDATED)는 BUY/SELL 산출 자체가
없어 성립 불가. B(PARTIALLY VALIDATED)는 "일부만 확인됐지만 구별
가능성은 확인됨"을 요구하는데, 6/6 전부 동일값이라 구별
가능성조차 관찰되지 않았다. C(NOT VALIDATED, "Evidence와 Action의
관계가 불명확함")도 맞지 않는다 — 오히려 §5·§6에서 확인했듯
Rationale/Reassess when은 Evidence와 명확히 연결돼 있었고, HOLD로
수렴한 원인도 A(원본 데이터 자체의 균형)로 특정됐다 — "관계가
불명확한" 것이 아니라 "관계는 명확하지만 입력 자체가 다양하지
않다."

---

## 11. 다음 선행조건(§13 D 경로)

사용자 지시(§13)대로, D 판정 시 "BUY/SELL 사례가 발생할 때까지
Architecture Freeze를 보류"한다. 구체적으로:

1. **실제 명백한 방향성 사례가 나올 때까지 대기, 또는 신규 Dogfooding
   시도** — 다음 project-local 또는 HQ-level 실행에서 (a) 명백한
   실적 어닝쇼크(대폭 미스 또는 대폭 서프라이즈), (b) 신용등급
   강등/부도 위험 같은 명백한 부정적 이벤트, (c) 인수합병 발표 같은
   명백한 긍정적 이벤트를 다루는 종목이 자연스럽게 나오면, 그 사례로
   즉시 재검증한다. **인위적으로 이런 사례를 지금 만들지 않는다**
   (사용자 지시 §2·§3 준수 유지).
2. **B(Trader의 과도한 보수성) 가설을 계속 열어둔다** — 위 1번의
   실제 비대칭 사례가 나왔을 때도 HOLD가 나온다면, 그때는 A가
   아니라 B(또는 Decision Logic/Prompt 자체의 보수성 편향)로 판정이
   바뀔 수 있다는 것을 다음 조사자가 알아야 한다.
3. **REPORT 길이 감소(§8, 6개 중 5개, −18~−33%)**는 별도 조사
   대상으로 유지한다 — 이번 작업의 판정에는 영향을 주지 않았지만,
   Decision discrimination이 확인된 이후 단계에서 반드시 확인해야
   한다.
4. `action`을 제외한 `rationale`/`reassessment_trigger`는 이번
   조사로 구별력이 실증됐다(§9) — 이 둘은 D 판정과 별개로 Contract
   후보로서의 근거가 유지·강화됐다는 점을 기록한다.
5. 이번 판정(D)은 Trader Architecture 자체를 기각하는 것이 아니다
   — "현재 보유한 Evidence로는 Decision discrimination을 증명할 수
   없다"는 뜻이며, Architecture Freeze Review는 이 선행조건이
   충족되기 전까지 보류한다.

---

## Self Review

- 인위적으로 BUY/SELL을 유도하는 사례나 Prompt를 만들었는가 —
  **아니오**(§2 — 기존 데이터에서 가장 편향된 후보를 선정했을 뿐,
  실제 결과는 그래도 HOLD였다).
- 사례별로 Prompt를 수정했는가 — **아니오**(§1, 코드 diff로 확인).
- 동일 사례를 원하는 결과가 나올 때까지 반복 실행했는가 —
  **아니오**(6개 사례 각 1회씩만 실행).
- 결과를 사후 수정했는가 — **아니오**.
- Contract를 확정했는가 — **아니오**(§9, 후보 갱신만).
- Portfolio/Risk Architecture를 설계했는가 — **아니오**.
- Disclaimer를 삭제·약화했는가 — **아니오**(원본 무수정).
- `hqs/investment/`, `core/`, Governance 문서를 수정했는가 —
  **아니오**(`git diff --stat hqs/investment/` 빈 결과 재확인).
