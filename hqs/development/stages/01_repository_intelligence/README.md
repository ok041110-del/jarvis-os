# Stage: Repository Intelligence

## 목적

프로젝트를 이해한다.

## Responsibility

- Repository 분석
- 관련 파일 탐색
- Symbol 검색
- Dependency 분석
- Context 최적화

## Reference

- Aider Repository Map

## 상태

Capability 배정(정식 Catalog 등록)은 아직 없다(`docs/governance/adc/
ADC-0003.md` 판단 2: Capability Catalog 확장은 Defer). 다만 Repository
분석/관련 파일 탐색/Context 최적화 Responsibility에 대응하는 실행
코드는 MVP-0005(`hqs/development/mvp/project_intelligence.py`)로 이미
존재하며, `workflow_project_intelligence.py`/`workflow_0008.py`/
`workflow_0009.py`/`workflow_artifact_flow.py`에 배선되어 있다(키워드
매칭 기반, Symbol 검색·Dependency 분석은 아직 없음 —
`docs/research/DEV-HQ-V2.0-PRODUCTION-READINESS-AUDIT-0001.md` §5
참조). 관련 MVP 계획은 `docs/decisions/rfc/RFC-0003-development-hq-sdlc-pivot.md`
§11의 MVP-0006 후보를 참조한다.
