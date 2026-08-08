# Execution Layer MVP-0004 Artifact Mapping

Model Request → Execution Handle 변환 전/후, 항목 대응표. 사실만
기록한다. Architecture 판단은 하지 않는다.

## 변환 방식

`core/execution_layer/mvp_0004/execution_handle_builder.py`의
`build_execution_handle()`은 Model Request 앞에 고정 형식의 `## Handle`
절 하나만 추가한다.

```
# Execution Handle

## Handle
- handle_id: {호출자 제공}
- request_id: {Model Request의 ## Metadata 절에서 그대로 읽음}
- status: PENDING                              (고정값, 항상 동일)
- submitted_at: {호출자 제공}
- artifact_version: execution-layer-mvp-0004   (모듈 상수, 항상 동일)

## Model Request
{Model Request 원문 verbatim}
```

`handle_id`, `submitted_at`은 `build_execution_handle()`이 생성하지
않는다 — 호출자가 주입한 값을 그대로 담을 뿐이다(이유는
`execution_handle_builder.py` 모듈 docstring 참조). `request_id`는 새
값을 주입받지 않고 Model Request 안에 이미 있는 값을 그대로 읽어서
재사용한다 — Model Request를 Canonical 참조 대상으로 유지하기 위함이다.
`status`, `artifact_version`은 입력과 무관하게 항상 동일한 고정값이다.

## Case 1: 실제 Issue(`workflow_0008.REAL_ISSUE`, "Project Intelligence 개선")

Dogfooding 산출물: `core/execution_layer/mvp_0004/dogfooding/output/real_issue.*`

| 항목 | Before(Model Request) | After(Execution Handle) | 손실 여부 |
|---|---|---|---|
| Model Request 전체 | 6,883 글자 | 동일 텍스트가 `## Model Request` 절 아래 verbatim 포함 | 없음(`model_request in execution_handle` → `True`) |
| handle_id | (없음) | `3774bd87e088a9f5`(Model Request SHA-256 해시 앞 16자, 호출자가 결정론적으로 유도) | 신규 메타데이터 |
| request_id | Model Request `## Metadata` 절 안에 `099012e5add6bcb1` | Execution Handle `## Handle` 절에도 동일한 `099012e5add6bcb1` | 재사용(값 변경 없음) |
| status | (없음) | `PENDING` | 신규 메타데이터(고정값) |
| submitted_at | (없음) | `unresolved`(고정 placeholder) | 신규 메타데이터 |
| artifact_version | (없음) | `execution-layer-mvp-0004` | 신규 메타데이터 |

- 전체 길이: Model Request 6,883 글자 → Execution Handle 7,082 글자
  (차이 199 글자 = Handle 절 + 구조 마커).

## Case 2: 토이 Issue("reverse string")

Dogfooding 산출물: `core/execution_layer/mvp_0004/dogfooding/output/toy_issue.*`

| 항목 | Before(Model Request) | After(Execution Handle) | 손실 여부 |
|---|---|---|---|
| Model Request 전체 | 3,062 글자 | 동일 텍스트가 verbatim 포함 | 없음(`True`) |
| handle_id | (없음) | `f8e2ef639b4d6b92`(Case별로 다름 — Model Request 내용이 다르므로) | 신규 메타데이터 |
| request_id | Model Request 안에 `4b70a4540220e098` | Execution Handle에도 동일 값 | 재사용 |
| status | (없음) | `PENDING`(Case 1과 동일) | 신규 메타데이터 |
| submitted_at | (없음) | `unresolved`(Case 1과 동일) | 신규 메타데이터 |
| artifact_version | (없음) | `execution-layer-mvp-0004`(Case 1과 동일) | 신규 메타데이터 |

- 전체 길이: Model Request 3,062 글자 → Execution Handle 3,261 글자
  (차이 199 글자, Case 1과 정확히 동일).

## 변화 폭 확인 (메타데이터 외 변경이 없는지)

| Case | Model Request 길이 | Execution Handle 길이 | 증가량 |
|---|---|---|---|
| real_issue | 6,883 | 7,082 | 199 |
| toy_issue | 3,062 | 3,261 | 199 |

두 Case의 증가량이 정확히 동일(199 글자)하다는 사실은, 추가된 내용이
고정 구조(제목, `## Handle` 절 마커, 5개 필드 줄, `## Model Request`
절 마커)뿐이라는 것을 보여준다. `handle_id`, `request_id` 값 자체는
Case마다 다르지만(입력이 다르므로 해시 값도 다름), 두 값 모두 항상
16자 16진수 문자열이라 전체 증가량에 영향을 주지 않았다.

## request_id 일관성 확인

MVP-0003 Dogfooding에서 기록된 `request_id`(real_issue:
`099012e5add6bcb1`, toy_issue: `4b70a4540220e098`)와, 이번 MVP-0004
Execution Handle 안의 `request_id` 값이 두 Case 모두 완전히 동일했다.
이는 `build_execution_handle()`이 새 request_id를 만들지 않고 Model
Request에서 그대로 읽어온다는 사실을 실측으로 확인해 준다.

## 결론(사실 기반)

두 Case 모두 다음이 실측으로 확인되었다.

- Model Request 전체가 Execution Handle 안에 부분 문자열로 그대로
  포함된다(`in` 연산자로 직접 확인).
- 추가된 내용은 5개 Handle 필드와 그 절 마커뿐이며, 두 Case에서 구조
  오버헤드(199 글자)가 동일했다.
- `status`, `artifact_version`은 Case와 무관하게 항상 동일한 고정값
  (`PENDING`, `execution-layer-mvp-0004`)이었다.
- `request_id`는 Model Request에서 재사용된 값이며, MVP-0003 Dogfooding
  결과와 완전히 일치했다 — 새로 생성되지 않았다.
- `handle_id`는 Case마다 값이 달랐지만, 이는 무작위가 아니라 각 Model
  Request 내용이 다르기 때문이다(SHA-256 해시 유도, 같은 입력에는 항상
  같은 값).
