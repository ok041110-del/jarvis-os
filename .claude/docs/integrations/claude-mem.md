# Claude-Mem 통합 가이드

검증일: 2026-08-08

## 정체

Claude-Mem은 Claude Code 세션 간 영속 메모리를 제공하는 오픈소스 플러그인이다. 세션 중 도구 사용을 관찰해 AI로 요약을 생성하고, 다음 세션 시작 시 관련 컨텍스트를 주입한다.

- 공식 저장소: https://github.com/thedotmack/claude-mem
- 작성자: Alex Newman (@thedotmack)
- 검증 시점 버전: 13.14.0

## 설치 (검증 완료)

```bash
npx claude-mem@latest install
```

또는 Claude Code 플러그인 마켓플레이스:

```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

이번 세션에서 `npx claude-mem@latest install`을 실제로 실행해 검증했다. 결과:

```
Dependencies installed OK
Claude Code: plugin registered OK
Plugin dir:  ~/.claude/plugins/marketplaces/thedotmack
Auto-memory: left enabled (native Claude Code memory preserved)
```

`npx claude-mem@latest doctor` 결과 (worker 미기동 상태):

```
✓ Bun runtime            v1.3.11
✓ uv (vector search)     uv 0.8.17
✓ Plugin installed       ~/.claude/plugins/marketplaces/thedotmack
✓ Marketplace runtime    node_modules and install marker present
✗ Worker daemon          no response — start with `npx claude-mem start`
```

## 설치 범위 — 사용자(머신) 스코프, 저장소 스코프 아님

claude-mem은 **`scope: "user"`로 설치되며 항상 사용자 홈 디렉터리(`~/.claude-mem`, `~/.claude/plugins`)에 저장된다.** 이 저장소(jarvis-os) 안에는 claude-mem이 만드는 프로젝트 전용 설정 파일이 없다 — 그래서 이 저장소의 `.claude/` 트리에는 claude-mem 관련 파일을 커밋하지 않는다. 대신 이 문서가 설치 절차의 기록이다.

각 사용자가 이 저장소로 작업하려면 **자신의 머신에서** 위 설치 명령을 1회 실행하면 된다. 5개의 lifecycle hook(SessionStart, UserPromptSubmit, PostToolUse, Stop, SessionEnd)이 자동 등록되어, 두 번째 세션부터 이전 컨텍스트가 주입된다.

## 동작 시작

```bash
npx claude-mem start   # worker 데몬 기동 (설치만으로는 자동 시작되지 않음, non-TTY 환경)
```

## 제거/롤백

```bash
npx claude-mem uninstall
```

우선 열려 있는 모든 Claude Code 세션을 종료한 뒤 제거해야 한다 — 활성 hook이 있으면 `~/.claude-mem`이 재생성된다(공식 경고).
