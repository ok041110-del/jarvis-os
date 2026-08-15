# AI Tool & Workflow Audit 0001 — Development HQ Workflow 확장 도구 평가

## 문서 성격

Refactoring Track이 `d5a4850`에서 종료된 시점에, Claude Code 중심의
현재 Development HQ workflow에 다른 AI 도구(Cowork/Artifacts/ClaudeMem/
NotebookLM/Obsidian/Graph 계열)를 실제로 결합할 가치가 있는지 평가한다.
도구를 Architecture Component로 가정하지 않고, 실제 Workflow Tool로만
판단한다. Integration 코드나 RFC/ADC/ADR은 이 문서에서 작성하지 않는다
— Trial 필요성만 표시한다.

## Summary

- **Adopt**: Claude Code(변경 없음, 핵심 유지), ClaudeMem(이미
  user-scope로 채택됨 — 현상 유지, 보조 메모리로만 사용)
- **Trial**: Claude Cowork(독립적 병렬 Dogfooding 라운드 한정),
  Claude Artifacts(Governance/Evidence 시각화 검토 보조, 저장소
  통합 없음)
- **Defer**: NotebookLM(현재 구체적 미해결 문제 없음)
- **Defer(범위 밖)**: Obsidian(저장소 밖 개인 뷰어로만 의미, 저장소
  통합 불필요)
- **Reject(현시점)**: Graph/Knowledge Graph 계열 — Registry/Kernel
  형태 도구를 사전에 도입하는 것과 동일한 문제이며, Implementation
  Rules의 "Registry 구현 금지"와 충돌하는 성격
- Architecture 영향 없음 — 어떤 도구도 Architecture Component로
  채택하지 않는다. Governance 영향 없음 — RFC/ADC/ADR 트리거 없음.
- Trial 대상 2건만 다음 실제 작업으로 남는다(§9).

---

## 0. 평가 기준

각 도구를 다음 10개 관점으로 판단한다(단순 기능 비교 배제):

1. 현재 Jarvis OS의 실제 문제를 해결하는가
2. Development HQ / Investment HQ 어느 위치에서 가치가 있는가
3. Claude Code와 기능이 겹치는가
4. Token/Context 효율을 개선하는가
5. 장기 Memory/Knowledge 관리에 실제 도움이 되는가
6. Research → Analysis → Implementation → Validation 중 어느 단계에
   적합한가
7. 자동화 가능한가
8. 사람이 반드시 검토해야 하는 부분은 무엇인가
9. 별도 도구를 추가할 비용/복잡성이 가치보다 큰가
10. Jarvis OS Architecture/Contract에 연결할 필요가 있는가

---

## 1. Tool별 평가

### 1-1. Claude Code

- **역할**: Implementation / Repository Engineering. 현재 workflow의
  단일 실행 주체(task-intake → context-loader → task-planner →
  implementation → validation → handover 전 과정).
- **실제 적용 지점**: Development HQ MVP 구현·Dogfooding, Investment
  HQ Team 정의, Governance Review, 이 Audit 자체.
- **기존 도구와의 중복**: 없음(기준점).
- **장점**: 저장소·git·skill 체계와 완전히 통합, Completion Standard(실제
  evidence 확인)를 스스로 강제 가능.
- **단점**: 단일 세션 = 순차 실행만 가능, 장시간 병렬 작업에는 부적합.
- **Integration 필요 여부**: 불필요(이미 핵심).
- **추천 상태**: **Adopt**(변경 없음).

### 1-2. Claude Cowork

- **역할**: Long-running / Multi-file / Multi-step Knowledge Work.
- **실제 적용 지점**: 현재 워크플로우의 병목은 병렬성 부족이 아니라
  **의도적 순차성**이다 — MVP-0001~0048, Stock/ETF/Dividend Stock
  Dogfooding 모두 "한 라운드 검증 → 판단 → 다음 라운드" 구조로
  설계되어 있고, Kernel Extraction Rule 자체가 성급한 일반화를
  막기 위해 존재한다. Cowork의 자율 병렬 실행은 이 구조와 정면으로
  맞지 않는다. 다만 **서로 독립적인 반복 작업**(예: Investment HQ의
  다음 Dogfooding 라운드를 여러 Team에서 동시에 진행)에는 국지적으로
  쓸모가 있을 수 있다.
