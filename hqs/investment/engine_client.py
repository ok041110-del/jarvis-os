"""Investment HQ의 유일한 Engine 호출 경유 지점 — 새 Gateway/Adapter를 만들지 않는다
(`hqs/development/IMPLEMENTATION_RULES.md`와 동일 원칙). `hqs/development/`는 수정하지 않는다.
"""

import sys
from pathlib import Path

DEV_HQ_ROOT = Path(__file__).resolve().parent.parent.parent / "hqs" / "development"
sys.path.insert(0, str(DEV_HQ_ROOT))

from mvp.engine import call_engine  # noqa: E402

__all__ = ["call_engine"]
