---
project: 4-MaxMahon
created: 2026-06-08
last_updated: 2026-06-11
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: GET /api/portfolio/state คืนพอร์ตจริง (holdings + ราคา cache + สัดส่วนจริง vs เป้า + deficit + นอกแผน) ; POST /api/portfolio/topup ใส่เงินแล้วได้แผนซื้อแบบดึงกลับเป้า ; PUT /api/portfolio/holdings กรอก/แก้จำนวนหุ้น+เงินสด แล้ว state อัปเดต

### รายละเอียด
- สร้าง data/portfolio.json = single source ของพอร์ตจริง (ไม่ใช้ per-user เพราะ single-user): holdings{sym:{shares,avg_cost}} + cash(number) + targets{sym:pct} + off_plan{sym:{shares,avg_cost,mode}} + lh_triggers + meta{group:niwes/hong/cash per sym, sector, name, thesis}
- targets (เป้าสัดส่วน) seed ค่าจริง: AMATA 35 / BBL 22.5 / TCAP 12.5 / TOA 7.5 / SISB 7.5 / SECURE 6.25 / MOSHI 3.75 / cash 5
- off_plan seed: LH {mode:watch} + TISCO {mode:hold} (ไม่นับฐานคำนวณดึงกลับเป้า)
- holdings seed = ว่างหรือค่าตัวอย่าง (อาร์ทกรอกจริงผ่าน PUT ทีหลัง) — ห้าม hardcode เลขสมมติเป็นของจริง
- calculator ดึงกลับเป้า (pure function rebalance_topup): ฐานใหม่ = sum(holdings_value)+cash+new_money ; target_value[i]=ฐานใหม่*target_pct[i] ; deficit[i]=max(0,target_value[i]-current_value[i]) ; ถ้า new_money<=sum(deficit) เกลี่ย new_money*deficit[i]/sum(deficit) ; ถ้า new_money>sum(deficit) เติมเต็ม deficit ก่อน ส่วนเกินเกลี่ยตาม target_pct ; shares_to_buy=floor(topup_baht/price) (cash ช่องไม่มี price = ลงเป็นเงินตรงๆ)
- ราคาอ่านจาก data/price_cache/{sym}.json field price (เขียนโดย daily_price_refresh) — เขียน reader ใหม่ ไม่ใช่ _resolve_price_as_of (ตัวนั้นคืน date ไม่ใช่ price)
- metrics การ์ด (yield/PE/PBV/ROE/payout/streak/thesis/sector/name) อ่านจาก data/portfolio.json meta + price_cache ; ตัวเลข fundamental ดึงจาก screener ล่าสุดถ้ามี ไม่มี = ใช้ static ใน meta (seed จาก snapshot 2026-05-22)
- LH signals: คืน 3 trigger state (เด้งขาย 3.90-4.10 / หลุดรับ 3.50,3.18 / พื้นฐาน) เทียบ price ล่าสุด คืน status off/warn/danger
- ทุก API ใช้ Depends(get_current_user) ตามเดิม (เก็บ auth)

### Scope Boundary
**In scope:**
- data/portfolio.json (สร้างใหม่)
- scripts/portfolio_state.py (สร้างใหม่ — reader + calculator pure functions + price reader + LH signal)
- server/app.py — เพิ่ม 4 API: GET /api/portfolio/state, PUT /api/portfolio/holdings, POST /api/portfolio/topup, GET /api/portfolio/lh-signals

**Out of scope:**
- frontend (plan 02)
- archive routes + auth change (plan 03)
- portfolio_builder.py 80/20 (ไม่แตะ — คนละ feature ; reuse ได้แค่ to_canonical_sector ถ้าจำเป็น)
- daily_price_refresh.py + data_adapter.py (ไม่แตะ)

### Non-goals
- ไม่เก็บ holdings ใน user_data per-user (single-user = portfolio.json เดียว)
- ไม่ดึงราคา realtime ตอน request (ใช้ cache ที่ refresh 19:00 พอ)
- ไม่คำนวณ tax/commission (topup = เงินดิบ)

### Skill Flow
- /build -> /qc -> /done

### Stop Conditions
- price_cache ไม่มีไฟล์บางตัว (symbol ไม่เคย refresh) -> หยุดถาม จะ fallback ยังไง
- deficit ทุกตัว = 0 (พอร์ตเกินเป้าหมดหรือตรงเป้าหมด) แต่มีเงินเข้า -> ยืนยัน logic ส่วนเกินเกลี่ยตาม target_pct
- screener ล่าสุดไม่มี symbol ในพอร์ต -> ใช้ static meta แทน

### Report-Back Contract
- verdict
- files touched
- API ทดสอบด้วย curl ผ่านไหม
- calculator unit case
- unresolved

# Portfolio Redesign 01 — Backend (state + calculator + API)

> Part 1 of 4 — Backend: data/portfolio.json + portfolio_state.py + 4 API | Index: portfolio-redesign-index
> Depends on: none
> Parallel-safe with: none (03 แตะ app.py เหมือนกัน ต้อง sequential)

## Phase 1: Data schema + seed
- [x] สร้าง data/portfolio.json ตาม schema (holdings/cash/targets/off_plan/lh_triggers/meta) — seed targets + off_plan + meta(group/sector/name/thesis/fundamental) จาก snapshot 2026-05-22 ; holdings+cash seed = 0 หรือว่าง (อาร์ทกรอกเอง) — scope: ไม่ hardcode เลขหุ้นสมมติเป็น holdings จริง — Acceptance: json valid + มี 7 sym ใน targets รวม + cash 5 = 100 ; off_plan มี LH(watch)+TISCO(hold)
- [x] เพิ่ม load_portfolio()/save_portfolio() ใน scripts/portfolio_state.py (atomic write เหมือน user_data_io.save) — Acceptance: load คืน dict ตาม schema, save เขียนกลับ + stamp updated_at

