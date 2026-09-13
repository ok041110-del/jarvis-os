# Python Refactor Wave 2 — C1 Implementation: `investment/teams/*.py`

**Governance 근거**: `docs/research/PYTHON-REFACTOR-WAVE-2-AUDIT-0001.md`
§10.1/§12(C1)/§14 — Wave 2 Audit이 P1 `SIMPLIFY`+`DUPLICATION`,
`WAVE 2 IMPLEMENT` 2순위로 확정한 후보의 실제 구현 Evidence다. C2
(`auto_selection_client.py`, `PYTHON-REFACTOR-WAVE-2-C2-0001.md`) 완료
후 같은 Wave 2 branch/PR에서 이어서 진행한다.

## 1. Problem

`hqs/investment/teams/{stock,etf,dividend_stock}_team.py` 3개 파일의
`run()` 안에서 "checkpoint 확인 → 병렬 실행 → 결과 수집" 블록이 Wave 1과
Wave 2(각 파일 내부의 분석 Wave 명칭, 이 문서에서 소문자 "wave"로 표기)
두 곳에서 반복되고, 3개 파일에 걸쳐서도 완전히 동일한 코드였다(3파일 ×
2블록 = 6곳, Wave 2 Audit §5/§10.1).

## 2. Before Comparison

세 파일의 `run()` 전체와 관련 import를 직접 비교했다.

| 항목 | stock_team.py | etf_team.py | dividend_stock_team.py |
|---|---|---|---|
| Wave1(분석) 블록 코드 | `wave1_t0`/`pending`/`ThreadPoolExecutor`/`wave1_elapsed` | 동일 | 동일 |
| Wave2(bull/bear) 블록 코드 | `wave2_t0`/`pending2`/`ThreadPoolExecutor`/`wave2_elapsed` | 동일 | 동일 |
| checkpoint semantics | `cp.has(n)`로 필터 → 완료분 `cp.load(n)` → 나머지 `run_step` | 동일 | 동일 |
| parallel execution semantics | `ThreadPoolExecutor(max_workers=len(pending))`, `pool.submit(run_step, cp, n, fn, arg)` | 동일 | 동일 |
| result collection semantics | `futures.items()` 순회하며 `fut.result()`로 동기 수집 | 동일 | 동일 |
| 함수 signature(`run()`) | `(company_label, raw_data_path, issue_dir) -> dict` | `(fund_label, raw_data_path, issue_dir) -> dict` | `(company_label, raw_data_path, issue_dir) -> dict` |
| exception/timeout 처리 | `run_step`/`Checkpointer`에 위임(팀 파일 자체는 처리 없음) | 동일 | 동일 |
| logging | 없음(call_log.json 기록은 `Checkpointer.save`가 담당) | 동일 | 동일 |
| state mutation | `current_pool` 없음(auto_selection_client와 다른 파일) — `cp`(Checkpointer)가 유일한 mutable 상태, 세 파일 모두 동일하게 다룸 | 동일 | 동일 |
| return schema | `{"results": {...11개 키...}, "wave_summary": {...6개 키...}}` | 동일 구조(키 이름은 도메인별 analysis 파일명만 다름) | 동일 구조 |
| **Domain 차이** | analyst 함수 5개(`fundamental`/`technical`/`industry`/`news_event`/`sentiment`), `SECTION_TAGS` 5개 | analyst 함수 6개(`composition`/`holdings_exposure`/`cost_tracking`/`performance_risk`/`distribution`/`macro`), `SECTION_TAGS` 6개 | analyst 함수 7개(`fundamental`/`dividend_quality`/`valuation`/`technical`/`industry`/`news_event`/`sentiment`), `SECTION_TAGS` 7개 |
| **Domain 차이** | `_DATA_LIMITATION_NOTICE`, `SECTION_TAGS`, 각 analyst instruction 문구, `report_writer_final_report` 인자 개수(9~11개)와 payload 조립 | 좌동(값만 다름) | 좌동(값만 다름) |
| import 스타일 미세 차이(리팩터링 범위 밖) | `run()` 안에 `import json` 인라인 | 파일 상단 `import json` | 파일 상단 `import json` |

