---
project: MaxMahon
created: 2026-04-23
last_updated: 2026-04-23
status: done
---

# Stock Detail Polish — Δ Score + Niwes+Pillar-1 Prompt + Inline UX + Price As-of + Daily Refresh

> 5 fixes จาก user feedback รอบ production review (2026-04-23): (1) Δ SCORE bug — backend ส่ง null, ต้อง back-fill entry_score + compute delta, (2) Claude Opus prompt rewrite — ทิ้ง legacy 3-perspective (Buffett/เซียนฮง/Max) เปลี่ยนเป็น 4 section วิเคราะห์ Niwes (Dividend/Hidden/Moat/Valuation) + 1 section Max คุยกับอาร์ท (contextual dialog แปะเข้ากับเสาหลัก 1 พอร์ตปันผล 100M) + verdict BUY/HOLD/SELL, (3) UX: ปุ่มขอวิเคราะห์ + ผล ต้อง inline ที่เดียวกัน, (4) ราคาปัจจุบัน + as-of date แสดงบน card หน้าแรก + full report, (5) daily price refresh scheduler 19:00 เพื่อให้ as-of date fresh (ไม่ stale ตาม weekly scan)

## Phase 1: Backend — Δ score endpoint + price_as_of field
- [x] แก้ `projects/MaxMahon/server/app.py` endpoint `/api/watchlist/{symbol}/exit-status` (ประมาณบรรทัด 2121) — ตรวจ logic ที่ build `entry_context` dict: ต้องมี `delta_score = current_score - entry_score` ถ้า entry_score มีใน baseline. ถ้า entry_score หาย (baseline เก่าที่สร้างก่อน entry_score field ถูกเพิ่ม) → back-fill จาก latest screener_*.json (หา symbol นี้ใน candidates → เอา score ล่าสุด → save กลับเข้า baseline file + set เป็น entry_score). คำนวณ delta_score = current_score - entry_score (current จาก screener candidate). — scope: ไม่แก้ save_exit_baseline ใน screen_stocks.py — Acceptance: `curl http://localhost:50089/api/watchlist/BBL.BK/exit-status` ตอบ 200 + `entry_context.delta_score` เป็น number (ไม่ใช่ null)
- [x] แก้ `projects/MaxMahon/server/app.py` `_normalize_stock()` function — ensure response includes `price_as_of` field = วันที่ราคาที่ใช้. ใช้ priority: (1) `data/price_cache/{sym}.json` ถ้ามี (จาก daily scheduler Phase 3), (2) screener_data['date'] ถ้า stock จาก screener, (3) `datetime.now().strftime('%Y-%m-%d')` fallback. เพิ่ม field top-level ของ normalized dict. — scope: ไม่แก้ current_price logic — Acceptance: `curl http://localhost:50089/api/stock/BBL.BK` response มี field `price_as_of` เป็น YYYY-MM-DD string

### Reference
```python
# new logic conceptual
# exit-status endpoint: back-fill entry_score if missing
if baseline.get('entry_score') is None:
    for c in screener.get('candidates', []):
        if c.get('symbol') == symbol:
            baseline['entry_score'] = c.get('score')
            save_baseline(symbol, baseline)
            break
entry_context['delta_score'] = (current_score - baseline['entry_score']) if baseline.get('entry_score') is not None else None

# _normalize_stock: add price_as_of (priced_cache file > screener date > now)
result['price_as_of'] = _resolve_price_as_of(symbol)

def _resolve_price_as_of(symbol):
    cache_file = DATA_DIR / 'price_cache' / f'{symbol}.json'
    if cache_file.exists():
        return json.loads(cache_file.read_text()).get('fetched_at', '').split('T')[0]
    return screener_data.get('date') or datetime.now().strftime('%Y-%m-%d')
```

