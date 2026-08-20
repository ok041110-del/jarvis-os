# ADR-0003: Kernel Context Model의 Architecture Baseline 반영

| 필드 | 내용 |
|---|---|
| ID | ADR-0003 |
| 제목 | Kernel Context Model(Model·Builder 책임·Assembly 불변식·Prompt Output Format·HQ 책임 배치)을 Architecture Baseline에 반영하기 위한 구현 결정 |
| 상태 | **Accepted** |
| Context | `docs/architecture/core/ADC-0003-kernel-context-model.md` 판단 1(Accept), 2(Accept), 3(Accept), 5(Accept·R-3 제외), 6a(Accept), 7(Accept·범위 한정) |
| 관련 RFC | `docs/architecture/core/RFC-0003-kernel-context-model.md` |
| 관련 ADC | `docs/architecture/core/ADC-0003-kernel-context-model.md` |
| 선행 ADR | `docs/04_adr/ADR-0002-core-to-kernel-terminology-unification.md` (절 번호 정책·Freeze 해석의 선례) |

이 ADR은 ADC-0003이 이미 내린 결정을 다시 논의하지 않는다. 새로운
철학이나 Architecture를 제안하지 않는다. ADC-0003의 Accept 판단
6건을 실제 문서 변경으로 옮기기 위한 **구현 결정**만 기록한다.

## Out of Scope (이 ADR이 다루지 않는 것)

ADC-0003이 Defer하거나 Accept 범위에서 제외한 것은 **하나도 Baseline에
반영하지 않는다.**

| 항목 | 근거 |
|---|---|
| 4-Layer Context Model | ADC-0002 판단 2b **Defer 유지** |
| Context Identifier 파생 규칙 | ADC-0003 판단 1b Defer |
| Context Boundary의 확정 형태 | ADC-0003 판단 4 Defer (책임 후보 지위는 ADC-0002 판단 2a에 의해 유지) |
| Engine별 Renderer (Claude/GPT/Gemini) | ADC-0003 판단 5b Defer |
| R-3 (Renderer의 순서 재배치 금지) | ADC-0003 판단 5에서 Accept 범위 제외 — 코드 재설계를 수반한다 |
| 활용 사례 4건(Prompt Cache / Conversation Resume / Context Snapshot / Memory Restore) 및 실제 HQ 통합 | ADC-0003 판단 6b Defer |
| Kernel Architecture 및 Component Design | `BASELINE.md` §10 Out of Scope **그대로 유지** |
| Development HQ 및 Execution Layer의 문서·코드 | Phase 1 종료 후 불변(ADR-0001·ADR-0002 선례). §4에서 이 제약의 충족을 실제로 확인한다 |

---

## Decision

### 1. 변경 대상 파일

| 파일 | 변경 내용 |
|---|---|
| `docs/01_architecture/BASELINE.md` | §13 Kernel Context Model 신설, 기존 §13 Version → §14로 이동, v1.1 → v1.2 |
| `docs/architecture/core/ADC-0002-kernel-definition.md` | Baseline 절 번호 인용 1건 갱신(§13 → §14) |
| `docs/00_governance/GLOSSARY.md` | Kernel Context Model 용어 5건 추가 |

그 외 어떤 파일도 변경하지 않는다.

### 2. `BASELINE.md` 절 번호 정책

ADR-0002 §2.1이 확립한 정책을 그대로 따른다 — **기존 절의 번호를
재배치하지 않고, 새 절을 Version 앞에 삽입한 뒤 Version을 마지막으로
민다.**

| 절 | 변경 전 | 변경 후 |
|---|---|---|
| §1 ~ §12 | 그대로 | **그대로** |
| Kernel Context Model | (없음) | **§13 (신설)** |
| Version | §13 | **§14** |

**깨지는 외부 인용**: 조사 결과 `BASELINE.md` §13을 인용하는 문서는
`docs/architecture/core/ADC-0002-kernel-definition.md` 1건뿐이다
("§13(판단 당시 §11): Architecture State = Frozen"). 이 1건을
"§14(판단 당시 §11 → v1.1에서 §13)"로 갱신해 추적 사슬을 보존한다.

**`ADR-0002` 본문의 "§13 Version" 언급은 갱신하지 않는다.** 그것은
ADR-0002가 **당시 수행한 변경의 기록**이지 현재 Baseline에 대한
참조가 아니다. 과거 기록을 소급 수정하지 않는다는 이 프로젝트의
원칙을 따른다.

**§11·§12 인용은 전부 그대로 유효하다**(`GLOSSARY.md` 2건).

