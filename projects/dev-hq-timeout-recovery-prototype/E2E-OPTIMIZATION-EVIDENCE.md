# Evidence — Dev HQ End-to-End 실행시간 최적화 검증

목표는 LLM 자체를 빠르게 만드는 것이 아니라, Dividend Stock Team류
11단계 파이프라인의 **end-to-end 완료시간**을 줄이는 것이다. PR
#74~76에서 이미 확인된 사실(Final Report 180초 타임아웃 반복 재현,
Checkpointing으로 실패 시 데이터 유실 0건 실증)을 출발점으로,
병렬화·호출 최적화·캐시·적절한 Timeout까지 네 축을 실측했다.
`development-hq/`는 이번에도 한 줄도 수정하지 않았다.

## BOTTLENECK — Workflow overhead vs LLM 대기시간

기존 PR #76 데이터(`trials/raised_timeout_trial{1,2}/`)를 재분석했다.

| 시행 | 총 wall time | 11개 호출 elapsed 합계 | overhead(Python/IO 등) |
|---|---|---|---|
| raised_timeout_trial1 | 514.8초 | 514.7초 | 0.1초(0.02%) |
| raised_timeout_trial2 | 631.8초 | 631.7초 | 0.1초(0.02%) |

**Workflow overhead(파일 읽기, 문자열 조립, 디스크 쓰기)는 사실상
0이다.** 총 소요시간의 100%가 `claude -p` 서브프로세스 자체의
대기시간(LLM 입력 처리 + 응답 생성)이다. 이는 다음 두 가지를
결정짓는다:
- project-local Python 코드(`runner.py` 류)를 아무리 최적화해도
  실질적 시간 절감은 없다 — 시간은 전부 Engine 호출 안에서 소모된다.
- 남은 유일한 레버는 **호출을 얼마나 동시에/적게 하는가**뿐이다 —
  이것이 병렬화와 호출 최적화를 우선 검증 대상으로 삼은 근거다.

추가로, 개별 호출의 `elapsed_sec`는 입력 길이보다 **출력 길이**와
더 강하게 연관된다는 것이 UUP/Nestlé/Toyota EVIDENCE.md에서 이미
반복 관찰됐고, 이번 데이터도 동일 패턴이다(예: Final Report는 입력이
비슷해도 출력이 클수록 오래 걸림) — 즉 병목은 "생성(generation)"
쪽이며, 이는 아래 CACHE 결론과 직결된다.

## PARALLELISM — Prototype C 실측

`parallel/parallel_runner.py`: 7개 분석(상호 독립) → Wave1 병렬,
Bull/Bear(상호 독립) → Wave2 병렬, Synthesis/Final Report는 원래
의존관계대로 순차 유지. `ThreadPoolExecutor`로 실제 OS 프로세스
수준 동시 실행을 냈다(각 호출이 `subprocess.run()` 대기 중 GIL을
반환하므로 진짜 병렬성). Workflow Parser/Scheduler는 만들지 않았다
— 4개 Wave 순서는 `runner.py`와 동일하게 코드에 하드코딩했고, 어떤
호출이 어느 Wave에 속하는지 런타임에 계산하지 않는다.

| Wave | 병렬 실측 | 동일 호출 순차 합산(비교 기준) | 속도 향상 |
|---|---|---|---|
| Wave1(7개 분석) | 47.0초 | 265.7초 | **5.65배** |
| Wave2(Bull/Bear) | 44.9초 | 89.7초 | **2.0배** |
| Wave3(Synthesis) | 74.5초(순차, 변경 없음) | — | — |
| Wave4(Final Report) | 111.6초(순차, 변경 없음) | — | — |
| **파이프라인 총합** | **278.0초** | **541.5초**(같은 4개 값을 순차로 더한 값) | **1.95배(48.7% 단축)** |

