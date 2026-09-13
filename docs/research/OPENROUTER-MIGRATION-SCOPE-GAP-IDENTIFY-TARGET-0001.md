# `identify_target()` OpenRouter Migration Scope Gap — Architecture 분석

**Date**: 2026-09-13
**Branch**: `claude/jarvis-openrouter-validation-bin9aj`
**전제 Evidence**: `docs/research/ADR-0027-VALIDATION-GATE-EXECUTION-0001.md`(commit `c39eb26`) — 이 문서는 보존하며 수정하지 않는다.
**작업 성격**: 분석/판정만 수행. Production 코드(`identify_target()` 포함) / RFC / ADC / ADR 문서는 이번 세션에서 전혀 수정하지 않는다.

## Summary

- `identify_target()`이 여전히 `chatgpt_engine.py`를 쓰는 것은 **Governance가
  의도적으로 결정한 예외가 아니라, `RFC-0041`/`ADC-0044`/`ADR-0027` 어디에도
  다뤄지지 않은 순수 구현 단계의 호출 경로 추적 누락**이다.
- 그런데 이 호출부는 `ADR-0024`가 **명시적으로 "Reasoning 성격"이라는
  이유로 ChatGPT에 배정**했던 지점이다(§4) — 단순 "깜빡함"이 아니라
  실제로는 "Reasoning 성격의 호출은 OpenRouter Migration 대상이 될 수
  있는가"라는, `RFC-0041`이 이미 Stage 01 Reasoning Agent들에게 적용한
  것과 **동일한 질문**이다.
- 결론: `identify_target()`을 OpenRouter로 전환하는 것은 `ADR-0027` §11이
  이미 승인한 "변경 가능" 범위(LLM Engine adapter / Model selection
  path) 안에 있다 — **새 RFC/ADC/ADR은 필요 없다**. 다만 `ADR-0024`
  §Stage Mapping 표의 해당 행과 `test_engine_boundary.py`/Migration
  Evidence의 "out of scope" 서술이 부정확했으므로, **Evidence 레벨의
  정정 기록**은 필요하다(Governance 문서 자체 수정 아님).
- 이번 세션에서는 이 판정만 내리고, `identify_target()` 코드/테스트/
  Engine adapter는 수정하지 않는다(사용자 명시적 지시).

## 1~2. ADR-0027/RFC-0041/ADC-0044 재확인 + 호출 경로 추적

- `RFC-0041` §Migration Scope(145행~): "바뀌는 것 = Stage가 LLM 응답을
  얻는 경로"만 규정하고, Stage 단위로 "독립적으로 Migration 여부를
  판단할 수 있다"고만 명시한다. **개별 함수/호출부 단위의 포함·제외를
  언급하지 않는다.**
- `RFC-0041`/`ADC-0044`/`ADR-0027` 세 문서 전체를 `identify_target`/
  `workflow_ast_context`로 grep한 결과 **0건** — 세 문서 중 어디에도
  이 함수가 언급된 적이 없다. 즉 "제외한다"는 결정을 Governance
  차원에서 내린 적이 없다.
- 실제 호출 경로(`stage_04.py::run_stage_04()`, 코드 재확인):
  ```
  Stage 03 design
        ↓
  identify_target(design, candidate_index)      — Engine 호출 1회, chatgpt_engine.py
        ↓
  _assemble_build_input(...)                     — Engine 미호출(순수 조립)
        ↓
  backend_agent_code_generation(build_input)     — Engine 호출 1회, openrouter_engine.py(이미 Migration됨)
        ↓
  {target, implementation, expose_target}
  ```
  `identify_target`은 `run_stage_04()` 최상단에서 **무조건, 매 실행마다**
  호출된다(조건 분기 없음) — Stage 04의 "필수" LLM 호출이지 부가
  경로가 아니다.

## 3. `c39eb26` Evidence와의 대조

`ADR-0027-VALIDATION-GATE-EXECUTION-0001.md`(§F/발견된 defect)가 실측한
그대로다: 실제 E2E 2회 실행 모두 `identify_target()` 단계에서
`RuntimeError: ChatGPT rate limit exceeded (HTTP 429): ... insufficient_quota`
로 실패했고, OpenRouter로 이미 전환된 `backend_agent_code_generation`에는
도달조차 하지 못했다. 정적 분석(import 확인)만으로는 이 호출부가 실행
경로상 얼마나 치명적인지 드러나지 않았고, 실제 실행으로만 발견됐다 —
이는 "Migration Scope 판단이 실제 호출 그래프가 아니라 파일명/추정에
의존했다"는 근본 원인과 정확히 일치한다.

