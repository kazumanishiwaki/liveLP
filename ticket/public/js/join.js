// 参加の申込
import { $, api, el, eventFacts, put, qs, showError } from './common.js';

const app = $('#app');
const id = qs.get('e') || '';
const ERR = {
  name: 'お名前を入力してから、もう一度お試しください。',
  cancel: 'LINEでの申込を中止しました。もう一度お試しいただくか、メールアドレスでお申し込みください。',
  line: 'LINEでの申込がうまくいきませんでした。もう一度お試しいただくか、メールアドレスでお申し込みください。',
  full: '会場での参加は定員に達しました。',
  closed: 'この会の申込は、いま受け付けていません。',
};

const r = await api(`e/${encodeURIComponent(id)}`);
if (!r.ok) showError(app, r.message || 'この会は見つかりませんでした。');
else render(r.event);

function render(ev) {
  const head = [
    el('a', { class: 'brand', href: '/' }, 'KARURA LIVE', el('small', {}, 'カルラライブ')),
    el('div', { class: 'stack' }, el('p', {}, el('span', { class: 'tag' }, '参加の申込')), el('h1', { class: 'h1' }, ev.title), eventFacts(ev)),
  ];
  if (!ev.registration_open) {
    put(app, ...head, el('p', { class: 'msg' }, ev.closed ? 'この会の受付は終了しました。' : 'この会の申込は、いま受け付けていません。'));
    return;
  }
  const msg = el('p', { class: 'msg msg--err', role: 'alert', hidden: !ERR[qs.get('err')] }, ERR[qs.get('err')] || '');
  const radio = (value, label, opts = {}) => el('label', { class: 'choice' }, el('input', { type: 'radio', name: 'kind', value, ...opts }), label);
  const venueOk = !ev.venue_full;
  const kinds = el('fieldset', { class: 'fld' }, el('legend', {}, '参加の方法'),
    el('div', { class: 'choices' },
      radio('venue', venueOk ? '会場で参加' : '会場で参加（満席）', { checked: venueOk, disabled: !venueOk }),
      ev.has_stream ? radio('online', 'オンライン', { checked: !venueOk }) : null));
  const name = el('input', { class: 'inp', id: 'name', name: 'name', required: true, maxlength: '80', autocomplete: 'name' });
  const org = el('input', { class: 'inp', id: 'org', name: 'org', maxlength: '120', autocomplete: 'organization' });
  const email = el('input', { class: 'inp', id: 'email', name: 'email', type: 'email', maxlength: '254', autocomplete: 'email', inputmode: 'email', placeholder: 'name@example.ac.jp' });
  const trap = el('input', { class: 'hp', name: 'website', tabindex: '-1', autocomplete: 'off', 'aria-hidden': 'true' });
  const send = el('button', { class: 'btn btn--full', type: 'submit' }, ev.line ? 'メールアドレスで申し込む' : '申し込む');

  const form = el('form', { class: 'card stack', novalidate: true },
    msg,
    el('div', { class: 'fld' }, el('label', { for: 'name' }, 'お名前', el('span', { class: 'req' }, '必須')), name),
    el('div', { class: 'fld' }, el('label', { for: 'org' }, 'ご所属'), org),
    venueOk || ev.has_stream ? kinds : null,
    ev.line ? lineBlock() : null,
    el('div', { class: 'fld' }, el('label', { for: 'email' }, 'メールアドレス', ev.line ? null : el('span', { class: 'req' }, '必須')), email),
    trap, send,
    el('p', { class: 'note' }, 'ご記入いただいた内容は、この会の受付と開催報告のためだけに使い、会の終了後、一定の期間で削除します。'));

  if (!venueOk && !ev.has_stream) {
    put(app, ...head, el('p', { class: 'msg' }, '定員に達したため、申込を締め切りました。'));
    return;
  }

  function fail(text, focus) { msg.textContent = text; msg.hidden = false; focus?.focus(); msg.scrollIntoView({ block: 'nearest' }); }

  function lineBlock() {
    const go = el('button', { class: 'btn btn--full btn--lineapp', type: 'button' }, 'LINEで申し込む');
    go.addEventListener('click', () => {
      if (!name.value.trim()) return fail(ERR.name, name);
      // 名前などはこのサイトにだけ送り、LINE の同意画面へ移る
      const f = el('form', { method: 'post', action: `/api/e/${encodeURIComponent(ev.id)}/line/start`, hidden: true },
        el('input', { name: 'name', value: name.value }), el('input', { name: 'org', value: org.value }),
        el('input', { name: 'kind', value: form.elements.kind?.value || 'venue' }));
      document.body.append(f);
      f.submit();
    });
    return el('div', { class: 'box box--wash stack' }, go,
      el('p', { class: 'note' }, '主催者のLINE公式アカウントを友だちに追加すると、次回の案内がLINEで届きます。追加するかどうかは、次の画面で選べます。'),
      el('p', { class: 'note' }, 'LINEを使わない方は、下のメールアドレスでお申し込みください。'));
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!name.value.trim()) return fail('お名前を入力してください。', name);
    if (!email.value.trim() || !email.checkValidity()) return fail('メールアドレスの形で入力してください（例：name@example.ac.jp）。', email);
    send.disabled = true;
    const res = await api(`e/${encodeURIComponent(ev.id)}/join`, { method: 'POST', body: { name: name.value, org: org.value, email: email.value, kind: form.elements.kind?.value || 'venue', website: trap.value } });
    send.disabled = false;
    if (!res.ok) return fail(res.message || 'うまく送信できませんでした。');
    location.href = res.ticket_url + '&new=1';
  });

  put(app, ...head, form);
}
