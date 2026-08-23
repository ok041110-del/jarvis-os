# RFC-0007: AST 기반 Context 자동 추출의 Production Build Capability 통합

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code (DEV-HQ-V2.0-T06~T16 Context Research 종료 시점 요청에 대한 RFC)
**대상**: Build Capability(`backend_agent_code_generation`)에 실제 프로젝트
소스 Context를 자동으로 제공할지 여부 (통합 필요성 판단만, 구현 아님)
**Evidence 범위**: `docs/research/DEV-HQ-V2.0-01-05-WORKFLOW-DOGFOODING-0001.md`
~ `DEV-HQ-V2.0-CONTEXT-EXPOSURE-REPRODUCTION-0001.md` (T06~T16, 11개
Research 문서). 이 RFC 자체는 새로운 실험을 하지 않는다.

> 본 RFC는 Workflow/Agent/Model을 변경하지 않는다. Production Code도
> 변경하지 않는다 — 통합이 필요하다고 판단되더라도 구현은 이 RFC의
> 범위 밖이며, 필요 시 별도 ADC → 실제 구현 단계로 넘긴다.

## 0. 이 RFC가 열린 이유

T06 Dogfooding은 Design→Build 단계에서 반복적인 정보 손실(잘못된 모듈명,
잘못된 시그니처, 잘못된 내부 자료구조 가정)을 발견했다. 원인은
`engine.py`의 `DISALLOWED_TOOLS`가 Engine의 파일시스템 접근을 전면
차단하고, 기존 Project Intelligence(`collect_relevant_context`)가
Planning에만 파일 **경로** 목록을 제공할 뿐 소스 **내용**은 어떤
Capability에도 전달되지 않는다는 구조적 사실에 있다(§3 참고). T09~T16은
이 손실을 Context로 완화할 수 있는지, 완화할 수 있다면 어떤 방식이
안전한지를 실증했다. 이 RFC는 그 결과를 근거로 Production 통합
필요성만 판단한다.

## 1. Evidence 요약 (T06~T16, 새 실험 없이 인용만)

| 항목 | 결론 | 근거 |
|---|---|---|
| Multi-Module AST Automatic Excerpt | Validated — 단일/다중 모듈(최대 6~7개), 얕은 호출 그래프에서 Full Source와 동등한 Build 정확성 | T09~T12 |
| Target File Exposure | 반복 위험 확인 — 대상 파일을 Context에 노출하면 파일 전체 재작성 발생 가능(미노출 0/6, 노출 4/10 ≈ 40%, 확률적) | T13~T16 |
| Context Size Effect(Automatic vs Full Source) | 주요 원인 아님 — 노출 여부를 고정하면 Automatic/Full Source가 항상 같은 방향으로 움직임 | T13, T15 |
| 기존 코드 손상 | 0건 — 재작성이 일어나도 기존 코드는 항상 정확히 보존됨(4개 Task, 16개 이상 조건) | T12~T16 |
| Design 시그니처 제공 효과 | 방향성 있는 개선(표본 각 1개, 일반화 아님) — 실제 함수 시그니처를 Design 입력에 포함하면 존재하지 않는 파일시스템 스캐폴딩 오판이 사라짐 | T15, T16 |
| Context Research 상태 | CLOSED (T16) — 추가 반복이 위 결론을 바꿀 가능성이 낮다고 판단 | T16 |

## 2. 검토 1 — 현재 Build Capability 구조와 AST Context의 결합 지점

현재 흐름(`workflow_0008.py` 등 실제 workflow 파일 기준):

```
design = design_agent_design(issue, requirement)
code = backend_agent_code_generation(design)
```

`backend_agent_code_generation(design: str) -> str`의 시그니처는
그대로 두고, 호출 **직전**에 `design` 문자열에 Context 발췌를
concatenate하는 지점이 유일한 결합 지점이다:

```
context_excerpt = <AST 자동 추출 결과>
code = backend_agent_code_generation(f"{design}\n\n{context_excerpt}")
```

이는 새로운 개념이 아니다 — `workflow_project_intelligence._enrich_issue()`가
이미 동일한 패턴(Context를 문자열로 렌더링해 Planning 입력에
concatenate)으로 Project Intelligence를 Planning에 연결하고 있다.
**Build 단계에 그 패턴을 한 단계 확장하는 것**이 결합 지점의 본질이다.

