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
export function App() {
    const [state, setState] = React.useState({ kind: "loading" });
    React.useEffect(() => {
        let cancelled = false;
        fetch(SNAPSHOT_URL)
            .then((res) => {
            if (!res.ok) {
                throw new Error(`snapshot.json fetch 실패: HTTP ${res.status}`);
            }
            return res.json();
        })
            .then((data) => {
            if (cancelled)
                return;
            setState({
                kind: "ready",
                snapshots: data.snapshots ?? [],
                generatedAt: data.generated_at ?? null,
            });
        })
            .catch((err) => {
            if (cancelled)
                return;
            const message = err instanceof Error ? err.message : String(err);
            setState({ kind: "error", message });
        });
        return () => {
            cancelled = true;
        };
    }, []);
    if (state.kind === "loading") {
        return (React.createElement("div", { className: "shell" },
            React.createElement("p", { className: "status-line" }, "Loading snapshot.json\u2026")));
    }
    if (state.kind === "error") {
        return (React.createElement("div", { className: "shell" },
            React.createElement("p", { className: "status-line error" },
                "snapshot.json\uC744 \uBD88\uB7EC\uC624\uC9C0 \uBABB\uD588\uC2B5\uB2C8\uB2E4: ",
                state.message,
                ". (",
                React.createElement("code", null, "export_snapshot_json.py"),
                "\uB97C \uBA3C\uC800 \uC2E4\uD589\uD588\uB294\uC9C0 \uD655\uC778)")));
    }
    return (React.createElement("div", { className: "shell" },
        React.createElement(Header, { location: "Overview", overall: overallStatus(state.snapshots), generatedAt: state.generatedAt }),
        React.createElement("div", { className: "shell-body" },
            React.createElement(Sidebar, { snapshots: state.snapshots }),
            React.createElement("main", { className: "shell-main" },
                React.createElement(Overview, { snapshots: state.snapshots })))));
}
