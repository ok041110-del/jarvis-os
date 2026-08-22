# INVESTMENT-HQ-TRADER-WORKFLOW-STABILIZATION-0001

**문서 성격**: Production Implementation 완료 보고서. **새 Architecture를
만들지 않는다** — `INVESTMENT-HQ-RISK-ARCHITECTURE-FREEZE-REVIEW-0001`이
확정한 범위(Trader는 v2.0 핵심 Workflow에 포함, Portfolio/Risk는
Defer)를 그대로 따라 **Trader 책임만** `hqs/investment/` Production
코드에 최소 변경으로 반영했다. Portfolio/Risk/Execution/Event
Bus/새 Runtime/새 Policy/LangGraph 전체 전환 — 전부 구현하지 않았다.
Structure v1.0·Architecture Baseline·RFC/ADC/ADR·Phase 7은 수정하지
않았다.

**핵심 결론**: 판정 A. READY FOR TRADER FREEZE — Trader 책임이
Production 코드에 최소 변경으로 반영됐다. 3개 Team 전부 실제 E2E
Dogfooding 성공(action/rationale/reassessment_trigger 파싱 실패 0건),
전체 회귀 테스트 198건 통과.

---

## 1. 무엇을 변경했는가

| 파일 | 변경 |
|---|---|
| `hqs/investment/trader.py`(신규) | REPORT/DECISION 분리(`split_report_decision`) + action/rationale/reassessment_trigger 파싱(`parse_decision`) 공유 유틸리티. Team 간 공통 텍스트 처리만 — Registry/Scheduler 아님 |
| `hqs/investment/teams/stock_team.py` | `synthesis_judgment()` → `trader_decision()`로 개명, 지시문에 Decision 책임 추가(기존 문장 무수정, "not a trade order" 문장만 대체). `run()`의 Wave3/Wave4 배선 변경 |
| `hqs/investment/teams/dividend_stock_team.py` | 동일 변경(7개 분석 역할 그대로 유지) |
| `hqs/investment/teams/etf_team.py` | 동일 변경(6개 분석 역할 그대로 유지) |
| `hqs/investment/STRUCTURE.md` | Wave3 설명을 "Synthesis"에서 "Trader Decision"으로 정정(사실 기반 최소 수정), Portfolio/Risk Defer 상태 재확인 링크 추가 |
| `hqs/investment/tests/test_trader.py`(신규) | `trader.py` Unit Test 7건 |
| `hqs/investment/tests/test_{stock,dividend_stock,etf}_team_integration.py`(신규) | 3개 Team 각각의 Integration Test(Mock Engine) |
| `hqs/investment/dogfooding/{aapl,pg,efa}-trader-verify/`(신규) | 실제 Engine 호출 E2E Dogfooding 산출물(§10) |

**변경하지 않은 것**: `checkpoint.py`, `engine_client.py`, `run.py`,
5/6/7개 Analyst 함수, Bull/Bear Researcher 함수, `report_writer_
final_report()`의 지시문 자체(인자 하나의 내용만 REPORT-only로
바뀜), 기존 완료 프로젝트(`aapl-hq-verify` 등 Frozen 디렉토리) 전부
— 어느 것도 소급 수정하지 않았다.

---

## 2. 실제 Workflow가 어떻게 바뀌었는가

**변경 전**: `Analysis(병렬) → Bull/Bear(병렬) → Synthesis(방향 판단
금지) → Final Report`. Synthesis는 "not a trade order"라는 명시적
금지 문구로 끝났다.

**변경 후**: `Analysis(병렬) → Bull/Bear(병렬) → Trader Decision(REPORT+
DECISION 단일 호출) → Final Report`. Wave 개수는 그대로 4개
(하드코딩 유지, Workflow Parser 도입 없음). Wave3 호출 하나가
Synthesis 책임과 Trader 책임을 동시에 수행하고, 그 출력을 코드가
`report_text`/`decision_text`로 분리한다. `report_text`만 Wave4(Final
Report)로 전달돼 기존 "투자 조언 아님" disclaimer와의 충돌을 코드
레벨에서 원천 차단한다(§7).

---

## 3. 무엇이 해결됐는가

