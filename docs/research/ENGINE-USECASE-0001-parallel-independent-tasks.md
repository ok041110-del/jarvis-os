# ENGINE-USECASE-0001: 독립적인 두 Task의 병렬 실행 — Runtime Evidence

이 문서는 사용 후기가 아니다. 실제로 수행한 실험 하나의 기록이다. Phase 9
Resolution Audit 종료 이후, 현재 단일 Engine(`call_engine()`) 환경에서
실제로 유용한 Use Case를 발굴하는 것이 목적이며, Adapter/Gateway 필요성을
전제하지 않는다. `development-hq/mvp/engine.py`의 `call_engine()`은
전혀 수정하지 않았다 — 호출부(실험 스크립트)만 존재했고, 그 스크립트는
이 세션의 scratchpad에만 있었다(`ENGINE-CONNECT-0006`과 동일한 격리
원칙). `git status --porcelain`이 실험 전후 비어 있음을 확인했다.

## Use Case

서로 완전히 독립적인 두 개의 실제 Task(공유 상태 없음, 서로의 출력을
입력으로 쓰지 않음)를 하나의 호출 지점(`call_engine()`)만으로 "순차"와
"병렬(스레드)" 두 방식으로 각각 실행해 비교한다.

- Task A: `backend_agent_code_review()` — 기존 `test_mvp_0001.py`의
  `SAMPLE_CODE` 재사용(신규 입력 생성 안 함).
- Task B: `call_engine()` 직접 호출 — 기존 `ENGINE-CONNECT-0006`이 쓴
  `core/execution_layer/mvp_0006/dogfooding/output/toy_issue.prompt_specification.md`
  재사용(신규 입력 생성 안 함).

## Execution

- 실제 Engine 호출 4회(순차 2회 + 병렬 2회), 전부 real `claude -p`.
- 순차: Task A → Task B, `elapsed=32.19s`.
- 병렬: `concurrent.futures.ThreadPoolExecutor(max_workers=2)`로 Task A/B
  동시 제출, `elapsed=20.11s`.
- `call_engine()` 시그니처/구현은 완전히 그대로다 — 병렬 실행은 호출부가
  Python 표준 라이브러리 스레드로 동일 함수를 두 번 부른 것뿐이며, 새
  Gateway/Adapter/Registry를 만들지 않았다.

## 관찰 결과

1. **병렬 실행이 코드 변경 없이 동작한다.** `call_engine()`은 매 호출마다
   독립된 `subprocess.run()`이므로 스레드 두 개에서 동시에 불러도 서로
   간섭하지 않았다 — 두 결과 모두 실제 실행으로 정상 수신됨(빈 문자열,
   예외, 잘림 없음).
2. **출력 교차오염 없음(실측).** Task A 결과에 "reverse"가 등장하지
   않았고, Task B 결과에 "add(" 또는 "except"가 등장하지 않았다 — 두
   프로세스의 입력/출력이 서로 섞이지 않았음을 직접 확인했다.
3. **실제 단축 효과가 있었다** (32.19s → 20.11s, 약 37% 단축). 단,
   2배 단축은 아니다 — 두 `claude -p` 프로세스가 동일 머신 자원(CPU/
   네트워크)을 공유하기 때문으로 추정되며, 이번 실험(n=1)은 그 원인을
   분리 검증하지 않았다.
4. **비용 관측 불가(구조적 한계).** `call_engine()`은 `--output-format
   text`로 raw stdout만 반환한다 — 병렬로 몇 번을 부르든, 실제 토큰/비용이
   얼마나 들었는지 이 함수의 반환값만으로는 알 수 없다. 이는 새로운
   결함이 아니라 기존 계약("텍스트를 받아 텍스트를 반환한다")이 처음부터
   비용 정보를 다루지 않는다는 사실의 재확인이다 — Adapter 없이도
   `--output-format json`으로 바꾸면 비용 필드를 받을 수 있겠지만, 그
   자체가 `call_engine()`의 반환 계약 변경이므로 이번 실험에서는
   시도하지 않았다(Contract 변경 필요 → 별도 판단 대상, 아래 참고).

## Adapter Need

없음. 이번 Use Case는 호출부가 동일 함수를 여러 스레드에서 부르는 것만으로
충족됐다 — Engine Routing/Gateway/Adapter가 필요하다는 신호는 관찰되지
않았다.

## Governance / Architecture

Architecture/Contract 변경 없음. `call_engine()`의 반환 계약을
`text`에서 `json`(비용 필드 포함)으로 바꾸는 안은 이번 실험에서
발견됐지만 실행하지 않았다 — Contract 변경이므로 이 문서는 그 필요성만
기록하고 결정하지 않는다. 필요 시 별도 RFC 대상이다.

## Evidence

- 실험 스크립트: 세션 scratchpad(`experiment_engine_usecase_0001.py`,
  tracked 브랜치 미포함).
- 실제 실행 로그(요약): 순차 `elapsed=32.19s`, 병렬 `elapsed=20.11s`,
  교차오염 체크 2건 모두 `False`(오염 없음).

## Next

- 병렬 호출 개수를 2 → N으로 늘렸을 때 단축률이 어떻게 변하는지는
  미관찰(n=2, 1회 실행) — 후속 관찰 대상.
- 비용 관측이 실제로 필요해지는 시점(예: 병렬 호출이 반복적으로
  일어나는 실제 Use Case)이 생기면, `--output-format json` 전환을
  Contract 변경으로 별도 판단한다.
