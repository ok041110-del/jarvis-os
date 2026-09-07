# omniroute-thin-engine-caller-v1 (Experimental)

OmniRoute를 Jarvis OS의 단일 Implementation Engine으로 호출하는
**Thin Engine Caller**(Case A, `ADC-0031` §Q1)를 구현하고, 그 경계가
실제로 지켜지는지 검증한다.

- **Owner**: Claude Code (세션 2026-09-07)
- **레인**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
  Implementation" — "격리된 실행 환경에서의 구현", "테스트용 실행",
  "성능/신뢰성/경계 검증"에 해당. `hqs/development/`·`hqs/investment/`
  production path 무연결(`test_case_a_boundary.py`가 이를 정적으로
  확인한다). Formal Contract·Frozen Boundary 무변경, 저장소 의존성
  매니페스트 무변경(stdlib만 사용).
- **근거**: `docs/architecture/core/ADC-0027`~`ADC-0031`,
  `docs/architecture/core/ADR-0015`, `docs/architecture/core/ADR-0016`
  (Freeze Scoped 예외), `EVIDENCE-0001`, `EVIDENCE-0002`.
- **산출물**: `EVIDENCE.md`(자립 Evidence — Governance 문서 아님).

## 이것이 하지 않는 것

OmniRoute Production Adoption 완료 선언 아님(`ADR-0016` §9가 요구하는
Integration Validation·Final Adoption Review는 여전히 별도 절차).
Engine Gateway·Multi-Engine abstraction·Jarvis 자체 Routing/Policy
layer 아님. `hqs/development/mvp/engine.py`의 `call_engine()`을
대체·수정하는 것 아님(완전히 별개 경로, read-only조차 아니고 아예
참조하지 않는다). Provider/Model 선택·우선순위·fallback 판단 아님 —
전부 OmniRoute 책임으로 남긴다.

## 구조

- `caller.py` — Thin Caller 본체. `call_omniroute()`(동기),
  `call_omniroute_async()`+`OmniRouteCallHandle`(비동기, 상태 조회·
  취소). 외부 의존성 없음(stdlib `http.client`만 사용).
- `tests/fake_server.py` — 로컬 test double(stdlib `http.server`).
  실제 OmniRoute가 아니라 OpenAI-compatible 응답 형태를 흉내 낸
  결정론적 fixture.
- `tests/test_caller_unit.py` — request 변환·response 파싱·오류 코드
  매핑 단위 테스트(test double 사용, 네트워크 egress 없음).
- `tests/test_caller_lifecycle.py` — 비동기 상태 조회·취소 lifecycle
  테스트(test double 사용).
- `tests/test_case_a_boundary.py` — Thin Caller가 Case A 범위를
  지키고 Jarvis Routing/Gateway가 없음을 정적(AST/grep)으로 검증.
- `tests/test_real_engine_budget_block.py` — 실제 격리 OmniRoute
  서버로 `domain_budgets` 차단 경로만 검증하려 한 시도. **현재 알려진
  실패 상태**(아래 "실제 Engine 호출 범위와 안전 사고" 참조) — 이중
  opt-in 게이트로 잠가 뒀다.

## 환경 변수(최소 범위)

기존 저장소에 HTTP client 라이브러리·설정 파일 convention이 없어
(`requests`/`httpx` 미설치, 저장소 전체에 사용 사례 없음) stdlib만
쓰고, 설정은 OmniRoute 자신이 이미 문서화한 이름과 일치시켰다
(`.claude/docs/integrations/omniroute.md`, `OMNIROUTE_API_KEY`는
OmniRoute 소스가 실제로 읽는 env var — 이전 세션 `EVIDENCE-0001`/
`EVIDENCE-0002`에서 확인).

| 변수 | 기본값 | 용도 |
|---|---|---|
| `OMNIROUTE_BASE_URL` | `http://127.0.0.1:20128` | OmniRoute 서버 주소 |
| `OMNIROUTE_API_KEY` | (없음) | Authorization Bearer 토큰 |

