# Execution Layer MVP-0001 Artifact Mapping

Implementation Specification → Execution Request 변환 전/후, 항목별 대응표.
사실만 기록한다. Architecture 판단은 하지 않는다.

## 변환 방식

`core/execution_layer/mvp_0001/execution_request_builder.py`의
`build_execution_request()`는 입력 문자열 앞에 머리말
`"# Execution Request\n\n"`(21 글자)만 붙인다. 그 외 어떤 글자도 추가·
삭제·치환하지 않는다.

## Case 1: 실제 Issue(`workflow_0008.REAL_ISSUE`, "Project Intelligence 개선")

Dogfooding 산출물: `core/execution_layer/mvp_0001/dogfooding/output/real_issue.*`

| 항목 | Before(Implementation Specification, 글자 수) | After(Execution Request 안의 동일 절, 글자 수) | 손실 여부 |
|---|---|---|---|
| Target File | 52 | 52 | 없음 |
| Public Interface | 43 | 43 | 없음 |
| Functions | 941 | 941 | 없음 |
| Classes | 41 | 41 | 없음 |
| Dependencies | 169 | 169 | 없음 |
| Algorithm Outline | 361 | 361 | 없음 |
| Edge Cases | 206 | 206 | 없음 |
| Validation Notes | 166 | 166 | 없음 |
| Reference Design(Design + Reference Requirement + Reference Context 전체 verbatim, MVP-0013 관례) | 나머지 전체 | 나머지 전체 | 없음 |

- 전체 길이: Implementation Specification 6,602 글자 → Execution Request
  6,623 글자 (차이 21 글자 = 머리말 길이와 정확히 일치).
- `implementation_specification in execution_request` → `True`
  (Python `in` 연산자로 직접 확인, 원문이 부분 문자열로 그대로
  포함됨을 실측 확인).
- 8개 알려진 절(`## {Section}` 마커) 존재 여부: 변환 전/후 8개 모두
  `True`로 동일.

## Case 2: 토이 Issue("reverse string")

Dogfooding 산출물: `core/execution_layer/mvp_0001/dogfooding/output/toy_issue.*`

| 항목 | Before(글자 수) | After(글자 수) | 손실 여부 |
|---|---|---|---|
| Target File | 46 | 46 | 없음 |
| Public Interface | 37 | 37 | 없음 |
| Functions | 322 | 322 | 없음 |
| Classes | 41 | 41 | 없음 |
| Dependencies | 215 | 215 | 없음 |
| Algorithm Outline | 28 | 28 | 없음 |
| Edge Cases | 34 | 34 | 없음 |
| Validation Notes | 76 | 76 | 없음 |
| Reference Design | 나머지 전체 | 나머지 전체 | 없음 |

- 전체 길이: Implementation Specification 2,781 글자 → Execution Request
  2,802 글자 (차이 21 글자, Case 1과 동일).
- `implementation_specification in execution_request` → `True`.
- 8개 알려진 절 존재 여부: 변환 전/후 8개 모두 `True`로 동일.

## 결론(사실 기반)

두 Case 모두 다음이 실측으로 확인되었다.

- 8개 항목 각각의 글자 수가 변환 전/후 완전히 동일하다(항목별 요약·재구성
  없음).
- 원본 Implementation Specification 전체가 Execution Request 안에 부분
  문자열로 그대로 포함된다.
- 변환 전/후 길이 차이는 정확히 머리말 길이(21 글자)와 일치한다 — 그 외
  어떤 내용도 추가되지 않았다.
- 두 Case의 결과는 서로 다른 입력(실제 Issue vs 토이 Issue)에서 얻어졌지만,
  "머리말만 추가되고 나머지는 완전히 보존된다"는 패턴은 동일하게
  재현되었다.
