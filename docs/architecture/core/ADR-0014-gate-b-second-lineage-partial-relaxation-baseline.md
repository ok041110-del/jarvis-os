# ADR-0014: Gate (B) 2차 부분 완화(E6/L-B)의 Baseline 반영 (ADC-0025 후속)

| 필드 | 내용 |
|---|---|
| ID | `docs/architecture/core/ADR-0014` (`docs/decisions/adr/`에는 동명 문서 없음 — 네임스페이스로 구분) |
| 제목 | `ADC-0025`의 Decision(`ADC-0024` §D-B4(i) "2번째 비-LangGraph 독립 계보"가 E6/L-B로 충족되나, Gate (B) **완전 완화는 아님 — 2차 부분 완화**)을 Architecture Baseline·GLOSSARY에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** — Architecture/Governance Review PASS(아래 §Governance Chain 검증·§Self Review) 이후, 사용자 승인에 따라 §Migration Strategy 1~4를 실행했다. `BASELINE.md` v1.17 → v1.18(§16.6 2.1 부기·2.2 정정·§17 버전/이력), `GLOSSARY.md` 주석 1문장 추가 반영 완료. `IMPLEMENTATION_RULES.md`·§14·§16.6 A-IN/A-OUT·Adapter Contract (a)(b)(c)(d) 문언·§16.1~§16.5·§16.7·§6·§15.2·기존 ADC/ADR 원문·`core/`·`hqs/`·`dashboard/`·experimental project 3건은 무변경(§4 검증 결과로 확인). 5(Commit/PR)는 이번 반영과 함께 `claude/*` feature branch에서 수행, PR 생성까지 진행한다(`main` 직접 Merge는 없음 — `ADR-0011`~`ADR-0013` 선례) |
| Context | `docs/architecture/core/ADC-0025-gate-b-second-lineage-partial-relaxation.md` — **Status: Decided — ADR Required**, Architecture/Governance Review PASS(§9), 판정 **Partial**. D-C1(E6이 `ADC-0024` §D-B4(i)를 충족 — Yes), D-C2(Gate B 완전 완화 아님 — 2차 부분 완화), D-C3(완전 완화의 실질적 경로 = v2 프로덕션 관찰로 수렴, 정책적 판단), D-C4(연다: 형식 요건 강화 기록 / 열지 않는다: 완전 완화·LangGraph 평가·Gate (C)·Production·§14) |
| 관련 ADC | `docs/architecture/core/ADC-0025-gate-b-second-lineage-partial-relaxation.md` |
| 선행 ADR | `docs/architecture/core/ADR-0013`(Gate (B) 1차 부분 완화, BASELINE v1.17 — 이 ADR이 이어받는 버전), `docs/architecture/core/ADR-0010`(Gate (C) E4 "부분 충족" — 이 ADR이 건드리지 않는 문단), `docs/architecture/core/ADR-0011`·`ADR-0012`(Gate (A) 전체 Resolved, BASELINE v1.16) |
| 선행 Decision(참고, 뒤집지 않음) | `ADC-0019` §Decision 조건 1~6·재검토 조건 (a)(b), `ADC-0021` §8 AND 게이트(조건 1·3·4)·Sequential Reference 기본선, `ADC-0024` §D-B1~D-B4(K-1 인정 기준·E5 형식 요건 충족/부분 완화), `ADR-0010`(Gate (C) "부분 충족"), `ADR-0013`(Gate (B) 1차 부분 완화) — 이 ADR은 어느 것도 변경하지 않는다 |

이 ADR은 `ADC-0025`가 이미 내린 Decision을 다시 논의하지 않는다. 새로운
철학·Architecture·Contract를 제안하지 않는다. `ADC-0025` §5 D-C1~D-C4
중 **Gate (B)의 2차 부분 완화(완전 완화 아님)**를 실제
`BASELINE.md`·`GLOSSARY.md` 문서 변경으로 옮기기 위한 **구현 결정**만
기록한다.

