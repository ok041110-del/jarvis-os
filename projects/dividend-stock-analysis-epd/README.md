# Dividend Stock Analysis — Enterprise Products Partners L.P. (NYSE: EPD)

기존 14건 Dogfooding(Stock: AAPL/NVDA/MSFT/JPM, ETF: QQQ/SCHD/AGG/
GLD/VNQ/UUP, Dividend Stock: JNJ/KO/PG/Nestlé/Toyota/Realty Income)과
중복되지 않는 신규 대상 — **MLP(Master Limited Partnership, 합자회사)**
개별 종목. 법적 형태 자체가 파트너십이라 "배당"이 아닌 "분배금
(distribution)", 표준 1099-DIV가 아닌 **Schedule K-1** 세금 서류,
배당성향 대신 **분배 커버리지 비율(DCR)** 지표를 쓴다 — 이전
6개 배당주(전부 법인, REIT 포함)에 없던 법적/세제 구조.

신규 표준 실행 패턴(PR #80에서 검증·채택, PR #81에서 Realty Income에
첫 프로덕션 적용)의 **2번째 프로덕션 적용**이다:

1. **병렬화** — 7개 분석(Wave1), Bull/Bear(Wave2) 동시 실행
2. **출력 최적화** — Report Writer instruction에 출력 길이 제약 반영
3. **Checkpointing** — 단계 완료 즉시 저장, 재실행 시 완료 단계 스킵
4. **180초 Timeout 안전장치** — `ENGINE_TIMEOUT_SECONDS` 상향 없음

Dividend Stock Team의 7개 역할·지시문은 한 글자도 바꾸지 않았다.

## 기존 완료 프로젝트와의 관계

**JNJ/KO/PG/Nestlé/Toyota/Realty Income의 `agents.py`/`runner.py`는
소급 수정하지 않았다.**

## Out of Scope

- Dividend Stock Team/Agent 실제 확장, Investment HQ Architecture 확정
- 새 Kernel Component, Runtime
- 자동매매, 실거래
- `development-hq/` 수정

## Development HQ Update Policy

기존 Dogfooding 프로젝트와 동일: Observe First, Decide Later.
