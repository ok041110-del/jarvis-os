# Context7 통합 가이드 (미도입)

검증일: 2026-08-30

## 정체

Context7(Upstash)는 실시간으로 최신 라이브러리 공식 문서를 가져와 LLM/AI 코드 에디터에 제공하는 MCP 서버다.

- 공식 저장소: https://github.com/upstash/context7
- 라이선스: MIT
- CLI 패키지: `ctx7` (npx로 실행, 검증 시점 `npx ctx7 --help` 정상 동작)

## 설치 시도 및 실패 (검증 결과: FAIL)

```bash
npx -y ctx7 library langgraph "state graph quickstart"
```

결과: `✖ HTTP error 403`

원인 확인: 이 세션의 아웃바운드는 정책 프록시(`$HTTPS_PROXY`)를 경유하며, `context7.com`은 조직 egress 정책의 허용 목록(no-proxy 목록: `registry.npmjs.org`, `pypi.org` 등만 포함)에 없다. 직접 확인:

```bash
curl -sS -i "https://context7.com/api/v1/search?query=langgraph"
# curl: (56) CONNECT tunnel failed, response 403
```

`$HTTPS_PROXY/__agentproxy/status`에도 `recentRelayFailures`는 없었고, 프록시 README는 이 403을 "목적지 호스트가 이 세션의 조직 egress 정책에서 허용되지 않음 — 우회하지 말고 보고"로 명시한다. 즉 **Context7 자체의 결함이 아니라, 이 실행환경(ephemeral 세션)의 네트워크 정책 제약**이다.

## 검증 대상으로 선정했던 라이브러리

이 저장소의 실제 외부 의존성(`archive/v1/pyproject.toml` 워크스페이스 및 소스 import 기준: `langgraph`, `casbin`, `pyyaml`, `mcp`, `pytest`)을 먼저 조사했고, 이 중 공식 문서 조회 검증 대상으로 `langgraph`를 선정했다(실제 코드에서 `jarvis_adapter_workflow_langgraph`로 사용 중). API 조회 자체가 네트워크 단계에서 차단되어 문서 반환 여부는 확인하지 못했다.

## 설치/등록 잔여물

`npx -y ctx7 ...`는 세션 내 npx 캐시로 일시 실행되었을 뿐, `setup`(MCP 등록/OAuth) 단계까지 도달하지 못했다. 확인 결과 `~/.claude` 하위 MCP 설정, `~/.context7` 등 잔여 설정 파일 없음 — 별도 롤백 불필요.

## 기존 도구와의 역할 중복

Claude-Mem/Task Observer/OmniRoute 중 "외부 라이브러리 공식 문서를 실시간 조회"하는 기능은 없다 — 역할 자체는 중복되지 않는다(검증만 실패).

## 도입 판단

**미도입.** 도구 자체의 적합성(역할 비중복, MIT 라이선스, 실제 의존성과의 연관성)은 확인됐으나, 이 실행환경에서 `context7.com`이 egress 정책으로 차단되어 실사용 검증(Acceptance Criteria: 실제 문서 조회 결과 1건 이상)을 충족하지 못했다. 사용자 로컬 환경(정책 제약이 없는 환경)에서는 위 설치 절차로 재검증 가능 — 이 문서는 그 재현 절차와 이번 세션의 실패 원인 기록이다.
