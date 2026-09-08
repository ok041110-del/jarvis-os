# Jarvis OS Tooling Finalization Review (2026-09)

검증일: 2026-09-08
범위: Claude-Mem, Token Optimizer(ooples/token-optimizer-mcp), Context Handoff(who96/claude-code-context-handoff)

이 문서는 별도 PoC 세션 5회(격리된 `claude/*` 브랜치 + worktree/HOME, 실제 Architecture/Governance/Contract/OmniRoute/Dashboard/main 및 실제 `~/.claude`/`~/.omniroute`/`~/.claude-mem` 미변경)에서 수집한 Evidence를 종합해 세 도구의 최종 채택 상태를 확정한다. 이번 리뷰 자체는 새 라이브 테스트를 수행하지 않고, 기존 Evidence의 재검토·재종합만 수행했다.

## 판정 기준 (요구사항 8)

기능 성공 여부만이 아니라 다음 5개 축으로 판단한다: **token efficiency / reliability / context quality / security / operational complexity**.

## 종합 판정표

| 도구 | 판정 | 근거 Evidence | 남은 검증 항목 |
|---|---|---|---|
| **Claude-Mem** | **Conditional Adopt** (유지, 조건부) | 로컬 전용 설치·hook 등록 실제 검증(설치일 2026-08-08, `integrations/claude-mem.md`). 3-way PoC에서 다른 두 도구와 hook 충돌 없이 병행 동작 확인(additionalContext concatenation 실측). 실제 fresh-startup(`SessionStart:startup`)에서 메모리 주입 구조 실측 확인. 3회 `/clear` 라이브 재검증에서 매 라운드 내적으로 일관된 project-grounded 복원 답변 생성(narrative 연속성 확보). | (1) `user_prompts` 테이블이 원문 프롬프트를 **평문·무기한·필터링 없이** 저장 — 자격증명/민감정보를 프롬프트에 직접 입력한 경우 보존 위험, 완화책 UNVERIFIED. (2) Claude-Mem 자체의 순수 token/context overhead는 3-way 측정에서 통계적으로 불충분해 **UNVERIFIED**. (3) "지시받은 특정 사실의 verbatim 보존" 정확도는 검증되지 않음 — 관찰된 것은 narrative 재구성이지 값 그대로의 재현이 아님, **UNVERIFIED**. |
| **Token Optimizer** | **Conditional Adopt** (2026-09-08 HOLD Resolution PoC로 갱신 — [`integrations/token-optimizer-hold-resolution-2026-09.md`](token-optimizer-hold-resolution-2026-09.md)) | 후속 PoC에서 upstream 최신 코드(v6.0.2)를 실제 재빌드·직접 실행해 재검증한 결과, 이전 HOLD의 근거였던 "대형 Read 강제 차단→chunk 1 고정 반환"은 (a) upstream 기본 모드가 `enforce`에서 `assist`로 바뀌어 기본값에서는 Read가 전혀 차단·재작성되지 않고(BASELINE.md 100,240 bytes Read를 실제 hook에 통과시켜 무개입 확인), (b) chunkIndex 페이지네이션 버그도 upstream에서 이미 수정되어 17개 chunk를 전부 순회·재조립하면 원본과 byte-for-byte 동일함을 실측 확인, (c) `offset`/`limit` paged Read는 `enforce` 모드에서도 차단되지 않는 구조적 안전 경로임을 실측 확인. | (a) `TOKEN_OPTIMIZER_MODE=enforce`로 명시 전환 시에는 이 위험이 그대로 재현됨(실측 확인) — 절대 enforce로 전환하지 않는다는 운영 규칙 준수 여부는 사람이 지켜야 하는 조건이라 지속 확인 필요. (b) BASELINE.md가 성장해 100,000자(현재 63,414자) 임계값을 넘으면 markdown 대상 truncation 결함(코드로 확인, 실측 재현은 아님)이 발동할 수 있음 — 주기적 크기 점검 필요. (c) harvest egress 기능이 `ANTHROPIC_API_KEY` 사전 존재만으로 의도치 않게 켜질 수 있음(코드 확인, 이번 세션 환경에서는 미설정 확인) — 향후 환경변수 변경 시 재확인 필요. |
| **Context Handoff (-lite 포함)** | **Exclude** (최종 제외, 확정) | 정식 구현 라이브 재현 테스트 3/3 전부 실패(5필드 추출 0건, `~/.claude/handoff-lite/` 생성 안 됨) — 이전 PoC의 FAIL 결과 그대로 확정. 원인은 자유 서술형 모델 출력을 단일 라인 정규식으로 파싱하는 구현 방식 자체의 결함이며, hook 등록/scope/guard 설계는 정상 동작이 확인됨. | 없음 — 요구사항에 따라 재구현하지 않고 이 판정으로 확정. 향후 재도전 시 구조화 출력 기반 재설계가 필요하다는 점만 기록으로 남긴다(과거 세션 Observation 15). |

## 항목별 상세

### 4. Claude-Mem — 유지 후보 재평가

- **Reliability / context quality**: 3-way PoC와 fresh-startup 검증 모두 hook이 등록대로 실행되고, 다른 두 도구와 병행 시에도 자신의 `additionalContext`가 다른 도구 출력과 함께 누락 없이 concatenate됨을 실측 확인했다. 이는 병행 운용 시 신뢰성 근거로 유효하다.
- **Token efficiency**: 3-way 측정에서 baseline(3개 도구 OFF) 대비 Claude-Mem 자체의 순수 오버헤드를 프롬프트 캐시 잡음 때문에 통계적으로 분리하지 못했다 — **UNVERIFIED로 명시**, "무시할 만하다"고 단정하지 않는다.
- **Security**: `user_prompts` 테이블의 원문 프롬프트 무기한·비필터 저장은 실제로 스키마 검사로 확인된 사실(추정 아님). 이는 조건부 채택의 핵심 사유다 — 로컬 전용 모드(cloud sync 비활성)라는 완화 요인은 있으나, 로컬 파일 자체의 노출 위험(디스크 접근 권한, 백업 유출 등)은 남는다.
- **결론**: 이미 실사용 중(2026-08-08 설치 검증)이고 반증 근거가 없으므로 유지를 권고하되, 위 3개 UNVERIFIED 항목을 Open Issue로 명시하고 향후 재검토 대상으로 남긴다.

