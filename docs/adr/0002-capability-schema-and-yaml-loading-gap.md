# ADR-0002: Walking Skeleton 구현 중 발견된 구조적 사실 2건

날짜: 2026-08-02
상태: Accepted (Architecture 원칙 위반 아님, 기록 목적)

## 배경 (Context)
Repository 최종 정리 과정에서 문서 간 대조를 하다가, Walking Skeleton 구현(packages/core)이
설계 문서(Capability_Registry_v1.md) 및 스캐폴딩 시점의 데이터 파일(capabilities.yaml)과
두 지점에서 실제로 어긋나 있는 것을 발견했다.

## 발견한 사실 1 — Capability 스키마가 구현 중 평탄화되고 필드가 추가됨
Capability_Registry_v1.md의 스키마는 `constraints { cost_tier, latency_tier,
required_permission }`처럼 제약 조건을 중첩 객체로 정의했다. 그러나 실제
`packages/core/.../capability_registry/models.py` 구현에서는 이 세 필드가
Capability의 최상위 필드로 평탄화되었고, PoC 매칭 알고리즘을 위한 `keywords`
필드가 새로 추가되었다(원 설계 문서엔 없던 필드).

## 발견한 사실 2 — capabilities.yaml이 런타임에 실제로 로드되지 않음
Monorepo_Structure_v1.md와 Capability_Registry_v1.md는 "새 HQ는 capabilities.yaml
선언만으로 등록된다"는 것을 확장성의 핵심 근거로 삼았다. 그러나 Walking Skeleton
구현(`apps/poc-runner/main.py`)은 이 YAML 파일을 읽지 않고, 동일한 Capability 값을
`build_world()` 함수 안에 직접 하드코딩한다. 즉 **지금 시점에는 "새 HQ 추가 =
Kernel 코드 무변경"이라는 확장성 원칙이 코드로 증명되어 있지 않다** — Composition
Root를 수정해야 새 Capability가 반영된다.

## 결정 (Decision)
- 사실 1(스키마 평탄화 + keywords 추가)은 **그대로 승인**한다. Architecture v1.0의
  어떤 조항도 위반하지 않으며, Port(`ICapabilityStore` 등)의 계약을 바꾸지 않는
  구현 세부사항이다. Capability_Registry_v1.md의 스키마 표기는 차기 개정 시
  평탄화된 형태로 갱신한다(설계 변경이 아니라 표기 갱신).
- 사실 2(YAML 미로딩)는 **알려진 격차(Known Gap)로 기록**하고 지금 당장 고치지
  않는다. Walking Skeleton은 "가장 단순한 방법으로 전체 배선을 먼저 검증한다"는
  철학에 따라 하드코딩을 허용한 상태였다. 다만 이 격차가 방치되면 Capability
  Registry의 핵심 가치(레지스트리 등록만으로 확장)가 실증되지 않은 채로 남으므로,
  **Phase 1~4 완료 후 별도 증분("Capability YAML Loader")으로 반드시 해소한다.**

## 근거 (Rationale)
Re-evaluation Principle(ADR-0001)과 같은 정신 — 지금 당장 고치는 것보다,
왜 지금 안 고쳤는지와 언제 고쳐야 하는지를 남기는 것이 장기적으로 더 안전하다.

## 영향 범위 (Impact)
- `docs/architecture/v1.0/05-capability-registry.md`의 스키마 표기(차기 개정 시)
- `docs/roadmap/ROADMAP.md`에 "Capability YAML Loader" 항목 추가
- `hqs/*/capabilities.yaml`은 이번 정리에서 실제 스키마에 맞게 값만 갱신함 (동작은 안 바뀜)
