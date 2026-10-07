---
project: 4-MaxMahon
created: 2026-06-24
last_updated: 2026-06-24
status: done
---

## Target / Goal

### เป้าหมาย
ทำได้: GET /api/portfolio/state?pf=A|B|C คืน state ของพอร์ตนั้น, GET /api/portfolios คืน list 3 พอร์ต {id,name}, PUT /api/portfolio/{id}/name เปลี่ยนชื่อได้, ดึงราคา 1 ครั้งครอบ symbol ทุกพอร์ต, ข้อมูลพอร์ตเดิมไม่หาย

### รายละเอียด
- portfolio_state.py: ทุก function (load/save/build_state/rebalance_topup) รับ param portfolio_id='A' (default A) คำนวณ path = DATA_DIR/'portfolios'/f'{id}.json'
- valid id = A/B/C เท่านั้น (reject อื่น = 400/ValueError)
- build_state เพิ่ม key 'price_as_of' = ISO ของ newest mtime ใน data/price_cache (None ถ้าว่าง)
- migration script: portfolio.json -> portfolios/A.json (เพิ่ม name='พอร์ตหลัก') + archive ต้นฉบับ -> data/_archive/, seed B.json/C.json (copy targets+meta จาก A, holdings={} cash=0, off_plan={}, name='พอร์ต 2'/'พอร์ต 3'), idempotent (ไม่ทับถ้ามีแล้ว)
- endpoints 4 ตัวรับ query pf: str='A' ส่งต่อ portfolio_id; PUT holdings ใช้ load+save(pf); topup ส่ง pf เข้า build_state
- เพิ่ม GET /api/portfolios (list [{id,name}] อ่าน name จากแต่ละไฟล์) + PUT /api/portfolio/{pf}/name body {name:str} (validate id, trim, save)
- daily_price_refresh _load_symbols(): loop data/portfolios/*.json แทน portfolio.json เดียว
- auth เดิม: state/holdings/topup/lh-signals/portfolios/rename = Depends(get_current_user)

### Scope Boundary
**In scope:**
- scripts/portfolio_state.py
- server/app.py (4 endpoints + 2 ใหม่)
- scripts/daily_price_refresh.py _load_symbols()
- scripts/migrate_portfolio_to_separate.py (ใหม่)
- data/portfolios/ (ใหม่)

**Out of scope:**
- frontend ทั้งหมด
- scan pipeline
- UI

### Non-goals
- ไม่เปลี่ยน schema ภายในพอร์ต (targets/holdings/meta โครงเดิม) — แค่เพิ่ม field name
- ไม่ทำ endpoint เพิ่ม/ลบพอร์ต

### Skill Flow
- /build -> /qc -> /done

### Stop Conditions
- schema portfolio.json ต่างจาก reference
- endpoint signature ต่างจาก reference
- ไม่ชัดว่า id ใช้ A/B/C หรือ slug อื่น

# Multi-Portfolio Backend — data แยกไฟล์ + api รับ portfolio_id + price รวมพอร์ต

> Part 1 of 2 — Backend | Index: multi-portfolio-index
> Depends on: none
> Parallel-safe with: none (frontend รอ backend นี้ merge ก่อน)

## Phase 1: Migration + data/portfolios/
- [x] Pre-build Review: อ่าน plan ทั้งไฟล์ + อ่าน scripts/portfolio_state.py, scripts/daily_price_refresh.py, scripts/migrate_to_per_user.py, data/portfolio.json จริงก่อนแก้; ตรวจ path/schema/line ตรง reference ไหม; สงสัย/ไม่พอ/ขัดกัน = หยุดถาม; ชัด = ตอบ plan clear แล้วเริ่ม task ถัดไป
- [x] สร้าง scripts/migrate_portfolio_to_separate.py ตาม pattern scripts/migrate_to_per_user.py — อ่าน data/portfolio.json (ถ้ามี) -> เขียน data/portfolios/A.json เพิ่ม key name='พอร์ตหลัก' -> archive ต้นฉบับไป data/_archive/portfolio.legacy.json (rotate ถ้ามีแล้ว) -> seed B.json/C.json: copy targets+meta จาก A, ตั้ง holdings={}, cash=0, off_plan={}, lh_triggers={}, name='พอร์ต 2'/'พอร์ต 3' — idempotent: ถ้า portfolios/{id}.json มีแล้วข้ามไฟล์นั้น (ไม่ทับ). scope: ไม่แตะ portfolio_state.py. Acceptance: รัน py scripts/migrate_portfolio_to_separate.py -> มี data/portfolios/{A,B,C}.json, A.json มี holdings เดิมครบ + name, รันซ้ำไม่ error ไม่ทับ

### Reference
# pattern อ้างอิง: scripts/migrate_to_per_user.py (validate JSON -> write ถ้ายังไม่มี -> archive + rotate)
# data/portfolio.json keys: targets{sym:pct}, holdings{sym:{shares,avg_cost}}, cash:float,
#   off_plan{sym:{shares,avg_cost,mode}}, lh_triggers{sell_zone,support}, meta{sym:{...}}, updated_at
# A.json = portfolio.json เดิม + name; B/C = targets+meta copy, holdings/off_plan/lh_triggers ว่าง, cash 0

## Phase 2: portfolio_state.py รับ portfolio_id + price_as_of
- [x] แก้ scripts/portfolio_state.py: เพิ่ม helper _portfolio_path(portfolio_id='A') -> DATA_DIR/'portfolios'/f'{id}.json' (validate id in {'A','B','C'} else ValueError); ให้ load_portfolio/save_portfolio รับ portfolio_id='A' ใช้ _portfolio_path แทน PORTFOLIO_FILE hardcode; build_state รับ portfolio_id='A' ส่งเข้า load_portfolio; rebalance_topup รับ portfolio_id='A' ส่งเข้า load_portfolio. scope: ไม่แตะ read_price (อ่าน cache เฉยๆ). Acceptance: build_state('A') คืนพอร์ตหลักเดิม, build_state('B') คืนพอร์ต 2 (holdings ว่าง), id อื่น raise ValueError
- [x] แก้ build_state ใน scripts/portfolio_state.py: เพิ่ม key 'price_as_of' ใน dict ที่ return = ISO string ของไฟล์ใน data/price_cache ที่ mtime ใหม่สุด (None ถ้าโฟลเดอร์ว่าง). Acceptance: build_state()['price_as_of'] เป็น ISO ของ price_cache ล่าสุด หรือ None

### Reference
# current (scripts/portfolio_state.py:36-38, 48, 62, 133-155, 305)
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
def load_portfolio() -> dict: ...  # อ่าน PORTFOLIO_FILE
def save_portfolio(data: dict) -> dict: ...  # เขียน PORTFOLIO_FILE atomic + updated_at
def build_state() -> dict:
    p = load_portfolio()  # line 155
def rebalance_topup(state, new_money) -> list[dict]:
    p = load_portfolio()  # line 305

# new
VALID_PF = {'A', 'B', 'C'}
def _portfolio_path(portfolio_id: str = 'A') -> Path:
    if portfolio_id not in VALID_PF: raise ValueError(f'bad portfolio id: {portfolio_id}')
    return DATA_DIR / 'portfolios' / f'{portfolio_id}.json'
def load_portfolio(portfolio_id: str = 'A') -> dict: ...  # ใช้ _portfolio_path
def save_portfolio(data: dict, portfolio_id: str = 'A') -> dict: ...
def build_state(portfolio_id: str = 'A') -> dict:
    p = load_portfolio(portfolio_id)
    # ...เพิ่มท้าย return dict: 'price_as_of': <newest mtime ISO ใน data/price_cache or None>
def rebalance_topup(state, new_money, portfolio_id: str = 'A') -> list[dict]:
    p = load_portfolio(portfolio_id)

## Phase 3: endpoints รับ ?pf= + list + rename
- [x] แก้ 4 endpoints ใน server/app.py (state ~3013, holdings ~3025, topup ~3050, lh-signals ~3061): เพิ่ม query param pf: str='A'; state->build_state(pf); holdings->load_portfolio(pf)+save_portfolio(data,pf)+build_state(pf); topup->build_state(pf) แล้ว rebalance_topup(state,new_money,pf); lh-signals->load_portfolio(pf). scope: ไม่เปลี่ยน auth (get_current_user เดิม). Acceptance: GET /api/portfolio/state?pf=B คืนพอร์ต 2, ไม่ส่ง pf = พอร์ต A เดิม (backward compat)
- [x] เพิ่ม 2 endpoint ใน server/app.py: GET /api/portfolios -> list [{id,name}] อ่าน name จาก portfolios/{A,B,C}.json (Depends get_current_user); PUT /api/portfolio/{pf}/name body {name:str} -> validate pf in A/B/C, load_portfolio(pf), set data['name']=name.strip(), save_portfolio(data,pf), return {id,name} (Depends get_current_user). Acceptance: GET /api/portfolios คืน 3 รายการ; PUT /api/portfolio/B/name {name:'เมีย'} -> portfolios/B.json name='เมีย'

### Reference
# current (server/app.py:3013-3123)
@app.get('/api/portfolio/state')
async def get_portfolio_state(user=Depends(get_current_user)): return build_state()
@app.put('/api/portfolio/holdings')
async def update_portfolio_holdings(body: PortfolioHoldingsUpdate, user=Depends(get_current_user)):
    data = load_portfolio(); ...; save_portfolio(data); return build_state()
@app.post('/api/portfolio/topup')
async def portfolio_topup(body: PortfolioTopup, user=Depends(get_current_user)):
    state = build_state(); allocation = rebalance_topup(state, body.new_money)
@app.get('/api/portfolio/lh-signals')
async def get_lh_signals(user=Depends(get_current_user)):
    p = load_portfolio(); ...

# new — เพิ่ม pf param (FastAPI: pf: str = 'A' ใน signature = query param)
async def get_portfolio_state(pf: str = 'A', user=Depends(get_current_user)): return build_state(pf)
# GET /api/portfolios + PUT /api/portfolio/{pf}/name ใหม่ (ใช้ load/save_portfolio(pf))

## Phase 4: price refresh รวมทุกพอร์ต
- [x] แก้ scripts/daily_price_refresh.py _load_symbols() (บรรทัด ~71-82): เปลี่ยนจากอ่าน data/portfolio.json เดียว เป็น loop ทุกไฟล์ใน data/portfolios/*.json รวม symbol จาก targets+holdings+off_plan ของทุกพอร์ต (dedupe ด้วย set เดิม). scope: ไม่แตะส่วน watchlist/screener ใน function เดียวกัน. Acceptance: _load_symbols() คืน symbol รวมจากทั้ง 3 พอร์ต (หุ้นซ้ำนับครั้งเดียว); ถ้าไม่มีโฟลเดอร์ portfolios ไม่ crash

### Reference
# current (scripts/daily_price_refresh.py:71-82)
try:
    pf = json.loads((DATA_DIR / 'portfolio.json').read_text(encoding='utf-8'))
    pf_syms = set(pf.get('targets',{})) | set(pf.get('holdings',{})) | set(pf.get('off_plan',{}))
    for sym in pf_syms:
        if sym and sym != 'cash': symbols.add(sym if sym.endswith('.BK') else f'{sym}.BK')
except (OSError, json.JSONDecodeError) as e: logger.warning(...)

# new — loop data/portfolios/*.json (กัน crash ถ้าโฟลเดอร์ไม่มี/ไฟล์พัง per-file)
pf_dir = DATA_DIR / 'portfolios'
if pf_dir.exists():
    for pf_path in pf_dir.glob('*.json'):
        try:
            pf = json.loads(pf_path.read_text(encoding='utf-8'))
            pf_syms = set(pf.get('targets',{})) | set(pf.get('holdings',{})) | set(pf.get('off_plan',{}))
            for sym in pf_syms:
                if sym and sym != 'cash': symbols.add(sym if sym.endswith('.BK') else f'{sym}.BK')
        except (OSError, json.JSONDecodeError) as e: logger.warning(f'could not read {pf_path.name}: {e}')
