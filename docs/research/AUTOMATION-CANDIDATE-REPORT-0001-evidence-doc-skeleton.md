# AUTOMATION-CANDIDATE-REPORT-0001: Evidence 문서 골격 반복 — 보고 전용

이 문서는 사용 후기가 아니다. `automation-candidate-watch` Skill을
실제로 실행해 나온 보고 기록이다. **자동화를 구현하지 않는다** — 아래는
보고만이며, Prototype은 사용자 승인 전까지 시작하지 않는다. Branch
Lifecycle Skill(이미 구현·검증 완료)은 이 보고 대상에서 제외했다.

## Candidate 식별

`docs/01_mvp/*.md`(50개) 중 39개, `docs/research/*.md` 중 2개가
"Self Review" 체크리스트 절을 포함한 유사 골격(목적 → BEFORE/실행 →
변경 → AFTER → 비교/판정 → 회귀 확인 → Architecture/Contract 여부 →
Governance → Self Review)을 공유한다. **3회 이상 반복 기준을 크게
초과한다(41건).**

### 오탐 점검 (실제 파일 대조)

- `MVP-0010-observation.md`(초기 문서)는 "Self Review" 절이 **없다** —
  이 골격이 저장소 시작부터 고정된 것이 아니라 시간이 지나며
  수렴된 관행임을 확인했다(추측이 아니라 실제 대조).
- `MVP-0030-observation.md`·`MVP-0049-observation.md`도 절 이름·순서가
  완전히 동일하지 않다(예: 번호를 붙이는 방식, 절 이름 표현이 문서마다
  조금씩 다름) — **"똑같은 템플릿"이 아니라 "느슨하게 수렴한 관행"**
  이다. 이는 자동화의 위험도를 낮추지만(강제 템플릿이 아니라 자유
  변형이 이미 허용됨을 뜻함), 동시에 "완전히 고정된 골격을 강제
  자동화"하면 오히려 기존 자유도를 해친다는 뜻이기도 하다.
- 이미 `CLAUDE.md`가 `md-writer`(Markdown 문서 형식)·`validation`
  (Acceptance Criteria 검증, Self Review와 목적이 겹침) Skill을
  선언해 뒀다(`.claude/skills/md-writer/SKILL.md`,
  `.claude/skills/validation/SKILL.md` 실재 확인). **→ 오탐 점검
  규칙에 따라, 이것은 "새 Automation Candidate"가 아니라 "기존 Skill
  활용도" 문제로 재분류한다.**

## 보고 (7개 항목)

① **반복 횟수**: 41건(`docs/01_mvp/` 39 + `docs/research/` 2), 실제
파일 목록 대조로 확인.

② **현재 Workflow**: 실험/조사 → BEFORE 확인 → 변경 → AFTER 재실행 →
비교 → 회귀 테스트 → 판정(Success/Failure/Inconclusive) →
Architecture/Governance 명시 → Self Review 체크리스트 작성 → commit.

③ **반복 비용/불편**: 매번 손으로 절 구성을 새로 짜면서 Self Review
항목을 빠뜨릴 위험이 있다(실제 관찰: 초기 문서 `MVP-0010`은 그 절
자체가 없었다 — 관행이 자리잡기 전 실제로 빠졌던 사례). 그 외
"자동화가 없어서 지연/실패했다"는 실제 사례는 찾지 못했다(추측
아님).

④ **자동화 가능 단계**: 문서 골격 제공(빈 절 제목 나열), Self Review
체크리스트 항목 누락 여부 확인 — 판단이 필요 없는 형식 점검만.

⑤ **Human 판단 단계**: 실제 실행 결과 판정(Success/Failure/Inconclusive),
BEFORE/AFTER 내용 자체, "억지로 성공 판정하지 않기" — 전부 자동화
대상에서 제외.

⑥ **기존 도구만으로 가능한가**: **가능하다.** `md-writer`/`validation`
Skill이 이미 선언돼 있다 — 새 Skill/Script를 만들 필요가 원칙적으로
없다. 문제는 도구 부재가 아니라 **매번 명시적으로 호출되지 않는
것**이다.

⑦ **Runtime/Architecture 필요 여부**: 없음. 순수 문서 작성 보조이며
Runtime/Scheduler와 무관하다.

## 평가 (위험/복잡도/절감 효과)

- **위험**: 낮음 — 문서 형식 보조일 뿐 삭제/병합/push 같은 되돌리기
  어려운 행동이 없다.
- **복잡도**: 이미 있는 두 Skill을 호출하기만 하면 되므로 매우 낮다
  (새로 만들 것이 없다).
- **절감 효과**: 작음~중간 — 형식 누락을 줄이는 정도이며, 조사·판정
  이라는 핵심 작업 시간은 줄지 않는다. 골격이 관행마다 자유롭게
  변형돼 온 점(§오탐 점검)을 고려하면, 엄격한 새 템플릿을 강제하는
  것은 오히려 손해일 수 있다.

## 결론 — 이 보고의 성격

**새 Skill/Script Prototype을 권장하지 않는다.** 3회 반복 기준은
충족하지만, 오탐 점검 결과 이는 새 Candidate가 아니라 **이미 존재하는
`md-writer`/`validation` Skill을 다음 Evidence 문서 작성부터 실제로
호출할지 여부**의 문제다. 이 판단은 사용자 몫이며, 이 문서는 구현하지
않는다.

## Architecture/Contract 변경 여부

**없음.**

## Governance

RFC/ADC/ADR 불필요.

## Next

- 사용자가 "다음 Evidence 문서부터 `md-writer`/`validation` Skill을
  실제로 호출하라"고 승인하면 그때부터 적용한다 — 이 문서가 선제적으로
  결정하지 않는다.
- Branch Lifecycle 외 다른 반복 후보(예: Governance Review 재확인
  패턴)는 이번 조사에서 3회 미만이거나 구조 편차가 커 보고 대상에
  포함하지 않았다.
