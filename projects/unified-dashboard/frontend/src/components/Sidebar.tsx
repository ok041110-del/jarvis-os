import type { HQSnapshot } from "../types.js";
import { statusColor } from "../statusColor.js";

/**
 * Global Shell Navigation — 현재는 Overview 단일 화면만 존재한다.
 * HQ별 하위 화면/Multi-HQ Routing은 이 Prototype 범위 밖(ADC-0018 Defer).
 * 각 HQ 항목은 snapshot.json에 이미 있는 identity/status를 그대로
 * 노출할 뿐, 클릭해도 별도 화면으로 이동하지 않는다(같은 Overview
 * 안의 앵커일 뿐).
 */

export function Sidebar({ snapshots }: { snapshots: HQSnapshot[] }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <h3>Dashboard</h3>
        <ul>
          <li className="nav-current">Overview</li>
        </ul>
      </div>
      <div className="sidebar-section">
        <h3>HQ</h3>
        <ul>
          {snapshots.map((s) => (
            <li key={s.identity}>
              <a href={`#hq-${s.identity}`}>{s.identity}</a>{" "}
              <span
                className="badge-inline"
                style={{ backgroundColor: statusColor(s.status) }}
              >
                {s.status}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
