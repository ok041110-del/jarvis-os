# INVESTMENT-HQ-SYNTHESIS-TRADER-EXPANSION-PROTOTYPE-0001

**문서 성격**: Experimental Prototype + Dogfooding Evidence 문서.
**Architecture Freeze가 아니다.** RFC/ADC/ADR을 생성하지 않고,
`hqs/investment/`·`core/`·Governance 문서를 수정하지 않는다. Prototype
코드는 격리된 `projects/synthesis-trader-expansion-prototype/`에만
존재하며, 실행 후에도 `hqs/investment/`는 무수정 상태로 확인됐다
(`git diff --stat hqs/investment/` — 빈 결과). Contract를 확정하지
않는다.

**핵심 결론**: 판정 B — Synthesis→Trader 확장은 가능하지만 근거가
더 필요하다. 실제 Engine 호출 4회로 REPORT/DECISION 분리는 검증됐지만
4건 모두 HOLD로 수렴해 action 필드의 변별력은 입증되지 않았고, E2E
Workflow 통합은 테스트되지 않았다.

**이번 작업은 실제 Engine 호출을 포함한다** — 이전 세 Dogfooding
문서(수작업 재검토)와 달리, 이번엔 `hqs/development/mvp/engine.py`의
`call_engine()`을 통해 **실제로 4회 Engine을 호출**했다(AAPL/CAT/
PG/QQQ 각 1회, 총 4회, 성공 4/4). 원본 `synthesis_judgment()`는
import만 하고 호출하지 않았다 — 비교 대상 산출물(`synthesis.md`)은
이미 존재하는 기존 Frozen Evidence를 그대로 재사용했다.

---

## 1. 기존 Synthesis 구현 Audit

**경로 정정**: 사용자 지시는 `hqs/investment/teams/stock/`를
언급했으나, 실제 저장소 구조는 `hqs/investment/teams/stock_team.py`
(하위 디렉토리 없는 단일 파일)이다 — `STRUCTURE.md`/`README.md`와
직접 대조해 확인했다. 이 문서 전체에서 실제 경로를 사용한다.

`stock_team.py`(232줄)를 직접 재확인:

- **Synthesis input**: `bull_case`, `bear_case`(둘 다 `str`) — Analysis
  5건 원본에는 접근하지 않는다(`all_analyses`는 Bull/Bear 생성에만
  쓰이고 Synthesis에는 전달되지 않음, 코드 확인).
- **Synthesis prompt**(`synthesis_judgment()`): "Bull Case와 Bear Case를
  종합해 균형 잡힌 판단을 만들라. 사실 충돌과 해석 차이를 구분하고,
  결론을 가장 크게 바꿀 미해결 질문을 명시하라. **이것은 거래
  주문이 아니며 buy/sell/hold 지시를 포함해서는 안 된다.**"
- **Synthesis output**: `str`(자유 서술, Contract 없음).
- **Final Report 생성**: `report_writer_final_report()`가 `synthesis`
  문자열을 다른 8개 섹션과 함께 그대로 받아 `[SYNTHESIS]\n{synthesis}`
  형태로 삽입, 최종적으로 "explicit disclaimer that this is an
  analysis exercise, not investment advice or a trade recommendation"
  로 끝나야 한다는 지시를 별도로 갖는다(코드 확인, 재인용).
- **Team State**: 없음 — `wave1_results`/`wave2_results`는 `run()`
  함수 지역 dict(§이전 Freeze Review에서 이미 확인된 사실 재확인).
- **기존 Workflow 연결**: `run()`이 Wave1(5개 분석, 병렬) → Wave2
  (Bull/Bear, 병렬) → Wave3(Synthesis, 단일) → Wave4(Final Report,
  단일) 순으로 하드코딩 호출. `synthesis_judgment(bull_case, bear_case)`
  결과가 `synthesis` 변수 하나로 `wave4`에 그대로 전달된다.