### Reference
# user_data_io.py save pattern (line 86) อ้างอิงวิธี atomic write + stamp
# DEFAULT shape (portfolio.json):
# {
#   "targets": {"AMATA":35,"BBL":22.5,"TCAP":12.5,"TOA":7.5,"SISB":7.5,"SECURE":6.25,"MOSHI":3.75,"cash":5},
#   "holdings": {"AMATA":{"shares":0,"avg_cost":0}, ...},
#   "cash": 0,
#   "off_plan": {"LH":{"shares":0,"avg_cost":4.00,"mode":"watch"},"TISCO":{"shares":0,"avg_cost":103.16,"mode":"hold"}},
#   "lh_triggers": {"sell_zone":[3.90,4.10],"support":[3.50,3.18]},
#   "meta": {"AMATA":{"name":"อมตะ คอร์ปอเรชัน","sector":"นิคมอุตสาหกรรม","group":"niwes","thesis":"...","yield":5.31,"pe":7.5,"pbv":1.0,"roe":13.9,"payout":40,"streak":"..."}, ...},
#   "updated_at": null
# }

## Phase 2: Price reader + state builder
- [x] เพิ่ม read_price(sym) ใน portfolio_state.py — อ่าน data/price_cache/{sym}.json field 'price' (strip .BK ถ้าจำเป็น) คืน float หรือ None — scope: ไม่แก้ daily_price_refresh — Acceptance: read_price('AMATA') คืนราคาจาก cache, sym ไม่มี cache คืน None
- [x] เพิ่ม build_state() ใน portfolio_state.py — รวม holdings+ราคา = current_value/pct ต่อตัว, เทียบ targets = deficit/over, สรุปรวม (total_value, cash_pct, count ตรงเป้า/เกิน/ขาด), แนบ meta + off_plan(พร้อมราคา+P/L) — Acceptance: คืน dict ที่ frontend render การ์ดได้ครบทุก field ใน mockup

### Reference
# price_cache file format (เขียนโดย daily_price_refresh.py line 1071+):
# data/price_cache/{symbol}.json = {"symbol":"AMATA","price":20.70,"fetched_at":"...","source":"setsmart"}
# NOTE: app.py _resolve_price_as_of() (553-585) อ่านแค่ fetched_at (date) ไม่ใช่ price — ต้องเขียน reader ใหม่อ่าน field price
# current_value[sym] = holdings[sym].shares * read_price(sym)
# pct[sym] = current_value[sym] / total_value * 100 ; deficit เทียบ targets[sym]

## Phase 3: Calculator ดึงกลับเป้า
- [x] เพิ่ม rebalance_topup(state, new_money) ใน portfolio_state.py (pure function) — คำนวณ deficit-based fill ตาม logic ใน details — scope: เฉพาะ 7 ตัวในแผน + cash (off_plan ไม่นับ) — Acceptance: case1 new_money<=sum(deficit) เกลี่ยตาม deficit ratio ; case2 new_money>sum(deficit) เติมเต็มแล้วส่วนเกินตาม target_pct ; case3 deficit=0 ทั้งหมด เกลี่ยตาม target_pct ; sum(topup)=new_money เป๊ะ ; shares_to_buy=floor(topup/price)

### Reference
# rebalance_topup logic:
# base_new = sum(current_value) + cash + new_money
# target_val[i] = base_new * targets[i]/100
# deficit[i] = max(0, target_val[i] - current_value[i])
# total_def = sum(deficit)
# if new_money <= total_def: topup[i] = new_money * deficit[i]/total_def
# else: topup[i] = deficit[i] + (new_money-total_def) * targets[i]/sum(targets_in_plan)
# shares_to_buy[i] = floor(topup[i] / price[i])  (ยกเว้น cash = topup ตรงๆ)
# return [{sym, status:under/over/ok, deficit_pct, price, shares_to_buy, baht}]

## Phase 4: API endpoints
- [x] เพิ่ม GET /api/portfolio/state ใน server/app.py — เรียก build_state() คืน JSON — Depends(get_current_user) — Acceptance: curl คืน holdings+ราคา+pct+deficit+off_plan+meta
- [x] เพิ่ม PUT /api/portfolio/holdings ใน server/app.py — body {holdings:{sym:{shares,avg_cost}}, cash, off_plan} -> save_portfolio() -> คืน state ใหม่ — Acceptance: PUT แล้ว GET state สะท้อนค่าใหม่
- [x] เพิ่ม POST /api/portfolio/topup ใน server/app.py — body {new_money} -> rebalance_topup() คืนแผนซื้อ — Acceptance: POST 100000 คืน list ตัวขาดพร้อม shares_to_buy, ตัวเกินขึ้น baht=0
- [x] เพิ่ม GET /api/portfolio/lh-signals ใน server/app.py — เทียบ price LH กับ lh_triggers คืน 3 สัญญาณ status — Acceptance: คืน 3 trigger พร้อม off/warn/danger

### Reference
# app.py API pattern (existing): @app.get('/api/...') + user=Depends(get_current_user)
# portfolio builder API อยู่ line 2794-2927 = ตัวอย่าง pattern เรียก pure function จาก scripts/
# import: from scripts.portfolio_state import build_state, save_portfolio, rebalance_topup, lh_signals
