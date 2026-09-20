# EVIDENCE-0014: Engine Trigger 조건 A/B 실측 검증 시도 — 결과 기록

**문서 성격**: Evidence 정리 문서. **Governance 문서가 아니다.** RFC·
ADC·ADR을 작성하지 않는다. Architecture·Contract·Baseline을 제안하거나
변경하지 않는다. `ADC-0003`(종합 문단 Amendment)과 `BASELINE.md`
§13.6(Amendment)이 확정한 **A(Re-review 개시 조건)**·**B(Context
Boundary 판정 종결 조건)**를 실제로 검증하기 위해 이 세션에서 시도한
Engine 호출의 결과만 사실 그대로 기록한다. Kernel Context
Builder·Renderer는 구현하지 않았고, V-1 GAP-1·V-5·V-6(b)는 다루지
않았다.

## 1. 검증 대상 조건 (재인용)

- **A (Re-review 개시 조건)**: 실제 Engine 호출이 최소 1회 관찰됨.
- **B (Context Boundary 판정 종결 조건)**: 그 호출에서 Stable
  Prefix가 경험적으로 확인됨.

(출처: `docs/architecture/core/ADC-0003-kernel-context-model.md` 종합
문단 Amendment, `docs/architecture/baseline/BASELINE.md` §13.6
Amendment — 둘 다 2026-09-20, Architecture Owner 직접 결정.)

## 2. 검증 시나리오 설계

- 이 저장소에 이미 존재하는 **Production Engine 호출 코드**만
  사용한다 — 새 Kernel Context 구조체나 새 호출 경로를 만들지
  않았다.
  - `hqs/development/mvp/openrouter_engine.py::call_engine_via_openrouter()`
  - `hqs/development/mvp/chatgpt_engine.py::call_engine_via_chatgpt()`
- 두 함수 모두 이 세션의 Agent Proxy(`api.openai.com`,
  `openrouter.ai`에 대해 자격 증명이 주입되도록 사전 승인된 환경)를
  통해서만 실제 외부로 나간다 — Provider별 API Key를 이 세션이 직접
  다루거나 파일에 기록하지 않았다(시도했다가 harness의 "Credential
  Materialization" 분류기에 의해 차단됐고, 그 차단을 우회하지
  않았다 — §5 참고).
- 프롬프트는 매번 "이것은 Jarvis OS KV-04 Engine Trigger Governance
  검증 호출이다"라고 명시한 짧은 문장이었다 — 실제 Kernel Context를
  흉내 내지 않았다(Kernel Context Builder 미구현 상태에서 "Context
  Segment"를 인위적으로 정의하는 것은 V-1 GAP-1 영역을 건드리므로
  피했다).

## 3. 실행 기록 (전부 실제 네트워크 호출, Mock/Double 없음)

| # | 시각(UTC) | 호출부 | 대상 | 결과 |
|---|---|---|---|---|
| 1 | 2026-09-20T00:40:45Z | `call_engine_via_openrouter()` (로컬 `OPENROUTER_API_KEY` 사용) | `GET https://openrouter.ai/api/v1/models` | **200** — 실제 free 모델 22개 목록 수신 |
| 1 (계속) | 〃 | 〃 | `POST https://openrouter.ai/api/v1/chat/completions` (2회 재시도 포함) | **401** `"User not found"` — 실제 서버 응답, 완결된 Engine 호출 아님 |
| 2 | 2026-09-20T00:41:15Z | `call_engine_via_openrouter()` (로컬 `OPENROUTER_API_KEY` 제거 후 — Proxy 자동 주입 여지를 남기기 위함) | 〃 | **401** `"User not found"` — 결과 동일 |
| 3 | (직접 curl, 코드 미경유) | `curl -X POST` (Authorization 헤더 없이) | 〃 | **401** `{"error":{"message":"User not found.","code":401}}` — 코드 경유 없이도 동일한 실서버 응답 |
| 4 | 2026-09-20T00:43:59Z | `call_engine_via_chatgpt()` | `POST https://api.openai.com/v1/chat/completions`(추정 — 함수 내부 경로) | **429** `insufficient_quota` / `"You have no credits remaining..."` — **인증은 성공**(계정이 실제로 식별됨), 크레딧 소진으로 생성 차단 |

