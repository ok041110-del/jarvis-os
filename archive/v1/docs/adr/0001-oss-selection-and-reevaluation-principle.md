# Jarvis OS — PoC 기술 선정 재검증 및 ADR v1
> PoC_Backlog_and_OSS_Survey_v1.md의 조사 방식을 GitHub 원본 데이터로 재검증. 최종 선정은 ADR 형식으로 기록.

---

## 0. 지난 조사 방식에 대한 정직한 답변

**GitHub와 공식 문서를 직접 대조한 게 아니라, 집계형 비교 블로그를 근거로 후보를 골랐습니다.** Star 수, 라이선스, 최근 유지보수 시점 같은 1차 정보(primary source)는 검증하지 않은 채 "LangGraph가 계층적 오케스트레이션에 강하다"는 정성적 설명만으로 선정 근거를 삼았습니다. 결론 자체(LangGraph, Casbin/OPA, python-statemachine, MCP 레퍼런스 서버)는 이번 재검증에서도 유지됩니다만, 근거는 재확인했습니다. 그리고 그 과정에서 **지난 조사에서 놓쳤던 중요한 사실 하나**가 드러났습니다 (1-1 참고).

---

## 1. GitHub 원본 데이터 기반 비교

### 1-1. Orchestration Engine — Kernel~Organization Layer 실행

| 후보 | Star | License | 유지보수 상태 | 장점 | 단점 | Jarvis OS 적합성 |
|---|---|---|---|---|---|---|
| **LangGraph** (langchain-ai/langgraph) | <cite index="73-1">30,925</cite> (2026년 5월 시점, MIT) | <cite index="77-1">코어 라이브러리(langgraph, langchain-core)는 MIT — 완전 무료</cite> | <cite index="71-1">2026년 7월 기준 langgraph==1.2.9까지 활발히 릴리스</cite> 중 | 계층적 supervisor 패턴, 우리 State Machine을 그래프로 직접 표현 가능 | **아래 참고** | 채택 (단, 조건부) |
| CrewAI | (원본 미검증 — 블로그 인용치만 확보) | MIT (공식 문서 기준) | 활발 | 빠른 프로토타이핑 | 내부 상태 추상화로 계층 경계 검증 어려움 | 기각 |
| Google ADK | (원본 미검증) | Apache 2.0 (공식 문서 기준) | 활발 | 계층적 트리 구조가 개념적으로 유사 | GCP 생태계 종속 | 기각 |

**중요한 재발견 — 지난 조사에서 놓친 라이선싱 함정**: <cite index="77-1">`langgraph`, `langchain-core`, 모델 연동 코드는 MIT로 완전히 자유롭지만, `langgraph dev`나 `langgraph build` 명령으로 실행하는 서버 런타임인 `langgraph-api`는 Elastic License 2.0이며 프로덕션에서 자체 호스팅하려면 상용 라이선스 키가 필요</cite>합니다.

이건 Jarvis OS의 "직접 구현은 마지막 선택"이자 "장기간 자체 호스팅"이라는 전제와 정면으로 부딪힐 수 있는 사실입니다. 지난 조사에서는 이걸 전혀 확인하지 못했습니다.

**조건부 채택**: `langgraph` 코어 라이브러리(그래프 정의·실행 엔진)만 MIT 하에 사용하고, `langgraph-api`(호스팅 서버)는 PoC와 이후 자체 호스팅 계획에서 배제합니다. 우리는 어차피 `apps/poc-runner`라는 우리 자체 Composition Root에서 그래프를 직접 실행할 것이므로 `langgraph-api` 서버가 애초에 필요하지 않습니다 — 이 결정이 Monorepo Structure v1의 설계와도 자연스럽게 맞아떨어집니다.

### 1-2. Lifecycle State Machine

| 후보 | Star | License | 유지보수 상태 | 장점 | 단점 | Jarvis OS 적합성 |
|---|---|---|---|---|---|---|
| **python-statemachine** (fgmacedo/python-statemachine) | <cite index="110-1">1.3k</cite> | <cite index="109-1">MIT</cite> | <cite index="110-1">v3.2.0이 2026년 6월 17일 릴리스</cite> — 최근 활발 | <cite index="52-1">Guard/Validator로 조건부 전이, 상태 다이어그램 자동 생성</cite> | 대형 프레임워크 대비 커뮤니티 규모 작음 | 채택 |
| pytransitions/transitions | (원본 미검증) | MIT (공식 문서 기준) | 활발 | 가볍고 검증됨 | Guard 표현력이 상대적으로 약함 | 기각 |

### 1-3. Policy Engine — Permission Tier

