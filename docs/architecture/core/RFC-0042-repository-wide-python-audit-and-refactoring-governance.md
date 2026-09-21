# RFC-0042: Repository-wide Python Audit & Refactoring — Governance Boundary (구현 아님)

**Status**: Proposed (검토 대상, 결정 아님 — 확정은 `ADC-0045`/`ADR-0028`가 담당)
**Author**: Claude Code(사용자 요청에 따른 Governance 설계)
**대상**: Repository 전체 `*.py`(`hqs/`, `mvp/`, `tests/`, `projects/`
포함, `*.md`는 제외). 신규 Lifecycle/권한 경계/Wave 정책을
설명한다 — 이 RFC 자체는 어떤 `*.py`도 수정/삭제/이동하지 않는다.

**요청 배경**: 사용자가 "Repository 전체 Python 코드를 Ponytail
원칙 + Senior Developer 수준의 가시성/의미 전달/간결성 기준으로
감사하고 단계적으로 리팩토링할 수 있는 Governance를 먼저 확립하라"고
요청했다. 이 RFC는 그 Governance의 **경계와 절차**만 정의한다 —
실제 Audit 실행, 실제 코드 수정은 이 RFC/후속 ADC/ADR의 범위 밖이며
별도 Implementation 단계(§9)에서만 착수한다.

---

## 1. Identity & Status

| Field | Value |
|---|---|
| Document ID | RFC-0042 |
| Title | Repository-wide Python Audit & Refactoring — Governance Boundary (구현 아님) |
| Type | RFC |
| Target Domain | Repository 전체 — Python Audit/Refactoring Governance Lifecycle 신설(구현 아님) |
| Status | Proposed (검토 대상, 결정 아님 — 확정은 ADC-0045/ADR-0028가 담당) |
| Decision Group | Repository-wide Python Audit Governance(RFC-0042 → ADC-0045 → ADR-0028) |
| Parent Documents | docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md, docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md(Ponytail 원 정의, 재론 아님) |
| Related Documents | 아래 「Related Documents」 참조 |
| Evidence References | hqs/development/IMPLEMENTATION_RULES.md, docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md |
| Source Path | docs/architecture/core/RFC-0042-repository-wide-python-audit-and-refactoring-governance.md |
| Last Verified | 정보 없음 — 원문에 정의되지 않음 |
| Verification Confidence | 정보 없음 — 원문에 정의되지 않음 |

## 2. Context & Problem

### 0. 기존 Governance 조사 결과(사용자 지시 — 먼저 조사)

- 현재 Kernel/Architecture 연구 트랙은 `docs/architecture/core/`에
  `RFC-0001~0041` → `ADC-0001~0044`(단, `docs/governance/adc/`의
  `ADC-0001~0009`는 별도 Development HQ Governance v1/v2 트랙이며
  번호 체계가 다름 — 혼동하지 않는다) → `ADR-0001~0027` 순서로
  누적돼 있다. 이 RFC는 이 트랙의 다음 번호(`RFC-0042`)를 그대로
  이어 쓴다 — 새 디렉터리·새 번호 체계·새 문서 종류를 만들지 않는다.
- RFC Status 어휘는 `Proposed`(검토 중) → `Resolved — ADC-xxxx로
  종결`(ADC 완료 후) 두 단계만 관찰됐다 — 이 RFC도 동일 어휘를
  재사용한다.
- ADC Status 어휘는 `Decided — ADR Required`(ADR로 이어짐),
  `Decided — Partial`, `Decided — Strategy Framing Accepted` 등
  "Decided — X" 형태만 관찰됐다 — 새 어휘를 만들지 않는다.
- ADR Status는 저장소 전체에서 예외 없이 `Accepted`(필요 시
  `Accepted (Scoped)` 수식어) 계열뿐이다(`ADR-0025`~`ADR-0027`이
  이미 이 사실을 명시적으로 재확인함) — 이 RFC의 후속 ADR도 동일
  어휘를 재사용한다.
