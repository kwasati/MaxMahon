/* ==========================================================
   MAX MAHON v6 — Portfolio Home v2 MINIMAL (Desktop)  — route "/"
   เว็บพอร์ตจริง (pillar 1 ปันผล) — 2 งานชัดๆ บนหน้าเดียว:
     (1) กรอกจำนวนหุ้น inline ในตาราง -> ปุ่มบันทึก PUT holdings ทีเดียว
     (2) กรอกเงินรอบนี้ -> คำนวณแผนซื้อ (ดึงกลับเป้า)
   ของรอง (นอกแผน + แผนเต็ม) พับเก็บล่างสุดด้วย <details>.
   Layout source of truth: .claude/artifacts/maxmahon-portfolio-mockup-v2-minimal.html
   Live data:
     GET  /api/portfolio/state       -> total_value + positions[] + off_plan[] + cash
     GET  /api/portfolio/lh-signals  -> LH sell/support signals
     POST /api/portfolio/topup       -> pull-back-to-target calculator
     PUT  /api/portfolio/holdings    -> save shares/avg_cost (all) + cash
   All markup scoped under .pf-home (CSS in components.css + mobile.css).
   ========================================================== */

let _state = null;
const _REPORT_BASE = '/report/';

export function mount(root) {
  root.classList.add('pf-home');
  root.innerHTML = _renderShell();
  _bindEvents(root);
  _load(root);
}

/* ---------- shell (static scaffold; tables filled by _load) ---------- */
function _renderShell() {
  return (
    '<div class="pf-wrap">' +

      '<div class="pf-total">' +
        '<span class="lbl">มูลค่าพอร์ต</span>' +
        '<span class="val mono" id="ph-total">—</span>' +
      '</div>' +

      /* ====== งานที่ 1: พอร์ตของกู (กรอกหุ้น inline) ====== */
      '<div class="pf-card">' +
        '<div class="pf-card-h">' +
          '<h2>พอร์ตของกู</h2>' +
          '<span class="hint">กรอกจำนวนหุ้นที่ถือในช่อง แล้วกดบันทึก · แท่ง = สัดส่วนจริง ขีด = เป้า</span>' +
        '</div>' +
        '<div class="pf-table-wrap"><table class="pf-table">' +
          '<thead><tr><th>หุ้น</th><th>จำนวนหุ้น</th><th>ราคา</th><th>มูลค่า</th><th>สัดส่วน จริง / เป้า</th></tr></thead>' +
          '<tbody id="ph-rows"><tr><td colspan="5" style="text-align:center;color:var(--fg-dim)">โหลดพอร์ต&hellip;</td></tr></tbody>' +
        '</table></div>' +
        '<div class="pf-card-f">' +
          '<span class="note">แก้ตัวเลขในช่องแล้วกดบันทึก · เงินสดกรอกเป็นบาท</span>' +
          '<button class="pf-btn" id="ph-save" type="button">บันทึกพอร์ต</button>' +
        '</div>' +
      '</div>' +

      /* ====== งานที่ 2: เติมเงินรอบนี้ ====== */
      '<div class="pf-card">' +
        '<div class="pf-card-h">' +
          '<h2>มีเงินมาเพิ่ม</h2>' +
          '<span class="hint">เติมเฉพาะตัวที่ขาดเป้า ดึงพอร์ตกลับสัดส่วน · ตัวเกินไม่ต้องซื้อ</span>' +
        '</div>' +
        '<div class="topup-in">' +
          '<input class="mono" id="ph-calc-input" inputmode="numeric" value="100,000">' +
          '<span class="cur">บาท</span>' +
          '<button class="pf-btn" id="ph-calc-btn" type="button" style="margin-left:auto">คำนวณ &rarr;</button>' +
        '</div>' +
        '<div class="pf-table-wrap"><table class="pf-table">' +
          '<thead><tr><th>ซื้อเพิ่ม</th><th>สถานะ</th><th>ราคา</th><th>จำนวนหุ้น</th><th>ลงเงิน</th></tr></thead>' +
          '<tbody class="buyrow" id="ph-calc-body"><tr><td colspan="5" style="text-align:center;color:var(--fg-dim)">กดคำนวณเพื่อดูแผนซื้อ</td></tr></tbody>' +
        '</table></div>' +
      '</div>' +

      /* ====== ของรอง: ย่อเก็บล่างสุด ====== */
      '<div class="pf-minor">' +
        '<details id="ph-offplan-det">' +
          '<summary><span id="ph-offplan-sum">นอกแผน</span> <span class="chev">กดดู &#9662;</span></summary>' +
          '<div class="det-body" id="ph-offplan"></div>' +
        '</details>' +
        '<details>' +
          '<summary>แผนการลงทุน — Niwes 70 · เซียนฮง 25 · เงินสด 5 <span class="chev">กดดู &#9662;</span></summary>' +
          '<div class="det-body">' +
            '<p class="det-text">' +
              'ปันผล + รายได้ใหม่ รวมกองกลางก้อนเดียว เติมเฉพาะตัวขาดเป้า · ไม่ cut loss · ' +
              'ไม่ซื้อเพิ่มตามราคา · เงินสด 5% ช้อนตอนหุ้นตก &ge;20% ทั้งที่ thesis ยังอยู่ · ' +
              'กดที่ชื่อหุ้นแต่ละตัวดูเหตุผลเต็มได้' +
            '</p>' +
          '</div>' +
        '</details>' +
      '</div>' +

      '<div class="pf-foot" id="ph-foot">ราคาอัปเดตจาก SETSMART</div>' +
    '</div>'
  );
}

