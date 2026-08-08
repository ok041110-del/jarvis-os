# Execution Layer MVP-0005 Artifact Mapping

Execution Handle → Execution State 변환 전/후, 항목 대응표. 사실만
기록한다. Architecture 판단은 하지 않는다.

## 변환 방식

`core/execution_layer/mvp_0005/execution_state_builder.py`의
`build_execution_state()`는 Execution Handle 앞에 고정 형식의 `## State`
절 하나만 추가한 **새 Artifact**를 반환한다(Execution Handle 자체는
변경되지 않는다).

```
# Execution State

## State
- handle_id: {호출자 제공}
- request_id: {Execution Handle의 ## Handle 절에서 그대로 읽음}
- state: {호출자 제공, 5개 허용 값 중 하나인지만 검증}
- changed_at: {호출자 제공}
- artifact_version: execution-layer-mvp-0005   (모듈 상수, 항상 동일)

## Execution Handle
{Execution Handle 원문 verbatim}
```

`handle_id`, `state`, `changed_at`은 `build_execution_state()`가 생성하지
않는다 — 호출자가 주입한 값을 그대로 담을 뿐이다(이유는
`execution_state_builder.py` 모듈 docstring 참조). `request_id`는 새
값을 주입받지 않고 Execution Handle 안에 이미 있는 값을 그대로 읽어서
재사용한다 — Execution Handle을 Canonical 참조로 유지하기 위함이다.
`state`는 5개 허용된 이름(PENDING/RUNNING/COMPLETED/FAILED/CANCELLED)
중 하나인지만 검증하며, 상태 전이 규칙(이전 상태 → 다음 상태의 허용
여부)은 검증하지 않는다. `artifact_version`은 입력과 무관하게 항상
동일한 고정값이다.

## Case 1: 실제 Issue(`workflow_0008.REAL_ISSUE`, "Project Intelligence 개선")

Dogfooding 산출물: `core/execution_layer/mvp_0005/dogfooding/output/real_issue.*`

| 항목 | Before(Execution Handle) | After(Execution State) | 손실 여부 |
|---|---|---|---|
| Execution Handle 전체 | 7,082 글자 | 동일 텍스트가 `## Execution Handle` 절 아래 verbatim 포함 | 없음(`execution_handle in execution_state` → `True`) |
| handle_id | Execution Handle `## Handle` 절 안에 `3774bd87e088a9f5` | Execution State `## State` 절에서 호출자가 동일 값을 전달(`3774bd87e088a9f5`) | 값 일치(호출자가 Execution Handle 자신의 값을 그대로 재사용) |
| request_id | Execution Handle 안에 `099012e5add6bcb1` | Execution State에도 동일한 `099012e5add6bcb1` | 재사용(값 변경 없음, Builder가 직접 읽음) |
| state | (없음) | `PENDING` | 신규 메타데이터 |
| changed_at | (없음) | `unresolved`(고정 placeholder) | 신규 메타데이터 |
| artifact_version | (없음) | `execution-layer-mvp-0005` | 신규 메타데이터 |

- 전체 길이: Execution Handle 7,082 글자 → Execution State 7,279 글자
  (차이 197 글자 = State 절 + 구조 마커).

## Case 2: 토이 Issue("reverse string")

Dogfooding 산출물: `core/execution_layer/mvp_0005/dogfooding/output/toy_issue.*`

| 항목 | Before(Execution Handle) | After(Execution State) | 손실 여부 |
|---|---|---|---|
| Execution Handle 전체 | 3,261 글자 | 동일 텍스트가 verbatim 포함 | 없음(`True`) |
| handle_id | Execution Handle 안에 `f8e2ef639b4d6b92` | Execution State에도 동일 값 | 값 일치 |
| request_id | Execution Handle 안에 `4b70a4540220e098` | Execution State에도 동일 값 | 재사용 |
| state | (없음) | `PENDING`(Case 1과 동일) | 신규 메타데이터 |
| changed_at | (없음) | `unresolved`(Case 1과 동일) | 신규 메타데이터 |
| artifact_version | (없음) | `execution-layer-mvp-0005`(Case 1과 동일) | 신규 메타데이터 |

- 전체 길이: Execution Handle 3,261 글자 → Execution State 3,458 글자
  (차이 197 글자, Case 1과 정확히 동일).

## 변화 폭 확인 (메타데이터 외 변경이 없는지)

| Case | Execution Handle 길이 | Execution State 길이 | 증가량 |
|---|---|---|---|
| real_issue | 7,082 | 7,279 | 197 |
| toy_issue | 3,261 | 3,458 | 197 |

두 Case의 증가량이 정확히 동일(197 글자)하다는 사실은, 추가된 내용이
고정 구조(제목, `## State` 절 마커, 5개 필드 줄, `## Execution Handle`
절 마커)뿐이라는 것을 보여준다. `handle_id`, `request_id` 값 자체는
Case마다 다르지만(입력이 다르므로 해시 값도 다름), 두 값 모두 항상
16자 16진수 문자열이라 전체 증가량에 영향을 주지 않았다.

## Canonical Reference 일관성 확인

두 Case 모두에서 다음을 실측으로 확인했다.

- `handle_id (derived)`(Execution Handle을 만들 때 사용한 값)와
  `handle_id (from execution_handle)`(Execution Handle 본문에서 다시
  추출한 값)이 완전히 동일했다.
- `request_id`는 MVP-0003·MVP-0004 Dogfooding에서 기록된 값과 이번
  MVP-0005 Execution State에서도 동일했다(real_issue:
  `099012e5add6bcb1`, toy_issue: `4b70a4540220e098`) — 체인 전체에서
  한 번도 값이 바뀌지 않았다.

## 결론(사실 기반)

두 Case 모두 다음이 실측으로 확인되었다.

- Execution Handle 전체가 Execution State 안에 부분 문자열로 그대로
  포함된다(`in` 연산자로 직접 확인). Execution Handle 자체는 변경되지
  않았다(`test_execution_handle_itself_is_unchanged_by_state_creation`).
- 추가된 내용은 5개 State 필드와 그 절 마커뿐이며, 두 Case에서 구조
  오버헤드(197 글자)가 동일했다.
- `artifact_version`은 Case와 무관하게 항상 동일한 고정값
  (`execution-layer-mvp-0005`)이었다.
- `request_id`는 Execution Handle에서 재사용된 값이며, 체인의 이전
  단계(MVP-0003, MVP-0004)에서 기록된 값과 완전히 일치했다.
- `state`는 5개 허용된 이름(PENDING/RUNNING/COMPLETED/FAILED/CANCELLED)
  중 하나인지만 검증되었고, 순서와 무관하게 임의의 허용된 상태로 여러
  번 Execution State를 만들 수 있음을 테스트로 확인했다(State Transition
  규칙 미검증).
