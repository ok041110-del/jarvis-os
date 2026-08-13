# ETF Dogfooding Review 0003 — QQQ/SCHD/AGG 3/3 반복성 확정 및 ETF Team 승격 판단

## 문서 성격

이 문서는 세 번째 ETF Dogfooding(AGG, 채권형)까지 완료한 시점에서
QQQ/SCHD/AGG 3건의 EVIDENCE.md를 종합해, Stock Team이 적용했던 것과
동일한 3회 반복 기준으로 ETF Team 승격 여부를 판단한다. Agent 이름·세부
Architecture는 확정하지 않는다.

## 범위

- `projects/etf-analysis-{qqq,schd,agg}/issues/*/EVIDENCE.md`
- `docs/research/ETF-DOGFOODING-REVIEW-{0001,0002}.md`(QQQ, QQQ/SCHD)
- `docs/research/STOCK-TEAM-DEFINITION-0001.md`,
  `docs/research/STOCK-AGENT-SEPARATION-REVIEW-0001.md`(Stock 비교 기준)

---

# 1. 무엇이 반복됐는가

3개 ETF(QQQ: 기술 성장주, SCHD: 배당 가치주, AGG: 채권형 — 자산군까지
포함해 성격이 서로 다름) 전체에서 3/3 반복 확인된 것:

- 파이프라인 완주(수동 개입 없음), Kernel/Registry/Scheduler 불필요,
  in-memory Context 충분, Stop Trigger 미발동.
- 데이터 불일치 자기인정 패턴(보유종목/섹터/배당수익률 수치가 소스마다
  다르게 보도된 것을 각 역할이 스스로 명시).
- Bull/Bear/Synthesis의 "사실 자체의 충돌 없음, 순수 해석 차이만 존재"
  결론 유형 — JPM(Stock)에서 시작해 QQQ→SCHD→AGG까지 **4회 연속**
  재현됐다. Stock 1건을 포함하면 도메인을 넘나드는 반복이며, 이 정도
  반복이면 이 패턴 자체는 이미 안정적인 것으로 취급할 수 있다.
- Cache/Runtime/Automation 필요성 3/3 미발생.

# 2. ETF 고유 역할이 3/3 반복됐는가

**그렇다.** QQQ에서 처음 식별된 "Stock에 대응 항목 없음" 역할군
(Composition/Index, Cost/Tracking, Distribution)이 SCHD에서 2/2로,
이번 AGG(채권형, 6개 역할로 재구성)에서 3/3으로 확인됐다. 특히 AGG는
역할의 **경계**(7개→6개, Holdings와 Exposure 통합, Performance와
Risk 통합)가 사용자 지시로 재구성됐음에도 그 안에서 다뤄지는 핵심
기능은 빠짐없이 필요했다 — 예를 들어 "종목 집중도"라는 QQQ/SCHD의
프레임이 AGG(13,224개 채권 분산)에는 무의미하다는 것을 Holdings/
Exposure Analyst가 스스로 인지하고 섹터·신용등급·만기 구조로 프레임을
전환했다. 이는 **역할의 정확한 경계(7개 vs 6개)는 자산군에 따라
달라질 수 있지만, 역할이 다루는 핵심 기능 자체는 3/3 안정적**이라는
것을 보여준다.

# 3. Bull/Bear/Synthesis가 반복됐는가

**그렇다, 3/3.** 추가로 AGG에서 새로운 강화 근거가 나왔다: AA 등급
비중(73.60%)이 AAA(2.21%)·Treasury(46.26%)와 모순되는 데이터 이상치를
Holdings/Exposure, Bull, Bear, Synthesis **4개 역할 모두**가 각자
독립적으로 포착했다 — 역할 분리가 동일한 데이터 문제를 여러 각도에서
교차 검증하는 데 실제로 기여한다는 근거다.

# 4. 새로운 요구사항

- **Engine이 제공된 데이터 범위를 벗어난 사례를 처음으로 실제 관찰함**
  (`projects/etf-analysis-agg/issues/0001-agg-analysis/EVIDENCE.md`
  참조): AGG의 Performance/Risk 분석 호출에 전달되지 않은 SCHD의
  실제 수치(11.10%)가 산출물에 등장했다 — 우연히 정확한 값이었지만,
  "제공된 데이터만 사용하라"는 Data Limitation Notice를 실제로
  위반한 사례다. Capability Contract 개선 후보로 하위 기록하며, 지금
  프롬프트를 수정하지 않는다(1회 관찰).
- Final Report 소요시간-출력크기 상관 가설이 3번째 데이터 포인트
  에서도 대체로 유지됐으나 완벽한 선형 관계는 아님을 확인 —
  10단계(AGG)로 줄어든 것 자체가 전체 소요시간 감소의 더 직접적인
  원인으로 보인다.