/* ---------- load + render ---------- */
async function _load(root) {
  const rowsHost = root.querySelector('#ph-rows');
  try {
    const state = await window.MMApi.get('/api/portfolio/state');
    _state = state;
    _renderTotal(root, state);
    _renderRows(root, state);
    _renderOffPlan(root, state);
    _renderFoot(root, state);
  } catch (e) {
    if (rowsHost) {
      rowsHost.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--c-negative)">' +
        'โหลดพอร์ตไม่สำเร็จ: ' + window.MMUtils.escapeHtml((e && e.message) || String(e)) + '</td></tr>';
    }
  }
}

function _renderTotal(root, state) {
  const el = root.querySelector('#ph-total');
  if (el) el.textContent = window.MMUtils.fmtNum(state.total_value || 0, 0);
}

function _renderFoot(root, state) {
  const el = root.querySelector('#ph-foot');
  if (!el) return;
  let txt = 'ราคาอัปเดตจาก SETSMART';
  if (state.updated_at) {
    const d = new Date(state.updated_at);
    if (!isNaN(d.getTime())) {
      txt += ' · บันทึกล่าสุด ' + d.toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' });
    }
  }
  el.textContent = txt;
}

/* group dot class from position.group */
function _groupDot(group) {
  if (group === 'niwes') return 'niwes';
  if (group === 'hong') return 'hong';
  return 'niwes';  // default in-plan symbols use the niwes (green) dot
}

/* one allocation cell (badge + now/target + bar + mark) */
function _allocCell(pct, target, status) {
  // status ∈ ok / over / deficit  → badge under / over / ok
  let st, fillCls, nowCls;
  if (status === 'deficit') { st = 'under'; fillCls = 'under'; nowCls = ' warn'; }
  else if (status === 'over') { st = 'over'; fillCls = 'over'; nowCls = ''; }
  else { st = 'ok'; fillCls = 'ok'; nowCls = ''; }
  const stText = st === 'under' ? 'ขาด' : (st === 'over' ? 'เกิน' : 'ตรง');
  // fill width: pct relative to its own target, capped at 100%
  const fillW = target > 0 ? Math.min(100, pct / target * 100) : (pct > 0 ? 100 : 0);
  // target mark: position of target along the max(target,pct) scale
  const scale = Math.max(target, pct) || 1;
  const markLeft = Math.min(100, target / scale * 100);
  return '<span class="st ' + st + '">' + stText + '</span> ' +
    '<span class="now' + nowCls + '">' + pct.toFixed(1) + '%</span>' +
    '<span class="arrow">/</span><span class="tgt">' + target.toFixed(1) + '</span>' +
    '<div class="bar"><div class="fill ' + fillCls + '" style="width:' + fillW + '%"></div>' +
    '<div class="mk" style="left:' + markLeft + '%"></div></div>';
}

