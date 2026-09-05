# ADC-0025: Gate (B) — E6(L-B 재귀 조합자)의 `ADC-0024` §D-B4(i) "2번째 비-LangGraph 독립 계보" 기여도 판정

**Status**: Decided — ADR Required (예상 `ADR-0014`). Architecture/Governance Review PASS(§9). `BASELINE.md`·`GLOSSARY.md`·ADR 미착수, Commit/PR/Merge 없음. 사용자 승인 후 진행(`ADR-0011`~`ADR-0013` 선례).
**Author**: Claude Code
**선행 체인**: `RFC-0019`→`ADC-0019`→`ADR-0008`(§16.6 존재 Accept·Conditional, 재검토 조건 (c)) → `ADC-0021` §8(Gate (A)/(B)/(C) 명명; AND 게이트 조건 1~4) → `ADR-0010`(Gate (C) E4 "부분 충족") → `ADC-0022`·`ADC-0023`→`ADR-0011`·`ADR-0012`(Gate (A) 전체 Resolved, BASELINE v1.16) → `ADC-0024`→`ADR-0013`(Gate (B) E5/L-A로 "형식 요건 충족 / 부분 완화", BASELINE v1.17, §D-B4가 완전 완화 후속조건 (i)·(ii) 명명)
**RFC pairing**: `ADC-0019` §Risks·재검토 조건 (c) + `ADC-0021` §8 조건 2 + `ADC-0024` §D-B4 — 이 셋이 이 ADC의 판정 대상이자 트리거다. `ADC-0024`가 `ADC-0021`의 RFC pairing 선례(`RFC-0020` §8.2를 상위 RFC-level 개설로 인정, 신규 RFC 미작성)를 그대로 계승했으므로, 이 ADC도 별도 RFC 없이 동일 pairing을 계승한다 — 새 Boundary Question을 열지 않기 때문이다(§9.1).
**대상**: `ADC-0021` §8 Gate **(B)**에 대해 `ADC-0024` §D-B4가 명명한 완전 완화 후속조건 (i) "2번째 비-LangGraph 독립 계보(L-B)"가 `projects/workflow-adapter-recursive-lineage-v1/`(E6, L-B = 재귀 조합자)로 실제 충족되는지, 그리고 그 결과가 Gate (B)를 "완전 완화(Conditional 해제)"로 재판정하게 하는지.

> 이 ADC는 **E6/L-B가 D-B4(i)를 충족하는지, 그리고 Gate (B) 완전 완화 여부만** 판정한다. Gate (C)(잔여 한계 (i) 결정론적 stub·(iii) 프로덕션 트래픽)를 판정하지 않는다 — E6이 겨냥하지 않았고 해소하지도 않는다. `ADC-0021` §8 AND 게이트 **조건 1**(LangGraph 고유 능력 필요의 반복 관찰)을 판정하지 않는다 — E6은 이 조건과 무관하다. LangGraph 채택·평가 ADC 개설·Production 구현 착수·§14 승격·`IMPLEMENTATION_RULES.md` 해제를 결정하지 않는다. `BASELINE.md`·`GLOSSARY.md`·`ADC-0019`/`ADC-0021`/`ADC-0024`·`ADR-0010`/`ADR-0013` 원문을 편집하지 않는다(후속 ADR의 몫).

---

## 1. 목적과 경계

### 1.1 이 ADC가 판단하는 것 (둘)

| # | 판단 항목 | 근거 위임 |
|---|---|---|
| **D-C1** | **E6/L-B가 `ADC-0024` §D-B4(i)의 "2번째 비-LangGraph 독립 계보"를 실제로 충족하는가** — E5/L-A와의 독립성 Evidence를 기준으로 판단(E5 IN-6이 세운 바보다 E6 IN-6′이 세운 바가 엄밀한지, 아니면 형식만 다른 재구현인지) | `ADC-0024` §D-B4, E5 `EVIDENCE.md`(IN-6), E6 `EVIDENCE.md`(IN-6′-1/2/3) |
| **D-C2** | **Gate (B) 완전 완화(Conditional 해제) 여부** — D-C1이 Yes일 때, 그것으로 충분한지 아니면 추가로 필요한 것이 있는지 | `ADC-0019` §Risks("동일 계보"·"v2 프로덕션 트래픽 아님" 두 우려), `ADC-0024` §D-B2·§D-B4 |

### 1.2 이 ADC가 판단하지 않는 것 (경계)

- **Gate (C) 판정 / `ADR-0010` "부분 충족" 재판정** — 별도 gate. E6은 결정론적 stub이며 (i)·(iii) 잔여 한계를 해소하지 않는다(E6 `EVIDENCE.md` §5).
- **`ADC-0021` §8 AND 게이트 조건 1**(LangGraph 고유 능력 필요) — E6은 이 조건과 무관하다. 조건 1은 이 ADC 이후에도 관찰 0건으로 남는다.
- **LangGraph 채택 / 평가 ADC 개설 / Production 구현 착수 / `IMPLEMENTATION_RULES.md` 해제 / §14 승격** — Gate (B)가 이 ADC로 어떻게 재기술되든, 조건 1·Gate (C)가 미충족·부분 충족인 한 열리지 않는다(§4.4).
- **3번째 비-LangGraph 계보(L-C 등) 또는 v2 프로덕션 관찰의 착수 지시** — 필요 여부만 후속 조건으로 기록한다(§5 D-C3).
- **`BASELINE.md` §16.6 / `GLOSSARY.md` 문언 편집** — 후속 ADR.
- **`ADC-0019`/`ADC-0021`/`ADC-0024`/`ADR-0010`/`ADR-0013` 원문 편집** — Gate (B)의 새 상태는 §16.6 cross-reference로만 반영.

