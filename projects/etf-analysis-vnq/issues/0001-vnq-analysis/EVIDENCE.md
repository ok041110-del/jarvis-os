# Evidence — VNQ ETF Dogfooding (실행 1회차, ETF 다섯 번째, 리츠형) — 자산군 재평가 조건 "리츠" 항목 최초 검증

PRD v1.2 관찰 항목 기준, QQQ/SCHD/AGG/GLD EVIDENCE.md와 동일한 형식.
이번 실행의 목적은 `docs/research/ETF-TEAM-DEFINITION-0001.md`의
재평가 조건 중 GLD가 이미 다룬 "원자재"에 이어 **"리츠"** 항목을
검증하는 것이다. GLD와 동일하게 6개 역할 구조(Composition/Index,
Holdings/Exposure, Cost/Tracking, Performance/Risk, Distribution,
Macro)를 그대로 유지했다.

## 업무 (Task)

- 10단계 파이프라인(6개 분석 → Bull/Bear → Synthesis → Final Report)이
  수동 개입 없이 완주됐다.
- `call_log.json` 실측: 10회 호출 합계 400.9초 — QQQ(402.8초)와 거의
  동일, SCHD(400.7초)·AGG(331.5초)·GLD(339.8초) 범위 내. 개별 분석
  6건은 15.8~39.8초/건(입력 557~1,171자, 출력 1,896~4,054자)로
  GLD보다 다소 컸고, Final Report가 87.1초(입력 39,861자, 출력
  22,839자)로 5개 ETF 중 가장 컸다.

## ETF 고유 역할 5/5 반복 여부 — "소득 있는 실물자산"이라는 세 번째 유형

QQQ/SCHD(주식)·AGG(채권)·GLD(원자재)에 이어 VNQ(리츠)에서도 6개 역할이
전부 유효했다. GLD가 "지수/종목/소득 개념 자체가 없음"을 보여준
사례였다면, VNQ는 그 반대 방향 — "표준 프레임이 적용되긴 하지만 수치가
자산군 특유의 방식으로 해석되어야 하는" 사례였다:

- **Composition/Index Analyst**: MSCI US Investable Market Real Estate
  25/50 Index를 추종한다고 스스로 확인했고, "25/50"이라는 지수 방법론
  명칭이 집중도 상한 규칙을 시사한다는 것까지 추론했다 — 다만 구체적
  규칙 문구가 소스에 없다는 점도 명시. QQQ(가중방법론)·SCHD(스크리닝)·
  AGG(표본추출)·GLD(지수 없음)에 이어, VNQ는 "지수는 있지만 그 상세
  메커니즘은 이름으로만 알 수 있다"는 다섯 번째 패턴.
- **Holdings/Exposure Analyst**: 가장 뚜렷한 발견 — AGG(집중도 개념
  무의미)·GLD(종목 개념 자체 없음)와 달리, VNQ는 **집중도 개념이
  완전히 유효하고 실제로 높다**(160종목 중 상위 10개가 54.5%)고
  스스로 평가했다. "25/50 규칙이 있음에도 이 정도 집중도가 통상적
  수준인지 판단할 비교 데이터가 없다"는 것도 정직하게 인정 — 다섯
  ETF 중 처음으로 "집중도 지표가 그대로 적용되고, 수치도 산출됐지만,
  맥락(peer 비교)이 없어 해석은 유보"라는 세 번째 케이스가 나타났다.
- **Cost/Tracking Analyst**: 추적오차 수치 부재를 5/5 반복 확인.
  0.13% 총보수율(카테고리 평균 대비 74% 낮음)이라는 구체적 비교
  수치를 자체 제시.
