# RFC-0017: Multi-Task Result Store/Checkpointer Integrity Boundary (ADC-0016/ADR-0006 후속, Execution Host·Multi-Task와 분리)

**Status**: Proposed (검토 대상, 결정 아님)
**Author**: Claude Code
**대상**: `docs/architecture/baseline/BASELINE.md` §16.4(Multi-Task, Accept
Scoped·Conditional) 자체가 아니라, §16.4가 Conditional로 이월한 조건 —
Data/Artifact Isolation — 아래에서 **아직 다뤄지지 않은 하위 질문 하나**를
연다.
**Evidence**: `hqs/investment/checkpoint.py`(`Checkpointer`, `run_step`),
`hqs/investment/teams/{stock,etf,dividend_stock}_team.py`(Wave1/Wave2
`ThreadPoolExecutor` 실행), `hqs/investment/tests/test_checkpoint.py`,
`hqs/investment/dogfooding/pg-hq-verify/EVIDENCE.md`(콘텐츠 레벨 실패
4회째 재현, 수동 복구),
`hqs/investment/dogfooding/aapl-hq-verify/EVIDENCE.md`(정상 동시 실행
실측), `docs/architecture/core/RFC-0016-multi-task-minimal-responsibility.md`
§4·§5, `docs/architecture/core/ADC-0016-multi-task-minimal-responsibility.md`
Q4, `docs/architecture/core/ADR-0006-multi-task-minimal-responsibility-baseline.md`.
새로운 실험을 만들지 않는다 — 이미 `main`에 존재하는 실제 Production
Code(`hqs/investment/`)와 그 실행 산출물(Dogfooding Evidence)만 근거로
삼는다.

> 본 RFC는 Checkpointer/Result Store에 새 Component나 Interface를
> 제안하지 않는다. Execution Host(§16.3)와 Multi-Task(§16.4)가 이미
> Accept한 책임(동시 시작·대기·수집, 실패 격리)은 변경하지 않는다.
> 저장 전 검증·Resume 재검증의 **구현 방법**을 설계하지 않으며,
> Scheduler/우선순위/Workflow orchestration/§6 넓은 Runtime은 다루지
> 않는다. Production Code(`hqs/`, `core/`, `dashboard/`)는 수정하지
> 않는다.

## 0. 이 RFC가 열린 이유

`ADC-0016`은 Multi-Task 책임을 Accept하면서 Data/Artifact Isolation을
**최소 안전조건**으로 명시했다(§Q4) — "동시 실행되는 각 Task가 서로
다른 파일/Artifact 이름공간에 쓰거나, 아무것도 쓰지 않는다"는 것이
사전 확인된 조합에만 이 Accept가 적용된다. `ADR-0006`이 Baseline에
반영한 §16.4도 이 조건을 그대로 옮겼다(§Decision 조건 3).

`workflow_0009.py`(RFC-0016의 유일한 근거)는 파일을 전혀 쓰지 않아 이
조건을 검증할 기회 자체가 없었다. 이후 별도 조사(READ-ONLY, Production
Code 무수정)로 `hqs/investment/`의 세 Team(`stock_team.py`,
`etf_team.py`, `dividend_stock_team.py`)이 실제로 파일을 쓰는
Multi-Task 사례라는 것이 관찰됐다 — Wave1(5~7개 독립 Analyst Task)과
Wave2(Bull/Bear)를 `ThreadPoolExecutor`로 동시 실행하며, 각 Task가
`Checkpointer.save()`를 통해 `checkpoints/{step}.md`와 공유
`checkpoints/manifest.json`을 쓴다.

이 조사에서 확인된 것은 두 갈래로 갈린다.

1. §4가 나열했던 위험 중 **파일 덮어쓰기**와 **Git 충돌**은 이 사례에서
   관찰되지 않았다 — 각 Task는 서로 다른 파일명을 쓰고, Git 작업을
   전혀 하지 않는다(§2).
2. 그러나 §4가 나열하지 않았던 종류의 실제 결함이 재현됐다 —
   `pg-hq-verify` Dogfooding에서, 콘텐츠 레벨 실패(API 오류 메시지)가
   정상 산출물처럼 `synthesis.md`에 체크포인트됐고, 이후 재실행
   (Resume)이 이 손상된 결과를 "이미 완료됨"으로 판단해 그대로
   재사용했다 — 사람이 `manifest.json`을 수동 편집해야 복구됐다(§3).