function _renderRows(root, state) {
  const host = root.querySelector('#ph-rows');
  if (!host) return;
  const esc = window.MMUtils.escapeHtml;
  const positions = state.positions || [];
  let html = '';

  positions.forEach(function (p) {
    const sym = p.sym || '';
    const status = p.status || 'ok';
    const pct = p.pct || 0;
    const target = p.target_pct || 0;
    // มูลค่า = current_value (fallback shares*price ถ้า backend ไม่คืน)
    let cv = p.current_value;
    if (cv == null) cv = (p.shares || 0) * (p.price || 0);
    const priceStr = p.price != null ? window.MMUtils.fmtNum(p.price, 2) : '—';
    const shares = p.shares || 0;

    html += '<tr data-ph-sym="' + esc(sym) + '">' +
      '<td><a class="sym" href="' + _REPORT_BASE + esc(sym) + '">' +
        '<span class="g ' + _groupDot(p.group) + '"></span>' + esc(sym) + '</a></td>' +
      '<td><input class="qty" data-ph-qty="' + esc(sym) + '" inputmode="numeric" value="' +
        window.MMUtils.fmtNum(shares, 0) + '"></td>' +
      '<td>' + priceStr + '</td>' +
      '<td>' + window.MMUtils.fmtNum(cv, 0) + '</td>' +
      '<td class="alloc">' + _allocCell(pct, target, status) + '</td>' +
    '</tr>';
  });

  // cash row (input = บาท)
  const cash = state.cash || 0;
  const cashPct = state.cash_pct || 0;
  const cashTgt = state.cash_target_pct || 0;
  const cashStatus = (cashPct - cashTgt < -0.5) ? 'deficit'
    : ((cashPct - cashTgt > 0.5) ? 'over' : 'ok');
  html += '<tr data-ph-cash="1">' +
    '<td><span class="sym"><span class="g cash"></span>เงินสด</span> <span class="sub">dry powder</span></td>' +
    '<td><input class="qty" id="ph-qty-cash" inputmode="numeric" value="' +
      window.MMUtils.fmtNum(cash, 0) + '"></td>' +
    '<td class="dim">—</td>' +
    '<td>' + window.MMUtils.fmtNum(cash, 0) + '</td>' +
    '<td class="alloc">' + _allocCell(cashPct, cashTgt, cashStatus) + '</td>' +
  '</tr>';

  host.innerHTML = html;
}