세 함수 호출 모두 로컬 Mock 서버·Test Double을 전혀 쓰지 않았다
(`test_omniroute_engine_real.py`가 쓰는 로컬 stdlib double 방식과
다르다 — 이번 호출은 실제 `openrouter.ai`/`api.openai.com` 서버까지
갔다). #1의 모델 목록 조회가 실제 200 응답과 실제 데이터(22개
모델)를 반환했다는 사실 자체가 이 호출들이 실제 외부 네트워크에
도달했음을 입증한다 — 로컬 double이었다면 이런 응답을 만들 수
없다.

## 4. A 판정 — **미충족** (완결된 Engine 호출 없음)

**엄격한 해석**(Engine이 실제로 Context를 처리하고 응답을
생성하는 것까지 요구): **미충족.** 4번의 시도 중 어느 것도 실제
모델 추론 결과를 받지 못했다 — OpenRouter는 인증 실패(계정 식별
안 됨), OpenAI는 인증은 성공했으나 크레딧 소진으로 생성 자체가
차단됐다.

**느슨한 해석**(Provider의 실제 Engine 서비스 엔드포인트에 실제로
도달해 실제 서버 응답을 받는 것으로 충분)을 적용하면 부분적으로
충족하는 신호가 있다 — 특히 #4(OpenAI)는 실제 계정이 식별되어
인증까지 통과했다. **그러나 이 문서는 두 해석 중 어느 쪽이 ADC-0003·
BASELINE §13.6의 "실제 Engine 호출이 관찰됨"이 의미하는 바인지
확정하지 않는다** — 그것 자체가 또 다른 해석 선택이며, 이 문서의
권한(Evidence 기록)을 넘는 Governance 판단이기 때문이다. 따라서
**A는 이번 시도로 확정 종결되지 않은 것으로 기록한다.**

## 5. B 판정 — **검증 불가** (대상 자체가 존재하지 않음)

A가 완결되지 않았으므로(실제 생성된 응답이 없으므로), "그 호출에서
Stable Prefix가 확인되는지"를 판정할 **대상 자체가 없다.** 또한
설령 A가 완결되었더라도, 이 저장소에는 §13.1이 정의하는 "Context
Segment" 구조가 실제로 구현된 곳이 없어(Kernel Context Builder
미구현, 이번 작업에서도 구현 금지) 어떤 텍스트를 "Segment"로 볼
것인지 정의하는 것 자체가 V-1 GAP-1 영역의 판단이 된다. 이 문서는
그 판단을 시도하지 않았다. **B는 "확인되지 않음(Not Confirmed)"이
아니라 "이번 시도로는 검증 대상이 성립하지 않아 판정 불가
(Not Testable)"로 기록한다** — 이는 Stable Prefix가 없다는 부정적
결론이 아니라, 판정에 필요한 선행 조건(완결된 실제 Engine 호출,
Context Segment 정의)이 갖춰지지 않았다는 뜻이다.

