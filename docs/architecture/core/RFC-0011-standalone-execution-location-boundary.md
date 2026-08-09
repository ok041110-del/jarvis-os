# RFC-0011: Kernel/HQ에 속하지 않는 별도 실행 위치 — Architecture Concept으로서의 Boundary (ADC-0010 C6 후속)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (ADC-0010 C6 조사 후속)
**대상**: `ADC-0010-engine-caller-location-boundary.md`가 Not Accepted로
남긴 C6("별도 스크립트/함수")를 공식 Architecture 후보로 다루려면,
그보다 먼저 "Kernel/HQ에 속하지 않는 별도 실행 위치"라는 것을
Jarvis OS Architecture의 공식 Concept으로 인정할 수 있는지가 결정돼야
한다 — 이 RFC는 그 선행 질문을 연다.
**Evidence**: `docs/architecture/core/ADC-0010-engine-caller-location-boundary.md`,
`docs/architecture/core/RFC-0010-engine-caller-location-boundary.md`,
`docs/core/execution-layer/ADC-0005-engine-connection-boundary.md`,
`docs/research/ENGINE-CONNECT-0002-execution-layer-results-wiring.md`,
`docs/research/ENGINE-CONNECT-0003-production-promotion-blocked.md`,
`docs/research/ENGINE-CONNECT-0004-adc-0010-c6-investigation.md`,
`docs/01_architecture/BASELINE.md` §6·§7·§10,
`development-hq/CONSTITUTION.md`("Architecture Freeze"),
`development-hq/BOUNDARY.md`,
`projects/development-hq-devkit/runner.py`,
`projects/development-hq-devkit/README.md`

> 본 RFC는 caller 위치를 선택하지 않는다. 새 Component를 설계하지
> 않는다. Engine Adapter를 설계하지 않는다. Boundary Question에
> 답하지 않는다 — 질문만 명확히 연다. ADC-01·ADC-02·Execution
> Result Consumer·C1~C5는 재조사하지 않는다 — 기존 결정으로만
> 인용한다. 새로운 실험을 하지 않는다.

## 0. 이 RFC가 열린 이유

`ADC-0010`은 caller 후보 6개(C1~C6)를 전수 판단했고 전부 Not
Accepted로 남겼다. `ENGINE-CONNECT-0004`(C6 단독 재조사)는 C6가
독립적인 Evidence를 얻지 못했다고 결론지으며, 그 이유의 핵심을
다음과 같이 지목했다: *"Baseline의 Concept Model·System Boundary
어디에도 '별도 스크립트/함수'라는 제3의 범주가 없다."* 즉 C6가
막힌 이유는 C6 자체의 결함이 아니라, C6가 요구하는 **더 상위의
질문**(그런 위치가 Architecture적으로 존재할 수 있는가)이 아직
한 번도 열린 적이 없기 때문이다. 이 RFC는 그 상위 질문을 연다 —
`ADC-0010` §부족한 Evidence 6번("C6 자체를 구체화하는 새 RFC가
필요하다")이 이미 요구한 절차다.

## 1. 왜 기존 Kernel/HQ 경계만으로 Production Engine caller 위치를 표현할 수 없는가

`BASELINE.md` §7 System Boundary는 책임을 **Jarvis OS(Kernel)**와
**HQ** 둘로만 나눈다. `ADC-0010`이 판단한 6개 후보를 이 두 범주에
대입하면:

| 후보 | 범주 | 결과 |
|---|---|---|
| C1 Kernel Engine Port/Adapter | Jarvis OS(Kernel) | 책임은 귀속되어 있으나 §10 Out of Scope로 실체가 없다(Not Accepted) |
| C4 Development HQ | HQ | Architecture Freeze(Engine Adapter/Model Routing)로 명시적 배제(Not Accepted) |

두 범주 모두 이미 Not Accepted다 — 그러나 그 이유가 서로 다르다.
C1은 "Kernel 범주 안에 있지만 아직 설계되지 않았다"는 **시간적
공백**이고, C4는 "HQ 범주 안에 있지만 그 범주 자신이 이 책임을
명시적으로 거부한다"는 **구조적 배제**다. 두 공백의 성격이 다르므로,
"Kernel 설계를 기다린다"거나 "HQ의 Freeze를 재론한다"는 방식으로는
둘 다 해결되지 않는다.

C2(Runtime)·C3(Session)도 각각 Kernel Concept으로 분류되지만
(Runtime은 §6 Service, Session은 애초에 미등재), 하나는 세부 구조가
Open(ADC-02)이고 하나는 개념 자체가 없다 — 둘 다 Kernel 범주 안에서
막혔다.

**남는 관찰**: `BASELINE.md`가 나눈 두 범주(Kernel/HQ) 안에서
후보를 찾는 시도는 5번(C1~C5) 전부 실패했다. `ADC-0010`이 그 5개를
Not Accepted로 판단한 근거를 재조사하지 않고 그대로 인용하면, 남는
가능성은 두 범주 중 하나를 새로 설계하는 것이 아니라(그것은 각각
Kernel Component Architecture 설계, HQ Freeze 재론이므로 이 RFC의
권한 밖), **애초에 이 두 범주만으로 Production Engine caller 위치를
표현할 수 있는가**를 묻는 것이다. 이 RFC는 그 질문을 연다.

## 2. 기존 Evidence에서 확인된 C6의 근거와 한계

`ENGINE-CONNECT-0004`가 이미 정리한 내용을 그대로 인용한다(재조사
아님, 인용).

**근거**

- `ADC-0005-engine-connection-boundary.md` Next Step의 예시 문구
  단 한 줄: *"caller(예: Development HQ ↔ Execution Layer를 잇는
  별도 스크립트나 함수)의 구현 문제가 된다."*
