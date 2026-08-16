# ETF Analysis — VNQ

Investment HQ의 다섯 번째 ETF Dogfooding이자 첫 리츠형(REIT) ETF 실행이다.
목적은 VNQ(Vanguard Real Estate ETF, MSCI US Investable Market Real
Estate 25/50 Index 추적) 분석 자체가 아니라, **QQQ(주식)·SCHD(주식)·
AGG(채권)·GLD(원자재)에서 확인된 ETF Team 6개 역할 구조가 리츠라는
다섯 번째 자산군에서도 반복되는지 검증**하는 것이다. 이는
`docs/research/ETF-TEAM-DEFINITION-0001.md`의 재평가 조건("원자재/리츠/
통화 등 다른 자산군에서도 이 범위가 반복되는지")에서 "리츠" 항목을
다룬다(GLD가 "원자재" 항목을 이미 다룸). ETF Team이나 Agent를 이
실행에서 선행 설계하지 않는다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `projects/etf-analysis-{qqq,schd,agg,gld}`와
코드를 공유하지 않는 별도의 project-local 구현이다. AGG/GLD와 동일한
6개 역할 구조(Composition/Index, Holdings/Exposure, Cost/Tracking,
Performance/Risk, Distribution, Macro → Bull Case/Bear Case →
Synthesis → Final Report, 총 10회 `call_engine()` 호출)를 그대로
유지했다 — 역할을 REIT에 맞춰 미리 재구성하지 않았다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## QQQ/SCHD/AGG/GLD와의 차이

- VNQ는 주식형 리츠 ETF로, GLD(소득 없음)와 정반대로 **소득(Income)
  창출이 펀드 목표에 명시적으로 포함**된다(분기 배당) — Distribution
  Analyst가 이 대조를 스스로 짚었다.
- 지수 방법론에 "25/50" 집중도 상한 규칙이 있음에도 상위 10개 종목이
  54.5%를 차지 — Holdings/Exposure Analyst가 "종목 수 대비 상당히
  높은 집중도"라고 자체 평가했다(AGG/GLD처럼 "개념이 무의미"가 아니라
  "구체적 수치로 집중도를 평가"한 첫 사례).
- 리스크 성격이 또 다르다 — 베타(주식)·듀레이션(채권)·상품가격
  리스크(금) 어디에도 속하지 않는 "금리에 민감한 실물자산" 복합
  리스크를 Performance/Risk Analyst가 스스로 설명했다.
- Bull/Bear 대립에서 처음으로 "사실 자체의 충돌"과 "동일 사실의 해석
  차이"를 Synthesis가 명시적으로 별도 섹션으로 구분했다(YTD/배당수익률/
  보유종목수 불일치는 전자, 25/50 방법론·섹터 순수성 99.45%는 후자).

## 구조

`projects/etf-analysis-agg/README.md`·`etf-analysis-gld/README.md`와
동일한 구조, 6개 분석 Capability.

## Out of Scope

`projects/etf-analysis-{qqq,schd,agg,gld}/README.md`의 Out of Scope와
동일. 여러 ETF의 동시/배치 처리도 이번 범위 밖이다.

## Development HQ Update Policy

`projects/stock-analysis-*`·`projects/etf-analysis-{qqq,schd,agg,gld}`
와 동일: 이 프로젝트에서 발견되는 문제는 즉시 Development HQ를 고치는
근거로 쓰지 않는다. Observe First, Decide Later.
