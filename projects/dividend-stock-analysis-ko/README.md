# Dividend Stock Analysis — KO

Investment HQ의 2번째 Dividend Stock Dogfooding이다(1차: JNJ,
`projects/dividend-stock-analysis-jnj/`). 목적은 KO(The Coca-Cola
Company) 분석 자체가 아니라, `docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0001.md`
§7이 요구한 반복성 검증 — Dividend Quality/Valuation 역할이 다른 산업의
배당주에서도 반복되는지, "Stock Team 확장 vs 독립 Team" 판단 근거를
확보하는 것이다. Dividend Stock Team이나 Agent를 이 실행에서 승격하지
않는다.

54년 연속 배당 증액(Dividend King)을 기록한 실제 배당주이며, JNJ(헬스케어/
제약)와 다른 산업(소비재/음료)이다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `projects/stock-analysis-*`, `projects/dividend-stock-analysis-jnj`와
코드를 공유하지 않는 별도의 project-local 구현이다(지시문 패턴만 JNJ와
동일하게 유지 — 공정한 반복 관찰을 위해). Stock의 5개 분석(Fundamental/
Technical/Industry-Competition/News-Event/Sentiment) + Dividend
Quality/Valuation 2개 = 7개 분석 → Bull Case/Bear Case → Synthesis →
Final Report(총 11회 `call_engine()` 호출) 구조를 쓴다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## JNJ와의 차이

- JNJ는 배당성향 46.19%(전년 84%에서 급락), KO는 77.24~80.1%로 소스 간
  다르지만 일관되게 높은 수준 — 배당성향 자체가 산업/기업마다 다른
  구간에 있음을 보여준다.
- JNJ 자료에는 DCF 내재가치 추정치가 있어 "이익 배수 vs DCF" 상반 신호를
  보였으나, 이번 KO 자료에는 DCF 추정치가 없어 그 비교가 불가능함을
  Valuation 분석이 스스로 명시하도록 raw_data.md에 기록해 두었다 —
  데이터 공백 자체가 산출물에 정직하게 반영되는지 관찰 대상이다.
- AGG에서 처음 관찰된 "Engine의 데이터 범위 이탈"의 재현 여부를 이번에도
  확인했다(`issues/0001-ko-analysis/EVIDENCE.md` 참조).

## 구조

`projects/dividend-stock-analysis-jnj/README.md`와 동일한 구조.

## Out of Scope

- Dividend Stock Team/Agent 실제 생성/등록, Investment HQ Architecture
  확정
- 새 Kernel Component, Runtime, Production caller, Prompt Cache
- 자동매매, 실거래

## Development HQ Update Policy

`projects/stock-analysis-*`·`projects/etf-analysis-*`·`projects/dividend-stock-analysis-jnj`와
동일: 이 프로젝트에서 발견되는 문제는 즉시 Development HQ를 고치는
근거로 쓰지 않는다. Observe First, Decide Later.
