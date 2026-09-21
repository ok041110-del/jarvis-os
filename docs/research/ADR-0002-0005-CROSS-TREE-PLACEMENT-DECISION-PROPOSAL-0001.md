# ADR-0002~0005 교차 트리 물리 배치 — Governance Decision

## 0. 성격과 조사 범위

이 문서는 ADR-0002~0005의 물리적 배치 문제에 대한 Governance Decision을
기록한다. 기준 커밋: `origin/claude/decision-ledger-registration-74a9a1`
HEAD(`358fc36`), base `origin/main`(`94c47762`). 어떤 파일도
이동·이름 변경·삭제·alias 생성·경로 자동 치환하지 않았다.
`docs/decisions/REGISTRATION-CANDIDATES-0001.md`가 이미 3개 라운드에
걸쳐 이 문제를 조사하고 "사용자 판단 필요"로 반복 확인한 내용을
이번 라운드에서 재검증했다.

**조사 대상 정정**: 이번 작업 지시는 조사 대상을 `docs/core/
execution-layer/ADR-0002~0005-*.md`로 지정했으나, 실제 확인 결과
`docs/core/execution-layer/`에는 **`ADR-0002-execution-result-item-
schema.md` 1건만 존재**하며 ADR-0003/0004/0005는 이 디렉터리에
존재하지 않는다(`ls docs/core/execution-layer/` 직접 확인). 따라서
실제 충돌 구조는 아래 §3에서 정정된 형태로 기록한다 — 없는 파일을
있다고 가정하거나 경로를 추측해 만들지 않았다.

## 1. Problem Statement

Kernel Architecture 연구 트랙에서 Document ID `ADR-0002`~`ADR-0005`가
**서로 다른 물리적 위치에 있는, 내용이 전혀 다른 문서들**을 동시에
가리킨다. Bare ID(`grep -r "ADR-0002"`)만으로는 어느 문서를 가리키는지
특정할 수 없다.

## 2. Historical Cause

`docs/decisions/adr/ADR-0002~0005-*.md`(Kernel 내용, Development HQ
트리 디렉터리에 물리적으로 위치) 4개 문서는 자기 자신의 "선행 ADR"
필드에서 옛 경로 `docs/04_adr/ADR-0002-...`를 인용한다(예:
`ADR-0003-kernel-context-model-baseline.md`, `ADR-0004-kernel-public-
contract-baseline.md`, `ADR-0005-kernel-logical-reference-architecture-
baseline.md`가 모두 `docs/04_adr/ADR-000X`형태로 서로를 인용) — 이는
현재 저장소 어디에도 없는 옛 경로다. Structure v1.0 Migration
(`docs/decisions/adr/ADR-0006-structure-v1-migration.md`,
`ADR-0007-baseline-relocation.md`)이 이 옛 `docs/04_adr/` 트리를
`docs/decisions/adr/`로 일괄 재배치했을 때, 이 4개 초기 Kernel ADR도
Development HQ 문서들과 함께 그대로 옮겨진 것으로 판단된다. 이후
`docs/architecture/core/` 트리가 Kernel 연구 트랙 전용으로 신설되며
ADR 번호를 `0001`부터 다시 채번하기 시작해, 같은 번호(`0002`~`0005`)가
우연히 재사용됐다. 두 트리 모두 각자의 트리 안에서는 채번 규칙을
지켰으므로, 어느 쪽도 잘못 채번한 것은 아니다 — 이는 저장소가
Kernel 문서를 담는 트리를 한 번 이전하고 다시 신설한, 역사적 재구조화의
부산물이다.

## 3. Current Evidence

실제 물리 파일과 Target Domain을 직접 대조한 결과는 다음과 같다.

| Document ID | 물리 경로 A | 물리 경로 B | 물리 경로 C (Execution Layer) |
|---|---|---|---|
| ADR-0002 | `docs/architecture/core/ADR-0002-execution-layer-module-baseline.md`(Kernel) | `docs/decisions/adr/ADR-0002-core-to-kernel-terminology-unification.md`(Kernel, 교차 트리) | `docs/core/execution-layer/ADR-0002-execution-result-item-schema.md`(Execution Layer, 별개 Target Domain) |
| ADR-0003 | `docs/architecture/core/ADR-0003-single-execution-unit-dispatch-isolation-baseline.md`(Kernel) | `docs/decisions/adr/ADR-0003-kernel-context-model-baseline.md`(Kernel, 교차 트리) | 없음(이 디렉터리에 ADR-0003 부재) |
| ADR-0004 | `docs/architecture/core/ADR-0004-execution-host-naming-baseline.md`(Kernel) | `docs/decisions/adr/ADR-0004-kernel-public-contract-baseline.md`(Kernel, 교차 트리) | 없음(이 디렉터리에 ADR-0004 부재) |
| ADR-0005 | `docs/architecture/core/ADR-0005-execution-host-implementation-strategy-baseline.md`(Kernel) | `docs/decisions/adr/ADR-0005-kernel-logical-reference-architecture-baseline.md`(Kernel, 교차 트리) | 없음(이 디렉터리에 ADR-0005 부재) |

