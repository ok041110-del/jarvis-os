# PHASE10-PROMPT-SPECIFICATION-AUDIT-0001: Prompt Specification 필요성 검증

이 문서는 사용 후기가 아니다. 실제로 수행한 조사 + 실험 하나의 기록이다.
Phase 9(Engine Use Case 발굴, `ENGINE-USECASE-0001/0002`) 종료 후, "Prompt
Specification이 실제로 필요한가"를 실제 Use Case로 검증한다. Prompt
Specification을 전제로 설계하지 않았다. 새 Contract/Architecture를
생성하지 않았다. RFC/ADC/ADR을 선행 작성하지 않았다. `development-hq/mvp/`
어떤 코드도 수정하지 않았다(조사·실험만 수행, `git status --porcelain`
실험 전후 clean 확인).

## 1. "Prompt Specification"의 현재 정의와 Governance 근거

저장소에 "Prompt Specification"이라는 이름을 쓰는 대상은 **하나뿐**이다:
`core/execution_layer/mvp_0002/prompt_specification_builder.py` —
Execution Layer(Engine MVP 산하, `development-hq/mvp/`와는 별개 트랙)의
6-Builder Pipeline 중 2번째 Artifact. Execution Request(구조화된 8개
항목)를 5개 절(Mission/Input/Constraints/Expected Output/Validation
Notes)로 **재배치(Rendering)** 만 한다 — 본문 텍스트를 한 글자도 바꾸지
않고, "Interpretation을 수행하지 않는다"고 스스로 명시한다.

- 이 모듈을 다루는 전용 ADC/RFC는 없다(`docs/03_adc/ADC.md`,
  `docs/02_rfc/RFC_CANDIDATES.md` 검색 결과 "Prompt Specification"
  언급 없음). Execution Layer 자체의 Production 진입은
  `GOVERNANCE-REVIEW-0004`가 "Blocked — caller 위치 없음"으로 이미
  판정했고(`ADC-0010`/`ADC-0011` 전부 Not Accepted), 이는 Prompt
  Specification의 유용성과 무관하게 Execution Layer 트랙 전체에
  적용되는 별도 Blocking이다.
- `development-hq/mvp/`(Development HQ의 실제 MVP-0001~0049 실행
  경로)는 Prompt Specification을 **한 번도 쓰지 않는다.** 대신
  `agents.py`의 각 Capability 함수가 손으로 쓴 한 문장짜리 지시문
  (instruction) + 원본 입력을 그대로 `call_engine()`에 넘긴다.
  `IMPLEMENTATION_RULES.md`도 Engine Gateway/Registry는 금지하지만
  Prompt Specification 같은 입력 구조화 계층을 요구하는 문구는 없다.

**결론**: Phase 10의 "Prompt Specification"은 이미 존재하는 별개
Concept(Execution Layer MVP-0002)이며, Development HQ의 실제 운영
경로는 그것 없이 49개 MVP를 완주했다. 이번 조사는 "그 없음이 실제
문제였는가"를 검증한다.

## 2. 기존 Prompt 관련 Contract/Rule/Evidence

- Contract 수준의 문서화된 Prompt 형식 요구는 없다 — `agents.py`
  각 함수 docstring이 실제 Engine 실행에서 관찰된 문제(MVP-0025:
  리터럴 마커 단독으로는 의도를 놓침, MVP-0047: 상대 import 검증
  불가 명시 요구)에 대응해 **그때그때 지시 문장 한 줄을 추가**하는
  방식으로 누적되어 왔다.
- 유일한 구조화 시도는 `NO_ISSUES_MARKER`(MVP-0027) — "이슈가 없을
  때만 정확한 문자열을 마지막 줄에 적으라"는 단일 신호 요청. 이것이
  현재 Development HQ에서 "Capability 출력의 verifiability"를
  요구하는 유일한 실제 사례다.

## 3. 실험: 현재 방식의 반복성/일관성/검증 가능성

### Use Case

`backend_agent_code_review()`를 동일 입력에 **3회씩 반복** 호출해
`NO_ISSUES_MARKER` 등장이 안정적인지 검증한다. `MVP-0027-observation.md`는
CLEAN_CODE/SAMPLE_CODE 각각 **1회씩만** 실제 Engine으로 검증했다 —
반복성 자체는 지금까지 한 번도 측정되지 않았다. 두 입력 모두 기존
문서에서 재사용(신규 입력 생성 안 함): `CLEAN_CODE`(`MVP-0027-observation.md`),
`SAMPLE_CODE`(`test_mvp_0001.py`).

### Execution

실제 Engine 호출 6회(`claude -p`, 전부 real):

