// 通しの確認：会を作る → 名簿を入れる → 入場する → 報告 → 名簿を消す
// wrangler dev をこのテストの中で立ち上げ、LINE は手元に立てた代わりのサーバーで確かめる。
//   npm test
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import { createServer } from 'node:http';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const PORT = 8792, LINE_PORT = 8799;
const ORIGIN = `http://127.0.0.1:${PORT}`;
const ADMIN = 'test-admin-key';
const state = mkdtempSync(join(tmpdir(), 'karura-ticket-'));
let dev, line;
const lineUsers = { 'code-a': { userId: 'U-aaa', friend: true }, 'code-b': { userId: 'U-bbb', friend: false } };

async function call(path, { method = 'GET', body, key, headers = {}, redirect = 'manual' } = {}) {
  const h = { ...headers };
  if (body !== undefined && !h['content-type']) h['content-type'] = 'application/json';
  if (key) h.authorization = `Bearer ${key}`;
  const res = await fetch(`${ORIGIN}${path}`, { method, headers: h, redirect, body: body === undefined ? undefined : typeof body === 'string' ? body : JSON.stringify(body) });
  const text = await res.text();
  let data; try { data = JSON.parse(text); } catch { data = text; }
  return { status: res.status, data, headers: res.headers };
}

before(async () => {
  // LINE の代わり：トークン、プロフィール、友だちの状態を返す
  line = createServer((req, res) => {
    let raw = '';
    req.on('data', (c) => { raw += c; });
    req.on('end', () => {
      const send = (code, obj) => { res.writeHead(code, { 'content-type': 'application/json' }); res.end(JSON.stringify(obj)); };
      if (req.url === '/oauth2/v2.1/token') {
        const p = new URLSearchParams(raw);
        if (p.get('client_secret') !== 'line-secret' || !lineUsers[p.get('code')]) return send(400, { error: 'invalid_grant' });
        return send(200, { access_token: p.get('code') });
      }
      const user = lineUsers[(req.headers.authorization || '').replace('Bearer ', '')];
      if (!user) return send(401, {});
      if (req.url === '/v2/profile') return send(200, { userId: user.userId, displayName: 'LINEの名前' });
      if (req.url === '/friendship/v1/status') return send(200, { friendFlag: user.friend });
      send(404, {});
    });
  }).listen(LINE_PORT, '127.0.0.1');

  const wrangler = join(root, 'node_modules/.bin/wrangler');
  execFileSync(wrangler, ['d1', 'migrations', 'apply', 'karura-ticket-db', '--local', '--persist-to', state], { cwd: root, stdio: 'pipe', env: { ...process.env, CI: '1' } });
  dev = spawn(wrangler, ['dev', '--port', String(PORT), '--ip', '127.0.0.1', '--persist-to', state, '--test-scheduled',
    '--var', `ADMIN_KEY:${ADMIN}`, '--var', 'SESSION_SECRET:test-session-secret',
    '--var', `LINE_AUTH_BASE:http://127.0.0.1:${LINE_PORT}`, '--var', `LINE_API_BASE:http://127.0.0.1:${LINE_PORT}`],
    { cwd: root, stdio: 'pipe', env: { ...process.env, CI: '1' } });
  for (let i = 0; i < 120; i++) {
    try { if ((await fetch(`${ORIGIN}/api/config`)).ok) return; } catch { /* まだ立ち上がっていない */ }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error('wrangler dev が立ち上がりませんでした');
});

after(() => {
  dev?.kill('SIGTERM');
  line?.close();
  rmSync(state, { recursive: true, force: true });
});

const today = new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);
let ev, staffKey, doorKey;

test('管理：鍵がなければ会を作れない', async () => {
  assert.equal((await call('/api/admin/events')).status, 401);
  assert.equal((await call('/api/admin/events', { key: 'wrong' })).status, 401);
});