- `ADR` 문서는 표 헤더(ID/상태/Context/관련 RFC/관련 ADC/관련 ADR/
  관련 Evidence/Governance Status 확인) + 번호 섹션 구조를 쓴다 —
  이 RFC의 후속 ADR도 동일 구조를 재사용한다.
- **"Ponytail" 기존 정의 재확인(중요)**: `RFC-0037` →
  `ADC-0040`(현재 **NOT DETERMINED — Real Engine Evidence
  Required**, 아직 Open)이 Stage 04 Multi-Agent Code Generation
  맥락에서 "Ponytail Supervisor"를 정의했다. 그 문서의 `ponytail_policy.py`
  guardrail 4종(Target 불변/새 import 금지/Scope 불변/이미 통과한
  후보 무수정)은 이미 코드로 구현·테스트됐고, 이 RFC가 §3에서
  정의하는 Ponytail 권한 경계는 **그 guardrail과 정확히 동일한
  원칙을 재사용**한다. 단, 적용 대상이 다르다 — `ADC-0040`의
  Ponytail은 "Stage 04 Code Generation 후보를 선택/수정하는
  Multi-Agent 구성원"이고, 이 RFC의 Ponytail은 "Repository 전체
  기존 코드를 지역적으로 단순화하는 감사/리팩토링 역할"이다. **이
  RFC는 `ADC-0040`을 재론하지도, 대신 결정하지도 않는다** — Stage 04
  Multi-Agent Production 채택 여부는 여전히 Open이며, 이 RFC가
  정의하는 "Ponytail 권한 경계"라는 이름/원칙만 재사용할 뿐 별개의
  적용이다.
- `hqs/development/IMPLEMENTATION_RULES.md`의 Comment/Docstring
  정책(최대 2줄, WHY 중심, Self-documenting Code First)은 CLAUDE.md
  Code Documentation 절과 동일 원칙이며 이미 확정 상태다 — 이 RFC는
  이 정책을 새로 만들지 않고 그대로 인용·적용한다(§5).
- 기존 Validation 체계(`py_compile`/`pytest`/각 Stage·Team의
  `test_*.py`, `docs/architecture/core/EVIDENCE-*` 관례)를 조사한
  결과 별도의 새 정적분석 도구는 저장소에 없다 — 이 RFC는 새
  Validator 신설을 최소화하고 기존 체계를 우선 재사용한다(§6).

### 1. 목적과 비목표

**목적**: Repository 전체 `*.py`를 대상으로, Ponytail 원칙
(YAGNI/stdlib 우선/최소 복잡성/명시성) + Senior Developer 수준의
가독성 기준으로 감사(Audit)하고, 승인된 범위 내에서만 단계적으로
리팩토링(Refactoring)할 수 있는 **Governance 절차**를 확립한다.

**비목표(이 RFC가 하지 않는 것)**:

- 실제 `*.py` 파일을 수정/삭제/이동하지 않는다.
- 현재 Architecture/Public Contract/Stage·Team Responsibility를
  변경하지 않는다.
- `*.md`를 Audit/Refactoring 대상에 포함하지 않는다.
- 새로운 Capability/Layer/Component를 추가하지 않는다.
- `ADC-0040`(Stage 04 Multi-Agent) 등 이미 Open된 별도 Governance
  판단을 대신하거나 재론하지 않는다.

### 2. Audit 범위

- **포함**: `hqs/`, `mvp/`(hqs 하위 포함), `tests/`, `projects/`
  하위 모든 `*.py`, 그리고 위 네 경로 밖에 존재하는 기타 `*.py`
  (예: 저장소 루트 `core/`, `archive/v1/` 등 — 단, `archive/v1/`는
  `ADR-0006`이 Migration 대상에서 명시적으로 제외한 Historical
  Evidence이므로 §7의 KEEP/GOVERNANCE REQUIRED 분류 시 이 사실을
  최우선으로 반영한다). Test code도 Audit 대상에 **포함**한다(사용자
  지시 명시).
