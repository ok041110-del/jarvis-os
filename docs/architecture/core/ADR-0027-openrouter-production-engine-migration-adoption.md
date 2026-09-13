# ADR-0027: OpenRouter Production Engine Migration — Adoption

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0027` |
| 상태 | **Accepted (Scoped) — Production Routing Integration(Architecture Adoption) 확정: OpenRouter를 Jarvis의 3번째 Production LLM Engine으로 승인하고, Stage 01~05가 Free Model Selection Architecture로 Migration 가능함을 확정한다. §10 Validation Gate(12개 항목)는 이후 실측으로 전부 PASS 확인됐다(§16 Gate 통과 기록 참조, Evidence: `ADR-0027-VALIDATION-GATE-EXECUTION-0001.md` 외 3건) — Stage 01~05 Production 코드 Migration 착수 조건이 충족됐다. 단, §9 Production Operational Validation(장기 quota 안정성/latency/광범위 model quality 평가/long-term 가용성)은 이 ADR이 여전히 전부 결정하지 않는다 — 그 항목들은 계속 `NOT YET DETERMINED`로 유보한다(§9, §16 각주로 최신화).** |
| Context | `RFC-0041-openrouter-production-engine-migration.md` → `ADC-0044-openrouter-production-engine-migration-decision.md` → 이 ADR |
| 관련 RFC | `RFC-0041`(3번째 Engine 추가 제안), `RFC-0040`(Architecture Boundary 원 제안) |
| 관련 ADC | `ADC-0044`(Architecture Adoption 확정, Operational Reliability NOT DETERMINED), `ADC-0043`(Architecture Boundary 확정, 재론하지 않고 승계) |
| 관련 ADR | `ADR-0026`(Architecture Boundary Accepted/Scoped, §10에서 유보했던 Production Routing Integration을 이 ADR이 승격), `ADR-0024`(2-Engine 구조, 3번째 Engine 추가의 절차적 근거) |
| 관련 Evidence | `OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`, `STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`, `OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md` |
| Governance Status 확인 | `ADR-0025`/`ADR-0026`이 이미 확인한 대로, 이 저장소의 모든 ADR Status는 "Accepted"(Scoped 등 수식어 동반) 계열뿐이다. 이 ADR도 동일 어휘("Accepted (Scoped)")를 재사용한다 — 새 상태명을 만들지 않는다. 단, 이 ADR은 `ADR-0025`/`ADR-0026`과 달리 **"Production Routing/Integration" 자체를 최초로 Accepted로 승격**한다는 점에서 구분된다 — 이 구분을 §1/§8에서 명시한다. |

---

## 1. Context

`ADR-0026`은 OpenRouter Free Model Selection의 Architecture
Boundary(Free Pool/Deterministic Filter/Candidate Selection/
OpenRouter Delegation/Contract Validation 독립성)를 Accept했지만,
§9(Concrete API 구현)와 §10(Production Routing Integration)은
명시적으로 NOT YET DETERMINED로 남겼다. 그 뒤 두 Experiment
(`OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`,
`STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`)가 Free Pool→
Filter→Candidate Selection 구간을 실제 Pool 데이터로 실측 확정했으나,
OpenRouter 실제 선택/Contract Validation/Retry 회복 구간은 계정 단위
quota 소진으로 세션 내내 확인하지 못했다. 이후 Stage 01~05 Production
코드를 직접 Migration하려는 시도가 있었으나
(`OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md`), `ADR-0026`
§10의 유보 상태와 `IMPLEMENTATION_RULES.md`의 "3번째 Engine은 별도
RFC → ADC → ADR 대상" 규칙 때문에 STOP했다. `RFC-0041` → `ADC-0044`가
그 STOP이 요구한 별도 절차이며, 이 ADR이 그 절차의 마지막 단계다.

## 2. Problem

"Architecture Boundary가 Accept됐다"는 사실만으로는 Production Stage
01~05 코드를 바꿀 근거가 되지 않는다 — `IMPLEMENTATION_RULES.md`가
3번째 Engine 추가에 별도 절차를 요구하기 때문이다. 이 ADR은 그 절차의
마지막 단계로서, "Migration 가능"이라는 Governance 근거를 만드는
것과 "실제로 안정적으로 동작한다"는 것을 **분리**해서 답해야 한다 —
후자를 전자의 조건으로 삼으면 Architecture Adoption이 영원히
불가능해지고(quota 같은 외부 조건에 좌우), 전자만으로 후자를
생략하면 검증되지 않은 것을 검증됐다고 주장하는 셈이 된다.

## 3. Existing Evidence

| 출처 | 확인한 것 |
|---|---|
| `RFC-0041` §Engine Boundary | Jarvis Engine selection(A)과 OpenRouter 내부 selection(B)의 구분, 3번째 Engine 추가가 `ADR-0024` Option C의 "정적 import" 원칙을 훼손하지 않음을 논증 |
| `ADC-0044` Q1~Q5 | 3번째 Engine 절차 충족(Q1), A/B 구분 유지(Q2), Free Pool/Filter/Candidate Selection의 실측 근거 충분(Q3), OpenRouter 실제 선택/Contract 구간의 근거 부재(Q4), `ADC-0043`/`ADR-0026`과 비충돌(Q5) |
| `OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md` §3, §4 | Free Pool 19개 모델 실측, 5개 Candidate Case(0/1/2/3/>3) 전부 실제 Pool 데이터로 재현, tie-break 15회 일관 적용 |
| `OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md` §5~§7 | OpenRouter 실제 선택/Contract Validation/Retry 회복 — 15/15 실행이 계정 단위 quota 소진(HTTP 429)으로 전부 실패, NOT DETERMINED |
| `STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md` §1, §2 | Stage 05 Review에 placeholder가 아닌 실제 Stage 04 Implementation이 전달되는 구조를 pre-check로 확정 |
| `STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md` §4~§6 | 6/6 attempt 전부 quota 소진(429)으로 실패, LLM Review 실제 결과 여전히 미확인. Deterministic 기준선(AST/Dependency PASS)만 확보 |
| `OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md` | Stage 01~05 실제 LLM 호출 지점 전수 조사 — 5개 Stage 전부 `ADR-0024` Option C(정적 import) 그대로, 어느 Stage도 모델명을 하드코딩하지 않음(제거할 hardcoded model이 애초에 없었음) |

## 4. Architectural Options

### A. 현행 유지(2-Engine 고정, Migration 승인하지 않음)

`ADR-0026` §10을 NOT YET DETERMINED로 계속 유지한다. 장점: 추가
리스크 없음. 단점: 무료 모델 Pool을 Production에서 영구히 활용하지
못한다.

### B. Architecture Adoption만 승인, Operational Validation은 별도 Gate(채택안)

Free Pool→Filter→Candidate Selection→`models[]` 요청 구성까지의
경로를 Production Engine으로 승인하되, 실제 코드 Migration은
`ADR-0027` §9 Validation Gate를 통과한 뒤에만 진행한다.

### C. 즉시 전면 Migration(Operational Validation 없이)

quota 미확인 상태에서 Stage 01~05 코드를 바로 바꾼다. 장점: 없음.
단점: `OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-
0001.md`/`STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`가
확인하지 못한 구간(OpenRouter 실제 선택/Contract/Review 품질)을
검증 없이 Production에 노출시킨다 — 채택하지 않는다.

## 5. Engine Boundary Decision

**확정한다(Scoped Accept)**: `RFC-0041` §Engine Boundary를 그대로
채택한다.

- **A. Jarvis Engine selection**: 정확히 하나의 Engine 모듈을 파일
  import 시점에 정적으로 선택하는 원칙(`ADR-0024` Option C)을 그대로
  유지한다 — 선택 가능한 모듈이 2개(ChatGPT/Claude Code)에서
  3개(+ OpenRouter Adapter)로 늘어날 뿐이다.
- **B. OpenRouter 내부 Free Model selection**: 후보 중 실제 모델
  선택은 OpenRouter의 책임으로 확정한다(`ADR-0026` §7 그대로 승계).
- 이 구분이 깨지는 순간(런타임 조건 분기, Central Router 도입,
  Provider-specific 함수의 Stage/Agent 노출)은 `IMPLEMENTATION_
  RULES.md`의 금지 조항이 다시 전면 적용된다 — `ADR-0024` §Multi-
  Engine 허용 범위의 조건(a)~(c)와 동일한 조건이 이번 3-Engine
  구조에도 그대로 적용된다.

## 6. Free Model Selection Architecture Decision

**확정한다**: 아래 8단계를 Production Engine의 내부 구조로 채택한다
(`ADR-0026`이 이미 Accept한 것의 재확인, 새로 결정하지 않음):

```
Stage → Stage Requirement → Free Pool → Deterministic Filter →
Candidate Selection ≤3 → OpenRouter models[] →
OpenRouter 실제 선택/failover → Stage Execution → Contract Validation
```

- Free Pool 기반, deterministic filtering, 최대 3개, OpenRouter
  delegation, Contract Validation 유지 — `ADC-0044` §Decision
  "확정하는 것" 목록을 그대로 승계.
- Stage별 fixed model mapping은 Production Architecture로 승격하지
  **않는다** — 애초에 현재 Production Stage 01~05 어디에도 하드코딩된
  모델명이 없었다(`OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-
  0001.md` §8)는 사실을 그대로 유지 요건으로 삼는다.

## 7. Stage Contract Decision

**확정한다**: Stage 01~05의 기존 Input/Output Contract는 이 Migration
으로 **전혀 변경되지 않는다**(`RFC-0041` §Stage 01~05 영향 표 그대로).
Stage 05 Review는 반드시 실제 Stage 04 Implementation을 입력으로
받아야 한다는 요건(`STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-
0001.md`가 실증한 구조)을 Production 요건으로 확정한다 — placeholder/
dummy Implementation을 Review에 전달하는 것은 이 ADR 위반이다.

## 8. Production Routing Integration Decision — 이번에 처음 Accepted로 승격

**확정한다(이전 ADR과의 결정적 차이점).**

- `ADR-0026` §10: "NOT YET DETERMINED... OpenRouter는 지금까지
  Production Stage Engine Routing에 편입된 적이 없고, '실험적 검증
  endpoint'로만 다뤄져 왔다."
- **이 ADR은 그 구분을 바꾼다.** OpenRouter는 이제 Production Stage
  Engine Routing에 **편입 가능**하다 — 단, §9의 Validation Gate를
  통과한 뒤에만 실제 코드 Migration을 진행한다는 조건이 붙는다.
- `IMPLEMENTATION_RULES.md` "3번째 이상의 Engine 추가... 별도 RFC →
  ADC → ADR 대상" 요건은 `RFC-0041` → `ADC-0044` → 이 ADR로 충족된다.

## 9. Production Operational Validation Decision Status

**NOT YET DETERMINED(아래 두 항목은 §16 Gate 통과 기록으로 부분
갱신됨 — 각주 참조).**

Architecture Adoption(§5~§8)과 이 절은 명확히 분리된다 — Architecture
가 Production에 "적용 가능"하다는 것과 "실제로 안정적으로 동작한다"는
것은 다른 질문이다. 이 절의 원문(아래)은 ADR 최초 작성 시점의 기록을
그대로 보존한다 — §16이 그 이후 실측으로 새로 확인된 사실만 각주로
덧붙인다.

- **실제 quota 안정성**: 미확인. 모든 실측 시도가 계정 단위 일일
  quota 소진 상태에서 이뤄졌다(`OPENROUTER-FREE-MODEL-SELECTION-
  ARCHITECTURE-EXPERIMENT-0001.md` §5~§7, `STAGE05-ACTUAL-
  IMPLEMENTATION-REVALIDATION-0001.md` §4~§5 — 15/15 + 6/6 attempt
  전부 HTTP 429). **[§16 각주]** §10 Gate 실측(`ADR-0027-VALIDATION-
  GATE-EXECUTION-0001.md`) 중 일부 실제 OpenRouter 호출이 성공했으나,
  이는 이 환경의 Egress Proxy 경유 credential이었고 **사용자 소유
  Production 계정의 quota가 아니다** — "장기 quota 안정성"에 대한
  판단은 여전히 미확인으로 남는다.
- **실제 latency**: Stage 01~04는 이전 Auto Selection v1 실험에서
  일부 측정됐으나(Stage 01~03은 Fixed Model보다 빠름, Stage 04는
  느림 — `OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`), Stage
  05는 미확인. **[§16 각주]** 변경 없음 — 이번 Gate 실측도 latency를
  측정 대상으로 삼지 않았다.
- **실제 model quality**: 미확인 — 어느 실험도 실제 OpenRouter 선택
  결과의 품질을 평가하지 못했다(quota로 응답 자체를 못 받음).
  **[§16 각주]** §10 Gate 실측에서 실제 생성 코드 표본 2건(단순 함수
  추가/기존 함수 주석 추가)이 의도대로 정확히 생성됨을 관찰했으나,
  표본이 2건뿐이라 "model quality가 확인됐다"로 일반화하지 않는다 —
  미확인 상태 유지.
- **Stage 05 LLM Review quality**: 미확인 — `STAGE05-ACTUAL-
  IMPLEMENTATION-REVALIDATION-0001.md`가 구조(실제 Implementation
  전달)는 확정했지만 실제 Review 결과는 한 번도 관찰하지 못했다.
  **[§16 각주]** §10 Gate #11 실측(`OPENROUTER-MIGRATION-IDENTIFY-
  TARGET-FIX-0001.md`)으로 **최초로 실제 Review 결과를 1회 관찰**했다
  (`structural`/`specification_scope`/`design_scope` 전부 PASS,
  `code_review: "NO_ISSUES_FOUND"`) — placeholder가 아닌 실제 Stage 04
  Implementation에 대한 실제 LLM Review 응답이 처음으로 확보됐다.
  다만 표본 1건이므로 반복적·체계적 품질 평가가 끝났다고 확대
  해석하지 않는다.
- **long-term availability**: 미확인 — Free Pool 구성이 장기적으로
  안정적인지는 이 세션의 짧은 관찰 기간(반복 조회 간 순서 불변)만으로
  판단할 수 없다. **[§16 각주]** 변경 없음.
- **retry recovery**: 미확인 — 모든 실측에서 429 실패만 관찰됐고,
  실제로 다른 candidate로 성공적으로 회복되는 사례는 0건이다.
  **[§16 각주]** §10 Gate #9 실측(`ADR-0027-VALIDATION-GATE-9-10-
  RESOLUTION-0001.md`)으로 **실제 Production 코드의 retry 로직
  자체가 구조적으로 정상 동작함**(1차 실패→2차 회복, bounded 종료)을
  확인했다 — 단, 이는 로컬 결정론적 fault injection(실제 OpenRouter
  API 429 상황이 아님) 기반이다. **"실제 429 quota 상황에서 다른
  candidate로 회복되는 사례"는 여전히 0건으로 미확인** — 코드 레벨
  정상 동작 확인과 실제 quota 상황에서의 회복 실측은 서로 다른
  질문이며, 후자는 아직 답하지 않는다.

이 항목들 중 어느 것도 **"Migration을 승인할 수 없다"는 근거로
쓰지 않는다** — Architecture 자체의 결함이 아니라 실행 조건(quota)의
문제이기 때문이다(`ADC-0044` Q4). 대신 이 항목들은 §10 Validation
Gate로 옮겨, 실제 코드 Migration 착수 **전**에 통과해야 하는 조건으로
못박는다(§10 Gate 자체의 통과 여부는 §16 참조 — §9의 장기/체계적
Operational Validation과는 범위가 다르다).

## 10. Validation Gate — 실제 코드 Migration 착수 전 필수 확인

**확정한다**: 아래 항목을 전부 통과하기 전에는 Stage 01~05 Production
코드를 실제로 변경하지 않는다.

**Gate 통과 결과(§16 참조, 전부 PASS 확정)**:

1. Stage 01 Contract 회귀 없음(실제 OpenRouter 응답으로 재확인) — **PASS**
2. Stage 02 Contract 회귀 없음 — **PASS**
3. Stage 03 Contract 회귀 없음 — **PASS**
4. Stage 04 Contract 회귀 없음 — **PASS**
5. Stage 05 Contract 회귀 없음 — **PASS**
6. Free Pool availability(실행 시점 재조회로 확인) — **PASS**
7. Candidate ≤3 적용 확인(Production 경로에서) — **PASS**
8. `models[]` 요청 구성 정확성(Production 경로에서) — **PASS**
9. Retry 정상 동작(bounded, 최대 1회) — **PASS**
10. Failure classification(quota를 모델 품질 실패와 분리) — **PASS**
11. Stage 05가 실제 Stage 04 Implementation으로 Review를 수행하는지
    (Production 경로에서 최소 1회 실제 LLM 응답 확보) — **PASS**
12. Stage 01→05 전체 E2E 1회 이상 실제 통과 — **PASS**

**12개 항목 전부 PASS** — Evidence 및 판정 경위는 §16 참조.

**Quota failure는 이 Gate에서 별도 category로 분류한다** — quota
실패가 다른 실패(Contract 실패, malformed response 등)와 섞여 "Gate
실패"로 뭉뚱그려지지 않게 한다(`STAGE05-ACTUAL-IMPLEMENTATION-
REVALIDATION-0001.md` §5가 이미 구현·검증한 `429_quota` 분류 방식을
그대로 승계).

## 11. Migration Boundary

**확정한다**(`RFC-0041` §9 그대로):

- **변경 가능**: LLM Engine adapter(OpenRouter Adapter 신설),
  Model selection path, Free Pool discovery, Candidate filter,
  Candidate list, OpenRouter request construction.
- **변경 불가**: Stage responsibility, Agent responsibility,
  Capability boundary, Stage Contract, Output schema, Stage
  ordering, deterministic validation semantics.
- Migration 도중 Architecture 변경이 필요하다고 판단되면 Migration을
  중단하고 별도 RFC/ADC/ADR로 escalate한다 — 이 ADR이 승인한 범위를
  임의로 넘지 않는다.

## 12. Rollback

**확정한다**(`RFC-0041` §Rollback Strategy 그대로): OpenRouter
Selection Layer를 제거/비활성화하면 기존 Engine import로 즉시
복구된다(`ADR-0024` Option C의 "정적 import" 구조 덕분에 Rollback이
import 한 줄 수준으로 단순함). Rollback은 Stage Contract를 변경하지
않는다.

## 13. Consequences

- OpenRouter는 이제 Jarvis의 3번째 Production LLM Engine으로
  Governance 상 승인됐다 — 향후 세션이 "OpenRouter를 Production에
  쓸 수 있는가"를 처음부터 재검토할 필요가 없다.
- **[§16 갱신]** 이 ADR 최초 작성 시점에는 "실제 코드 Migration은
  아직 시작되지 않았다 — §10 Validation Gate를 통과해야만 착수
  가능하다"고 기록했다. 이후 사용자가 명시적으로 승인한 선(先) 배선
  (§16 §a 참조)과 그에 이은 §10 Gate 실측(§16)으로, **현재는 Stage
  01~05 Production 코드가 실제로 OpenRouter로 Migration됐고, §10
  Gate 12개 항목 전부 PASS로 확인됐다.** 이 문단은 원문 그대로 보존해
  "Gate 통과 전에는 Migration 근거로 인용할 수 없었다"는 당시의
  제약을 역사적으로 남긴다 — 현재 상태는 §16을 인용한다.
- Stage 01~05 Production 코드, Contract, Agent, Capability는 이
  ADR 자체(§5~§12 결정)로는 바뀌지 않았다 — 실제 코드 변경은 §16이
  기록하는 후속 구현 세션들에서 이뤄졌으며, 그 각각이 Contract/
  Responsibility/Ordering을 §11 Migration Boundary 안에서만 바꿨음을
  각 Evidence 문서가 개별적으로 확인했다.
- 다음 단계는 (a) ~~§10 Validation Gate 통과를 위한 별도 실측
  작업~~(§16으로 완료), (b) 사용자가 예고한 "Stage 01~05 Team
  Architecture Review"(Skeleton/Responsibility/Agent/Capability/DAG/
  Contract/Failure/Documentation 검증) — 이 ADR은 후자를 다루지
  않는다.

## 14. Production 확인

이 ADR **원문 작성 시점**의 커밋에서는 `git diff --stat -- hqs/`가
빈 결과였다(Evidence 문서 §git diff 절 참조) — 그 시점까지는
Production 코드가 전혀 바뀌지 않았다. **[§16 갱신]** 이후 §16이
기록하는 후속 세션들에서 Stage 01~05 Production 코드가 실제로
변경됐다 — 그 각각의 diff 범위/검증 결과는 해당 Evidence 문서에
개별적으로 기록돼 있으며, 이 ADR 문서 자체의 이번 수정(§10/§13/§16
갱신)은 Production 코드를 변경하지 않는다(문서 전용 변경).

## 15. Non-Goals

- Stage 01~05 Production `stage_0N.py`를 OpenRouter 경로로 재구현하는
  것 — 하지 않음(§10 Gate 통과 후 별도 작업).
- OpenRouter Adapter 코드를 작성하는 것 — 하지 않음.
- Stage Contract/Output schema를 변경하는 것 — 하지 않음.
- Central Engine Router/Gateway를 신설하는 것 — 하지 않음(§5 Engine
  Boundary가 명시적으로 배제).
- ChatGPT/Claude Code Engine을 OpenRouter로 대체하는 것 — 하지 않음
  (추가일 뿐, `ADR-0024`의 목적별 분리 원칙 유지).
- 특정 free 모델명, Stage-모델 매핑, scoring/ranking, LLM judge,
  latency/quality routing을 확정하는 것 — 하지 않음(`ADC-0044`
  "확정하지 않는 것" 그대로 승계).
- Stage 01~05 Team Architecture Review(Skeleton/DAG/Documentation
  검증) — 하지 않음(별도 후속 작업).
- 기존 RFC(`RFC-0040`, `RFC-0041`)/ADC(`ADC-0043`, `ADC-0044`)를
  수정하거나 완료 처리하지 않는다 — 그대로 Related로만 인용한다.

---

## Self Review

- Architecture Adoption과 Production Operational Reliability를
  하나로 뭉뚱그렸는가 — **아니오**(§8·§9가 명시적으로 분리, §9 전체가
  NOT YET DETERMINED로 남음).
- quota 소진으로 미확인된 항목을 확인된 것처럼 서술했는가 —
  **아니오**(§9가 6개 항목 전부 "미확인"으로 정직하게 기록).
- Stage 01~05 코드를 실제로 바꿨는가(이 ADR 원문 작성 시점 기준) —
  **아니오**(§14, §11 Migration Boundary가 이 ADR 자체의 범위를
  문서로 한정). **[§16 갱신]** 현재 시점 기준으로는 — **예**, 단
  §11 Migration Boundary(변경 가능 범위)를 벗어나지 않았음을 각
  후속 Evidence 문서가 개별 확인했다(§16).
- Central Router로 해석될 여지를 남겼는가 — **아니오**(§5 Engine
  Boundary, `ADR-0024` Option D와의 구조적 차이 유지).
- 특정 모델명/Stage 매핑/scoring/latency-routing/quality-routing을
  확정했는가 — **아니오**(§15 Non-Goals 전부 명시).
- 임의의 ADR 상태명을 만들었는가 — **아니오**(§Governance Status
  확인 — `ADR-0025`/`ADR-0026`과 동일하게 기존 "Accepted(Scoped)"
  어휘만 재사용).
- 기존 RFC/ADC/ADR을 임의로 수정하거나 완료 처리했는가 — **아니오**
  (`RFC-0040`/`RFC-0041`/`ADC-0043`/`ADC-0044`/`ADR-0026` 본문
  무수정, Related로만 인용).
- API Key/Credential을 탐색하거나 출력했는가 — **아니오**(이 ADR
  자체가 어떤 실행도 수행하지 않는다 — 순수 문서 작업).
- Production 코드를 변경했는가 — **아니오**(변경 범위는 이 ADR +
  `RFC-0041` + `ADC-0044` 문서 3건뿐, §14에서 재확인).

## 16. Gate 통과 기록(Post-Hoc Amendment, 2026-09-13)

이 절은 이 ADR이 §13에서 이미 예고한 "다음 단계 (a) §10 Validation
Gate 통과를 위한 별도 실측 작업"이 실제로 수행되고 완료된 사실을
사후에 기록한다 — 새로운 Architecture 결정이 아니라, 이 ADR
자신이 §10에서 이미 확정한 기준을 실측으로 충족했음을 확인하는
절차다. §5~§12의 결정 내용, §11 Migration Boundary, §15 Non-Goals는
이 절로 인해 전혀 바뀌지 않는다.

### a. §10 Gate 착수 전 배선(사용자 승인 Deviation)

§10은 "Gate를 전부 통과하기 전에는 Production 코드를 변경하지
않는다"고 확정했으나, 이후 세션에서 사용자가 "Gate 실측은 다음 날
별도로 수행하되, Stage import 배선은 오늘 먼저 진행한다"를 명시적으로
선택했다(`AskUserQuestion`, 옵션 2 — "오늘 Stage import까지 전부
전환"). 이는 §10 문언과 직접 상충하는 사용자 지시였고, 그 선택 자체를
문서화된 Deviation으로 기록해두었다(`OPENROUTER-PRODUCTION-ENGINE-
MIGRATION-IMPLEMENTATION-0001.md`) — Gate가 통과된 것으로 간주하지
않은 채로 진행했다.

### b. Gate 실측 경과

| 단계 | Evidence 문서 | 결과 |
|---|---|---|
| 1차 실측 | `ADR-0027-VALIDATION-GATE-EXECUTION-0001.md`(`c39eb26`) | #1/2/3/6/7/8 PASS, #9/10 BLOCKED(실사용 조건 미재현), #4/11/12 FAIL(신규 defect 발견: Stage 04 `identify_target()`이 여전히 `chatgpt_engine` 경유, quota 소진으로 항상 실패) |
| Scope Gap 분석 | `OPENROUTER-MIGRATION-SCOPE-GAP-IDENTIFY-TARGET-0001.md`(`40300a4`) | `identify_target()` 누락이 Governance 결정이 아니라 구현 단계의 `RFC-0041` 오인용이었음을 확인 — §11 "변경 가능" 범위 안이라 신규 RFC/ADC/ADR 불필요로 판정 |
| defect 수정 | `OPENROUTER-MIGRATION-IDENTIFY-TARGET-FIX-0001.md`(`8678327`) | `identify_target()`의 Engine을 OpenRouter로 전환(import 1줄, 판단 로직 무변경) → #4/#11 PASS 확정. #12는 별개 환경 문제(pytest interpreter 불일치)로 계속 FAIL |
| Gate #12 해결 | `ADR-0027-VALIDATION-GATE-12-RESOLUTION-0001.md`(`568e736`) | #12 FAIL의 원인이 순수 실행 environment 문제(파이프라인 실행과 회귀 테스트 실행이 서로 다른 Python interpreter를 씀)였음을 규명 — Production 코드/설정 수정 없이 올바른 interpreter로 재실행해 Stage 01→05 전체 `verdict: PASS` 실측 → #12 PASS 확정 |
| Gate #9/#10 해결 | `ADR-0027-VALIDATION-GATE-9-10-RESOLUTION-0001.md`(`9e96608`) | 기존 로컬 fake server 테스트 인프라(실제 OpenRouter egress 0회)로 retryable/terminal failure를 결정론적으로 재현 — bounded retry(정확히 2회, 무한 재시도 없음)와 quota/5xx/malformed/empty/connection 5개 분류의 배타성, 그리고 실제 Production 호출 경로(`identify_target`)에서 분류 결과가 Stage Contract를 깨지 않음을 실측 → #9/#10 PASS 확정 |

### c. 최종 결과

**§10 Validation Gate 12개 항목 전부 PASS.** 항목별 상세 판정과
실측 방법은 위 표의 각 Evidence 문서를 참조한다. Gate #9/#10은 실제
OpenRouter quota를 소모하지 않는 결정론적 fault injection으로
검증됐고, 나머지 항목은 최소 1회 이상의 실제 OpenRouter API 호출로
검증됐다(§16 §b 표 참조) — 이 구분(quota 소모 여부)은 각 Evidence
문서에 명시돼 있다.

### d. 이 절이 바꾸지 않는 것

- §9 Production Operational Validation(장기 quota 안정성/latency/
  체계적 model quality 평가/long-term availability)은 여전히 전부
  `NOT YET DETERMINED`다 — §10 Gate 통과와 §9는 범위가 다른 질문이다
  (§9 각주 참조).
- §11 Migration Boundary("변경 가능"/"변경 불가" 목록)는 그대로다 —
  §16 §b의 모든 후속 구현이 이 경계 안에서만 이뤄졌음을 각 Evidence
  문서가 개별 확인했다.
- §15 Non-Goals는 그대로다 — 특정 모델 고정, Stage-모델 매핑,
  scoring/ranking, LLM judge, latency/quality routing, Central
  Router는 여전히 어디에도 도입되지 않았다.
- 이 절 자체(문서 수정)는 Production 코드를 변경하지 않는다 — §16
  §b 표에 인용된 실제 코드 변경은 전부 그 시점의 개별 커밋
  (`8678327` 등)에서 이미 이뤄졌고, 이번 ADR 문서 수정은 그 사실을
  사후 기록할 뿐이다.

## Related

- `docs/architecture/core/RFC-0041-openrouter-production-engine-migration.md`
- `docs/architecture/core/ADC-0044-openrouter-production-engine-migration-decision.md`
- `docs/architecture/core/ADR-0026-openrouter-free-model-selection-architecture-boundary.md`
  (§10 Production Routing Integration NOT YET DETERMINED — 이 ADR이
  Accepted로 승격)
- `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`
  (2-Engine 구조, 3번째 Engine 추가의 절차적 근거, Central Router
  거부 선례)
- `docs/architecture/core/RFC-0040-openrouter-free-model-selection-architecture.md`,
  `docs/architecture/core/ADC-0043-openrouter-free-model-selection-decision.md`
  (Architecture Boundary 원 결정, 이 ADR이 재론하지 않고 승계)
- `hqs/development/IMPLEMENTATION_RULES.md`("Multi-Engine 허용 범위
  확인" 절)
- `docs/research/OPENROUTER-VALIDATION-0001.md`
- `docs/research/OPENROUTER-STAGE-MODEL-SELECTION-0001.md`
- `docs/research/OPENROUTER-MODELS-ARRAY-LIMIT-REVERIFICATION-0001.md`
- `docs/research/OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`
- `docs/research/STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`
- `docs/research/OPENROUTER-AUTO-SELECTION-V1-VALIDATION-0001.md`
- `docs/research/OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md`
- `docs/research/OPENROUTER-PRODUCTION-ENGINE-MIGRATION-IMPLEMENTATION-0001.md`(§16 §a)
- `docs/research/ADR-0027-VALIDATION-GATE-EXECUTION-0001.md`(§16 §b, 1차 실측)
- `docs/research/OPENROUTER-MIGRATION-SCOPE-GAP-IDENTIFY-TARGET-0001.md`(§16 §b, Scope Gap 분석)
- `docs/research/OPENROUTER-MIGRATION-IDENTIFY-TARGET-FIX-0001.md`(§16 §b, defect 수정)
- `docs/research/ADR-0027-VALIDATION-GATE-12-RESOLUTION-0001.md`(§16 §b, Gate #12 해결)
- `docs/research/ADR-0027-VALIDATION-GATE-9-10-RESOLUTION-0001.md`(§16 §b, Gate #9/#10 해결)
