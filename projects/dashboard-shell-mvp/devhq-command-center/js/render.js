/*
 * Render — Dev HQ Command Center Prototype
 *
 * 데이터를 입력받아 DOM 문자열을 만드는 순수 함수 모음. Mock/Real
 * 여부를 모른다 — Adapter가 넘긴 값을 그대로 그릴 뿐이다. Mock Data를
 * 표시할 때는 `MOCK` 배지를 붙여 실제 데이터로 오인되지 않게 한다.
 */

var CCRender = (function () {

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function mockBadge(source) {
    if (source === "mock") return '<span class="badge badge-mock" title="Prototype Mock Data — 실제 Evidence 아님">MOCK</span>';
    if (source === "real") return '<span class="badge badge-real" title="실제 저장소 데이터(export_real_snapshot.py 스냅샷)">REAL</span>';
    if (source === "unavailable") return '<span class="badge badge-unavailable" title="실제 데이터 소스 없음 — Mock으로 대체하지 않음">UNAVAILABLE</span>';
    return "";
  }

  var STATUS_CLASS = {
    RUNNING: "status-running", WAITING: "status-waiting", IDLE: "status-idle",
    APPROVAL_REQUIRED: "status-waiting", SUCCESS: "status-success", COMPLETED: "status-success",
    FAILED: "status-failed", CANCELLED: "status-failed", BLOCKED: "status-failed"
  };

  function statusChip(status) {
    var cls = STATUS_CLASS[status] || "status-idle";
    return '<span class="status-chip ' + cls + '">' + esc(status) + "</span>";
  }

  var VERDICT_CLASS = { PASS: "verdict-pass", FAIL: "verdict-fail", INCONCLUSIVE: "verdict-inconclusive", SKIPPED: "verdict-skipped" };

  function verdictChip(status) {
    var cls = VERDICT_CLASS[status] || "verdict-skipped";
    return '<span class="verdict-chip ' + cls + '">' + esc(status) + "</span>";
  }

  // ---- Sidebar ----

  var HQ_NAV = [
    { id: "development", label: "Development HQ", enabled: true },
    { id: "investment", label: "Investment HQ", enabled: false },
    { id: "trading", label: "Trading HQ", enabled: false },
    { id: "evidence", label: "Evidence", enabled: false }
  ];

  function nav(activeNav) {
    return HQ_NAV.map(function (item) {
      var cls = "nav-item" + (item.id === activeNav ? " nav-item-active" : "") + (!item.enabled ? " nav-item-disabled" : "");
      var suffix = item.enabled ? "" : '<span class="nav-placeholder">Placeholder</span>';
      return '<button class="' + cls + '" data-nav="' + item.id + '"' + (item.enabled ? "" : " disabled") + ">" + esc(item.label) + suffix + "</button>";
    }).join("");
  }

  function fileTreeNode(node, depth) {
    depth = depth || 0;
    var indent = 'style="padding-left:' + (10 + depth * 14) + 'px"';
    if (node.type === "dir") {
      var children = (node.children || []).map(function (c) { return fileTreeNode(c, depth + 1); }).join("");
      return '<div class="tree-dir" ' + indent + '>' + icon("folder") + esc(node.name) + "</div>" + children;
    }
    var dot = node.changed ? '<span class="changed-dot" title="변경됨"></span>' : "";
    var dataPath = node.path || node.name;
    return '<div class="tree-file" data-path="' + esc(dataPath) + '" ' + indent + '>' + icon("file") + esc(node.name) + dot + "</div>";
  }

  function icon(kind) {
    var glyphs = { folder: "▸ ", file: "• " };
    return '<span class="tree-icon">' + (glyphs[kind] || "") + "</span>";
  }

  function explorer(tree) {
    return '<div class="explorer-tree">' + tree.map(function (n) { return fileTreeNode(n, 0); }).join("") + "</div>";
  }

  function conversationList(conversations, activeTaskId) {
    return conversations.map(function (c) {
      var cls = "conv-item" + (c.taskId === activeTaskId ? " conv-item-active" : "");
      return '<button class="' + cls + '" data-task-id="' + esc(c.taskId) + '">' + esc(c.title) + "</button>";
    }).join("");
  }

  // Task와 무관한 저장소 전역 상태(Git branch/변경 파일 수, Dev HQ Workflow
  // Phase) — `real/git.json`/`real/workflow.json`이 있을 때만 채워진다.
  // 없으면(export_real_snapshot.py 미실행) UNAVAILABLE 배지만 붙이고 값은
  // 비워둔다(Mock으로 대체하지 않음).
  function repoStatusBlock(gitStatus, workflowStatus) {
    var gitLine = gitStatus && gitStatus.source === "real"
      ? "Branch " + esc(gitStatus.data.branch || "—") + " · " + esc(gitStatus.data.summary)
      : "—";
    var workflowLine = workflowStatus && workflowStatus.source === "real"
      ? esc((workflowStatus.data.detail || [])[0] || "—")
      : "—";
    var badgeSource = gitStatus ? gitStatus.source : "unavailable";
    return (
      '<div class="sidebar-section"><div class="sidebar-title">Repository ' + mockBadge(badgeSource) + '</div>' +
      '<div class="repo-status-line">' + gitLine + "</div>" +
      '<div class="repo-status-line">' + workflowLine + "</div></div>"
    );
  }

  function sidebar(activeNav, tree, conversations, activeTaskId, treeSource, gitStatus, workflowStatus) {
    return (
      '<div class="sidebar-section"><div class="sidebar-title">Navigation</div>' + nav(activeNav) + "</div>" +
      repoStatusBlock(gitStatus, workflowStatus) +
      '<div class="sidebar-section"><div class="sidebar-title">Explorer ' + mockBadge(treeSource) + '</div>' + explorer(tree) + "</div>" +
      '<div class="sidebar-section sidebar-section-grow"><div class="sidebar-title">Recent Conversations</div>' +
      '<div class="conv-list">' + conversationList(conversations, activeTaskId) + "</div></div>"
    );
  }

  // ---- Task Header ----

  function progressBar(percent, cls) {
    var pct = Math.max(0, Math.min(100, percent || 0));
    return (
      '<div class="progress-row"><div class="progress-track ' + (cls || "") + '"><div class="progress-fill" style="width:' + pct + '%"></div></div>' +
      '<span class="progress-pct">' + pct + "%</span></div>"
    );
  }

  function taskHeader(task, elapsedLabel) {
    if (!task) {
      return '<div class="task-header-empty">Task가 선택되지 않았다. Chat에서 요청을 입력하면 Task가 생성된다.</div>';
    }
    return (
      '<div class="task-header">' +
      '<div class="task-header-top">' +
      '<span class="task-id">TASK #' + esc(task.id) + "</span>" +
      "<h2>" + esc(task.title) + "</h2>" +
      statusChip(task.status) +
      "</div>" +
      '<div class="task-header-meta">' +
      '<div class="meta-item"><span>Current Stage</span><strong>' + esc(task.currentStage) + "</strong></div>" +
      '<div class="meta-item"><span>Elapsed</span><strong>' + esc(elapsedLabel) + "</strong></div>" +
      '<div class="meta-item"><span>Agent</span><strong>' + esc(task.agent) + "</strong></div>" +
      "</div>" +
      '<div class="task-header-progress">' +
      '<div class="progress-line"><span>Overall Progress</span>' + progressBar(task.progress.overall) + "</div>" +
      '<div class="progress-line progress-line-sub"><span>Workflow</span>' + progressBar(task.progress.workflow, "progress-sub") + "</div>" +
      '<div class="progress-line progress-line-sub"><span>Tasks</span>' + progressBar(task.progress.tasks, "progress-sub") + "</div>" +
      '<div class="progress-line progress-line-sub"><span>Verification</span>' + progressBar(task.progress.verification, "progress-sub") + "</div>" +
      "</div>" +
      stageTimeline(task.stages) +
      "</div>"
    );
  }

  var STAGE_GLYPH = { done: "✓", running: "●", pending: "○", blocked: "✕" };

  function stageTimeline(stages) {
    return '<div class="stage-timeline">' + stages.map(function (s) {
      return '<div class="stage-step stage-' + s.status + '"><span class="stage-glyph">' + (STAGE_GLYPH[s.status] || "○") + "</span>" + esc(s.label) + "</div>";
    }).join('<div class="stage-sep"></div>') + "</div>";
  }

  // ---- Tabs ----

  var TABS = [
    { key: "chat", label: "Chat" },
    { key: "overview", label: "Overview" },
    { key: "plan", label: "Plan" },
    { key: "activity", label: "Activity" },
    { key: "code", label: "Code" },
    { key: "terminal", label: "Terminal" },
    { key: "changes", label: "Changes" },
    { key: "tests", label: "Tests" },
    { key: "evidence", label: "Evidence" },
    { key: "report", label: "Report" }
  ];

  function tabBar(activeTab) {
    return TABS.map(function (t) {
      var cls = "tab-item" + (t.key === activeTab ? " tab-item-active" : "");
      return '<button class="' + cls + '" data-tab="' + t.key + '">' + t.label + "</button>";
    }).join("");
  }

  // ---- Chat ----

  function chat(messages) {
    var msgs = messages.map(function (m) {
      return '<div class="chat-message chat-' + m.role + '"><span class="chat-role">' + m.role + '</span><span class="chat-text">' + esc(m.text) + "</span></div>";
    }).join("");
    return (
      '<div class="chat-panel">' +
      '<div class="chat-messages" id="cc-chat-messages">' + msgs + "</div>" +
      '<form class="chat-input-row" id="cc-chat-form">' +
      '<input id="cc-chat-input" type="text" placeholder="Task를 생성하거나 진행 상태를 물어보세요 (예: Engine refactor 작업 상태 분석해줘)" autocomplete="off">' +
      '<button type="submit">Send</button>' +
      "</form></div>"
    );
  }

  // ---- Overview / Time UI ----

  function overview(task, elapsedLabel) {
    var rows = task.stages.map(function (s) {
      return '<tr><td>' + esc(s.label) + "</td><td>" + (s.duration || "—") + "</td></tr>";
    }).join("");
    return (
      '<div class="panel-block"><h3>Time</h3>' +
      '<div class="kv-row"><span>Elapsed</span><strong>' + esc(elapsedLabel) + "</strong></div>" +
      '<div class="kv-row"><span>Current Stage</span><strong>' + esc(task.currentStage) + "</strong></div>" +
      '<table class="table"><thead><tr><th>Stage</th><th>Duration</th></tr></thead><tbody>' + rows + "</tbody></table>" +
      "</div>" +
      '<div class="panel-block"><h3>State</h3>' +
      '<div class="kv-row"><span>Progress</span><strong>' + task.progress.overall + '%</strong></div>' +
      '<div class="kv-row"><span>Status</span><strong>' + statusChip(task.status) + "</strong></div>" +
      '<p class="hint-text">Progress와 Status는 독립적이다 — Progress 100%가 자동으로 성공(Status=SUCCESS/COMPLETED)을 의미하지 않는다.</p>' +
      "</div>"
    );
  }

  function plan(task) {
    return '<div class="panel-block"><h3>Plan</h3><ol class="plan-list">' +
      task.plan.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") +
      "</ol></div>";
  }

  function activity(list, source) {
    if (!list.length) return '<div class="panel-block"><h3>Activity ' + mockBadge(source) + '</h3><p class="hint-text">기록된 Activity가 없다.</p></div>';
    return '<div class="panel-block"><h3>Activity ' + mockBadge(source) + '</h3><div class="activity-list">' +
      list.map(function (a) { return '<div class="activity-row"><span class="activity-time">' + esc(a.time) + '</span><span>' + esc(a.text) + "</span></div>"; }).join("") +
      "</div></div>";
  }

  // ---- Code Editor ----

  function codeEditor(tree, openTabs, activePath, content, source) {
    var tabsHtml = openTabs.map(function (p) {
      var cls = "editor-tab" + (p === activePath ? " editor-tab-active" : "");
      var short = p.split("/").pop();
      return '<div class="' + cls + '" data-editor-tab="' + esc(p) + '">' + esc(short) + '<span class="editor-tab-close" data-editor-close="' + esc(p) + '">×</span></div>';
    }).join("");
    var body = activePath
      ? '<pre class="code-view">' + esc(content) + "</pre>"
      : '<div class="code-empty">Explorer에서 파일을 선택하면 여기 표시된다.</div>';
    return (
      '<div class="editor-layout">' +
      '<div class="editor-search"><input type="text" placeholder="파일 검색 (Prototype — 비활성)" disabled></div>' +
      '<div class="editor-tree">' + explorer(tree) + "</div>" +
      '<div class="editor-main">' +
      '<div class="editor-tabbar">' + tabsHtml + "</div>" +
      '<div class="editor-body">' + mockBadge(source) + body + "</div>" +
      "</div></div>"
    );
  }

  // ---- Terminal ----

  function terminal(history, source) {
    var rows = history.map(function (h) {
      var statusCls = h.exitCode === 0 ? "term-ok" : "term-fail";
      return (
        '<div class="term-entry">' +
        '<div class="term-cmd">$ ' + esc(h.command) + '<span class="term-time">' + esc(h.timestamp) + "</span></div>" +
        (h.stdout ? '<pre class="term-out">' + esc(h.stdout) + "</pre>" : "") +
        (h.stderr ? '<pre class="term-err">' + esc(h.stderr) + "</pre>" : "") +
        '<div class="term-meta ' + statusCls + '">Process exited with code ' + h.exitCode + " &middot; Duration: " + esc(h.duration) + "</div>" +
        "</div>"
      );
    }).join("");
    return (
      '<div class="terminal-panel">' +
      '<div class="terminal-header">TERMINAL ' + mockBadge(source) + '</div>' +
      '<div class="terminal-scroll" id="cc-terminal-scroll">' + (rows || '<div class="hint-text">실행 이력이 없다.</div>') + "</div>" +
      '<form class="terminal-input-row" id="cc-terminal-form">' +
      '<span>$</span><input id="cc-terminal-input" type="text" placeholder="pytest projects/dashboard-shell-mvp/tests -q" autocomplete="off">' +
      "</form></div>"
    );
  }

  // ---- Changes / Diff ----

  function changes(changesData, activePath, source) {
    var files = changesData.files || [];
    var list = files.map(function (f) {
      var cls = "change-row" + (f.path === activePath ? " change-row-active" : "");
      return '<div class="' + cls + '" data-change-path="' + esc(f.path) + '"><span class="change-status change-' + f.status + '">' + f.status + "</span>" + esc(f.path) + "</div>";
    }).join("");
    var active = files.filter(function (f) { return f.path === activePath; })[0];
    var diffHtml = active ? diffView(active) : '<div class="code-empty">변경 파일을 선택하면 Diff가 표시된다.</div>';
    return (
      '<div class="changes-layout">' +
      '<div class="changes-list-col"><div class="changes-summary">' + esc(changesData.summary) + " " + mockBadge(source) + "</div>" + (list || '<div class="hint-text">변경된 파일이 없다.</div>') + "</div>" +
      '<div class="changes-diff-col">' + diffHtml + "</div>" +
      "</div>"
    );
  }

  function diffLines(before, after) {
    var b = (before || "").split("\n");
    var a = (after || "").split("\n");
    var max = Math.max(b.length, a.length);
    var out = "";
    for (var i = 0; i < max; i++) {
      if (b[i] !== undefined && b[i] !== a[i]) out += '<div class="diff-line diff-del">- ' + esc(b[i]) + "</div>";
      if (a[i] !== undefined && a[i] !== b[i]) out += '<div class="diff-line diff-add">+ ' + esc(a[i]) + "</div>";
      if (a[i] !== undefined && a[i] === b[i]) out += '<div class="diff-line diff-ctx">&nbsp;&nbsp;' + esc(a[i]) + "</div>";
    }
    return out;
  }

  function diffView(file) {
    return '<div class="diff-view"><div class="diff-path">' + esc(file.path) + "</div>" + diffLines(file.before, file.after) + "</div>";
  }

  // ---- Tests ----

  function tests(t, source) {
    return (
      '<div class="panel-block"><h3>Tests ' + mockBadge(source) + '</h3>' +
      '<div class="tests-grid">' +
      '<div class="tests-stat tests-pass"><span>' + t.pass + '</span><label>PASS</label></div>' +
      '<div class="tests-stat tests-skip"><span>' + t.skipped + '</span><label>SKIPPED</label></div>' +
      '<div class="tests-stat tests-fail"><span>' + t.failed + '</span><label>FAILED</label></div>' +
      "</div>" +
      '<div class="kv-row"><span>Last Run</span><strong>' + (t.lastRun || "—") + "</strong></div>" +
      '<div class="kv-row"><span>Duration</span><strong>' + (t.duration || "—") + "</strong></div>" +
      "</div>"
    );
  }

  // ---- Evidence ----

  function evidence(ev, source) {
    var checklist = (ev.checklist || []).map(function (c) {
      return '<div class="evidence-row" data-evidence-key="' + esc(c.key) + '"><span>' + esc(c.label) + "</span>" + verdictChip(c.status) + "</div>";
    }).join("");
    var verification = (ev.verification || []).map(function (v) {
      return '<div class="evidence-row"><span>' + esc(v.label) + "</span>" + verdictChip(v.status) + (v.detail ? '<div class="evidence-detail">' + esc(v.detail) + "</div>" : "") + "</div>";
    }).join("");
    var artifacts = (ev.artifacts || []).map(function (a) {
      return '<div class="artifact-row">' + esc(a.name) + '<span class="artifact-type">' + esc(a.type) + "</span></div>";
    }).join("") || '<div class="hint-text">등록된 Artifact가 없다.</div>';
    return (
      '<div class="panel-block"><h3>Evidence ' + mockBadge(source) + '</h3>' + checklist + "</div>" +
      '<div class="panel-block"><h3>Verification (Stage 05)</h3>' + verification + "</div>" +
      '<div class="panel-block"><h3>Artifacts</h3>' + artifacts + "</div>"
    );
  }

  // ---- Report ----

  function reportText(task, changesData, testsData, evidenceData) {
    var lines = [
      "FINAL REPORT",
      "Task #" + task.id + " " + task.title,
      "Status: " + task.status,
      "Progress: " + task.progress.overall + "%",
      "Changes: " + (changesData.files || []).length + " files",
      "Tests: " + testsData.pass + " passed, " + testsData.skipped + " skipped, " + testsData.failed + " failed",
      "Evidence: " + (evidenceData.artifacts || []).length + " artifacts"
    ];
    return lines.join("\n");
  }

  function report(task, changesData, testsData, evidenceData, source) {
    return (
      '<div class="panel-block report-block">' +
      '<h3>Final Report ' + mockBadge(source) + '</h3>' +
      '<div class="kv-row"><span>Task</span><strong>#' + esc(task.id) + " " + esc(task.title) + "</strong></div>" +
      '<div class="kv-row"><span>Status</span><strong>' + statusChip(task.status) + "</strong></div>" +
      '<div class="kv-row"><span>Progress</span><strong>' + task.progress.overall + '%</strong></div>' +
      '<div class="kv-row"><span>Changes</span><strong>' + (changesData.files || []).length + " files</strong></div>" +
      '<div class="kv-row"><span>Tests</span><strong>' + testsData.pass + " passed / " + testsData.skipped + " skipped / " + testsData.failed + " failed</strong></div>" +
      '<div class="kv-row"><span>Evidence</span><strong>' + (evidenceData.artifacts || []).length + " artifacts</strong></div>" +
      '<div class="report-actions">' +
      '<button id="cc-report-copy">Copy All</button>' +
      '<button id="cc-report-export">Export Markdown</button>' +
      "</div></div>"
    );
  }

  // ---- Inspector ----

  function inspector(task, changesData, testsData, evidenceData, elapsedLabel) {
    if (!task) return '<div class="inspector-empty">Task 없음</div>';
    return (
      '<div class="inspector-block"><div class="inspector-title">TASK #' + esc(task.id) + "</div>" +
      '<div class="kv-row"><span>Status</span><strong>' + statusChip(task.status) + "</strong></div>" +
      '<div class="kv-row"><span>Progress</span><strong>' + task.progress.overall + '%</strong></div>' +
      '<div class="kv-row"><span>Current Stage</span><strong>' + esc(task.currentStage) + "</strong></div>" +
      '<div class="kv-row"><span>Agent</span><strong>' + esc(task.agent) + "</strong></div>" +
      '<div class="kv-row"><span>Current Activity</span><strong>' + esc(task.currentActivity || "—") + "</strong></div>" +
      '<div class="kv-row"><span>Files Changed</span><strong>' + (changesData.files || []).length + "</strong></div>" +
      '<div class="kv-row"><span>Tests</span><strong>' + (testsData.lastRun ? (testsData.pass + " passed") : "Not run") + "</strong></div>" +
      '<div class="kv-row"><span>Evidence</span><strong>' + (evidenceData.artifacts || []).length + " artifacts</strong></div>" +
      '<div class="kv-row"><span>Elapsed</span><strong>' + esc(elapsedLabel) + "</strong></div>" +
      "</div>"
    );
  }

  // ---- Status Bar ----

  function statusBar(task, testsData, changesData, evidenceData, elapsedLabel) {
    if (!task) return '<span class="statusbar-item">No Task Selected</span>';
    var evPass = (evidenceData.checklist || []).filter(function (c) { return c.status === "PASS"; }).length;
    var evTotal = (evidenceData.checklist || []).length;
    return (
      '<span class="statusbar-item">Task ' + statusChip(task.status) + "</span>" +
      '<span class="statusbar-item">Progress ' + task.progress.overall + "%</span>" +
      '<span class="statusbar-item">Time ' + esc(elapsedLabel) + "</span>" +
      '<span class="statusbar-item">Tests ' + testsData.pass + "P/" + testsData.failed + "F</span>" +
      '<span class="statusbar-item">Changes ' + (changesData.files || []).length + "</span>" +
      '<span class="statusbar-item">Evidence ' + evPass + "/" + evTotal + "</span>" +
      '<span class="statusbar-item">Agent ' + esc(task.agent) + "</span>"
    );
  }

  return {
    sidebar: sidebar, taskHeader: taskHeader, tabBar: tabBar, chat: chat,
    overview: overview, plan: plan, activity: activity, codeEditor: codeEditor,
    terminal: terminal, changes: changes, tests: tests, evidence: evidence,
    report: report, reportText: reportText, inspector: inspector, statusBar: statusBar,
    mockBadge: mockBadge
  };

})();
