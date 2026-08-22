# PHASE7-EXTERNAL-OBSERVATION-TRADINGAGENTS-0001

**문서 성격**: Evidence/Observation 문서. **RFC/ADC/ADR이 아니다.**
`COMPONENT-CANDIDATE-0001`과 동일한 지위 — Phase 7 HOLD 기간의 외부
Architecture Observation을 기록한다. 이 문서는:

- `docs/decisions/adc/ADC.md`의 어떤 항목도 상태를 바꾸지 않는다.
- 새 RFC/ADC/ADR을 생성하지 않는다.
- Architecture Baseline·Structure v1.0·Freeze 문서를 수정하지 않는다.
- `core/`, `hqs/investment/` 코드를 수정하지 않는다.
- TradingAgents 저장소 코드를 수정하거나 복사하지 않는다.

**목적**: 외부 Investment/Trading Agent Framework(TradingAgents)를 실제로
설치·독립 실행하고 Investment HQ와 비교하여, Phase 7 HOLD를 재개할
정도의 새로운 Architecture Observation이 발생하는지 확인한다.

---

## 0. 대상 및 환경

| 항목 | 값 |
|---|---|
| 외부 저장소 | https://github.com/TauricResearch/TradingAgents.git |
| Commit | `a33fd4c0f134485a43553a2c23a63cb14adbd88f` ("docs: streamline README header", 2026-07-18) |
| `pyproject.toml` version | `0.3.1` |
| Python 요구 | `>=3.10` (세션 환경: Python 3.11.15, 별도 venv 사용) |
| 설치 위치 | 세션 scratchpad(`/tmp/.../scratchpad/external/TradingAgents`) — Jarvis OS 저장소 밖, 별도 venv(`ta-venv`) |
| Jarvis OS 측 비교 대상 | `hqs/investment/{run.py, engine_client.py, checkpoint.py, teams/stock_team.py}`, `hqs/investment/STRUCTURE.md` |

---

## 1. 설치

`pip install -e <TradingAgents>` 를 별도 venv에서 실행 — 에러 없이
성공(`EXIT: 0`). Jarvis OS의 어떤 dependency 파일(`pyproject.toml` 등)도
수정하지 않았고, TradingAgents를 Jarvis OS dependency로 등록하지 않았다.
TradingAgents 코드도 수정하지 않았다.

---

## 2. 독립 실행 검증 (FACT)

| 단계 | 결과 |
|---|---|
| 1) import | **성공** — `import tradingagents`, `TradingAgentsGraph` import 정상 |
| 2) configuration 로딩 | **성공** — `DEFAULT_CONFIG` 로드됨. 기본값: `llm_provider=openai`, `deep_think_llm=gpt-5.5`, `quick_think_llm=gpt-5.4-mini`, `max_debate_rounds=1`, `max_risk_discuss_rounds=1`, `checkpoint_enabled=False` |
| 3) API 연결 | **실패(환경 제약)** — `TradingAgentsGraph(config=config)` 생성 시 `ValueError: API key for provider 'openai' is not set. Please set the OPENAI_API_KEY environment variable...`. 이 세션 환경에 어떤 LLM API Key도 존재하지 않음(`env \| grep -i api_key` 결과 없음) — TradingAgents 결함이 아니라, 이 세션에 Key가 주어지지 않았기 때문 |
| 3-보조) Market Data 연결(yfinance, Key 불필요 경로) | **실패(환경 제약)** — `yfinance.Ticker('AAPL').history()` 호출 시 `curl: (7) CONNECT tunnel failed, response 403`. 이 세션의 outbound 프록시가 Yahoo Finance 호스트를 차단 — TradingAgents 결함이 아니라 세션 네트워크 정책 |
| 4) 최소 분석 실행 | **미실행** — 3)이 두 경로(LLM/Market Data) 모두 세션 제약으로 막혀 실행 불가 |
| 5) 결과 생성 | **미실행** |
| 6) 오류 전파 | 관찰됨 — 두 실패 모두 조용히 무시되지 않고 명시적 예외로 즉시 전파됨(`ValueError`, `ConnectionError`) |
| 7) 종료 상태 | 두 경우 모두 Python 프로세스가 예외로 명확히 종료(`Exception` catch 후 메시지 출력, 스크립트 자체는 `exit 0`로 방어적으로 짜서 확인만 했다) |