다만 결정적인 차이가 있다: Planning 단계의 Context는 "무엇에 대한
Context를 모을 것인가"가 Issue(`title`/`description`)로 이미 주어져
있다. Build 단계의 AST 자동 추출은 "어느 모듈의 어느 함수를 시작점으로
폐쇄를 계산할 것인가"가 필요한데, **현재 Design의 출력은 자유
서술형 prose이며 이 정보를 구조적으로 담고 있지 않다.** T09~T16
전체에서 이 시작점(target module/function)은 실험을 설계한 사람(나)이
매번 수동으로 지정했다 — Production에서 이를 자동으로 얻는 방법은
검증된 바 없다(§7 최소 변경 범위, Open Issues 참고).

## 3. 검토 2 — 기존 Contract 변경 필요 여부

**함수 시그니처 수준에서는 변경이 필요 없다.**
`backend_agent_code_generation(design: str) -> str`은 그대로 유지된다
— Context는 Planning과 동일하게 입력 문자열에 얹히는 방식이면 충분하다
(T09~T16 전체가 이 방식으로 실험했다).

**그러나 사실상의 암묵적 Contract(각 Capability 함수가 받는 입력의
"모양")는 새로 생긴다.** 지금까지 Build 입력은 "Design 결과(자연어
서술)"뿐이었다. Context를 얹으면 Build 입력은 "Design 서술 + 실제
프로젝트 코드 발췌"라는 두 부분으로 구성되는 것이 사실상 고정된다.
이는 코드 수준 시그니처 변경은 아니지만, Capability의 실질적 입력
계약이 넓어지는 것이므로 ADC 수준에서 명시적으로 기록해 둘 가치가
있다(Contract Impact 참고).

## 4. 검토 3 — Context 생성 책임의 위치

두 가지 후보가 있다:

1. **`project_intelligence.py` 확장**: 기존 `collect_relevant_context`/
   `build_context_bundle`과 같은 파일에 AST 폐쇄 함수를 추가한다.
   장점: Context 생성 책임이 이미 한 곳에 모여 있다는 기존 관례를
   유지한다. 단점: 현재 `project_intelligence.py`는 "파일 **경로**
   목록만 반환한다"는 성질을 갖고 있다(§0 근거, `CATEGORY_PATHS`
   전체가 경로 문자열만 산출). AST 폐쇄는 파일 **내용**을 읽어
   반환하므로, 같은 모듈 안에 서로 다른 두 가지 반환 형태(경로 vs
   내용)가 섞이게 된다.
2. **별도 신규 모듈**: `build_context.py` 같은 새 파일을 추가해 "내용
   기반 Context"와 "경로 기반 Context"의 책임을 분리한다. 장점:
   기존 Project Intelligence의 성질(경로만 반환)을 보존한다. 단점:
   `hqs/development/IMPLEMENTATION_RULES.md`의 "구현 중 새
   Capability/Agent 추가 금지"에는 저촉되지 않지만(이 함수는 Agent가
   아니라 `project_intelligence.py`류의 helper 모듈이다), 새 모듈
   추가 자체가 "이미 승인된 최소 구조"를 넘어서는 확장이라는 점은
   Governance 검토가 필요하다.

이 RFC는 둘 중 하나를 결정하지 않는다 — 통합이 승인될 경우 ADC
단계에서 판단할 사안으로 남긴다.

## 5. 검토 4 — 실패 시 기존 Workflow에 미치는 영향

AST 폐쇄 계산은 순수 정적 분석(파일 읽기 + `ast.parse`)이며 Engine
호출을 포함하지 않는다. 실패 모드는 두 가지뿐이다:

- 대상 모듈/함수가 존재하지 않거나 파싱 실패 → 예외 발생. 현재
  `workflow_0008.run_pipeline()` 등의 `try/except` 블록이 이미 모든
  예외를 잡아 `_engine_failure_message()`로 통일 처리하는 구조이므로,
  AST 추출 실패도 동일 경로로 흡수된다(추가 예외 처리 로직 불필요 —
  기존 Workflow 구조를 그대로 재사용 가능).
- 폐쇄 계산 자체는 성공하지만 결과가 비어있거나 과도하게 커짐 →
  T11/T12에서 관찰된 "과잉 포함 방지"(불필요한 모듈 배제)는 이미
  검증됐으므로 위험은 낮다고 판단하되, 큰 프로젝트(수십 개 이상
  모듈)에서의 폐쇄 크기 상한은 검증된 바 없다(Open Issues).

