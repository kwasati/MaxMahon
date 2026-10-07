---
project: MaxMahon
created: 2026-04-25
last_updated: 2026-04-25
status: done
---

# Portfolio Builder จาก Watchlist (Niwes role-based)

> Feature ใหม่ /portfolio: เอาหุ้นจาก watchlist มาจัดพอร์ต Niwes 5-sector × 80/20 + role tags (anchor/supporting/tail) + bench list + sector warning + Claude Opus pillar-1 commentary. ของเก่า portfolio builder ถูก archive ไปแล้ววันนี้ (capital-based 5 SET sectors) — ใหม่ตัด capital, ใช้ watchlist เป็น input, เพิ่ม role reasoning per stock. Mockup desktop+mobile approved (mockup/portfolio-from-watchlist-{desktop,mobile}.html). Watchlist click→report quick fix (uncommitted in pages/watchlist.{js,mobile.js}) include in feature commit. **QC notes (ต้องอ่านก่อน build):** (1) screener candidates มี metrics nested (`c.metrics.pe` ไม่ใช่ pe_ratio) — ดู Phase 1 task (3) source mapping. (2) `from scripts import` ต้องเป็น lazy import per-function ตาม pattern เดิม (sys.path.insert) — module-level จะ crash. (3) mockup CSS ใช้ tokens `--radius/--font/--tap` ที่ production ไม่มี — ต้อง search-replace ก่อน paste. (4) mobile mappedActive ต้องเพิ่ม portfolio key.

## Phase 1: Backend Algo (Pure Functions)
- [x] สร้าง `scripts/portfolio_builder.py` (ไฟล์ใหม่) — pure functions ไม่มี I/O ไม่มี FastAPI: (1) `to_canonical_sector(raw: str) -> str` map raw SET sector → 5 buckets {Banking, Energy, Property, REIT-PFund, Other}. **Verified jaก screener_2026-04-14.json:** raw values include 'Banking', 'Commerce', 'Construction Materials', 'Energy & Utilities', 'Food & Beverage', 'Health Care Services', 'Information & Communication Technology', 'Insurance', 'Personal Products & Pharmaceuticals', '-' (empty marker). Logic: ถ้า raw is None or strip in ('', '-') → 'Other'. lower → check 'bank' → Banking, 'energy'/'petroleum'/'refining'/'utilit' → Energy, 'reit'/'property fund'/'infrastructure trust' → REIT-PFund, 'property'/'real estate' → Property, default → Other. (2) `niwes_composite_score(stock: dict) -> float` — port verbatim จาก archive `_archive/portfolio-simulator-builder-2026-04-25/backend/portfolio_builder.py:9-27` (formula: yield up to 8% × 3 + PE value + PBV value + HIDDEN_VALUE bonus 20 + score × 0.25). อ่าน top-level keys (dividend_yield/pe_ratio/pb_ratio) — Phase 1 task (3) ต้อง flatten ก่อนส่งเข้า. (3) `enrich_watchlist_stocks(watchlist: list[str], screener: dict) -> list[dict]` — join watchlist symbols กับ screener candidates+review_candidates+filtered_out_stocks. **CRITICAL source mapping (verified จาก screener_*.json จริง):** screener candidate dict มี top-level `symbol/name/sector/signals/score` + nested `metrics: {dividend_yield, pe, pb_ratio, current_price, ...}`. ต้อง flatten: `c['metrics']['dividend_yield']` → `dividend_yield`, `c['metrics']['pe']` (KEY ชื่อ 'pe' ไม่ใช่ 'pe_ratio'!) → `pe_ratio`, `c['metrics']['pb_ratio']` → `pb_ratio`, `c['metrics']['current_price']` → `current_price`. Top-level pass-through: symbol, name, sector, signals, score. คำนวณเพิ่ม: `sector_canonical = to_canonical_sector(c['sector'])`. ถ้า watchlist symbol ไม่มีใน screener → skip + collect ใน missing_list. (4) `apply_pin_overrides(stocks: list, pins: list[str]) -> tuple[list, list[str]]` — mark `_pinned=True` สำหรับ pin symbols ใน stocks, return (stocks_unchanged_order_with_flag, warnings). Pin symbol ที่ไม่มีใน stocks → warning 'pin not in watchlist: {sym}'. (5) `top_per_canonical_sector(stocks: list) -> list` — group by sector_canonical, pick top-1 per bucket: pinned wins → else max niwes_composite_score. Annotate `_composite` field. Return list sorted desc by _composite. (6) `allocate_80_20(picks: list) -> list` — port from archive line 42-55 (DEFAULT_WEIGHTS=[40,35,12,8,5], rescale proportional to sum 100 if <5 picks). (7) `tag_roles(picks: list) -> list` — annotate role/role_label_th/score_dot/sector_class/rank: rank 1-2=anchor (ตัวหลัก), 3=supporting (ตัวรอง), 4-5=tail (ตัวท้าย). score_dot='a' if score≥80 else 'b'. sector_class จาก SECTOR_CLASS_MAP. (8) `generate_role_reason(stock: dict, role: str, rank: int) -> str` — return Thai 1-line ขึ้นต้น 'ทำไมเป็น Anchor/Supporting/Tail:' + signals composed (HIDDEN_VALUE → mention hidden + holdings, DEEP_VALUE → mention PE/PBV ต่ำ, QUALITY_DIVIDEND → mention streak, yield ≥7% → high yield, score <75 + tail → 'น้ำหนักน้อยสุด · monitor closely'). (9) `build_bench(all_stocks: list, picked_symbols: set) -> list` — non-picked + bench reason (sector ซ้ำ → '{sector_canonical} มี {pick_sym} เป็น {role} แล้ว · score X รอง', score <60 → 'score X ต่ำ + [PE สูง / yield ต่ำ]'). (10) `build_sector_warnings(picked_canonical_sectors: set) -> list[dict]` — flag missing Banking/Energy/Property/REIT-PFund (ไม่ flag Other) → return [{sector, msg, suggestions}]. Suggestions hardcoded: Banking=['BBL','SCB','KBANK'], Energy=['PTT','PTTEP','BCP'], Property=['QH','AP','LPN'], REIT-PFund=['DIF','JASIF','CPNREIT']. (11) `build_portfolio(watchlist, screener, pins=None) -> dict` — orchestrator: enrich → apply_pin_overrides → top_per_canonical_sector → allocate_80_20 → tag_roles → for each pick add `reason=generate_role_reason()` + `tags` (PASS if NIWES_5555 in signals else REVIEW, 'Hidden ' + holdings if HIDDEN_VALUE, 'PINNED' if _pinned) → build_bench → build_sector_warnings → return {summary: {stock_count, sector_filled: 'X/5', score_avg}, warnings, portfolio, bench}. — scope: pure functions เท่านั้น. — Acceptance: รัน `python scripts/portfolio_builder.py` (มี `if __name__ == '__main__':` block) ด้วย sample 10 หุ้น (mock screener data ที่มี nested metrics เหมือนของจริง) → print portfolio dict ครบ 5 picks + role badges + reason ภาษาคน + bench 5 ตัว + warnings list. Verify: pinning QH ทำให้ QH เป็น anchor แม้ score ต่ำกว่า. Verify: ตัด Banking สาขาออกจาก sample → warnings มี Banking + suggestions ['BBL','SCB','KBANK'].

