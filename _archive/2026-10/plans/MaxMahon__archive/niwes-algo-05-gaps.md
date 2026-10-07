---
project: MaxMahon
created: 2026-04-21
last_updated: 2026-04-21
status: done
---

# Gaps Fix: Safety + Completeness + Features (delisted-safe, REVIEW tab, Telegram, TTL, Transactions, Integration Test)

> Part 5 of 5 — rethinking gaps: MUST (delisted-safe fetch / REVIEW UI tab / Claude cache TTL 7d / Telegram exit alert / integration test) + SHOULD (sector spread / transactions+P&L / 3 more patterns / VN pattern disable / MVP marker). NOTE: auto_adjust=False + price_avg cache merged into plan 01 Phase 1 task 3 | Index: niwes-algo-index | Depends on: niwes-algo-03-server, niwes-algo-04-ui | Parallel-safe with: none (last polish pass)

## Phase 1: Data Safety + Patterns Expansion
- [x] แก้ `projects/MaxMahon/scripts/fetch_data.py` — สร้าง wrapper `fetch_multi_year_safe(symbol: str) -> dict` ครอบ `fetch_multi_year(symbol)` (existing function ที่ line 393) ด้วย try/except; ถ้า fetch fail → return `{"symbol": symbol, "delisted": True, "error": str(e)}` (skip enrichment, ไม่ raise) + log warning; ใน main loop / run_scan.py / scan.py caller เปลี่ยนจาก `fetch_multi_year(sym)` เป็น `fetch_multi_year_safe(sym)` + เพิ่ม check: `if stock.get('delisted'): delisted_log.append(sym); continue` — scope: safety wrapper เฉพาะ, ไม่เปลี่ยน happy path logic — Acceptance: รัน `py -c 'from scripts.fetch_data import fetch_multi_year_safe; r = fetch_multi_year_safe("FAKE.BK"); assert r.get("delisted") == True; print("ok", r.get("error"))'` ไม่ throw exception + print 'ok' + error message; scan full universe ที่มี symbol invalid 1 ตัว → scan completes ไม่ crash
- [x] แก้ `projects/MaxMahon/data/case_study_patterns.json` (created by plan 01 Phase 1 task 1) — **ADDITIVE edit: เพิ่ม 3 top-level keys ใหม่** (UTILITY_DEFENSIVE, HOSPITAL_AGING, F&B_CONSUMER_BRAND) ตาม reference + **mark existing key `VIETNAM_GROWTH_EXPOSURE` ให้มี `"disabled": true, "disabled_reason": "data_adapter ยังไม่รองรับ VN data — enable หลังเพิ่ม VN source"`** (ห้ามเขียนทับ entry อื่น, ห้ามลบเก่า); detector ใน plan 01 Phase 2 รองรับ `p.get('disabled')` แล้ว — scope: JSON additive edit, ไม่แตะ detector code — Acceptance: `py -c 'import json; d=json.load(open("projects/MaxMahon/data/case_study_patterns.json")); assert len(d)==8; assert d["VIETNAM_GROWTH_EXPOSURE"]["disabled"]==True; assert "UTILITY_DEFENSIVE" in d and "HOSPITAL_AGING" in d and "F&B_CONSUMER_BRAND" in d; print("ok")'`

### Reference
```python
# projects/MaxMahon/scripts/fetch_data.py — add near fetch_multi_year (line 393)
import logging
logger = logging.getLogger(__name__)


def fetch_multi_year_safe(symbol: str) -> dict:
    """Wrap fetch_multi_year with try/except.
    Returns {'symbol', 'delisted': True, 'error': str} if fetch fails.
    Caller must check .get('delisted') before processing.
    """
    try:
        return fetch_multi_year(symbol)
    except Exception as e:
        logger.warning(f"fetch failed for {symbol}: {e}")
        return {"symbol": symbol, "delisted": True, "error": str(e)}


# caller (wherever fetch_multi_year is used — grep first):
delisted_log: list[str] = []
for sym in universe:
    stock = fetch_multi_year_safe(sym)
    if stock.get("delisted"):
        delisted_log.append(sym)
        logger.info(f"skip delisted {sym}")
        continue
    # ... existing per-stock processing ...
```