이 RFC는 이 두 번째 관찰이 가리키는 좁은 질문 하나만 연다 — Multi-Task가
공유하는 Result Store(Checkpointer)에, **저장되는 결과의 유효성·무결성을
보장하는 책임이 별도로 필요한가**.

## 1. Problem Statement

`hqs/investment/checkpoint.py`의 `run_step()`은 다음과 같다.

```python
def run_step(cp: Checkpointer, step: str, fn, *args) -> str:
    if cp.has(step):
        return cp.load(step)
    ...
    output = fn(*args)
    ...
    if _is_known_content_failure(output):
        raise ContentFailureError(...)
    cp.save(step, output, input_len, elapsed)
    return output
```

`_is_known_content_failure()`는 알려진 시그니처 하나("API Error:"로
시작)만 검사한다. `pg-hq-verify/EVIDENCE.md`가 기록한 실제 재현은 이
검사를 통과한 실패였다 — Engine이 반환한 오류 문자열이 그 시그니처와
정확히 일치하지 않아 `cp.save()`가 그대로 실행됐고, `synthesis.md`와
`manifest.json`의 `completed_steps`에 `"synthesis"`가 정상 완료로
기록됐다. 이후 Final Report Writer가 이 손상된 입력을 그대로 받았고,
스스로 오류를 감지해 우회했지만 최종 산출물 품질이 저하됐다(§QUALITY
참조, 목표 단어 수 초과·핵심 수치 2건 누락).

재실행(Resume) 경로에서는 더 뚜렷하다 — `cp.has(step)`은 `manifest.json`
의 `completed_steps` 목록만 확인할 뿐, 그 안에 기록된 산출물이 실제로
유효한지는 검증하지 않는다. 그 결과 손상된 `synthesis.md`가 있는 채로
파이프라인을 재실행해도 `run_step`은 `cp.load("synthesis")`로 손상된
값을 그대로 반환한다 — 복구를 위해 사람이 `checkpoints/manifest.json`
에서 `synthesis`/`final_report` 두 항목을 수동으로 지우고 해당 `.md`
파일을 삭제해야 했다.

이 상황은 RFC-0016 §4가 나열한 5개 위험(파일 덮어쓰기, Artifact/Result
충돌, 공유 상태, Git 충돌, Retry 충돌) 중 어느 것과도 정확히 일치하지
않는다 — "저장 자체가 경쟁 상태로 깨지는" 문제가 아니라, **"저장된 것이
유효한지 아무도 확인하지 않는"** 문제다. `_save_manifest_locked()`의
`threading.Lock`은 동시 쓰기의 순서만 보장할 뿐, 저장되는 내용의
정합성은 전혀 보장하지 않는다.

## 2. 관찰된 것과 관찰되지 않은 것의 구분

이 RFC는 실제로 재현된 것과 재현되지 않은 것을 섞지 않는다.

| 위험(RFC-0016 §4 분류) | 이 사례(`hqs/investment/`)에서 관찰됐는가 | Evidence |
|---|---|---|
| 파일 덮어쓰기 | **아니오** — 각 Task는 `step` 문자열(dict key)로 고정된 서로 다른 파일명(`{step}.md`)만 쓴다. 같은 wave 안에서 파일명이 겹치는 조합은 세 Team 어디에도 없다 | `stock_team.py`/`etf_team.py`/`dividend_stock_team.py`의 `wave1_jobs`/`wave2_jobs` dict key 전수 확인 |
| Artifact/Result 충돌(공유 저장소 쓰기 경쟁) | **관찰됐으나 이미 완화돼 있다** — `manifest.json`은 같은 wave의 여러 Worker Thread가 공유하지만, `_save_manifest_locked()`가 `threading.Lock`으로 직렬화한다 | `checkpoint.py:35-39`, `aapl-hq-verify/checkpoints/manifest.json`(완료 순서가 dict 정의 순서와 다름 — 실제 동시 실행이면서도 manifest는 정상 구조 유지) |
| 공유 상태(프로세스 전역 변수 등) | **아니오** — `Checkpointer` 인스턴스는 `run()` 호출마다 새로 생성되고, 그 안의 Lock도 그 인스턴스 생애주기에 한정된다. 프로세스 전역 가변 상태는 없다 | `checkpoint.py:22-27`(`__init__`), 세 Team `run()` 함수 각각 `cp = Checkpointer(issue_dir)`로 매번 신규 생성 |
| Git 충돌 | **아니오** — `hqs/investment/` 전체에 git 명령·저장소 조작 코드가 없다 | `hqs/investment/*.py`, `hqs/investment/teams/*.py` 전수 grep, 매치 0건 |
| Retry 충돌(재시도가 이전 성공 결과를 훼손) | **관찰됐다 — 그러나 RFC-0016 §4-5가 예상한 방향과 반대다** | 아래 §3 |

