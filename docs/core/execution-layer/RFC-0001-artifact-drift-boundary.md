# RFC-0001: Spec-Repository Artifact Drift — Boundary

**Status**: Resolved — `ADC-0001-artifact-drift-boundary.md`로 종결됨(Not Accepted, based on current evidence; ADR 불필요, STABILITY-0001 §1.2). RFC 자체는 결정 문서가 아니며, 이 라벨은 절차 진행 상태만 반영한다.
**Author**: Claude Code (Execution Protocol Research, Governance v2 Rule B 적용)
**Governance v2 근거**: Rule B(Observation Count ≥ 3인 반복 Pattern → RFC)
**Evidence**: `docs/research/ENGINE-INTEGRATION-0001-Claude-Code.md`,
`docs/research/ENGINE-INTEGRATION-0002-Claude-Code.md`,
`docs/research/ENGINE-INTEGRATION-0003-Claude-Code.md`

> 본 RFC는 Spec-Repository Artifact Drift의 해결책을 제안하지 않는다.
> 본 RFC는 세 실험에서 반복 관찰된 Drift의 책임 경계만 질문한다.
> 새 실험을 하지 않는다. Architecture를 변경하지 않는다. Execution
> Layer를 수정하지 않는다.

## 0. 이 RFC가 열린 이유

Execution Protocol Research(ENGINE-INTEGRATION-0001~0003) 3건 모두에서
동일한 근본 현상 — Prompt Specification 안의 문자열이 Repository의
실제 최신 상태와 어긋나는 것 — 이 반복 관찰되었다(Observation Count =
3). Governance v2 Rule B("Observation Count ≥ 3인 반복 Pattern → RFC")
에 따라, 이 RFC는 그 Pattern 하나만 근거로 열렸다. 이 RFC는 답을
제시하지 않는다 — 세 실험에서 실제로 관찰된 사실을 근거로, 이 현상의
책임 소재에 대한 질문만 제기한다.

## 1. Problem Statement

세 번의 독립 실험(신규 파일 생성, 기존 파일 1개 수정, 기존 파일 3개
다중 수정 — 서로 다른 Repository 조건)에서, 동일한 Spec-Repository
Artifact Drift가 반복 관찰되었다.

**Observation Count = 3**

세 실험 모두 같은 근본 원인을 공유했다: Prompt Specification이
참조하는 문자열(Relevant Context 마커)이, 그 Specification을 만들어낸
Development HQ 파이프라인의 실제 최신 동작(`engine._analyze_requirement`
가 해당 헤더를 partition해 제거하는 것)과 어긋났다. 이 어긋남은 세
실험 각각에서 독립적으로 재현되었으며, 발생 시점(사후 발견 vs 사전
예방)만 실험마다 달랐다.

## 2. Evidence Summary

| 실험 | 조건 | Drift 발생 여부 | 결과 |
|---|---|---|---|
| ENGINE-INTEGRATION-0001 | 신규 파일 생성(Target File이 Repository에 존재하지 않음) | 발생 — 사후 발견 | `leak_reproduced`가 최초 구현에서 항상 `False`를 반환. subagent가 수동 실행(테스트)으로 발견하고, 실제 파이프라인 출력에서 마커를 재도출해 `Edit`으로 수정한 뒤 `True`로 정정됨. |
| ENGINE-INTEGRATION-0002 | 기존 파일 1개 수정(Target File이 스텁 형태로 이미 존재) | 발생 — 사후 발견 | `project_intelligence_check_3`이 최초 구현에서 항상 `False`. 동일한 근본 원인(마커 불일치)이 재현되었고, subagent가 `run_pipeline` 출력을 직접 검사해 수정. 이와 별도로 모듈 경로 오류 2건도 관찰되었으나 이는 Drift와 무관한 별개 현상이었다. |
| ENGINE-INTEGRATION-0003 | 기존 파일 3개 다중 수정(Target File + 재노출 파일 + 테스트 파일, 낡은 이름으로 이미 존재) | 발생 — **사전 예방**(코드 작성 전에 미리 발견) | subagent가 코드를 작성하기 전에 `collect_relevant_context`/`_summarize_context`/`_enrich_issue`의 실제 반환값을 먼저 조사(T18)해, 마커 불일치를 사전에 회피했다 — 그 결과 이번에는 check 함수가 처음부터 `True`를 반환했고, 사후 수정이 관찰되지 않았다. |

