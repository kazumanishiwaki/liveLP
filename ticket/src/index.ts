// カルラライブ 受付用デジタルチケット：API
//
//   /api/admin/*      カルラライブの担当者（ADMIN_KEY）：会を作る、LINE連携を設定する、消す
//   /api/staff/:id/*  受付スタッフ・主催者（会ごとの鍵）：入場、名簿、CSV、メール、報告
//   /api/e/:id/*      参加者：会の情報、申込
//   /api/t/:token/*   参加者：チケット、タッチで入場、配信を見る
//   /api/door/:id     受付に置いたタグ（NFC・掲示QR）からの入場
//   /api/line/*       LINEログイン
//
// チケットの販売と決済は扱わない。

import {
  Env, addDays, clean, cookie, csvCell, fail, isEmail, isHttpUrl, isYmd, json, nowIso, parseCsv,
  randomCode, randomId, randomKey, safeEqual, seal, sign, todayJst, unseal, unsign,
} from './util';
import { lineAuthorizeUrl, lineExchange } from './line';

interface EventRow {
  id: string; title: string; held_on: string; time_note: string; venue: string; capacity: number; stream_url: string;
  staff_key: string; door_key: string; door_code: string; reception_open: number; registration_open: number;
  online_manual: number | null; retention_days: number; purge_on: string; purged_at: string | null; summary_json: string | null;
  line_channel_id: string | null; line_secret_enc: string | null; created_at: string;
}
interface AttendeeRow {
  id: number; event_id: string; token: string; name: string; email: string; org: string; kind: 'venue' | 'online'; source: string;
  line_user_id: string | null; line_friend: number; line_friend_new: number; checked_in_at: string | null; checkin_method: string | null;
  watched_at: string | null; mailed_at: string | null; code_fails: number; created_at: string;
}
type Method = 'qr' | 'touch' | 'door' | 'staff';

const MAX_BODY = 400_000;      // CSV の取り込みを含めた、受け取る本文の上限（バイト）
const MAX_IMPORT_ROWS = 2000;
const CODE_FAIL_LIMIT = 5;     // 4桁コードをこの回数まちがえたチケットは、受付での対応に切り替える
const MAIL_BATCH = 20;         // 1回の操作で送るメールの数

// ------------------------------------------------------------------ DB
const getEvent = (env: Env, id: string) => env.DB.prepare('SELECT * FROM events WHERE id = ?').bind(id).first<EventRow>();

const lineOn = (ev: EventRow) => !!(ev.line_channel_id && ev.line_secret_enc);

/** だれに見せてもよい会の情報 */
function eventPublic(ev: EventRow) {
  return {
    id: ev.id, title: ev.title, held_on: ev.held_on, time_note: ev.time_note, venue: ev.venue,
    registration_open: !!ev.registration_open && !ev.purged_at, reception_open: !!ev.reception_open && !ev.purged_at,
    has_stream: !!ev.stream_url, line: lineOn(ev), closed: !!ev.purged_at,
  };
}

/** 受付スタッフに見せる会の情報 */
function eventStaff(ev: EventRow, origin: string) {
  return {
    ...eventPublic(ev), capacity: ev.capacity, stream_url: ev.stream_url, door_code: ev.door_code, online_manual: ev.online_manual,
    retention_days: ev.retention_days, purge_on: ev.purge_on, purged_at: ev.purged_at,
    join_url: `${origin}/join?e=${ev.id}`, door_url: `${origin}/door?e=${ev.id}&k=${ev.door_key}`,
  };
}

interface Summary {
  venue_total: number; online_total: number; checked_in: number; by_method: Record<Method, number>;
  online_watched: number; online_manual: number | null; line_joined: number; line_friends: number; line_friends_new: number;
  timeline: { t: string; n: number }[];
}

/** 報告に使う集計。名簿を消したあとは、消す直前に残した集計を返す */
async function summarize(env: Env, ev: EventRow): Promise<Summary> {
  if (ev.purged_at && ev.summary_json) return JSON.parse(ev.summary_json) as Summary;
  const c = await env.DB.prepare(`SELECT
      SUM(kind = 'venue') AS venue_total, SUM(kind = 'online') AS online_total,
      SUM(checked_in_at IS NOT NULL) AS checked_in,
      SUM(checkin_method = 'qr') AS qr, SUM(checkin_method = 'touch') AS touch, SUM(checkin_method = 'door') AS door, SUM(checkin_method = 'staff') AS staff,
      SUM(watched_at IS NOT NULL) AS online_watched,
      SUM(line_user_id IS NOT NULL) AS line_joined, SUM(line_friend = 1) AS line_friends, SUM(line_friend_new = 1) AS line_friends_new
    FROM attendees WHERE event_id = ?`).bind(ev.id).first<Record<string, number | null>>();
  const n = (k: string) => Number(c?.[k] ?? 0);
  const times = await env.DB.prepare('SELECT checked_in_at FROM attendees WHERE event_id = ? AND checked_in_at IS NOT NULL').bind(ev.id).all<{ checked_in_at: string }>();
  const buckets = new Map<string, number>();
  for (const r of times.results) {
    const jst = new Date(Date.parse(r.checked_in_at) + 9 * 3600 * 1000); // 日本時間で10分ごとに数える
    const t = `${String(jst.getUTCHours()).padStart(2, '0')}:${String(Math.floor(jst.getUTCMinutes() / 10) * 10).padStart(2, '0')}`;
    buckets.set(t, (buckets.get(t) || 0) + 1);
  }
  return {
    venue_total: n('venue_total'), online_total: n('online_total'), checked_in: n('checked_in'),
    by_method: { qr: n('qr'), touch: n('touch'), door: n('door'), staff: n('staff') },
    online_watched: n('online_watched'), online_manual: ev.online_manual,
    line_joined: n('line_joined'), line_friends: n('line_friends'), line_friends_new: n('line_friends_new'),
    timeline: [...buckets].sort((a, b) => a[0].localeCompare(b[0])).map(([t, k]) => ({ t, n: k })),
  };
}

