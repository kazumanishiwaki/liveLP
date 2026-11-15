// 配信のあと、本番が開けるかを読むだけで確かめる： node scripts/smoke.mjs
// 確かめる先は SMOKE_BASE_URL（既定は本番）。反映の遅れに備えて、最大90秒・10秒おきにやり直す。
const BASE = (process.env.SMOKE_BASE_URL || "https://thisandthat.jp/live/").replace(/\/?$/, "/");
const TIMEOUT_MS = Number(process.env.SMOKE_TIMEOUT_MS || 90_000);
const RETRY_MS = Number(process.env.SMOKE_RETRY_MS || 10_000);

const checks = [
  { name: "トップ", path: "", type: "text/html", text: "カルラライブ" },
  { name: "見積の依頼", path: "contact.html", type: "text/html", text: "見積" },
  { name: "CSS", path: "assets/site.css", type: "text/css" },
  { name: "共通トークン", path: "assets/karura-tokens.css", type: "text/css" },
  { name: "JS", path: "assets/site.js", type: "javascript" },
  { name: "書体", path: "assets/fonts/zkgn-500.woff2", type: "font/woff2" },
];

async function run(check) {
  const url = new URL(check.path, BASE);
  const res = await fetch(url, { redirect: "follow" });
  if (res.status !== 200) throw new Error(`${check.name} ${url} → ${res.status}`);
  const type = res.headers.get("content-type") || "";
  if (!type.includes(check.type)) throw new Error(`${check.name} ${url} → 種類が ${type}`);
  if (!res.url.startsWith(BASE)) throw new Error(`${check.name} ${url} → ${res.url} へ転送された`);
  if (check.text && !(await res.text()).includes(check.text)) throw new Error(`${check.name} ${url} → 「${check.text}」が無い`);
  return `${check.name} ${url}`;
}

console.log(`確かめる先: ${BASE}`);
const startedAt = Date.now();
for (let attempt = 1; ; attempt += 1) {
  const results = await Promise.allSettled(checks.map(run));
  const failed = results.filter((r) => r.status === "rejected").map((r) => r.reason.message);
  if (failed.length === 0) {
    for (const r of results) console.log(`ok  ${r.value}`);
    console.log(`本番の確認が通りました（${attempt}回目）。`);
    process.exit(0);
  }
  if (Date.now() - startedAt + RETRY_MS > TIMEOUT_MS) {
    for (const message of failed) console.error(`NG  ${message}`);
    console.error(`本番の確認が ${attempt}回やっても通りませんでした。自動では巻き戻しません。`);
    process.exit(1);
  }
  console.log(`…  ${attempt}回目：${failed[0]} ほか${failed.length - 1}件。${RETRY_MS / 1000}秒後にやり直します。`);
  await new Promise((resolve) => setTimeout(resolve, RETRY_MS));
}
