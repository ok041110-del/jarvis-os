# Evidence — Investment HQ MVP 최초 E2E 검증 (EFA, ETF Team)

`investment-hq/run.py`(HQ 최소 E2E 진입점)를 통한 첫 실제 실행이다.
목적은 EFA 분석 자체가 아니라 **Investment HQ MVP가 실제로 동작하는지
증명**하는 것 — HQ에서 Team(ETF)을 선택해 신규 종목(EFA, 기존 18건
Dogfooding과 중복되지 않음)을 실제로 분석할 수 있는지 검증했다.

## TARGET

iShares MSCI EAFE ETF(EFA) — 선진국(미국·캐나다 제외) 대형/중형주
ETF. 기존 ETF 6건(QQQ/SCHD/AGG/GLD/VNQ/UUP)이 전부 미국 시장/자산
이었던 것과 달리, 처음으로 미국 외 지역(일본 24%·영국 15% 등) 주식에
노출되는 펀드를 선택해 국제 자산군에서도 HQ 경로가 동작하는지 함께
확인했다.

## 실행 결과

| 시도 | 결과 |
|---|---|
| 1차 | 8단계 성공, **Synthesis 호출이 콘텐츠 레벨 실패**(아래 CONTENT_FAILURE 참조) |
| 2차(재개) | 8단계 정확히 스킵(Engine 재호출 없음), Synthesis/Final Report만 재실행 → **완주** |

**E2E 시간(2차 시도, 재구성)**: Wave1(6개 분석, 병렬) 41.0초 + Wave2
(Bull/Bear, 병렬) 44.0초 + Wave3(Synthesis) 34.0초 + Wave4(Final
Report) 34.6초 = **153.6초**.

## QUALITY

- 9개 필수 섹션(Composition/Holdings/Cost/Performance/Distribution/
  Macro/Bull Case/Bear Case/Synthesis) + Disclaimer — **전부 존재**
- 952단어(목표 800~1200단어 범위 내)
- raw_data.md 핵심 데이터 11항목(총보수율 0.32%, 대표추출법, 국가
  비중 일본24%/영국15%, ASML 3.22%, VEA 대비 비용/추적오차 비교,
  1년 수익률 20.06%, 최대낙폭 61.0%, 변동성 20.8%, 배당수익률 소스
  불일치(3.36%/2.75%), 반기 배당, 700개 종목) — **11/11 전부 보존**

**결론: ETF Team의 6개 역할이 investment-hq/run.py를 통해서도, 그리고
처음으로 국제(비미국) 자산에서도 지시문 변경 없이 유효했다.** Cost/
Tracking Analyst가 EFA 고유의 추적오차 수치 부재(VEA와의 상대 비교만
존재)를, Distribution Analyst가 배당수익률 소스 불일치(3.36%/2.75%)
를 각각 자기인정 — project-local Dogfooding에서 관찰된 것과 동일한
자기인정 패턴이 HQ 경로에서도 재현됐다.

## TOKENS / COST / CALL_COUNT

- **CALL_COUNT**: 10회(ETF Team 구조, 6개 분석+Bull/Bear/Synthesis/
  Final Report) — 1차+2차 시도를 합쳐도 **총 10회, 중복 0회**
  (8단계는 체크포인트에서 로드, 재계산되지 않음)
- **TOKENS**: 10회 호출 output 문자수 합계 49,485자(약 12,371 토큰,
  4자/토큰 근사)
- **COST**: 전체 파이프라인 정확한 비용은 계측되지 않았다(기존
  Dogfooding과 동일한 계측 한계 — `investment-hq/checkpoint.py`도
  `--output-format text`를 쓰는 진짜 `call_engine()`을 그대로 호출)

## CONTENT_FAILURE — 3회째 재현 확정

1차 시도의 Synthesis 호출이 `"API Error: Unable to connect to API:
Self-signed certificate detected. Check your proxy or corporate SSL
certificates"`를 반환했으나, `call_engine()`이 이를 예외로 처리하지
않아 오류 메시지가 정상 산출물처럼 체크포인트됐다(PR #80/#81과 동일한
구조적 패턴 — 콘텐츠 레벨 실패가 예외 기반 Checkpointing으로 감지되지
않음).

