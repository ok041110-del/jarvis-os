# ADC-0026: Gate (C) — E7(실제 Engine 호출) 기반 잔여 한계 (i) 판정

**Status**: Decided — **Partial**. Architecture/Governance Review PASS(§9). `BASELINE.md`·`GLOSSARY.md`·기존 ADC/ADR 미착수(반영 여부는 후속 별도 절차, §8). 이 ADC 파일 자체의 Commit/PR만 진행, Merge는 사용자 승인 후.
**Author**: Claude Code
**선행 체인**: `RFC-0019`→`ADC-0019`→`ADR-0008`(§16.6 존재 Accept·Conditional) → `ADC-0021` §8(Gate (A)/(B)/(C) 명명, AND 게이트 조건 1~4) → `ADR-0010`(Gate (C) E4 "부분 충족", 잔여 한계 (i)~(iii) 명문화) → E5→`ADC-0024`→`ADR-0013`(Gate (B) 1차 부분 완화, 잔여 한계 (ii) 부분 진전) → E6→`ADC-0025`→`ADR-0014`(Gate (B) 2차 부분 완화, BASELINE v1.18) → **E7**(`projects/workflow-adapter-gate-c-real-engine-v1/EVIDENCE.md` — 이 ADC의 대상, 잔여 한계 **(i)** 겨냥)
**RFC pairing**: `ADC-0019` §Q6·§Decision 조건 4 + `ADC-0021` §8 조건 4(Gate C) + `ADR-0010` §Decision 2.1 잔여 한계 (i) — 이 셋이 이 ADC의 판정 대상이자 트리거다. `ADC-0024`/`ADC-0025`가 `RFC-0020` §8.2를 상위 RFC-level 개설로 계승한 선례를 그대로 따른다 — 새 Boundary Question을 열지 않으므로 별도 RFC 불요.
**대상**: `BASELINE.md` §16.6 "부분 충족(E4)" 문단이 명시한 Gate (C) 잔여 한계 **(i)**("노드가 결정론적 stub — 실제 엔진 비결정성·부분 실패율 미검증")이 E7(`projects/workflow-adapter-gate-c-real-engine-v1/`)로 어느 정도 진전됐는지 판정한다. **Full Discharge는 판정하지 않는다.**

> 이 ADC는 **Gate (C) 잔여 한계 (i)의 부분 진전 여부만** 판정한다. Gate (C)의 전체 지위("부분 충족", `ADR-0010`)를 재론하지 않는다. 잔여 한계 (ii)(대조 계보 단일성 — Gate (B) 축에서 E5/E6으로 이미 별도 판정됨, `ADC-0024`/`ADC-0025`)·**(iii)**(프로덕션 트래픽 미검증)은 이 ADC가 손대지 않는다. **Gate (C)(iii), Gate (B), `ADC-0021` §8 조건 1, LangGraph 채택/평가, Production 구현 착수, `IMPLEMENTATION_RULES.md` 해제 — 어느 것도 판정을 변경하지 않는다.**

---

## 1. 목적과 경계

### 1.1 이 ADC가 판단하는 것 (둘)

