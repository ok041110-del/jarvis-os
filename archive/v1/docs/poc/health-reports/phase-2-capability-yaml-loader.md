# Repository Health Report — Phase 2 (Capability YAML Loader)

날짜: 2026-08-03
범위: `packages/core/src/jarvis_core/ports/i_capability_provider.py` 신규,
`packages/core/src/jarvis_core/application/hq_provisioner.py` 신규(Application
Service), `adapters/capability-provider-yaml` 신규, `hqs/*/pyproject.toml`
entry point 추가, `apps/poc-runner/main.py` 제네릭 부팅 루프로 교체,
`tests/integration/test_capability_provider_yaml.py`·
`tests/integration/test_hq_zero_code_addition.py` 신규.

| 항목 | 점수 | 근거 |
|---|---|---|
| Architecture | 93 | ADR-0004의 7개 결정이 코드로 전부 검증됨: Registry는 무수정(결정 1), `ICapabilityProvider`는 discover+parse만 담당(결정 2), Provisioning 단계에서 등록(결정 3), 등록 성공/실패에 따른 Idle/Error 전이(결정 4), Registry-Lifecycle 독립성이 `HQProvisioner`에서만 연결됨(결정 5), Composition Root는 `HQProvisioner`+구체 Adapter를 연결만 함(결정 6, 사용자 승인 사항), Discovery는 entry point로 구현하되 Port에는 노출하지 않음(결정 7). 7점 감점 사유: "owner가 HQ 식별자와 일치"라는 결정 4의 조건 중 하나를 Provider(어댑터)가 판단하는데, 이는 Core가 아니라 어댑터에 위치한 구조적 판단이라 향후 다른 Provider 구현체(DB/Remote)가 이 검증을 빠뜨릴 여지가 있음 — Core 쪽에 공통 검증 유틸리티를 두는 방안은 검토했으나 이번 Phase 범위 밖으로 남김. |
| Documentation | 90 | ADR-0004가 Accepted로 커밋되고 PROJECT_CONTEXT.md/ROADMAP.md에 반영됨. `capabilities.yaml` 파일들의 주석이 "이제 실제로 로드된다"로 갱신되어 ADR-0002 Known Gap 해소가 문서상으로도 명확함. 10점 감점 사유: `docs/architecture/v1.0/05-capability-registry.md`(Frozen 설계 문서)는 의도적으로 손대지 않았으나, "Entry Point 기반 Discovery"라는 구현 선택 자체를 설명하는 별도 구현 노트는 아직 없음(ADR-0004 본문이 그 역할을 겸하고 있음). |
| Implementation | 91 | `HQProvisioner`가 실제 YAML 파일을 실제로 파싱해 `CapabilityRegistry`에 등록하고, 실제 `HQStateMachineRuntime`으로 Provisioning→Idle 전이를 실행함(Mock 없음). `main.py` 실행 결과, 3개 시나리오 전부 이전과 동일하게 동작 확인(Wake-up/Disabled/Permission 거부 포함). 9점 감점 사유: Division/Agent 생성이 여전히 `HQProvisioner` 안에 "Capability 1개 = Division 1개 + Agent 1개"라는 최소 관례로 하드코딩되어 있음(ADR-0004 Rejected Alternative C에 따라 의도적으로 범위 밖에 둔 것이나, 다음 Phase에서 여러 Division/Agent를 가진 HQ를 다뤄야 할 때 이 지점을 다시 설계해야 함). |
| Tests | 88 | 신규 통합 테스트가 (1) 실제 entry point discovery, (2) 구조적 실패(스키마 누락/owner 불일치) 시 조용히 무시되지 않음, (3) **legal-hq를 실제로 저장소에 추가/제거하며 `uv sync`를 두 번 실행**하는 실증 테스트로 "새 HQ 추가 시 Core/Kernel/Registry/main.py 무수정 + 자동 Discovery + 자동 Routing"과 "복수 HQ(3개) 동시 자동 Discovery", "HQ 제거 후 나머지 정상 동작"을 전부 실제 코드 경로로 증명함. 기존 e2e 10개 + Phase 1 integration 6개 전부 무수정 통과(회귀 없음). 12점 감점 사유: 이 신규 테스트들이 실제 `uv sync` 서브프로세스를 호출하므로 실행 시간이 상대적으로 김(약 2.7초, 기존 대비 15배) — CI에서 이 테스트만 별도 job으로 분리하는 것을 고려할 만하나 이번 Phase에서 적용하지 않음. |
| Technical Debt | 80 | 새로 추가된 부채: (1) Architecture 항목에 적은 owner-일치 검증의 어댑터 위치, (2) `main.py`의 함수 시그니처(`handle_request`, `run_organization_layer`)가 여전히 Phase 1에서 지적한 대로 인자 개수가 많음(이번 Phase에서 늘리지는 않았으나 Context 객체 리팩터링을 아직 하지 않음 — Phase 1 Health Report의 권고가 아직 미적용 상태로 이월됨), (3) `HQProvisioner`가 Division/Agent를 생성할 때 `required_tools=[]`로 고정되어, entry point로 자동 추가된 HQ는 MCP Connector를 호출하지 않음(Division/Agent 설계를 별도 Phase로 미룬 것의 직접적 결과 — 의도된 것이지만 부채로 기록). | 
| Known Gap | 92 | ADR-0002가 기록한 Known Gap(YAML이 로드되지 않음)이 이번 Phase로 완전히 해소됨. 새로 발생한 Known Gap: Division/Agent 자동 등록은 여전히 최소 관례 수준(1 Capability = 1 Division = 1 Agent, tool 없음)이며, 여러 Division/Agent를 가진 HQ 확장은 다음 Phase 대상. Registry의 Decommissioned 처리(§5 문서상 규칙)도 Phase 2 범위에서 다루지 않음(ADR-0004에 이미 명시됨 — 은폐 아님). |
| Repository Readiness | 91 | `uv sync`/`uv run pytest` 전체 통과. Core(`packages/core`)에는 순수 추가만 있고 기존 파일(Kernel/Registry/Lifecycle/Organization) 수정 없음(git diff --stat으로 확인). `apps/poc-runner/pyproject.toml`은 신규 adapter 의존성 1건만 추가되었고, legal-hq 같은 신규 HQ는 poc-runner의 의존성 목록에 전혀 나타나지 않음(테스트가 이를 최우선 전제조건으로 명시적으로 assert함). 9점 감점 사유: entry point 기반 discovery는 이 저장소가 uv workspace라는 전제에 묶여 있음 — 완전히 분리 배포된 HQ 패키지(별도 PyPI 인덱스 등)에서도 동일하게 동작하는지는 아직 검증되지 않음(Known Gap으로 기록, v1.1 후보). |

