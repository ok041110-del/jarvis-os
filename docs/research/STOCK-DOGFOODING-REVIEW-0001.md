# Stock Dogfooding Review 0001 — Stock Team 승격 판단

## 문서 성격

이 문서는 AAPL/NVDA/MSFT 3회 Stock Dogfooding(`projects/stock-analysis-*`)의
EVIDENCE.md 3건과 PRD v1.2(원문 저장소 부재, 각 프로젝트 README/EVIDENCE에
인용된 章 기준)를 종합해 **Stock Team 승격 여부를 판단**하는 문서다.
`docs/research/EVIDENCE-REVIEW-0001`과 달리 이 문서는 판단을 내린다 —
사용자가 명시적으로 판단을 요청했고, MSFT EVIDENCE.md가 이미 같은 성격의
권고를 담고 있어 그 판단을 최종 정리·확정하는 것이 이 문서의 목적이다.

Architecture Decision이 아니다. 새 Agent 이름, 새 Capability, 새 Kernel
Component, 새 Runtime, 새 Contract를 만들지 않는다. Investment HQ
Architecture를 이 문서에서 확정하지 않는다.

## 범위

- `projects/stock-analysis-aapl/issues/0001-aapl-analysis/EVIDENCE.md`
- `projects/stock-analysis-nvda/issues/0001-nvda-analysis/EVIDENCE.md`
- `projects/stock-analysis-msft/issues/0001-msft-analysis/EVIDENCE.md`
- `projects/stock-analysis-{aapl,nvda,msft}/README.md`
- PRD v1.2 — **원문 파일이 저장소에 없음.** 3개 README와 EVIDENCE.md가
  인용한 章(2장/5장/8장/10장/11장) 서술로만 간접 참조 가능. 이 문서의
  "PRD 기준" 판단은 전부 이 간접 인용에 근거하며, PRD 원문 대조는
  불가능했다 — Unknowns에 기록.

---

# 1. 무엇을 확인했는가

3개 EVIDENCE.md는 동일한 형식(PRD v1.2 8장 관찰 항목 기준)으로, 각자 다른
산업(소비자 하드웨어/AI 반도체/기업용 소프트웨어+클라우드)의 실제 기업을
대상으로 9단계 파이프라인(5개 독립 분석 → Bull Case/Bear Case → Synthesis
→ Final Report, `call_engine()` 순차 호출)을 실제로 실행한 기록이다. MSFT
EVIDENCE.md는 추가로 3사 비교표와 "Stock Team 승격" 질문에 대한 1차 권고를
이미 포함하고 있다. 이 문서는 그 1차 권고를 재검증하고, TradingAgents
Reference 비교와 Governance(Division/Team 조항) 근거를 덧붙여 확정한다.

