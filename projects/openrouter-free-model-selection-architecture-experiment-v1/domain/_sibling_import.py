"""`openrouter-auto-selection-v1` 프로젝트를 읽기 전용으로 재사용하기
위한 import 헬퍼. 두 프로젝트 모두 최상위 패키지 이름이 `domain`이라
일반 `sys.path` 조작만으로는 이미 로드된 이 프로젝트의 `domain`
패키지와 충돌한다 — 별칭 패키지 이름으로 독립적으로 로드해 충돌을
피한다. 이 파일은 sibling 프로젝트의 어떤 파일도 수정하지 않는다
(읽기 전용)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ALIAS = "sibling_auto_selection_domain"
_SIBLING_DOMAIN_DIR = Path(__file__).resolve().parents[2] / "openrouter-auto-selection-v1" / "domain"


def load_sibling_domain():
    """`openrouter-auto-selection-v1/domain` 패키지를 별칭
    (`sibling_auto_selection_domain`)으로 로드해 반환한다. 한 프로세스
    안에서 여러 번 호출돼도 한 번만 로드한다(idempotent)."""
    if _ALIAS in sys.modules:
        return sys.modules[_ALIAS]

    spec = importlib.util.spec_from_file_location(
        _ALIAS, _SIBLING_DOMAIN_DIR / "__init__.py", submodule_search_locations=[str(_SIBLING_DOMAIN_DIR)]
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[_ALIAS] = module
    spec.loader.exec_module(module)

    for submodule_name in ("contracts", "fixtures", "stage_policy", "model_pool", "auto_selection_client"):
        sub_spec = importlib.util.spec_from_file_location(
            f"{_ALIAS}.{submodule_name}", _SIBLING_DOMAIN_DIR / f"{submodule_name}.py"
        )
        sub_module = importlib.util.module_from_spec(sub_spec)
        sub_module.__package__ = _ALIAS
        sys.modules[f"{_ALIAS}.{submodule_name}"] = sub_module
        sub_spec.loader.exec_module(sub_module)
        setattr(module, submodule_name, sub_module)

    return module
