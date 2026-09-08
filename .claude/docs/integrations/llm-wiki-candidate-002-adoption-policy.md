# LLM Wiki Candidate #2 — Adoption Policy & Live Smoke 준비

작성일: 2026-09-08
대상: `Pratiyush/llm-wiki` v1.3.82 (@ `b1088890`) — 현재 Preferred Candidate
근거 Evidence: PR [#161](https://github.com/ok041110-del/jarvis-os/pull/161) · [#162](https://github.com/ok041110-del/jarvis-os/pull/162) · [#163](https://github.com/ok041110-del/jarvis-os/pull/163) · [#165](https://github.com/ok041110-del/jarvis-os/pull/165) · [#166](https://github.com/ok041110-del/jarvis-os/pull/166) (전부 open, 미merge)

이 문서는 Candidate #2의 **Adoption Policy 초안을 확정 형태로 정리**하고, Production Adoption 직전에
**사용자가 로그인된 Claude Code에서 직접 수행할 Live Smoke 절차**를 준비한다.
정책 텍스트는 이 문서로 내부 정합성까지 완성되나, **정책의 발효(ratify)와 Production Adoption은
사용자의 Live Smoke PASS 이후에만** 다음 단계로 넘어간다. `.claude/docs/` 규정대로 실행환경 검증
evidence이며 RFC/ADC/ADR/BASELINE의 source of truth가 아니다.

## 0. 현재 상태 (요구사항 1)

| 항목 | 값 |
|---|---|
| Preferred Candidate | `Pratiyush/llm-wiki` |
| 상태 | **CONDITIONAL PASS** |
| Production Adoption | **아직 하지 않는다** — 이 문서로 상향하지 않음 |
| Fallback | `nvk/llm-wiki` (무패치 shipped plugin이 필수이고 session-capture 계층 비활성 조건, PR #165 §최종판단) |

---

## 1. 유지 전략 — MCP-first Hybrid 확정 검토 (요구사항 2)

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
| M2 | SessionStart hook 한 줄 (`… python3 -m llmwiki sync …`, scoped) | **Jarvis 측 설정** (프로젝트 `.claude/settings.json`) — upstream 파일 아님 | 영향 없음 |
| M3 | `examples/sessions_config.json` redaction 튜닝 (`include_projects` + identity `extra_patterns`) | **머신-로컬 설정 데이터** (코드 패치 아님, 커밋 금지 — R1) | 재적용 필요. 스니펫을 이 문서 §5에 고정. 미적용 시 key-shaped provider redaction은 그대로 동작, identity extra_patterns만 소실 → R1이 커버 |
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

**현재 Evidence 상태**: SessionStart hook을 실제 `~/.claude` HOME에서 무-scope 실행 시 **claude_code 79 + codex_cli 53 = 129 세션 전량 변환** (PR #163 실측).

**운영 규칙 (명시)**:
- **R3-a**: SessionStart hook 및 모든 수동 sync는 `examples/sessions_config.json`에 **`include_projects: ["jarvis-os"]`** 를 설정하여 scoping한다.
- **R3-b**: **무-scope ingest 금지.** `include_projects` 미설정 상태 또는 격리 HOME 미병행 상태에서의
  `python3 -m llmwiki sync` 실행을 금지한다.
- **R3-c**: 최초 1회 백필은 scoped 상태에서 수행하고, 결과 세션 수를 jarvis-os 세션 수 기대치와 대조 확인한다
  (100건 이상이면 scope leak으로 간주하고 중단).
- **R3-d**: 채택 문서에 정확한 `include_projects` 값과 hook 커맨드 전문을 명시한다 (§5 스니펫).

### R4 — Truncation (93% 축소) (요구사항 6)

**현재 Evidence 상태**: 결정론 변환이 `tool_result_chars: 500` 등으로 tool 출력을 공격적으로 truncate → 대형 governance 문서 Read 원문은 `raw/`에 **들어오지 않음** (PR #161). 사실 링크는 유지되나 evidence 원문은 아님.

**운영 규칙**:
- **R4-a**: Evidence 원문의 유일 보관처는 **git + `.claude/docs/integrations/`** 다. wiki `raw/`는 사실 링크·요약이며 evidence 원문이 아니다.
- **R4-b**: wiki에서 governance 문서를 인용할 때는 항상 원본 경로/커밋을 병기한다 (`sources:` 규약이 이미 강제).
- **운영상 허용 범위**: 93% 축소는 **설계 특성으로 허용**한다. 단 wiki를 evidence 아카이브로 사용하지 않는다는 것이 전제다.

### R5 — Wiki 비권위 (Non-authoritative) 규칙 (요구사항 3·4)

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
  "include_projects": ["jarvis-os"],            // R3-a: scoping. 이 키 없이 sync 금지 (R3-b)
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
  "command": "umask 077; cd /Users/<you>/tools/llm-wiki && (python3 -m llmwiki sync > \"${TMPDIR:-/tmp}/llmwiki-sync.log\" 2>&1 &) ; exit 0"
} ] } ] } }
```

- `umask 077` → R2-b. `( … &) ; exit 0` → 완전 백그라운드·non-blocking·stdout 없음(자동 주입 0).
- `include_projects` scoping은 §5.2가 담당 → R3-a.

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
| S3 | scoped sync (`/wiki-sync` 대체) | 터미널: `cd ~/tools/llm-wiki && umask 077 && python3 -m llmwiki sync` | `N converted, 0 errors`, **N이 jarvis-os 세션 수 기대치와 근사** | **N ≥ 100** (scope leak → 중단, §5.2 `include_projects` 재확인) |
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
| 유지 전략 | **MCP-first Hybrid로 확정 검토 완료.** full plugin 3파일 patch 의존 = **제거 가능(코드/매니페스트 패치 0건)**. 남는 것은 Jarvis 측 설정(M1·M2) + 머신-로컬 설정 데이터(M3) + 버전 pin(M4) |
| 계층 경계 | **고정** — SoT(RFC/ADC/ADR/BASELINE/Evidence) / Claude-Mem(Session·Operational, push) / LLM Wiki(Project Knowledge·Derived Recall, pull·비권위) |
| 운영 규칙 | **R1–R5 초안 완성.** 각 항목의 "운영상 허용 범위"를 Evidence 범위 내에서 명시(초과 주장 없음) |
| `include_projects=jarvis-os` scoping / 무-scope 금지 | **명시 완료** (R3-a·R3-b) |
| Architecture/Public Contract | **변경 없음 (확인)** |
| 정책 발효(ratify) | **사용자 승인 대기.** 이 문서는 정책 텍스트를 확정 형태로 완성했으나 스스로 발효하지 않는다 |

### 8.2 Live Smoke 준비 상태

| 항목 | 상태 |
|---|---|
| 체크리스트 | **작성 완료** (§6, 11단계 + 결과표 + 판정 규칙, 약 10분) |
| 사전 스니펫 | **작성 완료** (§5, checkout/config/MCP/hook) |
| 실행 주체 | **사용자** — 로그인된 대화형 Claude Code 필요 (자동화 세션 구조적 불가) |
| B2 게이트 | 체크리스트로 닫을 수 있도록 준비됨. **아직 미수행** |

### 8.3 Production Adoption

**진행하지 않는다.** PR #166이 정의한 BLOCKING 게이트 상태:

| 게이트 | 상태 |
|---|---|
| B1 패치 유지 전략 결정 + 소유자 | 이 문서가 **MCP-first Hybrid 기준안 + 근거** 제시 → **사용자 승인 시 충족** |
| B2 로그인 대화형 Live Smoke (사용자) | §6 체크리스트 준비됨 → **사용자 수행 + PASS 시 충족** |
| B3 운영 규칙 R1–R5 승인 | 이 문서가 초안 완성 → **사용자 승인 시 충족** |
| B4 wiki 비권위 규칙 고정 | R5 = 초안 완성 → **사용자 승인 시 충족** |

**다음 단계**: 사용자가 (1) 이 정책(§1·§3·§8.1)을 승인하고 (2) §6 Live Smoke를 직접 수행해 B2가 PASS하면,
`.claude/docs/integrations/llm-wiki-candidate-002-adoption.md`를 작성하고 Production Adopt로 상향한다.
**그 전까지 Candidate #2 = CONDITIONAL PASS 유지.**

---

## Branch / PR / Cleanup

| | |
|---|---|
| branch | `claude/llm-wiki-002-adoption-policy` @ base `origin/main` `0de386c` |
| diff | `.claude/docs/integrations/llm-wiki-candidate-002-adoption-policy.md` (신규) + `.claude/docs/README.md` (인덱스 1행) |
| 선행 Evidence | PR #161 / #162 / #163 / #165 / #166 — 전부 open, 미merge, 보존 |
| PR | 생성, **merge 안 함** |
| cleanup | 이 정책 작성용 worktree 제거. 실제 `~/.claude` / `~/.omniroute` / `~/.claude-mem` 미접촉 — 이 작업은 정책 문서 작성만, 어떤 hook/MCP/sync도 실행하지 않음 |