- **제외**: `*.md`(사용자 지시 명시, RFC/ADC/ADR 자체는 이 RFC가
  Governance 문서로서 작성하는 것이므로 예외가 아니라 애초에
  Audit 대상 파일 유형이 아니다). `__pycache__`/`.pyc` 등 미추적
  빌드 산출물(대상 자체가 아님, 선행
  `STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`
  §7과 동일 결론).
- **Historical/Governance-cited 파일과의 관계**: `docs/research/
  ARCHIVE-CLEANUP-REVALIDATION-0001.md`가 이미 확인한 대로,
  `projects/`의 다수 `*.py`는 RFC/ADC/ADR/Freeze 문서가 실제로
  인용하는 Historical Evidence다. 이 RFC의 Audit은 그런 파일도
  **읽고 분류는 하되**, §3이 정의하는 Ponytail 권한으로는 수정하지
  않는다 — Historical Evidence 파일에 대한 어떤 수정도 최소
  `GOVERNANCE REQUIRED`로 분류한다(§7).

## 3. Analysis & Decision

### 3. Lifecycle — Audit과 Refactoring 분리

```
Inventory
   ↓
Deterministic Audit
   ↓
Semantic/Ponytail Review
   ↓
Candidate Classification
   ↓
Refactoring Wave
   ↓
Validation
   ↓
Evidence
```

#### 3.1 Inventory

대상 범위(§2) 전체 `*.py` 파일 목록을 기계적으로 수집한다(파일
경로, LOC, 마지막 커밋, 소속 프로젝트/HQ). 판단을 포함하지 않는다 —
`docs/governance/observations/README.md`의 "OBS는 사실만 기록한다"
원칙과 동일한 성격의 단계다.

#### 3.2 Deterministic Audit

Import graph, syntax/AST 파싱, 순환 참조, 미사용 import, 함수/파일
길이, 중복 코드 패턴 등 **도구로 기계적으로 확인 가능한 사실**만
수집한다. 품질 판단(Simplicity/Readability)을 포함하지 않는다.

#### 3.3 Semantic/Ponytail Review

Deterministic Audit 결과 위에서, RFC 본문 §A~E(사용자 지시 원문,
아래 §4에 재정리)의 기준으로 **의미 판단**을 수행한다 — 여기서만
"이 코드가 의도를 잘 드러내는가"를 사람 또는 Ponytail 역할이
판정한다.

#### 3.4 Candidate Classification

§7의 분류표(KEEP/COMMENT·DOCSTRING CLEANUP/SIMPLIFY/REFACTOR/
POSSIBLE BUG/ARCHITECTURE·CONTRACT RISK/GOVERNANCE REQUIRED)로
각 파일·각 발견 사항을 분류한다.

#### 3.5 Refactoring Wave

Candidate Classification에서 `SIMPLIFY`/`REFACTOR`/`COMMENT·
DOCSTRING CLEANUP`로 분류되고 §3 Ponytail 권한 범위 안에 있는
항목만, §8의 Wave 단위로 실제 코드를 수정한다. `POSSIBLE BUG`/
`ARCHITECTURE·CONTRACT RISK`/`GOVERNANCE REQUIRED`는 이 단계에서
수정하지 않는다(§5 Ponytail 권한 경계 밖).

#### 3.6 Validation

§9가 정의하는 검증(syntax/compile, 회귀 테스트, import 무결성,
Public Contract 회귀, AST-level sanity, dependency 무결성, scope
compliance, comment/docstring policy, readability review)을
Wave 단위로 수행한다.

#### 3.7 Evidence

각 Wave 완료 시 `docs/research/`에 Evidence 문서를 남긴다(기존
저장소 관례 — `EVIDENCE-*`/`*-REVALIDATION-*`/`*-REVIEW-*` 명명
패턴 재사용, 새 명명 규칙을 만들지 않는다).

