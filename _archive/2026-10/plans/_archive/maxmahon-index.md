---
project: 4-MaxMahon
created: 2026-05-16
last_updated: 2026-05-18
status: active
---

## Target / Goal

### เป้าหมาย
ทำได้: เปิดไฟล์ index นี้ -> รู้ build order ที่ถูก (infra ก่อน scoring), อันไหนเป็น test gate, อันไหน archive + เปิด plan ที่ active ตัวจริงต่อได้ทันที (ไม่ต้องเดา + ไม่ข้าม phase)

### รายละเอียด
- MaxMahon มี 3 phase **sequential ห้ามข้าม**: Phase 1 Infrastructure -> Test Gate -> Phase 2 Scoring Discussion DONE -> Phase 3 Anchor Implementation
- **[CRITICAL] ห้ามข้าม Phase 1 -> Phase 3** — infra ต้องครบ + test gate ผ่านก่อน implementation รวมถึง standalone scan (อาร์ท reminder 2026-05-18: "ต้อง build infra ให้เสร็จก่อน แล้ว test แล้วค่อยไปทำอย่างอื่นต่อ")
- Infrastructure status (audit 2026-05-17 + content verify 2026-05-18):
  - filter-01 DONE 2026-05-17 (commit `e0995fb`)
  - filter-02 PARTIAL ~30% (8 tasks ค้าง) — SETSMART primary 5y quarterly
  - filter-03 PARTIAL ~50% (5 tasks ค้าง, depend filter-02 Phase 3) — DPS yahoo-only
  - filter-07 TODO 0% (12 tasks) — flake retry queue (robustness)
- **Build order ภายใน Phase 1 (sequential):**
  - filter-02 Phase 1-3 (SETSMART adapter + routing + fetch_fundamentals primary)
  - filter-03 Phase 1 (remove thaifin DPS fallback — depend filter-02 Phase 3)
  - filter-02 Phase 4-5 (scheduler + smoke)
  - filter-03 Phase 2 (verify DPS)
  - **TEST GATE 1**: smoke scan 5 หุ้น BBL/PTT/CPALL/KBANK/SCB — verify DPS ถูก + yahoo call ลด >50%
  - filter-07 Phase 1-5 (flake queue, depend filter-01 + filter-03)
  - **TEST GATE 2**: simulate flake + retry success
- Phase 2 Scoring Discussion: DONE 2026-05-18 v1.0 RELEASE — scoring-anchor-spec.md ครบ Phase 1-7
- Phase 3 Anchor Implementation: rewrite scoring-redesign-config-refactor.md (STALE — design ผิด) ตาม spec v1.0 + sector taxonomy + standalone scan — **block until Phase 1 Test Gates ผ่านครบ**
- **Build order Phase 3 (multi-plan):**
  - Plan 01: Extend _build_aggregates 21 fields + assign Stage 1-6 tags (gap analysis 2026-05-18: 88% missing)
  - Plan 02: Anchor scoring core + sector taxonomy + standalone scan
  - **TEST GATE 3**: scan universe 933 หุ้น -> ดู TOP anchor candidates ปัจจุบัน
- Archive ไปแล้ว 4 plans (filter-04/05/06/08) -> .claude/plans/4-MaxMahon/_archive/
- Reference plans (ไม่ใช่ build target): niwes-refactor-v2-design (parent design FINAL Stage 1-6) + stage7-research (artifact) + scoring-formula-discussion (discussion plan DONE)

### Scope Boundary
**In scope:**
- .claude/plans/4-MaxMahon/ ทั้ง folder — index + active plans + archived
- Build order documentation + test gates

**Out of scope:**
- Implementation code (อยู่ใน plan แต่ละไฟล์)
- Spec content (อยู่ใน plan แต่ละไฟล์)

### Non-goals
- ไม่ resurrect archived plans
- ไม่ implement anything ใน index นี้ - แค่ orchestrate
- ห้ามข้าม phase order — infra -> test gate -> scoring -> implementation

