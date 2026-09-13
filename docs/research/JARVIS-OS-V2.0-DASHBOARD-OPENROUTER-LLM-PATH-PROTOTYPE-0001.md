# Dashboard Chat → OpenRouter LLM 경로 Prototype — 조사·구현·검증 Evidence

**Date**: 2026-09-13
**Branch**: main 기준 작업(커밋 전 — Freebuff Changes Panel 경유)
**작업 성격**: Experimental Prototype 범위의 조사·구현·검증. Production
`dashboard/`, `core/`, `hqs/` production path, Frozen Architecture,
Command Contract는 전부 무수정.

## Summary

- Dashboard Chat에 "OpenRouter 기반 LLM 호출 최소 경로"를 **새 client
  구현 없이** 기존 `hqs/development/mvp/openrouter_engine.py`의
  `call_engine_via_openrouter()`(Thin Engine Caller, ADR-0026/0027)를
  함수 객체 그대로 재사용해 연결했다. 조사 결과 이미 존재하는 호출 경로가
  3개(engine.py/omniroute_engine.py/openrouter_engine.py) 모두
  동일 계약(`str -> str`, 단일 `RuntimeError`)을 지키고 있었고,
  Dashboard 전용 LLM client를 새로 만들 필요가 없었다(A 항목 판정).
- Chat → 기존 OpenRouter Engine → 구조화 응답 → 기존 resolver 전체를
  로컬 test double로 검증했다. 신규 테스트 20건 전부 통과, 기존
  관련 스위트 93건 통과, 전체 회귀(수집 에러 11건·실패 8건)는 pristine
  HEAD worktree 재현으로 **사전 존재 확인 — 회귀 0건**(F 항목).
- 모델 독립성 경계가 실제로 성립한다 — Jarvis 코드는 모델을 하나도
  고정하지 않는다. 후보 선정(free pool, 최대 3개)과 실제 모델/failover는
  기존 Engine 모듈과 OpenRouter의 책임이고, 어떤 free 모델이 선택되든
  Dashboard/Command 스키마는 변하지 않는다(E 항목).
- Stop Trigger(G 항목) 전 항목 미발동 — 새 Runtime/Registry/Scheduler/
  Dispatcher/Contract/Baseline 변경 없이 검증이 끝났다. RFC/ADC/ADR
  불필요 판정(아래 Governance 참조).

## 1. 조사 — 기존 호출 구조(A 항목)

| 호출 경로 | 위치 | 계약 | 현재 사용처 |
|---|---|---|---|
| `call_engine()` | `hqs/development/mvp/engine.py` | str → str, RuntimeError | QA Agent(test_execution), Claude CLI |
| `call_engine_via_omniroute()` | `hqs/development/mvp/omniroute_engine.py` | 동일 | 단일 OmniRoute endpoint(로컬 20128) |
| `call_engine_via_openrouter()` | `hqs/development/mvp/openrouter_engine.py` | 동일 | Backend/Requirements/Design Agent(ADR-0027 Migration) |

- 세 경로 모두 `IMPLEMENTATION_RULES.md`의 Thin Engine Caller/Multi-Engine
  Scoped 범위(ADC-0031, ADR-0024) 안의 단일 함수형 Adapter다. Engine
  Gateway/Routing/Policy 추상화는 존재하지 않으며, 존재해서도 안 된다.
- OmniRoute 경로는 로컬 인스턴스(`OMNIROUTE_BASE_URL`, 기본
  `http://127.0.0.1:20128`) 전제라 이 환경에서 실행 불가(미구동 확인).
  OpenRouter 경로는 환경변수만으로 동작하고 free pool 자체 선택을 하므로
  이번 목적(모델 독립성 검증 포함)에 맞는 경로다.
- 판정: **재사용**. `call_engine_via_openrouter()`를 그대로 쓰면 신규
  네트워킹/파싱/retry 코드가 전부 0줄이고, 모델 독립성은 이미 ADR-0026 §7이
  보장한 바를 그대로 얻는다. Dashboard 전용 LLM client는 중복 구현이므로
  만들지 않았다 — 테스트 `test_reuses_existing_engine_function_object`가
  동일 함수 객체임을 검증한다.

## 2. 구현 — 최소 경로(B 항목)

변경 파일 5개, 전부 `projects/dashboard-shell-mvp/` 이내:

| 파일 | 변경 |
|---|---|
| `serve_dashboard.py` | `POST /api/openrouter-command` 핸들러 + `_classify_with_openrouter()`(Engine 출력 파싱 책임 — Engine 모듈 무수정). 기존 `/api/command`, `/api/llm-command` 무수정 |
| `js/data.js` | `runOpenRouterCommand()` 1개 추가(기존 fetch 패턴 동일) |
| `js/app.js` | provider 상태 + 분기(`runChatCommand`), 기존 Claude 경로가 기본값 |
| `js/render.js` | Chat 헤더에 provider `<select>` 1개 |
| `css/dashboard.css` | `.chat-provider` 토큰 1개 |

