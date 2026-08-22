# INVESTMENT-HQ-V2.0-ARCHITECTURE-FREEZE-REVIEW-0001

**문서 성격**: Architecture Freeze Review(Governance 판단 문서). **RFC/ADC/ADR이
아니다.** `PHASE7-EXTERNAL-OBSERVATION-TRADINGAGENTS-0001.md`,
`INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001.md`와 동일한 지위 —
`docs/research/`에 두는 이유도 같다(공식 Architecture 확정이 아니라
확정 가능 여부에 대한 판단). 이 문서는:

- `docs/architecture/baseline/BASELINE.md`, `STRUCTURE-V1.0-FROZEN.md`,
  `INVESTMENT-HQ-V1.0-FREEZE-0001.md`를 수정하지 않는다.
- 새 RFC/ADC/ADR을 생성하지 않는다.
- `hqs/investment/`, `core/` 코드를 한 줄도 수정하지 않는다.
- TradingAgents 코드를 복사·수정하지 않는다.
- Freeze Decision 이전에 어떠한 구현도 하지 않는다(사용자 지시,
  §19 준수).

**결론 선반영**: **C. NOT READY.** 근거와 선행조건은 §16·§18에
기록한다.

---

## 0. 조사 방법과 대상

| 대상 | 방법 |
|---|---|
| Investment HQ 현재 구현 | `hqs/investment/{STRUCTURE.md, README.md, run.py, engine_client.py, checkpoint.py, teams/*.py}` 직접 읽기 |
| Jarvis OS Governance/Baseline | `docs/architecture/baseline/{BASELINE.md, STRUCTURE-V1.0-FROZEN.md}`, `docs/architecture/core/{INVESTMENT-HQ-V1.0-FREEZE-0001.md, COMPONENT-CANDIDATE-0001-...md}`, `roadmap.md`, `hqs/development/IMPLEMENTATION_RULES.md` |
| 기존 Investment HQ Governance 축적 | `docs/research/{STOCK,ETF,DIVIDEND-STOCK}-TEAM-DEFINITION-0001.md`, `INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001.md`, `INVESTMENT-HQ-MINIMAL-STRUCTURE-REVIEW-0001.md` |
| TradingAgents Reference | `https://github.com/TauricResearch/TradingAgents` 실제 clone(commit `a33fd4c0`, 이미 `PHASE7-EXTERNAL-OBSERVATION-TRADINGAGENTS-0001.md`가 검증한 커밋과 **동일** — drift 없음, 이번 세션에서 `git log -1`로 재확인) — `tradingagents/agents/{analysts,researchers,managers,risk_mgmt,trader,schemas.py}`, `tradingagents/graph/setup.py`, `tradingagents/agents/utils/agent_states.py` 직접 읽기로 재검증 |

기존 `PHASE7-EXTERNAL-OBSERVATION-TRADINGAGENTS-0001.md`는 commit
`a33fd4c0` 기준 FACT를 이미 충분히 확보했고, 이번 검토에서 동일 commit을
재확인해 drift가 없음을 확인했다 — 그 문서의 §4(비교표)·§6(FACT)를
그대로 재사용하고, 이번 문서는 **v2.0이 새로 요구하는 개념(Trader,
Risk, Portfolio, TradingDecision Contract)**에 한정해 TradingAgents의
`schemas.py`/`trader.py`/`portfolio_manager.py`/`graph/setup.py`를
새로 직접 확인했다(§4).

---

## 1. Investment HQ 현재 Architecture Audit

**Frozen 상태**: `hqs/investment/`는 이미 `INVESTMENT-HQ-V1.0-FREEZE-0001.md`로
Stable v1.0 Freeze됐다(roadmap Phase 3, 완료). 현재 구현의 실제 범위:

```
hqs/investment/
├── run.py            # TEAMS = {stock, etf, dividend_stock} 리터럴 딕셔너리, argv 4개
├── engine_client.py  # call_engine() re-export (13줄, hqs/development/mvp/engine.py 그대로 import)
├── checkpoint.py      # Checkpointer — 단계 이름→파일 매핑, ContentFailureError 감지
└── teams/
    ├── stock_team.py            (232줄, 5 analysis + Bull/Bear + Synthesis + Report = 9 Engine call)
    ├── etf_team.py               (276줄, 6 analysis + ... = 10 Engine call)
    └── dividend_stock_team.py    (268줄, 7 analysis + ... = 11 Engine call)
```

**결정적 FACT**: 세 Team의 실제 코드를 직접 읽은 결과, **파이프라인이
`final_report.md`에서 끝난다.** 그리고 각 단계 instruction이 명시적으로
거래 판단을 금지한다 — `stock_team.py`에서 확인한 문구:

- Fundamental/Technical/Industry/News/Sentiment 각 Analyst: `"Do not give
  a buy/sell recommendation."` (5회 반복)
- Bull/Bear Researcher: 사실 근거만 요구, 판단 금지 문구는 없지만 각자
  "case"(주장)를 구성할 뿐 결정을 내리지 않음
- Synthesis: `"This is not a trade order and must not include a
  buy/sell/hold instruction."`
- Report Writer: `"an explicit disclaimer that this is an analysis
  exercise, not investment advice or a trade recommendation."`

즉 **현재 Investment HQ는 BUY/SELL/HOLD, Trader, TradingDecision,
Risk, Portfolio, Execution 중 어느 것도 코드·지시문·산출물 어디에도
존재하지 않는다.** 18건의 project-local Dogfooding + HQ-level 실행
6건(`aapl-hq-verify`, `pg-hq-verify`, `efa-2026-08` 각 2회) 전부가
"리서치 리포트 생성"까지만 검증했다 — 이번에 검토 대상인 v2.0의
Trader 이후 전체 Workflow(§0의 "목표 Workflow" 6단계 중 뒤 4단계)는
**어떤 형태의 실행 Evidence도 존재하지 않는 완전한 백지 상태**다.

**Team 간 공유**: `INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001.md`가 이미
명시: "코드 공유 방식: project-local 복제(코드 공유 없음)". 실제로
`stock_team.py`와 `dividend_stock_team.py`를 대조하면 5개 역할
instruction 문자열이 완전히 동일하게 복제돼 있다(Dividend Stock이
Stock의 5/5 역할을 그대로 재사용하고 2개 역할을 추가) — 이는 "나중에
공통일 것 같아서"가 아니라 **실제로 이미 100% 동일한 문자열이 세
파일에 복제돼 있다는 관찰된 FACT**이며, 그럼에도 v1.0 Freeze 시점에
Common Layer로 추출하지 않기로 판단했다(§5에서 재검토).

