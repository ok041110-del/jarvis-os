# EFFICIENCY-AUDIT-0001: Token / Text Efficiency Audit (Phase 9)

**문서 성격**: Audit 문서. **변경을 실행하지 않는다.** 이번 작업에서
어떤 `.md`·`.py` 파일도 수정하지 않았다 — Problem → Evidence →
Recommendation만 기록한다. 실행 여부·순서는 사용자 승인 후 별도
작업으로 넘긴다. `docs/03_adc/ADC.md`, `BASELINE.md`를 포함해 어떤
Architecture/Governance 상태도 변경하지 않는다.

**범위**: 이 Audit은 Kernel Architecture 한정이 아니라 저장소 전체
(`docs/`, `development-hq/`, `core/`, `projects/`, 루트)를 대상으로
한다 — Phase 6~8과 번호는 이어가지만 범위는 더 넓다.

**원칙(사용자 지시 그대로 적용)**: 실제 LLM 입력으로 쓰이는 Prompt
텍스트(`agents.py`의 `instruction = (...)` 문자열)는 일반 문서와
동일하게 압축하지 않는다. 이 Audit은 그런 텍스트를 "압축 대상"이 아니라
"구조적 배치(파일 분리/구성) 대상"으로만 다룬다.

---

## 0. 실행한 검증

```
find . -name "*.md" | wc -l → 484개, 총 54,314줄
find . -name "*.py" | wc -l → 총 11,397줄
python3 -m pyflakes development-hq/mvp/*.py core/execution_layer/**/*.py \
    projects/*/agents.py projects/*/runner.py → 출력 없음(미사용 import/이름 없음)
```

코드는 수정하지 않았으므로 `pytest`는 재실행하지 않았다(회귀 대상
자체가 없음).

---

## 1. MD — 발견

### 1-1. 중복 설명 / 반복 Evidence — RFC ↔ ADC 재진술

| 쌍 | RFC 줄 수 | ADC 줄 수 | 완전 동일 줄(교집합) |
|---|---|---|---|
| RFC-0005 ↔ ADC-0005(Kernel Logical Reference Architecture) | 510 | 661 | 142 |
| RFC-0003 ↔ ADC-0003(Kernel Context Model) | 609 | 629 | (미측정, 유사 패턴 추정) |
| RFC-0004 ↔ ADC-0004(Kernel Public Contract) | 433 | 565 | (미측정) |
| RFC-0006 ↔ ADC-0006(Kernel Context Ownership) | 456 | 592 | (미측정) |

**Problem처럼 보이지만 대부분 아니다**: 이 저장소는 "Evidence만
인용, 재구성·추정 금지"라는 엄격한 원칙을 전 Governance 문서에서
반복 적용한다(`ADC-0008` 등 다수). ADC가 RFC 원문을 **그대로 인용**
하는 것은 이 원칙을 지키는 정상적인 방식이지, 부주의한 중복이 아니다.
그러나 RFC-0004~0007처럼 **ADC가 RFC보다 오히려 더 길어지는 패턴**
(ADC가 RFC를 인용한 뒤 그 위에 추가 판단을 쌓는 구조)은, RFC 본문을
"요약 참조 + 링크"가 아니라 "전문 재수록"에 가깝게 인용하고 있을
가능성이 있다 — 실제로 전문 재수록인지, 필요한 발췌만인지는 이
Audit이 4개 쌍 전부를 정독하지 않아 확정하지 못한다.

**Recommendation**: 새 ADC/RFC 작성 시 "발췌 인용 + 정확한 줄 번호
참조"를 원칙으로 굳히는 것을 권고(이미 부분적으로 관행화됨 — 예:
`docs/01_architecture/BASELINE.md:50` 같은 줄 번호 인용 패턴). **기존
RFC/ADC 문서는 Point-in-time Governance 기록이므로 지금 압축하지
않는다** — §1-4 참조.

### 1-2. 반복 Evidence — Team Definition / Dogfooding Review 3세트

`STOCK-TEAM-DEFINITION-0001.md`·`ETF-TEAM-DEFINITION-0001.md`·
`DIVIDEND-STOCK-TEAM-DEFINITION-0001.md`는 섹션 제목·문장 골격
("## Status", "**Promoted**", "## 명시적 제외 범위", "## 재평가 조건",
"# Architecture/Contract 변경 여부 — **없음.**")이 거의 동일하게
반복된다. 마찬가지로 `*-DOGFOODING-REVIEW-*.md` 6개 문서도 "## N.
무엇이 반복됐는가" 같은 절 구조를 반복한다.

