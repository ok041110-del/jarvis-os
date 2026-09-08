# LLM Wiki Candidate #2 PoC — Pratiyush/llm-wiki

검증일: 2026-09-08
범위: `Pratiyush/llm-wiki` v1.3.82 (LLM Wiki 후보 #2)를 격리된 `claude/*` 브랜치 +
isolated worktree/HOME에서 독립 PoC. Candidate #1(`nvk/llm-wiki`)과 동일 평가 기준 적용.
이 문서는 `.claude/docs/` 규정대로 실행환경 검증 evidence이며 Architecture/RFC/ADC/ADR/
Baseline의 source of truth가 아니다.

## 판정

**CONDITIONAL PASS. Production Adoption으로 승격하지 않는다.** 결정론적
session→markdown 변환, 항상 켜져 있는 항목이 없는(zero auto-injection) 아키텍처, 12개
tool을 노출하는 로그인 불필요 MCP server, 결정론적 lint/build/export, 그리고 keyword
검색이 이전 프로젝트의 Architecture/Decision/Evidence/Open Issue를 정확히 되짚는 능력은
실측으로 확인됐다. 그러나 **공식 문서가 안내하는 Claude Code 연동 두 경로(plugin
marketplace, SessionStart auto-sync hook)가 shipped 상태에서 전부 동작하지 않는다** —
이는 채택 전 upstream 수정 또는 비공식 우회가 필요한 blocker다. redaction은 key-shaped
secret에 대해 Candidate #1보다 강하나 identity/handle leakage와 생성물 파일권한(0644)
문제가 남는다. curated 지식층(entities/concepts/decisions)과 query 최종 답변 품질은 LLM
에이전트 ingest에 의존하며, 이 PoC에서 에이전트 역할을 직접 수행해 구조는 검증했으나
대안 모델·규모에서의 품질은 UNVERIFIED다. 이 PoC는 Jarvis Architecture/Contract/
Governance 변경을 제안하거나 구현하지 않으며, 이 판정은 채택 결정이 아니라 후속
검토·조건 충족을 위한 근거 기록이다.

## 핵심 Evidence 요약 (요구사항 5)

| Evidence | 상태 | 근거 (상세는 아래 해당 §) |
|---|---|---|
| **자동 context injection 0** | VERIFIED | 코드베이스 전체 `additionalContext`/`hookSpecificOutput`/`systemMessage` 0건. 권장 SessionStart hook의 stdout 캡처 = 빈 문자열. wiki는 pull(slash/MCP) 전용, push 없음 |
| **Markdown portability** | VERIFIED | 순수 MD + YAML frontmatter + 상대링크 + `[[wikilink]]`. 표준 뷰어에서 그대로 읽힘, Obsidian optional. `raw/`·`wiki/`는 `.gitignore` 대상 |
| **provenance** | VERIFIED | source 페이지 `sources:` frontmatter가 exact raw 상대경로. `wiki_search`가 커밋 해시(`1309d68`)·ADR 번호를 라인 anchor로 회수. 결정론적 `lint` 25 pages 0 issues |
| **secret redaction** | 부분 VERIFIED | key-shaped secret(GitHub PAT/AWS/Anthropic/OpenAI/Google/Stripe/npm/JWT/PEM)은 config 무관 항상 redact + 테스트 통과. identity/handle(username, `ok041110-del`, scratchpad 경로)은 **미redact = LEAK** |
| **query/search 정확도** | VERIFIED (retrieval) / UNVERIFIED (최종 합성) | `wiki_query`/`wiki_search`가 이전 프로젝트의 Architecture/Decision/Evidence/Open Issue를 상위 결과로 정확 회수. 자연어 최종 답변 합성은 에이전트 대행으로만 확인 |

## 격리 및 범위

| 항목 | Evidence |
|---|---|
| Jarvis 기준점 | `origin/main` `0de386c` (Candidate #1은 `a9a1291` 기준 — 본 리포트 base는 최신 main) |
| PoC branch | `claude/llm-wiki-poc-002` (standalone isolated clone, base `0de386c`) |
| PoC 작업 클론 | `/private/tmp/jarvis-os-llm-wiki-poc-002` (별도 `.git`, main repo와 분리) |
| 후보 source | `https://github.com/Pratiyush/llm-wiki`, tested HEAD `b1088890ee0743810a92577aecad946c6b3eb2d2` (`master`, pyproject `version = 1.3.82`; 최신 tag `v1.3.82` = `83499874`, marketplace.json 동일) |
| 후보 checkout | `/private/tmp/llm-wiki-poc-002/llm-wiki-src` |
| 격리 HOME | `/private/tmp/llm-wiki-poc-002/home` (`HOME`, `XDG_*`, `CLAUDE_CONFIG_DIR`, `PYTHONUSERBASE` 전부 재지정; `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` unset) |
| 격리 Claude 세션 입력 | 실제 `~/.claude/projects/-Users-chan-Developer-jarvis-os/`에서 **읽기 전용**으로 4개 `.jsonl` 복사 → 격리 HOME (`0c715dde`, `6fdc52f1`, `4924975c`, `7d892313`; 총 2,219,103 bytes) |
| 보호 영역 실측 | `~/.claude/settings.json` sha256 `ea64416c…` **변경 전=후 동일**; `~/.omniroute/.env` sha256 `8827a024…` **동일**; `~/.claude-mem` 부재(변경 없음); 실제 project `.jsonl` 46개 → 46개 |
| 알려진 격리 예외 | 실패한 `claude plugin marketplace add` 호출이 `CLAUDE_CONFIG_DIR` 재지정에도 불구하고 실제 `~/.claude/plugins/known_marketplaces.json`을 재직렬화(mtime + `lastUpdated` 갱신). **내용 영향 없음** — 파일은 여전히 기존 `claude-plugins-official` 하나만 나열, llmwiki marketplace/plugin은 전역에 등록되지 않음(내용 직접 확인). `claude` CLI 동작이며 llm-wiki 동작 아님. 이 파일의 PoC 이전 byte 상태는 스냅샷하지 않음 → "미추가"는 VERIFIED, "무접촉"은 아님. |

이 branch의 Jarvis 변경은 이 evidence 문서(`.claude/docs/integrations/llm-wiki-candidate-002-poc.md`)와
`.claude/docs/README.md` 인덱스 1행뿐이다. 후보 설치, 생성된 wiki, 격리 HOME은 모두
`/private/tmp/llm-wiki-poc-002/` 아래에 있다.

## 후보 구조와 연동 조사

- **3계층 Karpathy 모델**: `raw/` (immutable, `.jsonl`→markdown 결정론적 변환) → `wiki/`
  (LLM 유지: `sources/` `entities/` `concepts/` `syntheses/` `comparisons/` `questions/`
  `archive/`) → `site/` (생성 HTML + AI export).
- **스키마/네비 파일**: `CLAUDE.md`(9,987 B), `AGENTS.md`(6,472 B, 비-Claude 에이전트용),
  `wiki/CRITICAL_FACTS.md`(309 B), `wiki/MEMORY.md`(195 B), `wiki/SOUL.md`(211 B),
  `wiki/index.md`, `wiki/overview.md`, `wiki/log.md`.
- **Claude Code 연동 표면 3종**:
  1. **Plugin** (`.claude-plugin/marketplace.json` + `plugin.json`) — commands 7개,
     skills 3개, `hooks/session-start.sh`, `mcpServers.llmwiki = python3 -m llmwiki.mcp`.
  2. **Repo-local** — `.claude/commands/*.md` 18개(`/wiki-sync` `/wiki-ingest` `/wiki-query`
     `/wiki-lint` `/wiki-build` `/wiki-graph` 등) + `.claude/skills/` 6개. Claude Code를
     llm-wiki repo 디렉터리 안에서 실행할 때만 활성.
  3. **SessionStart hook** — `setup.sh`와 `docs/getting-started.md`가 안내하는
     `~/.claude/settings.json` 백그라운드 auto-sync 항목.
- **MCP server** — stdio, 12 tool: `wiki_query`, `wiki_search`, `wiki_list_sources`,
  `wiki_read_page`, `wiki_lint`, `wiki_sync`, `wiki_export`, `wiki_confidence`,
  `wiki_lifecycle`, `wiki_dashboard`, `wiki_entity_search`, `wiki_category_browse`.
  `initialize`/`tools/list`/`tools/call` handshake 실측 성공, 로그인·네트워크 불필요.
- **knowledge model**: `raw/`는 session 사실의 source-of-truth로 취급하되 **truncated·redacted
  요약**이다(원본 `.jsonl` 아님). `wiki/`는 에이전트가 Ingest Workflow(`CLAUDE.md`)를 따라
  수기 작성. `synthesis.backend`는 `dummy`(stub) 기본, `ollama`(localhost), `agent-delegate`
  (에이전트에게 pending prompt 위임) 중 선택.

## 공식 설치 과정의 마찰 (요구사항 3)

실제로 격리 환경에서 공식 순서(`git clone` → `./setup.sh` → 문서의 SessionStart hook
→ plugin marketplace)를 수행하며 수집한 마찰:

| # | 심각도 | 마찰 | Evidence |
|---|---|---|---|
| F1 | **BLOCKER** | **Plugin marketplace 추가 불가.** `claude plugin marketplace add <repo>` → `✘ Failed to parse marketplace file … owner: Invalid input: expected object, received undefined`. `marketplace.json`(v0.1.0)이 `"author": "Pratiyush"` 문자열만 두고 현행 Claude Code 2.1.220 스키마가 요구하는 `owner` object가 없음. 최신 tag `v1.3.82`에서도 동일. → plugin 경로(commands/skills/hooks/MCP 자동 등록) 전체 사용 불가. (Candidate #1은 `wiki@llm-wiki` v0.24.4로 정상 설치됐음) |
| F2 | **BLOCKER** | **문서가 안내하는 SessionStart auto-sync hook이 동작하지 않음.** `setup.sh` 출력과 `docs/getting-started.md` 모두 `(python3 /path/to/llm-wiki/llmwiki/convert.py > /tmp/llmwiki-sync.log 2>&1 &) ; exit 0`을 안내. 이 명령은 어느 cwd에서든 `ModuleNotFoundError: No module named 'llmwiki'` (convert.py:20 `from llmwiki import REPO_ROOT`)로 `exit 1`. 원인: `python3 <path>/convert.py`는 `sys.path[0]`을 스크립트 디렉터리(`llmwiki/`)로 잡아 패키지 루트가 빠지고, `setup.sh`는 `pip install -e .`를 하지 않아 site-packages에도 없음. hook은 `exit 0` + logfile 리다이렉트라 Claude Code에 오류가 안 보임 → **매 세션 조용한 no-op**. 정상 동작하는 형태는 `python3 -m llmwiki sync` (문서화 안 됨). |
| F3 | minor | `setup.sh`/`sync.sh`/`build.sh`/`serve.sh`가 repo에서 mode `100644`(비실행). 문서는 `./setup.sh`라고 안내 → `permission denied`. `bash setup.sh` 또는 `chmod +x` 필요. |
| F4 | minor | `README.md`는 setup이 `pip install -e .`를 한다고 서술하나 실제 `setup.sh`는 `markdown>=3.9`만 `--user` 설치하고 패키지는 미설치. `llmwiki` 콘솔 스크립트 없음 → 모든 호출이 `python3 -m llmwiki …`. |
| F5 | minor | Python 3.9.6(시스템 유일)에서 코어 CLI·테스트는 정상. 단 `graph` extra(`graphifyy`), `e2e` extra(Playwright)는 미검증. LLM synthesis용 실제 backend(ollama/agent) 미구성 시 `wiki/sources/`는 stub 상태 유지(설치 로그가 명시적으로 경고). |
| F6 | minor | plugin이 실제로 로드된다 해도 `plugin.json`이 존재하지 않는 경로를 가리킴: `commands/wiki-init.md`·`skills/llmwiki-sync/SKILL.md`·`hooks/session-start.sh` (실제 파일은 `.claude/commands/`, `.claude/skills/`에 있고 `hooks/`는 아예 없음). |

**결과적으로 채택 가능한 Claude Code 연동은 (a) repo-local `.claude/commands` + `CLAUDE.md`
(cwd가 llm-wiki repo일 때), (b) MCP server 수동 등록, (c) hook을 `python3 -m llmwiki sync`로
직접 재작성 — 셋 다 공식 문서의 1차 안내 경로가 아니다.**

설치 타이밍: `bash setup.sh` 전체 ~1.9s. `python3 -m llmwiki sync`(4 세션, 1.8MB `.jsonl`
포함, auto-build 포함) **1.17s wall** (`/usr/bin/time`: user 1.06s, peak RSS 48 MB).

## Session → Wiki 변환 검증 (요구사항 4)

`python3 -m llmwiki sync` → `raw/sessions/*.md` 4개 생성 (`4 converted, 0 errors`).

### 변환 산출물 구조

- **frontmatter가 풍부**: `sessionId`, `slug`, `project`, `started`/`ended`, `cwd`,
  `gitBranch`, `permissionMode`, `model`, `user_messages`, `tool_calls`,
  `tools_used`/`tool_counts`, `token_totals`(`input`/`cache_creation`/`cache_read`/`output`),
  `turn_count`, `hour_buckets`, `duration_seconds`, `is_subagent`. → Claude-Mem이 노출하지
  않는 정량 메타데이터.
- **본문**: `## Conversation` 아래 `### Turn N — User/Assistant`, 각 턴의 `Tools used` +
  `Tool results`. `drop_thinking_blocks: True`로 thinking 블록 제거.
- **sources/entities/concepts/decisions**: `sync` 자체는 curated 페이지를 만들지 않는다.
  `wiki/sources/`·`wiki/entities/`·`wiki/concepts/`·`wiki/questions/`는 에이전트가
  Ingest Workflow를 따라 작성. **decisions는 별도 폴더가 아니라 `wiki/concepts/`에
  들어간다** (`CLAUDE.md` Ingest §"Extract decisions — … goes into `wiki/concepts/`").
  이 PoC에서 에이전트 역할을 직접 수행해 7개 페이지 작성:
  `sources/3335a107.md`, `sources/token-optimizer-probes.md`, `entities/JarvisOs.md`,
  `entities/LangGraph.md`, `entities/TokenOptimizer.md`, `concepts/WorkflowAdapterContract.md`
  (= decision candidate), `concepts/ReversibilityInvariant.md`,
  `concepts/EvidenceTraceability.md`, `questions/langgraph-public-contract-open-issues.md`.
  dual-link(`[[wikilink]]` + `## Connections`)과 `## Contradictions` 규약을 따름.

### 결정론적 변환의 손실 (중요)

| 관찰 | 수치 |
|---|---|
| `.jsonl` 입력 합계 | 2,219,103 bytes (4 파일) |
| `raw/sessions/*.md` 합계 | 149,310 bytes (**93% 축소**) |
| 예: `4924975c` `.jsonl` 224,276 B → md 4,717 B | tool result truncation |
| `token_totals` 등 메타 | 100% 보존 |

기본 `truncation`: `tool_result_chars: 500`, `bash_stdout_lines: 5`,
`user_prompt_chars: 4000`, `assistant_text_chars: 8000`. → 대형 tool 출력(예: BASELINE.md
전체 Read 100 KB)은 raw 페이지에 **들어오지 않는다**. 긴 `## 최종 보고` 같은 assistant
텍스트(8 KB 미만)는 verbatim 보존됨 — `3335a107.md`(136 KB)는 LangGraph governance 최종
보고, ADC-0019 후속 초안, C1~C3 checkpoint 모델 비교표, E3 Findings 7건을 원문 그대로 담음.

### Markdown portability (요구사항 4)

- 순수 Markdown + YAML frontmatter + 상대 링크 + `[[wikilink]]`. 표준 Markdown 뷰어에서
  그대로 읽힘 (`[[ ]]`는 렌더 안 돼도 텍스트로 보임). Obsidian은 optional.
- `raw/`·`wiki/sources|entities|concepts|syntheses`·`index.md`·`overview.md`·`log.md`·
  `MEMORY.md`·`SOUL.md`·`CRITICAL_FACTS.md`는 전부 `.gitignore` 대상 → 개인 데이터는
  로컬에만, llm-wiki repo에 커밋되지 않음. public deploy는 opt-in + demo 데이터 전용.
- `deterministic lint`(`python3 -m llmwiki lint`): 25 페이지, **0 issues, 0.09s** — source
  provenance, frontmatter, markdown 구조 검사(구조적 lint만; orphan/broken-wikilink/
  contradiction 같은 semantic lint는 에이전트 Lint Workflow 소관).
- AI export: `site/llms.txt`(1.3 KB), `site/llms-full.txt`(9.6 KB), `site/graph.jsonld`
  (2.5 KB, schema.org), 페이지별 `.txt`/`.json` sibling. 전부 로컬 파일.

## Query / Search 검증 (요구사항 6)

curated 층을 채운 뒤 MCP tool로 실측. 대상 질의 = 이전 프로젝트의 Architecture/Decision/
Evidence/Open Issue.

| 질의 | tool | 결과 |
|---|---|---|
| "LangGraph checkpoint ownership model 결정 (C1/C2/C3)" | `wiki_query` | top hit `sources/3335a107.md`(25.3) + `entities/LangGraph.md` + overview. overview가 "C1 채택 + C2 기각" 반환. 실제 결정 페이지(`WorkflowAdapterContract.md`)는 상위 3에 없음 → **ranking 아쉬움**, 사실 자체는 회수됨 |
| "workflow adapter contract 남은 governance 항목" | `wiki_query` | **정확** — `concepts/WorkflowAdapterContract.md`(65.6), `questions/langgraph-public-contract-open-issues.md`(65.0) 상위 2. 7개 open item 원문 반환 |
| "Rule B / E1·E2·E3 independent observations reproducible" | `wiki_query` | **정확** — `concepts/EvidenceTraceability.md`(86.1) #1, "Rule B 미충족 / 재검토 조건 c" 원문 |
| `wiki_search "ADR-0007"` (wiki-only) | `wiki_search` | 라인 단위 정확 매치 2건 (`WorkflowAdapterContract.md:19`, `ReversibilityInvariant.md:11`) |
| `wiki_search "ADR-0007" include_raw` | `wiki_search` | +raw 4건 (`3335a107.md:1991/2004/2603`, ADC-0019 조건 5 인용 포함) |
| `wiki_search "1309d68" include_raw` (정확 커밋 해시) | `wiki_search` | 8건 — merge commit, origin sync 라인, PR #138 표까지 추적 |
| `wiki_entity_search "LangGraph"` | `wiki_entity_search` | 3개 entity 반환(필터 느슨 — 전부 반환하되 순위) |

**결론**: `wiki_search`(결정론적 substring, 라인 anchor)는 커밋 해시·ADR 번호 같은 정확
사실 추적에 신뢰할 만하다. `wiki_query`(결정론적 keyword scoring, LLM 아님)는 "open issue",
"evidence/Rule B" 류 질의에서 정확한 페이지를 상위로 올리나 결정 요약 페이지 ranking은
완벽하지 않다. 최종 자연어 답변은 이 excerpt들을 에이전트가 읽어 합성하며, 그 과정은
자명하게 가능하나 대안 모델·대규모에서의 품질은 **UNVERIFIED**. `wiki_query`는 매 호출에
`overview.md` 전문을 append(고정 오버헤드, overview 성장에 비례).

## Context/token overhead, auto-injection, hook, latency (요구사항 7)

| 항목 | 실측 |
|---|---|
| **자동 주입 범위** | **없음.** 코드베이스 전체에 `additionalContext`/`hookSpecificOutput`/`systemMessage` 0건. SessionStart hook은 background sync만 하고 stdout에 아무것도 쓰지 않음(실측: 권장 hook 형태의 stdout 캡처 = 빈 문자열). wiki는 pull 모델(slash command / MCP tool)이지 push 아님 |
| **항상 켜진 컨텍스트** | plugin 경로 사망 → repo-local `CLAUDE.md`(9,987 B ≈ 2.5–3k tok)는 **cwd가 llm-wiki repo일 때만**. MCP-only 사용 시 항상 켜진 것은 12개 tool 스키마뿐(~1–2k tok). `AGENTS.md`(6,472 B)는 비-Claude 에이전트용 |
| **hook 실행 지연** | 정상 형태 `python3 -m llmwiki sync`: cold/warm sync만 0.03–0.05s, auto-build 포함 시 1.17s. mtime 기반 `.llmwiki-state.json`으로 미변경 세션은 빠른 no-op. 문서 hook 형태(convert.py)는 0.05s에 **crash**(F2) |
| **hook 충돌** | `( … &) ; exit 0` 완전 백그라운드·non-blocking·stdout 없음 → 다른 SessionStart hook의 `additionalContext` concatenation에 기여도 간섭도 없음. **구조적으로 충돌 불가** (Candidate #1 tooling review의 3-way concatenation 우려가 여기선 성립 안 함). 단 정상 형태로 고쳐도 하는 일은 파일 I/O뿐 |
| **중복 저장** | 격리 HOME `.jsonl` 2,172 KB → `raw/` 156 KB + `wiki/` 100 KB + `site/` 2,928 KB. `raw/`는 원본의 redacted·93%-축소 사본(부분 중복), `site/`는 `raw/`+`wiki/`의 HTML 재생성(전량 중복). Claude-Mem과의 중복은 아래 §참조 |

## 보안 (요구사항 8)

| 항목 | 상태 | Evidence |
|---|---|---|
| **key-shaped secret redaction** | **양호 (VERIFIED, 코드+테스트)** | `convert.py`의 `_DEFAULT_TOKEN_PATTERNS`는 config와 무관하게 항상 적용: GitHub PAT(`ghp_`/`gho_`/`ghs_`/`ghu_`/`github_pat_`), AWS `AKIA`, Slack `xox[abprs]-`, Anthropic `sk-ant-api\d\d-`, OpenAI `sk-`/`sk-proj-`/`sk-svcacct-`, Google `AIza`, Stripe `sk_live_`/`pk_live_`, npm `npm_`, JWT 3-segment shape, PEM BEGIN/END. `extra_patterns` 기본값에 `api_key|secret|token|bearer|password` k=v, `sk-…`, 이메일. redaction 테스트 스위트 통과 (`test_default_redaction.py`, `test_username_redact_paths.py`) |
| **이메일 / `/Users/<name>/` 경로** | redact됨 | git author email → `<REDACTED>`; `cwd: /Users/USER/Developer/jarvis-os` |
| **OS username `chan`** | **LEAK (VERIFIED)** | bash tool 결과에 포함된 `ls -la` 출력의 소유자 컬럼(`drwxr-xr-x@ 12 chan staff …`)은 redact 안 됨 — username redactor는 `/Users/<name>/` 경로 패턴만 다룸 |
| **GitHub handle `ok041110-del`** | **LEAK (VERIFIED)** | `raw/sessions/3335a107.md`에 10+회: repo URL, `gh auth status` "Logged in to github.com account ok041110-del (keyring)", PR URL. `wiki_search "ok041110" include_raw`로 전부 회수됨. 어떤 패턴에도 안 걸림 |
| **scratchpad 절대경로 / `-Users-chan-` project dir 명** | **LEAK (VERIFIED)** | `/private/tmp/claude-501/-Users-chan-Developer-jarvis-os/…`, `/Users/USER/.claude/projects/-Users-chan-Developer-jarvis-os/…` — `USER` 치환 후에도 dir 명에 `chan` 잔존, UID 501 노출 |
| **원문(raw transcript) 저장** | 로컬만, 축소·redacted 사본 | `.jsonl` 원본은 복사 안 함. `raw/`는 truncated markdown. `.gitignore`가 `raw/`·`wiki/` 커밋 차단. public deploy 시 GitHub Pages 노출 위험을 코드 주석이 명시(#484) — deploy는 opt-in |
| **파일 권한** | **REGRESSION (VERIFIED)** | 생성된 `raw/`·`wiki/`·`site/` 141개 파일 전부 `-rw-r--r--` (0644, world-readable). 원본 `.jsonl`은 `0600`. 변환이 권한을 넓힘 → 다중 사용자 머신에서 session 내용(불완전 redaction 포함) 노출 |
| **외부 egress** | **없음 (VERIFIED by code-read; runtime packet capture 미수행 → 잔여 UNVERIFIED)** | `dummy`(기본)·`agent-delegate` backend는 네트워크 호출 0 (`agent_delegate.py`: "No network. test suite asserts via socket … No secrets. Works when ANTHROPIC_API_KEY is unset"). `ollama` backend만 `http://localhost:11434`. highlight.js CDN은 브라우저 view-time. `convert.py`/`mcp/server.py`에 `urllib`/`requests`/`socket` outbound 0. `api.anthropic`/`api.openai`/telemetry/analytics 문자열 0 |
| **credential 사용** | **없음 (VERIFIED, 기본/agent 경로)** | 기본·agent-delegate 경로는 `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` 미참조. `ollama`는 키 불필요. 이 PoC는 두 키 unset 상태로 전 과정 수행 |
| **live 답변 품질 / 대안 모델** | **UNVERIFIED** | agent synthesis를 이 세션의 에이전트가 대행함. 다른 모델·규모에서 ingest/query 품질 미측정 |
| **runtime egress 완전 검증** | **UNVERIFIED** | 코드 판독 + 리스너 부재 확인에 근거. 패킷 캡처는 하지 않음 |

## Claude-Mem과의 역할 경계 — Project Knowledge Layer vs Session/Operational Memory (요구사항 6)

**역할 경계 (명시):**

- **Claude-Mem = Session / Operational Memory.** 세션 실행 중 도구 사용을 관찰해 AI
  narrative 요약을 만들고, 다음 세션 시작 시 `additionalContext`로 **자동 주입**한다.
  단위는 "직전 세션들에서 무슨 일이 있었나"이고, 성격은 휘발적·운영적 연속성이다.
  cross-session 작업 재개를 매끄럽게 하는 것이 목적.
- **LLM Wiki = Project Knowledge Layer.** immutable `raw/` 사실 + 에이전트가 큐레이션한
  `wiki/`(sources/entities/concepts/questions) + explicit provenance(`sources:` 경로) +
  dual-link 그래프 + 결정론적 lint/export. 단위는 "이 프로젝트에 대해 무엇이 사실이고
  어떻게 연결되는가"이고, 성격은 영속적·검증 가능·portable하다. **자동 주입하지 않는다**
  — 필요할 때 slash command / MCP tool로 pull한다.
- 두 층은 **보완적이고 겹치지 않는 자리**를 가진다: Claude-Mem은 세션 간 즉시 컨텍스트,
  LLM Wiki는 조회 시점의 구조화된 프로젝트 지식. 같은 세션 transcript에서 파생되므로
  "무슨 작업/결정/파일" 수준의 사실은 중복되지만, 소비 방식(push vs pull), 보존성
  (휘발 vs 영속), 근거성(narrative vs provenance-linked)이 다르다.

이 머신에 Claude-Mem은 현재 미설치(`~/.claude-mem` 부재, npm global 부재,
`~/.claude/settings.json`에 hook 0건). 따라서 **live 병렬 실행 비교는 UNVERIFIED**이며,
아래는 Claude-Mem 통합 문서(`.claude/docs/integrations/claude-mem.md`, v13.14.0)와 Tooling
Finalization Review가 기록한 Claude-Mem 설계 대비 구조 비교다.

| 축 | Claude-Mem | Pratiyush/llm-wiki |
|---|---|---|
| 컨텍스트 전달 | SessionStart hook이 AI 요약을 `additionalContext`로 **push** (자동 주입) | **push 없음** — slash command / MCP tool로만 **pull** |
| lifecycle hook | 5개 (SessionStart, UserPromptSubmit, PostToolUse, Stop, SessionEnd) | 1개 (SessionStart, background sync만) — shipped 형태는 미동작(F2) |
| 저장 형태 | SQLite; `user_prompts` 테이블에 **원문 프롬프트를 평문·무기한·무필터** 저장(Tooling Review Open Issue 1) | Markdown + YAML; `raw/`는 **redacted + truncated**; `.gitignore` 대상; key-shaped secret 다층 redaction |
| 지식 단위 | AI 생성 narrative 요약(세션 간) | immutable `raw/` 사실 + 에이전트 수기 `wiki/` (sources/entities/concepts/questions) + dual-link 그래프 + 결정론적 lint |
| Architecture 근거성 | narrative 재구성 (Tooling Review: verbatim 보존은 UNVERIFIED) | `sources:` frontmatter가 exact raw 상대경로; `wiki_search`가 커밋 해시/ADR 번호 라인 anchor 회수 |
| 정량 메타 | 미노출 | token_totals/tool_counts/gitBranch/model 등 frontmatter |
| 순수 overhead | Tooling Review에서 프롬프트 캐시 잡음으로 분리 실패 → UNVERIFIED | 자동 주입 0이므로 pull 안 하면 0; MCP 스키마 ~1–2k tok |

- **중복**: 둘 다 "이전 세션에서 무엇을 했나"를 되짚는 cross-session recall 기능. 세션
  transcript 유래 정보(무슨 작업, 어떤 결정, 어떤 파일)가 겹친다.
- **llm-wiki가 추가하는 것**: immutable raw layer, explicit provenance(`sources:` 경로),
  dual-link 지식 그래프, 결정론적 lint/graph/export, Markdown portability, 정량 메타데이터,
  자동 주입 0(토큰 예측 가능성).
- **Claude-Mem이 추가하는 것**: 제로-노력 자동 주입(다음 세션이 그냥 알고 시작), AI 요약
  파이프라인 내장(별도 backend 불필요), 5-hook 관찰로 더 촘촘한 캡처.

## Governance Boundary — Wiki는 RFC/ADC/ADR/Baseline/Evidence를 대체하지 않는다 (요구사항 7·9)

**명시된 경계:**

- **Wiki의 `concepts/`·`sources/`는 Governance 규범이 아니다.** RFC/ADC/ADR/BASELINE 및
  `.claude/docs/integrations/` Evidence 문서가 Jarvis Architecture/Governance의 유일한
  source of truth이며, wiki 페이지는 그것들을 **대체하거나 갱신하거나 인용 근거로 승격
  될 수 없다**. wiki `sources/`는 세션 사실의 요약이고, `concepts/`는 그 사실의 파생
  큐레이션일 뿐이다.
- llm-wiki 자체 문서도 이 경계를 뒷받침: `CLAUDE.md` "raw/ … Treat as source-of-truth
  **for facts**" (= session 사실이지 Architecture 규범 아님), `wiki/`는 "summarise,
  cross-reference, synthesise the raw layer". RFC/ADC/ADR/Baseline이라는 개념 자체가 없음.
- **Jarvis에서의 자리**: `.claude/docs/integrations/`와 같은 등급의 **파생 recall 층**.
  Architecture SoT는 여전히 `docs/architecture/baseline/BASELINE.md` +
  `docs/decisions/{rfc,adc,adr}/`. Architecture 변경은 이 PoC와 무관하게 항상
  `RFC → ADC → ADR` 절차를 따른다.
- **리스크와 완화**: `wiki/concepts/*.md`(예: 이 PoC가 만든 `WorkflowAdapterContract.md`)가
  ADR처럼 **권위 있게 보인다**. `type: concept` frontmatter, "초안/승인 대기" 표기,
  `overview.md`의 "이 wiki는 Architecture/Governance의 source of truth가 아니다" disclaimer로
  완화. 채택 시 이 disclaimer를 `SOUL.md`/`CRITICAL_FACTS.md`에 고정하고, wiki 페이지를
  RFC/ADC/ADR **입력 근거로만** 쓰고 **결정 자체로는 쓰지 않는** 운영 규칙을 조건으로
  둔다.
- Candidate #1과 동일 결론: session digest/wiki 페이지는 explicit promotion(#1) 또는
  Governance 절차(#2) 전에는 canonical evidence가 아니다.

## Tests

| 검증 | 실제 결과 |
|---|---|
| `bash setup.sh` (격리 HOME) | PASS — `markdown 3.9` `--user` 설치, `llmwiki init`, adapters, sync status. ~1.9s |
| `python3 -m llmwiki sync` (4 세션) | PASS — `4 converted, 0 unchanged, 0 errors`, auto-build 93 HTML, 1.17s |
| `python3 -m llmwiki lint` | PASS — 25 pages, 0 errors/0 warnings/0 info, 0.09s |
| deterministic pytest (`-k "redact or convert or lint or build or adapter or export"`) | PASS — 547 passed, 1 skipped (Python 3.9.6) |
| pytest `-k redact` | PASS |
| MCP `initialize` + `tools/list` | PASS — server `llmwiki 1.3.82`, 12 tools |
| MCP `wiki_query` / `wiki_search` / `wiki_entity_search` `tools/call` | PASS — §Query 검증 참조 |
| **문서 SessionStart hook** (`python3 …/llmwiki/convert.py`) | **FAIL** — `ModuleNotFoundError: No module named 'llmwiki'`, exit 1, 전 cwd 재현 (F2) |
| **`claude plugin marketplace add`** | **FAIL** — marketplace.json 스키마 검증 실패 (`owner` 누락), plugin install 불가 (F1) |
| repo-local `.claude/commands` 실제 슬래시 실행 | **UNVERIFIED** — 격리 `claude`가 `Not logged in`, live 세션 불가 (Candidate #1과 동일 한계) |
| live model ingest/query 답변 품질 | **UNVERIFIED** — 에이전트 대행으로 구조만 검증 |
| runtime 네트워크 패킷 캡처 | **UNVERIFIED** — 코드 판독 + 리스너 부재로 갈음 |

## Open Issues

1. **P0 / blocker**: `.claude-plugin/marketplace.json`이 현행 Claude Code 스키마(`owner` object)
   미충족 → plugin marketplace 경로 전면 불가 (F1). upstream 수정 필요.
2. **P0 / blocker**: 문서화된 SessionStart auto-sync hook(`python3 …/llmwiki/convert.py`)이
   `ModuleNotFoundError`로 매번 조용히 실패 (F2). `python3 -m llmwiki sync`로 재작성하거나
   `pip install -e .` 후 콘솔 스크립트 사용해야 함 — 어느 쪽도 문서화 안 됨.
3. **P1 / security**: identity leakage — OS username(`ls` 출력 소유자 컬럼), GitHub handle
   `ok041110-del`(`gh` keyring 라인 포함), scratchpad 절대경로/`-Users-chan-` project dir 명이
   `raw/`에 그대로. key-shaped secret redaction은 양호하나 handle/path는 미커버.
4. **P1 / security**: 생성물 파일 권한 0644(world-readable) — 원본 `.jsonl`의 0600 대비 완화.
   다중 사용자 머신에서 불완전 redaction된 session 내용 노출.
5. **P1 / evidence**: live model ingest/query 답변 품질, 실제 token/cache/cost, repo-local
   slash command 및 Claude hook 실동작이 UNVERIFIED (격리 `claude` 미로그인).
6. **P2 / lossy**: 결정론적 변환이 tool 출력을 공격적으로 truncate(`tool_result_chars: 500`)
   → 대형 governance 문서 Read 내용은 `raw/`에 안 들어옴. 사실 링크는 유지되나 evidence
   원문은 아님.
7. **P2 / operations**: curated `wiki/` 층은 에이전트 수기 ingest 필요(자동 아님). `wiki_query`
   결정 요약 페이지 ranking 불완전. `wiki_query`가 매 호출 `overview.md` 전문 append.
8. **P2 / isolation**: `claude plugin marketplace add`가 `CLAUDE_CONFIG_DIR` 재지정에도
   실제 `~/.claude/plugins/known_marketplaces.json`을 touch(내용 무영향). `claude` CLI 동작.
9. **P3 / packaging**: `setup.sh` 등 셸 스크립트 비실행 비트(F3), README ↔ setup.sh
   불일치(F4), `plugin.json` 경로 오참조(F6).

## Cleanup

PR 내용 확인 후 제거 (evidence는 원격 branch + PR에 보존됨):
- `/private/tmp/llm-wiki-poc-002/` (격리 HOME + `llm-wiki-src` checkout + snapshots + demo-backup)
- `/private/tmp/jarvis-os-llm-wiki-poc-002/` (이 branch의 isolated 작업 클론 — push 완료 후 삭제 가능)
- `/tmp/llmwiki-sync.log` (문서 hook이 남긴 crash 로그)
- `claude/llm-wiki-poc-002` branch — PR merge/close 처리 후 원격·로컬 정리
- **되돌릴 것 없음**: 실제 `~/.claude/settings.json`·`~/.omniroute`·`~/.claude-mem`
  미변경(sha 확인). `~/.claude/plugins/known_marketplaces.json`은 touch됐으나 내용상
  기존 상태와 동일(llmwiki 미등록) — 별도 조치 불필요. `~/.local/bin/gh`는 이전 세션이
  설치한 것으로 이 PoC가 만들지 않았고 PR 생성에만 사용, 제거 대상 아님.

## Architecture / Public Contract / Governance

**변경 없음.** Jarvis baseline, RFC/ADC/ADR, Governance, public Contract, OmniRoute,
Claude-Mem, Token Optimizer, Dashboard를 수정하지 않았고 새 component/runtime/interface를
추가하지 않았다. 이 report는 isolated experimental evidence이며 adoption decision이 아니다.
LLM Wiki를 Architecture/Governance Source of Truth로 취급하지 않는다 — §경계/역할 분리 참조.

## Branch / PR 상태

| | |
|---|---|
| PoC branch | `claude/llm-wiki-poc-002` @ base `0de386c` (isolated clone `/private/tmp/jarvis-os-llm-wiki-poc-002`) |
| 이 branch diff | `.claude/docs/integrations/llm-wiki-candidate-002-poc.md` (신규, `projects/…/REPORT.md`에서 이동), `.claude/docs/README.md` (인덱스 1행 추가) |
| main repo 영향 | 없음 — main worktree(`/Users/chan/Developer/jarvis-os`)는 `main` @ `0de386c` clean 유지. 실수로 생성됐던 동명 branch는 삭제(`git branch -D`, 커밋 없었음) |
| Candidate #1 branch | `claude/llm-wiki-poc-001` @ `9628b7d` — 그대로 둠(Candidate #1 evidence 보존) |
| PR | [#161](https://github.com/ok041110-del/jarvis-os/pull/161) `claude/llm-wiki-poc-002 → main` Governance evidence PR. merge는 사용자 승인 대기이며 **Production Adoption 승격 아님** — merge는 채택 결정이 아니라 evidence 기록 |
| Evidence 원격 보존 | branch `claude/llm-wiki-poc-002` @ `e54a799` (초기; 이 표 갱신 후 후속 커밋)를 `github.com/ok041110-del/jarvis-os`에 push 완료 → PoC worktree/HOME/temp 정리 후에도 evidence는 원격 branch + PR #161로 보존됨 |

## Candidate #1 (nvk/llm-wiki) vs Candidate #2 (Pratiyush/llm-wiki)

| 기준 | #1 nvk/llm-wiki (CONDITIONAL PASS) | #2 Pratiyush/llm-wiki (CONDITIONAL PASS) |
|---|---|---|
| isolated clean-home 설치 | plugin `wiki@llm-wiki` v0.24.4 정상 설치·enabled | **plugin marketplace 설치 불가**(schema); **문서 hook 미동작**(import). MCP server·repo-local·`-m llmwiki`는 동작 |
| runtime resolution | Codex verify probe FAIL(격리 cache 무시) | 격리 `claude` 미로그인 → live 세션 UNVERIFIED. MCP는 로그인 불필요, 정상 |
| 보호 경로 diff | 보고서 1개 파일만 | 보고서 1개 파일만. `~/.claude/plugins` 레지스트리 touch(무영향) |
| source immutability / provenance | `sources:` exact raw 경로 요구, lint 검증 | `raw/` immutable + `.gitignore`, `sources:` 경로, `wiki_search` 라인 anchor. 단 변환이 93% truncate |
| source→article link / conflict | dual-link, lint PASS | dual-link, `## Contradictions` 규약, 결정론적 lint 25 pages 0 issues |
| query citation / abstention | 구조·근거·링크 검증, 실모델 답변 UNVERIFIED | `wiki_query`/`wiki_search` 실측 — Architecture/Decision/Evidence/Open Issue 정확 회수. 최종 답변 합성만 UNVERIFIED |
| real model token/cache/cost | UNVERIFIED(clean-home skill 실패 / 미로그인) | UNVERIFIED(미로그인). **자동 주입 0**은 코드로 확정 |
| session capture secret redaction | **P0 FAIL** — `tool_input` k=v secret 미제거 | key-shaped secret 다층 redaction **양호**. identity/handle **LEAK**(username, GitHub handle, path) |
| promotion lint | **P1 FAIL** — 8-space 들여쓰기 → `unterminated YAML` critical | 해당 promotion 메커니즘 없음. 에이전트 수기 ingest → lint PASS |
| Claude-Mem overlap | cross-session memory 중복, 차별점 = immutable raw/provenance/graph/portability | 동일 결론 + "자동 주입 0" 추가 차별점. live 병렬 비교는 UNVERIFIED(Claude-Mem 미설치) |
| LangGraph boundary | read-only query adapter로 결합 가능, 구현 안 함 | 동일 — RFC→ADC→ADR 필요, 이 PoC 범위 밖 |
| Markdown export / cleanup | vendor-neutral MD/YAML, `/tmp` 격리 | vendor-neutral MD/YAML + `.gitignore` + llms.txt/graph.jsonld, `/tmp` 격리 |
| 필수 외부 서비스 / 대체성 | base lint/session은 API 불필요, compile/answer는 LLM/network 의존 | base sync/lint/build/export/MCP는 **네트워크·credential 완전 불필요**. synthesis만 ollama(local) 또는 agent 위임 |
| deterministic + live test evidence | 다수 `test-*.sh` PASS, live lane 미완 | pytest 547 PASS, sync/lint/MCP 실측 PASS, live lane 미완 |

**요약**: #2는 #1의 P0(secret redaction)·P1(promotion lint) 결함이 없고, 자동 주입 0 아키텍처와
네트워크·credential 불필요 코어라는 장점이 뚜렷하다. 대신 #1은 정상 설치되는 plugin을
갖고 있고, #2는 **shipped 상태에서 공식 Claude Code 연동 두 경로가 모두 깨져 있다**는 것이
가장 큰 blocker다. 두 후보 모두 CONDITIONAL PASS이며, #2의 조건은 (a) upstream marketplace.json
스키마 수정 또는 MCP-only 채택, (b) SessionStart hook을 `-m llmwiki sync`로 재작성, (c) raw
handle/path redaction 및 0644 권한 보완, (d) wiki를 규범 아닌 회상 층으로 고정하는 운영 규칙이다.
