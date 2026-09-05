/*
 * Mock Data Layer — Experimental Prototype
 *
 * 이 파일은 실제 Backend/Core/HQ에 연결되어 있지 않다. 모든 값은
 * JavaScript 객체 안에 보관된 Mock Data이며, 아래 get* 함수들이
 * 유일한 조회 지점(single source)이다.
 *
 * 향후 실제 데이터로 교체할 때는 이 파일의 get* 함수 "내부 구현"만
 * fetch(API)/이벤트 구독 등으로 바꾸면 된다 — render.js와 app.js는
 * 이 함수들의 반환 형태(shape)만 알면 되고, Mock인지 실제인지는
 * 몰라도 되도록 분리했다.
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
    investment: {
      connection: "MOCK",
      status: "ACTIVE",
      teams: [
        { name: "Stock Team", status: "Promoted", lastDecision: "HOLD" },
        { name: "ETF Team", status: "Promoted", lastDecision: "HOLD" },
        { name: "Dividend Stock Team", status: "Promoted", lastDecision: "HOLD" }
      ],
      deferred: ["Portfolio", "Risk", "Execution"]
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

  function getHQSnapshot(hqId) {
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
