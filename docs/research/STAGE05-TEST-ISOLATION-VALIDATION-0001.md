# Stage 05 Test Isolation — Existing Test Suite Validation — Evidence 0001

## Summary

- **최종 판정: B(추가적인 lightweight isolation 필요).** "A(기존 test/ +
  격리된 Implementation 사본만으로 충분)"는 실측으로 **기각**됐다 —
  `hqs/development/mvp/tests/`가 import하는 소스는 `mvp/`뿐 아니라
  `stages/`·`workflow.py`·`cli.py`까지 걸쳐 있고, 그중 1개 파일
  (`test_execution_host.py`)은 **`hqs/investment/`(다른 HQ)까지
  참조**한다(실측 재현, §1.3). Git/Container는 근거가 없어 **기각**
  (§3, §6).
- **가장 단순한 해결책이 실제로 충분했다**: `.git`을 제외한 저장소
  작업 트리 전체를 일반 디렉터리 복사(`tar`/`cp`, git 아님)로 격리된
  임시 위치에 복제하니 **251ms**만에 끝났고, 그 복제본에서 실행한
  기존 스위트가 원본과 **완전히 동일한 결과**(324 passed, 6 skipped)를
  냈다(실측, §1.4·§5). 개별 파일을 손으로 골라 복제하는 방식(Option
  B/C 원안)은 §1.3이 발견한 것처럼 **깨지기 쉬워서**(새 테스트가 어떤
  파일을 참조할지 미리 다 알 수 없음), "전체 작업 트리 복사"가 더
  견고하면서도 여전히 가볍다는 것이 이 조사의 핵심 결론이다.
- Test의 mutation은 복제본 안에서만 일어나므로, **복제본을 지우는
  cleanup이 실패해도 실제 Production 소스는 전혀 위험하지 않다** —
  이는 현재 구현(실제 파일을 직접 덮어쓰고 `finally`로 복원하는 방식,
  복원 실패 시 Production 오염 위험 존재)보다 **구조적으로 더
  안전하다**(§7). 현재 구현을 보존하는 방향으로 결론을 유도하지
  않는다는 전제를 그대로 지켰다.
- **이미 Production에 존재하는 조각을 재사용할 수 있다**:
  `hqs/development/mvp/execution_host.py::run_isolated()`가
  `ADC-0015`(Conditional Accept, Process 1차·Thread 금지)로 이미
  Production 채택된 Process 기반 격리 실행 함수이며, "동일 Target
  동시 실행"을 오염 없이 처리하는 것까지 이미 테스트로 고정돼 있다
  (`test_execution_host.py`, §1.5). Test Node의 실행 **디스패치**는
  이 함수를 그대로 재사용할 수 있다 — 단, 이 함수 자체는 파일 시스템
  격리(Workspace 복제)를 제공하지 않으므로 **Workspace 복제 + Process
  격리 실행은 서로 다른 두 메커니즘이며 둘 다 필요하다**(§3.2).
- Production 코드는 변경하지 않았다 — 이 문서는 임시 scratch
  디렉터리(repository 밖)에서 실측한 결과만 기록한다(§ Validation).

---

## 1. Existing Test Suite Analysis

### 1.1 대상 test/ 디렉터리 전수 조사

Stage 05가 실제로 실행하는 스위트는 `hqs/development/mvp/tests/`
(`stage_05.py::_TESTS_DIR`, 이전 조사에서 이미 확인) — 이 디렉터리를
전수 조사했다.

- **테스트 파일 수**: 41개(`*.py`, `__pycache__` 제외, `ls` 실측).
- **`conftest.py`**: **없음**(디렉터리 전체에 `conftest.py`가
  존재하지 않음, 실측 확인). 공유 fixture는 각 파일이 직접
  `pytest.fixture`로 선언하거나 `monkeypatch` 인자로만 처리한다.
- **source import 방식**: 19개 파일이 `sys.path.insert(0, ...)`를
  직접 사용하며, 경로는 전부 `Path(__file__).resolve().parents[N]`
  형태 — **하드코딩된 절대경로가 아니라 파일 자신의 위치를 기준으로
  한 상대 계산**이다(실측, `grep` 전수 확인). 이는 디렉터리를 복제해도
  내부 상대 구조만 보존하면 그대로 동작한다는 뜻이다(§1.4가 이를
  실측으로 검증).
