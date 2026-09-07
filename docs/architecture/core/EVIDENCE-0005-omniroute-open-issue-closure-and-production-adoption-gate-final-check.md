# EVIDENCE-0005: OmniRoute Open Issue 전수 종결과 Production Adoption Gate 최종 점검

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. `EVIDENCE-0001`~`EVIDENCE-0004`, `ADC-0027`~`ADC-0031`,
`ADR-0015`~`ADR-0016`을 수정하지 않고, 이번에 새로 수행한 정리
작업의 결과만 **독립된 문서**로 기록한다.

## 1. 검증 목적

지금까지의 OmniRoute 트랙 전체(`RFC-0023` → `ADC-0027`~`ADC-0031` →
`ADR-0015`~`ADR-0016` → `EVIDENCE-0001`~`EVIDENCE-0004`)에 남아 있는
Open Issue를 전수 재검토하고, 그중 이번 세션이 실제로 종결할 수 있는
항목을 종결한다. 구체적으로:

1. `test_real_engine_budget_block.py`가 여전히 구식(정지→삽입→
   재기동) 방법론을 쓰던 문제를 갱신 또는 폐기로 판정하고 실행한다.
2. Production Adoption 전제조건을 문서별로 대조해 미충족 항목을
   전수 검사한다.
3. `blockedProviders`/`REQUIRE_API_KEY`/zero-config egress 방어
   상태가 기존 Evidence와 여전히 일치하는지 read-only로 재확인한다.
4. 기존 26/26·Case A·실제 Engine lifecycle·`domain_budgets` PASS
   상태가 회귀하지 않았는지 재확인한다.

이 문서는 새로운 Architecture Decision을 만들지 않는다 — Governance
절차가 필요하다고 판단되는 항목은 **종결하지 않고 별도 Decision
대상으로 명시적으로 분리**한다(§3, §8).

## 2. 격리 조건

`EVIDENCE-0004` §2와 동일한 조건을 그대로 적용한다.

| 항목 | 값 |
|---|---|
| OmniRoute 버전 | `3.8.50` standalone(`dist/server.js`), 이전 세션 캐시(volatile scratchpad) |
| `DATA_DIR` | 매 인스턴스마다 새 temporary directory, 실제 `~/.omniroute`와 완전 분리 |
| 인증 | test-only fake key만 사용 |
| 실제 provider egress | **0건** — 모든 dispatch 검증은 로컬 stdlib 서버(`127.0.0.1:11434`) 대상 |
| 재기동 | `domain_budgets` 관련 모든 테스트에서 서버를 **정확히 한 번만** 기동, 재기동 없음(`EVIDENCE-0004` §3.2 원인 회피) |
| 실제 `~/.omniroute` 영향 | 검증 시작 전/각 단계 종료 후/최종 종료 후 3회 이상 mtime(`1788605986`)·size(`2547712`) 동일 확인 |

---

## 3. Open Issue 전수 재검토

`EVIDENCE-0001` §4, `EVIDENCE-0002` §7, `EVIDENCE-0003` Final
Judgment·"답하지 않는 것", `EVIDENCE-0004` §9, `ADR-0015` §12,
`ADR-0016` §12에 흩어진 모든 항목을 한 표로 모았다. **분류** 열은
세 값 중 하나다 — **CLOSED**(이번 작업으로 종결), **BY-DESIGN**(원
문서가 이미 "Adoption precondition 아님"으로 확정한 항목 — 종결
대상 자체가 아니다), **GOVERNANCE-REQUIRED**(종결하려면
Architecture/Baseline/Contract 변경이 필요해 이번 작업이 손대지
않고 별도 Decision으로 남긴 항목).