- **기존 도구와의 중복**: Claude Code의 Task/Agent 병렬 실행과 개념적으로
  겹친다 — Cowork는 그 상위의 "장시간 자율" 버전일 뿐.
- **장점**: 사람이 자리를 비운 동안 독립적 반복 검증을 진행할 수 있음.
- **단점**: Governance-gated 판단(ADC 채택, Architecture 문제 발견 시
  RFC 전환 등)은 사람의 순차적 개입이 전제이므로, Cowork에 맡기면
  Completion Standard("실패한 검증을 성공으로 표현하지 않음")를
  검증 없이 통과시킬 위험이 있음.
- **Integration 필요 여부**: 없음(외부 실행 도구로 ad hoc 사용 가능,
  저장소에 아무것도 추가하지 않음).
- **추천 상태**: **Trial** — Kernel/Architecture 판단이 없는, 완전히
  독립적인 반복 작업 한정.

### 1-3. Claude Artifacts

- **역할**: Interactive Output / Prototype / Review.
- **실제 적용 지점**: 현재 산출물은 전부 Markdown(RFC/ADC/ADR/Evidence
  Review)이며 UI 산출물이 필요한 MVP 범위가 없다. 다만 Governance
  상태(12개 Open ADC, MVP-0001~0048 Evidence, 3개 Investment Team
  Promotion 이력)를 사람이 검토할 때 표/타임라인 형태로 한눈에 보는
  보조 자료로는 가치가 있다.
- **기존 도구와의 중복**: 없음 — Claude Code는 텍스트 산출만 하고
  Artifacts 같은 시각적 렌더링을 하지 않는다.
- **장점**: 사람의 Governance Review 속도를 높일 수 있음(Completion
  Standard의 "실제 evidence 확인" 단계를 보조).
- **단점**: 저장소의 canonical source가 아님 — 재생성 가능한 뷰일
  뿐이며, 데이터 원본은 항상 Markdown이어야 함.
- **Integration 필요 여부**: 없음(세션 내 ad hoc 산출물, 저장소에
  커밋하지 않음).
- **추천 상태**: **Trial** — Governance Review 시점에 한정해 보조
  시각화로 사용.

### 1-4. ClaudeMem

- **역할**: Session/Project Memory 후보.
- **실제 적용 지점**: 이미 평가·설치되어 `.claude/docs/integrations/claude-mem.md`에
  기록되어 있고, CLAUDE.md의 Context Loading 목록에도 "세션 기억 →
  Claude-Mem"으로 명시되어 있다. User-scope(머신 단위) 설치이며 저장소에는
  아무 파일도 남기지 않는다.
- **기존 도구와의 중복**: HANDOVER.md/CLAUDE.md/ADC.md 같은 git 기반
  authoritative memory와 역할이 겹칠 위험이 있음 — 이 저장소의 규칙
  ("source가 존재하면 memory보다 source를 우선")이 이미 이 위험을
  차단하고 있음.
- **장점**: 세션 간 tacit 컨텍스트(아직 문서화 전 판단)를 보완.
- **단점**: 자동 요약이 authoritative 문서와 어긋날 수 있음 — 항상
  보조 역할로만 취급해야 함.
- **Integration 필요 여부**: 이미 완료(문서화됨), 추가 조치 불필요.
- **추천 상태**: **Adopt**(현상 유지 — 이미 채택된 상태를 재확인).

### 1-5. NotebookLM

- **역할**: Source-grounded Research / Learning 후보.
- **실제 적용 지점**: Architecture Baseline + RFC/ADC/ADR + Evidence
  전체를 업로드해 사람이 질의응답 형태로 훑어볼 수 있게 하는 시나리오는
  상상 가능하지만, 이 역할은 이미 context-loader 스킬 + HANDOVER.md가
  Claude Code 세션 안에서 수행하고 있다. 사람 단독(비-Claude) 온보딩
  수요가 현재 확인되지 않음.