## FAILURE_CAUSE — 기존 2건과의 비교

| 회차 | 근거 | 원인 |
|---|---|---|
| 1회(PR #80, Nestlé) | `development-hq/`를 거치지 않는 project-local Dogfooding | 프록시/자체 서명 인증서 오류 |
| 2회(PR #81, Realty Income) | 동일 | 세션 사용 한도 초과 |
| **3회(이번, EFA)** | **Investment HQ MVP(`investment-hq/run.py`) 경로에서 처음 발생** | **프록시/자체 서명 인증서 오류 — 1회차와 동일 원인** |

**이번 재현은 project-local Dogfooding이 아니라 Investment HQ의 신규
실행 경로에서 처음 발생했다는 점이 새롭다.** `investment-hq/
checkpoint.py`의 `Checkpointer`/`run_step`이 `projects/dev-hq-
timeout-recovery-prototype`의 검증된 구조를 그대로 옮긴 것이므로,
이 구조적 한계도 그대로 함께 이식됐다 — 즉 **HQ로 이전한 코드 자체가
새 버그를 만든 것이 아니라, 기존에 알려진 한계가 새 경로에서도
동일하게 나타난 것**이다.

## REPRODUCTION_COUNT / DEV_HQ_FEEDBACK — Failure Detection 개선 후보로 격상

**누적 재현 3회.** 사용자 지시 기준("3회째 재현이면 Failure Detection을
Dev HQ 개선 후보로 격상하고 Prototype 필요성을 판단한다")에 따라
**이번에 격상한다**:

- **격상 판정: Yes.** 서로 다른 두 가지 원인(인증서 오류 2회, 세션
  한도 1회)에서 동일한 감지 실패 패턴이 3회 재현됐다 — project-local
  Dogfooding과 Investment HQ MVP 양쪽 경로 모두에서 발생해, 특정
  실행 방식에 국한된 문제가 아니라 `call_engine()` 자체의 구조적
  한계(콘텐츠를 검증하지 않고 stdout을 그대로 반환)임이 확정됐다.
- **Prototype 필요성 판단: 필요하다고 판단한다.** 검증해야 할 최소
  Prototype 범위(다음 PR에서 착수, 이번 PR에서는 구현하지 않음):
  1. 알려진 오류 시그니처("API Error:", "Unable to connect" 등)를
     `call_engine()` 반환값에서 감지하는 project-local 진단 wrapper
     (PR #75의 `call_engine_prototype.py`류 패턴 재사용 — `engine.py`
     자체는 수정하지 않음)
  2. 감지 시 자동 재시도(몇 회, 어떤 backoff)가 실제로 재현율을
     낮추는지 실측
  3. Checkpointing과의 통합 — 콘텐츠 검증 실패를 예외로 승격시켜
     `Checkpointer.save()`가 오탐 콘텐츠를 저장하지 않도록 하는
     최소 변경 범위 확인
- **지금 구현하지 않는다.** `development-hq/`의 `call_engine()`
  자체는 이번에도 수정하지 않았다 — Evidence(3회 재현) → 필요성
  판단(이번 문서) → Prototype(다음 PR) → 채택이라는 순서를 그대로
  따른다.

## DEV_HQ_ISSUES vs Invest HQ 문제 — 분리 확인

- **Dev HQ 문제**: `call_engine()`의 콘텐츠 레벨 실패 미검출(위
  CONTENT_FAILURE/DEV_HQ_FEEDBACK). `development-hq/mvp/engine.py`
  자체의 한계이며, project-local Dogfooding·Investment HQ MVP 양쪽
  모두에서 동일하게 나타난다 — Invest HQ가 새로 만든 문제가 아니다.
- **Invest HQ 문제**: 이번 실행에서 관찰되지 않았다. 3개 Team의 역할
  구조, `investment-hq/checkpoint.py`의 동시성 처리(Lock), `run.py`
  의 Team 선택 로직 전부 의도대로 동작했다.

## DECISION

**Investment HQ MVP의 최소 E2E 경로가 실제로 동작함을 확인했다** —
HQ에서 Team을 선택하고, 신규 종목(EFA, 국제 자산)을 실제로 분석해
품질 저하 없이 완주했다(재개 포함). 3회째 콘텐츠 레벨 실패 재현은
Dev HQ 개선 후보로 공식 격상하되, 이번 PR에서 `development-hq/`를
수정하지 않는다 — Prototype은 별도 PR로 착수를 권고한다.

## ARCHIVE_PLAN — 후보만 기록, 실제 이동/삭제 없음

Investment HQ MVP가 이번 실행으로 **최초로 동작을 증명**했을 뿐,
아직 "안정적으로 기존 project-local Dogfooding과 동일한 기능을
수행"한다고 보기엔 이르다(실행 1건, 재현성 미검증). 따라서 이번
PR에서는 다음 후보만 기록하고 **아무 파일도 이동·삭제하지 않는다**:

| 후보 | 분류(잠정) | 근거 |
|---|---|---|
| `projects/{stock,etf,dividend-stock}-analysis-*`(18건) | 유지(Archive 대상 아님) | EVIDENCE.md·핵심 결과·call_log 등 검증 가치 있는 완료 기록. Investment HQ가 안정화되기 전까지 유지 |
| `projects/dev-hq-timeout-recovery-prototype/`(Prototype A~E) | Archive 후보(추후) | Investment HQ의 `checkpoint.py`/`engine_client.py`에 구조가 흡수됨. 단, Evidence 문서(EVIDENCE.md류)는 Dev HQ 개선 판단의 근거 기록이므로 보존 우선 검토 |
| `archive/v1/hqs/investment-hq/` | 그대로 유지(이미 Archive) | 1줄 stub, 이번에 참고도 재사용도 하지 않음 — 기존 Archive 상태 유지가 맞다 |

**Archive 이동 조건(다음 단계, 이번에 실행하지 않음)**: Investment
HQ MVP가 (a) 3개 Team 전부에서 반복 재현되고, (b) 기존 project-local
실행과 동등하거나 더 나은 신뢰성을 보이고, (c) 사용자가 안정화를
확인한 뒤에만 개별 파일 단위로 유지/Archive/삭제를 결정한다. 참조·
테스트·문서 링크 검증은 그 단계에서 수행한다.

## PHASE9_11

이번 Investment HQ MVP 검증은 Phase 9~11 재개 조건이 아니다 — 별도
조건(Investment HQ 자체의 다음 단계 필요성, 사용자 판단)을 충족해야
하며, 자동으로 재개하지 않는다.

## 관찰되지 않은 것 (명시적으로 기록)

- Stock/Dividend Stock Team의 `investment-hq/run.py` 경로 검증 —
  이번엔 ETF Team만 실행(코드는 3개 Team 모두 준비됐으나, 실제 실행
  증거는 ETF 1건뿐).
- Content-level 실패 감지 Prototype의 실제 구현 — 판단만 하고 구현
  하지 않음.
- Investment HQ MVP의 반복 재현성(2회 이상 시행) — 이번엔 1건만 실행.
- 기존 project-local 프로젝트의 실제 Archive 이동 — 안정화 전까지
  보류.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다(3회째 재현을
확인만 하고 `call_engine()`을 고치지 않음). 기존 완료 프로젝트(18건)
는 어느 것도 이동·삭제·수정하지 않았다. 새 Capability/Agent/Kernel
Component/Contract를 만들지 않았다. v1.0 Freeze를 해제하지 않았다.
RFC/ADC/ADR을 작성하지 않았다(Investment HQ 인스턴스화 자체가 RFC
대상이 아니라는 판단은 `investment-hq/STRUCTURE.md`에 이미 기록).
Phase 9~11 재개는 하지 않았다.
