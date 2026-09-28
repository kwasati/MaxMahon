---
project: 4-MaxMahon
created: 2026-05-15
last_updated: 2026-05-18
status: archived
---
> **[STALE 2026-05-16]** Design model เปลี่ยนจาก role classification (anchor/supporting/tail/none) เป็น **anchor score เดียว 100 pts + DCA signal แยก** (ตาม chat ตกผลึก 2026-05-16). Plan นี้ stale — ต้อง rewrite หลัง `scoring-formula-discussion.md` finalize `docs/scoring-anchor-spec.md` ก่อน. ห้าม /build plan นี้ตามเนื้อหาเดิม. ดู `maxmahon-index.md` Phase 3.

---


## Target / Goal

### เป้าหมาย
ทำได้: รัน screening pipeline แล้วทุกหุ้นได้ role assignment (anchor/supporting/tail/none) + per-role ranking score + admin แก้ทุก threshold/rule/list/weight ผ่าน /settings UI โดยไม่ต้องแก้ code

### รายละเอียด
- ทาง 3 hybrid: role classification (anchor/supporting/tail/none) + per-role ranking score — แทน single quality score 100 (เดิม 5 pillars 50/25/10/5/10)
- 3 ชั้น config in single config.json: stages (per-stage threshold dict ครอบ Stage 1-6 ~30+ ค่า) + roles (anchor/supporting/tail rule = required_any + required_all + forbidden tag lists) + scoring (anchor/supporting/tail weight formula dict)
- UI hybrid: form (hard filter + score weights) + JSON editor (stage threshold + role rules) + diff default-vs-current + reset button per section
- ห้าม hardcode (CRITICAL): threshold ตัวเลข/role rule/sector list/symbol exception/tag display name + description ทั้งหมดอยู่ใน config — code อ้างอิงผ่าน load helpers เท่านั้น
- Sector lists (STABLE_SECTORS, CYCLICAL_SECTORS, ASSET_HEAVY) + symbol exceptions (STABLE_UTILITY_SYMBOLS, ASSET_HEAVY_EXCEPTIONS) ย้ายเข้า config — โหลดผ่าน new sector_taxonomy.py module
- ที่ยังต้องอยู่ใน code: tag identifier string เท่านั้น (เช่น 'STRONG_MOAT', 'QUALITY_DIVIDEND') — display name + Thai description แยกไป config
- Admin POST /api/settings validation: extend whitelist per-section keys (filters/stages/roles/scoring)
- Admin GET /api/admin/config/defaults: return DEFAULT_CONFIG dict สำหรับ frontend diff display
- quality_score() return shape เปลี่ยน: {role: str, score: int, breakdown: dict, signals: list} แทน {score: int, breakdown: dict, signals: list}
- Default role rules (encoded ใน DEFAULT_ROLE_CONFIG): anchor = required_any(QUALITY_DIVIDEND, STABLE_PAYER) + required_all(STRONG_MOAT, STABLE_BUSINESS, RESILIENT_THROUGH_CRISIS) + forbidden(MOAT_ERODING, DIVIDEND_SHRINKING, MULTIPLE_SELL_TRIGGERS) — derive จาก Stage 1-6 FINAL design ที่ parent plan
- Resume Checkpoint phase บังคับ: review Phase 1 decisions 6 ข้อก่อน implement Phase 1+ ทุกครั้ง (อาร์ทระบุไว้)

### Scope Boundary
**In scope:**
- projects/4-MaxMahon/config.json — expand schema (add stages/roles/scoring top-level sections)
- projects/4-MaxMahon/scripts/screen_stocks.py — refactor quality_score (lines 722-760) + assign_signals (565-632) + valuation_grade (635-719) + add 3 load helpers
- projects/4-MaxMahon/scripts/sector_taxonomy.py (NEW) — load sector lists from config
- projects/4-MaxMahon/scripts/role_classifier.py (NEW) — classify_role(tags) -> str
- projects/4-MaxMahon/scripts/role_scoring.py (NEW) — score_per_role(data, role) -> dict
- projects/4-MaxMahon/server/app.py — extend POST /api/settings validation (lines 988-1020) + add GET /api/admin/config/defaults endpoint
- projects/4-MaxMahon/web/v6/static/js/pages/settings.js + settings.mobile.js — add Score Weights form section + Advanced JSON editor section + diff + reset per section

