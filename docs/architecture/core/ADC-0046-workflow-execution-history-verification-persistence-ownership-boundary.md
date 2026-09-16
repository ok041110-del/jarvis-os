# ADC-0046: Workflow Execution History / Verification Persistence Ownership Boundary 판단 (RFC-0044 후속)

## 목적

`docs/architecture/core/RFC-0044-narrow-execution-history-verification-persistence-boundary.md`
§12 Decision Candidate — **"Option B(Scope §4의 6개 기록을 파일로
남기는 것)를 `hqs/development/HANDOVER.md`의 영속 저장소 금지 조항의
Scoped 예외로 Accept할 것인가, 그리고 그 caller는 누구인가"** — 에
대해 판단한다.

근거는 RFC-0044와 그것이 재확인한 RFC-0043
(`docs/architecture/core/RFC-0043-execution-history-evidence-persistence-architecture.md`)
으로만 한정하되, 이 ADC 작성 시점에 다음을 독립적으로 재조사해
드리프트 여부를 확인한다(RFC-0044 §2.1과 동일한 방법): `BASELINE.md`
§16, `docs/decisions/adc/ADC.md`, `hqs/development/BASELINE.md`,
`hqs/development/HANDOVER.md`, `hqs/development/IMPLEMENTATION_RULES.md`,
Workflow Adapter 관련 ADC(`ADC-0019`/`ADC-0020`/`ADC-0022`/`ADC-0023`),
`docs/core/execution-layer/ADC-0002-execution-result-contract.md`,
`ADR-0003`(`docs/architecture/core/`), `ADC-0013`. 새로운 실험·Evidence는
만들지 않는다 — 단, 이 ADC 작성 직전 세션에서 실제로 완료된 작업 하나
(Command Center Terminal → `hqs/development/workflow.py::run_workflow()`
실 E2E 연결, `projects/dashboard-shell-mvp/`, persistence 미도입)는
이 저장소에 이미 존재하는 사실이므로 Evidence로 인용한다(§Q6).

### 이 ADC가 답하지 않는 것

- Persistence의 실제 파일 포맷·스키마·저장 경로.
- Persistence를 트리거하는 구체적 CLI/스크립트 구현.
- `execution_id` 채번 방식, 파일 이름 규칙.
- partial/incomplete execution 기록 처리 방식(RFC-0044 §14 Q4).
- Evidence artifact reference의 보존 기간·접근 범위(RFC-0044 §14 Q5).
- Evidence를 Kernel Concept으로 신설할지 여부(RFC-0044 §14 Q3, §6.5)
  — 이 ADC는 이 질문에 답하기 위한 전제(§6.2 caller 식별)조차 아직
  성립하지 않는다고 판단하므로(§Decision), 이 질문 자체에 도달하지
  않는다.
- Live Execution State, Live Progress, Background Execution, Scheduler,
  Runtime, Retry, Resume, Cancellation, Distributed Execution — RFC-0044
  §5·Non-Goals 그대로 이 ADC도 제외한다.
- Multi-Task.
- `check_results`/`KNOWN_CHECK_NAMES` 등 Stage Data Contract(Public
  Contract) 자체의 확장.
- ADC-02("Runtime 개념의 존폐")의 재개·재론.
- §16.3~§16.6의 어떤 Scoped Accept의 수정.
- Production Code(`core/`, `hqs/`, `dashboard/`, `projects/`)의 수정.
  이 ADC는 문서만 작성한다.

이 ADC가 판단하는 것은 다섯이다: **(1) RFC-0044 §12의 좁은 질문 —
Option B를 이번에 Scoped 예외로 Accept할 수 있는가, (2) 그 판단에
필요한 Evidence가 이 저장소의 실제 Accept 선례(`ADC-0013`/`ADC-0016`/
`ADC-0017`) 기준을 충족하는가, (3) Option A/C/D는 각각 어떻게
판단되는가, (4) ADC-02·`ADC-0002`(Execution Result)와 이 판단이 실제로
독립적인가, (5) Option B가 미결로 남는다면 재판단에 필요한 최소
조건은 무엇인가.**

---

## Q0. Architecture Intent만으로 지금 판단할 수 있는가

### 검토

`BASELINE.md` §16.3~§16.6이 각 Kernel Module을 Accept할 때 인용한
근거를 다시 보면, "사후 실행 기록을 어디에 남길 것인가"라는 질문을
사전에 예견한 절은 없다. §16.5(Multi-Task Result Store)조차 "저장
**전** 검증 게이트"만 다루고 "저장 자체"·"보존 기간"은 명시적으로
`ADC-0017` §Q6·§Implementation Boundary "제외"로 남겼다(RFC-0044
§6.2 인용과 동일). `hqs/development/BASELINE.md`의 "Not Included"에
Runtime이 명시돼 있을 뿐, Persistence 항목은 별도로 언급되지 않는다
— `HANDOVER.md` §What Claude Code Must Never Do가 "영속 저장소...
추가 금지"를 Frozen 규칙으로 못박은 것이 이 저장소가 가진 유일한
직접 신호다(금지 방향으로).

