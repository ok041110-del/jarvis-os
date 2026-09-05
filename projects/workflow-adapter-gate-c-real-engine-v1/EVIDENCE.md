# E7 — Gate C(i) 실제 Engine 호출 검증 Evidence

검증일: 2026-09-05

## 문서 성격

이 문서는 **Evidence 기록이다. Governance 문서가 아니다.** Architecture
Decision을 포함하지 않는다. RFC/ADC/ADR/Baseline을 수정하지 않는다.
**Gate C(i) discharge를 선언하지 않는다. Gate C(iii)(프로덕션 트래픽)
해결도 선언하지 않는다** — 이 실험은 샌드박스 안의 단발 실제 Engine
호출이지 실 HQ 운영 트래픽이 아니다. 결과가 두 잔여 한계에 무엇을
기여하는지 과장 없이 판정한다.

## Summary — 실제 실행 결과 (가정 없음)

- **opt-in 게이팅 확인**: `RUN_REAL_ENGINE_TESTS` 미설정 시 12개 테스트
  전부 **SKIPPED**(0.18초, 실제 Engine 호출 0회) — 안전한 기본값 확인.
- **`RUN_REAL_ENGINE_TESTS=1`로 실행 시: 12/12 PASSED (12.41초)**.
- **실제 Engine 호출 총량: 3회**(예산 10회 대비 여유 7회) —
  `engine_cache.real_call_count()` 실측, `test_IN7_meta_real_call_budget_within_limit`
  로 assert.
  - `clean` 캡처 1회 — 실제 응답(발췌): "가상의 스타트업 '블루문
    커머스'는 이번 분기 매출과 고객 유지율이 전년 대비 완만하게
    증가했고 특이 리스크 신호 없이 전반적으로 안정적인 흐름을
    유지하고 있다."
  - `data_gap` 캡처 1회 — 실제 응답(발췌): "유가리 코퍼레이션에 대한
    감정 분석 결과, 일부 소스는 긍정적 전망을, 다른 소스는 공급망
    우려로 부정적 전망을 제시해 결론이 엇갈렸다."
  - 실제 timeout 유도 1회 — `ENGINE_TIMEOUT_SECONDS=0.01`로 실제
    `claude` subprocess를 기동시켜 **진짜** `subprocess.TimeoutExpired`
    발생 확인(명령행 인자까지 실제 호출 그대로 캡처됨).
  - RuntimeError 재현은 **0회**(합성) — `subprocess.run`을 로컬
    대체해 `call_engine()`의 실제 소스 코드(비-zero exit 분기)만
    조건 통제로 실행, `claude` CLI는 기동하지 않음. 실측:
    `RuntimeError('exit code 1: synthetic non-zero exit (IN-7-3b)')`.
- **환경 SKIP은 발생하지 않았다** — 이 실행 환경에는 `claude` CLI가
  설치·인증돼 있어 전체 스위트가 정상 실행됨. (다른 환경에서 CLI
  미설치·미인증이면 `_capture_real_scenarios`/`_real_timeout_exception`
  fixture가 `pytest.skip`으로 구분 보고한다 — 이번 실행에서는 해당
  경로를 타지 않았다.)
- `core/`·`hqs/`·`dashboard/` 변경 0(`git diff --stat` 빈 출력,
  IN-7-5로 실측 확인). 저장소 의존성 매니페스트 무변경.

## 1. 검증 환경

| 항목 | 값 |
|---|---|
| 실행 위치 | `projects/workflow-adapter-gate-c-real-engine-v1/` (저장소 안) |
| Python | 3.12.14 (E4/E5/E6 격리 venv 재사용) |
| 실제 Engine | `hqs/development/mvp/engine.py::call_engine()`(read-only import, `claude` CLI subprocess) |
| `claude` CLI | `/usr/local/bin/claude`, version `2.1.220 (Claude Code)` — 이 실행 환경에 설치·인증돼 있음을 실측 확인 |
| pytest | 9.1.1 |
| opt-in 게이팅 | `RUN_REAL_ENGINE_TESTS=1` 필요. 미설정 시 전체 SKIP(12/12, 0.18초) |
| 저장소 의존성 매니페스트 | 무변경 |

재현: `README.md` "실행" 절.

## 2. 검증 대상 구성

- **도메인**: E4/E5/E6에서 `state.py`/`graph_spec.py` byte-identical
  복제. `nodes.py`는 `analyst_sentiment` **한 노드만** 실제 Engine
  호출(engine_cache 경유)로 대체, 나머지 12개 노드는 결정론적 stub
  그대로.