**Out of scope:**
- Stage 1-6 design (FINAL ที่ parent plan niwes-refactor-v2-design.md — ไม่แก้)
- Section 2.9 Claude Opus prompt redesign — separate plan
- Section 2.10 Dictionary lib + UI — separate plan (จะ integrate กับ tag display ที่ใส่ใน config)
- Phase A pre-impl tasks (A1-A4: data_adapter unit normalize / OCF/NP verify / sector_pe_precompute / _build_aggregates extend) — separate plan ทำก่อน implementation นี้
- Hard filter logic change (keep semantic: PASS/REVIEW/FAIL)
- Tag identifier rename (display name + description แยกแทน)
- Stage 7 (ตัดทิ้ง 2026-05-15 ใน parent plan)

### Non-goals
- ไม่ทำ retroactive migration ของ historic tag — recompute fresh per scan
- ไม่ทำ multi-axis 3 ตัวเลขต่อหุ้น (ทาง 2 ที่ปฏิเสธ) — ใช้ role + 1 score per role แทน
- ไม่ทำ real-time config reload — load on import + restart server เมื่อแก้ config
- ไม่ทำ form input ทุก threshold (~50 fields) — advanced threshold ใช้ JSON editor แทน
- ไม่ลบ 5 pillar score functions เดิม (dividend_score/valuation_score/cash_flow_score/hidden_value_score/track_record_score) ทันที — keep เป็น raw metric extractor ให้ role_scoring re-use; cleanup ทีหลังถ้าไม่ใช้

# Scoring Redesign + Config Refactor (Niwes v2 — Section 2.8)

> Section 2.8 ของ niwes-refactor-v2 — แทน single quality score (100 pts 5 pillars) ด้วย role classification (anchor/supporting/tail/none) + per-role ranking score. ทุก threshold + role rule + score weight + sector list + tag display อยู่ใน config.json (ห้าม hardcode) + admin ปรับผ่าน /settings UI (form + JSON editor hybrid).

## Phase 0: Resume Review (CRITICAL — ก่อน implement)
- [ ] Review Phase 1 decisions 6 ข้อใน spec_scope.details (และตัวเลข default ใน DEFAULT_*_CONFIG ทั้งหมด) กับอาร์ทก่อนเริ่ม implement Phase 1+. Verify (a) scope ครบไม่พลาด, (b) กฎห้าม hardcode apply ทั่วถึงทุก threshold/rule/list/sector/symbol/tag display, (c) UI flow makes sense ตอน user แก้ config จริง (form vs JSON editor mental model ชัด — user รู้ว่าค่าไหนแก้ที่ไหน), (d) Stage 1-6 design ใน parent plan ยัง align กับ default ค่าใน config นี้. — scope: ไม่ implement code ใดๆ ที่ phase นี้ — Acceptance: อาร์ท ack 'review ผ่าน decisions ครบ' หรือ flag gap ที่ต้องแก้ก่อน /build Phase 1

### Reference
Phase 1 decisions to review:

1. ทาง 3 hybrid (role classification + per-role score) — ยืน?
2. 3 ชั้น config (stages + roles + scoring) — ยืน?
3. UI hybrid (form + JSON editor advanced) — ยืน?
4. รวม config.json ไฟล์เดียว — ยืน?
5. ห้าม hardcode (threshold/rule/list/sector/symbol/tag display) — ยืน?
6. Admin /settings 3 section + diff default-vs-current + reset per section — ยืน?

Reference: scoring-redesign-config-refactor.md spec_scope + niwes-refactor-v2-design.md parent

## Phase 1: Config schema + load helpers
- [ ] Expand projects/4-MaxMahon/config.json default schema — เพิ่ม 3 top-level sections: `stages` (per-stage threshold dict ครอบ Stage 1-6 ~30+ ค่า ดู Stage 1-6 FINAL design ที่ parent plan), `roles` (anchor/supporting/tail = {required_any: [], required_all: [], forbidden: []}), `scoring` (anchor/supporting/tail weight formula dict). Keep existing schedule + filters + universe sections (backward compat). — scope: ไม่แก้ existing keys + ไม่ implement load helper (Task 2) + ไม่ implement validation server-side (Phase 5) — Acceptance: config.json file มี 6 top-level keys (schedule/filters/universe/stages/roles/scoring); existing filter keys ยัง work; default value ของ stages section derive จาก Stage 1-6 threshold ที่ parent plan ระบุ (เช่น strong_moat_roe_min=15, strong_moat_consec_years=7, etc.)
- [ ] Add 3 config loader helpers ใน projects/4-MaxMahon/scripts/screen_stocks.py — `load_stage_config()`, `load_role_config()`, `load_scoring_config()`. Pattern: เหมือน existing `load_filters()` (lines 45-54) — merge DEFAULT_* + user config section. เพิ่ม module-level DEFAULT_STAGE_CONFIG / DEFAULT_ROLE_CONFIG / DEFAULT_SCORING_CONFIG dicts (encode Phase 1 defaults). — scope: ไม่ refactor existing load_filters() — Acceptance: `from screen_stocks import load_stage_config, load_role_config, load_scoring_config`; แต่ละ helper return dict; missing config key → fallback DEFAULT_*