## 3. True Duplication Analysis

"코드가 비슷하다"와 "동일한 책임이다"를 구분한 결과:

- **동일 책임(진짜 중복)**: "`jobs`(이름 → (analyst 함수, 입력 문자열))
  딕셔너리를 받아, 이미 완료된 step은 checkpoint에서 로드하고 나머지만
  `ThreadPoolExecutor`로 동시 실행해 이름별 결과 dict와 소요 시간을
  반환한다"는 책임은 3개 파일, 2개 블록 모두에서 **완전히 동일**하다 —
  변수명(`wave1_*` vs `wave2_*`, `pending` vs `pending2`)만 다를 뿐
  로직·순서·조건이 토씨 하나 다르지 않다. 이 책임은 앞으로도 세
  파일에서 항상 동일하게 변경돼야 한다 — 예를 들어 "재시도 로직을
  추가한다"는 변경이 필요해지면 세 파일 모두 똑같이 바뀌어야 하며,
  지금 구조에서는 세 곳(→ 실제로는 6곳)에 각각 적용해야 해 drift
  위험이 있다.
- **다른 책임(진짜 domain 차이)**: 어떤 analyst 함수를 몇 개 호출하는지,
  각 analyst의 프롬프트 지시문, `SECTION_TAGS`, `report_writer_final_report`가
  받는 섹션 개수와 payload 조립 방식은 팀마다 다르고 **앞으로도 서로
  다르게 진화해야 한다**(예: ETF Team에 새 analyst를 추가해도 Stock
  Team은 영향받지 않아야 한다). 이 부분은 공통화 대상이 아니다.
- **결론**: "checkpoint-aware 병렬 실행"만 진짜 중복이며, `run()`의
  나머지(어떤 job을 만들 것인가, 결과를 어떻게 조합할 것인가)는
  domain-specific이라 공통화하지 않는다.

## 4. Domain-specific Differences

공통화 이후에도 각 파일에 그대로 남아야 하는 부분(변경하지 않음):

- `SECTION_TAGS`, `_DATA_LIMITATION_NOTICE`, 각 analyst 함수와 그
  프롬프트 지시문 — 100% domain 고유.
- `wave1_jobs`/`wave2_jobs` **딕셔너리를 만드는 코드**(어떤 analyst를
  어떤 입력으로 부를지) — 팀마다 다른 리터럴이므로 각 파일에 유지.
- `report_writer_final_report` 호출과 `results`/`wave_summary` 조합 —
  팀별 반환 키 이름이 다르므로 유지.
- `run()`의 함수 시그니처(두 번째 인자 이름이 `company_label`/`fund_label`로
  다름) — 그대로 유지.

## 5. Commonization Decision

§3 기준으로 평가한 결과:

- **책임이 동일**: 예 — "이름별 job을 checkpoint 확인 후 병렬 실행"은
  세 파일 모두 정확히 같은 의미.
- **입력/출력 의미가 동일**: 예 — 입력은 `Checkpointer` + `{name: (fn, arg)}`,
  출력은 `{name: 결과}` + 소요 시간, 세 파일 모두 동일한 형태로 소비.
- **향후 변경 시 동일하게 변경돼야 함**: 예 — 재시도/동시성 정책
  변경은 세 팀에 항상 동일하게 적용돼야 한다(팀마다 다르게 둘 이유가
  없음, 실제로 지금까지 항상 동일하게 복사돼 왔다는 사실 자체가 근거).
- **abstraction이 의미를 명확하게 함**: 예 — 이 블록을 이름 있는
  함수로 뽑으면 `run()`을 처음 읽는 사람이 "checkpoint/병렬 실행
  디테일"을 건너뛰고 바로 "이 팀이 어떤 analyst를 어떤 순서로
  부르는가"를 볼 수 있다.
- **파라미터가 지나치게 많아지는가**: 아니다 — `(cp, jobs)` 2개
  파라미터로 충분하다.
