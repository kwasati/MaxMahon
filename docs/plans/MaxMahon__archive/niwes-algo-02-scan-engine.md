---
project: MaxMahon
created: 2026-04-21
last_updated: 2026-04-21
status: done
---

# Scan Engine: Kill Claude + Template Report + History v2

> Part 2 of 5 — ถอด anthropic SDK ออกจาก scan.py (pipeline = pure algo), สร้าง deterministic markdown report generator จาก screener output, migrate history.json เป็น v2 schema (portfolio-ready) | Index: niwes-algo-index | Depends on: niwes-algo-01-screener | Parallel-safe with: none (03 + 04 ต้องรอ 02 merge)

## Phase 1: Kill Claude Dependency (keep load_dotenv)
- [x] แก้ `projects/MaxMahon/scripts/scan.py` — ลบเฉพาะ anthropic-specific lines: line 9 `import anthropic`, lines 27-31 `_API_KEY = os.getenv('MAX_ANTHROPIC_API_KEY'); if not _API_KEY: sys.exit(1); _client = anthropic.Anthropic(...)` (ลบเฉพาะ 3 บรรทัดนี้ **เก็บ `load_dotenv(Path('C:/WORKSPACE/.env'))` ไว้** เพราะอาจมี env vars อื่นใช้), ลบ function `run_claude()` (บรรทัด 396-420), ลบ call site line ~456 `raw_text = run_claude(system_prompt, user_prompt)`, ลบ `build_system_prompt()` (line 239-299) + `build_user_prompt()` (line 318-363) ถ้าเป็น Claude-specific — scope: ห้ามแตะ screener data loader + report write I/O — Acceptance: `grep -n '^import anthropic\|_client\|run_claude\|messages.create' projects/MaxMahon/scripts/scan.py` return 0 lines; `load_dotenv` ยังอยู่; `py -c 'import sys; sys.path.insert(0, "projects/MaxMahon/scripts"); import scan'` ไม่มี ImportError

### Reference
```python
# scan.py — lines to DELETE
# line 9
import anthropic  # DELETE

# lines 27-31 (load_dotenv stays, only delete below)
_API_KEY = os.getenv("MAX_ANTHROPIC_API_KEY")  # DELETE
if not _API_KEY:                                # DELETE
    print("MAX_ANTHROPIC_API_KEY not set in C:/WORKSPACE/.env")  # DELETE
    sys.exit(1)                                  # DELETE
_client = anthropic.Anthropic(api_key=_API_KEY)  # DELETE

# line 239-299 build_system_prompt() — DELETE entire function (Claude-specific)
# line 318-363 build_user_prompt() — DELETE entire function (Claude-specific)
# line 396-420 run_claude() — DELETE entire function
# line ~450-456 in main(): system_prompt = build_system_prompt(); user_prompt = build_user_prompt(...); raw_text = run_claude(...) — DELETE 3 lines

# KEEP:
from dotenv import load_dotenv
load_dotenv(Path("C:/WORKSPACE/.env"))  # KEEP — may load MAX_TOKEN or other vars
```

## Phase 2: Template-Based Report Generator
- [x] สร้างไฟล์ `projects/MaxMahon/scripts/report_template.py` — pure Python string formatting (no Jinja2) — exported function `generate_report_md(screener_data: dict, scan_num: int, prev_scan: dict | None = None) -> str` — ต้องสร้าง sections: YAML frontmatter (agent, date, type, scan_num, scoring_version), Header + summary line, Top Picks (sort candidates by score desc top 10 — show symbol/name/sector/score/yield/pe/pbv + signals ต่อ tag กับ narrative จาก patterns.json + reasons top 5), Review Candidates (REVIEW bucket จาก screener_data.review_candidates — symbol + review_reasons), New In Batch (diff symbols ปัจจุบัน top กับ prev_scan.top_candidates), Watchlist Exit Alerts (group by severity high/medium จาก candidates[].exit_triggers), Watch Out (symbols ที่มี DIVIDEND_TRAP หรือ DATA_WARNING), Footer (scoring_version + timestamp) — scope: deterministic, ห้ามสุ่ม ห้ามเรียก LLM — Acceptance: `py projects/MaxMahon/scripts/report_template.py --test projects/MaxMahon/data/screener_2026-04-19.json` output มี section headings ครบ 6 ส่วน + footer scoring_version
- [x] Wire ใน scan.py main() — ระบุแหล่ง prev_scan: `from history_manager import load_history` แล้ว `prev_scan = (load_history().get('scans') or [])[-1] if ...` (ใช้ entry ก่อนหน้าของ history — ก่อน append เข้าใหม่) — เพิ่ม import `from report_template import generate_report_md` — แทนที่ส่วน run_claude call ด้วย `report_md = generate_report_md(screener_data, scan_num, prev_scan)` + `Path(report_path).write_text(report_md, encoding='utf-8')` — scope: ห้ามแก้ screener loader — Acceptance: `py projects/MaxMahon/scripts/run_scan.py` รันจบ → `reports/scan_{today}.md` generated มี 6 sections ตรง template; ไม่มี anthropic import

