"""`hqs/development/mvp/tests/` 공유 fixture — 여러 test_*.py가 동일하게
반복하던 `_load(name, path)`(파일 경로로 sibling module을 동적 로드)를
한 곳에 둔다."""

import importlib.util
import sys


def load_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
