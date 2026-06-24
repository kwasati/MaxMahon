# -*- coding: utf-8 -*-
"""One-shot migration: single ``data/portfolio.json`` -> ``data/portfolios/{A,B,C}.json``.

Multi-portfolio redesign — 3 fixed tabs (A/B/C), each its own file.

  A = the existing portfolio (copied from data/portfolio.json, name "พอร์ตหลัก")
  B = seed: same targets+meta as A, but empty holdings/cash (name "พอร์ต 2")
  C = seed: same as B (name "พอร์ต 3")

Design choices (matches build plan multi-portfolio-01-backend):
  - COPY, not move — the legacy ``data/portfolio.json`` is left in place so a
    still-running old server (which reads it) does not break mid-migration.
    Archive it manually later, after the new code is confirmed live.
  - Idempotent — any portfolios/{id}.json that already exists is left untouched
    (re-running never overwrites real data).

Run:  py scripts/migrate_portfolio_to_separate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
LEGACY_FILE = DATA_DIR / "portfolio.json"
PORTFOLIOS_DIR = DATA_DIR / "portfolios"

PF_NAMES = {"A": "พอร์ตหลัก", "B": "พอร์ต 2", "C": "พอร์ต 3"}


def _write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def migrate() -> int:
    if not LEGACY_FILE.exists() and not (PORTFOLIOS_DIR / "A.json").exists():
        print(f"[migrate] ERROR: no source — neither {LEGACY_FILE} nor portfolios/A.json exists",
              file=sys.stderr)
        return 2

    PORTFOLIOS_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Portfolio A: copy legacy file (if A.json not already present) -------
    a_path = PORTFOLIOS_DIR / "A.json"
    if a_path.exists():
        print(f"[migrate] A.json already exists — skip")
        a_data = json.loads(a_path.read_text(encoding="utf-8"))
    else:
        try:
            a_data = json.loads(LEGACY_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"[migrate] ERROR: cannot read/parse {LEGACY_FILE}: {e}", file=sys.stderr)
            return 2
        if not isinstance(a_data, dict):
            print("[migrate] ERROR: legacy portfolio.json is not a JSON object", file=sys.stderr)
            return 2
        a_data.setdefault("name", PF_NAMES["A"])
        _write_json(a_path, a_data)
        print(f"[migrate] wrote A.json (name={a_data.get('name')}, "
              f"holdings={len(a_data.get('holdings', {}))})")

    # ---- Portfolios B, C: seed from A's targets+meta, empty positions --------
    for pid in ("B", "C"):
        p_path = PORTFOLIOS_DIR / f"{pid}.json"
        if p_path.exists():
            print(f"[migrate] {pid}.json already exists — skip")
            continue
        # Same structure as A (same symbols, same target weights) but every
        # position zeroed — so the table shows all rows ready to fill in.
        seed_holdings = {
            sym: {"shares": 0, "avg_cost": 0}
            for sym in (a_data.get("holdings", {}) or {})
        }
        seed_offplan = {
            sym: {"shares": 0, "avg_cost": 0, "mode": (info or {}).get("mode", "hold")}
            for sym, info in (a_data.get("off_plan", {}) or {}).items()
        }
        seed = {
            "name": PF_NAMES[pid],
            "targets": dict(a_data.get("targets", {}) or {}),
            "holdings": seed_holdings,
            "cash": 0,
            "off_plan": seed_offplan,
            "lh_triggers": dict(a_data.get("lh_triggers", {}) or {}),
            "meta": dict(a_data.get("meta", {}) or {}),
        }
        _write_json(p_path, seed)
        print(f"[migrate] seeded {pid}.json (name={seed['name']}, "
              f"targets={len(seed['targets'])}, holdings={len(seed_holdings)} zeroed)")

    print("[migrate] done. NOTE: legacy data/portfolio.json kept in place "
          "(archive manually after confirming new code is live).")
    return 0


if __name__ == "__main__":
    raise SystemExit(migrate())
