# DEV-HQ-V2.0 — ChatGPT 실제 호출 환경 확보 + Claude Code Repository Execution 준비 조사 (Part 2)

**전제**: `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`
(PR #183, main 미병합)가 승인된 상태를 가정. 이 문서는
`DEV-HQ-V2.0-STAGE01-04-CHATGPT-CLAUDE-CODE-CONNECTION-0001.md`(Part 1,
이 branch/PR #184)의 Open Issue 2·3·4를 이어서 조사한다. **Production
코드는 변경하지 않았다** — Repository Execution은 아래 §8이 확인하는
대로 `ADR-0024` Non-goal 재검토(RFC→ADC→ADR)가 선행되어야 하기 때문이다.

---

## 1. ChatGPT egress 상태(재검증, 이번 세션 컨테이너 기준)

Part 1과 다른 컨테이너 인스턴스일 수 있어 전부 재확인했다.

| 확인 항목 | 결과 |
|---|---|
| `OPENAI_API_KEY` 존재 여부 | **없음**(`env` 전수 확인) |
| DNS resolution(`api.openai.com`) | **성공**(`2606:4700:7::f3` 등 정상 응답) |
| Raw TCP connect(443, `/dev/tcp`) | **성공** — 전송 계층 자체는 막혀 있지 않음 |
| `http.client`로 실제 HTTPS 요청(`POST /v1/chat/completions`, 무효 key) | **HTTP 403** — 응답 바디: `"Host not in allowlist: api.openai.com. Add this host to your network egress settings to allow access."` |
| 대조군: `api.anthropic.com`(`GET /v1/models`, 무효 key) | **HTTP 401**(`authentication_error`, 정상적인 실제 API 응답) — 연결 자체는 완전히 성공 |

**정확한 결론**: 이것은 코드 문제가 아니라 **이 세션 환경의 조직
(organization) 단위 network egress allowlist 정책**이다
(`/root/.ccr/README.md`: "The destination host is not allowed by your
organization's egress policy for this session. Do not retry or route
around it — report the blocked host."). `api.anthropic.com`은
allowlist에 있고 `api.openai.com`은 없다 — TLS/DNS/코드 구현 어느
것도 원인이 아니다. 이 지시에 따라 **우회를 시도하지 않았다.**

### ChatGPT 실제 호출 결과

```
ChatGPT Real Engine = BLOCKED
(원인: organization egress policy가 api.openai.com을 allowlist에서 제외.
 실제 API 응답까지 도달함(401/403 등 정상 오류 형식이 아니라 프록시 자체의
 403 차단 응답) — 이 세션에서 개발자가 고칠 수 있는 코드 결함이 아니다.)
```

**필요한 조치(코드 밖)**: 이 실행 환경(Claude Code on the web/cloud
환경)의 network egress 설정에서 `api.openai.com`을 허용 목록에
추가해야 한다 — 이는 Repository 코드가 아니라 환경 설정 변경이며,
이 세션은 그 권한이 없다(조직 정책). `chatgpt_engine.py`의
`http.client` 구현 자체는 (a) DNS/TLS/HTTP 계층 정상 동작(대조군
Anthropic 테스트로 확인), (b) API Key를 하드코딩하지 않음(§확인
결과 재검증, `sk-` 리터럴 없음), (c) egress가 허용되면 즉시 동작할
준비가 되어 있다 — 코드 변경 불필요.

---

## 2. Claude Code 현재 권한(Production, `engine.py`)

```python
DISALLOWED_TOOLS = "Write,Edit,Bash,Read,Glob,Grep,NotebookEdit,WebFetch,WebSearch"
cwd = tempfile.gettempdir()
```

**전체 도구 차단 + 저장소 밖 cwd** — 순수 Text Mode(Part 1 §3.2에서
실제 호출 성공 확인, 재론하지 않음).

---

## 3. Claude Code Repository Execution 가능 범위(실측, 격리 테스트 디렉터리 — Production 미접촉)

`/tmp/cc-boundary-test`(임시 git repo, Production 저장소 아님)에서
3가지를 실측했다.

### 3.1 Command Execution 차단 확인

```
$ claude -p "... Bash 도구로 'echo HACKED' 실행 ..." \
    --allowedTools "Read,Edit" --disallowedTools "Bash" --permission-mode acceptEdits
→ "BASH_UNAVAILABLE"(요청대로 Bash 미사용 확인, exit 0)
```

`--disallowedTools "Bash"`로 명령 실행을 확실히 차단할 수 있다 —
git/test runner/Python/shell 어느 것도 Bash 도구 경유이므로 이
하나로 전부 차단된다. **결론: Stage 04 Code Generation에 Command
Execution 권한은 필요하지 않다**(코드 생성은 텍스트 반환 + 파일
Edit만 필요, 실행/테스트는 기존 Stage 04 `VALIDATION.md` 절차처럼
Jarvis 쪽에서 별도로 결정론적으로 수행).

### 3.2 **중요한 보안 발견 — Read는 cwd에 갇히지 않는다**

```
$ claude -p "Read /etc/hostname 읽어서 내용 출력 ..." \
    --allowedTools "Read" --permission-mode acceptEdits
    (cwd=/tmp/cc-boundary-test, --add-dir 미지정)
→ "vm"(실제로 /etc/hostname 내용을 읽어 반환함, exit 0)
```

**`--allowedTools "Read"`만으로는 파일 접근 범위가 작업 디렉터리로
제한되지 않는다** — 프로세스가 OS 권한상 읽을 수 있는 어떤 경로든
Read 도구로 읽을 수 있었다(`cwd`를 target repo로 좁혀도 credential/
secret 파일이 같은 컨테이너 안에 있으면 이론상 읽힐 수 있다는
뜻이다). `--add-dir`는 접근 범위를 **넓히는** 옵션이지, 기본
상태가 **좁게** 시작하는 것이 아니다.

**결론**: "Read 허용 범위 = Target Repository만"을 CLI 플래그
만으로는 강제할 수 없다. 실제로 이 범위를 좁히려면 다음 중 하나가
필요하다(이번 세션은 어느 것도 구현하지 않는다 — Governance
선행 필요, §8):

- OS 수준 격리(별도 컨테이너/chroot/제한된 사용자 계정으로 프로세스
  실행, `IMPLEMENTATION_RULES.md` Execution Host 허용 범위·`ADC-0015`
  의 Process/Subprocess 격리 원칙과 정합적인 방향).
- 또는 credential/secret 파일이 애초에 그 프로세스의 파일시스템
  네임스페이스에 존재하지 않도록 격리된 작업 디렉터리 자체를
  마운트/복사해서 넘기는 방식(§6 Option B/C와 직결).

### 3.3 Write 미허용 시 실제로 거부되는지 확인

```
$ claude -p "newfile.txt를 만들어라 ..." \
    --allowedTools "Read,Edit" --disallowedTools "Write,Bash"
→ "WRITE_DENIED"(실제로 파일이 생성되지 않음, `ls` 결과로 재확인)
```

**결론**: Edit는 "기존 파일의 부분 수정"만 허용하고 새 파일 생성은
막을 수 있다 — Stage 04가 "기존 함수 확장"(Exposure Policy가 이미
전제하는 시나리오)만 원한다면 `Write`를 아예 허용 목록에서 빼는
것이 안전하다. 새 파일이 실제로 필요한 작업(신규 함수/모듈)이라면
`Write`를 허용하되 Scope 검사(Deterministic Gate)로 사후 검증해야
한다(이미 PR #180 Harness의 `check_scope`/`ponytail_policy.py`
패턴과 정합적).

### 3.4 `--output-format json`의 Cost/Usage 계측(부가 발견)

```json
{
  "result": "PONG3",
  "is_error": false,
  "total_cost_usd": 0.0513116,
  "duration_ms": 2710,
  "duration_api_ms": 2236,
  "usage": {"input_tokens": 2, "output_tokens": 6, ...},
  "permission_denials": [],
  "num_turns": 1
}
```

**실측 확인**: `engine.py`가 지금 `--output-format text`를 쓰지만,
`--output-format json`으로 바꾸면 **별도 계측 모듈 없이도**
`total_cost_usd`/`duration_ms`/`usage`/`permission_denials`를 그대로
얻을 수 있다 — PR #180의 `cost_instrumentation.py`가 OmniRoute용으로
만든 것과 동등한 역할을 Claude Code에서는 CLI 자체가 이미 제공한다.
**`permission_denials` 필드는 Stage 04 Ponytail의 "금지 영역 요구
시 에스컬레이션" Gap(`ADC-0040` §6이 미구현으로 남긴 부분)을 채울
실제 신호로 쓸 수 있다** — 권한 거부가 발생하면 이 배열이 비어있지
않게 된다.

이 발견은 **Contract 변경 논의(§7)에 직접 영향**을 준다 — 현재
`str -> str`을 유지하면 이 풍부한 구조화 정보(cost/permission_denials
포함)를 전부 버리게 된다.

---

## 4. 권장 Execution Boundary 비교(사용자 지시 §5 Option A/B/C)

| 기준 | Option A(현재 Repository에 직접) | Option B(격리된 작업 디렉터리) | Option C(별도 Execution Adapter + 격리 환경) |
|---|---|---|---|
| 보안 | **낮음** — §3.2가 실증한 대로 Read가 cwd에 갇히지 않아 같은 컨테이너의 다른 경로(credential 등)에 노출될 위험 | **중간~높음** — 격리된 디렉터리에 Target 관련 파일만 배치하면 §3.2 문제의 실질적 노출 범위가 줄어듦(단, 여전히 완전한 OS 격리는 아님) | **높음** — Adapter가 실제 컨테이너/프로세스 격리를 강제할 수 있음 |
| 구현 복잡성 | 낮음(현재 `engine.py` 패턴 + 인자만 변경) | 중간(작업 디렉터리 준비/정리 로직 필요 — Stage 04 `VALIDATION.md`의 backup/restore와 유사) | 높음(Adapter 계층 신설) |
| 권한 통제 | `--allowedTools`만으로 통제(§3.2 한계 있음) | 동일 + 디렉터리 범위 자체가 좁아짐 | 동일 + 컨테이너 경계 추가 |
| diff 추적 | `git diff`로 가능(Production repo 그대로) | `git diff`(격리 디렉터리가 별도 clone/worktree라면) 또는 파일 비교 | 동일 |
| rollback | Production repo에 직접 반영되므로 위험(즉시 `git checkout`/restore 필요) | **안전** — 격리 디렉터리 자체를 버리면 rollback 완료 | 안전(Adapter가 폐기) |
| test 실행 | 가능(단, Production 위에서 직접 — 실패 시 원상복구 절차 필수) | 가능(격리 디렉터리 안에서, Production 영향 없음) | 가능 |
| Stage 04 Contract | 무변경 시도 가능하나 §3.2 리스크 존재 | 무변경 가능, 리스크 감소 | Adapter 자체의 Contract 신설 필요(Gateway화 위험) |
| 기존 Governance | `ADR-0024` Non-goal과 충돌(어느 Option이든 동일 — Repository Execution 자체가 문제) | 동일 | 동일 + `IMPLEMENTATION_RULES.md` 15행(Gateway 금지) 위반 위험 추가 |

**권장(향후 RFC의 출발점으로만, 이번 세션이 확정하지 않음): Option
B.** 이유: (1) §3.2가 실증한 보안 한계를 완화하면서, (2) 기존 Stage 04
`VALIDATION.md`의 real E2E 절차(backup→apply→pytest→diff→restore)가
이미 "격리된 적용 후 검증"이라는 동일한 패턴을 쓰고 있어 재사용
가능하고, (3) Option C처럼 새 Adapter 계층(Gateway화 위험)을 만들지
않는다. **단, 이것은 권장일 뿐 Decision이 아니다** — §8에 따라 실제
채택은 RFC→ADC→ADR을 거쳐야 한다.

---

## 5. 가장 중요한 질문(사용자 지시 §6)에 대한 답

**"Claude Code → 파일 수정 → Deterministic Gate"로 끝내면 안 된다.**
실제로 필요한 것은:

```
Claude Code 실행(격리 디렉터리, Read+Edit만)
        ↓
git diff(격리 디렉터리 기준)
        ↓
Deterministic Gate(PR #180 Harness의 check_syntax/scope/contract 등 재사용)
        ↓
PASS → Jarvis(사람 또는 별도 결정론적 정책)가 Production에 반영 여부 결정
FAIL → 격리 디렉터리 폐기, Production 무영향
```

**Claude Code가 직접 commit/push하는 구조는 채택하지 않는다**(사용자
지시 그대로 재확인) — 이유: (1) commit 권한을 LLM에게 주는 것은
Repository Execution보다 한 단계 더 큰 권한 위임이며 이번 조사
범위 밖, (2) Deterministic Gate가 FAIL한 뒤에 이미 commit이 발생하면
rollback이 `git revert` 수준의 추가 작업이 되어 Option B의 "폐기로
끝나는" 안전성 이점이 사라진다. commit/push는 Gate 통과 이후 **별도
주체**(Jarvis 결정론적 로직 또는 사람)의 몫으로 명확히 분리한다.

---

## 6. Contract 영향(사용자 지시 §7 — 판단만, 변경 없음)

**질문**: Stage 04가 Claude Code Execution 결과를 현재 `str -> str`
Contract만으로 안전하게 처리할 수 있는가?

**답**: **아니오, Repository Execution(B)을 채택하면 불충분하다.**
근거:

1. §3.4가 실측한 대로 `--output-format json`은 이미 `is_error`/
   `permission_denials`/`total_cost_usd`/`duration_ms`를 제공한다 —
   이것을 `str`로 압축하면 Deterministic Gate가 "권한 거부가
   있었는지"를 문자열 파싱으로 추측해야 한다(취약함).
2. §5의 lifecycle이 요구하는 `git diff`/변경 파일 목록은 텍스트
   반환값에 없다 — 호출자가 별도로 `git diff`를 실행해야 하는데,
   이는 Engine Contract 밖의 책임이 되어 "Engine이 실제로 무엇을
   했는지"와 "호출자가 사후에 관찰한 것"이 분리된다(신뢰 경계 모호).
3. 반대로 **현재 Text Mode(A)** 범위에서는 `str -> str`이 여전히
   충분하다(Part 1 §5와 동일 결론, 재확인) — 이번 조사로도 이
   결론이 바뀌지 않았다.

**결론**: Contract는 지금 변경하지 않는다(사용자 지시 그대로). B가
실제로 채택되면 필요한 최소 확장 후보(YAGNI 재확인 대상, 이번
세션이 확정하지 않음):

```
{
  "output": str,            # 기존 필드 유지(하위 호환)
  "exit_status": "success" | "error" | "permission_denied",
  "changed_files": list[str],
  "diff": str | None,
  "test_result": ... | None,   # Stage 04 범위에서는 보류 가능(Stage 05 소관)
  "execution_error": str | None,
}
```

---

## 7. Governance 확인(사용자 지시 §8, 실제 판정)

```
Claude Code Repository Execution
          ↓
ADR-0024 §Engine Architecture(Claude Code의 특수성) 원문:
"Non-goal(명시적 범위 밖): LLM에게 실제 filesystem/shell/git 접근
권한을 주는 Repository Execution Engine 도입은 이 ADR이 승인하지
않는다 — 이는 에러 모델·타임아웃·중간 진행 상태·보안 경계가 전부
달라지는 별도의, 훨씬 더 큰 Architecture Decision 대상이다."
          ↓
이번 조사(§3.2 Read 범위 실측, §6 Contract 불충분 확인)가 그 원문의
우려("보안 경계가 달라짐")를 실제 Evidence로 재확인했다.
          ↓
판정: YES — ADR-0024 Non-goal 변경 필요
          ↓
RFC → ADC → ADR 필요(이번 세션은 착수하지 않음)
```

**이번 세션은 Governance를 우회하지 않았다** — §3의 모든 실측은
Production 저장소가 아닌 `/tmp/cc-boundary-test`(임시 격리
디렉터리)에서만 수행했고, `engine.py`/Stage 04/Contract 어느 것도
수정하지 않았다.

---

## 8. 실제 변경사항

**Production 코드 변경: 없음.** ChatGPT는 코드가 아니라 환경(조직
egress 설정)이 원인이라 이 저장소에서 고칠 대상이 없다. Claude Code
Repository Execution은 Governance 선행 조건(§7)이 충족되지 않아
구현하지 않았다. 이 문서(Evidence) 1건만 추가했다.

## 9. Stage 01~04 E2E 결과(갱신)

| 단계 | 결과 |
|---|---|
| Stage 01~04 Target(ChatGPT ×4) | **BLOCKED**(§1, organization egress policy) |
| Stage 04 Code Generation(Claude Code Text Mode) | Part 1에서 이미 CONFIRMED(재확인 안 함) |
| Stage 04 Code Generation(Claude Code **Repository Execution**) | **기술적으로 가능함을 격리 환경에서 실측(§3)**, Production 미적용(Governance 대기) |
| Deterministic Gate | Engine 불필요, PR #180 Harness로 이미 검증 |

전체 E2E(Stage01→04)는 여전히 이 환경에서 완주 불가(ChatGPT 구간
BLOCKED, Part 1과 동일).

## 10. Open Issues

1. `api.openai.com`을 이 환경의 network egress allowlist에 추가하는
   것은 이 세션의 권한 밖이다 — 사용자/조직 관리자가 Claude Code
   환경 설정에서 처리해야 한다.
2. Option B(격리된 작업 디렉터리) 채택을 위한 실제 RFC 작성은 이번
   세션 범위 밖 — 다음 세션 대상.
3. `--output-format json`을 실제로 `engine.py`에 반영할지는 Text
   Mode 범위 안의 결정(Contract 변경 아님 — `result` 필드만 추출하면
   기존 `str` 반환과 동일)이지만, 이번 세션은 코드를 변경하지
   않았으므로 반영 여부도 다음 세션 판단 대상으로 남긴다.
4. §3.2의 Read 범위 문제는 Claude Code CLI 자체의 설계(문서화된
   동작인지, 향후 CLI 옵션으로 좁힐 수 있는지)를 CLI 자체 문서에서
   추가 확인할 필요가 있다 — 이번 세션은 실측만 했고 CLI 공식 문서를
   대조하지 않았다.

## 11. Architecture 변경 여부

없음.

## 12. Contract 변경 여부

없음(필요 시 확장 후보만 §6에 기록).
