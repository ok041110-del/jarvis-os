# Stock Analysis — MSFT

Investment HQ / Stock Dogfooding PRD v1.2의 세 번째 실행이다. AAPL → NVDA →
MSFT로 동일 업무를 반복해, 공통 역할·Context·협업·데이터 요구사항이 세
번째 기업에서도 반복되는지 확인하는 것이 목적이다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `stock-analysis-aapl`/`stock-analysis-nvda`와
사실상 동일한 구조다(코드는 공유하지 않음 — project-local 원칙). `raw_data.md`
(이 세션이 WebSearch로 직접 수집한 실제 MSFT 자료)를 입력으로 5개 전문 분석 →
Bull Case/Bear Case → Synthesis → Final Report를 실제 Engine(`call_engine`)
으로 순서대로 실행한다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## AAPL/NVDA와의 차이

- AAPL에서 검증된 회사 식별 수정(`_COMPANY_HEADER`)을 그대로 재사용한다.
- 출력 언어를 강제하지 않는다 — AAPL(한국어)/NVDA(영어) 비일관성이 3번째
  실행에서도 재현되는지 그대로 관찰한다.

## 구조

`projects/stock-analysis-aapl/README.md`와 동일한 구조.

## Out of Scope

`projects/stock-analysis-aapl/README.md`/`projects/stock-analysis-nvda/README.md`의
Out of Scope와 동일. AAPL/NVDA와의 3사 비교 Evidence는
`issues/0001-msft-analysis/EVIDENCE.md`에 정리하며, 다른 두 프로젝트의
파일은 수정하지 않는다.

## Development HQ Update Policy

`projects/textkit`·`projects/notekeeper`·`projects/stock-analysis-aapl`·
`projects/stock-analysis-nvda`와 동일: 이 프로젝트에서 발견되는 문제는
즉시 Development HQ를 고치는 근거로 쓰지 않는다. Observe First, Decide
Later.
