# EVIDENCE-0009: OmniRoute 운영 환경 가용성 — macOS + iPhone 범위 확정 검증

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. `ADR-0017`, `EVIDENCE-0006`, `EVIDENCE-0007`, `EVIDENCE-0008`이
확정한 범위를 그대로 전제하고, 이번 검토(운영 환경 가용성 범위를
macOS + iPhone 두 환경으로 확정)의 결과만 기록한다. **코드 변경
없음.** 실제 Provider egress 없음(§3, §9).

## 1. 검토 목적

OmniRoute 운영 환경 가용성 검증 범위에서 Android를 제외하고,
macOS(Primary Execution Host)와 iPhone 두 환경으로 확정한다.
`EVIDENCE-0007` §6.2가 남긴 4개 재검토 선행조건 중 1번("사용자가
실제 로컬 환경에서 OmniRoute를 기동·구성했음을 확인")과 관련해,
"실제 로컬 환경"이 구체적으로 어떤 기기·실행 구조를 가리키는지
정리하는 것이 이 문서의 목적이다. Call-Site Conversion 자체의
재개 여부를 판정하지 않는다 — 그 판정은 `EVIDENCE-0007`의 선행조건
전체가 충족될 때까지 별도로 유지된다(§7).

## 2. macOS — Primary Execution Host 검증

### 2.1 정적 확인

```
--- macOS platform ---
Darwin ...-MacBookAir.local 24.5.0 Darwin Kernel Version 24.5.0 ...
RELEASE_ARM64_T8103 arm64
--- Node.js ---
/usr/local/bin/node
v24.18.0
--- OmniRoute cached package ---
.../node_modules/omniroute/dist/server.js
3.8.50
--- real ~/.omniroute snapshot ---
mtime=1788605986 size=2547712
```

macOS(Darwin, Apple Silicon arm64), Node.js v24.18.0, OmniRoute
패키지(v3.8.50, `dist/server.js`)가 모두 이 환경에 실재한다 —
Claude Code(CLI, 이 세션 자체가 그 증거) + Jarvis(이 저장소) +
OmniRoute(캐시된 패키지)가 **동일 macOS 환경에서 실행·연결
가능한 구조**임을 정적으로 확인했다.

### 2.2 실제 기동·연결 사이클(isolated, controlled)

격리된 `DATA_DIR`, 가짜 API 키, 비표준 포트로 OmniRoute standalone
서버를 실제로 1회 기동했다.

```
DATA_DIR=<isolated temp dir> NODE_ENV=test \
  OMNIROUTE_ALLOW_DEFAULT_DATA_DIR=0 OMNIROUTE_API_KEY=avail-check-key-0001 \
  PORT=20350 HOSTNAME=127.0.0.1 node dist/server.js
```

- `GET http://127.0.0.1:20350/api/health` → **200** (2회 polling
  이내, 기동 확인).
- `blockedProviders` 안전조건 재확인(read-only 우선, `EVIDENCE-0003`/
  `0004` 방식과 동일): 격리된 `storage.sqlite`의 `key_value` 테이블에
  `blockedProviders=["opencode","felo-web"]`를 삽입 후
  `GET /api/v1/auto-combo/auto/candidates` → `{"channel":"auto",
  "candidates":[]}` — **후보 0개**, 즉 이 메커니즘이 격리 환경에서도
  여전히 정확히 동작함을 재확인했다.
- `REQUIRE_API_KEY` 관련: 이번 기동에서는 `OMNIROUTE_API_KEY`(관리자
  키)만 설정했고 `REQUIRE_API_KEY`는 설정하지 않았다 — 인증 헤더
  없이도 `/api/v1/auto-combo/auto/candidates`가 200을 반환했다.
  이는 **이번 검토에서 새로 발견한 것이 아니라 기존에 이미 알려진
  구성 방식대로 재현한 것**이다(`REQUIRE_API_KEY`는 별도로 명시
  설정해야 하는 독립 플래그) — 이 문서는 그 플래그의 기존 동작을
  변경하거나 재판정하지 않는다(사용자 지침 7, 변경 금지).
  실제 egress 위험은 이 플래그 유무와 무관하게, 이 격리 인스턴스에
  **실제 provider connection이 전혀 구성되지 않았으므로**
  `candidates`가 0개로 유지되어 원천 차단됐다(위 결과) — zero-egress
  결론 자체는 이 재확인으로 흔들리지 않는다.
- 정리: 프로세스 종료(`kill`), 임시 `DATA_DIR` 삭제. 실제
  `~/.omniroute/storage.sqlite`는 검증 전후 **mtime=1788605986,
  size=2547712로 완전 동일**(변경 없음, 세션 전체를 통틀어 유지된
  값과 일치).

### 2.3 판정 — macOS

**PASS.** Claude Code + Jarvis + OmniRoute가 동일 macOS 환경에서
실행·연결 가능함을 정적·동적으로 모두 확인했다. isolated `DATA_DIR`,
localhost/controlled endpoint 접근, `blockedProviders` 안전조건,
zero real egress, 실제 `~/.omniroute` 비변경을 모두 재확인했다.

## 3. iPhone — Claude Code 사용 환경과 OmniRoute 연결 구조 분석

이 절은 **아키텍처 추론에 근거한 분석**이다(이 세션은 iPhone
실기기에 접근할 수 없으므로 경험적 실행 검증은 불가능하다 —
§7이 이를 명시적 UNVERIFIED로 구분한다).

### 3.1 Claude Code의 iPhone 사용 경로

이 세션 자신의 시스템 프롬프트가 명시하는 Claude Code의 공식
인터페이스는 "CLI in the terminal, desktop app (Mac/Windows), web
app (claude.ai/code), and IDE extensions (VS Code, JetBrains)"뿐이다
— **네이티브 iOS 앱은 명시된 인터페이스 목록에 없다.** 저장소
전체(`.claude/docs/`, `docs/`)를 검색한 결과 iPhone/iOS/mobile/
Remote Control 관련 기존 문서는 없다(`docs/research/INVESTMENT-HQ-*`의
무관한 2건 제외) — 이번이 이 저장소 최초의 관련 검토다.

iPhone에서 Claude Code에 접근하는 경로는 구조적으로 두 갈래로
나뉜다.

**(A) Remote Control — 이미 기동 중인 Mac 세션을 원격 조작**

이 계정에서 실제로 관측 가능한 예시: `ListAgents` 결과, 이 세션
자신 외에 idle 상태의 "cloud" 세션 2개("Engine 실패 전파 결함
수정", "Jarvis OS Architecture/Governance 종합 감사")가 존재한다.
`ListAgents`의 도구 설명 자체가 "Remote Control Sessions on other
machines"과 "cloud sessions"를 구조적으로 구분한다 — 즉 이 계정의
세션은 최소 두 실행 모델을 가진다: (i) 사용자의 실제 로컬 머신에서
실행되며 원격(예: iPhone)에서 제어만 하는 세션, (ii) Anthropic
호스팅 sandbox(클라우드 컨테이너)에서 자체적으로 실행되는 세션.

iPhone이 (i) 방식으로 macOS의 Claude Code 세션을 Remote Control하는
경우, **실제 실행(및 그에 따른 OmniRoute HTTP 호출)은 여전히 그
macOS 머신 위에서 일어난다** — 네트워크 관점에서 이는 §2에서 이미
PASS로 검증한 것과 **동일한 머신, 동일한 loopback 경로**다. iPhone은
입출력만 중계할 뿐 별도의 네트워크 경로를 새로 만들지 않는다.

**(B) 완전 클라우드 호스팅 세션(claude.ai/code 웹앱 또는 동등한
클라우드 세션) — Remote Control 없이 독립 실행**

이 경우 실제 실행은 Anthropic이 호스팅하는 별도 sandbox
컨테이너에서 일어난다(위 관측된 2개의 idle "cloud" 세션과 같은
실행 모델로 추정). 이 컨테이너의 `127.0.0.1`/loopback은 그
컨테이너 **자신의 네트워크 네임스페이스**를 가리키며, 사용자의
Mac에서 실행 중인 OmniRoute 인스턴스(§2의 `127.0.0.1:20350`)는
이 컨테이너 입장에서 도달 불가능한 별도 호스트다. 이 경로가
OmniRoute에 연결되려면 사용자가 OmniRoute를 **공인 네트워크에
명시적으로 노출**해야 하는데, 이는 (a) 이번 검토 범위 밖의
별도 보안 결정이고, (b) 지금까지 이 트랙 전체가 유지해 온
"controlled/isolated 환경 우선, 외부 노출 없음" 원칙과 어긋나는
방향이므로 이 문서는 이를 권고하지 않는다.

### 3.2 OmniRoute를 iPhone 자체에서 직접 실행하는 경로

OmniRoute standalone 서버는 Node.js 런타임 + 네이티브 바이너리
의존성(예: `better-sqlite3`)을 가진 상시 구동 프로세스다. 표준
(비탈옥) iOS 앱 샌드박스 모델은 이런 형태의 임의 백그라운드
Node.js 데몬을 지원하지 않으며, Claude Code의 공식 인터페이스
목록(§3.1)에도 iOS 네이티브 실행 경로가 없다. 따라서 "OmniRoute를
iPhone 위에서 직접 실행"하는 경로는 현재 표준 iOS 환경 기준으로
**구조적으로 성립하지 않는다.**

## 4. PASS/FAIL/UNVERIFIED 판정표

| 경로 | 판정 | 근거 |
|---|---|---|
| macOS → OmniRoute → controlled endpoint | **PASS** | §2 — 정적+실동 검증 완료 |
| iPhone → (Remote Control) → macOS 세션 실행 → OmniRoute | **PASS(추정, macOS 결과 상속)** | §3.1(A) — 실행이 §2에서 검증된 동일 macOS 경로 위에서 일어나므로 네트워크 관점에서 별도 경로가 아니다. iPhone 실기기 자체의 Remote Control 접속 동작은 이 세션에서 실행 검증 불가 — 상속 판단이지 독립 실측은 아니다 |
| iPhone → (완전 클라우드 세션, Remote Control 없음) → OmniRoute | **FAIL(구조적)** | §3.1(B) — 클라우드 컨테이너의 loopback이 Mac의 OmniRoute에 도달 불가. 공인 네트워크 노출은 범위 밖의 별도 보안 결정 |
| OmniRoute를 iPhone 자체에서 직접 실행 | **FAIL(구조적)** | §3.2 — 표준 iOS 앱 샌드박스 모델·Claude Code 공식 인터페이스 목록 어디에도 지원 근거 없음 |

## 5. Case A Boundary / 기존 안전조건 무변경 확인

- `blockedProviders`, `REQUIRE_API_KEY`: 기존 동작 그대로 재확인만
  했다(§2.2) — 코드·설정 변경 없음.
- `RUN_REAL_ENGINE_TESTS`, 이중 opt-in 게이트(`RUN_REAL_OMNIROUTE_TESTS`
  + `I_UNDERSTAND_REAL_EGRESS_RISK`): 이번 검토에서 실행하지 않았다
  (§2.2의 기동 사이클은 이 게이트들과 무관한, 별도의 read-only 위주
  수동 확인이며 pytest 자체를 실행하지 않았다) — 무변경.
- Case A Boundary: 이번 검토는 코드를 전혀 작성·수정하지 않았다
  (`git status`로 확인, §9) — 트리비얼하게 유지.
- 실제 Provider egress: 격리 인스턴스에 provider connection이
  구성되지 않았으므로 원천적으로 발생 불가능했다(§2.2).

## 6. Python 3.9 환경 문제와의 명시적 분리

`workflow_ast_context.py`의 PEP 604(`X | None`) 문법으로 인한 Python
3.9 collection 오류(`EVIDENCE-0006` §8, `EVIDENCE-0007` §2.1이 이미
기록)는 **이번 macOS/iPhone 가용성 검토와 무관한 별도 상태**로
유지한다. 이번 검토는 이 문제를 재현·재확인하지 않았고, 해결하지도
않았다 — macOS/iPhone 판정(§4)과 절대 혼합하지 않는다.

## 7. Call-Site Conversion 선행조건 재정리

`EVIDENCE-0007` §6.2의 4개 선행조건을 이번 발견에 비추어
재정리한다.

| # | 선행조건(원문 요약) | 이번 검토 이후 상태 |
|---|---|---|
| 1 | 사용자가 실제 로컬 환경에서 OmniRoute를 기동·`blockedProviders`/`REQUIRE_API_KEY` 구성을 **직접 확인** | **부분 진전, 미충족.** "실제 로컬 환경"이 macOS를 가리킨다는 것과 그 macOS 환경 자체가 구조적으로 가용하다는 것은 이번에 PASS로 확인했다(§2). 그러나 "사용자가 실제로(이 세션이 아니라) 자신의 운영용 OmniRoute 인스턴스를 기동하고 올바르게 구성했음을 확인"하는 것은 여전히 이 세션이 대신할 수 없다(`EVIDENCE-0007` §3.3과 동일한 한계) — 격리 검증(§2.2)은 "가능함"을 보였을 뿐 "실제로 그렇게 돼 있음"을 보이지 않는다 |
| 2 | `test_mvp_0001.py` 게이트 없는 실제 Engine 호출 재설계 | **충족(`EVIDENCE-0008`).** 이번 검토는 이 상태를 변경하지 않았다(§5) |
| 3 | Python 3.10+ 환경 또는 `workflow_ast_context.py` 제외 재검토 | **미충족, 무변경**(§6 — 이번 검토 범위 밖으로 명시적으로 분리) |
| 4 | 전환 자체를 Governance 절차(RFC/ADC/ADR)로 다시 확인할지 사용자가 명시적으로 선택 | **미충족, 무변경** — 이번 검토는 이 선택을 대신하지 않는다 |

**결론**: 4개 중 1개(#2)만 충족된 상태가 그대로 유지된다. 이번
검토는 #1의 "환경 구조" 측면을 명확히 했을 뿐, #1이 요구하는
"운영자의 직접 확인" 자체는 대체하지 못한다. 따라서 **Call-Site
Conversion은 여전히 HOLD**다 — `EVIDENCE-0007`의 판정을 재개하지
않는다.

## 8. Governance / Architecture 영향

- Architecture 변경: **없음**. Contract 변경: **없음**. Freeze 변경:
  **없음**.
- 코드 변경: **없음**(격리 검증은 캐시된 OmniRoute 패키지의 기존
  바이너리를 그대로 기동했을 뿐, 이 저장소의 어떤 파일도 수정하지
  않았다).
- `ADC-0027`~`ADC-0031`, `ADR-0015`~`ADR-0017`, `EVIDENCE-0001`~
  `EVIDENCE-0008`: **무수정**.
- 새로 작성한 파일: 이 Evidence 문서 1개뿐.

## 9. Provenance / Reproducibility

- macOS 정적 확인(§2.1): `uname -a`, `node -v`, OmniRoute 캐시
  패키지 경로 확인, 실제 `~/.omniroute/storage.sqlite` 스냅샷
  (`stat`) — 명령 및 원문 출력 §2.1에 그대로 인용.
- macOS 실동 확인(§2.2): 격리 `DATA_DIR`로 OmniRoute standalone
  서버 1회 기동 → `/api/health` 200 확인 → `blockedProviders`
  삽입(격리 `storage.sqlite`에 대해서만) → `/api/v1/auto-combo/
  auto/candidates` → `{"candidates":[]}` 확인 → 프로세스 종료 →
  임시 디렉터리 삭제 → 실제 `~/.omniroute/storage.sqlite`
  mtime/size 사전(`1788605986`/`2547712`)·사후(`1788605986`/
  `2547712`) 동일 확인.
- iPhone 분석(§3): 실기기 접근 불가 — 이 세션 자신의 시스템
  프롬프트(공식 인터페이스 목록), `ListAgents` 실행 결과(cloud
  세션 2개 관측), 저장소 전체 grep(`iphone|ios\b|mobile|remote
  control`, 무관한 2건 외 없음)에 근거한 아키텍처 추론 — **경험적
  실행 검증이 아님을 명시**(§4 표의 "UNVERIFIED/추정" 표기).
- 실제 Provider egress: 없음(격리 인스턴스에 provider connection
  미구성, 클라우드-경로는 분석만 수행하고 실행하지 않음).
- 코드 변경: **없음**(`git status`로 확인 — 이 Evidence 문서 1개만
  추가).
- commit/push/PR: 수행하지 않음.

## Self Review

- macOS를 Primary Execution Host로 정의하고 실행·연결 가능함을
  확인했는가 — **Pass**(§2).
- Node.js/OmniRoute 설치·기동·isolated `DATA_DIR`·localhost 접근·
  기존 안전조건을 검증했는가 — **Pass**(§2.2).
- iPhone을 "직접 실행 가능성"만으로 좁혀 조사했는가 — **아니오**,
  Claude Code 사용 환경과 OmniRoute 연결 구조를 독립적으로 검토했다
  (§3).
- iPhone에서 "OmniRoute를 iPhone에서 직접 실행" vs "macOS에서
  실행 후 iPhone이 접근"을 구분했는가 — **Pass**(§3.1, §3.2).
- 각 경로를 PASS/FAIL/UNVERIFIED로 판정했는가 — **Pass**(§4, 단
  Remote Control 경로는 "PASS(추정, 상속)"로 실측과 구분 표기).
- 실제 Provider egress를 발생시켰는가 — **아니오**(§9).
- `blockedProviders`/`REQUIRE_API_KEY`/`RUN_REAL_ENGINE_TESTS`/Case A
  Boundary/기존 zero-egress 조건을 변경했는가 — **아니오**(§5).
- Python 3.9 문제와 이번 가용성 문제를 혼합했는가 — **아니오**(§6).
- `EVIDENCE-0007`/`0008`을 대조해 Call-Site Conversion 실제
  선행조건을 재정리했는가 — **Pass**(§7).
- Call-Site Conversion을 재개했는가 — **아니오**(§7 결론 — HOLD
  유지).
- commit/push/PR을 수행했는가 — **아니오**.
