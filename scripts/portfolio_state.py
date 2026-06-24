"""Real-portfolio state + rebalance calculator (single-user, pillar-1 dividend).

This module is the backend brain for the "real portfolio" redesign:

    Phase 1 — data accessor    : load_portfolio / save_portfolio
    Phase 2 — price + state     : read_price / build_state
    Phase 3 — top-up calculator : rebalance_topup  (pure, "pull back to target")

Single source of truth = ``data/portfolio.json`` (NOT per-user — this is one
real portfolio, the one Art actually holds). Targets, holdings (shares +
avg_cost), free cash, off-plan positions (LH watch / TISCO hold), LH trigger
zones, and per-symbol meta (Thai name/sector/group/thesis/metrics) all live in
that single file.

Public API:
    PORTFOLIO_FILE              — Path to data/portfolio.json
    load_portfolio()            — read the file (returns dict)
    save_portfolio(data)        — atomic write + stamp updated_at
    read_price(sym)             — latest cached price (float) or None
    build_state()               — holdings + prices merged into a render-ready dict
    rebalance_topup(state, new) — pure "pull back to target" calculator

Used by:
    server.app — /api/portfolio/* endpoints
"""
from __future__ import annotations

import json
import math
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"  # legacy single-portfolio (pre multi-portfolio)
PORTFOLIOS_DIR = DATA_DIR / "portfolios"
PRICE_CACHE_DIR = DATA_DIR / "price_cache"

# Multi-portfolio: 3 fixed tabs. Each portfolio lives in data/portfolios/{id}.json.
VALID_PF = ("A", "B", "C")


def _portfolio_path(portfolio_id: str = "A") -> Path:
    """Resolve data/portfolios/{id}.json, validating the id (A/B/C only)."""
    if portfolio_id not in VALID_PF:
        raise ValueError(
            f"invalid portfolio id: {portfolio_id!r} (expected one of {VALID_PF})"
        )
    return PORTFOLIOS_DIR / f"{portfolio_id}.json"

# The 7 in-plan symbols are derived from holdings; cash is a virtual slot in
# targets. off_plan (LH/TISCO) is tracked but excluded from rebalance math.


# ---------------------------------------------------------------------------
# Phase 1 — data accessor
# ---------------------------------------------------------------------------
def load_portfolio(portfolio_id: str = "A") -> dict:
    """Read ``data/portfolios/{id}.json`` and return it as a dict.

    Legacy fallback: if portfolio A's file is missing but the old single
    ``data/portfolio.json`` still exists (pre-migration deploy), read that — so
    a server restart before the migration runs cannot break the live portfolio.

    Raises FileNotFoundError if the file is missing (the file is the single
    source of truth and must exist — we do NOT synthesize fake holdings).
    """
    path = _portfolio_path(portfolio_id)
    if not path.exists() and portfolio_id == "A" and PORTFOLIO_FILE.exists():
        path = PORTFOLIO_FILE
    if not path.exists():
        raise FileNotFoundError(f"portfolio file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} did not contain a JSON object")
    return data


def save_portfolio(data: dict, portfolio_id: str = "A") -> dict:
    """Write the portfolio back atomically, stamping ``updated_at``.

    Returns the payload that was written (with the fresh timestamp). Uses a
    temp-file + os.replace for an atomic swap so a crash mid-write cannot
    truncate the source of truth (same guard intent as user_data_io).
    """
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")
    path = _portfolio_path(portfolio_id)
    payload = dict(data)  # shallow copy so caller's dict is untouched
    payload["updated_at"] = datetime.now().isoformat()

    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), prefix=".portfolio_", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp_path, path)
    except Exception:
        # Clean up the temp file on any failure so we don't litter the dir.
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise
    return payload