| # | 출처 | 항목 | 분류 | 근거 |
|---|---|---|---|---|
| 1 | `EVIDENCE-0003`§5, `EVIDENCE.md`§Open Issues 1 | `domain_budgets` 재현 실패 원인 미진단 | **CLOSED** | `EVIDENCE-0004`§3이 health-check-repair를 근본 원인으로 확정, 재기동 없는 삽입으로 재현 |
| 2 | `EVIDENCE.md`§Final Judgment, `EVIDENCE-0003`§7 | 실제 Engine 성공 응답 lifecycle 미시도 | **CLOSED** | `EVIDENCE-0004`§5.2 — `caller.py` 직접 호출로 확인 |
| 3 | `EVIDENCE.md`§Final Judgment, `EVIDENCE-0003`§7 | 실제 Engine 오류 전달 lifecycle 미시도 | **CLOSED** | `EVIDENCE-0004`§5.3 |
| 4 | (`EVIDENCE-0003`까지 test double로만 확인) | 실제 Engine cancellation lifecycle 미확인 | **CLOSED** | `EVIDENCE-0004`§5.4 |
| 5 | `EVIDENCE.md`, `README.md` | `test_real_engine_budget_block.py`가 구식 방법론(정지→삽입→재기동) 사용 | **CLOSED**(이 문서) | §4·§5 — 새 방법론으로 갱신, 실제 실행 2회 PASS |
| 6 | `ADC-0027`§Q4, `ADC-0030` | `priority` tie-break이 실제 dispatch selection에 미치는 영향 | **BY-DESIGN** | `ADC-0030`이 Responsibility redesign으로 Adoption precondition에서 이미 제외 — Jarvis가 그 tie-break을 사용/재구현하지 않으므로 검증 대상 자체가 아니다 |
| 7 | `ADC-0029`§Q3 | `routing_decisions` score/factors durable 부재(Audit gap) | **BY-DESIGN** | `ADC-0029`가 이미 제외 — OmniRoute 업스트림 이슈이며 Jarvis 쪽 명시적 Audit requirement가 없다 |
| 8 | `ADC-0028` | `domain_fallback_chains` dead code 상태 | **BY-DESIGN** | `ADC-0028`이 이미 제외 — 실제 fallback execution은 별도 메커니즘이 담당한다고 확인됨 |
| 9 | `EVIDENCE-0002`§9 | `domain_budgets` semantics 전체(warning threshold, 기간 리셋, 복수 API key, DB-backed key 경로) 미검증 | **BY-DESIGN** | `ADC-0027` 선행조건 3은 "초과 시 차단 여부의 확정"만 요구했다 — 이미 `EVIDENCE-0002`/`EVIDENCE-0004`로 충족. 이 항목들은 애초에 Adoption precondition에 포함된 적이 없다 |
| 10 | `EVIDENCE-0004`§3.4 | 대조군(budget 충분) 케이스를 재기동 없이 재현하는 것의 잔여 한계 | **BY-DESIGN** | `EVIDENCE-0002` Process B(별도 fresh 프로세스)가 이미 이 형태의 대조를 PASS로 확인했다 — 이번 두 UNVERIFIED 항목의 판정 범위 밖 |
| 11 | `EVIDENCE-0004`§9 | health-check-repair의 정확한 트리거 조건(소스 미규명) | **BY-DESIGN** | OmniRoute 컴파일 전용 동작, 소스 미배포 — Jarvis 쪽에서 해소할 수 있는 공백이 아니다. 회피 방법(재기동 없는 삽입)은 이미 확립·검증됨 |
| 12 | `ADR-0016`§12 항목4, `ADC-0031`§Out of Scope | Routing/Cost/Audit Policy가 Jarvis 코드로 구현돼야 하는지, OmniRoute 설정으로 존재해도 되는지 | **GOVERNANCE-REQUIRED** | 실제 Production caller **설계** 시점의 판단 대상으로 `ADC-0031`이 명시적으로 위임했다 — 지금 이 판단을 내리면 새로운 Responsibility 배분을 이 문서가 임의로 확정하는 것이 되어 §7 지시(새 Routing/Policy 미구현) 위반이다 |
| 13 | `ADR-0016`§12 항목5, `ADC-0027`§Next Step 2 | `BASELINE.md` §14.1("Engine 호출 책임=미결")·§16.2 실제 텍스트 갱신 | **GOVERNANCE-REQUIRED** | Baseline 문서 수정은 RFC → ADC → ADR 절차 대상이다(`CONSTITUTION.md` Governance Loop). 이 문서가 직접 수정하면 절차를 우회하게 된다 |
| 14 | `ADR-0015`§5, `ADR-0016`§9 | "Final Adoption Review" 공식 선언 및 Production 배포 승인 | **GOVERNANCE-REQUIRED** | 아래 §8에서 사실관계(3단계 중 1·2 완료)만 정리한다 — "Adoption 완료"라는 **선언**은 Governance 절차의 몫이며 Evidence 문서의 권한 밖이다(`ADR-0015`§9, `ADR-0016`§9가 반복 명시) |
| 15 | `ADR-0015`§13 항목8 | `ADC-0003`판단4, `ADC-01`·`ADC-02`·`ADC-07`(Open) | **BY-DESIGN**(무관) | 이 트랙(`RFC-0023`~) 시작부터 명시적으로 범위 밖이다 — 이번 작업도 재론하지 않는다 |