**IMPLEMENTATION_RULES 준수 현황**: `hqs/investment/STRUCTURE.md`가
`hqs/development/IMPLEMENTATION_RULES.md`와 동일 원칙을 명시 —
Workflow Parser/Scheduler/Registry 일반화/Runtime/Engine
Gateway·Routing/Policy/Memory Service/Event Bus **전부 구현 금지**가
현재도 유효하다. `run.py`의 `TEAMS` 딕셔너리, `checkpoint.py`의
`Checkpointer`는 이 금지를 어기지 않는 최소 구현으로 유지되고 있다
(직접 코드 확인).

---

## 2. TradingAgents Repository Audit

Clone: `https://github.com/TauricResearch/TradingAgents`, commit
`a33fd4c0f134485a43553a2c23a63cb14adbd88f`(2026-07-18) — **Phase 7
Observation 문서가 검증한 것과 동일 commit**, drift 없음.

### 2-1. 구조(직접 확인)

```
tradingagents/agents/
├── analysts/     (fundamentals, market, news, sentiment, social_media — 5개)
├── researchers/  (bull_researcher.py, bear_researcher.py)
├── managers/     (research_manager.py, portfolio_manager.py)
├── risk_mgmt/    (aggressive_debator.py, conservative_debator.py, neutral_debator.py)
├── trader/       (trader.py)
├── schemas.py    (Pydantic 구조화 출력 스키마)
└── utils/
tradingagents/graph/
├── setup.py            (StateGraph 정의 — 노드/엣지)
├── conditional_logic.py
├── propagation.py
├── checkpointer.py      (LangGraph SqliteSaver)
├── trading_graph.py
└── reflection.py
tradingagents/llm_clients/  (Provider별 client — Multi-provider)
```

### 2-2. Graph 실제 흐름(`graph/setup.py` 직접 확인, README 아님)

```python
workflow.add_edge(START, plan.specs[0].agent_node)
# Analyst 체인(analyst → tool → clear → 다음 analyst, 순차, tool 호출 있는 analyst만 conditional routing)
workflow.add_edge(current_clear, "Bull Researcher")
# Bull/Bear ↔ Research Manager (conditional edge, 토론 라운드 수만큼 반복)
workflow.add_edge("Research Manager", "Trader")
workflow.add_edge("Trader", "Aggressive Analyst")
# Aggressive → Neutral → Conservative (risk debate, conditional edge, 라운드 반복)
workflow.add_edge("Portfolio Manager", END)
```

**FACT**: Analyst 체인은 **순차 실행**(하나씩), Bull/Bear와 Risk
Debator 3인은 **토론(다회 왕복)**, `ThreadPoolExecutor`/`asyncio`/
LangGraph `Send()` fan-out은 코드 전체에 **없음**(grep 확인, Phase7
문서와 동일 결론 재확인). Investment HQ의 "Wave 내 병렬"과 정반대
설계다 — TradingAgents는 병렬화보다 **다회 왕복 토론(debate rounds)**
으로 신뢰도를 높이는 방식을 택했다.

**결정적으로**, 이 그래프는 **종목 하나(single ticker)를 입력받아
`final_trade_decision` 하나를 반환하는 단일 실행**이다(`main.py`의
`ta.propagate(ticker, date)`). **여러 종목/여러 자산군의 결과를 합쳐
포트폴리오 전체를 조정하는 로직은 이 Repository 어디에도 없다** —
`portfolio_manager.py`는 "이 종목에 대한 최종 판단"을 내릴 뿐,
Investment HQ가 원하는 "Stock BUY + Dividend BUY + ETF BUY를 보고 일부를
HOLD로 조정"하는 **Cross-Asset Portfolio 조정 책임과는 다른 개념**이다
(§7 Portfolio 참조).

### 2-3. Trading Decision 관련 구조화 출력(`schemas.py` 직접 확인)

| 클래스 | 담당 Agent | 필드 |
|---|---|---|
| `ResearchPlan` | Research Manager | `recommendation`(5단계: Buy/Overweight/Hold/Underweight/Sell), `rationale`, `strategic_actions`(sizing 가이드 포함) |
| `TraderProposal` | Trader | `action`(3단계: Buy/Hold/Sell), `reasoning`, `entry_price`(optional), `stop_loss`(optional), `position_sizing`(optional 문자열) |
| `PortfolioDecision` | Portfolio Manager | `rating`(5단계, Research Manager와 동일 scale), `executive_summary`, `investment_thesis`, `price_target`(optional), `time_horizon`(optional) |

**FACT**: `TraderProposal`에는 **`confidence`, `expected_direction`
필드가 없다.** 대신 `entry_price`/`stop_loss`/`position_sizing`(모두
optional)이 있다 — TradingAgents의 Trader는 **3단계 방향(action)** +
**근거(reasoning)** + **선택적 실행 파라미터(가격/손절/사이징)** 를
담당하고, `confidence`는 어느 Trading Decision 스키마에도 없다(단,
`SentimentReport`에는 `confidence: Literal["low","medium","high"]`가
있다 — Analyst 레벨 데이터 품질 신뢰도이지 Trading Decision 신뢰도가
아니다). `time_horizon`은 **Trader가 아니라 Portfolio Manager
레벨**(optional)에서만 등장한다.

### 2-4. Memory / Checkpoint(Phase7 문서 재확인, drift 없음)

- Checkpoint: `graph/checkpointer.py` — LangGraph `SqliteSaver`,
  종목당 `checkpoints/{TICKER}.db`, 그래프 스텝 단위, 기본
  `checkpoint_enabled=False`.
- Memory: `agents/utils/memory.py` — 과거 결정과 결과("lessons from
  prior decisions")를 다음 프롬프트에 주입(`portfolio_manager.py`의
  `past_context`/`lessons_line`에서 실사용 확인). Investment HQ에는
  이 개념(과거 실행 결과를 다음 실행에 주입)이 **전혀 없다** — 매
  실행이 완전히 독립적이다.

### 2-5. UI/CLI

`cli/`, `main.py` 확인 — CLI 진입점과 콘솔 출력(rich 기반 progress
표시)만 있고, 별도 Web Dashboard 코드는 없다. `AssetType` enum은
`STOCK`/`CRYPTO` 두 값뿐(Phase7 문서 §6 FACT 재확인) — ETF/배당주
전용 처리 경로가 없다.

---

## 3. TradingAgents → Investment HQ Mapping

