# PHASE12-RUNTIME-AUTOMATION-AUDIT-0001: Runtime/Automation 필요성 검증 (READ-ONLY)

이 문서는 사용 후기가 아니다. 기존 Governance/Evidence 문서를 종합한
READ-ONLY 조사 기록이다. 코드를 한 줄도 작성/수정하지 않았다(`git
status --porcelain` 이번 문서 추가 외 변경 없음). Runtime Architecture,
Scheduler, Event Bus, Registry를 설계·구현하지 않았다. RFC/ADC/ADR을
작성하지 않았다.

## 1. 현재 Runtime/Automation Architecture·Governance 정의

- **ADC-02(`docs/03_adc/ADC.md`)**: "Runtime 개념의 존폐" — Concept
  Model은 Runtime을 Service로 유지하나 Core Component 검토는 Scheduler+
  Engine Gateway로 대체를 권고, **상태: Open, 우선순위 NOW.**
- **ADC-0008(`docs/architecture/core/ADC-0008-runtime-existence-boundary.md`)**:
  Not Accepted — "유지"/"대체" 두 후보 모두 확정 근거 부족.
- **GOVERNANCE-REVIEW-0006**: MVP-0038~0048 + Stock/ETF/Dividend Stock
  Dogfooding 9건을 ADC-02 재검토 조건(원 "Core Component 검토" 문서
  확보 / 반복 관찰 축적) 두 가지에 대조 — **둘 다 미충족, Open 유지가
  타당**하다고 판단. ADC 채택 기준(지금 결정 안 하면 진행 불가 / 되돌리는
  비용이 큼) 둘 다 미충족도 재확인.
- **IMPLEMENTATION_RULES.md**: "Runtime 구현 금지 — Runtime 개념 자체가
  Open Decision(ADC-02)이다", "Scheduler 구현 금지 — MVP는 Task 순서를
  스크립트에 하드코딩한다."

**결론**: Runtime은 정의조차 확정되지 않은 Open Decision이며, 지금까지
Governance가 이를 "필요하다"고 판단한 적이 없다.

## 2. 기존 Dogfooding/MVP에서 반복 작업·자동화 필요성이 실제 발생했는가

- `GOVERNANCE-REVIEW-0006` 표: 9건의 project-local Dogfooding(Stock
  4회, ETF 3회, Dividend Stock 2회) **전부 `runner.py`의 하드코딩된
  순차 함수 호출로 완주**했고, "Workflow를 참조해 Task를 Agent에
  배분하는 별도 Service"의 필요성이 드러난 사례가 없다.
- Development HQ MVP-0001~0052(이번 Phase 9~11 포함)도 전부 `workflow*.py`의
  직접 함수 호출 또는 이번 세션의 임시 실험 스크립트(scratchpad, 매번
  사람/Claude Code가 직접 실행)로 완주했다 — Background 실행이나
  Scheduling 없이 매번 즉시 실행·즉시 결과 확인으로 충분했다.
- 유일하게 "향후 자동화"를 명시적으로 검토 대상으로 남긴 사례는
  `ARTIFACT-DASHBOARD-TRIAL-0001.md` §7(Dashboard 자동 갱신, push
  이벤트 트리거) 하나뿐이며, 그 문서 자신이 "실제 필요가 확인된 뒤
  별도로 검토할 대상"이라고 **이미 DEFER**해 놓았다 — 지금 재점화할
  근거가 이번 조사에서 새로 나오지 않았다.

## 3. 현재 Development HQ/Claude Code workflow로 해결 가능한가

**가능하다 — 실제로 계속 그렇게 해왔다.** 이번 세션 자체가 그 증거다:
Phase 9(N-way 병렬 검증) → Phase 10(Prompt Specification Audit + 2회
Capability Prototype + Boundary Validation) → Phase 11(Prompt Cache
Audit)까지, branch 생성 → 실험 스크립트 작성/실행 → Evidence 문서 작성 →
commit/push 전 과정을 Claude Code가 매번 사람의 지시를 받아 순차
실행했다. Background로 넘기거나 예약 실행이 필요했던 지점은 한 번도
없었다 — 매 Phase가 한 대화 턴 안에서 시작·완료됐다.

## 4. 자동화가 없어서 발생한 실제 비용·지연·누락·반복 작업 Evidence

**찾지 못했다.** `docs/01_mvp/`(MVP-0001~0052), `docs/research/`
전체를 대상으로 "자동화가 없어서 실패/누락/지연됐다"는 실제 관찰을
검색했으나, 그런 사례를 기록한 문서를 찾지 못했다. 반대로 여러
문서가 "자동화는 지금 필요하지 않다"는 판단을 반복 기록했다(§1, §2).
추측을 Evidence로 취급하지 않는다 — "없음"을 실제 결과로 기록한다.

## 5. Background 실행·Scheduling·Event Trigger가 실제 필요한 Use Case인가