새 설정 파일·새 의존성·새 CI 스텝을 추가하지 않았다.

## 실행

```bash
# 로컬 검증(권장, 안전 — 기본 실행 대상)
python3 -m pytest projects/omniroute-thin-engine-caller-v1/tests/ \
  --ignore=projects/omniroute-thin-engine-caller-v1/tests/test_real_engine_budget_block.py -v
```

`test_real_engine_budget_block.py`는 기본적으로 SKIP되며, 아래
"실제 Engine 호출 범위와 안전 사고" 절을 읽지 않고는 실행하지 않는다.

## 실제 Engine 호출 범위와 안전 사고 (중요)

이 구현 세션 중, 완전히 격리된 임시 `DATA_DIR`(provider connection
0개, 잘못된 API Key 포함)로 실제 OmniRoute 서버에 `model:"auto"`
요청을 보내는 것만으로 **OmniRoute 패키지에 내장된 기본("opencode")
계정을 통한 실제 egress 호출이 발생**한다는 것을 발견했다(호출
지연 900~2000ms, 서버 로그 `Using opencode account`/`[ProxyEgress]
opencode status=success`). 이는 provider connection이 전혀 없어도,
`REQUIRE_API_KEY=false`인 이 서버 설정에서는 인증 실패조차 dispatch
를 막지 않기 때문이다.

이 발견에 따라 사용자와 협의해 실제 Engine 호출 검증 범위를 다음과
같이 좁혔다.

1. **정상 응답(success)**: 로컬 test double로만 검증. "OmniRoute가
   실제로 좋은 응답을 준다"는 주장은 하지 않는다 — Caller의 request
   구성·response 파싱 로직만 검증한다.
2. **오류 전달 중 dispatch 이전 차단**: `domain_budgets` 초과 429
   경로만 실제 서버로 검증 시도(egress 없음이 사전 조건).
3. **cancellation/status**: 로컬 test double로만 검증.

**그러나 2번 시도가 실제로는 실패했다** — `domain_budgets`/
`domain_cost_history`에 삽입한 행이 실제 예산 차단 로직을 트리거하지
못했고, 요청이 dispatch까지 진행되어 **의도치 않은 실제 egress가
다시 발생했다**(이 세션에서 총 3회: 최초 프로브 2회 + 이 시도 1회).
원인은 진단하지 못했다(스키마 불일치로 추정 — 재시도 자체가 같은
위험을 반복하므로 추가 시도를 중단했다).

**결론**: 이 프로젝트는 "실제 Engine 호출을 통한 오류 전달 검증"
요구사항을 **부분적으로만 충족**한다 — dispatch 이전 차단 경로는
UNVERIFIED로 남는다(`EVIDENCE.md` §Final Judgment 참조).
`test_real_engine_budget_block.py`는 이중 opt-in 게이트
(`RUN_REAL_OMNIROUTE_TESTS=1` + `I_UNDERSTAND_REAL_EGRESS_RISK=1`)
없이는 절대 실행되지 않으며, 원인 진단 없이 재실행하지 않는다.

## 성공 / 실패 / SKIP / 폐기 기준

- **성공**: 단위·lifecycle·Case A boundary 테스트 전부 PASS(달성,
  26/26).
- **실패**: 실제 서버 대상 budget 차단 재현(달성 못함, 위 참조).
- **SKIP**: `test_real_engine_budget_block.py`는 이중 게이트 미설정 시
  기본 SKIP(설계된 안전 기본값).
- **폐기**: 후속 ADR/ADC가 실제 caller 구현 위치·형태를 별도로
  확정하면, 이 프로토타입은 그 결정에 맞춰 대체되거나 폐기될 수
  있다(`ARCHITECTURE_GOVERNANCE.md` "Experimental").
