---
project: MaxMahon
created: 2026-04-21
last_updated: 2026-04-21
status: done
---

# Screener: Case Study Detectors + Moat Tags + 3-tier Thresholds + Exit Baseline Wire

> Part 1 of 5 — Foundation ของ Niwes algo framework: enrich data pipeline (price_avg with auto_adjust=False + persistent cache + holding_mcap), แกะ case study (CPALL/TCAP/QH/FPT/OR) + moat patterns เป็น deterministic Python rules, ทำ 3-tier hard filter (PASS/REVIEW/FAIL), wire exit baseline save/load เข้า pipeline | Index: niwes-algo-index | Depends on: none | Parallel-safe with: none (02/03/04 ต้องรอ 01 merge)

## Phase 1: Data Pipeline Enrichment + Schema Foundation
- [x] สร้างไฟล์ `projects/MaxMahon/data/case_study_patterns.json` บรรจุ 5 case study patterns (CPALL=RETAIL_DEFENSIVE_MOAT / TCAP=BANK_VALUE_PBV1 / QH=HOLDING_CO_HIDDEN / FPT=VIETNAM_GROWTH_EXPOSURE / OR=ENERGY_CYCLICAL_EXIT) — แต่ละ pattern มี fields: `tag`, `source` (path docs/niwes/06-10), `rules` (dict thresholds), optional `anti_rules: true`, `narrative` (Thai 1-2 บรรทัด) — ดู reference เพื่อ schema ละเอียด — scope: data only, ห้าม wire เข้า code — Acceptance: `python -c "import json; d=json.load(open('projects/MaxMahon/data/case_study_patterns.json')); assert len(d)==5 and all('tag' in v and 'rules' in v for v in d.values())"` pass
- [x] สร้างไฟล์ `projects/MaxMahon/data/exit_baselines.json` เป็น empty dict `{}` — Acceptance: file exists + `json.load()` returns `{}`
- [x] แก้ `projects/MaxMahon/scripts/fetch_data.py` function `fetch_multi_year()` (line 393) หรือ yearly_metrics builder ในนั้น — เพิ่ม helper `_get_price_avg(yf_sym, year)` ใช้ `yf.Ticker(yf_sym).history(start, end, interval='1mo', auto_adjust=False)['Close'].mean()` (**auto_adjust=False บังคับ** — ต้องการ raw close ไม่ dividend/split-adjusted เพื่อให้ yield calc = dps/price_avg ตรงกับค่าจริง) + docstring: 'Returns raw monthly close avg (NOT adjusted) — for yield calculation parity with historical DPS' + **persistent cache** `data/price_avg_cache/{yf_sym}.json` schema `{"_fetched_at": ISO, "2024": 55.3, "2023": 48.1, ...}` (refresh ถ้า _fetched_at > 30 วัน) + เพิ่ม `data/price_avg_cache/` ใน `.gitignore` — สำหรับแต่ละ year ใน yearly_metrics: `m['price_avg'] = _get_price_avg(yf_sym, m['year'])` — scope: ห้ามแก้ logic อื่น, เฉพาะเพิ่ม field — Acceptance: snapshot_{date}.json entry CPALL.BK มี `yearly_metrics[].price_avg` field ทุกปี (null ถ้า fetch fail); year 2020 ประมาณ 60-70 THB (ราคาจริง NOT adjusted); cache file `data/price_avg_cache/CPALL.BK.json` สร้างขึ้น + รัน scan รอบ 2 ภายใน 30 วัน → ไม่ re-fetch
- [x] แก้ `projects/MaxMahon/scripts/data_adapter.py` function `check_hidden_value()` (line 622) — หลัง load hidden_value_holdings.json, enrich แต่ละ holding entry ด้วย `holding_mcap` จาก yfinance `yf.Ticker(holding).info.get('marketCap')` (error-safe — ถ้า fetch fail ให้ set `holding_mcap: None`) + cache lookup (symbol-level dict) — scope: ไม่เปลี่ยน return shape field อื่น, แค่เพิ่ม holding_mcap ต่อ entry — Acceptance: `check_hidden_value('QH.BK')` return list มี `[{holding:'HMPRO.BK', stake_pct:19.87, note:..., holding_mcap:<number>}]`