| TradingAgents 개념 | Investment HQ 대응 | 그대로 채택 가능한가 |
|---|---|---|
| Analyst(4, asset_type 필터) | Analyst(Stock 5 / ETF 6 / Dividend 7, Team별 고정) | **아니오** — Investment HQ는 자산군별로 이미 검증된 다른 역할 수를 쓴다(§1). TradingAgents의 "필터링된 4개"보다 Investment HQ의 자산군별 전용 Analyst가 더 세분화돼 있고 18회 Dogfooding으로 이미 검증됨. TradingAgents로 대체할 이유 없음 |
| Bull/Bear Researcher | Bull/Bear(Team마다 동일 패턴) | 이미 동등 구조 존재, 참고할 것 없음 |
| Research Manager(`ResearchPlan`) | **없음** | Investment HQ는 Synthesis에서 멈추고 방향(recommendation)을 명시적으로 금지한다(§1) — Research Manager 개념 자체가 아직 없음 |
| Trader(`TraderProposal`) | **없음** | v2.0이 신규로 원하는 개념. §2-3의 필드 구성(action 3단계 + reasoning + optional 실행 파라미터, confidence 없음)은 **참고 가능한 근거**이나 그대로 채택할 근거(Evidence)는 Investment HQ 쪽에 없음 |
| Risk Debator 3인(Aggressive/Neutral/Conservative) | **없음** | TradingAgents는 Risk를 "단일 종목에 대한 3관점 토론"으로 구현 — Investment HQ가 원하는 "HQ-level/Portfolio-level Risk"(여러 Team의 포지션을 종합하는 리스크)와는 **범위가 다르다**. 그대로 복제하면 안 됨(§7) |
| Portfolio Manager(`PortfolioDecision`) | **없음** | **이름은 같지만 책임이 다르다** — TradingAgents의 Portfolio Manager는 "이 한 종목의 최종 판단"이고, Investment HQ가 원하는 Portfolio Manager는 "여러 Team의 여러 종목 결정을 조정"이다(§2-2). 이름만 보고 대응시키면 오판(§7에서 상세) |
| `StateGraph`/LangGraph | **없음**(Wave 하드코딩) | §10에서 판단 — 지금 필요 근거 부족 |
| `AgentState`/`InvestDebateState`/`RiskDebateState` | **없음**(dict/지역 변수) | §9에서 판단 |
| `SqliteSaver` Checkpoint(그래프 스텝 단위) | `Checkpointer`(파일, named-step 단위) | 이미 동등 기능 보유, 대체 불필요(§11) |
| `agents/utils/memory.py`(과거 결정 lessons) | **없음** | Investment HQ 전체에 없는 개념 — 새 Need인지부터 판단 필요(§11), 이번 v2.0 범위에서 사용자가 명시적으로 요구하지 않음 |
| `llm_clients/`(Multi-provider) | `call_engine()`(Claude Code 단일) | Phase7 문서 결론 유지 — 필요 시 얇은 wrapper로 충분, Investment HQ가 재구현할 이유 없음 |

**핵심 원칙 재확인**: "TradingAgents에 존재한다 ≠ Investment HQ에도
필요하다"를 적용한 결과, **채택 후보로 남는 것은 Trader의 필드 구성
아이디어(action/reasoning/optional 실행 파라미터) 하나뿐**이다. 나머지
(Research Manager, Risk Debator 3인 토론, LangGraph, Memory)는 Investment
HQ의 실제 Need가 아직 관찰되지 않았거나(§17 분류 C), 책임 범위 자체가
다르다(Portfolio Manager).

---

## 4. Agent Taxonomy 검증

사용자가 제시한 후보(Analysts/Researchers/Research Manager 또는
Synthesis/Trader/Reporting)를 실제 구현과 대조한다.

| 계층 | Investment HQ 현재 실증(18회) | TradingAgents 실제 구현 | 판단 |
|---|---|---|---|
| Analysts | Stock 5 / ETF 6 / Dividend 7, 자산군별 role 이름·수가 다름 | 4개, asset_type로 필터(단 ETF/Dividend 전용 asset_type 없음, §2-5) | Investment HQ 쪽이 더 세분화·검증됨. 유지 |
| Researchers(Bull/Bear) | 존재, 공통 패턴 | 존재 | 일치, 변경 불필요 |
| Research Manager/Synthesis | **"Synthesis"만 존재, 방향 결정 금지** | Research Manager가 5단계 `recommendation` 결정 | **불일치** — 사용자 후보의 "Research Manager / Synthesis"를 동의어처럼 묶었으나 실제로는 서로 다른 책임이다. 현재 Synthesis는 "Bull/Bear가 어디서 갈리는지 설명"만 하고 방향을 정하지 않는다. TradingAgents의 Research Manager는 방향까지 정한다. **v2.0에서 이 둘을 합칠지, Synthesis 뒤에 별도 Research Manager를 추가할지는 아직 결정된 바 없다** — Evidence 없이 taxonomy를 확정하면 안 된다(§17 C) |
| Trader | **없음** | 존재(`TraderProposal`) | §3 참조. 신규 개념, Evidence 없음 |
| Reporting | 존재(Report Writer, "not investment advice" 명시) | `reporting.py`(구조화 리포트 트리) | Investment HQ 쪽 리포트가 "투자 조언 아님"을 명시하는 것 자체가 **현재 Architecture의 의도적 경계**임을 보여준다 — 이 경계를 v2.0에서 없앨지는 Freeze Decision의 핵심 쟁점(§16) |

**결론**: 사용자가 제시한 taxonomy 초안은 "Research Manager /
Synthesis"를 사실상 동일시했지만, 실제로는 **"방향을 정하지 않는
Synthesis"에서 "방향을 정하는 무언가"로의 전환이 필요하며, 이 전환
자체가 아직 한 번도 실행된 적 없는 새 책임**이다. Trader 이전에 이미
한 단계(방향 결정)가 비어 있다는 사실이 이번 Audit에서 새로 드러났다.

---

## 5. Team / Common Boundary

§1에서 확인한 대로 5개 Analyst instruction이 Stock/Dividend Stock
간 **문자 그대로 100% 동일**하게 복제돼 있다(FACT, 추측 아님). 그럼에도:

- **공통성이 확인된 부분**: 4-Wave 실행 패턴(N개 분석 병렬 → Bull/Bear
  병렬 → Synthesis → Report), Checkpoint 사용 방식, `call_engine()`
  호출 방식, Stock↔Dividend Stock의 5개 analyst instruction 문자열.
- **Domain-specific 부분**: 분석 role의 **개수**(5/6/7)와 ETF/Dividend
  전용 역할(예: Dividend Quality, Composition/Index)의 instruction
  내용.

**Commonization을 지금 Freeze할 만큼 Evidence가 충분한가 — 아니오,
그리고 이번에 다시 확인했다.** 이유:

1. `INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001.md`가 v1.0 Freeze
   시점에 "코드 공유 방식: project-local 복제(코드 공유 없음)"를 3개
   Team 모두에 대해 이미 명시적으로 확정했다 — 이는 실수로 안 만든
   것이 아니라 **의도적 판단**이었다.
