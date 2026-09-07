# EVIDENCE-0007: 기존 5개 `call_engine()` 호출부 OmniRoute 전환 검토 — 전환 보류(HOLD)

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. `ADR-0017`, `EVIDENCE-0006`이 확정한 범위를 그대로 전제하고,
이번 검토 결과(전환 보류 판정과 근거)만 기록한다. **코드 변경
없음**(사용자 지침 9 — 위험 판정 시 코드를 변경하지 않는다).

## 1. 검토 목적

`EVIDENCE-0006` §7.2 항목1이 남긴 질문 — "기존 5개 호출부(`agents/
backend.py`·`design.py`·`qa.py`·`requirements.py`·
`workflow_ast_context.py`)를 `call_engine_via_omniroute()`로 전환할지" —
에 답한다. 전환이 안전하다고 판단되면 실제로 전환하고, 위험하거나
현재 환경에서 검증 불가능하면 코드를 변경하지 않고 보류 근거를
기록한다.

## 2. 5개 호출부 ↔ `engine.py`/`omniroute_engine.py` 관계 전수 분석

| 파일 | `call_engine` 사용 | 프롬프트 형태 | 계약 | 직접 real-call 테스트 |
|---|---|---|---|---|
| `agents/backend.py` | `code_review`(1회), `code_generation`(1회) — 2개 호출 지점 | `f"CODE_REVIEW:{...}"`, `f"CODE_GENERATION:{...}"` | 단일 prompt → 단일 텍스트, `code_generation`은 `_strip_code_fence()`로 후처리 | 있음(§3.1) |
| `agents/design.py` | `design_agent_design`(1회) | `f"DESIGN:{...}"` | 동일 | 없음(간접 노출) |
| `agents/qa.py` | `qa_agent_test_execution`(1회) | `f"TEST_EXECUTION:{...}"` | 동일 | 있음(§3.1, `test_mvp_0001.py`) |
| `agents/requirements.py` | `requirements_agent_requirement_analysis`(1회) | `f"REQUIREMENT_ANALYSIS:{...}"` | 동일 | 없음(간접 노출) |
| `workflow_ast_context.py` | `identify_target`(1회) | prefix 없는 raw prompt(`_IDENTIFY_INSTRUCTION` + design + candidate index) | 동일 | 없음(mock 처리, 이 파일 자체는 현재 Python 3.9 collection 오류로 비활성 — §2.1) |

모두 예외 없이 `from ..engine import call_engine`(또는 `.engine`)로
**같은 함수를 각자 local import**한다 — `EVIDENCE-0006` §3.1이 확인한
`call_engine_via_omniroute()`의 시그니처(`str -> str`, 실패 시
`RuntimeError`)와 완전히 동일한 모양이므로, import문 교체만으로
기술적으로는 즉시 대체 가능하다(**기술적 가능성**과 **운영
안전성**은 다른 질문이다 — §4).

### 2.1 `workflow_ast_context.py`의 특수성

이 파일은 `hqs/development/mvp/tests/test_workflow_ast_context.py`
수집 시 Python 3.9 환경에서 `str | None`(PEP 604) 문법 오류로
**현재 이 환경에서 아예 로드되지 않는다**(`EVIDENCE-0006` §8이 이미
기록한, 이번 작업과 무관한 기존 조건). 즉 이 호출부는 지금 이
환경에서 회귀 검증 자체가 불가능하다 — 이 사실 하나만으로도 "5개
전부를 동시에, 검증된 상태로 전환"하는 것은 이 환경에서 성립하지
않는다.

## 3. 운영 리스크·회귀 범위 판단

### 3.1 결정적 발견 — 기존 테스트의 **게이트 없는 실제 Engine 호출**

`hqs/development/mvp/tests/test_mvp_0001.py`의 첫 두 테스트를 실제
실행해 확인했다.

```
python3 -m pytest hqs/development/mvp/tests/test_mvp_0001.py -v --durations=5
```

```
test_returns_review_then_test_cases_without_manual_intervention PASSED  (46.17s)
test_review_content_reaches_test_execution_as_context PASSED            (48.16s)
```

**이 두 테스트는 `call_engine`을 전혀 mock하지 않는다**(`test_returns_
review_then_test_cases_without_manual_intervention`은 아예 monkeypatch가
없고, `test_review_content_reaches_test_execution_as_context`도 원본
`call_engine`을 감싸 그대로 호출하는 spy를 쓴다, §2 코드 인용).
소요 시간(46~48초)은 실제 `claude` CLI subprocess 왕복 시간과
일치한다 — 이 저장소의 통상적인(이중 opt-in 게이트 없는)
`pytest` 실행이 **실제 Engine을 매번 호출한다.**

**이것이 결정적인 이유**: `agents/backend.py`(`code_review`)와
`agents/qa.py`(`test_execution`)가 이 테스트를 통해 실제로
행사된다. 만약 이 두 파일의 import를 `call_engine_via_omniroute`로
전환하면, **바로 이 게이트 없는 테스트가 매 `pytest` 실행마다
실제 OmniRoute 호출을 시도하게 된다** — `OmniRoute-thin-engine-caller`
트랙 전체가 지금까지 유지해 온 "실제 서버 호출은 반드시 이중
opt-in 게이트 뒤에 둔다"는 안전 원칙(`EVIDENCE-0004`/`0005`/`0006`,
`test_real_engine_budget_block.py`/`test_omniroute_engine_real.py`의
게이트 설계)과 정면으로 충돌한다. 구체적으로 두 가지 실패 모드가
있다.

1. **로컬에 OmniRoute가 떠 있지 않은 경우(현재 이 환경 포함)**:
   `test_mvp_0001.py`의 두 테스트가 매번 connection-refused로
   FAIL하게 된다 — Development HQ의 **가장 기본적인 Exit
   Criteria 테스트**(`MVP.md`)가 깨진다.
2. **어떤 이유로든 OmniRoute가 `127.0.0.1:20128`에 떠 있는
   경우**: `OMNIROUTE_MODEL` 기본값 `"auto"`가 그대로 적용되며
   (`omniroute_engine.py`는 이 값을 검사하지 않는다 — 사용자
   지침 4가 요구하는 그대로), 그 인스턴스에 `blockedProviders`/
   `REQUIRE_API_KEY`가 구성되어 있는지 **이 테스트도, 이
   저장소의 어떤 코드도 확인하지 않는다.** 구성되어 있지 않다면
   `EVIDENCE-0003`/`0004`가 규명한 zero-config egress 경로(내장
   `opencode`/`felo-web` 계정)로 **매 `pytest` 실행마다 실제
   외부 provider 호출이 발생할 위험**이 생긴다 — 사용자 지침
   8("외부 Provider egress는 금지")이 정확히 막으려는 상황이다.

이 위험은 **이번 작업이 새로 만든 것이 아니다** — `test_mvp_0001.py`가
게이트 없이 실제 Engine을 호출하는 것 자체는 기존 저장소의 확립된
관행(local `claude` CLI는 이미 신뢰된 대상이므로 게이트가 필요
없었다)이다. 문제는 **그 관행이 대상 Engine이 `claude` CLI일
때만 안전하다는 암묵적 전제 위에 있다는 것** — OmniRoute로
대상을 바꾸는 순간 그 전제가 깨진다.

### 3.2 회귀 범위(전환을 강행했을 경우)

| 대상 | 영향 |
|---|---|
| `test_mvp_0001.py`(2개, 게이트 없음) | **직접 파괴적 영향**(§3.1) |
| `test_workflow_0002/0008/0009/artifact_flow/hello_sdlc/project_intelligence.py` | Agent 함수 레벨(`backend_agent_code_review` 등)에서 monkeypatch — `call_engine` import 경로 변경 자체로는 깨지지 않음(간접 확인, §2 표) |
| `test_ast_context_package_paths.py` | `engine.py` 소스 텍스트를 정적으로 검사 — `engine.py` 무수정이므로 영향 없음 |
| `test_workflow_ast_context.py` | 이미 이 환경에서 collection 오류(§2.1) — 검증 자체 불가 |
| `test_engine.py` | `engine.py` 무수정이므로 영향 없음 |

**핵심 결론**: 전환의 실제 파괴적 회귀는 §3.1 하나에 집중돼
있지만, 그 하나가 Development HQ의 Exit Criteria 테스트 자체이며
동시에 이 트랙이 지금까지 지켜 온 zero-egress 원칙을 무력화할 수
있는 성격이라는 점에서 **치명적이다.**

### 3.3 운영 의존성 리스크(테스트와 별개)

- `.claude/docs/integrations/omniroute.md`가 이미 기록한 대로, 이
  실행 환경(ephemeral 컨테이너/세션)에는 **상시로 떠 있는 실제
  OmniRoute 인스턴스가 없다** — "실제 연결은 사용자의 로컬 개발
  환경에서 수행해야 한다"고 그 문서 자신이 명시한다.
- 5개 호출부를 전부 전환하면(§4.1이 확인하듯 RT-0001 회피를 위해
  "부분 전환"은 선택지가 아니다) Development HQ의 **모든** 실제
  Dogfooding 작업(Backend/Design/QA/Requirements Agent 전부)이
  즉시, 예외 없이, 실제로 살아있고 올바르게 설정된 OmniRoute
  인스턴스에 하드 의존하게 된다.
- 이 의존성이 실제로 충족되는지(OmniRoute가 떠 있는지, 실제
  provider connection이 구성됐는지, `blockedProviders`/
  `REQUIRE_API_KEY`가 설정됐는지)는 **이 세션이 검증할 수 없다** —
  검증하려면 실제 provider egress를 감수하거나(사용자 지침 8 위반),
  사용자의 실제 로컬 환경에 직접 접근해야 한다(이 세션의 권한 밖).

## 4. Case A Boundary·Policy 소재 유지 확인(전환 여부와 무관하게 재확인)

이번 검토는 코드를 변경하지 않았으므로 이 항목은 트리비얼하게
유지된다 — 그러나 "만약 전환했다면 지켰을 설계"를 명시해 둔다.

- Jarvis 코드에 provider/model 선택, routing, fallback, budget,
  policy, OmniRoute 설정 검사를 추가하지 않는다(사용자 지침 3) —
  전환이 실제로 일어났다면 5개 파일의 **import문 한 줄씩**만
  바뀌었을 것이고, 어떤 조건 분기·검사 로직도 추가되지 않았을
  것이다.
- `OMNIROUTE_MODEL=auto`의 안전성을 Jarvis 코드가 검사하지 않는다
  (사용자 지침 4) — `omniroute_engine.py`는 이미 이 원칙을
  지키도록 구현돼 있다(`EVIDENCE-0006` §3.1). §3.1이 지적한 위험은
  바로 이 "Jarvis가 검사하지 않는다"는 설계 원칙의 **필연적
  귀결**이다 — 원칙 자체를 어기지 않고는 그 위험을 코드로 막을
  수 없다(코드로 막으면 Policy 판정 로직이 되어 Case A를 벗어난다,
  `ADR-0017` §2.4). 이 구조적 긴장은 §6이 다시 다룬다.

## 5. RT-0001 Candidate 2 / `ADC-0010` 재검토 조건 사전 확인

전환을 실제로 하지 않았지만, 사용자 지침 5에 따라 "실제로
전환했다면"을 가정한 사전 확인을 수행한다.

- **가능한 유일한 안전 설계는 "전부 동시 전환"뿐이다.** 5개 중
  일부만 전환하면(예: `backend.py`만 전환, 나머지는 `call_engine`
  유지) Development HQ의 실제 파이프라인 안에 두 Engine이
  동시에 실재하게 되어 `RT-0001` Candidate 2 Trigger("Engine 수
  ≥2")의 근거가 되는 "단일 Engine" 전제가 직접 깨진다 — **부분
  전환은 이 검토에서 처음부터 배제한다.**
- **전부 동시에 전환**했다면: `call_engine()`은 여전히 `engine.py`에
  정의된 채로 남지만(§6이 이유를 설명), 실제 프로덕션 호출부
  어디에서도 사용되지 않게 된다. Development HQ의 실제 파이프라인은
  **여전히 정확히 1개 Engine**(OmniRoute로 교체됨)만 대상으로 한다
  — "두 번째 Engine이 실제로 추가되어 호출 지점이 둘 이상을
  대상으로 하게 됨"이 아니라 "Engine이 교체됨"이다. `ADC-0010`
  C1 재검토에 필요한 "Engine 수 ≥2" 결합 조건도 이 의미에서
  충족되지 않는다.
- **결론**: 가상의 "전부 동시 전환" 설계 자체는 RT-0001/`ADC-0010`
  Trigger를 발생시키지 **않았을 것이다.** 이번 보류 판정은
  Governance Trigger 때문이 아니라 §3의 운영 안전성 문제 때문이다
  — 이 둘을 혼동하지 않는다.

## 6. 판정 — 전환 보류(HOLD)

**전환하지 않는다. 코드를 변경하지 않았다.**

### 6.1 보류 근거(요약)

1. `test_mvp_0001.py`의 게이트 없는 실제 Engine 호출 테스트가,
   전환 시 이 트랙 전체가 지켜 온 이중 opt-in 게이트 원칙을
   우회해 실제 OmniRoute 호출(최악의 경우 실제 provider egress)을
   매 `pytest` 실행마다 발생시킬 수 있다(§3.1) — 사용자 지침
   8("외부 Provider egress는 금지")과 직접 충돌할 위험.
2. RT-0001 회피를 위해 유일하게 허용되는 설계(5개 전부 동시 전환)는
   Development HQ의 **모든** 실제 작업을 되돌릴 수 없이 실제
   OmniRoute 가용성에 의존시킨다 — 그 가용성(설치·기동·provider
   connection·`blockedProviders`/`REQUIRE_API_KEY` 구성)은 이
   세션이 실제 egress 없이는 검증할 수 없다(§3.3).
3. `workflow_ast_context.py`는 현재 이 Python 환경에서 아예 로드되지
   않는다(§2.1) — "5개 전부, 검증된 상태로" 전환한다는 조건 자체가
   이 환경에서 성립할 수 없다.
4. 이 세 가지 모두 **Jarvis 코드로 우회할 수 없다** — 우회하려는
   시도(예: Jarvis가 OmniRoute 가용성을 사전 검사하는 코드 추가)
   자체가 Policy 판정 로직이 되어 Case A를 벗어난다(§4) — 사용자
   지침 8이 명시한 "임의 우회 구현 금지"에 해당한다.

### 6.2 전환을 다시 검토할 수 있는 선행조건

이 보류는 영구적 Reject가 아니다 — 아래가 **전부** 충족되면 재검토
가능하다.

1. 사용자(운영자)가 실제 로컬 환경에서 OmniRoute를 기동하고,
   `blockedProviders`/`REQUIRE_API_KEY`를 구성했음을 **직접 확인**
   한다(이 세션이 대신 확인할 수 없다, §3.3).
2. `test_mvp_0001.py`의 게이트 없는 두 테스트를, 이 트랙의 기존
   이중 opt-in 게이트 관례에 맞춰 재설계한다(전환과 무관하게 이미
   존재하는 위험이지만, 전환의 **필요조건**이 된다) — 이 재설계
   자체가 별도의, 이번 작업 범위 밖의 결정이다.
3. Python 환경을 `workflow_ast_context.py`가 로드 가능한 버전(3.10+)
   으로 맞추거나, 그 파일을 5개 전환 대상에서 명시적으로 제외하고
   "4개 전환 + 1개 보류"의 혼합 상태가 RT-0001을 촉발하지 않는지
   별도로 재검토한다(§5의 "부분 전환 배제" 논리와 충돌할 수 있어
   신중한 재분석이 필요하다 — 이 문서는 그 재분석을 대신하지
   않는다).
4. 전환 자체를 Architecture/Governance 절차(RFC/ADC/ADR)로 다시
   확인할지, 아니면 순수 운영 결정으로 충분한지 사용자가 명시적으로
   선택한다.

## 7. Governance / Architecture 영향

- Architecture 변경: **없음**. Contract 변경: **없음**. Freeze 변경:
  **없음**.
- `hqs/development/mvp/engine.py`, `omniroute_engine.py`, 5개
  호출부 파일: **전부 무수정**(코드 diff 0).
- `ADC-0027`~`ADC-0031`, `ADR-0015`~`ADR-0017`, `EVIDENCE-0001`~
  `EVIDENCE-0006`: **무수정**.
- 새로 작성한 파일: 이 Evidence 문서 1개뿐.

## 8. Open Issue 재분류

### 8.1 이번 검토로 새로 확인된 것(결함 발견 — 별도 관심 필요, 이번 작업 범위 밖)

| 항목 | 성격 |
|---|---|
| `test_mvp_0001.py`의 두 테스트가 이중 opt-in 게이트 없이 실제 Engine을 호출한다 | **기존 저장소의 확립된 관행**(`claude` CLI가 이미 신뢰된 로컬 대상이므로 지금까지는 안전했다) — 이번 검토가 처음 발견했지만 이번 작업이 만든 결함은 아니다. OmniRoute 전환의 **차단 사유**이지, 그 자체로 지금 당장 고쳐야 할 버그는 아니다(`call_engine()`이 여전히 `claude` CLI를 호출하는 한 안전하다) |

### 8.2 무변경으로 유지되는 것

`EVIDENCE-0006` §7.2·§7.3이 분류한 항목(5개 호출부 전환 여부 —
이번 문서가 답함: 보류, `OMNIROUTE_MODEL=auto` 안전장치 책임 소재
— 무변경, Audit Policy 공백·`priority`·`domain_budgets` semantics·
`ADC-0010`/`RT-0001`·ADC-01/02/`ADC-0003`판단4 — 전부 무변경) 그대로
유지된다.

## 9. Provenance / Reproducibility

- 5개 호출부 파일 직접 읽기(§2): `agents/backend.py`, `agents/
  design.py`, `agents/qa.py`, `agents/requirements.py`,
  `workflow_ast_context.py`.
- 결정적 발견 재현: `python3 -m pytest
  hqs/development/mvp/tests/test_mvp_0001.py -v --durations=5` →
  `3 passed in 94.35s`, 상위 2개 durations 46~48초(§3.1).
- `workflow_ast_context.py` collection 오류 재확인:
  `python3 -m pytest hqs/development/mvp/tests/test_workflow_ast_context.py`
  → `TypeError: unsupported operand type(s) for |: 'type' and
  'NoneType'`(Python 3.9.6, `EVIDENCE-0006` §8과 동일 기존 조건).
- 실제 `~/.omniroute/storage.sqlite`: 이번 검토 전체(분석만,
  서버 미기동)에서 mtime(`1788605986`)·size(`2547712`) 완전
  동일(변경 자체가 없었으므로 자명).
- 코드 변경: **없음**(`git status`로 확인 — 이 Evidence 문서
  1개만 추가).

## Self Review

- 5개 호출부와 `engine.py`/`omniroute_engine.py`의 관계를 전수
  분석했는가 — **Pass**(§2, §2.1).
- 운영 리스크와 회귀 범위를 명확히 판단했는가 — **Pass**(§3, 특히
  §3.1의 실측 재현).
- Case A Boundary·Policy 소재 원칙을 지켰는가(전환하지 않았으므로
  트리비얼하지만 설계도 확인) — **Pass**(§4).
- `OMNIROUTE_MODEL=auto` 안전성을 Jarvis 코드로 검사하려 했는가 —
  **아니오**(§4 — 기존 책임 경계 유지, 그로 인한 위험을 §3.1에서
  있는 그대로 기록했을 뿐 코드로 우회하지 않았다).
- RT-0001/`ADC-0010`을 전환 전에 재확인했는가 — **Pass**(§5).
- 실제 전환으로 Trigger가 발생했는가 — **해당 없음**(전환하지
  않았다). 가상 설계에 대한 사전 분석 결과는 §5에 기록했다.
- 전환이 안전하다고 판단했는가 — **아니오**(§3, §6.1) — 따라서
  전환하지 않았다.
- 위험 판정 시 코드를 변경했는가 — **아니오**(§7 — 이 문서 1개
  파일만 추가, `git status`로 확인 가능).
- 임의 우회 구현을 시도했는가 — **아니오**(§6.1 항목4 — 우회
  자체가 Case A 위반이 된다는 것을 명시하고 시도하지 않았다).
- Architecture/Contract 변경이 있는가 — **아니오**(§7).
- 재검토를 위한 선행조건을 명시했는가 — **Pass**(§6.2).
- commit/push/PR을 수행했는가 — **아니오**.
