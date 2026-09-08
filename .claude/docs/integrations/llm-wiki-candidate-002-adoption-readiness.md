# LLM Wiki Candidate #2 — Production Adoption Readiness Review

검토일: 2026-09-08
대상: `Pratiyush/llm-wiki` v1.3.82 (@ `b1088890`)
근거: PR [#161](https://github.com/ok041110-del/jarvis-os/pull/161)(PoC) · [#162](https://github.com/ok041110-del/jarvis-os/pull/162)(P0/P1 Resolution) · [#163](https://github.com/ok041110-del/jarvis-os/pull/163)(Live Validation) · [#165](https://github.com/ok041110-del/jarvis-os/pull/165)(Candidate #1 vs #2 Final Comparison) — 전부 open, 미merge.

이 문서는 **새 기능 개발·Candidate 소스 수정 없이** 현재 남은 Open Issue만 대상으로 Adoption 준비도를 평가한다.
`.claude/docs/` 규정대로 실행환경 검증 evidence이며 RFC/ADC/ADR/BASELINE의 source of truth가 아니다.

## 판정

**CONDITIONAL PASS.** Production Adoption으로 상향하지 않는다.

Candidate #2의 알려진 blocker(P0 marketplace schema, P0 hook import)는 vendored patch로 **해결 가능성이 VERIFIED**이고,
identity leak(P1)·hook 경로 권한(P1)은 config/`umask`로 **부분 완화(Mitigated)**됐으며, retrieval/synthesis(소규모)·
auto-injection 0·egress(code+lsof)는 로그인 세션에서 **실측 PASS**다. 그러나 Production Adoption에 반드시 필요한
4개 게이트 중 **하나(로그인 대화형 Claude Code에서 사람이 직접 수행하는 1회 스모크)**가 구조적 제약으로 여전히
UNVERIFIED이고, 나머지 3개(패치 유지 전략 결정, 운영 규칙 승인, wiki 규범-아님 규칙 고정)는 이 검토가 초안을
제시했을 뿐 아직 사람 승인 전이다. 따라서 지금은 **Conditional Pass** — Hold로 낮출 근거(구조적 안전 결함,
해결 불가 항목)는 없고, Production Adopt로 올릴 근거(4개 게이트 충족)도 없다.

## 1. Adoption 선행조건 충족 여부 재검토 (요구사항 1)

Final Comparison(PR #165)이 정리한 선행조건 5개 + Live Validation(PR #163)의 "Adoption 상향 3조건"을 현재 Evidence로 재평가.

| 선행조건 | 출처 | 현재 상태 | 판정 |
|---|---|---|---|
| (a) 패치 유지 전략 확정 (upstream PR merge vs vendored fork) | #163 조건1, #162 OI1, #165 §8-1 | 전략 **미결정**. 3파일 패치가 재-clone 시 소실됨은 #163에서 실측. upstream PR 존재 여부 **미확인(UNVERIFIED)** | **미충족 (결정 필요)** |
| (b) 로그인 대화형 Claude Code 1회 live 스모크 (사람이 직접) | #163 조건2, #165 §8-2 | plugin install/enabled·always-on 토큰·임의-cwd hook은 **로그인+격리 config 동시 불가**로 UNVERIFIED. 대체 표면(project `.claude/commands/` + `--mcp-config` MCP)은 #163에서 live PASS | **미충족 (사람 수행 필요, constraint-blocked)** |
| (c) redaction 운영 규칙 + `0644` limitation 문서화·수용 | #163 조건3, #162 OI2·3, #165 §8-3 | 규칙 **미작성/미승인**. 아래 §4에 최소 초안 제시. 기술적 근거(오탐 redaction 실측, `umask` 완화 범위)는 #163에 있음 | **미충족 (규칙 승인 필요)** |
| (d) hook ingest scoping 운영 규칙 | #163 OI3, #165 §8-4 | 무-scope 시 129 세션 전량 변환 실측(#163). `include_projects` scoping 방법은 존재하나 규칙 **미고정** | **미충족 (규칙 승인 필요)** |
| (e) wiki를 규범 아닌 회상 층으로 고정 | #161 §Governance Boundary, #165 §8-5 | 완화안(disclaimer 고정 + 입력 근거로만) 제시됨. **운영 규칙으로 미채택** | **미충족 (규칙 승인 필요)** |

**요약**: 5개 선행조건 전부 아직 미충족. 단 (a)(c)(d)(e)는 **사람의 결정·문서 승인**만으로 충족 가능(추가 개발·테스트 불필요),
(b)만 **로그인 대화형 세션에서 사람이 직접 수행**해야 하며 자동화 세션에서는 구조적으로 불가.

## 2. 현재 남은 Open Issues — 재분류 (요구사항 2)

새 개발/소스 수정 없이, 현재 상태 그대로의 Open Issue만.

| ID | Open Issue | 현재 분류 | 근거 |
|---|---|---|---|
| O1 | P0 패치 3파일이 vendored fork/upstream PR 필요 (재-clone 시 소실) | **Open (결정 필요)** | #162 OI1, #163 §Patch 유지성 |
| O2 | 로그인 세션 내 plugin enabled/hook/always-on 토큰 = UNVERIFIED (constraint-blocked) | **UNVERIFIED (사람 스모크로만 해소)** | #163 조건2 |
| O3 | identity leak (username/handle/path) — config `extra_patterns`로 0 hits, full-match 치환이라 lossy, per-user 수기 입력 | **Mitigated (잔여: lossy + 수기)** | #162 §P1 |
| O4 | 생성물 `0644` — hook 경로만 `umask 077`→`0600`. `/wiki-*` slash·수동 실행·에이전트 Write `wiki/*.md`는 `0644` | **Mitigated (부분)** | #162 §P1, #163 §Security |
| O5 | 오탐 redaction — 기본 `extra_patterns[0]`가 산문 "token/secret/key/password + 단어"를 `<REDACTED>` (`"token overhead"` 실측) | **Open (지식 손실 위험)** | #163 §Session→Wiki |
| O6 | 결정론 변환 93% truncation (대형 governance Read 원문 raw/에 미포함) | **Open (설계, 수용 가능)** | #161 OI6 |
| O7 | hook × 실제 `~/.claude` HOME 무-scope → 129 세션 전량 ingest | **Open (규칙으로 차단 가능)** | #163 OI3 |
| O8 | `wiki_query` 결정 요약 ranking 불완전 + 매 호출 `overview.md` append | **Open (품질, 비차단)** | #161 OI7 |
| O9 | at-scale synthesis 품질 = UNVERIFIED (3-page corpus만) | **UNVERIFIED (유지)** | #163 §Query, 요구사항 6 |
| O10 | 정밀 token/cache/cost = UNVERIFIED (n=2, trivial 프롬프트, 방향성만) | **UNVERIFIED (유지)** | #163 §Token/Context, 요구사항 6 |
| O11 | network-level egress absence = UNVERIFIED (packet capture 미수행; code-read + `lsof` 소켓 0 + credential 미참조로 갈음) | **UNVERIFIED (유지)** | #163 §Egress, 요구사항 6 |
| O12 | `claude plugin marketplace add`가 격리 `CLAUDE_CONFIG_DIR`에도 실제 `known_marketplaces.json` touch (내용 무영향) | **Open (무영향, 비차단)** | #161 OI8 |
| O13 | upstream 문서/`setup.sh`/`./config.json` 로딩 주석 불일치 | **Open (upstream 소관, Jarvis는 정정 경로 사용)** | #161 F3·F4, #162 OI4 |
| O14 | `graph`(`graphifyy`)·`e2e`(Playwright) extra, 실제 synthesis backend(ollama/agent) 미검증 | **Open (미사용 시 무관)** | #161 F5 |

## 3. Patch 유지 전략 — 선택지 비교와 권고 (요구사항 3)

패치 표면(현재):
- **매니페스트 3파일** — `.claude-plugin/marketplace.json`(`owner`/`source`), `.claude-plugin/plugin.json`(`commands`/`skills` 경로, 깨진 `hooks` 키 삭제), 신규 `hooks/hooks.json`.
- **redaction 튜닝 1파일** — `examples/sessions_config.json`(`real_username` + `extra_patterns` identity 클래스).
- **hook 커맨드 재작성** — 문서화된 `convert.py` → `python3 -m llmwiki sync`.

| 선택지 | 내용 | 장점 | 단점 / 비용 |
|---|---|---|---|
| **A. Upstream PR merge** | 매니페스트 스키마 수정을 `Pratiyush/llm-wiki`에 PR | 병합 시 장기 유지 부담 0, 스키마 수정은 객관적으로 옳음(현행 Claude Code 스키마 준수) | 메인테이너 응답·타이밍 **UNVERIFIED**, Jarvis Adoption을 외부 일정에 종속시킬 수 없음, upstream 스키마 재변경 시 재발 가능 |
| **B. Vendored fork** | Jarvis 통제 하 fork/vendored copy, 버전 pin | 완전 통제·결정론적, upstream 무관하게 안정 | upstream update마다 rebase·재검증 부담, drift 위험, 소유자 지정 필요 |
| **C. MCP-only + repo-local (매니페스트 패치 회피)** | plugin 패키징을 쓰지 않고 (1) MCP server(`python3 -m llmwiki.mcp`) 등록 + (2) repo-local `.claude/commands/` 사용. 매니페스트 3파일 패치 **불필요**. 남는 것은 hook 재작성 + `sessions_config.json` redaction뿐 | 패치 표면이 4파일 → **사실상 2개(hook 1줄 + config)**로 축소. MCP는 로그인·네트워크 불필요(#161 실측). "pull 전용 Project Knowledge Layer" 프레이밍과 정확히 일치 | 자동 등록(commands/skills/hooks 일괄)이 없어 MCP·commands를 각 환경에서 명시 등록. plugin `enabled` UI 상태를 못 씀 |
| **D. Hybrid (권고)** | **C를 1차 채택** + A를 병행 제출(강제 아님) + full plugin 패키징이 나중에 필요해지면 B로 전환 | 지금 Adoption을 외부 일정에 종속시키지 않음, 패치 표면 최소, upstream 병합 시 자연 소멸, fork는 필요할 때만 | MCP/commands 등록 절차를 `.claude/docs/`에 문서화해야 함(1회) |

**권고 = D (Hybrid, MCP-first).** 근거: (1) Jarvis가 LLM Wiki에 기대하는 자리는 pull 전용 Project Knowledge Layer이며
MCP server + repo-local commands로 그 자리를 100% 커버한다(#161·#163 실측). (2) 매니페스트 3파일 패치를 제거하면
"vendored fork 유지 부담"이라는 가장 큰 Open Issue(O1)가 사실상 소멸한다. (3) upstream PR(A)은 커뮤니티 기여로
병행하되 Jarvis Adoption의 전제조건으로 걸지 않는다. (4) full plugin 패키징(자동 등록 + `enabled` 상태)이 향후
반드시 필요해지는 경우에만 B(vendored fork)로 승격하고, 그때 별도 검토를 연다.

이 권고를 채택하면 선행조건 (a)는 **"MCP-first 채택 + hook/config 2개 항목만 Jarvis가 유지 + upstream PR 병행"**으로 확정된다.

## 4. 최소 운영 규칙 (요구사항 4)

새 개발 없이 **설정·절차·문서**만으로 성립하는 최소 규칙. Adoption 시 `.claude/docs/`에 고정.

### R1 — Redaction 오탐/누락 대응 (O3·O5)

- **R1-a (누락 방어)**: 각 머신에서 sync를 켜기 전, 사용자 본인의 `real_username`, GitHub handle,
  scratchpad 경로 shape를 `examples/sessions_config.json`의 `extra_patterns`에 추가한다(머신-로컬, 커밋 금지).
  자동 감지가 아니므로 이 입력은 사용자 책임이다.
- **R1-b (오탐 억제)**: 기본 `extra_patterns[0]`(산문 "token/secret/key/password + 단어" 매칭)는 지식 손실 위험이 있다.
  소스 수정 없이 대응 → 이 패턴을 머신-로컬 config에서 **제거하거나 더 좁은 형태로 교체**하고(설정값 변경일 뿐 소스 수정 아님),
  key-shaped provider redaction(`_DEFAULT_TOKEN_PATTERNS`, 항상 적용)에 의존한다.
- **R1-c (사후 감사)**: `site/` deploy 또는 wiki 공유 전에 `wiki_search`로 handle/절대경로/UID 클래스를 1회 grep 감사한다.
- **R1-d**: `raw/`·`wiki/`는 "redacted-but-imperfect"로 취급한다. 실제 credential을 세션 프롬프트/도구 입력에 직접 넣지 않는다
  (redaction은 2차 방어선이지 1차 방어선이 아니다).

### R2 — wiki `0644` 봉쇄 (O4)

- **R2-a**: LLM Wiki hub 디렉터리(`raw/`·`wiki/`·`site/` 상위)는 **`0700` 부모 디렉터리** 아래에 둔다.
  파일이 `0644`여도 디렉터리 레벨에서 타 사용자 접근이 차단된다(다중 사용자 머신 대응).
- **R2-b**: sync는 가능하면 SessionStart hook 경로(`umask 077` → `0600`)로만 실행한다.
  수동 `python3 -m llmwiki sync` 및 에이전트 `wiki/` 쓰기는 `umask 077 && …` 프리픽스를 절차로 강제한다.
- **R2-c**: 단일 사용자 개발 머신에서는 `0644` 자체의 위험이 낮음 — R2-a만으로 충분하며, code-level fix(0600 write)는 upstream 소관으로 남긴다.

### R3 — Ingest scope (O7)

- **R3-a**: SessionStart hook 및 수동 sync는 **반드시** `sessions_config.json`의 `include_projects`를 `jarvis-os` 프로젝트로
  scoping하거나 격리 HOME과 병행한다. 무-scope 실행 금지(129 세션 전량 변환 실측).
- **R3-b**: 채택 문서에 정확한 `include_projects` 값과 hook 커맨드 전문을 명시한다.
- **R3-c**: 최초 1회 백필은 scoped 상태에서 수행하고, 결과 세션 수를 기대치와 대조 확인한다.

### R4 — 93% truncation (O6)

- Evidence 원문은 `.claude/docs/integrations/` + git이 유일 보관처다. wiki `raw/`는 **사실 링크·요약**이지 evidence 원문이 아니다.
  대형 governance 문서를 wiki에서 "인용"할 때는 항상 원본 경로/커밋을 함께 표기한다(이미 `sources:` 규약이 강제).

## 5. 역할 경계 고정 (요구사항 5)

- **LLM Wiki (Candidate #2) = Project Knowledge / Derived Recall Layer.** `.claude/docs/integrations/` evidence와 동급의 파생 계층이다.
  immutable `raw/` 사실 + 큐레이션 `wiki/` + `sources:` provenance + dual-link 그래프. **pull 전용**(MCP tool / repo-local slash),
  자동 context 주입 없음(#161·#163 코드+세션 실측으로 0 확정).
- **Source of Truth 불변**: Architecture/Governance는 `docs/architecture/baseline/BASELINE.md` + `docs/decisions/{rfc,adc,adr}/` +
  `.claude/docs/integrations/` evidence. Architecture 변경은 이 검토와 무관하게 항상 **RFC → ADC → ADR**.
  wiki `concepts/`·`sources/`는 RFC/ADC/ADR/BASELINE/Evidence를 **대체·갱신·인용 근거로 승격할 수 없다**.
- **Claude-Mem 경계 유지**: Claude-Mem = Session/Operational Memory(SessionStart hook이 AI 요약을 `additionalContext`로 push, 휘발적).
  LLM Wiki = 조회 시점 구조화 프로젝트 지식(pull, 영속, provenance-linked). 두 계층은 세션 transcript에서 파생돼 "무슨 작업/결정/파일"
  수준이 중복되지만 소비 방식·보존성·근거성이 다르다. **live 병렬 실행 비교는 Claude-Mem 미설치로 UNVERIFIED(유지).**

## 6. UNVERIFIED 유지 항목 (요구사항 6)

아래는 이 검토로 해소되지 않으며 실제 Evidence 없이는 UNVERIFIED로 유지한다:

| 항목 | 사유 |
|---|---|
| 정밀 token/cache/cost, plugin always-on 토큰 | #163 A/B는 n=2·trivial 프롬프트 → 방향성(MCP ≈ 수백 토큰, auto-injection 0)만 유효 |
| 대규모 wiki에서의 retrieval ranking + synthesis 품질 | #163은 3-page corpus. at-scale 미측정 |
| network-level egress absence | packet capture 미수행. code-read + `lsof`(소켓 0) + credential 미참조로 갈음 |
| 로그인 대화형 세션 내 plugin install/enabled 상태, 임의-cwd에서 ancestor project hook 발화 | 로그인 + 격리 `CLAUDE_CONFIG_DIR` 동시 불가 (구조적 제약) |

이 항목들은 §7에서 **Adoption 후 Open 허용**으로 분류한다(단 하나, 로그인 스모크는 예외 — §7 참조).

## 7. Adoption 필수 조건 vs Adoption 후 Open 허용 (요구사항 7)

### A. Production Adoption 전 반드시 충족 (BLOCKING)

| # | 조건 | 충족 방법 | 현재 |
|---|---|---|---|
| B1 | **패치 유지 전략 결정 및 소유자 지정** | §3 권고(D: MCP-first Hybrid) 채택 여부를 사람이 결정. 유지 대상 = hook 커맨드 1줄 + `sessions_config.json`. 재검토 트리거 = 후보 minor 버전 업 | 결정 대기 (개발 불필요) |
| B2 | **로그인 대화형 Claude Code 1회 스모크 (사람 수행)** | 실제 로그인 세션에서: MCP server 등록 → `wiki_search`/`wiki_query` 1회 → SessionStart hook(scoped) 1회 발화 → always-on 토큰 델타 기록. plugin 패키징을 쓸 경우 `claude plugin install` + `enabled` 확인 추가 | UNVERIFIED (constraint-blocked, 자동화 불가) |
| B3 | **운영 규칙 R1–R4 문서화 및 사람 승인** | §4를 `.claude/docs/integrations/` 채택 문서에 고정하고 승인 | 초안 제시됨, 승인 대기 |
| B4 | **wiki 규범-아님 규칙 고정** | §5 경계를 채택 문서 + (선택) wiki `SOUL.md`/`CRITICAL_FACTS.md`에 명시. "wiki 페이지는 RFC/ADC/ADR 입력 근거로만, 결정 자체로는 불가" | 초안 제시됨, 승인 대기 |

B1·B3·B4는 **추가 개발·테스트 없이 사람의 결정·문서 승인만으로 충족**된다. B2만 로그인 대화형 세션에서 사람이 직접 10분 규모로 수행해야 한다.

### B. Adoption 후 Open으로 남겨도 되는 항목 (NON-BLOCKING, 추적)

| # | 항목 | 남겨도 되는 이유 | 추적 방법 |
|---|---|---|---|
| N1 | 93% truncation (O6) | 설계 특성. evidence 원문은 git/`.claude/docs/`가 보관(R4). wiki는 사실 링크 | 대형 문서 인용 시 원본 경로 병기 규약(이미 `sources:` 강제) |
| N2 | `wiki_query` ranking 불완전 + `overview.md` append (O8) | 품질 이슈, 안전성 아님. 소규모에서 정확 회수 확인됨 | wiki 성장 시 주기 점검 |
| N3 | at-scale synthesis 품질 UNVERIFIED (O9) | 초기 corpus는 소규모. 인용 기반·hallucination 0 확인됨 | 페이지 수 임계(예: 50+) 도달 시 재측정 |
| N4 | 정밀 token/cost UNVERIFIED (O10) | 방향성(auto-injection 0, MCP ≈ 수백 토큰) 확인. 비용 위험 낮음 | B2 스모크에서 1회 델타 기록, 이후 주기 확인 |
| N5 | network-level egress UNVERIFIED (O11) | 로컬 전용 도구. code + `lsof` + credential 미참조로 갈음. 네트워크 backend(ollama/agent) 미사용 조건 | ollama/agent backend 활성화 시에만 재검토 |
| N6 | identity redaction lossy/수기 (O3) | R1로 절차 커버. full-match 치환은 읽힘 유지 | R1-c 사후 감사 |
| N7 | `0644` (hook 밖 경로) (O4) | R2-a(`0700` 부모)로 봉쇄. 단일 사용자 머신 위험 낮음 | code-level fix는 upstream 대기 |
| N8 | `known_marketplaces.json` touch (O12) | 내용 무영향 (llmwiki 미등록 확인) | — |
| N9 | upstream 문서/`setup.sh` 불일치 (O13) | Jarvis는 정정 경로(`-m llmwiki sync`) 사용. upstream 소관 | upstream PR(§3 A) 병행 |
| N10 | `graph`/`e2e` extra, synthesis backend (O14) | 미사용 시 무관 | 해당 기능 채택 시 별도 검토 |
| N11 | 오탐 redaction 기본 패턴 (O5) | R1-b로 머신-로컬 config에서 무력화 (설정 변경, 소스 수정 아님) | upstream이 기본 패턴 개선 시 재검토 |

## 8. Architecture / Governance / Public Contract 변경 필요 여부 (요구사항 8)

**변경 불필요 — 명시적으로 "변경 없음".**

- LLM Wiki(Candidate #2)는 새 architectural component·runtime·public interface를 추가하지 않는다.
  `.claude/docs/integrations/` 등급의 **로컬 개발 도구**이며, Claude-Mem·Token Optimizer가
  RFC/ADC/ADR 없이 `.claude/docs/integrations/` evidence + Tooling Finalization Review로 채택된 것과 동일 패턴이다.
- Adoption은 **운영적 tooling 결정**으로, 채택 시 `.claude/docs/integrations/`에 채택 문서를 남기고 `README.md` 인덱스를 갱신하는 것으로 족하다.
- Governance 절차가 필요해지는 유일한 경우 = wiki 페이지를 **결정 권위**로 사용하려는 시도인데, §5·B4 규칙이 이를 명시적으로 금지한다.
- 따라서 BASELINE / RFC / ADC / ADR / Public Contract / OmniRoute 변경 **없음**. 이 검토 자체도 Jarvis에 evidence 문서 1개 + README 1행만 추가한다.

## 9. 최종 판정 및 다음 단계 (요구사항 10)

**CONDITIONAL PASS.** Production Adoption 상향 금지.

- **Hold 아님**: 구조적 안전 결함이나 해결 불가 항목이 없다. blocker는 해결 가능성이 실증됐고, 안전 관련 잔여(identity/권한)는 운영 규칙으로 봉쇄 가능하다.
- **Production Adopt 아님**: BLOCKING 게이트 B1–B4가 모두 미충족. 특히 B2(로그인 대화형 스모크)는 이 자동화 세션에서 수행 불가.

**다음 단계 (전부 사람 몫, 추가 개발 없음)**:
1. §3 권고(D: MCP-first Hybrid)에 대한 결정 → B1 충족
2. 로그인된 Claude Code에서 10분 스모크(MCP 등록 + `wiki_query` 1회 + scoped hook 1회 + 토큰 델타) → B2 충족
3. §4 운영 규칙 R1–R4 및 §5 경계·B4 규칙 승인 → B3·B4 충족
4. 위 3개가 끝나면 `.claude/docs/integrations/`에 최종 Adoption 문서를 남기고 Production Adopt로 상향

## Architecture / Public Contract / Governance

**변경 없음.** BASELINE, RFC/ADC/ADR, Governance, Public Contract, OmniRoute, Claude-Mem, Token Optimizer,
Dashboard, `core/`, `hqs/` 미변경. 새 component/runtime/interface 없음. 이 문서는 기존 PoC Evidence의
Adoption 관점 재평가이며 채택 결정이 아니다. LLM Wiki를 Architecture/Governance Source of Truth로 취급하지 않는다.

## Branch / PR / Cleanup

| | |
|---|---|
| branch | `claude/llm-wiki-002-adoption-readiness` @ base `origin/main` `0de386c` |
| diff | `.claude/docs/integrations/llm-wiki-candidate-002-adoption-readiness.md` (신규) + `.claude/docs/README.md` (인덱스 1행) |
| 선행 Evidence | PR #161 / #162 / #163 / #165 — 전부 open, 미merge, 보존 |
| PR | 생성, **merge 안 함** |
| cleanup | 이 검토용 worktree 제거. 실제 `~/.claude` / `~/.omniroute` / `~/.claude-mem` 미접촉 (이 작업은 Evidence 재평가만) |