### Reference
```python
# current (screen_stocks.py:31-57)
DEFAULT_FILTERS = {
    'min_dividend_yield': 5.0,
    ...
    'min_market_cap': 5_000_000_000,
}

def load_filters() -> dict:
    config_path = ROOT / 'config.json'
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding='utf-8'))
            return {**DEFAULT_FILTERS, **config.get('filters', {})}
        except Exception:
            pass
    return dict(DEFAULT_FILTERS)

HARD_FILTERS = load_filters()

# new — repeat pattern for stages/roles/scoring
DEFAULT_STAGE_CONFIG = {
    'quality_dividend': {'min_yield': 5, 'max_payout': 0.70, 'min_streak': 10},
    'dividend_trap': {'min_yield_trap': 8.0, 'min_payout_trap': 1.0},
    'deep_value': {'max_pe': 8, 'max_pbv': 1.0},
    'strong_moat': {'min_roe': 15, 'min_consec_years': 7},
    'moat_eroding': {'roe_decline_years': 3, 'gm_decline_min_pct': 5},
    'stable_business': {'max_eps_cv': 30},
    'cyclical_business': {'min_eps_cv': 50},
    'resilient_crisis': {'max_dps_drop_pct': -40},
    'valuation_grade': {'boundaries': {'A': 80, 'B': 60, 'C': 40, 'D': 20}, 'labels': {...}},
    'sector_mapping': {
        'stable_sectors': ['Health Care Services', 'Food & Beverage', ...],
        'cyclical_sectors': [...],
        'asset_heavy_industries': [...],
        'stable_utility_symbols': [],
        'asset_heavy_exceptions': ['AOT', 'BTS', 'BEM']
    },
    # ... ~30+ keys ครอบ Stage 1-6
}

DEFAULT_ROLE_CONFIG = {
    'anchor': {
        'required_any': ['QUALITY_DIVIDEND', 'STABLE_PAYER'],
        'required_all': ['STRONG_MOAT', 'STABLE_BUSINESS', 'RESILIENT_THROUGH_CRISIS'],
        'forbidden': ['MOAT_ERODING', 'DIVIDEND_SHRINKING', 'MULTIPLE_SELL_TRIGGERS']
    },
    'supporting': {
        'required_any': ['DPS_RISING', 'DPS_GROWING'],
        'required_all': ['STRONG_MOAT'],  # or MODERATE_MOAT — TBD review
        'forbidden': ['MOAT_ERODING']
    },
    'tail': {
        'required_any': ['HIDDEN_HOLDING', 'DEEP_VALUE', 'ASSET_RICH_PBV_LOW'],
        'required_all': [],
        'forbidden': ['CHRONIC_LOSS']
    }
}

DEFAULT_SCORING_CONFIG = {
    'anchor': {'yield_weight': 10, 'streak_weight': 2, 'moat_weight': 5, 'stability_bonus': 3},
    'supporting': {'dps_growth_weight': 10, 'moat_weight': 3, 'valuation_bonus': 2},
    'tail': {'hidden_depth_weight': 5, 'mos_pct_weight': 2}
}

def load_stage_config() -> dict:
    config_path = ROOT / 'config.json'
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding='utf-8'))
            return _deep_merge(DEFAULT_STAGE_CONFIG, config.get('stages', {}))
        except Exception:
            pass
    return dict(DEFAULT_STAGE_CONFIG)
# load_role_config + load_scoring_config — same pattern
```

Note: ตัวเลข default ทั้งหมดต้อง verify จาก parent plan Stage 1-6 design ก่อน commit. Resume Review Phase 0 จะ catch ค่าที่ misalign.

