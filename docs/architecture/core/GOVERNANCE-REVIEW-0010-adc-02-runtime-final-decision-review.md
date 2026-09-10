# GOVERNANCE-REVIEW-0010: ADC-02 Runtime Final Decision Review

**문서 성격**: READ-ONLY Governance Review. **Decision 문서이지만
Baseline 변경 문서는 아니다.** `docs/decisions/adc/ADC.md`의 ADC-02
상태를 이 문서가 직접 바꾸지 않는다 — 아래 §6~§9에서 그 이유를
명시한다. 새 RFC/ADC/ADR을 작성하지 않는다. Production 코드는 한
줄도 수정하지 않았다. ADC-09/ADC-10 등 다른 항목을 재판단하지
않는다.

**질문**: "현재 Jarvis OS에 독립 Runtime Component를 구현할 필요성이
실제 Evidence로 입증되었는가?" — `GOVERNANCE-REVIEW-0006`,
`GOVERNANCE-REVIEW-0009`, `projects/runtime-prototype-v1/`(Runtime
Prototype, 11/11 PASS, NEUTRAL)까지 누적된 모든 Evidence를 종합해
A(독립 Component 채택)/B(Concept 완전 제거)/C(상위 Concept 유지,
독립 구현 미확정) 중 최종 방향을 판단한다. 새 조사는 하지 않는다.

---

## 1. 현재까지 Evidence로 확인된 것

| Evidence | 출처 | 확인된 사실 |
|---|---|---|
| ADC-02 현재 상태 | `docs/decisions/adc/ADC.md` | Open · NOW, 원문 그대로("Concept Model은 Runtime을 Service로 유지 vs Core Component 검토는 폐기 권고") — 이번 조사로도 재확인, 변경 없음 |
| "넓은 범위" Runtime 반복 Not Accepted/Defer | `ADC-0008`(양쪽 후보 Not Accepted), `ADC-0011`(Not Accepted), `ADC-0012`(Defer) | "유지"·"대체" 어느 방향도 근거 부족이 반복 확인됨 |
| "좁은 범위" 책임은 별개 Concept로 이미 Accept | `ADC-0013`/`ADC-0014`/`ADR-0004` → Execution Host(§16.3, Scoped) | Execution Host는 §6 "Runtime" 항목의 재명명이 아니라 별개의 더 좁은 Concept — ADC-02는 이 Accept로 전혀 변경되지 않음(`ADC-0014` §Q2, `ADR-0004` 명시) |
| Dogfooding 9건 + Multi-Agent Handoff 1건 | `GOVERNANCE-REVIEW-0006`, `RFC-0028`(Phase E) | 전부 하드코딩 직접 호출/표준 라이브러리만으로 마찰 없이 완주 — "새 Runtime 없이도 충분하다"는 반대 방향 Evidence만 누적 |
| 문서 조사 종합 | `GOVERNANCE-REVIEW-0009` | Runtime 관련 전체 Decision Chain 대조 결과 C 방향이 가장 정합적이라고 이미 권고(Decision 아님) |
| **Runtime Prototype 실행 Evidence(신규)** | `projects/runtime-prototype-v1/EVIDENCE.md` | 11/11 PASS. Q1(책임 분리)은 이점 있음, Q2(복잡성)는 실비용 있음(코드 3.5배, `shutdown()` 신규 책임), Q5(실제 적합성)는 **Production `run_isolated()` 자체를 호출하는 곳이 저장소에 없음**을 새로 확인. 최종 판정 **NEUTRAL** |
| 실제 구현 검색(이번 재확인) | `grep -rln "class.*Runtime" core/ hqs/ dashboard/` → 0건, `grep -rln run_isolated hqs/ core/` → `execution_host.py` 자기 자신과 테스트 파일 외 0건, `dashboard/` 디렉터리 자체가 저장소에 없음 | Runtime이라는 이름의 독립 Component가 실제 코드 어디에도 없고, 그 밑단인 Execution Host조차 아직 실제 호출부가 없음 |