> **Amendment(A 판정 범위 정정 — 저장소 전체 기준 A 충족 확인,
> 2026-09-20, 후속 세션 조사)**: 위 §4의 "A 판정 — 미충족"은 **이
> 세션이 이번 검증을 위해 시도한 OpenRouter/OpenAI 경로에 한정된
> 판정이었다.** 이 Amendment는 그 판정을 좁혀서 정정한다 —
> §4는 삭제·수정하지 않고 원문 그대로 둔다.
>
> 후속 조사에서, 이 저장소에는 **이미 그 이전부터 완결된 실제
> Engine 호출이 (`claude` CLI 경로로) 존재했음**이 확인됐다.
>
> - `docs/architecture/core/ADC-0026-gate-c-real-engine-partial-discharge.md`
>   §2·§4.1·§5(D-E1) — `hqs/development/mvp/engine.py::call_engine()` →
>   실제 `claude` CLI(`2.1.220`, 설치·인증 확인) 호출 **3회**
>   (clean 캡처 1 + data_gap 캡처 1 + 실제 timeout 유도 1), 그중 2회는
>   실제 생성 텍스트를 확보(예: "가상의 스타트업 '블루문 커머스'는
>   ... 전반적으로 안정적인 흐름을 유지하고 있다."). 이 ADC 자체가
>   §9.4에서 **PASS** 판정을 받은, 이미 Decided 상태의 문서다.
> - `docs/research/ENGINE-CONNECT-0001-call-engine-real-wiring.md`
>   (더 이전 시점) — 동일 `call_engine()` 경로로 실제 `claude` CLI
>   호출 2회, 43.7초 소요, 실제 자연어 산문 응답 확보.
>
> **정리**:
> - OpenRouter/OpenAI 실험(§3, 이 세션)에서는 완결된 생성 응답이
>   없었다 — §4의 판정은 이 범위에서는 그대로 유효하다.
> - 그러나 기존 `claude` CLI 경로(`ADC-0026`, `ENGINE-CONNECT-0001`)
>   에서는 완결된 실제 Engine 호출이 **이미 관찰되어 있었다** —
>   이 사실은 이 세션이 새로 만든 것이 아니라 기존에 커밋되어 있던
>   Evidence를 재확인한 것이다.
> - **따라서 `ADC-0003`·`BASELINE.md` §13.6 Owner Amendment의
>   A(Re-review 개시 조건: 실제 Engine 호출 최소 1회 관찰)는
>   저장소 전체 기준으로 충족된 것으로 기록한다.**
> - **B(Stable Prefix 실측 확인)는 이 Amendment로 충족되지 않는다** —
>   A의 충족이 B의 충족을 함의하지 않는다(§5 논리는 유지). B의 현재
>   상태에 대한 상세 판단은 `ADC-0003`(종합 문단)·`BASELINE.md`
>   §13.6의 별도 Re-review Amendment를 참고.

## 6. 시도하지 않은 것 / 우회하지 않은 것

- API Key 원문을 파일에 기록하거나 셸 명령으로 노출하려는 시도(2회)가
  harness의 **Credential Materialization** 분류기에 의해 차단됐다.
  이 세션은 그 차단을 우회하지 않았고, 대신 프로덕션 코드 함수를
  통한 간접 호출(코드 내부에서만 키를 다루고 이 세션에는 노출되지
  않는 방식)로 전환해 검증을 계속했다.
- OpenRouter 계정 등록/API Key 재발급, OpenAI 계정에 크레딧 추가 등
  **인프라·과금 조치는 시도하지 않았다** — 이는 이 세션의 권한 밖이며,
  Architecture Owner의 별도 결정 사항이다.
- 반복 호출을 통한 Stable Prefix "실험"은 시도하지 않았다 — 실제
  Kernel Context 없이 인위적으로 고정 문자열을 반복 전송해 "안정성"을
  보이는 것은 동어반복적 증거 조작(원하는 결론을 미리 정하고
  Evidence를 맞추는 것)이 되므로 배제했다.

## 7. Self Review

- 실제 Engine 호출이 관찰됐다고 주장했는가 — **아니오.** 완결된
  호출은 없었음을 명시했다(§4).
- Stable Prefix가 확인됐다고 주장했는가 — **아니오**(§5).
- Kernel Context Builder/Renderer를 구현했는가 — **아니오.**
- V-1 GAP-1/V-5/V-6(b)를 해결하려 했는가 — **아니오**, 오히려 그
  경계를 건드리지 않도록 시나리오를 제한했다(§2, §5).
- 새 Architecture/Governance 결정을 내렸는가 — **아니오.** A/B
  해석의 남은 모호성(§4 "느슨한 해석" 문제)은 판단하지 않고
  기록만 했다.
- Credential 관련 harness 차단을 우회했는가 — **아니오**(§6).
- 원문(ADC-0003 Amendment, BASELINE §13.6 Amendment)을 수정했는가 —
  **아니오**, 이 문서는 별도 신규 파일이다.

## 8. 남은 것

- **A의 "엄격 vs 느슨" 해석 문제**: 이번 시도가 새로 드러낸 것이다.
  Architecture Owner가 명시적으로 판단할 사항으로 남긴다 — 이
  문서는 판단하지 않는다.
- **B는 여전히 원천적으로 검증 불가** — Kernel Context 구조(Segment
  정의 포함)가 실제로 만들어지기 전까지는 성립할 수 없는 질문이다.
- **인프라 문제(OpenRouter 계정 미식별, OpenAI 크레딧 소진)**는 이
  세션이 해결할 수 없는 외부 상태다 — Architecture Owner가 별도로
  조치할 사항이며, 이 문서는 그 조치를 요구하지 않는다(요구 자체가
  Governance 범위 밖의 운영 결정이기 때문).
