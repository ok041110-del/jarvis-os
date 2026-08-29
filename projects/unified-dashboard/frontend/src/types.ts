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

export interface HQSnapshot {
  identity: string;
  status: PresentationState;
  detail: string[];
  deferred: string[];
  source_files: string[];
  execution: ExecutionCallLogEntry[];
}