### Reference
```python
# projects/MaxMahon/scripts/report_template.py — new file
from datetime import datetime
from pathlib import Path
import json

_PATTERNS_PATH = Path(__file__).resolve().parent.parent / "data" / "case_study_patterns.json"
_PATTERNS = json.loads(_PATTERNS_PATH.read_text(encoding="utf-8")) if _PATTERNS_PATH.exists() else {}
_TAG_NARRATIVES = {k: v.get("narrative", "") for k, v in _PATTERNS.items()}
_TAG_NARRATIVES.update({
    "NIWES_5555": "ผ่านเกณฑ์ 5-5-5-5 ครบ (yield≥5 / streak≥5 / EPS 5yr+ / PE≤15 / PBV≤1.5)",
    "BRAND_MOAT": "Brand moat — margin สูง + dividend streak ยาว",
    "STRUCTURAL_MOAT": "Structural moat — utility/transport/telecom scale ใหญ่",
    "GOVT_LOCKIN": "Government lock-in — recurring revenue จากภาครัฐ",
    "HIDDEN_VALUE": "มี holding ที่ตลาดไม่ได้ pricing in",
    "DEEP_VALUE": "PE ≤8 + PBV ≤1.0 — ถูกกว่าค่าเฉลี่ย",
    "QUALITY_DIVIDEND": "yield ≥5% + payout <70% + streak ≥10 ปี",
    "DIVIDEND_TRAP": "ระวัง — yield >8% + ROE declining + payout >100%",
    "DATA_WARNING": "ข้อมูลผิดปกติ — ตรวจสอบก่อนใช้",
    "OVERPRICED": "valuation grade F — แพงกว่าคุณภาพ",
})

def _fm(date, scan_num, version):
    return f"---\nagent: Max Mahon v5\ndate: {date}\ntype: scan\nscan_num: {scan_num}\nscoring_version: {version}\n---\n"

def _top_pick_md(c):
    sig_lines = "\n".join(f"- `{s}` — {_TAG_NARRATIVES.get(s, '')}" for s in c.get("signals", []))
    m = c.get("metrics", {})
    a = c.get("aggregates", {})
    return (f"### {c['symbol']} — {c.get('name','')}\n"
            f"Sector: {c.get('sector','N/A')} · Score {c.get('score',0)}/100\n\n"
            f"- Yield {m.get('dy',0):.2f}% · PE {m.get('pe','-')} · PBV {c.get('pb_ratio', m.get('pb_ratio','-'))} · Streak {a.get('dividend_streak',0)}y\n"
            + sig_lines + "\n\n**Reasons:** " + "; ".join(c.get("reasons", [])[:5]) + "\n")

def _diff_new(current, prev):
    prev_syms = {c.get("symbol") for c in (prev or [])}
    return [c for c in current if c.get("symbol") not in prev_syms]

def generate_report_md(screener_data, scan_num, prev_scan=None):
    date = screener_data.get("date", datetime.now().strftime("%Y-%m-%d"))
    version = screener_data.get("scoring_version", "niwes-dividend-first-v2")
    cands = screener_data.get("candidates", [])
    review = screener_data.get("review_candidates", [])
    top = sorted(cands, key=lambda x: x.get("score", 0), reverse=True)[:10]
    new_in = _diff_new(top, (prev_scan or {}).get("top_candidates", []))
    alerts_high, alerts_med = [], []
    for c in cands:
        for t in c.get("exit_triggers", []):
            entry = f"- **{c['symbol']}** `{t.get('type','')}` — {t.get('reason','')}"
            (alerts_high if t.get("severity") == "high" else alerts_med).append(entry)
    warn = [c for c in cands if any(s in c.get("signals", []) for s in ["DIVIDEND_TRAP", "DATA_WARNING"])]
    parts = [
        _fm(date, scan_num, version),
        f"# รายงานตรวจหุ้น Niwes 5-5-5-5 (รอบที่ {scan_num})\n",
        f"_วันที่ {date} · ผ่าน {len(cands)} · review {len(review)} · new {len(new_in)}_\n",
        "## Top Picks\n\n" + ("\n".join(_top_pick_md(c) for c in top) or "_ไม่มีหุ้นผ่านรอบนี้_"),
        "\n## Review Candidates\n\n" + ("\n".join(f"- **{r['symbol']}** ({r.get('sector','')}) — {'; '.join(r.get('review_reasons', []))}" for r in review) or "_ไม่มี_"),
        "\n## New In Batch\n\n" + ("\n".join(f"- {c['symbol']}" for c in new_in) or "_ไม่มี_"),
        "\n## Watchlist Exit Alerts\n\n**High:**\n" + ("\n".join(alerts_high) or "_ไม่มี_") + "\n\n**Medium:**\n" + ("\n".join(alerts_med) or "_ไม่มี_"),
        "\n## Watch Out\n\n" + ("\n".join(f"- **{c['symbol']}** — {', '.join(c.get('signals', []))}" for c in warn) or "_ไม่มี_"),
        f"\n---\n_Generated by Max Mahon algo · scoring_version={version} · {datetime.now().isoformat(timespec='seconds')}_\n",
    ]
    return "\n".join(parts)

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "--test":
        print(generate_report_md(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")), 0))
```