interface NewAttendee { name: string; email?: string; org?: string; kind: 'venue' | 'online'; source: string; line_user_id?: string; line_friend?: boolean; line_friend_new?: boolean }

function insertAttendee(env: Env, eventId: string, a: NewAttendee, token = randomKey()) {
  return env.DB.prepare(`INSERT INTO attendees (event_id, token, name, email, org, kind, source, line_user_id, line_friend, line_friend_new, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`)
    .bind(eventId, token, a.name, a.email || '', a.org || '', a.kind, a.source, a.line_user_id ?? null, a.line_friend ? 1 : 0, a.line_friend_new ? 1 : 0, nowIso());
}

async function addAttendee(env: Env, eventId: string, a: NewAttendee): Promise<AttendeeRow> {
  const token = randomKey();
  await insertAttendee(env, eventId, a, token).run();
  return (await env.DB.prepare('SELECT * FROM attendees WHERE token = ?').bind(token).first<AttendeeRow>())!;
}

const venueCount = async (env: Env, eventId: string) =>
  Number((await env.DB.prepare("SELECT COUNT(*) AS n FROM attendees WHERE event_id = ? AND kind = 'venue'").bind(eventId).first<{ n: number }>())?.n ?? 0);

/** 入場済みにする。すでに入場済みなら already: true で、最初の入場時刻を返す */
async function checkIn(env: Env, a: AttendeeRow, method: Method) {
  const at = nowIso();
  const r = await env.DB.prepare('UPDATE attendees SET checked_in_at = ?, checkin_method = ?, code_fails = 0 WHERE id = ? AND checked_in_at IS NULL').bind(at, method, a.id).run();
  const changed = r.meta.changes > 0;
  return {
    ok: true, already: !changed, id: a.id, name: a.name, org: a.org, kind: a.kind,
    checked_in_at: changed ? at : a.checked_in_at, checkin_method: changed ? method : a.checkin_method,
  };
}

/** 保存期間を過ぎた会の名簿を消す。集計だけ残す */
async function purgeEvent(env: Env, ev: EventRow) {
  const summary = await summarize(env, ev);
  await env.DB.batch([
    env.DB.prepare(`UPDATE events SET summary_json = ?, purged_at = ?, reception_open = 0, registration_open = 0, stream_url = '',
        line_channel_id = NULL, line_secret_enc = NULL WHERE id = ?`).bind(JSON.stringify(summary), nowIso(), ev.id),
    env.DB.prepare('DELETE FROM attendees WHERE event_id = ?').bind(ev.id),
  ]);
}
async function purgeDue(env: Env): Promise<number> {
  const due = await env.DB.prepare('SELECT * FROM events WHERE purged_at IS NULL AND purge_on < ?').bind(todayJst()).all<EventRow>();
  for (const ev of due.results) await purgeEvent(env, ev);
  return due.results.length;
}

// ------------------------------------------------------------------ メール
const mailOn = (env: Env) => !!(env.RESEND_API_KEY && env.MAIL_FROM);

async function sendTicketMail(env: Env, origin: string, ev: EventRow, a: AttendeeRow): Promise<boolean> {
  if (!mailOn(env) || !a.email) return false;
  const lines = [
    `${a.name} 様`, '',
    `「${ev.title}」のチケットをお送りします。`, '',
    `${origin}/t?k=${a.token}`, '',
    a.kind === 'online' ? '当日は、上のページの「配信を見る」からご視聴ください。' : '当日は、上のページを開いて受付でお見せください。',
    '', `開催日：${ev.held_on}${ev.time_note ? '　' + ev.time_note : ''}`,
    ...(ev.venue ? [`会場：${ev.venue}`] : []),
    '', 'このメールに心当たりがない場合は、破棄してください。',
  ];
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, 'content-type': 'application/json' },
    body: JSON.stringify({ from: env.MAIL_FROM, to: [a.email], subject: `【チケット】${ev.title}`, text: lines.join('\n') }),
  });
  if (!res.ok) return false;
  await env.DB.prepare('UPDATE attendees SET mailed_at = ? WHERE id = ?').bind(nowIso(), a.id).run();
  return true;
}