## Phase 2: Backend — Niwes+Pillar-1 Prompt Rewrite (6 keys: dividend/hidden/moat/valuation/to_art/verdict)
- [x] Rewrite `projects/MaxMahon/server/app.py` function `_build_analysis_prompt` (บรรทัด 1883-1956) — เปลี่ยนจาก legacy 3-perspective (Buffett / เซียนฮง / Max) → Niwes-only 4 sections + 1 Max-to-Art conversational section + verdict. Output JSON 6 keys: {dividend, hidden, moat, valuation, to_art, verdict}. **สำคัญ — Max persona + pillar-1 context MUST be in prompt:** (a) ระบุ Max = AI stock analyst ที่คุยกับ 'อาร์ท' แบบเพื่อน ไม่ stiff (ใช้สรรพนาม 'อาร์ท' หรือ 'คุณ' ไม่ใช้ กู/มึง), (b) inject Karl's goal context: 'เป้าหมายอาร์ท = เสาหลัก 1 พอร์ตปันผล 100M, passive income target 10M/ปี, DCA ยาว 10-20 ปี, กรอบ ดร.นิเวศน์ 5 sector กระจาย 80/20', (c) `to_art` section ต้องเป็น **3 paragraphs** (conversational): scenario ตัวเลขจริง (เช่น 'ถ้าอาร์ทใส่ 10M ที่ yield X% = ปีแรก Y บาท, compound 10y ที่ DPS growth 5%...') + ตำแหน่งใน pillar 1 (sector fit + concentration 80/20) + Step ถัดไปสำหรับอาร์ท (เช่น 'ลอง DCA simulator 20y scenarios...'), (d) 4 analysis sections (dividend/hidden/moat/valuation) ยัง neutral tone — วิเคราะห์อย่างเดียว, (e) verdict = BUY/HOLD/SELL + เหตุผล 1 ประโยค ผ่าน DCA 10-20y + dividend-first lens. — scope: ไม่แตะ parse_analysis_response (Task ถัดไป) — Acceptance: `grep -c 'Buffett\|เซียนฮง\|exit_check' server/app.py` ต้อง 0. `grep -c 'to_art\|อาร์ท\|เสาหลัก 1\|100M' server/app.py` ≥ 4
- [x] แก้ `projects/MaxMahon/server/app.py` function `parse_analysis_response` + cache payload ใน `trigger_analysis` endpoint (บรรทัด 2052-2062) — update JSON keys จาก {buffett, hong, max} → {dividend, hidden, moat, valuation, to_art, verdict}. รักษา backward compat: ถ้า parse ไม่ได้ให้ return empty string ไม่ crash. Cache payload dict ก็ใช้ keys ใหม่. — Acceptance: POST `/api/stock/BBL.BK/analyze` response body มี keys ใหม่ครบ 6 ตัว (dividend/hidden/moat/valuation/to_art/verdict) + ไม่มี buffett/hong/max/exit_check

