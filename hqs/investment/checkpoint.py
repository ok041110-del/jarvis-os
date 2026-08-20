"""단계별 산출물을 즉시 디스크에 저장하고, 재실행 시 완료된 단계를
Engine 재호출 없이 건너뛰는 파일 기반 캐시. `docs/research/
DEV-HQ-TIMEOUT-RECOVERY`류 Prototype(PR #76/#80)에서 실측 검증된
구조를 그대로 옮긴 것이며, Registry/Scheduler가 아니다 — 이 클래스는
"단계 이름 -> 파일 하나"라는 고정된 매핑 하나만 다루고, 동적 등록
API나 일반화된 조회 인터페이스를 제공하지 않는다.
"""

import json
import threading
from pathlib import Path


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
    """체크포인트가 있으면 Engine을 재호출하지 않고 디스크에서 읽는다."""
    import time

    if cp.has(step):
        return cp.load(step)
    input_len = sum(len(a) for a in args)
    t0 = time.monotonic()
    output = fn(*args)
    elapsed = time.monotonic() - t0
    cp.save(step, output, input_len, elapsed)
    return output