// ------------------------------------------------------------------ 入力
async function body<T = Record<string, unknown>>(req: Request): Promise<T | null> {
  if (Number(req.headers.get('content-length') || 0) > MAX_BODY) return null;
  const text = await req.text();
  if (text.length > MAX_BODY) return null;
  try { const v = JSON.parse(text); return v && typeof v === 'object' ? (v as T) : null; } catch { return null; }
}
const bearer = (req: Request) => (req.headers.get('authorization') || '').replace(/^Bearer\s+/i, '');
const kindOf = (v: unknown): 'venue' | 'online' => (v === 'online' || v === 'オンライン' ? 'online' : 'venue');

const BAD = () => fail(400, 'bad_request', '送信された内容を読み取れませんでした。');
const NOT_FOUND = () => fail(404, 'not_found', '見つかりませんでした。');
const NO_EVENT = () => fail(404, 'no_event', 'この会は見つかりませんでした。URLをご確認ください。');
const CLOSED = () => fail(410, 'closed', 'この会の受付は終了し、名簿は削除されました。');

/** 会の設定を読み取って確かめる。create=true のときは必須項目もそろっているか見る */
async function readEventInput(env: Env, b: Record<string, unknown>, create: boolean) {
  const out: Record<string, string | number | null> = {};
  const err = (m: string) => ({ error: m });
  if (create || 'title' in b) { const v = clean(b.title, 120); if (!v) return err('会の名称を入力してください。'); out.title = v; }
  if (create || 'held_on' in b) { if (!isYmd(b.held_on)) return err('開催日を 2027-02-20 の形で入力してください。'); out.held_on = b.held_on; }
  if ('time_note' in b) out.time_note = clean(b.time_note, 80);
  if ('venue' in b) out.venue = clean(b.venue, 120);
  if ('capacity' in b) { const n = Number(b.capacity); if (!Number.isInteger(n) || n < 1 || n > 2000) return err('会場の定員は 1〜2000 の数字で入力してください。'); out.capacity = n; }
  if ('stream_url' in b) { const v = clean(b.stream_url, 500); if (v && !isHttpUrl(v)) return err('配信のURLは https:// から入力してください。'); out.stream_url = v; }
  if ('retention_days' in b) { const n = Number(b.retention_days); if (!Number.isInteger(n) || n < 1 || n > 365) return err('名簿の保存期間は 1〜365 日で入力してください。'); out.retention_days = n; }
  if ('registration_open' in b) out.registration_open = b.registration_open ? 1 : 0;
  if ('reception_open' in b) out.reception_open = b.reception_open ? 1 : 0;
  if ('online_manual' in b) {
    if (b.online_manual === null || b.online_manual === '') out.online_manual = null;
    else { const n = Number(b.online_manual); if (!Number.isInteger(n) || n < 0 || n > 1_000_000) return err('視聴者数は 0 以上の数字で入力してください。'); out.online_manual = n; }
  }
  if ('line_channel_id' in b || 'line_channel_secret' in b) {
    const id = clean(b.line_channel_id, 20), secret = clean(b.line_channel_secret, 64);
    if (!id && !secret) { out.line_channel_id = null; out.line_secret_enc = null; }
    else {
      if (!/^\d{6,20}$/.test(id)) return err('LINEログインのチャネルIDは数字で入力してください。');
      out.line_channel_id = id;
      if (secret) {
        if (!env.SESSION_SECRET) return err('SESSION_SECRET が未設定のため、LINE連携を保存できません。');
        out.line_secret_enc = await seal(env.SESSION_SECRET, secret);
      } else if (create) return err('LINEログインのチャネルシークレットを入力してください。');
    }
  }
  return { values: out };
}

