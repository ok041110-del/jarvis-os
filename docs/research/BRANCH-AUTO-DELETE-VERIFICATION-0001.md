# BRANCH-AUTO-DELETE-VERIFICATION-0001: GitHub Head Branch Auto-Delete 실측 확인

**목적**: PR merge 후 head branch가 자동 삭제되는지 실제 PR→merge로
검증한다. Repository Settings API를 읽거나 쓰는 도구가 이 세션에
없어(GitHub MCP 서버에 repository settings 엔드포인트 없음), 직접
설정값을 확인/변경할 수 없다 — 대신 실제 동작으로 간접 검증한다.

## 배경(간접 증거)

`PHASE12-AUTOMATION-WORKFLOW-AUDIT-0001.md` 후보 2가 이미 관찰한 사실:
Phase 9 종료 시 PR #60/#61 병합 후 `git push origin --delete`가
"remote ref does not exist"로 실패했다 — 이는 병합 시 GitHub이 이미
head branch를 자동 삭제했다는 뜻이다.

## 이번 실측

이 문서 자체가 그 실측용 PR의 유일한 변경 내용이다. 이 branch를
`main`으로 PR→merge한 뒤, `git fetch --all --prune`로 이 branch의
remote ref가 자동으로 사라지는지 확인한다.

## Architecture/Governance

RFC/ADC/ADR 없음. Baseline/코드 변경 없음.
