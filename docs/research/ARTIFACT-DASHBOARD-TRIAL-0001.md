# Artifact Dashboard Trial 0001 — 현재 사용 방식 기록

## 문서 성격

이 문서는 Artifact Dashboard Sync Trial의 **현재 사용 방식**만 기록하는
연구 문서다. 새 Architecture 결정이나 Contract를 만들지 않는다.
`docs/01_architecture/BASELINE.md`, `docs/03_adc/ADC.md`를 포함해 기존
Architecture/Governance 문서를 재정의하지 않는다. RFC/ADC/ADR을
생성하지 않는다. `development-hq/`, `core/` 등 Runtime 코드는 이
문서에서 건드리지 않는다.

## 현재 사용 방식

1. **Repository가 Source of Truth다.** Dashboard가 표시하는 모든
   상태는 이 Git Repository의 실제 파일 내용에서만 나온다 — Dashboard
   자체는 별도의 데이터 저장소를 갖지 않는다.
2. **Claude Code가 Repository를 검증한다.** Dashboard는 Repository를
   직접 파싱하지 않는다 — Claude Code가 실제 파일(`BASELINE.md`,
   `ADC.md`, `HANDOVER.md`, `docs/research/`, `docs/architecture/core/`
   등)을 읽고 실행(`pytest`, `git log` 등)해 사실 여부를 확인한다.
3. **`/sync`를 통해 Verified Project State를 갱신한다.** Claude Code가
   검증을 마치면 그 결과를 Verified Project State 데이터셋(VERIFIED/
   INFERRED/UNCONFIRMED/CONFLICT/N/A로 분류된 구조화 데이터)으로
   정리하고, 이 데이터셋이 Dashboard가 읽는 최신 스냅샷이 된다.
4. **Artifact는 Verified State를 보여주는 Read-only View다.**
   Dashboard 자체는 판단을 내리거나 데이터를 생성하지 않는다 — Claude
   Code가 만든 Verified Project State를 그대로 렌더링만 한다.
5. **현재 Claude Resource/Context Runtime 데이터는 N/A다.** 5H usage,
   weekly usage, context percentage 등 실제 API/Runtime 사용량 데이터에
   접근할 수단이 없으므로, 추정하지 않고 N/A로 표시한다.
6. **현재 Dashboard는 GitHub에 쓰기/commit/PR을 수행하지 않는다.**
   데이터 흐름은 Repository → Claude Code → Dashboard의 단방향이며,
   Dashboard에서 Repository로 되돌아가는 쓰기 경로는 없다.
7. **향후 Runtime/Automation 단계에서 자동 갱신을 검토한다.** 지금은
   `/sync`를 사람이 트리거하는 수동 절차이며, 자동 트리거(예: push
   이벤트 기반 자동 재조사)는 실제 필요가 확인된 뒤 별도로 검토할
   대상이다 — 이 문서가 그 설계를 확정하지 않는다.

---

## Architecture/Contract 변경 여부

**없음.** 이 문서는 기존 Architecture/Governance 문서를 재정의하지
않았고, 새 RFC/ADC/ADR을 생성하지 않았다. `development-hq/`, `core/`
등 Runtime 코드를 수정하지 않았다.
