---
project: MaxMahon
created: 2026-04-23
last_updated: 2026-04-23
status: done
---

# Feature: จัดพอร์ตสไตล์แมกซ์ — Niwes Portfolio Builder

> Part 2 of 3 — สร้าง feature ใหม่ให้ user ทดลองจัดพอร์ต 5 หุ้นสไตล์ ดร.นิเวศน์ จาก PASS list ของ screener: เลือก top-1 ต่อ sector (composite: yield + PE value + PBV value + hidden + quality) → 5 sector ต่างกัน → weight 80/20 pattern (40/35/12/8/5) → ถ้า user ใส่ capital ก็คำนวณจำนวนหุ้น/เงินต่อตัว. Backend = pure functions + FastAPI POST /api/portfolio/builder. Frontend = new page /portfolio-builder (desktop + mobile) แค่ SHELL + DATA WIRING เท่านั้น — ยังใช้ vintage newspaper style เดิมไปก่อน (visual redesign รอ plan 03). | Index: maxmahon-next-index | Depends on: maxmahon-next-01-qc-fix | Parallel-safe with: none

## Phase 1: Niwes composite score + sector grouper (pure functions)
- [x] สร้างไฟล์ใหม่ `projects/MaxMahon/scripts/portfolio_builder.py` — module สำหรับ Niwes portfolio construction. เพิ่ม function `niwes_composite_score(stock: dict) -> float` ที่รวม 5 ปัจจัย: (1) yield_score = dividend_yield × 3 (sigmoid cap at ≥8%), (2) pe_value = max(0, (15 - pe) / 15 × 20) — ถูกกว่า PE=15 ได้คะแนน, (3) pbv_value = max(0, (1.5 - pbv) / 1.5 × 15), (4) hidden_bonus = 20 if stock has NIWES hidden value tag else 0, (5) quality = stock['score'] (0-100 จาก screener). Return weighted sum 0-100+. เพิ่ม function `group_by_sector(stocks: list[dict]) -> dict[str, list[dict]]` ที่ key = SET sector (field `sector`). เพิ่ม `top_per_sector(grouped: dict) -> list[dict]` — pick stock ที่ composite สูงสุดใน sector นั้น, return list of 1-per-sector sorted desc by composite. — scope: ไม่แตะ API endpoint, ไม่คำนวณ weights (Phase 2), ไม่เขียน frontend — Acceptance: `py -c "import sys; sys.path.insert(0,'projects/MaxMahon/scripts'); from portfolio_builder import niwes_composite_score, group_by_sector, top_per_sector; s={'dividend_yield':7.5,'pe_ratio':8.9,'pb_ratio':0.7,'signals':['HIDDEN_VALUE'],'score':92,'sector':'Property Development'}; print('composite:', niwes_composite_score(s))"` ต้อง print ตัวเลข > 50 (QH น่าจะสูง)

### Reference
```python
# new file — scripts/portfolio_builder.py
"""Niwes portfolio construction logic — pure functions, no I/O.

Feature: จัดพอร์ตสไตล์แมกซ์ — 5 หุ้น 5 sector 80/20 weight pattern.
"""
from collections import defaultdict


def niwes_composite_score(stock: dict) -> float:
    """Rank score combining yield + value + hidden + quality. 0 to ~100+."""
    dy = stock.get("dividend_yield") or 0
    pe = stock.get("pe_ratio") or 999
    pbv = stock.get("pb_ratio") or 999
    signals = stock.get("signals") or []
    quality = stock.get("score") or 0

    # yield — reward up to 8%
    yield_score = min(dy, 8) * 3  # up to 24
    # PE value — cheaper is better (PE <= 15)
    pe_value = max(0, (15 - pe) / 15 * 20) if pe > 0 else 0  # up to 20
    # PBV value — cheaper is better (PBV <= 1.5)
    pbv_value = max(0, (1.5 - pbv) / 1.5 * 15) if pbv > 0 else 0  # up to 15
    # Hidden value bonus
    hidden_bonus = 20 if "HIDDEN_VALUE" in signals else 0
    # Quality score contribution (normalize to 0-25)
    quality_contribution = quality * 0.25  # up to 25
    return yield_score + pe_value + pbv_value + hidden_bonus + quality_contribution


def group_by_sector(stocks: list[dict]) -> dict:
    """Group PASS stocks by SET sector. Unknown sector bucketed as 'Unknown'."""
    groups = defaultdict(list)
    for s in stocks:
        sector = s.get("sector") or "Unknown"
        groups[sector].append(s)
    return dict(groups)


def top_per_sector(grouped: dict) -> list[dict]:
    """Pick top-1 per sector by niwes_composite_score, sort desc by composite."""
    picks = []
    for sector, stocks in grouped.items():
        scored = [(s, niwes_composite_score(s)) for s in stocks]
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[0][0]
        top["_composite"] = scored[0][1]  # annotate for debugging
        picks.append(top)
    picks.sort(key=lambda x: x["_composite"], reverse=True)
    return picks
```

