# ADR-0012: Gate (A) v1 `ADR-0007` 결정 9 잔여 계약 표면 Resolution의 Baseline 반영 (ADC-0023 후속)

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0012` (`docs/decisions/adr/`에는 동명 문서 없음 — 네임스페이스로 구분) |
| 제목 | `ADC-0023`의 Decision(Gate (A) 중 `ADC-0022`가 "별도 Track"으로 남긴 v1 `ADR-0007` **결정 9** — `IWorkflowEngine` Port 존재 지위 / 입력 시그니처 / `WorkflowResult` 반환 타입 — 의 v2 Resolution)을 Architecture Baseline·GLOSSARY에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** — Architecture/Governance Review PASS(아래 §Governance Chain 검증·§Self Review) 이후, 사용자 승인(2026-09-04)으로 §Migration Strategy 1~2를 실행했다: `BASELINE.md` §16.6 "v2 공백의 현재 상태" 문단 재작성 + A-IN·A-IN(a)·명칭·Adapter Contract 도입부 문단에 각 1문장 부기(+ Adapter Contract 문단의 stale cross-reference "미해결 상태로 유지되는 v2 공백" → "v2 공백의 현재 상태" 정정), §17 Version v1.15 → **v1.16** + 변경 이력 1행, `GLOSSARY.md` "Workflow Adapter (Reference)" 절 주석 블록 2문장 정정. §14·§14.1 표·§7 목록·§16.2·§16.6 Reversibility 2문단·Adapter Contract (a)(b)(c)(d) bullet·"실행 단위"·"실행 단위 Lifecycle" 문단·§16.1~§16.5·§16.7·§6 Concept Model 표·`IMPLEMENTATION_RULES.md`·`ADC-0021`·`ADC-0022`는 무변경. feature branch `claude/adr-0012-decision-9-baseline-v1.16`에 commit + PR — `main` 직접 commit/Merge 없음 |
| Context | `docs/architecture/core/ADC-0023-workflow-engine-port-contract-surface-and-engine-seam-resolution.md` — **Status: Decided — ADR Required**, Architecture/Governance Review PASS(§9). D-9b(v1 "Engine" ≠ §16.2 Engine Adapter seam), D-9a(Reversibility seam = 비-§14 유지), D-9c(입력 시그니처 Kernel 미규정), D-9d(결과 반환 타입 Kernel 미정의), D-9e(§7 ↔ §14.1 = 다른 층위), D-9f(결정 9 "해소" 최소 조건 충족), D-Gate-A(Gate (A) "부분 해소" → "해소") |
| 관련 RFC | `docs/architecture/core/RFC-0022-workflow-engine-port-contract-surface-and-engine-seam-boundary.md` §6(F-9a~F-9f Boundary Question, Proposed 유지) |
| 관련 ADC | `docs/architecture/core/ADC-0023-workflow-engine-port-contract-surface-and-engine-seam-resolution.md` |
| 선행 ADR | `docs/architecture/core/ADR-0008`(§16.6 **존재** 등재 — 조건 5로 결정 2/5/9/11 이월), `docs/architecture/core/ADR-0009`(명칭 + Adapter Contract (a)(b)(d) 반영, "명칭만 반영·`IMPLEMENTATION_RULES.md` 무변경" 층위 — 이 ADR이 계승), `docs/architecture/core/ADR-0010`(Gate (C) E4 "부분 충족" 반영, §16.6 내부 문단 + §17 + GLOSSARY 한 문장 층위 — 이 ADR이 계승), `docs/architecture/core/ADR-0011`(Gate (A) 결정 **2·5·11** Resolution 반영, BASELINE v1.15 — 이 ADR이 결정 9로 이어받음) |
| 선행 Decision(참고, 뒤집지 않음) | `ADC-0019` §Decision 조건 1~6·재검토 조건 (c), `ADC-0020` §6 Conditions 1~8, `ADC-0021` §D1~D4·§6~§8, `ADC-0022` §D-0~§D-11c, `ADR-0010` "부분 충족", `docs/architecture/core/ADC-0010`(Engine Caller 위치 Not Accepted), `docs/decisions/adc/ADC.md` ADC-02(Open·NOW), `docs/architecture/core/ADC-0008`(Not Accepted) — 이 ADR은 어느 것도 변경하지 않는다 |

이 ADR은 `ADC-0023`이 이미 내린 Decision을 다시 논의하지 않는다. 새로운
철학·Architecture·Contract를 제안하지 않는다. `ADC-0023` §5 D-9a~D-Gate-A와
§8 지침이 정리한 것을 실제 `BASELINE.md`·`GLOSSARY.md` 문서 변경으로 옮기기
위한 **구현 결정**만 기록한다.

| 단계 | 다루는 것 |
|---|---|
| `RFC-0022` | F-9a~F-9f Boundary Question 개설 — 결정하지 않음 |
| `ADC-0023` | D-9b(seam 구분) / D-9a(비-§14 seam) / D-9c(입력 Kernel 미규정) / D-9d(반환 타입 Kernel 미정의) / D-9e(§7↔§14.1 층위) / D-9f("해소" 최소 조건) / D-Gate-A(Gate (A) 해소) |
| **이 ADR** | `ADC-0023` §8 지침의 Baseline Governance 반영 — §16.6 "v2 공백의 현재 상태" 문단 재작성 + A-IN·A-IN(a)·명칭·Adapter Contract 문단에 각 1문장 부기, §17 v1.15 → v1.16, `GLOSSARY.md` "Workflow Adapter (Reference)" 절 주석 정정 |
| 후속 별도 절차 | §14 Kernel Public Contract 승격(§14 scope의 Context→Execution 확장) / §14.1 #1·#3의 Kernel 귀속 / §16.2 Engine Adapter seam 설계 / Gate (B)·(C) / LangGraph 채택 / Implementation Strategy / `IMPLEMENTATION_RULES.md` Scoped 해제 / Production 구현 |

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0023`이 Decision 범위에서 반영을 지시하지 않은 것, 그리고 사용자
지시가 명시적으로 배제한 것은 **하나도 반영하지 않는다**(`ADC-0023`
§1.2·§6·§7).

