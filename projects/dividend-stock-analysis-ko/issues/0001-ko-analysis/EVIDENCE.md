# Evidence — KO Dividend Stock Dogfooding (2번째 실행) — Dividend Stock 반복성 검증

`docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0001.md` §7이 요구한
"최소 1~2회 추가 배당주 실행"의 첫 회차다. JNJ(헬스케어/제약)와 다른
산업(소비재/음료)의 배당주로 Coca-Cola(KO)를 선정해, Stock/ETF/
Dividend Stock(JNJ) Team의 승격 기준을 그대로 적용해 반복성을 검증한다.

## 업무 (Task)

- 11단계 파이프라인(7개 분석 → Bull/Bear → Synthesis → Final Report)이
  수동 개입 없이 완주됐다.
- `call_log.json` 실측: 11회 호출 합계 356.4초 — JNJ와 동일한 11단계
  구조를 유지했고, 소요 시간대도 비슷한 범위(각 분석 단계 20~40초,
  Bull/Bear/Synthesis/Final Report 40~81초)다.

## Dividend Stock 고유 역할(Dividend Quality/Valuation) 2/2 반복 여부

**반복됐다.** JNJ에서 확인된 두 고유 역할이 KO에서도 다른 6개 역할과
겹치지 않는 독립적 관찰을 만들어냈다.

- **Dividend Quality Analyst**: 배당성향 77.24~80.1%(JNJ 46.19%와
  대조), FCF 커버리지 데이터 부재, 배당 연속 증액 연수 자체의 소스 간
  불일치(54년 vs 60+년)를 독자적으로 지적 — Fundamental Analyst(매출/
  마진 추세)와 역할이 겹치지 않음을 재확인.
- **Valuation Analyst**: P/E 프리미엄(피어 대비 60~113%)을 정량적으로
  제시하면서도, **JNJ와 달리 이번 자료에는 DCF 추정치가 없다는 사실
  자체를 데이터 공백으로 명시**했다("no DCF cross-check... This
  should be treated as a real limitation, not a minor omission") —
  JNJ의 "valuation tug of war"(DCF vs P/E 상반 신호)를 이번에는
  재현할 수 없다는 사실을 raw_data.md가 의도적으로 남긴 공백대로
  정확히 인식했다. Fundamental/Sentiment와 다른 질문(가격이 실적
  대비 싼가 비싼가)에 답하는 역할로 재확인.

**결론**: Dividend Quality/Valuation 역할이 2/2(JNJ, KO) 반복 확인됐다.

## Stock 5개 역할의 재사용 가능성 — 2/2 반복 여부

JNJ에서 처음 확인된 "Stock Team 5개 분석이 지시문 변경 없이 그대로
유효하다"는 관찰이 **KO에서도 그대로 반복됐다** — `agents.py`는 JNJ의
5개 함수(Fundamental/Technical/Industry-Competition/News-Event/
Sentiment)를 지시문 한 글자도 바꾸지 않고 그대로 재사용했고, 산출물
품질(공백 인식, 소스 간 불일치 지적)도 JNJ와 동일한 수준으로 나타났다.

**결론**: "Dividend Stock은 Stock Team의 확장(2개 역할 추가)에 가깝다"는
JNJ 관찰이 2/2로 반복됐다.

## 데이터 불일치 자기인정 패턴

JNJ와 동일한 성격으로 반복됐다: 배당 연속 연수(54 vs 60+), 목표주가
($80.83~$95.40, 18% 스프레드 — JNJ의 $28 스프레드와 유사한 유형), 기술적
지표(일간 RSI 76 vs 주간 61.23, 두 세트의 이동평균 수치 불일치), 배당성향
(77.24~80.1%) — 7개 분석 모두 소스 간 불일치를 은폐하지 않고 명시적으로
기록했다.

## Bull/Bear/Synthesis 구조 재검증

- Synthesis가 이번에도 사실 충돌과 해석 차이를 명확히 구분했다:
  "이 데이터 자체에 내재된 불일치"(배당 연수, 목표주가, 이동평균)와
  "동일 사실에 대한 상반된 해석"(가이던스 5% vs 실적 6%의 함의, 마진
  확대의 지속성, 밸류에이션 프리미엄의 정당성)을 별도 절로 분리 —
  JPM→QQQ→SCHD→AGG→JNJ→**KO로 6회 연속** "사실 충돌 없음, 순수 해석
  차이" 패턴이 재현됐다(Stock 1건 + ETF 3건 + Dividend Stock 2건).
- 추가로 Synthesis는 "Bull/Bear 둘 다 주장하지 않은, 산업 데이터 자체가
  스스로 지적한 방법론 문제"(KO 47.1% US CSD 점유율 vs PepsiCo 점유율
  수치의 카테고리 정의 불일치)를 별도로 식별했다 — 이는 AGG의
  AA/Treasury 신용등급 모순 자기지적과 같은 유형(데이터 자체가 스스로
  결함을 노출)의 반복이다.