이 결과는 사전 이론 예측(raised_timeout_trial1의 개별 elapsed로
"Wave별 max"만 더한 값 ≈ 261.7초)과 거의 일치해, 병렬화 효과가
우연이 아니라 재현 가능한 구조적 절감임을 확인한다. **역할 지시문,
Team 구조, Capability 어느 것도 바꾸지 않았다** — 오직 "언제
호출하는가"만 바꿨다. `final_report.md`에 Disclaimer가 그대로
포함되는 등 산출물 품질도 유지됨을 확인했다(동일 품질 조건 충족).

**주의**: 병렬화는 Wave3/Wave4(Synthesis, Final Report)의 개별
호출 시간 자체는 줄이지 못한다 — 이 둘은 의존관계상 항상 순차다.
이번 실행에서도 Final Report(111.6초)는 여전히 180초에 근접했고,
누적 관측(67.6~324.2초, PR #74~76 전체 실행 기준)으로는 180초를
넘는 사례가 반복됐다 — **병렬화가 정상 실행시간은 크게 줄여도,
Final Report 타임아웃 위험 자체를 없애지는 못한다.** 이 위험을
줄이는 것은 여전히 Checkpointing(피해 최소화)이나 Timeout 상향
(발생 완화)의 몫이다.

## CALL_OPTIMIZATION — 제거 가능한 호출 탐색(데스크 분석)

11개 호출 각각이 `docs/research/DIVIDEND-STOCK-TEAM-DEFINITION-0001.md`
에 정의된 서로 다른 역할(Fundamental/Dividend Quality/Valuation/
Technical/Industry-Competition/News-Event/Sentiment/Bull Researcher/
Bear Researcher/Portfolio Synthesis/Report Writer)에 정확히 대응한다.
**Role 구조를 바꾸지 않고 제거할 수 있는 호출은 발견되지 않았다** —
예컨대 "Synthesis를 Final Report에 흡수해 10개로 줄인다"는 방안은
코드량은 줄일 수 있으나 두 개의 독립된 정의된 역할(Portfolio
Synthesis, Report Writer)을 하나로 합치는 것이므로 Capability/Role
구조 변경(Architecture 영역)이 되어 이번 범위(RFC 없이 구현 금지)
밖이다. **결론: 호출 수 자체를 줄이는 최적화는 이번 Team 구조
내에서는 안전한 후보가 없다** — 병렬화가 더 안전하고 효과도 큰
축이다.

부차 관찰(구현하지 않음, 기록만): 7개 분석 호출 모두에 공통
`_DATA_LIMITATION_NOTICE` 문자열이 매번 반복 포함된다(내용은 몇
줄 수준으로 작아 실질적 시간 절감 효과는 미미할 것으로 추정 —
BOTTLENECK에서 확인했듯 입력 길이보다 출력 길이가 소요시간을
지배하므로).

## CACHE — 실측 진단(engine.py 미수정, 진단 호출만)

`claude -p ... --output-format json`(engine.py를 거치지 않는 순수
진단 호출, Bash에서 직접 실행)로 실제 캐시 토큰 사용량을 확인했다:

```
"usage": {
  "cache_creation_input_tokens": 4424,
  "cache_read_input_tokens": 27108,
  ...
}
```

**일부 캐싱은 이미 자동으로 발생하고 있다** — 각 호출에 공통되는
CLI/시스템 프롬프트 수준의 콘텐츠(도구 차단 목록, `STATELESS_CALL_NOTICE`
등)로 추정된다. 그러나 이는 project-local 코드가 통제하는 지점이
아니며(Anthropic API/CLI 인프라 레벨), **project-specific 데이터
(raw_data.md의 각 섹션, 역할별 instruction)는 호출마다 전부 달라
캐시 재사용 대상이 아니다.**

더 중요한 점: BOTTLENECK에서 확인했듯 소요시간은 **입력 처리가
아니라 출력 생성**이 지배한다. 프롬프트 캐시는 입력 토큰 처리
비용/レ이턴시를 줄이는 메커니즘이지 출력 생성 시간을 줄이지 않는다
— 즉 **캐시 적중률을 인위적으로 높이더라도 이번 파이프라인의
실질적 E2E 병목(생성 시간)에는 효과가 제한적**이라는 결론이다.
Cache는 이번 파이프라인의 주요 최적화 축이 아니다(PR #74~76에서
반복 관찰된 "Cache: 발생하지 않음"과 모순되지 않는다 — 그 관찰은
project-data 재사용이 없다는 뜻이었고, 이번 진단은 그와 별개인
CLI 레벨 캐시가 이미 일부 존재함을 보였을 뿐, 결론은 동일하게
"실질적 레버 아님"이다).

## CHECKPOINT — 재확인(PR #76 재사용)

PR #76에서 실측 검증된 결과를 그대로 재사용한다(재실험하지 않음,
"현재 Evidence가 입증한 효과를 우선 활용" 지시에 따름):
- 자동 복구 0/11 → Checkpointing 적용 시 실측 데이터 유실 0건
- 재개 시 완료 단계는 Engine을 재호출하지 않음(`elapsed_sec` 불변으로
  증명됨)