- **fixture**: `tmp_path`/`tmpdir`이 6개 파일에서 쓰인다(`test_stage_05.py`
  포함) — 전부 pytest 표준 fixture로 각 테스트별 임시 디렉터리를
  자동 격리한다.
- **environment dependency**: `os.environ`을 **직접 대입**(`os.environ[...] =`)
  하는 파일은 **0건**(실측) — 전부 `monkeypatch.setenv`류를 통해서만
  읽거나 바꾸며, pytest가 테스트 종료 시 자동 복원한다. 프로세스
  전역 상태를 영구히 바꾸는 코드는 없다.
- **subprocess**: 4개 파일(`test_engine.py`/`test_mvp_0001.py`/
  `test_omniroute_engine_real.py`/`test_stage_05.py`)이 `subprocess`를
  언급하지만, `test_engine.py`는 `subprocess.run`을 **mock으로 대체**
  하고(`patch("mvp.engine.subprocess.run", ...)`), `test_mvp_0001.py`의
  실제 subprocess 호출 테스트는 `RUN_REAL_ENGINE_TESTS=1`이 명시적으로
  설정되지 않으면 **skip**된다(`_skip_unless_real_engine_gate`, 실측
  확인). 기본 실행(`pytest tests/ -q`)에서 실제 외부 프로세스(`claude`
  CLI 등)를 호출하는 테스트는 **없다.**
- **temporary directory**: `tmp_path` fixture 기반(위 항목), 별도
  수동 temp dir 관리 없음.
- **filesystem mutation**: `.write_text(`을 쓰는 파일 5개 — 전부
  `tmp_path`(격리된 임시 경로) 대상이며, 유일한 예외가
  `stage_05.py::_run_pytest_with_applied_implementation`이 (테스트
  대상 함수 자체로서) 실제 Production 파일을 backup→write→restore
  하는 경로다 — 이는 **Stage 05 Test 책임 자신의 본질적 동작**이지
  테스트 스위트의 부작용이 아니다(§2에서 별도로 다룬다).
- **Git dependency**: `git` 명령/`GitPython`/`.git` 참조 **0건**(실측
  `grep`, 전체 41개 파일). Stage 05 Test 실행에 Git 저장소 상태(브랜치/
  커밋)가 필요하다는 근거가 없다.
- **외부 서비스 dependency**: `test_github_adapter.py`는
  `urllib.request.urlopen`을 **전부 monkeypatch로 대체**해 실제 GitHub
  API를 호출하지 않는다. `test_github_adapter_real.py`는
  `GITHUB_TOKEN` 미설정 시 skip(기본 실행에서 비활성). 유일하게 실제
  네트워크 유사 동작을 하는 것은 `test_omniroute_engine_real.py`가
  **로컬 loopback**(`127.0.0.1`, `http.server.HTTPServer`)에 띄우는
  in-process test double뿐이며, 이마저 미응답 시 `pytest.skip`으로
  스스로 빠진다("환경 문제, FAIL 아님"이라고 명시). **외부 네트워크에
  실제로 나가는 테스트는 0건.**

### 1.2 `__pycache__`/`.pytest_cache` 실측

```
$ pytest hqs/development/mvp/tests/ -q      # 기본 실행(플래그 없음)
324 passed, 6 skipped in 32.82s
$ git status --short                         # 실행 후
(출력 없음 — .gitignore가 __pycache__/·.pytest_cache/를 무시)
$ find hqs/development -iname "__pycache__" | wc -l
16
$ find . -maxdepth 1 -iname ".pytest_cache"
./.pytest_cache
```

`git status`에는 잡히지 않지만(`.gitignore`), 실제로는 **저장소
디렉터리 트리에 16개의 `__pycache__`와 저장소 루트에 `.pytest_cache`가
실제로 쓰인다** — 이는 진짜 filesystem mutation이며, "Git이 추적하지
않는다"는 것과 "디스크에 아무것도 안 쓴다"는 것은 다른 사실이다(§2가
이 구분을 그대로 유지한다).

### 1.3 소스 의존성 폐쇄(Closure) 실측 — 가정이 틀렸던 지점

당초 가설(문서만으로 세운 가정): "`hqs/development/mvp/`와
`hqs/development/stages/`만 있으면 충분하다." **이 가설은 실측으로
기각됐다.**

- `parents[2]`/`parents[4]` 기반 경로 전수 조사 결과, 테스트가 직접
  참조하는 소스는 `mvp/`·`stages/`뿐 아니라 **`hqs/development/workflow.py`
  ·`hqs/development/cli.py`**(둘 다 `mvp/` 밖, `development/` 바로
  아래)까지 포함한다(`test_workflow_integrated.py`/`test_cli_integrated.py`
  등, `grep` 재확인).
