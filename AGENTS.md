# AGENTS.md — liveLP（カルラライブのサイト）

シンポジウム・講演会のハイブリッド配信代行「カルラライブ」のサービスサイト。大学・公共機関の担当者向け。
公開先は https://thisandthat.jp/live/。いまの状況と次の作業は `notes/handoff.md`。

## 守ること

- **`docs/` は生成物。直接編集しない。** 文言は `src/build.py`、見た目は `src/site.css`・`src/site.js`。直したら `python3 src/build.py` で `docs/` を作り直し、`docs/` も一緒にコミットする。
- **`main` に `docs/` や `cloudflare/` の変更が入ると、本番に自動で出る。** `main` への push は、持ち主（西脇）の OK をもらってから。作業はブランチで行う。
- コメント・コミット・文書は日本語。「何をしているか」より「なぜそうするか」を書く。
- `design/karura-tokens.css`（`--k-*`）は、このサイトと2つのツール（タイムキーパー：kazumanishiwaki/timekeeper、FAQ：kazumanishiwaki/slide）で共通の、ただ1つの元。値を変えたら、ツール側も `npm run sync:design` して配信し直す必要がある。
- サイトの中のリンクは相対パスにする（`/live` の下で配っているため）。

## デザインのきまり

- 色は https://recruit.handy.school に完全に寄せている。主色はティール（`--k-teal`）。
- 色の意味を混ぜない：
  - **ティール** … 主な操作・いまの場所・選択中、その他の操作（`.btn`）
  - **コーラル** … 「見積を依頼する」だけ（`.btn.quote`）。ほかに使うのは FAQ の Q と、当日の流れの「いま」
  - **黄色** … 「プラン診断をはじめる」だけ（`.btn.plan`）。蛍光ペンの黄色（`--k-marker`）は別の薄い色
- 影は重ねない。ボタンに影を付けない。
- 英字のラベルは使わない。トップの見出しのタグは、メニューと同じ言葉にする。
- メニューは7項目まで（`src/build.py` の `MENU`）。ほかに「プラン診断」「見積を依頼する」の2つの行動を、アイコンつきでどのページにも置く。
- PC は左レール（メニュー）＋本文1段。セクションは頭にタグ・見出し・リード、その下に中身（`sec()`）。左に見出しだけの列を作らない。スマホは上に張り付くメニューの横並び。スマホの章の切れ目は、全幅のティールの線とタグ。
- トップは メインビジュアル／費用の内訳／料金プラン／オプション／対応事例／よくある質問 まで。ほかは下層ページ（service・reception・coaching・public）。
- プラン診断はページに埋め込まない。どのページからでも `data-open-diag` のボタンでモーダルを開く（スマホは全画面、PCは中央）。
- 料金は スタンダード 25万円（カメラ3台・2名）／ワイド 35万円（カメラ5台・3名）／オーダー ASK（ロケ配信・進行台本など）。定期的な配信は割引あり。スタンダードを目立たせ、オーダーは控えめに。含まれるものはプランの比較表、追加の費用は「オプション」の1つの表にまとめる。見積のボタンは料金の節に1つ。
- メインビジュアルは本文の幅いっぱいの写真に文を重ねる。文の案は `MV`（比較は mvs.html）。よくある質問は最初から開いておく。
- 言い回しは素直に、質実剛健に。とんちや、人を下げる言い方（「立っているだけ」など）はしない。
- 文字の詰めと行送りは `--k-tracking`・`--k-leading-body`・`--k-leading-head` を使う。値をじかに書かない。
- 全体の規則は `rules.html`（`src/build.py` の `rules()`）に書き出している。

## 確かめ方

```
python3 src/build.py         # docs/ を作り直す（書体の切り出しも含む）。Pillow・fonttools（brotli つき）が要る
python3 tests/site_test.py   # スマホ幅で、診断・メニュー・フォーム・JSなしの表示。Playwright と Chrome が要る
npx wrangler dev --config cloudflare/wrangler.toml   # → http://127.0.0.1:8787/live/
```

- 配信は `.github/workflows/deploy.yml`。Worker（`cloudflare/worker.js`）が `/live` を外して `docs/` を返すだけ。配信のあと `scripts/smoke.mjs` が本番を読んで確かめる。

## `ticket/`

受付用デジタルチケット（別の Worker と D1）。説明は `ticket/README.md`。サイトとは別に配信する。
