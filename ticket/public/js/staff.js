// 受付スタッフ・主催者の画面：入場、名簿、設定
import { $, api, copyRow, drawQr, el, eventFacts, fmtDate, fmtTime, put, qs, showError, toast } from './common.js';

const app = $('#app');
const id = qs.get('e') || '', key = qs.get('k') || '';
const base = `staff/${encodeURIComponent(id)}`;
const call = (path = '', opts = {}) => api(base + (path ? `/${path}` : ''), { ...opts, key });

let ev, summary, mailOn = false, people = [], tab = 'door', filter = '', scanning = null;
const METHOD = { qr: 'QRコード', touch: 'タッチ', door: '受付のタグ', staff: '受付で確認' };

const first = await call();
if (!first.ok) showError(app, first.message || 'このURLでは開けません。');
else {
  ({ event: ev, summary, mail: mailOn } = first);
  await loadPeople();
  draw();
  setInterval(async () => { // ほかの受付スタッフの操作や、タッチでの入場を取り込む
    if (document.visibilityState !== 'visible' || ev.closed || document.activeElement?.matches('input, textarea')) return;
    const r = await call();
    if (r.ok) { ({ event: ev, summary } = r); await loadPeople(); if (!scanning) draw(); else drawCounts(); }
  }, 10000);
}

async function loadPeople() {
  if (ev.closed) { people = []; return; }
  const r = await call('attendees');
  if (r.ok) people = r.attendees;
}
async function refresh() {
  const r = await call();
  if (r.ok) ({ event: ev, summary } = r);
  await loadPeople();
  draw();
}

function countsNode() {
  const c = (label, n, sub) => el('div', { class: 'count' }, el('dt', {}, label), el('dd', {}, String(n), sub ? el('small', {}, sub) : null));
  return el('dl', { class: 'counts', id: 'counts' },
    c('来場', summary.checked_in, `/ ${summary.venue_total}`), c('会場の申込', summary.venue_total, `定員 ${ev.capacity}`),
    c('オンラインの申込', summary.online_total), c('配信を開いた人', summary.online_watched));
}
function drawCounts() { $('#counts')?.replaceWith(countsNode()); }

function draw() {
  stopScan();
  const tabs = [['door', '受付'], ['list', '名簿'], ['set', '設定']];
  const head = [
    el('a', { class: 'brand', href: '/' }, 'KARURA LIVE', el('small', {}, 'カルラライブ')),
    el('div', { class: 'stack' },
      el('div', { class: 'row' }, el('span', { class: `tag${ev.reception_open ? '' : ' tag--off'}` }, ev.closed ? '終了' : ev.reception_open ? '受付中' : '受付前'), el('span', { class: 'note' }, '受付スタッフ用')),
      el('h1', { class: 'h1' }, ev.title), eventFacts(ev)),
    countsNode(),
  ];
  if (ev.closed) {
    put(app, ...head, el('p', { class: 'msg' }, `名簿は ${fmtTime(ev.purged_at)}（${ev.purged_at.slice(0, 10)}）に削除しました。集計は開催報告でご覧いただけます。`), reportLink());
    return;
  }
  const bar = el('div', { class: 'tabs', role: 'tablist' }, tabs.map(([k, t]) =>
    el('button', { class: 'tab', role: 'tab', type: 'button', 'aria-selected': String(tab === k), onclick: () => { tab = k; draw(); } }, t)));
  const panel = el('section', { class: 'stack', role: 'tabpanel' }, tab === 'door' ? doorTab() : tab === 'list' ? listTab() : setTab());
  put(app, ...head, bar, panel);
}

const reportLink = () => el('a', { class: 'btn btn--line', href: `/report?e=${encodeURIComponent(id)}&k=${encodeURIComponent(key)}` }, '開催報告を開く');

