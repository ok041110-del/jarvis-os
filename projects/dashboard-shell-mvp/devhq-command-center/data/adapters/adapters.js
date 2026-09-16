/*
 * Data Adapter — Dev HQ Command Center Prototype
 *
 * UI 컴포넌트는 이 모듈만 호출한다. Mock JSON(`data/mock/*.json`)을 직접
 * 참조하지 않는다. 실제 Execution/Evidence가 연결되는 단계에서는 각 함수의
 * 내부 구현(fetch 대상)만 교체하면 되고, UI/렌더 코드는 변경할 필요가 없다.
 *
 * 모든 반환값은 `source: "mock" | "real" | "unavailable"`를 포함한다 —
 * 실제 데이터로 오인시킬 수 있는 표기를 UI가 하지 않도록, 데이터 원천을
 * 항상 함께 전달한다. Real 데이터 원천: `data/real/export_real_snapshot.py`
 * (수동 실행, 새 서버 API 없음)가 내보낸 정적 JSON — 실행하지 않았거나
 * 특정 경로를 다루지 않으면 `unavailable`이며, 이때 Mock 성공값으로
 * 조용히 대체하지 않는다(getFileTree/getFileContent의 Mock Tree
 * 호환 fallback은 예외 — Real Tree 자체가 없을 때만 동작).
 */

var DevHQAdapters = (function () {

  var MOCK_BASE = "data/mock/";
  var REAL_BASE = "data/real/";
  var cache = {};
  var realCache = {};

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

  // Real 데이터는 `data/real/export_real_snapshot.py`(수동 실행, 새 서버
  // API 없음)가 내보낸 정적 JSON이다 — 아직 실행되지 않았거나 파일이
  // 없으면 null을 반환한다(예외를 던지지 않음, 호출부가 "unavailable"로
  // 처리). 실패를 Mock 성공값으로 조용히 대체하지 않는다 — null이면
  // 호출부가 명시적으로 unavailable을 반환한다.
  function loadReal(name) {
    if (realCache[name]) return realCache[name];
    var promise = fetch(REAL_BASE + name + ".json").then(function (res) {
      if (!res.ok) return null;
      return res.json();
    }).catch(function () { return null; });
    realCache[name] = promise;
    return promise;
  }

  function withSource(value) {
    return { source: "mock", data: value };
  }

  function unavailable(reason) {
    return { source: "unavailable", data: null, reason: reason };
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

  // 실제 저장소 File Tree(`export_real_snapshot.py`가 내보낸 `real/files.json`)가
  // 있으면 그것을 쓰고, 없으면(스크립트 미실행) Mock Tree로 그대로 fallback한다
  // — Real 시도가 실패했다고 Mock을 "real"인 것처럼 위장하지 않는다(source는
  // 항상 실제 사용된 출처를 반영).
  function getFileTree() {
    return loadReal("files").then(function (real) {
      if (real && real.tree) {
        return { source: "real", data: real.tree, generatedAt: real.generated_at };
      }
      return loadMock("files").then(function (json) {
        return withSource(json.tree);
      });
    });
  }

  // 파일 내용 — `path`가 `projects/dashboard-shell-mvp/` 아래면 기존 정적
  // 서버(serve_dashboard.py, 무수정)가 이미 서빙하므로 그 경로를 직접
  // fetch한다. 그 밖의 경로(hqs/, docs/ 등)는 export 스크립트가 미리
  // 내보낸 `real/content/<path>.json`을 쓴다. 둘 다 없으면(export
  // 스크립트를 아직 실행하지 않아 Mock Tree만 있는 경우 등) 기존 Prototype
  // 동작대로 Mock changes.json에서 합성해 보여준다 — 이 fallback은 Real
  // Explorer 항목(경로가 실제 저장소 구조)에는 사실상 매치되지 않고,
  // Mock Tree(파일명만 있는 옛 구조) 클릭 시에만 동작해 회귀를 막는다.
  var DASHBOARD_PREFIX = "projects/dashboard-shell-mvp/";

  function getFileContentFromMockSynthesis(taskId, path) {
    return loadMock("changes").then(function (json) {
      var change = (json.byTask[taskId] || { files: [] }).files
        .filter(function (f) { return f.path.indexOf(path) !== -1 || path.indexOf(f.path) !== -1; })[0];
      if (change) {
        return withSource({ path: path, content: change.after });
      }
      return unavailable("Real/Mock 어느 쪽에도 이 경로의 내용이 없음: " + path);
    });
  }

  function getFileContent(taskId, path) {
    if (path.indexOf(DASHBOARD_PREFIX) === 0) {
      var relPath = path.slice(DASHBOARD_PREFIX.length);
      return fetch("../" + relPath).then(function (res) {
        if (!res.ok) return getFileContentFromMockSynthesis(taskId, path);
        return res.text().then(function (text) {
          return { source: "real", data: { path: path, content: text } };
        });
      }).catch(function () { return getFileContentFromMockSynthesis(taskId, path); });
    }

    var safeName = path.replace(/\//g, "__") + ".json";
    return fetch(REAL_BASE + "content/" + safeName).then(function (res) {
      if (!res.ok) return getFileContentFromMockSynthesis(taskId, path);
      return res.json().then(function (json) {
        return { source: "real", data: { path: json.path, content: json.content } };
      });
    }).catch(function () { return getFileContentFromMockSynthesis(taskId, path); });
  }

  // ---- Repository/Git 상태(Task 무관, 전역) ----
  //
  // `real/git.json`이 있으면 그대로 쓰고, 없으면 unavailable — Mock 대체
  // fixture를 별도로 만들지 않는다(Git 상태는 본래 Mock 개념이 아니다).
  function getRepoStatus() {
    return loadReal("git").then(function (real) {
      if (!real) return unavailable("git.json 없음 — export_real_snapshot.py 미실행");
      return { source: "real", data: real };
    });
  }

  // ---- Dev HQ Workflow 상태(Task 무관, 전역) ----
  //
  // `unified-dashboard/snapshot.py::build_dev_hq_snapshot()`를 재사용해
  // 만든 `real/workflow.json`을 그대로 노출한다(Stage/Agent 코드 재해석
  // 없음).
  function getWorkflowStatus() {
    return loadReal("workflow").then(function (real) {
      if (!real) return unavailable("workflow.json 없음 — export_real_snapshot.py 미실행");
      return { source: "real", data: real };
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
    getRepoStatus: getRepoStatus,
    getWorkflowStatus: getWorkflowStatus,
    createOrRouteTaskFromChat: createOrRouteTaskFromChat
  };

})();