흐름:

```
Chat input
  → POST /api/openrouter-command
  → call_engine_via_openrouter(prompt)      [기존 Engine, 무수정]
  → _classify_with_openrouter()             [fence/라벨형 편차 복구 → JSON 파싱]
  → {intent, target_hq}                     [기존 Command 스키마 그대로]
  → resolve(command)                        [기존 resolver, 무수정]
  → Dashboard 표시(해석/실행 결과 분리 메시지)
```

- 파싱 책임을 Dashboard 쪽 함수가 진다 — Engine의 `str -> str` 계약은
  건드리지 않는다(계약 변경 = Architecture 변경이므로 의도적 선택).
- 자유모델 응답의 실측 편차(markdown fence, 필드 라벨형 답변)를 복구하는
  최소 정규화 2단계만 두었다. 복구 불가분은 422로 노출한다.
- **Tool 호출 확장 경계 확인**: 분류 결과가 이미 기존 `Command` Contract에
  그대로 들어가고, 실행은 resolver가 전담한다. 향후 Tool 호출이 필요해지는
  지점은 "resolver가 지원하는 intent 집합"이 늘어나는 순간이며, 그 순간
  Command Contract 확장이므로 이번 단계에서는 만지지 않고 테스트
  (`test_llm_unsupported_intent_is_refused_by_resolver`)로 경계만 고정했다.

## 3. 검증 Evidence — 실제 실행 결과(F 항목)

`python3 -m pytest` 실측(이 세션, Python 3.10.12, pytest 9.1.1):

| 스위트 | 결과 |
|---|---|
| `projects/dashboard-shell-mvp/tests/test_openrouter_command.py` (신규) | **26 passed** |
| dashboard 전체 + command-contract + openrouter engine 스위트 | **78 passed** |
| 전체 저장소 `pytest --ignore=archive` (신규 9개 폴더 제외, 1차 세션) | 659 passed, 8 failed, 8 skipped |

- 신규 20건의 커버리지: 정상 요청 E2E(200, ok), fence/라벨형 복구,
  provider 500(502), quota 429(502), 실제 timeout(502), garbage 응답(422),
  잘못된 요청 본문(400), LLM이 trading/deploy/null로 분류해도 resolver가
  거부(Boundary 우회 없음 3건), RuntimeError 매핑, 파싱 단위 3건, 기존
  `/api/command` 회귀, 404, 정적 Boundary 검증 4건(hqs/core 직접 import
  없음, Engine 함수 객체 동일성, 새 client/네트워킹 부재, Contract 파일
  무변경 리터럴).
- **전체 실패/수집 에러의 사전 존재 입증**: `git worktree add`로 pristine
  HEAD를 임시 worktree에 띄워 동일 명령 재실행 → 수집 에러 11건
  (projects/{multi-agent-handoff-mvp-v1, omniroute-thin-engine-caller-v1,
  openrouter-auto-selection-v1, openrouter-free-model-selection-architecture-experiment-v1,
  stage05-parallel-validation-harness-v1, workflow-adapter-*-v1/v2} —
  `domain.*` 모듈 해상도 문제)과 실패 8건(projects/{dev-hq-vertical-slice,
  in-process-async-command, process-runtime-strategy, runtime-boundary})
  **정확히 동일하게 재현**. 이 환경의 사전 존재 결함이며 이번 변경과
  무관하다. 대상 폴더 diff 없음 확인.
- 기존 기능 회귀 없음: `/api/command` E2E 테스트 통과, dashboard/
  command-contract/mvp 엔진 스위트 93건 통과.
- 실제 OpenRouter 네트워크 호출 실측(실패 경로): **1회 수행됨** —
  실제 `serve_dashboard` 서버에서 `OPENROUTER_API_KEY` 없이
  `https://openrouter.ai`로 실제 호출 → 502
  (`category=malformed_response, candidates_tried=3`, Free Pool 조회 →
  chat/completions → bounded retry 전 경로 실측). 오류 메시지에 Key/
  Authorization 노출 없음(확인). 성공 경로(분류 → resolve)는 test double로
  검증 — `OPENROUTER_API_KEY`가 있는 환경에서의 성공 실측은 Remaining.

## 4. Dev HQ 연결 — 가능한 최소 capability(C 항목 판정)

