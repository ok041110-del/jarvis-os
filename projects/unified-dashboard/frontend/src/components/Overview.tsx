import type { HQSnapshot } from "../types.js";
import { HqCard } from "./HqCard.js";
import { ExecutionEvidence } from "./ExecutionEvidence.js";
import { HistoryEvidence } from "./HistoryEvidence.js";

/**
 * Overview 화면 — snapshot.json이 제공하는 HQSnapshot 목록을 HqCard +
 * ExecutionEvidence + HistoryEvidence로 나열할 뿐이다. Task 등 Snapshot에
 * 아직 없는 데이터는 표시하지 않는다(존재하지 않는 Backend 데이터를
 * 임의로 만들지 않음). Global Shell은 history/execution의 HQ-specific
 * 의미를 해석하지 않고 각 Evidence 컴포넌트에 그대로 위임한다.
 */

export function Overview({ snapshots }: { snapshots: HQSnapshot[] }) {
  return (
    <section className="overview">
      <h2>Overview</h2>
      <div className="hq-cards">
        {snapshots.map((s) => (
          <div id={`hq-${s.identity}`} key={s.identity}>
            <HqCard snapshot={s} />
            <ExecutionEvidence execution={s.execution} />
            <HistoryEvidence history={s.history} />
          </div>
        ))}
      </div>
    </section>
  );
}
