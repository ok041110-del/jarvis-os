# DEV-HQ-V2.0-T13 — Context 자동 추출 경계조건 Research

## 목적

T12에서 AST 기반 Multi-Module Automatic Excerpt가 5-6개 모듈·얕은 호출
그래프에서 Full Source와 동등한 Build 정확성을 검증했다. 이 문서는 그
검증이 어디까지 안전한지 경계조건을 찾는다:

1. 순환 참조(circular import) / 동적 import(`importlib`, `__import__`)가
   존재하는 실제 코드에서도 AST 폐쇄(closure) 알고리즘이 안전한가.
2. T12에서 관찰된 Full Source의 "Scope Pollution"(좁은 범위 Task에서
   파일 전체를 재작성하는 부작용)이 재현되는가.

이 문서는 Context 자동 추출을 구현하는 작업이 아니다. Production Code,
Architecture, Contract, Workflow는 수정하지 않았다.

## 사전 조사 — 경계조건이 실제로 존재하는가

Task 지시대로 "실제 코드"를 대상으로 검증하기 위해, 먼저 `hqs/development/mvp`
와 저장소 전체에서 순환 참조·동적 import 사례를 조사했다.

### 순환 참조

`mvp/*.py`의 상대 import(`from .X import Y`) 전체를 나열한 결과:

```
agents              -> engine
workflow            -> agents
workflow_0002       -> agents, workflow
workflow_0008       -> agents, project_intelligence, workflow, workflow_project_intelligence
workflow_0009       -> agents, project_intelligence, workflow, workflow_0008, workflow_project_intelligence
workflow_artifact_flow -> agents, project_intelligence, workflow, workflow_project_intelligence
workflow_hello_sdlc -> agents
workflow_project_intelligence -> agents, project_intelligence, workflow
```

이 그래프는 **비순환(DAG)**이다 — `engine`이 최종 leaf이고, 어떤 모듈도
자신을 가리키는 역방향 import를 갖지 않는다. `mvp` 패키지 안에는 순환
참조가 존재하지 않는다.

### 동적 import

저장소 전체(`find . -name "*.py"`, 224개 파일)에서 `importlib` /
`__import__(` 사용처를 검색한 결과, 일치하는 파일은 2개뿐이었다:

- `archive/v1/adapters/connector-discovery-entrypoint/.../discovery.py`
- `archive/v1/adapters/capability-provider-yaml/.../provider.py`

둘 다 `archive/v1` — Structure v1 Migration 이전의 동결된(frozen) 레거시
코드이며, Development HQ의 Scope Boundary(Kernel/Architecture 경계 우회
금지) 밖에 있다. Development HQ가 실제로 다루는 어떤 모듈에도 동적
import는 없다.

**결론(Evidence)**: 순환 참조·동적 import 경계조건은 Development HQ
Scope 안의 실제 코드에는 존재하지 않는다. `인위적인 복잡성을 만들지
않는다`는 규칙에 따라 이를 인위적으로 재현하는 합성 모듈을 만들지
않았다 — 대신 아래 두 가지로 대체했다.

- 이 경계조건 자체는 **Untestable(Scope 안에 실례 없음)** 으로 기록한다.
- 대신 실제로 존재하는 다른 경계조건, **"대상 파일 자체가 Context에
  포함될 때"** (모듈 수준 import는 있지만 특정 함수에서는 실제로 쓰이지
  않는 경우 포함 여부 판단, 그리고 기존 테스트 파일을 Context로 보여줄
  때의 파일 전체 재작성 여부)를 실제 Task로 검증했다.

## 실험 설계

새 Task: `workflow_0009.run_comparison()`에 대한 real-Engine E2E 테스트
함수 1개를 `mvp/tests/test_workflow_0009.py`에 추가(T12와 동일한 패턴,
다른 대상 함수). Design은 T12 Design을 재사용하지 않고 새로 실행했다
(대상 함수가 다르므로).

`workflow_0009.py`는 모듈 최상단에서 `workflow_0008`을 import하지만
(`from .workflow_0008 import REAL_ISSUE`), `run_comparison()` 본문은
`REAL_ISSUE`를 전혀 참조하지 않는다 — 이는 "모듈 수준 import가 있어도
대상 함수 폐쇄에는 불필요한 경우"를 실제 코드에서 검증할 수 있는
드문 사례였다.

### AST 자동 폐쇄 결과 (재사용: T11/T12 알고리즘)

`run_comparison`을 시작점으로 상대 import(level==1)를 따라 계산한
전이적 의존성:

| 모듈 | 포함된 정의 |
|---|---|
| `workflow_0009` | `run_comparison`, `run_issue_to_planning_with_bundle`, `_enrich_issue_with_bundle`, `_render_context_bundle` |
| `workflow_project_intelligence` | `run_issue_to_planning`, `_enrich_issue`, `_summarize_context` |
| `project_intelligence` | `build_context_bundle`, `collect_relevant_context`, `validate_issue`, `IssueValidationError` 외 helper 전체 |
| `agents` | `requirements_agent_requirement_analysis` |
| `engine` | `call_engine`, `DISALLOWED_TOOLS`, `ENGINE_TIMEOUT_SECONDS`, `STATELESS_CALL_NOTICE`, `ENGINE_CLI` |
| `workflow` | `_engine_failure_message` |

**`workflow_0008`은 포함되지 않았다** — 알고리즘이 `run_comparison`의
실제 사용(Load) 이름만 추적하므로, 모듈 최상단에만 존재하고 함수
본문에서는 죽은(dead) import인 `REAL_ISSUE`를 정확히 걸러냈다. 이는
자동 추출이 "모듈이 import하는 모든 것"이 아니라 "함수가 실제로
필요로 하는 것"을 기준으로 삼는다는 것을 재확인한 사례다(과잉 포함
방지 = 정밀도 경계 통과).