- 실패 반복 시나리오(4회 호출: 강제중단 1 + 자연 타임아웃 2 + 성공 1)
  총 비용 약 867초 — **매번 전체 재실행하는 것보다 낮음**

**이번 검증에서 확인된 새 사실**: 병렬화를 적용해도 Wave3/4(특히
Final Report)의 개별 실패 위험은 남으므로, Checkpointing은 병렬화
이후에도 여전히 유효한 방어선이다 — 오히려 병렬화로 Wave1/2가 훨씬
짧아지면서, 실패가 나더라도 "다시 재현해야 할 앞단 작업"의 절대
시간이 더 줄어든다(Checkpointing 없이 전체 재실행하더라도 병렬화
덕분에 재실행 자체가 빨라짐 — 두 최적화가 서로를 보완한다).

## TIMEOUT — 보조 수단으로 재확인

PR #75/#76 결론을 그대로 유지한다: Timeout 상향은 속도 향상 수단이
아니라 **불필요한 실패·재실행을 줄이는 보조 수단**이다. 병렬화로
Wave1/2의 개별 호출 시간이 크게 줄었지만(각 47초, 45초 — 180초에서
멀리 떨어짐), Wave3/4는 여전히 180초 경계 부근에서 변동한다
(Final Report 관측 범위: 67.6~324.2초). Timeout 상향 자체를 다시
구현/실험하지 않았다(PR #76에서 이미 검증 완료, 재사용).

## E2E_TIME — 정상 실행 vs 실패 후 총 소요시간 구분

| 시나리오 | 개선 없음(원본 순차) | 병렬화만 | 병렬화+Checkpointing(권고 조합, 미구현) |
|---|---|---|---|
| **정상 실행**(실패 없음) | 514.8~631.8초(raised_timeout 실측) / 264.8초(checkpoint trial1, 변동성 반영) | **278.0초**(실측, 최대 관측 대비 약 45~56% 단축) | 병렬화와 동일(Checkpointing은 정상 실행시간에 영향 없음) |
| **실패 1회 후 총 소요**(Final Report에서 타임아웃) | 전체 11단계 재실행(약 500~600초) + 재실패 시 반복 누적(Nestlé 실측 6회 반복) | 전체 재실행하되 병렬화로 앞단이 빨라짐(약 92~170초, Wave1+Wave2만) + Final Report 재시도(최대 180초) | **실패한 단계만 재시도**(최대 180초) — Wave1~3 재실행 불필요(Checkpointing 실측) |

**정상 실행시간 단축**은 병렬화가 실측으로 입증(48.7%, 1.95배).
**실패 후 총 소요시간 단축**은 Checkpointing이 실측으로 입증(PR
#76, 반복 실패에도 완료 단계 유실 0건). 두 축은 서로 다른 문제를
풀며 상호 배타적이지 않다 — **병렬화+Checkpointing을 함께 쓰는 것이
이론상 최선**이라는 결론이나, 이 조합 자체는 이번 실행에서 직접
구현/실측하지 않았다(개별 두 축은 각각 실측 완료, 조합은 추정).

## DECISION

**우선순위: 병렬화(정상 실행시간) > Checkpointing(실패 시 피해
최소화) > Timeout 상향(보조) > 캐시(효과 제한적) > 호출 자체 제거
(안전한 후보 없음).**

근거:
1. 병렬화는 Architecture/Role/Capability를 전혀 바꾸지 않고 실행
   순서만 바꿔 **정상 케이스에서 절반에 가까운 시간을 실측으로
   절감**했다 — 투자 대비 효과가 가장 크고 리스크가 가장 낮다.
2. Checkpointing은 PR #76에서 이미 "더 작은 변경으로 실제 문제를
   해결"로 판정됐고, 이번에도 그 결론이 재확인된다 — 병렬화 이후에도
   여전히 필요하다(Wave3/4의 잔존 타임아웃 위험).
3. Timeout 상향은 여전히 보조 수단이다 — 데이터 유실을 해결하지
   못하고 Dev HQ Frozen 파일 수정이 필요하다.
4. 캐시는 이번 파이프라인의 병목(출력 생성)에 구조적으로 도달하지
   못해 우선순위가 낮다.
5. 호출 자체를 줄이는 것은 Role 구조를 건드리므로 이번 범위에서
   제외한다.

**이 우선순위는 권고이며, 어떤 구현도 이번 실행에서 채택하지
않았다.**

## GOVERNANCE

- `development-hq/` 어떤 파일도 수정하지 않았다. Prototype C도
  진짜 `call_engine()`(180초, 미수정)을 그대로 썼다.
- 병렬화를 project-local `runner.py` 패턴으로 실제 도입하는 것은
  Capability/Role 자체를 바꾸지 않으므로(호출 순서만 변경) RFC가
  반드시 필요한 Architecture 변경은 아닐 수 있다는 판단이나, 이는
  판단일 뿐 이번에 RFC를 작성하지도, 패턴을 실제 채택하지도 않았다.
- Checkpointing의 GOVERNANCE 판단은 PR #76과 동일하게 유지한다.
- Architecture/Contract/Governance 문서는 이번에도 전혀 수정하지
  않았다.

## PHASE9_11

이번 검증으로 "무엇을 먼저 해야 하는가"에 대한 Evidence 기반
우선순위(병렬화 → Checkpointing → Timeout 상향)가 마련됐지만,
**실제 구현 착수나 Phase 9~11 재개는 사용자 승인 없이 진행하지
않는다.** 다음 결정은 사용자 몫이다: (a) 병렬화를 project-local
표준 패턴으로 채택할지, (b) Checkpointing과 함께 도입할지, (c) 이
우선순위 자체를 다르게 판단할지.

## 관찰되지 않은 것 (명시적으로 기록)

- 병렬화+Checkpointing 조합을 실제로 함께 구현·실측 — 시도하지 않음
  (두 축 각각의 개별 실측만 완료).
- 병렬화의 반복 재현성(3회 이상 시행을 통한 통계적 신뢰도) — 1회
  실측 + 이론치 교차검증으로 대체(최소 Prototype 원칙, 이론과 실측이
  근접해 추가 시행의 한계효용이 낮다고 판단).
- Wave1 내에서 7개보다 더 세밀한 배치(예: 3+4 분할) 등 다른 병렬화
  전략 비교 — 시도하지 않음(현재 의존관계상 7개 전부가 동시에
  가능하므로 추가 분할의 이점 없음).
- 캐시를 프로젝트 데이터 레벨에서 강제로 늘리는 방안(예: 공통 프리픽스
  재구성) — 병목이 출력 생성이라는 결론에 따라 시도하지 않음.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다.
`parallel_runner.py`는 실행 순서만 바꾸는 project-local 스크립트이며
Role/Capability/지시문을 전혀 바꾸지 않았고, 범용 Workflow Parser/
Scheduler도 만들지 않았다(4-wave 순서 하드코딩). 새 Capability, 새
Agent, 새 Kernel Component, 새 Contract를 만들지 않았다. v1.0
Freeze를 해제하지 않았다. RFC/ADC/ADR 문서를 작성하지 않았다(필요
여부 판단만 기록). 구현 채택도, Phase 9~11 재개도 하지 않았다.