### Reference
```python
# current — _archive/portfolio-simulator-builder-2026-04-25/backend/portfolio_builder.py:9-90 (REUSE 2 functions verbatim)
def niwes_composite_score(stock: dict) -> float:
    dy = stock.get('dividend_yield') or 0
    pe = stock.get('pe_ratio') or 999
    pbv = stock.get('pb_ratio') or 999
    signals = stock.get('signals') or []
    quality = stock.get('score') or 0
    yield_score = min(dy, 8) * 3
    pe_value = max(0, (15 - pe) / 15 * 20) if pe > 0 else 0
    pbv_value = max(0, (1.5 - pbv) / 1.5 * 15) if pbv > 0 else 0
    hidden_bonus = 20 if 'HIDDEN_VALUE' in signals else 0
    quality_contribution = quality * 0.25
    return yield_score + pe_value + pbv_value + hidden_bonus + quality_contribution

DEFAULT_WEIGHTS = [40, 35, 12, 8, 5]

def allocate_80_20(picks: list) -> list:
    picks = picks[:5]
    n = len(picks)
    if n == 0:
        return []
    base = DEFAULT_WEIGHTS[:n]
    total = sum(base)
    weights = [round(w / total * 100, 1) for w in base]
    for s, w in zip(picks, weights):
        s['weight_pct'] = w
    return picks

# new — scripts/portfolio_builder.py
CANONICAL_SECTORS = ['Banking', 'Energy', 'Property', 'REIT-PFund', 'Other']
SECTOR_CLASS_MAP = {
    'Banking': 's-bank', 'Energy': 's-nrg', 'Property': 's-prop',
    'REIT-PFund': 's-purple', 'Other': 's-comm',
}
SECTOR_SUGGESTIONS = {
    'Banking': ['BBL', 'SCB', 'KBANK'],
    'Energy': ['PTT', 'PTTEP', 'BCP'],
    'Property': ['QH', 'AP', 'LPN'],
    'REIT-PFund': ['DIF', 'JASIF', 'CPNREIT'],
}

def to_canonical_sector(raw: str) -> str:
    if not raw or raw.strip() in ('', '-'):
        return 'Other'
    r = raw.lower()
    if 'bank' in r:
        return 'Banking'
    if any(k in r for k in ['energy', 'petroleum', 'refining', 'utilit']):
        return 'Energy'
    if 'reit' in r or 'property fund' in r or 'infrastructure trust' in r:
        return 'REIT-PFund'
    if 'property' in r or 'real estate' in r:
        return 'Property'
    return 'Other'

def enrich_watchlist_stocks(watchlist, screener):
    all_entries = (
        (screener.get('candidates') or [])
        + (screener.get('review_candidates') or [])
        + (screener.get('filtered_out_stocks') or [])
    )
    by_sym = {e.get('symbol'): e for e in all_entries if e.get('symbol')}
    out = []
    for sym in watchlist:
        c = by_sym.get(sym)
        if not c:
            continue
        m = c.get('metrics') or {}
        out.append({
            'symbol': c.get('symbol'),
            'name': c.get('name'),
            'sector': c.get('sector'),
            'sector_canonical': to_canonical_sector(c.get('sector')),
            'dividend_yield': m.get('dividend_yield'),
            'pe_ratio': m.get('pe'),  # NOTE: screener key is 'pe' NOT 'pe_ratio'
            'pb_ratio': m.get('pb_ratio'),
            'current_price': m.get('current_price'),
            'signals': c.get('signals') or [],
            'score': c.get('score'),
        })
    return out

def tag_roles(picks: list) -> list:
    role_map = {1: ('anchor', 'ตัวหลัก'), 2: ('anchor', 'ตัวหลัก'),
                3: ('supporting', 'ตัวรอง'),
                4: ('tail', 'ตัวท้าย'), 5: ('tail', 'ตัวท้าย')}
    for i, p in enumerate(picks, 1):
        role, label = role_map.get(i, ('tail', 'ตัวท้าย'))
        p['rank'] = i
        p['role'] = role
        p['role_label_th'] = label
        p['score_dot'] = 'a' if (p.get('score') or 0) >= 80 else 'b'
        p['sector_class'] = SECTOR_CLASS_MAP.get(p.get('sector_canonical', 'Other'), 's-comm')
    return picks

if __name__ == '__main__':
    # Sample with nested metrics shape (matches real screener)
    sample_screener = {
        'candidates': [
            {'symbol': 'QH', 'name': 'ควอลิตี้เฮ้าส์', 'sector': 'Property Development',
             'metrics': {'dividend_yield': 7.5, 'pe': 11, 'pb_ratio': 0.85, 'current_price': 1.33},
             'score': 92, 'signals': ['NIWES_5555', 'HIDDEN_VALUE']},
            # ... 9 more sample stocks
        ],
        'review_candidates': [], 'filtered_out_stocks': []
    }
    sample_watchlist = ['QH', 'TCAP', 'MC', 'INTUCH', 'PTT', 'BBL', 'CPALL', 'SCC', 'BCP', 'HMPRO']
    result = build_portfolio(sample_watchlist, sample_screener, pins=['QH'])
    import json; print(json.dumps(result, ensure_ascii=False, indent=2))
```

