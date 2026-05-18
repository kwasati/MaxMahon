"""Yahoo flake retry queue — file-based JSON queue.

Schema:
  {
    "version": 1,
    "queue": [
      {
        "symbol": "BBL",
        "first_flaked_at": "2026-05-12T10:00:00",
        "last_retry_at": "2026-05-12T19:00:00",
        "retry_count": 1,
        "reasons": ["ไม่มีข้อมูลปันผลย้อนหลัง (yahoo flake)"],
        "scan_date": "2026-05-12",
        "stale": false
      }
    ]
  }
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_FILE = ROOT / "data" / "flake_queue.json"


def _ensure_queue():
    if not QUEUE_FILE.exists():
        QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        QUEUE_FILE.write_text(json.dumps({"version": 1, "queue": []}), encoding="utf-8")


def load_queue() -> dict:
    _ensure_queue()
    return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))


def save_queue(data: dict):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def add_to_queue(symbol: str, reasons: list[str], scan_date: str):
    """Add or update entry in queue. Does NOT bump retry_count (use mark_retry for that)."""
    data = load_queue()
    now = datetime.now().isoformat()
    for e in data["queue"]:
        if e["symbol"] == symbol:
            e["reasons"] = reasons
            e["scan_date"] = scan_date
            save_queue(data)
            return
    data["queue"].append({
        "symbol": symbol,
        "first_flaked_at": now,
        "last_retry_at": None,
        "retry_count": 0,
        "reasons": reasons,
        "scan_date": scan_date,
        "stale": False,
    })
    save_queue(data)


def remove_from_queue(symbol: str):
    data = load_queue()
    data["queue"] = [e for e in data["queue"] if e["symbol"] != symbol]
    save_queue(data)


def mark_retry(symbol: str, success: bool):
    """Update last_retry_at + retry_count for symbol. If success=True, remove from queue."""
    data = load_queue()
    now = datetime.now().isoformat()
    for e in data["queue"]:
        if e["symbol"] == symbol:
            e["last_retry_at"] = now
            e["retry_count"] = e.get("retry_count", 0) + 1
            break
    save_queue(data)
    if success:
        remove_from_queue(symbol)


def list_pending() -> list[str]:
    """Return list of symbols in queue that are not marked stale."""
    return [e["symbol"] for e in load_queue()["queue"] if not e.get("stale")]


def list_stale(days: int = 7) -> list[dict]:
    """Return list of queue entries older than N days (not yet marked stale)."""
    threshold = datetime.now() - timedelta(days=days)
    result = []
    for e in load_queue()["queue"]:
        first = e.get("first_flaked_at")
        if first and datetime.fromisoformat(first) < threshold and not e.get("stale"):
            result.append(e)
    return result


def mark_stale(symbol: str):
    data = load_queue()
    for e in data["queue"]:
        if e["symbol"] == symbol:
            e["stale"] = True
            break
    save_queue(data)