**판정**: 설치·import·configuration까지는 **직접 확인된 FACT**다.
실제 LLM 호출을 포함한 end-to-end 분석 실행은 이 세션에서 **BLOCKED**
(API Key 부재 + 프록시의 시장 데이터 호스트 차단) — TradingAgents
자체의 실행 가능성을 부정하는 근거가 아니라, 이 세션이 가진 두 개의
독립적 외부 접근 제약이다. 사용자가 로컬 환경에서 실제 Key를 입력하고
직접 실행하면 이 두 제약은 사라진다(§3 참조).

AAPL/EFA(ETF)/PG(Dividend Stock) 각각에 대한 **실제 실행 결과**는
위 이유로 확보하지 못했다 — 아래 §4의 ETF/Dividend Stock 지원 여부
판정은 **실행 결과가 아니라 코드 직접 확인(FACT)**에 근거한다(추측
아님).

---

## 3. API Provider / Key (FACT, 실제 값 미기록)

TradingAgents `.env.example`(2944 bytes, 실제 코드 파일 확인)에서
직접 확인:

- **지원 LLM Provider**: OpenAI, Google, Anthropic, xAI, DeepSeek,
  DashScope(+CN), Zhipu(+CN), MiniMax(+CN), OpenRouter, Mistral,
  Moonshot, Groq, NVIDIA, OpenAI-호환 커스텀 엔드포인트, AWS Bedrock,
  로컬 Ollama — `llm_provider` 설정값 하나로 전환.
- **기본 Provider**: `openai` (`default_config.py` 확인).
- **Market/Data Key는 LLM Key와 분리**: 시세 데이터는 yfinance(Key
  불필요)가 기본이며, `alpha_vantage_*.py`가 대안 경로로 별도 존재.
  거시경제 데이터는 FRED API(`FRED_API_KEY`, 선택)로 별도 분리.
- **필요 환경변수**: 사용하는 Provider 하나의 `*_API_KEY`(예:
  `OPENAI_API_KEY`) — 미설정 시 `TradingAgentsGraph()` 생성 단계에서
  즉시 `ValueError`로 실패(§2 확인).

**Key 취급**: 실제 값은 어디에도 기록하지 않았다(prompt/stdout/
source/커밋 전부 미기록). 아래처럼 `.env.example`만 이미 저장소에
존재함을 확인했고, Jarvis OS 쪽에 별도 `.env.example`을 새로 만들지
않았다(TradingAgents 자체 clone에 이미 존재, Jarvis OS에 복사하지
않음 — §8 절대 금지 준수).

---

## 4. Investment HQ 비교 (FACT 기반)