## 4. 기존 Migration Boundary에서 제외된 경위

두 개의 서로 다른 층위의 "제외"가 섞여 있었다:

1. **`ADR-0024`(2-Engine 구조, `RFC-0041` 이전)** — Stage Mapping 표
   (167행)에서 `identify_target`을 **명시적으로 ChatGPT에 배정**했다.
   사유: "Design 텍스트를 읽고 판단하는 Reasoning 성격이 Code 자체를
   생성하는 것보다 강하다고 판단." 이것은 실수가 아니라 **의도된
   Architecture 판단**이었다 — 다만 이 판단은 "ChatGPT vs Claude Code"
   2択 안에서 내려진 것이지, "OpenRouter가 3번째 선택지로 추가된 이후"를
   전제하지 않았다.
2. **`RFC-0041`/`ADC-0044`/`ADR-0027` Migration 구현 단계(이번 세션
   이전)** — `test_engine_boundary.py`의 실제 주석(38~40행)은
   "`workflow_ast_context.py`는 실제 Stage 01~05 파이프라인 호출부가
   아니다... 이번 Migration 범위(`RFC-0041` §Migration Scope) 밖"이라고
   적어 **마치 RFC-0041이 이렇게 결정한 것처럼 서술**했다. 그러나 §1~2에서
   확인했듯 `RFC-0041` 본문은 이 파일/함수를 한 번도 언급하지 않는다 —
   이 서술은 **구현 세션이 파일명("workflow_XXXX" MVP 계열)과 "T18
   Evidence 당시 스냅샷"이라는 과거 맥락만으로 내린 추정**이었고, 실제
   호출 그래프(`stage_04.py`가 이 함수를 직접 import·호출)를 재확인하지
   않은 채 Governance 문서를 잘못 인용했다.

즉 "왜 제외됐는가"의 답은: **①은 정당한 과거 결정(2-Engine 시절
Reasoning/Generation 구분), ②는 그 이후 벌어진 잘못된 인용/추정에
의한 실무적 누락**이다. `RFC-0041` 자신은 어느 쪽도 결정한 적이 없다.

## 5. 현재 Architecture상 `identify_target()`이 Stage 04 필수 LLM 호출임을 확인

- `RFC-0037`(Team04 Multi-Agent/Ponytail 제안, `ADC-0040` NOT DETERMINED
  — 검증됨, 이번 세션에서 재열람) 56~62행이 이미 "**중요한 정정**:
  Target Identification(`identify_target`)도 Engine 호출이다 — Stage 04
  전체는 Production에서 Engine을 2회 호출한다"고 명시적으로 기록해뒀다.
  이는 별도 RFC가 이미 같은 사실을 확인해둔 선행 Evidence다.
- `RFC-0030`(Stage/Agent 경계 분석, Proposed) #5도 `identify_target`을
  "Stage 04가 직접 호출, `mvp/agents/`에 없음"으로 별도 분류했다 — 이
  함수가 formal Agent로 등록되지 않은 채 실제 Engine 호출을 수행하는
  존재임은 이전부터 알려져 있었다.
- 오늘 실측(`c39eb26`)으로 "알려져 있던 사실"이 "실행 시 Stage 04를
  100% 차단하는 실제 defect"로 격상됐다 — Architecture 문서상으로는
  이미 명확했던 필수 호출이, 실제로는 하나도 검증되지 않은 채 방치돼
  있었다.

## 6. "OpenRouter Migration Scope에 포함해야 하는가" — Architecture 관점 분석

찬성 근거:

- `identify_target`은 `ADR-0024`가 스스로 분류한 "Reasoning 성격"의
  호출이다. Stage 01의 4개 Reasoning Agent(`reasoning.py`)는 **동일한
  Reasoning 성격**으로 이미 `RFC-0041`/`ADR-0027`에 의해 OpenRouter로
  전환됐다. 같은 성격의 호출을 하나는 전환하고 하나는 방치할 architectural
  근거가 없다 — 오히려 일관성 위반에 가깝다.
