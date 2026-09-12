# LangGraph Conditional Routing Prototype (v1)

**문서 성격**: Experimental Prototype(Formal Architecture Decision
아님). Development HQ v2.0 Baseline(`hqs/development/`)을 수정하지
않으며, 그 안의 실제 프로덕션 Capability 함수(`backend_agent_code_review`,
`qa_agent_test_execution`)를 **읽기 전용 import**로만 재사용한다.

## 목적

기존 LangGraph 검증(v1 `archive`, v2 E2/E3 toy·Domain PoC, Phase E/F
Multi-Agent Handoff/Failure Isolation)은 반복하지 않는다. 이 Prototype이
새로 확인하는 것은 하나뿐이다 — **실제 프로덕션 Capability와 실제
Engine 호출을 그대로 두고, 그 위의 "조건부 분기" 배선만 LangGraph의
`add_conditional_edges`로 바꿨을 때 기존 plain Python 분기
(`workflow_0002.py::run_mvp_0002`)와 비교해 무엇이 달라지는가**.

## 대상으로 고른 이유

`hqs/development/mvp/workflow_0002.py`(MVP-0002)는 이미 실제
Production 코드에 다음 조건부 분기를 갖고 있다.

```python
if NO_ISSUES_MARKER in review:
    test_cases = "(생략됨: ...)"
else:
    test_cases = qa_agent_test_execution(code, review)
```

이것이 지금 저장소에서 "State 기반 Agent workflow / Conditional
routing / Agent handoff / 실패 전파" 네 후보 중 **Conditional
routing**을 고른 이유다 — 이미 실제로 동작하는 최소 비교 대상
(baseline)이 프로덕션에 존재해서, 새로 baseline을 만들 필요가 없다.

## 이 Prototype이 재사용하는 것 (수정하지 않음)

- `hqs.development.mvp.agents.backend.backend_agent_code_review`
- `hqs.development.mvp.agents.qa.qa_agent_test_execution`
- `hqs.development.mvp.agents.backend.NO_ISSUES_MARKER`
- `hqs.development.mvp.workflow_0002.run_mvp_0002` (baseline 비교 대상,
  그대로 호출만 한다)
- `hqs.development.mvp.engine.call_engine` (아래 참고)

## Engine 호출 경로에 대한 unavoidable 차이 (명시)

`agents/backend.py`·`agents/qa.py`는 현재 `omniroute_engine.
call_engine_via_omniroute`를 통해 Engine을 호출한다(Production
경로, OmniRoute Thin Engine Caller). 그러나 OmniRoute는 **사용자
로컬 머신에서 상시로 떠 있어야 하는 게이트웨이**이며
(`.claude/docs/integrations/omniroute.md`), 이 Prototype이 실행된
일시적(ephemeral) 세션에는 그 서버가 없다(`Connection refused`
실측 확인, `EVIDENCE.md` §0).

그래서 이 Prototype **한정으로**, `run_prototype.py`가 세션 시작
시점에 `agents.backend.call_engine`/`agents.qa.call_engine`
전역 이름을 `hqs.development.mvp.engine.call_engine`(Claude CLI 직접
호출, 이 저장소의 다른 real Engine 경로)로 교체한다. 이는:

- 프로덕션 파일(`agents/backend.py`, `agents/qa.py`,
  `omniroute_engine.py`)을 **한 글자도 수정하지 않는다** — 교체는
  이 Prototype 스크립트의 프로세스 메모리 안에서만 일어난다.
- Capability의 지시문(instruction)·판정 로직(`NO_ISSUES_MARKER`)은
  **완전히 동일하게 재사용**된다 — 바뀌는 것은 어떤 전송 경로로
  Engine에 도달하는가뿐이다.
- baseline(`run_mvp_0002`)과 LangGraph 버전 양쪽에 **동일하게** 적용된다
  — 두 비교 대상이 같은 조건에서 실행되므로 비교 결과의 공정성에
  영향을 주지 않는다.

## 실행 방법

```bash
# 저장소 밖 별도 venv에 langgraph만 설치(저장소 의존성 파일 변경 없음)
python3 -m venv /path/to/venv && source /path/to/venv/bin/activate
pip install langgraph==1.2.11

# 저장소 루트에서 PYTHONPATH를 잡고 실행
cd /path/to/jarvis-os
python3 projects/langgraph-conditional-routing-poc-v1/run_prototype.py
```

## 파일 구성

- `graph_langgraph.py` — LangGraph 구현(State/Node/Conditional Edge).
- `run_prototype.py` — 실행 harness. baseline과 LangGraph 버전을
  동일 입력으로 실행하고 결과를 비교·출력한다.
- `EVIDENCE.md` — 실제 실행 로그와 판단.

## 이 Prototype이 다루지 않는 것

- Checkpoint/Resume, Loop, Multi-Agent Handoff — 이미 E2/E3/Phase
  E/F가 검증했다(재검증 안 함).
- LangGraph를 Architecture Kernel Module로 채택하는 문제 — 이
  Prototype은 LangGraph를 Implementation Technology로만 다룬다.
- `workflow_0002.py`, `agents/*.py`, Development HQ v2.0 Freeze
  대상 어떤 파일도 변경하지 않는다.
