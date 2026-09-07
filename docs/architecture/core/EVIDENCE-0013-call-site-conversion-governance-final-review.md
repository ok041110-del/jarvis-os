# EVIDENCE-0013: OmniRoute Call-Site Conversion — Governance 최종 재확인(READ-ONLY Review) 결과

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하거나
변경하지 않는다. 이 문서는 `EVIDENCE-0012` 이후 수행된 **READ-ONLY
Governance Review**(코드 수정·설정 수정·OmniRoute 서버 기동·실제
provider 호출·문서 수정·commit/push/PR 전부 없음)의 최종 판정을
감사 가능한 형태로 기록할 뿐이다. 이 문서 자체도 기존 ADC/ADR의
Decision을 재론하지 않는다 — 기존 Decision을 원문과 대조해 현재
구현 상태에 적용한 결과만 기록한다.

## 1. Review 성격 — READ-ONLY 확인

이 Review는 다음을 수행하지 않았다.

- 코드 수정 — 없음.
- 설정 수정 — 없음(`~/.omniroute` 등 어떤 설정도 이번 Review에서
  변경하지 않았다 — `EVIDENCE-0012`가 이미 변경한 상태를 그대로
  읽기만 했다).
- OmniRoute 서버 기동 — 없음.
- 실제 provider 호출 — 없음.
- 기존 문서 수정 — 없음(`CONSTITUTION.md`/`IMPLEMENTATION_RULES.md`/
  `BASELINE.md`/`ADC-0027`/`ADC-0031`/`ADR-0015`~`ADR-0017`/
  `EVIDENCE-0007`/`0008`/`0010`/`0011`/`0012`/`RT-0001.md`/
  `ADC-0010` 전부 원문 그대로 다시 읽었을 뿐 한 글자도 바꾸지
  않았다).
- Architecture/Contract 변경 — 없음.
- commit/push/PR — 없음.

이 Review가 수행한 것은 위 문서 전체를 **원문 기준으로 재대조**하고,
`hqs/development/mvp/omniroute_engine.py` 전체를 다시 읽고, 5개 기존
호출부에 대해 `grep`으로 "omniroute" 미참조를 재확인하고,
`test_omniroute_engine_boundary.py` 7개를 read-only로 재실행(서버
기동·provider 호출·코드 변경 전혀 없는 순수 AST 기반 정적 검증)한
것뿐이다.

## 2. 원문 재대조 대상(전수)

| 문서 | 재확인한 핵심 내용 |
|---|---|
| `hqs/development/CONSTITUTION.md` | Architecture Freeze 9개 항목 목록 + `ADR-0016`이 추가한 Scoped 예외 문단("Engine Adapter"·"Model Routing" 두 항목만, Thin Engine Caller 형태에 한정) |
| `hqs/development/IMPLEMENTATION_RULES.md` | 금지 표 15·16·17·21행(Engine Gateway/Routing/Policy/Multi Engine 금지) + `ADR-0016`이 추가한 "OmniRoute Thin Engine Caller 범위 확인" 절 |
| `docs/architecture/baseline/BASELINE.md` | §14.1 "3. Engine 호출 책임"(부분 진전, `ADR-0017` 반영), §16.2 "이 Accept가 결정하지 않는 것" 문단(OmniRoute Thin Engine Caller Production Adoption 부분 진전 서술) |
| `ADC-0027` | Q1~Q7, Decision(Accept, Conditional·Scoped), 구현 착수 선행조건 4개 |
| `ADC-0031` | Case A/B/C 정의(Q1), Case A 두 조건((a) 단일 함수 (b) Policy 판정 로직 미포함), 허용/금지 목록, Gate Impact |
| `ADR-0015` | 5개 ADC Decision 통합 정리(Consolidation Only), Production Adoption Gate 미완료 명시 |
| `ADR-0016` | `CONSTITUTION.md` Freeze Scoped 예외 실제 반영, `IMPLEMENTATION_RULES.md` 범위 확인 절 실제 반영 |
| `ADR-0017` | §2 Responsibility Boundary(Policy 소재), §4 기존 Governance 규칙 충돌 최종 검토, §5 Gate 10개 PASS 판정, §6.1 Production Adoption 선언, **§6.2**(이 선언이 하지 않는 것) |
| `EVIDENCE-0007` | Call-Site Conversion HOLD 판정, §6.2 재검토 선행조건 4개 |
| `EVIDENCE-0008` | `test_mvp_0001.py` 게이트 재설계·해결 |
| `EVIDENCE-0010` | Python 3.10+ isolated venv 확보, 5개 collection 오류 파일 해소 |
| `EVIDENCE-0011` | 실제 운영 인스턴스 `blockedProviders`/`REQUIRE_API_KEY` 미구성 FAIL 확정 |
| `EVIDENCE-0012` | 실제 운영 인스턴스에 두 설정 적용·검증(사본 기반, credential 비노출) |
| `docs/governance/rt/RT-0001.md` | Candidate 2(Engine Gateway) Trigger 원문·Trigger Rationale 원문 |
| `docs/architecture/core/ADC-0010-engine-caller-location-boundary.md` | C1(Kernel Engine Port/Adapter) 재검토에 필요한 "부족한 Evidence" 결합 조건(Kernel Module Defer 3건·ADC-01·02·Engine 수 ≥2) |

