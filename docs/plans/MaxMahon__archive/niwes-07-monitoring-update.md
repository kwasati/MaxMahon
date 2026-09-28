---
project: MaxMahon
created: 2026-04-20
last_updated: 2026-04-20
status: done
---

# Monitoring + Update Loop — News Scrape + Diff Alert

> Part 7 of 8 — Index: niwes-master-index | Depends on: niwes-02-research-report, niwes-04-framework-migration | Parallel-safe with: niwes-08 — automated monitor ดร.นิเวศน์ portfolio + thesis changes — ป้องกัน framework outdated เร็ว (ดร.นิเวศน์ release พอร์ตทุก 6 เดือน + เปลี่ยน thesis บ่อย)

## Phase 1: News Scraper (ดร.นิเวศน์ shareholder + interview)
- [x] สร้าง `projects/MaxMahon/scripts/monitor_niwes_news.py` — scrape latest news ที่กล่าวถึง 'นิเวศน์ เหมวชิรวรากร' จาก: (1) kaohoon.com search RSS/HTML, (2) prachachat.net search, (3) thestandard.co search, (4) longtunman.com tag, (5) finnomena.com author search. Output: list of {url, title, date, snippet, source}. ใช้ requests + BeautifulSoup. ห้าม scrape ถี่เกิน rate limit (delay 2s ระหว่าง request). Save ผลลัพธ์ที่ `projects/MaxMahon/data/niwes_news_{date}.json`. — Scope: ห้าม scrape full article body (เกิน fair use) — แค่ title + snippet + URL. — Acceptance: รันได้ output JSON file มี ≥10 news items ใน 1 รอบ run
- [x] สร้าง dedup cache ที่ `projects/MaxMahon/data/niwes_news_seen.json` — track URL ที่เคยเห็น (set). Script update cache ทุก run + skip URL ที่อยู่แล้ว. — Acceptance: รัน 2 รอบติดกัน — รอบที่ 2 มี new items 0 (หรือน้อยกว่ารอบแรก)

## Phase 2: Portfolio Diff Detector
- [x] สร้าง `projects/MaxMahon/scripts/diff_niwes_portfolio.py` — เปรียบเทียบ news ใหม่กับ snapshot ใน `projects/MaxMahon/docs/niwes/11-current-portfolio.md`: ใช้ Anthropic SDK (claude-haiku-4-5 fast + cheap) วิเคราะห์ news titles + snippets — return list of {detected_change_type: 'add_position'|'reduce'|'exit'|'thesis_change'|'view_change', symbol: 'X', evidence: 'news URL', confidence: 0-100}. ถ้า confidence > 70 = trigger alert (Phase 3). — Scope: ห้าม update 11-current-portfolio.md อัตโนมัติ — แค่ detect + alert. Karl manual review + update ถ้าจริง. — Acceptance: รัน detect mock news → output structured findings + confidence
- [x] สร้าง `projects/MaxMahon/data/niwes_diff_history.json` — เก็บประวัติ detection (date, findings) สำหรับ trend analysis. — Acceptance: หลัง run มี entry ใหม่

## Phase 3: Telegram Alert (ใช้ Karl Notify bot ที่มี)
- [x] สร้าง `projects/MaxMahon/scripts/alert_niwes.py` — รับ findings จาก diff_niwes_portfolio.py + ส่ง Telegram via Karl Notify bot (token จาก `.env` — ใช้ pattern เดียวกับ scripts/notify อื่น). Format message: '🔔 ดร.นิเวศน์ update — {change_type} {symbol} (confidence {N}%) — source: {URL}'. ส่งเฉพาะ findings confidence > 70. — Scope: ห้ามส่ง spam — รวม findings ใน 1 message ถ้ามีหลายอัน + ห้ามส่งซ้ำ findings เดิม. — Acceptance: รัน mock findings 1 รอบ → Telegram message ส่งสำเร็จ + format ถูก

### Reference
```python
# pattern จาก scripts/notify อื่นใน workspace
import os, requests
from dotenv import load_dotenv
load_dotenv('C:/WORKSPACE/.env')
TOKEN = os.getenv('KARL_NOTIFY_BOT_TOKEN')
CHAT_ID = os.getenv('KARL_NOTIFY_CHAT_ID')

def send(msg):
    requests.post(
        f'https://api.telegram.org/bot{TOKEN}/sendMessage',
        json={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'}
    )
```

## Phase 4: Cron Schedule (Windows Task Scheduler)
- [x] สร้าง `projects/MaxMahon/scripts/run_monitor_pipeline.bat` — เรียก scripts ทั้ง 3 ตามลำดับ: monitor_niwes_news → diff_niwes_portfolio → alert_niwes. Log output ที่ `projects/MaxMahon/data/monitor_log_{date}.log`. — Acceptance: bat รันได้ end-to-end ไม่ error
- [x] Document cron setup ที่ `projects/MaxMahon/docs/niwes/14-monitoring-setup.md` — instruction ให้ Karl ใช้ Windows Task Scheduler: `schtasks /create /tn 'NiwesMonitor' /tr 'C:/WORKSPACE/projects/MaxMahon/scripts/run_monitor_pipeline.bat' /sc weekly /d MON /st 09:00`. รวม troubleshooting (ถ้า task fail check log file). — Scope: ห้ามรัน schtasks command ใน build (Karl ตัดสินใจเอง) — แค่ document. — Acceptance: doc มี setup command + troubleshooting + Karl เปิดอ่านแล้วรู้วิธี enable
