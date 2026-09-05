# ADC-0024: Gate (B) — `ADC-0019` 재검토 조건 (c) "독립 관찰 3건" 충족 여부 판정 (E1·E2·E5/L-A)

**Status**: Decided — ADR Required (예상 `ADR-0013`). Architecture/Governance Review PASS(§9, 최종 재검토 포함 — `ADC-0019` (c) 문언·`ADC-0021` §8 조건 2와 K-1/E5 Partial 판정의 정합성 확인, 신규·범위 초과 결정 없음). `BASELINE.md`·`GLOSSARY.md`·ADR 미착수, Commit/PR/Merge 없음. 사용자 승인 후 진행(`ADR-0011`/`ADR-0012` 선례).
**Author**: Claude Code
**선행 체인**: `RFC-0019`→`ADC-0019`→`ADR-0008` (§16.6 존재 Accept·Scoped·Conditional; §Risks·재검토 조건 (c) = "다른 계보 또는 v2 프로덕션 관찰로 독립 관찰 3건") → `ADC-0021` §8 (Gate (A)/(B)/(C) 명명; §8 조건 2 = 재검토 조건 (c)) → `ADR-0010` (Gate (C) E4 "부분 충족") → `ADC-0022`·`ADC-0023`→`ADR-0011`·`ADR-0012` (Gate (A) 전체 Resolved, BASELINE v1.16)
**RFC pairing**: `ADC-0019` §Risks·재검토 조건 (c) + `ADC-0021` §8 조건 2 — 이 두 절이 이 ADC의 판정 대상이자 트리거다(`ADC-0021`이 `RFC-0020` §8.2를 RFC pairing으로 삼은 것과 동일 관계). `ADC-0019` 재검토 조건 (c)가 "재검토는 RFC → ADC → ADR 절차를 따른다"고 명시하므로, 절차 엄격성을 우선한다면 얇은 `RFC-0023`이 선행할 수 있다 — 이 ADC는 형식 요건 충족 여부와 완화 정도만 판정하고 §16.6 문언을 건드리지 않으므로 `ADC-0021` 선례(선행 RFC 없이 상위 문서 절을 pairing)를 따르되, RFC-0023 선행 여부는 사용자 판단으로 남긴다.
**대상**: `ADC-0021` §8 Gate **(B)** = `ADC-0019` 재검토 조건 (c)의 형식 요건("LangGraph와 다른 계보 또는 v2 프로덕션 맥락의 조건부 분기·Loop 실행 관찰이 추가되어 독립 관찰 3건에 도달") 충족 여부와, Conditional 성격 완화의 정도.

> 이 ADC는 **Gate (B) 인정 기준(무엇이 "독립 관찰 3건"인가)과 E5/L-A의 실제 기여도만** 판정한다. LangGraph 채택을 평가하지 않는다(`ADC-0021` §8 조건 1·4 별개). Production 구현 착수·`IMPLEMENTATION_RULES.md` 해제·§14 승격을 결정하지 않는다. Gate (C)를 판정하지 않는다(별도 gate — E5는 C(ii)만 부분 진전). **L-B(2번째 비-LangGraph 계보)를 구현하도록 요구하지 않는다** — 필요 여부만 후속 조건으로 기록한다. `BASELINE.md` §16.6 문언은 후속 ADR이 갱신한다.

---

## 1. 목적과 경계

### 1.1 이 ADC가 판단하는 것 (둘)

| # | 판단 항목 | 근거 위임 |
|---|---|---|
| **D-B1** | **Gate (B) 인정 기준** — `ADC-0019` 재검토 조건 (c)의 "독립 관찰 3건"이 무엇을 요구하는지 정련(관찰의 독립성·조건부 분기·Loop 실제 실행·"다른 계보 또는 v2 프로덕션" OR 분기) | `ADC-0019` §Risks·재검토 조건 (c), `ADC-0021` §8 조건 2·"1회 관찰 불인정" 기준 |
| **D-B2** | **E5/L-A의 실제 기여도** — E5가 bona fide 독립 비-LangGraph 관찰인지, "동일 계보" 형식 우려를 해소하는지, Conditional 성격을 어느 정도 완화하는지 | `projects/workflow-adapter-nonlanggraph-lineage-v1/EVIDENCE.md` (IN-1~IN-6, 25/25 PASS), E4 `EVIDENCE.md` §4·§5, `ADC-0019` §Risks |

### 1.2 이 ADC가 판단하지 않는 것 (경계)

