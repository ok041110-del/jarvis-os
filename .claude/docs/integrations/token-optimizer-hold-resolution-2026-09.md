# Token Optimizer HOLD Resolution PoC (2026-09)

검증일: 2026-09-08
대상: ooples/token-optimizer-mcp, 이 PoC 시점 upstream HEAD(`ee91e8b`, v6.0.2) 기준
목적: 이전 PoC(HOLD)와 3-way PoC 결과를 실제 최신 upstream 코드 기준으로 재검증하고, Jarvis OS Governance 문서(BASELINE/RFC/ADC/ADR) 전수 검토와의 충돌 가능성을 실측한다.

이 PoC는 별도 브랜치(`claude/token-optimizer-hold-resolution`) + 격리 worktree/HOME + 별도로 clone한 upstream 소스 사본에서 수행했다. 실제 `~/.claude`, `~/.omniroute`, `~/.claude-mem`, jarvis-os `main`, Architecture/Governance/Contract 문서는 전혀 변경하지 않았다 — 대상 문서는 격리 worktree 자체의 체크아웃 사본(원본과 byte-identical)만 읽기 전용으로 사용했다.

## 핵심 결론: 이전 HOLD의 근거가 최신 upstream에서는 재현되지 않는다

이전 PoC/3-way PoC가 관찰한 "대형 Read 강제 차단 → smart_read 강제 유도 → chunk 1 고정 반환" 문제는 **당시 버전(또는 enforce 가정) 기준의 동작이며, 현재 upstream 기본값에서는 발생하지 않는다.** 이는 코드 레벨 분석과 실제 스크립트 재실행 양쪽에서 확인했다.

### 1. 기본 모드가 `enforce`가 아니라 `assist`로 변경됨 (upstream 자체 A/B 측정에 근거)

`plugin/hooks/lib/policy.mjs`의 `mode()`는 `TOKEN_OPTIMIZER_MODE` 미설정 시 **`assist`를 기본값으로 반환**한다. upstream 자신의 실측 데이터(코드 주석에 원문 인용)에 따르면 enforce 모드가 세 가지 지표(비용/점수/턴 수) 모두에서 최악으로 측정되어 기본값에서 제외되었다:

```
THOL 2.1.251, 17 tasks x 3 reps x 3 arms, 153 runs
  control  $21.13  score 0.969  turns 16.2
  assist   $20.48  score 0.971  turns 14.4   <- 세 지표 모두 우세
  enforce  $23.33  score 0.935  turns 17.6   <- 세 지표 모두 열세, 17개 중 12개 태스크 패배
```

`assist` 모드에서 `enforce(reason, deniedBefore)` 함수는 `Read`를 포함한 모든 도구 호출을 **차단·재작성 없이 그대로 통과**시킨다(`if (current === MODE_OFF || current === MODE_ASSIST) allow();`).

### 2. 실측 재현: BASELINE.md(100,240 bytes) Read를 기본 설정으로 실제 hook에 통과시킴

```
$ echo '{"tool_name":"Read","tool_input":{"file_path":".../BASELINE.md"},...}' \
  | node pretooluse-router.mjs
[exit=0, 출력 없음]
```

**차단도 재작성도 없이 그대로 허용됨 — 실측 확인.** 반면 `TOKEN_OPTIMIZER_MODE=enforce`로 명시적으로 전환한 동일 호출은:

```
{"permissionDecision":"deny", "...": "BASELINE.md -- 62 KB. ... Call smart_read with path=\"...\" for the full contents. (Not what you wanted? TOKEN_OPTIMIZER_MODE=off disables enforcement.)"}
```

로 실제 차단됨을 확인했다. 즉 **위험은 여전히 코드에 존재하지만, 오직 사용자가 명시적으로 `TOKEN_OPTIMIZER_MODE=enforce`를 설정했을 때만 발동한다.**

### 3. chunkIndex 페이지네이션 버그는 upstream에서 이미 수정됨

이전 PoC가 관찰한 "100KB 문서 → 17 chunks → 항상 chunk 1만 반환"은 소스코드 주석에 upstream 자신이 명시한 과거 결함으로 남아있다("Advertised in the tool schema from the start, but absent from this interface and never read, so asking for chunk 2 silently returned chunk 1"). 현재는 `options.chunkIndex`가 정상적으로 읽힌다. 실측으로 확인:

```
BASELINE.md smart_read(기본 옵션) → chunked:true, chunkCount:17, chunkIndex:0 반환 (4,056자 / 원본 63,414자)
chunkIndex 0..16 전체를 순차 호출해 각 chunk를 '\n'으로 재조립 → 원본과 byte-for-byte 완전 일치 확인
```

