"""Drop Stage 7 — phase 2: clean up leftover references in code map + impl plan + section 10."""

from pathlib import Path

PLAN = Path(r"C:\WORKSPACE\.claude\plans\4-MaxMahon\niwes-refactor-v2-design.md")
text = PLAN.read_text(encoding="utf-8")

# Edit 1 — Line 960 (code map row 5: "Stage 5-7 พอเสร็จ design" → "Stage 5-6 ครบแล้ว")
old = "| 5 | `scripts/screen_stocks.py::assign_signals` (lines 565-632) | replace existing tags ด้วย Stage 1-4 tags (Stage 5-7 พอเสร็จ design) |"
new = "| 5 | `scripts/screen_stocks.py::assign_signals` (lines 565-632) | replace existing tags ด้วย Stage 1-6 tags (design ครบแล้ว) |"
assert old in text, "Code map row 5 not found"
text = text.replace(old, new)

# Edit 2 — Line 962 code map row 7 (Stage 7 mention) — drop Stage 7 reference, keep file row
old = "| 7 | `scripts/case_study_detector.py` + `data/case_study_patterns.json` | align กับ Stage 7 (อำนาจตลาด) tags |"
new = "| 7 | `scripts/case_study_detector.py` + `data/case_study_patterns.json` | align กับ Stage 4/5 tag definitions |"
assert old in text, "Code map row 7 not found"
text = text.replace(old, new)

# Edit 3 — Line 1125 Day 8 Stage 7 row → drop
old = "| Day 8 | Stage 7 (อำนาจตลาด) | A2 + manual curation list |\n"
new = ""
assert old in text, "Day 8 row not found"
text = text.replace(old, new)

# Edit 4 — Line 1127 "Stage 5-7 ยังไม่ design"
old = "Stage 5-7 ยังไม่ design — block until approve\n"
new = ""
assert old in text, "Stage 5-7 block line not found"
text = text.replace(old, new)

# Edit 5 — Line 1131 "ตาม 7 stage"
old = "2. **C2:** Claude prompt redesign (Stage 2.9) — รับ input ตาม 7 stage"
new = "2. **C2:** Claude prompt redesign (Stage 2.9) — รับ input ตาม 6 stage"
assert old in text, "C2 line not found"
text = text.replace(old, new)

# Edit 6 — Line 1142 critical path
old = "A1 -> A4 -> Stage 1/3 (parallel) -> Stage 2/4 (parallel) -> Stage 5/6 (parallel) -> Stage 7 -> C1 (Scoring) -> C2 (Claude) -> C3/C4 (Glossary + UI) -> D"
# Source uses Thai arrow, try both
old_arrow = "A1 → A4 → Stage 1/3 (parallel) → Stage 2/4 (parallel) → Stage 5/6 (parallel) → Stage 7 → C1 (Scoring) → C2 (Claude) → C3/C4 (Glossary + UI) → D"
new_arrow = "A1 → A4 → Stage 1/3 (parallel) → Stage 2/4 (parallel) → Stage 5/6 (parallel) → C1 (Scoring) → C2 (Claude) → C3/C4 (Glossary + UI) → D"
assert old_arrow in text, "Critical path not found"
text = text.replace(old_arrow, new_arrow)

# Edit 7 — Replace entire Section 10 (Resume Checkpoint — ต่อ Stage 7)
start_marker = "## 10. Resume Checkpoint — ต่อ Stage 7"
# Find end — section 10 runs to end of file based on grep result
start_idx = text.find(start_marker)
assert start_idx >= 0, "Section 10 marker not found"

new_section_10 = """## 10. Resume Checkpoint — ต่อ Section 2.8+

**Status (2026-05-15):** Stage 1-6 design ครบ + Stage 7 ตัดทิ้ง (decision logged section 2.7d)

**Stage ที่เสร็จแล้ว (6/6):**
- Stage 1 — ราคาถูกพอ (2026-05-14)
- Stage 2 — ปันผลต่อเนื่อง (2026-05-14)
- Stage 3 — Cash flow จริง (2026-05-14)
- Stage 4 — Moat (2026-05-14)
- Stage 5 — ถือยาวได้ (2026-05-14)
- Stage 6 — Hidden value (2026-05-14)

**ที่ค้าง (6 ก้อน — Stage 7 ตัดออก จาก 7 เดิม):**
1. **Section 2.8** — Scoring redesign (multi-axis vs tag-based)
2. **Section 2.9** — Claude Opus prompt redesign (input 6 stage tags → output Niwes mental model)
3. **Section 2.10** — Dictionary (`data/niwes_glossary.json` + UI hover + page route)
4. **Stage 6 initial seed** — Claude propose ~20-30 entries `hidden_value_holdings.json` → อาร์ท approve → commit
5. **Phase A pre-implementation tasks (A1-A4):**
   - A1: `data_adapter.py` unit normalization (D/E percent vs ratio)
   - A2: verify OCF/NP definition (อาจ switch เป็น OCF/EBITDA)
   - A3: `sector_pe_precompute.py` + `data/sector_pe_median.json` (weekly refresh)
   - A4: extend `_build_aggregates` ทุก Stage 1-5 fields
6. **Archive obsolete plans** — `filter-04/05/06/08` + regen `filter-index.md`

**Test data source:** SETSMART (Layer 0) verified 5 หุ้น (PTT/SCC/CPALL/ADVANC/BDMS)

**Manual list governance (Stage 6):** Claude curate เท่านั้น — initial seed Phase B Day 7 + refresh ทุก 3-6 เดือน
"""

# Section 10 is the last section in the file
text = text[:start_idx] + new_section_10

PLAN.write_text(text, encoding="utf-8")
print(f"[OK] Updated {PLAN}")
print(f"[OK] Line count: {len(text.splitlines())}")
