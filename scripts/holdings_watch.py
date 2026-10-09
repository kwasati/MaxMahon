"""Holdings watch: one table for every stock Art really holds + the "wrong direction" status. Facts only.

Usage: py scripts\\holdings_watch.py [--cost SYM=ราคา ...] [--refresh] [--out reports\\holdings]

Holdings = keys of rebalance.TARGETS (in plan, read at call time - never copied; leg from rebalance.LEGS) + config.json holdings.off_plan.
ขาเซียนฮง rows: no gate / T flags / year-N scenarios (S3: Hong scanner is not imported). Roll-up = ขา Niwes only.
Status rule (fixed): เปิดทบทวน = T1 triggered · เฝ้า = any other flag triggered · ปกติ = none.
Every threshold comes from config.json (fact_sheet + holdings). No score, no rank, no instruction to trade.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fact_sheet as fsmod  # noqa: E402

NA = fsmod.NA
REVIEW, WATCH, NORMAL = "เปิดทบทวน", "เฝ้า", "ปกติ"
DEFAULT_HOLDINGS = {"off_plan": ["TISCO"], "costs": {}, "costs_as_of": None, "yoc_year": 10}
LEG_NIWES, LEG_HONG = "niwes", "hong"
LEG_TEXT = {LEG_NIWES: "Niwes", LEG_HONG: "เซียนฮง", None: "นอกแผน"}
HONG_STATUS = "ขาเซียนฮง — ดูด้วย Hong scanner"
NO_COST_TEXT = "ไม่ได้กรอก — ใช้ราคาวันนี้"


def load_holdings_cfg(path=fsmod.CONFIG_PATH) -> dict:
    cfg = {k: (list(v) if isinstance(v, list) else dict(v) if isinstance(v, dict) else v)
           for k, v in DEFAULT_HOLDINGS.items()}
    try:
        cfg.update(json.loads(Path(path).read_text(encoding="utf-8")).get("holdings") or {})
    except (OSError, ValueError):
        pass
    return cfg


def holding_entries(hcfg: dict) -> list:
    """[{symbol, in_plan, target, leg}] - plan keys of rebalance.TARGETS (leg from rebalance.LEGS), then config off_plan (deduped).

    Order: ขา Niwes -> ขาเซียนฮง -> in-plan without a leg -> off-plan."""
    import rebalance
    leg_of = {s: leg for leg, syms in rebalance.LEGS.items() for s in syms}
    rank = {LEG_NIWES: 0, LEG_HONG: 1, None: 2}
    plan = sorted(rebalance.TARGETS, key=lambda s: rank.get(leg_of.get(s), 2))  # stable: keeps TARGETS order inside a leg
    entries = [{"symbol": fsmod.bare_symbol(s), "in_plan": True, "target": float(rebalance.TARGETS[s]), "leg": leg_of.get(s)}
               for s in plan]
    seen = {e["symbol"] for e in entries}
    for s in hcfg.get("off_plan") or []:
        b = fsmod.bare_symbol(s)
        if b not in seen:
            seen.add(b)
            entries.append({"symbol": b, "in_plan": False, "target": None, "leg": None})
    return entries


def resolve_costs(config_costs, cli_costs) -> dict:
    """{SYM: cost}. config holdings.costs first (0 / empty = not entered), --cost SYM=ราคา overrides it."""
    out = {}
    for s, c in (config_costs or {}).items():
        if isinstance(c, (int, float)) and not isinstance(c, bool) and c > 0:
            out[fsmod.bare_symbol(s)] = float(c)
    for s, vals in (cli_costs or {}).items():
        vals = [v for v in vals if v and v > 0]
        if vals:
            out[fsmod.bare_symbol(s)] = float(vals[-1])
    return out


def status_of(fs: dict) -> str:
    triggered = [f["code"] for f in fs.get("flags", []) if f.get("triggered")]
    if "T1" in triggered:
        return REVIEW
    return WATCH if triggered else NORMAL


def triggered_flags(fs: dict) -> list:
    return [f for f in fs.get("flags", []) if f.get("triggered")]


def _cost_index(fs: dict, cost):
    for i, c in enumerate(fs.get("costs") or []):
        if cost is not None and round(c["cost"], 2) == round(cost, 2):
            return i
    return None


def yoc_at(fs: dict, scenario: str, year: int, idx):
    """DPS in `year` under `scenario` / cost level idx (%), None if the table lacks it."""
    if idx is None:
        return None
    for r in fs.get("yoc") or []:
        if r["scenario"] == scenario and r["year"] == year:
            return r["yoc"][idx]
    return None


def summarize(entry: dict, fs: dict, cost, year: int) -> dict:
    """One table row. fs may be an error stub ({'symbol', 'error'}) -> row marked ดึงข้อมูลไม่ได้."""
    row = {"symbol": entry["symbol"], "in_plan": entry["in_plan"], "target": entry["target"],
           "plan_text": "ในแผน" if entry["in_plan"] else "นอกแผน", "error": None,
           "leg": entry.get("leg"), "leg_text": LEG_TEXT.get(entry.get("leg"), "นอกแผน" if not entry["in_plan"] else "—")}
    if fs.get("error"):
        row.update(error=str(fs["error"]), status=None, flags=[], missing=[])
        return row
    used = cost if cost else fs.get("price")
    base = fs["dividends"]["base_dps"]
    idx = _cost_index(fs, used)
    hong = row["leg"] == LEG_HONG  # เซียนฮง: no Niwes gate / T flags / year-N scenarios - facts only
    row.update(
        price=fs.get("price"), price_date=fs.get("price_date"), age=fs.get("price_age_days"),
        yield_today=fs["today"]["yield"], cost_text=(f"{cost:g}" if cost else NO_COST_TEXT), cost_used=used,
        pnl_pct=(((fs.get("price") / cost) - 1) * 100 if cost and fs.get("price") else None),
        yoc_now=(base / used * 100 if base and used else None),
        yoc_scen={k: (None if hong else yoc_at(fs, k, year, idx)) for k in fsmod.SCENARIOS},
        dca={m: (None if row["leg"] != LEG_NIWES else fsmod.dca_yoc(base, fs.get("price"), (fs.get("rates") or {}).get("mid"), year,
                                                                   fs["cfg"]["dca_years"], m)) for m in (fsmod.PRICE_GROWS, fsmod.PRICE_FLAT)},
        rates=dict(fs.get("rates") or {}), scenario_ok=(not hong) and (fs.get("rates") or {}).get("mid") is not None,
        price_label=fs["price_label"]["label"], gate=("—" if hong else (fs.get("gate") or {}).get("status", NA)),
        status=(HONG_STATUS if hong else status_of(fs)),
        flags=([] if hong else [f["code"] for f in triggered_flags(fs)]),
        missing=([] if hong else [f["code"] for f in fs.get("flags", []) if f.get("triggered") is None]))
    return row


def collect(entries: list, costs: dict, builder=None) -> dict:
    """{SYM: fact sheet or error stub}. One stock failing (error stub or exception) never stops the rest."""
    builder = builder or fsmod.build_fact_sheet
    sheets = {}
    for e in entries:
        s = e["symbol"]
        try:
            sheets[s] = builder(s, [costs[s]] if s in costs else None)
        except Exception as ex:  # noqa: BLE001
            sheets[s] = {"symbol": s, "error": f"{type(ex).__name__}: {ex}"}
    return sheets


# --- portfolio roll-up (in-plan only, weighted by target share) ---

def portfolio_rollup(rows: list) -> dict:
    """Target-weighted dividend/cost for ขา Niwes rows only (base re-weighted to 100%). A stock lacking a number is skipped for that column (and named)."""
    plan = [r for r in rows if r["in_plan"] and r.get("leg") == LEG_NIWES]
    cols = {"now": lambda r: r.get("yoc_now")}
    cols.update({"dca_" + m: (lambda r, m=m: (r.get("dca") or {}).get(m)) for m in (fsmod.PRICE_GROWS, fsmod.PRICE_FLAT)})
    cols.update({k: (lambda r, k=k: (r.get("yoc_scen") or {}).get(k) if r.get("scenario_ok") else None) for k in fsmod.SCENARIOS})
    out = {}
    for name, get in cols.items():
        use = [(r["target"], get(r)) for r in plan if r.get("error") is None and get(r) is not None]
        skipped = [r["symbol"] for r in plan if r.get("error") is not None or get(r) is None]
        total = sum(w for w, _ in use)
        out[name] = {"value": (sum(w * v for w, v in use) / total if total else None), "skipped": skipped}
    return out


def _band(v, lo, hi):
    if v is None:
        return NA
    return "ต่ำกว่าเป้าล่าง" if v < lo else ("สูงกว่าเป้าบน" if v > hi else "อยู่ในช่วงเป้า")


QUESTION = ("ตัวเลขข้างบนคือข้อเท็จจริงที่ติดเกณฑ์ — คำถามที่คนต้องตอบ: เหตุของธงนี้ **ชั่วคราวหรือถาวร**? "
            "T3 กำไรปกติ (ตัด one-off) ลดตามไหม หรือ payout ลดแต่กำไรโต · "
            "T5 อุตสาหกรรมตกต่ำ/ถูกรบกวนอยู่ไหม (ไม่มีเลข ต้องหาข้อมูลเอง) · Art กับหัวเป็นคนตัดสิน")


def _scen(r, k):
    """Year-N cell: ข้อมูลไม่พอ when the stock has no scenarios (history < min window), else the number."""
    return fsmod.INSUFFICIENT if not r["scenario_ok"] else _f(r["yoc_scen"][k])


def _rates(r):
    if not r["scenario_ok"]:
        return fsmod.INSUFFICIENT
    return " / ".join(_f(r["rates"][k] * 100) for k in fsmod.SCENARIOS)


def _f(v, nd=1, suffix="%"):
    return NA if v is None else f"{v:,.{nd}f}{suffix}"


def render_report(rows: list, sheets: dict, today: str, cfg: dict, hcfg: dict, refresh: dict = None) -> str:
    year = hcfg.get("yoc_year", 10)
    lo, hi = cfg["yoc_target_low"], cfg["yoc_target_high"]
    limit = cfg["price_stale_days"]
    lines = [f"# เฝ้าหุ้นที่ถือ — {today}", ""]
    stale = [f"{r['symbol']} ({r['age']} วัน)" if r.get("age") is not None else f"{r['symbol']} (ไม่รู้วันที่ราคา)"
             for r in rows if r.get("error") is None and (r.get("age") is None or r["age"] > limit)]
    if stale:
        lines += [f"⏳ ราคาเก่าเกิน {limit} วัน: {', '.join(stale)} — yield/PE/PBV วันนี้ตามราคาเก่านี้ (รันด้วย `--refresh`)", ""]
    if refresh:
        lines += ["รีเฟรชราคา: " + " · ".join(
            f"{s} {i['close']:g}@{i['date']}" if i["ok"] else f"{s} ไม่ได้ ({i['error']})" for s, i in refresh.items()), ""]
    lines += ["> ข้อเท็จจริงให้คนอ่าน — ไม่ใช่คำสั่งทำรายการ · สถานะ: `เปิดทบทวน` = T1 ปันผลต่อหุ้นลดครบ "
              f"{cfg['t1_cut_years']} ปีติด · `เฝ้า` = ติดธงอื่นอย่างน้อย 1 ตัว · `ปกติ` = ไม่ติดธง",
              f"> ปันผลเทียบต้นทุน = ปันผลต่อหุ้นปีบัญชีล่าสุดที่ครบ ÷ ต้นทุน · ปีที่ {year} = ปันผลปีที่ {year} ตามฉากโต ÷ ต้นทุนเดียวกัน (ก้อนที่ถืออยู่)",
              f"> DCA (ขา Niwes เท่านั้น) = ลงเงินเท่ากันทุกเดือน {cfg['dca_years']} ปีแล้วถือต่อ · ราคาโตเท่าปันผล = yield ตอนลงคงที่ · ราคานิ่ง = ลงที่ราคาวันนี้ตลอด · สูตรเต็มในใบข้อเท็จจริง", ""]
    head = ["หุ้น", "ขา", "แผน", "เป้า%", "ราคา", "อายุราคา(วัน)", "yield วันนี้", "ต้นทุนที่ใช้", "กำไร/ขาดทุนเทียบต้นทุน", "ปันผล/ต้นทุน วันนี้",
            "โต/ปี แย่ / กลาง / ดี", f"ปีที่ {year} แย่", f"ปีที่ {year} กลาง", f"ปีที่ {year} ดี",
            f"DCA ปีที่ {year} กลาง: ราคาโตเท่าปันผล", f"DCA ปีที่ {year} กลาง: ราคานิ่ง", "ป้ายราคา", "ผลด่าน", "ธงที่ติด", "สถานะ"]
    body = []
    for r in rows:
        if r.get("error") is not None:
            body.append([r["symbol"], r["leg_text"], r["plan_text"], ("—" if r["target"] is None else _f(r["target"], 2, "")), "ดึงข้อมูลไม่ได้", f"เหตุ: {r['error']}"] + [""] * 13)
            continue
        flags = ", ".join(r["flags"]) or "—"
        if r["missing"]:
            flags += f" (ไม่มีข้อมูล: {', '.join(r['missing'])})"
        hong = r["leg"] == LEG_HONG
        dash = lambda v: "—" if hong else v
        body.append([r["symbol"], r["leg_text"], r["plan_text"], ("—" if r["target"] is None else _f(r["target"], 2, "")), _f(r["price"], 2, ""),
                     NA if r["age"] is None else r["age"], _f(r["yield_today"]), r["cost_text"],
                     ("—" if r["pnl_pct"] is None else f"{r['pnl_pct']:+,.1f}%"), _f(r["yoc_now"]),
                     dash(_rates(r)), dash(_scen(r, "bad")), dash(_scen(r, "mid")), dash(_scen(r, "good")),
                     dash(_f((r.get("dca") or {}).get(fsmod.PRICE_GROWS))), dash(_f((r.get("dca") or {}).get(fsmod.PRICE_FLAT))),
                     dash(r["price_label"]), dash(r["gate"]), dash(flags), r["status"]])
    lines += fsmod._table(head, body)
    lines += ["", "ขาเซียนฮง (TOA SISB SECURE MOSHI) คัดด้วย `scripts\\hong_stage1_scanner.py` ตาม `hong-lens\\CLAUDE.md` — ตารางนี้ไม่ใช้ผลด่าน/ธง T/ฉากปีที่ "
              f"{year} ของนิเวศน์กับขานี้ แสดงแค่ข้อเท็จจริงกลาง ๆ (ราคา · ต้นทุน · กำไร/ขาดทุนเทียบต้นทุน · yield · ปันผลเทียบต้นทุน)"]
    asof = hcfg.get("costs_as_of")
    if asof:
        lines.append(f"ต้นทุนเฉลี่ยในตาราง ณ วันที่ {asof} (จาก config `holdings.costs`)")
    lines += ["", f"## รวมเฉพาะขา Niwes (AMATA BBL TCAP · ถ่วงน้ำหนักตามเป้าสัดส่วน ปรับฐานเป็น 100% · เทียบเป้า {lo:g}–{hi:g}%)", ""]
    roll = portfolio_rollup(rows)
    names = {"now": "วันนี้ (ก้อนที่ถืออยู่)", "bad": f"ก้อนที่ถืออยู่ ปีที่ {year} แย่", "mid": f"ก้อนที่ถืออยู่ ปีที่ {year} กลาง",
             "good": f"ก้อนที่ถืออยู่ ปีที่ {year} ดี", "dca_grows": f"DCA ปีที่ {year} กลาง ราคาโตเท่าปันผล",
             "dca_flat": f"DCA ปีที่ {year} กลาง ราคานิ่ง"}
    prow = []
    for k, label in names.items():
        v = roll[k]
        prow.append([label, _f(v["value"]), _band(v["value"], lo, hi), ", ".join(v["skipped"]) or "—"])
    lines += fsmod._table(["ช่วง", "ปันผล/ต้นทุน ถ่วงน้ำหนัก (เฉพาะขา Niwes)", f"เทียบเป้า {lo:g}–{hi:g}%", "ข้ามตัวที่ข้อมูลไม่พอ/ไม่มีข้อมูล"], prow)
    nocost = [r["symbol"] for r in rows if r.get("error") is None and r["cost_text"] == NO_COST_TEXT]
    if nocost:
        lines += ["", f"ตัวที่ไม่ได้กรอกต้นทุน ({', '.join(nocost)}) ใช้ราคาวันนี้เป็นต้นทุน — ตัวเลขรวมจึงไม่ใช่ผลตอบแทนจริงของ Art จนกว่าจะกรอกต้นทุน (`--cost` หรือ config `holdings.costs`)"]
    flagged = [r for r in rows if r.get("status") in (REVIEW, WATCH)]
    lines += ["", "## ตัวที่สถานะไม่ใช่ปกติ", ""]
    if not flagged:
        lines.append("ไม่มี")
    for r in flagged:
        lines.append(f"### {r['symbol']} — {r['status']}")
        for f in triggered_flags(sheets[r["symbol"]]):
            lines.append(f"- **{f['code']}** {f['name']}: {f['detail']}")
        lines += ["", QUESTION, ""]
    return "\n".join(lines).rstrip() + "\n"


# --- CLI ---

def run(cli_costs=None, refresh=False, out_dir=None, builder=None, refresher=None, today=None, cfg_path=fsmod.CONFIG_PATH):
    """Build rows + report. Returns (report text, rows, sheets, refresh info). Writes nothing."""
    cfg, hcfg = fsmod.load_cfg(cfg_path), load_holdings_cfg(cfg_path)
    entries = holding_entries(hcfg)
    costs = resolve_costs(hcfg.get("costs"), cli_costs)
    info = None
    if refresh:
        if refresher is None:
            import data_adapter
            refresher = data_adapter.refresh_prices
        info = refresher([e["symbol"] for e in entries])
    sheets = collect(entries, costs, builder)
    rows = [summarize(e, sheets[e["symbol"]], costs.get(e["symbol"]), hcfg.get("yoc_year", 10)) for e in entries]
    return render_report(rows, sheets, str(today or date.today()), cfg, hcfg, info), rows, sheets, info


def main(argv=None):
    ap = argparse.ArgumentParser(description="เฝ้าหุ้นที่ถือ")
    ap.add_argument("--cost", action="append", default=[], help="SYM=ราคา (ต้นทุนเฉลี่ย ทับ config)")
    ap.add_argument("--refresh", action="store_true", help="ดึงราคาล่าสุดของหุ้นในรายชื่อก่อนสร้างใบ")
    ap.add_argument("--out", default=str(ROOT / "reports" / "holdings"))
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    text, rows, sheets, _ = run(fsmod.parse_costs(args.cost), args.refresh)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    today = str(date.today())
    (out / f"watch_{today}.md").write_text(text, encoding="utf-8")
    for sym, fs in sheets.items():
        if not fs.get("error"):
            (out / f"{sym}_{fs['date']}.md").write_text(fsmod.render_markdown(fs), encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
