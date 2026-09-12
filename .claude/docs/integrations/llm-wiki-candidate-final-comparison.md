# LLM Wiki Candidate #1 vs #2 — Final Comparison

검증일: 2026-09-08
목적: Candidate #1(`nvk/llm-wiki` @ `7c94c9bf`, v0.24.4)과 Candidate #2(`Pratiyush/llm-wiki` @ `b1088890`, v1.3.82)의
PoC / Resolution / Live Validation Evidence를 **하나로 종합**하고, 두 후보를 축별로 비교하여
Jarvis에서의 채택 방향을 결정한다. 이 문서는 새 라이브 테스트를 수행하지 않고 기존 Evidence의
재종합만 한다. `.claude/docs/` 규정대로 실행환경 검증 evidence이며 RFC/ADC/ADR/BASELINE의
source of truth가 아니다.

## 종합 대상 Evidence (요구사항 1)

| # | 문서 | 위치 | 상태 |
|---|---|---|---|
| C1-PoC | Candidate #1 PoC — nvk/llm-wiki | `claude/llm-wiki-poc-001` worktree `projects/llm-wiki-candidate-001-poc/REPORT.md` (Codex 수행, Jarvis 미반영) | CONDITIONAL PASS |
| C1-Res | Candidate #1 Resolution PoC | PR #164 / `claude/llm-wiki-poc-001-resolution` → `.claude/docs/integrations/llm-wiki-candidate-001-resolution-poc.md` | CONDITIONAL PASS (해결 가능 확인) |
| C2-PoC | Candidate #2 PoC — Pratiyush/llm-wiki | PR #161 / `claude/llm-wiki-poc-002` | CONDITIONAL PASS |
| C2-Res | Candidate #2 P0/P1 Resolution PoC | PR #162 / `claude/llm-wiki-poc-002-resolution` | CONDITIONAL PASS 유지 |
| C2-Live | Candidate #2 Live Validation | PR #163 / `claude/llm-wiki-poc-002-live` | CONDITIONAL PASS |

세 개의 Candidate #2 문서와 두 개의 Candidate #1 문서 모두 **아직 main에 merge되지 않았다**.
이 비교는 그 5개 문서에 기록된 실측 결과만 근거로 하며, 확인되지 않은 항목은 UNVERIFIED로 표시한다.

## 요구사항 5 — "해결 가능성 VERIFIED" ≠ "Production-safe / Adoption VERIFIED"

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| **해결 가능성 VERIFIED** | 격리 환경에서 결함을 재현하고, 수정을 적용해 재현이 사라짐을 실측 | **C1**: P0(redaction)·P1(promote lint) 둘 다 — 소스 패치로 adversarial 12형태 차단·오탐 0·회귀 14/14. **C2**: P0×2(marketplace schema·hook import) — vendored 3파일 패치로 plugin `✔ enabled`. C2 P1 identity leak — config로 0 hits. |
| **Production-safe / Adoption VERIFIED** | 로그인된 실사용 환경에서 상시 안전성·비용·회귀 부재가 측정됨 | **두 후보 모두 미달성.** 공통 미검증: (a) 로그인 세션 내 plugin enabled 상태 + always-on 토큰 실측, (b) `0644` 생성물 권한의 완전 해소, (c) 패치/fork 유지 전략 확정, (d) 대규모 wiki에서의 synthesis 품질, (e) Governance operating rule 승인. |

**즉, 두 후보의 알려진 blocker는 "고칠 수 있음"이 실증됐으나, "지금 프로덕션에 켜도 안전함"은 어느 쪽도 실증되지 않았다.**

## 축별 비교 (요구사항 2·3)

Winner는 종합 Evidence 기준 상대 우위이며, 두 후보 모두 CONDITIONAL임을 전제로 한다.
Evidence Confidence = 그 판정을 뒷받침하는 실측의 강도(High=로그인/런타임 실측, Medium=코드+격리 실측, Low=추정/소규모/단일).