// ------------------------------------------------------------------ 受付
function doorTab() {
  const result = el('div', { id: 'result', 'aria-live': 'assertive' });
  const toggle = el('button', { class: `btn ${ev.reception_open ? 'btn--line' : ''}`, type: 'button' }, ev.reception_open ? '受付を終了する' : '受付を始める');
  toggle.addEventListener('click', async () => {
    toggle.disabled = true;
    const r = await call('', { method: 'PATCH', body: { reception_open: !ev.reception_open } });
    if (r.ok) { ev = r.event; draw(); } else { toggle.disabled = false; toast(r.message); }
  });
  const scanBtn = el('button', { class: 'btn btn--xl btn--full', type: 'button', onclick: () => startScan(scanBox, scanBtn) }, 'QRコードを読み取る');
  const scanBox = el('div', { class: 'stack', hidden: true });
  const search = el('input', { class: 'inp', type: 'search', placeholder: '名前・所属・メールでさがす', value: filter, 'aria-label': '名簿をさがす', autocomplete: 'off' });
  const list = el('ul', { class: 'people' });
  const fill = () => {
    const q = filter.trim().toLowerCase();
    const hit = q ? people.filter((p) => `${p.name} ${p.org} ${p.email}`.toLowerCase().includes(q)).slice(0, 30) : [];
    put(list, ...hit.map((p) => personRow(p, true)));
    if (q && !hit.length) list.append(el('li', { class: 'note' }, '名簿に見つかりません。下の「当日受付」から追加できます。'));
  };
  search.addEventListener('input', () => { filter = search.value; fill(); });
  fill();

  const wName = el('input', { class: 'inp', id: 'w-name', maxlength: '80', required: true, autocomplete: 'off' });
  const wOrg = el('input', { class: 'inp', id: 'w-org', maxlength: '120', autocomplete: 'off' });
  const walkin = el('form', { class: 'box stack' }, el('h2', { class: 'h2' }, '当日受付（名簿にない方）'),
    el('div', { class: 'row' }, el('div', { class: 'fld grow' }, el('label', { for: 'w-name' }, 'お名前'), wName), el('div', { class: 'fld grow' }, el('label', { for: 'w-org' }, 'ご所属'), wOrg)),
    el('button', { class: 'btn btn--line', type: 'submit' }, '名簿に追加して入場済みにする'));
  walkin.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!wName.value.trim()) return wName.focus();
    const r = await call('attendees', { method: 'POST', body: { name: wName.value, org: wOrg.value, kind: 'venue', checkin: true } });
    if (!r.ok) return toast(r.message);
    await refresh();
    show({ ok: true, name: r.checkin.name, org: r.checkin.org, checked_in_at: r.checkin.checked_in_at });
  });

  return [
    el('div', { class: `box ${ev.reception_open ? 'box--wash' : ''} row row--between` },
      el('p', { class: 'grow' }, ev.reception_open ? 'タッチ（4桁のコード）と受付のタグで入場できます。' : '受付を始めるまで、参加者はタッチやタグで入場できません。QRコードの読み取りと、名簿からの入場は、いつでも使えます。'), toggle),
    ev.reception_open ? el('div', { class: 'row' }, el('span', { class: 'note' }, '4桁のコード'), el('span', { class: 'bigcode' }, ev.door_code)) : null,
    scanBtn, scanBox, result,
    el('div', { class: 'stack' }, search, list), walkin,
  ];
}

function show(r) {
  const box = $('#result');
  if (!box) return;
  const cls = !r.ok ? 'result result--ng' : r.already ? 'result result--again' : 'result';
  const title = !r.ok ? (r.message || '入場を記録できませんでした') : r.already ? `すでに入場済みです（${fmtTime(r.checked_in_at)}）` : '入場しました';
  put(box, el('div', { class: cls, role: 'status' }, el('span', {}, title),
    r.name ? el('b', {}, `${r.name} 様`) : null, r.org ? el('span', {}, r.org) : null,
    r.ok && r.kind === 'online' ? el('span', {}, 'オンライン視聴で申し込まれた方です') : null));
  try { navigator.vibrate?.(r.ok && !r.already ? 80 : [80, 60, 80]); } catch { /* 振動できない端末でも動く */ }
}

