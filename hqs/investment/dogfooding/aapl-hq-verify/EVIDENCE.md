# Evidence — Investment HQ MVP E2E 검증 (AAPL, Stock Team)

`hqs/investment/run.py`를 통한 Stock Team 실행. `efa-2026-08`(ETF Team)에
이어 두 번째 Team의 HQ 경로 검증이며, roadmap.md Phase 2 완료 조건의
일부(`aapl-hq-verify`)다. AAPL 자체는 `projects/stock-analysis-aapl`에서
이미 project-local로 검증된 종목이지만, 이번 목적은 종목 분석이 아니라
**Stock Team이 `run.py` 경로에서도 project-local과 동일하게 동작하는지**
검증하는 것이다. `raw_data.md`는 `projects/stock-analysis-aapl/issues/
0001-aapl-analysis/raw_data.md`를 그대로 복사해 재사용했다(원본 미수정).

## TARGET

AAPL(Apple Inc.) — Q3 FY2026 실적(2026-07-30 발표) 기준 데이터.

## 실행 결과

| 시도 | 결과 |
|---|---|
| 1차 | 9단계(5개 분석 + Bull/Bear + Synthesis + Final Report) **전부 성공, 콘텐츠 레벨 실패 없음** |

**E2E 시간**: Wave1(5개 분석, 병렬) 42.3초 + Wave2(Bull/Bear, 병렬) 31.5초
+ Wave3(Synthesis) 42.2초 + Wave4(Final Report) 33.2초 = **149.3초**.

## QUALITY

- 8개 필수 섹션(Fundamental/Technical/Industry/News-Event/Sentiment/
  Bull Case/Bear Case/Synthesis) + Disclaimer — **전부 존재**
- 1,066단어(목표 800~1200단어 범위 내)
- raw_data.md 핵심 수치 19항목(매출 $109.4B/+16%, EPS $2.02/+29%,
  iPhone $54.3B, Mac $10.35B, Services $30.74B, 영업이익 $35.7B, 50일/
  200일 이평 $295.9/$271.9, 지지/저항 $246.24/$315.2, 미국 점유율
  58.2%/28.4%, 목표주가 $322.82/$322.71, 목표범위 $215~$400, 추정치
  상향 +6.44% 등) 스팟체크 결과 **19/19 전부 Final Report에서 확인됨**
  (grep 기반 검증, `grep -c` 결과 전부 ≥1)
- Synthesis가 "bull/bear가 동일 데이터셋에서 해석만 다르다"는 점과
  raw_data의 데이터 갭(마진율 부재, 중국 지표 부재, 현재가 부재 등)을
  명시적으로 자기인정 — project-local Dogfooding 및 EFA에서 관찰된
  자기인정 패턴이 이번에도 재현됨

**결론: Stock Team의 5개 분석 역할이 `run.py`를 통해서도 지시문 변경
없이 유효했고, 콘텐츠 레벨 실패 없이 1차 시도로 완주했다.**

## TOKENS / COST / CALL_COUNT

- **CALL_COUNT**: 9회(Stock Team 구조: 5개 분석 + Bull/Bear + Synthesis
  + Final Report), 중복 0회
- **TOKENS**: 9회 호출 output 문자수 합계 34,871자(약 8,718 토큰, 4자/
  토큰 근사)
- **COST**: 정확한 비용은 계측되지 않음(기존 Dogfooding과 동일한 계측
  한계 — `call_engine()`이 `--output-format text`만 반환)

## CONTENT_FAILURE

**이번 실행에서는 재현되지 않았다.** EFA(3회째)에서 재현된 `call_engine()`
콘텐츠 레벨 실패(API Error가 예외로 처리되지 않고 정상 산출물처럼
체크포인트되는 문제)가 AAPL에서는 발생하지 않았다 — 문제가 항상
재현되는 것이 아니라 간헐적(프록시/인증서 상태에 의존)임을 보여준다.

## DEV_HQ_ISSUES vs Invest HQ 문제 — 분리 확인

- **Dev HQ 문제**: 이번 실행에서 관찰되지 않음.
- **Invest HQ 문제**: 관찰되지 않음. Stock Team의 5개 분석 역할,
  `checkpoint.py`의 저장/스킵 로직, `run.py`의 Team 선택 로직 전부
  의도대로 동작했다.

## DECISION

**Investment HQ MVP의 `run.py` 경로가 Stock Team에서도 실제로 동작함을
확인했다** — 콘텐츠 레벨 실패 없이 1차 시도로 완주, 8개 필수 섹션과
19개 핵심 수치 전부 보존.

## 관찰되지 않은 것 (명시적으로 기록)

- Stock Team의 반복 재현성(2회 이상 시행) — 이번엔 1건만 실행.
- 콘텐츠 레벨 실패 시나리오(이번엔 발생하지 않음 — PG(Dividend Stock)
  실행에서 재현됨, `pg-hq-verify/EVIDENCE.md` 참조).

---

# Architecture/Contract 변경 여부

**없음.** `hqs/development/` 어떤 파일도 수정하지 않았다. 기존 완료
프로젝트(`projects/stock-analysis-aapl`)는 읽기만 했고 수정하지
않았다(raw_data.md 복사본만 별도 디렉토리에 생성). 새 Capability/
Agent/Kernel Component/Contract를 만들지 않았다. Structure v1.0 /
Development HQ v1.0 Freeze를 변경하지 않았다. RFC/ADC/ADR을 작성하지
않았다.
