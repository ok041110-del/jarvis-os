import type { HQSnapshot } from "../types.js";
import { statusColor } from "../statusColor.js";

/**
 * HQ View 책임 — 자신에게 주어진 HQSnapshot 하나를 그대로 표시할
 * 뿐, 값의 의미를 해석하지 않는다(Python `render.py`의
 * `_render_hq_card`와 동일한 원칙).
 */

export function HqCard({ snapshot }: { snapshot: HQSnapshot }) {
  const color = statusColor(snapshot.status);

  return (
    <section className="hq-card">
      <h2>
        {snapshot.identity}{" "}
        <span className="badge" style={{ backgroundColor: color }}>
          {snapshot.status}
        </span>
      </h2>
      <ul>
        {snapshot.detail.map((line, i) => (
          <li key={i}>{line}</li>
        ))}
      </ul>
      {snapshot.deferred.length > 0 && (
        <>
          <h3 className="deferred-heading">Deferred (의도적 미구현)</h3>
          <ul>
            {snapshot.deferred.map((item, i) => (
              <li key={i}>
                {item} — <em>DEFERRED</em>
              </li>
            ))}
          </ul>
        </>
      )}
      <p className="source">
        Source: {snapshot.source_files.join(", ") || "N/A"}
      </p>
    </section>
  );
}
