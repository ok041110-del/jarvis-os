# Evidence — Investment HQ Conditional Freeze 2차 Dogfooding 라운드

CONDITIONAL FREEZE 판정(`checkpoint.py` Integration `de4f5e2` 기준)이 남긴
조건 — "HQ 경로에서 실제 콘텐츠 실패가 다음에 자연 발생할 때, 저장 차단과
자동 재시도가 수동 개입 없이 실사례로 동작함을 확인" — 을 검증하기 위해,
3개 Team 전부를 `hqs/investment/run.py` 경로로 **2번째 독립 실행**했다.
콘텐츠 실패를 인위적으로 주입하지 않았다.

## INPUT

- `hqs/investment/dogfooding/{aapl-hq-verify,pg-hq-verify,efa-2026-08}/raw_data.md`
  를 그대로 복사해 신규 디렉토리(`*-run2`)에 배치(원본 미수정,
  `projects/` 원본도 이번 라운드에서 전혀 참조하지 않음).
- 체크포인트 없이 **처음부터** 실행(기존 `-run2` 아닌 디렉토리들은 이미
  완료된 상태라 재실행 시 Resume만 되고 새 Engine 호출이 발생하지
  않으므로, 새 콘텐츠 실패 관찰 기회를 얻으려면 신규 디렉토리가
  필요했다).

## EXECUTION

```
python3 hqs/investment/run.py stock "AAPL(Apple Inc.)" \
  hqs/investment/dogfooding/aapl-hq-verify-run2/raw_data.md \
  hqs/investment/dogfooding/aapl-hq-verify-run2

python3 hqs/investment/run.py dividend_stock "PG(Procter & Gamble)" \
  hqs/investment/dogfooding/pg-hq-verify-run2/raw_data.md \
  hqs/investment/dogfooding/pg-hq-verify-run2

python3 hqs/investment/run.py etf "EFA" \
  hqs/investment/dogfooding/efa-2026-08-run2/raw_data.md \
  hqs/investment/dogfooding/efa-2026-08-run2
```

## OUTPUT

| Team | 전체 완료 | ContentFailureError 발생 | 완료 단계 수 | E2E 시간 |
|---|---|---|---|---|
| Stock(AAPL) | ✅ exit 0 | 없음 | 9/9 | 147.4초 |
| Dividend Stock(PG) | ✅ exit 0 | 없음 | 11/11 | 223.8초 |
| ETF(EFA) | ✅ exit 0 | 없음 | 10/10 | 133.3초 |

3건 전부 필수 섹션 + Disclaimer 존재 확인(AAPL 8섹션, PG 10섹션+Data
Inconsistency Log, EFA 9섹션). 모든 `checkpoints/manifest.json`과
산출물 `.md` 파일을 `grep -rl "API Error"`로 검색한 결과 **어디에도
실패 시그니처가 없음** — 이번 라운드는 콘텐츠 실패를 전혀 겪지 않고
1차 시도로 완주했다.

## VALIDATION

- `pytest --ignore=archive`: 이번 라운드 실행 전후 **187 passed**(변화
  없음, 기존 182 + `test_checkpoint.py` 5).
- `git status`로 이번 라운드가 `*-run2` 신규 디렉토리 외 어떤 기존
  파일도 건드리지 않았음을 확인(원본 `aapl-hq-verify`/`pg-hq-verify`/
  `efa-2026-08`, `projects/`, `hqs/development/`, Structure/Architecture/
  Freeze 문서 — 전부 무변화).

## ANOMALY

**없음.** 관찰된 그대로 기록한다 — 이번 3건의 신규 실행에서 콘텐츠
레벨 실패가 자연 발생하지 않았다. 이전 라운드(1차 HQ 실행)에서는 3건
중 2건(EFA, PG)이 실패를 겪었지만, 이번 2차 라운드에서는 3건 전부
1차 시도로 완주했다 — 실패율이 매번 동일하게 재현되는 것이 아니라
간헐적(프록시/인증서 상태 등 인프라 조건에 의존)임을 다시 확인했다.

## CONCLUSION

**저장 차단 → `ContentFailureError` → 재실행 시 자동 복구 경로는
이번 라운드에서 실사례로 검증되지 않았다** — 검증할 실패 자체가
발생하지 않았기 때문이다. 지시(#5)에 따라 성공을 꾸며내지 않고
관찰된 사실만 기록한다:

- 확보된 것: HQ 경로 반복 실행 증거가 Team당 1건→2건으로 늘었다(총
  3건→6건). 6건 전부 완료됐고, 결함(콘텐츠 실패) 발생률은 1차
  3건 중 2건(67%) → 누적 6건 중 2건(33%)으로 재계산된다.
- 확보되지 않은 것: `checkpoint.py` Integration(`de4f5e2`)의 저장
  차단·자동 재시도 로직이 **실제 프로덕션 실행에서 자연 발생한
  실패로 동작을 증명한 사례**. 이 로직은 여전히
  `hqs/investment/tests/test_checkpoint.py`의 단위 테스트(합성
  `fn`)로만 검증된 상태다.

## 관찰되지 않은 것 (명시적으로 기록)

- Content Failure 저장 차단의 실제 프로덕션 재현 사례 — 이번에도
  얻지 못함.
- 3회 이상 반복에서의 실패율 추세(현재 6건, 2/6) — 표본이 여전히
  작아 신뢰 구간을 논하기엔 이르다.

---

# Architecture/Contract 변경 여부

**없음.** `hqs/development/`, Structure v1.0, Architecture Baseline,
Development HQ Freeze 어느 것도 수정하지 않았다. `projects/`의 기존
18건 원본을 이번 라운드에서 참조하지도 수정하지도 않았다(raw_data.md는
이미 이전 라운드에서 만든 `hqs/investment/dogfooding/` 복사본에서
다시 복사했다). 코드 변경 없음(`checkpoint.py`, `run.py`, `teams/*`
전부 무수정) — 순수 실행 및 Evidence 수집만 수행했다.
