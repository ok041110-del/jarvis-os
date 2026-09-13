# Archive Cleanup Revalidation — main(9984408) 기준 재검증

## Summary

- `docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`
  (이하 "선행 조사")의 DEFER 두 항목 — (1) `projects/` 1회성
  Dogfooding/PoC 27개의 `projects/archive/` 이동 검토, (2)
  `mvp/cli.py`/`run_mvp_0001`의 공식 Deprecated 문서화 여부 — 를
  현재 `main`(9984408) 기준으로 재검증했다.
- **재검증 결론**: 두 DEFER 항목 모두 **정리(MOVE/DELETE) 불가**로
  확정한다. 조사만 수행했고 파일을 이동/삭제하지 않았다.
- 선행 조사 이후(`865d41a`→`9984408`) 커밋 중 archive/deprecated/
  obsolete/superseded/legacy/prototype/poc/stage_0N 패턴에 해당하는
  파일 변경은 **0건**이며, 신규 파일명 패턴(`*_old*`, `old_*` 등)도
  **0건** — 선행 조사가 다룬 대상 집합 자체가 그대로 유효하다.

## 1단계 — 재조사 결과

패턴(archive/deprecated/obsolete/superseded/legacy/prototype/poc/
mvp/stage_01~05) 검색 결과는 선행 조사와 동일했다(신규 후보 없음).
`archive/v1/`(146개), `docs/decisions/{rfc,adc,adr}/`,
`stages/04_implementation/architecture_validation/`,
`stages/06_devops_release/README.md`, MVP 프로토타입 6개 파일은
선행 조사의 판정(B/C, 전부 KEEP)이 현재도 그대로 유효함을
재확인했다(git log로 해당 경로 무변경 확인).

## 2단계 — 참조 검증: `projects/` 27개 DEFER 후보

45개 `projects/` 디렉터리 전체에 대해 (a) 다른 프로젝트의
`sys.path`/`importlib` sibling-import, (b) `docs/research/*.md` 및
`docs/architecture/core/*.md`(RFC/ADC/ADR/EVIDENCE/GOVERNANCE-REVIEW)
경로·티커 인용, (c) `hqs/investment/dogfooding/*/EVIDENCE.md` 인용을
전수 확인했다.

**핵심 발견**: 27개 DEFER 후보 **전원**이 Governance/Evidence
문서에서 실제로 인용되고 있었다. 디렉터리 경로 문자열(`projects/<name>`)
로는 참조가 안 잡히는 5개(`dividend-stock-analysis-epd`,
`dividend-stock-analysis-realty-income`,
`dividend-stock-analysis-toyota`, `etf-analysis-uup`,
`etf-analysis-vnq`)도 티커 심볼 단위로 재확인한 결과:

| 프로젝트 | 인용 문서 |
|---|---|
| `dividend-stock-analysis-epd`(EPD) | `INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001.md`, `INVESTMENT-HQ-TRADER-DECISION-DISCRIMINATION-DOGFOODING-0001.md` |
| `dividend-stock-analysis-realty-income`(Realty Income) | 위 2건 + `INVESTMENT-HQ-ETF-LOOKTHROUGH-EXPOSURE-DOGFOODING-0001.md` + **`ADC-0017-multi-task-result-store-integrity-boundary.md`** + **`INVESTMENT-HQ-V1.0-FREEZE-0001.md`**(Freeze 문서) |
| `dividend-stock-analysis-toyota`(Toyota) | 위 2건 |
| `etf-analysis-uup`(UUP) | `INVESTMENT-HQ-ETF-LOOKTHROUGH-EXPOSURE-DOGFOODING-0001.md`, `INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001.md`, `INVESTMENT-HQ-TRADER-DECISION-DISCRIMINATION-DOGFOODING-0001.md`(3개 극단 사례 중 하나로 명시 인용) |
| `etf-analysis-vnq`(VNQ) | 위 3건과 동일(3개 극단 사례 중 하나로 명시 인용) |

나머지 22개(`dividend-stock-analysis-{jnj,ko,nestle,pg}`,
`etf-analysis-{agg,gld,qqq,schd}`, `stock-analysis-*` 5개,
`dev-hq-timeout-recovery-prototype`,
`synthesis-trader-expansion-prototype`,
`kernel-parallel-execution-prototype`,
`investment-hq-checkpoint-detection-prototype`,
`dev-hq-agent-responsibility-decomposition-v1`,
`dev-hq-stage04-05-agent-team-poc-v1`,
`workflow-adapter-*` 4개, `langgraph-conditional-routing-poc-v1`,
`multi-agent-handoff-mvp-v1`, `omniroute-thin-engine-caller-v1`,
`notekeeper`, `textkit`, `development-hq-devkit`)는 경로 문자열
자체가 `docs/research/*.md`와 `docs/architecture/core/`의 RFC/ADC/ADR/
EVIDENCE/GOVERNANCE-REVIEW 문서에서 직접 인용됨을 확인했다(상세는
스크래치패드 `project_refs.txt` 원본 grep 결과 참고, 본 문서에는
결론만 반영).

