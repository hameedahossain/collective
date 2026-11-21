/* Connections map: a radial "constellation" of people around Dr. Hossain.
   Data comes from <script type="application/json" id="people-data">. The list below the map works without JS. */
(function () {
  var dataEl = document.getElementById('people-data');
  var stage = document.querySelector('.cx-stage');
  if (!dataEl || !stage) return;
  var D = JSON.parse(dataEl.textContent);
  var people = D.people, groups = D.groups;
  var byId = {}; people.forEach(function (p) { byId[p.id] = p; });
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  var svg = stage.querySelector('svg');
  var nodesLayer = stage.querySelector('.cx-nodes');
  var NS = 'http://www.w3.org/2000/svg';
  var C = 500, R = 305;

  // ── layout: groups as sectors, people alternating between two rings ──
  var order = groups.map(function (g) { return g.key; });
  var counts = {}; people.forEach(function (p) { counts[p.group] = (counts[p.group] || 0) + 1; });
  var total = people.length, gap = 0.06, usable = Math.PI * 2 - gap * order.length;
  var angle = -Math.PI / 2, sectors = {};
  order.forEach(function (k) {
    var n = counts[k] || 0; if (!n) return;
    var span = usable * n / total;
    sectors[k] = { start: angle, end: angle + span };
    angle += span + gap;
  });
  var idx = {};
  people.forEach(function (p) {
    var s = sectors[p.group], n = counts[p.group];
    var i = idx[p.group] = (idx[p.group] || 0) + 1;
    var a = s.start + (s.end - s.start) * (i - 0.5) / n;
    p._a = a; p._x = C + R * Math.cos(a); p._y = C + R * Math.sin(a);
  });

  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  var gColor = {}; groups.forEach(function (g) { gColor[g.key] = g.color; });

  // sector arcs + labels
  var deco = el('g', { 'class': 'cx-deco' }, svg);
  order.forEach(function (k) {
    var s = sectors[k]; if (!s) return;
    var r = R - 38, a0 = s.start, a1 = s.end;
    var x0 = C + r * Math.cos(a0), y0 = C + r * Math.sin(a0), x1 = C + r * Math.cos(a1), y1 = C + r * Math.sin(a1);
    el('path', { d: 'M' + x0 + ' ' + y0 + ' A' + r + ' ' + r + ' 0 ' + ((a1 - a0) > Math.PI ? 1 : 0) + ' 1 ' + x1 + ' ' + y1, stroke: gColor[k], 'class': 'cx-arc' }, deco);
  });
  [150, R].forEach(function (r) { el('circle', { cx: C, cy: C, r: r, 'class': 'cx-ring' }, deco); });

  // threads from centre + cross-links
  var threads = el('g', { 'class': 'cx-threads' }, svg);
  var links = el('g', { 'class': 'cx-links' }, svg);
  people.forEach(function (p) {
    var sx = C + 112 * Math.cos(p._a), sy = C + 112 * Math.sin(p._a);
    var mx = C + 210 * Math.cos(p._a + 0.06), my = C + 210 * Math.sin(p._a + 0.06);
    p._thread = el('path', { d: 'M' + sx + ' ' + sy + ' Q' + mx + ' ' + my + ' ' + p._x + ' ' + p._y, stroke: gColor[p.group], 'class': 'cx-thread' }, threads);
  });
  var seen = {};
  people.forEach(function (p) {
    (p.related || []).forEach(function (rid) {
      var q = byId[rid]; if (!q) return;
      var key = [p.id, rid].sort().join('|'); if (seen[key]) return; seen[key] = 1;
      var mx = (p._x + q._x) / 2, my = (p._y + q._y) / 2;
      var cx = C + (mx - C) * 0.35, cy = C + (my - C) * 0.35;
      var l = el('path', { d: 'M' + p._x + ' ' + p._y + ' Q' + cx + ' ' + cy + ' ' + q._x + ' ' + q._y, 'class': 'cx-link' }, links);
      l._a = p.id; l._b = rid;
      (p._links = p._links || []).push(l); (q._links = q._links || []).push(l);
    });
  });

  // nodes (HTML buttons positioned over the SVG)
  function initials(n) { return n.replace(/^(Dr|Prof|Professor|Begum|Justice|Sir)\.?\s+/i, '').split(/\s+/).filter(Boolean).map(function (w) { return w[0]; }).slice(0, 2).join('').toUpperCase(); }
  people.forEach(function (p, i) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'cx-node'; b.setAttribute('data-id', p.id);
    b.style.left = (p._x / 10) + '%'; b.style.top = (p._y / 10) + '%';
    b.style.setProperty('--gc', gColor[p.group]);
    b.style.setProperty('--d', (reduce ? 0 : 0.25 + i * 0.025) + 's');
    var deg = p._a * 180 / Math.PI, right = Math.cos(p._a) >= 0;
    b.innerHTML = '<span class="cx-dot">' + initials(p.name) + '</span><span class="cx-name">' + p.name + '</span>';
    var lab = b.querySelector('.cx-name');
    lab.style.transform = right ? 'rotate(' + deg + 'deg) translate(var(--off), -50%)' : 'rotate(' + (deg + 180) + 'deg) translate(calc(-100% - var(--off)), -50%)';
    b.setAttribute('aria-label', p.name + ', ' + p.role);
    b.addEventListener('mouseenter', function () { focus(p.id); });
    b.addEventListener('mouseleave', function () { if (!openId) focus(null); });
    b.addEventListener('focus', function () { focus(p.id); });
    b.addEventListener('click', function () { open(p.id); });
    nodesLayer.appendChild(b);
    p._node = b;
  });

  // ── highlight ──
  function focus(id) {
    stage.classList.toggle('dim', !!id);
    people.forEach(function (p) {
      var rel = id && (p.id === id || (byId[id].related || []).indexOf(p.id) >= 0 || (p.related || []).indexOf(id) >= 0);
      p._node.classList.toggle('on', !!rel);
      p._node.classList.toggle('self', p.id === id);
      p._thread.classList.toggle('on', p.id === id);
      (p._links || []).forEach(function (l) { l.classList.toggle('on', !!id && (l._a === id || l._b === id)); });
    });
  }

  // ── detail panel ──
  var panel = document.querySelector('.cx-panel'), openId = null, emptyHTML = panel.innerHTML;
  function esc(s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function open(id) {
    var p = byId[id]; if (!p) return;
    openId = id; focus(id);
    var g = groups.filter(function (x) { return x.key === p.group; })[0];
    var works = (p.works || []).map(function (w) { return '<li><a href="' + esc(w.href) + '">' + esc(w.label) + '</a></li>'; }).join('');
    var ext = (p.links || []).map(function (l) { return '<li><a href="' + esc(l.url) + '" target="_blank" rel="noopener">' + esc(l.label) + ' ↗</a></li>'; }).join('');
    var rel = (p.related || []).filter(function (r) { return byId[r]; }).map(function (r) { return '<button type="button" class="cx-chip" data-go="' + r + '" style="--gc:' + gColor[byId[r].group] + '">' + esc(byId[r].name) + '</button>'; }).join('');
    panel.innerHTML =
      '<button type="button" class="cx-close" aria-label="Close">×</button>' +
      '<p class="cx-group" style="--gc:' + g.color + '">' + esc(g.label) + (p.years ? ' · ' + esc(p.years) : '') + '</p>' +
      '<h2>' + esc(p.name) + '</h2><p class="cx-role">' + esc(p.role) + '</p>' +
      '<p class="cx-conn">' + esc(p.connection) + '</p>' +
      (works ? '<h3>Her work with them</h3><ul class="cx-list">' + works + '</ul>' : '') +
      (ext ? '<h3>About ' + esc(p.name) + '</h3><ul class="cx-list ext">' + ext + '</ul>' : '') +
      (rel ? '<h3>Also connected to</h3><div class="cx-chips">' + rel + '</div>' : '');
    panel.classList.add('open');
    panel.querySelector('.cx-close').addEventListener('click', close);
    panel.querySelectorAll('[data-go]').forEach(function (b) { b.addEventListener('click', function () { open(b.getAttribute('data-go')); }); });
    if (history.replaceState) history.replaceState(null, '', '#' + id);
    panel.querySelector('h2').setAttribute('tabindex', '-1'); panel.querySelector('h2').focus({ preventScroll: true });
  }
  function close() {
    openId = null; panel.classList.remove('open'); panel.innerHTML = emptyHTML; focus(null);
    if (history.replaceState) history.replaceState(null, '', location.pathname);
  }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && openId) close(); });
  document.querySelectorAll('.cx-person [data-open]').forEach(function (a) {
    a.addEventListener('click', function (e) { e.preventDefault(); open(a.getAttribute('data-open')); stage.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); });
  });

  // ── filters & search ──
  var active = 'all', q = '';
  function applyFilter() {
    people.forEach(function (p) {
      var ok = (active === 'all' || p.group === active) && (!q || (p.name + ' ' + p.role + ' ' + p.connection).toLowerCase().indexOf(q) >= 0);
      p._node.classList.toggle('hide', !ok); p._thread.classList.toggle('hide', !ok);
      (p._links || []).forEach(function (l) { l.classList.toggle('hide', !ok); });
    });
  }
  document.querySelectorAll('[data-cx-group]').forEach(function (b) {
    b.addEventListener('click', function () {
      active = b.getAttribute('data-cx-group');
      document.querySelectorAll('[data-cx-group]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      applyFilter();
    });
  });
  var s = document.querySelector('[data-cx-search]');
  if (s) s.addEventListener('input', function () {
    q = s.value.trim().toLowerCase(); applyFilter();
    var hits = people.filter(function (p) { return !p._node.classList.contains('hide'); });
    if (q && hits.length === 1) focus(hits[0].id); else if (!openId) focus(null);
  });

  // intro animation, then deep link
  requestAnimationFrame(function () { stage.classList.add('ready'); });
  if (location.hash && byId[location.hash.slice(1)]) setTimeout(function () { open(location.hash.slice(1)); }, reduce ? 0 : 900);
})();