§4-1(파일 덮어쓰기)·§4-4(Git 충돌)는 이 사례에서 실제 위험으로
드러나지 않았다 — 이 RFC는 이를 억지로 문제로 만들지 않는다.
§4-3(공유 상태)도 마찬가지다. §4-2(Artifact/Result 충돌)는 실제로
발생할 수 있는 지점이었으나 `threading.Lock`으로 이미 완화돼 있다는
것이 실측으로 확인됐다 — 이 RFC가 새로 열 질문이 아니다.

## 3. 실제 재현된 것 — Retry/Resume이 손상을 "보존"하는 방향

RFC-0016 §4-5는 Retry 충돌을 이렇게 서술했다: "두 Task 중 하나만
실패해 재시도할 때, 이미 성공한 다른 Task의 결과를 보존하면서 실패한
Task만 재실행하는 것이 필요하다." 이 서술은 **재시도가 성공한 결과를
잘못 덮어쓸 위험**을 가정한다.

`pg-hq-verify`에서 실제로 관찰된 것은 정반대다 — Resume은 성공한
결과를 덮어쓰지 않는다(오히려 그것이 설계 의도, `test_checkpoint.py`의
`test_resume_skips_second_engine_call`이 이를 검증한다). 문제는
**"완료됨"으로 잘못 기록된 실패 결과를 Resume이 성공으로 오인해
그대로 보존·재사용**하는 방향이다:

1. `run_step()`은 알려진 시그니처(`"API Error:"`)만 실패로 판정한다.
   이 시그니처와 정확히 일치하지 않는 콘텐츠 레벨 실패는 `_is_known_
   content_failure()`를 통과해 `cp.save()`로 저장된다.
2. 저장된 순간 `manifest.json["completed_steps"]`에 해당 `step`이
   기록되고, 이후 어떤 재실행(같은 `issue_dir`로 새 `Checkpointer`
   생성)도 `cp.has(step)`이 `True`를 반환해 `cp.load(step)`으로 손상된
   값을 그대로 돌려준다 — Engine을 다시 호출하지 않는다(이것이 Resume의
   정상 동작 자체이며, 정상 결과에 대해서는 옳다).
3. `pg-hq-verify`는 이 상태에서 하위 Task(Final Report Writer)가 손상된
   입력을 받아 스스로 우회했지만 품질이 저하됐고, 최종적으로는 사람이
   `manifest.json`에서 `completed_steps` 항목을 수동으로 제거하고 해당
   `.md` 파일을 삭제해야 정상 재실행됐다.

`test_checkpoint.py`의 문서화 주석("범위 밖: 재시도/알림/동시성")이
이 공백을 스스로 인정한다 — 저장 전 콘텐츠 검증의 커버리지(알려진
시그니처 1건)와 Resume의 재검증 부재는 테스트로도 다뤄진 적이 없다.