/* ---------- off-plan (collapsed details) ---------- */
function _renderOffPlan(root, state) {
  const host = root.querySelector('#ph-offplan');
  const sum = root.querySelector('#ph-offplan-sum');
  if (!host) return;
  const esc = window.MMUtils.escapeHtml;
  const list = state.off_plan || [];
  if (!list.length) {
    host.innerHTML = '<div class="dim" style="padding:var(--sp-3) 0">ไม่มีรายการนอกแผน</div>';
    if (sum) sum.textContent = 'นอกแผน';
    return;
  }
  // summary line lists symbols + mode
  const labels = list.map(function (op) {
    const m = (op.mode === 'watch') ? '(รอขาย)' : '(ถือถาวร)';
    return (op.sym || '') + ' ' + m;
  });
  if (sum) sum.textContent = 'นอกแผน — ' + labels.join(' · ');

  let html = '';
  list.forEach(function (op) {
    const sym = op.sym || '';
    const mode = op.mode || 'hold';
    const tagCls = mode === 'watch' ? 'watch' : 'hold';
    const tagTxt = mode === 'watch' ? 'รอจังหวะขาย' : 'ถือถาวร ไม่ซื้อเพิ่ม';
    const plPct = op.pl_pct;
    const plCls = (plPct != null && plPct < 0) ? 'neg' : 'pos';
    const plStr = plPct != null ? ((plPct >= 0 ? '+' : '') + plPct.toFixed(0) + '%') : '';
    const priceStr = op.price != null ? window.MMUtils.fmtNum(op.price, 2) : '—';
    const sharesStr = window.MMUtils.fmtNum(op.shares || 0, 0);
    const avgStr = window.MMUtils.fmtNum(op.avg_cost || 0, 2);

    let opr = priceStr + (plStr ? ' <span class="' + plCls + '">' + plStr + '</span>' : '');
    if (mode === 'watch') {
      opr += ' · <span data-ph-lh-signals>สัญญาณ: กำลังโหลด&hellip;</span>';
    }
    html += '<div class="op">' +
      '<span class="opl">' + esc(sym) +
        ' <span class="tag ' + tagCls + '">' + esc(tagTxt) + '</span>' +
        ' <span class="sub">' + sharesStr + ' หุ้น · ทุน ' + avgStr + '</span></span>' +
      '<span class="opr">' + opr + '</span>' +
    '</div>';
  });
  host.innerHTML = html;
  _loadLhSignals(root);
}

async function _loadLhSignals(root) {
  const hosts = root.querySelectorAll('[data-ph-lh-signals]');
  if (!hosts.length) return;
  try {
    const res = await window.MMApi.get('/api/portfolio/lh-signals');
    const esc = window.MMUtils.escapeHtml;
    const signals = res.signals || [];
    let out;
    if (!signals.length) {
      out = 'สัญญาณ: ไม่มี';
    } else {
      const parts = signals.map(function (s) {
        const dot = s.status === 'danger' ? '●' : (s.status === 'warn' ? '●' : '○');
        return esc(s.label || '') + dot + (s.detail ? esc(s.detail) : '');
      });
      out = 'สัญญาณ: ' + parts.join(' · ');
    }
    hosts.forEach(function (h) { h.innerHTML = out; });
  } catch (e) {
    hosts.forEach(function (h) { h.textContent = 'สัญญาณ: โหลดไม่ได้'; });
  }
}

/* ---------- calculator (top-up) ---------- */
function _parseMoney(raw) {
  const n = parseFloat(String(raw || '').replace(/[, ]/g, ''));
  return isNaN(n) ? 0 : n;
}

async function _runCalc(root) {
  const input = root.querySelector('#ph-calc-input');
  const body = root.querySelector('#ph-calc-body');
  if (!input || !body) return;
  const money = _parseMoney(input.value);
  if (money <= 0) {
    body.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--c-warn-fg)">ใส่จำนวนเงินมากกว่า 0</td></tr>';
    return;
  }
  body.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--fg-dim)">กำลังคำนวณ&hellip;</td></tr>';
  try {
    const res = await window.MMApi.post('/api/portfolio/topup', { new_money: money });
    _renderCalcTable(body, res.allocation || []);
  } catch (e) {
    body.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--c-negative)">คำนวณไม่สำเร็จ: ' +
      window.MMUtils.escapeHtml((e && e.message) || String(e)) + '</td></tr>';
  }
}

