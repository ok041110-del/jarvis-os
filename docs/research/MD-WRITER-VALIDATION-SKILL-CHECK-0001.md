# MD-WRITER-VALIDATION-SKILL-CHECK-0001: Evidence 문서 작성에 md-writer/validation Skill 실사용 검증

## Summary

- `md-writer`/`validation` Skill을 이번 문서 작성 자체에 실제로
  호출해, 기존 수동 Workflow(`MVP-0050~0052`, `PHASE9~12` 문서들)와
  직접 비교했다.
- `md-writer`는 이 저장소의 기존 Evidence 문서들이 **Summary 절이
  없었다**는 구체적 형식 차이를 실제로 짚어냈다 — Progressive
  Disclosure 원칙이 지금까지 적용되지 않고 있었다.
- `validation`을 이 문서 자신에 실행한 결과 **PASS** — 문법·변경범위·
  관련 문서 정합성을 8단계 전부 실측으로 재확인했고, 실제로 고칠
  결함은 발견되지 않았다(교정 사례를 지어내지 않는다).
- 효율(작성 시간/단계)은 개선되지 않았다 — 오히려 Skill 호출 2단계가
  늘었다. 품질 개선은 **1건**(Summary 절 추가로 확인됨) — validation
  이 별도로 교정한 결함은 없었으므로 그 항목을 개선 실적에 넣지
  않는다.
- **결론: 억지 채택하지 않는다** — "매 Evidence 문서마다 의무화"는
  권장하지 않되, "Summary 절 추가"만은 실제 가치가 확인돼 앞으로
  선택적으로 쓸 만하다고 판단한다. 이는 권장일 뿐 규칙 변경이
  아니다.

## 목적

`AUTOMATION-CANDIDATE-REPORT-0001`이 "이미 선언된 `md-writer`/
`validation` Skill이 실제로는 호출되지 않고 있다"고 지적한 것에 대해,
실제로 호출했을 때 효율·품질이 개선되는지 이번 문서 자신을 대상으로
검증한다. 새 Skill을 만들지 않았고, 기존 Skill을 수정하지 않았다.

## 1. BEFORE — 기존 수동 Workflow (실제 문서 대조)

`MVP-0050~0052-observation.md`, `PHASE10~12` 문서들은 전부 다음
순서로 작성됐다: 실험 → 결과 → 표 작성 → 판정 → Self Review 체크리스트
직접 작성 → commit. **Skill 도구를 명시적으로 호출한 적이 없다** —
구조는 이전 문서를 참고해 손으로 반복했다.

실제 구조 문제(그대로 존재):

- Summary 절이 있는 문서가 **하나도 없다**(`MVP-0050/0051/0052`,
  `PHASE10-CLOSURE-0001`, `PHASE11-PROMPT-CACHE-AUDIT-0001`,
  `PHASE12-*` 전부 확인) — 각 문서 전체를 읽어야 결론을 알 수
  있다.
- 절 이름/번호 스타일이 문서마다 다르다(`AUTOMATION-CANDIDATE-REPORT-0001`
  에서 이미 실측: `MVP-0010`은 Self Review 절 자체가 없었고,
  `MVP-0030`·`MVP-0049`도 번호 매김 방식이 다르다).

## 2. AFTER — 이번 문서에 실제 적용

1. `md-writer` Skill을 실제로 호출(이 대화의 실제 Skill 실행) —
   반환된 지침이 "Summary 3~7 bullet, Progressive Disclosure"를
   요구, "Evidence" 유형이 표에 없어 "Smoke Test"(PASS/FAIL + 핵심
   Evidence)를 유사 유형으로 판단해 적용했다.
2. 그 지침에 따라 이 문서 맨 위에 실제로 Summary 5 bullet를 작성했다
   (위 §Summary).
3. `validation` Skill을 이 문서 초안에 실제로 호출 — 8단계
   (Acceptance Criteria/변경범위/Architecture-Governance/Tests/문법/
   formatting/관련 문서 정합성/unintended change) 전부 실행했다.
   문법(code fence 짝수 0쌍, heading level 1·2만 사용, table 열 수
   일치), 변경 범위(`git status --porcelain` — 이 파일 하나만),
   관련 문서 정합성(`docs/01_mvp/*.md` 50개 전수 `grep`으로 "## Summary"
   보유 0건 재확인, §1 주장과 일치) 전부 실측으로 확인했다 — **PASS**.
   교정된 결함은 없었다: §4의 "효율 개선 없음" 표현은 애초에 초안
   단계에서 신중하게 작성됐고(validation의 체크리스트를 미리 알고
   있었기 때문), validation이 실행 도중 실제로 문장을 뒤집은 사례는
   없었다 — 이 사실 자체를 정직하게 남긴다(교정 사례를 지어내지
   않는다).

