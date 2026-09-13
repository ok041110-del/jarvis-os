# ADC-0045: Repository-wide Python Audit & Refactoring Governance Decision (RFC-0042 후속)

## 목적

`RFC-0042-repository-wide-python-audit-and-refactoring-governance.md`가
설계한 Lifecycle(Inventory → Deterministic Audit → Semantic/
Ponytail Review → Candidate Classification → Refactoring Wave →
Validation → Evidence), Ponytail 권한 경계, 7종 Candidate
Classification, Wave 정책, Validation 정책을 공식 Governance
Decision으로 채택할지 판정한다. 이 ADC는 `RFC-0042`의 조사 내용을
재론하지 않고 그 결론 위에서 ADOPT/KEEP(=현행 유지)/REJECT 중
하나를 판정한다.

---

## Q1. 이 RFC는 실제로 Governance 절차만 정의했는가(코드 변경 없음 확인)

**예.** `RFC-0042`는 어떤 `*.py`도 수정/삭제/이동하지 않았다(git
diff 확인 대상: 이 세션에서 추가된 파일은 `docs/architecture/core/`
아래 문서 3건뿐). 실제 Inventory/Audit/Refactoring 실행은 이
ADC/RFC의 범위 밖으로 명시적으로 미뤄졌다(`RFC-0042` §11).

## Q2. 기존 Governance 체계와 충돌하는가

**아니오.** 확인한 항목:

- RFC/ADC/ADR 번호 체계·문서 위치(`docs/architecture/core/`)를
  그대로 이었다 — 새 트랙을 만들지 않았다.
- `RFC-0042` §6의 7종 분류(KEEP/COMMENT·DOCSTRING CLEANUP/
  SIMPLIFY/REFACTOR/POSSIBLE BUG/ARCHITECTURE·CONTRACT RISK/
  GOVERNANCE REQUIRED)는 선행
  `STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`의
  파일 보존 분류(A~E)와 이름이 겹치지 않으며, "파일 내용 개선
  필요 여부"라는 다른 축을 분류한다 — 직교하는 별개 체계로
  확인했다.
- `ADC-0040`(Stage 04 Multi-Agent Ponytail, 여전히 **NOT
  DETERMINED — Open**)을 재론하지 않았고, 그 Decision을 대신하지도
  않았다 — "Ponytail"이라는 이름과 `ponytail_policy.py` guardrail
  4종의 원칙만 재사용했을 뿐, Stage 04 Production 채택 여부에는
  어떤 영향도 주지 않는다.
- Comment/Docstring 정책(최대 2줄, WHY 중심)은 새로 만들지 않고
  `IMPLEMENTATION_RULES.md`/CLAUDE.md 기존 확정 정책을 그대로
  인용했다.

## Q3. Ponytail 권한 경계가 Architecture/Contract를 임의로 바꿀 여지를 남기는가