test('管理：会を作る', async () => {
  const bad = await call('/api/admin/events', { method: 'POST', key: ADMIN, body: { title: '', held_on: today } });
  assert.equal(bad.status, 400);
  const r = await call('/api/admin/events', { method: 'POST', key: ADMIN, body: { title: '公開シンポジウム', held_on: today, venue: '大ホール', capacity: 3, stream_url: 'https://example.com/live', registration_open: true } });
  assert.equal(r.status, 201);
  const list = await call('/api/admin/events', { key: ADMIN });
  ev = list.data.events.find((e) => e.id === r.data.id);
  assert.ok(ev);
  staffKey = new URL(ev.staff_url).searchParams.get('k');
  doorKey = new URL(ev.door_url).searchParams.get('k');
  assert.match(ev.door_code, /^\d{4}$/);
  assert.equal(JSON.stringify(list.data).includes('line_secret'), false);
});

test('受付スタッフ：鍵が違えば開けない。会がない場合と見分けがつかない', async () => {
  const a = await call(`/api/staff/${ev.id}`, { key: 'wrong' });
  const b = await call('/api/staff/nosuchevent', { key: 'wrong' });
  assert.equal(a.status, 401);
  assert.deepEqual(a.data, b.data);
});

test('名簿：CSVを取り込む（見出しあり、重複と不正な行は飛ばす）', async () => {
  const csv = '﻿所属,氏名,メール,区分\r\n"東京, 大学",山田 花子,Hanako@Example.ac.jp,会場\r\n,=cmd|calc,evil@example.com,オンライン\r\n,,noname@example.com,会場\r\n,重複 太郎,hanako@example.ac.jp,会場\r\n,形式 違い,not-an-email,会場\r\n';
  const r = await call(`/api/staff/${ev.id}/import`, { method: 'POST', key: staffKey, body: { csv } });
  assert.equal(r.data.added, 2);
  assert.equal(r.data.skipped.length, 3);
  const list = await call(`/api/staff/${ev.id}/attendees`, { key: staffKey });
  const hanako = list.data.attendees.find((a) => a.name === '山田 花子');
  assert.equal(hanako.email, 'hanako@example.ac.jp');
  assert.equal(hanako.org, '東京, 大学');
  assert.equal(list.data.attendees.find((a) => a.name === '=cmd|calc').kind, 'online');
});

test('名簿：書き出したCSVは、式として動かない', async () => {
  const res = await fetch(`${ORIGIN}/api/staff/${ev.id}/export.csv`, { headers: { authorization: `Bearer ${staffKey}` } });
  const bytes = new Uint8Array(await res.arrayBuffer());
  assert.deepEqual([...bytes.slice(0, 3)], [0xef, 0xbb, 0xbf]); // Excel で文字化けしないよう、先頭に BOM を付けている
  const text = new TextDecoder().decode(bytes);
  assert.ok(text.startsWith('名前,'));
  assert.ok(text.includes("'=cmd|calc"));
  assert.ok(text.includes('"東京, 大学"'));
  assert.match(text, /\/t\?k=[A-Za-z0-9_-]{22}/);
  assert.equal((await call(`/api/staff/${ev.id}/export.csv`)).status, 401);
});

let hanakoToken;
test('入場：受付のスマホでQRコードを読む。2回目は「すでに入場済み」', async () => {
  const csv = await (await fetch(`${ORIGIN}/api/staff/${ev.id}/export.csv`, { headers: { authorization: `Bearer ${staffKey}` } })).text();
  hanakoToken = csv.split('\r\n').find((l) => l.includes('山田 花子')).match(/k=([A-Za-z0-9_-]+)/)[1];
  const a = await call(`/api/staff/${ev.id}/checkin`, { method: 'POST', key: staffKey, body: { token: hanakoToken } });
  assert.equal(a.data.already, false);
  assert.equal(a.data.checkin_method, 'qr');
  const b = await call(`/api/staff/${ev.id}/checkin`, { method: 'POST', key: staffKey, body: { token: hanakoToken } });
  assert.equal(b.data.already, true);
  assert.equal(b.data.checked_in_at, a.data.checked_in_at);
  const none = await call(`/api/staff/${ev.id}/checkin`, { method: 'POST', key: staffKey, body: { token: 'x'.repeat(22) } });
  assert.equal(none.status, 404);
});

