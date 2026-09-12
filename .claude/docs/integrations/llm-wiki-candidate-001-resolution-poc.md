# LLM Wiki Candidate #1 (nvk/llm-wiki) Resolution PoC

검증일: 2026-09-08
후보: `github.com/nvk/llm-wiki` @ `7c94c9bf2968f17deb496b285db0afdb610a01d9` (v0.24.4)
목적: 기존 Candidate #1 PoC(Codex 수행, 요약만 존재)에서 제기된 **P0 secret redaction 누락**과
**P1 `session promote` Markdown 들여쓰기 → lint critical**이 실제로 재현되는지, 그리고 **해결 가능한지**를
현재 upstream 소스에서 직접 재현·수정·검증한다. 이 PoC는 Adoption을 전제하지 않으며 Architecture/Governance/
Contract를 변경하지 않는다.

## 격리 및 보호 범위

| 항목 | 값 |
|---|---|
| 샌드박스 루트 | `/private/tmp/llm-wiki-poc-001R/` (HOME·XDG_*·`CLAUDE_CONFIG_DIR`·`PYTHONUSERBASE` 전부 재지정, `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` unset) |
| 후보 clone | `/private/tmp/llm-wiki-poc-001R/src` @ `7c94c9bf` |
| PoC branch | `claude/llm-wiki-poc-001-resolution` (별도 worktree) |
| 미변경 확인(전=후 sha256) | `~/.claude/settings.json` `ea64416c…`, `~/.omniroute/.env` `8827a024…`, `~/.claude/plugins/known_marketplaces.json` `01f36380…`, `~/.claude-mem` 부재 |
| 기존 `claude/llm-wiki-poc-001` 브랜치/worktree | 손대지 않음 |
| 실제 credential 값 | 문서·로그에 미기록 (테스트는 전부 합성 토큰) |

이 브랜치의 Jarvis 변경은 이 evidence 문서와 README 인덱스 1줄뿐이다. 후보 소스 수정은 전부 `/private/tmp` 안에서만 이뤄졌다.

## 1. 민감정보가 저장되는 단계

session capture 파이프라인:

```
hook 이벤트(stdin JSON) → redact() → queue/YYYY-MM-DD.jsonl 의 payload_preview 필드
                                   ↘ state/<harness>/<id>.json
                                   ↘ digests/YYYY/MM/<harness>-<id>.md (체크포인트 시)
       promote → topics/<topic>/raw/notes/<date>-session-*.md  (digest 기반, raw transcript 아님)
```

- 민감정보가 실제로 남는 지점은 **`HUB/.sessions/queue/<date>.jsonl` 의 `payload_preview` 문자열**이다.
  `state/*.json` 은 이벤트 메타데이터(tool_name, ts 등)만 저장하고 payload 본문은 넣지 않는다.
- `digest` 와 `promote` 산출물은 queue/이벤트를 거쳐 만들어지므로, queue 단계에서 redaction이 완전하면
  하위 단계로 secret이 전파되지 않는다(실측: promote note·digest에 secret 미존재).

## 2. redaction 적용 시점 — 저장 이전 (구조는 정상)

`hooks/llm_wiki_session.py` 의 `compact_json(payload)` → `redact(value)` → `redact_scalar()` 는
`payload_preview` 를 **파일에 기록하기 전에** 호출된다(`llm_wiki_session.py:563` 부근). 즉 redaction은
raw/session capture "이전"에 적용된다. 문제는 시점이 아니라 **커버리지**다.

원본 `redact()` 규칙:

| 규칙 | 동작 |
|---|---|
| `SECRET_KEY_RE` 가 dict **키 이름**에 매칭 | 값 전체 → `[REDACTED]` |
| `CONTENT_KEY_RE` 매칭 (`prompt`,`content`,`tool_response`,`stdout` 등) | 값 생략 + `sha256` 다이제스트 |
| 그 외 스칼라 문자열 | `SECRET_VALUE_RE.sub()` 만 적용 |

원본 `SECRET_VALUE_RE` 는 `bearer <12+>`, `sk-<12+>`, `xxx.yyy.zzz`(JWT 3-파트)만 잡는다.
`tool_input` 은 `CONTENT_KEY_RE` 목록에 없으므로 **스칼라 문자열 경로**로만 처리되고,
`tool_input` 하위 키(`command`, `env`, `note` …)가 `SECRET_KEY_RE` 에 안 걸리면
그 문자열 안의 secret은 위 세 형태가 아닌 한 **그대로 통과**한다.

## 3. 설정 변경으로는 불가 — 소스 수정 필요

