# Graphify 통합 가이드

검증일: 2026-08-30

## 정체

Graphify는 코드베이스(+문서/SQL/PDF)를 tree-sitter 기반으로 파싱해 queryable knowledge graph로 변환하는 도구다. Claude Code에서는 MCP 서버가 아니라 CLI + Skill 형태로 동작한다.

- 공식 저장소: https://github.com/Graphify-Labs/graphify
- 라이선스: Apache-2.0 / MIT 이중 라이선스
- PyPI 패키지: `graphifyy` (검증 시점 버전 0.9.52)

## 설치 (검증 완료)

```bash
uv tool install graphifyy
```

`pypi.org`가 이 세션의 아웃바운드 허용 목록(no-proxy)에 있어 문제없이 설치됨. 실행 파일 `graphify`, `graphify-mcp` 2개가 설치된다.

## 이 저장소에서 실행한 검증 (jarvis-os repo 대상)

```bash
graphify update . --no-cluster
```

결과:

```
AST extraction: 1524/1524 uncached files (100%) [4 workers]
[graphify watch] Rebuilt (no clustering): 14231 nodes, 17988 edges
```

API Key 없이(코드 전용 추출, LLM 클러스터링 생략) 완료됨.

이어서 `query` / `path` / `explain` 3개 기능을 모두 실제 그래프에 대해 실행해 정상 동작을 확인했다.

- `graphify query "Development HQ와 Kernel의 관계는?"` → `hqs/development/MVP.md`, `docs/architecture/core/RFC-0002-kernel-definition.md` 등 62개 관련 노드를 BFS로 반환.
- `graphify path "HQProvisioner" "CapabilityRegistry" --undirected` → `HQProvisioner --uses--> CapabilityRegistry` (1 hop) 반환.
- `graphify explain "CapabilityRegistry"` → 정의 위치(`archive/v1/.../registry.py:L11`)와 21개 연결(import/uses/method) 정확히 반환.

## Claude Code 연결 방법 (검증하지 않음, 문서 기준만 기록)

`graphify claude install`은 **CLAUDE.md에 graphify 섹션을 쓰고 PreToolUse hook을 등록**한다. 이는 이 저장소의 CLAUDE.md(승인된 governance 문서)를 자동으로 수정하는 동작이라, 이번 검증 범위(불필요한 설정/코드 변경 금지)에서 **의도적으로 실행하지 않았다** — CLI 단독 사용(`graphify query`/`path`/`explain`)만으로 검증 목적(실제 graph 생성·조회)은 충분히 달성됨. Claude Code에 정식으로 연결하려면 별도로 CLAUDE.md 변경 승인이 필요하다.

## 저장소 구조 영향

`graphify update .`는 저장소 루트에 `graphify-out/`(약 28MB, graph.json 등)을 생성한다. 이는 `.gitignore`에 없는 미추적(untracked) 산출물이었다 — 검증 종료 후 삭제했고, 커밋된 것은 없다(`git status` 클린 확인).

## 기존 도구와의 역할 중복

- Claude-Mem(세션 간 대화 요약 메모리), Task Observer(skill 개선 관찰), OmniRoute(Provider/Model 라우팅) 중 어느 것도 "코드/문서 구조를 그래프로 만들어 query/path/explain"하는 기능을 갖지 않는다 — 역할 중복 없음.

## 제거/롤백

```bash
uv tool uninstall graphifyy
rm -rf graphify-out  # 저장소에 남아있다면
```

## 도입 판단

CLI 기능(graph 생성 + query/path/explain)은 이 세션에서 실사용 검증 완료(PASS). 단, Claude Code 정식 연결(`graphify claude install`)은 CLAUDE.md 자동 수정을 동반하므로 **이 문서로 절차만 기록하고 실제 연결은 보류** — 필요 시 별도 승인 하에 진행한다.