### Q0 결론

Architecture Intent는 이 질문에 침묵하지 않는다 — `HANDOVER.md`가
명시적으로 **금지**를 선언하고 있다. 따라서 이 질문은 `ADC-0011`류의
"양쪽 다 침묵" 상황이 아니라, "기존 금지 조항의 예외를 Evidence로
정당화할 수 있는가"라는 더 무거운 질문이다 — Not Accepted 쪽이
default이고, Accept 쪽이 입증 책임을 진다.

---

## Q1. Option A(현행 no-persistence 유지)

### 검토

- **기존 Architecture와의 충돌**: 없음. `run_workflow()`를 그대로 둔다.
- **ADC-02와의 관계**: 없음 — Runtime 개념 자체가 개입하지 않는다.
- **현재 Evidence가 직접 뒷받침하는 범위**: 전부 — 이 Option은 아무
  것도 새로 주장하지 않는다. 이미 현재 상태다.
- **추가 Architecture 결정이 필요한 범위**: 없음.
- **새 Evidence(이 ADC 작성 시점)**: 직전 세션에서 Command Center
  Terminal이 `/api/command`를 통해 실제 `run_workflow()`를 호출하고
  Stage 01→05 결과(`FAIL` verdict 포함, 실제 Engine 호출 포함 약 2분
  소요)를 **persistence 없이** 단일 HTTP 응답으로 그대로 전달하는
  경로가 실제로 동작함을 확인했다(§Q6에서 상술). 이는 Option A가
  "실행 결과를 실시간으로 한 번 보여주는" 요구는 **이미 persistence
  없이 충족 가능하다**는 것을 실제 코드로 보여준다 — RFC-0043/0044
  작성 시점에는 없었던 새 사실이다.

### Q1 결론

Option A는 언제든 선택 가능한 기본값이며, 이 ADC 작성 시점 기준으로
그 유효 범위(단발 real-time round-trip)가 실제 코드로 한 번 더
확인됐다. 다만 이것이 채우지 못하는 것 — **세션이 끝난 뒤에도 그
결과를 다시 조회하는 것** — 은 여전히 채워지지 않는다(같은 세션
관찰: 새로고침하면 Terminal 이력도 사라짐). Option A는 RFC-0044가
Problem(§3)으로 정의한 질문 자체에는 답하지 않는다 — 그 질문은
그대로 남는다.

---

## Q2. Option D(Runtime/Scheduler 중심 Persistence)

### 검토

- **기존 Architecture와의 충돌**: 크다. `IMPLEMENTATION_RULES.md`의
  "Scheduler/우선순위/Workflow orchestration/Dynamic Routing... 구현
  금지" 조항과 정면 충돌한다.
- **ADC-02와의 관계**: 직접·선행적. `docs/decisions/adc/ADC.md`
  ADC-02(Open·NOW)가 해소돼야 이 Option에 진입할 수 있다 — 이 ADC가
  독립적으로 재확인했다(§Q4).
- **현재 Evidence가 직접 뒷받침하는 범위**: 없음 — RFC-0043/0044
  어디에도 Runtime/Scheduler 중심 구조가 실제로 필요하다는 Evidence가
  없다.
- **추가 Architecture 결정이 필요한 범위**: 전체 — ADC-02 해소 자체가
  선행조건이며, 그 해소는 이 ADC/RFC-0044 트랙 하나로 열 수 있는
  범위가 아니다(`ADC-0021` §8 Gate B/C와 동일 구조의 선행조건).

### Q2 결론

**Not Accepted (based on current evidence).** ADC-02가 Open으로 남아
있는 한 이 Option은 애초에 판단 대상이 아니다 — RFC-0043 §22·RFC-0044
§7의 동일 결론을 독립적으로 재확인한다. 부족한 Evidence: ADC-02
자체의 해소(별도의, 훨씬 큰 절차).

---

## Q3. Option C(전담 Persistence Service/Store)

### 검토

- **기존 Architecture와의 충돌**: 크다. `IMPLEMENTATION_RULES.md`의
  "Memory Service(영속화 계층) 구현 금지", "Registry 구현 금지·일반화
  금지" 조항과 직접 충돌한다.
- **ADC-02와의 관계**: 간접적 — "전담 서비스"가 실질적으로 Runtime의
  한 형태로 해석될 위험이 있다(RFC-0044 §7 Option C 분석과 동일).
  ADC-02가 Open인 채로 이 Option을 채택하면 그 방향(Runtime 유지)으로
  선판단하는 효과를 낸다.