### Reference
```python
# current (server/app.py:1931-1956) — legacy prompt
# 3-perspective Buffett/เซียนฮง/Max

# new — Niwes 4-angle + Max-to-Art conversation + verdict
return f"""คุณกำลังสวมบทบาท 'Max' — AI stock analyst ส่วนตัวของ 'อาร์ท' (user) Max = เพื่อนสนิทที่เชี่ยวชาญหุ้นปันผลไทย สไตล์ ดร.นิเวศน์ เหมวชิรวรากร

**เป้าหมายของอาร์ท (context สำคัญ — อ้างอิงใน section Max คุยกับอาร์ท เสมอ):**
- เสาหลัก 1 = พอร์ตหุ้นปันผลไทย มูลค่าเป้าหมาย 100,000,000 บาท
- Passive income target = 10,000,000 บาท/ปี จากปันผล
- Horizon = DCA 10-20 ปี (ไม่ trade สั้น)
- Framework = ดร.นิเวศน์ 5-5-5-5 → กระจาย 5 sector × 80/20 concentration (anchor 40% + supporting 35% + 3 tails 25%)

**Tone guidance:** Max คุยกับอาร์ทแบบเพื่อน ไม่ formal — ใช้สรรพนาม 'อาร์ท' หรือ 'คุณ' (ห้าม กู/มึง), ใส่ตัวเลขจริง (เงินลงทุน, ปันผลที่จะได้, yield-on-cost projection), ชี้ทิศทางว่าทำยังไงต่อ ไม่ใช่แค่ข้อมูล

**ข้อมูลหุ้น {sym} ({name}):**
- คะแนน: {score}/100 (ปันผล {bd.get('dividend',0)}/50 + ราคา {bd.get('valuation',0)}/25 + cash flow {bd.get('cash_flow',0)}/15 + hidden {bd.get('hidden_value',0)}/10)
- Sector: {sector} | Mcap: {mcap_str}
- Yield: {yield_str}% | Payout: {payout_str}% | streak: {streak}y | FCF+: {fcf_pos}/{fcf_total}
- Rev CAGR: {rev_cagr_str}% | EPS CAGR: {eps_cagr_str}% | ROE: {avg_roe_str}%
- D/E: {de_str} | Int Cov: {int_cov_str}x | OCF/NI: {ocf_ni_str}x
- Valuation: {grade} ({label}) | PEG: {peg_str} | ราคา: {price_str} | 52w: {low52}-{high52}
- สัญญาณ: {signals_str}

**งานของคุณ — 4 analysis + 1 dialog + verdict:**

1. **Dividend Sustainability** (neutral analysis, 3-5 ประโยค) — จ่ายกี่ปี? payout ยั่งยืน? FCF รองรับ? DPS growth trajectory?
2. **Hidden Value Audit** (neutral, 3-5 ประโยค) — cross-holdings / land bank / non-core asset ตลาดไม่ pricing in?
3. **Business Moat (Thai market)** (neutral, 3-5 ประโยค) — structural ยืนนานไหม? daily-use? เทียบคู่แข่ง sector?
4. **Valuation Discipline** (neutral, 3-5 ประโยค) — PE vs sector median + self 5y? PBV <1? yield ≥5% ตอนนี้ + 5 ปีหน้า?

5. **Max คุยกับอาร์ท** (conversational — Max → อาร์ท, 3 ย่อหน้าสั้น):
   - ย่อหน้า 1 = scenario ตัวเลขจริง: 'ถ้าอาร์ทใส่ X M ที่ yield Y% = ปันผลปีแรก Z บาท compound 10 ปีที่ DPS growth 5% → yield-on-cost ประมาณ ...' (ใช้เลขจริงจากข้อมูลหุ้น)
   - ย่อหน้า 2 = ตำแหน่งใน pillar 1: 'ใน sector [X] ถ้าเอาเข้า pillar 1 จะทำหน้าที่ anchor/supporting/tail? concentration กี่ % ของ 100M? กระจายกับหุ้นตัวไหนใน sector เดียวกัน?'
   - ย่อหน้า 3 = Step ถัดไป: 'อาร์ทลอง [action เฉพาะ — เช่น DCA simulator 20y scenarios, ดู historical dividend, เทียบกับหุ้น sector เดียวกัน]'

6. **verdict** — BUY / HOLD / SELL + เหตุผล 1 ประโยค (lens = DCA 10-20y + dividend-first + pillar 1 fit)

**ตอบ JSON (ไม่มี text นอก JSON):**
{{"dividend":"...", "hidden":"...", "moat":"...", "valuation":"...", "to_art":"ย่อหน้า 1...\n\nย่อหน้า 2...\n\nย่อหน้า 3...", "verdict":"BUY|HOLD|SELL + reason"}}"""

# parse_analysis_response + cache payload
def parse_analysis_response(raw: str) -> dict:
    import json, re
    try:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(m.group(0)) if m else {}
    except Exception:
        data = {}
    return {k: str(data.get(k, '')) for k in ('dividend', 'hidden', 'moat', 'valuation', 'to_art', 'verdict')}

# trigger_analysis cache payload
payload = {
    'analyzed_at': datetime.now().isoformat(timespec='seconds'),
    'model': 'claude-opus-4-7',
    **parsed,  # spreads dividend/hidden/moat/valuation/to_art/verdict
}
```

## Phase 3: Backend — Daily Price Refresh Scheduler (19:00 post-market)
- [x] สร้างไฟล์ใหม่ `projects/MaxMahon/scripts/daily_price_refresh.py` — function `refresh_prices()` ที่: (1) รวมรายชื่อ symbols = watchlist (จาก user_data.json) + PASS candidates (จาก latest screener_*.json), (2) batch fetch ราคาปัจจุบันจาก yahooquery `Ticker(chunk).price` (batch size 20), (3) บันทึก `{sym: {price, fetched_at}}` ลงในไฟล์ `data/price_cache/{sym}.json`. Rate limit: sleep 0.2s ระหว่าง batch. Error tolerance: ถ้า sym fail → log + continue. — scope: ไม่แตะ data_adapter / fetch_data — Acceptance: `py scripts/daily_price_refresh.py` รันได้ + สร้าง `data/price_cache/BBL.BK.json` มี field `price` + `fetched_at` ISO format
- [x] แก้ `projects/MaxMahon/server/app.py` APScheduler config — เพิ่ม cron job `scheduled_price_refresh_job` ทุกวันเวลา 19:00 timezone Asia/Bangkok (หลังตลาดปิด 17:00 + buffer 2h). Job = call `refresh_prices()` จาก `scripts/daily_price_refresh.py`. Log start/end + count. เพิ่ม admin endpoint `POST /api/admin/price-refresh/trigger` สำหรับ manual trigger. — scope: ไม่เปลี่ยน weekly scan schedule — Acceptance: `curl -X POST http://localhost:50089/api/admin/price-refresh/trigger -H 'Authorization: Bearer $MAX_TOKEN'` ตอบ 200 + สร้าง/update ไฟล์ใน `data/price_cache/`

