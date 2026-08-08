# ADR-0001: Execution Result Contract의 Artifact Standard 반영

| 필드 | 내용 |
|---|---|
| ID | ADR-0001 |
| 제목 | Execution Result(여섯 번째 Artifact)의 Contract 형태(목록형)를 `ARTIFACT-STANDARD-v1.md`에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/core/execution-layer/ADC-0002-execution-result-contract.md` Decision — Candidate 2(산출물 목록) Accepted (based on current evidence) |
| 관련 RFC | `docs/core/execution-layer/RFC-0002-execution-result-contract.md` |
| 관련 ADC | `docs/core/execution-layer/ADC-0002-execution-result-contract.md` |
| 선행 ADR | `docs/core/execution-layer/RFC-0001-artifact-drift-boundary.md` → `ADC-0001-artifact-drift-boundary.md`("No ADR Required" — 이 ADR과 무관한 별개 판단) |

이 ADR은 ADC-0002가 이미 내린 결정을 다시 논의하지 않는다. 새로운
철학이나 Architecture를 제안하지 않는다. ADC-0002가 채택한 것 —
"Execution Result는 산출물 목록(list)을 담는다"는 **형태(shape)
결정 하나** — 를 `ARTIFACT-STANDARD-v1.md`에 옮기기 위한 **구현
결정**만 기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

ADC-0002가 명시적으로 판단하지 않은 것은 **하나도 Baseline에
반영하지 않는다.**

| 항목 | 근거 |
|---|---|
| 목록 항목의 실제 필드 스키마(타입, 이름, 개수 제한) | ADC-0002 "이 ADC가 답하지 않는 것" — Contract 상세는 후속 구현/추가 ADR 대상 |
| 산출물 항목의 타입 분류(파일/로그/텍스트 보고 구분 방식) | 동일 |
| Execution Result Builder의 실제 구현 | ADC-0002 §목적, RFC-0002 §Non-goals — 이 ADR도 구현하지 않는다 |
| Candidate 3이 요구했던 Memory 영역(저장 위치) 설계 | ADC-0002 Q1에서 Not Accepted로 배제, Defer 상태 유지 |
| `call_engine()` 실제 Engine 배선 여부 | ADC-0002 목적 밖, 별도 사안(`ENGINE-CONNECT-0001`) |
| Execution State의 상태 전이 규칙 | ADC-0002 목적 밖, 별도 사안 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/core/execution-layer/ARTIFACT-STANDARD-v1.md` | Artifact Chain 도식의 6번째 화살표 갱신, "Artifact 6: Execution Result" 절 신설(형태만, 필드 미정), 문서 상단 Boundary 문구를 ADC-0002 결정과 일치하도록 정정, Boundary/근거 절에 ADR-0001 인용 추가 |

그 외 어떤 파일도 변경하지 않는다. `docs/01_architecture/BASELINE.md`
(Kernel Architecture Baseline)는 이 ADR의 대상이 아니다 —
`ARTIFACT-STANDARD-v1.md`는 Execution Layer 자체의 Baseline이며
Kernel Architecture Baseline과 별개 문서다(RFC-0001·ADC-0001 선례와
동일한 네임스페이스 구분).

### 2. `ARTIFACT-STANDARD-v1.md` 갱신 내용

#### 2.1 문서 상단 Boundary 문구 정정

