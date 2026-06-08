/* ==========================================================
   MAX MAHON v6 — Portfolio Home (Mobile)  — route "/m"
   เว็บพอร์ตจริง (pillar 1 ปันผล) — หน้าเดียวจบ, layout 1-col
   Same data + logic as desktop portfolio-home.js; layout differences
   come from .pf-home overrides in shared/mobile.css.
   Live data:
     GET  /api/portfolio/state / lh-signals
     POST /api/portfolio/topup
     PUT  /api/portfolio/holdings
   ========================================================== */

let _state = null;

export function mount(root) {
  root.classList.add('pf-home');
  root.innerHTML = _renderShell();
  _bindEvents(root);
  _load(root);
}

function _renderShell() {
  return (
    '<section class="pf-hero">' +
      '<div class="inner">' +
        '<div class="hero-eyebrow uppercase">มูลค่าพอร์ตหลัก</div>' +
        '<div class="hero-value mono" id="ph-hero-value">—</div>' +
        '<div class="hero-sub" id="ph-hero-sub"></div>' +
        '<div class="pf-summary-strip" id="ph-summary"></div>' +
      '</div>' +
    '</section>' +
    '<div class="pf-container">' +

      '<section class="pf-section">' +
        '<div class="pf-section-head">' +
          '<div class="pf-section-title serif">มีเงินมาเพิ่ม ใส่ตรงไหน</div>' +
          '<div class="pf-section-note">ปันผล + รายได้ใหม่ = กองกลางก้อนเดียว เติมเฉพาะตัวที่ขาดเป้า</div>' +
        '</div>' +
        '<div class="calc">' +
          '<div class="calc-top">' +
            '<div>' +
              '<div class="calc-label">เงินกองกลางรอลง (บาท)</div>' +
              '<div class="calc-input-row">' +
                '<input class="calc-input mono" id="ph-calc-input" inputmode="numeric" value="100,000">' +
                '<button class="calc-btn" id="ph-calc-btn" type="button">คำนวณ &rarr;</button>' +
              '</div>' +
            '</div>' +
            '<div class="calc-hint">เติมเฉพาะช่องที่ต่ำกว่าเป้า เกลี่ยตามยอดที่ขาด ช่องที่เกินเป้าไม่เติม</div>' +
          '</div>' +
          '<div class="calc-table-wrap"><table class="calc-table">' +
            '<thead><tr><th>หุ้น</th><th>สถานะ</th><th>ราคา</th><th>ซื้อ (หุ้น)</th><th>ลงเงิน</th></tr></thead>' +
            '<tbody id="ph-calc-body"><tr><td colspan="5" style="text-align:center;color:var(--fg-dim)">กดคำนวณเพื่อดูแผนซื้อ</td></tr></tbody>' +
          '</table></div>' +
        '</div>' +
      '</section>' +

      '<section class="pf-section">' +
        '<div class="pf-section-head">' +
          '<div class="pf-section-title serif">พอร์ตหลัก</div>' +
          '<div class="pf-section-note">แท่ง = สัดส่วนจริง ขีดดำ = เป้า แตะการ์ดเพื่อดูเหตุผลเต็ม</div>' +
        '</div>' +
        '<div id="ph-holdings"></div>' +
      '</section>' +

      '<section class="pf-section">' +
        '<div class="pf-section-head">' +
          '<div class="pf-section-title serif">นอกแผน</div>' +
          '<div class="pf-section-note">ไม่นับฐานคำนวณดึงกลับเป้า</div>' +
        '</div>' +
        '<div class="offplan" id="ph-offplan"></div>' +
      '</section>' +

      '<section class="pf-section">' +
        '<div class="pf-section-head">' +
          '<div class="pf-section-title serif">แผนการลงทุน</div>' +
          '<div class="pf-section-note">Pillar 1 Niwes + เซียนฮง DCA 10-20 ปี</div>' +
        '</div>' +
        '<div class="plan-card" style="margin-bottom:var(--sp-4)">' +
          '<h4>โครงสร้างพอร์ต</h4>' +
          '<div class="struct-bar">' +
            '<div class="niwes" style="flex:70">Niwes 70%</div>' +
            '<div class="hong" style="flex:25">ฮง 25%</div>' +
            '<div class="cash" style="flex:5">5%</div>' +
          '</div>' +
          '<p>4 cyclical (AMATA + BBL + TOA + MOSHI = 68.75%) : 3 defensive (TCAP + SISB + SECURE = 26.25%) : เงินสด 5%</p>' +
        '</div>' +
        '<div class="plan-grid">' +
          '<div class="plan-card"><h4>วิธีเติมเงิน</h4><p>ปันผล + รายได้ใหม่ รวมกองกลางก้อนเดียว เติมเฉพาะตัวขาดเป้า ดึงพอร์ตกลับสัดส่วนเอง</p></div>' +
          '<div class="plan-card"><h4>ไม่ทำอะไร</h4><p>ไม่แบ่งรอบ 30:30:30:10 ไม่ซื้อเพิ่มตามราคา ไม่ cut loss (ถือยาว thesis ยังอยู่)</p></div>' +
          '<div class="plan-card"><h4>ใช้เงินสดเมื่อไหร่</h4><p>หุ้นตก &ge;20% จาก high ทั้งที่ thesis ยังจริง หรือ crash ทั้งตลาด</p></div>' +
        '</div>' +
      '</section>' +

    '</div>'
  );
}

