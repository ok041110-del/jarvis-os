# Execution Layer MVP-0002 Artifact Mapping

Execution Request → Prompt Specification 변환 전/후, 항목별 대응표.
사실만 기록한다. Architecture 판단은 하지 않는다.

## Rendering Map

`core/execution_layer/mvp_0002/prompt_specification_builder.py`의
`RENDERING_MAP`이 유일한 배치 규칙이다. Execution Request의 9개 절(8개
Implementation Specification 항목 + Reference Design)을 Prompt
Specification의 5개 절로 1:1 배정한다.

| Execution Request 절 | → | Prompt Specification 절 |
|---|---|---|
| Target File | → | Mission |
| Public Interface | → | Mission |
| Dependencies | → | Input |
| Reference Design | → | Input |
| Classes | → | Constraints |
| Edge Cases | → | Constraints |
| Functions | → | Expected Output |
| Algorithm Outline | → | Expected Output |
| Validation Notes | → | Validation Notes |

각 절의 본문은 원본 소제목(`## {절 이름}`)을 그대로 유지한 채 새 상위
절(`# {Prompt Structure 절 이름}`) 아래로 옮겨질 뿐, 텍스트 내용은 한
글자도 바뀌지 않는다.

## Case 1: 실제 Issue(`workflow_0008.REAL_ISSUE`, "Project Intelligence 개선")

Dogfooding 산출물: `core/execution_layer/mvp_0002/dogfooding/output/real_issue.*`

| Execution Request 절 | Prompt Specification 절 | 본문 글자 수 | Prompt Specification 안에 원문 그대로 포함되는가 |
|---|---|---|---|
| Target File | Mission | 52 | True |
| Public Interface | Mission | 43 | True |
| Dependencies | Input | 169 | True |
| Reference Design | Input | 4,457 | True |
| Classes | Constraints | 41 | True |
| Edge Cases | Constraints | 206 | True |
| Functions | Expected Output | 941 | True |
| Algorithm Outline | Expected Output | 361 | True |
| Validation Notes | Validation Notes | 166 | True |

- 전체 길이: Execution Request 6,623 글자 → Prompt Specification 6,700
  글자.
- 9개 절 본문 모두 `body in prompt_specification`(Python `in` 연산자)로
  `True` 확인 — 손실 없음.
- Prompt Structure 5개 절(`# Mission`, `# Input`, `# Constraints`,
  `# Expected Output`, `# Validation Notes`) 모두 최상위 마커로 존재함을
  확인(`find_prompt_sections()`).

## Case 2: 토이 Issue("reverse string")

Dogfooding 산출물: `core/execution_layer/mvp_0002/dogfooding/output/toy_issue.*`

| Execution Request 절 | Prompt Specification 절 | 본문 글자 수 | Prompt Specification 안에 원문 그대로 포함되는가 |
|---|---|---|---|
| Target File | Mission | 46 | True |
| Public Interface | Mission | 37 | True |
| Dependencies | Input | 215 | True |
| Reference Design | Input | 1,816 | True |
| Classes | Constraints | 41 | True |
| Edge Cases | Constraints | 34 | True |
| Functions | Expected Output | 322 | True |
| Algorithm Outline | Expected Output | 28 | True |
| Validation Notes | Validation Notes | 76 | True |

- 전체 길이: Execution Request 2,802 글자 → Prompt Specification 2,879
  글자.
- 9개 절 본문 모두 `True` — 손실 없음.
- Prompt Structure 5개 절 모두 존재 확인.

## 변화 폭 확인 (Rendering 외 변화가 없는지)

전체 길이 증가분은 새로 추가된 구조용 텍스트(제목·소제목 마커, 절 구분
개행)뿐이다.

| Case | Execution Request 길이 | Prompt Specification 길이 | 증가량 |
|---|---|---|---|
| real_issue | 6,623 | 6,700 | 77 |
| toy_issue | 2,802 | 2,879 | 77 |

두 Case의 증가량이 정확히 동일(77 글자)하다는 사실은, 추가된 내용이
입력 데이터에 의존하지 않는 고정된 구조(문서 제목 1개 + Prompt Section
제목 5개 + 그 사이 구분 개행)뿐이라는 것을 보여준다 — 절 개수(9개 소제목)
와 배치 규칙이 두 Case에서 동일했으므로 구조 오버헤드도 동일했다.

## 결론(사실 기반)

두 Case 모두 다음이 실측으로 확인되었다.

- 9개 절(8개 항목 + Reference Design) 각각의 본문이 Prompt Specification
  안에 원문 그대로(byte 단위) 포함된다.
- 추가된 내용은 Prompt Structure가 요구하는 5개 절 제목과 원본 소제목
  마커, 그 사이 구분 개행뿐이며, 두 Case에서 그 증가량이 동일했다.
- Execution Request 자체는 변환 과정에서 변경되지 않았다
  (`test_execution_request_itself_is_unchanged_by_rendering`).
