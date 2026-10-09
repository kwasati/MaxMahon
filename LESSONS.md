# LESSONS — กล่องจด 4-MaxMahon
กล่องจดรอย่อย · ต่อท้ายด้วย `ws.mjs pass` เท่านั้น · ห้ามอ่านเพื่อใช้งาน — ความรู้ที่ใช้ได้อยู่ใน knowledge · ย่อยเมื่อ Art สั่ง


## 2026-10-09 job-01-niwes-principles (desk maxmahon/krv3)
<!-- krv3/job-01-niwes-principles -->
- เกิดอะไร: `docs/scoring-anchor-spec.md` อ้าง "Niwes ch3–ch7" ทั้งใบ แต่ต้นทางเป็นไฟล์ tmp ใน reMarkable ที่ไม่มีในเครื่อง · ทำไม: plan เก่าชี้ path tmp แล้วไม่ย้ายเข้า repo/00-sources · หลักฐาน: `_archive/2026-10/plans/_archive/niwes-refactor-v2-design.md:5` + `ls` 2026-10-09 = No such file
- เกิดอะไร: `15-exit-rules.md` ติดป้าย "Verbatim quote" ให้ประโยค Lessons ของผู้รวบรวมเอง · ทำไม: ไฟล์ 13-16 เขียนทีหลังโดยไม่ผ่านกติกา 00-research-rules · หลักฐาน: `15-exit-rules.md:19-27` vs `09-case-or-exit.md:70-71`
- เกิดอะไร: prachachat ทุก URL ตอบ 403 ตั้งแต่ 2026-04-20 (00-sources #35) แต่ฐานเรายกคำจากมันเป็นหลัก #6 #7 · ทำไม: ตอนรวบรวมใช้ snippet แล้วติดป้ายเป็นคำยก · หลักฐาน: WebFetch 2026-10-09 = 403 ทั้ง 3 URL


## 2026-10-09 job-03-review-screen-score (desk maxmahon/krv3)
<!-- krv3/job-03-review-screen-score -->
- เกิดอะไร: ฝังโค้ด python ที่มี `\2026` ใน heredoc ของ Bash tool แล้ว backslash+ตัวเลขกลายเป็นอักขระแปลก (`_archive\2026-10` → `_archive` + 0x82 + `6-10`) · ทำไม: shell/tool ตีความ `\NNN` เป็น octal · หลักฐาน: `ascii()` เจอ `\x82` ในไฟล์ผล · แก้ด้วย `chr(0x82)`; ทางที่ดี: เขียนไฟล์ด้วย Write tool หรือใช้ `chr(92)` แทน backslash
- เกิดอะไร: heredoc ใหญ่ใน Bash tool ล้ม `unexpected EOF` 2 ครั้งโดยไม่มีไฟล์ถูกเขียน · หลักฐาน: ใช้ Write tool สร้างไฟล์ส่วนแล้ว `cat part >> main` ผ่านทันที


## 2026-10-09 job-05-amata-deep-dive (desk maxmahon/krv3)
<!-- krv3/job-05-amata-deep-dive -->
- เกิดอะไร: ประวัติปันผลยาวต้องเทียบ 3 แหล่ง — IR ของบริษัทพิมพ์ผิด (FY2021 final 0.03 แทน 0.30) · panphol ขาดงวด 2010–2011 (ให้ 0.23/0.04 จริง 0.30/0.40) · yahoo ปรับ ×0.9919 และก่อน 2003 ต่าง 5 เท่าจากเปลี่ยนพาร์
  ทำไม: แหล่งเดียวทำให้ปีวิกฤตอ่านผิด (2011 จะดูเหมือนตัด 87% ทั้งที่ไม่ตัด) · หลักฐาน: `amata-deep-dive.md` ข้อ 2.1 คอลัมน์ที่มา
- เกิดอะไร: `py -I` ตัด PYTHONUTF8 ทิ้ง → พิมพ์ไทย/ลูกศรล้ม (cp874) · ทำไม: -I = -E ไม่อ่าน env PYTHON* · หลักฐาน: รัน `calc_amata.py --proj` ล้มครั้งแรก แก้ด้วย `py -X utf8 -I`
- เกิดอะไร: heredoc ก้อน ~110 บรรทัดไทยหนาแน่นล้ม "unexpected EOF" ทั้งที่ <150 บรรทัด · ทำไม: เดา: ความยาวไบต์ (ไทย 3 ไบต์/ตัว) เกินลิมิตคำสั่ง · หลักฐาน: แบ่งเป็น 2 ก้อน ~50 บรรทัดผ่าน


## 2026-10-09 job-02-deep-dive-tcap (desk maxmahon/krv3)
<!-- krv3/job-02-deep-dive-tcap -->
- เกิดอะไร: ใบข้อเท็จจริงนับปันผลพิเศษ 4.00 (XD 27 ธ.ค. 2562) เป็นปันผลปี 2019 → A2 รายงาน "ลด 57% ปี 2020 ยังไม่กลับ" และยีลด์สิ้นปี 2019 = 13.1% ทั้งที่ปันผลปกติไม่เคยลด / ทำไม: set.or.th+yahoo ไม่มีป้ายปกติ-พิเศษ / หลักฐาน: panphol แยกงวด 1.20+4.00+1.80 · `files/tcap/dca_out.txt` ex-date
- เกิดอะไร: WebFetch อ่าน PDF snapshot ของบริษัท (thanachart.co.th) ไม่ออก แต่ไฟล์ถูกเซฟลง tool-results → อ่านด้วย pypdf ได้ครบ (โครงสร้าง % ถือ ผู้ถือหุ้น งบ 4 ปี) / ทำไม: WebFetch ส่ง binary ให้โมเดลสรุป / หลักฐาน: `files/tcap/snapshot_fy25.txt`
- เกิดอะไร: heredoc `cat >> file <<'EOF'` ผ่าน Bash tool ล้ม "unexpected EOF while looking for matching ''" กับก้อนข้อความไทยยาว ~120 บรรทัด → ใช้ Edit ต่อท้ายไฟล์โดย anchor บรรทัดสุดท้ายแทน ได้ทุกครั้ง / ทำไม: เดา: ตัว tool ส่งคำสั่งยาวผ่านชั้น shell ที่ตีความ quote / หลักฐาน: error ใน transcript tool call ที่ 29


## 2026-10-09 job-01-deep-dive-bbl (desk maxmahon/krv3)
<!-- krv3/job-01-deep-dive-bbl -->
- เกิดอะไร: bangkokbank.com ทุก URL (IR page / PDF presentation / MD&A / ashx) timeout 60 วินาที 7 ครั้งติด ขณะ search engine ยกตัวเลขจากไฟล์เดียวกันได้
  ทำไม: เว็บ BBL ช้ากับ fetcher ของเรา (น่าจะ WAF/ขนาด PDF) — ไม่ใช่ไฟล์ไม่มี
  หลักฐาน: WebFetch 4Q25/3Q25 presentation, mda2q_en2026, Financial-Information, Dividend-Payment, boardresolutions_th2026, ten-year ashx ทั้งหมด "timeout of 60000ms exceeded" · ตัวเลขเดียวกันได้จาก WebSearch snippet → ติดป้าย IRS ในผล
- เกิดอะไร: ตัวเลขปันผลที่เครื่องมือสรุปจากหน้า panphol ของ KBANK/SCB ผิดชัด (KBANK FY2020 "4.75" > FY2019 "3.00" ทั้งที่ 2563 ธปท. สั่งงดระหว่างกาล)
  ทำไม: หน้ายาวหลายสิบแถว เครื่องมือสรุปจับแถวผิดปี — ถามแบบ "เฉพาะแถว XD ปี X–Y" ช่วยได้กับ BBL แต่ไม่ช่วย KBANK/SCB
  หลักฐาน: fetch panphol KBANK/SCB 2 รอบ ได้คนละเลข · BBL ตรวจกับ yahoo XD รายงวดตรงทุกแถว 2547–2569 จึงเชื่อได้ · ตัวที่ตรวจข้ามแหล่งไม่ได้ไม่เอาลงผล
- เกิดอะไร: heredoc `cat >> file <<'EOF'` กับเนื้อหาไทยยาว ~70 บรรทัดล้ม "unexpected EOF while looking for matching `''"
  ทำไม: เดา: wrapper ของ Bash tool ตัด/แปลงข้อความยาวก่อนถึง shell — ไม่ใช่เนื้อหา (quoted heredoc ไม่ตีความ)
  หลักฐาน: เขียนท่อนเดียวกันด้วย Write เป็นไฟล์ part แล้ว `cat part >> main` สำเร็จ → ไฟล์ยาวให้เขียน part ≤150 บรรทัดด้วย Write แล้วต่อด้วย cat


## 2026-10-09 job-09-amata-dca-addendum (desk maxmahon/krv3)
<!-- krv3/job-09-amata-dca-addendum -->
- `scripts/fact_sheet.py` ไม่อ่านต้นทุนจาก `config.json` ท่อน holdings เอง — ต้องส่ง `--cost AMATA=26.40` ไม่งั้นตาราง A4 ใช้ราคาวันนี้แทน (ใบงานบอกว่า "ต้นทุนอ่านจาก config เอง")
  ทำไม: fact_sheet รับต้นทุนจาก argument เท่านั้น (holdings_watch เป็นตัวอ่าน config แล้วส่งต่อ) · หลักฐาน: รันครั้งแรกไม่มี --cost ใบพิมพ์ "ยังไม่ได้ส่งต้นทุน — ใช้ราคาวันนี้แทน" รันซ้ำพร้อม --cost ได้คอลัมน์ @26.40
- ราคาย้อนหลังจาก yfinance ใน `files/calc_amata.py` (เล่มแรก) เป็น adjclose ปรับปันผล — AMATA ปิดจริงสิ้นปี 2014 = 15.57 แต่ adjclose 10.59 (ต่าง 32%) ทำให้ PE/PBV/ยีลด์ย้อนหลังผิดทั้งชุดและสรุปทิศราคาผิด
  ทำไม: yfinance auto_adjust ค่าเริ่มต้น · ตรวจได้ด้วย yahooquery history(adj_ohlc=False) แล้วเทียบ close กับ adjclose ก่อนใช้ทุกครั้ง · หลักฐาน: `files/amata_yahoo_raw.json` yearend close vs adjclose ต่างทุกปีก่อน 2026
- ราคา "วันนี้" ของระบบ (cache --refresh = 31.75 ปิด 8 ต.ค.) กับ yahoo สดตอนรัน backtest (9 ต.ค. ปิด 31.50) เป็นคนละวัน — ใบ deep dive ต้องระบุวันปิดที่ใช้ ไม่ใช่วันรัน
  หลักฐาน: fact_sheet พิมพ์ "refresh AMATA: 31.75 @ 2026-10-08" · backtest พิมพ์ "last close 2026-10-09 = 31.5"


## 2026-10-09 job-08-deep-dive-tisco (desk maxmahon/krv3)
<!-- krv3/job-08-deep-dive-tisco -->
- เกิดอะไร: ฉาก A4 ของ fact_sheet ให้ TISCO โตกลาง 7.1%/ปี ทั้งที่ DPS นิ่ง 0% มา 4 ปี · ทำไม: ทุกหน้าต่าง CAGR มีฐานในช่วง payout 36–45% การโตที่วัดคือ payout ขยาย · หลักฐาน: FS A12 2015 45% → 2019 85% → 2025 93% + AR24 หน้า 38 (เล่ม ข้อ 4.1 / 9.1)
- เกิดอะไร: WebFetch อ่าน PDF ไม่ได้ (ตอบว่า binary) แต่บันทึกไฟล์ไว้ใน tool-results → แกะด้วย `py -X utf8 -I` + pypdf ได้ครบ (ttb report / annual report 241–355 หน้า) · ทำไม: ตัวสรุปของ WebFetch ไม่ parse PDF · หลักฐาน: 5 PDF ในงานนี้ · ใช้ `-X utf8` ไม่ใช่ `PYTHONUTF8` เพราะ `-I` ignore env
- เกิดอะไร: bash heredoc ยาว ~12 KB (ไทย) ล้ม "unexpected EOF while looking for matching quote" · ทำไม: เดา: ลิมิตความยาวคำสั่งของ bash tool บน Windows · หลักฐาน: heredoc 6 KB ผ่าน 12 KB ล้ม → เปลี่ยนเป็น Write + Edit (marker `<!-- ต่อ -->`) ทีละ ≤150 บรรทัดผ่าน
- เกิดอะไร: snippet ค้นเว็บบอก "นิเวศน์ถือ TISCO 14 ล้านหุ้น 1.34%" — ผิด เป็นเลข TCAP (14M/1,048M = 1.34%) · ทำไม: snippet ปนบริบทบทความ 5 เซียน · หลักฐาน: fetch บทความจริง BB 1173220 + SS/PP ไม่มีชื่อ · บทเรียน: ตัวเลขผู้ถือหุ้นต้องเทียบ % กับจำนวนหุ้นบริษัทก่อนเชื่อ


## 2026-10-09 job-11-hong-dive-toa (desk maxmahon/krv3)
<!-- krv3/job-11-hong-dive-toa -->
- เกิดอะไร: PEG/CAGR 3 ปีของ TOA (27%) ผ่านเกณฑ์เซียนฮงเพราะปีฐาน 2022 เป็นปี GM ถูกบีบ — รายได้ 3 ปีโตแค่ 4.6% รวม
- ทำไม: เกณฑ์ "โต 26%/ปี 3 ปี" ไม่แยกโตจากยอดขายกับโตจากอัตรากำไรฟื้น · ควรดู CAGR รายได้คู่กับ CAGR กำไร และ CAGR 5-6 ปีด้วย
- หลักฐาน: cache yearly_metrics 2019→2025 กำไร CAGR 5.1% · 2022→2025 27.2% · ท่อน 4 ของไฟล์ผล
- เกิดอะไร: deep dive รอบ พ.ค. ให้ "ไม่มี SEC enforcement" ทั้งที่ผู้ถือหุ้นใหญ่ลำดับ 5 และ 7 ติดคดี STARK/DPAINT ตั้งแต่ปี 2567
- ทำไม: รอบก่อนค้นแค่ข่าว SET ของบริษัท ไม่ได้ค้นชื่อผู้ถือหุ้นรายคน
- หลักฐาน: bangkokbiznews 1112804 (ฟ้อง 12 ก.พ. 2567) · prachachat 1703313 (ก.ล.ต. 26 พ.ย. 2567)
- เกิดอะไร: kaohoon / Bangkok Post ตอบ 403/402 กับ WebFetch · set.or.th/settrade โหลดด้วย JS อ่านตัวเลขไม่ได้
- ทำไม: กัน bot · ใช้ hoonsmart / posttoday / siamrath / brandbuffet / IR ของบริษัท (investor.toagroup.com) แทนได้ทุกครั้ง
- หลักฐาน: ผลเรียก WebFetch ในงานนี้


## 2026-10-09 job-12-hong-dive-sisb (desk maxmahon/krv3)
<!-- krv3/job-12-hong-dive-sisb -->
- เกิดอะไร: deep dive รอบ พ.ค. 2026 สร้าง thesis "โรงเรียนเต็ม ต้องรอวิทยาเขตใหม่" จาก estimate ที่ไม่ได้ตรวจ — ของจริงใช้ที่นั่งแค่ 62% และระยองเปิดมาตั้งแต่ 2023
  ทำไม: ใช้ "public knowledge" แทนเอกสารบริษัท (presentation รายไตรมาสบน sisb.ac.th มีตารางนักเรียน/ความจุ/วิทยาเขตครบ) · หลักฐาน: `files\sisb\sisb_2q2026_update.txt` หน้า 14, 17, 19 เทียบ `_deep_SISB_2026-05-21.md:122-137, 468-482`
  บทเรียน: deep dive หุ้นที่มี investor presentation ต้องดึง PDF บริษัทก่อน (pypdf อ่านได้) ค่อยเติมจากข่าว
- เกิดอะไร: WebFetch สรุป PDF/บทวิเคราะห์ไม่ได้ (บอก "corrupted") ทั้งที่ไฟล์ปกติ · บางเว็บ (kaohoon) 403
  ทำไม: WebFetch ย่อยไบนารีไม่ได้ แต่เซฟไฟล์ไว้ให้ใน tool-results → เปิดด้วย `py -I` + pypdf ได้ครบ (Krungsri 7 หน้า · presentation 36 หน้า)
  หลักฐาน: `files\sisb\sisb_2q2026_update.txt` 2,308 บรรทัดจาก PDF ที่ WebFetch บอกอ่านไม่ได้
- เกิดอะไร: heredoc `cat <<'EOF'` ใน Bash tool ล้ม "unexpected EOF" ตอนเขียนไฟล์ ~100 บรรทัดที่มีตาราง/อักขระไทย
  ทำไม: เดา: tool ตัดคำสั่งยาว · แก้โดยใช้ Write (ไฟล์ใหม่) + Edit ต่อท้ายทีละ ≤150 บรรทัด ได้ปกติ


## 2026-10-09 job-13-hong-dive-secure (desk maxmahon/krv3)
<!-- krv3/job-13-hong-dive-secure -->
- เกิดอะไร: ข้อมูลรายไตรมาสล่าสุดของหุ้นไทยดึงได้จาก yfinance `quarterly_income_stmt / balance_sheet / cashflow` ตรงกับ MD&A ของบริษัททุกตัวที่เทียบ (Q2/26 รายได้ 195.16 กำไร 12.98) · ทำไม: SET/settrade/aio/kaohoon ปิด (403/500/JS) แต่ yahoo มีงบ SET ครบ · หลักฐาน: `files\secure
force_secure_MDA_2026Q2_EN.pdf.txt` เทียบ output yfinance ในงานนี้
- เกิดอะไร: IR site ของบริษัท mai (`www.nforcesecure.com/investor-relations`) มี link PDF ตรง (MD&A / งบ / One Report บน image.makewebeasy.net) ดาวน์โหลดด้วย curl ได้ แล้วใช้ pypdf ดึงข้อความ — One Report 264 หน้าดึงได้ใน 1 คำสั่ง · ทำไม: WebFetch อ่าน PDF ไม่ได้ (เห็นแต่โครง) ต้อง curl + pypdf · หลักฐาน: `files\secure\onereport2025.txt` 1.39 MB
- เกิดอะไร: ด่าน "กำไร new high" และ PEG ของ scanner มองไม่เห็นการพังของไตรมาสล่าสุด (SECURE ผ่าน 6 ด่านทั้งที่ TTM ต่ำกว่าปีก่อน) · ทำไม: cache มีแต่ `yearly_metrics` ไม่มีไตรมาส · หลักฐาน: csv แถว 596 vs ท่อน 3 ของไฟล์ผล


## 2026-10-09 job-14-hong-dive-moshi (desk maxmahon/krv3)
<!-- krv3/job-14-hong-dive-moshi -->
- เกิดอะไร: ใบข้อเท็จจริง MOSHI รายงานหนี้สินรวม 2025 = 2,656 ล้าน → อัตรา 0.97 → ธง T6 "เพิ่ม 3 ปีติด" ติด ทั้งที่ของจริง 2,320.9 (0.85 ลดจาก 0.88)
  ทำไม: `total_debt` ปี 2025 ใน cache (thaifin) ผิดตัวเดียว ปี 2022–2024 ตรง yahoo/SET ทุกปี — ธงที่คิดจากคอลัมน์เดียวของ cache เชื่อไม่ได้ถ้าไม่เทียบปีล่าสุดกับแหล่งที่สอง
  หลักฐาน: yahoo `TotalLiabilitiesNetMinorityInterest` 2025-12-31 = 2,320,856,267 · SET factsheet (deep dive รอบก่อนบรรทัด 272) 2,320.86 · ใบ `files\moshi\MOSHI_2026-10-09.md` บรรทัด 137
- เกิดอะไร: Bash heredoc ยาว (>~50 บรรทัดภาษาไทย) ล้ม "unexpected EOF while looking for matching `''" 2 ครั้ง ทั้งที่ heredoc สั้นผ่าน
  ทำไม: เดา: คำสั่งถูกตัดกลางเมื่อยาวเกินขนาดหนึ่ง (ตัวอักษรไทย 3 ไบต์) → ตัวปิด heredoc หาย — ไม่เกี่ยวกับเครื่องหมายคำพูดในเนื้อ
  หลักฐาน: ล้มที่ "line 110" และ "line 55" ซึ่งคือท้ายคำสั่ง · เขียนไฟล์ด้วย Write แล้วต่อท้ายด้วย Edit (anchor บรรทัดสุดท้าย) ผ่านทุกครั้ง
- เกิดอะไร: yahooquery `balance_sheet()` / `cash_flow()` ไม่รับ `trailing=` (มีเฉพาะ `income_statement()`)
  ทำไม: API ต่างกันระหว่าง 3 เมธอด — ก๊อปจาก income_statement มาใช้แล้วพัง
  หลักฐาน: TypeError ใน `moshi_dca.py` รันครั้งแรก · ลบ kwarg แล้วผ่าน


## 2026-10-09 job-15-code-wrap-up (desk maxmahon/krv3)
<!-- krv3/job-15-code-wrap-up -->
- สคริปต์ python ที่มี backslash (regex / path Windows) ห้ามสร้างด้วย heredoc ผ่าน Bash tool: เกิด `\\` ถูกลดเหลือ `\` แล้ว regex พัง (`bad escape \p`) — หลักฐาน: fix_refs.py รอบแรก · ใช้ Write tool หรือสร้าง `\` ด้วย `chr(92)`
- `py -I` ไม่อ่าน env `PYTHONUTF8` — print ภาษาไทยตก cp874 (`UnicodeEncodeError`) · ใช้ `py -X utf8 -I`
