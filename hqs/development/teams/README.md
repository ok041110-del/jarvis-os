# Development HQ Teams

Development HQ의 논리적 구조를 Stage 01~05에서 Team 구조로 전환한다
(Multi-Agent Adoption 방향에 따른 구조 정리, Kernel/Architecture 변경
아님). `hqs/development/stages/`의 기존 코드/문서를 대체하지 않고,
각 Team이 해당 Stage capability를 호출하는 얇은 진입점을 추가한다.

## Stage → Team Mapping

| 기존 Stage | Team | 진입점 |
|---|---|---|
| `01_context_analysis` | `context/` | `run_context_team()` |
| `02_planning_specification` | `planning/` | `run_planning_team()` |
| `03_architecture_design` | `architecture/` | `run_architecture_team()` |
| `04_implementation` | `implementation/` | `run_implementation_team()` |
| `05_validation` | `validation/` | `run_validation_team()` |

Stage 06(`devops_release`)은 이번 Migration 범위에 포함하지 않는다
(코드 없음, 책임 재정의 안 함).

## 원칙

- **Team = 하나의 Development 책임 영역.** Agent는 Team 내부의 전문화된
  reasoning/execution 역할이다. 이 둘을 동일 개념으로 취급하지 않는다.
- 각 Team의 상세 책임/Capability/Validation 정의는 대응하는
  `hqs/development/stages/0N_*/README.md`·`RESPONSIBILITY.md`·
  `CAPABILITIES.md`·`VALIDATION.md`가 계속 Source of Truth다 — Team은
  이를 재정의하지 않고 재사용한다.
- 각 Team은 향후 `agents/`(전문화된 reasoning 역할)와 `capabilities/`
  (기존 deterministic capability 재배치) 하위 구조로 확장 가능하다.
  현재 실제로 필요하지 않은 Agent/Capability 파일은 미리 만들지 않는다
  (§8 Agent 구현 원칙 — 독립적 reasoning responsibility가 실제로
  있을 때만 추가).
- Team 간 Handoff 의미는 `hqs/development/stages/contracts.py`가
  정의하는 기존 Contract(`ContextAnalysisResult`/`SpecificationResult`/
  `DesignResult`/`ImplementationResult`/`VerificationResult`)를 그대로
  따른다 — 이번 Migration으로 변경되지 않았다.

## 향후 Agent 후보 (구현 대상 아님, 기록용)

문서(`RFC-0030-dev-hq-stage-agent-team-boundary-analysis.md`, Proposed)가
분석한 실제 Engine 호출 지점 기준:

| Team | 현재 Agent(재사용) | 향후 후보 |
|---|---|---|
| Context | 없음 | Intent/Requirement/Context Retrieval/Ambiguity Agent |
| Planning | Requirements Agent | Decomposition/Dependency/Risk Agent |
| Architecture | Design Agent | Contract/Security/Trade-off Agent |
| Implementation | Backend Agent(code_generation) | Target Identification Agent(RFC-0030 §3 미명명 후보), Test/Debugging/Refactoring Agent |
| Validation | Backend Agent(code_review) | QA Agent(정의는 존재, 미호출 — RFC-0030 §3) |

후보 등재가 곧 구현 승인은 아니다 — §8 기준(독립 reasoning
responsibility·중복 없음·분리 가치·Team 목적 기여)을 만족할 때만
추가하며, 숫자를 맞추기 위해 생성하지 않는다.