### 1.3 새 실험 없음

이 ADC는 `main`(`15ac209`)에 병합된 Evidence(E4 `projects/workflow-adapter-reversibility-v2/`, E5 `projects/workflow-adapter-nonlanggraph-lineage-v1/`)와, 아직 미병합·미커밋 상태로 세션에 존재하는 E6(`projects/workflow-adapter-recursive-lineage-v1/`, 승인된 Test Design에 따라 구현·실행됨)만 인용한다. 새 PoC·측정을 수행하지 않는다.

---

## 2. Evidence

| # | Evidence | 계보 | 독립성 검증 방식 | 조건부 분기·Loop 실행 |
|---|---|---|---|---|
| **E1** | v1 `ADR-0007` 실사용 + 통합 테스트 | LangGraph | — | 결정 7(병렬 fan-out/fan-in) |
| **E2** | RFC-0019 세션 PoC | LangGraph | — | Conditional Edge + Loop 4회 |
| **E4** | `projects/workflow-adapter-reversibility-v2/` — Sequential ↔ LangGraph | LangGraph(대조축) | — | 조건부 라우팅 + 토론 Loop 3라운드. Gate (C) "부분 충족"(`ADR-0010`) |
| **E5 / L-A** | `projects/workflow-adapter-nonlanggraph-lineage-v1/` — worklist 인터프리터(`_Interpreter` 인스턴스 + `collections.deque` 큐 + `completed`/`pending`/`ready` mutable 속성) | **비-LangGraph #1** | IN-6: import root ⊆ stdlib+domain(AST), docstring에 실행 모델 서술, L-A↔L-LG 상호 import 0 | 조건부 분기 두 갈래 + 수렴 Loop 3회. Gate (B) "형식 요건 충족 / 부분 완화"(`ADC-0024`→`ADR-0013`) |
| **E6 / L-B** | `projects/workflow-adapter-recursive-lineage-v1/` — 재귀 조합자(`_advance` 순수 재귀, 인스턴스·큐 없음, `visited`/`state` 매 단계 새 객체) | **비-LangGraph #2** | IN-6′-1: import root ⊆ stdlib+domain(AST, E5와 동일 바). IN-6′-2(신설): `class`·`collections` 부재를 AST로 확인 + L-A 소스에는 있음을 대조. IN-6′-3(신설): `_advance` 자기 재귀 호출을 AST로 검출 + 실행 중 **최대 콜스택 깊이 14** 실측(그래프 실행 경로 길이에 비례) + L-A `run()`은 `while` 루프 기반·자기 재귀 없음을 동일 방식으로 대조 확인(sibling 파일 텍스트 읽기, import 없음) | 조건부 분기 두 갈래 + 수렴 Loop 3회. `run_full(recursive) == run_full(langgraph)` 3 시나리오. IN-1′~IN-6′ 31/31 PASS |

**핵심 사실**:
- 독립 관찰(K-1 기준, `ADC-0024` §D-B1)은 이제 **4건**(E1·E2·E5·E6)이며, 그중 **2건(E5, E6)이 비-LangGraph**다.
- E6의 독립성 검증은 **E5보다 엄밀하다** — E5 IN-6은 정적 import 목록·docstring 서술·상호 import 0에 그쳤으나("E5 IN-6이 형식적"이라는 점은 `ADC-0024` 당시 지적되지 않았다), E6 IN-6′은 (a) 동일한 정적 import 검사에 더해 (b) **자료구조 부재**(class/큐 없음, AST)와 (c) **실행 메커니즘 자체의 계측**(자기 재귀 호출 검출 + 실측 콜스택 깊이)까지 확인했고, 이 두 축 모두에서 L-A와의 실측 대조를 포함한다.
- E6은 구현 과정에서 실제 결함(phase2 재개 시 Loop 재진입이 predecessor 검사를 통과하지 못함)을 IN-3′가 FAIL로 잡아냈고, 수정 후 재검증했다(E6 `EVIDENCE.md` §4). 이는 L-B가 "이름만 바꾼 재구현"이 아니라 **실제로 다른 스케줄링 표현**을 썼기 때문에 발생한 결함이라는 정황 증거이기도 하다 — L-A의 `self.start`(인스턴스 속성, 생애 전체에 걸쳐 매 pop마다 검사)와 L-B의 `starts`(재귀 인자로 매 호출에 전달)가 **같은 의미론을 다른 메커니즘으로 재현**해야 했다는 사실 자체가 두 계보의 구현이 독립적으로 이뤄졌음을 보여준다.
- 그러나 E5·E6 둘 다 **단일 프로세스·단일 언어(Python)·결정론적 stub**이며, 둘 다 동일한 `graph_spec`/predecessor-set(`_PREDS`) 데이터 파생 방식을 소비한다(스케줄링 **메커니즘**만 다르다 — 데이터 **모델**은 두 계보가 사실상 공유하는 개념이다, 코드 자체는 공유하지 않음).
- v2 프로덕션·실엔진 관찰은 여전히 **0건**.