### 5-6. Token Optimizer — 상시 활성화 가치 및 governance 문서 검토 방해 가능성 (2026-09-08 갱신)

**이 섹션은 2026-09-08 Token Optimizer HOLD Resolution PoC로 대체·갱신되었다. 상세 Evidence는 [`integrations/token-optimizer-hold-resolution-2026-09.md`](token-optimizer-hold-resolution-2026-09.md) 참고.**

- 후속 PoC에서 upstream 최신 소스를 실제로 clone·빌드하고 hook 스크립트를 합성 payload로 직접 재실행해 재검증했다. 이전 리뷰가 "실측된 실패 사례는 아니다(UNVERIFIED)"로 남겼던 청크 경계 누락 여부는 이번에 **실제로 재현·측정**했다: BASELINE.md(63,414자, 17 chunk)를 chunkIndex 0~16 전부 순회·재조립한 결과 원본과 byte-for-byte 완전 일치 — 청크 분할 자체는 정보를 누락하지 않는다.
- 더 근본적으로, upstream의 기본 동작 모드가 이전 리뷰 시점 이후 `enforce`에서 `assist`로 바뀌어 있었다(upstream 자신의 A/B 측정 근거). **기본 설정에서는 Read가 애초에 차단·재작성되지 않는다** — BASELINE.md Read를 기본 모드로 실제 hook에 통과시켜 무개입(exit 0, 출력 없음)을 실측 확인했다. 이전 리뷰의 우려("100KB 파일을 17개 청크로 분할해 반환한다")는 사용자가 `TOKEN_OPTIMIZER_MODE=enforce`를 명시적으로 켰을 때만 발생하며, 이 경우도 실측 확인했다.
- 코드 기반 allowlist(경로별 인터셉션 제외 설정)는 존재하지 않지만, **`offset`/`limit`를 지정한 paged Read는 어떤 모드에서도 차단되지 않는 구조적 안전 경로**임을 실측 확인했다 — 별도 설정 없이 이미 안전하게 문서를 완독할 수 있는 방법이 있다는 뜻이다.
- **판단 변경**: 위 근거로 "상시 활성화 가치 없음(Hold)"에서 "정확히 명시된 운영 범위 내에서 채택 가능(Conditional Adopt)"으로 재판정한다. 핵심 조건은 `TOKEN_OPTIMIZER_MODE`를 `enforce`로 절대 전환하지 않는 것 — 이 조건이 지켜지는 한 governance 문서 전수 검토를 방해하지 않는다.

## Open Issues

1. Claude-Mem `user_prompts` 원문 저장에 대한 필터링/보존기간 정책 부재 — 완화책 미검증.
2. Claude-Mem 순수 token/context overhead 정밀 측정 미완료(프롬프트 캐시 잡음으로 인한 방법론적 한계).
3. Claude-Mem의 "지시받은 특정 사실의 verbatim 보존" 정확도 미검증(narrative 재구성만 확인됨).
4. ~~Token Optimizer의 대형 governance 문서 청크 분할이 실제 내용 누락으로 이어지는지 실측 필요~~ → 2026-09-08 PoC로 해소: 청크 전체 순회 시 정보 손실 없음을 실측 확인.
5. ~~Token Optimizer에 경로별 allowlist 설정 존재 여부~~ → 2026-09-08 PoC로 해소: 그런 설정은 없으나, `assist` 기본 모드 자체가 governance 문서를 차단하지 않고, `offset`/`limit` paged Read가 구조적 안전 경로임을 확인.
6. Token Optimizer: `TOKEN_OPTIMIZER_MODE=enforce`로의 전환이 사람의 실수로 발생하지 않도록 하는 절차적 장치 없음(현재는 "설정하지 않는다"는 운영 규칙에 의존) — 자동 검증 수단 미검증.
7. Token Optimizer: BASELINE.md가 향후 100,000자를 넘어설 경우의 markdown truncation 결함 — 코드로는 확인했으나 실제 재현은 하지 않음, 주기적 문서 크기 점검 필요.
8. Token Optimizer: harvest egress가 `ANTHROPIC_API_KEY` 사전 존재만으로 의도치 않게 활성화될 수 있는 경로 — 이번 세션 환경에서는 비활성 확인, 향후 환경변수 변경 시 재확인 필요.

## Architecture/Contract 변경 여부

없음. 이 문서는 `.claude/docs/integrations/` 아래의 검증 evidence 문서이며, Architecture/RFC/ADC/ADR의 source of truth를 변경하지 않는다.

## 최종 구성안 요약

- **Claude-Mem**: 유지(조건부) — 현행 로컬 전용 설치 그대로, 위 Open Issue 1–3을 추적 대상으로 기록.
- **Token Optimizer**: 조건부 채택(Conditional Adopt) — `TOKEN_OPTIMIZER_MODE`를 기본값(`assist`)에서 절대 `enforce`로 전환하지 않는다는 조건 하에 상시 설치 가능. Open Issue 6–8을 추적 대상으로 기록.
- **Context Handoff**: 최종 제외(Exclude) — 재구현하지 않는다.
