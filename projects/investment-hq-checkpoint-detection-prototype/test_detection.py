"""Prototype 검증 — 실제 관찰값(재현) 대비 True Positive, 실제 Dogfooding
산출물 30건 대비 False Positive 여부만 확인한다. `pytest` 스위트에는
포함하지 않는다(Prototype이며, 본 구현으로 승격되지 않았다).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detect_content_failure import is_content_failure

REPO_ROOT = Path(__file__).resolve().parents[2]

# 이 세션이 `pg-hq-verify` 1차 시도 중 `cat synthesis.md`로 직접 확인하고,
# `efa-2026-08/EVIDENCE.md`에 동일 문장으로 인용된 실제 관찰값 재구성.
OBSERVED_FAILURE_TEXT = (
    "API Error: Unable to connect to API: Self-signed certificate detected. "
    "Check your proxy or corporate SSL certificates"
)

DOGFOODING_DIRS = [
    "hqs/investment/dogfooding/aapl-hq-verify",
    "hqs/investment/dogfooding/pg-hq-verify",
    "hqs/investment/dogfooding/efa-2026-08",
]


def main():
    failures = []

    # 1) True Positive — 실제 관찰된 실패 시그니처를 감지하는가
    if not is_content_failure(OBSERVED_FAILURE_TEXT):
        failures.append("TRUE POSITIVE 실패: 실제 관찰된 실패 텍스트를 감지하지 못함")

    # 2) False Positive — 실제 정상 산출물(3개 Team, 30개 checkpoint 파일)을
    #    실패로 오탐하지 않는가
    checked = 0
    for rel_dir in DOGFOODING_DIRS:
        cp_dir = REPO_ROOT / rel_dir / "checkpoints"
        for md_file in sorted(cp_dir.glob("*.md")):
            checked += 1
            content = md_file.read_text(encoding="utf-8")
            if is_content_failure(content):
                failures.append(f"FALSE POSITIVE: {md_file.relative_to(REPO_ROOT)}")

    print(f"checked {checked} real checkpoint files across {len(DOGFOODING_DIRS)} dirs")

    if failures:
        print("FAIL")
        for f in failures:
            print(" -", f)
        sys.exit(1)

    print("PASS — true positive 1/1, false positive 0/%d" % checked)


if __name__ == "__main__":
    main()