| 입력 | 기대 | run 1 | run 2 | run 3 | 기대 충족 |
|---|---|---|---|---|---|
| CLEAN_CODE (실제 이슈 없음) | marker 등장 | False | False | **True** | **아니오 (1/3)** |
| SAMPLE_CODE (mutable default + bare except) | marker 미등장 | False | False | False | 예 (3/3) |

### 관찰 결과

1. **SAMPLE_CODE(실이슈 있음)는 3/3 안정적으로 마커를 내지 않았다** —
   위양성(실제 이슈가 있는데 "이슈 없음"으로 잘못 마킹) 없음.
2. **CLEAN_CODE(실이슈 없음)는 3회 중 1회만 마커가 등장했다.**
   `MVP-0027`이 실제로 관찰했던 1회 성공 사례는 반복 시행의 대표값이
   아니었다 — 이번 실험으로 처음 반복성이 깨지는 것을 확인했다.
3. **원인(실제 응답 원문 확인)**: 마커가 없던 두 회차 모두, Engine이
   CLEAN_CODE에 대해 "입력 검증 없음", "테스트 안 보임" 같은
   **style-level 관찰**을 "minor/style-level observations rather
   than functional defects"라고 스스로 구분해 놓고도, 그 관찰들을
   "Issues with the code:" 아래에 나열했다 — 지시문의 "실제 이슈가
   없을 때만"이라는 기준을, 모델이 매번 다르게(엄격하게 vs 관대하게)
   해석했다.

## 4. 현재 방식 vs Prompt Specification — 이 문제를 해결하는가

**Prompt Specification은 이 문제를 해결하지 못한다.**
`prompt_specification_builder.py`는 스스로 "Interpretation을 수행하지
않는다", "Deterministic Rendering"이라고 규정한다 — 그 Deterministic은
**같은 입력 텍스트 → 같은 렌더링 결과**(순수 문자열 재배치)를
뜻한다(`MVP-0002-observation.md` §Deterministic 검증). 이번에 관찰된
문제는 렌더링 단계가 아니라 **Engine이 실제로 응답을 생성하는 단계**의
판단 기준 편차이므로, 입력을 어떻게 구조화해 보여주든 Prompt
Specification의 책임 범위 밖이다.

반대로 이 문제는 Development HQ가 이미 여러 번 실제로 써 온 방법
(Capability 함수의 지시문 한 줄 보강, MVP-0025/0027/0047과 동일한
패턴)으로 좁힐 수 있는 종류다 — 예: "minor style-level observation도
있다면 이슈로 취급하라"처럼 "이슈 없음"의 기준을 지시문에서 더 명시적으로
정의하는 것. 이는 새 Concept이 아니라 기존 Capability 함수의 instruction
문자열 한 줄 조정이다.

## 5. 최종 분류

**B. Capability Prototype으로 해결한다.**

- 반복성 한계는 **실제로 존재한다**(Evidence: 3-repeat 실험, 1/3).
  "문제 없는 것을 문제로 분류"한 것이 아니다 — 실측으로 확인된
  실패다.
- 그러나 이 한계는 Prompt Specification(입력 렌더링 계층)의 책임
  범위 밖이다 — Prompt Specification을 도입해도 마커 반복성은
  개선되지 않는다(§4). 따라서 **C(Prompt Specification 필요성
  Evidence)로 분류하지 않는다.**
- 기존에 이미 반복적으로 성공해 온 방법(지시문 보강, MVP-0025/0027/0047)
  범위 안에서 해결 가능하다 — 새 Architecture/Contract 불필요.
- Architecture/Governance 재검토(D)가 필요한 신호(Concept 누락,
  Boundary 모순)는 관찰되지 않았다.

## Adapter/Contract 필요성

없음. Prompt Specification도, 다른 새 Contract도 이번 조사·실험에서
필요성이 확보되지 않았다.

## Evidence

- 실험 스크립트: 세션 scratchpad(`experiment_prompt_spec_0001.py`,
  tracked 브랜치 미포함).
- 실제 실행 로그(요약): 위 §3 표, CLEAN_CODE run 1/2 전체 응답 원문
  확인(마커 없이 "Issues with the code:" 절 아래 style-level 관찰
  나열).

## Next

- 이번 문서는 **구현하지 않는다** — 지시문 보강(예: "minor
  style-level observation도 이슈로 취급하라")은 별도 작업으로,
  `agents.py`를 실제로 수정할지는 이 조사 범위 밖의 결정이다.
- 반복 횟수 3회(n=3)는 최소 표본이다 — 실제로 마커 기준을 수정한
  뒤 재현율을 다시 측정하는 것이 후속 검증이 된다.
