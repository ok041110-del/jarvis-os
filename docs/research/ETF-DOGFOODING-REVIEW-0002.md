# ETF Dogfooding Review 0002 — QQQ/SCHD 반복성 종합

## 문서 성격

이 문서는 두 번째 ETF Dogfooding(SCHD, `projects/etf-analysis-schd/`)
결과를 첫 번째 실행(QQQ, `docs/research/ETF-DOGFOODING-REVIEW-0001.md`)
과 비교해, ETF 업무 구조의 반복성을 재검증한다. ETF Team이나 Agent를
이 문서에서 설계하지 않는다.

## 범위

- `projects/etf-analysis-schd/issues/0001-schd-analysis/EVIDENCE.md`
- `docs/research/ETF-DOGFOODING-REVIEW-0001.md`(QQQ, 비교 대상)
- `docs/research/STOCK-AGENT-SEPARATION-REVIEW-0001.md`(Stock 비교
  대상)

---

# 1. QQQ와 무엇이 반복됐는가

- 11단계 파이프라인 완주(2/2), Kernel/Registry/Scheduler 불필요(2/2),
  in-memory Context 충분(2/2), Stop Trigger 미발동(2/2).
- 데이터 불일치 자기인정 패턴 — 보유종목/섹터/수익률 수치가 소스마다
  다르게 보도된 것을 각 역할이 스스로 명시(2/2).
- Bull/Bear/Synthesis 구조 — "동일 사실, 대립적 해석만 존재"라는
  Synthesis 결론 유형이 2/2 반복됐다(JPM Stock에서 최초 관찰된 유형이
  QQQ→SCHD로 이어져 **3회 연속** 재현 — Stock/ETF 도메인을 넘나드는
  반복).
- 11단계 파이프라인 전체 소요 시간이 두 실행에서 거의 동일했다(QQQ
  402.8초, SCHD 400.7초) — 개별 단계 편차와 무관하게 전체 소요는
  안정적이었다.

# 2. ETF 고유 역할이 반복됐는가

**그렇다, 확인됐다.** Composition/Index, Cost/Tracking, Distribution
3개 역할(QQQ 1회 실행에서는 "Stock에 대응 항목 없음"으로만 기록됐던
역할)이 SCHD(완전히 다른 성격의 펀드 — 배당/가치주 vs 기술 성장주)
에서도 동일한 역할 이름·함수 시그니처로 실제 유의미한 산출물을
만들어냈다. 다만 각 역할이 다루는 실제 내용(방법론, 비용 이슈,
배당수익률 불일치 패턴)은 ETF마다 완전히 달랐다 — "같은 역할이 다른
내용을 다룬다"는 것 자체가 실측으로 확인됐다.

이제 이 3개 역할은 2/2(QQQ, SCHD) 반복 근거를 가진다 — 1회 실행에서
1/1이었을 때보다 명확히 근거가 강화됐다.

# 3. Bull/Bear/Synthesis 구조가 반복됐는가

**그렇다.** Synthesis가 이번에도 "실제 사실 충돌 없음, 순수 해석 차이만
존재"로 결론 내렸다 — QQQ와 사실상 동일한 결론 유형이다. Bull/Bear가
갈리는 지점의 성격도 동일했다: 같은 수치(집중도, 변동성, 구조적 변화)를
두고 "우위"(Bull) vs "리스크"(Bear)로 정반대 해석하는 패턴이 QQQ에
이어 재현됐다.

**다만 구조적 유사성이 실제 코드 공유로 이어지지는 않았다** — SCHD의
`agents.py`도 QQQ의 어떤 함수도 import하지 않고 독립적으로 작성됐다.
2회 실행 모두 동일한 패턴을 "손으로 다시 썼다"는 뜻이지 "공유했다"는
뜻이 아니다.

# 4. 새로운 요구사항이 발생했는가

- **Reconstitution발 세금/분배 효과**(Cost Analyst가 SCHD에서 자발적
  으로 식별) — Stock/QQQ 어디에도 없던 하위 관찰이지만, 기존
  Cost/Tracking Analyst 역할 안에서 자연스럽게 처리됐다. 새 역할이나
  Capability를 요구하지 않는다.
- **교차 ETF Context 참조** — SCHD의 Macro Analyst가 QQQ의 Macro
  자료를 인지하고 정합성 미검증을 명시했다. 이는 이 세션이
  `raw_data.md` 작성 시 의도적으로 넣은 문구에 대한 반응이며, Capability
  가 스스로 다른 프로젝트 파일을 조회한 것이 아니다(Engine은 WebFetch/
  파일 접근이 차단됨). 새 Architecture 필요를 시사하지 않는다.
