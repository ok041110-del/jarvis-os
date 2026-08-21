# Evidence — Investment HQ MVP E2E 검증 (PG, Dividend Stock Team)

`hqs/investment/run.py`를 통한 Dividend Stock Team 실행. `efa-2026-08`
(ETF Team), `aapl-hq-verify`(Stock Team)에 이어 세 번째 Team의 HQ 경로
검증이며, roadmap.md Phase 2 완료 조건(3개 Team 전부 HQ-level 실행
증명)의 마지막 항목이다. `raw_data.md`는 `projects/dividend-stock-
analysis-pg/issues/0001-pg-analysis/raw_data.md`를 그대로 복사해
재사용했다(원본 미수정).

## TARGET

PG(Procter & Gamble) — FY2026 Q4(2026-07-29 발표) 실적 기준 데이터.

## 실행 결과

| 시도 | 결과 |
|---|---|
| 1차 | 9단계(7개 분석 + Bull/Bear) 성공, **Synthesis 호출이 콘텐츠 레벨 실패**(아래 CONTENT_FAILURE 참조), Final Report Writer는 손상된 Synthesis 입력을 감지하고 스스로 우회해 완주(품질 저하 있음, 아래 참조) |
| 2차(수동 복구, 재개) | `checkpoints/manifest.json`에서 `synthesis`/`final_report` 두 단계만 완료 목록에서 제거하고 해당 파일 삭제 → 7+2단계는 Engine 재호출 없이 스킵, Synthesis/Final Report만 재실행 → **콘텐츠 레벨 실패 없이 완주** |

**2차 시도 기준 E2E 시간(재구성)**: Wave1(7개 분석, 병렬) 39.5초 +
Wave2(Bull/Bear, 병렬) 39.9초(1차 시도값, 스킵되어 재계측 안 됨) +
Wave3(Synthesis, 2차) 39.3초 + Wave4(Final Report, 2차) 37.9초 =
**156.6초**(1차+2차 실측 합산).

**주의**: EFA 선례와 달리 이번엔 `checkpoint.py`가 실패 콘텐츠를 자동
스킵하지 않았다 — 재개를 위해 `checkpoints/manifest.json`을 수동으로
편집해 `synthesis`/`final_report`를 완료 목록에서 제거해야 했다(아래
DEV_HQ_ISSUES 참조). 이는 `checkpoint.py`/`run.py` 자체 수정이 아니라
기존 실행 산출물(이 실행에서 생성된 것)을 정리한 것이다.

## QUALITY (2차 시도, 최종 채택본)

- 9개 필수 섹션(Fundamental/Dividend Quality/Valuation/Technical/
  Industry/News-Event/Sentiment/Bull Case/Bear Case/Synthesis) +
  Disclaimer — **전부 존재**
- 1,220단어(목표 800~1200단어 범위를 근소하게 초과 — 220단어 초과)
- raw_data.md 핵심 수치 24항목 스팟체크 결과 **22/24 Final Report에서
  확인됨**(grep 기반). 누락 2건: 배당수익률 3.02%(배당 관련 수치 중
  연간 배당액 $4.35/36과 배당성향 63.77%는 보존되었으나 수익률 %
  자체는 본문에 명시 안 됨), P/E(TTM) 21.66배(Forward P/E 25.4/21.1은
  보존됨)
- Synthesis가 "bull/bear가 동일 사실에서 해석만 다르다"는 점과 5개
  미해결 쟁점(배당성향 산정 기준, 관세/구조조정 비용의 가이던스 반영
  여부, P/FCF 프리미엄의 근거 부재 등)을 명시적으로 자기인정 —
  AAPL/EFA와 동일한 자기인정 패턴 재현

**결론: Dividend Stock Team의 7개 분석 역할이 `run.py`를 통해서도
지시문 변경 없이 유효했다. 다만 이번 실행은 콘텐츠 레벨 실패를
1차에서 실제로 겪었고, 자동 재개가 아닌 수동 개입으로 복구했다는
점에서 AAPL/EFA와 다르다(아래 DEV_HQ_ISSUES 참조).**

