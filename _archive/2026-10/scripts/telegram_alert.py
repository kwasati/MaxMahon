"""Telegram alert for high-severity exit triggers.

Uses TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID from root .env (C:/WORKSPACE/.env line 72-73).
Error-safe: fail silently + log, never crash caller.
"""
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path("C:/WORKSPACE/.env"))

_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_alert(message: str) -> bool:
    """Generic Telegram alert wrapper — sends a single text message.

    Returns True if sent successfully, False on failure (does not raise).
    Used by filter-07 for STALE flake alerts + future ad-hoc notifications.
    Safe to call when env vars missing or message empty (returns False, no send).
    """
    if not _TOKEN or not _CHAT_ID or not message:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{_TOKEN}/sendMessage",
            json={"chat_id": _CHAT_ID, "text": message},
            timeout=10,
        )
        return r.ok
    except Exception as e:
        print(f"telegram alert failed: {e}")
        return False


def send_exit_alert(high_triggers: list[dict]) -> bool:
    """Send one Telegram message summarizing N high-severity exit triggers.

    Each trigger dict should have: symbol, type, reason, severity.
    Returns True on success, False on any failure.
    Safe to call with empty list (returns False, no send).
    """
    if not _TOKEN or not _CHAT_ID or not high_triggers:
        return False
    lines = [f"⚠ Max Mahon Exit Alert ({len(high_triggers)} high severity)", ""]
    for t in high_triggers[:15]:  # cap to avoid Telegram 4096 char limit
        sym = t.get("symbol", "?")
        typ = t.get("type", "?")
        reason = (t.get("reason", "?") or "?")[:120]
        lines.append(f"• {sym} ({typ}): {reason}")
    msg = "\n".join(lines)
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{_TOKEN}/sendMessage",
            json={"chat_id": _CHAT_ID, "text": msg},
            timeout=10,
        )
        return r.ok
    except Exception as e:
        print(f"telegram alert failed: {e}")
        return False