## Phase 2: Sector taxonomy module
- [ ] Create projects/4-MaxMahon/scripts/sector_taxonomy.py — NEW module load sector mapping lists from config (config.stages.sector_mapping section). Export: `get_stable_sectors() -> set[str]`, `get_cyclical_sectors() -> set[str]`, `get_asset_heavy_industries() -> set[str]`, `get_stable_utility_symbols() -> set[str]`, `get_asset_heavy_exceptions() -> set[str]`. ห้าม hardcode list ใน module — load ผ่าน `_load_mapping()` helper (เรียก config.json ทุกครั้ง หรือ cache module-level). — scope: ไม่แก้ caller ใน screen_stocks.py (Phase 3 task) + ไม่เพิ่ม mapping category อื่น — Acceptance: `import sector_taxonomy; assert get_stable_sectors() == set(default_list)`; แก้ config.stages.sector_mapping.stable_sectors เพิ่ม 'Pharma & Chem' → get_stable_sectors() return ที่มี 'Pharma & Chem'

### Reference
```python
# new — projects/4-MaxMahon/scripts/sector_taxonomy.py
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_SECTOR_MAPPING = {
    'stable_sectors': [
        'Health Care Services', 'Food & Beverage',
        'Personal Products & Pharmaceuticals',
        'Information & Communication Technology',
        'Commerce', 'Banking', 'Finance & Securities', 'Insurance'
    ],
    'cyclical_sectors': [
        'Energy & Utilities', 'Construction Materials',
        'Tourism & Leisure', 'Transportation & Logistics', 'Chemicals'
    ],
    'asset_heavy_industries': [
        'Financials', 'Property & Construction', 'Resources', 'Industrials'
    ],
    'stable_utility_symbols': [],
    'asset_heavy_exceptions': ['AOT', 'BTS', 'BEM']
}

def _load_mapping() -> dict:
    cfg = ROOT / 'config.json'
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding='utf-8'))
            user_map = data.get('stages', {}).get('sector_mapping', {})
            return {**DEFAULT_SECTOR_MAPPING, **user_map}
        except Exception:
            pass
    return dict(DEFAULT_SECTOR_MAPPING)

def get_stable_sectors() -> set[str]:
    return set(_load_mapping()['stable_sectors'])

def get_cyclical_sectors() -> set[str]:
    return set(_load_mapping()['cyclical_sectors'])

def get_asset_heavy_industries() -> set[str]:
    return set(_load_mapping()['asset_heavy_industries'])

def get_stable_utility_symbols() -> set[str]:
    return set(_load_mapping()['stable_utility_symbols'])

def get_asset_heavy_exceptions() -> set[str]:
    return set(_load_mapping()['asset_heavy_exceptions'])
```

## Phase 3: Tag threshold from config
- [ ] Rewrite `assign_signals()` ใน projects/4-MaxMahon/scripts/screen_stocks.py (lines 565-632) — replace ทุก hardcoded threshold ด้วย config lookup ผ่าน `load_stage_config()`. Tag identifier strings (NIWES_5555, NIWES_GROWING, QUALITY_DIVIDEND, DEEP_VALUE, DIVIDEND_TRAP, YIELD_SPIKE_FROM_PRICE_DROP, DATA_WARNING, DATA_INCOMPLETE) คงเดิม. — scope: ไม่เพิ่ม tag identifier ใหม่ (Stage 1-6 design ที่ parent plan กำหนดแล้ว) + ไม่แก้ caller (quality_score) — Acceptance: assign_signals(data, score) return same tag list as before เมื่อ config = default; แก้ config.stages.quality_dividend.min_yield จาก 5 เป็น 7 → QUALITY_DIVIDEND ไม่ติดให้หุ้นที่ dy=6%; แก้ config.stages.dividend_trap.min_yield_trap จาก 8 เป็น 6 → DIVIDEND_TRAP ติดง่ายขึ้น
- [ ] Rewrite `valuation_grade()` ใน projects/4-MaxMahon/scripts/screen_stocks.py (lines 635-719) — replace hardcoded grade boundaries (80/60/40/20), label dict (A-F Thai labels), bonus values (PEG 20/12/4, P/E vs sector 35/21/7, yield vs 5y 30/18/6, 52w 15/9/3) ด้วย config lookup ผ่าน `load_stage_config()['valuation_grade']`. — scope: ไม่แก้ caller signature (keep `(data, sector_medians) -> dict`) + ไม่ลบ OVERPRICED tag logic — Acceptance: valuation_grade(data, sector_medians) return same grade dict as before เมื่อ config = default; แก้ config.stages.valuation_grade.boundaries.A จาก 80 เป็น 70 → หุ้นคะแนน 75 ได้ grade A (เดิม B)