**ADR-0002는 3개의 서로 다른 물리 파일**(물리 경로 A/B/C 전부 실존),
**ADR-0003~0005는 각각 2개의 서로 다른 물리 파일**(물리 경로 A/B만
실존, C는 없음)이 실제로 존재한다. 물리 경로 C(`docs/core/
execution-layer/`)는 Target Domain 자체가 `Execution Layer`로 물리
경로 A/B(둘 다 `Kernel`)와 다르므로, 원장의 전역 유일 키(Document
ID + Target Domain + Source Path) 정의로 이미 명확히 구분된다 —
혼동 위험은 물리 경로 A와 B 사이(둘 다 Kernel Target Domain)에만
실질적으로 존재한다.

세 원장(`docs/decisions/rfc.md`/`adc.md`/`adr.md`)은 이 상황을 이미
정확히 반영하고 있다 — `adr.md`는 물리 경로 A/B 각 행의 Status
셀에 "교차 트리"임을 명시하고, §2 필드 설명에 "전역 유일성은
Document ID + Target Domain + Source Path 조합으로만 보장된다"고
이미 정정해 두었다. `docs/research/OPEN-ISSUES-PR214-VERIFICATION-
0001.md`(이번 세션 선행 감사)가 원장 162행 전수 검증에서 이 4쌍을
정상적인 교차 참조로 재확인했으며, 실제 중복 등록·파일 부재는
0건이었다.

**Architecture/Public Contract 영향**: 없음 — 이 문제는 순수하게
문서의 물리적 위치 문제이며, 어떤 Kernel Module/Public Contract의
내용도 바꾸지 않는다.

## 4. Considered Alternatives

1. **현상 유지** — 파일을 옮기지 않고, 원장의 Source Path 기반
   구분에만 의존한다.
2. **물리 이동** — `docs/decisions/adr/ADR-0002~0005-*.md` 4개 파일을
   `docs/architecture/core/`로 옮긴다(슬러그가 이미 서로 달라 파일명
   충돌은 없다).
3. **헤더 주석 추가** — 파일 위치는 유지하되, 각 파일에 "이 ADR은
   Kernel Target Domain에 속하며 `docs/architecture/core/` 트리와
   물리적으로 분리되어 있다"는 한 문장을 추가한다.
4. **디렉터리 재편** — `docs/decisions/adr/`를 도메인별 하위
   디렉터리로 재구조화한다(저장소 전체 배치 규칙 재설계, 이번 이슈
   범위를 크게 초과).

| 대안 | 장점 | 단점 | 추적성 영향 | Governance 비용 |
|---|---|---|---|---|
| 1. 현상 유지 | 실행 위험 0. 원장이 이미 정확히 반영 중 | bare-ID grep 혼동은 계속 남음 | 원장(Source Path 키)에만 의존 — 이미 충분히 정확함 | 없음(원장 스키마 정정으로 이미 완료) |
| 2. 물리 이동 | 디렉터리 관례 일치 | git blame/history 연속성에 rename 기록 남음. 최소 10곳 이상(각 RFC/ADC의 "관련 ADR" 필드, `REGISTRATION-CANDIDATES-0001.md`, 세 원장, `BASELINE.md` 각주 등)의 경로 문자열을 동시 갱신해야 함 — 부분 갱신 시 깨진 링크 위험 | 단기 하락(이동 도중), 장기 상승 | 최소 ADC 수준 승인 필요, 실행 전 전수 참조 조사 필요 |
| 3. 헤더 주석 추가 | 실행 위험 낮음(1줄 추가) | 4개 파일 본문 수정 — "구조 보존, 본문 무수정" 원칙과 결이 다름 | 약간 상승 | RFC 불필요, 최소 사용자 승인 필요 |
| 4. 디렉터리 재편 | 장기적으로 가장 깨끗한 구조 | 범위가 이번 이슈를 크게 초과, 다수 참조 영향 | 재편 직후 하락, 이후 상승 | RFC → ADC → ADR 필수, 별도 세션 |

