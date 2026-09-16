/*
 * App Controller — Dev HQ Command Center Prototype
 *
 * 상태를 보관하고, Adapter에서 데이터를 읽어 Render로 그린다. Task
 * 선택에 따라 Chat/Plan/Activity/Code/Terminal/Changes/Tests/Evidence/
 * Report 탭이 모두 같은 Task를 바라본다(원칙: Task First).
 */

(function () {

  var el = {
    sidebar: document.getElementById("cc-sidebar"),
    taskHeader: document.getElementById("cc-task-header"),
    tabbar: document.getElementById("cc-tabbar"),
    tabContent: document.getElementById("cc-tab-content"),
    inspector: document.getElementById("cc-inspector"),
    statusbar: document.getElementById("cc-statusbar")
  };

  var state = {
    activeNav: "development",
    activeTaskId: "042",
    activeTab: "chat",
    conversations: [],
    fileTree: [],
    fileTreeSource: "mock",
    gitStatus: { source: "unavailable", data: null },
    workflowStatus: { source: "unavailable", data: null },
    task: null,
    activity: { data: [], source: "mock" },
    changes: { data: { summary: "", files: [] }, source: "mock" },
    tests: { data: { pass: 0, skipped: 0, failed: 0 }, source: "mock" },
    evidence: { data: { checklist: [], verification: [], artifacts: [] }, source: "mock" },
    terminal: { data: [], source: "mock" },
    editor: { openTabs: [], activePath: null },
    activeChangePath: null,
    chatMessages: [
      { role: "system", text: "Prototype — 실제 Task Runtime/Agent Orchestrator는 연결되어 있지 않다. Chat 입력은 Mock Task 데이터를 라우팅하거나, 알려지지 않은 요청이면 새 Mock Task를 즉석 생성한다." }
    ]
  };

  function pad2(n) { return n < 10 ? "0" + n : String(n); }

  function formatElapsed(totalSeconds) {
    var h = Math.floor(totalSeconds / 3600);
    var m = Math.floor((totalSeconds % 3600) / 60);
    var s = totalSeconds % 60;
    return (h > 0 ? h + "h " : "") + pad2(m) + "m " + pad2(s) + "s";
  }

  // ---- Data loading ----

  function loadTaskBundle(taskId) {
    return Promise.all([
      DevHQAdapters.getTask(taskId),
      DevHQAdapters.getActivity(taskId),
      DevHQAdapters.getChanges(taskId),
      DevHQAdapters.getTests(taskId),
      DevHQAdapters.getEvidence(taskId),
      DevHQAdapters.getTerminalHistory(taskId)
    ]).then(function (results) {
      state.task = results[0].data;
      state.activity = { data: results[1].data, source: results[1].source };
      state.changes = { data: results[2].data, source: results[2].source };
      state.tests = { data: results[3].data, source: results[3].source };
      state.evidence = { data: results[4].data, source: results[4].source };
      state.terminal = { data: results[5].data, source: results[5].source };
      state.editor = { openTabs: [], activePath: null };
      state.activeChangePath = (state.changes.data.files[0] || {}).path || null;
    });
  }

  // ---- Render orchestration ----

  function renderSidebar() {
    el.sidebar.innerHTML = CCRender.sidebar(
      state.activeNav, state.fileTree, state.conversations, state.activeTaskId,
      state.fileTreeSource, state.gitStatus, state.workflowStatus
    );
    bindSidebarEvents();
  }

  function elapsedLabel() {
    if (!state.task) return "—";
    return formatElapsed(state.task.elapsedSeconds || 0);
  }

  function renderHeader() {
    el.taskHeader.innerHTML = CCRender.taskHeader(state.task, elapsedLabel());
  }

  function renderTabbar() {
    el.tabbar.innerHTML = CCRender.tabBar(state.activeTab);
    var buttons = el.tabbar.querySelectorAll(".tab-item");
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        state.activeTab = btn.getAttribute("data-tab");
        renderTabbar();
        renderTabContent();
      });
    });
  }

  function renderTabContent() {
    if (!state.task) {
      el.tabContent.innerHTML = '<div class="tab-empty">Task가 없다. Chat 탭에서 요청을 입력해 Task를 생성하라.</div>';
      return;
    }
    switch (state.activeTab) {
      case "chat":
        el.tabContent.innerHTML = CCRender.chat(state.chatMessages);
        bindChatEvents();
        break;
      case "overview":
        el.tabContent.innerHTML = CCRender.overview(state.task, elapsedLabel());
        break;
      case "plan":
        el.tabContent.innerHTML = CCRender.plan(state.task);
        break;
      case "activity":
        el.tabContent.innerHTML = CCRender.activity(state.activity.data, state.activity.source);
        break;
      case "code":
        el.tabContent.innerHTML = CCRender.codeEditor(
          state.fileTree, state.editor.openTabs, state.editor.activePath,
          state.editor.activeContent || "", state.editor.activeContentSource || state.fileTreeSource
        );
        bindEditorEvents();
        break;
      case "terminal":
        el.tabContent.innerHTML = CCRender.terminal(state.terminal.data, state.terminal.source);
        bindTerminalEvents();
        break;
      case "changes":
        el.tabContent.innerHTML = CCRender.changes(state.changes.data, state.activeChangePath, state.changes.source);
        bindChangesEvents();
        break;
      case "tests":
        el.tabContent.innerHTML = CCRender.tests(state.tests.data, state.tests.source);
        break;
      case "evidence":
        el.tabContent.innerHTML = CCRender.evidence(state.evidence.data, state.evidence.source);
        break;
      case "report":
        el.tabContent.innerHTML = CCRender.report(state.task, state.changes.data, state.tests.data, state.evidence.data, "mock");
        bindReportEvents();
        break;
      default:
        el.tabContent.innerHTML = "";
    }
  }

  function renderInspector() {
    el.inspector.innerHTML = CCRender.inspector(state.task, state.changes.data, state.tests.data, state.evidence.data, elapsedLabel());
  }

  function renderStatusbar() {
    el.statusbar.innerHTML = CCRender.statusBar(state.task, state.tests.data, state.changes.data, state.evidence.data, elapsedLabel());
  }

  function renderAll() {
    renderSidebar();
    renderHeader();
    renderTabbar();
    renderTabContent();
    renderInspector();
    renderStatusbar();
  }

  function renderLiveStrips() {
    // 1초마다 갱신되는 값(Elapsed 등)만 가볍게 다시 그린다 — 전체 재렌더 방지.
    renderHeader();
    renderInspector();
    renderStatusbar();
  }

  // ---- Event bindings ----

  function bindSidebarEvents() {
    el.sidebar.querySelectorAll(".conv-item").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var taskId = btn.getAttribute("data-task-id");
        if (taskId === state.activeTaskId) return;
        state.activeTaskId = taskId;
        state.activeTab = "overview";
        loadTaskBundle(taskId).then(renderAll);
      });
    });
  }

  function bindEditorEvents() {
    el.tabContent.querySelectorAll(".tree-file").forEach(function (row) {
      row.addEventListener("click", function () {
        var path = row.getAttribute("data-path");
        if (state.editor.openTabs.indexOf(path) === -1) state.editor.openTabs.push(path);
        state.editor.activePath = path;
        DevHQAdapters.getFileContent(state.activeTaskId, path).then(function (res) {
          state.editor.activeContent = res.data ? res.data.content : "(" + (res.reason || "unavailable") + ")";
          state.editor.activeContentSource = res.source;
          renderTabContent();
        });
      });
    });
    el.tabContent.querySelectorAll("[data-editor-tab]").forEach(function (tab) {
      tab.addEventListener("click", function (evt) {
        if (evt.target.hasAttribute("data-editor-close")) return;
        var path = tab.getAttribute("data-editor-tab");
        state.editor.activePath = path;
        DevHQAdapters.getFileContent(state.activeTaskId, path).then(function (res) {
          state.editor.activeContent = res.data ? res.data.content : "(" + (res.reason || "unavailable") + ")";
          state.editor.activeContentSource = res.source;
          renderTabContent();
        });
      });
    });
    el.tabContent.querySelectorAll("[data-editor-close]").forEach(function (btn) {
      btn.addEventListener("click", function (evt) {
        evt.stopPropagation();
        var path = btn.getAttribute("data-editor-close");
        state.editor.openTabs = state.editor.openTabs.filter(function (p) { return p !== path; });
        if (state.editor.activePath === path) {
          state.editor.activePath = state.editor.openTabs[0] || null;
        }
        renderTabContent();
      });
    });
  }

  function bindChangesEvents() {
    el.tabContent.querySelectorAll("[data-change-path]").forEach(function (row) {
      row.addEventListener("click", function () {
        state.activeChangePath = row.getAttribute("data-change-path");
        renderTabContent();
      });
    });
  }

  // CommandResult.detail(list[str])을 Terminal stdout으로 펼친다. 단일
  // 원소가 JSON이면(run_workflow() 결과를 그대로 담은 경우) 읽기 좋게
  // pretty-print하고, 아니면 줄 단위로 그대로 이어붙인다(재해석 없음).
  function formatCommandDetail(detail) {
    var lines = detail || [];
    if (lines.length === 1) {
      try {
        return JSON.stringify(JSON.parse(lines[0]), null, 2);
      } catch (e) { /* JSON이 아니면 그대로 아래로 */ }
    }
    return lines.join("\n");
  }

  function bindTerminalEvents() {
    var form = document.getElementById("cc-terminal-form");
    var scroller = document.getElementById("cc-terminal-scroll");
    if (scroller) scroller.scrollTop = scroller.scrollHeight;
    if (!form) return;
    form.addEventListener("submit", function (evt) {
      evt.preventDefault();
      var input = document.getElementById("cc-terminal-input");
      var command = input.value.trim();
      if (!command) return;
      input.value = "";
      var startedAt = Date.now();
      // 실제 Command Contract/Resolver(`/api/command`)를 호출한다 — 이
      // 화면은 더 이상 입력을 echo만 하지 않는다(Terminal은 shell이
      // 아니라 Command Center Command 입력창).
      DevHQAdapters.executeCommand(command).then(function (res) {
        var durationLabel = ((Date.now() - startedAt) / 1000).toFixed(1) + "s";
        var ok = res.source === "real" && res.data && res.data.status === "ok";
        state.terminal.source = "real";
        state.terminal.data = state.terminal.data.concat([{
          command: command,
          stdout: ok ? formatCommandDetail(res.data.detail) : "",
          stderr: ok ? "" : "(" + (res.data ? (res.data.reason || "invalid") : res.reason) + ")",
          exitCode: ok ? 0 : 1,
          duration: durationLabel,
          timestamp: new Date().toTimeString().slice(0, 8)
        }]);
        renderTabContent();
      });
    });
  }

  function formatCommandResult(res) {
    if (res.routedExisting) {
      return "기존 Task #" + res.task.id + "(" + res.task.title + ")로 이동한다.";
    }
    return "새 Mock Task #" + res.task.id + " 생성됨 (실제 Task Runtime 미연결 — 진행률/Evidence는 아직 없음).";
  }

  function bindChatEvents() {
    var form = document.getElementById("cc-chat-form");
    var scroller = document.getElementById("cc-chat-messages");
    if (scroller) scroller.scrollTop = scroller.scrollHeight;
    if (!form) return;
    form.addEventListener("submit", function (evt) {
      evt.preventDefault();
      var input = document.getElementById("cc-chat-input");
      var text = input.value.trim();
      if (!text) return;
      input.value = "";
      state.chatMessages.push({ role: "user", text: text });
      renderTabContent();

      DevHQAdapters.createOrRouteTaskFromChat(text).then(function (res) {
        state.chatMessages.push({ role: "agent", text: formatCommandResult(res.data) });
        var task = res.data.task;
        if (!res.data.routedExisting) {
          state.conversations = state.conversations.concat([{ taskId: task.id, title: "#" + task.id + " " + task.title }]);
        }
        state.activeTaskId = task.id;
        return loadTaskBundle(task.id).then(function () {
          state.activeTab = "chat";
          renderAll();
        });
      });
    });
  }

  function bindReportEvents() {
    var copyBtn = document.getElementById("cc-report-copy");
    var exportBtn = document.getElementById("cc-report-export");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        var text = CCRender.reportText(state.task, state.changes.data, state.tests.data, state.evidence.data);
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            copyBtn.textContent = "Copied";
            setTimeout(function () { copyBtn.textContent = "Copy All"; }, 1500);
          });
        }
      });
    }
    if (exportBtn) {
      exportBtn.addEventListener("click", function () {
        var text = "# " + CCRender.reportText(state.task, state.changes.data, state.tests.data, state.evidence.data).replace(/\n/g, "\n\n");
        var blob = new Blob([text], { type: "text/markdown" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = "task-" + state.task.id + "-report.md";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      });
    }
  }

  // ---- Init ----

  function init() {
    Promise.all([
      DevHQAdapters.getConversations(),
      DevHQAdapters.getFileTree(),
      DevHQAdapters.getRepoStatus(),
      DevHQAdapters.getWorkflowStatus()
    ]).then(function (results) {
      state.conversations = results[0].data;
      state.fileTree = results[1].data;
      state.fileTreeSource = results[1].source;
      state.gitStatus = { source: results[2].source, data: results[2].data };
      state.workflowStatus = { source: results[3].source, data: results[3].data };
      return loadTaskBundle(state.activeTaskId);
    }).then(function () {
      renderAll();
      setInterval(function () {
        if (state.task && state.task.status === "RUNNING") {
          state.task.elapsedSeconds = (state.task.elapsedSeconds || 0) + 1;
          renderLiveStrips();
        }
      }, 1000);
    });
  }

  document.addEventListener("DOMContentLoaded", init);

})();