## Phase 2: Backend API + Routes
- [x] เพิ่ม endpoint `GET /api/portfolio/builder` ใน `server/app.py` (วางหลัง `/api/watchlist/compare` ที่บรรทัด ~2487). Query param: `pins: str = ''` (comma-separated). **CRITICAL — import pattern:** `portfolio_builder` ไม่ใช่ Python package (ไม่มี __init__.py) → ต้องใช้ **lazy import per-function** ตาม pattern เดิมของ server/app.py (line 733-735, 957-958, 1040-1041, 2006-2008): `if _project_root not in sys.path: sys.path.insert(0, _project_root)` แล้วค่อย `from scripts import portfolio_builder as pb_mod`. **ห้ามใส่ import ที่ module-level จะ crash startup**. `import hashlib` วาง module-level ได้ (stdlib). Logic: load `user_data.watchlist` ผ่าน `load_user_data()` → load latest screener ผ่าน `_latest_screener_file()` (มีอยู่แล้ว line 1989) → call `pb_mod.build_portfolio(watchlist, screener, pins=pin_list)` → คำนวณ source block: watchlist_count=len(watchlist), scan_at=mtime ของ latest screener file, scan_hours_ago=delta. Return {source, summary, warnings, portfolio, bench}. — scope: ห้ามเรียก Claude หรือ fetch external. — Acceptance: `curl http://localhost:50089/api/portfolio/builder` (with watchlist populated) return 200 + JSON shape ที่ frontend ใช้. `curl ...?pins=QH` return พอร์ตที่ QH เป็น anchor (rank 1, tag PINNED).
- [x] เพิ่ม endpoint `POST /api/portfolio/builder/explain` ใน `server/app.py` (วางต่อจาก /api/portfolio/builder). Body: `{watchlist: list[str], pins: list[str], portfolio: list[dict]}`. Logic: hash request `hashlib.sha256(('|'.join(sorted(watchlist))+'|'+'|'.join(sorted(pins))).encode()).hexdigest()[:16]` → check cache `data/portfolio_opus_cache/{hash}.json` (TTL 7d ตาม `_CACHE_TTL_DAYS` ที่บรรทัด 54) → if cached + fresh return cached → else build prompt (Niwes pillar-1 100M context: 3 ย่อหน้า — (a) scenario ตัวเลข ถ้าใส่ X ล้านที่ avg yield Y% ปันผลปีแรก Z + compound 10y, (b) ตำแหน่งใน pillar 1 (anchor 75% concentration ตามนิเวศน์), (c) Step ถัดไปสำหรับอาร์ท) → call `_anthropic_client.messages.create(model='claude-opus-4-7', max_tokens=4000, messages=[{'role':'user','content':prompt}], timeout=90.0)` ผ่าน `loop.run_in_executor` (replicate pattern จากบรรทัด 1957-1966). **MANDATORY: check stop_reason ตามกฎ Karl 'Claude max_tokens Thai'** — ถ้า `response.stop_reason != 'end_turn'` → `logging.warning(...)` (truncated risk). save cache → return {analyzed_at, model, commentary}. — scope: max_tokens=4000+ + log stop_reason ทุกครั้ง. — Acceptance: POST request return 200 + commentary 3 ย่อหน้า ภาษาไทย. ถ้า MAX_ANTHROPIC_API_KEY ไม่ตั้ง → 503. Server log มี stop_reason check.
- [x] เพิ่ม HTML routes `GET /portfolio` (desktop) + `GET /m/portfolio` (mobile) ใน `server/app.py` ติดกับ block routes ที่บรรทัด 2619-2646. Implementation: 2 route handlers ที่เรียก `_render_shell(_V6_DESKTOP)` และ `_render_shell(_V6_MOBILE)` ตามลำดับ. ไม่สร้างไฟล์ shell HTML ใหม่ — reuse `desktop/index.html` + `mobile/index.html`. — scope: ห้ามแตะ shell template files. — Acceptance: เปิด `http://localhost:50089/portfolio` + `/m/portfolio` ใน browser → render shell + console log โหลด `pages/portfolio.js` หรือ `portfolio.mobile.js`.