test('入場：取り消せる', async () => {
  const list = await call(`/api/staff/${ev.id}/attendees`, { key: staffKey });
  const id = list.data.attendees.find((a) => a.name === '山田 花子').id;
  assert.equal((await call(`/api/staff/${ev.id}/undo`, { method: 'POST', key: staffKey, body: { id } })).status, 200);
  const t = await call(`/api/t/${hanakoToken}`);
  assert.equal(t.data.ticket.checked_in_at, null);
  assert.equal('email' in t.data.ticket, false);
});

test('申込：フォームから申し込むとチケットが出る。同じメールでは他人のチケットを出さない', async () => {
  const r = await call(`/api/e/${ev.id}/join`, { method: 'POST', body: { name: '佐藤 次郎', email: 'jiro@example.com', kind: 'venue' } });
  assert.equal(r.status, 201);
  assert.match(r.data.ticket_url, /\/t\?k=/);
  const dup = await call(`/api/e/${ev.id}/join`, { method: 'POST', body: { name: 'なりすまし', email: 'JIRO@example.com', kind: 'venue' } });
  assert.equal(dup.status, 409);
  assert.equal('ticket_url' in dup.data, false);
  const bot = await call(`/api/e/${ev.id}/join`, { method: 'POST', body: { name: 'bot', email: 'bot@example.com', website: 'http://spam' } });
  assert.equal(bot.status, 200);
  const list = await call(`/api/staff/${ev.id}/attendees`, { key: staffKey });
  assert.equal(list.data.attendees.some((a) => a.name === 'bot'), false);
});

let jiroToken;
test('タッチ：受付前は入れない。受付中は4桁のコードで入場。5回まちがえると止まる', async () => {
  const list = await (await fetch(`${ORIGIN}/api/staff/${ev.id}/export.csv`, { headers: { authorization: `Bearer ${staffKey}` } })).text();
  jiroToken = list.split('\r\n').find((l) => l.includes('佐藤 次郎')).match(/k=([A-Za-z0-9_-]+)/)[1];
  assert.equal((await call(`/api/t/${jiroToken}/touch`, { method: 'POST', body: { code: ev.door_code } })).status, 403);
  const open = await call(`/api/staff/${ev.id}`, { method: 'PATCH', key: staffKey, body: { reception_open: true, title: '書き換え' } });
  assert.equal(open.data.event.reception_open, true);
  assert.equal(open.data.event.title, '公開シンポジウム'); // 受付スタッフは会の名称を変えられない
  const wrong = ev.door_code === '0000' ? '1111' : '0000';
  for (let i = 0; i < 5; i++) assert.equal((await call(`/api/t/${hanakoToken}/touch`, { method: 'POST', body: { code: wrong } })).status, 400);
  assert.equal((await call(`/api/t/${hanakoToken}/touch`, { method: 'POST', body: { code: ev.door_code } })).status, 423);
  const ok = await call(`/api/t/${jiroToken}/touch`, { method: 'POST', body: { code: ev.door_code } });
  assert.equal(ok.data.checkin_method, 'touch');
});

test('受付のタグ：チケットを開いたスマホなら入力なし、なければメールアドレスで入場', async () => {
  assert.equal((await call(`/api/door/${ev.id}`, { method: 'POST', body: { key: 'wrong', token: hanakoToken } })).status, 404);
  const a = await call(`/api/door/${ev.id}`, { method: 'POST', body: { key: doorKey, token: hanakoToken } });
  assert.equal(a.data.checkin_method, 'door');
  const again = await call(`/api/door/${ev.id}`, { method: 'POST', body: { key: doorKey, email: 'hanako@example.ac.jp' } });
  assert.equal(again.data.already, true);
  assert.equal((await call(`/api/door/${ev.id}`, { method: 'POST', body: { key: doorKey, email: 'nobody@example.com' } })).status, 404);
});

