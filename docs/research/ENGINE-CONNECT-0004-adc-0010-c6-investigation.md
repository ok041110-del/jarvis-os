# ENGINE-CONNECT-0004: ADC-0010 C6("별도 스크립트/함수") 조사 — Production Caller 후보 승격 가능성

이 문서는 구현 문서가 아니다. `ADC-0010-engine-caller-location-boundary.md`
가 Not Accepted로 남긴 6개 caller 후보 중 C6("별도 스크립트/함수")를
독립적인 Production Caller 후보로 승격할 수 있는지 기존 Evidence만으로
조사한다. **C1~C5는 재조사하지 않는다. ADC-01·ADC-02·Execution Result
Consumer도 재조사하지 않는다. 새 Architecture를 설계하지 않는다. C6를
Accept하지 않는다. 구현하지 않는다.**

## 배경

- `ENGINE-CONNECT-0002`: 외부 caller → `call_engine()` → 실제 Engine
  → `results:list[str]` → `ExecutionResult` 흐름이 기술적으로
  작동함을 1회 실행으로 확인(worktree 전용, tracked 브랜치 미반영).
- `ENGINE-CONNECT-0003`: 그 흐름을 Production에 연결하려 했으나
  caller 위치가 없어 Blocked — `ADC-0010`이 6개 후보 전부 Not
  Accepted로 남긴 상태를 재확인.
- `ADC-0010`: C1(Kernel Engine Port/Adapter, 실체 없음) · C2(Runtime,
  ADC-02 Open) · C3(Session, 미정의 Concept) · C4(Development HQ,
  명시적 배제) · C5(Dogfooding 스크립트, 검증 전용) · C6(별도
  스크립트/함수, "예시 수준의 언급 외에 근거가 없다") — 전부 Not
  Accepted.

## Q1. 저장소에 C6와 동일하거나 유사한 Production 책임/구조가 이미 존재하는가?

**부분적으로 유사한 것이 하나 존재하지만, C6가 요구하는 모양과
일치하지 않는다.**

`projects/development-hq-devkit/runner.py`가 Kernel도 `development-hq/`
자신도 아닌 별도 위치(`projects/`)에 있는 스크립트다. `development-hq/mvp`
의 기존 공개 함수(`backend_agent_code_review` 등, 내부적으로
`call_engine()`을 호출)를 그대로 import해서 순서대로 호출한다 —
"별도 스크립트가 기존 공개 함수를 그대로 호출한다"는 구조 자체는
C6와 표면적으로 유사하다.

그러나 세 가지 지점에서 C6와 다르다:

1. **Execution Layer를 전혀 참조하지 않는다.** `grep -rl "execution_layer" projects/`
   결과 0건 — `build_execution_result()`나 `run_execution_layer_pipeline()`
   중 어느 것도 호출하지 않는다. C6가 풀어야 하는 문제(`results:list[str]`
   를 실제로 채우는 것)를 이 스크립트는 다루지 않는다.
2. **스스로 Engine Adapter 역할을 명시적으로 배제한다.** `projects/development-hq-devkit/README.md`
   "Out of Scope": *"...Engine Adapter, Model Routing — 모두 이번
   프로젝트 범위 밖이다."* — Development HQ의 Architecture Freeze
   원칙(`development-hq/CONSTITUTION.md`)을 `development-hq/` 바깥의
   이 위치에서도 그대로 따르고 있다.
3. **자기 정의가 "Dogfooding Testbed"다.** README 첫 줄: *"Development
   HQ를 검증하기 위한 첫 번째 Dogfooding 프로젝트(Testbed)다."* —
   `ADC-0010` C5(Dogfooding 스크립트)가 "검증 전용으로만 명시됨"이라는
   이유로 Not Accepted였던 것과 동일한 자기 한정이 여기도 그대로
   적용된다.

**결론**: "Kernel/HQ 밖의 별도 위치에 존재하는 스크립트"라는 패턴
자체는 저장소에 실존하지만, 그 실존 사례가 스스로 Engine Adapter
역할을 배제하고 검증 목적으로 자신을 한정한다는 점에서, C6가
필요로 하는 역할(Execution Layer ↔ Engine을 잇는 Production
Adapter)의 선례가 되지 못한다.

