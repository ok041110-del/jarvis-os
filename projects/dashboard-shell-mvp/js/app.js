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
    // 분류 LLM provider 선택 — UI 기본값은 기존 Claude 경로(디폴트 변경 아님),
    // "OpenRouter"는 기존 hqs/development/mvp/openrouter_engine.py 재사용 경로다.
    llmProvider: "claude",
    messages: [
      { role: "system", text: "메시지는 선택한 LLM(Claude/OpenRouter)으로 해석된 뒤 기존 Command Resolution을 거쳐 실행된다 — Engine/Workflow 호출은 없다(읽기 전용 상태 조회만)." }
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

  function formatLLMInterpretation(result) {
    return "Claude 해석: intent=" + (result.llm_intent || "null") +
      " target_hq=" + (result.llm_target_hq || "null");
  }

  function formatOpenRouterInterpretation(result) {
    var llm = result.llm || {};
    return "OpenRouter 해석: intent=" + (llm.intent || "null") +
      " target_hq=" + (llm.target_hq || "null");
  }

  // Chat 입력을 "선택한 LLM 분류 → 기존 Command Resolution" 순서로 전달한다.
  // LLM 해석 결과와 실행 결과를 별도 메시지로 구분해 표시한다 — 실패해도(LLM
  // 호출/파싱 실패 포함) Mock으로 대체하지 않고 그대로 드러낸다.
  function runChatCommand(text, provider) {
    if (provider === "openrouter") {
      return MockData.runOpenRouterCommand(text).then(function (result) {
        state.messages.push({ role: "llm", text: formatOpenRouterInterpretation(result) });
        return result;
      });
    }
    return MockData.runLLMCommand(text).then(function (result) {
      state.messages.push({ role: "llm", text: formatLLMInterpretation(result) });
      return result;
    });
  }

  function renderChat() {
    el.chat.innerHTML = Render.chat(state.messages, state.llmProvider);
    var form = document.getElementById("chat-form");
    var input = document.getElementById("chat-input");
    var providerSelect = document.getElementById("chat-provider");
    if (providerSelect) {
      // 재렌더링은 선택을 유지한다 — 상태가 단일 source of truth고, DOM은 그 표상이다.
      providerSelect.value = state.llmProvider;
      providerSelect.addEventListener("change", function () {
        state.llmProvider = providerSelect.value;
      });
    }
    form.addEventListener("submit", function (evt) {
      evt.preventDefault();
      var text = input.value.trim();
      if (!text) return;
      var provider = state.llmProvider;
      state.messages.push({ role: "user", text: text });
      input.value = "";
      renderChat();
      scrollChatToBottom();

      runChatCommand(text, provider)
        .then(function (result) {
          state.messages.push({ role: "command", text: formatCommandResult({
            intent: provider === "openrouter"
              ? (result.llm && result.llm.intent) || null
              : result.llm_intent,
            target_hq: provider === "openrouter"
              ? (result.llm && result.llm.target_hq) || null
              : result.llm_target_hq,
            status: result.status,
            reason: result.reason,
            hq_identity: result.hq_identity,
            detail: result.detail
          }) });
          renderChat();
          scrollChatToBottom();
        })
        .catch(function (err) {
          state.messages.push({
            role: "error",
            text: "LLM 호출/파싱 실패 — Mock으로 대체하지 않음: " +
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