| 항목 | TradingAgents | Investment HQ (`hqs/investment/`) |
|---|---|---|
| **A. Agent** | LangGraph 노드 함수(`create_market_analyst()` 등)로 정의, `AgentState`(LangGraph `MessagesState` 상속 TypedDict)를 입력/출력으로 공유 | 순수 Python 함수(`fundamental_analyst_fundamental_analysis()` 등), `str` 입력/출력만 사용 — LangGraph/State 프레임워크 없음 |
| **B. Team/역할 그룹** | 역할 카테고리: Analyst(4, asset_type에 따라 필터링) → Researcher(Bull/Bear) → Research Manager → Trader → Risk Debator(3) → Portfolio Manager. Team 개념 없음, 전부 하나의 그래프 | Stock(5)/ETF(6)/Dividend Stock(7) **Team**이 명시적으로 분리된 모듈(`teams/*.py`)이며, asset class별로 **역할 수 자체가 다르다**(Dogfooding 반복으로 결정, `*-TEAM-DEFINITION-0001.md`) |
| **C. Workflow 구성** | `langgraph.StateGraph` — 노드/엣지를 명시적 그래프 API로 선언(`workflow.add_node`, `add_conditional_edges`). 순차/조건부 엣지로 표현 — **분석가 체인은 순차 실행**(analyst1→tool→clear→analyst2→...), 병렬 아님 | Wave 하드코딩 함수 호출(`stock_team.run()` 내부 4단계) — Workflow Parser/Scheduler 없음, `STRUCTURE.md`가 명시적으로 "Workflow Parser 구현 금지" 원칙 |
| **D. Task** | 그래프의 각 노드 = 하나의 LLM 호출(ReAct, tool-calling 포함) | Wave 내부 각 함수 호출 = 하나의 `call_engine()` 호출(단일 프롬프트, tool 없음) |
| **E. State** | **명시적 상태 모델**(`AgentState` TypedDict, `InvestDebateState`, `RiskDebateState`) — LangGraph reducer가 노드 간 상태 병합/누적을 프레임워크 수준에서 관리 | **상태 모델 없음** — 파이썬 지역 변수(`wave1_results` dict)로 전달, `Checkpointer`가 완료된 단계의 산출물만 파일로 저장(§I) |
| **F. Context 전달** | `AgentState`를 그래프 실행 전체에 스레딩, `resolve_instrument_context()`가 실행 시작 시 한 번 종목 정체성을 확정해 주입 | `raw_data.md`를 프로젝트 시작 시 한 번 읽어 섹션 태그(`[FUNDAMENTAL]` 등)로 파싱, 각 함수 호출마다 필요한 섹션만 문자열로 전달 |
| **G. Execution(실제 LLM 호출)** | `tradingagents/llm_clients/*`(Provider별 client, `factory.py`가 provider 이름으로 분기) — Jarvis의 Execution Layer(C-4)와 유사한 "여러 Provider를 하나의 인터페이스로 통일"하는 자체 추상화를 **이미 내부에 보유** | `hqs/development/mvp/engine.py`의 `call_engine()` 단일 함수(Claude Code 하나만 호출) — Investment HQ는 이 함수를 그대로 import, 별도 Provider 추상화 없음 |
| **H. Parallel Execution** | **관찰되지 않음** — 코드 전체에 `ThreadPoolExecutor`/`asyncio`/LangGraph `Send()` fan-out 없음(grep 확인). 그래프 엣지는 전부 순차/조건부 분기이며 동시 실행 노드가 없다 | **명시적** — `ThreadPoolExecutor`로 Wave 내부 독립 분석을 동시 실행(Wave1: 5개 병렬, Wave2: 2개 병렬), PR #80~83에서 실측 검증된 패턴 |
| **I. Checkpoint/Resume** | LangGraph `SqliteSaver`, 종목당 SQLite DB 하나(`checkpoints/{TICKER}.db`), **그래프 스텝 단위** 저장·재개(옵션, 기본 `checkpoint_enabled=False`) — `_run_signature()`로 analyst 선택/debate 라운드/asset_type이 바뀌면 체크포인트 자동 무효화 | 파일 기반(`Checkpointer`, `manifest.json` + `{step}.md`), **단계 이름 단위**(Wave의 각 named step) 저장, 재실행 시 완료된 step은 Engine 재호출 없이 스킵. 콘텐츠 레벨 실패 시그니처(`API Error:`) 감지 시 저장 안 함 |
| **J. Output/Artifact** | `reporting.py`의 `write_report_tree()` — 구조화된 리포트 트리 + 최종 `decision`(`propagate()`의 반환값) | Wave별 `.md` 파일(9개) + `call_log.json`(호출별 elapsed/문자수 로그) — project-local issue 디렉터리에 flat하게 기록 |
| **K. Error Handling** | LLM SDK 재시도(`TRADINGAGENTS_LLM_MAX_RETRIES`, provider별 SDK 레벨), 설정값 검증 실패 시 즉시 `ValueError`(loud fail) | `ContentFailureError` — 알려진 콘텐츠 실패 시그니처(`API Error:`)만 감지해 저장을 막고 재시도 대상으로 남김. 재시도 자체는 다루지 않음(다음 실행이 자연 재시도) |

---

## 5. Architecture 질문 (Q1~Q5)

### Q1. 새로운 책임이 실제로 필요한가?

**아니오.** TradingAgents를 "외부 Engine"으로 쓴다면, 필요한 것은
`propagate(ticker, date)` 호출 하나를 감싸는 얇은 호출 지점뿐이다 —
이는 지금 Investment HQ가 `engine_client.py`로 Claude Code를 감싸는
것과 **동일한 패턴**이다. TradingAgents는 자신의 Workflow(LangGraph
그래프)·State(`AgentState`)·Checkpoint(`SqliteSaver`)·Provider
추상화(`llm_clients/`)를 **전부 자기 내부에 이미 완결된 형태로
가지고 있다** — Jarvis OS가 그 안을 들여다보거나 재현할 필요가
없다. Investment HQ가 지금 Claude Code 호출을 "prompt 문자열 하나
넣고 결과 문자열 하나 받는" 블랙박스로 취급하는 것과 정확히 같은
경계에서, TradingAgents도 "ticker/date 넣고 decision 하나 받는"
블랙박스로 취급 가능하다(FACT: `main.py`의 `ta.propagate(...)` 가
정확히 이 형태).

### Q2. Adapter / Dispatch / Execution Component / Provider abstraction 중 무엇이 필요한가?

