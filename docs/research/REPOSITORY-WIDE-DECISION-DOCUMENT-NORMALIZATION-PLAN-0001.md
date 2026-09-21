# REPOSITORY-WIDE-DECISION-DOCUMENT-NORMALIZATION-PLAN-0001

## 0. 목적

PR #214의 RFC/ADC/ADR 템플릿 정합성 작업에서 이미 검증한 "구조 보존형
재배치(structure-preserving relocation)" 기법을 근거로, 나머지 154개
RFC/ADC/ADR 문서에 대한 안전한 정규화 계획을 수립한다. **이 문서는
계획 보고서이며, 대상 문서 중 어느 것도 수정하지 않는다.**

---

## 1. 범위 및 방법론

### 1.1 범위

- 4개 트리(Development HQ, Kernel, Governance ADC, Execution Layer)의
  RFC/ADC/ADR 문서 전체에서, 이미 처리된 10건(압축 완료 6건 + 구조
  보존형 정렬 완료 3건 + ADC-0019 별도 거버넌스 보류 1건)을 제외한
  **154건**을 대상으로 한다.
- TEMPLATE/README/CANDIDATES 파일은 제외(문서 자체가 아니라 양식·색인).

### 1.2 방법론(자동화된 신호 수집 + 근거 기반 분류)

이번 계획은 **줄 수만으로 분류하지 않는다.** 대신 다음 신호를
저장소 전체에서 스크립트로 수집했다:

1. **실제 인용 횟수(`real_cite_count`)**: 이 문서의 **전체 파일명
   슬러그**(예: `RFC-0006-structure-v1-hqs-core-execution-docs-taxonomy`)를
   본문에 포함하는 다른 문서의 수. 단, `docs/decisions/{rfc,adc,adr,open_decision}.md`
   (통합 원장), `REGISTRATION-CANDIDATES-0001.md`, `DOCUMENT-INVENTORY-0001.md`,
   `RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md`,
   `DECISION-GROUP-REGISTRY.md` 등 **등록/색인 목적의 메타 문서는
   제외**했다 — 이들은 "존재를 등재"할 뿐 "내용을 근거로 판단을
   내리는" 인용이 아니기 때문이다.
   - **버그 수정 기록**: 최초 스크립트는 **bare ID**(예: `RFC-0002`)만으로
     인용을 셌는데, 이 저장소는 3개 독립 채번 트리가 있어 `RFC-0002`가
     Dev HQ·Kernel·Execution Layer에 **각각 다른 문서**로 존재한다
     (RFC-ADC-ADR-ID-UNIFICATION-INVESTIGATION-0001.md가 이미 확인한
     구조적 사실). bare ID 매칭은 서로 다른 트리의 문서를 같은
     문서로 오인해 인용 횟수를 부풀렸다 — 전체 파일명 슬러그 매칭으로
     교체해 이 문제를 제거했다.
2. **`BASELINE.md` 실제 인용 여부(`baseline_real_cite`)**: 위 슬러그
   인용자 목록에 `docs/architecture/baseline/BASELINE.md`가 포함되는지.
   ADC-0019 사례(§Q2~§Q8을 Frozen Baseline이 8곳에서 직접 인용)와
   동일한 패턴을 다른 문서에서도 찾기 위한 신호다.
3. **감사 기록(`before_after`)**: "기존"/"교체 후" 쌍 또는 Before/After
   쌍이 본문에 존재하는지 — ADR-0011처럼 이미 실행된 Baseline 편집의
   diff 기록을 담은 문서를 식별한다.
4. **체크리스트/Self Review(`checklist`)**: `- [ ]`/`- [x]` 또는
   "Self Review" 절 존재 여부.
