# liveLP

シンポジウム・講演会のハイブリッド配信代行「カルラライブ」のサービスサイト。
大学・公共機関の担当者向け。基本プランは カメラ3台・スタッフ2名・マイク5本まで・25万円（税別）、対応エリアは新宿から90分圏内。

## 置き場所

| 場所 | 内容 | 編集 |
| --- | --- | --- |
| `design/karura-tokens.css` | 色・影・角丸・文字・動きの値。サイトと2つのツールで共通の、ただ1つの元 | する |
| `src/build.py` | サイトを書き出すスクリプト。文言はすべてこの中 | する |
| `src/site.css` `src/site.js` | 見た目と動き | する |
| `src/img/` `src/fonts/` | 写真と、書体の元ファイル | する |
| `tests/site_test.py` | 診断・メニュー・フォームの動作確認 | する |
| `notes/` | 公開までに埋める項目のメモ | する |
| `docs/` | 公開するサイト一式（生成物） | しない |
| `ticket/` | 受付用のデジタルチケット（申込・QRコードやタッチでの入場・開催報告）。Cloudflare Workers + D1 で動く別のサービス。使い方は `ticket/README.md` | する |

## 直して確かめる

```
python3 src/build.py        # docs/ を作り直す（書体の切り出しも含む）
python3 tests/site_test.py  # スマホ幅で通しの確認。画面の写しは tests/shots/
```

必要なもの：Python 3、Pillow、fonttools（brotli つき）、テストには Playwright と Chrome。
`docs/` は毎回まるごと作り直すので、直接は編集しません。直したら `docs/` も一緒にコミットします。

## 公開

GitHub の Settings → Pages で、Source を「Deploy from a branch」、Branch を `main` の `/docs` にすると、
https://kazumanishiwaki.github.io/liveLP/ で見られます。

公開前に残っていること：

- 文中の［ ］（黄色の穴埋め）を埋める。一覧は `notes/穴埋めリスト.md`
- 見積フォームの送信先（`src/build.py` の `data-endpoint`）を決める。いまは空で、送信すると完了ページへ進むだけ
- 検索に出すなら `src/build.py` の `noindex` を外す

## デザイントークンをツールへ反映する

タイムキーパー（kazumanishiwaki/timekeeper）と FAQ（kazumanishiwaki/slide）は、
`npm run sync:design` でこのリポジトリの `design/karura-tokens.css` を取り込みます（デプロイ時にも自動で実行）。
デジタルチケット（`ticket/`）も、同じく `npm run sync:design` で `ticket/public/css/` に取り込みます（`npm run dev` と `npm run deploy` の前に自動で実行）。
値を変えるときは `design/karura-tokens.css` だけを直し、サイトを作り直して、3つのツールをデプロイし直します。

## 以前の比較案

採用前に見比べた A案・B案と入口のページは、ブランチ `archive/abc-comparison` に残しています。
