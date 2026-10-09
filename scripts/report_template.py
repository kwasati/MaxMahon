"""Deterministic scan report (no LLM, no score): who passed the gate, by which path, with which flags.

Sections: summary · main-path table · growth-path table · in/out vs previous scan ·
watchlist stocks that failed · closing line. Same input = same output.
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from history_manager import passed_of  # noqa: E402

CLOSING = "รายงานนี้บอกแค่ว่าผ่านด่าน ไม่ใช่คำแนะนำ — ดูต่อด้วย `py scripts\fact_sheet.py <SYM>`"
PATH_LABEL = {"main": "ทางหลัก", "growth": "ทางอนุโลม"}


def _n(v, nd=2, suffix=""):
    return "-" if not isinstance(v, (int, float)) else f"{v:.{nd}f}{suffix}"


def _pct(v, nd=1):
    return "-" if not isinstance(v, (int, float)) else f"{v * 100:.{nd}f}%"


def _bare(sym: str) -> str:
    return sym[:-3] if sym.endswith(".BK") else sym


def _row(cells: list) -> str:
    return "| " + " | ".join(str(c).replace("|", "/") for c in cells) + " |"


def _table(head: list, rows: list) -> str:
    return "\n".join([_row(head), _row(["---"] * len(head))] + [_row(r) for r in rows])


def _common(c: dict) -> list:
    fy = c.get("last_dps_fy")
    return [
        _bare(c["symbol"]) + (" (watchlist)" if c.get("in_watchlist") else ""),
        c.get("name") or "", c.get("sector") or "-", _n(c.get("price")),
        _n(c.get("dividend_yield"), 2, "%"),
        f"{_n(c.get('last_dps'))} (FY{fy})" if fy is not None else "-",
        f"{_pct(c.get('dps_cagr_5y'))} / {_pct(c.get('dps_cagr_10y'))}",
        c.get("dividend_streak") if c.get("dividend_streak") is not None else "-",
        c.get("material_cuts_10y") if c.get("material_cuts_10y") is not None else "-",
        _n(c.get("pe"), 1), _n(c.get("pbv"), 2),
    ]


def _flags(c: dict) -> str:
    return ", ".join(list(c.get("gate_flags") or []) + [f"ข้อมูลขาด:{g}" for g in (c.get("data_gaps") or [])]) or "-"


MAIN_HEAD = ["หุ้น", "ชื่อ", "กลุ่ม", "ราคา", "yield วันนี้", "ปันผลปีครบล่าสุด", "โตปันผล 5ป / 10ป",
             "จ่ายต่อเนื่อง (ปี)", "ลด≥10% ใน 10ปี (ครั้ง)", "PE", "PBV", "ธง"]
GROWTH_HEAD = MAIN_HEAD[:5] + ["yield ที่คาดปีที่ 5", "อัตราโตที่ใช้"] + MAIN_HEAD[5:]


def _main_table(rows: list) -> str:
    if not rows:
        return "_ไม่มี_"
    return _table(MAIN_HEAD, [_common(c) + [_flags(c)] for c in rows])


def _growth_table(rows: list) -> str:
    if not rows:
        return "_ไม่มี_"
    out = []
    for c in rows:
        cells = _common(c)
        out.append(cells[:5] + [_n(c.get("projected_yield_5y"), 2, "%"), _pct(c.get("growth_used"))] + cells[5:] + [_flags(c)])
    return _table(GROWTH_HEAD, out)


def _price_dates(cands: list) -> str:
    dates = sorted({str(c["price_as_of"])[:10] for c in cands if c.get("price_as_of")})
    if not dates:
        return "ไม่มีวันที่ราคา"
    return dates[0] if len(dates) == 1 else f"{dates[0]} ถึง {dates[-1]}"


def stale_price_warning(cands: list, scan_date: str, limit: int) -> str:
    """Top-of-report line when any passer's price is older than `limit` days (same key as the fact sheet)."""
    from datetime import date
    stale = []
    for c in cands:
        pd_ = c.get("price_as_of")
        try:
            age = (date.fromisoformat(str(scan_date)[:10]) - date.fromisoformat(str(pd_)[:10])).days
        except (TypeError, ValueError):
            stale.append(_bare(c["symbol"]))   # no readable price date = can't call it fresh
            continue
        if age > limit:
            stale.append(_bare(c["symbol"]))
    if not stale:
        return ""
    return (f"> ⏳ ราคาเก่าเกิน {limit} วัน {len(stale)} จาก {len(cands)} ตัวที่ผ่านด่าน — yield/PE/PBV ตามราคาเก่า "
            f"(รันสแกนใหม่โดยไม่ใส่ `--no-refresh`): {', '.join(stale[:15])}" + (" ..." if len(stale) > 15 else ""))


