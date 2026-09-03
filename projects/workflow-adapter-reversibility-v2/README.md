# workflow-adapter-reversibility-v2 (Experimental)

`ADC-0021` §8 Gate **(C)** — Workflow Adapter(§16.6)의 Reversibility 필수
불변조건을 v2 맥락 in-repo 통합 테스트로 재현 검증한다.

- **Owner**: Claude Code (세션 2026-09-03)
- **레인**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation". `hqs/` production path 무연결, Formal Contract·Frozen Boundary 무변경.
- **설계 근거**: `docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md`
- **산출물(E4)**: `EVIDENCE.md` + 위 Test Design 문서 §10

## 이것이 하지 않는 것

LangGraph 채택 아님(`ADC-0021` §D2 — 대조 Evidence). Production 구현 착수
아님. `IMPLEMENTATION_RULES.md` 해제 아님. Public Port / §14 표면 / 호출자
계약 확정 시그니처 정의 아님(seam은 harness 로컬 관례). mid-node resume /
성능 / 실제 엔진 / (c) reducer 규약 규범화 검증 아님.

## 구성

| 경로 | 역할 |
|---|---|
| `domain/state.py` `nodes.py` `fixtures.py` `graph_spec.py` | HQ가 정의하는 도메인 그래프·노드·시나리오. `langgraph` 무의존 |
| `adapters/sequential.py` | Reference — 순차 함수 호출(if/elif, while, ThreadPoolExecutor, 명시적 merge) |
| `adapters/langgraph.py` | 대조 — `langgraph` import는 저장소에서 이 파일 한 곳뿐 |
| `caller.py` | 호출자(HQ 자리). adapter 모듈을 인자로 받고 checkpoint 값을 파일로 소유 |
| `tests/test_reversibility_v2.py` | IN-1 ~ IN-5 |
| `tests/_resume_subprocess.py` | IN-3 — fresh 프로세스 재개 진입점 |

## 재현

```bash
# 격리 venv (Python 3.12, langgraph 1.2.11 — E2/E3와 동일 계보)
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python "langgraph==1.2.11" pytest

.venv/bin/pytest tests/ -v
```

`langgraph`는 이 격리 venv에만 설치한다. 저장소 최상위 의존성 매니페스트는
건드리지 않는다.

## 성공 / 실패 / 폐기 기준

- **성공**: IN-1 ~ IN-5 전부 PASS → `EVIDENCE.md` 산출, (C) 재현 검증 완료로 보고.
- **실패**: 하나라도 FAIL → 원인 수정 후 재검증(테스트 범위 임의 확장 금지). 수정 불가 시 구현 착수 불가 사유로 기록·보고.
- **폐기**: 후속 ADR이 E4를 반영(또는 불충분 판정)한 뒤 필요 없어지면 RFC 없이 삭제 가능(`ARCHITECTURE_GOVERNANCE.md` "Experimental").
