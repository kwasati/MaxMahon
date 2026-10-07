"""Drop Stage 7 from niwes-refactor-v2-design.md plan.

Decision (2026-05-15): Stage 7 dropped because Stage 1-6 already covers
quality + dividend resilience + crisis test. Stage 7 value-add (SET50/mcap/age)
deemed insufficient vs cost (new data source + maintenance).
"""

from pathlib import Path

PLAN = Path(r"C:\WORKSPACE\.claude\plans\4-MaxMahon\niwes-refactor-v2-design.md")
text = PLAN.read_text(encoding="utf-8")

# Edit 1 — Status line (line 3)
old = "**Status:** Phase 1 (Spec) — Stage 1+2+3+4+5+6 ออกแบบเสร็จ, Stage 7 ค้าง"
new = "**Status:** Phase 1 (Spec) — Stage 1-6 ออกแบบเสร็จครบ (Stage 7 ตัดทิ้ง 2026-05-15)"
assert old in text, "Status line not found"
text = text.replace(old, new)

# Edit 2 — Architecture diagram (line 32)
old = "L2: 7 Stage Tag Classification  ->  ทุกตัวได้ป้าย + raw data ครบ"
new = "L2: 6 Stage Tag Classification  ->  ทุกตัวได้ป้าย + raw data ครบ"
assert old in text, "Architecture diagram L2 not found"
text = text.replace(old, new)

# Edit 3 — Section 2.2 header (line 50)
old = "### 2.2 7 Stage Framework (จาก Niwes 8 บท + Thai market reality)"
new = "### 2.2 6 Stage Framework (จาก Niwes 8 บท)"
assert old in text, "Section 2.2 header not found"
text = text.replace(old, new)

# Edit 4 — Remove Stage 7 row from table (line 60)
old = "| 7 | NEW | อำนาจตลาด? (monopoly / pillar) | ค้าง — design หลัง Stage 6 |\n"
new = ""
assert old in text, "Stage 7 table row not found"
text = text.replace(old, new)

# Edit 5 — Remove entire Section 2.7d (lines 776-804)
# Find start: "### 2.7d Stage 7" / End: before "### 2.8 Scoring Redesign"
start_marker = "### 2.7d Stage 7 — อำนาจตลาด (TBD — design ตามนี้)"
end_marker = "### 2.8 Scoring Redesign (TBD)"
start_idx = text.find(start_marker)
end_idx = text.find(end_marker)
assert start_idx >= 0 and end_idx >= 0 and end_idx > start_idx, "Section 2.7d/2.8 markers not found"

# Replace whole Section 2.7d block with a Decision log note
decision_log = """### 2.7d Stage 7 — ตัดทิ้ง (Decision 2026-05-15)

**Reason:**
- Stage 1-6 ครอบ quality + dividend resilience + crisis test ครบแล้ว
- Stage 7 candidate tag (PILLAR_STOCK 4 เงื่อนไข SET50 + mcap >=100B + listed >=15y + dividend 10y unbroken):
  - [d] dividend 10y unbroken ทับซ้อน Stage 2 (consecutive_no_cut + streak)
  - [a]+[b]+[c] ใหม่จริง แต่ value-add น้อย — `STRONG_MOAT` (Stage 4) + `RESILIENT_THROUGH_CRISIS` (Stage 5) บอกเรื่องเดียวกันใกล้เคียง
- DELTA case ที่กังวล (ใหญ่+เก่าแต่ผันผวน) — Stage 4 (ROE swing) + Stage 5 (CYCLICAL_BUSINESS) จับได้แล้ว
- Cost ที่ตัดได้: scrape SET50 semi-annual list + IPO listing date factsheet + 6-month refresh maintenance

**Research artifact (kept for reference):** `C:\\WORKSPACE\\.claude\\plans\\4-MaxMahon\\stage7-research.md` — 391-line synthesis (Niwes book + SET50 + Graham defensive + global investor criteria)

**Framework final = 6 stages** (no Stage 7)

"""
text = text[:start_idx] + decision_log + text[end_idx:]

# Edit 6 — Section 2.9 mention "7 stage" → "6 stage"
old = "- Input ใหม่ตาม Niwes framework (raw data + tag จาก 7 stage)"
new = "- Input ใหม่ตาม Niwes framework (raw data + tag จาก 6 stage)"
assert old in text, "Section 2.9 7-stage mention not found"
text = text.replace(old, new)

# Edit 7 — Section 2.10 "ทุก tag ที่ design (7+TBD)"
old = "- ทุก tag ที่ design (7+TBD) → มี definition + ตัวอย่าง"
new = "- ทุก tag ที่ design (6 stage รวม ~37 tags) → มี definition + ตัวอย่าง"
assert old in text, "Section 2.10 tag count mention not found"
text = text.replace(old, new)

# Edit 8 — Scope Boundary line 835
old = "- Refactor pipeline 4 layer ใหม่ (Hard Filter → 7 Stage Tag → Scoring → Display → Claude Analyze)"
new = "- Refactor pipeline 4 layer ใหม่ (Hard Filter → 6 Stage Tag → Scoring → Display → Claude Analyze)"
assert old in text, "Scope Boundary 4-layer line not found"
text = text.replace(old, new)

# Edit 9 — Scope Boundary line 836
old = "- Design + implement 7 Stage tag (Niwes ch2-ch7 + Stage 7 อำนาจตลาด NEW)"
new = "- Design + implement 6 Stage tag (Niwes ch2-ch7)"
assert old in text, "Scope Boundary 7-stage tag line not found"
text = text.replace(old, new)

PLAN.write_text(text, encoding="utf-8")
print(f"[OK] Updated {PLAN}")
print(f"[OK] Line count: {len(text.splitlines())}")
