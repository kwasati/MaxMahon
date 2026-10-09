"""set_official_adapter: เรียกจากหลายเธรดต้องไม่ล้ม (ไม่ยิงเน็ต — browser ปลอม)."""
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import set_official_adapter as soa  # noqa: E402


class _Resp:
    status = 200

    def body(self):
        return b'[{"caType":"XD","dividendType":"Cash Dividend","xdate":"2024-05-01","endOperation":"2023-12-31","dividend":1.5}]'


class _Request:
    def __init__(self, owner):
        self.owner = owner

    def get(self, url, headers=None):
        # เหมือน playwright sync: เรียกจากเธรดอื่นที่ไม่ใช่เธรดที่สร้างแล้วพัง
        if threading.get_ident() != self.owner:
            raise RuntimeError('greenlet.error: Cannot switch to a different thread')
        return _Resp()


class _Ctx:
    def __init__(self):
        self.request = _Request(threading.get_ident())


def test_fetch_dividends_from_five_threads(monkeypatch):
    soa._close_browser()
    monkeypatch.setattr(soa, '_get_browser_context', _fake_ctx_factory())
    with ThreadPoolExecutor(max_workers=5) as ex:
        results = list(ex.map(soa.fetch_dividends, [f'S{i}' for i in range(20)]))
    assert all(len(r) == 1 and r[0]['dps'] == 1.5 for r in results)
    soa._close_browser()


def _fake_ctx_factory():
    holder = {}

    def get():
        if 'ctx' not in holder:
            holder['ctx'] = _Ctx()
        return holder['ctx']
    return get
