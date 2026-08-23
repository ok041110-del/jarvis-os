# Stage 04: Responsibility

## 책임진다

- Stage 03 `design`(`str`)에서 AST 시작점(target module/function)을
  식별(`identify_target` 재사용)
- 식별된 시작점의 Dependency Closure를 계산해 Build Context로 포함
  (`build_dependency_closure` 재사용)
- `expose_target=True`일 때 대상 파일 전체와 Exposure 정책 지시문을
  Build 입력에 포함(`module_source_path`/`_EXPOSURE_POLICY_INSTRUCTION`
  재사용) — Target 함수 내부만 확장하고 그 외 영역은 건드리지 않도록
  강제
- 조립된 Build 입력으로 실제 Code를 생성/수정(`backend_agent_code_
  generation` 재사용)
- 생성 결과를 Stage 05(Validation)가 소비할 수 있는 고정된 스키마
  (`IMPLEMENTATION.md`)로 반환

## 책임지지 않는다

- Context 수집, Specification 생성, Design 생성(→ Stage 01/02/03. 이
  Stage는 Stage 03의 Output을 그대로 Input으로 받을 뿐, 다시
  생성하지 않는다)
- 생성된 Code를 실제 저장소 파일에 적용하는 것 — `run_stage_04()`은
  Code 문자열만 반환한다. 파일 쓰기/커밋은 호출자(현재는 검증 절차,
  향후 Stage 05 이후 배포 경로)의 책임이다(T06~T19/ADC-0005 §8과 동일
  원칙 — "임시 적용 후 원상복구"는 검증 절차이지 Production 경로가
  아니다)
- 코드 리뷰/테스트 실행(→ Stage 05)
- Target File Exposure 여부 자동 판별 — RFC-0007 Open Issues가 이미
  "검증된 적 없다"고 기록했다. `expose_target`은 호출자가 명시적으로
  지정한다(ADC-0005 §7과 동일한 결정)
- 신규 Capability/Agent 추가 — 3개 Capability 전부 `workflow_ast_
  context.py`/`agents.py`의 기존 함수를 재사용한다(`IMPLEMENTATION_
  RULES.md`, ADR-0008 §4 충족)
- `workflow_ast_context.py`/`agents.py` 자체 수정 — 이미 ADC-0005
  §8에서 real Engine E2E로 검증된(Scope 준수 3/3) 코드이므로 호출만
  하고 건드리지 않는다

## Kernel/Architecture 경계

Development HQ MVP Implementation 범위 — Kernel Architecture/Baseline
변경 없음, 새 Interface/Contract 미추가, `agents.py`/`engine.py`/
`workflow_ast_context.py` 무수정.
