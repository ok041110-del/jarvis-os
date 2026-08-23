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
  Code 문자열만 반환한다. 파일에 쓰기/커밋은 호출자(현재는 Stage 04의
  real Engine E2E 검증 절차, 향후 Stage 05 이후 실제 배포 경로)의
  책임이다. 이는 T06~T19/ADC-0005 §8 E2E와 동일한 원칙 — "생성된
  코드를 임시로 적용해 검증한 뒤 원상복구"는 검증 절차이지 이
  Capability의 Production 경로가 아니다
- 코드 리뷰/테스트 실행(→ Stage 05)
- Target File Exposure 여부의 자동 판별 — RFC-0007 Open Issues가 이미
  "Design 출력에서 노출 여부를 자동 판별하는 것은 검증된 적이 없다"고
  기록했다. `expose_target`은 여전히 호출자가 명시적으로 지정한다
  (ADC-0005 §7과 동일한 결정, 이 Stage가 새로 판단하지 않는다)
- 신규 Capability/Agent 추가 — 3개 Capability(`CAPABILITIES.md`) 전부
  `workflow_ast_context.py`/`agents.py`의 기존 함수를 그대로 재사용한다.
  `IMPLEMENTATION_RULES.md`의 "구현 중 새 Capability/Agent 추가 금지"
  원칙과 ADR-0008 §4를 모두 만족하는 범위로 판단했다
- `workflow_ast_context.py`/`agents.py` 자체의 수정 — 이미 ADC-0005
  §8에서 real Engine E2E로 검증된(Scope 준수 3/3) 코드이므로, Stage
  04는 이를 호출만 하고 건드리지 않는다

## Kernel/Architecture 경계

Stage 04는 Development HQ MVP Implementation 범위이며, Jarvis OS Kernel
Architecture나 Development HQ Baseline을 변경하지 않는다. 새 Interface/
Contract를 추가하지 않았고, `agents.py`/`engine.py`/`workflow_ast_
context.py`는 수정하지 않았다.
