"""Test Workspace — 격리된 pytest 실행 환경(`STAGE05-TEST-ISOLATION-
VALIDATION-0001.md` §1.4/§8 실측 결론을 그대로 구현).

Workspace = repository working tree 전체 복사(`.git` 제외) + Stage 04
Implementation 적용. 원본 repository는 어떤 경로로도 쓰지 않는다 —
모든 쓰기는 이 모듈이 만든 임시 디렉터리 안에서만 일어난다.

이 모듈은 Production `hqs/development/`를 import하지 않는다 — 대상
repository 경로는 호출자가 명시적으로 전달한다(이 Harness가 임의
repository를 가리키게 하지 않기 위한 격리 확인, `projects/`
관례와 동일)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path


class WorkspaceCreationError(RuntimeError):
    """Workspace 복사 자체가 실패했을 때(디스크/권한 등)."""


class ImplementationApplyError(RuntimeError):
    """Implementation을 Workspace 내부 대상 파일에 쓰는 데 실패했을 때."""


@dataclass
class WorkspaceCleanupResult:
    attempted: bool
    succeeded: bool
    error: str | None = None


class TestWorkspace:
    """단일 실행에 대응하는 1회용 Workspace. `create()` -> `apply_implementation()`
    -> `run_pytest()` -> `cleanup()` 순서로 사용한다. 각 단계의 실패는
    별도 예외/결과로 구분되며, 어떤 실패도 원본 repository에 영향을
    주지 않는다(원본은애초에 이 클래스가 쓰기 대상으로 삼지 않는다)."""

    def __init__(self, source_repo_root: Path, *, base_tmp_dir: Path | None = None):
        self.source_repo_root = Path(source_repo_root).resolve()
        self._base_tmp_dir = Path(base_tmp_dir) if base_tmp_dir else Path(tempfile.gettempdir())
        self.workspace_root: Path | None = None
        self._created = False

    def create(self) -> Path:
        """`.git` 제외 전체 working tree 복사. 실패 시 `WorkspaceCreationError`."""
        target = self._base_tmp_dir / f"stage05-test-workspace-{uuid.uuid4().hex[:12]}"
        try:
            target.mkdir(parents=True, exist_ok=False)
            proc = subprocess.run(
                [
                    "tar",
                    "--exclude=.git",
                    "--exclude=__pycache__",
                    "--exclude=.pytest_cache",
                    "-cf",
                    "-",
                    "-C",
                    str(self.source_repo_root),
                    ".",
                ],
                stdout=subprocess.PIPE,
                check=True,
            )
            subprocess.run(
                ["tar", "-xf", "-", "-C", str(target)],
                input=proc.stdout,
                check=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise WorkspaceCreationError(f"Test Workspace 생성 실패: {exc}") from exc
        self.workspace_root = target
        self._created = True
        return target

    def apply_implementation(self, relative_target_path: str, implementation: str) -> None:
        """Workspace 내부(repository 밖 절대 없음) 대상 파일을 Implementation으로
        덮어쓴다. `relative_target_path`는 repository root 기준 상대 경로여야
        한다(예: `hqs/development/mvp/agents/backend.py`) — 이 밖으로 나가는
        경로(`..` 포함)는 거부한다."""
        if not self._created or self.workspace_root is None:
            raise ImplementationApplyError("Workspace가 아직 생성되지 않았다 — create() 선행 필요")
        rel = Path(relative_target_path)
        if rel.is_absolute() or ".." in rel.parts:
            raise ImplementationApplyError(f"허용되지 않는 대상 경로: {relative_target_path!r}")
        target_path = self.workspace_root / rel
        if not target_path.is_relative_to(self.workspace_root):
            raise ImplementationApplyError(f"Workspace 밖 경로로 이탈: {relative_target_path!r}")
        try:
            target_path.write_text(implementation, encoding="utf-8")
        except OSError as exc:
            raise ImplementationApplyError(f"Implementation 적용 실패: {exc}") from exc

    def run_pytest(self, relative_tests_dir: str, *, pytest_bin: str = "/root/.local/bin/pytest") -> dict:
        """Workspace 내부에서 pytest를 실행한다. 원본 repository는 참조하지
        않는다(cwd·경로 전부 Workspace 내부로 고정). 실패(비정상 종료 포함)는
        예외를 던지지 않고 구조화된 dict로 반환한다 — pytest FAIL과 실행
        자체의 실패(예: 바이너리 없음)를 `executed` 필드로 구분한다."""
        if not self._created or self.workspace_root is None:
            return {"executed": False, "returncode": None, "output": "", "error": "workspace not created"}
        tests_path = self.workspace_root / relative_tests_dir
        try:
            proc = subprocess.run(
                [pytest_bin, str(tests_path), "-q", "-p", "no:cacheprovider"],
                capture_output=True,
                text=True,
                cwd=str(self.workspace_root),
                timeout=300,
            )
            return {
                "executed": True,
                "returncode": proc.returncode,
                "output": (proc.stdout + proc.stderr)[-4000:],
                "error": None,
            }
        except subprocess.TimeoutExpired as exc:
            return {"executed": False, "returncode": None, "output": "", "error": f"timeout: {exc}"}
        except OSError as exc:
            return {"executed": False, "returncode": None, "output": "", "error": f"pytest 실행 실패: {exc}"}

    def cleanup(self) -> WorkspaceCleanupResult:
        """Workspace 삭제. 실패해도 원본 repository는 절대 영향받지 않는다
        (Workspace는 원본과 물리적으로 분리된 별도 경로였을 뿐이므로) — 이
        메서드의 실패는 디스크 공간 누수일 뿐이라는 것을 호출자가 확인할 수
        있도록 결과를 구조화해 반환한다."""
        if self.workspace_root is None:
            return WorkspaceCleanupResult(attempted=False, succeeded=True)
        try:
            shutil.rmtree(self.workspace_root)
            return WorkspaceCleanupResult(attempted=True, succeeded=True)
        except OSError as exc:
            return WorkspaceCleanupResult(attempted=True, succeeded=False, error=str(exc))