### Reference
```json
// projects/MaxMahon/data/case_study_patterns.json — 5 patterns
{
  "RETAIL_DEFENSIVE_MOAT": {
    "tag": "RETAIL_DEFENSIVE_MOAT",
    "source": "docs/niwes/06-case-cpall.md",
    "rules": {
      "sector_keywords": ["retail","commerce","consumer","food","ค้าปลีก"],
      "dividend_streak_min": 5,
      "pe_max": 15,
      "dividend_yield_min": 5,
      "market_cap_min": 5000000000
    },
    "narrative": "ธุรกิจค้าปลีก/consumer defensive — ขาดไม่ได้ของผู้บริโภค ผ่านวิกฤติได้ (แบบ CPALL 17 ปี)"
  },
  "BANK_VALUE_PBV1": {
    "tag": "BANK_VALUE_PBV1",
    "source": "docs/niwes/07-case-tcap.md",
    "rules": {"sector_keywords":["financial","bank","ธนาคาร"],"pbv_max":1.0,"pe_max":9,"dividend_yield_min":5,"market_cap_min":5000000000},
    "narrative": "ธนาคาร mid-tier PBV<1 + yield 5%+ (แบบ TCAP)"
  },
  "HOLDING_CO_HIDDEN": {
    "tag": "HOLDING_CO_HIDDEN",
    "source": "docs/niwes/08-case-qh.md",
    "rules": {"has_hidden_holdings":true,"hidden_value_vs_mcap_min":1.0,"dividend_yield_min":5,"pbv_max":1.5},
    "narrative": "Holding company sum-of-parts > parent mcap (แบบ QH ถือ HMPRO)"
  },
  "VIETNAM_GROWTH_EXPOSURE": {
    "tag": "VIETNAM_GROWTH_EXPOSURE",
    "source": "docs/niwes/10-case-fpt.md",
    "rules": {"country":"VN","sector_keywords":["technology","it","communications"],"market_cap_min":50000000000,"roe_3yr_avg_min":0.10,"dividend_yield_min":3},
    "narrative": "Vietnam tech scale 50B+ ROE 10%+ (แบบ FPT)"
  },
  "ENERGY_CYCLICAL_EXIT": {
    "tag": "ENERGY_CYCLICAL_EXIT",
    "source": "docs/niwes/09-case-or.md",
    "rules": {"sector_keywords":["energy","petroleum","oil"],"structural_disruption":true},
    "anti_rules": true,
    "narrative": "Energy/petroleum กำลังถูก disrupt (EV) — ทบทวน thesis (แบบ OR)"
  }
}
```

```python
# projects/MaxMahon/scripts/fetch_data.py — _get_price_avg with auto_adjust=False + persistent cache
import json
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf

_PRICE_AVG_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "price_avg_cache"
_PRICE_AVG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_CACHE_TTL = timedelta(days=30)


def _get_price_avg(yf_sym: str, year: int) -> float | None:
    """Returns raw monthly close avg (NOT adjusted) — for yield calculation parity with historical DPS.

    auto_adjust=False บังคับ เพราะ: yield = dps(raw) / price(raw).
    ถ้าใช้ adjusted price → ได้ yield ต่ำเพี้ยน 5-10% (dividend-adjusted price)
    """
    cache_file = _PRICE_AVG_CACHE_DIR / f"{yf_sym}.json"
    cache: dict = {}
    if cache_file.exists():
        try:
            cache = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            cache = {}
    key = str(year)
    fetched_at_str = cache.get("_fetched_at")
    if key in cache and fetched_at_str:
        try:
            if datetime.fromisoformat(fetched_at_str) > datetime.now() - _CACHE_TTL:
                return cache[key]
        except Exception:
            pass
    try:
        hist = yf.Ticker(yf_sym).history(
            start=f"{year}-01-01", end=f"{year}-12-31", interval="1mo", auto_adjust=False
        )
        val = float(hist["Close"].mean()) if not hist.empty else None
    except Exception:
        val = None
    cache[key] = val
    cache["_fetched_at"] = datetime.now().isoformat(timespec="seconds")
    cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return val


# ใน yearly_metrics builder loop (ภายใน fetch_multi_year หรือ _build_aggregates):
#   for m in yearly_metrics:
#       m["price_avg"] = _get_price_avg(yf_sym, m["year"])
```