async function _load(root) {
  const holdHost = root.querySelector('#ph-holdings');
  if (holdHost) window.MMComponents.renderLoading(holdHost, 'โหลดพอร์ต');
  try {
    const state = await window.MMApi.get('/api/portfolio/state');
    _state = state;
    _renderHero(root, state);
    _renderSummary(root, state);
    _renderHoldings(root, state);
    _renderOffPlan(root, state);
    _loadLhSignals(root);
  } catch (e) {
    window.MMComponents.renderError(
      holdHost || root,
      'โหลดพอร์ตไม่สำเร็จ: ' + (e && e.message || e),
      function () { _load(root); }
    );
  }
}

function _renderHero(root, state) {
  const valEl = root.querySelector('#ph-hero-value');
  const subEl = root.querySelector('#ph-hero-sub');
  if (valEl) {
    valEl.innerHTML = window.MMUtils.fmtNum(state.total_value || 0, 0) + '<span class="cur">บาท</span>';
  }
  if (subEl) {
    let divIncome = 0, weightedYieldNum = 0;
    const positions = state.positions || [];
    for (let i = 0; i < positions.length; i++) {
      const p = positions[i];
      const cv = p.current_value || 0;
      const y = (p.metrics && p.metrics.yield) || 0;
      divIncome += cv * y / 100;
      weightedYieldNum += cv * y;
    }
    const totalCv = (state.total_value || 0) - (state.cash || 0);
    const wYield = totalCv > 0 ? (weightedYieldNum / totalCv) : 0;
    subEl.innerHTML =
      'ปันผลคาด <b class="mono pos">~' + window.MMUtils.fmtNum(divIncome, 0) + ' บาท</b> ' +
      '&middot; yield <b class="mono">' + wYield.toFixed(1) + '%</b> ' +
      '&middot; เป้า 100M';
  }
}

function _renderSummary(root, state) {
  const host = root.querySelector('#ph-summary');
  if (!host) return;
  const s = state.summary || {};
  const esc = window.MMUtils.escapeHtml;
  const slots = (s.count_total || 0) + 1;
  const overSyms = [], deficitSyms = [];
  (state.positions || []).forEach(function (p) {
    if (p.status === 'over') overSyms.push(p.sym);
    else if (p.status === 'deficit') deficitSyms.push(p.sym);
  });
  const cashPct = state.cash_pct || 0;
  const cashTgt = state.cash_target_pct || 0;
  if (cashPct - cashTgt < -0.5) deficitSyms.push('Cash');
  else if (cashPct - cashTgt > 0.5) overSyms.push('Cash');

  function cell(label, val, warn) {
    return '<div class="pf-summary-cell"><div class="label">' + esc(label) + '</div>' +
      '<div class="val"' + (warn ? ' style="color:var(--c-warn-fg)"' : '') + '>' + val + '</div></div>';
  }
  host.innerHTML =
    cell('หุ้นในแผน', (s.count_total || 0) + ' ตัว', false) +
    cell('เงินสด', cashPct.toFixed(1) + '%', false) +
    cell('ตรงเป้า', '<span class="pos">' + (s.count_on_target || 0) + ' / ' + slots + '</span>', false) +
    cell('เกินเป้า', overSyms.length ? esc(overSyms.join('·')) : '—', false) +
    cell('ขาดเป้า', deficitSyms.length ? esc(deficitSyms.join('·')) : '—', true);
}

