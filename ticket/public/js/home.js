import { $, api, el, put } from './common.js';

const app = $('#app');
const cfg = await api('config');
put(app, 
  el('a', { class: 'brand', href: '/' }, 'KARURA LIVE', el('small', {}, 'カルラライブ')),
  el('h1', { class: 'h1' }, '受付用デジタルチケット'),
  el('p', { class: 'lead' }, 'シンポジウム・講演会の配信を担当する「カルラライブ」が、申込の受付と当日の入場、終了後の報告に使っている道具です。'),
  el('div', { class: 'box stack' },
    el('p', {}, 'チケットをお持ちの方は、申込のあとに表示されたページ、またはメールで届いたURLを開いてください。'),
    el('p', { class: 'note' }, 'チケットが見つからないときは、当日の受付でお名前をお伝えください。')),
  cfg.lp_url ? el('p', {}, el('a', { href: cfg.lp_url, rel: 'noopener' }, 'カルラライブのサービスについて')) : null,
);
