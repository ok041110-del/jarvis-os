# GOVERNANCE-REVIEW-0006: ADC-02 · ADC-09 · ADC-10 — Dogfooding/MVP 신규 Evidence 대조

**문서 성격**: Governance Review. **Decision 문서가 아니다.** 새 RFC/ADC/ADR을
작성하지 않는다. `docs/03_adc/ADC.md`의 ADC-02·ADC-09·ADC-10 상태를 이
문서가 직접 바꾸지 않는다(Governance 절차 없이 상태 변경 금지). 새
Architecture/Concept을 설계하지 않는다. **이번 검토에서 Production 코드는
한 줄도 작성하지 않았다.**

## 목적

"Development HQ Validation" 작업 지시에 따라, MVP-0038~0048·Stock Team·
ETF Team·Dividend Stock Team(JNJ·KO) Dogfooding에서 누적된 Evidence가
`docs/03_adc/ADC.md`의 NOW 우선순위 Open Decision 3건(ADC-02, ADC-09,
ADC-10)에 대해 Open 유지/Close/Update 중 무엇을 판단하게 하는지 대조한다.
기존 결정(`ADC-0008`, `GOVERNANCE-REVIEW-0001`)을 재조사하지 않고 그대로
인용하며, 이번에 새로 관찰된 Evidence만 추가로 대조한다.

**주의(namespace)**: 이 문서가 다루는 ADC-02/09/10은 `docs/03_adc/ADC.md`
(Jarvis OS Kernel 수준) 항목이다. `docs/architecture/core/ADC-0010-*.md`
(Engine Caller 위치)와 이름이 겹치는 별도 문서이며, 서로 다른 질문이다 —
혼동하지 않는다.

---

## ADC-02. Runtime 개념의 존폐

**기존 판단**: `ADC-0008-runtime-existence-boundary.md`(Not Accepted,
based on current evidence) — "유지" 후보는 원문이 스스로 미결정을
선언해 확정 근거 부족, "대체" 후보는 추론 과정이 저장소에 없어 근거
부족. 재검토 조건: (1) "Core Component 검토" 원문 확보, (2) Runtime
미결정으로 인한 반복 관찰 축적.

**이번에 대조한 신규 Evidence**: MVP-0038~0048(Development HQ 자체
Dogfooding 10건), Stock Team 4회(AAPL/NVDA/MSFT/JPM), ETF Team 3회
(QQQ/SCHD/AGG), Dividend Stock 2회(JNJ/KO).

| 재검토 조건 | 이번 Evidence로 충족되는가 |
|---|---|
| (1) "Core Component 검토" 원문 확보 | **아니오**. 이번 Dogfooding·MVP 어느 것도 그 원문을 찾거나 재구성하지 않았다 — 대상 범위 밖이다. |
| (2) Runtime 미결정으로 인한 반복 관찰 축적 | **아니오**. 9회의 project-local Dogfooding(Stock/ETF/Dividend Stock) 모두 `runner.py`의 하드코딩된 순차 함수 호출로 완주했고, Runtime 개념(Workflow를 참조해 Task를 Agent에 배분하는 별도 Service)의 필요성이 드러난 사례가 없다. MVP-0038~0048의 Stop Trigger 점검표(예: `MVP-0046-observation.md`)도 "Task 호출이 Workflow Parser/Scheduler로 일반화 — 미발동"을 반복 확인했을 뿐이다. |

**판단**: 재검토 조건 둘 다 미충족. **Open 유지가 타당하다.** 상태를
바꿀 근거가 이번 Validation에서 나오지 않았다.

---

## ADC-09. Workflow 그래프의 의미론적 경계

**충돌 내용**: OS가 이해해야 하는 Workflow 스키마가 순수 범용 그래프인지,
도메인 특화 노드 타입을 포함하는지. **참고 자료**로 Development HQ MVP의
Workflow 스키마(`{task_type, capability_required, inputs/outputs}`)가
이미 지정되어 있다.

**기존 판단**: `GOVERNANCE-REVIEW-0001` §4 — ADC-0001(Artifact Drift)이
"OS는 도메인 내용을 모른다" 원칙을 근거로 재사용했을 뿐, ADC-09 자체
상태는 바뀌지 않았다.

**이번에 대조한 신규 Evidence**: Stock/ETF/Dividend Stock Team의
`runner.py` 9건 전부가 "Task 1 → Task 2 → … → Task N" 하드코딩된
직접 함수 호출이며, 그 어떤 것도 범용 그래프나 도메인 특화 노드 타입을
런타임에 해석하는 스키마를 만들지 않았다. Stock(9단계)·ETF(10~11단계)·
Dividend Stock(11단계)이 서로 다른 단계 수를 갖지만, 이는 **코드
작성 시점에 사람이 정한 것**이지 OS가 실행 시점에 해석하는 그래프가
아니다. Development HQ MVP의 참고 스키마(`{task_type,
capability_required, inputs/outputs}`)에 새로운 필드나 도메인 특화
노드 타입이 추가된 사례도 없다.

**판단**: 이 9건은 ADC-09가 구분하려는 두 후보(순수 범용 그래프 vs
도메인 특화 노드) 중 **어느 쪽도 실제로 만들어지지 않은** 사례다 — 그래프
자체가 없으므로 "그래프의 의미론적 경계"를 판단할 대상이 아직 존재하지
않는다. `GOVERNANCE-REVIEW-0001`의 기존 결론(참고 자료로만 재사용, 상태
불변)과 같은 성격의 사실이 반복 확인됐을 뿐, ADC-09를 Close하거나 Update할
새 근거는 아니다. **Open 유지가 타당하다.**

