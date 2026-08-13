# Evidence — AAPL Stock Dogfooding (실행 1회차)

PRD v1.2 8장 관찰 항목 기준. 여기 적힌 것은 모두 이번 실제 실행(`runner.py`,
2026-08-10, 2회 실행 — 1차 실행 + 결함 수정 후 재실행)에서 직접 관찰된
사실이다. 추측이나 일반론은 적지 않는다.

## 업무 (Task)

- 5개 분석 Capability(Fundamental/Technical/Industry/News-Event/Sentiment)는
  구조적으로 완전히 동일했다: "지시문 프리픽스 + 데이터 한계 고지 + `call_engine`
  단일 호출 + 텍스트 반환". `development-hq/mvp/agents.py`의 code_review/
  test_execution과 같은 패턴이 도메인과 무관하게 그대로 재사용됐다 — 이번
  실행에서 새 호출 방식이나 새 Contract가 필요하지 않았다.
- Bull Case/Bear Case/Synthesis/Final Report 4개 Task는 이전 Task 출력에
  전적으로 의존하는 선형 체인이었다 — `textkit`/`notekeeper`의
  requirement→design→code 체인과 동일한 형태(Task 출력이 다음 Task의 입력).
- 5개 분석 Task는 서로 데이터 의존성이 없어 이론적으로는 병렬 실행이 가능한
  구조였다. 그러나 이번 실행은 순차 실행했고(하드코딩된 순서), 전체 9회
  Engine 호출이 수 분 내 끝나 성능 문제가 실제로 발생하지 않았다 — 병렬
  Runtime의 필요성은 **이번 실행에서는 확인되지 않았다** (필요 없다는
  뜻이 아니라, 필요하다는 근거가 아직 없다는 뜻).

## 역할 (Role)

- 5개 역할이 실제로 서로 겹치지 않는 관점을 냈다: Fundamental은 매출/마진,
  Technical은 추세/모멘텀, Industry는 경쟁 구도, News/Event는 정성적 이벤트,
  Sentiment는 애널리스트 컨센서스. 하나의 범용 Agent로 합쳤을 때보다 각
  역할이 "자기 영역 밖은 판단하지 않는다"는 정직성을 지키기 쉬웠다(각
  산출물이 반복적으로 "제공된 자료 범위 밖은 판단할 수 없다"고 명시함).
- **역할 분리의 부작용을 실제로 관찰함**: Technical 분석은 "현재가가
  제공되지 않아 지지/저항선 대비 위치를 판단할 수 없다"고 했는데, 실제
  현재가($308.63)는 Sentiment 섹션(raw_data.md)에만 있었다. `raw_data.md`를
  태그별로 쪼개 각 Capability에 자기 섹션만 준 것이 원인이다. 이는 Report
  Writer 단계(최종 보고서 종합)에서 교차 인용으로 보완됐지만, 개별 Capability
  실행 시점에는 실제로 정보가 파편화됐다 — Agent 간 Context 공유 범위를
  어떻게 정할지가 실제 문제로 나타난 사례다.

## 협업 (Collaboration)

- Bull/Bear 대립 검토는 실제로 유용했다: Synthesis 단계가 "합의된 사실 /
  진짜 사실 충돌(글로벌 점유율 순위) / 같은 사실의 다른 해석(8가지) /
  결론을 바꿀 미해결 질문(6가지)"을 구분해냈다 — 5개 분석을 단순 나열하는
  것보다 명백히 더 많은 구조화된 정보를 만들어냈다.
- Task 간 Context 전달은 in-memory 변수(문자열 결합)만으로 충분했다 —
  `IMPLEMENTATION_RULES.md`의 "Memory Service 구현 금지" 원칙이 이 도메인
  에서도 그대로 유지됐다. 별도 저장소나 상태 관리가 필요하지 않았다.

## 시스템 (System)

- `call_engine()` 단일 함수 + 리터럴 dict 패턴이 Investment 도메인에서도
  변경 없이 그대로 동작했다. 새 Capability(9개)를 정의하는 데 Registry,
  Scheduler, Engine Gateway 등 어떤 Kernel 확장도 필요하지 않았다 — Stop
  Trigger가 실행 중 한 번도 발동하지 않았다.
- **실제로 발생한 유일한 결함은 Architecture 문제가 아니라 데이터 준비
  문제였다**: `raw_data.md`의 섹션에 회사/티커명이 없어 5개 분석 전부가
  회사를 "추정"해야 했다(1차 실행 산출물에 그 추정 문구가 남음). 각 섹션
  앞에 `Company: Apple Inc. (Ticker: AAPL)` 한 줄을 추가하는 최소 수정으로
  해결됨(재실행으로 검증 완료, 추정 문구 사라짐). Capability 함수 시그니처나
  Contract는 변경하지 않았다.
- `call_engine()`은 원래부터(코드 리뷰 등 기존 Capability에서도) 실시간
  데이터에 접근할 수 없었지만, 그것이 실제로 문제가 된 것은 이번이 처음이다
  — 코드 리뷰는 입력 코드 자체가 완결된 데이터였던 반면, Stock 분석은 외부
  실시간 데이터가 반드시 필요했다. 이번에는 이 세션(오케스트레이터)이
  WebSearch로 직접 수집해 우회했다(`notekeeper`의 기존 코드 enrich 패턴
  재사용, 새 Architecture 아님). 다만 이는 **매번 사람 또는 세션이 수동으로
  다시 검색해야 함**을 의미한다 — 향후 "주기적/자동 데이터 수집"이 실제로
  필요해지는 시점이 오면 그것은 Runtime/Connector 영역의 진짜 Boundary
  Question이 될 수 있다. **이번 1회성 실행에서는 그 필요성이 실제로
  발생하지 않았으므로 지금 RFC로 올리지 않고 기록만 한다.**

## 관찰되지 않은 것 (명시적으로 기록)

- Bull/Bear가 실제 사실을 두고 대립하는 사례는 5개 분석 중 산업/경쟁구도
  1건(글로벌 스마트폰 순위 집계기관 간 불일치)뿐이었다 — 나머지는 전부
  "같은 숫자의 다른 해석"이었다. Bull/Bear가 실제 사실 자체를 놓고 싸우는
  경우가 얼마나 흔한지는 1회 실행으로 판단할 수 없다.
- 병렬 실행, 대규모 데이터, 여러 기업 비교, 반복 실행에 따른 Task 패턴
  안정성은 이번 1회 실행 범위 밖이며 관찰되지 않았다.