**총평**: Phase 2는 사용자가 지정한 최종 Architecture Validation 기준 — "새 HQ를 코드 수정 없이 추가하여 자동 인식 및 자동 Routing이 가능함" — 을 실제로 저장소에 HQ 패키지를 추가/제거하는 실증 테스트로 증명했습니다. ADR-0004의 7개 결정 사항 모두 코드에 반영되었고, `HQProvisioner`를 별도 Application Service로 분리하라는 요청과 "복수 HQ 자동 Discovery" DoD 추가 요청 모두 반영했습니다. 감점 요인은 전부 다음 Phase(Division/Agent 확장, Context 객체 리팩터링)로 이월 가능한 수준이며, 즉시 조치가 필요한 결함은 없습니다.

## 다음 Phase 착수 전 권고 (Architecture Suggestion, 미적용)
1. Phase 1 Health Report의 권고(Context 객체로 `main.py` 함수 시그니처 정리)가 아직 미적용 상태로 이월되었습니다 — Phase 3(Policy/Casbin) 착수 전에 검토를 제안합니다.
2. `HQProvisioner`의 Division/Agent 최소 관례(1:1:0-tools)를 실제 요구사항이 생기기 전까지는 그대로 유지하되, 여러 Division/Agent가 필요한 HQ가 등장하면 이 지점부터 재설계가 필요합니다(현재는 조기 확장 없이 미룬 상태).
3. entry point 기반 discovery가 "완전히 분리 배포된 패키지"에서도 동작하는지는 검증되지 않았습니다 — 현재는 uv workspace 전제에서만 실증되었습니다(v1.1 후보로 기록 권장).
