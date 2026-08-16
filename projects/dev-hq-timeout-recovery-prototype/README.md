# Dev HQ Timeout/Recovery/실행시간 개선 Prototype

`docs/research/`(Dividend Stock Team) PR #74/#75에서 재현·확정된 문제
(Final Report `ENGINE_TIMEOUT_SECONDS`=180초 타임아웃 반복, all-or-nothing
저장 구조로 인한 중간 산출물 유실 위험)에 대해, **개선안을 실제
채택하기 전에 최소 Prototype으로 먼저 검증**하기 위한 실험 공간이다.
PR #76(Timeout 상향 vs Checkpointing 비교)에 이어, PR #77에서
**병렬화(Prototype C)를 포함한 End-to-End 실행시간 최적화** 검증까지
확장됐다 — `parallel/`, `E2E-OPTIMIZATION-EVIDENCE.md` 참조.

## 이 디렉터리가 하지 않는 것

- **`development-hq/` 어떤 파일도 수정하지 않는다.** `ENGINE_TIMEOUT_SECONDS`
  상수, `call_engine()` 함수, `runner.py` 패턴 자체는 이 실험 전체에서
  단 한 줄도 바뀌지 않는다. Dev HQ v1.0 Freeze를 그대로 유지한다.
- **Architecture/Contract/Governance를 변경하지 않는다.** 새 Capability,
  새 Agent, 새 Kernel Component를 만들지 않는다.
- **이 Prototype의 결과만으로 실제 구현을 채택하지 않는다.** RFC 작성,
  `engine.py`/`runner.py` 실제 수정, Phase 9~11 재개는 이 실험의 범위
  밖이며, 결과를 본 뒤 사용자 판단을 거쳐야 한다.
- **Dividend Stock Team의 Role/지시문을 바꾸지 않는다.** `shared/agents.py`
  는 Nestlé/Toyota의 `agents.py`를 import 경로만 조정해 그대로 옮긴
  것이다.

## 실험 설계

**동일한 장시간 Task**: `shared/raw_data.md`(Nestlé raw_data 그대로 —
Final Report가 180초를 안정적으로, 큰 폭으로 초과하는 것으로 이미
확인된 콘텐츠)를 두 Prototype이 동일하게 사용한다. 대상을 고정해야
"타임아웃 상향"과 "체크포인팅"의 효과를 공정하게 비교할 수 있다.

| Prototype | 무엇을 바꾸는가 | 무엇을 그대로 두는가 |
|---|---|---|
| A. `raised_timeout/` | Engine 호출의 timeout을 180초 → 400초로(프로세스 내부 함수 교체, 파일 수정 아님) | 저장 구조(all-or-nothing, 기존 `runner.py`와 동일) |
| B. `checkpointing/` | 각 단계 완료 즉시 디스크에 기록 + 재실행 시 완료된 단계는 건너뛰고 이어서 실행 | Engine 호출(180초, 진짜 `call_engine()` 그대로) |
| C. `parallel/` | 서로 독립적인 호출(7개 분석, Bull/Bear)을 `ThreadPoolExecutor`로 동시 실행(의존관계는 원래대로, 4-wave 순서 하드코딩) | Engine 호출(180초, 진짜 `call_engine()` 그대로), Role/지시문 전부 |

## 측정 항목

- **timeout 발생률**: 각 variant, N회 시행 중 실패 횟수
- **실행시간**: 시행별 총 소요시간(및 checkpointing의 경우 재실행분만의
  소요시간)
- **데이터 유실**: 실패 시 몇 개 단계의 산출물이 디스크에 남아있는가
- **실패 복구 가능성**: 실패 후 재실행이 처음부터인가, 마지막 성공
  지점부터인가

## 결과

`EVIDENCE.md` 참조.
