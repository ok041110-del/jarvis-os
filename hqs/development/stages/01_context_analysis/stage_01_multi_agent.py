"""Stage 01 Context Analysis — Multi-Agent 기반 실행 진입점(RFC-0033/
ADC-0036/ADR-0021, PRD Synthesis는 RFC-0034/ADC-0037/ADR-0022). 기존
`stage_01.py`(결정적, Engine 미호출)는 변경하지 않고 그대로 유지한다 —
이 모듈이 신규 진입점이다.

흐름(사용자 지시 순서 그대로, 재정렬하지 않음):

    User Request
        -> Multi-Agent Reasoning(Intent/Goal/Requirement/Ambiguity, 병렬)
        -> Reasoning Aggregator -> Structured Understanding
        -> GitHub Repository Adapter -> RepositorySnapshot(Tree만)
        -> Code Analysis(Structure/RelevantDiscovery/ASTCandidate, 병렬)
        -> Dependency Analysis(target이 있을 때만, 조건부)
        -> PRD/Specification Synthesis(Structured Understanding + Repository
           Context 종합, 기존 Requirement Agent 1회 재사용)
        -> Context Aggregator -> Stage 01 Output(6-key Contract, `prd` 포함)

LLM Reasoning과 Code Analysis는 병렬화하지 않는다 — Reasoning 전체가
끝나야 Code Analysis를 시작한다. PRD Synthesis는 둘 다 끝난 뒤에만
실행한다(Structured Understanding과 Repository Context 둘 다 필요)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import code_analysis  # noqa: E402
import prd_synthesis  # noqa: E402
import reasoning  # noqa: E402
from mvp.github_adapter import GitHubRepositoryAdapter  # noqa: E402
from mvp.parallel_runner import ParallelRunner, ParallelTask, RetryPolicy  # noqa: E402

DEFAULT_REPOSITORY_OWNER = "ok041110-del"
DEFAULT_REPOSITORY_NAME = "jarvis-os"

# LLM 호출은 일시적 오류(RuntimeError, `call_engine_via_omniroute` 계약)에
# 한해서만 제한적으로 재시도한다(§5) — 스키마 검증 실패(`AgentOutputError`)는
# 재시도하지 않고 즉시 INVALID_OUTPUT으로 분류한다.
_AGENT_RETRY_POLICY = RetryPolicy(max_attempts=2, retry_on=(RuntimeError,))
_AGENT_TIMEOUT_SECONDS = 180.0
_CODE_ANALYSIS_TIMEOUT_SECONDS = 60.0


def _run_reasoning_phase(issue: dict, runner: ParallelRunner) -> dict:
    tasks = [
        ParallelTask(
            task_id=task_id,
            executor=agent_fn,
            input=issue,
            timeout=_AGENT_TIMEOUT_SECONDS,
            retry_policy=_AGENT_RETRY_POLICY,
            invalid_output_errors=(reasoning.AgentOutputError,),
        )
        for task_id, agent_fn in reasoning.AGENT_FUNCTIONS.items()
    ]
    batch_result = runner.run(tasks)
    return reasoning.aggregate_reasoning(batch_result)


def _run_code_analysis_phase(snapshot, fetch_content, issue: dict, search_specification: dict, runner: ParallelRunner):
    tasks = [
        ParallelTask(
            task_id="structure",
            executor=lambda _snapshot: code_analysis.structure_analysis(_snapshot),
            input=snapshot,
            timeout=_CODE_ANALYSIS_TIMEOUT_SECONDS,
        ),
        ParallelTask(
            task_id="relevant_discovery",
            executor=lambda _snapshot: code_analysis.relevant_discovery(
                _snapshot, fetch_content, issue, search_specification
            ),
            input=snapshot,
            timeout=_CODE_ANALYSIS_TIMEOUT_SECONDS,
        ),
        ParallelTask(
            task_id="ast_candidate",
            executor=lambda _snapshot: code_analysis.ast_candidate_analysis(_snapshot, fetch_content),
            input=snapshot,
            timeout=_CODE_ANALYSIS_TIMEOUT_SECONDS,
        ),
    ]
    return runner.run(tasks)


def run_stage_01_multi_agent(
    issue: dict,
    target: tuple | None = None,
    owner: str = DEFAULT_REPOSITORY_OWNER,
    repo: str = DEFAULT_REPOSITORY_NAME,
    ref: str | None = None,
    adapter: GitHubRepositoryAdapter | None = None,
    runner: ParallelRunner | None = None,
) -> dict:
    """Stage 01 Multi-Agent 진입점. `stages/contracts.py::
    ContextAnalysisResult`의 6-key 출력(`prd` 포함, RFC-0034/ADC-0037/
    ADR-0022)을 반환한다. `adapter`/`runner`는 테스트에서 대체 가능하도록
    주입 지점으로 남긴다(GitHub API/스레드풀을 직접 강제하지 않음)."""
    from mvp.parallel_runner import TaskStatus  # 지연 import — 순환 의존 회피

    runner = runner or ParallelRunner(max_workers=4)
    adapter = adapter or GitHubRepositoryAdapter()

    # 1) Multi-Agent Reasoning 전체 완료 (Code Analysis와 병렬화하지 않음)
    structured_understanding = _run_reasoning_phase(issue, runner)

    # 2) GitHub Repository Adapter -> RepositorySnapshot (Tree만, 파일은
    #    Code Analysis가 필요한 만큼만 지연 fetch — §7 preload 금지)
    snapshot = adapter.build_snapshot(owner, repo, ref, paths_to_fetch=[])

    fetch_cache: dict = {}

    def fetch_content(path: str):
        if path not in fetch_cache:
            try:
                repo_file = adapter.get_file_content(owner, repo, path, snapshot.ref)
                fetch_cache[path] = repo_file.content
            except Exception:  # noqa: BLE001 — 결정적 분석에서 개별 파일 실패는 스킵
                fetch_cache[path] = None
        return fetch_cache[path]

    # 3) Code Analysis(Structure/RelevantDiscovery/ASTCandidate) — 병렬 실행
    code_analysis_batch = _run_code_analysis_phase(
        snapshot, fetch_content, issue, structured_understanding["search_specification"], runner
    )

    directory_structure = []
    context_bundle = {}
    candidate_index = ""
    for result in code_analysis_batch.results:
        if result.status != TaskStatus.SUCCESS:
            continue
        if result.task_id == "structure":
            directory_structure = result.output
        elif result.task_id == "relevant_discovery":
            context_bundle = result.output
        elif result.task_id == "ast_candidate":
            candidate_index = result.output

    # 4) Dependency Analysis — target이 명확히 주어졌을 때만(조건부, §8)
    dependency_closure = code_analysis.dependency_analysis(target) if target is not None else None

    # 5) PRD/Specification Synthesis — Reasoning과 Code Analysis가 둘 다
    #    끝난 뒤에만 실행(둘 다 입력으로 필요, RFC-0034)
    prd = prd_synthesis.synthesize_prd(
        issue=issue,
        structured_understanding=structured_understanding,
        context_bundle=context_bundle,
        directory_structure=directory_structure,
        candidate_index=candidate_index,
    )

    # 6) Context Aggregator -> Stage 01 Output Contract(6-key, `prd` 포함)
    return code_analysis.aggregate_context(
        directory_structure=directory_structure,
        context_bundle=context_bundle,
        candidate_index=candidate_index,
        target=target,
        dependency_closure=dependency_closure,
        prd=prd,
    )
