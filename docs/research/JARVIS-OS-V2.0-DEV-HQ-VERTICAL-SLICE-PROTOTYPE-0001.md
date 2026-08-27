# JARVIS-OS-V2.0-DEV-HQ-VERTICAL-SLICE-PROTOTYPE-0001: Development HQ Vertical Slice — Evidence

**문서 성격**: Experimental Implementation 완료 보고서
(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
Implementation" 절 준수). Formal Architecture Decision이 아니다.
Production `core/`, `hqs/`, `dashboard/`, 기존 Runtime/Engine/
Workflow, `BASELINE.md`를 수정하지 않는다.

**원래 요청과 축소 경위**: 원래 요청은 "Production 구조로 Command
→Task→Runtime→Development HQ→Result→Dashboard를 관통하는 최소
구현"이었다. 구현 전 Governance 영향 확인(작업 지시 자체가 요구한
절차)에서 다음 충돌을 발견해 구현 전에 사용자에게 보고했다:

- `hqs/development/IMPLEMENTATION_RULES.md` 금지 항목: **"Runtime
  구현 금지 | Runtime 개념 자체가 Open Decision(ADC-02)이다."**
- `docs/decisions/adc/ADC.md`의 ADC-02(Runtime 존폐)는 지금도 Open,
  우선순위 NOW.
- `ADC-0008-runtime-existence-boundary.md`(RFC-0008 후속)가 이
  질문을 한 번 더 대조했지만 **"Not Accepted (based on current
  evidence)"** — 재검토는 새 RFC를 여는 절차로만 가능하다고 명시.
