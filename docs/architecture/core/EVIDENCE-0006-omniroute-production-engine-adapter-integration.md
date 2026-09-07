# EVIDENCE-0006: OmniRoute Production Engine Adapter Integration — 구현·검증 결과

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. `ADR-0017`이 확정한 범위(§2 Responsibility Boundary, §6
Production Adoption 선언과 그 한계)를 그대로 전제하고, 이번에 실제로
수행한 코드 구현·테스트 결과만 기록한다.

## 1. 목적

`ADR-0017` §6.2가 "별도 구현 작업"으로 명시적으로 남겨 둔 것 —
OmniRoute Thin Caller를 `hqs/development/mvp/`의 실제 Engine Adapter
경계 안에 실제로 연결하는 것 — 을 확정된 Architecture/Governance
범위 안에서 수행한다. 새로운 Architecture/Contract 판단을 내리지
않으며, `ADC-0027`~`ADC-0031`·`ADR-0015`~`ADR-0017`의 Decision을
재론하지 않는다.

## 2. 사전 확인 — `call_engine()` 구조와 Trigger 검토

### 2.1 `hqs/development/mvp/engine.py::call_engine()` 구조

- 단일 함수 `call_engine(prompt: str) -> str`, `subprocess.run(["claude",
  ...])` 호출, 실패 시 `RuntimeError` 하나만 raise한다.
- 실제 호출부(전수 확인): `agents/backend.py`(2곳), `agents/design.py`,
  `agents/qa.py`, `agents/requirements.py`, `workflow_ast_context.py` —
  5개 파일, 모두 Development HQ의 실제 Dogfooding 경로다.
