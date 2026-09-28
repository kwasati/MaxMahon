---
project: MaxMahon
created: 2026-04-12
last_updated: 2026-04-12
status: done
---

# Max Mahon Server — Dashboard + API + Tunnel

> เปลี่ยน Max จาก script pipeline เป็น server รัน 24/7 — dashboard ดูข้อมูลหุ้น Buffett+เซียนฮง ตรง mockup 100%, สั่ง scan/analyze/request จาก browser, เข้าได้จากทุกที่ผ่าน Cloudflare Tunnel

## Phase 0: Data Pipeline Patch (เพิ่ม fields ที่ขาด)
- [x] fetch_data.py — เพิ่ม SG&A (Selling General And Administration) ใน yearly_metrics, เพิ่ม avg_gross_margin + avg_operating_margin ใน aggregates (คำนวณจาก yearly_metrics), ทดสอบกับ 3 ตัว (DELTA, PTT, TISCO)
- [x] screen_stocks.py — เพิ่ม 52w_high, pb_ratio, five_year_avg_yield, gross_margins, operating_margins ใน candidate output (ดึงจาก snapshot data ที่ fetch มา), แก้ score breakdown max ใน code comments ให้ตรง (P:30 G:25 D:25 S:20)

### Reference
```python
# fetch_data.py — เพิ่ม SG&A
# ใน yearly_metrics loop:
sga = safe_get(inc, 'Selling General And Administration', col)
metrics['sga'] = sga
if revenue and sga:
    metrics['sga_ratio'] = sga / revenue

# ใน aggregates:
gross_margins = [y['gross_margin'] for y in yearly_metrics if y.get('gross_margin')]
agg['avg_gross_margin'] = sum(gross_margins)/len(gross_margins) if gross_margins else None
op_margins = [y['operating_margin'] for y in yearly_metrics if y.get('operating_margin')]
agg['avg_operating_margin'] = sum(op_margins)/len(op_margins) if op_margins else None
```

```python
# screen_stocks.py — เพิ่ม fields ใน candidate
candidate['metrics']['52w_high'] = data.get('52w_high')
candidate['metrics']['pb_ratio'] = data.get('pb_ratio')
candidate['metrics']['five_year_avg_yield'] = data.get('five_year_avg_yield')
candidate['metrics']['gross_margins'] = data.get('gross_margins')
candidate['metrics']['operating_margins'] = data.get('operating_margins')
```

## Phase 1: Server + API
- [x] สร้าง FastAPI server (server/app.py) — token auth (MAX_TOKEN จาก .env), serve static web/, port 50089; Data API: GET /api/watchlist, /api/screener, /api/stock/{symbol} (merge snapshot+screener: ถ้าหุ้นอยู่ใน screener ให้ merge score+breakdown+signals เข้ากับ snapshot data), /api/history, /api/status; deps: fastapi, uvicorn, python-dotenv
- [x] เพิ่ม Request Analyze API — POST /api/request {symbols: ['CHG.BK','NYT.BK']} สั่งให้ Max fetch+analyze หุ้นที่ไม่อยู่ใน watchlist/universe, ผลลัพธ์เก็บเป็น data/request_{date}_{symbols}.json + reports/request_{date}.md, GET /api/requests list request results; ใช้ fetch_multi_year() + Claude analyze เหมือน pipeline ปกติแต่เฉพาะตัวที่สั่ง

### Reference
```python
# server/app.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
import json
from pathlib import Path

app = FastAPI(title='Max Mahon')
DATA_DIR = Path(__file__).parent.parent / 'data'
REPORTS_DIR = Path(__file__).parent.parent / 'reports'

def find_latest(directory, pattern):
    files = sorted(directory.glob(pattern), reverse=True)
    return files[0] if files else None

def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

@app.get('/api/stock/{symbol}')
async def stock_detail(symbol: str):
    # Merge snapshot + screener
    snap_file = find_latest(DATA_DIR, 'snapshot_*.json')
    scr_file = find_latest(DATA_DIR, 'screener_*.json')
    stock = None
    if snap_file:
        for s in load_json(snap_file)['stocks']:
            if s['symbol'] == symbol:
                stock = s
                break
    if stock and scr_file:
        for c in load_json(scr_file)['candidates']:
            if c['symbol'] == symbol:
                stock['score'] = c['score']
                stock['breakdown'] = c['breakdown']
                stock['signals'] = c['signals']
                stock['reasons'] = c['reasons']
                break
    if not stock:
        raise HTTPException(404)
    return stock
```

