# workflow-adapter-recursive-lineage-v1 (Experimental)

`ADC-0021` §8 Gate **(B)** — `ADC-0024` §D-B4가 이름 붙인 **완전 완화
후속조건 (i) "2번째 비-LangGraph 독립 계보(L-B)"**를 구현·실행한다.
Workflow Adapter(§16.6)의 A-IN 5항목과 Reversibility 필수 불변조건이
L-A(worklist)와도 LangGraph와도 다른 세 번째 실행 메커니즘에서도
성립함을 in-repo 통합 테스트로 확인한다.

- **Owner**: Claude Code (세션 2026-09-05)
- **레인**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
  Implementation". `hqs/` production path 무연결, Formal Contract·Frozen
  Boundary 무변경, `IMPLEMENTATION_RULES.md` 무변경, 저장소 의존성
  매니페스트 무변경.
- **선행**: `projects/workflow-adapter-nonlanggraph-lineage-v1/`(E5, L-A =
  worklist 인터프리터)·`projects/workflow-adapter-reversibility-v2/`(E4,
  Sequential ↔ LangGraph). 이 프로젝트는 E5의 `domain/*`·`caller.py`·
  `adapters/langgraph.py`·IN 하네스를 **바이트 단위로 복제**해 재사용하고,
  세 번째 독립 계보 어댑터(L-B = 재귀 조합자)를 추가한다.
- **근거**: `ADC-0024` §D-B4("(i) 2번째 비-LangGraph 독립 계보(예: FSM /
  코루틴 실행기 / 대안 라이브러리 — L-B) ... 착수 여부·시점·형태는 이
  ADC가 정하지 않는다"), `RFC-0020` §8.2 Q-I("직접 구현 최소 그래프
  실행기"), 세션 승인 Test Design(2026-09-05, 대화 기록 — 정식 문서
  파일로는 미커밋).
- **산출물**: `EVIDENCE.md` (자립 Evidence — Governance 문서 아님).

## 이것이 하지 않는 것

Gate B 완전 완화 **선언** 아님(후속 ADC의 몫). Gate C 잔여 한계 (i)
결정론적 stub·(iii) 프로덕션 트래픽 해소 아님(이 프로젝트도 stub 기반).
LangGraph 채택 아님. Production 구현 착수 아님. `IMPLEMENTATION_RULES.md`
해제 아님. Public Port / §14 표면 / 확정 계약 시그니처 정의 아님(seam은
harness 로컬 관례 — E4/E5와 동일). mid-node resume / 성능 / 실제 엔진 /
(c) reducer 규약 규범화 아님. 독립 관찰 카운팅·"몇 건이면 충분한가"의
판정 아님(후속 ADC의 몫, `ADC-0024` §D-B4 계승).

## L-B 계보 독립성 (요지 — 상세는 `adapters/recursive.py` docstring)

- **L-A(worklist)와 다르다**: L-A는 `_Interpreter` 인스턴스가
  `collections.deque` 큐 + `completed`/`pending`/`ready` mutable 속성을
  하나의 `while` 루프 안에서 계속 바꿔가며 진행한다. L-B는 그런 인스턴스·
  큐가 없다 — 진행은 `_advance()` 순수 재귀 호출이며, "무엇이 끝났는가"는
  매 호출마다 새로 만들어지는 `frozenset`으로 표현한다. 수렴 Loop는
  `visited - _DEBATE`로 새 frozenset을 만들어 다음 재귀 프레임에 넘기는
  것으로 재현한다(기존 객체 mutate 없음).
- **`adapters/langgraph.py`와 다르다**: 컴파일·superstep·외부 그래프
  런타임 없음.
- `langgraph`/`langchain`/서드파티 import 0. `worklist.py`/`sequential.py`
  import 0(계보 상호 독립 — 공유는 `domain/*`). `class` 정의·
  `collections` import 0 — 인터프리터 인스턴스·큐 자료구조가 이름만 바뀐
  재구현이 아님을 소스 구조로 강제(IN-6'-2).
- 실행 메커니즘 차이는 주장이 아니라 계측으로 확인한다(IN-6'-3): `_advance`가
  자기 자신을 재귀 호출함을 AST로 검출하고, 실행 중 최대 콜스택 깊이가
  그래프 실행 경로 길이에 비례하는 다층 값(실측 14)임을 확인 — L-A의
  `run()`은 동일 방식으로 계측해도 `while` 루프 기반이며 자기 재귀 호출이
  없음을 대조 확인한다(sibling 파일 소스 텍스트 읽기, import 없음 — 두
  프로젝트는 런타임 결합 없이 독립적으로 폐기 가능하다).

## 재현

E4/E5의 격리 venv(Python 3.12, `langgraph==1.2.11`, `pytest`)를 재사용한다.

```bash
V=../workflow-adapter-reversibility-v2/.venv/bin/python
$V -m pytest tests/ -v
```

## 성공 / 실패 / 폐기 기준

- **성공**: IN-1' ~ IN-6'(6'-1/2/3 포함) 전부 PASS → `EVIDENCE.md` 산출,
  Gate B "비-LangGraph 계보 2번째(L-B)" 관찰 1건으로 보고. Gate B 완전
  완화·Governance 결정은 선언하지 않는다.
- **실패**: 하나라도 FAIL → 원인을 L-B 계보 독립성 문제로 명확히 기록하고
  (구조적 재구현에 불과한지, 실행 메커니즘 실측이 주장과 불일치하는지)
  수정 또는 폐기 판단. 테스트 범위 임의 확장 금지.
- **폐기**: 후속 ADC가 L-B를 반영(또는 불충분 판정)한 뒤 필요 없어지면
  RFC 없이 삭제 가능(`ARCHITECTURE_GOVERNANCE.md` "Experimental").