---

## ADC-10. Policy 규칙의 출처 분리

**충돌 내용**: Policy Engine이 OS 전역 규칙만 평가하는지, HQ 도메인
규칙까지 평가 대상으로 삼는지.

**기존 판단**: 별도 core-level ADC 없음 — `docs/03_adc/ADC.md` 등재
이후 직접 다뤄진 기록이 없다(이번 검토로 처음 확인).

**이번에 대조한 신규 Evidence**: `development-hq/MVP.md`·
`IMPLEMENTATION_RULES.md`가 "Policy 판정(PDP/PEP 호출 자체)"을 MVP
Out of Scope로 명시했고, 9건의 Investment Dogfooding
(`projects/stock-analysis-*`, `projects/etf-analysis-*`,
`projects/dividend-stock-analysis-*`) 어디에도 Policy 평가 호출이 없다.
유일하게 Policy와 근접한 것은 각 Capability 함수의 하드코딩된 영어
지시문(예: "Do not give a buy/sell recommendation")인데, 이는 **OS
수준 Policy Engine이 아니라 프롬프트 텍스트에 박힌 도메인 규칙**이다 —
"OS 규칙 vs HQ 규칙 분리"라는 ADC-10의 질문 자체가 성립하려면 먼저
Policy Engine이라는 대상이 존재해야 하는데, 그 대상이 아직 없다.

**판단**: 새 Evidence는 ADC-10이 구분하려는 두 후보 중 어느 쪽도 아직
실체화되지 않았다는 사실만 반복 확인시켰다 — 이는 "결정 방향에 대한
근거"가 아니라 "결정할 대상이 아직 없다"는 사실이며, ADC-08(Runtime)에서
이미 확립된 것과 같은 종류의 결론이다. **Open 유지가 타당하다.**

---

## ADC 채택 기준 대조 — 지금 상태를 바꾸는 것이 정당화되는가

`docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준(HANDOVER.md
인용): (1) 지금 결정하지 않으면 상위 Architecture를 진행할 수 없다, (2)
결정이 늦어질수록 되돌리는 비용이 매우 커진다.

| 항목 | 기준 (1) | 기준 (2) |
|---|---|---|
| ADC-02 | 아니오 — Development HQ MVP는 Kernel 결정과 무관하게 계속 진행 중이며 실제로 진행됐다(MVP-0048까지) | 아니오 — Runtime을 구현한 코드가 전혀 없어 되돌릴 대상이 없다 |
| ADC-09 | 아니오 — 9건의 Dogfooding 모두 하드코딩 호출로 완주, 그래프 스키마 없이도 진행 가능함이 반복 증명됨 | 아니오 — 그래프를 구현한 코드가 없다 |
| ADC-10 | 아니오 — Policy Out of Scope로 명시된 채 9건 모두 문제없이 진행됨 | 아니오 — Policy Engine을 구현한 코드가 없다 |

**세 항목 모두 두 조건 미충족.** 지금 Governance 절차(RFC → ADC → ADR)를
새로 여는 것은 정당화되지 않는다.

---

## 결론

| ADC | 신규 Evidence로 판단 가능한 상태 변화 | 권고 |
|---|---|---|
| ADC-02 | 없음 | **Open 유지** |
| ADC-09 | 없음 | **Open 유지** |
| ADC-10 | 없음 | **Open 유지** |

`docs/03_adc/ADC.md`는 이 문서로 수정하지 않는다. 세 항목 모두 상태·
우선순위(Open · NOW) 그대로 유지된다. 이 판단을 뒤집으려면 새 RFC가 새
Evidence(위 표의 미충족 항목 중 하나가 실제로 채워지는 사건)를 근거로
열려야 한다 — 이번 Validation은 그런 사건을 만들지 않았다.

---

## 관련 발견 — AGG Data Boundary 재현 검토

이번 Validation 과정에서 `docs/research/AGG-DATA-BOUNDARY-REPRODUCTION-0001.md`가
별도로 다루는 발견(ETF-DOGFOODING-REVIEW-0003/EVIDENCE.md의 "Engine
데이터 범위 이탈" 관찰이 실제로는 Data Acquisition 단계의 문제였을
가능성)이 나왔다. 이 발견은 ADC-02/09/10 어디와도 직접 연결되지 않는다
— Runtime/Workflow 그래프/Policy 어느 것도 아니라 project-local raw
data 작성 관행의 문제이기 때문이다. 별도 문서로 분리해 두었다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `ADC-0008`, `GOVERNANCE-REVIEW-0001`,
  `docs/03_adc/ADC.md`, `development-hq/MVP.md`,
  `development-hq/IMPLEMENTATION_RULES.md`, `docs/01_mvp/MVP-0038~0048`,
  `projects/stock-analysis-*`·`etf-analysis-*`·`dividend-stock-analysis-*`의
  실제 `runner.py`/observation 파일만 인용했다.
- `docs/03_adc/ADC.md`를 수정했는가 — **아니오**.
- ADC-02/09/10을 임의로 Accept/Close했는가 — **아니오**. 세 항목 모두
  Open 유지를 권고했을 뿐이다.
- 새 RFC/ADC/ADR을 작성했는가 — **아니오**.
- Runtime/Workflow Parser/Policy Engine을 설계하거나 구현했는가 —
  **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**(AGG 관련 발견은
  별도 문서로 분리, Architecture Decision이 아니라 project-local 데이터
  작성 관행 문제).
