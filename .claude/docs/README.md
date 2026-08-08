# .claude/docs/

- 이 디렉터리는 실행환경 구성요소의 검증 evidence를 보관한다.
- Architecture/RFC/ADC/ADR/Baseline의 source of truth가 아니다 — 그 문서들은 `docs/`, `development-hq/`에 있다.
- 새 구성요소를 설치·검증할 때만 문서를 추가한다.

## 문서

| 문서 | 내용 |
|---|---|
| [`integrations/task-observer.md`](integrations/task-observer.md) | Task Observer 스킬 설치 근거 |
| [`integrations/claude-mem.md`](integrations/claude-mem.md) | Claude-Mem 설치·연결 검증 |
| [`integrations/omniroute.md`](integrations/omniroute.md) | OmniRoute 설치·연결 검증 |
| [`SMOKE_TEST-2026-08-08.md`](SMOKE_TEST-2026-08-08.md) | 실행환경 구성요소 Smoke Test 결과 |

`.claude/skills/*/SKILL.md` 각각의 목적/trigger/동작은 여기서 중복 기술하지 않는다 — 해당 SKILL.md가 유일한 출처다.
