# RFC-0039: Stage 05 Parallel Validation DAG — Architecture Independence Validation

**Status**: Proposed (검토 대상, 결정 아님 — §9가 이 RFC의 핵심 결론이다)
**Author**: Claude Code(사용자 요청에 따른 Architecture 조사)
**대상**: Stage 05의 목표 Architecture(현재 구현이 아니라 재설계 후보).
**방법론 전제(사용자 지시)**: 현재 `stage_05.py` 구현은 이 조사의
기준이 아니다 — 기존 함수/호출 순서를 보존해야 한다는 전제를 두지
않는다. 기존 문서(`RESPONSIBILITY.md`/`CAPABILITIES.md`/`VALIDATION.md`,
`RFC-0030`, `RFC-0038`/`ADC-0041`)는 **책임과 의도를 파악하기 위한
참고자료로만** 사용한다. 판단은 코드가 아니라 **책임의 본질**을
기준으로 한다.

**이 RFC가 확정하지 않는 것**: Production 코드 변경, Stage 05 재구현,
Contract 변경. §9에서 Independence 판정 결과와 채택 여부를 공식화한다.

---

## 0. 책임 재정의(6개, 사용자 지시 그대로 채택)

기존 `stage_05.py`의 함수 이름(`_check_structural` 등)이 아니라, 사용자가
이번에 재정의한 6개 책임 이름을 그대로 쓴다 — 이는 기존 4개 결정적
검사 + Code Review 재사용이라는 현재 구현의 5-분류와 **의도적으로 다른
분류**다(현재 구현을 기준으로 삼지 않는다는 전제 반영).

| 책임 | 본질(현재 구현이 아니라 "이 책임이 답해야 하는 질문") |
|---|---|
| **Structure** | Stage 04 Output이 기대하는 형태(Contract Shape)를 갖췄는가? |
| **Scope** | 대상(Target)이 이미 정의된 Scope Context(Specification이 승인한 범위) 안에 있는가? |
| **AST** | Implementation이 Target 외의 다른 부분을 바꾸지 않았는가? |
| **Dependency** | Implementation이 참조하는 것들(함수/심볼/모듈)이 실제로 존재/유효한가? |
| **Test** | Implementation을 실제로 적용했을 때 기존 동작이 깨지지 않는가? |
| **Review** | Implementation에 실질적 결함/위험/스타일 문제가 있는가? |

---

## 1. 공통 전제

목표 Architecture 후보 DAG가 가정하는 대로, 아래 분석은 **"Stage 04
Implementation과 Stage 05에 필요한 Context가 이미 준비된 상태"**에서
출발한다 — 즉 각 책임의 실행 시점에 다음 antecedent(선행) 자료가
이미 손에 있다고 가정한다(이 자체가 Fan-out 이전의 "Stage 05
Validation Context" 노드의 역할이며, 이 RFC는 이 노드를 §5에서
구체화한다):

- Stage 04 Output(target, implementation, expose_target 등)
- Scope Context(Stage 02가 승인한 scope 후보 — **Validator가 아니라
  Context**, §2.2에서 구분을 엄격히 지킨다)
- Dependency Context(Implementation이 참조 가능한 심볼/모듈의 유효
  집합 — 예: candidate index/closure류)
- Architecture/Design Context(Stage 03 Output)
- Contract(각 책임이 지켜야 할 계약 자체)
- 대상 파일의 원본 코드(**"메타데이터"** — 이 자체가 나중에 §4가
  분석하는 Race Condition의 핵심 대상이다)

---

## 2. 책임별 8항목 독립성 분석

각 항목은 코드가 아니라 책임의 본질로만 판단한다(사용자 지시).

### 2.1 Structure

| 항목 | 판단 |
|---|---|
| 1. Input Dependency | Stage 04 Output 객체(이미 만들어진 값)뿐 — 다른 Stage 05 책임의 결과 불필요 |
| 2. Output Dependency | 다른 어떤 책임도 Structure의 결과를 자신의 입력으로 요구하지 않는다(형태 확인은 그 자체로 완결) |
| 3. Shared State | 없음 — 순수하게 이미 주어진 객체의 키/형태만 본다 |
| 4. File I/O / Mutation | 없음 |
| 5. Execution Ordering Dependency | 없음 |
| 6. Failure Dependency | Structure가 실패(형태 이상/Engine 실패 신호)해도 다른 책임의 "실행 가능 여부"를 논리적으로 막지 않는다 — 단, 다른 책임이 "쓸모 있는 결과"를 낼 수 있는지는 별개 질문(§3에서 Test에 대해 별도로 다룬다) |
| 7. 다른 5개 책임 결과 필요 여부 | 불필요 |
| 8. Parallel 시 Race Condition | 없음(읽기 전용, 공유 가변 상태 없음) |