```python
# scan.py main() — wire
from report_template import generate_report_md
from history_manager import load_history

hist = load_history()
prev_scan = (hist.get("scans") or [None])[-1] if hist.get("scans") else None
report_md = generate_report_md(screener_data, scan_num, prev_scan)
Path(report_path).write_text(report_md, encoding="utf-8")
```

## Phase 3: History v2 Schema + Migration
- [x] สร้างไฟล์ `projects/MaxMahon/scripts/history_manager.py` — exports: `load_history() -> dict` (อ่าน data/history.json return `{'scans':[]}` ถ้าไม่มี), `build_v2_entry(screener_data, scan_num, report_filename) -> dict` (สร้าง entry มี 10 keys: num/date/counts/summary/report/scoring_version/top_candidates[]/watchlist_status[]/entry_thesis{}/dividend_paid_since_entry{}/price_snapshot{} ตาม schema ใน reference), `append_scan_v2(entry, history=None) -> dict` (append + atomic write) — scope: encapsulate history I/O — Acceptance: `build_v2_entry({'candidates':[sample], 'scoring_version':'niwes-dividend-first-v2'}, 99, 'scan_x.md')` return dict มี 10 keys ตรง schema
- [x] สร้างไฟล์ `projects/MaxMahon/scripts/migrate_history_v2.py` — one-off idempotent migration: backup เป็น data/history.json.v1.bak (ถ้ายังไม่มี), อ่าน history.json, เติม v2 defaults สำหรับ entries ที่ไม่มี keys (top_candidates=[], watchlist_status=[], entry_thesis={}, dividend_paid_since_entry={}, price_snapshot={}, scoring_version='niwes-dividend-first-v1-legacy'), write back — scope: รันซ้ำได้ (check key มีอยู่ก่อนเติม) — Acceptance: `py projects/MaxMahon/scripts/migrate_history_v2.py` → all entries มี 10 keys + backup file มี
- [ ] Wire ใน scan.py main() แทน save_history_entry เดิม — `from history_manager import build_v2_entry, append_scan_v2, load_history` — `entry = build_v2_entry(screener_data, scan_num, report_filename); append_scan_v2(entry)` (หรือ pass loaded history เพื่อ avoid re-read) — scope: ห้ามเขียน history.json จากที่อื่น — Acceptance: scan รอบใหม่ → history.json append entry ใหม่มี scoring_version='niwes-dividend-first-v2' + top_candidates populated

