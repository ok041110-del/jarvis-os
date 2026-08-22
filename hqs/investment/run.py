"""Investment HQ 최소 E2E 진입점. `TEAMS`는 리터럴 딕셔너리다(Registry
아님, Team 추가 시 한 줄만 추가). `hqs/development/`는 수정하지 않는다.

사용법:
    python3 hqs/investment/run.py <team> <company_label> <raw_data_path> <issue_dir>

    team: stock | etf | dividend_stock
    company_label: Final Report에 쓰일 회사/펀드 표기
    raw_data_path: raw_data.md 경로
    issue_dir: 결과를 쓸 디렉터리
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
