# MaxMahon — DESIGN System

> สเปกหน้าตา (visual identity) ของ MaxMahon — **AI ต้องอ่านไฟล์นี้ก่อนเขียน/แก้ UI ทุกครั้ง**
> Source-of-truth: `web/v6/shared/tokens.css` + `web/v6/shared/base.css` + `web/v6/shared/mobile.css` + `web/v6/static/css/components.css`
> ถ้า token ขัดกัน → ไฟล์นี้คือคำตัดสิน (ไม่ใช่ component inline style)

---

## 1. Identity

- **มู้ด:** Robinhood-inspired — disciplined / minimalist / data-first / serif accent (IBM Plex Serif Thai)
- **กลุ่มสี:** Sage (positive) + Rose (negative) + Wheat (warning) + Slate-Blue (info) + Lavender (purple secondary) บน warm cream paper background
- **Typography:** Thai-first (IBM Plex Serif Thai) + Inter (UI) + JetBrains Mono (data)
- **Theming:** 2 mode auto-switch ตาม `prefers-color-scheme` (OS preference — ไม่มี toggle ใน UI)
  - `light` (default `:root`)
  - `dark` (`@media (prefers-color-scheme: dark)`)
- **Layout:** desktop/mobile **แยกชั้น** ที่ breakpoint **900px** — แยกทั้ง HTML shell + JS module + CSS override
- **Token system:** 2-layer — primitive swatches → semantic tokens (ห้าม component อ้าง primitive ตรง)

---

## 2. Color Tokens

> ทุก token override ใน dark mode — component อ้าง `var(--xxx)` พอ ไม่ต้องสน mode

### 2.1 Primitive Layer (base swatches — internal use)

| Token | Value |
|-------|-------|
| `--sage-500` | `#7ba688` (positive accent หลัก) |
| `--sage-600` | `#5d8c69` (positive strong) |
| `--rose-500` | `#c98b85` (negative/danger) |
| `--wheat-500` | `#caa673` (warning) |
| `--lavender-500` | `#9d90c7` (purple secondary) |
| `--slate-blue-500` | `#84a8c9` (info) |

**กฎ:** ห้าม component อ้าง primitive ตรง — ใช้ semantic เท่านั้น

### 2.2 Semantic — Light mode

#### Background

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-base` | `#f5f5f0` | พื้นหลังหน้าหลัก |
| `--bg-outside` | `#e8e6dd` | ขอบนอก/page edge |
| `--bg-surface` | `#ffffff` | card / surface |
| `--bg-surface-2` | `#ebebe4` | hover / elevated |
| `--bg-elevated-start` | `#f1eee3` | gradient start (hero) |
| `--bg-elevated-end` | `#e6e2d4` | gradient end (hero) |
| `--bg-elevated-border` | `#d9d4c4` | ขอบ elevated section |
| `--btn-on-elevated` | `rgba(255,255,255,.75)` | button บน elevated bg |

#### Foreground (text)

| Token | Value | Usage |
|-------|-------|-------|
| `--fg-primary` | `#3b4050` | text หลัก |
| `--fg-secondary` | `#5a6072` | text รอง |
| `--fg-dim` | `#878d9a` | label / tertiary |
| `--fg-mute` | `#b2b6c0` | very faint (ใช้น้อย) |

#### Border

| Token | Value | Usage |
|-------|-------|-------|
| `--border-subtle` | `#e6e4db` | hairline divider |
| `--border-strong` | `#d1cec1` | rule ปกติ |

#### Semantic Accents

| Token | Value | Usage |
|-------|-------|-------|
| `--c-positive` | `#7ba688` | primary action / positive sentiment |
| `--c-positive-strong` | `#5d8c69` | darker positive |
| `--c-positive-soft` | `#e9f1eb` | bg positive context |
| `--c-positive-tint` | `#f3f8f4` | bg positive อ่อนสุด |
| `--c-positive-border` | `rgba(123,166,136,.35)` | border positive |
| `--c-negative` | `#c98b85` | danger / loss |
| `--c-negative-soft` | `#f4eae8` | bg negative |
| `--c-negative-border` | `rgba(201,139,133,.35)` | |
| `--c-warn` | `#caa673` | warning |
| `--c-warn-soft` | `#f5eed8` | bg warning |
| `--c-warn-fg` | `#8a6d3a` | text warning |
| `--c-warn-border` | `rgba(202,166,115,.3)` | |
| `--c-info` | `#84a8c9` | info |
| `--c-info-soft` | `#e6eef5` | bg info |
| `--c-info-fg` | `#456a8c` | text info |
| `--c-purple` | `#9d90c7` | secondary brand |
| `--c-purple-soft` | `#ebe7f4` | bg purple |
| `--c-purple-fg` | `#6a5c9e` | text purple |

