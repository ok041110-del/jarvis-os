/**
 * History Evidence Vertical Slice — HQ의 history(run 목록)가 있을
 * 때만 표를 그린다. run family/completed_steps/trader_decision/
 * final_report를 있는 그대로 나열할 뿐 해석하지 않는다(ExecutionEvidence
 * 와 동일한 원칙). commit_order는 "Repository commit order"로만
 * 표기한다 — 실행 시각으로 오해되지 않도록 이름 자체를 그렇게 쓴다.
 * history가 빈 배열인 HQ(Development HQ 등)는 아무것도 렌더링하지
 * 않는다.
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
                    React.createElement("th", null, "Trader Decision"),
                    React.createElement("th", null, "Final Report"),
                    React.createElement("th", null, "Repository commit order"))),
            React.createElement("tbody", null, history.map((entry, i) => (React.createElement("tr", { key: i },
                React.createElement("td", null, entry.team),
                React.createElement("td", null, entry.run),
                React.createElement("td", null, entry.family),
                React.createElement("td", null, entry.completed_steps),
                React.createElement("td", null, entry.trader_decision ?? "N/A"),
                React.createElement("td", null, entry.final_report ? "있음" : "없음"),
                React.createElement("td", null, entry.commit_order ?? "N/A"))))))));
}
