# Vendored Dependencies

이 디렉터리는 React 18.3.1의 공식 UMD Development Build를 그대로
복사한 것이다(`npm view react@18` → `node_modules/react/umd/`,
`node_modules/react-dom/umd/`에서 추출). 원본 License 헤더를 그대로
보존한다.

- `react.development.js`, `react-dom.development.js` — React 공식
  배포판(MIT License), 버전 18.3.1 고정.
- 번들러/CDN 없이 `<script>` 태그로 직접 로드하기 위해 UMD 형식을
  선택했다 — `window.React`/`window.ReactDOM` 전역을 노출한다.
- Production 최적화 빌드(`*.production.min.js`)가 아니라
  Development 빌드를 사용한다 — Prototype 단계에서는 콘솔 경고가
  디버깅에 더 유용하다고 판단했다. Production 승격 시 재검토 대상.
- 버전을 올리려면 이 파일들을 동일한 방식으로 다시 추출해
  교체한다. `package.json`/`node_modules`는 저장소에 두지 않는다
  (신규 dependency 관리 도구를 도입하지 않는다는 원칙 유지).