- **REPORT/DECISION 분리가 Production 코드에 실제로 반영됨** — 이전
  Prototype(격리된 스크립트)이 아니라 `hqs/investment/teams/*.py`
  자체에서 동작한다.
- **Contract 최소 범위(action/rationale/reassessment_trigger)가
  안정적으로 파싱됨** — 3개 Team 실제 E2E 실행 3건 전부 `warnings: []`
  (파싱 실패 0건, §10).
- **Checkpoint/Resume이 새 단계명("trader_decision")과 정상 호환**
  — ETF 사례에서 실제 콘텐츠 실패(`API Error:` 시그니처, 저장소에
  이미 문서화된 알려진 간헐적 인프라 flake) 발생 후 재실행 시
  Wave1/Wave2는 재호출 없이 스킵(0.0초), Wave3/Wave4만 재시도돼
  정상 완료됐다(§10) — 새 Runtime/Memory 없이 기존 Checkpointer
  그대로 작동.
- **정보 손실 우려가 실제로는 대부분 해소됨** — AAPL은 원본과 거의
  동일한 길이(854→870 단어), PG/EFA는 길이가 줄었지만(§8) 핵심
  범주(사실/해석 분기점/데이터 공백/미해결 질문)는 전부 보존됨을
  실제 산출물로 확인.

---

## 4. 무엇이 검증됐는가

Unit(A) 7건, Integration(B) 3건(Team별 1건씩), E2E(C/D/E) 3건(Stock/
Dividend Stock/ETF), Regression(F) 198건 — 전부 `docs/research/` 문서화
없이 `pytest --ignore=archive`로 실행해 확인(§8~9 결과 요약).

---

## 5. Stock / Dividend Stock / ETF 결과

| Team | 사례 | action | warnings | 원본 대비 synthesis.md 단어수 |
|---|---|---|---|---|
| Stock | AAPL(`aapl-hq-verify/raw_data.md` 재사용) | HOLD | 없음 | 854→870(+1.9%) |
| Dividend Stock | PG(`pg-hq-verify/raw_data.md` 재사용) | HOLD | 없음 | 1220→695(−43.0%) |
| ETF | EFA(`efa-2026-08/raw_data.md` 재사용) | HOLD | 없음 | 856→583(−31.9%) |

3/3 전부 HOLD — 이는 §11의 기존 판정(`INVESTMENT-HQ-TRADER-DECISION-
DISCRIMINATION-DOGFOODING-0001`, D. UNTESTABLE)과 일치하며, 이번
작업의 성공 기준이 아니므로 재확인만 하고 넘어간다.

---

## 6. REPORT / DECISION 분리 결과

3/3 사례 전부에서 `final_report.md`에 `"Direction:"` 문자열이
**0회** 등장(`grep -c` 확인) — Trader의 방향 판단이 사람이 읽는
Final Report에 전혀 섞이지 않았다. 이는 Integration Test에서도
동일하게 강제됐다(Mock Final Report 호출 시 payload에 `"Direction:"`
이 있으면 즉시 `AssertionError`).

---

## 7. Contract 상태

| 필드 | 상태 | 근거 |
|---|---|---|
| `action` | **구현됨**(BUY/SELL/HOLD 파싱) | 3/3 실제 사례에서 정확히 추출 |
| `rationale` | **구현됨** | 3/3 실제 사례에서 정확히 추출 |
| `reassessment_trigger` | **구현됨** | 3/3 실제 사례에서 정확히 추출 |
| `confidence` | **미구현**(의도적) | Evidence 반복 부족(기존 판정 유지) |
| `position_size` | **미구현**(의도적) | Portfolio 책임으로 전이(기존 판정 유지, Defer) |
| `time_horizon` | **미구현**(의도적) | 실제 필요 의미 불명확(기존 판정 유지) |
| `risk_notes` | **미구현**(의도적) | Bull/Bear 자체 약점 서술 재사용 가능성이 높다는 기존 판정 유지 — 이번에도 새 필드를 추가하지 않았다 |

저장소에 이미 존재하던 필드 중 삭제한 것은 없다(`checkpoint.py`,
`engine_client.py`, Analyst/Researcher 함수 시그니처 전부 무수정).