**핵심 Audit 결과**: Synthesis는 이미 **Bull/Bear만 입력**으로 받고
있어(원본 Analysis 5건과 직접 연결되지 않음), 사용자가 제시한 가설
다이어그램(`Analysis → Bull/Bear → Trader`)과 **정확히 일치하는
입력 경계**를 이미 갖고 있었다 — Prototype이 입력 경계를 바꿀
필요가 없었다.

---

## 2. Prototype 변경 범위

`projects/synthesis-trader-expansion-prototype/trader_prototype.py`
(신규 파일, 격리된 디렉토리)만 작성했다:

- `hqs/investment/teams/stock_team.py`의 `synthesis_judgment` 등을
  **import만** 하고 원본을 수정하지 않았다.
- `trader_expanded()`라는 새 함수 하나만 작성 — 원본
  `synthesis_judgment()`의 지시문 문장을 **한 글자도 바꾸지 않고
  그대로 포함**하고, "not a trade order" 문장만 제거한 뒤 Decision
  책임(§4)을 추가했다(최소 변경 원칙).
- 실행 결과는 `projects/synthesis-trader-expansion-prototype/results/
  {case}_trader_expanded.md`에 저장 — `hqs/investment/dogfooding/`나
  `projects/*-analysis-*/`의 기존 산출물은 전혀 건드리지 않았다.

`git diff --stat hqs/investment/` 결과가 빈 값임을 재확인했다 —
Prototype이 기존 Investment HQ 코드에 미친 영향은 **0**이다.

---

## 3. Trader 책임 정의(Prototype 프롬프트)

실제 프롬프트(`trader_expanded()` 발췌):

```
[기존 synthesis_judgment() 지시문 그대로]
+ "decide a present-moment directional stance for this individual
   security based only on the information given here. Do not assume
   any portfolio context, existing position, capital allocation, or
   position sizing — if such information would be needed... say so
   explicitly... your scope is limited to this single security's
   current-information directional stance; you are not a portfolio
   manager..."

## REPORT  (기존 Synthesis와 동일한 내용, 방향 결정 없음)
## DECISION
- Direction: BUY / SELL / HOLD 중 하나
- Rationale: REPORT에만 근거, 2-4문장
- Reassess when: REPORT의 미해결 질문 중 가장 결정적인 것 하나
```

Position size/capital allocation/portfolio는 프롬프트에서 **명시적으로
금지**했다(사용자 지시 §4 준수) — 4개 결과 전부에서 실제로 이
경계가 지켜졌는지 §11에서 확인한다.

---

## 4. Decision / Report Output 분석

