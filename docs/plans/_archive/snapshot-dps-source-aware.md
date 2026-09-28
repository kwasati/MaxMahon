---
project: 4-MaxMahon
created: 2026-05-20
last_updated: 2026-05-20
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: fetch_fundamentals('HTC') แล้ว snapshot fields (dps, dividend_rate, dividend_yield, five_year_avg_yield) คำนวณจาก set.or.th DPS (= dividend_history) ไม่ใช่ yahoo split-adjusted DPS — ค่าจะตรงกับ dividend_history dict ที่ฝั่ง consumer เห็น (1.52/1.05/0.99 ของ HTC ตามจริง ไม่ใช่ split-adjusted)

### รายละเอียด
- Root cause: data_adapter.py:904 + :923 อ่าน DPS จาก `yf_dps_by_fy` ตรงๆ regardless of dividend_source — เมื่อ set.or.th success (dividend_source='set_official') dividend_history ใช้ค่า set.or.th แต่ snapshot ใช้ค่า yahoo → split stocks (HTC/BBL/KBANK/AMATA) snapshot ไม่ match history
- Approach: source-resolved dict — เปลี่ยน 2 จุดให้อ่านจาก `dividend_history` (ถูก resolve source แล้วใน lines 800-817) แทน `yf_dps_by_fy` ตรงๆ → consistent 1 source กับ dividend_history
- Timing gate: ยังคง `yf_fy_complete` เป็น completeness signal — set.or.th ไม่มี completeness dict (key คือ FY ที่จ่ายจริง ไม่บอกว่าปิดงบรึยัง) → ใช้ yahoo timing pattern คุม latest_complete_fy / recent_complete_fys เหมือนเดิม
- Logging: เพิ่ม log line ระบุ snapshot_dps_source = dividend_source (parity กับ tag DPS_SOURCE_YAHOO ที่มีอยู่)
- Implicit fix (โบนัสจาก approach นี้): `payout_ratio` (data_adapter.py:932-942) จะตามไปด้วยอัตโนมัติ เพราะคำนวณจาก `dps_current` ที่แก้ source แล้ว — ไม่ใช่ scope creep แต่เป็น cascade effect ที่ต้องการ (payout = DPS / EPS, EPS จาก thaifin yearly_metrics ยังเหมือนเดิม) → tag QUALITY_DIVIDEND ที่ใช้ payout < 70% จะ recomputed ตามด้วย
- Edge case acceptable: ถ้า set.or.th ขาด FY บางปีที่ yahoo มี → dividend_history.get(fy) = None → snapshot ลด weight (5y avg มี dps น้อยกว่า) — ถือว่า set.or.th = source of truth ตาม CLAUDE.md Rule 0
- Doc sync: update CLAUDE.md Rule 0 NOTE (ลบบรรทัด 'known inconsistency' เพราะ fix แล้ว) + docs/data-sources-guide.md Surprises #0 (mark FIXED)
- Smoke test: รัน fetch_fundamentals('HTC') + fetch_fundamentals('BBL') print snapshot 5 fields (dps, dividend_rate, dividend_yield, five_year_avg_yield, payout_ratio) เทียบกับ dividend_history dict ของแต่ละตัว — pass = match

### Scope Boundary
**In scope:**
- scripts/data_adapter.py lines 899-930 (snapshot DPS block + 5y avg)
- scripts/data_adapter.py inline comment near same block
- projects/4-MaxMahon/CLAUDE.md Rule 0 NOTE block (lines ~52-53)
- projects/4-MaxMahon/docs/data-sources-guide.md Surprises section #0 (line 475)

**Out of scope:**
- Surprises #1 dead code thaifin dividend (batch later)
- Surprises #2 financingCashFlow key collision (batch later)
- Surprises #5 fy_is_complete always yahoo (batch later — set.or.th completeness signal = separate design)
- Surprises #7 SETSMART EOD adjustedPriceFlag (doc only, batch later)
- UI/frontend update (snapshot DPS เปลี่ยน value แต่ schema/key เดิม)
- Re-run weekly scan
- Re-rank Niwes 55 หุ้น (= แยก backlog task `MaxMahon manual ranking refresh`)
- Test framework setup (projects/4-MaxMahon/tests/ ยังไม่มี — smoke test แบบ __main__ ใน script เดิม)