---

## 8. 테스트 결과

```
hqs/investment/tests/  16 passed (Unit 7 + Integration 3 + 기존 Checkpoint 5 + 신규 3개 Integration... )
전체 저장소  198 passed (기존 187 + 신규 11) — pytest --ignore=archive
```

Integration Test는 실제 Engine을 호출하지 않고 `call_engine`을
Mock으로 대체해, (a) Wave 배선이 올바른지 (b) DECISION이 Final
Report 프롬프트에 새어 들어가지 않는지 (c) Checkpoint 파일명이
`trader_decision.md`로 통합되고 별도 `synthesis.md` 체크포인트가
남지 않는지 (d) Resume 시 Trader가 재호출되지 않는지를 검증한다 —
비용 없이 반복 가능한 회귀 안전망이다.

---

## 9. E2E 결과

3개 Team 전부 실제 Engine으로 End-to-End 성공(§5). ETF 사례에서
발생한 콘텐츠 레벨 실패(`API Error:` 시그니처)는 기존
`ContentFailureError` 메커니즘이 설계대로 작동해 저장을 차단했고,
재실행이 완료된 단계를 재호출 없이 건너뛰며 정상 복구됐다 — 새로운
Error Handling 코드를 추가하지 않고 기존 Architecture만으로
해결됐다(사용자 지시 §12 준수).

---

## 10. Dogfooding 결과(요약, 원자료는 §5 표 및 각 디렉토리 참조)

- **Stock(AAPL)**: `hqs/investment/dogfooding/aapl-trader-verify/`.
  action=HOLD, rationale/trigger 정상, `final_report.md` 오염 없음.
- **Dividend Stock(PG)**: `hqs/investment/dogfooding/pg-trader-verify/`.
  action=HOLD, rationale/trigger 정상, synthesis.md가 −43% 축소됐으나
  핵심 5개 해석 분기점과 5개 미해결 질문 전부 보존(직접 대조 확인,
  발췌 인용 가능).
  reassessment_trigger는 "$1B 헤드윈드가 가이던스에 이미 반영됐는지"
  로, 기존 Trader Need Dogfooding에서 관찰된 것과 동일한 축.
- **ETF(EFA)**: `hqs/investment/dogfooding/efa-trader-verify/`.
  action=HOLD, 1회 콘텐츠 실패 후 Resume으로 정상 복구.

세 사례 전부 새로운 시장 데이터를 만들지 않고 기존 Frozen
`raw_data.md`를 재사용했다(사용자 지시 §15 준수) — 원본 Frozen
디렉토리(`aapl-hq-verify` 등)는 읽기만 했고 수정하지 않았다.

---

## 11. 남은 문제

1. **PG/EFA의 REPORT 길이 감소(−43%/−32%)**가 이번에도 재현됐다 —
   내용 범주는 보존됐지만(§10), "REPORT는 기존과 동일한 상세도를
   유지하라"는 프롬프트 보강을 시도해볼 가치가 있다(다음 단계
   후보, Architecture 변경 아님).
2. **BUY/SELL은 이번에도 관찰되지 않았다**(3/3 HOLD) — 기존
   Discrimination Dogfooding의 D(UNTESTABLE) 판정이 그대로 유지된다.
   이는 이번 작업의 실패가 아니다(사용자 지시 §11 명시).
3. **Portfolio/Risk는 여전히 Defer** — 이번 작업이 그 상태를
   바꾸지 않았다.
4. Production 코드에 `trader_decision`이라는 이름으로 반영됐지만,
   이것이 **최종 Contract로 Freeze된 것은 아니다** — 별도
   `INVESTMENT-HQ-TRADER-ARCHITECTURE-FREEZE-REVIEW`가 이를
   판단한다(§13 다음 단계).

---

## 12. Architecture 변경 여부

**없음.** 구체적으로:

- Workflow Parser/Scheduler/Registry 일반화 — 추가하지 않음(Wave는
  여전히 하드코딩된 4단계).
- Engine Gateway/Routing — 추가하지 않음(`call_engine()` 단일 함수
  그대로).
