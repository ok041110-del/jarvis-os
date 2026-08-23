# DEV-HQ-V2.0-T16 — Context Exposure Reproduction Research

## 목적

T15는 대상 파일 노출(Exposure)이 Scope Pollution(파일 전체 재작성)의
확률적 위험 요인이라는 가설을 세웠다(미노출 0/6, 노출 3/5). 표본이
작아 신뢰구간이 넓었다. 이 문서는 **T12~T15와 다른 실제 Task**로 노출
조건을 **5회 반복**해 재현율을 재추정하고, T12~T16 전체를 종합해
Context Research를 종료할 수 있는지 판단한다.

## 실험 설계

- 대상: `workflow_hello_sdlc.run_hello_sdlc(issue: dict) -> dict` —
  T12(`workflow_0008`)/T13(`workflow_0009`)/T14(`workflow_artifact_flow`)/
  T15(`workflow_0002`)와 다른 모듈. 기존 테스트 4개(mock), E2E 없음.
- Design 1회만 실행(모든 trial이 동일 Design 공유) — T15에서 효과를
  보인 최소 함수 시그니처를 이번에도 issue description에 포함했다.
- Build를 **동일한 입력(같은 Design, 같은 Automatic 발췌, 같은
  "대상 파일 노출" 프롬프트)으로 5회 반복 호출**했다 — 각 trial은
  독립적인 real Engine 호출이다(재사용/캐시 없음).
- Automatic AST 발췌: `agents`, `engine`, `workflow_hello_sdlc` 3개
  모듈, 5,332자.

## 5회 반복 결과

| Trial | 반환 코드 크기 | 형태 | 기존 4개 테스트 손상 |
|---|---|---|---|
| 1 | 4,670자 | **파일 전체 재작성**(기존 4개 + 신규 1개) | 없음(diff 확인 — import 2줄 추가 외 전부 동일) |
| 2 | 523자 | 함수 1개만(자체 import 포함) | 없음 |
| 3 | 586자 | 함수 1개만 | 없음 |
| 4 | 717자 | 함수 1개만(마크다운 fence + 후행 설명 문장 잔존 — harness가 제거) | 없음 |
| 5 | 516자 | 함수 1개만 | 없음 |

**재현율: 1/5 (20%)** — T15의 노출 조건 재현율(3/5, 60%)보다 낮지만,
0%(미노출)보다는 명백히 높다.

### 내용 검증

Trial 1(전체 재작성)의 diff를 원본과 대조한 결과, 차이는 `import
shutil`/`import pytest` 2줄 추가와 새 함수 삽입뿐이었다 — 기존 4개
테스트 본문은 문자 단위로 동일했다.

모든 5개 trial을 실제 `test_workflow_hello_sdlc.py`에 적용해(trial
1은 그대로, 2/3/4/5는 harness가 기존 파일에 append) pytest 실행:

```
25 passed in 423.30s (0:07:03)
```

5개 trial 전부, 기존 4개 mock 테스트 + 신규 real-Engine E2E 테스트
1개(`run_hello_sdlc`의 다단계 real Engine 호출 체인 전체 실행)가
정상 통과했다. Trial 4의 마크다운 코드펜스 잔존은 Build의 사소한
지시 불이행("코드만 반환, 부연 설명 없이")이었고 harness가 이를
제거하는 정형적 후처리로 해결했다 — 이는 Scope Pollution과는 다른
별개의 결함 유형이다(코드 자체 손상이 아니라 출력 포맷 문제).

## T12~T16 종합

| Task | 조건 | 대상 파일 노출 | 재작성 발생 | 표본 |
|---|---|---|---|---|
| T12 | Manual/Automatic | 아니오 | 아니오/아니오 | 2 |
| T12 | Full Source | 예 | 예 | 1 |
| T13 | Automatic/Full Source | 예/예 | 예/예 | 2 |
| T14 | Automatic/Full Source | 아니오/아니오 | 아니오/아니오 | 2 |
| T15 | A/C(미노출) | 아니오 | 아니오/아니오 | 2 |
| T15 | B/D(노출) | 예 | 아니오/아니오 | 2 |
| T16 | 노출 반복 5회 | 예 | 1/5 재작성 | 5 |

