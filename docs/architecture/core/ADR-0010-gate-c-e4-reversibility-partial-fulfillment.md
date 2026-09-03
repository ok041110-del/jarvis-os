# ADR-0010: Gate (C) E4 Evidence 반영 — §16.6 Reversibility 통합 테스트 재현 상태를 "부분 충족"으로 Baseline 기록

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0010` (`docs/decisions/adr/`에는 동명 문서 없음 — 네임스페이스로 구분) |
| 제목 | `ADC-0021` §8 Gate **(C)**가 예고한 후속 ADR. E4(Experimental Evidence)를 근거로 `BASELINE.md` §16.6 "Reversibility — 필수 Architecture 불변조건"의 v2 통합 테스트 재현 이행 상태를 **부분 충족**으로 §16.6·GLOSSARY에 기록하고 잔여 한계를 명시 |
| 상태 | **Accepted** — Architecture/Governance Review PASS(§Review) 이후, §Decision·§Migration Strategy가 정의하는 `BASELINE.md` 변경(§16.6 "Reversibility" 문단 뒤에 "부분 충족(E4)" 문단 추가, §17 Version v1.13 → v1.14)과 `GLOSSARY.md` 변경("Workflow Adapter (Reference)" 절 주석 블록에 E4 한 문장 추가)이 반영되었다. `IMPLEMENTATION_RULES.md`·§14·§16.6 A-IN/A-OUT·Adapter Contract (a)(b)(c)(d) 문언·§16.1~§16.5·§16.7·§6·§15.2·`docs/decisions/adc/ADC.md`는 무변경. Commit/PR/Merge는 별도로 진행한다 |
| Context | `docs/architecture/core/ADC-0021-workflow-adapter-implementation-strategy.md` §8 — "(선택) Minor ADR … Gate (C) … 이후 후속 ADR이 조건 4 충족/부분 할인 판정"; `docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md` §4·§8; E4 `projects/workflow-adapter-reversibility-v2/EVIDENCE.md`(IN-1~IN-5, 22 테스트 PASS) |
| 관련 ADC | `docs/architecture/core/ADC-0021`(§8 Gate (C)) — 이 ADR의 지정자. `docs/architecture/core/ADC-0019` §Q6·§Decision 조건 4·§Next Step 4(재현 검증 요구), `docs/architecture/core/ADC-0020` §Q-D (d) |
| 선행 ADR | `docs/architecture/core/ADR-0009`(§16.6에 명칭·Adapter Contract 부속 명세만 반영, `IMPLEMENTATION_RULES.md` 무변경 — 이 ADR이 계승하는 층위), `docs/architecture/core/ADR-0008` §5(§17 표만 갱신, 제목줄은 범위 밖으로 남긴 관행), `docs/architecture/core/ADR-0004`(명칭만 Baseline·GLOSSARY 반영) |
| 선행 Decision(참고, 뒤집지 않음) | `ADC-0019` §Decision 조건 1~6·재검토 조건 (c), `ADC-0020` §6 Conditions 1~8, `ADC-0021` §D1~§D4·§6·§7·§8, v1 `ADR-0007` 결정 2/5/9/11 미해결 — 이 ADR은 어느 것도 변경하지 않는다 |

이 ADR은 새 Architecture나 Contract를 제안하지 않는다. `ADC-0021` §8이
예고한 대로 **E4의 결과를 §16.6 문언에 반영하는 구현 결정**만 기록한다 —
Reversibility 필수 불변조건의 **v2 통합 테스트 재현 요구**(이미 §16.6에
있음, `ADR-0008`/`ADR-0009`가 `ADC-0019` 조건 4로 등재)가 E4로 **부분
충족**됐음을, 잔여 한계와 함께 사실 기록한다. **완전 discharge를 선언하지
않는다.**

| 단계 | 다루는 것 |
|---|---|
| `ADC-0019` 조건 4 | Reversibility 불변조건의 v2 통합 테스트 재현 검증을 후속 구현의 **선행 요구**로 등재 |
| `ADC-0021` §8 Gate (C) | 그 재현 검증을 첫 Gate-clearing 단계로 지정, "이후 후속 ADR이 조건 4 충족/부분 할인 판정" |
| Test Design 0001 + E4 | `projects/workflow-adapter-reversibility-v2/` 통합 테스트 설계·구현·실행(IN-1~IN-5, 22 PASS) |
| **이 ADR** | E4를 근거로 §16.6에 "부분 충족(E4)" 문단 추가 + §17 v1.14 + GLOSSARY 한 문장. 새 결정 없음 |
| 후속 별도 절차 | 완전 discharge / 조건 4 Conditional 해제(잔여 한계 i~iii 해소 시), Gate (A) v1 결정 2/5/9/11, Gate (B) 재검토 조건 (c), Implementation Strategy 세부 ADC, `IMPLEMENTATION_RULES` Scoped 해제 |

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0021`이 반영을 지시하지 않은 것, 그리고 사용자 지시(2026-09-03)가
명시적으로 배제한 것은 **하나도 반영하지 않는다**.

