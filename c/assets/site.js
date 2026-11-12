/* カルラライブ C案 site.js
   標準の HTML/CSS で足りないところだけを補う。どれも無くても、内容は読めて、リンクとフォームは使える。
   1. スマホのメニュー（dialog.showModal と背景クリックで閉じる）
   2. カメラ切り替えの自動送り（切り替え自体はラジオと :has で動く）
   3. プラン診断（1問ずつ表示と判定）
   4. サブナビの現在地（スクロール位置から計算）
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
    dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
    // メニュー内のページ内リンクは、閉じてから移動する
    dlg.addEventListener('click', (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (a) dlg.close();
    });
    dlg.addEventListener('close', () => open.focus());
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

  if (big) {
    return { key: 'big', plan: '大手の制作会社をおすすめします', price: null, adds, why, cta: 'consult',
      lead: `${a.spk === '7+' ? '登壇者が7人以上' : '会場が300人以上'}の会は、カメラ3台・スタッフ2名の私たちの体制より大きな会です。無理にお引き受けするより、大手の制作会社に頼んだほうが安心です。` };
  }
  if (need <= 1 && a.aud !== '100-300') {
    return { key: 'self', plan: 'iPhoneで足ります', price: ['0', '円'], adds, cta: 'self',
      why: ['登壇者が1人で、質疑を配信に乗せない会は、カメラ1台で十分に伝わります'],
      lead: 'この条件なら、ご自身で配信できます。業者に頼む必要はありません。iPhoneと外付けマイク1本で始められます。' };
  }
  if (need <= 3) {
    return { key: 'consult', plan: '配信コーチング：相談', price: ['［3］', '万円（税別）'], adds, why, cta: 'quote',
      lead: '機材と接続を一度整理すれば、ご自身で配信できる可能性が高い会です。オンライン60分で、接続の図と当日のチェックリストを作成します。' };
  }
  const maru = opts.length >= 2;
  const mics = ({ '2-3': 3, '4-6': 6 })[a.spk] + (a.qa === 'y' ? 1 : 0);
  const addStaff = a.rmt === 'y' || mics > 5;
  if (addStaff) adds.push(['スタッフを1名追加', a.rmt === 'y' ? 'オンラインから登壇する人がいるため' : `マイクが${mics}本必要になるため`]);
  if (a.time === '3+') adds.push(['配信時間の延長', '3時間を超える分']);
  if (!maru && opts.length === 1) adds.push([LABEL.opt[opts[0]], '同じ日にまとめて依頼']);
  if (a.self === 'y') adds.push(['コーチング：同行', '私たちの配信を横で見て、次の会から自分たちで回せるように']);
  return {
    key: maru ? 'marugoto' : 'standard', plan: maru ? 'まるごと' : 'スタンダード',
    price: maru ? ['［40］', '万円（税別）'] : ['25', '万円（税別）'],
    lead: maru
      ? 'スタンダードに、記録写真・記録映像の編集・ダイジェスト・文字起こしを加えて、スタッフ3名で伺います。一回の現場で、報告書の素材まで揃います。'
      : 'カメラ3台・スタッフ2名・マイク5本の基本プランが合う会です。事前の打ち合わせ、会場の下見、録画データの納品まで含みます。',
    staff: (maru ? 3 : 2) + (addStaff ? 1 : 0), mics: Math.min(mics, addStaff ? 8 : 5), adds, why, cta: 'quote',
  };
}

/* 結果は DOM を組み立てて入れる（innerHTML に利用者の入力は入れない） */
function el(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  for (const k of kids.flat()) if (k != null) n.append(k);
  return n;
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
    const dl = el('dl', { class: 'dg-sum' }, el('div', {}, el('dt', {}, '当日の体制'), el('dd', {}, `スタッフ${r.staff}名・カメラ3台・マイク${r.mics}本`)));
    r.adds.forEach(([t, d]) => dl.append(el('div', {}, el('dt', {}, '追加'), el('dd', {}, t, '　', el('span', { class: 'ana' }, '［金額］'), el('small', {}, d)))));
    parts.push(dl);
  }
  if (r.why.length) parts.push(el('p', { class: 't-note' }, 'こう判断した理由'), el('ul', { class: 'dg-why' }, r.why.map((w) => el('li', {}, w))));
  const btns = el('div', { class: 'btns' });
  if (r.cta === 'quote') btns.append(el('a', { class: 'btn', href: 'contact.html' }, 'この内容で見積書を受け取る'), el('a', { class: 'btn line', href: '#price' }, '料金の内訳を見る'));
  else if (r.cta === 'self') btns.append(el('a', { class: 'btn line', href: 'contact.html#consult' }, '念のため相談する'));
  else btns.append(el('a', { class: 'btn', href: 'contact.html#consult' }, '15分のオンライン相談で確かめる'));
  parts.push(btns, el('button', { type: 'button', class: 'dg-again' }, '最初から診断しなおす'));
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