```json
// projects/MaxMahon/data/case_study_patterns.json — ADDITIVE edit
// 1) APPEND 3 new top-level keys (don't touch others)
// 2) ADD fields disabled=true + disabled_reason to existing VIETNAM_GROWTH_EXPOSURE key
// final file should have 8 keys total (5 from plan 01 + 3 new)

{
  // ... keep RETAIL_DEFENSIVE_MOAT, BANK_VALUE_PBV1, HOLDING_CO_HIDDEN, ENERGY_CYCLICAL_EXIT as-is ...

  "VIETNAM_GROWTH_EXPOSURE": {
    "tag": "VIETNAM_GROWTH_EXPOSURE",
    "source": "docs/niwes/10-case-fpt.md",
    "rules": { "country": "VN", "sector_keywords": ["technology","it","communications"], "market_cap_min": 50000000000, "roe_3yr_avg_min": 0.10, "dividend_yield_min": 3 },
    "narrative": "Vietnam tech scale 50B+ ROE 10%+ (แบบ FPT)",
    "disabled": true,
    "disabled_reason": "data_adapter ยังไม่รองรับ VN data — enable หลังเพิ่ม VN data source"
  },

  "UTILITY_DEFENSIVE": {
    "tag": "UTILITY_DEFENSIVE",
    "source": "docs/niwes/03-philosophy.md",
    "rules": { "sector_keywords": ["utilit","power","infrastructure","energy"], "market_cap_min": 30000000000, "dividend_streak_min": 10, "dividend_yield_min": 4 },
    "narrative": "Utility/infra defensive — regulated revenue + streak ยาว (แบบ GULF/RATCH/EGCO)"
  },

  "HOSPITAL_AGING": {
    "tag": "HOSPITAL_AGING",
    "source": "docs/niwes/03-philosophy.md",
    "rules": { "sector_keywords": ["health","hospital","medical"], "market_cap_min": 10000000000, "roe_3yr_avg_min": 0.10, "dividend_streak_min": 5 },
    "narrative": "Hospital — aging demographics ผลดี long-term (แบบ BDMS/BH)"
  },

  "F&B_CONSUMER_BRAND": {
    "tag": "F&B_CONSUMER_BRAND",
    "source": "docs/niwes/03-philosophy.md",
    "rules": { "sector_keywords": ["food","beverage","agro-industry"], "market_cap_min": 10000000000, "dividend_streak_min": 5, "dividend_yield_min": 3 },
    "narrative": "F&B brand — consumer staples, pricing power (แบบ CBG/OSP/TU/MINT)"
  }
}
```

## Phase 2: Sector Spread + REVIEW UI Tab
- [x] แก้ `projects/MaxMahon/scripts/report_template.py` (created by plan 02 Phase 2) — เพิ่ม helper `_fmt_sector_spread(top_10) -> str` + insert section 'Sector Spread' หลัง Top Picks ใน `generate_report_md()` parts list — logic: Counter group by sector, show `- {sector}: {cnt}/{total} ({pct}%)` + flag `⚠ over-concentrated` ถ้า pct > 40 — scope: add-only ไม่แก้ section อื่น — Acceptance: run `generate_report_md(sample)` → report มี heading `## Sector Spread` + bullets sector count; ถ้า 5+ ตัวเป็น retail → มี warning emoji
- [x] แก้ `projects/MaxMahon/web/index.html` — เพิ่ม tab 'Review' ใน section nav (ใกล้ `data-tab="filtered"` line 49): `<button class="tab" data-tab="review" data-type="stock">รีวิว</button>` + สร้าง page-panel ใหม่ (insert **ก่อน** `<section class="page-panel" id="page-history">` line 152) โดย structure ตาม reference (reuse `.stock-list-container` + `.stock-table`) — scope: HTML additive only — Acceptance: nav มี tab 'รีวิว' + panel id='page-review' อยู่ก่อน page-history + empty tbody `#review-list`
- [x] แก้ `projects/MaxMahon/web/app.js` — เพิ่ม function `reviewRowHTML(r)` + `loadReviewTab()` — fetch existing `/api/screener` (server/app.py:183), extract `data.review_candidates[]`, render ผ่าน `reviewRowHTML` เข้า `#review-list`; update count chip `.review-count` — ต่อด้วย wire เข้า tab click handler (where existing tabs like 'filtered' dispatch) เพิ่ม case `'review': loadReviewTab();` — scope: add-only ไม่แก้ tab อื่น — Acceptance: click tab 'รีวิว' → fetch 1 call ไป `/api/screener` → tbody populate ด้วย review candidates + badge 'REVIEW' สีเหลือง; ถ้า empty → แสดง 'ไม่มี review candidates'
- [x] เพิ่ม CSS ใน `projects/MaxMahon/web/style.css`: `.badge-review { background: #b45309; color: #f4f0e6; padding: 1px 6px; font-size: 0.75em; border-radius: 2px; }` + `.review-reasons { color: #b45309; font-size: 0.9em; }` — scope: add-only, reuse editorial palette — Acceptance: inspect row → badge-review สีอำพัน, review_reasons text สีเดียวกันขนาดเล็ก

