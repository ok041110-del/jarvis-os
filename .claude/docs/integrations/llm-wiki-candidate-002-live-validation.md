# LLM Wiki Candidate #2 — Live Validation

## 목적

Candidate #2(`Pratiyush/llm-wiki` v1.3.82)의 P0/P1 Resolution([PR #162](https://github.com/ok041110-del/jarvis-os/pull/162)) 이후,
**실제 로그인된 Claude Code**에서 최종 통합 가능성을 검증한다. 현재 판정은 CONDITIONAL
PASS이며 이 검증은 Production Adoption 상향 여부 판단용 근거다 — 검증 결과와 무관하게
이 PR로는 상향하지 않는다. `.claude/docs/` 규정대로 실행환경 검증 evidence이며
RFC/ADC/ADR/Baseline의 source of truth가 아니다.

## 환경

| 항목 | 값 |
|---|---|
| branch | `claude/llm-wiki-poc-002-live`, base `origin/main` `0de386c` |
| isolated jarvis clone | `/private/tmp/llm-wiki-poc-002L/jarvis` (별도 `.git`) |
| 후보 checkout + patch | `/private/tmp/llm-wiki-poc-002L/src` (upstream HEAD `b1088890` + P0 patch 재적용: `marketplace.json` owner/source, `plugin.json` commands/skills, 신규 `hooks/hooks.json`, `examples/sessions_config.json` redaction) |
| Claude Code | **2.1.261**, **실제 로그인 계정 사용** (nested `claude -p`) |
| MCP 등록 방식 | `--mcp-config` (임시 JSON, `~/.claude/settings.json` 미변경) |
| hook 검증 방식 | isolated worktree의 **project-level** `.claude/settings.json` (`~/.claude` 미변경) |
| plugin load 검증 | **isolated `CLAUDE_CONFIG_DIR`** (로그인 안 됨) — 로그인+plugin 동시 불가(제약) |
| 격리 원칙 | 실제 `~/.claude/settings.json`·`~/.claude-mem`·`~/.omniroute` 미변경. nested 세션 transcript는 `~/.claude/projects/-private-tmp-llm-wiki-poc-002L-src/`에 생성 후 정리 |

### 구조적 제약 (측정 불가 사유)

- **로그인 + 격리 config 동시 불가**: `CLAUDE_CONFIG_DIR`를 격리하면 `claude`는 "Not
  logged in"(keychain 인증이 default config에 묶임). 로그인된 세션은 실제 `~/.claude`를
  쓴다.
- 따라서 **로그인된 세션에서의 `claude plugin install`/plugin enabled 상태**는 실제
  `~/.claude/plugins`·`settings.json`을 건드려야 하므로 제약상 수행 불가 →
  **UNVERIFIED (constraint-blocked)**. 대신 plugin과 동일 표면(project `.claude/commands/`
  + `CLAUDE.md` + `--mcp-config` MCP)을 로그인 세션에서 검증했고, plugin 로드 자체는
  격리 config에서 `✔ enabled` 재확인.

## Live Test