**결론**: 실패해도 기존 Workflow의 반환 계약(각 workflow_*.py의 키
집합)은 깨지지 않는다 — 이는 새 Workflow 로직이 아니라 기존
예외 처리 경로에 자연히 편입되기 때문이다.

## 6. 검토 5 — Token / 실행시간 / 유지보수 비용

- **Token/크기**: T09~T16 전체에서 Automatic 발췌는 Full Source
  대비 일관되게 40~60% 크기였다(예: T14 8,676자 vs 21,954자, T15
  4,090자 vs 10,312자). 비용 절감 방향은 뚜렷하다.
- **실행시간**: elapsed 비교는 방향이 일관되지 않았다(T14: Automatic
  17.3s vs Full Source 6.9s — 오히려 역전). Build 단계의 실제 Engine
  응답 시간은 Context 크기보다 다른 요인(응답 내용의 복잡도 등)에
  더 좌우되는 것으로 보이며, 실행시간 단축을 통합의 근거로 삼기는
  어렵다.
- **유지보수 비용**: AST 폐쇄 알고리즘(`ast.parse` + Load-context
  이름 추적 + 상대 import 재귀)은 T11~T16에서 반복 재사용된 약
  90줄 내외의 순수 함수다. 새 의존성 없이 표준 라이브러리(`ast`)만
  사용하므로 유지보수 부담 자체는 낮다. 다만 "어느 함수가 시작점인가"를
  구하는 부분(§2)이 아직 없다 — 이 부분이 실제로 추가될 유지보수
  대상이다.

## 7. 검토 6 — 기존 Context 전달 방식과의 호환성

완전히 호환된다. Planning 단계가 이미 "문자열을 만들어 입력 앞/뒤에
concatenate"하는 방식으로 Context를 전달하고 있고(§2), Build 단계에
같은 방식을 적용하는 것은 새로운 전달 메커니즘을 만드는 것이 아니라
기존 메커니즘을 한 Capability 더 적용하는 것이다. Runtime, Registry,
Event Bus 등 금지된 개념을 전혀 필요로 하지 않는다
(`IMPLEMENTATION_RULES.md` 금지 목록과 충돌 없음).

## 8. 검토 7 — Production 적용 시 최소 변경 범위

만약 통합이 승인된다면(이 RFC는 승인하지 않는다), 최소 변경 범위는:

1. AST 폐쇄 함수 1개 추가(§4의 위치 결정 필요) — 새 Capability/Agent
   아님, 새 Runtime/Registry 아님.
2. 대상 workflow 파일(예: `workflow_0008.py`) 안에서 Build 호출
   직전 한 줄 추가(Context concatenate) — Workflow의 하드코딩된
   순차 호출 패턴 그대로 유지, 조건문/파서로 대체하지 않음.
3. **선행 조건(§2의 핵심 격차)**: "시작점(target module/function)을
   어떻게 자동으로 얻는가"가 먼저 해결되어야 한다. 이것이 해결되지
   않으면 AST 자동 추출은 사람이 매 Task마다 수동으로 대상을 지정해야
   하는 Research 도구로만 남는다 — Production 자동화의 전제 조건이
   아직 없다.
4. Target File Exposure 위험(§1)에 대한 완화 정책: 기존 파일을 수정하는
   실제 Build Task(신규 함수 추가가 아니라 기존 함수 수정)에서는
   대상 파일 노출이 구조적으로 불가피할 수 있다 — 이 경우 파일 전체
   재작성이 발생할 확률(~40%)을 그대로 감수할 것인지, 아니면 Build
   출력을 diff 형태로 강제하는 후처리를 추가할 것인지는 이 RFC가
   결정하지 않는다.

## Decision

**B. CONDITIONAL** — Production 통합의 방향성(Automatic Excerpt가
Full Source를 대체할 수 있다는 정확성 근거, 내용 손상 위험이 사실상
없다는 안전성 근거)은 Evidence로 충분히 뒷받침된다. 그러나 다음 두
선행조건이 해결되지 않은 상태에서 통합을 진행하는 것은 권장하지
않는다:

1. **시작점 식별 문제(§2)**: Design의 자유 서술형 출력에서 AST 폐쇄의
   시작점(target module/function)을 자동으로 얻는 방법이 검증된 적이
   없다. T06~T16 전체는 이 정보를 실험자가 수동으로 제공했다.
2. **Exposure 위험의 완화 정책 부재(§8-4)**: 실제 기존 파일 수정
   Task에서는 노출이 구조적으로 불가피할 수 있고, 그 경우의 재작성
   위험(~40%, 확률적)을 어떻게 다룰지 정책이 없다.

