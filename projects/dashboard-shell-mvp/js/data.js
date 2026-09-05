/*
 * Mock Data Layer — Experimental Prototype
 *
 * Trading/Header/Chat/Mock Refresh는 여전히 실제 Backend/Core/HQ에
 * 연결되어 있지 않다 — 아래 JavaScript 객체 안 Mock Data가 유일한
 * 소스다.
 *
 * `getHQSnapshot('development'|'investment')`만 예외다 —
 * `generate_development_snapshot.py`/`generate_investment_snapshot.py`
 * (둘 다 projects/unified-dashboard/snapshot.py의 Evidence 수집을
 * 재사용)가 생성한 JSON을 fetch()로 읽는다(`EVIDENCE_SNAPSHOT_FILES`
 * 참조). 이 함수는 그래서 두 HQ일 때만 Promise를 반환하고, Trading은
 * 기존과 동일하게 동기 객체를 반환한다 — app.js가 `Promise.resolve()`로
 * 두 경우를 모두 감싸 처리한다.
 *
 * Evidence fetch가 실패하면(파일 없음/서버 미기동/JSON 손상) Mock으로
 * 조용히 대체하지 않는다 — Promise를 reject해 app.js가 실패 사실을
 * 그대로 화면에 드러내게 한다.
 */

var MockData = (function () {

  // 내부 State — 이 저장소의 상태는 시연을 위해 mutate 가능하게 둔다.
  var state = {
    aiBudgetUsedPercent: 42,
    tick: 0,
    development: {
      connection: "MOCK",
      status: "ACTIVE",
      stage: "Stage 3 / 5",
      progressPercent: 58,
      currentTask: "MVP Dogfooding 결함 재현 검증",
      agents: ["Planner", "Implementer", "Reviewer", "Validator"],
      recentEvents: [
        "MVP-0048 결함 수정 완료",
        "Kernel Boundary Validation 재확인",
        "회귀 테스트 36 passed"
      ]
    },
    trading: {
      connection: "NOT_IMPLEMENTED",
      status: "PLANNED",
      note: "Trading HQ는 아직 구현되지 않았다 — Architecture Boundary만 예약된 상태."
    }
  };

  function nowLabel() {
    var d = new Date();
    return d.toTimeString().slice(0, 8);
  }

  // ---- 조회 함수 (실제 연결 시 이 함수들의 내부만 교체) ----

  function getSystemStatus() {
    return {
      kernel: "NORMAL",
      boundary: "NORMAL",
      updatedAt: nowLabel()
    };
  }

  function getAIBudget() {
    return {
      usedPercent: state.aiBudgetUsedPercent,
      label: "Session Token Budget"
    };
  }

  function getHQList() {
    return [
      { id: "development", label: "Development" },
      { id: "investment", label: "Investment" },
      { id: "trading", label: "Trading" }
    ];
  }

  var EVIDENCE_SNAPSHOT_FILES = {
    development: "data/development-snapshot.json",
    investment: "data/investment-snapshot.json"
  };

  function getHQSnapshot(hqId) {
    var snapshotFile = EVIDENCE_SNAPSHOT_FILES[hqId];
    if (snapshotFile) {
      return fetch(snapshotFile).then(function (res) {
        if (!res.ok) {
          throw new Error(snapshotFile + " 응답 실패: HTTP " + res.status);
        }
        return res.json();
      });
    }
    return state[hqId] || null;
  }

  // ---- Mock 갱신 시뮬레이션 (Mock Data 변경 → UI 재렌더링 검증용) ----

  function simulateUpdate() {
    state.tick += 1;
    state.aiBudgetUsedPercent = Math.min(99, (state.aiBudgetUsedPercent + 7) % 100 || 5);
    state.development.progressPercent = Math.min(100, state.development.progressPercent + 5);
    state.development.recentEvents.unshift("Mock Refresh #" + state.tick + " (" + nowLabel() + ")");
    state.development.recentEvents = state.development.recentEvents.slice(0, 5);
  }

  return {
    getSystemStatus: getSystemStatus,
    getAIBudget: getAIBudget,
    getHQList: getHQList,
    getHQSnapshot: getHQSnapshot,
    simulateUpdate: simulateUpdate
  };

})();