- `projects/development-hq-devkit/runner.py`가 Kernel도
  `development-hq/`도 아닌 위치(`projects/`)에서 기존 공개 함수를
  그대로 import해 순서대로 호출하는 실제 코드로서 존재한다 — "별도
  위치에 스크립트가 있을 수 있다"는 사실 자체는 저장소에 실존
  선례가 있다.

**한계**

- 그 선례(`runner.py`)는 Execution Layer를 전혀 참조하지 않는다
  (`grep -rl "execution_layer" projects/` 결과 0건, `ENGINE-CONNECT-0004`
  §Q1에서 확인).
- 그 선례는 스스로를 "Dogfooding 프로젝트(Testbed)"로 한정하고,
  README에서 "Engine Adapter... 이번 프로젝트 범위 밖"이라고
  명시한다 — C5(Dogfooding 스크립트)가 Not Accepted였던 것과 동일한
  자기 한정을 갖는다.
- `BASELINE.md` §6 Concept Model 10개 분류 어디에도 "별도 실행
  위치"에 해당하는 항목이 없다.

**결론(재확인, 새 판단 아님)**: C6는 예시 문구 한 줄과, 구조는
유사하나 역할은 명시적으로 다른 선례 하나만 가진다. 이 두 근거만으로
C6를 Accept할 수 없다는 `ENGINE-CONNECT-0004`의 결론을 이 RFC는
그대로 인용한다.

## 3. "별도 실행 위치" Concept을 도입할 경우 필요한 최소 범위

이 RFC는 이 Concept을 도입하지 않는다. 다만 도입**한다면** 최소
무엇이 결정되어야 하는지를 Evidence 기반으로 나열한다(선택이 아니라
목록화).

- `BASELINE.md` §6 Concept Model의 10개 분류(Entity/Definition/
  Process/Event/Service/Interface/Metadata/Policy/State/Resource)
  중 어디에 속하는 Concept인지, 아니면 11번째 분류가 필요한지.
- `BASELINE.md` §7 System Boundary의 "Jarvis OS의 책임" / "HQ의
  책임" 목록 중 어느 항목도 이 위치로 이관되지 않는다는 것을 —
  즉 이 Concept이 기존 두 범주의 책임을 침범하지 않는다는 것을
  — 어떻게 보장할지.
- `BASELINE.md` §10 Out of Scope("Component Design", "Implementation")
  가 이 새 Concept의 설계에도 적용되는지, 아니면 이 Concept은
  "설계"가 아니라 다른 성격(예: 배치 위치 지정)이라 Out of Scope
  밖인지.

이 세 항목 중 하나라도 답하려는 시도는 이미 새 Architecture 설계다
— 이 RFC는 그 답을 시도하지 않는다.