#### Portfolio Role Badge

| Token | Value |
|-------|-------|
| `--role-anchor-bg` | `linear-gradient(135deg, #7ba688, #5d8c69)` |
| `--role-anchor-fg` | `#ffffff` |
| `--role-support-bg` | `linear-gradient(135deg, #e7eaf0, #c9cfdb)` |
| `--role-support-fg` | `#4a5264` |
| `--role-tail-bg` | `#ebebe4` |
| `--role-tail-fg` | `#878d9a` |

#### Rank Medal

| Token | Value |
|-------|-------|
| `--rank-gold-start` | `#f2e5ba` |
| `--rank-gold-end` | `#d9c08a` |
| `--rank-gold-fg` | `#6d5524` |
| `--rank-silver-start` | `#e7eaf0` |
| `--rank-silver-end` | `#c9cfdb` |
| `--rank-silver-fg` | `#4a5264` |

#### Chart

| Token | Value |
|-------|-------|
| `--chart-grid` | `rgba(59,64,80,0.15)` |
| `--chart-grid-strong` | `rgba(59,64,80,0.22)` |
| `--chart-fill-soft` | `rgba(59,64,80,0.06)` |
| `--chart-fill-medium` | `rgba(59,64,80,0.08)` |

#### Modal scrim

| Token | Value |
|-------|-------|
| `--modal-scrim` | `rgba(15,17,21,0.55)` |

### 2.3 Semantic — Dark mode

`@media (prefers-color-scheme: dark)` override:

| Token | Value (dark) |
|-------|--------------|
| `--bg-base` | `#1c1f25` |
| `--bg-surface` | `#262a32` |
| `--fg-primary` | `#e4e6eb` |
| `--fg-secondary` | `#b3b7c1` |
| `--c-positive-soft` | `rgba(123,166,136,.14)` (alpha-based) |
| `--c-negative-soft` | `rgba(201,139,133,.14)` |
| `--shadow-card` | `0 2px 10px rgba(0,0,0,.28)` (inverted opacity) |

**กฎ:** ทุก token light mode ต้องมี dark counterpart — ห้ามขาด

### 2.4 Legacy aliases (backward compat — ใช้กับ template เก่า)

| Old token | Maps to |
|-----------|---------|
| `--paper` | `--bg-base` |
| `--ink` | `--fg-primary` |
| `--accent` | `--c-positive-strong` |
| `--rule` | `--border-strong` |

**กฎ:** ไม่ใช้ alias ใน code ใหม่ — ใช้ semantic ตรง

---

## 3. Typography

### Font families

| Token | Stack |
|-------|-------|
| `--font-head` | `Inter, "IBM Plex Serif Thai", -apple-system, system-ui, sans-serif` |
| `--font-body` | `Inter, "IBM Plex Serif Thai", -apple-system, system-ui, sans-serif` |
| `--font-mono` | `"JetBrains Mono", ui-monospace, "Courier New", monospace` |
| `--font-micro` | `"JetBrains Mono", "IBM Plex Serif Thai", monospace` |

### Type scale (rem-based — 1rem = 16px desktop / 15px mobile)

| Token | Value | Desktop px | Usage |
|-------|-------|-----------|-------|
| `--fs-xs` | `0.72rem` | 11.5 | micro label / uppercase |
| `--fs-sm` | `0.82rem` | 13 | caption / small text |
| `--fs-base` | `1rem` | 16 | body |
| `--fs-md` | `1.14rem` | 18 | list header |
| `--fs-lg` | `1.4rem` | 22.4 | card title |
| `--fs-xl` | `1.85rem` | 29.6 | section heading |
| `--fs-2xl` | `2.6rem` | 41.6 | page headline |
| `--fs-3xl` | `3.8rem` | 60.8 | hero / large emphasis |