- **LangGraph 채택 / 평가 ADC 개설** — `ADC-0021` §8 AND 게이트의 조건 1(LangGraph 고유 능력 필요의 반복 관찰) 미충족, 조건 4(Reversibility v2 완전 검증) 부분 충족(E4). Gate (B) 판정이 이를 열지 않는다.
- **Gate (C) 판정 / `ADR-0010` "부분 충족" 재판정** — 별도 gate. E5는 C(ii)(대조 어댑터 LangGraph 단일 계보)만 부분 진전, C(i)(결정론적 stub)·C(iii)(프로덕션 트래픽)은 미해소.
- **Production 구현 착수 / `IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19 해제 / §14 승격** — 결정 9 해소(BASELINE v1.16)와 무관하게 Gate (B)·(C)·조건 1로 계속 차단.
- **L-B(2번째 비-LangGraph 계보) 구현 요구** — 필요 여부만 후속 조건으로 기록.
- **`BASELINE.md` §16.6 "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)" 문단 / `GLOSSARY.md` 편집** — 후속 ADR.
- **`ADC-0019`·`ADC-0021` 원문 편집** — Gate (B)의 새 상태는 후속 ADR의 §16.6 cross-reference로만 반영.

### 1.3 새 실험 없음

이 ADC는 `main`(`7b71fed`)에 병합된 Evidence(E4 `projects/workflow-adapter-reversibility-v2/`, E5 `projects/workflow-adapter-nonlanggraph-lineage-v1/`)와 Governance 문서(`ADC-0019`, `ADC-0021`, `ADR-0010`, `BASELINE.md` v1.16, `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`), v1 Evidence(`archive/v1/.../test_workflow_adapter_reversibility.py`), 세션 PoC 기록(`.claude/docs/integrations/langgraph.md`)만 인용한다. 새 PoC·측정을 수행하지 않는다.

---

## 2. Evidence

| # | Evidence | 계보 | 맥락 | 조건부 분기·Loop 실행 |
|---|---|---|---|---|
| **E1** | v1 `ADR-0007` (Accepted) — LangGraph를 `IWorkflowEngine` 구현체로 실사용 + `archive/v1/tests/integration/test_workflow_adapter_reversibility.py` (LangGraph↔Sequential 교체 무수정) | LangGraph | v1 실사용·통합 테스트 (v2 아님, `ADC-0019` G2 cross-arch 부분 할인) | 병렬 fan-out/fan-in 실측(결정 7). 조건부 분기·수렴 Loop는 v1 도메인 범위 |
| **E2** | RFC-0019 세션 PoC (`.claude/docs/integrations/langgraph.md`) — `langgraph` 1.2.11, State→Node→Conditional Edge→Loop→종료(4회 반복 후 종료), `MemorySaver` 중단/재개 | LangGraph | 저장소 밖 임시 디렉터리 PoC (프로덕션 트래픽 아님) | 조건부 Edge + Loop 4회 실행, checkpoint 재개 확인 |
| **E3** | Architecture Intent (`BASELINE.md` §6·§7) | — | 문서 서술 | **관찰 아님** — Rule B / (c) 카운트 대상 아님 |
| **E4** | `projects/workflow-adapter-reversibility-v2/` — Sequential Reference ↔ **LangGraph 대조**, IN-1~IN-5 22 PASS. `ADR-0010` "부분 충족" | LangGraph (대조축) | in-repo, 결정론적 stub | 조건부 라우팅 + 토론 Loop 3라운드. **`ADC-0019` 재검토 조건 (c) 미충족 명시**(EVIDENCE §4 한계 2) |
| **E5 / L-A** | `projects/workflow-adapter-nonlanggraph-lineage-v1/` — **worklist 인터프리터**(`adapters/worklist.py`, 170 LOC, import = `{__future__, collections, copy, domain}`), IN-1~IN-6 25 PASS. `run_full(worklist) == run_full(langgraph)` 3 시나리오 | **비-LangGraph** (stdlib worklist) | in-repo, 결정론적 stub, seam = harness 로컬 관례 | **조건부 분기 두 갈래(`clean`→report / `data_gap`→escalate) + 수렴 Loop 3회(`BULL r0/r1/r2`, `debate_round==3`) 실제 실행** (IN-1 behavior record). node_error catch-and-encode |
| **E5 IN-6** | 계보 독립성 강제 — AST 검사로 L-A import root ⊆ stdlib+domain; docstring이 E4 `sequential.py`(하드코딩 절차)·`langgraph.py`(`StateGraph.compile()`+superstep)와의 실행 모델 차이 명문화; L-A↔L-LG 상호 import 0 | — | — | L-A가 "대조와 co-design된 reference floor"가 아니라 구조적으로 독립인 실행 계보임을 테스트로 고정 |

**"E3" 라벨 충돌 주의**: `ADC-0019` §Evidence의 E3 = **"Architecture Intent"**(`BASELINE.md` §6·§7 서술 — 관찰 아님, `ADC-0019` §G1이 "독립 관찰은 사실상 2건(E1+E2)"로 명시). `ADC-0021` §8·§Traceability의 E3 = **`.claude/docs/integrations/langgraph-domain-poc.md`**(도메인 형태 LangGraph PoC — `ADC-0021`이 "E1/E2/E3는 전부 LangGraph 계보"로 카운트). 이 ADC는 두 라벨을 구분해 인용한다.

**핵심 사실 (두 카운팅 모두에서 형식 요건 충족)**:
- **`ADC-0019` 카운팅**: 독립 관찰 2건(E1+E2, 전부 LangGraph) + E5/L-A = **3건**.
- **`ADC-0021` §8 카운팅**: 독립 관찰 3건(E1·E2·E3=langgraph-domain-poc, 전부 LangGraph) + E5/L-A = **4건**.
- **어느 카운팅에서도**: E5/L-A는 **첫 비-LangGraph 관찰**이며, `ADC-0021` §8이 미충족 원인으로 특정한 "E1/E2/E3는 전부 LangGraph 계보" 상태가 **해소**된다. 독립 관찰은 3건 이상으로 유지된다.
- v2 프로덕션 맥락 관찰: **0건** (E1은 v1, E2·E3(langgraph-domain-poc)·E4·E5는 PoC/experimental).
- 결정론적 stub 아닌 관찰(실엔진·실트래픽): **0건**.
- 비-LangGraph 계보: **1개(L-A)뿐**.

---

## 3. Alternatives

### 3.1 "독립 관찰 3건"의 인정 기준 (D-B1)

| | 기준 정의 | 판정 |
|---|---|---|
| **K-1 (채택)** | (a) 서로 다른 실행 맥락 **3건** + (b) 각 관찰이 조건부 분기·Loop를 **실제 실행** + (c) 그중 **최소 1건**이 "LangGraph와 다른 계보" **또는** "v2 프로덕션 맥락" (재검토 조건 (c)의 OR 그대로) + (d) 각 관찰이 재사용 대조가 아닌 **독립적**(co-design된 reference floor는 별건으로 카운트 불가 — E5 IN-6이 이 독립성을 강제) | **Accept** — `ADC-0019` 재검토 조건 (c) 문언 + `ADC-0021` §8 "1회 관찰 불인정" 기준의 정합 해석. 형식 요건이지 견고성 판정이 아님(§3.2 참조) |
| **K-2** | "3건" = LangGraph 아닌 관찰 **3건** | **Reject** — 재검토 조건 (c)는 "다른 계보 또는 v2 프로덕션 관찰이 **추가되어** 독립 관찰 **3건**에 도달"이다. 기존 관찰(E1·E2)을 무효화하지 않는다. 3건 전부 비-LangGraph를 요구하면 문언 초과 |
| **K-3** | "3건" 도달 시 Conditional 성격이 **자동 완화** | **Reject** — 재검토 조건 (c)는 "재판단이 **가능하다**"이지 자동이 아니다. 이 ADC가 완화 정도를 판정한다(§3.2) |

### 3.2 Conditional 성격 완화의 정도 (D-B2)

| | 판정 방향 | 근거 |
|---|---|---|
| **R-1 (채택)** | **부분 완화** — 형식 요건(K-1) 충족 + "동일 계보" 형식 우려 해소로 갱신하되, "v2 프로덕션·실엔진 관찰 0 / 비-LangGraph 계보 1개"는 그대로. Gate (B)를 "형식 요건 충족 / 견고성 조건 잔존"으로 재기술 | E5/L-A는 bona fide 독립 비-LangGraph 관찰(§4.2). 그러나 3건 전부 결정론적 stub·PoC, 프로덕션 관찰 0(`ADC-0019` §Risks의 "견고하게 만든다" 목표 부분 달성) |
| **R-2** | **완전 완화** — Gate (B) 충족, Conditional 해제 | **Reject** — 3건이 전부 stub/PoC이고, `ADC-0019` §Risks가 "v2 프로덕션 트래픽 아님"을 별도 우려로 명시했으며, E5 EVIDENCE §5가 "(c) 충족을 선언하지 않음"으로 자기 한정. `ADC-0021` §8 조건 1·4도 미충족이라 완전 완화는 다음 단계를 열지 않으면서 gate 문언만 약화 |
| **R-3** | **미충족 유지** — E5가 stub 수준이므로 (c) 진전 없음 | **Reject** — 재검토 조건 (c)는 "다른 계보 **또는** v2 프로덕션"의 OR다. E5/L-A는 "다른 계보"를 실제로 채운다(§4.2, IN-6). "다른 계보" 요건에 "프로덕션 수준"을 덧붙이면 (c) 문언 재작성 |

---

## 4. Analysis

### 4.1 D-B1 — 인정 기준 (K-1)

`ADC-0019` 재검토 조건 (c)는 **형식 요건**이다: "독립 관찰 3건에 도달". `ADC-0021` §8은 이를 조건 2로 두고 "E1/E2/E3는 전부 LangGraph 계보이므로 이를 채우지 못한다"고 했다 — 즉 미충족의 지목된 원인은 **계보 단일성**이다(관찰 수 자체는 `ADC-0021` §8 카운팅에서 이미 3건이었다). 따라서 (c)를 채우려면 "다른 계보 또는 v2 프로덕션" 관찰이 **최소 1건** 추가되어야 하며, 그때 독립 관찰이 3건 이상이면서 더 이상 단일 계보가 아니게 된다(K-1 (a)(c)).

- (b) **조건부 분기·Loop 실제 실행**: (c) 문언이 "조건부 분기·Loop 실행 관찰"이라고 못박았다. 서술이나 컴파일만으로는 부족하다 — 관찰은 그래프가 실제로 분기하고 반복해야 한다.
- (d) **독립성**: co-design된 reference floor(E4의 Sequential이 그런 성격)는 "LangGraph와 동치"를 보이는 대조축일 뿐 그 자체가 독립 관찰로 카운트되기 약하다. E5는 이 문제를 IN-6으로 정면 대응했다 — L-A의 import를 stdlib+domain으로 제한하고, 실행 모델의 구조적 차이를 docstring에 명문화하고, L-A↔L-LG 코드 비공유를 테스트로 강제했다.
- "1회 관찰 불인정"(`ADC-0021` §8 조건 1): 이 기준은 조건 1(LangGraph 고유 능력 필요)에 대한 것이나, 정신은 (c)에도 적용된다 — 단일 인스턴스는 약하다. (c)가 "3건"을 요구하는 이유가 그것이다. 현재 3건에 도달했다.

### 4.2 D-B2 — E5/L-A의 기여 (R-1)

**E5/L-A는 bona fide 독립 비-LangGraph 관찰이다**:
- 계보: `adapters/worklist.py`는 `langgraph`/`langchain`/서드파티 무의존(IN-6 AST 검사). `graph_spec`을 데이터로 해석하는 ready-queue worklist 인터프리터로, E4 `sequential.py`(하드코딩된 `_phase1()`/`_phase2()` 절차)와도, LangGraph(`StateGraph.compile()` + Pregel superstep)와도 구조적으로 다르다.
- 조건부 분기·Loop 실제 실행: IN-1 behavior record가 `clean`→report / `data_gap`→escalate 두 갈래, `BULL r0/r1/r2` (Loop 본문 3회), `debate_round==3`, node_error catch-and-encode를 확인. 3 시나리오 전부 `run_full(worklist) == run_full(langgraph)` (dict deep-equal).
- in-repo 검증: IN-1~IN-6 25/25 PASS. 교체 무영향(IN-4), 라이브러리 격리(IN-5)까지 E4 구조 계승.

**"동일 계보" 형식 우려 해소**: `ADC-0021` §8이 지목한 "E1/E2/E3는 전부 LangGraph 계보" 상태가 깨진다 — 3건 중 1건(E5/L-A)이 비-LangGraph다.

**그러나 완전 완화(R-2)에는 이르지 않는다**:
- 3건 전부 결정론적 stub / PoC 수준이다. E1은 v1(v2 아님), E2·E4·E5는 experimental. **v2 프로덕션 트래픽 관찰은 0건**이며, `ADC-0019` §Risks가 이를 "동일 계보"와 **별도의** 우려로 명시했다("E1+E2가 모두 LangGraph 계보이고 v2 프로덕션 트래픽이 **아니라는 사실은 그대로 남는다**").
- 비-LangGraph 계보는 L-A **1개**뿐이다. "다른 계보"의 견고성(여러 독립 메커니즘에서 재현)은 부분적이다.
- E5 EVIDENCE §5가 스스로 "(c) 충족을 선언하지 않음 / 3건 카운팅·1건으로 충분한지는 후속 ADC"로 한정했다 — 이 ADC가 그 판정이며, 위 두 잔존 우려 때문에 부분 완화로 판정한다.

### 4.3 `ADC-0021` §8 AND 게이트와의 관계

`ADC-0021` §8은 LangGraph 평가 ADC의 진입을 4조건 AND로 걸었다:
1. LangGraph 고유 능력 필요의 반복 관찰 — **미충족** (관찰 0).
2. `ADC-0019` 재검토 조건 (c) = Gate (B) — **이 ADC로 형식 요건 충족 / 견고성 조건 잔존**.
3. v1 `ADR-0007` 결정 2/5/9/11 v2 공백 해소 — **충족** (`ADC-0022`·`ADC-0023` → BASELINE v1.16).
4. Reversibility v2 in-repo 통합 테스트 재현 — **부분 충족** (E4, `ADR-0010`).

→ 조건 1이 미충족이고 조건 4가 부분 충족이므로, **Gate (B)를 부분 완화해도 LangGraph 평가 ADC는 열리지 않는다.** `ADC-0021` §8의 "역으로 조건 2·3·4가 모두 충족되어도 조건 1이 없으면 Sequential Reference를 유지하는 것이 기본 결론" 문언 그대로다.

---

## 5. Decision

**A. Accept — Gate (B) 형식 요건 충족 / Conditional 성격 부분 완화.**

### D-B1. "독립 관찰 3건"의 인정 기준 (K-1)

`ADC-0019` 재검토 조건 (c)의 "독립 관찰 3건"은 다음을 요구한다:

1. 서로 다른 실행 맥락의 관찰 **3건**.
2. 각 관찰이 조건부 분기·Loop를 **실제 실행**한다(서술·컴파일만으로는 불인정).
3. 그중 **최소 1건**이 "LangGraph와 다른 계보" **또는** "v2 프로덕션 맥락"이다(재검토 조건 (c)의 OR 그대로).
4. 각 관찰이 재사용 대조가 아닌 **독립적**이다 — co-design된 reference floor는 그 자체로 독립 관찰이 아니며, 독립성은 계보 무의존·실행 모델 구조 차이·코드 비공유로 입증한다(E5 IN-6 패턴).

"3건"은 비-LangGraph 3건을 뜻하지 않는다 — 기존 LangGraph 관찰(E1·E2)은 무효화되지 않는다(K-2 Reject). "3건 도달"은 Conditional 자동 완화가 아니라 재판단을 **가능하게** 한다(K-3 Reject).

### D-B2. E5/L-A의 기여도와 Gate (B) 상태

1. **E5/L-A = bona fide 독립 비-LangGraph 관찰**: worklist 인터프리터(stdlib+domain 무의존, IN-6), 조건부 분기 두 갈래 + 수렴 Loop 3회 실제 실행(IN-1 behavior record), `run_full(worklist) == run_full(langgraph)` 3 시나리오, IN-1~IN-6 25/25 PASS.
2. **형식 요건 충족**: 관찰 3건(E1 + E2 + E5/L-A) 도달, 그중 1건(E5/L-A)이 "LangGraph와 다른 계보". `ADC-0021` §8이 지목한 "E1/E2/E3 전부 LangGraph 계보" 상태 — **해소**.
3. **Conditional 성격 = 부분 완화** (R-1): Gate (B)를 "**형식 요건 충족(독립 관찰 3건 / 다른 계보 1건 확보) / 견고성 조건 잔존**"으로 재기술한다. 잔존 조건:
   - **v2 프로덕션·실엔진 맥락 관찰 0건** — 3건 전부 결정론적 stub / PoC. `ADC-0019` §Risks가 "동일 계보"와 별도로 명시한 우려.
   - **비-LangGraph 계보 1개(L-A)뿐** — "다른 계보"의 견고성 부분적.
4. **완전 완화(Conditional 해제)는 아니다** (R-2 Reject): 위 잔존 조건 + `ADC-0021` §8 조건 1·4 미충족.
5. **미충족 유지도 아니다** (R-3 Reject): E5/L-A는 "다른 계보" OR 분기를 실제로 채운다.

### D-B3. 이 판정이 여는 것 / 열지 않는 것

- **연다**: `ADC-0021` §8 조건 2의 **형식 요건**(독립 관찰 3건 이상 / 그중 최소 1건이 "다른 계보" — E5/L-A로 충족)과 "E1/E2/E3 전부 LangGraph 계보" 상태의 해소를 **기록**한다. 조건 2가 LangGraph 평가를 지지하는 수준으로 완전 충족되는지(Conditional 완전 완화)는 조건 1·4 미충족으로 지금 판단하지 않는다 — AND 게이트가 그 판단 없이도 닫혀 있기 때문이다.
- **열지 않는다**:
  - LangGraph 평가 ADC — `ADC-0021` §8 조건 1(고유 능력 필요 반복 관찰) 미충족, 조건 4(Reversibility v2 완전 검증) 부분 충족. Sequential Reference 기본선 유지.
  - Gate (C) — 별도 gate. E5는 C(ii)만 부분 진전, C(i)·C(iii) 미해소.
  - Production 구현 착수 / `IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19 해제 / §14 승격.