## TOKENS / COST / CALL_COUNT

- **CALL_COUNT**: 실제 Engine 호출 13회(1차 11회: 7개 분석+Bull/Bear+
  Synthesis(실패)+Final Report(손상 입력 기반) + 2차 2회: Synthesis
  재실행+Final Report 재실행) — **중복 2회**(Synthesis, Final Report
  각 1회씩 재호출됨). 최종 채택된 유효 콘텐츠는 11건(7분석+Bull/Bear+
  Synthesis 재실행분+Final Report 재실행분)
- **TOKENS**: 13회 호출 output 문자수 합계 55,555자(약 13,889 토큰,
  4자/토큰 근사) — 실패 Synthesis(118자)와 손상 입력 기반 Final
  Report(8,466자)도 포함(실제로 API 호출·과금이 발생했으므로)
- **COST**: 정확한 비용은 계측되지 않음(기존 Dogfooding과 동일한 계측
  한계)

## CONTENT_FAILURE — 4회째 재현 확정

1차 시도의 Synthesis 호출이 `"API Error: Unable to connect to API:
Self-signed certificate detected. Check your proxy or corporate SSL
certificates"`를 반환했고, `call_engine()`이 이를 예외로 처리하지
않아 118자 오류 메시지가 `synthesis.md`에 정상 산출물처럼
체크포인트됐다 — PR #80/#81, EFA(3회)와 동일한 구조적 패턴.

**새로 관찰된 것(EFA와의 차이)**: EFA에서는 오류가 Synthesis 단계에서
멈췄지만, 이번엔 그 손상된 Synthesis가 그대로 Final Report Writer의
입력으로 전달됐다. Final Report Writer(Engine 호출)는 입력에 포함된
"API Error: ..." 문자열을 콘텐츠가 아니라 오류로 스스로 인식하고,
"*(Note: the original Synthesis input for this report failed with an
API error... the following is derived directly from the sections
above)*"라는 문구와 함께 Bull/Bear Case 등 상위 섹션에서 직접 재구성한
Synthesis를 대신 작성했다. 즉 **Engine 자신은 콘텐츠 레벨 실패를
인식했지만, `call_engine()`/`Checkpointer`는 인식하지 못해 손상된
중간 산출물(`synthesis.md`)이 디스크에 그대로 남았다** — Engine의
자기인식과 파이프라인의 기계적 검증 부재가 분리되어 있음을 보여주는
새로운 관찰.

## FAILURE_CAUSE — 기존 3건과의 비교