| 축 | Candidate #1 (nvk) | Candidate #2 (Pratiyush) | Winner | Evidence Confidence |
|---|---|---|---|---|
| **Security** | P0(tool_input k=v secret 미제거)는 shipped 상태에서 심각했으나 소스 패치로 12형태 차단·오탐 0(C1-Res). egress/credential 검증은 깊이 부족. `0644` Open. | key-shaped secret redaction이 **무패치로** 동작(GitHub/AWS/Anthropic/OpenAI/Google/Stripe/npm/JWT/PEM, pytest PASS). egress=code-read+`lsof` 소켓 0+credential 미참조(C2-Live). 단 identity leak(username/handle/path)은 per-user config로만 완화(lossy), **오탐 redaction 신규 발견**("token overhead"→`<REDACTED>`), `0644`는 hook 경로만 완화. | **#2 (marginal)** | Medium (C2 egress/redaction 코드+lsof 실측; C1 patch는 격리 실측) |
| **Session Capture** | 목적 지향 파이프라인: hook 이벤트 → redacted queue/state → digest → rehydrate → explicit **promote** → raw/notes. 증분 캡처·체크포인트·재수화 semantics 보유. 결함 2건은 해결 가능 확인. | `llmwiki sync`가 `.jsonl` → raw markdown **일괄 결정론 변환**(93% truncation, `tool_result_chars:500`). promote/체크포인트 개념 없음. 무-scope 실행 시 실제 HOME의 129 세션 전량 변환(scoping 필수). | **#1** | Medium (양쪽 격리 실측; C1의 promote 결함/수정도 실측) |
| **Knowledge Model** | Karpathy 3계층. `topics/<t>/raw/{articles,papers,repos,notes,data}` → `wiki/{concepts,topics,references}`. `sources:` frontmatter + dual-link `[[ ]]` + 결정론적 lint(provenance/frontmatter/link/placement). | Karpathy 3계층 + 더 풍부한 큐레이션 taxonomy: `wiki/{sources,entities,concepts,syntheses,comparisons,questions,archive}` + `## Contradictions` 규약 + 정량 메타(`token_totals`/`tool_counts`/`gitBranch`/`model`) frontmatter + `llms.txt`/`llms-full.txt`/`graph.jsonld`(schema.org) export. lint 25 pages 0 issues. | **#2** | High (양쪽 구조·lint 실측) |
| **Query** | query-lite 프로토콜(인덱스→category→article→raw). 구조·근거·링크는 검증. **실모델 답변 품질 UNVERIFIED**(미로그인). | `wiki_query`(keyword scoring) + `wiki_search`(substring, 라인 anchor) MCP tool. **retrieval = 로그인 실측 PASS**(commit hash `0de386c`·`ADR-0008`·Open Issue 라인 회수). **synthesis = 로그인 실모델, 소규모 corpus PASS**(인용 기반, hallucination 0). at-scale synthesis UNVERIFIED. `wiki_query`가 매 호출 `overview.md` append. | **#2** | High (retrieval) / Medium (synthesis, 3-page corpus) |
| **Claude Code Integration** | shipped `wiki@llm-wiki` v0.24.4가 **무패치로** `marketplace add` + `install` + `✔ enabled`(격리). Claude 플러그인에는 **자동 hook 없음** → session capture는 opt-in. Codex desktop verify probe는 격리 cache 무시 FAIL(C1-PoC). | shipped 공식 2경로(plugin marketplace, SessionStart hook)가 **둘 다 깨짐**(`owner` schema, `ModuleNotFoundError`). vendored 3파일 패치 후 `✔ enabled`. 패치는 **재-clone 시 소실 실측**. 로그인 세션 내 enabled 상태 UNVERIFIED(제약). | **#1** | High (양쪽 격리 install 실측; C2 shipped 실패도 실측) |
| **Token / Context** | always-on ≈ 1,378 tok, query ≈ 750 tok — **Claude CLI 추정치, UNVERIFIED**. 실제 token/cache/cost UNVERIFIED. | **자동 context injection 0 = VERIFIED**(코드 전수 + 로그인 세션 A/B). MCP 12-tool schema ≈ +300 tok cache-creation(n=2, Low). `CLAUDE.md` ~10KB는 cwd=repo일 때만 상주(분리 미측정). plugin always-on 토큰 UNVERIFIED. | **#2** | Medium (auto-injection 0 = High; 정밀 토큰값 = Low) |
| **Maintainability** | shipped plugin/query는 **무패치**. 패치 부담은 session-capture 채택 시에만: redaction 코드가 **2개 파일에 중복**(`scripts/llm-wiki-session` + `plugins/.../llm_wiki_session.py`) → 양쪽 동기화 필요 + `sync-codex-plugin.sh` 재생성. | **설치 자체가 3파일 vendored 패치에 의존**(`marketplace.json`/`plugin.json`/신규 `hooks/hooks.json`) + `examples/sessions_config.json` redaction 튜닝. 재-clone 시 전부 재적용. upstream 스키마 재변경 시 3-way 충돌 가능. | **#1** | High (양쪽 파일 구조·재적용 실측) |
| **Governance Fit** | derived recall 층으로 명시. promote 전 digest는 canonical 아님(explicit promotion gate). RFC/ADC/ADR 개념 없음 → SoT 오인 위험은 disclaimer로 완화. | derived recall 층으로 명시. 에이전트 수기 ingest gate + `overview.md` disclaimer. 단 `wiki/concepts/*.md`가 ADR처럼 **권위 있게 보임**(위험을 C2-PoC가 상세 기록 + 완화안 제시). | **Tie** | Medium (양쪽 경계·완화안 문서화, 운영 규칙 미승인) |
| **Claude-Mem Overlap** | cross-session recall 중복. 차별점 = immutable raw / provenance / dual-link graph / lint·audit / Markdown portability. live 병렬 비교 UNVERIFIED. | 동일 차별점 + **자동 주입 0**(토큰 예측성) + 정량 메타(Claude-Mem 미노출). 역할 경계표 상세(push vs pull, 휘발 vs 영속, narrative vs provenance-linked). live 병렬 비교 UNVERIFIED(Claude-Mem 미설치). | **#2 (marginal)** | Low–Medium (양쪽 live 병렬 비교 없음) |
| **Future Compatibility** | portable `AGENTS.md`(59,952 B) + compact `profiles/query-lite/SKILL.md`(2,797 B). vendor-neutral MD/YAML. LangGraph read-only query adapter 결합 가능(미구현, RFC→ADC→ADR 필요). | `AGENTS.md`(비-Claude 에이전트) + **MCP stdio server**(로그인·네트워크 불필요, 임의 MCP 클라이언트 호환) + `llms.txt`/`graph.jsonld` 구조화 export + adapters 시스템. LangGraph 결합도 동일 조건. | **#2** | Medium (C2 MCP·export 실측; 결합 자체는 양쪽 미구현) |

