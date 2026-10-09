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

## เก็บเพิ่ม 2026-10-09 (รอบเอกสาร — job-04 docs-index-tree)

- เหตุ: เอกสารบรรยายระบบที่ถอดไปแล้ว (คะแนน 0–100 / กฎขายชุดเก่า / backtest ที่ใช้เลขที่เราตั้งเอง) หรือถูกแทนที่ · ใช้ไม้บรรทัด `docs\niwes-principles.md` · กฎขายที่ใช้จริง = F3 ใน `roadmap\agreed-portfolio-framework.md`
- ย้ายด้วย `git mv` เข้า `docs\` (ในโฟลเดอร์นี้): `scoring-anchor-spec.md` (สเปกคะแนน · ที่มา "Niwes ch3–ch7" ไม่มีไฟล์ต้นทาง) · `dps-fix-verification-2026-04-27.md` `dps-set-fix-verification-2026-05-19.md` (บันทึกตรวจของสคริปต์ `_verify_dps_fix.py` ที่เก็บไปแล้ว) · `niwes\13-threshold-adjustments.md` `niwes\00-backtest-protocol.md` (เลข PE / PBV / streak เราตั้งเอง ไม่ใช่สูตร 5-5-5-5) · `niwes\14-monitoring-setup.md` `niwes\15-exit-rules.md` `niwes\16-exit-decision-template.md` (กฎขายชุดเก่า — ป้าย Verbatim ให้ประโยคของผู้รวบรวม)
- ย้ายเข้า `research\` (ในโฟลเดอร์นี้): `_full_AMATA_2026-05-24.md` `_full_AMATA_2026-05-21.md` `_deep_AMATA_2026-05-20.md` `_business_AMATA_2026-05-20.md` `amata_report.md` (แทนที่ด้วย `research\amata-deep-dive-2026-10-09.md` · จุดที่ผิด/เก่าดูท่อน 10 ของไฟล์นั้น) · `_portfolio_70-25-5_framework_2026-05-20.md` (ร่างเก่า รายชื่อหุ้นไม่ตรงพอร์ตจริง · ปัจจุบัน = `roadmap\agreed-portfolio-framework.md`) · `niwes-analysis-master.md` `niwes-criteria-coverage-map.md` (ตัดข้อยกเว้นปันผลโต / นับ PE PBV ว่าคลุมเกณฑ์ ขัดกับแหล่งจริง)
- บล็อกหมายเหตุ `⛔ 2026-10-09` ที่เคยติดหัวไฟล์เหล่านี้ถูกเอาออก (เหตุอยู่ในรายการข้างบนแล้ว · รายการ E1–E17 ที่ `docs\review-2026-10\niwes-vs-system.md`)
- เอากลับ: `git mv` ไฟล์กลับที่เดิม (`docs\` / `docs\niwes\` / `research\`) · ไฟล์เหล่านี้ไม่มีใครชี้แล้ว ณ วันเก็บ — กลับมาต้องแก้ path ที่อ้างในไฟล์ `docs\niwes-principles.md` ด้วย
- `scripts\flake_queue.py` (ย้าย 2026-10-09): คิวหุ้นที่ yahoo flake เขียน `data\flake_queue.json` — เหลือแต่ฝั่งเขียน ไม่มีใครอ่านคิว · เอากลับ: `git mv` กลับ `scripts\` แล้วเติม `from flake_queue import add_to_queue` + เรียก `add_to_queue(sym, filter_reasons, today)` ตอนสถานะ PENDING ใน `screen_stocks.py`

## เก็บเพิ่ม 2026-10-09 (รอบ deep dive 7 เล่ม — job-15 code-wrap-up)

- เหตุ: deep dive รอบนี้เขียนใหม่ทับ 7 ตัว (`research\bbl-deep-dive-2026-10-09.md` `tcap-` `tisco-` · `hong-lens\research\_deep_<TOA|SISB|SECURE|MOSHI>_2026-10-09.md`) · ท่อน 10 ของแต่ละเล่มบอกจุดผิด/เก่าของงานเดิมแล้ว · `hong-v5-rerun` คิดอันดับจากสูตร PEG ที่กลับด้าน (แก้ 2026-10-09) แทนด้วย `research\hong-v5-scan-2026-10-09.md` + `.csv` · `portfolio-snapshot-*` ตัวเลขพอร์ต / ยอดเติม / projection ถูกแทนด้วย `scripts\holdings_watch.py` + deep dive รอบนี้
- ย้ายเข้า `research\` (ในโฟลเดอร์นี้): `_full_BBL_2026-05-21.md` `_business_BBL_2026-05-20.md` `_deep_BBL_2026-05-20.md` `_full_TCAP_2026-05-21.md` `hong-v5-rerun.md` `hong-v5-rerun.csv` `portfolio-snapshot-2026-07-20.md` `portfolio-snapshot-2026-05-22.md` · `refs\setsmart-xls-2026-05-21\companyprofile_excel_bbl.xls` `factsheet_excel_bbl.xls` (มีแต่ `_full_BBL` ชี้ · xls ของ AMATA / HTC / PTTEP ยังอยู่ที่เดิม)
- ย้ายเข้า `hong-lens\research\` (ในโฟลเดอร์นี้): `_deep_TOA_2026-05-21.md` `_deep_SISB_2026-05-21.md` `_deep_SECURE_2026-05-21.md` `_deep_MOSHI_2026-05-21.md`
- path ที่อ้างในไฟล์ใต้ `research\` `hong-lens\research\` ถูกแก้ให้ชี้มาที่นี่แล้ว · `docs\review-2026-10\` ไม่แก้ (บันทึกมีวันที่)
- เอากลับ: `git mv` ไฟล์กลับที่เดิม แล้วแก้ path ที่อ้างในไฟล์ `research\*-2026-10-09.md` `hong-lens\research\_deep_*_2026-10-09.md` `hong-lens\research\_master_hong-lens_2026-05-21.md` กลับ