### Reference
```python
# scripts/daily_price_refresh.py (new)
"""Daily price refresh for watchlist + PASS candidates.
Scheduled 19:00 Asia/Bangkok (post SET close 17:00 + 2h buffer).
"""
import json, logging, time
from datetime import datetime
from pathlib import Path
from yahooquery import Ticker

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
USER_DATA = ROOT / 'user_data.json'
CACHE_DIR = DATA_DIR / 'price_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
logger = logging.getLogger(__name__)

def _load_symbols():
    symbols = set()
    if USER_DATA.exists():
        user = json.loads(USER_DATA.read_text(encoding='utf-8'))
        symbols.update(user.get('watchlist', []))
    screeners = sorted(DATA_DIR.glob('screener_*.json'), reverse=True)
    if screeners:
        s = json.loads(screeners[0].read_text(encoding='utf-8'))
        for c in s.get('candidates', []):
            if c.get('symbol'): symbols.add(c['symbol'])
    return sorted(symbols)

def refresh_prices() -> dict:
    symbols = _load_symbols()
    logger.info(f'refreshing {len(symbols)} symbols')
    fetched = {}
    for i in range(0, len(symbols), 20):
        chunk = symbols[i:i+20]
        try:
            tk = Ticker(chunk)
            prices = tk.price
            for sym in chunk:
                info = prices.get(sym) if isinstance(prices, dict) else None
                if not isinstance(info, dict): continue
                price = info.get('regularMarketPrice')
                if price is None: continue
                payload = {'symbol': sym, 'price': price, 'fetched_at': datetime.now().isoformat(timespec='seconds')}
                (CACHE_DIR / f'{sym}.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
                fetched[sym] = price
        except Exception as e:
            logger.warning(f'batch {i} failed: {e}')
        time.sleep(0.2)
    logger.info(f'refreshed {len(fetched)}/{len(symbols)} prices')
    return fetched

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(f'OK — {len(refresh_prices())} prices refreshed')


# server/app.py — add scheduler + admin endpoint
from apscheduler.triggers.cron import CronTrigger

def scheduled_price_refresh_job():
    logger.info('daily price refresh — START')
    sys.path.insert(0, str(PROJECT_DIR / 'scripts'))
    from daily_price_refresh import refresh_prices
    r = refresh_prices()
    logger.info(f'daily price refresh — DONE ({len(r)} prices)')

scheduler.add_job(
    scheduled_price_refresh_job,
    trigger=CronTrigger(hour=19, minute=0, timezone='Asia/Bangkok'),
    id='daily_price_refresh',
    replace_existing=True,
)

@app.post('/api/admin/price-refresh/trigger')
async def admin_trigger_price_refresh():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, scheduled_price_refresh_job)
    return {'status': 'ok', 'message': 'price refresh triggered'}
```

## Phase 4: Frontend — Price + as-of display on home + report
- [x] แก้ `projects/MaxMahon/web/v6/static/js/pages/home.js` + `home.mobile.js` — screener candidate cards เพิ่ม price + as-of date display, format: `฿43.50 · ณ 23 เม.ย. 68` (Thai short date Buddhist year จาก price_as_of). Helper function: Gregorian YYYY + 543 = Thai year, month = เดือนย่อ ('ม.ค.', 'ก.พ.', ... 'ธ.ค.'). อ่านจาก `candidate.metrics.current_price` + `candidate.price_as_of`. ใช้ var(--font-mono) สำหรับตัวเลข + var(--fg-dim) สำหรับ date. — scope: ไม่แตะ card layout หลัก — Acceptance: เปิด `/` + `/m/` → ทุก card มีราคา + วันที่ Thai format (ไม่ใช่ YYYY-MM-DD dash format)
- [x] แก้ `projects/MaxMahon/web/v6/static/js/pages/report.js` + `report.mobile.js` — full report page แสดง current_price + as-of date prominently ใน hero section ด้านบน (ก่อน 5-5-5-5 Hard Filters). Format: `฿43.50 THB · ราคาวันที่ 23 เม.ย. 68` (ขนาดใหญ่ 36px bold mono). Layout: gradient bg (var(--bg-elevated-start) → var(--bg-elevated-end)) + border subtle, 22px padding, radius lg. Reference: mockup `mockup/stock-detail-polish.html` section 02 (report-hero). — Acceptance: เปิด `/m/report/BBL.BK` → hero section ด้านบนแสดงราคาขนาดใหญ่ + as-of

