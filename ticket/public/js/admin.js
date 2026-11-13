// 管理（カルラライブの担当者）：会を作る、LINE連携を設定する、名簿を消す
import { $, api, copyRow, el, fmtDate, put, toast } from './common.js';

const app = $('#app');
const KEY = 'kt-admin';
let key = '';
try { key = sessionStorage.getItem(KEY) || ''; } catch { /* 保存できない環境では、毎回入力する */ }
const call = (path, opts = {}) => api(`admin/${path}`, { ...opts, key });
const brand = () => el('a', { class: 'brand', href: '/' }, 'KARURA LIVE', el('small', {}, 'カルラライブ'));

key ? load() : login();

function login(message) {
  const inp = el('input', { class: 'inp', id: 'key', type: 'password', required: true, autocomplete: 'current-password' });
  const form = el('form', { class: 'card stack' }, el('h1', { class: 'h2' }, '管理'),
    message ? el('p', { class: 'msg msg--err', role: 'alert' }, message) : null,
    el('div', { class: 'fld' }, el('label', { for: 'key' }, '管理用の鍵'), inp), el('button', { class: 'btn', type: 'submit' }, '開く'));
  form.addEventListener('submit', (e) => { e.preventDefault(); key = inp.value; load(); });
  put(app, brand(), form);
}

async function load() {
  const r = await call('events');
  if (!r.ok) { key = ''; try { sessionStorage.removeItem(KEY); } catch { /* 何もしない */ } return login(r.message); }
  try { sessionStorage.setItem(KEY, key); } catch { /* 何もしない */ }
  put(app, brand(),
    el('div', { class: 'row row--between' }, el('h1', { class: 'h1' }, '会の一覧'), el('button', { class: 'btn', type: 'button', onclick: () => edit(null, r) }, '会を作る')),
    r.mail ? null : el('p', { class: 'msg' }, 'メールの送信は設定されていません（RESEND_API_KEY）。チケットのURLは、名簿のCSVから主催者に送ってもらいます。'),
    r.events.length ? el('ul', { class: 'stack' }, r.events.map((ev) => card(ev, r))) : el('p', { class: 'note' }, 'まだ会がありません。'));
}

function card(ev, r) {
  const act = (label, fn, cls = 'btn--line') => el('button', { class: `btn ${cls} btn--s`, type: 'button', onclick: fn }, label);
  return el('li', { class: 'card stack' },
    el('div', { class: 'row' }, el('span', { class: `tag${ev.closed ? ' tag--off' : ''}` }, ev.closed ? '名簿は削除済み' : ev.reception_open ? '受付中' : ev.registration_open ? '申込受付中' : '準備中'),
      ev.line ? el('span', { class: 'tag' }, 'LINE連携') : null),
    el('h2', { class: 'h2' }, ev.title),
    el('p', { class: 'note' }, `${fmtDate(ev.held_on)}　${ev.venue}　｜　申込 ${ev.total}人、来場 ${ev.checked}人　｜　名簿の削除：${fmtDate(ev.purge_on)} のあと`),
    el('div', { class: 'fld' }, el('label', {}, '受付スタッフ用のURL（主催者に渡す）'), copyRow(ev.staff_url)),
    el('div', { class: 'row' }, el('a', { class: 'btn btn--s', href: ev.staff_url }, '受付の画面'), el('a', { class: 'btn btn--line btn--s', href: ev.report_url }, '開催報告'),
      ev.closed ? null : act('設定を変える', () => edit(ev, r)),
      ev.closed ? null : act('名簿をいま削除する', async () => {
        if (!confirm(`「${ev.title}」の名簿を削除します。集計だけが残り、元に戻せません。よろしいですか？`)) return;
        const x = await call(`events/${ev.id}/purge`, { method: 'POST', body: {} });
        x.ok ? load() : toast(x.message);
      }),
      act('会ごと削除する', async () => {
        if (!confirm(`「${ev.title}」を、名簿も集計も含めてすべて削除します。元に戻せません。よろしいですか？`)) return;
        const x = await call(`events/${ev.id}`, { method: 'DELETE' });
        x.ok ? load() : toast(x.message);
      }, 'btn--danger')));
}

