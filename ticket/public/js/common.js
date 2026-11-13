// どのページでも使う小さな道具
import qrcode from '../vendor/qrcode.js';

export const qs = new URLSearchParams(location.search);

/** API を呼ぶ。通信できなかったときも同じ形（ok: false と message）で返す */
export async function api(path, { method = 'GET', body, key } = {}) {
  const headers = {};
  if (body !== undefined) headers['content-type'] = 'application/json';
  if (key) headers.authorization = `Bearer ${key}`;
  try {
    const res = await fetch(`/api/${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body), cache: 'no-store' });
    const data = await res.json().catch(() => ({}));
    return { ...data, ok: res.ok && data.ok !== false, status: res.status };
  } catch {
    return { ok: false, status: 0, code: 'offline', message: '通信できませんでした。電波の状態をご確認のうえ、もう一度お試しください。' };
  }
}

/** 要素を作る。文字はすべて textContent で入れる（HTML としては解釈しない） */
export function el(tag, attrs = {}, ...kids) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === false || v == null) continue;
    if (k === 'class') node.className = v;
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
    else if (k === 'hidden' || k === 'disabled' || k === 'checked' || k === 'required') node[k] = !!v;
    else node.setAttribute(k, v === true ? '' : v);
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) node.append(kid);
  return node;
}

export const $ = (sel, root = document) => root.querySelector(sel);

/** 中身を入れ替える。null や false は飛ばす（replaceChildren にそのまま渡すと "null" という文字が出てしまう） */
export function put(node, ...kids) {
  node.replaceChildren(...kids.flat().filter((k) => k != null && k !== false));
}

const WD = ['日', '月', '火', '水', '木', '金', '土'];
/** 2027-02-20 → 2027年2月20日（土） */
export function fmtDate(ymd) {
  const [y, m, d] = ymd.split('-').map(Number);
  return `${y}年${m}月${d}日（${WD[new Date(Date.UTC(y, m - 1, d)).getUTCDay()]}）`;
}
/** 時刻を日本時間の 13:05 の形にする */
export function fmtTime(iso) {
  return new Intl.DateTimeFormat('ja-JP', { timeZone: 'Asia/Tokyo', hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(iso));
}

/** QRコードを canvas に描く */
export function drawQr(canvas, text) {
  const qr = qrcode(0, 'M');
  qr.addData(text);
  qr.make();
  const n = qr.getModuleCount(), quiet = 4, scale = 8, size = (n + quiet * 2) * scale;
  canvas.width = canvas.height = size;
  const g = canvas.getContext('2d');
  g.fillStyle = '#fff';
  g.fillRect(0, 0, size, size);
  g.fillStyle = '#000';
  for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (qr.isDark(r, c)) g.fillRect((c + quiet) * scale, (r + quiet) * scale, scale, scale);
}

let toastTimer;
export function toast(text) {
  let t = $('.toast');
  if (!t) { t = el('p', { class: 'toast', role: 'status' }); document.body.append(t); }
  t.textContent = text;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.hidden = true; }, 3500);
}

export async function copyText(text) {
  try { await navigator.clipboard.writeText(text); toast('コピーしました'); }
  catch { toast('コピーできませんでした。長押しで選んでコピーしてください'); }
}

/** コピーボタンつきの URL 表示 */
export function copyRow(text) {
  return el('div', { class: 'copy' }, el('code', {}, text), el('button', { type: 'button', class: 'btn btn--line btn--s', onclick: () => copyText(text) }, 'コピー'));
}

/** 会の日付・時間・会場 */
export function eventFacts(ev) {
  return el('dl', { class: 'facts' },
    el('div', {}, el('dt', {}, '開催日'), el('dd', {}, fmtDate(ev.held_on) + (ev.time_note ? `　${ev.time_note}` : ''))),
    ev.venue ? el('div', {}, el('dt', {}, '会場'), el('dd', {}, ev.venue)) : null);
}

// ブラウザの保存領域は使えないことがあるので、失敗しても先へ進む
export const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* 保存できなくても動く */ } },
};

export function showError(root, message) {
  put(root, el('p', { class: 'msg msg--err', role: 'alert' }, message));
}
