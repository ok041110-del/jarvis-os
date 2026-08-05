# Repository Health Report — Phase 1 (Lifecycle Adapter, python-statemachine)

날짜: 2026-08-02
범위: `packages/core/src/jarvis_core/ports/i_lifecycle_runtime.py` 신규 정의,
`adapters/lifecycle-statemachine` 구현, `apps/poc-runner/main.py` wiring,
`tests/integration/test_lifecycle_statemachine.py` 신규.

| 항목 | 점수 | 근거 |
|---|---|---|
| Architecture | 92 | `LifecycleRuntime`을 Domain Interface로 정의(ADR-0003 결정 2)하고 python-statemachine 타입을 Core에 전혀 노출하지 않음. Guard 판정은 Core(`hq_state.transition`)에 100% 위임(결정 3), 어댑터는 FSM 그래프 실행만 담당. `main.py`가 Adapter 종류에 따라 분기하지 않음(결정 4). 8점 감점 사유: python-statemachine의 전이 그래프를 `_ALLOWED_TRANSITIONS`(Core의 private 속성)에서 직접 읽어와 구성하는데, 이는 "private 속성을 외부에서 참조"하는 결합이라 향후 Core가 이 이름을 바꾸면 어댑터가 조용히 깨질 수 있음 — Public 접근자 필요성 검토 대상. |
| Documentation | 88 | ADR-0003이 Lifecycle뿐 아니라 전체 Port 설계 헌장으로 명확히 기록됨. PROJECT_CONTEXT.md의 "Phase 실행 로그"와 ROADMAP.md를 실제 완료 상태로 갱신함. 12점 감점 사유: `docs/architecture/v1.0/02-core-design-principles.md` 등 원본 설계 문서 자체에는 아직 "python-statemachine 어댑터가 실제로 어떻게 배선되는가"에 대한 갱신이 없음(설계 문서 자체는 Frozen이라 의도적으로 손대지 않았으나, 별도 구현 노트 문서가 있으면 더 좋았을 것). |
| Implementation | 90 | 실제 python-statemachine 3.2.1 라이브러리 설치·실행 성공, 실제 FSM 엔진이 8-state 전이를 실행. 시뮬레이션이나 Mock이 아님. 10점 감점 사유: `current_state`가 python-statemachine 내부적으로 deprecated된 속성이었던 것을 수정하며 우회했는데, 향후 라이브러리 메이저 버전 업 시 API 변경에 취약한 지점이 하나 생김(허용 가능한 수준의 기술 부채로 판단, 아래 Technical Debt 참고). |
| Tests | 85 | 신규 integration 테스트가 `itertools.product(HQState, HQState)` 전수 조사(8×8×2=128 subtests)로 Core와 어댑터의 판정 100% 일치를 증명 — 우연한 케이스 누락 위험이 거의 없음. 기존 e2e 10개 테스트 전부 무수정 통과(회귀 없음 증명). 15점 감점 사유: `tests/unit/`은 여전히 비어 있음 — 이번 Phase에서 Core(`hq_state.py`)에 대한 unit 테스트를 신규로 추가하지 않았고(기존에 없었음), integration 테스트가 그 역할을 대신 하고 있어 테스트 피라미드가 여전히 역삼각형에 가까움. |
| Technical Debt | 78 | 새로 추가된 부채 2건: (1) 어댑터가 Core의 private 속성(`_ALLOWED_TRANSITIONS`)을 직접 참조함(위 Architecture 항목과 동일 사안), (2) `apps/poc-runner/main.py`에 `advance_hq()` 헬퍼가 추가되며 함수 시그니처(`handle_request`, `run_organization_layer`)에 `lifecycle_runtimes` 인자가 늘어나 파라미터 개수가 커짐 — Phase 2~5에서 Policy/Connector/Workflow Adapter가 같은 패턴으로 추가되면 이 함수들의 인자 리스트가 계속 길어질 위험(향후 Context 객체로 묶는 리팩터링 후보, 지금 당장 처리하지 않음). |
| Known Gap | 95 | 이번 Phase가 새로 만든 Known Gap 없음. 기존 Known Gap(ADR-0002, Capability YAML Loader)은 그대로 유지되며 다음 Phase(Phase 2)에서 다루기로 이미 문서화되어 있음. 은폐된 격차 없음. |
| Repository Readiness | 90 | `uv sync` 및 `uv run pytest`가 이 환경에서 실제로 성공함을 확인(walking-skeleton-status.md가 우려했던 "네트워크 차단" 가정이 이번 세션에서는 해당하지 않음 — 이 사실 자체를 별도로 갱신 필요, 아래 권고 참고). Core 변경 0건, 기존 테스트 회귀 0건으로 병합 가능한 상태. 10점 감점 사유: `docs/poc/walking-skeleton-status.md`가 아직 "네트워크 접근 불가" 전제로 작성되어 있어 실제 환경과 문서가 어긋남 — Phase 2 착수 전에 갱신 권장. |

**총평**: Phase 1은 계획대로 완료되었고, ADR-0003이 규정한 5가지 결정 사항(빈 Port 정의는 Core 확장, Domain Interface로 명명, Core가 Guard 단일 진실 공급원, Core는 Adapter를 추론하지 않음, Adapter는 가역적이어야 함)을 모두 코드로 검증했습니다. 감점 요인은 전부 "지금 당장 위험하지는 않지만 다음 Phase에서 반복되면 커질 수 있는" 항목들이며, 즉시 조치가 필요한 결함은 없습니다.

## 다음 Phase 착수 전 권고 (Architecture Suggestion, 미적용)
1. `docs/poc/walking-skeleton-status.md`의 "네트워크 차단" 전제를 갱신 — 이번 세션에서 `uv sync`가 실제로 성공했습니다.
2. `main.py`의 `handle_request`/`run_organization_layer` 인자가 Phase가 늘어날 때마다 계속 커지는 추세이므로, Phase 2(Capability YAML Loader) 착수 시점에 Context 객체로 묶는 리팩터링 여부를 검토할 것을 제안합니다(지금 적용하지 않음).
3. 어댑터가 Core의 `_ALLOWED_TRANSITIONS`(private)를 직접 참조하는 결합을 완화하려면, Core에 공개 접근자(예: `allowed_transitions(state) -> frozenset[HQState]`)를 추가하는 것을 Phase 2 이후 검토 후보로 제안합니다 — 이는 Core 확장이므로 별도 ADR 논의 대상입니다.
