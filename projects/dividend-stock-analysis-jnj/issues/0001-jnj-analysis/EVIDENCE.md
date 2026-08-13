# Evidence — JNJ Dividend Stock Dogfooding (실행 1회차) — Stock 공통성/고유 역할 검증

PRD v1.2 관찰 항목 기준, Stock/ETF EVIDENCE.md와 동일한 형식. 이번 실행의
목적은 Stock Team의 5개 분석이 배당주에서도 그대로 유효한지, Dividend
Quality가 독립적인 역할로 실제 필요한지를 검증하는 것이다.

## 업무 (Task)

- 11단계 파이프라인(7개 분석 → Bull/Bear → Synthesis → Final Report)이
  수동 개입 없이 완주됐다.
- `call_log.json` 실측: 11회 호출 합계 414.1초 — JPM(Stock, 313초)보다
  길고 QQQ/SCHD(ETF, ~400초)와 비슷했다. 분석 축이 5개→7개로 늘어난
  것이 JPM 대비 소요시간 증가의 직접적 원인으로 보인다(ETF가 7개
  분석일 때의 소요시간과 유사한 규모로 수렴).

## Stock과 공통인 역할은 무엇인가

**Fundamental/Technical/Industry-Competition/News-Event/Sentiment 5개
역할이 그대로 유효했다.** 지시문을 Stock과 거의 동일하게 유지한 채
실행했고, 5개 모두 실제로 유의미한 산출물을 만들어냈다:

- **Fundamental**: JPM과 동일하게 GAAP vs 조정 EPS 괴리(JNJ: $2.27 vs
  $2.90, 약 22%차)를 스스로 지적 — Stock 4사에서 반복된 "헤드라인
  수치와 조정 수치의 괴리 인정" 패턴이 5번째로도 재현.
- **Technical**: 소스 간 이동평균·RSI 수치 불일치(RSI 64.566 vs
  55.45)를 자기인정 — JPM의 RSI/저항선 근접 신호와 유사한 유형의
  자기인정.
- **Industry-Competition**: "면역학에서 AbbVie가 강력한 경쟁자로
  지목됨"을 스스로 "JNJ가 방어적 위치에 있을 수 있음을 시사하는 언어"
  라고 해석 — NVDA/JPM Industry Analyst의 자발적 비판 패턴과 동일한
  성격.
- **News/Event**: $5.5B 탈크 합의라는 정성적 이벤트를 다뤘고, 이것이
  재무 가이던스에 미치는 영향이 자료에 없다는 공백을 스스로 명시 —
  JPM의 Dimon 발언 분석과 동일한 구조(이벤트를 다루되 재무적 영향은
  자료 범위 밖으로 명시).
- **Sentiment**: 목표주가(중위값 $210.02, 평균 $238.2)가 현재가
  ($259.24)보다 낮다는, Stock 4사에서 없던 새로운 유형의 불일치를
  발견 — "목표주가 소스 간 수치 불일치"(QQQ/SCHD/AGG)에서 한 걸음 더
  나아가 "목표주가 자체가 이미 낡았을 가능성"까지 스스로 추론.

**결론: Stock의 5개 분석 역할은 배당주에서도 지시문 변경 없이 그대로
유효했다.** 이는 QQQ/SCHD/AGG(ETF)에서 Stock의 5개 역할이 전혀
재사용되지 않았던 것과 대조적이다 — **Dividend Stock은 Stock의 하위
유형(같은 "개별 종목" 자산군)이므로 기존 5개 역할이 그대로 재사용
가능했고, ETF는 자산군 자체가 달라 재사용되지 않았다**는 구분이 이번
실행으로 명확해졌다.

## Dividend Quality가 독립적인 역할로 반복되는가

**1회 실행이므로 아직 반복은 아니지만, 독립적 역할로서의 근거는
뚜렷하다.** Dividend Quality Analyst는 다른 6개 역할 어디에도 없는
고유한 관찰을 만들어냈다:
- 배당성향(Payout Ratio) 84%→46.19% 변화의 회계적 근거(GAAP vs 조정
  기준, 일회성 항목 여부)가 자료에 없다는 공백을 독자적으로 지적.
- 경영진의 "배당 인상을 FCF 전망에 연동"이라는 방침을, 발행주식수·
  총배당지급액 부재로 인해 "수치로 재검증되지 않은 인용"이라고 스스로
  한계를 명시 — Fundamental Analyst의 EPS 분석과는 다른 각도(현금흐름
  기반 커버리지)에서 접근.
- Bull/Bear Synthesis가 이 배당성향 개선을 "구조적 개선"(Bull) vs
  "전년도 소송충당금 등 일회성 요인의 착시"(Bear)로 정반대 해석했다 —
  Dividend Quality Analyst가 제기한 공백이 실제로 Bull/Bear 대립의
  핵심 소재가 됨.

Fundamental Analyst도 EPS/매출 추세를 다루지만 "배당의 지속가능성"이라는
질문에는 답하지 않는다 — 이 둘의 역할 경계가 실제로 겹치지 않음을
확인했다.

## 밸류에이션이 별도 분석 축을 요구하는가

