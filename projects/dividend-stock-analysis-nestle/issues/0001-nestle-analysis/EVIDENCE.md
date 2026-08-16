# Evidence — Nestlé S.A. Dividend Stock Dogfooding (비미국 종목 경계 검증)

PRD v1.2 관찰 항목 기준, JNJ/KO/PG EVIDENCE.md와 동일한 형식. 이번
실행의 목적은 `docs/research/DIVIDEND-STOCK-TEAM-DEFINITION-0001.md`
재평가 조건("국제/신흥시장/리츠형 배당주 Dogfooding에서 이번 범위와
다르거나 겹치는 부분이 실제로 관찰될 때")을 검증하는 것 — Dividend
Stock Team의 7개 역할(Fundamental/Dividend Quality/Valuation/
Technical/Industry-Competition/News-Event/Sentiment)이 미국 상장·
USD·분기배당 종목(JNJ/KO/PG)이 아닌 스위스 1차 상장·CHF/USD 이중
통화·연 1회 배당·35% 원천징수세 구조의 Nestlé S.A.에서도 그대로
유효한지를 확인하는 것이다.

## 업무 (Task) — 인프라 수준 실패, 6회 시도 끝에 완주

- 11단계 파이프라인(7개 분석 → Bull/Bear → Synthesis → Final Report)
  중 **앞 10단계는 매 시도마다 전부 성공**했으나, **Final Report
  호출이 5회 연속(전체 파이프라인 재실행 기준) 동일 지점에서
  `ENGINE_TIMEOUT_SECONDS`(180초) 초과로 실패**했다.
- UUP(PR #73)에서 관찰된 타임아웃은 **1회 발생 후 재실행 1회로 즉시
  해결**(2차 시도 174.1초, 180초 이내)됐던 것과 달리, 이번 Final
  Report는 **재현율이 뚜렷이 높다**:
  1. 전체 파이프라인 재실행 1~5차 — 전부 Final Report 단계에서
     `subprocess.TimeoutExpired`(180초)
  2. 매 재시도가 앞 10단계를 처음부터 다시 실행하는 비효율을 피하기
     위해, 5차 시도의 트레이스백에 그대로 보존돼 있던 완성된 10개
     분석 결과(raw text)를 재사용해 Final Report 호출만 별도로
     재시도(`retry_final_report.py`, 여전히 `call_engine()`을 통해
     180초 제한 적용) — 6차 시도도 동일하게 180초 초과
  3. **진단 목적으로**(Dev HQ 파일은 수정하지 않음) 동일한 프롬프트를
     `call_engine()`을 거치지 않고 `claude -p`를 직접 180초보다 긴
     수동 wrapper(400초)로 호출 — **324.2초 만에 실제로 성공**
     (출력 25,072자)
- **결론: 이 Final Report 호출은 인프라 플레이키(flaky)가 아니라,
  180초 제한보다 실제로 더 오래 걸리는 콘텐츠였다.** JNJ의 Final
  Report(입력 46,243자, 출력 17,370자)는 67.6초로 완주했는데, Nestlé
  Final Report는 입력 크기(47,445자)가 JNJ와 비슷함에도 출력이
  25,072자로 JNJ보다 44% 크고 소요시간은 324.2초로 JNJ의 약 4.8배다
  — **입력 크기가 아니라 출력 길이(모델이 생성하기로 선택한 응답의
  분량)가 소요시간을 지배한다**는 UUP EVIDENCE.md의 가설과 일치하되,
  이번에는 그 격차가 180초 경계를 실제로 넘어설 만큼 컸다.
- `call_log.json`은 표준 형식으로 기록되지 못했다 — `runner.py`가
  11단계 전부 성공해야만 `call_log.json`을 한 번에 기록하는 구조라,
  앞 10단계(5회 반복 성공한)의 실측 input/output/elapsed가 유실됐다.
  이는 JNJ/KO/PG/UUP 어디에서도 관찰되지 않은 새로운 구조적 한계다
  (그 실행들은 전부 완주했기 때문에 처음 드러나지 않았을 뿐). 상세는
  `call_log.json`의 `timing_data_loss` 필드 참조.

## Dev HQ 관점의 관찰(수정하지 않음, 개선 후보로 격상)

- UUP EVIDENCE.md는 1회 관찰만으로는 `ENGINE_TIMEOUT_SECONDS`를
  수정하지 않되 "반복 관찰 시 개선 후보로 격상한다"고 명시했다. 이번
  실행이 바로 그 반복 관찰이다 — **UUP(1회, 재시도로 즉시 해결) →
  Nestlé(5~6회 연속 재현, 180초보다 실제로 오래 걸리는 콘텐츠로 확인)**
  로 재현 빈도와 확실성이 모두 높아졌다.
- 원인은 project-local 데이터/역할 지시문의 문제가 아니라
  `development-hq/mvp/engine.py`의 고정 타임아웃 상수
  (`ENGINE_TIMEOUT_SECONDS = 180`)가, 파이프라인 뒤로 갈수록
  누적되는 입력(Final Report가 10개 산출물 전체를 받음)과 결합할 때
  특정 콘텐츠에서 실제로 부족해질 수 있다는 것이다.
- **추가 구조적 관찰(신규)**: `runner.py`가 전체 11단계 성공 후에만
  결과를 디스크에 쓰는 all-or-nothing 구조이기 때문에, 마지막
  단계 하나가 반복 실패하면 이미 성공한 10단계의 산출물과 타이밍
  데이터가 통째로 유실된다. 이번에는 트레이스백에 우연히 프롬프트
  전문이 남아있어 복구 가능했으나, 이는 project-local 스크립트의
  우연한 동작이지 보장된 것이 아니다.
- **이것은 Dev HQ 개선 후보로 보고하되, 지금 수정하지 않는다** — v1.0
  Freeze 유지, RFC 없이 `ENGINE_TIMEOUT_SECONDS` 상향이나 `runner.py`
  류의 중간 결과 저장(체크포인팅) 구조를 도입하지 않는다. Invest HQ
  자체 문제(비미국 종목에서 7개 역할의 적합성)와는 명확히 분리한다 —
  아래에서 보듯 역할 구조 자체는 전혀 깨지지 않았다.

## Dividend Stock Team 7개 역할 — 비미국 종목에서도 유효한가

**그렇다, 7/7 역할 전부 유효했다.** 지시문을 JNJ/KO/PG와 한 글자도
바꾸지 않은 채 실행했고, 비미국 시장 구조(통화 이중화·연 1회 배당·
원천징수세)가 만든 데이터 특이성을 각 역할이 스스로 정확히 짚어냈다:

- **Fundamental**: GAAP 순이익 -31.4% vs 조정 순이익 -2.4%(불변환율
  +3.4%)라는, JNJ의 GAAP/조정 EPS 괴리(22%차)보다 훨씬 큰 방향성
  자체의 불일치를 스스로 지적 — "헤드라인 수치와 조정 수치의 괴리
  인정" 패턴이 6번째로 재현(Stock 4 + JNJ)됐을 뿐 아니라, 이번엔
  두 수치가 반대 방향(악화 vs 개선)이라는 더 극단적인 사례.
- **Dividend Quality**: **연 1회 배당**이라는 raw_data의 구조 자체를
  "지급 주기 리스크"로 명시적으로 다뤘고, 배당성향 86.9%(JNJ
  46.19%보다 훨씬 높음)의 산정 기준(GAAP/조정)이 자료에 없다는 공백을
  Fundamental의 GAAP/조정 순이익 불일치와 연결지어 "이 두 자료가
  서로를 검증하지 못한다"고 스스로 지적 — 다른 배당주에 없던 새로운
  유형의 교차 분석.
- **Valuation**: raw_data가 그대로 노출한 통화/시점 혼재(DCF 공정가치
  $113.62 vs $179.01, 기준 현재가 $77.76 vs $102)를 "재구성 불가능한
  데이터"로 명확히 플래그하고, 유일하게 신뢰 가능한 수치(업종 대비
  Forward P/E)만으로 제한된 결론을 냄 — JNJ의 "valuation tug of war"
  (방법론 간 상반)과는 다른 유형("소스 자체의 통화/기준 불일치")의
  결함 포착.
- **Technical**: 단기/중기 이동평균(매수) vs 장기 이동평균(매도)의
  방향 불일치, CHF/USD 가격 표시 혼재를 스스로 지적 — JNJ(RSI 수치
  자체의 불일치)와는 다른 각도의 자기인정.
- **Industry-Competition**: 시가총액 소스 간 1.5배 차이($258.56B vs
  $385B)를 원인 불명으로 명시하면서도 경쟁 구도(Unilever 매출 규모,
  Danone 시가총액) 서술은 유지 — 데이터 결함과 정성적 분석을 분리하는
  능력이 비미국 종목에서도 재현.
- **News/Event**: CEO 전격 해임·16,000명 감원이라는 지배구조 이벤트를
  다뤘고, 이것이 Fundamental의 순이익 급감과 직접적 인과관계로
  연결되는지는 자료에 없다고 스스로 명시 — JNJ의 탈크 소송(재무 영향
  불명)과 동일한 구조의 자기인정.
- **Sentiment**: 동일 기관의 등급이 시점에 따라 Hold(2025-08)→
  Buy(2026-08)로 바뀐 것을 스스로 포착 — JNJ의 "목표주가가 현재가를
  하회"와는 다른 유형("등급 자체가 시간에 따라 바뀜")의 이상치.

**결론: Dividend Stock Team의 7개 역할은 미국 상장 종목(JNJ/KO/PG)
뿐 아니라 국가/거래소/통화/배당주기/세제가 전부 다른 비미국 종목
(Nestlé)에서도 지시문 변경 없이 그대로 유효했다.** 각 역할이 비미국
시장 특유의 데이터 왜곡(통화 이중 표시, 연 1회 배당, 시가총액 소스
불일치)을 새로운 역할 없이 기존 역할의 틀 안에서 정확히 흡수했다 —
Composition Analyst류의 새 역할이 필요했던 ETF Team의 사례와 다르게,
Dividend Stock Team은 애초에 Stock Team 확장이라는 성격상 "종목 자체를
보는 방식"은 국가와 무관하게 동일했다.

## 새로운 역할/정보 구조가 실제로 필요한가

**아니다, 필요가 관찰되지 않았다.** 통화 환산(CHF↔USD), 스위스
원천징수세율(35%→15%) 조정, 연 1회 배당의 재투자 스케줄 같은 비미국
시장 고유 정보는, raw_data.md의 "데이터 한계" 섹션에서 이미 명시적
공백으로 처리됐고, 각 담당 Analyst(Dividend Quality/Valuation/
Technical)가 그 공백을 자기 역할 안에서 스스로 지적했다. **"통화/세금
전문 Analyst"라는 새 역할을 요구하는 신호는 나타나지 않았다** — 기존
7개 역할이 "이 데이터는 통화/세금 문제로 비교 불가능하다"는 판단까지
포함해서 충분히 수행했다.

## Bull/Bear/Synthesis 구조 재검증

- Synthesis가 이번에도 "사실 충돌보다 해석/가중치 차이"를 명시(6회
  연속: JPM→QQQ→SCHD→AGG→JNJ→UUP→Nestlé는 실제로는 7회째지만, ETF와
  Dividend Stock을 합산한 누적 기준). Bull/Bear가 갈리는 지점: GAAP
  순이익 급감을 "일회성 구조조정 비용"(Bull)으로 볼지 "구조적
  악화 신호"(Bear)로 볼지 — 다른 배당주들과 동일한 "같은 사실, 반대
  해석" 패턴.
- **새로운 유형의 교차 검증**: 시가총액 불일치($258.56B/$385B)를
  "양쪽 모두의 동종업계 비교를 동일하게 약화시키는 결함"이라고 Bear
  Case가 스스로 인정 — 자기 진영에 유리하게 쓰지 않고 중립적 결함으로
  처리한 첫 사례(JNJ/UUP 등에서는 각 진영이 결함을 자기 논리 보강에
  활용하는 경우가 많았음).

## Context/실행시간/Cache/Runtime 요구

- Context 규모: Final Report 입력 47,445자 — JNJ(46,243자)와 유사한
  규모.
- 앞 10단계 개별 timing은 유실(위 참조). Final Report만 실측:
  324.2초(claude -p 직접 호출, 180초 제한 우회) — 12건 누적 Dogfooding
  중 최대치.
- Cache: 발생하지 않음.
- 병렬 실행: 발생하지 않음 — 미검증 상태 유지.
- Runtime/Automation: **이번 실행 자체가 "Final Report 실패 시 자동
  재시도"라는 Runtime 성격의 필요를 UUP보다 훨씬 강하게 시사한다** —
  automation-candidate-watch 기준으로 관찰 기록(아래 참조), 지금
  Runtime을 만들지 않는다.

## 시스템 (System)

- Stop Trigger 미발동. Kernel/Registry/Scheduler 확장 불필요함이
  비미국 종목에서도 재확인됐다.
- 출력 언어: Sentiment 1개가 전체 한국어, 나머지 9개는 순수 영어 —
  13회 누적(Stock 4 + ETF 6 + Dividend Stock 3) 기준으로도 언어 패턴은
  여전히 비결정적.

## automation-candidate-watch 기록 (Dev HQ, 관찰만)

- **반복 작업**: "파이프라인 재실행"이 UUP 1회, Nestlé 5~6회로
  누적 6~7회 관찰됐다. 특히 Nestlé에서는 동일 지점(Final Report)의
  반복 실패가 명확한 패턴으로 재현됐다 — 자동 재시도(exponential
  backoff 또는 마지막 성공 단계부터 재개하는 체크포인팅) 도입이
  검토할 만한 개선 후보다.
- **지금 만들지 않는 이유**: v1.0 Freeze, RFC 없는 Dev HQ 수정 금지
  원칙에 따라 이번 실행에서 구현하지 않는다. 이 문단 자체가 관찰
  보고이며, 실제 개선은 별도 RFC → ADC → ADR 절차를 거쳐야 한다.

## Dividend Stock Team 비미국 종목 경계 검증 — 최종 판정

`DIVIDEND-STOCK-TEAM-DEFINITION-0001.md` 재평가 조건 중 "국제/신흥시장/
리츠형 배당주 Dogfooding에서 이번 범위와 다르거나 겹치는 부분이 실제로
관찰될 때"가 이번 실행으로 검증됐다. 결과: **7개 역할은 비미국 종목
(국가/거래소/통화/배당주기/세제가 전부 다른 Nestlé)에서도 이름·개수·
지시문 변경 없이 전부 유효했다.** 단순 국가 차이(통화 표시, 배당주기,
원천징수세)는 각 기존 역할이 데이터 결함/공백으로 흡수했고, Team의
구조적 한계로 이어지지 않았다. **`DIVIDEND-STOCK-TEAM-DEFINITION-0001.md`
의 업무 범위를 변경하지 않는다 — 재평가 조건이 "기존 정의 재확인"으로
종결된다.**

다만 이번 실행에서 Invest HQ 문제와 명확히 분리되는 **Dev HQ 개선
후보**(Final Report 180초 타임아웃의 반복 재현, `runner.py`의
all-or-nothing 저장 구조로 인한 중간 산출물 유실 위험)가 새로 확인됐고,
위 automation-candidate-watch 항목으로 기록했다.

## 관찰되지 않은 것 (명시적으로 기록)

- 여러 배당주의 동시/배치 처리 — 시도되지 않음.
- 통화/세금 전문 Analyst 신설 필요성 — 나타나지 않음(위 참조).
- Dev HQ 개선(타임아웃 상향, 체크포인팅)의 실제 시행 — 이번 실행
  범위 밖(관찰·보고만).

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다(진단용
`claude -p` 직접 호출은 `development-hq/mvp/engine.py`를 거치지
않고 Bash에서 동일 인자로만 재현한 것이며, 그 파일 자체를 수정하지
않았다). 새 Capability, 새 Agent, 새 Kernel Component, 새 Contract를
만들지 않았다. `DIVIDEND-STOCK-TEAM-DEFINITION-0001.md`도 수정하지
않았다(위 판정에 따라 변경 불필요 — 재평가 조건 검증 결과만 이
EVIDENCE.md에 기록). Governance/Boundary 판단 변경이 필요한 지점은
발견되지 않았다.
