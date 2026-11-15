# 申し送り（2026-11-15）

## いまの状況

- `main` は `7e6e1ef`。サイトは `docs/` に書き出し済み。
- **thisandthat.jp/live への配信は、まだ一度も通っていない。** リポジトリの Secrets に `CLOUDFLARE_API_TOKEN` が無いため。持ち主が登録したら、Actions の「Deploy site」を再実行（Run workflow）すれば出る。
- GitHub Pages が有効で、`https://kazumanishiwaki.github.io/liveLP/docs/` にも同じサイトが出ている。公開先を1つにするなら、持ち主が Settings → Pages で止める。
- 検索には出さない設定（`noindex`、`src/build.py`）。

## この数日でやったこと

- C案を採用し、デザインのきまり（`AGENTS.md`）に合わせて作り込んだ。A案・B案はブランチ `archive/abc-comparison`。
- リポジトリを整理：`src/` から `docs/` へ書き出す形。書体の切り出しを `build.py` に組み込んだ。
- `thisandthat.jp/live` で配る Worker と、配信・本番確認のワークフロー。
- 別の作業で `ticket/`（受付用デジタルチケット）と、サイトの「受付とチケット」の節が入っている。

## 次にやること（優先順）

1. **配信を通す**（上の Secrets）。通ったら `https://thisandthat.jp/live/` をスマホ幅と PC 幅で見る。
2. **穴埋め（［ ］、黄色）を埋める。** 一覧は `notes/穴埋めリスト.md`。素材（実績・写真・数字）は持ち主が用意する。
3. **見積フォームの送信先。** `src/build.py` の `data-endpoint`（見積の依頼と、仕様のフォームの2か所）が空で、いまは送ると完了ページへ進むだけ（届かない）。送信先を決めて実装する。決まるまで公開の告知はしない。
4. 2と3が済んだら `noindex` を外す。
5. **`ticket/` は未公開**（`wrangler.jsonc` の `database_id` が仮の値）。公開の手順は `ticket/README.md`。サイトへのリンク（`LP_URL`）は `https://thisandthat.jp/live/#ticket` に合わせてある。

## 決めてあること

- サービス名「カルラライブ」。基本プランは カメラ3台・スタッフ2名・マイク5本まで・25万円（税別）。対応エリアは新宿から90分圏内。金額・体制・機材の内訳は出してよい。
- スマホファースト。プラン診断を主役にする。問い合わせが増えることを最優先。
- AI の学習用クローラーは許可する。
- チケットは配信プランのおまけ（無料）。販売・決済はしない。
- ツール（タイムキーパー・FAQ）は GitHub ではなくデモで見せる。