### D-B4. L-B (2번째 비-LangGraph 계보) — 후속 조건 (구현 요구 아님)

Gate (B)의 **완전 완화**(Conditional 해제)는 다음 중 하나가 추가될 때 재판정한다:
- (i) 2번째 비-LangGraph 독립 계보 관찰(예: FSM / 코루틴 실행기 / 대안 라이브러리 — L-B), **또는**
- (ii) v2 프로덕션 맥락(실제 HQ 트래픽)의 조건부 분기·Loop 실행 관찰 1건.

**이 ADC는 (i)·(ii) 중 어느 것도 지금 구현·수행하도록 요구하지 않는다.** 착수 여부·시점·형태는 이 ADC가 정하지 않는다.

### Reason

- **§4.1 (D-B1)** — `ADC-0019` 재검토 조건 (c)는 형식 요건이고, `ADC-0021` §8이 그 미충족 원인을 "계보 단일성"으로 특정했다. K-1은 그 문언 + "1회 관찰 불인정" 정신의 정합 해석이다.
- **§4.2 (D-B2)** — E5 IN-6이 L-A의 독립성을 테스트로 고정했고, IN-1이 조건부 분기·Loop 실제 실행 + LangGraph 동치를 확인했다. 그러나 3건 전부 stub/PoC이고 프로덕션 관찰 0이라 부분 완화에 그친다.
- **§4.3 (D-B3)** — `ADC-0021` §8 AND 게이트의 조건 1·4가 미충족이므로 Gate (B) 부분 완화가 다음 단계를 열지 않는다.

