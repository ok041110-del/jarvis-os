import type { PresentationState } from "./types.js";

/** Global Shell과 HQ Card가 공유하는 상태 배지 색상표. */
export const STATE_COLOR: Record<PresentationState | string, string> = {
  NORMAL: "#2e7d32",
  WORKING: "#f9a825",
  BLOCKED: "#c62828",
  DEFERRED: "#616161",
  UNKNOWN: "#9e9e9e",
};

export function statusColor(status: string): string {
  return STATE_COLOR[status] ?? STATE_COLOR.UNKNOWN;
}