## 5. Selected Decision: Maintain Current Placement

**현상 유지를 채택한다.** ADR-0002~0005(물리 경로 B, `docs/decisions/
adr/`)는 현재 위치에서 이동하지 않는다.

- 교차 트리의 동일 ID는 ID 단독으로 식별하지 않고, 다음 조합으로
  식별한다: **Document ID + Target Domain + Source Path**(이미
  `docs/decisions/adr.md`/`adc.md`/`rfc.md` §2·§7에 명문화됨).
- Structure v1.0 Migration으로 인한 역사적 물리 배치 차이를 그대로
  유지한다 — 이 결정은 그 역사적 사실을 부정하거나 기존 Source
  Path를 수정하는 것이 아니다.
- 향후 실제로 파일을 이동해야 할 필요가 생기면, 별도 RFC/ADC/ADR
  또는 명시적 Governance Decision을 거친다.
- 이번 작업에서 파일 이동·rename·삭제·alias 생성·경로 자동 치환을
  수행하지 않았다(어떤 실행도 이 문서에 포함되지 않는다).

## 6. Consequences

- 원장 3종의 스키마(전역 유일 키 = Document ID + Target Domain +
  Source Path)가 이 결정의 실질적 시행 수단으로 계속 사용된다 —
  추가 조치 불필요.
- 각 RFC/ADC/ADR 문서 자신의 "관련 RFC"/"관련 ADC"/"선행 ADR" 필드가
  이미 정확한 상대/절대 경로를 담고 있어, 원장과 원문 양쪽에서
  이중으로 추적 가능한 상태가 유지된다.
- `docs/decisions/adr/`에는 Development HQ 문서와 Kernel 내용 문서가
  물리적으로 계속 혼재한다 — 디렉터리 이름만으로 도메인을 추정할 수
  없다는 사실은 앞으로도 유효하다.

## 7. Risks

- **bare-ID grep 혼동**: `grep -r "ADR-0002"` 같은 검색은 여전히
  3개 파일(§3 표)을 모두 반환한다 — 조사자가 Target Domain/Source
  Path를 함께 확인하지 않으면 잘못된 문서를 인용할 위험이 남는다.
- **신규 기여자 온보딩 비용**: 저장소를 처음 접하는 사람이 "같은
  번호 ADR"을 다른 문서로 착각할 수 있다 — 원장과 각 문서의 상호
  참조가 이 위험을 완화하지만 완전히 제거하지는 않는다.
- **디렉터리 관례 위반이 관행화될 위험**: 향후 새 Kernel 문서가
  실수로 `docs/decisions/adr/`에 추가될 수 있다(단, 신규 문서는
  `docs/architecture/core/` 채번 규칙을 따르므로 실제 위험은 낮다).

## 8. Reconsideration Conditions

다음 중 하나가 실제로 관찰되면 이 결정(현상 유지)을 재검토한다.

1. bare-ID grep 혼동으로 인한 **실제 오류**(잘못된 ADR을 인용해
   Governance 판단이 뒤바뀐 사례)가 1회 이상 발생하는 경우.
2. `docs/decisions/adr/`에 Kernel 내용 문서가 추가로 유입되어 혼재
   범위가 확대되는 경우.
3. 저장소 전체 문서 배치 규칙을 다루는 별도 RFC(디렉터리 재편, 대안
   4)가 다른 목적으로 개설되어 이 문제를 함께 해소할 기회가 생기는
   경우.

## 9. Governance Impact

없음 — 이 결정은 기존 파일을 이동·수정하지 않으며, 원장 스키마는
이전 라운드에서 이미 정정 완료된 상태를 그대로 인정한다. 새로운
Architecture Decision이나 Baseline 변경을 발생시키지 않는다. 대안
2/4를 채택하는 경우에만 별도 RFC → ADC → ADR 절차가 필요하다(§4
표 참조) — 이번 결정(현상 유지)은 그 절차를 요구하지 않는다.

## 10. Implementation Status

**실행 완료 항목**: 없음(이 결정 자체가 "이동하지 않음"이므로 실행할
파일 변경이 없다). 이 문서의 작성과 원장 상태 재확인만 이번 작업의
산출물이다.

**실행하지 않은 항목**(의도적): ADR-0002~0005 물리 이동, 헤더 주석
추가, 디렉터리 재편 — 전부 §4에서 검토했으나 §5 결정에 따라 실행하지
않는다.
