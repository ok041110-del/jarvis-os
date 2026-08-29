import type { HistoryRunEntry } from "../types.js";

/**
 * History Evidence Vertical Slice — HQ의 history(run 목록)가 있을
 * 때만 표를 그린다. run family/completed_steps/trader_decision/
 * final_report를 있는 그대로 나열할 뿐 해석하지 않는다(ExecutionEvidence
 * 와 동일한 원칙). commit_order는 "Repository commit order"로만
 * 표기한다 — 실행 시각으로 오해되지 않도록 이름 자체를 그렇게 쓴다.
 * history가 빈 배열인 HQ(Development HQ 등)는 아무것도 렌더링하지
 * 않는다.
 */
export function HistoryEvidence({ history }: { history: HistoryRunEntry[] }) {
  if (history.length === 0) {
    return null;
  }

  return (
    <section className="history-evidence">
      <h3>History (Repository Runs)</h3>
      <table className="history-table">
        <thead>
          <tr>
            <th>Team</th>
            <th>Run</th>
            <th>Family</th>
            <th>Completed Steps</th>
            <th>Trader Decision</th>
            <th>Final Report</th>
            <th>Repository commit order</th>
          </tr>
        </thead>
        <tbody>
          {history.map((entry, i) => (
            <tr key={i}>
              <td>{entry.team}</td>
              <td>{entry.run}</td>
              <td>{entry.family}</td>
              <td>{entry.completed_steps}</td>
              <td>{entry.trader_decision ?? "N/A"}</td>
              <td>{entry.final_report ? "있음" : "없음"}</td>
              <td>{entry.commit_order ?? "N/A"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