### Reference
```python
# current — server/app.py existing patterns
# Lazy import pattern (line 733-735) — REPLICATE THIS
def _some_function():
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    from scripts.fetch_data import fetch_multi_year
    # use it...

# Claude Opus pattern (line 1946-1982) — replicate
@app.post('/api/stock/{symbol}/analyze')
async def trigger_analysis(symbol: str):
    if _anthropic_client is None:
        raise HTTPException(503, 'anthropic package not installed or MAX_ANTHROPIC_API_KEY missing')
    prompt = build_analysis_prompt(symbol)
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: _anthropic_client.messages.create(
            model='claude-opus-4-7', max_tokens=4000,
            messages=[{'role': 'user', 'content': prompt}], timeout=90.0,
        ),
    )
    raw = response.content[0].text.strip()
    # ... parse + cache

# Constants (line 52-54)
_ANALYSIS_CACHE_DIR = PROJECT_DIR / 'data' / 'analysis_cache'
_CACHE_TTL_DAYS = 7

# Route block (line 2619-2630)
@app.get('/', response_class=HTMLResponse)
@app.get('/home', response_class=HTMLResponse)
@app.get('/watchlist', response_class=HTMLResponse)
@app.get('/settings', response_class=HTMLResponse)
async def serve_index():
    return _render_shell(_V6_DESKTOP)

# new — additions in server/app.py (module-level: hashlib only)
import hashlib  # OK at module-level

_PORTFOLIO_OPUS_CACHE_DIR = DATA_DIR / 'portfolio_opus_cache'
_PORTFOLIO_OPUS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@app.get('/api/portfolio/builder')
async def get_portfolio_builder(pins: str = ''):
    # CRITICAL: lazy import (scripts not a package + sys.path)
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    from scripts import portfolio_builder as pb_mod

    user_data = load_user_data()
    watchlist = user_data.get('watchlist') or []
    try:
        screener = _latest_screener_file()
    except HTTPException:
        screener = {'candidates': [], 'review_candidates': [], 'filtered_out_stocks': []}
    pin_list = [p.strip().upper() for p in pins.split(',') if p.strip()]
    result = pb_mod.build_portfolio(watchlist, screener, pins=pin_list)

    # source block — find latest screener file mtime
    files = sorted(DATA_DIR.glob('screener_*.json'), reverse=True)
    if files:
        m_ts = files[0].stat().st_mtime
        scan_at = datetime.fromtimestamp(m_ts).isoformat(timespec='seconds')
        hours_ago = int((datetime.now() - datetime.fromtimestamp(m_ts)).total_seconds() / 3600)
    else:
        scan_at, hours_ago = None, None
    result['source'] = {
        'watchlist_count': len(watchlist),
        'scan_at': scan_at,
        'scan_hours_ago': hours_ago,
    }
    return result

@app.post('/api/portfolio/builder/explain')
async def explain_portfolio(payload: dict):
    if _anthropic_client is None:
        raise HTTPException(503, 'MAX_ANTHROPIC_API_KEY missing')
    watchlist = payload.get('watchlist', [])
    pins = payload.get('pins', [])
    portfolio = payload.get('portfolio', [])
    h = hashlib.sha256(('|'.join(sorted(watchlist)) + '|' + '|'.join(sorted(pins))).encode()).hexdigest()[:16]
    cache_file = _PORTFOLIO_OPUS_CACHE_DIR / f'{h}.json'
    if cache_file.exists():
        cached = json.loads(cache_file.read_text(encoding='utf-8'))
        try:
            age = datetime.now() - datetime.fromisoformat(cached.get('analyzed_at', ''))
            if age < timedelta(days=_CACHE_TTL_DAYS):
                return cached
        except Exception:
            pass
    prompt = _build_portfolio_explain_prompt(portfolio)  # 3-paragraph Niwes pillar-1 prompt
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: _anthropic_client.messages.create(
            model='claude-opus-4-7', max_tokens=4000,
            messages=[{'role': 'user', 'content': prompt}], timeout=90.0,
        ),
    )
    # MANDATORY stop_reason check (Karl rule: Thai output truncate risk)
    if response.stop_reason != 'end_turn':
        logging.warning(
            'explain_portfolio: stop_reason=%s (not end_turn) — Thai may be truncated',
            response.stop_reason
        )
    payload_out = {
        'analyzed_at': datetime.now().isoformat(timespec='seconds'),
        'model': 'claude-opus-4-7',
        'commentary': response.content[0].text.strip(),
    }
    cache_file.write_text(json.dumps(payload_out, indent=2, ensure_ascii=False), encoding='utf-8')
    return payload_out

@app.get('/portfolio', response_class=HTMLResponse)
async def serve_portfolio_desktop():
    return _render_shell(_V6_DESKTOP)

@app.get('/m/portfolio', response_class=HTMLResponse)
async def serve_portfolio_mobile():
    return _render_shell(_V6_MOBILE)
```

