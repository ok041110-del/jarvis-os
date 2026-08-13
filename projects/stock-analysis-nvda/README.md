# Stock Analysis — NVDA

Investment HQ / Stock Dogfooding PRD v1.2의 두 번째 실행이다. `projects/
stock-analysis-aapl`과 동일한 분석 업무를 다른 기업(NVIDIA, NVDA)에 반복
적용해, 역할/Context/협업/데이터 요구사항이 기업이 바뀌어도 반복되는지
확인하는 것이 목적이다. 이번에도 AAPL 분석 프로그램 자체 완성이 목적이
아니라 Development HQ의 반복 재사용성 검증이 목적이다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `projects/stock-analysis-aapl`과 사실상 동일한
구조다(코드는 공유하지 않음 — `textkit`/`notekeeper`처럼 프로젝트별로
독립적인 project-local 코드). `raw_data.md`(이 세션이 WebSearch로 직접
수집한 실제 NVDA 자료)를 입력으로 5개 전문 분석 → Bull Case/Bear Case →
Synthesis → Final Report를 실제 Engine(`call_engine`)으로 순서대로
실행한다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## AAPL과의 차이 (의도적으로 다르게 한 것)

- `raw_data.md` 자체에 섹션별로 회사명을 직접 적었다(AAPL 1차 실행에서
  발견된 회사 식별 누락 문제 재발을 관찰하기 위한 대조군).
- `runner.py`는 AAPL에서 검증된 `_COMPANY_HEADER` 프리픽스 수정을 처음부터
  포함한다(같은 문제를 또 발견해서 또 고치는 것이 아니라, 이미 검증된 수정을
  재사용).

## 구조

`projects/stock-analysis-aapl/README.md`와 동일한 구조
(`agents.py`/`runner.py`/`issues/0001-nvda-analysis/raw_data.md`,`*.md`,
`EVIDENCE.md`).

## Out of Scope

`projects/stock-analysis-aapl/README.md`의 Out of Scope와 동일. 추가로:
- AAPL과의 비교 Evidence는 `EVIDENCE.md`(이 프로젝트)와
  `../stock-analysis-aapl/issues/0001-aapl-analysis/EVIDENCE.md`를 교차
  참조해 별도 비교 문서로 정리하며, 이 프로젝트가 AAPL 프로젝트의 파일을
  수정하지는 않는다.

## Development HQ Update Policy

`projects/textkit`·`projects/notekeeper`·`projects/stock-analysis-aapl`과
동일: 이 프로젝트에서 발견되는 문제는 즉시 Development HQ를 고치는 근거로
쓰지 않는다. Observe First, Decide Later.