- **소요시간-입력크기 반비례 사례**: QQQ에서 관찰된 "Final Report
  소요시간이 입력보다 출력 길이와 더 강하게 연관된다"는 가설이 SCHD
  에서 강하게 뒷받침됐다 — SCHD의 Final Report 입력이 QQQ보다 컸음에도
  (51,306>41,567자) 출력은 더 작았고(14,803<19,709자) 소요시간도 더
  짧았다(60.3초<133.5초). Runtime/Timeout 조정이 필요하다는 근거는
  아니며, 관찰 기록으로만 남긴다.
- 그 외 새로운 역할/Capability 요구는 없었다 — 오히려 QQQ의 7개 역할
  분류가 성격이 다른 ETF에서도 변경 없이 충분했다는 것이 이번 실행의
  핵심 결론이다.

# 5. ETF Team 승격 판단

**아직 판단하지 않는다 — 다만 근거가 QQQ 1회 때보다 강화됐다.**
Stock Team은 3회 반복(AAPL/NVDA/MSFT) 후 승격을 검토했다. ETF는
이번이 2회차다:

- ETF 고유 7개 역할이 서로 다른 두 성격의 펀드(성장주/배당주)에서
  변경 없이 반복됐다 — 이는 Stock Team이 3사에서 반복성을 확인했던
  것과 같은 종류의 근거다.
- 다만 Stock Team의 승격 기준(3회 반복)에는 아직 미달한다(2/3).
  사용자 지시대로 ETF Team/Agent를 이번에도 선행 설계하지 않는다.
- 공통 Capability(Stock-ETF 간 실제 공유)는 여전히 관찰되지 않았다 —
  두 도메인은 서로 다른 분석 축을 필요로 한다는 결론이 유지된다.

**권고(결정 아님)**: 세 번째 ETF 실행(예: 채권형 ETF, 좁은 섹터 ETF
등 QQQ/SCHD와 또 다른 성격)이 이번과 같은 7개 역할 반복성을 재확인
하면, Stock Team과 동일한 기준(3회 반복)으로 ETF Team 승격을 검토할
근거가 충분해진다.

# 6. Phase 7/11/12 압력 여부

**발생하지 않았다.** 2회 ETF 실행 전체에서 Cache/Runtime/병렬 실행
인프라를 실제로 요구하는 사실은 없었다:

- Cache — 2/2 미발생(동일 Prompt/데이터 반복 없음).
- 병렬 실행 — 이번에 ETF가 2개(QQQ, SCHD)로 늘었지만, 두 실행은
  서로 다른 세션에서 순차 처리됐을 뿐 "여러 ETF의 동시/배치 처리"라는
  실제 업무는 발생하지 않았다. 사용자 지시대로 "실제 다중 ETF 업무가
  발생할 경우에만" 관찰하기로 했고, 그 조건 자체가 아직 충족되지
  않았다 — 병렬 실행 필요성은 계속 미검증 상태로 정직하게 남긴다.
- Runtime/Automation — 2/2 미발생. reconstitution/리밸런싱 주기라는
  개념은 두 ETF 모두에서 나타났지만, 실제 자동 갱신 필요는 발생하지
  않았다.

# 7. 다음 작업

- 세 번째 ETF(채권형/좁은 섹터형 등 QQQ·SCHD와 또 다른 성격)를
  추가 실행해 7개 역할의 반복성을 Stock Team과 동일한 3회 기준으로
  검증.
- Bull/Bear/Synthesis의 "순수 해석 차이" 패턴이 3회째(Stock 포함하면
  4회째)에도 유지되는지 계속 관찰.
- Final Report 소요시간-출력크기 상관 가설을 추가 실행에서 재검증.
- Stock-ETF 간 실제 Capability 공유 필요는 계속 미발생 상태 — 향후
  두 도메인을 동시에 다루는 실제 업무(예: 포트폴리오 단위 통합 분석)
  가 생길 때 재검증.
- ETF Team 승격 여부는 3회차 실행 이후 재검토, 최종 결정은 사용자
  판단에 맡긴다.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새 Agent, 새
Kernel Component, 새 Runtime, 새 Contract, 새 Cache를 만들지 않았다.
ETF Team/Agent를 선행 구현하지 않았다. Stop Trigger 미발동.
