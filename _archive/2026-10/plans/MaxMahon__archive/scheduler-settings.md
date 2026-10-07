---
project: MaxMahon
created: 2026-04-12
last_updated: 2026-04-12
status: done
---

# Max Mahon — หน้าตั้งค่า Schedule + Pipeline + Filters

> เพิ่มหน้าตั้งค่าให้ปรับ schedule (วัน/เวลา), เลือก pipeline (weekly/discovery), และปรับเกณฑ์คัดกรองหุ้นได้ผ่าน UI โดยไม่ต้องแก้ code

## Phase 1: Config System + Schedule Settings
- [x] สร้าง config system — config.json (default values), load_config()/save_config() helper, GET/POST /api/settings endpoint ใน app.py + แก้ scheduler ให้ใช้ job id + apply_schedule() reschedule จาก config + scheduled_run() อ่าน pipeline action จาก config แทน hardcode
- [x] เพิ่ม tab 'ตั้งค่า' + settings panel ใน UI — HTML: settings-panel (schedule section: วัน dropdown, เวลา input, เปิด/ปิด toggle) + JS: bindSettings(), loadSettings() จาก GET /api/settings, saveSettings() POST /api/settings + CSS: settings panel, form groups, responsive + bindTabs() เพิ่ม settings panel show/hide

### Reference
```python
# server/app.py — current scheduler (hardcoded)
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_run, "cron", day_of_week="sun", hour=9, minute=0)

# new — config-driven scheduler
CONFIG_PATH = PROJECT_DIR / "config.json"
DEFAULT_CONFIG = {
    "schedule": {"enabled": True, "day_of_week": "sun", "hour": 9, "minute": 0},
    "pipeline": {"odd_weeks": "weekly", "even_weeks": "discovery"},
    "filters": {
        "min_roe_avg": 0.15, "min_roe_floor": 0.12, "min_net_margin": 0.10,
        "max_de_non_fin": 1.5, "max_de_financial": 10,
        "min_eps_positive_years": 3, "min_fcf_positive_years": 3,
        "min_market_cap": 5_000_000_000,
    },
}

def load_config():
    if CONFIG_PATH.exists():
        saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        config = {}
        for k in DEFAULT_CONFIG:
            if isinstance(DEFAULT_CONFIG[k], dict):
                config[k] = {**DEFAULT_CONFIG[k], **(saved.get(k) or {})}
            else:
                config[k] = saved.get(k, DEFAULT_CONFIG[k])
        return config
    return dict(DEFAULT_CONFIG)

def apply_schedule(config):
    sched = config["schedule"]
    try:
        scheduler.remove_job("max_pipeline")
    except Exception:
        pass
    if sched["enabled"]:
        scheduler.add_job(scheduled_run, "cron", id="max_pipeline",
            day_of_week=sched["day_of_week"], hour=sched["hour"], minute=sched["minute"])

@app.post("/api/settings")
async def post_settings(request: Request):
    body = await request.json()
    config = load_config()
    for k in body:
        if k in config and isinstance(config[k], dict):
            config[k].update(body[k])
        else:
            config[k] = body[k]
    save_config(config)
    apply_schedule(config)
    return {"status": "ok", "config": config}

@app.get("/api/settings")
async def get_settings():
    return load_config()
```

## Phase 2: Pipeline Toggle + Filter Settings
- [x] เพิ่ม pipeline + filter form ใน settings panel — HTML: pipeline section (dropdown เลือก action สัปดาห์คี่/คู่) + filter section (input: ROE%, Net Margin%, D/E, Market Cap) พร้อม label ภาษาไทย + JS: loadSettings/saveSettings รวม pipeline+filters fields + แสดงค่า default กำกับ
- [x] Backend อ่าน config — scheduled_run() อ่าน config['pipeline'] เลือก action แทน hardcode week logic + screen_stocks.py อ่าน config.json filters แทน HARD_FILTERS constant (fallback เป็น default ถ้าไม่มี config)

### Reference
```python
# server/app.py — scheduled_run() current
week = get_week_of_month()
action = "weekly" if week in (1, 3) else "discovery"

# new — config-driven
config = load_config()
pipeline = config["pipeline"]
week = get_week_of_month()
action = pipeline["odd_weeks"] if week in (1, 3) else pipeline["even_weeks"]

# scripts/screen_stocks.py — current
HARD_FILTERS = {"min_roe_avg": 0.15, ...}

# new — config-aware
DEFAULT_FILTERS = {"min_roe_avg": 0.15, ...}
def load_filters():
    config_path = ROOT / "config.json"
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        return {**DEFAULT_FILTERS, **config.get("filters", {})}
    return dict(DEFAULT_FILTERS)
HARD_FILTERS = load_filters()
```