이 Lifecycle은 기존 Governance 체계(RFC → ADC → ADR, MVP →
Observation → RFC)와 병렬로 존재하는 **Python 코드 품질 전용
하위 절차**다 — 기존 체계를 대체하지 않는다. Lifecycle 도중
Architecture/Contract 판단이 필요해지면 즉시 이 Lifecycle을
멈추고 별도 RFC를 연다(§5 GOVERNANCE REQUIRED 분류가 이 이탈구를
공식화한다).

### 4. 핵심 목표(사용자 지시 원문 재정리 — 이 RFC가 새로 만들지 않음)

Audit/Refactoring이 따라야 할 기준은 사용자 지시 A~E를 그대로
채택한다(요약, 원문은 이 RFC의 근거 요청 문서 자체):

- **A. Simplicity** — 불필요한 abstraction/중복/과도한 계층 제거,
  YAGNI, 불필요한 dependency 제거.
- **B. Semantic Visibility** — 함수명/변수명/제어 흐름만으로 의도가
  드러나야 한다. 상위 함수는 흐름을, 하위 함수는 의미 단위를
  드러낸다. 단순화를 위해 가독성을 희생하지 않는다.
- **C. Senior Developer Style** — 함수 분리 자체가 목표가 아니다.
  의미 단위가 명확해질 때만 분리한다. 줄 수 최소화가 목표가
  아니다. 이름이 구조/역할을 설명해야 한다. 불필요한 clever
  code/압축 표현/과도한 one-liner를 지양한다.
- **D. Ponytail** — YAGNI, stdlib/native 우선, 최소 복잡성,
  명시적이고 읽기 쉬운 코드. correctness/security/trust boundary는
  단순화 대상이 아니다.
- **E. Comment/Docstring** — Self-documenting Code First, 코드가
  설명하는 내용을 반복하지 않는다, WHY 중심, 외부 제약/비자명한
  trade-off/의도적 설계 이유는 보존한다, 최대 2줄(기존 확정
  정책 재사용), `ponytail: <이유>` 형태의 marker를 debt/의도적
  예외 표시로 허용한다, comment cleanup을 이유로 코드 로직을
  바꾸지 않는다.

### 5. Ponytail 권한 경계

`ADC-0040`의 `ponytail_policy.py` guardrail과 동일한 원칙을
Repository-wide Audit 맥락으로 재사용한다.

**Ponytail이 할 수 있는 것(Local, Governance 불필요)**:

- Local simplification(같은 파일/같은 함수 범위 내 단순화)
- Readability improvement(이름 개선, 제어 흐름 정리)
- Unnecessary abstraction 제거(호출부가 1곳뿐인 wrapper 제거 등)
- Comment/docstring cleanup(§4 E 기준)
- Obvious duplication 축소(같은 파일/같은 모듈 내 명백한 중복)
- Naming/control-flow improvement

**별도 Governance(RFC → ADC → ADR)가 필요한 것**:

- Architecture 변경
- Stage/Team responsibility 변경
- Public Contract 변경
- Output schema 변경
- Dependency boundary 변경(새 외부 패키지 도입, HQ 간 경계 이동 등)
- 새로운 capability 추가
- Cross-HQ architectural change