function _groupLabel(tagCls, tagText, note) {
  const esc = window.MMUtils.escapeHtml;
  return '<div class="group-label">' +
    '<span class="tag ' + tagCls + '">' + esc(tagText) + '</span>' +
    '<span class="gl-note">' + esc(note) + '</span>' +
    '<span class="gl-line"></span>' +
  '</div>';
}

function _renderHoldings(root, state) {
  const host = root.querySelector('#ph-holdings');
  if (!host) return;
  const positions = state.positions || [];
  const niwes = positions.filter(function (p) { return (p.group || '') === 'niwes'; });
  const hong = positions.filter(function (p) { return (p.group || '') === 'hong'; });
  const other = positions.filter(function (p) {
    return (p.group || '') !== 'niwes' && (p.group || '') !== 'hong';
  });

  let html = '';
  html += _groupLabel('niwes', 'Niwes 70%', 'แกนหลัก AMATA + BBL anchor');
  niwes.forEach(function (p) { html += _holdingCard(p); });
  if (other.length) { other.forEach(function (p) { html += _holdingCard(p); }); }
  html += _groupLabel('hong', 'เซียนฮง 25%', 'TOA SISB SECURE MOSHI');
  hong.forEach(function (p) { html += _holdingCard(p); });
  html += _groupLabel('cash', 'เงินสด 5%', 'Dry powder ช้อนตอนตกแรง');
  html += _cashCard(state);
  host.innerHTML = html;
}

function _holdingCard(p) {
  const esc = window.MMUtils.escapeHtml;
  const sym = p.sym || '';
  const status = p.status || 'ok';
  const fillCls = status === 'over' ? 'over' : (status === 'deficit' ? 'under' : '');
  const pctNumCls = status === 'deficit' ? ' under' : '';
  const pct = p.pct || 0;
  const target = p.target_pct || 0;
  const fillW = target > 0 ? Math.min(100, pct / target * 100) : (pct > 0 ? 100 : 0);
  const scale = Math.max(target, pct) || 1;
  const markLeft = Math.min(100, target / scale * 100);

  const m = p.metrics || {};
  function metric(label, val, suffix) {
    if (val === null || val === undefined) return '';
    return '<span class="h-metric">' + label + '<b>' + esc(String(val)) + (suffix || '') + '</b></span>';
  }
  const metricsHtml =
    metric('Yield', m.yield != null ? m.yield.toFixed(2) : null, '%') +
    metric('P/E', m.pe, '') +
    metric('P/BV', m.pbv, '') +
    metric('ROE', m.roe != null ? m.roe.toFixed(1) : null, '%') +
    metric('Payout', m.payout, '%');

  const priceStr = p.price != null ? window.MMUtils.fmtNum(p.price, 2) : '—';
  const sharesStr = window.MMUtils.fmtNum(p.shares || 0, 0) + ' หุ้น';

  return '<div class="holding" data-ph-sym="' + esc(sym) + '">' +
    '<div>' +
      '<div class="h-sym">' + esc(sym) + '</div>' +
      '<div class="h-name">' + esc(p.name || '') + '</div>' +
      (p.sector ? '<div class="h-sector">' + esc(p.sector) + '</div>' : '') +
    '</div>' +
    '<div>' +
      '<div class="h-thesis">' + esc(p.thesis || '') + '</div>' +
      '<div class="h-metrics">' + metricsHtml + '</div>' +
    '</div>' +
    '<div class="alloc">' +
      '<div class="alloc-nums"><span class="cur-pct' + pctNumCls + '">' + pct.toFixed(1) + '%</span> ' +
        '<span class="tgt">/ ' + target.toFixed(1) + '</span></div>' +
      '<div class="alloc-bar">' +
        '<div class="fill ' + fillCls + '" style="width:' + fillW + '%"></div>' +
        '<div class="target-mark" style="left:' + markLeft + '%"></div>' +
      '</div>' +
    '</div>' +
    '<div class="h-right">' +
      '<div class="h-price mono">' + priceStr + '</div>' +
      '<div class="h-shares">' + sharesStr + '</div>' +
      '<div class="h-view" data-ph-view="' + esc(sym) + '">ดูเหตุผลเต็ม &rarr;</div>' +
      '<div class="h-edit" data-ph-edit="' + esc(sym) + '">แก้จำนวนหุ้น</div>' +
    '</div>' +
  '</div>';
}

