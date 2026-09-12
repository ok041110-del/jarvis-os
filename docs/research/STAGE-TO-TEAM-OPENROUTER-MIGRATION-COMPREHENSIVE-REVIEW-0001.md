# Stage 01~05 → Team 01~05 + OpenRouter Migration — Comprehensive Review

## Summary

- 목적: "테스트 PASS"만으로 완료를 주장하지 않고, Stage→Team rename,
  Team의 실제 Multi-Agent 여부, 설계된 Parallelization의 실제 구현
  여부, OpenRouter Migration의 완전성, Contract/Architecture 보존
  여부를 실제 코드 기준으로 재검증한다.
- **핵심 발견**: Team 01~05 중 **Team 01만 실제 Multi-Agent + 실제
  병렬 실행 + 실제 Aggregation**을 갖췄다(L3). Team 02는 단일 LLM
  호출 + 결정적 후처리(L1), Team 03/04는 단일 LLM 호출뿐인 이름만
  Team 래퍼(L0), Team 05는 4개 결정적 검사 + 1개 LLM Review가
  분리돼 있고 간단한 Aggregator는 있으나 전부 순차 실행이며 Test
  격리도 없다(L2, 실제로는 원본 파일을 직접 mutate 후 restore).
- Stage→Team rename 자체는 **실제로 동작하는 진짜 진입점 교체**다
  (`workflow.py` → `teams/*/team.py` → `stages/0N_*/stage_0N.py`,
  importlib 동적 로드, 재구현 없음) — 그러나 이 rename을 승인한
  전용 RFC/ADC/ADR이 없고(`HANDOVER.md` 서술만 근거), `workflow.py`
  내부 dict key/변수명은 여전히 전부 "stage_XX"라 Team이 실제
  호출 대상이라는 사실과 이름이 어긋난다 — 둘 다 "고장"은 아니지만
  Governance/일관성 공백으로 기록한다.
- OpenRouter Migration은 **완전하고 정확하다** — Team → Stage →
  Agent → `openrouter_engine.py`까지 실제 call path가 전부 연결됨을
  직접 import 실행으로 확인했고, 하드코딩된 모델명·Central Router·
  순환 import·끊어진 의존성이 없다. Free Pool → Deterministic
  Filter → ≤3 Candidate → `models[]` 구조도 코드에 그대로 존재한다.
  의도적으로 범위 밖에 남긴 두 파일(`qa.py`, `workflow_ast_context.py`)
  은 실제 Production 파이프라인에서 호출되지 않음을 재확인했다.
- Contract/Architecture는 100% 보존됐다 — 이전 Migration 커밋
  (`2da2e9d..8ca4bc7`) diff에 `contracts.py`/`stage_0N.py` 어느 것도
  포함되지 않았다.
- 테스트: **352 passed, 6 skipped**(이 리뷰 세션에서 독립적으로
  재실행해 확인, 회귀 없음).
- **Production 코드는 이 리뷰 세션에서 전혀 수정하지 않았다.**
  `ADR-0027` §9 Validation Gate는 그대로 OPEN(미검증) 상태로 유지했다
  — 오늘 어떤 실제 OpenRouter API 호출도 시도하지 않았다.

---

## 1. Stage → Team Rename 검증

### 실제 진입점 확인(코드로 직접 확인)

```
cli.py → workflow.py::run_workflow()
  → teams/context/team.py::run_context_team()      → stage_01_multi_agent.py
  → teams/planning/team.py::run_planning_team()     → stage_02.py::run_stage_02()
  → teams/architecture/team.py::run_architecture_team() → stage_03.py::run_stage_03()
  → teams/implementation/team.py::run_implementation_team() → stage_04.py::run_stage_04()
  → teams/validation/team.py::run_validation_team() → stage_05.py::run_stage_05()
```

- 5개 `teams/*/team.py` 전부 `importlib.util.spec_from_file_location()`
  으로 `stages/0N_*/stage_0N.py`를 파일 경로로 동적 로드하고, 그
  안의 `run_stage_0N()`을 그대로 호출한다 — 재구현 없음(직접 확인,
  `teams/planning/team.py:17-20`, `teams/architecture/team.py:17-20`,
  `teams/implementation/team.py:19-23`, `teams/validation/team.py:17-22`).