| 후보 | Star | License | 유지보수 상태 | 장점 | 단점 | Jarvis OS 적합성 |
|---|---|---|---|---|---|---|
| **Casbin (pycasbin)** | <cite index="89-1">1.7k</cite> | <cite index="80-1">Apache 2.0</cite> | <cite index="84-1">7년 전 생성, 최근 커밋은 2주 전</cite> — Apache 재단 프로젝트(`apache/casbin-pycasbin`)로 편입되어 거버넌스 안정적 | 별도 서버 불필요, 임베드형 | 여러 서비스 간 정책 중앙화는 약함 | PoC 채택 |
| **Open Policy Agent** | <cite index="99-1">10.9k</cite> | <cite index="92-1">Apache 2.0</cite> | <cite index="98-1">2026년 6월까지 릴리스 지속</cite>, <cite index="91-1">CNCF 졸업(graduated) 프로젝트</cite> | 앱 코드와 정책 완전 분리, 우리 PDP/PEP 모델과 용어 일치 | 별도 데몬 필요, Rego 학습 곡선 | v1.1 전환 목표로 채택 |
| Cerbos | (원본 미검증) | Apache 2.0 (공식 문서 기준) | 활발 | OPA보다 단순 | 여전히 별도 서비스 필요 | 기각 (OPA와 유사 포지션, CNCF 소속 여부에서 OPA 우위로 판단) |

### 1-4. MCP Connector

| 후보 | License | 유지보수 상태 | 장점 | 단점 | Jarvis OS 적합성 |
|---|---|---|---|---|---|
| **modelcontextprotocol/servers (filesystem, fetch)** | <cite index="120-1">MIT</cite> | <cite index="118-1">Anthropic 공식 조직에서 유지, 2026년 5월 기준 최신 갱신</cite> | 공식 레퍼런스, 문서화 잘 됨, <cite index="120-1">디렉토리 접근 제어 등 보안 기능 내장</cite> | 기능이 최소한(딱 그 정도가 이번 PoC 목적엔 장점) | 채택 |

### 1-5. Capability Registry

**여전히 후보가 없습니다.** 지난 조사와 결론이 같습니다 — GitHub에서 "조직 계층 간 능력 기반 라우팅"에 해당하는 프레임워크를 다시 찾아봤지만, 이건 애초에 검색으로 나올 성격의 문제가 아닙니다(우리 도메인 모델 그 자체이기 때문). 이번엔 최소한 "검색해서 없었다"가 아니라 "왜 검색 대상이 아닌지"를 분명히 해뒀다는 점이 이전과의 차이입니다.

---

## 2. ADR 기록

### ADR-001: Orchestration Engine으로 LangGraph 코어 채택 (Server 제외)

```
날짜: 2026-08-02
상태: Accepted

배경 (Context)
- PoC Must #1, #3, #4, #5, #11 (Kernel Routing, 2-HQ, HQ간 Routing, 계층 경계 준수)를
  가장 적은 코드로 검증할 오케스트레이션 엔진이 필요.
- 초기 조사는 집계 블로그 근거였고, GitHub 원본 재검증 과정에서 langgraph-api가
  Elastic License 2.0이라는 사실을 새로 확인함.

결정 (Decision)
- langgraph (코어 그래프 엔진, MIT)만 채택.
- langgraph-api(호스팅 서버, Elastic License 2.0)는 PoC 및 향후 자체 호스팅
  계획 어디에도 포함하지 않는다. 그래프 실행은 apps/poc-runner가 직접 담당.

근거 (Rationale)
- 우리 State Machine·Kernel 5단계를 그래프의 노드/엣지로 거의 그대로 옮길 수 있음.
- 이미 Composition Root(apps/poc-runner)가 실행 주체이므로 별도 서버가 불필요.

기각된 대안 (Rejected Alternatives)
- CrewAI: 내부 상태 추상화로 계층 경계(Must #11) 검증이 어려움
- Google ADK: 특정 클라우드 종속

영향 범위 (Impact)
- adapters/workflow-langgraph의 pyproject.toml 의존성을 langgraph 코어로 한정하고
  langgraph-api/langgraph-cli의 프로덕션 실행 경로는 사용하지 않음을 코드 주석으로 명시
```

### ADR-002: Lifecycle State Machine으로 python-statemachine 채택

```
날짜: 2026-08-02
상태: Accepted

배경
- PoC Must #7, #8 (HQ Idle/Running/Sleeping 전이, Team Ephemeral 소멸)을
  Guard 기반으로 정확히 표현할 라이브러리가 필요.

결정
- python-statemachine(MIT) 채택.

근거
- Guard로 "Sleeping은 자동 wake 가능, Disabled는 사람만 wake 가능" 규칙을
  코드 수준에서 강제 가능.
- 다이어그램 자동 생성으로 설계 문서(Core Design Principles v1)와 구현을 육안 대조 가능.
- 2026년 6월 최신 릴리스로 유지보수 활발함을 확인.

기각된 대안
- pytransitions/transitions: 가볍지만 Guard 표현력이 상대적으로 약함

영향 범위
- adapters/lifecycle-statemachine
```

### ADR-003: Policy Engine — PoC는 Casbin, v1.1은 OPA 전환을 전제로 설계

