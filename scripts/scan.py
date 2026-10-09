"""Max Mahon v5 — Scan report: gate result (who passed, which path, which flags) -> report + history."""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
HISTORY_FILE = DATA_DIR / "history.json"

sys.path.insert(0, str(ROOT / "scripts"))

load_dotenv(Path("C:/WORKSPACE/.env"))


_SCREENER_DATE_PATTERN = re.compile(r"^screener_\d{4}-\d{2}-\d{2}\.json$")


def get_latest_screener() -> Path:
    files = sorted(
        [f for f in DATA_DIR.glob("screener_*.json") if _SCREENER_DATE_PATTERN.match(f.name)],
        reverse=True,
    )
    if not files:
        print("No screener data found. Run screen_stocks.py first.")
        sys.exit(1)
    return files[0]


def load_history() -> dict:
    if not HISTORY_FILE.exists():
        return {"scans": []}
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "scans" not in data:
            return {"scans": []}
        return data
    except Exception:
        return {"scans": []}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Max Mahon scan report")
    ap.add_argument("--screener", help="screener json to report on (default: latest in data/)")
    ap.add_argument("--out-dir", help="write the report here; reports/ and data/history.json are left untouched")
    args = ap.parse_args(argv)
    out_dir = Path(args.out_dir) if args.out_dir else None

    screener_path = Path(args.screener) if args.screener else get_latest_screener()
    print(f"Using screener: {screener_path.name}")

    screener_data = json.loads(screener_path.read_text(encoding="utf-8"))

    history = load_history()
    scanned_at = datetime.now()
    today = scanned_at.strftime("%Y-%m-%d")

    from report_template import generate_report_md
    from history_manager import build_v2_entry, upsert_scan_v2, iso_week_key

    # previous scan (history is read-only unless this is a full run)
    scans_list = history.get("scans") or []
    prev_scan = scans_list[-1] if scans_list else None

    iso_week = iso_week_key(scanned_at.date())
    report_dir = out_dir or REPORTS_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"scan_{today}.md"
    report_md = generate_report_md(screener_data, iso_week, scanned_at, prev_scan)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"report written: {report_path}")

    if out_dir is None:
        history_entry = build_v2_entry(screener_data, scanned_at, report_path.name)
        upsert_scan_v2(history_entry, history)  # pass loaded history dict to avoid re-read
        print(f"history upserted: iso_week={iso_week} scanned_at={scanned_at.isoformat(timespec='seconds')}")
    else:
        print("history not touched (--out-dir)")


if __name__ == "__main__":
    main()
