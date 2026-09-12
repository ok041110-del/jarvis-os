# RFC-0037: Stage 04 Multi-Agent(Case A/B/C) + Ponytail Supervisor — Freeze 경계 확인 (구현 아님)

**Status**: Proposed (검토 대상, 결정 아님 — §8이 이 RFC의 핵심 결론이다)
**Author**: Claude Code(사용자 요청에 따른 Architecture Decision 조사)
**대상**: `hqs/development/stages/04_implementation/stage_04.py`,
`hqs/development/stages/04_implementation/architecture_validation/*`
(이 branch, PR #180이 이미 구현한 Validation Harness), `mvp/agents/backend.py`,
`mvp/ast_context.py`, `docs/architecture/core/ADR-0024`(별도 PR #183,
main 미병합), `docs/architecture/core/ADC-0039`(별도 PR #183, main
미병합), `docs/governance/rt/RT-0001.md`, `hqs/development/
IMPLEMENTATION_RULES.md`.

**요청 배경**: 사용자가 Stage 04 Implementation의 현재 Single-Agent
구조를 3개 Code Agent(implementation/consistency/minimality) +
Deterministic Gate + Ponytail Supervisor 구조로 전환할지 판단해
달라고 요청했다. 이 RFC는 main 기준 실제 코드/문서와, 같은 작업
단위인 PR #180(`claude/stage04-architecture-validation`, 이 브랜치
자신)이 이미 만든 Validation Harness·Evidence를 교차 검증한 결과를
기록한다.

**이 RFC가 확정하지 않는 것**: Production 코드 변경, Stage 04
workflow 변경, Multi-Agent/Ponytail 실제 구현, Engine Contract
변경. 이 RFC는 "지금 Multi-Agent Architecture를 Production으로
채택할 근거가 있는가"를 조사한 결과 **NOT DETERMINED — Real Engine
Evidence 필요**라는 결론에 도달했다(§8). 그래서 코드 변경 없이 이
RFC와 후속 ADC만 제출한다.

---

## 1. 현재 구조 조사(main `50db4c6` 기준, 실제 파일 재확인)

### 1.1 Stage 04 Production 구조(Case A, 현재)

`stage_04.py::run_stage_04()`:

```
Stage 03 design
      ↓
identify_target(design, candidate_index)     — Engine 호출 1회(Target 식별)
      ↓
_assemble_build_input(design, target, expose_target)   — Engine 미호출, 순수 조립
      ↓
backend_agent_code_generation(build_input)   — Engine 호출 1회(Code 생성)
      ↓
{target, implementation, expose_target}
```

문서(`README.md`/`CAPABILITIES.md`/`RESPONSIBILITY.md`/
`IMPLEMENTATION.md`/`VALIDATION.md`)와 실제 `stage_04.py` 코드를
줄 단위로 대조한 결과 **불일치 없음** — 3개 Capability(Target
Identification/Dependency Closure & Exposure 조립/Code Generation)
전부 문서가 서술한 그대로 구현돼 있다. `backend_agent_code_generation`
은 신규 Capability 없이 기존 `agents/backend.py`를 재사용한다
(`RESPONSIBILITY.md` "신규 Capability/Agent 추가" 금지 항목과 일치).

**중요한 정정**: Target Identification(`identify_target`)도 Engine
호출이다 — Code Generation 1회만 있는 것이 아니라 Stage 04 전체는
Production에서 Engine을 2회 호출한다. 다만 이번 Multi-Agent 제안은
Code Generation 단계만을 대상으로 하며(§2의 Controlled Variables가
Target을 Case별로 고정해 이 부분을 비교 대상에서 제외), Target
Identification은 A/B/C 어느 경우에도 무변경이다 — 이 RFC의 Engine
호출 횟수 비교(§5)도 이 범위(Code Generation 단계만)로 한정한다.

### 1.2 PR #180 Validation Harness 조사(같은 브랜치, 실제 코드 재확인)

