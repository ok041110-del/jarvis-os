# EVIDENCE-0010: Python 3.9 Collection 문제 해결 — Isolated Python 3.10+ 환경 확보 및 전체 Regression 검증

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·ADC·
ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하지
않는다. `EVIDENCE-0007`·`EVIDENCE-0009`가 확정한 HOLD 상태를 그대로
전제하고, 이번 검토(Python 3.9 collection 문제 해결)의 결과만
기록한다. **시스템 Python 무변경**(§3). 실제 Provider egress
없음(§9). `RUN_REAL_ENGINE_TESTS` 등 게이트는 기본 OFF 유지(§7).

## 1. 문제 정의 및 정확한 원인 확인

### 1.1 재현

```
python3 -m pytest hqs/development/mvp/tests/test_workflow_ast_context.py -v
```

```
platform darwin -- Python 3.9.6, pytest-8.4.2 ...
hqs/development/mvp/workflow_ast_context.py:41: in <module>
    def identify_target(design: str, candidate_index: str | None = None):
E   TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

### 1.2 정확한 원인 — 근본 원인 파일 2개

`str | None`(PEP 604 Union 문법, Python 3.10+ 필요)을 사용하는
소스 파일은 정확히 **2개**이며, 이 2개가 import 체인을 통해 기존
5개 테스트 파일의 collection을 깨뜨린다.

| 근본 원인 파일:줄 | 코드 | Import 체인으로 영향받는 테스트 파일 |
|---|---|---|
| `hqs/development/mvp/workflow_ast_context.py:41` | `def identify_target(design: str, candidate_index: str \| None = None):` | `test_workflow_ast_context.py`(직접), `test_stage_04.py`(→`stage_04.py`→직접) |
| `hqs/development/stages/01_context_analysis/stage_01.py:13` | `def run_stage_01(issue: dict, target: tuple \| None = None) -> dict:` | `test_stage_01.py`(직접), `test_cli_integrated.py`(→`cli.py`→`workflow.py`→직접), `test_workflow_integrated.py`(→`workflow.py`→직접) |

두 파일 모두 `from __future__ import annotations`가 없어(§1.3),
Python 3.9는 함수 정의 시점에 기본값 annotation(`str | None`,
`tuple | None`)을 즉시 평가하며, 3.9의 `str.__or__`/`tuple.__or__`가
`type`을 피연산자로 받는 `X | Y` union 문법을 지원하지 않아
`TypeError`가 발생한다(PEP 604는 Python 3.10에서 도입).

### 1.3 Pre-existing 여부 — 기준선 대조

`git blame`으로 두 줄의 최초 커밋을 확인했다.

```
3711a3eb (ok041110-del 2026-08-31 19:14:12 +0900) workflow_ast_context.py:41
26ce9ae0 (Claude        2026-08-23 11:07:27 +0000) stage_01.py:13
```

- `3711a3e`: "Dev HQ: Stage Data Contract Governance 반영 (RFC-0009 →
  ADC-0007 → ADR-0009) (#127)"
- `26ce9ae`: "feat: ADR-0008 + Stage 01 Context Analysis (docs +
  stage_01.py)"

두 커밋 모두 이번 OmniRoute Governance/Integration 작업 브랜치
(`claude/adc-omniroute-model-routing-conditional-adoption`)가
분기하기 이전, 별개의 완전히 무관한 작업에서 도입됐다.
`git diff --stat`로 이번 세션 전체에서 두 파일이 **한 번도
수정되지 않았음**을 재확인했다(§9) — `EVIDENCE-0006`~`0009`가
이미 기록한 "pre-existing, 이번 작업과 무관" 판단을 원본 커밋
증거로 재확인한다.

## 2. Python 버전 정책 확인(임의 변경 없이 사전 확인)

- 저장소 최상위에 이 프로젝트(`hqs/`, `core/`)에 대한
  `pyproject.toml`/`requirements.txt`/`.python-version`/CI
  설정이 **없다** — `archive/v1/pyproject.toml`은 legacy v1
  아카이브 전용이며 현재 `hqs/development/mvp/`와 무관하다(uv
  workspace 정의만 있고 Python 버전 하한을 명시하지 않는다).
- `pytest.ini`는 `--import-mode=importlib` 외 버전 관련 설정이
  없다.
- 이 저장소의 기존 선례(같은 저장소, 다른 트랙): `docs/research/
  PHASE7-EXTERNAL-OBSERVATION-TRADINGAGENTS-0001.md`가 "Python
  요구: `>=3.10` (세션 환경: Python 3.11.15, 별도 venv 사용)"을
  명시하고, `docs/research/JARVIS-OS-V2.0-WORKFLOW-ADAPTER-
  REVERSIBILITY-V2-TEST-DESIGN-0001.md`가 "Python 3.12.14(uv 관리
  격리 venv)"를 사용한 선례가 있다 — **모두 isolated venv 방식이며
  시스템 Python을 바꾸지 않았다.**
- 결론: 명시적 project-wide 버전 정책 문서는 없지만, PEP 604 문법
  자체가 코드베이스의 사실상 `>=3.10` 요구이며, 이 저장소의 기존
  선례도 "시스템 Python 무변경 + isolated venv"를 일관되게
  택했다 — 이번 검토도 동일 방식을 따른다(사용자 지침 2, 3).

## 3. Isolated Python 3.10+ 환경 구성

시스템 Python(`/usr/bin/python3`, Apple CommandLineTools, 3.9.6)은
**전혀 건드리지 않았다.**

```
/Users/chan/.local/bin/python3.12 -m venv <scratchpad>/py310-venv
<venv>/bin/pip install pytest
```

- venv 위치: 세션 scratchpad 디렉터리(저장소 밖) — 저장소에
  어떤 파일도 추가되지 않는다(`.venv`를 저장소 안에 만들지 않음).
- 결과: `Python 3.12.14`, `pytest 9.1.1`.
- 이 venv 생성 자체가 `git status`에 어떤 변경도 만들지 않음을
  확인했다(§9).

## 4. 5개 Collection 오류 파일의 3.10+ Import/Collection 확인

```
<venv>/bin/python -m pytest \
  hqs/development/mvp/tests/test_workflow_ast_context.py \
  hqs/development/mvp/tests/test_cli_integrated.py \
  hqs/development/mvp/tests/test_stage_01.py \
  hqs/development/mvp/tests/test_stage_04.py \
  hqs/development/mvp/tests/test_workflow_integrated.py \
  --co
