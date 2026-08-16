import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "development-hq"))

from mvp.engine import call_engine

PROMPT_PATH = Path("/tmp/claude-0/-home-user-jarvis-os/a17fa421-986b-5493-b3aa-47b16259a75f/scratchpad/final_report_prompt.txt")
ISSUE_DIR = Path("/home/user/jarvis-os/projects/dividend-stock-analysis-nestle/issues/0001-nestle-analysis")

prompt = PROMPT_PATH.read_text(encoding="utf-8")

t0 = time.monotonic()
output = call_engine(prompt)
elapsed = time.monotonic() - t0

(ISSUE_DIR / "final_report.md").write_text(output.rstrip() + "\n", encoding="utf-8")
print(f"OK elapsed={elapsed:.1f}s output_chars={len(output)}")
