# Evidence — Toyota Dividend Stock Dogfooding (Dev HQ timeout/recovery 재현성 검증)

이 실행의 목적은 Toyota 분석 자체나 Dividend Stock Team 역할 검증이
아니다(그 검증은 `projects/dividend-stock-analysis-nestle`에서 이미
완료·판정됨). 목적은 **Nestlé에서 관찰된 Final Report
`ENGINE_TIMEOUT_SECONDS`(180초) 타임아웃이 다른 종목/데이터에서도
재현되는지, 그리고 타임아웃 시 `runner.py`가 중간 산출물을 실제로
얼마나 보존하는지**를 코드 레벨로 검증하는 것이다. Team/Role/
Architecture는 전혀 변경하지 않았다(Nestlé의 `agents.py`/`runner.py`를
회사명/티커/경로만 바꿔 그대로 복제).

## TIMEOUT 재현성 — 서로 무관한 두 종목에서 총 8회 관찰

| 실행 | 시도 | 방식 | 결과 |
|---|---|---|---|
| Nestlé | 1~5차 | `runner.py` 전체 파이프라인(180초 제한) | 전부 Final Report에서 `TimeoutExpired` |
| Nestlé | 6차 | `retry_final_report.py`(Final Report만 재시도, 180초 제한 유지) | `TimeoutExpired` |
| Nestlé | 진단 | `claude -p` 직접 호출(180초 제한 우회, 400초 wrapper) | **성공, 324.2초** |
| Toyota | 1차 | `runner.py` 전체 파이프라인(180초 제한) | Final Report에서 `TimeoutExpired` |
| Toyota | 진단 | `claude -p` 직접 호출(180초 제한 우회, 400초 wrapper) | **성공, 153.8초** |
| Toyota | 2차(재검증) | `runner.py` 전체 파이프라인(180초 제한, 재실행) | Final Report에서 다시 `TimeoutExpired` |

**결론: 완전히 다른 두 종목(스위스 식품/연배당 vs 일본 자동차/반기배당),
완전히 다른 raw_data로 총 8회 시도 중 7회가 정확히 동일한 단계
(Final Report)에서 재현됐다.** 이는 project-local 콘텐츠 한 건의
특이 현상이 아니라 **Dev HQ 인프라(`ENGINE_TIMEOUT_SECONDS=180` +
project-local Final Report의 누적 입력 설계) 수준에서 반복 가능한
경계 문제**임을 확인한다.

### 두 종목 간 성격 차이 — 단일 원인이 아님을 시사

- **Nestlé**: 진단 성공 시간 324.2초 — 180초 대비 +80%, 명확하고
  큰 폭의 초과. 6회 전부 실패, "재시도하면 이번엔 될 것"이라는 기대가
  통하지 않았다.
- **Toyota**: 진단 성공 시간 153.8초 — 오히려 180초 미만. 그런데도
  정식 파이프라인 경로(`call_engine()`)로는 1차·2차 모두 실패했다.
  이는 **동일 콘텐츠라도 호출마다 실제 소요시간이 상당히 변동**한다는
  것을 시사한다(진단 호출과 정식 재시도는 같은 프롬프트를 쓰지만
  서로 다른 별개의 Engine 호출이므로 결과 텍스트/소요시간이 다를 수
  있음).
- **종합 판단**: 원인은 하나가 아니라 최소 두 겹이다 — (1) Nestlé처럼
  콘텐츠 자체가 구조적으로 180초를 초과하는 경우, (2) Toyota처럼
  180초 경계선 부근에서 호출 간 변동성 때문에 성공/실패가 갈리는
  경우. 둘 다 원인은 project-local 데이터가 아니라 **Engine 호출의
  소요시간 분포가 180초라는 고정 상수와 자주 충돌하는 것** — Dev HQ
  경계 문제로 분류하는 근거가 된다.

## RECOVERY — 코드 레벨 구조 분석 (자동 복구 0/11, 수동 복구는 실패 지점에 좌우)

`runner.py`(Nestlé/Toyota 동일 구조, `development-hq/` 밖의
project-local 파일이므로 이 분석 자체가 코드 수정이 아님)를 직접
읽어 확인한 사실:

- `_call_log`는 in-memory 리스트이며 `_timed()`가 `fn()`이 **정상
  반환한 뒤에만** append한다. 타임아웃으로 예외가 발생하면 그 호출의
  로그는 애초에 기록되지 않는다.
- 11개 결과 파일과 `call_log.json`은 **`run()` 함수의 맨 마지막,
  11단계 전부가 예외 없이 끝난 뒤 한 번에만** 디스크에 쓰인다
  (all-or-nothing). 10단계까지 전부 성공했어도 11번째에서 예외가
  나면 **디스크에는 파일이 단 하나도 생기지 않는다** — Nestlé/Toyota
  둘 다 `issues/*/` 디렉터리가 실패 직후에는 `raw_data.md` 외
  아무것도 없었다(직접 확인).
- **자동 복구는 0/11 — 어떤 단계도 실패 시 자동으로 보존되지 않는다.**

### 수동 복구 가능 여부는 "어느 단계가 실패했는가"에 전적으로 좌우된다