## Phase 2: Weight allocator + override resolver
- [x] เพิ่มใน `projects/MaxMahon/scripts/portfolio_builder.py` — function `allocate_80_20(picks: list[dict]) -> list[dict]` รับ stocks sorted by composite desc, return stocks with `weight_pct` field added: [40, 35, 12, 8, 5] สำหรับ 5 ตัวแรก. ถ้าได้น้อยกว่า 5 ตัว: rescale proportional ให้รวม 100%. Return only top 5. — scope: ไม่แตะ shares calculation (Phase 3) — Acceptance: `py -c "from portfolio_builder import allocate_80_20; picks=[{'symbol':'A','_composite':90},{'symbol':'B','_composite':80},{'symbol':'C','_composite':70}]; r=allocate_80_20(picks); print([(s['symbol'],s['weight_pct']) for s in r])"` ต้องคืน 3 ตัว น้ำหนักรวม 100% (น่าจะเป็น ~44.4 / 38.9 / 16.7)
- [x] เพิ่มใน `projects/MaxMahon/scripts/portfolio_builder.py` — function `apply_overrides(candidates: list[dict], pins: list[str], excludes: list[str]) -> tuple[list[dict], list[str]]` รับ PASS stocks + user pins (symbols ต้องมี) + excludes (symbols ต้องไม่มี). Return (filtered_stocks, warnings). Logic: (a) filter out excludes, (b) force-include pins (validate pin symbol exists in candidates, ถ้าไม่มี → warning), (c) ถ้า pin อยู่ sector เดียวกับ top-pick ของ sector นั้น → pin ชนะ. — scope: ไม่แตะ capital calculation — Acceptance: `py -c "from portfolio_builder import apply_overrides; stocks=[{'symbol':'A.BK','sector':'X'},{'symbol':'B.BK','sector':'X'},{'symbol':'C.BK','sector':'Y'}]; f,w=apply_overrides(stocks, pins=['B.BK'], excludes=['A.BK']); print([s['symbol'] for s in f], 'warnings:', w)"` ต้องคืน `['B.BK','C.BK']` + warnings ว่าง

### Reference
```python
# add to scripts/portfolio_builder.py

DEFAULT_WEIGHTS = [40, 35, 12, 8, 5]  # 80/20 Niwes pattern


def allocate_80_20(picks: list[dict]) -> list[dict]:
    """Assign weights from DEFAULT_WEIGHTS pattern to picks sorted by composite.
    If fewer than 5 picks, rescale proportional to sum 100.
    """
    picks = picks[:5]
    n = len(picks)
    if n == 0:
        return []
    base = DEFAULT_WEIGHTS[:n]
    total = sum(base)
    weights = [round(w / total * 100, 1) for w in base]
    for s, w in zip(picks, weights):
        s["weight_pct"] = w
    return picks


def apply_overrides(candidates: list[dict], pins: list[str], excludes: list[str]) -> tuple:
    """Filter candidates by user pins + excludes.
    
    Returns (filtered_stocks, warnings). Pins validated against candidates;
    unknown pin symbols surface as warnings.
    """
    warnings = []
    symbols_available = {s.get("symbol") for s in candidates}
    for pin in pins:
        if pin not in symbols_available:
            warnings.append(f"pin symbol not in PASS list: {pin}")
    excludes_set = set(excludes)
    filtered = [s for s in candidates if s.get("symbol") not in excludes_set]
    # Mark pins so downstream can prioritize within sector
    for s in filtered:
        s["_pinned"] = s.get("symbol") in set(pins)
    return filtered, warnings
```

