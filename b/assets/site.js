/* カルラライブ site.js：配信画面のデモ、診断、フォーム、ツール体験、プレビュー用の切り替え */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  var PREVIEW = root.dataset.mode === 'preview';
  var REDUCED = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); }

  /* ---------- スマホのメニュー ---------- */
  var menuBtn = $('.menu-btn'), nav = $('.nav');
  function closeNav() { if (nav) { nav.classList.remove('is-open'); menuBtn.setAttribute('aria-expanded', 'false'); menuBtn.textContent = 'メニュー'; } }
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.textContent = open ? '閉じる' : 'メニュー';
    });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) closeNav(); });
  }

  /* ---------- 配信画面（スイッチャー） ---------- */
  var SPK = [520, 730, 940, 1150];
  var VB = { 2: '360 300 960 540', 3: '0 0 1600 900' };
  function closeVB(i) { return (SPK[i] - 200) + ' 400 400 225'; }
  var SHOT = { 1: ['CAM 1', '話している人のアップ'], 2: ['CAM 2', '登壇者全体'], 3: ['CAM 3', '会場全体'], s: ['SLIDE', '発表スライドと、話している人の顔'] };
  var CAP = {
    1: '話す人が替わるたびに、映像担当がカメラ1を向け直して切り替えます。表情まで届きます。',
    2: '掛け合いが続くときは、登壇者全体の画に切り替えます。誰と誰が話しているかがわかります。',
    3: '会の始まりや質疑のときは、会場全体の画を使います。',
    s: 'スライドの説明中は、スライドを大きく映して、話している人の顔を隅に出します。',
    one: 'カメラ1台だと、ずっとこの画です。誰が話しているのか、表情までは届きません。'
  };
  var SEQ = [[1, 0], [2, 0], [1, 2], ['s', 2], [1, 1], [3, 1], [1, 3], [2, 3]];
  var SUBS = ['それでは、パネルディスカッションを始めます。', '最初に、お一人ずつご意見を伺います。', '現場の立場から、少し補足させてください。', 'こちらのグラフをご覧ください。', 'その点は、私たちの調査でも同じ結果でした。', '会場の皆さんからも、ご質問を受け付けます。', '最後に、今後の課題を一つだけ挙げます。', '本日はありがとうございました。'];

  $$('[data-sw]').forEach(function (el) {
    var main = $('.sw-main', el), slide = $('.sw-slide', el), pip = $('.sw-pip', el), pipSvg = $('svg', pip);
    var shot = $('.sw-shot', el), cap = $('.sw-cap', el), sub = $('.sw-sub', el);
    var tiles = $$('.sw-tile', el), modeBtns = $$('.seg button', el);
    var cam1 = $('.sw-tile[data-src="1"] svg', el);
    var scene = doc.getElementById('scn');
    var cams = 3, step = 0, spk = 0, src = 1, timer = null, hold = 0, visible = false;

    function render() {
      if (scene) scene.setAttribute('class', 'spk-' + spk);
      cam1.setAttribute('viewBox', closeVB(spk));
      var s = cams === 1 ? 3 : src;
      var isSlide = s === 's';
      main.classList.toggle('is-hid', isSlide);
      slide.classList.toggle('is-hid', !isSlide);
      pip.hidden = !isSlide;
      if (isSlide) pipSvg.setAttribute('viewBox', closeVB(spk));
      else main.setAttribute('viewBox', s === 1 ? closeVB(spk) : VB[s]);
      shot.innerHTML = '<b>' + SHOT[s][0] + '</b>' + SHOT[s][1];
      cap.textContent = cams === 1 ? CAP.one : CAP[s];
      tiles.forEach(function (t) {
        var v = t.dataset.src;
        t.setAttribute('aria-pressed', String(String(s) === v));
        t.classList.toggle('is-off', cams === 1 && v !== '3');
      });
      if (sub) sub.textContent = SUBS[step % SUBS.length];
    }
    function next() {
      if (Date.now() < hold) { spk = (spk + 1) % 4; step++; render(); return; }
      step = (step + 1) % SEQ.length;
      src = SEQ[step][0]; spk = SEQ[step][1];
      render();
    }
    function run() {
      clearInterval(timer); timer = null;
      if (visible && !REDUCED && !doc.hidden) timer = setInterval(next, 3600);
    }
    tiles.forEach(function (t) {
      t.addEventListener('click', function () {
        var v = t.dataset.src;
        src = v === 's' ? 's' : Number(v);
        hold = Date.now() + 12000;
        render();
      });
    });
    modeBtns.forEach(function (b) {
      b.addEventListener('click', function () {
        cams = Number(b.dataset.cams);
        modeBtns.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        hold = 0;
        render();
      });
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; run(); }, { threshold: 0.2 }).observe(el);
    } else { visible = true; run(); }
    doc.addEventListener('visibilitychange', run);
    render();
  });

  /* ---------- フォーム ---------- */
  function go(page, fallbackUrl) {
    if (PREVIEW) location.hash = '#' + page; else location.href = fallbackUrl;
  }
  $$('form[data-form]').forEach(function (f) {
    var msg = $('.form-msg', f);
    f.setAttribute('novalidate', '');
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var firstErr = null;
      $$('.field', f).forEach(function (fd) {
        var inp = $('input[data-req],textarea[data-req]', fd);
        if (!inp) return;
        var v = inp.value.trim(), bad = !v;
        if (!bad && inp.type === 'email') bad = !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
        fd.classList.toggle('is-err', bad);
        inp.setAttribute('aria-invalid', String(bad));
        if (bad && !firstErr) firstErr = inp;
      });
      if (firstErr) { firstErr.focus(); return; }
      var endpoint = f.dataset.endpoint, kind = f.dataset.form;
      if (!endpoint) {
        /* 送信先が未設定。見本として次の画面だけ見せる（何も送信しない） */
        if (kind === 'quote') go('thanks', f.dataset.thanks);
        else if (msg) { msg.hidden = false; msg.textContent = 'この見本サイトでは、まだ何も送信されません。公開時に送信先を設定すると、入力したアドレスにひな形が届くようになります。'; }
        return;
      }
      var data = {};
      new FormData(f).forEach(function (v, k) { data[k] = data[k] ? data[k] + '、' + v : v; });
      var btn = $('button[type=submit]', f); btn.disabled = true;
      fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); if (kind === 'quote') location.href = f.dataset.thanks; else if (msg) { msg.hidden = false; msg.textContent = '送信しました。メールをご確認ください。'; } })
        .catch(function () { btn.disabled = false; if (msg) { msg.hidden = false; msg.textContent = '送信できませんでした。時間をおいてもう一度お試しいただくか、お電話でご連絡ください。'; } });
    });
  });

  /* ---------- iPhone診断 ---------- */
  var WHY = [
    '登壇者が複数いると、話す人に合わせてカメラを切り替える必要があります。',
    '会場でスピーカーを使うと、ハウリングや音の回り込みが起きやすくなります。',
    '会場の質問をオンラインに届けるには、質問用のマイクと音の経路の設計が必要です。',
    '2時間を超えると、バッテリーや回線を見張る専任の人が必要になります。',
    'アーカイブを公開するなら、予備の録画と聞き取りやすい音が欠かせません。',
    '学外の視聴者や来賓がいる会は、止まったときの備えが必要です。'
  ];
  $$('.quiz').forEach(function (q) {
    var items = $$('ol li', q), res = $('.quiz-res', q), warn = $('.quiz-warn', q);
    $('.quiz-go', q).addEventListener('click', function () {
      var ans = items.map(function (li) { var c = $('input:checked', li); return c ? c.value : null; });
      if (ans.indexOf(null) > -1) { warn.hidden = false; items[ans.indexOf(null)].querySelector('input').focus(); return; }
      warn.hidden = true;
      var y = ans.map(function (a) { return a === 'y'; });
      var c = y.filter(Boolean).length;
      var kind = (c >= 4 || (y[0] && (y[2] || y[5]))) ? 'order' : (c >= 2 ? 'consult' : 'self');
      $$('[data-res]', res).forEach(function (d) { d.hidden = d.dataset.res !== kind; });
      var ul = $('.quiz-why', res); ul.innerHTML = '';
      y.forEach(function (v, i) { if (v) { var li = doc.createElement('li'); li.textContent = WHY[i]; ul.appendChild(li); } });
      $('.quiz-why-h', res).hidden = c === 0;
      res.hidden = false;
      res.focus();
    });
  });

  /* ---------- QA Board 体験 ---------- */
  $$('.qa').forEach(function (qa) {
    var list = $('.qa-list', qa), scr = $('.qa-screen', qa), form = $('form', qa), inp = $('input', qa);
    function bind(li) {
      $('button', li).addEventListener('click', function () {
        var on = li.classList.contains('is-on');
        $$('li', list).forEach(function (x) { x.classList.remove('is-on'); $('button', x).textContent = '表示する'; });
        if (on) { scr.innerHTML = '<p class="is-empty">選んだ質問だけが、ここに表示されます</p>'; return; }
        li.classList.add('is-on'); $('button', li).textContent = '表示中';
        scr.innerHTML = ''; var p = doc.createElement('p'), s = doc.createElement('small');
        s.textContent = $('small', li).textContent + 'からの質問'; p.appendChild(s);
        p.appendChild(doc.createTextNode($('span', li).textContent)); scr.appendChild(p);
      });
    }
    $$('li', list).forEach(bind);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = inp.value.trim(); if (!v) { inp.focus(); return; }
      var li = doc.createElement('li'), d = doc.createElement('div'), s = doc.createElement('small'), sp = doc.createElement('span'), b = doc.createElement('button');
      s.textContent = 'オンライン'; sp.textContent = v.slice(0, 80); b.type = 'button'; b.textContent = '表示する';
      d.appendChild(s); d.appendChild(sp); li.appendChild(d); li.appendChild(b);
      list.insertBefore(li, list.firstChild); bind(li); inp.value = '';
    });
  });

  /* ---------- Que 体験 ---------- */
  $$('.que').forEach(function (q) {
    var scr = $('.phone-in', q), time = $('.n', scr), cue = $('p', scr), left = 300, t = null, cueT = null;
    function fmt(s) { return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2); }
    function draw() { time.textContent = fmt(left); }
    function tick() { if (left > 0) { left--; draw(); } else stop(); }
    function stop() { clearInterval(t); t = null; $('[data-que=start]', q).textContent = 'スタート'; }
    $$('[data-que]', q).forEach(function (b) {
      b.addEventListener('click', function () {
        var k = b.dataset.que;
        if (k === 'start') { if (t) stop(); else { if (left === 0) left = 300; t = setInterval(tick, 1000); b.textContent = '一時停止'; } draw(); }
        else if (k === 'reset') { stop(); left = 300; draw(); cue.textContent = ''; scr.classList.remove('is-cue'); }
        else { cue.textContent = b.textContent; scr.classList.add('is-cue'); clearTimeout(cueT); cueT = setTimeout(function () { scr.classList.remove('is-cue'); }, 4000); }
      });
    });
    draw();
  });

  /* ---------- まだ用意していないファイル ---------- */
  doc.addEventListener('click', function (e) {
    var a = e.target.closest('a[data-todo]');
    if (!a) return;
    e.preventDefault();
    var n = a.parentNode.querySelector('.todo-msg');
    if (!n) { n = doc.createElement('span'); n.className = 'note todo-msg'; n.setAttribute('role', 'status'); a.parentNode.appendChild(n); }
    n.textContent = '「' + a.dataset.todo + '」は、まだこのサイトに置いていません。ファイルを用意すると、ここから開けます。';
  });


  /* ---------- 出現の動き（rondo テーマのときだけ） ---------- */
  if (root.dataset.theme === 'rondo' && !REDUCED && 'IntersectionObserver' in window) {
    root.classList.add('js-anim');
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -6% 0px' });
    var splitText = function (h) {
      var n = 0, walk = function (node) {
        Array.prototype.slice.call(node.childNodes).forEach(function (c) {
          if (c.nodeType === 3) {
            var f = doc.createDocumentFragment();
            c.textContent.split('').forEach(function (ch) {
              if (/\s/.test(ch)) { f.appendChild(doc.createTextNode(ch)); return; }
              var s = doc.createElement('span'); s.className = 'w'; s.textContent = ch; s.style.animationDelay = (n++ * 25) + 'ms'; f.appendChild(s);
            });
            node.replaceChild(f, c);
          } else if (c.nodeType === 1 && c.tagName !== 'BR') walk(c);
        });
      };
      h.setAttribute('aria-label', h.textContent.replace(/\s+/g, ' ').trim());
      walk(h);
    };
    $$('.hero h1, .ph h1, .h2, .cta h2').forEach(function (h) { splitText(h); h.setAttribute('data-rv', 'w'); io.observe(h); });
    $$('.sec-body, .hero .sw, .strip, .lead, .last .qform').forEach(function (el) { el.setAttribute('data-rv', 'fade'); io.observe(el); });
  }

  /* ---------- プレビュー（1ファイルの中でページを切り替える） ---------- */
  if (PREVIEW) {
    var mains = $$('main[data-page]'), want = null, mbar = $('.mbar');
    var scrollToAnchor = function (m, a) {
      var t = a && m.querySelector('[id="' + a + '"]');
      var y = t ? t.getBoundingClientRect().top + window.pageYOffset - 76 : 0;
      try { window.scrollTo({ top: y, behavior: 'instant' }); } catch (e) { window.scrollTo(0, y); }
    };
    var show = function () {
      var id = (location.hash || '#home').slice(1);
      var m = mains.filter(function (x) { return x.dataset.page === id; })[0] || mains[0];
      mains.forEach(function (x) { x.classList.toggle('is-active', x === m); });
      doc.title = m.dataset.title;
      $$('.nav a').forEach(function (a) { if (a.dataset.nav === m.dataset.page) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
      if (mbar) mbar.classList.toggle('is-off', m.hasAttribute('data-nobar'));
      closeNav();
      var a = want; want = null;
      setTimeout(function () { scrollToAnchor(m, a); }, 0);
    };
    doc.addEventListener('click', function (e) {
      var a = e.target.closest('a[href^="#"]');
      if (!a || a.hasAttribute('data-todo')) return;
      var id = a.getAttribute('href').slice(1) || 'home';
      want = a.dataset.a || null;
      var cur = (location.hash || '#home').slice(1);
      if (id === cur) { e.preventDefault(); show(); }
    });
    window.addEventListener('hashchange', show);
    show();
  }
})();