| # | 판단 항목 | 근거 위임 |
|---|---|---|
| **D-E1** | **E7이 Gate (C) 잔여 한계 (i)에 실제로 기여하는가, 어느 정도인가** — 실제 Engine 표본 수·실제화된 노드 범위·검증된 예외 유형(진짜 vs 합성)을 기준으로 판단 | `ADR-0010` §Decision 2.1(잔여 한계 (i) 원문), E7 `EVIDENCE.md` §3~§5 |
| **D-E2** | **Full Discharge 여부** — D-E1의 기여가 잔여 한계 (i)를 "완전히" 메우는지, 아니면 부분 진전에 그치는지 | `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ADC Accept를 발생시키지 않는다", E7 §4 한계 목록 |

### 1.2 이 ADC가 판단하지 않는 것 (경계)

- **Gate (C) 전체 지위 재판정** — `ADR-0010` "부분 충족"은 그대로다. 이 ADC는 그 아래 잔여 한계 (i) 항목 하나에 대해서만 추가 사실을 기록한다.
- **Gate (C) 잔여 한계 (ii)·(iii)** — (ii)는 Gate (B) 축에서 이미 별도로 다뤄졌다(`ADC-0024`/`ADC-0025`). (iii)(프로덕션 트래픽)은 E7이 애초에 겨냥하지 않았고 해소하지도 않는다(E7 §4 한계 1, §5).
- **Gate (B)** — `ADC-0024`/`ADC-0025`가 확정한 "2차 부분 완화" 상태를 이 ADC는 재론하지 않는다.
- **`ADC-0021` §8 조건 1**(LangGraph 고유 능력 필요) — 관찰 0건 그대로, 이 ADC와 무관.
- **LangGraph 채택 / 평가 ADC 개설 / Production 구현 착수 / `IMPLEMENTATION_RULES.md` 해제 / §14 승격** — 무엇도 결정하지 않는다.
- **`BASELINE.md`/`GLOSSARY.md`/기존 ADC·ADR 원문 편집** — 이 ADC는 하지 않는다. 반영이 필요한지 여부만 §8에서 언급하고, 실행은 별도 절차로 남긴다(불필요한 Governance 문서 증식 방지).

### 1.3 새 실험 없음

이 ADC는 `main`(BASELINE v1.18)에서 아직 커밋되지 않은 세션 내 Evidence, E7(`projects/workflow-adapter-gate-c-real-engine-v1/EVIDENCE.md`)만 인용한다. 새 PoC·측정을 수행하지 않는다.

---

## 2. Evidence

| # | Evidence | 실제 Engine 호출 | 검증 내용 |
|---|---|---|---|
| **E4** | `projects/workflow-adapter-reversibility-v2/` — 결정론적 stub, IN-1~IN-5 22 PASS | 0회 | Gate (C) "부분 충족" 원 Evidence. 잔여 한계 (i)~(iii) 원문 명시(`ADR-0010`) |
| **E7** | `projects/workflow-adapter-gate-c-real-engine-v1/` — `analyst_sentiment` 1개 노드를 실제 Engine 호출로 대체, IN-7-1~IN-7-5 **12/12 PASS** | **3회**(clean 캡처 1 + data_gap 캡처 1 + 실제 timeout 유도 1) | 아래 참조 |

**E7이 실제로 실행·확인한 것 (EVIDENCE §3 실측)**:
- **opt-in 게이팅**: `RUN_REAL_ENGINE_TESTS` 미설정 시 12개 테스트 전부 **SKIPPED**(0.18초, 실제 Engine 호출 0회) — 기본 스위트에 비용이 섞이지 않음을 실측 확인.
- **`RUN_REAL_ENGINE_TESTS=1`로 실행 시 12/12 PASSED(12.41초)**.
- **실제 `claude` CLI 호출 3회**(`/usr/local/bin/claude`, `2.1.220`, 실제 설치·인증 확인):
  - `clean` 캡처 1회 — 실제 응답: "가상의 스타트업 '블루문 커머스'는 ... 전반적으로 안정적인 흐름을 유지하고 있다."
  - `data_gap` 캡처 1회 — 실제 응답: "유가리 코퍼레이션에 대한 감정 분석 결과 ... 결론이 엇갈렸다."
  - **실제 timeout 유도 1회** — `ENGINE_TIMEOUT_SECONDS=0.01`로 진짜 `claude` subprocess를 기동시켜 실제 `subprocess.TimeoutExpired(['claude', '-p', ...])` 발생을 명령행 인자까지 실측 확인.
- **RuntimeError 경로는 0회의 실제 호출로 검증**(합성) — `subprocess.run`을 로컬 대체해 `call_engine()`의 **실제 소스 코드**(비-zero exit 시 raise하는 분기)만 조건 통제로 실행. `claude` CLI는 기동되지 않았다. 실측: `RuntimeError('exit code 1: synthetic non-zero exit (IN-7-3b)')`.
- **Record-once-replay**: 캡처된 각 값이 4개 어댑터(sequential/worklist L-A/recursive L-B/langgraph L-LG)에 동일 주입돼 최종 State dict 동치 확인(IN-7-2).
- **catch-and-encode**: 진짜 `TimeoutExpired`와 합성 `RuntimeError` 모두 4개 어댑터 전부에서 `NODE_ERROR:analyst_sentiment:{ExcType}` State 값으로 인코딩, 경계 밖 전파 없음(IN-7-3).
- **Checkpoint round-trip**: 실제 Engine 텍스트가 포함된 phase1 checkpoint 값이 JSON round-trip 성공, 별도 프로세스가 로드해 `run_phase2` 실행 → 단발 `run_full`과 동일 결과(IN-7-4). 재개 프로세스는 실제 Engine을 재호출하지 않음(캡처값이 checkpoint 값 자체에 이미 실려 있음).
- **`core/`·`hqs/`·`dashboard/` 무변경**: `git diff --stat` 빈 출력, 해시 불변(IN-7-5).
- **예산 준수**: 실측 `real_call_count() == 3` ≤ 승인된 예산 10(메타 검증 PASS).

---

## 3. Alternatives

### 3.1 E7의 기여를 어떻게 볼 것인가 (D-E1)

| | 판정 | 근거 |
|---|---|---|
| **G-1** | **기여 없음** | **Reject** — E4/E5/E6과 달리 E7은 실제 `claude` CLI subprocess를 3회 기동해 진짜 비결정적 텍스트·진짜 `TimeoutExpired`를 얻었고, 4개 어댑터 전부가 그것을 catch-and-encode·Checkpoint round-trip으로 정상 처리함을 실측했다(§2). "미검증"이라는 원 서술의 핵심 결여(실제 Engine 실행 자체의 부재)를 정면으로 메웠다 |
| **G-2** | **완전 기여 — 잔여 한계 (i) 완전 해소** | **Reject**(§3.2에서 상술) — 표본 극소(시나리오당 1회)·실제화된 노드 1개뿐·RuntimeError 경로는 합성으로만 검증(진짜 non-zero exit 미실측)이라는 세 결여가 남는다(E7 §4 한계 2·3, §5) |
| **G-3 (채택)** | **부분 기여** — "실제 Engine을 통한 비결정성·catch-and-encode가 4개 어댑터에서 작동하는가"라는 좁은 질문에는 실측으로 답했으나, "부분 실패율"(반복·분포) 및 "모든 노드가 실제화됐을 때"의 일반화는 답하지 않았다 | E7 EVIDENCE §4·§5가 스스로 "완전 discharge 여부는 이 문서가 선언하지 않음"으로 자기 한정 |

### 3.2 Full Discharge 여부 (D-E2)

| | 판정 | 근거 |
|---|---|---|
| **F-1** | **Full Discharge** — E7로 잔여 한계 (i) 완전 해소, `ADC-0019` 조건 4 완전 discharge 향해 진전 | **Reject** — 아래 §4.2 잔존 한계 3가지가 명확히 남아 있고, `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ... Accept를 발생시키지 않는다"는 원칙과 직접 충돌한다 |
| **F-2** | **진전 없음(미충족 유지)** | **Reject** — E7이 실측한 것(진짜 timeout 발생·4개 어댑터 catch-and-encode 일치·실제 텍스트의 Checkpoint round-trip)을 무시하는 것이며 사실과 맞지 않는다 |
| **F-3 (채택)** | **Partial** — 잔여 한계 (i)에 대해 "부분 진전"을 기록하되, Gate (C)의 "부분 충족" 전체 지위·discharge 미선언 원칙은 그대로 유지 | E4가 "부분 충족"으로 판정된 것과 같은 논리 층위 — 실측된 것만큼만 인정하고 과장하지 않는다 |