function _cashCard(state) {
  const cash = state.cash || 0;
  const pct = state.cash_pct || 0;
  const target = state.cash_target_pct || 0;
  const status = (pct - target < -0.5) ? 'deficit' : ((pct - target > 0.5) ? 'over' : 'ok');
  const fillCls = status === 'over' ? 'over' : (status === 'deficit' ? 'under' : '');
  const pctNumCls = status === 'deficit' ? ' under' : '';
  const fillW = target > 0 ? Math.min(100, pct / target * 100) : (pct > 0 ? 100 : 0);
  const scale = Math.max(target, pct) || 1;
  const markLeft = Math.min(100, target / scale * 100);

  return '<div class="holding static">' +
    '<div><div class="h-sym">เงินสด</div><div class="h-name">Dry powder</div></div>' +
    '<div><div class="h-thesis">รอจังหวะของถูก ใช้เฉพาะตอนราคาตกแรงทั้งที่ thesis ไม่เสีย หรือ crash ทั้งตลาด</div></div>' +
    '<div class="alloc">' +
      '<div class="alloc-nums"><span class="cur-pct' + pctNumCls + '">' + pct.toFixed(1) + '%</span> ' +
        '<span class="tgt">/ ' + target.toFixed(1) + '</span></div>' +
      '<div class="alloc-bar">' +
        '<div class="fill ' + fillCls + '" style="width:' + fillW + '%"></div>' +
        '<div class="target-mark" style="left:' + markLeft + '%"></div>' +
      '</div>' +
    '</div>' +
    '<div class="h-right">' +
      '<div class="h-price mono">' + window.MMUtils.fmtNum(cash, 0) + '</div>' +
      '<div class="h-shares">บาท</div>' +
      '<div class="h-edit" data-ph-edit-cash="1">แก้เงินสด</div>' +
    '</div>' +
  '</div>';
}

function _renderOffPlan(root, state) {
  const host = root.querySelector('#ph-offplan');
  if (!host) return;
  const esc = window.MMUtils.escapeHtml;
  const list = state.off_plan || [];
  let html = '';
  list.forEach(function (op) {
    const sym = op.sym || '';
    const mode = op.mode || 'hold';
    const cardCls = mode === 'watch' ? 'watch' : 'hold';
    const statusTxt = mode === 'watch' ? 'รอจังหวะขาย' : 'ถือถาวร ไม่ซื้อเพิ่ม';
    const plPct = op.pl_pct;
    const plCls = (plPct != null && plPct < 0) ? 'neg' : 'pos';
    const plStr = plPct != null ? ((plPct >= 0 ? '+' : '') + plPct.toFixed(1) + '%') : '—';
    const priceStr = op.price != null ? window.MMUtils.fmtNum(op.price, 2) : '—';
    const cvStr = window.MMUtils.fmtNum(op.current_value || 0, 0);
    const sharesStr = window.MMUtils.fmtNum(op.shares || 0, 0);
    const avgStr = window.MMUtils.fmtNum(op.avg_cost || 0, 2);

    let body =
      '<div class="op-head">' +
        '<div><div class="op-sym">' + esc(sym) + '</div></div>' +
        '<div class="op-status ' + cardCls + '">' + esc(statusTxt) + '</div>' +
      '</div>' +
      '<div class="op-row"><span>ถือ ' + sharesStr + ' หุ้น ทุน ' + avgStr + '</span>' +
        '<span class="op-pl ' + plCls + '">' + plStr + '</span></div>' +
      '<div class="op-row"><span>ราคาล่าสุด</span><span class="v">' + priceStr + '</span></div>' +
      '<div class="op-row"><span>มูลค่าปัจจุบัน</span><span class="v">' + cvStr + '</span></div>';

    if (mode === 'watch') {
      body += '<div class="signals" data-ph-lh-signals>' +
        '<div class="signal"><span class="dot off"></span><span class="s-label dim">กำลังโหลดสัญญาณ LH</span><span class="s-val"></span></div>' +
      '</div>';
    } else {
      body += '<div class="op-note">อยู่ในพอร์ตถาวร เก็บกินปันผล ไม่เข้า cycle ดึงกลับเป้า และไม่ซื้อเพิ่ม</div>';
    }
    html += '<div class="op-card ' + cardCls + '">' + body + '</div>';
  });
  host.innerHTML = html || '<div style="color:var(--fg-dim)">ไม่มีรายการนอกแผน</div>';
}