function edit(ev, r) {
  const f = (name, label, attrs = {}, hint) => {
    const input = el('input', { class: 'inp', id: `f-${name}`, name, ...attrs });
    return el('div', { class: 'fld' }, el('label', { for: `f-${name}` }, label, attrs.required ? el('span', { class: 'req' }, '必須') : null), input, hint ? el('p', { class: 'note' }, hint) : null);
  };
  const msg = el('p', { class: 'msg msg--err', role: 'alert', hidden: true });
  const open = el('input', { type: 'checkbox', name: 'registration_open', checked: !!ev?.registration_open });
  const form = el('form', { class: 'stack', method: 'dialog' },
    el('h2', { class: 'h2' }, ev ? '設定を変える' : '会を作る'), msg,
    f('title', '会の名称', { required: true, maxlength: '120', value: ev?.title || '' }),
    el('div', { class: 'row' }, el('div', { class: 'grow' }, f('held_on', '開催日', { type: 'date', required: true, value: ev?.held_on || '' })), el('div', { class: 'grow' }, f('time_note', '時間', { maxlength: '80', value: ev?.time_note || '', placeholder: '13:00 開場／13:30 開演' }))),
    f('venue', '会場', { maxlength: '120', value: ev?.venue || '' }),
    el('div', { class: 'row' }, el('div', { class: 'grow' }, f('capacity', '会場の定員', { type: 'number', min: '1', max: '2000', value: ev?.capacity ?? 300 })), el('div', { class: 'grow' }, f('retention_days', '名簿の保存（会の終了から何日）', { type: 'number', min: '1', max: '365', value: ev?.retention_days ?? 30 }))),
    f('stream_url', '配信のURL', { type: 'url', maxlength: '500', value: ev?.stream_url || '', placeholder: 'https://' }, '入れておくと「オンラインで視聴」の申込と、チケットの「配信を見る」が使えます。'),
    el('label', { class: 'choice' }, open, '申込フォームを開ける'),
    el('div', { class: 'box stack' }, el('h3', { class: 'h2' }, 'LINE連携（オプション）'),
      el('p', { class: 'note' }, '主催者の LINE Developers コンソールで、LINEログインのチャネルを作り、同じプロバイダーにある LINE公式アカウントをリンクします。コールバックURLには下を登録します。'),
      copyRow(r.line_callback),
      f('line_channel_id', 'チャネルID', { inputmode: 'numeric', maxlength: '20', value: ev?.line_channel_id || '', autocomplete: 'off' }),
      f('line_channel_secret', 'チャネルシークレット', { type: 'password', maxlength: '64', autocomplete: 'new-password', placeholder: ev?.line ? '変えないときは空のまま' : '' }, 'やめるときは、チャネルIDを空にして保存します。')),
    el('div', { class: 'row' }, el('button', { class: 'btn', type: 'submit', value: 'save' }, '保存する'), el('button', { class: 'btn btn--line', type: 'button', onclick: () => dlg.close() }, 'やめる')));
  const dlg = el('dialog', { class: 'dlg' }, form);
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const d = Object.fromEntries(new FormData(form));
    const bodyObj = { title: d.title, held_on: d.held_on, time_note: d.time_note, venue: d.venue, capacity: Number(d.capacity), retention_days: Number(d.retention_days),
      stream_url: d.stream_url, registration_open: open.checked };
    if (d.line_channel_id || d.line_channel_secret || ev?.line_channel_id) { bodyObj.line_channel_id = d.line_channel_id; bodyObj.line_channel_secret = d.line_channel_secret; }
    const x = ev ? await call(`events/${ev.id}`, { method: 'PATCH', body: bodyObj }) : await call('events', { method: 'POST', body: bodyObj });
    if (!x.ok) { msg.textContent = x.message; msg.hidden = false; return; }
    dlg.close(); load();
  });
  dlg.addEventListener('close', () => dlg.remove());
  document.body.append(dlg);
  dlg.showModal();
}
