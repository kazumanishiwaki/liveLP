// LINEログイン（v2.1）と、友だち追加オプション
//
// 参考：https://developers.line.biz/ja/docs/line-login/link-a-bot/
// - 認可URLに bot_prompt を付けると、同意のあとに「友だち追加」の画面が出る
// - 友だちに追加する LINE公式アカウントは、LINE Developers コンソールで LINEログインのチャネルにリンクしておく
//   （公式アカウントの Messaging API チャネルと、LINEログインのチャネルが同じプロバイダーにあること）

import type { Env } from './util';

// テストのときだけ、LINE の代わりに立てたサーバーへ向ける
type LineEnv = Env & { LINE_AUTH_BASE?: string; LINE_API_BASE?: string };
const authBase = (env: LineEnv) => env.LINE_AUTH_BASE || 'https://access.line.me';
const apiBase = (env: LineEnv) => env.LINE_API_BASE || 'https://api.line.me';

export function lineAuthorizeUrl(env: Env, channelId: string, redirectUri: string, state: string): string {
  const q = new URLSearchParams({
    response_type: 'code', client_id: channelId, redirect_uri: redirectUri, state,
    scope: 'profile',          // 名前とユーザーIDだけ。メールアドレスは受け取らない
    bot_prompt: 'aggressive',  // 同意のあと、友だち追加の画面を出す
  });
  return `${authBase(env)}/oauth2/v2.1/authorize?${q}`;
}

/** 認可コードを、ユーザーIDと「友だちかどうか」に引き換える。うまくいかなければ null */
export async function lineExchange(env: Env, channelId: string, channelSecret: string, code: string, redirectUri: string): Promise<{ userId: string; friend: boolean } | null> {
  try {
    const tok = await fetch(`${apiBase(env)}/oauth2/v2.1/token`, {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ grant_type: 'authorization_code', code, redirect_uri: redirectUri, client_id: channelId, client_secret: channelSecret }),
    });
    if (!tok.ok) return null;
    const { access_token } = await tok.json<{ access_token?: string }>();
    if (!access_token) return null;
    const auth = { authorization: `Bearer ${access_token}` };
    const [p, f] = await Promise.all([fetch(`${apiBase(env)}/v2/profile`, { headers: auth }), fetch(`${apiBase(env)}/friendship/v1/status`, { headers: auth })]);
    if (!p.ok) return null;
    const profile = await p.json<{ userId?: string }>();
    if (!profile.userId) return null;
    // 公式アカウントがリンクされていないチャネルでは、友だちの状態は取れない。申込そのものは通す
    const friend = f.ok ? !!(await f.json<{ friendFlag?: boolean }>()).friendFlag : false;
    return { userId: profile.userId, friend };
  } catch {
    return null;
  }
}