async function _loadLhSignals(root) {
  const host = root.querySelector('[data-ph-lh-signals]');
  if (!host) return;
  try {
    const res = await window.MMApi.get('/api/portfolio/lh-signals');
    const esc = window.MMUtils.escapeHtml;
    const signals = res.signals || [];
    if (!signals.length) { host.innerHTML = '<div class="signal dim">ไม่มีสัญญาณ</div>'; return; }
    let html = '';
    signals.forEach(function (s) {
      const dotCls = s.status === 'danger' ? 'danger' : (s.status === 'warn' ? 'warn' : 'off');
      html += '<div class="signal">' +
        '<span class="dot ' + dotCls + '"></span>' +
        '<span class="s-label">' + esc(s.label || '') + '</span>' +
        '<span class="s-val">' + esc(s.detail || '') + '</span>' +
      '</div>';
    });
    host.innerHTML = html;
  } catch (e) {
    host.innerHTML = '<div class="signal"><span class="dot off"></span><span class="s-label dim">โหลดสัญญาณ LH ไม่ได้</span></div>';
  }
}

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
  body.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--fg-dim)">กำลังคำนวณ</td></tr>';
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
  const rows = allocation.slice().sort(function (a, b) {
    const au = a.status === 'under' ? 0 : 1;
    const bu = b.status === 'under' ? 0 : 1;
    if (au !== bu) return au - bu;
    return (b.baht || 0) - (a.baht || 0);
  });
  let html = '';
  rows.forEach(function (r) {
    const isCash = (r.sym === 'cash');
    const symLabel = isCash ? 'เงินสด' : r.sym;
    let pill;
    if (r.status === 'under') {
      pill = '<span class="pf-pill under">ขาด ' + (r.deficit_pct != null ? r.deficit_pct.toFixed(1) : '0') + '%</span>';
    } else if (r.status === 'over') {
      pill = '<span class="pf-pill over">เกินเป้า</span>';
    } else {
      pill = '<span class="pf-pill ok">ตรงเป้า</span>';
    }
    const priceStr = isCash ? '—' : (r.price != null ? window.MMUtils.fmtNum(r.price, 2) : '—');
    const buys = r.shares_to_buy;
    const cellCls = (r.status === 'under' && (r.baht || 0) > 0) ? 'add' : 'skip';
    let sharesCell;
    if (isCash) {
      sharesCell = '—';
    } else if (buys != null && buys > 0) {
      sharesCell = '+' + window.MMUtils.fmtNum(buys, 0);
    } else {
      sharesCell = '—';
    }
    const bahtCell = (r.baht || 0) > 0 ? window.MMUtils.fmtNum(r.baht, 0) : '0';
    html += '<tr>' +
      '<td>' + esc(symLabel) + '</td>' +
      '<td>' + pill + '</td>' +
      '<td>' + priceStr + '</td>' +
      '<td class="' + cellCls + '">' + sharesCell + '</td>' +
      '<td class="' + cellCls + '">' + bahtCell + '</td>' +
    '</tr>';
  });
  body.innerHTML = html || '<tr><td colspan="5" style="text-align:center;color:var(--fg-dim)">ไม่มีผลลัพธ์</td></tr>';
}