**Problem 여부 판단**: 이것은 낭비가 아니라 **의도된 템플릿 재사용**
이다 — 뒤 문서가 앞 문서의 판단 기준(3회 반복, ADC 채택 기준 등)을
동일하게 적용했음을 독자가 한눈에 대조할 수 있게 하는 것이 목적이며,
이 저장소가 반복적으로 강조해 온 "선례 일관성"(Stock → ETF →
Dividend Stock 순으로 동일 기준 적용)과 직접 부합한다.

**Recommendation**: 압축하지 않는다. 다만 향후 4번째 Team이 생기면,
공통 골격을 매번 재작성하지 말고 **체크리스트 형태의 공용 템플릿**
(신규 파일, 예: `docs/research/_TEAM-DEFINITION-TEMPLATE.md`)을 만들어
"이 문서가 각 항목을 어떻게 채웠는지"만 쓰게 하면 향후 신규 작성
비용은 줄일 수 있다 — **기존 3개 문서를 소급 수정하지 않는 조건**
으로만 권고한다(Point-in-time 문서 원칙, §1-4).

### 1-3. README / HANDOVER / BASELINE 중복

이전 세션(Documentation Drift 작업)에서 이미 이 항목을 다뤄, README는
HANDOVER로 상세를 위임하고 BASELINE 내용을 반복하지 않는 구조로
정리됐다(`README.md`: "Architecture 자체에 대한 설명은 이 문서에서
반복하지 않는다"). 이번 Audit에서 재확인한 결과 **새로운 중복은
발견되지 않았다** — 세 문서가 각자 다른 상세도(README: 안내,
HANDOVER: 현재 상태+다음 단계, BASELINE: 원본 정의)를 유지한다.

### 1-4. Living Document ↔ Point-in-time Evidence 구분

이 저장소는 이미 이 구분을 실제로 지켜 온 전례가 있다:
- `VALIDATION_REPORT.md`(Starter Kit v1.0 시점 스냅샷)는 현재 상태와
  불일치해도 의도적으로 그대로 둔다("point-in-time 문서") — 이전
  세션의 Documentation Drift 작업이 이미 이 원칙을 명시.
- `HANDOVER.md`/`README.md`는 Living Document로 계속 갱신됨.
- `EVIDENCE.md`류(project별)와 `*-TEAM-DEFINITION*.md`/
  `GOVERNANCE-REVIEW-*.md`/`ADC-*.md`/`ADR-*.md`는 전부 Point-in-time
  — 실제로 사후 수정된 사례가 없음(`AGG-DATA-BOUNDARY-REPRODUCTION-0001.md`
  가 새 재현 결과를 추가할 때도 원본 AGG `EVIDENCE.md`를 고치지 않고
  **별도 문서**에 Follow-up을 남긴 것이 바로 이 원칙의 실제 적용
  사례다).

**Problem**: 없음 — 이 구분은 이미 이 저장소의 확립된 관행이다. 이번
Audit이 새로 발견한 위반 사례는 없다.

### 1-5. 불필요한 장문

`docs/architecture/core/`의 RFC/ADC 문서들이 각 400~660줄로 길지만,
이는 "Q0/Q1/Q2 형태의 근거 심사 → Decision → Consequences → Risks →
Self Review"라는 반복 가능한 엄격한 논증 구조 때문이며 장식적 장문이
아니다. `.claude/skills/task-observer/SKILL.md`(446줄)는 이 Audit
범위(Governance/코드) 밖의 Skill 정의 문서로, 별도 검토가 필요하면
후속 작업으로 분리한다(이번 Audit은 검토하지 않음).

**Problem 발견 안 됨.**

---

## 2. PY — 발견

### 2-1. 긴 Docstring

| 파일 | 총 줄 | Docstring 줄 | 비율 |
|---|---|---|---|
| `development-hq/mvp/engine.py` | 87 | 48 | 55% |
| `development-hq/mvp/agents.py` | 166 | 84 | 51% |
| `development-hq/mvp/workflow.py` | 41 | 21 | 51% |
| `core/execution_layer/pipeline.py` | 131 | 58 | 44% |
| `development-hq/mvp/project_intelligence.py` | 233 | 47 | 20% |

**Problem**: `engine.py`의 `call_engine()` docstring이 MVP-0009·
MVP-0028 결함의 발견 경위를 문장 단위로 재서술한다 — 같은 내용이
`docs/01_mvp/MVP-0009-observation.md`·`MVP-0028-observation.md`에 이미
전체 기록으로 존재한다.

**Evidence**: `docs/01_mvp/MVP-0028-observation.md`(114줄, 전체 재현
기록) vs `engine.py` docstring 내 같은 사건 서술(약 15줄, 요약).

**Boundary 판단**: 이것은 순수 낭비가 아니다 — 이 저장소의 comment
원칙("WHY가 non-obvious할 때만 comment")에 부합하는 **정당한 WHY
설명**(왜 `cwd`를 고정했는지, 왜 도구를 막았는지)이다. 다만 서술
분량이 "이유 한 줄"을 넘어 "사건 재현 과정"까지 포함하는 지점은
압축 여지가 있다.

**Recommendation(코드 아님, 문서 구조 제안만)**: 다음 패턴을 향후
신규 코드에 권고한다 — docstring은 "무엇을·왜"만 1~3문장으로 남기고,
"어떻게 재현·검증했는가"는 이미 존재하는 `docs/01_mvp/MVP-XXXX-observation.md`
링크로 대체. **기존 `engine.py`는 지금 수정하지 않는다** — 이 Audit은
실행하지 않으며, 수정 시 그 자체가 동작 중인 Kernel-adjacent 코드
(`development-hq/mvp/`)를 건드리는 것이라 별도 승인이 필요하다.

### 2-2. 반복 Prompt / 반복 Reference Text — Investment Dogfooding 10개 프로젝트

| 비교 | 총 줄(두 파일) | diff 줄 | 실질 중복률 |
|---|---|---|---|
| `dividend-stock-analysis-{jnj,ko}/agents.py` | 185+185 | 6 | **~97%** |
| `dividend-stock-analysis-{ko,pg}/agents.py` | 185+185 | 4 | **~98%** |
| `stock-analysis-{aapl,msft}/agents.py` | 160+151 | 36 | **~77%** |
| `etf-analysis-{qqq,schd}/agents.py` | 190+192 | 90 | **~53%**(역할 재구성으로 차이 큼) |
| `dividend-stock-analysis-{jnj,pg}/runner.py` | 182+184 | 22 | **~88%**(boilerplate) |

10개 `agents.py` 합계 1,734줄, 10개 `runner.py` 합계 1,948줄 —
**대부분이 파일 간 거의 동일한 텍스트**(Fundamental/Technical/
Industry/News/Sentiment 5개 역할 instruction은 Stock 4개 + Dividend
Stock 3개 = 7개 파일에 사실상 동일하게 박제되어 있다).

**Problem 여부 판단 — 중요한 구분**: 이 중복은 "발견"이 아니라 **이미
검토되고 의도적으로 유지하기로 결정된 상태**다.
`docs/research/STOCK-AGENT-SEPARATION-REVIEW-0001.md` §3이 "8개 업무
전부 독립 실행/재사용 가치가 실제로 확인되지 않았다"며 Agent 승격을
보류했고, `docs/research/DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001.md`
§3-1이 같은 논리로 "project-local 코드 복제"를 명시적으로 유지하기로
했다. **이 Audit이 "Reference Text로 파일을 분리해 재사용하라"고
권고하는 것은 그 두 Governance 판단을 사실상 뒤집는 것과 같다** —
실제 코드 공유 필요가 관찰되지 않는 한(재검토 조건, 위 문서들에
명시) 이 중복은 "낭비"가 아니라 "관찰 우선(Observe First, Decide
Later) 원칙의 비용"으로 분류해야 한다.

