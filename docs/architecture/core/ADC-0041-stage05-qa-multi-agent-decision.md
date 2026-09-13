# ADC-0041: Stage 05 QA Multi-Agent/Parallel Decision (RFC-0038 후속)

## 목적

`RFC-0038-stage05-qa-multi-agent-boundary.md`의 조사를 근거로, Stage 05
Validation의 Case A(현재, Code Review만)/B(Code Review + QA Agent,
Deterministic Gate)/C(B + 병렬 실행 + Deterministic Aggregation) 중
어느 것을 Production Architecture로 채택할지 공식 Decision을 내린다.
`ADC-0040`(Stage 04 Multi-Agent, 동일 판정 구조)과 같은 원칙을
따른다 — `RFC-0038`의 조사 내용(독립성 확인, Cost 분석, QA Agent
실제 미호출 확인)을 재론하지 않고 그 결론 위에서 판정한다.

---

## Q1. Evidence 충분성 재확인

`RFC-0038` §0.2·§2.6이 이미 확인한 대로, QA Agent
(`qa_agent_test_execution`)는 Stage 05(v2.0 Validation) 경로로 **단
한 번도 실행된 적이 없다**(정의만 존재, `teams/README.md` 자신도 이를
"정의는 존재, 미호출"로 기록). Real Engine Evidence(품질·비용·
지연시간)는 **0건**이다.

이 저장소의 다른 Decision들(`ADC-0040` Q1의 동일 기준, `RT-0001`의
"1회 관찰은 Evidence로 인정하지 않는다")과 같은 기준을 적용하면,
**0건의 실제 관찰**은 명백히 미달이다.

## Q2. Case A 유지가 여전히 안전한 선택인가

**예.** Case A(Code Review만)는 이미 Production에서 동작 중이며
(`stage_05.py`, `test_stage_05.py`), 변경하지 않아도 Stage 05 Public
Contract·상위 Workflow 연결성 어느 것도 위험에 처하지 않는다. Case A를
유지하는 데 드는 추가 비용은 없다.

## Q3. RFC-0038이 발견한 추가 제약(Stage 04에는 없던 것)이 지금 확정될 수 있는가

**아니오, 오히려 새 Open Item을 만든다.** `RFC-0038` §2.2가 확인한 대로
`qa_agent_test_execution(code, review)`의 현재 시그니처는 Code Review
출력에 의존한다 — Stage 04의 B/C(완전 독립 3-Agent)와 달리, Stage 05의
QA Agent는 **Contract를 바꾸지 않는 한 병렬화 자체가 불가능**하다. 이
제약을 지금 풀지(시그니처 재설계) 여부는 Real Engine Evidence 확보와
별개로 이미 결정 대상이며, 이 ADC는 그 설계에 착수하지 않는다(구현
금지, §Validation Requirements 3번).

---

## Decision

**NOT DETERMINED — Real Engine Evidence Required.**

`ADOPT`(Case B 또는 C 승인)/`KEEP`(Case A 확정 Freeze)/`REJECT` 어느
것도 이번 세션에서 근거를 갖추지 못했다. Real Engine Evidence가 0건인
상태에서 Multi-Agent Production Architecture를 확정하지 않는다
(`ADC-0040`과 동일 원칙).

### 이 Decision이 하는 것

- Case A(현재, Code Review만)를 **잠정 유지**한다 — "Case B/C가
  틀렸다"는 판정이 아니라 "아직 판정할 수 없다"는 것이다.
- `RFC-0038`이 발견한 QA Agent의 실제 Contract 의존성(§2.2, Code
  Review 출력에 의존)을 공식 기록으로 확정한다 — 향후 어떤 세션도
  "QA Agent가 Stage 04의 B/C처럼 완전 독립적"이라고 근거 없이
  전제하지 않는다.
- `RFC-0030` §3(Stage 05 ③)의 "완전 독립 Fan-out" 서술이 현재 QA
  Agent 시그니처 기준으로는 부정확함을 기록한다 — `RFC-0030` 본문은
  수정하지 않고(역사적 기록 보존, `ADC-0036` §Decision 2와 동일
  원칙), 이 ADC와 `RFC-0038`을 교차 참조로만 남긴다.

### 이 Decision이 하지 않는 것

- QA Agent의 실제 활성화(Stage 05 호출부 추가) — 미착수.
- QA Agent 시그니처 재설계(`review` 의존 제거) — 미착수.
- `stages/05_validation/RESPONSIBILITY.md`/`VALIDATION.md`/
  `stages/contracts.py` 변경 — 전부 무변경.