- `python3 -c "..."`로 `workflow.py` 전체를 실제 로드해 Team→Stage→
  Agent→Engine 전체 의존성 그래프가 import 시점에 깨지지 않음을
  직접 실행으로 확인(§4).

### ACTIVE STALE vs HISTORICAL 구분

| 유형 | 위치 | 판정 |
|---|---|---|
| ACTIVE(정상) | `workflow.py`의 `_load_team()`이 `teams/*` 5개를 로드해 실제 파이프라인을 구성 | 정상 — Team이 실제 호출 대상 |
| **FLAG(비파괴, 일관성 문제)** | `workflow.py:49-53` — `stage_01 = context_team.stage_01` 등으로 Stage 모듈 객체를 Team 래퍼 레벨에서도 노출(기존 `mvp/tests/test_workflow_integrated.py`의 monkeypatch 하위 호환 목적) | 의도적 하위 호환 조치, 그러나 Stage/Team 이름이 같은 파일에서 혼용됨 |
| **FLAG(비파괴, 일관성 문제)** | `workflow.py:60-110` 결과 dict key가 전부 `"stage_01"`~`"stage_05"`(실제 호출은 `run_context_team()` 등 Team 함수인데 결과 데이터 모델은 Stage 이름) | 오늘 당장 깨지는 것은 없으나 향후 혼동 소지 |
| HISTORICAL(정상) | `mvp/tests/test_stage_01.py`~`test_stage_05.py` 등이 `stages/0N_*/stage_0N.py`를 직접 import해 white-box 테스트 — `HANDOVER.md` §11이 "제거하지 않음"을 명시적으로 밝힘 | 의도적 보존, 문제 아님 |
| HISTORICAL(정상) | `stages/**/*.py` 자체의 "Stage 01~05" docstring/주석 | 실제 구현 파일 이름 그대로, 문제 아님 |
| **GOVERNANCE GAP** | Team rename 자체를 승인한 전용 RFC/ADC/ADR이 `docs/architecture/core/`에 없음 — `RFC-0030`(Proposed, 미채택 분석 문서)만 배경으로 인용되고, 실제 근거는 `HANDOVER.md`의 서술뿐 | RFC/ADC/ADR을 임의로 만들지 않는다(이번 리뷰 지시) — 이 문서가 그대로 기록만 한다 |
| 정상 | `stages/06_devops_release/`는 Team 대응 없음(`teams/README.md`가 범위 밖으로 명시) | 문제 아님 |
| 정상 | `stages/**/*.py`가 `teams`를 참조하는 사례 0건(단방향 의존, 순환 없음) | 문제 아님 |

**결론**: Rename은 코드 레벨에서 실제로 완료됐고 정상 작동한다(cosmetic wrapper가 아니라 실제 진입점 교체). 다만 (a) 전용 Governance 문서 부재, (b) `workflow.py` 내부 명명 불일치라는 두 가지 비파괴적 findings가 있다.

## 2. Team 01~05 실제 구조 검증(Multi-Agent 깊이)