추가로(위 목록 외, 이번 Review가 현재 구현 상태 대조를 위해 직접
재확인한 것): `hqs/development/mvp/omniroute_engine.py` 전체,
5개 기존 호출부(`agents/backend.py`·`design.py`·`qa.py`·
`requirements.py`·`workflow_ast_context.py`)의 "omniroute" 미참조,
`test_omniroute_engine_boundary.py` 7개 read-only 재실행.

## 3. Governance 최종 판정

**PASS — 5개 Call-Site Conversion 진행 가능.** 단, §10의 조건이
전제된 PASS이며 무조건적 승인이 아니다.

| # | 판정 대상 | 결과 |
|---|---|---|
| 1 | 실제 운영 안전 설정 | **PASS(caveat 포함)** — `EVIDENCE-0012`가 실제 `key_value` 테이블에 `blockedProviders`(12개)·`REQUIRE_API_KEY=true`를 기록했고, 사본 기반 동작 검증(무인증 401, 인증 시 후보 0개)으로 기능이 실제로 작동함을 확인했다. `EVIDENCE-0011`의 FAIL은 공식적으로 해소됐다. Caveat은 §11. |
| 2 | Thin Caller(Case A) | **PASS** — `omniroute_engine.py` 재확인: 단일 함수, provider/model 선택·routing·fallback·policy 로직 0줄, `OMNIROUTE_MODEL` 값 자체를 검사하지 않고 OmniRoute에 위임, `engine.py`와 상호 무참조. `test_omniroute_engine_boundary.py` 7/7 재실행 PASS(이번 Review, read-only). |
| 3 | RT-0001 / ADC-0010 | **Trigger 비-성립(조건부)** — §4·§5·§6 참조. |
| 4 | Freeze / `IMPLEMENTATION_RULES.md` | **충돌 없음** — §7 참조. |
| 5 | Governance 선행조건 #4 | **이 문서(단순 Governance confirmation)로 충분** — §8·§9 참조. |

## 4. `ADR-0017` §6.2 재확인 결과

`ADR-0017` §6.2("이 선언이 하지 않는 것") 원문을 다시 대조한 결과,
다음 문장이 이미 명시돼 있음을 확인했다.

> "**`hqs/development/mvp/engine.py`를 교체하거나 실제 서비스
> 트래픽에 OmniRoute를 연결하지 않는다.** ... 실제 production
> 배포는 별도의 구현 작업(코드 변경, 테스트, PR)이며, 이 ADR은
> 그 작업이 **Architecture/Governance 차원에서 이제 허용된다**는
> 것만 확정한다."

