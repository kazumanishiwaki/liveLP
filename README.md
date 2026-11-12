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
