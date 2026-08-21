# PHASE4-HQ-CROSS-VALIDATION-0001: Development HQ ↔ Investment HQ 실행 패턴 대조

**문서 성격**: Governance 판단이 아니라 실측 비교 기록이다. Kernel을 설계하지 않는다. Structure v1.0 / Architecture Baseline / Development HQ v1.0 Freeze / Investment HQ v1.0 Freeze 어느 것도 수정하지 않는다.

## 목적

`roadmap.md` Phase 4 완료 조건("두 HQ의 실행 패턴을 항목별로 대조해 Common/HQ-Specific/Uncertain 3분류표를 작성한다, 실제 코드·Evidence 인용과 함께")을 충족하기 위해, Development HQ와 Investment HQ의 실행 패턴 6항목을 `git log --all --follow`와 코드 diff 수준으로 대조했다.

## 방법

각 항목에 대해 (1) 최초 생성 커밋과 위치, (2) `hqs/development/` 실제 코드에 승격됐는지, (3) 코드 diff 수준 동일성을 확인했다. 추측 없이 git 이력과 실제 파일 내용만 근거로 삼았다.

## 대조 결과

| 항목 | 판정 | 근거 |
|---|---|---|
| **Engine 호출 방식**(`call_engine()`) | **Common** | `hqs/development/mvp/engine.py`가 최초 생성 지점(커밋 `b7cc96c`, Dev HQ 플랫폼 네이티브 — `projects/` 프로토타입 경유 없음). `hqs/investment/engine_client.py`는 이 함수를 **복사하지 않고 live import**(`from mvp.engine import call_engine`) — 두 HQ가 동일 함수 객체를 공유. |
| **Agent/Capability(개념)** | **Common Domain** | Structure v1.0 Core Domain Model(`HQ→Project→Workflow→Stage→Task→Agent→Capability→Execution→Provider/Tool/MCP`)이 원문으로 선언 — 코드 증거가 아니라 Architecture 문서 자체가 이미 두 HQ 공통 계층으로 확정. |
| **Agent-Capability 매핑(아티팩트)** | **Uncertain** | Dev HQ `hqs/development/mvp/agents.py`의 `AGENT_CAPABILITY_MAP`은 `test_mvp_0001.py`에서만 참조되는 선언적 상수(실제 Dispatch는 `workflow.py`가 직접 함수 import로 수행, 이 dict를 조회하지 않음). Investment HQ `hqs/investment/run.py`의 `TEAMS` dict는 실제 런타임 Dispatch(`team = TEAMS[team_key]`)에 쓰임 — 값 타입도 다름(문자열 vs 모듈 객체). 두 아티팩트 간 계보를 뒷받침하는 git 근거 없음. |
| **Checkpointing** | **Investment-specific** | `hqs/investment/checkpoint.py`의 `Checkpointer`/`run_step`은 PR #80(`78309c1`) `projects/dev-hq-timeout-recovery-prototype/combined/combined_runner.py`의 동일 클래스와 로직 100% 동일(diff 확인). 이 Prototype은 PR #76(`f3e4f95`)에서 기원. **`hqs/development/mvp/`에는 Checkpointer가 단 한 번도 존재한 적 없음**(전수 grep 0건) — Dev HQ 플랫폼으로 승격된 적이 없다. |
| **Parallel Execution(원시 기법)** | **Common** | `docs/research/ENGINE-USECASE-0001-parallel-independent-tasks.md`/`ENGINE-USECASE-0002-nway-parallel-validation.md`(PR #60/#61, 2026-08-15, **Dev HQ 자체 소유**)가 `ThreadPoolExecutor + call_engine()` 2/3/4-way 동시 호출을 독립적으로 검증(교차오염 0건, Gateway/Registry 없이 동작). 이는 Investment 계보(PR #77/#80, 2026-08-16, **하루 뒤**)와 무관한 별개 Evidence — 두 HQ가 독립적으로 동일 기법에 도달했다. |
| **Wave 구조**(4단계 하드코딩 + Bull/Bear/Synthesis 등 도메인 명명) | **HQ-specific** | Dev HQ의 Task 그래프는 2-Task 선형(`workflow.py`)이라 다단계 병렬 구조가 필요한 적이 없다(실측, 추측 아님). 단계 명명 자체가 Investment 도메인 특정적. |
| **Team/Workflow** | **HQ-specific** | Structure v1.0 Core Domain Model이 Workflow를 HQ 하위 소유로 명시. |

## 추가 관찰(GAP, 판정에는 포함하지 않음)

`core/execution/`(MVP-0001~0006 Builder 파이프라인, ExecutionRequest→PromptSpec→ModelRequest→Handle→State→Result)는 두 HQ의 실제 코드 어디에서도 import되지 않는다(`grep` 0건) — HQ가 실제로 쓰는 `call_engine()`/Checkpointing/ThreadPoolExecutor 계보와 완전히 별개의, 연결되지 않은 두 번째 "Execution" 개념이 저장소에 이미 존재한다. Phase 5/6이 "Execution" Kernel Candidate를 다룰 때 이 기존 산출물과의 관계를 별도로 정리해야 한다.

## 완료 조건 충족 확인

- 3분류표 작성 완료(위 표), 전 항목 실제 코드·git 커밋 인용 포함.
- "Common"으로 분류된 항목(Engine 호출 방식, Parallel Execution)이 존재 — Phase 5 진입 조건 충족.

---

## Architecture/Governance 영향

**없음.** Structure v1.0 / Architecture Baseline / Development HQ v1.0 Freeze / Investment HQ v1.0 Freeze 어느 것도 수정하지 않았다. 새 RFC/ADC/ADR을 작성하지 않았다. Kernel Component/코드를 설계·구현하지 않았다(비교·분류만 수행).