이는 **`EVIDENCE-0007`이 §6.2에 추가한 "선행조건 #4(전환 자체를
Governance 절차로 다시 확인할지 사용자가 명시적으로 선택)"가
`ADR-0017` 자신이 실제로 요구한 조건이 아니었다**는 것을 의미한다
— `ADR-0017`은 이미 실제 코드 수준 전환(engine.py 교체 포함)을
"별도 구현 작업"으로 규정하며 Architecture/Governance 차원의
허용을 선언해 뒀다. `EVIDENCE-0007`의 선행조건 #4는 그 세션이
추가한 **보수적 caution**이었을 뿐, 별도 RFC/ADC/ADR을 요구하는
근거가 원문에 없다. 이 재발견이 §9(새 RFC/ADC/ADR 불필요 판정)의
직접 근거다.

이 허용은 **무조건**이 아니다 — `ADR-0017` §2.4·§6.2 자신이 "Case A
밖(Case B/C)으로의 전환을 승인하지 않는다"고 명시했으므로, 이
허용은 **Case A 유지 + RT-0001/ADC-0010 비-Trigger**를 조건으로
한다(§10).

## 5. RT-0001 논증(원문 재대조, 단순 반복이 아닌 재도출)

`RT-0001.md` Candidate 2 원문:

> Trigger: "Engine 수 ≥ 2 (두 번째 Engine이 실제로 **추가**되어
> `call_engine()` 호출 지점이 둘 이상의 서로 다른 Engine을
> 대상으로 하게 됨)"
> Rationale: "ADC-0001의 Decision Rationale은 '...단일 Engine'에서만
> 근거를 얻었다. 두 번째 Engine이 실제로 **추가**되는 순간, 그
> 전제(단일 Engine)가 더 이상 성립하지 않는다."

### 5.1 5개 전부 동시 전환 — Trigger 비-성립

5개 호출부 전부를 하나의 동기화된 변경으로 `call_engine_via_omniroute`
로 전환하면, `engine.py::call_engine()`은 **어떤 production 호출
지점도 갖지 않게 된다**(0개) — 삭제되지 않고 정의는 남지만
호출되지 않는 dead code가 된다. Trigger 원문이 요구하는 "호출
지점이 둘 이상의 서로 다른 Engine을 대상으로 하게 됨"은 애초에
호출 지점이 **0개**이므로 성립할 수 없다(0은 "둘 이상"이 아니다).
동시에 Rationale이 말하는 "두 번째 Engine이 **추가**"라는 사건도
일어나지 않는다 — 이것은 **추가(addition)가 아니라 교체
(replacement)**다: 실행 중인 Engine의 수는 전환 전후 모두
정확히 1개이며, 다만 그 1개가 Claude CLI에서 OmniRoute로 바뀔
뿐이다. Trigger의 문면과 취지 양쪽 모두 미충족이다.

### 5.2 부분 전환 — Trigger 성립 가능(그래서 금지)

일부 호출부만 전환하면(예: `backend.py`만 전환, 나머지 4개는
`call_engine()` 유지), 실제 production 파이프라인 안에 **Claude
CLI와 OmniRoute 두 Engine이 동시에 실재**하게 된다. `call_engine()`
자신의 남은 4개 호출 지점은 여전히 1개 Engine(Claude CLI)만
가리키므로 Trigger 문면을 리터럴하게 만족시키지는 않을 수 있으나,
Rationale이 명시한 "단일 Engine 전제가 깨지는 순간"이라는 취지는
시스템 수준에서 정확히 충족된다 — Jarvis가 실제로 2개의 서로 다른
Engine을 동시에 운용하게 되기 때문이다. **따라서 부분 전환은
Trigger를 충족시킬 위험이 있으므로 명시적으로 금지한다** — 허용
가능한 유일한 설계는 5개 전부의 동기화된 동시 전환뿐이다.

