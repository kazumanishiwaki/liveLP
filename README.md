# liveLP

シンポジウム・講演会のハイブリッド配信代行「カルラライブ」のサービスサイト。

| 場所 | 内容 |
| --- | --- |
| index.html | A案とB案を選ぶ入口 |
| a/ | A：新しいテイスト（確認用。1ファイルで全ページを切り替え） |
| b/ | B：前のテイスト（同上） |
| c/ | C：採用案。トップ、問い合わせ、完了、デザインルール（rules.html）の4ページ。書き出しは source/c/build_c.py、CSS と JS は c/assets/ を直接編集 |
| source/ | 書き出しのスクリプト一式。使い方は source/README.md |

## ブラウザで見る

Settings → Pages で、Source を「Deploy from a branch」、Branch を `main` と `/ (root)` にすると、
https://kazumanishiwaki.github.io/liveLP/ で見られます。

## デザイントークン（ただ1つの元）

色・影・角丸・文字・動きの値は `design/karura-tokens.css` にまとめています。

- サイト（C案）：`python3 source/c/build_c.py` が `c/assets/karura-tokens.css` にコピーし、`site.css` が読み込みます。`c/assets/` 側は直接編集しません。
- タイムキーパー（kazumanishiwaki/timekeeper）と FAQ（kazumanishiwaki/slide）：`npm run sync:design` でこのファイルを取り込みます（デプロイ時にも自動で実行）。
- 値を変えるときは `design/karura-tokens.css` だけを直し、サイトを作り直して、タイムキーパーと FAQ をデプロイし直します。