2. `IMPLEMENTATION_RULES.md`의 "Registry 일반화 금지"·"정적 딕셔너리를
   조회 함수/클래스/동적 등록 API로 일반화하지 않는다"는 금지가
   Investment HQ에도 동일 적용된다(`STRUCTURE.md` §금지 사항) — 5개
   instruction을 `agents/prompts/common.py` 같은 공유 모듈로 뽑는
   순간, 그 모듈은 정확히 이 금지가 막으려는 "일반화된 조회 계층"이
   될 위험이 크다.
3. v1.0 Freeze 이후 새로운 반복(Regression 확인이 필요한 수정, 예:
   Stock instruction 변경 후 Dividend Stock도 자동 반영돼야 했던
   사례)이 **한 건도 관찰되지 않았다** — "동일한 문자열이 세 곳에
   있다"는 사실 자체는 Commonization의 **가능성**이지 **필요성**의
   증거가 아니다. 실제로 유지보수 비용이 발생했다는 Evidence(예:
   한쪽만 고치고 다른 쪽을 놓친 버그)가 없다.

**판정**: `agents/`, `workflow/`, `prompts/` 구조를 세 Team에 강제
복제하지 않는다는 원칙(사용자 지시)에 동의하며, 실제 Evidence는 오히려
"지금은 Common Layer를 만들지 않는 것"을 지지한다. **Team 구조 자체는
Freeze 가능**(이미 v1.0에서 사실상 Frozen) — 단, "언제 Common Layer를
재검토할 것인가"의 조건은 v1.0 Closure 문서가 이미 기록한 것과 동일하게
유지한다: **실제 유지보수 비용(양쪽에 반영 누락 등)이 관찰될 때**.

---

## 6. Workflow / LangGraph

Investment HQ 현재 Workflow(Wave 하드코딩, `run()` 함수 내부 4단계
호출)는 v2.0이 원하는 "HQ-level Graph"(여러 Team의 Trading Decision을
Risk→Portfolio→Execution으로 잇는 흐름)를 **표현할 수단이 전혀 없다** —
`run.py`는 Team 하나를 실행하고 끝나는 단발성 스크립트이며, 여러 Team의
결과를 한 프로세스에서 모아 다음 단계로 넘기는 코드가 없다(FACT,
`run.py` 52줄 전체 확인).

**LangGraph가 실제로 필요한가**에 대한 판단(§10 질문 적용):

| 질문 | 판단 |
|---|---|
| Team별 Graph가 필요한가 | **아니오, 아직.** 현재 4-Wave 하드코딩이 3개 Team 18회 반복에서 한 번도 문제를 일으키지 않았다(Closure 문서). Conditional routing이나 반복 토론이 필요하다는 Evidence가 없다 |
| HQ-level Graph가 필요한가 | **판단 불가 — Need 자체가 아직 없다.** HQ-level로 여러 Team의 결과를 조합하는 실행이 **한 번도 일어난 적이 없다**(§1) — 무엇을 그래프로 표현해야 하는지조차 아직 모른다 |
| Subgraph 구조가 적합한가 | 판단 불가(위와 동일 이유) |
| Conditional Routing이 실제로 필요한가 | **아니오.** TradingAgents의 conditional edge는 "tool 호출 여부"와 "토론 라운드 반복"에 쓰인다 — Investment HQ는 tool 호출도, 라운드제 토론도 쓰지 않는다(단발 프롬프트, §1) |
| 현재 요구사항에 비해 과도한 구조인가 | **그렇다.** LangGraph 도입은 `StateGraph`/`AgentState`/조건부 엣지라는 **일반화된 실행 엔진**을 들여오는 것과 같고, 이는 `IMPLEMENTATION_RULES.md`의 "Workflow Parser 구현 금지"·"Scheduler 구현 금지"가 막으려는 것과 기능적으로 동일하다. LangGraph를 쓰는 순간 "Task 1→Task 2가 조건문·설정 파일·파서로 대체되려는 순간" 트리거(§구현 중단 트리거)를 사실상 충족한다 |

**판정**: LangGraph 도입은 지금 시점에 **명시적 Governance 금지
조항과 충돌**한다. "LangGraph 때문에 Architecture 변경"(§19 금지
목록)이 실제로 일어날 위험이 있다 — 순서가 거꾸로다: Architecture가
먼저 결정되고 LangGraph는 그 구현 도구로만 검토돼야 하는데, 지금은
LangGraph의 기능(conditional edge, subgraph)이 Architecture 논의를
이끌고 있다. **v2.0 Workflow/LangGraph 축은 Freeze 불가.**

---

## 7. State

현재 Investment HQ에 **State 모델이 없다**(FACT, §1의 TradingAgents
비교표 E행). `wave1_results` 같은 Python 지역 dict가 있을 뿐이고,
프로세스가 끝나면 사라진다(Checkpoint는 산출물 파일만 남긴다, State
객체를 직렬화하지 않는다).

v2.0이 요구하는 두 State:

- **Team/Investment State**: 현재 지역 변수 수준으로 이미 존재(다만
  "State"라고 부를 만한 명시적 모델은 아니다) — Team 실행 범위 안에서는
  당장 문제가 없다(18회 무사고).
- **Portfolio State**: **완전히 새로운 개념, 어떤 형태의 Evidence도
  없다.** "Investment HQ 전체 Portfolio 상태"를 저장·조회한 적이
  한 번도 없다 — 심지어 "Portfolio"라는 개념 자체가 지금 코드에
  등장하지 않는다(현재 실행은 종목 1개, Team 1개 단위로 완결된다).

**Kernel Governance와의 직접 충돌**: `COMPONENT-CANDIDATE-0001.md`의
C-7(Event/State) 판정을 직접 확인했다 — **"가장 이른 단계. Multi-HQ
시나리오가 아직 한 번도 [관찰되지 않음]"**. Portfolio State는 정확히
"여러 Team(사실상 Investment HQ 내부의 Multi-Team, Kernel 관점에서는
Multi-HQ와 유사한 다중 소스 상태 집계 문제)"에 해당하는 시나리오이며,
Kernel 쪽 판정과 Investment HQ 쪽 관찰(전무)이 정확히 일치한다.

**판정**: Team State는 지금 형태(지역 변수)로 계속 써도 문제없다 —
Freeze할 필요조차 없다(이미 동작 중). **Portfolio State는 Freeze
불가** — 정의할 데이터조차 없다.

---

## 8. Memory / Knowledge / Checkpoint

