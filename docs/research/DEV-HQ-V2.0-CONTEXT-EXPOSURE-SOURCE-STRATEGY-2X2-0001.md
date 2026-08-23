# DEV-HQ-V2.0-T15 — Context Exposure × Source Strategy 2×2 Research

## 목적

T14는 Scope Pollution이 Full Source 자체보다 "대상 파일이 Context에
노출됐는가"와 상관관계가 있다는 가설을 세웠다. 이 문서는 **동일한
실제 Task, 동일한 Design**을 공유하는 2×2 통제 실험(대상 파일
노출 유/무 × Automatic/Full Source)으로 이를 직접 검증하고, T12~T15
전체를 종합해 원인을 판정한다.

## 실험 대상

`workflow_0002.run_mvp_0002(code: str) -> dict` — T12(`workflow_0008`),
T13(`workflow_0009`), T14(`workflow_artifact_flow`)와 다른 모듈. 기존
`test_workflow_0002.py`에는 mock 기반 테스트 6개가 있고 real-Engine
E2E 테스트가 없다.

### Design — 최소 시그니처 제공 효과

이번에는 Design 입력(issue description)에 함수 시그니처
(`def run_mvp_0002(code: str) -> dict:`)와 "code는 순수 문자열이며
파일시스템/git 상태가 필요 없다"는 한 줄을 명시적으로 포함했다.

T14의 Design(시그니처 미제공)은 존재하지 않는 `tmp_path`/git 워크스페이스
스캐폴딩을 제안했다. 이번 Design은 그 문장을 그대로 반영해 "tmp_path는
요구사항에서 명시적으로 불필요하다고 했으므로 만들지 않는다"고 스스로
명시했다 — **최소 시그니처 한 줄만으로 T14에서 관찰된 파일시스템
오판이 사라졌다.** 하나의 사례이므로 일반화하려면 반복 검증이
필요하지만(다음 Research 참고), 이번 사례에서는 효과가 뚜렷했다.

이 Design 하나를 4개 Build 조건 모두에 동일하게 사용했다.

### AST 자동 폐쇄 결과

`run_mvp_0002` 기준 전이적 의존성: 4개 모듈(`workflow_0002`, `agents`,
`engine`, `workflow`), 발췌 4,090자. Full Source(같은 4개 파일 전문):
10,312자.

## 2×2 Build 결과

| 조건 | prompt_chars | elapsed | 반환 코드 | 기존 6개 테스트 보존 | pytest |
|---|---|---|---|---|---|
| A. Automatic, 미노출 | 6,553 | 6.2s | 415자, 함수 1개 | 보존(harness가 append) | 7 passed |
| B. Automatic, 노출 | 11,227 | 7.3s | 481자, 함수 1개만(기존 SAMPLE_CODE 재사용) | 보존(byte-identical) | 7 passed |
| C. Full Source, 미노출 | 11,082 | 5.7s | 437자, 함수 1개 | 보존(harness가 append) | 7 passed |
| D. Full Source, 노출 | 15,756 | 7.2s | 533자, 함수 1개만 | 보존(byte-identical) | 7 passed |

**이번 4개 조건 전부 파일 전체 재작성이 발생하지 않았다** — 노출
조건(B, D)조차 새 함수 1개만 반환했고, B는 심지어 기존 파일에 이미
정의된 `SAMPLE_CODE` 상수를 재사용하며 import를 반복하지 않는 등
기존 관례를 정확히 인식한 모습을 보였다. 4개 조건 모두 real Engine
E2E 테스트가 정상 실행돼 `{"code_review", "test_execution"}` 키
집합을 정확히 반환했다(harness의 import 경로 보정 1건 외 모델
결과물 자체의 결함은 없었다 — D 조건에서 harness 스크립트의 문자열
치환이 이중 접두어를 만든 것은 검증 도구의 버그였고 수정 후
재검증에서 8개 전부 통과했다).

## T12~T15 종합

| Task | 조건 | 대상 파일 노출 | Context | 재작성(Pollution) 여부 |
|---|---|---|---|---|
| T12 | Manual | 아니오 | 발췌(수동) | 아니오 |
| T12 | Automatic | 아니오 | 발췌(자동) | 아니오 |
| T12 | Full Source | **예** | 전문 | **예** |
| T13 | Automatic | **예** | 발췌(자동) | **예** |
| T13 | Full Source | **예** | 전문 | **예** |
| T14 | Automatic | 아니오 | 발췌(자동) | 아니오 |
| T14 | Full Source | 아니오 | 전문 | 아니오 |
| T15 | A. Automatic | 아니오 | 발췌(자동) | 아니오 |
| T15 | B. Automatic | **예** | 발췌(자동) | 아니오 |
| T15 | C. Full Source | 아니오 | 전문 | 아니오 |
| T15 | D. Full Source | **예** | 전문 | 아니오 |