- 그 외 새로운 역할/Capability 요구는 없었다.

# 5. ETF Team 승격 판단

## 판단: **조건부 Go — Stock Team과 동일한 근거 수준에 도달했다.**

**근거(찬성)**:
1. ETF 고유 역할군(Composition/Index, Cost/Tracking, Distribution,
   그리고 확장된 Performance/Risk, Holdings/Exposure)이 3개의 서로
   다른 자산군·성격(기술 성장주/배당 가치주/채권)에서 **핵심 기능
   변경 없이** 3/3 확인됐다 — Stock Team이 3개 산업(소비자 하드웨어/
   AI 반도체/기업용 SW+클라우드)에서 반복성을 확인했던 것과 동일한
   종류·수준의 근거다.
2. Bull/Bear/Synthesis 구조는 오히려 Stock을 포함해 4회 연속 반복돼
   Stock Team보다도 더 넓은 반복 근거를 가진다.
3. Kernel/Registry/Scheduler 확장이 3/3 불필요했다 — Development HQ
   Platform이 ETF 도메인에서도 변경 없이 재사용 가능함을 다시 확인.
4. Division/Team은 여전히 `docs/01_architecture/BASELINE.md`의
   Division/Team 조항에 따라 RFC 없이 결정 가능한 사안이다.

**근거(유보)**:
1. Stock-ETF 간 실제 Capability 공유는 3회 모두 관찰되지 않았다 —
   ETF Team이 승격되더라도 Stock Team과는 독립적인 역할 집합을
   가져야 한다는 뜻이다(공유 Capability 후보 없음).
2. 병렬 실행 필요성은 여전히 미검증이다("다중 ETF 업무 발생" 조건이
   실제로 충족되지 않았다) — Team 승격 판단과는 별개 축이지만,
   Team 내부에서 다뤄야 할 실행 모델은 여전히 확인되지 않았다.
3. 이번 승격 판단도 이 세션이 임의로 확정하지 않는다 — Stock Team
   때와 동일하게 사용자에게 권고로 제시하고 최종 결정은 사용자
   판단에 맡긴다(Observe First, Decide Later).

## 승격 시 최소 역할/업무 범위 (확정 아님, 후보로만 제시)

3/3 반복된 범위만 제시한다:

- **업무 범위**: 구성/추적 방법론, 보유·노출 구조(종목 집중도 또는
  섹터/신용/만기 구조 — 자산군에 따라 적절한 프레임 선택), 비용/추적
  정확도, 성과·리스크(가격 성과 + 자산군에 맞는 리스크 지표), 분배/
  배당, 시장·거시환경 — 5~7개(자산군에 따라 재구성 가능)로 나눌 수
  있는 분석 → Bull/Bear 대립 검토 → Synthesis → Final Report.
- **명시적 제외 범위**: 실거래, 자동매매, Portfolio Management, Risk
  Management(Stock Team과 동일).

## 아직 확정할 수 없는 것

- Agent 이름, 세부 Architecture, Capability Contract, Development HQ
  Registry 등록 여부.
- Stock Team과의 관계(완전 독립 vs 일부 공유) — 3회 모두 독립으로
  나타났으나 향후 재검증 가능.
- 주식형·채권형 외 다른 자산군(원자재, 통화, 리츠 등)에서도 이 구조가
  반복되는지 — 미검증.
- ETF Team 최종 승격 여부·시점 — 이 문서는 권고이며 결정이 아니다.

# 6. Phase 7/11/12 압력 여부

**발생하지 않았다.** 3회 ETF 실행 전체에서 Cache/Runtime/병렬 실행
인프라를 실제로 요구하는 사실은 나타나지 않았다. Engine의 데이터
범위 이탈 사례(위 4번)도 Capability 지시문 개선 후보일 뿐, Kernel/
Contract/Runtime 변경을 요구하지 않는다.

# 7. 다음 작업

1. 사용자가 이 문서의 권고("조건부 Go")를 확정 결정으로 승인할지 판단.
2. 승인 시, ETF Team이라는 이름/디렉터리 관례를 Development HQ
   Baseline의 선택적 관례 범위 안에서(RFC 없이) 어떻게 반영할지는
   별도 후속 작업으로 정의.
3. Engine의 데이터 범위 이탈(SCHD 수치 혼입) 재현 여부를 향후 실행에서
   계속 관찰 — 반복되면 Capability 지시문에 격리 방안을 추가할지
   검토할 후보로 기록.
4. 다른 자산군(원자재/리츠 등) 확장이 필요하면 추가 Dogfooding 고려.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새 Agent, 새
Kernel Component, 새 Runtime, 새 Contract, 새 Cache를 만들지 않았다.
ETF Team/Agent를 선행 구현하지 않았다. Stop Trigger 미발동.