| 책임 | Investment HQ 현재 | 필요성 판단 |
|---|---|---|
| State(실행 상태) | 지역 변수(§7) | 기존 그대로 |
| Checkpoint(재개) | `checkpoint.py` — 파일 기반, named-step 단위, `ContentFailureError` 감지. v1.0 Freeze Evidence(§Freeze 문서 참조)로 이미 검증 완료 | **중복 없음** — LangGraph `SqliteSaver`와 책임이 겹치지만, Investment HQ는 LangGraph를 쓰지 않으므로(§6) 실제 중복이 아니다. TradingAgents를 도입하지 않는 한 통합 대상 자체가 없다 |
| Memory(과거 실행 재사용) | **없음** | Evidence 없음. 사용자 v2.0 목표(§1의 6단계 Workflow)에도 명시적으로 요구되지 않았다 — "좋아 보인다"는 이유로 추가하지 않는다는 원칙(§11) 그대로 적용, **이번에 도입하지 않는다** |
| Knowledge(축적 투자 지식) | **없음** | 동일 |
| Obsidian(Human 지식) | 이 Repository에 연동 없음(확인) | Out of scope |
| LLM Wiki(AI 지식/Retrieval) | 없음 | Out of scope |

**판정**: Checkpoint는 이미 Freeze된 자산이고 v2.0이 건드릴 이유가
없다. Memory/Knowledge는 v2.0 목표 정의(사용자 §1)에 아예 등장하지
않는 개념이며, 이번 Freeze Review 범위에서 **추가하지 않는다** —
Freeze 가능/불가 판단 대상이 아니라 애초에 **Scope 밖**이다.

---

## 9. Risk / Portfolio

### 9-1. Risk

| 질문 | 판단과 근거 |
|---|---|
| Risk는 Team-level인가 HQ-level인가 | **판단 불가 — 실제 관찰이 없다.** 현재 어떤 Team도 Risk에 해당하는 산출물을 생성한 적이 없다. TradingAgents는 Risk를 "종목 1개에 대한 3관점 토론"(Team 수준에 가까움)으로 구현했지만(§2-1), 사용자가 원하는 것은 "Portfolio 전체 관점의 Risk"(HQ 수준)이다 — 이 둘은 다른 문제이고, TradingAgents 사례는 후자에 대한 근거가 되지 못한다 |
| Portfolio-level Risk가 필요한가 | **필요성 자체가 아직 관찰되지 않았다.** Investment HQ는 지금 "포트폴리오"(여러 종목의 조합)라는 개념 자체를 다뤄본 적이 없다(모든 실행이 종목 1건 단위) |
| Trader와 Risk의 책임 경계 | 정의할 Trader 자체가 없으므로(§3·§4) 경계를 지금 그을 근거가 없다 |
| Risk와 Portfolio Manager의 책임 차이 | 아래 9-2와 동일한 이유로 미정 |
| 실제 Investment HQ에서 Risk Need가 관찰됐는가 | **아니오.** 18회 Dogfooding 어디에서도 "리스크 판단이 필요했는데 못 했다"는 기록이 없다(Closure/Freeze 문서에 그런 기록 없음, 직접 확인) |
| Evidence가 부족하면 지금 Freeze할 수 있는가 | **아니오** |

### 9-2. Portfolio

사용자가 제시한 개념(Stock BUY + Dividend BUY + ETF BUY → Portfolio
Manager가 현재 Portfolio 상태를 보고 일부를 HOLD/축소)은 **TradingAgents
에도 존재하지 않는, Investment HQ가 스스로 설계해야 하는 완전히 새로운
책임**이다(§2-2 FACT: TradingAgents의 Portfolio Manager는 종목 1개
단위). 즉 이 부분은 "TradingAgents Reference를 참고해 채택 여부를
판단"하는 것 자체가 불가능하다 — **참고할 Reference Architecture가
없다.**

- **Portfolio Manager의 실제 책임**: 정의된 바 없음(설계 대상이지
  검토 대상이 아니다).
- **Portfolio State 필요성**: §7에서 판정 — 정의할 데이터가 없어
  Freeze 불가.
- **Risk와 Portfolio Manager의 경계**: 둘 다 정의되지 않았으므로
  경계도 정의 불가.
- **Portfolio Decision Contract**: 아래 §Trading Decision Contract와
  동일한 이유로 지금 확정 불가.

**판정**: Risk/Portfolio 축은 **Evidence가 전무**하고, 참고할 외부
Reference도 없다(TradingAgents가 다루는 문제와 범위가 다름) —
**Freeze 대상에서 명확히 제외한다.**

---

## Trading Decision Contract (사용자 §6 대응)

| 필드 | TradingAgents 근거(§2-3) | Investment HQ 필요성 판단 |
|---|---|---|
| `action`(BUY/SELL/HOLD) | `TraderProposal.action`(3단계 Enum) | Trader 자체가 없으므로(§4) 확정 불가 |
| `confidence` | **TradingAgents의 어떤 Trading Decision 스키마에도 없다**(§2-3 FACT) | 사용자 후보에 있었지만 외부 Reference의 근거가 없다 — 임의로 넣을 수 없다(사용자 지시: "근거가 부족하면 임의로 확정하지 않는다") |
| `rationale`/`reasoning` | `TraderProposal.reasoning`(2~4문장) | Investment HQ의 기존 산출물(Synthesis 등)이 이미 이런 서술형 근거를 생성하는 패턴을 갖고 있어 형식상 재사용 가능성은 있음 — 그러나 담을 내용(무엇에 대한 근거인가)이 아직 없다 |
| `expected_direction` | TradingAgents에 없음(action이 사실상 방향) | 근거 없음 |
| `time_horizon` | **Trader가 아니라 Portfolio Manager**(`PortfolioDecision.time_horizon`, optional)에만 존재(§2-3 FACT) | 사용자 후보는 이를 Trading Decision(Team-level) 필드로 뒀으나, TradingAgents Evidence는 오히려 **Portfolio-level 필드**임을 시사한다 — 사용자 초안의 배치가 재검토 대상 |
| `risk_notes` | TradingAgents는 Risk Debator의 History 전체를 Portfolio Manager에 전달, 별도 필드로 축약하지 않음 | 근거 불충분 |
| `asset` | 자명(식별자) | 문제없음 — 단, 확정할 Contract 자체가 없어 의미 없음 |
| (TradingAgents에만 있는 것) `entry_price`, `stop_loss`, `position_sizing` | Trader 필드(§2-3) | 사용자 후보에 없던 필드 — Position sizing/entry/stop을 Trader 책임으로 볼지 Portfolio 책임으로 볼지는 §5(Trader) 질문과 직결, 아직 미정 |

**Trader vs Portfolio-level 책임(사용자 §5 대응)**: TradingAgents의
실제 배치(§2-3)를 근거로 삼으면 — `action`/`reasoning`/(선택적)
`entry_price`·`stop_loss`·`position_sizing`은 **Trader(개별 자산)**
책임, `rating`(비중 조정 포함 5단계)·`time_horizon`은 **Portfolio
Manager** 책임으로 나뉜다. 이는 **하나의 유효한 참고 패턴**이지, 이대로
확정할 만큼 Investment HQ 쪽 Evidence(실제로 이렇게 나눠서 실행해 본
경험)가 있는 것은 아니다.

