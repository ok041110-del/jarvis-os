# BATCH6-COMPLETION-AND-BATCH7-READINESS-0001

## 0. 목적 및 범위

Batch 6(Kernel-ADC Medium 25건, `REPOSITORY-WIDE-DECISION-DOCUMENT-
NORMALIZATION-PLAN-0001.md` §5) 중 ADC-0021~0023(Governance Hold,
PR #217)을 제외한 잔여 22건을 대상으로 (1) §1.4 보완 방법론 재적용,
(2) 확정 가능한 Governance 결정 실행, (3) 안전이 확인된 문서의 실제
정규화, (4) 아직 안전하지 않거나 별도 승인이 필요한 문서의 명시적
이연을 수행한다. 이 문서는 그 전체 처리 근거와 결과를 기록한다.

## 1. Repository / Branch 상태

- Base commit: `3ff89dae48e513a79fe4b1a60602ed4884dea380`(PR #217
  병합 후 최신 `origin/main`)
- 작업 브랜치: `claude/batch6-completion-readiness`(신규 생성)

## 2. ADC-0024 Governance Hold 결정 (§4.1)

### 2.1 독립 재검증

- 트리 유일성: `find . -iname "ADC-0024-*.md"` → `docs/architecture/
  core/ADC-0024-gate-b-independent-observation-threshold-judgment.md`
  1개뿐(단일 트리, short-ID 안전).
- `BASELINE.md` short-ID 인용: 7곳 — 라인 1178, 1182, 1185, 1187,
  1224, 1366, 1367(전부 `grep -n` 재현 확인). 라벨 §D-B4 동반(1185,
  1366).
- 전체 short-ID 인용 문서 수(메타 제외): **10건** —
  `GLOSSARY.md`, `BASELINE.md`, `ADC-0025`, `ADC-0026`, `ADR-0013`,
  `ADR-0014`, `ADR-0018`, `RFC-0026`,
  `projects/workflow-adapter-recursive-lineage-v1/{EVIDENCE,README}.md`.

### 2.2 기준 적용

`baseline_real_cite=True`(True) ∧ `real_cite_count`(10) `≥8` → **기준
충족**. 새 기준을 만들지 않고 §3의 기존 정의를 그대로 적용했다.

### 2.3 결정

**ADC-0024를 Governance Hold 유효 범위에 추가한다**
(`REPOSITORY-WIDE-DECISION-DOCUMENT-NORMALIZATION-PLAN-0001.md`
§7.2에 기록). ADC-0024 원문은 열람만 했으며 이 작업에서 수정하지
않았다.

### 2.4 ADC-0021~0023·ADC-0025와의 관계

ADC-0024(Gate (B) 1차 부분 완화) → ADC-0025(2차 부분 완화, §D-B4를
직접 승계)로 이어지는 체인이며, ADC-0021 §8 Gate (B) 진입 조건과
같은 문장에서 병기 인용된다(BASELINE.md:1187, 1224). ADC-0025는
인용 수(6)가 임계값 미달이라 Hold로 확대하지 않고 High로만
재분류했다 — 인접성만으로 Hold를 넓히지 않는다.

## 3. High 재분류 결정 (§4.2)

| ID | 재확인 Evidence | 현재 등급 | 근거 규칙 | 결정 |
|---|---|---|---|---|
| ADC-0018 | `BASELINE.md`:1104, 1회, 라벨 없는 "범위" 언급 | Medium | §3: "baseline_real_cite=True(기준 미만이라도)" → High | **High로 확정** |
| ADC-0025 | `BASELINE.md` 6곳(§D-C2/§D-C3), 전체 인용 문서 6건 | Medium | 상동 | **High로 확정** |
| ADC-0034 | `BASELINE.md`:1325,1365, 2회, 라벨 없는 changelog 언급 | Medium | 상동 | **High로 확정** |

**결정 근거**: §3 "High" 등급 정의는 `baseline_real_cite=True`이면
인용 깊이(얕음/깊음)와 무관하게 즉시 적용되도록 이미 규정돼 있다 —
이는 새 프레임워크가 아니라 기존 규칙의 기계적 적용이다. High
재분류는 "구조 보존형 재배치만 허용, 압축 금지"라는 편집 기법
제한을 의미할 뿐, 개별 사용자 승인을 추가로 요구하지 않는다(§3
정의 자체가 그렇게 규정). 단, **이 3건의 실제 편집은 이번 작업에서
수행하지 않았다** — 결정만 확정하고, 편집은 후속 Batch 6b 또는
별도 작업으로 이관한다(문서 크기·교차 참조 확인에 추가 시간이
필요하다고 판단).

## 4. ADC-0012 / ADC-0013 조율 (§4.3)

### 4.1 교차 참조 확인

`ADC-0013-runtime-existence-scoped-reconsideration.md`(Governance
Hold, 13건 중 하나)가 `ADC-0012`를 5곳에서 인용하며, 그중 라인 297이
"`ADC-0012`의 DEFER와 모순되는가 — 아니오(§Decision Rationale)"로
**섹션 단위**를 지목한다.

### 4.2 안전성 판단

`ADC-0012`의 현재 구조를 확인한 결과, "§Decision Rationale"에
정확히 대응하는 것은 `## Decision` 하위의 `### 근거(요약)` 절이다 —
ADC-0013의 인용은 정확한 heading 문자열을 앵커링한 것이 아니라
내용을 서술적으로 가리키는 것으로 확인했다. 구조 보존형 재배치
(헤딩 레벨 조정 + Identity & Status 표 추가, 텍스트 재서술 없음)는
이 절의 본문 텍스트를 전혀 바꾸지 않으므로, 원칙적으로는 **안전**하다고
판단한다.

### 4.3 결정

**Deferred로 분류한다.** 안전성 판단 자체는 내렸으나(§4.2), 다음
이유로 이번 세션에서 실제 편집은 보류한다.

1. `ADC-0012`(290줄)는 이번 세션에서 실제로 정규화한 5건(72~211줄)
   보다 크며, `ADC-0013`(Governance Hold, 편집 절대 불가)이 그 내용을
   직접 인용하는 유일한 문서라는 점에서 검증 실패의 대가가 다른
   Medium 문서보다 크다.
2. §"배치 크기 원칙"(High/Hold 인접 문서 1배치당 5건 상한)을 적용해,
   이번 세션은 순수 Medium·저위험 5건(§5.1 참조)에 한정했다.
3. 편집 착수 시 반드시 지켜야 할 조건을 여기 기록한다: "### 근거(요약)"
   heading 텍스트를 변경하지 않을 것, 편집 후 `ADC-0013`:297의 인용
   문맥이 여전히 유효한지 재확인할 것, `ADC-0013` 자신은 어떤 경우에도
   수정하지 않을 것(Governance Hold).

**최종 상태**: ADC-0012는 정규화되지도, 원상태로 방치되지도 않은
"안전성 확인 완료, 편집 대기" 상태로 명시한다 — Batch 6b 착수 시
최우선 순위로 처리할 것을 권장한다.

## 5. ADC-0045 / Archive Cleanup 의존성 (§4.4)

### 5.1 현재 상태 재확인

- `origin/claude/jarvis-archive-cleanup-snro5w`(커밋 `e54e27f`)는
  여전히 main에 병합되지 않은 상태다(이전 세션에서 확인한 상태와
  동일, 이번 세션에서 재확인만 하고 병합·생성·수정하지 않았다).
- `ADC-0045`가 인용하는 `docs/research/ARCHIVE-CLEANUP-REVALIDATION-
  0001.md`는 그 미병합 브랜치에만 존재한다.

### 5.2 의존성 성격 판단

`ADC-0045`의 **Governance Decision 자체**(Lifecycle/Ponytail 권한
경계/Classification/Wave 정책 Accept 여부)는 이 파일의 내용에 의존하지
않는다 — 이 파일은 ADC-0045 §Q2가 "기존 Governance 체계와 충돌
없음"을 뒷받침하는 참고 선례 중 하나일 뿐이며, ADC-0045의 Decision
값(ADOPT)이나 Rationale을 바꾸지 않고도 문서 구조만 재배치할 수
있다. 즉 **정규화 자체는 이 의존성과 독립적**이다.

### 5.3 결정 및 조치

**정규화를 진행했다**(§5.1 목록 참조). 조치:

- `ARCHIVE-CLEANUP-REVALIDATION-0001.md` 인용 문구는 원문 그대로
  보존했다(경로·문구 어느 것도 수정하지 않음).
- Related Documents 표에 "(별도 Workstream, main 미병합)" 각주를
  추가해 이 의존성이 여전히 미해소 상태임을 명시했다(내용 왜곡
  아님 — 사실 기록).
- Archive Cleanup 브랜치 자체는 병합·재현·수정하지 않았다.

## 5.1 실제 정규화 완료 문서 (5건)

각 문서는 (1) 전체 슬러그 재확인 결과 실질적 외부 인용이 없거나
얕음, (2) `comm -23` 기반 라인 집합 비교로 "매칭되지 않는 삭제 줄
0건" 확인, (3) Decision/Status 값의 완전 일치를 확인한 뒤에만
정규화했다.

| ID | 원 분류 | 인용 재확인 | 검증 결과 | 처리 |
|---|---|---|---|---|
| ADC-0009 | Medium | 트리 충돌(Kernel/GovAdc 2-way) 확인 후 전체 슬러그로 재확인 — 실질 외부 인용 없음(메타 문서만) | MISSING=0 | 6-섹션 구조 보존형 재배치 |
| ADC-0037 | Medium | §Decision 3, §Out of Scope 라벨 인용 있으나 라벨 텍스트 100% 보존 | MISSING=0 | 6-섹션 구조 보존형 재배치 |
| ADC-0038 | Medium | §Out of Scope 라벨 인용 있으나 라벨 텍스트 100% 보존 | MISSING=0 | 6-섹션 구조 보존형 재배치 |
| ADC-0041 | Medium | Status "NOT DETERMINED — Real Engine Evidence Required" 문구만 인용 대상 | MISSING=0, Status byte 단위 보존 확인 | 6-섹션 구조 보존형 재배치 |
| ADC-0045 | Medium | 문서 단위 인용만(Archive Cleanup 각주는 §5 참조) | MISSING=0 | 6-섹션 구조 보존형 재배치 |

**ADC-0007은 이 표에 포함하지 않는다** — 트리 충돌(Kernel/GovAdc
2-way) 재확인 결과 실질 외부 인용이 없음(안전)까지는 확인했으나,
문서 크기(531줄)를 고려해 실제 편집은 하지 않고 §6 Deferred로
분류했다. "인용이 안전함을 확인한 것"과 "실제로 정규화한 것"을
구분하기 위해 표를 분리했다.

## 6. Deferred 문서 (13건, ADC-0012 포함)

다음 문서는 §9-5 패턴(깊은 내부 라벨 인용, Baseline 직접 인용은
아님)이 확인되어 기법 C가 필요하지만, §"배치 크기 원칙"에 따라
이번 세션에서는 편집하지 않고 다음 세부 배치(Batch 6b)로 이연한다.

| ID | 확인된 교차 참조/라벨 | 그룹 |
|---|---|---|
| ADC-0006 | RFC-0007이 "OQ-1·OQ-8", "판단 8", "§0.1/§0.2/§6.4/§11" 인용(3-way 트리 충돌 주의 — RFC-0006 페어만 유효 인용) | 단독 |
| ADC-0007 | (§5.1 참고 — 안전 확인됨, 크기(531줄)로 이연) | 단독 |
| ADC-0011 | GOVERNANCE-REVIEW-0004/0005가 "§부족한 Evidence 1·3" 인용 | ADC-0008(Hold)·ADC-0012 인접 |
| ADC-0012 | ADC-0013(Hold)이 "§Decision Rationale" 인용(§4 참조, 안전성 확인·편집 대기) | ADC-0011·ADC-0013(Hold) 인접 |
| ADC-0028 | ADR-0015/0017이 trio로 인용 | ADC-0029/0030과 coordinated unit |
| ADC-0029 | "§Q3" 라벨 — ADR-0015/0017, EVIDENCE-0005 | ADC-0028/0030과 coordinated unit |
| ADC-0030 | "§4 표" 라벨 — ADR-0015/0017 | ADC-0028/0029와 coordinated unit |
| ADC-0032 | "§Q1~Q5", "§Conditions" — ADC-0033/RFC-0026/ADR-0018 | ADC-0033과 coordinated unit |
| ADC-0033 | "§Q1/Q2" — ADR-0018 | ADC-0032와 coordinated unit |
| ADC-0035 | "§Evidence" — ADR-0020 | 단독(경미) |
| ADC-0039 | "§Validation Requirements", "§Options 1~4", "§Trade-offs", "§Engine Contract" — ADR-0024 5회 이상 | 단독 |
| ADC-0044 | "Q1~Q5", "§Decision" — ADR-0027 반복 | ADC-0043 인접 |
| ADC-0046 | "§16.6 결론" — HIGH-RISK 리뷰 | 단독 |

**coordinated unit 처리 원칙**: ADC-0028/0029/0030과 ADC-0032/0033은
같은 배치 안에서 함께 처리해야 한다 — 한 문서만 라벨을 바꾸면 trio/
pair의 다른 문서가 참조하는 라벨이 깨질 위험이 있다(이번 세션은
어느 쪽도 편집하지 않았으므로 이 원칙이 위반되지 않았다).

## 7. Batch 6 최종 분류 요약

| 분류 | 건수 | 문서 |
|---|---|---|
| Normalized(실제 편집 완료) | 5 | ADC-0009, ADC-0037, ADC-0038, ADC-0041, ADC-0045 |
| Reclassified(Medium→High, 결정 확정·편집 미착수) | 3 | ADC-0018, ADC-0025, ADC-0034 |
| Governance Hold(신규) | 1 | ADC-0024 |
| Deferred(안전성 확인, 편집 대기) | 13 | ADC-0006, ADC-0007, ADC-0011, ADC-0012, ADC-0028, ADC-0029, ADC-0030, ADC-0032, ADC-0033, ADC-0035, ADC-0039, ADC-0044, ADC-0046 |
| Governance Hold(기존, PR #217) | 3 | ADC-0021, ADC-0022, ADC-0023 |
| **합계** | **25** | |

**어떤 문서도 "미설명" 상태로 남지 않았다** — 25건 전부가 위 5개
분류(Normalized / Reclassified / Governance Hold / Deferred with
documented reason) 중 하나로 명시적으로 배정됐다.

## 8. Batch 7 준비 상태

### 8.1 Batch 7 범위(계획 §5 표 기준)

`REPOSITORY-WIDE-DECISION-DOCUMENT-NORMALIZATION-PLAN-0001.md` §5의
원 배치 순서表는 "Batch 7 | Kernel-ADR Medium(8건)"으로 정의했다.
이 문서는 그 8건을 열거하거나 착수하지 않는다 — 범위 확인만 한다.

### 8.2 Batch 7 착수 전 확인 사항

- [x] Batch 6의 25건 전부가 분류됨(§7)
- [x] Batch 6 Deferred 항목에 명시적 이유·좌표(coordinated unit)가 기록됨(§6)
- [x] Governance Hold 경계가 최신 상태(원본 17 − Ratified 4 + 신규 4 = 17건, §7/§7.1/§7.2)
- [x] 계획 문서의 Batch 5/Batch 6 상태 서술이 최신화됨(§10, "완료 조건 확인" 갱신)
- [ ] Batch 7 대상 8건에 대한 §1.4 절차(트리 유일성 → 전체 슬러그 → short-ID → 라벨 심층 확인) 미실시 — **Batch 7 착수 전 반드시 선행**
- [ ] 보호 문서 무변경 — 아래 §9 검증 결과 참조(통과)

**결론**: Batch 6의 절차적·분류적 모호성은 해소됐다. 그러나 Batch 7은
그 대상 문서에 대한 §1.4 절차가 아직 한 번도 수행되지 않았으므로,
"착수 가능"이 아니라 "다음에 착수할 대상이 명확히 식별된" 상태다 —
이번 작업은 Batch 7 실행을 시작하지 않았다.

## 9. Validation

```
git status --short          → (커밋 전 기준) 6개 문서 + 계획 문서 1개 + 이 문서 1개
git diff --check            → exit 0
```

- ADC-0019: zero-diff(열람 없음, 접촉 없음)
- Architecture Baseline(`BASELINE.md`): zero-diff(인용 검색을 위해 열람만 함)
- Development HQ Baseline: 접촉 없음
- Kernel Public Contract(ADC-0004/RFC-0004): 접촉 없음
- Decision Ledger 4종: 접촉 없음
- Governance Hold 정책 문서(Ratification): 접촉 없음
- ADC-0021/0022/0023 원문: 접촉 없음
- 정규화 6건(ADC-0007 재확인만, 실제 5건 편집: ADC-0009/0037/0038/0041/0045): 각 파일 `comm -23` 검증으로 MISSING=0 확인
- Normalization Plan 편집 중 발견한 실수: §8 헤딩이 최초 편집에서 실수로 삭제됐다가 같은 세션 내에서 즉시 발견·복구함(§10 참조, 최종 diff에는 헤딩 정상 존재로 반영)

## 완료 조건 확인

- 코드(`hqs/`, `mvp/`, `core/` 등) 변경: 없음.
- Architecture Baseline/Kernel Public Contract 변경: 없음.
- ADC-0019 변경: 없음.
- Governance Hold 대상 문서(원본 13건 + ADC-0021/0022/0023) 변경: 없음.
- Archive Cleanup 브랜치: 병합·생성·수정하지 않음.
