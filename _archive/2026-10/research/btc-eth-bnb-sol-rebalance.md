---
date: 2026-05-03
mode: full
project: MaxMahon
topic: Crypto rebalance strategy backtest BTC/ETH/BNB/USDT/SOL 5 ปี
status: research
---

# Research: Crypto Rebalance Strategy 5 ตัว — ใช้ได้จริงไหมสำหรับเงิน $10,000

> Date: 2026-05-03 | Mode: full (4 agents parallel + web research)
> Project: MaxMahon (เสาหลัก #1 — ลงทุนมูลค่าเน้นปันผล→100M)
> Asset universe: BTC / ETH / BNB / USDT / SOL
> Time frame: ม.ค. 2021 - พ.ค. 2026
> Budget context: $10,000 retail Thai investor

---

## 1. Summary (อ่านแค่นี้ก็เข้าใจ)

- **Rebalance บน crypto = ใช้ได้จริง แต่ไม่เวิร์คเหมือนที่ practitioner blog โฆษณา** — งานวิจัย academic ค้านหลายเปเปอร์ว่ามันไม่ได้ "สร้าง alpha" จริงๆ มันคือ "เครื่องคุมความเสี่ยง" มากกว่า
- **BTC/ETH correlation = 0.85** → rebalance ระหว่าง 2 ตัวนี้แทบไม่ช่วย เพราะมันวิ่งทิศเดียวกันเกือบหมด — **USDT คือตัวที่ทำให้ rebalance work จริงๆ** (correlation ≈ 0 → ทำหน้าที่ "เงินสดสำรอง" ซื้อตอน crash)
- **คำตอบเฉพาะ portfolio นี้:** ไม่มี backtest paper ไหนทดสอบ exact 5 ตัวนี้ + ช่วงนี้ + งบ $10k มาก่อน — ต้อง run เอง แต่ pattern จาก research ใกล้เคียง บอกชัด:
  - **2021 (alt season):** SOL ขึ้น +11,180% / BNB +1,270% — rebalance equal-weight = ตัด winner = แพ้ hold ล้วนแน่ๆ
  - **2022 (crypto winter):** BTC -65% / ETH -67% / SOL -94% — USDT 20% ทำให้ portfolio เจ็บน้อยลงมาก
  - **2024-2025 (BTC dominance):** BTC +122% / ETH -3% / SOL -43% — rebalance ตัด BTC = แพ้ hold BTC
- **กับดักใหญ่สุด: Tail risk แบบ LUNA** — rebalance ที่บังคับ "ซื้อตัวที่ลง" ตอน asset กำลังจะตายถาวร = พินาศ. กฎเหล็ก: **cap แต่ละ asset ไม่เกิน 25% + kill switch หยุด rebalance ตอน asset ลงเกิน 70% ใน 7 วัน**
- **ค่าใช้จ่ายจริงสำหรับ Thai retail $10k:** ใช้ Bitkub หรือ Binance TH (SEC licensed) → กำไรยกเว้นภาษีถึง 2029 + fee 0.10-0.25% ต่อ trade. ห้ามใช้ Binance global (เสียสิทธิ์ tax exemption) ห้ามจ่าย subscription tool $15-19/เดือน (cost > trading fee ทั้งปี)
- **คำแนะนำสุดท้าย:** **Quarterly rebalance + threshold 20-25% drift trigger + cap 25%/asset + USDT 15-20%** — ไม่ใช่ "เครื่องปั๊มกำไร" แต่เป็น "ระบบลด volatility + บังคับซื้อตอน fear" ผลลัพธ์คาดหวัง: Sharpe ดีกว่า hold ตัวเดียว แต่ **return อาจแพ้ hold BTC ล้วน** ในช่วง BTC dominance

---

## 2. Findings

### 2.1 ทฤษฎี — rebalance ทำงานยังไง สูตรไหน work / ไม่ work

**สูตรหลักที่ทุกอย่างวิ่งจาก: Bernstein Rebalancing Bonus (1996)**

> RB₁₂ = X₁X₂ × σ₁σ₂(1 − ρ) + (σ₁ − σ₂)²/2

แปลเป็นภาษาคน: rebalance bonus ขึ้นกับ 3 ปัจจัย
- **ความผันผวนของแต่ละตัว** (σ) — ยิ่งเหวี่ยงเยอะยิ่งดี → crypto ผ่านเงื่อนไขนี้แน่นอน (BTC vol 50-80%/ปี)
- **correlation ระหว่าง 2 ตัว** (ρ) — ยิ่งต่ำ ยิ่งดี ถ้า ρ = 1 (วิ่งเหมือนกันเป๊ะ) bonus = 0
- **ขนาด weight ใกล้เคียงกัน** — equal-weight ได้ bonus สูงสุด

**ปัญหาใหญ่ของ portfolio นี้:** BTC-ETH correlation ≈ 0.85 (CME Group 2023) → (1-0.85) = 0.15 → bonus เหลือแค่ **15%** ของที่ควรจะได้ ถ้า correlation ต่ำกว่านี้

→ **ตัวที่ทำให้สูตรนี้ work จริงๆ คือ USDT** (correlation กับ crypto ≈ 0) ไม่ใช่ BTC/ETH/BNB/SOL ที่วิ่งคล้ายกันเอง

**Shannon's Demon — ทำไม rebalance สร้างกำไรได้จากของที่ไม่กำไร**
- ของ 2 อย่าง: ตัวหนึ่งเด้งขึ้นลง 50/50 (return 0% รวม) + เงินสด
- ถ้า hold เฉยๆ = 0%
- ถ้า rebalance 50/50 ทุกครั้งที่เด้ง = ได้กำไรจริง! เพราะบังคับขายตอนแพง ซื้อตอนถูก
- เครื่องนี้ work ดีที่สุดเมื่อของ "เด้งไปเด้งมา" ไม่ใช่ "วิ่งทิศเดียวยาวๆ"

**งานวิจัยที่ค้านว่า rebalance ไม่ได้สร้าง alpha จริง — Cuthbertson et al. (2016)**
- Paper สำคัญสุดที่ค้านความเชื่อ "rebalance = สร้างเงิน"
- บอกชัด: "premium" ที่ practitioner blog พูดถึง = จริงๆ คือ "diversification return" ที่ buy-and-hold portfolio ก็ได้เหมือนกัน
- เฉพาะ "rebalance return" จริงๆ ในระยะเวลาที่นักลงทุนถือจริง (10-30 ปี) = เล็กมากหรือติดลบ

**Kitces สรุปสั้นที่สุด:**
> "Rebalancing is not a return-enhancing strategy. It is a return-reducing strategy done for risk management purposes."

แปลภาษาคน: **rebalance ลด return แต่คุมความเสี่ยง** — ถ้าอยากได้เงินมากสุด → hold ตัวที่จะชนะแล้วถือยาว / ถ้าอยากได้นอนหลับสบาย → rebalance

### 2.2 Performance — ตัวเลขจริงปี 2021-2026

**ผลตอบแทนแต่ละตัว (Jan 1 → Dec 31)**

| ปี | BTC | ETH | SOL | BNB | USDT | บริบท |
|---|---|---|---|---|---|---|
| 2021 | +58% | +395% | **+11,180%** | +1,270% | ~0% | Alt season — SOL/BNB ระเบิด |
| 2022 | -65% | -67% | -94% | -52% | -2.3% (depeg ชั่วคราว) | Crypto winter + LUNA + FTX |
| 2023 | +156% | +91% | +918% | +28% | ~0% | Recovery |
| 2024 | +122% | +46% | +681% | +20% | ~0% | Halving year |
| 2025 | -3% | -3% | -43% | +40% | ~0% | BTC dominance 72.4% — alt อ่อน |

(Source: Bitcoin Magazine Pro, CoinGecko Annual Report 2024-2025, CryptoRank)

**Rebalance vs Hold — ตัวเลขจาก research จริง (ไม่ใช่ portfolio นี้เป๊ะๆ แต่ใกล้เคียง)**

**Hanicova-Vojtko paper (SSRN 3982120) — 27 cryptos equal-weight, ธ.ค. 2018 - ต.ค. 2021 (bull-only):**
| Strategy | Return/ปี | Volatility | Sharpe | Max ลงต่ำสุด |
|---|---|---|---|---|
| Buy & Hold (market cap) | ~95% | ~75% | 1.26 | -83% |
| Daily Rebalance (equal weight) | **~125%** | ~65% | **1.92** | -65% |
| Monthly Rebalance | ~120% | ~68% | 1.77 | -70% |

→ ในตลาดขาขึ้น rebalance ชนะ **ทั้ง return + Sharpe + drawdown**

**Crypto Research Report — mixed portfolio (หุ้น+bond+BTC 2.5%) ม.ค. 2014 - พ.ย. 2023:**
| Frequency | 3-year Rolling Return |
|---|---|
| **No rebalance** | **178%** |
| Annual | 143% |
| Quarterly | 111% |
| Monthly | 97% |

→ ใน mixed portfolio ที่ BTC วิ่งทิศเดียวยาวๆ **hold เฉยๆ ชนะ** เพราะ rebalance ตัด winner ออกตลอด

**ความขัดแย้ง 2 paper นี้คือหัวใจของเรื่องทั้งหมด:**
- Pure crypto + asset เด้งไปเด้งมา → rebalance ชนะ
- BTC dominate + วิ่งทิศเดียวยาว → hold ชนะ

**Portfolio 5 ตัวนี้ (BTC/ETH/BNB/USDT/SOL):** ไม่มี paper ทดสอบ exact ตัวนี้ + ช่วงนี้ → ต้อง run backtest เอง

### 2.3 Sweet Spot — ความถี่ + threshold ที่ดีที่สุด

**สำหรับ traditional asset (Vanguard 2015 / Daryanani 2008):**
- Annual + threshold 5% absolute = consensus
- Threshold-based ชนะ calendar-based เมื่อหัก fee
- Vanguard 2022 (institutional): trigger ที่ 2% deviation, rebalance to 1.75% destination

**สำหรับ crypto (งานวิจัยใหม่ที่สุด):**
- **Sornmayura 2024 (academic):** Annual + threshold 25-30% relative = best Sharpe สำหรับ crypto
- **Shrimpy 20,000 backtests:** threshold 15% = sweet spot, ชนะ HODL +77.1% (แต่ Shrimpy = commercial → bias)
- **MDPI 2024:** ช่วง high-vol → bands 20% + interval 1-10 day = best
- **CEUR-WS 2023:** crypto 8-10 ตัว → frequency สั้นดีกว่า / 2 ตัว → ไม่ต่าง

**ความขัดแย้ง:** academic บอก "annual + wide threshold" / commercial บอก "weekly + tight threshold" — ตอบไม่ได้ว่าใครถูก เพราะขึ้นกับ regime

**สำหรับ portfolio 5 ตัว + งบ $10k → คำแนะนำ practical:**
- **Quarterly check + threshold 20% drift trigger** = balance ระหว่าง vol harvest + cost
- ห้าม monthly — fee + spread กิน
- ห้าม daily — เหมาะ portfolio 10+ ตัว ไม่ใช่ 5 ตัว

### 2.4 Tools + Fees + ภาษีไทย (สำคัญที่สุดสำหรับงบ $10k)

**Tools comparison:**

| Platform | สถานะ 2026 | Fee | ใช้กับไทยได้? |
|---|---|---|---|
| Shrimpy | เปิด | $19/เดือน | ใช้กับ Binance global เท่านั้น = เสีย tax |
| 3Commas | เปิด | $15/เดือน | rebalance feature ลด priority แล้ว |
| ICONOMI | เปิด | 0.5%/trade | ไม่รับ THB deposit |
| Hummingbot | เปิด (free) | ฟรี | ต้องเป็น dev — ไม่เหมาะ retail |
| **Manual rebalance** | — | **fee เฉพาะ trade** | **เหมาะสุดสำหรับ $10k quarterly** |

→ subscription $19/เดือน = $228/ปี = **มากกว่า trading fee ทั้งปี 10-100 เท่า** สำหรับงบ $10k → manual ดีกว่าแน่นอน

**Exchange Fee (Spot Trading):**

| Exchange | Maker | Taker | ไทย licensed? |
|---|---|---|---|
| Binance global | 0.10% | 0.10% | ❌ → เสียภาษี |
| Binance TH (Gulf Binance) | 0.10% | 0.10% | ✅ → tax exemption |
| **Bitkub** | **0.25%** | **0.25%** | **✅ → tax exemption** |
| Bybit | 0.10% | 0.10% | ❌ |
| OKX | 0.08% | 0.10% | ❌ |

**ภาษีไทย 2026 — กฎสำคัญ (กฎกระทรวง 399, มีผล ม.ค. 2025 - ธ.ค. 2029):**
- กำไร crypto บน exchange SEC ไทย licensed = **ยกเว้นภาษีบุคคล 100%** ถึง 2029
- VAT 7% = ยกเว้นถาวร
- Exchange ต่างชาติ (Binance global, Bybit, OKX) = **ไม่ได้ยกเว้น** ต้อง declare เป็นรายได้ progressive 0-35%
- Staking / Airdrop / Mining = **ไม่ยกเว้น** — เสียภาษีปกติ

**Cost simulation $10k portfolio:**

| Strategy | Bitkub (0.25%) | Binance TH (0.10%) |
|---|---|---|
| Quarterly (4x/ปี) | $5/ปี | $2/ปี |
| Monthly (12x/ปี) | $15/ปี | $6/ปี |
| Threshold 5% (~10x/ปี) | $12.50/ปี | $5/ปี |

(Spread cost ที่ซ่อนอยู่ใน Bitkub คู่ minor เช่น SOL/THB อาจสูงกว่า fee 2-4 เท่า)

→ **Stack แนะนำสำหรับ $10k Thai retail:**
- ชั้นหลัก: **Binance TH (Gulf Binance)** — fee ถูก + tax exempt + asset ครบ 5 ตัว
- ชั้น backup: **Bitkub** — liquidity ดีสุดในไทย + on-ramp THB สะดวก

### 2.5 Major Events Impact — กระทบ rebalance portfolio ยังไง

| Event | วันที่ | ผลต่อ portfolio 5 ตัว |
|---|---|---|
| **LUNA collapse** | 7-13 พ.ค. 2022 | LUNA ไม่ได้อยู่ใน portfolio = safe / **แต่ USDT depeg ชั่วคราว $0.95** ทำให้ floor 20% สั่นนิดหนึ่ง |
| **FTX collapse** | 8-11 พ.ย. 2022 | **SOL -50% ใน 1 สัปดาห์** ($250 → $8 ใน 1 ปี) — rebalance threshold trigger ซื้อ SOL ที่ $10-15 = ดีถ้าถือถึง 2024 ($295 ATH) / เจ็บถ้าหยุดที่ก้น |
| **USDC depeg (SVB)** | 11 มี.ค. 2023 | USDC แตะ $0.87 — portfolio นี้ไม่มี USDC = safe |
| **ETH Merge** | 15 ก.ย. 2022 | ETH -8% ใน 24h, -25% ใน 1 เดือน — ไม่กระทบ rebalance ระบบมาก |
| **BTC Halving** | 19 เม.ย. 2024 | BTC +122% ปีนั้น — rebalance ตัด BTC ไป buy SOL/ETH = แพ้ hold BTC |
| **2025 BTC Dominance** | ทั้งปี 2025 | BTC dominance 72.4% (8-year high) — rebalance equal-weight = แพ้ BTC ล้วนชัดเจน |

### 2.6 Risks + Edge Cases — กับดักที่ทำให้ rebalance พัง

**1. Tail risk — asset หายถาวร (กับดักร้ายแรงสุด)**
- LUNA $116 → $0.00008 ใน 6 วัน — rebalance ที่ "ซื้อตอนลง" = พินาศ
- FTT $26 → $1 ใน 3 วัน
- ความต่าง: BTC/ETH/SOL ลงแล้วกลับมา / LUNA / FTT ไม่กลับ — ระบบ rebalance ไม่รู้ผลต่างนี้
- **Mitigation: Kill switch + asset selection criteria + position cap**

**2. Stablecoin depeg risk:**
- USDT พ.ค. 2022: $0.9455 (กลับมา 24h)
- USDC มี.ค. 2023: $0.87 (กลับมา 2-3 วัน หลัง Fed รับประกัน SVB)
- UST พ.ค. 2022: $0 ถาวร (algorithmic = ไม่มี real backing)
- **Mitigation: ใช้เฉพาะ fiat-backed (USDT/USDC) ห้าม algorithmic / กระจาย issuer ถ้าถือเยอะ**

**3. Exchange risk:**
- FTX: lock fund ถาวร $8B (พ.ย. 2022)
- Binance: settlement $4.3B + CZ resign (พ.ย. 2023) → BNB ลง 12% / outflow $1B
- Zipmex (TH): หยุด withdraw ก.ค. 2022 → ปิดในไทย
- Bitkub (TH): wash trading + insider trading CTO → ปรับ 24.2M THB
- **Mitigation: ไม่เก็บทุกอย่างใน exchange เดียว / ถือ > 500k THB → แบ่ง 2 exchange + cold wallet**

**4. Per-asset risk profile:**

| Asset | Tail risk | Regulatory | Concentration | Verdict |
|---|---|---|---|---|
| BTC | ต่ำ | ต่ำ (commodity) | ต่ำ (decentralized) | safest |
| ETH | ต่ำ-กลาง | กลาง | ต่ำ | safe |
| BNB | กลาง | **สูง** (SEC unresolved) | **สูง** (Binance control) | watch |
| SOL | ต่ำ-กลาง (ปัจจุบัน) | กลาง | กลาง (ประวัติ Alameda dump) | recovered |
| USDT | กลาง (Tether opacity) | กลาง | สูง (Tether ผูกขาด) | acceptable |

**5. Pseudo-diversification:**
- BTC/ETH/BNB/SOL ตอน crisis correlation 0.79-0.90 → ลงพร้อมกัน
- "กระจาย 4 ตัว" แต่จริงๆ = "ถือ crypto beta 1 ตัว"
- **มี USDT 15-20% เท่านั้นที่ diversify จริง**

**6. Behavioral pitfall:**
- ตอน crash 2022 ทุกตัวลงพร้อมกัน → ไม่มีตัวไหน "กำไร" ให้ขาย
- คนส่วนใหญ่หยุด rebalance ตอนกลัวสุด = พลาดซื้อถูก
- ระบบ auto-rebalance ช่วยแก้ปัญหานี้ได้

---

## 3. Architecture / Decision Framework

**Decision tree สำหรับ portfolio นี้:**

| สถานการณ์ตลาด | ควรทำอะไร |
|---|---|
| Bull market ที่ alt วิ่ง (เหมือน 2021) | Rebalance ตัด winner = พลาด upside → **widen threshold หรือหยุด rebalance** asset ที่ outperform |
| Bear market ทุกตัวลง (เหมือน 2022) | USDT 20% ทำหน้าที่ floor → **rebalance threshold trigger** ซื้อ asset ลง = ดีถ้าฟื้น |
| BTC dominance สูง (เหมือน 2024-2025) | Rebalance ตัด BTC = แพ้ hold BTC → **suspend rebalance สำหรับ BTC ที่กำลัง outperform** |
| Tail event (asset ลง > 70% ใน 7 วัน) | **Kill switch** หยุด rebalance asset นั้นทันที — รอ 30 วัน ประเมินก่อนกลับมา |

**Rebalance Algorithm แนะนำสำหรับ $10k:**
```
Target weights: BTC 35% / ETH 25% / SOL 15% / BNB 10% / USDT 15%

Trigger:
  - Quarterly check (มี.ค./มิ.ย./ก.ย./ธ.ค.)
  - OR threshold: ใดๆ asset drift ±20% relative จาก target

Kill switch:
  - asset ใด ลง > 70% ใน 7 วัน → ห้าม rebalance เข้าตัวนั้น 30 วัน
  - exchange มี withdrawal halt / regulatory action → ถอนออกก่อน
  - stablecoin depeg > 3% → convert ออกทันที

Position cap:
  - ห้าม asset ใดเกิน 40% ของ portfolio (จาก target + drift)
  - USDT ห้ามต่ำกว่า 10%
```

---

## 4. Risks & Limitations

| ความเสี่ยง | ระดับ | วิธีรับมือ |
|---|---|---|
| Asset tail risk (เป็น LUNA ครั้ง 2) | สูง | Kill switch + position cap 25% + ห้าม algorithmic stablecoin |
| Exchange risk (FTX-style) | สูง | แบ่ง 2 exchange (Bitkub + Binance TH) + cold wallet > 500k THB |
| Pseudo-diversification (ลงพร้อมกัน) | สูง | USDT 15-20% เป็น real diversifier ตัวเดียว |
| Tax compliance ผิด | กลาง | ใช้ exclusive SEC ไทย licensed exchange เท่านั้น |
| Trending market แพ้ HODL | กลาง-สูง | Suspend rebalance asset ที่ outperform / ยอมรับ "Sharpe สูงกว่า แต่ return อาจน้อยกว่า BTC ล้วน" |
| Subscription tool ไม่คุ้ม | กลาง | Manual rebalance quarterly — ไม่ต้องจ่าย Shrimpy/3Commas |
| Behavioral หยุด rebalance ตอน crash | กลาง | เขียน rule ไว้ก่อน + automate ถ้าทำได้ |

---

## 5. Recommendation / Next Steps

**ตอบคำถามตรงๆ "ใช้ได้จริงไหม":**

✅ **ใช้ได้จริง** ในแง่ "ระบบลด volatility + บังคับซื้อตอน fear" — research support ชัด

⚠️ **อย่าคาดหวังว่าจะทำเงินมากกว่า hold BTC ล้วน** ใน 5 ปีข้างหน้า — ถ้า BTC dominance ยังสูง rebalance จะแพ้

❌ **อย่าใช้ tool subscription** สำหรับงบ $10k — manual quarterly คุ้มสุด

**Action items ตามลำดับ:**

1. **เปิดบัญชี Binance TH (Gulf Binance)** ถ้ายังไม่มี — verify KYC ครบ → ได้ tax exemption
2. **(ทางเลือก) เปิด Bitkub สำรอง** — สำหรับ on-ramp THB และ liquidity backup
3. **ตั้ง target weight + เขียน rule:** BTC 35 / ETH 25 / SOL 15 / BNB 10 / USDT 15 + threshold 20% drift
4. **Build backtest จริง** สำหรับ portfolio นี้ + ช่วงนี้ → ใช้ pipeline ของ YukiTanaka (ccxt fetch + apply_risk + simulate rebalance) — paper ที่มียังไม่ครอบ exact 5 ตัวนี้
5. **ทดสอบ paper trade 3 เดือน** ก่อนใส่เงินจริง — record fee + spread จริง
6. **Live $1,000 ก่อน 1 quarter** → เห็น cost จริง → scale ถึง $10k ถ้า work

**ถ้าอยากให้กูช่วยต่อ:**
- Build backtest จริงสำหรับ portfolio นี้ (reuse YukiTanaka pipeline เปลี่ยน asset เป็น crypto + เพิ่ม rebalance logic)
- Code rebalance bot — ccxt + Binance TH/Bitkub API
- Spec sheet เป็นไฟล์ตามตัวอย่าง MaxMahon stock pillar (ถ้าอยากให้ rebalance เป็น "เสาหลัก #1.5")

---

## 6. References

### Academic / Theory
| What | Source |
|---|---|
| Bernstein Rebalancing Bonus 1996 | https://www.efficientfrontier.com/ef/996/rebal.htm |
| Cuthbertson et al. 2016 (anti-rebalance) | https://dx.doi.org/10.2139/ssrn.2311240 |
| Fernholz Stochastic Portfolio Theory | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3753722 |
| Hanicova-Vojtko crypto premium | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3982120 |
| Sornmayura 2024 crypto rebalance | https://ideas.repec.org/p/gtr/gatrjs/jfbr220.html |
| Sun et al. 2006 dynamic programming | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=639284 |
| ScienceDirect 2022 stablecoin downside | https://www.sciencedirect.com/article/pii/S1062940822001735 |
| MDPI 2024 ETF rebalance | https://www.mdpi.com/1911-8074/17/12/533 |
| Vanguard Best Practices 2015 | https://pdf4pro.com/amp/view/best-practices-for-portfolio-rebalancing-vanguard-2e648f.html |
| Vanguard Rational Rebalancing 2022 | https://www.vanguardmexico.com/content/dam/intl/americas/documents/latam/en/2022/10/mx-sa-2558523-rational-rebalancing-an-analytical-approach.pdf |
| Daryanani Opportunistic Rebalance 2008 | https://www.financialplanningassociation.org/article/journal/JAN08-opportunistic-rebalancing-new-paradigm-wealth-managers |
| Kitces rebalance reduces returns | https://www.kitces.com/blog/how-rebalancing-usually-reduces-long-term-returns-but-is-good-risk-management-anyway/ |
| AQR Common Misconceptions 2017 | https://www.aqr.com/Insights/Research/White-Papers/Portfolio-Rebalancing-Common-Misconceptions |

### Performance Data
| What | Source |
|---|---|
| Bitcoin Magazine Pro annual returns | https://www.bitcoinmagazinepro.com/blog/a-decade-of-bitcoin-annual-returns-and-insights-for-investors/ |
| CoinGecko 2024 Annual Report | https://www.coingecko.com/research/publications/2024-annual-crypto-report |
| CoinGecko 2025 Annual Report | https://www.coingecko.com/research/publications/2025-annual-crypto-report |
| Crypto Research Report optimal rebalance | https://cryptoresearch.report/crypto-research/optimal-rebalancing-strategy/ |
| Quantpedia rebalance premium | https://quantpedia.com/estimating-rebalancing-premium-in-cryptocurrencies/ |
| Shrimpy backtest vs HODL | https://help.shrimpy.io/backtests/rebalance-vs-hodl |
| CME Group BTC-ETH correlation 2023 | https://www.cmegroup.com/insights/economic-research/2023/three-factors-driving-the-ether-bitcoin-price-nexus.html |
| Fidelity Halving One Year Later | https://www.fidelitydigitalassets.com/research-and-insights/2024-bitcoin-halving-one-year-later |
| VanEck optimal crypto allocation | https://www.vaneck.com/us/en/blogs/digital-assets/matthew-sigel-optimal-crypto-allocation-for-portfolios/ |

### Events / Risks
| What | Source |
|---|---|
| Harvard Law LUNA Anatomy | https://corpgov.law.harvard.edu/2023/05/22/anatomy-of-a-run-the-terra-luna-crash/ |
| Chainalysis UST Collapse | https://www.chainalysis.com/blog/how-terrausd-collapsed/ |
| NBER W31160 Terra-Luna | https://www.nber.org/papers/w31160 |
| Solana FTX Bankruptcy facts | https://solana.com/news/solana-facts-ftx-bankruptcy |
| ScienceDirect FTX academic paper | https://www.sciencedirect.com/science/article/pii/S037843712300599X |
| Bloomberg USDT Depeg May 2022 | https://www.bloomberg.com/news/articles/2022-05-12/tether-moves-to-reassure-market-after-biggest-stablecoin-slips |
| CNBC USDC SVB Depeg | https://www.cnbc.com/2023/03/11/stablecoin-usdc-breaks-dollar-peg-after-firm-reveals-it-has-3point3-billion-in-svb-exposure.html |
| S&P Global Stablecoin Deep Dive | https://www.spglobal.com/en/research-insights/special-reports/stablecoins-a-deep-dive-into-valuation-and-depegging |
| CoinDesk Binance DOJ $4.3B | https://www.coindesk.com/policy/2023/11/21/binance-to-settle-charges-with-us-doj-source |
| Helius Solana Outage History | https://www.helius.dev/blog/solana-outages-complete-history |
| Decrypt SOL ATH Recovery | https://decrypt.co/292874/solana-hits-all-time-high-price |
| OECD Crypto Winter Report | https://www.oecd.org/content/dam/oecd/en/publications/reports/2022/12/lessons-from-the-crypto-winter_37bf4b9e/199edf4f-en.pdf |
| CoinDesk Zipmex Thailand | https://www.coindesk.com/business/2022/09/07/thai-sec-files-police-complaint-against-crypto-exchange-zipmex |

### Tools / Fees / Thai Tax
| What | Source |
|---|---|
| Binance fee schedule | https://www.binance.com/en/fee/schedule |
| Bitkub trading fees | https://www.bitkub.com/en/fee/cryptocurrency |
| Bybit fee structure | https://www.bybit.com/en/help-center/article/Trading-Fee-Structure |
| Shrimpy review | https://coinsutra.com/shrimpy-review/ |
| 3Commas pricing | https://3commas.io/pricing |
| ICONOMI fees | https://www.iconomi.com/fees-disclosure |
| ExpatTax Thailand crypto | https://www.expattaxthailand.com/thailand-crypto-tax-exemption-2025-2029/ |
| Acclime Thailand digital asset | https://thailand.acclime.com/news/digital-asset-tax-exemption/ |
| Forvis Mazars TH crypto tax | https://www.forvismazars.com/th/en/insights/doing-business-in-thailand/tax/thailand-exempts-tax-on-digital-asset-gains |
| Nishimura Thailand 2029 | https://www.nishimura.com/en/knowledge/publications/20250701-113956 |

---

## Conflicts / Uncertainties (สิ่งที่ research ตอบไม่ได้แน่)

1. **ไม่มี backtest paper สำหรับ exact portfolio นี้ + ช่วงนี้** — ทุก inference จาก paper ใกล้เคียง → ต้อง run จริง
2. **Rebalance สร้าง alpha จริงไหม** — Fernholz บอก yes / Cuthbertson บอก no — magnitude เล็กกว่าที่ practitioner blog อ้าง
3. **Optimal frequency for crypto** — academic บอก annual + wide threshold / commercial บอก weekly + tight — ขัดกัน depend on regime
4. **Thai tax: rebalance trade นับเป็น taxable event ไหม** — กฎไม่ได้ระบุชัด แต่ถ้าทำบน licensed exchange → ยกเว้นอยู่แล้ว
5. **Shrimpy 77.1% outperformance** — มาจาก period pre-2020 (ก่อน SOL era) — ยังไม่มี independent academic verify
6. **Binance TH fee + asset list ครบไหม** — ไม่มี official English fee page → ต้องเช็คใน app