## Phase 3: Frontend Nav + Page Modules
- [x] อัปเดต nav 4-tab (3 sub-edits): (1) แก้ `web/v6/static/js/components.js` ฟังก์ชัน `renderMastNav` (บรรทัด 29-60): เพิ่ม `['portfolio', '/portfolio', 'จัดพอร์ต']` ใน items array ระหว่าง watchlist กับ settings. (2) แก้ ฟังก์ชัน `renderMobileNav` (บรรทัด 68-86): เพิ่ม `['portfolio', '/m/portfolio', '◇', 'จัดพอร์ต']` ระหว่าง saved กับ settings. **(3) CRITICAL — แก้ `web/v6/mobile/index.html` บรรทัด 54-57** (mappedActive object): เพิ่ม key `portfolio: 'portfolio'` มิฉะนั้น `/m/portfolio` จะ fallback ไป Home tab active. — scope: ห้ามแก้ icon glyph อื่น, ห้ามเปลี่ยนสีหรือ style. — Acceptance: เปิด /portfolio → header แสดง 4 tabs โดย 'จัดพอร์ต' active. เปิด / → 'LATEST SCAN' active. Mobile: /m/portfolio → bottom nav 4 tabs โดย 'จัดพอร์ต' active (ไม่ใช่ home).
- [x] สร้าง `web/v6/static/js/pages/portfolio.js` (ไฟล์ใหม่) — desktop page module ตาม mockup `mockup/portfolio-from-watchlist-desktop.html`. Export: `mount(root)`. Internal helpers: `_renderShell()` returns 2-col layout HTML (left: pin chips + opus button + algo footer | right: source banner + sector warning + summary strip + sector chart + position list + bench list). `_load(root)` → fetch `/api/portfolio/builder?pins=...` (pins from localStorage `mm-portfolio-pins`) → render. `_renderSourceBanner(host, source)` → render watchlist count + scan_hours_ago + sync button. `_renderWarnings(host, warnings)` — render only if warnings.length>0, each warning card has icon + title + msg + suggestion chips. `_renderPinChips(host, pins)` — chips จาก localStorage with × button + add button (modal input from watchlist symbols dropdown). `_renderSummary(host, summary)`. `_renderSectorChart(host, portfolio)` — segmented bar (5 segments จาก portfolio[].weight_pct + sector_class) + legend below. `_renderPositions(host, portfolio)` — 5 cards each with `<div class='role-badge {role}'>{ROLE EN}<span class='th'>{role_label_th}</span></div>` + sym/name/sector chip + tags + weight_num + score dot + reason + w-track. `_renderBench(host, bench)` — compact rows with sym/name/reason/score-mini. `_bindEvents(root)` — pin chip × → remove + re-fetch | pin add → modal | opus button → `_openOpusModal()`. `_openOpusModal()` — open modal, POST `/api/portfolio/builder/explain`, render commentary 3 ย่อหน้า + analyzed_at timestamp. Use `window.MMApi.{get,post}`, `window.MMComponents.{renderLoading, renderError, openModal, closeModal, showToast}`, `window.MMUtils.escapeHtml`. — scope: ห้าม inline CSS เกินสิ่งที่ mockup ใช้ (mockup ใช้ inline style บางจุด — copy ตาม). ห้ามเรียก Chart.js (sector chart ใช้ pure HTML segmented bar). — Acceptance: เปิด /portfolio → render ตรง mockup desktop 100% ด้วย live data. Add pin → re-fetch → pin stock กลายเป็น anchor. Click opus → modal เปิด + commentary load.
- [x] สร้าง `web/v6/static/js/pages/portfolio.mobile.js` (ไฟล์ใหม่) — mobile variant ตาม mockup `mockup/portfolio-from-watchlist-mobile.html`. Same API + functions structure as desktop module but stacked single-column layout: source banner → sector warning → pin chips → opus button → summary → sector chart → position list (3-row card per `pos-row1`/`pos-row2`/`pos-tags`/`pos-reason`/`w-track` per mockup) → bench list (column rows). — scope: ห้าม share code กับ desktop module (each page module standalone — เพื่อ tree-shake และอ่านง่าย). — Acceptance: เปิด /m/portfolio → render ตรง mockup mobile 100%. Bottom nav 'จัดพอร์ต' active (verify mappedActive fix from task 1).