**축 집계**: #1 우위 3(Claude Code Integration, Maintainability, Session Capture) · #2 우위 6(Security, Knowledge Model, Query, Token/Context, Claude-Mem Overlap, Future Compatibility) · Tie 1(Governance Fit).

## P0 / P1 / P2 및 Risk 분류 (요구사항 4)

상태값: **Resolved(patch)** = 해결 가능성 VERIFIED(격리 실측, shipped 아님) · **Mitigated** = 부분 완화(잔여 존재) · **Open** = 미해결 · **UNVERIFIED** = 측정 못 함.

### Candidate #1 (nvk/llm-wiki)

| ID | 항목 | 분류 | 근거 |
|---|---|---|---|
| C1-P0 | session capture `tool_input` k=v/provider-shape secret 미redact | **Resolved(patch)** — shipped=Open | C1-Res: `_redact_secret_values` 헬퍼(2파일), adversarial 12형태 `[REDACTED]`, benign 12 오탐 0, 회귀 14/14 |
| C1-P1a | `session promote` frontmatter 8-space indent → `unterminated YAML` critical | **Resolved(patch)** — shipped=Open | C1-Res: `textwrap.dedent`+f-string 상호작용, header/body 분리로 lint 통과 |
| C1-P1b | Codex desktop plugin resolution이 clean-home cache 무시(verify probe FAIL) | **Open / UNVERIFIED** | C1-PoC에서 FAIL. 이번 Resolution 범위 밖 — 해결 가능성 미검증 |
| C1-P1c | live query 품질 · 실제 token/cache/cost · Claude hook 실동작 | **UNVERIFIED** | 미로그인. C1-Res에서도 미해소 |
| C1-P2a | 생성물 `HUB/.sessions/**` 권한 `0644`(world-readable) | **Open** | C1-Res: 패치가 권한 미수정 |
| C1-P2b | 정규식 redaction 구조적 한계(숫자 없는 짧은 순수-알파벳 secret 값) | **Open** | C1-Res 명시 한계 |
| C1-P2c | 패치 유지성 — redaction 코드 2파일 중복 + upstream 의존 | **Open** | C1-Res: 양쪽 동일 패치 필요, upstream update 시 재적용 |
| C1-P2d | promote/compile 큐레이션 수작업, 동일 article 동시쓰기 last-write-wins | **Open (수용)** | C1-PoC Open Issue 5 |
| C1-P2e | promote frontmatter 유효성 회귀 가드 테스트 upstream 부재 | **Open** | C1-Res |
| C1-Ops | 민감정보 가능 repo에서 session capture는 패치 전 비활성화 필요 | **Mitigated(patch 후)** | C1-PoC 권고 → C1-Res 패치로 완화, 단 `0644`·토큰 미검증 잔존 |