- **Distribution Analyst**: GLD와 정확히 대조되는 지점 — VNQ는 "소득
  창출이 펀드 목표에 명시적으로 포함"되어 있음을 스스로 짚으며 GLD를
  직접 언급해 대조했다("This distinguishes it from a fund like GLD,
  which carries no income mandate at all"). 배당수익률 소스 간 불일치
  (3.96% vs 3.52%)는 QQQ~GLD까지 4/4 반복된 패턴과 동일하게 5/5로
  이어졌다.
- **Performance/Risk Analyst**: 베타(주식)·듀레이션(채권)·상품가격
  리스크(금) 어디에도 속하지 않는 **"금리 민감도를 가진 실물자산"**
  이라는 REIT 고유의 복합 리스크 성격을 스스로 명명했다 — 다만 이
  설명이 "일반적으로 알려진 REIT 자산군 지식"이지 VNQ 데이터에서
  직접 도출된 정량적 결과가 아니라는 것까지 스스로 구분해 명시한
  점이 새롭다(다른 ETF에서는 이 정도로 명시적인 지식-출처 구분이
  없었다).
- **Macro Analyst**: 금리·Cap Rate·신용/대출 환경·오피스 리스크 등
  리츠 고유의 거시 변수를 다뤘다 — "5~15bp Cap Rate 압축은 지지적"
  (Bull)과 "10년물 금리가 현 수준 유지 전망이라 압축 여력 제한적"
  (Bear)이 **동일 Macro 보고서 안의 서로 다른 문장**이라는 점을
  Synthesis가 정확히 짚어냈다.

**결론: ETF 고유 역할이 5/5(QQQ, SCHD, AGG, GLD, VNQ) 반복 확인됐다.**
GLD가 "역할의 전제(지수/종목/소득)가 없는 경우도 프레임이 깨지지
않는다"를 보여줬다면, VNQ는 "전제가 전부 유효하고 표준적으로 작동하는
경우"를 보여줘 — 5개 자산군(주식 2·채권·원자재·리츠)에 걸쳐 6개 역할
프레임이 양 극단(전제 없음 ↔ 전제 충족) 모두에서 흔들리지 않았다.

## Bull/Bear/Synthesis 구조 재검증 — 새로운 분류 체계 등장

- Synthesis가 이번에 처음으로 **"사실 자체의 충돌"과 "동일 사실의
  해석 차이"를 별도 섹션으로 명시적으로 구분**했다. 기존 4회
  (JPM/QQQ/SCHD/AGG/GLD)는 이 구분을 서술 안에서 암묵적으로만
  드러냈으나, VNQ Synthesis는 "Genuine factual conflicts"(YTD
  13.59% vs +14.67%, 배당수익률 3.96% vs 3.52%, 보유종목수 159 vs
  160, 최상위 종목 정체 불명)와 "Same facts, different
  interpretation"(25/50 방법론의 실효성, 99.45% 섹터 순수성의
  양면성, 5~15bp Cap Rate 압축의 크기 평가)을 구조적으로 분리했다 —
  Bull/Bear/Synthesis의 4단 구조(합의된 사실/해석차/데이터 불일치/
  미해결 질문, AAPL부터 관찰)가 5회 반복 속에서 스스로 더 정교해진
  사례.
- **원본 데이터 결함을 Bull/Bear/Synthesis 3개 역할 모두가 독립적으로
  지적**: YTD 수익률 불일치, 배당수익률 불일치, 보유종목수 불일치
  (159 vs 160), "Vanguard Real Estate II Index Fund" 14.36%라는
  정체불명 최상위 항목 — AGG(AA등급 모순)·GLD(YTD/종가 모순)에 이은
  세 번째 "여러 역할이 같은 데이터 결함을 각자 포착" 사례.

## Context 규모/실행시간 — QQQ/SCHD/AGG/GLD 대비 실측 비교

| 항목 | QQQ(7분석,11단계) | SCHD(7분석,11단계) | AGG(6분석,10단계) | GLD(6분석,10단계) | VNQ(6분석,10단계) |
|---|---|---|---|---|---|
| 단계 합계 | 402.8초 | 400.7초 | 331.5초 | 339.8초 | 400.9초 |
| Final Report 입력 | 41,567자 | 51,306자 | 40,657자 | 38,860자 | 39,861자 |
| Final Report 출력 | 19,709자 | 14,803자 | 16,943자 | 17,795자 | 22,839자 |
| Final Report 소요 | 133.5초 | 60.3초 | 67.3초 | 67.7초 | 87.1초 |

VNQ는 6분석/10단계로 AGG·GLD와 동일한 규모임에도 합계 소요시간
(400.9초)이 QQQ(402.8초)에 근접할 만큼 길었다 — Bear Case(64.1초)와
Final Report(87.1초, 5개 ETF 중 최장 출력 22,839자)가 특히 컸다.
데이터 소스 간 불일치 항목이 다른 ETF보다 많았던 것(YTD·수익률·
보유종목수·최상위종목 4건 동시 불일치)이 각 역할의 서술 분량을
늘렸을 가능성이 있으나, 이는 관찰이지 인과관계를 확정한 것은 아니다.

