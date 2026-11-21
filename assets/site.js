/* Hameeda Hossain Collective — small progressive enhancements. Everything works without JS. */
(function () {
  var root = document.documentElement;

  // theme toggle (remembered per browser; falls back gracefully)
  function stored() { try { return localStorage.getItem('hh-theme'); } catch (e) { return null; } }
  function store(v) { try { localStorage.setItem('hh-theme', v); } catch (e) {} }
  var t = stored();
  if (t === 'light' || t === 'dark') root.setAttribute('data-theme', t);
  var tb = document.querySelector('.theme-toggle');
  function label() {
    var dark = root.getAttribute('data-theme') === 'dark' ||
      (!root.getAttribute('data-theme') && window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches);
    if (tb) { tb.textContent = dark ? 'Light' : 'Dark'; tb.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode'); }
    return dark;
  }
  if (tb) {
    label();
    tb.addEventListener('click', function () {
      var next = label() ? 'light' : 'dark';
      root.setAttribute('data-theme', next); store(next); label();
    });
  }

  // mobile nav
  var nt = document.querySelector('.nav-toggle'), nav = document.getElementById('site-nav');
  if (nt && nav) nt.addEventListener('click', function () {
    var open = nav.classList.toggle('open'); nt.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // copy citation
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var el = document.getElementById(b.getAttribute('data-copy'));
      if (!el) return;
      var text = el.innerText;
      var done = function () { var o = b.textContent; b.textContent = 'Copied'; setTimeout(function () { b.textContent = o; }, 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {});
      else { var r = document.createRange(); r.selectNodeContents(el); var s = getSelection(); s.removeAllRanges(); s.addRange(r); }
    });
  });

  // filterable lists: <ul data-filter-list> with <li data-*> ; chips <button data-filter="key" data-value="v">
  var list = document.querySelector('[data-filter-list]');
  if (!list) return;
  var items = Array.prototype.slice.call(list.querySelectorAll('[data-item]'));
  var state = {};
  var q = '';
  var search = document.querySelector('[data-search]');
  var count = document.querySelector('[data-count]');
  var empty = document.querySelector('[data-empty]');

  function apply() {
    var shown = 0;
    items.forEach(function (it) {
      var ok = true;
      for (var k in state) {
        if (state[k] && state[k] !== 'all') {
          var vals = (it.getAttribute('data-' + k) || '').split('|');
          if (vals.indexOf(state[k]) < 0) ok = false;
        }
      }
      if (ok && q) ok = (it.getAttribute('data-text') || it.textContent).toLowerCase().indexOf(q) >= 0;
      it.hidden = !ok; if (ok) shown++;
    });
    if (count) count.textContent = shown + (shown === 1 ? ' item' : ' items');
    if (empty) empty.style.display = shown ? 'none' : 'block';
    var params = new URLSearchParams();
    for (var k2 in state) if (state[k2] && state[k2] !== 'all') params.set(k2, state[k2]);
    if (q) params.set('q', q);
    var qs = params.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }

  document.querySelectorAll('[data-filter]').forEach(function (b) {
    b.addEventListener('click', function () {
      var k = b.getAttribute('data-filter');
      state[k] = b.getAttribute('data-value');
      document.querySelectorAll('[data-filter="' + k + '"]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      apply();
    });
  });
  if (search) search.addEventListener('input', function () { q = search.value.trim().toLowerCase(); apply(); });

  // restore from URL (?theme=…&lang=…&q=…)
  var p = new URLSearchParams(location.search);
  p.forEach(function (v, k) {
    if (k === 'q' && search) { search.value = v; q = v.toLowerCase(); return; }
    var b = document.querySelector('[data-filter="' + k + '"][data-value="' + CSS.escape(v) + '"]');
    if (b) { state[k] = v; document.querySelectorAll('[data-filter="' + k + '"]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); }); }
  });
  apply();
})();
