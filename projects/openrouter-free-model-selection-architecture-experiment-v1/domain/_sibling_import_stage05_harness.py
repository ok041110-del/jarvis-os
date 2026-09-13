"""`stage05-parallel-validation-harness-v1` 프로젝트를 읽기 전용으로
재사용하기 위한 import 헬퍼(`domain/_sibling_import.py`와 동일한 패턴
— 세 프로젝트 모두 최상위 패키지 이름이 `domain`이라 일반 import는
충돌한다). 이 파일은 sibling 프로젝트의 어떤 파일도 수정하지 않는다."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ALIAS = "sibling_stage05_harness_domain"
_SIBLING_DOMAIN_DIR = Path(__file__).resolve().parents[2] / "stage05-parallel-validation-harness-v1" / "domain"


def load_sibling_stage05_harness_domain():
    if _ALIAS in sys.modules:
        return sys.modules[_ALIAS]

    spec = importlib.util.spec_from_file_location(
        _ALIAS, _SIBLING_DOMAIN_DIR / "__init__.py", submodule_search_locations=[str(_SIBLING_DOMAIN_DIR)]
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[_ALIAS] = module
    spec.loader.exec_module(module)

    # `validators.py`가 `.results`를 상대 import하므로 의존 순서대로 로드한다.
    for submodule_name in ("results", "validators"):
        sub_spec = importlib.util.spec_from_file_location(
            f"{_ALIAS}.{submodule_name}", _SIBLING_DOMAIN_DIR / f"{submodule_name}.py"
        )
        sub_module = importlib.util.module_from_spec(sub_spec)
        sub_module.__package__ = _ALIAS
        sys.modules[f"{_ALIAS}.{submodule_name}"] = sub_module
        sub_spec.loader.exec_module(sub_module)
        setattr(module, submodule_name, sub_module)

    return module