### 5.3 결론

**5개 전부 동시 전환 → RT-0001 Candidate 2 Trigger 비-성립.**
**부분/단계적 전환 → Trigger 성립 가능, 금지.**

이 결론은 `EVIDENCE-0007` §5가 이미 도달한 결론과 방향이 같지만,
이번 Review는 "0개 호출 지점" 논증(§5.1)으로 그 결론을 원문에
더 밀착시켜 재도출했다 — 단순 반복이 아니라 원문 대조를 통한
재확인이다.

## 6. `ADC-0010` C1 비-Trigger 유지

`ADC-0010` §부족한 Evidence 1(C1, Kernel Engine Port/Adapter)의
재검토 조건은 "Kernel Module Defer 3건, ADC-01·02, **Engine 수
≥2** 등"의 **결합**이다 — 어느 하나만으로 문이 열리지 않는다.
§5가 확인한 대로 5개 전부 동시 전환 시 "Engine 수 ≥2"(RT-0001과
동일 정의) 자체가 성립하지 않으므로, 이 결합 조건은 이번 전환으로
전혀 충족되지 않는다. ADC-01·ADC-02도 여전히 Open 상태 그대로다
(Open은 "충족"이 아니다). **C1 재검토는 이번 전환으로 열리지
않는다** — `ADR-0017` §4의 기존 판단과 동일하며, 이번 Review가
원문 재대조로 재확인했다.

## 7. Case A / Freeze / `IMPLEMENTATION_RULES.md` 충돌 검토

- **Case A 유지**: `omniroute_engine.py`는 `ADC-0031` §Q1의 두 조건
  — (a) 단일 함수 형태, (b) Routing/Cost-Budget/Audit Policy·API
  Key Scope 판정 로직 Jarvis 코드에 부재 — 를 현재 코드 상태로
  만족한다(§3 항목2, `test_omniroute_engine_boundary.py` 재확인).