- **시나리오**: `clean`/`data_gap`(실제 Engine, record-once-replay),
  `engine_error_real_timeout`/`engine_error_runtime`(실제/합성 예외
  재발생, catch-and-encode 검증 전용).
- **어댑터 4종**: `sequential`(E4)·`worklist` L-A(E5)·`recursive`
  L-B(E6)·`langgraph` L-LG — 전부 byte-identical 복제, 무수정.
- **Record-once-replay**: `domain/engine_cache.py`가 시나리오당 정확히
  1회만 `call_engine()`을 호출하고, 캡처값을 4개 어댑터 모두에 동일
  주입한다.

## 3. 실행 결과 — 12/12 PASS (opt-in), 12/12 SKIP (기본값)

```
$ .venv/bin/pytest tests/ -v                              # 기본값
============================== 12 skipped in 0.18s ==============================

$ RUN_REAL_ENGINE_TESTS=1 .venv/bin/pytest tests/ -v -s   # opt-in
============================== 12 passed in 12.41s ==============================
```

| 항목 | 테스트 | n | 결과 | 검증 내용 |
|---|---|---|---|---|
| **IN-7-1** 실제 호출 생존 확인 | `test_IN7_1_real_engine_actually_invoked_and_returns_text` | 1 | PASS | `clean`/`data_gap` 캡처 텍스트가 비어있지 않고, `real_call_count() >= 2` 실측 확인 |
| **IN-7-2** Record-once-replay 동치 | `test_IN7_2_..._across_four_adapters[clean/data_gap]` | 2 | PASS | 동일 캡처값 주입 시 sequential/worklist/recursive/langgraph 4개 어댑터의 최종 State가 서로 dict 동치. `engine_note` 필드가 실제 캡처 텍스트와 일치(스텁 고정값 아님을 재확인) |
| **IN-7-3** 실제/합성 예외의 catch-and-encode | `test_IN7_3_..._across_four_adapters[engine_error_real_timeout/...]` | 2 | PASS | 진짜 `subprocess.TimeoutExpired`(실제 timeout 1회 유도) + 합성 `RuntimeError`(call_engine 실제 코드 경로, 0비용) 각각이 4개 어댑터 전부에서 `NODE_ERROR:analyst_sentiment:{ExcType}` State 값으로 인코딩되고 경계 밖 전파 없음 |
| **IN-7-4** Checkpoint round-trip with 실제 응답 | `test_IN7_4_..._real_engine_payload[4 어댑터]` | 4 | PASS | phase1 checkpoint 값(실제 Engine 텍스트 포함)이 JSON round-trip 성공·라이브러리 타입 0. 별도 프로세스가 로드해 `run_phase2` → 결과 == 단발 실행(재개 프로세스는 실제 Engine을 재호출하지 않음 — phase1에서 이미 캡처된 값이 값으로 실려있을 뿐) |
| **IN-7-5** 교체 시 Kernel/HQ 코드 0 변경 | `test_IN7_5_swap_zero_kernel_hq_change` | 1 | PASS | `caller.py`/`domain/*`에 `adapters`/`langgraph`/`langchain` import 0. `git diff --stat -- core/ hqs/ dashboard/` 빈 출력 |
| | `test_IN7_5_hashes_identical_across_adapters` | 1 | PASS | 4개 어댑터 실행 후에도 `caller.py`+`domain/*` SHA-256 6개 전부 불변 |
| **예산 메타** | `test_IN7_meta_real_call_budget_within_limit` | 1 | PASS | 실측 `real_call_count() == 3` ≤ 예산 10 |

## 4. 이 Evidence가 보이는 것 / 보이지 않는 것

**보이는 것** — `analyst_sentiment` 노드가 진짜 `claude` CLI subprocess를
호출해 매번 다른(진짜 비결정적) 텍스트를 낼 때도, 4개 Workflow Adapter
계보(sequential/worklist/recursive/langgraph) 전부가 (a) 그 값을 동일하게
병합·전달해 최종 State 동치를 유지하고, (b) 진짜 인프라 예외
(`subprocess.TimeoutExpired`)와 `call_engine()`의 실제 RuntimeError
코드 경로를 catch-and-encode해 경계 밖 전파 없이 State 값으로
인코딩하며, (c) 그 실제 텍스트가 포함된 값도 JSON Checkpoint round-trip과
별도 프로세스 재개를 여전히 통과함을 **저장소 안의 실행 가능한 통합
테스트**로 확인했다. 이는 E4/E5/E6이 "결정론적 stub" 한계로 미검증
상태로 남겼던 지점을 정면으로 실측한 것이다.

