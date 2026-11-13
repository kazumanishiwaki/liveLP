// 小さな道具：乱数、時刻、署名、暗号化、CSV

export interface Env {
  DB: D1Database;
  ASSETS: Fetcher;
  ADMIN_KEY?: string;
  SESSION_SECRET?: string;
  RESEND_API_KEY?: string;
  MAIL_FROM?: string;
  LP_URL?: string;
}

const enc = new TextEncoder();
const dec = new TextDecoder();

export function b64url(bytes: Uint8Array): string {
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
export function unb64url(s: string): Uint8Array {
  const bin = atob(s.replace(/-/g, '+').replace(/_/g, '/'));
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

/** URL に入れる鍵（128bit） */
export function randomKey(bytes = 16): string {
  return b64url(crypto.getRandomValues(new Uint8Array(bytes)));
}

const ID_CHARS = 'abcdefghijkmnpqrstuvwxyz23456789'; // 32文字。まぎらわしい l・o・0・1 は使わない
export function randomId(len = 10): string {
  const r = crypto.getRandomValues(new Uint8Array(len));
  let s = '';
  for (const b of r) s += ID_CHARS[b & 31];
  return s;
}

/** 受付で伝える4桁のコード */
export function randomCode(): string {
  const r = new Uint32Array(1);
  for (;;) {
    crypto.getRandomValues(r);
    if (r[0] < 4294960000) return String(r[0] % 10000).padStart(4, '0'); // 偏りが出ない範囲だけ使う
  }
}

export const nowIso = () => new Date().toISOString();

/** 日本時間の今日 YYYY-MM-DD */
export function todayJst(d = new Date()): string {
  return new Date(d.getTime() + 9 * 3600 * 1000).toISOString().slice(0, 10);
}
export function addDays(ymd: string, days: number): string {
  const d = new Date(ymd + 'T00:00:00Z');
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}
export const isYmd = (s: unknown): s is string =>
  typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && !Number.isNaN(Date.parse(s + 'T00:00:00Z'));

/** 長さや中身から時間差が漏れない比較 */
export async function safeEqual(a: string, b: string): Promise<boolean> {
  const [x, y] = await Promise.all([crypto.subtle.digest('SHA-256', enc.encode(a)), crypto.subtle.digest('SHA-256', enc.encode(b))]);
  const u = new Uint8Array(x), v = new Uint8Array(y);
  let diff = 0;
  for (let i = 0; i < u.length; i++) diff |= u[i] ^ v[i];
  return diff === 0;
}

async function hmacKey(secret: string) {
  return crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
}
/** 中身に署名をつけた文字列を作る（Cookie 用） */
export async function sign(secret: string, payload: unknown): Promise<string> {
  const body = b64url(enc.encode(JSON.stringify(payload)));
  const sig = b64url(new Uint8Array(await crypto.subtle.sign('HMAC', await hmacKey(secret), enc.encode(body))));
  return `${body}.${sig}`;
}
export async function unsign<T>(secret: string, value: string | undefined): Promise<T | null> {
  if (!value) return null;
  const [body, sig] = value.split('.');
  if (!body || !sig) return null;
  const want = b64url(new Uint8Array(await crypto.subtle.sign('HMAC', await hmacKey(secret), enc.encode(body))));
  if (!(await safeEqual(sig, want))) return null;
  try { return JSON.parse(dec.decode(unb64url(body))) as T; } catch { return null; }
}

async function aesKey(secret: string) {
  const raw = await crypto.subtle.digest('SHA-256', enc.encode('karura-ticket:line:' + secret));
  return crypto.subtle.importKey('raw', raw, 'AES-GCM', false, ['encrypt', 'decrypt']);
}
/** LINE のチャネルシークレットは、暗号化してから D1 に入れる */
export async function seal(secret: string, plain: string): Promise<string> {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, await aesKey(secret), enc.encode(plain)));
  return `${b64url(iv)}.${b64url(ct)}`;
}
export async function unseal(secret: string, sealed: string): Promise<string | null> {
  try {
    const [iv, ct] = sealed.split('.');
    const pt = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: unb64url(iv) }, await aesKey(secret), unb64url(ct));
    return dec.decode(pt);
  } catch { return null; }
}

/** CSV を行と列に分ける（"" の引用、改行入りの欄、BOM に対応） */
export function parseCsv(text: string): string[][] {
  const src = text.replace(/^﻿/, '');
  const rows: string[][] = [];
  let row: string[] = [], cell = '', quoted = false;
  for (let i = 0; i < src.length; i++) {
    const c = src[i];
    if (quoted) {
      if (c === '"') { if (src[i + 1] === '"') { cell += '"'; i++; } else quoted = false; }
      else cell += c;
    } else if (c === '"' && cell === '') quoted = true;
    else if (c === ',' || c === '\t') { row.push(cell); cell = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && src[i + 1] === '\n') i++;
      row.push(cell); cell = '';
      if (row.some((v) => v.trim() !== '')) rows.push(row);
      row = [];
    } else cell += c;
  }
  row.push(cell);
  if (row.some((v) => v.trim() !== '')) rows.push(row);
  return rows;
}

/** CSV の1欄。表計算ソフトで式として動かないよう、= + - @ で始まる値には ' を付ける */
export function csvCell(v: unknown): string {
  let s = v == null ? '' : String(v);
  if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export const clean = (v: unknown, max: number): string =>
  typeof v === 'string' ? v.replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, max) : '';

export const isEmail = (s: string): boolean => /^[^\s@<>"]+@[^\s@<>"]+\.[^\s@<>"]+$/.test(s) && s.length <= 254;

export const isHttpUrl = (s: string): boolean => {
  try { const u = new URL(s); return u.protocol === 'https:' || u.protocol === 'http:'; } catch { return false; }
};

export function json(data: unknown, status = 200, headers: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff', ...headers },
  });
}
/** 利用者に見せるエラー。message はそのまま画面に出す日本語 */
export const fail = (status: number, code: string, message: string) => json({ ok: false, code, message }, status);

export function cookie(req: Request, name: string): string | undefined {
  for (const part of (req.headers.get('cookie') || '').split(';')) {
    const i = part.indexOf('=');
    if (i > 0 && part.slice(0, i).trim() === name) return part.slice(i + 1).trim();
  }
  return undefined;
}