**판정**: Trading Decision Contract는 **필드 하나도 확정할 수 없다.**
`confidence`는 외부 Reference에조차 근거가 없고(임의 추가 금지),
`time_horizon`은 사용자 초안이 배치한 계층(Team-level)과 TradingAgents
Evidence가 시사하는 계층(Portfolio-level)이 다르다 — 이 자체가
"Evidence 없이 taxonomy를 확정하면 위험하다"는 것을 보여주는 구체적
사례다. **세 Team이 동일 Contract를 쓸 수 있는가**라는 질문에 답하려면
Contract가 먼저 존재해야 하는데, 그 전 단계(필드 확정)부터 막혀 있다.

---

## 10. Execution

`STRUCTURE-V1.0-FROZEN.md`와 `COMPONENT-CANDIDATE-0001.md`를 직접
대조한 결과, **"Execution"이라는 단어가 이미 Jarvis OS 안에서 두 가지
다른 의미로 쓰이고 있다** — 이번 v2.0 논의가 이 둘을 혼동할 위험이 크다:

1. **Kernel의 Execution(C-4)** — `core/execution_layer/`, 이미
   Accept·구현된 Kernel Component. Domain Model의 `... → Capability →
   Execution → Provider/Tool/MCP`가 가리키는 것은 **"LLM/Engine 호출을
   실행하는 계층"**이다(`call_engine()`이 이 경계).
2. **사용자 §12가 말하는 "Execution"** — Portfolio Decision을 실제
   매매(브로커 주문 등)로 옮기는 **Trade Execution**. 이는 Kernel의
   Execution(1)과 이름만 같을 뿐 **완전히 다른 책임**이다 — 증권사/거래
   API 연동, 주문 체결, 체결 확인 같은 Investment-domain 전용 문제이며
   Kernel Execution Layer가 다루는 "Engine 호출"과 무관하다.

**판정**: 이 두 "Execution"을 같은 이름으로 논의를 진행하면 Boundary
혼동이 발생한다(사용자 §12가 우려한 바로 그 상황). 게다가 **Trade
Execution은 이번 조사에서 Investment HQ 어디에도 구현·계획·Evidence가
없다** — Portfolio Decision 자체가 없으니(§9) 그것을 "실행"할 대상도
없다. **Trade Execution 축은 Freeze는커녕 설계 착수 근거조차 없다.**
사용자 지시(§12) "Core Architecture 변경이 필요하다고 판단하면 구현을
중단하고 보고" — 지금은 구현 이전 단계이므로 중단할 구현은 없지만,
**"Execution"이라는 용어를 v2.0 문서에 그대로 쓰면 Kernel의
Execution(C-4, 이미 Frozen)과 혼동될 여지가 있다는 것 자체가
선행조건(§18)에 포함돼야 한다.**

---

## 11. Reporting / Dashboard

- **Team-level Report**: 이미 존재(`final_report.md`), Freeze 상태 —
  변경 불필요.
- **Portfolio-level Report / Final Report**: Portfolio Decision이 없으니
  (§9) 만들 대상 자체가 없다.
- **Dashboard**: `STRUCTURE-V1.0-FROZEN.md`에서 `dashboard/`는 **"사용자가
  Jarvis OS와 HQ를 관리하는 외부 인터페이스"**로 이미 명확히 정의돼
  있다 — Investment HQ 내부 Component가 아니라 **Jarvis OS 상위
  Dashboard**(Structure v1.0 Top-level)다. TradingAgents의 `cli/`는
  단순 콘솔 출력이며(§2-5), Investment HQ가 참고할 만한 "Investment
  전용 Dashboard 서브구조"를 제공하지 않는다.