// ------------------------------------------------------------------ 管理（カルラライブの担当者）
async function admin(req: Request, env: Env, seg: string[], origin: string): Promise<Response> {
  if (!env.ADMIN_KEY) return fail(503, 'not_configured', 'ADMIN_KEY が設定されていません。');
  if (!(await safeEqual(bearer(req), env.ADMIN_KEY))) return fail(401, 'unauthorized', '管理用の鍵が違います。');

  if (seg[0] === 'events' && seg.length === 1) {
    if (req.method === 'GET') {
      const rows = await env.DB.prepare(`SELECT e.*,
          (SELECT COUNT(*) FROM attendees a WHERE a.event_id = e.id) AS total,
          (SELECT COUNT(*) FROM attendees a WHERE a.event_id = e.id AND a.checked_in_at IS NOT NULL) AS checked
        FROM events e ORDER BY e.held_on DESC, e.created_at DESC LIMIT 200`).all<EventRow & { total: number; checked: number }>();
      return json({
        ok: true, mail: mailOn(env), line_callback: `${origin}/api/line/callback`,
        events: rows.results.map((ev) => ({
          ...eventStaff(ev, origin), total: ev.total, checked: ev.checked, line_channel_id: ev.line_channel_id,
          staff_url: `${origin}/staff?e=${ev.id}&k=${ev.staff_key}`, report_url: `${origin}/report?e=${ev.id}&k=${ev.staff_key}`,
        })),
      });
    }
    if (req.method === 'POST') {
      const b = await body(req); if (!b) return BAD();
      const r = await readEventInput(env, b, true);
      if ('error' in r) return fail(400, 'invalid', r.error!);
      const v = r.values!;
      const id = randomId(), days = Number(v.retention_days ?? 30);
      await env.DB.prepare(`INSERT INTO events (id, title, held_on, time_note, venue, capacity, stream_url, staff_key, door_key, door_code,
          registration_open, retention_days, purge_on, line_channel_id, line_secret_enc, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`)
        .bind(id, v.title, v.held_on, v.time_note ?? '', v.venue ?? '', v.capacity ?? 300, v.stream_url ?? '', randomKey(), randomKey(), randomCode(),
          v.registration_open ?? 0, days, addDays(String(v.held_on), days), v.line_channel_id ?? null, v.line_secret_enc ?? null, nowIso()).run();
      return json({ ok: true, id }, 201);
    }
  }

  if (seg[0] === 'events' && seg.length === 2) {
    const ev = await getEvent(env, seg[1]); if (!ev) return NO_EVENT();
    if (req.method === 'PATCH') {
      if (ev.purged_at) return CLOSED();
      const b = await body(req); if (!b) return BAD();
      const r = await readEventInput(env, b, false);
      if ('error' in r) return fail(400, 'invalid', r.error!);
      const v = r.values!;
      if ('held_on' in v || 'retention_days' in v) v.purge_on = addDays(String(v.held_on ?? ev.held_on), Number(v.retention_days ?? ev.retention_days));
      if (v.line_channel_id && !('line_secret_enc' in v) && !ev.line_secret_enc) return fail(400, 'invalid', 'LINEログインのチャネルシークレットを入力してください。');
      const keys = Object.keys(v);
      if (keys.length) await env.DB.prepare(`UPDATE events SET ${keys.map((k) => `${k} = ?`).join(', ')} WHERE id = ?`).bind(...keys.map((k) => v[k]), ev.id).run();
      return json({ ok: true });
    }
    if (req.method === 'DELETE') { // 名簿ごと、会そのものを消す
      await env.DB.batch([env.DB.prepare('DELETE FROM attendees WHERE event_id = ?').bind(ev.id), env.DB.prepare('DELETE FROM events WHERE id = ?').bind(ev.id)]);
      return json({ ok: true });
    }
  }

  if (seg[0] === 'events' && seg[2] === 'purge' && req.method === 'POST') { // 保存期間を待たずに名簿を消す（集計は残す）
    const ev = await getEvent(env, seg[1]); if (!ev) return NO_EVENT();
    if (!ev.purged_at) await purgeEvent(env, ev);
    return json({ ok: true });
  }
  if (seg[0] === 'purge' && req.method === 'POST') return json({ ok: true, purged: await purgeDue(env) });
  return NOT_FOUND();
}