- **현재 Evidence가 직접 뒷받침하는 범위**: 없음 — 전담 서비스가
  필요하다는 관찰은 어디에도 없다. RFC-0043/0044의 Evidence는 "저장
  위치가 전혀 없다"는 사실만 확인했을 뿐, "그 저장 위치가 서비스
  수준이어야 한다"는 관찰은 없다.
- **추가 Architecture 결정이 필요한 범위**: 크다 — 새 Kernel Component
  후보에 준하는 검토(§16.7류 신규 Module 승격 절차)가 별도로 필요하다.

### Q3 결론

**Not Accepted (based on current evidence).** 이 ADC 하나로 열기에는
Governance 비용이 범위를 벗어난다 — RFC-0044 §12의 동일 결론을
재확인한다. 부족한 Evidence: 파일 기반 저장(Option B)으로 해결되지
않는 구체적 요구(동시 다중 쓰기, 트랜잭션 무결성 등)가 실제로 관찰된
사례 — 현재 없음.

---

## Q4. ADC-02와의 관계 — 독립 재확인

### 검토

RFC-0044 §9가 이미 "Runtime 유지안과 충돌하지 않는다 / Runtime
폐기안과 충돌하지 않는다 / ADC-02 결정 이후에도 유지 가능해 보인다"고
분석했다. 이 ADC는 그 분석을 재론하지 않고, 독립적으로 같은 질문을
다시 확인한다.

- Option B(파일 기반, caller-owned)는 `run_workflow()` 호출 지점을
  감싸는 wrapper일 뿐이다 — Runtime이 그 호출을 대신하게 되더라도,
  또는 Runtime이 끝까지 폐기되더라도, "결과가 나온 뒤 그것을 파일로
  남긴다"는 동작 자체는 **무엇이 그 결과를 만들어냈는지와 무관하게**
  성립한다.
- 단, 이 독립성은 **caller가 확정된 이후**에만 안정적이다 — caller가
  누구인지에 따라 "그 caller가 Runtime의 일부가 되는가"라는 질문이
  후속으로 열릴 수 있다(예: caller가 Development HQ CLI라면 무관하지만,
  caller가 미래의 Execution Host/Workflow Adapter 구현체 내부라면
  ADC-02와 다시 얽힐 수 있다). RFC-0044 §6.2가 이미 이 caller 질문에
  답하지 않았고(§Q5에서 재확인), 이 ADC도 답하지 않는다.

### Q4 결론

Option B의 **추상적 존재**(파일로 남긴다는 개념)는 ADC-02와
독립적이라는 RFC-0044의 판단에 동의한다. 그러나 이 독립성은 caller가
정해지기 전까지는 **조건부**다 — caller 확정이 이 ADC의 범위 밖으로
남는 한(§Decision), "완전히 독립적"이라고 확정할 수는 없고 "현재
분석상 독립적으로 보인다"는 RFC-0044의 잠정적 표현을 그대로 유지해야
한다. ADC-02는 이 ADC로 재개되지 않는다.

---

## Q5. `ADC-0002`(Execution Result Contract)와의 혼동 방지

### 검토

`docs/core/execution-layer/ADC-0002-execution-result-contract.md`를
직접 확인했다(작업 지시 §확인 대상 무관하게, 혼동 방지를 위해 이
ADC가 별도로 재조사). 그 문서는 **Execution Layer 트랙**(`docs/core/
execution-layer/`)에 속하며, **단일 Engine 호출 1회**의 산출물(신규
파일/로그/텍스트 보고 등)을 "단일 문자열/목록/참조" 세 후보 중
무엇으로 묶을지를 판단했다(Decision: Candidate 2, 목록). 그 문서 §목적
"이 ADC가 답하지 않는 것"은 명시적으로 **"Execution State의 상태
전이 규칙(별도 사안)"**을 제외한다.

이 ADC(`ADC-0046`, `docs/architecture/core/` 트랙)가 다루는 것은
그와 다른 질문이다 — **여러 Stage(01~05)로 구성된 하나의 Workflow
Run 전체**가 실행을 마친 뒤 그 이력(무엇을 언제 실행했는가)과 판정
근거(Evidence)를 사후에 어디에 남길 것인가다. 이름이 같은 `ADC-0002`
파일이 세 트랙(`docs/architecture/core/ADC-0002-kernel-definition.md`,
`docs/core/execution-layer/ADC-0002-execution-result-contract.md`,
`docs/governance/adc/ADC-0002.md`)에 각각 존재하며, 이 ADC가 재확인·
계승하는 것은 그중 어느 것도 아니다 — Execution Layer의 `ADC-0002`가
정의한 "Execution Result(단일 Engine 호출 1회의 산출물 목록)"와
"Workflow Execution History(Workflow Run 1회 전체의 이력)"는 서로
다른 대상이며, 하나가 다른 하나를 포함하거나 대체하지 않는다.