### Decision Rationale

이 Decision은 `ADC-0019`·`ADC-0021`·`ADR-0010`이 확정한 것을 뒤집지 않는다 — §16.6 존재·A-IN·A-OUT·Reversibility 필수 불변조건·Sequential Reference 기본선·AND 게이트·"부분 충족(E4)"을 전부 전제로만 사용한다. `ADC-0019` 재검토 조건 (c)의 "3건 도달 시 재판단 가능"을 이 ADC가 수행하며, 그 재판단 결과는 "형식 요건 충족 / 부분 완화 / 완전 완화는 프로덕션·실엔진 또는 2번째 비-LangGraph 계보 추가 이후"다. `ADC-0019`·`ADC-0021` 원문은 수정되지 않으며, Gate (B)의 새 상태는 후속 ADR의 §16.6 cross-reference로만 반영된다.

---

## 6. Conditions (유지 — 이 ADC가 약화하지 않음)

1. **`ADC-0019` §Decision 조건 1~6·재검토 조건 (a)(b)** 무변경 — (c)만 "형식 요건 충족 / 견고성 조건 잔존"으로 재판단.
2. **`ADC-0021` §8 AND 게이트** 무변경 — 조건 2만 "형식 요건 충족"으로 갱신. 조건 1(미충족)·조건 3(충족)·조건 4(부분 충족)는 그대로. "조건 1 없으면 Sequential Reference 유지" 기본 결론 유지.
3. **`ADR-0010` "부분 충족"** 무변경 — Gate (C) E4 잔여 한계 (i)~(iii)·완전 discharge 미선언 유지. E5는 C(ii)만 부분 진전.
4. **§16.6 "Reversibility — 필수 Architecture 불변조건" 문단, "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)" 문단** — 후속 ADR이 "다른 계보 요건은 E5로 충족, 프로덕션 관찰 여전히 0"을 부기하되 "부분 충족" 문구·상태는 유지.
5. **§14 미승격 / Production 구현 차단 / `IMPLEMENTATION_RULES.md` line 9/13/14/15/16/19 유지** — Gate (B) 부분 완화가 어느 것도 해제하지 않는다.
6. **Sequential Reference 기본선** (`ADC-0021` §D1) 무변경 — LangGraph 채택은 조건 1·4 충족 시 별도 절차.

