# DEV-HQ-V2.0 — Stage 01~04 실제 ChatGPT / Claude Code Engine 연결 조사

**전제**: `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`/
`ADC-0039`(PR #183)가 아직 main에 병합되지 않았다 — 이 문서는 그 PR의
실제 코드(`chatgpt_engine.py`, `engine.py`, Stage 01~04 호출부)를
기준으로 조사하고, 그 Architecture가 승인된 상태를 가정한다. 코드는
변경하지 않는다(사용자 지시 §1 — 조사·연결 Architecture 확정 우선).

---

## 1. 현재 Stage 01~04 Engine 연결 상태(코드 기준, PR #183 재확인)

| 파일 | Import | 대상 Engine |
|---|---|---|
| `agents/requirements.py` | `from ..chatgpt_engine import call_engine_via_chatgpt as call_engine` | ChatGPT |
| `agents/design.py` | 동일 | ChatGPT |
| `workflow_ast_context.py`(Stage 04 Target Identification) | 동일 | ChatGPT |
| `stages/01_context_analysis/reasoning.py` | `from mvp.chatgpt_engine import call_engine_via_chatgpt as call_engine` | ChatGPT |
| `stages/02_planning_specification/task_dependency_agent.py` | 동일 | ChatGPT |
| `agents/backend.py::backend_agent_code_review` | `from ..chatgpt_engine import call_engine_via_chatgpt as call_engine_review` | ChatGPT |
| `agents/backend.py::backend_agent_code_generation` | `from ..engine import call_engine as call_engine_generation` | Claude Code |
| `agents/qa.py::qa_agent_test_execution` | `from ..engine import call_engine` | Claude Code |

Import 배선은 정확히 사용자가 이번에 제시한 목표(§1)와 일치한다 —
코드 조사 결과 **불일치 없음**.

---

## 2. ChatGPT 실제 연결 방법 조사

`chatgpt_engine.py`(PR #183) 구현:

- **SDK**: 사용하지 않음 — `http.client`(stdlib)만 사용(OmniRoute Thin
  Caller와 동일 패턴, 외부 의존성 0).
- **API 형태**: OpenAI **Chat Completions**(`POST /v1/chat/completions`).
  **Responses API(`/v1/responses`)는 사용하지 않는다.**
- **model**: 환경변수 `CHATGPT_MODEL`(기본값 `gpt-4o`).
- **API Key**: `OPENAI_API_KEY` 환경변수에서만 읽음 — 하드코딩 없음
  (코드 재확인, `sk-` 리터럴 grep 0건).
- **timeout**: `CHATGPT_TIMEOUT_SECONDS`(기본 180초), `http.client`
  connection-level timeout으로 적용.
- **retry**: 없음 — Thin Caller 설계상 의도적(단일 호출, 실패는
  그대로 `RuntimeError`로 전파).
- **error handling**: 401/403(auth)/429(rate limit)/5xx(provider)/
  4xx(call error)/timeout/connection 전부 구분된 메시지의 단일
  `RuntimeError`로 매핑.
- **output parsing**: `choices[0].message.content`만 추출(OpenAI
  Chat Completions 표준 스키마).
- **logging/cost instrumentation**: 없음 — `usage` 필드를 파싱하지
  않고 버린다(OmniRoute Thin Caller와 동일 설계 원칙, Contract를
  단순하게 유지).

### OpenAI 공식 문서와의 비교(제약 있음 — 아래 참조)

이 세션 환경에서 `platform.openai.com`/`api.openai.com`에 대한
egress가 **모두 차단**되어 있어(§4 재확인), OpenAI 최신 공식 문서를
이번 세션에서 직접 열람하지 못했다(`WebFetch`가
`EGRESS_BLOCKED(platform.openai.com)`으로 실패). 따라서 아래는
**학습 데이터 기준 판단이며 이번 세션에서 라이브 검증하지 못했다**는
점을 명시한다:

- OpenAI는 2025년부터 도구 사용/에이전틱 워크플로우를 위한
  **Responses API**를 새 통합의 기본 권장 경로로 안내해 왔다(모델의
  reasoning trace 유지, built-in tool 연동 등). 그러나 **Chat
  Completions API 자체가 폐기(deprecated)된 것은 아니며**, 단순
  text-in/text-out 호출(도구 사용 없음, streaming 없음, 상태
  비저장)에는 여전히 널리 쓰이고 충분하다.
- 이 저장소의 요구(Stage 01~04의 `str -> str` 단일 호출, 도구 미사용,
  상태 비저장)는 Chat Completions로 충분한 범위다 — Responses API로
  옮겨야 할 **기능적 필요는 지금 관찰되지 않는다.**
- **Open Issue로 기록**: 실제 배포 전에 OpenAI 공식 문서를 egress가
  허용된 환경에서 재확인해, Chat Completions가 여전히 활성 지원
  상태인지(모델별 최소 지원 API가 Responses로 좁혀지는 경우가
  있는지) 확인이 필요하다. 이번 세션은 이 확인을 완료하지 못했다
  (BLOCKED로 기록, 억지로 라이브 검증했다고 서술하지 않는다).

### Real Engine 연결 시도 결과

```
$ curl -sS -o /dev/null -w "HTTP_STATUS=%{http_code}" https://api.openai.com/v1/models
curl: (56) CONNECT tunnel failed, response 403
```

이 세션의 Agent Proxy 상태(`$HTTPS_PROXY/__agentproxy/status`)가
직접 확인해 준다:

```json
"recentRelayFailures": [{
  "kind": "connect_rejected",
  "detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
  "host": "api.openai.com:443"
}]
```

**결론: ChatGPT Real Engine Connection = BLOCKED(이 세션/이
환경의 network egress policy가 `api.openai.com`을 명시적으로
거부함).** `OPENAI_API_KEY` 자체도 이 환경에 설정되어 있지 않다
(env 전수 확인). 코드 구현의 결함이 아니라 **이 실행 환경의 egress
allowlist 제약**이다 — 실제 Jarvis 운영 환경(사용자의 실제 배포
대상)에서 `api.openai.com`이 허용되어 있는지는 별도로 확인해야
한다(이 세션은 그 환경을 대표하지 않는다).

---

## 3. Claude Code 실제 연결 방법 조사(핵심)

### 3.1 CLI 존재 및 기본 동작 확인

```
$ which claude
/opt/node22/bin/claude
$ claude --version
2.1.269 (Claude Code)
$ claude -p "Reply with exactly the word: PONG" --output-format text
PONG
(exit code 0)
```

**Non-interactive(headless) 실행이 실제로 가능하다** — `-p`/`--print`
플래그로 대화형 세션 없이 단일 응답을 받는다(`engine.py`가 이미 이
방식을 쓴다).

### 3.2 현재 `engine.py`가 실제로 하는 것 — Text Mode(A에 해당)

```python
subprocess.run(
    [ENGINE_CLI, "-p", prompt, "--output-format", "text",
     "--disallowedTools", "Write,Edit,Bash,Read,Glob,Grep,NotebookEdit,WebFetch,WebSearch",
     "--append-system-prompt", STATELESS_CALL_NOTICE],
    cwd=tempfile.gettempdir(), timeout=180,
)
```

이 세션에서 `mvp/engine.py::call_engine()`을 **실제로 그대로
실행**해 재확인했다:

```
call_engine("Reply with exactly the word: PONG2")
→ 'PONG2\n' (성공, 3.8초)
```

**Claude Code Text Mode Engine = 실제로 연결되어 동작한다**(Real
Engine Evidence 확보, 이 세션의 실제 계정/네트워크로 호출됨 —
`api.anthropic.com`은 이 환경의 egress allowlist에 포함되어 있어
차단되지 않는다).

이 모드는 사용자가 구분한 **A(Claude API처럼 text만 주고받는 모드)**에
해당한다 — `disallowedTools`가 filesystem/shell/git 접근을 전부
차단하고 `cwd`를 저장소 밖으로 고정하기 때문이다. **이것은 사용자가
정의한 B(Repository Execution)가 아니다.**

### 3.3 Claude Code가 실제로 Repository에 접근할 수 있는가 — 별도 실측(중요)

**추측하지 않고 실제로 확인했다.** `disallowedTools` 없이, 실제
git repository(테스트용 격리 디렉터리, `/tmp/claude-code-repo-test`,
Production 저장소 아님)를 대상으로 headless 실행:

```
$ git init && echo 'def add(a,b): return a+b' > mod.py && git commit ...
$ claude -p "In the file mod.py, add a one-line docstring..." \
    --output-format text \
    --allowedTools "Read,Edit" \
    --permission-mode acceptEdits
→ "Done — added `\"\"\"Add two numbers.\"\"\"` as the docstring." (exit 0)

$ git diff
+ """Add two numbers."""
```

**결론: Claude Code CLI는 headless 모드에서도 실제로 파일을 읽고
수정할 수 있다(B가 기술적으로 실제 가능함을 실측으로 확인).**
핵심 메커니즘:

| 항목 | 확인 결과 |
|---|---|
| Non-interactive/headless 실행 | `-p`(`--print`)로 가능, 이미 `engine.py`가 사용 중 |
| Repository working directory 지정 | `subprocess.run(..., cwd=<repo_path>)` — 프로세스 `cwd`가 곧 Claude Code의 작업 디렉터리 |
| Prompt 전달 | 위치 인자(`claude -p "<prompt>"`) |
| stdout/stderr 처리 | `capture_output=True` — `engine.py`가 이미 이 패턴 사용 |
| exit code 처리 | 0=성공, 비0=실패(`engine.py`의 기존 처리와 동일 패턴 재사용 가능) |
| 변경 파일 감지 | Claude Code 자체 기능 아님 — 호출자가 `git status`/`git diff`로 확인(Stage 04 `VALIDATION.md`의 real E2E 절차와 동일 방법론) |
| 권한/approval 처리 | `--permission-mode acceptEdits`(Edit/Write 자동 승인) 또는 `--allowedTools`로 도구별 화이트리스트, 또는 `--allow-dangerously-skip-permissions`(전체 우회, 비권장) |
| sandbox 여부 | 이 세션 자체가 컨테이너 격리 환경 — Claude Code 자체의 별도 sandbox 계층은 없음(호출자가 디렉터리/도구 범위로 통제) |
| 환경변수 전달 | `subprocess.run(..., env=...)`로 표준 상속/override 가능(`engine.py`는 현재 명시하지 않아 부모 프로세스 env를 그대로 상속) |
| timeout | `subprocess.run(..., timeout=...)` — `engine.py`가 이미 180초로 설정 |

### 3.4 A(Claude API) vs B(Claude Code) 구분 재확인

- **A**: `engine.py`의 현재 방식 — `disallowedTools`로 전 도구 차단,
  `cwd`를 저장소 밖으로 고정. 순수 `str -> str`. **이것은 사실상
  Claude API를 CLI로 감싼 것과 동등하다**(도구가 없으므로).
- **B**: §3.3에서 실측한 방식 — 실제 저장소 `cwd`, `allowedTools`에
  Read/Edit(필요시 Write/Bash) 포함, 파일을 직접 읽고 수정. **이것이
  Stage 04가 실제로 요구하는 것**(사용자 지시 §4)이다.

**현재 Production 코드(`engine.py`)는 A만 구현되어 있다.** B는 이
세션에서 격리된 테스트로 기술적 가능성만 실측했을 뿐, Production에
연결되어 있지 않다.

---

## 4. Connection Architecture 옵션 비교

| 기준 | Option 1(Jarvis→Claude Code CLI→Repo) | Option 2(Jarvis→Claude API+tools→Repo) | Option 3(Jarvis→별도 Execution Adapter→Claude Code→Repo) |
|---|---|---|---|
| 실제 Repository 수정 가능 여부 | **실측 확인됨(§3.3)** | 가능(Anthropic Messages API의 tool-use로 Jarvis가 직접 파일 I/O 도구를 구현해야 함) — 이 세션에서 구현/실측하지 않음 | Option 1과 동일 메커니즘 + 별도 격리 계층 |
| Engine Contract와의 적합성 | 기존 `subprocess` 패턴 재사용 — Contract는 확장 필요(§5) | Jarvis가 tool-loop을 직접 구현해야 해 Contract가 더 복잡해짐(멀티턴 상태 필요) | Option 1과 동일 + Adapter 자체의 Contract 추가 필요 |
| 보안/권한 경계 | `--allowedTools`/`cwd`로 Jarvis가 직접 통제 — 명확 | Jarvis가 tool 실행기를 직접 구현해야 해 통제 로직이 Jarvis 코드 안으로 들어옴(Policy 로직 증가 위험, `IMPLEMENTATION_RULES.md` 17행과 긴장) | Adapter가 통제를 대신 — 경계는 명확하나 계층이 하나 더 생김 |
| Deterministic Validation과의 연결성 | 자연스러움 — Claude Code 실행 후 `git diff`/`pytest`를 Jarvis가 그대로 이어서 실행(Stage 04 `VALIDATION.md` 절차와 동일 방법론, PR #180 Harness와도 호환) | 가능하나 Jarvis가 tool 실행 자체도 구현해야 하므로 중복 | Option 1과 동일 |
| 비용 측정 가능성 | Claude Code CLI가 `--output-format json`으로 실행 시 사용량 메타데이터를 포함할 수 있음(이번 세션에서 `text` 포맷만 확인, `json` 포맷 실측은 미수행 — Open Issue) | Anthropic Messages API 응답에 `usage` 필드가 표준으로 포함(SDK 사용 시 직접 확인 가능) | Option 1과 동일 |
| latency 측정 가능성 | 가능(subprocess 실행 시간 측정, 이미 `omniroute_engine.py`/`chatgpt_engine.py`가 쓰는 `perf_counter` 패턴 재사용 가능) | 가능 | 가능 |
| 구현 복잡성 | **낮음** — 기존 `engine.py` 패턴에 `cwd`/`allowedTools`/`permission-mode` 인자만 바꾸면 됨 | **높음** — tool-use loop, 파일 I/O 도구 정의, 상태 관리를 Jarvis가 새로 구현해야 함 | **중간** — Option 1 메커니즘 + Adapter 계층 신설 |
| 기존 Governance와의 충돌 | `ADR-0024` §Non-goal("LLM에게 실제 filesystem/shell 접근 권한을 주는 것은 이 ADR이 승인하지 않는다")과 **정면으로 충돌** — 채택하려면 별도 RFC→ADC→ADR 필요 | 동일하게 `ADR-0024` §Non-goal과 충돌 + `IMPLEMENTATION_RULES.md` 17행(Policy 로직 금지)과도 긴장(도구 실행 판정 로직이 Jarvis 코드에 생김) | 동일 충돌 + `IMPLEMENTATION_RULES.md` 15행(Engine Gateway 금지) 위반 위험(Adapter가 일반화된 추상화가 되면) |

**이번 세션의 판단**: 세 Option 모두 "Repository Execution(B)"을
채택하려면 `ADR-0024` §Non-goal을 재검토하는 새 Governance
절차(RFC→ADC→ADR)가 필요하다 — 이 문서는 그 절차를 대신하지
않는다. **지금 코드 변경 없이 연결 가능한 것은 A(Text Mode)뿐**이며,
이는 이미 Production에 존재하고(§3.2) 실제로 동작한다(§3.2 재확인).

---

## 5. Engine Contract 검증

**현재 `str -> str` Contract는 A(Text Mode) 범위에서는 충분하다** —
근거: Stage 04 `RESPONSIBILITY.md`가 이미 "생성된 Code를 실제
저장소 파일에 적용하는 것은 Stage 04의 책임이 아니다"라고 명시했고,
현재 Production Claude Code Engine(`engine.py`)도 파일을 쓰지
않는다(§3.2). 즉 현재 Architecture는 **A로 설계되어 있고, 그 설계
안에서 Contract는 이미 충분하다.**

**B(Repository Execution)를 채택하면 Contract는 불충분해진다** —
아래 필드가 없으면 호출자가 "무엇이 실제로 바뀌었는지" 알 수 없다:

- `exit_status`(성공/실패)
- `changed_files`(수정된 파일 목록)
- `diff`(실제 변경 내용 — Stage 05/Deterministic Gate가 지금처럼
  텍스트 하나만으로 검증할 수 없게 됨)
- `test_result`(선택 — Claude Code가 직접 `pytest`를 실행했다면)
- `execution_error`(도구 실행 자체의 실패, LLM 응답 실패와 구분 필요)

**이번 단계 결론(사용자 지시 §7 그대로 따름)**: B를 채택할지는
아직 결정되지 않았으므로 **Contract를 지금 변경하지 않는다.** B가
실제로 필요하다고 Governance가 판단하면, 새 Result 스키마(위 5개
필드)가 필요하다는 것을 Architecture/Governance 영향으로만 기록한다
— 코드 구현은 그 이후 별도 RFC→ADC→ADR 완료 후 진행한다.

---

## 6. Stage 01~04 연결 방식 확정(사용자 지시 §8 표)

| Stage | 작업 | Engine | 실제 연결(코드 배선) | 실행 형태 | Real Engine 실행 결과 |
|---|---|---|---|---|---|
| 01 | Context | ChatGPT | 연결됨(`chatgpt_engine`) | HTTP(Chat Completions) | **BLOCKED**(egress) |
| 02 | Specification | ChatGPT | 연결됨 | HTTP(Chat Completions) | **BLOCKED**(egress) |
| 03 | Design | ChatGPT | 연결됨 | HTTP(Chat Completions) | **BLOCKED**(egress) |
| 04 | Target Identification | ChatGPT | 연결됨(`workflow_ast_context.py`) | HTTP(Chat Completions) | **BLOCKED**(egress) |
| 04 | Code Generation | Claude Code(Text Mode, A) | 연결됨(`engine.py`) | subprocess(`claude -p`, 도구 차단) | **CONFIRMED — 실제 호출 성공**(`PONG2`, 3.8초, exit 0) |
| 04 | Validation | Deterministic | N/A | 순수 Python(`ast`/`builtins`) | 해당 없음(Engine 미사용, PR #180 Harness가 이미 검증) |

**"실제 연결"은 import 존재가 아니라 실제 Engine 실행 성공 여부로
판단했다**(사용자 지시 §8 원칙) — ChatGPT 4곳은 코드 배선은 정확하지만
이 환경에서 네트워크가 막혀 있어 실행 자체를 확인하지 못했고, Claude
Code Text Mode 1곳(Code Generation)만 실제 실행까지 확인됐다.

---

## 7. 구현 범위(계획만, 이번 세션에서 실행하지 않음)

### 원칙 준수 확인

- Central Router/Gateway 없음 — 여전히 파일 import 시점 정적 선택.
- Engine 선택 로직을 하나의 Router에 모으지 않음 — 유지.
- 정적 Engine 분리 — 유지(`ADR-0024` Stage Mapping 그대로).
- API Key 환경변수 — `OPENAI_API_KEY`/`ANTHROPIC_*`(Claude Code CLI
  자체 인증, Jarvis 코드가 별도로 관리하지 않음) 유지.
- Stage Contract — 이번 계획은 변경하지 않는다(§5 결론).
- Production Multi-Agent/Ponytail 구현 — 포함하지 않음(`ADC-0040`과
  동일 원칙 — Single Agent Real Baseline 우선, §11).
- OmniRoute 재도입 없음 — 계획에 포함 안 함.

### 실제 계획(향후 세션 실행 대상, 이번 세션은 계획만)

1. **ChatGPT 연결 검증**: 이 환경이 아닌, `api.openai.com` egress가
   허용되고 `OPENAI_API_KEY`가 설정된 환경에서
   `chatgpt_engine.call_engine_via_chatgpt("ping")` 1회 호출로 연결
   자체를 확인한다(코드 변경 없음, 순수 실행 검증).
2. **Claude Code Text Mode 연결 검증**: 이미 이번 세션에서 완료됨
   (§3.2) — 추가 작업 불필요.
3. **B(Repository Execution) 채택 여부**: 별도 RFC 작성 — `ADR-0024`
   §Non-goal 재검토, Contract 확장안(§5 5개 필드) 구체화, 보안
   경계(`--allowedTools` 화이트리스트 최소 원칙) 명시. 이 RFC 이후
   ADC→ADR을 거쳐야만 코드 변경에 착수할 수 있다.
4. **Cost/Latency 계측**: `chatgpt_engine.py`/`engine.py` 양쪽에
   `cost_instrumentation.py`(PR #180 패턴, 이미 검증된 방식) 적용
   가능성 검토 — 이번 세션은 검토만, 구현하지 않음.

---

## 8. 실제 E2E 계획 및 현재 실행 가능 여부

| 단계 | 실행 가능 여부(이 환경) |
|---|---|
| Stage 01 ChatGPT 실제 호출 | **BLOCKED**(egress) |
| Stage 02 ChatGPT 실제 호출 | **BLOCKED**(egress) |
| Stage 03 ChatGPT 실제 호출 | **BLOCKED**(egress) |
| Stage 04 Target ChatGPT 실제 호출 | **BLOCKED**(egress) |
| Stage 04 Code Generation Claude Code 실제 실행 | **가능 — 확인됨**(§3.2) |
| Stage 04 Deterministic Gate | 가능(Engine 불필요, PR #180 Harness로 이미 검증) |

**전체 E2E(Stage01→04 전 구간)는 이 환경에서 완주할 수 없다** —
ChatGPT 구간 4곳이 전부 BLOCKED이기 때문이다. Claude Code 구간만
독립적으로 실행 가능함을 확인했다(§3.2).

---

## 9. Open Issues

1. OpenAI Chat Completions API가 여전히 활성 지원 상태인지 공식
   문서로 라이브 재확인 필요(이 세션은 egress 차단으로 미확인, §2).
2. `api.openai.com` egress 허용 여부는 실제 배포 환경마다 다를 수
   있다 — 이 세션의 BLOCKED 판정을 다른 환경에 일반화하지 않는다.
3. Claude Code CLI `--output-format json`의 실제 cost/usage 필드
   존재 여부 미실측(§4 비용 측정 가능성 행).
4. B(Repository Execution) 채택 여부와 그에 따른 Contract 확장은
   별도 RFC 대상 — 이번 세션은 착수하지 않는다.
5. Claude Code Text Mode의 실제 latency(3.8초, 1회 관측)는 표본이
   1건뿐이라 대표값으로 쓰지 않는다 — 반복 측정 필요.

## 10. Architecture / Contract 변경 여부

**둘 다 없음.** 이번 세션은 조사만 수행했다 — `ADR-0024` Stage
Mapping, Engine Contract(`str -> str`) 전부 무변경으로 유지된다.