**Recommendation**: **지금 통합/파일 분리하지 않는다.** 이 발견은
새로운 것이 아니라 기존 Governance 판단(STOCK-AGENT-SEPARATION-REVIEW-0001,
DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001)의 재확인이다. 실제 재사용
필요(예: 4번째 Investment 도메인이 같은 5개 역할을 또 필요로 하는
사례)가 관찰되면, 그때가 그 문서들이 이미 명시한 재검토 시점이다.

### 2-3. Prompt와 Documentation의 혼재

`agents.py`의 각 함수는 "Python docstring(있다면) + `instruction`
변수(실제 Prompt)"를 섞어 쓰지 않는다 — 실제로 확인한 결과, 각
Capability 함수는 별도 docstring 없이 `instruction = (...)`만 갖고,
파일 최상단 모듈 docstring에만 설계 의도(문서화 목적)가 있다. **즉
Prompt와 Documentation이 물리적으로는 이미 분리되어 있다** —
`_run(capability_marker, instruction, data)`이 Prompt 조립 지점이고,
모듈 docstring은 순수 문서다.

**Problem 발견 안 됨.** 이미 분리된 상태.

### 2-4. Prompt를 외부 파일로 분리할 수 있는가

**가능하지만 지금 하지 않기를 권고한다.** 근거:
1. 사용자 지시: "실제 LLM 입력으로 사용되는 Prompt는 압축하지 않는다"
   — 파일 분리 자체는 압축이 아니지만, 분리 후 다시 조합하는 과정에서
   문자열 결합 방식(줄바꿈, 공백)이 미세하게 바뀌면 Prompt가 달라져
   Engine 출력이 달라질 위험이 있다(이 저장소가 이미 실측한 사실 —
   `MVP-0025`: "지시문 한 문장 누락"이 실제 결과 차이를 만든 사례).
