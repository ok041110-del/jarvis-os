"""`hqs/development/cli.py`(CLI -> `workflow.py` 진입점) `main()` 검증.

`run_workflow()`는 재구현하지 않았으므로 여기서는 (a) CLI가 사용자
입력(Issue JSON, `--expose-target`)을 정확히 파싱해 `run_workflow()`에
그대로 전달하는지, (b) Workflow 결과를 재해석 없이 출력하는지, (c)
Workflow 실패 시 실패 상태를 명확히(stderr + non-zero exit code)
전달하는지만 mock으로 검증한다.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_CLI_PATH = Path(__file__).resolve().parents[2] / "cli.py"
_spec = importlib.util.spec_from_file_location("cli", _CLI_PATH)
cli = importlib.util.module_from_spec(_spec)
sys.modules["cli"] = cli
_spec.loader.exec_module(cli)

SAMPLE_ISSUE = {"title": "Sample Issue", "description": "Do the thing.", "status": "Open"}


def _happy_workflow_result():
    return {
        "stage_01": {"stage": 1},
        "stage_02": {"stage": 2},
        "stage_03": {"stage": 3},
        "stage_04": {"stage": 4},
        "stage_05": {"stage": 5, "verdict": "PASS"},
        "failed_at": None,
        "error": None,
    }


def test_issue_read_from_file_path_and_passed_to_run_workflow(tmp_path, monkeypatch, capsys):
    issue_path = tmp_path / "issue.json"
    issue_path.write_text(json.dumps(SAMPLE_ISSUE))

    seen = {}

    def fake_run_workflow(issue, expose_target=False):
        seen["issue"] = issue
        seen["expose_target"] = expose_target
        return _happy_workflow_result()

    monkeypatch.setattr(cli, "run_workflow", fake_run_workflow)
    monkeypatch.setattr(sys, "argv", ["cli.py", str(issue_path)])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0
    assert seen["issue"] == SAMPLE_ISSUE
    assert seen["expose_target"] is False


def test_issue_read_from_stdin_when_no_path_given(monkeypatch):
    seen = {}

    def fake_run_workflow(issue, expose_target=False):
        seen["issue"] = issue
        return _happy_workflow_result()

    monkeypatch.setattr(cli, "run_workflow", fake_run_workflow)
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    monkeypatch.setattr(sys.stdin, "read", lambda: json.dumps(SAMPLE_ISSUE))

    with pytest.raises(SystemExit):
        cli.main()

    assert seen["issue"] == SAMPLE_ISSUE


def test_expose_target_flag_is_passed_through(tmp_path, monkeypatch):
    issue_path = tmp_path / "issue.json"
    issue_path.write_text(json.dumps(SAMPLE_ISSUE))

    seen = {}

    def fake_run_workflow(issue, expose_target=False):
        seen["expose_target"] = expose_target
        return _happy_workflow_result()

    monkeypatch.setattr(cli, "run_workflow", fake_run_workflow)
    monkeypatch.setattr(sys, "argv", ["cli.py", str(issue_path), "--expose-target"])

    with pytest.raises(SystemExit):
        cli.main()

    assert seen["expose_target"] is True


def test_successful_workflow_prints_result_unmodified(tmp_path, monkeypatch, capsys):
    issue_path = tmp_path / "issue.json"
    issue_path.write_text(json.dumps(SAMPLE_ISSUE))

    monkeypatch.setattr(cli, "run_workflow", lambda issue, expose_target=False: _happy_workflow_result())
    monkeypatch.setattr(sys, "argv", ["cli.py", str(issue_path)])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed == _happy_workflow_result()


def test_workflow_failure_reports_clearly_and_exits_nonzero(tmp_path, monkeypatch, capsys):
    issue_path = tmp_path / "issue.json"
    issue_path.write_text(json.dumps(SAMPLE_ISSUE))

    failed_result = {
        "stage_01": {"stage": 1},
        "stage_02": None,
        "stage_03": None,
        "stage_04": None,
        "stage_05": None,
        "failed_at": "stage_02",
        "error": "boom",
    }
    monkeypatch.setattr(cli, "run_workflow", lambda issue, expose_target=False: failed_result)
    monkeypatch.setattr(sys, "argv", ["cli.py", str(issue_path)])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 1
    err = capsys.readouterr().err
    assert "stage_02" in err
    assert "boom" in err


def test_malformed_issue_json_exits_nonzero_with_clear_message(tmp_path, monkeypatch, capsys):
    issue_path = tmp_path / "issue.json"
    issue_path.write_text("not valid json")

    monkeypatch.setattr(sys, "argv", ["cli.py", str(issue_path)])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 1
    assert "Cannot read issue input" in capsys.readouterr().err
