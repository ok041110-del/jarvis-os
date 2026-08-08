# Smoke Test — Development HQ 실행환경 (2026-08-08)

범위: 설치된 구성요소의 최소 동작 확인만 수행한다. 실제 Task는 실행하지 않는다(사용자 지시).

## 1. Task Observer 스킬

- 배치: `.claude/skills/task-observer/SKILL.md` + `references/` 3개 파일 + `LICENSE.txt`
- **결과: PASS** — 파일을 저장소에 추가한 직후, 이 세션의 harness가 스킬 목록에 `task-observer`를 자동으로 인식했다(별도 재시작 없이 즉시 탐색됨). SKILL.md YAML frontmatter(`name`, `description`)가 정상 파싱되었다는 뜻이다.
- 스킬 자체 기능(관찰 로그 기록 등)은 이번 세션에서 활성 호출하지 않았다 — "실제 Task 실행 금지" 지시에 따라 별도 실행하지 않음.

## 2. Claude-Mem

- 설치 명령: `npx claude-mem@latest install` — 실제 실행, 성공.
- `npx claude-mem@latest doctor` 결과: Bun/uv/Plugin/Marketplace runtime 모두 OK. Worker daemon만 미기동(WARN, 정상 — 자동 시작 안 함 옵션대로 동작).
- `npx claude-mem@latest status` 결과: `Worker is not running` — 예상된 상태(수동 시작 필요, 문서화됨).
- **결과: PASS** (설치·CLI 응답 확인). Worker 상시 기동은 수행하지 않음(일시적 컨테이너이므로 의미 없음, 문서에 명시).

## 3. OmniRoute

- 설치 명령: `npm install -g omniroute` — 실제 실행, 성공(패키지 1181개, 경고만 있고 실패 없음).
- `omniroute --version` → `3.8.49`
- `omniroute doctor` 결과: `5 ok, 12 warning(s), 0 failure(s)`. WARN 항목은 모두 "서버 미기동" · "각 IDE/CLI 미연결" 등 아직 연결 단계를 수행하지 않았기 때문에 나오는 예상된 경고이며 실패(FAIL)는 0건.
- **결과: PASS** (CLI 설치·기동 가능 여부 확인). 상시 서버(`omniroute serve`)는 기동하지 않음(문서에 명시).

## 4. CLAUDE.md

- 저장소 루트에 신규 생성. Frozen Architecture 문서 목록, 작업 시작 순서, 실행환경 구성요소 표, Task Observer 활성화 지시문 포함.
- **결과: PASS** (harness가 세션 시작 시 읽는 표준 위치에 파일 존재 확인).

## 5. Headroom

- 설치하지 않음 — 사용자 결정(OmniRoute와의 프록시 충돌 가능성 + Claude Code 연동 활성 버그로 제외).
- Smoke Test 대상 아님.

## 종합

| 구성요소 | 설치 | Claude Code 연결 | Smoke Test |
|---|---|---|---|
| Task Observer | 완료 (저장소 스킬) | 완료 (harness 자동 인식) | PASS |
| Claude-Mem | 완료 (이 세션 검증) | 문서화만 (사용자 머신에서 개별 설치 필요) | PASS |
| OmniRoute | 완료 (이 세션 검증) | 문서화만 (사용자 머신에서 개별 연결 필요) | PASS |
| Headroom | 제외 | 해당 없음 | 해당 없음 |

실제 Task 1건 실행은 이번 세션 범위에서 제외되었다(사용자 지시, 2026-08-08). 다음 세션에서 별도로 진행한다.