```
# projects/MaxMahon/.gitignore — append
data/price_avg_cache/
```

```python
# projects/MaxMahon/scripts/data_adapter.py — check_hidden_value() enrich
import yfinance as yf
_HOLDING_MCAP_CACHE: dict[str, int | None] = {}

def _holding_mcap(sym: str) -> int | None:
    if sym in _HOLDING_MCAP_CACHE:
        return _HOLDING_MCAP_CACHE[sym]
    try:
        v = yf.Ticker(sym).info.get("marketCap")
    except Exception:
        v = None
    _HOLDING_MCAP_CACHE[sym] = v
    return v

# ใน check_hidden_value() ก่อน return — enrich holdings list:
#   holdings = data.get(yf_sym, [])
#   for h in holdings:
#       h['holding_mcap'] = _holding_mcap(h.get('holding'))
#   return holdings
```

## Phase 2: Case Study + Moat Detectors + Wire
- [x] สร้างไฟล์ `projects/MaxMahon/scripts/case_study_detector.py` — module ใหม่ pure functions: `load_patterns() -> dict`, `detect_case_study_tags(stock: dict, patterns: dict) -> list[str]`, `detect_moat_tags(stock: dict) -> list[str]` — logic ตาม reference (sector keyword + metric thresholds matching; BRAND_MOAT = commerce/food/beverage/consumer + net_margin>0.20 + streak>=10; STRUCTURAL_MOAT = utility/transport/telecom/infrastructure + mcap>=50B; GOVT_LOCKIN = 'government'/'e-document'/'public service'/'ราชการ' ใน sector+industry) — scope: module-level only, no I/O except load_patterns, skip anti_rules patterns + skip disabled patterns (ถ้า `p.get('disabled')` — forward-compat กับ plan 05) — Acceptance: `python -c` test CPALL-like dict → `['RETAIL_DEFENSIVE_MOAT']`; QH-like dict with `_hidden_holdings` populated → `['HOLDING_CO_HIDDEN']`
- [x] แก้ `projects/MaxMahon/scripts/screen_stocks.py` — top-of-file เพิ่ม import `from case_study_detector import detect_case_study_tags, detect_moat_tags, load_patterns` + module-level `_PATTERNS = load_patterns()` — ใน caller ของ `assign_signals()` (main loop / screen_stock function) ก่อนเรียก assign_signals: `stock['_hidden_holdings'] = check_hidden_value(stock.get('symbol', ''))` (import check_hidden_value from data_adapter) — ใน assign_signals() ท้ายก่อน return: `signals.extend(detect_case_study_tags(data, _PATTERNS)); signals.extend(detect_moat_tags(data))` — scope: ห้ามลบ/แก้ signal logic เดิม (NIWES_5555 ฯลฯ), เพิ่มเท่านั้น — Acceptance: run scan → screener_{date}.json candidate ของ CPALL.BK มี signals array รวม NIWES_5555 + RETAIL_DEFENSIVE_MOAT (+ BRAND_MOAT ถ้า margin/streak ผ่าน)

