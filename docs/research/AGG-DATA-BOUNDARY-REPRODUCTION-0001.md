# AGG Data Boundary Reproduction 0001 — "Engine 데이터 범위 이탈" 재현 검토

## 문서 성격

이 문서는 `projects/etf-analysis-agg/issues/0001-agg-analysis/EVIDENCE.md`
(§"새로운 요구사항")와 `docs/research/ETF-DOGFOODING-REVIEW-0003.md`,
`docs/research/ETF-TEAM-DEFINITION-0001.md`가 공통으로 인용해 온 "Engine의
데이터 범위 이탈" 관찰을, 동일 조건으로 실제 재현을 시도해 검증한
Governance Review 성격의 기록이다. **문제를 발견해도 임의로 수정하지
않는다** — `projects/etf-analysis-agg/`의 어떤 기존 파일도 수정하지
않았고, 재현에 쓴 코드는 이 문서 옆의 `agg-boundary-repro/`에 결과만
남겼다.

## Problem (기존 관찰이 주장한 것)

`EVIDENCE.md`(line 96-111, 요약):

> Performance/Risk Analyst 호출은 AGG의 `[PERFORMANCE_RISK]` 섹션만
> 입력으로 받았는데(**SCHD의 구체적 수치는 포함되지 않음**), 산출물에
> "the same source set reports SCHD's annualized volatility at 11.10%"
> 라는 문장이 나타났다. 이 수치는 실제 SCHD EVIDENCE.md의 정확한
> 값이지만, **AGG 실행의 이번 호출에 전달된 데이터에는 없었다** —
> Data Limitation Notice("주어진 데이터만 사용")를 실제로 위반한 사례.

이 관찰은 Engine이 (a) 사전 학습 지식에서 SCHD 수치를 회상했거나, (b)
세션 간 맥락이 섞였을 가능성을 시사한다고 결론지었고, 이는 이후
`ETF-DOGFOODING-REVIEW-0003.md`와 `ETF-TEAM-DEFINITION-0001.md`에
"Capability 개선 후보"(재평가 조건: 반복 관찰 시 지시문 개선 검토)로
그대로 인용되어 왔다.

## Evidence (실제 재현 결과)

### 1. 입력 데이터 자체를 재확인

`projects/etf-analysis-agg/issues/0001-agg-analysis/raw_data.md`의
`[PERFORMANCE_RISK]` 섹션(61~78행)을 그대로 읽으면:

```
- QQQ(변동성 정성적 서술만 존재)·SCHD(연환산 변동성 11.10%, 베타
  0.56)와 달리, AGG는 **듀레이션이라는 채권 고유의 정량적 금리
  민감도 지표**를 제공함 — 이는 Stock/주식형 ETF 어디에도 없던 지표
```

즉 **"SCHD 연환산 변동성 11.10%"라는 문구는 AGG의 `[PERFORMANCE_RISK]`
섹션 안에 원래부터 포함되어 있었다.** `runner.py`의 `_extract_section()`은
`## [PERFORMANCE_RISK]`부터 다음 `## ` 헤더 직전까지를 통째로 추출하므로,
이 SCHD 비교 문구는 실제로 Performance/Risk Analyst 호출의 입력에
**포함되어 전달됐다.**