| Team | 실제 Agent/Check 목록 | 실행 방식 | Aggregator |
|---|---|---|---|
| 01 Context | 4개 reasoning agent(intent/goal/requirement/ambiguity, `reasoning.py:72-115`) + 3개 결정적 code-analysis 유닛(`code_analysis.py:59-160`) + PRD synthesis 1개 | **실제 병렬**(`ParallelRunner`가 `ThreadPoolExecutor`로 각 phase 내부를 동시 실행, `parallel_runner.py:113-140`, `stage_01_multi_agent.py:41-72`) | 있음 — `aggregate_reasoning()`(중복 제거/충돌 탐지/신뢰도 평균, `reasoning.py:156-231`) + `aggregate_context()`(`code_analysis.py:174-185`) |
| 02 Planning | 1개 LLM 호출(`task_dependency_agent.py:44`) + 결정적 파이프라인(스키마/사이클/위상정렬, `planning_pipeline.py`) | 순차 | 없음(단일 생산자) |
| 03 Architecture | 1개 LLM 호출(`stage_03.py:59`) | 순차 | 없음 |
| 04 Implementation | 1개 LLM 호출(`stage_04.py:66`). Ponytail/Consistency/Minimality Multi-Agent 설계는 `stages/04_implementation/architecture_validation/`에 **실험 코드로만 존재**, `stage_04.py`/`team.py` 어디서도 import되지 않음(직접 grep 재확인, 0건) — `ADC-0040` §구현 금지 확인이 "Multi-Agent/Ponytail Production 배선 없음"을 이미 명시 | 순차, 병렬 primitive 0건 | 없음 |
| 05 Validation | 4개 결정적 검사(Structure/Scope-spec/Scope-design(AST)/Test) + 1개 LLM Review — `stage_05.py:224-283`에서 전부 한 함수 안 순차 실행 | 순차(`ThreadPoolExecutor`/`ParallelRunner` 참조 0건, 직접 grep 재확인) | 있음, 단순(`_build_check_results`/`_determine_verdict`가 4개 결정적 검사만 병합, LLM Review는 advisory로 병합 대상 아님) |

**Test Isolation(Team 05) 실측 재확인**: `stage_05.py:140-159`
(`_run_pytest_with_applied_implementation`)를 직접 읽어 확인한 결과,
**Test Workspace 복제가 아니라 실제 저장소 파일을 직접 mutate한 뒤
`finally`에서 restore**하는 방식이다:

```python
path = module_source_path(module_name)
original = path.read_text(encoding="utf-8")
try:
    path.write_text(implementation, encoding="utf-8")
    result = subprocess.run([...pytest...], cwd=ROOT, ...)
    ...
finally:
    path.write_text(original, encoding="utf-8")
```

`projects/stage05-parallel-validation-harness-v1/`(격리된 Workspace
복제 방식을 실제로 구현·검증한 실험 프로젝트)는 `stage_05.py`/
`teams/validation/team.py` 어디에서도 참조되지 않는다(0건 확인) —
설계된 격리 메커니즘이 Production에 배선되지 않았다는 뜻이다.

## 3. Parallelization — "설계 가능" vs "실제 병렬 실행"

| 항목 | 설계 문서(Governance) | Production 실제 구현 |
|---|---|---|
| Team 01 Reasoning 4-Agent | (설계 자체가 Accepted, `RFC-0033`/`ADC-0036`/`ADR-0021`) | **실제 병렬 구현·배선됨**(`ThreadPoolExecutor`) |
| Team 04 Implementation/Consistency/Minimality + Ponytail | `RFC-0037` 제안, `ADC-0040` Decision = **NOT DETERMINED**(Real Engine Evidence 부재로 판정 보류, Production 배선 명시적으로 금지 확인) | **미배선** — 실험 코드만 존재 |
| Team 05 6-Responsibility Parallel DAG(Structure/Scope/AST/Dependency/Test/Review) + Aggregator + Test Isolation | `RFC-0039` 제안, `ADC-0042` Decision = **PARTIAL**(Independence 구조는 confirmed, Production Adoption은 NOT DETERMINED), `ADR-0025` Boundary만 Accepted(Scoped), Parallel/LLM Review Adoption은 NOT YET DETERMINED | **미배선** — 4 deterministic + 1 Review가 순차 실행, Isolation 없음(직접 mutate+restore) |

**결론**: Team 04/05의 병렬화는 "독립적으로 가능하다는 것을
문서/실험으로 확인"까지만 진행됐고, "실제로 병렬 실행되고 있다"는
사실이 아니다 — 이는 은폐된 문제가 아니라 해당 ADC들 자신이 이미
정직하게 NOT DETERMINED/PARTIAL로 기록해 둔 상태이며, 이번 리뷰가
Production 코드 재확인으로 그 기록이 현재도 정확함을 재검증했다.

## 4. OpenRouter Migration 완전성/정확성 검증

### Call Path 실측(실제 import 실행으로 확인, 추측 아님)

