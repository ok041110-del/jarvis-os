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
    return (React.createElement(React.Fragment, null,
        React.createElement("header", null,
            React.createElement("h1", null, "Jarvis OS \u2014 Unified Dashboard (React Frontend Prototype)"),
            React.createElement("p", null,
                "Experimental Prototype \u2014 Production Dashboard \uC544\uB2D8 (projects/unified-dashboard/frontend). Observe-only, read-only fetch of snapshot.json.",
                state.kind === "ready" && state.generatedAt
                    ? ` Snapshot generated: ${state.generatedAt}`
                    : "")),
        React.createElement("main", null,
            state.kind === "loading" && React.createElement("p", { className: "status-line" }, "Loading snapshot.json\u2026"),
            state.kind === "error" && (React.createElement("p", { className: "status-line error" },
                "snapshot.json\uC744 \uBD88\uB7EC\uC624\uC9C0 \uBABB\uD588\uC2B5\uB2C8\uB2E4: ",
                state.message,
                ". (",
                React.createElement("code", null, "export_snapshot_json.py"),
                "\uB97C \uBA3C\uC800 \uC2E4\uD589\uD588\uB294\uC9C0 \uD655\uC778)")),
            state.kind === "ready" && (React.createElement(React.Fragment, null,
                React.createElement("nav", null,
                    React.createElement("h3", null, "HQ Navigation"),
                    React.createElement("ul", null, state.snapshots.map((s) => (React.createElement("li", { key: s.identity },
                        s.identity,
                        " ",
                        React.createElement("span", { className: "badge-inline", style: { backgroundColor: statusColor(s.status) } }, s.status)))))),
                React.createElement("div", { className: "hq-cards" }, state.snapshots.map((s) => (React.createElement(HqCard, { key: s.identity, snapshot: s })))))))));
}