### Q5 결론

두 개념은 혼동되지 않는다. 이 ADC는 `docs/core/execution-layer/
ADC-0002`의 Decision(Execution Result = 목록)을 변경하지도, 그
범위를 Workflow 수준으로 확장하지도 않는다 — 완전히 별개 트랙, 별개
질문으로 유지한다.

---

## Q6. 새 Evidence — Command Center Terminal의 실제 E2E 연결이 이 판단에 미치는 영향

### 검토

이 ADC 직전 세션에서 `projects/dashboard-shell-mvp/serve_dashboard.py`에
`_resolve_or_execute()`가 추가되어, Command Center Terminal이
`/api/command`를 통해 실제 `hqs/development/workflow.py::run_workflow()`
를 호출하고 그 결과(Stage 01→05 dict, `FAIL` verdict 포함)를 HTTP
응답 1회로 돌려주는 경로가 실제로 동작함을 라이브 서버로 확인했다.
이 경로는 **persistence를 전혀 추가하지 않았다** — 응답을 보낸 뒤
그 실행이 있었다는 사실은 다시 사라진다(`devhq-command-center/
README.md` "Command → Workflow E2E v0.1" 절이 이를 명시).

이 사실이 RFC-0044의 Problem(§3)·Scope(§4)에 미치는 영향:

- RFC-0044 §3이 지적한 "**Execution Identity가 없다**"·"**Stage
  History가 없다**"는 문제는 이 새 경로로도 전혀 해결되지 않았다 —
  오히려 실제 코드로 재확인됐다. 이 경로는 "한 번의 요청-응답"
  범위에서만 결과를 보여줄 뿐, 그 요청이 끝난 뒤에는 RFC-0044가
  Scope(§4)로 정의한 7종 기록 중 어느 것도 남지 않는다.
- 동시에, 이 경로는 RFC-0043 §6이 나열한 Command Center 요구사항 중
  "실행 결과를 실제로 본다"는 부분은 **persistence 없이도** 충족
  가능함을 보여준다(§Q1) — 즉 persistence가 필요한 것은 "실시간
  1회 조회"가 아니라 정확히 RFC-0044가 좁힌 "**사후** 조회"뿐이라는
  경계가 실제 코드로 한 번 더 확인됐다.
- 이 경로는 Command Center가 Writer가 아니라 Reader로만 남아야 한다는
  RFC-0043 §20/§6.4 원칙과도 일치한다 — Terminal은 `run_workflow()`의
  반환값을 그대로 보여줄 뿐, 그 값을 판정·수정·저장하지 않는다.

### Q6 결론

이 새 Evidence는 RFC-0044의 Problem/Scope 정의를 **약화시키지
않는다** — 오히려 "무엇이 persistence 없이 되는지"와 "무엇이 여전히
안 되는지"의 경계를 실측으로 좁혀 확인했다. 그러나 이 Evidence는
"post-execution History가 실제로 필요하다"는 **소극적** 확인
(그 문제가 아직 해결되지 않았다는 재확인)일 뿐, "그것을 지금
Accept해야 한다"는 **적극적** 근거(운영상 실제 피해, 반복 관찰된
필요)를 새로 제공하지 않는다 — §Decision의 판단에 영향을 주지 않는다.

---

## Q7. Option B — 이번에 Accept할 수 있는가

### 검토: 기존 Architecture와의 충돌

RFC-0044 §7·§10이 이미 정리한 대로, Option B는 `hqs/development/
HANDOVER.md`의 "영속 저장소... 추가 금지" 조항과 **문언상 정면으로
충돌**한다. §16 Kernel Module 어느 것도 건드리지 않고(§16.5/§16.6
caller-owned 원칙과 정합적, RFC-0044 §6.3), 새 Registry/Scheduler/
Engine Gateway를 요구하지 않는다는 점에서 Option C/D보다 훨씬 좁다 —
그러나 "좁다"는 것이 곧 "Evidence가 충분하다"는 뜻은 아니다.

### 검토: ADC-02와의 관계

§Q4에서 확인한 대로 조건부 독립적이다 — caller 확정 전까지는 잠정
판단이다.

### 검토: 현재 Evidence가 직접 뒷받침하는 범위

- **뒷받침되는 것**: "현재 persistence가 전혀 없다"는 사실(직접 코드
  확인, 모호함 없음), "그 형태(Public Contract)는 이미
  `hqs/development/BASELINE.md`가 확정했다"는 사실, "§16.5/§16.6이
  이미 같은 성격의 caller-owned 좁은 Accept 선례를 두 번 만들었다"는
  사실. 이 세 가지는 모두 문서·코드를 직접 읽어 확인 가능하며 이견의
  여지가 없다.