// ------------------------------------------------------------------ 受付スタッフ・主催者
async function staff(req: Request, env: Env, seg: string[], origin: string, ctx: ExecutionContext): Promise<Response> {
  const ev = await getEvent(env, seg[0] || '');
  // 会があるかどうかを鍵なしで確かめられないよう、どちらの失敗も同じ答えにする
  if (!ev || !(await safeEqual(bearer(req), ev.staff_key))) return fail(401, 'unauthorized', 'このURLでは開けません。受付用のURLをご確認ください。');
  const sub = seg[1] || '';

  if (!sub && req.method === 'GET') return json({ ok: true, event: eventStaff(ev, origin), summary: await summarize(env, ev), mail: mailOn(env) });
  if (sub === 'report' && req.method === 'GET') return json({ ok: true, event: eventStaff(ev, origin), summary: await summarize(env, ev) });
  if (ev.purged_at) return CLOSED();

  if (!sub && req.method === 'PATCH') {
    const b = await body(req); if (!b) return BAD();
    const allowed: Record<string, unknown> = {};
    for (const k of ['reception_open', 'registration_open', 'online_manual']) if (k in b) allowed[k] = b[k];
    const r = await readEventInput(env, allowed, false);
    if ('error' in r) return fail(400, 'invalid', r.error!);
    const v = r.values!;
    if (b.new_door_code) v.door_code = randomCode();
    const keys = Object.keys(v);
    if (keys.length) await env.DB.prepare(`UPDATE events SET ${keys.map((k) => `${k} = ?`).join(', ')} WHERE id = ?`).bind(...keys.map((k) => v[k]), ev.id).run();
    return json({ ok: true, event: eventStaff((await getEvent(env, ev.id))!, origin) });
  }

  if (sub === 'attendees' && seg.length === 2) {
    if (req.method === 'GET') {
      const rows = await env.DB.prepare(`SELECT id, name, email, org, kind, source, checked_in_at, checkin_method, watched_at, mailed_at,
          line_user_id IS NOT NULL AS line, code_fails >= ${CODE_FAIL_LIMIT} AS locked
        FROM attendees WHERE event_id = ? ORDER BY name COLLATE NOCASE, id`).bind(ev.id).all();
      return json({ ok: true, attendees: rows.results });
    }
    if (req.method === 'POST') { // 当日受付など、1人ずつ足す
      const b = await body(req); if (!b) return BAD();
      const name = clean(b.name, 80), email = clean(b.email, 254).toLowerCase();
      if (!name) return fail(400, 'invalid', 'お名前を入力してください。');
      if (email && !isEmail(email)) return fail(400, 'invalid', 'メールアドレスの形で入力してください。');
      const a = await addAttendee(env, ev.id, { name, email, org: clean(b.org, 120), kind: kindOf(b.kind), source: 'staff' });
      const result = b.checkin ? await checkIn(env, a, 'staff') : null;
      return json({ ok: true, id: a.id, ticket_url: `${origin}/t?k=${a.token}`, checkin: result }, 201);
    }
  }

  if (sub === 'attendees' && seg.length === 3 && req.method === 'DELETE') { // 本人からの削除の求めに応じる
    const r = await env.DB.prepare('DELETE FROM attendees WHERE id = ? AND event_id = ?').bind(Number(seg[2]), ev.id).run();
    return r.meta.changes ? json({ ok: true }) : NOT_FOUND();
  }

  if (sub === 'checkin' && req.method === 'POST') {
    const b = await body(req); if (!b) return BAD();
    const a = typeof b.token === 'string'
      ? await env.DB.prepare('SELECT * FROM attendees WHERE token = ?').bind(b.token).first<AttendeeRow>()
      : await env.DB.prepare('SELECT * FROM attendees WHERE id = ?').bind(Number(b.id)).first<AttendeeRow>();
    if (!a) return fail(404, 'no_ticket', 'このチケットは名簿にありません。');
    if (a.event_id !== ev.id) return fail(404, 'other_event', '別の会のチケットです。');
    return json(await checkIn(env, a, typeof b.token === 'string' ? 'qr' : 'staff'));
  }

  if (sub === 'undo' && req.method === 'POST') { // まちがえて入場済みにしたときの取り消し
    const b = await body(req); if (!b) return BAD();
    const r = await env.DB.prepare('UPDATE attendees SET checked_in_at = NULL, checkin_method = NULL, code_fails = 0 WHERE id = ? AND event_id = ?').bind(Number(b.id), ev.id).run();
    return r.meta.changes ? json({ ok: true }) : NOT_FOUND();
  }

  if (sub === 'import' && req.method === 'POST') {
    const b = await body<{ csv?: unknown }>(req);
    if (!b || typeof b.csv !== 'string') return fail(400, 'invalid', 'CSVを読み取れませんでした。ファイルが大きすぎる場合は、分けて取り込んでください。');
    const rows = parseCsv(b.csv);
    if (!rows.length) return fail(400, 'invalid', 'CSVに行がありません。');
    if (rows.length > MAX_IMPORT_ROWS + 1) return fail(400, 'invalid', `一度に取り込めるのは ${MAX_IMPORT_ROWS} 行までです。`);
    // 見出しの行があれば、列の並びはそれに合わせる。なければ「名前, メール, 所属, 区分」の順
    const col = { name: 0, email: 1, org: 2, kind: 3 };
    const head = rows[0].map((h) => h.trim().toLowerCase());
    const find = (re: RegExp) => head.findIndex((h) => re.test(h));
    const hasHead = find(/^(名前|氏名|お名前|name)$/) >= 0;
    if (hasHead) {
      col.name = find(/^(名前|氏名|お名前|name)$/); col.email = find(/メール|mail/); col.org = find(/所属|会社|組織|org/); col.kind = find(/区分|参加方法|種別|kind/);
      rows.shift();
    }
    const known = new Set((await env.DB.prepare("SELECT email FROM attendees WHERE event_id = ? AND email != ''").bind(ev.id).all<{ email: string }>()).results.map((r) => r.email));
    const stmts: D1PreparedStatement[] = [];
    const skipped: { line: number; reason: string }[] = [];
    rows.forEach((r, i) => {
      const line = i + (hasHead ? 2 : 1), at = (c: number) => (c >= 0 ? r[c] : '');
      const name = clean(at(col.name), 80), email = clean(at(col.email), 254).toLowerCase();
      if (!name) return void skipped.push({ line, reason: '名前がありません' });
      if (email && !isEmail(email)) return void skipped.push({ line, reason: 'メールアドレスの形ではありません' });
      if (email && known.has(email)) return void skipped.push({ line, reason: '同じメールアドレスが名簿にあります' });
      if (email) known.add(email);
      stmts.push(insertAttendee(env, ev.id, { name, email, org: clean(at(col.org), 120), kind: kindOf(clean(at(col.kind), 20)), source: 'csv' }));
    });
    for (let i = 0; i < stmts.length; i += 50) await env.DB.batch(stmts.slice(i, i + 50));
    return json({ ok: true, added: stmts.length, skipped });
  }

  if (sub === 'export.csv' && req.method === 'GET') {
    const rows = await env.DB.prepare('SELECT * FROM attendees WHERE event_id = ? ORDER BY name COLLATE NOCASE, id').bind(ev.id).all<AttendeeRow>();
    const jst = (iso: string | null) => (iso ? new Date(Date.parse(iso) + 9 * 3600 * 1000).toISOString().slice(0, 16).replace('T', ' ') : '');
    const methods: Record<string, string> = { qr: 'QRコード', touch: 'タッチ', door: '受付のタグ', staff: '受付で確認' };
    const lines = [['名前', 'メール', '所属', '区分', 'チケットのURL', '入場時刻', '入場の方法', '配信を開いた時刻'].join(',')];
    for (const a of rows.results) {
      lines.push([a.name, a.email, a.org, a.kind === 'online' ? 'オンライン' : '会場', `${origin}/t?k=${a.token}`,
        jst(a.checked_in_at), methods[a.checkin_method || ''] || '', jst(a.watched_at)].map(csvCell).join(','));
    }
    return new Response('﻿' + lines.join('\r\n') + '\r\n', {
      headers: { 'content-type': 'text/csv; charset=utf-8', 'content-disposition': `attachment; filename="meibo-${ev.id}.csv"`, 'cache-control': 'no-store' },
    });
  }

  if (sub === 'mail' && req.method === 'POST') { // まだ送っていない人に、チケットをメールで送る（少しずつ）
    if (!mailOn(env)) return fail(503, 'mail_off', 'メールの送信は設定されていません。名簿をCSVで書き出して、チケットのURLをお送りください。');
    const rows = await env.DB.prepare("SELECT * FROM attendees WHERE event_id = ? AND email != '' AND mailed_at IS NULL ORDER BY id LIMIT ?").bind(ev.id, MAIL_BATCH).all<AttendeeRow>();
    let sent = 0, failed = 0;
    for (const a of rows.results) (await sendTicketMail(env, origin, ev, a)) ? sent++ : failed++;
    const left = Number((await env.DB.prepare("SELECT COUNT(*) AS n FROM attendees WHERE event_id = ? AND email != '' AND mailed_at IS NULL").bind(ev.id).first<{ n: number }>())?.n ?? 0);
    return json({ ok: true, sent, failed, remaining: left });
  }
  void ctx;
  return NOT_FOUND();
}