| 단계 | 다루는 것 |
|---|---|
| `ADC-0019`/`ADC-0021` | 재검토 조건 (c) 명문화, Gate (B) 명명, AND 게이트 조건 2 배정 |
| `ADC-0024`/`ADR-0013` | E5(L-A) 비-LangGraph 독립 계보 1개, Gate (B) 1차 부분 완화(형식 요건 충족), BASELINE v1.17 |
| E6 (Experimental) | 비-LangGraph 독립 계보 2개째(L-B, 재귀 조합자), IN-1′~IN-6′ 31 PASS — `ADC-0024` §D-B4(i) 실제 실행 |
| `ADC-0025` | D-C1(E6 = D-B4(i) 충족, Yes) / D-C2(완전 완화 아님 — 2차 부분 완화) / D-C3(완전 완화 실질 경로 = v2 프로덕션 관찰로 수렴) / D-C4(연다: 형식 요건 강화 기록 / 열지 않는다: 완전 완화·LangGraph 평가·Gate (C)·Production·§14) |
| **이 ADR** | `ADC-0025` §8 지침의 Baseline Governance 반영 — §16.6에 짧은 부기 문단 추가, "v2 공백의 현재 상태" 문단 괄호 설명 정정, `GLOSSARY.md` 주석에 1문장 추가, §17 v1.17 → v1.18 (**실행 완료**) |
| 후속 별도 절차 | Gate (B) 완전 완화(v2 프로덕션·실엔진 관찰, `ADC-0025` §D-C3) / Gate (C) 완전 discharge / `ADC-0021` §8 조건 1(LangGraph 평가 ADC) / Implementation Strategy / `IMPLEMENTATION_RULES.md` Scoped 해제 / Production 구현 |

## Out of Scope (이 ADR이 다루지 않는 것)

`ADC-0025`가 Decision 범위에서 반영을 지시하지 않은 것, 사용자 지시가
명시적으로 배제한 것은 **하나도 반영하지 않는다**(`ADC-0025` §1.2·§7).

