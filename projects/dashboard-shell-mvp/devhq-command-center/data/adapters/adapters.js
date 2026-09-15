/*
 * Data Adapter — Dev HQ Command Center Prototype
 *
 * UI 컴포넌트는 이 모듈만 호출한다. Mock JSON(`data/mock/*.json`)을 직접
 * 참조하지 않는다. 실제 Execution/Evidence가 연결되는 단계에서는 각 함수의
 * 내부 구현(fetch 대상)만 교체하면 되고, UI/렌더 코드는 변경할 필요가 없다.
 *
 * 모든 반환값은 `source: "mock" | "real"`를 포함한다 — 실제 데이터로
 * 오인시킬 수 있는 표기를 UI가 하지 않도록, 데이터 원천을 항상 함께
 * 전달한다.
 */

var DevHQAdapters = (function () {

  var MOCK_BASE = "data/mock/";
  var cache = {};

  // Chat에서 즉석 생성된 Task(_synthetic)는 정적 tasks.json에 없다 — 세션
  // 메모리에만 보관해 getTask()/getActivity() 등이 계속 같은 값을 반환하게
  // 한다. 페이지를 새로고침하면 사라진다(영속 저장소를 만들지 않는다).
  var syntheticTasks = {};

  function loadMock(name) {
    if (cache[name]) return cache[name];
    var promise = fetch(MOCK_BASE + name + ".json").then(function (res) {
      if (!res.ok) {
        throw new Error("Mock 데이터 로드 실패: " + name + " (HTTP " + res.status + ")");
      }
      return res.json();
    });
    cache[name] = promise;
    return promise;
  }

  function withSource(value) {
    return { source: "mock", data: value };
  }

  // ---- Conversations ----

  function getConversations() {
    return loadMock("conversations").then(function (json) {
      return withSource(json.recent);
    });
  }

  // ---- Tasks ----

  function getTaskList() {
    return loadMock("tasks").then(function (json) {
      return withSource(json.tasks);
    });
  }

  function getTask(taskId) {
    if (syntheticTasks[taskId]) {
      return Promise.resolve(withSource(syntheticTasks[taskId]));
    }
    return loadMock("tasks").then(function (json) {
      var task = json.tasks.filter(function (t) { return t.id === taskId; })[0] || null;
      return withSource(task);
    });
  }

  function getActivity(taskId) {
    return loadMock("activity").then(function (json) {
      return withSource(json.byTask[taskId] || []);
    });
  }

  function getChanges(taskId) {
    return loadMock("changes").then(function (json) {
      return withSource(json.byTask[taskId] || { summary: "0 files changed", files: [] });
    });
  }

  function getTests(taskId) {
    return loadMock("tests").then(function (json) {
      return withSource(json.byTask[taskId] || { pass: 0, skipped: 0, failed: 0, lastRun: null, duration: null });
    });
  }

  function getEvidence(taskId) {
    return loadMock("evidence").then(function (json) {
      return withSource(json.byTask[taskId] || { checklist: [], verification: [], artifacts: [] });
    });
  }

  function getTerminalHistory(taskId) {
    return loadMock("terminal").then(function (json) {
      return withSource(json.byTask[taskId] || []);
    });
  }

  function getFileTree() {
    return loadMock("files").then(function (json) {
      return withSource(json.tree);
    });
  }

  // 파일 내용은 별도 fixture 없이, 변경된 파일이면 changes.json의 after를
  // 합성해 보여준다 — 새로운 Mock 소스를 늘리지 않는다.
  function getFileContent(taskId, path) {
    return loadMock("changes").then(function (json) {
      var change = (json.byTask[taskId] || { files: [] }).files
        .filter(function (f) { return f.path.indexOf(path) !== -1 || path.indexOf(f.path) !== -1; })[0];
      if (change) {
        return withSource({ path: path, content: change.after });
      }
      return withSource({ path: path, content: "# " + path + "\n(Prototype — 이 파일은 Mock Tree 항목이며 내용 fixture가 없다)\n" });
    });
  }

  // ---- Task 생성(Chat -> Task) ----
  //
  // 실제 Task Runtime/Orchestrator는 이번 Prototype 범위 밖이다. 사용자
  // 입력이 기존 Mock Task 제목과 일치하면 그 Task로 전환하고, 아니면
  // 새 Mock Task(진행률 0%, WAITING)를 즉석에서 만들어 UX만 보여준다 —
  // 실제 실행이 시작된 것처럼 보이는 문구를 쓰지 않는다.
  function createOrRouteTaskFromChat(text) {
    return loadMock("tasks").then(function (json) {
      var normalized = text.trim();
      var matched = json.tasks.filter(function (t) {
        return normalized.indexOf(t.title) !== -1 || t.title.indexOf(normalized) !== -1;
      })[0];
      if (matched) {
        return withSource({ routedExisting: true, task: matched });
      }
      var nextId = String(Math.max.apply(null, json.tasks.map(function (t) { return parseInt(t.id, 10); })) + 1).padStart(3, "0");
      var newTask = {
        id: nextId,
        title: normalized,
        status: "WAITING",
        currentStage: "context",
        agent: "Development Agent",
        currentActivity: null,
        progress: { overall: 0, workflow: 0, tasks: 0, verification: 0 },
        stages: [
          { key: "context", label: "Context", status: "pending", startedAt: null, completedAt: null, duration: null },
          { key: "planning", label: "Planning", status: "pending", startedAt: null, completedAt: null, duration: null },
          { key: "architecture", label: "Architecture", status: "pending", startedAt: null, completedAt: null, duration: null },
          { key: "implementation", label: "Implementation", status: "pending", startedAt: null, completedAt: null, duration: null },
          { key: "validation", label: "Validation", status: "pending", startedAt: null, completedAt: null, duration: null }
        ],
        elapsedSeconds: 0,
        createdAt: new Date().toTimeString().slice(0, 5),
        plan: ["(Prototype) 실제 Task Runtime 미연결 — Plan은 아직 생성되지 않음"],
        _synthetic: true
      };
      syntheticTasks[nextId] = newTask;
      return withSource({ routedExisting: false, task: newTask });
    });
  }

  return {
    getConversations: getConversations,
    getTaskList: getTaskList,
    getTask: getTask,
    getActivity: getActivity,
    getChanges: getChanges,
    getTests: getTests,
    getEvidence: getEvidence,
    getTerminalHistory: getTerminalHistory,
    getFileTree: getFileTree,
    getFileContent: getFileContent,
    createOrRouteTaskFromChat: createOrRouteTaskFromChat
  };

})();
