# LLM Wiki Candidate #2 — Production Adoption (최종)

작성일: 2026-09-08
대상: `Pratiyush/llm-wiki` v1.3.82 (@ `b1088890`, 검증 checkout `c4f9bc9`)
선행 정책: [`llm-wiki-candidate-002-adoption-policy.md`](llm-wiki-candidate-002-adoption-policy.md) (PR [#167](https://github.com/ok041110-del/jarvis-os/pull/167))
선행 Evidence: PR [#161](https://github.com/ok041110-del/jarvis-os/pull/161) · [#162](https://github.com/ok041110-del/jarvis-os/pull/162) · [#163](https://github.com/ok041110-del/jarvis-os/pull/163) · [#165](https://github.com/ok041110-del/jarvis-os/pull/165) · [#166](https://github.com/ok041110-del/jarvis-os/pull/166)

이 문서는 Candidate #2의 **Production Adoption 최종 기록**이다. 선행 정책(PR #167)이 정의한
BLOCKING 게이트 B1–B4가 모두 CLOSED 되었음을 공식 결과로 확정하고, 채택 범위·Evidence 연결·
이월 Open Issue를 기록한다. 새 검증·실험은 수행하지 않았다. `.claude/docs/` 규정대로
**실행환경 채택 evidence**이며 RFC/ADC/ADR/BASELINE의 source of truth가 아니다.

---

## 0. Production Adopt 판정

| 항목 | 값 |
|---|---|
| 대상 | `Pratiyush/llm-wiki` v1.3.82 (`b1088890`) — MCP-first Hybrid 형태 |
| 판정 | **PRODUCTION ADOPT** (2026-09-08) |
| 직전 상태 | CONDITIONAL PASS → 게이트 B1·B2·B3·B4 CLOSED로 해제 |
| 계층 | **Project Knowledge / Derived Recall Layer — non-authoritative, pull 전용** |
| 유지 형태 | MCP-first Hybrid (upstream 코드/매니페스트 패치 0건, 유지 항목 M1–M4) |
| Fallback | `nvk/llm-wiki` (무패치 shipped plugin 필수 + session-capture 계층 비활성 조건에서만) |
| Architecture / Public Contract | **변경 없음** — `.claude/docs/integrations/` 등급 운영 tooling 결정 |

Candidate #2는 Claude-Mem·OmniRoute·Token Optimizer가 RFC/ADC/ADR 없이 `.claude/docs/integrations/`
evidence로 채택된 것과 **동일 패턴**으로 채택된다. Governance 절차 트리거 없음(§7).

---

## 1. 게이트 최종 결과 (B1–B4 전부 CLOSED)

PR #166이 정의하고 PR #167이 상태를 관리해 온 4개 BLOCKING 게이트의 최종 결과.

| 게이트 | 결과 | 근거 |
|---|---|---|
| **B1** 패치 유지 전략 + 소유자 | **CLOSED** | 사용자 승인(2026-09-08, 정책 §0.1 A1). MCP-first Hybrid 확정 — full plugin 3파일 patch 의존 제거, 코드/매니페스트 패치 **0건**, 유지 항목 M1(MCP 등록)·M2(SessionStart hook 한 줄)·M3(머신-로컬 config)·M4(버전 pin). 정책 §1 |
| **B2** 로그인 대화형 Live Smoke | **CLOSED** | **사용자가 로그인된 대화형 Claude Code 세션에서 직접 수행**, S1·S3·S4·S5·S6·S7·S8 **전부 PASS** 확인. §6.3 B2 PASS 조건(S1·S3·S5·S6·S7·S8 전부 PASS + S4 PASS) 충족. 정책 §6 |
| **B3** 운영 규칙 R1–R4 승인 | **CLOSED** | R1 PASS · R2 PASS · R3 PASS(운영상 Accepted) · R4 PASS · R5 APPROVED. 아래 §1.1 |
| **B4** Wiki 비권위(R5) + 계층 경계 | **CLOSED** | 사용자 승인(2026-09-08, 정책 §0.1 A2 + A3). 계층 경계(SoT / Claude-Mem push / LLM Wiki pull·비권위) 고정 + R5 발효. 정책 §2 · §3 R5 |

### 1.1 B3 세부 — 운영 규칙 최종 판정

| R | 판정 | 근거 (재검증 없음 — 기존 Evidence 사용) |
|---|---|---|
| **R1** Redaction | **PASS** | key-shaped provider secret은 `_DEFAULT_TOKEN_PATTERNS`로 config 무관 항상 redact (PR #161, VERIFIED). identity(handle/encoded-home/scratchpad path)는 머신-로컬 `sessions_config.json` `extra_patterns`에 shape 등록(R1-a) + 기본 과탐 패턴을 `["'\s]*[:=]["'\s]*` 구분자로 축소(R1-b) 완료. redaction dry-run 재확인: secret 전량 `<REDACTED>`, prose false-positive(`"token overhead"` 류) 제거, identity 전 클래스 마스킹. 배포 레이어 `wiki/` 대상 `wiki_search` 사후 감사(R1-c) handle/절대경로/encoded-home/UID/prose-FP **0 hits**. 잔여는 정책 "운영상 허용 범위"(§3 R1, lossy 치환 + 로컬 머신 + `site/` 미deploy) |
| **R2** 파일 권한 | **PASS** | `raw/`·`wiki/`·`site/` 전부 `0700` 부모 아래(R2-a) — `chmod 700 wiki` 적용으로 정렬 완료. hook·수동 sync `umask 077` 프리픽스(R2-b, 정책 §5.4). 파일 `0644` 잔존은 R2-a 전제 하 허용(단일 사용자 개발 머신) |
| **R3** Ingest scope | **PASS (운영상 Accepted)** | `--project jarvis-os`가 현재 후보의 유효한 유일 scope enforcement(`convert.py:1478` 서브스트링 게이트). SessionStart hook(`.claude/settings.json`)이 정책 §5.4와 verbatim 일치하며 `--project jarvis-os` 포함. scoped sync 실동작 확인: `filtered=60`(비-jarvis-os 세션 전량 제외), `converted=0 / unchanged=70`(idempotent), in-scope N ≈ 71–73 (< 100, §6.3 정지 조건 미발동). **no-scope sync 금지의 절차적 보장을 사용자가 명시적으로 수용** → CONDITIONAL 근거 해소. 코드 레벨 non-enforcement는 미해결 항목이 아니라 **수용된 운영 제약**으로 확정(§5 이월) |
| **R4** Truncation (93% 축소) | **PASS** | 결정론 변환의 공격적 truncation은 **수용된 설계 특성**. Evidence 원문의 유일 보관처 = git + `.claude/docs/integrations/`(R4-a), canonical 문서 sha256 불변 확인. wiki `raw/`는 사실 링크·요약이며 evidence 아카이브 아님. wiki 인용 시 원본 경로/커밋 병기(R4-b, `sources:` 규약 강제) |
| **R5** Wiki 비권위 | **APPROVED** | 사용자 승인(정책 §0.1 A3). wiki 페이지 = RFC/ADC/ADR/BASELINE/Evidence의 입력 근거(reference)로만, 결정·규범·SoT 인용 근거로 승격 불가(R5-a). `wiki/concepts/*.md`의 권위 오인 위험은 `overview.md` disclaimer로 완화(R5-b) |

**B3 = CLOSED.** R1·R2·R4 PASS, R3 PASS(운영상 Accepted), R5 APPROVED. 미해결 항목 없음.

---

## 2. 적용 범위 (Scope of Adoption)

### 2.1 채택되는 것

| # | 항목 | 성격 | 위치 |
|---|---|---|---|
| M1 | MCP server 등록 (`python3 -m llmwiki.mcp`) | Jarvis 측 설정 (upstream 파일 아님) | 프로젝트 `.mcp.json` 또는 `claude mcp add` (정책 §5.3) |
| M2 | SessionStart hook 한 줄 (`… python3 -m llmwiki sync --project jarvis-os …`) | Jarvis 측 설정 (upstream 파일 아님) | jarvis-os `.claude/settings.json` (정책 §5.4) |
| M3 | `examples/sessions_config.json` redaction 튜닝 (identity `extra_patterns`, `real_username`) | 머신-로컬 설정 데이터 — **커밋 금지** (R1) | `~/tools/llm-wiki/` 로컬 (정책 §5.2) |
| M4 | 후보 checkout 버전 pin | 문서화된 커밋/태그 | `b1088890` / `v1.3.82` |

- upstream 코드/매니페스트 패치 **0건**. 재-clone 시 M1·M2는 Jarvis가 소유하는 설정이라 영향 없음,
  M3만 로컬 재적용 필요(스니펫은 정책 §5.2에 고정).
- `.claude/settings.json`(사용자 배선 SessionStart hook)은 개별 환경 설정이며 이 문서/PR #167의 커밋 대상이 아니다.

### 2.2 채택으로 바뀌지 않는 것

- **Architecture / BASELINE / Public Contract / OmniRoute** — 변경 없음.
- **RFC / ADC / ADR** — 신규·변경 없음. Governance 절차 트리거 없음.
- **Claude-Mem / Token Optimizer / Task Observer** — 무관, 무변경. LLM Wiki와 Claude-Mem은
  소비 방식(pull vs push)·보존성(영속 vs 휘발)·근거성(provenance-linked vs narrative)이 달라 **보완적**으로 병존.
- **canonical evidence 문서** — `docs/architecture/baseline/BASELINE.md`, `.claude/docs/integrations/langgraph.md`,
  `docs/00_governance/GLOSSARY.md` sha256 불변 확인. wiki `sources/jarvis-arch/`의 파생 페이지는
  `authority: derived` frontmatter로 명시(비권위).

### 2.3 Adoption에 따른 Jarvis repo 변경

1. `.claude/docs/integrations/llm-wiki-candidate-002-adoption.md` (이 문서) — 신규
2. `.claude/docs/README.md` — 인덱스 1행 갱신

그 외 diff 없음.

---

## 3. Wiki 역할 규정 — Derived Recall / Non-authoritative

정책 §2 · §3 R5 발효 내용을 채택 기준으로 확정한다.

| 계층 | LLM Wiki (Candidate #2) |
|---|---|
| 정의 | immutable `raw/` 사실 + 큐레이션 `wiki/` + `sources:` provenance + dual-link 그래프 |
| 소비 방식 | **pull 전용** (MCP tool / repo-local slash). **자동 컨텍스트 주입 없음** (PR #161·#163 코드 + 세션 실측으로 0 확정, Live Smoke S6 PASS로 재확인) |
| 보존성 | 영속·portable, 단 **파생·비권위** |
| 권위 | **없음.** RFC/ADC/ADR/BASELINE/Evidence를 대체·갱신·인용 근거로 승격 불가 |
| 허용 용도 | 프로젝트 지식의 derived recall — 과거 세션/결정/파일 맥락을 pull로 조회, 답변은 인용 기반 |
| 금지 용도 | 결정 권위, 규범 근거, SoT 인용, evidence 아카이브 |

- **불변 규칙**: Architecture/Governance 변경은 이 채택과 무관하게 **항상 RFC → ADC → ADR**.
- **disclaimer 고정**: wiki `overview.md`(가능하면 `SOUL.md`/`CRITICAL_FACTS.md`)에
  "이 wiki는 Jarvis Architecture/Governance의 source of truth가 아니다. 모든 결정은
  `docs/decisions/{rfc,adc,adr}/`에 있다." 를 유지(R5-b).

---

## 4. Evidence 연결 (PR #167 게이트 ↔ 실제 Evidence)

| 게이트 / 규칙 | 근거 Evidence | 형태 |
|---|---|---|
| B1 (유지 전략) | PR #162 §P0-1 (3파일 패치 목록), PR #163 §Patch 유지성, PR #166 §최종판단 | 패치 대상별 "MCP-first Hybrid에서 불필요" 확정 (정책 §1.1) |
| B2 (Live Smoke) | 사용자 대화형 세션 직접 수행 결과 — S1(MCP 연결), S3(scoped sync N<100), S4(권한), S5(hook 발화), S6(자동 주입 0), S7(`wiki_query` 인용 기반), S8(`wiki_search` 정확 매치) 전부 PASS | 정책 §6.1 체크리스트, §6.3 판정 규칙 |
| B3 / R1 (redaction) | PR #161 (`_DEFAULT_TOKEN_PATTERNS` + pytest PASS), PR #162 (identity `extra_patterns` 0 hits, lossy), PR #163 (`"token overhead"` 과탐 실측) + Task-G redaction dry-run·`wiki_search` 사후 감사 0 hits | 정책 §3 R1-a~d |
| B3 / R2 (permission) | PR #162 (`umask 077` 경로 0600), PR #163 (`0644` 잔존) + `chmod 700` 부모 디렉터리 정렬 | 정책 §3 R2-a~b |
| B3 / R3 (ingest scope) | PR #163 (무-scope 129 세션 실측), 2026-09-08 `include_projects` no-op 정정 (`convert.py:32-33` 선언만, `convert_all`은 `cli.py:704`→`convert.py:1478` `--project` 서브스트링 게이트만 소비), dry-run 무-scope N=131 / `--project jarvis-os` N=71 (131 = 71 + 60) + scoped sync 실동작(`filtered=60`, `converted=0`) | 정책 §3 R3-a~e, §5.4 |
| B3 / R4 (truncation) | PR #161 (`tool_result_chars: 500` 등 공격적 truncation, 대형 governance Read 원문 `raw/` 미유입) + canonical sha256 불변 확인 | 정책 §3 R4-a~b |
| B4 / R5 (비권위) + 계층 경계 | 사용자 승인 (정책 §0.1 A2·A3), PR #161·#163 (auto-injection 0) | 정책 §2 표, §3 R5-a~c |

선행 Evidence PR #161 / #162 / #163 / #165 / #166은 **전부 보존**한다(merge 여부 무관, 이 채택의 근거 chain).

---

## 5. Known Open Issues (이월 — 운영상 허용 범위 내)

아래 항목은 채택을 차단하지 않으며, 정책 §4가 정의한 "운영상 허용 범위" 안에서 **이월**된다.
어느 것도 "Evidence 범위를 넘어 해결됐다"고 주장하지 않는다.

### 5.1 N-series (Ingest scope / 세션 수) Open Issues

| # | 항목 | 상태 | 허용 범위 / 이월 조건 |
|---|---|---|---|
| N-1 | no-scope sync 금지가 **절차적**이며 코드로 강제되지 않음 | Accepted (수용된 운영 제약) | 운영자가 SessionStart hook + 수동 CLI에서 **반드시 `--project jarvis-os`만** 사용. bare `python3 -m llmwiki sync` 실행 금지 |
| N-2 | MCP `wiki_sync` 툴이 `--project`를 하위 커맨드에 전달하지 않음 (`mcp/server.py` `tool_wiki_sync`) | Accepted | MCP `wiki_sync`는 **dry-run 확인 전용**. 실제 백필·주기 sync는 CLI/hook 경로(`--project jarvis-os`)로만 |
| N-3 | `--project`가 프로젝트 슬러그 **서브스트링** 매치 (R3-e) | Accepted | 단일 사용자·알려진 프로젝트명 조건에서 허용. 정확 매치 필요 시 §5.3 upstream 옵션 |
| N-4 | 정지 조건 — scoped 백필 결과 **N ≥ 100 이면 scope leak으로 간주, 즉시 중단** | 유지 (활성 규칙) | 현재 dry-run·실측 N ≈ 71–73. 초과 시 `--project jarvis-os` 인자 누락 여부 재확인 (정책 §6.3, R3-c) |
| N-5 | `include_projects` config 키가 현재 후보에서 no-op | Accepted (문서화됨) | `sessions_config.json`에 no-op 주석과 함께 유지(forward-compat 표식). scope 근거로 인용 금지 (R3-d) |
| N-6 | sync가 content-hash gated → 기존 `raw/`의 패치 前 인스턴스는 해당 transcript 변경 전까지 잔존 | Accepted | `raw/`·`wiki/`는 "redacted-but-imperfect" 2차 방어선(R1-d). 배포 레이어 `wiki/` 사후 감사는 0 hits |

### 5.2 기타 이월 Open Issues (정책 §4)

| Open Issue | 상태 | 허용 범위 |
|---|---|---|
| identity redaction lossy / shape 수기 입력 | Mitigated (해결 아님) | 로컬 머신 + `site/` 미deploy 시 허용. 외부 공유 시 R1-c 감사 필수 |
| 산문 과탐 redaction (기본 패턴) | R1-b로 축소 적용 | 잔여 과탐은 로컬 개발 조건에서 허용 |
| `0644` (hook 밖 경로) | Mitigated 부분 (upstream 필요) | R2-a(`0700` 부모) 전제 시 허용. 공유 머신은 R2-a 없이 Adoption 불가 |
| 93% truncation | Open (설계) | R4 전제(wiki ≠ evidence 아카이브) 하 허용 |
| `wiki_query` ranking / `overview.md` append 품질 | Open (품질, 비차단) | wiki 성장 시 주기 점검 |
| at-scale synthesis 품질 | UNVERIFIED (유지) | 초기 소규모 corpus 허용. 페이지 50+ 도달 시 재측정 |
| 정밀 token/cost 델타 | UNVERIFIED (유지) | 방향성(auto-injection 0, MCP ≈ 수백 토큰)만 확인. Live Smoke S9(선택)에서 1회 기록 |
| network-level egress absence | UNVERIFIED (유지) | code-read + `lsof`(소켓 0) + credential 미참조로 갈음. ollama/agent backend 미사용 조건 |

### 5.3 upstream 옵션 (선택 — 채택 전제조건 아님)

- `marketplace.json` / `plugin.json` 스키마 수정 → full plugin 무패치 패키징 선택지 (정책 §1.2)
- `filters.include_projects` / `exclude_projects` 를 `convert_all()`에 구현 → `--project` 서브스트링 대신 정확 매치 config scoping (정책 §5.3 / R3 upstream 옵션)

둘 다 커뮤니티 기여로 제출 가능하나 **Jarvis Adoption의 전제조건으로 걸지 않는다**. 병합 시 별도 검토를 연다.

---

## 6. 발효되는 운영 규칙 (요약)

정책 §3 R1–R5 전문이 이 채택으로 **운영 규칙 본문**이 된다. 요지:

- **R1** — sync 전 `real_username` / GitHub handle / scratchpad 경로 shape를 머신-로컬 `sessions_config.json`
  `extra_patterns`에 등록(커밋 금지). 기본 과탐 패턴은 좁은 형태 유지. `site/` deploy·외부 공유 전 `wiki_search` 감사 필수.
  `raw/`·`wiki/`에 실제 credential을 직접 넣지 않는다(2차 방어선).
- **R2** — `raw/`·`wiki/`·`site/` 는 `0700` 부모 아래. 수동 sync·에이전트 `wiki/` 쓰기는 `umask 077` 프리픽스.
- **R3** — SessionStart hook + 모든 실제 sync는 `python3 -m llmwiki sync --project jarvis-os`. 무-scope ingest 금지.
  MCP `wiki_sync`는 dry-run 전용. 백필 결과 N ≥ 100 이면 즉시 중단.
- **R4** — Evidence 원문의 유일 보관처는 git + `.claude/docs/integrations/`. wiki 인용 시 원본 경로/커밋 병기.
  wiki를 evidence 아카이브로 쓰지 않는다.
- **R5** — wiki 페이지는 RFC/ADC/ADR/BASELINE/Evidence의 입력 근거로만. 결정·규범·SoT 인용 근거로 승격 불가.
  `overview.md` disclaimer 유지.

---

## 7. Architecture / Public Contract / Governance

**변경 없음 — 명시적으로 확인.**

- 새 architectural component·runtime·public interface 추가 없음. LLM Wiki(Candidate #2)는
  `.claude/docs/integrations/` 등급의 로컬 개발 도구다.
- Adoption은 **운영적 tooling 결정**이며, repo 변경은 이 evidence 문서 1개 + `README.md` 인덱스 1행뿐이다.
  BASELINE / RFC / ADC / ADR / Public Contract / OmniRoute 변경 **없음**.
- Governance 절차가 필요해지는 유일한 경우 = wiki 페이지를 결정 권위로 쓰려는 시도 → **R5가 금지**한다.
- wiki `sources/jarvis-arch/`의 canonical-derived 페이지는 `authority: derived` + `derived_from: <commit>` +
  `source_file:` frontmatter로 파생·비권위임을 명시한다. canonical 원본(BASELINE/langgraph/GLOSSARY) sha256 불변.

---

## 8. Branch / PR

| | |
|---|---|
| branch | `claude/llm-wiki-002-adoption-policy` @ PR [#167](https://github.com/ok041110-del/jarvis-os/pull/167) |
| diff (이 커밋) | `.claude/docs/integrations/llm-wiki-candidate-002-adoption.md` (신규) + `.claude/docs/README.md` (인덱스 1행) |
| 선행 Evidence | PR #161 / #162 / #163 / #165 / #166 — 전부 보존 |
| PR | #167 유지. merge·branch 삭제는 기존 승인 절차대로 |
| main 직접 커밋 | 없음 |
| 미접촉 | `~/.claude` / `~/.omniroute` / `~/.claude-mem` — 이 작업은 문서 산출만, hook/MCP/sync 미실행. `.claude/settings.json`(사용자 배선)은 커밋 대상 아님 |