### Candidate #2 (Pratiyush/llm-wiki)

| ID | 항목 | 분류 | 근거 |
|---|---|---|---|
| C2-P0a | `marketplace.json`이 현행 Claude Code 스키마(`owner` object) 미충족 → plugin 경로 전면 불가 | **Resolved(patch)** — shipped=Open | C2-Res: `owner`/`source` 수정 → `✔ Successfully added/installed`. C2-Live 재확인 |
| C2-P0b | 문서화된 SessionStart hook `python3 …/convert.py` → `ModuleNotFoundError`(조용한 no-op) | **Resolved(patch)** — shipped=Open | C2-Res: `hooks/hooks.json` = `cd $CLAUDE_PLUGIN_ROOT && python3 -m llmwiki sync`, 임의 cwd exit 0 |
| C2-P1a | identity leakage — OS username / GitHub handle `ok041110-del` / scratchpad 절대경로 / project dir 명 | **Mitigated** | C2-Res: `examples/sessions_config.json` `extra_patterns` → 4 class 전부 0 hits. 단 full-match 치환이라 lossy, per-user 수기 입력 |
| C2-P1b | 생성물 권한 `0644`(원본 `.jsonl`은 `0600`) | **Mitigated(부분)** | C2-Res: hook 경로 `umask 077`→`0600`. `/wiki-sync` slash·수동 실행·에이전트 Write `wiki/*.md`는 `0644` 잔존(C2-Live) |
| C2-P1c | live model ingest/query 품질 · 실제 token/cache/cost · 로그인 세션 내 plugin enabled | **부분 Resolved / UNVERIFIED** | C2-Live: retrieval PASS + synthesis 소규모 PASS. at-scale synthesis·정밀 토큰·로그인 plugin enabled = UNVERIFIED(제약) |
| C2-P2a | 결정론 변환 93% truncation(대형 governance Read 원문 raw/에 미포함) | **Open (설계)** | C2-PoC: 사실 링크는 유지, evidence 원문 아님 |
| C2-P2b | curated `wiki/`는 에이전트 수기 ingest 필요, `wiki_query` 결정 요약 ranking 불완전, `overview.md` 매회 append | **Open** | C2-PoC / C2-Res |
| C2-P2c | `claude plugin marketplace add`가 `CLAUDE_CONFIG_DIR` 재지정에도 실제 `~/.claude/plugins/known_marketplaces.json` touch(내용 무영향) | **Open (무영향)** | C2-PoC Open Issue 8 |
| C2-P2d | **오탐 redaction(신규)** — 기본 `extra_patterns[0]`가 산문 "token/secret/key/password + 단어"를 `<REDACTED>` | **Open** | C2-Live 실측(`"token overhead"`) — 지식 손실 위험 |
| C2-P3 | `setup.sh` 비실행 비트 · README↔setup.sh 불일치 · `plugin.json` 경로 오참조 · `./config.json` 로딩 주석 오류 | **부분 Resolved** | C2-Res: `plugin.json` 경로는 패치. `setup.sh`/docs/주석은 upstream Open |
| C2-Ops | SessionStart hook을 실제 `~/.claude` HOME에서 무-scope 실행 시 129 세션 전량 변환 | **Open** | C2-Live 실측 — `include_projects` scoping 또는 격리 HOME 병행 필수 |
| C2-Maint | P0 패치 = vendored fork/upstream PR 필수(재-clone 시 소실 실측) | **Open** | C2-Live |