### Reference
```python
# report_template.py — add sector spread helper
from collections import Counter

def _fmt_sector_spread(top: list) -> str:
    if not top: return "_ไม่มี_"
    sectors = Counter(c.get("sector", "Unknown") for c in top)
    total = len(top)
    lines = []
    for sector, cnt in sectors.most_common():
        pct = cnt / total * 100
        warn = " ⚠ over-concentrated" if pct > 40 else ""
        lines.append(f"- {sector}: {cnt}/{total} ({pct:.0f}%){warn}")
    return "\n".join(lines)

# in generate_report_md() parts list, insert after Top Picks, before Review Candidates:
#   "\n## Sector Spread\n\n" + _fmt_sector_spread(top),
```

```html
<!-- index.html — insert tab button near line 49 (after data-tab="filtered") -->
<button class="tab" data-tab="filtered" data-type="stock">หลุดรอบ</button>
<button class="tab" data-tab="review" data-type="stock">รีวิว</button>  <!-- NEW -->

<!-- insert BEFORE <section class="page-panel" id="page-history"> (line 152) -->
<section class="page-panel" id="page-review">
  <div class="stock-section">
    <div class="section-head-bar">
      <span class="section-num mono">№REV</span>
      <h3 class="serif section-title">รีวิว (3-tier REVIEW bucket)</h3>
      <span class="review-count mono">— REVIEW</span>
    </div>
    <div class="stock-list-container">
      <table class="stock-table">
        <thead><tr><th>Stock</th><th>Sector</th><th>Review Reasons</th><th>Yield</th><th>PE</th><th>Streak</th></tr></thead>
        <tbody id="review-list"><tr><td colspan="6"><div class="loading-state">—</div></td></tr></tbody>
      </table>
    </div>
  </div>
</section>
```

```javascript
// app.js — add functions + tab wire
function reviewRowHTML(r) {
  const m = r.basic_metrics || {};
  return `<tr data-sym="${escapeHtml(r.symbol)}">
    <td><strong>${escapeHtml(r.symbol)}</strong> ${escapeHtml(r.name || '')}</td>
    <td>${escapeHtml(r.sector || '-')}</td>
    <td class="review-reasons">${(r.review_reasons || []).map(escapeHtml).join('; ')} <span class="badge-review">REVIEW</span></td>
    <td>${m.dy != null ? m.dy.toFixed(1) + '%' : '-'}</td>
    <td>${m.pe != null ? m.pe.toFixed(1) : '-'}</td>
    <td>${m.streak ?? '-'}</td>
  </tr>`;
}

async function loadReviewTab() {
  const res = await fetch(`${API}/api/screener`);
  const data = await res.json();
  const reviews = data.review_candidates || [];
  document.getElementById('review-list').innerHTML =
    reviews.map(reviewRowHTML).join('') ||
    '<tr><td colspan="6"><em>ไม่มี review candidates</em></td></tr>';
  document.querySelector('.review-count').textContent = `${reviews.length} REVIEW`;
}
// in existing tab click dispatch: case 'review': loadReviewTab(); break;
```

