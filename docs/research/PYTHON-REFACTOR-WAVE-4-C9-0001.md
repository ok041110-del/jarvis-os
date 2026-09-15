# Python Refactor Wave 4 — C9(테스트 fixture 공유화) 완료

**Governance 근거**: `RFC-0042` → `ADC-0045` → `ADR-0028` Lifecycle.
`docs/research/PYTHON-REFACTOR-WAVE-2-AUDIT-0001.md` §15가 DEFER한
C9(테스트 fixture 중복)를 Ponytail 권한 내에서 구현했다.

## 대상

`hqs/development/mvp/tests/` 아래 5개 파일이 완전히 동일한
`_load(name, path)`(파일 경로로 sibling 모듈을 동적 로드,
`importlib.util.spec_from_file_location` 기반) 함수를 각자 정의하고
있었다: `test_stage01_stage02_prd_handoff.py`,
`test_stage04_arch_validation_harness.py`,
`test_stage04_arch_validation_harness_extended.py`, `test_stage_02.py`,
`test_task_dependency_agent.py`(총 5개, 29회 호출).

`test_stage_01_multi_agent.py`의 `_load(name, filename)`은 시그니처와
내부 경로 결합 방식이 다른(파일명만 받아 `_STAGE_DIR`와 결합) 실제
변형이라 그대로 두었다(강제 통합 시 호출부를 모두 바꿔야 해 이득
대비 위험이 커짐 — Ponytail "억지 재사용 금지" 원칙).

## 변경

- 신규 `hqs/development/mvp/tests/conftest.py`에
  `load_module_from_path(name, path)`(기존 5개 파일의 `_load` 본문과
  100% 동일한 구현)를 한 곳에 정의.
- 5개 파일 각각에서 로컬 `_load` 정의를 제거하고
  `from conftest import load_module_from_path as _load`로 대체 —
  **호출부(`_load("reasoning", ...)` 등 29곳)는 전혀 건드리지
  않았다**(로컬 이름 `_load`를 그대로 유지해 diff를 최소화).
- `--import-mode=importlib`(이 저장소 `pytest.ini`) 환경에서
  `from conftest import ...`이 그냥은 동작하지 않아(conftest.py는
  pytest 플러그인으로만 특별 취급되고 일반 import 대상이 아님),
  각 파일 상단에 `sys.path.insert(0, str(Path(__file__).resolve().parent))`
  한 줄을 추가해 안전하게 해결했다(이 저장소가 이미 다른 곳에서
  쓰는 것과 동일한 sys.path 패턴, 새 기법 도입 아님).

## Behavior Preservation

- `_load`가 반환하는 값, `sys.modules` 등록 방식, 예외 전파 — 전부
  1바이트도 다르지 않다(함수 본문을 그대로 옮겼을 뿐).
- 각 파일의 실제 모듈 로드 호출(`reasoning = _load(...)` 등) 무변경.

## Validation

- `python3 -m py_compile`(변경 5개 파일 + `conftest.py` + 전체
  active tree): 오류 0건.
- `pytest hqs/development/mvp/tests/`: **356 passed, 6 skipped**
  (Wave 3 직후 baseline과 동일 총합, 회귀 없음).
- `pytest hqs/` 전체: **380 passed, 6 skipped**(baseline과 동일).

## Architecture/Contract 영향

없음 — 테스트 전용 헬퍼 중복 제거이며 Production 코드/Contract는
전혀 건드리지 않았다.

## Related

- `docs/research/PYTHON-REFACTOR-WAVE-2-AUDIT-0001.md`(C9 원 발견,
  §15 DEFER)
- `docs/research/PYTHON-REFACTOR-WAVE-3-DOCSTRING-FINAL-0001.md`