---

## 7. Out of Scope

| 항목 | 근거 |
|---|---|
| LangGraph 채택 / 평가 ADC 개설 | `ADC-0021` §8 조건 1 미충족·조건 4 부분 충족. D-B3 |
| Gate (C) 판정 / `ADR-0010` 재판정 | 별도 gate. E5 C(ii)만 부분 진전 |
| Production 구현 착수 / `IMPLEMENTATION_RULES.md` 해제 / §14 승격 | Gate (B)·(C)·조건 1로 계속 차단 |
| L-B 또는 v2 프로덕션 관찰 확보의 착수 지시 | D-B4 — 필요 여부만 후속 조건으로 기록 |
| `BASELINE.md` §16.6 / `GLOSSARY.md` 문언 편집 | 후속 ADR |
| `ADC-0019` / `ADC-0021` 원문 편집 | Gate (B) 새 상태는 §16.6 cross-reference로만 |
| Rule B 전면 재판정 | `ADC-0019` §Q2 — §16.6 전체 Rule B 미충족은 유지, (c)만 형식 요건 충족 |

---

## 8. 후속 ADR에서 반영할 사항 (Baseline 지침)

후속 ADR(Minor 예상, `ADR-0009`/`0010`/`0011`/`0012`류 granularity)이 `BASELINE.md` §16.6과 `GLOSSARY.md`에 아래를 반영한다. §5·§6·§7·§11·§14·§14.1 표·§16.1~§16.5·§16.7, Adapter Contract (a)(b)(c)(d) bullet, `IMPLEMENTATION_RULES.md`는 무변경.

