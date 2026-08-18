import subprocess
import tempfile

ENGINE_CLI = "claude"

DISALLOWED_TOOLS = "Write,Edit,Bash,Read,Glob,Grep,NotebookEdit,WebFetch,WebSearch"

STATELESS_CALL_NOTICE = (
    "You are being invoked as a stateless text-in/text-out function call, "
    "not an interactive coding session. You have no filesystem or shell "
    "tools available on this call, and that is expected and permanent — "
    "do not report it, apologize for it, or ask for permissions. Respond "
    "only with the requested content as plain text."
)


def call_engine_with_timeout(prompt: str, timeout_seconds: int) -> str:
    result = subprocess.run(
        [
            ENGINE_CLI, "-p", prompt,
            "--output-format", "text",
            "--disallowedTools", DISALLOWED_TOOLS,
            "--append-system-prompt", STATELESS_CALL_NOTICE,
        ],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        cwd=tempfile.gettempdir(),
    )
    return result.stdout