# ---------------------------------------------------------------------------
# Phase 2 — price reader + state builder
# ---------------------------------------------------------------------------
def read_price(sym: str) -> Optional[float]:
    """Return the latest cached price for ``sym`` as a float, or None.

    The daily refresh writes ``data/price_cache/{SYM}.BK.json`` with a ``price``
    field. We accept a bare symbol (e.g. "AMATA") or one with ".BK" and try the
    ".BK.json" file first (real layout), then a plain "{SYM}.json" fallback.

    We deliberately do NOT use ``_resolve_price_as_of`` from app.py — that one
    returns a *date* string, not the price.
    """
    if not sym or not isinstance(sym, str):
        return None
    base = sym.strip().upper()
    if base.endswith(".BK"):
        base = base[:-3]
    candidates = [
        PRICE_CACHE_DIR / f"{base}.BK.json",
        PRICE_CACHE_DIR / f"{base}.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        price = cached.get("price")
        if isinstance(price, (int, float)):
            return float(price)
    return None


def _round2(x: float) -> float:
    return round(float(x), 2)


def _price_cache_as_of() -> Optional[str]:
    """ISO timestamp of the newest file in data/price_cache, or None if empty.

    Reflects when prices were last refreshed (the daily job / manual trigger
    rewrites every cache file in one pass), shown next to the refresh button.
    """
    if not PRICE_CACHE_DIR.exists():
        return None
    mtimes = [p.stat().st_mtime for p in PRICE_CACHE_DIR.glob("*.json")]
    if not mtimes:
        return None
    return datetime.fromtimestamp(max(mtimes)).isoformat(timespec="seconds")


def build_state(portfolio_id: str = "A") -> dict:
    """Merge holdings + live prices + targets into a render-ready dict.

    Returns a dict shaped for the frontend cards:
        {
          "positions": [ {sym, name, sector, group, thesis, metrics,
                          price, shares, avg_cost, current_value, pct,
                          target_pct, status, diff_pct, missing_price}, ... ],
          "off_plan":  [ {sym, mode, shares, avg_cost, price,
                          current_value, pl_pct, missing_price}, ... ],
          "cash":      <float>,
          "cash_pct":  <float>,
          "cash_target_pct": <float>,
          "total_value": <float>,
          "summary":   {count_total, count_on_target, count_over,
                        count_deficit, missing_prices: [...]},
          "lh_triggers": {...},
          "updated_at": <str|None>,
        }

    status ∈ {"ok","over","deficit"} per symbol (vs target, ±0.5pct dead-band).
    """
    p = load_portfolio(portfolio_id)
    targets: dict = p.get("targets", {}) or {}
    holdings: dict = p.get("holdings", {}) or {}
    meta: dict = p.get("meta", {}) or {}
    cash = float(p.get("cash", 0) or 0)

    # in-plan symbols = keys of holdings (cash handled separately)
    plan_syms = list(holdings.keys())

    current_value: dict[str, float] = {}
    missing_prices: list[str] = []
    for sym in plan_syms:
        h = holdings.get(sym, {}) or {}
        shares = float(h.get("shares", 0) or 0)
        price = read_price(sym)
        if price is None:
            missing_prices.append(sym)
            cv = 0.0
        else:
            cv = shares * price
        current_value[sym] = cv

    total_value = sum(current_value.values()) + cash

    positions = []
    count_on_target = count_over = count_deficit = 0
    DEAD_BAND = 0.5  # pct points — within this of target counts as "ok"

    for sym in plan_syms:
        h = holdings.get(sym, {}) or {}
        m = meta.get(sym, {}) or {}
        shares = float(h.get("shares", 0) or 0)
        avg_cost = float(h.get("avg_cost", 0) or 0)
        price = read_price(sym)
        cv = current_value[sym]
        pct = (cv / total_value * 100) if total_value > 0 else 0.0
        target_pct = float(targets.get(sym, 0) or 0)
        diff = pct - target_pct
        if diff < -DEAD_BAND:
            status = "deficit"
            count_deficit += 1
        elif diff > DEAD_BAND:
            status = "over"
            count_over += 1
        else:
            status = "ok"
            count_on_target += 1

        positions.append({
            "sym": sym,
            "name": m.get("name"),
            "sector": m.get("sector"),
            "group": m.get("group"),
            "thesis": m.get("thesis"),
            "metrics": {
                "yield": m.get("yield"),
                "pe": m.get("pe"),
                "pbv": m.get("pbv"),
                "roe": m.get("roe"),
                "payout": m.get("payout"),
                "streak": m.get("streak"),
            },
            "price": price,
            "shares": shares,
            "avg_cost": avg_cost,
            "current_value": _round2(cv),
            "pct": _round2(pct),
            "target_pct": target_pct,
            "status": status,
            "diff_pct": _round2(diff),
            "missing_price": price is None,
        })

    # off-plan positions (LH watch / TISCO hold) — tracked, not rebalanced
    off_plan_out = []
    off_plan: dict = p.get("off_plan", {}) or {}
    for sym, info in off_plan.items():
        info = info or {}
        shares = float(info.get("shares", 0) or 0)
        avg_cost = float(info.get("avg_cost", 0) or 0)
        price = read_price(sym)
        cv = (shares * price) if price is not None else 0.0
        pl_pct = None
        if price is not None and avg_cost > 0:
            pl_pct = _round2((price - avg_cost) / avg_cost * 100)
        off_plan_out.append({
            "sym": sym,
            "mode": info.get("mode"),
            "shares": shares,
            "avg_cost": avg_cost,
            "price": price,
            "current_value": _round2(cv),
            "pl_pct": pl_pct,
            "missing_price": price is None,
        })

    cash_target_pct = float(targets.get("cash", 0) or 0)
    cash_pct = (cash / total_value * 100) if total_value > 0 else 0.0

    return {
        "positions": positions,
        "off_plan": off_plan_out,
        "cash": _round2(cash),
        "cash_pct": _round2(cash_pct),
        "cash_target_pct": cash_target_pct,
        "total_value": _round2(total_value),
        "summary": {
            "count_total": len(plan_syms),
            "count_on_target": count_on_target,
            "count_over": count_over,
            "count_deficit": count_deficit,
            "missing_prices": missing_prices,
        },
        "lh_triggers": p.get("lh_triggers", {}),
        "updated_at": p.get("updated_at"),
        "name": p.get("name"),
        "price_as_of": _price_cache_as_of(),
    }


# ---------------------------------------------------------------------------
# Phase 3 — "pull back to target" top-up calculator
# ---------------------------------------------------------------------------
def rebalance_topup(state: dict, new_money: float, portfolio_id: str = "A") -> list[dict]:
    """Pure calculator: where should fresh money go to pull the portfolio
    back toward its target weights (without selling overweight names)?

    Logic (cash counted as one slot in targets):
        base_new   = sum(current_value of 7) + cash + new_money
        target_val = base_new * target_pct/100   for each slot (incl cash)
        deficit    = max(0, target_val - current_value)
        total_def  = sum(deficit)

        if new_money <= total_def:
            topup = new_money * deficit/total_def
        elif new_money > total_def:
            topup = deficit + (new_money - total_def) * target_pct/sum(targets)
        if total_def == 0 (all over/on-target):
            topup = new_money * target_pct/sum(targets)

        shares_to_buy = floor(topup / price)   (cash slot has no shares)

    Returns a list of dicts (one per slot incl cash):
        {sym, status, deficit_pct, price, shares_to_buy, baht}

    Guarantee: sum(baht) == new_money exactly (no rounding leak — the largest
    remainder is absorbed into the final slot so totals reconcile to the cent).
    """
    new_money = float(new_money)
    if new_money < 0:
        raise ValueError("new_money must be >= 0")

    p = load_portfolio(portfolio_id)
    targets: dict = p.get("targets", {}) or {}

    # Build current_value per slot from the passed-in state (7 syms) + cash.
    cv: dict[str, float] = {}
    price_map: dict[str, Optional[float]] = {}
    for pos in state.get("positions", []):
        sym = pos["sym"]
        cv[sym] = float(pos.get("current_value", 0) or 0)
        price_map[sym] = pos.get("price")
    cash_now = float(state.get("cash", 0) or 0)
    cv["cash"] = cash_now
    price_map["cash"] = None

    # Slots = every key in targets (the 7 syms + "cash"). Restrict cv to those.
    slots = list(targets.keys())
    target_sum = sum(float(targets.get(s, 0) or 0) for s in slots)
    if target_sum <= 0:
        raise ValueError("targets sum to 0 — cannot rebalance")

    base_existing = sum(cv.get(s, 0.0) for s in slots)
    base_new = base_existing + new_money

    deficit: dict[str, float] = {}
    for s in slots:
        tval = base_new * float(targets.get(s, 0) or 0) / 100.0
        deficit[s] = max(0.0, tval - cv.get(s, 0.0))
    total_def = sum(deficit.values())

    topup: dict[str, float] = {}
    if total_def <= 1e-9:
        # Everyone is at/over target — spread purely by target weight.
        for s in slots:
            topup[s] = new_money * float(targets.get(s, 0) or 0) / target_sum
    elif new_money <= total_def:
        # Not enough to fill all gaps — share proportional to the gaps.
        for s in slots:
            topup[s] = new_money * deficit[s] / total_def
    else:
        # Fill every gap, then spread the surplus by target weight.
        surplus = new_money - total_def
        for s in slots:
            topup[s] = deficit[s] + surplus * float(targets.get(s, 0) or 0) / target_sum

    # ---- reconcile baht so sum(baht) == new_money exactly --------------------
    # Round each slot to 2dp, then push the residual into the slot that
    # received the most (largest-remainder style) so totals match to the cent.
    baht: dict[str, float] = {s: _round2(topup.get(s, 0.0)) for s in slots}
    residual = _round2(new_money - sum(baht.values()))
    if abs(residual) >= 0.01:
        # absorb residual into the slot with the largest top-up
        biggest = max(slots, key=lambda s: topup.get(s, 0.0))
        baht[biggest] = _round2(baht[biggest] + residual)

    out = []
    for s in slots:
        is_cash = (s == "cash")
        price = price_map.get(s)
        shares_to_buy = None
        if not is_cash:
            if price and price > 0:
                shares_to_buy = int(math.floor(baht[s] / price))
            else:
                shares_to_buy = 0  # no price -> can't size shares
        # status vs target (deficit if it had a gap, else over/ok)
        if deficit.get(s, 0.0) > 1e-9:
            status = "under"
        else:
            # distinguish over vs on-target using current pct vs target
            cur_pct = (cv.get(s, 0.0) / base_existing * 100) if base_existing > 0 else 0.0
            tgt = float(targets.get(s, 0) or 0)
            status = "over" if cur_pct > tgt + 0.5 else "ok"
        out.append({
            "sym": s,
            "status": status,
            "deficit_pct": _round2(
                (deficit.get(s, 0.0) / new_money * 100) if new_money > 0 else 0.0
            ),
            "price": price,
            "shares_to_buy": shares_to_buy,
            "baht": baht[s],
        })
    return out


# ---------------------------------------------------------------------------
# Smoke test — run `python scripts/portfolio_state.py`
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("portfolio file:", PORTFOLIO_FILE, "exists:", PORTFOLIO_FILE.exists())
    pf = load_portfolio()
    print("targets sum:", sum(pf["targets"].values()))
    st = build_state()
    print("total_value:", st["total_value"], "summary:", st["summary"])