`DEFAULT_CONFIG` / `MODE_CONFIGS`(off·capture-only·balanced·aggressive) 어디에도
사용자 정의 redaction 패턴 항목이 없다(`extra_patterns`/`custom_pattern`/`redact_pattern` grep 결과 없음).
`privacy: redacted`, `raw_transcripts: false` 는 이미 기본값이며 그 상태에서 누출이 발생한다.
즉 **config로는 해결 불가**, 정규식이 모듈 상수로 하드코딩되어 있어 **소스 수정이 필요**하다.
또한 redaction 코드는 **두 파일에 중복** 존재한다:
`plugins/llm-wiki/hooks/llm_wiki_session.py` 와 `scripts/llm-wiki-session`
(후자가 source of truth, 전자는 `scripts/sync-codex-plugin.sh` 가 생성하는 mirror). 패치는 양쪽에 동일 적용해야 한다.

## 4. Adversarial 재현 (패치 전)

합성 payload를 실제 hook(`llm-wiki-session hook --harness claude --if-enabled`, balanced)로 통과시킨 뒤
`HUB/.sessions/` 전체를 grep한 결과 — **아래 전부 평문 생존**:

| secret 형태 | 패치 전 | 패치 후 |
|---|---|---|
| `export API_KEY=AKIA…` (AWS access key id) | 생존 | `[REDACTED]` |
| `x-api-key: <20자 토큰>` (헤더 값) | 생존 | `[REDACTED]` |
| `echo secret=<pw>` | 생존 | `[REDACTED]` |
| `PGPASSWORD=<pw>` | 생존 | `[REDACTED]` |
| `postgresql://u:<pw>@db` (URL 자격증명) | 생존 | `://u:[REDACTED]@db` |
| `GITHUB_TOKEN=ghp_…` | 생존 | `[REDACTED]` |
| `xoxb-…-…-…` (Slack bot token) | 생존 | `[REDACTED]` |
| `AIzaSy…` (Google API key) | 생존 | `[REDACTED]` |
| `-----BEGIN OPENSSH PRIVATE KEY----- … -----END …-----` | BEGIN 라인 외 본문 생존 | 블록 전체 `[REDACTED]` |
| `Bearer <12+>`, `sk-<12+>`, 정상 JWT 3-파트 | (원본도) `[REDACTED]` | `[REDACTED]` 유지 |
| dict 키 `api_key`, `password` | (원본도) `[REDACTED]` | `[REDACTED]` 유지 |

## 5. 패치 (소스 수정, 두 파일 동일)

`scripts/llm-wiki-session` + `plugins/llm-wiki/hooks/llm_wiki_session.py` 의 `redact_scalar()` 가
`SECRET_VALUE_RE.sub()` 대신 `_redact_secret_values(text)` 헬퍼를 호출하도록 변경. 헬퍼는 순서대로:

1. `SECRET_PEM_RE` — `-----BEGIN…PRIVATE KEY-----` ~ `-----END…-----` 블록 전체 제거 (`re.DOTALL`)
2. 기존 `SECRET_VALUE_RE` — bearer/`sk-`/JWT (prefix 보존 로직 유지)
3. `SECRET_TOKEN_RE` — provider 토큰 형태: `sk-live/test-…`, `sk_/rk_/pk_live_…`, `ghp_/gho_/ghu_/ghs_/ghr_…`,
   `github_pat_…`, `xox[baprs]-…`, `AIza…`, `ya29.…`, `AKIA/ASIA…`, `npm_…`, `eyJ…`(느슨한 JWT)
4. `SECRET_URLCRED_RE` — `scheme://user:PASSWORD@host` 의 password만 제거
5. `SECRET_ASSIGN_RE` — 민감 키 이름(`api_key|secret|token|password|passwd|pwd|access_key|private_key|client_secret|auth` 포함)
   뒤 `=`/`:` 대입에서 **값만** 제거하고 키·구분자는 유지. 값은 (따옴표 문자열) | (숫자 포함 토큰) |
   (16자 이상 긴 토큰) 일 때만 secret으로 간주 — 문서/스키마 산문 오탐 축소.

P1도 같은 파일에서 함께 수정 (아래 8절).

## 6. False positive 검증 (Q4)

패치 후 `redact_scalar()` 에 24개 문자열을 직접 통과:

- **정상 산문 / 프로젝트 지식 12개 — 전부 무변경**:
  `"We should document the api_key parameter and the password reset flow."`,
  `"See ADR-0003 and RFC-0007 for the boundary decision."`,
  `"commit 7c94c9bf2968f17deb496b285db0afdb610a01d9"`,
  `"the password must be rotated every 90 days"`, `"token: the smallest lexical unit"`,
  `"the secret to good caching is invalidation"`, `"timeout=30 retries=5 LOG_LEVEL=debug"`,
  `"export PATH=/usr/local/bin:/usr/bin"`, `"**Token:** the unit the tokenizer emits"`,
  `"- api_key: required (string)"`, `"Investment HQ tracks dividend stock yield and ETF expense ratio."`,
  `"access key rotation is quarterly per policy"` → **오탐 0건**.
