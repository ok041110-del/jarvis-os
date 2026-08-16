# Evidence — 3종 통합(병렬화+출력최적화+Checkpointing) 실제 검증

PR #79까지 개별적으로 검증된 병렬화(PR #77)·출력 최적화(PR #78/79)·
Checkpointing(PR #76)을 **하나의 실행 파이프라인**(`combined/
combined_runner.py`)으로 실제 통합해 검증했다. `development-hq/`는
여전히 한 줄도 수정하지 않았다.

## NORMAL_E2E — 정상 실행 시간

| 구성 | 총 시간 |
|---|---|
| 원본(개선 없음, 순차) | 514.8~631.8초(관측 범위) |
| 병렬화만(PR #77) | 278.0초 |
| 병렬화+출력최적화(PR #79) | 202.6초 |
| **병렬화+출력최적화+Checkpointing(이번, 재구성)** | **203.0초** |

3종 통합의 정상 실행 시간(203.0초 = Wave1 46.0s + Wave2 56.3s + Wave3
62.5s + Wave4 38.2s)은 PR #79의 병렬화+출력최적화 실측(202.6초)과
사실상 동일하다 — **Checkpointing을 추가해도 정상 경로의 오버헤드는
없다**(체크포인트 파일 쓰기는 각 단계 완료 후 한 번씩만 발생하며,
BOTTLENECK 분석에서 이미 확인된 "Workflow overhead ≈ 0"과 일치).

## FAILURE_E2E / CHECKPOINT_RECOVERY — 병렬 Wave 중 강제 중단

`kill_test` 시행: **Wave1(7개 분석이 동시 실행 중)이 진행되는 도중,
4개 단계가 완료된 시점에 SIGTERM으로 강제 종료**했다.

- 강제 종료 직후 `checkpoints/manifest.json` 확인: 4개 단계
  (`news_event_analysis`, `fundamental_analysis`,
  `industry_analysis`, `technical_analysis`)가 **정확히, 손상 없이**
  기록돼 있었다 — 여러 스레드가 동시에 완료돼도 `threading.Lock`으로
  보호된 manifest 쓰기가 깨지지 않음을 실측으로 확인했다(병렬화와
  Checkpointing을 결합할 때의 유일한 신규 리스크였다).
- 재실행(같은 `trial_id`)에서 `steps_skipped_via_checkpoint`가 정확히
  그 4개와 일치했고, 나머지 7단계(Wave1 잔여 3개 + Bull/Bear +
  Synthesis + Final Report)만 새로 실행됐다.
- 최종 11/11 완주, 11개 섹션 + Disclaimer + 19개 핵심 데이터 전부
  보존(아래 OUTPUT_QUALITY 참조).

## REEXECUTION — 재계산 여부

`kill_test`의 `checkpoints/manifest.json`을 실측 집계한 결과, 두
번의 invocation(강제종료 전 1회 + 재개 1회)을 합쳐 **총 Engine
호출은 정확히 11회 — 중복/재계산은 0회**였다. 원본 `runner.py`
(all-or-nothing)였다면 이 시점의 중단은 이미 완료된 4개 분석
(실측 합산 113.3초 분의 Engine 작업)을 포함해 **11개 전부를 처음부터
다시 실행**해야 했을 것이다 — Checkpointing이 정확히 그만큼의 중복
작업을 제거했다.

## OUTPUT_QUALITY — 11개 섹션·Disclaimer·핵심 데이터 보존

`kill_test`(강제 중단 후 재개로 완성된 산출물)의 `final_report.md`를
raw_data.md의 19개 핵심 사실과 대조했다:

- 11개 필수 섹션(Fundamental/Dividend Quality/Valuation/Technical/
  Industry/News-Event/Sentiment/Bull Case/Bear Case/Synthesis) —
  **전부 존재**
- Disclaimer — **존재**
- 19개 핵심 데이터(H1 매출, GAAP 순이익 -31.4%, 배당성향 86.9%, 16년
  연속 배당 증액, 스위스 원천징수세 35%, Trailing/Forward P/E,
  DCF·시가총액 소스 불일치, CEO 해임, 16,000명 감원, Blue Bottle 매각,
  RSI, 이동평균 상충, 애널리스트 등급/목표주가) — **19/19 전부 보존**
- 1,089단어(목표 800~1200단어 범위 내)

**강제 중단·재개라는 비정상 경로를 거쳤음에도 품질 저하가 없었다.**

### 부수 관찰 — call_engine()의 콘텐츠 레벨 실패 미검출(신규)

`normal_trial1` 1차 시도에서 Synthesis 호출이 실제로 API 오류
("Self-signed certificate detected")를 반환했으나, `call_engine()`
은 `subprocess.run()`의 stdout을 그대로 반환할 뿐 내용을 검증하지
않으므로 **이 오류 메시지가 정상 산출물처럼 체크포인트됐다**(예외가
발생하지 않아 자동 복구 대상이 되지 못함). Report Writer가 이 결함을
스스로 감지해 대체 서술로 우아하게 대응했지만, `synthesis.md` 자체는
무효했다 — 수동으로 해당 체크포인트만 무효화하고 재실행해 정상
품질을 확보했다. **이는 Checkpointing이 다루도록 설계된 실패 유형
(예외/타임아웃)과 다른 새로운 실패 유형(콘텐츠 레벨의 조용한 실패)
이며, 지금 수정하지 않고 관찰로만 기록한다** — Dev HQ 개선 후보
목록에 추가할 가치가 있으나 이번 범위 밖이다.

## TOKENS / COST — 재사용(전체 파이프라인은 미계측)

`combined_runner.py`/`parallel_runner.py`는 (Dividend Stock Team의
실제 `runner.py`와 동일하게) `--output-format text`를 쓰는 진짜
`call_engine()`을 그대로 호출하므로, `call_log`에는 문자 수만
기록되고 토큰/비용은 기록되지 않는다(이 계측 방식 자체를 project-local
Team 코드와 동일하게 유지하기 위해 바꾸지 않았다). 참고용 근사치:

- `normal_trial1`: 11회 호출 합계 output 52,584자(≈13,146 토큰 근사,
  4자/토큰 가정), input 115,166자
- `kill_test`: 11회 호출 합계 output 53,269자(≈13,317 토큰 근사),
  input 115,617자

**정확한 토큰/비용은 PR #78/79에서 Final Report 단일 호출에 대해서만
`--output-format json` 진단 호출로 실측됐다**(Sonnet 출력최적화:
3,427 토큰/$0.231) — 전체 11회 파이프라인의 정확한 토큰/비용 합계는
이번에도 계측하지 않았다(관찰되지 않은 것으로 명시).

## CALL_COUNT

정상 실행: 11회(항상 동일, Team 구조 불변).
`kill_test`(강제 중단 포함): **11회**(중복 0회) — 위 REEXECUTION 참조.

## TIMEOUT

이번 두 시행 모두 180초 타임아웃이 발생하지 않았다(출력 최적화로
Final Report가 36.9~44.3초 수준으로 안정화됨, 180초 대비 충분한
여유). Timeout 상향은 이번에도 **적용하지 않았고 성능 개선으로
계산하지 않았다** — 지시대로 "보조 안전장치"로만 유지한다(정상
케이스에서 역할이 없었을 뿐 여전히 안전망으로 존재).

## INTEGRATION — 3종이 서로 간섭하지 않는가

**간섭하지 않음을 실측으로 확인했다:**
- 병렬화(Wave1/2)와 Checkpointing: `kill_test`에서 병렬 실행 중
  동시 완료가 manifest 손상 없이 처리됨 — 새로운 통합 리스크였던
  지점이 실제로 안전했다.
- 출력 최적화(Wave4)와 병렬화: Wave1~3 소요시간은 출력 최적화 유무와
  무관하게 PR #77 수준을 유지했고(46.0~56.7초, 49.8~62.5초), Wave4만
  출력 최적화의 영향을 받았다(36.9~44.3초) — 두 축이 서로 다른
  Wave에 독립적으로 작용한다.
- 출력 최적화와 Checkpointing: Checkpointing은 각 단계의 산출물을
  그대로 저장할 뿐 내용에 관여하지 않으므로, 출력 최적화된 Final
  Report도 다른 단계와 동일하게 체크포인트됐다(간섭 없음).

## DECISION

**3종 통합을 신규 Dogfooding 실행의 표준 실행 패턴으로 채택한다.**
근거:
- NORMAL_E2E: 원본(514.8~631.8초) 대비 **최대 68%(3.1배) 단축**,
  Checkpointing 추가에 따른 오버헤드는 실측상 없음(203.0초 ≈
  202.6초).
- FAILURE_E2E: 병렬 실행 중 강제 중단이라는 이번에 새로 검증된
  시나리오에서도 데이터 유실 0건, 재계산 0회.
- OUTPUT_QUALITY: 정상/실패-재개 두 경로 모두 19/19 핵심 데이터·11개
  섹션·Disclaimer 보존, 품질 저하 없음.
- INTEGRATION: 3종이 서로 다른 지점(Wave 순서, 단계 저장, 단일 호출
  내용)에 독립적으로 작용해 간섭이 없음을 확인.

**기존 완료 프로젝트(JNJ/KO/PG/Nestlé/Toyota)는 소급 수정하지
않는다** — 이미 병합된 Evidence 기록(각 EVIDENCE.md)의 재현조건을
보존하기 위함이며, 사용자 지시와도 일치한다. 표준 패턴은 **다음에
새로 시작하는 Dogfooding 실행부터** 적용 대상이 된다(project-local
`runner.py`/`agents.py`를 신규 프로젝트 디렉터리에 복제할 때
`combined_runner.py`류 구조를 참고).

## ARCHITECTURE/GOVERNANCE

- `development-hq/` 어떤 파일도 수정하지 않았다.
- 이번 3종 통합도 Capability/Role 구조를 전혀 바꾸지 않았다 — Wave
  실행 순서(병렬화), 체크포인트 저장 시점(Checkpointing), Report
  Writer instruction의 길이 제약(출력 최적화) 모두 project-local
  실행 방식/문서 정책의 변경이지 Architecture/Contract 변경이 아니다.
- **필요성이 실측으로 확인된 만큼**, "신규 Dogfooding 표준 실행
  패턴"이라는 문서화(예: 향후 project-local README 템플릿에 안내
  추가)는 검토할 가치가 있으나, 이번 PR에서 그 문서화 자체를
  수행하지는 않는다(범위 밖, 필요 시 후속 작업).
- v1.0 Freeze를 해제하지 않았다. RFC/ADC/ADR을 작성하지 않았다 —
  Dev HQ 자체는 변경되지 않았으므로 이번 결정에는 RFC가 필요하지
  않다고 판단한다.

## PHASE9_11

3종 통합이 실측으로 검증되고 신규 표준 패턴으로 채택됐지만, 이것이
곧바로 Phase 9~11 재개를 의미하지 않는다. **Phase 9~11 재개는 이
PR과 무관한 별도 조건(Dividend Stock Team 등 Investment HQ 자체의
다음 단계 필요성)이 충족돼야 한다** — 이번 Evidence는 Dev HQ 실행
인프라의 성능/안정성 검증이며, Phase 9~11 재개 여부는 여전히 사용자
판단 사항으로 남긴다.

## 관찰되지 않은 것 (명시적으로 기록)

- 전체 11회 파이프라인의 정확한 토큰/비용 합계 — 근사치만 제시(위
  TOKENS/COST 참조).
- Wave2/3/4(개별 분석 이후 단계)에서의 강제 중단·재개 시나리오 —
  PR #76(Nestlé resume_test)에서 이미 Wave4 실패 케이스는 검증됨,
  이번엔 Wave1(병렬 구간) 케이스만 신규 검증.
- `call_engine()`의 콘텐츠 레벨 실패(자체 서명 인증서 오류 등)에
  대한 자동 감지/재시도 메커니즘 — 실제로 관찰됐으나 구현하지 않고
  기록만 함(Dev HQ 개선 후보로 별도 등재 가치가 있음, 이번 범위
  밖).
- 다른 raw_data(Toyota 등)로도 3종 통합 효과가 재현되는지 — 이번엔
  Nestlé 하나로 통제.
- "신규 Dogfooding 표준 실행 패턴" 문서화(README 템플릿 등) 자체 —
  결정만 기록, 문서화 작업은 하지 않음.

---

# Architecture/Contract 변경 여부

**없음.** `development-hq/` 어떤 파일도 수정하지 않았다.
`combined_runner.py`는 병렬화(Wave 순서 하드코딩)+Checkpointing
(단계별 저장/재개)+출력 최적화(instruction 문구)를 결합한
project-local 실행 스크립트일 뿐, 새 Capability/Agent/Kernel
Component/Contract를 만들지 않았다. 실제 완료된 Dogfooding 프로젝트
(JNJ/KO/PG/Nestlé/Toyota)는 어느 것도 수정하지 않았다(소급 수정
금지 원칙 준수). v1.0 Freeze를 해제하지 않았다. RFC/ADC/ADR을
작성하지 않았다. Phase 9~11 재개는 하지 않았다 — 이 결정은 이번
Evidence와 무관한 별도 조건을 필요로 한다.