- **호출부가 더 이해하기 어려워지는가**: 아니다 — 원래 12줄이던
  블록이 `wave1_results, wave1_elapsed = run_checkpointed_wave(cp, wave1_jobs)`
  한 줄이 되어 오히려 "이 Wave가 무엇을 하는지"(job dict를 만들고
  실행한다)가 더 잘 보인다.
- **indirection이 증가하는가**: 최소한만 — 함수 정의를 보려면
  `checkpoint.py` 1개 파일만 열면 된다(이미 세 팀이 `Checkpointer`/
  `run_step`을 그 파일에서 import하고 있어 새 파일을 왕복하지 않는다).

→ **공통화한다.** 대상은 정확히 "checkpoint 확인 → 병렬 실행 → 결과
수집" 6곳뿐이며, `wave1_jobs`/`wave2_jobs` 생성 로직이나 결과 조합
로직은 공통화하지 않는다(§4).

## 6. Refactoring Design

- **위치**: 새 파일/새 모듈을 만들지 않고 기존 `hqs/investment/checkpoint.py`에
  함수를 추가했다 — 이 파일은 이미 세 팀이 공유하는 `Checkpointer`/
  `run_step`을 담고 있고, `trader.py::run_trader_decision()`도 같은
  방식으로 `checkpoint.run_step`을 감싸는 공유 wrapper를 제공하는
  선례가 있다(동일 저장소 관례를 따름, 새 framework 아님).
- **이름**: `run_checkpointed_wave(cp, jobs)` — "checkpoint를 확인하며
  하나의 Wave(job 묶음)를 실행한다"는 실제 책임을 그대로 표현한다.
  일반적인 `run_parallel`/`execute_jobs` 같은 generic 이름은 피했다
  (checkpoint 확인이 이 함수의 핵심 의미이기 때문).
- **시그니처**: `(cp: Checkpointer, jobs: dict) -> tuple[dict, float]` —
  파라미터 2개로 최소화, 반환값은 원래 코드가 만들던
  `(wave*_results, wave*_elapsed)` 튜플과 순서·의미를 그대로 맞췄다.
- **채택하지 않은 방향**: generic manager/pipeline framework, base
  class, strategy pattern, registry, factory, configuration layer는
  전부 사용하지 않았다 — 이 저장소의 세 팀은 항상 "job dict → 병렬
  실행 → 결과 dict"라는 하나의 고정된 실행 모델만 쓰므로, 그 이상의
  일반화는 실제로 쓰이지 않을 유연성을 미리 만드는 것이라 판단했다
  (Wave 2 Audit §3 "abstraction ≠ 무조건 나쁜 것"의 반대 방향 적용 —
  여기서는 작은 함수 하나가 충분하다).

## 7. After Structure

`checkpoint.py`(신규 함수, 다른 함수는 무변경):

```python
def run_checkpointed_wave(cp: Checkpointer, jobs: dict) -> tuple[dict, float]:
    t0 = time.monotonic()
    results = {}
    pending = {name: value for name, value in jobs.items() if not cp.has(name)}
    for name in jobs:
        if cp.has(name):
            results[name] = cp.load(name)
    if pending:
        with ThreadPoolExecutor(max_workers=len(pending)) as pool:
            futures = {name: pool.submit(run_step, cp, name, fn, arg) for name, (fn, arg) in pending.items()}
            for name, future in futures.items():
                results[name] = future.result()
    elapsed = time.monotonic() - t0
    return results, elapsed
```

세 팀 파일의 `run()`(예시, `stock_team.py`):

```python
wave1_jobs = {...}                                            # domain-specific, 무변경
wave1_results, wave1_elapsed = run_checkpointed_wave(cp, wave1_jobs)

...

wave2_jobs = {"bull_case": (...), "bear_case": (...)}          # domain-specific, 무변경
wave2_results, wave2_elapsed = run_checkpointed_wave(cp, wave2_jobs)
```