# MaxMahon Master Index — Build Order + Plan Status

> Master index ของ MaxMahon plans — ระบุ build order, plan status, dependency, test gates. เปิดไฟล์นี้ก่อนเริ่มงาน MaxMahon ทุกครั้ง

## Phase 1: Infrastructure (RESUME — block Phase 3)

**Build order ภายใน Phase 1 (sequential — ไม่ parallel):**

- [x] /build filter-01-year-completeness — **DONE 2026-05-17** (commit `e0995fb`). 5 task เสร็จ: forward fy_is_complete param ลง streak + CAGR + EPS exclude current year + 2 keys ใน config.json. Smoke 5 หุ้นผ่าน (BBL streak 21 / PTT 20 / KBANK 19 / SCB 4)
- [x] /build filter-02-setsmart-migration **Phase 1-3** — **PARTIAL ~30%**. เสร็จ: EOD bulk cache + SETSMART snapshot override skeleton (data_adapter.py:830-861). ค้าง Phase 1-3: cached_financial_by_symbol_range() + smoke 6 + _setsmart_financial_to_yearly() + refactor _fetch_setsmart + fetch_fundamentals SETSMART primary (skip yahoo redundant). Acceptance Phase 1-3: SETSMART range cache ใช้งานได้ + fetch_fundamentals snapshot จาก SETSMART
- [x] /build filter-03-dps-yahoo-only **Phase 1 only** — **PARTIAL ~50%**. ค้าง Phase 1: grep audit + ลบ thaifin DPS fallback (data_adapter.py:774) + warning log. **Depend filter-02 Phase 3** (fetch_fundamentals refactor). Acceptance Phase 1: no thaifin DPS derivation
- [x] /build filter-02 **Phase 4-5** — scheduler job + smoke. Acceptance: cron daily 19:00 financial refresh + 5 หุ้น smoke ผ่าน + yahoo API call ลด >50%
- [x] /build filter-03 **Phase 2** — verify DPS. Acceptance: BBL DPS 2010=5.0 + streak >= 20 + growth_streak >= 3
- [x] **TEST GATE 1 — Infra Critical** — smoke scan 5 หุ้น (BBL/PTT/CPALL/KBANK/SCB) confirm DPS accurate + SETSMART primary + yahoo call <50% baseline. Acceptance: ทุกหุ้น DPS match yahoo events + scan output stable
- [x] /build filter-07-flake-retry-queue — **TODO 0%** (12 tasks). Depend filter-01 + filter-03 DONE. Tasks: flake_queue.py module + JSON queue + hard_filter PENDING + daily retry + telegram stale alert + API + UI (home.js + home.mobile.js). Acceptance: yahoo flake -> queue + daily retry + 0 false FAIL + stale alert
- [x] **TEST GATE 2 — Infra Robustness** — simulate flake + retry success + stale alert trigger. Acceptance: หุ้นที่ recover แล้ว push back to candidates

### Reference
Status check ก่อน /build ทุก plan: open file -> Phase 0 (ถ้ามี) -> resume review -> confirm no design change ตั้งแต่ create_date

Dependency: filter-03 Phase 1 depend filter-02 Phase 3 (fetch_fundamentals refactor). filter-07 depend filter-01 + filter-03 DONE. Sequential order ภายใน Phase 1 ห้าม parallel

Test gates บังคับก่อนข้ามไป Phase 3 — ถ้า data quality ไม่ stable scoring จะ misleading

Audit 2026-05-17 + content verify 2026-05-18: design ทั้ง 4 plans ยัง valid (ไม่ขัด project CLAUDE.md ปัจจุบัน — Data Source Invariants + Scan Pipeline 3 Stages ยัง compat)

Reference: parent plan niwes-refactor-v2-design.md section 5 ระบุ 'Keep' ทั้ง 4 — Infrastructure ไม่ผูก scoring framework

