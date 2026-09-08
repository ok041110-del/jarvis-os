# LLM Wiki Candidate #2 — Adoption Policy & Live Smoke 준비

작성일: 2026-09-08
개정: 2026-09-08 — 사용자 부분 승인 반영 (§0.1); Ingest scope 정정 — `sessions_config.json`의 `include_projects`가 현재 후보에서 no-op임을 확인하고 R3-a~d를 `sync --project jarvis-os` 기준으로 재작성 (§5.2 · §5.4 · §6.1 S3 · R3)
대상: `Pratiyush/llm-wiki` v1.3.82 (@ `b1088890`) — 현재 Preferred Candidate
근거 Evidence: PR [#161](https://github.com/ok041110-del/jarvis-os/pull/161) · [#162](https://github.com/ok041110-del/jarvis-os/pull/162) · [#163](https://github.com/ok041110-del/jarvis-os/pull/163) · [#165](https://github.com/ok041110-del/jarvis-os/pull/165) · [#166](https://github.com/ok041110-del/jarvis-os/pull/166) (전부 open, 미merge)

이 문서는 Candidate #2의 **Adoption Policy**와, Production Adoption 직전에
**사용자가 로그인된 Claude Code에서 직접 수행할 Live Smoke 절차**를 담는다.
2026-09-08 사용자가 유지 전략(§1)·계층 경계(§2)·Wiki 비권위 규칙(§3 R5)을 승인했다(§0.1).
**나머지 운영 규칙(R1–R4) 승인과 Production Adoption 선언은 Live Smoke B2 PASS 이후**로 남는다.
`.claude/docs/` 규정대로 실행환경 검증 evidence이며 RFC/ADC/ADR/BASELINE의 source of truth가 아니다.

## 0. 현재 상태 (요구사항 1)

| 항목 | 값 |
|---|---|
| Preferred Candidate | `Pratiyush/llm-wiki` |
| 상태 | **CONDITIONAL PASS** (Live Smoke B2 PASS 전까지 유지) |
| 정책 승인 | **부분 승인됨** — §1 유지 전략 · §2 계층 경계 · §3 R5(비권위) (§0.1) |
| Production Adoption | **아직 하지 않는다** — 이 문서로 상향하지 않음 |
| Fallback | `nvk/llm-wiki` (무패치 shipped plugin이 필수이고 session-capture 계층 비활성 조건, PR #165 §최종판단) |

## 0.1 정책 승인 상태 (2026-09-08 사용자 승인)

사용자가 아래 3개 항목을 **승인**했다. 이 승인으로 해당 정책 조항은 Jarvis 운영 기준으로 **발효**한다
(단 Architecture/Governance/Public Contract는 불변 — §7).

| # | 승인 항목 | 문서 위치 | 상태 |
|---|---|---|---|
| A1 | **MCP-first Hybrid 유지 전략** — full plugin 3파일 patch 의존 제거, 유지 항목은 M1(MCP 등록)·M2(hook 한 줄)·M3(머신-로컬 config)·M4(버전 pin) | §1 | **APPROVED** → BLOCKING 게이트 **B1 CLOSED** |
| A2 | **계층 경계** — Canonical SoT(RFC/ADC/ADR/BASELINE/Evidence) / Claude-Mem(Session·Operational, push) / LLM Wiki(Project Knowledge·Derived Recall, pull) | §2 | **APPROVED** |
| A3 | **Wiki 비권위(Non-authoritative) 규칙 R5** — wiki 페이지는 RFC/ADC/ADR/BASELINE/Evidence의 입력 근거로만, 결정·규범·SoT 인용 근거로 승격 불가 | §3 R5 | **APPROVED** → BLOCKING 게이트 **B4 CLOSED** (A2 + R5) |

**승인 범위에 포함되지 않은 것 (여전히 대기)**:

| 항목 | 상태 |
|---|---|
| 운영 규칙 R1(redaction)·R2(permission `0644`)·R3(ingest scope)·R4(truncation) 승인 | **PENDING** → BLOCKING 게이트 **B3 OPEN** |
| Live Smoke B2 (사용자 직접 수행) | **PENDING** → BLOCKING 게이트 **B2 OPEN** |
| Production Adoption 선언 | **하지 않음** — B2·B3 충족 후 별도 Adoption 문서로 |

이 개정은 PR #167 branch에서 정책 상태만 갱신하며 main에 직접 커밋하지 않는다. Candidate #2 = **CONDITIONAL PASS 유지**.

---

## 1. 유지 전략 — MCP-first Hybrid 확정 검토 (요구사항 2)

> **상태: APPROVED (§0.1 A1) — 2026-09-08 사용자 승인. BLOCKING 게이트 B1 CLOSED.**

### 1.1 full plugin 3파일 patch 의존 제거 가능 여부 — 최종 확인

PR #163 §Patch 유지성이 남긴 "3파일 vendored patch(재-clone 시 소실)"가 MCP-first Hybrid에서 **불필요해지는지** 파일별로 확정한다.

| 패치 대상 (PR #162 §P0-1) | plugin 패키징 경로에서의 용도 | MCP-first Hybrid에서 | 결론 |
|---|---|---|---|
| `.claude-plugin/marketplace.json` (`owner`/`source` 스키마) | `claude plugin marketplace add` 통과용 | `marketplace add`를 **하지 않음** | **불필요** |
| `.claude-plugin/plugin.json` (`commands`/`skills` 경로, 깨진 `hooks` 키 삭제) | `claude plugin install` + 자동 등록용 | `plugin install`을 **하지 않음** | **불필요** |
| 신규 `hooks/hooks.json` (SessionStart command) | 플러그인 자동 hook 로드용 | SessionStart hook을 **jarvis-os 프로젝트 `.claude/settings.json` 한 줄**로 직접 배선 | **불필요** (플러그인 파일로서는) |

**확정**: **full plugin 3파일 patch 의존은 제거 가능하다.** MCP-first Hybrid에서 Candidate #2 소스에 대한
코드/매니페스트 패치는 **0건**이다.

### 1.2 MCP-first Hybrid에서 남는 유지 항목 (패치 아님)

| # | 항목 | 성격 | 재-clone 시 |
|---|---|---|---|
| M1 | MCP server 등록 (`python3 -m llmwiki.mcp`) | **Jarvis 측 설정** (`.mcp.json` 또는 `claude mcp add`) — upstream 파일 아님 | 영향 없음 (Jarvis repo/설정에 존재) |
| M2 | SessionStart hook 한 줄 (`… python3 -m llmwiki sync --project jarvis-os …`) | **Jarvis 측 설정** (프로젝트 `.claude/settings.json`) — upstream 파일 아님 | 영향 없음 |
| M3 | `examples/sessions_config.json` redaction 튜닝 (identity `extra_patterns`; `include_projects`는 현재 후보에서 no-op) | **머신-로컬 설정 데이터** (코드 패치 아님, 커밋 금지 — R1) | 재적용 필요. 스니펫을 이 문서 §5에 고정. 미적용 시 key-shaped provider redaction은 그대로 동작, identity extra_patterns만 소실 → R1이 커버. Ingest scope는 M2 hook의 `--project jarvis-os`가 담당(R3-a) |
| M4 | 후보 checkout 버전 pin | 문서화된 커밋/태그 (`b1088890` / `v1.3.82`) | 동일 커밋 재clone |

- **결과**: PR #163/#166이 지목한 최대 Open Issue("vendored fork 유지 부담")가 **사실상 소멸**한다.
  M1·M2는 Jarvis가 원래 소유하는 설정이고, M3는 코드가 아닌 로컬 설정 데이터다.
- **upstream PR (선택, 강제 아님)**: `marketplace.json`/`plugin.json` 스키마 수정을 `Pratiyush/llm-wiki`에
  커뮤니티 기여로 제출할 수 있으나, **Jarvis Adoption의 전제조건으로 걸지 않는다**. 병합되면 향후
  full plugin 패키징 선택지가 무패치로 열린다(그때 별도 검토).
- **full plugin 패키징으로의 승격 조건**: 자동 등록(commands/skills 일괄) + plugin `enabled` UI 상태가
  반드시 필요해지는 구체적 사유가 생길 때에만. 그 경우 vendored fork + 소유자 지정으로 별도 검토를 연다.

### 1.3 채택 시 Jarvis에 추가될 산출물 (지금 추가하지 않음 — Adoption 단계에서)

1. `.claude/docs/integrations/llm-wiki-candidate-002-adoption.md` (최종 Adoption 기록)
2. MCP 등록 스니펫 + SessionStart hook 스니펫 (문서 내 코드블록으로만; 실제 배선은 사용자 환경)
3. `README.md` 인덱스 1행

Architecture/Public Contract/RFC/ADC/ADR 산출물은 **없다** (§7 참조).

---

## 2. 계층 경계 고정 (요구사항 3)

> **상태: APPROVED (§0.1 A2) — 2026-09-08 사용자 승인.**

| 계층 | 정의 | 소비 방식 | 보존성 | 이 계층이 **아닌** 것 |
|---|---|---|---|---|
| **Canonical SoT** | `docs/architecture/baseline/BASELINE.md` + `docs/decisions/{rfc,adc,adr}/` + `.claude/docs/integrations/` Evidence | Governance 절차(RFC→ADC→ADR)로만 생성·변경 | 영속·권위 | — |
| **Claude-Mem = Session / Operational Memory** | 세션 실행 관찰 → AI narrative 요약 | SessionStart hook이 `additionalContext`로 **push (자동 주입)** | 휘발적·운영적 연속성 | 프로젝트 사실의 검증 가능한 근거 아님 (Tooling Review: verbatim 보존 UNVERIFIED) |
| **LLM Wiki (Candidate #2) = Project Knowledge / Derived Recall Layer** | immutable `raw/` 사실 + 큐레이션 `wiki/` + `sources:` provenance + dual-link 그래프 | **pull 전용** (MCP tool / repo-local slash). **자동 주입 없음** (PR #161·#163 코드+세션 실측으로 0 확정) | 영속·portable, 단 **파생·비권위** | Architecture/Governance 규범 아님. RFC/ADC/ADR/BASELINE/Evidence를 대체·갱신·인용 근거로 승격 불가 |

- **불변 규칙**: Architecture/Governance 변경은 이 정책과 무관하게 **항상 RFC → ADC → ADR**.
- **중복 처리**: Claude-Mem과 LLM Wiki는 같은 세션 transcript에서 파생돼 "무슨 작업/결정/파일" 수준이
  겹친다. 소비 방식(push vs pull)·보존성(휘발 vs 영속)·근거성(narrative vs provenance-linked)이 다르므로
  **보완적**으로 둔다. live 병렬 실행 비교는 Claude-Mem 미설치로 **UNVERIFIED (유지)**.

---

## 3. 최소 운영 정책 R1–R4 + Wiki 비권위 규칙 (요구사항 4·6)

> **상태: R5(Wiki 비권위) = APPROVED (§0.1 A3, B4 CLOSED). R1–R4 = PENDING (B3 OPEN — Live Smoke B2 이후 승인).**

새 개발 없이 **설정·절차·문서**만으로 성립. Adoption 발효 시 이 절이 운영 규칙 본문이 된다.

### R1 — Redaction 오탐 / 누락 (요구사항 6: Evidence 범위 초과 주장 금지)

**현재 Evidence 상태 (초과 주장하지 않음)**:
- key-shaped provider secret(GitHub/AWS/Anthropic/OpenAI/Google/Stripe/npm/JWT/PEM)은 `_DEFAULT_TOKEN_PATTERNS`로
  config 무관 항상 redact + pytest PASS (PR #161). **이 범위는 VERIFIED.**
- identity(username/handle/절대경로)는 `extra_patterns`로 0 hits 달성했으나 **full-match `<REDACTED>` 치환이라 lossy**,
  **자동 감지가 아니라 사용자가 자기 shape를 수기 입력**해야 함 (PR #162). **"identity leak 해결됨"이라고 주장하지 않는다 — Mitigated.**
- 기본 `extra_patterns[0]`가 산문 "token/secret/key/password + 단어"를 `<REDACTED>` 처리하는 **오탐**이 실측됨
  (`"token overhead"`, PR #163). **"오탐 없음"이라고 주장하지 않는다.**

**운영 규칙**:
- **R1-a (누락 방어)**: sync를 켜기 전, 사용자 본인의 `real_username` / GitHub handle / scratchpad 경로 shape를
  `examples/sessions_config.json`의 `extra_patterns`에 추가한다 (머신-로컬, **커밋 금지**). 자동 아님 — 사용자 책임.
- **R1-b (오탐 억제)**: 기본 `extra_patterns[0]`(과도한 산문 매칭)를 **머신-로컬 config에서 제거하거나 더 좁은 형태로 교체**한다
  (설정값 변경일 뿐 소스 수정 아님). 그 결과 key-shaped provider redaction에 의존한다.
- **R1-c (사후 감사)**: `site/` deploy 또는 wiki 외부 공유 전, `wiki_search`로 handle / 절대경로 / UID 클래스를 1회 grep 감사한다.
- **R1-d (1차 방어선 아님)**: `raw/`·`wiki/`는 "redacted-but-imperfect"로 취급한다. 실제 credential·비밀값을
  세션 프롬프트/도구 입력에 **직접 넣지 않는다**. redaction은 2차 방어선이다.
- **운영상 허용 범위**: identity redaction의 lossy 치환(perms/count 컬럼까지 `<REDACTED>`)과 산문 오탐 잔여는
  **로컬 개발 머신 + `site/` 미deploy 조건에서 허용**한다. 외부 배포·공유 시에는 R1-c 감사를 **필수**로 한다.

### R2 — 파일 권한 `0644` limitation (요구사항 6)

**현재 Evidence 상태**:
- SessionStart hook 경로(`umask 077`)는 생성물 `0600` (PR #162).
- `/wiki-*` slash·수동 `python3 -m llmwiki sync`·에이전트 `wiki/*.md` Write는 **`0644` 잔존** (PR #163).
- code-level fix(convert.py가 0600으로 write)는 **upstream 필요 — 이 정책 범위 밖. "해결됨"이라고 주장하지 않는다.**

**운영 규칙**:
- **R2-a**: LLM Wiki hub 디렉터리(`raw/`·`wiki/`·`site/` 상위)는 **`0700` 부모 디렉터리** 아래에 둔다.
  파일이 `0644`여도 디렉터리 레벨에서 타 사용자 접근이 차단된다.
- **R2-b**: 수동 sync 및 에이전트 `wiki/` 쓰기는 `umask 077 && …` 프리픽스를 절차로 강제한다.
- **운영상 허용 범위**: 단일 사용자 개발 머신에서 R2-a 적용 시 `0644` 파일 권한 자체는 **허용**한다.
  다중 사용자 / 공유 머신에서는 R2-a(`0700` 부모)가 **필수 전제**이며, 그것 없이는 Adoption하지 않는다.

### R3 — Ingest scope (요구사항 5)

**현재 Evidence 상태**:
- SessionStart hook을 실제 `~/.claude` HOME에서 무-scope 실행 시 **claude_code 79 + codex_cli 53 = 129 세션 전량 변환** (PR #163 실측).
- **2026-09-08 정정**: `examples/sessions_config.json`의 `include_projects` 키는 pin된 후보(`b1088890` / v1.3.82,
  검증 checkout `c4f9bc9` 동일)의 `convert_all()`이 **소비하지 않는다**. `convert_all`은 `filters.drop_record_types`·
  `live_session_minutes`만 읽고, `include_projects`/`exclude_projects`는 `DEFAULT_CONFIG` 선언(`convert.py:32-33`)에만
  존재한다. 이 후보에서 실제로 동작하는 유일한 scope 수단은 CLI 서브스트링 필터
  **`python3 -m llmwiki sync --project jarvis-os`** 다 (`cli.py:704` → `convert_all(project=…)` →
  `convert.py:1478` `if project and project not in project_slug: filtered += 1`).
- dry-run 실측 (2026-09-08, 2회 동일, in-process `convert_all(dry_run=True, force=True)`, socket tripwire, 무-write):
  무-scope(정책 §5.4 hook 경로) = **N=131** (`0 filtered`; #163 시점 129 → 시간 경과분 +2) → **정지 조건 발동**;
  `--project jarvis-os` = **N=71** (`60 filtered` — 비-jarvis-os 세션이 `convert.py:1478` 게이트에서 실제로 제거됨).
  131 = 71 + 60 으로 정합.

**운영 규칙 (명시)**:
- **R3-a**: SessionStart hook(§5.4) 및 **모든 실제 sync**(수동 CLI, `/wiki-sync` 대체 포함)는
  **`python3 -m llmwiki sync --project jarvis-os`** 형태로 `--project jarvis-os` 인자를 반드시 포함한다.
  이 인자가 현재 후보에서 유효한 유일한 scope enforcement다.
- **R3-b**: **무-scope ingest 금지.** `--project jarvis-os`(또는 격리 HOME) 없이 `python3 -m llmwiki sync`를
  실행하지 않는다. MCP `wiki_sync` 툴은 `--project`를 하위 커맨드에 전달하지 않으므로
  (`mcp/server.py` `tool_wiki_sync`), MCP 경유 sync는 **dry-run 확인용으로만** 쓰고 실제 백필·주기 sync는
  CLI/hook 경로(`--project jarvis-os`)로 한다.
- **R3-c**: 최초 1회 백필은 `--project jarvis-os` 상태에서 수행하고, 결과 세션 수 N을 jarvis-os 세션 수
  기대치와 대조 확인한다. **N ≥ 100이면 scope leak으로 간주하고 즉시 중단**한다 (§6.3 정지 조건 유지).
- **R3-d**: 채택 문서에 정확한 `--project` 값(`jarvis-os`)과 hook 커맨드 전문을 명시한다 (§5.4).
  `include_projects` 키는 §5.2 스니펫에 **no-op 주석과 함께** 남겨 두되 scope 근거로 인용하지 않는다.
- **R3-e (잔여 한계)**: `--project`는 프로젝트 슬러그에 대한 **서브스트링** 매치이므로 슬러그에 `jarvis-os`를
  포함하는 다른 프로젝트도 통과한다. 단일 사용자·알려진 프로젝트명 조건에서 허용하며, 정확 매치가 필요해지면
  아래 upstream 옵션을 연다.

**upstream 옵션 (선택 — Adoption 전제조건 아님)**: `Pratiyush/llm-wiki`에 `filters.include_projects` /
`exclude_projects` 소비를 `convert_all()`에 구현하는 패치(정확 매치 리스트 필터)를 커뮤니티 기여로 제출할 수 있다.
§1.2의 marketplace 스키마 upstream PR과 동일하게 **Jarvis Adoption의 전제조건으로 걸지 않는다**. 병합되면 `--project`
대신 config 기반 scoping으로 전환을 별도 검토한다. 그 전까지 `--project jarvis-os`가 정본 scope 수단이다.

### R4 — Truncation (93% 축소) (요구사항 6)

**현재 Evidence 상태**: 결정론 변환이 `tool_result_chars: 500` 등으로 tool 출력을 공격적으로 truncate → 대형 governance 문서 Read 원문은 `raw/`에 **들어오지 않음** (PR #161). 사실 링크는 유지되나 evidence 원문은 아님.

**운영 규칙**:
- **R4-a**: Evidence 원문의 유일 보관처는 **git + `.claude/docs/integrations/`** 다. wiki `raw/`는 사실 링크·요약이며 evidence 원문이 아니다.
- **R4-b**: wiki에서 governance 문서를 인용할 때는 항상 원본 경로/커밋을 병기한다 (`sources:` 규약이 이미 강제).
- **운영상 허용 범위**: 93% 축소는 **설계 특성으로 허용**한다. 단 wiki를 evidence 아카이브로 사용하지 않는다는 것이 전제다.

### R5 — Wiki 비권위 (Non-authoritative) 규칙 (요구사항 3·4) — **APPROVED (§0.1 A3)**

- **R5-a**: `wiki/concepts/*.md`·`wiki/sources/*.md`를 포함한 모든 wiki 페이지는 **RFC/ADC/ADR/BASELINE/Evidence의
  입력 근거(reference)로만** 사용한다. **결정 자체·규범·SoT 인용 근거로 승격할 수 없다.**
- **R5-b**: `wiki/concepts/*.md`가 `type: concept` frontmatter와 구조 때문에 ADR처럼 **권위 있게 보이는** 위험을
  인지한다. 완화 = wiki `overview.md`(및 가능하면 `SOUL.md`/`CRITICAL_FACTS.md`)에 다음 disclaimer를 고정:
  > 이 wiki는 Jarvis Architecture/Governance의 source of truth가 아니다. 모든 결정은 `docs/decisions/{rfc,adc,adr}/`에 있다.
- **R5-c**: session digest / wiki 페이지는 explicit 큐레이션(에이전트 Ingest) 및 Governance 절차 전에는 canonical evidence가 아니다.

---

## 4. Open Issue 운영상 허용 범위 요약 (요구사항 6·10)

| Open Issue | 상태 (초과 주장 없음) | 운영상 허용 범위 |
|---|---|---|
| identity redaction lossy / 수기 입력 | **Mitigated** (해결 아님) | 로컬 머신 + `site/` 미deploy 시 허용. 외부 공유 시 R1-c 감사 필수 |
| 산문 오탐 redaction (기본 패턴) | **Open** | R1-b로 머신-로컬 config에서 무력화(설정 변경). 잔여 오탐은 로컬 개발 조건에서 허용 |
| `0644` (hook 밖 경로) | **Mitigated 부분** (해결 아님, upstream 필요) | R2-a(`0700` 부모) 전제 시 허용. 공유 머신은 R2-a 없이는 Adoption 불가 |
| 93% truncation | **Open (설계)** | R4 전제(wiki ≠ evidence 아카이브) 하 허용 |
| `wiki_query` ranking / `overview.md` append | **Open (품질)** | 비차단. wiki 성장 시 주기 점검 |
| at-scale synthesis 품질 | **UNVERIFIED (유지)** | 초기 소규모 corpus에서 허용. 페이지 50+ 도달 시 재측정 |
| 정밀 token/cost, plugin always-on 토큰 | **UNVERIFIED (유지)** | 방향성(auto-injection 0, MCP ≈ 수백 토큰)만 확인. Live Smoke에서 1회 델타 기록 |
| network-level egress absence | **UNVERIFIED (유지)** | code-read + `lsof`(소켓 0) + credential 미참조로 갈음. ollama/agent backend 미사용 조건 |
| 로그인 세션 내 plugin enabled 상태 | **UNVERIFIED (constraint-blocked)** | MCP-first Hybrid는 plugin install 자체를 안 하므로 대부분 무관. §6 Live Smoke에서 MCP 경로로 확인 |

**이 정책은 위 항목 중 어느 것도 "Evidence 범위를 넘어 해결됐다"고 주장하지 않는다.**

---

## 5. 채택 시 설정 스니펫 (참조용 — 지금 배선하지 않음)

> 아래는 Adoption 발효 시 사용자 환경에 적용할 형태의 참조 스니펫이다. 실제 경로/사용자명은 환경별로 채운다.
> 이 문서를 커밋해도 이 스니펫은 **문서 텍스트**일 뿐이며 어떤 hook·MCP도 활성화하지 않는다.

### 5.1 후보 checkout (버전 pin)

```
git clone https://github.com/Pratiyush/llm-wiki  ~/tools/llm-wiki
cd ~/tools/llm-wiki && git checkout b1088890   # == tag v1.3.82
bash setup.sh                                   # setup.sh는 비실행 비트 — 'bash' 로 실행 (PR #161 F3)
mkdir -p ~/.local/share/llm-wiki-hub            # hub 부모
chmod 700 ~/.local/share/llm-wiki-hub           # R2-a
```

### 5.2 `~/tools/llm-wiki/examples/sessions_config.json` (머신-로컬, 커밋 금지 — R1/R3)

```jsonc
{
  "include_projects": ["jarvis-os"],            // NO-OP (v1.3.82 / b1088890): convert_all()이 읽지 않음. Ingest scope는 §5.4 hook의 `--project jarvis-os`가 강제 (R3-a). upstream 구현 대비 forward-compat 표식일 뿐 (R3-d)
  "redaction": {
    "real_username": "<본인 OS username>",       // R1-a
    "extra_patterns": [
      // R1-b: 기본 과도 패턴을 좁은 형태로 대체하거나 제거. 아래는 identity 클래스만.
      "(?i)\\b<본인 GitHub handle>(?:-del)?\\b",
      "/private/tmp/claude-[0-9]+/[-A-Za-z0-9_./]+",
      "-Users-[a-z0-9_.-]+-Developer-[A-Za-z0-9_.-]+"
    ]
  }
}
```

### 5.3 MCP 등록 (M1 — Jarvis 측 설정, upstream 패치 아님)

프로젝트 `.mcp.json` (jarvis-os 루트) 또는 `claude mcp add`:

```json
{ "mcpServers": { "llmwiki": {
  "command": "python3", "args": ["-m", "llmwiki.mcp"],
  "cwd": "/Users/<you>/tools/llm-wiki"
} } }
```

### 5.4 SessionStart hook (M2 — jarvis-os 프로젝트 `.claude/settings.json`, 한 줄)

```json
{ "hooks": { "SessionStart": [ { "hooks": [ { "type": "command",
  "command": "umask 077; cd /Users/<you>/tools/llm-wiki && (python3 -m llmwiki sync --project jarvis-os > \"${TMPDIR:-/tmp}/llmwiki-sync.log\" 2>&1 &) ; exit 0"
} ] } ] } }
```

- `umask 077` → R2-b. `( … &) ; exit 0` → 완전 백그라운드·non-blocking·stdout 없음(자동 주입 0).
- `--project jarvis-os` → R3-a. 이 인자가 현재 후보에서 유효한 유일한 scope enforcement다
  (`convert.py:1478` 서브스트링 게이트). §5.2의 `include_projects`는 no-op이므로 scope를 그것에 의존하지 않는다.

---

## 6. 사용자 Live Smoke 체크리스트 (요구사항 9) — 약 10분, 로그인된 대화형 Claude Code에서 직접

> 목적: PR #166이 정의한 BLOCKING 게이트 **B2**(로그인 세션 스모크)를 사용자가 직접 닫는다.
> 사전: §5.1~5.4 적용 완료. 실제 로그인 계정으로 jarvis-os 디렉터리에서 Claude Code 실행.
> 각 단계 PASS/FAIL을 §6.2 표에 기록.

### 6.1 단계

| # | 단계 | 명령 / 조작 | PASS 기준 | FAIL 신호 |
|---|---|---|---|---|
| S1 | MCP 연결 | 새 세션에서 `/mcp` | `llmwiki` 서버 `connected`, tool 12개 노출 (`wiki_query`, `wiki_search`, …) | 서버 목록에 없음 / `failed` |
| S2 | MCP 로그인·네트워크 불요 확인 | S1 상태에서 `env | grep -i anthropic_api_key` (없어야 정상) | MCP가 키 없이 동작 | 키 요구 오류 |
| S3 | scoped sync (`/wiki-sync` 대체) | 터미널: `cd ~/tools/llm-wiki && umask 077 && python3 -m llmwiki sync --project jarvis-os` | `N converted, 0 errors`, **N이 jarvis-os 세션 수 기대치와 근사** (dry-run 기준 N≈71) | **N ≥ 100** (scope leak → `--project jarvis-os` 인자 누락 여부 재확인, §5.4 · R3-a) |
| S4 | 생성물 권한 | `ls -l ~/tools/llm-wiki/raw/sessions/ | head` + `ls -ld ~/.local/share/llm-wiki-hub` | 파일 `-rw-------` (umask 경로) **또는** hub 부모 `drwx------` | 파일 `0644` **이고** 부모도 `0755` (R2-a 미충족) |
| S5 | SessionStart hook 발화 | jarvis-os에서 **새** Claude Code 세션 시작 → `cat "${TMPDIR:-/tmp}/llmwiki-sync.log"` | 로그 timestamp 갱신, `… converted … 0 errors`, 세션 즉시 응답(지연 체감 없음) | 세션 시작이 수 초 지연 / 로그 미갱신 / 에러 |
| S6 | 자동 주입 0 확인 | S5 세션 첫 응답에서 "이전 세션/ wiki 내용이 주입됐는지" 관찰 + `/context` 로 컨텍스트 확인 | wiki `raw/`·`wiki/` 내용이 컨텍스트에 **없음** | 세션이 sync 내용/이전 세션 요약을 자동으로 알고 시작 |
| S7 | `wiki_query` (retrieval + synthesis) | 세션에서: "llm-wiki에게 물어봐 — workflow adapter contract의 남은 governance 항목" (MCP `wiki_query` 사용) | 관련 wiki 페이지가 상위로 회수 + 답변이 **인용 기반**, 모델이 인용과 추론을 구분 | 관련 없는 페이지 / 인용 없는 창작 / hallucination |
| S8 | `wiki_search` (정확 매치) | 세션에서: `wiki_search` 로 알려진 커밋 해시(예: `0de386c`) 또는 `ADR-0008` 검색, `include_raw` 포함 | 라인 anchor 단위 정확 매치 반환 | 매치 0 / 잘못된 라인 |
| S9 | (선택) 토큰 델타 | trivial 프롬프트(`"Reply with exactly: PONG"`)를 MCP OFF vs ON 각 1회, `/cost` 또는 usage 확인 | 델타를 **숫자로 기록** (기대: cache_creation ~ 수백 토큰). PASS/FAIL 아님 — 측정 | — |
| S10 | (선택) egress 스팟 | S3 sync 실행 중 다른 터미널: `lsof -a -p "$(pgrep -f 'llmwiki')" -i` | 네트워크 소켓 **0** | 외부 소켓 존재 |
| S11 | teardown | §5.4 hook 라인 제거 (원치 않으면), `${TMPDIR}/llmwiki-sync.log` 정리 | jarvis-os `.claude/settings.json` 원복 | — |

### 6.2 결과 기록표 (사용자 작성)

| 단계 | 결과 (PASS/FAIL/기록값) | 메모 |
|---|---|---|
| S1 MCP 연결 | | |
| S2 키 불요 | | |
| S3 scoped sync (N=?) | | |
| S4 권한 | | |
| S5 hook 발화 | | |
| S6 자동 주입 0 | | |
| S7 wiki_query | | |
| S8 wiki_search | | |
| S9 토큰 델타 (선택) | | 기록값: |
| S10 egress (선택) | | |

### 6.3 Smoke 판정 규칙

- **B2 PASS 조건**: S1·S3·S5·S6·S7·S8 **전부 PASS** + S4가 PASS(파일 0600 또는 부모 0700).
  S2는 보조 확인, S9·S10·S11은 선택.
- **B2 FAIL 시**: 해당 단계 메모를 근거로 후속 판단(설정 오류면 §5 재적용 후 재시도, 구조적이면 Fallback(`nvk/llm-wiki`) 재검토).

---

## 7. Architecture / Public Contract / Governance (요구사항 7·8)

**변경 없음 — 명시적으로 확인.**

- 이 정책은 새 architectural component·runtime·public interface를 추가하지 않는다. LLM Wiki(Candidate #2)는
  `.claude/docs/integrations/` 등급의 **로컬 개발 도구**이며, Claude-Mem·Token Optimizer가 RFC/ADC/ADR 없이
  `.claude/docs/integrations/` evidence로 채택된 것과 동일 패턴이다.
- Adoption(발효)은 **운영적 tooling 결정**이며, 발효 시 `.claude/docs/integrations/`에 Adoption 문서 + `README.md`
  인덱스 1행만 추가한다. BASELINE / RFC / ADC / ADR / Public Contract / OmniRoute 변경 **없음**.
- Governance 절차가 필요해지는 유일한 경우 = wiki 페이지를 결정 권위로 쓰려는 시도 → **R5가 명시적으로 금지**한다.
- 이 문서 자체의 Jarvis 변경 = evidence 문서 1개 + `README.md` 1행. Architecture/Public Contract 미변경.

---

## 8. 최종 판정 (요구사항 10)

### 8.1 정책 확정 상태

| 항목 | 상태 |
|---|---|
| 유지 전략 (§1) | **APPROVED (2026-09-08).** MCP-first Hybrid — full plugin 3파일 patch 의존 제거(코드/매니페스트 패치 0건), 유지 항목 M1·M2·M3·M4. **B1 CLOSED** |
| 계층 경계 (§2) | **APPROVED (2026-09-08).** SoT(RFC/ADC/ADR/BASELINE/Evidence) / Claude-Mem(Session·Operational, push) / LLM Wiki(Project Knowledge·Derived Recall, pull·비권위) |
| Wiki 비권위 규칙 R5 (§3) | **APPROVED (2026-09-08).** wiki 페이지 = RFC/ADC/ADR/BASELINE/Evidence 입력 근거로만. **B4 CLOSED** (A2 + R5) |
| 운영 규칙 R1–R4 (redaction/permission/ingest scope/truncation) | **PENDING.** 초안 완성, "운영상 허용 범위"를 Evidence 범위 내에서 명시(초과 주장 없음). Live Smoke B2 이후 승인 → **B3 OPEN** |
| Ingest scope = `sync --project jarvis-os` (hook·수동 공통) / 무-scope 금지 | **명시 완료** (R3-a·R3-b; 2026-09-08 `include_projects` no-op 정정 반영, R3-e 잔여 한계 명시). R3 자체 승인은 B3에 포함(PENDING) |
| Architecture/Public Contract/Governance | **변경 없음 (확인).** 승인은 `.claude/docs/integrations/` 등급 운영 정책 발효일 뿐 SoT 불변 |
| 정책 발효(ratify) | **부분 발효.** §1·§2·R5 발효(위). R1–R4 및 Production Adoption은 미발효 |

### 8.2 Live Smoke 준비 상태

| 항목 | 상태 |
|---|---|
| 체크리스트 | **작성 완료** (§6, 11단계 + 결과표 + 판정 규칙, 약 10분) |
| 사전 스니펫 | **작성 완료** (§5, checkout/config/MCP/hook) |
| 실행 주체 | **사용자** — 로그인된 대화형 Claude Code 필요 (자동화 세션 구조적 불가) |
| B2 게이트 | 체크리스트로 닫을 수 있도록 준비됨. **아직 미수행** |

### 8.3 Production Adoption

**진행하지 않는다.** PR #166이 정의한 BLOCKING 게이트 상태 (2026-09-08 부분 승인 반영):

| 게이트 | 상태 |
|---|---|
| B1 패치 유지 전략 결정 + 소유자 | **CLOSED** — 사용자가 MCP-first Hybrid 승인 (§0.1 A1) |
| B2 로그인 대화형 Live Smoke (사용자) | **OPEN** — §6 체크리스트 준비됨, 사용자 수행 + PASS 필요 |
| B3 운영 규칙 R1–R4 승인 | **OPEN** — 초안 완성, Live Smoke 결과 반영 후 승인 |
| B4 wiki 비권위 규칙(R5) + 계층 경계 고정 | **CLOSED** — 사용자가 §2·R5 승인 (§0.1 A2·A3) |

**남은 단계**: (1) 사용자가 §6 Live Smoke를 직접 수행해 **B2 PASS** → (2) Smoke 결과를 반영해 **B3(R1–R4) 승인** →
(3) `.claude/docs/integrations/llm-wiki-candidate-002-adoption.md`를 작성하고 Production Adopt로 상향.
**그 전까지 Candidate #2 = CONDITIONAL PASS 유지.**

---

## Branch / PR / Cleanup

| | |
|---|---|
| branch | `claude/llm-wiki-002-adoption-policy` @ base `origin/main` `0de386c` (PR [#167](https://github.com/ok041110-del/jarvis-os/pull/167)) |
| diff | `.claude/docs/integrations/llm-wiki-candidate-002-adoption-policy.md` (신규 + 2026-09-08 부분 승인 개정) + `.claude/docs/README.md` (인덱스 1행) |
| 선행 Evidence | PR #161 / #162 / #163 / #165 / #166 — 전부 open, 미merge, 보존 |
| PR | #167 유지, **merge 안 함**. main 직접 커밋 없음 |
| cleanup | 정책 개정용 worktree 제거. 실제 `~/.claude` / `~/.omniroute` / `~/.claude-mem` 미접촉 — 이 작업은 정책 상태 문서 갱신만, 어떤 hook/MCP/sync도 실행하지 않음 |