- Engine Contract·Stage 05 Public Contract 변경 — 전부 무변경.

---

## Validation Requirements — Case B/C를 재판정하려면 필요한 것

1. **QA Agent Contract 재설계 여부 결정**: 현재 시그니처(`code, review`)를
   유지한 채 순차(Sequential Handoff, Stage 04 Target Identification →
   Code Generation과 동형)로 채택할지, 아니면 `review` 의존을 제거한
   독립 변형을 새로 설계해 병렬 채택할지 — 이 선택 자체가 별도 판단
   대상이다.
2. **실제 Engine 실행**: 1번의 선택 이후, 실제 Engine(ChatGPT/Claude
   Code)으로 QA Agent를 Stage 05 경로에서 최소 1회 이상 실행해 실제
   테스트 케이스 제안 품질을 확인한다.
3. **Quality 평가 방법론 확정**: 제안된 테스트 케이스가 "유용한가"를
   Human rubric/LLM Judge 중 무엇으로 측정할지 결정한다(`ADC-0040`
   Validation Requirement 2번과 동일 성격의 질문).
4. **비용 정당화 판단**: 2배 비용(§RFC-0038 §5)이 실제 테스트 커버리지/
   품질 향상으로 정당화되는가에 실측 근거로 답한다(현재 Not
   Determined).
5. **Contract 확장 절차**: `VerificationResult`에 QA Agent 출력을
   담을 신규 필드를 추가하려면 별도 RFC → ADC → ADR(`ADR-0009` Public
   Scope 변경 절차, `VALIDATION.md` 자신이 명시)을 거친다 — 이 ADC는
   그 절차를 대신하지 않는다.

## Open Questions

- QA Agent를 병렬 실행하려면 `IMPLEMENTATION_RULES.md` "Execution
  Host 허용 범위" 또는 Stage 01의 `ParallelRunner`(ThreadPoolExecutor
  기반, ADR-0021 Production Adopted) 재사용 중 무엇을 따를지는 별도
  확인이 필요하다 — `ParallelRunner`가 LLM API 호출(I/O-bound)
  병렬화를 이미 Production에서 다루고 있어 유력한 재사용 후보이지만,
  이 ADC는 그 채택을 확정하지 않는다.
- `qa_agent_test_execution`의 `review` 의존을 제거하는 것이 QA Agent의
  판단 품질을 떨어뜨리는지(Review 없이 테스트 케이스를 제안하는 것이
  더 나쁜 제안으로 이어지는지)는 Not Determined — 이는 §Validation
  Requirements 2번의 실제 Evidence가 있어야 답할 수 있다.

## ADR 여부

**이번 세션에서 ADR을 작성하지 않는다.** Decision이 TRANSITION이 아니라
NOT DETERMINED이므로, `ADC-0040`이 세운 것과 동일한 원칙을 따른다.

## 구현 금지 확인

이 ADC는 다음을 하지 않았다: `stage_05.py` 변경, QA Agent 활성화,
Engine 변경, Contract 변경, `RESPONSIBILITY.md`/`VALIDATION.md` 변경.
문서 2건(이 ADC + `RFC-0038`)만 추가했다.

## Self Review

- Real Engine Evidence 없이 Production Architecture를 승인했는가 —
  **아니오**(NOT DETERMINED로 명시).
- RFC-0030의 "완전 독립" 전제를 그대로 인용했는가 — **아니오**
  (`RFC-0038` §2.2가 실제 코드로 정정: 현재 시그니처는 Code Review
  출력에 의존).
- Stage 04(`ADC-0040`)와 동일한 판정 구조·엄밀성을 적용했는가 —
  **Pass**(Q1~Q3, Decision, Validation Requirements 형식 동일).
- 코드를 작성했는가 — **아니오**.
- commit/push/PR을 수행했는가 — 이 파일 작성 이후 별도로 수행한다
  (PR은 사용자 지시에 따라 생성하지 않는다).

## Related

- `docs/architecture/core/RFC-0038-stage05-qa-multi-agent-boundary.md`
- `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md`(동일
  판정 구조 선례)
- `docs/architecture/core/RFC-0030-dev-hq-stage-agent-team-boundary-analysis.md`
- `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`
- `hqs/development/stages/05_validation/`
- `hqs/development/mvp/agents/qa.py`, `hqs/development/mvp/parallel_runner.py`