| 항목 | 근거 |
|---|---|
| **§14 Kernel Public Contract 승격 / §14 scope의 Context→Execution 확장 / Public Responsibilities·Guarantees·Extension Points·Port·Surface·Interface 신설·수정** | `ADC-0023` §D-9a·§6 조건 7 — seam 지위 = 비-§14 유지. §14 항목 추가 없음. §14 승격은 §14 scope 확장이라는 상위 별도 절차(별도 RFC → ADC → ADR) |
| **§14.1 표의 행 상태 변경 (#1 "Task 전달 책임" / #3 "Engine 호출 책임"의 Kernel 귀속)** | `ADC-0023` §D-9c·§D-9e·§7 — "미결" 상태 그대로. 이 ADR의 §16.6 갱신은 "Kernel은 규정하지 않는다"를 §16.6 본문에만 서술하고 §14.1 표를 건드리지 않는다 |
| **§7 System Boundary 목록 편집** | `ADC-0023` §D-9e (4) — §7은 "책임 소재" 선언. 이 ADR은 §16.6 명칭 문단에 §7↔§14.1 층위 해석 1문장만 부기하고 §7 원문을 수정하지 않는다 |
| **§16.2 Engine Adapter / §11 Engine Gateway / `ADC-0010`(Engine Caller 위치 Not Accepted) 재판단** | `ADC-0023` §D-9b·§6 조건 10 — "별개 seam" 확정만, 설계 아님 |
| **Gate (B)** (`ADC-0019` 재검토 조건 (c) — 다른 계보 또는 v2 프로덕션 관찰) 진전·충족 선언 | `ADC-0021` §8, `ADC-0023` §6 조건 6 — E1~E4 전부 LangGraph 계보. hard gate로 존속 |
| **Gate (C)** (Reversibility 필수 불변조건의 v2 완전 discharge) / `ADR-0010` "부분 충족" 재판정 | `ADR-0010`, `ADC-0023` §6 조건 5 — §16.6 "Reversibility — 필수 Architecture 불변조건" 문단과 "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)" 문단은 **문자 그대로 유지** |
| **Adapter Contract 부속 명세 (a)(b)(c)(d) bullet 문언 재정의** | `ADC-0023` §9.2, `ADR-0009`/`ADR-0010`/`ADR-0011` §Out of Scope — 인용만, verbatim 유지 |
| **(c)의 계약화 여부 / HQ State 설계 구속 강화** | `ADC-0020` §Q-D Defer, `ADR-0009` §3, `ADR-0011` §3 — `ADR-0011`이 반영한 (c) 배치 문장 그대로. 이 ADR은 (c)를 손대지 않는다 |
| **"실행 단위(Execution Unit)"의 §6 Concept Model 표 등재 / 새 Kernel Domain·Layer·Component·enum·타입 신설** | `ADC-0023` §9.2·§D-9c·§D-9d, `ADR-0011` §4 — §16.6 본문 서술에 한정. Kernel `WorkflowResult`/`Dispatch` 타입 미도입 |
| **LangGraph 최종 채택 / 어댑터 래핑 방식 / Checkpointer 백엔드 / Implementation Strategy 세부** | `ADC-0019` §Q8, `ADC-0021` §D2·§7 |
| **`hqs/development/IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19 전면·Scoped 해제** | `ADC-0021` §8, `ADC-0023` §6 조건 8 — `ADC-0015`류 부분 해제를 **하지 않는다** |
| **`docs/decisions/adc/ADC.md` ADC-02 / `ADC-0008` / §16.7 Workflow Kernel Module Defer 재판단** | `ADC-0019` §Q8, §16.6 "Workflow Module Defer(§16.7)와의 구분" 문단 |
| **`BASELINE.md` §1~§15·§16.1~§16.5·§16.7·§6 Concept Model 표·§14·§15.2, §16.6의 Reversibility 2문단·Adapter Contract (a)(b)(c)(d) bullet·"실행 단위(Execution Unit)"·"실행 단위 Lifecycle" 문단** | `ADR-0009`/`ADR-0010`/`ADR-0011` §Out of Scope 관행 — 참조만, 문자 그대로 유지 |
| **`BASELINE.md` H1 제목줄과 §17 Version 표의 불일치 정정** | `ADR-0008`~`ADR-0011` §Out of Scope와 동일 관행 — §17 표만 갱신 |
| **`ADC-0021`·`ADC-0022` 원문 편집** (§8 Gate (A) 라벨 자체) | 사용자 지시 — ADC/ADR 미수정. Gate (A)의 새 상태는 `BASELINE.md` §16.6의 cross-reference로만 반영한다 |
| **Production Code(`core/`, `hqs/`, `dashboard/`), `docs/research/`** | 전혀 수정하지 않는다 |
| **`RFC-0022` Status 전환 (Proposed → Accepted/Resolved)** | 프로젝트 RFC convention — RFC-0009~0022 전부 `Proposed` 유지. 이 ADR은 `ADC-0023`이 그 Boundary Question을 이미 판정했음만 인용한다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16.6에서 **(2.1)** "v2 공백의 현재 상태" 문단을 재작성하고, **(2.2)** A-IN 문단·**(2.3)** A-IN(a) 문단·**(2.4)** 명칭 문단·**(2.5)** Adapter Contract 도입부 문단의 각 **마지막에 1문장씩 부기**한다. §17 Version을 v1.15 → v1.16으로 갱신하고 변경 이력 한 줄을 추가한다. §16.6의 다른 문단(책임·근거·"실행 단위(Execution Unit)"·"실행 단위 Lifecycle"·§16.3~16.5 경계·Checkpoint 용어 구분·Reversibility 필수 불변조건·Reversibility v2 부분 충족(E4)·Workflow Module Defer 구분·Adapter Contract (a)(b)(c)(d) bullet·이 Accept가 결정하지 않는 것·Production 구현과의 관계)과 §1~§15·§16.1~§16.5·§16.7·§6 Concept Model 표·§14·§14.1 표·§7 목록·§15.2는 **문자 그대로 유지**한다 |
| `docs/00_governance/GLOSSARY.md` | "Kernel Modules — Workflow Adapter (Reference)" 절 **주석 블록(`>` 인용)의 두 문장**을 정정한다(결정 9 = `ADC-0023` Resolved). 표의 "Workflow Adapter"·"Adapter Contract"·"실행 단위 (Execution Unit)" 행, "Concept Model 용어" 절은 무변경 |

`hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
`docs/architecture/core/ADC-0008`, `docs/architecture/core/ADC-0010`,
`docs/architecture/core/ADC-0021`, `docs/architecture/core/ADC-0022`,
Kernel Public Contract(§14·§14.1), §7 목록, Production Code는 이 ADR로
건드리지 않는다(§Out of Scope·§4·§5).

### 2. `BASELINE.md` §16.6 갱신 내용

`ADC-0023` §5 D-9a~D-Gate-A와 §8 지침이 이미 정리한 것만 옮긴다. 새 판단을
만들지 않는다.

#### 2.1 "v2 공백의 현재 상태 (Conditional)" 문단 재작성 (D-9a·D-9b·D-9d·D-9f·D-Gate-A)

기존:

```markdown
**v2 공백의 현재 상태 (Conditional)**: v1 `ADR-0007` 결정 **2(Core 소유
Lifecycle 소비)·5(Team/Division 경계)·11(State Model)은 `ADC-0022`로
Resolved**다 — Team/Division 부재에서 비롯된 세 공백의 v2 재정의가
완료됐다(위 "실행 단위(Execution Unit)"·"실행 단위 Lifecycle"·"A-IN(a)
공유 State가 담는 정보" 문단, `ADC-0022` §D-2·§D-5·§D-11·§D-11c).
**결정 9(`IWorkflowEngine` Port / 결과 반환 타입 / 입력 시그니처)는
미해결로 남는다** — 공백 원인이 Team 부재가 아니라 §14.1이 "Task 전달
책임"·"Engine 호출 책임"을 계약 범위 밖으로 두는 것이므로, 이 책임보다
상위의 별도 Kernel Public Contract 확장 절차(별도 RFC → ADC → ADR)가
다룬다. **이 책임을 Kernel Public Contract(§14)로 승격하는 것은 결정 9
해소 이후에만 가능하다**(`ADC-0019` §Q7·§Decision 조건 5). Production
구현 착수는 결정 9 + `ADC-0019` 재검토 조건 (c)(다른 계보 또는 v2
프로덕션 관찰 — `ADC-0021` §8 Gate (B)) + Reversibility 필수 불변조건의
v2 완전 검증(위 "부분 충족(E4)" 문단, `ADC-0021` §8 Gate (C)) +
`hqs/development/IMPLEMENTATION_RULES.md`로 **계속 차단된다** — 결정
2·5·11의 해소는 이 중 어느 것도 해제하지 않는다. `ADC-0021` §8 Gate
(A)는 이 반영 이후 **"부분 해소(결정 2·5·11 Resolved / 결정 9 pending)"**로
읽힌다.
```

교체 후(문단 bold 라벨 포함 재작성 — 상태 갱신이지 새 Decision이 아님):

```markdown
**v2 공백의 현재 상태 (Conditional)**: v1 `ADR-0007` 결정 **2(Core 소유
Lifecycle 소비)·5(Team/Division 경계)·11(State Model)은 `ADC-0022`로,
9(`IWorkflowEngine` Port 존재 지위 / 입력 시그니처 / `WorkflowResult`
반환 타입)는 `ADC-0023`으로 Resolved**다 — Gate (A)의 네 공백이 모두
v2 위에서 재정의됐다(위 "실행 단위(Execution Unit)"·"실행 단위
Lifecycle"·"A-IN(a) 공유 State가 담는 정보" 문단, `ADC-0022`
§D-2·§D-5·§D-11·§D-11c, `ADC-0023` §D-9a~§D-9f). 결정 9에 대해
**Kernel은 (i) 교체 가능 seam을 §16.6 Adapter Contract(비-§14)로 두고,
(ii) 실행 메커니즘 호출의 입력 시그니처를 규정하지 않으며, (iii) 결과
반환 타입을 정의하지 않는다**(caller-owned 최종 State 값 + HQ 도메인
타입) — 결정 9의 공백 원인은 Team 부재가 아니라 §14.1이 "Task 전달
책임"을 계약 범위 밖으로 두는 것이었고, `ADC-0023`은 그 잔여 계약 표면을
"Kernel이 §16.6 밖 별도 계약으로 규정하지 않는다"로 종결했다. **이
책임을 Kernel Public Contract(§14)로 승격하는 것은 여전히 별도 절차
— §14 scope의 Context→Execution 확장(별도 RFC → ADC → ADR) — 를
거쳐야 한다**(`ADC-0019` §Q7·§Decision 조건 5, `ADC-0023` §D-9a);
결정 9 해소는 그 승격의 선행조건 하나를 충족한 것이다. Production 구현
착수는 `ADC-0019` 재검토 조건 (c)(다른 계보 또는 v2 프로덕션 관찰 —
`ADC-0021` §8 Gate (B)) + Reversibility 필수 불변조건의 v2 완전
검증(위 "부분 충족(E4)" 문단, `ADC-0021` §8 Gate (C)) +
`hqs/development/IMPLEMENTATION_RULES.md`로 **계속 차단된다** — 결정
2·5·9·11의 해소는 이 중 어느 것도 해제하지 않는다. `ADC-0021` §8 Gate
(A)는 이 반영 이후 **"해소(결정 2·5·9·11 전부 Resolved)"**로 읽히며,
그것이 여는 것은 `ADC-0021` §8 진입 순서의 "(A)" 항목뿐이다.
```

#### 2.2 A-IN 문단에 D-9c 문장 부기

기존(마지막 문장):

```markdown
... 입력의 **구체 시그니처**(v1 `ADR-0007` 결정
9 `IWorkflowEngine.run(team, dispatch)`의 v2 대응)는 이 Accept가 정하지
않는다 — §14.1 "Task 전달 책임" 트랙에 남는다.
```

교체 후(마지막 문장 뒤에 1문장 부기, 기존 문장은 문자 그대로 유지):

```markdown
... 입력의 **구체 시그니처**(v1 `ADR-0007` 결정
9 `IWorkflowEngine.run(team, dispatch)`의 v2 대응)는 이 Accept가 정하지
않는다 — §14.1 "Task 전달 책임" 트랙에 남는다. `ADC-0023` §D-9c는 이
입력 시그니처를 **Kernel이 규정하지 않는다**로 종결했다 — 실행 단위
절반 = 불투명 HQ 입력(`ADC-0022` §D-5), 나머지 = HQ별 진입
시그니처(`run_mvp_0001(code)`, `team.run(...)`). "Task 전달 책임"을
Kernel 책임으로 승격할지 여부는 그와 별개로 §14.1 #1에 남는다.
```

#### 2.3 A-IN(a) 문단에 D-9d 문장 부기

기존(마지막 문장):

```markdown
... 실행
결과를 호출자에게 돌려주는 반환 타입(`WorkflowResult` 대응)은 이 Accept
밖이며 §14.1 "Task 전달 책임" 트랙에 남는다.
```

교체 후(마지막 문장 뒤에 1문장 부기, 기존 문장은 문자 그대로 유지):

```markdown
... 실행
결과를 호출자에게 돌려주는 반환 타입(`WorkflowResult` 대응)은 이 Accept
밖이며 §14.1 "Task 전달 책임" 트랙에 남는다. `ADC-0023` §D-9d는 이 반환
타입을 **Kernel이 정의하지 않는다**로 종결했다 — 어댑터 경계 산출물 =
caller-owned 최종 State 값(Adapter Contract (a)(b), §14.3 G-6), 그
값에서 HQ가 도출하는 종료 disposition·요약의 타입 = HQ 도메인
(`hqs/development` `VerificationResult` 등 HQ-level Public Contract).
Kernel-typed envelope(`WorkflowResult` 대응)는 도입하지 않는다(`ADC-0022`
§D-11 계승).
```

#### 2.4 명칭 문단에 D-9b·D-9e 문장 부기

기존(마지막 문장):

```markdown
... §6 Concept Model의 "Runtime"·"Adapter" 항목은
이 명칭 반영으로 변경되지 않으며, `docs/decisions/adc/ADC.md`
ADC-02(Runtime 존폐, Open)도 그대로다.
```

교체 후(마지막 문장 뒤에 1문장 부기, 기존 문장은 문자 그대로 유지):

```markdown
... §6 Concept Model의 "Runtime"·"Adapter" 항목은
이 명칭 반영으로 변경되지 않으며, `docs/decisions/adc/ADC.md`
ADC-02(Runtime 존폐, Open)도 그대로다. v1 `IWorkflowEngine`의
"Engine"(Workflow 그래프 실행 조립·진행)과 §16.2 Engine Adapter /
§14.1 #3 "Engine 호출 책임" / §11 "Engine Gateway"(Model/LLM Provider
호출)는 **별개 seam**이며, `ADC-0023` §D-9b는 결정 9를 이 구분 위에서
§14.1 #1 "Task 전달 책임" 트랙 하나로 판정했다(#3 및 `ADC-0010`
Engine Caller 위치 Not Accepted와 무관). §7 "Engine 호출의 표준
인터페이스 제공 (Port/Adapter)"(책임 소재 선언)와 §14.1 "Engine 호출
책임 = 계약 범위 밖"(Public Guarantee 결정 여부)은 층위 차이이지
모순이 아니다(`ADC-0023` §D-9e).
```

#### 2.5 Adapter Contract 도입부 문단에 D-9a 문장 부기

기존(마지막 문장):

```markdown
... 이 명세에는 "Port" / "Public" /
"Guarantee" / "Interface" 어휘를 쓰지 않으며, §14에는 어떤 항목도
추가되지 않는다.
```

교체 후(마지막 문장 뒤에 1문장 부기, 기존 문장은 문자 그대로 유지):

```markdown
... 이 명세에는 "Port" / "Public" /
"Guarantee" / "Interface" 어휘를 쓰지 않으며, §14에는 어떤 항목도
추가되지 않는다. `ADC-0023` §D-9a는 이 부속 명세가 규정하는 교체 가능
seam의 §14 지위를 **비-§14**로 확정했다 — §14 Extension Point 승격은
§14 scope의 Context→Execution 확장이라는 별도 ADR의 몫이며, 결정 9
해소는 §14 항목을 추가하지 않는다.
```

### 3. `BASELINE.md` §16.6에서 손대지 않는 문단 (명시)

아래는 인용은 되나 **문자 그대로 유지**된다 — `ADR-0009` §6·`ADR-0010`
§4·`ADR-0011` §2 관행.

- "책임" 문단, "근거" 문단, "A-OUT (이 Accept가 다루지 않는 것)" 문단
- "실행 단위(Execution Unit) — §16.6 A-IN 입력 경계 설명 용어" 문단 (`ADR-0011`이 신설)
- "실행 단위 Lifecycle — Adapter가 소비할 Kernel 소유 전이는 없다" 문단 (`ADR-0011`이 신설)
- "§16.3~16.5와의 경계" 문단, "Checkpoint 용어 구분" 문단
- "Reversibility — 필수 Architecture 불변조건" 문단 **(verbatim)**
- "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4, `ADC-0021` §8 Gate (C))" 문단 **(verbatim)**
- "Workflow Module Defer(§16.7)와의 구분" 문단
- Adapter Contract (a)·(b)·(d) bullet과 병렬 (c) 문단 **(verbatim — `ADR-0011`이 부기한 (c) 배치 문장 포함)**
- "이 Accept가 결정하지 않는 것" 문단
- "Production 구현과의 관계" 문단 — **참조번호 정정 불필요**: `ADR-0011` §2.7이 이미 "v1 `ADR-0007` 결정 9 공백 해소(결정 2·5·11은 `ADC-0022`로 해소됨)와 `ADC-0021` §8 Gate (B)·(C) 충족 및 Reversibility의 v2 완전 검증 이후"로 정정했고, 결정 9가 Resolved된 지금 그 문장은 "결정 9 공백 해소" 조건이 이미 충족됐다는 의미로 자연스럽게 읽힌다. 남은 차단 조건(Gate (B)·(C) + Reversibility v2 완전 검증)이 그대로이므로 문장의 실질은 불변 — 재편집하지 않는다(최소 반영, `ADR-0011` §2.7 주석과 동일 논리)

> **§2.5의 Adapter Contract 부기와 §3의 "Adapter Contract bullet verbatim"은 모순이 아니다** — §2.5는 (a)·(b)·(d) bullet **위의 도입부 문단** 마지막에 1문장을 부기하며, bullet 자체와 (c) 문단은 손대지 않는다.

### 4. `BASELINE.md` §6 Concept Model 표 / §14·§14.1 / §7 목록 갱신 여부

**추가·수정하지 않는다.**

- **§6**: `ADR-0009` §Decision 4 판단이 "실행 단위"·"Workflow Adapter"에 이어 결정 9의 어떤 서술에도 그대로 적용된다 — §16 Kernel Module 내부 서술은 §6에 등재하지 않는다. `ADR-0011` §4를 계승한다.
- **§14·§14.1**: `ADC-0023` §D-9a·§6 조건 7 — §14 항목 0건 추가, §14.1 표의 "1. Task 전달 책임"·"3. Engine 호출 책임" = "미결, 계약 범위 밖" 행 무변경. 결정 9의 "Kernel은 규정하지 않는다"는 §16.6 본문에만 서술된다.
- **§7 System Boundary 목록**: `ADC-0023` §D-9e (4) — §7은 "책임 소재" 선언이고, §7 ↔ §14.1 층위 해석은 §16.6 명칭 문단 부기(§2.4)로만 반영한다. §7 원문 무편집.

### 5. `hqs/development/IMPLEMENTATION_RULES.md` 갱신 여부

**갱신하지 않는다.** `ADR-0009` §6·`ADR-0010` §4·`ADR-0011` §6과 동일 판단.

- `ADC-0019` §Decision 조건 5의 "구현 착수 불가"는 결정 9 해소로 **§14
  승격 선행조건 하나**만 충족되며, Gate (B)·Gate (C)·§14 scope 확장이
  미해소 hard gate로 남는다.
- `IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19(Workflow Parser /
  Scheduler·우선순위·Workflow orchestration·Dynamic Routing·§6 넓은
  Runtime / Stage 재진입·조건부 Stage / Engine Gateway Port/Adapter /
  Engine Routing / Event Bus 구현 금지)는 전면 **유지**된다.

### 6. `docs/00_governance/GLOSSARY.md` 갱신 내용

"Kernel Modules — Workflow Adapter (Reference)" 절 **주석 블록(`>` 인용)만**
변경한다. 표의 세 행("Workflow Adapter"·"Adapter Contract"·"실행 단위
(Execution Unit)")과 "Concept Model 용어" 절은 무변경.

#### 6.1 주석 블록 정정 ①

기존:

```markdown
> ... 구현체 선택·구현 전략·Public Port·§14 승격은 미확정이며, v1
> `ADR-0007` 결정 9(및 `ADC-0021` §8 Gate (B)·(C))가 미해결인 동안 §14
> 승격·Production 구현 착수는 불가하다 — v1 `ADR-0007` 결정 2·5·11은
> `ADC-0022`로 해소됐다.
```

정정 후:

```markdown
> ... 구현체 선택·구현 전략·Public Port·§14 승격은 미확정이며, v1
> `ADR-0007` 결정 9는 `ADC-0023`으로 해소됐고(Kernel은 seam 지위·입력
> 시그니처·결과 반환 타입을 §16.6 밖 별도 계약으로 규정하지 않는다),
> `ADC-0021` §8 Gate (B)·(C)가 미해결인 동안 §14 승격·Production 구현
> 착수는 불가하다 — v1 `ADR-0007` 결정 2·5·11은 `ADC-0022`로 해소됐고,
> §14 승격은 §14 scope의 Context→Execution 확장 이후다.
```

#### 6.2 주석 블록 정정 ②

기존(`ADR-0010`이 덧붙이고 `ADR-0011`이 번호 정정한 문장):

```markdown
> ... `ADC-0019` 재검토 조건 (c)와 v1
> `ADR-0007` 결정 9는 그대로 미충족이다(결정 2·5·11은 `ADC-0022`로
> 해소; `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md`).
```

정정 후(Gate (C) "부분 충족" 문구·상태는 불변, 결정 9 해소 사실만 반영):

```markdown
> ... `ADC-0019` 재검토 조건 (c)는 그대로 미충족이다(v1 `ADR-0007`
> 결정 9는 `ADC-0023`으로, 결정 2·5·11은 `ADC-0022`로 해소;
> `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md`).
```

### 7. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version(§17) | v1.15 | **v1.16** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: 이번 변경은 `RFC-0022` → `ADC-0023` → 이 ADR
절차를 그대로 거쳤다. `ADR-0001`~`ADR-0011`의 선례와 동일하다.

**Minor 증가(v1.16) 근거**: 신설 절·문단이 없다. §16.6 문단 1개
재작성(상태 갱신) + 문단 4곳에 1문장씩 부기 + §17 갱신 + `GLOSSARY.md`
주석 2문장 정정뿐이다(§16.1~§16.5·§16.7·§6·§14·§14.1·§7·§15.2 무변경,
`IMPLEMENTATION_RULES.md` 무변경). 선행 `ADR-0009`(v1.13)·`ADR-0010`
(v1.14)·`ADR-0011`(v1.15)과 같은 granularity로 Minor 단위로 기록한다.
`ADC-0023` §8-8이 예상한 폭(v1.16, Minor)과 일치한다.

### 8. Migration Strategy

> 아래 1~2는 Architecture/Governance Review PASS + 사용자 승인
> (2026-09-04) 이후 **실행되었다**(Status: Accepted). 3은 무변경 확인,
> 4는 검증 절차이며 실행됐다. 5(커밋·PR)는 그 이후 feature branch
> `claude/adr-0012-decision-9-baseline-v1.16`에서 진행한다 — `main`
> 직접 commit/Merge는 하지 않는다(`ADR-0011`이 거친 절차와 동일).

1. `docs/architecture/baseline/BASELINE.md`:
   - §16.6 "v2 공백의 현재 상태" 문단을 §2.1대로 교체한다.
   - §16.6 A-IN 문단 마지막에 §2.2 문장을 부기한다.
   - §16.6 A-IN(a) 문단 마지막에 §2.3 문장을 부기한다.
   - §16.6 명칭 문단 마지막에 §2.4 문장을 부기한다.
   - §16.6 Adapter Contract **도입부 문단** 마지막에 §2.5 문장을
     부기한다(bullet (a)(b)(c)(d)는 무변경).
   - §3에 열거한 §16.6의 다른 모든 문단, §1~§15·§16.1~§16.5·§16.7·§6·
     §14·§14.1·§7·§15.2는 문자 그대로 유지한다.
   - §17 Version을 v1.15 → v1.16으로 바꾸고 변경 이력 맨 위에 다음 한
     줄을 추가한다:

     > `| v1.16 | §16.6에 Gate (A) 결정 9 Resolution 반영(`ADC-0022` → `ADR-0011`이 결정 2·5·11, `ADC-0023` → 이 ADR이 결정 9). D-9b: v1 `IWorkflowEngine`의 "Engine"(Workflow 그래프 실행)과 §16.2 Engine Adapter / §14.1 #3 "Engine 호출 책임"(Model/LLM 호출)은 별개 seam — 결정 9는 §14.1 #1 "Task 전달 책임" 트랙 하나. D-9a: 교체 가능 seam의 §14 지위 = 비-§14(§16.6 Adapter Contract) — §14 승격은 §14 scope의 Context→Execution 확장 별도 절차, 이 반영은 §14 항목 무추가. D-9c: 입력 시그니처 = Kernel 미규정(실행 단위 절반 = 불투명 HQ 입력, 나머지 = HQ별 진입 시그니처). D-9d: 결과 반환 타입 = Kernel 미정의(caller-owned 최종 State 값 + HQ 도메인 타입, `WorkflowResult` 대응 미도입). D-9e: §7 "표준 인터페이스 제공"(책임 소재) ↔ §14.1 "계약 범위 밖"(Public Guarantee 결정 여부)은 층위 차이 — `ADC-0010` 유지. **Gate (A) = "해소"(결정 2·5·9·11 전부 Resolved)** — 여는 것은 `ADC-0021` §8 진입 순서 "(A)" 항목뿐. Gate (B)(재검토 조건 (c))·Gate (C)(Reversibility 완전 검증)·§14 승격·`IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19·Production 구현 차단 유지. §5·§6·§7·§11·§14·§14.1 표·§16.1~§16.5·§16.7·§6 Concept Model 표·§16.2·§16.6 Reversibility 2문단·Adapter Contract (a)(b)(c)(d) bullet·"실행 단위"·"실행 단위 Lifecycle" 문단 무변경. `GLOSSARY.md` "Workflow Adapter (Reference)" 절 주석 2문장 정정. 근거: `docs/architecture/core/ADR-0012-gate-a-decision-9-contract-surface-resolution-baseline.md` |`

2. `docs/00_governance/GLOSSARY.md` — §6.1·§6.2의 주석 블록 두 문장을
   정정한다. 표의 세 행·"Concept Model 용어" 절은 무변경.

3. `hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
   `docs/architecture/core/ADC-0008`, `docs/architecture/core/ADC-0010`,
   `docs/architecture/core/ADC-0021`, `docs/architecture/core/ADC-0022`,
   `core/`·`hqs/`·`dashboard/`·`docs/research/` — 변경하지 않는다.

4. 검증:
   - `BASELINE.md` 최상위 절 번호가 §1~§17로 유지되는지(신설 절 없음,
     §16.6 번호 유지).
   - §16.6에서 §2.1 재작성 문단 + §2.2~§2.5 부기 4문장 외의 모든 문단,
     그리고 §16.1~§16.5·§16.7·§6·§14·§14.1·§7·§15.2가 문자 그대로인지
     (`git diff`가 `BASELINE.md` §16.6·§17 + `GLOSSARY.md` 주석 2문장 +
     이 ADR 파일에만 국한).
   - §16.6 "Reversibility — 필수 Architecture 불변조건" 문단, "Reversibility
     v2 통합 테스트 재현 — 부분 충족 (E4)" 문단, "실행 단위(Execution
     Unit)" 문단, "실행 단위 Lifecycle" 문단이 verbatim.
   - Adapter Contract (a)(b)(c)(d) bullet과 병렬 (c) 문단이 verbatim
     (§2.5 부기는 **도입부 문단** 마지막에만).
   - 부기·재작성 문단에 "Port" / "Public" / "Guarantee" / "Interface"
     어휘가 (인용 문맥 "Port 존재 지위"·"Public Guarantee" 외에) 새
     계약 항목으로 쓰이지 않고, §14·§14.1 표에 추가된 항목·행이 없는지.
   - §2.1 재작성 문단에 결정 9의 §14.1 #1 원인 서술, "§14 승격은 §14
     scope 확장 별도 절차", Gate (B)·(C) "계속 차단", "Gate (A) = 해소"가
     명문으로 있는지.
   - 새 Kernel enum·타입(`WorkflowResult`/`Dispatch` 등)이 도입되지
     않았는지 — §2.3·§2.1 (iii)는 "정의하지 않는다"의 부정형.
   - `GLOSSARY.md`의 "Workflow Adapter"·"Adapter Contract"·"실행 단위
     (Execution Unit)" 표 행, "Concept Model 용어" 절이 문자 그대로인지.
   - `IMPLEMENTATION_RULES.md`·`ADC-0021`·`ADC-0022`·`ADC-0010`이
     `git diff` 0줄인지.
   - `git status`로 `core/`·`hqs/`·`dashboard/`·`docs/decisions/`가
     무변경인지.

5. 커밋 — 이 ADR과 위 `BASELINE.md`·`GLOSSARY.md` 변경을 함께, `main`이
   아닌 `claude/*` feature branch에 커밋하고 PR을 생성한다(승인 이후,
   `main` 직접 커밋·Merge 금지).

---

## Consequences

- `docs/architecture/baseline/BASELINE.md`가 v1.15 → v1.16이 되고, §16.6
  "v2 공백의 현재 상태" 문단이 **결정 9까지 Resolved**로 갱신된다 —
  Gate (A)의 네 공백(2·5·9·11)이 모두 v2 위에서 재정의된 상태가 §16.6
  본문에 기록된다.
- **결정 9는 Resolved**로 기록된다: (a) 교체 가능 seam의 §14 지위 =
  비-§14(§16.6 Adapter Contract), (b) 입력 시그니처 = Kernel 미규정
  (HQ별 진입 시그니처), (c) 결과 반환 타입 = Kernel 미정의(caller-owned
  최종 State 값 + HQ 도메인 타입). v1 "Engine"(Workflow 실행)과 §16.2
  Engine Adapter(Model/LLM 호출)가 별개 seam임이 명칭 문단에 부기되고,
  §7 ↔ §14.1 층위 차이가 함께 서술된다.
- **§14 Kernel Public Contract는 무변경** — 항목 0건 추가. §14.1 표의
  "1. Task 전달 책임"·"3. Engine 호출 책임" = "미결" 행 그대로. §14
  승격은 §14 scope의 Context→Execution 확장이라는 상위 별도 절차로 남고,
  결정 9 해소는 그 선행조건 하나만 충족한다.
- **§7 System Boundary 목록·§11 표는 무변경** — D-9e는 §16.6 명칭 문단
  부기(§2.4)로만 반영된다.
- `ADC-0021` §8 **Gate (A)의 상태가 "해소(결정 2·5·9·11 전부 Resolved)"로
  읽힌다** — `ADC-0021` 원문은 수정되지 않으며, BASELINE §16.6의
  cross-reference가 그 상태를 반영한다. Gate (A) 해소가 여는 것은
  `ADC-0021` §8 진입 순서의 "(A)" 항목뿐이다.
- **Gate (B)·Gate (C)·LangGraph 채택·Production 구현·`IMPLEMENTATION_RULES.md`
  Scoped 해제는 전혀 진전되지 않는다** — §16.6 "v2 공백의 현재 상태"
  재작성 문단이 이들을 hard gate로 "계속 차단"으로 명문화하고, Reversibility
  2문단·"부분 충족 (E4)" 문단은 verbatim 유지된다.
- `docs/00_governance/GLOSSARY.md` "Workflow Adapter (Reference)" 절
  주석의 두 문장이 결정 9 = `ADC-0023` Resolved로 정정된다. 표의 세
  행("Workflow Adapter"·"Adapter Contract"·"실행 단위 (Execution Unit)"),
  "Concept Model 용어" 절은 무변경.
- `hqs/development/IMPLEMENTATION_RULES.md`는 **무변경**이다 — line
  9/13/14/15/16/19 전면 유지.
- Kernel Public Contract(§14), §16.6 "실행 단위(Execution Unit)"·"실행
  단위 Lifecycle" 문단(`ADR-0011` 신설), Adapter Contract (a)(b)(c)(d)
  bullet은 **문자 그대로 유지**된다.
- Rule B는 여전히 미충족이다(`ADC-0019` §Q2, 재검토 조건 (c) = Gate
  (B)). 이 반영은 §14 승격·Implementation Strategy·`IMPLEMENTATION_RULES.md`
  Scoped 해제의 hard gate를 약화하지 않는다.
- 이 ADR은 **Accepted** 상태다 — Architecture/Governance Review PASS +
  사용자 승인(2026-09-04) 이후 §Migration Strategy 1~4를 실행했다:
  `BASELINE.md` v1.16(§16.6 문단 1개 재작성·4곳 1문장 부기 + §17),
  `GLOSSARY.md` "Workflow Adapter (Reference)" 절 주석 2문장 정정.
  §14·§14.1·§7·§16.2·Reversibility 2문단·Adapter Contract bullet·
  `IMPLEMENTATION_RULES.md`는 무변경. commit·PR은 feature branch에서
  별도 진행(`main` 직접 금지).

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **있음(제한적 — 기존 경계의 상태 확정)** —
  §16.6이 가리키는 책임의 범위(A-IN/A-OUT)는 전혀 바뀌지 않는다. "결정
  9의 잔여 계약 표면(Port 존재 지위·입력 시그니처·결과 반환 타입)에
  대해 Kernel이 §16.6 밖 별도 계약을 두지 않는다"는 상태가 §16.6
  본문에 서술되고, Gate (A)가 "해소"로 읽힌다. Component 설계(§10 Out
  of Scope)에는 영향이 없다 — Interface·구현 전략·Public Port는 여전히
  미정이고, §14 승격은 별도 상위 절차로 남는다.
- **Contract Impact**: **없음** — 공개 Interface·Public Port·Guarantee·
  Kernel enum·타입을 정의하지 않았다. Kernel Public Contract(§14)·§14.1
  표는 무변경. Adapter Contract 부속 명세 (a)(b)(c)(d) bullet은 verbatim
  유지되고, §2.5 부기는 도입부 문단에만 들어가며 "비-§14" 상태를 재확인할
  뿐 새 계약이 아니다. §14.1 "Task 전달 책임" 미결 상태가 이 책임의 §14
  승격을 계속 막는다.
- **Kernel Impact**: **없음(경계·상태 기록)** — 새 Kernel Concept·Layer·
  Component·enum·타입이 추가되지 않는다. Kernel이 아는 생명주기는 여전히
  HQ Lifecycle뿐이다(§6). v1 `IWorkflowEngine`의 "Engine"과 §16.2 Engine
  Adapter가 별개 seam임을 서술하되 §16.2 seam을 설계하지 않는다.

## Governance Chain 검증

`RFC-0022`(Proposed — F-9a~F-9f Boundary Question 개설, 판단은 `ADC-0023`에
위임) → `ADC-0023`(Decided — Architecture/Governance Review PASS §9;
D-9b seam 구분, D-9a 비-§14, D-9c/D-9d Kernel 미규정/미정의, D-9e 층위,
D-9f "해소" 최소 조건, D-Gate-A Gate (A) 해소) → 이 ADR(Accepted —
`ADC-0023` §8 지침 중 D-9a~D-Gate-A를 `BASELINE.md` §16.6·§17·
`GLOSSARY.md`에 반영, 새 결정 없음).

- `RFC-0022`는 Boundary Question만 열고 `ADC-0023`에 위임했다 — 위반 없음.
  프로젝트 RFC convention대로 `Proposed` 유지(RFC-0009~0022 전부 동일).
- `ADC-0023`은 `RFC-0022` §4 "가능한 갈래"를 자동 채택하지 않고 §5
  D-9a~D-9f로 독립 판정했으며(F-9b 우선), §14 승격·§14.1 #1·#3 Kernel
  귀속·§16.2 seam 설계·Gate (B)·(C)·LangGraph·구현·`IMPLEMENTATION_RULES.md`
  해제를 범위 밖으로 명시했다(`ADC-0023` §1.2·§7) — 위반 없음.
- 이 ADR은 `ADC-0023` §5 Decision과 §8 지침만 Baseline 문서 변경으로
  옮겼을 뿐, `ADC-0023`이 Out of Scope로 둔 것(§14 승격·§14 scope 확장,
  §14.1 표 편집, §7 목록 편집, §16.2 seam 설계, Gate (B)·(C), Adapter
  Contract bullet 재정의, LangGraph 채택, `IMPLEMENTATION_RULES.md`
  해제, §6 표 등재)을 새로 결정하지 않았다(§Out of Scope·§3·§4·§5) —
  위반 없음.
- `ADC-0019` §Decision 조건 1~6, Rule B 미충족(재검토 조건 (c) = Gate
  (B)), `ADC-0020` §6 Conditions 1~8, `ADC-0021` §D1~D4·§6~§8, `ADC-0022`
  §D-0~§D-11c, `ADR-0010` "부분 충족", `ADR-0011` 반영분(BASELINE v1.15)이
  §Out of Scope·§Consequences에 그대로 재확인됨을 확인했다 — `ADC-0023`
  §6 Conditions와 일치.
- §16.6에 재작성·부기되는 문단이 §16.3~16.5·§14·§14.1·§7의 문장을
  인용은 하되 수정·재정의하지 않음을 §2·§3·§4가 명시하고 §8 검증
  절차가 확인하도록 했다 — 충돌 없음.
- `ADR-0011` §2.7이 정정한 "Production 구현과의 관계" 문단은 결정 9가
  Resolved된 지금도 실질(Gate (B)·(C) + Reversibility v2 완전 검증
  차단)이 불변이므로 재편집하지 않는다(§3) — `ADR-0011` §2.7 주석의
  "새 Architecture Decision이 아니다" 논리와 동일.

## Self Review

- `ADC-0023`이 결정하지 않은 것을 반영했는가 — **아니오**. §Out of Scope에
  명시한 항목(§14 승격 / §14 scope 확장 / §14.1 표 편집 / §7 목록 편집 /
  §16.2 Engine Adapter seam 설계 / `ADC-0010` 재판단 / Gate (B) / Gate
  (C) / Adapter Contract bullet 재정의 / (c) 계약화 / LangGraph 채택 /
  `IMPLEMENTATION_RULES.md` 해제 / §6 표 등재 / H1 제목줄 / `ADC-0021`·
  `ADC-0022` 원문)은 손대지 않았다.
- 결정 9의 Resolution만 공식화했는가 — **예**(§2.1~§2.5, §Decision).
  결정 2·5·11은 `ADR-0011`이 이미 반영했고, 이 ADR은 §2.1에서 "네 공백
  모두 Resolved"로 상태만 갱신한다.
- D-9b(v1 "Engine" ≠ §16.2 Engine Adapter seam)를 정확히 반영했는가 —
  **예**(§2.4) — "별개 seam", "결정 9는 §14.1 #1 트랙 하나", "#3 및
  `ADC-0010`과 무관" 명문화.
- D-9a(비-§14 seam)를 §14 항목 추가 없이 반영했는가 — **예**(§2.5·§2.1
  (i)) — "§14 지위 = 비-§14", "§14 Extension Point 승격은 §14 scope
  확장 별도 ADR의 몫", "결정 9 해소는 §14 항목을 추가하지 않는다". §14·
  §14.1 표 무변경(§4).
- D-9c/D-9d(Kernel 입력·반환 타입 미규정)를 새 타입 도입 없이 반영했는가 —
  **예**(§2.2·§2.3) — "Kernel이 규정하지 않는다 / 정의하지 않는다"의
  부정형, `WorkflowResult`/`Dispatch` 대응 Kernel 타입 미도입, HQ별
  시그니처·HQ 도메인 타입 서술.
- D-9e(§7 ↔ §14.1 층위)를 §7·§14.1 원문 편집 없이 반영했는가 —
  **예**(§2.4·§4) — §16.6 명칭 문단에 "책임 소재 ↔ Public Guarantee
  결정 여부는 층위 차이" 1문장만 부기. §7 목록·§14.1 표 무편집.
- Gate (A) 상태를 정확히 반영했는가 — **예**(§2.1) — "해소(결정 2·5·9·11
  전부 Resolved)", "여는 것은 `ADC-0021` §8 (A) 항목뿐", §14 승격은
  §14 scope 확장 이후, Gate (B)·(C) "계속 차단" 명문.
- 결정 9 해소가 §14 승격·Gate (B)·Gate (C)·LangGraph·Production 구현·
  `IMPLEMENTATION_RULES.md` 해제 중 무엇이든 여는 것으로 서술했는가 —
  **아니오**(§2.1·§Consequences·§Out of Scope) — 전부 hard gate로 "계속
  차단" 유지, Reversibility 2문단·"부분 충족 (E4)" 문단 verbatim.
- §14 / Public Port / Guarantee를 신설·우회했는가 — **아니오**(§2·§4·§8
  검증) — §14 항목 추가 없음, 부기 문장은 "비-§14" 상태 재확인.
- `BASELINE.md` §16.1~§16.5·§16.7·§6 Concept Model 표·§14·§14.1·§7·
  §15.2, §16.6의 Reversibility 2문단·Adapter Contract (a)(b)(c)(d)
  bullet·"실행 단위"·"실행 단위 Lifecycle" 문단을 수정했는가 —
  **아니오**(§3·§4·§8 검증 절차).
- `hqs/development/IMPLEMENTATION_RULES.md`·`docs/decisions/adc/ADC.md`·
  `ADC-0008`·`ADC-0010`·`ADC-0021`·`ADC-0022`를 변경했는가 —
  **아니오**(§1·§5·§8).
- Rule B 충족을 선언했는가 — **아니오**(§Consequences) — 미충족·재검토
  조건 (c)(Gate (B)) 유지.
- 새 최상위·하위 절을 신설했는가 — **아니오**(§7) — §16.6 내부 문단
  재작성/부기만, §16.6 번호 유지.
- `BASELINE.md` / `GLOSSARY.md`를 실제로 수정했는가 — **예(승인 반영)** —
  Review PASS + 사용자 승인(2026-09-04) 이후 §Migration Strategy 1~4를
  실행했다: `BASELINE.md` §16.6 "v2 공백의 현재 상태" 문단 재작성 +
  A-IN·A-IN(a)·명칭·Adapter Contract 도입부 4곳 1문장 부기 + §17 v1.16,
  `GLOSSARY.md` 주석 2문장 정정. §14·§14.1·§7·§16.2·Reversibility
  2문단·Adapter Contract (a)(b)(c)(d) bullet·"실행 단위"·"실행 단위
  Lifecycle" 문단·§16.1~§16.5·§16.7·§6·§15.2·`IMPLEMENTATION_RULES.md`·
  `ADC-0021`·`ADC-0022`는 무변경.
- Adapter Contract 도입부 문단의 stale cross-reference("미해결 상태로
  유지되는 v2 공백" → "v2 공백의 현재 상태" — `ADR-0011` §2.6이 문단
  라벨을 바꿨으나 이 참조는 갱신하지 않았음)를 정정했는가 — **예**,
  §2.5 부기 문장이 붙는 같은 문장의 참조 정합화이며 새 Decision이
  아니다(`ADR-0011` §2.7 주석 논리와 동일).
- Production Code를 변경했는가 — **아니오**.
- 반영 과정에서 `ADC-0023`이 이미 인지한 것 이상의 새 Architecture 결정
  지점이 나타났는가 — **아니오**. "Production 구현과의 관계" 문단
  재편집 불필요 판단(§3)·Adapter Contract stale 참조 정정은 반영
  granularity·참조 정합화이지 새 결정이 아니다.
- Commit/PR/Merge를 했는가 — feature branch
  `claude/adr-0012-decision-9-baseline-v1.16`에 commit + PR을
  진행한다(사용자 지시). `main` 직접 commit/Merge는 하지 않는다.