### Non-goals
- ไม่ deprecate yahoo DPS fallback — ยังคงต้องใช้เมื่อ set.or.th fail (Cloudflare block / ไม่มีข้อมูล) → dividend_source='yahoo' + tag DPS_SOURCE_YAHOO เดิม
- ไม่ refactor dividend_source detection logic (try/except branch lines 800-817 OK อยู่แล้ว)
- ไม่ create new completeness dict สำหรับ set.or.th (ใหญ่ + ต้อง design heuristic — แยก task)
- ไม่ rerun weekly_dividend_refresh cron — cache TTL 7 วัน + fix นี้ไม่กระทบ cache (เป็น read-side fix)
- ไม่ลบ raw `yf_dps_by_fy` ตัวแปร — payout_ratio calculation lines 932-942 ยังใช้ผ่าน yearly_metrics.diluted_eps + dps_current แล้ว แต่ตัวแปร yf_dps_by_fy อาจถูก consumer อื่นใช้ (ค้นหา reference ก่อนลบ)
- ไม่ clear `data/analysis_cache/{sym}.json` ใน task นี้ — แต่ flag ว่าหลัง fix + rerank ครบแล้ว ต้อง clear cache (หรือใช้ TTL 7 วัน auto-expire) เพื่อกัน Claude narrative เก่า (อ้าง yield เก่า) ทับ data ใหม่บน UI report page — แยก task หลัง rerank backlog

# Snapshot DPS Source-Aware Fix — Read from dividend_history (set.or.th primary) instead of yahoo dps_by_fy

> แก้ root cause #0 จาก data-sources-guide.md audit — snapshot DPS อ่านจาก yahoo dict ตรงๆ ไม่สน dividend_source ทำให้หุ้นที่มี split (HTC/BBL/KBANK/AMATA) snapshot fields ไม่ตรงกับ dividend_history. แก้แล้วจะ unblock backlog task `MaxMahon manual ranking refresh` (re-rank 55 ตัวด้วย DPS ที่ถูก) + ทำให้ Tier ของ Niwes assessment น่าเชื่อถือ.

