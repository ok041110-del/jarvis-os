# Evidence — 출력 최적화 실제 채택 여부 검증 + 병렬화 통합 실행

PR #78에서 "유망 후보, 정성 검토·통합 실행 필요"로 보류됐던 출력
최적화를 이번에 (1) 정성 품질 대조, (2) `agents.py` 최소 변경 적용,
(3) 병렬화와의 실제 통합 실행까지 완료해 검증했다. `development-hq/`
는 여전히 한 줄도 수정하지 않았다.

## QUALITY — 정량 + 정성 대조

**정량**: 11개 필수 섹션(Fundamental/Dividend Quality/Valuation/
Technical/Industry/News-Event/Sentiment/Bull Case/Bear Case/
Synthesis) 전부 포함, Disclaimer 포함 — Baseline과 출력 최적화 버전
모두 동일하게 충족.

**정성(핵심 데이터 19항목 대조)**: raw_data.md에 있는 19개 핵심
수치/사실(H1 매출 CHF 43.1B, GAAP 순이익 -31.4%, 배당성향 86.9%,
16년 연속 배당 증액, 스위스 원천징수세 35%, Trailing/Forward P/E,
DCF·시가총액 소스 불일치, CEO 해임, 16,000명 감원, RSI, 이동평균
상충, 애널리스트 등급/목표주가 등)을 Baseline·출력최적화 두 산출물
에서 각각 검색 대조한 결과 **19/19 전부 보존**됐다(최초 1건은 키워드
매칭 방식의 오탐이었고, 원문 확인 결과 실제로는 존재함을 재확인).

**해석 논리(Synthesis) 대조**: Baseline과 출력 최적화 버전 모두
"Bull/Bear는 사실이 아니라 disclosure gap에 대한 가중치에서 갈린다"
는 동일한 핵심 논지를 유지했다 — 표현은 압축됐지만 판단 구조 자체는
동일했다.

**결론: 품질 저하가 확인되지 않았다.** "품질 저하가 없을 때만
출력 최적화를 채택 후보로 판정한다"는 기준을 충족한다.

## OUTPUT_TOKENS / CALL_TIME / COST — 재확인(PR #78 재사용)

PR #78에서 이미 단일 호출 기준으로 실측됨(재실험하지 않음):
Sonnet Baseline 7,481 tokens/78.8초/$0.290 → 출력최적화
3,427 tokens(-54.2%)/38.1초(-51.7%)/$0.231(-20.6%).

## E2E_TIME — 병렬화와 실제 통합 실행(프로젝션이 아닌 실측)

