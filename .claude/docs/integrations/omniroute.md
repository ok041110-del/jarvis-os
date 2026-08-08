# OmniRoute 통합 가이드

검증일: 2026-08-08

## 정체

OmniRoute는 290+ Provider, 500+ Model을 하나의 엔드포인트로 라우팅하는 MIT 라이선스 AI Gateway다.

- 공식 저장소: https://github.com/diegosouzapw/OmniRoute
- npm 패키지: `omniroute` (검증 시점 npm 최신 버전 3.8.49)

## 설치

```bash
npm install -g omniroute
```

Docker로도 설치 가능: `docker run -d diegosouzapw/omniroute:latest`

설치 후 `omniroute doctor`로 상태를 점검한다.

## Claude Code 연결 방법

1. `omniroute serve` (또는 `omniroute setup`)로 로컬 서버를 기동한다. 기본 데이터 디렉터리는 `~/.omniroute`.
2. Claude Code 쪽에서 `ANTHROPIC_BASE_URL`을 OmniRoute 엔드포인트(예: `http://localhost:20128/v1`)로 지정하고, 대시보드에서 발급한 API Key를 사용한다.
3. 모델은 `auto`로 두면 OmniRoute가 Provider/Model을 자동 선택한다.

## 중요 — 이 실행환경(원격/일시적 컨테이너)에서의 제약

OmniRoute는 **사용자의 로컬 머신에서 상시로 떠 있어야 의미가 있는 게이트웨이 서버**다. 이 저장소 작업이 수행된 세션은 일시적(ephemeral) 컨테이너이므로:

- 이번 세션에서는 CLI 설치와 `omniroute doctor` 정상 동작까지만 검증했다.
- 서버(`omniroute serve`)를 상시로 띄워 두지 않았다 — 컨테이너 종료 시 사라지며 아무 의미가 없기 때문이다.
- 실제 연결(1~3단계)은 **사용자의 로컬 개발 환경에서** 수행해야 한다.

## Headroom과의 동시 사용 주의

Headroom(`headroomlabs-ai/headroom`)도 동일하게 `ANTHROPIC_BASE_URL`을 자신의 로컬 프록시로 재설정하는 방식이라, OmniRoute와 Headroom을 동시에 `wrap`하는 것은 **검증된 조합이 아니다**. 이번 세션에서는 Headroom 설치를 보류했다 (사용자 결정, 2026-08-08).

## 제거/롤백

```bash
omniroute stop
npm uninstall -g omniroute
rm -rf ~/.omniroute
```
