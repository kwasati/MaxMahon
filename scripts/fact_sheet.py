"""Fact sheet per stock: numbers a person reads before a deep dive. No score, no rank, no buy/sell.

Usage: py scripts\\fact_sheet.py AMATA BBL --cost AMATA=27.5 [--out reports\\facts]

Layout: pure calculators (dict in, dict out, no network) -> compute_fact_sheet()
        -> fetch wrapper build_fact_sheet() -> render_markdown() -> CLI.
Every threshold is read from config.json "fact_sheet" (DEFAULT_CFG is the fallback).
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from data_adapter import complete_dividend_by_year, dividend_crisis_facts  # noqa: E402
from fetch_data import compute_dps_cagr  # noqa: E402

CONFIG_PATH = ROOT / "config.json"
NA = "ไม่มีข้อมูล"
INSUFFICIENT = "ข้อมูลไม่พอ"
SCENARIOS = ("bad", "mid", "good")
SCENARIO_TH = {"bad": "แย่", "mid": "กลาง", "good": "ดี"}

DEFAULT_CFG = {
    "yoc_target_low": 7, "yoc_target_high": 12, "growth_cap": 0.10, "min_scenario_window_years": 10,
    "cost_discounts": [0.8, 0.6], "cagr_windows": [5, 10, 15, 20], "yoc_years": [5, 10, 15],
    "cut_material_pct": 10, "crisis_years": [2008, 2009, 2011, 2020],
    "price_cheap_top_pct": 25, "price_expensive_bottom_pct": 25, "price_min_years": 5,
    "pe_niwes_max": 10, "yield_niwes_min": 5,
    "t1_cut_years": 2, "t4_years": 2, "t6_years": 3, "t2_year": 10,
    "payout_over": 1.0, "loss_window_years": 10, "price_stale_days": 5,
    "dca_years": 10, "dca_report_years": [5, 10, 15], "dca_required_year": 10,
    "max_yahoo_only_share": 0.5, "debt_suspect_ratio": 5,
}


def load_cfg(path=CONFIG_PATH) -> dict:
    cfg = dict(DEFAULT_CFG)
    try:
        cfg.update(json.loads(Path(path).read_text(encoding="utf-8")).get("fact_sheet") or {})
    except (OSError, ValueError):
        pass
    return cfg


def _num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) and v == v else None


# --- A1 / A2 / A3: dividend history, cuts, growth windows ---

def dividend_series(data: dict) -> tuple:
    """(complete {FY: DPS}, incomplete {FY: DPS}) from the merged dividend_history."""
    hist = {int(k): v for k, v in (data.get("dividend_history") or {}).items() if v is not None}
    complete = complete_dividend_by_year(hist, data.get("fy_is_complete"))
    return complete, {y: v for y, v in hist.items() if y not in complete}


def dividend_cuts(complete: dict, material_pct: float) -> list:
    """Every FY whose DPS is below the previous FY (both complete, adjacent).

    recovery_years = years after the cut until a complete FY is back at the pre-cut DPS
    (None = not yet). `material` = cut of at least material_pct %.
    """
    cuts = []
    for fy in sorted(complete):
        prev, cur = complete.get(fy - 1), complete[fy]
        if prev is None or prev <= 0 or cur >= prev * (1 - 1e-9):
            continue
        rec = next((k - fy for k in sorted(complete) if k > fy and complete[k] >= prev), None)
        change = cur / prev - 1
        cuts.append({"fy": fy, "prev": prev, "cur": cur, "change": change,
                     "recovery_years": rec, "material": change <= -material_pct / 100})
    return cuts


def crisis_rows(data: dict, years) -> list:
    facts = dividend_crisis_facts(data.get("dividend_history"), data.get("fy_is_complete"))
    return [{"year": y, "change": facts.get(f"dps_change_{y}"),
             "recovery_years": facts.get(f"dps_recovery_years_{y}")} for y in years]


def cagr_windows(data: dict, windows) -> dict:
    """{years: CAGR or None}: (DPS[L]/DPS[L-n])^(1/n)-1 from the latest complete FY L."""
    return {n: compute_dps_cagr(data.get("dividend_history"), data.get("fy_is_complete"), years=n)
            for n in windows}


# --- A4: scenarios, cost levels, dividend-vs-cost table ---

def growth_scenarios(cagrs: dict, cap: float, min_window: int = 10) -> dict:
    """Fixed rules (our own): needs a window >= min_window years, else every scenario is None (ข้อมูลไม่พอ).
    bad = lowest window CAGR (0..cap) · good = highest window CAGR, capped · mid = mean(bad, good). Always bad <= mid <= good."""
    avail = {n: v for n, v in cagrs.items() if v is not None}
    if not any(n >= min_window for n in avail):
        return {"bad": None, "mid": None, "good": None}
    bad = min(cap, max(0.0, min(avail.values())))
    good = max(bad, min(cap, max(avail.values())))  # all windows negative: good floored at bad (0) to keep the order
    return {"bad": bad, "mid": (bad + good) / 2, "good": good}


def cost_levels(price, supplied: list, discounts) -> list:
    """[{cost, label}] supplied cost(s), today's price, price x each discount. Duplicates dropped."""
    raw = [(c, "ต้นทุนที่ส่งมา") for c in supplied]
    if price:
        raw.append((price, "ราคาวันนี้"))
        raw += [(price * d, f"ราคาวันนี้ x {d:g}") for d in discounts]
    out, seen = [], set()
    for c, label in raw:
        if c and c > 0 and round(c, 2) not in seen:
            seen.add(round(c, 2))
            out.append({"cost": c, "label": label})
    return out


def yoc_table(base_dps, rates: dict, costs: list, years) -> list:
    """Rows scenario x year: DPS in year N and DPS/cost (%) per cost level."""
    rows = []
    for key in SCENARIOS:
        g = rates.get(key)
        for n in years:
            dps_n = base_dps * (1 + g) ** n if (g is not None and base_dps and base_dps > 0) else None
            rows.append({"scenario": key, "rate": g, "year": n, "dps": dps_n,
                         "yoc": [dps_n / c["cost"] * 100 if dps_n is not None else None for c in costs]})
    return rows


def required_growth(base_dps, costs: list, targets, years) -> list:
    """Growth per year needed so that DPS_N / cost reaches each target %: (t% x cost / base)^(1/N)-1."""
    rows = []
    for c in costs:
        for n in years:
            vals = [((t / 100 * c["cost"] / base_dps) ** (1 / n) - 1) if (base_dps and base_dps > 0) else None
                    for t in targets]
            rows.append({"cost": c["cost"], "year": n, "growth": vals})
    return rows


PRICE_GROWS, PRICE_FLAT = "grows", "flat"


