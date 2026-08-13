# Stock Analysis — JPM

Investment HQ / Stock Dogfooding의 네 번째 실행이자, `docs/research/STOCK-TEAM-DEFINITION-0001.md`
승격 이후 첫 실행이다. 목적은 JPM 분석 자체가 아니라 **Stock Team의 8개
업무(Fundamental/Technical/Industry-Competition/News-Event/Sentiment/
Bull-Bear/Synthesis/Final Report)를 역할 분리 상태로 반복 수행해, 각 역할을
독립 Agent로 승격해야 할 만큼 반복성·독립성이 있는지 Evidence를 확보**하는
것이다. 새 Agent를 만드는 것이 이번 실행의 목적이 아니다.

AAPL/NVDA/MSFT(소비자 하드웨어/AI 반도체/기업용 SW+클라우드)와 다른 산업
(금융/투자은행)의 실제 기업(JPMorgan Chase, JPM)을 대상으로 선정했다 —
기존 3회 실행의 산업 다양성 한계를 부분적으로 보완하는 부차적 이점이며,
이번 실행의 주 목적은 아니다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `stock-analysis-aapl`/`nvda`/`msft`와 사실상
동일한 구조다(코드는 공유하지 않음 — project-local 원칙). `raw_data.md`
(이 세션이 WebSearch로 직접 수집한 실제 JPM 자료)를 입력으로 5개 전문 분석
→ Bull Case/Bear Case → Synthesis → Final Report를 실제 Engine
(`call_engine`)으로 순서대로 실행한다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## AAPL/NVDA/MSFT와의 차이

- `runner.py`는 AAPL에서 검증된 `_COMPANY_HEADER` 프리픽스 수정을 그대로
  재사용한다.
- 이번 실행만 추가로 각 `call_engine()` 호출의 입력 길이/출력 길이/소요
  시간을 `issues/0001-jpm-analysis/call_log.json`에 기록한다 — 새
  Contract가 아니라, 이번 Evidence 목적(역할/Agent 분리 필요성 검증)을
  위한 project-local 관찰 데이터다.

## 구조

`projects/stock-analysis-aapl/README.md`와 동일한 구조, 추가로
`issues/0001-jpm-analysis/call_log.json`(호출별 관찰 데이터).

## Out of Scope

`projects/stock-analysis-aapl/README.md`의 Out of Scope와 동일. 추가로:
- 새 Agent 실제 생성/등록, Stock Team 범위 밖 신규 Capability
- ETF/Dividend Stock Team

## Development HQ Update Policy

`projects/stock-analysis-{aapl,nvda,msft}`와 동일: 이 프로젝트에서 발견되는
문제는 즉시 Development HQ를 고치는 근거로 쓰지 않는다. Observe First,
Decide Later.
