# Dividend Stock Analysis — Toyota Motor Corporation (7203.T / TM)

Dividend Stock Team의 **비미국 종목 경계 검증**이 아니라, Nestlé
실행(`projects/dividend-stock-analysis-nestle`)에서 관찰된 **Final
Report `ENGINE_TIMEOUT_SECONDS`(180초) 타임아웃의 재현성 검증**이
이번 실행의 목적이다. Team/Role/Architecture는 전혀 바꾸지 않는다.

일본 1차 상장(7203.T)·ADR(TM), 반기 배당(중간+기말), JPY 통화, 일본
원천징수세(20.315~20.42%, 조세조약 시 우대) 구조를 가진 실제 배당주이며,
기존 Investment Dogfooding(Stock 4종·ETF 6종·Dividend Stock: JNJ/KO/
PG/Nestlé)과 국가·산업·배당주기가 전부 겹치지 않는다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `projects/dividend-stock-analysis-nestle`의
project-local 코드를 그대로 복제한 것이다(회사명/티커/경로만 교체,
역할 지시문은 한 글자도 바꾸지 않음). 7개 분석 → Bull/Bear → Synthesis
→ Final Report(총 11회 `call_engine()` 호출) 구조를 그대로 쓴다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## 검증 대상

- Nestlé Final Report가 5~6회 연속 180초 타임아웃(실측 324.2초)을
  보인 것이, project-local 콘텐츠 특이 현상인지 Dev HQ 인프라의
  반복 가능한 한계인지를 다른 종목·다른 데이터로 재확인한다.
- Recovery: 타임아웃 시 `runner.py`가 중간 산출물을 실제로 보존하는지,
  어떤 실패 지점에서 수동 복구가 가능/불가능한지 관찰한다.
- retry/checkpointing은 이번 실행에서 구현하지 않는다(관찰만).

## Out of Scope

- Dividend Stock Team/Agent 실제 확장, Investment HQ Architecture 확정
- 새 Kernel Component, Runtime, checkpointing 구현
- 자동매매, 실거래

## Development HQ Update Policy

`projects/dividend-stock-analysis-*`와 동일: 이 프로젝트에서 발견되는
문제는 즉시 Development HQ를 고치는 근거로 쓰지 않는다. Observe First,
Decide Later.
