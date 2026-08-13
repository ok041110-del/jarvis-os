# ETF Team Definition 0001 — 최소 업무 범위 승격 확정

## 문서 성격

이 문서는 `docs/research/ETF-DOGFOODING-REVIEW-0003.md`가 "조건부 Go"로
권고한 ETF Team 승격을, 사용자 지시("ETF Team 승격을 확정")에 따라
**확정**하는 문서다. `docs/research/STOCK-TEAM-DEFINITION-0001.md`와
동일한 성격·형식을 따른다. Division/Team은 Jarvis OS Meta Architecture의
필수 계층이 아니라 HQ 내부에서 선택적으로 쓸 수 있는 관례이며
(`docs/01_architecture/BASELINE.md:50`, `development-hq/STRUCTURE.md:15`),
Jarvis OS Kernel은 그 존재 여부를 알 필요가 없다. 따라서 이 승격은
RFC → ADC → ADR 절차의 대상이 아니다.

이 문서가 하지 않는 것:
- Investment HQ 전체 Architecture 설계 (Investment HQ 자체는 이 저장소에
  아직 인스턴스화되어 있지 않다)
- Agent 이름 확정, 세부 구현, Capability Contract, Development HQ
  Registry 등록
- `development-hq/`(Development HQ Platform) 어떤 파일도 수정하지 않는다

## 근거

- `projects/etf-analysis-{qqq,schd,agg}/issues/*/EVIDENCE.md` 3건 —
  동일 업무 구조가 3개의 서로 다른 자산군·성격(기술 성장주/배당
  가치주/채권형)에서 핵심 기능 변경 없이 3/3 반복됐다.
- `docs/research/ETF-DOGFOODING-REVIEW-0003.md` — 위 3건을 종합해
  Stock Team과 동일한 3회 반복 기준으로 "조건부 Go"를 권고함.
- 사용자 지시("ETF Team 승격을 확정하고 Dividend Stock Dogfooding을
  시작하라") — 최종 결정 권한을 사용자가 행사함.

## Status

**Promoted** (최소 업무 범위 한정, Agent/Capability 미확정)

## ETF Team — 최소 업무 범위

3회 실행 모두에서 반복 관찰된 업무만 포함한다. AGG 실행에서 사용자
지시로 7개→6개로 재구성된 최종 형태를 기준으로 한다.

| 업무 | 내용 | 3/3 반복 근거 |
|---|---|---|
| Composition/Index | 추적 지수, 선정·가중 방법론, 리밸런싱/재구성 주기 | QQQ(가중방법론 변경)·SCHD(4단계 스크리닝)·AGG(표본추출) — 방법론은 매번 다르지만 역할은 3/3 유효 |
| Holdings/Exposure | 보유종목 집중도 또는(자산군에 따라) 섹터/신용등급/만기 구조 | QQQ·SCHD는 종목 집중도, AGG는 "종목 집중도 무의미 → 섹터/신용/만기로 전환"을 스스로 수행 — 프레임이 자산군에 맞게 전환되는 것 자체가 3/3 확인된 역할의 특성 |
| Cost/Tracking | 총보수율, 추적오차(수치 부재 시 그 사실 자체를 명시) | 3/3 추적오차 수치 부재를 자기인정, 원인은 매번 다름(유동성/증권대여/표본추출) |
| Performance/Risk | 수익률 성과 + 자산군에 맞는 리스크 지표(변동성, 베타, 듀레이션 등) | QQQ(정성적 변동성만)·SCHD(변동성/베타/샤프)·AGG(듀레이션·금리민감도) — 리스크 지표 유형은 자산군마다 다르지만 역할은 3/3 유효 |
| Distribution | 배당수익률, 지급주기, 분배금 추이 | 3/3 소스 간 수익률 수치 불일치를 자기인정, 지급주기는 자산군마다 다름(분기 vs 월간) |
| Macro/Market | 거시경제·금리 환경, 시나리오 | 3/3 실행 모두 거시 데이터의 불확실성/상충하는 보도를 명시적으로 인정 |

이후 → Bull Case/Bear Case → Synthesis → Final Report(Stock Team과
동일한 4단계, JPM→QQQ→SCHD→AGG 4회 연속 "사실 충돌 없음, 순수 해석
차이만 존재" 패턴 확인).

**Context 요구사항**: 별도 저장소 불필요, in-memory 전달로 3/3 충분.

## 명시적 제외 범위

Stock Team과 동일하게, 다음은 ETF Team의 업무 범위에 포함하지 않는다.

- 실거래 실행
- 자동매매
- Portfolio Management(포트폴리오 구성/조정 승인)
- Risk Management(리스크 승인·거부)
- 여러 ETF의 동시/배치 처리(3회 실행 모두 순차 단일 실행만 검증됨)

## 아직 확정되지 않은 것

- Agent 이름(예: "Composition Analyst Agent" 같은 구체적 명명).
- 세부 Architecture(Capability Contract, Development HQ Registry 등록
  여부, Investment HQ와 Development HQ의 관계).
- Stock Team과의 관계 — 3회 실행 모두 Stock의 5개 분석 역할이 재사용
  되지 않았고 공통 Capability 필요도 관찰되지 않았다. ETF Team은 Stock
  Team과 독립적인 역할 집합으로 취급한다.
- Investment HQ 자체의 존재/구조 — 이 문서는 Investment HQ를 설계하거나
  인스턴스화하지 않는다.
- 주식형·채권형 외 다른 자산군(원자재, 리츠, 통화 등)에서도 이 범위가
  반복되는지 — 미검증.
- 병렬 실행 필요성 — 3회 모두 "다중 ETF 동시 업무"가 실제 발생하지
  않아 미검증 상태로 남아 있다.

## Capability 개선 후보 (기록만, 지금 수정하지 않음)

- **출력 언어 비결정성**: `docs/research/STOCK-DOGFOODING-REVIEW-0001.md`
  ·`ETF-DOGFOODING-REVIEW-0001~0003`에 이미 기록됨. 7회 누적(Stock 4 +
  ETF 3) 기준으로도 패턴이 비결정적임을 재확인.
- **Engine의 데이터 범위 이탈**: AGG 실행에서 처음 관찰(전달되지 않은
  SCHD 수치를 산출물에 언급) — `docs/research/ETF-DOGFOODING-REVIEW-0003.md`
  참조. 1회 관찰이므로 지금 프롬프트를 수정하지 않는다.

## 재평가 조건

다음 중 하나가 실제로 발생하면 이 정의를 재검토한다(지금 트리거하지
않는다, 조건만 기록):

- 원자재/리츠/통화 등 다른 자산군 ETF Dogfooding에서 이번 범위와 다르거나
  겹치는 부분이 실제로 관찰될 때
- 여러 ETF를 동시/배치로 처리해야 하는 실제 업무가 발생할 때
- Stock Team과 실제로 Capability를 공유해야 하는 필요가 관찰될 때
- Engine의 데이터 범위 이탈이 반복 관찰될 때(Capability 지시문 개선
  검토)
- Investment HQ Architecture 설계가 별도로 착수될 때(RFC 절차 대상)

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새 Capability,
새 Agent, 새 Kernel Component, 새 Contract를 만들지 않았다. Governance/
Boundary 판단 변경이 필요한 지점은 발견되지 않았다.