| 항목 | 근거 |
|---|---|
| **Gate (B) 완전 완화(Conditional 해제) 선언** | `ADC-0025` §D-C2·D-C4 — 이 ADR은 "2차 부분 완화"만 기록한다. "완전 완화"·"충족 선언" 문언은 어디에도 넣지 않는다 |
| **Gate (C) 판정 / `ADR-0010` "부분 충족" 재판정** | `ADC-0025` §6 조건 3, §7 — 별도 gate. E6이 건드리지 않음. §16.6 "잔여 한계 (i)~(iii)" 서술은 verbatim 유지 |
| **`ADC-0021` §8 조건 1(LangGraph 고유 능력 필요) 판정 / LangGraph 평가 ADC 개설 / LangGraph 채택** | `ADC-0025` §4.4·§7 — 조건 1은 관찰 0건 그대로. Sequential Reference 기본선 유지 |
| **Production 구현 착수 / `IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19 해제** | `ADC-0021` §8, `ADC-0025` §6 조건 5 — Gate (B) 2차 부분 완화가 해제하지 않음 |
| **§14 Kernel Public Contract 승격 / §14 scope 확장** | `ADC-0025` §6 — Gate (B) 강화도 §14 승격을 열지 않음 |
| **3번째 비-LangGraph 계보(L-C) 또는 v2 프로덕션 관찰 확보의 착수 지시** | `ADC-0025` §D-C3·§7 — 완전 완화의 실질적 경로로 지목만, 착수 여부·시점·형태는 정하지 않음 |
| **§7 System Boundary 목록 / §11 표 / §14.1 표 편집** | 이 ADR의 반영 대상이 아님 — Gate (B) 상태는 §16.6 cross-reference로만 반영 |
| **`BASELINE.md` §5·§6·§14·§16.1~§16.5·§16.7·§6 Concept Model 표, §16.6 A-IN/A-OUT·Reversibility 필수 불변조건 문단·Adapter Contract (a)(b)(c)(d) bullet·"실행 단위"·"실행 단위 Lifecycle" 문단** | `ADC-0025` §8-4 — 명시적 비변경. 참조만, 문자 그대로 유지 |
| **`GLOSSARY.md` "Workflow Adapter"·"Adapter Contract"·"실행 단위 (Execution Unit)" 표 행, "Concept Model 용어" 절** | 이 ADR은 주석 블록에 1문장만 추가 |
| **`ADC-0019`·`ADC-0021`·`ADC-0024`·`ADR-0010`·`ADR-0013` 원문 편집** | Gate (B)의 새 상태는 `BASELINE.md` §16.6 cross-reference로만 반영한다 |
| **Production Code(`core/`, `hqs/`, `dashboard/`), E4/E5/E6 experimental project** | 전혀 수정하지 않는다 |
| **`main`으로의 직접 Merge** | 이번 단계는 사용자 승인에 따른 Migration 실행 + `claude/*` feature branch 커밋·PR 생성까지만. Merge는 별도 승인 후 진행(사용자 지시) |

---

## Decision (실행 완료)

### 1. 변경 대상 파일 (실행 완료)

| 파일 | 변경 내용 |
|---|---|
| `docs/architecture/baseline/BASELINE.md` | §16.6 **(2.1)** "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)" 문단 뒤, `ADR-0013`이 부기한 E5 문단(현재 §16.6 "`ADC-0019` 재검토 조건 (c)(= `ADC-0021` §8 Gate (B))의 **형식 요건**..." 문단, `main` 현재 라인 1165~1178) **바로 뒤에 1개 문단 추가**(E6/2차 부분 완화). **(2.2)** "v2 공백의 현재 상태" 문단의 Gate (B) 언급 parenthetical **1곳 정정**(문언 그대로 유지, 괄호 안 설명만 갱신 — `ADC-0025` 인용 추가). §17 Version을 v1.17 → v1.18로 갱신하고 변경 이력 한 줄 추가. §16.6의 다른 모든 문단과 §1~§15·§16.1~§16.5·§16.7·§6 Concept Model 표·§14·§14.1·§7·§15.2는 **문자 그대로 유지** |
| `docs/00_governance/GLOSSARY.md` | "Workflow Adapter (Reference)" 절 주석 블록 끝에 **1문장 추가**(Gate (B) 2차 부분 완화 상태). 표의 세 행("Workflow Adapter"·"Adapter Contract"·"실행 단위 (Execution Unit)")·"Concept Model 용어" 절은 무변경 |

`hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
`docs/architecture/core/ADC-0008`, `docs/architecture/core/ADC-0010`,
`docs/architecture/core/ADC-0019`, `docs/architecture/core/ADC-0021`,
`docs/architecture/core/ADC-0022`, `docs/architecture/core/ADC-0023`,
`docs/architecture/core/ADC-0024`, `ADR-0010`, `ADR-0011`, `ADR-0012`,
`ADR-0013`, Kernel Public Contract(§14·§14.1), §7 목록, Production Code는
이 ADR로 건드리지 않는다(§Out of Scope·§4·§5) — 위 두 파일 외에는
**어떤 파일도 변경 대상이 아니다**.

### 2. `BASELINE.md` §16.6 갱신 내용 (계획)

`ADC-0025` §5 D-C1~D-C4와 §8 지침이 이미 정리한 것만 옮긴다. 새 판단을
만들지 않는다.

#### 2.1 새 문단 추가 — E6/Gate (B) 2차 부분 완화

삽입 위치: `ADR-0013`이 부기한 E5 문단("`ADC-0019` 재검토 조건 (c)(=
`ADC-0021` §8 Gate (B))의 **형식 요건**... 완전 완화(Conditional
해제)는 2번째 비-LangGraph 계보 또는 v2 프로덕션 맥락의 조건부 분기·
Loop 실행 관찰이 추가된 뒤 재판정한다(`ADC-0024` §D-B4)... §D-B3.")
**바로 뒤**, "**v2 공백의 현재 상태 (Conditional)**" 문단 **앞**.

기존(그 문단의 마지막 문장, 무변경 대상 — 참고용):

```markdown
이 부분 완화는 (i)·(iii) 잔여 한계나 Gate (C)
자체를 해소하지 않으며, LangGraph 평가 ADC·Production 구현 착수·§14
승격 중 무엇도 열지 않는다(`ADC-0021` §8 조건 1·4 미충족, `ADC-0024`
§D-B3).
```

추가(위 문단 뒤에 새 문단, 기존 문단은 문자 그대로 유지):

```markdown
2번째 비-LangGraph 독립 계보 관찰이 이후 E6(`projects/workflow-adapter-recursive-lineage-v1/`
— 재귀 조합자 L-B, IN-1′~IN-6′ 31 PASS)로 추가됐다(`ADC-0025`). E6의
독립성 검증(자료구조 부재 — 인터프리터 인스턴스·큐 없음; 실행 메커니즘
계측 — 자기 재귀 호출의 정적 검출과 실측 최대 콜스택 깊이 14)은 위 E5
문단의 독립성 검증(정적 import 목록)보다 엄밀하다. 독립 관찰은 4건
(E1·E2·E5·E6), 비-LangGraph 계보는 **2개**로 강화됐다. 그러나 v2
프로덕션·실엔진 맥락 관찰은 여전히 **0건**이고 두 비-LangGraph 계보
모두 동일 프로세스·언어(Python)·데이터 모델(`graph_spec`)을 소비하므로,
Conditional 성격은 **2차 부분 완화**에 그친다(`ADC-0025` §D-C2). 완전
완화에 이르는 실질적 경로는 비-LangGraph 계보의 추가 반복이 아니라 v2
프로덕션 맥락의 조건부 분기·Loop 실행 관찰로 사실상 수렴한다고 판단됐다
(`ADC-0025` §D-C3). 이 2차 부분 완화는 위 잔여 한계 (i)·(iii)나 Gate
(C) 자체를 해소하지 않으며, LangGraph 평가 ADC·Production 구현 착수·
§14 승격 중 무엇도 열지 않는다(`ADC-0021` §8 조건 1·4 미충족, `ADC-0025`
§D-C4).
```

#### 2.2 "v2 공백의 현재 상태" 문단의 Gate (B) parenthetical 정정

기존(해당 문장만 — 그 앞뒤 문장은 문자 그대로 유지, `main` 현재 라인
1196~1201):

```markdown
Production 구현 착수는 `ADC-0019` 재검토 조건 (c)(형식 요건 충족 / 견고성 조건 잔존 —
`ADC-0021` §8 Gate (B), `ADC-0024`) + Reversibility 필수 불변조건의 v2
완전 검증(위 "부분 충족(E4)" 문단, `ADC-0021` §8 Gate (C)) +
`hqs/development/IMPLEMENTATION_RULES.md`로 **계속 차단된다** — 결정
2·5·9·11의 해소는 이 중 어느 것도 해제하지 않는다.
```

교체 후(괄호 안 설명만 갱신 — 차단 문언·나머지 문장은 문자 그대로
유지):

```markdown
Production 구현 착수는 `ADC-0019` 재검토 조건 (c)(형식 요건 충족(강화) /
견고성 조건 잔존 — `ADC-0021` §8 Gate (B), `ADC-0024`·`ADC-0025`) +
Reversibility 필수 불변조건의 v2 완전 검증(위 "부분 충족(E4)" 문단,
`ADC-0021` §8 Gate (C)) + `hqs/development/IMPLEMENTATION_RULES.md`로
**계속 차단된다** — 결정 2·5·9·11의 해소는 이 중 어느 것도 해제하지
않는다.
```

> §2.2는 §2.1이 확정한 상태(Gate (B) 2차 부분 완화)를 이 문단의
> cross-reference에도 정합하게 만드는 **참조 정정**이다. 새 Architecture
> Decision이 아니며, 차단의 실질(Gate (B) 부분 완화 + Gate (C) +
> `IMPLEMENTATION_RULES.md`)은 그대로다(`ADR-0011` §2.7·`ADR-0012`
> §Migration Strategy 주석·`ADR-0013` §2.2와 동일 논리).

### 3. `BASELINE.md`에서 손대지 않는 것 (명시)

- §16.6 "Reversibility — 필수 Architecture 불변조건" 문단 **(verbatim)**.
- §16.6 "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)" 문단의 **기존 문장 전부**(잔여 한계 (i)~(iii) 서술 포함).
- `ADR-0013`이 부기한 E5 문단(§16.6 "형식 요건... 부분 완화..." 문단)의 **기존 문장 전부** — §2.1은 그 **뒤에 새 문단을 추가**할 뿐, 기존 문단 문언은 한 글자도 바꾸지 않는다.
- §16.6 A-IN/A-OUT, "실행 단위(Execution Unit)"·"실행 단위 Lifecycle"·"A-IN(a) 공유 State가 담는 정보" 문단, 명칭 문단, Adapter Contract (a)(b)(c)(d) bullet + 도입부, "Workflow Module Defer(§16.7)와의 구분" 문단.
- §1~§15·§16.1~§16.5·§16.7·§6 Concept Model 표·§14·§14.1 표·§7 목록·§11 표·§15.2.

### 4. `BASELINE.md` §6 Concept Model 표 / §14·§14.1 / §7 목록 갱신 여부

**추가·수정하지 않는다.** Gate (B) 2차 부분 완화는 §14 승격을 열지
않으며(`ADC-0025` §6), §7·§11·§14.1의 어떤 행도 이 반영으로 바뀌지
않는다. Gate (B)의 새 상태는 §16.6 본문 cross-reference로만 서술한다.

### 5. `hqs/development/IMPLEMENTATION_RULES.md` 갱신 여부

**갱신하지 않는다.** `ADC-0021` §8 AND 게이트의 조건 1(미충족)·4(부분
충족)가 그대로이므로 Scoped 해제 대상이 없다. line 9/13/14/15/16/19
전면 유지.

### 6. `docs/00_governance/GLOSSARY.md` 갱신 내용 (계획)

"Kernel Modules — Workflow Adapter (Reference)" 절 **주석 블록 끝에
1문장만** 추가한다. 표의 세 행·"Concept Model 용어" 절은 무변경.

기존(주석 블록 마지막 문장, `main` 현재 상태):

```markdown
> Reversibility 불변조건은 `ADC-0021` §8 Gate (C)의 in-repo 통합
> 테스트(E4 `projects/workflow-adapter-reversibility-v2/EVIDENCE.md`,
> IN-1~IN-5 22 PASS)로 v2 맥락에서 **부분 충족**으로 재현됐다 —
> 결정론적 stub·LangGraph 단일 계보·실엔진 미검증이라는 잔여 한계가
> 있어 완전 discharge는 아니며, `ADC-0019` 재검토 조건 (c)는 형식 요건
> 충족·견고성 조건 잔존이다(`ADC-0024`; v1 `ADR-0007` 결정 9는
> `ADC-0023`으로, 결정 2·5·11은 `ADC-0022`로 해소;
> `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md`).
```

추가 후(마지막 문장 뒤에 1문장 추가, 기존 문장은 문자 그대로 유지):

```markdown
> Reversibility 불변조건은 `ADC-0021` §8 Gate (C)의 in-repo 통합
> 테스트(E4 `projects/workflow-adapter-reversibility-v2/EVIDENCE.md`,
> IN-1~IN-5 22 PASS)로 v2 맥락에서 **부분 충족**으로 재현됐다 —
> 결정론적 stub·LangGraph 단일 계보·실엔진 미검증이라는 잔여 한계가
> 있어 완전 discharge는 아니며, `ADC-0019` 재검토 조건 (c)는 형식 요건
> 충족·견고성 조건 잔존이다(`ADC-0024`; v1 `ADR-0007` 결정 9는
> `ADC-0023`으로, 결정 2·5·11은 `ADC-0022`로 해소;
> `docs/architecture/core/ADR-0010-gate-c-e4-reversibility-partial-fulfillment.md`).
> 비-LangGraph 독립 계보는 이후 2개(E5 worklist L-A, E6 재귀 조합자
> L-B)로 강화됐으나 완전 완화는 아니다 — v2 프로덕션·실엔진 관찰이
> 여전히 0건이다
> (`docs/architecture/core/ADC-0025-gate-b-second-lineage-partial-relaxation.md`).
```

### 7. Version 정책 (계획)

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version(§17) | v1.17 | **v1.18** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: `RFC-0019`(재검토 조건 (c) 원 출처) → `ADC-0021`
§8(Gate (B) 명명) → E5/E6(Experimental Evidence) → `ADC-0024`·`ADC-0025`
(판정) → 이 ADR 절차를 그대로 거친다. `ADR-0001`~`ADR-0013`의 선례와
동일.

**Minor 증가(v1.18) 근거**: 신설 절·문단이 없다. 기존 §16.6 문단
뒤에 문단 1개 추가 + 문단 1곳의 괄호 설명 1건 정정뿐이다(§16.1~
§16.5·§16.7·§6·§14·§14.1·§7·§15.2 무변경, `IMPLEMENTATION_RULES.md`
무변경). 선행 `ADR-0010`(v1.14)·`ADR-0013`(v1.17)과 같은 granularity로
Minor 단위 기록. `ADC-0025` §8이 예상한 폭(v1.18, Minor)과 일치.

### 8. Migration Strategy (1~4 실행 완료, 5는 사용자 승인에 따라 이번 반영에 포함)

> 아래 1~4는 사용자 승인(Architecture/Governance Review PASS 확인 후
> "승인된 Migration 계획에 따라 반영하라" 지시)에 따라 **실행됐다**.
> `BASELINE.md` v1.17 → v1.18, `GLOSSARY.md` 주석 1문장 반영 완료.
> `main` 직접 Commit은 하지 않으며, feature branch 커밋 + PR까지만
> 이번 단계에서 수행한다(Merge는 별도 승인).

1. `docs/architecture/baseline/BASELINE.md`:
   - §16.6에서 `ADR-0013`이 부기한 E5 문단 바로 뒤에 §2.1의 새 문단(E6/
     2차 부분 완화)을 추가한다.
   - §16.6 "v2 공백의 현재 상태" 문단의 Gate (B) parenthetical을 §2.2대로
     교체한다(그 문장의 나머지·차단 문언은 무변경).
   - §3에 열거한 모든 문단, §1~§15·§16.1~§16.5·§16.7·§6·§14·§14.1·§7·
     §15.2는 문자 그대로 유지한다.
   - §17 Version을 v1.17 → v1.18로 바꾸고 변경 이력 맨 위에 한 줄을
     추가한다:

     > `| v1.18 | §16.6 "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)" 문단에 이어 Gate (B) 2차 부분 완화 반영(`ADC-0025`) — `ADC-0024` §D-B4(i)("2번째 비-LangGraph 독립 계보")가 E6(`projects/workflow-adapter-recursive-lineage-v1/` 재귀 조합자 L-B, IN-1′~IN-6′ 31 PASS)로 충족됨을 명시. 독립 관찰 4건(비-LangGraph 계보 2개)으로 강화됐으나 v2 프로덕션·실엔진 관찰은 여전히 0건이므로 Conditional 성격은 **2차 부분 완화**에 그침 — 완전 완화는 v2 프로덕션 맥락 관찰 이후 재판정(`ADC-0025` §D-C3). "v2 공백의 현재 상태" 문단의 Gate (B) cross-reference 괄호 설명 정정(`ADC-0025` 추가 인용). `ADC-0021` §8 조건 1(미충족)·4(부분 충족)로 LangGraph 평가 ADC·Production 구현·§14 승격은 열리지 않음 — 전부 유지. Gate (C)("부분 충족") 무변경, E6이 해소하지 않음. §5·§6·§7·§11·§14·§14.1 표·§16.1~§16.5·§16.7·§6 Concept Model 표·Reversibility 필수 불변조건 문단·Adapter Contract (a)(b)(c)(d) bullet·"실행 단위"·"실행 단위 Lifecycle" 문단·잔여 한계 (i)~(iii) 서술 무변경. `GLOSSARY.md` "Workflow Adapter (Reference)" 절 주석에 1문장 추가. 근거: `docs/architecture/core/ADR-0014-gate-b-second-lineage-partial-relaxation-baseline.md` |`

2. `docs/00_governance/GLOSSARY.md` — §6의 1문장 추가를 "Workflow Adapter
   (Reference)" 절 주석 블록 끝에 반영한다. 표의 세 행·"Concept Model
   용어" 절은 무변경.

3. `hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`,
   `docs/architecture/core/ADC-0008`, `ADC-0010`, `ADC-0019`, `ADC-0021`,
   `ADC-0022`, `ADC-0023`, `ADC-0024`, `ADR-0010`, `ADR-0011`, `ADR-0012`,
   `ADR-0013`, `core/`·`hqs/`·`dashboard/`,
   `projects/workflow-adapter-reversibility-v2/`,
   `projects/workflow-adapter-nonlanggraph-lineage-v1/`,
   `projects/workflow-adapter-recursive-lineage-v1/` — 변경하지 않는다.

4. 검증(실행 완료 — 실제로 수행한 결과):
   - `BASELINE.md` 최상위 절 번호 §1~§17 유지(신설 절 없음).
   - §16.6에서 §2.1 신규 문단 추가 + §2.2 parenthetical 정정 1건 외의
     모든 문단, 그리고 §16.1~§16.5·§16.7·§6·§14·§14.1·§7·§15.2가 문자
     그대로인지(`git diff`가 `BASELINE.md` §16.6·§17 + `GLOSSARY.md`
     1문장 + 이 ADR 파일에만 국한).
   - §16.6 "Reversibility — 필수 Architecture 불변조건" 문단, "부분
     충족 (E4)" 문단, `ADR-0013`이 부기한 E5 문단의 **기존 문장**(전부),
     Adapter Contract (a)(b)(c)(d) bullet, "실행 단위"·"실행 단위
     Lifecycle" 문단이 verbatim.
   - §2.1 신규 문단에 "완전 완화"·"충족 선언"·"Conditional 해제"로
     읽히는 문언이 없고, "2차 부분 완화" + "완전 완화는 ... 이후
     재판정한다"는 유보 문언이 명시되는지.
   - §2.1 신규 문단에 "Port"/"Public"/"Guarantee"/"Interface" 어휘가
     새 계약 항목으로 쓰이지 않고, §14·§14.1 표에 추가된 항목이 없는지.
   - `GLOSSARY.md`의 "Workflow Adapter"·"Adapter Contract"·"실행 단위
     (Execution Unit)" 표 행, "Concept Model 용어" 절이 문자 그대로인지.
   - `IMPLEMENTATION_RULES.md`·`ADC-0019`·`ADC-0021`·`ADC-0024`·
     `ADR-0010`·`ADR-0011`·`ADR-0012`·`ADR-0013`이 `git diff` 0줄인지.
   - `git status`로 `core/`·`hqs/`·`dashboard/`·`docs/decisions/`·
     experimental project 3건(E4/E5/E6)이 무변경인지.

5. 커밋 — 이 ADR과 위 `BASELINE.md`·`GLOSSARY.md` 변경, 그리고 이를
   판정한 `ADC-0025`·근거 Evidence(E6 `projects/workflow-adapter-recursive-lineage-v1/`)를
   함께 `claude/*` feature branch에 커밋하고 PR을 생성한다(`main` 직접
   커밋·Merge는 금지 — Merge는 사용자의 별도 승인 이후 진행).

---

## Consequences (반영됨)

- `docs/architecture/baseline/BASELINE.md`가 v1.17 → v1.18이 되고,
  §16.6에 **Gate (B) 2차 부분 완화**(독립 관찰 4건, 비-LangGraph 계보
  2개) 상태가 기록된다 — 잔여 한계 (i)~(iii)·Gate (C) "부분 충족" 자체,
  `ADC-0021` §8 조건 1(미충족)은 그대로다.
- **Gate (B)**가 "형식 요건 충족(강화: 계보 2개) / 견고성 조건
  잔존(축소되었으나 소멸 안 함 — 프로세스·언어·실엔진 다양성 0)"으로
  읽힌다. **완전 완화(Conditional 해제)는 선언되지 않는다.**
- **Gate (A)**(v1.16)·**Gate (C)**(`ADR-0010` "부분 충족")는 이 ADR로
  **변경되지 않는다**.
- `ADC-0021` §8 조건 1(LangGraph 고유 능력 필요)은 **관찰 0건 그대로**다
  — 이 ADR·`ADC-0025` 어느 것도 이를 진전시키지 않는다.
- `hqs/development/IMPLEMENTATION_RULES.md`는 **무변경**이다.
- Kernel Public Contract(§14)는 무변경 — §14.1 "Task 전달 책임"·"Engine
  호출 책임" 미결 상태 그대로.
- `docs/00_governance/GLOSSARY.md` "Workflow Adapter (Reference)" 절
  주석이 1문장 늘어난다. 표·"Concept Model 용어" 절은 무변경.
- 완전 완화에 이르는 실질적 경로는 v2 프로덕션·실엔진 맥락 관찰로
  수렴한다는 판단(`ADC-0025` §D-C3)이 기록되나, 그 착수를 이 ADR은
  지시하지 않는다.
- 이 ADR은 **Accepted** 상태다 — Architecture/Governance Review PASS
  + 사용자 승인에 따라 §Migration Strategy 1~5를 실행했다(`ADR-0011`~
  `ADR-0013`이 거친 절차와 동일). Commit + PR까지 이번 단계에서
  수행하며, `main` Merge는 별도 승인 후 진행한다.

## Architecture / Contract / Kernel 영향

- **Architecture Impact**: **있음(제한적 — 기존 gate 상태의 서술
  갱신)** — §16.6이 가리키는 책임의 범위(A-IN/A-OUT)는 전혀 바뀌지
  않는다. Gate (B)의 2차 부분 완화 상태만 §16.6 본문에 서술된다.
  Component 설계(§10 Out of Scope)에는 영향 없음.
- **Contract Impact**: **없음** — 공개 Interface·Public Port·Guarantee를
  정의하지 않는다. Kernel Public Contract(§14)·§14.1 표 무변경.
  Adapter Contract 부속 명세 (a)(b)(c)(d) verbatim.
- **Kernel Impact**: **없음(경계·상태 기록)** — 새 Kernel
  Concept·Layer·Component·enum·타입 없음.

## Governance Chain 검증

`ADC-0019`(재검토 조건 (c) 명문화) → `ADC-0021` §8(Gate (B) 명명, AND
게이트 조건 2) → E5(`ADC-0024`→`ADR-0013`, Gate (B) 1차 부분 완화,
BASELINE v1.17) → E6(비-LangGraph 독립 계보 2개째) → `ADC-0025`(Decided
— Partial 판정, Architecture/Governance Review PASS §9) → **이 ADR**
(Accepted — `ADC-0025` §8 지침을 `BASELINE.md` §16.6·§17·`GLOSSARY.md`에
반영 완료, 새 결정 없음).

- `ADC-0025`가 확정한 것(D-C1·D-C2·D-C3·D-C4)을 이 ADR이 재논의하지
  않았다 — Baseline 반영 지침(§8)만 옮겼다.
- `ADC-0025`가 Out of Scope로 둔 것(Gate (B) 완전 완화 선언·Gate (C)·
  `ADC-0021` §8 조건 1·LangGraph 평가·Production·§14 승격·3번째 계보
  착수)을 이 ADR도 새로 결정하지 않았다(§Out of Scope·§4·§5).
- §2.2의 parenthetical 정정은 §2.1이 확정한 상태를 다른 위치에도
  정합하게 만드는 참조 정정이며 새 Architecture Decision이 아니다
  (`ADR-0011` §2.7·`ADR-0012` §Migration Strategy 주석·`ADR-0013` §2.2와
  동일 논리).
- Gate (C)("부분 충족")·`ADC-0021` §8 조건 1·3·4·Sequential Reference
  기본선은 §Out of Scope·§Consequences에 그대로 재확인됨을 확인했다 —
  `ADC-0025` §6 Conditions와 일치.
- 사용자 지시("Gate B Full Relaxation, Gate C(i)/(iii), `ADC-0021` §8
  조건 1, LangGraph 평가, Production 구현은 절대 열지 마라")를 §Out of
  Scope·§2.1 신규 문단 문언("2차 부분 완화", "완전 완화는 ... 재판정한다")·
  §4 검증 체크리스트("완전 완화로 읽히지 않는지")로 3중 확인했다.

## Self Review

- `ADC-0025`가 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(Gate (B) 완전 완화 / Gate (C) / `ADC-0021` §8
  조건 1 / LangGraph 평가·채택 / L-C·프로덕션 관찰 착수 / Production
  구현 / §14 승격 / §7·§11·§14.1 편집 / 기존 ADC·ADR 원문)은 손대지
  않았다.
- Gate (B) 2차 부분 완화만 공식화했는가(완전 완화 아님을 명시) —
  **예**(§2.1·§2.2·§Decision, §4 검증 체크리스트가 "완전 완화로 읽히지
  않는지"를 명시적 검증 항목으로 둠).
- Gate (C) / `ADR-0010` "부분 충족", `ADC-0021` §8 조건 1을 건드렸는가 —
  **아니오**(§3·§Out of Scope) — 잔여 한계 (i)~(iii) 서술·조건 1(관찰
  0건)·Reversibility 불변조건 문단 verbatim.
- LangGraph 평가 ADC 개설이나 Production 구현 착수를 열었는가 —
  **아니오**(§Out of Scope, §Consequences) — Sequential Reference
  기본선·조건 1 미충족·Gate (C) 부분 충족 전부 유지.
- §14 / Public Port / Guarantee를 신설·우회했는가 — **아니오**(§4·§8
  검증) — §14 항목 추가 없음.
- `BASELINE.md` §16.6의 Reversibility 필수 불변조건 문단·"부분 충족
  (E4)" 문단·`ADR-0013`이 부기한 E5 문단의 기존 문장·Adapter Contract
  bullet·"실행 단위"·"실행 단위 Lifecycle" 문단, §1~§15·§16.1~§16.5·
  §16.7·§6·§14·§14.1·§7·§15.2를 수정했는가 — **아니오**(§3·§4 검증
  절차 실행 확인 — `git diff`가 `BASELINE.md` §16.6 2곳·§17,
  `GLOSSARY.md` 1곳에만 국한됨을 확인).
- `hqs/development/IMPLEMENTATION_RULES.md`·`docs/decisions/adc/ADC.md`·
  `ADC-0008`~`ADC-0024`·`ADR-0010`~`ADR-0013`을 변경했는가 — **아니오**
  (§1·§5·§8, `git diff --stat` 0줄로 확인).
- 새 최상위·하위 절을 신설했는가 — **아니오**(§7 개념) — §16.6 내부
  문단 추가·괄호 정정만, §16.6 번호 유지(§1~§17 전체 17개 절 확인).
- `BASELINE.md` / `GLOSSARY.md`를 실제로 수정했는가 — **예** —
  Review PASS + 사용자의 명시적 Migration 승인 이후 §Migration
  Strategy 1~4를 실행했다. 변경은 §2.1·§2.2·§17·§6에 계획된 범위와
  정확히 일치한다(그 이상·이하 없음).
- Production Code·experimental project(E4/E5/E6)를 변경했는가 —
  **아니오**(`git status --porcelain` 확인).
- 반영 과정에서 `ADC-0025`가 이미 인지한 것 이상의 새 Architecture 결정
  지점이 나타났는가 — **아니오**. §2.2 parenthetical 정정은 참조
  정합화이지 새 결정이 아니다.
- Commit/PR을 했는가 — **예** — 이 ADR 파일 + `BASELINE.md`+
  `GLOSSARY.md` Migration + 선행 `ADC-0025` + 근거 Evidence(E6)를
  `claude/*` feature branch에 함께 커밋하고 PR을 생성했다. **Merge는
  아니오** — `main` 직접 커밋/Merge 없이 사용자의 별도 승인을 기다린다.
