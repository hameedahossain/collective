/* Hameeda Hossain — small progressive enhancements. Everything works without JS. */
(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // open the credits panel when linked to directly
  if (location.hash === '#credits') { var cr = document.getElementById('credits'); if (cr) cr.open = true; }

  // ── mobile nav ──
  var nt = document.querySelector('.nav-toggle'), nav = document.getElementById('site-nav');
  if (nt && nav) nt.addEventListener('click', function () { var o = nav.classList.toggle('open'); nt.setAttribute('aria-expanded', o ? 'true' : 'false'); });

  // ── copy citation ──
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var el = document.getElementById(b.getAttribute('data-copy')); if (!el) return;
      var done = function () { var o = b.textContent; b.textContent = 'Copied'; setTimeout(function () { b.textContent = o; }, 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText(el.innerText).then(done, function () {});
    });
  });

  // ── lightbox for photographs ──
  var lb = document.querySelector('.lightbox');
  if (lb) {
    var lbImg = lb.querySelector('img'), lbCap = lb.querySelector('figcaption'), lastFocus = null;
    var close = function () { lb.hidden = true; document.body.style.overflow = ''; if (lastFocus) lastFocus.focus(); };
    document.addEventListener('click', function (e) {
      var b = e.target.closest && e.target.closest('.g-open');
      if (!b) return;
      lastFocus = b;
      var up = location.pathname.indexOf('/writings/') >= 0 ? '../' : '';
      var src = b.getAttribute('data-full');
      lbImg.src = /^https?:/.test(src) ? src : up + src;
      lbImg.alt = (b.querySelector('img') || {}).alt || '';
      lbCap.textContent = b.getAttribute('data-caption') || '';
      lb.hidden = false; document.body.style.overflow = 'hidden';
      lb.querySelector('.lb-close').focus();
    });
    lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('lb-close')) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !lb.hidden) close(); });
  }

  // ── timeline ──
  var tl = document.querySelector('[data-timeline]');
  if (tl) {
    var events = Array.prototype.slice.call(tl.querySelectorAll('.tl-event'));
    var markers = Array.prototype.slice.call(tl.querySelectorAll('.tl-decade'));
    var on = { life: true, work: true, movement: true, history: true };
    function layout() {
      var side = 0;
      events.forEach(function (ev) {
        var show = on[ev.getAttribute('data-strand')];
        ev.hidden = !show;
        ev.classList.remove('right');
        if (show) { if (side % 2) ev.classList.add('right'); side++; }
      });
      markers.forEach(function (m) {
        var n = m.nextElementSibling, any = false;
        while (n && !n.classList.contains('tl-decade')) { if (!n.hidden) any = true; n = n.nextElementSibling; }
        m.hidden = !any;
      });
    }
    document.querySelectorAll('[data-strand-toggle]').forEach(function (b) {
      b.addEventListener('click', function () {
        var k = b.getAttribute('data-strand-toggle');
        var count = Object.keys(on).filter(function (x) { return on[x]; }).length;
        if (on[k] && count === 1) return; // keep at least one strand visible
        on[k] = !on[k]; b.setAttribute('aria-pressed', on[k] ? 'true' : 'false'); layout();
      });
    });
    layout();

    // reveal on scroll
    if (!reduce && 'IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
      }, { rootMargin: '0px 0px -8% 0px' });
      events.forEach(function (ev) { ev.classList.add('reveal'); io.observe(ev); });
    }

    // progress bar + active decade
    var bar = document.querySelector('.tl-progress span');
    var links = Array.prototype.slice.call(document.querySelectorAll('.tl-decades a'));
    var ticking = false;
    function onScroll() {
      ticking = false;
      var r = tl.getBoundingClientRect(), h = window.innerHeight;
      var p = Math.min(1, Math.max(0, (h * 0.5 - r.top) / r.height));
      if (bar) bar.style.width = (p * 100).toFixed(1) + '%';
      var cur = null;
      markers.forEach(function (m) { if (!m.hidden && m.getBoundingClientRect().top < 180) cur = m.id; });
      links.forEach(function (a) { a.classList.toggle('active', cur && a.getAttribute('href') === '#' + cur); });
    }
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
    onScroll();
  }

  // ── filterable lists ──
  var list = document.querySelector('[data-filter-list]');
  if (!list) return;
  var items = Array.prototype.slice.call(list.querySelectorAll('[data-item]'));
  var state = {}, q = '';
  var search = document.querySelector('[data-search]');
  var count = document.querySelector('[data-count]');
  var empty = document.querySelector('[data-empty]');
  function apply() {
    var shown = 0;
    items.forEach(function (it) {
      var ok = true;
      for (var k in state) {
        if (state[k] && state[k] !== 'all' && (it.getAttribute('data-' + k) || '').split('|').indexOf(state[k]) < 0) ok = false;
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
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
  }
  document.querySelectorAll('[data-filter]').forEach(function (b) {
    b.addEventListener('click', function () {
      var k = b.getAttribute('data-filter'); state[k] = b.getAttribute('data-value');
      document.querySelectorAll('[data-filter="' + k + '"]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      apply();
    });
  });
  if (search) search.addEventListener('input', function () { q = search.value.trim().toLowerCase(); apply(); });
  new URLSearchParams(location.search).forEach(function (v, k) {
    if (k === 'q' && search) { search.value = v; q = v.toLowerCase(); return; }
    var b = document.querySelector('[data-filter="' + k + '"][data-value="' + CSS.escape(v) + '"]');
    if (b) { state[k] = v; document.querySelectorAll('[data-filter="' + k + '"]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); }); }
  });
  apply();
})();
