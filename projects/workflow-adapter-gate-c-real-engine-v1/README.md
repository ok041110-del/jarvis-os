# workflow-adapter-gate-c-real-engine-v1 (Experimental)

Gate **(C) 잔여 한계 (i)**("노드가 결정론적 stub — 실제 엔진 비결정성·
부분 실패율 미검증", `BASELINE.md` §16.6 "부분 충족(E4)" 문단·`ADR-0010`)를
겨냥한다. `analyst_sentiment` 한 노드만 실제 Engine 호출로 대체해, 그
비결정적·때로 실패하는 실행이 4개 Workflow Adapter 계보
(sequential/worklist L-A/recursive L-B/langgraph L-LG) 전체에서 같은
방식으로 처리되는지 in-repo 통합 테스트로 확인한다.

- **Owner**: Claude Code (세션 2026-09-05)
- **레인**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental
  Implementation" — "실제 HQ traffic pattern을 복제한 실험"에 해당.
  `hqs/` production path 무연결(단, `hqs/development/mvp/engine.py`
  ::`call_engine()`은 **read-only import**), Formal Contract·Frozen
  Boundary 무변경, `IMPLEMENTATION_RULES.md` 무변경, 저장소 의존성
  매니페스트 무변경.
- **선행**: E4 `projects/workflow-adapter-reversibility-v2/`(Sequential↔
  LangGraph, Gate (C) "부분 충족"), E5 `projects/workflow-adapter-nonlanggraph-lineage-v1/`
  (L-A), E6 `projects/workflow-adapter-recursive-lineage-v1/`(L-B). 이
  프로젝트는 세 프로젝트의 `domain/*`(`nodes.py`·`fixtures.py` 제외)·
  `caller.py`·`adapters/{sequential,worklist,recursive,langgraph}.py`를
  바이트 단위로 복제해 재사용하고, `analyst_sentiment` 노드와
  `domain/engine_cache.py`(신규)만 추가·변경한다.
- **근거**: `ADR-0010` §Decision 2.1 잔여 한계 (i), 승인된 Test Design
  (세션 2026-09-05, 대화 기록 — 정식 문서 파일로는 미커밋).
- **산출물**: `EVIDENCE.md`(자립 Evidence — Governance 문서 아님, 실제
  실행 결과를 있는 그대로 기록).

## 이것이 하지 않는 것

Gate C(i) discharge 선언 아님. Gate C(iii)(프로덕션 트래픽) 해결 아님 —
이 실험은 샌드박스 실험이지 실 HQ 운영 트래픽이 아니다. Gate B·`ADC-0021`
§8 조건 1·LangGraph 채택·Production 구현 착수·`IMPLEMENTATION_RULES.md`
해제 아님. 실제 Engine의 텍스트 재현성 주장 아님(애초에 불가능·무관).
실패율의 통계적 분포 측정 아님(표본 1~2회로는 불가). `hqs/development/`·
`hqs/investment/` 수정 아님(`call_engine()` read-only import만).

## Record-once-replay 설계 (핵심)

실제 Engine은 호출마다 다른 텍스트를 낸다 — 이 자체를 "어댑터 결함"으로
오인하지 않기 위해, 시나리오당 실제 Engine을 **정확히 1회**만 호출해
캡처하고(`domain/engine_cache.py`), 그 **동일한 캡처값**을 4개 어댑터
모두에 주입해 실행한다. 이렇게 하면 "LLM이 매번 같은 말을 하는가"가
아니라 "같은 값을 4개 어댑터가 동일하게 병합·전달·Checkpoint하는가"를
검증하게 된다. 조건부 분기(`data_gap`의 conflict 여부)는 여전히 시나리오
설정이 결정한다(업무 분기의 재현성 유지) — 실제 Engine 텍스트는
`sentiment.engine_note` 값으로만 실려 파이프라인을 관통한다.

## 실행

**opt-in 게이팅** — 기본 `pytest`로는 실행되지 않는다(비용·지연 발생):

```bash
V=../workflow-adapter-reversibility-v2/.venv/bin/python
RUN_REAL_ENGINE_TESTS=1 $V -m pytest tests/ -v
```

플래그 없이 실행하면 전체 모듈이 SKIP된다(안전한 기본값).

## 실제 Engine 호출 예산 (≤10회, 설계상 실제로는 3회)

| 항목 | 실제 호출 |
|---|---|
| `clean` 캡처(IN-7-1/2 공용) | 1 |
| `data_gap` 캡처(IN-7-1/2 공용) | 1 |
| 실제 timeout 유도(IN-7-3a, `engine_error_real_timeout`) | 1 |
| RuntimeError 재현(IN-7-3b, `engine_error_runtime`) | 0 (`subprocess.run` 로컬 대체 — 합성, `claude` CLI 기동 없음) |
| **합계** | **3** (예산 10 대비 여유 7) |

`domain/engine_cache.py::real_call_count()`가 실측하고,
`test_IN7_meta_real_call_budget_within_limit`이 이를 assert한다.

## 안전 경계

- 프롬프트는 완전히 합성적 지시만 사용 — 실제 티커·실제 투자 조언·실제
  시장 판단을 요청하지 않는다.
- `ENGINE_TIMEOUT_SECONDS` 단축은 테스트 fixture 안에서만 일시 적용 후
  즉시 원복(`hqs/development/mvp/engine.py` 파일 자체는 무수정).
- `subprocess.run` 대체(IN-7-3b)는 그 fixture의 `trigger()` 실행 구간에만
  적용 후 즉시 원복.
- 환경 문제(claude CLI 부재·미인증·네트워크 실패)는 SKIP으로 보고한다
  (FAIL 아님) — `_capture_real_scenarios`/`_real_timeout_exception`
  fixture가 예외를 감지하면 `pytest.skip`.

## 성공 / 실패 / SKIP / 폐기 기준

- **성공**: IN-7-1~IN-7-5 + 예산 메타 검증 전부 PASS.
- **실패**: 어댑터가 동치·catch-and-encode·checkpoint round-trip 중
  하나라도 어긴 경우 — 원인을 Gate C(i) 잔여 위험으로 명확히 기록.
- **SKIP**: `claude` CLI 미설치·미인증·네트워크 문제로 실제 캡처 자체가
  안 되는 경우 — 이는 실패가 아니라 환경 가용성 문제로 별도 기록한다.
- **폐기**: 후속 ADR/ADC가 Gate C(i) 상태를 반영(또는 불충분 판정)한 뒤
  필요 없어지면 RFC 없이 삭제 가능(`ARCHITECTURE_GOVERNANCE.md` "Experimental").