### Font weights

| Weight | Usage |
|--------|-------|
| 400 | body |
| 500 | secondary heading / label |
| 600 | nav / filter |
| 700 | emphasis / card title |
| 800 | section header |
| 900 | page headline / hero |

### Text utilities

| Class | Effect |
|-------|--------|
| `.serif` | `font-family: var(--font-head)` |
| `.mono` | mono + `font-variant-numeric: tabular-nums` |
| `.uppercase` | uppercase + `letter-spacing: 0.16em` |
| `.smallcaps` | `letter-spacing: 0.08em` |
| `.dim` | `color: var(--fg-dim)` |
| `.faint` | `color: var(--fg-mute)` |
| `.micro` | mono + `--fs-xs` + `letter-spacing: 0.14em` + uppercase |

### Font features (global)

```css
font-feature-settings: "kern" 1, "liga" 1;
-webkit-font-smoothing: antialiased;
text-rendering: optimizeLegibility;
```

**กฎ:** ตัวเลข/ราคาใช้ `.mono` หรือ `font-variant-numeric: tabular-nums` เสมอ (กัน digit shift)

---

## 4. Spacing & Layout

### Spacing scale (rem-based)

| Token | Value | px (desktop) | Use case |
|-------|-------|--------------|----------|
| `--sp-1` | `0.25rem` | 4 | tight margin |
| `--sp-2` | `0.5rem` | 8 | standard gap |
| `--sp-3` | `0.75rem` | 12 | |
| `--sp-4` | `1rem` | 16 | section gap |
| `--sp-5` | `1.5rem` | 24 | section margin |
| `--sp-6` | `2rem` | 32 | **container horizontal padding** |
| `--sp-7` | `3rem` | 48 | extra large |
| `--sp-8` | `4rem` | 64 | hero spacing |

### Layout container

| Token | Value | Usage |
|-------|-------|-------|
| `--col-max` | `1320px` | desktop max-width |
| `--col-narrow` | `720px` | article column |

### Container rules

- `.container` desktop: `max-width: 1320px; margin: 0 auto; padding: 0 var(--sp-6)`
- `.container` mobile: `padding: 0 16px` (override)
- `.narrow`: `max-width: 720px` (article-like content)

### Rule weights

| Token | Value |
|-------|-------|
| `--rule-thin` | 1px (hairline) |
| `--rule-med` | 2px |
| `--rule-thick` | 4px (heavy divider) |

### Breakpoints

| Width | Cut |
|-------|-----|
| **900px** | desktop ↔ mobile split (HTML shell + JS module + CSS) |
| **1100px** | secondary: portfolio builder 2-col → 1-col |

---

## 5. Border Radius

| Token | Value | Standard usage |
|-------|-------|----------------|
| `--r-0` | 0 | sharp |
| `--r-1` | 1px | barely rounded |
| `--r-2` | 2px | filter chip / tag |
| `--r-3` | 8px | button / card edge |
| `--r-4` | 14px | **card (standard)** |
| `--r-5` | 18px | portfolio section |
| `--r-6` | 24px | modal / large elevated |

**กฎ:** card = `--r-4` (14px) เป็น default

---

## 6. Shadows

| Token | Value (light) | Usage |
|-------|---------------|-------|
| `--shadow-card` | `0 2px 10px rgba(60,66,82,.06)` | card hover |
| `--shadow-elevated` | `0 8px 24px rgba(60,66,82,.08)` | modal / hero |
| `--shadow-accent-positive` | `0 4px 12px rgba(123,166,136,.22)` | brand glow |
| `--shadow-toggle` | `0 2px 6px rgba(60,66,82,.12)` | small interactive |

Dark mode: shadow opacity เพิ่ม (เช่น `--shadow-card: 0 2px 10px rgba(0,0,0,.28)`)

---

## 7. Desktop/Mobile Split Pattern

### Shared assets (load both)

| File | Purpose |
|------|---------|
| `web/v6/shared/tokens.css` | color + typography + spacing tokens |
| `web/v6/shared/base.css` | reset + typography utilities + base styles |
| `web/v6/static/css/components.css` | page-level blocks (lede/hero/report/portfolio/app-header/bottom-nav) |