각 단계의 프롬프트가 무엇을 인자로 받는지에 따라, 실패 시 Python
예외 트레이스백(`subprocess.run(['claude','-p', prompt, ...])`의
인자 목록이 그대로 출력됨 — Python 표준 동작이지 설계된 기능이
아님)에 **직전 단계들의 결과 텍스트가 우연히 포함되는지**가 갈린다:

| 실패 단계 | 그 단계의 프롬프트 인자 | 트레이스백에서 복구 가능한 것 | 복구 불가능한 것 |
|---|---|---|---|
| 7개 개별 분석(Fundamental~Sentiment) 중 하나 | `raw_data.md`의 해당 소섹션만(수백~1천여 자) | 없음(그 섹션 자체는 raw_data.md에 이미 있어 새로 얻을 정보 없음) | 그 호출 자체의 출력, 그 이전 단계들의 출력(애초에 그 단계 프롬프트에 포함 안 됨) |
| Bull Case | `all_analyses`(7개 분석 concat) | 7개 분석 텍스트 | Bull Case 자신의 출력 |
| Bear Case | `all_analyses`(7개 분석 concat, Bull Case는 **포함 안 됨**) | 7개 분석 텍스트(Bull과 동일한 것 재복구) | Bear Case 자신의 출력, **이미 성공한 Bull Case 출력(프롬프트에 없어서 유실)** |
| Synthesis | `bull_case + bear_case` | Bull/Bear Case 텍스트 | Synthesis 자신의 출력, **이미 성공한 7개 분석(프롬프트에 없어서 유실)** |
| Final Report | 10개 산출물 전체(7개 분석+Bull+Bear+Synthesis) | **10개 산출물 전부**(이번 Nestlé·Toyota 실행이 여기 해당) | Final Report 자신의 출력만 |

**따라서 "몇 단계까지 성공했나"와 "몇 단계를 복구할 수 있나"는
비례하지 않는다.** 이번 두 실행이 우연히 가장 마지막 단계(Final
Report, 모든 것을 인자로 받는 유일한 단계)에서 실패했기 때문에
"10/11 완전 복구"라는 최선의 결과를 얻었을 뿐이다. 만약 예컨대
Bear Case나 Synthesis에서 타임아웃이 났다면, 이미 계산이 끝난
분석/Bull Case조차 유실되어 처음부터 다시 실행해야 했을 것이다.

### 실제로 유실된 것 (두 실행 공통)

- **타이밍 데이터(`call_log.json`)는 어느 경우든 100% 유실된다** —
  트레이스백에는 텍스트만 있고 `_call_log`의 elapsed/input_chars/
  output_chars는 in-memory에서만 존재하다 프로세스 종료와 함께
  사라진다. 이번 두 `EVIDENCE.md`의 "call_log.json"이 표준 형식이
  아니라 수기 재구성 노트인 이유가 이것이다.
- 복구는 **완전히 수동**이다 — 에이전트가 트레이스백 로그 파일에서
  프롬프트 문자열을 찾아 이스케이프를 복원하고, 알려진 섹션 태그로
  문자열을 잘라 각 파일에 저장하는 스크립트를 즉석에서 작성해야
  했다. `runner.py`/`engine.py` 어디에도 이런 복구를 지원하는
  코드는 없다.

## DATA_LOSS — Checkpointing 필요성 판단

**필요성이 실제로 확인됐다.** 근거:
1. All-or-nothing 저장 구조가 두 실행 모두에서 실제로 관찰됐다
   (가정이 아니라 실측).
2. 복구 가능 여부가 "어느 단계가 실패했는가"라는 우연에 좌우된다 —
   이번엔 운 좋게 마지막 단계였을 뿐, 설계된 안전장치가 아니다.
3. Final Report가 아닌 다른 단계(특히 Bear Case/Synthesis)에서
   실패하면 이미 완료된 작업(최대 9단계, 전체의 80% 이상)까지
   통째로 재실행해야 한다 — 이번 관찰 범위 밖이지만 코드 구조상
   확실히 발생 가능한 시나리오다.

다만 **이번 실행에서 checkpointing을 구현하지 않는다** — 사용자
지시("retry/checkpointing을 아직 구현하지 않는다")와 v1.0 Freeze에
따라 필요성 판단까지만 하고 실제 구현은 하지 않는다.

## AUTOMATION_CANDIDATE — 실제 반복 횟수와 비용

- **반복 횟수**: Nestlé 6회 + Toyota 2회 = **파이프라인 재실행
  8회**(그중 7회가 Final Report에서 실패). 여기에 진단 목적의 직접
  호출 2회(Nestlé 1회, Toyota 1회)가 추가로 발생했다.
- **비용(시간)**: 실패한 시도마다 앞 10단계(성공)를 처음부터 다시
  실행해야 했다 — 10단계 자체의 소요시간은 유실되어 정확한 합산은
  불가능하지만, JNJ(414.1초)·Nestlé/UUP 유사 사례(약 350~400초)를
  참고하면 **10단계만으로도 매 재시도마다 약 300~400초가 추가로
  소모됐을 것으로 추정**된다(추정치임을 명시, 실측 아님). 여기에
  Final Report 자체의 180초(타임아웃까지 대기) 또는 150~325초(성공
  시)가 더해진다.