`etf_team.py`/`dividend_stock_team.py`도 동일 패턴이며, 각 파일의
`wave1_jobs`/`wave2_jobs` 리터럴과 이후 결과 조합 코드는 그대로다.

세 파일에서 더 이상 쓰지 않게 된 `from concurrent.futures import
ThreadPoolExecutor` import를 제거했다(그 책임이 `checkpoint.py`로
이동했으므로).

## 8. Behavior Preservation

- **checkpoint semantics**: `cp.has(name)`으로 pending 필터링 → 완료된
  step은 `cp.load(name)` → 나머지만 `run_step` 실행, 순서와 조건 전부
  원본과 1:1 동일(변수명만 `n`→`name`, `pending`/`pending2`→`pending`
  으로 통일했으나 로직은 동일).
- **execution order**: `jobs`(Python 3.7+ dict, 삽입 순서 보존) 순회
  순서로 완료분 로드 → pending만 병렬 제출, 원본과 동일.
- **parallelism semantics/worker count**: `ThreadPoolExecutor(max_workers=len(pending))`
  그대로 — pending 개수만큼 worker를 쓰는 정책 무변경.
- **timeout/retry**: 원본에 없던 것을 추가하지 않았다(원본도 timeout/
  retry 로직이 없었음 — `run_step`/`Checkpointer` 책임 그대로 위임).
  Wave 2 Audit §11에서 이미 언급했듯 이 파일에는 재시도/timeout 로직
  자체가 존재하지 않는다.
- **exception behavior**: `future.result()`가 예외를 그대로 전파하는
  동작 무변경(`run_step`이 `ContentFailureError`를 던지면 원본처럼
  `run_checkpointed_wave` 호출자까지 그대로 전파된다 — 새로운 `try`/
  `except`를 추가하지 않았음).
- **result ordering**: `results` dict의 키는 `jobs`와 동일한 이름
  집합, 세 팀의 이후 코드(`wave1_results["fundamental_analysis"]` 등)가
  키로 접근하므로 순서 자체는 관측되지 않는다(원본도 동일).
- **result schema**: `run()`의 최종 반환값(`{"results": {...}, "wave_summary": {...}}`)
  구조·키 이름 전부 무변경 — 이번 리팩터링은 `wave1_results`/
  `wave2_results`를 만드는 **과정**만 바꿨을 뿐 그 값의 사용처는
  건드리지 않았다.
- **state mutation**: `cp`(Checkpointer, 유일한 mutable 상태) 전달
  방식 무변경 — 이전과 동일하게 `run_step` 내부에서만 `cp.save()`가
  호출된다.
- **logging semantics**: `Checkpointer.save()`가 채우는 `call_log`
  구조 무변경, 팀 파일들의 `call_log.json` 기록 코드 무변경.
- **external API behavior**: OpenRouter/Engine 호출 경로(`engine_client.call_engine`)는
  전혀 건드리지 않았다.
- **public API**: `run()` 시그니처 3개 파일 모두 무변경, `Checkpointer`/
  `run_step`의 기존 시그니처 무변경(순수 함수 추가만).

## 9. Tests

- 리팩터링 전 baseline: `hqs/investment/tests/` 24 passed(3개 팀
  integration 테스트 + `test_checkpoint.py` 5개 + `test_trader.py` +
  `test_wave_failure_isolation.py` 포함).
- 리팩터링 후 동일 테스트 스위트 재실행 — **24 passed, 변화 없음**.
  이 중 `test_stock_team_integration.py`/`test_etf_team_integration.py`/
  `test_dividend_stock_team_integration.py`가 `run()`을 실제로
  호출하며 checkpoint 저장 파일 존재 여부, resume 시 재호출 안 됨,
  Trader 데이터 흐름을 검증하므로 이번 변경의 실제 risk(checkpoint
  skip, 병렬 실행 결과 취합)를 이미 커버한다.
