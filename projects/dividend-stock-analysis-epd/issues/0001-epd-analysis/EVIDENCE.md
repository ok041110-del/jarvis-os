# Evidence — Enterprise Products Partners(EPD) Dividend Stock Dogfooding (신규 표준 패턴 2번째 프로덕션)

신규 표준 실행 패턴(병렬화+출력최적화+Checkpointing+180초 Timeout
안전장치, PR #80에서 채택·PR #81에서 Realty Income에 첫 프로덕션
적용)을 **2번째로 프로덕션 적용**한 실행이다. 기존 14건(Stock 4·
ETF 6·Dividend Stock 6: JNJ/KO/PG/Nestlé/Toyota/Realty Income)과
중복되지 않는 신규 대상 Enterprise Products Partners L.P.(NYSE:
EPD — MLP, 분배금/K-1/DCR 구조)로 실행했다. Dividend Stock Team의
7개 역할·지시문은 변경하지 않았다.

## TARGET 선정 근거

- **법적 형태 자체가 법인이 아닌 파트너십(MLP)** — 이전 6개
  배당주(Realty Income 포함, REIT도 법인)와 근본적으로 다른 구조.
  "배당"이 아닌 "**분배금(distribution)**", 표준 1099-DIV가 아닌
  **Schedule K-1** 세금 서류, 배당성향 대신 **분배 커버리지 비율
  (DCR)** 지표.
- ETF Team의 UUP EVIDENCE.md가 언급했던 "K-1/K-3 세금 보고 구조"
  관찰(파트너십 법적 형태)을 실제 개별 종목으로 처음 검증하는
  기회이기도 하다.

## NORMAL_E2E — 정상 실행 시간

1차 시도에서 콘텐츠 레벨 실패 없이 완주(아래 CONTENT_FAILURE 참조):

| Wave | 소요시간 |
|---|---|
| Wave1(7개 분석, 병렬) | 58.3초 |
| Wave2(Bull/Bear, 병렬) | 49.7초 |
| Wave3(Synthesis) | 40.6초 |
| Wave4(Final Report) | 63.0초 |
| **총합** | **211.5초** |

원본(개선 없음, 순차) 대비 514.8~631.8초 관측 범위에서 **최대
66%(2.9배) 단축**. Realty Income(183.6초)보다 다소 길었으나
(EPD의 raw_data가 더 조밀하고 데이터 불일치 항목이 많아 입력/출력
분량이 컸음 — input 152,614자 vs Realty Income 대비 큼), 여전히
원본 대비 2.9배 이상의 개선을 유지한다.

## FAILURE_RECOVERY

이번 실행은 **1차 시도에서 콘텐츠 레벨 실패 없이 바로 완주**했다
— 강제 중단/재개 테스트는 이번 실행에서 별도로 수행하지 않았다
(PR #76/#80에서 이미 병렬 Wave 중 강제 중단 시나리오를 충분히
검증했으므로 반복하지 않음, 최소 Prototype 원칙).

## TOKENS

11회 호출 output 문자수 합계 64,422자(약 16,106 토큰, 4자/토큰
근사 — 정확한 토큰 수는 기존 Dogfooding 프로젝트들과 동일한 이유로
계측되지 않음). input 문자수 합계 152,614자(Realty Income
103,549자보다 큼 — EPD raw_data.md의 데이터 불일치 서술이 더
조밀했기 때문으로 추정).

## COST

전체 파이프라인의 정확한 비용은 계측되지 않았다(위 TOKENS와 동일한
이유). PR #78/#79의 Final Report 단일 호출 실측치(Sonnet 출력최적화:
$0.231/3,427토큰)를 참고 기준으로만 인용한다.

## CALL_COUNT

**11회**(항상 동일, Team 구조 불변). 이번 실행은 재시도 없이 1회
시도로 11회 전부 성공했다 — 재계산 0회(애초에 실패가 없었으므로).

## QUALITY — 11개 섹션/Disclaimer/핵심 데이터

- **11개 필수 섹션 전부 존재**(Dividend Quality는 "Dividend
  (Distribution) Quality"로 MLP 용어에 맞게 자연스럽게 조정됨 —
  섹션 자체는 누락이 아니라 정확한 용어 반영).
