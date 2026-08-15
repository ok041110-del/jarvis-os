---
name: automation-candidate-watch
description: Detects when the same or substantially the same manual workflow has actually repeated 3+ times in this repository's real history, and reports it as an Automation Candidate — it never implements automation itself. Use when a task feels like "I've done this exact sequence of steps before," when closing out a Phase/Audit/Evidence document, or when the user asks "is there anything worth automating here?" Reports only; a Skill/Script Prototype is only ever started after the user explicitly approves it.
---

# automation-candidate-watch

## 책임

동일하거나 실질적으로 동일한 수동 작업이 실제로 3회 이상 반복된 사실을
저장소의 실제 이력(git log, 문서, PR)으로 확인하고, 그 사실만
사용자에게 보고한다. **자동화를 구현하지 않는다** — 승인 전까지는
보고로 끝난다.

## Trigger 규칙

- **3회 이상**: 같은 종류의 수동 작업(같은 단계 순서, 같은 산출물
  형태)이 저장소 실제 이력에서 3회 이상 확인될 때만 Candidate로
  본다. 2회 이하는 후보로 보고하지 않는다.
- **"실질적으로 동일"의 기준**: 산출물 구조(문서 골격, 커맨드 순서)가
  반복되는지를 본다 — 겉보기 키워드가 같아도 실제 단계·산출물이
  다르면 동일 작업으로 세지 않는다(오탐 방지, 아래 참고).
- **기록 방법**: 이 Skill은 자체 카운터나 새 저장소를 만들지 않는다
  (`development-hq/IMPLEMENTATION_RULES.md`의 Memory Service 금지
  원칙과 같은 방향). 매번 호출 시점에 `git log`, `docs/`, PR 이력을
  실제로 다시 조회해 반복 횟수를 그 자리에서 센다 — 영속 상태를
  따로 두지 않는다.

## 보고 항목 (Candidate가 실제로 있을 때만)

① 반복 횟수(실제 근거: commit/문서/PR 목록)
② 현재 Workflow(수동 단계 나열)
③ 반복 비용/불편(실제 관찰, 추측 아님)
④ 자동화 가능 단계(판단이 필요 없는 기계적 부분만)
⑤ Human 판단 단계(자동화 대상에서 항상 제외)
⑥ 기존 도구(Skill/CLI/MCP)만으로 가능한지
⑦ Runtime/Architecture 필요 여부

## 평가 원칙 (자동 강제 금지)

- **반복 횟수만으로 자동화를 권하지 않는다.** 위험(잘못 자동화됐을 때
  되돌리기 비용), 복잡도(자동화 자체의 구현/유지 비용), 절감 효과
  (실제로 아끼는 시간/실수 감소)를 함께 평가해 보고에 포함한다.
- 위험이 크거나(예: 삭제·병합·push 관련) 절감 효과가 작으면, 3회
  이상이어도 "권장하지 않음"으로 보고할 수 있다.
- **Prototype은 사용자가 명시적으로 승인한 뒤에만 시작한다.** 이
  Skill 호출만으로는 어떤 코드/Skill/Script도 만들지 않는다.

## Human-in-the-loop

- Candidate 여부의 최종 판단(자동화할지 말지)은 항상 사용자 몫이다.
- 이 Skill이 보고할 수 있는 것은 "반복된 사실 + 평가"뿐이다 —
  "자동화해야 한다"는 결론을 스스로 내리지 않는다.

## 금지

- 보고 없이 바로 Skill/Script를 구현하는 것.
- Runtime/Scheduler/Event Bus 구현.
- 반복 작업을 대신 실행하는 것(자동 merge/delete/push 등) — 이
  Skill은 관찰과 보고만 한다.
- Architecture/Contract/Governance 문서 수정, RFC/ADC/ADR 작성.
- 새 영속 상태(카운터 파일, DB 등)를 만드는 것 — 매번 실제 이력을
  다시 조회한다.

## 오탐(False Positive) 점검

보고 전에 반드시 확인한다:

- 후보로 꼽은 각 사례가 정말 같은 산출물 구조/단계 순서를 갖는가,
  아니면 우연히 이름/주제만 비슷한가?
- 이미 다른 Skill(예: `md-writer`, `validation`, `branch-lifecycle`)이
  같은 반복을 이미 다루고 있지는 않은가 — 있다면 새 Candidate가
  아니라 "기존 Skill 활용도" 문제로 분류한다.
- 표본이 이 저장소의 실제 반복인가, 다른 프로젝트/가정에서 가져온
  추측인가.

## Pre-Flight

- 반복 횟수를 실제 `git log`/문서/PR 조회로 확인했는가(추측 아님)?
- 보고만 하고 구현하지 않았는가?
- 위험/복잡도/절감 효과를 반복 횟수와 별도로 평가했는가?
- 이미 존재하는 Skill과 후보가 겹치지 않는지 확인했는가?