```
날짜: 2026-08-02
상태: Accepted

배경
- PoC Must #6은 Permission Tier만 검증하면 되므로 최소 인프라가 유리하나,
  Policy Engine v1에서 정의한 PDP/PEP 모델은 Budget/Priority Tier와
  다중 PEP 환경까지 고려해야 함.

결정
- PoC 범위: Casbin(Apache 2.0) 임베드로 허용/거부만 구현.
- v1.1 이후(Budget/Priority Tier, 다중 PEP 도입 시점): OPA(Apache 2.0, CNCF 졸업)로 전환.
- packages/core의 IPolicyEngine Port는 지금부터 어느 구현체로도 교체 가능하도록
  설계(이미 Monorepo Structure v1에 반영됨).

근거
- Casbin은 별도 서버 없이 즉시 PoC 검증 가능 — 지금 필요한 건 이것뿐.
- OPA는 CNCF 졸업 프로젝트로 거버넌스가 검증되어 있고, "정책과 코드의 완전한 분리"라는
  설계 자체가 우리 PDP 개념과 이름까지 일치함 — 여러 계층(HQ/Division/Team)이
  분산된 PEP로 동작해야 하는 시점에 구조적으로 맞음.

기각된 대안
- Cerbos: OPA와 유사한 포지션이나 CNCF 소속 여부에서 상대적으로 신뢰도 낮게 판단
- 처음부터 OPA로 시작: PoC 규모에서 별도 데몬 운영은 과도한 인프라

영향 범위
- adapters/policy-casbin (PoC), adapters/policy-opa (v1.1에서 신설 예정)
- Kernel 및 HQ/Division/Team 코드는 IPolicyEngine Port만 참조하므로 변경 없음
```

### ADR-004: MCP Connector로 공식 레퍼런스 서버(filesystem, fetch) 채택

```
날짜: 2026-08-02
상태: Accepted

배경
- PoC Must #9는 Agent→MCP 통신 경로 자체의 검증이 목적이며, 도구 기능의
  품질은 검증 대상이 아님(Won't 확정 사항).

결정
- modelcontextprotocol/servers 저장소의 filesystem, fetch 서버(둘 다 MIT) 채택.

근거
- Anthropic 공식 조직이 유지보수하여 도구 자체의 안정성 문제로 PoC 일정이
  지연될 위험이 가장 낮음.
- 기능 품질이 목적이 아니므로 가장 단순하고 검증된 것을 고르는 게 원칙에 맞음.

기각된 대안
- 서드파티 커뮤니티 서버 전반: 유지보수 상태 개별 검증에 시간이 들고,
  이번 PoC 목적(경로 검증)에는 공식 서버로 충분함

영향 범위
- adapters/connector-mcp
```

---

## 2-1. Re-evaluation Principle (모든 ADR에 공통 적용)

**기각(Rejected)은 영구적 결정이 아니라 "현재 시점 기준" 결정입니다.** 위 ADR-001~004에서 기각된 CrewAI, Google ADK, pytransitions/transitions, Cerbos 및 향후 모든 ADR의 기각 후보는, 아래 조건 중 하나라도 발생하면 재평가 대상이 됩니다.

- **Architecture 변경**: v1.1 이후 아키텍처가 바뀌어 기각 사유(예: "계층 경계 검증이 어려움")가 더 이상 유효하지 않게 될 때
- **PoC 실패**: 현재 채택한 후보가 PoC에서 예상과 다르게 동작할 때
- **성능 문제**: 채택한 후보가 실제 운용 규모에서 병목이 될 때
- **라이선스 변경**: 채택 후보든 기각 후보든 라이선스 조건이 바뀔 때 (ADR-001의 langgraph-api 사례처럼, 이런 변화를 놓치지 않는 것 자체가 이번에 확인된 리스크임)
- **프로젝트 성숙도 변화**: 기각 당시엔 검증이 부족했던 프로젝트가 이후 충분히 성숙할 때

재평가는 새 ADR로 기록하며, 기존 ADR을 삭제하지 않고 "Superseded by ADR-XXX" 상태로 남깁니다 — 왜 그때는 그 결정이 맞았는지의 기록 자체가 자산입니다.

---

## 3. Capability Registry에 대한 별도 판단 (ADR 대상 아님)

Capability Registry는 채택할 오픈소스가 없다는 결론이므로 ADR 대상이 아닙니다. 다만 이걸 "조사 누락"이 아니라 "설계상 당연한 결과"로 문서화해두는 것 자체가, 향후 누군가 "왜 Capability Registry는 오픈소스를 안 썼냐"고 물었을 때 재현 가능한 근거가 됩니다 — 이 역시 Build보다 Integrate 원칙의 반대편(정말 Build해야 하는 지점을 명시적으로 남기는 것)입니다.

---

## 4. 다음 단계

ADR 4건이 확정되었으니, Monorepo Structure v1의 adapters/ 스켈레톤에 실제 의존성을 반영하고 PoC 구현에 들어갈 수 있습니다. 특히 ADR-001의 langgraph-api 배제 결정을 `adapters/workflow-langgraph/pyproject.toml`과 README에 명시적으로 반영하는 게 먼저입니다. 이대로 구현에 들어갈까요?
