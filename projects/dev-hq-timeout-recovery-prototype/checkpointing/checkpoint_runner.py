"""Prototype B — Checkpointing. `shared/agents.py`(Nestlé/Toyota와 동일한
7분석→Bull/Bear→Synthesis→Final Report, 11단계) 파이프라인을 그대로
쓰고, `development-hq/mvp/engine.py`의 진짜 `call_engine()`(180초,
수정하지 않음)도 그대로 쓴다 — 이 Prototype이 바꾸는 것은 오직
"각 단계 결과를 언제 디스크에 쓰는가"뿐이다.

기존 `runner.py`(Nestlé/Toyota/JNJ 전부 동일)는 11단계가 전부 성공한
뒤 한 번에만 파일을 쓴다(all-or-nothing). 이 Prototype은 **각 단계가
끝나는 즉시** 그 결과를 `<issue_dir>/checkpoints/<step>.md`에 쓰고
`<issue_dir>/checkpoints/manifest.json`에 진행 상태를 기록한다.
재실행 시 이미 체크포인트가 있는 단계는 Engine을 다시 호출하지 않고
디스크에서 읽어 재사용하며, 처음으로 체크포인트가 없는 단계부터
이어서 실행한다.

사용법: python3 checkpoint_runner.py <trial_id>  (같은 trial_id로
재실행하면 자동으로 마지막 성공 지점부터 재개한다)
"""

import json
import sys
import time
from pathlib import Path

PROTO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROTO_ROOT / "shared"))

import agents  # noqa: E402  (shared/agents.py, 진짜 call_engine을 그대로 씀)

RAW_DATA_PATH = PROTO_ROOT / "shared" / "raw_data.md"

_SECTION_TAGS = [
    "[FUNDAMENTAL]",
    "[DIVIDEND_QUALITY]",
    "[VALUATION]",
    "[TECHNICAL]",
    "[INDUSTRY]",
    "[NEWS/EVENT]",
    "[SENTIMENT]",
]

_COMPANY_HEADER = "Company: Nestlé S.A. (Primary: NESN.SW, ADR: NSRGY)"

# 순서가 곧 파이프라인 순서다. 각 단계는 (파일명, agents 함수명, 입력을
# 만드는 방법)을 담는다 — "prior"는 이미 끝난 단계들의 결과 dict.
STEP_ORDER = [
    "fundamental_analysis",
    "dividend_quality_analysis",
    "valuation_analysis",
    "technical_analysis",
    "industry_analysis",
    "news_event_analysis",
    "sentiment_analysis",
    "bull_case",
    "bear_case",
    "synthesis",
    "final_report",
]


class Checkpointer:
    def __init__(self, issue_dir: Path):
        self.dir = issue_dir / "checkpoints"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.dir / "manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        if self.manifest_path.exists():
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return {"completed_steps": [], "call_log": []}

    def _save_manifest(self):
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
        self.manifest["completed_steps"].append(step)
        self.manifest["call_log"].append(
            {
                "role": step,
                "input_chars": input_chars,
                "output_chars": len(content),
                "elapsed_sec": round(elapsed_sec, 1),
            }
        )
        self._save_manifest()  # 이 단계까지는 확정적으로 디스크에 남는다


def _extract_section(raw_text: str, tag: str) -> str:
    marker = f"## {tag}"
    start = raw_text.index(marker)
    rest = raw_text[start:]
    next_header = rest.find("\n## ", 1)
    section = rest if next_header == -1 else rest[:next_header]
    return section.strip()


def _run_step(cp: Checkpointer, step: str, fn, *args) -> str:
    if cp.has(step):
        # 이미 완료된 단계 — Engine을 재호출하지 않고 체크포인트에서 읽는다.
        return cp.load(step)
    input_len = sum(len(a) for a in args)
    t0 = time.monotonic()
    output = fn(*args)  # 여기서 예외(TimeoutExpired 등)가 나면 저장 없이 그대로 전파
    elapsed = time.monotonic() - t0
    cp.save(step, output, input_len, elapsed)
    return output