**판정**: Dashboard는 이미 Structure v1.0에서 Investment HQ 밖의
책임으로 확정돼 있다 — 이번 v2.0 논의에서 재확인만 하면 되고, 새로
설계할 필요가 없다(Freeze 상태 유지, 사용자 §13 "Dashboard를
Architecture 핵심 책임으로 불필요하게 확장하지 않는다"는 지시와 일치).

---

## 12. Structure v1.0 Mapping

| v2.0 후보 Component | Responsibility | Boundary | Owner | Architecture Need Evidence | Core 승격 필요? |
|---|---|---|---|---|---|
| Team(Stock/ETF/Dividend) | 자산군별 리서치 파이프라인 | `hqs/investment/teams/` | Investment HQ | 18회 Dogfooding, **충분** | 아니오 |
| Common Layer(agents/workflow/prompts) | (가정) 3 Team 공통 로직 | `hqs/investment/` | Investment HQ | **불충분**(§5) — 유지보수 비용 관찰 안 됨 | 아니오, 지금은 만들지 않음 |
| Trader | 개별 자산 매매 방향 결정 | 미정 | 미정 | **없음**(§4·§9) | 판단 불가 |
| TradingDecision Contract | Team→HQ 공통 반환 계약 | 미정 | 미정 | **없음**(필드 하나도 확정 불가, §Trading Decision Contract) | 판단 불가 |
| Risk(HQ-level) | 포트폴리오 리스크 평가 | 미정 | 미정 | **없음**(§9-1) | 판단 불가 |
| Portfolio Manager | Cross-Team 포지션 조정 | 미정 | 미정 | **없음, 외부 Reference도 없음**(§9-2) | 판단 불가 |
| Portfolio State | HQ 전체 포트폴리오 상태 | 미정 | 미정 | **없음**(§7, Kernel C-7과 일치) | Kernel C-7이 이미 "가장 이른 단계"로 판정 — 지금 Core 승격 검토 자체가 시기상조 |
| Trade Execution | 실제 매매 실행 | 미정(Kernel Execution과 용어 혼동 위험, §10) | 미정 | **없음** | 판단 불가, 용어부터 정리 필요 |
| Dashboard | 외부 관리 Interface | `dashboard/`(Investment HQ 밖) | Jarvis OS(Top-level) | 이미 Structure v1.0에서 확정 | 이미 Core 영역(Structure v1.0 정의) |
| Checkpoint | 실행 상태 저장/재개 | `hqs/investment/checkpoint.py` | Investment HQ | v1.0 Freeze Evidence로 충분 | 아니오(Investment-specific 유지, `INVESTMENT-HQ-V1.0-FREEZE-0001.md` 판정 재확인) |

**HQ에서 해결 가능한 문제 vs Jarvis OS Core가 해결해야 하는 문제**:
Team/Common Layer/Checkpoint는 **HQ에서 이미 해결됐거나 해결 가능**
(추가 Kernel 개입 불필요). Trader/TradingDecision/Risk/Portfolio/
Execution은 **"HQ 문제인지 Core 문제인지조차 아직 판단할 근거가
없다"** — Component가 존재하지 않는데 그 소속을 미리 정할 수 없다.
Portfolio State만은 Kernel C-7 판정(Multi-HQ 시나리오 미관찰)과 정확히
같은 이유로 **"지금은 Core 문제인지 판단할 단계 자체가 아니다"**라고
명확히 말할 수 있다.

---

## 13. Governance 검토

- **RFC → ADC → ADR**: 유지, 이번 문서도 그 절차를 거치지 않는다(§0의
  문서 성격과 일치, 이 Review 자체가 Governance 판단이지 Architecture
  결정이 아니다).
- **Phase 7 HOLD**: `roadmap.md` 직접 확인 — Phase 6 이후 전부
  미착수, Phase 7은 "⬜ 미착수(Phase 7 ADR 승인 시)". 이번 v2.0 논의가
  Phase 7 착수 근거를 자동으로 만들지 않는다(§15 사용자 지시와 일치).
  다만 §6(LangGraph)·§7(Portfolio State)에서 확인했듯, v2.0의 핵심
  요구(HQ-level Graph, Portfolio State)는 **Kernel Governance가 아직
  다루지 않은 영역과 정확히 겹친다** — Phase 7을 우회하지 않고 진행할
  방법이 현재로선 "Investment HQ 내부에서 Kernel 개념 없이 최소
  구현으로 시작"뿐인데, 그 최소 구현조차 무엇을 만들지 정할 Evidence가
  없다(§9·§Trading Decision Contract).
- **Architecture Need → 자동 Promotion 아님**: 이번 Review에서 발견한
  Gap(Trader/Risk/Portfolio 부재)을 "그러니 지금 Kernel Component로
  만들자"로 해석하지 않는다 — 오히려 반대로, **HQ 내부에서 먼저 최소
  구현·Dogfooding을 쌓아야 Kernel 승격 여부를 판단할 자격이 생긴다**는
  기존 원칙(C-2, C-7 판정의 논리)을 그대로 적용한다.
- **IMPLEMENTATION_RULES 충돌 가능성**: §6에서 확인한 대로 LangGraph
  도입은 Workflow Parser/Scheduler 금지와 정면 충돌할 위험이 있다 —
  이는 새 규칙이 아니라 **기존 금지 조항의 재확인**이다.

---

## 14. Evidence Gap 분석(사용자 §17 분류 적용)

| 항목 | 분류 | 근거 |
|---|---|---|
| Trader(방향 결정 책임) | **C. 실제 Need 자체가 아직 발생하지 않음** | 현재 모든 Team instruction이 방향 결정을 명시적으로 금지한다(§1) — 이는 우연한 공백이 아니라 v1.0 Freeze 시점의 의도적 Boundary였다. Need가 "아직 관찰 안 됨"이 아니라 "지금까지 의도적으로 배제돼 왔다"는 점에서 §17의 C에 해당하되, **의도적 배제였다는 사실 자체를 다음 판단자가 알아야 한다** |
| TradingDecision Contract 필드(confidence 등) | **A(양 부족) + E(정의 자체가 잘못됨)의 혼합** | `confidence`는 외부 Reference에도 없는데 사용자 초안에 있었다 — 후보 자체가 근거 없이 설계됐을 가능성(E)과, 설계를 뒷받침할 실행 Evidence가 원천적으로 없다는 점(A)이 같이 작용 |
| Risk(HQ-level) | **C. Need 미발생** | 18회 실행 중 Risk 판단이 필요했던 사례 자체가 기록에 없다 |
| Portfolio Manager(Cross-Team) | **C + 외부 Reference 부재** | TradingAgents도 이 문제를 다루지 않는다(§2-2) — "잘못된 방향에서 수집 중(B)"이 아니라 **애초에 수집할 곳(Reference)이 없다** |
| Portfolio State | **C, Kernel 판정과 일치** | C-7 "가장 이른 단계, Multi-HQ 시나리오 미관찰"이 Investment HQ 관찰과 정확히 일치 |
| LangGraph 필요성 | **D. 기존 Architecture로 이미 해결 가능함** | 현재 4-Wave 하드코딩이 18회 무사고 — conditional routing/토론 라운드가 필요하다는 신호 없음. 오히려 도입 시 IMPLEMENTATION_RULES와 충돌(§6) |
| Common Layer(agents/workflow/prompts) | **D. 기존 Architecture(복제)로 이미 해결 가능함** | 3 Team 복제 방식이 18회 문제없이 동작, 유지보수 비용 미관찰(§5) |
| Trade Execution | **C. Need 미발생 + 용어 자체가 Core Execution과 충돌 위험(E 인접)** | Portfolio Decision이 없으니 실행할 대상이 없고, "Execution"이라는 이름이 이미 Kernel에서 다른 의미로 쓰이고 있다(§10) |

---

## 15. Open Issues

1. **"Research Manager/Synthesis" 계층의 실제 정체가 불명확**(§4) —
   현재 Synthesis는 방향을 정하지 않는데, v2.0 Workflow는 Trader
   앞에 방향 결정 주체를 요구한다. 이 gap이 Freeze 이전에 먼저
   메워져야 한다.
2. **"Execution" 용어 충돌**(§10) — Kernel Execution Layer(C-4)와
   Trade Execution을 같은 이름으로 계속 쓰면 향후 문서/코드에서 혼동
   가능성이 높다.
3. **TradingDecision Contract 필드가 사용자 초안과 외부 Evidence 사이에서
   불일치**(`time_horizon`의 계층, `confidence`의 존재 여부) — Contract
   설계 자체를 다시 열어야 한다.
4. **Portfolio 개념에 대한 외부 Reference 부재** — TradingAgents가 이
   문제를 다루지 않으므로, Investment HQ가 이 부분만큼은 순수하게
   자체 설계해야 한다. 참고할 만한 실행 사례(내부든 외부든)가 전혀
   없는 상태에서 Contract를 확정하는 것은 위험하다.
5. **checkpoint_enabled 기본값 False인 이유가 TradingAgents 쪽도
   불명확**(Phase7 문서 UNKNOWN 재확인) — 참고 시 주의.

---

## 16. Freeze Decision

### A~J 기준 평가

| 기준 | 평가 | 근거 |
|---|---|---|
| A. Responsibility | **부분 충족** | Team/Common Layer는 명확(§5). Trader/Risk/Portfolio/Execution은 책임 자체가 정의되지 않음(§4·§9·§10) |
| B. Boundary | **미충족** | Execution 용어 충돌(§10), Portfolio Manager 이름 혼동(§3), HQ/Kernel 경계는 Portfolio State 관련해 판단 불가(§7·§12) |
| C. Workflow | **미충족** | HQ-level Workflow를 설명할 수단 자체가 없다(§6) — "설명 가능한가"에 답하려면 최소한 초안이라도 있어야 하는데, 존재하지 않음 |
| D. State | **부분 미충족** | Team State는 명확(그대로 유지), Portfolio State는 정의 자체가 없음(§7) |
| E. Contract | **미충족** | TradingDecision Contract 필드를 하나도 확정하지 못함(§Trading Decision Contract) |
| F. Commonization | **충족** | Common 구조를 "만들지 않는다"는 결론 자체는 Evidence(복제 방식 무사고 18회)에 기반함(§5) — 이 축만은 Freeze 가능 |
| G. Domain Extension | **충족** | Stock→Dividend Stock→ETF 확장은 이미 18회로 실증됨(§1) |
| H. Integration | **판단 불가** | LangGraph/Memory/Knowledge/Checkpoint 대부분이 "도입하지 않음"으로 정리되어 충돌 자체가 발생하지 않음(§6·§8) — 이 축은 사실상 통과지만, 통과의 이유가 "설계했더니 안 맞더라"가 아니라 "애초에 안 만들기로 해서"라는 점을 분명히 해야 한다 |
| I. Governance | **충족(단, 조건부)** | Phase 7 HOLD를 우회하지 않는 한 충돌 없음(§13) — 단 LangGraph를 실제로 도입하면 즉시 충돌 |
| J. Implementation Readiness | **미충족** | Contract/Responsibility/Boundary가 없는 상태에서 Claude Code가 구현하면 반드시 임의 설계를 하게 된다(§Trading Decision Contract가 보여준 필드 불일치가 그 증거) |

### 최종 판정

## **C. NOT READY**

**판정 이유(요약)**: 사용자가 정의한 v2.0의 목표 Workflow 6단계(Team
Analysis → Team Trading Decision → HQ-level Risk Assessment →
Portfolio Decision → Execution → Reporting) 중, **앞의 1단계(Team
Analysis)만 Frozen 상태이고 나머지 5단계는 코드·Evidence·외부
Reference 어디에도 존재하지 않는다.** 이는 "Evidence가 조금 부족한"
수준이 아니라, **핵심 개념(Trader, TradingDecision, Risk, Portfolio,
Execution) 자체가 아직 한 번도 실행되거나 설계된 적이 없는 백지
상태**다(§14의 C 분류가 대부분을 차지). Domain Team 축(§5·G기준)만은
명확히 Freeze 가능하지만, 이것만으로는 "Investment HQ v2.0 Architecture
Freeze"라고 부를 수 없다 — 사용자가 v2.0의 핵심으로 제시한 것이
정확히 지금 비어 있는 나머지 5단계이기 때문이다.

---

## 17. Freeze 가능 시 최종 구조

**해당 없음(NOT READY).** 대신 아래를 "지금 확정 가능한 부분"과
"Freeze 전 반드시 채워야 할 선행조건"으로 나눠 기록한다.

### 지금 이미 확정된 것(재확인, 변경 없음)
```
Investment HQ
└── (선택) Investment Division
    ├── Stock Team    (5 analysis, Frozen)
    ├── ETF Team      (6 analysis, Frozen)
    └── Dividend Stock Team (7 analysis, Frozen)
        모두: N-analysis(병렬) → Bull/Bear(병렬) → Synthesis → Final Report
        Common Layer 없음(의도적, 복제 유지)
        Checkpoint: Investment-specific, Kernel 승격 대상 아님
```

### 선행조건(Freeze 전 반드시 필요, §18)

1. **Research Manager/Synthesis 경계 재정의** — 방향 결정 주체가
   Synthesis 확장인지 별도 신규 단계인지부터 결정(§4·§15-1).
2. **최소 1건의 실제 Trader Dogfooding** — 기존 Team의 Synthesis
   산출물을 입력으로, 방향(action) + 근거만 담은 **최소 스키마**로
   실제 실행 1건을 project-local(기존 관행)로 먼저 시도해 실제로
   무엇이 나오는지 관찰한다. TradingAgents 스키마(§2-3)를 시작점
   참고용으로만 쓰고, 그대로 채택하지 않는다.
3. **Risk/Portfolio Need의 실측** — 여러 Team의 Trader 결과가 실제로
   상충하는 사례(예: Stock BUY vs Dividend HOLD가 같은 섹터일 때)가
   나올 때까지는 Risk/Portfolio를 설계하지 않는다 — 최소 2~3개 Team의
   Trader 결과를 나란히 놓고 "정말 조정이 필요한가"를 먼저 관찰한다.
4. **"Execution" 용어 분리** — Kernel Execution Layer(C-4)와 Trade
   Execution을 문서 레벨에서부터 다른 이름으로 구분(예: "Trade
   Execution" 고정 표기)한다.
5. **LangGraph는 Prototype에서만** — 격리된 `projects/*-prototype/`에서
   기존 IMPLEMENTATION_RULES 금지 조항과 충돌하는지 실증 후 판단한다
   (Kernel 코드에 먼저 들여오지 않는다).
6. **TradingDecision Contract는 필드 단위로 점증 확정** — 한 번에
   전체 스키마를 확정하지 않고, §Trading Decision Contract가 식별한
   불일치(`confidence`, `time_horizon` 계층)부터 실제 실행으로
   검증한다.

---

## 18. Freeze 이후 Implementation Plan

**작성하지 않는다.** §16 판정이 NOT READY이므로, 사용자 지시(§19,
§20)에 따라 Implementation Plan은 FREEZE READY 판정 시에만 제시한다.
대신 위 §17 "선행조건"이 이 문서의 실질적 Next Step이다 — 이 항목들은
전부 **코드 구현이 아니라 최소 규모의 Dogfooding/관찰**이며, 다음 세션이
착수할 수 있는 구체적 단위다.

---

## Self Review

- Architecture를 Freeze했는가 — **아니오**.
- 새 RFC/ADC/ADR을 생성했는가 — **아니오**.
- `hqs/investment/`, `core/` 코드를 수정했는가 — **아니오**.
- TradingAgents 코드를 복제·수정했는가 — **아니오**.
- Common Layer를 임의로 만들었는가 — **아니오**(오히려 만들지 않는
  근거를 재확인).
- 세 Team에 동일 구조를 강제했는가 — **아니오**.
- Core에 새 책임을 추가했는가 — **아니오**.
- Phase 7 HOLD를 우회했는가 — **아니오**.
- Evidence 없이 Promotion을 주장했는가 — **아니오**(오히려 Evidence
  부재를 근거로 NOT READY를 판정).
- LangGraph 때문에 Architecture를 변경했는가 — **아니오**(오히려
  LangGraph 도입의 위험을 지적).
- 구현 과정에서 Architecture를 임의 결정했는가 — **아니오**(구현
  자체를 하지 않았다).
