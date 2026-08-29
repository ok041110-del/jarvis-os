import { statusColor } from "../statusColor.js";
/**
 * Global Shell Header — 현재 Dashboard 위치("Overview")와 전체
 * System Status(overallStatus.ts가 계산한 값)만 표시한다. HQ 내부
 * 값을 직접 참조하지 않는다.
 */
export function Header({ location, overall, generatedAt, }) {
    return (React.createElement("header", { className: "shell-header" },
        React.createElement("div", { className: "shell-header-title" },
            React.createElement("h1", null, "Jarvis OS \u2014 Unified Dashboard (React Frontend Prototype)"),
            React.createElement("p", { className: "shell-location" },
                "\uD604\uC7AC \uC704\uCE58: ",
                location)),
        React.createElement("div", { className: "shell-header-status" },
            React.createElement("span", { className: "badge system-status-badge", style: { backgroundColor: statusColor(overall) } },
                "System Status: ",
                overall),
            generatedAt && React.createElement("p", { className: "shell-generated-at" },
                "Snapshot generated: ",
                generatedAt))));
}