def diff_vs_prev(screener_data: dict, prev_scan: dict | None) -> tuple:
    """(new, dropped, has_prev). new = passes now, not in previous. dropped = passed before, scanned now
    and now fails / pending (stocks not scanned this run are not called dropped)."""
    prev = passed_of(prev_scan)
    if not prev:
        return [], [], False
    cands = screener_data.get("candidates") or []
    now = {c["symbol"] for c in cands}
    new = [c for c in cands if c["symbol"] not in prev]
    failed = {s["symbol"]: s for s in (screener_data.get("filtered_out_stocks") or [])}
    pend = {s["symbol"]: s for s in (screener_data.get("pending_candidates") or [])}
    dropped = []
    for sym in sorted(prev):
        if sym in now:
            continue
        if sym in failed:
            dropped.append((sym, "; ".join(failed[sym].get("reasons") or [])))
        elif sym in pend:
            dropped.append((sym, "รอข้อมูล: " + "; ".join(pend[sym].get("reasons") or [])))
    return new, dropped, True


def generate_report_md(screener_data: dict, iso_week: str, scanned_at: datetime, prev_scan: dict | None = None,
                       stale_days: int | None = None) -> str:
    date = screener_data.get("date", scanned_at.strftime("%Y-%m-%d"))
    if stale_days is None:
        from fact_sheet import load_cfg
        stale_days = load_cfg()["price_stale_days"]
    version = screener_data.get("gate_version", "-")
    cands = screener_data.get("candidates") or []
    main = [c for c in cands if c.get("gate_path") == "main"]
    growth = [c for c in cands if c.get("gate_path") != "main"]
    failed = screener_data.get("filtered_out_stocks") or []
    pending = screener_data.get("pending_candidates") or []
    new, dropped, has_prev = diff_vs_prev(screener_data, prev_scan)

    if has_prev:
        new_txt = "\n".join(f"- {_bare(c['symbol'])} ({PATH_LABEL.get(c.get('gate_path'), '-')})" for c in new) or "_ไม่มี_"
        drop_txt = "\n".join(f"- {_bare(s)} — {why}" for s, why in dropped) or "_ไม่มี_"
    else:
        new_txt = drop_txt = "_ไม่มีรอบก่อนให้เทียบ_"

    watch_fail = [s for s in failed if s.get("in_watchlist")]
    watch_txt = "\n".join(f"- **{_bare(s['symbol'])}** — {'; '.join(s.get('reasons') or [])}" for s in watch_fail) or "_ไม่มี_"

    parts = [
        f"---\nagent: Max Mahon v5\ndate: {date}\ntype: scan\niso_week: {iso_week}\n"
        f"scanned_at: {scanned_at.isoformat(timespec='seconds')}\ngate_version: {version}\n---\n",
        f"# รายงานสแกนหุ้นผ่านด่าน (สัปดาห์ {iso_week})\n",
        *([warn] if (warn := stale_price_warning(cands, date, stale_days)) else []),
        "## สรุป\n\n"
        f"- สแกน {screener_data.get('total_scanned', 0)} ตัว · ผ่านด่าน {len(cands)} ตัว "
        f"(ทางหลัก {len(main)} / ทางอนุโลม {len(growth)})\n"
        f"- ตกด่าน {len(failed)} ตัว · รอข้อมูล {len(pending)} ตัว\n"
        f"- วันที่ของราคา: {_price_dates(cands)} · วันที่สแกน {date}",
        "## ผ่านทางหลัก (yield ถึงเกณฑ์)\n\n" + _main_table(main),
        "## ผ่านทางอนุโลม (ปันผลโตจน yield ปีที่ 5 ถึงเกณฑ์)\n\n" + _growth_table(growth),
        "## เข้าใหม่รอบนี้\n\n" + new_txt,
        "## หลุดจากรอบก่อน\n\n" + drop_txt,
        "## หุ้นใน watchlist ที่ตกด่าน\n\n" + watch_txt,
        "---\n" + CLOSING + "\n",
    ]
    return "\n\n".join(parts)


if __name__ == "__main__":
    import json
    from datetime import date
    from history_manager import iso_week_key
    if len(sys.argv) >= 3 and sys.argv[1] == "--test":
        data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        print(generate_report_md(data, iso_week_key(date.today()), datetime.now()))