## Phase 3: Claude Cache TTL + Telegram Exit Alert
- [x] แก้ `projects/MaxMahon/server/app.py` GET `/api/stock/{symbol}/analysis` endpoint (created by plan 03 Phase 1) — หลัง load cache file check age: `age = datetime.now() - datetime.fromisoformat(cached.get('analyzed_at', ''))`; ถ้า `age > timedelta(days=7)` → raise `HTTPException(404, detail={status:'stale_cache', hint:'cache older than 7d — POST /analyze to refresh', cached_at: cached.get('analyzed_at'), age_days: age.days})` — scope: ไม่ auto-refresh, UI handle 404 stale → popup ถาม — Acceptance: สร้าง cache file มือด้วย `analyzed_at` = 8 วันก่อน → curl GET → 404 + response body status='stale_cache' + age_days=8
- [x] แก้ `projects/MaxMahon/web/app.js` function `triggerAnalysis` (created by plan 04 Phase 4) — แก้ branch `if (res.status === 404)` ให้ parse error detail; ถ้า `detail.status === 'stale_cache'` → ถาม `confirm('Cache อายุ ${d.age_days} วัน — วิเคราะห์ใหม่? (ใช้ API credit)')` → ถ้า user OK → POST /analyze ต่อ (เดิม); ถ้า cancel → แสดง placeholder + button 'Refresh' (ถ้า Karl อยากใหม่ทีหลัง) + note 'Cache อายุ N วัน ({cached_at})' — scope: UI flow only — Acceptance: stale cache → dialog ปรากฏ → OK → trigger POST; cancel → button 'Refresh' + note age
- [x] สร้างไฟล์ `projects/MaxMahon/scripts/telegram_alert.py` — import requests + load `.env` root; function `send_exit_alert(high_triggers: list[dict]) -> bool` รับ `[{symbol, type, reason, severity}]` format message Thai + POST `https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage` (ใช้ env vars **`TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`** ที่มีอยู่จริงใน `.env` บรรทัด 72-73 ไม่ใช่ _KARL_ prefix) — scope: error-safe (fail silent + log); cap message 15 triggers กัน Telegram length limit — Acceptance: mock `send_exit_alert([{symbol:'CPALL.BK', type:'VALUATION_BUBBLE', reason:'...', severity:'high'}])` → Telegram ได้ข้อความ + function return True
- [x] Wire ใน `projects/MaxMahon/scripts/scan.py` main() — หลัง history append + report written: collect `high_triggers = [{**t, 'symbol': c['symbol']} for c in candidates for t in c.get('exit_triggers', []) if t.get('severity') == 'high']` + ถ้า `len(high_triggers) > 0` → `from telegram_alert import send_exit_alert; send_exit_alert(high_triggers)` — scope: notification-only, ไม่ block scan ถ้า fail — Acceptance: inject candidate ที่มี high-severity trigger + run scan → Telegram ได้ alert message; ถ้าไม่มี high triggers → ไม่ส่ง

### Reference
```python
# server/app.py GET /analysis — add TTL check
from datetime import datetime, timedelta

_CACHE_TTL_DAYS = 7

@app.get("/api/stock/{symbol}/analysis")
async def get_cached_analysis(symbol: str):
    cache_file = _ANALYSIS_CACHE_DIR / f"{symbol}.json"
    if not cache_file.exists():
        raise HTTPException(404, detail={"status": "no_cache", "hint": "POST /analyze to generate"})
    cached = json.loads(cache_file.read_text(encoding="utf-8"))
    try:
        age = datetime.now() - datetime.fromisoformat(cached.get("analyzed_at", ""))
    except Exception:
        age = timedelta(days=999)
    if age > timedelta(days=_CACHE_TTL_DAYS):
        raise HTTPException(404, detail={
            "status": "stale_cache",
            "hint": f"cache older than {_CACHE_TTL_DAYS}d — POST /analyze to refresh",
            "cached_at": cached.get("analyzed_at"),
            "age_days": age.days,
        })
    return cached
```

