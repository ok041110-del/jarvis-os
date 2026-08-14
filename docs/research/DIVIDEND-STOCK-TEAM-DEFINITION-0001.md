# Dividend Stock Team Definition 0001 — 최소 업무 범위 승격 확정

## 문서 성격

이 문서는 `docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0002.md`가
"조건부 Go"로 권고한 Dividend Stock Team 승격을, 사용자 지시("Dividend
Stock Team Promotion을 정식 반영하라")에 따라 **확정**하는 문서다.
`docs/research/STOCK-TEAM-DEFINITION-0001.md`,
`docs/research/ETF-TEAM-DEFINITION-0001.md`와 동일한 성격·형식을
따른다. Division/Team은 Jarvis OS Meta Architecture의 필수 계층이
아니라 HQ 내부에서 선택적으로 쓸 수 있는 관례이며
(`docs/01_architecture/BASELINE.md:50`, `development-hq/STRUCTURE.md:15`),
Jarvis OS Kernel은 그 존재 여부를 알 필요가 없다. 따라서 이 승격은
RFC → ADC → ADR 절차의 대상이 아니다.

이 문서가 하지 않는 것:
- Investment HQ 전체 Architecture 설계 (Investment HQ 자체는 이 저장소에
  아직 인스턴스화되어 있지 않다)
- Agent 이름 확정, 세부 구현, Capability Contract, Development HQ
  Registry 등록
- Stock Team과의 코드 공유(import) 강제 — 3회 실행 모두 project-local
  코드 복제로만 재사용됐고, 이 문서는 그 방식을 그대로 유지한다
  (`docs/research/DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001.md` §3-1)
- `development-hq/`(Development HQ Platform) 어떤 파일도 수정하지 않는다

## 근거

- `projects/dividend-stock-analysis-{jnj,ko,pg}/issues/*/EVIDENCE.md`
  3건 — Stock의 5개 분석 역할이 지시문 변경 없이 3/3 재사용됐고,
  Dividend Quality/Valuation 고유 역할이 3개의 서로 다른 산업(헬스케어/
  음료/생활용품)에서 매번 다른 유형의 밸류에이션 데이터 결함을
  자기인정 방식으로 정확히 포착하며 3/3 반복됐다.
- `docs/research/DIVIDEND-STOCK-DOGFOODING-REVIEW-0002.md` — 위 3건을
  Stock/ETF Team과 동일한 3회 반복 기준으로 종합해 "조건부 Go"를
  권고함.
- `docs/research/DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001.md` —
  "Stock Team 확장 vs 독립 Team" 질문에 대해 "독립 명명 + 확장 성격
  문서화"를 권고함(코드 공유 근거 없음, Division/Team은 관례).
- 사용자 지시("Dividend Stock Team Promotion을 정식 반영하고... Team은
  독립적으로 명명하되, 역할/Capability 관점에서는 Stock Team의 확장으로
  문서화하라") — 최종 결정 권한을 사용자가 행사함.

## Status

**Promoted** (최소 업무 범위 한정, Agent/세부 Architecture 미확정)

## Dividend Stock Team — Stock Team과의 관계

**독립적으로 명명된 Team이며, 역할/Capability 관점에서는 Stock Team의
확장이다.** 이 두 서술은 배타적이지 않다:

- **명명/디렉터리**: `projects/stock-analysis-*`, `projects/etf-analysis-*`
  와 동일한 수준의 독립 관례로 `projects/dividend-stock-analysis-*`를
  유지한다. Team 자체는 코드 공유 단위가 아니라 이름/문서 정체성
  단위다(§3-2, `DIVIDEND-STOCK-TEAM-STRUCTURE-DECISION-0001.md`).
- **역할/Capability 내용**: 7개 역할 중 5개(Fundamental/Technical/
  Industry-Competition/News-Event/Sentiment)가 Stock Team의 역할과
  지시문 한 글자 차이 없이 3/3 동일하다 — ETF Team(Stock 역할을 전혀
  재사용하지 않음, 완전 독립)과 대조되는 지점이며, 이 대조 자체가
  "Dividend Stock은 Stock Team의 하위 유형(확장)"이라는 성격 규정의
  근거다.
- **코드 공유는 강제하지 않는다**: 3회 실행 모두 project-local 코드
  복제(각 프로젝트가 자기만의 `agents.py` 사본을 가짐)로 재사용됐다.
  실제 import/공유 모듈은 만들지 않았고, 이 문서도 만들지 않는다 —
  `docs/research/STOCK-AGENT-SEPARATION-REVIEW-0001.md` §3이 이미
  Stock Team 내부에서도 "독립 실행/재사용 가치가 실제로 확인된 사례
  없음"으로 판정한 것과 동일한 원칙을 그대로 따른다.

## Dividend Stock Team — 최소 업무 범위

3회 실행 모두에서 반복 관찰된 업무만 포함한다.

| 업무 | 내용 | 3/3 반복 근거 | Stock과의 관계 |
|---|---|---|---|
| Fundamental Analysis | 재무/펀더멘털 추세 | JNJ·KO·PG 3/3, 지시문 변경 없음 | Stock 역할 그대로 재사용 |
| Technical Analysis | 기술적 추세/모멘텀 | JNJ·KO(강세)·PG(약세/중립) — 데이터 방향이 반대여도 역할은 3/3 유효 | Stock 역할 그대로 재사용 |
| Industry-Competition Analysis | 산업/경쟁 구도 | 3/3 | Stock 역할 그대로 재사용 |
| News-Event Analysis | 뉴스/이벤트 영향 | 3/3 | Stock 역할 그대로 재사용 |
| Sentiment Analysis | 애널리스트 컨센서스/시장 심리 | 3/3 | Stock 역할 그대로 재사용 |
| Dividend Quality Analysis | 배당 성장 트랙레코드/지급여력/커버리지 | JNJ(배당성향 급락 지적)·KO(FCF 연동 부재 지적)·PG(분기/연간 산정 기준 모호성 지적) — 매번 다른 유형의 결함을 3/3 자기인정 | **Dividend Stock 고유** |
| Valuation Analysis | 밸류에이션 배수, 동종업계 비교, 데이터 결함 식별 | JNJ(DCF vs P/E 상반)·KO(DCF 부재 인식)·PG(P/E 수치 자체의 내부 모순) — 3/3, 매번 다른 유형 | **Dividend Stock 고유** |

이후 → Bull Case/Bear Case → Synthesis → Final Report(Stock/ETF Team과
동일한 4단계, JPM→QQQ→SCHD→AGG→JNJ→KO→PG **7회 연속** "사실 충돌은
데이터 자체의 문제, Bull/Bear 대립은 순수 해석 차이"라는 결론 패턴
확인).

**Context 요구사항**: 별도 저장소 불필요, in-memory 전달로 3/3 충분.

## 명시적 제외 범위

Stock/ETF Team과 동일하게, 다음은 Dividend Stock Team의 업무 범위에
포함하지 않는다.

- 실거래 실행
- 자동매매
- Portfolio Management(포트폴리오 구성/조정 승인)
- Risk Management(리스크 승인·거부)
- 여러 배당주의 동시/배치 처리(3회 실행 모두 순차 단일 실행만 검증됨)

## 아직 확정되지 않은 것

- Agent 이름(예: "Dividend Quality Analyst Agent" 같은 구체적 명명).
- 세부 Architecture(Capability Contract, Development HQ Registry 등록
  여부, Investment HQ와 Development HQ의 관계).
- Stock Team과의 실제 코드 공유 여부 — 지금은 project-local 복제로
  충분하며, 실제 공유 필요가 관찰되기 전까지 선행 설계하지 않는다
  (`STOCK-AGENT-SEPARATION-REVIEW-0001.md` §6).
- Investment HQ 자체의 존재/구조 — 이 문서는 Investment HQ를 설계하거나
  인스턴스화하지 않는다.
- 미국 대형 배당주 외(국제/신흥시장/리츠형 배당) 자산군에서도 이 범위가
  반복되는지 — 미검증.
- 병렬 실행 필요성 — 3회 모두 "다중 배당주 동시 업무"가 실제 발생하지
  않아 미검증 상태로 남아 있다.

## Capability 개선 후보 (기록만, 지금 수정하지 않음)

- **출력 언어 비결정성**: `docs/research/STOCK-DOGFOODING-REVIEW-0001.md`
  ·`ETF-DOGFOODING-REVIEW-0001~0003.md`에 이미 기록됨. JNJ(대부분
  영어)·KO(전량 영어)·PG(전량 영어)로 이번 3회는 영어 우세였으나,
  10회 누적(Stock 4 + ETF 3 + Dividend Stock 3) 기준으로는 여전히
  패턴을 확정하지 않는다(표본 3만으로 결정적 판단 금지).
- **AGG Data Boundary 재평가 가능성**: `docs/research/
  AGG-DATA-BOUNDARY-REPRODUCTION-0001.md`가 AGG의 "Engine 데이터 범위
  이탈" 관찰을 Execution이 아닌 Acquisition 단계 문제일 가능성으로
  재분류했고, JNJ/KO/PG 4회 재현 시도 전부 새 이상 징후 없음으로
  확인했다. 이 문서는 그 결론을 참고만 하며, `ETF-TEAM-DEFINITION-0001.md`
  의 기존 서술을 이 문서가 대신 수정하지 않는다.

## 재평가 조건

다음 중 하나가 실제로 발생하면 이 정의를 재검토한다(지금 트리거하지
않는다, 조건만 기록):

- Stock Team과 실제로 코드(Agent 인스턴스)를 공유해야 하는 필요가
  관찰될 때 — 이때 RFC → ADC → ADR 절차로 논의한다
  (`STOCK-AGENT-SEPARATION-REVIEW-0001.md` §6).
- 국제/신흥시장/리츠형 배당주 Dogfooding에서 이번 범위와 다르거나
  겹치는 부분이 실제로 관찰될 때.
- 여러 배당주를 동시/배치로 처리해야 하는 실제 업무가 발생할 때.
- Investment HQ Architecture 설계가 별도로 착수될 때(RFC 절차 대상).

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새 Capability,
새 Agent, 새 Kernel Component, 새 Contract, 새 Runtime을 만들지 않았다.
Stock↔Dividend Stock 코드 공유를 강제하지 않았다. Governance/Boundary
판단 변경이 필요한 지점은 발견되지 않았다.
