import type { HQSnapshot } from "./types.js";
import { HqCard } from "./components/HqCard.js";
import { statusColor } from "./statusColor.js";

/**
 * Global Shell — Navigation + HQ Snapshot 목록을 조합할 뿐, HQ
 * 내부 의미를 해석하지 않는다(Python `render.py`의 `render_dashboard`
 * 원칙과 동일).
 *
 * Observe-only: `public/data/snapshot.json`을 fetch로 읽기만 한다.
 * subprocess/child_process/fs로 Repository에 접근하거나 Python을
 * 실행하지 않는다 — 이 파일이 하는 유일한 I/O는 정적 JSON `fetch`다.
 */

const SNAPSHOT_URL = "./public/data/snapshot.json";

type LoadState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; snapshots: HQSnapshot[]; generatedAt: string | null };

export function App() {
  const [state, setState] = React.useState<LoadState>({ kind: "loading" });

  React.useEffect(() => {
    let cancelled = false;

    fetch(SNAPSHOT_URL)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`snapshot.json fetch 실패: HTTP ${res.status}`);
        }
        return res.json();
      })
      .then((data: { generated_at?: string; snapshots?: HQSnapshot[] }) => {
        if (cancelled) return;
        setState({
          kind: "ready",
          snapshots: data.snapshots ?? [],
          generatedAt: data.generated_at ?? null,
        });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : String(err);
        setState({ kind: "error", message });
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <>
      <header>
        <h1>Jarvis OS — Unified Dashboard (React Frontend Prototype)</h1>
        <p>
          Experimental Prototype — Production Dashboard 아님
          (projects/unified-dashboard/frontend). Observe-only, read-only
          fetch of snapshot.json.
          {state.kind === "ready" && state.generatedAt
            ? ` Snapshot generated: ${state.generatedAt}`
            : ""}
        </p>
      </header>
      <main>
        {state.kind === "loading" && <p className="status-line">Loading snapshot.json…</p>}
        {state.kind === "error" && (
          <p className="status-line error">
            snapshot.json을 불러오지 못했습니다: {state.message}. (
            <code>export_snapshot_json.py</code>를 먼저 실행했는지 확인)
          </p>
        )}
        {state.kind === "ready" && (
          <>
            <nav>
              <h3>HQ Navigation</h3>
              <ul>
                {state.snapshots.map((s) => (
                  <li key={s.identity}>
                    {s.identity}{" "}
                    <span
                      className="badge-inline"
                      style={{ backgroundColor: statusColor(s.status) }}
                    >
                      {s.status}
                    </span>
                  </li>
                ))}
              </ul>
            </nav>
            <div className="hq-cards">
              {state.snapshots.map((s) => (
                <HqCard key={s.identity} snapshot={s} />
              ))}
            </div>
          </>
        )}
      </main>
    </>
  );
}