- `ADR-0027` §11 Migration Boundary의 "변경 가능" 목록(LLM Engine
  adapter, Model selection path)에 정확히 해당한다. Stage
  Responsibility/Agent Responsibility/Capability Boundary/Contract/
  Output Schema/Stage Ordering/deterministic validation semantics —
  "변경 불가" 목록 중 어느 것도 건드리지 않는다. `identify_target`의
  Input(`design`, `candidate_index`)/Output(`(module_name,
  function_name)` 튜플 또는 `None`) 계약은 전혀 바뀌지 않는다 — 단지
  그 출력을 만드는 Engine 모듈만 바뀐다.
- Rollback도 기존과 동일하게 import 한 줄 수준(§12 그대로 승계 가능).

반대/유보 근거(검토했으나 기각):

- "Reasoning 성격이라 ChatGPT가 더 적합하다"는 `ADR-0024`의 원래
  판단 자체를 재론해야 하는 것 아닌가? → **아니다.** `ADR-0024`가
  비교한 것은 "ChatGPT vs Claude Code" 2개 Engine 중 어느 것이 이
  Reasoning 작업에 더 적합한가였다. `RFC-0041`/`ADR-0027`은 이미
  "OpenRouter도 Reasoning 성격 호출에 쓸 수 있다"를 Stage 01에서
  선례로 확정했으므로, 이 질문은 새로운 질문이 아니라 **이미 답이 나온
  질문을 다른 호출부에 동일하게 적용하는 것**이다.
- `RFC-0037`(Team04 Multi-Agent 제안)이 `identify_target`을 "A/B/C
  어느 경우에도 무변경"이라고 못박지 않았나? → 그 문서는 **Code
  Generation 단계의 병렬/Ponytail 실험 범위를 한정**하기 위해
  Target을 고정한 것이지(§2 Controlled Variables), `identify_target`의
  **Engine 선택**을 결정한 것이 아니다. 서로 다른 질문이다.

**결론**: 포함하는 것이 Architecture적으로 타당하고, 기존 승인 범위
(`ADR-0027` §11) 안에서 실행 가능하다.

## 7. RFC/ADC/ADR amendment 또는 신규 Governance 기록 필요 여부

**필요 없음(신규 RFC/ADC/ADR 불필요)** — 이유:

- `ADR-0027` §11이 이미 "LLM Engine adapter / Model selection path"
  변경을 승인해뒀고, `identify_target`의 Engine 전환은 정확히 이
  범주다. 새로 승인받을 권한이 없는 게 아니라, **이미 받은 승인을
  아직 다 쓰지 않은 상태**다.
- Stage Contract/Responsibility/Ordering 등 "변경 불가" 목록은 전혀
  건드리지 않는다.

다만 아래는 **Governance 문서 수정이 아닌 Evidence 레벨 정정**으로
별도 필요하다(이번 세션에서 하지 않음, 향후 구현 세션 때 함께 처리
권고):

- `test_engine_boundary.py`(38~40행) 주석이 "이번 Migration 범위
  (`RFC-0041` §Migration Scope) 밖"이라고 `RFC-0041`을 잘못 인용한
  부분 — 실제로 그 문서가 결정한 바 없음을 바로잡는 주석 수정.
- `docs/architecture/core/ADR-0024-multi-engine-architecture-adoption.md`
  167행 Stage Mapping 표는 **역사적 기록으로는 그대로 두되**(그 시점의
  올바른 결정이었음), `identify_target`의 Engine이 이후 `ADR-0027`
  Migration으로 바뀌었다는 사실을 인용하는 쪽(Migration Evidence 문서)에서
  명확히 밝히면 된다 — `ADR-0024` 자체는 Frozen Architecture 원칙상
  직접 수정 대상이 아니다.

## 8. 기존 ADR-0027 권한 범위를 넘는지 여부

**넘지 않는다.** §6/§7의 분석대로 §11 "변경 가능" 범위 안이므로, 사용자
지시 8번("범위를 넘는 변경이면 구현하지 않는다")에 해당하지 않는다 —
구현 자체는 이미 허가된 범위 안의 작업이다. 다만 이번 세션에서는
**분석만 하고 구현하지 않는다**(사용자 지시 9/11).

## 최종 정리

### Scope Gap
`identify_target()`(`mvp/workflow_ast_context.py:41`, `stage_04.py`가
무조건 호출)이 `ADR-0027` OpenRouter Migration에서 누락됐다. 원인은
Governance의 의도적 제외가 아니라, 구현 단계에서 `RFC-0041`을
잘못 인용해 "범위 밖"이라 잘못 판단한 것 — 실제로는 `RFC-0041`이
한 번도 다룬 적 없는 호출부다.