### Desktop only

| File | Note |
|------|------|
| `web/v6/desktop/index.html` | shell (tokens + base + components — NO mobile.css) |
| `web/v6/static/js/pages/{route}.js` | page module (home/report/watchlist/portfolio/settings/login) |

- Header: `.app-header` grid 3-col (brand | nav | icon buttons)
- Nav: horizontal top nav 4 links
- Layout: card grid 3-col / summary strip multi-col flex / filter bar flex wrap

### Mobile only

| File | Note |
|------|------|
| `web/v6/mobile/index.html` | shell (tokens + base + **mobile.css** + components — mobile.css โหลด SECOND) |
| `web/v6/static/js/pages/{route}.mobile.js` | mobile page module |
| `web/v6/shared/mobile.css` | override ≤900px |

- Header: hidden / replaced ด้วย `.bottom-nav`
- Nav: bottom-nav fixed 4 tabs (56px per item, 88px total with safe-area)
- Layout: card grid 1-col / summary strip 2-col grid / filter bar horizontal scroll

### Detection logic

- Server-side: ไม่มี UA detection ใน backend
- Client-side: `device.js` — touch UA pattern → redirect `/m` on load (one-time, ไม่ loop)
- Direct: `/` → desktop, `/m` → mobile

### Mobile-specific overrides (≤900px in mobile.css)

| Override | From → To |
|----------|-----------|
| Body font-size | 16px → 15px |
| Body padding-bottom | 0 → `calc(88px + env(safe-area-inset-bottom))` |
| Container padding | `var(--sp-6)` (32px) → 16px |
| Card grid | 3-col → 1fr |
| Filter bar | flex wrap → `overflow-x: auto; flex-wrap: nowrap` |
| Filter chip | `padding: 4px 8px` → `padding: 6px 12px; min-height: 32px` |
| Summary strip | multi-col flex → `grid-template-columns: 1fr 1fr` |
| Tables | natural width → `overflow-x: auto; min-width: 560px` |
| Score block | 2-col → 1-col |
| Portfolio | 2-col grid → 1-col stack |
| Bottom-nav | hidden → `display: grid; grid-template-columns: repeat(4, 1fr); height: 56px` |

**กฎเหล็ก mobile:**
1. แก้ desktop → ต้อง check ว่า mobile.css override ตามไหม
2. mobile.css **โหลดทีหลัง** base.css — specificity ไม่ต้องสูง override ได้ตรงๆ
3. ทุก fixed element ต้องคำนวณ `env(safe-area-inset-bottom)` (iOS notch)

---

## 8. Component Specs

### 8.1 Stock Card (`.card`)

- Layout: desktop 3-col grid / mobile 1-col
- Padding: `var(--sp-5)` ⇒ 24px
- Radius: `var(--r-4)` ⇒ 14px
- Background: `var(--bg-surface)`
- Border: `1px solid var(--border-subtle)`
- Hover: `border-color: var(--c-positive-border); box-shadow: var(--shadow-card); .card-sym color → var(--c-positive)`

**Inner structure:**
- `.card-head` — symbol + name
- `.card-sym` — symbol large (font-weight 700)
- `.card-name` — company name (font-weight 500, dim)
- `.card-tags` — flex wrap tags
- `.card-score-row` — score-big + score-max + score-delta

### 8.2 Filter Bar + Chips

- `.filter-bar`: flex container, padding `var(--sp-3) 0`, border top+bottom `1px solid var(--border-subtle)`
- `.filter-chip`: padding `4px 8px` (desktop) / `6px 12px` (mobile), radius `var(--r-2)`, border `1px solid var(--border-strong)`
- `.filter-chip:hover`: `border-color: var(--border-strong); color: var(--fg-primary)`
- `.filter-chip.active`: `background: var(--c-positive); color: #fff; border-color: var(--c-positive)`

**Sector chips:** multi-select OR logic — dynamic from screener output (ไม่ hardcode)
**Sort chips:** single-select radio (Score / Yield / P/E / P/BV / Δ Score)
**Signal chips:** single-select radio (All / NIWES_5555 / HIDDEN_VALUE / DEEP_VALUE / QUALITY_DIVIDEND)

### 8.3 Summary Strip

