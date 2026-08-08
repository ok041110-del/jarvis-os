---
name: md-writer
description: Writes or edits Markdown documents in this repository so humans and AI can understand them quickly via Progressive Disclosure (Summary → needed Section → Details), reading detail only when needed. Use when producing or updating any Markdown deliverable — RFC/ADC/ADR entries, Integration docs, Smoke Test reports, Skill docs, Handover docs — to keep the Summary accurate and the formatting valid. Does not decide Architecture.
---

# md-writer

## 책임

사람과 AI가 문서를 빠르게 이해하고, 필요한 경우에만 상세 내용을 읽도록 Markdown을 작성/수정한다.

## 핵심 원칙

Progressive Disclosure

Summary → 필요한 Section → Details

## Summary 규칙

- 일반적으로 3~7 bullet
- 핵심 결론/상태/결정/다음 행동을 압축
- 본문에 없는 새로운 사실을 추가하지 않음
- 본문과 의미가 일치해야 함
- 단순 반복을 최소화

## 문서 유형별 Summary

| 유형 | Summary 내용 |
|---|---|
| Architecture | 구조 / 경계 / 결정 |
| RFC | 문제 / 제안 / 핵심 변경 |
| ADC | 판단 / 이유 / 결과 |
| ADR | 결정 / 이유 / 대안 |
| Baseline | 현재 확정 상태 |
| Integration | 역할 / 설치 상태 / 핵심 사용법 |
| Smoke Test | PASS/FAIL / 핵심 Evidence |
| Skill | 목적 / Trigger / 핵심 동작 |
| Handover | 현재 상태 / 완료 / Open Issues / Next Step |

## Markdown 품질

- heading hierarchy
- list indentation
- code fence
- table syntax
- 줄바꿈
- 링크
- 중복 내용

문서가 지나치게 길어지면 Summary를 길게 만드는 대신 상세 내용을 별도 문서로 분리할지 판단한다.

## 중요

md-writer는 Architecture를 결정하지 않는다.

## Pre-Flight

- Summary와 본문의 사실이 일치하는가?
- 새로운 사실을 Summary가 만들어내지 않았는가?
- 핵심 정보가 누락되지 않았는가?
- Markdown 문법이 유효한가?
- 불필요한 반복이 없는가?
