import type { PresentationState } from "../types.js";
import { statusColor } from "../statusColor.js";

/**
 * Global Shell Header — 현재 Dashboard 위치("Overview")와 전체
 * System Status(overallStatus.ts가 계산한 값)만 표시한다. HQ 내부
 * 값을 직접 참조하지 않는다.
 */

export function Header({
  location,
  overall,
  generatedAt,
}: {
  location: string;
  overall: PresentationState;
  generatedAt: string | null;
}) {
  return (
    <header className="shell-header">
      <div className="shell-header-title">
        <h1>Jarvis OS — Unified Dashboard (React Frontend Prototype)</h1>
        <p className="shell-location">현재 위치: {location}</p>
      </div>
      <div className="shell-header-status">
        <span
          className="badge system-status-badge"
          style={{ backgroundColor: statusColor(overall) }}
        >
          System Status: {overall}
        </span>
        {generatedAt && <p className="shell-generated-at">Snapshot generated: {generatedAt}</p>}
      </div>
    </header>
  );
}