이 raw_data.md는 `git log`상 단일 커밋(`b7cc96c`, MVP-ETF-0003 PR #57)에서
작성됐다 — `EVIDENCE.md`와 같은 PR의 같은 커밋이다. 즉 이후에 누군가
데이터를 추가한 것이 아니라, 애초에 "전달되지 않았다"는 `EVIDENCE.md`의
서술 자체가 raw_data.md의 실제 내용과 어긋난다.

### 2. 동일 조건 재현 실행 (2회, 이번 세션이 실제 `call_engine()`으로 실행)

`agents.py`의 `performance_risk_analyst_performance_risk_analysis()`를
원본과 동일한 입력(`[PERFORMANCE_RISK]` 섹션 + 데이터 한계 문구, Fund
Header 포함)으로 2회 재실행했다(`docs/research/agg-boundary-repro/agg_perf_risk_repro_{1,2}.md`).

| 실행 | 소요 | 출력에 "SCHD" 등장 | 출력에 "11.10%" 등장 |
|---|---|---|---|
| 1회 | 32.9초 | 예(비교 각주 형태) | **아니오** |
| 2회 | 24.9초 | 예(비교 각주 형태) | **아니오** |

두 재현 실행 모두 SCHD를 **입력에 있는 그대로**(추적오차 부재의 비교
대상, macro 서술의 출처 비교) 인용했을 뿐, `EVIDENCE.md`가 인용한
"SCHD's annualized volatility at 11.10%"라는 구체적 조합을 재생산하지
않았다. 즉 이번 2회 재현에서는 **입력 범위를 벗어난 내용이 관찰되지
않았다** — 입력에 있던 SCHD 관련 문구를 적절히 인용했을 뿐이다.

## Boundary (책임 경계 식별)

`EVIDENCE.md`가 지목한 책임 경계는 **Execution(Engine 호출)**이었다 —
"Engine이 제공된 데이터 범위를 벗어났다"는 서술은 Execution 단계의
Contract 위반으로 분류된 것이다.

그러나 이번 재확인 결과, 실제 책임 경계는 다르다:

- **Data Source / External Boundary**: 문제 없음. SCHD 11.10%는 실제
  SCHD 자료(`etf-analysis-schd`)에서 온 정확한 수치이며, 외부 데이터
  자체의 오류가 아니다.
- **Acquisition(raw_data.md 작성) — 실제 책임 경계**: AGG의
  `[PERFORMANCE_RISK]` 섹션을 작성할 때 "AGG는 QQQ/SCHD와 다른 지표
  유형을 제공한다"는 **비교 맥락**을 설명하려는 의도로 SCHD의 구체적
  수치를 섹션 안에 직접 인용해 넣었다. 이 시점에 "이 섹션은 AGG 전용
  섹션이며 다른 자산의 구체적 수치를 포함해서는 안 된다"는 경계가
  지켜지지 않았다 — Acquisition 단계에서 이미 경계가 넘어갔다.
- **Workflow(섹션 추출 메커니즘) — 2차 책임 경계**: `_extract_section()`은
  `## [TAG]` 헤더 단위로만 텍스트를 자르며, 그 안에 다른 자산의 식별자·
  수치가 섞여 있는지는 검사하지 않는다. 즉 Workflow의 데이터 전달 경계는
  "토픽 태그" 기준이지 "자산 정체성" 기준이 아니다 — Acquisition의 실수를
  걸러낼 장치가 Workflow에도 없다.
- **Execution(Engine 호출) — 이번 재현에서는 문제 없음**: 2회 재현
  모두 Engine은 입력에 실제로 주어진 내용만 사용했다. `EVIDENCE.md`가
  Execution 문제로 분류한 것은, Acquisition 단계에서 이미 섞여 들어간
  데이터를 Engine이 (당연히) 그대로 사용한 것을 "범위 이탈"로
  오분류했을 가능성이 높다.

## Recommendation (수정하지 않고 기록만)

이번 작업 지침("문제를 임의로 수정하지 말 것")에 따라 다음을 **제안만**
하고 실행하지 않는다.

1. `EVIDENCE.md`/`ETF-DOGFOODING-REVIEW-0003.md`/`ETF-TEAM-DEFINITION-0001.md`가
   인용해 온 "Engine의 데이터 범위 이탈" 관찰은, 이번 재현 결과에 비추어
   **재평가가 필요하다** — Execution 결함이 아니라 Acquisition 단계에서
   비교 대상 자산의 구체적 수치를 섹션 안에 직접 기입한 관행의 결과일
   가능성이 높다. 이 재평가는 이 문서의 권한 밖이며(기존 문서를 임의로
   재작성하지 않는다는 원칙), 별도 절차(문서 소유자 또는 사용자 판단)로
   넘긴다.
2. 재현 표본이 2회뿐이므로, "Execution 문제가 아니다"를 완전히 확정하는
   것도 아니다 — 이번 재현 조건(원본과 동일한 입력)에서는 재현되지
   않았다는 사실만 기록한다.
3. Capability 지시문(Data Limitation Notice)을 지금 수정하지 않는다 —
   원래 관찰 자체의 원인 소재가 Execution이 아닐 가능성이 높아졌으므로,
   Execution 쪽 지시문을 고치는 것은 오히려 잘못된 지점을 수정하는
   결과가 될 수 있다.
4. project-local raw_data.md를 작성할 때 "이 섹션은 대상 자산 전용이며
   다른 자산의 구체적 수치는 별도 비교 섹션으로 분리한다"는 관행을
   차기 Dogfooding(예: Dividend Stock 추가 실행)에서 시험적으로 지켜
   보는 것은 Development HQ Platform 변경이 아니라 project-local 작성
   관행의 문제이므로, 이 문서의 권한 밖에서(각 project 작성자 판단으로)
   자유롭게 시도 가능하다.

## Architecture/Contract 변경 여부

**없음.** `development-hq/`, `projects/etf-analysis-agg/`(기존 파일)
어느 것도 수정하지 않았다. 새 Capability/Agent/Kernel Component를 만들지
않았다. `docs/03_adc/ADC.md`도 이 문서로 수정하지 않는다(관련 ADC 항목
없음 — 이 발견은 ADC-02/09/10 어디와도 직접 연결되지 않는다,
`GOVERNANCE-REVIEW-0006` 참조).

---

## Follow-up (KO/PG Dividend Stock Dogfooding에서 추가 확인, 결론 유지)

KO(`projects/dividend-stock-analysis-ko/issues/0001-ko-analysis/EVIDENCE.md`
§"Data Boundary 재확인")·PG(`projects/dividend-stock-analysis-pg/issues/0001-pg-analysis/EVIDENCE.md`
§"Data Boundary 재확인")에서도 동일한 조건(비교 대상 자산의 수치를
의도적으로 섹션 안에 포함)으로 재현을 시도했다. 두 실행(11개 산출물씩,
총 22개) 전수 확인 결과 **새로운 이상 징후는 관찰되지 않았다** —
제공된 비교 수치는 매번 원래 그 정보가 제공된 섹션에서 파생된
산출물에만 정확히 국한됐다.

**결론 유지**: 이 발견을 Execution Layer violation으로 확정하지
않는다. Acquisition/Workflow 경계 가능성을 계속 유지한다(§Boundary
원 판단 그대로). 재현 표본은 이제 4건(AGG 원본 재실행 2회 + KO + PG)
으로 늘었으나 전부 "재현 안 됨" 방향이므로, 최초 관찰(AGG 1건)이
이례적이었을 가능성이 더 강해졌을 뿐 결론 자체는 바뀌지 않는다.

**기존 문서 직접 수정 여부 판단**: `projects/etf-analysis-agg/issues/0001-agg-analysis/EVIDENCE.md`,
`docs/research/ETF-DOGFOODING-REVIEW-0003.md`,
`docs/research/ETF-TEAM-DEFINITION-0001.md`는 **이번에도 직접 수정하지
않는다.** 이유:
1. 세 문서 모두 "특정 시점에 실제로 관찰된 것"을 기록한 point-in-time
   Evidence/확정 문서다 — 사후에 다른 세션의 재해석으로 원문을 고치는
   것은 이 저장소의 관행(예: `VALIDATION_REPORT.md`를 그대로 두는 것)
   과 어긋난다.
2. 특히 `ETF-TEAM-DEFINITION-0001.md`는 **이미 승격이 확정된 문서**다
   — 확정 문서를 다른 세션이 사후에 고치는 것은 그 문서가 대표하는
   사용자 결정 자체를 소급 수정하는 것과 같다.
3. 재분류 Evidence는 이미 별도의 발견 가능한 문서(이 문서 + 각 EVIDENCE.md
   의 "Data Boundary 재확인" 절)에 남아 있어, 향후 세션이 `docs/research/`
   를 훑으면 자연히 발견할 수 있다.

**대신 권고하는 것**: 다음에 ETF Team 관련 공식 Governance 문서(예:
ETF Team의 4번째 Dogfooding, 또는 별도 재평가)가 실제로 열릴 때, 그
문서가 이 재분류 Evidence를 인용해 "Capability 개선 후보"·"재평가
조건" 절을 갱신하는 것이 적절하다 — 지금 이 문서가 선제적으로 그
갱신을 대신하지 않는다.