1. **§16.6 "Reversibility v2 통합 테스트 재현 — 부분 충족 (E4)" 문단에 1~2문장 부기** — "`ADC-0019` 재검토 조건 (c)(= `ADC-0021` §8 Gate (B))의 **형식 요건**(독립 관찰 3건, 그중 1건이 LangGraph와 다른 계보)은 E5(`projects/workflow-adapter-nonlanggraph-lineage-v1/` — worklist 인터프리터 L-A, IN-1~IN-6 25 PASS)로 **충족된다**(`ADC-0024`). 그러나 3건 전부 결정론적 stub / PoC이고 v2 프로덕션·실엔진 관찰은 0건, 비-LangGraph 계보는 1개뿐이므로 Conditional 성격은 **부분 완화**에 그친다 — 완전 완화는 2번째 비-LangGraph 계보 또는 v2 프로덕션 관찰 이후 재판정한다(`ADC-0024` §D-B4)." "부분 충족" 문구·Gate (C) 상태는 불변.
2. **§16.6 "v2 공백의 현재 상태" 또는 "Production 구현과의 관계" 문단** — "`ADC-0021` §8 Gate (B)"를 언급하는 cross-reference에 "(형식 요건 충족 / 견고성 조건 잔존, `ADC-0024`)" 부기. 차단 문언("계속 차단된다")은 불변.
3. **`GLOSSARY.md` "Workflow Adapter (Reference)" 절 주석** — "`ADC-0019` 재검토 조건 (c)와 v1 `ADR-0007` 결정 9는 그대로 미충족" 문장을 "`ADC-0019` 재검토 조건 (c)는 형식 요건 충족·견고성 조건 잔존(`ADC-0024`), v1 `ADR-0007` 결정 9는 `ADC-0023`으로 해소"로 정정.
4. **Version**: v1.16 → v1.17 (Minor 예상), Frozen 유지.
5. **명시적 비변경**: §16.6 A-IN/A-OUT·Reversibility 필수 불변조건 문단·Adapter Contract bullet·"실행 단위"·"실행 단위 Lifecycle" 문단, §14·§14.1·§7·§11, `IMPLEMENTATION_RULES.md`, `ADC-0019`·`ADC-0021` 원문, Gate (C) "부분 충족".