test('当日受付：名簿にない人を足して入場済みにする', async () => {
  const r = await call(`/api/staff/${ev.id}/attendees`, { method: 'POST', key: staffKey, body: { name: '当日 三郎', checkin: true } });
  assert.equal(r.status, 201);
  assert.equal(r.data.checkin.checkin_method, 'staff');
});

test('定員：会場が埋まったら、オンラインだけ受け付ける', async () => {
  const full = await call(`/api/e/${ev.id}/join`, { method: 'POST', body: { name: '四人目', email: 'four@example.com', kind: 'venue' } });
  assert.equal(full.status, 409);
  assert.equal(full.data.code, 'full');
  assert.equal((await call(`/api/e/${ev.id}`)).data.event.venue_full, true);
  const online = await call(`/api/e/${ev.id}/join`, { method: 'POST', body: { name: '四人目', email: 'four@example.com', kind: 'online' } });
  assert.equal(online.status, 201);
  const token = new URL(online.data.ticket_url).searchParams.get('k');
  const w = await call(`/api/t/${token}/watch`, { method: 'POST', body: {} });
  assert.equal(w.data.url, 'https://example.com/live');
});

test('LINE：申込 → 同意 → チケット。友だちの数が報告に載る', async () => {
  const set = await call(`/api/admin/events/${ev.id}`, { method: 'PATCH', key: ADMIN, body: { line_channel_id: '1234567890', line_channel_secret: 'line-secret', capacity: 10 } });
  assert.equal(set.status, 200);
  assert.equal((await call(`/api/e/${ev.id}`)).data.event.line, true);

  async function lineJoin(code, name, changed) {
    const start = await call(`/api/e/${ev.id}/line/start`, { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams({ name, org: '', kind: 'venue' }).toString() });
    assert.equal(start.status, 303);
    const to = new URL(start.headers.get('location'));
    assert.equal(to.origin, `http://127.0.0.1:${LINE_PORT}`);
    assert.equal(to.searchParams.get('bot_prompt'), 'aggressive');
    assert.equal(to.searchParams.get('client_id'), '1234567890');
    assert.equal(to.searchParams.get('redirect_uri'), `${ORIGIN}/api/line/callback`);
    assert.equal(to.search.includes(encodeURIComponent(name)), false); // 名前は LINE に送らない
    const jar = start.headers.get('set-cookie').split(';')[0];
    return { jar, state: to.searchParams.get('state'), cb: (s, c = jar) => call(`/api/line/callback?code=${code}&state=${s}${changed ? '&friendship_status_changed=true' : ''}`, { headers: { cookie: c } }) };
  }

  const a = await lineJoin('code-a', 'LINE 一郎', true);
  const forged = await a.cb('forged-state');
  assert.match(forged.headers.get('location'), /err=line/);
  const noCookie = await call(`/api/line/callback?code=code-a&state=${a.state}`);
  assert.equal(noCookie.headers.get('location'), `${ORIGIN}/`);
  const ok = await a.cb(a.state);
  assert.match(ok.headers.get('location'), /\/t\?k=[A-Za-z0-9_-]{22}&new=1$/);
  const tokenA = new URL(ok.headers.get('location')).searchParams.get('k');
  assert.equal((await call(`/api/t/${tokenA}`)).data.ticket.name, 'LINE 一郎');

  const again = await lineJoin('code-a', '別の名前', false); // 同じ人がもう一度：同じチケットが開く
  assert.equal(new URL((await again.cb(again.state)).headers.get('location')).searchParams.get('k'), tokenA);

  const b = await lineJoin('code-b', 'LINE 二郎', false);
  assert.match((await b.cb(b.state)).headers.get('location'), /\/t\?k=/);

  const rep = await call(`/api/staff/${ev.id}/report`, { key: staffKey });
  assert.equal(rep.data.summary.line_joined, 2);
  assert.equal(rep.data.summary.line_friends, 1);
  assert.equal(rep.data.summary.line_friends_new, 1);
});

