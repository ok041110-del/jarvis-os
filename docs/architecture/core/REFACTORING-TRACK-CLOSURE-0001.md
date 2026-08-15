# REFACTORING-TRACK-CLOSURE-0001: P2/P3 처리 결과 및 Refactoring Track 종료 판단 (Phase 10)

**문서 성격**: Refactoring 실행 기록 + Governance 판단. P1(P1-2
Characterization Tests → P1-1 중복 제거, 이전 커밋)에 이은 P2/P3
단계의 결과를 기록한다. P3는 **판단만 하고 코드를 수정하지 않았다.**
`docs/03_adc/ADC.md`를 수정하지 않는다.

**선행 문서**: `EFFICIENCY-AUDIT-0001`(Phase 9, 저장소 전체 중복 실사),
`docs/research/STOCK-AGENT-SEPARATION-REVIEW-0001.md`,
`docs/research/DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001.md`,
`development-hq/IMPLEMENTATION_RULES.md`.

---

## 0. 실행한 검증

각 단계 직후 `python3 -m pytest development-hq/mvp/tests -q`를
재실행했다. 회귀 없음 확인 시에만 다음 단계로 진행했다 — 이 문서
작성 시점까지 어떤 단계도 중단되지 않았다.

| 단계 | 결과 |
|---|---|
| P2-1(상수 추출) 직후 | 36 passed |
| P2-4(docstring 압축) 직후 | 36 passed |
| 최종 재확인(`development-hq/mvp/tests`) | 36 passed in 68.92s |
| 최종 재확인(`core/execution_layer`, 무관 확인) | 55 passed in 0.05s |

P2-2(보류)·P2-3(변경 없음)·P3(판단만)는 코드 변경이 없어 별도
테스트 대상이 아니다.

---

## 1. P2-1: `engine.py` 상수 추출

**판단**: 가치 있음 — 안전하게 추출.

`"claude"` 리터럴 → `ENGINE_CLI`, `timeout=180` → `ENGINE_TIMEOUT_SECONDS`
로 치환했다. 값 자체는 완전히 동일(`"claude"` == `ENGINE_CLI`, `180` ==
`ENGINE_TIMEOUT_SECONDS`)하므로 `subprocess.run()` 호출 behavior는
바뀌지 않는다. `git diff` 확인 결과 리터럴이 이름으로 바뀐 것 외
어떤 인자·순서·값도 변경되지 않았다.

## 2. P2-2: import 관례 검토

**판단**: 보류 — 단순 import 수정으로 끝나지 않는 구조적 문제.

조사 결과:
- `development-hq/`, `development-hq/mvp/` 어디에도 `pyproject.toml`/
  `setup.py`/`setup.cfg`가 없다 — `mvp`는 설치 가능한 패키지가 아니다.
- 패키지 내부(`workflow*.py`, `agents.py`)는 전부 상대 import
  (`from .agents import ...`)로 **이미 일관되어 있다.**
- 진입점(`cli.py`, `tests/*.py`)은 전부 `sys.path.insert(0, ...)` 후
  절대 import(`from mvp.X import Y`)로 **이미 일관되어 있다.**