`engine_client.py`와 동급의 **얇은 호출 지점(Adapter라 부르기도
과할 정도)** 뿐이다. Dispatch(여러 Engine 중 동적 선택)·Execution
Component(Jarvis Kernel Context/Execution Layer와의 통합)·Provider
abstraction(Jarvis 레벨에서 여러 LLM Provider 통일) 어느 것도
필요하지 않다 — TradingAgents 자신이 이미 Provider abstraction을
내부에 갖고 있으므로 Jarvis가 중복 설계할 이유가 없다.

### Q3. 그 책임은 어디에 해당하는가?

| 책임 | 귀속 |
|---|---|
| TradingAgents 호출 지점(얇은 wrapper) | **Investment-specific**(HQ-local, `engine_client.py`와 동급) |
| Workflow(그래프)·State·Checkpoint·Provider 추상화 | **External Framework 내부 책임**(TradingAgents가 이미 소유, Jarvis가 관여할 지점이 없음) |
| Kernel Candidate로 새로 편입될 것 | **없음** |

### Q4. Structure v1.0 Domain Model과의 관계

`HQ → Project → Workflow → Stage → Task → Agent → Capability →
Execution → Provider/Tool/MCP` 중, TradingAgents 전체가 **Execution
→ Provider/Tool 경계의 단일 지점**으로 수렴한다 — TradingAgents 내부의
Analyst→Researcher→Trader→Risk Debator 체인(자체 Workflow)은 Jarvis
OS 쪽 Domain Model의 어떤 계층과도 대응하지 않는다(대응시킬 필요가
없다, 블랙박스이므로). 이는 `COMPONENT-CANDIDATE-0001.md`의 C-4
Execution 판정("이미 구현·Accept됨, Kernel이 관여하는 유일한 실제
경계")과 **정확히 일치**한다 — TradingAgents 도입은 그 판정을
반박하는 것이 아니라, 다른 각도(외부 Framework 도입 시나리오)에서
같은 결론을 재확인한다.

### Q5. Phase 7 HOLD를 재개할 정도의 새 Observation이 발생했는가?

**아니오.** TradingAgents는 Jarvis OS가 미해결로 두고 있는 개념들
(Workflow 표현, State 모델, Checkpoint, Provider 추상화)을 전부
자체적으로 이미 설계·구현했지만, 이 사실이 Jarvis OS *자신의*
Kernel 설계에 새 압력을 주지 않는다 — Jarvis가 TradingAgents를
쓰려면 그 내부를 몰라도 되기 때문이다(Q1~Q4). 오히려 이번 관찰은
"Execution 경계 하나만 있으면 임의의 외부 Multi-Agent Framework를
붙일 수 있다"는 기존 판정의 **외부 검증(cross-validation)**에
가깝다.

---

## 6. FACT / INFERENCE / UNKNOWN

**FACT**
- TradingAgents commit `a33fd4c0`, `pyproject.toml` v0.3.1, 별도
  venv에 `pip install -e .` 성공.
- `import`·`DEFAULT_CONFIG` 로드 성공(실제 실행 로그로 확인).
- 기본 Provider `openai`, Key 미설정 시 `TradingAgentsGraph()` 생성
  단계에서 명시적 `ValueError`.
- 이 세션에 LLM API Key 없음(env 확인), yfinance 호출이 세션
  프록시에서 403으로 차단됨(실제 에러 메시지 확인).
- `AssetType` enum은 `STOCK`/`CRYPTO` 두 값만 가지며(`cli/utils.py`
  확인), ETF·배당주 전용 asset_type이 코드에 존재하지 않는다 —
  EFA·PG 같은 티커는 `detect_asset_type()`에서 `STOCK`으로 분류되어
  **일반 Stock 경로로 처리**된다(코드 직접 확인, 실행 결과 아님).
- 코드 전체에 `ThreadPoolExecutor`/`asyncio`/LangGraph `Send()`
  fan-out 없음(grep으로 확인) — 병렬 실행 미관찰.
- Investment HQ의 병렬화(Wave 내 `ThreadPoolExecutor`)·Checkpoint
  (파일 기반, step 단위)·Team 분리(Stock/ETF/Dividend Stock 역할 수
  차등)는 기존 코드 그대로(수정 없음, 이번 세션에서 읽기만 함).

**INFERENCE**
- TradingAgents를 Investment HQ에 붙인다면 `engine_client.py`와
  동급의 얇은 wrapper 하나로 충분하다는 판단은, TradingAgents가
  자신의 Workflow/State/Checkpoint/Provider를 전부 내부에서
  완결한다는 FACT로부터 도출한 것이다(Q1~Q3).
- ETF/Dividend Stock이 "일반 Stock 경로로 처리 가능"이라는 판정은
  `AssetType` enum과 `detect_asset_type()` 로직(FACT)에서 도출한
  것이며, 실제 실행 결과(리포트 품질 등)로 검증한 것은 아니다.

**UNKNOWN**
- TradingAgents가 실제로 EFA/PG에 대해 생성하는 리포트의 품질·
  ETF/배당주 특유의 판단(분배율, NAV 괴리 등)을 실제로 반영하는지는
  **이 세션에서 확인 불가**(실행 자체가 BLOCKED) — 로컬 환경에서
  Key를 넣고 사용자가 직접 실행해야 확인 가능하다.
- `checkpoint_enabled=False`가 기본값인 이유(운영 관행인지 설계
  의도인지)는 README/코드만으로 확정할 수 없다.

---

## 7. Phase 5~7 영향

없음. 8개 Kernel Component 후보(C-1~C-8, `COMPONENT-CANDIDATE-0001.md`)
중 어느 것도 이 Observation으로 재검토 근거를 얻지 못했다 — 특히
C-2(Task/Workflow)·C-8(External Data/Acquisition)에 대해 "새 Evidence
계열이 추가되면 재검토"라는 기존 조건이 있었으나, 이번 TradingAgents
관찰은 그 조건을 충족하지 않는다: TradingAgents의 Workflow/Acquisition은
Jarvis OS 쪽 경계 밖(블랙박스 내부)에 머물러, Jarvis가 그 내용을
Kernel Concept으로 흡수할 필요 자체가 생기지 않았기 때문이다.

---

## 8. 최종 판정

**NO NEW OBSERVATION**

- TradingAgents 설치·import·configuration 확인은 **성공**했다.
- 실제 LLM 호출을 포함한 end-to-end 분석 실행은 이 세션 환경 제약
  (API Key 부재, 시장 데이터 호스트 프록시 차단)으로 **BLOCKED**
  됐다 — 이는 TradingAgents 또는 Jarvis OS의 결함이 아니라 이 세션의
  네트워크/Credential 제약이며, Architecture 판단에 필요한 FACT는
  코드 직접 확인으로 충분히 확보했다.
- Investment HQ와의 비교(§4) 및 Q1~Q5(§5) 분석 결과, 현재 Architecture
  Boundary 또는 Common 책임에 영향을 주는 새로운 사실은 확인되지
  않았다.
- **Phase 7 HOLD를 유지한다.** 추가 Architecture 작업(RFC/ADC/ADR,
  새 Phase)을 만들지 않는다.

---

## 9. Open Issues

1. 실제 LLM Key를 가진 로컬 환경에서 AAPL/EFA/PG 세 건을 실행해
   리포트 품질을 직접 확인하는 것은, 이번 Architecture 판정과
   무관한 별도의 (선택적) 후속 검증으로 남는다 — 이 판정을 뒤집을
   가능성은 낮다(Q1~Q4가 실행 결과가 아니라 코드 구조에서 도출됨).
2. TradingAgents는 계속 활발히 개발 중인 저장소(CHANGELOG 다수)이므로,
   이번 관찰은 commit `a33fd4c0` 시점 기준이다 — 이후 구조가 크게
   바뀌면(예: Workflow를 외부에 노출하는 방향으로 리팩터링) 이 문서의
   결론도 재검토 대상이 될 수 있다(트리거는 아직 발생하지 않음).

---

## Architecture Governance Review

- 새로운 Architecture가 추가되었는가 — **아니오**.
- 새로운 Layer/Component/Concept이 추가되었는가 — **아니오**.
- Baseline 문서를 변경했는가 — **아니오**.
- `docs/decisions/adc/ADC.md`를 변경했는가 — **아니오**.
- RFC/ADC/ADR을 생성했는가 — **아니오**.
- `core/`, `hqs/investment/` 코드를 수정했는가 — **아니오**.
- TradingAgents 코드를 수정했는가 — **아니오**.
- TradingAgents를 Jarvis OS dependency로 등록했는가 — **아니오**.
- TradingAgents 코드를 `hqs/`, `core/`로 복사했는가 — **아니오**.

## Self Review

- Phase 7 HOLD를 강제로 종료하거나 Phase 8에 착수했는가 — **아니오**.
- 인위적으로 실패를 발생시키거나 Architecture Trigger를 충족시켰는가
  — **아니오**(BLOCKED 상태를 있는 그대로 기록했다).
- 실제 API Key 값을 어디에도 기록했는가 — **아니오**.
- README/블로그만으로 구현 사실을 확정했는가 — **아니오**(모든 판정은
  clone된 실제 코드 읽기 또는 실제 실행 로그에 근거).
