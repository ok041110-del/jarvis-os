# ADR-0002: Execution Result Item Schema의 Artifact Standard 반영

| 필드 | 내용 |
|---|---|
| ID | ADR-0002 |
| 제목 | Execution Result 목록 항목의 타입(`list[str]`)을 `ARTIFACT-STANDARD-v1.md`에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/core/execution-layer/ADC-0003-execution-result-item-schema.md` Decision — `list[str]` Accepted (based on current evidence) |
| 관련 RFC | `docs/core/execution-layer/RFC-0003-execution-result-item-schema.md` |
| 관련 ADC | `docs/core/execution-layer/ADC-0003-execution-result-item-schema.md` |
| 선행 ADR | `docs/core/execution-layer/ADR-0001-execution-result-contract.md`(Execution Result의 "형태"를 Baseline에 반영한 선례 — 이 ADR은 그다음 단계인 "항목 타입"을 반영한다) |

이 ADR은 ADC-0003이 이미 내린 결정을 다시 논의하지 않는다. 새로운
철학이나 Architecture를 제안하지 않는다. ADC-0003이 채택한 것 —
"Execution Result 목록의 각 항목은 opaque 문자열(`str`)이다"는
**타입 결정 하나** — 를 `ARTIFACT-STANDARD-v1.md`에 옮기기 위한
**구현 결정**만 기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

ADC-0003이 명시적으로 판단하지 않은 것은 **하나도 Baseline에
반영하지 않는다.**

| 항목 | 근거 |
|---|---|
| 산출물 문자열의 의미론적 종류 구분(파일/로그/텍스트 보고 등) | ADC-0003 "이 ADC가 답하지 않는 것" — Not Accepted된 `list[dict]`가 다뤘을 영역 |
| 목록의 빈 목록 허용 여부, 최소/최대 개수 | ADC-0003 §Next Step — ADR 또는 후속 구현 단계 대상, 이 ADR도 다루지 않는다 |
| Execution Result Builder의 실제 구현 | ADC-0003 §목적, RFC-0003 §Non-goals — 이 ADR도 구현하지 않는다 |
| `list[dict]`(구조화 레코드) 방향 | ADC-0003 Q0에서 Not Accepted로 배제, 재검토 조건 충족 시까지 열어두지 않는다 |
| `call_engine()` 실제 Engine 배선 여부, Execution State 전이 규칙 | ADC-0003 목적 밖, 별도 사안 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md` | "Artifact 6: Execution Result" 절의 `Output`·`Canonical Fields` 행을 `list[str]` 결정으로 구체화, 문서 상단 요약 문구 갱신, 근거 절에 RFC-0003·ADC-0003·ADR-0002 인용 추가 |

그 외 어떤 파일도 변경하지 않는다.

### 2. `ARTIFACT-STANDARD-v1.md` 갱신 내용

#### 2.1 문서 상단 문구 갱신

기존(ADR-0001이 반영한) 문구 뒤에 한 문장을 추가한다.

> 목록 항목의 타입(opaque `str`)은 `ADC-0003-execution-result-item-schema.md`가
> 결정했다. 그 문자열이 의미론적으로 무엇을 나타내는지(파일/로그/
> 텍스트 보고 구분)는 여전히 결정되지 않았다.

#### 2.2 "Artifact 6: Execution Result" 절 갱신

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Output | Execution Result — **형태: 산출물 목록(list)**(ADC-0002 Decision). 구체적 직렬화 형식(`str` 내 목록 표현인지, 다른 타입인지)은 미정(ADC-0002 범위 밖). | Execution Result — **형태: 산출물 목록(list)**(ADC-0002 Decision), **항목 타입: opaque `str`**(ADC-0003 Decision). 목록을 최종적으로 어떤 컨테이너로 감쌀지(`str` 안에 렌더링된 목록인지, 다른 표현인지)는 미정(ADC-0003 범위 밖 — Builder 구현 단계 대상). |
| Canonical Fields | 미정(ADC-0002 범위 밖) — 목록 항목의 타입 스키마는 후속 결정 대상. | 목록 항목의 타입은 `str`(ADC-0003 Decision). 개별 항목이 나타내는 의미(파일/로그/텍스트 보고 구분), 목록의 개수 제한은 여전히 미정(ADC-0003 범위 밖). |