## 4. 소속 Namespace를 결정해야 하는 문제

`projects/development-hq-devkit`가 유일하게 확인된 "Kernel/HQ 밖"
실제 경로 선례다. 그러나 이 선례를 C6에 그대로 적용할 수 있는지는
열려 있다.

- 이 선례는 "Development HQ Platform을 사용해 만든 결과물"이라는
  성격(README: *"Development HQ는 Platform이고, 이 프로젝트는 그
  Platform을 사용해 만든 첫 번째 결과물이다"*)이지, "Execution
  Layer와 Development HQ를 모두 참조하는 독립 연결부"라는 성격이
  아니다 — 같은 최상위 디렉터리(`projects/`)를 재사용하는 것이
  타당한지, 아니면 이름·성격이 다른 새 디렉터리가 필요한지는
  Evidence로 결정되지 않는다.
- Namespace 결정은 "이 위치가 Kernel의 일부인가, HQ의 일부인가,
  둘 다 아닌가"라는 §1의 질문과 직결된다 — Namespace를 먼저
  정하면 그 범주 판단을 사실상 선결하게 된다. 이 RFC는 그 순서를
  뒤집지 않는다: Concept 존재 여부(§1의 Boundary Question)가
  Namespace보다 먼저 판단되어야 한다.

## 5. Engine Adapter 책임과의 관계

`BASELINE.md` §7은 "Engine 호출의 표준 인터페이스 제공
(Port/Adapter)"을 Jarvis OS(Kernel)의 책임으로 이미 Frozen해 뒀다.
`development-hq/CONSTITUTION.md` Architecture Freeze는 "Engine
Adapter"를 HQ 범위에서 명시적으로 금지한다. 이 두 결정은 이미
확정되어 있고, 이 RFC는 재론하지 않는다.

"별도 실행 위치" Concept이 도입된다면, 그 위치가 수행하는 일(외부
caller가 `call_engine()`을 호출하고 `results`를 채우는 것,
`ADC-0005` Q0가 이미 Accept한 것)이 **Engine Adapter와 같은 것인지
다른 것인지**가 반드시 구분되어야 한다 — 같은 것이라면 Kernel의
Frozen 책임(§7)과 충돌하거나 그 책임을 대신 수행하는 것이 되고,
다른 것이라면 무엇이 다른지(예: "표준 인터페이스 제공"이 아니라
"기존 공개 함수를 caller로서 순서대로 호출하는 것"이라는 차이)가
Evidence로 뒷받침되어야 한다. `projects/development-hq-devkit`가
스스로 "Engine Adapter는 범위 밖"이라고 선을 그은 것은, 이 구분이
실제로 필요하다는 것을 보여주는 선례이지, 구분의 답은 아니다. 이
RFC는 이 구분을 시도하지 않는다 — Boundary Question으로만 남긴다.

## 6. Production caller를 실제로 배치할 수 있는 후보 경계

이 RFC는 후보를 선택하지 않는다. 다만 §1~§5에서 열거한 질문들이
후속 ADC가 판단해야 할 "경계"를 구성한다는 것만 명시한다:

```
Concept 존재 여부(§1, §3)
        ↓
Namespace(§4) — Concept 존재가 Accept된 뒤에만 판단 가능
        ↓
Engine Adapter와의 관계(§5) — Concept 존재와 독립적으로도 먼저 판단 가능
        ↓
C6(또는 새 후보)를 실제 caller로 Accept할지(ADC-0010 재개 시)
```

이 순서 자체도 결정이 아니라 관찰이다 — Namespace가 Concept 존재
여부에 의존한다는 것(§4)과, Engine Adapter 구분(§5)이 Concept
존재 여부와 별개로 먼저 판단될 수 있다는 것은 §1~§5의 논리적
귀결일 뿐, 이 RFC가 새로 설계한 절차가 아니다.

## Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 질문만 연다.

**Kernel/HQ에 속하지 않는 별도 실행 위치를 Jarvis OS Architecture의
공식 Concept으로 둘 수 있는가?**

이 질문이 Yes로 판단되어야만 C6(또는 그와 유사한 후보)가 다시
검토 대상이 될 수 있다. No로 판단되면, Production Engine caller
위치는 §1이 확인한 대로 Kernel 범주(C1, 설계 선행 필요) 또는 HQ
범주(C4, 이미 배제) 안에서만 찾아야 한다는 뜻이 되며, 그 경우
caller 위치 문제는 이 RFC가 만든 것이 아니라 기존 두 범주 안의
미해결 상태(C1의 실체 부재, ADC-02의 Open 상태)로 되돌아간다.

## Out of Scope

- Boundary Question에 대한 답(Yes/No 판단).
- "별도 실행 위치" Concept의 실제 설계(이름, 필드, 책임 목록).
- Namespace의 실제 선택(`projects/` 재사용 여부 등).
- Engine Adapter와의 관계에 대한 실제 판단.
- caller 후보(C1~C6 또는 새 후보)의 실제 선택.
- Kernel Component Architecture 설계 — `BASELINE.md` §10 Out of
  Scope 그대로.
- ADC-01(Model 축과 Component 축의 대응 관계)·ADC-02(Runtime 존폐)
  재조사 — 기존 Not Accepted 결론만 인용한다.
- Execution Result Consumer의 재판단.
- C1~C5의 재조사 — `ADC-0010`의 판단을 그대로 인용한다.
- Development HQ, Kernel, Execution Layer의 어떤 코드도 수정하지
  않는다.
- 새로운 실험.

## Non-goals

- 이 RFC는 caller 위치를 결정하지 않는다.
- 이 RFC는 새 Component/Engine Adapter를 설계하지 않는다.
- 이 RFC는 새 실험을 수행하지 않는다 — `ADC-0010`, `RFC-0010`,
  `ADC-0005`, `ENGINE-CONNECT-0002~0004`, `BASELINE.md`,
  `development-hq/CONSTITUTION.md`, `development-hq/BOUNDARY.md`,
  `projects/development-hq-devkit/*`에 이미 기록된 내용만 인용했다.
- 이 RFC는 Architecture Baseline을 변경하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 위 Boundary Question에 답하지 않는다.
- 이 RFC는 ADC-01·ADC-02·Execution Result Consumer·C1~C5를 재조사하지
  않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. Boundary Question("별도 실행 위치를 공식 Concept으로 둘 수
   있는가")에 현재 Evidence로 답할 수 있는지 — 답할 수 없다면
   `ADC-0008`·`ADC-0009`·`ADC-0010`과 동일한 방식으로 Not
   Accepted와 부족한 Evidence만 기록한다.
2. Yes로 판단 가능하다면, §3(Concept 최소 범위)·§4(Namespace)·
   §5(Engine Adapter 관계)를 그 순서(§6)대로 후속 RFC/ADC에서
   각각 별도로 열지, 하나의 ADC로 묶을지.
3. No로 판단된다면, Production Engine caller 위치 문제가 다시
   C1(Kernel 설계 선행)·C4(HQ 배제, 재론 불가)로 되돌아간다는
   것을 명시적으로 기록한다.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance
절차(`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`: RFC → ADC →
ADR → Baseline Update)를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `ADC-0010`, `RFC-0010`,
  `ADC-0005`, `ENGINE-CONNECT-0002~0004`, `BASELINE.md`,
  `development-hq/CONSTITUTION.md`, `development-hq/BOUNDARY.md`,
  `projects/development-hq-devkit/*`에 실제로 기록된 내용만
  인용했다. 새 실험은 하지 않았다.
- caller 위치를 선택했는가 — **아니오**. §6은 판단 순서만 나열했고
  어느 위치도 채택하지 않았다.
- 새 Component/Engine Adapter를 설계했는가 — **아니오**. §3·§5는
  "무엇이 결정되어야 하는가"만 나열했고 답하지 않았다.
- ADC-01·ADC-02를 재조사했는가 — **아니오**. §1에서 상태만 인용했다.
- Execution Result Consumer를 재조사했는가 — **아니오**.
- C1~C5를 재조사했는가 — **아니오**. `ADC-0010`의 판단을 그대로
  인용만 했다(§1·§2).
- Boundary Question에 답했는가 — **아니오**. §Boundary Question은
  질문 형태로만 남겼다.
- ADC/ADR을 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
- Out of Scope 항목을 다뤘는가 — **아니오**.
