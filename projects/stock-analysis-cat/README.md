# Stock Analysis — Caterpillar Inc. (NYSE: CAT)

Investment HQ / Stock Dogfooding의 다섯 번째 실행. 목적은 CAT 분석
자체가 아니라 **Stock Team의 5개 역할(Fundamental/Technical/
Industry-Competition/News-Event/Sentiment)이 기존 4건(AAPL/NVDA/MSFT
=기술주, JPM=금융주)의 산업 편중을 벗어난 산업재/중장비 제조업에서도
지시문 변경 없이 일반화되는지 검증**하는 것이다. 새 Agent/Role을
만드는 것이 이번 실행의 목적이 아니다.

경기순환 산업, 백로그(수주잔고) 지표, 관세 노출도 등 기술/금융과
완전히 다른 펀더멘털 구조를 가진 실제 기업(Caterpillar, CAT)을
대상으로 선정했다.

## 무엇을 하는가

`agents.py`는 `stock-analysis-{aapl,nvda,msft,jpm}`와 지시문이 한
글자도 다르지 않다(회사명만 교체). `runner.py`는 이번부터 **신규
표준 실행 패턴**(Dividend Stock Team에서 PR #80 검증·PR #81/82
프로덕션 적용, Stock Team에는 처음)을 적용한다:

1. **병렬화** — Wave1(5개 분석), Wave2(Bull/Bear) 동시 실행
2. **출력 최적화** — Report Writer instruction에 800~1200단어 제약
3. **Checkpointing** — 단계 완료 즉시 저장, 재실행 시 완료 단계 스킵
4. **180초 Timeout 안전장치** — `ENGINE_TIMEOUT_SECONDS` 상향 없음

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## AAPL/NVDA/MSFT/JPM과의 차이

- 산업: 산업재/중장비 제조업(경기순환) — 이전 4건과 산업 자체가
  다름(신규 Team 아님, Stock Team 그대로 재사용).
- 실행 패턴: 이전 4건은 순차 실행(`_timed` 단순 호출)이었으나, 이번은
  Wave 기반 병렬+Checkpointing 구조로 바뀌었다 — **AAPL/NVDA/MSFT/
  JPM의 `agents.py`/`runner.py`는 소급 수정하지 않았다.**

## 구조

`projects/stock-analysis-jpm/README.md`와 유사한 구조, `runner.py`
내부 실행 방식만 신규 표준 패턴으로 교체됐다.

## Out of Scope

`projects/stock-analysis-jpm/README.md`의 Out of Scope와 동일. 추가로:
- 새 Agent 실제 생성/등록, Stock Team 범위 밖 신규 Capability
- ETF/Dividend Stock Team

## Development HQ Update Policy

기존 Stock Dogfooding 프로젝트와 동일: Observe First, Decide Later.