---

## 3. Alternatives

### 3.1 "독립적 2번째 비-LangGraph 계보"의 인정 기준 (D-C1)

| | 기준 정의 | 판정 |
<br>
|---|---|---|
| **L-1** | 다른 프로세스/언어/런타임 경계까지 요구 | **Reject** — `ADC-0024` §D-B4(i) 예시("FSM / 코루틴 실행기 / 대안 라이브러리")가 이미 같은 Python 프로세스 안의 대안을 명시적으로 들었다. 프로세스·언어 경계까지 요구하는 것은 문언 초과 |
| **L-2** | 정적 import 목록·상호 import 0(E5 IN-6 수준)만으로 충분 | **Reject** — 이 기준만으로는 "이름만 바꾼 재구현"과 "실제로 다른 스케줄링 메커니즘"을 구분하지 못한다. E5 스스로도 `ADC-0024` §4.2에서 "3건 전부 stub/PoC"라는 견고성 우려를 남겼고, 계보 자체의 실질을 더 깊이 검증할 여지가 있었다 |
| **L-3 (채택)** | **자료구조 부재(인스턴스·큐 없음) + 실행 메커니즘의 계측 가능한 차이(자기 재귀 호출 등 정적 검출 + 실측값) + 코드 비공유**의 결합 | **Accept** — E6 IN-6′-1/2/3이 정확히 이 기준으로 설계·실증됐고, E5 IN-6보다 엄밀한 상위 기준이다. `ADC-0024` K-1 (d)("독립성은 계보 무의존·실행 모델 구조 차이·코드 비공유로 입증")의 정신을 계측 가능한 형태로 구체화한 것 — K-1을 뒤집지 않고 그 적용을 정련한다 |

### 3.2 Gate (B) 완전 완화 여부 (D-C2)

| | 판정 방향 | 근거 |
|---|---|---|
| **M-1** | **완전 완화(Conditional 해제)** — D-C1이 Yes이므로 `ADC-0024` §D-B4(i) 충족, Gate (B) 완전 해제 | **Reject** — `ADC-0019` §Risks는 "동일 계보"와 "v2 프로덕션 트래픽 아님"을 **별도의 두 우려**로 명시했다. E6은 전자만 두텁게 할 뿐 후자(프로덕션·실엔진 관찰)를 조금도 진전시키지 않는다. 두 우려 모두 해소돼야 "완전"이라 부를 수 있다는 것이 `ADC-0024` §4.2의 논리("3건 전부 stub/PoC"라 부분 완화에 그침)이며, 이 ADC는 그 논리를 그대로 계승한다 |
| **M-2** | **미충족 유지** — E6은 D-B4(i)를 충족하지 못했다고 판정 | **Reject** — §3.1 L-3 기준으로 D-C1은 Yes다. E6의 기여를 무시하는 것은 실측 Evidence(IN-6′-2/3)를 근거 없이 할인하는 것 |
| **M-3 (채택)** | **2차 부분 완화** — D-C1 Yes(비-LangGraph 계보 2개 확보, 독립성 검증 수준 E5 대비 강화)를 인정하되, 완전 완화는 보류. Gate (B)를 "형식 요건 충족(강화) / 견고성 조건 잔존(축소되었으나 잔존)"으로 재기술 | E6이 실제로 기여한 것(계보 다양성 심화)과 기여하지 않은 것(프로세스/언어 다양성, 프로덕션·실엔진 관찰)을 정확히 구분해 반영. `ADC-0024`가 E5에 대해 취한 것과 동일한 판정 형태(형식 요건 충족 + 부분 완화)를 E6에도 일관되게 적용 |

---

## 4. Analysis

### 4.1 D-C1 — E6은 L-3 기준으로 D-B4(i)를 충족한다

E6 `EVIDENCE.md` §3의 IN-6′-1/2/3은 세 층위에서 독립성을 실증한다:

