# Dev HQ Vertical Slice — Experimental Prototype

**성격**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의
"Experimental Implementation" 절이 허용하는 격리 Prototype. Formal
Architecture Decision이 아니다. Production `core/`, `hqs/`,
`dashboard/`, 기존 Runtime/Engine/Workflow를 수정하지 않는다.

**축소 배경**: 원래 요청은 "Production 구조로 Command→Task→Runtime→
Development HQ→Result→Dashboard를 관통하는 최소 구현"이었으나,
구현 전 Governance 확인(`hqs/development/IMPLEMENTATION_RULES.md`
"Runtime 구현 금지 — Runtime 개념 자체가 Open Decision(ADC-02)이다",
`docs/decisions/adc/ADC.md` ADC-02 Open·NOW, `ADC-0008-runtime-
existence-boundary.md` Not Accepted 재확인)에서 명시적 충돌을
발견해 사용자에게 보고했고, **7번째 Experimental Prototype으로
축소 진행**하기로 결정했다(`projects/` 격리, Production `core/`
무생성).

**목적**: Command → Task → Runtime → Dev HQ(Adapter) → Result 저장
→ Dashboard 관찰까지, 지금까지의 6개 Prototype이 각각 따로
검증했던 조각들을 **하나의 실제 경로로 관통 연결**해 E2E로
검증한다. 새로운 Architecture 질문을 만들지 않는다 — 기존
Evidence(Task=CANDIDATE, Runtime=CANDIDATE(Process 조건부))를
그대로 재사용한다.

## 구성 요소와 재사용 관계

| 구성 요소 | 이 Prototype의 파일 | 재사용 |
|---|---|---|
| Command(immutable) | `vs_command.py` | 신규(Dev HQ 단독 범위로 축소한 최소 파싱) |
| Task(identity/lifecycle) | (재사용) | `runtime-boundary`의 `rtb_task.py` 그대로 |
| Runtime(execution/isolation) | (재사용) | `runtime-boundary`의 `rtb_runtime.py` 그대로, Process 전략만 사용 |
| Dev HQ Adapter | `vs_dev_hq_adapter.py` | 신규(action → 실제 대상 경로 매핑만, Dev HQ 코드 미import) |
| Result 저장 | `vs_result_store.py` | 신규(파일 기반, 이번 Prototype의 새 질문) |
| Dashboard(observe-only) | `vs_dashboard_view.py` | 신규 + `rtb_dashboard_view.py` 재사용 |
| Pipeline(연결) | `vs_pipeline.py` | 신규(위 조각들을 순서대로 호출만 함) |

`rtb_task.py`/`rtb_runtime.py`는 이 디렉터리에 복사하지 않는다 —
`sys.path`로 `../runtime-boundary/`를 참조한다.

## 실행

```
python3 projects/dev-hq-vertical-slice/demo.py
```

## 테스트

```
python3 -m pytest projects/dev-hq-vertical-slice/tests/ -q
```

`results/*.json`은 테스트/데모 실행 산출물이다(`.gitignore`로 제외).

## Evidence

전체 판정과 Evidence는
`docs/research/JARVIS-OS-V2.0-DEV-HQ-VERTICAL-SLICE-PROTOTYPE-0001.md`
참조.
