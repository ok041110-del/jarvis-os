/**
 * Unified Dashboard Frontend Prototype — Experimental Prototype 타입.
 *
 * Python `snapshot.py`의 `HQSnapshot` dataclass를 그대로 미러링한다.
 * Public Contract가 아니다 — 공식 HQDashboardSnapshot(아직 저장소에
 * 존재하지 않는 Architecture 문서가 제안한 Contract)을 Freeze하지
 * 않는다. 필드를 추가/변경하려면 Python 쪽 `HQSnapshot`을 먼저
 * 바꾸고 이 파일을 그에 맞춰 갱신한다 — 이 파일이 먼저 앞서가지
 * 않는다.
 */

export type PresentationState =
  | "NORMAL"
  | "WORKING"
  | "BLOCKED"
  | "DEFERRED"
  | "UNKNOWN";

/**
 * Investment HQ Execution Evidence Vertical Slice로 추가된 Experimental
 * 필드 — 기존 `checkpoints/manifest.json`의 `call_log` 항목 하나를
 * 그대로 미러링한다. Python 쪽 `HQSnapshot.execution` dict 항목과
 * 동일한 키만 갖는다. Public Contract가 아니다.
 */
/**
 * `run`은 Execution Evidence — 전체 History Run 확장 Vertical Slice로
 * 추가됐다 — 팀별 대표 run 1개만 보이던 것을 실제 존재하는 9개 run
 * 전체로 넓히면서 각 항목이 어느 run에서 왔는지 구분하기 위해
 * 추가했다. `HistoryRunEntry.run`과 같은 디렉터리명이다.
 */
export interface ExecutionCallLogEntry {
  team: string;
  run: string;
  role: string;
  input_chars: number;
  output_chars: number;
  elapsed_sec: number;
}

/**
 * Investment HQ History Vertical Slice로 추가된 Experimental 필드 —
 * `hqs/investment/dogfooding/`의 실제 run 디렉터리 하나를 그대로
 * 요약한다. Python 쪽 `HQSnapshot.history` dict 항목과 동일한 키만
 * 갖는다. 정렬은 디렉터리명 오름차순일 뿐이며 절대 실행 시각을
 * 담은 필드는 없다(Snapshot Boundary Review 결론 — git 등 외부
 * 프로세스 조회 없음). `trader_decision`이 null인 run은 애초에
 * `trader_decision.md` 자체가 없는 계열(hq-verify 등)이다. Public
 * Contract가 아니다.
 *
 * `tasks`는 Investment HQ Tasks/Progress Vertical Slice로 추가된
 * 필드다 — `manifest.json`의 `completed_steps`를 그대로 옮긴 것이며,
 * 배열 순서는 **완료 도착 순서**다(병렬 실행되는 Wave1 분석 단계들의
 * 저장 순서일 뿐, `teams/*.py`가 정의한 Wave 실행 순서가 아니다).
 * Frontend는 이 순서를 재구성하거나 Wave 단위로 재배열하지 않는다.
 *
 * `progress_total`/`progress_pct`는 같은 Vertical Slice로 추가됐다 —
 * `trader_decision` 단계가 실제로 관측된 run(현재 `trader-verify`
 * 계열)에만 값이 채워진다. `synthesis` 패턴의 레거시 run(`hq-verify`
 * 등)은 Task 구성 자체가 달라 분모를 알 수 없으므로 둘 다 `null`이다
 * — "진행률 0%"가 아니라 "계산할 수 없음"을 뜻한다.
 *
 * `trader_decision_detail`은 Trader Decision Rationale/Reassess
 * Vertical Slice로 추가됐다 — 기존 `trader_decision`(Direction 한
 * 단어)이 읽던 같은 `trader_decision.md`에서 Rationale/Reassess when을
 * 추가로 노출한다. `trader_decision.md`가 없는 run은 `null`이다(빈
 * 문자열·placeholder 아님). `trader_decision` 필드 자체의 의미는
 * 바뀌지 않는다(하위 호환).
 */
export interface TraderDecisionDetail {
  action: string | null;
  rationale: string | null;
  reassess_when: string | null;
}

export interface HistoryRunEntry {
  team: string;
  run: string;
  family: string;
  completed_steps: number;
  tasks: string[];
  trader_decision: string | null;
  trader_decision_detail: TraderDecisionDetail | null;
  final_report: boolean;
  progress_total: number | null;
  progress_pct: number | null;
}

export interface HQSnapshot {
  identity: string;
  status: PresentationState;
  detail: string[];
  deferred: string[];
  source_files: string[];
  execution: ExecutionCallLogEntry[];
  history: HistoryRunEntry[];
}
