# Fix Cycle: truncate() validation-ordering contract

`validation.md`(첫 실행)가 실제로 찾아낸 결함을 실제 pytest로
재현하고, 기존 `backend_agent_code_generation`(새 Capability 아님)을
다시 호출해 수정한 뒤, 그 수정을 두 번째 real Review와 real pytest로
재검증한 기록이다. 두 라운드 모두 real Engine 호출이며 mock 없음.

## Round 1 — 첫 실행이 찾은 결함, pytest로 재현

`validation.md`의 code_review: "Validation is bypassed on the 'no
truncation needed' path" — `max_len < len(suffix)` 검사가
`len(text) <= max_len` 조기 반환 **뒤에** 있어, 텍스트가 이미
`max_len` 안에 들어가면 검사 자체가 건너뛰어진다.

`tests/test_truncate.py`에 그 문서화된 계약(`Raises` 절: "무조건
raise")을 그대로 인코딩한 테스트를 작성해 실제로 실행:

```
FAILED test_max_len_shorter_than_suffix_raises_even_when_text_already_fits
    with pytest.raises(ValueError):
E       Failed: DID NOT RAISE ValueError
```

## Round 1 Fix — 실제 재현된 pytest 실패를 그대로 입력해 재수정 요청

원본 코드 + 위 pytest 실패 메시지를 `backend_agent_code_generation()`의
입력(design 텍스트)에 그대로 포함해 재호출했다. 반환된 코드는 두
검증(`max_len < 0`, `max_len < len(suffix)`)을 `len(text) <= max_len`
조기 반환보다 **앞으로** 옮겼다 — Round 1의 실패를 문자 그대로
해소한다.

## Round 2 — 수정된 코드를 다시 real Review — 새로운 실제 결함 발견

`run_mvp_0002()`로 수정된 코드를 다시 리뷰한 결과, real Engine이
**정반대 방향의 실제 결함**을 지적했다: "Real bug — validation fires
even when no truncation is needed." `truncate("ok", 2)`처럼
`len(text) == max_len`이라 텍스트가 그대로 반환돼야 하는(docstring이
스스로 약속한 "returned unchanged") 경우인데도, 기본 suffix(`"..."`,
길이 3)가 `max_len`(2)보다 길다는 이유만으로 이제는 `ValueError`가
발생한다 — Round 1 결함의 정반대 증상이다.

## Round 2 판단 — 코드가 아니라 원래 docstring의 "Raises" 문구가 과잉 약속이었다

두 라운드는 서로 모순되는 것이 아니라, 이 함수의 원래 명세(Issue
0002 description: "max_len이 len(suffix)보다 작은 경우를 어떻게
처리할지도 명확히 정의해야 한다")가 애초에 "언제" 검증해야 하는지를
명시하지 않은 데서 비롯된 자연스러운 모호성이다. 실제로 truncation이
필요 없는 호출(`len(text) <= max_len`)에서는 `suffix`가 전혀 쓰이지
않으므로, 그 경우까지 `max_len < len(suffix)`를 강제하는 것은 사용자
관점에서 놀라운 실패(정상적인 짧은 입력이 실패)를 만든다 — Round 1의
pytest 테스트가 인코딩한 가정(무조건 raise) 자체가 틀렸다.

**최종 결정**: 코드는 원래 순서(조기 반환 먼저, 검증은 truncation이
실제로 필요할 때만)로 되돌리고, docstring의 `Raises` 절만 "truncation이
실제로 필요할 때만 검증한다"고 정확하게 고쳤다 — 이는 코드 버그
수정이 아니라 문서가 실제 동작을 정확히 반영하도록 한 것이다. Round 1의
잘못된 가정을 인코딩했던 pytest 테스트도 함께 고쳐, 이제는 `truncate("hi",
2, suffix="...")`가 raise 없이 `"hi"`를 그대로 반환하는 것을
확인한다.

## Round 3 — 최종 코드에 대한 real Review 재확인

```
"The core truncation math is correct and matches the documented
contract in all the cases I traced through"
```

남은 지적(Unicode grapheme 경계, `suffix=None`일 때 `TypeError`,
음수·suffix-length 두 조건이 동시에 참일 때 에러 메시지 우선순위)은
전부 스타일/견고성 개선 후보이며, 이번 세션에서 실제로 재현되지 않은
이론적 확장이라 반영하지 않았다(README의 "이론적 문제는 만들지
않는다" 원칙).

## 최종 검증

`python3 -m pytest projects/textkit/tests -v` — **32건 모두 통과**
(회귀 없음, `test_cli.py`/`test_slugify.py` 포함 전체 재실행).