```javascript
// app.js triggerAnalysis — 404 stale handling
if (res.status === 404) {
  let err = {};
  try { err = await res.json(); } catch {}
  const d = err.detail || err;
  if (d.status === 'stale_cache') {
    const ok = confirm(`Cache อายุ ${d.age_days} วัน — วิเคราะห์ใหม่? (ใช้ API credit)`);
    if (!ok) {
      const section = document.getElementById('analysis-section');
      section.innerHTML = `<p class="muted">Cache อายุ ${d.age_days} วัน (${d.cached_at}) — กด 'Refresh' เพื่อใช้ของใหม่</p><button id="analyze-btn" class="btn-primary">Refresh</button>`;
      document.getElementById('analyze-btn').addEventListener('click', () => triggerAnalysis(symbol));
      return;
    }
  }
  res = await fetch(`${API}/api/stock/${encodeURIComponent(symbol)}/analyze`, { method: 'POST' });
  if (!res.ok) throw new Error('analyze failed: ' + res.status);
  data = await res.json();
} else if (res.ok) {
  data = await res.json();
} else { throw new Error('fetch: ' + res.status); }
```

```python
# projects/MaxMahon/scripts/telegram_alert.py — new file
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path("C:/WORKSPACE/.env"))

# NOTE: env vars ที่มีใน .env ROOT (line 72-73) — ไม่มี prefix _KARL_
_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_exit_alert(high_triggers: list[dict]) -> bool:
    if not _TOKEN or not _CHAT_ID or not high_triggers:
        return False
    lines = [f"⚠ Max Mahon Exit Alert ({len(high_triggers)} high severity)", ""]
    for t in high_triggers[:15]:  # cap — Telegram 4096 char limit
        lines.append(f"• {t.get('symbol', '?')} ({t.get('type', '?')}): {t.get('reason', '?')[:120]}")
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
```

```python
# scan.py main — wire after history append
from telegram_alert import send_exit_alert
high_triggers = [
    {**t, "symbol": c["symbol"]}
    for c in candidates
    for t in c.get("exit_triggers", [])
    if t.get("severity") == "high"
]
if high_triggers:
    send_exit_alert(high_triggers)
```

