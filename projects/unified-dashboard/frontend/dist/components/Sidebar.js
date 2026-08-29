import { statusColor } from "../statusColor.js";
/**
 * Global Shell Navigation — 현재는 Overview 단일 화면만 존재한다.
 * HQ별 하위 화면/Multi-HQ Routing은 이 Prototype 범위 밖(ADC-0018 Defer).
 * 각 HQ 항목은 snapshot.json에 이미 있는 identity/status를 그대로
 * 노출할 뿐, 클릭해도 별도 화면으로 이동하지 않는다(같은 Overview
 * 안의 앵커일 뿐).
 */
export function Sidebar({ snapshots }) {
    return (React.createElement("aside", { className: "sidebar" },
        React.createElement("div", { className: "sidebar-section" },
            React.createElement("h3", null, "Dashboard"),
            React.createElement("ul", null,
                React.createElement("li", { className: "nav-current" }, "Overview"))),
        React.createElement("div", { className: "sidebar-section" },
            React.createElement("h3", null, "HQ"),
            React.createElement("ul", null, snapshots.map((s) => (React.createElement("li", { key: s.identity },
                React.createElement("a", { href: `#hq-${s.identity}` }, s.identity),
                " ",
                React.createElement("span", { className: "badge-inline", style: { backgroundColor: statusColor(s.status) } }, s.status))))))));
}
