// カルラライブのサイトを thisandthat.jp/live の下で配る。
// 配るファイルは docs/（src/build.py の書き出し）。このWorkerは、パスの先頭の /live を外して静的ファイルに渡すだけ。
// サイトの中のリンクはすべて相対パスなので、HTML を書き換える必要はない。
const MOUNT = "/live";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === MOUNT) {
      url.pathname = `${MOUNT}/`;
      return Response.redirect(url.toString(), 301);
    }
    if (!url.pathname.startsWith(`${MOUNT}/`)) return new Response("Not Found", { status: 404 });
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method Not Allowed", { status: 405, headers: { Allow: "GET, HEAD" } });
    }

    const inner = new URL(url);
    inner.pathname = url.pathname.slice(MOUNT.length);
    const response = await env.ASSETS.fetch(new Request(inner, request));

    // 静的ファイル側は /contact.html → /contact のように転送する。転送先に /live を付け直す
    const location = response.headers.get("Location");
    if (!location) return response;
    const target = new URL(location, inner);
    if (target.origin !== url.origin || target.pathname.startsWith(`${MOUNT}/`)) return response;
    target.pathname = `${MOUNT}${target.pathname}`;
    const headers = new Headers(response.headers);
    headers.set("Location", `${target.pathname}${target.search}${target.hash}`);
    return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
  },
};