- **뒷받침되지 않는 것**: "이 persistence의 부재가 실제로 운영상
  문제를 일으켰다"는 관찰. `ADC-0013`(Execution Host)은 "부재 시
  실제 정확성 결함 재현"을 포함한 5개 Prototype Evidence로 Accept
  했고, `ADC-0017`(Result Store)은 실제 Production 환경에서 4회
  재현된 콘텐츠 손상 피해(`pg-hq-verify`)로 Accept했다. 이 ADC가
  가진 것은 그와 다른 종류다 — Command Center의 **UI Contract가
  이미 요구하는 필드**(RFC-0043 §3)라는 사전 설계 요구와, "MVP
  단계에서 아직 아무 실제 실행 기록도 없다"(RFC-0043 §2.1
  `export_real_snapshot.py` 조사에서 이미 확인된 사실 — "Task ID에
  대응하는 실제 실행 기록은 존재하지 않는다")는 사실뿐이다. 부재로
  인한 **재현 가능한 결함이나 실제 피해 사례**는 RFC-0043/0044 어디
  에도 없다 — §Q6의 새 E2E 연결도 이 공백을 메우지 않는다.
- Rule A/B(`docs/governance/README.md`)는 RFC 트리거 기준(RT 충족 또는
  동일 Tag Observation 3회)이며, RFC-0043/0044는 이미 그 기준을
  통과해 RFC로 성립했다 — 이 사실이 곧 **ADC Accept의 충분조건은
  아니다**. `ADC-0013`/`ADC-0016`/`ADC-0017`은 RFC 성립 이후에도
  각각 별도로 "부재 시 결함 재현" 또는 "실제 피해 반복"이라는 추가
  Evidence를 Accept의 근거로 요구했다 — 이 ADC는 그 선례를 따른다.

### 검토: 추가 Architecture 결정이 필요한 범위

- **caller 식별**(RFC-0044 §6.2가 이미 답하지 못한 질문) — Kernel(§16
  어느 절도 지지하지 않음), Development HQ(`HANDOVER.md`와 정면
  충돌), Command Center(§6.4가 이미 배제 — Writer 금지) 세 후보 모두
  현재 Accept 근거가 없다. 이 질문에 답하지 않고는 "누가 예외의
  수혜자인가"조차 정의되지 않는다.
- **HANDOVER.md 조항의 실제 개정 절차** — Option B를 Accept하더라도
  그 자체로 `HANDOVER.md` 문구가 바뀌지 않는다(ADC는 ADR이 아니다).
- Evidence artifact reference의 보존 범위, partial record 처리 등
  RFC-0044 §14가 이미 Open Question으로 남긴 항목들.

### Q7 결론

**Not Accepted (based on current evidence) — 그러나 완전한 기각이
아니라, 이 저장소의 실제 Accept 선례가 요구해 온 Evidence 종류
(재현 가능한 결함 또는 실제 운영 피해)가 아직 갖춰지지 않았다는
뜻이다.** Option B는 A/C/D 중 유일하게 "부족한 것이 Evidence뿐이고
Architecture 원칙과는 이미 정합적인" Option이다 — RFC-0044 §12의
판단(Option B가 실질적 후보)에 동의하되, "다음 후보로 유력하다"와
"지금 Accept할 근거가 있다"는 서로 다른 문장이라는 것이 이 Q7의
핵심 결론이다.

---

## Decision

**Not Accepted (based on current evidence) — Boundary Question은
Open으로 남는다.**