- **결정적 발견**: `test_execution_host.py`(41개 중 1개)는
  `_pytest_target.py::run_pytest_target()`을 통해
  `CONTAMINATION_TARGET = "hqs/investment/tests/test_stock_team_integration.py"`
  — **`hqs/development/` 밖, 다른 HQ(`hqs/investment/`)의 파일**을
  `REPO_ROOT` 상대 경로로 실행한다. 이 타겟 파일은 다시
  `hqs/investment/teams/stock_team.py`를 import한다(실제로 읽어
  확인).
- **실측 재현**: `hqs/development/{mvp,stages,workflow.py,cli.py}`만
  복제한 임시 작업 공간에서 `pytest tests/ -q`를 실행하면 **8개
  파일이 즉시 collection error**로 실패한다(`FileNotFoundError:
  .../hqs/development/workflow.py` 등) — 애초에 가설이 부족했던
  파일들이 정확히 이 오류로 드러났다.

**결론**: "기존 test/가 참조하는 소스"의 실제 폐쇄 범위는 **손으로
미리 다 나열하기 어렵다** — 새 테스트가 추가될 때마다 이 폐쇄가
조용히 넓어질 수 있다(예: 이번 조사가 아니었다면 `hqs/investment/`
의존을 사전에 알 수 없었다). 이는 Option B/C(손으로 고른 파일만
복제)의 **구조적 취약점**이며, §1.4가 더 견고한 대안을 실측한다.

### 1.4 전체 작업 트리 복사(선별 없음) — 실측 검증

```
$ time tar --exclude='.git' --exclude='__pycache__' --exclude='.pytest_cache' \
    -cf - . | tar -xf - -C <isolated_tmp_dir>
real  0m0.251s

$ du -sh <isolated_tmp_dir>
19M

$ pytest <isolated_tmp_dir>/hqs/development/mvp/tests/ -q -p no:cacheprovider
324 passed, 6 skipped in 30.14s   # 원본과 완전히 동일
```

**"손으로 최소 집합을 고르는 것"보다 "`.git`만 빼고 전부 복사하는
것"이 더 견고하면서(§1.3의 누락 위험 원천 제거) 비용도 무시할 만하다
(251ms, 30초짜리 pytest 실행 시간의 1% 미만)** — 이 조사가 추천하는
방향이다(§8 최종 판정).

### 1.5 재사용 가능한 기존 Production 격리 인프라

`hqs/development/mvp/execution_host.py::run_isolated()`가 이미
Production에 존재한다:

```python
_EXECUTOR = ProcessPoolExecutor(max_workers=4)

def run_isolated(func, *args, **kwargs):
    future = _EXECUTOR.submit(func, *args, **kwargs)
    return future.result()
```