### Architecture 영향
없음 — 전환해도 Stage 04의 Responsibility/DAG 위치/`_assemble_build_input`
조립 순서는 그대로다. `identify_target`이 "Reasoning 성격"이라는
`ADR-0024`의 분류 자체도 바뀌지 않는다(단지 그 Reasoning을 수행하는
Engine 모듈만 바뀐다).

### Contract 영향
없음 — Input(`design`, `candidate_index`)/Output(`target` 튜플 또는
`None`) 형태는 전혀 바뀌지 않는다. Stage 04의 반환 Contract(`target`/
`implementation`/`expose_target` 3키)도 무변경.

### Governance 필요 여부
새 RFC/ADC/ADR **불필요**. `ADR-0027` §11이 이미 승인한 범위 안의
구현 완성 작업이다. Evidence 레벨 정정(주석 1건)만 권고.

### 구현해야 할 변경 범위(향후, 이번 세션 아님)
- `mvp/workflow_ast_context.py` 11행의
  `from .chatgpt_engine import call_engine_via_chatgpt as call_engine`를
  `from .openrouter_engine import call_engine_via_openrouter as call_engine`로 변경(한 줄).
- `test_engine_boundary.py`의 `OPENROUTER_ROUTED_FILES`/`CHATGPT_ROUTED_FILES`
  목록에서 이 파일 재분류(`CHATGPT_ROUTED_FILES`가 공집합이 됨 —
  해당 테스트/목록 처리 방식 조정 필요).
- 위 변경으로 인해 재발할 것으로 예상되는 회귀 테스트(예:
  `test_chatgpt_routed_files_import_chatgpt_engine_only`)를 이전
  Migration 때와 동일한 방식(§3 "의도된 변화" 패턴)으로 갱신.
- `identify_target()`을 OpenRouter로 전환한 뒤 `c39eb26`과 동일한 방식의
  실측 재실행(Stage 04가 실제로 Target을 식별하고 Code Generation까지
  도달하는지) — 이는 Gate 항목 #4/#11/#12 재검증에 해당한다.

### 구현하지 말아야 할 범위
- `identify_target()`의 판단 로직(어떤 함수를 Target으로 고를지) 자체
  변경 — Engine 모듈만 바뀌고 판단 방식은 그대로.
- `_assemble_build_input`/`_EXPOSURE_POLICY_INSTRUCTION`/Exposure
  Policy 충돌 처리 로직 — Engine 호출이 없는 순수 조립 로직이므로
  이번 Scope Gap과 무관, 손대지 않는다.
- `ADR-0024`/`RFC-0030`/`RFC-0037`/`ADC-0040` 등 기존 Governance
  문서의 직접 수정 — Frozen Architecture 원칙상 항상 금지.
- Stage 04의 3-Agent(`implementation`/`consistency`/`minimality`)+
  Ponytail Production 도입 — 이는 `ADC-0040`이 별도로 NOT DETERMINED로
  유보한, 이번 Scope Gap과 무관한 완전히 다른 주제.
- 새 Agent 추가, 새 routing/scoring 로직, 특정 free 모델 하드코딩 —
  이번 분석과 무관하게 항상 금지 사항.

## Architecture / Contract / Governance / Production Code / Validation Gate / Branch / Commit / PR

- Architecture: 무변경(분석 문서만 작성).
- Contract: 무변경.
- Governance: RFC/ADC/ADR 어느 것도 수정하지 않음 — 새 Governance
  기록도 이번엔 만들지 않음(§7 결론: 불필요).
- Production Code: **무변경** — `identify_target()`/`workflow_ast_context.py`/
  `test_engine_boundary.py` 전부 이번 세션에서 손대지 않았다.
- Validation Gate(`ADR-0027` §10): 여전히 **OPEN** — 이번 분석은 Gate
  판정을 바꾸지 않는다. Gate 항목 #4/#11/#12는 `identify_target()` 전환
  및 재실측 이후에만 재평가 가능하다.
- Branch: `claude/jarvis-openrouter-validation-bin9aj`
- Commit: 본 문서 커밋 예정(이전 HEAD `c39eb26`)
- PR: 없음(사용자 명시적 요청 없음)