2. `engine.py`의 `DISALLOWED_TOOLS`(WebFetch/WebSearch 차단) 때문에
   Prompt 파일을 외부화해도 Engine이 그 파일을 직접 읽지 않는다 — 결국
   Python이 파일을 읽어 문자열로 조립해 넘기는 추가 계층이 생길
   뿐이며, 그 계층 자체가 새로운 버그 표면(인코딩, 줄바꿈, 파일 누락)
   이 된다.
3. 외부화의 이득(가독성)이 현재 각 `agents.py`가 이미 함수 단위로
   Prompt를 명확히 분리해 둔 상태(§2-3)보다 크지 않다.

**Recommendation**: 분리하지 않는다. 대신 §2-2에서 이미 결론 낸 대로,
실제 재사용 필요가 관찰될 때(새 project가 같은 5개 역할을 또
필요로 할 때) **그 시점에** 공용 모듈(예:
`projects/_shared/stock_common_roles.py`) 도입 여부를 Governance
판단으로 검토하는 것이 순서에 맞다 — 지금 "혹시 몰라서" 분리하는
것은 이 저장소가 반복적으로 경계해 온 "이론적으로 필요해 보인다는
이유만으로 만들지 않는다" 원칙과 충돌한다.

### 2-5. Prompt composition으로 중복을 줄일 수 있는가

기술적으로는 가능하다(예: `_DATA_LIMITATION_NOTICE`처럼 프로젝트마다
거의 동일한 상수를 공용 모듈에서 import). 그러나 §2-2·§2-4와 동일한
이유로 **지금 하지 않기를 권고한다** — project-local 독립성이 이
저장소의 명시적 설계 원칙(각 project가 서로 영향받지 않고 독립적으로
관찰됨)이며, 공용 모듈을 만드는 순간 그 모듈에 대한 변경이 여러
project의 Evidence 재현성에 동시에 영향을 미치게 되어(한 곳을
고치면 3~10개 project의 향후 실행 결과가 동시에 달라짐), 이는 지금까지
쌓아 온 "각 project는 독립적으로 재현 가능하다"는 Evidence 성격 자체를
바꾼다.

### 2-6. 사용되지 않는 문자열 / 하드코딩된 긴 텍스트

`pyflakes` 정적 검사(§0)로는 미사용 import/이름이 발견되지 않았다.
수동 확인 결과 `_COMPANY_HEADER`/`_FUND_HEADER` 상수는 전부 실제로
`runner.py`에서 사용되고 있었다. **미사용 문자열/Dead Code는 발견되지
않았다.**

`raw_data.md`(project별, 10개 파일)는 하드코딩된 긴 텍스트지만 이는
코드가 아니라 **Engine에 전달되는 실제 입력 데이터**(WebSearch로
수집한 실제 수치)이므로 "하드코딩된 긴 텍스트" 문제가 아니라 이
project들의 존재 이유 그 자체다 — 압축·이동 대상이 아니다.

---

## 3. 종합 판단