- `ADC-0015`(Conditional Accept, "Process 1차, Thread는 사용하지
  않는다") 범위 안에서 이미 채택된 모듈이다.
- `test_execution_host.py::test_run_isolated_is_accurate_on_identical_target_concurrent_execution`가
  **"동일 Target을 2개 호출자가 동시에 요청해도 결과가 오염되지
  않는다"**를 이미 테스트로 고정해 두었다 — 이는 이번 Test Node
  설계가 필요로 하는 "동시 실행 안전성"과 정확히 같은 성질이다.
- **주의(과장 방지)**: 이 함수는 **Process 격리만** 제공한다(별도
  worker process에서 실행) — **파일 시스템 격리는 제공하지 않는다.**
  `run_isolated(run_pytest_target, "some/path.py")`를 호출해도
  `run_pytest_target` 내부가 여전히 같은 디스크의 같은 파일 경로를
  읽는다면 격리되지 않는다. 즉 **"어디서 실행하는가"(Process)**와
  **"무엇을 대상으로 실행하는가"(Workspace/파일)**는 서로 다른
  축이며, Test Node는 **둘 다** 필요하다(§3.2).

---

## 2. Test Mutation 전수 조사

Stage 05의 Test 책임(pytest 실행)이 유발할 수 있는 mutation을
항목별로 조사했다. "실제 발생 여부"는 §1의 실측, "다른 Validator와
충돌 가능성"·"Workspace 내부로 제한 가능한지"는 RFC-0039(§2.5, §4)의
독립성 분석을 이번 실측으로 재확인한 결과다.

| Mutation 항목 | 실제 발생 여부 | 다른 Validator와 충돌 가능성 | Workspace 내부로 제한 가능한지 |
|---|---|---|---|
| Source file 변경 | **있음** — Target 파일에 Implementation을 적용(Test 책임의 본질) | **있음(조건부)** — AST/Review가 같은 파일을 라이브로 읽는 설계라면 충돌(RFC-0039 §4) | **가능** — Workspace 복제본 안의 파일만 바뀌므로, 원본 파일을 라이브로 읽는 Validator가 없다면 충돌 자체가 성립하지 않음(§1.4 실측이 Workspace가 완전히 독립된 사본임을 증명) |
| Test file 변경 | **없음** — Test 자신은 테스트 파일을 쓰지 않는다(실측, `write_text` 대상은 `tmp_path`뿐) | 없음 | 해당 없음 |
| `__pycache__` | **있음**(실측, §1.2 — 16개 디렉터리) | **낮음** — `*.py` glob 기반 후보 인덱스(`_mvp_source_files()` 등)는 `__pycache__`를 매칭하지 않음(확장자 다름) | **가능** — Workspace 내부 복제본에서 발생하면 원본 저장소를 전혀 건드리지 않는다 |
| Temporary files | 있음(`tmp_path` fixture, pytest가 자동 정리) | 없음(pytest 표준 fixture, 테스트별 격리) | 해당 없음(이미 격리됨) |
| Generated artifacts | 없음(이 스위트는 별도 산출물 파일을 생성하지 않음, 실측 확인) | 없음 | 해당 없음 |
| Environment variables | **없음(영구 변경)** — `monkeypatch`만 사용, 프로세스 종료 시 자동 복원(§1.1) | 없음 | 해당 없음(이미 안전) |
| Process-global state | 낮음 — `sys.modules` 캐시에 테스트가 import한 모듈이 남을 수 있으나, Process 격리(`run_isolated`) 시 별도 worker process라 다음 실행에 영향 없음 | **있음(Thread 실행 시)** — `ADC-0015` §Q0가 "동일 Target 동시 실행 오염"으로 이미 관찰·경고한 바로 그 문제(Thread 금지 근거) | **가능** — Process 격리(`run_isolated`)로 해소(§1.5) |
| Working directory 변경 | **없음** — `os.chdir` 사용 0건(실측 `grep`), `subprocess.run(cwd=...)`만 사용해 하위 프로세스에만 영향 | 없음 | 해당 없음 |
| Subprocess | 있음(pytest 자체 실행이 `sys.executable -m pytest` subprocess, 현재 Production 구현) | 없음(자식 프로세스는 부모의 파일 시스템 격리 범위를 벗어나지 않음) | 가능 |
| Network access | **없음(기본 실행)** — 전부 mock 또는 로컬 loopback, 외부 네트워크 0건(§1.1) | 없음 | 해당 없음 |

**요약**: 6개 Validator 사이에서 실제로 충돌 가능한 mutation은
**"Source file 변경"** 단 하나이며, 그마저도 Workspace 복제(§1.4)로
완전히 제거 가능하다는 것이 이번 실측의 핵심 결론이다 — RFC-0039의
추론 기반 결론(§4, "유일한 실제 공유 가변 상태는 대상 파일")과
정확히 일치한다.

---

## 3. 기존 test/ 재사용 가능성 판정

### 3.1 A~E 판정

| 옵션 | 판정 | 근거 |
|---|---|---|
| A. 기존 test/ 그대로 + Implementation만 별도 위치 제공 | **기각** | "그대로 사용"은 라이브 원본 파일을 그대로 두고 위치만 바꾼다는 뜻이므로, Test의 mutation이 여전히 공유 자원(원본 파일)에 가해진다 — Race Condition이 해소되지 않는다(§2). |
| B. test/ 자체만 복제 | **기각** | test/가 참조하는 소스(`mvp/`·`stages/`·`workflow.py`·`cli.py`·심지어 `hqs/investment/`)가 test/ 밖에 있어 복제만으로는 실행 자체가 안 된다(§1.3 실측 — `FileNotFoundError`로 즉시 재현). |
| C. test/와 source 모두 복제 | **채택(수정된 형태로)** | 필요조건이지만, 손으로 고른 "source"의 범위가 §1.3처럼 깨지기 쉽다 — **`.git`만 제외한 작업 트리 전체 복사**로 이 취약점을 없앴다(§1.4). 251ms, 원본과 동일 결과(324 passed/6 skipped) 실측. |
| D. Git Worktree | **기각** | 41개 테스트 파일 어디에도 git 의존성이 없다(실측 `grep` 0건, §1.1). `git worktree`는 Git 이력/브랜치 상태가 필요할 때 쓰는 도구인데, 이 스위트는 파일 내용만 있으면 동작한다 — Worktree가 주는 이점(공유 `.git` object store, 브랜치 전환)을 이 문제가 필요로 하지 않는다. |
| E. Container/Sandbox | **기각** | 권한 상승·커널 자원 격리·네트워크 차단이 필요하다는 근거가 없다(외부 네트워크 0건, 위험한 시스템 호출 없음, §1.1·§2). 일반 디렉터리 복사 + Process 격리(`run_isolated`)로 이미 §2의 유일한 충돌 지점(Source file)이 해소된다. |

### 3.2 왜 "Workspace 복제"와 "Process 격리"가 둘 다 필요한가

- **Workspace 복제(파일 시스템 축)**: Test의 mutation을 원본과 완전히
  분리된 디스크 경로에 가둔다 — §2가 확인한 유일한 실제 충돌
  지점(Source file)을 원천 제거.
- **Process 격리(`run_isolated`, 실행 축)**: `sys.modules` 캐시나
  import 시점 부작용이 같은 프로세스 안에서 누적되는 것을 막는다 —
  `ADC-0015`가 이미 "동일 Target 동시 실행 오염"으로 지적한 문제(§1.5).
- 둘은 **직교하는 다른 문제를 푼다** — 하나만으로는 부족하다. 이
  구분을 명시하지 않으면 "`run_isolated`가 이미 있으니 추가 작업이
  필요 없다"는 **과장된 결론**에 이르게 된다(방지 대상).

---

## 4. Test Workspace 정의

사용자가 제시한 목표 형태를 실측 근거로 그대로 채택한다(수정 불필요):

```
Stage 04 Implementation
        ↓
Validation Context
        ↓
Test Workspace
   ├── required source snapshot   (= .git 제외 작업 트리 전체 복사, §1.4)
   ├── existing test/              (= 위 복사에 이미 포함됨, 별도 작업 없음)
   └── required fixtures/config    (= conftest.py 없음, 별도 config 불필요 — §1.1)
        ↓
      pytest (-p no:cacheprovider 권장, §7)
        ↓
    Test Result
```

- "required source snapshot"을 손으로 최소화하려는 시도(§1.3)는
  실측으로 깨졌으므로, **"필요한 최소"가 아니라 "`.git` 제외 전체"**가
  실용적 정의다 — 이는 목표 형태를 부정하는 것이 아니라, 그
  "required"의 실제 범위를 이번 조사로 구체화한 것이다.
- Test Workspace 밖(원본 저장소)은 **한 번도 쓰기 대상이 되지
  않는다** — §1.4의 실측(Implementation 적용·pytest 실행 후 원본
  `git status --short` 무변화 확인)이 이를 직접 증명한다.

---

## 5. Snapshot과 Test의 관계

- **Snapshot을 먼저 생성해야 하는가?** — **그렇다.** Test Workspace
  자체가 "복제 후 실행" 순서를 전제한다 — 이는 Test 책임 내부의
  순서이지, 다른 5개 Validator와의 순서 제약이 아니다(RFC-0039 §9.2
  질문 3과 일치).
- **어떤 파일이 Snapshot에 포함되어야 하는가?** — §1.4 실측 결론대로
  `.git`을 제외한 작업 트리 전체(`__pycache__`/`.pytest_cache`는
  제외해도 무방 — 실측상 있어도 없어도 결과에 영향 없음, 단 제외하면
  더 가볍고 깨끗함).
- **Test가 Snapshot을 직접 수정해도 되는가?** — **그렇다, 그리고
  그래야 한다.** Snapshot이 곧 Test Workspace이므로, Implementation
  적용은 이 Snapshot 안에서 이뤄진다 — 원본이 아니라 사본이므로
  "수정해도 되는가"라는 질문 자체가 원본 기준으로는 성립하지 않는다.
- **Test 실행 중 Snapshot mutation이 다른 Validator에 노출될 수
  있는가?** — **아니오, 노출되지 않는다(설계 전제).** 다른 5개
  Validator(Structure/Scope/AST/Dependency/Review)는 Test Workspace를
  전혀 참조하지 않는다 — AST/Review가 필요로 하는 "원본 코드"는
  Validation Context 단계에서 별도로 확보한 **읽기 전용 스냅샷**
  (RFC-0039 §5 수정 1)이지, Test Workspace가 아니다. 두 스냅샷(Test용
  전체 복제 vs AST/Review용 원본 코드 조각)은 **서로 다른 목적의
  별도 자원**이며 섞이지 않는다.

---

## 6. Parallel Validator와의 충돌 검증

| Validator | Test mutation ↔ Validator read 충돌 가능성 | 근거 |
|---|---|---|
| Structure | 없음 | Stage 04 Output 객체만 읽는다 — 파일 시스템 접근 자체가 없다(RFC-0039 §2.1). |
| Scope | 없음 | Target 식별자 + Scope Context(사전 확정 목록)만 비교 — 파일 시스템 접근 없다(RFC-0039 §2.2). |
| AST | **원천적으로 없음(Workspace 분리 시)** | AST가 읽는 "원본 코드"는 Validation Context가 Fan-out 이전에 확보한 별도 스냅샷이지 Test Workspace가 아니다(§5). Test Workspace와 물리적으로 다른 경로이므로 애초에 같은 파일을 두고 경합할 여지가 없다. |
| Dependency | 없음 | 사전에 구축된 Dependency Context(참조 인덱스)만 사용 — 라이브 파일 접근 없다(RFC-0039 §2.4). |
| Review | **원천적으로 없음(Workspace 분리 시)** | AST와 동일 — Review가 참조하는 원본 코드/메타데이터도 Validation Context의 스냅샷에서 온다(§5). |

**결론**: 원안이 우려했던 "repository source를 Test가 직접 수정하는
경우"의 병렬 실행 문제는, **Test가 원본이 아니라 자신만의 Workspace
복제본을 수정하는 구조로 바꾸면 애초에 발생하지 않는다** — 5개
Validator 전부와 무조건적으로 병렬 실행 가능(금지할 필요 없음, 최소
격리로 해결됨 — 사용자 지시의 우선순위와 일치).

---

## 7. Failure / Timeout / Cleanup Policy

| 실패 유형 | 다른 Validator에 영향? | 근거/설계 원칙 |
|---|---|---|
| pytest FAIL(정상 실행, 테스트 실패) | **아니오** | 유효한 Test Result(`executed: True, returncode != 0`)일 뿐 — 예외가 아니다. Aggregator가 그대로 수집한다(현재 `stage_05.py` 패턴과 동일, §RFC-0039 §6). |
| Timeout | **아니오** | `run_isolated`가 `ProcessPoolExecutor.Future`를 반환하므로, 호출부가 `future.result(timeout=...)`로 시간 제한을 걸 수 있다 — worker process는 별도 프로세스이므로 timeout이 다른 Validator의 프로세스/스레드에 영향을 주지 않는다. |
| Workspace 생성 실패(디스크 공간/권한) | **아니오** | Workspace 생성은 Test Node 자신의 준비 단계에서 실패하며, 다른 Validator는 이 단계 자체를 공유하지 않는다(RFC-0039 §5 — Validation Context의 "원본 스냅샷"과 Test의 "Workspace 복제"는 별개 자원, §3.2). Test는 이 경우 INCONCLUSIVE/FAILED 상태를 반환하면 된다. |
| Fixture 준비 실패 | **아니오** | pytest 자신의 fixture 오류는 Test Node 내부의 실행 결과(비정상 종료 코드/에러 출력)로 흡수된다 — 다른 Validator의 입력·실행에 어떤 의존성도 없다(RFC-0039 §2.5 항목 7). |
| Cleanup 실패(Workspace 삭제 실패) | **아니오, 그리고 원본도 안전하다** | Workspace가 원본과 물리적으로 분리된 사본이므로, 삭제가 실패해도 **디스크 공간 누수**일 뿐 Production 소스 오염이 아니다 — 이는 현재 구현(원본을 직접 mutate 후 `finally`로 복원, 복원 자체가 실패하면 Production 파일이 오염된 채 남는 실제 위험이 있음)보다 **더 안전한 실패 모드**다. |

**원칙 재확인**: 위 표 전체가 "한 Validator failure가 다른 Validator
실행을 막지 않는다"는 원칙을 만족한다 — Aggregator는 각 Node의
Future/Result를 독립적으로 수집하며, Test의 어떤 실패 형태도 다른
5개 Node를 중단시키는 경로가 없다.

---

## 8. 최종 판정

| 항목 | 결과 | 근거 |
|---|---|---|
| Existing test/ 재사용 | **가능(단, source 폐쇄 전체와 함께)** | test/ 자체는 무수정 재사용 가능 — 단독으로는 실행 불가(§1.3), 소스와 함께 복제하면 원본과 동일 결과(§1.4) |
| Source Snapshot 필요 | **필요, `.git` 제외 작업 트리 전체 권장** | 손으로 고른 최소 집합은 실측으로 깨짐(§1.3 hqs/investment 발견) — 전체 복사가 더 견고하고 여전히 가벼움(251ms, §1.4) |
| Test Workspace 필요 | **필요** | §4 |
| Test mutation | **있음(Source file, Workspace 내부로 한정 가능)** | §2 — Workspace 복제본 안에서만 발생하도록 설계 가능, 실측으로 원본 무변화 확인 |
| Shared State | **원본 저장소의 대상 파일뿐, Workspace 분리로 제거됨** | §2, §5, §6 |
| Repository 직접 변경 | **없음(Workspace 방식 채택 시)** | §1.4 실측 — Implementation 적용·pytest 실행 후 원본 `git status --short` 무변화 확인 |
| Worktree 필요 | **아니오** | Git 의존성 0건(§1.1, §3.1) |
| Container 필요 | **아니오** | 권한/네트워크 격리 필요 근거 없음(§1.1, §3.1) |
| Parallel Test 가능 | **가능(Workspace 격리 시 5개 전부와 무조건 병렬)** | §6 |

### 최종 Test Isolation 판정: **B(추가적인 lightweight isolation 필요)**

**A(기존 test/ + 격리된 Implementation 사본만으로 충분)를 기본값으로
가정하지 않았고, 실측 결과 실제로 A는 성립하지 않았다** —
Implementation 파일 하나만 격리해서는 충분하지 않고, source 전체의
격리된 사본(Workspace)이 필요했다(§1.3). 그러나 그 Workspace는
Worktree(C)나 Container(D)가 필요할 만큼 무겁지 않다 — 일반 디렉터리
복사(수백 ms)로 충분함을 실측했다(§1.4). 이것이 "B"의 정의(lightweight
isolation)에 정확히 부합한다.

---

## 9. Stage 05 Parallel DAG 영향

사용자가 제시한 구조를 그대로 재현한다:

```
Stage 04 Implementation
        ↓
Context Preparation
        ├── Immutable Source Snapshot
        └── Test Workspace
                 ↓
        ┌────────┬────────┬────────┬────────┬────────┬────────┐
        │        │        │        │        │        │
        ▼        ▼        ▼        ▼        ▼        ▼
    Structure Scope     AST  Dependency   Test     Review
        │        │        │        │        │        │
        └────────┴────────┴────────┴────────┴────────┴────────┘
                                  ↓
                             Aggregator
                                  ↓
                            Final Verdict
```

**이 구조는 타당하다 — 수정 없이 채택 가능하다(구조 자체는 옳았다,
"Test Workspace"를 별도 화살표로 이미 분리해 그린 것이 정확히 이번
실측이 요구하는 형태와 일치한다).** RFC-0039가 제안했던 수정(Context
단계에서 원본 스냅샷을 미리 확보)이 이 그림에서는 "Immutable Source
Snapshot"으로 이미 명시돼 있고, 이번 조사가 추가로 확정한 것은 **그
Snapshot의 실제 구성 방법**(`.git` 제외 전체 복사, §1.4)과 **Test
Workspace가 Immutable Source Snapshot과 별개의 자원**이어야 한다는 점
(§3.2, §5 — Test는 자신만의 **쓰기 가능한** 복제본이 필요하고,
AST/Review는 **읽기 전용** 스냅샷만 있으면 된다 — 둘을 같은 자원으로
착각하면 안 된다)이다.

**세부 구체화(그림을 부정하지 않는 보강)**:

```
Context Preparation
        │
        ├── Immutable Source Snapshot(읽기 전용, AST/Review가 참조)
        │      = 원본 대상 파일 내용만 최소 캡처 가능(전체 복사 불필요 — 이건 "일부"만 있으면 충분)
        │
        └── Test Workspace(쓰기 가능, Test 전용)
               = `.git` 제외 작업 트리 전체 복사(§1.4) — Implementation을
                 이 안에서 적용 후 pytest 실행, 종료 후 그대로 폐기(cleanup)
```

두 자원의 크기/성격이 다르다는 것도 실측으로 뒷받침된다 — Immutable
Source Snapshot은 "원본 파일 1개 내용"이면 충분(AST diff·Review
컨텍스트용)한 반면, Test Workspace는 "실행 가능한 전체 트리"가 필요
하다(§1.3). 이 둘을 하나의 "Snapshot"으로 뭉뚱그리면 Test Workspace가
필요 이상으로 가벼워지거나(실행 불가) Immutable Snapshot이 필요
이상으로 무거워진다(원본 전체 복사를 읽기 전용 캐시로 들고 있는
낭비) — 그림을 이 두 자원으로 명확히 분리해 유지할 것을 권고한다.

---

## 10. RFC/ADC/ADR 변경 필요 여부

**이 문서 자체는 RFC/ADC/ADR을 새로 요구하지 않는다** — `RFC-0039`
(Stage 05 Parallel Validation DAG)가 이미 "Test 격리 실행의 실제
메커니즘"을 Out of Scope(§11)로, `ADC-0042`가 이를 Validation
Requirement 1번("Context 선-스냅샷 + Test 격리 실행의 실제 구현 및
검증")으로 지정해 둔 상태였다 — 이 문서는 **그 후속 조사를 수행한
것**이며, 새로운 Architecture 방향을 제안하지 않는다.

- **`ADC-0042` Validation Requirement 1번에 대한 갱신 근거를
  제공한다**: "실제 구현"은 여전히 안 했지만(사용자 지시, Production
  변경 금지), "실제 구현 및 검증"이 요구한 메커니즘 자체(Workspace
  복제 방식, Process 격리 재사용 가능성)는 이번 실측으로 구체화됐다 —
  다음에 `ADC-0042`를 갱신하거나 재검토할 때 이 문서를 근거로 인용할
  수 있다.
- **여전히 별도 RFC → ADC → ADR이 필요한 것**(`RFC-0039` §10과
  동일하게 무변경): `VerificationResult` Contract 재설계, Stage 05
  문서(`RESPONSIBILITY.md` 등) 전면 개정, 6-Node 분리의 실제 Production
  구현 — 이 문서는 이 중 어느 것도 수행하지 않는다.
- **이번 조사로 새롭게 Governance 대상이 될 수 있는 것**: 만약
  "저장소 작업 트리 전체를 Test Workspace로 복제하는" 패턴이 실제로
  Production에 구현된다면, 이는 `execution_host.py`(`ADC-0015` 범위)
  보다 넓은 새 책임(파일 시스템 복제 자체)이므로, 그 구현 시점에
  `ADC-0015`의 범위를 그대로 재사용하는지 별도 확인이 필요할 수
  있다 — 이 문서는 그 확인을 대신하지 않는다(Not Determined로 남김).

---

## Validation — Production 무변경 확인

이번 조사의 모든 실측(§1.2, §1.3, §1.4, §5, §6)은 저장소 **밖**의
임시 scratch 디렉터리(`/tmp/.../scratchpad/stage05_test_workspace_*`)
에서 수행했다 — 실행 후 해당 디렉터리는 삭제했다.

```
$ git status --short
(출력 없음)
$ git diff --stat
(출력 없음)
```

Production 코드/Architecture/Contract/Governance는 변경하지 않았다 —
변경 범위는 이 신규 Evidence 문서 1건뿐이다.

## Related

- `docs/architecture/core/RFC-0039-stage05-parallel-validation-dag.md`,
  `docs/architecture/core/ADC-0042-stage05-parallel-validation-dag-decision.md`(이
  문서가 후속 조사하는 대상, Validation Requirement 1번)
- `hqs/development/mvp/execution_host.py`,
  `hqs/development/mvp/tests/test_execution_host.py`,
  `hqs/development/mvp/tests/_pytest_target.py`(재사용 가능한 Production
  Process 격리 인프라)
- `hqs/development/IMPLEMENTATION_RULES.md`(Execution Host §16.3,
  ADC-0015 Scoped 허용 범위)
- `hqs/development/stages/05_validation/stage_05.py`(현재 구현 —
  이 문서는 이를 기준으로 삼지 않고 참고자료로만 인용)
- `hqs/investment/tests/test_stock_team_integration.py`,
  `hqs/investment/teams/stock_team.py`(§1.3이 발견한 Cross-HQ 의존)
