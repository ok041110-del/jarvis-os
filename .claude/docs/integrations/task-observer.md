# Task Observer 스킬 통합 가이드

검증일: 2026-08-08

## 정체

Task Observer("One Skill to Rule Them All")는 작업 세션 중 스킬 개선 기회를 관찰·기록하는 메타 스킬이다. 작성자: Eoghan Henn (rebelytics.com). 라이선스: CC BY 4.0.

- 공식 저장소(Canonical Source): https://github.com/rebelytics/one-skill-to-rule-them-all

## 설치 (완료)

공식 번들(SKILL.md + references/ 3개 파일)을 그대로 복사해 배치했다.

```
.claude/skills/task-observer/
├── LICENSE.txt
├── SKILL.md
└── references/
    ├── environments.md
    ├── skill-authoring.md
    └── weekly-review.md
```

## 동작 방식

- 코드/설정 설치가 아니라 **Claude Code가 세션 시작 시 자동으로 탐색하는 스킬 파일**이다. 별도 실행 파일이나 서버가 없다.
- SKILL.md 자체가 "설명 매칭만으로는 안정적으로 트리거되지 않으니 CLAUDE.md에 활성화 지시문을 함께 두라"고 권고한다 → 이 저장소 루트 `CLAUDE.md`에 반영했다.
- 관찰 로그는 `[workspace folder]/skill-observations/log.md`에 쌓인다. `workspace folder`는 세션마다 사라지지 않는 안정적인 경로여야 한다(SKILL.md 40행 참조) — 이 저장소를 작업 디렉터리로 쓰는 한, 로그는 저장소 밖(예: `~/.claude/projects/<project-id>/`)에 쌓이도록 스킬이 스스로 판단한다. 저장소 안에 로그 디렉터리를 미리 만들지 않았다.

## 충돌 가능성

기존 `.claude/skills/`가 비어 있었으므로(설치 전 확인 완료) 이름 충돌 없음.

## 제거/롤백

```bash
rm -rf .claude/skills/task-observer
```