**그렇다, 확인됐다.** Valuation Analyst가 P/E 수치의 3중 불일치
(16.9배/27.61배/29.7배)와 DCF vs P/E 배수 간 상반된 신호("valuation
tug of war")를 독자적으로 발견했다. 이는 Fundamental(실적 추세)이나
Sentiment(애널리스트 목표주가)와는 다른 질문("현재 가격이 실적 대비
싼가 비싼가")에 답하는 역할로, 다른 6개 역할과 실제로 구분되는 관점을
냈다.

## Bull/Bear/Synthesis가 반복되는가

**그렇다, 5회 연속(누적 기준).** Synthesis가 이번에도 "**사실 자체의
분쟁은 거의 없다**"고 명시했다 — JPM→QQQ→SCHD→AGG→JNJ로 5회 연속
동일한 결론 유형이 재현됐다(Stock 2건 + ETF 3건). Bull/Bear가 갈리는
지점의 구조도 동일했다: 같은 사실(배당성향 개선, 애널리스트 등급
구성, 파산절차 기각)을 두고 정반대로 해석하는 패턴.

**새로운 데이터 이상치**: 목표주가(최고 $240)보다 현재가($259.24)가
높다는 사실을 Bull/Bear/Synthesis 3개 역할 모두가 독립적으로 포착하고
"가장 명확한 하나의 데이터 포인트"로 취급했다 — AGG의 AA/AAA 신용등급
모순처럼, 여러 역할이 같은 이상치를 교차 검증한 두 번째 사례.

## Stock/ETF와 Capability 공유가 실제 필요한가

**Stock과는 필요가 확인됐다(5/5 역할 재사용).** ETF와는 여전히 필요가
없다 — 이번 JNJ 실행도 ETF의 6~7개 분석 축(Composition, Holdings/
Exposure, Cost/Tracking 등)을 전혀 사용하지 않았고, JNJ의 Dividend
Quality/Valuation도 ETF 쪽에서 재사용되지 않았다. **Stock과 Dividend
Stock 사이의 Capability 공유 필요성은 이번 실행에서 실제로 확인된
첫 사례**이며, 지금 코드 수준의 공유는 시도하지 않았다(project-local
원칙 유지 — 지시문 패턴만 유사하게 따라했을 뿐, import는 없음).

## Context/실행시간/Cache/Runtime 요구

- Context 규모: 5개 공통 분석의 입력 크기(954~1,089자)가 JPM(684~947자)
  보다 약간 크고 QQQ/SCHD/AGG(872~1,180자)와 비슷한 범위 — Dividend
  Quality/Valuation 2개 추가로 전체 파이프라인이 ETF와 유사한 규모로
  수렴했다.
- Final Report: 입력 46,243자, 출력 17,370자, 소요 67.6초 — AGG
  (입력 40,657자, 출력 16,943자, 67.6초와 거의 동일한 소요시간)와
  비교해 "출력 길이가 소요시간과 더 강하게 연관된다"는 기존 가설과
  일치한다(출력이 AGG보다 조금 더 컸고 소요시간도 거의 동일).
- Cache: 발생하지 않음(11개 호출 전부 서로 다른 데이터).
- 병렬 실행: 이번에도 단일 종목만 다뤄 "다중 종목 동시 처리"는 발생
  하지 않았다 — 미검증 상태 유지.
- Runtime/Automation: 발생하지 않음. 1회성 수동 WebSearch로 충분했다.

## AGG의 Data Boundary 이탈이 재현되는가

**재현되지 않았다.** 11개 산출물 전체를 "AGG/SCHD/QQQ/JPMorgan/
Nasdaq-100/Bloomberg U.S. Aggregate" 등 다른 프로젝트 고유 키워드로
grep 검색한 결과, 실제 교차 참조는 발견되지 않았다(매칭된 것은 전부
"flagged"라는 단어에 우연히 포함된 "agg" 문자열 등 false positive였다).
raw_data.md에도 다른 프로젝트를 교차 언급하는 문구를 이번에는 넣지
않았다(SCHD 실행에서는 의도적으로 QQQ를 언급했으나, 이번 JNJ에서는
넣지 않음 — 조건이 다르므로 직접 비교는 제한적). **AGG의 이탈 사례가
매 실행마다 반복되는 현상은 아니라는 것을 1건의 반례로 확인했다** —
1/2(AGG에서 발생, JNJ에서 미발생)로, 반복 패턴이라 단정할 근거는
아직 없다.

## 시스템 (System)

- Stop Trigger 미발동. Kernel/Registry/Scheduler 확장 불필요함이 Stock
  도메인 5번째 실행에서도 재확인됐다.
- 출력 언어: 11개 산출물 중 Dividend Quality/Valuation/Sentiment 3개가
  한국어, 나머지 8개는 영어 — 4번째 "단일 실행 내 혼재" 사례(MSFT,
  QQQ, AGG에 이어). 8회 누적 기준으로도 언어 패턴은 여전히 비결정적.

## 관찰되지 않은 것 (명시적으로 기록)

- 여러 배당주의 동시/배치 처리 — 시도되지 않음.
- Dividend Quality/Valuation이 실제로 독립 Agent로 승격되어야 할
  근거(공유 재사용 등) — 1회 실행이므로 미확정.
- AGG의 Data Boundary 이탈이 반복 패턴인지 — 1/2로 아직 판단 불가.
