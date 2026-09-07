# EVIDENCE: omniroute-thin-engine-caller-v1

자립 Evidence 문서 — Governance 문서가 아니다. 실제 실행 결과를 있는
그대로 기록한다. 판단(PASS/FAIL 그 이상의 Architecture 결론)은 여기서
내리지 않는다 — 그 판단은 이번 작업의 최종 보고와 향후 Governance
검토의 몫이다.

## 검증 목적

`ADR-0016`이 Architecture/Governance 관점에서 열어 둔 OmniRoute Thin
Engine Caller 구현이, 실제로 (1) Case A 경계를 지키는 코드로
작성됐는지, (2) 정상 응답·오류 전달·cancellation/status lifecycle을
올바르게 처리하는지, (3) 실제 OmniRoute Engine 호출로도 재현되는지
확인한다.

## 격리 조건

| 항목 | 값 |
|---|---|
| 실행 환경 | macOS(darwin), Python 3.9.6 stdlib, Node.js(OmniRoute 3.8.50) |
| OmniRoute 패키지 | 이전 세션이 캐시해 둔 npm 패키지(volatile scratchpad 경로, `EVIDENCE-0001` §한계와 동일 성격) |
| 실제 계정/자격증명 | 사용하지 않음(fake API key만 사용) |
| DATA_DIR | 모든 실제 서버 실행에서 임시 디렉터리로 격리, 실행 후 삭제 |
| 실제 `~/.omniroute` | 매 실행 전후 mtime/size 대조로 미접촉 확인 |

## Part 1 — 단위/lifecycle/Case A boundary 테스트 (로컬 test double)

실행 커맨드:

```
python3 -m pytest projects/omniroute-thin-engine-caller-v1/tests/test_caller_unit.py \
  projects/omniroute-thin-engine-caller-v1/tests/test_caller_lifecycle.py \
  projects/omniroute-thin-engine-caller-v1/tests/test_case_a_boundary.py -v
```

결과(2026-09-07 실제 실행, 그대로 기록):

```
26 passed in 10.78s
```

- `test_caller_unit.py`(13개): 정상 응답 파싱, request body/헤더
  변환 정확성, `model` 기본값(`auto`), HTTP 401/403/429/500/503/400
  → 타입별 예외 매핑, 잘못된 응답 형태 처리, 연결 거부, timeout,
  env var 기반 설정 — 전부 PASS.
- `test_caller_lifecycle.py`(5개): 비동기 성공/실패 상태 전이, 취소
  전/후 동작, `result()` 대기 시간 초과 — 전부 PASS.
- `test_case_a_boundary.py`(8개): 단일 파일 구성, 두 번째 Engine
  hardcode 없음, provider/routing/우선순위 관련 식별자·정렬 호출
  없음, 일반화된 Gateway/Adapter 추상화 없음, 네트워크 호출 지점
  1곳, `call_engine` import/호출 없음, `hqs/` 아래에서 이 프로젝트를
  참조하는 파일 없음, 독립 import 가능 — 전부 PASS.

이 26개는 모두 **로컬 test double**(`tests/fake_server.py`) 또는
정적 분석 기준이며, 실제 OmniRoute 서버·실제 네트워크 egress를
전혀 쓰지 않는다.

## Part 2 — 실제(격리) OmniRoute 서버 프로브와 안전 사고

### 프로브 1 (구현 착수 전 사전 조사)

임시 `DATA_DIR`, provider connection 0개, `OMNIROUTE_API_KEY=probe-
fake-key-0001`로 서버를 띄우고 `/api/v1/chat/completions`에
`model:"auto"`로 2회 요청(하나는 올바른 fake key, 하나는 의도적으로
틀린 key)을 보냈다.

**관찰**: 둘 다 HTTP 200 반환. 서버 로그:

```
[clientApiPolicy] invalid bearer presented to /api/v1/chat/completions but REQUIRE_API_KEY=false — falling through to anonymous (key_id=key_-key)
...
Auto selection: oc/big-pickle | ... 
oc/big-pickle → opencode/big-pickle
Using opencode account: ***...
[ProxyEgress] opencode status=success
Model oc/big-pickle succeeded (940~2062ms, 0 fallbacks)
```

**판정**: provider connection이 하나도 없어도, `REQUIRE_API_KEY=false`
설정(이 서버의 기본값으로 보임)에서는 인증 실패조차 dispatch를 막지
못하며, OmniRoute 패키지에 내장된 기본 "opencode" 계정으로 **실제
egress 호출**이 발생한다. 이는 이 세션 전체가 유지해 온 "실제
provider 호출 금지" 경계를 의도치 않게 2회 넘은 것이다. 비용 발생
여부는 확인할 수 없다(사용자 자격증명이 아니라 OmniRoute 번들 기본
계정이 사용됨).

**조치**: 즉시 `kill -9`로 서버 종료, 임시 디렉터리 삭제, 실제
`~/.omniroute/storage.sqlite` mtime(`Sep 5 19:59`)·size(`2547712`)
불변 확인. 사용자에게 즉시 보고하고 이후 실제 Engine 호출 범위를
좁히는 데 합의를 구했다(대화 기록, 2026-09-07).

### 프로브 2 (`domain_budgets` 차단 경로 재현 시도)

