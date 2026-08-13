# Stock Team Definition 0001 — 최소 업무 범위 승격

## 문서 성격

이 문서는 `docs/research/STOCK-DOGFOODING-REVIEW-0001.md`가 "조건부 Go"로
권고한 Stock Team 승격을, 사용자 지시에 따라 **확정**하는 문서다. Division/
Team은 Jarvis OS Meta Architecture의 필수 계층이 아니라 HQ 내부에서
선택적으로 쓸 수 있는 관례이며(`docs/01_architecture/BASELINE.md:50`,
`development-hq/STRUCTURE.md:15`), Jarvis OS Kernel은 그 존재 여부를 알
필요가 없다. 따라서 이 승격은 RFC → ADC → ADR 절차의 대상이 아니다.

이 문서가 하지 않는 것:
- Investment HQ 전체 Architecture 설계 (PRD 11장이 이 단계에서 금지한
  범위 — 여전히 하지 않는다. Investment HQ 자체는 이 저장소에 아직
  인스턴스화되어 있지 않다)
- Agent 이름 확정, 세부 구현, Capability Contract, Development HQ
  Registry 등록
- ETF/Dividend Stock Team 생성
- `development-hq/`(Development HQ Platform) 어떤 파일도 수정하지 않는다

## 근거

- `projects/stock-analysis-{aapl,nvda,msft}/issues/*/EVIDENCE.md` 3건 —
  동일 9단계 업무 구조가 3개의 서로 다른 산업(소비자 하드웨어/AI 반도체/
  기업용 SW+클라우드)에서 구조 변경 없이 3/3 반복됐다.
- `docs/research/STOCK-DOGFOODING-REVIEW-0001.md` — 위 3건을 종합해
  "조건부 Go"로 권고했고, PR #52로 main에 병합됨.
- 사용자 지시("Stock Team 승격을 진행하라") — 최종 결정 권한(Review-0001의
  "이 세션이 임의로 내리지 않는다" 유보 조건)을 사용자가 행사함.

## Status

**Promoted** (최소 업무 범위 한정, Agent/Architecture 미확정)

## Stock Team — 최소 업무 범위

3회 실행 모두에서 반복 관찰된 업무만 포함한다. 나열 순서는 3회 실행에서
실제로 실행된 순서(하드코딩된 순차 호출)를 따르되, 이 순서 자체가 Team의
Architecture나 Runtime 규약을 의미하지 않는다 — `development-hq/STRUCTURE.md`
의 Capability 나열과 동일한 원칙(나열 순서 ≠ 실행 순서 보장)을 그대로
따른다.

| 업무 | 내용 | 3/3 반복 근거 |
|---|---|---|
| Fundamental | 재무/마진/매출 구조 분석 | AAPL/NVDA/MSFT EVIDENCE §역할 |
| Technical | 추세/모멘텀 분석 | 동일 |
| Industry/Competition | 경쟁 구도, 산업 데이터 분석 | 동일 (MSFT에서 News-Event와 교차 통찰 사례 추가 확인) |
| News/Event | 정성적 이벤트 분석 | 동일 |
| Sentiment | 애널리스트 컨센서스/시장 심리 분석 | 동일 |
| Bull/Bear | 위 5개 분석을 근거로 낙관/비관 대립 검토 | 3/3, MSFT에서 가장 뚜렷하게 확인(Azure 번들링 사례) |
| Synthesis | Bull/Bear를 "합의된 사실/충돌/해석차/미해결질문"으로 구조화 | 3/3 자연 발생적 반복 |
| Final Report | 위 전체를 종합한 최종 보고서 | 3/3, 언어 혼재까지 정규화하는 역할까지 반복 확인(MSFT) |

**Context 요구사항**: 별도 저장소·Memory Service 불필요, in-memory 전달로
3/3 충분했다(`IMPLEMENTATION_RULES.md`의 Memory Service 구현 금지 원칙과
일치).

## 명시적 제외 범위

다음은 Stock Team의 업무 범위에 포함하지 않는다. PRD 2장이 명시적으로
범위 밖으로 규정했고, 3회 실행 모두 실제로 손대지 않았다.

- 실거래 실행
- 자동매매
- Portfolio Management(포트폴리오 구성/조정 승인)
- Risk Management(리스크 승인·거부)

## 아직 확정되지 않은 것

- Agent 이름(예: "Fundamental Analyst Agent" 같은 구체적 명명) — 이번
  승격은 업무 범위만 정의하며 Agent 단위 분할을 확정하지 않는다.
- 세부 Architecture(Capability Contract, Development HQ Registry 등록
  여부, Investment HQ와 Development HQ의 관계) — 실제 필요가 반복
  확인될 때만 구체화한다(사용자 지시 6번 원칙).
- Investment HQ 자체의 존재/구조 — 이 문서는 Investment HQ를 설계하거나
  인스턴스화하지 않는다. Stock Team은 향후 Investment HQ가 만들어질 때
  그 내부에서 선택적으로 쓰일 수 있는 업무 범위 정의일 뿐이다.
- ETF/Dividend Stock Team — 미생성. PRD 10장의 확장 순서(Stock → ETF →
  Dividend Stock)를 따라 각각 별도의 반복 검증(Dogfooding)이 필요할 때
  판단한다.
- 미국 대형 기술주 외 산업(금융/헬스케어/소비재/신흥시장 등)에서도 이
  범위가 그대로 반복되는지 — 3회 모두 미검증.

## Capability 개선 후보 (기록만, 지금 수정하지 않음)

- **출력 언어 비결정성**: `docs/research/STOCK-DOGFOODING-REVIEW-0001.md`
  §Capability 개선 후보에 이미 기록됨(3회 실행에서 3가지 다른 언어
  패턴 관찰). 이 문서는 중복 기록하지 않고 참조만 한다 — 필요 시 그
  문서를 갱신한다.

## 재평가 조건

다음 중 하나가 실제로 발생하면 이 정의를 재검토한다(지금 트리거하지
않는다, 조건만 기록):

- ETF 또는 Dividend Stock 대상 Dogfooding이 실행되어 Stock Team과 업무
  구조가 다르거나 겹치는 부분이 실제로 관찰될 때
- Agent 단위 분할이 실제 업무(예: 병렬 실행, 개별 Capability 재사용)에서
  필요하다는 근거가 실제로 나타날 때
- Investment HQ Architecture 설계가 별도로 착수될 때(RFC 절차 대상)

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새 Capability,
새 Agent, 새 Kernel Component, 새 Contract를 만들지 않았다. Governance/
Boundary 판단 변경이 필요한 지점은 발견되지 않았다.
