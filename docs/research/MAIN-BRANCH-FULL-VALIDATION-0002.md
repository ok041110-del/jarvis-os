# Main Branch Full Validation — 코드·문서·Governance 무결성 검증 (2차)

**문서 성격**: READ-ONLY 검증. 근거 없이 코드를 수정하거나 문서를
변경하지 않는다. 이 문서 자체는 신규 추가 파일이며, 기존 파일은
1건도 수정하지 않는다. 문서 번호에 "0002"를 붙인 이유: 본문 §2.1이
인용하는 "이전 Main Branch Full Validation 세션"(§2.1, §3.2에서
재확인된 선행 검증)이 이미 1회 수행되었고, 그 결과 일부가
`docs/research/RFC-ROLE-BOUNDARY-REVIEW-0001.md`,
`docs/research/ADC-0010-IMPLEMENTATION-SEQUENCE-COMPLIANCE-REVIEW-0001.md`
(PR #209)로 기록되었다 — 그 선행 산출물을 재작성하지 않고 인용하며,
이번 문서는 그 이후 상태(main HEAD `412330b`)에 대한 독립적 재검증이다.

## 0. 대상

| 항목 | 값 |
|---|---|
| Repository | ok041110-del/jarvis-os |
| 검증 대상 Branch | `main` |
| 검증 시점 HEAD | `412330b` (Merge PR #209) |
| 관련 Issue | #206(Open) |
| 관련 PR | #207(Merged), #208(Merged), #209(Merged), #210(Open, 미병합) |

---

## 1. 사전 확인

| 항목 | 결과 |
|---|---|
| Repository/Branch/HEAD | 세션 시작 시 `claude/decision-templates-restructure-lf3jwf`(HEAD `c035431`, `origin/main`보다 1커밋 앞섬 — PR #210) 상태였음. 검증 대상이 `main`이므로 `git checkout main && git pull origin main`으로 전환 |
| origin/main 동기화 | 전환 후 `git rev-parse HEAD origin/main` 동일 값(`412330b6e722a3de2b9a50fa0bc3540255e26d52`) — 완전 동기화 확인 |
| Working tree | `git status --short` 출력 없음 — Clean |
| 최신 main 여부 | `git fetch origin` 이후 `origin/main`과 로컬 `main`이 일치 — 최신 확인 |
| Issue #206 | GitHub API로 재조회 — **Open** 상태 유지 |
| PR #207 | Merged(템플릿 통합) |
| PR #208 | Merged(식별자 통일 조사/ADC-0010/Registry/RFC-0008 재검증) |
| PR #209 | Merged(Issue #206 후속 문서 정정 — 이번 검증 시작 시점의 main에 포함됨) |
| PR #210 | **Open, 미병합** — RFC-0007 Role Note + HANDOVER.md 테스트 기준선 정정. 이 PR의 변경 사항은 아직 `main`에 없다 — 아래 §3.1/§4에서 발견되는 "RFC-0007 role 위반 원문 그대로", "HANDOVER.md 테스트 기준선 stale(186 passed)"은 **PR #210이 이미 고치는 중인 항목**이며 이번 검증이 새로 발견한 결함이 아니다(단, 검증 대상은 어디까지나 `main`이므로 사실 그대로 기록한다) |

이 검증은 최신 `main`(`412330b`) 기준으로 수행했다.

---

## 2. 코드 검증

### 2.1 실행한 명령어

프로젝트 표준 확인: `README.md`에는 테스트 명령이 명시되어 있지
않다. `pytest.ini`(repo root)는 `addopts = --import-mode=importlib`
만 지정하며, "`projects/notekeeper`와 `projects/textkit`의 tests
패키지명 충돌 회피" 주석이 있다. `hqs/development/HANDOVER.md`(현재
작업 상태 문서, CLAUDE.md Context Loading 지정 경로)가 실제
표준으로 `pytest hqs/development/mvp/tests/ -q` 및 개별
`core/execution/mvp_000X` 형태를 반복 사용한다 — 이를 근거로 아래
명령을 실행했다.

```bash
python3 -m py_compile <379개 .py 파일, archive/ 제외>
find docs -name "*.md" ... (Markdown 구조·링크 검증, 별도 스크립트)
/root/.local/bin/pytest hqs/development/mvp/tests/ -q
/root/.local/bin/pytest hqs/investment/tests/ -q
/root/.local/bin/pytest core/execution/ -q
/root/.local/bin/pytest projects/dashboard-shell-mvp/tests/ -q
/root/.local/bin/pytest projects/unified-dashboard -q
/root/.local/bin/pytest projects/notekeeper -q
/root/.local/bin/pytest projects/textkit -q
/root/.local/bin/pytest projects/command-contract -q
/root/.local/bin/pytest projects/async-command -q
/root/.local/bin/pytest projects/in-process-async-command -q
/root/.local/bin/pytest projects/process-runtime-strategy -q
/root/.local/bin/pytest projects/runtime-boundary -q
/root/.local/bin/pytest projects/dev-hq-vertical-slice -q
/root/.local/bin/pytest projects/dev-hq-stage04-05-agent-team-poc-v1 -q
/root/.local/bin/pytest --collect-only -q  (repo 전체 수집 시도)
```

`pip3 install pytest`가 없어 `/root/.local/bin/pytest`(사전 설치된
바이너리)를 사용했다 — 별도 설치는 하지 않았다.

### 2.2 구문 검증(py_compile)

`archive/`, `__pycache__`, `.git`을 제외한 **379개** `.py` 파일 전체를
`python3 -m py_compile`로 개별 실행. **구문 오류 0건.**

### 2.3 Import 오류 / 전체 수집 시도

`pytest --collect-only -q`(repo root)를 시도한 결과 **728개 테스트
수집 + 18개 수집 오류(ImportError)**. 오류 18건의 원인은 전부 다음
둘 중 하나로 확인됨(코드 결함 아님):

| 원인 | 해당 파일 수 | 근거 |
|---|---|---|
| `langgraph` 모듈 미설치(이 샌드박스 환경) | 12개(`projects/workflow-adapter-*-v1/`, `omniroute-thin-engine-caller-v1` 등) | `ModuleNotFoundError: No module named 'langgraph'` — Freeze/Deferred 상태의 실험 PoC이며 optional dependency |
| `archive/v1/` 레거시 코드(명시적으로 Frozen/Archived) | 6개(`archive/v1/tests/...`) | 저장소 자체가 `archive/`를 유지보수 대상에서 제외(Frozen Starter Kit) |

두 원인 모두 "실제 실행 대상 코드(HQ 활성 구현)"의 결함이 아니라
"환경에 optional dependency가 없거나, 애초에 검증 대상이 아닌
archive 코드"다.

### 2.4 실제 테스트 실행 결과 (활성 코드 스위트)

| 스위트 | 결과 |
|---|---|
| `hqs/development/mvp/tests/` | **364 passed, 6 skipped** |
| `hqs/investment/tests/` | **24 passed** |
| `core/execution/`(mvp_0001~0006, Structure v1 Frozen Kernel Track) | **55 passed** |
| `projects/dashboard-shell-mvp/tests/` | **58 passed** |
| `projects/unified-dashboard` | 27 passed |
| `projects/notekeeper` | 52 passed |
| `projects/textkit` | 32 passed |
| `projects/command-contract` | 11 passed |
| `projects/async-command` | 14 passed |
| `projects/dev-hq-stage04-05-agent-team-poc-v1` | 14 passed |
| `projects/in-process-async-command` | 10 passed, **3 failed** |
| `projects/process-runtime-strategy` | 9 passed, 2 skipped, **1 failed** |
| `projects/runtime-boundary` | 10 passed, **3 failed** |
| `projects/dev-hq-vertical-slice` | 6 passed, 2 skipped, **1 failed** |
| **합계(실행분)** | **686 passed, 10 skipped, 8 failed** |

**결론**: 활성 유지보수 대상 4개 스위트(`hqs/development/mvp`,
`hqs/investment`, `core/execution`, `dashboard-shell-mvp`, 합계
501 passed, 6 skipped)는 **전부 통과, 실패 0건**. 실패 8건은 전부
"Runtime/Process 경계 실험" 계열 PoC 디렉터리 4곳에 집중되어 있다
(§2.5).

### 2.5 발견된 테스트 실패의 근본 원인 (전수 진단)

8건 전부 **동일한 근본 원인 패턴** — 이 PoC들이 "다른 테스트 스위트를
서브프로세스로 실행해 그 pytest 결과(통과 개수)를 자기 assertion의
golden value로 하드코딩"하는데, 참조 대상 스위트의 테스트 개수가
그 이후 정상적으로 늘어나면서(기능 추가) 하드코딩된 개수가 stale해진
것이다. 코드 자체의 동시성/경계 로직은 전부 정상 동작했다(상태 전이,
non-blocking 시작, 격리 등은 모두 통과) — 실패한 것은 "몇 개
통과했는가"라는 숫자 assertion뿐이다.

| 파일:라인 | 하드코딩된 기대값 | 실제값(이번 세션 측정) | 참조 대상 |
|---|---|---|---|
| `projects/runtime-boundary/tests/test_runtime_boundary.py:19`("16 tests"), `:45,:53,:135` | `(16, 0)` | `(24, 0)` | `hqs/investment/tests`(현재 24개, §2.4에서 직접 확인) |
| `projects/in-process-async-command/tests/test_inprocess_async_command.py:37,56,69` | `16` | `24` | 상동 |
| `projects/process-runtime-strategy/prs_dev_validation.py:15`(`EXPECTED_PASSED["mvp_0001"]=3`) → `test_process_runtime_strategy.py:49` | `(3, 0)` | `(1, 0)` | `hqs/development/mvp/tests/test_mvp_0001.py`(현재 1 passed + 2 skipped — 환경상 real-engine 게이트로 2건 skip) |
| `projects/dev-hq-vertical-slice/vs_dev_hq_adapter.py:15`(`"mvp_0001": 3`) → `test_vertical_slice.py:65` | `(3, 0)` | `(1, 0)` | 상동 |

**심각도**: Low. 근거: (a) 4개 파일 모두 "Runtime/Process 실행 전략"을
탐색한 v2.0 이전 PoC 산출물이며 `hqs/development/mvp`·
`hqs/investment`·`core/execution`·production API(`dashboard-shell-mvp`)
등 실제 서비스 코드가 아니다, (b) 실패가 기능 결함이 아니라 "다른
스위트의 테스트 개수 변화를 추적하지 못한 하드코딩 값" 하나뿐이다,
(c) Architecture/Contract/Baseline에 어떤 영향도 주지 않는다.
**수정 필요 여부**: 필요(테스트가 실패 상태로 방치되어 있으면 향후
회귀 탐지 신뢰도가 떨어짐) — 그러나 이번 세션은 검증 전용이므로
수정하지 않는다. §5 "다음 작업 제안"에 기록한다.

---

## 3. 문서 검증

### 3.1 RFC / ADC / ADR

| 검증 항목 | 결과 |
|---|---|
| 파일명 ID ↔ 제목 ID 일치 | `docs/decisions/{rfc,adc,adr}/`, `docs/governance/adc/`, `docs/architecture/core/`, `docs/core/execution-layer/` 전수 재확인(이전 세션과 동일 스크립트 재실행) — **불일치 0건** |
| 중복 ID | 트리 간 번호 재사용(RFC/ADC/ADR-0002 등)은 기존에 이미 확인·기록된 사실(`RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md`, 2026-09-20 PR #209에서 위치 C 누락을 정정하고 "self-disambiguated" 표현을 정확한 표현으로 수정함 — 이번 세션 시작 시 이 파일이 그렇게 갱신된 상태였음을 확인). **동일 도메인 내 진짜 중복은 없음.** |
| 명시적 내부 참조 유효성 | `docs/decisions/` 141개 문서 기준 dangling reference 0건(기존 검증 재확인) + 이번 세션에서 **repo 전체(1,252개 .md, archive 제외)**로 확대 재검사 — 백틱 인용 경로 기준 **39건의 "존재하지 않는 경로"** 발견, 그러나 **전수 확인 결과 전부 legacy path 역사적 인용**(`docs/02_rfc/`, `docs/03_adc/`, `docs/04_adr/`, `docs/01_architecture/`, `docs/01_mvp/` — Structure v1 Migration 이전 경로를 "당시 기록 그대로 보존"하는 저장소 컨벤션) 또는 템플릿 placeholder(`RFC-XXXX.md` 등) 또는 저자의 의도적 축약(`VALIDATION-0002-...md`)이었다 — **실제 오류 0건**. 예외 1건: `docs/architecture/core/ADC-0023-...md:400`이 `archive/v1/docs/adr/0007-workflow-execution-model.md`를 인용하며 `archive/v1/` 접두사를 빠뜨림(다른 15곳은 전부 접두사 포함) — 경로 자체(`archive/v1/...`)는 실존하므로 "깨진 링크"는 아니고 "표기 누락"에 해당(§3.4 발견 문제 목록에 기록) |
| RFC·ADC·ADR 역할 구분 | `docs/research/RFC-ROLE-BOUNDARY-REVIEW-0001.md`(PR #209, 2026-09-20)가 6개 RFC의 `## Decision` 절을 전수 대조: **RFC-0007만 역할 위반 확인**(ADC 판정을 인용하지 않고 RFC 스스로 최종 결론을 내림), RFC-0009/0010/0011, RFC-0031/0032는 "ADC 판정 인용" 형태로 위반 아님. 이번 세션이 원문(RFC-0007 §Decision, 173~189행)을 재열람해 그 결론을 **재확인**했다(main 현재 상태 — PR #210이 Role Note 추가로 수정 예정이나 아직 미병합) |
| ADC Recommendation ↔ ADR Decision 혼동 | `ADC-0006`(Decision "B — Conditional Accept" + 별도 "Implementation Boundary"), `ADC-0009`(판단별 "Recommendation"과 "Final Judgment" 분리), `ADC-0010`(Candidate 비교/Recommendation과 "종합 Decision" 분리)을 재열람 — 혼동 사례 없음 |
| 번호·링크·Architecture 결론 임의 변경 여부 | `git log`로 `BASELINE.md` 수정 이력(§4.1) 및 RFC/ADC/ADR 파일들의 최근 변경(PR #207~#210)을 대조 — 모두 신규 파일 추가 또는 명시적 근거를 단 최소 수정(PR #209의 pipe-escape, RFC-0011 표 줄바꿈 수정)뿐, 기존 결론 재작성 없음 |

### 3.2 Decision Group Registry

| 항목 | 결과 |
|---|---|
| Registry 파일 존재 | `docs/governance/DECISION-GROUP-REGISTRY.md` 존재 확인 |
| DG ID 중복 | `DG-0001`(4회), `DG-0002`(4회) — 각 4회는 요약 표 1 + 섹션 헤더 1 + 본문 인용 2로 일관 — 중복 등록 없음(스크립트 재확인) |
| 참조 경로 실존 여부 | Registry 본문의 백틱 인용 경로 전수 재확인 — **누락 0건** |
| 추측성 매핑 여부 | DG-0001(RFC-0006→ADC 2건→ADR 2건), DG-0002(RFC-0024~30→ADC-0032/33→ADR-0018) 모두 원문 인용 근거 보유(이전 세션에서 확인, 이번 세션 재확인) — 추측 매핑 없음 |
| 기존 문서와의 관계 기록 정확성 | PR #209가 두 그룹의 "Relationship Evidence" 필드에서 이스케이프되지 않은 `\|`를 `\\|`로 수정(표 셀 파싱 오류 예방) — 내용 자체는 변경 없이 순수 Markdown 문법 수정임을 diff로 확인 |

### 3.3 Markdown / 링크

| 항목 | 결과 |
|---|---|
| Markdown 표 문법 오류 | 이번 세션이 repo 전체(1,252개 .md)를 대상으로 "백틱 코드 스팬 안에 이스케이프되지 않은 `\|`가 표 셀 안에 있는" 패턴을 스캔 — **3건 발견**(§3.4). PR #209가 이미 고친 2건(Registry)과 **동일한 위험 패턴**이나 별도 파일 |
| 깨진 상대 경로 링크(`[text](path)` 형식) | repo 전체 스캔 — **0건** |
| 존재하지 않는 문서 참조(백틱 인용) | §3.1에서 서술 — 실질 오류 0건, 표기 누락 1건 |
| 템플릿과 실제 문서의 구조적 불일치 | PR #207 템플릿(`RFC-TEMPLATE.md`, `ADC-TEMPLATE.md`, `ADR-TEMPLATE.md`, `OPEN-DECISION-REGISTER-TEMPLATE.md`)은 신규 문서용이며 기존 문서에 소급 적용하지 않기로 이미 명시(PR #207 본문) — 기존 문서와의 "불일치"는 애초에 기대되지 않는 상태이므로 위반 아님 |
| Baseline 문서 직접 수정 여부 | §4.1에서 별도 확인 |

### 3.4 발견된 문서 문제 (신규, 이번 세션에서 발견)

1. **`docs/architecture/core/VALIDATION-0001-kernel-reference-architecture.md:63`** — 표 셀 안 백틱 스팬에 이스케이프되지 않은 `\|` 포함: `` `| H-2 | Builder 내부 구조 |` ``. 이 셀은 "BASELINE.md의 옛 표현을 인용"하는 예시이며, 렌더러가 백틱 안의 `|`를 셀 구분자로 오인식할 경우 표가 깨질 수 있다(PR #209가 동일 위험 패턴을 이미 2건 수정한 전례와 동일 성격). 심각도: Low(가독성 문제, 내용 손실 없음). 수정 필요: 예(권장, 이번 세션은 수행하지 않음).
2. **`projects/workflow-adapter-reversibility-v2/EVIDENCE.md:60`**, **`docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md:94`** — 표 셀 안 백틱 스팬에 정규식 리터럴 `'langgraph|langchain'`이 이스케이프 없이 포함. 동일 위험 패턴, 심각도 Low.
3. **`docs/architecture/core/ADC-0023-workflow-engine-port-contract-surface-and-engine-seam-resolution.md:400`** — `archive/v1/docs/adr/0007-workflow-execution-model.md`를 인용하며 `archive/v1/` 접두사 누락(다른 15곳은 정상 인용). 실제 파일은 존재하므로 깨진 링크는 아니나 표기 오류. 심각도: Low.

이 3건 모두 **Architecture 결론이나 Decision 내용에는 영향이 없다** —
순수 표기(Markdown 문법·경로 접두사) 문제다.

### 3.5 이미 알려진 문서 이슈(재확인만, 신규 아님)

- RFC-0007 role 위반(§3.1) — PR #210이 수정 예정, 미병합.
- `HANDOVER.md`의 마지막 테스트 기준선 표기가 "186 passed, 6 skipped"
  로 남아 있으나 실제 현재값은 "364 passed, 6 skipped"(§2.4로 직접
  재확인) — PR #210이 "테스트 기준선(현재)" 행 추가로 수정 예정,
  미병합. **`main`에는 아직 이 정정이 반영되지 않았다.**
- `ADC-0010`이 스스로 정한 "Governance 승인 → 별도 구현 세션" 순서와
  실제 실행 순서(동일 세션·동일 PR 내 6분 29초 뒤 즉시 구현)의
  불일치 — `ADC-0010-IMPLEMENTATION-SEQUENCE-COMPLIANCE-REVIEW-0001.md`
  (PR #209)가 이미 medium 심각도로 기록, Architecture/Baseline 영향
  없음으로 판정됨. 이번 세션이 그 판정 근거(Registry가 신규 파일만
  추가했는지 여부)를 재확인했고 이견 없음.

---

## 4. Architecture / Contract 검증

### 4.1 `docs/architecture/baseline/BASELINE.md` 수정 이력

`git log --oneline --follow`로 전체 이력 확인 — 저장소 대규모
초기 병합(`15ac209`) 이후 **5건**의 후속 수정만 존재하며, 각 커밋
메시지가 전부 특정 ADR/ADC를 근거로 명시한다:

```
54c7ed5 RFC-0031/ADC-0034/ADR-0019: LangGraph 승인된 비강제 구현 전략 확정
0e53301 docs(architecture): RFC-0027 Multi-Agent Runtime Contract Candidate Boundary (Phase D)
fcba0e8 docs(architecture/core): OmniRoute Model Routing/Engine Adapter Governance chain (ADC-0027~0031, ADR-0015~0017)
72bd513 docs(architecture): ADR-0014 — Gate (B) 2차 부분 완화(E6/L-B) Baseline 반영, BASELINE v1.18
```

**결론**: 근거 없는 직접 수정은 발견되지 않았다 — RFC → ADC → ADR
절차 위반 없음.

### 4.2 Development HQ Baseline / Public Contract

- `hqs/development/HANDOVER.md`(Development HQ의 사실상 Baseline
  겸 현재 상태 문서)는 이번 검증 기간 중 코드/Contract 변경과
  무관하게 "기록 정정"(HANDOVER 자체도 PR #210에서 테스트 기준선
  숫자만 추가 예정)만 있었다 — Public Contract에 해당하는 함수
  시그니처·API 변경은 없음(§2.2 py_compile 전수 통과, §2.4 테스트
  전수 통과가 간접 근거).
- Issue #206/PR #207~#210 전체에서 코드 변경은 **0건**(전부 문서
  신규 추가 또는 표기 수정) — Development HQ Baseline 자체를 건드린
  적이 없다.

### 4.3 RFC → ADC → ADR Governance 절차 위반 여부

- §3.1에서 확인한 RFC-0007의 role 위반(RFC 자신이 최종 판단 서술)은
  **절차 위반의 흔적**이지만, 실제 최종 결정은 `ADC-0005`가 별도로
  내렸고(§3.1 재확인, `ADC-0005` 원문의 4건 Accept/Reject/Defer
  판정 존재) `BASELINE.md`에는 그 ADC-0005 판정을 근거로 한 항목만
  반영되어 있다 — **절차 자체(RFC→ADC→ADR)는 실제로는 지켜졌고,
  RFC 파일 표기만 그 사실을 정확히 반영하지 못한 상태**다.
- `ADC-0010`의 승인-순서 불일치(§3.5)도 동일한 성격 — 결과물
  (Registry, 신규 문서 추가만)은 Architecture Baseline에 영향을
  주지 않았으므로 절차 위반이 실질적 위험으로 이어지지 않았다.

### 4.4 Architecture 변경이 있었는데 관련 문서가 없는 경우

발견되지 않음. §4.1의 5건 BASELINE 수정 모두 대응하는 ADR이 커밋
메시지와 본문에 명시되어 있다.

### 4.5 단순 문서 정리 vs 실제 Architecture 변경 구분

PR #207(템플릿), #208(조사/ADC-0010/Registry/재검증), #209(표기
정정+검토 문서)는 전부 **문서 전용**이며 Architecture/Contract
변경은 각 PR 본문에서 "No"로 명시되고 이번 검증에서도 코드 diff
없음으로 재확인됐다. PR #210(미병합)도 동일(RFC-0007 Note 추가 +
HANDOVER 기록 정정, 코드 변경 없음).

---

## 5. 변경 금지 사항 준수 확인

이번 세션은 다음을 수행하지 **않았다**(전부 확인):

- 파일 이동/재번호화: 없음
- 기존 RFC/ADC/ADR 내용 수정: 없음(`git status --short` 최종 확인,
  이 보고서 파일 1개만 신규 추가)
- 링크 추측 수정: 없음
- 테스트 실패 무시/삭제: 8건의 실패를 §2.5에서 근본 원인까지
  진단해 그대로 기록했다 — 삭제하거나 skip 처리하지 않았다
- Architecture Baseline 직접 수정: 없음
- 근거 없는 Registry 항목 추가: 없음(Registry 파일 자체를 열람만
  했고 수정하지 않음)
- 신규 기능 구현: 없음
- 검증 결과 과장: §2.4/§2.5에서 8건 실패를 "발견된 문제 없음"으로
  덮지 않고 원인·파일·줄 번호와 함께 명시했다

---

## 최종 보고

### 1. 무엇을 검증했는가

`main`(HEAD `412330b`) 전체를 대상으로: (a) 활성 코드 14개 테스트
스위트 직접 실행 + `py_compile` 379개 파일 전수 + repo 전체
`pytest --collect-only` 시도, (b) `docs/decisions/`·
`docs/governance/adc/`·`docs/architecture/core/`·
`docs/core/execution-layer/`의 RFC/ADC/ADR 141개 문서 재검증(파일명-ID,
중복, 내부 참조) + Decision Group Registry 재검증, (c) repo 전체
1,252개 Markdown 파일에 대한 표 문법·상대 링크·백틱 경로 인용
전수 스캔, (d) `BASELINE.md` 수정 이력 및 Governance 절차 준수 여부.

### 2. 무엇이 확인됐는가

- **테스트**: 활성 유지보수 코드(501 passed, 6 skipped, 실패 0) 전부
  통과. 전체 실행분 686 passed, 10 skipped, **8 failed**(전부
  Runtime/Process 경계 탐색용 PoC 4개 디렉터리에 국한, 근본 원인은
  "다른 스위트의 테스트 개수 변화를 추적하지 못한 하드코딩 golden
  value" 하나로 수렴).
- **구문 검증**: 379개 파일 전수 `py_compile` 통과, 오류 0건.
- **문서 검증**: RFC/ADC/ADR 파일명-ID 불일치 0건, 진짜 중복 ID
  0건(도메인 간 번호 재사용은 기존에 이미 문서화·해명됨), 내부
  참조 dangling 0건(legacy path 역사적 인용만, 검증 완료).
- **링크 검증**: `[text](path)` 형식 링크 0건 오류. 백틱 인용
  경로는 repo 전체 39건이 "누락"으로 잡혔으나 전수 확인 결과
  전부 legacy path 보존 관례 또는 의도적 축약이며 실질 오류 없음.
- **Governance 검증**: `BASELINE.md`의 모든 수정이 ADR 근거를
  가짐(절차 준수). RFC-0007의 role 표기 위반은 이미 알려져 있고
  실제 최종 결정 경로(ADC-0005)는 정상 작동했음을 재확인.
- **Architecture/Public Contract 영향**: 코드 diff 없음(문서 전용
  변경만 존재) — No.

### 3. 발견된 문제

| # | 파일 경로 | 관련 줄/명령어 | 문제 내용 | 심각도 | 수정 필요 |
|---|---|---|---|---|---|
| 1 | `projects/runtime-boundary/tests/test_runtime_boundary.py` | 19, 45, 53, 135 | `hqs/investment/tests` 테스트 개수 하드코딩(16)이 실제 현재값(24)과 불일치해 3건 실패 | Low | 예(별도 작업) |
| 2 | `projects/in-process-async-command/tests/test_inprocess_async_command.py` | 37, 56, 69 | 동일 원인(16 vs 24)으로 3건 실패 | Low | 예(별도 작업) |
| 3 | `projects/process-runtime-strategy/prs_dev_validation.py` + `tests/test_process_runtime_strategy.py` | `prs_dev_validation.py:15`, `test_process_runtime_strategy.py:49` | `test_mvp_0001.py` 기대 통과 수(3) vs 실제(1 passed+2 skipped) 불일치로 1건 실패 | Low | 예(별도 작업) |
| 4 | `projects/dev-hq-vertical-slice/vs_dev_hq_adapter.py` + `tests/test_vertical_slice.py` | `vs_dev_hq_adapter.py:15`, `test_vertical_slice.py:65` | 동일 원인으로 1건 실패 | Low | 예(별도 작업) |
| 5 | `docs/architecture/core/VALIDATION-0001-kernel-reference-architecture.md` | 63 | 표 셀 내 백틱 스팬에 이스케이프 없는 `\|` — 표 렌더링 위험(PR #209가 고친 것과 동일 패턴) | Low | 예(선택, 가독성) |
| 6 | `projects/workflow-adapter-reversibility-v2/EVIDENCE.md` | 60 | 동일 패턴(`langgraph\|langchain` 정규식 리터럴) | Low | 예(선택) |
| 7 | `docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-0001.md` | 94 | 동일 패턴 | Low | 예(선택) |
| 8 | `docs/architecture/core/ADC-0023-workflow-engine-port-contract-surface-and-engine-seam-resolution.md` | 400 | `archive/v1/` 접두사 누락(경로 자체는 실존, 표기만 불완전) | Low | 예(선택) |

**이미 알려져 있고 PR #210(미병합)이 처리 중인 항목**(신규 문제
아님, §3.5 참고): RFC-0007 role 표기, `HANDOVER.md` 테스트 기준선
stale 표기.

**이미 기록되었고 Architecture 영향 없음으로 판정된 항목**(신규
아님): `ADC-0010` 구현 순서 불일치(medium, PR #209에서 기록 완료).

### 4. 아직 검증하지 못한 항목

- `projects/workflow-adapter-*-v1`, `omniroute-thin-engine-caller-v1`
  등 12개 파일이 `langgraph` 모듈 미설치로 수집조차 되지 않았다 —
  이 샌드박스에 해당 패키지를 설치하지 않았으므로(근거 없는 환경
  변경을 피하기 위해) 이 PoC들의 런타임 동작은 이번 세션에서
  **검증 불가**로 남긴다.
- `archive/v1/` 6개 테스트 파일은 저장소 컨벤션상 유지보수 대상이
  아니므로(Frozen Starter Kit) 의도적으로 실행하지 않았다 —
  실패 여부 자체를 판단하지 않는다.
- Markdown 렌더링 실제 결과(GitHub 웹 UI에서 표가 실제로 깨지는지)는
  이 환경에서 브라우저 렌더링을 확인할 수단이 없어 **정적 패턴
  매칭으로만 판단**했다 — §3.4의 3건이 실제로 GitHub에서 깨지는지는
  미확인(패턴이 PR #209가 이미 "위험하다고 판단해 고친" 것과
  동일하므로 같은 기준으로 Low 위험 표기했다).
- 저장소의 `.github/workflows` 등 CI 설정 파일이 존재하는지, 존재한다면
  이번 로컬 실행과 CI 실행 결과가 같은지는 확인하지 않았다(`.github`
  디렉터리 자체를 이번 세션에서 조회하지 않음).

### 5. 다음 작업 제안

1. (Low, 독립 수행 가능) `projects/runtime-boundary`,
   `projects/in-process-async-command`,
   `projects/process-runtime-strategy`,
   `projects/dev-hq-vertical-slice`의 하드코딩된 golden test-count
   값을 실제 참조 스위트의 현재 값으로 갱신하거나, 하드코딩 대신
   "0건 실패"만 확인하는 방식으로 assertion을 완화하는 별도 Task.
   근거: §2.5, §3의 발견 #1~4.
2. (Low, 선택) §3.4 발견 #5~8의 Markdown 표기 수정(pipe escape 4곳
   + prefix 보정 1곳) — PR #209가 이미 시작한 것과 동일한 정리
   작업의 연장.
3. (이미 진행 중) PR #210 병합 — RFC-0007 role 표기, HANDOVER 테스트
   기준선 정정. 이번 검증이 그 필요성을 재확인했다.
4. 검증만으로 해결되지 않는 항목: 없음 — 이번 세션에서 발견된 모든
   문제는 성격상 "별도 최소 편집 Task"로 분리 가능하며, Architecture/
   Baseline 재검토가 필요한 항목은 없었다.

---

## 별도 상태 표시

- Architecture 변경 여부: **No**
- Public Contract 변경 여부: **No**
- Branch 상태: `claude/main-branch-full-validation-0001`(이 보고서
  전용 신규 브랜치, `main` HEAD `412330b`에서 분기)
- HEAD: `412330b`(검증 대상) → 이 보고서 커밋 후 해당 브랜치 HEAD 갱신
- Working tree: 이 보고서 파일 1개 추가 외 Clean
- Test 결과: **686 passed, 10 skipped, 8 failed**(활성 유지보수
  코드는 501 passed, 6 skipped, 0 failed) + 18 collection error
  (환경 의존성/archive, 코드 결함 아님)
- 문서 검증 결과: RFC/ADC/ADR 파일명-ID 불일치 0, 진짜 중복 ID 0,
  dangling reference(실질) 0, Markdown 표 문법 위험 4건(Low),
  인용 표기 누락 1건(Low), 알려진 role/기준선 표기 이슈 2건(PR #210
  처리 중)
- PR 생성 필요 여부: **예** — 이 검증 보고서를 `main`에 반영하기
  위한 PR 생성 권장(문서 전용, Architecture/Contract 영향 없음)

## Related Documents

| Type | ID | Relationship |
|---|---|---|
| Prior Validation | (세션 내 언급된) 이전 Main Branch Full Validation | 이번 검증이 재확인·확장하는 선행 세션 |
| Review | `docs/research/RFC-ROLE-BOUNDARY-REVIEW-0001.md` | RFC role 위반 조사(§3.1, §3.5 인용) |
| Review | `docs/research/ADC-0010-IMPLEMENTATION-SEQUENCE-COMPLIANCE-REVIEW-0001.md` | ADC-0010 순서 불일치(§3.5 인용) |
| Investigation | `docs/research/RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md` | 번호 충돌 근거(§3.1 인용) |
| Registry | `docs/governance/DECISION-GROUP-REGISTRY.md` | §3.2 검증 대상 |
| Issue | #206 | 상위 요청 |
| PR | #207, #208, #209(Merged), #210(Open) | 검증 대상 이력 |
