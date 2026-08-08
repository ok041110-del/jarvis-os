# CLAUDE.md

Claude Code가 이 저장소에서 작업을 시작할 때 가장 먼저 읽는 문서다.

## 이 저장소는 무엇인가

Jarvis OS v2 Starter Kit이다. `README.md`가 프로젝트 구조 개요를, `development-hq/HANDOVER.md`가 구현 인수인계 시작점을 갖는다.

## 절대 규칙 — Frozen Architecture

다음 문서는 **참조 대상이며 변경 대상이 아니다**:

- `docs/01_architecture/BASELINE.md` — Jarvis OS Architecture Baseline v1.0
- `development-hq/BASELINE.md` — Development HQ Baseline v1.0
- `development-hq/*` 전체 (MISSION/RESPONSIBILITY/BOUNDARY/STRUCTURE/MVP/IMPLEMENTATION_RULES/HANDOVER)
- `docs/02_rfc/`, `docs/03_adc/`, `docs/04_adr/`

Architecture 변경이 필요하다고 판단되면 **직접 수정하지 않고** `docs/02_rfc` → `docs/03_adc` → `docs/04_adr` 절차로 제안만 기록한다. 자세한 금지 사항은 `development-hq/IMPLEMENTATION_RULES.md`를 그대로 따른다.

## 작업 시작 순서

1. `README.md`
2. `development-hq/HANDOVER.md` — 인수인계 요약, Next Step
3. `docs/01_architecture/BASELINE.md`
4. `development-hq/BASELINE.md`
5. `development-hq/MVP.md`
6. `development-hq/IMPLEMENTATION_RULES.md`

## 실행환경 (Development HQ Execution Environment)

이 저장소는 아래 실행환경 구성요소를 사용한다. 각 구성요소의 검증 결과와 설치 방법은 `.claude/docs/integrations/`에 기록되어 있다.

| 구성요소 | 역할 | 스코프 | 문서 |
|---|---|---|---|
| Task Observer | 작업 세션 관찰 및 스킬 개선 기회 기록 | 저장소(`.claude/skills/`) | `.claude/docs/integrations/task-observer.md` |
| Claude-Mem | 세션 간 영속 메모리 | 사용자 머신(`~/.claude-mem`) | `.claude/docs/integrations/claude-mem.md` |
| OmniRoute | AI Gateway (Provider/Model 라우팅) | 사용자 머신(`~/.omniroute`) | `.claude/docs/integrations/omniroute.md` |

Headroom(컨텍스트 압축 proxy)은 2026-08-08 검증에서 OmniRoute와 동일하게 `ANTHROPIC_BASE_URL`을 점유하려 하고, Claude Code 연동 관련 활성 버그(1M 컨텍스트 축소, Remote Control 비활성화 등)가 다수 확인되어 이번 실행환경 구성에서 **의도적으로 제외**했다. 재검토 시 `.claude/docs/integrations/omniroute.md`의 "Headroom과의 동시 사용 주의" 절을 먼저 참고한다.

Claude-Mem과 OmniRoute는 사용자 로컬 머신에서 상시 실행되어야 의미가 있는 도구이므로, 이 저장소 자체에는 실행 상태나 자격 증명을 커밋하지 않는다. 각 사용자가 자신의 머신에서 통합 문서의 설치 절차를 1회 수행한다.

## Task Observer 활성화

`.claude/skills/task-observer/SKILL.md`가 이 저장소에 설치되어 있다. 이 스킬은 설명 매칭만으로는 안정적으로 트리거되지 않으므로, **작업 지향 세션을 시작할 때(도구를 사용해 산출물을 만들기 시작하기 전) task-observer 스킬을 먼저 호출한다.**

## Skills

`.claude/skills/`에 등록된 스킬:

- `task-observer` — 세션 관찰 및 스킬 개선 후보 기록 (위 참조)

새 스킬을 추가할 때는 기존 스킬과의 이름 충돌 여부를 먼저 확인한다.

## 이 문서를 변경할 때

CLAUDE.md는 실행환경 설정 문서이며 Frozen Architecture 대상이 아니다. 실행환경 구성요소가 바뀌면 이 문서와 `.claude/docs/integrations/`를 함께 갱신한다.