| 항목 | 근거 |
|---|---|
| **조건 4의 완전 discharge 선언** | 사용자 지시 1 — "완전 discharge는 선언하지 마라". E4 §5, Test Design §8.3 — 잔여 한계 3건으로 부분 충족만 |
| **Gate (A) — v1 `ADR-0007` 결정 2/5/9/11(Core 소유 Lifecycle·Team/Division 경계·`IWorkflowEngine` Port·State Model) 해소** | 사용자 지시 3, `ADC-0019` 조건 5, `ADC-0021` §8 (A) — 미해소 hard gate 유지 |
| **Gate (B) — `ADC-0019` 재검토 조건 (c)(다른 계보 또는 v2 프로덕션 관찰) 충족** | 사용자 지시 3, E4 §4 한계 2 — E1·E2·E3·E4 전부 LangGraph 계보. 미충족 hard gate 유지 |
| **LangGraph 채택 / 어댑터 래핑 방식 / Checkpointer 백엔드** | 사용자 지시 4, `ADC-0019` §Q8, `ADC-0020` §7, `ADC-0021` §D2·§7 |
| **§14 Kernel Public Contract 승격 / Public Port·Surface·Guarantee·Interface 정의** | 사용자 지시 4, `ADC-0019` §Q7·조건 5, `ADC-0020` §Q-C, `ADC-0021` §6 조건 5 |
| **`IMPLEMENTATION_RULES.md` line 9/13/14/19 전면·Scoped 해제** | 사용자 지시 4, `ADC-0020` §6 조건 4, `ADR-0009` §6. `ADC-0015`류 부분 해제를 **하지 않는다** |
| **Production 구현 착수** (`core/`·`hqs/`·`dashboard/`) | 사용자 지시 4, `BASELINE.md` §16.6 "Production 구현과의 관계", `ADC-0019` 조건 5 |
| **§16.6 A-IN/A-OUT·Adapter Contract (a)(b)(c)(d) 문언 재정의** | `ADC-0021` §6 조건 2, `ADR-0009` §Out of Scope — 인용만, 문자 그대로 유지. (d) 문단도 verbatim 유지(§Decision 2.2) |
| **Checkpoint 입도 C1 / phase 경계 선언 주체(Q-E-2) 재론** | `ADC-0020` §Q-E-1·§Q-E-2, `ADC-0021` §6 조건 9 |
| **(c) 병렬 State 동시 쓰기 규약의 계약화·규범화** | `ADC-0020` §Q-D (c) Defer, `ADR-0009` §3 |
| **"Sequential = Reference Implementation" 지정의 §16.6/GLOSSARY 신설** | `ADC-0021` §8 권고(전략 기록만, 이연 가능). 이 ADR은 E4 반영만 |
| **E4 harness seam(`run_full`/`run_phase*`)을 구현체 계약 시그니처로 승격** | E4 §2·§4 한계 3, Test Design §3.1 — harness 로컬 관례이며 `ADC-0020` §Q-C 계약 아님 |
| **`BASELINE.md` §16.1~§16.5·§16.7·§6 Concept Model 표·§14·§15.2** | `ADR-0009` §Out of Scope와 동일 — 참조만 |
| **`BASELINE.md` H1 제목줄(현재 `v1.8` 표기)과 §17 불일치 정정** | `ADR-0008` §5·`ADR-0009` §Out of Scope와 동일 — §17 표만 갱신 |
| **`docs/decisions/adc/ADC.md` ADC-02 / `docs/architecture/core/ADC-0008` 재판단** | `ADC-0019` §Q8 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16.6 "Reversibility — 필수 Architecture 불변조건" 문단 **바로 뒤**에 "**Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)**" 문단을 신설한다(재배치·신설 절 없음, 같은 §16.6 내부 문단 추가). §17 Version을 v1.13 → v1.14로 갱신하고 변경 이력 한 줄을 추가한다 |
| `docs/00_governance/GLOSSARY.md` | "Kernel Modules — Workflow Adapter (Reference)" 절의 주석 블록(`>` 인용) 끝에 E4 관련 한 문장을 추가한다. 표(Workflow Adapter·Adapter Contract 행)와 "Concept Model 용어" 절은 무변경 |

`hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
`docs/architecture/core/ADC-0008`, Kernel Public Contract(§14), Production
Code는 이 ADR로 건드리지 않는다(§Out of Scope).

### 2. `BASELINE.md` §16.6 갱신 내용

#### 2.1 "부분 충족(E4)" 문단 신설

삽입 위치: "**Reversibility — 필수 Architecture 불변조건**" 문단 **뒤**,
"**미해결 상태로 유지되는 v2 공백 (Conditional)**" 문단 **앞**.

```markdown
**Reversibility v2 통합 테스트 재현 — 부분 충족 (E4, `ADC-0021` §8 Gate (C))**:
`projects/workflow-adapter-reversibility-v2/`의 in-repo 통합 테스트가
Sequential Reference 어댑터와 LangGraph 대조 어댑터로 도메인 형태
그래프(5-way 병렬 fan-out → 토론 Loop → 조건부 라우팅, 3 시나리오)에서
위 불변조건을 v2 맥락·저장소 안에서 재현했다 — 최종 State 동치, 실행
결과의 값 표현(예외 비전파), caller-owned 값 Checkpoint의 별도-프로세스
재개, 어댑터 교체 시 Kernel·HQ 파일 해시 불변, 구현체 고유 문법의 단일
모듈 격리를 IN-1~IN-5 22개 테스트 PASS로 확인했다(E4
`projects/workflow-adapter-reversibility-v2/EVIDENCE.md`,
`docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md`).
이는 **부분 충족**이며 `ADC-0019` §Decision 조건 4의 완전 discharge가
아니다. 잔여 한계: (i) 노드가 결정론적 stub — 실제 엔진 비결정성·부분
실패율 미검증, (ii) 대조 구현체가 여전히 LangGraph 단일 계보(E1·E2·E3·E4
전부 동일 계보), (iii) 실제 엔진 실행·프로덕션 트래픽 미검증. 이 재현은
`ADC-0019` 재검토 조건 (c)(다른 계보 또는 v2 프로덕션 관찰 — `ADC-0021`
§8 Gate (B))를 **충족하지 않으며**, v1 `ADR-0007` 결정 2/5/9/11 공백
(`ADC-0021` §8 Gate (A))도 해소하지 않는다. E4는
`docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation"의
Evidence이며, 그 존재만으로 Public Contract 승격·LangGraph 채택·
`IMPLEMENTATION_RULES.md` 해제·Production 구현 착수를 발생시키지 않는다.
완전 discharge 및 조건 4의 Conditional 해제는 위 잔여 한계 (i)~(iii)가
후속 절차로 메워질 때 별도로 판정된다.
```

#### 2.2 그 외 §16.6 문단 — 문자 그대로 유지

"책임"·"근거"·"A-IN"·"A-OUT"·"§16.3~16.5와의 경계"·"Checkpoint 용어
구분"·"Reversibility — 필수 Architecture 불변조건"·"미해결 상태로
유지되는 v2 공백"·"Workflow Module Defer(§16.7)와의 구분"·"명칭"·
"Adapter Contract — §16.6 A-IN 부속 명세"의 (a)(b)(d) bullet·(c) 문단·
"이 Accept가 결정하지 않는 것"·"Production 구현과의 관계" 문단은 **전부
문자 그대로 유지**한다.