즉 현재 import 스타일 자체에는 실제 버그나 내부 불일치가 없다 —
발견된 것은 "패키지가 `pyproject.toml` 없이 수동 `sys.path` 조작으로만
동작한다"는 구조적 특성이다. 이를 "고치는" 것은 `pyproject.toml` 추가,
`pip install -e .` 도입, 테스트/CLI 실행 방식 변경까지 이어지는 패키지
구조 변경이며, 이는 import 한두 줄 수정이 아니라 `development-hq/mvp/`
전체의 실행 관례를 바꾸는 작업이다 — 사용자 지시("단순 import 수정으로
끝나지 않으면 구현하지 말고 보류 사유를 기록")에 따라 **구현하지
않는다.**

**보류 사유(기록)**: 실제 버그 없음, 이득(설치 가능한 패키지)이 이번
Refactoring Track의 "안전한 최소 변경" 범위를 넘어선다. 필요해지면
별도 작업으로 분리한다(예: 저장소 전체를 실제로 배포/설치해야 하는
필요가 생길 때).

## 3. P2-3: `agents.py` naming inconsistency 검토

**판단**: 안전한 rename 대상 없음 — 변경하지 않는다.

**조사한 것**: 5개 Agent 함수(`backend_agent_code_review`,
`qa_agent_test_execution`, `requirements_agent_requirement_analysis`,
`design_agent_design`, `backend_agent_code_generation`) 각각의 이름이
`AGENT_CAPABILITY_MAP`/`HELLO_SDLC_CAPABILITY_MAP`의 Agent 표시명·
Capability 키와 실제로 일치하는지, 그리고 **저장소 전체**(`grep -rn`)
에서 각 함수를 호출하는 모든 지점을 확인했다.

**발견 1 — 겉보기 비대칭은 실제 불일치가 아니다**: `requirements_agent`
(복수형)가 `requirement_analysis`(단수형)와 나란히 쓰여 어색해 보이지만,
이는 `AGENT_CAPABILITY_MAP`이 이미 등록한 두 개의 독립적인 정답
(Agent 표시명 "Requirements Agent"=복수, Capability 키
"requirement_analysis"=단수)을 함수 이름이 정확히 반영한 것이다 —
함수 이름을 "고치면" 오히려 Map과 어긋나게 된다.

**발견 2(결정적) — 이름 변경이 안전하지 않다**: 5개 함수 전부
`development-hq/mvp/` 밖의 **3개 project-local Dogfooding 프로젝트**
(`projects/development-hq-devkit/runner.py`, `projects/textkit/runner.py`,
`projects/notekeeper/runner.py`)가 이름으로 직접 import한다
(`from ... import requirements_agent_requirement_analysis` 등). 이
3개는 각각 point-in-time Dogfooding Evidence를 만든 project다 — 이
파일들을 건드리는 것은 "함수 이름을 예쁘게 정리"하는 것 이상으로,
이미 완결된 Evidence 산출에 쓰인 코드를 사후 변경하는 것이 된다.

**결론**: 겉보기 비대칭은 실제 오류가 아니고(Map과 정확히 대응),
설령 "더 나은" 이름이 있다 해도 3개 외부 project의 import를 함께
고쳐야 해서 이번 "안전한 최소 리팩토링" 범위를 벗어난다. **변경하지
않는다.**

## 4. P2-4: `engine.py` 이력형 docstring 압축

**판단**: 압축 가치 있음(2곳), 압축하지 말아야 할 곳도 명확히 구분됨.

| 위치 | `docs/01_mvp/`·`docs/research/`와 중복? | 조치 |
|---|---|---|
| 모듈 docstring 2문단(ENGINE-CONNECT-0001 worktree 실험, MVP-0043 rule-based 삭제) | **예** — `docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md`, `docs/01_mvp/MVP-0043-observation.md`가 전체 기록 보유 | 압축(요약 2문장 + 링크) |
| `call_engine()` docstring MVP-0028 문단(cwd 오염 재현) | **예** — `docs/01_mvp/MVP-0028-observation.md`(114줄)가 전체 재현 기록 보유 | 압축(요약 + 링크). 부수적으로 원문의 부정확한 인용("MVP-0009 Observation"으로 잘못 표시된 것을 실제 근거 문서로 정정) |
| `# 도구 차단 이후 관찰된 두 번째 문제(2026-08-08)` 주석 | **아니오** — `docs/01_mvp/`·`docs/research/`를 전수 검색했으나 이 사건을 별도로 기록한 문서를 찾지 못함(이 주석이 유일한 기록) | **압축하지 않음** — 정보 손실 위험 |
| `STATELESS_CALL_NOTICE`, `DISALLOWED_TOOLS` 값 자체 | 해당 없음(Prompt 텍스트) | **절대 수정하지 않음**(사용자 지시) |

`engine.py`는 87줄 → 79줄로 줄었다. 실제 Prompt 문자열(`STATELESS_CALL_NOTICE`,
`DISALLOWED_TOOLS`)과 `subprocess.run()` 호출 로직은 한 글자도 바뀌지
않았다 — `git diff`로 직접 확인.

---

## 5. P3: `projects/*/agents.py`·`runner.py` 구조적 중복 — Governance 최종 판단

**판단: Architecture/Governance 대상이 맞다. 코드를 수정하지 않는다.
현재(project-local 중복 유지) 상태가 맞다.**

### 5-1. 근거 — 기존 문서가 이미 이 질문에 답했다

- `development-hq/IMPLEMENTATION_RULES.md`: "Registry 구현 금지 —
  Agent-Capability 매핑은 리터럴 딕셔너리 이상으로 발전시키지 않는다."
  project 간 공용 모듈을 만드는 것은 사실상 여러 project가 공유
  조회하는 대상을 만드는 것이며, Registry 일반화의 초기 형태와 같은
  종류의 문제로 이어질 수 있다.
- `docs/research/STOCK-AGENT-SEPARATION-REVIEW-0001.md` §3·§6: Stock
  Team 8개 업무 전부 "독립 실행/재사용 가치가 실제로 확인됨"이라는
  4번째 승격 기준을 충족하지 못해 Agent 승격을 보류했고, 재검토
  조건을 명시적으로 남겼다 — **"Stock Team과 실제로 Capability를
  공유해야 하는 필요가 관찰될 때"**만 재검토한다.
- `docs/research/DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001.md` §3-1:
  Dividend Stock Team(JNJ/KO/PG)도 동일한 논리로 project-local 코드
  복제를 명시적으로 유지하기로 결정했다.
- `EFFICIENCY-AUDIT-0001` §2-2: 실측 결과(중복률 53~98%)를 이미
  확인했고, "지금 통합하면 기존 Governance 판단을 뒤집는 것"이라고
  결론지었다 — 이번 문서가 그 결론을 재확인한다.

### 5-2. RFC → ADC → ADR 대상인가

**그렇다 — 단, 지금 열 조건은 충족되지 않는다.**

`ARCHITECTURE_GOVERNANCE.md`의 ADC 채택 기준(두 조건) 대조:

| 기준 | 충족 여부 |
|---|---|
| (1) 지금 결정하지 않으면 진행 불가 | **아니오** — 10개 Investment project + notekeeper/textkit/development-hq-devkit 전부 project-local 복제로 정상 완주했고, 앞으로도 이 방식으로 계속 진행 가능하다 |
| (2) 결정이 늦어질수록 되돌리는 비용이 매우 큼 | **아니오** — 아직 어떤 공유 코드도 존재하지 않아 되돌릴 대상이 없다 |

**두 조건 모두 미충족 → RFC를 지금 열지 않는다.** 이는 새 판단이
아니라 `STOCK-AGENT-SEPARATION-REVIEW-0001`이 이미 남긴 재검토 조건
("실제 공유 필요가 관찰될 때")이 아직 발생하지 않았다는 사실의
재확인이다.

### 5-3. RFC 필요성 기록(실행하지 않음, 조건만)

향후 다음 중 하나가 **실제로** 관찰되면, 그것이 RFC를 여는 근거가
된다(지금 선제적으로 만들지 않는다):

1. 두 개 이상의 project가 동일한 Agent 함수를 실제로 import해 공유
   코드로 실행하려는 시도가 나타날 때(현재는 매 project가 자기
   `agents.py` 사본만 사용).
2. 5개 Stock 역할 또는 Dividend Stock 고유 역할이 4번째 이상의 새
   Investment project에서도 반복돼, project-local 복제 비용(현재
   ~1,700줄)이 실질적인 유지보수 부담으로 이어지는 사례가 실제로
   보고될 때.
3. Development HQ Platform 자체(`development-hq/mvp/`)가 아니라
   project 계층에 Registry 유사 기능이 필요하다는 압력이 실제로
   나타날 때.

**이번 문서는 위 조건이 충족됐다고 판단하지 않는다 — 셋 다 발생하지
않았다.**

---

## 6. 실제 변경 사항 요약

| 파일 | 변경 |
|---|---|
| `development-hq/mvp/engine.py` | P2-1(상수 추출) + P2-4(docstring 압축) — 유일하게 수정된 코드 파일 |
| `docs/architecture/core/REFACTORING-TRACK-CLOSURE-0001.md` | 이 문서(신규) |

`projects/*/agents.py`·`runner.py`, `development-hq/mvp/agents.py`,
`docs/03_adc/ADC.md`, 그 외 어떤 파일도 수정하지 않았다.

---

## 7. Architecture/Contract 변경 여부

**없음.** Task 순서, Agent-Capability 매핑, Prompt, 반환 dict shape
전부 무변경(P1과 동일 원칙 유지). 새 Kernel/Runtime/Capability 없음.
`docs/03_adc/ADC.md` 미수정.

## 8. Refactoring Track 종료 가능 여부

**종료 가능하다.**

- P1(Characterization Tests → 중복 제거): 완료, 회귀 없음.
- P2-1: 완료. P2-2: 보류(사유 기록). P2-3: 변경 없음(사유 기록).
  P2-4: 완료.
- P3: Governance 판단 완료(RFC 대상이나 지금 열 조건 미충족, 코드
  변경 없음) — 이는 "미완료"가 아니라 **"판단이 곧 이 단계의
  산출물"**이다(사용자 지시: "P3가 Architecture/Governance 대상이면
  코드 수정 금지, 필요한 경우 RFC 필요성만 기록").
- 남은 기술 부채(P2-2 sys.path 관행, P2-3 이름 비대칭, P3 project 간
  중복)는 전부 "지금 손대지 않는 것이 맞다"는 근거와 재검토 조건을
  갖춘 상태로 문서화됐다 — Track을 열어 둘 이유가 없다.

## 9. 다음 단계

사용자가 지시한 대로 **AI Tool Audit**으로 전환한다. 이 Refactoring
Track에서 남긴 재검토 조건(§2, §3, §5-3)은 실제로 그 조건이 발생할 때
별도로 다시 연다 — 지금 후속 작업으로 예약하지 않는다.

---

## Self Review

- Task 순서/Agent-Capability 매핑/Prompt/반환 dict shape을 변경했는가
  — **아니오**.
- Point-in-time Evidence(`docs/01_mvp/`, 각 project의 `EVIDENCE.md`)를
  수정했는가 — **아니오**, 링크만 걸었다.
- 실제 Prompt(`STATELESS_CALL_NOTICE`, `DISALLOWED_TOOLS`, `agents.py`
  각 함수의 `instruction`)를 압축·수정했는가 — **아니오**.
- P3에서 코드를 수정했는가 — **아니오**, 판단만 기록했다.
- 새 RFC/ADC/ADR을 열었는가 — **아니오**, 필요성만 기록했다.
- 각 단계마다 테스트를 실행했는가 — **예**(§0, §4 표 참조 — 모든
  단계에서 36 passed, 회귀 없음).
