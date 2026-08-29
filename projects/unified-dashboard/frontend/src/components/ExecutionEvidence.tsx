import type { ExecutionCallLogEntry } from "../types.js";

/**
 * Execution Evidence Vertical Slice — HQ의 execution(call_log)이
 * 있을 때만 표를 그린다. 값의 의미를 해석하지 않고 role/input·output
 * 크기/elapsed_sec을 있는 그대로 나열한다(HqCard와 동일한 원칙).
 * execution이 빈 배열인 HQ(Development HQ 등)는 아무것도 렌더링하지
 * 않는다 — 존재하지 않는 데이터를 표시하지 않는다.
 */
export function ExecutionEvidence({ execution }: { execution: ExecutionCallLogEntry[] }) {
  if (execution.length === 0) {
    return null;
  }

  return (
    <section className="execution-evidence">
      <h3>Execution Evidence</h3>
      <table className="execution-table">
        <thead>
          <tr>
            <th>Team</th>
            <th>Role</th>
            <th>Input (chars)</th>
            <th>Output (chars)</th>
            <th>Elapsed (sec)</th>
          </tr>
        </thead>
        <tbody>
          {execution.map((entry, i) => (
            <tr key={i}>
              <td>{entry.team}</td>
              <td>{entry.role}</td>
              <td>{entry.input_chars}</td>
              <td>{entry.output_chars}</td>
              <td>{entry.elapsed_sec}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
