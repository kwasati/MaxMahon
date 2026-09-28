---
project: 4-MaxMahon
created: 2026-05-12
last_updated: 2026-05-12
status: active
---

## Target / Goal

### เป้าหมาย
ทำได้: หุ้นที่ hard_filter คืน status REVIEW จะถูกจัดเข้า candidates[] เหมือน PASS + ติด tag EPS_COVID_REVIEW + ได้คะแนน 100 + มี signals + ขึ้นบนมือถือ + refresh ราคารายวัน + scan report แสดงในรายการหลัก + portfolio_builder ใช้งานได้ตามปกติ — ไม่มี dead-end flow อีกต่อไป

### รายละเอียด
- ปัจจุบัน REVIEW เป็น dead-end (verified ใน agent review):
- - screen_stocks.py:893-911 → review_candidates list แยกจาก candidates
- - screen_stocks.py:915-916 → quality_score เรียกแค่ PASS path
- - screen_stocks.py:1041, 1051 → screener output มี review_count + review_candidates แยก
- - report_template.py:110-115 → '## Review Candidates' section minimal (symbol/sector/reasons)
- - home.js:174 → แสดง review_count summary cell
- - home.js:279 → renderCard loop ใช้ candidates เท่านั้น
- - home.mobile.js → REVIEW absent ทั้งหมด
- - daily_price_refresh.py:57 → iterate candidates[] เท่านั้น
- - portfolio_builder.py:42-46 → pool candidates + review_candidates + filtered_out (ตรงนี้รวมแล้ว แต่ score = N/A สำหรับ REVIEW)
- Implementation: REVIEW stocks เข้า candidates[] + extra field filter_status='REVIEW' + review_reasons[] preserved
- Signal tag ใหม่: EPS_COVID_REVIEW (เพิ่มใน assign_signals function) — flag ใน frontend ว่าเป็น REVIEW
- Backward compat: screener output ยังมี review_candidates[] key (empty list) + review_count = 0 — เพื่อไม่กระทบ /api/screener consumers ที่ดู review_count
- หรือเปลี่ยน schema: review_count = count of EPS_COVID_REVIEW tag ใน candidates[] (semantic ดีกว่า) — เลือก approach นี้
- quality_score รัน REVIEW ด้วย (Plan A ต้องเสร็จก่อน — filter logic stable แล้ว)
- Frontend: home.js + home.mobile.js render REVIEW card เหมือน PASS + extra warning badge CSS class .filter-status-review

### Scope Boundary
**In scope:**
- scripts/screen_stocks.py — main() flow รวม REVIEW เข้า candidates + assign_signals เพิ่ม EPS_COVID_REVIEW tag
- scripts/report_template.py — แสดง REVIEW stocks ในรายการหลัก + badge เตือน
- scripts/daily_price_refresh.py — _load_symbols รวม REVIEW (จาก candidates ใหม่)
- web/v6/static/js/pages/home.js — render REVIEW cards เหมือน PASS + warning badge
- web/v6/static/js/pages/home.mobile.js — same
- web/v6/static/css/components.css — เพิ่ม CSS class .filter-status-review
- server/app.py — /api/screener backward compat (review_count = EPS_COVID_REVIEW tag count)

**Out of scope:**
- Year-completeness fixes (Plan A — must be done first)
- Data source migration (Plan B)
- DPS source (Plan C)
- Normalized EPS (Plan E)
- Other signal tag definitions
- Portfolio builder logic นอกเหนือ REVIEW tag pickup

### Non-goals
- ไม่เพิ่ม UI element นอกเหนือ warning badge (อาจ tooltip explain review reason — เก็บไว้ phase 2 ถ้าจำเป็น)
- ไม่ remove review_candidates[] key จาก screener output (backward compat — empty list)
- ไม่เปลี่ยน hard_filter logic — แค่ downstream handling

# Plan D — REVIEW = PASS + Tag Warning (Full Auto Pipeline Integration)

> Part 4 of 7 — REVIEW unification. REVIEW = PASS + tag เตือน. หุ้น 4/5 EPS positive + 3 ปีล่าสุดบวกติด (COVID exception) → เข้า auto pipeline ปกติ + flag ให้คนเห็น.
> Depends on: filter-01-year-completeness (filter logic ต้องเสถียร — quality_score รัน REVIEW ด้วย)
> Parallel-safe with: filter-02-setsmart-migration, filter-03-dps-yahoo-only, filter-05-normalized-eps (แตะคนละไฟล์)

## Phase 1: assign_signals เพิ่ม EPS_COVID_REVIEW tag
- [ ] แก้ scripts/screen_stocks.py assign_signals function (บรรทัด 565-632) — เพิ่ม logic: ถ้า data.get('filter_status') == 'REVIEW' → append 'EPS_COVID_REVIEW' to signals — Scope: ไม่แก้ existing tags — Acceptance: assign_signals({'filter_status': 'REVIEW', ...}, 75) คืน signals ที่มี EPS_COVID_REVIEW

