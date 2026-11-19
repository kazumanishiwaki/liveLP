/* カルラライブ site.js
   標準の HTML/CSS で足りないところだけを補う。どれも無くても、内容は読めて、リンクとフォームは使える。
   1. スマホのメニュー（dialog.showModal と背景クリックで閉じる）
   2. カメラ切り替えの自動送り（切り替え自体はラジオと :has で動く）
   3. プラン診断（1問ずつ表示と判定。どのページからでもモーダルで開く）
   4. メニューの現在地（トップの中の項目だけ、スクロール位置から計算）と、要点のマーカー
   5. フォームの送信（送信先が決まるまでは完了ページの見本へ）と、診断結果の引き継ぎ */

const $ = (s, c = document) => c.querySelector(s);
const $$ = (s, c = document) => [...c.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const pc = matchMedia('(width >= 64rem)');

/* ------------------------------------------------ 1. スマホのメニュー */
{
  const dlg = $('#menu');
  const open = $('[data-open-menu]');
  if (dlg && open) {
    open.addEventListener('click', () => dlg.showModal());
    // 背景（dialog 自身）を押したら閉じる。closedby="any" は Baseline 未満なので自前で
    // メニュー内のページ内リンクも、閉じてから移動する
    dlg.addEventListener('click', (e) => {
      if (e.target === dlg || e.target.closest('a[href^="#"]')) dlg.close();
    });
    // 診断のモーダルを続けて開くときは、そちらにフォーカスを渡す
    dlg.addEventListener('close', () => { if (!$('#diag-modal')?.open) open.focus(); });
  }
}

/* ------------------------------------------------ 2. カメラの自動送り */
{
  const sw = $('[data-sw]');
  if (sw) {
    const radios = $$('input[name="cam"]', sw);
    const btn = $('.sw-pause', sw);
    let timer = 0, paused = reduce.matches, visible = false;
    const step = () => {
      const i = radios.findIndex((r) => r.checked);
      radios[(i + 1) % radios.length].checked = true;
    };
    const run = () => {
      clearInterval(timer);
      if (!paused && visible && !document.hidden) timer = setInterval(step, 5000);
    };
    const label = () => {
      btn.textContent = paused ? '自動で切り替える' : '切り替えを止める';
      btn.setAttribute('aria-pressed', String(paused));
    };
    btn.hidden = false;
    btn.addEventListener('click', () => { paused = !paused; label(); run(); });
    // 自分で選んだら、そこから数え直す
    radios.forEach((r) => r.addEventListener('change', run));
    // 見えているときだけ動かす
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; run(); }, { threshold: 0.3 }).observe(sw);
    document.addEventListener('visibilitychange', run);
    reduce.addEventListener('change', () => { paused = reduce.matches; label(); run(); });
    label();
  }
}

/* ------------------------------------------------ 3. プラン診断 */
const LABEL = {
  spk: { '1': '1人', '2-3': '2〜3人', '4-6': '4〜6人', '7+': '7人以上' },
  aud: { '-30': '30人まで', '30-100': '30〜100人', '100-300': '100〜300人', '300+': '300人以上' },
  rmt: { y: 'いる', n: 'いない' },
  qa: { y: '届けたい', n: '会場だけ' },
  time: { '-2': '2時間まで', '2-3': '2〜3時間', '3+': '3時間を超える' },
  pub: { y: 'ある', n: 'ない' },
  opt: { photo: '記録写真', edit: '記録映像の編集', digest: 'ダイジェスト映像', text: '文字起こし' },
  self: { y: 'はい', n: 'いいえ' },
};
const QTEXT = { spk: '登壇者', aud: '会場の人数', rmt: 'オンライン登壇', qa: '会場の質問をオンラインへ', time: '配信時間', pub: '録画公開・学外の視聴者', opt: '同じ日に頼みたいもの', self: '来年度から自分たちで' };
const STORE = 'karura-plan';