5. **코드 블록(`` ``` ``) 존재 여부.**
6. **줄 수·헤더 구조**는 참고 정보로만 수집했고, **분류 기준에는
   사용하지 않았다**(지시사항 준수).

### 1.3 한계(투명하게 명시)

- 이 방법론은 **스크립트 기반 신호 탐지**이며, 4개 고위험 문서
  (RFC-0020/RFC-0043/ADR-0011/ADC-0019)에서 수행한 것과 같은 전체
  원문 정독은 154건 전부에 대해 수행하지 않았다. 신호가 낮게 나온
  문서라도 실제 편집 착수 전에는 반드시 원문을 다시 읽고 개별
  재확인해야 한다 — 이 계획은 "편집해도 된다"는 최종 승인이 아니라
  "어떤 순서로, 어떤 주의 수준으로 접근해야 하는가"의 우선순위
  지도다.
- 인용 탐지는 "파일명 슬러그가 본문에 등장하는가"라는 텍스트 매칭이며,
  의미적 판단(그 인용이 실제로 얼마나 논증에 의존적인지)은 하지
  않았다. 개별 문서 편집 시 그 인용 문맥을 직접 읽고 재확인해야 한다.

---

## 2. 인벤토리 요약

| 트리 | 문서 수 |
|---|---|
| Kernel-ADC | 44 |
| Kernel-RFC | 42 |
| Kernel-ADR | 26 |
| DevHQ-RFC | 10 |
| DevHQ-ADR | 10 |
| GovAdc | 9 |
| ExecLayer-RFC | 5 |
| ExecLayer-ADC | 5 |
| ExecLayer-ADR | 2 |
| DevHQ-ADC | 1 |
| **합계** | **154** |

**저장소 전체 RFC/ADC/ADR 문서 재검증**: `glob` 재실행 결과 4개 트리
합계 **164건**(TEMPLATE/README/CANDIDATES 제외) — 이 값은 "163건"과의
불일치를 **결론적으로 해소**했다(§9.1 참조: 파일 추가/삭제가 아니라
이전 라운드 보고서 문장의 단순 산술 오기). 이번 계획은 164건
(= 이미 처리 10건 + 이번 계획 대상 154건)을 확정 기준으로 한다.

Front Matter 존재 여부 재확인: 154건 전부 **없음**(정상 — Option C
결정과 일치, 개별 문서에 Front Matter를 추가하지 않는다는 원칙이
지금까지 위반되지 않았음을 재확인).

---

## 3. 위험 분류 기준

줄 수가 아니라 위 §1.2 신호의 조합으로 4단계로 분류한다. **문서가
템플릿을 준수하지 않는다는 사실 자체는 위험도에 영향을 주지 않는다**
(모든 154건이 템플릿 미준수이므로 이는 구분 기준이 될 수 없다).

| 등급 | 기준 | 의미 |
|---|---|---|
| **Governance Hold** | `baseline_real_cite`=True **그리고** `real_cite_count` ≥ 8 | Frozen `BASELINE.md` 본문이 이 문서를 근거로 반복 인용 — ADC-0019와 동일한 패턴. 수정 시 Frozen 문서의 근거 사슬이 훼손될 위험 |
| **High** | 감사 기록(`before_after`) 존재, **또는** `baseline_real_cite`=True(위 기준 미만이라도), **또는** `real_cite_count` ≥ 5 | 외부에서 추론 근거로 실제 인용되거나, 이미 실행된 편집의 유일한 기록 — 구조 보존형 재배치만 허용, 압축 금지 |
| **Medium** | `real_cite_count` 1~4, 또는 checklist/code block 존재 | 인용 관계·감사 기록을 개별 확인한 뒤 제한적 압축 가능 |
| **Low** | 위 어느 조건도 해당하지 않음 | 압축 리스크가 상대적으로 낮음(그래도 편집 전 개별 재확인 필요) |

**주의**: 이 등급은 "위험도"이지 "변경 필요 여부"가 아니다. Low로
분류된 문서도 편집이 의무가 아니며, Governance Hold로 분류된 문서도
영구히 손대지 않는다는 뜻이 아니라 "사용자 승인 없이는 먼저 손대지
않는다"는 뜻이다.

**분류 결과 분포**: Governance Hold 17건 / High 62건 / Medium 73건 /
Low 2건.

---

## 4. 문서별 분류 (트리별)

### DevHQ-RFC (10건)

| ID | Lines | Signals | Risk | Recommended Treatment |
|---|---|---|---|---|
| `RFC-0001` | 94 | code-block, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0002` | 115 | checklist, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0004` | 124 | BASELINE-cited, cited-by=15 | Governance Hold | Explicit governance approval required |
| `RFC-0005` | 202 | BASELINE-cited, audit-record, cited-by=17 | Governance Hold | Explicit governance approval required |
| `RFC-0006` | 168 | cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0007` | 286 | code-block, cited-by=4 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0008` | 214 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0009` | 236 | cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0010` | 155 | cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0011` | 151 | cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |

### DevHQ-ADC (1건)

| ID | Lines | Signals | Risk | Recommended Treatment |
|---|---|---|---|---|
| `ADC-0005` | 196 | code-block, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |

### DevHQ-ADR (10건)

| ID | Lines | Signals | Risk | Recommended Treatment |
|---|---|---|---|---|
| `ADR-0002` | 290 | BASELINE-cited, cited-by=8 | Governance Hold | Explicit governance approval required |
| `ADR-0003` | 223 | BASELINE-cited, cited-by=3 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0004` | 281 | BASELINE-cited, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0005` | 270 | BASELINE-cited, cited-by=2 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0006` | 98 | cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0007` | 169 | cited-by=1 | Low | Safe structural relocation + full compression |
| `ADR-0008` | 148 | code-block, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADR-0009` | 160 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADR-0010` | 165 | cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADR-0011` | 128 | cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |

### Kernel-RFC (42건)

| ID | Lines | Signals | Risk | Recommended Treatment |
|---|---|---|---|---|
| `RFC-0001` | 303 | BASELINE-cited, checklist, code-block, cited-by=16 | Governance Hold | Explicit governance approval required |
| `RFC-0002` | 447 | BASELINE-cited, checklist, code-block, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0003` | 609 | BASELINE-cited, checklist, code-block, cited-by=4 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0004` | 433 | BASELINE-cited, checklist, code-block, cited-by=3 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0005` | 510 | BASELINE-cited, checklist, code-block, cited-by=4 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0006` | 456 | checklist, code-block, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0007` | 497 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0008` | 221 | checklist, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0009` | 171 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0010` | 162 | checklist, cited-by=4 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0011` | 267 | checklist, code-block, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0012` | 388 | checklist, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0013` | 232 | BASELINE-cited, checklist, cited-by=8 | Governance Hold | Explicit governance approval required |
| `RFC-0014` | 219 | checklist, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0015` | 338 | checklist, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0016` | 328 | BASELINE-cited, checklist, code-block, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0017` | 322 | BASELINE-cited, checklist, code-block, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0018` | 432 | checklist, code-block, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0019` | 437 | BASELINE-cited, checklist, cited-by=7 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0021` | 388 | checklist, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0022` | 499 | checklist, code-block, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0023` | 388 | checklist, code-block, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0024` | 352 | checklist, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0025` | 315 | checklist, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0026` | 238 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0027` | 232 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0028` | 189 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0029` | 255 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0030` | 300 | checklist, cited-by=8 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0031` | 144 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0032` | 123 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0033` | 166 | checklist, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0034` | 141 | checklist, code-block, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0035` | 235 | checklist, code-block, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0036` | 280 | code-block, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0037` | 328 | code-block, cited-by=9 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0038` | 371 | checklist, code-block, cited-by=4 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0039` | 497 | checklist, code-block, cited-by=8 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0040` | 275 | code-block, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0041` | 441 | code-block, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0042` | 362 | code-block, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0044` | 460 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |

### Kernel-ADC (44건)

| ID | Lines | Signals | Risk | Recommended Treatment |
|---|---|---|---|---|
| `ADC-0001` | 293 | BASELINE-cited, checklist, cited-by=27 | Governance Hold | Explicit governance approval required |
| `ADC-0002` | 346 | BASELINE-cited, checklist, cited-by=10 | Governance Hold | Explicit governance approval required |
| `ADC-0003` | 629 | BASELINE-cited, checklist, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0004` | 565 | BASELINE-cited, checklist, cited-by=4 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0005` | 661 | BASELINE-cited, checklist, code-block, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0006` | 592 | checklist, code-block, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0007` | 531 | checklist, code-block, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0008` | 199 | BASELINE-cited, checklist, cited-by=19 | Governance Hold | Explicit governance approval required |
| `ADC-0009` | 206 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0010` | 211 | checklist, cited-by=13 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0011` | 178 | checklist, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0012` | 290 | checklist, cited-by=4 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0013` | 309 | BASELINE-cited, checklist, cited-by=11 | Governance Hold | Explicit governance approval required |
| `ADC-0014` | 339 | BASELINE-cited, checklist, cited-by=7 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0015` | 448 | BASELINE-cited, checklist, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0016` | 440 | BASELINE-cited, checklist, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0017` | 500 | BASELINE-cited, checklist, code-block, cited-by=3 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0018` | 377 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0020` | 318 | BASELINE-cited, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0021` | 372 | code-block, cited-by=4 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0022` | 406 | cited-by=4 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0023` | 420 | cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0024` | 275 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0025` | 270 | cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0026` | 242 | cited-by=1 | Low | Safe structural relocation + full compression |
| `ADC-0027` | 581 | checklist, cited-by=11 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0028` | 366 | checklist, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0029` | 418 | checklist, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0030` | 440 | checklist, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0031` | 370 | checklist, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0032` | 314 | checklist, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0033` | 316 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0034` | 136 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0035` | 122 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0037` | 72 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0038` | 90 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0039` | 426 | checklist, code-block, cited-by=4 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0040` | 164 | checklist, cited-by=11 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0041` | 144 | checklist, cited-by=4 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0042` | 178 | checklist, cited-by=8 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0043` | 190 | checklist, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0044` | 211 | checklist, cited-by=4 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0045` | 124 | checklist, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADC-0046` | 556 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |

### Kernel-ADR (26건)

| ID | Lines | Signals | Risk | Recommended Treatment |
|---|---|---|---|---|
| `ADR-0001` | 201 | BASELINE-cited, checklist, code-block, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0002` | 177 | BASELINE-cited, checklist, code-block, cited-by=13 | Governance Hold | Explicit governance approval required |
| `ADR-0003` | 256 | BASELINE-cited, checklist, code-block, cited-by=10 | Governance Hold | Explicit governance approval required |
| `ADR-0004` | 277 | BASELINE-cited, audit-record, checklist, code-block, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0005` | 278 | BASELINE-cited, audit-record, checklist, code-block, cited-by=3 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0006` | 329 | BASELINE-cited, audit-record, checklist, code-block, cited-by=3 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0007` | 332 | BASELINE-cited, checklist, code-block, cited-by=1 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0008` | 419 | BASELINE-cited, checklist, code-block, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0009` | 459 | BASELINE-cited, audit-record, checklist, code-block, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0010` | 304 | BASELINE-cited, checklist, code-block, cited-by=7 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0012` | 551 | BASELINE-cited, audit-record, checklist, code-block, cited-by=2 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0013` | 342 | BASELINE-cited, audit-record, checklist, code-block, cited-by=2 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0014` | 381 | BASELINE-cited, audit-record, checklist, code-block, cited-by=2 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0015` | 301 | checklist, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADR-0016` | 267 | checklist, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADR-0017` | 416 | checklist, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADR-0018` | 363 | checklist, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADR-0019` | 147 | BASELINE-cited, cited-by=3 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0020` | 120 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADR-0021` | 46 | cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0022` | 51 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADR-0023` | 99 | cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `ADR-0024` | 305 | checklist, code-block, cited-by=17 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0025` | 279 | checklist, cited-by=8 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0026` | 229 | checklist, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0027` | 414 | checklist, code-block, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |

### GovAdc (9건)

| ID | Lines | Signals | Risk | Recommended Treatment |
|---|---|---|---|---|
| `ADC-0001` | 189 | BASELINE-cited, checklist, cited-by=77 | Governance Hold | Explicit governance approval required |
| `ADC-0002` | 81 | BASELINE-cited, checklist, cited-by=48 | Governance Hold | Explicit governance approval required |
| `ADC-0003` | 217 | BASELINE-cited, checklist, cited-by=66 | Governance Hold | Explicit governance approval required |
| `ADC-0004` | 121 | BASELINE-cited, checklist, cited-by=46 | Governance Hold | Explicit governance approval required |
| `ADC-0005` | 301 | BASELINE-cited, checklist, cited-by=52 | Governance Hold | Explicit governance approval required |
| `ADC-0006` | 255 | checklist, cited-by=26 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0007` | 128 | cited-by=14 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0008` | 226 | BASELINE-cited, cited-by=64 | Governance Hold | Explicit governance approval required |
| `ADC-0009` | 180 | cited-by=17 | High | Safe structural relocation (demotion only, no compression) |

### ExecLayer-RFC (5건)

| ID | Lines | Signals | Risk | Recommended Treatment |
|---|---|---|---|---|
| `RFC-0001` | 128 | checklist, cited-by=5 | High | Safe structural relocation (demotion only, no compression) |
| `RFC-0002` | 157 | checklist, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0003` | 142 | checklist, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0004` | 163 | checklist, cited-by=1 | Medium | Structural relocation + limited compression (per-doc citation check first) |
| `RFC-0005` | 178 | checklist, cited-by=2 | Medium | Structural relocation + limited compression (per-doc citation check first) |

### ExecLayer-ADC (5건)

| ID | Lines | Signals | Risk | Recommended Treatment |
|---|---|---|---|---|
| `ADC-0001` | 205 | checklist, cited-by=7 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0002` | 197 | checklist, cited-by=8 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0003` | 174 | checklist, cited-by=8 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0004` | 225 | checklist, cited-by=15 | High | Safe structural relocation (demotion only, no compression) |
| `ADC-0005` | 205 | checklist, cited-by=7 | High | Safe structural relocation (demotion only, no compression) |

### ExecLayer-ADR (2건)

| ID | Lines | Signals | Risk | Recommended Treatment |
|---|---|---|---|---|
| `ADR-0001` | 200 | checklist, code-block, cited-by=6 | High | Safe structural relocation (demotion only, no compression) |
| `ADR-0002` | 138 | checklist, code-block, cited-by=3 | Medium | Structural relocation + limited compression (per-doc citation check first) |

---

## 5. 제안 구현 배치(Batch)

이미 검증된 3가지 기법을 위험 등급에 매칭한다.

| 기법 | 적용 대상 | 근거 |
|---|---|---|
| A. 전체 압축 + 템플릿 정렬 | Low(2건) | 6개 샘플 라운드에서 검증된 방식 — 반복 서술만 표로 압축, 결정/근거/영향 보존 |
| B. 구조 보존형 재배치 + 제한적 압축 | Medium(73건) | 편집 직전 해당 문서의 슬러그 인용자를 재확인한 후, 순수 반복 문장만 축약(라벨·번호·표는 불변) |
| C. 구조 보존형 재배치만(압축 없음) | High(62건) | RFC-0020/RFC-0043/ADR-0011에서 검증된 "섹션 강등" 기법 — 번호·라벨·표·코드 블록 전부 verbatim, 헤더 레벨만 조정 |
| D. 수정 보류, 별도 승인 필요 | Governance Hold(17건) | ADC-0019와 동일 원칙 — Frozen Baseline이 직접 인용하는 문서는 사용자 승인 없이 착수하지 않는다 |

### 제안 배치 순서(위험이 낮은 것부터, 트리별로 소규모 배치)

| 배치 | 대상 | 건수 | 기법 |
|---|---|---|---|
| Batch 1 | Low 전체(DevHQ-ADR ADR-0007, Kernel-ADC ADC-0026) | 2 | A |
| Batch 2 | DevHQ-RFC Medium(RFC-0002/0007/0008/0009/0010/0011) | 6 | B |
| Batch 3 | DevHQ-ADR Medium + ExecLayer 전체 Medium | ~8 | B |
| Batch 4 | GovAdc Medium/High(Governance Hold 6건 제외) | ~3 | B/C |
| Batch 5 | Kernel-RFC Medium(25건) — 5건씩 5개 세부 배치로 재분할 | 25 | B |
| Batch 6 | Kernel-ADC Medium(25건) — 5건씩 5개 세부 배치로 재분할 | 25 | B |
| Batch 7 | Kernel-ADR Medium(8건) | 8 | B |
| Batch 8 | DevHQ-RFC/ADR High | 4 | C |
| Batch 9 | Kernel-RFC High(15건) — 5건씩 3개 세부 배치 | 15 | C |
| Batch 10 | Kernel-ADC High(14건) — 5건씩 3개 세부 배치 | 14 | C |
| Batch 11 | Kernel-ADR High(16건) — 5건씩 4개 세부 배치 | 16 | C |
| Batch 12 | ExecLayer/GovAdc/DevHQ 잔여 High | ~11 | C |
| (보류) | Governance Hold 17건 | 17 | D — 사용자 승인 후 별도 계획 |

**배치 크기 원칙**: High/Governance Hold 인접 문서는 한 배치당
5건을 넘기지 않는다(RFC-0020/RFC-0043/ADR-0011 라운드에서 3건 처리에
전체 세션 상당 시간이 소요됐음을 감안). Medium은 문서당 검증
비용이 낮으므로 최대 8건까지 허용한다.

---

## 6. 배치별 검증 요구사항

모든 배치 공통:

1. 편집 전, 대상 문서의 슬러그를 인용하는 **모든** 문서 목록을
   `grep -rn "<slug>"` 로 재수집(스냅샷 저장) — 이번 계획의 §1.2
   신호는 참고용일 뿐, 실제 편집 직전 반드시 재수집한다.
2. 편집 후, 동일 grep을 재실행해 인용 대상 라벨·번호·절 제목이
   여전히 동일한 문자열로 존재하는지 대조.
3. Document ID·Status 필드 변경 여부 확인(무변경이어야 함).
4. Front Matter 미추가 확인.
5. `git diff`에서 `-`(삭제) 라인이 "헤더 재배치/중복 제거"만인지,
   실제 서술 문장·표·코드 블록 삭제가 없는지 육안 검토.
6. Markdown 표 구조(malformed row) 스크립트 재검증.
7. Related Documents/Source Path 경로 존재 재확인.
8. **C 기법(High) 추가 요구사항**: 편집 대상 문서를 인용하는 각
   문서를 열어 그 인용 문맥이 여전히 유효한지 직접 확인(자동화된
   grep 매칭만으로 충분하다고 간주하지 않는다).
9. **B 기법(Medium) 추가 요구사항**: 압축하려는 문장이 다른 문서의
   인용 대상이 아님을 grep으로 개별 확인한 뒤에만 압축한다.
10. **[Batch 3 이후 추가] 감사용 verbatim 블록 확인**: 문서 내
    blockquote/code block이 다른 라이브 문서(`BASELINE.md`,
    `governance/README.md`, `ARTIFACT-STANDARD-v1.md` 등)에 실제로
    삽입된 원문과 일치하는지 확인하고, 일치하면 인용 깊이·위험
    등급과 무관하게 byte-for-byte 보존한다(§9-6).

배치 완료 후 다음 배치로 진행하기 전, 각 배치의 검증 결과를
`REGISTRATION-CANDIDATES-0001.md` 또는 별도 라운드 기록에 남기고
`git status`로 의도치 않은 파일 변경이 없는지 확인한다.

---

## 7. 명시적 승인이 필요한 문서(Governance Hold, 17건)

| 트리 | ID | 실제 인용 수 | 비고 |
|---|---|---|---|
| DevHQ-RFC | RFC-0004 | 15 | BASELINE.md 인용 |
| DevHQ-RFC | RFC-0005 | 17 | BASELINE.md 인용 + 감사 기록 |
| DevHQ-ADR | ADR-0002 | 8 | BASELINE.md 인용 |
| Kernel-RFC | RFC-0001 | 6 | BASELINE.md 인용(Jarvis OS Core Baseline 원문) |
| Kernel-RFC | RFC-0013 | 9 | BASELINE.md 인용 |
| Kernel-ADC | ADC-0001 | 9 | BASELINE.md 인용 |
| Kernel-ADC | ADC-0002 | 18 | BASELINE.md 인용 |
| Kernel-ADC | ADC-0008 | 10 | BASELINE.md 인용 |
| Kernel-ADC | ADC-0013 | 9 | BASELINE.md 인용 |
| Kernel-ADR | ADR-0002 | 9 | BASELINE.md 인용 |
| Kernel-ADR | ADR-0003 | 9 | BASELINE.md 인용 |
| GovAdc | ADC-0001 | 77 | BASELINE.md 최다 인용 문서 중 하나 |
| GovAdc | ADC-0002 | 48 | BASELINE.md 인용 |
| GovAdc | ADC-0003 | 66 | BASELINE.md 인용 |
| GovAdc | ADC-0004 | 46 | BASELINE.md 인용 |
| GovAdc | ADC-0005 | 52 | BASELINE.md 인용 |
| GovAdc | ADC-0008 | 64 | BASELINE.md 인용 |

**공통 특징**: 전부 Development HQ 초기 Governance ADC(`docs/governance/adc/ADC-0001~0005, 0008`)와 그에 대응하는 Kernel/Dev HQ 초기 RFC/ADR이다 —
이 저장소의 Architecture Baseline이 지금도 근거로 삼는 **가장 오래되고
가장 자주 참조되는 기초 결정 문서군**이다. `ADC-0019`와 동일한
이유(Frozen 문서의 근거 사슬 보호)로, 이번 계획은 이 17건에 대해
어떤 편집도 제안하지 않는다.

---

## 8. 변경 없이 유지를 권장하는 문서

- 위 Governance Hold 17건(§7) — 무기한이 아니라 "사용자 승인
  전까지" 보류.
- `ADC-0019`(이미 별도 거버넌스 보류 확정, 이번 계획 범위 밖).
- 이번 스크립트 신호 수집에서 포착되지 않았을 수 있는 **역사적
  Superseded/Not Accepted 문서**(예: 이미 다른 문서에 의해
  대체된 것으로 표시된 문서)는 원문 재확인 없이 "낮은 위험"으로
  넘겨짚지 않는다 — 그 대체 관계 자체가 추적성 정보이므로, 실제
  배치 착수 시 개별 확인이 필요하다.

---

## 9. 미해결 거버넌스 질문

1. **[해소됨] 164 vs 163 불일치**: 재조사 결과, 실제 파일 추가·삭제는
   없었다. `git log --diff-filter=AD --name-only`을 4개 트리 전체
   RFC/ADC/ADR 패턴에 대해 실행한 결과, 저장소 역사상 이 문서
   유형이 삭제된 사례는 0건이며, PR #214 브랜치가 분기된 이후
   새로 생성된 RFC/ADC/ADR 물리 문서도 없다(이 브랜치의 커밋은
   원장·보고서 `.md` 파일만 추가했다). "163건"은 이전 라운드
   보고서 문장이 트리별 내역(DevHQ 11+2+11, Kernel 44+46+28,
   GovAdc 10, ExecLayer 5+5+2)을 **산술로 잘못 합산한 단순
   오기**였다 — 실제 합은 164다(11+2+11+44+46+28+10+5+5+2=164,
   재계산 확인). 원장(`docs/decisions/{rfc,adc,adr}.md`)의 등록
   총계(RFC 60 + ADC 61 + ADR 41 = 162)는 이와 별개의 수치다 —
   원장은 34건의 비-결정 문서를 등록 대상에서 제외하고 교차 트리
   중복 여부를 별도 키로 관리하므로, "물리 파일 수(164)"와
   "원장 등록 행 수(162)"가 다른 것은 정상이며 추가 조사가
   필요한 불일치가 아니다.
2. **Governance Hold 17건의 최종 처리 방침**: 영구 보류인지, 별도
   경량 절차(예: Front Matter나 라벨 변경 없이 문서 최상단에 "Identity
   & Status 요약 표"만 추가하는 초저위험 변형)를 정의해 재검토할지
   결정이 필요하다.
3. **배치 실행 주체**: 154건을 전부 이 세션에서 순차 처리할지, 아니면
   일부 배치만 승인받고 나머지는 후속 세션/PR로 넘길지 — 배치 규모가
   커서 단일 PR #214에서 전부 처리하면 리뷰 부담이 커질 수 있다.
4. **압축 기준의 명문화 필요성**: Medium 배치(B 기법)에서 "순수 반복
   문장"을 판단하는 기준이 지금까지는 세션마다 개별 판단이었다 —
   반복 적용 전에 이 기준을 별도 가이드 문서로 명문화할지 검토 가치가
   있다.
5. **[Batch 2에서 발견] 자동 분류(§1.2 신호)가 놓치는 "깊은 내부
   라벨 인용" 위험**: Batch 2(DevHQ-RFC Medium 6건) 실행 전 재검증
   과정에서, 자동화 스크립트의 "전체 파일명 슬러그 인용 여부"만으로는
   포착되지 않는 위험 패턴을 발견했다 — 문서를 판정한 후속 ADC가
   그 문서의 **개별 §번호 또는 B-/Q- 라벨**을 본문 곳곳에서
   반복 인용하며 논증을 전개하는 경우(RFC-0007→ADC-0005 15회,
   RFC-0008→`governance/adc/ADC-0006.md` 6회, RFC-0009→ADC-0007
   11회, RFC-0010→ADC-0008 10회, RFC-0011→ADC-0009 8회)다. 이는
   "문서가 인용되는가"보다 훨씬 강한 신호이며, §3의 위험 등급
   기준(§1.2의 `real_cite_count`/`baseline_real_cite`)에는
   반영되지 않았다. **따라서 아직 처리하지 않은 Medium/Low 등급
   문서 전체에 대해, 실제 편집 착수 직전 `grep -n "<ID> §\|<ID>.*
   [A-Z]-[0-9]"` 형태로 그 문서를 판정한 후속 ADC/ADR 본문을
   직접 재확인하는 절차를 §6 검증 요구사항에 추가해야 한다** — 이
   재확인에서 깊은 라벨 인용이 발견되면, 등급이 Medium/Low여도
   기법 B/A 대신 기법 C(구조 보존형 재배치만, 압축 없음)로
   전환한다(Batch 1의 ADC-0026, Batch 2의 RFC-0007/0008/0009/
   0010/0011에 실제로 적용한 선례).
6. **[Batch 3에서 발견] "얕은 인용"이어도 감사용 verbatim 블록은
   별도로 보존해야 한다**: Batch 3(DevHQ-ADR ADR-0009/0010/0011,
   ExecLayer-ADR-0002)는 §9-5 재확인에서 판정 문서의 §번호·라벨
   반복 인용은 발견되지 않아 얕은 인용으로 확인됐지만, 문서 본문에
   `governance/README.md`·`ARTIFACT-STANDARD-v1.md`에 실제로 삽입된
   텍스트를 그대로 옮긴 인용 블록(blockquote/code block)을 포함하고
   있었다. 이런 블록은 인용 깊이와 무관하게 "이미 실행된 편집의
   감사 기록"이므로 압축 대상에서 제외하고 byte-for-byte 보존해야
   한다 — §6 검증 요구사항에 "문서 내 인용 블록/코드 블록이 다른
   라이브 문서에 삽입된 원문과 대조해 무변경인지 확인" 항목을
   추가로 반영해야 한다. 또한 ExecLayer-RFC-0002~0005는 각각을
   판정하는 ADC-0002~0005(`docs/core/execution-layer/`)가 §번호를
   3~4회씩 반복 인용해 §9-5 패턴이 재확인되어 기법 C로 전환했다.

---

## 10. 권장 다음 구현 배치

**[완료] Batch 1**(Low, 2건: `ADR-0007-baseline-relocation.md`,
`ADC-0026-gate-c-real-engine-partial-discharge.md`) — 완료. ADC-0026은
외부 인용은 낮았으나 내용 밀도가 높아 기법 A 대신 기법 C로 처리(§9-5
참조).

**[완료] Batch 2**(DevHQ-RFC Medium, 6건: RFC-0002/0007/0008/0009/
0010/0011) — 완료. 재검증 결과 6건 중 5건(RFC-0007/0008/0009/0010/
0011)이 §9-5가 발견한 "깊은 내부 라벨 인용" 패턴에 해당해 기법 C로
전환 처리했다. RFC-0002만 원래 계획대로 기법 B(제한적 압축)를
적용했다.

**[완료] Batch 3**(DevHQ-ADR Medium + ExecLayer 전체 Medium, 9건:
ADR-0008/0009/0010/0011, ExecLayer-RFC-0002/0003/0004/0005,
ExecLayer-ADR-0002) — 완료. 재검증 결과 ADR-0008만 얕은 인용 +
낮은 밀도로 확인되어 기법 A(전체 압축)를 적용했고, ADR-0009/0010/
0011·ExecLayer-ADR-0002는 얕은 인용이지만 감사용 verbatim 인용
블록 보존이 필요해 템플릿 정렬 + 제한적 압축(블록만 예외)을
적용했다. ExecLayer-RFC-0002/0003/0004/0005는 §9-5 패턴(판정
ADC의 §번호 반복 인용)이 재확인되어 기법 C로 전환 처리했다(§9-6
참조).

**[완료] Batch 4**(GovAdc High, Governance Hold 6건 제외 3건:
`docs/governance/adc/ADC-0006.md`, `ADC-0007.md`, `ADC-0009.md`) —
완료. Deep Reference Verification 결과 3건 전부 원래 계획대로
기법 C(구조 보존형 재배치만, 압축 없음)가 필요함을 재확인했다 —
`RFC-0008-ADC-0006-COMPLIANCE-VERIFICATION-0001.md`가 ADC-0006의
Q1/Q2/Q3·Conditions 2~6을 라벨 단위로 반복 인용(실제 코드 준수
여부 감사), `ADR-0009`(DevHQ)가 "ADC-0007 판단 1", `docs/governance/
adc/ADC-0008.md`가 "ADC-0007(§ 판단 2)"를 직접 인용, `ADR-0011`
(DevHQ)이 "ADC-0009 판단 1"·"판단 2"를 직접 인용 — 전부 §9-5가
정의한 "깊은 내부 라벨 인용" 패턴에 해당한다. 3건 모두 원문 라벨
(Q1~Q4, Conditions 1~8, Candidate A/B/C, 판단 1/2/3, Q-1/Q-2)을
100% 보존하고 헤더 위치만 조정했다(압축 없음). GovAdc 6건
(ADC-0001~0005, ADC-0008)은 Governance Hold로 이번 배치에서
제외했다(§7).

**다음 배치 권장**: Batch 5(Kernel-RFC Medium 25건, §5 기준 5건씩
5개 세부 배치로 재분할). 착수 전 §9-5·§9-6의 재확인 절차(판정
ADC/ADR의 §번호·라벨 직접 인용 여부 grep 재확인 + 감사용 verbatim
블록 존재 여부 확인)를 반드시 먼저 수행하고, 발견되는 문서는
기법 B/A 대신 기법 C로 전환하거나 verbatim 블록만 예외 보존할
것을 전제로 진행한다.

---

## 완료 조건 확인

- 문서 수정: 없음(154건 전부 미수정, 인벤토리 수집을 위한 읽기만 수행).
- Architecture/Contract 변경: 없음.
- Commit/Push: 이번 로컬 검토 단계에서는 수행하지 않음(사용자 검토 후 진행).

