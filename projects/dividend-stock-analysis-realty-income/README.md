# Dividend Stock Analysis — Realty Income Corporation (NYSE: O)

기존 13건 Dogfooding(Stock: AAPL/NVDA/MSFT/JPM, ETF: QQQ/SCHD/AGG/
GLD/VNQ/UUP, Dividend Stock: JNJ/KO/PG/Nestlé/Toyota)과 중복되지
않는 신규 대상 — 순임대(net lease) REIT 개별 종목. 월 배당(673회
연속), FFO/AFFO 기준 밸류에이션, REIT 세법상 의무배당 구조라는,
이전 5개 배당주(전부 일반 기업)에 없던 특성을 가진다.

**이번 실행부터 PR #80에서 검증·채택된 신규 표준 실행 패턴을 적용한
첫 프로덕션 Dogfooding이다:**

1. **병렬화** — 7개 분석(Wave1), Bull/Bear(Wave2)를 동시 실행
2. **출력 최적화** — Report Writer instruction에 800~1200단어 길이
   제약 반영(agents.py에 처음부터 포함, 섹션/데이터 불일치 플래그는
   유지)
3. **Checkpointing** — 단계 완료 즉시 `issues/0001-realty-income-analysis/
   checkpoints/`에 저장, 재실행 시 완료 단계는 Engine 재호출 없이 스킵
4. **180초 Timeout 안전장치** — `development-hq/mvp/engine.py`의
   `ENGINE_TIMEOUT_SECONDS`는 상향하지 않고 그대로 유지(보조
   안전장치, 성능 개선 수단 아님)

Dividend Stock Team의 7개 역할·지시문은 한 글자도 바꾸지 않았다.

## 기존 완료 프로젝트와의 관계

**JNJ/KO/PG/Nestlé/Toyota의 `agents.py`/`runner.py`는 소급 수정하지
않았다.** 이 신규 패턴은 이번 실행부터 새로 시작하는 Dogfooding에만
적용되며, 기존 5건은 각자의 완료 시점 Evidence 기록을 그대로 유지한다.

## Out of Scope

- Dividend Stock Team/Agent 실제 확장, Investment HQ Architecture 확정
- 새 Kernel Component, Runtime
- 자동매매, 실거래
- `development-hq/` 수정

## Development HQ Update Policy

기존 Dogfooding 프로젝트와 동일: 이 프로젝트에서 발견되는 문제는
즉시 Development HQ를 고치는 근거로 쓰지 않는다. Observe First,
Decide Later.