**판정: A(Fully Independent)**

### 2.2 Scope

| 항목 | 판단 |
|---|---|
| 1. Input Dependency | Target 식별자(Stage 04 Output) + **Scope Context**(Stage 02가 이미 확정한 scope 후보 목록) — **주의**: 이는 "Scope Validator의 결과"가 아니라 "Scope의 정의/Context"다(사용자 지시의 구분을 정확히 반영). Scope 책임은 이 Context를 소비할 뿐, 스스로 그 Context를 만들지 않는다 |
| 2. Output Dependency | 다른 책임이 Scope의 PASS/FAIL을 입력으로 요구하지 않는다(각자 독립적으로 Target/Context를 직접 참조 가능) |
| 3. Shared State | Scope Context 객체(읽기 전용으로 취급되면 안전) |
| 4. File I/O / Mutation | 없음(문자열/식별자 비교) |
| 5. Execution Ordering Dependency | 없음 |
| 6. Failure Dependency | 없음 |
| 7. 다른 5개 책임 결과 필요 여부 | 불필요 |
| 8. Parallel 시 Race Condition | 없음(Context가 읽기 전용으로 공유되는 한) |

**판정: A(Fully Independent)**

### 2.3 AST

| 항목 | 판단 |
|---|---|
| 1. Input Dependency | Target 원본 파일의 **원본 코드**(변경 전) + Implementation 텍스트 + Target 식별자 |
| 2. Output Dependency | 다른 책임이 AST의 결과를 요구하지 않는다 |
| 3. Shared State | **원본 코드 스냅샷**(§4에서 핵심 쟁점으로 다룸) |
| 4. File I/O / Mutation | **읽기만** — 자신은 파일을 바꾸지 않는다 |
| 5. Execution Ordering Dependency | 없음(단, "원본 코드"를 어느 시점에 확보하느냐가 §4의 Race 문제와 직결) |
| 6. Failure Dependency | 없음 |
| 7. 다른 5개 책임 결과 필요 여부 | 불필요 |
| 8. Parallel 시 Race Condition | **있음, 조건부** — Test가 같은 파일을 일시적으로 mutate하는 동안 AST가 "원본"을 읽으면 오염된 값을 읽을 위험(§4에서 해소 방법 제시) |

**판정: A(원본 스냅샷을 Context 단계에서 미리 확보하는 경우) / B(그렇지 않고 실행 시점에 라이브 파일을 직접 읽는 경우)** — §4·§5에서 A로 수렴시키는 설계를 제시한다.

### 2.4 Dependency

| 항목 | 판단 |
|---|---|
| 1. Input Dependency | Implementation 텍스트 + **Dependency Context**(참조 가능한 심볼/모듈의 유효 집합 — AST와 마찬가지로 "Validator의 결과"가 아니라 사전에 구축된 Context) |
| 2. Output Dependency | 없음 |
| 3. Shared State | Dependency Context(읽기 전용) |
| 4. File I/O / Mutation | 없음(순수 정적 참조 검사) |
| 5. Execution Ordering Dependency | 없음 |
| 6. Failure Dependency | 없음 |
| 7. 다른 5개 책임 결과 필요 여부 | 불필요 |
| 8. Parallel 시 Race Condition | 없음(Context가 읽기 전용인 한) |

**판정: A(Fully Independent)** — AST와 동일한 책임 계열(정적 분석)이나, Dependency는 원본 파일이 아니라 사전에 구축된 참조 인덱스만 있으면 되므로 AST보다도 Race 위험이 낮다.

### 2.5 Test

| 항목 | 판단 |
|---|---|
| 1. Input Dependency | Implementation 텍스트 + Target 파일 경로(적용 대상) |
| 2. Output Dependency | 없음(다른 책임이 Test 결과를 자신의 입력으로 요구하지 않는다) |
| 3. Shared State | **대상 파일 자체**(전체 DAG에서 유일하게 "쓰기"가 필요한 공유 자원) |
| 4. File I/O / Mutation | **있음** — Implementation을 파일에 적용 → 실행 → 반드시 원상복구. 이는 책임의 본질에 내재한다(실제로 동작하는지 확인하려면 실제로 적용해봐야 한다) |
| 5. Execution Ordering Dependency | 다른 책임에 대해서는 없음. 다만 자기 자신의 mutate→run→revert 3단계는 내부적으로 순서가 고정된다 |
| 6. Failure Dependency | 없음(Implementation이 구조적으로 이상해도 Test는 "적용 후 실패"라는 그 자체로 유효한 결과를 낸다 — 다른 책임의 결과를 기다릴 논리적 필요가 없다. 단, §3에서 실효성/효율성 관점의 별도 논의) |
| 7. 다른 5개 책임 결과 필요 여부 | 불필요 |
| 8. Parallel 시 Race Condition | **있음, 구조적** — AST/Review가 같은 파일 경로를 읽는 시점과 Test의 mutate 구간이 겹치면 오염된 값을 읽는다. 이는 책임의 본질(mutation)에서 나오는 것이라 "피할 수 없는" 위험이지만, "격리로 해결 가능한" 위험이다(§4) |