function _renderCalcTable(body, allocation) {
  const esc = window.MMUtils.escapeHtml;
  // ตัวขาด (under) ที่ลงเงินจริง vs ที่เหลือ (เกิน/ตรง — ยุบรวมบรรทัดเดียว)
  const buys = [];
  const skips = [];
  allocation.forEach(function (r) {
    const isBuy = (r.status === 'under') && ((r.baht || 0) > 0);
    if (isBuy) buys.push(r);
    else skips.push(r);
  });
  // sort buys by baht desc
  buys.sort(function (a, b) { return (b.baht || 0) - (a.baht || 0); });

  let html = '';
  buys.forEach(function (r) {
    const isCash = (r.sym === 'cash');
    const symLabel = isCash ? 'เงินสด' : r.sym;
    const deficit = r.deficit_pct != null ? r.deficit_pct.toFixed(1) : '0';
    const priceStr = isCash ? '<span class="dim">—</span>' :
      (r.price != null ? window.MMUtils.fmtNum(r.price, 2) : '—');
    const buy = r.shares_to_buy;
    const sharesCell = isCash ? '<span class="b">—</span>'
      : (buy != null && buy > 0 ? '<span class="b">+' + window.MMUtils.fmtNum(buy, 0) + '</span>' : '—');
    const bahtCell = '<span class="b">' + window.MMUtils.fmtNum(r.baht || 0, 0) + '</span>';
    html += '<tr>' +
      '<td class="sym">' + esc(symLabel) + '</td>' +
      '<td><span class="st under">ขาด ' + deficit + '%</span></td>' +
      '<td>' + priceStr + '</td>' +
      '<td>' + sharesCell + '</td>' +
      '<td>' + bahtCell + '</td>' +
    '</tr>';
  });

  if (skips.length) {
    const names = skips.map(function (r) { return r.sym === 'cash' ? 'เงินสด' : r.sym; });
    html += '<tr>' +
      '<td class="sym skip">' + esc(names.join(' · ')) + '</td>' +
      '<td colspan="4" style="text-align:left" class="skip">เกิน/ตรงเป้า — ไม่ต้องซื้อ</td>' +
    '</tr>';
  }
  body.innerHTML = html || '<tr><td colspan="5" style="text-align:center;color:var(--fg-dim)">ไม่มีผลลัพธ์</td></tr>';
}

/* ---------- save whole portfolio (PUT holdings + cash) ---------- */
async function _saveAll(root) {
  if (!_state) return;
  const btn = root.querySelector('#ph-save');
  const holdings = {};
  (_state.positions || []).forEach(function (p) {
    const sel = (window.CSS && window.CSS.escape) ? window.CSS.escape(p.sym) : p.sym;
    const inp = root.querySelector('[data-ph-qty="' + sel + '"]');
    const shares = inp ? _parseMoney(inp.value) : (p.shares || 0);
    holdings[p.sym] = { shares: shares, avg_cost: (p.avg_cost || 0) };
  });
  const cashInp = root.querySelector('#ph-qty-cash');
  const cash = cashInp ? _parseMoney(cashInp.value) : (_state.cash || 0);

  if (btn) { btn.disabled = true; btn.textContent = 'กำลังบันทึก…'; }
  try {
    const state = await window.MMApi.put('/api/portfolio/holdings', { holdings: holdings, cash: cash });
    _state = state;
    window.MMComponents.showToast('บันทึกพอร์ตแล้ว', 'info');
    _renderTotal(root, state);
    _renderRows(root, state);
    _renderOffPlan(root, state);
    _renderFoot(root, state);
  } catch (e) {
    window.MMComponents.showToast('บันทึกไม่สำเร็จ: ' + ((e && e.message) || e), 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = 'บันทึกพอร์ต'; }
  }
}

/* ---------- events ---------- */
function _bindEvents(root) {
  root.addEventListener('click', function (e) {
    if (e.target.closest('#ph-calc-btn')) { _runCalc(root); return; }
    if (e.target.closest('#ph-save')) { _saveAll(root); return; }
  });
  root.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter') return;
    if (e.target.id === 'ph-calc-input') { e.preventDefault(); _runCalc(root); return; }
    if (e.target.classList && e.target.classList.contains('qty')) { e.preventDefault(); _saveAll(root); }
  });
}