### Reference
```python
# current (scripts/screen_stocks.py:565-632 — abbreviated)
def assign_signals(data: dict, total: int) -> list[str]:
    signals = []
    # ... existing tag logic (NIWES_5555, NIWES_GROWING, etc.) ...
    return signals

# new — add EPS_COVID_REVIEW
def assign_signals(data: dict, total: int) -> list[str]:
    signals = []
    # ... existing logic ...
    
    # NEW: REVIEW status tag
    if data.get('filter_status') == 'REVIEW':
        signals.append('EPS_COVID_REVIEW')
    
    return signals
```

## Phase 2: main() flow — merge REVIEW into candidates
- [ ] แก้ scripts/screen_stocks.py main() (บรรทัด 700-1068) — เปลี่ยน flow: ถ้า status == 'REVIEW' → data['filter_status'] = 'REVIEW' + data['review_reasons'] = filter_reasons → continue to quality_score path (ไม่ append review_candidates) — Acceptance: REVIEW stocks เข้า candidates[] + มี filter_status field + ได้ quality_score + signals
- [ ] แก้ scripts/screen_stocks.py main() screener output (บรรทัด 1035-1056) — keep review_candidates[] = [] (backward compat) + counts.review = count(filter_status='REVIEW' in candidates) — Acceptance: screener_*.json มี candidates[] รวม REVIEW + review_candidates[] empty + counts.review = จำนวน REVIEW จริง

### Reference
```python
# current (scripts/screen_stocks.py main flow — abbreviated)
status, filter_reasons = hard_filter(data)  # line 872
if status == "FAIL":
    filtered_out += 1
    continue
if status == "REVIEW":  # line 893
    review_entry = {
        'symbol': sym,
        'sector': data.get('sector'),
        'review_reasons': filter_reasons,
        # ... basic_metrics ...
    }
    review_candidates.append(review_entry)
    continue
# status == "PASS"
result = quality_score(data)
candidates.append({...})

# new — REVIEW merges into candidates
status, filter_reasons = hard_filter(data)
if status == "FAIL":
    filtered_out += 1
    continue

# REVIEW and PASS both go through quality_score
data['filter_status'] = status  # 'PASS' or 'REVIEW'
if status == "REVIEW":
    data['review_reasons'] = filter_reasons

result = quality_score(data)
entry = {
    'symbol': sym,
    'sector': data.get('sector'),
    'score': result['score'],
    'signals': result['signals'],  # includes EPS_COVID_REVIEW if REVIEW
    'filter_status': status,
    # ... existing fields ...
}
if status == "REVIEW":
    entry['review_reasons'] = filter_reasons
candidates.append(entry)

# Output JSON (line 1035-1056)
out = {
    # ... existing fields ...
    "review_count": sum(1 for c in candidates if c.get('filter_status') == 'REVIEW'),
    "counts": {
        "passed": sum(1 for c in candidates if c.get('filter_status') == 'PASS'),
        "review": sum(1 for c in candidates if c.get('filter_status') == 'REVIEW'),
        "filtered_out": filtered_out,
    },
    "candidates": candidates,
    "review_candidates": [],  # backward compat — empty
    "filtered_out_stocks": filtered_stocks,
}
```

## Phase 3: Frontend — render REVIEW with warning badge
- [ ] แก้ web/v6/static/css/components.css — เพิ่ม CSS class .filter-status-review (warning color: เช่น border-left 3px solid amber + bg slight tint) — Acceptance: class มีอยู่ใน components.css + DevTools inspect แสดง styles
- [ ] แก้ web/v6/static/js/pages/home.js _renderCard function (บรรทัด 52-140) — ถ้า stock.filter_status == 'REVIEW' → เพิ่ม class 'filter-status-review' ที่ article + แสดง badge 'REVIEW' ตัวเล็กข้าง symbol — Acceptance: REVIEW card มี border สีเตือน + badge text 'REVIEW'
- [ ] แก้ web/v6/static/js/pages/home.mobile.js _renderCard function — same logic — Acceptance: REVIEW card มือถือ render พร้อม warning badge
- [ ] แก้ web/v6/static/js/pages/home.js summary cell (บรรทัด 174) — ดึง review_count จาก screener.summary หรือ screener.review_count (verify schema) + แสดง 'Review' label ตามเดิม — Acceptance: summary แสดงจำนวน REVIEW ถูกต้อง

### Reference
```css
/* web/v6/static/css/components.css — new */
.card.filter-status-review {
    border-left: 3px solid var(--color-warning, #f59e0b);
    background-color: rgba(245, 158, 11, 0.04);
}

.card.filter-status-review .card-sym::after {
    content: 'REVIEW';
    display: inline-block;
    margin-left: 0.5em;
    padding: 0.1em 0.5em;
    font-size: 0.7em;
    background: var(--color-warning, #f59e0b);
    color: white;
    border-radius: 3px;
    vertical-align: middle;
}
```