| # | 항목 | 방법 | 결과 |
|---|---|---|---|
| A | marketplace add/install | 격리 `CLAUDE_CONFIG_DIR` + patched 후보 | **PASS** — `✔ Successfully added marketplace: llmwiki` / `✔ Successfully installed plugin: llmwiki@llmwiki` |
| B | plugin enabled 상태 | `claude plugin list` (격리 config) | **PASS** — `❯ llmwiki@llmwiki … Status: ✔ enabled`; commands 18 / skills 6 / MCP `python3 -m llmwiki.mcp` resolve. **로그인 세션 내 enabled 상태는 UNVERIFIED (constraint-blocked)** |
| C | SessionStart hook 실제 실행 | project `.claude/settings.json` hook, `claude -p` from project root | **PASS (부분)** — hook 발화 확인(`hook-fired.log` 생성, `umask 077` → `-rw-------`), 세션은 즉시 응답 반환(non-blocking) |
| D | 임의 cwd에서 hook 실행 | `claude -p` from `hooktest/sub/deeper` | **INCONCLUSIVE** — 이 실행에서는 project hook이 발화한 흔적 없음(로그 미생성). hook body 자체가 임의 cwd에서 동작함은 Resolution PoC에서 `/tmp` 실행으로 입증됨(`cd "${CLAUDE_PLUGIN_ROOT}"`); Claude Code가 **깊은 subdir에서 ancestor project hook을 로드하는지**는 이 세션에서 **UNVERIFIED** |
| E | `/wiki-sync` 실제 실행 | `python3 -m llmwiki sync --include-current` (patched hook body와 동일) | **PASS** — `1 converted, 0 errors` (scoped). 단, 실제 `~/.claude` HOME으로 무-scope 실행 시 **claude_code 79 + codex_cli 53 = 129 세션 전량 변환**(실측) — hook은 `include_projects` scoping 또는 격리 HOME과 반드시 병행해야 함 |
| F | `/wiki-query` 실제 실행 | nested `claude -p` + `--mcp-config`(llmwiki MCP), 4-query battery | **PASS** — 아래 Query §. slash command 리터럴(`/wiki-query`) 실행은 project `.claude/commands/`로 로드되나 이 세션에서는 MCP tool 경로로 검증 |
| G | `wiki_search` 실제 실행 | nested `claude -p` MCP tool call | **PASS** — `wiki_search "0de386c" include_raw` → `WorkflowBoundaryDecision.md:12` + `raw/…:44,54` 라인 anchor |
| H | provenance / commit hash / ADR anchor 회수 | 동상 | **PASS** — commit `0de386c`·`45d4c2d`, `RFC-0019 → ADC-0019 → ADR-0008` 전부 라인 단위 회수 |
| I | 자동 context injection 없음 | hook 세션 결과·A/B usage 분석 | **PASS** — hook cmd는 logfile + `exit 0`만, SessionStart stdout이 context로 안 들어감. 세션 결과에 wiki 내용 주입 흔적 0. 코드 전체 `additionalContext`/`hookSpecificOutput` 0건 |
| J | plugin/MCP always-on overhead | A/B (§Token/Context) | MCP tool schema ≈ **+300 tokens cache-creation** (n=2, low-confidence). `CLAUDE.md` ~10KB는 cwd=repo일 때 상주(두 arm 공통이라 분리 안 됨) |

## Session → Wiki

로그인 세션 1건(`live-test`, sessionId `0d8588c9`, model `claude-sonnet-5`)에서 7개
지식 항목을 의도적으로 발생시키고 `llmwiki sync --include-current`(격리 HOME, scoped)로
변환.

| 항목 | raw/ (`raw/sessions/2026-09-08T04-31-live-test-3181c17b.md`) | source/ (`wiki/sources/`) | wiki (`concepts/`, `questions/`) |
|---|---|---|---|
| **Goal** | ✅ 본문 verbatim (User + Assistant 턴 중복) | 에이전트 ingest 시 `## Summary`로 요약 | — |
| **Decision** | ✅ verbatim | ✅ `## Key Claims`에 "vendored-fork 채택"으로 | ✅ `concepts/llmwiki-candidate2-patch.md` |
| **Progress** | ✅ verbatim | ✅ `## Key Claims` | — |
| **Open Issue** | ✅ verbatim (단 §Security 참고 — 오탐 redaction 발생) | ✅ `## Key Claims` | ✅ `concepts/llmwiki-candidate2-patch.md` "Open Issue" |
| **Next Action** | ⚠️ verbatim이나 `"record token overhead"` → `"record <REDACTED>"`로 **오탐 redaction** | (요약 반영) | — |
| **commit hash** (`0de386c`, `45d4c2d`) | ✅ verbatim | — | ✅ `concepts/WorkflowBoundaryDecision.md` |
| **RFC/ADR ref** (`RFC-0019`, `ADC-0019`, `ADR-0008`) | ✅ verbatim | — | ✅ `concepts/WorkflowBoundaryDecision.md` |