---

## 4. Analysis

### 4.1 D-E1 — E7이 실제로 메운 것

`ADR-0010` §Decision 2.1의 잔여 한계 (i) 원문: "노드가 결정론적 stub — 실제 엔진 비결정성·부분 실패율 미검증." 이 문장이 지목한 결여는 **두 개의 하위 질문**으로 분해된다:

1. **"진짜 비결정적인 값이 파이프라인을 관통해도 Reversibility가 유지되는가?"** — E7 IN-7-1·IN-7-2가 답했다. 3회의 실제 `claude` CLI 호출로 얻은 진짜, 예측 불가능한 텍스트가 4개 어댑터 전부에서 동일하게 병합·전달됨을 실측했다(record-once-replay 설계로 "LLM 재현성"과 "어댑터 정합성"을 분리했기 때문에 이 비교가 의미를 가진다 — §2).
2. **"실제 인프라 예외가 catch-and-encode 경로를 타는가?"** — E7 IN-7-3가 부분적으로 답했다. **`subprocess.TimeoutExpired`는 진짜 실행으로** 확인했다(실제 timeout 유도 1회). **그러나 `RuntimeError`(비-zero exit) 경로는 `call_engine()`의 실제 소스 코드를 실행했을 뿐, `claude` CLI가 실제로 non-zero exit를 낸 사례는 관측하지 못했다** — `subprocess.run`을 로컬로 대체한 합성 조건이다(E7 §Summary "RuntimeError 재현은 0회(합성)").

