"""จัดพอร์ต pillar 1 — ดึงกลับเป้าด้วยเงินสดในพอร์ต (ไม่ขายตัวเกินเป้า)

ใช้: py scripts\\rebalance.py --cash 1300722.11 AMATA=107900@33 BBL=11800@190.5 ... TISCO=15700@127.5
- หุ้นที่ไม่อยู่ใน TARGETS = นอกแผน: ไม่นับฐาน ไม่เติม (แสดงแยก)
- ฐาน = มูลค่าหุ้นในแผน + เงินสด · เงินสดเป้า 5% คือช่องหนึ่ง ไม่ใช่ source
- ตัวต่ำกว่าเป้าได้เติม · ถ้าเงินไม่พอเติมทุกช่อง เกลี่ยตามยอดที่ขาด · ปัดลงทีละ 100 หุ้น (board lot)
"""
import argparse

# เป้า final 2026-05-22 — Niwes 70 (AMATA/BBL/TCAP) + เซียนฮง 25 (TOA/SISB/SECURE/MOSHI) + เงินสด 5
TARGETS = {
    "AMATA": 35.0, "BBL": 22.5, "TCAP": 12.5,
    "TOA": 7.5, "SISB": 7.5, "SECURE": 6.25, "MOSHI": 3.75,
}
CASH_TARGET = 5.0
LOT = 100

assert abs(sum(TARGETS.values()) + CASH_TARGET - 100) < 1e-9


def parse_holding(s):
    sym, rest = s.split("=")
    vol, price = rest.split("@")
    return sym.upper(), int(vol.replace(",", "")), float(price.replace(",", ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cash", type=float, required=True)
    ap.add_argument("holdings", nargs="+", help="SYM=vol@price")
    a = ap.parse_args()

    h = {s: (v, p) for s, v, p in map(parse_holding, a.holdings)}
    missing = [s for s in TARGETS if s not in h]
    if missing:
        raise SystemExit(f"ขาดราคาหุ้นในแผน: {missing} — ใส่ SYM=0@price")

    val = {s: h[s][0] * h[s][1] for s in TARGETS}
    base = sum(val.values()) + a.cash
    gap = {s: max(0.0, base * TARGETS[s] / 100 - val[s]) for s in TARGETS}
    budget = max(0.0, a.cash - base * CASH_TARGET / 100)
    scale = min(1.0, budget / sum(gap.values())) if sum(gap.values()) else 0.0

    print(f"ฐานในแผน {base:,.0f} | เงินใช้ได้ (หลังกันเงินสด {CASH_TARGET}%) {budget:,.0f}")
    print(f"{'หุ้น':8}{'ตอนนี้%':>9}{'เป้า%':>7}{'ซื้อ(หุ้น)':>11}{'ใช้เงิน':>12}{'หลังซื้อ%':>10}")
    spent = 0.0
    for s in TARGETS:
        price = h[s][1]
        buy = int(gap[s] * scale / price // LOT * LOT)
        cost = buy * price
        spent += cost
        print(f"{s:8}{val[s]/base*100:9.2f}{TARGETS[s]:7.2f}{buy:11,}{cost:12,.0f}{(val[s]+cost)/base*100:10.2f}")
    left = a.cash - spent
    print(f"{'เงินสด':8}{a.cash/base*100:9.2f}{CASH_TARGET:7.2f}{'':11}{-spent:12,.0f}{left/base*100:10.2f}")

    off = {s: v for s, v in h.items() if s not in TARGETS}
    if off:
        total = base + sum(v * p for v, p in off.values())
        print(f"\nนอกแผน (ไม่เติม) — พอร์ตรวม {total:,.0f}")
        for s, (v, p) in off.items():
            print(f"  {s:8}{v:>10,} @ {p:<8} = {v*p:12,.0f} ({v*p/total*100:.1f}%)")


if __name__ == "__main__":
    main()