### 공통 Governance Risk

| 항목 | 분류 | 근거 |
|---|---|---|
| `wiki/concepts/*.md`가 ADR처럼 권위 있게 보여 SoT로 오인될 위험 | **Open (운영 규칙 미승인)** | 양쪽 PoC가 완화안(disclaimer 고정 + "RFC/ADC/ADR 입력 근거로만, 결정 자체로는 불가" 규칙) 제시했으나 사람 승인 절차 미진행 |
| LLM Wiki ↔ Claude-Mem 역할 경계(Project Knowledge Layer vs Session/Operational Memory) | **문서화됨, 라이브 병렬 비교 UNVERIFIED** | 양쪽 PoC + `claude-mem.md` + Tooling Review 기준 구조 비교만 |

### 공통 Operational Risk

| 항목 | 분류 |
|---|---|
| 로그인 + 격리 `CLAUDE_CONFIG_DIR` 동시 불가 → 로그인 세션 내 plugin 동작 실측 불가 | **UNVERIFIED (constraint-blocked)** — 두 후보 공통 |
| 대규모 wiki에서의 retrieval ranking + synthesis 품질 | **UNVERIFIED** — 두 후보 공통 |
| network-level egress absence (packet capture 미수행) | **UNVERIFIED** — C2는 code-read+lsof+credential 미참조로 갈음, C1은 미측정 |

## 역할 경계 재확인 (요구사항 6)

- **Jarvis Source of Truth** = `docs/architecture/baseline/BASELINE.md` + `docs/decisions/{rfc,adc,adr}/` + `.claude/docs/integrations/` Evidence.
  Architecture/Governance 변경은 이 비교와 무관하게 항상 **RFC → ADC → ADR** 절차를 따른다.