- **기존 도구와의 중복**: context-loader + docs/ 구조와 상당 부분 겹침.
- **장점**: 없음(현재 확인된 수요 기준).
- **단점**: 외부(Google) 서비스에 저장소 문서를 업로드해야 함(기밀성
  고려 필요), git과 연동되지 않아 문서 변경 시 수동 재업로드 필요,
  자동화 불가능.
- **Integration 필요 여부**: 없음.
- **추천 상태**: **Defer** — 비-Claude 인간 이해관계자의 구체적 수요가
  생기기 전까지 보류.

### 1-6. Obsidian

- **역할**: Human-managed Knowledge Base 후보.
- **실제 적용 지점**: `docs/` 트리 자체가 이미 git 버전관리되는
  Markdown 지식베이스다. Obsidian은 이 파일들을 그대로 열어볼 수
  있는 개인용 뷰어/그래프 UI일 뿐, 저장소에 어떤 변경도 요구하지
  않는다(설정 없이 즉시 호환).
- **기존 도구와의 중복**: docs/ 구조 + GitHub UI + 일반 에디터와 거의
  전부 겹침.
- **장점**: 개인이 로컬에서 backlink/graph view로 문서를 탐색하고
  싶다면 저장소 변경 없이 바로 쓸 수 있음.
- **단점**: 저장소 workflow에 어떤 자동화나 기여도 하지 않음. `[[wikilink]]`
  같은 Obsidian 전용 문법을 문서에 도입하면 "도구 사용을 위해 기존
  Architecture/문서를 바꾸지 않는다"는 원칙과 충돌.
- **Integration 필요 여부**: 없음 —애초에 저장소 범위의 결정 대상이
  아님(개인 로컬 도구 선택 문제).
- **추천 상태**: **Defer**(저장소 workflow 범위 밖 — 개인 선택 사항으로
  분리).

### 1-7. Graph / Knowledge Graph 계열

- **역할**: Relationship / Knowledge Graph 탐색 후보.
- **실제 적용 지점**: ADC-RFC-ADR-Evidence 간 관계, MVP-0001~0048과
  Investment Dogfooding 이력 간 관계를 그래프로 탐색하는 시나리오.
  그러나 현재 문서 규모(~50여 개 research 문서, 12개 Open ADC)는
  Grep/Glob과 ADC.md 단일 문서로 충분히 추적 가능하다.
- **기존 도구와의 중복**: `docs/research/`, `docs/03_adc/ADC.md`가
  이미 이 역할의 canonical source.
- **장점**: 문서 규모가 훨씬 커지면 탐색 효율이 오를 수 있음(현재는
  해당 없음).
- **단점**: 관계를 저장·질의하는 별도 인덱스/서비스는 본질적으로
  Registry-형태 컴포넌트다. Implementation Rules는 "Registry 구현
  금지", "Registry 일반화 금지"를 명시하고 있고, Kernel Extraction
  Rule은 "필요성이 실제로 드러났을 때만" 다루라고 규정한다. 지금
  도입하면 이 두 규칙을 도구 선택이라는 우회로로 위반하는 셈이다.
- **Integration 필요 여부**: 해당 없음(도입 자체를 보류).
- **추천 상태**: **Reject(현시점)** — Kernel Extraction Candidate로
  실제로 나타날 때(문서/결정 규모가 ad hoc 탐색으로 감당 안 될 때)만
  재검토.

---

## 2. Workflow별 최적 도구

```
Research → Knowledge → Planning → Implementation → Validation → Evidence → Memory
```

