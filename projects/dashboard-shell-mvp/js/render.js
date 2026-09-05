/*
 * Render Layer — Experimental Prototype
 *
 * data.js가 반환한 값만 입력으로 받아 DOM을 만든다. 이 파일은 Mock
 * 여부를 모른다 — data → render 경계를 분리하기 위한 지점이다.
 */

var Render = (function () {

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function connectionBadge(connection) {
    var map = {
      MOCK: { text: "MOCK DATA", cls: "badge badge-mock" },
      NOT_IMPLEMENTED: { text: "NOT IMPLEMENTED", cls: "badge badge-planned" }
    };
    var m = map[connection] || { text: connection, cls: "badge" };
    return '<span class="' + m.cls + '">' + m.text + "</span>";
  }

  function header(systemStatus, aiBudget) {
    return (
      '<div class="header-left">JARVIS OS</div>' +
      '<div class="header-right">' +
        '<div class="status-item">' +
          '<span class="status-label">System Status</span>' +
          '<span class="status-value status-ok">' + systemStatus.kernel + "</span>" +
        "</div>" +
        '<div class="status-item">' +
          '<span class="status-label">' + escapeHtml(aiBudget.label) + "</span>" +
          '<span class="status-value">' + aiBudget.usedPercent + "%</span>" +
        "</div>" +
        '<button id="btn-mock-refresh" class="btn-refresh" type="button">Mock Refresh</button>' +
        '<span class="status-updated">Updated ' + systemStatus.updatedAt + "</span>" +
      "</div>"
    );
  }

  function nav(hqList, activeHQ) {
    var items = hqList.map(function (hq) {
      var activeCls = hq.id === activeHQ ? " nav-item-active" : "";
      return (
        '<button class="nav-item' + activeCls + '" data-hq="' + hq.id + '" type="button">' +
          escapeHtml(hq.label) +
        "</button>"
      );
    }).join("");
    return '<div class="nav-title">HQ</div>' + items;
  }

  function developmentPanel(snapshot) {
    var events = snapshot.recentEvents.map(function (e) {
      return "<li>" + escapeHtml(e) + "</li>";
    }).join("");
    var agents = snapshot.agents.map(function (a) {
      return '<span class="chip">' + escapeHtml(a) + "</span>";
    }).join("");
    // progressPercent는 Evidence 기반 값에서 null일 수 있다(Development HQ에는
    // 진행률(%) Evidence 자체가 없음) — 임의로 0%를 그리지 않고 없음을 그대로 드러낸다.
    var progressMarkup = typeof snapshot.progressPercent === "number"
      ? '<div class="progress-track"><div class="progress-fill" style="width:' + snapshot.progressPercent + '%"></div></div>'
      : '<p class="evidence-missing">진행률(%) Evidence 없음 — 표시하지 않음</p>';
    return (
      '<div class="panel-grid">' +
        '<div class="card">' +
          '<div class="card-header"><h3>Development HQ</h3>' + connectionBadge(snapshot.connection) + "</div>" +
          '<div class="card-body">' +
            '<p class="kv"><span>Stage</span><strong>' + escapeHtml(snapshot.stage) + "</strong></p>" +
            progressMarkup +
            '<p class="kv"><span>Current Task</span><strong>' + escapeHtml(snapshot.currentTask) + "</strong></p>" +
          "</div>" +
        "</div>" +
        '<div class="card">' +
          '<div class="card-header"><h3>Agent Roles</h3></div>' +
          '<div class="card-body">' + agents + "</div>" +
        "</div>" +
        '<div class="card card-wide">' +
          '<div class="card-header"><h3>Recent Events</h3></div>' +
          '<div class="card-body"><ul class="event-list">' + events + "</ul></div>" +
        "</div>" +
      "</div>"
    );
  }

  function investmentPanel(snapshot) {
    var rows = snapshot.teams.map(function (t) {
      return (
        "<tr><td>" + escapeHtml(t.name) + "</td><td>" + escapeHtml(t.status) +
        "</td><td>" + escapeHtml(t.lastDecision) + "</td></tr>"
      );
    }).join("");
    var deferred = snapshot.deferred.map(function (d) {
      return '<span class="chip chip-deferred">' + escapeHtml(d) + " (Deferred)</span>";
    }).join("");
    return (
      '<div class="panel-grid">' +
        '<div class="card card-wide">' +
          '<div class="card-header"><h3>Investment HQ — Team Status</h3>' + connectionBadge(snapshot.connection) + "</div>" +
          '<div class="card-body">' +
            '<div class="table-scroll">' +
            '<table class="table"><thead><tr><th>Team</th><th>Status</th><th>Last Trader Decision</th></tr></thead>' +
            "<tbody>" + rows + "</tbody></table>" +
            "</div>" +
          "</div>" +
        "</div>" +
        '<div class="card">' +
          '<div class="card-header"><h3>Not Yet Implemented</h3></div>' +
          '<div class="card-body">' + deferred + "</div>" +
        "</div>" +
      "</div>"
    );
  }

  function tradingPanel(snapshot) {
    return (
      '<div class="panel-grid">' +
        '<div class="card card-wide">' +
          '<div class="card-header"><h3>Trading HQ</h3>' + connectionBadge(snapshot.connection) + "</div>" +
          '<div class="card-body">' +
            '<p class="planned-banner">PLANNED</p>' +
            "<p>" + escapeHtml(snapshot.note) + "</p>" +
          "</div>" +
        "</div>" +
      "</div>"
    );
  }

  function main(hqId, snapshot) {
    if (hqId === "development") return developmentPanel(snapshot);
    if (hqId === "investment") return investmentPanel(snapshot);
    if (hqId === "trading") return tradingPanel(snapshot);
    return "<p>Unknown HQ</p>";
  }

  function errorPanel(hqId, message) {
    return (
      '<div class="panel-grid">' +
        '<div class="card card-wide">' +
          '<div class="card-header"><h3>' + escapeHtml(hqId) + ' — Evidence 연결 실패</h3>' + connectionBadge("ERROR") + "</div>" +
          '<div class="card-body">' +
            '<p class="evidence-missing">Mock으로 대체하지 않음 — 실패 원인을 그대로 표시한다.</p>' +
            "<p><code>" + escapeHtml(message) + "</code></p>" +
          "</div>" +
        "</div>" +
      "</div>"
    );
  }

  function chat(messages) {
    var list = messages.map(function (m) {
      return '<div class="chat-message chat-' + m.role + '">' +
        '<span class="chat-role">' + m.role + "</span>" +
        '<span class="chat-text">' + escapeHtml(m.text) + "</span>" +
      "</div>";
    }).join("");
    return (
      '<div class="chat-header"><h3>Chat</h3><span class="badge badge-planned">Claude 연결(해석 전용) — Engine 미호출</span></div>' +
      '<div class="chat-messages" id="chat-messages">' + list + "</div>" +
      '<form class="chat-input-row" id="chat-form">' +
        '<input type="text" id="chat-input" placeholder="메시지 입력..." autocomplete="off">' +
        '<button type="submit">Send</button>' +
      "</form>"
    );
  }

  return {
    header: header,
    nav: nav,
    main: main,
    chat: chat,
    errorPanel: errorPanel
  };

})();
