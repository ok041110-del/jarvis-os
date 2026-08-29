import { App } from "./App.js";

/** Entry point — DOM에 마운트만 한다. */

const container = document.getElementById("root");
if (!container) {
  throw new Error("#root 요소를 찾을 수 없습니다.");
}

ReactDOM.createRoot(container).render(React.createElement(App));