- **Claude-Mem** = Session / Operational Memory. SessionStart hook이 AI narrative 요약을 `additionalContext`로 **push**(자동 주입). 휘발적·운영적 연속성.
- **LLM Wiki**(어느 후보든) = Project Knowledge Layer. immutable raw 사실 + 큐레이션 `wiki/` + explicit provenance + dual-link 그래프. **pull 전용**(slash/MCP), 자동 주입 안 함(#2는 코드로 확정, #1은 always-on 토큰 존재·UNVERIFIED).
- 두 후보의 `wiki/concepts` · `sources`는 RFC/ADC/ADR/BASELINE/Evidence를 **대체·갱신·인용 근거 승격할 수 없다**. session digest/wiki 페이지는 explicit promotion(#1) 또는 Governance 절차(#2) 전에는 canonical evidence가 아니다.

## 최종 판단 (요구사항 7)

**둘 다 Conditional (Both Conditional).**

- 두 후보의 알려진 blocker(#1: P0 redaction·P1 promote lint / #2: P0 marketplace schema·P0 hook import)는 **해결 가능성이 VERIFIED**다.
- 그러나 어느 후보도 **Production-safe / Adoption VERIFIED**에 도달하지 못했다 — 공통으로 `0644` 권한 완전 해소, 로그인 세션 내 plugin enabled + always-on 토큰 실측, 패치/fork 유지 전략, 대규모 synthesis 품질, Governance operating rule 승인이 미충족.
- 따라서 지금 시점에 **어느 후보도 Production Adoption으로 상향하지 않는다.**

**Jarvis에서 계속 추진할 후보로는 Candidate #2를 권고한다** (채택 확정 아님, "추진 대상" 선정):

- Jarvis가 LLM Wiki에 기대하는 자리는 **Project Knowledge Layer**(provenance·큐레이션·pull·portable, Claude-Mem 보완)이고, 이 자리를 규정하는 축 — Knowledge Model, Query(로그인 실측), Token/Context(자동 주입 0 확정), Future Compatibility(MCP·구조화 export) — 에서 #2가 우위다.
- #1의 강점(무패치 shipped plugin)은 그 플러그인의 always-on 비용이 UNVERIFIED이고, 결함이 집중된 영역이 정확히 Jarvis가 상시로 원치 않는 session-capture 계층이라 이점이 상쇄된다.
- **Candidate #1은 fallback으로 유지한다**: "무패치 shipped Claude 플러그인이 필수이고 session-capture 계층을 비활성화한 채 query만 쓴다"는 조건이면 #1이 더 적합하다.

## 선정 후보(#2) Production Adoption 선행조건 (요구사항 8)

아래는 **기존 Evidence(C2-PoC / C2-Res / C2-Live)에 이미 기록된 조건**을 정리한 것이며 새 요구사항을 추가하지 않는다.

1. **패치 유지 전략 확정** (C2-Res OI 1, C2-Live 조건 1·OI 1) — `marketplace.json`/`plugin.json`/`hooks/hooks.json` 3파일 패치를 **upstream PR로 병합**하거나 Jarvis가 **vendored fork**로 유지하기로 결정. 재-clone 시 소실됨이 실측됨.
2. **로그인된 Claude Code 1회 live 스모크(사람이 직접)** (C2-Live 조건 2) — 로그인 세션에서 `claude plugin install` 포함, plugin `enabled` 상태 + SessionStart hook 실행 + `/wiki-sync` + `/wiki-query` + plugin always-on 토큰 실측. 현재 로그인+격리 config 동시 불가로 UNVERIFIED.
3. **redaction 운영 규칙 + `0644` limitation 문서화·수용** (C2-Live 조건 3, C2-Res OI 2·3) — (a) `extra_patterns` 기반 identity redaction의 per-user 패턴 입력 규칙과 lossy full-match 치환 감수, (b) **오탐 redaction**(`"token overhead"`류) 해소 또는 감수, (c) `/wiki-*` slash·수동 실행·에이전트 Write `wiki/*.md` 경로의 `0644` 감수 범위를 Governance 관점에서 문서화·승인.
4. **hook ingest scoping 운영 규칙** (C2-Live OI 3) — SessionStart hook을 `include_projects` scoping 또는 격리 HOME과 반드시 병행(무-scope 시 129 세션 전량 변환 실측).
5. **wiki를 규범 아닌 회상 층으로 고정하는 운영 규칙** (C2-PoC §Governance Boundary) — disclaimer를 `SOUL.md`/`CRITICAL_FACTS.md`에 고정하고 wiki 페이지를 RFC/ADC/ADR **입력 근거로만** 사용.

C2-Live의 "Adoption 상향 3조건" 평가는 현재 (1) 미충족 · (2) 부분 PASS · (3) 미충족(판단 보류) 이며, **세 조건이 모두 충족되기 전에는 Production Adoption 상향 금지**가 그대로 유지된다.

## Architecture / Public Contract / Governance

**변경 없음.** Jarvis baseline, RFC/ADC/ADR, Governance, public Contract, OmniRoute, Claude-Mem,
Token Optimizer, Dashboard, `core/`, `hqs/` 미변경. 새 component/runtime/interface 추가 없음.
이 문서는 5개 PoC Evidence의 재종합이며 채택 결정이 아니다. LLM Wiki를 Architecture/Governance
Source of Truth로 취급하지 않는다.

## Branch / PR / Cleanup

| | |
|---|---|
| branch | `claude/llm-wiki-final-comparison` @ base `origin/main` `0de386c` |
| diff | `.claude/docs/integrations/llm-wiki-candidate-final-comparison.md` (신규) + `.claude/docs/README.md` (인덱스 1행) |
| 선행 Evidence | PR #161 / #162 / #163 (Candidate #2), PR #164 (Candidate #1 Resolution) — 전부 merge 대기, 보존 |
| PR | 생성, **merge 안 함** |
| cleanup | 이 비교용 worktree 제거. 실제 `~/.claude` / `~/.omniroute` / `~/.claude-mem` 미접촉(이 작업은 문서 재종합만) |