- Automatic 발췌 크기: 10,707자 (6개 모듈)
- Full Source 크기: 25,447자 (7개 파일 — `workflow_0008.py` 포함, 실제로는
  불필요)

## Build 비교

| 조건 | prompt_chars | elapsed | pytest 결과 |
|---|---|---|---|
| A. Automatic (6모듈 발췌) | 16,244 | 16.5s | 6 passed (기존 5개 + 신규 1개, 신규는 real Engine 실행) |
| B. Full Source (7개 파일, `workflow_0008.py` 포함) | 27,678 | 17.8s | 6 passed (기존 5개 + 신규 1개, 신규는 real Engine 실행) |

두 조건 모두 기존 테스트 파일 내용을 Design 입력에 포함시켜(Design이
"기존 4개 테스트를 그대로 유지하라"를 지시할 수 있도록) Build를
실행했다.

### Scope Pollution 재현 여부

T12에서는 Full Source 조건만 파일 전체(기존 4개 테스트 + 신규 1개)를
재생성했고, Manual/Automatic은 신규 함수 1개만 반환했다. 이번에는 **A
(Automatic)와 B (Full Source) 모두 파일 전체를 재생성**했다 — 신규
함수는 정확히 1개씩만 추가됐고, 기존 4개 테스트는 import 구문 추가로
인한 줄 번호 이동을 제외하면 **바이트 단위로 동일**했다(diff로 확인,
본문 변경 없음).

이 차이는 Context 크기(Automatic vs Full Source)가 아니라 **Design
입력에 "수정 대상 파일의 현재 내용"을 보여주었는지 여부**와 상관관계가
있다: T13은 A/B 모두 기존 테스트 파일 전체를 Context에 포함시켰고, 그
결과 둘 다 "전체 파일을 다시 씀"이라는 형식을 택했다. T12의 Full Source만
그런 형태였던 것은 T12의 Manual/Automatic 조건에 기존 테스트 파일
내용이 포함되지 않았기 때문일 가능성이 높다(Context 크기 자체의
문제가 아니라, 파일 가시성의 문제).

즉:

- **내용(Content) 정확성**: Full Source의 "재작성"은 이번 실험에서
  버그가 아니었다 — 기존 테스트는 전부 보존됐고 신규 함수도 정확했다.
- **형식(Format) 특성**: "파일 전체를 다시 쓰는가, 함수만 추가하는가"는
  Full Source 여부가 아니라 "기존 파일 내용이 Context에 노출됐는가"에
  좌우되는 것으로 보인다. Automatic Excerpt도 대상 파일 자체를 Context에
  포함시키면 동일한 전체 재작성 형식을 택했다.

T12의 1회 관찰만으로 "Full Source = Scope Pollution"이라 단정할 수
없다는 뜻이며, 이번 T13 결과가 그 가설을 반증하는 두 번째 데이터
포인트다.

## 판정

**B. Partial — 일부 조건에서 추가 규칙 필요**

- 순환 참조 / 동적 import 경계조건: Development HQ Scope 안에 실례가
  없어 검증 자체가 불가능했다(Untestable, 인위적 복잡성 생성 금지
  원칙에 따라 합성하지 않음).
- 대체 경계조건(모듈 수준 import이지만 함수 내 미사용 / 대상 파일이
  Context에 노출될 때의 전체 재작성)은 통과했다: 자동 추출은 정확히
  불필요한 `workflow_0008`을 배제했고, 재작성 형식이 있어도 내용
  손상은 없었다.
- 완전한 "A. Boundary Validated"로 판정하지 않는 이유: 순환 참조·동적
  import라는 원래 요청된 경계조건 자체가 검증되지 않았기 때문이다.
  이는 알고리즘의 결함이 아니라 검증 대상의 부재이므로, 향후 그런
  코드가 Scope 안에 생기면 별도로 검증이 필요하다(추가 규칙: "순환
  참조가 있는 모듈에서는 폐쇄 알고리즘이 무한 재귀에 빠지지 않도록
  방문 집합(`visited`) 검사를 두고 있는지"는 알고리즘 코드 상으로는
  이미 `visited` set으로 방어되어 있으나, 실제 순환 코드로 실행
  검증된 적은 없다).

## 다음 Task

1. Development HQ Scope 안에서 순환 참조/동적 import가 있는 실제 코드가
   생기면(또는 다른 저장소 Task에서), 그 시점에 이 알고리즘의 `visited`
   기반 방어가 실제로 안전한지 재검증한다(구현 아님, Research로).
2. "Design 입력에 대상 파일의 현재 내용을 포함시키면 Build가 diff가
   아닌 전체 파일을 반환한다"는 이번 관찰을 별도 Research로 세 번째
   데이터 포인트까지 확보해 패턴인지 확인한다(구현 아님).

```text
Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: 36 passed (mvp 전체), 임시 비교 파일(_t13_condition_a.py/_t13_condition_b.py)은 검증 후 삭제, git status clean 확인
E2E: PASS (A, B 모두 real Engine E2E 통과)
PR: NOT CREATED
Commit: (아래 커밋 해시)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: YES
Next Implementation Candidate: (1) 순환 참조/동적 import가 Scope 안에 실제로 생겼을 때 AST 폐쇄 알고리즘의 visited 기반 방어를 재검증하는 Research, (2) "대상 파일 노출 시 전체 재작성" 가설을 세 번째 데이터 포인트로 확인하는 Research (둘 다 구현 아님)
```