- Disclaimer 존재.
- raw_data.md의 핵심 데이터 14항목(DCF $2.3B/1.9배 커버리지, 분배금
  $0.56/+2.8%, 28년 연속 분배 증액, DCR 소스 간 불일치, 배당성향
  57%/80%/56% 정면 모순, K-1 세금서류, P/E 13.5배, EV/EBITDA 소스
  간 불일치(11.31 vs 9.82), 분배수익률 5.66%, RSI 타임프레임 불일치,
  시가총액 $84.1B, CEO 승계, 목표주가 소스 간 불일치, 애널리스트
  등급 기관별 불일치) — **14/14 전부 보존**.
- 1,190단어 — 목표(800~1200단어) 범위 내.

**결론: MLP라는 신규 법적 구조(파트너십, K-1, DCR)에서도 Dividend
Stock Team의 7개 역할이 지시문 변경 없이 그대로 유효했다.**
Dividend Quality Analyst는 배당성향 57%/80%/56%의 정면 모순을,
Valuation Analyst는 EV/EBITDA 11.31배 vs 9.82배의 동일 지표 불일치를
각각 스스로 정확히 포착했다 — 새 역할 없이 기존 역할 틀 안에서
MLP 고유의 복잡한 데이터 불일치를 흡수했다.

## CONTENT_FAILURE — 3회째 재현 여부

**이번 실행에서는 콘텐츠 레벨 실패가 재현되지 않았다.** 1차 시도가
바로 11/11 성공했다.

## FAILURE_CAUSE

해당 없음 — 실패가 발생하지 않았다.

## REPRODUCTION_COUNT

**누적 2회 유지**(PR #80: 원인=프록시/인증서 오류, PR #81: 원인=
세션 사용 한도 초과). 이번(PR #81 후속, EPD)에서는 재현되지 않아
**3회째로 격상되지 않았다.**

## DEV_HQ_NEED

지시 기준("3회째가 아니면 수정하지 않고 계속 관찰한다")에 따라,
이번 실행은 재현 자체가 없었으므로 개선 착수나 Prototype 검토가
필요하지 않다. **누적 재현 횟수는 2회로 유지되며, Dev HQ 코드/
Architecture/Contract를 수정하지 않는다.** 다음 신규 Dogfooding
실행에서도 이 관찰(콘텐츠 레벨 실패 미검출)을 계속 확인한다.

## DECISION

신규 표준 실행 패턴이 **2번째 프로덕션 적용에서도 정상 동작함을
확인했다**:
- NORMAL_E2E: 211.5초(원본 대비 최대 2.9배 단축)
- QUALITY: 14/14 핵심 데이터, 11개 섹션(MLP 용어 반영), Disclaimer
  전부 보존
- Dividend Stock Team 7개 역할이 MLP라는 새로운 법적 구조에서도
  지시문 변경 없이 유효
- 콘텐츠 레벨 실패는 이번에 재현되지 않아 누적 2회로 유지, Dev HQ
  수정 불필요

**패턴을 계속 표준으로 유지한다.**

## ARCHITECTURE/GOVERNANCE

- `development-hq/` 어떤 파일도 수정하지 않았다.
- Dividend Stock Team의 7개 역할·Architecture는 변경하지 않았다.
- 콘텐츠 레벨 실패가 3회째 재현되지 않았으므로 RFC 필요 여부 판단도
  이번엔 보류한다(2회 누적 유지).
- v1.0 Freeze를 해제하지 않았다.

## PHASE9_11

이번 실행 결과가 Phase 9~11 재개 조건이 되지 않는다 — 이 실행과
무관한 별도 조건(Investment HQ 자체의 다음 단계 필요성)을 충족해야
하며, 자동으로 재개하지 않는다.

## 관찰되지 않은 것 (명시적으로 기록)

- 강제 중단/Resume 시나리오 — 이번엔 재현하지 않음(PR #76/#80에서
  이미 충분히 검증, 최소 Prototype 원칙에 따라 반복하지 않음).
- 전체 파이프라인의 정확한 토큰/비용 총계 — 근사치만 제시.
- 3회째 콘텐츠 레벨 실패 — 이번엔 발생하지 않음, 다음 신규 실행에서
  계속 관찰.
- 여러 배당주/MLP 동시 처리 — 시도되지 않음.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다. 새
Capability/Agent/Kernel Component/Contract를 만들지 않았다.
Dividend Stock Team의 7개 역할은 지시문 변경 없이 그대로
재사용했다. 기존 완료 프로젝트(JNJ/KO/PG/Nestlé/Toyota/Realty
Income)는 소급 수정하지 않았다. v1.0 Freeze를 해제하지 않았다.
RFC/ADC/ADR을 작성하지 않았다. Phase 9~11 재개는 하지 않았다.