## Q2. 기존 Architecture/Baseline에서 별도 실행 함수/Service/Adapter를 허용하거나 암시하는 Evidence가 있는가?

**없다.**

- `BASELINE.md` §6 Concept Model은 10개 분류(Entity/Definition/
  Process/Event/Service/Interface/Metadata/Policy/State/Resource)
  아래 이름 붙은 Concept만 나열한다(`HQ, Agent, Principal` /
  `Workflow` / `Task` / `Event, Fault` / `Runtime, Memory, Registry`
  / `Engine Port, Adapter, Message` / `Capability, Artifact` /
  `Policy` / `Context, Lifecycle State` / `Resource`). "별도
  스크립트/함수"에 해당하는 항목은 없다 — Engine 호출과 관련된
  유일한 Interface Concept은 `Engine Port, Adapter`이며, 이는
  이미 C1(Kernel Engine Port/Adapter)로 분류되어 실체 없음으로
  Not Accepted된 것과 같은 것이다.
- `BASELINE.md` §7 System Boundary는 책임을 Jarvis OS(Kernel)와
  HQ 둘로만 나눈다. "Kernel도 HQ도 아닌 제3의 실행 위치"라는
  범주 자체가 Baseline에 없다.
- `BASELINE.md` §10 Out of Scope: *"Component Design (Scheduler,
  Engine Gateway, Registry, Communication, Memory, Policy 등)"*,
  *"Implementation"* — Engine Gateway 설계 자체가 Baseline 수준에서
  Out of Scope로 유지된다. 이는 C1을 막았던 것과 동일한 근거이며,
  C6가 "Kernel Engine Port/Adapter가 아닌 다른 이름의 Adapter"로
  해석될 경우 똑같이 이 Out of Scope에 걸린다.
- `development-hq/BOUNDARY.md`, `RFC-0005-development-hq-execution-boundary.md`
  어디에도 "Development HQ와 Execution Layer 사이의 독립 연결부"를
  허용하거나 암시하는 문장이 없다(이미 `RFC-0010` §2가 확인한 대로,
  C6의 유일한 근거는 `ADC-0005` Next Step의 예시 문구 한 줄뿐이다).

## Q3. C6를 기존 결정의 단순 재해석 없이 독립적인 후보로 볼 수 있는가?

**아니오.**

C6의 근거는 `RFC-0010`이 이미 확인한 대로 `ADC-0005-engine-connection-boundary.md`
Next Step의 예시 문구("caller(예: Development HQ ↔ Execution Layer를
잇는 별도 스크립트나 함수)의 구현 문제가 된다") 단 한 줄이며, 그
문서 자신이 "이 ADC는 그 선택을 하지 않는다"고 명시했다. 이번
조사에서 새로 찾은 유일한 관련 사례(`projects/development-hq-devkit/runner.py`,
§Q1)는 구조적으로 다르다(Execution Layer 미참조) 그리고 스스로
Engine Adapter 역할을 배제한다 — 이를 C6의 근거로 재해석하면, 그
사례 자신이 명시적으로 부인하는 역할을 그 사례에 덧씌우는 것이 된다.
즉 "재해석 없이" 독립적으로 성립하는 새 Evidence는 발견되지 않았다.

## Q4. C6를 후보로 만들려면 새로운 Architecture/Contract 결정이 필요한가?

**필요하다.**

C6를 실제로 판단 가능한 후보로 만들려면 최소한 다음이 먼저 결정되어야
하며, 각각이 그 자체로 Architecture 결정이다(이번 조사 권한 밖):

- **이름·정체성**: "별도 스크립트/함수"가 무엇을 가리키는지 —
  `BASELINE.md` §6 Concept Model에 없는 새 Concept을 도입하는
  일이다.