### Reference
```python
# projects/MaxMahon/scripts/case_study_detector.py — new file
import json
from pathlib import Path

_PATTERNS_PATH = Path(__file__).resolve().parent.parent / "data" / "case_study_patterns.json"

def load_patterns() -> dict:
    return json.loads(_PATTERNS_PATH.read_text(encoding="utf-8"))

def _matches(sector: str, keywords: list[str]) -> bool:
    s = (sector or "").lower()
    return any(kw.lower() in s for kw in keywords)

def detect_case_study_tags(stock: dict, patterns: dict) -> list[str]:
    tags = []
    agg = stock.get("aggregates") or {}
    streak = agg.get("dividend_streak", 0)
    dy = stock.get("dividend_yield") or 0
    pe = stock.get("pe_ratio")
    pbv = stock.get("pb_ratio")
    mcap = stock.get("market_cap") or 0
    sector = stock.get("sector", "")
    for p in patterns.values():
        if p.get("anti_rules") or p.get("disabled"):
            continue
        r = p.get("rules", {})
        if "sector_keywords" in r and not _matches(sector, r["sector_keywords"]):
            continue
        if "dividend_streak_min" in r and streak < r["dividend_streak_min"]:
            continue
        if "dividend_yield_min" in r and dy < r["dividend_yield_min"]:
            continue
        if "pe_max" in r and (pe is None or pe <= 0 or pe > r["pe_max"]):
            continue
        if "pbv_max" in r and (pbv is None or pbv <= 0 or pbv > r["pbv_max"]):
            continue
        if "market_cap_min" in r and mcap < r["market_cap_min"]:
            continue
        if r.get("has_hidden_holdings"):
            hh = stock.get("_hidden_holdings") or []
            if not hh:
                continue
            hidden_total = sum((h.get("holding_mcap") or 0) * (h.get("stake_pct", 0) / 100.0) for h in hh)
            if hidden_total < r.get("hidden_value_vs_mcap_min", 1.0) * mcap:
                continue
        tags.append(p["tag"])
    return tags

def detect_moat_tags(stock: dict) -> list[str]:
    tags = []
    sector = (stock.get("sector") or "").lower()
    industry = (stock.get("industry") or "").lower()
    agg = stock.get("aggregates") or {}
    nm = stock.get("profit_margin") or agg.get("avg_net_margin") or 0
    streak = agg.get("dividend_streak", 0)
    mcap = stock.get("market_cap") or 0
    combo = sector + " " + industry
    if any(k in sector for k in ["commerce","food","beverage","consumer"]) and nm > 0.20 and streak >= 10:
        tags.append("BRAND_MOAT")
    if any(k in sector for k in ["utilit","transport","telecom","infrastructure"]) and mcap >= 50_000_000_000:
        tags.append("STRUCTURAL_MOAT")
    if any(k in combo for k in ["government","e-document","public service","ราชการ"]):
        tags.append("GOVT_LOCKIN")
    return tags
```

```python
# screen_stocks.py — wire (near existing main loop / per-stock pipeline)
from case_study_detector import detect_case_study_tags, detect_moat_tags, load_patterns
from data_adapter import check_hidden_value
_PATTERNS = load_patterns()

# In per-stock processing, BEFORE calling assign_signals:
stock['_hidden_holdings'] = check_hidden_value(stock.get('symbol', ''))

# In assign_signals() at end before return signals:
signals.extend(detect_case_study_tags(data, _PATTERNS))
signals.extend(detect_moat_tags(data))
```

## Phase 3: 3-Tier Hard Filter + Review Candidates
- [x] แก้ `projects/MaxMahon/scripts/screen_stocks.py` function `hard_filter()` (line 50-112) — เปลี่ยน return type จาก `(bool, list, list)` เป็น `(str, list, list)` โดย status ∈ {'PASS','REVIEW','FAIL'} — keep 3rd element = `near_miss` list เดิม — logic: market_cap < min → FAIL ทันที (hard); dividend streak 3-tier (≥5 PASS contrib / 3-4 REVIEW / <3 FAIL); EPS 3-tier (5/5 PASS / 4/5 & last 3 positive REVIEW / else FAIL); yield/PE/PBV ยังเป็น hard FAIL เดิม — aggregation rule: any FAIL → 'FAIL'; no FAIL + any REVIEW → 'REVIEW'; ไม่มีเลย → 'PASS' — scope: เก็บ reasons list format เดิม (strings ภาษาไทย) — Acceptance: call กับ stock streak=4 + EPS 5/5 + yield=6 + PE=10 + PBV=1.2 + mcap=10B → status='REVIEW', reasons มี 'dividend streak 4yr (3-4 = REVIEW)'
- [x] แก้ caller ของ hard_filter() ใน screen_stocks.py main loop (line 559+) — แยก output เป็น 3 bucket: `candidates[]` (PASS→build full entry with score), `review_candidates[]` (REVIEW→basic metrics + review_reasons), `filtered_out_stocks[]` (FAIL→existing shape) — อัพเดท `save_screener_results()` เพิ่ม key `review_candidates` ใน JSON output + เปลี่ยน `scoring_version: 'niwes-dividend-first-v1'` เป็น `'niwes-dividend-first-v2'` — scope: ไม่แก้ quality scoring function — Acceptance: screener_{date}.json มี keys: candidates/review_candidates/filtered_out_stocks/hard_filters + scoring_version=v2