- **raw/**: 결정론적, 모든 항목 verbatim(오탐 1건 제외), `-rw-------`(0600, hook `umask` 경로).
  frontmatter에 `sessionId`/`slug`/`project`/`cwd`/`gitBranch`/`model`/`token_totals`/
  `hour_buckets` 등 정량 메타 보존.
- **wiki/sources/**·**wiki/concepts/**: `sync`가 **자동 생성하지 않음** — 에이전트가
  Ingest Workflow(`CLAUDE.md`)를 따라 수기 작성(이 PoC에서 대행). 즉 "source/wiki 계층에
  어떻게 보존되나"는 **에이전트 ingest 품질에 의존**하며, sync만으로는 raw/ 계층까지만
  보장된다.
- **오탐 redaction (신규 발견)**: shipped 기본 `extra_patterns[0]`
  `(?i)(api[_-]?key|secret|token|bearer|password)["'\s:=]+[\w\-\.]{8,}` 가 산문의
  `"token overhead"` 를 매치 → `token` 뒤에 8자 이상 단어가 오면 무조건 `<REDACTED>`.
  일반 문장의 "token/secret/key/password" 단어를 파괴할 수 있음.

## Query

nested 로그인 `claude -p` + `--mcp-config`(llmwiki MCP)로 4-query 실행. wiki 페이지 3개
(sources 1 + concepts 2)만 있는 소규모 corpus.

| Query | retrieval (deterministic) | synthesis (real model) |
|---|---|---|
| 특정 commit hash (`0de386c`) | **PASS** — `wiki_search` → `WorkflowBoundaryDecision.md:12` | **PASS** — verbatim 인용, "not synthesized" 명시 |
| 특정 ADR (chain의 ADR) | **PASS** — `ADR-0008` (RFC-0019 → ADC-0019 → ADR-0008) | **PASS** — verbatim |
| 특정 Open Issue (0644) | **PASS** — `wiki_search "0644"` → `sources/3181c17b.md:17` (+ concepts 중복) | **PASS** — 인용 + 자기 번역을 "my translation"으로 구분 |
| 특정 Architecture decision (3 manifest 파일) | **PASS** — `sources/3181c17b.md:20` "Decision line" | **PASS** — "vendored-fork approach" 인용 |

- **retrieval = VERIFIED PASS** — `wiki_search`(substring, 라인 anchor) + `wiki_query`
  (keyword scoring)는 결정론적이고 정확.
- **synthesis = 이 소규모 corpus에서 VERIFIED PASS** — 실모델이 4건 모두 정확·인용 기반,
  추론과 인용을 스스로 구분, hallucination 0. **대규모 실제 wiki에서의 synthesis 품질은
  UNVERIFIED**(3페이지만 테스트).
- 6 turns, $0.16, cache_creation 18.7k / cache_read 91.9k / output 1.3k.

## Token/Context

동일 프롬프트(`"Reply with exactly: PONG"`), cwd=후보 repo(=`CLAUDE.md` 상주), n=2/arm.

| arm | input | cache_creation | cache_read | output | cost |
|---|---:|---:|---:|---:|---:|
| MCP OFF #1 | 2 | 15,408 | 19,881 | 5 | $0.09909 |
| MCP OFF #2 | 2 | 15,239 | 19,881 | 5 | $0.09808 |
| MCP ON #1 | 2 | 15,622 | 19,881 | 5 | $0.10036 |
| MCP ON #2 | 2 | 15,625 | 19,881 | 5 | $0.10039 |

- **MCP tool schema overhead ≈ +300 tokens** (ON mean ~15,624 vs OFF mean ~15,324 in
  cache_creation), 비용 **≈ +$0.0016/call**. `cache_read`·`input` 불변.
- **n=2, trivial 프롬프트 → 통계적으로 불충분.** OFF arm 내부 분산(15,239–15,408, ±170)이
  ON−OFF 갭(~300)의 절반. 방향성만 유효(MCP 12-tool 스키마 ≈ 수백 토큰). **정밀값은
  UNVERIFIED.** 단일 측정을 일반적 절감/증가율로 과장하지 않는다.
- `CLAUDE.md`(~10KB, cwd=repo 상주)는 두 arm 공통이라 이 A/B로 분리 불가 →
  plugin 상주 `CLAUDE.md` 토큰 비용은 **UNVERIFIED**.
- plugin 미설치(로그인 세션)라 plugin always-on 실측 불가 → **UNVERIFIED**.

## Security

live-path 생성물(`raw/sessions/*live-test*.md` + 에이전트 ingest `wiki/`) 실검사.

| 항목 | 결과 |
|---|---|
| API key / token / password / JWT / PEM | **0** (세션에 secret 없음 — negative test; redaction 코드 자체는 Resolution PoC `pytest -k redact` PASS) |
| OS username | **0** (세션 cwd `/private/tmp/…`, `ls` 출력 없음) |
| GitHub handle | **0** |
| absolute path | frontmatter `cwd: /private/tmp/llm-wiki-poc-002L/src` 노출(민감 아님). `/Users/<name>` 형태면 username redaction 적용 대상 |
| session metadata | `sessionId`/`slug`/`project`/`cwd`/`gitBranch`/`model`/`token_totals`/`hour_buckets` — **의도적 저장**(frontmatter) |
| file permissions | `raw/` = **0600** (hook `umask 077` 경로); **에이전트가 Write로 만드는 `wiki/` 페이지 = 0644**(umask 022) — 0644 이슈가 curated 계층에도 존재 |
| P0/P1 결과 유지 | key-shaped redaction·provenance·`wiki_search`/`wiki_query`·auto-injection 0 = live path에서 **유지 확인**. 단 **오탐 redaction** 신규 발견(§Session → Wiki), 0644는 wiki/ 계층까지 확장 |

## Egress

packet capture 미수행 → **network-level absence UNVERIFIED**. 아래 3근거로 구분 기록:

| 근거 | 결과 |
|---|---|
| code-level | 런타임 모듈(`llmwiki/`, `hooks/`)에 `urllib.request`/`requests`/`httpx`/`socket.socket`/`urlopen` **0건**(단 `synth/ollama.py` = localhost 전용, `dummy` 기본에서 미사용). `api.anthropic`/`api.openai`/telemetry/analytics/sentry/posthog **0건** |
| process/network inspection | `llmwiki sync` 실행 중 `lsof -a -p <pid> -i` → **네트워크 소켓 0**. MCP `wiki_search` 호출 중 `lsof` → **네트워크 소켓 0** |
| credential 사용 | `ANTHROPIC_API_KEY`/`OPENAI_API_KEY`를 읽는 코드 **0건**(`agent_delegate.py`에 "Works when ANTHROPIC_API_KEY is unset" 주석뿐). 테스트 전 과정 두 키 **unset** |

## Patch 유지성

- 이번 live test에서 P0 patch(=`marketplace.json` owner/source, `plugin.json` commands/
  skills, 신규 `hooks/hooks.json`) 3파일은 **plugin runtime에서 모두 적용됨** —
  `claude plugin list` `✔ enabled`, 18 commands / 6 skills / MCP resolve.
- **fresh `git clone` of upstream에는 이 3파일 수정이 없다** — 이 PoC에서도 재-clone 후
  patch를 처음부터 재적용해야 했다. `examples/sessions_config.json` redaction도 배포
  환경별로 수기 유지.
- 따라서 **vendored fork 또는 upstream PR merge가 필수**. upstream update 시:
  `marketplace.json`/`plugin.json`은 3-way merge 충돌 가능(스키마가 또 바뀌면 재작성),
  `hooks/hooks.json`은 신규 파일이라 보통 무충돌, `sessions_config.json`은 upstream이
  기본 패턴을 바꾸면 재검토 필요(§오탐 redaction 참고).

## Open Issues

1. **P0 patch = vendored fork/upstream PR 필수** — 3파일을 Jarvis가 유지하거나 upstream에
   병합해야 함. 후보 업데이트마다 재적용·재검증.
2. **로그인 세션 내 plugin enabled/hook/always-on 토큰 = UNVERIFIED (constraint-blocked)** —
   로그인+격리 config 동시 불가. 대체 표면(project commands + MCP)은 live PASS.
3. **hook × 실제 HOME = 광범위 ingest** — SessionStart hook을 실제 `~/.claude` HOME에서
   무-scope 실행 시 claude_code 79 + codex_cli 53 세션 전량 변환(실측). `include_projects`
   scoping 또는 격리 HOME 병행이 운영 필수.
4. **깊은 subdir에서 project hook 발화 여부 = UNVERIFIED** (이 세션에서 로그 미생성).
5. **오탐 redaction (신규)** — 기본 `extra_patterns[0]`가 산문의 "token/secret/key/
   password + 단어"를 `<REDACTED>` 처리(`"token overhead"` 실측). 지식 손실 위험.
6. **0644가 wiki/ 계층까지** — 에이전트 Write로 만드는 `wiki/*.md`도 0644. `umask`는
   hook 경로만.
7. **synthesis 품질 at scale = UNVERIFIED** — 3페이지 corpus만 테스트. 대규모 실 wiki
   미검증.
8. **token overhead 정밀값 = UNVERIFIED** — n=2, trivial 프롬프트. 방향성(MCP ≈ 수백 토큰)만.
9. **network-level egress absence = UNVERIFIED** — packet capture 미수행(code-read + lsof +
   credential 미참조로 갈음).

## Final Judgment

**CONDITIONAL PASS.** Production Adoption으로 상향하지 않는다.

live 환경에서 검증된 것: patched plugin 로드(`✔ enabled`), MCP 12 tools, `wiki_search`/
`wiki_query` retrieval + 실모델 synthesis(소규모) 정확·인용 기반, provenance/commit/ADR
라인 anchor 회수, 자동 context injection 0, hook 발화 + non-blocking + `umask` 0600,
egress code/process 근거상 없음, credential 미사용. **P0/P1 Resolution 결과가 live path
에서 유지됨.**

Adoption 상향 3조건 평가:

| 조건 | 판정 |
|---|---|
| (1) 3파일 patch를 upstream PR merge 또는 Jarvis vendored fork로 유지할 전략이 있는가? | **미충족** — 전략 미결정. patch는 재-clone 시 소실됨을 실측. |
| (2) 로그인된 Claude Code live smoke가 PASS인가? | **부분 PASS** — MCP·query·hook 발화·retrieval/synthesis는 live PASS. 그러나 **로그인 세션 내 plugin install/enabled·always-on 토큰·임의-cwd hook**은 제약상 UNVERIFIED. |
| (3) redaction 운영 규칙 + slash/manual 0644 limitation을 Governance 관점에서 수용 가능한가? | **미충족(판단 보류)** — 오탐 redaction(지식 손실)·0644가 wiki/까지 확장·hook×실HOME 광범위 ingest는 운영 규칙 문서화와 사람 승인이 선행돼야 함. |

세 조건 모두 충족되지 않았다 → **Production Adoption 상향 금지.** 다음 단계는 (1) patch
유지 전략(upstream PR 시도 vs vendored fork) 결정, (2) 실제 대화형 로그인 Claude Code에서
plugin install 포함 1회 스모크(사람이 직접), (3) redaction/권한/ingest scoping 운영 규칙
초안.

## Candidate #1 비교에 필요한 결과

| 축 | Candidate #1 `nvk/llm-wiki` | Candidate #2 `Pratiyush/llm-wiki` (patch + live) |
|---|---|---|
| shipped 설치 | plugin 정상 | FAIL → 3파일 vendored patch 필요 (재-clone 시 소실 실측) |
| live 로그인 plugin load | 미검증 | 격리 config `✔ enabled` / 로그인 세션 내 = UNVERIFIED(제약) |
| live query (retrieval) | 구조·링크만, 실모델 UNVERIFIED | **live PASS** — `wiki_search`/`wiki_query` 라인 anchor 회수 |
| live query (synthesis) | UNVERIFIED | **소규모 corpus PASS** (인용 기반, hallucination 0); at-scale UNVERIFIED |
| secret redaction | **P0 FAIL** | key-shaped PASS + **오탐 redaction 신규 발견** |
| 자동 injection | 미확정 | **0 (live 확인)** |
| 필수 외부 서비스 | compile/answer가 network 의존 | 코어 sync/lint/MCP **network·credential 0** (lsof 확인) |
| file 권한 | (미측정) | raw/ 0600(hook 경로), wiki/ 0644 |
| 운영 부담 | 낮음 | vendored fork 유지 + hook scoping + redaction 튜닝 |

## Architecture / Contract

**변경 없음.** 모든 코드/매니페스트 수정은 격리 checkout의 Candidate #2 내부. Jarvis에는
이 evidence 문서 + `.claude/docs/README.md` 인덱스 1행만 추가. `core/`/`hqs/`/Dashboard/
Baseline/RFC/ADC/ADR/Public Contract/OmniRoute 0건. LLM Wiki를 Architecture/Governance
Source of Truth로 취급하지 않는다.

## Cleanup

PR 내용 확인 후 제거 (evidence는 원격 branch + PR로 보존):
- `/private/tmp/llm-wiki-poc-002L/` (격리 HOME·후보 checkout·jarvis clone·synchome·ccfg2·hooktest)
- `~/.claude/projects/-private-tmp-llm-wiki-poc-002L-src/` (nested 스모크 세션 transcript — 이 PoC가 생성)
- `/private/tmp/llm-wiki-poc-002L/*.log`, `${TMPDIR}/llmwiki-sync*.log`
- `claude/llm-wiki-poc-002-live` branch — PR 처리 후
- **되돌릴 것 없음**: 실제 `~/.claude/settings.json`·`~/.claude/plugins/known_marketplaces.json`·`~/.omniroute/.env` sha256 전후 동일, `~/.claude-mem` 부재.

## Branch / PR 상태

| | |
|---|---|
| branch | `claude/llm-wiki-poc-002-live` @ base `0de386c` |
| diff | `.claude/docs/integrations/llm-wiki-candidate-002-live-validation.md` (신규) + `.claude/docs/README.md` (1행) |
| 선행 evidence | PR #161(PoC), PR #162(Resolution) — 보존 |
| PR | [#163](https://github.com/ok041110-del/jarvis-os/pull/163) `claude/llm-wiki-poc-002-live → main`. **merge 안 함.** |
