# workflow-adapter-nonlanggraph-lineage-v1 (Experimental)

`ADC-0021` §8 Gate **(B)** / Gate **(C) 잔여 한계 (ii)** — Workflow
Adapter(§16.6)의 §16.6 A-IN 5항목과 Reversibility 필수 불변조건이
**LangGraph 아닌 독립 실행 계보**에서도 성립함을 in-repo 통합 테스트로
확인한다.

- **Owner**: Claude Code (세션 2026-09-04)
- **레인**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
  Implementation". `hqs/` production path 무연결, Formal Contract·Frozen
  Boundary 무변경, `IMPLEMENTATION_RULES.md` 무변경.
- **선행**: E4 `projects/workflow-adapter-reversibility-v2/`
  (Sequential Reference ↔ LangGraph 2-way, Gate (C) "부분 충족").
  이 프로젝트는 E4의 `domain/*`·`caller.py`·IN 하네스를 **바이트 단위로
  복제**해 재사용하고, 비-LangGraph **독립 계보 어댑터**를 추가한다.
- **근거**: `ADC-0019` 재검토 조건 (c)("LangGraph와 다른 계보 또는 v2
  프로덕션 맥락의 조건부 분기·Loop 실행 관찰이 추가되어 독립 관찰 3건에
  도달"), `RFC-0020` §8.2 Q-I("직접 구현 최소 그래프 실행기"),
  E4 Test Design `docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md` §205.
- **산출물**: `EVIDENCE.md` (자립 Evidence — Governance 문서 아님).

## 이것이 하지 않는 것

Gate (B) 충족 **선언** 아님(후속 ADC의 몫). Gate (C) 완전 discharge 아님
(잔여 한계 (i) 결정론적 stub·(iii) 프로덕션 트래픽은 범위 밖). LangGraph
채택 아님. Production 구현 착수 아님. `IMPLEMENTATION_RULES.md` 해제 아님.
Public Port / §14 표면 / 확정 계약 시그니처 정의 아님(seam은 harness
로컬 관례 — E4와 동일). mid-node resume / 성능 / 실제 엔진 / (c) reducer
규약 규범화 아님. L-B(2번째 비-LangGraph 계보)는 이 프로젝트에 없다 —
L-A 결과 확인 후 별도 결정.

## 구성

| 경로 | 역할 | 출처 |
|---|---|---|
| `domain/{state,graph_spec,nodes,fixtures}.py` | HQ가 정의하는 도메인 그래프·노드·시나리오. `langgraph` 무의존 | E4 복제 (byte-identical) |
| `caller.py` | 호출자(HQ 자리). adapter 모듈을 인자로 받고 checkpoint 값을 파일로 소유 | E4 복제 (byte-identical) |
| `adapters/langgraph.py` | 대조 계보 (L-LG). `langgraph` import는 이 파일 한 곳 | E4 복제 (byte-identical) |
| **`adapters/worklist.py`** | **L-A — 비-LangGraph 독립 계보.** `graph_spec`을 데이터로 해석하는 ready-queue worklist 인터프리터. 표준 라이브러리 + `domain.graph_spec`만 의존 | **신규** |
| `tests/test_lineage_v1.py` | IN-1 ~ IN-6 (L-A vs L-LG) | 신규 (E4 IN-1~IN-5 구조 계승 + IN-6 신설) |
| `tests/_resume_subprocess.py` | IN-3 — fresh 프로세스 재개 진입점 | E4 복제 (adapter 이름만 교체) |

## L-A 계보 독립성 (요지 — 상세는 `adapters/worklist.py` docstring)

- **E4 `adapters/sequential.py`와 다르다**: sequential은 `_phase1()`·
  `_phase2()`에 실행 순서를 하드코딩한 절차다. L-A는 그런 절차가 없고
  `graph_spec`의 edge 구조(정적 + 조건부 predicate)를 **런타임에 계산**해
  ready-queue를 돌린다.
- **`adapters/langgraph.py`와 다르다**: LangGraph는 `StateGraph.compile()`
  + Pregel 계열 superstep 엔진. L-A는 컴파일도, superstep도, 외부 그래프
  런타임도 없다 — 단일 스레드 worklist 루프 + 명시적 predecessor 집합.
- `langgraph`/`langchain`/서드파티 import 0. `sequential.py` import 0
  (계보 상호 독립 — 공유는 `domain/*`).

## 재현

E4의 격리 venv(Python 3.12, `langgraph==1.2.11`, `pytest`)를 재사용한다 —
`langgraph`는 L-LG 대조 레그에만 필요하고, 저장소 의존성 매니페스트는
건드리지 않는다.

```bash
V=../workflow-adapter-reversibility-v2/.venv/bin/python
$V -m pytest tests/ -v
```

동등 venv를 새로 만들려면 Python 3.12 + `langgraph==1.2.11` + `pytest`를
격리 환경에 설치한다(E4 `README.md` "재현" 절과 동일 계보·버전).

## 성공 / 실패 / 폐기 기준

- **성공**: IN-1 ~ IN-6 전부 PASS → `EVIDENCE.md` 산출, B-1 관찰 1건 +
  C(ii) 대조 계보 추가로 보고.
- **실패**: 하나라도 FAIL → 원인 수정 후 재검증(테스트 범위 임의 확장
  금지). L-A가 도메인 그래프에서 L-LG와 동치를 못 내면 구현 착수 불가
  사유로 기록·보고.
- **폐기**: 후속 ADC가 E5를 반영(또는 불충분 판정)한 뒤 필요 없어지면
  RFC 없이 삭제 가능(`ARCHITECTURE_GOVERNANCE.md` "Experimental").