async function checkin(bodyObj) {
  const r = await call('checkin', { method: 'POST', body: bodyObj });
  show(r);
  if (r.ok) {
    const p = people.find((x) => x.id === r.id);
    if (p) { p.checked_in_at = r.checked_in_at; p.checkin_method = r.checkin_method; }
    if (!r.already) summary.checked_in += 1;
    drawCounts();
  }
  return r;
}

function personRow(p, compact) {
  const sub = [p.org, p.kind === 'online' ? 'オンライン' : null, p.checked_in_at ? `${fmtTime(p.checked_in_at)} 入場（${METHOD[p.checkin_method] || ''}）` : null,
    !compact && p.email ? p.email : null, !compact && p.watched_at ? '配信を開いた' : null, !compact && p.locked ? 'コードの入力が止まっています' : null].filter(Boolean).join('　');
  const act = el('div', { class: 'person-act' });
  if (p.checked_in_at) {
    act.append(el('button', { class: 'btn btn--line btn--s', type: 'button', onclick: async () => {
      if (!confirm(`${p.name} 様の入場を取り消しますか？`)) return;
      const r = await call('undo', { method: 'POST', body: { id: p.id } });
      if (r.ok) refresh(); else toast(r.message);
    } }, '取り消す'));
  } else {
    act.append(el('button', { class: 'btn btn--s', type: 'button', onclick: async () => { const r = await checkin({ id: p.id }); if (r.ok) draw(); } }, '入場'));
  }
  if (!compact) {
    act.append(el('button', { class: 'btn btn--line btn--s', type: 'button', 'aria-label': `${p.name} 様を名簿から消す`, onclick: async () => {
      if (!confirm(`${p.name} 様を名簿から消しますか？ 元に戻せません。`)) return;
      const r = await call(`attendees/${p.id}`, { method: 'DELETE' });
      if (r.ok) refresh(); else toast(r.message);
    } }, '消す'));
  }
  return el('li', { class: `person${p.checked_in_at ? ' is-in' : ''}` }, el('span', { class: 'person-name' }, p.name), el('span', { class: 'person-sub' }, sub), act);
}

// ------------------------------------------------------------------ QRコードの読み取り
async function startScan(box, btn) {
  if (!navigator.mediaDevices?.getUserMedia) return toast('このブラウザではカメラを使えません。名簿から入場を記録してください。');
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false }); }
  catch { return toast('カメラを使えませんでした。ブラウザの設定でカメラを許可してください。'); }
  const video = el('video', { playsinline: true, muted: true, autoplay: true });
  video.srcObject = stream;
  put(box, el('div', { class: 'scan' }, video, el('span', { class: 'scan-frame', 'aria-hidden': 'true' })),
    el('button', { class: 'btn btn--line btn--full', type: 'button', onclick: draw }, '読み取りを終える'));
  box.hidden = false; btn.hidden = true;
  await video.play().catch(() => {});

  const state = scanning = { stream, stop: false };
  let detect;
  if ('BarcodeDetector' in window) {
    const d = new BarcodeDetector({ formats: ['qr_code'] });
    detect = async () => (await d.detect(video))[0]?.rawValue;
  } else { // BarcodeDetector がないブラウザ（iPhone の Safari など）は、jsQR で読む
    const { default: jsQR } = await import('../vendor/jsqr.js');
    const canvas = document.createElement('canvas'), g = canvas.getContext('2d', { willReadFrequently: true });
    detect = async () => {
      const w = video.videoWidth, h = video.videoHeight;
      if (!w) return null;
      const s = Math.min(1, 640 / Math.max(w, h));
      canvas.width = Math.round(w * s); canvas.height = Math.round(h * s);
      g.drawImage(video, 0, 0, canvas.width, canvas.height);
      return jsQR(g.getImageData(0, 0, canvas.width, canvas.height).data, canvas.width, canvas.height, { inversionAttempts: 'dontInvert' })?.data;
    };
  }
  let last = '', lastAt = 0, busy = false;
  const loop = async () => {
    if (state.stop) return;
    try {
      const text = busy ? null : await detect();
      const tk = text && tokenOf(text);
      if (tk && (tk !== last || Date.now() - lastAt > 4000)) { // 同じチケットを続けて読まない
        last = tk; lastAt = Date.now(); busy = true;
        await checkin({ token: tk });
        busy = false;
      } else if (text && !tk && Date.now() - lastAt > 4000) { lastAt = Date.now(); show({ ok: false, message: 'チケットのQRコードではありません' }); }
    } catch { busy = false; }
    setTimeout(loop, 200);
  };
  loop();
}
function stopScan() {
  if (!scanning) return;
  scanning.stop = true;
  scanning.stream.getTracks().forEach((t) => t.stop());
  scanning = null;
}
/** QRコードの中身（チケットのURL）から、チケットの鍵を取り出す */
function tokenOf(text) {
  try { const u = new URL(text); const k = u.searchParams.get('k'); if (u.pathname === '/t' && k) return k; } catch { /* URL でなければ下へ */ }
  return /^[A-Za-z0-9_-]{20,24}$/.test(text) ? text : null;
}

