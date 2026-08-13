# Stock Agent Separation Review 0001 — 역할/Agent 분리 필요성 검증

## 문서 성격

이 문서는 `docs/research/STOCK-TEAM-DEFINITION-0001.md`(Stock Team 최소
업무 범위 승격) 이후, 실제 업무(JPM 분석, 4번째 반복)를 역할 분리 상태로
수행해 8개 업무 각각이 독립 Agent로 승격될 만큼 반복성·독립성이 있는지
검증한 결과를 종합한다. `projects/stock-analysis-jpm/issues/0001-jpm-analysis/EVIDENCE.md`
의 판정을 그대로 확정하며, 새 Agent를 만들지 않는다.

## 범위

- `projects/stock-analysis-jpm/`(신규, 4번째 실행) 전체 산출물과
  `EVIDENCE.md`
- `projects/stock-analysis-{aapl,nvda,msft}/issues/*/EVIDENCE.md`(비교 대상)
- `docs/research/STOCK-TEAM-DEFINITION-0001.md`(전제 조건)

---

# 1. 무엇을 했는가

Stock Team의 8개 업무(Fundamental/Technical/Industry-Competition/
News-Event/Sentiment/Bull-Bear/Synthesis/Final Report)를 project-local
패턴(`agents.py`/`runner.py`, 실제 `call_engine()` 호출)으로 JPMorgan
Chase(JPM) 대상 실제 실행했다. AAPL/NVDA/MSFT와 다른 산업(금융)의 실제
기업을 선정해 산업 다양성 한계를 부분적으로 보완했다. 이번 실행은
기존 3회와 달리 각 호출의 입력 길이/출력 길이/소요 시간을
`call_log.json`으로 계측해, 역할 간 입력·출력·Context 의존성을 정량
근거로 남겼다.

# 2. 무엇이 반복 확인됐는가

- 9단계 파이프라인 완주, Kernel/Registry/Scheduler 불필요, in-memory
  Context 충분, 병렬 실행 불필요, 역할 비중복성 — 4/4 반복.
- 회사 식별 수정(`_COMPANY_HEADER`) 안정적 재사용 — 3/3.
- 정보 파편화 미발생 — 3/3(AAPL 최초 발견·수정 이후).
- Industry Analyst의 자발적 출처 신뢰도 비판 — NVDA에 이어 JPM에서도
  재현(2회 이상).
- Bull/Bear 협업 유용성 — 4/4, 다만 JPM은 "순수 해석 차이만 존재, 사실
  충돌 없음"이라는 새로운 하위 유형을 처음 보였다(AAPL/MSFT는 최소 1건의
  사실 차원 충돌/이중성이 있었음).
- 출력 언어 비결정성 — 4회 중 AAPL(전체 한국어)/NVDA(전체 영어)/MSFT
  (혼재)/JPM(전체 영어)로 패턴이 여전히 비결정적이며, JPM에서는 영어
  문장 안에 한국어 로마자 표기가 섞이는 새로운 하위 현상(부분 언어
  누출)이 추가로 관찰됨 — 기존 Capability 개선 후보에 하위 항목으로
  추가.
- **역할을 독립적으로(파이프라인 밖에서) 반복 호출해야 하는 필요, 그리고
  동일 Agent를 여러 프로젝트/Workflow가 공유 호출하는 사례 — 4회 모두
  관찰되지 않았다.**

# 3. 어떤 역할이 실제 Agent 후보인가

**현재 기준으로는 없다.** 8개 업무 모두 "동일 역할 반복(4/4)", "독립
입출력 경계", "명확한 전문 목적 구분" 3개 기준은 정도 차이는 있으나
충족했지만, 4번째 기준인 **"독립 실행 또는 재사용 가치가 실제로
확인됨"은 8개 업무 어디에서도 충족되지 않았다.** 모든 재사용은
project-local 코드 복제(각 프로젝트가 자기만의 `agents.py` 사본을
가짐)를 통한 것이며, 하나의 Agent 인스턴스를 여러 Workflow/Team이
실제로 공유 호출한 사례는 4회 실행 어디에도 없다.

