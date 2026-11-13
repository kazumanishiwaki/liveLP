// 開催報告：申込数・来場者数・オンライン視聴者数を1枚に
import { $, api, el, eventFacts, fmtDate, put, qs, showError } from './common.js';

const app = $('#app');
const id = qs.get('e') || '', key = qs.get('k') || '';
const r = await api(`staff/${encodeURIComponent(id)}/report`, { key });
if (!r.ok) showError(app, r.message || 'このURLでは開けません。');
else render(r.event, r.summary);

function render(ev, s) {
  const rate = s.venue_total ? Math.round((s.checked_in / s.venue_total) * 100) : 0;
  const c = (label, n, sub) => el('div', { class: 'count' }, el('dt', {}, label), el('dd', {}, String(n), sub ? el('small', {}, sub) : null));
  const row = (label, n) => el('tr', {}, el('th', { scope: 'row' }, label), el('td', {}, `${n}人`));
  const max = Math.max(1, ...s.timeline.map((t) => t.n));
  const bars = s.timeline.map((t) => {
    const bar = el('i');
    bar.style.inlineSize = `${Math.round((t.n / max) * 100)}%`;
    return el('li', { class: 'bar' }, el('span', {}, t.t), el('span', {}, bar), el('span', {}, String(t.n)));
  });
  const online = s.online_manual ?? s.online_watched;
  put(app, 
    el('div', { class: 'row row--between' }, el('a', { class: 'brand', href: '/' }, 'KARURA LIVE', el('small', {}, 'カルラライブ')),
      el('button', { class: 'btn btn--line btn--s no-print', type: 'button', onclick: () => print() }, '印刷・PDFにする')),
    el('div', { class: 'stack' }, el('p', {}, el('span', { class: 'tag' }, '開催報告')), el('h1', { class: 'h1' }, ev.title), eventFacts(ev)),
    el('dl', { class: 'counts' }, c('申込（会場）', s.venue_total, '人'), c('来場', s.checked_in, `人（${rate}%）`), c('申込（オンライン）', s.online_total, '人'), c('オンライン視聴', online, '人')),
    el('section', { class: 'stack' }, el('h2', { class: 'h2' }, '来場の内訳'),
      el('table', { class: 'tbl' }, el('tbody', {}, row('QRコードで入場', s.by_method.qr), row('タッチ（4桁のコード）で入場', s.by_method.touch), row('受付のタグで入場', s.by_method.door), row('受付で名前を確認して入場', s.by_method.staff)))),
    s.timeline.length ? el('section', { class: 'stack' }, el('h2', { class: 'h2' }, '入場した時刻（10分ごと）'), el('ul', { class: 'bars' }, bars)) : null,
    el('section', { class: 'stack' }, el('h2', { class: 'h2' }, 'オンライン'),
      el('table', { class: 'tbl' }, el('tbody', {}, row('チケットから配信を開いた人', s.online_watched),
        s.online_manual != null ? row('配信サービス側の視聴者数', s.online_manual) : null))),
    s.line_joined ? el('section', { class: 'stack' }, el('h2', { class: 'h2' }, 'LINE'),
      el('table', { class: 'tbl' }, el('tbody', {}, row('LINEで申し込んだ人', s.line_joined), row('LINE公式アカウントの友だち', s.line_friends), row('うち、この申込で新しく友だちになった人', s.line_friends_new)))) : null,
    el('p', { class: 'note' }, ev.closed ? '参加者の名簿は削除済みです。この報告には集計だけが残っています。' : `参加者の名簿は ${fmtDate(ev.purge_on)} を過ぎると自動で削除されます。この報告の数字は残ります。`),
  );
}
