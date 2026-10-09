"""จัดพอร์ต pillar 1 — ดึงกลับเป้าด้วยเงินสดในพอร์ต (ไม่ขายตัวเกินเป้า)

ใช้: py scripts\\rebalance.py --cash 1300722.11 AMATA=107900@33 BBL=11800@190.5 ... TISCO=15700@127.5
- หุ้นที่ไม่อยู่ใน TARGETS = นอกแผน: ไม่นับฐาน ไม่เติม (แสดงแยก)
- ฐาน = มูลค่าหุ้นในแผน + เงินสด · เงินสดเป้า 5% คือช่องหนึ่ง ไม่ใช่ source
- ตัวต่ำกว่าเป้าได้เติม · ถ้าเงินไม่พอเติมทุกช่อง เกลี่ยตามยอดที่ขาด · ปัดลงทีละ 100 หุ้น (board lot) แล้วเกลี่ยเศษที่เหลือทีละล็อตให้ตัวที่ขาดมากสุด (ไม่เกินเป้า)
"""
import argparse

# เป้า final 2026-05-22 — Niwes 70 (AMATA/BBL/TCAP) + เซียนฮง 25 (TOA/SISB/SECURE/MOSHI) + เงินสด 5
TARGETS = {
    "AMATA": 35.0, "BBL": 22.5, "TCAP": 12.5,
    "TOA": 7.5, "SISB": 7.5, "SECURE": 6.25, "MOSHI": 3.75,
}
CASH_TARGET = 5.0
LOT = 100

# ขาของหุ้นในแผน — ที่เดียวที่บอกว่าตัวไหนอยู่ขาไหน (holdings_watch อ่านจากนี่)
LEGS = {
    "niwes": ["AMATA", "BBL", "TCAP"],
    "hong": ["TOA", "SISB", "SECURE", "MOSHI"],
}

assert abs(sum(TARGETS.values()) + CASH_TARGET - 100) < 1e-9
assert sorted(s for legs in LEGS.values() for s in legs) == sorted(TARGETS)


def parse_holding(s):
    sym, rest = s.split("=")
    vol, price = rest.split("@")
    return sym.upper(), int(vol.replace(",", "")), float(price.replace(",", ""))


def parse_all(items):
    """แปลง SYM=vol@price หลายตัวเป็น dict · ซ้ำ / ราคา <= 0 → ValueError"""
    h, dup = {}, []
    for s, v, p in map(parse_holding, items):
        if s in h and s not in dup:
            dup.append(s)
        if p <= 0:
            raise ValueError(f"ราคา {s} ต้องมากกว่า 0 (ได้ {p})")
        h[s] = (v, p)
    if dup:
        raise ValueError(f"หุ้นซ้ำในอินพุต: {dup}")
    return h


def compute_plan(h, cash):
    """h = {SYM: (vol, price)} · คืน dict แผนซื้อ (หุ้นนอกแผนไม่นับ)

    buy1 = ผลปัดลงรอบแรก · buy = หลังเกลี่ยเศษ · extra = [(SYM, ล็อตที่เพิ่ม)]
    """
    missing = [s for s in TARGETS if s not in h]
    if missing:
        raise ValueError(f"ขาดราคาหุ้นในแผน: {missing} — ใส่ SYM=0@price")
    bad = [s for s in TARGETS if h[s][1] <= 0]
    if bad:
        raise ValueError(f"ราคาต้องมากกว่า 0: {bad}")
    val = {s: h[s][0] * h[s][1] for s in TARGETS}
    base = sum(val.values()) + cash
    if base <= 0:
        raise ValueError("ฐานพอร์ตเป็น 0 — ไม่มีหุ้นในแผนและไม่มีเงินสด")
    gap = {s: max(0.0, base * TARGETS[s] / 100 - val[s]) for s in TARGETS}
    budget = max(0.0, cash - base * CASH_TARGET / 100)
    scale = min(1.0, budget / sum(gap.values())) if sum(gap.values()) else 0.0
    buy1 = {s: int(gap[s] * scale / h[s][1] // LOT * LOT) for s in TARGETS}
    buy = dict(buy1)
    left_budget = budget - sum(buy[s] * h[s][1] for s in TARGETS)
    extra = {}
    while True:
        best, best_rem = None, 0.0
        for s in TARGETS:  # เสมอ → ตัวแรกใน TARGETS (> เข้มงวด)
            lot_cost = LOT * h[s][1]
            rem = gap[s] - buy[s] * h[s][1]
            if lot_cost <= left_budget and lot_cost <= rem and rem > best_rem:
                best, best_rem = s, rem
        if best is None:
            break
        buy[best] += LOT
        left_budget -= LOT * h[best][1]
        extra[best] = extra.get(best, 0) + 1
    spent = sum(buy[s] * h[s][1] for s in TARGETS)
    return {"val": val, "base": base, "gap": gap, "budget": budget, "scale": scale,
            "buy1": buy1, "buy": buy, "extra": list(extra.items()),
            "spent": spent, "left": cash - spent, "left1": cash - sum(buy1[s] * h[s][1] for s in TARGETS)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cash", type=float, required=True)
    ap.add_argument("holdings", nargs="+", help="SYM=vol@price")
    a = ap.parse_args()

    try:
        h = parse_all(a.holdings)
        pl = compute_plan(h, a.cash)
    except ValueError as e:
        raise SystemExit(str(e))
    val, base, budget, buy = pl["val"], pl["base"], pl["budget"], pl["buy"]

    print(f"ฐานในแผน {base:,.0f} | เงินใช้ได้ (หลังกันเงินสด {CASH_TARGET}%) {budget:,.0f}")
    if budget == 0:
        print(f"เงินใช้ได้ = 0 เพราะเงินสด {a.cash:,.0f} ({a.cash/base*100:.2f}%) ไม่เกินช่องเงินสดเป้า {CASH_TARGET}% ({base*CASH_TARGET/100:,.0f}) — ไม่ซื้อ")
    print(f"{'หุ้น':8}{'ตอนนี้%':>9}{'เป้า%':>7}{'ซื้อ(หุ้น)':>11}{'ใช้เงิน':>12}{'หลังซื้อ%':>10}")
    for s in TARGETS:
        cost = buy[s] * h[s][1]
        print(f"{s:8}{val[s]/base*100:9.2f}{TARGETS[s]:7.2f}{buy[s]:11,}{cost:12,.0f}{(val[s]+cost)/base*100:10.2f}")
    print(f"{'เงินสด':8}{a.cash/base*100:9.2f}{CASH_TARGET:7.2f}{'':11}{-pl['spent']:12,.0f}{pl['left']/base*100:10.2f}")
    if pl["extra"]:
        txt = " · ".join(f"{s} +{n} ล็อต" for s, n in pl["extra"])
        print(f"เกลี่ยเศษจากการปัดลง: {txt} (เงินเหลือค้าง {pl['left1']:,.0f} → {pl['left']:,.0f})")

    off = {s: v for s, v in h.items() if s not in TARGETS}
    if off:
        total = base + sum(v * p for v, p in off.values())
        print(f"\nนอกแผน (ไม่เติม) — พอร์ตรวม {total:,.0f}")
        for s, (v, p) in off.items():
            print(f"  {s:8}{v:>10,} @ {p:<8} = {v*p:12,.0f} ({v*p/total*100:.1f}%)")


if __name__ == "__main__":
    main()