이번 조사는 위 Evidence를 **재수집하지 않고 그대로 인용**했다(작업
지시 "기존 검증을 반복하지 말고"). Runtime Prototype의 테스트
결과만 이번 세션에서 독립적으로 재실행해 재확인했다(§Validation).

## 2. Runtime 독립 Component가 해결하는 실제 문제가 있는가

**없다.** `hqs/development/workflow.py`(Stage 순차 직접 호출)와
`hqs/investment/teams/stock_team.py`(팀 코드 내부 `ThreadPoolExecutor`
직접 사용) 둘 다, Runtime이 제공하려는 "여러 Execution Unit의
lifecycle 통합 조회"를 필요로 한 적이 없다 — 각자 이미 자신의
방식으로 문제 없이 동작한다. 이 사실은 Runtime Prototype의 Q5가
새로 확인했고(§1), 기존 Dogfooding Evidence(9건 + Handoff 1건)와도
방향이 같다. **문제가 없는 곳에 해법을 놓을 이유가 없다**(작업 지시
원칙 1 — 필요성을 먼저 만들지 않는다).

## 3. Runtime Prototype의 결과가 Architecture 필요성을 입증하는가

**입증하지 않는다.** Prototype이 11/11 PASS로 "정상 동작"했다는
사실 자체는 필요성의 증거로 간주하지 않는다(작업 지시 원칙 3) —
동작 여부와 필요 여부는 다른 질문이다. Q1에서 확인된 이점(명시적
4-상태 lifecycle, 이중 실행 방지)은 **실재**하지만, 그 이점을
소비할 실제 호출부가 없다(Q5). Q2에서 확인된 비용(코드 3.5배, 새
자원 관리 책임)도 **실재**한다. 이점과 비용이 둘 다 확인됐고 그
이점을 필요로 하는 실제 소비자가 없으므로, 이 Evidence는 "채택
정당화"가 아니라 "판단 보류 정당화" 방향으로 수렴한다 — Prototype
문서 자신의 최종 판정(NEUTRAL)과 일치한다.

## 4. Runtime 없이 현재 구조가 요구사항을 충족하는가

**충족한다.** 확인된 사실(§1~§2):

- Execution Host(§16.3, Scoped Accept)가 단일 실행 단위의 dispatch·
  격리 책임을 이미 충족한다 — 단, 현재 그 책임조차 실제 호출부가
  없다(자체 테스트 제외 0건).
- Development HQ의 Stage 진행은 정적 순차 호출로 9건 Dogfooding을
  전부 통과했다.
- Investment HQ의 병렬 실행(Wave)은 팀 코드 내부 `ThreadPoolExecutor`
  직접 사용으로 이미 해결되어 있다.
- Multi-Agent Handoff(Phase E, `RFC-0028`)도 기존 Contract(직접 함수
  호출 + 표준 라이브러리)만으로 마찰 없이 재현됐다.

현재 관찰된 모든 실행 시나리오가 Runtime 없이 충족되고 있다 —
반대 방향(Runtime 없이는 안 되는 사례)은 한 건도 관찰되지 않았다.

## 5. A/B/C 비교

### A. Runtime 독립 Component/Service로 채택

- 지지 Evidence: `BASELINE.md` §6이 Runtime을 Service로 이미 분류해
  둔 Architecture Intent뿐 — 이 자체가 이미 "단독으로는 Accept 근거
  부족"으로 판정된 상태(`ADC-0013` Q0, `GOVERNANCE-REVIEW-0009` §2.3).
- 반대 Evidence: 해결할 실제 문제가 없고(§2), Prototype이 이점과
  비용을 둘 다 실측했으나 이점을 소비할 대상이 없다(§3). ADC 채택
  기준(①지금 결정 안 하면 상위 진행 불가, ②지연 시 되돌리는 비용
  급증) **둘 다 미충족** — Execution Host조차 아직 호출부가 없는데
  그 위에 Runtime을 얹을 이유가 없다.
- **판정**: 기각. Evidence가 뒷받침하지 않는다.

### B. Runtime Concept 완전 제거