**판정: B(Independent with Isolation/Coordination)** — 유일하게 A가 아닌 이유는 실행 로직이 다른 책임에 의존해서가 아니라, **공유 파일 시스템 자원에 쓰기를 한다는 책임의 본질** 때문이다.

### 2.6 Review — 가장 엄격하게 검증(사용자 지시)

| 항목 | 판단 |
|---|---|
| 1. Input Dependency | Implementation 텍스트 + Architecture/Design Context + Contract + Scope Context(정의, Result 아님) + 필요 시 원본 코드/메타데이터(읽기 전용) |
| 2. Output Dependency | 없음 |
| 3. Shared State | 원본 코드 스냅샷이 필요하다면 AST와 동일한 Shared State(§4에서 함께 해소) |
| 4. File I/O / Mutation | 없음(자신은 쓰지 않는다) |
| 5. Execution Ordering Dependency | 없음(원본 스냅샷이 Context 단계에서 미리 확보되는 한) |
| 6. Failure Dependency | 없음 |
| 7. 다른 5개 책임 결과 필요 여부 | **아래 §2.6.1에서 5개 각각 독립적으로 판정** |
| 8. Parallel 시 Race Condition | AST와 동일 조건(§4) — 원본 코드를 라이브로 읽지 않는 한 없음 |

#### 2.6.1 Review ← 각 책임 결과, 5개 독립 판정