---

## 9. Architecture / Governance Review

### 9.1 Governance Chain 정합성

| 점검 | 결과 |
|---|---|
| 선행(`ADC-0019`·`ADC-0021`·`ADR-0010`)이 확정한 것을 뒤집는가 | **아니오** — §16.6 존재·Reversibility 불변조건·Sequential Reference 기본선·AND 게이트·"부분 충족(E4)"을 전제로만 사용(§6) |
| `ADC-0019` 재검토 조건 (c)의 "재판단이 가능하다"를 수행하는가 | **예** — 3건 도달을 확인하고 완화 정도를 판정(D-B2). 자동 완화 아님(K-3 Reject) |
| `ADC-0019` 재검토 조건 (c)의 OR("다른 계보 또는 v2 프로덕션")를 준수하는가 | **예** — E5/L-A가 "다른 계보"를 채움. "프로덕션 수준"을 덧붙이지 않음(R-3 Reject) |
| `ADC-0021` §8 AND 게이트를 우회하는가 | **아니오** — 조건 2만 갱신, 조건 1·4 미충족으로 LangGraph 평가 ADC 불가 명시(§4.3, D-B3) |
| `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ADC Accept를 발생시키지 않는다" | **준수** — E5는 §5 정합 판정의 입력. LangGraph 채택·구현을 발생시키지 않음 |

### 9.2 경계 — 선행 확장 여부

| 점검 | 결과 |
|---|---|
| 새 Architecture 책임·Layer·Component·Concept·Contract를 추가하는가 | **아니오** — Gate (B) 상태 판정만 |
| §14 / §14.1 / §16.6 A-IN·A-OUT / Adapter Contract를 건드리는가 | **아니오** — §8이 후속 ADR로 §16.6 문단 부기만 지시 |
| Gate (C) / LangGraph 채택 / Production / `IMPLEMENTATION_RULES.md`를 진전시키는가 | **아니오** — §7 Out of Scope, D-B3 |
| L-B 구현을 요구하는가 | **아니오** — D-B4, 필요 여부만 후속 조건 |
| `BASELINE.md`·`GLOSSARY.md`·`ADC-0019`·`ADC-0021`을 이 ADC가 편집하는가 | **아니오** — 이 ADC 파일 1건만 신규 작성(미커밋) |

### 9.3 사용자 지시 준수

| 지시 | 준수 |
|---|---|
| E1·E2·E5(L-A)의 "독립 관찰 3건"이 `ADC-0019` 조건 (c)를 충족하는지 판단하는 ADC 초안 | **준수** — D-B1(기준)·D-B2(판정): 형식 요건 충족 / 부분 완화 |
| L-B는 추가 구현하지 않음 | **준수** — D-B4는 필요 여부만 후속 조건. §7 Out of Scope |
| 이번 ADC에서는 Gate B 인정 기준과 E5의 실제 기여도만 판정 | **준수** — §1.1 판단 항목 2개(D-B1·D-B2). Gate (C)·LangGraph 채택·Production은 §7 Out of Scope |

### 9.4 판정

**PASS.** 이 ADC는 `ADC-0019` 조건 1~6·재검토 조건 (a)(b), `ADC-0021` §8 AND 게이트(조건 1·3·4), `ADR-0010` "부분 충족", Rule B 전체 미충족, `IMPLEMENTATION_RULES.md` 금지, Sequential Reference 기본선을 **하나도 약화하지 않는다**(§6). Gate (B)를 "형식 요건 충족 / 견고성 조건 잔존"으로 부분 완화하되, LangGraph 평가 ADC·Gate (C)·Production·§14 승격을 열지 않는다(§7·D-B3).

**Next Step**: ADR Required — §8 지침으로 §16.6·`GLOSSARY.md`에 Gate (B) 부분 완화 상태를 반영(Minor, v1.16 → v1.17). Commit/PR/Merge는 사용자 보고 후.

---

## 10. Traceability

| 문서 / 절 | 관계 |
|---|---|
| `ADC-0019` §Risks·재검토 조건 (c) | 이 ADC가 판정하는 대상. "3건 도달 시 재판단 가능" 수행. §Risks의 "v2 프로덕션 트래픽 아님"은 별도 잔존 우려로 인용 |
| `ADC-0021` §8 조건 2·"1회 관찰 불인정"·AND 게이트 | Gate (B) = 조건 2. K-1이 "1회 관찰 불인정" 정신 계승. 조건 1·4 미충족 → LangGraph 평가 ADC 불가(§4.3) |
| `ADR-0010` (Gate (C) "부분 충족") | 무변경 — E5는 C(ii)만 부분 진전 |
| `ADC-0022`·`ADC-0023` → `ADR-0011`·`ADR-0012` (Gate (A) Resolved, BASELINE v1.16) | `ADC-0021` §8 조건 3 충족의 근거. 이 ADC와 별개 축 |
| E4 `projects/workflow-adapter-reversibility-v2/EVIDENCE.md` §4 한계 2·§5 | E5가 겨냥한 한계("대조 어댑터 LangGraph 단일 계보"). Gate (B) "미충족" 자기 명시 |
| E5 `projects/workflow-adapter-nonlanggraph-lineage-v1/EVIDENCE.md` | D-B2의 직접 근거. IN-1~IN-6 25 PASS, "(c) 충족 선언 안 함" 자기 한정 |
| `BASELINE.md` v1.16 §16.6 "Reversibility v2 ... 부분 충족 (E4)" 문단 | 반영 대상(후속 ADR §8-1). "부분 충족" 문구 불변 |
| `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" | E4·E5의 레인. Evidence는 판정 입력이지 자동 Accept 아님 |
| `archive/v1/tests/integration/test_workflow_adapter_reversibility.py` | E1 — v1 LangGraph 실사용 관찰 |
| `.claude/docs/integrations/langgraph.md` | E2 — RFC-0019 세션 LangGraph PoC 관찰 |