**아니오.** `RFC-0042` §5가 "판단 불명확 시 기본값은 Governance
필요 쪽"이라는 보수적 원칙을 명시했고, §6 분류표에서
`ARCHITECTURE/CONTRACT RISK`는 자동으로 `GOVERNANCE REQUIRED`로
승격되도록 설계했다 — Ponytail 스스로 이 경계를 넓힐 수 있는
경로가 코드/절차 어디에도 없다(§9에서 "경계를 바꾸려면 새 RFC가
필요하다"고 명시).

## Q4. Wave 정책이 "Repository 전체를 한 번에 수정"할 위험을 실제로 막는가

**예, 절차적으로는 그렇다.** `RFC-0042` §7이 각 Wave 착수 시점에
범위를 문서로 선언하고 그 선언을 벗어나면 Wave를 종료·분리하도록
설계했다 — 이는 코드로 강제되는 장치가 아니라 절차 규범이다(이
저장소의 다른 절차 규범들, 예: "Governance 우회 금지"와 동일한
성격 — `RFC-0037` §6이 이미 "코드로 강제 불가능한 절차 규범"이라는
동일 Gap을 인정한 선례가 있다). **Gap으로 기록**: Wave 크기 상한을
숫자로 고정하지 않았다 — 이는 실제 Wave 착수 시점의 사용자 승인이
매 Wave마다 그 범위를 재확인하는 것으로 보완한다(Decision에 조건으로
반영, 아래 참고).

## Q5. Validation 정책이 새 Validator 신설을 최소화했는가

**예.** `RFC-0042` §8 표는 9개 항목 전부에 기존 도구/기존 테스트
재사용 경로를 제시했고, 유일한 신규 제안(AST-level sanity/comment
정책 검사의 Repository 전체 일반화)도 "필요성만 인정, 실제 작성은
Wave 착수 시점으로 유보"로 최소화했다.

## Q6. 이 Decision이 별도 RFC 없이 실제 Refactoring Wave 착수를 자동으로 허가하는가

**아니오, 명시적으로 아니다.** `RFC-0042` §9/§11이 "Accepted 이후
별도 세션/별도 사용자 승인을 거쳐 Wave 0(Inventory 전용, 코드
무변경)부터 시작한다"고 명시했다 — 이 ADC의 Accept는 **Governance
절차 자체의 채택**이지 **실제 코드 수정의 사전 승인**이 아니다.
이 구분을 `ADR-0028`에서도 동일하게 유지한다.

---

## Decision

**ADOPT — Governance Lifecycle Accepted, Implementation은 별도
승인 필요.**

`RFC-0042`가 설계한 Lifecycle/Ponytail 권한 경계/7종 Classification/
Wave 정책/Validation 정책을 Repository-wide Python Audit &
Refactoring의 공식 Governance 절차로 채택한다. 이 Decision은
다음을 명확히 구분한다:

- **지금 승인하는 것**: Governance 절차 자체(Lifecycle 정의, 권한
  경계, 분류 체계, Wave/Validation 정책). 이는 RFC/ADC/ADR
  문서로만 존재하며 코드에 아무 영향을 주지 않는다.
- **지금 승인하지 않는 것**: 실제 Inventory 실행, 실제 Deterministic
  Audit 실행, 실제 `*.py` 수정. 이들은 이 Decision이 Baseline에
  기록된(`ADR-0028`) 이후, Wave 단위로 별도 사용자 승인을 받아야만
  착수한다.
- **조건**: 매 Wave 착수 전, 그 Wave의 범위(대상 디렉터리/HQ,
  대상 Classification)를 Evidence 문서 서두에 선언하고 사용자
  승인을 받는다(Q4의 Gap을 절차로 보완).

## Self Review

- Architecture를 새로 설계했는가 — **아니오**. 현재 Architecture/
  Contract는 무변경(§Q3).
- `ADC-0040`과 충돌하는가 — **아니오**(§Q2, Ponytail 이름/원칙만
  재사용, Stage 04 Decision은 그대로 Open 유지).
- 코드를 작성했는가 — **아니오**.
- commit/push를 수행했는가 — 이 파일 작성 이후 `ADR-0028`과 함께
  일괄 커밋한다(PR은 사용자 지시에 따라 이번 세션에서 생성하지
  않는다 — CLAUDE.md PR 필요성 기준상 코드 변경이 없는 순수
  Governance 문서 추가).

## Related

- `docs/architecture/core/RFC-0042-repository-wide-python-audit-and-refactoring-governance.md`
- `docs/architecture/core/RFC-0037-stage04-multi-agent-ponytail-boundary.md`,
  `docs/architecture/core/ADC-0040-stage04-multi-agent-ponytail-decision.md`
  (Ponytail 원 정의, 재론하지 않음)
- `hqs/development/IMPLEMENTATION_RULES.md`
- `docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`,
  `docs/research/ARCHIVE-CLEANUP-REVALIDATION-0001.md`
