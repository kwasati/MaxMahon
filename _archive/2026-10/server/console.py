"""Max Mahon — Real-time console status panel.

Uses ANSI cursor-home to redraw in-place without clearing screen.
No flickering, no selection loss.
"""

import json
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

_first_render = True


# ANSI colors
class C:
    reset = "\x1b[0m"
    dim = "\x1b[2m"
    bold = "\x1b[1m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    cyan = "\x1b[36m"
    white = "\x1b[37m"


def _uptime_str(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


def _ts() -> str:
    now = datetime.now()
    return now.strftime("%H:%M:%S")


def _age_days(date_str: str):
    """Return whole days between date_str (YYYY-MM-DD) and now, or None if unparseable."""
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return (datetime.now() - d).days
    except (ValueError, TypeError):
        return None


def _fresh_color(days, warn: int, bad: int) -> str:
    """Green if fresh (<=warn days), yellow if aging (<=bad), red if stale."""
    if days is None:
        return C.white
    if days <= warn:
        return C.green
    if days <= bad:
        return C.yellow
    return C.red


def _age_str(days) -> str:
    if days is None:
        return ""
    if days <= 0:
        return f" {C.dim}(today){C.reset}"
    if days == 1:
        return f" {C.dim}(1d ago){C.reset}"
    return f" {C.dim}({days}d ago){C.reset}"


def _data_row(label: str, date_str: str, warn: int, bad: int, suffix: str, clr: str) -> str:
    """Render one Data-section row with freshness color + age annotation."""
    days = _age_days(date_str)
    col = _fresh_color(days, warn, bad)
    return f"    {label}  {col}{date_str}{C.reset}{_age_str(days)}{suffix}{clr}"


def _latest_price_info(data_dir: Path):
    """Return (price_date, sym_count, refreshed_at) from data/price_cache/.

    price_date = EOD date of the data (from fetched_at); refreshed_at = file mtime
    of the newest cache file (when the cron actually wrote it).
    """
    price_dir = data_dir / "price_cache"
    if not price_dir.exists():
        return "-", 0, ""
    files = list(price_dir.glob("*.json"))
    if not files:
        return "-", 0, ""
    latest = max(files, key=lambda p: p.stat().st_mtime)
    price_date = "-"
    try:
        d = json.loads(latest.read_text(encoding="utf-8"))
        price_date = str(d.get("fetched_at", ""))[:10] or "-"
    except (json.JSONDecodeError, OSError):
        pass
    if price_date == "-":
        price_date = datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d")
    refreshed = datetime.fromtimestamp(latest.stat().st_mtime).strftime("%m-%d %H:%M")
    return price_date, len(files), refreshed


# Request counter (thread-safe)
_request_count = 0
_request_lock = threading.Lock()
_last_requests: list[str] = []  # last 5 requests for display


def count_request(method: str, path: str, status_code: int):
    global _request_count
    with _request_lock:
        _request_count += 1
        entry = f"{C.dim}{_ts()}{C.reset} {method} {path} "
        if status_code < 400:
            entry += f"{C.green}{status_code}{C.reset}"
        else:
            entry += f"{C.red}{status_code}{C.reset}"
        _last_requests.append(entry)
        if len(_last_requests) > 5:
            _last_requests.pop(0)


def render(
    port: int,
    pid: int,
    start_time: float,
    pipeline_state: dict,
    data_dir: Path,
    url: str = "https://max.intensivetrader.com",
):
    """Render the status panel in-place (no flicker)."""
    global _first_render
    if _first_render:
        os.system("cls" if os.name == "nt" else "clear")
        _first_render = False

    uptime = time.time() - start_time

    # Current system: daily price cache (v6.7.0+).
    price_date, price_count, price_refreshed = _latest_price_info(data_dir)

    with _request_lock:
        req_count = _request_count
        recent = list(_last_requests)

    clr = "\x1b[K"

    price_suffix = f"  {C.dim}{price_count} syms{C.reset}"

    lines = [
        f"{clr}",
        f"  {C.cyan}●{C.reset} {C.bold}Max Mahon Server{C.reset}{clr}",
        f"{C.dim}    Port: {port} · PID: {pid} · Uptime: {_uptime_str(uptime)}{C.reset}{clr}",
        f"{C.dim}    URL:  {url}{C.reset}{clr}",
        f"{clr}",
        f"  {C.bold}Data{C.reset}{clr}",
        _data_row("Prices:", price_date, 3, 7, price_suffix, clr),
    ]
    if price_refreshed:
        lines.append(f"    {C.dim}last refresh: {price_refreshed}{C.reset}{clr}")
    lines += [
        f"{clr}",
        f"  {C.bold}Scheduler{C.reset}{clr}",
        f"    {C.dim}Price refresh:{C.reset}  daily 19:00 Asia/Bangkok{clr}",
        f"{clr}",
        f"  {C.bold}Requests{C.reset}  {C.dim}({req_count} total){C.reset}{clr}",
    ]
    if recent:
        for r in recent:
            lines.append(f"    {r}{clr}")
    else:
        lines.append(f"    {C.dim}No requests yet{C.reset}{clr}")
    lines.append(f"{clr}")
    lines.append(f"{C.dim}  Ctrl+C to stop{C.reset}{clr}")
    lines.append(f"{clr}")

    sys.stdout.write("\x1b[H" + "\n".join(lines))
    sys.stdout.flush()


def start_refresh_loop(
    port: int,
    pid: int,
    start_time: float,
    pipeline_state: dict,
    data_dir: Path,
    url: str = "https://max.intensivetrader.com",
    interval: float = 2.0,
):
    """Start background thread that refreshes console every N seconds."""

    def _loop():
        while True:
            try:
                render(port, pid, start_time, pipeline_state, data_dir, url)
            except Exception:
                pass
            time.sleep(interval)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t