### Reference
```python
# screen_stocks.py — hard_filter() current state (line 50):
# def hard_filter(data: dict) -> tuple:
#     reasons = []; near_miss = []
#     ... (market_cap early return; yield/streak/EPS/PE/PBV collect reasons)
#     return len(reasons) == 0, reasons, near_miss

# new (3-tier)
def hard_filter(data: dict) -> tuple:
    """Returns (status, reasons, near_miss) where status in {'PASS','REVIEW','FAIL'}."""
    fail_reasons: list[str] = []
    review_reasons: list[str] = []
    near_miss: list[str] = []
    agg = data.get("aggregates") or {}
    info_mcap = data.get("market_cap") or 0

    # Market cap — hard gate (same as before)
    if info_mcap < HARD_FILTERS["min_market_cap"]:
        fail_reasons.append(f"market cap {info_mcap/1e9:.1f}B < {HARD_FILTERS['min_market_cap']/1e9:.0f}B")
        return "FAIL", fail_reasons, near_miss

    # Dividend streak — 3-tier
    streak = agg.get("dividend_streak", 0)
    if streak < 3:
        fail_reasons.append(f"dividend streak {streak}yr < 3 (FAIL)")
    elif streak < 5:
        review_reasons.append(f"dividend streak {streak}yr (3-4 = REVIEW)")

    # EPS — 3-tier
    norm_eps = compute_normalized_earnings(data)
    if norm_eps:
        sorted_years = sorted(norm_eps.keys())[-5:]
        eps_recent = [norm_eps[y] for y in sorted_years]
        pos = sum(1 for e in eps_recent if e is not None and e > 0)
        total = len(eps_recent)
        if total < 5:
            fail_reasons.append(f"EPS history {total}yr (need 5)")
        elif pos == 5:
            pass  # PASS contrib
        elif pos == 4 and all(e is not None and e > 0 for e in eps_recent[-3:]):
            review_reasons.append("EPS 4/5 & last 3 positive (COVID exception = REVIEW)")
        else:
            fail_reasons.append(f"EPS positive {pos}/5 (FAIL)")
    else:
        fail_reasons.append("ไม่มีข้อมูล EPS")

    # Yield / PE / PBV — hard rules (unchanged)
    dy = data.get("dividend_yield")
    if dy is None:
        fail_reasons.append("ไม่มีข้อมูลปันผล")
    elif dy < HARD_FILTERS["min_dividend_yield"]:
        fail_reasons.append(f"dividend yield {dy:.1f}% < {HARD_FILTERS['min_dividend_yield']:.0f}%")
    pe = data.get("pe_ratio")
    if pe is None or pe <= 0:
        fail_reasons.append("ไม่มี P/E ที่ใช้ได้")
    elif pe > HARD_FILTERS["max_pe"]:
        fail_reasons.append(f"P/E {pe:.1f} > {HARD_FILTERS['max_pe']:.0f}")
    pbv = data.get("pb_ratio")
    if pbv is None or pbv <= 0:
        fail_reasons.append("ไม่มี P/BV ที่ใช้ได้")
    elif pbv > HARD_FILTERS["max_pbv"]:
        fail_reasons.append(f"P/BV {pbv:.2f} > {HARD_FILTERS['max_pbv']:.1f}")

    if fail_reasons:
        return "FAIL", fail_reasons + review_reasons, near_miss
    if review_reasons:
        return "REVIEW", review_reasons, near_miss
    return "PASS", [], near_miss
```