def dca_yoc(base_dps, price, g, year: int, buy_years: int, price_mode: str):
    """DCA dividend / money invested (%) in `year`. None (ข้อมูลไม่พอ) when g / base_dps / price is missing.

    Rules (our own, fixed - not a forecast): equal money M every month for `buy_years` years (month k = 0..12*buy_years-1
    at time t_k = k/12 years), then hold. DPS grows g a year from the last full-year dividend: DPS_N = base x (1+g)^N
    (same convention as yoc_table). Shares bought in month k = M / P_k, P_k = buy price of that month:
      grows = P_k = price x (1+g)^t_k  (price grows with dividend -> yield at purchase stays = today's yield)
      flat  = P_k = price              (yield at purchase rises with the dividend)
    Only months before `year` count (year 5 = 60 months bought; year 15 = still 120, buying stopped after year 10).
    Dividend in year N = DPS_N x sum(M / P_k); invested = M x months bought, so M cancels:
      yoc = DPS_N x mean(1 / P_k) x 100.   grows: yoc = today_yield x (1+g)^N x mean((1+g)^-t_k) ; flat: yoc = DPS_N / price."""
    if g is None or not base_dps or base_dps <= 0 or not price or price <= 0:
        return None
    months = 12 * min(year, buy_years)
    if months <= 0:
        return None
    dps_n = base_dps * (1 + g) ** year
    if price_mode == PRICE_FLAT:
        inv = [1 / price] * months
    else:
        inv = [1 / (price * (1 + g) ** (k / 12)) for k in range(months)]
    return dps_n * sum(inv) / months * 100


def dca_required_yield(g, target, year: int):
    """Average yield at purchase (today's DPS / average buy price, %) needed so DPS_N / avg buy price reaches target %:
    DPS_N / avg_cost = target  ->  base / avg_cost = target / (1+g)^N. None when g is missing."""
    return None if g is None else target / (1 + g) ** year


def dca_table(base_dps, price, rates: dict, years, buy_years: int, targets, req_year: int) -> list:
    """Rows per scenario: rate, [{year, grows, flat}], required avg purchase yield for each target in req_year."""
    out = []
    for key in SCENARIOS:
        g = rates.get(key)
        ok = g is not None and base_dps and base_dps > 0 and price and price > 0
        out.append({"scenario": key, "rate": g, "ok": bool(ok),
                    "years": [{"year": n, PRICE_GROWS: dca_yoc(base_dps, price, g, n, buy_years, PRICE_GROWS),
                               PRICE_FLAT: dca_yoc(base_dps, price, g, n, buy_years, PRICE_FLAT)} for n in years],
                    "required": [dca_required_yield(g, t, req_year) if ok else None for t in targets]})
    return out


# --- A5 / A6 / A7 / A12: yearly financials ---

def yearly_rows(data: dict) -> list:
    """One dict per year from yearly_metrics. Missing value -> None (never 0). invest = |capex|."""
    rows = []
    for r in data.get("yearly_metrics") or []:
        try:
            year = int(r.get("year"))
        except (TypeError, ValueError):
            continue
        eps = _num(r.get("diluted_eps"))
        if eps is None:
            eps = _num(r.get("eps_setsmart"))
        capex = _num(r.get("capex"))
        rows.append({"year": year, "eps": eps, "roe": _num(r.get("roe")), "net_income": _num(r.get("net_income")),
                     "ocf": _num(r.get("ocf")), "invest": abs(capex) if capex is not None else None,
                     "liabilities": _num(r.get("total_debt")), "equity": _num(r.get("equity")),
                     "bvps": _num(r.get("bvps")), "dividends_paid": _num(r.get("dividends_paid"))})
    return sorted(rows, key=lambda x: x["year"])


def shares_outstanding(data: dict):
    mcap, price = _num(data.get("market_cap")), _num(data.get("price"))
    return mcap / price if mcap and price else None


def loss_years(rows: list, window: int) -> list:
    last = rows[-window:] if window else rows
    return [r["year"] for r in last
            if (r["eps"] is not None and r["eps"] <= 0) or (r["eps"] is None and (r["net_income"] or 0) < 0)]


def cash_vs_dividend(rows: list, dps: dict, shares) -> list:
    """A7: (OCF - investment) vs dividends paid per year, in times. Paid = reported, else DPS x today's shares (estimate)."""
    out = []
    for r in rows:
        free = r["ocf"] - r["invest"] if r["ocf"] is not None and r["invest"] is not None else None
        paid, src = None, None
        if r["dividends_paid"] is not None:
            paid, src = abs(r["dividends_paid"]), "งบ"
        elif dps.get(r["year"]) is not None and shares:
            paid, src = dps[r["year"]] * shares, "ประมาณ (DPS x หุ้นวันนี้)"
        times = free / paid if free is not None and paid else None
        out.append({"year": r["year"], "free": free, "paid": paid, "paid_source": src, "times": times})
    return out


def payout_rows(rows: list, dps: dict) -> list:
    return [{"year": r["year"], "dps": dps.get(r["year"]), "eps": r["eps"],
             "payout": dps[r["year"]] / r["eps"] if dps.get(r["year"]) is not None and r["eps"] and r["eps"] > 0 else None}
            for r in rows]