## Phase 5: Frontend — Inline Analysis UX (4 analysis + Max-to-Art + verdict badge)
- [x] Rewrite `projects/MaxMahon/web/v6/static/js/pages/report.mobile.js` function `_renderDeepAnalyze()` (บรรทัด 264-273) + click handler — change UX จาก button+jump → inline flow: กดปุ่ม → spinner ที่เดิม → POST `/api/stock/{sym}/analyze` → render ผลที่ตำแหน่งปุ่มเดิม. Layout ผล (อ้างอิง mockup `mockup/stock-detail-polish.html` section 06): (a) meta header (analyzed_at + cache hint), (b) **verdict card** ด้านบน (badge BUY=sage / HOLD=dim / SELL=rose + why reason), (c) 4 neutral sections แนวตั้ง: Dividend (icon 💵), Hidden Value Audit (💎), Business Moat (🏛️), Valuation Discipline (⚖️), (d) **Max คุยกับอาร์ท section สุดท้าย** ด้วย distinct sage-tint background + icon 💬 + pillar tag 'เสาหลัก 1 · พอร์ตปันผล 100M' + 3 paragraphs content. ถ้า cache hit จาก GET `/api/stock/{sym}/analysis` → auto-render (ไม่ต้องรอกด). Error → retry button. — scope: ไม่เพิ่ม share/export feature — Acceptance: เปิด `/m/report/BBL.BK` → กดปุ่ม 'ขอวิเคราะห์เพิ่มเติม' → spinner ที่เดิม → ผล 6 parts render: verdict(top) + 4 neutral sections + Max-to-Art(sage tint bg, last) ในตำแหน่งปุ่มเดิม
- [x] Rewrite desktop version ใน `projects/MaxMahon/web/v6/static/js/pages/report.js` — **ใช้ pattern เดียวกับ mobile** (single column stacked, ไม่แยก sidebar): verdict card → 4 sections → Max-to-Art section สุดท้าย. รองรับ 6 keys (dividend/hidden/moat/valuation/to_art/verdict). Max-to-Art section ใช้ CSS class `.art-talk` สีเดียวกับ mobile (sage tint). Icons เดียวกัน (💵 💎 🏛️ ⚖️ 💬). — scope: ไม่ redesign desktop layout อื่น — Acceptance: `/report/BBL.BK` desktop กดปุ่ม → inline expand ที่เดิม + visual feel ตรงกับ mobile (Max-to-Art highlighted สุด)

## Phase 6: End-to-end verify
- [x] Smoke test ผ่าน TestClient + server: (1) Δ SCORE — `curl /api/watchlist/BBL.BK/exit-status | jq .entry_context.delta_score` ต้องเป็น number (ไม่ใช่ null). (2) Prompt — `curl -X POST /api/stock/BBL.BK/analyze` response body มี keys 6 ตัว: dividend/hidden/moat/valuation/**to_art**/verdict (ไม่มี buffett/hong/max/exit_check). to_art content ต้องกล่าวถึง 'อาร์ท' หรือ 'เสาหลัก' หรือ '100M' อย่างน้อย 1 คำ (prove prompt context landed). (3) Price as-of — `curl /api/stock/BBL.BK | jq .price_as_of` เป็น YYYY-MM-DD. (4) Daily price refresh — `curl -X POST /api/admin/price-refresh/trigger` 200 + ไฟล์ `data/price_cache/BBL.BK.json` มี fetched_at เป็นเวลาปัจจุบัน. (5) Home card + report hero — open browser เห็นราคา + วันที่ Thai format. (6) Inline analysis UX — กดปุ่มวิเคราะห์ใน `/m/report/BBL.BK` → loading ที่เดิม → ผล render 6 parts (verdict + 4 sections + Max-to-Art) ที่ตำแหน่งเดียวกับปุ่ม. — Acceptance: 6/6 checks ผ่าน