### 3. §13 Kernel Context Model (신설) — 반영할 내용

ADC-0003이 Accept한 것만 옮긴다. 새 문장을 만들지 않는다. 다음 5개
소절로 구성한다.

#### 3.1 Kernel Context Model (판단 1)

5개 요소(Context / Context Segment / Context Source / Context
Metadata / Context Identifier)를 RFC-0003 §2의 정의 그대로 옮기고,
Accept 조건 4개(계층 분류 금지 / Engine 종속 요소 금지 / Kernel의
Identifier·시각 생성 금지 / Content·Source 해석 금지)를 함께 기록한다.

`BASELINE.md` §6 Concept Model의 "Context"와 이름이 겹치므로,
**"Kernel Context는 §6 Context의 구체화이며 §6을 재정의하지
않는다"**는 문장을 포함한다(RFC-0003 §2.8, ADC-0003 판단 1 반론
검토).

#### 3.2 Context Builder 책임 (판단 2)

4개 책임(수집·검증·병합·정렬)과 각 책임의 경계를 옮긴다. 정렬에는
**"Ordering Policy는 입력이며 Model에 박힌 분류가 아니다"**라는 Accept
조건을 반드시 함께 기록한다 — 이 조건이 4-Layer Defer를 유지시키는
장치이기 때문이다.

#### 3.3 Assembly 불변식 (판단 3)

A-1 ~ A-5와 Stable Ordering 요구 O-1 ~ O-4를 옮긴다. "Assembly의
입력은 (Segment 집합, Ordering Policy) 둘뿐이다"라는 진술을 포함한다 —
이것이 KP-2를 테스트 가능하게 만드는 문장이다.

#### 3.4 Prompt는 Output Format이다 (판단 5)

정본/표현의 방향과 Renderer 계약 **R-1·R-2·R-4·R-5**만 옮긴다.
**R-3은 옮기지 않는다**(Accept 범위 제외). Baseline에 R-3이 빠져
있다는 사실 자체를 각주로 남겨, 나중에 읽는 사람이 누락이 아니라
의도적 제외임을 알 수 있게 한다.

#### 3.5 Kernel과 HQ의 Context 책임 배치 (판단 6a)

HQ = Context 생산자 / Kernel = Context 소유자. `BOUNDARY.md`가 이미
갖고 있는 배치를 Context 영역에 적용한 것임을 명시한다.

#### 3.6 미결 항목 표기

§13 말미에 **Defer된 6개 항목을 명시적으로 나열한다.** Freeze
원칙("미결정 사항이 정직하게 드러나 추적되는 것이 목표")에 따라,
Baseline을 읽는 사람이 무엇이 아직 결정되지 않았는지 같은 자리에서
확인할 수 있어야 한다.

### 4. Development HQ · Execution Layer 불변 확인

ADC-0003의 판단 2·3·6a는 **장기적으로** `project_intelligence.py`의
Context 코드가 Kernel로 이동할 대상임을 함의하지만, ADC-0003이 그
이동을 지시하지 않았다.

따라서 이 ADR은 다음을 확인하고 그대로 유지한다.

- `development-hq/` 이하 어떤 파일도 변경하지 않는다.
- `core/execution_layer/` 이하 어떤 파일도 변경하지 않는다.
- 42개 테스트는 이번 변경으로 영향을 받지 않는다(문서만 변경).

### 5. `docs/03_adc/ADC.md` 갱신 여부

**갱신하지 않는다.** ADC.md는 Jarvis OS 수준 Open Decision의 Single
Source of Truth이며, ADC-0003의 Accept 판단은 전부 **결정**이지 미결
사항이 아니다. Defer 4건은 `BASELINE.md` §13.6과 ADC-0003 자체에
추적 가능한 형태로 기록되므로, ADC.md에 중복 등록하면 Single Source
of Truth 원칙에 반한다.

이 판단은 ADR-0002 §4가 같은 상황에서 내린 것과 동일하다.

### 6. Version 정책

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Version | v1.1 | **v1.2** |
| Status | Active | Active (변경 없음) |
| Architecture State | Frozen | **Frozen (변경 없음)** |

**Frozen 유지 근거**: `ARCHITECTURE_GOVERNANCE.md`의 Freeze 원칙은
"변경 불가"가 아니라 "절차를 거치지 않은 변경이 반영되지 않는 상태"를
뜻한다. 이번 변경은 RFC-0003 → ADC-0003 → ADR-0003 절차를 그대로
거쳤다. ADR-0001·ADR-0002의 선례와 동일하다.