- **Review ← Structure Result**: **불필요.** Review의 본질("이 코드에
  실질적 결함/위험/스타일 문제가 있는가")은 Structure가 확인하는 것
  ("Stage 04 Output이 기대 형태를 갖췄는가")과 다른 질문이다. Structure의
  PASS/FAIL을 몰라도 주어진 Implementation 텍스트를 그대로 검토할 수
  있다. (실무적 최적화로 "Structure가 FAIL이면 Review를 건너뛴다"는
  선택은 가능하지만, 이는 **효율성 short-circuit**이지 **논리적
  의존**이 아니다 — 이 RFC는 이 둘을 명확히 구분한다.)
- **Review ← Scope Result**: **불필요.** Review는 "이 코드가 허용된
  범위 안에 있는가"가 아니라 "이 코드 자체에 결함이 있는가"를 묻는다.
  Scope의 **정의/Context**(예: "이 함수만 고치도록 되어 있다")는
  Review에 유용한 배경 정보가 될 수 있지만, 이는 Scope **Context**의
  소비이지 Scope **Validator의 PASS/FAIL 결과**에 대한 의존이 아니다
  (사용자 지시의 구분을 그대로 적용).
- **Review ← AST Result**: **불필요.** AST가 확인하는 것("Target 외에
  다른 것이 바뀌었는가")은 Scope 무결성 신호이지 코드 품질 신호가
  아니다. Review는 AST의 `changed_names` 같은 목록 없이도 주어진 텍스트
  자체의 결함을 판단할 수 있다.
- **Review ← Dependency Result**: **불필요.** 두 책임이 서로 닿는 것처럼
  보이는 지점("정의되지 않은 심볼을 참조하는가")이지만, 본질적으로
  다른 성격이다 — Dependency는 "참조가 실제로 해소되는가"를 결정적으로
  확인하는 정적 분석이고, Review는 "이 코드가 설계 의도에 맞게 잘
  쓰였는가"를 판단하는 질적 검토다. Review가 Dependency의 결과를
  기다려야만 판단 가능한 구조가 **아니다** — 오히려 Review는 "이
  참조가 유효한지 검증되지 않았다"는 사실 자체를 결함/위험으로
  지적할 수 있다(Dependency의 최종 판정 없이도 그 불확실성 자체를
  서술 가능).
- **Review ← Test Result**: **불필요.** Test는 "실제로 동작하는가"라는
  경험적 사실을, Review는 "코드가 잘 쓰였는가"라는 질적 판단을 묻는다.
  테스트를 통과해도 스타일/위험 문제가 있을 수 있고, 테스트가 실패해도
  코드 자체의 품질 판단(원인 분석 포함)은 가능하다 — Review가 Test의
  PASS/FAIL을 몰라도 자신의 판단을 완결할 수 있다.

**결론(사용자 지시의 판정 기준 적용)**: Review는 5개 중 **어느 것의
PASS/FAIL 결과도 입력으로 요구하지 않는다.** Review Input이
"Stage 04 Implementation / Architecture·Design Context / Contract /
Scope Context / 필요한 원본 코드·메타데이터"만으로 구성된다는 목표
Architecture의 전제와 일치한다.

**판정: A(Fully Independent)** — 단, 원본 코드/메타데이터를 라이브
파일에서 직접 읽지 않고 Context 단계의 읽기 전용 스냅샷에서 받는다는
조건 하에(§4·§5, AST와 동일 조건).

---

## 3. Test 전용 추가 검증(사용자 지시)

- **Test가 다른 Validator의 결과를 기다려야 하는가?** — 논리적으로는
  **아니오**(§2.5 항목 6). Implementation이 구조적으로 결함이 있어도
  Test는 "적용 후 실패"라는 유효한 결과를 낸다.
- **Test 실행이 다른 Validator의 결과에 의해 skip/fail되어야 하는가?** —
  **아니오, 필수는 아니다.** 다만 Structure가 이미 "이 Implementation은
  Engine 실패 메시지이며 실제 코드가 아니다"를 확인했다면, Test를 그대로
  파일에 적용해 pytest를 돌리는 것은 "실패할 게 뻔한 작업을 반복"하는
  것이다 — 이는 **효율성(Cost/Latency) 최적화를 위한 선택적
  short-circuit**이며, 독립성 판정 자체를 바꾸지 않는다(§2.1의 Structure
  분석과 동일 원칙, "논리적 필요"와 "실무적 최적화"를 구분).
- **Test가 파일/환경을 mutation하는가?** — **그렇다, 필연적으로.**
  실제로 동작하는지 확인하려면 실제로 적용해봐야 한다 — 이는 Test라는
  책임의 본질에서 나오는 특성이지 구현상의 우연이 아니다.
- **mutation이 다른 Validator와 충돌하는가?** — **AST와 Review가 같은
  파일의 "원본" 내용을 라이브로 읽는 설계라면 충돌한다.** Scope/
  Structure/Dependency는 파일을 직접 읽지 않으므로(Context/객체만
  소비) 충돌하지 않는다.
- **충돌한다면 독립 실행 환경으로 해결 가능한가?** — **가능하다,
  두 가지 방법으로**(§5에서 채택 설계로 구체화):
  1. **Context 단계 선(先) 스냅샷**: Fan-out 이전에 "Stage 05 Validation
     Context" 노드가 원본 파일 내용을 1회 읽어 불변 값으로 만들고,
     AST/Review는 이 스냅샷만 참조한다 — 그러면 Test의 mutation
     시점과 무관해진다.
  2. **Test 자체의 격리 실행**: Test가 공유 원본 파일이 아니라
     격리된 사본(임시 디렉터리/격리 checkout)에 Implementation을
     적용해 실행한다 — `IMPLEMENTATION_RULES.md` "Execution Host
     구현 허용 범위(Scoped, ADC-0015)"가 정확히 이 문제("동일
     Target을 동시 실행할 가능성이 있는 경로에서 격리 제공")를
     다루며, "Process를 1차로, Subprocess를 대안으로, **Thread는
     사용하지 않는다**"는 조건을 명시한다 — Test의 병렬 격리 실행은
     이 허용 범위 안에서만 설계되어야 한다.

두 방법은 상호 배타적이지 않다 — **1번(Context 선-스냅샷)은 AST/
Review·Test 사이의 충돌을 원천적으로 제거하고, 2번(Test 자체 격리)은
설령 향후 다른 Node가 파일을 읽는 경우가 추가되어도 안전망이 된다.**
이 RFC는 둘 다 채택을 권고한다(§5).

---

## 4. Race Condition 종합 — "무엇이 진짜 공유 가변 상태인가"

6개 책임 전체에서 **유일한 실제 공유 가변 상태는 대상 파일 자체**다.
나머지(Stage 04 Output 객체, Scope/Dependency Context, Design Context)는
전부 Fan-out 이전에 이미 값이 고정된 **불변 입력**이다 — 이것들을 여러
Node가 동시에 "읽는" 것은 Race Condition이 아니다(쓰기가 없는 한
충돌은 정의상 발생하지 않는다).

따라서 Race Condition은 정확히 하나의 질문으로 좁혀진다: **"AST/
Review가 원본 파일을 읽는 시점"과 "Test가 그 파일을 mutate하는
구간"이 겹치는가?** — 이것은 §3이 이미 답했다: **Context 단계 선-
스냅샷 + Test 격리 실행**으로 해소 가능하다.

`IMPLEMENTATION_RULES.md`의 Multi-Task 허용 범위(ADC-0016)가 요구하는
사전 조건("동시 실행되는 각 Task가 서로 다른 파일/Artifact
이름공간에 쓰거나 아무것도 쓰지 않는다는 것이 **구현 착수 전에**
확인되어야 한다")도 정확히 이 설계로 충족된다 — Test만 쓰고, 그마저도
격리된 이름공간에 쓴다면 이 조건을 만족한다.

---

## 5. 채택/수정/거부 판단 — 목표 DAG를 그대로 채택하지 않는다

사용자가 제시한 DAG(Structure/Scope/AST/Dependency/Test/Review 6-way
Fan-out → Aggregator → Final Verdict)는 **구조적으로는 채택 가능**하지만,
이 RFC의 분석 결과 **한 가지 필수 수정**을 요구한다 — 원안을 그대로
가정하지 말라는 사용자 지시를 그대로 따른다:

**수정 1(필수)**: "Stage 05 Validation Context" 노드는 단순히 데이터를
전달하는 통로가 아니라, **원본 파일 내용의 읽기 전용 스냅샷을 이 시점에
1회 확보하는 책임**을 명시적으로 가져야 한다. 이 스냅샷이 AST와
Review 양쪽에 공급된다. 이 수정 없이는 AST/Review가 §2.3/§2.6에서
B로 강등된다.

**수정 2(권고)**: Test는 원본 공유 파일이 아니라 격리된 실행 환경
(Process/Subprocess 기반 사본)에서 mutate→run→revert를 수행한다.
`ADC-0015` Scoped 허용 범위(Thread 금지)를 그대로 따른다.

이 두 수정을 반영하면:

```
Stage 04 Implementation
        |
        v
+---------------------------------------------------+
| Stage 05 Validation Context                        |
| - Stage 04 Output, Scope/Dependency/Design Context  |
| - 원본 파일 내용의 읽기 전용 스냅샷(1회 확보, 수정 1)|
+-------------------------+---------------------------+
                          |
     +------------+-------+-------+-------+------------+
     |            |               |       |            |
     v            v               v       v            v
 Structure(A)  Scope(A)      AST(A*)  Dependency(A)  Test(B, 격리 실행)  Review(A*)
     |            |               |       |            |            |
     +------------+-------+-------+-------+------------+------------+
                              |
                              v
                         Aggregator
                       (결정적 수집·병합)
                              |
                              v
                        Final Verdict
                     (결정적 규칙만 사용)
```

(`A*` = 수정 1이 전제될 때만 A, 그렇지 않으면 B)

**원안 대비 차이**: 그림의 형태(6-way Fan-out → Aggregator → Verdict)는
그대로 유지된다 — 사용자가 제시한 DAG는 **구조적으로 틀리지 않았다.**
다만 "Context가 준비된 상태"라는 전제를 **구체화**해, Context 노드의
책임에 "원본 파일 스냅샷 확보"를 명시적으로 포함시켜야 한다는 것이
이 RFC의 수정 사항이다.

---

## 6. Aggregation 원칙

- Aggregator는 각 Node가 반환한 **완결된 Result 객체**(status/detail
  형태, 기존 `CheckResult` 패턴과 동형)만 수집한다 — Aggregator
  자신은 재판단하지 않는다(순수 수집·병합).
- 어떤 Node가 실패/타임아웃해도 Aggregator나 다른 Node를 중단시키지
  않는다 — Stage 01의 `ParallelRunner`(`TaskStatus`:
  SUCCESS/TIMEOUT/FAILED/INVALID_OUTPUT, ADR-0021 Production
  Adopted)가 이미 이 정확한 문제를 해결한 선례이며, 이 설계의 재사용
  후보다.
- Node 결과가 누락되면(예: 아직 실행되지 않음) 조용히 무시하지 않고
  명시적 상태(SKIPPED/INCONCLUSIVE류)로 남긴다 — 현재 `stage_05.py`의
  `required_checks`/`check_results` 패턴이 이미 이 원칙을 지키고
  있으며, 재설계에서도 유지해야 한다.

## 7. Final Verdict 종합 원칙

- Structure/Scope/AST/Dependency/Test — 이 5개는 **결정적으로 판정
  가능한 사실**(형태/멤버십/구조적 diff/참조 유효성/실행 결과)이므로,
  FAIL 시 Verdict를 blocking하는 기존 원칙을 유지한다.
- Review는 그 결과가 Deterministic이든 LLM이든 **Verdict 계산에 직접
  반영하지 않는다** — `RESPONSIBILITY.md`/`RFC-0030`/`RFC-0038`이 이미
  일관되게 확인한 "Policy 구현 금지" 원칙(Engine 판단을 Verdict
  결정에 두지 않는다)을 그대로 유지한다. Review는 보조 Evidence로
  남는다.
- Verdict 계산 로직 자체를 Agent(LLM)로 만들지 않는다 — 이 원칙은
  이번 재설계로도 바뀌지 않는다.

---

## 8. Review의 Deterministic/LLM/Hybrid 적합성 — 독립성과 분리해서 판단

**사용자 지시대로, Review가 LLM이어야 한다고 가정하지 않는다.** §2.6이
이미 Review의 **독립성**을 확정했으므로(Deterministic이든 LLM이든
Hybrid든 입력 Contract는 동일), 이제 "무엇으로 구현해야 하는가"는
별개 질문이다.

- Review의 본질 중 **"스타일/구문 패턴/명백한 안티패턴" 부분**은
  결정론적 도구(linter류, AST 패턴 매칭)로 근사 가능하다 — Stage 04
  Architecture Validation Harness의 `quality_heuristics.py`가 이미
  이런 근사(`explicitness_issue_count`/`simplicity_issue_count`)를
  결정론적으로 구현한 선례가 있다.
- Review의 본질 중 **"이것이 함수 자신이 명시한 동작을 위반하는
  실제 결함인가"**(현재 `backend_agent_code_review`의 지시문 자체가
  "개선 아이디어와 실제 결함을 구분하라"고 명시)는 일반적으로
  결정론적으로 완전히 판정할 수 없는 **의미적(semantic) 판단**이다 —
  Stage 04의 Ponytail 조사(`RFC-0037` §2 Q5)가 동일한 결론(Readability/
  Semantic Consistency는 결정론적으로 측정할 방법이 없음)에 도달한
  것과 같은 성격의 문제다.
- **결론**: Review에 LLM 사용은 **Architecture상 필수가 아니라
  선택사항**이다. 순수 Deterministic Review는 "구현 가능하지만 책임
  범위가 좁아진다"(스타일/패턴만 커버), 순수 LLM Review는 "현재
  구현"(범위는 넓지만 재현성 없음), **Hybrid**(Deterministic
  pre-filter/보조 신호 + LLM 최종 판단, 또는 둘을 별도 Evidence로
  병렬 산출)가 가장 방어 가능한 기본 방향이다 — 단, 이 RFC는 셋 중
  하나를 확정하지 않는다(Not Determined, §9).

---

## 9. 이 RFC의 결론

### 9.1 최종 독립성 판정표

| Responsibility | Input | Dependency | Shared State | Mutation | Ordering | Parallel Verdict | Evidence |
|---|---|---|---|---|---|---|---|
| **Structure** | Stage 04 Output 객체 | 없음 | 없음 | 없음 | 없음 | **A** | §2.1 — 순수 형태 확인, 다른 책임과 접점 없음 |
| **Scope** | Target + Scope **Context**(Result 아님) | 없음 | Scope Context(읽기 전용) | 없음 | 없음 | **A** | §2.2 — Context와 Result를 구분, Context만 소비 |
| **AST** | 원본 코드 스냅샷 + Implementation | 없음(단, 스냅샷 확보 시점에 조건부) | 원본 코드 스냅샷 | 없음(읽기만) | Context 선-스냅샷 필요 | **A\*** (수정 1 전제) | §2.3, §4 — Test와의 파일 공유가 유일한 위험, 스냅샷으로 해소 |
| **Dependency** | Implementation + Dependency Context | 없음 | Dependency Context(읽기 전용) | 없음 | 없음 | **A** | §2.4 — AST와 동일 계열이나 원본 파일 불필요, 더 안전 |
| **Test** | Implementation + Target 파일 | 없음(논리적) | **대상 파일(유일한 실제 공유 가변 자원)** | **있음(mutate→run→revert)** | 자기 내부만 | **B** | §2.5, §3, §4 — 격리 실행 또는 선-스냅샷으로 해소 가능한 구조적 위험 |
| **Review** | Implementation + Design/Scope **Context** + Contract + 원본 코드(읽기 전용) | **없음(5개 전부, §2.6.1 개별 확인)** | 원본 코드 스냅샷(AST와 공유) | 없음 | Context 선-스냅샷 필요 | **A\*** (수정 1 전제) | §2.6, §2.6.1 — 5개 Validator 결과 중 어느 것도 논리적으로 불필요 |

### 9.2 최종 결론(사용자 지시 8개 질문)

1. **6개 모두 Parallel 가능한가?** — 조건부로 **그렇다.** §5의 수정
   1(Context 선-스냅샷)과 수정 2(Test 격리 실행)를 채택하면 6개 전부
   Fan-out 가능(A 5개 + B 1개, B는 "실행 불가"가 아니라 "격리 필요"라는
   뜻).
2. **일부만 Parallel 가능한가?** — 위 두 수정을 채택하지 **않는다면**,
   AST/Review는 Test와의 파일 공유 때문에 B로 강등되고, 사실상 Test가
   완료된 뒤에만 안전하게 실행해야 하는 순서 제약이 생긴다. 이 RFC는
   수정 채택을 권고하므로, "일부만"이 아니라 "전부, 단 Test는 격리
   조건부"가 정확한 답이다.
3. **순차로 남겨야 하는 책임은 무엇인가?** — **없다.** 6개 중 어느
   것도 다른 5개 중 하나의 출력을 자신의 입력으로 요구하지 않는다
   (§2 전체, §2.6.1). 유일한 순서 제약은 "Context 노드의 스냅샷 확보"가
   Fan-out **이전에** 끝나야 한다는 것뿐이며, 이는 6개 책임 사이의
   순서가 아니라 Context 준비 단계 자체의 순서다.
4. **Isolation이 필요한 책임은 무엇인가?** — **Test뿐이다.** 유일하게
   공유 가변 자원(파일)에 쓰기를 하기 때문이다(§2.5, §4).
5. **Aggregator가 각 결과를 어떻게 수집해야 하는가?** — §6 — 완결된
   Result 객체만 수집, 재판단하지 않음, 부분 실패를 명시적 상태로
   기록, Stage 01 `ParallelRunner`의 `TaskStatus` 패턴 재사용 후보.
6. **Final Verdict는 각 Validator의 결과를 어떻게 종합해야 하는가?** —
   §7 — Structure/Scope/AST/Dependency/Test는 blocking 결정적 신호,
   Review는 Deterministic/LLM/Hybrid 무엇이든 **비-blocking 보조
   Evidence로만** 유지(Policy 구현 금지 원칙 재확인).
7. **Review가 다른 5개와 완전히 독립적인가?** — **그렇다(A)**, 단
   원본 코드를 Context 단계의 읽기 전용 스냅샷에서 받는다는 조건
   (수정 1)에서(§2.6, §2.6.1, §9.1).
8. **Review의 LLM 사용은 Architecture상 필수인가, 선택사항인가?** —
   **선택사항이다.** 독립성은 구현 방식(Deterministic/LLM/Hybrid)과
   무관하게 성립하며, Review 책임의 일부(스타일/패턴)는 결정론적으로
   근사 가능하지만 전체 범위(의미적 결함 판단)는 여전히 사람 또는
   LLM 판단이 필요한 영역으로 남는다 — **Hybrid를 가장 방어 가능한
   기본 방향으로 제시**하되 확정하지 않는다(§8).

### 9.3 Parallel DAG 채택 여부

**구조 자체는 채택(Accept), 그대로는 아니고 §5의 수정 1·2를 포함해
채택을 권고한다.** 사용자가 제시한 6-way Fan-out → Aggregator → Final
Verdict 형태는 이 RFC의 독립성 분석과 논리적으로 정합하다 — 다만
"Context가 준비된 상태"라는 전제를 Context 노드의 명시적 책임(원본
스냅샷 확보)으로 구체화해야 한다.

**단, 이것은 "Architecture 방향에 대한 채택"이지 "Production 구현
승인"이 아니다.** RFC-0037/ADC-0040(Stage 04)과 동일한 이유로 — 이
RFC는 **문서/추론 기반 독립성만 검증**했고, 실제 Engine으로 6개 Node를
동시 실행했을 때의 실제 latency/cost/실패율/Isolation 구현의 실제
정확성은 **Real Execution Evidence 0건**이다. 구조적 독립성이 확인됐다는
것과 Production Architecture로 확정하는 것은 다르다 — 후속 ADC(§10)가
이 구분을 그대로 유지한다.

---

## 10. Architecture/Contract/Governance 영향

| 항목 | 영향 |
|---|---|
| Kernel Public Contract(`BASELINE.md` §14) | 영향 없음 — Stage 내부 실행 구조는 Kernel이 규정하지 않는다(`ADC-0036` §Q2, `RFC-0038` §7과 동일 근거 구조) |
| `VerificationResult` Contract(`ADR-0009` Public Scope) | **영향 있음** — 현재 4개 결정적 키 + `code_review` flat 구조에서, 6개 Node별 Result + Aggregator 병합 구조로 바뀌면 Public Scope 자체가 바뀐다. `VALIDATION.md`가 이미 "`KNOWN_CHECK_NAMES`에 새 검사 이름을 추가하는 것은 Public Scope 변경이므로 RFC → ADC → ADR 대상"이라고 명시했다 — 이 재설계는 그보다 큰 변경(구조 자체 변경)이므로 동일하거나 더 엄격한 절차가 필요하다 |
| `IMPLEMENTATION_RULES.md` Execution Host(§16.3, ADC-0015 Scoped) | Test의 격리 실행(Process/Subprocess, Thread 금지)이 이미 허용된 범위 안에 있는지 **재확인이 필요하다** — 이 RFC의 판단으로는 "동일 Target 동시 실행 경로에서 격리 제공"이라는 기존 허용 범위와 정확히 일치하지만(§3, §4), 공식 재확인은 별도 ADC 대상 |
| `IMPLEMENTATION_RULES.md` Multi-Task(§16.4, ADC-0016 Scoped) | 6-way Fan-out이 "서로 입력 독립·출력 비의존인 소수의 실행 단위를 동시에 시작·수집"이라는 기존 허용 범위와 부합하는지 확인 필요 — 이 RFC의 분석(§9.1)은 부합한다고 보지만, "Data/Artifact Isolation 사전 확인"(ADC-0016 §Q4)이 실제로 구현 전에 충족되는지는 Test Node의 격리 설계가 실제로 구현된 뒤에만 검증 가능 |
| Stage 05 `RESPONSIBILITY.md`/`CAPABILITIES.md`/`VALIDATION.md` | 6개 책임 재정의를 반영하려면 전면 재작성이 필요(현재 4+1 분류와 다른 6개 분류) |
| ParallelRunner(`mvp/parallel_runner.py`) 재사용 여부 | Stage 01 선례가 있으나, ThreadPoolExecutor 기반이라 Engine 호출(Review, LLM일 경우)엔 적합해도 Test의 파일 mutation에는 부적합(Thread 금지 규칙과 충돌 가능성) — Test와 나머지 5개는 서로 다른 실행 메커니즘이 필요할 수 있다는 점을 Governance가 확인해야 한다 |

**RFC → ADC → ADR 필요 여부**: **필요하다.** Public Contract 변경
(VerificationResult 구조), Execution Host/Multi-Task 허용 범위와의
정합성 재확인, Stage 05 문서 전면 재작성 — 이 세 가지 전부 Frozen
Architecture/Governance 절차 대상이다. 이 RFC는 그 절차의 첫 단계일
뿐이다.

## 11. Out of Scope / Non-goals

- Test 격리 실행의 실제 메커니즘(Process vs Subprocess, 어떤 방식으로
  파일 사본을 만들지)을 구체적으로 설계하는 것 — 후속 작업.
- Review를 Deterministic/LLM/Hybrid 중 무엇으로 구현할지 확정하는
  것 — §8이 선택지만 제시하고 확정하지 않는다.
- `VerificationResult`의 새 Contract 형태를 구체적으로 설계하는 것 —
  이는 별도 RFC 대상이다(§10).
- Production 코드 변경 — 이 RFC는 문서만 추가한다.

## Related

- `hqs/development/stages/05_validation/README.md`/`RESPONSIBILITY.md`/`CAPABILITIES.md`/`VALIDATION.md`(참고자료로만 사용, §서두)
- `docs/architecture/core/RFC-0030-dev-hq-stage-agent-team-boundary-analysis.md`(§3 Stage 05 원 분석)
- `docs/architecture/core/RFC-0038-stage05-qa-multi-agent-boundary.md`,
  `docs/architecture/core/ADC-0041-stage05-qa-multi-agent-decision.md`(QA Agent 활성화 관점의 선행 조사 — 이 RFC는 그와 다른 축(6개 책임의 Parallel DAG)을 다룬다)
- `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md`,
  `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md`(동일 방법론·판정 구조 선례)
- `docs/architecture/core/ADR-0021-stage01-multi-agent-reasoning-adoption-baseline.md`(`ParallelRunner`/`TaskStatus` Production 선례)
- `hqs/development/IMPLEMENTATION_RULES.md`(Execution Host §16.3 ADC-0015, Multi-Task §16.4 ADC-0016)

## Self Review

- 현재 구현을 Architecture 기준으로 삼았는가 — **아니오**(전 구간
  "책임의 본질" 기준으로 분석, 현재 함수는 참고자료로만 인용).
- 기존 함수/호출 순서 보존을 전제했는가 — **아니오**(§0에서 사용자가
  재정의한 6개 책임 이름을 그대로 채택, 현재 5-분류와 의도적으로
  다르게 유지).
- Review가 LLM이어야 한다고 가정했는가 — **아니오**(§8, 독립성 판정과
  구현 방식 선택을 명시적으로 분리).
- Review의 5개 의존성을 각각 독립적으로 판정했는가 — **Pass**(§2.6.1).
- 원안 DAG를 결론으로 가정했는가 — **아니오**(§5 — 독립성 분석 결과에
  따라 수정 사항을 도출한 뒤 채택).
- Production 코드를 변경했는가 — **아니오**.
- Architecture 결정을 내렸는가 — **아니오**(§9.3 — 방향 채택 권고이지
  Production 승인 아님, 후속 ADC로 공식화).
- commit/push를 수행했는가 — 이 파일 작성 이후 `ADC-0042`와 함께
  별도로 수행한다.

## Validation — 기존 Architecture/Governance와의 충돌 여부 확인

- `git status --porcelain` — 이 RFC 파일 1건만 신규 추가 예정.
  `hqs/development/`·`core/`·`dashboard/` Production Code 무변경(읽기만
  수행).