// ------------------------------------------------------------------ 参加者：申込
async function publicEvent(req: Request, env: Env, seg: string[], origin: string, ctx: ExecutionContext): Promise<Response> {
  const ev = await getEvent(env, seg[0] || ''); if (!ev) return NO_EVENT();
  const sub = seg[1] || '';
  if (!sub && req.method === 'GET') {
    const full = ev.registration_open ? (await venueCount(env, ev.id)) >= ev.capacity : false;
    return json({ ok: true, event: { ...eventPublic(ev), venue_full: full } });
  }

  if (sub === 'join' && req.method === 'POST') {
    if (ev.purged_at) return CLOSED();
    if (!ev.registration_open) return fail(403, 'not_open', 'この会の申込は、いま受け付けていません。');
    const b = await body(req); if (!b) return BAD();
    if (clean(b.website, 200)) return json({ ok: true, ticket_url: `${origin}/` }); // 人には見えない欄。埋めてくるのは自動送信
    const name = clean(b.name, 80), email = clean(b.email, 254).toLowerCase(), kind = kindOf(b.kind);
    if (!name) return fail(400, 'invalid', 'お名前を入力してください。');
    if (!isEmail(email)) return fail(400, 'invalid', 'メールアドレスの形で入力してください（例：name@example.ac.jp）。');
    if (kind === 'online' && !ev.stream_url) return fail(400, 'invalid', 'この会は、会場での参加だけを受け付けています。');
    const dup = await env.DB.prepare('SELECT * FROM attendees WHERE event_id = ? AND email = ? LIMIT 1').bind(ev.id, email).first<AttendeeRow>();
    if (dup) { // 他人のチケットを画面に出さないよう、再送はメールだけにする
      if (mailOn(env)) { ctx.waitUntil(sendTicketMail(env, origin, ev, dup)); return fail(409, 'duplicate', 'このメールアドレスは申込済みです。チケットをメールでもう一度お送りしました。'); }
      return fail(409, 'duplicate', 'このメールアドレスは申込済みです。チケットが見つからない場合は、当日の受付でお名前をお伝えください。');
    }
    if (kind === 'venue' && (await venueCount(env, ev.id)) >= ev.capacity) {
      return fail(409, 'full', ev.stream_url ? '会場での参加は定員に達しました。オンラインでの参加をお選びいただけます。' : '定員に達したため、申込を締め切りました。');
    }
    const a = await addAttendee(env, ev.id, { name, email, org: clean(b.org, 120), kind, source: 'form' });
    if (mailOn(env)) ctx.waitUntil(sendTicketMail(env, origin, ev, a));
    return json({ ok: true, ticket_url: `${origin}/t?k=${a.token}`, mailed: mailOn(env) }, 201);
  }

  // LINEで申し込む：名前などは署名つきの Cookie に持たせて、LINE の同意画面へ送る
  if (sub === 'line' && seg[2] === 'start' && req.method === 'POST') {
    const back = (code: string) => Response.redirect(`${origin}/join?e=${ev.id}&err=${code}`, 303);
    if (ev.purged_at || !ev.registration_open || !lineOn(ev) || !env.SESSION_SECRET) return back('closed');
    const f = await req.formData();
    const name = clean(f.get('name'), 80), kind = kindOf(f.get('kind'));
    if (!name) return back('name');
    if (kind === 'online' && !ev.stream_url) return back('closed');
    const nonce = randomKey();
    const jar = await sign(env.SESSION_SECRET, { n: nonce, e: ev.id, kind, name, org: clean(f.get('org'), 120), exp: Date.now() + 15 * 60 * 1000 });
    const secure = origin.startsWith('https:') ? ' Secure;' : '';
    return new Response(null, {
      status: 303,
      headers: {
        location: lineAuthorizeUrl(env, ev.line_channel_id!, `${origin}/api/line/callback`, nonce),
        'set-cookie': `kt_line=${jar}; Path=/api/line; Max-Age=900; HttpOnly;${secure} SameSite=Lax`,
        'cache-control': 'no-store',
      },
    });
  }
  return NOT_FOUND();
}