1. **정적 의존성**(IN-6′-1) — `adapters/recursive.py`의 import root ⊆ `{__future__, copy, domain}`. `worklist`/`sequential`/`langgraph`/서드파티 0. E5 IN-6과 동일한 바를 충족.
2. **자료구조 부재**(IN-6′-2, 신설) — `class` 정의 0, `collections`(`deque`) import 0을 AST로 확인. **대조로 L-A(`worklist.py`) 소스를 텍스트로 읽어**(import 없음 — 런타임 결합 없음) 실제로 `class`+`deque`를 씀을 재확인했다. "L-B가 L-A의 이름만 바꾼 재구현"이라는 가설을 소스 구조 자체로 기각한다.
3. **실행 메커니즘 실측**(IN-6′-3, 신설) — `_advance`가 자기 자신을 재귀 호출함을 AST의 `Call` 노드로 검출했고, 3 시나리오 전부에서 **최대 콜스택 깊이 14**를 실측했다(그래프 실행 경로 길이 — fan-in 이후 debate 3라운드×3노드+trader+terminal 약 13~14단 — 에 비례). 동일 계측 방식을 L-A `run()`에 적용(가능하도록 설계됐다면)했을 때 그 함수는 `while` 루프를 포함하고 자기 자신을 재귀 호출하지 않음을 정적으로 확인했다.

E6 §4가 스스로 기록한 대로, 구현 중 IN-3′가 실제 FAIL을 낸 결함(phase2 재개 시 Loop 재진입 predecessor 검사 실패)은 L-A의 "인스턴스 속성 기반 영속 시작점"과 L-B의 "재귀 인자 기반 시작점"이 **동일 의미론을 다른 메커니즘으로 재현해야 했다**는 것을 보여주는 정황 증거다 — 우연히 같은 코드를 복사한 것이었다면 이런 종류의 결함이 발생하지 않았을 것이다.

이 세 층위는 `ADC-0024` K-1 (d)("독립성은 계보 무의존·실행 모델 구조 차이·코드 비공유로 입증")가 요구한 것을 **주장이 아니라 계측**으로 만족시킨다. 따라서 **D-C1 = Yes** — E6은 `ADC-0024` §D-B4(i)의 "2번째 비-LangGraph 독립 계보"를 충족한다.

### 4.2 D-C2 — 그러나 완전 완화는 아니다

`ADC-0019` §Risks는 두 우려를 **병렬로** 명시했다:

> "E1+E2가 모두 LangGraph 계보이고 v2 프로덕션 트래픽이 **아니라는 사실은 그대로 남는다**" — 완화책: "재검토 시 다른 계보 또는 v2 프로덕션 맥락의 독립 관찰 추가"

이 문장의 구조("다른 계보 **또는** v2 프로덕션")는 Gate (B) 재검토 조건 (c)의 형식 요건(3건 도달)에는 OR로 충분하지만, `ADC-0024` §4.2가 이미 지적했듯 "완전 완화"는 **형식 요건 충족과 다른 질문**이다 — 형식 요건은 (c)의 문언을 채우는 것이고, 완전 완화는 §Risks가 실제로 우려한 것(신뢰성)이 해소됐는지의 질문이다. `ADC-0024`는 E5 하나로 형식 요건을 채웠지만 "3건 전부 stub/PoC, 프로덕션 관찰 0"이라는 이유로 완전 완화를 보류했다. E6은:

- **계보 다양성**(L-3 기준의 "실행 메커니즘 차이")을 두텁게 한다 — 비-LangGraph 계보가 이제 2개.
- 그러나 **`ADC-0019` §Risks의 두 번째 우려(v2 프로덕션 트래픽)를 전혀 진전시키지 않는다** — E5·E6 둘 다 동일 프로세스·동일 언어·동일 결정론적 stub 환경이다.
- 나아가 두 계보는 **동일한 데이터 모델**(`graph_spec` + predecessor-set 파생)을 소비한다 — 차이는 그 데이터를 "어떻게 걷는가"(스케줄링 메커니즘)에 있다. 이는 실질적이고 계측 가능한 차이이지만, "완전히 독립적인 재구현 접근"이 갖는 이상적인 다양성(예: 다른 데이터 표현, 다른 언어, 다른 프로세스)에는 못 미친다.

따라서 이 ADC는 **M-3(2차 부분 완화)**을 채택한다: Gate (B)는 "형식 요건 충족(독립 관찰 4건 / 비-LangGraph 계보 2개, 계보 독립성 검증 수준 E5 대비 강화) / 견고성 조건 잔존(v2 프로덕션·실엔진 관찰 0, 두 비-LangGraph 계보 모두 동일 프로세스·언어·데이터 모델)"으로 재기술한다.

### 4.3 D-C3 — 완전 완화에 이르는 실질적 경로 (새 판단, `ADC-0024` 위에 정련)

`ADC-0024` §D-B4는 (i)·(ii)를 OR로 열거하며 "어느 것이 추가되면 재판정한다"고만 했다 — (i)의 반복이 완전 완화에 이르는지는 판단하지 않았다. 이 ADC는 실제로 (i)를 한 번 더 시도해본 결과를 근거로 다음을 판단한다:

**(i)의 반복(3번째, 4번째 비-LangGraph 계보 추가)만으로는 완전 완화에 이르지 못한다고 본다.** 이유: 동일 프로세스·언어·결정론적 stub 축 안에서 스케줄링 메커니즘만 다른 계보를 아무리 쌓아도 `ADC-0019` §Risks의 "v2 프로덕션 트래픽 아님" 우려는 조금도 줄지 않는다 — 그 우려는 계보 다양성과 독립적인 별개 축이다. 따라서 완전 완화에 이르는 실질적 경로는 사실상 **(ii) v2 프로덕션·실엔진 맥락 관찰**로 수렴한다.