**중요한 구분**: 이 결함은 Wave1/Wave2의 **동시 실행 자체**(여러
Worker Thread가 동시에 시작·대기·수집되는 조율)에서 발생하지 않는다 —
문제가 재현된 지점(Synthesis, Wave3)은 순차 실행 구간이다. 그러나
`run_step()`/`Checkpointer`는 Wave1·Wave2(동시)와 Wave3·Wave4(순차)
전 구간에서 **동일한 컴포넌트**를 통해 저장·Resume이 이뤄진다 — 따라서
이 결함은 Multi-Task 전용 위험이 아니라, Multi-Task가 의존하는 Result
Store 컴포넌트 자체의 무결성 공백이며, 그 공백은 Multi-Task가 이 Result
Store를 공유하는 순간 Multi-Task의 실제 위험이 된다(동시 실행 중인 여러
Task 중 하나가 손상된 결과를 저장하면, 그 손상은 동시성과 무관하게
이후 모든 Resume에 전파된다).

## 4. Execution Host·Multi-Task 기존 책임과의 경계

이 RFC는 §16.3(Execution Host)·§16.4(Multi-Task)가 이미 Accept한 것을
재론하지 않는다.

| | Execution Host(§16.3) | Multi-Task(§16.4) | 이 RFC가 여는 질문 |
|---|---|---|---|
| 다루는 문제 | 단일 실행 단위의 Execution Isolation | 복수 독립 Task의 동시 시작·대기·수집(Coordination), 실패 격리 | 저장된 결과의 유효성·무결성을 누가·어떻게 보장하는가(Integrity) |
| `checkpoint.py`와의 관계 | 무관 — `call_engine()`은 이미 Engine 자체가 격리된 별도 프로세스(`subprocess.run`, Investment HQ는 `engine_client.py`)로 호출됨 | Wave1/Wave2의 동시 시작·대기는 이미 Accept(Scoped) 범위 그대로 — 이 RFC가 다시 열지 않음 | `run_step()`이 저장 여부를 판단하는 기준(`_is_known_content_failure`)과 `Checkpointer.has()`가 재사용 여부를 판단하는 기준(존재 여부만) — 이 두 판단 지점 |
| 결정 상태 | 기확정, 무변경 | 기확정(Accept, Scoped·Conditional), 무변경 | Open — 이 RFC가 처음 연다 |

Multi-Task의 실패 격리(§16.4 "포함") — 한 Task의 실패가 다른 Task의
진행에 영향을 주지 않는다는 것 — 는 이 RFC로 전혀 흔들리지 않는다.
`pg-hq-verify`에서도 실패한 것은 저장 판정 로직이지, Task 간 격리가
아니다(다른 Task들은 영향받지 않고 정상 완료됐다).

## 5. Boundary Question

이 RFC는 답을 제시하지 않는다. 다음 좁은 질문만 제기한다.

**Multi-Task가 공유하는 Result Store(Checkpointer)에, 저장되는 결과의
유효성·무결성을 보장하는 책임을 Execution Host(§16.3)·Multi-Task
(§16.4)와 별개의 Kernel Concept 또는 그 두 책임에 속한 하위 의무로
Accept하는가?**

| 후보 | 근거 | 근거 성격 |
|---|---|---|
| Accept(최소 범위) | `pg-hq-verify` 4회째 재현(누적, `efa-2026-08` 포함) — 이미 여러 차례 관찰된 동일 실패 패턴, 수동 복구가 반복적으로 필요했다는 실측 | 실제 Production 실행 Evidence, 그러나 원인은 항상 같은 근본 원인(프록시/자체 서명 인증서)에서 비롯됨 |
| Not Accepted(현행 유지) | 관찰된 실패는 Engine 호출 계층(프록시/인증서)의 문제이지 Result Store 설계의 문제가 아니라고 볼 여지가 있다 — `_is_known_content_failure()`의 시그니처만 넓히면 되는 국소 수정일 수 있다 | 원인의 위치(Engine 호출 신뢰성 vs. Result Store 검증 책임)가 아직 명확히 분리되지 않음 |

이 RFC는 이 중 어느 쪽이 맞는지 판단하지 않는다. 판단은 후속 ADC로
위임한다.

### 이 Boundary Question이 명시적으로 제외하는 것

- **저장 전 검증의 구현 방법**: 콘텐츠 실패 시그니처를 어떻게 넓힐지,
  스키마 검증을 도입할지, 별도 검증 단계를 둘지는 다루지 않는다 —
  질문 후보로만 남긴다(§6).
