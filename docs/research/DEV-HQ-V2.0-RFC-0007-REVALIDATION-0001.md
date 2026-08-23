# DEV-HQ-V2.0 — RFC-0007 Revalidation & Decision

## 목적

RFC-0007(§Decision: B. CONDITIONAL)이 요구한 두 선행조건이 각각
별도 Research 문서로 검증됐다. 이 문서는 **새 실험 없이** T06~T19
Evidence만을 근거로 RFC-0007의 Decision을 재평가한다.

## 1. 무엇을 재검토했는가

- RFC-0007 원문(§Decision, §2, §8-4, Open Issues)
- 선행조건 1 Evidence: `DEV-HQ-V2.0-DESIGN-AST-STARTPOINT-IDENTIFICATION-0001.md`(T17, 1건),
  `DEV-HQ-V2.0-AST-CANDIDATE-INDEX-REPRODUCTION-0001.md`(T17 재현 2건)
- 선행조건 2 Evidence: `DEV-HQ-V2.0-TARGET-FILE-EXPOSURE-MITIGATION-0001.md`(1 Task, 3조건)
- 위 문서들이 인용하는 T12~T16 Context Research 종합
  (`DEV-HQ-V2.0-CONTEXT-EXPOSURE-REPRODUCTION-0001.md` 등)

## 2. 두 선행조건의 Evidence

### 선행조건 1 — 시작점(target module/function) 자동 식별

RFC-0007 §2가 지적한 격차: "Design의 자유 서술형 출력은 AST 폐쇄의
시작점 정보를 구조적으로 담지 않는다."

- Design 원문만(A) / Design + 파일 목록만(B)으로는 식별 **실패**
  (`FILE: UNKNOWN` / `FUNCTION: UNKNOWN`, 정직한 실패 — 오답을
  지어내지 않음).
- Design + **AST 함수 후보 인덱스**(이름 + 시그니처 + docstring 첫
  줄, 본문 없음, 저비용)를 추가하면 **3/3(100%)** 정확히 식별됨 —
  서로 다른 성격의 Task 3건(공백 검증 로직, 코드펜스 경계 케이스,
  Context 재사용 계약)에서 실패 없이 재현.
- 3건 모두 식별된 시작점으로 실제 AST 폐쇄 → Build → pytest까지
  end-to-end로 검증됨(전부 real Engine, 전부 통과).

**판정**: 재현됨. 표본은 작지만(3건) 실패 사례가 없고, 서로 다른
Task 성격에서 반복 확인됐다.

### 선행조건 2 — Target File Exposure 완화 정책

RFC-0007 §8-4가 지적한 격차: "실제 파일 수정 Task에서는 노출이
불가피할 수 있고, 그 경우의 재작성 위험(T12~T16 누적 ~40%)을 다룰
정책이 없다."

- T12~T18은 전부 "기존 파일에 새 함수를 **추가**"하는 Task였다 —
  실제 "기존 함수 수정" Task는 이번이 처음이다.
- **미노출(A)**: Design 요구사항("기존 함수를 확장")을 구조적으로
  충족 불가 — 새 함수를 별도로 만드는 것 외 선택지가 없었다. 즉
  실제 수정 Task에서 Exposure는 "위험이 낮은 선택지"가 아니라
  "생략 불가능한 전제조건"임이 확인됐다.
- **노출 + 최소 정책(B, C)**: "대상 함수를 정확한 이름으로 지목" +
  "다른 부분은 건드리지 않는다는 명시적 부정 지시"를 포함하면,
  반환된 전체 파일의 실제 diff가 **2/2 전부** 지정된 함수 내부의
  순수 추가로 한정됐다(다른 함수/import/공백 변경 없음, pytest
  14 passed).
- 이 결과는 T15/T16의 지표("재작성 발생률 ~40%")를 반박하지 않는다
  — 측정 대상 자체가 다르다. T15/T16은 "재작성이 일어나는가"를,
  이 Research는 "재작성이 일어났을 때 Scope를 지켰는가"를 측정했다.
  이 지표 전환은 Evidence 문서 자체가 명시적으로 밝힌 것이며, 이번
  재검토도 그 구분을 그대로 유지한다.