- 신규 회귀 테스트는 추가하지 않았다 — 기존 integration 테스트가
  "checkpoint 있으면 재호출 안 함"(`test_resume_does_not_recall_trader`
  등)과 "병렬 실행 결과가 올바르게 조합됨"(전체 `run()` 성공 경로)을
  이미 직접 검증하고 있어 추가 위험 지점이 없다고 판단했다. 기존
  테스트의 assertion은 1개도 수정하지 않았다.

## 10. Validation

| 항목 | 결과 |
|---|---|
| Targeted tests(`hqs/investment/tests/`) | **24 passed**(변경 전/후 동일) |
| `hqs/` 전체 pytest | **380 passed, 6 skipped**(Wave 1/Wave 2 baseline과 동일, 회귀 없음) |
| `python3 -m py_compile`(4개 변경 파일) | 오류 0건 |
| `ast.parse()`(4개 변경 파일) | 오류 0건 |
| `git diff` 범위 | `checkpoint.py` + 3개 Team 파일, **4개 파일만** 변경 |
| Contract 검사 | `run()` 시그니처·반환 dict 키, `Checkpointer`/`run_step` 시그니처 무변경 |
| dependency/import 검사 | 3개 Team 파일에서 `ThreadPoolExecutor` import 제거(책임 이동), `checkpoint.py`에 `time`/`ThreadPoolExecutor` 추가 — 외부 신규 dependency 없음(둘 다 stdlib, 기존에도 사용 중이던 모듈) |

## 11. Architecture/Contract Check

- **대상 외 변경**: 0건 — `checkpoint.py` + 3개 Team 파일만 변경(§10).
- **public API 변경**: 0건 — `run()`(3개 팀), `Checkpointer`, `run_step`
  시그니처 전부 무변경. `run_checkpointed_wave`는 순수 추가.
- **return schema 변경**: 0건 — `run()`의 반환 dict 구조·키 무변경.
- **parallelism 변경**: 0건 — `ThreadPoolExecutor` 사용 방식·worker
  수 정책 무변경.
- **checkpoint semantics 변경**: 0건 — `cp.has`/`cp.load`/`run_step`
  호출 순서·조건 무변경.
- **exception behavior 변경**: 0건 — 신규 `try`/`except` 없음.
- **dependency boundary 변경**: 0건 — 세 팀 파일 모두 `checkpoint`
  모듈에서만 새 이름(`run_checkpointed_wave`)을 추가로 import했을 뿐,
  모듈 경계 자체(어느 파일이 어느 파일을 import하는지)는 이미 존재하던
  `checkpoint` 의존을 그대로 재사용했다 — 새 모듈/새 경계가 생기지
  않았다.
- **Architecture/Governance**: 무변경. Stage/Team responsibility,
  Investment HQ의 팀 구조·역할 분리에 영향 없음.

## 12. Conclusion

Wave 2 Audit이 C1로 확정한 "checkpoint 확인 → 병렬 실행 → 결과 수집"
중복 6곳을, 이미 세 팀이 공유하고 있던 `checkpoint.py`에 `run_checkpointed_wave()`
하나를 추가해 제거했다. Domain별 차이(어떤 analyst를 부르는지, 결과를
어떻게 조합하는지)는 각 팀 파일에 그대로 남겨 팀 간 독립적인 진화
가능성을 보존했다. `run()`의 public 시그니처·반환 schema·checkpoint/
병렬 실행 semantics·예외 처리는 모두 동일하게 유지됐으며, 전용
테스트 24개와 `hqs/` 전체 380 passed/6 skipped로 무회귀를 확인했다.
새 framework/class/generic abstraction은 도입하지 않았고, 공통 함수는
파라미터 2개짜리 순수 함수 하나로 최소화됐다.

## Related

- `docs/research/PYTHON-REFACTOR-WAVE-2-AUDIT-0001.md`(§10.1, §12 C1, §14)
- `docs/research/PYTHON-REFACTOR-WAVE-2-C2-0001.md`(같은 Wave 2의 앞선 IMPLEMENT 항목)
- `hqs/investment/tests/test_stock_team_integration.py`,
  `test_etf_team_integration.py`, `test_dividend_stock_team_integration.py`,
  `test_checkpoint.py`