```
$ python3 -c "from mvp.agents import backend, design, requirements, qa; ..."
backend.call_engine_review.__module__     -> mvp.openrouter_engine
backend.call_engine_generation.__module__ -> mvp.openrouter_engine
design.call_engine.__module__             -> mvp.openrouter_engine
requirements.call_engine.__module__       -> mvp.openrouter_engine
qa.call_engine.__module__                 -> mvp.engine   (의도적으로 미전환, Stage 05 미사용)

$ python3 -c "<workflow.py 전체 importlib 로드>"
workflow.py fully loaded OK (Team→Stage→Agent→Engine 전체 체인 import 성공)
```

- `reasoning.py`/`task_dependency_agent.py`도 동일하게 `mvp.openrouter_
  engine`을 가리킴(소스 확인, 이전 Migration 커밋에서 이미 변경).
- **순환 import**: 없음 — `openrouter_engine.py`는 `mvp.agents`/
  `stages`/`teams` 어느 것도 import하지 않는 leaf 모듈이다(소스
  확인, `hqs/development/mvp/openrouter_engine.py` 전체에 그런
  import 없음).
- **Missing dependency**: 없음 — `workflow.py` 전체 로드가 실제로
  성공했다(위 실행 결과).

### Free Pool → Deterministic Filter → ≤3 → `models[]` 구조 확인

`hqs/development/mvp/openrouter_engine.py`에서 직접 확인:

- `MAX_CANDIDATES = 3`(58행, `OPENROUTER-MODELS-ARRAY-LIMIT-
  REVERIFICATION-0001.md` §6 API-level limit 인용).
- `_fetch_free_model_pool()`(103행) → `_deterministic_filter()`
  (130행) → `_select_candidates()`(157행, `kept_model_ids[:MAX_
  CANDIDATES]`) → `_single_chat_call()`(206행, `"models": list(
  candidate_ids)`) — 8단계 경로 중 Jarvis 책임 구간이 코드에
  그대로 존재.

### 하드코딩/Central Router 검색(재실행, 이 리뷰 세션 자체 결과)

```
$ grep -rniE "gpt-4o|claude-[0-9]|nemotron|nex-agi|inclusionai|ling-3\.0" \
    hqs/development/stages/ hqs/development/teams/ hqs/development/mvp/agents/ \
    hqs/development/mvp/openrouter_engine.py hqs/development/workflow.py hqs/development/cli.py
(0건)

$ find hqs/development -iname "*router*.py" -o -iname "*gateway*.py"
openrouter_engine.py, test_openrouter_engine.py, fake_openrouter_server.py
(전부 "openrouter" 문자열 안의 "router" 부분 매칭 — 실제 Router/Gateway 모듈 아님)
```

### 기존 ChatGPT/Claude active path 잔존 확인

`qa.py`(Claude Code Engine 유지)와 `workflow_ast_context.py`(ChatGPT
Engine 유지) 2개만 이전 Engine을 그대로 쓴다 — 둘 다 이번 리뷰가
직접 재확인한 대로 **실제 Production Stage 01~05 파이프라인에서
호출되지 않는다**(`qa_agent_test_execution`은 `stage_05.py`가
호출하지 않음, `workflow_ast_context.py`는 `workflow.py`/`teams/`
어디에서도 import되지 않는 별도 유틸리티). 의도된 범위 제외이며
실제 활성 경로의 잔존이 아니다.

## 5. Contract/Architecture 보존 검증

```
$ git diff 2da2e9d..8ca4bc7 --stat
```

Migration 커밋에 `contracts.py`/`stage_01.py`~`stage_05.py`/
`stage_01_multi_agent.py`/`planning_pipeline.py` 등 Contract·순서·
책임을 정의하는 어떤 파일도 포함되지 않았다 — 변경된 파일은
`mvp/agents/*.py`(import 1줄), `stages/01_context_analysis/reasoning.py`
+`task_dependency_agent.py`(import 1줄), 신규 `openrouter_engine.py`,
신규/갱신 테스트뿐이다.