기존 문구("Execution Result를 설계하지 않는다... 이 문서는 그 자리를
예고만 할 뿐 설계하지 않는다")는 ADC-0002 이전 상태를 기술한 것이며,
지금은 부정확하다. 다음으로 교체한다.

> Execution Result(여섯 번째 Artifact)의 **형태(shape)** 는
> `ADC-0002-execution-result-contract.md`가 결정했다 — 산출물
> 목록(list)이다. 이 문서는 그 형태만 반영하며, 목록 항목의 필드
> 스키마는 여전히 설계하지 않는다.

#### 2.2 Artifact Chain 도식 갱신

```
            ▼  ExecutionStateBuilder        (MVP-0005)
Execution State
            │
            ▼  (미구현 Builder — ADC-0002: 형태는 산출물 목록)
Execution Result
```

기존 `▼ (미구현 — Execution Result, 이 문서의 범위 밖)`을 위와 같이
교체한다 — "범위 밖"이 아니라 "형태는 결정됨, Builder는 미구현"으로
정정한다.

#### 2.3 "Artifact 6: Execution Result" 절 신설

기존 Artifact 1~5와 같은 표 형식을 쓰되, ADC-0002가 실제로 결정한
것만 채운다. 결정되지 않은 칸은 빈칸이 아니라 "미정(ADC-0002 범위
밖)"으로 명시한다.

| 항목 | 내용 |
|---|---|
| Mission | Engine이 실제로 만들어낸 산출물을 Execution Layer 내부에서 다룰 수 있는 여섯 번째 Artifact로 담는다. |
| Input | Execution State(`str`). |
| Output | Execution Result — **형태: 산출물 목록(list)**(ADC-0002 Decision). 구체적 직렬화 형식(`str` 내 목록 표현인지, 다른 타입인지)은 미정(ADC-0002 범위 밖). |
| Canonical Fields | 미정(ADC-0002 범위 밖) — 목록 항목의 타입 스키마는 후속 결정 대상. |
| Version | 미정. |
| Producer | 미구현. |
| Consumer | 아직 없음. |
| Deterministic 여부 | 미정 — Builder가 구현되지 않아 확인 불가. |
| Immutable 여부 | 미정 — Builder가 구현되지 않아 확인 불가. |

절 말미에 다음 각주를 추가한다.

> 이 절은 `ADC-0002-execution-result-contract.md`가 결정한 형태
> (산출물 목록)만 반영한다. 5개 Builder(Artifact 1~5)와 달리, 이
> Artifact는 Deterministic/Immutable 여부를 실측(테스트)으로 확인한
> 적이 없다 — Builder 자체가 아직 구현되지 않았기 때문이다. "미정"
> 표시는 누락이 아니라 의도적 표기다(Freeze 원칙).

#### 2.4 "공통 패턴" 절의 정정

기존 "Wrap, not rewrite. 5개 Builder 모두..."는 그대로 둔다 — 이
패턴은 Artifact 1~5에 대해서만 실측된 사실이며 ADC-0002가 바꾸지
않았다. 다만 문단 끝에 다음 한 줄을 추가한다.

> Execution Result(Artifact 6)는 이 패턴을 따르지 않는 첫 사례로
> 결정됐다(ADC-0002) — 단일 텍스트 Wrap이 아니라 목록을 담는다.

#### 2.5 "Boundary" 절 갱신

기존 "Execution Result(여섯 번째, 아직 구현되지 않은 Artifact)를
설계하지 않는다" 항목을 다음으로 교체한다.

> Execution Result의 **필드 스키마**는 설계하지 않는다 — ADC-0002가
> 결정한 것은 형태(목록)뿐이다. Builder 구현, 목록 항목의 타입
> 분류는 여전히 이 문서의 범위 밖이다.

#### 2.6 "근거" 절에 추가

```
- docs/core/execution-layer/RFC-0002-execution-result-contract.md
- docs/core/execution-layer/ADC-0002-execution-result-contract.md
- docs/core/execution-layer/ADR-0001-execution-result-contract.md
```

#### 2.7 문서 말미 "이 문서는 커밋하지 않는다" 문구 삭제

`ARTIFACT-STANDARD-v1.md` 176행의 "이 문서는 커밋하지 않는다"는
문서 자체가 이미 저장소에 커밋되어 있는 상태(git 추적 파일)와
모순되는 잔존 문구다 — 이번 갱신에서 함께 정정한다(ADC-0002 판단과
직접 관련은 없으나, 같은 파일을 수정하는 김에 사실과 어긋난 문구를
방치하지 않는다).