- `docs/architecture/baseline/STRUCTURE-V1.0-FROZEN.md`의 Deferred
  Decisions("Kernel의 세부 Module 및 Interface 구조")와 Current
  Implementation Rule("Target Structure의 디렉터리를 즉시 생성하지
  않는다 — Migration 계획으로 관리")도 동일 결론.
- Command/Task는 `ADC-0001-core-baseline.md`가 애초에 검토한 5개
  Kernel Module 후보(Governance/Workflow/Memory/Execution Layer/
  Event Bus)에 포함조차 되지 않은 개념 — Runtime보다 이른 단계.

사용자가 **"7번째 Experimental Prototype으로 축소"**를 선택해, 이
문서는 그 축소된 범위(Production `core/` 무생성, `projects/` 격리)
로 진행한 결과를 기록한다.

**핵심 결론**: Command→Task→Runtime→Dev HQ(Adapter)→Result 저장
→Dashboard 관찰 전체 경로가 실제로 연결되어 동작함을 E2E로
확인했다. 새로운 Architecture 결론은 없다 — 기존 6개 Prototype의
Evidence(Task=CANDIDATE, Runtime=CANDIDATE 조건부)를 그대로
재사용했을 뿐이다. 다만 **"Result 저장"** 이라는 새 질문 하나가
이번에 처음 다뤄졌다 — 파일 기반 영속화가 실제로 Dashboard를
Task Registry 객체 참조 없이 동작하게 만든다는 것을 확인했지만,
이것이 별도 Kernel Responsibility로 이어질지는 아직 판단할 근거가
없다(§9).

---

## 1. Governance 사전 확인(구현 전, 작업 지시 §9)

위 "축소 경위"에 기록. **Production 구현은 진행하지 않았다.**
Experimental 범위에서는 Runtime 금지 규칙이 적용되지 않는다 —
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
Implementation" 절이 이미 이전 6개 Prototype에서 Runtime을 다뤘고,
`IMPLEMENTATION_RULES.md`의 금지는 `hqs/development/`(Dev HQ MVP
Production 구현)에 적용되는 규칙이지 `projects/`(Experimental)에는
적용되지 않는다 — 이전 Prototype들과 동일한 경계 해석이다.

---

## 2. Experimental Boundary

- 위치: `projects/dev-hq-vertical-slice/`(격리).
- `hqs/`, `core/`, Production `dashboard/`: **무수정**(`git diff
  main -- hqs/ core/ dashboard/` 0줄).
- `rtb_task.py`/`rtb_runtime.py`(`runtime-boundary`, 이미 main
  병합됨)를 그대로 재사용 — 중복 구현하지 않았다.
- `hqs/development/`를 직접 import하지 않는다 — `vs_dev_hq_
  adapter.py`는 action → 실제 테스트 경로 매핑만 제공하고,
  실행은 `rtb_runtime`이 `pytest.main()`으로만 수행한다(작업 지시
  §5 Adapter 방식).
- Context, Multi-HQ Orchestration, Trading HQ: 포함하지 않았다
  (작업 지시 §8).

---

## 3. 구성 요소와 재사용

| 요소 | 책임 | 신규/재사용 |
|---|---|---|
| `vs_command.py` | Command(immutable), Dev HQ 단독 action 파싱 | 신규(최소) |
| `rtb_task.py` | Task identity/lifecycle | 재사용(무수정) |
| `rtb_runtime.py` | Runtime execution/isolation(Process) | 재사용(무수정) |
| `vs_dev_hq_adapter.py` | action → 실제 Dev HQ Validation 대상 경로 | 신규(매핑만) |
| `vs_result_store.py` | Task 완료 결과를 파일로 영속화 | 신규 |
| `vs_dashboard_view.py` | Registry(RUNNING) + Result Store(완료) 관찰 | 신규(조합) + 재사용 |
| `vs_pipeline.py` | 위 조각을 순서대로 호출(연결 전용, 로직 없음) | 신규 |

`command-contract`의 `resolver._detect_hq`는 이번에 재사용하지
않았다 — Dev HQ 단독 범위라 HQ 판별이 불필요했다(불필요한 결합을
만들지 않기 위한 의도적 선택).

---

## 4. E2E 검증(작업 지시 §6)

`demo.py` 실행 결과(2026-08-27):

```
=== Command 제출 ===
  task_id=a82330a8 status=RUNNING

=== Dashboard 관찰(완료 전) ===
  RUNNING: ['a82330a8']

완료: status=COMPLETED result=(8, 0)

=== Dashboard 관찰(Result Store, 파일만으로) ===
  a82330a8 target=hqs/development/mvp/tests/test_ast_context.py status=COMPLETED result=[8, 0]

=== 알 수 없는 Command ===
  status=FAILED error=unknown_action
```

전체 경로가 실제로 관통했다: 사용자 입력 문자열 → `Command`(불변)
→ `Task.start()`(Runtime에 즉시 위임, 비동기 반환) → `rtb_runtime`
이 Process Worker에서 실제 `pytest`(`hqs/development/mvp/tests/
test_ast_context.py`, 8 tests) 실행 → 완료 결과가 `Task.result`에
반영 → `vs_result_store.save_result()`가 파일로 영속화 →
`vs_dashboard_view`가 **Registry 객체 참조 없이 파일만 읽어도**
동일한 결과를 관찰(자동 테스트 `test_e2e_valid_command_reaches_
dashboard_via_result_file`로 검증).

세 가지 실제 Dev HQ Validation Action(`ast_context`/`stage_01`/
`mvp_0001`, 실행 시간 0.1초~69초) 전부 정확하게 완료됨을 확인
(`test_e2e_covers_all_three_dev_hq_actions`).

---

## 5. Command 불변성, 동시 실행 독립성(재확인)

- `test_command_is_immutable`: `vs_command.Command`는 `frozen=True`
  — 외부 변경 시도가 `FrozenInstanceError`를 실제로 던짐.
- `test_concurrent_different_actions_are_independent`: 서로 다른
  두 Action(`ast_context`, `stage_01`)을 Process 전략으로 동시
  제출 — `task_id` 다름, 결과 각각 정확(`(8,0)`, `(5,0)`).
  `process-runtime-strategy` Evidence가 예측한 그대로다.

이 두 가지는 새로운 발견이 아니라, 기존 Evidence가 실제 Adapter
연결 상황에서도 깨지지 않는지 재확인한 것이다.

---

## 6. 알 수 없는 Command

`"Trading HQ 실행해줘"`처럼 Dev HQ action으로 파싱되지 않는 입력은
**Runtime을 전혀 시작하지 않고** 즉시 FAILED로 기록되고 Result
Store에도 저장된다(`test_unknown_command_fails_without_starting_
runtime`) — 잘못된 Command가 불필요하게 Process를 기동시키지
않는다는 것을 실제로 확인했다.

---

## 7. Dashboard — Observe-only(재확인)

`test_dashboard_module_does_not_import_pipeline`(AST 기반):
`vs_dashboard_view.py`는 `vs_pipeline`을 import조차 하지 않는다 —
실행을 시작/재시도할 **수단 자체가 이 모듈에 없다**(단순히 "호출
안 함"이 아니라 "호출할 방법이 없음"까지 구조로 강제).

---

## 8. Runtime 필요성 재확인 — 이번 Slice 자체는 조건을 만들지 않았다

`process-runtime-strategy` Evidence는 "동일 Target 동시 실행"에서만
Process가 필요하다고 결론지었다. 이번 Vertical Slice의 세 Action
(`ast_context`/`stage_01`/`mvp_0001`)은 서로 다른 파일이고 어느
것도 `monkeypatch`를 쓰지 않는다 — 즉 **이번 Slice 자체는 Process가
꼭 필요한 조건(동일 Target 동시 실행)을 한 번도 만들지 않았다.**
작업 지시 §3이 "Process 전략을 우선 사용"하라고 명시했으므로
그대로 따랐지만, 정직하게 기록하면 **이번 Slice의 실제 실행
패턴만으로는 Thread로도 충분했을 것**이다. Process를 쓴 것은
"이 조건에서 필요해서"가 아니라 "이후 조건이 어떻게 바뀔지 몰라
안전한 기본값을 따른 것"이다 — 이 구분을 Evidence에 남긴다.

---

## 9. Result 저장 — 이번에 처음 다룬 질문

`vs_result_store.py`(파일 기반 JSON 영속화)는 이전 6개 Prototype
에는 없던 새 조각이다. 실제로 확인한 것:

- Task Registry 객체 참조를 버려도(같은 프로세스 안에서 `del`하지
  않았지만, 파일만 읽는 `dashboard.list_completed_results()`가
  Registry를 전혀 참조하지 않고도 완료 결과를 정확히 재현) 결과
  관찰이 가능했다.
- 저장 시점은 Task가 `COMPLETED`/`FAILED`로 전이할 때만
  (`_maybe_persist`) — RUNNING 상태는 저장하지 않는다(파일 기반
  영속화가 필요한 것은 "완료된 사실의 보존"이지 "진행 중 상태의
  중계"가 아니라는 판단, 후자는 Registry가 이미 충분히 다룸).

**이것이 별도 Kernel Responsibility(가칭 "Result Service")로
이어질지는 판단하지 않는다** — 단일 Prototype, 단일 실행
프로세스에서 한 번 관찰한 것뿐이며, `ADC-0008`이 Runtime에 대해
요구한 것과 같은 기준("반복 관찰")이 아직 없다. Evidence로만
기록한다.

---

## 10. Governance / Boundary 검증

- `git diff main -- hqs/ core/ dashboard/`: 0줄(Production
  무수정).
- `git status`: `projects/dev-hq-vertical-slice/`,
  `docs/research/JARVIS-OS-V2.0-DEV-HQ-VERTICAL-SLICE-PROTOTYPE-0001.md`
  외 변경 없음.
- 신규 테스트: 7 passed
  (`pytest projects/dev-hq-vertical-slice/tests/ -q`, 58.23초 —
  `mvp_0001`(~69초 대상) 1회 포함).
- 전체 회귀: `pytest --ignore=archive -q` → **355 passed**(이전
  348 → 355, +7, 0 failed). `vs_` 접두어로 이름 충돌 없이 첫
  실행부터 통과.

---

## 11. Refactoring Audit

- **Command/Task 책임 중복?** 없음 — `Command`는 파싱된 의도만,
  `Task`는 실행 lifecycle만 가진다.
- **Task/Runtime 책임 중복?** 없음 — `rtb_task.py`를 그대로
  재사용했으므로 이전 Prototype에서 이미 검증된 분리가 그대로
  유지된다.
- **Runtime이 실제 필요한지?** §8 참조 — 이번 Slice 자체의 실행
  패턴만으로는 필요하지 않았다(정직하게 기록). "우선 사용" 지시를
  따른 것이지 이 Slice가 그 필요성을 새로 증명한 것은 아니다.
- **불필요한 lifecycle?** `PENDING`은 이번에도 관찰되지 않았다
  (다섯 번째 재확인).
- **불필요한 Context?** 추가하지 않았다.
- **불필요한 abstraction?** `vs_result_store.py`는 ORM/Schema
  Migration 없이 JSON 파일 읽기/쓰기 함수 3개뿐 — 과설계 없음.
- **Production Architecture 침범?** 없음(§10 diff).
- **HQ isolation 위반?** 없음 — Dev HQ 문자열만 다뤘고 Investment/
  Trading 참조 없음.
- **Dashboard가 execution을 관리하는지?** 아니오(§7, AST로 강제
  검증).
- **Prototype이 미래 Architecture를 과도하게 선행 구현했는지?**
  `vs_result_store.py`가 "Result 저장"이라는 새 개념을 만든 것은
  사실이지만, 재사용 가능한 API·Schema·Registry로 일반화하지
  않았다(파일 3개 함수뿐) — 과도한 선행 구현은 아니라고 판단한다.
  다만 §9에서 명시한 대로 이 개념 자체의 장기적 필요성은 판단하지
  않았다.
- **"Task를 만들기 위해 문제를 만든 것은 아닌가"**: 아니오 —
  Task는 이번에 새로 만들지 않고 재사용만 했다.

---

## 12. Kernel Impact

없음. Command/Task/Runtime/Result 어느 것도 Cross-HQ 공통성이 실제
관찰된 것이 아니라(Dev HQ 단독 범위), Kernel Candidate 기준에
해당하지 않는다.

---

## 13. Governance Impact

없음. RFC/ADC/ADR 생성하지 않음. Production `core/`, Production
Runtime/Task/Command/Result 생성하지 않음. `IMPLEMENTATION_RULES.md`
의 Runtime 금지는 Dev HQ Production 범위에 대한 것이며 이번
Prototype(Experimental, `projects/`)에는 적용되지 않는다 — 위반
없음.

---

## 14. Next Step

우선순위 미확정 — 사용자 결정 필요.

1. **ADC-02(Runtime 존폐) 재검토 RFC**: 이번까지 포함해 7개
   Prototype이 쌓은 Evidence(Task=CANDIDATE, Runtime=CANDIDATE
   조건부, "동일 Target 동시 실행"이라는 구체적 조건)가
   `ADC-0008`이 요구한 재검토 조건(§부족한 Evidence 2번 — "Runtime
   미결정으로 인한 반복 관찰")에 해당하는지 판단이 필요하다 — 이
   문서는 그 판단을 내리지 않는다(Governance 판단은 별도 Review
   대상).
2. **Result 저장 개념의 반복 관찰**: 다른 Prototype/시나리오에서도
   "완료 결과를 프로세스 밖에서 관찰해야 하는 필요"가 반복되는지
   지켜본다.
3. Trading HQ 등장 시 3-HQ 재검증(이전 Prototype들과 동일하게
   보류).

---

## 최종 보고

Command→Task→Runtime→Dev HQ(Adapter)→Result 저장→Dashboard 관찰
전체 경로를 실제로 관통 연결해 E2E로 검증했다(원래 요청은 Production
구현이었으나, 구현 전 Governance 확인에서 `IMPLEMENTATION_RULES.md`
의 명시적 Runtime 구현 금지와 ADC-02 Open 상태를 발견해 사용자
승인 하에 7번째 Experimental Prototype으로 축소). Task/Runtime은
`runtime-boundary` Prototype을 그대로 재사용해 중복 구현하지
않았고, Command 불변성·동시 실행 독립성·Dashboard Observe-only
원칙이 실제 Adapter 연결 상황에서도 깨지지 않음을 재확인했다. 이번
Slice 자체는 Process가 필요한 조건("동일 Target 동시 실행")을
만들지 않았다는 것을 정직하게 기록했다 — Process 사용은 지시를
따른 것이지 새 필요성 증명이 아니다. "Result 저장"이라는 새 질문을
처음 다뤘으나 별도 Responsibility로 일반화하지 않았다. Kernel/
Governance 영향 없음. Production 승격 판단은 이 문서의 권한 밖이다
— ADC-02가 여전히 Open이므로, 이번 Evidence를 포함한 재검토는
별도 Governance 절차(RFC)를 통해서만 가능하다.

---

Architecture Change: 없음
Contract Change: 없음
Production Code Change: 없음
Tests: 신규 7 passed, 전체 저장소 355 passed(0 failed, 회귀 없음)
E2E: 완료 — Command→Task→Runtime→Dev HQ→Result 저장→Dashboard 관찰 전체 경로 실제 검증(`demo.py`, 자동 테스트 `test_e2e_valid_command_reaches_dashboard_via_result_file`)
RFC: 없음(§14에서 후보로만 제시, 이 문서가 열지 않음)
ADC: 없음
ADR: 없음
PR: 미생성(사용자 승인 대기)
Commit: `a0fa2a8`
Branch: `claude/dev-hq-vertical-slice-prototype`(main에서 분기, `runtime-boundary`는 이미 main에 병합되어 있어 별도 Prototype 브랜치 의존 없음)
Next Implementation Candidate: ADC-02(Runtime 존폐) 재검토 RFC 필요성 판단, Result 저장 개념의 반복 관찰, 또는 Trading HQ 등장 시 3-HQ 재검증 — 우선순위 미확정, 사용자 결정 필요