이 판단은 정책적 판단이며 절대 규칙으로 못박지 않는다 — 예컨대 세 번째 계보가 **다른 프로세스나 언어 경계**를 실제로 넘는 형태(예: 별도 프로세스로 실행되는 실행기, subprocess IPC 기반 조정)라면 "동일 프로세스·언어" 우려의 일부를 진전시킬 수 있어 이 판단이 재검토될 수 있다. 다만 그런 계보는 지금 요구하지 않는다(§7 Out of Scope).

### 4.4 `ADC-0021` §8 AND 게이트와의 관계 — 변경 없음

`ADC-0021` §8 AND 게이트: 조건 1(LangGraph 고유 능력 필요, **미충족**·관찰 0) · 조건 2(Gate B) · 조건 3(Gate A, **충족**) · 조건 4(Gate C, **부분 충족**). 이 ADC는 조건 2를 "형식 요건 충족(강화) / 견고성 조건 잔존"으로 갱신할 뿐, 조건 1과 조건 4는 **전혀 건드리지 않는다** — E6은 결정론적 stub이며 Gate (C) 잔여 한계 (i)·(iii)를 해소하지 않고, LangGraph 고유 능력과 무관하다. `ADC-0021` §8의 "조건 2·3·4가 모두 충족되어도 조건 1이 없으면 Sequential Reference를 유지하는 것이 기본 결론" 문언 그대로다 — Gate (B)를 아무리 강화해도 조건 1이 열리지 않는 한 LangGraph 평가 ADC는 열리지 않는다.

---

## 5. Decision

**판정: Partial.**

E6/L-B는 `ADC-0024` §D-B4(i) "2번째 비-LangGraph 독립 계보"를 **실제로 충족한다**(D-C1 = Yes, §4.1) — E5보다 엄밀한 독립성 검증(자료구조 부재 + 실행 메커니즘 계측)으로 뒷받침된다. 그러나 이것이 Gate (B)의 **완전 완화(Conditional 해제)로 이어지지는 않는다**(D-C2 = No, §4.2) — `ADC-0019` §Risks의 두 우려 중 "동일 계보"만 두터워졌을 뿐 "v2 프로덕션 트래픽 아님"은 조금도 진전되지 않았기 때문이다. Gate (B)는 **2차 부분 완화** 상태로 재기술된다.

### D-C1. E6/L-B의 D-B4(i) 충족 여부

**충족한다.** §3.1 L-3 기준(자료구조 부재 + 실행 메커니즘의 계측 가능한 차이 + 코드 비공유)으로 판정하며, E6 IN-6′-1/2/3이 이를 실측으로 뒷받침한다:
- IN-6′-1(정적 의존성): E5와 동일한 바를 충족.
- IN-6′-2(자료구조 부재, 신설): `class`·`collections`/`deque` 0을 AST로 확인, L-A 소스에는 있음을 대조.
- IN-6′-3(실행 메커니즘 실측, 신설): 자기 재귀 호출을 AST로 검출 + 실측 최대 콜스택 깊이 14(그래프 실행 경로 길이에 비례) + L-A `run()`의 `while` 루프·비재귀 구조를 대조 확인.

### D-C2. Gate (B) 완전 완화 여부

**완전 완화 아님 — 2차 부분 완화로 재기술한다.**

1. **형식 요건 강화**: 독립 관찰 4건(E1·E2·E5·E6), 비-LangGraph 계보 **2개**(E5, E6). `ADC-0024`가 지목한 "동일 계보" 우려가 한 번 더 해소된다.
2. **견고성 조건 잔존**(축소되었으나 소멸하지 않음):
   - **v2 프로덕션·실엔진 맥락 관찰 여전히 0건** — E5·E6 둘 다 결정론적 stub/PoC. `ADC-0019` §Risks가 "동일 계보"와 별도로 명시한 우려.
   - **두 비-LangGraph 계보 모두 동일 프로세스·언어(Python)·데이터 모델**(`graph_spec`/predecessor-set) 소비 — 스케줄링 메커니즘만 다르다. "다른 계보"의 다양성은 이 축 안에서만 검증됐다.
3. **완전 완화(Conditional 해제)는 아니다**(M-1 Reject): 위 잔존 조건 + `ADC-0021` §8 조건 1·4 여전히 미충족·부분 충족.
4. **미충족 유지도 아니다**(M-2 Reject): E6은 D-B4(i)를 실제로 충족한다(D-C1 = Yes).

### D-C3. 완전 완화에 이르는 실질적 경로 (정련)

`ADC-0024` §D-B4(i)의 반복(3번째, 4번째 ... 비-LangGraph 계보 추가, 동일 프로세스·언어·stub 축 안에서)만으로는 완전 완화에 이르지 못한다고 판단한다. 완전 완화의 실질적 경로는 **(ii) v2 프로덕션·실엔진 맥락의 조건부 분기·Loop 실행 관찰 1건**으로 수렴한다(§4.3). 이는 정책적 판단이며, 프로세스/언어 경계를 실제로 넘는 형태의 계보가 추가되면 재검토될 수 있다.