### 4.2 D-E2 — Full Discharge를 판정하지 않는 이유 (잔존 한계, 요청대로 명시)

세 가지가 명확히 남는다:

1. **실제 Engine 표본이 3회뿐이다** — 시나리오당 1회(clean 1, data_gap 1)의 record-once-replay 캡처 + 실제 timeout 유도 1회. "비결정성 하에서도 항상 성립하는가"를 답하려면 반복 표본이 필요한데, E7은 "적어도 한 번은 성립한다"만 보였다(E7 §4 한계 2).
2. **실제화된 노드가 1개뿐이다** — 13개 노드 중 `analyst_sentiment` 하나만 실제 Engine 호출로 대체됐다. 나머지 12개(5-way fan-out 중 4개, fan-in, 토론 Loop 3노드, trader, 종단 2노드)는 여전히 결정론적 stub이다(E7 §4 한계 3).
3. **실제 non-zero exit가 미실측이다** — `call_engine()`이 raise하는 두 예외 유형 중 `subprocess.TimeoutExpired`는 진짜 실행으로 확인됐으나, `RuntimeError`는 `subprocess.run` 자체를 로컬 대체한 합성 조건에서만 확인됐다. **진짜 `claude` CLI가 실제로 non-zero exit code를 낸 사례는 이 Evidence에 없다**(§2, §4.1-2).

이 세 한계는 `ARCHITECTURE_GOVERNANCE.md`의 "Experimental Evidence는 그 존재만으로 Formal Architecture Decision이나 ADC Accept를 발생시키지 않는다"는 원칙과 정확히 같은 이유로 Full Discharge를 막는다 — E7이 보인 것은 실재하는 진전이지만, 원 서술("실제 엔진 비결정성·부분 실패율 미검증")이 요구하는 반복성·전면성·완전한 실측을 아직 충족하지 못한다.

### 4.3 Gate (C)(iii)·Gate (B)·조건 1·LangGraph·Production·`IMPLEMENTATION_RULES`와의 관계 — 전부 무변경

