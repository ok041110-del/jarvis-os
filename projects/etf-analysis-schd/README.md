# ETF Analysis — SCHD

Investment HQ의 두 번째 ETF Dogfooding이다. 목적은 SCHD(Schwab U.S.
Dividend Equity ETF, Dow Jones U.S. Dividend 100 Index 추적) 분석 자체가
아니라, **첫 ETF 실행(QQQ)에서 확인된 ETF 업무 구조가 완전히 다른 성격의
ETF에서도 반복되는지 검증**하는 것이다. ETF Team이나 Agent를 이 실행에서
선행 설계하지 않는다.

QQQ(기술 성장주 집중, 배당수익률 0.42%)와 의도적으로 대조되는 배당/
가치주 ETF(헬스케어·필수소비재·에너지 중심, 배당수익률 ~3%)를 선정했다
— 상위 보유종목이 QQQ와 거의 겹치지 않는다(QQQ: NVIDIA/Apple/Microsoft,
SCHD: Abbott/UnitedHealth/Merck).

## 무엇을 하는가

`agents.py`/`runner.py`는 `projects/etf-analysis-qqq`와 코드를 공유하지
않는 별도의 project-local 구현이지만, QQQ와 동일한 7개 분석(Composition/
Holdings/Cost/Performance/Exposure/Distribution/Macro) → Bull Case/Bear
Case → Synthesis → Final Report 구조를 재사용한다(총 11회 `call_engine()`
호출) — 이는 "ETF 고유 역할이 반복되는지"를 검증하는 것 자체가 이번
실행의 목적이기 때문이다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## QQQ와의 차이

- `raw_data.md`의 Macro 섹션에 QQQ의 Macro 자료를 의도적으로 교차
  언급하는 문구를 포함시켜, 서로 다른 ETF 실행 간 Context 참조 여부를
  관찰했다(`issues/0001-schd-analysis/EVIDENCE.md` 참조).
- QQQ와 동일하게 `call_log.json`으로 입력/출력/소요 시간을 계측한다.

## 구조

`projects/etf-analysis-qqq/README.md`와 동일한 구조.

## Out of Scope

`projects/etf-analysis-qqq/README.md`의 Out of Scope와 동일. 추가로
QQQ·SCHD 두 ETF의 동시/배치 처리도 이번 범위 밖이다(순차적으로 별도
실행됨).

## Development HQ Update Policy

`projects/stock-analysis-*`·`projects/etf-analysis-qqq`와 동일: 이
프로젝트에서 발견되는 문제는 즉시 Development HQ를 고치는 근거로 쓰지
않는다. Observe First, Decide Later.