### D-C4. 이 판정이 여는 것 / 열지 않는 것

- **연다**: `ADC-0021` §8 조건 2의 **형식 요건 강화**(독립 관찰 4건 / 비-LangGraph 계보 2개, E5 대비 엄밀한 독립성 검증)를 **기록**한다.
- **열지 않는다**:
  - Gate (B) 완전 완화 — §4.2·D-C2.
  - LangGraph 평가 ADC — `ADC-0021` §8 조건 1(미충족)·조건 4(부분 충족) 불변.
  - Gate (C) — 별도 gate, E6이 건드리지 않음.
  - Production 구현 착수 / `IMPLEMENTATION_RULES.md` 해제 / §14 승격.
  - 3번째 비-LangGraph 계보(L-C) 또는 v2 프로덕션 관찰의 착수 지시 — 필요성만 기록(§D-C3), 이 ADC가 요구하지 않는다.

### Reason

- **§4.1(D-C1)** — E6 IN-6′-2/3이 E5 IN-6보다 엄밀한 독립성 실증(자료구조 부재 + 실행 메커니즘 계측)을 제공했고, `ADC-0024` K-1 (d)의 정신을 계측 가능한 형태로 만족시킨다.
- **§4.2(D-C2)** — `ADC-0019` §Risks의 두 우려 중 하나만 진전됐다. `ADC-0024`가 E5 하나에 대해 취한 "부분 완화" 판정의 논리를 E6에도 일관되게 적용한다.
- **§4.3(D-C3)** — (i)의 반복은 "동일 계보" 축만 두텁게 할 뿐 "프로덕션·실엔진" 축을 진전시키지 못하므로, 완전 완화는 사실상 (ii)에 수렴한다.
- **§4.4** — `ADC-0021` §8 AND 게이트 조건 1·4는 이 ADC와 무관하게 그대로 미충족·부분 충족이다.

### Decision Rationale

이 Decision은 `ADC-0019`·`ADC-0021`·`ADC-0024`·`ADR-0010`·`ADR-0013`이 확정한 것을 뒤집지 않는다 — §16.6 존재·A-IN·A-OUT·Reversibility 필수 불변조건·Sequential Reference 기본선·AND 게이트·"부분 충족(E4)"·"형식 요건 충족/부분 완화(E5)"를 전부 전제로만 사용한다(§6). `ADC-0024` §D-B4가 "재판정이 가능하다"고 연 문을 이 ADC가 실제로 통과하며, 그 결과는 "형식 요건 강화 / 2차 부분 완화 / 완전 완화는 v2 프로덕션·실엔진 관찰 이후로 사실상 수렴"이다.

---

## 6. Conditions (유지 — 이 ADC가 약화하지 않음)

1. **`ADC-0019` §Decision 조건 1~6·재검토 조건 (a)(b)** 무변경 — (c)만 "형식 요건 충족(강화) / 견고성 조건 잔존(축소)"으로 재갱신.
2. **`ADC-0021` §8 AND 게이트** 무변경 — 조건 2만 갱신. 조건 1(미충족)·조건 3(충족)·조건 4(부분 충족)는 그대로. "조건 1 없으면 Sequential Reference 유지" 기본 결론 유지.
3. **`ADR-0010` "부분 충족"** 무변경 — Gate (C) E4 잔여 한계 (i)~(iii)·완전 discharge 미선언 유지. E6은 Gate (C)를 진전시키지 않는다.
4. **`ADC-0024`·`ADR-0013`의 Gate (B) "형식 요건 충족/부분 완화" 판정 자체는 뒤집지 않는다** — 이 ADC는 그 위에 E6을 더해 형식 요건을 강화할 뿐, E5/`ADC-0024`의 판정을 재론하지 않는다.
5. **§14 미승격 / Production 구현 차단 / `IMPLEMENTATION_RULES.md` 유지** — 어느 것도 해제하지 않는다.
6. **Sequential Reference 기본선**(`ADC-0021` §D1) 무변경.

---

## 7. Out of Scope

| 항목 | 근거 |
|---|---|
| Gate (C) 판정 / `ADR-0010` 재판정 | 별도 gate, E6이 건드리지 않음 |
| `ADC-0021` §8 조건 1(LangGraph 고유 능력 필요) 판정 | E6과 무관, 관찰 0건 그대로 |
| LangGraph 채택 / 평가 ADC 개설 | 조건 1·4 미충족·부분 충족 |
| Production 구현 착수 / `IMPLEMENTATION_RULES.md` 해제 / §14 승격 | Gate (B) 2차 부분 완화가 어느 것도 해제하지 않음 |
| 3번째 비-LangGraph 계보(L-C) 또는 v2 프로덕션 관찰 확보의 착수 지시 | §D-C3 — 실질적 경로로 지목만, 착수 지시 아님 |
| `BASELINE.md` §16.6 / `GLOSSARY.md` 문언 편집 | 후속 ADR |
| `ADC-0019`/`ADC-0021`/`ADC-0024`/`ADR-0010`/`ADR-0013` 원문 편집 | Gate (B)의 새 상태는 §16.6 cross-reference로만 |