| 범주 | Problem 존재? | 지금 조치? |
|---|---|---|
| RFC↔ADC 재진술 | 부분적(§1-1) — 대부분 정당한 인용 규율 | 아니오, 신규 문서 작성 시 발췌 인용 관행만 강화 |
| Team Definition/Dogfooding Review 반복 구조 | 아니오(의도된 템플릿) | 아니오 |
| README/HANDOVER/BASELINE 중복 | 아니오(이미 정리됨) | 아니오 |
| Living ↔ Point-in-time 혼재 | 아니오(이미 준수 중) | 아니오 |
| 긴 docstring(`engine.py` 등) | 경미(§2-1) | 아니오, 향후 신규 코드에만 적용 |
| Investment Dogfooding 10개 project 간 Prompt/코드 중복 | **아니오 — Governance가 이미 검토·유지 결정** | **아니오** |
| Prompt-Documentation 혼재 | 아니오(이미 분리됨) | 아니오 |
| Prompt 외부 파일 분리 | 해당 없음(권고하지 않음) | 아니오 |
| Prompt composition 공용화 | 해당 없음(권고하지 않음) | 아니오 |
| 미사용 문자열/Dead Code | 발견 안 됨 | 아니오 |

**핵심 결론**: 이 저장소의 "중복"처럼 보이는 것 대부분은 실수가 아니라
**의도된 설계 원칙의 부산물**이다 — project-local 독립성(재사용
최소화), Evidence 인용 규율(재구성 대신 원문 인용), Point-in-time
문서 불변성(사후 수정 금지). 이 세 원칙이 겹치는 지점에서 텍스트
중복이 구조적으로 발생하며, 이를 "효율화"라는 이름으로 제거하면
오히려 이 저장소가 여러 Governance 문서에서 반복적으로 지켜 온
원칙(관찰 우선, 임의 수정 금지, project 독립성)을 위반하게 된다.

**실제로 개선 여지가 있는 유일한 항목**: `engine.py`류의 긴 이력형
docstring(§2-1) — 다만 이것도 지금 수정하면 동작 중인 Kernel-adjacent
코드를 건드리는 것이라, 이 Audit은 "발견"만 하고 실행하지 않는다.

---

## 4. 다음 작업 (사용자 승인 필요, 이번엔 실행하지 않음)

1. (선택) `engine.py`/`agents.py`의 이력형 docstring을 "요약 1~3문장 +
   `docs/01_mvp/MVP-XXXX` 링크"로 줄이는 소규모 리팩터 — 동작 변경
   없음(문자열 리터럴인 `instruction`/`STATELESS_CALL_NOTICE` 등은
   건드리지 않음), 그래도 `development-hq/mvp/`이므로 수정 후
   `pytest development-hq/mvp/tests` 재실행 필수.
2. (선택) 향후 신규 Team Definition 문서 작성 시 쓸 공용 템플릿 신설 —
   기존 3개 문서는 소급 수정하지 않음.
3. (하지 않음) Investment Dogfooding 10개 project의 Prompt/코드 통합 —
   실제 재사용 필요가 관찰되기 전까지 Governance 판단(§2-2 인용)에
   따라 보류.

---

## Architecture/Contract 변경 여부

**없음.** 이 Audit은 어떤 `.md`·`.py` 파일도 수정하지 않았다. 새
Component/RFC/ADC/ADR을 만들지 않았다. `docs/03_adc/ADC.md`를
수정하지 않았다.

## Self Review

- 실제 파일을 수정했는가 — **아니오**. 이 문서(신규) 외 어떤 파일도
  건드리지 않았다.
- Prompt 텍스트를 압축 대상으로 취급했는가 — **아니오**. §2-4·§2-5에서
  명시적으로 압축·분리 모두 보류를 권고했다.
- 기존 Governance 판단(STOCK-AGENT-SEPARATION-REVIEW-0001,
  DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001)과 충돌하는 권고를
  했는가 — **아니오**, 오히려 그 판단들을 근거로 "지금 통합하지
  않는다"를 재확인했다(§2-2).
- Point-in-time 문서(EVIDENCE.md, ADC, ADR, TEAM-DEFINITION)를 압축
  대상으로 제안했는가 — **아니오**.
- 코드를 실행/수정해 회귀 위험을 만들었는가 — **아니오**, `pyflakes`
  정적 검사만 실행했다(파일 변경 없음).
