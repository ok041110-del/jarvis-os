# ETF Dogfooding Review 0001 — Stock/ETF 공통 요구사항 검증

## 문서 성격

이 문서는 첫 ETF Dogfooding(QQQ, `projects/etf-analysis-qqq/`) 결과를
Stock Team 4회 실행(`docs/research/STOCK-AGENT-SEPARATION-REVIEW-0001.md`)
과 비교해, ETF Team 승격 여부에 대한 최소한의 판단 재료를 정리한다. ETF
Team이나 Agent를 이 문서에서 설계하지 않는다.

## 범위

- `projects/etf-analysis-qqq/issues/0001-qqq-analysis/EVIDENCE.md`
- `docs/research/STOCK-AGENT-SEPARATION-REVIEW-0001.md`,
  `docs/research/STOCK-TEAM-DEFINITION-0001.md`(비교 대상)

---

# 1. 무엇을 했는가

Stock Team 4회 반복 검증 이후 첫 ETF(QQQ, Invesco QQQ Trust) 실제 분석을
project-local 코드(`projects/etf-analysis-qqq/agents.py`/`runner.py`,
Stock과 코드 공유 없음)로 실행했다. 7개 분석(Composition/Holdings/Cost/
Performance/Exposure/Distribution/Macro) → Bull/Bear → Synthesis →
Final Report, 총 11회 `call_engine()` 실제 호출을 수행하고 각 호출의
입력/출력/소요 시간을 `call_log.json`으로 계측했다. AAPL/NVDA/MSFT와
겹치는 상위 보유종목을 가진 QQQ를 선정해 Stock-ETF 간 Context 중복
가능성을 관찰하기 좋은 조건을 확보했다.

# 2. Stock과 무엇이 공통이었는가

- 9~11단계 파이프라인이 수동 개입 없이 완주되는 구조, Kernel/Registry/
  Scheduler 불필요, in-memory Context로 충분, Stop Trigger 미발동 —
  Stock 4회의 결론이 ETF 1회에서도 그대로 반복됐다.
- 데이터 불일치를 각 역할이 스스로 인정하는 패턴(보유종목 비중, 섹터
  비중, 추적오차 부재 등)이 ETF에서도 동일하게 나타났다.
- Bull/Bear/Synthesis/Final Report 4단계는 **구조적으로** Stock과 매우
  유사했다 — "N개 분석을 근거로 낙관/비관 사례 구성 → 사실합의/해석차/
  데이터불일치/미해결질문으로 종합"이라는 패턴, 그리고 "사실 자체의
  충돌은 없고 순수 해석차만 존재"라는 Synthesis 결론 유형(JPM에서
  최초 관찰)까지 재현됐다.
- 출력 언어 비결정성(단일 실행 내 언어 혼재)이 5번째 실행에서도
  계속됨 — MSFT 이후 두 번째 혼재 사례.

# 3. ETF 고유 요구사항은 무엇이었는가

- Stock의 5개 분석 역할(Fundamental/Technical/Industry/News-Event/
  Sentiment)을 그대로 재사용하지 않았다 — 개념적으로만 부분 대응되고
  (Performance≈Technical, Exposure≈Industry), 실제로는 처음부터 새로
  작성했다.
- **3개 역할이 Stock에 대응 항목 자체가 없었다**: Composition/Index
  Analyst(추적지수·가중방법론), Cost/Tracking Analyst(총보수·추적오차),
  Distribution Analyst(분배금 주기·추이) — 이들은 펀드라는 상품 구조
  자체에서 나오는 개념으로, 개별 주식 분석에는 대응 개념이 없다.
- Context 규모가 분석 축 수(5→7)에 비례해 커졌고, Final Report 소요
  시간이 입력 증가폭(1.3배)보다 큰 폭(2.6배, 50.9초→133.5초)으로
  늘었다 — 아직 문제는 아니지만 향후 분석 축이 더 늘어나는 경우를
  대비한 관찰로 기록.

# 4. 공통 Capability가 실제로 필요한가

**아니다, 이번 실행 기준으로는.** Bull/Bear/Synthesis/Report 4단계의
구조적 유사성은 관찰됐지만:

1. ETF Dogfooding은 아직 1회뿐이다 — Stock Team이 승격 전 3회 반복을
   근거로 삼았던 것과 같은 기준으로 보면, ETF는 반복성 자체가 없다.
2. 실제 코드/Capability 공유는 시도되지 않았다(project-local 원칙
   유지) — 구조적 유사성 관찰과 실제 공유 필요는 다른 질문이다.
3. Stock의 5개 분석은 ETF에서 재사용되지 않았고, ETF는 3개의 완전히
   새로운 역할을 필요로 했다 — 이는 공유보다 도메인 특화 쪽에 더 가까운
   증거다.

Bull/Bear/Synthesis/Report의 구조적 유사성은 향후 재평가 후보로만
기록한다(ETF Dogfooding이 추가로 반복되고 그 유사성이 재확인될 때).

# 5. Phase 7/11/12에 실제 압력이 발생했는가

아니다. 이번 실행에서 관찰된 어떤 사실도 Kernel/Registry/Scheduler
확장, Runtime, Prompt Cache, Engine Gateway, 병렬 실행 인프라를 실제로
요구하지 않았다:

- Cache 필요성 — 발생하지 않음(동일 Prompt/데이터 반복 호출 없음).
- 병렬 실행 필요성 — **불필요 확인이 아니라 애초에 검증하지 않음**
  (여러 ETF·구성종목 처리를 이번 범위에서 시도하지 않았다). 이 차이를
  숨기지 않고 그대로 기록한다.
- 정기 데이터 갱신/Automation 필요성 — 발생하지 않음(1회성 수동 수집
  으로 충분했다). "분기별 리밸런싱" 같은 ETF의 개념적 특성이 향후
  자동 갱신 필요와 연결될 가능성은 있으나, 이번 실행에서 실제로
  발생한 압력은 아니다.
- Final Report 소요 시간 증가(133.5초, `call_engine` timeout 180초
  대비 아직 여유 있음)는 추세로만 기록하며, 지금 Runtime/Timeout 조정이
  필요하다는 근거로 쓰지 않는다.

# 6. ETF Team 승격 판단

**판단하지 않는다 — 판단할 근거가 아직 부족하다.** Stock Team은 3회
반복(AAPL/NVDA/MSFT) 후 승격을 검토했다. ETF는 이번이 1회차이며, 사용자
지시 자체도 "ETF Team이나 Agent를 선행 설계하지 않는다"고 명시했다.
이번 실행이 보여주는 것은:

- ETF도 Stock과 동일한 **Development HQ 패턴**(project-local
  Capability 함수 + `call_engine` 단일 호출 + 하드코딩된 순차 실행)이
  변경 없이 작동한다는 사실 — 이는 Team 승격과 무관하게 이미 확인된
  Platform 재사용성의 연장선이다.
- ETF Team 승격을 판단하려면 Stock과 동일한 반복 기준(최소 2회 이상의
  서로 다른 ETF 실행)이 필요하다 — 이번 1회 실행만으로는 시기상조다.

# 7. 다음 작업

- ETF Dogfooding을 최소 1회 이상 추가 실행해(다른 성격의 ETF — 예:
  채권형, 배당형, 좁은 섹터형 등) 이번 QQQ 결과가 반복되는지 확인.
- Bull/Bear/Synthesis/Report의 구조적 유사성이 ETF 2회 이상에서도
  유지되는지 관찰 — 유지되면 그때 공통 Capability 후보를 재검토.
- Final Report 소요 시간 증가 추세를 계속 관찰(분석 축이 더 늘어나는
  경우 `call_engine` timeout 여유가 줄어들 수 있음 — 지금은 문제
  아님).
- 병렬 실행 필요성은 여러 ETF/구성종목을 실제로 처리해야 하는 상황이
  생길 때 재검증(지금 인위적으로 만들지 않음).
- Stock Team과 마찬가지로 ETF Team 승격 여부는 사용자 판단에 맡긴다.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새 Agent, 새
Kernel Component, 새 Runtime, 새 Contract, 새 Cache를 만들지 않았다.
ETF Team/Agent를 선행 구현하지 않았다. Stop Trigger 미발동.
