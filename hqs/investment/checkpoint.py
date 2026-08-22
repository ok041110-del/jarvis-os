"""단계별 산출물을 즉시 저장하고 재실행 시 완료된 단계를 건너뛰는
파일 기반 캐시(PR #76/#80 실측 검증). 고정 매핑만 다루는 Registry/Scheduler 아님."""

import json
import threading
from pathlib import Path

# 실제 관찰된 시그니처만(추측 추가 금지) — EVIDENCE.md 재현값.
_KNOWN_CONTENT_FAILURE_PREFIXES = ("API Error:",)


class ContentFailureError(RuntimeError):
    """콘텐츠 실패 시그니처일 때 저장 대신 발생 — 저장되지 않으므로
    다음 실행에서 자동 재시도(Resume) 대상이 된다."""


def _is_known_content_failure(output: str) -> bool:
    stripped = output.strip()
    return any(stripped.startswith(prefix) for prefix in _KNOWN_CONTENT_FAILURE_PREFIXES)


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


def run_step(cp: Checkpointer, step: str, fn, *args) -> str:
    """체크포인트가 있으면 재호출 없이 디스크에서 읽는다. 콘텐츠 실패
    시그니처면 저장하지 않고 `ContentFailureError`를 발생시킨다."""
    import time

    if cp.has(step):
        return cp.load(step)
    input_len = sum(len(a) for a in args)
    t0 = time.monotonic()
    output = fn(*args)
    elapsed = time.monotonic() - t0
    if _is_known_content_failure(output):
        raise ContentFailureError(
            f"step '{step}' returned a known content failure signature: {output[:200]!r}"
        )
    cp.save(step, output, input_len, elapsed)
    return output