| 후보 | 기존 capability | 이번 단계 판정 |
|---|---|---|
| 1. Dev HQ 상태 조회 | `projects/unified-dashboard/snapshot.py::build_dev_hq_snapshot()` → resolver가 이미 호출 | **이미 연결됨** — resolver 경유로 그대로 동작(추가 구현 불필요) |
| 2. Repository 상태 조회 | 위 snapshot의 stage/currentTask/sourceFiles | 동일 — snapshot Builder가 이미 제공 |
| 3. 개발 작업 intent 해석 | LLM 분류(이번에 OpenRouter 경로 추가) | 분류까지 검증됨 — resolver `_SUPPORTED_INTENTS`에 실행 intent가 없어 **실행은 의도적으로 불가** |
| 4. Dev HQ workflow/capability 호출 | `hqs/development/workflow.py::run_workflow()`, `mvp/workflow.py::run_mvp_0001()` 등 실존 | **호출하지 않았다** — resolver가 Command Layer이고 HQ 의미를 해석하지 않는 기존 경계 유지. 호출하려면 intent→workflow 연결이 필요 = Command Contract 확장 = RFC 대상 |

D 항목(Dashboard → LLM → Dev HQ → capability → Execution → Evidence)의
경계 확인: 이번 구조에서 LLM은 intent/target_hq 분류까지만 담당하고,
실행 책임은 전부 기존 resolver/snapshot Builder에 있다. 향후 확장은
(1) resolver의 intent 집합 확장(Contract 변경), (2) intent→기존 capability
연결(resolver 책임 확장) 두 단계로만 가능하며, 어느 쪽도 이번에
구현하지 않았다 — 새 Agent Runtime/Dispatcher를 설계할 필요가
전혀 관찰되지 않았다.

## 5. Stop Trigger 체크(G 항목)

| 트리거 | 발동 여부 |
|---|---|
| 새 Agent Runtime 필요 | 미발동 — 단일 동기 분류→resolve 흐름으로 충분 |
| Registry 필요 | 미발동 — capability 매핑은 기존 resolver 사전 그대로 |
| Scheduler 필요 | 미발동 |
| Generic Tool Dispatcher 필요 | 미발동 — Tool 호출 요구 자체가 이번 범위에 없음 |
| 새 Command Contract 필요 | 미발동 — `Command`/`CommandResult` 무수정(정적 테스트로 검증) |
| Kernel/Public Contract 변경 필요 | 미발동 |
| Architecture Baseline 변경 필요 | 미발동 — `docs/architecture/baseline/BASELINE.md`, `hqs/development/BASELINE.md` 미접촉 |

## 6. 남은 것

- `OPENROUTER_API_KEY`가 있는 환경에서의 실제 네트워크 실측(응답 시간,
  free 모델의 실제 분류 정확도, fence 편차 빈도). 로컬 test double 검증은
  완료됐다.
- Claude 경로와 OpenRouter 경로의 응답 품질 비교 실측(같은 문장 세트,
  같은 판정 기준).
- intent→Dev HQ workflow 연결은 **Command Contract 확장을 수반하므로**
  별도 RFC → ADC → ADR 대상이다. 이번 Evidence는 그 RFC 작성 시 인용할
  경계 자료다.

## 7. Jarvis OS 전체에서의 의미

- "Dashboard Chat을 Dev HQ Operating Interface로 쓸 수 있는가"에 대한
  최소 답: **분류 계층은 이미 모델 독립적으로 연결 가능**하다(이번
  검증). 실행 계층은 의도적으로 미연결이며, 연결의 유일한 관문은 기존
  Command Contract의 intent 집합이다 — 즉 향후 확장은 Architecture
  설계가 아니라 Contract 확장 절차(RFC) 하나로 귀결된다. 이것이 이번
  Prototype의 핵심 관찰이다.
- Dashboard 전용 LLM client/Engine 추상화를 만들지 않고 기존 Thin Engine
  Caller를 재사용한 선택은, "Dashboard가 Engine 계층의 새 소비자가 되는
  것"과 "Dashboard가 Engine 계층의 새 정의자가 되는 것"을 분리한다 —
  전자는 Governance 개입 없이 가능했고 후자는 발생하지 않았다.

## Governance 판정

- **Architecture/Contract 변경**: 없음. Command Contract, resolver,
  Engine 모듈, Baseline/Freeze 문서 전부 무수정(정적 테스트 포함 검증).
- **RFC/ADC/ADR**: 불필요 — 이번 작업은 `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`
  "Experimental Implementation" 절의 허용 범위(격리 Prototype, Contract
  보호, Frozen Boundary 보호, HQ production path 무단 연결 금지, 검증
  수행)를 그대로 충족한다. intent→workflow 실행 연결을 원할 때가 RFC
  시점이다(§6).
- **PR/branch**: main 기준 작업 트리에만 존재(커밋/푸시는 Freebuff
  Changes Panel 소관 — 이 세션에서 실행하지 않음).
- **테스트 결과**: §3 표 참조(신규 20 passed, 관련 93 passed, 전체
  회귀 0 — 사전 존재 실패는 pristine HEAD 재현으로 입증).
- **실제 Engine/Execution Evidence**: Engine **호출 경로**의 재사용과
  모델 독립성은 로컬 test double로 검증됐다. 실제 외부 Engine 실행
  (OpenRouter 네트워크, Dev HQ workflow 실행)은 이번 단계 범위 밖이며
  발생하지 않았다.