- **비용(리소스)**: 매 재시도가 독립적인 `claude -p` 서브프로세스를
  처음부터 새로 기동한다 — 캐시 재사용 없음(두 실행 모두 6/6, 8/8
  기준 Cache 미발생과 일치).
- **결론**: "실패 시 마지막 성공 단계부터 재개하는 자동
  재시도/체크포인팅"이 있었다면, 8번의 전체 재실행 대신 Final
  Report 단계만 최대 몇 차례 재시도하는 것으로 끝났을 것 — 반복
  비용이 실측 기준으로도 상당하다는 것이 이번에 확인됐다.
- **지금 구현하지 않는다**: automation-candidate-watch 관찰
  기록으로만 남기고, 사용자 승인 없이 자동화를 구현하지 않는다(지시
  사항 준수).

## PHASE9_11 — 곧바로 재개하지 않고 책임 경계 먼저 판단

두 문제(타임아웃 반복 재현, 중간 산출물 유실 위험)가 모두 실제로
재현됐지만, 아래 이유로 **Phase 9~11을 곧바로 재개하지 않는다**:

- **Invest HQ 문제와 Dev HQ 문제가 명확히 분리된다.** Dividend Stock
  Team의 7개 역할·지시문·데이터 해석 능력에는 이번 두 실행에서
  아무 결함도 발견되지 않았다(오히려 Toyota의 raw_data에 있는 연간/
  분기 실적 방향 불일치, P/E 소스 불일치, 목표주가 3중 불일치를
  각 역할이 정확히 자기인정했다 — Nestlé와 동일한 패턴). 이번에
  확인된 것은 **Engine 호출 인프라(`development-hq/mvp/engine.py`)와
  project-local 파이프라인 저장 구조(`runner.py`)의 경계 문제**이지,
  Dividend Stock Team이나 다른 Investment HQ Team의 역할 결함이
  아니다.
- **v1.0 Freeze를 임의로 해제하지 않는다.** 이번 Evidence는
  `ENGINE_TIMEOUT_SECONDS`를 올리거나 `runner.py`에 체크포인팅을
  추가할 근거는 마련했지만, 그 실행 자체는 RFC → ADC → ADR 절차
  또는 최소한 사용자의 명시적 승인을 거쳐야 한다 — 지금 이 Evidence
  만으로 Dev HQ 코드를 고치지 않는다.
- **Phase 9~11 재개는 이 개선(또는 개선 보류 결정)이 먼저 확정된
  뒤에 논의한다.** 두 문제를 "Dev HQ 개선 후보"로 승격 보고하는
  것까지가 이번 작업의 범위이며, 실제 코드 변경/Phase 진행 여부는
  사용자 판단 사항으로 남긴다.

## ARCHITECTURE/GOVERNANCE — RFC/ADC/ADR 필요 여부만 판단

- **RFC 필요 여부**: `ENGINE_TIMEOUT_SECONDS` 상향이나 `runner.py`류
  파이프라인의 체크포인팅 도입은 `development-hq/mvp/engine.py`
  자체(Frozen Architecture는 아니지만 v1.0 Freeze 대상) 또는
  project-local 파이프라인 패턴 전반에 영향을 미치는 변경이므로,
  **실제로 시행한다면 RFC → ADC → ADR 절차를 거치는 것이 적절하다고
  판단**된다(이번 Evidence가 그 RFC의 근거 자료가 될 수 있음).
- **지금 RFC를 작성하지 않는다** — 사용자가 명시적으로 요청하지
  않았고, 이번 작업 범위는 "재현성 검증과 보고"로 한정됐다.
- Architecture/Contract/Governance 자체는 변경하지 않았다.

## 관찰되지 않은 것 (명시적으로 기록)

- 7개 개별 분석 단계·Bull/Bear/Synthesis 단계에서의 타임아웃 — 이번
  두 실행 모두 Final Report에서만 발생, 다른 단계의 실패 시나리오는
  실측되지 않고 코드 분석으로만 추론했다(위 RECOVERY 표 참조).
- Checkpointing 실제 구현 — 이번 범위 밖.
- 3번째 이상 종목에서의 재현 — 이번 두 종목(Nestlé, Toyota)으로
  충분한 재현성 신호를 확보했다고 판단해 추가 종목 실행은 하지
  않았다(비용 대비 한계효용 판단, 임의 중단 아님).

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다(코드 읽기와
진단용 `claude -p` 직접 호출만 수행, `engine.py`/`runner.py` 자체는
불변). 새 Capability, 새 Agent, 새 Kernel Component, 새 Contract를
만들지 않았다. v1.0 Freeze를 해제하지 않았다. RFC/ADC/ADR 문서를
작성하지 않았다(필요 여부 판단만 위에 기록). Governance/Boundary
판단 변경이 필요한 지점은 발견되지 않았다 — 발견된 것은 Dev HQ
개선 후보이며, 그 실행 여부는 사용자 판단으로 남긴다.