- **Resume 재검증의 구현 방법**: `cp.has()`가 존재 여부 대신 무엇을
  추가로 확인해야 하는지는 다루지 않는다 — 질문 후보로만 남긴다(§6).
- **Retry/Resume의 책임 경계 자체**: 이 실패를 감지·복구하는 책임이
  Result Store(Checkpointer)에 속하는지, 호출자(Team `run()`)에
  속하는지, 아니면 별도 책임인지는 이 RFC가 정하지 않는다 — 별도 판단
  대상으로 남긴다(§7).
- **새 Component/Interface**: `Checkpointer`를 대체하거나 확장하는
  새 클래스·함수 시그니처를 제안하지 않는다.
- **Execution Host·Multi-Task의 범위 확장**: §16.3·§16.4의 기존
  Accept는 전혀 재론하지 않는다(§4).
- **Scheduler, 우선순위, Workflow orchestration**: 다루지 않는다.
- **§6 넓은 Runtime 확장**: 다루지 않는다.
- **근본 원인(프록시/자체 서명 인증서) 자체의 해결**: Engine 호출
  계층의 네트워크/인증서 문제 해결은 이 RFC의 대상이 아니다 — 이 RFC는
  그 실패가 Result Store에 어떻게 반영되는지만 다룬다.
- **구현 전략**: 무엇을 쓸지는 다루지 않는다.

## 6. 저장 전 검증·Resume 재검증 — 질문 후보로만 제시

§3이 보여준 두 판단 지점을 후속 ADC가 검토할 수 있도록 **질문
형태로만** 남긴다 — 이 RFC는 어느 쪽도 설계하지 않는다.

1. **저장 전 검증**: `run_step()`이 `cp.save()`를 호출하기 전에 결과의
   유효성을 판단하는 기준을, 지금처럼 알려진 실패 시그니처 목록으로
   유지할지, 아니면 다른 판단 방식(예: 최소 길이, 필수 마커 존재 등)을
   추가로 요구할지는 미결이다.
2. **Resume 재검증**: `Checkpointer.has(step)`이 지금처럼 "완료 목록에
   있는가"만 확인할지, 아니면 재개 시점에 저장된 콘텐츠를 다시 검사할지
   (그 경우 비용·의미가 어떻게 달라지는지 포함)는 미결이다.

두 질문 모두 "그렇게 해야 한다"는 결론을 이 RFC가 내리지 않는다 — 후속
ADC가 Evidence(이 RFC가 인용한 `pg-hq-verify` 등)를 근거로 판단할
후보로만 제시한다.

## 7. Retry/Resume의 책임 경계 — 별도 판단 대상

`pg-hq-verify`의 실제 복구는 사람이 수행했다(`manifest.json` 수동
편집, 파일 삭제). 이것이 드러내는 것은 "손상된 결과를 감지한 이후,
누가 그것을 고칠 책임을 지는가"라는 질문이며, 이는 §6의 "저장 전/Resume
시점의 판단 기준" 질문과는 다른 층위다 — 판단 기준이 아무리 정교해져도,
감지된 실패를 재시도할지·사람에게 알릴지·자동 복구를 시도할지 결정하는
책임의 소재는 별도로 남는다.

이 RFC는 이 책임 경계(Result Store 자신이 재시도까지 수행하는지,
호출자인 Team `run()`이 수행하는지, 혹은 그 경계 자체가 아직 Kernel
Concept으로 필요하지 않은지)를 **판단하지 않는다** — 후속 ADC가 §5의
Boundary Question에 대한 답과 별개로 다뤄야 할 판단 대상으로만
명시한다.

## Out of Scope

- Multi-Task Result Store Integrity 책임의 존재 여부 실제 판단(§5에
  위임).
- 저장 전 검증·Resume 재검증의 구체적 구현 방법(§6).
- Retry/Resume의 책임 경계 자체의 판단(§7).
- Engine 호출 계층(프록시/인증서)의 근본 원인 해결.
- Execution Host(§16.3)·Multi-Task(§16.4)의 범위 재론 또는 확장.
- Scheduler, 우선순위, Workflow orchestration 설계.
- `BASELINE.md` §6 "Runtime"의 넓은 정의 검증 또는 수정.
- 새 Component/Interface 확정.
- `docs/decisions/adc/ADC.md`의 ADC-02 항목 수정.
- Production Code(`hqs/`, `core/`, `dashboard/`) 수정 — 전혀 하지
  않는다.