def suspect_liability_years(liab: dict, ratio: float) -> set:
    """Years whose total liabilities jump more than `ratio` x against an adjacent year (either direction).
    Of a jumping pair only the year further from the series median (in log terms) is called suspect, so a good year
    next to a bad one is not dragged along; a run of bad years is caught at each jump."""
    import math
    vals = sorted(v for v in liab.values() if v and v > 0)
    if len(vals) < 3:
        return set()
    med = vals[len(vals) // 2]
    sus = set()
    for y, v in liab.items():
        nb = liab.get(y + 1)
        if not v or v <= 0 or not nb or nb <= 0:
            continue
        if max(v, nb) / min(v, nb) > ratio:
            sus.add(y if abs(math.log(v / med)) > abs(math.log(nb / med)) else y + 1)
    # extend through a run: adjacent years within ratio of an already-suspect year on the same side of the median
    changed = True
    while changed:
        changed = False
        for y, v in liab.items():
            if y in sus or not v or v <= 0:
                continue
            for n in (y - 1, y + 1):
                nv = liab.get(n)
                if n in sus and nv and nv > 0 and max(v, nv) / min(v, nv) <= ratio                         and (v < med) == (nv < med) and abs(math.log(v / med)) > math.log(ratio):
                    sus.add(y)
                    changed = True
    return sus


def debt_rows(rows: list, interest_bearing: dict, suspect_ratio: float = 5) -> list:
    """A6: total liabilities / equity from the cache (it is NOT interest-bearing debt) + yahoo interest-bearing if any.
    A year whose total liabilities jump > suspect_ratio x against an adjacent year is marked suspect (data likely wrong)."""
    sus = suspect_liability_years({r["year"]: r["liabilities"] for r in rows if r["liabilities"] is not None}, suspect_ratio)
    out = []
    for r in rows:
        ib = (interest_bearing or {}).get(r["year"]) or {}
        eq = r["equity"]
        out.append({"year": r["year"], "liabilities": r["liabilities"], "equity": eq, "suspect": r["year"] in sus,
                    "liab_to_equity": r["liabilities"] / eq if r["liabilities"] is not None and eq and eq > 0 else None,
                    "ib_debt": ib.get("total_debt"),
                    "ib_to_equity": ib["total_debt"] / ib["equity"] if ib.get("total_debt") is not None and ib.get("equity") else None})
    return out


# --- A10: own price history + price label ---

def price_history(rows: list, dps: dict, closes: dict, last_n: int = 10) -> list:
    """Year-end PE / PBV / yield. PE only when EPS > 0, PBV only when BVPS > 0, yield = FY DPS / year-end close."""
    by_year = {r["year"]: r for r in rows}
    out = []
    for y in sorted(closes)[-last_n:]:
        c, r = closes[y], by_year.get(y) or {}
        out.append({"year": y, "close": c,
                    "pe": c / r["eps"] if r.get("eps") and r["eps"] > 0 else None,
                    "pbv": c / r["bvps"] if r.get("bvps") and r["bvps"] > 0 else None,
                    "yield": dps[y] / c * 100 if dps.get(y) is not None and c > 0 else None})
    return out


def rank_in(value, history: list):
    """Share of history strictly below value (+ half of ties). None if no history/value."""
    if value is None or not history:
        return None
    return (sum(1 for h in history if h < value) + 0.5 * sum(1 for h in history if h == value)) / len(history)


def price_label(today_yield, hist: list, cfg: dict) -> dict:
    """Our own fixed rule: today's yield in the top N% of own year-end yields = cheap, bottom N% = expensive."""
    ys = [h["yield"] for h in hist if h["yield"] is not None]
    if today_yield is None or len(ys) < cfg["price_min_years"]:
        return {"label": "ข้อมูลไม่พอ", "rank": None, "years": len(ys)}
    r = rank_in(today_yield, ys)
    if r >= 1 - cfg["price_cheap_top_pct"] / 100:
        label = "ถูกเทียบตัวเอง"
    elif r <= cfg["price_expensive_bottom_pct"] / 100:
        label = "แพงเทียบตัวเอง"
    else:
        label = "กลางเทียบตัวเอง"
    return {"label": label, "rank": r, "years": len(ys), "min": min(ys), "max": max(ys)}


def pbv_position(today_pbv, hist: list, min_years: int) -> dict:
    vs = [h["pbv"] for h in hist if h["pbv"] is not None]
    if today_pbv is None or len(vs) < min_years:
        return {"rank": None, "years": len(vs)}
    return {"rank": rank_in(today_pbv, vs), "years": len(vs), "min": min(vs), "max": max(vs)}


# --- "wrong direction" flags (facts, not verdicts; codes follow niwes-principles T1..T6) ---

def _flag(code, name, triggered, detail):
    return {"code": code, "name": name, "triggered": triggered, "detail": detail}


def flag_t1(complete: dict, cuts: list, n_years: int) -> dict:
    """T1: DPS cut in each of the last n complete FYs (adjacent years)."""
    name = f"ปันผลต่อหุ้นลด {n_years} ปีติด"
    if not complete:
        return _flag("T1", name, None, NA)
    cut_by_fy = {c["fy"]: c for c in cuts}
    last, run = max(complete), []
    fy = last
    while fy in cut_by_fy:
        run.append(cut_by_fy[fy])
        fy -= 1
    run.reverse()
    if run:
        txt = ", ".join(f"FY{c['fy']} {c['prev']:.4g}→{c['cur']:.4g} ({c['change']*100:+.0f}%)" for c in run)
        return _flag("T1", name, len(run) >= n_years, f"ลดติดกัน {len(run)} ปีล่าสุด: {txt}")
    return _flag("T1", name, False, f"FY{last} ปันผล {complete[last]:.4g} ไม่ลดจากปีก่อน")


def flag_t2(base_dps, rates: dict, cost_list: list, year: int, low: float) -> dict:
    """T2: year-N dividend / cost in the mid scenario is below the low target (per cost level)."""
    name = f"ปันผลเทียบต้นทุนปีที่ {year} (ฉากกลาง) ต่ำกว่าเป้าล่าง {low:g}%"
    g = rates.get("mid")
    if g is None or not base_dps or base_dps <= 0 or not cost_list:
        return _flag("T2", name, None, "ข้อมูลไม่พอ — ต้องมีหน้าต่างอัตราโตปันผล 10 ปีขึ้นไป (หรือไม่มีราคา/ปันผลฐาน) จึงสร้างฉากกลางไม่ได้")
    dps_n = base_dps * (1 + g) ** year
    parts, hit = [], False
    for c in cost_list:
        y = dps_n / c["cost"] * 100
        hit = hit or y < low
        parts.append(f"ต้นทุน {c['cost']:.2f} ({c['label']}): {y:.1f}%")
    return _flag("T2", name, hit, f"ฉากกลางโต {g*100:.1f}%/ปี DPS ปีที่ {year} = {dps_n:.3f} · " + " · ".join(parts))


def flag_t4(cash_rows: list, n_years: int) -> dict:
    """T4: (OCF - investment) below dividends paid for n consecutive latest years."""
    name = f"เงินสดหลังลงทุนน้อยกว่าเงินปันผล {n_years} ปีติด"
    pts = [r for r in cash_rows if r["free"] is not None and r["paid"]][-n_years:]
    if len(pts) < n_years or pts[-1]["year"] - pts[0]["year"] != n_years - 1:
        return _flag("T4", name, None, NA)
    txt = ", ".join(f"{r['year']}: {r['free']/1e6:,.0f} vs {r['paid']/1e6:,.0f} ล้าน" for r in pts)
    return _flag("T4", name, all(r["free"] < r["paid"] for r in pts), txt)


def flag_t6(debt: list, n_years: int) -> dict:
    """T6: total liabilities / equity rose in each of the last n years."""
    name = f"หนี้สินรวมต่อทุนเพิ่ม {n_years} ปีติด"
    pts = [r for r in debt if r["liab_to_equity"] is not None and not r.get("suspect")]
    if len(pts) < n_years + 1:
        return _flag("T6", name, None, NA)
    pts = pts[-(n_years + 1):]
    if pts[-1]["year"] - pts[0]["year"] != n_years:
        return _flag("T6", name, None, NA)
    txt = " → ".join(f"{r['year']}: {r['liab_to_equity']:.2f}" for r in pts)
    return _flag("T6", name, all(b["liab_to_equity"] > a["liab_to_equity"] for a, b in zip(pts, pts[1:])), txt)


def flag_payout(payouts: list, limit: float) -> dict:
    name = f"จ่ายเกินกำไร (ปันผล/กำไรต่อหุ้น > {limit*100:.0f}%)"
    pts = [p for p in payouts if p["payout"] is not None]
    if not pts:
        return _flag("PAYOUT", name, None, NA)
    p = pts[-1]
    return _flag("PAYOUT", name, p["payout"] > limit,
                 f"ปี {p['year']}: ปันผล {p['dps']:.4g} / กำไรต่อหุ้น {p['eps']:.4g} = {p['payout']*100:.0f}%")


def flag_loss(years: list, window: int) -> dict:
    name = f"ปีขาดทุน (กำไรต่อหุ้น ≤ 0) ใน {window} ปีล่าสุด"
    return _flag("LOSS", name, bool(years), ("ปี " + ", ".join(map(str, years))) if years else "ไม่พบปีขาดทุน")


def past_double_cuts(cuts: list, n_years: int) -> list:
    """History only: runs of >= n adjacent cut years, as (first_fy, last_fy)."""
    fys = sorted(c["fy"] for c in cuts)
    runs, start, prev = [], None, None
    for fy in fys:
        if prev is not None and fy == prev + 1:
            pass
        else:
            if start is not None and prev - start + 1 >= n_years:
                runs.append((start, prev))
            start = fy
        prev = fy
    if start is not None and prev - start + 1 >= n_years:
        runs.append((start, prev))
    return runs


# --- assemble (pure) ---

MANUAL_TODO = [
    "รายได้ประจำเทียบรายได้ก้อน (D5 D18)",
    "ยอดขาย/งานรอโอน (backlog presale) (T3 T5)",
    "ผู้บริหาร + นโยบายปันผล (D7)",
    "อุตสาหกรรมตกต่ำถาวรไหม (D8)",
    "เป็นเจ้าตลาดไหม (D9)",
]


def normalize_costs(costs) -> list:
    if costs is None:
        return []
    if isinstance(costs, dict):
        costs = list(costs.values())
    elif isinstance(costs, (int, float)):
        costs = [costs]
    return [float(c) for c in costs if c]


def deep_dive_rates(override) -> dict | None:
    """{bad, mid, good} from a person-entered growth_scenarios entry, or None when it is missing / incomplete."""
    if not isinstance(override, dict) or any(_num(override.get(k)) is None for k in SCENARIOS):
        return None
    return {k: float(override[k]) for k in SCENARIOS}


def compute_fact_sheet(data: dict, costs=None, cfg=None, closes=None, interest_bearing=None,
                       gate=None, manual=None, today=None, growth_override=None) -> dict:
    """All numbers of the sheet from already-fetched inputs. No network, no files.

    growth_override: holdings.growth_scenarios entry for this stock (deep dive rates entered by a person). When
    given, it is the main scenario table; the fixed-rule rates are kept in `rates_fixed` for the comparison line."""
    cfg = cfg or load_cfg()
    profile = data.get("sector_profile") or (data.get("aggregates") or {}).get("sector_profile") or "general"
    bank = profile == "bank"
    price = _num(data.get("price"))
    complete, partial = dividend_series(data)
    last_fy = max(complete) if complete else None
    base = complete.get(last_fy) if last_fy is not None else None
    rows = yearly_rows(data)
    shares = shares_outstanding(data)
    cuts = dividend_cuts(complete, cfg["cut_material_pct"])
    cagrs = cagr_windows(data, cfg["cagr_windows"])
    rates_fixed = growth_scenarios(cagrs, cfg["growth_cap"], cfg["min_scenario_window_years"])
    dd_rates = deep_dive_rates(growth_override)
    rates = dd_rates or rates_fixed
    supplied = normalize_costs(costs)
    levels = cost_levels(price, supplied, cfg["cost_discounts"])
    targets = [cfg["yoc_target_low"], cfg["yoc_target_high"]]
    cash = None if bank else cash_vs_dividend(rows, complete, shares)
    payouts = payout_rows(rows, complete)
    debt = debt_rows(rows, interest_bearing, cfg["debt_suspect_ratio"])
    hist = price_history(rows, complete, closes or {})
    today_yield = base / price * 100 if base and price else None
    t2_costs = [c for c in levels if c["label"] == "ต้นทุนที่ส่งมา"] or [c for c in levels if c["label"] == "ราคาวันนี้"]
    losses = loss_years(rows, cfg["loss_window_years"])
    flags = [flag_t1(complete, cuts, cfg["t1_cut_years"]),
             flag_t2(base, rates, t2_costs, cfg["t2_year"], cfg["yoc_target_low"])]
    if not bank:
        flags.append(flag_t4(cash, cfg["t4_years"]))
    if not bank:
        flags.append(flag_t6(debt, cfg["t6_years"]))
    flags += [flag_payout(payouts, cfg["payout_over"]), flag_loss(losses, cfg["loss_window_years"])]
    pe_today = _num(data.get("pe_ratio"))
    price_date = data.get("price_as_of")
    try:
        price_age = (date.fromisoformat(str(today or date.today())) - date.fromisoformat(str(price_date)[:10])).days
    except (TypeError, ValueError):
        price_age = None
    return {
        "symbol": data.get("symbol"), "name": data.get("name"), "sector": data.get("sector"),
        "sector_profile": profile, "bank": bank, "price": price,
        "price_date": price_date, "price_age_days": price_age,
        "date": str(today or date.today()), "gate": gate or {},
        "dividends": {"complete": complete, "incomplete": partial, "sources": data.get("dividend_history_source") or {},
                      "last_fy": last_fy, "base_dps": base, "mismatch": data.get("dividend_source_mismatch") or {},
                      "source": data.get("dividend_source"),
                      "special": {int(k): v for k, v in (data.get("dividend_history_special") or {}).items()},
                      "first_fy": min(list(complete) + list(partial)) if (complete or partial) else None},
        "cuts": cuts, "cut_count": len(cuts), "cut_material_count": sum(1 for c in cuts if c["material"]),
        "crisis": crisis_rows(data, cfg["crisis_years"]), "cagrs": cagrs, "rates": rates, "rates_fixed": rates_fixed,
        "rates_source": ({"kind": "deep_dive", "source": growth_override.get("source"), "as_of": growth_override.get("as_of")}
                         if dd_rates else {"kind": "fixed"}),
        "costs": levels, "supplied_costs": supplied,
        "yoc": yoc_table(base, rates, levels, cfg["yoc_years"]),
        "required": required_growth(base, levels, targets, cfg["yoc_years"]),
        "dca": dca_table(base, price, rates, cfg["dca_report_years"], cfg["dca_years"], targets, cfg["dca_required_year"]),
        "targets": targets, "rows": rows, "shares": shares, "cash": cash, "payouts": payouts,
        "debt": debt, "loss_years": losses, "history": hist,
        "today": {"yield": today_yield, "yield_system": _num(data.get("dividend_yield")),
                  "pe": pe_today, "pbv": _num(data.get("pb_ratio")),
                  "pe_below_max": None if pe_today is None else (0 < pe_today < cfg["pe_niwes_max"])},
        "price_label": price_label(today_yield, hist, cfg),
        "pbv_position": pbv_position(_num(data.get("pb_ratio")), hist, cfg["price_min_years"]),
        "flags": flags, "past_double_cuts": past_double_cuts(cuts, cfg["t1_cut_years"]),
        "manual": manual, "manual_todo": MANUAL_TODO, "cfg": cfg,
    }


# --- fetch wrapper ---

MANUAL_DIR = ROOT / "data" / "manual_facts"


def bare_symbol(symbol: str) -> str:
    return symbol.upper().replace(".BK", "")


def load_manual_facts(symbol: str):
    p = MANUAL_DIR / f"{bare_symbol(symbol)}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load_growth_override(symbol: str, path=CONFIG_PATH):
    """config.json holdings.growth_scenarios[SYM] (deep dive rates a person entered), or None."""
    try:
        cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return ((cfg.get("holdings") or {}).get("growth_scenarios") or {}).get(bare_symbol(symbol))


def build_fact_sheet(symbol: str, costs=None) -> dict:
    """Fetch through the usual cache path (fetch_multi_year_safe) and compute the sheet.

    costs: None | float | list | {SYM: cost}. Returns the dict of compute_fact_sheet,
    or {"symbol", "error"} when the stock cannot be fetched.
    """
    import data_adapter
    import fetch_data
    from screen_stocks import hard_filter, gate_flags

    sym = bare_symbol(symbol) + ".BK"
    data = fetch_data.fetch_multi_year_safe(sym)
    if not isinstance(data, dict) or data.get("error") or data.get("delisted"):
        return {"symbol": sym, "error": (data or {}).get("error") or "fetch failed"}
    status, reasons = hard_filter(data)
    gate = {"status": status, "reasons": reasons, "flags": gate_flags(data)}
    return compute_fact_sheet(
        data, costs=costs, cfg=load_cfg(), growth_override=load_growth_override(sym),
        closes=data_adapter.ensure_yearend_closes(sym),
        interest_bearing=data_adapter.ensure_interest_bearing_debt(sym),
        gate=gate, manual=load_manual_facts(sym))


# --- markdown (Thai) ---

def fn(v, nd=2, scale=1.0, suffix=""):
    return NA if v is None else f"{v / scale:,.{nd}f}{suffix}"


def pct(v, nd=1):
    return NA if v is None else f"{v * 100:.{nd}f}%"


def _table(head: list, body: list) -> list:
    return ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"] + \
           ["| " + " | ".join(str(c) for c in r) + " |" for r in body]


def _src_label(s):
    return {"set": "set.or.th", "yahoo": "yahoo", "set_partial": "set.or.th (บางส่วน)"}.get(s, s or NA)


def _head_lines(fs):
    g = fs["gate"] or {}
    lines = [f"# ใบข้อเท็จจริง {bare_symbol(fs['symbol'])} — {fs.get('name') or NA}", "",
             f"- กลุ่ม: {fs.get('sector') or NA} · sector_profile: `{fs['sector_profile']}`",
             f"- ราคา: {fn(fs['price'])} บาท (ราคาปิดวันที่ {fs['price_date'] or NA}) · วันที่ใบ: {fs['date']}",
             f"- ผลด่าน: **{g.get('status', NA)}**" + (f" — {'; '.join(g['reasons'])}" if g.get("reasons") else "")]
    lines.append(f"- gate_flags: {', '.join(g['flags']) if g.get('flags') else 'ไม่มี'}")
    age, limit = fs["price_age_days"], fs["cfg"]["price_stale_days"]
    if age is None:
        lines.append("- ⏳ ไม่รู้วันที่ของราคา — ยีลด์/PE/PBV วันนี้อาจเก่า")
    elif age > limit:
        lines.append(f"- ⏳ ราคาเก่า {age} วัน (เกิน {limit} วัน) — cache SETSMART ไม่ได้อัปเดต ยีลด์/PE/PBV วันนี้ ตามราคานี้")
    lines += ["",
              "> ใบนี้คือข้อเท็จจริงให้คนอ่าน — ไม่มีคะแนนรวม ไม่มีอันดับ ไม่มีคำแนะนำซื้อ/ขาย",
              "> แหล่ง: ราคา/PE/PBV วันนี้ = SETSMART/yahoo ผ่าน cache ของระบบ · งบรายปี = thaifin/SETSMART (`yearly_metrics`) · "
              "ปันผล = set.or.th (ปีใหม่) + yahoo (ปีเก่า) ตามคอลัมน์ที่มา · ราคาสิ้นปี/หนี้มีดอกเบี้ย = yahoo",
              "> เกณฑ์ \"เราตั้งเอง\" = เลขที่ระบบนี้ตั้ง (อยู่ใน config.json `fact_sheet`) ไม่ใช่คำของดร.นิเวศน์", ""]
    return lines


def _a1(fs):
    d = fs["dividends"]
    lines = ["## A1 ปันผลต่อหุ้นรายปีบัญชี", "",
             f"แหล่ง: {d['source'] or NA} · ปีที่มี {len(d['complete'])} ปี "
             f"({min(d['complete']) if d['complete'] else NA}–{d['last_fy'] or NA})"]
    if d["source"] and "yahoo" in d["source"]:
        lines.append("หมายเหตุ: ค่าจาก yahoo เป็นค่าที่ปรับย้อนหลังตามการแตกพาร์/ปันผลหุ้น อาจต่างจากค่าที่บริษัทประกาศเล็กน้อย (เช่น AMATA 0.5456 แทน 0.55)")
    if fs["sector_profile"] == "reit":
        lines.append("หมายเหตุ REIT: ปีบัญชีของปันผลจาก yahoo อาจไม่ตรงปีบัญชีจริง (กฎจัดปี ม.ค.–มิ.ย. = ปีก่อน) — ดูผลเทียบแหล่งใน job 06")
    lines.append("")
    sp = d.get("special") or {}
    prev, body = None, []
    for fy in sorted(d["complete"]):
        v = d["complete"][fy]
        yoy = f"{(v / prev - 1) * 100:+.0f}%" if prev else "—"
        row = [fy, fn(v, 4)]
        if sp:
            row += [fn(sp[fy], 4) if fy in sp else "—", fn(v + sp.get(fy, 0), 4)]
        body.append(row + [yoy, _src_label(d["sources"].get(str(fy)) or d["sources"].get(fy))])
        prev = v if v else None
    head = ["ปีบัญชี", "ปันผลปกติ (บาท)" if sp else "ปันผลต่อหุ้น (บาท)"] + (["ปันผลพิเศษ (บาท)", "รวม"] if sp else []) + ["เทียบปีก่อน (ปกติ)" if sp else "เทียบปีก่อน", "ที่มา"]
    lines += _table(head, body) if body else [NA]
    if sp:
        lines += ["", "ปันผลพิเศษมาจาก `config.json` `special_dividends` (คนกรอกจาก deep dive) — นับครั้งที่ลด / ปีฟื้น / อัตราโต / ฉาก / ยีลด์สิ้นปี / ธง T1 ใช้เฉพาะ**ปกติ**: "
                  + ", ".join(f"FY{y} {v:g} บาท" for y, v in sorted(sp.items()))]
    if d.get("first_fy") is not None:
        lines += ["", f"ระบบมีข้อมูลตั้งแต่ปี {d['first_fy']} — เหตุการณ์ก่อนหน้านั้นไม่อยู่ในตาราง"]
    if d["incomplete"]:
        lines += ["", "ปีที่ยังไม่ครบ (ไม่นับในตัวเลขด้านล่าง): " +
                  ", ".join(f"FY{y} = {v:.4g}" for y, v in sorted(d["incomplete"].items()))]
    for fy, m in sorted(d["mismatch"].items()):
        lines.append(f"⛔ สองแหล่งไม่ตรงกัน FY{fy}: set={m.get('set')} yahoo={m.get('yahoo')}")
    return lines + [""]


def _a2(fs):
    th = fs["cfg"]["cut_material_pct"]
    lines = ["## A2 ปันผลลดกี่ครั้ง", "",
             f"ลดทุกขนาด {fs['cut_count']} ครั้ง · ลดตั้งแต่ {th:g}% ขึ้นไป {fs['cut_material_count']} ครั้ง (เกณฑ์ {th:g}% เราตั้งเอง)", ""]
    body = [[x["fy"], f"{x['prev']:.4g} → {x['cur']:.4g}", f"{x['change']*100:+.1f}%",
             ("ใช่" if x["material"] else "ไม่"),
             (f"{x['recovery_years']} ปี" if x["recovery_years"] is not None else "ยังไม่กลับ")] for x in fs["cuts"]]
    lines += _table(["ปีที่ลด", "ปันผล (ก่อน → หลัง)", "ลด", f"ลด ≥{th:g}%", "กลับมาเท่าเดิมใน"], body) if body else ["ไม่พบปีที่ปันผลลด"]
    lines += ["", "ปีวิกฤต:", ""]
    lines += _table(["ปี", "ปันผลเทียบปีก่อน", "กลับมาเท่าเดิมใน"],
                    [[x["year"], pct(x["change"], 0) if x["change"] is not None else NA,
                      NA if x["recovery_years"] is None and x["change"] is None else
                      ("ไม่ลด" if x["recovery_years"] == 0 else ("ยังไม่กลับ" if x["recovery_years"] is None else f"{x['recovery_years']} ปี"))]
                     for x in fs["crisis"]])
    return lines + [""]


def _a3(fs):
    lines = ["## A3 อัตราปันผลโตทบต้น (จากปีบัญชีล่าสุดที่ครบ)", ""]
    lines += _table(["หน้าต่าง", "โตต่อปี"], [[f"{n} ปี", pct(v)] for n, v in fs["cagrs"].items()])
    return lines + ["", "หน้าต่างเดียวหลอกตาได้ — ดูทุกหน้าต่างด้วยกัน", ""]


def _a4(fs):
    d, r = fs["dividends"], fs["rates"]
    lo, hi = fs["targets"]
    rs = fs.get("rates_source") or {"kind": "fixed"}
    dd = rs["kind"] == "deep_dive"
    rule = fs.get("rates_fixed") or r  # the fixed-rule bullets always show the fixed rates
    lines = ["## A4 ปันผลเทียบต้นทุน (ปันผลปีนั้น ÷ ต้นทุน) — ก้อนที่ถืออยู่ (ต้นทุนคงที่)", "",
             f"ฐาน: ปันผลปีบัญชีล่าสุดที่ครบ FY{d['last_fy'] or NA} = {fn(d['base_dps'], 4)} บาท · ปีที่ N = FY{d['last_fy'] or '?'}+N"]
    if dd:
        rf = fs["rates_fixed"]
        lines += [f"**อัตราโตจาก deep dive {rs.get('as_of') or NA} — สมมติฐานของคน รอ Art เคาะ** (ที่มา: {rs.get('source') or NA}) → "
                  f"แย่ {pct(r['bad'])} · กลาง {pct(r['mid'])} · ดี {pct(r['good'])} ใช้เป็นตารางหลักด้านล่าง",
                  f"เทียบกฎตายตัว: แย่ {pct(rf['bad'])} · กลาง {pct(rf['mid'])} · ดี {pct(rf['good'])} (กฎด้านล่างใช้เมื่อไม่มีค่าจาก deep dive)", ""]
    lines += ["ฉากอัตราโตตามกฎตายตัว (**เราตั้งเอง** ไม่ใช่คำนิเวศน์ และไม่ใช่คำทำนาย)" + (" — ไม่ได้ใช้ในตารางหลักของหุ้นนี้:" if dd else ":"),
             f"- ต้องมีหน้าต่างอัตราโตตั้งแต่ {fs['cfg']['min_scenario_window_years']} ปีขึ้นไปอย่างน้อย 1 หน้าต่าง ไม่งั้น = ข้อมูลไม่พอ (ไม่สร้างฉาก)",
             f"- เพดานอัตราโตทุกฉาก {fs['cfg']['growth_cap']*100:g}% ต่อปี",
             f"- แย่ = ค่าต่ำสุดของอัตราโตทุกหน้าต่างที่มี (ไม่ต่ำกว่า 0) → {pct(rule['bad']) if rule['bad'] is not None else 'ข้อมูลไม่พอ'}",
             f"- ดี = ค่าสูงสุดของอัตราโตทุกหน้าต่างที่มี ตัดที่เพดาน → {pct(rule['good']) if rule['good'] is not None else 'ข้อมูลไม่พอ'}",
             f"- กลาง = ค่าเฉลี่ยของแย่กับดี → {pct(rule['mid']) if rule['mid'] is not None else 'ข้อมูลไม่พอ'}",
             "- ต้นทุน = ที่ส่งมาด้วย `--cost` + ราคาวันนี้ + ราคาวันนี้ x 0.8 และ x 0.6 "
             + ("" if fs["supplied_costs"] else "(ยังไม่ได้ส่งต้นทุน — ใช้ราคาวันนี้แทน)"), ""]
    if not fs["costs"]:
        return lines + [NA, ""]
    head = ["ฉาก", "โต/ปี", "ปีที่", "DPS"] + [f"@{c['cost']:.2f}" for c in fs["costs"]]
    lines += ["ระดับต้นทุน: " + " · ".join(f"@{c['cost']:.2f} = {c['label']}" for c in fs["costs"]), ""]
    lines += _table(head, [[SCENARIO_TH[x["scenario"]], pct(x["rate"]) if x["rate"] is not None else INSUFFICIENT, x["year"],
                            fn(x["dps"], 3) if x["rate"] is not None else INSUFFICIENT] +
                           [fn(y, 1, suffix="%") if x["rate"] is not None else INSUFFICIENT for y in x["yoc"]] for x in fs["yoc"]])
    lines += ["", f"อัตราโตต่อปีที่ต้องการ เพื่อให้ปันผลปีที่ N แตะเป้าล่าง {lo:g}% / เป้าบน {hi:g}% ของต้นทุน (จากฐาน {fn(d['base_dps'], 4)}):", ""]
    lines += _table(["ต้นทุน", "ปีที่", f"ถึง {lo:g}%", f"ถึง {hi:g}%"],
                    [[f"{x['cost']:.2f}", x["year"]] + [pct(g) for g in x["growth"]] for x in fs["required"]])
    return lines + [""] + _a4_dca(fs)


def _band_text(v, lo, hi):
    return "ต่ำกว่าเป้าล่าง" if v < lo else ("สูงกว่าเป้าบน" if v > hi else "อยู่ในช่วงเป้า")


def _dca_cell(v, lo, hi):
    return INSUFFICIENT if v is None else f"{v:.1f}% ({_band_text(v, lo, hi)})"


def _a4_dca(fs):
    lo, hi = fs["targets"]
    cfg = fs["cfg"]
    req = cfg["dca_required_year"]
    lines = [f"### A4 ถ้าซื้อทุกเดือน (DCA) — เงินเท่ากันทุกเดือน {cfg['dca_years']} ปี แล้วถือต่อ", "",
             "กฎตายตัว (**เราตั้งเอง** ไม่ใช่คำนิเวศน์ ไม่ใช่คำทำนาย): ปันผลต่อหุ้นโตตามฉากเดิมจากปันผลปีครบล่าสุด · "
             "ราคาที่ซื้อแต่ละเดือนมี 2 กรณี: (ก) ราคาโตเท่าปันผล = yield ตอนซื้อคงที่เท่า yield วันนี้ · "
             "(ข) ราคานิ่ง = ซื้อที่ราคาวันนี้ตลอด yield ตอนซื้อสูงขึ้นตามปันผล · "
             f"ผล = ปันผลที่ได้ในปีที่ N ÷ เงินที่ลงทั้งหมดถึงปีนั้น (ปีที่ 5 ลงมาแค่ 5 ปี · ปีที่ 15 หยุดลงหลังปีที่ {cfg['dca_years']})",
             "เลขนี้ต่ำกว่าตารางก้อนที่ถืออยู่ เพราะเงินที่ลงปีหลัง ๆ มีเวลาให้ปันผลโตน้อยกว่า และราคาที่โตตามปันผลทำให้ต้นทุนเฉลี่ยสูงกว่าราคาวันนี้",
             f"กรณีราคานิ่งเท่ากับก้อนเดียวที่ต้นทุน = ราคาวันนี้ (ทุกหุ้นรับปันผลต่อหุ้นเท่ากันในปีนั้น) — ต่างกันที่กรณีราคาโตเท่าปันผลเท่านั้น", ""]
    if not any(x["ok"] for x in fs["dca"]):
        return lines + [INSUFFICIENT, ""]
    body = []
    for x in fs["dca"]:
        for y in x["years"]:
            body.append([SCENARIO_TH[x["scenario"]], pct(x["rate"]) if x["rate"] is not None else INSUFFICIENT, y["year"],
                         _dca_cell(y[PRICE_GROWS], lo, hi), _dca_cell(y[PRICE_FLAT], lo, hi)])
    lines += _table(["ฉาก", "โต/ปี", "ปีที่", f"ราคาโตเท่าปันผล (เทียบเป้า {lo:g} / {hi:g}%)", "ราคานิ่ง"], body)
    lines += ["", f"yield เฉลี่ยตอนซื้อ (ปันผลวันนี้ ÷ ราคาซื้อเฉลี่ย) ที่ต้องเป็น เพื่อให้ปันผลปีที่ {req} แตะเป้าล่าง {lo:g}% / เป้าบน {hi:g}%:", ""]
    lines += _table(["ฉาก", f"ถึง {lo:g}%", f"ถึง {hi:g}%"],
                    [[SCENARIO_TH[x["scenario"]]] + [f"{v:.2f}%" if v is not None else INSUFFICIENT for v in x["required"]] for x in fs["dca"]])
    return lines + [""]


def _a5(fs):
    bank = fs["bank"]
    lines = ["## A5 กำไรต่อหุ้น · ROE · เงินสด · เงินลงทุน รายปี", "",
             "แหล่ง: `yearly_metrics` (thaifin/SETSMART) · หน่วยเงิน = ล้านบาท · เงินลงทุน = ค่าสัมบูรณ์ของ capex (เครื่องหมายใน cache ไม่คงที่)"]
    if bank:
        lines.append("แบงก์: ไม่แสดงเงินสดจากดำเนินงาน/เงินลงทุน — ความหมายต่างจากธุรกิจทั่วไป (เงินฝาก/เงินให้สินเชื่อวิ่งผ่านงบกระแสเงินสด)")
    lines.append("")
    head = ["ปี", "กำไรต่อหุ้น", "ROE", "กำไรสุทธิ"] + ([] if bank else ["เงินสดจากดำเนินงาน", "เงินลงทุน"]) + ["ขาดทุน?"]
    body = []
    for r in fs["rows"]:
        loss = r["year"] in fs["loss_years"]
        body.append([r["year"], fn(r["eps"], 2), pct(r["roe"]), fn(r["net_income"], 0, 1e6)] +
                    ([] if bank else [fn(r["ocf"], 0, 1e6), fn(r["invest"], 0, 1e6)]) + ["ใช่" if loss else ""])
    lines += _table(head, body) if body else [NA]
    lines.append("")
    lines.append("ปีขาดทุน (ช่วง %d ปีล่าสุด): %s" % (fs["cfg"]["loss_window_years"],
                 ", ".join(map(str, fs["loss_years"])) if fs["loss_years"] else "ไม่พบ"))
    return lines + [""]


def _a7(fs):
    if fs["bank"]:
        return ["## A7 เงินสดหลังลงทุน เทียบเงินปันผลที่จ่าย", "", "ไม่พิมพ์สำหรับแบงก์ — เงินสดจากดำเนินงานของแบงก์มีความหมายต่างจากธุรกิจทั่วไป (ธง T4 ไม่ใช้ด้วย)", ""]
    lines = ["## A7 เงินสดหลังลงทุน (เงินสดจากดำเนินงาน − เงินลงทุน) เทียบเงินปันผลที่จ่าย", "",
             "ปันผลที่จ่าย: ใช้ตัวเลขจากงบถ้ามี ไม่มี → ประมาณ = ปันผลต่อหุ้น x จำนวนหุ้นวันนี้ "
             f"({fn(fs['shares'], 0, 1e6)} ล้านหุ้น = มูลค่าตลาด ÷ ราคา) — จำนวนหุ้นย้อนหลังอาจต่าง", ""]
    body = [[x["year"], fn(x["free"], 0, 1e6), fn(x["paid"], 0, 1e6), x["paid_source"] or NA,
             fn(x["times"], 1, suffix=" เท่า")] for x in fs["cash"]]
    return lines + (_table(["ปี", "เงินสดหลังลงทุน", "ปันผลจ่าย", "ที่มาของปันผลจ่าย", "เป็นกี่เท่า"], body) if body else [NA]) + [""]


def _a6(fs):
    if fs["bank"]:
        return ["## A6 หนี้", "", "ไม่พิมพ์ตารางหนี้ต่อทุนสำหรับแบงก์ และไม่คิดธง T6 — หนี้สินของธนาคารส่วนใหญ่คือเงินฝากของลูกค้า "
                "ความหมายต่างจากหนี้ของธุรกิจทั่วไป", ""]
    lines = ["## A6 หนี้", "",
             "**`total_debt` ใน cache = หนี้สินรวม (total liabilities) ไม่ใช่หนี้มีดอกเบี้ย** · หนี้มีดอกเบี้ย (yahoo TotalDebt) มีเฉพาะปีที่ yahoo ให้ (~4 ปี)"]
    if fs["bank"]:
        lines.append("แบงก์: หนี้สินรวมส่วนใหญ่คือเงินฝาก — อัตราส่วนนี้ไม่ใช่ความเสี่ยงหนี้แบบธุรกิจทั่วไป")
    lines.append("")
    sus = [x["year"] for x in fs["debt"] if x.get("suspect")]
    if sus:
        lines += [f"⛔ ข้อมูลปีนี้น่าสงสัย: {', '.join(map(str, sus))} — หนี้สินรวมต่างจากปีข้างเคียงเกิน {fs['cfg']['debt_suspect_ratio']:g} เท่า "
                  "(น่าจะเป็นฟิลด์ผิดในแหล่งข้อมูล) ไม่แสดงตัวเลขปีนั้น และไม่ใช้คิดธง T6", ""]
    S = "ข้อมูลปีนี้น่าสงสัย"
    body = [[x["year"], S if x.get("suspect") else fn(x["liabilities"], 0, 1e6), fn(x["equity"], 0, 1e6),
             S if x.get("suspect") else fn(x["liab_to_equity"], 2),
             fn(x["ib_debt"], 0, 1e6), fn(x["ib_to_equity"], 2)] for x in fs["debt"]]
    return lines + (_table(["ปี", "หนี้สินรวม", "ส่วนผู้ถือหุ้น", "หนี้สินรวม/ทุน", "หนี้มีดอกเบี้ย", "หนี้มีดอกเบี้ย/ทุน"], body) if body else [NA]) + [""]


def _a12(fs):
    lines = ["## A12 สัดส่วนจ่ายปันผลต่อกำไร (ปันผลต่อหุ้น ÷ กำไรต่อหุ้น)", ""]
    body = [[x["year"], fn(x["dps"], 4), fn(x["eps"], 2), pct(x["payout"], 0)] for x in fs["payouts"]]
    return lines + (_table(["ปี", "ปันผลต่อหุ้น", "กำไรต่อหุ้น", "จ่ายต่อกำไร"], body) if body else [NA]) + [""]


def yield_vs_niwes_line(today_yield, niwes_min) -> str:
    """The line printed under the price label: the label is relative to the stock itself, not to the 5% bar."""
    if today_yield is None:
        return f"yield วันนี้ {NA} เกณฑ์ {niwes_min:g}% ของนิเวศน์"
    rel = "ถึง" if today_yield >= niwes_min else "ต่ำกว่า"
    return f"yield วันนี้ {today_yield:.1f}% {rel} เกณฑ์ {niwes_min:g}% ของนิเวศน์"


def _a10(fs):
    cfg, t, pl, pp = fs["cfg"], fs["today"], fs["price_label"], fs["pbv_position"]
    lines = ["## A10 ประวัติราคาของตัวเอง (ณ สิ้นปี) และป้ายราคา", "",
             "แหล่ง: ราคาปิดเดือนธันวาคม (yahoo) · PE = ราคา ÷ กำไรต่อหุ้นปีนั้น (เฉพาะกำไร > 0) · PBV = ราคา ÷ มูลค่าทางบัญชีต่อหุ้น · "
             "ยีลด์ = ปันผลปีบัญชีนั้น ÷ ราคาสิ้นปี", ""]
    body = [[h["year"], fn(h["close"]), fn(h["pe"], 1), fn(h["pbv"], 2), fn(h["yield"], 1, suffix="%")] for h in fs["history"]]
    body.append(["วันนี้", fn(fs["price"]), fn(t["pe"], 1), fn(t["pbv"], 2), fn(t["yield"], 1, suffix="%")])
    lines += _table(["ปี", "ราคาปิดสิ้นปี", "PE", "PBV", "ยีลด์"], body)
    lines += ["", f"ยีลด์วันนี้ = ปันผล FY{fs['dividends']['last_fy'] or NA} ÷ ราคาวันนี้ (ให้เทียบกับตารางได้) · "
              f"ยีลด์ที่ระบบรายงาน (`dividend_yield`) = {fn(t['yield_system'], 2, suffix='%')}", ""]
    lines.append(f"### ป้ายราคา: **{pl['label']}**")
    if pl["rank"] is None:
        lines.append(f"ข้อมูลไม่พอ — มียีลด์ย้อนหลัง {pl['years']} ปี ต้องมีอย่างน้อย {cfg['price_min_years']} ปี")
    else:
        lines.append(f"ยีลด์วันนี้ {t['yield']:.1f}% อยู่ที่ตำแหน่ง {pl['rank']*100:.0f}% ของยีลด์สิ้นปีตัวเอง {pl['years']} ปี "
                     f"(ช่วง {pl['min']:.1f}–{pl['max']:.1f}%) · ตำแหน่งสูง = ราคาถูกเมื่อเทียบกับปันผล")
    lines.append(yield_vs_niwes_line(t["yield"], cfg["yield_niwes_min"]))
    lines += [f"กฎ (**เราตั้งเอง** ไม่ใช่คำนิเวศน์): ยีลด์วันนี้อยู่ในช่วงสูงสุด {cfg['price_cheap_top_pct']:g}% ของยีลด์สิ้นปีตัวเอง = ถูก · "
              f"ต่ำสุด {cfg['price_expensive_bottom_pct']:g}% = แพง · ที่เหลือ = กลาง · ประวัติน้อยกว่า {cfg['price_min_years']} ปี = ข้อมูลไม่พอ", ""]
    pe = t["pe"]
    lines.append(f"- PE วันนี้ {fn(pe, 1)} → " + (NA if t["pe_below_max"] is None else
                 ("ต่ำกว่า" if t["pe_below_max"] else "ไม่ต่ำกว่า") + f" {cfg['pe_niwes_max']:g} (เลข PE <{cfg['pe_niwes_max']:g} ที่นิเวศน์ให้ — หลัก P3)"))
    if pp["rank"] is None:
        lines.append(f"- PBV วันนี้ {fn(t['pbv'], 2)} · เทียบช่วงตัวเอง: ข้อมูลไม่พอ ({pp['years']} ปี)")
    else:
        lines.append(f"- PBV วันนี้ {t['pbv']:.2f} · ช่วงสิ้นปีตัวเอง {pp['min']:.2f}–{pp['max']:.2f} ({pp['years']} ปี) · "
                     f"สูงกว่า {pp['rank']*100:.0f}% ของปีในอดีต")
    lines.append(f"- ยีลด์เกณฑ์นิเวศน์ {cfg['yield_niwes_min']:g}% (C1): ยีลด์วันนี้ {fn(t['yield'], 1, suffix='%')}")
    return lines + [""]


def _flags(fs):
    lines = ["## ธง \"ผิดทาง\" (ข้อเท็จจริง ไม่ใช่คำตัดสิน — รหัส T ตาม niwes-principles ท่อน 4)", "",
             "นิเวศน์: ปันผลลดแล้ว \"ชั่วคราวไม่ต้องทำอะไร / ลดมากและถาวรปรับพอร์ต\" — ธงบอกแค่ว่าตัวเลขติดเกณฑ์ที่เราตั้ง คนต้องประเมินเหตุเอง", ""]
    for f in fs["flags"]:
        mark = "ไม่มีข้อมูล" if f["triggered"] is None else ("⛔ ติด" if f["triggered"] else "✅ ไม่ติด")
        lines.append(f"- **{f['code']}** {f['name']}: {mark} — {f['detail']}")
    if fs["bank"]:
        lines.append("- T4 ไม่ใช้กับแบงก์ (เงินสดจากดำเนินงานมีความหมายต่าง)")
    if fs["past_double_cuts"]:
        lines.append("- เคยลดติดกันในอดีต: " + ", ".join(f"FY{a}–FY{b}" for a, b in fs["past_double_cuts"]))
    return lines + [""]


def _manual(fs):
    lines = ["## ต้องกรอกมือ / ต้องคนตัดสิน", ""]
    m = fs["manual"]
    if m:
        lines.append(f"จาก `data/manual_facts/{bare_symbol(fs['symbol'])}.json` (as_of: {m.get('as_of', NA)})")
        lines += [f"- {k}: {json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v}" for k, v in m.items() if k != "as_of"]
    else:
        lines.append("ไม่มีไฟล์กรอกมือ — algo ตอบไม่ได้ ต้องคนหา/ตัดสิน:")
        lines += [f"- {t}" for t in fs["manual_todo"]]
    return lines + [""]


def render_markdown(fs: dict) -> str:
    if fs.get("error"):
        return f"# {fs.get('symbol')}\n\nดึงข้อมูลไม่ได้: {fs['error']}\n"
    parts = _head_lines(fs) + _a1(fs) + _a2(fs) + _a3(fs) + _a4(fs) + _a5(fs) + _a7(fs) + _a6(fs) + _a12(fs) + _a10(fs) + _flags(fs) + _manual(fs)
    return "\n".join(parts).rstrip() + "\n"


# --- CLI ---

def parse_costs(items) -> dict:
    out = {}
    for it in items or []:
        sym, _, val = it.partition("=")
        if not val:
            raise SystemExit(f"--cost ต้องเป็น SYM=ราคา (ได้ '{it}')")
        out.setdefault(bare_symbol(sym), []).append(float(val))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ใบข้อเท็จจริงต่อหุ้น")
    ap.add_argument("symbols", nargs="+")
    ap.add_argument("--cost", action="append", default=[], help="SYM=ราคา (ส่งซ้ำได้)")
    ap.add_argument("--out", default=str(ROOT / "reports" / "facts"))
    ap.add_argument("--refresh", action="store_true", help="ดึงราคาล่าสุดของหุ้นที่ระบุก่อนสร้างใบ")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    costs, out_dir = parse_costs(args.cost), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.refresh:
        import data_adapter
        for sym, info in data_adapter.refresh_prices(args.symbols).items():
            print(f"refresh {sym}: " + (f"{info['close']} @ {info['date']}" if info["ok"] else f"ไม่ได้ — {info['error']}"))
    for raw in args.symbols:
        sym = bare_symbol(raw)
        fs = build_fact_sheet(sym, costs.get(sym))
        text = render_markdown(fs)
        print(text)
        if not fs.get("error"):
            (out_dir / f"{sym}_{fs['date']}.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
