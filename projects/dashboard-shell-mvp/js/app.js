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
    var snapshot = MockData.getHQSnapshot(state.activeHQ);
    el.main.innerHTML = Render.main(state.activeHQ, snapshot);
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
      renderChat();
      var messagesEl = document.getElementById("chat-messages");
      messagesEl.scrollTop = messagesEl.scrollHeight;
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