```

→ **`34 tests collected in 0.05s`, collection 오류 0건.** 5개 파일
전부 정상 import되고, `identify_target`/`run_stage_01`의 `str |
None`/`tuple | None` annotation이 Python 3.12에서 문제없이
평가된다.

### 4.1 이번 검토 중 새로 발견된, 이번 작업과 무관한 부수 발견

전체 스위트를 3.12 venv에서 처음 실행했을 때 `test_omniroute_engine_
boundary.py::test_no_production_caller_imports_omniroute_engine_yet`
1건이 FAIL했다. 원인을 분리 확인했다.

- 이 테스트는 `grep -rl omniroute_engine <MVP_DIR>`로 production
  코드가 `omniroute_engine`을 참조하지 않음을 확인한다
  (`EVIDENCE-0006` 당시 작성).
- Apple CommandLineTools의 시스템 `python3`(3.9.6)는
  `sys.pycache_prefix`가 `/Users/chan/Library/Caches/com.apple.python`
  로 macOS 자체 커스터마이징되어 있어 소스 트리 안에 `__pycache__`를
  전혀 만들지 않는다(`sys.pycache_prefix` 확인, §9) — 그래서 지금까지
  이 grep 검사가 컴파일 캐시를 만난 적이 없었다.
- 표준 python.org 빌드인 `/Users/chan/.local/bin/python3.12`는
  `sys.pycache_prefix=None`(표준 동작)이라 일반적인 `__pycache__/*.pyc`를
  소스 옆에 그대로 만든다. `omniroute_engine.cpython-312.pyc` 같은
  캐시 파일명에 "omniroute_engine" 문자열이 그대로 포함되어, 검사의
  `grep -rl`이 **컴파일 캐시를 소스 참조로 오검출**했다.
- **판정**: 이는 Python 3.9/3.10+ 호환성 문제가 **아니다** —
  `test_omniroute_engine_boundary.py`(이번 세션 Request 4에서 작성한
  테스트 코드) 자체의, 인터프리터의 pycache 배치 방식에 의존하는
  latent 버그다. 이번 작업(3.10+ 환경 확보)이 처음으로 이 버그를
  노출시켰을 뿐, 근본 원인은 PEP 604와 무관하다 — 사용자 지침 5가
  요구하는 "새 실패의 원인을 이번 작업과 기존 문제로 분리"에 따라
  별도로 기록한다.
- **최소 수정**: `grep`에 `--include=*.py`를 추가해 `.py` 소스만
  검색하도록 좁혔다(`hqs/development/mvp/tests/test_omniroute_engine_
  boundary.py`, 검사 로직 1줄+docstring 보강만 변경, Case A
  Boundary·OmniRoute Policy·Architecture/Contract 무관). 수정 후
  캐시가 존재하는 상태로 반복 실행해도 안정적으로 PASS함을
  확인했다(§9).

## 5. Development HQ 전체 MVP Regression — 3.10+ vs 기존 3.9 기준선

### 5.1 Python 3.12 venv, Gate 기본 OFF

```
<venv>/bin/python -m pytest hqs/development/mvp/tests/
```

→ **`185 passed, 5 skipped in 5.22s`** = 190 items.

기존 3.9 기준선(156, 5개 파일 collection 오류로 제외)에 이번에
추가로 collection 가능해진 34개(§4)를 더하면 `156 + 34 = 190` —
정확히 일치한다.

skip된 5개는 기존과 동일한, 의도된 opt-in 게이트 skip이다.

```
SKIPPED test_mvp_0001.py::test_returns_review_then_test_cases_without_manual_intervention
SKIPPED test_mvp_0001.py::test_review_content_reaches_test_execution_as_context
SKIPPED test_omniroute_engine_real.py::test_success_via_production_function
SKIPPED test_omniroute_engine_real.py::test_error_mapping_via_production_function
SKIPPED test_omniroute_engine_real.py::test_timeout_abort_via_production_function
```

### 5.2 Python 3.9(시스템, 무수정) — 기존 156 기준선 재확인

```
python3 -m pytest hqs/development/mvp/tests/ \
  --ignore=test_cli_integrated.py --ignore=test_stage_01.py \
  --ignore=test_stage_04.py --ignore=test_workflow_ast_context.py \
  --ignore=test_workflow_integrated.py
```

→ **`151 passed, 5 skipped in 5.26s`** = 156. `EVIDENCE-0008` 이후
확립된 기준선과 완전히 동일 — 3.10+ 환경 구성이 기존 3.9 경로에
**어떤 영향도 주지 않았음**을 확인했다.

### 5.3 새 실패 유무 판정

3.12 venv 전체 실행에서 §4.1의 pycache 오검출 1건 외 **새로운
실패는 없었다.** 그 1건도 수정 후(§4.1) 안정적으로 PASS로
전환됐다 — **최종적으로 3.12 venv 전체 스위트는 185 passed, 5
skipped, 0 failed**로 수렴한다.

## 6. OmniRoute 관련 Regression — Python 3.12 venv

| 대상 | 결과 |
|---|---|
| `test_engine.py`(`call_engine()` 기존 계약) | `3 passed` |
| `test_omniroute_engine.py`(로컬 double, 7개) | 전체 스위트에 포함, PASS |
| `test_omniroute_engine_boundary.py`(Case A 정적 검사, 7개, §4.1 수정 후) | `7 passed` |
| `test_omniroute_engine_real.py`(이중 게이트, 3개) | `3 skipped`(게이트 OFF, 의도된 상태) |
| Experimental Thin Caller 프로토타입(`projects/omniroute-thin-engine-caller-v1/tests/`) | `26 passed, 1 skipped`(`test_real_engine_budget_block.py`, 이중 게이트 OFF) — 기존 27/27(26 무조건 + 1 게이트) 기준과 완전히 동일 |

RT-0001 non-trigger 증거(`test_no_existing_call_engine_call_site_
references_omniroute`)와 Case A Boundary 정적 검사
(`test_no_provider_or_routing_selection_logic` 등) 전부 Python
3.12에서도 PASS — 3.10+ 환경 전환이 이 트랙의 어떤 안전
경계에도 영향을 주지 않았다.

## 7. Gate/안전조건 무변경 확인

- `RUN_REAL_ENGINE_TESTS`: 이번 검토 전체에서 **설정하지 않음**
  (기본 OFF 유지) — §5.1의 skip 결과가 직접 증거.
- `RUN_REAL_OMNIROUTE_TESTS`/`I_UNDERSTAND_REAL_EGRESS_RISK`:
  **설정하지 않음** — §6의 skip 결과가 직접 증거.
- 실제 `claude` CLI 호출, 실제 OmniRoute 서버 기동, 실제 provider
  egress: **전혀 발생하지 않았다**(모든 실행이 mock/local
  double/skip 조합으로만 이뤄짐).
- Architecture/Contract/Freeze/OmniRoute Policy: **무변경**(§8).

## 8. Governance / Architecture 영향

- Architecture 변경: **없음**. Contract 변경: **없음**. Freeze 변경:
  **없음**. OmniRoute Policy(Routing/Cost-Budget/Audit) 변경:
  **없음**.
- 시스템 Python: **무변경**(`/usr/bin/python3` 그대로 3.9.6).
- 코드 변경: `hqs/development/mvp/tests/test_omniroute_engine_
  boundary.py` 1개 파일, 1개 테스트 함수의 `grep` 검사 범위
  좁힘(`--include=*.py`) + docstring 보강만(§4.1) — Python
  호환성 문제 해결에 직접 필요한 최소 변경이 아니라, 그 해결
  과정에서 노출된 별개의 latent 테스트 버그를 최소 수정한
  것으로, 어느 쪽이든 **테스트 코드 1줄 수준**이며 production
  코드(`omniroute_engine.py`, `engine.py`, 5개 호출부)는 전부
  무수정이다.
- `workflow_ast_context.py`, `stage_01.py`(근본 원인 파일 2개)를
  포함해 이 문제와 관련된 **production 소스 코드는 어디도 수정하지
  않았다** — PEP 604 문법을 `from __future__ import annotations`
  등으로 우회하는 수정도 하지 않았다(사용자 지침 3의 "가능하면
  시스템 Python 변경 없이 isolated venv로 검증" 원칙에 따라, venv
  전환만으로 문제가 해결되므로 소스 수정 자체가 불필요했다).
- 새로 작성한 파일: 이 Evidence 문서 1개.

## 9. Provenance / Reproducibility

- 오류 재현 및 원인 확인(§1): `python3 -m pytest
  hqs/development/mvp/tests/test_workflow_ast_context.py -v`,
  `test_stage_01.py -v`(전체 traceback), 나머지 3개 파일 traceback
  일괄 확인.
- Pre-existing 확인(§1.3): `git diff --stat`(두 파일 diff 없음),
  `git blame -L 41,41 hqs/development/mvp/workflow_ast_context.py`,
  `git blame -L 13,13 hqs/development/stages/01_context_analysis/
  stage_01.py`.
- Python 버전 정책 확인(§2): `find`로 `pyproject.toml`/
  `requirements*.txt`/`.python-version`/CI 설정 부재 확인,
  `docs/research/PHASE7-EXTERNAL-OBSERVATION-TRADINGAGENTS-0001.md`
  · `JARVIS-OS-V2.0-WORKFLOW-ADAPTER-REVERSIBILITY-V2-TEST-DESIGN-
  0001.md` 선례 확인.
- venv 구성(§3): `/Users/chan/.local/bin/python3.12 -m venv
  <scratchpad>/py310-venv` → `Python 3.12.14`, `pytest 9.1.1`.
- Collection 확인(§4): `<venv>/bin/python -m pytest <5개 파일> --co`
  → `34 tests collected in 0.05s`.
- pycache 오검출 원인 확인(§4.1): `sys.pycache_prefix` 비교
  (`python3` → `/Users/chan/Library/Caches/com.apple.python`,
  `python3.12` → `None`), 수정 전/후 반복 실행(수정 전 1회 FAIL,
  수정 후 연속 2회 `7 passed`).
- 전체 Regression(§5): `<venv>/bin/python -m pytest
  hqs/development/mvp/tests/` → `185 passed, 5 skipped in 5.22s`;
  `python3 -m pytest hqs/development/mvp/tests/ --ignore=...`(5개
  제외) → `151 passed, 5 skipped in 5.26s`.
- OmniRoute 관련 Regression(§6): `<venv>/bin/python -m pytest
  hqs/development/mvp/tests/test_engine.py` → `3 passed`;
  `<venv>/bin/python -m pytest
  projects/omniroute-thin-engine-caller-v1/tests/` → `26 passed,
  1 skipped`.
- 게이트 상태(§7): `env | grep RUN_REAL` — 검토 전체에서 미설정
  확인.
- `__pycache__` 정리: `find . -name "__pycache__" -exec rm -rf {} +`
  (전부 `.gitignore`에 등재, 저장소에 흔적 없음).
- 코드 변경 범위: `git status --short` — 이 Evidence 문서 1개
  추가 및 `test_omniroute_engine_boundary.py`(기존 미추적 신규
  파일, 이번에 1개 검사 로직만 조정) 외 무변경.
- 실제 Provider egress: 없음. 실제 `~/.omniroute` 접근: 없음
  (이번 검토는 OmniRoute 서버를 전혀 기동하지 않았다 — mock/
  local double/skip만 사용).
- commit/push/PR: 수행하지 않음.

## 10. Call-Site Conversion HOLD에 미치는 영향

`EVIDENCE-0007` §6.2·`EVIDENCE-0009` §7이 정리한 4개 선행조건 중
**#3(Python 3.10+ 환경 확보 또는 `workflow_ast_context.py` 제외
재검토)** 이 이번 검토로 **충족**된다 — isolated venv로 Python
3.10+ 환경이 실제로 구성·검증됐고, `workflow_ast_context.py`를
포함한 5개 파일 전부가 그 환경에서 정상 collection·PASS됨을
확인했다.

그러나 나머지 선행조건은 무변경이다.

| # | 선행조건 | 상태 |
|---|---|---|
| 1 | 사용자가 실제 로컬 OmniRoute를 기동·구성했음을 직접 확인 | **미충족**(`EVIDENCE-0009` §7과 동일 — 이 세션이 대신 확인 불가) |
| 2 | `test_mvp_0001.py` 게이트 재설계 | **충족**(`EVIDENCE-0008`) |
| 3 | Python 3.10+ 환경 확보 또는 `workflow_ast_context.py` 제외 재검토 | **충족(이번 문서)** — isolated venv로 5개 파일 전부 collection·PASS 확인. 단, 이 결과는 **isolated venv 안에서만** 유효하다 — 이 세션의 기본 실행 환경(시스템 Python 3.9.6)은 여전히 5개 파일을 collection할 수 없으므로, 실제 Call-Site Conversion을 강행한다면 그 운영 환경도 3.10+(또는 동등 venv)이어야 한다는 새로운 전제가 따라붙는다 |
| 4 | 전환 자체를 Governance 절차로 재확인할지 사용자가 명시적으로 선택 | **미충족, 무변경** |

**결론**: 4개 중 2개(#2, #3)가 충족됐지만 #1·#4가 여전히
미충족이다. **Call-Site Conversion은 여전히 HOLD**다 — 이번
검토는 HOLD를 재개하지 않는다. `EVIDENCE-0007`의 §3.1이 지적한
결정적 위험(게이트 없는 실제 Engine 호출)은 #2로 이미 해소됐고,
이번 #3 해소로 "5개 호출부 전부를 검증된 상태로 전환할 수 있는
Python 환경"이 처음으로 실증됐다는 점에서 진전이지만, #1(실제
운영 OmniRoute 가용성의 운영자 확인)이라는 이 세션 권한 밖의
조건이 여전히 남아 있는 한 전환을 재개할 근거는 되지 못한다.

## Self Review

- Python 3.9 collection 실패의 정확한 원인을 확인했는가 —
  **Pass**(§1.2, 근본 원인 파일 2개·정확한 줄 번호).
- pre-existing 여부를 기준선과 대조해 기록했는가 — **Pass**(§1.3,
  `git blame` 원본 커밋 증거).
- Python 버전 정책을 먼저 확인하고 임의로 변경하지 않았는가 —
  **Pass**(§2 — 정책 부재 확인, 저장소 선례에 따라 isolated venv
  선택. §3 — 시스템 Python 무변경).
- 시스템 Python을 바꾸지 않고 isolated venv를 구성했는가 —
  **Pass**(§3).
- 5개 collection 오류 파일의 3.10+ import/collection을
  확인했는가 — **Pass**(§4).
- 전체 MVP regression을 3.10+에서 실행하고 156 기준과
  비교했는가 — **Pass**(§5.1 — `156+34=190` 정확히 일치).
- 새 실패를 이번 작업과 기존 문제로 분리했는가 — **Pass**(§4.1 —
  pycache 오검출은 PEP 604와 무관한 별개의 latent 테스트 버그로
  분리 확인·최소 수정).
- `RUN_REAL_ENGINE_TESTS` Gate가 기본 OFF로 유지됐는가 —
  **Pass**(§7, §5.1 skip 결과).
- 실제 Claude CLI/OmniRoute/provider egress가 발생했는가 —
  **아니오**(§7, §9).
- `test_engine.py`, Thin Caller 27/27, Case A Boundary, RT-0001
  non-trigger를 3.10+에서 확인했는가 — **Pass**(§6).
- Architecture/Contract/Freeze/OmniRoute Policy를 변경했는가 —
  **아니오**(§8).
- Python 호환성 문제에 직접 필요한 최소 변경만 허용했는가 —
  **해당 없음(변경 자체가 불필요했다)** — venv 전환만으로 해결됐고,
  §4.1의 수정은 호환성 수정이 아니라 별개로 노출된 테스트 버그의
  최소 수정이다(범위를 명확히 구분해 기록).
- Call-Site Conversion HOLD에 미치는 영향을 명확히
  판정했는가 — **Pass**(§10 — 4개 중 2개 충족, HOLD 유지).
- commit/push/PR을 수행했는가 — **아니오**.