절 말미의 각주는 그대로 유지하고 다음 한 줄을 추가한다.

> 항목 타입(`str`)은 `ADC-0003`이 결정했다. 이 문자열이 무엇을
> 의미하는지는 이 문서가 결정하지 않는다 — `list[dict]`(구조화
> 레코드)는 `ADC-0003` Q0에서 Evidence 부족으로 Not Accepted됐다.

#### 2.3 "근거" 절에 추가

```
- docs/core/execution-layer/RFC-0003-execution-result-item-schema.md
- docs/core/execution-layer/ADC-0003-execution-result-item-schema.md
- docs/core/execution-layer/ADR-0002-execution-result-item-schema.md
```

### 3. `docs/03_adc/ADC.md` 갱신 여부

**갱신하지 않는다.** `ADC-0003`은 Execution Layer 네임스페이스의
ADC이며, `docs/03_adc/ADC.md`는 Jarvis OS(Kernel) 수준 Open Decision
만 관리한다(ADR-0001 §3과 동일한 판단).

### 4. Development HQ · Kernel Architecture 불변 확인

- `development-hq/` 이하 어떤 파일도 변경하지 않는다.
- `core/execution_layer/*/` 이하 소스 코드는 어떤 파일도 변경하지
  않는다 — Builder를 구현하지 않는다.
- `docs/01_architecture/BASELINE.md`(Kernel Architecture Baseline)는
  변경하지 않는다.
- 기존 테스트(39건)는 이번 변경으로 영향받지 않는다(문서만 변경).

### 5. Migration Strategy

1. `ARTIFACT-STANDARD-v1.md` — §2.1~§2.3 반영.
2. 검증:
   - `git status`로 `development-hq/`·`core/`(소스) 이하에 변경이
     없는지 확인.
   - `python3 -m pytest core/execution_layer -q` 기존 테스트가
     그대로 통과하는지 확인(문서만 변경했으므로 결과가 달라지면
     안 된다).
   - `ARTIFACT-STANDARD-v1.md`가 ADC-0003 Decision과 모순되는
     문장을 남기지 않았는지 재확인(§2.2).
3. 커밋 — ADR-0002와 `ARTIFACT-STANDARD-v1.md` 변경을 함께 커밋한다.

---

## Consequences

- `ARTIFACT-STANDARD-v1.md`가 Execution Result 목록 항목의 **타입**
  (`str`)을 처음으로 반영한다 — "Canonical Fields: 미정"이었던 자리가
  한 단계 더 구체화된다.
- 항목이 나타내는 **의미론적 종류(파일/로그/텍스트 보고 구분)는
  여전히 미정**이다 — 이 ADR은 그 미정 상태를 숨기지 않고
  명시적으로 남긴다. 다음에 Consumer가 이 구분을 필요로 한다는
  Evidence가 확보되면, 별도 RFC/ADC/ADR 대상이다.
- Execution Result Builder는 여전히 구현되지 않는다 — 이 ADR은
  코드를 한 줄도 만들지 않는다. 다만 `results: list[str]`이라는
  매개변수 타입은 이제 Governance 절차로 확정됐다 — `IMPL-STOP-0002`
  가 중단됐던 지점(항목 타입 미정)이 해소된다.
- Candidate `list[dict]`(구조화 레코드)는 재검토 조건이 충족되기
  전까지 Not Accepted로 남는다.
- `docs/03_adc/ADC.md`(Kernel Open Decision 목록)는 변경되지 않는다
  — 이 사이클도 ADR-0001과 동일하게 Execution Layer 네임스페이스
  안에서 종결된다.
- 이 ADR은 **승인되었으며**, §2에 정의된 실제 파일 변경이 이 승인에
  따라 실행된다.

## Self Review

- ADC-0003이 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(의미론적 종류 구분, 개수 제한, Builder 구현,
  `list[dict]`, call_engine 배선, State 전이 규칙)은 손대지 않았다.
- Kernel Architecture Baseline(`docs/01_architecture/BASELINE.md`)을
  변경했는가 — **아니오**.
- `docs/03_adc/ADC.md`를 변경했는가 — **아니오**(§3).
- 코드를 작성했는가 — **아니오**.
- Builder를 구현했는가 — **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**. 반영 과정에서
  ADC-0003·RFC-0003이 이미 인지한 것 이상의 새 결정 지점은
  나타나지 않았다.