- **Gate (C)(iii)**(프로덕션 트래픽): E7은 격리된 실험 샌드박스의 단발 호출이지 실 HQ 운영 트래픽이 아니다(E7 §4 한계 1). **무변경.**
- **Gate (B)**: E7의 4개 어댑터는 전부 이미 알려진 계보(sequential/L-A/L-B/L-LG)다 — 신규 계보가 아니므로 Gate (B) 독립 관찰 카운팅에 아무것도 더하지 않는다. `ADC-0024`/`ADC-0025`의 "2차 부분 완화" 상태 **무변경.**
- **`ADC-0021` §8 조건 1**(LangGraph 고유 능력 필요): E7은 이 질문과 무관하다. 관찰 0건 **무변경.**
- **LangGraph 채택 / 평가 ADC 개설**: 조건 1·(iii) 모두 무변경이므로 열리지 않는다.
- **Production 구현 착수 / `IMPLEMENTATION_RULES.md` 해제**: Gate (C) 전체 지위가 "부분 충족"에서 조금도 움직이지 않았으므로(§4.2) 차단 **무변경.**

---

## 5. Decision

**판정: Decided — Partial.**

### D-E1. E7의 기여

E7은 Gate (C) 잔여 한계 (i)에 **실재하는 부분 진전**을 제공한다:
- 실제 `claude` CLI 호출 3회로 진짜 비결정적 텍스트를 얻어, 4개 Workflow Adapter 계보(sequential/worklist L-A/recursive L-B/langgraph L-LG) 전부가 record-once-replay 방식으로 이를 동일하게 처리함을 실측(IN-7-1·IN-7-2, 12/12 PASS).
- 진짜 `subprocess.TimeoutExpired`(실제 timeout 1회 유도) + `call_engine()`의 실제 RuntimeError 코드 경로(합성 조건, 0비용)가 4개 어댑터 전부에서 `NODE_ERROR:analyst_sentiment:{ExcType}` 값으로 catch-and-encode됨을 실측(IN-7-3).
- 실제 Engine 텍스트가 포함된 값이 JSON Checkpoint round-trip과 별도 프로세스 재개를 통과함을 실측(IN-7-4).
- `core/`·`hqs/`·`dashboard/` 무변경, 실제 호출 총량 3회(승인 예산 10 이내)를 실측(IN-7-5, 예산 메타 검증).

### D-E2. Full Discharge는 판정하지 않는다 — 잔존 한계 3가지

1. **실제 Engine 표본 3회뿐** — 반복·분포 미검증(§4.2-1).
2. **실제화된 노드 1개뿐**(13개 중 `analyst_sentiment`만) — 나머지 12개는 결정론적 stub 그대로(§4.2-2).
3. **실제 non-zero exit 미실측** — `RuntimeError` 경로는 `subprocess.run` 로컬 대체로만 확인, 진짜 `claude` CLI의 non-zero exit 사례 없음(§4.2-3).

### D-E3. 다른 Gate/조건에 대한 판정 변경 — 없음

- **Gate (C) 전체 지위**("부분 충족", `ADR-0010`): **무변경.** 잔여 한계 (i)에 대한 사실만 추가로 기록한다.
- **Gate (C)(iii)**: **무변경**(§4.3).
- **Gate (B)**(`ADC-0024`/`ADC-0025` "2차 부분 완화"): **무변경**(§4.3).
- **`ADC-0021` §8 조건 1**: **무변경**(§4.3).
- **LangGraph 채택/평가, Production 구현 착수, `IMPLEMENTATION_RULES.md` 해제**: **무변경**(§4.3).

### Reason

