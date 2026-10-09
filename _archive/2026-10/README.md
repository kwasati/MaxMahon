# _archive\2026-10 — เก็บเมื่อ 2026-10-07

- Art 2026-10-07: "ตัวหน้า web+server ที่เปิดรันไว้ก็ไม่ได้ใช้เลย อยากให้เอาไปเก็บทั้งหมด" · สคริปต์ใน `scripts\` ยังใช้ — เปลี่ยนมาคุยกับ Claude ผ่านแชทแทน
- ย้ายด้วย `git mv` มาจาก root ของ `C:\WORKSPACE\projects\4-MaxMahon`: `server\` `web\` `max-server.bat` `mockup\` `web-v6-mockup\` `DESIGN.md` (design ของหน้าเว็บ) · `docs\auth-setup.md` `docs\archive\` (→ `docs-archive\`) `docs\plans\` (→ `plans\`) `docs\ui-modernize-screenshots\` · `scripts\_archive\` (→ `scripts\_archive\`) · `scripts\_smoke_filter_status.py` (import `server.app`) · `tmp\` · `research\` ที่ไม่มีใครชี้ 10 รายการ (→ `research\`)
- `..\2026-04\portfolio-simulator-builder-2026-04-25\` ย้ายมาจาก `_archive\` โดยตรง (จัดตามโครง `_archive\<yyyy-mm>\`)
- เปิด server กลับ: ย้าย `server\` `web\` `max-server.bat` กลับ root ของ project · `scripts\_smoke_filter_status.py` กลับ `scripts\` · `max-server.bat` มี path เต็ม `C:\WORKSPACE\projects\4-MaxMahon` · server โหลด `C:/WORKSPACE/.env` · Task Scheduler `Max Mahon Weekly` ถูก disable ไว้

## เก็บเพิ่ม 2026-10-09

- เหตุ: คัดหุ้นเลิกใช้คะแนน 0–100 (commit ebb5390) · เลิก server หลายผู้ใช้ + ตัวตั้งเวลา · งานใช้ครั้งเดียวจบแล้ว — grep แล้วไม่มีไฟล์ที่ยังใช้อยู่ import
- ย้ายด้วย `git mv` เข้า `scripts\` (ในโฟลเดอร์นี้): `_verify_dps_fix.py` `_verify_dps_set_fix.py` `clean_reset.py` `migrate_portfolio_to_separate.py` `migrate_to_per_user.py` (ใช้ครั้งเดียว) · `_smoke_scoring_v2.py` `_smoke_dehardcode.py` `_smoke_yahoo_resilience.py` (smoke พัง/ของเลิกใช้/เขียน `data\`) · `anchor_scoring.py` `scan_anchor.py` `case_study_detector.py` `sector_taxonomy.py` (คะแนนเดิม) · `portfolio_builder.py` `portfolio_state.py` `test_portfolio_math.py` (จัดพอร์ตชุด server — `test_portfolio_math.py` มาจาก `tests\`) · `user_data_io.py` `daily_price_refresh.py` `telegram_alert.py` (หลายผู้ใช้ + ตัวตั้งเวลา)
- `reports\anchor_scan_2026-05-18.md` → `reports\` (ในโฟลเดอร์นี้)
- ลบของตายในไฟล์ที่ยังใช้: alias `fetch_yfinance_supplement` · `compute_payout_sustainability` · `check_hidden_value` ใน `scripts\data_adapter.py` · import `fetch_from_thaifin` ใน `scripts\fetch_data.py` · ท่อน `schedule` ใน `config.json`
- เอากลับ: `git mv` ไฟล์กลับ `scripts\` (`test_portfolio_math.py` กลับ `tests\` · `anchor_scan_2026-05-18.md` กลับ `reports\`) · ฟังก์ชัน/alias ที่ลบ ดูจาก `git log -p -- scripts\data_adapter.py` · `daily_price_refresh.py` ตัวเดียวที่อ่านคิวของ `flake_queue.py` — กลับมาแล้วคิวจะมีคนอ่านอีก