- 새로운 실험 — `hqs/investment/`의 이미 존재하는 Production Code와
  실행 Evidence(Dogfooding)만 근거로 삼는다.

## Non-goals

- 이 RFC는 Multi-Task Result Store Integrity 책임의 존재를 확정하지
  않는다.
- 이 RFC는 새 실험을 수행하지 않는다.
- 이 RFC는 Architecture Baseline을 변경하지 않는다.
- 이 RFC는 저장 전 검증·Resume 재검증의 구현 방법을 설계하지 않는다.
- 이 RFC는 Retry/Resume의 책임 경계를 확정하지 않는다.
- 이 RFC는 Execution Host·Multi-Task의 기존 범위를 넓히지 않는다.
- 이 RFC는 새 Component·Interface를 제안하지 않는다.
- 이 RFC는 ADC, ADR 문서를 작성하지 않는다.
- 이 RFC는 §5의 Boundary Question에 답하지 않는다.

## Next Step

후속 ADC(신설 예정, 이 RFC의 후속)에서 다음을 판단하도록 제안한다.

1. §5 Boundary Question(Result Store 무결성 보장 책임의 존재 여부)을
   지금 Evidence(`pg-hq-verify` 4회째 재현 등)로 Accept할 수 있는지,
   아니면 근본 원인이 Engine 호출 계층(프록시/인증서)에 있다고 보아
   Result Store 설계 문제로 격상하지 않을지.
2. Accept된다면, §6이 나열한 두 질문(저장 전 검증 기준, Resume 재검증
   여부) 중 어느 쪽을 우선 다룰지, 아니면 둘 다 후속 구현 단계로
   넘길지.
3. Accept된다면, §7의 Retry/Resume 책임 경계(Result Store 자신이
   담당하는지, 호출자가 담당하는지)를 같은 ADC에서 판단할지, 별도
   RFC로 다시 좁혀 열지.
4. Not Accepted라면, `_is_known_content_failure()`의 시그니처를 넓히는
   것과 같은 국소 수정으로 충분한지, 아니면 이 좁은 질문 자체를
   보류할지.

이 RFC 자체는 그 판단을 내리지 않는다. Architecture Governance 절차
(RFC → ADC → ADR → Baseline Update)를 통해 별도로 판단한다.

## Self Review

- Evidence만 사용했는가 — **Pass**. `hqs/investment/checkpoint.py`,
  세 Team 파일, `test_checkpoint.py`, `pg-hq-verify`/`aapl-hq-verify`
  EVIDENCE.md, RFC-0016/ADC-0016/ADR-0006만 인용했다. 새 실험은
  수행하지 않았다.
- 근거를 Investment HQ 실제 실행과 `pg-hq-verify` 재현으로 한정했는가
  — **Pass**(Evidence 목록, §1·§3).
- 질문을 "저장 결과의 유효성·무결성 보장 책임" 하나로 좁혔는가 —
  **Pass**(§5, 단일 Boundary Question).
- Execution Host·Multi-Task의 기존 책임을 변경했는가 — **아니오**
  (§4가 명시적으로 분리·유지).
- 관찰되지 않은 위험(파일 덮어쓰기, Git 충돌)을 문제로 과장했는가 —
  **아니오**(§2, 표로 명시적 구분).
- 저장 전 검증·Resume 재검증을 구현 방법까지 결정했는가 — **아니오**
  (§6, 질문 후보로만 제시).
- Retry/Resume의 책임 경계를 판단했는가 — **아니오**(§7, 별도 판단
  대상으로 명시).
- 새 Component/Interface를 확정했는가 — **아니오**(§Out of Scope).
- §6 Runtime/Scheduler/Workflow orchestration을 Out of Scope로
  유지했는가 — **Pass**(§Out of Scope).
- Production Code를 수정했는가 — **아니오**.
- ADC, ADR 문서를 작성했는가 — **아니오**. RFC 문서 하나만 작성했다.
