# ADC-0040: Stage 04 Multi-Agent(Case A/B/C) + Ponytail Supervisor Decision (RFC-0037 후속)

## 목적

`RFC-0037-stage04-multi-agent-ponytail-boundary.md`의 조사를 근거로,
Stage 04 Implementation의 Case A(현재 Single Agent)/B(3 Code Agent +
Deterministic Gate)/C(B + Ponytail Supervisor) 중 어느 것을
Production Architecture로 채택할지 공식 Decision을 내린다. 이 ADC는
`RFC-0037`의 조사 내용(Independence 확인, Cost 분석, Ponytail 권한
범위)을 재론하지 않고 그 결론 위에서 KEEP/RE-EVALUATE(=NOT
DETERMINED)/TRANSITION 중 하나를 판정한다(`ADC-0039` 판정 구조와
동일 원칙).

---

## Q1. Evidence 충분성 재확인

`RFC-0037` §8이 이미 확인한 대로, Real Engine(OmniRoute 또는
ChatGPT/Claude Code) Evidence가 **전무**하다(이번 세션도 `env`에
Engine 관련 변수 없음을 직접 재확인). PR #180이 만든 Validation
Harness는 **Harness 자체로서는 Ready**(orchestration/Deterministic
Gate 7종/Ponytail policy guardrail/Failure Policy 4단계 전부 테스트로
고정, 20/20 PASS)이지만, 실제 코드 품질·비용·지연시간 비교는 단
한 건도 수행되지 않았다.

이 저장소의 다른 Decision들(`RT-0001`의 "1회 관찰은 Evidence로
인정하지 않는다", `IMPLEMENTATION_RULES.md` "Dynamic Workflow
재검토 Trigger"의 반복 관찰 요구)과 동일한 기준을 적용하면, **0건의
실제 관찰**은 그 기준에 명백히 미달한다.

## Q2. Case A 유지가 여전히 안전한 선택인가

**예.** Case A는 이미 Production에서 동작 중이며(`stage_04.py`,
`test_stage_04.py` 9건 PASS), Multi-Agent로 전환하지 않아도 Stage 04
Public Contract·Stage 05 연결성 어느 것도 위험에 처하지 않는다.
Case A를 유지하는 데 드는 추가 비용은 없다 — 이는 `ADC-0039`
Amendment 이전 상황(Single Engine 유지가 "실행 불가능"까지는 아니고
단지 "확인되지 않은 개선 가능성을 포기하는 것"에 그침)과 유사한
구조다.

## Q3. Ponytail 권한 범위가 지금 확정될 수 있는가

**부분적으로만.** `RFC-0037` §6이 확인한 대로 `ponytail_policy.py`의
4개 guardrail(Target 불변/새 import 금지/Scope 불변/이미 통과한
후보 무수정)은 이미 코드로 구현·테스트됐다 — 이 부분은 지금
확정해도 안전하다. 그러나 "금지 영역을 요구할 때 실패/에스컬레이션"
경로는 미구현이며, 이는 실제 Ponytail Supervisor가 존재하지 않는 한
검증할 대상 자체가 없다 — Production 채택 여부와 별개로, 이 Gap은
지금 기록만 하고 지금 메우지 않는다(구현 금지, 사용자 지시 §10).

---

## Decision

**NOT DETERMINED — Real Engine Evidence Required.**

`ADOPT`(Case B 또는 C 승인)/`KEEP`(Case A 확정 Freeze)/`REJECT`
어느 것도 이번 세션에서 근거를 갖추지 못했다. 사용자 지시 §8이
명시한 대로 "Evidence가 부족하면 억지로 Production Architecture를
승인하지 말라"는 원칙을 그대로 따른다 — 특히 Real Engine Evidence가
0건인 상태에서 Multi-Agent Production Architecture를 확정하지
않는다.

### 이 Decision이 하는 것

- Case A(현재 Single Agent)를 **잠정 유지**한다 — 이는 "Case B/C가
  틀렸다"는 판정이 아니라 "아직 판정할 수 없다"는 것이다.
- PR #180의 Validation Harness를 **Architecture Validation 도구로
  공식 인정**한다 — 향후 실제 Engine이 확보되면 이 Harness를 통해서만
  Evidence를 수집한다(새 Harness를 다시 만들 필요 없음).
- `RFC-0037`이 정정한 사실(Case C 현재 구현 = LLM 3회, 실제 Ponytail
  Supervisor 도입 시에만 4회)을 공식 기록으로 확정한다 — 향후 어떤
  세션도 "Case C = 4회"를 근거 없이 전제하지 않는다.

### 이 Decision이 하지 않는 것

- Multi-Agent/Ponytail의 실제 구현(Agent 코드, Deterministic Gate의
  Production 배선, `stage_04.py` 수정) — 전부 미착수.
- Engine Contract·Stage 04 Public Contract 변경 — 전부 무변경.
- `ADR-0024`(Multi-Engine, main 미병합)와의 실제 결합 — `RFC-0037`
  §4가 "결합 자체는 새 Architecture Decision을 요구하지 않는다"고
  확인했을 뿐, 결합을 승인하지 않는다(두 결정 모두 아직 main에
  확정되지 않았으므로 결합할 대상 자체가 없다).
- Ponytail 실패/에스컬레이션 경로 설계(Gap으로만 기록, §Validation
  Requirements 4번).

---

## Validation Requirements — Case B/C를 재판정하려면 필요한 것

1. **실제 Engine 실행**: `run_experiment.run_all(real_engine_call)`을
   OmniRoute 또는 ChatGPT/Claude Code Engine이 실제로 확보된 뒤
   실행해, A/B/C 15건(5 Case × 3 Variant, Code Gen 단계만)의 실제
   `correctness`/`quality`/`comments`/`cost`/`latency`를 수집한다.
2. **Quality 평가 방법론 확정**: Readability/Cognitive Load/
   Maintainability를 Human rubric/LLM Judge/Human+LLM Judge 중
   무엇으로 측정할지 결정한다(`RFC-0037`/PR #180 §11 선택지 인용,
   이 ADC는 그중 하나를 임의로 고르지 않는다).
3. **비용 정당화 판단**: 1번 Evidence로 "3배 비용이 실제 품질
   향상으로 정당화되는가"에 실측 근거로 답한다(현재는 Not
   Determined).
