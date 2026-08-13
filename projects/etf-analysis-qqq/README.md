# ETF Analysis — QQQ

Investment HQ의 첫 ETF Dogfooding이다. 목적은 QQQ(Invesco QQQ Trust,
Nasdaq-100 추적) 분석 자체가 아니라, **Stock Team(4회 반복 검증됨)과
공통으로 필요한 업무/Capability가 ETF에서도 실제로 발생하는지, 그리고
ETF 고유의 새로운 요구사항이 있는지를 실제 실행으로 확인**하는 것이다.
ETF Team이나 Agent를 이 실행에서 선행 설계하지 않는다.

Stock Dogfooding 4회(AAPL/NVDA/MSFT/JPM) 중 3개 종목(NVDA/AAPL/MSFT)이
QQQ의 상위 보유종목과 실제로 겹친다 — Stock과 ETF 간 Context 중복이
실제로 발생하는지 관찰하기 좋은 조건이라 QQQ를 선정했다.

## 무엇을 하는가

`agents.py`/`runner.py`는 Stock 프로젝트들과 코드를 공유하지 않는
완전히 별도의 project-local 구현이다. `raw_data.md`(이 세션이 WebSearch로
직접 수집한 실제 QQQ 자료)를 입력으로 7개 전문 분석(Composition/Holdings/
Cost/Performance/Exposure/Distribution/Macro) → Bull Case/Bear Case →
Synthesis → Final Report를 실제 Engine(`call_engine`)으로 순서대로
실행한다(총 11회 호출).

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## Stock과의 차이

- Stock의 5개 분석(Fundamental/Technical/Industry/News-Event/Sentiment)을
  그대로 재사용하지 않았다 — ETF 고유의 7개 분석 축(구성/추적지수,
  보유종목/집중도, 비용/추적오차, 성과/변동성, 섹터/지역 노출, 분배금/
  배당, 시장/거시환경)을 새로 정의했다. 재사용 가능성은 이론이 아니라
  이번 실행 결과로 판단한다(`issues/0001-qqq-analysis/EVIDENCE.md` 참조).
- Bull/Bear/Synthesis/Final Report 4단계는 Stock과 구조적으로 유사한
  패턴을 사용했다(공유 코드 아님, 별도 작성).
- Stock과 동일하게 `call_log.json`으로 입력/출력/소요 시간을 계측한다.

## 구조

`projects/stock-analysis-aapl/README.md`와 유사한 구조, Capability
개수만 다르다(7개 분석 + Bull/Bear/Synthesis/Report = 11개).

## Out of Scope

- ETF Team/Agent 실제 생성/등록, Investment HQ Architecture 확정
- 새 Kernel Component, Runtime, Production caller, Prompt Cache
- 자동매매, 실거래
- 여러 ETF 또는 ETF 구성종목 단위의 병렬 처리(이번 실행은 QQQ 1개만
  다룬다)
- 정기/자동 데이터 갱신(Stock과 동일하게 이 세션이 WebSearch로 1회
  수동 수집)

## Development HQ Update Policy

`projects/stock-analysis-*`와 동일: 이 프로젝트에서 발견되는 문제는
즉시 Development HQ를 고치는 근거로 쓰지 않는다. Observe First, Decide
Later.