- **§4.1(D-E1)** — E7이 실측한 3가지(비결정성 하 동치, 진짜/합성 예외의 catch-and-encode, 실제 텍스트의 Checkpoint round-trip)는 `ADR-0010`이 지목한 결여를 정면으로 다뤘다.
- **§4.2(D-E2)** — 표본 극소·노드 1개·non-zero exit 미실측이라는 세 한계가 Full Discharge를 막는다. `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ... 발생시키지 않는다"는 원칙과 일치.
- **§4.3** — Gate (C)(iii)·Gate (B)·조건 1·LangGraph·Production·`IMPLEMENTATION_RULES`는 E7의 실험 범위와 무관해 어느 것도 움직이지 않는다.

### Decision Rationale

이 Decision은 `ADC-0019`·`ADC-0021`·`ADR-0010`·`ADC-0024`·`ADC-0025`·`ADR-0013`·`ADR-0014`가 확정한 것을 뒤집지 않는다 — §16.6 존재·A-IN·A-OUT·Reversibility 필수 불변조건·Sequential Reference 기본선·AND 게이트·Gate (A) "해소"·Gate (B) "2차 부분 완화"·Gate (C) "부분 충족"을 전부 전제로만 사용한다(§6). E7이 보인 실측 결과만큼만 인정하고, 그 이상(Full Discharge, 다른 Gate/조건의 진전)을 선언하지 않는다.

---

## 6. Conditions (유지 — 이 ADC가 약화하지 않음)

1. **`ADC-0019` §Decision 조건 1~6·재검토 조건 (a)(b)(c)** 무변경.
2. **`ADC-0021` §8 AND 게이트 조건 1·2·3·4** 무변경 — 조건 4(Gate C)는 "부분 충족" 그대로, 이 ADC는 그 아래 잔여 한계 (i) 항목에만 사실을 추가한다.
3. **`ADR-0010` "부분 충족"** 무변경 — 완전 discharge 미선언 유지. 잔여 한계 (ii)·(iii) 서술 verbatim.
4. **`ADC-0024`·`ADR-0013`, `ADC-0025`·`ADR-0014`의 Gate (B) "2차 부분 완화" 판정** 무변경.
5. **§14 미승격 / Production 구현 차단 / `IMPLEMENTATION_RULES.md` 유지** — 어느 것도 해제하지 않는다.
6. **Sequential Reference 기본선**(`ADC-0021` §D1) 무변경.

---

## 7. Out of Scope

| 항목 | 근거 |
|---|---|
| Gate (C) 전체 지위 재판정 / Full Discharge 선언 | §4.2, D-E2 — 잔존 한계 3가지로 Reject |
| Gate (C) 잔여 한계 (ii)·(iii) 판정 | (ii)는 Gate (B) 축에서 별도 판정됨. (iii)은 E7이 겨냥·해소하지 않음(§4.3) |
| Gate (B) 재판정 | `ADC-0024`/`ADC-0025` 판정 무변경(§4.3) |
| `ADC-0021` §8 조건 1 판정 | E7과 무관, 관찰 0건 그대로(§4.3) |
| LangGraph 채택 / 평가 ADC 개설 / Production 구현 착수 / `IMPLEMENTATION_RULES.md` 해제 | §4.3 — 전부 무변경 |
| `BASELINE.md` / `GLOSSARY.md` / 기존 ADC·ADR 원문 편집 | 이 ADC는 하지 않는다. 필요 시 후속 별도 Minor ADR(§8) |
| 추가 실제 Engine 실험(반복 표본 확대, 나머지 노드 실제화, 진짜 non-zero exit 유도)의 착수 지시 | D-E2가 잔존 한계로 지목만 — 착수 여부·시점은 이 ADC가 정하지 않는다 |

---

## 8. 후속 절차 (필요 시에만 — 이 ADC가 지시하지 않음)

이 ADC의 결과를 `BASELINE.md` §16.6 잔여 한계 (i) 서술에 반영하려면, `ADR-0010`/`ADR-0013`/`ADR-0014`류 granularity의 Minor ADR 1건이 필요하다(기존 "(i) 노드가 결정론적 stub — 실제 엔진 비결정성·부분 실패율 미검증" 문장 뒤에 "E7로 부분 진전(1개 노드·표본 3회·실제 non-zero exit 미실측 — 완전 해소 아님)" 취지의 짧은 부기, Version Minor 증가). **이 ADC는 그 ADR을 작성하지 않는다** — 반영이 지금 필요한지, 다음 Gate C(iii) 조치와 묶어 나중에 반영할지는 사용자 판단으로 남긴다. 불필요한 Governance 문서 증식을 피하기 위해 이 판단이 내려지기 전까지는 후속 ADR을 만들지 않는다.

---

## 9. Architecture / Governance Review

### 9.1 Governance Chain 정합성

| 점검 | 결과 |
|---|---|
| 선행(`ADC-0019`·`ADC-0021`·`ADR-0010`·`ADC-0024`·`ADC-0025`·`ADR-0013`·`ADR-0014`)이 확정한 것을 뒤집는가 | **아니오** — §16.6 존재·Reversibility 불변조건·Gate (A)/(B)/(C) 상태를 전제로만 사용(§6) |
| Gate (C) 잔여 한계 (i)에 대해 근거 없이 과장했는가 | **아니오** — E7 EVIDENCE의 실측치(호출 3회, 노드 1개, 합성 vs 실제 예외 구분)를 그대로 인용(§2·§4) |
| `ADC-0021` §8 AND 게이트를 우회하는가 | **아니오** — 조건 4는 "부분 충족" 그대로, 이 ADC로 조건 1·2·3 어느 것도 건드리지 않음(§4.3) |
| `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ADC Accept를 발생시키지 않는다" | **준수** — E7은 §5 판정의 입력일 뿐. Full Discharge를 선언하지 않음(D-E2) |

