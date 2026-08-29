import { HqCard } from "./HqCard.js";
/**
 * Overview 화면 — snapshot.json이 제공하는 HQSnapshot 목록을 HqCard로
 * 나열할 뿐이다. Task/Execution/History 등 Snapshot에 없는 데이터는
 * 표시하지 않는다(존재하지 않는 Backend 데이터를 임의로 만들지 않음).
 */
export function Overview({ snapshots }) {
    return (React.createElement("section", { className: "overview" },
        React.createElement("h2", null, "Overview"),
        React.createElement("div", { className: "hq-cards" }, snapshots.map((s) => (React.createElement("div", { id: `hq-${s.identity}`, key: s.identity },
            React.createElement(HqCard, { snapshot: s })))))));
}