**보이지 않는 것 (E7의 한계 — 후속 ADR/ADC가 discharge 판정 시 고려)**:

1. **실제 프로덕션 트래픽이 아니다** — 실제 HQ 운영 컨텍스트(실
   사용자 Task, 실제 Investment/Development HQ 실행 파이프라인) 안에서
   실행된 것이 아니라 격리된 실험 샌드박스의 단발 호출이다. Gate C(iii)
   "프로덕션 트래픽 미검증"을 **해소하지 않는다**.
2. **표본 극소(시나리오당 1회)** — 부분 실패율이나 비결정성의 **분포**를
   측정하지 않았다. "적어도 한 번은 실제 예외 경로가 정상 동작함"을
   보였을 뿐, "항상 그런가"는 답하지 않는다.
3. **노드 12개는 여전히 stub** — `analyst_sentiment` 한 노드만 실제화
   됐다. 나머지 병렬 fan-out 노드·토론 Loop 노드·trader 노드는 결정론적
   그대로다.
4. **seam이 harness 로컬 관례** — `run_full`/`run_phase*`는 여전히
   확정 계약 시그니처가 아니다(E4/E5/E6 계승).
5. **timeout 값이 인위적으로 극단적** — `0.01초`는 실제 운영 시
   `ENGINE_TIMEOUT_SECONDS`(180초)와 무관한, 예외 경로만 유도하기 위한
   테스트 전용 값이다. "정상 범위 내 지연"에서의 부분 실패율은
   미검증.

## 5. 판정 — Gate C(i) 기여 (선언 아님, 사실 기록만)

| 질문 | 판정 |
|---|---|
| E7이 §16.6 Reversibility 불변조건을 **실제 Engine 비결정성 하에서** 재현했는가 | **예 — 부분** — 4개 어댑터 전부 IN-7-1~IN-7-5 PASS, 진짜 timeout·합성 RuntimeError 모두 catch-and-encode 확인 |
| E7이 Gate C(i)("실제 엔진 비결정성·부분 실패율 미검증")를 **완전히** discharge하는가 | **이 문서가 선언하지 않음** — §4의 한계 2·3(표본 극소, 노드 1개만 실제화)으로 "부분 진전" 판정 여지. 충분성 판정은 후속 ADR/ADC의 몫 |
| E7이 Gate C(iii)(프로덕션 트래픽)를 진전시키는가 | **아니오** — 샌드박스 실험, 실 HQ 운영 컨텍스트 아님(§4 한계 1) |
| E7이 Gate B / `ADC-0021` §8 조건 1 / LangGraph 채택을 진전시키는가 | **아니오** — 이 실험의 범위 밖. 4개 어댑터는 모두 이미 알려진 계보(신규 계보 아님) |
| E7이 LangGraph 채택·구현 착수·`IMPLEMENTATION_RULES` 해제·Production 구현 중 무엇이든 발생시키는가 | **아니오** — `ARCHITECTURE_GOVERNANCE.md` "Experimental Evidence는 그 존재만으로 ADC Accept를 발생시키지 않는다". 전부 후속 절차 |

## 6. Traceability

| 문서 / 절 | 관계 |
|---|---|
| `BASELINE.md` §16.6 "부분 충족(E4)" 문단 — 잔여 한계 (i) | 이 Evidence가 겨냥한 대상 |
| `ADR-0010` §Decision 2.1, §Review | Gate C(i) 원 서술("결정론적 stub — 실제 엔진 비결정성·부분 실패율 미검증") |
| `docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md` §2.3·§3.3 | "실제 엔진 호출·비결정성"을 의도적 비검증으로 명시한 원 설계 — 이 E7이 그 배제 항목을 별도 실험으로 수행 |
| E4/E5/E6 `EVIDENCE.md` | 도메인·seam·IN 하네스 구조의 원 출처. `analyst_sentiment` 외 12개 노드는 그대로 계승 |
| `hqs/development/mvp/engine.py::call_engine()`(`ENGINE-CONNECT-0001`) | read-only import한 유일한 실제 Engine 경유 지점 |
| `hqs/investment/engine_client.py` | `call_engine`을 재노출하는 Investment HQ 경유 지점, read-only import |
| `docs/00_governance/ARCHITECTURE_GOVERNANCE.md` "Experimental Implementation" | "실제 HQ traffic pattern을 복제한 실험" 허용 근거 |
| 승인된 Test Design(세션 2026-09-05) | IN-7-1~IN-7-5·예산 상한(≤10회)·opt-in 게이팅의 원 설계. 정식 문서 파일로는 미커밋 |
