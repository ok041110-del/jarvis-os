import type { HQSnapshot } from "./types.js";
import { Sidebar } from "./components/Sidebar.js";
import { Header } from "./components/Header.js";
import { Overview } from "./components/Overview.js";
import { overallStatus } from "./overallStatus.js";

/**
 * Global Shell — Header/Sidebar/Overview를 조합할 뿐, HQ 내부 의미를
 * 해석하지 않는다(Python `render.py`의 `render_dashboard` 원칙과 동일).
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

  if (state.kind === "loading") {
    return (
      <div className="shell">
        <p className="status-line">Loading snapshot.json…</p>
      </div>
    );
  }

  if (state.kind === "error") {
    return (
      <div className="shell">
        <p className="status-line error">
          snapshot.json을 불러오지 못했습니다: {state.message}. (
          <code>export_snapshot_json.py</code>를 먼저 실행했는지 확인)
        </p>
      </div>
    );
  }

  return (
    <div className="shell">
      <Header
        location="Overview"
        overall={overallStatus(state.snapshots)}
        generatedAt={state.generatedAt}
      />
      <div className="shell-body">
        <Sidebar snapshots={state.snapshots} />
        <main className="shell-main">
          <Overview snapshots={state.snapshots} />
        </main>
      </div>
    </div>
  );
}