`architecture_validation/variants.py`·`ponytail_adapter.py`·
`deterministic_checks.py`·`ponytail_policy.py`·`cases.py`·
`result_schema.py`·`run_experiment.py`를 전부 직접 읽고
`docs/research/DEV-HQ-V2.0-STAGE-04-ARCH-VALIDATION-0001.md`의
서술과 대조했다 — **서술과 코드가 정확히 일치한다**(불일치 0건).
재확인된 핵심 사실:

- **Case B**(`run_variant_b`): `implementation`/`consistency`/
  `minimality` 3개 고정 ID Agent가 **동일한 `build_input`**을 받아
  각각 1회씩 Engine을 호출한다(`_generate_and_gate_candidates`가
  순차 for-loop로 실행 — 실제 병렬 실행은 구현되어 있지 않다, §3.1
  재확인). Deterministic Gate(`syntax`/`scope`) 통과 후보 중 **고정
  ID 순서**(`implementation` < `consistency` < `minimality`)로 첫
  번째를 선택한다 — 이는 "품질이 가장 좋은 것을 고른다"가 아니라
  순서 무관성을 보장하는 tie-break일 뿐이다(`select_final_candidate`
  docstring이 이를 명시).
- **Case C**(`run_variant_c`): B와 **완전히 동일한 3개 후보**를
  재사용한다(`_generate_and_gate_candidates` 공유 호출, 추가 Engine
  호출 없음). `ponytail_adapter.select_final_candidate()`는 B와
  **동일한 함수**다 — 즉 현재 구현된 "Ponytail"은 실제 LLM 판단이
  전혀 없는 고정 ID 순서 선택기다. `ponytail_adapter.py` 자신의
  docstring이 "이것은 실제 Ponytail Supervisor가 아니다"라고 명시한다.
- **Engine 호출 횟수(harness 기준, 재확인)**: A=1, B=3, **C=3**(B와
  동일 — Ponytail이 추가 Engine을 호출하지 않기 때문). 사용자가 이번
  요청에서 가정한 "Case C = LLM 4회"는 **현재 구현·Evidence와
  일치하지 않는다** — 4번째 호출은 "실제 LLM 판단을 하는 Ponytail
  Supervisor"를 새로 만들 때만 발생하며, 그런 Supervisor는 이 branch
  포함 저장소 어디에도 아직 구현되어 있지 않다(§5에서 두 시나리오를
  분리해 비교한다).

### 1.3 Real Engine Evidence 상태(재확인)

이 세션 컨테이너에도 `OPENAI_API_KEY`/`OMNIROUTE_BASE_URL`/
`OMNIROUTE_API_KEY` 등 Engine 관련 환경변수가 전혀 없다(직접 확인,
`env | grep`). PR #180 문서가 기록한 "OmniRoute unavailable" 제약이
이번 세션에도 그대로 유지된다 — 이 RFC도 실제 Engine 실행을 시도하지
않는다(BLOCKED, §11에서 재확인).

### 1.4 Multi-Engine(ADR-0024, PR #183, main 미병합)과의 교차 확인

