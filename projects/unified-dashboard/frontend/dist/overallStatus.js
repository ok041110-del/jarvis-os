/**
 * 전체 System Status 집계 — 각 HQSnapshot이 이미 갖고 있는
 * PresentationState 값만 사용해 우선순위 기반으로 하나를 고른다.
 * HQ별 detail/deferred의 의미를 새로 해석하지 않는다(Global Shell은
 * HQ 내부 값을 조합만 한다).
 */
const PRIORITY = ["BLOCKED", "WORKING", "DEFERRED", "UNKNOWN", "NORMAL"];
export function overallStatus(snapshots) {
    if (snapshots.length === 0)
        return "UNKNOWN";
    for (const state of PRIORITY) {
        if (snapshots.some((s) => s.status === state))
            return state;
    }
    return "UNKNOWN";
}
