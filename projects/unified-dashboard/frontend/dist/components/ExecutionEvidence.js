/**
 * Execution Evidence Vertical Slice — HQ의 execution(call_log)이
 * 있을 때만 표를 그린다. 값의 의미를 해석하지 않고 role/input·output
 * 크기/elapsed_sec을 있는 그대로 나열한다(HqCard와 동일한 원칙).
 * execution이 빈 배열인 HQ(Development HQ 등)는 아무것도 렌더링하지
 * 않는다 — 존재하지 않는 데이터를 표시하지 않는다.
 */
export function ExecutionEvidence({ execution }) {
    if (execution.length === 0) {
        return null;
    }
    return (React.createElement("section", { className: "execution-evidence" },
        React.createElement("h3", null, "Execution Evidence"),
        React.createElement("table", { className: "execution-table" },
            React.createElement("thead", null,
                React.createElement("tr", null,
                    React.createElement("th", null, "Team"),
                    React.createElement("th", null, "Role"),
                    React.createElement("th", null, "Input (chars)"),
                    React.createElement("th", null, "Output (chars)"),
                    React.createElement("th", null, "Elapsed (sec)"))),
            React.createElement("tbody", null, execution.map((entry, i) => (React.createElement("tr", { key: i },
                React.createElement("td", null, entry.team),
                React.createElement("td", null, entry.role),
                React.createElement("td", null, entry.input_chars),
                React.createElement("td", null, entry.output_chars),
                React.createElement("td", null, entry.elapsed_sec))))))));
}