## Scope

- Build Capability(`backend_agent_code_generation`)에 실제 프로젝트
  소스 Context를 자동으로 제공할 필요성 여부의 판단.
- T06~T16 Evidence의 종합과 그로부터 도출 가능한 결합 지점/비용/호환성
  분석.

## Non-Goals

- 이 RFC는 AST 폐쇄 함수나 Context concatenate 로직을 구현하지 않는다.
- 이 RFC는 Workflow, Agent, Model, Frozen Architecture를 변경하지
  않는다.
- 이 RFC는 §2/§8-4의 선행조건을 해결하지 않는다 — 그 해결 방법(Design
  출력 구조화 여부 등)은 별도 RFC/ADC 대상이다.
- 이 RFC는 Context Research(T06~T16)를 재개하거나 새 실험을 추가하지
  않는다.

## Contract Impact

- **함수 시그니처 변경 없음** — `backend_agent_code_generation(design:
  str) -> str`은 그대로 유지 가능.
- **암묵적 입력 계약 확장** — Build 입력이 "Design 서술"에서 "Design
  서술 + 실제 코드 발췌"로 사실상 넓어진다는 것을 ADC 단계에서
  명시적으로 기록해 둘 필요가 있다(§3).
- Design Capability의 출력 계약(자유 서술형 prose)이 그대로면 §2의
  선행조건이 해결되지 않는다 — Design 출력을 구조화할지 여부는 이
  RFC 밖의 판단이다.

## Architecture Impact

- **없음(NONE)** — Runtime/Registry/Engine Gateway/Event Bus 등
  Frozen 금지 목록에 해당하는 어떤 개념도 요구하지 않는다(§7).
  Project Intelligence가 이미 확립한 "Context를 문자열로 렌더링해
  concatenate" 패턴의 확장이다.
- Context 생성 책임의 위치(§4, `project_intelligence.py` 확장 vs
  신규 모듈)는 Architecture 변경이 아니라 Development HQ 내부 구현
  선택이다 — 다만 어느 쪽을 택하든 "Project Intelligence는 경로만
  반환한다"는 현재 관례와의 정합성은 ADC에서 짚어야 한다.

## Implementation Candidate

(이 RFC는 구현하지 않는다 — 승인 시 다음이 구현 후보가 된다)

1. §2의 선행조건 해결: Design 출력에서 대상 모듈/함수를 얻는 최소
   방법(예: Design 프롬프트에 "Target Module/Function" 한 줄을
   요청하는 최소 구조화, 또는 Implementation Specification류의
   8항목 형식 재도입 — RFC-0005 §3 참고)을 별도로 검토.
2. AST 폐쇄 함수를 `project_intelligence.py`에 추가할지 신규 모듈로
   분리할지 ADC로 결정.
3. Target File Exposure 완화 정책(§8-4) 결정.
4. 위 3가지가 결정된 후에만 실제 workflow 파일에 최소 변경(§8) 적용.

## Open Issues

- §2: Design의 자유 서술형 출력에서 대상 모듈/함수를 자동으로 얻는
  방법이 검증되지 않았다 — Production 자동화의 실질적 전제 조건.
- §8-4: 기존 파일을 수정하는 실제 Task에서 Exposure가 구조적으로
  불가피한 경우의 재작성 위험(~40%, 확률적) 완화 정책이 없다.
- 대규모 프로젝트(수십 개 이상 모듈, 순환 참조/동적 import 포함)에서
  AST 폐쇄 알고리즘의 안전성은 T13에서 "Development HQ Scope 안에
  실례가 없어 검증 불가(Untestable)"로 남아 있다 — Scope가 커지면
  재검증이 필요하다.
- RFC-0005(Development HQ ↔ Execution Layer Boundary)는 Development
  HQ의 Implementation Capability가 "Implementation Specification"
  (8항목 텍스트, 코드 아님)만 생성하고 실제 코드 생성/실행은 Execution
  Layer의 책임이라고 기술한다. 그러나 T06~T16에서 실제로 Dogfooding한
  `backend_agent_code_generation`(agents.py)은 실제 코드 문자열을
  직접 생성·반환한다 — 두 기술이 같은 함수를 가리키는지, 서로 다른
  세대의 구현을 가리키는지는 이 RFC의 범위 밖이며 확인되지 않았다.
  이 불일치 자체를 별도로 기록해 둔다.
