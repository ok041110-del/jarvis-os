# MVP-0004 Observation: Hello SDLC

## 목적

`docs/01_mvp/MVP-0004-plan.md`에 따라 구현한 End-to-End Pipeline
(Planning → Design → Implementation → Validation → Complete)을 실행하고,
그 결과를 관찰한다. 이 문서는 RT-0001 Trigger 관점에서 Task Dispatcher
재검토가 필요한지 여부만 **관찰**한다. 판단은 하지 않는다(ADC 대상은
별도 절차).

## 변경 파일

- `development-hq/mvp/engine.py` — 기존 단일 함수 `call_engine()` 안에
  분기 3개 추가(`REQUIREMENT_ANALYSIS:`, `DESIGN:`, `CODE_GENERATION:`).
  기존 `CODE_REVIEW:`/`TEST_EXECUTION:` 분기와 동일한 패턴.
- `development-hq/mvp/agents.py` — 래퍼 함수 3개 추가
  (`requirements_agent_requirement_analysis`, `design_agent_design`,
  `backend_agent_code_generation`). `AGENT_CAPABILITY_MAP`(MVP-0001)은
  건드리지 않고, 별도 리터럴 딕셔너리 `HELLO_SDLC_CAPABILITY_MAP`을
  신설해 3개 항목을 담았다.
- `development-hq/mvp/workflow_hello_sdlc.py` (신규) — `run_hello_sdlc(issue)`:
  5단계를 하드코딩된 순차 호출로 연결하고, 전체를 `try/except`로 감싸
  `status`를 `"Complete"` 또는 `"Failed"`로 반환한다.
- `development-hq/mvp/workflow.py`, `workflow_0002.py`는 **수정하지
  않았다**.

## 관찰 결과

### Pipeline이 Issue 하나를 끝까지 통과하는가?

**예.** `{"title": "reverse string", "description": "문자열을 뒤집는
함수를 추가해 달라", "status": "Open"}` 입력에 대해 Planning → Design →
Implementation → Validation을 모두 통과해 `status: "Complete"`를
반환했다. Design 단계에서 만든 함수 이름(`reverse_string`)이
Implementation의 생성 코드, Validation의 테스트 제안까지 그대로
전달되는 것을 확인했다(단계 간 데이터가 실제로 이어짐).

### 실패 경로도 관찰되는가?

**예.** `description` 키가 없는 Issue(`{"title": "x"}`)를 입력하면
Planning 단계에서 `KeyError`가 발생하고, `status: "Failed"`와
`error` 메시지가 반환되는 것을 확인했다.

### 기존 테스트에 영향이 있었는가? (중요 발견)

**처음에는 그렇다.** `AGENT_CAPABILITY_MAP`에 3개 항목을 직접 추가했더니
`development-hq/mvp/tests/test_mvp_0001.py`의
`test_agent_capability_map_is_a_literal_dict_with_exactly_mvp_scope`가
실패했다. 그 테스트는 MVP-0001 시점의 딕셔너리를 정확히 2개 항목으로
고정해 검증하고 있었기 때문이다.

**조치**: `AGENT_CAPABILITY_MAP`을 원래대로 되돌리고, MVP-0004의 3개
항목은 별도 딕셔너리 `HELLO_SDLC_CAPABILITY_MAP`에 담았다. 이후 기존
테스트 3건 모두 다시 통과했다.

**이 조치 자체를 그대로 기록한다(판단하지 않음)**: Agent-Capability
정보가 이제 `agents.py` 안에 리터럴 딕셔너리 2개(`AGENT_CAPABILITY_MAP`,
`HELLO_SDLC_CAPABILITY_MAP`)로 나뉘어 존재한다. 두 딕셔너리는 서로 겹치는
키가 없다(같은 Capability를 두 곳에서 관리하는 것은 아니다).

### RT-0001 Trigger 관점에서 Task Dispatcher 재검토가 필요한가? (관찰만, 판단 없음)

RT-0001 · Candidate: Task Dispatcher의 Trigger는 "Workflow Branch 발생
... 또는 하드코딩된 Task 호출 체인 수 ≥ 2"이다.

- `development-hq/mvp/workflow.py`(2-Task 체인), `workflow_0002.py`
  (분기 포함 2-Task 체인)에 이어, 이번 `workflow_hello_sdlc.py`가 5단계
  (Task 6개: Planning·Design·Implementation·code_review·test_execution)
  짜리 세 번째 하드코딩된 호출 체인이다. **하드코딩된 Task 호출 체인
  수가 ≥ 2라는 조건은 이미 MVP-0002 시점부터 성립했고, 이번 관찰로도
  그대로 유지된다.**
- 이번 파이프라인은 이전 체인들보다 길다(5단계, 실질 함수 호출 5개)는
  점에서 규모가 커졌다. 다만 여전히 순차 호출이며, 분기·재시도·병렬
  실행이 하나로 얽혀 있지는 않다 — `run_hello_sdlc()` 내부의 유일한
  비-선형 요소는 `try/except`에 의한 성공/실패 2-way 종료뿐이다.
- Implementation Stop Trigger(조건문이 파서/설정 파일로 대체되려는
  순간)는 **발생하지 않았다**. 5단계 호출은 여전히 `if`/`else` 없는
  순수 순차 호출로 표현되었다(`try/except`는 순서 결정 로직이 아니라
  실패 시 조기 종료일 뿐이다).
- Agent-Capability 매핑이 딕셔너리 2개로 나뉜 사실(위 항목 참조)은
  Task Dispatcher가 아니라 Registry Candidate와 관련된 관찰이다. 이
  관찰이 RT-0001의 Registry Trigger("Registry 중복 관리 발생")에 해당
  하는지도 이 문서는 판단하지 않는다.

**요약**: 이번 관찰에서 Task Dispatcher에 대한 Implementation Stop
Trigger는 발생하지 않았다. RT-0001이 정의한 "하드코딩된 Task 호출 체인
수 ≥ 2" 조건은 이미 충족된 상태(MVP-0002 이후)가 유지되며, 이번 MVP는 그
체인 길이(5단계)를 늘렸다는 사실만 추가로 관찰되었다. 이 관찰이
ADC-0002(Task Dispatcher, Keep in MVP)를 재검토할 근거가 되는지는 이
문서가 판단하지 않는다 — 필요하다면 별도 RFC의 몫이다.

## 범위 밖 (이번 구현에서 하지 않은 것)

- 새로운 Capability, Agent 추가 (기존 STRUCTURE.md 예시 목록만 사용)
- Scheduler, Queue, Runtime, Registry, Memory, Event Bus, Workflow Parser
- 병렬 실행, Retry, Priority, 여러 Issue 동시 처리
- 실제 Git/CI 연동, Model Routing, Engine Adapter, Multi Model
- 기존 `workflow.py`, `workflow_0002.py` 수정
- Task Dispatcher/Registry 재검토에 대한 판단(RFC-0002/ADC-0002 재논의
  포함) — 관찰만 기록했다.

## 테스트 결과

- 기존 MVP-0001 테스트(`development-hq/mvp/tests/test_mvp_0001.py`) 3건
  모두 통과 (`AGENT_CAPABILITY_MAP`을 원상 복구한 뒤 재확인).
- `run_hello_sdlc()`를 성공 케이스(정상 Issue)와 실패 케이스(필드 누락
  Issue) 각각에 대해 수동 실행하여 `status: "Complete"`와
  `status: "Failed"` 모두 확인했다. 별도 자동화 테스트는 추가하지
  않았다.
