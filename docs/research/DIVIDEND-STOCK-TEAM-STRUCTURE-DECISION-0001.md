# Dividend Stock Team Structure Decision 0001 — Promotion 재확인 및 "확장 vs 독립" 구조 권고

## 문서 성격

이 문서는 `docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0002.md`(JNJ/
KO/PG 3/3, "조건부 Go")가 **결정하지 않고 남긴 질문**— "Dividend Stock
Team을 Stock Team의 확장으로 둘지, 독립 Team으로 둘지" — 에 대해 기존
Evidence만으로 권고안을 제시한다. **이 문서는 Promotion을 확정하지
않는다.** Stock/ETF Team이 그랬듯, 최종 승인은 사용자 판단으로 남긴다.
`development-hq/`, `docs/03_adc/ADC.md`, 기존 TEAM-DEFINITION 문서 중
어느 것도 수정하지 않는다.

## 1. Promotion 재확인 (요약, 재조사 없음)

`DIVIDEND-STOCK-DOGFOODING-REVIEW-0002.md`가 이미 확정한 3/3 반복
Evidence를 그대로 인용한다 — 재조사하지 않는다.

| 기준(Stock/ETF와 동일) | 충족 |
|---|---|
| 3개 산업에서 파이프라인 완주(수동 개입 0회) | 3/3 |
| Dividend Quality/Valuation 고유 역할 반복 | 3/3 |
| Stock 5개 역할 재사용(지시문 변경 없음) | 3/3 |
| Bull/Bear/Synthesis "사실 충돌=데이터 문제, 해석 차이=Bull/Bear" 구조 | 7회 연속(Stock 1+ETF 3+Dividend Stock 3) |
| Kernel/Registry/Scheduler 불필요 | 3/3 |
| Stop Trigger 미발동 | 3/3 |

**Promotion 기준 자체는 이미 충족된 것으로 재확인한다.** 이번 문서의
목적은 그 다음 질문(구조)이다.

## 2. "확장" vs "독립" — 실제로 무엇이 다른 질문인가

두 후보는 자주 같은 것으로 오해되지만, 이 저장소의 Governance 원칙
아래에서는 서로 다른 층위의 질문이다.

- **"확장"**: Dividend Stock의 7개 역할 중 5개가 Stock Team의 역할과
  **동일한 Capability 코드(공유 Agent/모듈)를 실제로 import/재사용**
  한다는 구조적 주장.
- **"독립"**: Dividend Stock Team이 Stock Team과 **별도의 이름/
  디렉터리/문서 정체성**을 갖는다는 관례적 주장(코드 공유 여부와
  무관).

이 둘은 배타적이지 않다 — "코드는 독립(project-local 중복), 성격은
확장(역할 내용이 Stock과 겹침)"인 상태가 실제로 관찰된 것과 정확히
일치한다.

## 3. Evidence 대조

### 3-1. 코드 수준 — "확장"을 뒷받침하는 실제 공유는 없다

`docs/research/STOCK-AGENT-SEPARATION-REVIEW-0001.md` §3이 이미 이
질문을 Stock Team 내부에서 검증했다: Stock의 8개 업무 전부가 "동일
역할 반복(4/4)"·"독립 입출력 경계"·"전문 목적 구분" 3개 기준은
충족했지만, 4번째 기준인 **"독립 실행 또는 재사용 가치가 실제로
확인됨"은 8개 업무 어디에서도 충족되지 않았다** — "모든 재사용은
project-local 코드 복제를 통한 것이며, 하나의 Agent 인스턴스를 여러
Workflow/Team이 실제로 공유 호출한 사례는 없다."

이번 3회(JNJ/KO/PG)도 정확히 같은 패턴이다: `projects/
dividend-stock-analysis-{jnj,ko,pg}/agents.py`는 매번 Stock의 5개
함수를 **파일로 복사**해서 재사용했다(import를 통한 공유가 아니다).
`projects/stock-analysis-*`의 `agents.py`를 실제로 import하거나 공유
모듈을 만든 사례는 3회 모두 없다.

**결론**: "확장"을 코드/Architecture 수준의 주장으로 읽으면, 그 근거는
아직 없다 — Stock Team 자체가 이미 이 질문에 보수적으로 답한 전례
(§3, 8개 업무 전부 Agent 승격 보류)와 일치하는 결과다.

### 3-2. 관례 수준 — Division/Team은 애초에 코드 공유를 요구하지 않는다

`docs/01_architecture/BASELINE.md:50`·`development-hq/STRUCTURE.md:15`가
이미 확인한 대로, Division/Team은 "HQ 내부에서 선택적으로 쓸 수 있는
관례"이며 Jarvis OS Kernel은 그 존재 여부조차 알 필요가 없다. 즉 "Team"
단위 자체가 **코드 공유 단위가 아니라 이름/문서 정체성 단위**다. Stock
Team과 ETF Team도 서로 코드를 공유하지 않으면서(3/3 확인됨,
`ETF-DOGFOODING-REVIEW-0003.md` §5 유보 근거 1) 각각 독립적인 "Team"
정체성을 가졌다 — 이는 Team 단위의 독립/공유 여부가 Team 명명 자체와
무관함을 보여주는 기존 선례다.

