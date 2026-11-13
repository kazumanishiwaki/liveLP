// チケット：QRコードを見せる、タッチ（4桁のコード）で入場する、配信を見る
import { $, api, drawQr, el, eventFacts, fmtTime, put, qs, showError, store } from './common.js';

const app = $('#app');
const token = qs.get('k') || '';
const path = `t/${encodeURIComponent(token)}`;
let timer;

const first = await api(path);
if (!first.ok) showError(app, first.message || 'チケットが見つかりませんでした。');
else {
  store.set(`kt:${first.event.id}`, token); // 受付のタグにかざしたとき、このチケットで入場できるようにする
  render(first);
  watch(first.event.reception_open);
}

// 受付のスマホでQRコードを読み取られたら、こちらの画面も「入場済み」に変わる。
// 確かめに行くのは、受付中は8秒ごと、受付前は1分ごと。入場済みになったらやめる
function watch(open) {
  setTimeout(async () => {
    if ($('.tk-done')) return;
    let next = open;
    if (document.visibilityState === 'visible') {
      const r = await api(path);
      if (r.ok) { render(r, true); next = r.event.reception_open; if (r.ticket.checked_in_at || r.event.closed) return; }
    }
    watch(next);
  }, open ? 8000 : 60000);
}

function render({ event: ev, ticket: tk }, quiet = false) {
  if (quiet && !tk.checked_in_at && $('#code')) return; // コードを入力している最中は、画面を作り直さない
  clearInterval(timer);
  const body = el('div', { class: 'tk-body' });
  if (tk.checked_in_at) body.append(doneView(tk));
  else if (ev.closed) body.append(el('p', { class: 'msg' }, 'この会の受付は終了しました。'));
  else if (tk.kind === 'online') body.append(el('p', { class: 'lead' }, 'オンラインで視聴するチケットです。当日は、下のボタンから配信をご覧ください。'));
  else body.append(...venueView(ev, tk));
  if (ev.has_stream && !ev.closed) body.append(watchButton(tk.kind === 'online'));

  put(app, 
    el('a', { class: 'brand', href: '/' }, 'KARURA LIVE', el('small', {}, 'カルラライブ')),
    qs.get('new') && !quiet && !tk.checked_in_at ? el('p', { class: 'msg', role: 'status' }, '申込を受け付けました。このページがチケットです。ブックマークするか、画面を保存しておいてください。') : null,
    el('article', { class: 'card tk' },
      el('div', { class: 'tk-head' },
        el('p', {}, el('span', { class: 'tag' }, tk.kind === 'online' ? 'オンライン視聴' : '会場参加')),
        el('h1', { class: 'h2' }, ev.title), eventFacts(ev),
        el('p', { class: 'tk-name' }, `${tk.name} 様`), tk.org ? el('p', { class: 'note' }, tk.org) : null),
      el('div', { class: 'tk-cut' }), body),
    el('p', { class: 'note' }, 'チケットが開けないときは、受付でお名前をお伝えください。'));
}

function doneView(tk) {
  const clock = el('span', { class: 'clock' });
  const tick = () => { clock.textContent = new Date().toLocaleTimeString('ja-JP', { hour12: false }); };
  tick();
  timer = setInterval(tick, 1000); // 動いている時計で、保存した画像ではないことが受付からわかる
  const check = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  check.setAttribute('viewBox', '0 0 24 24');
  const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  for (const [k, v] of Object.entries({ d: 'M5 12.5l4.2 4L19 7', fill: 'none', stroke: 'currentColor', 'stroke-width': '2.6', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })) p.setAttribute(k, v);
  check.append(p);
  return el('div', { class: 'tk-done', role: 'status' }, el('span', { class: 'tk-pulse', 'aria-hidden': 'true' }, check),
    el('b', {}, '入場済み'), el('span', {}, `${fmtTime(tk.checked_in_at)} に入場しました`), clock);
}

function venueView(ev, tk) {
  const canvas = el('canvas', { class: 'qr', role: 'img', 'aria-label': '入場用のQRコード' });
  drawQr(canvas, location.origin + location.pathname + '?k=' + encodeURIComponent(token));
  const out = [canvas, el('p', { class: 'note' }, '受付で、このQRコードをお見せください。')];
  if (tk.locked) out.push(el('p', { class: 'msg msg--err' }, 'コードの入力が続けて合いませんでした。受付でお名前をお伝えください。'));
  else out.push(touchBlock(ev));
  return out;
}

function touchBlock(ev) {
  const wrap = el('div', { class: 'stack' });
  const open = el('button', { class: 'btn btn--line btn--full', type: 'button' }, 'タッチで入場する');
  open.addEventListener('click', () => {
    const msg = el('p', { class: 'msg msg--err', role: 'alert', hidden: true });
    const code = el('input', { class: 'inp code-inp', id: 'code', inputmode: 'numeric', pattern: '[0-9]{4}', maxlength: '4', autocomplete: 'off', required: true, 'aria-describedby': 'code-h' });
    const go = el('button', { class: 'btn btn--full', type: 'submit' }, '入場する');
    const form = el('form', { class: 'box stack' },
      el('div', { class: 'fld' }, el('label', { for: 'code' }, '受付の4桁のコード'), code),
      el('p', { class: 'note', id: 'code-h' }, ev.reception_open ? '受付に表示されている4桁の数字を入力してください。' : 'まだ受付が始まっていません。会場に着いてからお試しください。'),
      msg, go);
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!/^\d{4}$/.test(code.value)) { msg.textContent = '4桁の数字を入力してください。'; msg.hidden = false; return; }
      go.disabled = true;
      const r = await api(`${path}/touch`, { method: 'POST', body: { code: code.value } });
      go.disabled = false;
      if (r.ok) { const now = await api(path); if (now.ok) render(now); return; }
      msg.textContent = r.message || 'うまくいきませんでした。'; msg.hidden = false;
      code.value = ''; code.focus();
      if (r.code === 'locked') { const now = await api(path); if (now.ok) render(now); }
    });
    put(wrap, form);
    code.focus();
  });
  wrap.append(open);
  return wrap;
}

function watchButton(primary) {
  const b = el('button', { class: `btn btn--full${primary ? ' btn--xl' : ' btn--line'}`, type: 'button' }, '配信を見る');
  b.addEventListener('click', async () => {
    b.disabled = true;
    const r = await api(`${path}/watch`, { method: 'POST', body: {} });
    b.disabled = false;
    if (r.ok) location.href = r.url;
    else b.after(el('p', { class: 'msg msg--err', role: 'alert' }, r.message || '配信を開けませんでした。'));
  });
  return b;
}