---

## 8. 후속 ADR에서 반영할 사항 (Baseline 지침)

후속 ADR(Minor 예상, `ADR-0010`/`0013`류 granularity)이 `BASELINE.md` §16.6과 `GLOSSARY.md`에 아래를 반영한다. 그 외 절·문언은 무변경.

1. **§16.6 "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)" 문단**(`ADR-0013`이 부기한 3문장 뒤)에 추가 부기 — 요지: "`ADC-0019` 재검토 조건 (c)(= Gate (B))에 2번째 비-LangGraph 독립 계보(E6, `projects/workflow-adapter-recursive-lineage-v1/` 재귀 조합자 L-B, IN-1′~IN-6′ 31 PASS)가 추가됐다(`ADC-0025`). 독립 관찰은 4건(비-LangGraph 계보 2개)으로 강화됐으나, v2 프로덕션·실엔진 관찰은 여전히 0건이므로 Conditional 성격은 **2차 부분 완화**에 그친다 — 완전 완화는 v2 프로덕션 맥락의 조건부 분기·Loop 실행 관찰 이후 재판정한다(`ADC-0025` §D-C3). 이 부분 완화는 Gate (C)나 `ADC-0021` §8 조건 1을 해소하지 않으며, LangGraph 평가 ADC·Production 구현 착수·§14 승격 중 무엇도 열지 않는다."
2. **`GLOSSARY.md` "Workflow Adapter (Reference)" 절 주석 1문장 정정** — `ADR-0013`이 정정한 문장에 "비-LangGraph 계보 2개(E5, E6)로 강화, 완전 완화는 미충족" 취지 반영.
3. **Version**: v1.17 → v1.18(Minor 예상), Frozen 유지.
4. **명시적 비변경**: §16.6 A-IN/A-OUT·Reversibility 필수 불변조건 문단·Adapter Contract (a)(b)(c)(d) bullet·"실행 단위"·"실행 단위 Lifecycle" 문단, §5·§6·§7·§11·§14·§14.1 표·§16.1~§16.5·§16.7, `IMPLEMENTATION_RULES.md`, `ADC-0019`/`ADC-0021`/`ADC-0024`/`ADR-0010`/`ADR-0013` 원문.

---

## 9. Architecture / Governance Review

### 9.1 Governance Chain 정합성