### Reference
```python
# current (screen_stocks.py:609-611 — QUALITY_DIVIDEND hardcoded)
if dy >= 5 and payout is not None and payout < 0.70 and streak >= 10:
    signals.append('QUALITY_DIVIDEND')

# new — read from config
stage_cfg = load_stage_config()
qd = stage_cfg['quality_dividend']  # {'min_yield': 5, 'max_payout': 0.70, 'min_streak': 10}
if dy >= qd['min_yield'] and payout is not None and payout < qd['max_payout'] and streak >= qd['min_streak']:
    signals.append('QUALITY_DIVIDEND')

# current (screen_stocks.py:689-707 — grade boundaries hardcoded)
if score >= 80:
    grade = 'A'
elif score >= 60:
    grade = 'B'
...
labels = {'A': 'ราคาน่าสนใจมาก', 'B': 'ราคาเหมาะสม', ...}

# new — read from config
vg = stage_cfg['valuation_grade']
bounds = vg['boundaries']  # {'A': 80, 'B': 60, 'C': 40, 'D': 20}
if score >= bounds['A']:
    grade = 'A'
elif score >= bounds['B']:
    grade = 'B'
...
labels = vg['labels']  # from config
```

## Phase 4: Role classifier + per-role score
- [ ] Create projects/4-MaxMahon/scripts/role_classifier.py — implement `classify_role(tags: list[str]) -> str` returns one of {'anchor', 'supporting', 'tail', 'none'}. Algorithm: load `load_role_config()` → check role rules in priority order anchor → supporting → tail → none. For each role: pass if (set(required_any) & set(tags)) >= 1 (or empty required_any = always pass) AND set(required_all) <= set(tags) (all required present) AND set(forbidden) & set(tags) == empty (no forbidden). Return first matching role; 'none' if none match. — scope: ไม่เพิ่ม role ใหม่ (anchor/supporting/tail/none พอ) + ไม่ implement explanation field — Acceptance: classify_role(['QUALITY_DIVIDEND','STRONG_MOAT','STABLE_BUSINESS','RESILIENT_THROUGH_CRISIS']) == 'anchor'; classify_role(['MOAT_ERODING','CYCLICAL_BUSINESS']) == 'none'; classify_role(['HIDDEN_HOLDING','DEEP_VALUE']) == 'tail'
- [ ] Create projects/4-MaxMahon/scripts/role_scoring.py — implement `score_per_role(data: dict, role: str) -> dict`. แต่ละ role ใช้ formula คนละสูตร อ่าน weight จาก `load_scoring_config()[role]`. Anchor formula example: `score = dy * w_yield + streak * w_streak + moat_tier_pts * w_moat + stability_bonus`; Supporting + Tail คนละสูตร. Cap score 0-100. Role='none' → return {score: 0, breakdown: {}}. — scope: ไม่ implement raw metric extractor ใหม่ (re-use compute_payout_sustainability/dividend score/etc. จาก existing functions ถ้าจำเป็น) + ไม่ทำ rebalance formula ระหว่าง role — Acceptance: score_per_role(ptt_data, 'anchor') return {score: int 0-100, breakdown: dict}; แก้ config.scoring.anchor.yield_weight จาก 10 เป็น 20 → score เปลี่ยน
- [ ] Refactor `quality_score()` ใน projects/4-MaxMahon/scripts/screen_stocks.py (lines 722-760) — replace 5 pillar score + modifier block ด้วย: (1) call `assign_signals(data, 0)` → tags list, (2) call `classify_role(tags)` → role string, (3) call `score_per_role(data, role)` → role_score dict. Return shape ใหม่: `{role: str, score: int 0-100, breakdown: dict, signals: list, reasons: list}`. Update caller ใน main() pipeline + report_template.py + report.js ที่ใช้ result['score'] / result['breakdown'] ให้รับ shape ใหม่ (เพิ่ม result['role']). — scope: ไม่ลบ 5 pillar score functions เก่า (keep — อาจ re-use เป็น raw metric inside role_scoring); ไม่ refactor scan.py / report_template.py output structure (เพิ่มเฉพาะ role field) — Acceptance: quality_score(ptt_data)['role'] in {'anchor','supporting','tail','none'}; quality_score(cpall_data)['role'] == 'anchor'; quality_score(scc_data)['role'] == 'none' (verified กับ SETSMART 5 หุ้นใน parent plan)