## 3단계 — 정리 결정

### DEFER 항목 1: `projects/` 27개 → `projects/archive/` 이동

**판정: MOVE 불가 (KEEP 유지)**

선행 조사 §10은 이동 전 확인 조건으로 "(a) 문서 경로 참조가 상대/
절대 경로인지, (b) 이동이 `docs/research/` 링크를 깨뜨리지 않는지"를
명시했다. 이번 재검증 결과 27개 전원이 RFC/ADC/ADR/EVIDENCE/
GOVERNANCE-REVIEW를 포함한 Governance/Evidence 문서에서 실제로
인용되고 있어, `projects/archive/`로 이동하면 다음이 즉시 발생한다:

- 이동 자체는 사용자 지시 원칙 2/3("Architecture/Governance/Evidence
  문서는 삭제하지 않는다", "역사적 Evidence는 삭제하지 않는다")을
  직접 위반하지는 않지만, 그 문서들이 인용하는 경로
  (`projects/<name>/...`)가 즉시 부정확해진다.
- 이를 바로잡으려면 RFC/ADC/ADR/`INVESTMENT-HQ-V1.0-FREEZE-0001.md`
  같은 Governance/Freeze 문서의 본문을 수정해야 하는데, 이는 이번
  작업 원칙 7("새로운 Architecture/Contract 변경을 하지 않는다")의
  범위를 벗어나고, Freeze 문서 수정은 그 자체로 별도 Governance
  판단이 필요하다.
- 즉, "이동은 안전하고 문서만 고치면 된다"가 아니라 "문서 인용
  경로를 그대로 둔 채 파일만 옮기면 Governance/Evidence 문서의
  참조 무결성이 깨진다" — 이것이 선행 조사가 §10에서 DEFER로 남긴
  바로 그 리스크가 실제로 존재함을 확인한 것이다.

**결론**: 27개 전원 **KEEP으로 재분류**(C/D: Historical Evidence,
Governance 문서가 실제로 인용 중). 물리적 이동은 Governance가
먼저 "이동 시 문서 인용을 어떻게 처리할지"(예: 인용 경로를
`projects/archive/`로 갱신할지, 인용 시점의 경로를 그대로 역사적
사실로 남길지)를 RFC/ADC 수준에서 결정한 뒤에만 실행 가능하다 —
**DEFER를 Governance 결정 없이 자체적으로 종결하지 않는다.**

### DEFER 항목 2: `mvp/cli.py` / `run_mvp_0001` 공식 Deprecated 문서화

**판정: 변경 불가 (KEEP/DEFER 유지)**

- 현재도 `hqs/development/mvp/tests/test_mvp_0001.py`가 여전히
  `run_mvp_0001`을 직접 테스트하고, `mvp/README.md`가 "MVP-0001
  원 구현 4개 파일"로 명시적으로 기술하며, `HANDOVER.md`가 이를
  완료된 원 구현으로 공식 기록하고 있어 **Active + Historical
  Evidence 상태에 변화가 없다.**
- "공식 Deprecated로 문서화할지"는 삭제/이동이 아니라 문서에
  상태 라벨을 추가하는 결정이지만, 이는 `mvp/cli.py`와
  `hqs/development/cli.py`(v2.0 트랙) 간의 선후 관계에 대한
  **Governance 판단**이며 사용자 지시 원칙 7("새로운 Architecture/
  Contract 변경을 하지 않는다")과 8("새로운 기능 구현을 하지
  않는다")에 따라 이번 순수 Cleanup 작업의 범위 밖이다.
- **결론**: 상태 불변, 파일 이동/삭제/문서 라벨링 없음. Governance
  트랙(RFC → ADC → ADR)에서 별도로 판단해야 할 사안으로 재확인만
  하고 종결하지 않는다.

## 4단계 — Implementation

**실행한 정리: 없음(0건).** DELETE 0건, MOVE 0건. 재검증 결과
Safe Cleanup Candidate(E)로 분류된 항목이 없어 실제 파일
이동/삭제를 수행하지 않았다.

## 5단계 — Validation

- 전체 참조 재검색: `projects/` 45개 디렉터리 전수 grep(경로 문자열
  + 5개 예외 항목 티커 심볼) 완료 — 위 §2 표 참고.
- `py_compile`: `hqs/`, `projects/` 하위 전체 `.py` 파일 컴파일
  확인 — **에러 0건**.
- pytest: 이 실행 환경에 `pytest` 모듈이 설치되어 있지 않아 실행하지
  못했다(`No module named pytest`) — 다만 이번 작업에서 파일을
  이동/삭제하지 않았으므로(diff 없음) 회귀 위험 자체가 없다. 실제
  코드/파일 변경이 발생하지 않았다는 사실을 이 문서와 git diff로
  확인 가능하다.
- import/workflow 무결성: 변경이 없으므로 깨질 대상이 없음.
- 기존 Evidence 문서 링크: 변경이 없으므로 깨진 링크 없음.

## 6단계 — 결과 보고

### DELETE

없음(0건).

### MOVE → `projects/archive/`

없음(0건) — 재검증 결과 27개 DEFER 후보 전원이 Governance/Evidence
문서 인용 대상으로 확인되어 이동 보류.

### KEEP

- 선행 조사 §10 KEEP 목록 전체(변경 없음): `hqs/development/`
  조사 대상, `archive/v1/`(146개), `docs/decisions/{rfc,adc,adr}/`,
  `core/`(Kernel/Execution Layer), `projects/`의 sibling-import
  5개(`openrouter-auto-selection-v1`,
  `stage05-parallel-validation-harness-v1`, `runtime-boundary`,
  `command-contract`, `unified-dashboard`), `.claude/` 전체.
- (재분류) 선행 조사에서 DEFER였던 `projects/` 27개 전체 → 이번
  재검증으로 **KEEP** 확정(Governance/Evidence 문서가 실제로 인용).
- `mvp/cli.py` / `run_mvp_0001` → KEEP 유지(Active + Historical
  Evidence, 상태 불변).

### DEFER

- `mvp/cli.py` / `run_mvp_0001`의 공식 Deprecated 문서화 여부 —
  Governance 판단 필요(이번 작업 범위 밖, 변경 없음).
- `projects/` 27개의 물리적 재배치는, 향후 Governance가
  "이동 시 RFC/ADC/ADR/Freeze 문서의 기존 경로 인용을 어떻게
  처리할지"를 먼저 결정한 뒤에만 재검토 가능 — 이번 작업에서는
  실행하지 않는다.

### 근거

- §2~§3 표 및 서술 참고. 원본 grep 전수 결과는 세션 스크래치패드에
  보관(재현 가능, repo에는 결론만 반영).

### Validation 결과

§5 참고 — 실제 변경 0건, `py_compile` 에러 0건, pytest는 환경 제약으로
미실행(변경이 없어 회귀 위험 없음).

### Architecture/Contract 변경 여부

없음. Baseline/RFC/ADC/ADR 어느 것도 수정하지 않았다.

### Governance 변경 여부

없음. 이 문서(신규 Evidence 문서 추가) 자체가 Governance 문서를
수정한 것이 아니라, 기존 조사 결과를 재검증하고 결론을 추가한
별개의 신규 기록이다.

### PR/branch 상태

- Branch: `claude/jarvis-archive-cleanup-snro5w`(`origin/main`
  9984408 기준으로 재생성).
- 파일 변경: 이 문서 추가 1건뿐, 코드/구조 변경 없음.
- PR: CLAUDE.md "PR 불필요" 기준(main에 반영할 실제 산출물 없음,
  READ-ONLY 재검증) 해당 — PR 생성 대신 사용자 승인 시 직접 반영
  가능. 사용자 판단에 따른다.

## Related

- `docs/research/STAGE-TO-TEAM-MIGRATION-ARCHIVE-CLEANUP-INVESTIGATION-0001.md`(선행 조사)
- `docs/architecture/core/ADC-0017-multi-task-result-store-integrity-boundary.md`
- `docs/architecture/core/INVESTMENT-HQ-V1.0-FREEZE-0001.md`
- `docs/research/INVESTMENT-HQ-ETF-LOOKTHROUGH-EXPOSURE-DOGFOODING-0001.md`
- `docs/research/INVESTMENT-HQ-TEAM-VALIDATION-CLOSURE-0001.md`
- `docs/research/INVESTMENT-HQ-TRADER-DECISION-DISCRIMINATION-DOGFOODING-0001.md`
- `hqs/development/HANDOVER.md`