**결과**: 15개 항목 중 **5개 CLOSED**(#1~5, 전부 이번 세션에서 실제
실행으로 종결), **7개 BY-DESIGN**(#6~11, #15 — 애초에 "Adoption
precondition"이 아니었던 항목이므로 종결 대상 자체가 아니다),
**3개 GOVERNANCE-REQUIRED**(#12~14 — 종결하려면 Architecture Decision
또는 Baseline 변경이 필요해 이번 작업이 의도적으로 손대지 않았다).

**"Open Issue 0개"의 정확한 의미**: 이 트랙의 **검증 공백**(실제
실행으로 확인 가능한 미해결 사실)은 이번 작업으로 0개가 됐다(#1~5
CLOSED). #6~11·#15는애초에 결함이 아니라 다른 문서가 이미 내린
설계상 결정이므로 "열려 있는 이슈"로 세는 것 자체가 부정확하다.
#12~14는 진짜로 남아 있지만, 이들은 "검증 공백"이 아니라 **다음
Governance 단계로 넘어가기 위한 절차적 전제**다 — 사용자 지시
§7("Architecture/Contract/Freeze 변경이 필요하면 즉시 중단하고
별도 Decision으로 보고")에 따라 이 문서는 이들을 종결하지 않고
명시적으로 별도 보고한다(§9 최종 보고 참조).

---

## 4. `test_real_engine_budget_block.py`: 갱신 판정

### 4.1 판단

**갱신한다(폐기하지 않는다).**

### 4.2 근거

- `EVIDENCE-0004` §3.3이 "재기동 없이 별도 `sqlite3` 연결로 실행 중인
  서버에 직접 삽입"하는 방법론을 이미 **실행으로 확정**했다 — 이는
  임시방편이 아니라 재현 가능한 절차다.
- 이 방법론은 기존 파일의 안전장치(이중 opt-in 게이트, `blockedProviders`/
  `domain_budgets` 이중 방어, 격리 `DATA_DIR`, 실제 `~/.omniroute`
  mtime/size 대조)와 완전히 호환된다 — 안전 설계를 다시 만들 필요가
  없었다.
- 폐기하면 "실제 서버를 통한 `domain_budgets` 차단 재현"이라는
  **자동화되고 재현 가능한 회귀 테스트**가 사라지고, `EVIDENCE-0004`의
  ad-hoc scratchpad 재현(문서로만 남고 코드로 재실행 불가능)만 남는다
  — 이는 `CONSTITUTION.md` Evidence Review 원칙("재현 가능한 형태로
  기록")에 역행한다.
- 갱신 비용이 낮다 — 새 Architecture나 새 안전 메커니즘을 설계할
  필요 없이, 이미 검증된 절차를 코드로 옮기는 것뿐이다.

### 4.3 실제 변경 내용

`projects/omniroute-thin-engine-caller-v1/tests/test_real_engine_budget_block.py`
전체를 재작성했다.

- **제거**: `proc.kill()` → 삽입 → `new_proc = subprocess.Popen(...)`
  재기동 패턴(구 버전 183~222행) 전체.
- **추가**: 서버를 fixture에서 **정확히 한 번**만 기동하고, 테스트
  본문은 그 프로세스를 살려 둔 채 별도 `sqlite3` 연결(`_sqlite_exec()`)
  로 `domain_budgets`/`domain_cost_history`를 삽입한다.
- **추가(2차 방어, defense-in-depth)**: `blockedProviders`에
  non-video NOAUTH provider 12개를 먼저 적용하고, dispatch를
  유발하지 않는 `GET /api/v1/auto-combo/auto/candidates`로 candidate
  수가 `0`인지 **먼저** 확인한 뒤에만 budget-exceeded 요청을
  보낸다 — 1차 방어(budget 차단)가 실패하더라도 실제 egress로
  이어지지 않도록 이중화했다.
- **유지(무변경)**: 이중 opt-in 게이트(`RUN_REAL_OMNIROUTE_TESTS=1`
  + `I_UNDERSTAND_REAL_EGRESS_RISK=1`), 격리 `DATA_DIR`, test-only
  fake API key, 실제 `~/.omniroute` mtime/size 대조 assertion,
  로그에 `ProxyEgress`/`Auto selection:` 부재를 확인하는 FAIL
  조건.

---

## 5. 실제 실행 결과

```
RUN_REAL_OMNIROUTE_TESTS=1 I_UNDERSTAND_REAL_EGRESS_RISK=1 \
  python3 -m pytest projects/omniroute-thin-engine-caller-v1/tests/test_real_engine_budget_block.py -v
```

| 실행 | 결과 |
|---|---|
| 1회차(단독) | `1 passed in 4.60s` |
| 2회차(독립 재현성 확인, 완전히 새 격리 인스턴스) | `1 passed in 2.97s` |
| 게이트 미설정 시(기본 실행) | `1 skipped`(SKIP, FAIL 아님 — 설계된 안전 기본값) |
| 전체 스위트(26개 로컬 + 이 1개, 이중 게이트 설정) | `27 passed in 13.83s` |

두 실행 모두 서버 로그에 `ProxyEgress`/`Auto selection:` **0건**,
`blockedProviders` 적용 후 candidate 수 **0개**를 확인했다. 매 실행
전후 실제 `~/.omniroute/storage.sqlite` mtime(`1788605986`)·
size(`2547712`) 완전 동일을 재확인했다.

---

## 6. `blockedProviders`/`REQUIRE_API_KEY`/zero-config egress 재확인(Read-only)

`EVIDENCE-0003`이 인용한 소스 지점을 이번에도 **read-only(grep/Read만,
서버 미기동)**로 재대조했다 — 캐시된 패키지가 이전 세션 이후
수정되지 않았으므로 드리프트 여부만 확인하면 충분하다는 판단이다.

| 대상 | `EVIDENCE-0003` 인용 | 이번 재확인 | 일치 여부 |
|---|---|---|---|
| `REQUIRE_API_KEY` 기본값 | `defaultValue: "false"`, `category: "security"`, `warningLevel: "caution"` | `featureFlagDefinitions.ts` 동일 값 재확인 | **일치** |
| `AUTO_COMBO_NOAUTH_ALLOWLIST` | `Set(["opencode", "felo-web"])` | `virtualFactory.ts:230` 동일 값 재확인 | **일치** |
| 패키지 버전 | `3.8.50` | `package.json` `version` 필드 동일 재확인 | **일치** |

드리프트 없음 — `EVIDENCE-0003`/`EVIDENCE-0004`의 정적 분석 결론은
이번 시점에도 그대로 유효하다. 실제 동적 재확인(candidate 0개)은
§5의 실행 과정에서 함께 이루어졌다(위 §5 참조, 서버 기동은 §4의
budget 테스트 실행 자체이며 이 재확인만을 위한 별도 서버를 새로
기동하지 않았다).

---

## 7. 회귀 재확인 — 26/26·Case A·실제 Engine Lifecycle·`domain_budgets`

새 격리 인스턴스(§2 조건, 이전 §5의 인스턴스와 무관한 별도 인스턴스)
하나를 추가로 기동해 `EVIDENCE-0004` §5의 세 가지 실제 dispatch
lifecycle을 `caller.py`로 재확인했다.

| 항목 | 결과 |
|---|---|
| 로컬 test double 26개(`test_caller_unit.py`/`test_caller_lifecycle.py`/`test_case_a_boundary.py`) | `26 passed` |
| 실제 서버 `domain_budgets` 차단(§5) | `PASS`(2회 독립 재현) |
| 실제 서버 성공 응답(`caller.call_omniroute()`, `ollama-local` + 로컬 double) | `'REGRESSION_CHECK_OK'` 반환 — **PASS** |
| 실제 서버 오류 매핑(로컬 double `error500` 모드) | `OmniRouteProviderError` 발생 — **PASS** |
| 실제 서버 cancellation(로컬 double `slow` 모드, `call_omniroute_async()`) | `status→cancelled`, `OmniRouteCancelledError` — **PASS** |
| 전체 스위트(27개) | `27 passed in 13.83s`(§5 표와 동일 실행) |

`caller.py`·`test_case_a_boundary.py`는 이번 작업에서 전혀 수정하지
않았다 — Case A 경계(단일 함수, Policy 판정 로직 없음, `hqs/`
무연결)는 코드 수준에서 그대로 유지된다.

---

## 8. Production Adoption Gate 최종 상태

`ADC-0027` §Decision "구현 착수 선행조건" 4개와, `ADR-0015`§5·
`ADR-0016`§9가 정의한 "실제 구현을 향해 남은 3단계"를 이번 시점
기준으로 다시 정리한다.

### 8.1 `ADC-0027` 선행조건 4개(무변경, 참고용 재인용)

| 선행조건 | 상태 |
|---|---|
| 1. Evidence 영속화 | 충족(`EVIDENCE-0001`~`EVIDENCE-0004`) |
| 2. FAIL 3건 재해소 | `ADC-0028`/`ADC-0029`/`ADC-0030`으로 Responsibility redesign 처리 |
| 3. `domain_budgets` 확정 | PASS(`EVIDENCE-0002`, `EVIDENCE-0004`§3이 근본 원인까지 확정) |
| 4. `IMPLEMENTATION_RULES.md` Scoped 완화 | `ADR-0016`으로 문서 반영 완료 |

**이 4개는 이미 `ADR-0016` 시점에 전부 처리된 상태였다 — 이번 작업이
새로 바꾼 것은 없다.**

### 8.2 실제 구현을 향한 3단계(이번 작업의 핵심 기여)

| 단계 | `ADR-0016` 시점 상태 | 이번 문서 이후 상태 |
|---|---|---|
| 1. Thin Engine Caller 실제 구현 | 미착수(코드 0줄) | **완료** — `projects/omniroute-thin-engine-caller-v1/caller.py` |
| 2. 실제 Integration Validation | 미착수 | **완료** — `EVIDENCE-0003`(정적)·`EVIDENCE-0004`(동적, 근본 원인 확정 + 실제 lifecycle 3종)·이 문서(회귀 재확인) |
| 3. Final Adoption Review | 미착수 | **사실관계는 완비, 공식 선언은 미수행**(§8.3) |

### 8.3 "Final Adoption Review"에 대한 정확한 서술

이 문서와 `EVIDENCE-0004`가 함께 제공하는 것은 다음 사실관계다.

- 실제 구현된 Thin Caller가 `ADC-0031` §Q1의 두 조건(단일 함수 유지,
  Jarvis 코드에 Policy 판정 로직 미포함)을 **코드 수준에서**
  지킨다(`test_case_a_boundary.py` 8개, 정적 분석, 27/27 스위트의
  일부로 매 실행마다 재확인됨).
- 실제 Engine 성공/오류/cancellation lifecycle이 실제(격리) OmniRoute
  서버를 통해 end-to-end로 확인됐다(`EVIDENCE-0004`§5, 이 문서 §7이
  재확인).
- `domain_budgets` pre-dispatch 차단이 재기동-안전 방법론으로 재현
  가능해졌고 자동화된 회귀 테스트로 고정됐다(§4·§5).

**그러나 이 문서는 "Final Adoption Review 완료"를 선언하지 않는다.**
그 선언 및 그에 따른 `BASELINE.md` §14.1·§16.2의 실제 Scoped 갱신은
`ADC-0027` §Next Step이 명시한 대로 **후속 ADR**의 몫이다 — Baseline
문서 수정은 `CONSTITUTION.md` Governance Loop(RFC→ADC→ADR→Baseline)
대상이며, Evidence 문서가 그 절차를 대신하거나 우회할 권한이 없다.
이 문서는 그 후속 ADR이 근거로 삼을 수 있는 **완비된 사실관계**를
제공했을 뿐이다(§3의 GOVERNANCE-REQUIRED 항목 #14).

### 8.4 남은 절차(변경 없음, 재확인)

1. **후속 ADR** — `BASELINE.md` §14.1("Engine 호출 책임=미결")·§16.2
   Scoped 갱신, "Final Adoption Review 완료"의 공식 선언. **이 문서는
   착수하지 않는다.**
2. **Routing/Cost/Audit Policy 소재 결정**(`ADC-0031` §Out of Scope) —
   실제 Production caller가 지금의 Experimental prototype과 동일한
   형태(Policy 로직 완전 부재, OmniRoute에 전면 위임)로 갈지, 아니면
   일부를 Jarvis 코드로 가져올지는 별도 설계 결정이 필요하다. **이
   문서는 판단하지 않는다.**

---

## 9. Final Judgment

| 항목 | 판정 |
|---|---|
| `test_real_engine_budget_block.py` 갱신 여부 | **갱신 완료, 실제 실행 PASS**(§4·§5, 2회 독립 재현) |
| `domain_budgets` 차단(자동화된 회귀 테스트로 재확인) | **PASS**(무변경 유지) |
| 실제 Engine 성공/오류/cancellation lifecycle(회귀) | **PASS**(무변경 유지, §7) |
| Case A 경계(회귀) | **PASS**(27/27, 코드 무변경) |
| `blockedProviders`/`REQUIRE_API_KEY` 소스 드리프트 | **없음**(§6, read-only 재확인) |
| 검증 공백(Adoption precondition 성격의 Open Issue) | **0개**(§3, #1~5 전부 CLOSED) |
| Architecture/Contract/Freeze 변경 | **없음**(이 문서는 어떤 Governance 문서도 수정하지 않았다) |
| 새 Routing/Fallback/Gateway/Policy 구현 | **없음**(`caller.py` 무수정, 새 코드는 테스트 파일 1개뿐) |
| Production Adoption 공식 선언 | **하지 않음**(§8.3 — 후속 ADR 대상으로 명시적으로 남김) |

### 과장 방지

- "검증 공백 0개"는 "이 트랙에 관련된 모든 질문이 끝났다"는 뜻이
  아니다 — §3의 BY-DESIGN 7건은 애초에 이 트랙의 책임 범위 밖이고,
  GOVERNANCE-REQUIRED 3건은 **의도적으로 미종결 상태로 남겨졌다**
  (사용자 지시 §7 준수).
- Production Adoption Gate의 "구현 착수 선행조건 4개"와 "실제 구현
  3단계"는 서로 다른 체크리스트다 — 전자는 `ADR-0016` 시점에 이미
  전부 충족됐고, 이번 작업은 후자의 1·2단계를 완료했을 뿐 3단계
  (공식 Final Adoption Review 선언 + Baseline 반영)는 완료하지
  않았다.

---

## 10. Governance / Architecture 영향

- Architecture 변경: **없음**. Contract 변경: **없음**. Freeze 변경:
  **없음**. `CONSTITUTION.md`/`BASELINE.md`/`IMPLEMENTATION_RULES.md`/
  `ARCHITECTURE_GOVERNANCE.md` 어느 것도 이 작업에서 수정하지 않았다
  (§6에서 읽기만 했다).
- `ADC-0027`~`ADC-0031`, `ADR-0015`~`ADR-0016`, `EVIDENCE-0001`~
  `EVIDENCE-0004` 파일: **무수정**.
- 새로 작성/수정한 파일: 이 문서(`EVIDENCE-0005`) 1개,
  `projects/omniroute-thin-engine-caller-v1/tests/test_real_engine_budget_block.py`
  1개(전체 재작성, §4). `caller.py`·다른 테스트 파일·`README.md`·
  `EVIDENCE.md`는 무수정.
- 새 Jarvis측 Routing/Fallback/Gateway/Policy: **구현하지 않았다**.
  §3 #12(Policy 소재 결정)는 명시적으로 GOVERNANCE-REQUIRED로 분류해
  이번 작업이 판단하지 않았다.

---

## 11. Provenance / Reproducibility

- **`test_real_engine_budget_block.py` 실행**: `RUN_REAL_OMNIROUTE_TESTS=1
  I_UNDERSTAND_REAL_EGRESS_RISK=1 python3 -m pytest
  projects/omniroute-thin-engine-caller-v1/tests/test_real_engine_budget_block.py -v`
  — 2회 독립 실행(각각 새 `tmp_path`, 새 서버 인스턴스), 게이트
  미설정 1회(SKIP 확인).
- **전체 스위트**: 위와 동일 게이트로
  `python3 -m pytest projects/omniroute-thin-engine-caller-v1/tests/ -v`
  → `27 passed`.
- **회귀 lifecycle 재확인(§7)**: 별도 격리 인스턴스
  (`DATA_DIR=<isolated> NODE_ENV=test OMNIROUTE_ALLOW_DEFAULT_DATA_DIR=0
  OMNIROUTE_API_KEY=regress-key-0001 PORT=20330 HOSTNAME=127.0.0.1
  node dist/server.js`, 재기동 없음) + `blockedProviders` 적용(§6과
  동일 12개 id) + `ollama-local` provider_connections placeholder
  row + 로컬 stdlib 서버(`127.0.0.1:11434`, success/error500/slow
  3모드) + `caller.call_omniroute()`/`call_omniroute_async()` 직접
  호출.
- **read-only 소스 재확인(§6)**: `grep`/`Read`로 `featureFlagDefinitions.ts`,
  `virtualFactory.ts:230`, `package.json` 대조. 서버 미기동.
- **cleanup 결과**: 이번 작업에서 기동한 모든 프로세스(OmniRoute
  standalone 서버 3개 인스턴스 — budget 테스트용 2회 + lifecycle
  회귀용 1회, 로컬 double 서버 3개 모드 전환) PID 기준 강제 종료
  확인, 모든 임시 `DATA_DIR`·scratchpad 스크립트 삭제, `lsof`로
  관련 포트 전부 미점유 재확인, 실제 `~/.omniroute/storage.sqlite`
  mtime(`1788605986`)·size(`2547712`)가 작업 시작 전과 매 단계 후
  동일함을 반복 재확인.

---

## Self Review

- `test_real_engine_budget_block.py`를 갱신할지 폐기할지 근거를 갖고
  판단했는가 — **Pass**(§4.2, 재현 가능한 방법론이 이미 확립돼
  있었고 안전 설계가 재사용 가능했다는 구체적 근거).
- 갱신한 테스트를 실제로 실행해 PASS를 확인했는가 — **Pass**(§5,
  2회 독립 실행 + 전체 스위트 + SKIP 기본값 확인).
- Open Issue를 근거 없이 "0개"로 선언했는가 — **아니오**(§3에서
  15개 항목을 전부 나열하고 CLOSED/BY-DESIGN/GOVERNANCE-REQUIRED로
  분류한 뒤, "검증 공백"과 "절차적 전제"를 구분해 정확히 서술했다).
- Architecture/Baseline 변경이 필요한 항목을 임의로 종결했는가 —
  **아니오**(§3 #12~14, §8.3·§8.4에서 GOVERNANCE-REQUIRED로 명시하고
  손대지 않았다 — 사용자 지시 §7 준수).
- 새 Routing/Fallback/Gateway/Policy를 구현했는가 — **아니오**(§10 —
  `caller.py` 무수정, 새 코드는 테스트 파일 재작성 1건뿐).
- Production Adoption 완료를 선언했는가 — **아니오**(§8.3·§9에서
  명시적으로 부정).
- `blockedProviders`/`REQUIRE_API_KEY`를 read-only로 우선 재확인했는가
  — **Pass**(§6 — grep/Read만 사용, 서버 기동 없이 소스 드리프트
  부재를 먼저 확인한 뒤 §5·§7에서만 동적 확인을 수행했다).
- 26/26(현재 27/27)·Case A·실제 Engine lifecycle·`domain_budgets`
  회귀를 재확인했는가 — **Pass**(§7).
- 실제 provider/실제 비용 발생이 있었는가 — **없다**. 모든 dispatch
  대상은 로컬 stdlib 서버였다.
- 실제 `~/.omniroute` 데이터·credential을 건드렸는가 — **아니다**
  (§11, 매 단계 mtime/size 동일 확인).
- 기존 `EVIDENCE-0001`~`EVIDENCE-0004`, `ADC-0027`~`ADC-0031`,
  `ADR-0015`~`ADR-0016`을 수정했는가 — **아니오**.
- commit/push/PR을 수행했는가 — **아니오**.