**결론: chunk를 전부(0~16) 순회하면 정보 손실 없이 원문을 완전히 복원할 수 있다.** 남은 실질적 위험은 "버그"가 아니라 "완전 순회를 강제하는 장치가 없다"는 운영상 리스크다 — chunkIndex를 지정하지 않은 단일 호출은 여전히 전체의 약 6%(4,056/63,414자)만 반환한다.

### 4. `.md` 확장자는 별도의 "outline substitution" 메커니즘에서 원천 제외됨

`pretooluse-router.mjs`는 모드와 무관하게(OFF가 아닌 한) Read를 구조적 outline(심볼 목록)으로 몰래 바꿔치기하는 별도 경로(`substitutionFor`/`outlineFor`, `lib/substitute.mjs`)를 갖는다. 이 경로는 `OUTLINEABLE` 확장자 목록(`.ts .tsx .js .jsx .mjs .cjs .py .go .rs .java .rb .php .cs`)에 **`.md`가 없어 governance 문서에는 전혀 적용되지 않는다** — 코드 확인.

### 5. 실제 안전한 우회 수단이 이미 존재함 (allowlist 설정이 아니라 구조적 예외)

`lib/decide.mjs`의 Read 판정 로직에는 명시적 예외가 있다:

```js
if (input.offset != null || input.limit != null) return null;  // 절대 거부하지 않음
```

**`enforce` 모드에서도 `offset`/`limit`를 지정한 paged Read는 차단되지 않음을 실측 확인**(동일 BASELINE.md, enforce 모드, offset/limit 지정 → exit 0, 무개입). 이는 Token Optimizer 자체의 allowlist 설정 기능이 아니라, Claude Code 내장 `Read` 도구의 offset/limit 파라미터를 사용하는 것만으로 항상 안전하게 전체 문서를 완독할 수 있다는 뜻이다. **경로 기반 allowlist(예: `docs/architecture/` 제외) 설정 자체는 코드베이스 어디에도 존재하지 않는다** — `allowlist`/`exclude`/`ignore` 관련 환경변수·설정을 전수 검색했으나 해당 기능 없음.

### 6. 현재 실제 Jarvis 문서 중 truncation 임계값을 넘는 문서는 없음(잠재적 리스크로 남음)

`smart_read`의 `maxSize`(기본 100,000, **문자 수 `.length` 기준**, 바이트 아님) 초과 시 `truncateContent`가 적용되며, `preserveStructure`(기본 true) 하에서는 markdown 프로즈에 `import`/`class`/`function` 같은 코드 구조 패턴이 전혀 매칭되지 않아 **최상단·본문이 전부 버려지고 마지막 50줄만 남는** 것을 코드 레벨로 확인했다(`syntax-utils.ts`). 그러나 실제 문서 전수 스캔 결과:

```
BASELINE.md 63,414자(가장 큼) < maxSize 100,000자 → 현재는 chunking 경로(정보 손실 없음), truncation 아님
ADC-0023(가장 큰 ADC) 42,683자, 그 외 전부 그 이하
```

**현재 어떤 실제 문서도 truncation 임계값을 넘지 않는다.** 다만 BASELINE.md는 ADR 병합마다 계속 성장 중이며(git 이력상 최근 90일간 14회 변경, v1.17→v1.18), 향후 100,000자를 넘으면 이 defect가 실제로 발동할 수 있는 **잠재적(latent) 위험**으로 Open Issue에 남긴다.

### 7. 캐시(반복 읽기) 동작 실측 재확인

```
1차 smart_read: fromCache=false
2차 smart_read(동일 파일): fromCache=true
```

이전 PoC와 동일하게 정상 동작 확인 — 반복 탐색형 워크로드에는 실질적 절감 근거 유지.

### 8. smart_grep은 기본적으로 무제한 결과 반환

`smart-grep.ts`의 `limit` 기본값은 `Infinity`(`options.limit ?? Infinity`)이며, `offset`/`limit`는 opt-in 페이지네이션이다. smart_read와 달리 **기본 설정에서 검색 결과를 임의로 잘라내지 않는다** — governance 문서 전수 grep에는 smart_read보다 안전한 프로파일.

### 9. Egress/보안