### Reference
```python
# projects/MaxMahon/scripts/history_manager.py — new file
import json
from pathlib import Path
from datetime import datetime

_HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "history.json"

def load_history() -> dict:
    if not _HISTORY_PATH.exists():
        return {"scans": []}
    try:
        return json.loads(_HISTORY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"scans": []}

def build_v2_entry(screener_data: dict, scan_num: int, report_filename: str) -> dict:
    cands = screener_data.get("candidates", [])
    review = screener_data.get("review_candidates", [])
    top = sorted(cands, key=lambda x: x.get("score", 0), reverse=True)[:15]
    top_candidates = [{
        "symbol": c["symbol"],
        "score": c.get("score", 0),
        "yield": (c.get("metrics") or {}).get("dy"),
        "pe": (c.get("metrics") or {}).get("pe"),
        "pbv": (c.get("metrics") or {}).get("pb_ratio") or c.get("pb_ratio"),
        "tags": c.get("signals", []),
    } for c in top]
    watchlist_status = [{
        "symbol": c["symbol"],
        "status": "HELD" if "NIWES_5555" in c.get("signals", []) else "REVIEW",
        "triggers": c.get("exit_triggers", []),
    } for c in cands if c.get("in_watchlist")]
    entry_thesis = {
        c["symbol"]: {
            "sector": c.get("sector"),
            "pe": (c.get("metrics") or {}).get("pe"),
            "pbv": (c.get("metrics") or {}).get("pb_ratio"),
            "yield": (c.get("metrics") or {}).get("dy"),
            "streak": (c.get("aggregates") or {}).get("dividend_streak"),
            "tags": c.get("signals", []),
        } for c in cands if "NIWES_5555" in c.get("signals", [])
    }
    price_snapshot = {
        c["symbol"]: {"price": (c.get("metrics") or {}).get("price"), "date": screener_data.get("date")}
        for c in top
    }
    return {
        "num": scan_num,
        "date": datetime.now().isoformat(timespec="seconds"),
        "counts": {
            "scanned": screener_data.get("total_scanned", 0),
            "passed": len(cands),
            "review": len(review),
            "new": screener_data.get("new_discoveries", 0),
            "filtered": screener_data.get("filtered_out", 0),
        },
        "summary": ", ".join(c["symbol"] for c in top[:3]) + f" · +{screener_data.get('new_discoveries', 0)} ใหม่",
        "report": report_filename,
        "scoring_version": screener_data.get("scoring_version", "niwes-dividend-first-v2"),
        "top_candidates": top_candidates,
        "watchlist_status": watchlist_status,
        "entry_thesis": entry_thesis,
        "dividend_paid_since_entry": {},
        "price_snapshot": price_snapshot,
    }

def append_scan_v2(entry: dict, history: dict | None = None) -> dict:
    hist = history or load_history()
    hist.setdefault("scans", []).append(entry)
    _HISTORY_PATH.write_text(json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8")
    return hist
```

```python
# projects/MaxMahon/scripts/migrate_history_v2.py — one-off
import json, shutil
from pathlib import Path
_HIST = Path(__file__).resolve().parent.parent / "data" / "history.json"
_BAK = _HIST.with_suffix(".json.v1.bak")
_V2 = {"top_candidates": [], "watchlist_status": [], "entry_thesis": {}, "dividend_paid_since_entry": {}, "price_snapshot": {}, "scoring_version": "niwes-dividend-first-v1-legacy"}

def main():
    if not _HIST.exists():
        print("no history.json"); return
    if not _BAK.exists(): shutil.copy2(_HIST, _BAK)
    data = json.loads(_HIST.read_text(encoding="utf-8"))
    changed = 0
    for entry in data.get("scans", []):
        for k, v in _V2.items():
            if k not in entry:
                entry[k] = list(v) if isinstance(v, list) else (dict(v) if isinstance(v, dict) else v)
                changed += 1
    _HIST.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"migrated {changed} fields across {len(data.get('scans', []))} entries")

if __name__ == "__main__": main()
```
