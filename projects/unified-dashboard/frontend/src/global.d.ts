/**
 * vendor/react.development.js, vendor/react-dom.development.js를
 * 일반 <script> 태그(비-module)로 로드해 만든 전역(window.React,
 * window.ReactDOM)의 최소 타입 선언.
 *
 * 번들러/npm 의존성 없이 동작해야 하므로 @types/react를 도입하지
 * 않는다 — 이 Prototype이 실제로 사용하는 API만 최소 타입으로
 * 선언한다(any 최소화, 필요 시 확장).
 */

declare namespace React {
  type ReactNode = unknown;
  type Key = string | number;

  const Fragment: (props: { children?: ReactNode }) => ReactNode;

  function createElement(
    type:
      | string
      | ((props: Record<string, unknown>) => ReactNode)
      | typeof Fragment,
    props?: Record<string, unknown> | null,
    ...children: ReactNode[]
  ): ReactNode;

  function useState<T>(initial: T): [T, (next: T | ((prev: T) => T)) => void];
  function useEffect(effect: () => void | (() => void), deps: unknown[]): void;
}

declare namespace ReactDOM {
  interface Root {
    render(node: React.ReactNode): void;
  }

  function createRoot(container: Element | DocumentFragment): Root;
}

// JSX 최소 타입 — @types/react를 도입하지 않으므로 IntrinsicElements를
// 직접 선언한다. Intrinsic 태그 Prop은 의도적으로 any로 둔다(엄격한
// Prop 타입 검사는 이 Prototype의 목표가 아니다 — 다음 단계 후보).
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
  type Element = React.ReactNode;
  // key/ref처럼 React가 암묵적으로 모든 Element에 허용하는 Prop.
  interface IntrinsicAttributes {
    key?: React.Key;
  }
}