| 단계 | 배치 도구 | 비고 |
|---|---|---|
| Research | Claude Code (WebSearch/WebFetch/Explore) | 1차 도구. NotebookLM은 Defer — 재검토 트리거 없이 추가하지 않음 |
| Knowledge | `docs/` Markdown 트리 (canonical) | Obsidian은 저장소 밖 개인 뷰어로만 가능, workflow에 포함하지 않음 |
| Planning | Claude Code (task-intake → context-loader → task-planner) | 이미 정착된 경로, 변경 없음 |
| Implementation | Claude Code | 유일한 구현 도구, 변경 없음 |
| Validation | Claude Code (validation skill) + Claude Artifacts(보조 시각화, Trial) | Artifacts는 검토 보조일 뿐 검증 주체가 아님 |
| Evidence | `docs/research/`, `docs/01_mvp/` (canonical, git) | Artifacts로 일회성 대시보드 생성 가능(Trial), 저장은 항상 Markdown |
| Memory | `HANDOVER.md` / `CLAUDE.md` / `ADC.md` (authoritative) + ClaudeMem(보조, user-scope) | ClaudeMem은 절대 authoritative가 아님 — 이미 이렇게 운영 중 |

Cowork는 특정 단계에 고정 배치하지 않는다. Kernel/Architecture 판단이
없는 독립적 반복 작업(Research 또는 Implementation의 병렬 반복분)에
한해 국지적으로만 시도한다.

---

## 3. 중복/불필요 도구

- **NotebookLM** — Research/Knowledge 단계에서 context-loader +
  `docs/`가 이미 수행 중인 역할과 중복, 자동화 이득 없음.
- **Graph 계열** — `docs/research/` + `ADC.md`가 이미 수행 중인 관계
  추적 역할과 중복이며, 현재 규모에서는 도구 자체가 불필요.
- **Obsidian** — `docs/`가 이미 Markdown 지식베이스이므로, 저장소
  workflow 관점에서는 추가 도구가 아니라 개인 선택 사항.

## 4. Trial 대상

- **Claude Cowork** — 다음 Investment HQ Dogfooding 라운드 1건을
  독립 실행으로 시도, 기존 순차 방식과 결과/Evidence 품질 비교.
- **Claude Artifacts** — 다음 Governance Review 시점에 ADC/Evidence
  상태를 1회 시각화해 검토 소요 시간 비교.

## 5. Adopt 대상

- **Claude Code** — 변경 없음, 핵심 유지.
- **ClaudeMem** — 이미 채택된 상태 재확인, 보조 역할 유지.

## 6. Defer/Reject 대상

- **NotebookLM** — Defer(구체적 미해결 문제 없음).
- **Obsidian** — Defer(저장소 workflow 범위 밖).
- **Graph/Knowledge Graph 계열** — Reject(현시점, Registry-형태 도구
  사전 도입 문제와 동일).

## 7. Architecture 영향

없음. 어떤 도구도 Architecture Component로 가정하지 않았고, Baseline
문서를 수정할 근거가 발견되지 않았다. Trial 2건(Cowork/Artifacts)에서
반복적 필요(예: 상시 대시보드, 병렬 실행 조정 로직)가 실제로 드러나면
그 시점에 Kernel Extraction Candidate로 `docs/03_adc/ADC.md`에
기록한다 — 지금 미리 설계하지 않는다.

## 8. Governance 영향

없음. RFC/ADC/ADR을 열 근거가 확인되지 않았다 — Integration 필요성이
실제로 확인된 경우에만 제안한다는 전제를 지켰다. Trial 결과가 저장소
workflow에 지속 반영할 가치를 실제로 입증하면, 그 시점에 RFC 절차로
넘긴다(지금은 아님).

## 9. 다음 실제 작업

1. Cowork Trial: Investment HQ 다음 Dogfooding 라운드 1건을 독립
   실행 조건에서 시도하고 Evidence 품질을 기존 방식과 비교한다.
2. Artifacts Trial: 다음 Governance Review에서 ADC/Evidence 상태
   시각화를 1회 시도하고 검토 효율을 비교한다.
3. 그 외 조치 없음 — 이 Audit은 Architecture/Baseline을 변경하지
   않았으며, Frozen 상태를 그대로 유지한다.