**판정**: 최소 정책(대상 함수 명시 + 불변 부분 명시)의 존재 자체는
Evidence로 뒷받침된다. 다만 표본이 1개 Task·2개 조건뿐이라
일반화에는 한계가 있다 — RFC-0007 §8-4가 요구한 "정책이 없다"는
공백은 채워졌으나, "이 정책이 항상 충분하다"는 것까지 증명된 것은
아니다.

## 3. RFC-0007 Decision 재평가

원 Decision(B. CONDITIONAL)의 조건문은 "다음 두 선행조건이
해결되지 않은 상태에서 통합을 진행하는 것은 권장하지 않는다"였다.
두 선행조건 모두 최소 1건 이상의 긍정적 Evidence로 해결됐으므로,
그 조건문의 전제가 더 이상 성립하지 않는다.

**Decision: A. INTEGRATION JUSTIFIED (조건부 범위로 한정)**

- 선행조건 1(시작점 식별)은 3건 재현으로 사실상 닫힌 문제로 본다.
- 선행조건 2(Exposure 정책)는 존재는 확인됐으나 표본이 얇다
  (1 Task) — 이는 A 판정을 막는 이유는 아니지만, 다음 ADC 단계에서
  **이 정책 문구를 그대로 고정 요구사항으로 명시**하고(§6), 초기
  적용 범위를 좁게(§7) 시작해야 하는 이유다.
- A 판정은 RFC 본문이 이미 명시한 대로 즉시 구현을 뜻하지 않는다
  — 다음 단계는 ADC(→ 필요 시 ADR) → 최소 Production
  Implementation → E2E Validation 순서다.

## 4. Architecture Impact

**없음(NONE, RFC-0007 원 판정 유지)**. 두 선행조건의 Evidence는
Runtime/Registry/Engine Gateway/Event Bus 등 Frozen 금지 목록에
해당하는 어떤 개념도 새로 요구하지 않는다. AST 함수 후보 인덱스
생성도, Exposure 정책 프롬프트도 모두 "문자열을 만들어 입력에
concatenate"하는 기존 패턴(Project Intelligence가 이미 확립) 안에
있다.

## 5. Contract Impact

RFC-0007 §Contract Impact가 이미 밝힌 것 이상으로 확장되지 않는다
— 다만 이번 Evidence로 암묵적 입력 계약의 구성 요소가 더 구체화됐다:

- 함수 시그니처 변경 없음(원 판정 유지).
- 암묵적 입력 계약은 이제 세 부분으로 구성된다: **(1)** Design
  서술, **(2)** AST 함수 후보 인덱스(시작점 식별용, 이름+시그니처+
  docstring 첫 줄), **(3)** 대상 파일 노출 시 최소 정책 지시(대상
  함수 명시 + 불변 부분 명시). 이 구성은 ADC 단계에서 명시적으로
  기록해야 한다(RFC-0007 §3 재확인).

## 6. Context 생성 책임 위치

RFC-0007 §4가 제기한 두 후보(`project_intelligence.py` 확장 vs
신규 모듈 분리)는 **이번 재검토의 대상이 아니다** — T17~T19
Evidence 어느 것도 이 질문을 다루지 않았다. RFC-0007 원문대로
ADC 단계의 판단 사안으로 남긴다.

## 7. Target File Exposure 정책

ADC로 이관할 최소 정책 후보(Evidence 2/2로 뒷받침, §2 참고)는
다음 두 요소를 **모두** 포함해야 한다:

1. 대상 함수를 정확한 이름으로 지목.
2. "다른 부분은 건드리지 않는다"는 명시적 부정 지시(예: "다른
   함수/import/공백은 어떤 이유로도 변경하지 않는다").

표본이 얇으므로(1 Task), ADC 단계에서 이 정책을 **고정 요구사항**
(선택적 권고가 아니라)으로 명시하고, 최소 Production Integration
초기 범위를 "기존 함수 확장"류의 좁은 Task로 제한하는 것을 권고한다
(§8 참고). "노출 + 무지시" 조건과의 직접 비교는 아직 없다 —
`TARGET-FILE-EXPOSURE-MITIGATION-0001.md` §다음 Task가 이미 Open
Issue로 남긴 항목이며, 이번 재검토도 이를 새로 실험하지 않는다.

## 8. 최소 Production Integration 범위

RFC-0007 §8(Implementation Candidate)이 제시한 범위를 그대로
유지하되, 이번 Evidence로 다음 두 항목이 구체화된다:

1. AST 폐쇄 함수 1개 추가 — 위치(§4)는 ADC 결정 사안(변경 없음).
2. **AST 함수 후보 인덱스 생성 로직**이 추가 구현 대상으로
   확정된다(§17 재검토에서 새로 확인된 구성 요소) — 저장소
   `mvp/*.py` 전체의 top-level 함수/클래스 이름+시그니처+docstring
   첫 줄만 추출하는 순수 정적 분석 함수. 새 Capability/Agent
   아님, 새 Runtime/Registry 아님(§4 Architecture Impact와 동일
   근거).
3. 대상 workflow 파일에서 Build 호출 직전 Context concatenate
   한 줄 추가(원 판정 유지).
4. Exposure 정책 지시문(§7의 두 요소)을 Build 호출 프롬프트에
   고정 포함.
5. **초기 적용 범위 제한(신규 권고)**: 표본이 1 Task뿐인 선행조건
   2의 한계를 감안해, 최소 Production Implementation의 첫 적용은
   "기존 함수 1개 확장" 성격의 좁은 Task로 한정하고, 더 넓은
   범위(다중 함수 동시 수정, 파일 구조 변경 등)는 별도 재검증 후
   확장하는 것을 ADC에 권고한다.

## Open Issues (해결하지 않음, ADC로 이관)

- Context 생성 책임 위치(§6) — 미해결.
- "노출 + 무지시" vs "노출 + 최소 정책" 직접 비교 — 미실험.
- 저장소 규모 확장 시(수십~수백 개 함수) AST 함수 후보 인덱스의
  크기·식별 정확도 — 미검증(`AST-CANDIDATE-INDEX-REPRODUCTION-0001.md`
  §다음 Task가 이미 지적).
- RFC-0005(Development HQ ↔ Execution Layer Boundary)와의 불일치
  — RFC-0007 Open Issues에 이미 기록된 그대로 미해결.

## 최종 보고

1. **무엇을 재검토했는가** — RFC-0007의 B. CONDITIONAL 판정과 그
   근거가 된 두 선행조건을, T17~T19의 세 Research 문서(시작점 식별
   재현 3건, Exposure 완화 정책 1건)로 재평가했다. 새 실험은
   수행하지 않았다.
2. **두 선행조건의 Evidence** — 시작점 식별 3/3 재현(서로 다른 Task
   성격), Exposure 완화 정책 2/2 Scope 준수(1 Task, 지표를
   "재작성 발생 여부"에서 "재작성 시 Scope 준수 여부"로 전환).
3. **RFC-0007 최종 Decision** — **A. INTEGRATION JUSTIFIED**(조건부
   범위로 한정 — §3, §7, §8-5 참고). 두 선행조건이 각각 최소
   1건 이상의 긍정적 Evidence로 뒷받침되어 원 Decision(B)의
   보류 사유가 해소됐다.
4. **Architecture / Contract 영향** — Architecture 영향 없음(원
   판정 유지). Contract는 함수 시그니처 변경 없이, 암묵적 입력
   계약이 3요소(Design 서술 + AST 함수 후보 인덱스 + Exposure
   정책 지시)로 구체화됨.
5. **Production Integration 범위** — RFC-0007 §8 범위 + AST 함수
   후보 인덱스 생성 로직(신규 구현 대상) + Exposure 정책 지시문
   고정 + 초기 적용 범위를 "기존 함수 1개 확장"류로 제한하는 권고.
6. **다음 Implementation** — ADC 작성(RFC-0007 Decision 승격을
   Decision Candidate로 등록) → 필요 시 ADR → 위 §8 범위의 최소
   Production Implementation → E2E Validation. 이 문서 자체는
   ADC/ADR을 작성하거나 Production Code를 변경하지 않는다.

```text
Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: N/A (신규 코드 실행 없음 — 기존 Evidence 문서 재인용만)
E2E: N/A
PR: NOT CREATED
Commit: (아래 커밋 해시)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: YES
Next Implementation Candidate: RFC-0007 Decision(A. INTEGRATION JUSTIFIED)을
ADC Decision Candidate로 등록 — Context 생성 책임 위치(§6)와
Exposure 정책(§7)을 ADC에서 확정한 뒤 §8 최소 범위로 Production
Implementation 착수
```