- 코드 전체에서 실제 네트워크 호출은 `lib/harvest.mjs`(Stop/PreCompact 시점의 "semantic harvest") 한 곳뿐이며, `TOKEN_OPTIMIZER_API_KEY` 또는 `ANTHROPIC_API_KEY` 환경변수가 있고(`apiKey()`) 로컬 엔드포인트가 아닌 경우에만 `https://api.anthropic.com/v1/messages`로 전송된다. 키가 전혀 없으면 함수 초입에서 즉시 `[]` 반환 — 코드 확인.
- 기본 전송 내용은 "구조화된 다이제스트"(터치한 파일, 편집된 심볼, 실행 커맨드와 종료코드, **사용자 프롬프트 원문**, 어시스턴트의 결론)이며 파일 내용 자체는 보내지 않음 — 단, **사용자 프롬프트 원문이 포함된다는 점은 opt-in 상태에서도 실제 노출 항목으로 명시 확인**. `TOKEN_OPTIMIZER_HARVEST_FULL=true`를 추가로 설정해야 transcript 전체가 전송됨.
- **실제 위험 경로**: `apiKey()`가 `ANTHROPIC_API_KEY`로도 폴백하므로, Token Optimizer를 위해 별도로 설정한 적 없는 `ANTHROPIC_API_KEY`가 다른 목적(OmniRoute 등)으로 이미 쉘 환경에 존재하는 경우 **본인도 모르게 harvest가 활성화되어 프롬프트 다이제스트가 외부로 전송될 수 있다.** 이번 세션의 실제 쉘 환경은 `ANTHROPIC_API_KEY`/`TOKEN_OPTIMIZER_API_KEY` 둘 다 미설정임을 확인했다(현재는 비활성 상태) — 그러나 이는 이 세션 시점의 스냅샷일 뿐, 향후 환경변수 추가 시 재확인 필요(UNVERIFIED for future state).

## UNVERIFIED 항목

- 실제 인증된 Claude Code 라이브 세션을 통한 end-to-end 검증은 수행하지 않음 — 이번 PoC는 실제 hook 스크립트를 합성 payload로 직접 재실행하는 코드 레벨 실측(직접 invocation)으로 수행했다. hook 등록·dispatch 자체가 실제 `claude` 프로세스 안에서 동일하게 동작하는지는 플러그인 설치 메커니즘 자체에 대한 이전 PoC들의 확인에 의존하며, 이번 세션에서 재확인하지 않았다.
- BASELINE.md가 100,000자를 넘어설 때의 실제 truncation 결과는 합성으로 재현하지 않았다(현재 실제 문서로는 임계값 미도달) — 코드 분석 결과에 근거한 예측이며 실측 재현은 아니다.
- `smart_grep`의 governance 문서 검색 시 실제 매칭 품질(관련성, 문맥 절단 여부)은 별도로 실측하지 않았다 — 기본값이 결과 수를 자르지 않는다는 코드 레벨 사실만 확인했다.

## Jarvis OS 적용 시 정확한 운영 범위 (Conditional Adopt 조건)

1. **`TOKEN_OPTIMIZER_MODE`를 절대 `enforce`로 설정하지 않는다.** 기본값(`assist`, 미설정과 동일)을 유지해야 governance 문서 Read가 차단·재작성 없이 통과한다.
2. 코드 탐색형 대형 파일(비-governance, 코드 파일)에 대해서만 `smart_read`/`smart_grep`을 모델이 자발적으로 사용하는 것은 허용 — 이 경로는 assist 모드에서도 계속 이용 가능하며 캐시 이점이 실측됨.
3. 만약 향후 비용 절감을 위해 `enforce` 모드를 고려한다면, 반드시 (a) governance 문서 Read는 `offset`/`limit` paged read를 사용하도록 팀 규칙화하거나 (b) `smart_read` 호출 시 `chunkIndex` 0부터 `chunkCount-1`까지 전부 순회하도록 명시적으로 지시해야 한다 — 단일 호출 결과만으로 문서를 이해했다고 간주해서는 안 된다.
4. `TOKEN_OPTIMIZER_API_KEY`/`ANTHROPIC_API_KEY`를 이 플러그인을 위해 설정하지 않는다. 다른 목적(OmniRoute 등)으로 `ANTHROPIC_API_KEY`를 셸에 export하는 별도 작업을 할 경우, 이 플러그인이 설치되어 있다면 harvest가 의도치 않게 활성화될 수 있음을 인지해야 한다.
5. BASELINE.md 크기(현재 63,414자, maxSize 100,000자)를 주기적으로 확인 — 임계값 근접 시 이 문서 자체의 재평가가 필요하다.

## Architecture/Contract 변경 여부

없음. 대상 문서는 격리 worktree의 읽기 전용 체크아웃 사본만 사용했다.