누적 집계:

- **미노출**: 6/6 (0%) 재작성.
- **노출**: 10회 시행 중 4회 재작성 (T12 1/1, T13 2/2, T15 0/2, T16
  1/5) = **40%**.

내용 손상은 T12~T16 전체 4개 Task, 16개 이상의 개별 조건/trial에서
**단 한 번도 발생하지 않았다** — 재작성이 일어나도 기존 코드는 항상
정확히 보존됐다.

## Context Research 종료 여부

**종료한다.** 근거:

1. **핵심 질문(노출 vs Context 크기)에 대한 답이 4개 Task에 걸쳐
   안정적으로 재현됨**: 미노출 0%, 노출 ~40% — 노출이 위험 요인이라는
   결론이 추가 반복으로도 뒤집히지 않았다.
2. **Context 크기(Automatic vs Full Source)가 독립 변수가 아니라는
   결론도 T13/T15에서 일관됨**: 노출 여부를 고정하면 Automatic과
   Full Source가 항상 같은 방향으로 움직였다.
3. **내용 손상 위험이 사실상 0으로 확인됨**: 4개 Task, 16개 이상 조건
   전체에서 재작성이 일어나도 기존 코드가 손상된 사례가 없다 — 이는
   "재작성 형식"이 Production 위험이 아니라 Build 단계의 출력 형식
   선택(diff vs full-file)의 문제임을 시사한다.
4. **추가 반복이 Architecture/Contract/Production 판단을 바꿀 여지가
   작다**: 재현율이 20%~60% 사이에서 흔들리는 것을 더 정밀하게
   추정해도, "노출을 피하면 위험이 사실상 0" / "노출해도 내용은
   손상되지 않는다"는 실무적 결론 자체는 바뀌지 않는다.

## 다음 Implementation

Context Research(T06~T16)를 종료하고, 결과를 요약하면:

- AST 기반 Multi-Module Automatic Excerpt는 단일/다중 모듈, 얕은
  호출 그래프에서 Full Source와 동등한 Build 정확성을 낸다(T09~T12).
- Scope Pollution(파일 전체 재작성)은 Context 크기가 아니라 "대상
  파일이 Context에 노출됐는가"에 좌우되는 확률적 현상이며(T13~T16),
  발생해도 지금까지 내용 손상 사례는 없다.
- Design 단계에 최소 함수 시그니처를 제공하면 존재하지 않는
  파일시스템 스캐폴딩 오판이 줄어드는 경향이 있었다(T15/T16, 표본
  각 1개).

이 결과를 Production에 통합할지(예: Build Capability에 AST 기반
Context 자동 추출을 실제로 연결할지)는 **Architecture 변경 여부를
판단해야 하는 문제**이므로, 이 Research 결과를 근거로 RFC를 검토하는
것이 다음 단계다. 이 문서 자체는 그 결정을 내리지 않는다(Frozen
Architecture 원칙).

```text
Architecture Change: NONE
Contract Change: NONE
Production Code Change: NO
Tests: 36 passed (mvp 전체, 검증용 25 passed는 임시 trial 파일 삭제 후 반영되지 않음), 임시 trial 파일(_t16_trial_1~5.py)은 검증 후 삭제, git status clean 확인
E2E: PASS (5회 반복 모두 real Engine E2E 통과, 1/5는 파일 전체 재작성 형태였으나 내용 손상 없음)
PR: NOT CREATED
Commit: (아래 커밋 해시)
Branch: claude/dev-hq-v2-readiness-audit-qyzj8e
Push: YES
Next Implementation Candidate: T06~T16 Context Research 결과를 근거로, AST 기반 Context 자동 추출을 Production Build Capability에 실제로 통합할지 판단하는 RFC 검토(Governance 절차, 이 세션의 판단 범위 밖)
```