function judge(a) {
  const opts = a.opt || [];
  const adds = [];
  const why = [];
  const big = a.spk === '7+' || a.aud === '300+';
  const need = (a.spk !== '1' ? 2 : 0) + (a.spk === '4-6' ? 1 : 0) + (a.aud === '100-300' ? 1 : 0) +
    (a.qa === 'y' ? 2 : 0) + (a.time !== '-2' ? 1 : 0) + (a.pub === 'y' ? 2 : 0) + (a.rmt === 'y' ? 2 : 0);
  if (a.spk !== '1') why.push(`登壇者が${LABEL.spk[a.spk]}いるので、話す人に合わせてカメラを切り替える必要があります`);
  if (a.qa === 'y') why.push('会場の質問をオンラインに届けるには、質問用のマイクと音の経路の設計が必要です');
  if (a.rmt === 'y') why.push('オンラインから登壇する人がいると、会場とオンラインの声を行き来させる担当が要ります');
  if (a.pub === 'y') why.push('録画の公開や学外の視聴者がある会は、やり直しがききません。予備の録画と回線を用意します');
  if (a.time !== '-2') why.push(`配信が${LABEL.time[a.time]}と長いので、機材と回線を見張り続ける人が必要です`);

  const mics = ({ '1': 1, '2-3': 3, '4-6': 6, '7+': 8 })[a.spk] + (a.qa === 'y' ? 1 : 0);
  if (!big && need <= 1 && a.aud !== '100-300') {
    return { key: 'self', plan: 'iPhoneで足ります', price: ['0', '円'], adds, cta: 'self',
      why: ['登壇者が1人で、質疑を配信に乗せない会は、カメラ1台で十分に伝わります'],
      lead: 'この条件なら、ご自身で配信できます。業者に頼む必要はありません。iPhoneと外付けマイク1本で始められます。' };
  }
  if (!big && need <= 3) {
    return { key: 'consult', plan: '内製化支援：相談', price: ['［3］', '万円（税別）'], adds, why, cta: 'quote',
      lead: '機材と接続を一度整理すれば、ご自身で配信できる可能性が高い会です。オンライン60分で、接続の図と当日のチェックリストを作成します。' };
  }
  if (big) why.unshift(`${a.spk === '7+' ? '登壇者が7人以上' : '会場が300人を超える'}ので、カメラ5台で登壇者と会場を撮り分けます`);
  const addStaff = !big && (a.rmt === 'y' || mics > 5);
  if (addStaff) adds.push(['スタッフを1人追加', a.rmt === 'y' ? 'オンラインから登壇する人がいるため' : `マイクが${mics}本必要になるため`]);
  if (a.time === '3+') adds.push(['配信時間の延長', '3時間を超える分']);
  opts.forEach((o) => adds.push([LABEL.opt[o], 'オプション：同じ日にまとめて依頼']));
  if (a.self === 'y') adds.push(['内製化支援：同行', '私たちの配信を横で見て、次の会から自分たちで回せるように']);
  return big
    ? { key: 'wide', plan: 'ワイド', price: ['35', '万円（税別）'], adds, why, cta: 'quote',
        lead: 'カメラ5台・スタッフ4人のプランが合う会です。登壇者が多い会や、広い会場の様子も届けたい会に向いています。',
        staff: 4, cams: 5, mics: ['［本数］'] }
    : { key: 'standard', plan: 'スタンダード', price: ['25', '万円（税別）'], adds, why, cta: 'quote',
        lead: 'カメラ3台・スタッフ3人・マイク5本の基本プランが合う会です。事前の打ち合わせと、会場のオンライン下見を含みます。',
        staff: 3 + (addStaff ? 1 : 0), cams: 3, mics: [String(Math.min(mics, addStaff ? 8 : 5)), '本'] };
}

