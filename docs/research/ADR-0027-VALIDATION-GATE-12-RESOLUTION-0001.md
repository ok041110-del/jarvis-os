# ADR-0027 §10 Validation Gate #12 최종 판정 — Evidence

**Date**: 2026-09-13
**Branch**: `claude/jarvis-openrouter-validation-bin9aj`
**연결 Evidence(전부 보존, 수정하지 않음)**:
`ADR-0027-VALIDATION-GATE-EXECUTION-0001.md`(`c39eb26`),
`OPENROUTER-MIGRATION-SCOPE-GAP-IDENTIFY-TARGET-0001.md`(`40300a4`),
`OPENROUTER-MIGRATION-IDENTIFY-TARGET-FIX-0001.md`(`8678327`)
**작업 성격**: 조사/실측만 수행. Production 코드/Architecture/Contract/
Governance 문서는 이번 세션에서 전혀 수정하지 않았다.

## Summary

- Gate #12(`test_execution`)가 FAIL했던 원인은 **순수 실행 환경(interpreter
  선택) 문제**였다 — 프로젝트 dependency/config 문제도, Production
  코드 결함도 아니었다.
- `stage_05.py`는 `subprocess.run([sys.executable, "-m", "pytest", ...])`로
  pytest를 호출한다. 이전 Gate 실행에서는 파이프라인 자체를
  `/usr/local/bin/python3 cli.py ...`로 실행했는데, 이 인터프리터에는
  pytest가 설치돼 있지 않다. 반면 이번 세션 내내 "352 passed"의
  근거로 삼아온 전체 회귀 테스트는 실제로는 `/root/.local/bin/pytest`
  (`uv tool install pytest`로 설치된 별도 격리 venv,
  `/root/.local/share/uv/tools/pytest/bin/python`)로 실행돼 왔다 —
  즉 **파이프라인 실행과 회귀 테스트 실행이 서로 다른 Python
  interpreter를 썼다**는 사실 자체가 이번 조사의 핵심 발견이다.
- 이 프로젝트에는 pytest를 어느 interpreter에 설치해야 하는지 규정하는
  `requirements.txt`/`pyproject.toml`이 `hqs/development/` 어디에도
  없다 — 즉 "pytest가 `sys.executable`에서 보여야 한다"는 `stage_05.py`의
  암묵적 가정은 **프로젝트가 명시적으로 관리·보증한 적이 없는 가정**이다.