## Phase 3: Integration + FastAPI endpoint
- [x] เพิ่มใน `projects/MaxMahon/scripts/portfolio_builder.py` — main integration function `build_portfolio(candidates: list[dict], capital: float | None = None, pins: list[str] | None = None, excludes: list[str] | None = None) -> dict`. Flow: (1) apply_overrides → filtered, warnings, (2) modify top_per_sector ให้ pin-priority (ถ้า sector มี pinned stock, เลือก pinned แทน highest composite), (3) group_by_sector → top_per_sector → allocate_80_20, (4) ถ้า capital ให้: amount_thb = capital × weight_pct/100, shares = floor(amount_thb / current_price), (5) assemble output. Return `{portfolio: [...], sector_count: int, total_score_avg: float, warnings: [...]}`. แก้ `top_per_sector` ให้ honor _pinned flag (pin ชนะ composite ใน sector เดียวกัน). — scope: ไม่เขียน FastAPI endpoint — Acceptance: `py -c "from portfolio_builder import build_portfolio; result=build_portfolio([{'symbol':'Q.BK','sector':'P','dividend_yield':7.5,'pe_ratio':8.9,'pb_ratio':0.7,'signals':['HIDDEN_VALUE'],'score':92,'current_price':1.33}], capital=1000000); print('len:', len(result['portfolio']), 'sum_weight:', sum(s['weight_pct'] for s in result['portfolio']))"` ต้องคืน len=1, sum_weight=100
- [x] เพิ่ม FastAPI endpoint ใน `projects/MaxMahon/server/app.py` (หาที่ว่างหลัง existing /api/portfolio/pnl บรรทัด ~1419): สร้าง `@app.post('/api/portfolio/builder')` รับ `PortfolioBuilderRequest` Pydantic model กับ fields `capital: Optional[float] = None`, `pins: list[str] = []`, `excludes: list[str] = []`. Flow: (a) load latest screener JSON จาก `data/screener_YYYY-MM-DD.json` (ใช้ pattern _SCREENER_DATE_PATTERN เหมือน screen_stocks.py), (b) extract `candidates` field (PASS list), (c) call `build_portfolio(...)`, (d) return result dict. Auth ใช้ existing MAX_TOKEN bearer (ตามแบบ /api/portfolio/transactions). — scope: ไม่เขียน frontend — Acceptance: server start ขึ้น + `curl -X POST http://localhost:50089/api/portfolio/builder -H "Authorization: Bearer $MAX_TOKEN" -H "Content-Type: application/json" -d '{"capital": 1000000}'` ตอบ 200 + body มี field `portfolio` (list) + `sector_count` (int) + `warnings` (list)

### Reference
```python
# add to scripts/portfolio_builder.py
import math


def build_portfolio(
    candidates: list[dict],
    capital: float | None = None,
    pins: list[str] | None = None,
    excludes: list[str] | None = None,
) -> dict:
    """Main entry — build 5-stock portfolio from PASS candidates."""
    pins = pins or []
    excludes = excludes or []
    filtered, warnings = apply_overrides(candidates, pins, excludes)
    grouped = group_by_sector(filtered)
    # top-per-sector with pin priority
    picks_per_sector = []
    for sector, stocks in grouped.items():
        pinned = [s for s in stocks if s.get("_pinned")]
        if pinned:
            pick = pinned[0]
        else:
            scored = [(s, niwes_composite_score(s)) for s in stocks]
            scored.sort(key=lambda x: x[1], reverse=True)
            pick = scored[0][0]
        pick["_composite"] = niwes_composite_score(pick)
        picks_per_sector.append(pick)
    picks_per_sector.sort(key=lambda x: x["_composite"], reverse=True)
    picked = allocate_80_20(picks_per_sector)
    if len(picked) < 5:
        warnings.append(f"only {len(picked)} sectors available — need 5 for full diversification")
    # Calc amounts + shares if capital provided
    if capital is not None and capital > 0:
        for s in picked:
            amount = capital * s["weight_pct"] / 100
            price = s.get("current_price") or s.get("price") or 0
            s["amount_thb"] = round(amount, 2)
            s["shares"] = math.floor(amount / price) if price > 0 else 0
    # Build response
    scores = [s.get("score", 0) for s in picked]
    return {
        "portfolio": picked,
        "sector_count": len(picks_per_sector),
        "total_score_avg": round(sum(scores) / len(scores), 1) if scores else 0,
        "warnings": warnings,
    }
```

```python
# add to server/app.py (after existing /api/portfolio/pnl ~line 1500)
from pydantic import BaseModel

class PortfolioBuilderRequest(BaseModel):
    capital: Optional[float] = None
    pins: list[str] = []
    excludes: list[str] = []

@app.post("/api/portfolio/builder")
async def portfolio_builder(req: PortfolioBuilderRequest, _: None = Depends(verify_token)):
    """Build Niwes-style 5-sector portfolio from latest screener PASS candidates."""
    import sys as _sys
    from pathlib import Path as _Path
    _scripts_dir = _Path(__file__).resolve().parent.parent / "scripts"
    if str(_scripts_dir) not in _sys.path:
        _sys.path.insert(0, str(_scripts_dir))
    from portfolio_builder import build_portfolio
    # Find latest screener JSON
    data_dir = _Path(__file__).resolve().parent.parent / "data"
    files = sorted(
        [f for f in data_dir.glob("screener_*.json")
         if re.match(r"^screener_\d{4}-\d{2}-\d{2}\.json$", f.name)],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        raise HTTPException(404, "no screener data — run /api/admin/scan/trigger first")
    screener = json.loads(files[0].read_text(encoding="utf-8"))
    candidates = screener.get("candidates", [])
    # Enrich candidates with current_price from metrics
    for c in candidates:
        c["current_price"] = (c.get("metrics") or {}).get("current_price")
    result = build_portfolio(
        candidates=candidates,
        capital=req.capital,
        pins=req.pins,
        excludes=req.excludes,
    )
    result["screener_date"] = screener.get("date")
    return result
```

