"""เทสต์ rebalance.py — ไม่ยิงเน็ต · ตัวเลขคิดมือจาก review-portfolio-misc.md ข้อ 1"""
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import rebalance as rb  # noqa: E402

# snapshot 2026-07-20 (vol, price)
SNAP = {
    "AMATA": (31400, 27.5), "BBL": (3100, 202.0), "TCAP": (4700, 71.5),
    "TOA": (13700, 15.7), "SISB": (18400, 10.3), "SECURE": (12100, 14.2),
    "MOSHI": (2500, 38.75),
}


def zero_buys(**kw):
    d = {s: 0 for s in rb.TARGETS}
    d.update(kw)
    return d


def test_case_a_cash_enough_for_all():
    pl = rb.compute_plan(SNAP, 1_000_000)
    assert round(pl["base"]) == 3_499_055 and round(pl["budget"]) == 825_047
    # assert: ผลรอบแรกตรงที่คิดมือ (ก่อนเกลี่ยเศษ)
    assert pl["buy1"] == dict(AMATA=13100, BBL=700, TCAP=1400, TOA=3000, SISB=7000, SECURE=3300, MOSHI=800)
    assert round(pl["left1"]) == 201_190


def test_case_b_short_with_overweight():
    pl = rb.compute_plan(SNAP, 259_217)
    assert round(pl["base"]) == 2_758_272 and round(pl["scale"], 4) == 0.8978
    assert pl["buy1"] == zero_buys(AMATA=3300, TCAP=100, SISB=1500, MOSHI=100)
    assert round(pl["left1"]) == 141_992


def test_case_c2_all_under_target():
    pl = rb.compute_plan(SNAP, 400_000)
    assert pl["scale"] == 1.0
    assert pl["buy1"] == dict(AMATA=5400, BBL=100, TCAP=300, TOA=100, SISB=2700, SECURE=600, MOSHI=300)


def test_case_d_cash_below_5pct():
    pl = rb.compute_plan(SNAP, 109_217)
    assert pl["budget"] == 0 and pl["buy"] == zero_buys() and pl["extra"] == []


def test_case_e_offplan_ignored_in_base():
    h = dict(SNAP, TISCO=(18600, 127.0))
    pl = rb.compute_plan(h, 109_217)
    assert round(pl["base"]) == 2_608_272 and pl["buy"] == zero_buys()


def test_extra_lots_case_b():
    # assert: เกลี่ยเศษกรณี ข+ค ได้ AMATA +1 ล็อต SISB +1 ล็อต เงินเหลือ 141,992 → 138,212
    pl = rb.compute_plan(SNAP, 259_217)
    assert pl["extra"] == [("AMATA", 1), ("SISB", 1)]
    assert pl["buy"]["AMATA"] == 3400 and pl["buy"]["SISB"] == 1600
    assert round(pl["left"]) == 138_212


def test_no_extra_when_lot_exceeds_gap():
    # assert: กรณี ก เศษของ BBL (19,687) < 1 ล็อต (20,200) → ไม่เกลี่ย (R2 ไม่ซื้อจนเกินเป้า)
    pl = rb.compute_plan(SNAP, 1_000_000)
    assert pl["extra"] == [] and pl["buy"] == pl["buy1"]


def test_duplicate_stops():
    with pytest.raises(ValueError, match="AMATA"):
        rb.parse_all(["AMATA=100@10", "BBL=1@1", "AMATA=200@10"])


def test_zero_price_stops():
    with pytest.raises(ValueError, match="ราคา"):
        rb.parse_all(["AMATA=100@0"])
    h = dict(SNAP, BBL=(3100, 0.0))
    with pytest.raises(ValueError, match="BBL"):
        rb.compute_plan(h, 100_000)


def test_missing_and_empty_base_stop():
    with pytest.raises(ValueError, match="ขาด"):
        rb.compute_plan({"AMATA": (1, 1.0)}, 1000)
    with pytest.raises(ValueError, match="ฐาน"):
        rb.compute_plan({s: (0, 10.0) for s in rb.TARGETS}, 0)


def test_legs_cover_targets_exactly():
    members = [s for legs in rb.LEGS.values() for s in legs]
    assert sorted(members) == sorted(rb.TARGETS) and len(members) == len(set(members))
    assert rb.LEGS["niwes"] == ["AMATA", "BBL", "TCAP"]


def test_random_invariants():
    rng = random.Random(20261009)
    for _ in range(250):
        h = {s: (rng.randint(0, 40000), round(rng.uniform(5, 250), 2)) for s in rb.TARGETS}
        cash = rng.uniform(10_000, 2_000_000)
        pl = rb.compute_plan(h, cash)
        price = {s: h[s][1] for s in rb.TARGETS}
        spent = sum(pl["buy"][s] * price[s] for s in rb.TARGETS)
        # ไม่ใช้เงินเกินเงินใช้ได้
        assert spent <= pl["budget"] + 1e-6
        left_budget = pl["budget"] - spent
        for s in rb.TARGETS:
            # ทวีคูณของ 100
            assert pl["buy"][s] % rb.LOT == 0 and pl["buy"][s] >= pl["buy1"][s]
            # ไม่ซื้อจนมูลค่าเกินเป้า (ถ้าซื้อเพิ่มจากรอบแรก)
            if pl["buy"][s] > pl["buy1"][s]:
                assert pl["buy"][s] * price[s] <= pl["gap"][s] + 1e-6
            # จบแล้วไม่เหลือตัวที่เข้าเงื่อนไขทั้ง 2 ข้อ
            lot = rb.LOT * price[s]
            rem = pl["gap"][s] - pl["buy"][s] * price[s]
            assert not (lot <= left_budget and lot <= rem), s