**결론**: "독립 Team"이라는 명명이 "Stock과 코드를 공유하지 않는다"는
사실과 전혀 충돌하지 않는다 — ETF Team이 이미 그 전례다.

### 3-3. 내용 수준 — "확장" 성격은 실제로 강하게 관찰됐다

`DIVIDEND-STOCK-DOGFOODING-REVIEW-0002.md` §3이 이미 확인한 대로,
Stock의 5개 역할이 산업이 바뀌어도(헬스케어/음료/생활용품) 지시문
변경 없이 3/3 재사용됐다 — 이는 ETF(Stock 역할을 전혀 재사용하지
않음, 완전 독립)와 뚜렷이 대조된다. **역할 "내용"의 유사성은 코드
수준의 확장 여부와 별개로 실제로 강하다.**

## 4. 권고

**구조: "독립 Team"(이름/디렉터리/문서 정체성 수준)으로 명명하되,
문서에 "Stock Team 확장 성격"을 명시한다.**

근거:
1. 코드 수준의 실제 공유는 3/3 관찰되지 않았고, Stock Team 자체도
   이미 같은 검증(§3-1)에서 Agent 승격을 보류했다 — "확장"을
   Architecture적 공유 메커니즘으로 구현할 근거가 없다.
2. Division/Team은 코드 공유와 무관한 관례이므로(§3-2), "독립
   Team"이라는 명명이 Stock과의 역할 유사성(§3-3)을 부정하지 않는다.
3. `projects/stock-analysis-*`, `projects/etf-analysis-*`,
   `projects/dividend-stock-analysis-*`라는 기존 디렉터리 관례(이미
   3개 트랙 모두 독립 디렉터리)와 일치한다 — 새 구조를 발명하지
   않는다.
4. 향후 실제 코드 공유 필요가 관찰되면(예: Fundamental Analyst를
   Stock과 Dividend Stock이 실제로 같은 모듈에서 호출해야 하는 사례),
   그때가 `STOCK-AGENT-SEPARATION-REVIEW-0001` §6이 이미 명시한
   재검토 시점이다 — 지금 선제적으로 설계하지 않는다.

**이 권고는 순수 문서/명명 결정이며 코드·Architecture를 변경하지
않는다.** 최종 승인은 사용자 판단으로 남긴다.

## 5. Governance 필요 여부 판단

| 항목 | 필요한 절차 | 근거 |
|---|---|---|
| "Dividend Stock Team" 명명/디렉터리 관례 확정 | **불필요(RFC/ADC/ADR 없음)** — Stock/ETF Team과 동일 | `docs/01_architecture/BASELINE.md:50`, `development-hq/STRUCTURE.md:15`(Division/Team은 Architecture가 아님) |
| `docs/research/DIVIDEND-STOCK-TEAM-DEFINITION-0001.md` 작성(Stock/ETF의 TEAM-DEFINITION과 동일한 형식으로 승격 확정) | **단순 문서 작성** — 단, 사용자의 명시적 승인("승격을 확정하라"에 준하는 지시) 이후에만 작성 | `STOCK-TEAM-DEFINITION-0001.md`, `ETF-TEAM-DEFINITION-0001.md` 선례(둘 다 사용자의 명시적 확정 지시 이후 작성됨) |
| 향후 Agent 단위 실제 코드 공유(Stock ↔ Dividend Stock) | **RFC → ADC → ADR 필요** | `STOCK-AGENT-SEPARATION-REVIEW-0001.md` §6 — Kernel Registry/Agent 개념에 닿는 결정이므로 실제 공유 필요가 관찰된 뒤에만 착수 |
| Investment HQ Architecture 자체의 설계/인스턴스화 | **RFC → ADC → ADR 필요(아직 착수 안 함)** | `ETF-TEAM-DEFINITION-0001.md`, `STOCK-TEAM-DEFINITION-0001.md`가 반복적으로 명시한 범위 밖 |

**이번 문서는 어떤 절차도 실행하지 않는다.** 표는 "무엇이 필요한가"만
식별한다.

## 6. 아직 확정할 수 없는 것

- `DIVIDEND-STOCK-TEAM-DEFINITION-0001.md`(승격 확정 문서) 작성 여부 —
  사용자 판단.
- Agent 이름, Capability Contract, Development HQ Registry 등록 여부.
- 3개 Team(Stock/ETF/Dividend Stock)을 상위에서 묶는 "Investment HQ"
  자체의 존재/구조.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 기존
TEAM-DEFINITION 문서, `docs/03_adc/ADC.md`도 수정하지 않았다. 새 Agent,
새 Capability, 새 Kernel Component를 만들지 않았다. Stop Trigger
미발동.