test('報告：数字が合う', async () => {
  await call(`/api/staff/${ev.id}`, { method: 'PATCH', key: staffKey, body: { online_manual: 48 } });
  const s = (await call(`/api/staff/${ev.id}/report`, { key: staffKey })).data.summary;
  assert.equal(s.venue_total, 5);   // 花子、次郎、三郎、LINE 2人
  assert.equal(s.online_total, 2);  // CSVの1人、四人目
  assert.equal(s.checked_in, 3);
  assert.deepEqual(s.by_method, { qr: 0, touch: 1, door: 1, staff: 1 });
  assert.equal(s.online_watched, 1);
  assert.equal(s.online_manual, 48);
  assert.equal(s.timeline.reduce((n, t) => n + t.n, 0), 3);
});

test('削除：保存期間を過ぎた会は、名簿が消えて集計だけ残る', async () => {
  const old = await call('/api/admin/events', { method: 'POST', key: ADMIN, body: { title: '去年の会', held_on: '2025-01-10', retention_days: 30 } });
  const oldEv = (await call('/api/admin/events', { key: ADMIN })).data.events.find((e) => e.id === old.data.id);
  const oldKey = new URL(oldEv.staff_url).searchParams.get('k');
  const add = await call(`/api/staff/${oldEv.id}/attendees`, { method: 'POST', key: oldKey, body: { name: '消える人', email: 'gone@example.com', checkin: true } });
  const goneToken = new URL(add.data.ticket_url).searchParams.get('k');

  assert.equal((await fetch(`${ORIGIN}/cdn-cgi/handler/scheduled?cron=17+18+*+*+*`)).status, 200); // 毎日の定時の処理
  for (let i = 0; i < 20; i++) { // 定時の処理は裏で走るので、終わるのを待つ
    if ((await call(`/api/t/${goneToken}`)).status === 404) break;
    await new Promise((r) => setTimeout(r, 250));
  }
  assert.equal((await call(`/api/t/${goneToken}`)).status, 404);
  assert.equal((await call(`/api/staff/${oldEv.id}/attendees`, { key: oldKey })).status, 410);
  const rep = await call(`/api/staff/${oldEv.id}/report`, { key: oldKey });
  assert.equal(rep.data.summary.checked_in, 1);
  assert.equal(rep.data.event.closed, true);
  assert.equal(JSON.stringify(rep.data).includes('消える人'), false);

  const still = await call(`/api/t/${hanakoToken}`); // 期間内の会はそのまま
  assert.equal(still.status, 200);
});

test('削除：1人だけ消す、会ごと消す', async () => {
  const list = await call(`/api/staff/${ev.id}/attendees`, { key: staffKey });
  const id = list.data.attendees.find((a) => a.name === '山田 花子').id;
  assert.equal((await call(`/api/staff/${ev.id}/attendees/${id}`, { method: 'DELETE', key: staffKey })).status, 200);
  assert.equal((await call(`/api/t/${hanakoToken}`)).status, 404);
  assert.equal((await call(`/api/admin/events/${ev.id}`, { method: 'DELETE', key: ADMIN })).status, 200);
  assert.equal((await call(`/api/t/${jiroToken}`)).status, 404);
  assert.equal((await call(`/api/e/${ev.id}`)).status, 404);
});

test('ページ：静的ファイルが出て、検索に載らない設定になっている', async () => {
  for (const p of ['/', '/t', '/join', '/door', '/staff', '/report', '/admin']) {
    const res = await fetch(`${ORIGIN}${p}`);
    assert.equal(res.status, 200, p);
    assert.match(res.headers.get('x-robots-tag') || '', /noindex/, p);
    assert.match(res.headers.get('content-security-policy') || '', /script-src 'self'/, p);
  }
  assert.equal((await fetch(`${ORIGIN}/no-such-page`)).status, 404);
});
