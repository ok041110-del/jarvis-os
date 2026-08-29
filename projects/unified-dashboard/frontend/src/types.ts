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
export interface ExecutionCallLogEntry {
  team: string;
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
 */
export interface HistoryRunEntry {
  team: string;
  run: string;
  family: string;
  completed_steps: number;
  trader_decision: string | null;
  final_report: boolean;
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