## Data Boundary 재확인 — "JNJ 46.19%" 비교 수치의 흐름 추적

이번 실행은 AGG에서 관찰된 "Engine의 데이터 범위 이탈" 이슈를 의도적으로
재현 가능한 조건으로 설계했다 — `raw_data.md`의 `[DIVIDEND_QUALITY]`
섹션에 JNJ의 배당성향(46.19%)을 비교 수치로 **의도적으로 포함**시켜
두고(AGG의 `[PERFORMANCE_RISK]` 섹션이 SCHD 수치를 포함했던 것과 동일한
패턴), 이 수치가 다른 섹션(Fundamental/Valuation/Technical/Industry/
News/Sentiment)에 새어나가는지 전수 확인했다.

**결과**: `grep`으로 확인한 결과, "JNJ"/"Johnson" 언급은
`dividend_quality_analysis.md`, `valuation_analysis.md`(JNJ의 DCF 유무
비교, 이 역시 raw_data.md에 명시적으로 기록해 둔 내용), `bull_case.md`,
`bear_case.md`, `final_report.md`에만 나타났고, 전부 "dividend report에
인용된 비교 대상(comparator)"으로 정확히 귀속되어 서술됐다 —
`technical_analysis.md`, `industry_analysis.md`, `news_event_analysis.md`,
`sentiment_analysis.md`, `fundamental_analysis.md`에는 JNJ 언급이 전혀
없다. 즉 **JNJ 비교 수치는 원래 그 정보가 제공된 섹션(Dividend
Quality, Valuation)에서 파생된 산출물에만 정확히 국한되어 나타났고,
제공되지 않은 다른 섹션으로 새어나가지 않았다.**

이는 `docs/research/AGG-DATA-BOUNDARY-REPRODUCTION-0001.md`가 별도로
정리한 발견(AGG의 "데이터 범위 이탈" 관찰이 실제로는 Acquisition
단계에서 비교 수치를 섹션 안에 직접 기입한 것이었을 가능성)과 같은
방향의 추가 Evidence다 — 데이터가 섹션 경계 안에 정확히 스코프된 채로
제공되면, Engine은 그 경계를 실제로 지킨다는 것을 11회 호출 전수
확인으로 재확인했다.

## Cache / 병렬 실행 / Runtime 필요성

- Cache: 2/2(JNJ, KO) 미발생.
- 병렬 실행: 미발생 — 순차 단일 실행만 계속 검증됨.
- Runtime/Automation: 2/2 미발생. Stop Trigger 미발동.

## 시스템 (System)

- Stop Trigger 미발동. `agents.py`/`runner.py`는 JNJ와 동일한
  하드코딩된 순차 함수 호출 구조를 그대로 재사용했다 — Registry/
  Scheduler로 일반화되려는 압력 없음.
- 출력 언어: 11개 산출물 전부 영어로 일관됨(JNJ는 대부분 영어, 일부
  혼재 사례가 Stock/ETF에 있었음 — KO는 전량 영어로 이번 실행에서는
  비결정성이 관찰되지 않았으나, 표본이 1회뿐이라 이 사실만으로
  "언어 패턴이 결정적으로 바뀌었다"고 판단하지 않는다).

## Dividend Stock Team 승격 판단

**여전히 판단하지 않는다 — Promotion 여부는 Evidence로만 판단한다는
원칙에 따라, 이번 2회차 결과를 정리만 한다.** `docs/research/
DIVIDEND-STOCK-DOGFOODING-REVIEW-0001.md`는 Stock Team·ETF Team이
채택한 "3회 반복" 기준을 Dividend Stock에도 동일하게 적용해야 한다고
전제했다. 이번 실행으로 반복 횟수는 **2/3**이 됐다 — Stock/ETF Team이
승격을 확정했던 3회 반복 기준에는 아직 1회가 부족하다.

이번 KO 실행이 JNJ 대비 추가로 확인한 것:
- Dividend Quality/Valuation 역할의 필요성과 경계가 산업이 바뀌어도
  (헬스케어→소비재) 그대로 유지됨(2/2).
- Stock의 5개 역할이 지시문 변경 없이 재사용 가능하다는 것이
  1회에서 2회로 반복됨.
- "AGG Data Boundary" 우려가 Dividend Stock 트랙에서는 (의도적 재현
  시도에도 불구하고) 나타나지 않음 — 오히려 그 우려 자체의 원인
  소재에 대한 반증 Evidence를 추가로 제공함.

**Promotion 여부는 이 문서가 결정하지 않는다.** 3회째 실행(예: PG 등)이
이 저장소 밖의 후속 작업으로 남는다 — 이번 Validation의 범위는 반복
Evidence 확보까지다.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새 Agent, 새
Kernel Component, 새 Runtime, 새 Contract, 새 Cache를 만들지 않았다.
Dividend Stock Team/Agent를 선행 구현하지 않았다. Stop Trigger 미발동.