// ------------------------------------------------------------------ 名簿
function listTab() {
  const file = el('input', { type: 'file', accept: '.csv,text/csv,text/plain', class: 'vh', id: 'csv' });
  file.addEventListener('change', async () => {
    const f = file.files[0];
    if (!f) return;
    if (f.size > 300_000) return toast('ファイルが大きすぎます。300KB までに分けてください。');
    const r = await call('import', { method: 'POST', body: { csv: await readText(f) } });
    file.value = '';
    if (!r.ok) return toast(r.message);
    await refresh();
    const note = r.skipped.length ? `${r.added}人を追加しました。${r.skipped.length}行は取り込みませんでした（${r.skipped.slice(0, 3).map((s) => `${s.line}行目：${s.reason}`).join('、')}${r.skipped.length > 3 ? ' ほか' : ''}）` : `${r.added}人を追加しました。`;
    $('#import-msg').textContent = note; $('#import-msg').hidden = false;
  });
  const unsent = people.filter((p) => p.email && !p.mailed_at).length;
  const mailBtn = el('button', { class: 'btn btn--line', type: 'button', disabled: !unsent }, `チケットをメールで送る（未送信 ${unsent}人）`);
  mailBtn.addEventListener('click', async () => {
    if (!confirm(`まだ送っていない ${unsent}人に、チケットのメールを送ります。よろしいですか？`)) return;
    mailBtn.disabled = true;
    let sent = 0, failed = 0;
    for (;;) { // 少しずつ送る
      const r = await call('mail', { method: 'POST', body: {} });
      if (!r.ok) { toast(r.message); break; }
      sent += r.sent; failed += r.failed;
      mailBtn.textContent = `送信中… ${sent}人`;
      if (!r.remaining || (!r.sent && r.failed)) break;
    }
    await refresh();
    toast(failed ? `${sent}人に送りました。${failed}人には送れませんでした。` : `${sent}人に送りました。`);
  });
  const dl = el('button', { class: 'btn btn--line', type: 'button' }, '名簿をCSVで書き出す');
  dl.addEventListener('click', async () => { // 鍵を URL に載せないよう、ヘッダーで送って受け取る
    const res = await fetch(`/api/${base}/export.csv`, { headers: { authorization: `Bearer ${key}` }, cache: 'no-store' }).catch(() => null);
    if (!res?.ok) return toast('書き出せませんでした。');
    const a = el('a', { href: URL.createObjectURL(await res.blob()), download: `meibo-${ev.id}.csv` });
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 10000);
  });
  return [
    el('div', { class: 'row' }, el('label', { class: 'btn', for: 'csv' }, '名簿のCSVを取り込む'), file, dl, mailOn ? mailBtn : null),
    el('p', { class: 'msg', id: 'import-msg', hidden: true, role: 'status' }),
    el('p', { class: 'note' }, 'CSVは「名前, メール, 所属, 区分（会場／オンライン）」の順。1行目が見出しなら、その並びに合わせます。書き出したCSVには、1人ずつのチケットのURLが入ります。',
      mailOn ? '' : 'このサーバーではメールを送りません。チケットのURLは、書き出したCSVからお送りください。'),
    el('h2', { class: 'h2' }, `名簿（${people.length}人）`),
    people.length ? el('ul', { class: 'people' }, people.map((p) => personRow(p, false))) : el('p', { class: 'note' }, 'まだ誰も入っていません。CSVを取り込むか、設定の「申込フォーム」を開けてください。'),
  ];
}
function readText(f) {
  return new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(String(r.result)); r.onerror = rej; r.readAsText(f); });
}