### Reference
```python
# new — projects/4-MaxMahon/scripts/role_classifier.py
from screen_stocks import load_role_config

ROLE_PRIORITY = ['anchor', 'supporting', 'tail']

def classify_role(tags: list[str]) -> str:
    rules = load_role_config()
    tag_set = set(tags)
    for role in ROLE_PRIORITY:
        rule = rules[role]
        required_any = set(rule.get('required_any', []))
        required_all = set(rule.get('required_all', []))
        forbidden = set(rule.get('forbidden', []))
        if forbidden & tag_set:
            continue
        if not required_all.issubset(tag_set):
            continue
        if required_any and not (required_any & tag_set):
            continue
        return role
    return 'none'

# new — projects/4-MaxMahon/scripts/role_scoring.py
from screen_stocks import load_scoring_config

def score_per_role(data: dict, role: str) -> dict:
    if role == 'none':
        return {'score': 0, 'breakdown': {}}
    cfg = load_scoring_config()[role]
    agg = data.get('aggregates', {})
    if role == 'anchor':
        dy = data.get('dividend_yield') or 0
        streak = agg.get('dividend_streak', 0)
        moat_pts = _moat_pts_from_tag(data.get('signals', []))
        score = dy * cfg['yield_weight'] + streak * cfg['streak_weight'] + moat_pts * cfg['moat_weight']
        breakdown = {'dy_pts': dy * cfg['yield_weight'], 'streak_pts': streak * cfg['streak_weight'], 'moat_pts': moat_pts * cfg['moat_weight']}
    elif role == 'supporting':
        # ... cnf['dps_growth_weight'] etc.
        pass
    elif role == 'tail':
        # ... cfg['hidden_depth_weight'] etc.
        pass
    return {'score': max(0, min(100, int(score))), 'breakdown': breakdown}

# refactor quality_score() in screen_stocks.py
from role_classifier import classify_role
from role_scoring import score_per_role

def quality_score(data: dict) -> dict:
    signals = assign_signals(data, 0)  # tags first (Phase 3 result)
    role = classify_role(signals)
    rs = score_per_role(data, role)
    return {
        'role': role,
        'score': rs['score'],
        'breakdown': rs['breakdown'],
        'signals': signals,
        'reasons': []  # backward compat
    }
```

## Phase 5: Server endpoint + UI hybrid
- [ ] Extend projects/4-MaxMahon/server/app.py POST /api/settings (lines 988-1020) — accept additional top-level keys `stages` (dict), `roles` (dict), `scoring` (dict). Add per-section whitelists `_ALLOWED_STAGE_KEYS` (e.g. {'quality_dividend', 'dividend_trap', 'deep_value', 'strong_moat', 'moat_eroding', 'stable_business', 'cyclical_business', 'resilient_crisis', 'valuation_grade', 'sector_mapping', ...}), `_ALLOWED_ROLE_KEYS = {'anchor', 'supporting', 'tail'}`, `_ALLOWED_SCORING_KEYS = {'anchor', 'supporting', 'tail'}`. Validate each section: dict type + key whitelist + role rule structure (required_any/required_all/forbidden lists). — scope: ไม่เปลี่ยน existing filter/universe validation logic — Acceptance: POST {'stages': {'quality_dividend': {'min_yield': 7}}} returns 200; POST {'stages': {'bad_key': 1}} returns 400; POST {'roles': {'anchor': {'required_any': ['QUALITY_DIVIDEND']}}} returns 200; POST {'roles': {'unknown_role': {}}} returns 400
- [ ] Add `GET /api/admin/config/defaults` endpoint ใน projects/4-MaxMahon/server/app.py — return DEFAULT_CONFIG dict โดย import DEFAULT_FILTERS + DEFAULT_STAGE_CONFIG + DEFAULT_ROLE_CONFIG + DEFAULT_SCORING_CONFIG จาก screen_stocks.py. Gate ด้วย `Depends(require_admin)`. — scope: ไม่เพิ่ม PUT/PATCH endpoint + ไม่ implement section-level reset endpoint (frontend ส่ง POST replace section แทน) — Acceptance: GET /api/admin/config/defaults (admin token) returns full default config dict {filters, stages, roles, scoring, universe}; non-admin returns 403
- [ ] Extend projects/4-MaxMahon/web/v6/static/js/pages/settings.js + settings.mobile.js — add 2 new sections: (1) 'Score Weights' form section (3 sub-blocks anchor/supporting/tail แต่ละ block แสดง weight inputs) (2) 'Advanced' section (JSON editor — stages threshold + role rules + sector mapping). Fetch GET /api/admin/config/defaults ตอน mount เพิ่มจาก existing /api/settings + show diff per field (highlight changed key vs default). Add 'Reset to default' button per section (filter / score weights / advanced) — click → replace section with default + dirty=true. Save unified ผ่าน existing POST /api/settings. — scope: ไม่เปลี่ยน existing Auto Scan / Niwes Thresholds / Stock Universe sections + ไม่ implement live preview / type validation per field (server-side validate) — Acceptance: section 'Score Weights' แสดง 3 sub-blocks (anchor/supporting/tail) แต่ละ block มี weight inputs + reset button; section 'Advanced' แสดง JSON editor (textarea หรือ CodeMirror) + validate JSON syntax ก่อน save + diff highlight changed keys vs default; reset button revert section to default + mark dirty