def run(issue_dir: Path) -> dict:
    cp = Checkpointer(issue_dir)

    raw_text = RAW_DATA_PATH.read_text(encoding="utf-8")
    limitation = _extract_section(raw_text, "데이터 한계")
    sections = {
        tag: f"{_COMPANY_HEADER}\n\n{_extract_section(raw_text, tag)}"
        for tag in _SECTION_TAGS
    }

    fundamental = _run_step(
        cp, "fundamental_analysis", agents.fundamental_analyst_fundamental_analysis,
        f"{sections['[FUNDAMENTAL]']}\n\n{limitation}",
    )
    dividend_quality = _run_step(
        cp, "dividend_quality_analysis", agents.dividend_quality_analyst_dividend_quality_analysis,
        f"{sections['[DIVIDEND_QUALITY]']}\n\n{limitation}",
    )
    valuation = _run_step(
        cp, "valuation_analysis", agents.valuation_analyst_valuation_analysis,
        f"{sections['[VALUATION]']}\n\n{limitation}",
    )
    technical = _run_step(
        cp, "technical_analysis", agents.technical_analyst_technical_analysis,
        f"{sections['[TECHNICAL]']}\n\n{limitation}",
    )
    industry = _run_step(
        cp, "industry_analysis", agents.industry_analyst_industry_analysis,
        f"{sections['[INDUSTRY]']}\n\n{limitation}",
    )
    news_event = _run_step(
        cp, "news_event_analysis", agents.news_analyst_news_event_analysis,
        f"{sections['[NEWS/EVENT]']}\n\n{limitation}",
    )
    sentiment = _run_step(
        cp, "sentiment_analysis", agents.sentiment_analyst_sentiment_analysis,
        f"{sections['[SENTIMENT]']}\n\n{limitation}",
    )

    all_analyses = (
        f"[FUNDAMENTAL ANALYSIS]\n{fundamental}\n\n"
        f"[DIVIDEND QUALITY ANALYSIS]\n{dividend_quality}\n\n"
        f"[VALUATION ANALYSIS]\n{valuation}\n\n"
        f"[TECHNICAL ANALYSIS]\n{technical}\n\n"
        f"[INDUSTRY ANALYSIS]\n{industry}\n\n"
        f"[NEWS/EVENT ANALYSIS]\n{news_event}\n\n"
        f"[SENTIMENT ANALYSIS]\n{sentiment}"
    )

    bull_case = _run_step(cp, "bull_case", agents.bull_researcher_bull_case, all_analyses)
    bear_case = _run_step(cp, "bear_case", agents.bear_researcher_bear_case, all_analyses)
    synthesis = _run_step(cp, "synthesis", agents.synthesis_judgment, bull_case, bear_case)
    final_report = _run_step(
        cp, "final_report", agents.report_writer_final_report,
        fundamental, dividend_quality, valuation, technical,
        industry, news_event, sentiment, bull_case, bear_case, synthesis,
    )

    results = {
        "fundamental_analysis.md": fundamental,
        "dividend_quality_analysis.md": dividend_quality,
        "valuation_analysis.md": valuation,
        "technical_analysis.md": technical,
        "industry_analysis.md": industry,
        "news_event_analysis.md": news_event,
        "sentiment_analysis.md": sentiment,
        "bull_case.md": bull_case,
        "bear_case.md": bear_case,
        "synthesis.md": synthesis,
        "final_report.md": final_report,
    }
    issue_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in results.items():
        (issue_dir / filename).write_text(content.rstrip() + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    trial_id = sys.argv[1] if len(sys.argv) > 1 else "trial"
    issue_dir = PROTO_ROOT / "trials" / f"checkpoint_{trial_id}"

    cp_before = Checkpointer(issue_dir)
    steps_before = list(cp_before.manifest["completed_steps"])

    t0 = time.monotonic()
    status = "success"
    try:
        run(issue_dir)
    except Exception as e:
        status = f"failed: {type(e).__name__}: {e}"
        raise
    finally:
        elapsed_total = time.monotonic() - t0
        cp_after = Checkpointer(issue_dir)
        steps_after = list(cp_after.manifest["completed_steps"])
        summary = {
            "variant": "checkpointing",
            "trial_id": trial_id,
            "timeout_seconds": 180,
            "status": status,
            "elapsed_this_invocation_sec": round(elapsed_total, 1),
            "steps_completed_before_this_invocation": steps_before,
            "steps_completed_after_this_invocation": steps_after,
            "steps_skipped_via_checkpoint_this_invocation": [
                s for s in steps_before if s in STEP_ORDER
            ],
            "steps_newly_run_this_invocation": [
                s for s in steps_after if s not in steps_before
            ],
        }
        summary_path = PROTO_ROOT / "trials" / f"checkpoint_{trial_id}_summary.json"
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