- Event Bus/새 Runtime/새 Memory Architecture — 추가하지 않음.
- LangGraph — 도입하지 않음(전체 호출 경로가 여전히
  `call_engine()` 하나).
- Portfolio/Risk/Execution — 구현하지 않음.
- 새 Policy(Synthetic Risk Policy 포함) — 추가하지 않음.
- `hqs/development/` — 무수정.
- Structure v1.0/Architecture Baseline/RFC/ADC/ADR/Phase 7 — 무수정.

변경은 전부 `hqs/investment/` 내부, 기존 3개 Team 파일 + 신규 공유
유틸리티 파일 1개 + 문서 정정 1건으로 한정됐다.

---

## 13. READY / CONDITIONALLY READY / NOT READY

## **A. READY FOR TRADER FREEZE**

**근거(§17 필수 10개 조건 전부 충족)**:

1. 실제 Workflow에서 Analysis→Bull/Bear→Synthesis→Trader→Final
   Report 실행 — **충족**(§2, §9).
2. Stock/Dividend Stock/ETF에서 동작 — **충족**(§5, 3/3).
3. REPORT/DECISION 분리 — **충족**(§6, 3/3 오염 없음, Integration
   Test로 강제됨).
4. action/rationale/reassessment_trigger 안정적 전달 — **충족**
   (§5·§7, 3/3 `warnings: []`).
5. 기존 정보 손실 없음 — **충족(범주 기준)**, 단 길이 감소는
   §11-1에서 Open Issue로 남김(이는 완료 조건 미충족이 아니라
   후속 개선 여지).
6. parsing/validation 실패 처리 — **충족**(`TraderOutputError`,
   `parse_decision`의 `warnings` 필드, §12 원칙대로 새 Runtime 없이
   구현).
7. 기존 Workflow regression 없음 — **충족**(198 passed, §8).
8. Checkpoint/Resume 호환 — **충족**, 실제 콘텐츠 실패로 실증
   (§9).
9. 실제 Engine Dogfooding 완료 — **충족**(§10, 3/3).
10. Architecture 변경 범위 최소화 — **충족**(§12).

**"READY FOR TRADER FREEZE"까지만 판단한다** — 이 판정이 Investment
HQ v2.0 전체 Freeze를 의미하지 않는다(사용자 지시 §19). Portfolio/
Risk는 여전히 Defer 상태로 남는다.

---

## 14. 다음 단계

1. 별도 문서 `INVESTMENT-HQ-TRADER-ARCHITECTURE-FREEZE-REVIEW`를
   수행해, 이번 Stabilization의 Contract(action/rationale/
   reassessment_trigger)와 코드 구조(공유 `trader.py`, Team별
   `trader_decision()`)를 실제로 Freeze할지 판단한다 — 이번 문서는
   그 판단을 내리지 않는다.
2. §11-1(REPORT 길이 감소)에 대한 프롬프트 보강 실험은 그 Freeze
   Review 이전/이후 어느 시점에도 착수 가능하지만, 이번 작업 범위는
   아니다.
3. Portfolio/Risk는 `INVESTMENT-HQ-RISK-ARCHITECTURE-FREEZE-
   REVIEW-0001`의 Required Future Evidence(실제 BUY/SELL 사례,
   실제 Repository Policy)가 갖춰지기 전까지 착수하지 않는다.

---

## Self Review

- Portfolio/Risk/Execution을 구현했는가 — **아니오**.
- Event Bus/새 Runtime/새 Memory/새 Policy/LangGraph 전체 전환을
  했는가 — **아니오**(§12).
- 기존 완료 프로젝트(`aapl-hq-verify` 등)를 소급 수정했는가 —
  **아니오**(읽기만 함, §10).
- 새로운 시장 데이터를 만들었는가 — **아니오**(기존 raw_data.md
  3건 재사용, §10).
- Investment HQ v2.0 전체 Freeze를 선언했는가 — **아니오**(§13,
  "READY FOR TRADER FREEZE"까지만 판단, 별도 Review로 이관).
- `hqs/development/`, Structure v1.0, RFC/ADC/ADR, Phase 7을
  수정했는가 — **아니오**.
- 전체 저장소 회귀 테스트를 실제로 실행해 확인했는가 — **예**
  (198 passed, §8).