```python
# Request analyze endpoint
from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    symbols: list[str]  # e.g. ['CHG.BK', 'NYT.BK']

@app.post('/api/request')
async def request_analyze(req: AnalyzeRequest, bg: BackgroundTasks):
    if pipeline_lock.locked():
        raise HTTPException(409, 'Pipeline running')
    bg.add_task(execute_request, req.symbols)
    return {'status': 'started', 'symbols': req.symbols}

async def execute_request(symbols):
    async with pipeline_lock:
        # 1. fetch_multi_year for each symbol
        # 2. compute quality score
        # 3. call Claude for full analysis
        # 4. save request_{date}_{symbols}.json + request_{date}.md
        pass
```

## Phase 2: Dashboard (ตรง mockup 100%)
- [x] สร้าง web/index.html + web/style.css — copy CSS ทั้งหมดจาก mockup/dashboard.html, HTML structure (header, summary cards, tabs, stock list, detail panel), ทุก class name ต้องตรง mockup, Score breakdown ใช้ max P:30 G:25 D:25 S:20; เพิ่ม request panel (input symbols + submit button + request results list)
- [x] สร้าง web/app.js — Stock List: fetch /api/screener render stock rows (symbol, score circle [high≥75 mid≥50 low<50], signal tags, price, yield); Tab switching (All Passed / Watchlist / Discoveries / Filtered Out / Requests); Click stock → fetch /api/stock/{symbol} render detail; Summary cards (passed count, avg score, discoveries, warnings)
- [x] สร้าง web/app.js — Detail Panel: Buffett 4-col metrics (Profitability: avg_roe, min_roe, avg_net_margin, avg_gross_margin, avg_operating_margin; Moat: roe_consistency [computed], gross_margin_trend [computed], sga_trend [computed from yearly sga_ratio], revenue_consistency; Financial: de_ratio, interest_coverage, current_ratio, fcf_positive [computed], ocf_ni_ratio; Growth: revenue_cagr, eps_cagr, eps_positive [computed], capital_intensity) + เซียนฮง 2-col (Dividend: yield, 5yr_avg_yield, payout, streak, growth_streak, dps_trend [computed]; Valuation: pe, forward_pe, pb_ratio, fcf_yield [computed], 52w_position [computed], earnings_growth); ทุก metric ใช้ details/summary tag กดขยายคำอธิบาย; คำอธิบายทั้ง 24 ตัว copy จาก mockup/dashboard.html ครบถ้วน; null handling แสดง '-' แทน
- [x] สร้าง web/app.js — YoY Table + Dividend Chart + DCA Verdict: YoY table render จาก yearly_metrics (Revenue, Net Income, EPS, ROE, Net Margin, D/E, FCF, DPS) + Trend column [computed: เทียบ YoY แล้วสรุปภาษาไทย]; Dividend bar chart จาก dividend_history (CSS bars เหมือน mockup); DCA Verdict: score≥80=5/5 ≥65=4/5 ≥50=3/5 ≥35=2/5 else=1/5 + auto-generate summary จาก key metrics