```javascript
// current (web/v6/static/js/pages/home.js:52-140 abbreviated)
function _renderCard(stock) {
    var sym = stock.symbol;
    // ...
    return '<article class="card" data-sym="' + sym + '">' + ...;
}

// new
function _renderCard(stock) {
    var sym = stock.symbol;
    var statusClass = stock.filter_status === 'REVIEW' ? ' filter-status-review' : '';
    // ...
    return '<article class="card' + statusClass + '" data-sym="' + sym + '">' + ...;
}
```

## Phase 4: Daily price refresh + report + API
- [ ] Verify scripts/daily_price_refresh.py _load_symbols (บรรทัด 41-64) — ตอนนี้ iterate candidates[] เท่านั้น (line 57) — หลัง Plan D, REVIEW อยู่ใน candidates[] แล้ว = auto-included → ไม่ต้องแก้ — Acceptance: cat scripts/daily_price_refresh.py | grep 'candidates' → ยังใช้ candidates[] (loop รวม REVIEW อัตโนมัติ)
- [ ] แก้ scripts/report_template.py (บรรทัด 110-115) — ลบ '## Review Candidates' section หรือเปลี่ยนเป็น '## Review-flagged Candidates' ที่ filter candidates ที่มี filter_status='REVIEW' จาก main list — Acceptance: scan report แสดง REVIEW ในรายการหลักพร้อม badge + section แยกตัด (หรือเป็น sub-section ของ main list)
- [ ] Verify server/app.py /api/screener (บรรทัด 200-273) — ตอนนี้ enrich review_candidates ที่ in_watchlist (บรรทัด 244) + summary review_count (บรรทัด 268) — หลัง Plan D, review_candidates[] = [] + review_count อ่านจาก counts.review ใหม่ — ปรับโค้ดให้อ่าน count จาก candidates ที่มี filter_status='REVIEW' — Acceptance: GET /api/screener คืน summary.review_count ตรงกับจำนวน REVIEW จริงใน candidates

### Reference
```python
# current (scripts/report_template.py:110-115)
report += "\n## Review Candidates\n\n" + (
    "\n".join(
        f"- **{r['symbol']}** ({r.get('sector','')}) — {'; '.join(r.get('review_reasons', []))}"
        for r in review
    ) or "_ไม่มี_"
)

# new — REVIEW อยู่ใน main candidates list, แสดง badge
review_in_candidates = [c for c in candidates if c.get('filter_status') == 'REVIEW']
report += "\n## Review-flagged Candidates (auto-included with warning)\n\n" + (
    "\n".join(
        f"- **{c['symbol']}** ({c.get('sector','')}) score={c.get('score','?')} — "
        f"reason: {'; '.join(c.get('review_reasons', []))}"
        for c in review_in_candidates
    ) or "_ไม่มี_"
)
```

```python
# current (server/app.py:268)
data["summary"] = {
    "total_scanned": ...,
    "passed_count": ...,
    "review_count": len(data.get("review_candidates", []) or []),
}

# new — count from candidates filter_status
review_count = sum(1 for c in (data.get("candidates") or []) if c.get('filter_status') == 'REVIEW')
passed_count = sum(1 for c in (data.get("candidates") or []) if c.get('filter_status') == 'PASS')
data["summary"] = {
    "total_scanned": ...,
    "passed_count": passed_count,
    "review_count": review_count,
}
```

## Phase 5: Smoke test + visual verify
- [ ] รัน py scripts/scan.py --no-write — Acceptance: screener_*.json มี candidates[] รวม PASS+REVIEW + filter_status field ทุก entry + signals มี EPS_COVID_REVIEW สำหรับ REVIEW
- [ ] Visual verify desktop: เปิด http://localhost:50089/ → home page → ดูว่า REVIEW card มี border warning + badge 'REVIEW' — Acceptance: visual ตรงตามที่ออกแบบ (อาร์ทกดดูแล้ว approve)
- [ ] Visual verify mobile: เปิด http://localhost:50089/m → home page → ดูว่า REVIEW card บนมือถือมี badge เตือน — Acceptance: visual ตรงตามที่ออกแบบ (อาร์ทกดดูแล้ว approve)

### Reference
Verify commands:
```bash
cd C:\WORKSPACE\projects\4-MaxMahon
py scripts/scan.py --no-write
# Check output JSON
py -c "
import json
from pathlib import Path
latest = sorted(Path('data').glob('screener_*.json'))[-1]
d = json.loads(latest.read_text(encoding='utf-8'))
review = [c for c in d['candidates'] if c.get('filter_status') == 'REVIEW']
print(f'Total candidates: {len(d[\"candidates\"])}')
print(f'REVIEW in candidates: {len(review)}')
if review:
    print(f'Sample REVIEW signals: {review[0][\"signals\"]}')
"
```

Visual: open browser http://localhost:50089/ + http://localhost:50089/m
