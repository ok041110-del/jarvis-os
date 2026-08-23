# Stage 04: Implementation Output 스키마 / Contract

`run_stage_04(issue, stage_03_output, expose_target: bool = False)`이
반환하는 `dict`의 키 3개. Stage 01~03처럼 새 Contract를 만들지 않고,
`workflow_ast_context.run_pipeline_with_ast_context()`가 이미 반환하는
`target`/`implementation` 키 형태를 그대로 재사용한다.

| 키 | 타입 | 생성 Capability | 항상 채워지는가 |
|---|---|---|---|
| `target` | `tuple[str, str] \| None` | Target Identification | 예(식별 실패 시 `None`) |
| `implementation` | `str` | Code Generation | 예(Engine 실패 시에도 `_engine_failure_message()` 문자열로 채워짐) |
| `expose_target` | `bool` | 호출자가 전달한 값을 그대로 echo | 예(호출자가 실제로 어떤 모드로 실행했는지 Stage 05가 알 수 있도록) |

`expose_target` 기본값은 `False`다(`workflow_ast_context.run_pipeline_
with_ast_context`와 동일한 기본값) — Design 출력에서 노출 여부를
자동 판별하는 것은 검증된 적이 없으므로(RFC-0007 Open Issues), 호출자가
명시적으로 켜야 한다.

## Implementation Contract (Stage 05가 기대할 수 있는 것)

- `target`이 `None`이 아니면, `implementation`은 **Target File Exposure
  정책이 적용된 경우** 대상 파일의 전체 내용(수정 포함)이고, **적용되지
  않은 경우** 부분 코드(마크다운 fence 제거된 순수 코드 문자열)다 —
  둘 중 어느 쪽인지는 `expose_target` 키로 판별한다
- `target`이 `None`이면 AST 시작점을 식별하지 못한 것이므로,
  `implementation`은 Design 전체를 기반으로 한 자유 형식 코드다(기존
  `run_pipeline_with_ast_context`와 동일한 폴백)
- Engine 호출(Target Identification, Code Generation) 중 어느 하나라도
  실패하면 `implementation`은 `_engine_failure_message()` 형식의 오류
  문자열이고, `target`은 실패 시점까지 확정된 값(식별 실패 전이면
  `None`, 이후면 실제 `target`)이다

## Stage 05가 이 Output을 어떻게 소비하는가

- `expose_target=True`이고 `target`이 있는 경우, `implementation`은
  `ast_context.module_source_path(target[0])` 경로의 파일 전체 내용과
  같은 형태(diff 가능)다 — Stage 05는 이 문자열을 그 경로에 임시로
  적용해 `pytest`를 실행하고 원상복구하는 절차(T06~T19/ADC-0005 §8과
  동일한 방법론)로 검증할 수 있다
- `expose_target=False`이거나 `target`이 `None`인 경우, `implementation`
  은 적용 대상 파일이 특정되지 않은 코드이므로 Stage 05는 코드
  리뷰/정적 분석 수준으로만 검증 가능하다(실제 파일 적용은 이 모드의
  범위 밖 — `RESPONSIBILITY.md`)

## 왜 Stage 04가 파일을 직접 쓰지 않는가

`run_stage_04()`는 순수하게 문자열을 반환하는 함수다 — 파일 시스템
쓰기는 이 Capability의 책임이 아니다(`RESPONSIBILITY.md`). 이는 기존
`backend_agent_code_generation()`/`run_pipeline_with_ast_context()`도
동일하게 지켜온 경계다 — Build 단계가 파일을 직접 덮어쓰는 Production
경로는 이 저장소 어디에도 아직 없다(검증 절차에서만 임시로 적용 후
원상복구한다).
