# Execution Layer MVP-0006 Observation

## 목적

이번 MVP의 목적은 Execution Result Contract를 정의하는 것이다.
Runtime/Scheduler를 구현하지 않는다. Execution State에 대한 결과
계약만 구현한다. 이 문서는 사실만 기록한다. Architecture 판단은
하지 않는다. RFC/ADC/ADR을 생성하지 않는다.

## 구현 범위

- `core/execution_layer/mvp_0006/execution_result_builder.py`(신규) —
  `build_execution_result(execution_state, *, handle_id, produced_at, results) -> str`
  하나와, 보조 추출 함수 `_extract_request_id()`, 고정 상수
  `ARTIFACT_VERSION`.
- `core/execution_layer/mvp_0006/tests/test_execution_result_builder.py`
  (신규) — 9개 테스트.
- `core/execution_layer/mvp_0006/dogfooding/run_dogfooding.py`(신규) —
  MVP-0001~0006 Builder 6개를 순서대로 호출해 전체 Artifact Chain
  (Implementation Specification → Execution Request → Prompt
  Specification → Model Request → Execution Handle → Execution State
  → Execution Result)을 검증한다. MVP-0001~0005 코드는 읽기(호출)만
  한다 — 수정 없음.
- Development HQ, MVP-0001~0005 코드 모두 수정하지 않았다.

## Dogfooding이 `development-hq/mvp/workflow_0008.run_pipeline()`을 쓰지 않는 이유 (설계 사실)

MVP-0001~0005의 Dogfooding 스크립트는 Development HQ
`workflow_0008.run_pipeline()`으로 Implementation Specification을
만들었다(예: `MVP-0005-observation.md` "구현 범위" 참고). 이 저장소의
`development-hq/mvp/engine.py` `call_engine()`은 `ENGINE-CONNECT-0001`
이후 더 이상 규칙 기반이 아니라 실제 Engine(Claude Code CLI,
`claude -p`, 최대 180초 timeout)을 호출한다. `run_pipeline()`은 내부에서
`call_engine()`을 5회 호출하므로, 이 스크립트가 `run_pipeline()`을
그대로 재사용하면 Dogfooding 1회 실행마다 최대 10회(Real Issue + Toy
Issue) 실제 Engine 호출이 발생한다 — 이는 이번 MVP(Execution Result
Builder 검증)가 요구하지 않는 실제 비용·시간이다.

`ExecutionResultBuilder`의 Contract는 Execution State(문자열)를
입력으로 받을 뿐, 그 Execution State를 만든 Implementation
Specification이 실제로 어떻게 생성됐는지와 무관하다 — MVP-0001~0005
각 Dogfooding이 이미 그 생성 경로를 실측 검증했으므로, 이번 MVP가
다시 확인할 필요가 없다. 따라서 이 스크립트는 `run_pipeline()`을
호출하지 않고, `core/execution_layer/mvp_0001/tests/`가 쓰는 것과
같은 고정 샘플 Implementation Specification(`SAMPLE_IMPLEMENTATION_SPECIFICATION`)
에서 시작한다. 이는 Contract 결정이 아니라 **검증 방법 선택**이며,
Execution Result의 Architecture/Contract를 바꾸지 않는다.

`docs/research/ENGINE-CONNECT-0005-full-pipeline-real-engine-wiring.md`
가 이후 이와 동일한 판단(`run_pipeline()` 미사용, 실제 비용 회피)을
별도 실험에서 재확인했다 — 두 문서의 사실 관계는 일치한다.

## handle_id / produced_at / results를 이 모듈이 생성하지 않기로 한 것 (설계 사실)

`build_execution_result()`는 `handle_id`, `produced_at`, `results`
셋 다 필수 인자로 받으며, 함수 내부에서 시스템 시계를 읽거나
산출물을 스스로 만들지 않는다 — MVP-0003(request_id/created_at)부터
MVP-0005(state/changed_at)까지와 동일한 이유다(값 생성·결정 자체가
Runtime/Scheduler/Engine의 책임 영역과 겹친다). `request_id`만
예외로, Execution State의 `## State` 절에 이미 있는 값을 정규식으로
그대로 읽어서 재사용한다.

Dogfooding 스크립트는 호출자로서 세 값을 다음과 같이 채웠다(이 결정은
`execution_result_builder.py`가 아니라 `run_dogfooding.py`에 있다):

- `handle_id`: 방금 만든 Execution Handle 자신의 `## Handle` 절에서
  추출한 값을 그대로 재사용했다(새로 유도하지 않음).
- `produced_at`: 고정 placeholder 문자열 `"unresolved"` — 이전 MVP의
  `created_at`/`submitted_at`/`changed_at`과 동일하게, 이 MVP도 실제
  시계를 읽지 않는다는 사실을 그대로 반영했다.
- `results`: Engine 산출물을 실제로 만들지 않으므로(`call_engine`
  미호출) opaque placeholder 문자열 목록(`PLACEHOLDER_RESULTS`)을
  caller로서 직접 주입했다 — Builder는 이 값의 의미를 해석하지
  않는다(`ADC-0003-execution-result-item-schema.md` Decision).

## 실행 결과 (실측)

`python3 -m pytest core/execution_layer/mvp_0006/tests/ -q` → 9개
테스트 모두 통과.

`core/execution_layer/mvp_0006/dogfooding/output/`에 저장된 산출물
(`toy_issue.*`, 7개 파일 — Implementation Specification부터 Execution
Result까지)을 대조한 결과:

- `toy_issue.execution_result.md`(1695 bytes)에 `handle_id`/
  `request_id`가 `## Result` 절과 `## Execution State`(원문 그대로
  포함된 Execution Handle/State 안의 값) 양쪽에서 동일하게
  (`f0ae314229f90c20` / `73d88e441e6f9302`) 나타났다 — 체인 전체에서
  값이 바뀌지 않았다.
- `toy_issue.execution_state.md`(1318 bytes) 전체가 `toy_issue.execution_result.md`
  안에 원문 그대로 포함되어 있다(Execution State 자체는 수정되지
  않고, 그 앞에 `## Result`/`## Results` 절만 추가됨).

## Non-goals (이번 MVP에서 하지 않은 것)

- `results` 항목의 의미 해석, 개수 제한(빈 목록 허용) — `ADC-0003`이
  명시적으로 범위 밖에 둔 결정이다.
- Runtime, Scheduler, Retry — 코드에 존재하지 않는다.
- 실제 Engine 호출(`call_engine`) — Dogfooding은 고정 샘플과
  placeholder만 사용한다(위 "Dogfooding이 run_pipeline()을 쓰지 않는
  이유" 참고).
- Development HQ, MVP-0001~0005 코드 — 모두 수정하지 않았다.
- 새 RFC, ADC, ADR — 생성하지 않았다.