## Phase 4: Transactions + P&L + Integration Test
- [x] Extend `projects/MaxMahon/user_data.json` schema — เพิ่ม top-level key `transactions: []` (default empty list); schema per entry: `{id: uuid, symbol, date: 'YYYY-MM-DD', type: 'BUY'|'SELL', price: float, qty: float, note: str|null}`; ตรวจสอบ loader/saver ใน server/app.py preserve field นี้ (ตอนนี้มี endpoints ที่โหลด/เซฟ user_data อยู่แล้ว — ต้อง re-read หลัง update เพื่อกัน race) — scope: data schema only — Acceptance: manual edit user_data.json เพิ่ม transactions entry 1 รายการ → reload server → GET `/api/user` ได้ field `transactions` กลับมา
- [x] เพิ่ม endpoints ใน `projects/MaxMahon/server/app.py`: `POST /api/portfolio/transactions` (body: TransactionIn pydantic model — server/app.py มี pydantic อยู่แล้วที่ line 27 + class patterns ที่ line 480/1235/1289/1305 ใช้เป็น reference) gen uuid + append + save; `DELETE /api/portfolio/transactions/{tx_id}`; `GET /api/portfolio/transactions?symbol=XXX` (filter optional) — scope: CRUD only — Acceptance: curl POST body JSON → 200 + entry สร้าง + id generated; curl GET → array มี entry ใหม่; curl DELETE id → array ไม่มี entry นั้น
- [x] เพิ่ม endpoint `GET /api/portfolio/pnl` ใน server/app.py — ใช้ helper `_latest_screener()` (created by plan 03 Phase 2) — compute per symbol: cost_basis = sum(BUY price*qty) - sum(SELL price*qty); qty = sum(BUY qty) - sum(SELL qty); avg_cost = cost/qty; current_price ดึงจาก screener candidates/review/filtered buckets (first match); market_value = current_price*qty; unrealized_pnl = mv - cost; total summary — scope: compute only, ไม่ fetch live price — Acceptance: user_data มี 2 BUY CPALL@60 qty100 + 1 SELL qty30 → GET /pnl → position CPALL qty=70 + cost_basis + unrealized_pct
- [x] เพิ่ม UI ใน `projects/MaxMahon/web/` — **[1] Transaction form** วาง **หลัง `#exit-status-section`** ใน detail panel aside (plan 04 Phase 3 สร้าง section นั้น): `<section id="tx-section">` + form BUY/SELL select + qty + price + date + note + submit → POST `/api/portfolio/transactions`; **[2] Portfolio P&L widget** วาง **ก่อน `<aside class="stats-panel" id="summary-row">`** ใน `#page-home` (index.html line 75): `<section id="portfolio-pnl">` fetch `/api/portfolio/pnl` → table positions (symbol/qty/avg_cost/current/mv/pnl/pct) + total row — scope: minimal UI, reuse existing form/table CSS — Acceptance: submit BUY CPALL @60 qty100 via form → transaction list updated + Home widget แสดง position CPALL + unrealized pct; ถ้า user_data.transactions empty → widget แสดง 'ยังไม่มี transactions'
- [x] สร้างไฟล์ `projects/MaxMahon/scripts/integration_test.py` — curated 10 symbols: CPALL.BK, TCAP.BK, QH.BK, ADVANC.BK, PTT.BK, BDMS.BK, SCB.BK, GULF.BK, CBG.BK, DITTO.BK — รัน per-symbol: `stock = fetch_multi_year_safe(sym)` (use safe wrapper from Phase 1) + `stock['_hidden_holdings'] = check_hidden_value(sym)` + `signals = assign_signals(stock, 0)` + `status, reasons, _ = hard_filter(stock)` + collect results; verify: CPALL→RETAIL_DEFENSIVE_MOAT, TCAP→BANK_VALUE_PBV1, GULF→UTILITY_DEFENSIVE, BDMS→HOSPITAL_AGING, CBG→F&B_CONSUMER_BRAND (5 tag assertions); benchmark total < 5 min — scope: smoke test ก่อน full scan — Acceptance: `py projects/MaxMahon/scripts/integration_test.py` pass 5/5 tag assertions + runtime < 300s + print summary

### Reference
```json
// user_data.json — extend schema
{
  "watchlist": ["CPALL.BK"],
  "blacklist": [],
  "notes": {},
  "lists": {},
  "transactions": [
    {"id": "uuid-here", "symbol": "CPALL.BK", "date": "2026-04-21", "type": "BUY", "price": 60.5, "qty": 100, "note": null}
  ]
}
```