**분리 가능성(Q3) — 실제로 검증**: 4개 결과 파일 전부 `## REPORT`/
`## DECISION` 헤더로 완전히 파싱 가능했다(수작업 확인). 추가로,
`## DECISION` **이전** 텍스트 구간에서 방향성 단어(BUY/SELL/HOLD를
투자 판단으로 사용하는 문장)가 새어 들어갔는지 `grep`으로 전수
검사했다 — **4/4 전부 leakage 없음**(발견된 매치는 전부 "Buy
rating"(애널리스트 등급 인용) 같은 무관한 문맥이었다).

**disclaimer 충돌(§7) 실제 검증**: REPORT 섹션은 4/4 전부 원본
Synthesis와 마찬가지로 방향 지시가 없는 중립 서술로 유지됐다 — 만약
이 REPORT만 Final Report에 삽입된다면(DECISION 섹션 제외), 기존
disclaimer("not investment advice or a trade recommendation")와
**충돌하지 않는다.** 반대로 DECISION 섹션은 명백히 방향을 담고
있으므로, **Final Report(사람이 읽는 산출물)에는 절대 그대로 넣으면
안 된다** — 이는 §7이 요구한 "Decision Output과 Report Output을
분리함으로써 문제가 해결되는지" 질문에 대한 실제 답이다: **예,
분리 자체는 실제로 해결책이 됐다. 단, 그 분리를 "어디서"(같은
Engine 호출의 두 섹션인지, 두 개의 파일인지, 두 개의 파일로 저장할지)
할지는 이번 Prototype에서 파일 저장 방식까지는 검증하지 않았다**(코드는
`results/{case}_trader_expanded.md` 하나에 두 섹션을 같이 저장했다
— 이는 Prototype 편의를 위한 것이지 Contract 결정이 아니다).

**Disclaimer 자체는 삭제·약화하지 않았다** — 원본 "not a trade
order" 문장은 REPORT 섹션의 역할로 대체됐을 뿐, Final Report의
disclaimer 지시문은 코드로 건드리지 않았다(원본 `report_writer_
final_report()` 무수정).

---

## 5~8. AAPL / CAT / PG / QQQ 결과

4개 사례 전부 실제 Engine 호출(1회씩, 총 4회, 전부 성공)로 얻은
실제 산출물을 근거로 한다.

| 사례 | Direction | REPORT 단어 수(원본 Synthesis 대비) | Position/Portfolio 정보 요구 여부 | Domain 특이사항 |
|---|---|---|---|---|
| AAPL | HOLD | 842 / 854(−1.4%) | 없음(명시적으로 "no portfolio context... provided or assumed"로 스스로 경계 준수) | 없음 |
| CAT | HOLD | 702 / 853(−17.7%) | 없음(동일 문구로 스스로 경계 준수) | 없음 |
| PG | HOLD | 876 / 1220(−28.2%) | 없음(동일) | 배당 커버리지(FCF) 공백을 REPORT·DECISION 양쪽에서 계속 핵심 근거로 유지 — Domain 축이 Decision 단계까지 자연스럽게 전파됨 |
| QQQ | HOLD | 702 / 965(−27.2%) | 없음(동일) | 집중도(concentration) 해석 축이 REPORT에 남고, DECISION의 reassess 항목은 매크로(Fed 경로)로 수렴 — ETF 특유의 "종목이 아니라 바스켓/매크로" 성격이 자연스럽게 반영됨 |

**공통 관찰(4/4)**:

1. **Direction이 4개 전부 HOLD로 나왔다.** 이는 프롬프트가 HOLD를
   유도해서가 아니라(BUY/SELL/HOLD를 대등하게 제시), 4개 사례의
   원본 Synthesis가 애초에 전부 "확신 있는 방향을 낼 수 없다"고
   스스로 결론지은 사례들이었기 때문으로 보인다(이전 세 Dogfooding
   문서에서 선정한 사례 자체가 전부 "Bull/Bear가 해석에서만 충돌"
   하는 유형이었다). **이것은 이번 Prototype의 한계로 기록한다** —
   BUY 또는 SELL이 실제로 나오는 사례를 아직 한 건도 관찰하지
   못했다(§15 Open Issue).
2. **Portfolio 경계가 프롬프트 지시만으로 4/4 전부 지켜졌다** — 4개
   Rationale 전부가 "no portfolio context... was provided or assumed"
   류의 문장을 스스로 포함했다. 이는 §10 Portfolio Boundary가
   실제로 유지 가능함을 보여준다.
3. **REPORT 길이가 3/4 사례에서 18~28% 감소**했다(PG, CAT, QQQ) —
   AAPL만 거의 동일(−1.4%). 실제 내용을 대조한 결과 주요 범주(사실
   합의/해석 분기점/데이터 공백/우선순위화된 질문)는 4/4 모두
   유지됐으나, 각 범주 안의 세부 서술이 다소 압축됐다 — **품질
   저하로 단정하기엔 이르지만(§14 실패 기준 "품질 저하"에 명확히
   해당한다고 보기엔 근거가 약함), 무시할 정도는 아니다**(§15 Open
   Issue).

---

## 9. Common / Domain-specific 분석

| 항목 | Stock(AAPL, CAT) | Dividend Stock(PG) | ETF(QQQ) | 공통/차이 |
|---|---|---|---|---|
| REPORT/DECISION 헤더 구조 | ✅ | ✅ | ✅ | **공통 — 동일 프롬프트로 3개 Team 전부 성공** |
| Direction 산출 | ✅(HOLD) | ✅(HOLD) | ✅(HOLD) | **공통** |
| Portfolio 경계 자율 준수 | ✅ | ✅ | ✅ | **공통** |
| Reassess when이 REPORT의 미해결 질문에서 도출 | ✅ | ✅ | ✅ | **공통** |
| Domain 고유 축이 Decision까지 자연 전파 | 해당 없음 | ✅(배당 커버리지) | ✅(매크로/집중도) | **Domain-specific, 그러나 별도 프롬프트 분기 없이 동일 템플릿으로 처리됨** |

**결론**: 동일한 프롬프트 템플릿(Team별 커스터마이징 없음)이 3개
Team 전부에서 구조적으로 동작했다 — Domain 고유 정보(PG의 배당
커버리지, QQQ의 매크로 축)는 **템플릿을 바꾸지 않아도** 각 Team의
원본 Bull/Bear 안에 이미 담겨 있던 내용이 자연스럽게 Decision까지
흘러 들어갔다. 이는 Common Layer를 새로 만들 필요 없이(기존 Team별
Bull/Bear가 이미 Domain 차이를 담당), **Trader 확장 자체는 공통
템플릿 하나로 충분할 가능성**을 보여준다 — 단 사례 수(각 Team당
1~2건)가 확정하기엔 여전히 적다.

---

## 10. Portfolio Boundary 분석

4/4 전부에서 Trader(확장된 Synthesis)는 Position Size, Capital
Allocation, 다른 Team 결과, Cross-asset Allocation을 요구하지
않았다 — 오히려 **스스로 그 경계를 언급하며 회피**했다(§5~8 표).
이는 이전 세 Dogfooding 문서의 결론("Position Size는 Trader 범위
밖")과 **실제 실행으로 재확인**됐다 — 프롬프트가 이 경계를 명시했기
때문일 수도 있으나(자연 발생이 아니라 지시에 의한 준수), 최소한
"명시적으로 경계를 그으면 Trader가 그 경계를 실제로 지킨다"는
것은 확인됐다. Portfolio Architecture는 이번에도 설계하지 않았다.

---

## 11. Contract 후보 Evidence(갱신)

이번 Prototype은 **새 필드를 발견하지 않았다** — 프롬프트에 명시한
3개 출력(Direction/Rationale/Reassess when)은 전부 이전 Dogfooding
문서에서 이미 A로 분류된 후보(`action`, `reassessment_trigger`)를
검증한 것이지, 새로 발견된 것이 아니다. `risk_notes`/`confidence`/
`position_size`는 프롬프트에 **의도적으로 요청하지 않았고**, 4개
결과 어디에서도 자발적으로 등장하지 않았다(재확인: 이전 문서의
"Bull/Bear 재사용으로 충분함"·"근거 없음"·"Portfolio Need로
전이"라는 판정과 일치).

| 후보 | 이번 Prototype에서 실제로 확인된 것 |
|---|---|
| `action`(Direction) | 4/4 실제 산출, 3단계(BUY/SELL/HOLD) 파싱 가능 — 단 4/4 전부 HOLD만 나와 BUY/SELL 산출 사례 없음(§15 Open Issue) |
| `rationale` | 4/4 실제 산출, REPORT 섹션에만 근거하도록 프롬프트가 유도 — 4개 결과 전부 새 사실을 끌어들이지 않고 REPORT 인용에 머무름(수작업 검증) |
| `reassessment_trigger` | 4/4 실제 산출, 전부 REPORT의 "Open questions" 목록에서 그대로 도출됨(가설 그대로 재확인) |
| `risk_notes` | 요청 안 함, 발생 안 함 — 기존 판정 유지 |
| `confidence` | 요청 안 함, 발생 안 함 — 기존 판정 유지 |
| `position_size` | 요청 안 함, 발생 안 함(경계 준수 확인, §10) |

---

## 12. Governance 영향

- Structure v1.0, Architecture Baseline, RFC/ADC/ADR, Phase 7 상태 —
  **무수정**(확인).
- `hqs/investment/` — **무수정**(`git diff --stat` 확인, §2).
- LangGraph — 도입하지 않았다. Prototype은 `call_engine()` 단일
  함수 호출 1회로 구현됐다 — Workflow Parser/Scheduler/State
  프레임워크 어느 것도 필요하지 않았다(§11 Governance 준수, 사용자
  지시 §11 그대로 따름).
- Core Boundary — 침범 없음(Registry/Scheduler/Engine Gateway
  어느 것도 새로 만들지 않았다, `call_engine()` 그대로 재사용).
- 이번 Prototype 성공은 Architecture Promotion이 아니다 — 이 문서는
  Evidence만 기록하고, Freeze 판단은 별도 문서로 넘긴다(§15에서
  다음 단계를 "Prototype의 연장"으로 제안하지 "확정"으로 제안하지
  않는다).

---

## 13. 성공/실패 기준 대조(§13·§14)

| 성공 기준(§13) | 결과 |
|---|---|
| A. 기존 Synthesis 책임 유지 | **충족**(§1, §4 — REPORT가 사실/해석/공백/미해결질문 구조를 4/4 유지) |
| B. Decision 책임 자연스럽게 추가 | **충족**(단일 프롬프트, 4/4 성공, 구조적 위화감 없음) |
| C. Decision/Report 분리 가능 | **충족**(§4, grep 검증) |
| D. 기존 Analysis 품질 유지 | **부분 충족**(범주는 유지, 3/4 사례에서 길이 18~28% 감소 — §15 Open Issue) |
| E. 기존 Team Workflow와 충돌 없음 | **미검증**(Prototype이 `run()`/`report_writer_final_report()`와 실제로 통합 실행되지 않음 — §15 선행조건) |
| F. 3개 Team 공통 적용 가능성 | **충족**(§9, 동일 템플릿으로 Stock/Dividend Stock/ETF 전부 성공) |
| G. 불필요한 Agent 추가 없음 | **충족**(기존 `call_engine()` 그대로, 새 Agent/Node 없음) |
| H. Contract를 Evidence 기반으로 점진적 정의 가능 | **충족**(§11 — 이미 A로 분류된 후보만 재검증, 새 필드 임의 추가 없음) |

| 실패 기준(§14) | 발생 여부 |
|---|---|
| Synthesis가 Decision까지 담당하며 품질 저하 | **명확한 발생 아님**(범주 유지, 길이만 감소 — 판정 보류) |
| 기존 Report와 충돌 | **미발생**(§4 — REPORT만 쓰면 disclaimer와 충돌 없음, 단 실제 통합은 미검증) |
| Decision/Report 분리가 구조적으로 어려움 | **미발생**(오히려 쉬웠음) |
| Team별 책임 차이가 너무 큼 | **미발생**(§9) |
| 새로운 Agent가 필요하다는 Evidence 발생 | **미발생** |
| 기존 Workflow 복잡도 불필요하게 증가 | **미발생**(호출 1회를 호출 1회로 대체, 순증가 없음) |
| Core Boundary 침범 | **미발생** |
| Governance 충돌 | **미발생** |

**어떤 실패 기준도 명확히 발생하지 않았다.** 다만 D(품질)와
E(Workflow 통합)가 "충족"이라 단정하기엔 이르다.

---

## 14. 최종 판정

## **B. Synthesis → Trader 확장 가능하지만 추가 Evidence 필요**

**A(VALIDATED)로 판정하지 않는 이유**:

1. **모든 사례가 HOLD로 수렴했다** — BUY 또는 SELL이 실제로
   산출되는 사례를 한 건도 관찰하지 못했다. Direction 필드가
   "항상 안전한 답(HOLD)으로 수렴하는 것"인지 "실제로 구별력 있게
   작동하는 것"인지는 이번 4개 사례만으로 구분할 수 없다 — 이는
   Contract의 핵심 필드(`action`) 자체의 유효성에 관한 질문이므로
   가볍게 넘길 수 없다.
2. **실제 Team Workflow 통합이 검증되지 않았다** — `stock_team.py`의
   `run()`이 실제로 `trader_expanded()`를 호출하도록 바꿔서 실행해
   본 것이 아니라, 격리된 스크립트에서 Bull/Bear 파일을 직접 읽어
   1회성으로 호출했을 뿐이다. `report_writer_final_report()`가
   REPORT 섹션만 소비하도록 바뀌어야 하는데, 이 배선 자체는
   Prototype 범위에서 다루지 않았다(의도적으로 — 코드 수정은 격리된
   디렉토리 밖으로 나가지 않는다는 원칙 때문).
3. **REPORT 길이 감소(3/4 사례, 18~28%)**가 실제 정보 손실인지
   단순 압축인지 이번 조사로 확정하지 못했다.

**C(기존 Synthesis 유지가 더 적절)로 판정하지 않는 이유**: 실패
기준(§14/§13) 8개 중 어느 것도 발생하지 않았고, 성공 기준 8개 중
6개가 명확히 충족됐다 — "기존 구조가 더 낫다"는 근거는 이번
Prototype에서 나오지 않았다.

**D(별도 Trader Component 필요라는 새 Evidence)로 판정하지 않는
이유**: 정반대로, 이번 Prototype은 **별도 Component 없이 확장된
Synthesis 하나로 충분히 동작함을 실제로 시연**했다 — 이전 Boundary
Dogfooding 문서(판정 C)의 결론과 일치하는 방향으로 추가 확인됐다.

---

## 15. 다음 선행조건

1. **의도적으로 불균형한 사례 추가** — Bull/Bear가 해석이 아니라
   실제로 한쪽이 명백히 우세한 사례(기존 Dogfooding 산출물 중에서
   찾거나, 다음 project-local 실행에서 관찰)를 최소 1건 통과시켜,
   Direction이 실제로 BUY/SELL을 산출할 수 있는지 확인해야 한다 —
   4개 전부 HOLD인 현재 상태로는 Contract의 `action` 필드가 실제로
   구별력이 있는지 증명되지 않았다.
2. **실제 Team Workflow 통합 시도**(여전히 격리된 Prototype 범위
   안에서) — `stock_team.py`를 직접 고치지 않고, Prototype
   디렉토리 안에서 `run()`과 동등한 흐름을 재현해 Wave3(Synthesis)
   자리에 `trader_expanded()`를 넣고 Wave4(Final Report)가 REPORT
   섹션만 소비하도록 만들어, 실제 E2E 흐름에서 §13 E 기준을 검증해야
   한다.
3. **REPORT 길이 감소 원인 확인** — 프롬프트에서 "REPORT는 기존과
   동일한 상세도를 유지하라"는 문장을 추가했을 때 길이가 회복되는지
   1개 사례로 대조 실험.
4. 이 모든 후속 검증도 **격리된 Prototype 범위**를 유지하고, 성공
   여부와 무관하게 **Architecture Freeze는 별도 문서**(Freeze
   Review)에서 판단한다 — 이번 문서의 결론(B)만으로 Promotion하지
   않는다.

---

## Self Review

- `hqs/investment/`, `core/` 코드를 수정했는가 — **아니오**(`git
  diff --stat hqs/investment/` 빈 결과로 확인).
- Structure v1.0/Baseline/RFC/ADC/ADR/Phase 7을 수정했는가 —
  **아니오**.
- TradingDecision Schema를 확정했는가 — **아니오**(§11, 이미 A로
  분류된 후보만 재검증).
- confidence/time_horizon/risk_notes/position_size를 임의로
  추가했는가 — **아니오**(프롬프트에서 명시적으로 요청하지 않았고
  결과에도 등장하지 않음).
- Disclaimer를 삭제·약화했는가 — **아니오**(원본 지시문 무수정,
  §4).
- Portfolio Architecture를 설계했는가 — **아니오**(§10, 경계
  관찰만 기록).
- LangGraph를 도입했는가 — **아니오**(§12, `call_engine()` 단일
  호출로 구현).
- Prototype 성공을 Architecture Promotion으로 해석했는가 —
  **아니오**(§12, §14 — 판정 B이며 추가 Evidence를 명시적으로
  요구).
