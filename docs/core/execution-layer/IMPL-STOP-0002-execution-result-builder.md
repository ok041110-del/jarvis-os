# IMPL-STOP-0002: Execution Result Builder 구현 중단 기록

**문서 성격**: 구현 중단 기록(Observation). **Architecture 문서가
아니다.**
**대상**: Execution Result Builder(`core/execution_layer/mvp_0006`,
미생성)
**선행 Governance**: `RFC-0002` → `ADC-0002` → `ADR-0001` →
`ARTIFACT-STANDARD-v1.md` Baseline Update (PR #10, main에 병합됨)
**결과**: **Stop Trigger 2 재발동. 코드를 작성하지 않았다.**

이 문서는 Architecture를 설계하지 않는다. Execution Result 목록
항목의 Contract를 정하지 않는다. RFC·ADC·ADR을 작성하지 않는다.
Baseline을 수정하지 않는다. **중단 지점과 Evidence만 기록한다.**

---

# 1. 중단 지점

**Builder 함수 시그니처를 정의하는 단계, 첫 매개변수(산출물 목록)의
항목 타입을 결정해야 하는 지점에서 중단했다.**

기존 5개 Builder 패턴(`ARTIFACT-STANDARD-v1.md` "공통 패턴")을 그대로
따르면 다음과 같은 형태가 된다.

```python
def build_execution_result(
    execution_state: str, *, result_id: str, produced_at: str, results: ???
) -> str:
    ...
```

`execution_state`(Input, `str`), `result_id`/`produced_at`
(caller-supplied identity/time, 기존 5개 Builder와 동일 패턴)까지는
결정할 근거가 있다. **`results`의 타입을 무엇으로 할지는 결정할
근거가 없다.**

# 2. Evidence

## E-1. ADC-0002가 "형태"만 결정하고 "항목 스키마"는 명시적으로 배제했다

`ADC-0002-execution-result-contract.md` §목적 "이 ADC가 답하지 않는
것":

> *"채택된 후보의 실제 필드 구성(이름, 타입, 개수). 산출물 항목의
> 타입 스키마(파일/로그/텍스트 보고를 어떻게 구분하는지)."*

`ADR-0001-execution-result-contract.md` §Out of Scope:

> *"목록 항목의 실제 필드 스키마(타입, 이름, 개수 제한) — ADC-0002
> "이 ADC가 답하지 않는 것" — Contract 상세는 후속 구현/추가 ADR
> 대상."*

## E-2. Baseline이 이미 "미정"으로 명시했다

`ARTIFACT-STANDARD-v1.md` "Artifact 6: Execution Result" 절:

> *Canonical Fields | 미정(ADC-0002 범위 밖) — 목록 항목의 타입
> 스키마는 후속 결정 대상.*

## E-3. `results`의 최소 후보조차 전부 새 결정이다

| 후보 | 무엇을 결정하게 되는가 |
|---|---|
| `list[str]`(opaque, caller가 이미 직렬화한 문자열) | "항목은 문자열이다"라는 최소 스키마 결정 — ADC-0002가 배제한 "실제 필드 구성"의 일부 |
| `list[dict]`(type/source/content 등 구조화 레코드) | 명백한 새 스키마 결정 — "파일/로그/텍스트 보고를 어떻게 구분하는지"(E-1) 그 자체 |
| 빈 목록 허용 여부, 최소/최대 개수 | ADC-0002·RFC-0002 어디에도 관찰되지 않은 검증 규칙 |

세 후보 모두 ADC-0002·ARTIFACT-STANDARD-v1.md·ADR-0001 어디에서도
결정된 바 없다. 어느 것을 선택해도 이번 작업이 스스로 새 Contract
결정을 내리는 것이 된다.

## E-4. 기존 5개 Builder의 선례가 이 지점에 적용되지 않는다

5개 Builder 전부 "Wrap, not rewrite" — Input Artifact 본문을
해석하지 않고 caller-supplied 메타데이터만 덧붙인다. 그러나
Execution Result의 "산출물 목록"은 기존 5개 Artifact Chain
(Execution Request → ... → Execution State) 어디에도 존재하지 않는
새 데이터다 — Engine이 실제로 만들어낸 산출물(`ENGINE-INTEGRATION-
0001~0003`이 관찰한 "여러 개별 산출물")이며, 기존 체인의 Input에
해당하는 선례가 없다. 이는 `IMPL-STOP-0001` §2 E-1이 이미 확인한
"content 필드 0건" 사실과 같은 구조의 반복이다 — 다만 이번에는
"형태(목록)"까지는 이미 결정되어 있다는 점이 다르다.

---

# 3. Stop Trigger 대조

| # | Trigger | 발동 |
|---|---|---|
| 1 | 새로운 Architecture 결정이 필요해지는 경우 | **발동** — §2 E-3 (results 타입 후보 3개 전부 새 결정) |
| **2** | **기존 Contract만으로 결정할 수 없는 경우** | **발동 — 주 사유.** E-1·E-2·E-3 |
| 3 | 새 Registry/Gateway/Scheduler/Runtime을 요구하는 경우 | 미발동 |
| 4~6 | (코드 미작성으로 발생할 수 없음) | 미발동 |

**IMPL-STOP-0001과의 차이**: IMPL-STOP-0001은 "형태(shape)" 자체가
미정이었다. 이번은 RFC-0002 → ADC-0002 → ADR-0001로 형태(목록)까지
Governance 절차를 거쳐 결정됐다는 점에서 진전이 있다. 그러나 그
다음 단계인 "항목 스키마"에서 동일한 종류의 Trigger 2가 재발동했다
— Contract 결정이 한 단계 더 구체화됐을 뿐, 구현 가능한 지점까지
도달하지는 못했다.

---

# 4. 이번 작업에서 실제로 한 것 / 하지 않은 것

- `git checkout -B claude/execution-result-builder origin/main` —
  최신 main(PR #10 병합 반영)에서 새 브랜치를 만들었다.
- `core/execution_layer/mvp_0006/` 디렉토리를 만들지 않았다.
- Builder 함수를 작성하지 않았다 — 시그니처 초안만 검토(§1)했고
  코드로 저장하지 않았다.
- 테스트를 작성하지 않았다.
- `ARTIFACT-STANDARD-v1.md`, ADC-0002, ADR-0001을 수정하지 않았다.
- 새 후보(§2 E-3의 3개)를 임의로 선택하지 않았다.

---

# 5. 이 중단이 뜻하는 것

Execution Result의 Governance 사이클(RFC-0002 → ADC-0002 → ADR-0001)
은 "형태" 질문에는 답했다. 이번 시도는 그 답이 구현에 필요한
최소 결정(항목 스키마)까지 자동으로 이어지지 않는다는 사실을
확인했다 — **형태 결정과 항목 스키마 결정은 서로 다른 결정이며,
전자가 후자를 함의하지 않는다.**

**이 문서는 그 다음에 무엇을 해야 하는지 판단하지 않는다.** 항목
스키마를 결정하려면 별도 RFC(Observation Count 요건 충족 여부 포함)
가 필요한지, 아니면 이번 1회 관찰만으로 ADC를 열 수 있는지는 이
문서의 판단 범위가 아니다.

---

## Self Review

- 코드를 작성했는가 — **아니오**. `core/execution_layer/mvp_0006`은
  생성되지 않았다.
- Architecture를 설계했는가 — **아니오**. §2 E-3은 후보를
  **나열**했을 뿐 어느 것도 선택하지 않았다.
- 항목 스키마를 정했는가 — **아니오**.
- ADC-0002/ADR-0001의 결정(형태=목록)을 뒤집었는가 — **아니오**.
  그 결정은 그대로 유지하며, 그 다음 단계에서 막혔다는 사실만
  기록한다.
- 새 RFC/ADC/ADR을 작성했는가 — **아니오**.
- Baseline을 수정했는가 — **아니오**.
- 억지로 구현을 완성했는가 — **아니오**. 시그니처 초안을 검토한
  시점에 중단했다.
