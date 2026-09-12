# ADC-0044: OpenRouter Production Engine Migration — Decision (RFC-0041 후속)

## 목적

`RFC-0041-openrouter-production-engine-migration.md`가 제안한
"OpenRouter를 3번째 Production Engine으로 추가하고 Stage 01~05를
Free Model Selection Architecture로 Migration 가능하게 만든다"는
제안을 채택할지 공식 Decision을 내린다.

---

## Q1. 3번째 Engine 추가 절차(IMPLEMENTATION_RULES.md)를 충족하는가

**예.** `hqs/development/IMPLEMENTATION_RULES.md` "Multi-Engine 허용
범위 확인" 절은 "3번째 이상의 Engine 추가... 별도 RFC → ADC → ADR
대상"이라고 명시했다. `RFC-0041` → 이 ADC → 후속 `ADR-0027`이 정확히
그 절차다. 절차 자체의 충족 여부는 형식적으로 확인 가능하며, 이 ADC가
그 형식 요건이 채워졌음을 확정한다.

## Q2. Jarvis Engine selection과 OpenRouter 내부 selection의 구분이
    실제로 유지되는가

**예.** `RFC-0041` §Engine Boundary가 A(Jarvis Engine selection —
파일 단위 정적 import, 여전히 정확히 하나의 모듈)와 B(OpenRouter
내부 Free Model selection — OpenRouter 책임)를 명확히 나눴다. A
층위에 런타임 조건 분기나 Central Router가 추가되지 않는 한, 이
구분은 `ADR-0024`의 Option C(2-Engine 정적 선택)가 이미 확립한
원칙과 구조적으로 동일하다 — Engine 모듈 개수만 2개에서 3개로 늘어난
것이지, 선택 방식 자체(정적 import)는 바뀌지 않는다.

## Q3. Architecture Boundary(Free Pool/Filter/Candidate Selection)는
    Production Adoption을 위한 근거가 충분한가

**예, 이 세 부분에 한해서만.** `OPENROUTER-FREE-MODEL-SELECTION-
ARCHITECTURE-EXPERIMENT-0001.md`가 실제 Pool 데이터로 5개 Candidate
Case(0/1/2/3/>3) 전부를 재현했고, tie-break 규칙이 15회 실행에서
일관되게 적용됨을 확인했다. 이 세 단계(Free Pool 조회 → Deterministic
Filter → Candidate Selection)는 **코드/데이터 근거로 완결 가능한
질문**이었고 실제로 완결됐다.

## Q4. OpenRouter 실제 선택/Contract Validation/Retry 회복까지
    Production Adoption 근거가 있는가

**아니오 — 이 질문은 Architecture Adoption과 분리한다.** 두 Evidence
(`OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`,
`STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`)가 이 부분을
검증하려 시도했으나, 세션 내내 계정 단위 일일 quota가 소진된 상태여서
15/15, 이어서 6/6 attempt가 전부 HTTP 429로 실패했다. **이는
Architecture의 결함이 아니라 실행 조건(quota)의 문제**이지만,
"Production에서 실제로 안정적으로 동작하는가"라는 질문에는 이
Evidence로 답할 수 없다. 이 Gap은 Architecture Adoption 여부와
분리해서, Production Operational Validation이라는 별도 축으로
남긴다(§Decision).

## Q5. `ADC-0043`/`ADR-0026`과 충돌하는가

