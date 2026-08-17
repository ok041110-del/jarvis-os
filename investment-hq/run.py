"""Investment HQ 최소 E2E 진입점 — HQ에서 Team을 선택하고 실제 분석을
실행한다. `TEAMS`는 리터럴 딕셔너리다(Registry가 아니다 — 동적 등록
API나 조회 인터페이스를 제공하지 않는다. `development-hq/mvp/agents.py`
류의 Capability Map과 동일한 성격). Team이 늘어나면 이 딕셔너리에 한
줄을 더할 뿐, 일반화된 조회 로직을 만들지 않는다.

사용법:
    python3 investment-hq/run.py <team> <company_label> <raw_data_path> <issue_dir>

    team: stock | etf | dividend_stock
    company_label: Final Report에 쓰일 회사/펀드 표기(예: "Enterprise
        Products Partners L.P. (NYSE: EPD)")
    raw_data_path: raw_data.md 경로
    issue_dir: 결과를 쓸 디렉터리(Checkpointing이 여기 checkpoints/를 만든다)

`development-hq/`는 이 파일에서도 한 줄도 수정하지 않는다. 기존
project-local Dogfooding(AAPL~CAT, QQQ~UUP, JNJ~EPD)은 이 파일이
존재하기 전에 완료됐으므로 소급 수정하지 않는다 — 이 진입점은
신규 실행부터 적용된다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "teams"))

import stock_team  # noqa: E402
import etf_team  # noqa: E402
import dividend_stock_team  # noqa: E402

TEAMS = {
    "stock": stock_team,
    "etf": etf_team,
    "dividend_stock": dividend_stock_team,
}


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    team_key, company_label, raw_data_path, issue_dir = sys.argv[1:5]
    if team_key not in TEAMS:
        print(f"Unknown team '{team_key}'. Choices: {list(TEAMS)}")
        sys.exit(1)

    team = TEAMS[team_key]
    issue_dir_path = Path(issue_dir)
    issue_dir_path.mkdir(parents=True, exist_ok=True)
    result = team.run(company_label, Path(raw_data_path), issue_dir_path)

    import json
    summary = {"team": team_key, "company_label": company_label, **result["wave_summary"]}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Done. Output written to {issue_dir_path}")


if __name__ == "__main__":
    main()