| 점검 | 결과 |
|---|---|
| 선행(`ADC-0019`·`ADC-0021`·`ADC-0024`·`ADR-0010`·`ADR-0013`)이 확정한 것을 뒤집는가 | **아니오** — §16.6 존재·Reversibility 불변조건·Sequential Reference 기본선·AND 게이트·"부분 충족(E4)"·"형식 요건 충족/부분 완화(E5)"를 전제로만 사용(§6) |
| `ADC-0024` §D-B4의 "재판정이 가능하다"를 수행하는가 | **예** — (i) 추가를 확인하고 완전 완화 여부를 실제로 재판정(D-C2). 자동 완화 아님 |
| `ADC-0024` §D-B4(i)·(ii)의 OR을 준수하는가 | **예** — (i)만으로는 완전 완화에 이르지 못한다는 판단을 새로 도출했을 뿐, (ii) 요건을 부당하게 추가한 것이 아니다 — §Risks 원문의 두 우려를 그대로 적용한 결과다(§4.2) |
| `ADC-0021` §8 AND 게이트를 우회하는가 | **아니오** — 조건 2만 갱신, 조건 1·4 미충족·부분 충족으로 LangGraph 평가 ADC 불가 명시(§4.4) |
| `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ADC Accept를 발생시키지 않는다" | **준수** — E6은 §5 판정의 입력. LangGraph 채택·구현을 발생시키지 않음 |

### 9.2 경계 — 선행 확장 여부

| 점검 | 결과 |
|---|---|
| 새 Architecture 책임·Layer·Component·Concept·Contract를 추가하는가 | **아니오** — Gate (B) 상태 판정만 |
| §14 / §14.1 / §16.6 A-IN·A-OUT / Adapter Contract를 건드리는가 | **아니오** — §8이 후속 ADR로 §16.6 문단 부기만 지시 |
| Gate (C) / LangGraph 채택 / Production / `IMPLEMENTATION_RULES.md`를 진전시키는가 | **아니오** — §7 Out of Scope |
| 3번째 비-LangGraph 계보(L-C) 또는 v2 프로덕션 관찰 착수를 요구하는가 | **아니오** — §D-C3은 방향 지목일 뿐 착수 지시가 아님(§7) |
| `BASELINE.md`·`GLOSSARY.md`·기존 ADC/ADR을 이 ADC가 편집하는가 | **아니오** — 이 ADC 파일 1건만 신규 작성(미커밋) |

### 9.3 사용자 지시 준수

| 지시 | 준수 |
|---|---|
| E6가 `ADC-0024` §D-B4의 "2번째 독립 비-LangGraph 계보" 조건을 실제로 충족하는지, E5/L-A와의 독립성 Evidence 기준으로 판단 | **준수** — D-C1(§4.1), L-1/L-2/L-3 비교(§3.1) |
| Gate B Full Relaxation 여부 명시, Gate C(i)/(iii)와 조건 1은 별도 잔존 조건으로 유지 | **준수** — D-C2(완전 완화 아님), §6 조건 3·2, §4.4가 조건 1·Gate (C)를 명시적으로 무변경 유지 |
| `BASELINE`/`GLOSSARY`/기존 ADC·ADR 아직 미변경, ADC-0025 자체의 Architecture/Governance Review까지 수행 | **준수** — §7 Out of Scope, §8은 지침만(미실행), 이 §9가 Review |
| 최종 판단(Decided/Rejected/Partial)과 근거, 이후 필요한 최소 Governance migration 보고 | **준수** — §5 "판정: Partial", §8 최소 Migration 지침 |

### 9.4 판정

**PASS.** 이 ADC는 `ADC-0019` 조건 1~6·재검토 조건 (a)(b), `ADC-0021` §8 AND 게이트(조건 1·3·4), `ADC-0024`·`ADR-0013`의 Gate (B) 판정, `ADR-0010` "부분 충족", Rule B 전체 미충족, `IMPLEMENTATION_RULES.md` 금지, Sequential Reference 기본선을 **하나도 약화하지 않는다**(§6). Gate (B)를 "형식 요건 충족(강화) / 견고성 조건 잔존(축소)"으로 2차 부분 완화하되, 완전 완화·LangGraph 평가 ADC·Gate (C)·Production·§14 승격을 열지 않는다(§7·D-C4).

**Next Step**: ADR Required — §8 지침으로 §16.6·`GLOSSARY.md`에 Gate (B) 2차 부분 완화 상태를 반영(Minor, v1.17 → v1.18). Commit/PR/Merge는 사용자 보고 후.

---

## 10. Traceability

| 문서 / 절 | 관계 |
|---|---|
| `ADC-0024` §D-B4(i) | 이 ADC가 판정하는 대상. "완전 완화 재판정 가능"을 실제로 수행 |
| `ADC-0021` §8 조건 2·AND 게이트 | Gate (B) = 조건 2. 조건 1·3·4는 무변경(§4.4) |
| `ADR-0013`(Gate (B) "형식 요건 충족/부분 완화", BASELINE v1.17) | 이 ADC가 이어받는 직전 상태. 뒤집지 않고 강화만 |
| `ADR-0010`(Gate (C) "부분 충족") | 무변경 — E6이 건드리지 않음 |
| E5 `projects/workflow-adapter-nonlanggraph-lineage-v1/EVIDENCE.md`(IN-6) | D-C1의 비교 기준선(§3.1 L-2) |
| E6 `projects/workflow-adapter-recursive-lineage-v1/EVIDENCE.md`(IN-1′~IN-6′) | D-C1·D-C2의 직접 근거 |
| `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" | E6의 레인. Evidence는 판정 입력이지 자동 Accept 아님 |

---

## 11. Self-Review

- `ADC-0019`·`ADC-0021`·`ADC-0024`·`ADR-0010`·`ADR-0013`이 확정하지 않은 것을 새로 결정했는가 — **E6의 D-B4(i) 충족 여부 + Gate (B) 완전 완화 여부만**. Gate (C)·조건 1·LangGraph 채택·Production·§14 승격은 §7 Out of Scope.
- E6이 D-B4(i)를 충족하는지 판단했는가 — **예**(D-C1 = Yes, §4.1) — E5보다 엄밀한 독립성 실증(자료구조 부재 + 실행 메커니즘 계측)에 근거.
- Gate B Full Relaxation을 명시했는가 — **예**(D-C2 = No) — "2차 부분 완화"로 명확히 재기술, 완전 완화와 구분.
- Gate C(i)/(iii)와 `ADC-0021` §8 조건 1을 별도 잔존 조건으로 유지했는가 — **예**(§4.4, §6 조건 2·3) — 이 ADC와 무관하게 그대로 미충족·부분 충족임을 명시.
- `BASELINE.md`·`GLOSSARY.md`·기존 ADC/ADR을 변경했는가 — **아니오**. 이 ADC 파일 1건만 신규 작성(미커밋).
- 이 ADC 자체의 Architecture/Governance Review를 수행했는가 — **예**(§9), 판정 = PASS.
- 최종 판단(Decided/Rejected/Partial)을 명시했는가 — **예**(§5 "판정: Partial").
- 이후 필요한 최소 Governance migration을 제시했는가 — **예**(§8) — Minor ADR 1건, BASELINE v1.17→v1.18 + GLOSSARY 1문장 정정만.
- 새 실험/PoC를 수행했는가 — **아니오**(§1.3) — `main` 병합 Evidence(E4/E5) + 세션 내 기 실행된 E6만 인용.
- Commit/PR/Merge를 했는가 — **아니오** — Status는 Decided이나 `BASELINE.md`·`GLOSSARY.md`·ADR은 미착수. 사용자 승인 후 진행(`main` 직접 금지).