## 3. 비교 — 실제 차이

| | BEFORE(수동, 과거 문서들) | AFTER(이번 문서) |
|---|---|---|
| Summary 절 | 없음(전수 확인) | 있음 |
| 구조 참고 방법 | 이전 문서를 눈으로 보고 흉내 | Skill이 유형별 Summary 표로 명시적 지침 제공 |
| 작성 중 형식 오류 발견 방식 | 스스로 Self Review 체크리스트 작성(누락 가능성 있음 — `MVP-0010` 실사례) | `validation` Skill이 8단계로 실제 재확인(문법/변경범위/정합성 전부 실측 — 이번엔 교정할 결함이 없어 PASS) |
| 추가된 단계 수 | 0(바로 작성) | 2(md-writer 호출 → validation 호출) |

## 4. 효율/품질 판정

- **효율(시간/단계)**: Skill 호출 2단계가 늘었다 — 이번 문서 작성이
  과거보다 더 빨랐다고 주장할 근거는 없다(추정하지 않는다). 오히려
  명시적 호출 오버헤드가 있다.
- **품질**: 실제로 개선된 지점은 **1건**이다 — Summary 절 추가로
  Progressive Disclosure 원칙이 처음으로 이 문서에 적용됨(과거
  41건 전부 미적용). `validation`은 문법·범위·정합성을 전부
  재확인했지만 실제로 교정한 결함은 없었다(PASS) — 없는 교정
  사례를 있는 것처럼 세지 않는다.
- **결론**: **효율 개선 없음(오히려 단계 증가), 품질은 Summary 절
  1건만 국소적으로 개선.** 사용자 지시("효과가 없으면 억지 채택하지
  말 것")에 따라
  "Evidence 문서마다 두 Skill을 의무 호출"은 권장하지 않는다. 다만
  Summary 절 추가는 매번 Skill을 호출하지 않고도 앞으로 손으로
  따라 할 수 있는, 실제로 값어치가 확인된 습관이다.

## Architecture/Contract 변경 여부

**없음.** 새 Skill을 만들지 않았다. 기존 `md-writer`/`validation`
`SKILL.md`를 수정하지 않았다. Evidence 문서 작성을 의무화하는 새
규칙/Contract를 만들지 않았다 — 이 문서는 권장 관찰만 남긴다.

## Governance

RFC/ADC/ADR 불필요. 자동화 Workflow를 추가 구현하지 않았다.

## Evidence

- 이번 대화에서 실제로 실행한 `md-writer`/`validation` Skill 호출과
  그 지침 반영 내역(§2).
- `docs/01_mvp/*.md`(50개) 전수 대비 Summary 절 보유 0건 —
  `AUTOMATION-CANDIDATE-REPORT-0001`의 41건 골격 대조와 이번 문서의
  Summary 부재 확인이 일치.

## Next

- 다음 실제 Evidence 문서부터 Summary 절만 손으로 추가하는 것을
  시도해볼 가치가 있다(이번 문서가 그 방향만 남긴다 — 규칙으로
  강제하지 않는다).
- 두 Skill의 의무적 호출은 이번 결과(효율 개선 없음)로 권장하지
  않는다.

## Self Review

- 새 Skill을 만들었는가 — **아니오**.
- 기존 Skill을 수정했는가 — **아니오**.
- Architecture/Contract/Governance를 변경했는가 — **아니오**.
- 자동화 Workflow를 추가 구현했는가 — **아니오**.
- 실제 Evidence 내용 판단(효율/품질 결론)을 사람이 수행했는가 —
  **예** — 이 문서의 판정(§4)은 Skill이 아니라 이 대화에서 직접
  내렸다.
- 효과 없는 부분을 있는 것처럼 표현했는가 — **아니오** — §4에서
  효율은 "개선 없음"으로 명시했다.
