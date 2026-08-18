import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agents import (
    bear_researcher_bear_case,
    bull_researcher_bull_case,
    fundamental_analyst_fundamental_analysis,
    industry_analyst_industry_analysis,
    news_analyst_news_event_analysis,
    report_writer_final_report,
    sentiment_analyst_sentiment_analysis,
    synthesis_judgment,
    technical_analyst_technical_analysis,
)

PROJECT_ROOT = Path(__file__).resolve().parent
ISSUE_DIR = PROJECT_ROOT / "issues" / "0001-cat-analysis"
RAW_DATA_PATH = ISSUE_DIR / "raw_data.md"

_SECTION_TAGS = [
    "[FUNDAMENTAL]",
    "[TECHNICAL]",
    "[INDUSTRY]",
    "[NEWS/EVENT]",
    "[SENTIMENT]",
]

_COMPANY_HEADER = "Company: Caterpillar Inc. (Ticker: CAT)"


class Checkpointer:
    def __init__(self, issue_dir: Path):
        self.dir = issue_dir / "checkpoints"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.dir / "manifest.json"
        self._lock = threading.Lock()
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        if self.manifest_path.exists():
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return {"completed_steps": [], "call_log": []}

    def _save_manifest_locked(self):
        self.manifest_path.write_text(
            json.dumps(self.manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def has(self, step: str) -> bool:
        return step in self.manifest["completed_steps"]

    def load(self, step: str) -> str:
        return (self.dir / f"{step}.md").read_text(encoding="utf-8")

    def save(self, step: str, content: str, input_chars: int, elapsed_sec: float):
        (self.dir / f"{step}.md").write_text(content.rstrip() + "\n", encoding="utf-8")
        with self._lock:
            if step not in self.manifest["completed_steps"]:
                self.manifest["completed_steps"].append(step)
            self.manifest["call_log"].append(
                {
                    "role": step,
                    "input_chars": input_chars,
                    "output_chars": len(content),
                    "elapsed_sec": round(elapsed_sec, 1),
                }
            )
            self._save_manifest_locked()


def _extract_section(raw_text: str, tag: str) -> str:
    marker = f"## {tag}"
    start = raw_text.index(marker)
    rest = raw_text[start:]
    next_header = rest.find("\n## ", 1)
    section = rest if next_header == -1 else rest[:next_header]
    return section.strip()


def _run_step(cp: Checkpointer, step: str, fn, *args) -> str:
    if cp.has(step):
        return cp.load(step)
    input_len = sum(len(a) for a in args)
    t0 = time.monotonic()
    output = fn(*args)
    elapsed = time.monotonic() - t0
    cp.save(step, output, input_len, elapsed)
    return output


def run() -> dict:
    pipeline_t0 = time.monotonic()
    cp = Checkpointer(ISSUE_DIR)

    raw_text = RAW_DATA_PATH.read_text(encoding="utf-8")
    limitation = _extract_section(raw_text, "데이터 한계")
    sections = {
        tag: f"{_COMPANY_HEADER}\n\n{_extract_section(raw_text, tag)}"
        for tag in _SECTION_TAGS
    }

    wave1_jobs = {
        "fundamental_analysis": (fundamental_analyst_fundamental_analysis, f"{sections['[FUNDAMENTAL]']}\n\n{limitation}"),
        "technical_analysis": (technical_analyst_technical_analysis, f"{sections['[TECHNICAL]']}\n\n{limitation}"),
        "industry_analysis": (industry_analyst_industry_analysis, f"{sections['[INDUSTRY]']}\n\n{limitation}"),
        "news_event_analysis": (news_analyst_news_event_analysis, f"{sections['[NEWS/EVENT]']}\n\n{limitation}"),
        "sentiment_analysis": (sentiment_analyst_sentiment_analysis, f"{sections['[SENTIMENT]']}\n\n{limitation}"),
    }
    wave1_t0 = time.monotonic()
    wave1_results = {}
    pending = {name: (fn, arg) for name, (fn, arg) in wave1_jobs.items() if not cp.has(name)}
    for name in wave1_jobs:
        if cp.has(name):
            wave1_results[name] = cp.load(name)
    if pending:
        with ThreadPoolExecutor(max_workers=len(pending)) as pool:
            futures = {name: pool.submit(_run_step, cp, name, fn, arg) for name, (fn, arg) in pending.items()}
            for name, fut in futures.items():
                wave1_results[name] = fut.result()
    wave1_elapsed = time.monotonic() - wave1_t0

    fundamental = wave1_results["fundamental_analysis"]
    technical = wave1_results["technical_analysis"]
    industry = wave1_results["industry_analysis"]
    news_event = wave1_results["news_event_analysis"]
    sentiment = wave1_results["sentiment_analysis"]

    all_analyses = (
        f"[FUNDAMENTAL ANALYSIS]\n{fundamental}\n\n"
        f"[TECHNICAL ANALYSIS]\n{technical}\n\n"
        f"[INDUSTRY ANALYSIS]\n{industry}\n\n"
        f"[NEWS/EVENT ANALYSIS]\n{news_event}\n\n"
        f"[SENTIMENT ANALYSIS]\n{sentiment}"
    )

    wave2_t0 = time.monotonic()
    wave2_jobs = {
        "bull_case": (bull_researcher_bull_case, all_analyses),
        "bear_case": (bear_researcher_bear_case, all_analyses),
    }
    wave2_results = {}
    pending2 = {name: (fn, arg) for name, (fn, arg) in wave2_jobs.items() if not cp.has(name)}
    for name in wave2_jobs:
        if cp.has(name):
            wave2_results[name] = cp.load(name)
    if pending2:
        with ThreadPoolExecutor(max_workers=len(pending2)) as pool:
            futures = {name: pool.submit(_run_step, cp, name, fn, arg) for name, (fn, arg) in pending2.items()}
            for name, fut in futures.items():
                wave2_results[name] = fut.result()
    wave2_elapsed = time.monotonic() - wave2_t0

    bull_case = wave2_results["bull_case"]
    bear_case = wave2_results["bear_case"]

    wave3_t0 = time.monotonic()
    synthesis = _run_step(cp, "synthesis", synthesis_judgment, bull_case, bear_case)
    wave3_elapsed = time.monotonic() - wave3_t0

    wave4_t0 = time.monotonic()
    final_report = _run_step(
        cp, "final_report", report_writer_final_report,
        fundamental, technical, industry, news_event, sentiment,
        bull_case, bear_case, synthesis,
    )
    wave4_elapsed = time.monotonic() - wave4_t0

    pipeline_elapsed = time.monotonic() - pipeline_t0

    results = {
        "fundamental_analysis.md": fundamental,
        "technical_analysis.md": technical,
        "industry_analysis.md": industry,
        "news_event_analysis.md": news_event,
        "sentiment_analysis.md": sentiment,
        "bull_case.md": bull_case,
        "bear_case.md": bear_case,
        "synthesis.md": synthesis,
        "final_report.md": final_report,
    }
    for filename, content in results.items():
        (ISSUE_DIR / filename).write_text(content.rstrip() + "\n", encoding="utf-8")

    wave_summary = {
        "wave1_elapsed_sec": round(wave1_elapsed, 1),
        "wave2_elapsed_sec": round(wave2_elapsed, 1),
        "wave3_elapsed_sec": round(wave3_elapsed, 1),
        "wave4_elapsed_sec": round(wave4_elapsed, 1),
        "pipeline_total_elapsed_sec": round(pipeline_elapsed, 1),
    }
    (ISSUE_DIR / "call_log.json").write_text(
        json.dumps({"calls": cp.manifest["call_log"], "wave_summary": wave_summary}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return results, wave_summary


if __name__ == "__main__":
    cp_before = Checkpointer(ISSUE_DIR)
    steps_before = list(cp_before.manifest["completed_steps"])

    t0 = time.monotonic()
    status = "success"
    wave_summary = {}
    try:
        _, wave_summary = run()
    except Exception as e:
        status = f"failed: {type(e).__name__}: {e}"
        raise
    finally:
        elapsed_total = time.monotonic() - t0
        cp_after = Checkpointer(ISSUE_DIR)
        steps_after = list(cp_after.manifest["completed_steps"])
        summary = {
            "status": status,
            "elapsed_this_invocation_sec": round(elapsed_total, 1),
            "steps_completed_before_this_invocation": steps_before,
            "steps_completed_after_this_invocation": steps_after,
            "steps_skipped_via_checkpoint_this_invocation": steps_before,
            "steps_newly_run_this_invocation": [s for s in steps_after if s not in steps_before],
            **wave_summary,
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        print(f"Done. Output written to {ISSUE_DIR}")