## Phase 4: Frontend page module + shell route
- [x] สร้างไฟล์ใหม่ `projects/MaxMahon/web/v6/static/js/pages/portfolio-builder.js` (desktop) — JS module export `init()` function. Render UI: (a) capital input (number), (b) pins/excludes chip rows, (c) submit button 'จัดพอร์ต', (d) result table 5 rows × (rank / symbol+name / sector badge / weight% / amount / shares / reason), (e) warnings banner. POST ไป `/api/portfolio/builder` กับ body จาก form. Render responses. ใช้ existing design tokens ที่ web/v6/shared/tokens.css (vintage newspaper — redesign อยู่ใน plan 03 ไม่ใช่ที่นี่). — scope: ใช้ style เดิม ไม่ import Robinhood tokens — Acceptance: `curl -s http://localhost:50089/portfolio-builder` ตอบ HTML shell + module load ไม่ crash (console error check manual)
- [x] สร้างไฟล์ `projects/MaxMahon/web/v6/static/js/pages/portfolio-builder.mobile.js` (mobile) — same flow แต่ mobile-responsive layout (stacked cards แทน table). — scope: เหมือน desktop — Acceptance: `curl -s http://localhost:50089/m/portfolio-builder` ตอบ HTML shell
- [x] เพิ่ม route ใน `projects/MaxMahon/server/app.py` (หลัง existing `@app.get('/settings', response_class=HTMLResponse)` บรรทัด ~3142) — 2 routes: `@app.get('/portfolio-builder', response_class=HTMLResponse)` = return desktop shell HTML (ใช้ pattern เดียวกับ portfolio.html เดิม — สร้าง `web/v6/desktop/portfolio-builder.html` ด้วย ที่ import `pages/portfolio-builder.js`). `@app.get('/m/portfolio-builder', response_class=HTMLResponse)` = mobile version. — scope: ไม่แก้ routes อื่น — Acceptance: `curl -I http://localhost:50089/portfolio-builder` ตอบ 200 content-type html
- [x] เพิ่ม navigation link ใน existing nav bars — update desktop shells (`web/v6/desktop/index.html` + `portfolio.html` + `watchlist.html` + `portfolio-builder.html`) + mobile shells — เพิ่ม nav item 'จัดพอร์ต' (icon 📊 หรือที่เหมาะ) ชี้ไปที่ `/portfolio-builder`. สำหรับ mobile bottom-nav ให้เพิ่ม tab 5 (ถ้ามีพื้นที่) หรือ replace tab ที่ใช้น้อยสุด. — scope: ไม่ redesign nav (แค่เพิ่ม link ในโครง existing) — Acceptance: desktop nav มี link 'จัดพอร์ต' ที่ชี้ /portfolio-builder, mobile nav มีเช่นกัน

## Phase 5: End-to-end smoke test
- [x] รัน E2E test: (a) start server, (b) ensure data/screener_*.json มี PASS candidates ≥5 ตัวกระจาย ≥5 sector (ถ้าไม่มี สร้าง mock ไฟล์ชั่วคราวสำหรับ test), (c) POST /api/portfolio/builder ด้วย capital=1000000 — ตรวจ response: portfolio length ≤5, sum(weight_pct) = 100, ทุกตัวมี sector ต่างกัน, ถ้ามี capital ทุกตัวมี amount_thb + shares (non-zero), (d) POST กับ pins=['TCAP.BK'] excludes=['CPALL.BK'] — ตรวจว่า TCAP อยู่ใน output, CPALL ไม่อยู่, (e) POST กับ capital=null — ตรวจ portfolio มีแต่ weight_pct (ไม่มี amount_thb), (f) เปิด browser /portfolio-builder + /m/portfolio-builder — ดู console error เก็บ screenshot 2 ใบลง docs/. — scope: ไม่แก้ code — Acceptance: 4/4 API test ผ่าน + 2 screenshots saved
