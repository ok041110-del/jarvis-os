# Dividend Stock Analysis — JNJ

Investment HQ의 첫 Dividend Stock Dogfooding이다. 목적은 JNJ(Johnson &
Johnson) 분석 자체가 아니라, **Stock Team의 5개 분석이 배당주에서도
그대로 유효한지, Dividend Quality가 독립적인 역할로 실제 필요한지를
검증**하는 것이다. Dividend Stock Team이나 Agent를 이 실행에서 선행
설계하지 않는다.

64년 연속 배당 증액(Dividend King)을 기록한 실제 배당주이며, 기존
Stock Dogfooding 4사(AAPL/NVDA/MSFT/JPM — 기술/금융)와 다른 산업
(헬스케어/제약·메드텍)이다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `projects/stock-analysis-*`와 코드를 공유하지
않는 별도의 project-local 구현이다. Stock의 5개 분석(Fundamental/
Technical/Industry-Competition/News-Event/Sentiment)과 최대한 동일한
지시문 패턴을 유지하고, Dividend Quality·Valuation 2개를 새로 추가해
7개 분석 → Bull Case/Bear Case → Synthesis → Final Report(총 11회
`call_engine()` 호출) 구조를 쓴다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## Stock과의 차이

- Dividend Quality Analyst(배당 성장 트랙레코드/지급여력/지속가능성)와
  Valuation Analyst(밸류에이션 배수, 동종업계 비교)가 새로 추가됐다.
- Stock/ETF와 동일하게 `call_log.json`으로 입력/출력/소요 시간을
  계측한다.
- AGG에서 처음 관찰된 "Engine의 데이터 범위 이탈"이 이번에도 재현되는지
  확인했다(`issues/0001-jnj-analysis/EVIDENCE.md` 참조).

## 구조

`projects/stock-analysis-aapl/README.md`와 유사한 구조, Capability
개수만 다르다(7개 분석 + Bull/Bear/Synthesis/Report = 11개).

## Out of Scope

- Dividend Stock Team/Agent 실제 생성/등록, Investment HQ Architecture
  확정
- 새 Kernel Component, Runtime, Production caller, Prompt Cache
- 자동매매, 실거래

## Development HQ Update Policy

`projects/stock-analysis-*`·`projects/etf-analysis-*`와 동일: 이
프로젝트에서 발견되는 문제는 즉시 Development HQ를 고치는 근거로 쓰지
않는다. Observe First, Decide Later.