### Reference
```javascript
// current — web/v6/static/js/components.js:29-86 (3-tab)
function renderMastNav(activeOrCtx) {
  // ... active resolution logic
  var items = [
    ['latest-scan', '/',          'LATEST SCAN'],
    ['watchlist',   '/watchlist', 'WATCHLIST'],
    ['settings',    '/settings',  'SETTINGS']
  ];
  // ... loop builds nav HTML
}

function renderMobileNav(active) {
  var items = [
    ['home',      '/m',                   '⌂', 'Home'],
    ['saved',     '/m/watchlist',         '⌕', 'WATCHLIST'],
    ['settings',  '/m/settings',          '⚙', 'Settings']
  ];
  // ... loop builds bn-item HTML
}

// current — web/v6/mobile/index.html:53-58 (active mapping)
var tabKey = routeFromPath();
var mappedActive = ({
  home: 'home', watchlist: 'saved', saved: 'saved',
  'latest-scan': 'home', settings: 'settings'
})[tabKey] || 'home';

// new — components.js (4-tab)
var items = [
  ['latest-scan', '/',          'LATEST SCAN'],
  ['watchlist',   '/watchlist', 'WATCHLIST'],
  ['portfolio',   '/portfolio', 'จัดพอร์ต'],
  ['settings',    '/settings',  'SETTINGS']
];

var items = [
  ['home',      '/m',                   '⌂', 'Home'],
  ['saved',     '/m/watchlist',         '⌕', 'WATCHLIST'],
  ['portfolio', '/m/portfolio',         '◇', 'จัดพอร์ต'],
  ['settings',  '/m/settings',          '⚙', 'Settings']
];

// new — mobile/index.html:53-58 (add portfolio key)
var mappedActive = ({
  home: 'home', watchlist: 'saved', saved: 'saved',
  'latest-scan': 'home', portfolio: 'portfolio', settings: 'settings'
})[tabKey] || 'home';

// new — pages/portfolio.js skeleton (full impl follows mockup HTML)
export function mount(root) {
  root.innerHTML = _renderShell();
  _bindEvents(root);
  _load(root);
}

async function _load(root) {
  const pins = JSON.parse(localStorage.getItem('mm-portfolio-pins') || '[]');
  try {
    const data = await window.MMApi.get('/api/portfolio/builder?pins=' + encodeURIComponent(pins.join(',')));
    _renderSourceBanner(root.querySelector('#pf-source'), data.source);
    _renderWarnings(root.querySelector('#pf-warnings'), data.warnings);
    _renderPinChips(root.querySelector('#pf-pins'), pins);
    _renderSummary(root.querySelector('#pf-summary'), data.summary);
    _renderSectorChart(root.querySelector('#pf-chart'), data.portfolio);
    _renderPositions(root.querySelector('#pf-positions'), data.portfolio);
    _renderBench(root.querySelector('#pf-bench'), data.bench);
  } catch (e) {
    window.MMComponents.renderError(root, 'โหลดพอร์ตไม่สำเร็จ: ' + (e && e.message || e), function () { _load(root); });
  }
}

// position card render — example showing role-badge usage
function _renderPositionCard(p) {
  const esc = window.MMUtils.escapeHtml;
  const tags = (p.tags || []).map(t => '<span class="tag pass">' + esc(t) + '</span>').join('');
  return (
    '<div class="pos">' +
      '<div class="role-badge ' + p.role + '">' + p.role.toUpperCase() + '<span class="th">' + esc(p.role_label_th) + '</span></div>' +
      '<div class="body">' +
        '<div class="row1"><span class="sym">' + esc(p.symbol) + '</span> <span class="th-name">' + esc(p.name) + '</span> <span class="sector ' + p.sector_class + '">' + esc(p.sector) + '</span></div>' +
        '<div class="tags">' + tags + '</div>' +
      '</div>' +
      '<div class="weight-col"><div class="weight-num ' + (p.role === 'anchor' ? 'anchor' : '') + '">' + p.weight_pct + '%</div><div class="score"><span class="s-dot ' + p.score_dot + '">' + p.score + '</span> Niwes</div></div>' +
      '<div class="reason">' + esc(p.reason) + '</div>' +
      '<div class="w-track"><i style="width:' + (p.weight_pct / 40 * 100) + '%"></i></div>' +
    '</div>'
  );
}
```

