import { statusColor } from "../statusColor.js";
/**
 * HQ View 책임 — 자신에게 주어진 HQSnapshot 하나를 그대로 표시할
 * 뿐, 값의 의미를 해석하지 않는다(Python `render.py`의
 * `_render_hq_card`와 동일한 원칙).
 */
export function HqCard({ snapshot }) {
    const color = statusColor(snapshot.status);
    return (React.createElement("section", { className: "hq-card" },
        React.createElement("h2", null,
            snapshot.identity,
            " ",
            React.createElement("span", { className: "badge", style: { backgroundColor: color } }, snapshot.status)),
        React.createElement("ul", null, snapshot.detail.map((line, i) => (React.createElement("li", { key: i }, line)))),
        snapshot.deferred.length > 0 && (React.createElement(React.Fragment, null,
            React.createElement("h3", { className: "deferred-heading" }, "Deferred (\uC758\uB3C4\uC801 \uBBF8\uAD6C\uD604)"),
            React.createElement("ul", null, snapshot.deferred.map((item, i) => (React.createElement("li", { key: i },
                item,
                " \u2014 ",
                React.createElement("em", null, "DEFERRED"))))))),
        React.createElement("p", { className: "source" },
            "Source: ",
            snapshot.source_files.join(", ") || "N/A")));
}