- **Failure semantics**: `workflow.py`의 `_engine_failure_message()`/
  `is_engine_failure()`는 `except Exception`으로 어떤 Engine이
  던진 예외든 동일하게 `"Engine call failed: {exc}"`로 감싼다 —
  `openrouter_engine.py`도 다른 두 Engine과 동일하게 `RuntimeError`
  단일 타입만 던지므로(소스 확인) 이 메커니즘이 그대로 작동한다.
  Engine 교체로 인한 failure semantics 변화 없음.
- Stage ordering(`workflow.py`의 01→02→03→04→05 순차 호출) 무변경.
- Agent/Capability 경계(4개 Agent 모듈의 함수 시그니처) 무변경 —
  각 함수는 여전히 동일한 인자/반환 타입을 갖는다.

## 6. Test 결과(이 리뷰 세션에서 독립 재실행)

```
$ pytest mvp/tests/ -q
352 passed, 6 skipped
```

이전 Migration 세션이 보고한 것과 동일한 결과 — 이 리뷰가 독립적으로
재현해 확인했다(신뢰하지 않고 재실행).

---

## 최종 Matrix

| Team | Rename | Multi-Agent | Actual Parallel | Aggregation | OpenRouter Import | Call Path | Contract | Tests |
|---|---|---|---|---|---|---|---|---|
| 01 | ✅ 실제 진입점 교체 | ✅ 4 reasoning + 3 code-analysis + PRD | ✅ ThreadPoolExecutor 실배선 | ✅ aggregate_reasoning/aggregate_context | ✅ openrouter_engine | ✅ 검증됨 | ✅ 보존 | ✅ PASS |
| 02 | ✅ | ❌ 단일 LLM 호출(+결정적 파이프라인) | ❌ 순차 | ❌ 단일 생산자 | ✅ openrouter_engine | ✅ 검증됨 | ✅ 보존 | ✅ PASS |
| 03 | ✅ | ❌ 단일 LLM 호출 | ❌ 순차 | ❌ 없음 | ✅ openrouter_engine | ✅ 검증됨 | ✅ 보존 | ✅ PASS |
| 04 | ✅ | ❌ 단일 LLM 호출(Ponytail 설계는 미배선) | ❌ 순차, 병렬 primitive 0건 | ❌ 없음 | ✅ openrouter_engine | ✅ 검증됨 | ✅ 보존 | ✅ PASS |
| 05 | ✅ | ⚠️ 4 결정적 체크 + 1 LLM Review(분리는 있음, "Agent"는 Review 1개뿐) | ❌ 순차, Isolation 없음(직접 mutate+restore) | ⚠️ 단순(결정적 4개만 병합) | ✅ openrouter_engine | ✅ 검증됨 | ✅ 보존 | ✅ PASS |

## 최종 판정

- **Team Architecture: PASS WITH FINDINGS** — Team 01만 설계 의도
  (Multi-Agent + Parallel + Aggregation)를 실제로 구현했다. Team
  02/03/04는 이름만 Team인 사실상 단일 Agent MVP 래퍼이고, Team 05는
  분리된 책임과 간단한 Aggregator는 있으나 병렬도 격리도 없다. 이
  자체는 각 팀의 governing ADC(`ADC-0040`/`ADC-0042`)가 이미 NOT
  DETERMINED/PARTIAL로 정직하게 기록해 둔 상태와 일치한다 — "새로운
  나쁜 소식"이 아니라 "이미 알려진 상태의 재확인"이다.
- **Stage→Team Migration: PASS WITH FINDINGS** — 실제 진입점 교체가
  정상 작동하나(재구현 없음, 재사용만), 전용 Governance 문서 부재와
  `workflow.py` 내부 명명 불일치라는 두 비파괴적 finding이 있다.
- **OpenRouter Migration: PASS** — call path/import/구조/하드코딩
  부재/Central Router 부재 전부 실측 재확인, 문제 발견 0건.

### Team 01~05 Level

| Team | Level |
|---|---|
| 01 Context | **L3** |
| 02 Planning | **L1** |
| 03 Architecture | **L0** |
| 04 Implementation | **L0** |
| 05 Validation | **L2** |

