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
| **Token Optimizer** | **Hold** (현행 미채택 유지) | 독립 PoC 자체 결과가 이미 HOLD. 3-way 결합 시 대형 Read(~25KB+)·raw grep을 실제로 차단해 smart_read/smart_grep으로 우회시키는 동작 실측, 반복 읽기 캐시 히트도 실측 확인(코드 탐색형 워크로드에는 실질 절감 근거 있음). 그러나 이번 리뷰에서 Baseline/Governance 문서 전수 검토 워크플로와의 충돌 가능성을 재평가함(아래 6번 항목). | 대형 governance 문서(`docs/architecture/baseline/BASELINE.md`, 누적 ADR/ADC 세트 등)를 대상으로 (a) 실제 청크 경계에서 내용 누락 여부, (b) `docs/architecture/`·`docs/decisions/` 경로를 인터셉션에서 제외하는 allowlist/threshold 설정이 실제로 존재하고 작동하는지, (c) 그 경우 실측 token/latency 재비교 — 모두 미검증. |
| **Context Handoff (-lite 포함)** | **Exclude** (최종 제외, 확정) | 정식 구현 라이브 재현 테스트 3/3 전부 실패(5필드 추출 0건, `~/.claude/handoff-lite/` 생성 안 됨) — 이전 PoC의 FAIL 결과 그대로 확정. 원인은 자유 서술형 모델 출력을 단일 라인 정규식으로 파싱하는 구현 방식 자체의 결함이며, hook 등록/scope/guard 설계는 정상 동작이 확인됨. | 없음 — 요구사항에 따라 재구현하지 않고 이 판정으로 확정. 향후 재도전 시 구조화 출력 기반 재설계가 필요하다는 점만 기록으로 남긴다(과거 세션 Observation 15). |

## 항목별 상세

### 4. Claude-Mem — 유지 후보 재평가

- **Reliability / context quality**: 3-way PoC와 fresh-startup 검증 모두 hook이 등록대로 실행되고, 다른 두 도구와 병행 시에도 자신의 `additionalContext`가 다른 도구 출력과 함께 누락 없이 concatenate됨을 실측 확인했다. 이는 병행 운용 시 신뢰성 근거로 유효하다.
- **Token efficiency**: 3-way 측정에서 baseline(3개 도구 OFF) 대비 Claude-Mem 자체의 순수 오버헤드를 프롬프트 캐시 잡음 때문에 통계적으로 분리하지 못했다 — **UNVERIFIED로 명시**, "무시할 만하다"고 단정하지 않는다.
- **Security**: `user_prompts` 테이블의 원문 프롬프트 무기한·비필터 저장은 실제로 스키마 검사로 확인된 사실(추정 아님). 이는 조건부 채택의 핵심 사유다 — 로컬 전용 모드(cloud sync 비활성)라는 완화 요인은 있으나, 로컬 파일 자체의 노출 위험(디스크 접근 권한, 백업 유출 등)은 남는다.
- **결론**: 이미 실사용 중(2026-08-08 설치 검증)이고 반증 근거가 없으므로 유지를 권고하되, 위 3개 UNVERIFIED 항목을 Open Issue로 명시하고 향후 재검토 대상으로 남긴다.

### 5-6. Token Optimizer — 상시 활성화 가치 및 governance 문서 검토 방해 가능성

- 독립 PoC(HOLD)와 3-way PoC 결과를 결합하면: 대형 파일 반복 탐색이 잦은 **코드 탐색형 워크로드**에는 실측된 캐시 히트·청크 분할 덕에 token 절감 가치가 있다.
- 그러나 Jarvis OS의 실제 운영 방식(`CLAUDE.md`의 Context Loading 원칙 — Architecture/Governance 문서를 **전수·완결 형태로** 읽는 것을 전제)과는 설계 철학이 충돌한다: smart_read가 100KB 파일을 17개 청크로 분할해 반환한다는 것은, 하나의 canonical 문서를 처음부터 끝까지 한 번에 읽어야 하는 governance 검토 작업에서 (a) 청크 경계에서 내용이 누락되거나 문맥이 끊길 위험, (b) 청크당 별도 tool round-trip으로 인한 추가 지연·오버헤드가 코드 탐색형 워크로드와 반대 방향으로 작용할 가능성을 의미한다.
- 이 충돌 가능성은 **실제 대형 governance 문서를 대상으로 한 청크 경계 누락 여부 실측 없이는 확정할 수 없다** — 이번 리뷰에서는 새 라이브 테스트를 수행하지 않았으므로, 이 결론은 "3-way PoC에서 관찰된 청크 분할 동작 + 문서 전수 검토라는 프로젝트 요구사항" 사이의 논리적 충돌 지적이며, 실측된 실패 사례는 아니다(UNVERIFIED로 표기).
- **판단**: 코드 탐색형 워크로드에 대한 실측 이점과, governance 문서 전수 검토 워크로드에 대한 미해결 리스크가 공존한다. 후자가 Jarvis OS Development HQ의 핵심 워크플로(Frozen Architecture 원칙상 Baseline/ADR을 정확히 완독해야 하는 절차)와 직접 관련되므로, 이 리스크를 해소(allowlist/threshold 설정 검증)하기 전에는 **상시 활성화 가치가 있다고 판단하지 않는다**. 독립 PoC의 HOLD를 유지한다.

## Open Issues

1. Claude-Mem `user_prompts` 원문 저장에 대한 필터링/보존기간 정책 부재 — 완화책 미검증.
2. Claude-Mem 순수 token/context overhead 정밀 측정 미완료(프롬프트 캐시 잡음으로 인한 방법론적 한계).
3. Claude-Mem의 "지시받은 특정 사실의 verbatim 보존" 정확도 미검증(narrative 재구성만 확인됨).
4. Token Optimizer의 대형 governance 문서 청크 분할이 실제 내용 누락으로 이어지는지 실측 필요.
5. Token Optimizer에 `docs/architecture/`, `docs/decisions/` 등 경로별 인터셉션 제외(allowlist) 설정이 실제로 존재·작동하는지 확인 필요 — 확인되면 재평가 대상.

## Architecture/Contract 변경 여부

없음. 이 문서는 `.claude/docs/integrations/` 아래의 검증 evidence 문서이며, Architecture/RFC/ADC/ADR의 source of truth를 변경하지 않는다.

## 최종 구성안 요약

- **Claude-Mem**: 유지(조건부) — 현행 로컬 전용 설치 그대로, 위 Open Issue 1–3을 추적 대상으로 기록.
- **Token Optimizer**: 미채택 유지(Hold) — 상시 활성화하지 않는다. Open Issue 4–5가 해소되면 재평가.
- **Context Handoff**: 최종 제외(Exclude) — 재구현하지 않는다.