---

## 11. Self-Review

- `ADC-0019`·`ADC-0021`·`ADR-0010`이 확정하지 않은 것을 새로 결정했는가 — **Gate (B) 형식 요건 충족 여부 + Conditional 완화 정도만**. LangGraph 채택·Gate (C)·Production·§14 승격·`IMPLEMENTATION_RULES.md` 해제는 §7 Out of Scope.
- E1·E2·E5(L-A)의 3건이 (c)를 충족하는지 판단했는가 — **예** — 형식 요건(독립 관찰 3건 / 다른 계보 1건) **충족**, Conditional **부분 완화**(v2 프로덕션·실엔진 관찰 0, 비-LangGraph 계보 1개).
- Gate (B) 인정 기준을 제시했는가 — **예**(D-B1, K-1): 맥락 3건 + 조건부 분기·Loop 실제 실행 + 최소 1건 다른 계보/프로덕션 + 독립성(co-design floor 불인정).
- E5의 실제 기여도를 판정했는가 — **예**(D-B2): bona fide 독립 비-LangGraph 관찰, "동일 계보" 형식 우려 해소, 그러나 stub/PoC 수준이라 부분 완화.
- Gate B 충족을 선언해 다음 단계를 열었는가 — **아니오**(D-B3) — `ADC-0021` §8 조건 1·4 미충족으로 LangGraph 평가 ADC 불가, Sequential Reference 기본선 유지.
- L-B를 구현하도록 요구했는가 — **아니오**(D-B4) — 완전 완화의 후속 조건으로 (i) 2번째 비-LangGraph 계보 또는 (ii) v2 프로덕션 관찰을 기록만. 착수 지시 없음.
- `BASELINE.md`·`GLOSSARY.md`·`ADR`·`IMPLEMENTATION_RULES.md`·`ADC-0019`·`ADC-0021`을 수정했는가 — **아니오**. 이 ADC 파일 1건만 신규 작성(미커밋).
- 새 실험/PoC를 수행했는가 — **아니오**(§1.3) — `main` 병합 Evidence + Governance 문서만.
- Gate (C) / `ADR-0010`을 건드렸는가 — **아니오**(§7·§6 조건 3) — E5의 C(ii) 부분 진전은 별도 gate의 사실로만 인용.
- "독립 관찰 3건" 문언과 E1+E2+E5/L-A(및 `ADC-0021` §8 카운팅의 E1·E2·E3-langgraph-domain-poc+E5/L-A) 인정의 정합성을 확인했는가 — **예**(§2 "E3 라벨 충돌 주의"·"핵심 사실", §4.1) — 두 카운팅 모두에서 독립 관찰 3건 이상 + 비-LangGraph 1건 확보, `ADC-0021` §8이 지목한 "전부 LangGraph 계보" 상태 해소.
- Gate (B)/(C)·`ADC-0021` §8 조건의 범위를 넘었는가 — **아니오**(§7·§9.2·§6) — 조건 2 형식 요건만 판정, 조건 1·3·4·Gate (C)·LangGraph 채택·Production·`IMPLEMENTATION_RULES.md`는 무변경.
- Architecture/Governance Review를 수행했는가 — **예**(§9), 판정 = PASS. 최종 재검토에서 K-1 채택/K-2·K-3 거부 논리와 E5 Partial 완화 판정의 정합성을 재확인했고, 신규·범위 초과 결정은 발견되지 않았다.
- Commit/PR/Merge를 했는가 — **아니오** — Status는 Decided이나 `BASELINE.md`·`GLOSSARY.md`·ADR은 미착수. 사용자 승인 후 Commit/PR 진행(`main` 직접 금지).