interface LineJar { n: string; e: string; kind: 'venue' | 'online'; name: string; org: string; exp: number }

async function lineCallback(req: Request, env: Env, url: URL, origin: string): Promise<Response> {
  const clear = 'kt_line=; Path=/api/line; Max-Age=0; HttpOnly; SameSite=Lax';
  const go = (to: string) => new Response(null, { status: 303, headers: { location: to, 'set-cookie': clear, 'cache-control': 'no-store' } });
  const jar = env.SESSION_SECRET ? await unsign<LineJar>(env.SESSION_SECRET, cookie(req, 'kt_line')) : null;
  if (!jar || jar.exp < Date.now()) return go(`${origin}/`);
  const back = (code: string) => go(`${origin}/join?e=${jar.e}&err=${code}`);
  const state = url.searchParams.get('state') || '', code = url.searchParams.get('code') || '';
  if (!(await safeEqual(state, jar.n))) return back('line');
  if (url.searchParams.get('error') || !code) return back('cancel'); // 同意画面で「キャンセル」を選んだとき
  const ev = await getEvent(env, jar.e);
  if (!ev || ev.purged_at || !ev.registration_open || !lineOn(ev)) return back('closed');
  const secret = await unseal(env.SESSION_SECRET!, ev.line_secret_enc!);
  if (!secret) return back('line');
  const who = await lineExchange(env, ev.line_channel_id!, secret, code, `${origin}/api/line/callback`);
  if (!who) return back('line');

  const had = await env.DB.prepare('SELECT * FROM attendees WHERE event_id = ? AND line_user_id = ?').bind(ev.id, who.userId).first<AttendeeRow>();
  if (had) { // 申込済みの人がもう一度ログインしたら、同じチケットを開く。友だちの状態だけ更新する
    if (who.friend && !had.line_friend) {
      await env.DB.prepare('UPDATE attendees SET line_friend = 1, line_friend_new = ? WHERE id = ?').bind(url.searchParams.get('friendship_status_changed') === 'true' ? 1 : had.line_friend_new, had.id).run();
    }
    return go(`${origin}/t?k=${had.token}`);
  }
  if (jar.kind === 'venue' && (await venueCount(env, ev.id)) >= ev.capacity) return back('full');
  const a = await addAttendee(env, ev.id, {
    name: jar.name, org: jar.org, kind: jar.kind, source: 'line', line_user_id: who.userId,
    line_friend: who.friend, line_friend_new: who.friend && url.searchParams.get('friendship_status_changed') === 'true',
  });
  return go(`${origin}/t?k=${a.token}&new=1`);
}

