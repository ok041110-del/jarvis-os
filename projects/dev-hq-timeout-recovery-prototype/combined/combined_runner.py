"""Prototype E — 3종 통합(병렬화 + 출력 최적화 + Checkpointing).

`parallel/parallel_runner.py`의 Wave 구조(의존관계 그대로, 4-wave
하드코딩)와 `checkpointing/checkpoint_runner.py`의 체크포인트 구조
(단계 완료 즉시 디스크 기록 + 재실행 시 완료 단계 스킵)를 하나로
합친다. `shared/agents.py`는 PR #79에서 이미 Report Writer
instruction에 출력 길이 제약이 반영된 사본을 그대로 쓴다(출력
최적화는 이 파일을 바꾸지 않고 자동으로 포함됨). 진짜
`call_engine()`(180초, 미수정)을 그대로 쓴다.

병렬 실행과 체크포인팅을 결합할 때의 유일한 새 위험은 "여러 스레드가
동시에 완료돼 `manifest.json`에 동시에 쓰려고 하는 것"이다 —
`threading.Lock`으로 manifest 쓰기만 직렬화한다(개별 결과 파일은
스레드마다 파일명이 달라 충돌하지 않는다).

사용법: python3 combined_runner.py <trial_id>  (같은 trial_id로
재실행하면 완료된 단계는 스킵하고 이어서 실행한다 — Wave 병렬 실행
중에도 동일하게 적용된다.)
"""

import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROTO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROTO_ROOT / "shared"))

import agents  # noqa: E402  (shared/agents.py — 출력 최적화 instruction 포함, 진짜 call_engine 사용)

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


class Checkpointer:
    """checkpoint_runner.py와 동일한 파일 포맷(같은 issue_dir을 계속
    재사용할 수 있게), 다만 병렬 호출에 대비해 manifest 쓰기에 락을 건다."""

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
            # 재확인(re-check) — 동시에 두 스레드가 같은 step을 실행할 일은
            # 없지만(step 이름이 항상 서로 다름), manifest 갱신 자체는 락으로 보호한다.
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
        return cp.load(step)  # Engine 재호출 없음 — 체크포인트에서 로드
    input_len = sum(len(a) for a in args)
    t0 = time.monotonic()
    output = fn(*args)  # 여기서 예외가 나면 저장 없이 그대로 전파(그 단계만 유실)
    elapsed = time.monotonic() - t0
    cp.save(step, output, input_len, elapsed)
    return output


