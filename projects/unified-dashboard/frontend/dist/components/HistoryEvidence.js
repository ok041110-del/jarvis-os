/**
 * History Evidence Vertical Slice — HQ의 history(run 목록)가 있을
 * 때만 표를 그린다. run family/completed_steps/trader_decision/
 * final_report를 있는 그대로 나열할 뿐 해석하지 않는다(ExecutionEvidence
 * 와 동일한 원칙). 절대 실행 시각이나 정렬 순위는 표시하지 않는다
 * (Snapshot Boundary Review 결론 — 파일에 없는 값은 만들지 않음).
 * history가 빈 배열인 HQ(Development HQ 등)는 아무것도 렌더링하지
 * 않는다.
 *
 * Tasks/Progress Vertical Slice: `tasks`는 Python이 준 배열 순서
 * 그대로(완료 도착 순서) 나열한다 — Wave 순서로 재구성하지 않는다.
 * `progress_pct`가 `null`인 run은 "0%"가 아니라 "N/A"로 표시해
 * "계산할 수 없음"과 "진행 없음"을 혼동하지 않게 한다.
 */
export function HistoryEvidence({ history }) {
    if (history.length === 0) {
        return null;
    }
    return (React.createElement("section", { className: "history-evidence" },
        React.createElement("h3", null, "History (Repository Runs)"),
        React.createElement("table", { className: "history-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", null, "Team"),
                    React.createElement("th", null, "Run"),
                    React.createElement("th", null, "Family"),
                    React.createElement("th", null, "Completed Steps"),
                    React.createElement("th", null, "Tasks (\uC644\uB8CC \uB3C4\uCC29 \uC21C\uC11C)"),
                    React.createElement("th", null, "Progress"),
                    React.createElement("th", null, "Trader Decision"),
                    React.createElement("th", null, "Final Report"))),
            React.createElement("tbody", null, history.map((entry, i) => (React.createElement("tr", { key: i },
                React.createElement("td", null, entry.team),
                React.createElement("td", null, entry.run),
                React.createElement("td", null, entry.family),
                React.createElement("td", null, entry.completed_steps),
                React.createElement("td", null, entry.tasks.join(", ")),
                React.createElement("td", null, entry.progress_pct === null || entry.progress_total === null
                    ? "N/A"
                    : `${entry.completed_steps}/${entry.progress_total} (${entry.progress_pct}%)`),
                React.createElement("td", null, entry.trader_decision ?? "N/A"),
                React.createElement("td", null, entry.final_report ? "있음" : "없음"))))))));
}