- 지지 Evidence: "유지" 방향 근거 부족이 반복 확인됨(`ADC-0008`,
  `ADC-0011` Not Accepted, `ADC-0012` Defer).
- 반대 Evidence: 이 판정들 자체가 "폐기"를 Accept한 적이 없다
  (`ADC-0008`은 대체 후보도 Not Accepted). `BASELINE.md` §16.3과
  `ADR-0004`는 "§6 Runtime 항목을 재명명·삭제하지 않는다"는 판단을
  반복해 왔다. `RFC-0028` §8은 "Multi-Agent Runtime이 영구적으로
  불필요하다고 주장하지 않는다"고 스스로 명시한다. 완전 제거는 지금
  가진 Evidence보다 더 강한 주장이며, 작업 지시 원칙 6("현재 독립
  구현 불필요"와 "Concept 영구 삭제"의 구분)에도 위배된다.
- **판정**: 기각. "영구 불필요"를 확정할 만큼 강한 근거가 없다.

### C. Runtime은 상위 Concept으로만 유지, 독립 구현은 하지 않음

- 지지 Evidence: 지금까지의 모든 Decision Chain이 사실상 이 노선을
  걸어왔다 — `BASELINE.md` §6(Concept 유지, 세부 구조는 Open으로
  유보), `ADC-0013`/`ADC-0014`(좁은 책임만 별도로 "Execution Host"라는
  이름으로 Accept, 넓은 Runtime과 명시적으로 분리), `ADR-0004`(§6
  Runtime 항목 불변), `IMPLEMENTATION_RULES.md`(넓은 Runtime 구현
  계속 금지, 좁은 Execution Host만 Scoped 허용), `RFC-0028`(Multi-Agent
  맥락에서도 기존 Scoped Component로 충분함을 실행 Evidence로 재확인),
  그리고 이번 **Runtime Prototype**(이점은 실재하나 소비자가 없다는
  것을 실행 수준에서 추가 확인, NEUTRAL).
- **판정**: 채택. 지금까지의 실제 Decision Chain과 실행 Evidence
  전부와 정합적이며, A(근거 없는 선제 확정)와 B(근거 없는 영구 삭제)
  양쪽의 과잉을 피한다.

## 6. Evidence 기반 최종 Decision

> **현재 Evidence에서는 Runtime 독립 Component의 필요성이 입증되지
> 않았다. 따라서 현재는 구현하지 않는다. Runtime은 상위 Concept으로
> 남길 수 있으나 독립 Component/Service로 구현하지 않는다. 향후 실제
> 요구사항이나 반복적인 Blocking Evidence가 발생하면 재평가한다.**

이번 조사는 이 결론을 그대로 지지한다(**C 채택, A/B 기각**) — 억지로
Runtime 구현을 시작하지 않는다(작업 지시 마지막 문단).

## 7. 이 Decision이 Architecture/Baseline 변경을 요구하는가

**요구하지 않는다.**

- C는 이미 `BASELINE.md` §6·§16.3, `ADC-0013`/`ADC-0014`/`ADR-0004`가
  실제로 걸어온 노선을 그대로 확인한 것이지, 새로운 노선을 여는 것이
  아니다. §6의 Runtime 항목·§16.3의 Execution Host 정의 어느 쪽도
  바뀔 이유가 없다.
- `docs/decisions/adc/ADC.md`의 ADC-02 상태를 "Open"에서 다른
  상태(예: Defer)로 바꾸는 것 자체도 **형식적으로는 하나의 Architecture
  Decision**이며, 그 문서 자신의 채택 기준("① 지금 결정하지 않으면
  상위 Architecture를 진행할 수 없다, ② 지연 시 되돌리는 비용이
  급증한다")을 충족해야 한다. 이번 Evidence는 둘 다 충족하지 못한다
  — Runtime 없이 모든 실행 Evidence가 계속 진행되고 있고(§4), 코드
  구현이 없어 되돌릴 비용도 없다(§1 grep 결과).

## 8. RFC/ADC/ADR 및 Baseline 변경 필요 여부

**필요하지 않다.** §7의 판단에 따라 새 RFC를 열지 않는다 — RFC를
연다 해도 그 RFC가 근거로 삼을 새 Evidence가 없다(이미 §1의 모든
Evidence를 이 문서가 재사용했을 뿐이다). `ADC.md`의 ADC-02는 **Open ·
NOW로 그대로 유지**한다. 이 문서가 그 상태를 바꾸지 않는 것은
누락이 아니라 §7의 근거에 따른 의도적 선택이다.

## 9. 문서 상태 변경 여부

**변경하지 않는다**(작업 지시 원칙 9). 아래 문서 중 어느 것도 이
Review로 수정하지 않는다.

- `docs/decisions/adc/ADC.md`(ADC-02 상태) — 무변경.
- `docs/architecture/baseline/BASELINE.md`(§6, §16.3) — 무변경.
- `docs/architecture/core/ADC-0008-runtime-existence-boundary.md` —
  무변경(인용만).
- `hqs/development/IMPLEMENTATION_RULES.md` — 무변경(기존 금지
  조항이 이미 이 Decision과 정합적).
- `projects/runtime-prototype-v1/` — 무변경, 격리된 채로 유지(반복적
  가치가 추가로 확인되지 않는 한 RFC 없이 즉시 제거 가능, 원 문서가
  이미 명시).

## 10. Production Runtime 구현 여부

**진행하지 않는다.** §6의 최종 Decision에 따라 필요성이 입증되지
않았으므로 작업 지시 원칙 10에 따라 Implementation을 시작하지 않는다.

---

## 남은 재평가 Trigger (변경 없음, `ADC-0008`이 이미 정의)

1. "Core Component 검토" 원문 확보 — 지금까지 세 차례(`ADC-0008`,
   `GOVERNANCE-REVIEW-0006`, 이 문서) 전부 미확인.
2. 넓은 정의(Workflow 참조·Multi-Task를 Agent에게 배분)의 실제 필요로
   인한 반복 관찰(서로 다른 독립 계기 3건 이상, Rule B) — 지금까지
   축적된 관찰은 전부 "불필요" 방향이며, 형식적 3건 독립 관찰은 여전히
   미충족.

두 조건 중 하나가 실제로 충족되기 전까지, 동일 질문에 대한 추가
Governance Review는 새로운 가치를 만들지 않는다 — 다음 Review는 위
Trigger 중 하나가 실제로 발생했을 때만 열어야 한다.

## Validation (이번 세션에서 독립 재실행)

- `pytest projects/runtime-prototype-v1/tests/ -v` → **11 passed**
  (재확인, `EVIDENCE.md` 원 수치와 일치).
- `pytest hqs/development/mvp/tests -q` → **186 passed, 6 skipped**
  (재확인, 회귀 없음).
- `grep -rln "class.*Runtime" core/ hqs/ dashboard/` → 0건(재확인,
  `dashboard/` 디렉터리 자체가 저장소에 없음).
- `grep -rln run_isolated hqs/ core/` → `execution_host.py`와 그
  테스트 파일 외 0건(재확인, Q5 근거).
- `git diff origin/main --stat` → 이 문서 추가 1건 외 없음(Production/
  Architecture 무변경).

## Self Review

- Evidence만 사용했는가 — **Pass**. `GOVERNANCE-REVIEW-0006`/`0009`,
  `RFC-0028`, `projects/runtime-prototype-v1/EVIDENCE.md`, 기존
  ADC 계보, 실제 grep/pytest 재실행 결과만 인용했다. 새 실험을 만들지
  않았다.
- Runtime 필요성을 먼저 만들었는가 — **아니오**(§2가 "해결할 문제
  없음"에서 출발).
- Prototype 동작 사실을 필요성 증거로 썼는가 — **아니오**(§3에서
  명시적으로 구분).
- "불필요"와 "영구 삭제"를 구분했는가 — **Pass**(§5 B 판정, §6 최종
  Decision 문구).
- 새로운 Architecture를 선제적으로 설계했는가 — **아니오**.
- `ADC.md`를 수정했는가 — **아니오**.
- Production Code를 변경했는가 — **아니오**.