### 9.2 경계 — 선행 확장 여부

| 점검 | 결과 |
|---|---|
| 새 Architecture 책임·Layer·Component·Concept·Contract를 추가하는가 | **아니오** — Gate (C) 잔여 한계 (i) 사실 기록만 |
| Gate (C)(iii) / Gate (B) / 조건 1 / LangGraph / Production / `IMPLEMENTATION_RULES.md`를 진전시키는가 | **아니오**(§4.3, §7 Out of Scope) |
| `BASELINE.md`·`GLOSSARY.md`·기존 ADC/ADR을 이 ADC가 편집하는가 | **아니오** — 이 ADC 파일 1건만 신규 작성(§8에서 후속 ADR 필요성만 언급, 미작성) |
| 필요 이상의 새 Governance 문서를 만들었는가 | **아니오** — 이 ADC 1건뿐. 후속 ADR은 §8에서 조건부로만 언급, 작성하지 않음 |

### 9.3 사용자 지시 준수

| 지시 | 준수 |
|---|---|
| 판정은 `Decided — Partial` | **준수** — Status 필드·§5 명시 |
| E7의 실제 claude CLI 3회 호출, IN-7-1~IN-7-5 12/12 PASS, 실제 timeout, Record-once-replay, checkpoint/process resume를 Evidence로 정확히 반영 | **준수** — §2(Evidence), §4.1이 각각 인용 |
| Full Discharge 금지 | **준수** — D-E2, F-1 Reject |
| 실제 Engine 표본 3회·real node 1개·실제 non-zero exit 미실측 등 residual limitation 명시 | **준수** — §4.2 세 항목, §5 D-E2 |
| Gate C(iii), Gate B, `ADC-0021` §8 조건 1, LangGraph 채택, Production 구현, `IMPLEMENTATION_RULES` 해제에 판정 변경 없음 | **준수** — §4.3, §5 D-E3, §6 Conditions |
| 기존 RFC/ADC/ADR/BASELINE/GLOSSARY 의미 변경 없음, 불필요한 Governance 문서 신규 생성 없음 | **준수** — §7 Out of Scope, §8(후속 ADR 미작성) |
| 코드·기존 experimental project 무수정 | **준수** — 이 ADC는 문서 1건만 신규 작성. `core/`·`hqs/`·`dashboard/`·E4/E5/E6/E7 프로젝트 전부 무변경(§9.4 검증) |

### 9.4 판정