## Phase 4: Styles (Tokens + Components)
- [x] เพิ่ม role badge tokens ใน `web/v6/shared/tokens.css` — append หลัง existing `--c-purple-*` tokens (บรรทัด 64). เพิ่มทั้ง light + dark mode (บรรทัด 158 dark @media block). Tokens: `--role-anchor-bg, --role-anchor-fg, --role-support-bg, --role-support-fg, --role-tail-bg, --role-tail-fg`. Light values: anchor=`linear-gradient(135deg, #7ba688, #5d8c69)` fg `#ffffff`, supporting=`linear-gradient(135deg, #e7eaf0, #c9cfdb)` fg `#4a5264`, tail=`#ebebe4` fg `#878d9a`. Dark values: anchor same gradient + #fff fg, supporting=`linear-gradient(135deg, #363c4a, #474e5f)` fg `#c9cfdb`, tail=`#2f343d` fg `#838896`. — scope: ห้ามแก้ token เก่า. — Acceptance: grep `--role-anchor-bg` ใน tokens.css พบทั้ง :root + dark @media block.
- [x] เพิ่ม component CSS ใน `web/v6/static/css/components.css` — append section `/* === PORTFOLIO BUILDER === */`. **CRITICAL — token mapping ก่อน paste verbatim:** mockup HTML ใช้ tokens ที่ production tokens.css ไม่มี — ต้อง search-replace **ทุกครั้ง** ก่อน paste: `var(--radius)` → `18px`, `var(--radius-lg)` → `24px`, `var(--tap)` → `48px`, `var(--font)` → `var(--font-body)`. Other tokens (`--c-positive*`, `--bg-elevated*`, `--btn-on-elevated`, `--shadow-*`) มี production แล้ว ใช้ verbatim ได้. Classes ที่ต้องเพิ่ม (extract จาก mockup desktop+mobile, dedupe): `.role-badge`, `.role-badge.{anchor,supporting,tail}`, `.role-badge .th`, `.src-banner`, `.src-banner .ic/.txt/.sync-btn`, `.sec-warn`, `.sec-warn .ic/.body/code`, `.opus-btn`, `.chip-section`, `.chip-title`, `.chip.pin`, `.chip.add`, `.algo-foot`, `.diversify`, `.dv-head`, `.seg-bar`, `.seg`, `.dv-legend`, `.lg-row/.lg-dot/.lg-label/.lg-val`, `.pos` + grid variant สำหรับ portfolio (ใช้ `auto 2fr auto` 3-col), `.pos .weight-col/weight-num/score/w-track`, sector class `.s-bank/.s-nrg/.s-prop/.s-purple/.s-comm` (verify dup กับ existing — ถ้ามีแล้ว skip), `.bench-list`, `.bench-row`. Mobile-specific stacked variants ใส่ใน existing `@media (max-width: 900px)` block (ไม่ใช่ 768px): `.pos` flex-column + `.pos-row1/pos-row2/pos-tags/pos-reason` styles. **CRITICAL — Bottom-nav 4-col:** **ห้ามแทน `.bottom-nav` block ทั้งหมด** (production ใช้ `left:50%;transform:translateX(-50%);max-width:480px` — เก็บไว้). แก้ตรง **components.css บรรทัด 360 เท่านั้น** เปลี่ยน `grid-template-columns: repeat(3, 1fr)` → `repeat(4, 1fr)`. ห้ามใส่ @media wrapper. — scope: ห้ามแก้ existing watchlist/home/report styles. — Acceptance: เปิด /portfolio + /m/portfolio → visual ตรง mockup 100% (compare side-by-side ใน browser dev tools). Watchlist mobile + Home mobile ยัง render ปกติ (regression check).

### Reference
```css
/* current — web/v6/shared/tokens.css:62-64 (last purple tokens) */
--c-purple:      var(--lavender-500);
--c-purple-soft: #ebe7f4;
--c-purple-fg:   #6a5c9e;

/* current — components.css:350-362 (existing .bottom-nav — 3-col) */
.bottom-nav {
  position: fixed;
  bottom: 0; left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  background: var(--bg-surface);
  border-top: 1px solid var(--border-subtle);
  padding: 8px 12px calc(8px + env(safe-area-inset-bottom));
  display: grid;
  grid-template-columns: repeat(3, 1fr);  /* ← CHANGE THIS LINE ONLY */
  gap: 4px;
  z-index: 60;
}

/* new — append in tokens.css :root (after line 64) */
--role-anchor-bg:  linear-gradient(135deg, #7ba688, #5d8c69);
--role-anchor-fg:  #ffffff;
--role-support-bg: linear-gradient(135deg, #e7eaf0, #c9cfdb);
--role-support-fg: #4a5264;
--role-tail-bg:    #ebebe4;
--role-tail-fg:    #878d9a;

/* new — append in tokens.css @media (prefers-color-scheme:dark) */
--role-anchor-bg:  linear-gradient(135deg, #7ba688, #5d8c69);
--role-anchor-fg:  #ffffff;
--role-support-bg: linear-gradient(135deg, #363c4a, #474e5f);
--role-support-fg: #c9cfdb;
--role-tail-bg:    #2f343d;
--role-tail-fg:    #838896;

/* new — components.css line 360 (EDIT IN PLACE — not a new block) */
grid-template-columns: repeat(4, 1fr);  /* was: repeat(3, 1fr) */

/* new — append section in components.css */
/* === PORTFOLIO BUILDER === */
.role-badge{
  width:auto;padding:0 14px;height:38px;border-radius:10px;  /* literal 10px — mockup used --radius */
  display:inline-flex;align-items:center;gap:8px;font-weight:800;font-size:12px;
  letter-spacing:.04em;text-transform:uppercase;flex-shrink:0;
}
.role-badge.anchor{background:var(--role-anchor-bg);color:var(--role-anchor-fg);box-shadow:var(--shadow-accent-positive)}
.role-badge.supporting{background:var(--role-support-bg);color:var(--role-support-fg)}
.role-badge.tail{background:var(--role-tail-bg);color:var(--role-tail-fg)}
.role-badge .th{font-weight:600;font-size:11px;opacity:.85;text-transform:none;letter-spacing:0}

.src-banner{display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding:14px 20px;border-radius:18px;margin-bottom:8px;background:var(--c-positive-tint);border:1px solid var(--c-positive-border)}
/* ^ note: --radius replaced with literal 18px */
.src-banner .ic{font-size:18px}
.src-banner .txt{font-size:13.5px;color:var(--fg-secondary);font-weight:500}
.src-banner .txt strong{color:var(--c-positive-strong);font-weight:700}
.src-banner .sync-btn{margin-left:auto;font-size:12px;font-weight:700;padding:6px 14px;border-radius:999px;background:var(--btn-on-elevated);border:1px solid var(--c-positive-border);color:var(--c-positive-strong);cursor:pointer}

/* ... continue with sec-warn, opus-btn, diversify, etc.
   — extract from mockup HTML <style> block
   — REPLACE: var(--radius)→18px, var(--radius-lg)→24px, var(--tap)→48px, var(--font)→var(--font-body)
*/
```

