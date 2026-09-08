# LLM Wiki Candidate #2 — P0/P1 Open Issue Resolution PoC

검증일: 2026-09-08
범위: [`llm-wiki-candidate-002-poc.md`](llm-wiki-candidate-002-poc.md)(PR #161)이 남긴
Candidate #2(`Pratiyush/llm-wiki` v1.3.82) P0/P1 Open Issue를, 별도 branch +
isolated HOME/checkout에서 **upstream 수정 없이** 해결 가능한지 검증. Candidate #2 내부
파일만 최소 수정하고 Jarvis Architecture/Source of Truth는 일절 변경하지 않았다.
이 문서는 `.claude/docs/` 규정대로 실행환경 검증 evidence이며 RFC/ADC/ADR/Baseline의
source of truth가 아니다.

## 판정

**CONDITIONAL PASS 유지. Production Adoption / Adoption 후보 상향 보류.**
두 P0 blocker는 Candidate #2 내부 3개 파일의 최소 수정(vendored patch, upstream 불필요)으로
**실제로 해소**됐고 — plugin이 `✔ enabled`로 로드되고 문서화된 hook 실패가 `python3 -m
llmwiki sync`로 안전하게 대체됨 — 회귀검증(secret redaction, provenance, wiki_search,
wiki_query, 자동 injection 0)도 전부 유지된다. 그러나 (a) 수정이 upstream이 아닌
**fork/patch**라 후보 업데이트마다 재적용 부담이 있고, (b) 0644 권한은 hook 경로에서만
`umask`로 완화되며 hook 밖 수동 실행 시 그대로이고, (c) live model ingest/query 품질·
token/cache/cost·repo-local slash command 실행은 **격리 `claude` 미로그인으로 여전히
UNVERIFIED**다. 따라서 P0/P1이 "모두" 해소된 상태가 아니며, Adoption 상향 대신 아래
"Candidate #1 최종 비교 기준"을 제시한다.

## 격리 및 범위

| 항목 | Evidence |
|---|---|
| resolution branch | `claude/llm-wiki-poc-002-resolution`, base `origin/main` `0de386c` |
| isolated jarvis clone | `/private/tmp/llm-wiki-poc-002r/jarvis` (별도 `.git`) |
| 후보 checkout | `/private/tmp/llm-wiki-poc-002r/src` (`Pratiyush/llm-wiki` HEAD `b1088890`, `version = 1.3.82`) |
| 격리 HOME | `/private/tmp/llm-wiki-poc-002r/home` (`HOME`/`XDG_*`/`CLAUDE_CONFIG_DIR`/`PYTHONUSERBASE` 재지정; API key unset) |
| Claude Code | **2.1.261** (세션 중 자동 업데이트된 최신) |
| 보호 영역 실측 | 실제 `~/.claude/settings.json` hooks 0건, `~/.claude/plugins/known_marketplaces.json` = `claude-plugins-official`만(llmwiki는 격리 config로), `~/.claude-mem` 부재, `~/.omniroute/.env` sha256 `8827a024…` 동일. 격리 config에서만 marketplace/plugin 등록 |
| Jarvis 변경 | 이 evidence 문서 + `.claude/docs/README.md` 인덱스 1행. Architecture/Governance/Contract/Dashboard/`core/`/`hqs/` 0건 |

## P0-1 — Plugin marketplace/schema 오류 (요구사항 3)

### 재현 (Claude Code 2.1.261, shipped 파일 그대로)

```
$ claude plugin marketplace add <src>
✘ Failed to add marketplace: … Invalid schema: … owner: Invalid input
```

현행 스키마(공식 docs 확인): top-level 필수 = `name`, **`owner`(object, `name` 필수)**,
`plugins[]`; plugin entry 필수 = `name`, **`source`**. shipped `marketplace.json`은
`"author": "Pratiyush"`(문자열, `owner` 없음) + plugin entry에 `"path": "."`(→ `source`
아님) + `plugin.json`이 존재하지 않는 파일 경로 배열(`commands/wiki-*.md`,
`skills/llmwiki-*/SKILL.md`, `hooks/session-start.sh`)을 참조.

### 해결 (upstream 없이 — Candidate #2 내부 최소 수정)

| 파일 | 수정 |
|---|---|
| `.claude-plugin/marketplace.json` | `"author":"Pratiyush"`(str) → `"owner":{"name":"Pratiyush","url":…}`; plugin entry `"path":"."` → `"source":"./"` |
| `.claude-plugin/plugin.json` | `"commands":[7 files]` → `"commands":"./.claude/commands/"`; `"skills":[3 SKILL.md]` → `"skills":"./.claude/skills/"`; 깨진 `"hooks":{"SessionStart":"hooks/session-start.sh"}` **삭제** (`hooks/hooks.json`이 자동 로드됨) |
| `hooks/hooks.json` (신규) | SessionStart command hook (P0-2 참조) |

### 결과 (실측)

```
$ claude plugin marketplace add <src>   → ✔ Successfully added marketplace: llmwiki
$ claude plugin install llmwiki@llmwiki → ✔ Successfully installed plugin: llmwiki@llmwiki (scope: user)
$ claude plugin list
  ❯ llmwiki@llmwiki  Version 0.1.0  Scope user  Status: ✔ enabled
```

`claude plugin list --json`: `enabled: true`, `mcpServers.llmwiki = python3 -m llmwiki.mcp`.
설치 cache에 commands 18개, skills 6개 디렉터리 resolve됨.

**판정**: P0-1 **RESOLVED (vendored patch, upstream 불필요)**. 비용 = shipped 매니페스트
2개 + 신규 1개를 fork로 유지, 후보 업데이트 시 재적용.

## P0-2 — SessionStart hook `ModuleNotFoundError` (요구사항 4)

### 재현 (문서화된 hook 명령 그대로, 임의 cwd)

```
$ cd /tmp && python3 /…/llm-wiki/llmwiki/convert.py
Traceback … File "…/llmwiki/convert.py", line 20, in <module>
    from llmwiki import REPO_ROOT
ModuleNotFoundError: No module named 'llmwiki'
```

`setup.sh` 출력과 `docs/getting-started.md`가 안내하는 형태. `python3 <path>/convert.py`는
`sys.path[0]`을 `llmwiki/`로 잡아 패키지 루트가 빠지고, `setup.sh`는 `pip install -e .`를
하지 않는다. hook은 `exit 0` + logfile 리다이렉트라 **매 세션 조용한 no-op**.

### 해결 — `python3 -m llmwiki sync`로 안전 교체

`hooks/hooks.json` (플러그인 자동 로드):

```json
{ "hooks": { "SessionStart": [ { "hooks": [ { "type": "command",
  "command": "umask 077; cd \"${CLAUDE_PLUGIN_ROOT}\" && (python3 -m llmwiki sync > \"${TMPDIR:-/tmp}/llmwiki-sync.log\" 2>&1 &) ; exit 0"
} ] } ] } }
```

- `cd "${CLAUDE_PLUGIN_ROOT}"` → `python3 -m llmwiki`가 `''`(cwd)를 `sys.path`에 올려
  `from llmwiki import REPO_ROOT`가 resolve됨. **임의 cwd에서 호출해도 정상.**
- 플러그인 밖(수동 `~/.claude/settings.json`)에서 쓸 때는 `${CLAUDE_PLUGIN_ROOT}` 대신
  절대경로: `cd /abs/path/to/llm-wiki && (python3 -m llmwiki sync … &) ; exit 0`.
- `( … &) ; exit 0` → 완전 백그라운드·non-blocking. `umask 077` → P1 권한 완화 겸용.

### 결과 (실측, cwd `/tmp`에서 hook body 실행)

```
hook exit=0   (non-blocking)
/tmp/llmwiki-sync.log: summary: 2 converted, 0 unchanged, 0 live, 0 filtered, 0 ignored, 0 errors
                       auto-build: … build complete
생성물 권한: -rw-------  (umask 077 → 0600)
stdout 캡처 = 빈 문자열  (컨텍스트 주입 0)
```

**판정**: P0-2 **RESOLVED**. 문서화된 `convert.py` 경로를 폐기하고 `-m llmwiki sync`로
교체하면 임의 cwd·비차단·무주입으로 안전 동작. (upstream 문서·`setup.sh` 출력도 함께
고쳐야 완전 해소.)

## P1 — raw/ leakage + 0644 권한 (요구사항 5)

### 재현 (shipped 기본 설정)

`raw/sessions/*.md`에서 실측: OS username `chan`(bash `ls -la` 소유자 컬럼), GitHub
handle `ok041110-del`(`gh auth status` keyring 라인·repo URL·PR URL), scratchpad 절대경로
`/private/tmp/claude-501/…`, project dir 명 `-Users-chan-Developer-jarvis-os`. 생성물
141개 전부 `-rw-r--r--`(0644), 원본 `.jsonl`은 `0600`.

### 최소 보완책 (config + umask — code 수정 없음)

**중요**: `convert.load_config()`는 repo root `./config.json`이 **아니라**
`examples/sessions_config.json`을 읽는다(코드 `DEFAULT_CONFIG_FILE`). 파일 상단 주석의
"`./config.json`이 있으면 그걸 읽는다"는 **실제 동작과 불일치**(문서 버그). 따라서 보완
패턴은 `examples/sessions_config.json`에 넣어야 적용된다.

`examples/sessions_config.json`:
```
redaction.real_username: "" → "<로컬 사용자명>"
redaction.extra_patterns += [
  "(?i)\\b<github-handle>(?:-del)?\\b",
  "/private/tmp/claude-[0-9]+/[-A-Za-z0-9_./]+",
  "-Users-[a-z0-9_.-]+-Developer-[A-Za-z0-9_.-]+",
  "(?m)^([d-][rwx-]{9}[@+ ]+\\d+ )<user>(  +(?:staff|wheel|admin))"
]
```

### 결과 (실측, 재-sync 후 grep)

| leak class | before | after |
|---|---:|---:|
| ` chan  staff` (ls 소유자 컬럼) | 다수 | **0** |
| `ok041110` (GitHub handle) | 10+ | **0** |
| `/private/tmp/claude-501` (scratchpad abs path) | 다수 | **0** |
| `-Users-chan-Developer-` (project dir 명) | 다수 | **0** |
| 생성물 권한 (hook 경로, `umask 077`) | 0644 | **0600** |
| 생성물 권한 (hook 밖 `python3 -m llmwiki sync` 수동) | 0644 | 0644 (미완화) |

- governance 내용(`RFC-0019 → ADC-0019 → ADR-0008`, `PR #135`, `LangGraph`, checkpoint
  C1/C2)은 보존됨 — over-redaction으로 인한 사실 손실 없음.
- 단, `extra_patterns`는 **full-match `<REDACTED>` 치환만** 지원(backreference 치환 불가)
  → `ls` 라인의 username 패턴이 perms·count 컬럼까지 함께 `<REDACTED>`로 삭제. 읽을 수는
  있으나 다소 lossy.
- 사용자가 자기 username/handle/경로 shape를 직접 넣어야 함(자동 감지 아님).

**판정**: P1 identity leakage **MITIGATED (config-only, 0 hits)**. 0644는 **부분
완화**(hook 경로 한정). code-level 해결(convert.py가 0600으로 write, `<REDACTED>` 대신
capture-group 치환)은 upstream 필요.

## 회귀검증 (요구사항 6) — 기존 PASS 유지

| 항목 | 결과 |
|---|---|
| secret redaction | **PASS** — `pytest -k redact` 59 passed (패치 후) |
| provenance | **PASS** — `wiki_search "ADR-0007"/"ADC-0019" include_raw`가 wiki/ + raw/ 라인 anchor 회수, `sources:` 경로 유지 |
| `wiki_search` | **PASS** — `ADC-0019` → `wiki/sources/*.md` + `raw/…:89 "RFC-0019 → ADC-0019 → ADR-0008 (all merged … PR #135)"` |
| `wiki_query` | **PASS** — 대상 세션 페이지 상위 회수 (retrieval); 최종 자연어 합성은 여전히 UNVERIFIED |
| 자동 context injection 0 | **PASS** — 패치 트리(신규 `hooks/hooks.json` 포함) `additionalContext`/`hookSpecificOutput`/`systemMessage` 0건, hook stdout 빈 문자열 |
| 결정론적 lint | structural 0 errors (semantic은 미-ingest wiki에서 `[info] orphan` 1건 — 회귀 아님) |
| MCP server | **PASS** — 12 tools, `llmwiki 1.3.82`, 로그인·네트워크 불필요 |

## 변경 전후 비교 (요구사항 8)

| 축 | BEFORE (shipped v1.3.82) | AFTER (Candidate #2 내부 patch) |
|---|---|---|
| 설치성 — marketplace add | FAIL (`owner: Invalid input`) | **PASS** |
| 설치성 — plugin install | FAIL (`source: Invalid input`) | **PASS** |
| 설치성 — plugin load | FAIL (`commands/skills Invalid input`, hooks path not found) | **PASS** (`✔ enabled`, 18 cmd / 6 skill / MCP) |
| SessionStart hook | FAIL (`ModuleNotFoundError`, 조용한 no-op) | **PASS** (`-m llmwiki sync`, 임의 cwd, exit 0, 비차단, `2 converted 0 errors`) |
| session sync | `python3 -m llmwiki`로만 | plugin hook + `-m llmwiki` 양쪽 |
| query / search | PASS | **PASS (회귀 clean)** |
| portability | PASS (MD/YAML/gitignore) | **PASS (불변)** |
| security — key-shaped secret redaction | PASS | **PASS (불변, pytest)** |
| security — identity/handle leak | LEAK (4 class) | **0 hits** (config `extra_patterns`, 다소 lossy) |
| security — 생성물 권한 | 0644 | **0600** (hook 경로) / 0644 (수동 실행) |
| context auto-injection | 0 (VERIFIED) | **0 (VERIFIED, 신규 hook 포함)** |
| context overhead — plugin always-on tokens | N/A (설치 불가) | 설치됨 (`CLAUDE.md` ~2.5–3k + 18 cmd + 6 skill 메타) — **정확 토큰값 UNVERIFIED** (미로그인) |
| live model ingest/query 품질·token/cache/cost | UNVERIFIED | **UNVERIFIED (불변 — 격리 `claude` 미로그인)** |
| repo-local slash command 실행 | UNVERIFIED | **UNVERIFIED** |

## 남은 Open Issues

1. **P0 수정이 fork/patch** — `marketplace.json`·`plugin.json`·`hooks/hooks.json` 3파일을
   vendored로 유지해야 하며 후보 업데이트마다 재적용·재검증 필요. upstream PR 병합 시 소멸.
2. **P1 0644 (hook 밖)** — `umask`는 SessionStart hook 경로만 커버. `/wiki-sync` slash나
   수동 `python3 -m llmwiki sync`는 0644 그대로. code-level fix는 upstream 필요.
3. **P1 redaction lossy** — `extra_patterns` full-match 치환만 지원해 `ls` 라인의 perms/
   count 컬럼까지 `<REDACTED>` 처리. 사용자별 username/handle/경로 패턴 수기 입력 필요
   (자동 감지 없음).
4. **문서/설치 스크립트 불일치 잔존** — `setup.sh` 출력·`docs/getting-started.md`의 hook
   예시가 여전히 깨진 `convert.py` 형태; `./config.json` 로딩 주석이 실제 코드와 불일치.
   upstream 문서 수정 대상.
5. **live evidence UNVERIFIED (미해소)** — 격리 `claude` 미로그인으로 live 세션 ingest/
   query 품질, 실제 plugin always-on 토큰, `/wiki-*` slash 실행, hook 실지연을 측정 못 함.
6. **F5 잔존** — `graph`(`graphifyy`)·`e2e`(Playwright) extra, 실제 synthesis backend
   (ollama/agent) 미검증. Python 3.9.6 코어 CLI·테스트는 정상.

## Candidate #1 vs Candidate #2 — 최종 비교 기준 (요구사항 9)

P0/P1이 "모두" 해소되진 않았으므로(위 Open Issues 1–5) Adoption 상향 대신 두 후보를
아래 축으로 최종 비교한다.

| 축 | Candidate #1 `nvk/llm-wiki` | Candidate #2 `Pratiyush/llm-wiki` (patch 후) |
|---|---|---|
| 공식 설치 (shipped 그대로) | plugin `wiki@llm-wiki` v0.24.4 **정상 설치** | **FAIL** — patch 필요 |
| patch/fork 부담 | 없음 | **shipped 매니페스트 3파일 vendored 유지** |
| SessionStart hook | (해당 도구 방식) | shipped FAIL → `-m llmwiki sync`로 해소 |
| session capture secret redaction | **P0 FAIL** (`tool_input` k=v secret 미제거) | key-shaped **PASS** + identity leak를 config로 0 hits |
| promotion lint | **P1 FAIL** (8-space indent → YAML critical) | 해당 없음, 에이전트 ingest → lint PASS |
| provenance / immutable raw | `sources:` 경로 + lint | `sources:` 경로 + `.gitignore` + `wiki_search` 라인 anchor. 변환 93% truncate |
| 자동 context injection | (미확정) | **0 (코드로 확정)** |
| 필수 외부 서비스 | compile/answer가 LLM/network 의존 | **코어(sync/lint/build/export/MCP)가 네트워크·credential 완전 불필요** |
| query/search 실측 | 구조·링크 검증, 실모델 답변 UNVERIFIED | `wiki_query`/`wiki_search` **실측 회수 PASS**, 최종 합성만 UNVERIFIED |
| real model token/cache/cost, live 세션 | UNVERIFIED | UNVERIFIED (동일 한계) |
| 결정론적 test | 다수 `test-*.sh` PASS | pytest 547+ PASS, sync/lint/MCP 실측 PASS |

**권고 기준**: Candidate #2를 채택하려면 (1) 위 3파일 patch를 upstream PR로 올려 병합
되거나 Jarvis가 vendored fork를 유지하기로 결정, (2) 로그인된 Claude Code에서 1회
live 스모크(세션 시작 hook 실행 + `/wiki-sync` + `/wiki-query` + plugin always-on 토큰
실측)를 통과, (3) `extra_patterns` 기반 redaction 운영 규칙과 `/wiki-*` slash·수동 실행
경로의 0644를 감수 가능한 범위로 문서화 — 세 조건이 충족돼야 Adoption 후보로 상향한다.
그 전까지 Candidate #2 = **CONDITIONAL PASS (blocker는 해소 가능함이 실증됨)**.

## Architecture / Public Contract / Governance

**변경 없음.** Jarvis baseline, RFC/ADC/ADR, Governance, public Contract, OmniRoute,
Claude-Mem, Token Optimizer, Dashboard 미변경. 모든 수정은 격리 checkout의 Candidate #2
파일 내부이며 Jarvis에는 이 evidence 문서 + README 인덱스 1행만 추가한다. LLM Wiki를
Architecture/Governance Source of Truth로 취급하지 않는다 — [`llm-wiki-candidate-002-poc.md`](llm-wiki-candidate-002-poc.md) §Governance Boundary 참조.

## Cleanup

PR 내용 확인 후 제거 (evidence는 원격 branch + PR로 보존):
- `/private/tmp/llm-wiki-poc-002r/` (격리 HOME + 후보 checkout + jarvis clone + patch summary)
- `${TMPDIR:-/tmp}/llmwiki-sync.log`, `/tmp/x.log`
- `claude/llm-wiki-poc-002-resolution` branch — PR 처리 후 정리
- **되돌릴 것 없음**: 실제 `~/.claude/settings.json`(hooks 0), `~/.claude/plugins/known_marketplaces.json`(llmwiki 미등록 — 격리 config에만), `~/.claude-mem`(부재), `~/.omniroute`(sha 동일) 미변경.

## Branch / PR 상태

| | |
|---|---|
| branch | `claude/llm-wiki-poc-002-resolution` @ base `0de386c` |
| diff | `.claude/docs/integrations/llm-wiki-candidate-002-resolution-poc.md` (신규) + `.claude/docs/README.md` (1행) |
| 선행 | Candidate #2 PoC = PR #161 (`claude/llm-wiki-poc-002`) |
| PR | 생성 후 URL을 이 표에 후속 커밋으로 기록. merge는 사용자 승인 대기 — **Adoption 상향 아님** |