- Engine Adapter Contract(`hqs/development/BOUNDARY.md` "Engine 호출 —
  Kernel Engine Port/Adapter의 책임", `BASELINE.md` §14.1·§16.2)는
  이 파일을 Development HQ의 유일한 Engine 호출 지점으로 취급한다.

### 2.2 RT-0001 Candidate 2 / `ADC-0010` 재검토 조건 사전 확인

`docs/governance/rt/RT-0001.md` Candidate 2 Trigger 원문:

> Engine 수 ≥ 2 (두 번째 Engine이 실제로 추가되어 `call_engine()`
> 호출 지점이 둘 이상의 서로 다른 Engine을 대상으로 하게 됨)

`ADC-0010`(Engine Caller 위치, C1~C6 전부 Not Accepted) §부족한
Evidence는 C1(Kernel Engine Port/Adapter) 재검토에 "Kernel Module
Defer 3건, ADC-01·02, **Engine 수 ≥2**"의 **결합**이 필요하다고
명시한다.

**설계 결정(구현 착수 전)**: `call_engine()` 자체와 그 5개 기존
호출 지점을 **전혀 수정하지 않고**, OmniRoute 연결을 완전히 별개의
새 함수(`call_engine_via_omniroute()`, 별도 파일)로 추가한다. 이
설계 아래에서는:

- `call_engine()`의 호출 지점이 여전히 정확히 1개 Engine(claude
  CLI)만 대상으로 한다 — RT-0001 Candidate 2의 Trigger 조건("call_engine()
  호출 지점이 둘 이상의... Engine을 대상으로 하게 됨")이 문언 그대로
  충족되지 않는다.
- `Engine 수 ≥2`(C1 재검토에 필요한 결합 조건 중 하나)도 이
  의미에서 충족되지 않는다 — `call_engine()`이라는 단일 호출 표면은
  여전히 1개 Engine만 가리킨다.

**이 판단이 틀렸을 경우의 대비**: 만약 실제 코드 작성 중 이 설계를
지킬 수 없다는 것이 드러나면(예: 두 함수가 같은 호출 표면을
공유해야 하거나, 기존 호출부를 수정해야만 연결이 성립하는 경우),
그 시점에 구현을 중단하고 별도 Governance Decision(RT-0001 재평가)
대상으로 보고하기로 사전에 정했다. **실제 구현 결과 이 대비가
발동할 필요는 없었다** — §4가 그 근거를 코드/테스트로 고정한다.

### 2.3 결론 — 최소 변경 지점

**`hqs/development/mvp/`에 완전히 새로운 파일(`omniroute_engine.py`)을
추가하고, `engine.py`와 5개 기존 호출부는 한 글자도 수정하지 않는다.**
이것이 "Thin Caller를 실제 실행 경로(실제 Engine Adapter 모듈)에
연결"하면서 동시에 RT-0001/`ADC-0010` Trigger를 피하는 최소 변경
지점이다.

---

## 3. 구현 내용

### 3.1 `hqs/development/mvp/omniroute_engine.py`(신규)

- `call_engine_via_omniroute(prompt: str) -> str` — `call_engine()`과
  동일한 외부 계약(성공 시 문자열 반환, 실패 시 `RuntimeError` 하나만
  raise)을 따르는 단일 함수.
- stdlib(`http.client`, `json`, `os`, `socket`, `urllib.parse`)만
  사용 — 새 의존성 없음(`caller.py`와 동일 관례).
- 설정은 env var(`OMNIROUTE_BASE_URL`, `OMNIROUTE_API_KEY`,
  `OMNIROUTE_MODEL`, `OMNIROUTE_TIMEOUT_SECONDS`)로만 받는다 —
  기본 `model="auto"`(OmniRoute에 provider/model 선택을 그대로
  위임, `ADC-0031`·`ADR-0017` §2.3과 정합). Production에서 실제
  사용하려면 운영자가 그 OmniRoute 인스턴스에 `blockedProviders`/
  `REQUIRE_API_KEY`를 사전에 구성해야 한다는 것을 docstring에
  명시했다(`EVIDENCE-0003`~`EVIDENCE-0005`의 zero-config egress
  식별 결과 인용) — 이 함수 자신은 그 설정을 대신하지 않는다.
- `engine.py`를 import하지 않고, `engine.py`도 이 파일을 import하지
  않는다(§2.2 설계의 실제 구현).
- Provider/Model 선택, routing, fallback, budget/policy 판정 로직:
  **0줄**(§4.2가 정적으로 확인).

### 3.2 테스트(신규 3개 파일, 17개 테스트)

| 파일 | 개수 | 성격 |
|---|---|---|
| `hqs/development/mvp/tests/fake_omniroute_server.py` | (fixture, 테스트 아님) | 로컬 stdlib test double |
| `hqs/development/mvp/tests/test_omniroute_engine.py` | 7 | 단위(성공/오류 매핑 401·429·5xx·malformed/연결거부/timeout/기본 model) — 로컬 test double |
| `hqs/development/mvp/tests/test_omniroute_engine_boundary.py` | 7 | Case A 정적 검증 + RT-0001 non-trigger 실증(§4.1) |
| `hqs/development/mvp/tests/test_omniroute_engine_real.py` | 3 | 실제(격리) OmniRoute 서버 + 로컬 controlled double, 이중 opt-in 게이트 |

기존 `hqs/development/mvp/engine.py`·`test_engine.py`·5개 호출부
파일은 **한 글자도 수정하지 않았다**(git diff 0).

---

## 4. Case A Boundary·RT-0001 Non-Trigger 실증

### 4.1 정적 검증(`test_omniroute_engine_boundary.py`, 7/7 PASS)

- `engine.py`가 여전히 `call_engine` 하나만 정의하고 "omniroute"
  문자열을 전혀 포함하지 않는다(AST + 문자열 검사).
- `omniroute_engine.py`가 `engine`/`mvp.engine`을 import하지 않는다.
- `call_engine()`의 5개 기존 호출 지점(`agents/backend.py`·
  `design.py`·`qa.py`·`requirements.py`·`workflow_ast_context.py`)
  중 어느 것도 "omniroute"를 참조하지 않는다 — **RT-0001 Candidate 2
  non-trigger의 직접 증거**.
- `hqs/development/mvp/` 전수 검색 결과, 이 테스트 파일들 자신 외에
  `omniroute_engine`을 참조하는 파일이 없다 — 순수 additive 상태
  (기존 파이프라인에 아직 실제로 연결되지 않음) 확인.
- `omniroute_engine.py`의 실행 가능한 코드(statement)에
  `provider_connections`/`priority`/`fallback_chain`/`score`/
  `candidates`/`blockedProviders` 식별자가 없다(docstring의 설명
  문장은 제외 — 그 문장 자체가 `ADR-0017` §2.3의 Policy 소재
  결정을 인용하는 것이지 코드가 아니다).
- `omniroute_engine.py`가 공개 함수 `call_engine_via_omniroute` 하나만
  정의한다.
- `omniroute_engine.py`가 독립적으로 import 가능하다.

### 4.2 실행 결과 종합

| 검증 | 결과 |
|---|---|
| 로컬 test double 단위(7개) | **PASS** |
| Case A/RT-0001 정적 검증(7개) | **PASS** |
| 실제(격리) 서버 성공(`call_engine_via_omniroute`, `ollama-local` + 로컬 double) | **PASS** — `'ENGINE_REAL_INTEGRATION_OK'` 반환 |
| 실제(격리) 서버 오류 매핑(업스트림 500) | **PASS** — `RuntimeError`(HTTP 500 포함) |
| 실제(격리) 서버 timeout(진행 중 중단의 동기 등가, `call_engine_via_omniroute`가 노출하는 유일한 lifecycle) | **PASS** — `RuntimeError`("timed out" 포함) |
| 기존 `test_engine.py`(3개, `call_engine()` 자체) | **PASS**(무변경 재확인) |
| `hqs/development/mvp/tests/` 전체(Python 3.9 비호환 기존 5개 파일 제외) | **156 passed**(신규 17개 포함, 이중 게이트 설정) |
| Experimental 프로토타입(`projects/omniroute-thin-engine-caller-v1/tests/`) | **27 passed**(무변경 재확인) |

**cancellation lifecycle**: `call_engine_via_omniroute()`는 `call_engine()`과
동일하게 순수 동기 계약만 노출한다(기존 계약을 불필요하게 확장하지
않음, 사용자 지침 3). 비동기 상태 조회·명시적 `.cancel()` API는
Experimental 프로토타입(`caller.py`의 `OmniRouteCallHandle`)에만
존재하며, 이번 회귀(27/27)에서 그 lifecycle이 여전히 PASS함을
재확인했다 — 새로 만들지 않았다.

### 4.3 안전 조건

- 실제 provider egress: **0건**(모든 실제-서버 검증은 `ollama-local`
  + 이 세션이 직접 띄운 로컬 stdlib 서버만 대상).
- `blockedProviders`(non-video NOAUTH 12개) 사전 적용 후 read-only
  candidates endpoint로 0개 확인 — 이후에만 요청 전송(`test_omniroute_engine_real.py`
  fixture).
- 서버는 격리 인스턴스당 정확히 한 번만 기동(재기동 없음,
  `EVIDENCE-0004` 근본 원인 회피).
- 실제 `~/.omniroute/storage.sqlite` mtime(`1788605986`)·
  size(`2547712`) — 이번 작업 전체(구현+3회 이상의 테스트 실행)
  동안 완전히 동일하게 유지됨을 반복 확인.
- 잔여 프로세스/포트 점유: 매 검증 후 확인 결과 없음.

---

## 5. RT-0001 / `ADC-0010` / Architecture Freeze 최종 재확인(구현 이후)

| 대상 | 판정 | 근거 |
|---|---|---|
| RT-0001 Candidate 2("Engine 수 ≥2") | **미충족(무변경)** | `call_engine()`의 실제 호출 지점 5개 중 어느 것도 OmniRoute를 참조하지 않음(§4.1 실증) — 구현 후에도 여전히 정확히 1개 Engine만 대상 |
| `ADC-0010` C1 재검토 결합 조건 | **미충족(무변경)** | "Engine 수 ≥2" 미충족 + Kernel Module Defer 3건·ADC-01·02 여전히 Open — 결합 자체가 성립하지 않음 |
| `CONSTITUTION.md` Architecture Freeze | **충돌 없음** | `omniroute_engine.py`는 `ADR-0016`이 이미 부여한 Scoped 예외(Thin Engine Caller 형태) 범위 안 — Case A 조건(단일 함수, Policy 로직 0줄) 유지(§4.1) |
| Engine Adapter Contract(§14, `BASELINE.md`) | **변경 없음** | 새 Public Responsibility/Guarantee·함수 시그니처를 Contract에 추가하지 않았다. `call_engine_via_omniroute`는 Contract가 아니라 그 경계 안의 구현일 뿐이다 |
| `IMPLEMENTATION_RULES.md` 15·16·17·21행 | **충돌 없음** | 단일 함수, provider/routing/policy 로직 0줄(§4.1), Engine Gateway/Multi-Engine 추상화 없음 |

**결론**: 구현 착수 전 사전 확인(§2.2)의 판단이 실제 구현·테스트
결과로 그대로 확인됐다 — 구현 도중 어떤 시점에도 Trigger가
발생하지 않았고, 따라서 구현을 중단할 필요가 없었다.

---

## 6. Governance / Architecture 영향

- Architecture 변경: **없음**. Contract 변경: **없음**. Freeze 변경:
  **없음**. `CONSTITUTION.md`/`BASELINE.md`/`IMPLEMENTATION_RULES.md`/
  `ARCHITECTURE_GOVERNANCE.md` 어느 것도 이번 작업에서 수정하지
  않았다.
- `ADC-0027`~`ADC-0031`, `ADR-0015`~`ADR-0017`, `EVIDENCE-0001`~
  `EVIDENCE-0005` 파일: **무수정**.
- `hqs/development/mvp/engine.py`와 그 5개 호출부: **무수정**(git
  diff 0, §4.1이 실증).
- 새로 작성한 파일: `hqs/development/mvp/omniroute_engine.py` 1개,
  테스트 3개 + fixture 1개, 이 Evidence 문서 1개. 그 외 **없음**.
- 새 Jarvis측 Routing/Fallback/Gateway/Policy: **구현하지 않았다**
  (§4.1이 코드 수준에서 확인).

---

## 7. Open Issue 재분류

### 7.1 이번 작업으로 해소된 것

| 항목 | 상태 |
|---|---|
| `ADR-0017` §6.2 "실제 Production 배포"가 전혀 착수되지 않은 상태 | **부분 해소** — 실제(비-Experimental) Engine Adapter 모듈에 실제 OmniRoute 연결 함수가 존재하고 실제 서버로 검증됨. 단, 기존 5개 호출부의 전환(아래 §7.2)은 별도 사안으로 남아 있다 |
| "OmniRoute 연결이 real 실행 경로에서 실제로 동작하는가"(구조만, 실행 아님이었던 이전 Evidence들의 한계) | **해소** — `call_engine_via_omniroute()`가 real Engine Adapter 모듈에서 실제 격리 서버를 통해 success/error/timeout 3종 모두 확인됨(§4.2) |

### 7.2 새로 발생한 것(결함이 아니라 향후 결정 대상)

이 항목들은 **이번 구현의 결함이 아니다** — 의도적으로 보수적인
설계(§2.3)의 직접적 귀결이며, 사용자 지침 8("불필요한 Architecture/
Contract 변경 금지")·안전 원칙에 따라 이번 작업 범위 밖으로 남겼다.

1. **기존 5개 호출부(`agents/backend.py` 등)를 `call_engine_via_omniroute()`로
   전환할지 여부** — 순수하게 새로운 운영/설계 결정이다. 전환하면
   Development HQ의 실제 Dogfooding 작업 전체가 실제로 기동 중인
   OmniRoute 인스턴스(+ 올바른 `blockedProviders`/`REQUIRE_API_KEY`
   설정)에 의존하게 된다 — 이는 이번 작업이 검증한 범위(격리된
   controlled 환경)를 넘어서는 별도의 운영 리스크 판단이 필요한
   결정이며, 이 Evidence는 그 결정을 내리지 않는다.
2. **`OMNIROUTE_MODEL` 기본값 `"auto"`를 실제 운영 환경에서 사용할
   때의 안전장치 확인 책임 소재** — `omniroute_engine.py`의
   docstring이 운영자 책임(OmniRoute 쪽 `blockedProviders`/
   `REQUIRE_API_KEY` 사전 구성)으로 명시했으나, 이 요구사항이 실제로
   충족됐는지 자동으로 확인하는 코드는 없다(Jarvis 코드가 그 확인을
   구현하면 곧 Policy 판정 로직이 되어 Case A를 벗어난다 —
   `ADR-0017` §2.4). 실제 운영 전 사람이 직접 확인해야 한다.

### 7.3 무변경으로 유지되는 기존 항목(재확인, 새 Issue 아님)

`EVIDENCE-0005` §12가 이미 분류한 6개 항목(Audit Policy 공백,
`priority` tie-break UNVERIFIED, `domain_budgets` semantics 전체,
`ADC-0010`/`RT-0001` 미충족, ADC-01·ADC-02·`ADC-0003`판단4 Open)은
이번 작업으로 전혀 변경되지 않았다 — §5가 그중 RT-0001/`ADC-0010`
부분을 구현 이후 시점 기준으로 재확인했을 뿐이다.

---

## 8. Provenance / Reproducibility

- **로컬 단위/정적 테스트**: `python3 -m pytest
  hqs/development/mvp/tests/test_omniroute_engine.py
  hqs/development/mvp/tests/test_omniroute_engine_boundary.py -v`
  (의존성 설치 불필요, stdlib만 사용) → `14 passed`.
- **실제 서버 통합 테스트**: `RUN_REAL_OMNIROUTE_TESTS=1
  I_UNDERSTAND_REAL_EGRESS_RISK=1 python3 -m pytest
  hqs/development/mvp/tests/test_omniroute_engine_real.py -v` →
  `3 passed`(격리 `DATA_DIR`, `OMNIROUTE_PKG_DIR` 기본값은
  이전 세션이 캐시해 둔 volatile scratchpad 경로 — `EVIDENCE-0001`
  §1.1과 동일한 재현성 한계).
- **전체 mvp 회귀**: `python3 -m pytest hqs/development/mvp/tests/ -q
  --ignore=.../test_cli_integrated.py --ignore=.../test_stage_01.py
  --ignore=.../test_stage_04.py --ignore=.../test_workflow_ast_context.py
  --ignore=.../test_workflow_integrated.py`(이 5개는 Python 3.9
  환경에서 `X | None` PEP604 문법 미지원으로 인한 **기존
  collection 오류** — 이번 작업과 무관, git diff로 무수정 확인) →
  이중 게이트 설정 시 `156 passed`.
- **Experimental 프로토타입 회귀**: `python3 -m pytest
  projects/omniroute-thin-engine-caller-v1/tests/ -q`(이중 게이트) →
  `27 passed`.
- **cleanup**: 모든 실제 서버·로컬 double 프로세스 PID 기준 종료
  확인, `lsof`로 포트 미점유 확인, 실제 `~/.omniroute/storage.sqlite`
  mtime/size 작업 전후 동일 확인(반복 3회 이상).

## Self Review

- 구현 전 `call_engine()` 구조와 Engine Adapter Contract를
  확인했는가 — **Pass**(§2.1).
- RT-0001/`ADC-0010` 조건을 구현 전에 확인했는가 — **Pass**(§2.2,
  설계 자체가 그 확인의 직접 결과다).
- 실제 연결로 Trigger가 발생했는가 — **아니오**(§5, 구현 후
  재확인까지 완료) — 따라서 중단·별도 보고 대상이 아니다.
- `call_engine()`의 외부 계약·호출 의미를 변경했는가 — **아니오**
  (§3.2, §4.1 — git diff 0, 5개 호출부 무수정).
- Jarvis가 provider/model 선택·routing·fallback·budget/policy를
  직접 구현했는가 — **아니오**(§4.1 정적 검증).
- 기존 Case A Boundary·cancellation/status/error mapping·27/27·
  zero-egress 안전조건이 보존됐는가 — **Pass**(§4.2, §4.3 — 전부
  무변경 재확인).
- 실제 provider egress가 필요한 검증을 수행했는가 — **아니오**
  (§4.3 — 전부 local/controlled).
- Architecture/Contract/Freeze 변경이 필요했는가 — **아니오**(§5·§6).
- 기존 Open Issue 해소와 신규 Issue를 구분했는가 — **Pass**(§7.1
  vs §7.2, §7.3).
- `ADC-0027`~`ADC-0031`, `ADR-0015`~`ADR-0017`,
  `EVIDENCE-0001`~`EVIDENCE-0005`를 수정했는가 — **아니오**.
- commit/push/PR을 수행했는가 — **아니오**.
