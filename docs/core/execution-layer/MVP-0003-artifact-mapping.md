# Execution Layer MVP-0003 Artifact Mapping

Prompt Specification → Model Request 변환 전/후, 항목 대응표. 사실만
기록한다. Architecture 판단은 하지 않는다.

## 변환 방식

`core/execution_layer/mvp_0003/model_request_builder.py`의
`build_model_request()`는 Prompt Specification 앞에 고정 형식의
`## Metadata` 절 하나만 추가한다.

```
# Model Request

## Metadata
- request_id: {호출자 제공}
- artifact_version: execution-layer-mvp-0003   (모듈 상수, 항상 동일)
- created_at: {호출자 제공}
- target_engine: unresolved                    (모듈 상수, 항상 동일)

## Prompt Specification
{Prompt Specification 원문 verbatim}
```

`request_id`, `created_at`은 `build_model_request()`가 생성하지 않는다
— 호출자가 주입한 값을 그대로 담을 뿐이다(이유는
`model_request_builder.py` 모듈 docstring 참조: 값 생성은 Session/Runtime
책임 영역과 겹치므로 이 MVP 범위 밖으로 남겨 둔다). `artifact_version`,
`target_engine`은 입력과 무관하게 항상 동일한 모듈 상수다.

## Case 1: 실제 Issue(`workflow_0008.REAL_ISSUE`, "Project Intelligence 개선")

Dogfooding 산출물: `core/execution_layer/mvp_0003/dogfooding/output/real_issue.*`

| 항목 | Before(Prompt Specification) | After(Model Request) | 손실 여부 |
|---|---|---|---|
| Prompt Specification 전체 | 6,700 글자 | 동일 텍스트가 `## Prompt Specification` 절 아래 verbatim 포함 | 없음(`prompt_specification in model_request` → `True`) |
| request_id | (없음) | `099012e5add6bcb1` (Prompt Specification SHA-256 해시 앞 16자, 호출자가 결정론적으로 유도) | 신규 메타데이터 |
| artifact_version | (없음) | `execution-layer-mvp-0003` | 신규 메타데이터 |
| created_at | (없음) | `unresolved`(고정 placeholder) | 신규 메타데이터 |
| target_engine | (없음) | `unresolved`(고정 placeholder, 실제 모델명 아님) | 신규 메타데이터 |

- 전체 길이: Prompt Specification 6,700 글자 → Model Request 6,883 글자
  (차이 183 글자 = 메타데이터 절 + 구조 마커).

## Case 2: 토이 Issue("reverse string")

Dogfooding 산출물: `core/execution_layer/mvp_0003/dogfooding/output/toy_issue.*`

| 항목 | Before(Prompt Specification) | After(Model Request) | 손실 여부 |
|---|---|---|---|
| Prompt Specification 전체 | 2,879 글자 | 동일 텍스트가 verbatim 포함 | 없음(`True`) |
| request_id | (없음) | `4b70a4540220e098`(Case별로 다름 — Prompt Specification 내용이 다르므로) | 신규 메타데이터 |
| artifact_version | (없음) | `execution-layer-mvp-0003`(Case 1과 동일) | 신규 메타데이터 |
| created_at | (없음) | `unresolved`(Case 1과 동일) | 신규 메타데이터 |
| target_engine | (없음) | `unresolved`(Case 1과 동일) | 신규 메타데이터 |

- 전체 길이: Prompt Specification 2,879 글자 → Model Request 3,062 글자
  (차이 183 글자, Case 1과 정확히 동일).

## 변화 폭 확인 (메타데이터 외 변경이 없는지)

| Case | Prompt Specification 길이 | Model Request 길이 | 증가량 |
|---|---|---|---|
| real_issue | 6,700 | 6,883 | 183 |
| toy_issue | 2,879 | 3,062 | 183 |

두 Case의 증가량이 정확히 동일(183 글자)하다는 사실은, 추가된 내용이
고정 구조(제목, `## Metadata` 절 마커, 4개 메타데이터 줄, `## Prompt
Specification` 절 마커)뿐이라는 것을 보여준다. `request_id` 값 자체는
Case마다 다르지만(입력이 다르므로 해시 값도 다름), 그 문자열 길이는
항상 16자로 고정되어 있어 전체 증가량에 영향을 주지 않았다.

## 결론(사실 기반)

두 Case 모두 다음이 실측으로 확인되었다.

- Prompt Specification 전체가 Model Request 안에 부분 문자열로 그대로
  포함된다(`in` 연산자로 직접 확인).
- 추가된 내용은 4개 메타데이터 필드와 그 절 마커뿐이며, 두 Case에서
  구조 오버헤드(183 글자)가 동일했다.
- `target_engine`, `artifact_version`은 Case와 무관하게 항상 동일한
  고정값이었다 — 실제 모델명은 어디에도 나타나지 않았다.
- `request_id`는 Case마다 값이 달랐지만, 이는 무작위가 아니라 각
  Prompt Specification 내용이 다르기 때문이다(SHA-256 해시 유도, 같은
  입력에는 항상 같은 값).
