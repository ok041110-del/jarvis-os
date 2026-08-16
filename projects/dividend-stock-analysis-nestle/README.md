# Dividend Stock Analysis — Nestlé S.A. (NESN.SW / NSRGY)

Dividend Stock Team의 **비미국 종목 경계 검증** Dogfooding이다. 목적은
Nestlé 분석 자체가 아니라, JNJ/KO/PG(전부 미국 상장·USD·분기배당) 3건으로
확정된 Dividend Stock Team의 최소 업무 범위(7개 분석 → Bull/Bear →
Synthesis → Final Report)가 **국가/시장 구조가 다른 비미국 종목**에서도
그대로 유효한지 확인하는 것이다. 새 Agent/Role/Architecture를 이 실행에서
선행 설계하지 않는다(`docs/research/DIVIDEND-STOCK-TEAM-DEFINITION-0001.md`
재평가 조건 — "국제/신흥시장/리츠형 배당주 Dogfooding에서 이번 범위와
다르거나 겹치는 부분이 실제로 관찰될 때" 트리거에 대응).

16년 연속 배당 증액을 기록한 실제 배당주이며, 스위스 1차 상장(SIX:
NESN.SW), 연 1회 배당, 스위스 35% 원천징수세, ADR(NSRGY) 환전 구조 등
JNJ/KO/PG와 구조적으로 다른 비미국 시장 특성을 가진다.

## 무엇을 하는가

`agents.py`/`runner.py`는 `projects/dividend-stock-analysis-{jnj,ko,pg}`의
project-local 코드를 그대로 복제한 것이다(회사명/티커/경로만 교체, 역할
지시문은 한 글자도 바꾸지 않음). 7개 분석(Fundamental/Dividend Quality/
Valuation/Technical/Industry-Competition/News-Event/Sentiment) → Bull
Case/Bear Case → Synthesis → Final Report(총 11회 `call_engine()` 호출)
구조를 그대로 쓴다.

**Development HQ(`development-hq/`)는 Platform이고, 이 프로젝트는 그
Platform을 사용한 결과물이다.** `development-hq/mvp`를 한 줄도 수정하지
않는다.

## JNJ/KO/PG와의 차이

- 국가/거래소: 스위스(SIX) 1차 상장, JNJ/KO/PG는 전부 미국(NYSE) 상장
- 통화: CHF 표시 원주 + USD 표시 ADR(NSRGY) 이중 구조 — raw_data.md에서
  통화 표시 혼재 자체를 데이터 한계로 기록
- 배당 주기: 연 1회(Annual) — JNJ/KO/PG는 전부 분기 지급
- 세금: 스위스 35% 원천징수세(미국 거주자는 절차를 거쳐 15%로 우대) —
  JNJ/KO/PG에는 없던 변수
- 산업: 식품/음료(소비재)로 KO/PG와 겹침 — 선정 기준은 산업이 아니라
  국가/시장 구조 차이이므로 의도적으로 유지

## 구조

`projects/dividend-stock-analysis-jnj/README.md`와 동일한 구조,
대상 종목만 다르다.

## Out of Scope

- Dividend Stock Team/Agent 실제 확장/신규 생성, Investment HQ
  Architecture 확정
- 새 Kernel Component, Runtime, Production caller, Prompt Cache
- 자동매매, 실거래

## Development HQ Update Policy

`projects/dividend-stock-analysis-{jnj,ko,pg}`와 동일: 이 프로젝트에서
발견되는 문제는 즉시 Development HQ를 고치는 근거로 쓰지 않는다.
Observe First, Decide Later.