## 3. Pattern

세 실험에서 반복된 사실만 정리한다. 새 사실을 추가하지 않는다.

- Prompt Specification이 Repository 최신 상태와 불일치할 수 있다
  (Observation Count = 3, ENGINE-INTEGRATION-0001~0003 전부).
- Engine(Claude Code)은 Prompt Specification 텍스트만으로 작업하지
  않고, Repository를 능동적으로 참조한다 — 세 실험 모두에서 Engine이
  스스로 여러 파일을 열람하고, 최소 1개 실험(0003)에서는 코드 실행
  결과를 코드 작성 전에 직접 조사했다.
- Drift는 시스템 오류(Tool Error/Timeout/Permission/Context Limit)로
  드러나지 않는다 — 세 실험 모두에서 이 현상은 오직 논리적 결과
  (check 함수가 조용히 `False`를 반환하는 것)로만 드러났다.
- Engine은 Drift를 스스로 발견하고 수정할 수 있다 — 세 실험 모두에서
  Engine이 추가 개입 없이 자체적으로(수동 테스트 실행 또는 사전 조사를
  통해) 이 불일치를 발견하고 대응했다. 대응 시점(사후/사전)은 실험마다
  달랐다.

## 4. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 질문만 제기한다.

Spec → Repository → Execution 흐름 중, Artifact Drift는 누가
책임지는가?

- Development HQ
- Execution Layer
- Engine
- Other

이 RFC는 이 중 어느 것이 맞는지 판단하지 않는다. 이 질문에 대한
판단은 ADC로 위임한다.

## Out of Scope

이번 RFC에서는 다루지 않는다.

- Repository Snapshot
- Git Hook
- Hash 비교
- 자동 동기화
- Prompt Builder 변경
- Execution Result
- Runtime
- Claude 개선안
- 해결책(위 Boundary Question에 대한 어떤 답도 포함)

## Non-goals

- 이 RFC는 Spec-Repository Artifact Drift를 해결하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다 — ENGINE-INTEGRATION-0001~0003
  에서 이미 관찰된 사실만 인용했다.
- 이 RFC는 Architecture Baseline이나 Execution Layer Artifact
  Standard v1을 변경하지 않는다.
- 이 RFC는 Development HQ, Execution Layer의 어떤 코드도 수정하지
  않는다.
- 이 RFC는 ADC, ADR, MVP 문서를 작성하지 않는다.
- 이 RFC는 위 Boundary Question에 답하지 않는다.

## Next Step

ADC-0001(신설 예정, 이 RFC의 후속)에서 다음 하나만 판단하도록 제안한다.

1. Spec-Repository Artifact Drift의 Boundary 책임 소재(Development
   HQ / Execution Layer / Engine / Other) 중 하나.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance 절차를
통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. ENGINE-INTEGRATION-0001~0003에
  실제로 기록된 내용만 인용했다. 새 실험은 수행하지 않았다.
- 해결책을 제안했는가 — **아니오**. Boundary Question은 질문 형태로만
  남겼고, 4개 선택지 중 어느 것도 판단하지 않았다.
- Architecture를 변경했는가 — **아니오**.
- Execution Layer를 수정했는가 — **아니오**.
- ADC/ADR/MVP를 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- Out of Scope 항목(Repository Snapshot, Git Hook, Hash 비교, 자동
  동기화, Prompt Builder 변경, Execution Result, Runtime, Claude
  개선안, 해결책)을 다뤘는가 — **아니오**.