RFC-0044 §12의 질문("Option B를 Scoped 예외로 Accept할 것인가, 그
caller는 누구인가")에 대해 **이번에는 Yes를 선택하지 않는다.** 다음을
함께 확정한다.

1. **Option D(Runtime/Scheduler 중심)는 Not Accepted** — ADC-02(Open)
   해소가 선행돼야 하며, 이 ADC/RFC-0044 트랙이 열 수 있는 범위가
   아니다(§Q2). ADC-02는 재개되지 않는다.
2. **Option C(전담 Persistence Service)는 Not Accepted** — Memory
   Service/Registry 금지 조항과 직접 충돌하고, 신규 Kernel Component
   후보에 준하는 별도 절차가 필요하다(§Q3).
3. **Option A(No Persistence)는 그대로 유효한 기본값이다** — 추가
   Governance 없이 계속 선택 가능하며, 이 ADC 작성 시점의 새 Evidence
   (§Q6 — Command Center Terminal의 실제 E2E 연결)가 그 유효 범위
   (단발 실시간 조회)를 실제 코드로 재확인했다. Option A가 채우지
   못하는 것(사후 조회)은 그대로 남는다.
4. **Option B(Narrow File-based)는 Architecture 원칙과 충돌하지
   않으며 유일하게 실질적인 후보로 남지만, 이 ADC는 그 Scoped 예외를
   승인하지 않는다** — `hqs/development/HANDOVER.md`의 명시적 금지
   조항을 뒤집기에는, 이 저장소가 유사 사례(`ADC-0013`/`ADC-0016`/
   `ADC-0017`)에서 실제로 요구해 온 Evidence 종류(부재 시 결함 재현
   또는 반복 관찰된 실제 피해)가 갖춰지지 않았다(§Q7).
5. **caller 식별 질문(§6.2)은 이 ADC가 답하지 않는다** — Option B
   자체가 Accept되지 않았으므로 이 질문은 아직 열 필요가 없다.
6. **`ADC-0002`(Execution Result Contract, Execution Layer 트랙)와
   이 판단이 다루는 대상(Workflow Execution History)은 서로 다른
   개념이며 혼동되지 않는다**(§Q5) — 어느 쪽도 서로를 대체·확장하지
   않는다.
7. ADC-02, §16.3~§16.6의 어떤 Scoped Accept도 이 Decision으로
   변경되지 않는다.

### Reason

- Q0 — `HANDOVER.md`가 명시적으로 금지를 선언하고 있어, 이 질문은
  침묵 상태의 "양쪽 다 근거 없음"이 아니라 "기존 금지의 예외를
  Evidence로 정당화해야 하는" 더 무거운 구도다.
- Q1 — Option A는 이미 유효하며, 새 E2E 연결(§Q6)이 그 유효 범위를
  재확인했다.
- Q2/Q3 — Option D/C는 각각 ADC-02·Memory Service 금지와 직접
  충돌해 이 ADC로 열 수 있는 범위가 아니다.
- Q4 — Option B의 ADC-02 독립성은 caller 확정 전까지 조건부다.
- Q5 — `ADC-0002`(Execution Result)와 이 ADC(Workflow Execution
  History)는 서로 다른 트랙, 다른 질문이며 혼동되지 않는다.
- Q6 — 새 E2E 연결 Evidence는 문제 정의를 재확인했을 뿐, Accept를
  정당화할 적극적 근거(피해·결함 재현)를 새로 제공하지 않는다.
- Q7 — Option B는 원칙적으로 정합적이나, 이 저장소의 실제 Accept
  선례가 요구해 온 Evidence 종류가 갖춰지지 않았다.

### Decision Rationale

RFC-0044 §12는 Option B를 "실질적 후보"로 판단했고, 이 ADC는 그
판단에 동의한다 — 그러나 "실질적 후보"와 "Accept할 근거가 충분하다"는
서로 다른 주장이다. 이 저장소가 실제로 Scoped Accept를 내린 선례
(`ADC-0013`의 5개 Prototype·결함 재현 포함 Evidence, `ADC-0016`의
Architecture Intent가 명확히 가리키는 상황에서의 1건 Accept, `ADC-0017`의
4회 재현된 실제 Production 피해)는 모두 "부재가 실제로 무엇을
망가뜨렸는가" 또는 "Architecture Intent가 이미 방향을 가리키고
있었는가"를 최소한의 형태로라도 보여줬다. 이 ADC가 가진 Evidence는
"필요할 것 같다"는 설계 요구(Command Center UI Contract)와 "아직 아무
기록도 없다"는 구조적 사실뿐이며, `HANDOVER.md`는 오히려 반대 방향
(금지)을 명시적으로 가리키고 있다(§Q0) — 이는 `ADC-0011`류의 "양쪽
다 근거 없음" 상황보다도 Accept에 불리한 구도다. 이 비대칭을 무시하고
Accept로 나아가는 것은 "RFC-0044의 Decision Candidate를 자동으로
Architecture Decision으로 승격"하는 것과 실질적으로 같은 효과를
낸다 — 이 ADC가 피하려는 바로 그것이다.

---

## 부족한 Evidence — 무엇이 있어야 Option B를 재판단할 수 있는가

새로 만들지 않는다 — 지금 확인된 공백만 기록한다.

1. **부재로 인한 재현 가능한 결함 또는 반복 관찰된 실제 운영 피해** —
   `ADC-0013`/`ADC-0017`이 요구한 것과 같은 종류. 예: Command Center를
   실제 Dogfooding에서 반복 사용하는 과정에서, "이전 실행 결과를 다시
   볼 수 없어서" 실제로 발생한 문제(재작업, 잘못된 판단, 신뢰 저하 등)
   가 관찰되는 경우.
2. **caller 후보 자체의 존재** — 현재 Kernel/Development HQ/Command
   Center 세 후보 모두 `HANDOVER.md`·§16 어느 것과도 정합적이지
   않다(§Q7). 넷째 후보가 식별되거나, 위 셋 중 하나가 예외를 감당할
   수 있다는 별도 근거(예: Development HQ Baseline 자체의 개정 논의)
   가 먼저 필요하다.
3. **`HANDOVER.md` "영속 저장소... 추가 금지" 조항 자체의 재검토
   여부** — 이 조항이 Frozen인 이유(MVP 범위 유지)가 여전히 유효한지,
   아니면 Development HQ MVP가 이제 그 범위를 넘어선 단계인지에 대한
   별도 판단(`hqs/development/HANDOVER.md`를 직접 개정하는 판단은 이
   ADC의 권한 밖이다).
4. Evidence artifact reference가 가리키는 파일의 보존 기간·접근
   범위에 대한 최소 설계 방향(RFC-0044 §14 Q5) — Option B를 Accept
   하더라도 이 질문에 먼저 답하지 않으면 "참조"가 실제로 무엇을
   가리키는지 불분명하다.

이 넷 중 하나라도 확인되면 재검토 대상이 된다. 이 ADC는 그 재검토를
지금 수행하지 않는다.

---

## Risks

- **"Not Accepted"가 "이 문제를 무시해도 된다"로 오독될 위험** — 그런
  뜻이 아니다. RFC-0044 §3이 정의한 Problem(Execution Identity 부재,
  Stage History 부재, 사후 조회 불가)은 이 Decision으로 전혀 해소되지
  않는다 — 단지 "지금 그 해소 방법(Option B)을 Architecture 수준에서
  승인할 근거가 아직 없다"는 것만 확정한다.
- **Command Center Real Data Adapter가 반복적으로 이 공백에 부딪힐
  위험** — `devhq-command-center/README.md`가 이미 "Task별 실행
  기록... Mock 유지"를 명시했으므로 새로운 피해는 아니지만, Dogfooding이
  계속되면 §부족한 Evidence 1항의 관찰이 자연스럽게 쌓일 가능성이
  높다 — 그 경우 이 ADC는 즉시 재검토 대상이 된다.
- **"Evidence가 없다"는 판단 자체가 향후 재확인 없이 고착될 위험** —
  이 ADC가 확인한 것은 "이 ADC 작성 시점"의 Evidence 상태다. 다음
  세션이 이 Decision을 인용할 때, Evidence 공백이 실제로 채워졌는지
  먼저 확인하지 않고 "이미 Not Accepted였다"로만 인용하면 안 된다.
- **RFC-0043/0044가 이미 수행한 방대한 분석이 낭비로 여겨질 위험** —
  아니다. 이 ADC의 Decision은 그 분석이 틀렸다는 것이 아니라, 분석이
  Boundary Question을 정확히 좁혔고(Option B가 유일한 실질적 후보라는
  판단은 유지) 이제 남은 것은 Evidence 축적뿐이라는 것을 확정한다.

**재검토 조건**: 위 "부족한 Evidence" §1~4 중 하나라도 확인되면, 이
Decision은 기존 Governance 절차(RFC → ADC → ADR)를 통해 재검토
대상이 된다. 재검토는 새 RFC가 아니라 이 ADC를 갱신하거나 후속 ADC를
여는 형태가 될 수 있다 — RFC-0043/0044가 이미 Boundary Question을
충분히 좁혀 놓았으므로, 재검토 시점에 그 두 RFC를 다시 여는 것은
불필요할 가능성이 높다(단, 이 판단도 재검토 시점에 다시 확인해야
한다).

## Next Step

**ADR 불필요 — 이 Decision은 Boundary를 이동시키지 않는다.**

`Not Accepted`는 Baseline 변경을 요구하지 않는다(`ADC-0011`과 동일
판단 구조) — `BASELINE.md`·`hqs/development/HANDOVER.md`·
`hqs/development/IMPLEMENTATION_RULES.md` 중 어느 것도 이 ADC로
갱신되지 않는다.

1. 이 ADC를 `docs/architecture/core/`에 등록된 상태로 유지한다 — 별도
   Registry 갱신은 필요 없다(`docs/decisions/adc/ADC.md`는 Jarvis OS
   수준 ADC-01~12 전용이며 이 트랙과 무관, RFC-0044 §2.1 인용과 동일).
2. Command Center/Development HQ Dogfooding이 계속되는 동안, "부족한
   Evidence" §1(재현 가능한 결함 또는 반복 관찰된 피해)이 실제로
   발생하는지 관찰한다 — 이 ADC가 그 관찰을 지금 수행하지 않는다.
3. `hqs/development/HANDOVER.md` "영속 저장소... 추가 금지" 조항은
   그대로 Frozen으로 유지된다 — 이 ADC가 그 조항에 어떤 예외도 만들지
   않는다.
4. Live Progress/Cancel/Retry/Resume(Option C/D 영역)은 계속 별도의,
   더 나중 RFC 대상으로 남는다 — RFC-0044 §15 Required ADC/ADR
   Follow-up과 동일.

## Governance Chain 검증

`RFC-0043`(Proposed, 분석만) → `RFC-0044`(Proposed, Option B로 범위
축소, Decision Candidate만 제시) → 이 ADC(`ADC-0046`, **Not
Accepted** — Option A 유효 재확인, Option C/D Not Accepted, Option B는
원칙적으로 정합적이나 Evidence 부족으로 Not Accepted, caller 식별
질문 미도달, ADC-02·`ADC-0002` 재확인만 하고 재개하지 않음) → 후속
ADR 없음(Boundary 이동 없음). RFC-0044가 후속 ADC(이 ADC)에 위임한
질문(§12 Decision Candidate, §14 Open Questions 1~5) 중 §12는 이
ADC가 Not Accepted로 답했고, §14의 나머지(caller 식별 등)는 §12가
Not Accepted이므로 이 ADC가 **도달하지 않는다**(§목적 "이 ADC가
답하지 않는 것"). RFC-0044의 Non-Goals(Live Progress/Cancel/Retry/
Resume/Distributed/Multi-Task 등)는 이 ADC도 하나도 건드리지 않았음을
각 Q절에서 확인했다.

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**. Not Accepted는
  Boundary를 이동시키지 않는다.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**.
- Contract Change — **없음**.
- Baseline 문서(`BASELINE.md`, `hqs/development/HANDOVER.md`,
  `hqs/development/IMPLEMENTATION_RULES.md`, `docs/decisions/adc/ADC.md`)
  를 변경했는가 — **아니오**.
- ADC-02를 재개·재론했는가 — **아니오**(§Q4, Decision 7).
- `ADC-0002`(Execution Result Contract)의 Decision을 변경했는가 —
  **아니오**(§Q5).
- §16.3~§16.6의 어떤 Scoped Accept도 수정했는가 — **아니오**(Decision 7).
- ADR이 필요한가 — **아니오**(§Next Step).
- Production Code(`core/`, `hqs/`, `dashboard/`, `projects/`)를
  수정했는가 — **아니오**.

## Self Review

- Evidence만 사용했는가 — **Pass**. RFC-0043·RFC-0044와 그것들이
  인용한 문서/코드, 그리고 이 ADC 작성 직전 세션에서 이미 완료된
  Command Center E2E 연결(§Q6, 새 실험이 아니라 이미 존재하는 사실의
  인용)만 사용했다.
- RFC-0044 §12의 Decision Candidate를 자동으로 Accept했는가 —
  **아니오**(§Q7, §Decision — 명시적으로 Not Accepted).
- Evidence가 부족한 부분을 결정된 사실처럼 서술했는가 — **아니오** —
  §부족한 Evidence 절에서 공백을 명시적으로 기록했다.
- Option A/B/C/D 각각에 대해 기존 Architecture 충돌·ADC-02 관계·
  Evidence 뒷받침 범위·추가 결정 필요 범위를 구분했는가 — **Pass**
  (§Q1~§Q3, §Q7).
- ADC-02를 재개했는가 — **아니오**(§Q4).
- `ADC-0002`(Execution Result)와 Workflow Execution History를
  혼동했는가 — **아니오**(§Q5, 명시적으로 구분).
- 새 Execution Entity/Execution Identity Contract/Execution Lifecycle
  Contract를 만들었는가 — **아니오**.
- Execution Host를 Identity/Lifecycle/Persistence Manager로
  확장했는가 — **아니오** — §16.3은 이 ADC에서 언급조차 되지 않는다
  (해당 없음).
- Live Execution State/Background/Scheduler/Runtime/Retry/Resume/
  Cancellation/Distributed Execution/Multi-Task를 결정 대상에
  포함했는가 — **아니오**.
- RFC-0044의 7개 persistence record scope(§4)를 임의로 확대했는가 —
  **아니오** — 이 ADC는 그 Scope 자체를 재론하지 않았고 인용만 했다.
- Architecture/Contract 구현을 했는가 — **아니오**.
- dashboard/persistence code/database/file store를 구현했는가 —
  **아니오**.
- 적절한 다음 ADC 번호를 기존 파일과 충돌 없이 확인했는가 — **Pass**
  (`docs/architecture/core/`의 기존 ADC는 `ADC-0001`~`ADC-0045`까지이며,
  이 문서는 `ADC-0046`).