## 새로운 요구사항 — 실제 발생한 것만 기록

- **부분 언어 누출의 새로운 하위 유형 관찰**: `bull_case.md`(전체
  영어 문서)에 Macro Analyst 산출물(전체 한국어)의 문장이 번역 없이
  그대로 인용된 뒤 괄호로 영어 번역이 병기된 사례가 나타났다("공개
  시장에서 거래되는 리츠 주가는 연중 대체로 상승 흐름을 나타냈다"
  (publicly traded REIT prices broadly trended upward for the
  year)), 그 외 "우량"·"건전" 두 단어도 영어 문장 속에 따옴표와
  함께 그대로 남았다. JPM에서 관찰된 "발음 로마자 전사"와는 다른
  하위 유형(원문 그대로 인용 + 번역 병기)이며, 두 사례 모두 원본
  한국어 산출물을 다음 역할이 그대로 이어받아 처리하는 과정에서
  나타났다. 2회 관찰(JPM 로마자 전사형, VNQ 인용+번역형) — 여전히
  반복 관찰 기준에는 못 미치므로 지금 프롬프트를 수정하지 않고
  기존 Capability 개선 후보에 하위 항목으로 추가 기록.
- 새로운 역할/Capability 요구는 발생하지 않았다.

## Stock/타 ETF와 공통으로 사용할 수 있는 역할의 실제 반복 여부

여전히 없다. VNQ도 Stock의 5개 분석 역할이나 QQQ/SCHD/AGG/GLD의 역할
코드를 재사용하지 않았다(project-local 복제만 존재, 5/5 ETF 동일).

## Cache / 병렬 실행 / Runtime 필요성

- Cache: 5/5 미발생.
- 병렬 실행: 이번에도 단일 ETF 순차 실행만 발생 — 계속 미검증 상태로
  정직하게 기록한다.
- Runtime/Automation: 5/5 미발생.

## 시스템 (System)

- Stop Trigger 미발동. Kernel/Registry/Scheduler 확장 불필요함이 ETF
  다섯 번째 실행에서도 재확인됐다.
- **출력 언어**: 10개 산출물 중 Composition·Holdings/Exposure·Macro
  3개가 전체 한국어, Bull Case 1개가 영어 문서 안에 한국어 문장 부분
  인용, 나머지 6개는 순수 영어 — 9회 누적 기준으로도 언어 패턴은
  여전히 비결정적이다.

## ETF-TEAM-DEFINITION-0001 재평가 조건 판정

재평가 조건 "원자재/리츠/통화 등 다른 자산군"의 두 번째 항목("리츠")이
이번 실행으로 다뤄졌다(원자재는 GLD가 완료). 결과: **6개 역할 범위와
이름 모두 그대로 유지된 채, VNQ 고유의 수치(25/50 집중도 규칙,
Cap Rate, 분기 배당, 금리 민감도)를 정확히 소화했다.** GLD(전제 없음)
와 VNQ(전제 충족, 표준적 작동)라는 양극단 모두에서 프레임이 깨지지
않았다는 것은 6개 역할 정의의 강건성(robustness)을 추가로 뒷받침하는
Evidence다. **ETF-TEAM-DEFINITION-0001.md의 6개 역할 범위를 변경하지
않는다.** 재평가 조건의 "통화(currency)" 항목만 아직 미검증으로
남는다.

## 관찰되지 않은 것 (명시적으로 기록)

- 여러 ETF의 동시/배치 처리 — 5회 실행 모두 시도되지 않음.
- Stock-ETF 간 실제 Capability 공유 — 5회 실행 모두 관찰되지 않음.
- Cache/Runtime이 실제로 필요해지는 시점 — 5회 실행 모두 나타나지
  않음.
- 통화형(Currency) ETF — 재평가 조건의 마지막 미검증 항목으로 남는다.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새 Capability,
새 Agent, 새 Kernel Component, 새 Contract를 만들지 않았다.
`docs/research/ETF-TEAM-DEFINITION-0001.md`도 수정하지 않았다(위 판정에
따라 변경 불필요). Governance/Boundary 판단 변경이 필요한 지점은
발견되지 않았다.