**Minor 증가(v1.2)를 택한 이유**: ADR-0002가 Kernel 정의라는 새 절
2개를 추가하면서 v1.1을 택한 선례를 따른다. 이번 변경도 기존 §1~§12의
어떤 문장도 수정하지 않고 새 절 하나를 추가하는 형태이므로, 같은
규모다.

### 7. `GLOSSARY.md` 갱신

"Kernel Context Model" 절을 신설하고 5개 용어를 등재한다. 각 항목은
`BASELINE.md` §13을 정의 출처로 가리킨다(상세를 GLOSSARY에 중복
기록하지 않는다 — Single Source of Truth).

기존 Concept Model 표의 `State | Context` 행은 **수정하지 않는다.**
대신 새 절에 §6과의 관계(구체화이며 재정의가 아님)를 한 줄로
남긴다.

### 8. Migration Strategy

1. `BASELINE.md` — §13 Kernel Context Model 삽입, 기존 §13 Version →
   §14 이동 및 v1.2 갱신, 변경 이력 한 줄 추가.
2. `ADC-0002-kernel-definition.md` — §13 인용 1건을 §14로 갱신.
3. `GLOSSARY.md` — Kernel Context Model 절 추가.
4. 검증:
   - `BASELINE.md`의 절 번호가 §1~§14로 연속하는지 확인.
   - `BASELINE.md` §13을 인용하던 문서가 §14를 가리키는지 확인하고,
     남은 §11·§12 인용이 그대로 유효한지 확인.
   - `git status`로 `development-hq/`·`core/` 이하에 변경이 없는지
     확인.
   - `python3 -m pytest development-hq/mvp/tests/ core/execution_layer/*/tests/ -q`
     42건이 그대로 통과하는지 확인(문서만 변경했으므로 결과가
     달라지면 안 된다).
5. 커밋 — RFC-0003, ADC-0003, ADR-0003과 위 변경을 함께 커밋한다.

---

## Consequences

- `docs/01_architecture/BASELINE.md`가 v1.1 → v1.2가 되고, **Kernel이
  무엇을 관리하는가**가 Baseline의 일부가 된다. §11이 Kernel의
  정의(무엇인가)를, §12가 설계 원칙(어떻게 해야 하는가)을 담았다면,
  §13은 그 원칙이 적용되는 **대상**을 담는다.
- KP-2·KP-3이 처음으로 **테스트 가능한 진술**을 갖게 된다 —
  "Assembly의 입력은 (Segment 집합, Ordering Policy) 둘뿐이다",
  "순서는 전순서이며 Identifier로 tie-break한다".
- Prompt가 Kernel의 본질이 아니라 Output Format이라는 것이 Baseline
  수준에서 고정된다. 이후 어떤 Engine을 붙이더라도 Model은 그대로
  남는다(KP-5).
- **4-Layer Context Model은 여전히 Baseline에 들어가지 않는다.**
  §13.2의 Ordering Policy 외부화가 그 Defer를 유지하는 장치이며,
  훗날 4-Layer가 확정되면 Model 변경 없이 **하나의 Policy로** 들어올
  수 있다.
- **Kernel Architecture는 여전히 설계되지 않는다** — §10 Out of
  Scope가 그대로 유지되고, §13이 Builder/Assembly/Renderer를 전부
  책임으로만 기술한다(KP-1).
- **Development HQ와 Execution Layer는 한 글자도 변경되지 않는다.**
- 남는 절차 부채를 정직하게 기록한다.
  1. ADC-0003 Defer 4건(판단 1b·4·5b·6b)은 미결로 남는다. 그중 3건
     (4·5b·6b)의 재검토 조건은 **실제 Engine 호출 1회 관찰**로
     동일하다.
  2. R-3(Renderer 순서 재배치 금지)은 Accept되지도 Reject되지도
     않은 채 남는다 — 채택하려면 Execution Layer 코드 변경을 다루는
     별도 RFC가 필요하다.
  3. ADR-0002가 남긴 부채 2건(디렉토리·파일명의 `core/`, Kernel
     ADC-0001의 미작성 ADR 2건)은 이 ADR이 해소하지 않는다.
  4. Kernel Context Model이 Baseline에 들어가지만 그것을 사용하는
     실행 경로는 아직 없다(ADC-0003 판단 6b Defer). 이 공백은
     `GOVERNANCE-REVIEW-0001-post-adc-0001.md` §1이 기록한 패턴과
     같은 종류다.
- 이 ADR은 **승인되었으며**, §8에 정의된 실제 파일 변경이 이 승인에
  따라 실행된다.