집계:

- **대상 파일 미노출**: 6/6 사례에서 재작성 없음 (0%).
- **대상 파일 노출**: 5개 사례 중 3개(T12 Full Source, T13
  Automatic/Full Source)에서 재작성 발생, 2개(T15 B/D)에서는 발생하지
  않음 (60%).
- **Automatic vs Full Source**: 노출 여부를 고정한 상태에서 비교하면
  Context 종류(자동 발췌 vs 전체 소스) 자체가 재작성 여부를 가르지
  않았다 — T15에서는 노출 상태에서도 Automatic(B)과 Full Source(D)가
  동일하게 "재작성 없음"이었고, T13에서는 노출 상태에서 Automatic과
  Full Source가 동일하게 "재작성 있음"이었다. 즉 **Context 크기/전략은
  독립적인 설명 변수로 보이지 않는다.**

## Scope Pollution의 실제 원인

"대상 파일 노출"은 재작성 발생의 **필요 조건에 가깝다**(미노출
상태에서는 6/6 전부 안전) 하지만 **충분 조건은 아니다**(노출 상태에서
3/5만 재작성, 2/5는 여전히 안전). 이는 실제 Engine 호출의 확률적
(stochastic) 출력 선택 — 같은 입력이라도 "diff 형태로 새 함수만
반환"과 "파일 전체를 다시 기술" 사이에서 결정적이지 않은 선택을 한다는
것을 시사한다. Context 종류(Automatic/Full Source)는 이 선택에
독립적인 영향을 주지 않는 것으로 관측됐다.

## Signature 제공 효과

이번 1개 사례에서, Design 입력에 함수 시그니처 한 줄만 추가한 것으로
T14에서 관찰된 "존재하지 않는 파일시스템 스캐폴딩 제안"이 사라졌다.
표본이 1개뿐이라 일반화할 수는 없지만, 방향성 있는 개선으로 기록한다.

## 최종 판정

**A. Exposure Effect Validated** (확률적 위험 요인으로) — 대상 파일
노출 여부는 재작성 발생과 강하게 상관관계가 있다(미노출 0/6 vs 노출
3/5). 다만 결정론적 스위치는 아니다: 노출되어도 재작성이 일어나지
않을 수 있다(T15 B, D). Context 크기/전략(Automatic vs Full Source)은
노출 여부를 통제했을 때 독립적인 효과를 보이지 않아 **B. Context Size
Effect는 기각**한다.

내용(Content) 손상 관점에서는 T12~T15, 4개 Task·12개 조건 전체에서
기존 코드가 손상된 사례는 **한 번도 없었다** — 재작성이 일어난
경우에도 형식만 바뀌었을 뿐 기존 테스트는 항상 정확히 보존됐다.

## 다음 Research

1. "대상 파일 노출" 조건에서 **동일 조건을 반복 시행**(n≥5)해 재작성
   발생 확률을 더 정밀하게 추정한다 — 이번 판정(0% vs 60%)은 표본이
   작아(6 대 5) 신뢰구간이 넓다(구현 아님).
2. Design에 함수 시그니처를 제공하는 것이 파일시스템 오판을
   줄이는 효과를 여러 사례에서 반복 검증한다(이번엔 표본 1개)
   (구현 아님).

```text
Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: 36 passed (mvp 전체), 임시 비교 파일(_t15_condition_{a,b,c,d}.py)은 검증 후 삭제, git status clean 확인
E2E: PASS (A/B/C/D 4개 조건 모두 real Engine E2E 통과, D는 harness 검증 스크립트의 치환 버그 수정 후 재확인 — Production Code/모델 결과물 결함 아님)
PR: NOT CREATED
Commit: (아래 커밋 해시)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: YES
Next Implementation Candidate: (1) "대상 파일 노출" 조건에서 반복 시행으로 재작성 확률을 정밀 추정하는 Research, (2) Design 시그니처 제공 효과를 여러 사례에서 반복 검증하는 Research (둘 다 구현 아님)
```