### 3. `docs/03_adc/ADC.md` 갱신 여부

**갱신하지 않는다.** `ADC-0002-execution-result-contract.md`는
Execution Layer 네임스페이스의 ADC이며, `docs/03_adc/ADC.md`는
Jarvis OS(Kernel) 수준 Open Decision만 관리한다(ADC-01~ADC-12 전부
Kernel 수준). Execution Layer ADC는 애초에 이 목록에 등록된 적이
없다(ADC-0001 선례와 동일).

### 4. Development HQ · Kernel Architecture 불변 확인

- `development-hq/` 이하 어떤 파일도 변경하지 않는다.
- `core/execution_layer/*/` 이하 소스 코드는 어떤 파일도 변경하지
  않는다 — Builder를 구현하지 않는다.
- `docs/01_architecture/BASELINE.md`(Kernel Architecture Baseline)는
  변경하지 않는다.
- 기존 42개(또는 그 이상) 테스트는 이번 변경으로 영향받지 않는다
  (문서만 변경).

### 5. Migration Strategy

1. `ARTIFACT-STANDARD-v1.md` — §2.1~§2.7 반영.
2. 검증:
   - `git status`로 `development-hq/`·`core/` 이하에 변경이 없는지
     확인.
   - `python3 -m pytest core/execution_layer -q` 기존 테스트가
     그대로 통과하는지 확인(문서만 변경했으므로 결과가 달라지면
     안 된다).
   - `ARTIFACT-STANDARD-v1.md`가 ADC-0002 Decision과 모순되는 문장을
     남기지 않았는지 재확인(§2.1·§2.5).
3. 커밋 — ADR-0001과 `ARTIFACT-STANDARD-v1.md` 변경을 함께 커밋한다.

---

## Consequences

- `ARTIFACT-STANDARD-v1.md`가 Execution Result의 **형태**(목록)를
  처음으로 반영한다 — 5개 Builder의 단일 텍스트 패턴이 깨지는 첫
  지점이 Baseline에 정직하게 기록된다.
- Execution Result의 **필드 스키마는 여전히 미정**이다 — 이 ADR은
  그 미정 상태를 숨기지 않고 "미정(ADC-0002 범위 밖)"으로 명시한다.
  다음에 이 Artifact를 구현하려는 시도는 여전히 필드 스키마 결정을
  선행해야 하며, 그 결정은 별도 RFC/ADC/ADR 대상이다.
- Execution Result Builder는 여전히 구현되지 않는다 — 이 ADR은
  코드를 한 줄도 만들지 않는다.
- Candidate 3(참조 + Memory 영역)이 요구했던 저장 위치 설계는
  Defer로 남는다 — 재검토 조건은 ADC-0002 Risks에 이미 기록됨.
- `docs/03_adc/ADC.md`(Kernel Open Decision 목록)는 변경되지 않는다
  — 이 사이클은 처음부터 끝까지 Execution Layer 네임스페이스
  안에서 종결된다.
- 이 ADR은 **승인되었으며**, §2에 정의된 실제 파일 변경이 이 승인에
  따라 실행된다.

## Self Review

- ADC-0002가 결정하지 않은 것을 반영했는가 — **아니오**. §Out of
  Scope에 명시한 항목(필드 스키마, 타입 분류, Builder 구현, Memory
  영역, call_engine 배선, State 전이 규칙)은 손대지 않았다.
- Kernel Architecture Baseline(`docs/01_architecture/BASELINE.md`)을
  변경했는가 — **아니오**.
- `docs/03_adc/ADC.md`를 변경했는가 — **아니오**(§3).
- 코드를 작성했는가 — **아니오**.
- Builder를 구현했는가 — **아니오**.
- 새로운 Architecture 문제를 발견했는가 — **아니오**. 반영 과정에서
  ADC-0002·RFC-0002가 이미 인지한 것 이상의 새 결정 지점은
  나타나지 않았다.