- **`CONSTITUTION.md` Architecture Freeze**: `ADR-0016`이 추가한
  Scoped 예외("OmniRoute를 Thin Engine Caller 형태로 사용하는
  범위에 한해 Conditional Scoped 해제")가 이미 이 범위를 허용해
  뒀고, 현재 구현이 정확히 그 범위 안에 있다 — **충돌 없음**.
- **`IMPLEMENTATION_RULES.md` 15·16·17·21행**: `ADC-0031`이 이미
  Thin Engine Caller가 이 네 조항과 충돌하지 않음을 확인했고,
  `ADR-0016`이 "범위 확인" 절로 반영했다 — 금지 표 문구 자체는
  무변경이며 이번 전환도 그 문구를 건드리지 않는다 — **충돌
  없음**.
- **Engine Adapter Contract(§14)**: `ADR-0017`도 이번 Review도
  §14를 확정하지 않는다 — 전환 후에도 함수 시그니처·Port
  인터페이스는 여전히 미결 상태로 유지된다.

## 8. 새 RFC/ADC/ADR 불필요 판정

§4가 확인한 대로 `ADR-0017` §6.2가 이미 실제 코드 수준 전환을
"Architecture/Governance 차원에서 이제 허용된다"고 명시했고, §5·§6·
§7이 그 허용의 조건(Case A 유지, RT-0001/ADC-0010 비-Trigger,
Freeze/Rules 무충돌)이 현재 구현 상태에서 실제로 지켜짐을
확인했다. 따라서 **이 전환에 새로운 RFC/ADC/ADR은 필요하지
않다** — 통상적 구현 절차(코드 변경 → 테스트 → PR)로 진행 가능하다.

**단, 이 판단은 무기한 유효하지 않다.** Case A 조건이나 RT-0001/
ADC-0010 비-Trigger 상태가 실제 구현 시점에 깨지는 것으로
판단되면(`ADC-0031` §Risks·`ADR-0017` §2.4가 이미 명시한 재검토
조건), 이 판정은 그 설계에 적용되지 않으며 별도 Architecture
Decision이 다시 필요해진다.

## 9. Governance 선행조건 #4 — 최종 해소

`EVIDENCE-0007` §6.2 선행조건 #4("전환 자체를 Architecture/
Governance 절차로 다시 확인할지, 아니면 순수 운영 결정으로
충분한지 사용자가 명시적으로 선택한다")는 이 문서로 **해소**된다
— §4·§8이 확인한 대로 `ADR-0017` 자신이 새 ADC/ADR을 요구하지
않았으므로, **이런 형태의 단순 Governance Review(원문 재대조 +
현재 구현 상태 대조 + 조건 재확인)로 충분하다.**

## 10. Conversion 진행 조건(전제, 무조건 승인 아님)

실제 착수 시 아래를 모두 지켜야 이번 PASS 판정이 유효하다.

1. **5개 call-site를 하나의 동기화된 변경으로 전환**한다 — 부분/
   단계적 전환 금지(§5.2).
2. **Case A를 코드로 유지**한다 — 전환 PR에 provider/model
   선택·routing·fallback·policy 판정 로직을 추가하지 않는다
   (`ADC-0031` §Q1, §3 항목2).
3. **Python 3.10+ 환경**에서 실행·테스트한다 — `workflow_ast_context.py`
   가 5개 호출부에 포함되며, 그 파일은 Python 3.9에서 collection
   자체가 불가능하다(`EVIDENCE-0010`).
4. **실제 코드 변경이므로 PR이 필요**하다(`CLAUDE.md` PR Creation
   Criteria — "실제 코드/Capability 변경, main에 반영할 실제
   산출물이 있는 작업"에 해당).

## 11. 남은 caveat(이 PASS 판정이 닫지 않는 것)

- **실제 운영 인스턴스 재기동 관찰**: `EVIDENCE-0012`의 설정
  적용은 사본 기반으로 기능 검증됐을 뿐, 실제 라이브 인스턴스를
  재기동해 새 설정이 실사용 트래픽에 적용되는 순간을 직접
  관찰하지는 않았다(health-check-repair 위험 회피를 위한 의도적
  판단, `EVIDENCE-0012` §6.2). 이 관찰은 운영자의 몫으로 남는다.
- **Real Engine Gate ON 시 실제 egress 검증**: `test_mvp_0001.py`의
  `RUN_REAL_ENGINE_TESTS` Gate가 전환 이후 실제로 켜지면 OmniRoute
  경로를 타게 된다 — 그 시점 실제 provider egress 여부는 운영자의
  실제 구성(이번에 적용된 `blockedProviders`/`REQUIRE_API_KEY`
  포함)에 최종적으로 달려 있으며, 이 문서가 그 실행을 대신
  검증하지 않는다.
- **`ADR-0017` §12의 별도 Open Issue**(무변경, 이 Adoption의
  전제조건이 아니었음, 이번 Review도 재론하지 않음): Audit Policy
  공백(`routing_decisions` OmniRoute 측 dead code), `priority`
  tie-break 실제 dispatch 영향 UNVERIFIED, `domain_budgets`
  semantics 전체(warning threshold·기간 리셋·복수 API key·DB-backed
  key 경로) 미검증, `ADC-0010`/`RT-0001`(전환 시 비-Trigger로
  재확인됐으나 §5의 조건이 지켜지는 한에서만), ADC-01·ADC-02·
  `docs/governance/adc/ADC-0003.md` 판단4(전부 Open, 이 트랙과
  무관).

## Governance / Architecture 영향

- Architecture 변경: **없음**. Contract 변경: **없음**. Freeze 변경:
  **없음**.
- 코드 변경: **없음**(이번 Review는 순수 read-only 재대조·재실행만
  수행했다 — `omniroute_engine.py`, `engine.py`, 5개 호출부 전부
  무수정).
- 설정 변경: **없음**(`EVIDENCE-0012`가 만든 상태를 그대로 읽었을
  뿐).
- `CONSTITUTION.md`/`IMPLEMENTATION_RULES.md`/`BASELINE.md`/
  `ADC-0027`~`ADC-0031`/`ADR-0015`~`ADR-0017`/`EVIDENCE-0007`~
  `EVIDENCE-0012`/`RT-0001.md`/`ADC-0010`: **전부 무수정**.
- 새로 작성한 파일: 이 Evidence 문서 1개뿐.

## Provenance / Reproducibility

- 원문 재대조: §2 표에 나열한 15개 문서 전체를 `Read` 도구로 직접
  재확인(요약·기억 인용 없이 원문 대조).
- 현재 구현 상태 재확인: `hqs/development/mvp/omniroute_engine.py`
  전체 재확인(단일 함수, Policy 로직 0줄, `engine.py` 상호
  무참조), `grep -l omniroute hqs/development/mvp/agents/backend.py
  .../design.py .../qa.py .../requirements.py
  .../workflow_ast_context.py` → 매치 없음(5개 호출부 전부
  omniroute 미참조), `python3 -m pytest
  hqs/development/mvp/tests/test_omniroute_engine_boundary.py -v`
  → `7 passed in 0.04s`(read-only, 서버 미기동, provider 호출 없음).
- `RT-0001.md` Candidate 2 Trigger·Rationale 원문 재확인, `ADC-0010`
  §부족한 Evidence 1(C1) 원문 재확인.
- 실제 Provider 호출: 없음. OmniRoute 서버 기동: 없음. 실제
  `~/.omniroute` 접근: 없음(이번 Review는 그 인스턴스에 전혀
  접근하지 않았다 — `EVIDENCE-0012`가 이미 만든 상태를 그 문서
  자체를 다시 읽어 확인했을 뿐).
- 코드/문서 변경: `git status --short` — 이 Evidence 문서 1개만
  추가.
- commit/push/PR: 수행하지 않음.

## Self Review

- Governance Review가 READ-ONLY였음을 기록했는가 — **Pass**(§1).
- 원문 재대조 대상 15개 문서를 전부 나열했는가 — **Pass**(§2).
- Governance 최종 판정(PASS, 5개 진행 가능)을 명확히 선언했는가 —
  **Pass**(§3).
- `ADR-0017` §6.2 재확인 결과(별도 구현 작업, 이미 허용됨)를
  정확히 인용했는가 — **Pass**(§4, 원문 인용).
- RT-0001 논증(0개 호출 지점 → 교체, 부분 전환 금지)을 원문
  대조로 재도출했는가(단순 반복이 아닌가) — **Pass**(§5, "0개
  호출 지점" 논증은 이번 Review의 재도출이지 기존 문서의 문구
  재인용이 아니다).
- `ADC-0010` C1 비-Trigger를 확인했는가 — **Pass**(§6).
- Case A 조건 유지를 확인했는가 — **Pass**(§7, §3 항목2).
- Architecture/Contract/Freeze 무변경을 확인했는가 — **Pass**(§7,
  Governance/Architecture 영향).
- 새 RFC/ADC/ADR 불필요 판정과 그 근거를 기록했는가 — **Pass**
  (§8, §4에 근거).
- Conversion 진행 조건 4가지를 명시했는가 — **Pass**(§10).
- 남은 caveat 3종을 명시했는가 — **Pass**(§11).
- 기존 문서를 수정했는가 — **아니오**.
- Architecture/Contract를 변경했는가 — **아니오**.
- 코드를 수정했는가 — **아니오**.
- OmniRoute 서버를 기동했는가 — **아니오**.
- 실제 provider를 호출했는가 — **아니오**.
- commit/push/PR을 수행했는가 — **아니오**.
