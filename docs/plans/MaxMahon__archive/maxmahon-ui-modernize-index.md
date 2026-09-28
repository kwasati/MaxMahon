---
project: MaxMahon
created: 2026-04-23
last_updated: 2026-04-23
status: done
---

# UI Modernize — Desktop Mockup + Production Port

> Orchestrator plan สำหรับงานค้างจาก maxmahon-next-03-ui-port: plan เดิม port แค่ tokens (sage colors) แต่ยังคง vintage newspaper chrome (Playfair Display + masthead 'VOL.VI·NO.17' + section № numbering) ซึ่งไม่ตรงกับ mockup ที่ user approve. ต้อง: (01) สร้าง desktop mockup Robinhood sage (ปัจจุบันมีแค่ mobile mockup) + (02) port ทั้ง mobile+desktop mockups ไปยัง production — swap font เป็น Inter, ลบ newspaper masthead chrome, restyle shell + 6 pages + portfolio-builder ให้ตรง mockup. Build order บังคับ sequential

## Phase 1: Desktop Mockup Creation
- [x] /build maxmahon-ui-modernize-01-desktop-mockup — สร้าง mockup/portfolio-builder-robinhood-desktop.html ด้วย Robinhood sage tokens + layout เหมาะกับ desktop 1200+ px (multi-column, bigger cards)

## Phase 2: Production UI Port (depends 01)
- [x] /build maxmahon-ui-modernize-02-production-port — port ทั้ง desktop + mobile mockups ไป production: Inter font swap, retire newspaper masthead, rewrite mast/mobile nav, restyle 6 pages + portfolio-builder ให้ตรง mockup