- **수정 없이** 파이프라인 자체를 pytest가 설치된 interpreter
  (`/root/.local/share/uv/tools/pytest/bin/python`)로 실행하자 —
  Production 코드/Contract/Engine/Governance 전부 무변경 상태로 —
  Stage 01→05 전체가 **`verdict: PASS`**로 결정적으로 통과했다(모든
  Gate 항목 포함, `test_execution` 자체가 내부적으로 "352 passed, 6
  skipped"를 실제로 재현).
- **Gate #12 최종 판정: PASS.**

## 1. Interpreter / PATH / pytest executable / pytest module 위치

| 항목 | 값 |
|---|---|
| `which python3` | `/usr/local/bin/python3` |
| `python3 -c "import sys; print(sys.executable)"` | `/usr/local/bin/python3` |
| `python3 -V` | Python 3.11.15 |
| `which pytest` | `/root/.local/bin/pytest` |
| `/root/.local/bin/pytest`의 실체 | symlink → `/root/.local/share/uv/tools/pytest/bin/pytest` |
| 그 shebang | `#!/root/.local/share/uv/tools/pytest/bin/python` |
| `/usr/local/bin/python3 -m pip list`에 pytest 존재 여부 | **없음**(conan/cryptography 등 시스템 패키지만 존재) |
| `/root/.local/share/uv/tools/pytest/bin/python -m pytest --version` | `pytest 9.0.2`(정상 동작) |
| PATH 순서 | `/root/.local/bin`이 최우선 — 사람이 터미널에서 `pytest`를 치면 uv-tool 버전이 실행됨 |

## 2. pytest 실행 방식의 차이

- **사람이 `pytest ...` 또는 `/root/.local/bin/pytest ...`를 직접 칠 때**:
  `uv tool install pytest`가 만든 격리 venv
  (`/root/.local/share/uv/tools/pytest/`)의 전용 Python으로 실행된다.
  이 venv는 pytest 실행 전용으로 격리돼 있고, 프로젝트의 다른 의존성은
  들어있지 않다(`pip`조차 없음 — `uv tool`의 격리 특성).
- **`stage_05.py`가 내부적으로 `test_execution`을 실행할 때**:
  `sys.executable`(즉, **Stage 04/05 파이프라인 자체를 실행 중인
  프로세스의 interpreter**)로 `-m pytest`를 호출한다. 파이프라인을
  `/usr/local/bin/python3 cli.py`로 띄우면 `sys.executable`이
  `/usr/local/bin/python3`가 되고, 이 interpreter에는 pytest가 없다.

즉 **"pytest가 설치돼 있는가"의 문제가 아니라 "어느 interpreter로
전체 파이프라인을 실행했는가"의 문제**다 — pytest 자체는 이
환경에 정상적으로 설치돼 있다(uv tool 경유).

## 3. 기존 352 passed가 실행된 interpreter 추적

이번 세션 전체(오늘 이전 포함, `c39eb26`/`8678327`의 "352 passed, 6
skipped" 결과 포함)에서 회귀 테스트를 돌릴 때 실제로 사용한 명령은
`/root/.local/bin/pytest -q`였다(대화 기록상 `python3 -m pytest`가
처음에 `No module named pytest`로 실패해 `/root/.local/bin/pytest`로
전환했던 이력 그대로). 따라서 **"352 passed" 자체는 처음부터
`/root/.local/share/uv/tools/pytest/bin/python`로 실행된 결과였다**
— `/usr/local/bin/python3`로는 애초에 회귀 테스트를 실행한 적이
없다. 이번 조사로 `/root/.local/bin/pytest`와
`/root/.local/share/uv/tools/pytest/bin/python -m pytest`가 동일한
실체임을 직접 확인했다(같은 버전 9.0.2, 같은 실행 결과: 352 passed,
6 skipped in ~35~40초).

## 4. Gate #12가 요구하는 실행 방식 vs 실제 실행 방식 비교

| | Gate #12 실행 방식(`stage_05.py`) | 이전 시도(FAIL) | 이번 재현(PASS) |
|---|---|---|---|
| 파이프라인 진입 interpreter | `sys.executable`을 그대로 계승 | `/usr/local/bin/python3 cli.py ...` | `/root/.local/share/uv/tools/pytest/bin/python cli.py ...` |
| `stage_05.py` 내부 `subprocess.run([sys.executable, "-m", "pytest", ...])`이 참조하는 interpreter | 위와 동일(자동 계승) | `/usr/local/bin/python3`(pytest 없음) | `/root/.local/share/uv/tools/pytest/bin/python`(pytest 있음) |
| 결과 | — | `ModuleNotFoundError`, `test_execution` FAIL | `test_execution` PASS(내부적으로 352 passed, 6 skipped 재현) |

`stage_05.py` 코드 자체는 "현재 파이프라인을 실행 중인 interpreter에
pytest가 있다"고 가정할 뿐, 특정 경로를 하드코딩하지 않는다 — 이
가정이 이전 실행에서는 성립하지 않았고 이번에는 성립했다는 차이뿐,
**코드 로직은 두 실행에서 완전히 동일**했다(diff 없음, 이번 세션에서
`stage_05.py`를 전혀 건드리지 않음).

## 5. 순수 환경 문제 vs 프로젝트 dependency/config 문제 판정

**순수 환경(execution) 문제로 판정한다.** 근거:

- `hqs/development/` 아래 어디에도 pytest를 어떤 interpreter에
  설치해야 하는지 규정하는 `requirements.txt`/`pyproject.toml`/
  `Pipfile` 등이 없다(레포 전체에서 유일한 `pyproject.toml`은
  `archive/v1/`의 것으로, 이미 KEEP·out-of-scope로 분류된 과거
  스냅샷이며 현재 `hqs/development` 실행과 무관).
  → 즉 "이 프로젝트는 pytest를 이런 방식으로 설치해야 한다"는
  프로젝트 차원의 명시적 계약이 애초에 존재하지 않는다. 존재하지
  않는 계약을 어겼다고 말할 수 없으므로 **"프로젝트 dependency
  선언의 결함"으로 분류할 근거가 없다.**
- `stage_05.py`의 `sys.executable` 사용 자체는 합리적인 설계다(어떤
  interpreter로 실행되든 그 interpreter의 pytest를 쓰겠다는 것 —
  하드코딩된 경로보다 오히려 이식성이 높은 선택). 코드 결함이 아니다.
- 실패의 유일한 원인은 **이 컨테이너에 pytest가 시스템 Python
  (`/usr/local/bin/python3`)이 아니라 `uv tool install`로 격리
  설치돼 있었다는, 이 세션 환경 고유의 설치 방식**이었다. 이는
  프로젝트 코드/설정과 무관하게 이 실행 환경을 준비한 방식에서
  비롯된 것이다.

## 6~9. 수정 여부 판단 및 최종 조치

- **Production Code 수정: 하지 않았다**(`stage_05.py` 등 전혀 변경 없음).
- **테스트 환경 설정 수정 필요성 검토**: 검토 결과, **수정이 전혀
  필요 없었다** — 이미 이 환경에 pytest가 설치돼 있는 interpreter
  (`/root/.local/share/uv/tools/pytest/bin/python`)가 존재했고, 그
  interpreter로 파이프라인을 실행하는 것만으로 Gate #12가 결정적으로
  PASS했다. 따라서 "최소 범위 환경 설정 수정" 여부를 판단할 필요
  자체가 사라졌다 — **아무것도 설치/수정하지 않고 해결**됐다.
- **OpenRouter 호출 추가/Engine 변경/Stage 변경/Contract 변경/
  Governance 문서 변경/모델 고정·라우팅 로직 변경**: 전부 하지
  않았다. 이번 재현에 쓰인 issue(`workflow_hello_sdlc.py` 기존 함수에
  주석 한 줄 추가)는 `8678327` 커밋에서 이미 검증에 썼던 것과
  동일한 issue를 재사용했다 — 새로운 코드 경로를 만들지 않았다.

## 실행 Evidence 상세

- 실행 명령: `/root/.local/share/uv/tools/pytest/bin/python cli.py --expose-target /tmp/or_gate_issue2.json`
  (issue: "workflow_hello_sdlc.py의 기존 함수에 안전한 주석 한 줄만 추가")
- `exit code: 0`, `failed_at: None`, `error: None`
- `stage_04.target`: `["workflow_hello_sdlc", "run_hello_sdlc"]`(실제 AST 후보 색인에서 정확히 식별 — `8678327`과 동일 결과 재현)
- `stage_05.verdict`: **`PASS`**
  - `structural`: PASS(`engine_failed: false`)
  - `specification_scope`: PASS(`target_in_scope: true`)
  - `design_scope`: PASS(`scope_ok: true`)
  - `test_execution`: **PASS**(`executed: true`, `returncode: 0`,
    output에 실제 pytest 실행 로그 `"352 passed, 6 skipped in 35.64s"`
    포함 — Stage 05가 적용한 실제 구현물에 대해 전체 프로젝트
    테스트를 실제로 돌려 통과를 확인했다)
- 실행 후 `git status --short`: 잔여 변경 없음(clean) — Stage 05의
  mutate→`finally` 복원이 이번에도 정상 동작.

## Gate #12 최종 판정

**PASS.**

- Stage 01→05 전체 E2E가 1회 이상 실제로 `verdict: PASS`까지 도달했다
  (`ADR-0027` §10 #12 요건 충족).
- 이 PASS는 Production 코드/Contract/Engine/Governance를 전혀
  바꾸지 않은 채, 이미 존재하던 interpreter를 선택해 재실행한 것만으로
  얻어졌다 — Migration 자체의 정확성을 훼손하는 우회가 아니다.
- 앞선 Evidence(`c39eb26`/`40300a4`/`8678327`)와 결합하면, `ADR-0027`
  §10의 12개 항목 중 이제 **#1/#2/#3/#4/#5(구조)/#6/#7/#8/#11/#12가
  실측 PASS**로 확정되고, **#9/#10만 여전히 BLOCKED**(실사용 실패
  조건을 인위로 재현하지 않았기 때문 — 자원 낭비 방지를 위해 의도적으로
  보류, `c39eb26` §A 사유 동일)로 남는다.

## Architecture / Contract / Governance / Production Code 변경 여부

- Architecture: 무변경.
- Contract: 무변경.
- Governance: RFC-0041/ADC-0044/ADR-0027 및 다른 어떤 문서도 수정하지 않음.
- Production Code: **무변경** — 이번 세션은 investigation + 실행
  interpreter 선택만으로 완료됐다. `stage_05.py`를 포함해 어떤
  파일도 diff가 없다.

## Branch / Commit / PR 상태

- Branch: `claude/jarvis-openrouter-validation-bin9aj`
- 이전 HEAD: `8678327`
- 본 Evidence 커밋 예정
- PR: 없음(사용자 명시적 요청 없음)
