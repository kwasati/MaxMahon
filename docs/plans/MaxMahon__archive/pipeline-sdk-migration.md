---
project: MaxMahon
created: 2026-04-19
last_updated: 2026-04-23
status: done
---

# Pipeline SDK Migration — ย้าย weekly/discovery จาก Claude CLI ไป Anthropic SDK

> weekly pipeline ใช้ CLI subprocess timeout 300 วิ ไม่พอสำหรับ multi-year data ทั้ง watchlist. app.py ใช้ SDK + Opus 4.7 อยู่แล้วสำหรับ on-demand analysis ย้าย analyze.py + discover.py มาใช้ pattern เดียวกันให้ consistent.

## Phase 1: Migrate analyze.py
- [x] ลบ subprocess + shutil + find_claude_cli() ออกจาก analyze.py
- [x] เพิ่ม import anthropic + load_dotenv จาก C:/WORKSPACE/.env
- [x] สร้าง Anthropic client จาก MAX_ANTHROPIC_API_KEY (pattern เดียวกับ app.py)
- [x] แยก prompt เป็น system (framework+rules ที่ไม่เปลี่ยน) + user (stock data ที่เปลี่ยนทุกรอบ) — เพื่อ prompt caching
- [x] เรียก client.messages.create(model=claude-opus-4-7, system=[{type:text, text:..., cache_control:{type:ephemeral}}], messages=[{role:user, content:stock_data}], max_tokens=16000)
- [x] ไม่ใส่ timeout param ให้ SDK handle เอง (default 600s ก็พอ หรือเซ็ต timeout=900.0)
- [x] handle error: ถ้า api_key ไม่มี หรือ response error ให้ print + sys.exit(1) แบบเดิม
- [x] เก็บ output format เหมือนเดิม: header + response.content[0].text → save report_path

### Reference
```python
# pattern จาก server/app.py:1508-1518
response = _anthropic_client.messages.create(
    model="claude-opus-4-7",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt}],
    timeout=60.0,
)
raw_text = response.content[0].text.strip()
```

## Phase 2: Migrate discover.py
- [x] ลบ subprocess + shutil + find_claude_cli() inline function ออกจาก discover.py
- [x] ย้าย prompt + SDK call มา pattern เดียวกับ analyze.py
- [x] แยก system prompt (Hard Filters + Quality Score + Signal Tags definitions — static) และ user prompt (watchlist + candidates — dynamic)
- [x] ใช้ claude-opus-4-7 + prompt caching + max_tokens=16000
- [x] output format เหมือนเดิม: header + response → save report_path

## Phase 3: Test + document
- [x] รัน py scripts/analyze.py ทดสอบว่าทำงานได้จริง — ตรวจ reports/weekly_2026-04-19.md ว่าสร้างสำเร็จ + มีเนื้อหา + ไม่มี error
- [x] รัน py scripts/discover.py ทดสอบว่าทำงานได้ (ถ้ามี screener data ล่าสุด) — ถ้าไม่มี screener ก็ skip
- [x] update CHANGELOG.md version bump เป็น v3.3.1 — อธิบายการ migrate SDK + model change
- [x] อัพเดต CLAUDE.md (projects/MaxMahon/CLAUDE.md): เปลี่ยน 'Stack: Python + thaifin + yfinance + Claude CLI' เป็น 'Anthropic SDK (claude-opus-4-7)'
- [x] commit + push submodule: 'refactor(pipeline): migrate analyze+discover to Anthropic SDK + Opus 4.7'
- [x] update parent submodule pointer ที่ C:/WORKSPACE + commit