**중요한 전제 명시**: `ADR-0024`(Multi-Engine Architecture: ChatGPT/
Claude Code)는 이 조사 시점에 **main에 아직 병합되지 않았다**(별도
PR #183, 이 세션이 이전에 작성). 이 RFC는 `ADR-0024`가 승인된
상태를 **가정**하고 그 위에서 Stage 04 Multi-Agent 구조의 타당성을
검토한다 — `ADR-0024`가 병합되지 않으면 아래 §4의 Engine 배정 논의는
적용 대상이 없다(Case A 그대로, `backend_agent_code_generation`은
여전히 OmniRoute 단일 호출).

---

## 2. Multi-Agent 독립성 — 실제 확인(추측 아님, 사용자 지시 §3 10개 질문에 답함)

1. **세 Code Agent가 동일 Design/Target/Scope를 입력받으면 실제로
   독립적으로 실행 가능한가?** — **예, 구조적으로는 그렇다.**
   `_generate_and_gate_candidates`가 각 Agent에게 완전히 동일한
   `build_input`을 전달하고, 서로 다른 Agent의 출력을 참조하는 코드
   경로가 없다(정적 확인, `variants.py` 전문 재확인). 단, **현재
   구현은 순차 실행**이다(for-loop) — "실행 가능"은 데이터
   의존성이 없다는 뜻이지, 지금 코드가 실제로 동시 실행한다는 뜻이
   아니다. 실제 동시 실행을 구현하려면 `IMPLEMENTATION_RULES.md`
   "Execution Host 구현 허용 범위(Scoped, ADC-0015)" — Process 1차,
   Subprocess 대안, **Thread 사용 금지** — 를 그대로 따라야 한다(이
   RFC는 그 구현에 착수하지 않는다).
2. **각 Agent가 다른 Agent의 결과를 필요로 하는가?** — **아니오.**
   세 Agent 모두 Stage 03 `design` + AST closure(+ 선택적 Exposure)
   로만 구성된 동일 입력을 받는다. 서로의 출력에 의존하는 코드는
   없다.
3. **Agent 간 결과를 LLM 없이 deterministic하게 비교/병합할 수
   있는가?** — **부분적으로만.** `deterministic_checks.py`가 syntax/
   AST 구조/Contract/Scope/Design Coverage/Dependency Validity/
   Comment-Docstring 정책 **7종**을 LLM 없이 결정론적으로 검사할 수
   있다(전부 실측 가능, PR #180 §6.1 재확인). 그러나 이 7종은
   "정답인가/정책을 지켰는가"만 판정하며, **"여러 정답 후보 중 어느
   것이 더 좋은가"는 판정하지 못한다** — 그 역할은 현재 고정 ID
   tie-break(`select_final_candidate`)가 대신하고 있을 뿐, 실제
   품질 비교가 아니다. `quality_heuristics.py`의 explicitness/
   simplicity 두 지표가 구조적 근사치를 제공하지만, Readability/
   Cognitive Load/Maintainability는 여전히 결정론적으로 측정할
   방법이 없다(PR #180 §11, 사람 또는 LLM-judge 필요, 방법론
   미결정).
4. **deterministic gate만으로 Ponytail의 역할을 충분히 대체할 수
   있는가?** — **아니오.** Deterministic Gate는 "틀린 후보를
   걸러내는 안전망" 역할만 한다 — 걸러지고 남은 여러 정답 후보 중
   최선을 고르는 것은 Gate의 설계 범위 밖이다(질문 3의 결론과 동일
   근거). 지금 그 자리를 메우는 것은 "품질 판단"이 아니라 "순서
   무관성을 보장하는 임의 tie-break"다 — 이것이 실제 Ponytail
   판단을 대체한다고 볼 수 없다.
5. **Ponytail이 실제로 필요한 판단은 무엇인가?** — 구조적으로 셀 수
   없는 축: Readability(변수명/함수 목적의 명확성), Cognitive
   Load(새 개발자가 추론해야 하는 양), 기존 코드 스타일과의 의미적
   일관성(`consistency` Agent의 의도를 실제로 판정하는 것) — 전부
   §3 질문의 결론과 동일선상에 있다.
6. **Ponytail이 후보 선택만 하면 되는가?** — 현재 Evidence(0%
   refinement로 설계된 Adapter, `ponytail_policy.py`의 4개
   guardrail이 전부 "무수정"을 전제로 공허하게 PASS)는 **선택만
   하는 것을 기본 모드로 가정**하고 있다. 그러나 이것이 충분한지는
   실제 LLM 판단 없이는 검증되지 않았다(Evidence 없음).
7. **Ponytail이 코드를 수정해야 하는 상황이 실제로 존재하는가?** —
   **Not Determined.** PR #180의 5개 합성 Case 중 어느 것도 실제
   Engine으로 실행된 적이 없어, "선택만으로 부족해 수정이 필요했던"
   실제 사례가 관찰된 바 없다.
8. **Ponytail이 코드를 수정할 경우 제한 방법은?** — §6에서 별도로
   확정한다(기존 `ponytail_policy.py`의 4개 guardrail을 그대로
   인용·확장).
9. **3개 Agent의 추가 LLM 호출 비용이 실제 품질 향상으로
   정당화되는가?** — **Not Determined.** 비용은 구조적으로 3배(§5),
   품질 향상은 실측치가 전혀 없다(Not Determined, 추정하지 않음).
10. **현재까지 확보된 Evidence만으로 Production Architecture를
    승인할 수 있는가?** — **아니오.** §8에서 이 결론을 공식화한다.

---

## 3. Case A/B/C 비교

| 기준 | Case A(현재) | Case B(3 Agent + Gate) | Case C(B + Ponytail, **현재 구현대로**: controlled selector) |
|---|---|---|---|
| Engine 호출 횟수(Code Gen 단계만) | 1 | 3 | 3(추가 호출 없음) |
| 병렬 실행 가능성 | 해당 없음 | 구조적으로 가능(데이터 의존 없음), **현재 코드는 순차 실행** | B와 동일 |
| 실제 독립성 | 해당 없음 | 확인됨(§2 Q1·Q2) | B와 동일 |
| Dependency | 없음 | 없음(3개 모두 동일 입력만 소비) | B와 동일 + Ponytail이 B의 후보 목록에 의존(순수 소비, 재생성 없음) |
| Latency | 기준 | B ≈ 3×generation(순차 실행 시) | C ≈ B + Ponytail Adapter 실행 시간(현재는 수 ms 미만, 순수 Python 비교) |
| Cost | 기준 | ≈3× Engine 비용 | B와 동일(실제 Ponytail Supervisor 도입 시에만 추가 비용) |
| Implementation complexity | 낮음(현재 Production) | 중간(Deterministic Gate 7종 이미 구현·테스트됨, PR #180) | 중간+(Ponytail 자리 확보, 단 실제 Supervisor는 미구현) |
| Failure handling | 단일 실패 = 전체 실패(`_engine_failure_message`) | 3/3~0/3 등급 정책 이미 테스트됨(3/3·2/3 정상, 1/3 제한적 진행, 0/3 실패) | B와 동일 |
| Deterministic validation 가능 범위 | 동일(Gate 자체는 A에도 적용 가능) | syntax/AST/contract/scope/design-coverage/dependency-validity/comment-policy 7종 | B와 동일 + Ponytail policy guardrail 4종(현재 공허하게 PASS) |
| Code quality 개선 가능성 | Not Determined(기준) | Not Determined(후보가 늘어난다고 품질이 느는지 실측 없음) | Not Determined(현재 selector는 품질 판단을 하지 않음 — §2 Q4) |
| Semantic consistency | 해당 없음(단일 후보) | 구조적 근사(explicitness/simplicity)만 가능, 의미적 일관성은 미판정 | B와 동일 |
| Maintainability | Not Determined | Not Determined(Result Schema에 전용 필드 없음, simplicity로 근사) | B와 동일 |
| Stage 05와의 연결성 | 무변경(Contract 그대로) | 무변경(Best Candidate만 `implementation`으로 반환하면 Contract 동일) | B와 동일 |

**참고 시나리오(현재 미구현, 실제 LLM 판단 Ponytail Supervisor 도입
시)**: Engine 호출 = 4(3 + Ponytail 1), Cost ≈ B의 1.33배, Latency는
Ponytail의 실제 추론 시간만큼 추가. 이 시나리오는 §6에서 권한
범위만 정의하고, 이 RFC는 그 실제 구현 여부를 결정하지 않는다.

---

## 4. Multi-Engine(ADR-0024 가정)과의 결합 검토

`ADR-0024`(main 미병합, §1.4)가 승인된 상태를 가정할 때:

- **Code Generation은 Claude Code Engine이 담당하는 것이 적절한가?**
  — `ADR-0024` Stage Mapping이 이미 `backend_agent_code_generation`을
  Claude Code Engine에 배정했다(Implementation 목적). Case B/C의 3개
  Agent(`implementation`/`consistency`/`minimality`)가 전부 동일한
  "코드 생성" 목적이므로, 이 배정을 그대로 3개 모두에 적용하는 것이
  일관적이다 — 3개 중 일부만 다른 Engine을 쓸 근거는 현재 Evidence에
  없다.
- **Ponytail은 ChatGPT Engine이 담당하는 것이 적절한가?** — Ponytail의
  역할(§2 Q5 — Readability/Cognitive Load/Semantic Consistency 판단)은
  `ADR-0024`가 ChatGPT에 배정한 "Review" 역할과 개념적으로 가장
  가깝다. 단, 이는 **실제 Ponytail Supervisor가 도입될 때만** 의미가
  있는 배정이다 — 지금의 controlled selector(§1.2)는 Engine을 전혀
  호출하지 않으므로 이 질문 자체가 적용되지 않는다.
- **Deterministic Gate는 Engine 호출 없이 실행 가능한가?** — **예,
  이미 그렇게 구현되어 있다**(§1.2, §2 Q3 — `deterministic_checks.py`
  전체가 `ast`/`builtins` stdlib만 사용, LLM 미호출).
- **Engine Router/Gateway 없이 위 구조를 구현할 수 있는가?** — **예.**
  `ADR-0024`가 이미 승인한 패턴(파일 import 시점에 Engine을 정적으로
  고정) 그대로, 3개 Code Agent가 각각(또는 함께) `from ..engine
  import call_engine`을 쓰고, 실제 Ponytail Supervisor가 생기면
  별도 파일에서 `from ..chatgpt_engine import call_engine_via_chatgpt`
  를 쓰면 된다 — Router는 필요 없다.
- **Multi-Agent와 Multi-Engine을 결합할 때 새로운 Architecture/
  Contract 변경이 필요한가?** — **아니오.** Engine Contract(`str ->
  str`)는 무변경으로 충분하다(3개 Agent 모두 이미 이 Contract로
  호출됨, PR #180 §1.5와 동일 결론 구조). Stage 04 Public Contract
  (`target`/`implementation`/`expose_target`)도 무변경 — 여러 후보 중
  하나만 최종적으로 `implementation`에 담기면 되므로 Contract 모양이
  달라지지 않는다.

**결론**: Multi-Engine과 Multi-Agent는 **서로 독립적인 결정**이며,
결합 자체가 새 Architecture Decision을 요구하지 않는다. 다만
"실제로 결합해도 되는가"는 두 결정이 각각 승인된 이후에만 의미가
있다 — `ADR-0024`는 아직 main에 없고(§1.4), 이 RFC의 Multi-Agent
채택 여부는 §8에서 NOT DETERMINED다.

---

## 5. Cost 관점 분석(사용자 지시 §5)

| Case | LLM 호출 수(Code Gen 단계) | 근거 |
|---|---|---|
| A | 1 | Production `stage_04.py` 재확인 |
| B | 3 | `variants.py::run_variant_b`(`_generate_and_gate_candidates`) 재확인 |
| C(현재 구현: controlled selector) | **3**(사용자 가정 4가 아님) | `ponytail_adapter.py`가 Engine을 호출하지 않음 — §1.2 재확인 |
| C(참고, 실제 Ponytail Supervisor 도입 시) | 4 | 아직 미구현 — 이 RFC가 결정하지 않음 |

추가 LLM 비용 vs 품질 향상 vs 실행 시간 증가 vs 구현 복잡성 증가:

- **추가 LLM 비용**: B/C 모두 A 대비 구조적으로 3배(Not Determined
  절대 금액 — 실제 Engine 단가·토큰 수 Evidence 없음).
- **품질 향상**: **Not Determined**(추정하지 않음 — 실제 Engine
  Evidence 전무, §1.3).
- **실행 시간 증가**: 순차 실행 시 B/C ≈ 3×generation latency, 병렬
  실행 시(미구현) 이론상 최대 1×generation + 약간의 오버헤드 — 실제
  값은 Not Determined.
- **구현 복잡성 증가**: 낮음~중간으로 실측 가능(코드 diff 크기,
  PR #180 기준 신규 파일 8개 + 테스트 20개, Production 코드 무변경) —
  이는 "품질 향상이 그 복잡성을 정당화하는가"와는 별개 질문이며, 이
  RFC는 후자를 Not Determined로 유지한다.

---

## 6. Ponytail 역할 제한(사용자 지시 §6 반영, `ponytail_policy.py` 재확인)

현재 코드(`ponytail_policy.py`)가 이미 구현한 4개 guardrail:

| 허용/금지 항목(사용자 지시) | 코드 대응 | 상태 |
|---|---|---|
| Target 변경 금지 | `check_target_unchanged` | 구현됨 |
| 새 dependency 추가 금지 | `check_no_new_imports` | 구현됨 |
| Scope 확대 금지 | `check_scope_unchanged`(최상위 함수 집합 불변) | 구현됨 |
| 이미 충분히 좋은 후보는 무수정 | `check_no_op_when_gate_passed` | 구현됨 |
| 다른 파일 수정 금지 | 코드 검사 대상 아님 — Harness가 애초에 파일을 쓰지 않아 구조적으로 항상 만족 | 구조적으로 충족 |
| Architecture/Contract 변경 금지 | 별도 코드 검사 없음(위 4개가 사실상 이 역할을 겸함) | 부분 커버 |
| Governance 우회 금지 | 코드로 강제 불가능한 절차 규범 — 이 RFC/ADC 문서 자체가 그 절차를 지킨다 | 문서 절차로만 보증 |
| **금지 영역 요구 시 실패/에스컬레이션** | **미구현** — 현재는 `verify_policy()`가 `passed: False`만 반환하고, 이를 Stage 04 실패로 승격하거나 사람에게 에스컬레이션하는 경로가 없다 | **Gap — §9 Validation Requirement로 기록** |

## 7. Comment/Docstring Policy 반영 확인

`deterministic_checks.py::check_comment_docstring_policy`/
`find_comments_and_docstrings`가 이미 "2줄 초과 comment/docstring"을
결정론적으로 탐지한다 — 사용자가 이번에 재확인을 요청한 정책
(Self-documenting Code First, WHY만 허용, 최대 2 lines, comment
최적화로 code logic을 바꾸지 않음)과 실제 코드가 일치한다:
`_annotate_result`가 채우는 `comments.code_changed_for_comment`는
Harness가 comment 압축을 위해 코드를 리라이트하지 않으므로 구조상
항상 `False`다(PR #180 §12 재확인, 코드 직접 대조로 일치 확인).
`ponytail: marker` 같은 명시적 예외 마커는 현재 코드 어디에도
구현되어 있지 않다 — 실제 Ponytail Supervisor가 생기면 그 표시가
필요한지 별도로 판단해야 한다(Not Determined, 새로 추가하지 않음).

---

## 8. 이 RFC의 결론(요약)

- **조사 완료**: Stage 04 Production 구조, PR #180 Harness 전체
  코드, Multi-Agent 독립성(10개 질문), Multi-Engine 결합 영향,
  Cost/Ponytail 권한 범위 — 전부 실제 코드 근거로 확인했다.
- **정정한 사실**: 사용자가 가정한 "Case C = LLM 4회"는 현재 구현
  기준 부정확하다 — 현재 Ponytail은 controlled selector로 추가
  호출이 없어 C=3이다. 실제 LLM 판단 Ponytail을 도입하면 C=4가
  된다(§5).
- **구현하지 않음**: Multi-Agent Production 채택은 실제 Engine
  Evidence(품질·비용·지연시간) 없이는 판정할 수 없다 — CLAUDE.md
  Frozen Architecture 규칙에 따라 RFC 단계에서 멈추고, 후속 ADC로
  이 결론을 공식화한다(§9).
- **Contract 변경**: 없음(필요하다면 없어도 된다는 것까지만 확정,
  §4).
- **Architecture 변경**: 없음(제안만, Case A Freeze 그대로 유지).

## 9. 후속 절차 제안(실행하지 않음, 제안만)

1. **ADC**: 이 RFC의 결론(NOT DETERMINED)을 공식 Decision으로
   등록하고, Production 채택에 필요한 Validation Requirement(실제
   Engine Evidence, Ponytail 실패/에스컬레이션 경로 설계, Quality
   평가 방법론 확정)를 명시한다 — `ADC-0040`.
2. **ADR**: NOT DETERMINED이므로 이번에 작성하지 않는다(TRANSITION
   판정 시에만 필요, 사용자 지시 §11 원칙과 동일 구조).
3. 실제 OmniRoute 또는 ChatGPT/Claude Code Engine이 확보되면
   `run_experiment.run_all(real_engine_call)`을 실행해 실제
   Evidence를 만든다 — 이 RFC는 그 실행에 착수하지 않는다.