```python
# server/app.py — transactions + pnl endpoints
import uuid
from datetime import datetime
from pydantic import BaseModel  # already imported at line 27


class TransactionIn(BaseModel):
    symbol: str
    date: str
    type: str  # 'BUY' | 'SELL'
    price: float
    qty: float
    note: str | None = None


_USER_DATA_PATH = Path(__file__).resolve().parent.parent / "user_data.json"


def _load_user_data() -> dict:
    return json.loads(_USER_DATA_PATH.read_text(encoding="utf-8"))


def _save_user_data(data: dict):
    _USER_DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


@app.post("/api/portfolio/transactions")
async def add_transaction(tx: TransactionIn):
    data = _load_user_data()
    data.setdefault("transactions", [])
    entry = {"id": str(uuid.uuid4()), **tx.model_dump()}
    data["transactions"].append(entry)
    _save_user_data(data)
    return entry


@app.delete("/api/portfolio/transactions/{tx_id}")
async def delete_transaction(tx_id: str):
    data = _load_user_data()
    data["transactions"] = [t for t in data.get("transactions", []) if t.get("id") != tx_id]
    _save_user_data(data)
    return {"deleted": tx_id}


@app.get("/api/portfolio/transactions")
async def list_transactions(symbol: str | None = None):
    txs = _load_user_data().get("transactions", [])
    if symbol:
        txs = [t for t in txs if t.get("symbol") == symbol]
    return {"transactions": txs}


@app.get("/api/portfolio/pnl")
async def get_pnl():
    txs = _load_user_data().get("transactions", [])
    by_sym: dict[str, list] = {}
    for t in txs:
        by_sym.setdefault(t["symbol"], []).append(t)
    screener = _latest_screener()
    all_entries = (screener.get("candidates", []) + screener.get("review_candidates", [])
                   + screener.get("filtered_out_stocks", []))
    price_map = {e["symbol"]: (e.get("metrics") or {}).get("price") or e.get("price")
                 for e in all_entries if e.get("symbol")}
    positions = []
    total_cost = total_mv = 0.0
    for sym, ts in by_sym.items():
        buys = [t for t in ts if t["type"] == "BUY"]
        sells = [t for t in ts if t["type"] == "SELL"]
        qty = sum(t["qty"] for t in buys) - sum(t["qty"] for t in sells)
        if qty <= 0:
            continue
        cost = sum(t["price"] * t["qty"] for t in buys) - sum(t["price"] * t["qty"] for t in sells)
        avg = cost / qty if qty else 0
        cur_price = price_map.get(sym)
        mv = cur_price * qty if cur_price else None
        pnl = (mv - cost) if mv is not None else None
        pct = (pnl / cost * 100) if (pnl is not None and cost) else None
        positions.append({"symbol": sym, "qty": qty, "cost_basis": cost, "avg_cost": avg,
                          "current_price": cur_price, "market_value": mv,
                          "unrealized_pnl": pnl, "unrealized_pct": pct})
        total_cost += cost
        if mv: total_mv += mv
    return {"positions": positions,
            "total": {"cost": total_cost, "market_value": total_mv,
                      "unrealized_pnl": total_mv - total_cost if total_mv else None,
                      "unrealized_pct": ((total_mv - total_cost) / total_cost * 100) if total_cost else None}}
```

```python
# projects/MaxMahon/scripts/integration_test.py — new file
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_data import fetch_multi_year_safe  # NOTE: use safe wrapper from Phase 1 task 1
from screen_stocks import assign_signals, hard_filter
from data_adapter import check_hidden_value

CURATED = ["CPALL.BK", "TCAP.BK", "QH.BK", "ADVANC.BK", "PTT.BK",
           "BDMS.BK", "SCB.BK", "GULF.BK", "CBG.BK", "DITTO.BK"]
EXPECTED_TAGS = {
    "CPALL.BK": "RETAIL_DEFENSIVE_MOAT",
    "TCAP.BK": "BANK_VALUE_PBV1",
    "GULF.BK": "UTILITY_DEFENSIVE",
    "BDMS.BK": "HOSPITAL_AGING",
    "CBG.BK": "F&B_CONSUMER_BRAND",
}


def main():
    t0 = time.time()
    results = {}
    for sym in CURATED:
        stock = fetch_multi_year_safe(sym)
        if stock.get("delisted"):
            results[sym] = {"delisted": True, "error": stock.get("error")}
            continue
        stock["_hidden_holdings"] = check_hidden_value(sym)
        signals = assign_signals(stock, 0)
        status, reasons, _ = hard_filter(stock)
        results[sym] = {"signals": signals, "status": status}

    elapsed = time.time() - t0
    print(f"\n=== Integration Test ({elapsed:.1f}s) ===")
    passed = failed = 0
    for sym, exp_tag in EXPECTED_TAGS.items():
        sigs = results.get(sym, {}).get("signals", [])
        ok = exp_tag in sigs
        print(f"{'ok' if ok else 'FAIL'} {sym}: expect {exp_tag} | got {sigs}")
        if ok: passed += 1
        else: failed += 1

    print(f"\n{passed}/{passed + failed} tag assertions pass · runtime {elapsed:.1f}s")
    assert elapsed < 300, f"runtime {elapsed:.1f}s exceeds 5 min budget"
    assert failed == 0, f"{failed} tag assertions failed"


if __name__ == "__main__":
    main()
```
