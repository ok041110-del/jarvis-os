# ETF Analysis — AGG

Investment HQ의 세 번째 ETF Dogfooding이다. 목적은 AGG(iShares Core U.S.
Aggregate Bond ETF, Bloomberg U.S. Aggregate Bond Index 추적) 분석 자체가
아니라, **QQQ(기술 성장주)·SCHD(배당 가치주)에서 확인된 ETF 업무 구조가
자산군 자체가 다른 채권형 ETF에서도 반복되는지 검증**해 3/3 Evidence를
확보하는 것이다. ETF Team이나 Agent를 이 실행에서 선행 설계하지 않는다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `projects/etf-analysis-{qqq,schd}`와 코드를
공유하지 않는 별도의 project-local 구현이다. 사용자 지시에 따라 QQQ/
SCHD의 7개 분석을 6개로 재구성했다: Composition/Index, Holdings·Exposure
(통합), Cost·Tracking(통합), Performance·Risk(통합), Distribution,
Macro → Bull Case/Bear Case → Synthesis → Final Report(총 10회
`call_engine()` 호출).

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## QQQ/SCHD와의 차이

- 자산군 자체가 다르다(채권 vs 주식) — "종목 집중도"라는 개념이 무의미
  해지고 대신 섹터/신용등급/만기 구조가 실질적 노출 지표가 된다는 것을
  Holdings/Exposure Analyst가 스스로 명시했다.
- 분석 축이 7개에서 6개로 재구성됐다(Holdings+Exposure 통합,
  Performance+Risk 통합) — 사용자 지시에 따른 것이며, 이 재구성 자체가
  "역할 경계를 다르게 그어도 Development HQ 패턴이 동작하는지"를
  관찰하는 대상이다.
- QQQ와 동일하게 `call_log.json`으로 입력/출력/소요 시간을 계측한다.

## 구조

`projects/etf-analysis-qqq/README.md`와 유사한 구조, 다만 분석 Capability
가 7개가 아니라 6개다(Holdings/Exposure, Cost/Tracking, Performance/Risk
통합).

## Out of Scope

`projects/etf-analysis-qqq/README.md`/`projects/etf-analysis-schd/README.md`
의 Out of Scope와 동일. 여러 ETF의 동시/배치 처리도 이번 범위 밖이다.

## Development HQ Update Policy

`projects/stock-analysis-*`·`projects/etf-analysis-{qqq,schd}`와 동일:
이 프로젝트에서 발견되는 문제는 즉시 Development HQ를 고치는 근거로
쓰지 않는다. Observe First, Decide Later.