def run(issue_dir: Path) -> dict:
    pipeline_t0 = time.monotonic()
    cp = Checkpointer(issue_dir)

    raw_text = RAW_DATA_PATH.read_text(encoding="utf-8")
    limitation = _extract_section(raw_text, "데이터 한계")
    sections = {
        tag: f"{_COMPANY_HEADER}\n\n{_extract_section(raw_text, tag)}"
        for tag in _SECTION_TAGS
    }

    # Wave 1 — 7개 분석, 상호 독립. 이미 체크포인트된 것은 스레드를
    # 만들지 않고 즉시 디스크에서 읽는다(Engine 재호출 없음).
    wave1_jobs = {
        "fundamental_analysis": (agents.fundamental_analyst_fundamental_analysis, f"{sections['[FUNDAMENTAL]']}\n\n{limitation}"),
        "dividend_quality_analysis": (agents.dividend_quality_analyst_dividend_quality_analysis, f"{sections['[DIVIDEND_QUALITY]']}\n\n{limitation}"),
        "valuation_analysis": (agents.valuation_analyst_valuation_analysis, f"{sections['[VALUATION]']}\n\n{limitation}"),
        "technical_analysis": (agents.technical_analyst_technical_analysis, f"{sections['[TECHNICAL]']}\n\n{limitation}"),
        "industry_analysis": (agents.industry_analyst_industry_analysis, f"{sections['[INDUSTRY]']}\n\n{limitation}"),
        "news_event_analysis": (agents.news_analyst_news_event_analysis, f"{sections['[NEWS/EVENT]']}\n\n{limitation}"),
        "sentiment_analysis": (agents.sentiment_analyst_sentiment_analysis, f"{sections['[SENTIMENT]']}\n\n{limitation}"),
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
    dividend_quality = wave1_results["dividend_quality_analysis"]
    valuation = wave1_results["valuation_analysis"]
    technical = wave1_results["technical_analysis"]
    industry = wave1_results["industry_analysis"]
    news_event = wave1_results["news_event_analysis"]
    sentiment = wave1_results["sentiment_analysis"]

    all_analyses = (
        f"[FUNDAMENTAL ANALYSIS]\n{fundamental}\n\n"
        f"[DIVIDEND QUALITY ANALYSIS]\n{dividend_quality}\n\n"
        f"[VALUATION ANALYSIS]\n{valuation}\n\n"
        f"[TECHNICAL ANALYSIS]\n{technical}\n\n"
        f"[INDUSTRY ANALYSIS]\n{industry}\n\n"
        f"[NEWS/EVENT ANALYSIS]\n{news_event}\n\n"
        f"[SENTIMENT ANALYSIS]\n{sentiment}"
    )

    # Wave 2 — Bull/Bear, 상호 독립.
    wave2_t0 = time.monotonic()
    wave2_jobs = {
        "bull_case": (agents.bull_researcher_bull_case, all_analyses),
        "bear_case": (agents.bear_researcher_bear_case, all_analyses),
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

    # Wave 3 — Synthesis, 순차(Bull+Bear 둘 다 필요).
    wave3_t0 = time.monotonic()
    synthesis = _run_step(cp, "synthesis", agents.synthesis_judgment, bull_case, bear_case)
    wave3_elapsed = time.monotonic() - wave3_t0

    # Wave 4 — Final Report, 순차(전부 필요). shared/agents.py의
    # instruction에 출력 길이 제약이 이미 반영되어 있다(PR #79).
    wave4_t0 = time.monotonic()
    final_report = _run_step(
        cp, "final_report", agents.report_writer_final_report,
        fundamental, dividend_quality, valuation, technical,
        industry, news_event, sentiment, bull_case, bear_case, synthesis,
    )
    wave4_elapsed = time.monotonic() - wave4_t0

    pipeline_elapsed = time.monotonic() - pipeline_t0

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

    wave_summary = {
        "wave1_elapsed_sec": round(wave1_elapsed, 1),
        "wave2_elapsed_sec": round(wave2_elapsed, 1),
        "wave3_elapsed_sec": round(wave3_elapsed, 1),
        "wave4_elapsed_sec": round(wave4_elapsed, 1),
        "pipeline_total_elapsed_sec": round(pipeline_elapsed, 1),
    }
    return results, wave_summary


if __name__ == "__main__":
    trial_id = sys.argv[1] if len(sys.argv) > 1 else "trial"
    issue_dir = PROTO_ROOT / "trials" / f"combined_{trial_id}"

    cp_before = Checkpointer(issue_dir)
    steps_before = list(cp_before.manifest["completed_steps"])

    t0 = time.monotonic()
    status = "success"
    wave_summary = {}
    try:
        _, wave_summary = run(issue_dir)
    except Exception as e:
        status = f"failed: {type(e).__name__}: {e}"
        raise
    finally:
        elapsed_total = time.monotonic() - t0
        cp_after = Checkpointer(issue_dir)
        steps_after = list(cp_after.manifest["completed_steps"])
        summary = {
            "variant": "combined(parallel+output_opt+checkpointing)",
            "trial_id": trial_id,
            "status": status,
            "elapsed_this_invocation_sec": round(elapsed_total, 1),
            "steps_completed_before_this_invocation": steps_before,
            "steps_completed_after_this_invocation": steps_after,
            "steps_skipped_via_checkpoint_this_invocation": [s for s in steps_before],
            "steps_newly_run_this_invocation": [s for s in steps_after if s not in steps_before],
            **wave_summary,
        }
        summary_path = PROTO_ROOT / "trials" / f"combined_{trial_id}_summary.json"
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