| 후보 | 실제 발생 여부 | 근거 |
|---|---|---|
| Background 실행(비동기/장시간 작업을 사람 대기 없이 처리) | **아니오** | 이번 세션 최대 소요 실험(Phase 9 4-way 병렬)도 60초 내외로 동기 실행·즉시 확인 가능했다(`ENGINE-USECASE-0002`) |
| Scheduling(정기 실행) | **아니오** | 모든 Phase가 사람의 명시적 지시로 시작됐다 — 정기적으로 저절로 실행돼야 하는 작업이 관찰된 적 없다 |
| Event Trigger(예: push 이벤트로 자동 재실행) | **후보 1건, 미확정** | `ARTIFACT-DASHBOARD-TRIAL-0001.md` §7이 유일한 후보이나 스스로 "실제 필요 확인 전까지 DEFER"라고 명시 |

## 6. Runtime 없이 해결되는 경우 vs Runtime이 필요한 경우 구분

- **Runtime 없이 해결됨(전부)**: Task 순서 결정(하드코딩 함수 호출),
  Agent-Capability 매핑(리터럴 딕셔너리), Engine 호출(단일 함수
  `call_engine()`), 병렬 실행(호출부 스레드화, `ENGINE-USECASE-0001/0002`),
  Capability 로직 개선(지시문 수정, `MVP-0050/0051/0052`) — 전부 Runtime
  Concept 없이 실제로 완료됐다.
- **Runtime이 필요할 후보(아직 미실현)**: Dashboard 자동 갱신(push
  이벤트 기반) 하나뿐이며, 이마저 "실제 필요"가 아직 확인되지 않았다.

## 7. 기존 Governance에 실제 Trigger/Stop 조건이 존재하는가

**존재한다 — 그리고 지금까지 발동한 적이 없다.**

`IMPLEMENTATION_RULES.md` 구현 중단 트리거 2건:

1. Agent-Capability 매핑이 리터럴 딕셔너리를 넘어 클래스/서비스로
   발전하려는 순간.
2. Task 1→Task 2 호출이 조건문·설정 파일·파서로 대체되려는 순간.

`HANDOVER.md`: "Implementation Stop Trigger·Kernel Extraction Candidate
발생 여부는 신규 작업마다 계속 점검한다 (지금까지 발동 사례 없음)."
이번 Phase 9~11 작업(N-way 병렬, Capability Prototype 2건, Boundary
Validation, Prompt Cache Audit)도 위 두 Trigger 중 어느 것도 발동시키지
않았다 — 전부 기존 문서(`ENGINE-USECASE-0001/0002`, `MVP-0050~0052`,
`PHASE10-CLOSURE-0001`, `PHASE11-PROMPT-CACHE-AUDIT-0001`)가 "Architecture/
Contract 변경 없음"으로 명시했다.

## 8. 판정

**A — 현재 구조로 충분. Runtime DEFER.**

- 근거 (1) 지금 결정하지 않으면 상위 Architecture를 진행할 수 없는가 —
  **아니오**. Development HQ MVP·Investment Dogfooding·Phase 9~11
  전부 Runtime 없이 실제로 완주했다.
- 근거 (2) 결정이 늦어질수록 되돌리는 비용이 매우 큰가 — **아니오**.
  Runtime을 구현한 코드가 여전히 전혀 없어 되돌릴 대상이 없다
  (`GOVERNANCE-REVIEW-0006`과 동일 결론, 이번 조사로 재확인).
- ADC-02 상태는 이 문서가 바꾸지 않는다 — Governance 절차 없이
  상태를 변경하지 않는다. **Open 유지.**

## Runtime Need / Automation Need

**없음(NEED-DRIVEN DEFER).** 유일한 후보(Dashboard 자동 갱신)는 이미
별도 문서가 DEFER 상태로 기록해 뒀다. 다음 조건 중 하나가 **실제로**
관찰될 때만 재조사한다(지금 선제적으로 설계하지 않는다):

1. 위 두 Stop Trigger 중 하나가 실제 코드에서 발동할 때.
2. Background 실행 없이는 완료할 수 없는 실제 장시간 작업이 나타날 때
   (지금까지 모든 작업이 동기 실행으로 충분했다).
3. Dashboard 자동 갱신처럼 사람의 수동 트리거 없이는 해결되지 않는
   실제 반복 업무가 관찰될 때.

## Architecture/Governance

RFC/ADC/ADR 작성 없음. ADC-02 상태(Open) 변경 없음. Scheduler/Event
Bus/Registry 설계·구현 없음.

## Evidence

- `docs/03_adc/ADC.md` ADC-02, `docs/architecture/core/ADC-0008-runtime-existence-boundary.md`
- `docs/architecture/core/GOVERNANCE-REVIEW-0006-adc-02-09-10-dogfooding-evidence-check.md`
- `docs/research/ARTIFACT-DASHBOARD-TRIAL-0001.md` §7
- `development-hq/IMPLEMENTATION_RULES.md` 구현 중단 트리거
- `development-hq/HANDOVER.md` "지금까지 발동 사례 없음"
- 이번 세션 자체(Phase 9~11, `ENGINE-USECASE-0001/0002`, `MVP-0050~0052`,
  `PHASE10-CLOSURE-0001`, `PHASE11-PROMPT-CACHE-AUDIT-0001`) — 전부
  Runtime 없이 완료됨

## Next

- 이번 문서는 READ-ONLY 조사다. 실험/Prototype이 필요한 시점은 §Runtime
  Need 조건이 실제로 충족될 때이며, 지금 선제적으로 설계하지 않는다.