이 4개 기준을 모두 충족하지 못하는 한, 사용자 지시 원칙("단순히 역할
이름이 존재한다는 이유로 Agent를 만들지 않는다", "이론적으로 필요해
보인다는 이유만으로 Architecture를 변경하지 않는다")에 따라 보수적으로
판정한다 — 8개 업무 전부 **승격 보류**.

# 4. 아직 Agent로 만들 필요가 없는 역할은 무엇인가

8개 업무 전부다. 다만 균질하지 않다:

- **가장 유력한 향후 후보 그룹**: Fundamental/Technical/Industry/
  News-Event/Sentiment 5개 분석 — 독립 입출력 경계(자기 raw_data 섹션만
  소비)와 전문성 차이가 4회 모두 가장 뚜렷하게 확인됨.
- **가장 후순위 그룹**: Bull/Bear(5개 분석 전체에 의존, 독립 입력 경계
  없음), Synthesis/Final Report(누적 Artifact 전체에 전적으로 의존,
  독립 입출력 경계가 사실상 없음 — `docs/research/EVIDENCE-REVIEW-0001.md`
  가 Development HQ SDLC에서 관찰한 Artifact Flow 패턴과 동일 성격).

# 5. 무엇이 남았는가

- **Agent 단위 공유 재사용의 실제 검증** — 지금까지 4회 실행 전부
  project-local 코드 복제로 처리됐다. 만약 ETF/Dividend Stock Team이
  향후 생기고, 그때 "Fundamental Analyst 역할을 Stock Team과 ETF Team이
  실제로 공유해야 하는 필요"가 관찰된다면, 그것이 Agent 승격을 재검토할
  첫 실제 근거가 된다. 지금은 그 필요가 존재하지 않는다(ETF/Dividend
  Stock Team 자체가 아직 없음 — 인위적으로 만들지 않는다).
- 미국 대형 기술주 외 산업 검증은 이번 JPM 실행으로 1건 추가됐으나
  (금융/투자은행), 헬스케어/소비재/신흥시장 등은 여전히 미검증.
- 부분 언어 누출 현상이 반복되는지(1회 관찰) — 추가 실행에서 재현 여부
  확인 필요.
- PRD v1.2 원문 부재 — `docs/research/STOCK-DOGFOODING-REVIEW-0001.md`
  이후 여전히 해소되지 않음.

# 6. Investment HQ에서의 의미

이 검증은 Investment HQ Architecture를 설계하지 않는다. 다만 다음 사실은
향후 Investment HQ 논의에 참고 자료로 남긴다:

- Stock Team의 8개 업무는 **Capability 함수 수준에서는** 이미 충분히
  분리되어 반복 가능하다(4/4) — 이는 Development HQ의 기존 패턴
  (`agents.py`의 리터럴 dict + 지시문-프리픽스 함수)이 Investment
  도메인에서도 변경 없이 그대로 작동함을 다시 확인한 것이다.
- 그러나 **Agent라는 단위**(Workflow → Task → Capability → Agent 관계에서
  여러 Workflow/Team이 공유하는 실행 주체)로 승격할 실제 필요는 아직
  한 번도 관찰되지 않았다 — Investment HQ가 여러 Team(Stock/ETF/
  Dividend 등)을 실제로 운영하게 되어 같은 Capability를 여러 Team이
  공유해야 하는 순간이 오기 전까지는, 이 승격은 이론적 필요일 뿐 실제
  필요가 아니다.
- 이는 `docs/01_architecture/BASELINE.md`의 Division/Team 조항과도
  일치한다: Team은 선택적 관례이며 Kernel이 알 필요가 없는 계층이므로,
  그 하위의 Agent 단위 분리 역시 실제 재사용 필요가 나타날 때만
  Governance 절차(RFC → ADC → ADR)로 논의하면 된다 — 지금 선행 설계하지
  않는다.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새 Agent, 새
Capability(Stock Team 범위 밖), 새 Kernel Component, 새 Contract를
만들지 않았다. Stop Trigger 미발동.