- `.summary-strip`: flex multi-col (desktop) / `grid-template-columns: 1fr 1fr` (mobile)
- `.summary-cell` — single metric block
- `.label` — small uppercase, `color: var(--fg-dim)`
- `.val` — large number, `font-family: var(--font-mono)`, `font-weight: 800`

### 8.4 Lede Block

- `.lede-block`: full-width section, background `linear-gradient(var(--bg-elevated-start), var(--bg-elevated-end))`, border-bottom `1px solid var(--bg-elevated-border)`
- `.lede-headline`: `--fs-xl` to `--fs-2xl`, serif
- `.lede-sub`: `--fs-md`, dim

### 8.5 Mini Chart Strip

- `.mini-chart-strip`: flex 2-col (chart | leader list)
- `.mini-chart-box`: Chart.js canvas, height ~140px
- `.strip-right`: leader stocks list, max 5

### 8.6 App Header (desktop)

- `.app-header`: grid 3-col (brand | nav | icon-buttons)
- `.app-header .brand`: logo + name, font weight 800
- `.app-header nav`: 4 horizontal links — active = `color: var(--c-positive-strong); border-bottom: 2px solid var(--c-positive)`
- Hidden in mobile

### 8.7 Bottom Nav (mobile)

- `.bottom-nav`: fixed bottom, z-index 60, grid 4-col, height 56px per item (88px with safe-area)
- `.bn-item`: flex column center, gap `var(--sp-1)`
- `.bn-item.active`: `color: var(--c-positive)`
- `.bn-item` inactive: `color: var(--fg-dim)`

### 8.8 Report Hero

- `.report-hero`: full-width gradient section, `--bg-elevated-start → --bg-elevated-end`
- `.report-hero-price`: huge number `--fs-3xl`, mono, tabular-nums
- Verdict chip: `.v6-verdict-chip.buy/hold/sell`

### 8.9 5-Pillar Score Block

- `.v6-score-block`: desktop 2-col (score display | chart) / mobile 1-col
- `.v6-score-display`: center, large `--fs-3xl` + `/100` suffix
- `.score-chart-wrap`: Chart.js doughnut chart (5 segments — 5 pillars)
- `.v6-checklist-item`: desktop grid 5-col / mobile 1-col stack
  - Col 1: filter name (e.g., "Yield ≥ 5%")
  - Col 2: actual value (e.g., "7.2%")
  - Col 3: threshold (e.g., "≥ 5%")
  - Col 4: pass/fail mark (`.v6-check-mark.pass/fail`)
  - Col 5: reason (if fail)

### 8.10 Portfolio Role Badge