/* 結果は DOM を組み立てて入れる（innerHTML に利用者の入力は入れない） */
function el(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  for (const k of kids.flat()) if (k != null) n.append(k);
  return n;
}
/* 見積ボタンの封筒アイコン（ページのボタンと同じ形） */
function mailIcon() {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  for (const [k, v] of Object.entries({ class: 'bico', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.8', 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'aria-hidden': 'true' })) svg.setAttribute(k, v);
  const rect = document.createElementNS(ns, 'rect');
  for (const [k, v] of Object.entries({ x: '3', y: '5', width: '18', height: '14', rx: '2' })) rect.setAttribute(k, v);
  const path = document.createElementNS(ns, 'path');
  path.setAttribute('d', 'M3.5 6.5 12 13l8.5-6.5');
  svg.append(rect, path);
  return svg;
}
function priceNode(p, hasAdds) {
  const isHole = p[0].includes('［');
  return el('p', { class: 'dg-res-price' },
    isHole ? el('span', { class: 'ana' }, p[0] + p[1]) : p[0],
    isHole ? null : el('small', {}, p[1]),
    hasAdds ? el('small', {}, '＋追加料金') : null);
}
function renderResult(box, r) {
  const parts = [
    el('p', { class: 't-note t-sub' }, 'あなたの会に合うのは'),
    el('h3', { class: 'dg-res-plan', id: 'dg-result-title' }, r.plan),
    r.price ? priceNode(r.price, r.adds.length > 0) : null,
    el('p', { class: 't-body' }, r.lead),
  ];
  if (r.staff) {
    const micText = r.mics[1] ? `${r.mics[0]}${r.mics[1]}` : r.mics[0];
    const dl = el('dl', { class: 'dg-sum' }, el('div', {}, el('dt', {}, '当日の体制'), el('dd', {}, `スタッフ${r.staff}人・カメラ${r.cams}台・マイク${micText}`)));
    r.adds.forEach(([t, d]) => dl.append(el('div', {}, el('dt', {}, '追加'), el('dd', {}, t, '　', el('span', { class: 'ana' }, '［金額］'), el('small', {}, d)))));
    parts.push(dl);
  }
  if (r.why.length) parts.push(el('p', { class: 't-note' }, 'こう判断した理由'), el('ul', { class: 'dg-why' }, r.why.map((w) => el('li', {}, w))));
  const btns = el('div', { class: 'btns' });
  if (r.cta === 'quote') btns.append(el('a', { class: 'btn quote', href: 'contact.html' }, mailIcon(), el('span', {}, 'この内容で見積書を受け取る')), el('a', { class: 'btn line', href: 'index.html#price' }, '料金プランを見る'));
  else if (r.cta === 'self') btns.append(el('a', { class: 'btn', href: 'contact.html#consult' }, '念のため相談する'));
  else btns.append(el('a', { class: 'btn', href: 'contact.html#consult' }, '15分のオンライン相談で確かめる'));
  parts.push(btns, el('button', { type: 'button', class: 'btn sq s dg-again' }, '最初から診断しなおす'));
  box.replaceChildren(...parts);
}

$$('[data-dg]').forEach((dg) => {
  const form = $('.dg-form', dg);
  const qs = $$('.dg-q', dg);
  const res = $('.dg-res', dg);
  const back = $('.dg-back', dg);
  const num = $('.dg-i', dg);
  const prog = $('.dg-prog', dg);
  const live = $('.dg-live', dg);
  const nextBtn = $('.dg-next', dg);
  let cur = 0;
  let pointer = false;

  const show = (i, focus) => {
    cur = i;
    qs.forEach((q, k) => q.classList.toggle('is-cur', k === i));
    num.textContent = i + 1;
    prog.style.setProperty('--p', (i + 1) / qs.length);
    back.hidden = i === 0;
    live.textContent = `質問 ${i + 1} / ${qs.length}`;
    nextBtn.textContent = i === qs.length - 1 ? '結果を見る' : '次へ';
    if (focus) ($('input:checked', qs[i]) || $('input', qs[i])).focus({ preventScroll: true });
  };
  const answers = () => {
    const fd = new FormData(form);
    const a = {};
    qs.forEach((q) => {
      const k = q.dataset.key;
      a[k] = q.hasAttribute('data-multi') ? fd.getAll(k) : fd.get(k);
    });
    return a;
  };
  const finish = () => {
    const a = answers();
    const r = judge(a);
    renderResult(res, r);
    dg.classList.add('is-done');
    res.focus({ preventScroll: true });
    if (dg.getBoundingClientRect().top < 0) dg.scrollIntoView({ block: 'start', behavior: reduce.matches ? 'auto' : 'smooth' });
    const lines = Object.keys(QTEXT).filter((k) => a[k] != null).map((k) =>
      `${QTEXT[k]}：${Array.isArray(a[k]) ? (a[k].length ? a[k].map((x) => LABEL.opt[x]).join('、') : 'なし') : LABEL[k][a[k]]}`);
    r.adds.forEach(([t]) => lines.push(`追加：${t}`));
    try { sessionStorage.setItem(STORE, JSON.stringify({ plan: r.plan, key: r.key, lines })); } catch {}
  };
  const next = () => {
    const q = qs[cur];
    if (!q.hasAttribute('data-multi') && !$('input:checked', q)) { $('input', q).focus(); return; }
    if (cur < qs.length - 1) show(cur + 1, true); else finish();
  };

  // 指やマウスで選んだときだけ自動で次へ。キーボードの矢印で選んでいる途中では進めない
  form.addEventListener('pointerdown', () => { pointer = true; });
  form.addEventListener('keydown', () => { pointer = false; });
  form.addEventListener('change', (e) => {
    if (e.target.type === 'radio' && pointer) setTimeout(next, reduce.matches ? 0 : 200);
  });
  // Enter キーや「次へ」ボタンでも進める
  form.addEventListener('submit', (e) => { e.preventDefault(); next(); });
  back.addEventListener('click', () => { if (cur > 0) show(cur - 1, true); });
  res.addEventListener('click', (e) => {
    if (!e.target.closest('.dg-again')) return;
    form.reset();
    dg.classList.remove('is-done');
    show(0, true);
  });
  show(0, false);
});

/* ------------------------------------------------ 3b. プラン診断は、どのページのどこからでもモーダルで開く（スマホは全画面、PCは中央） */
{
  const modal = $('#diag');
  if (modal && typeof modal.showModal === 'function') {
    const menu = $('#menu');
    let opener = null;
    document.addEventListener('click', (e) => {
      const t = e.target.closest('[data-open-diag]');
      if (!t || modal.open) return;
      e.preventDefault();
      // メニューの中から開いたときは、閉じたあとの戻り先をメニューのボタンにする（リンクはメニューと一緒に隠れるため）
      opener = menu?.contains(t) ? $('[data-open-menu]') : t;
      if (menu?.open) menu.close();
      modal.showModal();
    });
    // 背景を押したら閉じる。モーダルの中のリンク（料金プランを見る など）も、閉じてから移動する
    modal.addEventListener('click', (e) => {
      if (e.target === modal || e.target.closest('a[href]')) { if (e.target !== modal) opener = null; modal.close(); }
    });
    modal.addEventListener('close', () => { opener?.focus(); opener = null; });
  } else if (modal) modal.classList.add('is-inline');
}

/* ------------------------------------------------ 4. サブナビの現在地 */
$$('.subnav').forEach((nav) => {
  const links = $$('a[href^="#"]', nav);
  const list = $('ol', nav);
  const pairs = links.map((a) => [a, document.getElementById(a.hash.slice(1))]).filter(([, t]) => t);
  let current; // 最初の1回は必ず描く（下層ページでは、いまのページの項目を見える位置へ送る）
  let queued = false;
  const update = () => {
    queued = false;
    if (!nav.getClientRects().length) return;
    // スマホ：ヘッダーとサブナビの下端を通り過ぎた、いちばん最後のセクションが現在地。PC（左レール）：画面の上から3割の線
    const line = pc.matches ? innerHeight * .3 : nav.getBoundingClientRect().bottom + 24;
    let hit = null;
    for (const [a, t] of pairs) if (t.getBoundingClientRect().top <= line) hit = a;
    // メニューにない節（オプション・よくある質問）にいる間は、その前の項目を現在地のままにする。最初の項目より上では、どれも付けない
    if (hit === current) return;
    current = hit;
    for (const [a] of pairs) {
      if (a === hit) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    }
    const focus = hit || $('a[aria-current="page"]', nav);
    if (focus) {
      const li = focus.parentElement;
      const behavior = reduce.matches ? 'auto' : 'smooth';
      if (pc.matches) list.scrollTo({ top: li.offsetTop - (list.clientHeight - li.offsetHeight) / 2, behavior });
      else list.scrollTo({ left: li.offsetLeft - (list.clientWidth - li.offsetWidth) / 2, behavior });
    }
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  pc.addEventListener('change', () => { current = undefined; queue(); });
  update();
});

/* ------------------------------------------------ 4a. 事例のスライダー：いま何枚目か（1 / 4）を出す */
$$('.cases').forEach((list) => {
  const count = list.previousElementSibling?.querySelector('.cases-count');
  if (!count) return;
  const cards = [...list.children];
  const now = $('[data-cases-now]', count);
  $('[data-cases-all]', count).textContent = cards.length;
  count.hidden = false;
  let queued = false;
  const update = () => {
    queued = false;
    // 左端にいちばん近いカード。最後までスクロールしたら最後の1枚
    const left = list.getBoundingClientRect().left + parseFloat(getComputedStyle(list).scrollPaddingInlineStart || 0);
    let i = 0, best = Infinity;
    cards.forEach((c, k) => { const d = Math.abs(c.getBoundingClientRect().left - left); if (d < best) { best = d; i = k; } });
    if (list.scrollLeft + list.clientWidth >= list.scrollWidth - 2) i = cards.length - 1;
    now.textContent = i + 1;
  };
  list.addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(update); } }, { passive: true });
  update();
});

/* ------------------------------------------------ 4c. ケーススタディ：写真は横に流れ続ける。左端（主役）の写真の説明を下に出す */
$$('[data-cs]').forEach((box) => {
  const track = $('.cs-track', box);
  const items = $$('.cs-item', track);
  const n = items.length / 2;                       // 写真は2組並べて、つなぎ目なく回す
  const caps = $$('.cs-cap', box.parentElement);
  const now = $('[data-cs-now]', box.parentElement);
  const pauseBtn = $('[data-cs-pause]', box.parentElement);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let pos = 0, paused = reduce, hold = false, last = 0, cur = -1;
  if (reduce && pauseBtn) { pauseBtn.setAttribute('aria-pressed', 'true'); pauseBtn.textContent = '流す'; }
  const pick = () => {
    const left = box.getBoundingClientRect().left + parseFloat(getComputedStyle(track).paddingInlineStart);
    let best = Infinity, idx = 0;
    items.forEach((el, k) => { const d = Math.abs(el.getBoundingClientRect().left - left); if (d < best) { best = d; idx = k; } });
    items.forEach((el, k) => el.classList.toggle('is-main', k === idx));
    const i = idx % n;
    if (i !== cur) { cur = i; caps.forEach((c, k) => { c.hidden = k !== i; }); if (now) now.textContent = i + 1; }
  };
  const step = (t) => {
    const dt = last ? Math.min(t - last, 64) : 0; last = t;
    const r = box.getBoundingClientRect();
    const seen = r.bottom > 0 && r.top < innerHeight;   // 画面に見えているときだけ流す
    if (!paused && !hold && seen) {
      const loop = track.scrollWidth / 2;
      if (Math.abs(box.scrollLeft - pos) > 2) pos = box.scrollLeft;   // 手で動かしたら、そこから続ける
      pos = (pos + dt * 0.04) % loop;                 // 1秒に40px（小数は手元で持つ）
      box.scrollLeft = pos;
    }
    pick();
    requestAnimationFrame(step);
  };
  // 触っている間・フォーカスがある間は止める。手で動かしてもよい
  ['pointerenter', 'focusin', 'touchstart'].forEach((e) => box.addEventListener(e, () => { hold = true; }, { passive: true }));
  ['pointerleave', 'focusout', 'touchend'].forEach((e) => box.addEventListener(e, () => { hold = false; }, { passive: true }));
  pauseBtn?.addEventListener('click', () => {
    paused = !paused;
    pauseBtn.setAttribute('aria-pressed', String(paused));
    pauseBtn.textContent = paused ? '流す' : '止める';
  });
  requestAnimationFrame(step);
});

/* ------------------------------------------------ 4b. 要点のマーカー：画面に入ったら引く（CSS の transition。動きを減らす設定では最初から引いた状態） */
{
  const marks = $$('mark.mk');
  if (marks.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -15% 0px' });
    marks.forEach((m) => io.observe(m));
  } else marks.forEach((m) => m.classList.add('is-in'));
}

/* ------------------------------------------------ 5. フォーム */
$$('form[data-form]').forEach((f) => {
  f.addEventListener('submit', (e) => {
    // 入力の確認はブラウザ標準の検証（required / type=email）に任せる。ここに来るのは全項目が正しいときだけ
    e.preventDefault();
    const endpoint = f.dataset.endpoint;
    if (!endpoint) {
      // 送信先が未設定のあいだは何も送らず、完了ページの見本へ
      if (f.dataset.form === 'quote') location.href = 'thanks.html';
      else {
        const m = $('.form-msg:not(.prefill)', f);
        m.hidden = false;
        m.textContent = 'この見本サイトでは、まだ何も送信されません。公開時に送信先を設定すると、入力したアドレスにひな形が届きます。';
      }
      return;
    }
    const submit = $('button[type="submit"]', f);
    if (submit.disabled) return; // 送信中の二重送信を防ぐ
    submit.disabled = true;
    fetch(endpoint, { method: 'POST', body: new FormData(f), headers: { Accept: 'application/json' } })
      .then((r) => { if (!r.ok) throw new Error(r.status); location.href = 'thanks.html'; })
      .catch(() => {
        submit.disabled = false;
        const m = $('.form-msg:not(.prefill)', f);
        m.hidden = false;
        m.textContent = '送信できませんでした。時間をおいてもう一度お試しいただくか、お電話でご連絡ください。';
      });
  });
});

/* 診断の結果を、見積フォームの「気になっていること」に入れる */
{
  const f = $('form[data-form="quote"][data-prefill]');
  let m = null;
  try { m = JSON.parse(sessionStorage.getItem(STORE) || 'null'); } catch {}
  if (f && m) {
    const ta = $('textarea', f);
    ta.value = `【プラン診断の結果】おすすめ：${m.plan}\n${m.lines.join('\n')}`;
    const map = { standard: 'スタンダード', wide: 'ワイド', consult: '内製化支援', self: 'まだわからない' };
    $$('input[type="checkbox"]', f).forEach((c) => { if (c.value.startsWith(map[m.key])) c.checked = true; });
    const note = $('.prefill', f);
    note.textContent = `プラン診断の結果（${m.plan}）を、下の「気になっていること」欄に入れておきました。必須の4項目だけ入力すれば送信できます。`;
    note.hidden = false;
  }
}