**판단 불명확 시 원칙**: 어떤 변경이 위 두 목록 중 어디에 속하는지
불명확하면, `CLAUDE.md` Frozen Architecture 원칙("Architecture
변경이 필요하면 RFC → ADC → ADR")을 그대로 적용해 **기본값은
Governance 필요 쪽**으로 분류한다(§7의 `GOVERNANCE REQUIRED`).
Ponytail은 스스로 이 경계를 넓히지 못한다 — 경계 자체를 바꾸려면
이 RFC를 개정하는 새 RFC가 필요하다.

### 6. Candidate Classification 분류 체계

기존 Governance 체계(KEEP/DEFER 등, `STAGE-TO-TEAM-MIGRATION-
ARCHIVE-CLEANUP-INVESTIGATION-0001.md`가 쓴 A~E 분류)와 이름이
겹치지 않도록, Python Audit 전용 7개 분류를 신설한다. 기존 체계와
충돌하지 않는다 — Archive Cleanup의 A~E는 "파일의 존재/보존
여부"를, 이 7개는 "파일 내용의 개선 필요 여부"를 분류하며 서로
직교한다.

| 분류 | 의미 | 처리 |
|---|---|---|
| `KEEP` | 이미 §4 기준을 충족 | Wave에서 수정하지 않음 |
| `COMMENT/DOCSTRING CLEANUP` | 코드는 적절하나 주석/docstring이 §4-E 위반(2줄 초과, WHAT 반복, 사문화된 TODO 등) | Ponytail 권한 내(§5), 코드 로직 무변경 |
| `SIMPLIFY` | §4-A/D 위반(불필요한 abstraction/중복/과도한 계층) — Contract·동작 무변경 | Ponytail 권한 내(§5) |
| `REFACTOR` | §4-B/C 위반(가독성/의미 전달 부족) — 이름/제어 흐름/함수 분리 개선, 동작 무변경 | Ponytail 권한 내(§5), 단 Wave당 변경 범위 제한(§8) |
| `POSSIBLE BUG` | Audit 중 발견된 정확성 의심 사항(Refactoring 목적이 아님) | Ponytail이 수정하지 않는다 — 별도 Evidence 문서로 보고만 하고, 실제 수정은 이 RFC 범위 밖의 별도 결정(사용자 승인 또는 별도 Bugfix 절차)을 거친다 |
| `ARCHITECTURE/CONTRACT RISK` | 수정하면 Public Contract/Architecture Boundary에 영향 가능 | Ponytail 권한 밖 — 자동으로 `GOVERNANCE REQUIRED`로 승격 |
| `GOVERNANCE REQUIRED` | §5 "별도 Governance 필요" 목록에 해당하거나 판단 불명확 | Ponytail이 수정하지 않는다 — 신규 RFC 개설 여부를 별도로 판단 |

## 4. Evidence & Validation

### 7. 대규모 변경 안전성 — Wave 정책

Repository 전체를 한 번에 수정하지 않는다. 각 Wave는 다음을
반드시 포함한다:

```
Audit(§3.2~3.4 결과 중 이번 Wave 대상만)
   ↓
Candidate selection(범위를 명시적으로 좁힘 — 예: 특정 HQ/특정
디렉터리/특정 분류 1~2개)
   ↓
Implementation(선택된 Candidate만, §5 Ponytail 권한 내에서만)
   ↓
Focused validation(이번 Wave가 건드린 파일/모듈에 한정)
   ↓
Full regression(Repository 전체 기존 테스트 재실행)
   ↓
Evidence(`docs/research/`에 Wave별 기록)
   ↓
다음 Wave
```

**Wave 크기 제한 원칙**: 한 Wave에서 동시에 건드리는 디렉터리/HQ는
최소화한다(권장: 1개 HQ 또는 1개 최상위 디렉터리 단위). 한 Wave
안에서 `SIMPLIFY`/`REFACTOR`/`COMMENT·DOCSTRING CLEANUP`을
섞어야 한다면, 같은 파일에 대한 변경만 한 커밋으로 묶고 서로 다른
파일의 서로 다른 분류는 리뷰 가능한 단위로 나눈다. 이 원칙의
구체적 파일 수/LOC 상한은 이 RFC가 고정하지 않는다 — 각 Wave
착수 시점에 Wave별 Evidence 문서 서두에서 그 Wave의 범위를 명시
선언하고, 그 선언을 벗어나면 그 Wave를 종료하고 새 Wave로
분리한다(Wave 범위 확대 자체를 금지하는 절차적 장치).

### 8. Validation 정책

기존 체계를 우선 재사용한다(사용자 지시 §5). 새 Validator는
정말 필요한 경우에만 제안하며, 이 RFC는 다음 항목 전부를 **기존
도구/기존 테스트 스위트로 커버 가능**하다고 확인한다:

| 항목 | 재사용 대상 |
|---|---|
| Python syntax/compile | `python3 -m py_compile` / `compileall`(선행 Archive Cleanup 재검증에서 이미 사용한 방식 재사용) |
| Unit/Integration 회귀 | 각 HQ/Stage/Team/`mvp/tests/`/`projects/*/tests/`의 기존 `pytest` 스위트(`HANDOVER.md`가 기록한 테스트 기준선과 대조) |
| Import 무결성 | 대상 모듈 직접 import 시도 + 기존 sibling-import 체인(`STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md` §9가 이미 식별한 체인) 재확인 |
| Public Contract 회귀 | 각 Stage/Team README·`CAPABILITIES.md`가 명시한 Contract와 실제 반환값 대조(기존 관례, 새 스키마 도입 없음) |
| AST-level sanity | `ast.parse` 기반 구조 확인(Stage 04 `deterministic_checks.py`가 이미 증명한 접근 방식 재사용 — 이 RFC는 그 모듈을 새로 만들지 않고, 필요하면 동일 원칙의 경량 스크립트만 Wave Evidence에 첨부한다) |
| Dependency 무결성 | `grep`/AST import 추출로 이 저장소 특유의 `sys.path`/`importlib` sibling-import 관계 재확인(신규 도구 불필요) |
| Scope compliance | 이 RFC §2/§5가 정의한 범위·권한을 벗어난 변경이 있는지 diff 검토(도구가 아니라 절차 — Wave Evidence에 "범위 밖 변경 없음"을 명시) |
| Comment/docstring policy | `IMPLEMENTATION_RULES.md`/CLAUDE.md 정책 대조(최대 2줄, WHY 중심) — 필요 시 Stage 04 `check_comment_docstring_policy`와 동일 원칙의 경량 검사만 재사용, 새 정책을 만들지 않는다 |
| Readability/Simplicity review | Semantic/Ponytail Review 단계(§3.3) 자체가 이 역할 — 별도 자동화 도구를 강제하지 않는다 |

**신규 Validator 제안(최소)**: 위 표의 "AST-level sanity"/"comment/
docstring policy" 두 항목은 기존에 Stage 04 전용으로만 구현돼
있어(`architecture_validation/deterministic_checks.py`), Repository
전체로 일반화하려면 그 로직을 재사용하는 경량 스크립트가 필요할 수
있다 — 이 RFC는 그 스크립트의 **필요성만 인정**하고 실제 작성은
하지 않는다(구현 단계, §9 Implementation Freedom 원칙에 따라 실제
Wave 착수 시점의 개발자/Claude Code 판단에 맡긴다). 이 스크립트
자체가 새 Architecture Component는 아니다(Kernel/Stage/Team 구조에
편입되지 않는 순수 Tooling).

## 5. Consequences & Risks

### 9. 현재 Architecture 보호(사용자 지시 §8)

이 Governance의 핵심은 "Architecture를 다시 설계하는 것"이 아니라
"현재 Architecture 안에서 Python 구현을 더 단순하고 명확하며
의미가 잘 드러나는 코드로 개선하는 것"이다. 다음을 명시적으로
재확인한다:

- 현재 Jarvis OS Architecture/Contract를 "리팩토링 대상"이라는
  이유만으로 변경하지 않는다.
- `archive/v1/`, `docs/decisions/{rfc,adc,adr}/`, Governance/
  Evidence로 인용되는 `projects/*`, `stages/04_implementation/
  architecture_validation/`(Open ADC-0040의 지정 Evidence 도구) 등
  선행 조사가 KEEP으로 확정한 파일은 이 Audit에서도 최소
  `GOVERNANCE REQUIRED` 또는 `KEEP`으로만 분류될 수 있다 —
  `SIMPLIFY`/`REFACTOR` 대상이 될 수 없다(Historical Evidence의
  문언을 그대로 보존해야 하므로).
- 이 RFC/후속 ADC/ADR은 그 자체로 코드 변경을 수행하지 않는다.
  실제 Refactoring Wave 착수는 이 문서들이 Accepted된 이후 **별도
  세션/별도 사용자 승인**을 거쳐 시작한다.

## 6. Open Questions & Change History

### 10. 이 RFC의 결론(요약)

- Repository-wide Python Audit & Refactoring을 위한 Lifecycle(§3),
  권한 경계(§5), 분류 체계(§6), Wave 정책(§7), Validation 정책(§8)을
  전부 기존 Governance 체계·기존 도구 재사용을 우선해 설계했다.
- 새로운 Architecture Component/Layer/Capability를 추가하지 않았다.
- `*.py` 파일을 수정/삭제/이동하지 않았다.
- `ADC-0040`(Stage 04 Multi-Agent Ponytail, 여전히 Open)을 재론하지
  않았다 — "Ponytail"이라는 이름과 guardrail 원칙만 재사용했다.
- 후속 `ADC-0045`가 이 RFC의 채택 여부를 공식 Decision으로
  등록하고, `ADR-0028`이 Accepted된 Governance Lifecycle로 기록한다
  (§11).

### 11. 후속 절차 제안(실행하지 않음, 제안만)

1. **ADC**: 이 RFC의 Lifecycle/권한 경계/분류 체계/Wave·Validation
   정책을 공식 Decision으로 등록 — `ADC-0045`.
2. **ADR**: `ADC-0045`가 Accept를 판정하면, 이 Governance Lifecycle
   자체를 Baseline 절차로 기록 — `ADR-0028`. Architecture/Contract
   변경은 이 ADR에 포함되지 않는다(Process/Governance 기록일 뿐).
3. 실제 Inventory/Deterministic Audit 착수는 `ADR-0028` Accepted
   이후, 별도 사용자 승인을 받아 Wave 0(Inventory 전용, 코드
   무변경)부터 시작한다 — 이 RFC는 그 착수에 관여하지 않는다.

### Related Documents

- `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md`,
  `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md`
  (Ponytail 원 정의, Open 상태 — 재론하지 않음)
- `hqs/development/IMPLEMENTATION_RULES.md`(Comment/Docstring 정책 원 출처)
- `docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`,
  `docs/research/ARCHIVE-CLEANUP-REVALIDATION-0001.md`(파일 보존 판단 선례 —
  후속 검증 결과 이 파일은 `origin/claude/jarvis-archive-cleanup-snro5w`
  브랜치에는 실존하나 main/이 브랜치에는 병합되지 않음, 병합 여부는 이
  RFC의 판단 대상 밖. 근거: `docs/research/OPEN-ISSUES-PR214-VERIFICATION-0001.md`)
- `docs/decisions/adr/ADR-0006-structure-v1-migration.md`(원문은
  `docs/architecture/core/ADR-0006-structure-v1-migration.md`로 인용 —
  후속 검증으로 실제 경로 확인, archive/ 제외 근거)
- `docs/governance/README.md`(Governance 단계 정의, 이 RFC가 새 단계를 추가하지 않았음을 대조하는 근거)
- `docs/architecture/core/ADC-0045-repository-wide-python-audit-and-refactoring-decision.md`(이 RFC 판단을 등록할 후속 ADC, §10/§11 인용)
- `docs/architecture/core/ADR-0028-repository-wide-python-audit-and-refactoring-governance-adoption.md`(후속 Baseline, §10/§11 인용)

### Change History

| Date | Change | Reason |
|---|---|---|
| — | 최초 작성 | Repository 전체 Python Audit & Refactoring Governance Lifecycle/권한 경계/분류 체계/Wave·Validation 정책 확립(구현 아님) |
