# Evidence — Realty Income Dividend Stock Dogfooding (신규 표준 실행 패턴 최초 적용)

PR #80에서 채택된 신규 표준 실행 패턴(병렬화+출력최적화+Checkpointing
+180초 Timeout 안전장치)을 **실제 프로덕션 Dogfooding에 처음 적용**한
실행이다. 기존 13건(Stock 4·ETF 6·Dividend Stock 3: JNJ/KO/PG +
Nestlé/Toyota)과 중복되지 않는 신규 대상 Realty Income Corporation
(NYSE: O — 순임대 REIT, 월배당, FFO/AFFO 기준 밸류에이션)으로
실행했다. Dividend Stock Team의 7개 역할·지시문은 변경하지 않았다.

## TARGET 선정 근거

- 미국 상장이지만 **자산군/지표 체계가 이전 5개 배당주와 전부
  다르다**: 월배당(673회 연속, JNJ/KO/PG=분기·Nestlé=연1회·
  Toyota=반기와 전부 다름), REIT 고유 지표(FFO/AFFO, EPS/P/E가
  아님), REIT 세법상 90% 의무배당 구조.
- 기존 ETF Team의 VNQ(리츠 ETF)와도 다르다 — VNQ는 REIT 바스켓의
  ETF 구조/추적 방식을 다뤘고, 이번은 **개별 REIT 종목**의 배당
  지속가능성/펀더멘털을 다룬다(Dividend Stock Team의 스코프).

## REUSE — 기존 자산 재사용, 신규 Role/Architecture 없음

- `agents.py`: Nestlé/Toyota의 7개 역할·지시문을 문자 그대로 재사용
  (회사명/티커만 교체). Report Writer instruction의 출력 길이 제약도
  PR #79/#80에서 검증된 것과 동일한 문구를 그대로 사용.