합의된 좁은 범위(dispatch 이전에 차단되는 `domain_budgets` 초과
경로만 실제 서버로 검증)에 따라 `test_real_engine_budget_block.py`를
작성해 실행했다: 서버를 세우고 종료한 뒤, 격리된 `storage.sqlite`에
`domain_budgets`(daily_limit_usd=0.01)·`domain_cost_history`
(cost=999.0, api_key_id='env-key') 행을 직접 삽입하고, 완전히 새
PID로 서버를 재기동한 뒤 `call_omniroute()`로 요청했다.

**관찰**: 기대(HTTP 429 → `OmniRouteBudgetExceededError`)와 달리
`DID NOT RAISE` — 요청이 실제로 dispatch까지 진행되어 서버 로그에
다시 `Using opencode account`/`Auto selection: oc/big-pickle`이
찍혔다. **실제 egress가 3번째로 발생했다.**

**원인**: 진단하지 못함(스키마 불일치 추정 — 예: `env-key`가 실제
API Key 식별자와 일치하지 않거나, `domain_budgets` 필수 컬럼 중
하나가 누락돼 조회 조건에 걸리지 않았을 가능성). **추가 재시도는
같은 위험을 반복하므로 중단했다.**

**조치**: `finally` 블록이 새 PID를 즉시 `kill -9`, 임시 디렉터리는
pytest가 자동 정리, 실제 `~/.omniroute/storage.sqlite` mtime/size
불변 재확인(테스트 완료 후 `ps aux`로 프로세스 잔존 여부, `lsof`로
포트 점유 여부까지 확인 — 둘 다 깨끗함). `test_real_engine_budget_block.py`
에 이중 opt-in 게이트(`RUN_REAL_OMNIROUTE_TESTS=1` +
`I_UNDERSTAND_REAL_EGRESS_RISK=1`)를 추가해 재실행을 잠갔다.

## Final Judgment

| 검증 대상 | 방법 | 결과 |
|---|---|---|
| Request/Response 변환 정확성 | 로컬 test double | **PASS**(실제 실행 확인) |
| 오류 코드 → 타입 예외 매핑(401/403/429/5xx/4xx/timeout/connection) | 로컬 test double | **PASS**(실제 실행 확인) |
| Cancellation/Status lifecycle | 로컬 test double | **PASS**(실제 실행 확인) |
| Case A 경계(단일 함수, Policy 로직 없음, Gateway 없음) | 정적 분석(AST/grep) | **PASS**(실제 실행 확인) |
| 실제 OmniRoute Engine을 통한 정상 응답 | (계획했으나 미실행) | **시도 안 함** — 안전 사고 이후 로컬 double로 대체 |
| 실제 OmniRoute Engine을 통한 오류 전달(dispatch 이전 차단) | 실제 격리 서버 | **UNVERIFIED** — 재현 실패, 원인 미진단, 재시도 중단 |

**과장 방지**: 위 표의 "Case A 경계 PASS"는 이 모듈의 **코드 구조**가
Case A 조건을 지킨다는 것만 의미한다 — OmniRoute 실제 서버와의
end-to-end 상호작용이 Case A 조건 아래에서 항상 안전하다는 뜻이
아니다(프로브 1·2가 보여주듯, OmniRoute 쪽의 zero-config 기본 동작은
Jarvis 쪽 코드 구조와 무관하게 실제 egress를 발생시킬 수 있다 —
이것은 Thin Caller 코드의 결함이 아니라 OmniRoute 서버 자체의 zero-
config 기본값에서 비롯된 별개의 관찰이다).

## 이 Evidence가 답하지 않는 것

- OmniRoute의 zero-config 기본 egress 동작이 사용자의 실제(로컬)
  설치 환경에서도 동일한지 — 이번 프로브는 격리된 임시 인스턴스
  기준이다.
- `domain_budgets` 차단 로직 자체의 정확성 — `EVIDENCE-0002`가 이미
  다른 삽입 방식으로 이를 PASS 확인한 바 있다(이번 실패가 그 결과를
  뒤집지 않는다 — 이번 실패는 이 프로젝트의 삽입 스크립트 문제일
  가능성이 더 높다, 미진단).
- Production Adoption 여부 — 이 Evidence는 Experimental 프로토타입
  범위에 한정된다.

## Open Issues

1. `test_real_engine_budget_block.py`가 실제로 왜 budget 차단을
   트리거하지 못했는지 미진단 — 재시도 전 소스 레벨 재확인 필요.
2. OmniRoute의 zero-config 기본 egress 동작("opencode" 내장 계정,
   `REQUIRE_API_KEY=false` 기본값)은 이번 작업 범위 밖의 별도 관찰
   사항이다 — Jarvis가 향후 실제 caller를 배포할 때 이 기본값을
   명시적으로 비활성화(예: 실제 provider connection을 반드시
   등록하도록 강제)해야 하는지는 별도 검토 대상이다.
3. `RT-0001` "Engine 수 ≥ 2" 후보 — 이 프로토타입의 존재 자체가
   `ADC-0027` §Risks가 예고한 이 신호에 해당할 수 있다(아래 최종
   보고 참조).

## Provenance / Reproducibility

- 단위/lifecycle/boundary 테스트: `python3 -m pytest
  projects/omniroute-thin-engine-caller-v1/tests/ --ignore=.../test_real_engine_budget_block.py -v`
  (의존성 설치 불필요, stdlib만 사용).
- 실제 서버 프로브 1·2의 정확한 기동 커맨드·삽입 SQL은
  `test_real_engine_budget_block.py`의 fixture/테스트 본문에 그대로
  남아 있다 — 단, 위 경고에 따라 이중 게이트 없이 재실행하지 않는다.
