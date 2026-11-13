// 受付に置いたタグ（NFC・掲示したQRコード）を読んだときのページ
import { $, api, el, fmtTime, put, qs, store } from './common.js';

const app = $('#app');
const id = qs.get('e') || '', key = qs.get('k') || '';
const brand = () => el('a', { class: 'brand', href: '/' }, 'KARURA LIVE', el('small', {}, 'カルラライブ'));

const saved = store.get(`kt:${id}`);
if (saved) {
  const r = await enter({ token: saved });
  if (!r.ok && r.code === 'no_ticket') askEmail(); // このスマホに残っているのが、別の会のチケットだったとき
} else askEmail();

async function enter(extra) {
  const r = await api(`door/${encodeURIComponent(id)}`, { method: 'POST', body: { key, ...extra } });
  if (r.ok) done(r);
  else if (r.code !== 'no_ticket' && r.code !== 'need_ticket') {
    put(app, brand(), el('p', { class: 'msg msg--err', role: 'alert' }, r.message || '入場を記録できませんでした。受付でお名前をお伝えください。'),
      el('button', { class: 'btn btn--line', type: 'button', onclick: () => location.reload() }, 'もう一度試す'));
  }
  return r;
}

function done(r) {
  put(app, brand(),
    el('div', { class: 'card stack' },
      el('h1', { class: 'h2' }, r.event.title),
      el('div', { class: 'tk-done', role: 'status' }, el('b', {}, r.already ? '入場済みです' : '入場しました'),
        el('span', {}, `${r.name} 様`), el('span', { class: 'clock' }, `${fmtTime(r.checked_in_at)}`)),
      el('p', { class: 'note' }, 'この画面を受付にお見せのうえ、そのままお入りください。')));
}

function askEmail() {
  const msg = el('p', { class: 'msg msg--err', role: 'alert', hidden: true });
  const email = el('input', { class: 'inp', id: 'email', type: 'email', required: true, autocomplete: 'email', inputmode: 'email', placeholder: 'name@example.ac.jp' });
  const go = el('button', { class: 'btn btn--full', type: 'submit' }, '入場する');
  const form = el('form', { class: 'card stack', novalidate: true },
    el('h1', { class: 'h2' }, '申込のときのメールアドレスを入力してください'),
    el('div', { class: 'fld' }, el('label', { for: 'email' }, 'メールアドレス'), email), msg, go,
    el('p', { class: 'note' }, 'チケットのページを開いたことがあるスマホなら、入力なしで入場できます。うまくいかないときは、受付でお名前をお伝えください。'));
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!email.checkValidity()) { msg.textContent = 'メールアドレスの形で入力してください。'; msg.hidden = false; return; }
    go.disabled = true;
    const r = await enter({ email: email.value });
    go.disabled = false;
    if (!r.ok && (r.code === 'no_ticket' || r.code === 'need_ticket')) { msg.textContent = r.message; msg.hidden = false; }
  });
  put(app, brand(), form);
}