// ------------------------------------------------------------------ 設定
function setTab() {
  const qrOf = (text, label) => { const c = el('canvas', { class: 'qr', role: 'img', 'aria-label': label }); drawQr(c, text); return c; };
  const patch = async (bodyObj, done) => {
    const r = await call('', { method: 'PATCH', body: bodyObj });
    if (!r.ok) return toast(r.message);
    ev = r.event; draw(); if (done) toast(done);
  };
  const online = el('input', { class: 'inp', id: 'online', type: 'number', min: '0', inputmode: 'numeric', value: ev.online_manual ?? '' });
  const onlineForm = el('form', { class: 'row' }, el('div', { class: 'fld grow' }, el('label', { for: 'online' }, 'オンライン視聴者数（配信サービスの数字）'), online), el('button', { class: 'btn btn--line', type: 'submit' }, '保存'));
  onlineForm.addEventListener('submit', (e) => { e.preventDefault(); patch({ online_manual: online.value === '' ? null : Number(online.value) }, '保存しました'); });
  return [
    el('div', { class: 'card stack' }, el('h2', { class: 'h2' }, 'タッチで入場：4桁のコード'),
      el('p', { class: 'bigcode' }, ev.door_code),
      el('p', { class: 'note' }, '受付に掲示するか、口頭でお伝えください。参加者がチケットの「タッチで入場する」に入力すると、入場済みになります。受付中だけ使えます。'),
      el('div', {}, el('button', { class: 'btn btn--line btn--s', type: 'button', onclick: () => confirm('コードを作り直しますか？ いまのコードは使えなくなります。') && patch({ new_door_code: true }, 'コードを作り直しました') }, 'コードを作り直す'))),
    el('div', { class: 'card stack' }, el('h2', { class: 'h2' }, 'タッチで入場：受付に置くタグ'),
      el('p', { class: 'note' }, 'このURLをNFCタグに書き込むか、下のQRコードを受付に掲示してください。チケットを開いたことのあるスマホでかざすと、入場済みになります。受付中だけ使えます。'),
      copyRow(ev.door_url), qrOf(ev.door_url, '受付に掲示するQRコード')),
    el('div', { class: 'card stack' }, el('div', { class: 'row row--between' }, el('h2', { class: 'h2' }, '申込フォーム'), el('span', { class: `tag${ev.registration_open ? '' : ' tag--off'}` }, ev.registration_open ? '受付中' : '閉じています')),
      el('p', { class: 'note' }, `参加者がここから申し込むと、その場でチケットが発行されます。${ev.line ? 'LINEでの申込も使えます。' : ''}会場の定員は ${ev.capacity}人です。`),
      copyRow(ev.join_url), ev.registration_open ? qrOf(ev.join_url, '申込フォームのQRコード') : null,
      el('div', {}, el('button', { class: `btn ${ev.registration_open ? 'btn--line' : ''}`, type: 'button', onclick: () => patch({ registration_open: !ev.registration_open }) }, ev.registration_open ? '申込を締め切る' : '申込を受け付ける'))),
    el('div', { class: 'card stack' }, el('h2', { class: 'h2' }, '開催報告'), onlineForm,
      el('p', { class: 'note' }, 'チケットから配信を開いた人数は自動で数えます。YouTube や Zoom の視聴者数は、ここに入力すると報告に載ります。'), el('div', {}, reportLink())),
    el('p', { class: 'note' }, `名簿は ${fmtDate(ev.purge_on)} を過ぎると自動で削除されます（会の終了から${ev.retention_days}日）。集計だけが残ります。`),
  ];
}