function _openEditShares(root, sym) {
  if (!_state) return;
  const pos = (_state.positions || []).find(function (p) { return p.sym === sym; });
  if (!pos) return;
  const esc = window.MMUtils.escapeHtml;
  const html =
    '<p style="color:var(--fg-secondary);margin-bottom:var(--sp-4)">แก้จำนวนหุ้น + ราคาทุนเฉลี่ยของ <b>' + esc(sym) + '</b></p>' +
    '<label style="display:block;font-size:var(--fs-sm);color:var(--fg-dim);margin-bottom:var(--sp-1)">จำนวนหุ้น</label>' +
    '<input type="text" id="ph-ed-shares" inputmode="numeric" value="' + (pos.shares || 0) + '" ' +
      'style="width:100%;padding:10px 12px;border:1px solid var(--border-subtle);background:var(--bg-surface);' +
      'font-family:var(--font-mono);font-size:var(--fs-md);color:var(--fg-primary);outline:none;margin-bottom:var(--sp-4)">' +
    '<label style="display:block;font-size:var(--fs-sm);color:var(--fg-dim);margin-bottom:var(--sp-1)">ราคาทุนเฉลี่ย</label>' +
    '<input type="text" id="ph-ed-avg" inputmode="decimal" value="' + (pos.avg_cost || 0) + '" ' +
      'style="width:100%;padding:10px 12px;border:1px solid var(--border-subtle);background:var(--bg-surface);' +
      'font-family:var(--font-mono);font-size:var(--fs-md);color:var(--fg-primary);outline:none;margin-bottom:var(--sp-4)">' +
    '<div style="display:flex;justify-content:flex-end;gap:var(--sp-3)">' +
      '<button type="button" class="btn ghost" id="ph-ed-cancel">ยกเลิก</button>' +
      '<button type="button" class="btn primary" id="ph-ed-save">บันทึก</button>' +
    '</div>';
  window.MMComponents.openModal(html, { kicker: 'Portfolio · แก้พอร์ต', headline: 'แก้จำนวนหุ้น ' + sym });
  const cancel = document.getElementById('ph-ed-cancel');
  const save = document.getElementById('ph-ed-save');
  if (cancel) cancel.addEventListener('click', function () { window.MMComponents.closeModal(); });
  if (save) save.addEventListener('click', async function () {
    const shares = _parseMoney(document.getElementById('ph-ed-shares').value);
    const avg = _parseMoney(document.getElementById('ph-ed-avg').value);
    const holdings = {};
    (_state.positions || []).forEach(function (p) {
      holdings[p.sym] = { shares: p.sym === sym ? shares : (p.shares || 0),
                          avg_cost: p.sym === sym ? avg : (p.avg_cost || 0) };
    });
    await _saveHoldings(root, { holdings: holdings });
  });
}

function _openEditCash(root) {
  if (!_state) return;
  const html =
    '<p style="color:var(--fg-secondary);margin-bottom:var(--sp-4)">แก้ยอดเงินสด (dry powder)</p>' +
    '<input type="text" id="ph-ed-cash" inputmode="numeric" value="' + (_state.cash || 0) + '" ' +
      'style="width:100%;padding:10px 12px;border:1px solid var(--border-subtle);background:var(--bg-surface);' +
      'font-family:var(--font-mono);font-size:var(--fs-md);color:var(--fg-primary);outline:none;margin-bottom:var(--sp-4)">' +
    '<div style="display:flex;justify-content:flex-end;gap:var(--sp-3)">' +
      '<button type="button" class="btn ghost" id="ph-ed-cancel">ยกเลิก</button>' +
      '<button type="button" class="btn primary" id="ph-ed-save">บันทึก</button>' +
    '</div>';
  window.MMComponents.openModal(html, { kicker: 'Portfolio · แก้พอร์ต', headline: 'แก้เงินสด' });
  const cancel = document.getElementById('ph-ed-cancel');
  const save = document.getElementById('ph-ed-save');
  if (cancel) cancel.addEventListener('click', function () { window.MMComponents.closeModal(); });
  if (save) save.addEventListener('click', async function () {
    const cash = _parseMoney(document.getElementById('ph-ed-cash').value);
    await _saveHoldings(root, { cash: cash });
  });
}

async function _saveHoldings(root, body) {
  try {
    const state = await window.MMApi.put('/api/portfolio/holdings', body);
    _state = state;
    window.MMComponents.closeModal();
    window.MMComponents.showToast('อัปเดตพอร์ตแล้ว', 'info');
    _renderHero(root, state);
    _renderSummary(root, state);
    _renderHoldings(root, state);
    _renderOffPlan(root, state);
    _loadLhSignals(root);
  } catch (e) {
    window.MMComponents.showToast('บันทึกไม่สำเร็จ: ' + ((e && e.message) || e), 'error');
  }
}

function _bindEvents(root) {
  root.addEventListener('click', function (e) {
    const calcBtn = e.target.closest('#ph-calc-btn');
    if (calcBtn) { _runCalc(root); return; }
    const editBtn = e.target.closest('[data-ph-edit]');
    if (editBtn) { _openEditShares(root, editBtn.getAttribute('data-ph-edit')); return; }
    const editCash = e.target.closest('[data-ph-edit-cash]');
    if (editCash) { _openEditCash(root); return; }
    const viewBtn = e.target.closest('[data-ph-view]');
    if (viewBtn) { location.href = '/m/report/' + viewBtn.getAttribute('data-ph-view'); return; }
    const card = e.target.closest('.holding[data-ph-sym]');
    if (card && !e.target.closest('[data-ph-edit]')) {
      location.href = '/m/report/' + card.getAttribute('data-ph-sym');
    }
  });
  const input = root.querySelector('#ph-calc-input');
  if (input) {
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); _runCalc(root); }
    });
  }
}