## Phase 2: Niwes Refactor — Scoring Spec Discussion DONE
- [x] **Scoring Spec v1.0 RELEASE 2026-05-18** — All Phases 1-7 FINAL (4 ด้าน 35/25/25/15 + disqualify 3 + penalty 5 + verify 5 หุ้น + TOC + DEFAULT_SCORING_CONFIG dict + display 0.0-10.0). Acceptance MET — docs/scoring-anchor-spec.md v1.0 FINAL

### Reference
Status: COMPLETE — scoring-formula-discussion.md status: complete

Spec output: `C:\WORKSPACE\projects\4-MaxMahon\docs\scoring-anchor-spec.md` v1.0

Design model FINAL:
- ระบบ 2 ขา: anchor score (คุณภาพล้วน) + DCA signal (ราคาแยก)
- น้ำหนัก 4 ด้าน: ปันผล 35 / cash flow 25 / moat 25 / ถือยาว+ทนวิกฤต 15
- Disqualify (anchor=0): FAKE_PROFIT, CASHFLOW_DETERIORATING, MOAT_ERODING
- Penalty: YIELD_TRAP −15, DIVIDEND_SHRINKING −10, ROE_FUELED_BY_DEBT −10, CASHFLOW_BELOW_PROFIT −5, CYCLICAL_BUSINESS −5
- Display: internal 100 / UI 0.0-10.0 (1 decimal)

Reference: scoring-formula-discussion.md (status: complete) + niwes-refactor-v2-design.md

## Phase 3: Niwes Refactor — Anchor Implementation (BLOCKED until Phase 1 Test Gates)

**Status: BLOCKED — รอ Test Gate 2 ผ่าน**

- [x] /plan rewrite scoring-redesign-config-refactor.md (STALE) ตาม spec v1.0 — break เป็น multi-plan:
  - **Plan 01: Extend _build_aggregates + Stage tags** — เพิ่ม 21 missing fields (rising_ratio, ccr_avg_3y, roe_consecutive_15plus_years, eps_cv_10y, crisis_drop_pct ฯลฯ) + assign Stage 1-6 tags (GROWING_DIVIDEND, CASHFLOW_HEALTHY, STRONG_MOAT, STABLE_BUSINESS, MOAT_ERODING ฯลฯ)
  - **Plan 02: Anchor scoring + sector taxonomy + standalone scan** — anchor_scoring.py (load DEFAULT_SCORING_CONFIG + compute 4 ด้าน + disqualify + penalty + display_scale 10) + sector_taxonomy.py + scan_anchor.py standalone script (ไม่ replace existing quality_score / scan.py)
  - **anchor-scoring-index.md** orchestrate
- [x] **TEST GATE 3 — Anchor Scan** — รัน standalone scan 933 หุ้น -> output markdown report TOP candidates per anchor band -> validate Niwes invariant ทำงาน (PTT/SCC/CPALL ตก / ADVANC/BDMS เห็น)
- [x] **Full refactor (UI/API) DONE 2026-05-18 v1.1** — replace existing quality_score in main pipeline + update report.js + home.js + server endpoints — ทำหลัง standalone scan OK

### Reference
Existing plan `scoring-redesign-config-refactor.md` = STALE (role classification design ผิด, header warning). ห้าม build ตามเนื้อหาเดิม

Reference สำหรับ rewrite:
- `C:\WORKSPACE\projects\4-MaxMahon\docs\scoring-anchor-spec.md` v1.0 — source ของ DEFAULT_SCORING_CONFIG dict + 4 ด้าน calculation
- `niwes-refactor-v2-design.md` Stage 1-6 FINAL — tag rules
- Gap analysis 2026-05-18: 88% aggregates missing + Stage 1-6 tags ยังไม่ assign ใน screen_stocks.py — ต้อง extend _build_aggregates + assign_anchor_stage_tags() ก่อน scoring core

**Critical reminder:** ห้ามข้าม Test Gate 1 + 2 (infra) -> infra ผ่านก่อน scoring ใช้ data ที่ valid (ไม่งั้น TOP candidates มั่ว — data ผันผวน yahoo flake)