**PASS.** 이 ADC는 `ADC-0019` 조건 1~6·재검토 조건 (a)(b)(c), `ADC-0021` §8 AND 게이트(조건 1·2·3·4), `ADR-0010` "부분 충족"·잔여 한계 (ii)·(iii), `ADC-0024`·`ADC-0025`의 Gate (B) 판정, Rule B 전체 미충족, `IMPLEMENTATION_RULES.md` 금지, Sequential Reference 기본선을 **하나도 약화하지 않는다**(§6). Gate (C) 잔여 한계 (i)에 대해서만 "부분 진전(Partial)"을 사실로 기록하며, Full Discharge·다른 Gate/조건의 진전·LangGraph 평가·Production·§14 승격은 열지 않는다(§7·D-E3).

**Next Step**: 필요 시에만 Minor ADR(§8) — 이번 단계에서는 작성하지 않는다. `BASELINE.md`·`GLOSSARY.md`·기존 ADC/ADR·코드·experimental project 전부 무변경.

---

## 10. Traceability

| 문서 / 절 | 관계 |
|---|---|
| `ADR-0010` §Decision 2.1 잔여 한계 (i) | 이 ADC가 판정하는 대상 |
| `ADC-0021` §8 조건 4(Gate C) | 무변경, 이 ADC는 그 하위 사실만 추가 |
| `ADC-0024`·`ADR-0013`, `ADC-0025`·`ADR-0014`(Gate B) | 무변경 재확인(§4.3) |
| E7 `projects/workflow-adapter-gate-c-real-engine-v1/EVIDENCE.md` | D-E1·D-E2의 직접 근거 |
| E4 `projects/workflow-adapter-reversibility-v2/EVIDENCE.md` | Gate (C) 원 Evidence, 잔여 한계 (i)~(iii) 원 출처 |
| `hqs/development/mvp/engine.py::call_engine()`(`ENGINE-CONNECT-0001`) | E7이 read-only import한 실제 Engine 경유 지점 — 이 ADC도 무수정 확인 |
| `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" | E7의 레인. Evidence는 판정 입력이지 자동 Accept 아님 |

---

## 11. Self-Review

- `ADC-0019`·`ADC-0021`·`ADR-0010`·`ADC-0024`·`ADC-0025`가 확정하지 않은 것을 새로 결정했는가 — **Gate (C) 잔여 한계 (i)의 부분 진전 여부만**. Gate (C)(iii)·Gate (B)·조건 1·LangGraph·Production·`IMPLEMENTATION_RULES`는 §7 Out of Scope.
- E7의 실제 수치(호출 3회, 12/12 PASS, 실제 timeout, 합성 RuntimeError)를 정확히 반영했는가 — **예**(§2) — E7 `EVIDENCE.md` 원문 수치를 그대로 인용, 가정 없음.
- Full Discharge를 선언했는가 — **아니오**(D-E2, F-1 Reject) — 표본 3회·노드 1개·non-zero exit 미실측 세 한계를 명시.
- Gate C(iii)/Gate B/조건 1/LangGraph/Production/`IMPLEMENTATION_RULES`에 판정 변경이 있는가 — **아니오**(§4.3, §5 D-E3, §6).
- `BASELINE.md`·`GLOSSARY.md`·기존 ADC/ADR을 변경했는가 — **아니오**. 이 ADC 파일 1건만 신규 작성(미커밋 상태에서 작성, 이후 커밋은 이 파일에 한정).
- 필요 이상의 새 Governance 문서를 만들었는가 — **아니오**(§8) — 후속 ADR은 조건부 언급만, 작성하지 않음.
- 코드·기존 experimental project(E4/E5/E6/E7)를 변경했는가 — **아니오**.
- 이 ADC 자체의 Architecture/Governance Review를 수행했는가 — **예**(§9), 판정 = PASS.
- Commit/PR을 했는가 — 이 ADC 작성 시점 기준 아직 — 사용자 지시대로 이 뒤에 커밋 + PR만 진행(Merge는 하지 않음).
