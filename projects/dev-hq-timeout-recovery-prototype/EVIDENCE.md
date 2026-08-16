# Evidence — Dev HQ Timeout/Recovery 개선 Prototype 비교

PR #74/#75(EVIDENCE.md)에서 확정된 두 문제 — (1) Final Report
`ENGINE_TIMEOUT_SECONDS`(180초) 타임아웃 반복 재현, (2) `runner.py`의
all-or-nothing 저장 구조로 인한 데이터 유실 — 에 대해 두 개선안을
**실제 구현 전에** 최소 Prototype으로 검증했다. 두 Prototype 모두
동일한 장시간 Task(`shared/raw_data.md` = Nestlé raw_data, Final
Report가 180초를 안정적으로 초과하는 것으로 이미 확인된 콘텐츠)를
사용했다.

## TIMEOUT — Prototype A(Timeout 상향, 400초) 결과

| 시행 | 결과 | Final Report 소요 | 비고 |
|---|---|---|---|
| trial1 | 성공 | 97.4초 | 180초 이내 — 애초에 상향이 필요 없었던 사례 |
| trial2 | 성공 | 238.7초 | **180초 초과** — 원래 제한이었다면 실패했을 사례, 상향이 실제로 효과를 냈다 |

2/2 성공(실패율 0%). 다만 표본 2회이므로 "항상 성공"을 보장하지
않는다 — 원본 Nestlé 실행(6/6 실패)에서 이미 관측했듯 소요시간
자체가 호출마다 크게 변동하며, 400초라는 상한도 절대적 보장은
아니다(이론상 400초를 넘는 응답도 배제할 수 없음).

## CHECKPOINT — Prototype B(Checkpointing, 180초 그대로) 결과

| 시행 | 결과 | 비고 |
|---|---|---|
| trial1 | 11/11 성공(신규 실행) | 자연 타임아웃 없이 완주, 264.8초. 단계별 체크포인트 파일이 실행 중 실시간으로 쌓이는 것을 확인 |
| resume_test 1차 호출 | 3단계 완료 시점에 **의도적으로 강제 중단**(SIGTERM) | 체크포인트 3개(fundamental/dividend_quality/valuation) + `manifest.json`이 디스크에 보존됨을 확인 |
| resume_test 2차 호출(재개) | 1~3단계 스킵, 4~10단계 신규 실행 후 **Final Report 자연 타임아웃** | 10단계 전부 보존 확인. 스킵된 1~3단계의 `elapsed_sec`가 최초 값(19.4/44.0/31.4초)과 정확히 동일 — Engine 재호출 없이 디스크에서 로드된 직접 증거 |
| resume_test 3차 호출(재개) | 1~10단계 전부 스킵, Final Report만 재시도 → **다시 타임아웃** | 10단계 유실 없음 재확인 |
| resume_test 4차 호출(재개) | 1~10단계 전부 스킵, Final Report만 재시도 → **성공**(120.3초) | 11/11 완주, top-level 산출물 정상 기록 |

**재개(resume) 기능이 4회의 실제 호출을 통해 완전히 검증됐다** — 매
호출마다 `steps_skipped_via_checkpoint_this_invocation`이 정확히
이미 완료된 단계와 일치했고, 스킵된 단계는 Engine을 한 번도 다시
호출하지 않았다(타이밍 값 불변으로 증명).

## DATA_LOSS 비교 (원본 runner.py 대비)