4. **Ponytail 실패/에스컬레이션 경로 설계**: 실제 Ponytail
   Supervisor를 도입하기 전에, 금지 영역(Architecture/Contract/
   Target/Scope 변경, Governance 우회)을 요구하는 응답이 나왔을 때
   무엇으로 승격되는지(Stage 04 실패? 사람 에스컬레이션? 원 후보로
   fallback?)를 별도로 설계·문서화한다.
5. **병렬 실행 여부**: 실제로 3개 Agent를 동시 실행할지(Latency
   개선 목적)는 `IMPLEMENTATION_RULES.md` Execution Host 허용
   범위(ADC-0015, Process/Subprocess만, Thread 금지)를 그대로
   따라야 하며, 이 결정도 별도 확인이 필요하다(순차 실행으로도
   Case B/C 채택은 가능 — 병렬화는 독립적인 최적화 질문).

## Open Questions

- `ADR-0024`(Multi-Engine)가 main에 병합되지 않으면, Case B/C가
  실제로 채택되더라도 3개 Code Agent는 현재처럼 단일 Engine
  (OmniRoute 또는 `engine.py`)만 호출하게 된다 — 이 경우도 Cost
  구조(3배)는 동일하게 적용된다.
- Result Schema에 Agent별 개별 cost/latency 필드가 없다(PR #180 §15
  Remaining Issues) — 실제 Engine 연결 시점에 세분화가 필요한지는
  그때 판단한다.

## ADR 여부

**이번 세션에서 ADR을 작성하지 않는다.** Decision이 TRANSITION이
아니라 NOT DETERMINED이므로, `ADC-0039`가 세운 것과 동일한 원칙
("RE-EVALUATE/NOT DETERMINED라면 ADR을 선행 작성하지 않는다")을
그대로 따른다.

## 구현 금지 확인

이 ADC는 다음을 하지 않았다: `stage_04.py` 변경, Agent 구현,
Engine 변경, Contract 변경, Multi-Agent/Ponytail Production 배선.
문서 2건(이 ADC + `RFC-0037`)만 추가했다.

## Self Review

- Real Engine Evidence 없이 Production Architecture를 승인했는가 —
  **아니오**(NOT DETERMINED로 명시).
- 사용자가 가정한 Case C=4회를 그대로 인용했는가 — **아니오**
  (`RFC-0037`이 실제 코드로 정정: 현재 구현은 3회, 참고 시나리오로만
  4회를 별도 표기).
- PR #180의 기존 Evidence/Harness를 재론하거나 중복 구현했는가 —
  **아니오**(그대로 인용, 새 Harness 없음).
- Ponytail에 무제한 권한을 부여했는가 — **아니오**(§Ponytail 권한
  범위는 `RFC-0037` §6이 기존 4개 guardrail을 그대로 인용, Gap만
  추가 기록).
- Comment/Docstring Policy(2줄 제한, WHY만 허용)를 반영했는가 —
  **Pass**(`RFC-0037` §7, 기존 코드와 일치 확인).
- Multi-Agent와 Multi-Engine을 하나의 결정으로 섞었는가 — **아니오**
  (`RFC-0037` §4 — 두 결정이 독립적임을 확인했을 뿐, 결합을 승인하지
  않음).
- 코드를 작성했는가 — **아니오**.
- commit/push/PR을 수행했는가 — 이 파일 작성 이후 별도로 수행한다.

## Related

- `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md`
- `hqs/development/stages/04_implementation/architecture_validation/`(PR #180, 이 branch)
- `docs/research/DEV-HQ-V2.0-STAGE-04-ARCH-VALIDATION-0001.md`(PR #180, 이 branch)
- `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`(PR #183, main 미병합)
- `docs/architecture/core/ADC-0039-multi-engine-re-evaluation.md`(PR #183, main 미병합)
- `docs/governance/rt/RT-0001.md`
- `hqs/development/IMPLEMENTATION_RULES.md`