특히 Adapter Contract **(d) Reversibility — 재확인** bullet의 "그 통합
테스트의 **실행**은 이 반영의 결과가 아니다(후속 Implementation Strategy,
`ADC-0019` §Next Step 4)" 문장은 **verbatim 유지**한다 — 그 문장은
`ADR-0009` 반영의 범위를 기술한 것으로 시점상 정확하며, E4의 실행은
`ADR-0009`가 아니라 `ADC-0021` §8 Gate (C)의 결과다. 위 §2.1 신설 문단이
E4 실행 사실을 별도로 기록하며, (d)의 계약 문언을 재정의하지 않는다.

### 3. `GLOSSARY.md` 갱신 내용

"Kernel Modules — Workflow Adapter (Reference)" 절 주석 블록(`>` 인용)의
마지막 문장("`hqs/development/IMPLEMENTATION_RULES.md`의 Workflow/Scheduler/
Runtime/Event Bus 구현 금지는 그대로 유효하다.") **뒤**에 다음 한 문장을
잇는다:

```markdown
> Reversibility 불변조건은 `ADC-0021` §8 Gate (C)의 in-repo 통합
> 테스트(E4 `projects/workflow-adapter-reversibility-v2/EVIDENCE.md`,
> IN-1~IN-5 22 PASS)로 v2 맥락에서 **부분 충족**으로 재현됐다 —
> 결정론적 stub·LangGraph 단일 계보·실엔진 미검증이라는 잔여 한계가
> 있어 완전 discharge는 아니며, `ADC-0019` 재검토 조건 (c)와 v1
> `ADR-0007` 결정 2/5/9/11은 그대로 미충족이다
> (`docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md`).
```

표의 "Workflow Adapter"·"Adapter Contract" 행, "Concept Model 용어" 절은
무변경.

### 4. `hqs/development/IMPLEMENTATION_RULES.md` 갱신 여부

**갱신하지 않는다.** `ADC-0020` §6 조건 4·`ADR-0009` §6과 동일 판단 —
E4는 재현 검증 Evidence일 뿐 구현 착수를 허용하지 않는다. `ADC-0019`
조건 5가 여전히 Production 구현 착수를 금지하며(Gate (A) 미해소), Gate
(B)도 미충족이다. line 9/13/14/19(Workflow Parser / Scheduler·orchestration·
Dynamic Routing·§6 넓은 Runtime / Stage 재진입·조건부 Stage / Event Bus
구현 금지)는 전면 유지된다.

### 5. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version(§17) | v1.13 | **v1.14** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Minor 증가(v1.14) 근거**: 신설 최상위·하위 절이 없다. 기존 §16.6 절
내부에 "부분 충족(E4)" 문단 하나를 추가하고 §17 이력 한 줄을 더할
뿐이다(§16.6 다른 문단·§16.1~§16.5·§16.7·§6·§14·§15.2 무변경,
`IMPLEMENTATION_RULES.md` 무변경). `ADR-0004`(명칭 반영, v1.8)·`ADR-0009`
(부속 명세, v1.13)와 같은 granularity. `RFC-0020` → `ADC-0020` →
`ADR-0009` 이후 `ADC-0021` → 이 ADR의 절차를 그대로 거쳤다.

### 6. Migration Strategy

> 아래 1~3은 Review PASS 이후 **실행되었다**(Status: Accepted). 4(커밋)는
> 별도로 진행한다 — 이 시점까지 Commit/PR/Merge는 없다.

1. `docs/architecture/baseline/BASELINE.md`:
   - §16.6 "Reversibility — 필수 Architecture 불변조건" 문단 뒤에 §2.1
     "부분 충족(E4)" 문단을 삽입한다("미해결 상태로 유지되는 v2 공백"
     문단 앞).
   - §16.6의 다른 모든 문단, §16.1~§16.5·§16.7·§6·§14·§15.2는 문자
     그대로 유지한다.
   - §17 Version을 v1.13 → v1.14로 바꾸고 변경 이력 맨 위에 다음 한
     줄을 추가한다:

     > `| v1.14 | §16.6 Reversibility 필수 불변조건의 v2 통합 테스트 재현 상태를 **부분 충족(E4)**으로 기록 — `projects/workflow-adapter-reversibility-v2/` in-repo 통합 테스트(IN-1~IN-5, 22 PASS: 최종 State 동치·예외 비전파·caller-owned Checkpoint 별도-프로세스 재개·교체 시 파일 해시 불변·구현체 문법 격리)가 Sequential Reference ↔ LangGraph 대조로 도메인 형태 그래프에서 불변조건 재현. **완전 discharge 아님** — 잔여 한계: 결정론적 stub(실엔진 비결정성 미검증)·LangGraph 단일 계보·프로덕션 트래픽 미검증. `ADC-0019` 재검토 조건 (c)(=Gate (B)) 미충족 유지, v1 ADR-0007 결정 2/5/9/11(=Gate (A)) 미해소 유지. E4는 Experimental Evidence이며 Public Contract 승격·LangGraph 채택·IMPLEMENTATION_RULES 해제·Production 구현 착수를 발생시키지 않음(자동 승격 없음). §16.6 A-IN/A-OUT·Adapter Contract (a)(b)(c)(d) 문언(특히 (d) verbatim)·§16.1~§16.5·§16.7·§6·§14·§15.2 무변경. Checkpoint 입도 C1·Q-E-2·"Sequential=Reference" GLOSSARY 신설은 반영 대상 아님. `IMPLEMENTATION_RULES.md` 무변경. 근거: `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md` |`

2. `docs/00_governance/GLOSSARY.md` — §3의 한 문장을 "Workflow Adapter
   (Reference)" 절 주석 블록 끝에 잇는다. 표·"Concept Model 용어" 절
   무변경.

3. `hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
   `docs/architecture/core/ADC-0008`, `core/`·`hqs/`·`dashboard/` —
   변경하지 않는다.

4. 검증:
   - `BASELINE.md` 최상위 절 번호가 §1~§17로 유지되는지(신설 절 없음,
     §16.6 번호 유지).
   - §16.6의 §2.1 신설 문단 외 모든 문단, §16.1~§16.5·§16.7·§6·§14·
     §15.2가 문자 그대로인지(`git diff`가 §16.6과 §17에만 국한).
   - Adapter Contract (a)(b)(c)(d) bullet·(c) 문단이 무변경인지, 특히
     (d)의 "실행은 이 반영의 결과가 아니다" 문장이 verbatim인지.
   - 신설 문단에 "Port/Public/Guarantee/Interface" 어휘가 없고, §14에
     추가된 항목이 없는지. "완전 discharge"·"조건 4 충족" 선언 문언이
     없고 "부분 충족"만 있는지.
   - `GLOSSARY.md`의 표·"Concept Model 용어" 절이 문자 그대로인지.
   - `IMPLEMENTATION_RULES.md`가 `git diff` 0줄인지.
   - `git status`로 `core/`·`hqs/`·`dashboard/`·`docs/decisions/`가
     무변경인지.

5. 커밋 — 이 ADR과 위 `BASELINE.md`·`GLOSSARY.md` 변경을 함께 커밋한다
   (승인 이후).

---

## Consequences

- `BASELINE.md`가 v1.13 → v1.14가 되고, §16.6 Reversibility 필수
  불변조건이 **v2 맥락 in-repo 통합 테스트로 부분 재현**됐음이 잔여
  한계(결정론적 stub·LangGraph 단일 계보·실엔진 미검증)와 함께 기록된다.
- **완전 discharge는 선언되지 않는다.** `ADC-0019` 조건 4의 Conditional
  성격은 유지되며, 완전 충족·해제는 잔여 한계 (i)~(iii)가 후속 절차로
  메워질 때 별도 판정된다.
- **Gate (A)·(B)는 hard gate 그대로다.** v1 `ADR-0007` 결정 2/5/9/11
  미해결, `ADC-0019` 재검토 조건 (c) 미충족 — E4는 둘 중 어느 것도
  진전시키지 않는다.
- `GLOSSARY.md`에 E4 재현 상태가 한 문장으로 반영된다. 표·"Concept
  Model 용어" 절은 무변경.
- `IMPLEMENTATION_RULES.md`는 **무변경**이다 — E4는 구현 착수를 허용하지
  않는다. line 9/13/14/19 전면 유지.
- Kernel Public Contract(§14)는 무변경 — 새 Public Interface·Port·
  Surface·Guarantee 없음. §14.1 "Task 전달 책임" 미결 상태 그대로.
- Adapter Contract (a)(b)(c)(d) 문언, §16.6 A-IN/A-OUT, Checkpoint 입도
  C1, phase 경계 선언 주체(Q-E-2 Defer), (c) Defer는 무변경.
- E4는 Experimental Evidence로 남으며, 후속 ADR/절차가 이를 반영·심화하기
  전까지 Public Contract·LangGraph 채택·구현 착수의 근거가 되지 않는다.
- 이 ADR은 **Accepted** 상태이며, §Decision·§Migration Strategy의
  `BASELINE.md`(§16.6 문단 추가 + §17 v1.14)·`GLOSSARY.md`(주석 한 문장)
  변경이 Review PASS 이후 반영되었다. 커밋은 별도로 진행한다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **없음(사실 기록만)** — §16.6이 가리키는 책임의
  범위(A-IN/A-OUT)·불변조건 자체는 전혀 바뀌지 않는다. 이미 §16.6에 있는
  "v2 통합 테스트로 재현 검증해야 한다"는 요구의 **이행 상태**를 부분
  충족으로 기록할 뿐이다. 새 책임·Layer·Component·Concept 없음.
- **Contract Impact**: **없음** — 공개 Interface 미정의. §14 무변경.
  Adapter Contract 부속 명세 (a)(b)(c)(d) 문언 무변경. E4 harness seam은
  계약이 아니며 Baseline에 시그니처가 들어가지 않는다.
- **Kernel Impact**: **없음(사실 기록만)** — Kernel Concept 목록·책임
  경계 무변경. E4가 부분 재현한 불변조건은 이미 등재돼 있던 것이다.

## Governance Chain 검증

`ADC-0019`(§Q6·조건 4 — 재현 검증 요구) → `ADR-0008`/`ADR-0009`(§16.6에
그 요구 등재) → `RFC-0020` → `ADC-0020` → `ADR-0009` → `ADC-0021`(§8 Gate
(C) — 재현 검증을 첫 Gate-clearing으로 지정, 후속 ADR이 충족/부분 할인
판정) → Test Design 0001 + E4(설계·구현·실행, 22 PASS) → **이 ADR**
(Accepted — E4를 근거로 §16.6에 "부분 충족" 기록, §17 v1.14, GLOSSARY 한
문장. 새 결정 없음).

- `ADC-0021` §8이 이 ADR을 명시적으로 예고했다("이후 후속 ADR이 조건 4
  충족/부분 할인 판정") — 별도 ADC 불요(사실 기록 반영이지 새 Architecture
  결정 아님). RFC pairing은 `ADC-0021` §1.4대로 `RFC-0020` §8.2로 충족.
- `ADC-0019` 조건 1~6·재검토 조건 (c), `ADC-0020` §6 조건 1~8, `ADC-0021`
  §6·§7 조건이 §Out of Scope·§Consequences에 그대로 재확인됨 — 위반 없음.
- E4가 `ADC-0021` §7 Out of Scope로 둔 항목(LangGraph 채택, §14 승격,
  `IMPLEMENTATION_RULES` 해제, Production 구현, Gate (A)/(B))을 이 ADR이
  새로 반영하지 않음 — 위반 없음.
- `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로
  Formal Architecture Decision이나 ADC Accept를 발생시키지 않는다"를
  준수 — 이 ADR은 E4의 **재현 사실**만 기록하고, Promotion은 여전히 후속
  절차가 판단한다.
- §16.6 신설 문단이 §16.3~16.5·§14·Adapter Contract (a)(b)(c)(d)의 문장을
  인용은 하되 수정·재정의하지 않음을 §Decision 2.2·§Migration 4 검증
  절차가 확인 — 충돌 없음.

## Review (Architecture / Governance Review 결과)

| 점검 | 결과 |
|---|---|
| 완전 discharge를 선언했는가 | **아니오** — §Decision 2.1·§Consequences: "부분 충족"만, 조건 4 Conditional 유지, 완전 충족은 잔여 한계 해소 시 별도 판정 |
| 잔여 한계(결정론적 stub·LangGraph 단일 계보·실엔진 미검증)를 §16.6에 명시했는가 | **예** — §Decision 2.1 문단 (i)(ii)(iii), §17 이력 줄, GLOSSARY 문장 |
| Gate (B) 재검토 조건 (c)를 E4로 충족 처리했는가 | **아니오** — §Decision 2.1·§Consequences·§Out of Scope: 미충족 명시, hard gate 유지 |
| Gate (A) v1 결정 2/5/9/11을 해소했는가 | **아니오** — §Out of Scope·§Consequences: 미해소 유지 |
| Experimental Evidence를 Public Contract·LangGraph 채택·`IMPLEMENTATION_RULES` 해제·Production 구현으로 자동 승격했는가 | **아니오** — §Decision 4·§Consequences·§Governance Chain: 전부 무변경, 자동 승격 없음 명문화 |
| 기존 Architecture/Contract 범위를 변경했는가 | **아니오** — §Architecture/Contract/Kernel 영향: 전부 "없음(사실 기록만)". §16.6 A-IN/A-OUT·Adapter Contract 문언·§14·§16.1~§16.5·§16.7·§6·§15.2 무변경 |
| Adapter Contract (d) "실행은 이 반영의 결과가 아니다"를 재정의했는가 | **아니오** — §Decision 2.2: verbatim 유지, 신설 문단이 별도로 E4 실행 사실 기록 |
| 새 최상위·하위 절을 신설했는가 | **아니오** — §16.6 내부 문단 1개 추가, 번호 유지 |
| `IMPLEMENTATION_RULES.md`·§14·`ADC.md`·Production Code를 변경했는가 | **아니오** — §Decision 4·§Migration 3 |
| Version 증가가 적절한가 | **예** — Minor(v1.14), `ADR-0004`/`ADR-0009` granularity |
| ADR이 필요한가(vs 새 ADC) | **예, ADR** — `ADC-0021` §8이 예고한 사실 기록 반영. 새 Architecture 결정 없어 새 ADC 불요 |

**판정: PASS.** 수정사항 없음. §Decision·§Migration Strategy 1~3이 Review
PASS 이후 반영됐고, 커밋은 별도.

## Self Review

- `ADC-0021`이 예고하지 않은 것을 반영했는가 — **아니오**. §8 Gate (C)
  후속 ADR의 범위(E4 결과를 §16.6에 부분 충족으로 기록)에 정확히 한정.
- "완전 discharge"·"조건 4 충족"을 선언했는가 — **아니오**(§Decision 2.1,
  §Review) — "부분 충족"만, Conditional 유지.
- 잔여 한계 3건을 §16.6 문언에 넣었는가 — **예**(§Decision 2.1 (i)(ii)(iii)).
- Gate (A)·(B)를 hard gate로 유지했는가 — **예**(§Out of Scope·
  §Consequences·§Governance Chain).
- E4를 Public Contract·LangGraph 채택·`IMPLEMENTATION_RULES` 해제·
  Production 구현으로 자동 승격했는가 — **아니오**(§Decision 4,
  §Consequences, §Governance Chain — 자동 승격 없음 명문화).
- §16.6 A-IN/A-OUT·Adapter Contract (a)(b)(c)(d)·§14·§16.1~§16.5·§16.7·
  §6·§15.2를 수정했는가 — **아니오**(§Decision 2.2·§Migration 4).
- (d) 문단을 verbatim 유지했는가 — **예**(§Decision 2.2).
- `IMPLEMENTATION_RULES.md`를 변경했는가 — **아니오**(§Decision 4).
- 새 절/새 Architecture/새 Contract를 만들었는가 — **아니오**(§Architecture/
  Contract/Kernel 영향: 전부 "없음").
- Version을 Minor로 적절히 증가했는가 — **예**(v1.13 → v1.14, §Decision 5).
- Production Code를 변경했는가 — **아니오**.
- Commit/PR/Merge를 했는가 — **아니오** — Review PASS 후 `BASELINE.md`·
  `GLOSSARY.md` 반영만. 커밋은 사용자 승인 후 별도.