## Phase 1: Source-aware fix + doc sync + smoke test
- [x] แก้ `scripts/data_adapter.py` lines 899-906 (latest_complete_fy + dps_current) — เปลี่ยน `yf_dps_by_fy.get(latest_complete_fy)` → `dividend_history.get(latest_complete_fy)` + เพิ่มตัวแปร `snapshot_dps_source = dividend_source if dps_current is not None else None` — scope: ห้ามแตะ `yf_fy_complete` / `complete_fys` (ยังคงเป็น timing gate) — Acceptance: เมื่อ `dividend_source == 'set_official'` → `dps_current` value = set.or.th DPS ของ FY ล่าสุด (HTC FY2024 = 0.99) ไม่ใช่ yahoo split-adjusted
- [x] แก้ `scripts/data_adapter.py` line 923 (recent_dps สำหรับ 5y avg) — เปลี่ยน `yf_dps_by_fy.get(y)` → `dividend_history.get(y)` ทั้ง list comprehension — scope: ห้ามแตะ logic else branch (yahoo fiveYearAvgDividendYield fallback) — Acceptance: HTC 5y avg = mean([0.99, 1.05, 1.52, 1.52, ...]) จาก set.or.th, ไม่ใช่ split-adjusted yahoo values
- [x] แก้ `scripts/data_adapter.py` line 884-887 + 914-918 logging — เพิ่ม snapshot DPS source ใน log message (ทั้ง info success path + warning no-DPS path) — scope: ห้ามเปลี่ยน log level — Acceptance: log line มี `snapshot_dps_source=set_official` (หรือ yahoo) ระบุ source ที่ใช้คำนวณ snapshot DPS
- [x] อ่าน + dedupe + แก้ `projects/4-MaxMahon/CLAUDE.md` lines 50-55 (Rule 0 NOTE block) — ลบบรรทัด '**NOTE — known inconsistency:**' ทั้ง paragraph (line 53) + ปรับ Rule 0 ให้สะท้อน fix (snapshot DPS อ่านจาก dividend_history source-resolved) — scope: ห้ามแก้ Rule 1/2/3 — Acceptance: grep 'known inconsistency' ใน CLAUDE.md ไม่เจอ + Rule 0 อธิบายว่า snapshot DPS reads dividend_history (source-aware)
- [x] อ่าน + แก้ `projects/4-MaxMahon/docs/data-sources-guide.md` line 475 (Surprises #0) — mark `[FIXED 2026-05-20]` ที่ต้น bullet + เพิ่ม note อ้าง commit/fix description — scope: ห้ามลบ bullet (เก็บไว้เป็น audit trail) — Acceptance: line 475 ขึ้นต้น `0. **[FIXED 2026-05-20]** Top-level snapshot DPS...`
- [x] เพิ่ม smoke test ที่ท้าย `scripts/data_adapter.py` ใน `if __name__ == '__main__':` block (หรือ append ถ้ามีอยู่) — รัน `fetch_fundamentals('HTC.BK')` + `fetch_fundamentals('BBL.BK')` print 5 snapshot fields (dps, dividend_rate, dividend_yield, five_year_avg_yield, **payout_ratio**) + dividend_history dict + dividend_source — เช็คให้ครบทั้ง snapshot ที่เปลี่ยน source + ของแถม payout_ratio ที่ตามไปด้วย — scope: ห้ามรัน inline (smoke ต้อง explicit `py scripts/data_adapter.py`) — Acceptance: รัน `py C:/WORKSPACE/projects/4-MaxMahon/scripts/data_adapter.py` แล้วได้ output: HTC dividend_source=set_official + dps ตรงกับ dividend_history[latest_fy] + 5y avg = mean(dividend_history values 5y ล่าสุด)/price * 100 + payout_ratio = dps_current / yearly_metrics[latest_fy].diluted_eps

### Reference
```python
# current (data_adapter.py:899-906)
        # --- Dividend: DPS-first, yield = DPS/price (Fiscal Year Attribution per SET methodology) ---
        complete_fys = sorted([y for y, ok in yf_fy_complete.items() if ok])
        latest_complete_fy = complete_fys[-1] if complete_fys else None

        if latest_complete_fy is not None:
            dps_current = yf_dps_by_fy.get(latest_complete_fy)
        else:
            dps_current = None

# new
        # --- Dividend: DPS-first, yield = DPS/price (Fiscal Year Attribution per SET methodology) ---
        # Source-resolved: read from dividend_history (set.or.th primary, yahoo fallback)
        # — yf_fy_complete still gates timing (set.or.th has no completeness dict)
        complete_fys = sorted([y for y, ok in yf_fy_complete.items() if ok])
        latest_complete_fy = complete_fys[-1] if complete_fys else None

        if latest_complete_fy is not None:
            dps_current = dividend_history.get(latest_complete_fy)
            snapshot_dps_source = dividend_source if dps_current is not None else None
        else:
            dps_current = None
            snapshot_dps_source = None
```

```python
# current (data_adapter.py:920-923)
        # five_year_avg_yield = avg DPS of last 5 COMPLETE FYs / current price
        current_year = datetime.now().year
        recent_complete_fys = complete_fys[-5:] if len(complete_fys) >= 5 else complete_fys
        recent_dps = [yf_dps_by_fy.get(y) for y in recent_complete_fys if yf_dps_by_fy.get(y) is not None]

# new
        # five_year_avg_yield = avg DPS of last 5 COMPLETE FYs / current price
        # Source-resolved: read from dividend_history (matches dps_current source)
        current_year = datetime.now().year
        recent_complete_fys = complete_fys[-5:] if len(complete_fys) >= 5 else complete_fys
        recent_dps = [dividend_history.get(y) for y in recent_complete_fys if dividend_history.get(y) is not None]
```

```python
# current (data_adapter.py:884-887 + 914-918 — logging)
            logger.info(
                "SETSMART snapshot primary for %s (price=%s pe=%s pbv=%s mcap=%s dy=%s)",
                symbol, price, pe_ratio, pb_ratio, market_cap, dy_snapshot,
            )
# ...
            logger.warning(
                "no yahoo DPS for %s (latest_complete_fy=%s, dps_current=%s, price=%s) — "
                "dy unset (SETSMART cold + yahoo DPS unavailable; thaifin DPS approximation NOT used)",
                symbol, latest_complete_fy, dps_current, price,
            )

# new
            logger.info(
                "SETSMART snapshot primary for %s (price=%s pe=%s pbv=%s mcap=%s dy=%s dps_source=%s)",
                symbol, price, pe_ratio, pb_ratio, market_cap, dy_snapshot, snapshot_dps_source,
            )
# ...
            logger.warning(
                "no DPS for %s (latest_complete_fy=%s, dps_current=%s, price=%s, dps_source=%s) — "
                "dy unset (no DPS in dividend_history for latest complete FY; thaifin DPS approximation NOT used)",
                symbol, latest_complete_fy, dps_current, price, snapshot_dps_source,
            )
```

```markdown
# current (CLAUDE.md:50-55)
**Rule 0 — SETSMART precedence:**
- SETSMART = primary for realtime aggregate snapshot — **price, P/E, P/BV, market cap** (lines 878-881). For `dividend_yield`, SETSMART EOD `dividendYield` is only a **secondary fallback**; primary is computed `dps_current / price * 100` where `dps_current` = yahoo `dps_by_fiscal_year[latest_complete_fy]` (data_adapter.py:903-913).
- SETSMART also overrides 5y yearly ROE/ROA/D-E in `yearly_metrics` (sets `m["roe"]`, `m["roa"]`, `m["de_ratio"]` where year matches; adds `m["eps_setsmart"]` as new key — does NOT overwrite `diluted_eps`)
- set.or.th = primary for `dividend_history` FY event totals (Layer 0.5, Playwright-bootstrapped)
- **NOTE — known inconsistency:** `dividend_history` is built from set.or.th, but `dps_current`/`dividend_rate`/`five_year_avg_yield`/computed `dividend_yield` all read from **yahoo's** `dps_by_fiscal_year` regardless of `dividend_source` (lines 904, 923). When `DPS_SOURCE_YAHOO` is tagged the two are consistent; otherwise the snapshot DPS does NOT match `dividend_history`. See `docs/data-sources-guide.md` Surprises section.

# new
**Rule 0 — SETSMART precedence:**
- SETSMART = primary for realtime aggregate snapshot — **price, P/E, P/BV, market cap** (lines 878-881). For `dividend_yield`, SETSMART EOD `dividendYield` is only a **secondary fallback**; primary is computed `dps_current / price * 100` where `dps_current` = `dividend_history[latest_complete_fy]` (source-resolved: set.or.th primary, yahoo fallback per `dividend_source`).
- SETSMART also overrides 5y yearly ROE/ROA/D-E in `yearly_metrics` (sets `m["roe"]`, `m["roa"]`, `m["de_ratio"]` where year matches; adds `m["eps_setsmart"]` as new key — does NOT overwrite `diluted_eps`)
- set.or.th = primary for `dividend_history` FY event totals (Layer 0.5, Playwright-bootstrapped) — snapshot `dps_current`/`dividend_rate`/`five_year_avg_yield`/computed `dividend_yield` all read from this same `dividend_history` dict (source-aware fix 2026-05-20)
- `yf_fy_complete` still gates timing for `latest_complete_fy` (set.or.th has no completeness dict — keys = FY paid, not FY closed)
```

```markdown
# current (docs/data-sources-guide.md:475)
0. **Top-level snapshot DPS ignores `dividend_source`:** when set.or.th succeeds, `dividend_history` is built from set.or.th — but the snapshot fields `dps`, `dividend_rate`, `dividend_yield` (computed), and `five_year_avg_yield` read from **yahoo's** `dps_by_fiscal_year` regardless (`scripts/data_adapter.py:904, 923`). The values typically agree, but for stocks with stock splits the yahoo DPS is split-adjusted and the set.or.th `dividend_history` is not — so a downstream UI showing both will see mismatched numbers. Fix: change line 904/923 to read from set.or.th's `dps_by_fiscal_year` when `dividend_source == "set_official"`.

# new
0. **[FIXED 2026-05-20]** **Top-level snapshot DPS ignores `dividend_source`:** when set.or.th succeeds, `dividend_history` is built from set.or.th — but the snapshot fields `dps`, `dividend_rate`, `dividend_yield` (computed), and `five_year_avg_yield` previously read from **yahoo's** `dps_by_fiscal_year` regardless (`scripts/data_adapter.py:904, 923`). For stocks with stock splits the yahoo DPS is split-adjusted and the set.or.th `dividend_history` is not — so a downstream UI showing both saw mismatched numbers. **Fix applied:** snapshot block now reads from `dividend_history` (source-resolved) — `yf_fy_complete` still gates timing. **Implicit cascade:** `payout_ratio` (lines 932-942) auto-corrects because it uses `dps_current`; tag `QUALITY_DIVIDEND` (payout < 70%) recomputes accordingly.
```