/* ------------------------------------------------ 4. サブナビの現在地 */
$$('.subnav').forEach((nav) => {
  const links = $$('a[href^="#"]', nav);
  const list = $('ol', nav);
  const meter = $('.subnav-meter', nav);
  const pairs = links.map((a) => [a, document.getElementById(a.hash.slice(1))]).filter(([, t]) => t);
  let current = null;
  let queued = false;
  const update = () => {
    queued = false;
    if (!nav.getClientRects().length) return;
    // スマホ：ヘッダーとサブナビの下端を通り過ぎた、いちばん最後のセクションが現在地。PC（左レール）：画面の上から3割の線
    const line = pc.matches ? innerHeight * .3 : nav.getBoundingClientRect().bottom + 24;
    let hit = null;
    for (const [a, t] of pairs) if (t.getBoundingClientRect().top <= line) hit = a;
    const doc = document.documentElement;
    if (innerHeight + scrollY >= doc.scrollHeight - 4) hit = pairs.at(-1)[0];
    hit ??= pairs[0][0]; // ページの一番上では最初の項目
    meter.style.setProperty('--p', Math.min(1, scrollY / Math.max(1, doc.scrollHeight - innerHeight)));
    if (hit === current) return;
    current = hit;
    for (const [a] of pairs) {
      if (a === hit) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    }
    if (hit) {
      const li = hit.parentElement;
      const behavior = reduce.matches ? 'auto' : 'smooth';
      if (pc.matches) list.scrollTo({ top: li.offsetTop - (list.clientHeight - li.offsetHeight) / 2, behavior });
      else list.scrollTo({ left: li.offsetLeft - (list.clientWidth - li.offsetWidth) / 2, behavior });
    }
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  pc.addEventListener('change', () => { current = null; queue(); });
  update();
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
        const m = $('.form-msg', f);
        m.hidden = false;
        m.textContent = 'この見本サイトでは、まだ何も送信されません。公開時に送信先を設定すると、入力したアドレスにひな形が届きます。';
      }
      return;
    }
    fetch(endpoint, { method: 'POST', body: new FormData(f), headers: { Accept: 'application/json' } })
      .then((r) => { if (!r.ok) throw new Error(r.status); location.href = 'thanks.html'; })
      .catch(() => {
        const m = $('.form-msg', f);
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
    const map = { standard: 'スタンダード', marugoto: 'まるごと', consult: 'コーチング', self: 'まだわからない', big: 'まだわからない' };
    $$('input[type="checkbox"]', f).forEach((c) => { if (c.value.startsWith(map[m.key])) c.checked = true; });
    const note = $('.prefill', f);
    note.textContent = `プラン診断の結果（${m.plan}）を、下の「気になっていること」欄に入れておきました。必須の4項目だけ入力すれば送信できます。`;
    note.hidden = false;
  }
}
