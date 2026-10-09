"""History manager for Max Mahon scan archive.

v3 entry (gate only, no scores): date, counts by gate path, passed[] = {symbol, gate_path},
gate_version, report name. Older entries (v1/v2, with score / top_candidates) stay in the file
untouched; passed_of() reads both shapes.
"""
import json
from pathlib import Path
from datetime import datetime, date

_HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "history.json"


def load_history() -> dict:
    """Return history dict. If file missing/unreadable, return {'scans': []}."""
    if not _HISTORY_PATH.exists():
        return {"scans": []}
    try:
        return json.loads(_HISTORY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"scans": []}


def iso_week_key(d: date) -> str:
    """Return ISO week key like '2026-W17' (Mon-Sun, ISO 8601)."""
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def build_v2_entry(screener_data: dict, scanned_at: datetime, report_filename: str) -> dict:
    """Build a history entry from screener output (name kept for scan.py). No score fields."""
    cands = screener_data.get("candidates", [])
    counts = screener_data.get("counts") or {}
    n_main = sum(1 for c in cands if c.get("gate_path") == "main")
    return {
        "iso_week": iso_week_key(scanned_at.date()),
        "scanned_at": scanned_at.isoformat(timespec="seconds"),
        "date": scanned_at.strftime("%Y-%m-%d"),
        "gate_version": screener_data.get("gate_version"),
        "counts": {
            "scanned": screener_data.get("total_scanned", 0),
            "passed": len(cands),
            "passed_main": n_main,
            "passed_growth": len(cands) - n_main,
            "filtered": screener_data.get("filtered_out", counts.get("filtered_out", 0)),
            "pending": screener_data.get("pending_count", counts.get("pending", 0)),
        },
        "passed": [{"symbol": c["symbol"], "gate_path": c.get("gate_path")} for c in cands],
        "report": report_filename,
    }


def passed_of(scan: dict | None) -> dict:
    """{symbol: gate_path or None} of one history entry; reads the new shape and the old (top_candidates) shape."""
    if not isinstance(scan, dict):
        return {}
    if isinstance(scan.get("passed"), list):
        return {p["symbol"]: p.get("gate_path") for p in scan["passed"] if isinstance(p, dict) and p.get("symbol")}
    return {c["symbol"]: None for c in (scan.get("top_candidates") or []) if isinstance(c, dict) and c.get("symbol")}


def upsert_scan_v2(entry: dict, history: dict | None = None) -> dict:
    """Replace entry of same iso_week, or append if new week. Atomic write."""
    hist = history or load_history()
    iso_wk = entry["iso_week"]
    scans = [s for s in hist.get("scans", []) if s.get("iso_week") != iso_wk]
    scans.append(entry)
    hist["scans"] = scans
    _HISTORY_PATH.write_text(
        json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return hist
