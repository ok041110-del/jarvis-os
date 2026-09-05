/*
 * App Controller — Experimental Prototype
 *
 * 상태(state)를 보관하고, 이벤트에 따라 data.js에서 값을 읽어
 * render.js로 다시 그린다. 페이지 전체 reload 없이 DOM 일부만 갱신한다.
 */

(function () {

  var VALID_HQ_IDS = MockData.getHQList().map(function (hq) { return hq.id; });
  var DEFAULT_HQ = "development";

  var state = {
    activeHQ: DEFAULT_HQ,
    messages: [
      { role: "system", text: "Chat UI 상태 관리만 동작한다 — LLM/Engine에 연결되어 있지 않다." }
    ]
  };

  var el = {
    header: document.getElementById("header"),
    nav: document.getElementById("nav"),
    main: document.getElementById("main"),
    chat: document.getElementById("chat")
  };

  function hqFromHash() {
    var id = location.hash.replace(/^#/, "");
    return VALID_HQ_IDS.indexOf(id) !== -1 ? id : null;
  }

  function renderHeader() {
    el.header.innerHTML = Render.header(MockData.getSystemStatus(), MockData.getAIBudget());
    document.getElementById("btn-mock-refresh").addEventListener("click", function () {
      MockData.simulateUpdate();
      renderHeader();
      renderMain();
    });
  }

  function renderNav() {
    el.nav.innerHTML = Render.nav(MockData.getHQList(), state.activeHQ);
    var buttons = el.nav.querySelectorAll(".nav-item");
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var hqId = btn.getAttribute("data-hq");
        if (hqId === state.activeHQ) return;
        // 상태를 직접 바꾸지 않고 hash를 바꾼다 — 실제 전환은
        // hashchange 리스너 한 곳에서만 일어나, 새로고침/뒤로가기와
        // 클릭이 항상 같은 경로를 탄다.
        location.hash = hqId;
      });
    });
  }

  function renderMain() {
    var hqId = state.activeHQ;
    // getHQSnapshot()은 Development에서만 Promise를 반환한다(fetch 기반) —
    // Investment/Trading은 여전히 동기 객체를 그대로 반환하므로,
    // Promise.resolve()로 감싸 두 경우를 같은 경로에서 처리한다.
    Promise.resolve(MockData.getHQSnapshot(hqId))
      .then(function (snapshot) {
        if (hqId !== state.activeHQ) return; // 응답 도착 전 탭이 바뀐 경우 무시
        el.main.innerHTML = Render.main(hqId, snapshot);
      })
      .catch(function (err) {
        if (hqId !== state.activeHQ) return;
        el.main.innerHTML = Render.errorPanel(
          hqId,
          err && err.message ? err.message : String(err)
        );
      });
  }

  function scrollChatToBottom() {
    var messagesEl = document.getElementById("chat-messages");
    if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function formatCommandResult(result) {
    var header = "intent=" + (result.intent || "null") +
      " target_hq=" + (result.target_hq || "null") +
      " status=" + result.status;
    if (result.status !== "ok") {
      return header + " reason=" + result.reason;
    }
    var detailText = (result.detail || []).map(function (d) { return "- " + d; }).join("\n");
    return header + " hq_identity=" + result.hq_identity + (detailText ? "\n" + detailText : "");
  }

  function renderChat() {
    el.chat.innerHTML = Render.chat(state.messages);
    var form = document.getElementById("chat-form");
    var input = document.getElementById("chat-input");
    form.addEventListener("submit", function (evt) {
      evt.preventDefault();
      var text = input.value.trim();
      if (!text) return;
      state.messages.push({ role: "user", text: text });
      input.value = "";
      renderChat();
      scrollChatToBottom();

      // Chat 입력을 기존 Command Resolution(projects/command-contract/)에
      // 그대로 전달한다 — 실패해도 Mock으로 대체하지 않고 그대로 드러낸다.
      MockData.runCommand(text)
        .then(function (result) {
          state.messages.push({ role: "command", text: formatCommandResult(result) });
          renderChat();
          scrollChatToBottom();
        })
        .catch(function (err) {
          state.messages.push({
            role: "error",
            text: "Command Resolution 실패 — Mock으로 대체하지 않음: " +
              (err && err.message ? err.message : String(err))
          });
          renderChat();
          scrollChatToBottom();
        });
    });
  }

  function init() {
    var hqFromUrl = hqFromHash();
    state.activeHQ = hqFromUrl || DEFAULT_HQ;
    if (location.hash.replace(/^#/, "") !== state.activeHQ) {
      // URL을 정규화만 한다 — history entry나 hashchange를 만들지 않는다.
      history.replaceState(null, "", "#" + state.activeHQ);
    }

    window.addEventListener("hashchange", function () {
      var hqId = hqFromHash() || DEFAULT_HQ;
      if (hqId === state.activeHQ) return;
      state.activeHQ = hqId;
      renderNav();
      renderMain();
    });

    renderHeader();
    renderNav();
    renderMain();
    renderChat();
  }

  document.addEventListener("DOMContentLoaded", init);

})();