// ------------------------------------------------------------------ 参加者：チケット
async function ticket(req: Request, env: Env, seg: string[]): Promise<Response> {
  const a = await env.DB.prepare('SELECT * FROM attendees WHERE token = ?').bind(seg[0] || '').first<AttendeeRow>();
  if (!a) return fail(404, 'no_ticket', 'チケットが見つかりませんでした。会の終了後は、チケットは表示されません。');
  const ev = (await getEvent(env, a.event_id))!;
  const sub = seg[1] || '';
  const view = () => ({
    ok: true, event: eventPublic(ev),
    ticket: { name: a.name, org: a.org, kind: a.kind, checked_in_at: a.checked_in_at, locked: a.code_fails >= CODE_FAIL_LIMIT },
  });
  if (!sub && req.method === 'GET') return json(view());

  if (sub === 'touch' && req.method === 'POST') { // 受付で伝えられた4桁のコードで入場する
    if (a.checked_in_at) return json(await checkIn(env, a, 'touch'));
    if (!ev.reception_open) return fail(403, 'not_open', 'まだ受付が始まっていません。受付の開始後に、もう一度お試しください。');
    if (a.code_fails >= CODE_FAIL_LIMIT) return fail(423, 'locked', 'コードの入力が続けて合いませんでした。受付でお名前をお伝えください。');
    const b = await body(req); if (!b) return BAD();
    if (!(await safeEqual(clean(b.code, 8), ev.door_code))) {
      await env.DB.prepare('UPDATE attendees SET code_fails = code_fails + 1 WHERE id = ?').bind(a.id).run();
      const left = CODE_FAIL_LIMIT - a.code_fails - 1;
      return fail(400, 'wrong_code', left > 0 ? `コードが違います。受付の表示をご確認ください（あと${left}回）。` : 'コードが違います。受付でお名前をお伝えください。');
    }
    return json(await checkIn(env, a, 'touch'));
  }

  if (sub === 'watch' && req.method === 'POST') { // 配信を開く。開いたことを名簿に残す
    if (!ev.stream_url) return fail(404, 'no_stream', 'この会の配信は、まだ用意されていません。');
    if (!a.watched_at) await env.DB.prepare('UPDATE attendees SET watched_at = ? WHERE id = ?').bind(nowIso(), a.id).run();
    return json({ ok: true, url: ev.stream_url });
  }
  return NOT_FOUND();
}

// ------------------------------------------------------------------ 受付に置いたタグ（NFC・掲示QR）
async function door(req: Request, env: Env, seg: string[]): Promise<Response> {
  if (req.method !== 'POST') return NOT_FOUND();
  const ev = await getEvent(env, seg[0] || ''); const b = await body(req);
  if (!b) return BAD();
  if (!ev || !(await safeEqual(clean(b.key, 64), ev.door_key))) return fail(404, 'no_event', 'このタグは使えません。受付でお名前をお伝えください。');
  if (ev.purged_at) return CLOSED();
  if (!ev.reception_open) return fail(403, 'not_open', 'まだ受付が始まっていません。受付の開始後に、もう一度かざしてください。');
  let a: AttendeeRow | null = null;
  if (typeof b.token === 'string' && b.token) {
    a = await env.DB.prepare('SELECT * FROM attendees WHERE token = ? AND event_id = ?').bind(b.token, ev.id).first<AttendeeRow>();
  } else {
    const email = clean(b.email, 254).toLowerCase();
    if (!isEmail(email)) return fail(400, 'need_ticket', '申込のときのメールアドレスを入力してください。');
    a = await env.DB.prepare('SELECT * FROM attendees WHERE event_id = ? AND email = ? ORDER BY checked_in_at IS NOT NULL, id LIMIT 1').bind(ev.id, email).first<AttendeeRow>();
  }
  if (!a) return fail(404, 'no_ticket', '名簿に見つかりませんでした。受付でお名前をお伝えください。');
  return json({ ...(await checkIn(env, a, 'door')), event: eventPublic(ev) });
}

// ------------------------------------------------------------------ 入口
export default {
  async fetch(req: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(req.url);
    if (!url.pathname.startsWith('/api/')) return env.ASSETS.fetch(req);
    const seg = url.pathname.split('/').filter(Boolean).slice(1).map(decodeURIComponent);
    const origin = url.origin;
    try {
      switch (seg[0]) {
        case 'admin': return await admin(req, env, seg.slice(1), origin);
        case 'staff': return await staff(req, env, seg.slice(1), origin, ctx);
        case 'e': return await publicEvent(req, env, seg.slice(1), origin, ctx);
        case 't': return await ticket(req, env, seg.slice(1));
        case 'door': return await door(req, env, seg.slice(1));
        case 'line': if (seg[1] === 'callback' && req.method === 'GET') return await lineCallback(req, env, url, origin); break;
        case 'config': if (req.method === 'GET') return json({ ok: true, lp_url: env.LP_URL || '' }); break;
      }
      return NOT_FOUND();
    } catch (e) {
      console.error('api error', url.pathname, e instanceof Error ? e.message : e);
      return fail(500, 'server_error', 'うまく処理できませんでした。少し待って、もう一度お試しください。');
    }
  },

  async scheduled(_c: ScheduledController, env: Env, ctx: ExecutionContext) {
    ctx.waitUntil(purgeDue(env).then((n) => console.log(`purged ${n} event(s)`)));
  },
} satisfies ExportedHandler<Env>;