Division/Team이 실제로 Architecture급 결정인지도 확인했다:
`docs/01_architecture/BASELINE.md:50`("Division과 Team은 이 계층에
포함되지 않는다. Division과 Team은 HQ 내부에서 선택적으로 사용할 수 있는
구조이며, Jarvis OS는 그 존재 여부를 알지 못한다")와
`development-hq/STRUCTURE.md:15`("Division과 Team은 Development HQ 내부의
선택적 관례이며 ... Jarvis OS Kernel은 Division/Team의 존재 여부를 알지
못하며, 이 계층은 Registry에 등록되지 않는다")가 이를 확인해준다. 즉
"Stock Team" 여부 결정은 RFC → ADC → ADR 경로가 필요한 Architecture
변경이 아니다.

---

# 2. 반복적으로 확인된 구조

3회 모두에서 예외 없이 반복된 것만 적는다(1회성 관찰과 구분).

| 항목 | AAPL | NVDA | MSFT | 반복 여부 |
|---|---|---|---|---|
| 9단계 파이프라인 완주(수동 개입 없음) | 성공 | 성공 | 성공 | **3/3** |
| 새 Kernel/Registry/Scheduler 필요 | 없음 | 없음 | 없음 | **3/3** |
| Task 간 Context in-memory(문자열 결합)로 충분 | 예 | 예 | 예 | **3/3** |
| Bull/Bear 대립 검토의 실질적 유용성 | 확인 | 확인 | 확인(가장 뚜렷) | **3/3, 강화** |
| Synthesis의 "합의/충돌/해석차/미해결질문" 구조 자연 발생 | 예 | 예(더 명확) | — (표 미기재, 본문 확인) | **AAPL·NVDA 반복 확인, MSFT는 Bull/Bear 유용성 사례로 대체 서술** |
| 5개 역할의 관점 비중복성("자기 영역 밖 판단 불가" 명시) | 확인 | 확인 | 확인(+교차 통찰 사례 추가) | **3/3, 강화** |
| 회사 식별 문제(1차 발견) → 수정 재사용 | 최초 발견·수정 | 재발 안 함 | 재발 안 함 | **수정이 안정적으로 재사용됨** |
| 병렬 실행 필요성 | 미발생 | (표 미기재) | 미발생 | **AAPL·MSFT에서 명시적으로 불필요 확인, 3사 모두 순차 실행으로 완료** |
| Stop Trigger 발동 | 없음 | 없음 | 없음 | **3/3** |
| 출력 언어 | 전체 한국어 | 전체 영어 | 실행 내 혼재(파일 단위/문서 내부 단위) | **반복되지 않음 — 패턴 자체가 매번 다름** |

**Task/Role/Context/협업 구조 요약**:
- **Task**: 5개 독립 분석(데이터 의존성 없음) → 4단계 선형 체인(Bull/Bear/
  Synthesis/Report, 이전 출력에 전적으로 의존)이라는 9단계 구조가 산업이
  바뀌어도 변경 없이 재사용됐다.
- **Role**: 5개 역할(Fundamental/Technical/Industry-Competition/
  News-Event/Sentiment)이 서로 겹치지 않는 관점을 유지했고, "제공 데이터
  범위 밖은 판단하지 않는다"는 자기 제약이 3회 모두 반복됐다.
- **Context**: 별도 저장소·Memory Service 없이 in-memory 변수 결합만으로
  9단계 전체가 충분했다 — `IMPLEMENTATION_RULES.md`의 Memory Service
  구현 금지 원칙이 Investment 도메인에서도 그대로 유지됨을 3회 확인.
- **협업**: Bull/Bear 대립 → Synthesis 통합이라는 협업 패턴이 매 실행마다
  실제로 새로운 구조화된 정보(사실 충돌/해석 차이/미해결 질문 구분,
  MSFT에서는 "같은 사실의 이중적 해석"까지)를 만들어냈다.

---

# 3. TradingAgents Reference와의 비교

3개 프로젝트 README가 공통으로 명시한 편차는 3회 모두 동일하게 유지됐다
(재변경 없음):

| 항목 | TradingAgents Reference | 이번 3회 실행 |
|---|---|---|
| 분석 역할 구조(5개 전문 분석 → Bull/Bear → 종합) | 있음 | 그대로 채택 |
| Trader, Risk Management, Portfolio Manager의 승인/거부, 모의 거래소 실행 | 있음 | **제외** (PRD 2장이 명시적으로 범위 밖으로 규정) |
| State/Checkpoint(LangGraph, SQLite) | 있음 | **미사용** — in-memory 변수로 대체, 3회 모두 문제 없었음 |
| 실데이터 API(Alpha Vantage 등) 연동 | 있음 | **미사용** — 세션이 WebSearch로 수동 수집해 `raw_data.md`로 대체 |
| Agent 이름/세부 구조 | TradingAgents 고유 명명 | 그대로 복제하지 않음 — 이 저장소는 프로젝트별 project-local Capability 함수 패턴(`agents.py`) 재사용 |

**기존 구조(변경 없음)**: 5개 분석 역할 + Bull/Bear + Synthesis라는
TradingAgents의 핵심 분석 구조는 3회 모두 그대로 유지됐고, 이번 Dogfooding이
새로 발명한 것이 아니다.

**새롭게 확인된 구조(TradingAgents에는 없거나 이번에 처음 실제로 관찰된 것)**:
- 데이터 준비(회사/티커 식별 누락) 문제와 그 수정("_COMPANY_HEADER"
  프리픽스)이 실제 재사용 가능함을 확인한 것 — TradingAgents 자체의
  구조가 아니라 이번 project-local 구현에서 발견·해결된 결함.
- 출력 언어 비결정성 — TradingAgents Reference에는 없는 차원이며, 이번
  3회 실행에서 매번 다른 패턴(전체 한국어/전체 영어/실행 내 혼재)으로
  나타나 Capability Contract가 아직 다루지 않는 문제로 확인됨.

---

# 4. Stock Team 승격 판단

## 판단: **조건부 Go — "Stock Team" 후보 승격은 정당하나, 이 세션이 직접 확정하지 않는다.**

**근거(찬성)**:
1. 5개 분석 역할 + Bull/Bear + Synthesis + Report라는 9단계 구조가 3개의
   서로 다른 산업(소비자 하드웨어/AI 반도체/기업용 SW+클라우드)에서
   **구조 변경 없이** 3/3 성공했다 — 우연이 아니라 반복되는 패턴이라는
   근거로 충분하다.
2. Kernel/Registry/Scheduler 확장 없이 3회 모두 완주됐다 — Development
   HQ Platform 위에서 이 역할군이 재사용 가능하다는 근거이지, Kernel/
   Architecture 변경을 요구하는 근거가 아니다.
3. Division/Team은 Development HQ Baseline상 "선택적 내부 관례"이며
   Jarvis OS Kernel이 그 존재 여부를 알 필요가 없는 계층이다
   (`docs/01_architecture/BASELINE.md:50`, `development-hq/STRUCTURE.md:15`).
   따라서 "Stock Team" 명명 자체는 RFC 없이 결정 가능한 사안이다.

**근거(유보)**:
1. 3개 기업 모두 미국 대형 기술주다 — 산업 다양성이 제한적이다(금융/
   헬스케어/소비재/신흥시장 기업 등은 미검증).
2. PRD의 이번 단계 범위는 "Team/Role/Agent 후보로 승격을 검토"이지 "이
   세션이 그 구조를 코드/디렉터리로 확정한다"가 아니다(PRD 11장이
   Investment HQ Architecture 선행 설계를 명시적으로 금지).
3. 승격 자체가 RFC 없이 가능한 사안이라 해도, 그 결정을 이 Dogfooding
   세션이 임의로 내리는 것은 적절하지 않다 — 사용자에게 후보로 보고하고
   최종 결정은 사용자가 내리는 것이 Governance 원칙("Observe First,
   Decide Later")과 일치한다.

## 승격 시 최소 역할/업무 범위 (확정 아님, 후보로만 제시)

3회 모두 반복된 범위만 제시한다. Agent 이름, 세부 Architecture, Capability
Contract는 포함하지 않는다.

- **업무 범위**: 개별 기업 분석 요청에 대해 (1) 재무/펀더멘털,
  (2) 기술적 추세, (3) 산업/경쟁 구도, (4) 뉴스/이벤트,
  (5) 애널리스트 컨센서스/시장 심리 — 5개 관점의 독립 분석 → Bull/Bear
  대립 검토 → Synthesis(합의/충돌/해석차/미해결질문 구분) → 최종 보고서
  종합.
- **명시적 제외 범위**(PRD 2장 기준, 3회 모두 실제로 손대지 않음): 실거래
  실행, Risk Management/Portfolio Manager의 승인·거부, 자동매매, 실시간
  데이터 자동 수집(Connector/Runtime).
- **Context 요구사항**: 별도 저장소 불필요, in-memory 전달로 충분(3/3
  확인).

## 아직 확정할 수 없는 것

- Agent 이름, 세부 Architecture, Capability Contract(승격 여부와 무관하게
  이 문서·이 세션 범위 밖)
- 미국 대형 기술주 외 산업(금융/헬스케어/소비재/신흥시장 등)에서도 동일
  구조가 반복되는지 — 3회 모두 검증 안 됨
- **PRD v1.2 원문과의 정확한 대조** — 원문 파일이 저장소에 없어 이번
  판단은 README/EVIDENCE에 인용된 章 서술에 의존했다. 원문과 인용 사이에
  괴리가 있을 가능성은 배제할 수 없다.
- 최종 승격 여부·시점 자체 — 이 문서는 권고이며 결정이 아니다. 결정은
  PRD 10장이 명시한 확장 순서(Stock → ETF → Dividend Stock)와 사용자
  판단에 맡긴다.

## Capability 개선 후보 (Architecture 변경 아님, 기록만)

- **출력 언어 비결정성**: 3회 실행에서 3가지 다른 패턴(전체 한국어/전체
  영어/실행 내 혼재)이 나타났다. Capability Contract가 출력 언어를
  명시하지 않는다는 기존 사실(코드 리뷰 등 다른 Capability도 동일)이
  Investment 도메인에서 반복 확인된 것이며, 지금 지시문을 수정하지
  않는다 — 향후 Capability 지시문에 언어 고정 여부를 추가할지 검토할
  후보로만 기록한다.

---

# 5. 다음 작업

1. 사용자가 이 문서의 권고("조건부 Go")를 확정 결정으로 승인할지 판단
2. 승인 시, Stock Team이라는 이름/디렉터리 관례를 Development HQ Baseline
   의 선택적 관례 범위 안에서(RFC 없이) 어떻게 반영할지는 별도 후속 작업
   으로 정의 — 이 문서는 그 설계를 하지 않는다
3. 산업 다양성 확장이 필요하면(금융/헬스케어 등) 추가 Dogfooding 실행을
   후속 Task로 고려 — 이 문서가 그 실행을 스스로 트리거하지 않는다
4. PRD v1.2 원문이 저장소에 없는 상태가 반복되면(다음 단계에서도 원문
   대조가 필요해지면) 원문을 저장소에 반영할지 여부를 사용자에게 확인

---

# Architecture/Contract 변경 여부

**없음.** 이 문서 작성 과정에서 Architecture, Contract, Kernel, Runtime,
Production caller 변경이 필요한 지점은 발견되지 않았다. Stop Trigger
미발동.
