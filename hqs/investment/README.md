# Investment HQ

Jarvis OS의 두 번째 HQ. Development HQ가 확립한 Reference Architecture
(`docs/architecture/baseline/BASELINE.md` §4)를 재사용해서 만들었다 —
"Composable HQ" 원칙(새 HQ는 기존 Architecture를 재사용해 생성할 수
있어야 한다)의 첫 실제 적용 사례다.

## 왜 지금 만드는가

Stock/ETF/Dividend Stock 3개 Team이 `projects/` 아래 흩어진
project-local Dogfooding으로 각각 5회·6회·7회, 총 18회 반복
검증됐다(`docs/research/INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001.md`).
각 Team Definition 문서가 공통으로 명시한 "Investment HQ Architecture
설계가 별도로 착수될 때" 재평가 조건에 따라, 이번에 실제로 착수했다.

## Architecture

`STRUCTURE.md` 참조. `HQ → (선택) Division → (선택) Team → Agent/Role
→ Execution` — Development HQ와 동일한 계층, 새 Kernel Concept 없음.
RFC 대상이 아니다(`STRUCTURE.md`에 판단 근거 기록).

## 무엇을 하는가

`run.py`가 HQ의 최소 E2E 진입점이다 — Team(stock/etf/dividend_stock)
을 선택하고, 회사/펀드 표기·raw_data 경로·결과 디렉터리를 주면 그
Team의 검증된 역할 파이프라인(병렬화+출력최적화+Checkpointing+180초
Timeout, PR #80 표준)을 실행한다.

```
python3 hqs/investment/run.py <stock|etf|dividend_stock> "<회사/펀드 표기>" <raw_data.md 경로> <결과 디렉터리>
```

`teams/{stock,etf,dividend_stock}_team.py`는 각 Team의 project-local
Dogfooding(`projects/stock-analysis-*`, `projects/etf-analysis-*`,
`projects/dividend-stock-analysis-*`)에서 검증된 역할 지시문을 한
글자도 바꾸지 않고 옮긴 것이다 — 유일한 변화는 회사명이 하드코딩이
아니라 인자라는 것뿐이다(여러 종목에 재사용해야 하므로).

## 하지 않는 것 (`STRUCTURE.md` 금지 사항과 동일)

- Registry/Scheduler/Runtime/Workflow Parser 구현
- `hqs/development/` 수정
- 기존 완료 프로젝트(`projects/stock-analysis-*` 등 18건) 소급 수정
- Agent 이름 확정, Capability Contract, Development HQ Registry 등록

## Development HQ Update Policy

기존 Dogfooding과 동일: 이 HQ에서 발견되는 Dev HQ 문제는 즉시
Development HQ를 고치는 근거로 쓰지 않는다. Observe First, Decide
Later. Invest HQ 자체 문제와 Dev HQ 문제는 분리해서 기록한다.