- **소속 네임스페이스**: Kernel도 `development-hq/`도 아니라면
  어디인가(`projects/`와 같은 기존 패턴을 따를지, 새 최상위
  디렉터리를 둘지) — `BASELINE.md` §7 System Boundary가 Jarvis
  OS/HQ 둘로만 나눈 책임 분류에 세 번째 범주를 추가하는 일이다.
- **Engine Adapter 배제 원칙과의 관계**: `development-hq/CONSTITUTION.md`
  Freeze 목록(Engine Adapter/Model Routing)과 `BASELINE.md` §10
  Out of Scope(Engine Gateway)가 이 새 위치에는 적용되지 않는
  이유를 밝혀야 한다 — 지금까지 확인된 유사 사례(`projects/development-hq-devkit`)
  는 오히려 그 원칙을 그대로 따랐다(§Q1).

이 세 가지 모두 "C6를 있는 그대로 재확인"하는 수준을 넘어 새
Architecture를 만드는 일이므로, 이번 조사의 권한(새 Architecture
설계 금지, C6 임의 Accept 금지) 밖이다.

## Q5. C6가 실제 caller 위치 문제를 해결할 수 있는 최소 범위가 무엇인가?

**결정하지 않는다 — 이 질문에 답하는 것 자체가 Q4의 Architecture
결정을 선행 조건 없이 내리는 것과 같다.** 다만 지금까지 확인된
Evidence가 일관되게 가리키는 제약 조건만 관찰로 기록한다(선택이
아니라 제약의 나열):

- 어떤 형태든 Kernel Component Architecture(§10 Out of Scope, C1과
  동일 근거)를 설계하는 형태가 되면 그 시점에 다시 Blocked다.
- 어떤 형태든 `development-hq/` 내부에 위치하면 Engine Adapter/Model
  Routing Freeze(C4와 동일 근거)에 걸린다.
- `projects/development-hq-devkit`처럼 "검증/Dogfooding" 목적으로
  자신을 한정하면 C5와 동일한 이유(production 근거 없음)로 Not
  Accepted 상태를 벗어나지 못한다.

이 세 제약을 모두 피하는 위치·형태가 존재하는지는 이번 조사의
Evidence만으로는 알 수 없다 — 이것이 바로 `ADC-0010` §부족한
Evidence 6번("C6이 후보 자체를 구체화하는 새 RFC가 필요하다")이
이미 지목한 공백이며, 이번 조사는 그 공백을 메우지 못했다.

## Stop Trigger / 조사 범위 대조

| 확인 항목 | 결과 |
|---|---|
| Production 코드 변경 | **없음** |
| C1~C5 재조사 | **없음** — 인용만 했다 |
| ADC-01·ADC-02 재조사 | **없음** |
| Execution Result Consumer 재조사 | **없음** |
| C6를 Accept로 판단 | **없음** — Q3·Q4에서 명시적으로 보류 |
| 새 Architecture/Concept 도입 | **없음** — Q4에서 무엇이 필요한지만 나열하고 만들지 않았다 |

## Conclusion

C6는 이번 조사에서도 독립적인 Evidence를 얻지 못했다. 저장소에서
발견한 유일한 관련 사례(`projects/development-hq-devkit/runner.py`)는
표면적 구조("Kernel/HQ 밖의 별도 스크립트")만 유사할 뿐, Execution
Layer를 다루지 않고 스스로 Engine Adapter 역할을 배제한다는 점에서
C6를 뒷받침하지 않는다. Baseline의 Concept Model·System Boundary
어디에도 "별도 스크립트/함수"라는 제3의 범주가 없다. C6를 판단
가능한 후보로 만들려면 이름·네임스페이스·Engine Adapter 배제 원칙과의
관계를 새로 결정해야 하며, 이는 새 Architecture 설계이므로 이번
조사 권한 밖이다.

**판단: C6는 여전히 Not Accepted 상태를 벗어나지 못한다. 새 RFC 없이는
더 이상 진행할 수 없다.** `ADC-0010` §부족한 Evidence 6번이 이미
요구한 대로, C6을 구체화하려면 그 자체를 대상으로 하는 새 RFC가
필요하다 — 이 문서는 그 RFC를 작성하지 않는다.
