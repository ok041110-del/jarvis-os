---
name: context-loader
description: Selects the minimum sufficient context for a task already structured by task-intake. Use after task-intake produces Required Context, or whenever about to read multiple documents in this repository, to avoid bulk-loading every Baseline/RFC/ADC/ADR document. Prioritizes authoritative sources over memory and records any unresolved context gaps.
---

# context-loader

## 책임

현재 Task에 필요한 최소 Context를 선택한다.

## 절차

1. Task Scope 확인
2. authoritative source 식별
3. Summary 우선 확인
4. 필요한 Section만 로드
5. 추가 Context가 필요한 경우에만 확장
6. 사용한 source 기록
7. unresolved context gap 기록

## 우선순위

Architecture / Baseline
→ RFC / ADC / ADR
→ Project / Development HQ Rules
→ Task-specific docs
→ Memory
→ Historical material

## 규칙

- 모든 문서를 일괄 로드하지 않는다.
- source가 존재하면 memory보다 source를 우선한다.
- boundary/contract 검증에 필요한 정보는 생략하지 않는다.
- 추측으로 누락된 정보를 채우지 않는다.
- 최소 충분 Context를 목표로 한다.

## Pre-Flight

- 필요한 authoritative source를 확보했는가?
- Summary를 먼저 확인했는가?
- 불필요한 대량 Context를 읽지 않았는가?
- Context gap이 있다면 명시했는가?
