# .claude/docs/

- 이 디렉터리는 실행환경 구성요소의 검증 evidence를 보관한다.
- Architecture/RFC/ADC/ADR/Baseline의 source of truth가 아니다 — 그 문서들은 `docs/`, `hqs/development/`에 있다.
- 새 구성요소를 설치·검증할 때만 문서를 추가한다.

## 문서

| 문서 | 내용 |
|---|---|
| [`integrations/task-observer.md`](integrations/task-observer.md) | Task Observer 스킬 설치 근거 |
| [`integrations/claude-mem.md`](integrations/claude-mem.md) | Claude-Mem 설치·연결 검증 |
| [`integrations/omniroute.md`](integrations/omniroute.md) | OmniRoute 설치·연결 검증 |
| [`integrations/tooling-finalization-review-2026-09.md`](integrations/tooling-finalization-review-2026-09.md) | Claude-Mem/Token Optimizer/Context Handoff 최종 채택 판정 |
| [`integrations/token-optimizer-hold-resolution-2026-09.md`](integrations/token-optimizer-hold-resolution-2026-09.md) | Token Optimizer HOLD Resolution PoC — assist 기본 모드 재검증 |
| [`integrations/llm-wiki-candidate-002-poc.md`](integrations/llm-wiki-candidate-002-poc.md) | LLM Wiki 후보 #2 (`Pratiyush/llm-wiki`) 독립 PoC — 판정 CONDITIONAL PASS (Production Adoption 아님) |
| [`integrations/llm-wiki-candidate-002-adoption-policy.md`](integrations/llm-wiki-candidate-002-adoption-policy.md) | LLM Wiki Candidate #2 Adoption Policy — 유지 전략·계층 경계·운영 규칙 R1–R5·Live Smoke 절차 |
| [`integrations/llm-wiki-candidate-002-adoption.md`](integrations/llm-wiki-candidate-002-adoption.md) | LLM Wiki Candidate #2 Production Adoption — 게이트 B1–B4 CLOSED, Derived Recall / non-authoritative 계층으로 채택(2026-09-08) |
| [`SMOKE_TEST-2026-08-08.md`](SMOKE_TEST-2026-08-08.md) | 실행환경 구성요소 Smoke Test 결과 |

`.claude/skills/*/SKILL.md` 각각의 목적/trigger/동작은 여기서 중복 기술하지 않는다 — 해당 SKILL.md가 유일한 출처다.
