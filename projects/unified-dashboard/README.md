# Unified Dashboard — Experimental Prototype

**성격**: `docs/00_governance/ARCHITECTURE_GOVERNANCE.md`의
"Experimental Implementation" 절이 허용하는 격리 Prototype. Formal
Architecture Decision이 아니다. Production `dashboard/`(Structure
v1.0 Frozen 위치)에 구현하지 않는다.

**목적**: Dev HQ / Investment HQ의 실제 상태를 하나의 화면에서
관찰하면서, 향후 Dashboard Architecture에 필요한 Evidence를
생성한다. Production Dashboard를 완성하는 것이 목적이 아니다.

## 실행

```
python3 projects/unified-dashboard/generate_dashboard.py
```

`projects/unified-dashboard/output/dashboard.html`을 생성한다.

## 테스트

```
python3 -m pytest projects/unified-dashboard/tests/ -q
```

## 구조

| 파일 | 책임 |
|---|---|
| `snapshot.py` | Data Acquisition — 기존 Evidence 파일(Freeze 문서, `checkpoints/manifest.json`, `trader_decision.md`)만 읽는다. `hqs/*` Python 모듈을 import하지 않는다(Boundary 검증 대상) |
| `render.py` | Global Shell 렌더링 — HQ Card의 `detail` 문자열을 그대로 표시할 뿐 HQ 의미를 해석하지 않는다 |
| `generate_dashboard.py` | CLI 진입점 |
| `tests/test_snapshot.py` | Functional + Boundary Validation(AST 기반 import 검사 포함) |

## Boundary

- Engine/Agent를 직접 호출하지 않는다.
- `hqs/development`, `hqs/investment`의 Python 코드를 import하지
  않는다 — Markdown/JSON Evidence 파일만 읽는다.
- Portfolio/Risk/Execution(Investment HQ Freeze 범위 밖)은 Production
  기능처럼 표시하지 않고 `Deferred` 항목으로 명시적으로 분리한다.
- `HQSnapshot`은 Experimental Prototype Contract다 — Production
  Contract로 문서화하지 않는다.

## Evidence

전체 판정과 Evidence는
`docs/research/JARVIS-OS-V2.0-UNIFIED-DASHBOARD-PROTOTYPE-0001.md`
참조.