## Phase 5: Docs + Smoke Test
- [x] Update `projects/MaxMahon/CLAUDE.md` — แก้ section 'Architecture > Public API' (ค้นหาบรรทัดที่มี `/api/screener`) เพิ่ม `/api/portfolio/builder` (GET) + `/api/portfolio/builder/explain` (POST) + `/portfolio` + `/m/portfolio` HTML routes. แก้ section 'Frontend Layout (v6)' (ค้นหาบรรทัดที่มี `pages/{home,report,watchlist,...}`) เพิ่ม `pages/portfolio.{js,mobile.js}`. แก้ section 'Key Files' (ค้นหาบรรทัดที่มี `scripts/scan.py`) เพิ่ม `scripts/portfolio_builder.py`. ลบ outdated reference เรื่อง Portfolio Builder ของเก่า (capital-based 5 SET sectors) ในส่วน 'Architecture' line 6 ที่ระบุ 'POST /api/stock/{sym}/analyze' — ตรวจไม่ให้กล่าวถึง portfolio builder ของเก่า (ที่ archived แล้ว). — scope: ห้ามแก้ Hard Filters / Quality Score / Signal Tags blocks. — Acceptance: grep `/api/portfolio/builder` ใน CLAUDE.md เจอ. grep `portfolio_builder.py` เจอ. grep `จัดพอร์ต` เจอ.
- [x] Update `projects/MaxMahon/CHANGELOG.md` — เพิ่ม entry บนสุด (above v6.2.0 entry): `## v6.3.0 — 2026-04-25 · Portfolio Builder จาก Watchlist (Niwes role-based)`. Sections: 'New' (feature 'จัดพอร์ตจาก Watchlist' + endpoints + role tagger + bench list + sector warning + Claude Opus pillar-1 commentary) + 'Changed' (nav 3-tab → 4-tab desktop + mobile, watchlist row → clickable to full report) + 'Architecture' (new pure-function module sector canonical mapper). เขียนเป็นภาษาคน ตามกฎ Karl: ห้ามพ่นชื่อ function/symbol ถ้าไม่จำเป็น. — scope: ห้ามแก้ entry เก่า. — Acceptance: head -30 CHANGELOG.md เห็น v6.3.0 ครบ.
- [x] Smoke test ที่ dev server. รัน sequence: (1) start `max-server.bat` (FastAPI port 50089). (2) populate watchlist test ด้วย 10 หุ้น (ถ้าว่าง: PUT /api/user/watchlist กับ {add:['QH','TCAP','MC','INTUCH','PTT','BBL','CPALL','SCC','BCP','HMPRO']}). (3) curl `http://localhost:50089/api/portfolio/builder` → verify JSON shape ครบ {source, summary, warnings, portfolio (5 items with role/weight_pct/reason), bench}. (4) curl `?pins=QH` → verify QH rank=1 + tag=PINNED. (5) curl POST `/api/portfolio/builder/explain` → verify 200 + commentary 3 ย่อหน้า + log มี stop_reason=end_turn. (6) เปิด `http://localhost:50089/portfolio` ใน browser desktop → verify visual ตรง mockup desktop, role badges สีถูก, bench list render, sector warning render, watchlist row click ลิงก์ไป /report ได้. (7) เปิด `http://localhost:50089/m/portfolio` ใน browser mobile (DevTools mobile mode) → verify visual ตรง mockup mobile, bottom nav 4-tab, **'จัดพอร์ต' tab active (ไม่ใช่ home)**. (8) Click pin add modal + add CPALL → verify re-fetch + CPALL anchor (sector Other). (9) Click opus button → verify modal opens + commentary loads. (10) Regression: เปิด /watchlist + /m/watchlist + /m → verify ยัง render ปกติ (no breakage จาก nav/bottom-nav 4-col change). — scope: smoke เท่านั้น ไม่ใช่ unit test. ถ้าเจอ bug → log + handoff /bugfix ถ้าซับซ้อน. — Acceptance: ทั้ง 10 steps ผ่าน. ไม่มี console error ใน browser. existing pages (watchlist, home, settings) ทั้ง desktop + mobile ยัง render ปกติ.

### Reference
```bash
# Smoke test commands (foreground only — Karl rule: ห้ามรัน background server)
cd C:/WORKSPACE/projects/MaxMahon
# In separate terminal:
# ./max-server.bat

# Test API:
curl -s http://localhost:50089/api/portfolio/builder | jq '.summary, .portfolio[].role'
curl -s 'http://localhost:50089/api/portfolio/builder?pins=QH' | jq '.portfolio[0]'
curl -s -X POST http://localhost:50089/api/portfolio/builder/explain \
  -H 'Content-Type: application/json' \
  -d '{"watchlist":["QH","TCAP"],"pins":[],"portfolio":[]}' | jq '.commentary'

# Browser tests:
# /portfolio (desktop) — verify mockup match
# /m/portfolio (mobile DevTools) — verify mockup match + 'จัดพอร์ต' tab active
# /watchlist — regression: existing page still renders
# /m/watchlist — regression
```