```python
# caller (main loop)
status, reasons, near_miss = hard_filter(stock)
if status == "PASS":
    candidates.append(build_full_entry(stock))
elif status == "REVIEW":
    review_candidates.append({
        "symbol": stock["symbol"],
        "name": stock.get("name"),
        "sector": stock.get("sector"),
        "review_reasons": reasons,
        "basic_metrics": {"price": stock.get("price"), "pe": stock.get("pe_ratio"), "pbv": stock.get("pb_ratio"), "dy": stock.get("dividend_yield"), "streak": (stock.get("aggregates") or {}).get("dividend_streak")},
    })
else:
    filtered_out_stocks.append({"symbol": stock["symbol"], "reasons": reasons, ...})

# save_screener_results(): bump scoring_version → 'niwes-dividend-first-v2' + add key 'review_candidates'
```

## Phase 4: Exit Baseline Save/Load + Wire
- [x] เพิ่ม functions ใน `projects/MaxMahon/scripts/screen_stocks.py` (ใกล้ detect_exit_signal บรรทัด ~303): `load_exit_baselines() -> dict` (อ่าน data/exit_baselines.json, return {} ถ้าไม่มี/parse error), `save_exit_baseline(symbol, metrics, baselines) -> dict` (update in-memory + atomic write, fields: passed_5555=True, pe_baseline, pbv_baseline, dy_baseline, date_added, date_refreshed, thesis_change_flag=False); ถ้า symbol มี entry แล้ว + passed_5555=True → keep existing (refresh date_refreshed only) — scope: pure I/O helpers — Acceptance: unit test `save_exit_baseline('CPALL.BK', {'pe_ratio':8.5,'pb_ratio':1.1,'dividend_yield':5.5}, {})` → JSON มี key 'CPALL.BK' + passed_5555=True
- [x] Wire exit baseline ใน screen_stocks.py main loop: ก่อน main loop `baselines = load_exit_baselines()` + load watchlist symbols (existing helper); ใน per-stock processing หลัง assign_signals(): ถ้า 'NIWES_5555' ใน signals → `baselines = save_exit_baseline(sym, {'pe_ratio':.., 'pb_ratio':.., 'dividend_yield':..}, baselines)`; สำหรับ stock ใน watchlist → `exit_triggers = detect_exit_signal(sym, stock, baselines.get(sym))` + attach `candidate_entry['exit_triggers'] = exit_triggers` — scope: ไม่ต้อง alert/notification ในนี้ — Acceptance: stock watchlist ที่ baseline มี PE=8 + current PE=25 → candidate entry มี `exit_triggers: [{type:'VALUATION_BUBBLE', severity:'high', reason:...}]`

### Reference
```python
# screen_stocks.py — helpers (near line 303)
import json
from pathlib import Path
from datetime import datetime

_BASELINES_PATH = Path(__file__).resolve().parent.parent / "data" / "exit_baselines.json"

def load_exit_baselines() -> dict:
    if not _BASELINES_PATH.exists():
        return {}
    try:
        return json.loads(_BASELINES_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

def save_exit_baseline(symbol: str, metrics: dict, baselines: dict) -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    existing = baselines.get(symbol, {})
    if existing.get("passed_5555"):
        existing["date_refreshed"] = today
        baselines[symbol] = existing
    else:
        baselines[symbol] = {
            "passed_5555": True,
            "pe_baseline": metrics.get("pe_ratio"),
            "pbv_baseline": metrics.get("pb_ratio"),
            "dy_baseline": metrics.get("dividend_yield"),
            "date_added": today,
            "date_refreshed": today,
            "thesis_change_flag": False,
        }
    _BASELINES_PATH.write_text(json.dumps(baselines, indent=2, ensure_ascii=False), encoding="utf-8")
    return baselines
```

```python
# main loop wire (pseudo)
baselines = load_exit_baselines()
watchlist = load_user_watchlist()

for stock in all_stocks:
    stock['_hidden_holdings'] = check_hidden_value(stock['symbol'])
    status, reasons, near_miss = hard_filter(stock)
    signals = assign_signals(stock, total_score) if status == "PASS" else []
    if "NIWES_5555" in signals:
        baselines = save_exit_baseline(stock['symbol'],
            {"pe_ratio": stock.get("pe_ratio"), "pb_ratio": stock.get("pb_ratio"), "dividend_yield": stock.get("dividend_yield")},
            baselines)
    candidate_entry['exit_triggers'] = (detect_exit_signal(stock['symbol'], stock, baselines.get(stock['symbol']))
                                         if stock['symbol'] in watchlist else [])
```