- **실제 secret 12개 — 전부 `[REDACTED]`**.
- 초기 패치에서 `"- api_key: required (string)"` 의 `required` 가 오탐된 것을 확인 →
  `SECRET_ASSIGN_RE` 값 조건을 "숫자 포함 또는 16자+ 또는 따옴표"로 좁혀 해소.
- upstream `tests/test-session-capture.sh` fixture(정상 문장 + `super-secret-password` + `sk-…`)도 계속 통과.

한계: `password=purealphaword`(숫자 없고 16자 미만인 순수 알파벳 값)는 `SECRET_ASSIGN_RE` 를 통과할 수 있다.
dict 키가 `password` 인 경우는 `SECRET_KEY_RE` 로 잡히므로 실무 위험은 낮지만, 완전하지 않다.

## 7. 파일 권한 및 저장 범위 (Q5)

- `HUB/.sessions/**` 의 모든 파일 권한: **`0644` (world-readable)**, 디렉터리 `0755`. 패치 전후 동일 —
  이번 패치는 권한을 바꾸지 않는다. Candidate #2에서 확인된 것과 같은 잔여 이슈.
- HUB 기본 해석(`resolve_hub`): `--hub` → `~/.config/llm-wiki/config.json` 의 `hub_path` → 없으면 `~/wiki`.
  즉 저장 위치는 사용자 홈 하위이며 저장소 안에 커밋되지 않는다(로컬·머신 스코프).
- `queue/*.jsonl` 은 append-only, digest/promote note는 `atomic_write`.

## 8. P1 — `session promote` Markdown 들여쓰기 재현·수정

**재현(패치 전)**: `run_promote()` 가 `textwrap.dedent(f"""…{body.strip()}…""")` 를 쓰는데,
f-string 중간에 삽입되는 `body.strip()` 의 2번째 줄부터가 flush-left(들여쓰기 0)라서
`dedent` 의 "공통 선행 공백"이 빈 문자열이 되어 **아무것도 제거되지 않는다**. 결과적으로
템플릿 리터럴의 8칸 소스 들여쓰기가 그대로 남아, 생성된 note의 `---`·`title:` 등 frontmatter가
8칸 들여쓰기된 채 기록된다 → YAML frontmatter로 인식되지 않아 `llm-wiki lint` 가
`unterminated YAML frontmatter` critical을 낸다. (실측: 생성 note 1~17행이 8칸 들여쓰기됨)

**수정**: 템플릿을 header(보간 없는 고정 블록)와 body로 분리. `header = textwrap.dedent(f"""\ … """).strip()`
후 `promoted = header + "\n\n" + body.strip() + "\n"`. 재실행 결과 frontmatter가 0칸,
`---` 로 정상 개폐, lint 통과.

## 9. 회귀 검증 (Q7)

패치(P0+P1) 적용 + `scripts/sync-codex-plugin.sh` 재생성 후:

| 검증 | 결과 |
|---|---|
| upstream 테스트 스위트 (`tests/test-*.sh`, `test-codex-runtime.sh` 제외 = codex desktop 필요) | **14/14 PASS** |
| `test-session-capture.sh` | 19/19 PASS |
| `test-session-concurrency.sh` | 10/10 PASS |
| `test-local-cli-lint.sh` | 42/42 PASS |
| `test-structure.sh` / `test-plugin-validate.sh` | 172 / 135 PASS |
| `test-codex-sync.sh` | 두 파일을 함께 커밋하면 PASS (동일 md5 유지) |
| 격리 `CLAUDE_CONFIG_DIR` 로 `claude plugin marketplace add` + `plugin install wiki@llm-wiki --scope user` | PASS, v0.24.4 **enabled** |
| 라이브 model query / 실제 token·cache 비용 | **UNVERIFIED** — 격리 CLI는 `Not logged in`, 실제 `~/.claude` 를 건드리지 않기로 한 제약상 미검증 |

구조적 발견: **Claude Code 플러그인 패키지(`claude-plugin/`)에는 자동 hook이 없다.** `hooks/hooks.json` 은
Codex mirror(`plugins/llm-wiki/`)에만 생성된다. Claude Code에서 session capture는 `/session` 슬래시 커맨드
또는 `scripts/llm-wiki-session` 직접 실행으로 **명시적 opt-in** 이다(사용자가 직접 `~/.claude/settings.json`
에 hook을 넣지 않는 한 always-on PostToolUse 캡처가 아님). 따라서 Claude 경로에서 P0 노출은
"사용자가 hook 캡처를 켠 경우"에 한정되고, Codex 경로는 상시 노출이었다. 패치는 양쪽 모두를 막는다.