- `.role-badge.anchor`: `background: var(--role-anchor-bg)` (gradient), `color: var(--role-anchor-fg)` (#fff)
- `.role-badge.supporting`: `--role-support-bg/fg`
- `.role-badge.tail`: `--role-tail-bg/fg`
- Padding: `var(--sp-1) var(--sp-3)`, radius `var(--r-2)`, font weight 600

### 8.11 Verdict Chip

- `.v6-verdict-chip.buy`: bg `var(--c-positive)`, fg #fff
- `.v6-verdict-chip.hold`: bg `var(--c-warn-soft)`, fg `var(--c-warn-fg)`
- `.v6-verdict-chip.sell`: bg `var(--c-negative)`, fg #fff
- Radius: `var(--r-3)` ⇒ 8px

### 8.12 Toast

- `.v6-ops-toast-in`: keyframe — opacity 0→1, translateY 8px→0, **200ms ease-out**

---

## 9. Signal Tags (Domain-specific)

### Hard filter tags

| Tag | Condition | Score impact | UI |
|-----|-----------|--------------|----|
| `NIWES_5555` | passes all hard filters (5%+ yield + 5+ EPS streak + PE ≤15 + PBV ≤1.5 + mcap ≥5B) | primary | `<span class="tag primary">Niwes 5-5-5-5</span>` |
| `NIWES_GROWING` | yield 2-5% + DPS growth ≥3y + EPS 5/5 + PE ≤15 + PBV ≤1.5 | +10 boost | `<span class="tag">Niwes Growing</span>` |
| `HIDDEN_VALUE` | listed in hidden_value_holdings.json | — | `<span class="tag">Hidden Value</span>` |
| `QUALITY_DIVIDEND` | yield ≥5% + payout <70% + streak ≥10y | — | `<span class="tag">Quality Div</span>` |
| `DEEP_VALUE` | P/E ≤8 + P/BV ≤1.0 | — | `<span class="tag">Deep Value</span>` |

### Warning tags

| Tag | Condition | Score impact | UI |
|-----|-----------|--------------|----|
| `DIVIDEND_TRAP` | yield >8% + ROE declining + payout >100% | −20 | internal flag (not rendered) |
| `YIELD_SPIKE_FROM_PRICE_DROP` | yield_now / 5y_avg > 1.8x | −5 | planned report deep-dive |
| `DATA_INCOMPLETE` | yield >0 but dividend_history empty | hard FAIL | `<span class="tag dim">Data Incomplete</span>` |
| `DATA_WARNING` | outliers (yield>20% / growth>300% / ROE>150%) | −5 | not rendered yet |

### Case pattern tags (8 deterministic)

- `RETAIL_DEFENSIVE_MOAT` (CPALL)
- `BANK_VALUE_PBV1` (TCAP)
- `HOLDING_CO_HIDDEN` (QH)
- `UTILITY_DEFENSIVE`
- `HOSPITAL_AGING`
- `F&B_CONSUMER_BRAND`
- `ENERGY_CYCLICAL_EXIT`
- `VIETNAM_GROWTH_EXPOSURE`

UI: render first case tag เป็น `<span class="tag">{first_case_tag}</span>` ใน report

### Tag base style

- `.tag`: padding `var(--sp-1) var(--sp-2)`, radius `var(--r-2)`, `--fs-sm`, weight 600, border `1px solid var(--border-strong)`
- `.tag.primary`: bg `var(--c-positive)`, color #fff, no border
- `.tag.dim`: color `var(--fg-dim)`, border `1px dashed var(--border-strong)`

---

## 10. Score System (Niwes Dividend-First v2)

5 pillar — total 100 points + modifier

| Pillar | Max | Components |
|--------|-----|------------|
| **Dividend** | 50 | Yield (15) + Streak (15) + Payout sustainability (10) + Growth/Stable (10) |
| **Valuation** | 25 | P/E (10) + P/BV (10) + EV/EBITDA (5, neutral 2 if None) |
| **Cash Flow** | 10 | FCF positive (5) + OCF/NI ratio (3) + Interest coverage (2) |
| **Hidden Value** | 5 | `check_hidden_value` flag |
| **Track Record** | 10 | Revenue CAGR 5y (5) + EPS CAGR 5y (5) |

**Modifier:** Valuation Grade A/B/C/D/F → +5/+2/0/−3/−8

Final score capped 0–100

---

## 11. Animations

| Pattern | Effect | Duration |
|---------|--------|----------|
| Standard transition | `transition: all 120ms ease` | 120ms |
| Color transition | `transition: color 120ms ease` | 120ms |
| Toast in | opacity 0→1 + translateY 8px→0 | 200ms ease-out |
| Card hover | border + shadow + sym color | 120ms ease |
| Chip active | bg + color | 120ms ease |

---

## 12. Drift Candidates (รอ refactor — ของที่ยัง hardcode)

> ของพวกนี้ยังไม่อยู่ในระบบ token — ถ้าจะแก้สีต้องไปแก้ inline
> ทำ DESIGN.md เพื่อให้รู้ก่อน — ไม่ต้องรีบ refactor

### 12.1 Inline style ใน JS page modules
- `home.js`, `report.js` ใช้ `style="..."` ผสม:
  - ✅ ดี: `style="color:var(--fg-primary)"`
  - ⚠️ drift: `style="padding:10px"` (hardcode px แทน `var(--sp-3)`)
  - ⚠️ drift: `style="margin-top:10px"` (ควรเป็น `var(--sp-3)` หรือ `var(--sp-4)`)
- ตัวอย่าง: `.card-price-row` ใช้ `margin-top:10px; padding-top:8px` ตรง

### 12.2 ไม่มี icon size token
- Icon ใช้ `font-size: 18px / 20px` ฝัง CSS
- ข้อเสนอ: `--icon-sm / --icon-md / --icon-lg`

### 12.3 ไม่มี touch target token
- ฝัง `min-height: 44px` (watchlist) / `min-width: 40px` (icon button) กระจาย
- ข้อเสนอ: `--touch-target: 44px` (iOS guideline)

### 12.4 ไม่มี z-index token
- `bottom-nav z-index: 60` hardcode
- ข้อเสนอ: `--z-nav / --z-modal / --z-toast`

### 12.5 `--bg-elevated-start/end` gradient ใช้ inline ใน lede + report hero
- ปัจจุบัน OK เพราะเป็น token แล้ว — แต่หลาย component ทำซ้ำ pattern
- ข้อเสนอ: utility class `.bg-elevated-gradient`

### 12.6 ไม่มี dark mode toggle ใน UI
- ปัจจุบัน OS preference only (`prefers-color-scheme: dark`)
- Future: เพิ่ม toggle ใน Settings

---

## 13. Component Module Map

| Page | Desktop module | Mobile module | Components |
|------|----------------|---------------|------------|
| Home | `pages/home.js` | `pages/home.mobile.js` | Lede + summary strip + mini chart + filter bar + stock cards |
| Report | `pages/report.js` | `pages/report.mobile.js` | Hero + 5-pillar score + checklist + analysis text + case tag |
| Watchlist | `pages/watchlist.js` | `pages/watchlist.mobile.js` | Table (desktop) / card stack (mobile) + star + compare modal |
| Portfolio | `pages/portfolio.js` | `pages/portfolio.mobile.js` | 2-col layout + sector chips + pie chart + role badges + simulator |
| Settings | `pages/settings.js` | `pages/settings.mobile.js` | Config blocks + toggles + sliders + day chips |
| Login | `pages/login.js` | `pages/login.mobile.js` | Supabase Google OAuth card |

---

## 14. File Map

| File | Role |
|------|------|
| `web/v6/shared/tokens.css` | color + typography + spacing + radius + shadow tokens + dark mode |
| `web/v6/shared/base.css` | reset + typography utilities + base styles (card/filter/button/table) |
| `web/v6/shared/mobile.css` | ≤900px overrides (loaded SECOND on mobile shell only) |
| `web/v6/static/css/components.css` | page-level blocks + app-header + bottom-nav |
| `web/v6/desktop/index.html` | desktop shell |
| `web/v6/mobile/index.html` | mobile shell |
| `web/v6/static/js/pages/{route}.js` | desktop page module |
| `web/v6/static/js/pages/{route}.mobile.js` | mobile page module |
| `web/v6/static/js/components.js` | shared renderers (masthead/nav/loading/error) |
| `web/v6/static/js/device.js` | client-side mobile detection + redirect |

---

## 15. กฎเหล็ก (ใช้กับ AI ทุกครั้ง)

1. **อ้าง token ผ่าน `var(--xxx)` เท่านั้น** — ห้าม hardcode hex/px ใน CSS หรือ inline style
   - ถ้า token ไม่พอ → เพิ่มใน `tokens.css` ก่อน + update DESIGN.md
2. **ห้าม component อ้าง primitive (--sage-500 ฯลฯ) ตรง** — ใช้ semantic (--c-positive)
3. **ทุก token ต้องมี dark counterpart** — เพิ่ม `:root` ต้องเพิ่มใน `@media (prefers-color-scheme: dark)` ด้วย
4. **แก้ desktop → ต้อง check mobile.css override** — แยกชั้น ไม่ใช่ responsive single-file
5. **ทุก page route → ต้องมี 2 module** (`{route}.js` desktop + `{route}.mobile.js` mobile)
6. **Card = `var(--r-4)` (14px)** เป็น default — ไม่ใช่ค่ากลางๆ
7. **ตัวเลข/ราคา → ใช้ `.mono` หรือ `tabular-nums` เสมอ** กัน digit shift
8. **ห้ามแตะ Drift candidates (section 12)** ถ้าไม่ได้รับ scope refactor ชัดเจน
9. **เปลี่ยน token แล้วต้อง update ไฟล์นี้ด้วย** — สอง source = drift
10. **เพิ่ม signal tag ใหม่ → ต้อง update section 9** — กัน orphan tag
11. **Fixed element ที่ mobile → ต้องใช้ `env(safe-area-inset-bottom)`** กัน iOS notch
