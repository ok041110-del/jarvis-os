# Vision — Jarvis OS

## Mission
Jarvis OS는 AI Assistant를 만드는 프로젝트가 아니다.
Jarvis OS는 여러 전문 AI 조직을 운영하는 AI Organization Operating System이다.

## Goal
하나의 AI가 모든 일을 하는 것이 아니라 여러 전문 조직이 협업하는 구조를 만든다.

예)
- Development HQ
- Investment HQ
- Personal HQ
- Finance HQ
- Research HQ

각 조직은 독립적으로 발전하면서도 Kernel 아래에서 하나의 운영체제로 협력한다.

## Organization
모든 작업은 다음 구조를 따른다 (세부 계층 정의는 docs/architecture/ 참고).

```
User → Kernel → HQ → Division → Team → Agent
```

Agent는 핵심이 아니다. Organization이 핵심이다.

## Platform
Jarvis OS는 Desktop, Mobile, Web, Server 모든 환경에서 동일한 구조로 동작한다.

## Philosophy
- Build Thin, Replace Easily
- Organization First
- Architecture before Feature
- Validate before Optimize
- No Silent Failure

## Long-term Vision
Development HQ는 AI Workspace가 된다.
Investment HQ는 TradingAgents류 오픈소스를 확장한 투자 조직이 된다
(※ 특정 오픈소스명은 아직 검증 전 — 채택 시 ADR과 docs/research/에 근거를 남긴다).

향후 다양한 HQ를 추가하여 Jarvis OS를 개인용 AI 운영체제로 발전시키는 것이 목표이다.