`shared/agents.py`의 `report_writer_final_report` instruction에
출력 길이 제약(800~1200단어, 섹션/데이터 불일치 플래그는 유지)을
최소 추가한 뒤, `parallel/parallel_runner.py`로 **11단계 전체를
실제로 재실행**했다(PR #77의 병렬화 로직은 전혀 바꾸지 않음).

| | Wave1(7분석, 병렬) | Wave2(Bull/Bear, 병렬) | Wave3(Synthesis) | Wave4(Final Report) | **총합** |
|---|---|---|---|---|---|
| 병렬화만(PR #77, trial1) | 47.0초 | 44.9초 | 74.5초 | 111.6초 | **278.0초** |
| **병렬화+출력최적화(이번, trial2, 실측)** | 46.7초 | 51.4초 | 67.7초 | **36.9초** | **202.6초** |

Wave4(Final Report)가 111.6초→36.9초로 줄어든 것이 총 시간 감소의
주 원인이며, 격리 실험(PR #78, 38.1초)과 거의 일치해(36.9초) **재현성
이 확인됐다.** Wave1~3은 원래도 개별 분석/Bull/Bear에는 출력 제약을
추가하지 않았으므로 이번 실행에서도 실질적으로 변화가 없다(오차
범위 내 변동).

**PR #78의 프로젝션(204.5초)과 이번 실측(202.6초)의 차이는 0.9%
이내** — 프로젝션이 실측으로 검증됐다.

원본(개선 없음) 대비 비교:
- 동일 호출 순차 합산 기준(이번 실행의 실제 11개 호출 시간을 그대로
  더한 값) 464.8초 → 202.6초: **-56.4%(2.29배)**
- 절대 관측 범위(raised_timeout 514.8~631.8초) 대비: **-60.6%~
  -67.9%(2.54~3.12배)**

## PARALLEL_OUTPUT_COMBINED

병렬화와 출력 최적화는 **서로 간섭하지 않고 독립적으로 합산되는
효과**임이 실측으로 확인됐다 — Wave1~3(병렬화 대상)은 이번에도 PR
#77과 비슷한 수준을 유지했고, Wave4(출력 최적화 대상)만 예상대로
줄었다. 두 최적화를 같은 파이프라인에 동시에 적용해도 서로를
훼손하지 않는다.

## DATA_ACCURACY — 누락/왜곡 여부 최종 확인

이번 통합 실행(`trials/parallel_trial2_output_optimized/final_report.md`,
1,126단어, 목표 800~1200단어 범위 내)도 11개 섹션과 Disclaimer를
전부 포함했고, 위 19개 핵심 데이터 대조 기준을 그대로 만족한다(별도
재확인 완료). **누락이나 사실 왜곡은 발견되지 않았다.**

## DECISION

**출력 최적화를 채택 후보로 확정한다** — 품질 저하 없이, 병렬화와
독립적으로 결합 가능하며, 프로젝션이 실측으로 재검증됐다.

- 이번에 적용한 변경은 `shared/agents.py`(Prototype 전용 사본)의
  `report_writer_final_report` instruction에 **문장 3개 추가**뿐이다
  — 이것이 "agents.py 최소 변경"의 실제 크기다.
- Team의 7개 역할, 11단계 구조, Bull/Bear/Synthesis/Final Report
  라는 4단계 흐름 중 어느 것도 바꾸지 않았다 — Capability/Role
  정의 변경이 아니라 Report Writer 역할이 산출하는 **문서의 분량
  정책**만 바꾼 것이다.
- **아직 실제 Dogfooding 프로젝트(JNJ/KO/PG/Nestlé/Toyota의
  `agents.py`)에는 적용하지 않았다** — 이번 검증은 Prototype
  사본에서만 이뤄졌다. 실제 프로젝트에 반영할지는 별도 사용자 승인이
  필요하다.

**우선순위 최종본**: 병렬화+출력 최적화(정상 실행시간, 결합 시
2.5~3배 단축, 실측 완료) > Checkpointing(실패 시 피해 최소화, PR
#76에서 실측 완료) > Timeout 상향(보조, PR #75/76) > 모델 교체
(기각, PR #78) > 캐시(효과 제한적, PR #77) > 호출 자체 제거(안전한
후보 없음, PR #77).

## ARCHITECTURE/GOVERNANCE

- `development-hq/` 어떤 파일도 수정하지 않았다.
- `shared/agents.py`(project-local Prototype 사본) 수정은 Capability/
  Role 구조를 바꾸지 않는 instruction 문구 추가뿐이므로 Architecture/
  Contract 변경에 해당하지 않는다고 판단한다.
- 다만 **실제 Dogfooding 프로젝트의 `agents.py`에 이 변경을
  반영하는 것**은 그 프로젝트들이 이미 완료·병합된 Evidence 기록
  (JNJ/KO/PG/Nestlé/Toyota EVIDENCE.md)의 재현 조건을 바꾸는 일이므로,
  반영 여부는 이 문서가 아니라 사용자가 별도로 결정해야 한다 — 이번
  PR은 그 반영을 수행하지 않는다.
- v1.0 Freeze를 해제하지 않았다. RFC/ADC/ADR을 작성하지 않았다.

## PHASE9_11

병렬화+출력 최적화 결합이 실측으로 검증됐지만(2.29~3.12배 단축),
**Phase 9~11 재개나 실제 Dogfooding 프로젝트 반영은 이번 Evidence
만으로 진행하지 않는다.** 다음은 사용자 결정 사항이다: (a) 이
조합을 project-local 표준 패턴(신규 Dogfooding 실행부터 병렬+출력
제약 적용)으로 채택할지, (b) 기존 완료된 프로젝트(JNJ/KO/PG/Nestlé/
Toyota)는 그대로 두고 신규 실행에만 적용할지, (c) Checkpointing까지
포함한 3종 결합을 추가로 검증할지.

## 관찰되지 않은 것 (명시적으로 기록)

- 실제 Dogfooding 프로젝트(JNJ 등)의 `agents.py` 반영 — 수행하지
  않음, Prototype 사본에서만 검증.
- 병렬화+출력최적화+Checkpointing 3종 결합의 실제 실행 — 시도하지
  않음(Checkpointing은 이번 병렬 실행에 적용되지 않았다 — parallel_
  runner.py는 checkpoint_runner.py와 별도 파일이다).
- 이번 통합 실행의 실제 API 비용 총합 — `parallel_runner.py`는
  `--output-format text`를 쓰는 실제 `call_engine()`을 그대로 호출해
  비용 필드를 기록하지 않는다(PR #78의 단일 호출 비용만 참고 가능).
- 다른 raw_data(Toyota 등)로도 동일 조합 효과가 재현되는지 — 이번엔
  Nestlé 하나로 통제했다(다른 실험들과의 비교 가능성 유지 목적).
- 반복 시행을 통한 통계적 신뢰도 — 1회 통합 실행 + 프로젝션과의
  근접성(0.9% 이내)으로 대체(최소 Prototype 원칙).

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. `shared/
agents.py`(Prototype 전용 사본) 변경은 Report Writer 역할의 문서
분량 정책만 바꾼 instruction 문구 추가이며, 새 Capability/Agent/
Kernel Component/Contract를 만들지 않았다. 실제 Dogfooding 프로젝트
파일은 어느 것도 수정하지 않았다. v1.0 Freeze를 해제하지 않았다.
RFC/ADC/ADR을 작성하지 않았다. Phase 9~11 재개는 하지 않았다 — 실제
프로젝트 반영과 Phase 재개 여부는 사용자 승인 이후로 남긴다.