### Reference
```javascript
// Metric explanations — copy ทั้งหมดจาก mockup
const EXPLANATIONS = {
  avg_roe: {
    title: 'Return on Equity',
    desc: 'กำไรที่บริษัทสร้างได้จากเงินของผู้ถือหุ้น ยิ่งสูงยิ่งดี Buffett มองว่า 15% ขึ้นไปทุกปี คือธุรกิจคุณภาพ',
    scale: [{label:'20%+ ยอดเยี่ยม',cls:'good'}, {label:'15-20% ดี',cls:'ok'}, {label:'<15% ต่ำ',cls:'bad'}]
  },
  // ... ทั้ง 24 ตัว copy จาก mockup HTML
};

// Score circle class
function scoreClass(score) {
  if (score >= 75) return 'high';
  if (score >= 50) return 'mid';
  return 'low';
}

// Score breakdown max values (ตรง CLAUDE.md)
const SCORE_MAX = { profitability: 30, growth: 25, dividend: 25, strength: 20 };

// Null-safe display
function fmt(val, suffix='', decimals=1) {
  if (val == null) return '-';
  return (val * (suffix === '%' ? 100 : 1)).toFixed(decimals) + suffix;
}

// Trend computation
function computeTrend(values) {
  const valid = values.filter(v => v != null);
  if (valid.length < 2) return '-';
  let ups = 0;
  for (let i = 1; i < valid.length; i++) {
    if (valid[i] > valid[i-1]) ups++;
  }
  const ratio = ups / (valid.length - 1);
  if (ratio >= 0.8) return 'โตทุกปี';
  if (ratio >= 0.5) return 'โตรวม';
  if (ratio >= 0.3) return 'ขึ้นลง';
  return 'ลดลง';
}

// DCA Verdict
function dcaVerdict(score, stock) {
  const stars = score >= 80 ? 5 : score >= 65 ? 4 : score >= 50 ? 3 : score >= 35 ? 2 : 1;
  // Auto-generate summary from key metrics
  const parts = [];
  if (stock.aggregates?.avg_roe > 0.2) parts.push('ทำกำไรสม่ำเสมอสูงกว่า 20% ของทุน');
  if (stock.aggregates?.dividend_streak > 10) parts.push(`จ่ายปันผลมา ${stock.aggregates.dividend_streak} ปีไม่เคยขาด`);
  // ...
  return { stars, summary: parts.join(', ') };
}
```

```html
<!-- Request panel ใน index.html -->
<div class="request-panel">
  <h3>Request Analysis</h3>
  <input type="text" id="req-symbols" placeholder="CHG.BK, NYT.BK, ..." />
  <button onclick="submitRequest()">Analyze</button>
  <div id="req-results"></div>
</div>
```

## Phase 3: Pipeline Control + Reports
- [x] เพิ่ม pipeline API (server/app.py) — POST /api/run/{action} (fetch/analyze/screen/discover/weekly/discovery), asyncio subprocess + lock, SSE /api/events, pipeline status; APScheduler cron (อาทิตย์ 09:00 weekly, สัปดาห์ 2+4 discovery) แทน Task Scheduler
- [x] เพิ่ม reports API — GET /api/reports, GET /api/reports/{type}?date=, markdown→HTML; deps: markdown, apscheduler, sse-starlette
- [x] เพิ่ม UI: action buttons (Fetch/Analyze/Screen/Full Pipeline + confirm), progress indicator, SSE listener auto-refresh, reports tab (list + date picker + rendered HTML)

### Reference
```python
# Pipeline + scheduler
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date

scheduler = AsyncIOScheduler()

def get_week_of_month():
    d = date.today()
    return (d.day - 1) // 7 + 1

async def scheduled_weekly():
    week = get_week_of_month()
    if week in (2, 4):
        await execute_pipeline('discovery')
    else:
        await execute_pipeline('weekly')

@app.on_event('startup')
async def start_scheduler():
    scheduler.add_job(scheduled_weekly, 'cron', day_of_week='sun', hour=9)
    scheduler.start()
```

## Phase 4: Deploy
- [x] สร้าง max-server.bat; เพิ่ม Cloudflare Tunnel ingress (max.intensivetrader.com → localhost:50089); DNS CNAME; อัพเดท CLAUDE.md + CHANGELOG; ลบ Task Scheduler task เดิม; ทดสอบจากภายนอก

### Reference
```yaml
# ~/.cloudflared/config.yml
ingress:
  - hostname: kode.intensivetrader.com
    service: http://localhost:50088
  - hostname: max.intensivetrader.com
    service: http://localhost:50089
  - service: http_status:404
```