**아니오.** `ADC-0043`이 확정한 것(Free Pool 기반/deterministic
filtering/maximum 3/OpenRouter delegation/Contract Validation 유지,
특정 모델명·Stage 매핑·scoring·routing 미확정)을 이 ADC는 그대로
승계하며 재론하지 않는다. `ADC-0043`이 명시적으로 확정하지 않은
"Production Routing 편입 여부"만 이번에 별도로 다룬다 — 이는 `ADC-0043`
§Validation Requirements 5번("Production Routing 편입 여부의 별도
Governance 판단")이 이미 예견한 다음 단계다.

---

## Decision

**PARTIAL — Architecture Production Adoption ACCEPTED(경로 구성 한정),
Production Operational Reliability는 별도 Validation 대상으로 유지.**

### 확정하는 것 — Architecture/Governance 결정

- **OpenRouter Production Engine 도입**: OpenRouter를 Jarvis의 3번째
  Production LLM Engine으로 승인한다(`ADR-0024`의 2-Engine 구조를
  대체가 아니라 확장).
- **Free Model Pool 사용**: Production에서 OpenRouter `:free` 목록을
  실제로 조회해 후보 소스로 쓴다.
- **Deterministic Filter**: free 여부/capability/context/modality/
  Contract compatibility만으로 후보를 거른다 — 품질 추정 금지.
- **최대 3 Candidate**: `models[]` API-level 상한을 그대로 승계.
- **OpenRouter `models[]` 위임**: 실제 모델 선택/failover는 OpenRouter
  책임으로 확정.
- **Contract Validation 유지**: 기존 Stage Contract 검증 로직은
  모델 선택 경로와 무관하게 그대로 유지.
- **Stage별 fixed model mapping 제거**: Stage 코드에 특정 모델명을
  두지 않는다는 원칙을 Production 요건으로 확정.
- **Stage Contract 유지**: Stage 01~05의 기존 Input/Output Contract는
  전부 보존(변경 없음).
- **기존 ChatGPT/Claude Engine architecture와의 관계**: 대체가 아니라
  **추가**다 — `ADR-0024`의 Reasoning(ChatGPT)/Implementation(Claude
  Code) 목적별 분리 원칙은 훼손되지 않는다.

### 확정하지 않는 것 — 아래는 이 ADC가 명시적으로 보류한다

- 특정 free model 이름.
- 특정 Stage의 모델 매핑.
- OpenRouter 내부 selection algorithm.
- 복잡한 scoring/ranking.
- historical quality score.
- latency-based routing.
- LLM-based model judge.

이 항목들은 Implementation/Validation 단계 또는 별도 Architecture
변경(새 RFC → ADC → ADR) 대상으로 남긴다 — 이번 결정이 이들을 암묵적
으로 승인한 것으로 해석되지 않는다.

### 이 Decision이 하는 것

- `RFC-0041`의 Architecture(Free Pool → Filter → ≤3 → `models[]` →
  OpenRouter → Stage Execution → Contract Validation)를 Production
  적용 가능한 것으로 공식 확정한다.
- `IMPLEMENTATION_RULES.md`의 3번째 Engine 절차 요건이 충족됐음을
  기록한다.
- Production Operational Validation(§11 Validation Gate, `ADR-0027`
  담당)이 통과하기 전까지는 **실제 Stage 01~05 코드를 Migration하지
  않는다**는 전제를 명시한다 — Architecture Adoption ≠ 즉시 코드
  변경.

### 이 Decision이 하지 않는 것

- Stage 01~05 실제 코드 변경 — 전부 미착수(이번 ADC는 문서만).
- OpenRouter Adapter 구현 — 미착수.
- 특정 Stage의 실제 Migration 순서/시점 결정 — 미착수.
- Production 환경의 Credential 주입 방식 확정 — 미착수(`RFC-0041`
  §Open Questions).

---

## Validation Requirements — Production Operational Reliability를
재판정하려면 필요한 것

1. **Quota 비소진 상태에서의 실제 실행**: 현재까지의 모든 실측
   시도(`OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-
   0001.md`, `STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`)가
   quota 소진 상태에서 이뤄졌다 — quota가 정상인 상태에서 Stage
   01~05 각각 OpenRouter 실제 선택/Contract Validation/Retry 회복이
   실제로 동작하는지 재실측이 필요하다.
2. **Stage 05 Review 실제 품질 확인**: 실제 LLM Review 결과를 최소
   1회 이상 얻어, `STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`
   §6이 준비해 둔 Deterministic 기준선(AST/Dependency PASS)과 비교
   한다.
3. **E2E(Stage 01→05) 실행**: 개별 Stage 단위가 아니라 전체 파이프
   라인을 OpenRouter 경로로 한 번 이상 실제로 통과시킨다.
4. **Quota 정책 확정**: `RFC-0041` §Open Questions가 남긴 "quota
   초과 시 정책"(유료 전환/기존 Engine 복귀/실행 실패)을 결정한다.
5. **Rollback 실제 리허설**: `RFC-0041` §Rollback Strategy가 설계한
   "import 한 줄 되돌리기"가 실제로 문제없이 동작하는지 최소 1회
   확인한다.

## Open Questions

- Migration을 Stage별로 순차 적용할지, 5개 Stage를 동시에 적용할지 —
  Not Determined(`RFC-0041` §Migration Scope가 개별 적용 가능성만
  열어둠).
- Free Pool 조회 실패/후보 0개 시 기존 Engine으로 자동 전환할지 —
  Not Determined(자동 전환 로직 자체가 §Rejected Alternatives의
  "동적 Engine 선택"과 경계가 모호해질 위험이 있어 신중한 검토 필요).
- Production 환경(이 세션의 Egress Proxy가 아닌 실제 배포 환경)의
  Credential 관리 방식 — Not Determined, 이 ADC의 조사 범위 밖.

## ADR 여부

**이번 세션에서 ADR을 작성한다(`ADR-0027`).** `ADR-0025`/`ADR-0026`이
이미 세운 선례("Architecture/Boundary 확정은 Accepted, Operational/
Production 세부 Validation은 별도 유보")와 동일한 패턴이다 — 단, 이번
ADR은 `ADR-0026`과 달리 **"Production Routing Integration" 자체를
처음으로 Accepted로 승격**한다는 점에서 이전 ADR들과 구분된다(§Decision
문구, `ADR-0027`이 이를 명확히 표시).

## 구현 금지 확인

이 ADC는 다음을 하지 않았다: Stage 01~05 코드 변경, OpenRouter
Adapter 구현, Engine import 변경, Contract 변경, 기존 Agent/
Capability 코드 변경. 문서 3건(이 ADC + `RFC-0041` + 후속 `ADR-0027`)
만 추가한다.

## Self Review

- Architecture Adoption과 Production Operational Reliability를
  하나로 뭉뚱그렸는가 — **아니오**(§Decision이 명시적으로 분리,
  Q4 참조).
- quota 소진으로 확인하지 못한 부분을 확인된 것처럼 서술했는가 —
  **아니오**(Q4, §Validation Requirements 1번이 명시적으로 재실측
  필요성을 남김).
- Stage05 Auto Selection v1의 PARTIAL 판정을 PASS로 과장했는가 —
  **아니오**(`RFC-0041` §Evidence References가 원 판정을 그대로 인용).
- 특정 모델명/Stage 매핑/scoring/latency-routing/quality-routing을
  확정했는가 — **아니오**(§Decision "확정하지 않는 것" 전부 명시).
- Central Router로 해석될 여지를 남겼는가 — **아니오**(Q2, `RFC-0041`
  §Engine Boundary·§Rejected Alternatives와 함께 명시적으로 배제).
- `ADC-0043`/`ADR-0026`과 충돌하는가 — **아니오**(Q5).
- 코드를 작성했는가 — **아니오**.
- commit/push/PR을 수행했는가 — 이 파일 작성 이후 별도로 수행한다
  (PR은 사용자 지시에 따라 생성하지 않는다).

## Related

- `docs/architecture/core/RFC-0041-openrouter-production-engine-migration.md`
- `docs/architecture/core/ADC-0043-openrouter-free-model-selection-decision.md`
  (Architecture Boundary 선행 확정, 이번에 재론하지 않고 승계)
- `docs/architecture/core/ADR-0026-openrouter-free-model-selection-architecture-boundary.md`
  (§10 Production Routing Integration NOT YET DETERMINED — 이번에
  Accepted로 승격)
- `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`
  (2-Engine 구조, 이번 3번째 Engine 추가의 절차적 근거)
- `hqs/development/IMPLEMENTATION_RULES.md`("Multi-Engine 허용 범위
  확인" 절)
- `docs/research/OPENROUTER-FREE-MODEL-SELECTION-ARCHITECTURE-EXPERIMENT-0001.md`,
  `docs/research/STAGE05-ACTUAL-IMPLEMENTATION-REVALIDATION-0001.md`,
  `docs/research/OPENROUTER-STAGE-PRODUCTION-MIGRATION-EVIDENCE-0001.md`