## 10. Open Issues (잔여)

1. **P2 / 권한**: `HUB/.sessions/**` 가 `0644`. 이번 패치 범위 밖. hook 프로세스 `umask` 또는
   생성 직후 `chmod 0600` 필요(Candidate #2와 동일 미해결).
2. **P2 / redaction 완전성**: `SECRET_ASSIGN_RE` 는 숫자 없는 짧은 순수 알파벳 secret 값을 놓칠 수 있다.
   정규식 기반 redaction의 구조적 한계 — 완전한 방어에는 entropy 기반/사전 기반 탐지가 필요.
3. **패치 유지성**: 수정은 두 파일에 중복 적용해야 하고 upstream 업데이트 시 재적용/충돌 가능.
   upstream PR 또는 vendored fork 전략이 필요(코드 반영 안 함).
4. **UNVERIFIED**: 로그인된 Claude Code에서의 라이브 query 품질, 실제 input/output/cache token, cost,
   always-on/On-invoke overhead(기존 요약의 ~1,378 / ~750 tokens는 CLI 추정치).
5. **P1 회귀 가드 부재**: promote 산출물의 frontmatter 유효성을 검사하는 테스트가 upstream에 없음 —
   수정이 회귀해도 스위트가 못 잡는다.

## 11. 최종 판정

**CONDITIONAL PASS (해결 가능 확인).**

- P0(secret redaction 누락): **소스 패치로 해결 가능**. 시점은 원래 정상(저장 이전)이고 커버리지만 부족했으며,
  두 파일에 동일 패치를 적용해 adversarial 12형태 전부 차단, 정상 산문/프로젝트 지식 오탐 0건, 회귀 14/14 PASS.
- P1(promote 들여쓰기 → lint critical): **소스 패치로 해결 가능**. 원인은 `textwrap.dedent` + f-string 보간
  상호작용이며 header/body 분리로 해소, lint 통과.
- 단, (a) 파일 권한 `0644`, (b) 정규식 redaction의 구조적 한계, (c) 패치 유지성(중복 파일·upstream 의존),
  (d) 라이브 token/cost/query UNVERIFIED 가 남는다. 이 PoC는 후보 소스를 Jarvis에 반영하지 않으며
  Adoption으로 상향하지 않는다.

## 12. Candidate #2 비교

| 축 | Candidate #1 (nvk) | Candidate #2 (Pratiyush) |
|---|---|---|
| Claude 플러그인 설치 | `marketplace add` + `install` 정상, enabled | 스키마 오류 다수, 3-파일 vendored 패치 필요 |
| 자동 hook | Codex만 상시, Claude는 opt-in | SessionStart hook `ModuleNotFoundError` (패치로 해결) |
| P0 redaction | 시점 정상, 커버리지 부족 → 소스 패치로 해결 | config 패턴 지원 O, 단 prose 오탐(`token overhead`) 발생 |
| P1 | promote 들여쓰기 → lint critical → 패치로 해결 | 해당 없음 (Python 변환기) |
| 파일 권한 | `0644` 잔존 | hook 경로만 `0600` 수정, slash/manual 잔존 |
| 판정 | CONDITIONAL PASS (해결 가능) | CONDITIONAL PASS (Adoption 미상향) |

두 후보 모두 P0/P1은 소스/패치로 해결 가능하나, 공통적으로 (1) 파일 권한, (2) 정규식 redaction 한계,
(3) 패치의 upstream 의존성, (4) 로그인 환경 실측 부재가 Adoption 전 해소 대상이다.

## 13. Architecture / Public Contract / Governance

**변경 없음.** Jarvis baseline, RFC/ADC/ADR, Governance, public Contract, OmniRoute, Claude-Mem,
Token Optimizer, Dashboard 미수정. 새 component/runtime/interface 추가 없음.
LLM Wiki는 derived recall layer이며 Architecture/Governance Source of Truth(RFC/ADC/ADR/BASELINE)가 아니다.

## 14. Cleanup

`/private/tmp/llm-wiki-poc-001R/` 및 격리 `CLAUDE_CONFIG_DIR` 제거. PoC worktree 제거.
실제 환경 전=후 sha256 재확인: `~/.claude/settings.json` `ea64416c…`,
`~/.omniroute/.env` `8827a024…`, `~/.claude/plugins/known_marketplaces.json` `01f36380…`, `~/.claude-mem` 부재 — 모두 불변.
