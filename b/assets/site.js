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

  /* ---------- プラン診断 ---------- */
  var LABEL = {
    spk: { '1': '1人', '2-3': '2〜3人', '4-6': '4〜6人', '7+': '7人以上' },
    aud: { '-30': '30人まで', '30-100': '30〜100人', '100-300': '100〜300人', '300+': '300人以上' },
    rmt: { y: 'いる', n: 'いない' }, qa: { y: '届けたい', n: '会場だけ' },
    time: { '-2': '2時間まで', '2-3': '2〜3時間', '3+': '3時間を超える' }, pub: { y: 'ある', n: 'ない' },
    opt: { photo: '記録写真', edit: '記録映像の編集', digest: 'ダイジェスト映像', text: '文字起こし' }, self: { y: 'はい', n: 'いいえ' }
  };
  var PREFILL_KEY = 'karura-plan';
  var memo = null;
  function saveMemo(m) { memo = m; try { sessionStorage.setItem(PREFILL_KEY, JSON.stringify(m)); } catch (e) {} }
  function loadMemo() { if (memo) return memo; try { return JSON.parse(sessionStorage.getItem(PREFILL_KEY) || 'null'); } catch (e) { return null; } }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function href(page, anchor) {
    if (PREVIEW) return '#' + page + (anchor ? '" data-a="' + anchor : '');
    var p = { home: '/', price: '/price/', coaching: '/coaching/', contact: '/contact/', 'iphone-streaming': '/articles/iphone-streaming/' }[page];
    return p + (anchor ? '#' + anchor : '');
  }

  function judge(a) {
    var opts = a.opt || [], adds = [], why = [];
    var big = a.spk === '7+' || a.aud === '300+';
    var need = (a.spk !== '1' ? 2 : 0) + (a.spk === '4-6' ? 1 : 0) + (a.aud === '100-300' ? 1 : 0) + (a.qa === 'y' ? 2 : 0) +
      (a.time !== '-2' ? 1 : 0) + (a.pub === 'y' ? 2 : 0) + (a.rmt === 'y' ? 2 : 0);
    if (a.spk !== '1') why.push('登壇者が' + LABEL.spk[a.spk] + 'いるので、話す人に合わせてカメラを切り替える必要があります');
    if (a.qa === 'y') why.push('会場の質問をオンラインに届けるには、質問用のマイクと音の経路の設計が必要です');
    if (a.rmt === 'y') why.push('オンラインから登壇する人がいると、会場とオンラインの声を行き来させる担当が要ります');
    if (a.pub === 'y') why.push('録画の公開や学外の視聴者がある会は、やり直しがききません。予備の録画と回線を用意します');
    if (a.time !== '-2') why.push('配信が' + LABEL.time[a.time] + 'と長いので、機材と回線を見張り続ける人が必要です');
    var r = { adds: adds, why: why, cta: 'quote' };
    if (big) {
      r.key = 'big'; r.plan = '大手の制作会社をおすすめします'; r.price = null;
      r.lead = (a.spk === '7+' ? '登壇者が7人以上' : '会場が300人以上') + 'の会は、カメラ3台・スタッフ2名の私たちの体制より大きな会です。無理にお引き受けするより、大手の制作会社に頼んだほうが安心です。';
      r.cta = 'consult';
    } else if (need <= 1 && a.aud !== '100-300') {
      r.key = 'self'; r.plan = 'iPhoneで足ります'; r.price = ['0', '円'];
      r.lead = 'この条件なら、ご自身で配信できます。業者に頼む必要はありません。iPhoneと外付けマイク1本で始められます。';
      r.cta = 'self'; r.why = ['登壇者が1人で、質疑を配信に乗せない会は、カメラ1台で十分に伝わります'];
    } else if (need <= 3) {
      r.key = 'consult'; r.plan = '配信コーチング：相談'; r.price = ['［3］', '万円（税別）'];
      r.lead = '機材と接続を一度整理すれば、ご自身で配信できる可能性が高い会です。オンライン60分で、接続の図と当日のチェックリストを作成します。';
      r.cta = 'coaching';
    } else {
      var maru = opts.length >= 2;
      r.key = maru ? 'marugoto' : 'standard';
      r.plan = maru ? 'まるごと' : 'スタンダード';
      r.price = maru ? ['［40］', '万円（税別）'] : ['25', '万円（税別）'];
      r.lead = maru ? 'スタンダードに、記録写真・記録映像の編集・ダイジェスト・文字起こしを加えて、スタッフ3名で伺います。一回の現場で、報告書の素材まで揃います。'
        : 'カメラ3台・スタッフ2名・マイク5本の基本プランが合う会です。事前の打ち合わせ、会場の下見、録画データの納品まで含みます。';
      var mics = { '2-3': 3, '4-6': 6 }[a.spk] + (a.qa === 'y' ? 1 : 0);
      var addStaff = a.rmt === 'y' || mics > 5;
      if (addStaff) adds.push(['スタッフを1名追加', a.rmt === 'y' ? 'オンラインから登壇する人がいるため' : 'マイクが' + mics + '本必要になるため']);
      if (a.time === '3+') adds.push(['配信時間の延長', '3時間を超える分']);
      if (!maru && opts.length === 1) adds.push([LABEL.opt[opts[0]], '同じ日にまとめて依頼']);
      if (a.self === 'y') adds.push(['コーチング：同行', '私たちの配信を横で見て、次の会から自分たちで回せるように']);
      r.staff = (maru ? 3 : 2) + (addStaff ? 1 : 0);
      r.mics = Math.min(mics, addStaff ? 8 : 5);
    }
    if (r.key === 'self' && a.self === 'n') r.lead += ' 当日だけ不安な場合は、コーチングの「相談」もご利用いただけます。';
    return r;
  }

  function resultHtml(r, a) {
    var h = '<p class="dg-res-k">あなたの会に合うのは</p><h3 class="dg-res-plan">' + esc(r.plan) + '</h3>';
    if (r.price) h += '<p class="dg-res-price">' + (r.price[0].indexOf('［') > -1 ? '<span class="ana dg-res-ana">' + r.price[0] + r.price[1] + '</span>' : '<b class="n">' + r.price[0] + '</b>' + r.price[1]) + (r.adds.length ? '<small>　＋追加料金</small>' : '') + '</p>';
    h += '<p class="dg-res-lead">' + esc(r.lead) + '</p>';
    if (r.staff) {
      h += '<dl class="dg-sum"><div><dt>当日の体制</dt><dd>スタッフ' + r.staff + '名・カメラ3台・マイク' + r.mics + '本</dd></div>';
      r.adds.forEach(function (x) { h += '<div><dt>追加</dt><dd>' + esc(x[0]) + '　<span class="ana">［金額］</span><small>' + esc(x[1]) + '</small></dd></div>'; });
      h += '</dl>';
    }
    if (r.why.length) h += '<p class="h4">こう判断した理由</p><ul class="ticks">' + r.why.map(function (w) { return '<li>' + esc(w) + '</li>'; }).join('') + '</ul>';
    var b = '<div class="btns">';
    if (r.cta === 'quote') b += '<a class="btn" href="' + href('contact') + '" data-prefill>この内容で見積書を受け取る</a><a class="btn btn--ghost" href="' + href('price') + '">料金の内訳を見る</a>';
    else if (r.cta === 'coaching') b += '<a class="btn" href="' + href('contact') + '" data-prefill>この内容で相談する</a><a class="btn btn--ghost" href="' + href('coaching') + '">コーチングを詳しく見る</a>';
    else if (r.cta === 'self') b += '<a class="btn" href="' + href('iphone-streaming') + '">自分で配信するときの機材と注意点</a><a class="btn btn--ghost" href="' + href('contact', 'consult') + '">念のため相談する</a>';
    else b += '<a class="btn" href="' + href('contact', 'consult') + '">15分のオンライン相談で確かめる</a>';
    h += b + '</div><button type="button" class="dg-again">最初から診断しなおす</button>';
    return h;
  }

  $$('[data-dg]').forEach(function (dg) {
    var qs = $$('.dg-q', dg), res = $('.dg-res', dg), bar = $('.dg-prog i', dg), num = $('.dg-i', dg), back = $('.dg-back', dg);
    var cur = 0, answers = {}, lastResult = null;
    function show(i, focus) {
      cur = i;
      qs.forEach(function (q, k) { q.classList.toggle('is-cur', k === i); });
      bar.style.width = ((i + 1) / qs.length * 100) + '%';
      num.textContent = i + 1;
      back.hidden = i === 0;
      if (focus) { var f = $('input:checked', qs[i]) || $('input', qs[i]); if (f) f.focus({ preventScroll: true }); }
    }
    function read(q) {
      var key = q.dataset.key;
      if (q.hasAttribute('data-multi')) return $$('input:checked', q).map(function (x) { return x.value; });
      var c = $('input:checked', q); return c ? c.value : null;
    }
    function next() {
      answers[qs[cur].dataset.key] = read(qs[cur]);
      if (cur < qs.length - 1) { show(cur + 1, true); return; }
      lastResult = judge(answers);
      res.innerHTML = resultHtml(lastResult, answers);
      res.hidden = false; dg.classList.add('is-done');
      var top = dg.getBoundingClientRect().top + window.pageYOffset - offset();
      if (dg.getBoundingClientRect().top < offset()) window.scrollTo(0, top);
      res.focus({ preventScroll: true });
      var m = { plan: lastResult.plan, key: lastResult.key, lines: [] };
      DIAG_ORDER.forEach(function (k) {
        var v = answers[k]; if (v == null) return;
        var t = Array.isArray(v) ? (v.length ? v.map(function (x) { return LABEL.opt[x]; }).join('、') : 'なし') : LABEL[k][v];
        m.lines.push(QTEXT[k] + '：' + t);
      });
      lastResult.adds.forEach(function (x) { m.lines.push('追加：' + x[0]); });
      saveMemo(m);
    }
    var DIAG_ORDER = qs.map(function (q) { return q.dataset.key; });
    var QTEXT = { spk: '登壇者', aud: '会場の人数', rmt: 'オンライン登壇', qa: '会場の質問をオンラインへ', time: '配信時間', pub: '録画公開・学外の視聴者', opt: '同じ日に頼みたいもの', self: '来年度から自分たちで' };
    qs.forEach(function (q) {
      if (q.hasAttribute('data-multi')) $('.dg-next', q).addEventListener('click', next);
      else $$('input', q).forEach(function (inp) {
        inp.addEventListener('click', function () { setTimeout(next, REDUCED ? 0 : 220); });
      });
    });
    back.addEventListener('click', function () { if (cur > 0) show(cur - 1, true); });
    res.addEventListener('click', function (e) {
      if (e.target.closest('.dg-again')) {
        $$('input', dg).forEach(function (x) { x.checked = false; });
        answers = {}; res.hidden = true; dg.classList.remove('is-done'); show(0, true);
      }
    });
    show(0, false);
  });

  /* ---------- 診断の結果を見積フォームに入れる ---------- */
  function applyPrefill() {
    var m = loadMemo(); if (!m) return;
    $$('form[data-form=quote]').forEach(function (f) {
      var ta = $('textarea', f); if (!ta || f.dataset.filled === m.plan + m.lines.length) return;
      f.dataset.filled = m.plan + m.lines.length;
      ta.value = '【プラン診断の結果】おすすめ：' + m.plan + '\n' + m.lines.join('\n') + (ta.value ? '\n\n' + ta.value : '');
      var map = { standard: 'スタンダード', marugoto: 'まるごと', consult: 'コーチング', self: 'まだわからない', big: 'まだわからない' };
      $$('input[type=checkbox]', f).forEach(function (c) { if (c.value.indexOf(map[m.key]) === 0) c.checked = true; });
      if (!$('.prefill', f)) {
        var p = doc.createElement('p'); p.className = 'prefill'; p.setAttribute('role', 'status');
        p.textContent = 'プラン診断の結果（' + m.plan + '）を、下の「気になっていること」欄に入れておきました。必須の4項目だけ入力して送信できます。';
        f.insertBefore(p, f.firstChild.nextSibling);
      }
    });
  }
  applyPrefill();
  doc.addEventListener('karura:page', applyPrefill);

  /* ---------- サブナビ（現在地） ---------- */
  function offset() {
    var h = $('.head'), s = $$('.subnav').filter(function (x) { return x.offsetParent; })[0];
    return (h ? h.offsetHeight : 0) + (s ? s.offsetHeight : 0) + 8;
  }
  function jump(el) {
    var y = el.getBoundingClientRect().top + window.pageYOffset - offset() + 1;
    try { window.scrollTo({ top: y, behavior: REDUCED ? 'auto' : 'smooth' }); } catch (e) { window.scrollTo(0, y); }
  }
  var subs = $$('.subnav').map(function (nav) {
    var links = $$('a[data-sub]', nav), ol = $('ol', nav);
    var prog = doc.createElement('span'); prog.className = 'subnav-prog'; nav.appendChild(prog);
    links.forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        var main = nav.closest('main') || doc;
        var t = main.querySelector('[id="' + a.dataset.sub + '"]'); if (t) jump(t);
      });
    });
    return { nav: nav, links: links, ol: ol, prog: prog, last: null };
  });
  function spy() {
    subs.forEach(function (s) {
      if (!s.nav.offsetParent) return;
      var main = s.nav.closest('main') || doc, line = offset() + 4, curA = null;
      s.links.forEach(function (a) {
        var t = main.querySelector('[id="' + a.dataset.sub + '"]');
        if (t && t.getBoundingClientRect().top <= line) curA = a;
      });
      var end = window.innerHeight + window.pageYOffset >= doc.documentElement.scrollHeight - 4;
      if (end) curA = s.links[s.links.length - 1];
      if (curA !== s.last) {
        s.links.forEach(function (a) { if (a === curA) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
        s.last = curA;
        if (curA) {
          var li = curA.parentNode, ol = s.ol;
          var want = li.offsetLeft - (ol.clientWidth - li.offsetWidth) / 2;
          try { ol.scrollTo({ left: want, behavior: REDUCED ? 'auto' : 'smooth' }); } catch (e) { ol.scrollLeft = want; }
        }
      }
      var r = main.getBoundingClientRect ? main.getBoundingClientRect() : null;
      var total = doc.documentElement.scrollHeight - window.innerHeight;
      s.prog.style.width = (total > 0 ? Math.min(100, window.pageYOffset / total * 100) : 0) + '%';
    });
  }
  var ticking = false;
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; spy(); }); } }, { passive: true });
  window.addEventListener('resize', spy);
  doc.addEventListener('karura:page', function () { subs.forEach(function (s) { s.last = null; }); spy(); });
  spy();

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
      var y = t ? t.getBoundingClientRect().top + window.pageYOffset - offset() : 0;
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
      setTimeout(function () { scrollToAnchor(m, a); doc.dispatchEvent(new Event('karura:page')); }, 0);
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
