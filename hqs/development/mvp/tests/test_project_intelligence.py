"""`_directory_structure()`의 `max_depth` Blind Spot 회귀 테스트
(DEV-HQ-V2.0-CATEGORY-PATHS-BLIND-SPOT-REVIEW-0001 §7.2 Next Task).

실제 파일시스템(ROOT)을 그대로 사용한다 — 이 함수는 mock 대상 외부
의존성이 없고, 버그 자체가 실제 경로 깊이 계산에 있었기 때문이다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp.project_intelligence import _directory_structure


def test_directory_structure_includes_entries_below_base_directories():
    # 수정 전에는 ROOT 기준 depth를 세어 base(hqs/development, docs)
    # 자체가 이미 max_depth를 소모했다 — base 바로 아래 파일도 전부 누락됐다.
    result = _directory_structure()
    assert any(entry.startswith("hqs/development/mvp/") for entry in result)


def test_directory_structure_respects_max_depth_from_each_base():
    result = _directory_structure(max_depth=1)
    assert "hqs/development/mvp/" in result
    assert not any(entry.startswith("hqs/development/mvp/") and entry != "hqs/development/mvp/" for entry in result)


def test_directory_structure_excludes_noise_dirs():
    result = _directory_structure(max_depth=3)
    assert not any("__pycache__" in entry for entry in result)
