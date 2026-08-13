# Stock Analysis — AAPL

Investment HQ / Stock Dogfooding PRD v1.2의 첫 번째 실행이다. 목적은 AAPL 분석
프로그램 자체가 아니라 **Development HQ가 실제 Investment 업무를 수행할 수
있는지 검증**하는 것이다. Investment HQ Architecture는 이 프로젝트에서
확정하지 않는다.

## 무엇을 하는가

TradingAgents(https://github.com/TauricResearch/TradingAgents)를 구현
Reference로 참고해, `raw_data.md`(이 세션이 WebSearch로 직접 수집한 실제
AAPL 자료)를 입력으로 5개 전문 분석(Fundamental/Technical/Industry-Competition/
News-Event/Sentiment) → Bull Case/Bear Case → Synthesis → Final Report를
실제 Engine(`call_engine`)으로 순서대로 실행한다.

TradingAgents의 Agent 이름/구조를 그대로 복제하지 않았다 — 실거래(Trader,
Risk Management, Portfolio Manager의 승인/거부, 모의 거래소 실행)는
PRD 2장이 명시적으로 제외한 범위이므로 가져오지 않았다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다 — `agents.py`가 그 안의 유일한 Engine 호출 지점(`call_engine`)만
import해서 쓴다.

## 구조

- `agents.py` — 이 프로젝트 전용 Capability 함수(Fundamental/Technical/
  Industry/News-Event/Sentiment/Bull/Bear/Synthesis/Report). Development HQ의
  기존 예시 Capability 목록(`code_review` 등)에 없는 도메인이므로, Platform을
  확장하지 않고 project-local로 같은 패턴(리터럴 dict + 지시문-프리픽스 함수 +
  `call_engine` 단일 호출)을 재사용한다.
- `runner.py` — 위 함수들을 하드코딩된 순서로 직접 호출.
- `issues/0001-aapl-analysis/raw_data.md` — 실제 수집한 원본 데이터(Engine이
  스스로 가져올 수 없으므로 이 세션이 WebSearch로 미리 수집해 Context로 제공).
- `issues/0001-aapl-analysis/*.md` — 각 단계 실행 결과.
- `issues/0001-aapl-analysis/EVIDENCE.md` — 실행 중 관찰한 Evidence(반복
  Task/역할 필요성/협업/시스템 요구사항).

## Out of Scope

- Investment HQ Architecture, Stock/ETF/Dividend Agent Architecture 확정
- 새 Kernel Component, Runtime, Production caller, Prompt Cache
- 자동매매, 실거래, Risk Management/Portfolio Manager의 승인·거부 로직
- Task Dispatcher 일반화, Workflow Parser, Scheduler, Registry 일반화
- TradingAgents의 State/Checkpoint(LangGraph, SQLite), 실데이터 API(Alpha
  Vantage 등) 연동 — 이번 실행은 WebSearch 수동 수집 + 정적 텍스트 파일로
  대체한다.
- 투자 권유 — 최종 보고서는 분석 연습이며 투자 조언이 아니다.

## Development HQ Update Policy

`projects/textkit`·`projects/notekeeper`와 동일: 이 프로젝트에서 발견되는
문제는 즉시 Development HQ를 고치는 근거로 쓰지 않는다. Observe First,
Decide Later.