| | 원본 `runner.py`(PR #74/#75 실측) | A: Timeout 상향 | B: Checkpointing |
|---|---|---|---|
| 실패 시 유실되는 완료 단계 수 | **전부**(all-or-nothing, 예외 시 디스크에 파일 0개) | 여전히 전부(구조 안 바꿈) — 다만 실패 자체가 줄어듦 | **0개**(실측: 3단계, 이어서 10단계 보존을 각각 직접 확인) |
| 복구 가능 여부 | 실패 지점이 우연히 마지막 단계일 때만(트레이스백 파싱, 완전 수동) | 해당 없음(실패 안 나면 복구할 것도 없음) | **자동**(재실행 시 스스로 스킵) |
| 타이밍 데이터(call_log) 유실 | 100% | 실패 시 100%(구조 안 바꿈) | **0%**(각 단계 완료 즉시 manifest에 기록) |

## RECOVERY 비교 — 재시도 비용

| | 원본 `runner.py` | A: Timeout 상향 | B: Checkpointing |
|---|---|---|---|
| 실패 1회당 재작업 범위 | 11단계 전부(약 300~400초+180초 낭비) | 실패가 거의 안 나므로 해당 없음 | **실패한 단계 1개만**(Final Report 재시도, 최대 180초) |
| 이번 실험 실측 총 비용 | (참고) Nestlé 6회 실패 누적, 전체 재실행 반복 | trial1 514.8초 + trial2 631.8초 = 1146.6초(2회 모두 처음부터) | resume_test 4회 호출 합계 약 867초(그중 2회는 Final Report 180초 낭비 포함) — **실패가 여러 번 나도 총 비용이 "전체 재실행 반복"보다 낮음** |

## COMPARISON — 종합

- **Timeout 발생률**: A(상향)가 표본상 더 낮다(0/2 vs B의 Final
  Report 3회 시도 중 2회 실패). 그러나 A는 실패 확률을 낮출 뿐
  없애지 못하며, 표본 2회로는 "항상 성공"을 결론 내릴 수 없다 —
  원본 Nestlé가 6/6 실패했다는 사실 자체가 소요시간의 변동성이 크다는
  것을 이미 보여준다.
- **실행시간**: A는 성공해도 매번 전체 11단계(500~630초)를 다시
  치른다. B는 첫 실행만 전체 비용이 들고, 이후 실패가 나도 실패한
  단계만 반복하면 된다 — 반복 실패 시나리오에서 B의 총 비용이 A보다
  낮다(이번 실험에서 실측으로 확인: B 4회 호출 867초 vs A라면 동일
  시나리오에서 실패마다 전체 재실행이 필요해 훨씬 커졌을 것).
- **데이터 유실**: A는 구조를 바꾸지 않으므로 **전혀 해결하지 못한다**
  — 실패가 나면 원본과 동일하게 전부 유실된다. B는 **실측으로 유실
  0건**을 확인했다.
- **실패 복구 가능성**: A는 실패 시 여전히 수동/우연 복구(원본과
  동일)에 의존한다. B는 **자동 복구**를 실측으로 증명했다.

## DECISION — 더 작은 변경으로 실제 문제를 해결하는 방안

**"실제 문제"는 두 가지다: (1) Final Report가 종종 180초를 넘는다,
(2) 넘었을 때 이미 끝난 작업까지 통째로 사라진다.** Timeout 상향은
(1)을 완화할 뿐 (2)를 전혀 건드리지 못한다 — 400초조차 이론적 상한이
없어 (1)도 완전히 해결하지 못한다. Checkpointing은 (1)을 없애지는
못하지만 **(1)이 몇 번을 반복되든 (2)를 원천적으로 차단**하고, 그
결과 반복 실패의 총 비용도 실측상 더 낮다.

**변경의 "크기"도 governance 관점에서 재검토가 필요하다**:
- Timeout 상향을 실제로 채택하려면 `development-hq/mvp/engine.py`
  (Dev HQ v1.0 Freeze 대상 파일)의 `ENGINE_TIMEOUT_SECONDS` 상수
  자체를 고쳐야 한다 — 코드 diff는 1줄이지만, **Frozen 파일을 직접
  건드리는 변경**이다.
- Checkpointing을 실제로 채택하면 `development-hq/`는 **한 줄도
  건드릴 필요가 없다** — project-local `runner.py` 패턴(각
  Dogfooding 프로젝트가 개별적으로 갖고 있는 파일)에만 적용되는
  변경이다. 진짜 `call_engine()`(180초)도 그대로 쓴다.

**따라서 "더 작은 변경으로 실제 문제를 해결하는 방안"은
Checkpointing이다** — 코드량은 A보다 많지만(Prototype B가 A보다
파일이 큼), Dev HQ Frozen 경계를 전혀 넘지 않으면서 두 문제(발생
빈도 완화는 못하더라도 피해 자체)를 실측 기준으로 더 근본적으로
해결한다. Timeout 상향은 Dev HQ Frozen 파일을 수정해야 하는 더
무거운 변경이면서도 데이터 유실 문제는 그대로 남긴다.

이 둘은 상호 배타적이지 않다 — 실제 채택 시에는 두 개를 함께 쓰는
것(예: 약간의 timeout 상향 + checkpointing)이 더 나을 수 있다는
점도 기록해둔다. 다만 이번 Evidence에서 단일 우선순위를 정해야
한다면 Checkpointing이 우선이다.

## GOVERNANCE — RFC/ADC/ADR 필요 여부 판단만

- **Timeout 상향**: `development-hq/mvp/engine.py`(v1.0 Freeze 대상)
  수정이 필요하므로, 실제 채택 시 RFC → ADC → ADR 절차가 필요하다고
  판단한다.
- **Checkpointing**: `development-hq/` 미수정, project-local
  `runner.py` 패턴 변경으로 그친다 — RFC가 반드시 필요한 Architecture
  변경은 아닐 수 있다는 판단이나, "Dogfooding 파이프라인의 표준
  패턴"으로 문서화하는 것은 여전히 사용자 승인이 필요한 결정이다.
- **이번 Prototype 결과만으로 실제 구현을 진행하지 않는다.** RFC
  작성, `development-hq/` 수정, project-local `runner.py` 패턴
  전환 어느 것도 이 작업 범위에서 수행하지 않았다. Architecture/
  Contract/Governance는 전혀 변경하지 않았고, v1.0 Freeze를 그대로
  유지했다.

## PHASE9_11

이번 Prototype으로 "실제 문제를 더 작은 변경으로 해결하는 방향"을
Evidence 기반으로 제시했지만, **Phase 9~11 재개나 실제 구현 착수는
사용자 승인 없이 진행하지 않는다.** 사용자가 이 Evidence를 검토한
뒤 (a) Checkpointing 패턴을 실제로 도입할지, (b) Timeout 상향을
RFC로 진행할지, (c) 둘 다 보류하고 다른 우선순위로 넘어갈지를
결정해야 한다.

## 관찰되지 않은 것 (명시적으로 기록)

- 두 Prototype을 동시에 적용(timeout 상향 + checkpointing)하는
  조합 실험 — 시도하지 않음.
- 3회 이상의 반복 시행을 통한 통계적 신뢰도 확보 — 표본이 각 2~4회로
  적어 "최소 Prototype" 수준에 그친다(사용자 지시에 따름).
- Toyota 등 다른 raw_data로도 동일 비교가 재현되는지 — 이번엔 Nestlé
  하나로 통제해 실행했다(공정 비교를 위한 의도적 고정).

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. Prototype A의
`call_engine_prototype.py`는 `engine.py`를 import하지 않는 완전히
별도의 project-local 함수이며, 실행 시점에 `shared/agents.py`의 전역
이름 하나를 프로세스 내부에서만 바꿔치기했을 뿐 디스크 위 파일은
어디도 바뀌지 않았다. Prototype B는 진짜 `call_engine()`을 그대로
가져다 썼다. 새 Capability, 새 Agent, 새 Kernel Component, 새
Contract를 만들지 않았다. v1.0 Freeze를 해제하지 않았다. RFC/ADC/ADR
문서를 작성하지 않았다(필요 여부 판단만 위에 기록). 구현 채택도,
Phase 9~11 재개도 하지 않았다 — 이 모든 결정은 사용자 승인 이후로
남긴다.