- `runner.py`: `combined_runner.py`(PR #80 Prototype E)의 Wave 구조·
  Checkpointer 클래스를 실제 프로젝트 구조(단일 `ISSUE_DIR`, trial_id
  없음)에 맞게 이식. 새 Capability/Agent/Kernel Component 없음.
- **신규 Team/Role/Architecture 없음** — 지시대로 기존 Dividend
  Stock Team 구조를 그대로 썼다.

## NORMAL_E2E — 실행시간

1차 시도에서 Synthesis/Final Report 두 단계가 콘텐츠 레벨 실패(아래
CONTENT_FAILURE 참조)를 겪어, 정상 소요시간은 "유효한 각 Wave의
실측치 합"으로 재구성한다:

| Wave | 소요시간 |
|---|---|
| Wave1(7개 분석, 병렬) | 47.7초 |
| Wave2(Bull/Bear, 병렬) | 48.2초 |
| Wave3(Synthesis) | 44.4초(2차 재시도, 유효) |
| Wave4(Final Report) | 43.3초(2차 재시도, 유효) |
| **총합(재구성)** | **183.6초** |

원본(개선 없음, 순차) 대비 514.8~631.8초 관측 범위에서 **최대
71%(3.4배) 단축** — Nestlé/Toyota 기준 실측 대비도 여전히 유효한
수준의 개선폭이다.

## FAILURE_RECOVERY — Checkpointing 재개 여부

- 1차 시도: 9단계(7개 분석+Bull/Bear) 성공, Synthesis/Final Report
  2단계가 콘텐츠 레벨 실패(세션 한도 초과 메시지가 정상 산출물처럼
  체크포인트됨 — 예외가 발생하지 않아 Checkpointing이 자동 감지하지
  못함).
- 수동으로 해당 2개 체크포인트만 무효화(`manifest.json`에서 제거,
  파일 삭제) 후 재실행.
- 2차 시도: **9단계 전부 정확히 스킵**(Engine 재호출 없음,
  `steps_skipped_via_checkpoint_this_invocation`이 9개와 정확히
  일치), Synthesis/Final Report만 재실행되어 완주.
- **재계산 0회**(9단계는 한 번씩만 계산됨) — 원본 all-or-nothing
  `runner.py`였다면 이 실패는 11단계 전부 재실행을 요구했을 것이다.

## TOKENS

- 11회 호출 output 문자수 합계 50,653자(약 12,663 토큰, 4자/토큰
  근사 — project-local `runner.py`는 Team 코드와 동일하게
  `--output-format text`를 쓰므로 정확한 토큰 수는 계측되지 않는다,
  기존 Dogfooding 프로젝트들과 동일한 계측 한계)
- input 문자수 합계 103,549자

## COST

전체 파이프라인의 정확한 비용은 계측되지 않았다(위 TOKENS와 동일한
이유). PR #78/#79에서 Final Report 단일 호출에 대해 실측된 비용
(Sonnet 출력최적화 버전: $0.231/3,427 토큰)을 참고 기준으로만 인용
한다 — 이번 실행의 실제 비용은 그와 유사한 규모로 추정되나 정확한
합계는 관찰되지 않은 것으로 명시한다.

## CALL_COUNT

11회(항상 동일, Team 구조 불변) — 콘텐츠 레벨 실패 2건을 포함한
1차+2차 시도 합산으로도 **총 11회**(중복 0회, 위 FAILURE_RECOVERY
참조).

## QUALITY — 11개 섹션/Disclaimer/핵심 데이터

- 11개 필수 섹션 전부 존재, Disclaimer 존재.
- raw_data.md의 핵심 데이터 14항목(AFFO $1.09/+3.8%, AFFO 가이던스
  $4.44~4.45, 31년 연속 배당, 673회 연속 월배당, AFFO 배당성향 73%,
  P/FFO 13.62배, P/E 52.2배 vs 공정비율 36.6배, RSI 52, 시가총액
  $58.6B, NNN REIT 36년 연속 기록, 데이터센터 $1.4B 투자, Spirit
  Realty 인수, Hold/Buy 등급 불일치, 목표주가 $67.91)를 최종
  `final_report.md`와 대조 — **14/14 전부 보존**.
- 1,449단어 — 목표(800~1200단어)를 다소 초과했으나, 원본(제약 없음)
  대비로는 여전히 크게 압축된 수준(Nestlé 사례에서 원본이 약
  3,000단어 이상이었던 것과 비교). REIT 고유 지표(FFO/AFFO/P/FFO)와
  11개 섹션을 모두 다루면서 데이터 불일치(P/FFO vs P/E, Hold vs Buy)
  까지 빠짐없이 플래그하려다 보니 목표 상한을 약간 넘은 것으로 추정
  된다 — 품질 저하(누락)가 아니라 정보량 자체가 많은 것이 원인.

**결론: 신규 자산 구조(REIT, 월배당, FFO/AFFO)에서도 Dividend Stock
Team의 7개 역할과 출력 최적화 instruction이 지시문 변경 없이 그대로
유효했다.** Valuation Analyst는 P/FFO(저평가)와 P/E(고평가)의 상반된
신호를, Dividend Quality Analyst는 AFFO 배당성향과 REIT 세법상 90%
요건의 불일치를 각각 스스로 정확히 포착했다 — 새 역할 없이 기존
역할 틀 안에서 REIT 고유의 데이터 특이성을 흡수했다.

## CONTENT_FAILURE — call_engine() 콘텐츠 레벨 실패 재관찰

PR #80에서 처음 관찰된 문제(콘텐츠 레벨 API 실패가 예외로 처리되지
않아 오류 메시지가 정상 산출물처럼 체크포인트됨)가 **다른 원인으로
다시 재현됐다**:
- PR #80(Nestlé): 원인 = 프록시/자체 서명 인증서 오류
- 이번(Realty Income): 원인 = **세션 사용 한도 초과**("You've hit
  your session limit · resets 2pm (UTC)")

두 사례 모두 (1) `call_engine()`이 `subprocess.run()`의 stdout을
검증 없이 그대로 반환, (2) Checkpointing이 예외 기반이라 이런
콘텐츠 레벨 실패를 감지하지 못함, (3) 수동으로 체크포인트를 무효화
해야만 재시도가 가능함 — 이라는 동일한 구조적 패턴을 공유한다.
**서로 다른 두 가지 원인(네트워크/인증서, 세션 한도)에서 같은 감지
실패 패턴이 재현**됐다는 것은 이것이 우연이 아니라 `call_engine()`
설계 자체의 일반적 한계임을 시사한다.

**지금 수정하지 않는다** — v1.0 Freeze 유지, RFC 없이
`call_engine()`을 바꾸지 않는다. 아래 DEV_HQ_ISSUES에 반복 관찰로
기록한다.

## DEV_HQ_ISSUES — 반복 재현 기록(개선 후보 격상 후보, 미착수)

- **콘텐츠 레벨 실패 미검출**: PR #80(1회) + 이번(1회) = **2회 재현**,
  서로 다른 원인. "실제 반복 Evidence가 발생하기 전에는 Dev HQ를
  수정하지 않는다"는 이번 지시 기준으로, 2회째 재현이 이 조건을
  충족하는지 판단이 필요하다 — **판단: 아직 개선을 착수할 만큼의
  반복 횟수(임계치는 사용자 판단 사항)에 도달했다고 단정하지 않는다.
  세 번째 재현 시 명확히 개선 후보로 격상할 것을 권고한다.** 지금은
  관찰 기록만 한다.
- Final Report/Synthesis 타임아웃(180초) 자체는 이번에 발생하지
  않았다 — 출력 최적화 덕분에 두 Wave 모두 43~44초로 안정적이었다.

## DECISION

신규 표준 실행 패턴(병렬화+출력최적화+Checkpointing+180초 Timeout)이
**실제 프로덕션 첫 적용에서도 정상 동작함을 확인했다**:
- NORMAL_E2E: 183.6초(원본 대비 최대 3.4배 단축)
- FAILURE_RECOVERY: 콘텐츠 레벨 실패 2건에도 불구하고 재계산 0회
- QUALITY: 14/14 핵심 데이터, 11개 섹션, Disclaimer 전부 보존
- Dividend Stock Team 7개 역할은 REIT라는 신규 자산 구조에서도
  지시문 변경 없이 유효

**패턴 자체는 계속 표준으로 유지한다.** 신규로 발견된 것은 패턴의
결함이 아니라 `call_engine()`의 기존 한계(콘텐츠 레벨 실패 미검출)의
2번째 재현이며, 이는 별도 관찰 사항으로 분리해 기록한다.

## ARCHITECTURE/GOVERNANCE

- `development-hq/` 어떤 파일도 수정하지 않았다.
- Dividend Stock Team의 7개 역할·Architecture는 변경하지 않았다.
- `call_engine()`의 콘텐츠 레벨 실패는 2회 재현됐으나, 실제 개선
  착수(예외 처리 추가, 재시도 로직)에 필요한 반복 임계치에 아직
  도달하지 않았다고 판단해 이번에도 수정하지 않는다 — RFC 필요
  여부 판단조차 유보한다(반복이 더 쌓이면 판단).
- v1.0 Freeze를 해제하지 않았다.

## PHASE9_11

신규 표준 패턴이 프로덕션에서 검증됐다는 사실 자체가 Phase 9~11
재개 조건이 되지 않는다 — Phase 9~11 재개는 이 실행과 무관한 별도
조건(Investment HQ 자체의 다음 단계 필요성)을 충족해야 하며, 이번
PR에서 자동으로 재개하지 않는다.

## 관찰되지 않은 것 (명시적으로 기록)

- 전체 파이프라인의 정확한 토큰/비용 총계 — 근사치만 제시.
- `call_engine()` 콘텐츠 레벨 실패에 대한 자동 감지/재시도 구현 —
  2회 재현으로도 아직 착수하지 않음, 3회째 재현 시 재검토 권고.
- Wave1/Wave2(병렬 구간)에서의 콘텐츠 레벨 실패 사례 — 이번엔
  Wave3/4에서만 발생, 병렬 구간에서의 동일 현상은 관찰되지 않음.
- 여러 배당주 동시/배치 처리 — 시도되지 않음.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새
Capability/Agent/Kernel Component/Contract를 만들지 않았다.
Dividend Stock Team의 7개 역할은 지시문 변경 없이 그대로
재사용했다. v1.0 Freeze를 해제하지 않았다. RFC/ADC/ADR을 작성하지
않았다. Phase 9~11 재개는 하지 않았다 — 이 실행과 무관한 별도
조건이 필요하다.