어느 Team도 L4(실제 Engine Evidence까지 검증)에 도달하지 않았다 —
이번 리뷰가 실제 OpenRouter API 호출을 금지했으므로 L4 판정 자체가
범위 밖이다(의도적 제약, 결함 아님).

### 발견된 문제와 수정 필요사항(수정하지 않고 보고만 함)

1. **[Governance Gap]** Stage→Team rename을 승인하는 전용 RFC/ADC/ADR
   부재 — `HANDOVER.md` 서술만 근거. (수정 제안: 필요시 별도
   RFC/ADC/ADR로 사후 추인 검토, 이번 리뷰는 임의로 만들지 않음.)
2. **[일관성]** `workflow.py`가 실제로는 Team 함수를 호출하면서
   결과 dict key/내부 변수는 전부 "stage_XX"로 남아 있음 — 오늘
   당장 깨지는 것은 없으나 향후 "team_XX" key를 기대하는 코드가
   추가되면 혼동 위험.
3. **[Architecture 기대치 불일치]** "Team"이라는 이름이 Multi-Agent
   구조를 암시하지만 실제로는 Team 02/03/04가 단일 Agent다 — 사용자가
   예고한 후속 "Stage 01~05 Team Architecture Review"에서 본격적으로
   다룰 주제로 남긴다(이번 리뷰는 사실 확인까지만).
4. **[재확인, 새 문제 아님]** Team 04 Ponytail, Team 05 6-Responsibility
   Parallel DAG + Test Isolation은 각각 `ADC-0040`/`ADC-0042`가 이미
   NOT DETERMINED/PARTIAL로 유보한 상태 그대로이며, 이번 리뷰가
   Production 코드 재확인으로 그 상태가 여전히 유효함을 확인했을
   뿐이다 — Governance 문서와 실제 코드 사이의 불일치는 없다.

### 테스트 결과

`pytest mvp/tests/ -q` → **352 passed, 6 skipped**(회귀 없음, 이 리뷰
세션에서 독립 재실행으로 확인).

---

## 별도 확인 항목

- **Architecture**: 변경 없음(Team 구조/Stage 순서/Engine Boundary
  전부 기존 그대로, 이번 리뷰는 읽기 전용).
- **Contract**: 변경 없음(§5).
- **Governance**: `RFC-0040`/`ADC-0043`/`ADR-0026`/`RFC-0041`/
  `ADC-0044`/`ADR-0027` 전부 무수정. 새 RFC/ADC/ADR 미생성(이번
  리뷰의 발견은 이 Evidence 문서 하나로만 기록).
- **Production Code**: 이 리뷰 세션에서 **전혀 수정하지 않음**
  (`git status --short` 완전히 clean 상태로 리뷰 시작, 리뷰 종료
  시점까지 무변경).
- **Validation Gate**: `ADR-0027` §9 — **OPEN, 그대로 유지**. 오늘
  실제 OpenRouter API 호출을 단 한 번도 시도하지 않았다.
- **Branch**: `claude/jarvis-openrouter-validation-bin9aj`
- **Commit**: 이 리뷰 자체는 코드를 바꾸지 않았으므로, 직전 유효
  commit은 `8ca4bc729101ee66cb4d2e3bbaccca6f601b5caa`(Migration
  구현) — 이 Evidence 문서 추가가 새 commit이 된다.
- **PR**: 없음(생성하지 않음).

## Related

- `docs/architecture/core/RFC-0041-openrouter-production-engine-migration.md`
- `docs/architecture/core/ADC-0044-openrouter-production-engine-migration-decision.md`
- `docs/architecture/core/ADR-0027-openrouter-production-engine-migration-adoption.md`
- `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md`
- `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md`
- `docs/architecture/core/ADR-0025-stage05-parallel-validation-architecture-boundary.md`
- `docs/research/OPENROUTER-PRODUCTION-ENGINE-MIGRATION-IMPLEMENTATION-0001.md`
- `hqs/development/HANDOVER.md`("Development HQ Team Architecture Migration v1" 항목)
- `hqs/development/teams/README.md`

---

**Migration Review: PASS WITH FINDINGS**
**Validation Gate: OPEN — NOT YET VALIDATED**