| 회차 | 근거 | 원인 |
|---|---|---|
| 1회(PR #80, Nestlé) | project-local Dogfooding | 프록시/자체 서명 인증서 오류 |
| 2회(PR #81, Realty Income) | 동일 | 세션 사용 한도 초과 |
| 3회(EFA, `run.py` 경로) | Investment HQ MVP | 프록시/자체 서명 인증서 오류 |
| **4회(이번, PG, `run.py` 경로)** | **Investment HQ MVP** | **프록시/자체 서명 인증서 오류 — 1·3회차와 동일 원인** |

## REPRODUCTION_COUNT / DEV_HQ_FEEDBACK — 기존 격상 판정 재확인, 새 관찰 추가

**누적 재현 4회.** EFA(3회째)에서 이미 "Failure Detection을 Dev HQ
개선 후보로 격상"이 판정되었다(`efa-2026-08/EVIDENCE.md`). 이번
재현은 그 판정을 재확인하는 동시에 새 정보를 추가한다:

- **격상 판정**: 기존 판정 유지(Yes) — 이번이 재확인.
- **새로 추가된 판단 근거**: 손상된 콘텐츠가 후속 단계(Final Report)
  로 전파될 수 있고, 후속 단계의 Engine이 스스로 오류를 인식해도
  파이프라인 상의 중간 체크포인트 파일(`synthesis.md`)은 여전히
  손상된 채로 남는다 — 즉 "다음 호출의 Engine이 알아서 우회했으니
  괜찮다"고 볼 수 없다. 이는 EFA가 제안한 Prototype 범위(오류
  시그니처 감지 → 체크포인트 저장 차단)가 여전히 유효하며, 오히려
  **Final Report 같은 하위 소비 단계까지 오류가 전파되는 경로**를
  함께 검증해야 한다는 근거를 추가한다.
- **지금 구현하지 않는다.** `hqs/development/mvp/engine.py`는 이번에도
  수정하지 않았다. 이번 EVIDENCE는 Prototype 착수 필요성의 근거를
  하나 더 추가한 것뿐이다.

## DEV_HQ_ISSUES vs Invest HQ 문제 — 분리 확인

- **Dev HQ 문제**: `call_engine()`의 콘텐츠 레벨 실패 미검출(4회째
  재현, 위 CONTENT_FAILURE/REPRODUCTION_COUNT). `hqs/development/mvp/
  engine.py` 자체의 한계이며 이번에도 수정하지 않았다.
- **Invest HQ 문제**: `hqs/investment/checkpoint.py`가 콘텐츠 레벨
  실패를 감지하지 못해 재개 시 자동 스킵 대신 **수동 manifest 편집이
  필요했다** — EFA에서는 "8단계 정확히 스킵"이라고만 기록되었을 뿐
  실제 재개 절차가 자동인지 수동인지 이번 EVIDENCE만큼 상세히
  기록되지 않았다. 이는 Investment HQ(`checkpoint.py`) 자체의 한계로
  분리 기록한다 — Dev HQ의 `call_engine()` 콘텐츠 미검출과는 별개로,
  Invest HQ의 `Checkpointer`도 "완료됨"과 "성공적으로 완료됨"을
  구분하지 않는다는 동일 계열의 문제를 갖고 있다. 이번 PR에서
  `checkpoint.py`를 수정하지 않는다(Observe First, Decide Later).

## DECISION

**Investment HQ MVP의 `run.py` 경로가 Dividend Stock Team에서도
실제로 동작함을 확인했다** — 콘텐츠 레벨 실패를 실제로 겪었지만
수동 재개로 완주했고, 9개 필수 섹션과 22/24 핵심 수치가 보존됐다.
이로써 **3개 Team(Stock/ETF/Dividend Stock) 전부가 `hqs/investment/
run.py` 경로에서 최소 1건 이상 EVIDENCE.md와 함께 검증 완료** —
roadmap.md Phase 2 완료 조건을 충족한다.

## 관찰되지 않은 것 (명시적으로 기록)

- Dividend Stock Team의 반복 재현성(2회 이상 정상 시행) — 이번엔
  콘텐츠 레벨 실패 1회 + 수동 복구 1회로, "정상 1차 완주" 사례는
  아직 3개 Team 중 AAPL/EFA 2건뿐이다.
- Final Report Writer의 자기인식 우회가 항상 안전한지 — 이번엔
  결과적으로 합리적인 문구를 생성했으나, 다른 실패 시그니처(빈 응답,
  부분 응답 등)에서도 동일하게 안전한지는 검증되지 않았다.
- `Checkpointer`에 콘텐츠 검증을 추가하는 Prototype의 실제 구현 —
  판단만 하고 구현하지 않음.

---

# Architecture/Contract 변경 여부

**없음.** `hqs/development/` 어떤 파일도 수정하지 않았다(4회째 재현을
확인만 하고 `call_engine()`을 고치지 않음). `hqs/investment/
checkpoint.py`도 수정하지 않았다(수동 manifest 편집은 이번 실행
산출물에 대한 것이며, 코드 변경이 아니다). 기존 완료 프로젝트
(`projects/dividend-stock-analysis-pg`)는 읽기만 했고 수정하지
않았다. 새 Capability/Agent/Kernel Component/Contract를 만들지
않았다. Structure v1.0 / Development HQ v1.0 Freeze를 변경하지
않았다. RFC/ADC/ADR을 작성하지 않았다.