### Reference
```python
# current (server/app.py:988-1020)
_ALLOWED_FILTER_KEYS = {...}  # existing

@app.post('/api/settings')
async def post_settings(request: Request, _: dict = Depends(require_admin)):
    body = await request.json()
    filters = body.get('filters')
    if filters is not None:
        if not isinstance(filters, dict):
            raise HTTPException(400, 'filters must be an object')
        unknown = set(filters.keys()) - _ALLOWED_FILTER_KEYS
        if unknown:
            raise HTTPException(400, f'unknown filter keys: {sorted(unknown)}')
    # ... only filters + universe validation

# new — extend with stages/roles/scoring
_ALLOWED_STAGE_KEYS = {'quality_dividend', 'dividend_trap', 'deep_value', 'strong_moat', 'moat_eroding', 'stable_business', 'cyclical_business', 'resilient_crisis', 'valuation_grade', 'sector_mapping'}
_ALLOWED_ROLE_KEYS = {'anchor', 'supporting', 'tail'}
_ALLOWED_SCORING_KEYS = {'anchor', 'supporting', 'tail'}
_ROLE_RULE_FIELDS = {'required_any', 'required_all', 'forbidden'}

@app.post('/api/settings')
async def post_settings(request: Request, _: dict = Depends(require_admin)):
    body = await request.json()
    for section_name, allowed in [('filters', _ALLOWED_FILTER_KEYS), ('stages', _ALLOWED_STAGE_KEYS), ('roles', _ALLOWED_ROLE_KEYS), ('scoring', _ALLOWED_SCORING_KEYS)]:
        section = body.get(section_name)
        if section is not None:
            if not isinstance(section, dict):
                raise HTTPException(400, f'{section_name} must be an object')
            unknown = set(section.keys()) - allowed
            if unknown:
                raise HTTPException(400, f'unknown {section_name} keys: {sorted(unknown)}')
            # extra validation for roles: rule fields
            if section_name == 'roles':
                for role, rule in section.items():
                    if not isinstance(rule, dict):
                        raise HTTPException(400, f'roles.{role} must be an object')
                    bad_fields = set(rule.keys()) - _ROLE_RULE_FIELDS
                    if bad_fields:
                        raise HTTPException(400, f'roles.{role} bad fields: {sorted(bad_fields)}')
    # ... rest unchanged (deep-merge save)

@app.get('/api/admin/config/defaults')
async def get_default_config(_: dict = Depends(require_admin)):
    from screen_stocks import DEFAULT_FILTERS, DEFAULT_STAGE_CONFIG, DEFAULT_ROLE_CONFIG, DEFAULT_SCORING_CONFIG
    return {
        'filters': DEFAULT_FILTERS,
        'stages': DEFAULT_STAGE_CONFIG,
        'roles': DEFAULT_ROLE_CONFIG,
        'scoring': DEFAULT_SCORING_CONFIG,
        'universe': 'set_only'
    }
```

UI: settings.js ขยายจาก existing _renderShell pattern — เพิ่ม renderScoreWeightsSection() + renderAdvancedSection(). JSON editor ใช้ textarea + JSON.parse() validate ก่อน save (เริ่มต้นง่ายๆ — upgrade Monaco ทีหลังถ้าจำเป็น).
