#!/usr/bin/env python3
"""カルラライブのサイトを書き出す： python3 src/build.py
   ../docs/ に、公開するサイト一式を作る（GitHub Pages は main の /docs を配信する）。
   - 文言はすべてこのファイルの中
   - CSS と JS は src/site.css・src/site.js、写真は src/img/
   - 色・影・角丸・文字・動きの値は ../design/karura-tokens.css（ツールと共通）
   - 書体は、ページで使っている文字だけを src/fonts/ の元ファイルから切り出す
   docs/ の中は生成物なので、直接編集しない。"""
import shutil
import re
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'docs'
TOKENS = ROOT / 'design' / 'karura-tokens.css'
FONT_SRC = HERE / 'fonts' / 'zen-kaku-gothic-new-japanese-500-normal.woff2'
NAME, NAME_EN = 'カルラライブ', 'KARURA LIVE'
SIZES = {f.stem: Image.open(f).size for f in (HERE / 'img').glob('*.webp')}

ANA = re.compile(r'［[^］]*］')
def mark(h):
    """タグの外にある［ ］を黄色の穴埋め表示にする"""
    return ''.join(p if p.startswith('<') else ANA.sub(lambda m: f'<span class="ana">{m.group(0)}</span>', p)
                   for p in re.split(r'(<[^>]+>)', h))

def img(code, alt, cls='', lazy=True, eager_high=False):
    w, h = SIZES[code]
    a = ' loading="lazy" decoding="async"' if lazy else (' fetchpriority="high"' if eager_high else '')
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="img/{code}.webp" alt="{alt}" width="{w}" height="{h}"{a}>'

def btn(text, href, cls=''):
    return f'<a class="btn {cls}" href="{href}">{text}</a>'

ICON = {
    'check': '<path d="M5 12.5l4.2 4L19 7"/>',
    'mic': '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7"/>',
    'face': '<path d="M4 8V4h4M16 4h4v4M20 16v4h-4M8 20H4v-4"/><circle cx="12" cy="10.5" r="3"/><path d="M7 18c1-3 9-3 10 0"/>',
    'switch': '<rect x="3" y="4" width="12" height="9" rx="1"/><rect x="9" y="11" width="12" height="9" rx="1"/>',
    'backup': '<rect x="3" y="4" width="18" height="6" rx="1.5"/><rect x="3" y="14" width="18" height="6" rx="1.5"/><circle cx="7" cy="7" r=".8"/><circle cx="7" cy="17" r=".8"/>',
    'doc': '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
    'qr': '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h2.5v2.5H14zM17.5 17.5H20V20h-2.5z"/>',
    'touch': '<rect x="7" y="3" width="10" height="18" rx="2"/><path d="M10.5 17.5h3M3.5 9.5a4 4 0 0 0 0 5M20.5 9.5a4 4 0 0 1 0 5"/>',
    'list': '<rect x="5" y="4" width="14" height="17" rx="1.5"/><path d="M9 3h6v3H9zM8.5 11h7M8.5 15h7"/>',
    'report': '<path d="M4 20h16M7 20v-6M12 20V6M17 20v-9"/>',
}
def ico(name, size=''):
    """ティールの角丸チップに入った線画アイコン（飾りなので読み上げない）"""
    return (f'<span class="chipi{" chipi--" + size if size else ""}" aria-hidden="true">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg></span>')

def mk(t):
    """要点に引く黄色のマーカー"""
    return f'<mark class="mk">{t}</mark>'

def lab(t):
    return f'<p class="t-lab">{t}</p>'

def tag_sections(body, items):
    """各セクションの頭のタグを、目次（サブナビ）と同じ言葉にする"""
    for i, t in items:
        at = body.find(f'id="{i}"')
        if at < 0: continue
        nxt = body.find('<section', at + 1)
        m = re.compile(r'<p class="t-lab">.*?</p>').search(body, at, nxt if nxt > 0 else len(body))
        if m: body = body[:m.start()] + f'<p class="t-lab">{t}</p>' + body[m.end():]
    return body

# ------------------------------------------------------------------ 共通
# メニューは7項目まで（2026-11-16 決定）。ほかに「プラン診断」と「見積を依頼する」を、どのページにも置く。
# トップの中の項目は、トップではページ内リンク（現在地つき）、ほかのページからは index.html# へ。
MENU = [('index.html#cost', '費用の内訳'), ('index.html#price', '料金プラン'), ('index.html#works', '対応事例'),
        ('service.html', '当日の体制と流れ'), ('reception.html', '受付と現場の道具'), ('coaching.html', '自分たちで配信する'),
        ('public.html', '大学・公共機関の方へ')]

def menu_href(h, page):
    """トップにいるときは #cost のようなページ内リンクにする（現在地の計算に使う）"""
    return h[len('index.html'):] if page == 'index.html' and h.startswith('index.html#') else h

def menu_items(page, cls_a=''):
    out = ''
    for h, t in MENU:
        cur = ' aria-current="page"' if h == page else ''
        out += f'<li><a href="{menu_href(h, page)}"{cur}>{t}</a></li>'
    return out

BICON = {
    'diag': '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 3h6v3H9zM8.5 13.5l2.5 2.5 4.5-5"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5 12 13l8.5-6.5"/>',
    'arrow': '<path d="M5 12h13M13 6.5 18.5 12 13 17.5"/>',
}
def bico(name):
    """ボタンの頭に付ける線画アイコン（飾りなので読み上げない）"""
    return (f'<svg class="bico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true" focusable="false">{BICON[name]}</svg>')

def go():
    """ページ内や別の節へ移るリンクの印（下線の代わりの、ティールの丸い矢印）"""
    return f'<span class="go">{bico("arrow")}</span>'

def diag_btn(text='プラン診断をはじめる', cls=''):
    """どこからでもプラン診断のモーダルを開くボタン。JS が動かないときは、ページ下に置いた診断へ移動するリンク"""
    return f'<a class="btn plan {cls}" href="#diag" data-open-diag aria-haspopup="dialog">{bico("diag")}<span>{text}</span></a>'

def quote_btn(text='見積を依頼する', cls=''):
    return f'<a class="btn quote {cls}" href="contact.html">{bico("mail")}<span>{text}</span></a>'

def sec(sid, tag, title, body, lead='', tone=''):
    """1段のセクション。上にタグ・見出し・リード、その下に中身。tone：''＝白、'band'＝淡いティール、'bandg'＝クリーム"""
    cls, inner = (f'{tone} sec-2', 'wrap pad-band') if tone else ('sec', 'wrap')
    ld = f'<p class="t-lead">{lead}</p>' if lead else ''
    return (f'<section id="{sid}" class="{cls}" aria-labelledby="{sid}-title"><div class="{inner} stack s-56">'
            f'<div class="sec-head stack">{lab(tag)}<h2 class="t-h2" id="{sid}-title" data-rv>{title}</h2>{ld}</div>\n{body}\n</div></section>')

def page_head(crumb, title, lead):
    """下層ページの頭：パンくず・見出し・リード"""
    return (f'<div class="wrap ph-head stack s-48" id="top"><nav aria-label="パンくず"><ol class="crumb"><li><a href="index.html">トップ</a></li>'
            f'<li aria-current="page">{crumb}</li></ol></nav><h1 class="t-h1">{title}</h1><p class="t-lead">{lead}</p></div>')

def cta_box(title='日程と会場だけで、見積書をお送りします', note='1営業日以内に、スタッフの役割と機材の内訳が入った見積書PDFをメールでお送りします。'):
    return (f'<section class="sec-3 cta-end" aria-label="見積の依頼"><div class="wrap"><div class="boxd cta-in"><div class="stack"><p class="t-h2s">{title}</p>'
            f'<p class="t-note">{note}</p></div><div class="btns">{quote_btn("見積書を受け取る", "lg")}{diag_btn("プラン診断をする", "lg")}</div></div></div></section>')

def head(title, desc, home=False, extra=''):
    intro = ("try{if(!sessionStorage.getItem('karura-intro')&&!matchMedia('(prefers-reduced-motion: reduce)').matches)"
             "{document.documentElement.classList.add('intro-on');sessionStorage.setItem('karura-intro','1')}}catch(e){}") if home else ''
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%2300b4c3'/%3E%3Ccircle cx='16' cy='16' r='5' fill='%23ffffff'/%3E%3C/svg%3E">
<script>document.documentElement.classList.add('js');{intro}</script>
<link rel="preload" href="assets/fonts/zkgn-500.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/karura-tokens.css">
<link rel="stylesheet" href="assets/site.css">
<script type="module" src="assets/site.js"></script>{extra}
</head>
<body>
'''

def header(page):
    """スマホ：上のバー＋メニューの横並び（いっしょに追従）。PC：左の固定レール（ロゴ・メニュー・2つの行動）"""
    pages = [('index.html', 'トップ'), ('contact.html', 'お問い合わせ'), ('rules.html', 'デザインルール')]
    pg = ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in pages)
    items = ''.join(f'<li><a href="{menu_href(h, page)}">{t}<span aria-hidden="true">›</span></a></li>' for h, t in MENU)
    return f'''<a class="skip" href="#main">本文へ移動</a>
<header class="hdr">
<div class="hdr-bar">
<a class="logo" href="index.html" aria-label="{NAME} トップページ">{NAME_EN}<small>{NAME}</small></a>
<button type="button" class="menu-btn" data-open-menu aria-haspopup="dialog" aria-controls="menu"><span class="vh">メニューを開く</span><i></i><i></i></button>
<a class="menu-fallback t-note" href="#fnav">メニュー</a>
</div>
<nav class="subnav" aria-label="メニュー"><ol>{menu_items(page)}</ol><span class="subnav-meter" aria-hidden="true"></span></nav>
<div class="rail-foot">
<a class="tile tile--plan" href="#diag" data-open-diag aria-haspopup="dialog">{bico("diag")}8問で<br>プラン診断</a>
<a class="tile tile--quote" href="contact.html">{bico("mail")}見積を<br>依頼する</a>
<nav aria-label="ページ"><ul class="rail-pages">{pg}</ul></nav>
</div>
</header>
<dialog id="menu" class="menu" aria-label="メニュー">
<div class="menu-head"><span class="logo">{NAME_EN}<small>{NAME}</small></span><form method="dialog"><button class="menu-close">閉じる</button></form></div>
<nav aria-label="メニュー"><ul>{items}<li><a href="index.html#faq">よくある質問<span aria-hidden="true">›</span></a></li><li><a href="contact.html">お問い合わせ・お見積<span aria-hidden="true">›</span></a></li></ul>
<div class="stack s-16 menu-acts">{diag_btn("8問でプランを診断する", "full")}{quote_btn("見積を依頼する", "full")}</div></nav>
</dialog>
'''

def footer(page, form=False):
    contact = ''
    if form:
        contact = f'''<section id="contact" class="boxg stack s-48" aria-labelledby="contact-title" style="color:var(--ink)">
<div class="g57">
<div class="stack">{lab('見積を依頼する')}<h2 id="contact-title" class="t-h2">日程と会場だけ、<br>教えてください</h2>
<p class="t-lead">{mk('1営業日以内に、宛名入りの見積書PDF')}をメールでお送りします。詳しい内容は、その後のやりとりで詰めていきます。</p>
<p class="t-note">［年度末（2〜3月）の空き日程：残り〇日］</p>
<p class="t-note" id="tel">お電話でも受け付けています　［電話番号］　［受付時間］</p></div>
{quote_form('f')}
</div></section>'''
    links = MENU + [('index.html#option', 'オプション'), ('index.html#faq', 'よくある質問'), ('contact.html', 'お問い合わせ・お見積'), ('rules.html', 'デザインルール')]
    nav = ''.join(f'<li><a href="{menu_href(h, page)}">{t}</a></li>' for h, t in links)
    return f'''<div class="diag-host"><dialog id="diag" class="dg-modal" aria-labelledby="diag-title">
<div class="dg-modal-head"><p class="t-ct" id="diag-title">8問でプラン診断</p><form method="dialog"><button class="menu-close">閉じる</button></form></div>
{diag()}
</dialog></div>
<footer class="foot">
{contact}
<nav class="{"mtl" if form else ""}" aria-label="フッターメニュー" id="fnav"><ul class="fnav">{nav}</ul></nav>
<p class="copy">© 2026 {NAME_EN}　対応エリア：新宿から90分圏内　［運営者名］</p>
</footer>
<nav class="spbar" aria-label="よく使う操作"><a href="#diag" data-open-diag aria-haspopup="dialog">{bico("diag")}プラン診断</a><a href="contact.html">{bico("mail")}見積を依頼する</a></nav>
</body>
</html>
'''

def quote_form(p, prefill=False, full=False, fid=''):
    """見積フォーム。必須4項目。full=True で任意項目も"""
    def fld(name, label, ph, typ='text', req=True, err=''):
        r = ' required' if req else ''
        mk = '<span class="req">必須</span>' if req else ''
        ac = {'email': ' autocomplete="email" inputmode="email"'}.get(typ, '')
        e = f'<p class="err" id="{p}-{name}-e">{err}</p>' if err else ''
        d = f' aria-describedby="{p}-{name}-e"' if err else ''
        return (f'<div class="fld"><label for="{p}-{name}">{label}{mk}</label>'
                f'<input id="{p}-{name}" name="{name}" type="{typ}" placeholder="{ph}"{r}{ac}{d}>{e}</div>')
    req = (fld('date', '開催日（未定でも可）', '例：2027年2月20日', err='開催日を入力してください。未定なら「未定」で大丈夫です')
           + fld('venue', '会場', '例：〇〇大学 △△ホール', err='会場を入力してください')
           + fld('size', '登壇者と来場者のおおよその人数', '例：登壇4人、来場150人', err='おおよその人数を入力してください')
           + fld('email', 'メールアドレス', 'name@example.ac.jp', 'email', err='メールアドレスの形で入力してください（例：name@example.ac.jp）'))
    opt = ''
    if full:
        plans = ''.join(f'<label><input type="checkbox" name="plan" value="{v}">{v}</label>' for v in ['スタンダード（25万円）', 'ワイド（35万円）', 'オーダー（ロケ配信・台本制作など）', 'コーチング', 'まだわからない'])
        opt = f'''<h3 class="t-ct">わかる範囲でご記入ください（任意）</h3>
<div class="f2">{fld('name', 'お名前', '', req=False)}{fld('org', 'ご所属（見積書の宛名になります）', '', req=False)}</div>
<fieldset class="fld"><legend>気になっているプラン</legend><div class="checks">{plans}</div></fieldset>
<div class="checks"><label><input type="checkbox" name="aimitsu" value="はい">相見積のための依頼です（仕様書のひな形も一緒にお送りします）</label></div>
<div class="fld"><label for="{p}-memo">気になっていること、前回の配信で困ったこと</label><textarea id="{p}-memo" name="memo"></textarea></div>'''
    pf = ' data-prefill' if prefill else ''
    note = '<p class="form-msg prefill" role="status" hidden></p>' if prefill else ''
    head_ = '<h3 class="t-ct">必須（4項目）</h3>' if full else '<h3 class="t-ct">見積書を受け取る</h3>'
    idattr = f' id="{fid}"' if fid else ''
    return f'''<form{idattr} class="boxw stack" data-form="quote" data-endpoint=""{pf} aria-label="見積の依頼">
{note}{head_}
<div class="f2">{req}</div>
{opt}
<button class="btn full quote" type="submit">{bico("mail")}<span>見積書を受け取る</span></button>
<p class="t-note t-sub">送信いただいても、こちらから電話での営業はいたしません。相見積のためのご依頼も歓迎します。</p>
<p class="form-msg" role="status" hidden></p>
</form>'''

# ------------------------------------------------------------------ プラン診断
DIAG_Q = [
    ('spk', '登壇者は何人ですか', '司会は含めません。パネルディスカッションの方も数えます', [('1', '1人'), ('2-3', '2〜3人'), ('4-6', '4〜6人'), ('7+', '7人以上')]),
    ('aud', '会場に来る人は、何人くらいですか', 'おおよそでかまいません', [('-30', '30人まで'), ('30-100', '30〜100人'), ('100-300', '100〜300人'), ('300+', '300人以上')]),
    ('rmt', 'オンラインから登壇する人はいますか', '遠隔地の講師がZoomなどで話す場合です', [('n', 'いない'), ('y', 'いる')]),
    ('qa', '会場の質問を、オンラインの視聴者にも届けたいですか', '会場の声は、マイクを通さないと配信に入りません', [('y', '届けたい'), ('n', '会場だけでいい')]),
    ('time', '配信する時間は、どのくらいですか', '休憩を含めた、配信の開始から終了まで', [('-2', '2時間まで'), ('2-3', '2〜3時間'), ('3+', '3時間を超える')]),
    ('pub', '録画を公開する予定や、学外の視聴者・来賓はありますか', 'どちらかに当てはまれば「ある」', [('y', 'ある'), ('n', 'ない')]),
    ('opt', '同じ日に頼みたいものはありますか', 'いくつでも選べます。なければ、そのまま「次へ」', [('photo', '記録写真'), ('edit', '記録映像の編集'), ('digest', '2分のダイジェスト映像'), ('text', '文字起こし')]),
    ('self', '来年度からは、自分たちで配信したいですか', '小さい会だけでも自分たちで、という場合も「はい」', [('y', 'はい'), ('n', 'いいえ、毎回任せたい')]),
]
def diag():
    qs = ''
    for i, (k, q, hint, opts) in enumerate(DIAG_Q, 1):
        multi = k == 'opt'
        t = 'checkbox' if multi else 'radio'
        o = ''.join(f'<label class="dg-opt"><input type="{t}" name="{k}" value="{v}">{l}</label>' for v, l in opts)
        qs += (f'<fieldset class="dg-q" data-key="{k}"{" data-multi" if multi else ""} aria-describedby="dg-h{i}">'
               f'<legend><span class="dg-n">Q{i} / {len(DIAG_Q)}</span>{q}</legend><p class="dg-hint" id="dg-h{i}">{hint}</p>'
               f'<div class="dg-opts">{o}</div></fieldset>')
    return f'''<div class="dg" data-dg>
<div class="dg-head"><p class="dg-count"><b class="dg-i">1</b> / {len(DIAG_Q)}</p><div class="dg-prog" aria-hidden="true"><i></i></div><button type="button" class="dg-back" hidden>戻る</button></div>
<p class="vh dg-live" aria-live="polite"></p>
<form class="dg-form" action="contact.html" method="get" aria-label="プラン診断">
{qs}
<div class="dg-ctl"><button class="btn dg-next" type="submit">次へ</button></div>
<p class="dg-nojs t-note t-sub">お使いの環境では、結果をその場で表示できません。「次へ」を押すと、回答を持って見積のご依頼に進みます。</p>
</form>
<section class="dg-res" tabindex="-1" aria-labelledby="dg-result-title" aria-live="polite"></section>
</div>'''

# ------------------------------------------------------------------ 表
def tbl_gear():
    """持ち込む機材。機種名は並べない（選ぶ人が知りたいのは、数と何のために使うか）"""
    rows = [('カメラ', '3台', '話している人のアップ、登壇者全体、会場全体'),
            ('マイク', '5本', '登壇者4人分と、会場の質問用1本'),
            ('画面の切り替え機', '［数］', '発表スライドとカメラ映像の切り替え'),
            ('録画機', '2系統', '片方が止まっても、もう片方で記録を残します'),
            ('回線', '2系統', '会場の回線が切れても、予備回線で配信を続けます')]
    tr = ''.join(f'<tr><td class="k">{a}</td><td class="k" data-l="数">{c}</td><td data-l="用途">{d}</td></tr>' for a, c, d in rows)
    return f'<table class="tbl"><caption class="vh">持ち込む機材（スタンダード）</caption><thead><tr><th scope="col">種類</th><th scope="col">数</th><th scope="col">用途</th></tr></thead><tbody>{tr}</tbody></table>'

def tbl_option():
    """オプションは1つの表。体制や条件で足すもの（旧「追加料金の5つ」）と、同じ日に頼めるもの"""
    groups = [('当日の体制や条件で足すもの', [
                  ('配信時間の延長', '3時間を超える配信。1時間ごと', '［金額］'),
                  ('スタッフの追加', 'オンラインから登壇する人がいる会、マイクが6本以上要る会', '［金額］'),
                  ('カメラの追加', '1台ごと', '［金額］'),
                  ('回線の持ち込み', '会場に使えるインターネット回線がないとき', '［金額］'),
                  ('対応エリア外の交通費・宿泊費', '新宿から90分圏内の外の会場', '実費')]),
              ('同じ日に頼めるもの', [
                  ('記録写真', '専任のカメラマン1名が、報告書や広報に使える写真を撮ります', '［金額］'),
                  ('記録映像の編集', '3台のカメラの映像から、話している人に合わせて切り替えた記録映像を、字幕つきで作ります', '［金額］'),
                  ('2分のダイジェスト映像', '次回の告知や成果報告に使える、短いまとめの映像を作ります', '［金額］'),
                  ('文字起こし', '報告書の下書きにそのまま使えるテキストを作ります', '［金額］'),
                  ('LINEで申し込む受付', '申込をLINEログインにして、主催者のLINE公式アカウントの友だちを増やします。LINE側の設定も代行します', '［金額］')])]
    body = ''
    for g, rows in groups:
        body += f'<tbody><tr class="tbl-group"><th scope="rowgroup" colspan="3">{g}</th></tr>'
        body += ''.join(f'<tr><th scope="row">{a}</th><td data-l="内容">{b}</td><td class="r" data-l="料金（税別）">{c}</td></tr>' for a, b, c in rows) + '</tbody>'
    return f'<table class="tbl tbl--opt"><caption class="vh">オプションの一覧</caption><thead><tr><th scope="col">オプション</th><th scope="col">内容</th><th scope="col" class="r">料金（税別）</th></tr></thead>{body}</table>'

def tbl_plans():
    """プランの違いだけを並べる表。どのプランにも含まれるものは、表の下に1回だけ書く（COMMON）。スマホでは横にスクロール"""
    Y = '<span class="yes" role="img" aria-label="含む">○</span>'
    N = '<span class="no" role="img" aria-label="含まない">—</span>'
    rows = [('料金（税別）', '<b class="cmp-price">25<small>万円</small></b>', '<b class="cmp-price">35<small>万円</small></b>', '<b class="cmp-price">ASK</b>'),
            ('向いている会', '登壇者2〜6人<br>会場50〜300人', '登壇者7人以上<br>会場300人を超える', '会場の外からの中継<br>複数の会場・複数日'),
            ('スタッフ', '2名', '3名', '内容に合わせて'),
            ('カメラ', '3台', '5台', '内容に合わせて'),
            ('マイクの持ち込み', f'5本まで{tip("tip-mic", "マイクが5本の理由", "登壇者4人分と、会場の質問用1本です。6本以上必要な会は、スタッフを1名追加します。")}', '［本数］まで', '内容に合わせて'),
            ('配信の時間／会場での作業', f'3時間／6時間まで{tip("tip-time", "作業時間の内訳", "設営2時間、配信3時間、撤収1時間が目安です。")}', '［時間］', '内容に合わせて'),
            ('オンラインからの登壇', 'スタッフ1名の追加で対応', Y, Y),
            ('ロケ配信（会場の外からの中継）', N, N, Y),
            ('進行台本の制作', N, N, Y)]
    tr = ''.join(f'<tr><th scope="row">{a}</th><td class="is-main">{b}</td><td>{c}</td><td class="is-ask">{d}</td></tr>' for a, b, c, d in rows)
    return (f'<div class="cmp-wrap" tabindex="0" role="region" aria-label="プランの違い（横にスクロールできます）"><table class="cmp"><caption class="vh">プランの違い</caption>'
            f'<thead><tr><td></td><th scope="col" class="is-main">スタンダード</th><th scope="col">ワイド</th><th scope="col" class="is-ask">オーダー</th></tr></thead><tbody>{tr}</tbody></table></div>')

PRECHECK = [('Zoomでのオンライン下見', '会場をスマホで映していただき、カメラとマイクを置く場所、電源、客席からの見え方を一緒に確かめます'),
            ('回線の診断', '会場のインターネット回線が、配信に足りる速さと安定さかを確かめます'),
            ('会場診断ツール', '会場でスマホやPCから開くだけで、回線の速さと安定さを測れるツールをお渡しします［準備中］')]

COMMON = ['発表スライドの映像の取り込み', '会場設備のマイク音声の取り込み', '予備の録画機と、予備のインターネット回線', '事前の打ち合わせと会場の下見', '録画データの納品',
          '受付用のデジタルチケット（来場300人まで）', '対応エリア（新宿から90分圏内）の交通費']

def tip(tid, label, body):
    """「?」で開く補足。popover 未対応では、本文の下に注記として出る"""
    return (f'<span class="tip"><button type="button" class="tip-btn" popovertarget="{tid}" aria-label="{label}" style="anchor-name:--{tid}">?</button>'
            f'<span id="{tid}" popover class="tip-body" style="position-anchor:--{tid}">{body}</span></span>')

def case(n, photo, alt, size_note=''):
    """事例のカード（横スクロールの1枚）。どの事例も同じ項目で並べる"""
    return f'''<li class="case-card stack s-16"><div class="zoom">{img(photo, alt)}</div>
<p class="t-note t-sub">事例 {n}　|　［主催機関名］</p>
<div class="case-tags"><span class="pill">［大学］</span><span class="pill">［シンポジウム］</span></div>
<h3 class="t-ct">［会の名称：課題と成果を一文で］</h3>
<p class="t-body">［当日起きたことと、どう戻したか。2〜3行］</p>
<dl class="chips"><div class="chip"><dt>会の規模</dt><dd>登壇［ ］人、会場［ ］人</dd></div><div class="chip"><dt>当日の体制</dt><dd>スタッフ［ ］名{size_note}</dd></div>
<div class="chip"><dt>使用機材</dt><dd>カメラ［ ］台、マイク［ ］本</dd></div><div class="chip"><dt>金額</dt><dd>［25万〜35万円］</dd></div></dl></li>'''

FAQ = [
    ('何日前までに頼めば間に合いますか', '［最短の日数と、繁忙期の目安］'),
    ('Zoom、YouTube、Teamsのどれに対応していますか', '［対応している配信先］'),
    ('登壇者の一部がオンラインから参加します', '対応できます。スタッフを1名追加します（［金額］）。'),
    ('会場にインターネット回線がありません', '配信用の回線を持ち込みます（［金額］）。事前に会場で電波状況を確認します。'),
    ('配信が止まった場合、料金はどうなりますか', '［返金・減額の規定］'),
    ('対応エリアはどこまでですか', '新宿駅からおおむね90分以内で伺える会場が対応エリアです。エリア内は、会場の下見も交通費も料金に含まれます。エリア外の会場は、交通費と宿泊費の実費で伺います。'),
    ('登壇者が1人の講演や、30人ほどの勉強会でも頼めますか', 'お受けします。ただ、カメラ1台とお手持ちのiPhoneやPCで十分に伝わる会でもあります。<a href="#diag" data-open-diag>8問のプラン診断</a>で、ご自身で配信できるかどうかを確かめられます。'),
    ('屋外や複数の会場からの中継、同時通訳はできますか', 'オーダーでお見積りします。会場の下見をしてから、必要な人と機材をご提案します。'),
    ('依頼する前に、その会場で配信できるか確かめられますか', '確かめられます。Zoomでのオンライン下見と回線の診断を、無料で行います。会場で開くだけで回線を測れる会場診断ツールもお渡しします（［準備中］）。'),
    ('写真や記録映像もまとめて頼むと、安くなりますか', 'なります。配信・記録写真・記録映像の編集をまとめると、セット割で［割引率］引きです。'),
    ('毎月の公開講座など、定期的な配信の割引はありますか', 'あります。回数に応じて割引します。年間の予定がわかれば、まとめてお見積りします。'),
    ('参加者の受付や名簿の管理もお願いできますか', '対応できます。どのプランにも受付用のデジタルチケットが含まれます。申込の受付、当日の入場、終了後の来場者数の報告までを引き受けます。詳しくは<a href="reception.html">受付と現場の道具</a>をご覧ください。'),
    ('有料の会のチケット販売はできますか', '販売と決済は行っていません。参加費がある会は、お使いのチケット販売サービスや請求書で集金いただき、申込者の名簿（CSV）をお預かりして、当日の入場だけを引き受けます。'),
    ('参加者の個人情報は、どう扱いますか', '名簿は受付と報告のためだけに使い、会の終了から30日で自動的に削除します。委託契約書や情報セキュリティのチェックシートが必要な場合は、ご相談ください。'),
    ('相見積のための見積依頼でもかまいませんか', '歓迎します。<a href="public.html#spec">仕様書のひな形</a>と見積書の見本もお送りしますので、他社への依頼にもそのままお使いください。'),
    ('支払い方法を教えてください', '請求書払い（後払い）に対応しています。見積書・納品書・請求書の3点を発行します。'),
]

# ------------------------------------------------------------------ メインビジュアル（リードと箇条書きは3案を比べる。採用中は MV_USE）
# 箇条書きは、それぞれの中身が書いてある場所へのリンクにする（href はトップから見た場所。ほかのページでは index.html を付ける）
MV_KIND = 'シンポジウム・講演会・公開講座のライブ配信／ハイブリッド配信（会場＋オンライン）'
MV = {
    'A': {'name': '案A：必要なぶんだけ',
          'h1': '必要なぶんの機材と人で、<br>会場とオンラインに届けます。',
          'lead': '大学・公共機関のシンポジウムと講演会を、ハイブリッドで配信します。',
          'kind': 'list',
          'items': [('カメラ3台・スタッフ2名・マイク5本で、25万円（税別）から', '#price'), ('見積書に、スタッフの役割と機材の内訳をすべて書きます', '#cost'),
                    ('カメラ1台で足りる会なら、そうお伝えします', '#faq')]},
    'B': {'name': '案B：見積の中身から',
          'h1': '配信の見積を、<br>中身から読めるものに。',
          'lead': '誰が来て、何を持ち込み、何時間いるか。見積書にすべて書きます。',
          'kind': 'list',
          'items': [('スタンダード 25万円：カメラ3台・スタッフ2名', '#price'), ('ワイド 35万円：カメラ5台・スタッフ3名', '#price'),
                    ('オプションの料金も、表で公開しています', '#option')]},
    'C': {'name': '案C：いまの見出し＋対象・体制・費用',
          'h1': 'カメラ5台はいりません。<br>でも1台では、パネルディスカッションは撮れません。',
          'lead': '会の大きさに合った体制で、会場の様子をそのままオンラインに届けます。',
          'kind': 'facts',
          'items': [('対象', '登壇者2〜6人、会場50〜300人のシンポジウム・講演会', '#works'), ('体制', 'カメラ3台、スタッフ2名、マイク5本まで', 'service.html#team'),
                    ('費用', '25万円（税別）から。内訳はすべて見積書に書きます', '#price')]},
}
MV['D'] = {'name': '案D：大手と個人の間',
           'h1': '大手は大げさ。個人は不安。<br>その間の配信代行です。',
           'lead': '大学・公共機関のシンポジウムと講演会を、会の大きさに合った体制でハイブリッド配信します。',
           'kind': 'facts', 'items': MV['C']['items']}
MV_USE = 'C'

def mv(key, page='index.html', tag='h1', hid='mv-title'):
    """写真の上には、種類・見出し・リードだけを重ねる。箇条書き（それぞれの節への矢印つきリンク）と2つの行動は、写真の下の白い面に置く。
       写真はまだ穴埋め（ダミーの会場写真を暗くして敷いている）"""
    v = MV[key]
    at = lambda h: h if (page == 'index.html' or not h.startswith('#')) else 'index.html' + h
    if v['kind'] == 'facts':
        body = '<dl class="mv-facts">' + ''.join(f'<div><dt>{a}</dt><dd><a href="{at(h)}"><span>{b}</span>{go()}</a></dd></div>' for a, b, h in v['items']) + '</dl>'
    else:
        body = '<ul class="mv-facts mv-facts--list">' + ''.join(f'<li><a href="{at(h)}"><span>{t}</span>{go()}</a></li>' for t, h in v['items']) + '</ul>'
    return f'''<section class="mv" aria-labelledby="{hid}"><div class="mv-bg">{img('P03', '', lazy=False, eager_high=True)}</div>
<div class="wrap mv-in"><div class="mv-copy stack">
<p class="hero-kind">{MV_KIND}</p>
<{tag} class="t-h1" id="{hid}">{v['h1']}</{tag}>
<p class="t-lead">{v['lead']}</p>
</div></div></section>
<div class="wrap mv-after">{body}<div class="mv-acts">{diag_btn('プラン診断')}{quote_btn()}</div></div>'''

# ------------------------------------------------------------------ トップ
def index():
    intro = '<div class="intro" aria-hidden="true"><p>' + ''.join(f'<span style="--i:{i}">{c}</span>' for i, c in enumerate(NAME_EN)) + '</p></div>'
    hero = mv(MV_USE)
    voices = [('大学の事務・広報のご担当', '今年からシンポジウムをハイブリッドで、と言われました。Zoomで足りるのかも分からないし、失敗したら自分の責任です。大手の見積は桁が違いました。', '#price', '料金は3つ、すべて公開しています'),
              ('自治体・公共施設のご担当', '市民講座の企画と運営は自分たちでできます。配信だけを切り出して頼みたい。でも当日、誰が来て何をするのかは先に知っておきたいです。', 'service.html#team', '当日のスタッフ表を、見積と一緒にお渡しします'),
              ('学会・研究機関のご担当', '助成元も来賓も見ている、やり直しのきかない会です。「大丈夫です」ではなく、何がどう大丈夫なのかを説明できないと、決裁が通りません。', 'service.html#trouble', '起きがちなトラブルと、その予防を書いています')]
    vc = ''.join(f'<li class="voice"><blockquote class="voice-q"><p>{q}</p></blockquote><p class="voice-who t-note t-sub">{w}</p>'
                 f'<a class="tlink" href="{h}">{t}{go()}</a></li>' for w, q, h, t in voices)
    worries = sec('worries', 'よくあるお悩み', 'こんなことで、<br>困っていませんか', f'<ul class="voices">{vc}</ul>',
                  lead='初めて配信を任された方から、よく伺うお悩みです。どれも、ご依頼の前にお答えできます。')

    work = [('準備', '打ち合わせと下見', 'オンラインで30分の打ち合わせ、会場の下見、配信先（Zoom・YouTubeなど）の設定'),
            ('設営', '約2時間', 'カメラ・マイク・回線を置いて、音と映像を確かめます'),
            ('本番', '配信3時間まで', '撮影、音声の調整、画面の切り替え、配信の見守り'),
            ('撤収と納品', '約1時間', '機材を片づけ、録画データを納品します')]
    wk = ''.join(f'<li><span class="n">0{i}</span><span class="a">{a} <small>{t}</small></span><span class="b">{b}</span></li>' for i, (a, t, b) in enumerate(work, 1))
    factors = [('face', '人', 'スタッフの人数。映像と、音声・配信に1人ずつの2名が基本です。オンライン登壇やマイク6本以上の会では1名増えます。'),
               ('switch', '機材', 'カメラとマイクの数、予備の機材。カメラの台数は、登壇者の人数と会場の広さで決まります。'),
               ('report', '時間', '会場にいる時間。設営から撤収まで6時間（うち配信3時間）が基本です。')]
    fc = ''.join(f'<li class="reason">{ico(k)}<div class="stack s-16"><h3 class="t-ct">{t}</h3><p class="t-body">{b}</p></div></li>' for k, t, b in factors)
    lean = [('全員に持ち場があります', 'スタッフは、映像と、音声・配信の2つの持ち場に1人ずつ。持ち場のない人の費用はいただきません。'),
            ('機材は、会に合わせて選びます', '登壇者2〜6人の会にはカメラ3台。5台を持ち込むのは、登壇者が多い会や会場が広い会だけです。'),
            ('予備は、止まると取り返しがつかないものだけ', '録画機と回線は2系統。どちらかが止まっても、配信と記録は続きます。'),
            ('見積書にすべて書きます', '人・機材・時間の内訳を明記します。あとから増えるのは、オプションの表にあるものだけです。')]
    ln = ''.join(f'<li><span class="a">{a}</span><span class="b">{b}</span></li>' for a, b in lean)
    cost = sec('cost', '費用の内訳', '配信の費用は、<br>人と機材と時間で決まります', f'''<div class="stack"><h3 class="sub">配信の仕事の内訳</h3><ol class="steps">{wk}</ol></div>
<div class="stack"><h3 class="sub">費用を決める3つ</h3><ul class="reasons reasons--3">{fc}</ul></div>
<div class="boxg stack s-48" style="color:var(--ink)"><div class="stack s-16"><h3 class="t-h2s">無駄のない配信とは</h3>
<p class="t-body">引っ越しと同じです。単身の荷物に10トントラックはいりませんが、冷蔵庫を友人の軽トラックで運ぶのは不安です。配信も、会の大きさに合った人と機材を選ぶのがいちばん安く、いちばん確かです。</p></div><ul class="lean">{ln}</ul></div>''',
               lead='配信代行の見積は、会場に来る人の数、持ち込む機材、会場にいる時間の3つで、ほぼ決まります。カルラライブは、会の大きさに必要なぶんだけを組み合わせます。')

    plans = [('main', 'スタンダード', '25', '万円（税別）', 'カメラ3台・スタッフ2名・マイク5本まで', '登壇者2〜6人、会場50〜300人のシンポジウム・講演会'),
             ('', 'ワイド', '35', '万円（税別）', 'カメラ5台・スタッフ3名・マイク［本数］まで', '登壇者が7人以上の会、会場が300人を超える会、客席の様子も届けたい会'),
             ('ask', 'オーダー', 'ASK', '', 'ロケ配信、進行台本の制作など。内容に合わせてお見積りします', '屋外や会場の外からの中継、複数の会場や複数日にわたる会')]
    pl = ''.join(f'''<li class="plan-card stack s-16{" plan-card--" + k if k else ""}">{'<p class="plan-badge">基本のプラン</p>' if k == 'main' else ''}<h3 class="plan-name">{n}</h3><p class="t-big2">{p}{f"<small>{u}</small>" if u else ""}</p>
<p class="plan-spec">{sp}</p><dl class="plan-fit"><dt>向いている会</dt><dd>{f}</dd></dl></li>''' for k, n, p, u, sp, f in plans)
    price = sec('price', '料金プラン', '料金は3つです', f'''<ul class="plans">{pl}</ul>
<p class="t-note t-sub">定期的に配信する会（毎月の公開講座など）は、回数に応じて割引があります。</p>
<div class="stack"><h3 class="sub">プランの違い</h3>{tbl_plans()}</div>
<div class="stack"><h3 class="sub">どのプランにも含まれるもの</h3><ul class="incl">{''.join(f'<li>{ico("check", "s")}<span>{t}</span></li>' for t in COMMON)}</ul></div>
<div class="boxw stack" id="precheck"><h3 class="t-h3">ご依頼の前に、無料でできること</h3>
<ul class="incl">{''.join(f'<li>{ico("check", "s")}<span><b>{a}</b>　{b}</span></li>' for a, b in PRECHECK)}</ul>
<p class="t-note t-sub">見積を依頼するときに「事前の確認を希望」と書いてください。依頼しないと決めた会でも、費用はかかりません。</p></div>
<div class="btns">{quote_btn('見積を依頼する', 'lg')}</div>
<p class="t-note t-sub">見積書の見本は、上司への説明や相見積にそのまま使えます。　<a class="tlink" href="contact.html#sample">見積書の見本を見る{go()}</a></p>''',
                lead=f'どのプランにも、事前の打ち合わせ、会場の下見、録画データの納品、受付用のデジタルチケットが含まれます。{mk("見積書にも同じ内容を書きます。")}', tone='bandg')

    option = sec('option', 'オプション', '必要なときだけ、足せるもの', f'''<div class="boxd set stack"><p class="set-tag">セット割</p>
<h3 class="t-h2s">配信・記録写真・記録映像の編集を、まとめて頼むと［割引率］引き</h3>
<p class="set-price"><span class="t-note">別々に頼んだ場合</span><s>［合計金額］</s><span aria-hidden="true">→</span><b>［セット価格］</b><small>（税別）</small></p>
<p class="t-note">当日の立ち会いが1回で済み、打ち合わせ・見積・請求もまとめて1回になります。その手間が減るぶんを、お値引きします。</p></div>
{tbl_option()}
<p class="t-note t-sub">オプションは、どのプランにも付けられます。プラン診断で選んだものは、見積のご依頼にそのまま入ります。</p>''',
                 lead='当日の体制や条件で足すものと、同じ日に頼める記録写真・記録映像です。どれも見積書に1行ずつ書きます。見積・打ち合わせ・請求は、配信とまとめて1回です。')

    kinds = [('face', 'パネルディスカッションのあるシンポジウム', '登壇者2〜6人。話す人が替わるたびに、カメラを切り替えます'),
             ('mic', '公開講座・講演会', '会場に50〜300人。会場の質問も、オンラインの視聴者に届けます'),
             ('backup', '来賓や助成元、学外の方が見る会', 'やり直しのきかない配信。予備の録画と回線を用意します'),
             ('switch', '遠隔地の講師が登壇する会', '会場とオンラインの登壇者が、同じ画面で話せるようにします')]
    kd = ''.join(f'<li class="reason">{ico(k)}<div class="stack s-16"><h3 class="t-ct">{t}</h3><p class="t-body">{b}</p></div></li>' for k, t, b in kinds)
    works = f'''<section id="works" class="sec" aria-labelledby="works-title"><div class="wrap stack s-56">
<div class="sec-head stack">{lab('対応事例')}<h2 class="t-h2" id="works-title" data-rv>これまでに配信した会</h2>
<p class="t-lead">{mk('すべての事例を、人数・体制・機材・金額の同じ項目で載せています。')}ご自身の会に近いものを探してください。</p></div>
<div class="stack"><h3 class="sub">よくご依頼いただく会</h3><ul class="reasons">{kd}</ul></div>
<div class="stack"><h3 class="sub">これまでに配信・記録を担当した機関</h3><p class="t-note">［配信した会の件数、継続して依頼いただいている機関の数］</p>
<ul class="logos">{''.join('<li><div class="ph">［ロゴ］</div></li>' for _ in range(6))}</ul></div>
</div>
<ul class="cases" aria-label="事例の一覧（横にスクロールできます）">
{case(1, 'P02', '（ダミー）パネルディスカッション全体', '（映像1名、音声・配信1名）')}
{case(2, 'P09', '（ダミー）オンライン登壇者の映る画面')}
{case(3, 'P10', '（ダミー）会場からの質問')}
{case(4, 'P03', '（ダミー）会場全体')}
</ul>
<div class="wrap mtl"><blockquote class="boxw stack" style="max-width:48rem"><p class="t-lead">［頼む前に不安だったこと、当日どうだったか。2〜3行］</p><footer class="t-note t-sub">［所属・役職・氏名（掲載できる範囲）］</footer></blockquote></div>
</section>'''

    fq = ''.join(f'<details open><summary><span class="qa-mk qa-mk--q" aria-hidden="true">Q</span>{q}</summary><div class="ans"><span class="qa-mk qa-mk--a" aria-hidden="true">A</span><p class="t-body">{a}</p></div></details>' for q, a in FAQ)
    faq = sec('faq', 'よくある質問', 'よくある質問', f'<div class="faq">{fq}</div>', tone='band')

    return (head(f'シンポジウム・講演会のハイブリッド配信代行｜3カメ・2名・25万円〜｜{NAME}',
                 '大学や公共機関のシンポジウム、公開講座をハイブリッドで配信します。カメラ3台・スタッフ2名・マイク5本までで25万円（税別）から。8問のプラン診断で、合うプランと費用がわかります。', home=True)
            + intro + header('index.html') + '<main id="main">' + hero + worries + cost + price + option + works + faq + '</main>'
            + footer('index.html', form=True))

# ------------------------------------------------------------------ 当日の体制と流れ
def service():
    team = sec('team', '当日の体制', 'スタッフ2名、<br>それぞれに持ち場があります', f'''<ul class="staff">
<li class="staff-card"><div class="zoom">{img('P04', '（ダミー）映像担当のスタッフ')}</div><div class="stack s-16"><h3 class="t-ct">映像担当</h3><p class="t-body">カメラ3台の操作と、配信画面の切り替え</p><p class="t-note">当日いる場所：客席の後ろ、カメラの横</p><p class="t-note t-sub">［氏名・経歴一行］</p></div></li>
<li class="staff-card"><div class="zoom">{img('P05', '（ダミー）音声・配信担当のスタッフ')}</div><div class="stack s-16"><h3 class="t-ct">音声・配信担当</h3><p class="t-body">マイクと音量の調整、配信の見守り、登壇者のPCの接続</p><p class="t-note">当日いる場所：配信卓（会場の音響卓の隣）</p><p class="t-note t-sub">［氏名・経歴一行］</p></div></li></ul>
<p class="t-note">ワイド（35万円）では、3人目が［3人目の役割］を受け持ちます。</p>
<p class="t-body">見積書と一緒に「当日のスタッフ表」をお渡しします。来る人の名前、持ち場、当日いる場所を1枚にまとめたものです。会場の方や来賓に「あの人は何をしている人か」を聞かれても、すぐにお答えいただけます。</p>
<figure data-rv="media"><div class="ph" style="aspect-ratio:16/9">［図：会場の見取り図に、カメラ3台・スタッフ2名・マイクの位置を置いた配置図］</div></figure>
<div class="stack"><h3 class="t-h3">持ち込む機材（スタンダード）</h3>{tbl_gear()}</div>''',
               lead='映像と、音声・配信。2つの持ち場に1人ずつで伺います。どちらも本番中ずっと手を動かす仕事です。人数を増やして見積を大きくすることはしません。')

    switching = f'''<section id="switching" class="band sec-2" aria-labelledby="sw-title"><div class="wrap pad-band stack s-56">
<div class="sec-head stack">{lab('カメラ3台の切り替え')}<h2 class="t-h2" id="sw-title" data-rv>カメラを選ぶと、<br>配信中の画面が切り替わります</h2>
<p class="t-lead">3台あると、話す人が替わるたびに映像を切り替えられます。</p></div>
<div class="g57 sw" data-sw><div class="stack s-48">
<fieldset class="cams"><legend class="vh">映すカメラを選ぶ</legend>
<label class="cam"><input type="radio" name="cam" id="cam-1" value="1" checked><b>カメラ1</b><span>話している人</span></label>
<label class="cam"><input type="radio" name="cam" id="cam-2" value="2"><b>カメラ2</b><span>登壇者全体</span></label>
<label class="cam"><input type="radio" name="cam" id="cam-3" value="3"><b>カメラ3</b><span>会場全体</span></label></fieldset>
</div>
<div class="screen" data-rv="media">
{img('P01', '（ダミー）カメラ1：話している人のアップ', 'shot shot-1')}{img('P02', '（ダミー）カメラ2：パネルディスカッション全体', 'shot shot-2')}{img('P03', '（ダミー）カメラ3：会場全体、客席とスクリーン', 'shot shot-3')}
<p class="onair"><i></i>配信中の画面</p>
<button type="button" class="sw-pause" aria-pressed="false" hidden>切り替えを止める</button>
</div></div></div></section>'''

    reasons = [('聞き取りやすい音', '会場のマイク音声を配信機材に直接取り込みます。会場にマイクがなければ5本まで持ち込みます。音が悪いと、研究まで低く見られます（<a href="https://researchportalplus.anu.edu.au/en/publications/good-sound-good-research-how-audio-quality-influences-perceptions/">Newman &amp; Schwarz 2018</a>）。'),
               ('表情がわかるアップの映像', '客席の後ろから、話している人の表情を撮ります。来場者の視界をふさぎません。'),
               ('見やすい画面の切り替え', '発表スライド、登壇者、会場全体の映像を状況に合わせて切り替えます。スライドの隅に登壇者の顔を出すこともできます。'),
               ('万が一に備える予備機材', '録画機もインターネット回線も2系統ずつ用意します。どれか1つが止まっても、配信と記録は続きます。')]
    marks = ['mic', 'face', 'switch', 'backup']
    rs = ''.join(f'<li class="reason">{ico(marks[i - 1])}<div class="stack s-16"><h3 class="t-ct"><span class="t-num">0{i}</span>{t}</h3><p class="t-body">{b}</p></div></li>' for i, (t, b) in enumerate(reasons, 1))
    day = sec('day', '当日の流れ', '当日、ご担当者は配信に<br>かかりきりにならずに済みます', f'''<ul class="reasons">{rs}</ul>
<div class="boxg stack" style="color:var(--ink)"><h3 class="t-h2s">止まらないとは言いません。止まったときにどう戻すかを、事前にお渡しします</h3>
<p class="t-note">事前に「復旧手順書」を1枚お渡しします。何が止まったら、誰が、何分で、どう復旧するかを明記しています。</p>
<div class="ph" style="background:var(--paper)">［画像：復旧手順書の実物　穴埋め08］</div></div>''',
              lead=f'登壇者を迎え、進行を見守り、来賓に挨拶する。<br>{mk("配信の実務はスタッフにお任せください。")}')
    tl = [('10:30', '搬入・設営', 'カメラ・マイク・回線を置き、音と映像を確かめます'),
          ('12:00', 'リハーサル', '登壇者のPCをつなぎ、マイクの音量と、スライドの映り方を全員分確かめます'),
          ('12:30', '開場・配信の待機', '待機画面で配信を始めておき、視聴者が入れるかを確かめます'),
          ('13:00', '本番', '撮影、音声の調整、画面の切り替え、配信の見守り（3時間まで）'),
          ('16:00', '撤収', '機材を片づけ、録画が残っているかを確かめます'),
          ('17:00', '退館', '録画データは後日、納品します')]
    tls = ''.join(f'<li><span class="tl-time">{t}</span><span class="a">{a}</span><span class="b">{b}</span></li>' for t, a, b in tl)
    timeline = sec('timeline', '当日のタイムライン', '13時に始まる会なら、<br>10時半に伺います', f'<ol class="tl">{tls}</ol>',
                   lead='時刻は一例です。会場の入れる時間と開始の時刻に合わせて、打ち合わせのときに決めます。', tone='band')
    trouble = [('声が小さい、聞こえない', '会場の音響卓から音を直接取り込み、配信の音を音声担当がヘッドホンで聞き続けます'),
               ('回線が切れる', '予備の回線を用意しておき、切れたらすぐに切り替えます'),
               ('画面の切り替えを間違える', '事前に進行表をいただき、誰が話すときにどのカメラを使うかを決めておきます'),
               ('発表資料が映らない', 'リハーサルで登壇者全員のPCをつないで確かめ、予備のPCにも資料を入れておきます'),
               ('開始が遅れる', '開始の30分前から待機画面で配信を始め、視聴者が入れることを先に確かめます')]
    tr = ''.join(f'<li><p class="pair-q"><span class="t-num">0{i}</span>{a}</p><p class="pair-a">{b}</p></li>' for i, (a, b) in enumerate(trouble, 1))
    trouble_sec = sec('trouble', '起きがちなトラブル', 'トラブルは当日起きますが、<br>原因は準備にあります', f'''<ul class="pairs">{tr}</ul>
<form id="checklist" class="boxg stack" style="color:var(--ink)" data-form="spec" data-endpoint="" aria-labelledby="cl-title">
<h3 class="t-h2s" id="cl-title">事前チェックリストを、無料でお送りします</h3>
<p class="t-note">会場の回線、マイクの本数、登壇者のPCなど、配信の前に確かめることを1枚にまとめたPDFです。ご自身で配信する会にも、そのままお使いいただけます。</p>
<div class="fld"><label for="cl-mail">メールアドレス<span class="req">必須</span></label><input id="cl-mail" name="email" type="email" placeholder="name@example.ac.jp" required autocomplete="email" aria-describedby="cl-mail-e"><p class="err" id="cl-mail-e">メールアドレスの形で入力してください</p></div>
<button class="btn full" type="submit">チェックリストを受け取る</button>
<p class="form-msg" role="status" hidden></p></form>''',
                      lead='配信でよく起きる5つと、それぞれをどう防いでいるかです。')
    return (head(f'当日の体制と流れ｜{NAME}', 'スタッフ2名の持ち場、持ち込む機材、当日の流れと、止まったときの戻し方です。')
            + header('service.html') + '<main id="main">'
            + page_head('当日の体制と流れ', '当日の体制と流れ', '誰が来て、何を持ち込み、当日どう動くか。見積書にも同じ内容を書きます。')
            + team + timeline + switching + day + trouble_sec + cta_box() + '</main>' + footer('service.html'))

# ------------------------------------------------------------------ 受付と現場の道具
def reception():
    ways = [('qr', 'QRコードで入場', '参加者のスマホに表示されたQRコードを、受付のスマホで読み取ります。専用の読み取り機はいりません。'),
            ('touch', 'タッチで入場', '受付に置いたタグにスマホをかざすか、受付でお伝えする4桁のコードを入れると、入場済みになります。受付に立つ人を減らせます。'),
            ('list', '紙の名簿も用意します', '同じ名簿を紙でもお持ちします。スマホを持っていない方や、会場の通信が不安定なときも、受付は止まりません。'),
            ('report', '終了後の報告を1枚で', '申込数、来場者数、オンライン視聴者数を1枚にまとめてお渡しします。上司や助成元への報告にそのまま使えます。')]
    ws = ''.join(f'<li class="reason">{ico(k)}<div class="stack s-16"><h3 class="t-ct"><span class="t-num">0{i}</span>{t}</h3><p class="t-body">{b}</p></div></li>' for i, (k, t, b) in enumerate(ways, 1))
    ticket = sec('ticket', '受付とチケット', '受付の名簿も、<br>配信と一緒に引き受けます', f'''<ul class="reasons">{ws}</ul>
<div class="stack"><h3 class="sub">あらかじめ決めていること</h3><ul class="rows"><li>どのプランにも含まれます。追加料金はかかりません（単体でご提供する場合の参考価格：［金額］）</li><li>チケットだけのご利用は、お受けしていません。配信をお任せいただく会でお使いいただけます</li><li>参加無料・招待制の会が対象です。チケットの販売と決済は行いません</li><li>来場300人までの会が対象です</li><li>参加者の名簿は受付と報告のためだけに使い、会の終了から30日で自動的に削除します</li></ul></div>
<p class="t-note">申込をLINEログインにして、主催者のLINE公式アカウントの友だちを増やすこともできます（<a href="index.html#option">オプション</a>）。</p>
<p class="t-note t-sub">［QR］　読み取ると、デモのチケットが開きます　［デモ環境］</p>''',
                 lead=f'申込の受付、当日の入場、終了後の報告まで。<br>{mk("来場者とオンライン視聴者が、1つの名簿にまとまります。")}')
    tools = [('S01', 'FAQ の画面', '質疑応答：FAQ', '会場とオンラインからの質問を1か所に集め、選んだ質問だけを登壇者の画面に表示します。', 'コード ［000］　質問を送ると、上の画面に表示されます'),
             ('S02', 'タイムキーパー の画面', '進行管理：タイムキーパー', '残り時間と合図を、登壇者とスタッフのスマホに表示します。進行の遅れを防ぎます。', '読み取ると、デモの進行表が開きます'),
             ('S03', 'Movie Switcher の画面', '記録映像の作成：Movie Switcher', '3台のカメラの映像から、話している人に合わせて切り替えた記録映像と字幕を作ります。', ''),
             ('', '会場診断ツールの画面', '会場の確認：会場診断ツール', '会場でスマホやPCから開くだけで、回線の速さと安定さを測ります。ご依頼の前の確認に、無料でお使いいただけます。', '［準備中］')]
    tl = ''.join(f'<li class="hi stack s-16"><div class="zoom">{img(c, "（ダミー）" + a) if c else f"<div class=ph>［画面：{a}］</div>"}</div><h3 class="t-ct">{t}</h3><p class="t-body">{b}</p>'
                 + (f'<p class="t-note t-sub">{"" if n.startswith("［準備中") else "［QR］　"}{n}</p>' if n else '') + '</li>' for c, a, t, b, n in tools)
    demo = sec('demo', '現場の道具', '現場で使っている道具を、<br>いま試せます', f'''<ul class="tools" aria-label="道具の一覧">{tl}</ul>
<p class="t-note t-sub">これらの道具は、当日私たちが用意して操作します。ご自身で使えるようになりたい方には、<a href="coaching.html">コーチング</a>をご用意しています。　［穴埋め09：デモ環境］</p>''',
               lead='お手元のスマホでお試しください。当日の質疑応答と進行がどう進むかを確認できます。', tone='band')
    return (head(f'受付と現場の道具｜{NAME}', '受付用のデジタルチケットと、当日使う質疑応答・進行管理の道具です。')
            + header('reception.html') + '<main id="main">'
            + page_head('受付と現場の道具', '受付と現場の道具', '受付の名簿と、当日の質疑応答・進行も、配信と一緒に引き受けます。')
            + ticket + demo + cta_box() + '</main>' + footer('reception.html'))

# ------------------------------------------------------------------ 自分たちで配信する
def coaching():
    steps = [('相談', '［3万円］', 'オンライン60分。機材と接続の図、当日のチェックリストを作成します'), ('同行', '［代行＋3万円］', '私たちの配信現場に入り、実際の動きを横で見て覚えます'),
             ('伴走', '［12万円］', 'ご自身で配信を操作し、私たちは横で待機します'), ('卒業', '［5万円］', '事前の機材点検と、当日のオンライン待機だけで見守ります')]
    st = ''.join(f'<li><span class="n">0{i}</span><span class="a">{a} <small>{f}</small></span><span class="b">{b}</span></li>' for i, (a, f, b) in enumerate(steps, 1))
    body = sec('coaching', '自分たちで配信する', '4つの段階で、<br>自分たちで回せるようにします', f'''<ol class="steps">{st}</ol>
<div class="btns"><a class="btn" href="contact.html#consult">コーチングについて相談する</a></div>
<p class="t-note">配信の前に確かめることをまとめた<a class="tlink" href="service.html#checklist">事前チェックリスト（無料）{go()}</a></p>''',
               lead=f'小さい会はご自身で、大きい会だけ私たちにお任せください。{mk("手順書とチェックリストが残る")}ので、担当者が替わっても引き継げます。')
    return (head(f'自分たちで配信する（コーチング）｜{NAME}', '来年度から自分たちで配信したい方へ。相談・同行・伴走・卒業の4段階で、手順書とチェックリストを残します。')
            + header('coaching.html') + '<main id="main">'
            + page_head('自分たちで配信する', '来年度からは、<br>自分たちで配信する', '小さな会なら、お手持ちの機材で配信できます。何から揃えればよいかから、一緒に整理します。')
            + body + cta_box('まだ何も決まっていない方へ', '15分のオンライン相談で、iPhoneで足りるかどうかから一緒にお話しします。決まっているのが日程だけでもかまいません。') + '</main>' + footer('coaching.html'))

# ------------------------------------------------------------------ 大学・公共機関の方へ
def public():
    flow = [('問い合わせ', '決まっているのは日程と会場だけでかまいません'), ('見積書', '1営業日以内に、宛名入りのPDFでお送りします'), ('打ち合わせと会場確認', 'オンラインで30分の打ち合わせと、会場の下見を行います'),
            ('本番', '当日、スタッフが会場に伺います'), ('納品と請求', '完了報告書、納品書、請求書をまとめてお送りします')]
    fl = ''.join(f'<li><span class="n">0{i}</span><span class="a">{a}</span><span class="b">{b}</span></li>' for i, (a, b) in enumerate(flow, 1))
    body = sec('public', '発注の手続き', '大学・公共機関の<br>発注手続きに合わせます', f'''<div class="stack"><h3 class="sub">ご依頼から納品まで</h3><ol class="steps">{fl}</ol></div>
<div class="stack"><h3 class="sub">書類と支払い</h3><ul class="rows"><li>見積書・納品書・請求書の3点を発行します</li><li>請求書払い（後払い）に対応しています</li><li>インボイス登録番号：［T0000000000000］</li><li>相見積のための見積依頼も歓迎します</li></ul></div>
<form id="spec" class="boxg stack" style="color:var(--ink)" data-form="spec" data-endpoint="" aria-labelledby="spec-title">
<h3 class="t-h2s" id="spec-title">仕様書のひな形を、そのまま使えます</h3>
<p class="t-note">配信業務の仕様書（A4 1枚、Word形式）と、見積書の見本をお送りします。他社への相見積にもそのままお使いください。</p>
<div class="fld"><label for="spec-mail">メールアドレス<span class="req">必須</span></label><input id="spec-mail" name="email" type="email" placeholder="name@example.ac.jp" required autocomplete="email" aria-describedby="spec-mail-e"><p class="err" id="spec-mail-e">メールアドレスの形で入力してください</p></div>
<button class="btn full" type="submit">ひな形を受け取る</button>
<p class="form-msg" role="status" hidden></p></form>''',
               lead=f'稟議や相見積に必要な書類を、{mk("お問い合わせの前からご用意しています。")}')
    return (head(f'大学・公共機関の方へ｜{NAME}', '見積書・納品書・請求書の3点を発行し、請求書払いに対応します。仕様書のひな形もお送りします。')
            + header('public.html') + '<main id="main">'
            + page_head('大学・公共機関の方へ', '大学・公共機関の方へ', '稟議、相見積、請求書払い。発注の手続きに合わせて書類をご用意します。')
            + body + cta_box() + '</main>' + footer('public.html'))

# ------------------------------------------------------------------ メインビジュアルの比較（持ち主の確認用。メニューには出さない）
def mvs():
    blocks = ''.join(f'<div class="mv-cmp"><div class="wrap"><p class="t-lab" id="mv-{k}">{v["name"]}{"（いま使っている案）" if k == MV_USE else ""}</p></div>'
                     f'{mv(k, "mvs.html", "p", f"mv-{k}-h")}</div>' for k, v in MV.items())
    return (head(f'メインビジュアルの比較｜{NAME}', 'トップのリード文と箇条書きの案を並べて比べるページです。')
            + header('mvs.html') + '<main id="main">'
            + page_head('メインビジュアルの比較', 'リード文と箇条書きを比べる', f'トップの最初の画面に置く文の案です。src/build.py の MV_USE を変えると、トップの文が入れ替わります。いまは「{MV[MV_USE]["name"]}」を使っています。')
            + blocks + '</main>' + footer('mvs.html'))

def contact():
    sub = contact.sub = [('top', '見積を依頼する'), ('flow', '送信後の流れ'), ('sample', '見積書の見本'), ('consult', '見積の前に相談する'), ('tel', '電話で問い合わせる')]
    flow = [('1営業日以内', '見積書PDFがメールで届きます'), ('必要に応じて', 'オンラインで30分ほど打ち合わせをします'), ('ご発注後', '事前に会場を下見します')]
    fl = ''.join(f'<li><span class="n">0{i}</span><span class="a">{a}</span><span class="b">{b}</span></li>' for i, (a, b) in enumerate(flow, 1))
    doc = '''<div class="doc-sample"><table><caption>御見積書（見本）</caption>
<tr><th>ハイブリッド配信 スタンダード<br><small>配信3時間まで、会場での作業6時間まで</small></th><td class="r">250,000</td></tr>
<tr><th>映像担当 1名／音声・配信担当 1名</th><td class="r">含む</td></tr><tr><th>カメラ3台／マイク5本まで</th><td class="r">含む</td></tr>
<tr><th>予備の録画機・予備の回線</th><td class="r">含む</td></tr><tr><th>打ち合わせ・会場の下見・録画データの納品</th><td class="r">含む</td></tr>
<tr><th>受付用のデジタルチケット（来場300人まで）</th><td class="r">含む</td></tr>
<tr><th>消費税（10%）</th><td class="r">25,000</td></tr><tr><th>合計</th><td class="r">275,000</td></tr></table></div>'''
    return (head(f'お問い合わせ・お見積｜ハイブリッド配信のご相談｜{NAME}', '日程と会場、登壇者の人数がわかれば見積書をお出しします。1営業日以内に、宛名入りの見積書PDFをメールでお送りします。')
            + header('contact.html') + f'''<main id="main">
<div class="wrap ph-head stack s-48" id="top"><nav aria-label="パンくず"><ol class="crumb"><li><a href="index.html">トップ</a></li><li aria-current="page">お問い合わせ・お見積</li></ol></nav>
{lab('Contact')}<h1 class="t-h1">見積書をお送りします</h1><p class="t-lead">{mk('必須の4項目だけ')}で送信できます。1営業日以内に、宛名入りの見積書PDFをメールでお送りします。</p></div>
<div class="wrap g75">
{quote_form('c', prefill=True, full=True)}
<aside class="stack s-48" aria-label="補足">
<section class="stack" id="flow"><h2 class="sub">送信したあとの流れ</h2><ol class="steps">{fl}</ol></section>
<section class="stack" id="sample"><h2 class="sub">届く見積書の見本</h2>{doc}</section>
<section id="consult" class="boxd stack"><h2 class="t-h2s">まだ何も決まっていない方へ</h2><p class="t-note">15分のオンライン相談で、iPhoneで足りるかどうかから一緒にお話しします。</p>{btn('相談の日時を選ぶ', '#consult')}</section>
<section id="tel" class="stack s-16"><h2 class="sub">お電話でも受け付けています</h2><p class="t-ct">［電話番号］</p><p class="t-note t-sub">［受付時間］</p></section>
<blockquote class="boxw stack"><p class="t-body">［担当者の声を1件。頼む前の不安に触れているもの］</p><footer class="t-note t-sub">［所属・役職］</footer></blockquote>
</aside></div>
</main>''' + footer('contact.html'))

def thanks():
    flow = [('いまここ', '見積のご依頼を受け付けました'), ('1営業日以内', '見積書PDFがメールで届きます'), ('そのあと', '必要に応じて30分の打ち合わせを行い、ご発注後に会場を下見します')]
    fl = ''.join(f'<li{" class=\"now\"" if i == 0 else ""}><span class="a">{a}</span><span class="b">{b}</span></li>' for i, (a, b) in enumerate(flow))
    return (head(f'送信が完了しました｜{NAME}', 'お見積のご依頼を受け付けました。')
            + header('thanks.html') + f'''<main id="main">
<p class="form-msg" style="text-align:center">これは送信完了ページの見本です。フォームの送信先がまだ設定されていないため、実際には何も送信されていません。</p>
<div class="wrap ph-head stack s-48">{lab('送信完了')}<h1 class="t-h1">ご依頼を受け付けました</h1>
<p class="t-lead">1営業日以内に、宛名入りの見積書PDFをメールでお送りします。確認メールが届かない場合は、［電話番号］までご連絡ください。</p>
<ol class="flow">{fl}</ol></div>
<section class="bandg sec-2" aria-labelledby="dl-title"><div class="wrap pad-band stack s-48"><h2 class="t-h2" id="dl-title">お待ちいただく間に、<br>稟議の準備にお使いください</h2>
<p class="t-lead">上司への説明や相見積にそのまま使える書類です。どれも登録なしでダウンロードできます。</p>
<ul class="stack s-16"><li>{btn('仕様書のひな形（Word）［ファイル準備中］', 'thanks.html', 'line')}</li><li>{btn('料金表と見積書見本（PDF）［ファイル準備中］', 'thanks.html', 'line')}</li><li>{btn('当日のチェックリスト（PDF）［ファイル準備中］', 'thanks.html', 'line')}</li></ul></div></section>
<div class="wrap sec-3"><a class="tlink" href="index.html">トップページへ戻る{go()}</a></div>
</main>''' + footer('thanks.html'))

def rules():
    sub = rules.sub = [('rules-top', 'このページについて'), ('layout', '画面の組み方'), ('type', '文字の大きさと字間'), ('color', '色の役割'), ('marks', '目印と影'), ('motion', '動きの決まり'), ('platform', '使っているWeb標準')]
    css = (HERE / 'site.css').read_text(encoding='utf-8')
    apis = [
        ('&lt;dialog&gt;（showModal）', 'Widely', 'スマホのメニュー。フォーカスを閉じ込め、Esc で閉じる', '— （JS が動かないときは、ヘッダーの「メニュー」がフッターのメニューへ移動）'),
        ('&lt;details open&gt; / &lt;summary&gt;', 'Widely', 'よくある質問。最初から開いておき、読み終えたものを閉じられる', '—'),
        (':has()', 'Widely', 'カメラの切り替え（ラジオの選択で写真を出し分け）、診断の選択肢の色', '—'),
        ('コンテナクエリ（size）', 'Widely', '診断の選択肢を、箱の幅で1列／2列に。事例とスタッフの並び', '—'),
        ('CSS のネスト、@layer、色の混色 color-mix()', 'Widely', 'CSS の書き方', '—'),
        (':user-invalid と required / type=email', 'Widely', '入力の誤りを、触ったあとだけ赤く表示', '—'),
        ('IntersectionObserver', 'Widely', 'カメラの自動送りを、見えているときだけ動かす', '—'),
        ('popover', 'Newly（2025-01）', '「?」で開く補足（マイク5本の理由など）', '未対応では、補足を本文の下に注記として表示し「?」を隠す'),
        ('アンカー配置（anchor positioning）', 'Newly（2026-01）', '補足を「?」の真上に出す', '未対応では、画面の中央に出す'),
        ('@starting-style / transition-behavior', 'Newly（2024-08）', 'メニューと補足が開くときの動き', '未対応では、動きなしで開く'),
        ('スクロール連動アニメーション', 'Limited', '見出しや写真が、スクロールに合わせて現れる', '未対応では、最初から表示'),
        ('word-break: auto-phrase', 'Limited', '見出しを文節で改行', '未対応では、通常の折り返し'),
    ]
    tr = ''.join(f'<tr><th scope="row">{a}</th><td data-l="Baseline">{b}</td><td data-l="使っている場所">{c}</td><td data-l="使えないとき">{d}</td></tr>' for a, b, c, d in apis)
    # 色見本は、ただ1つの元（design/karura-tokens.css）から読む
    kcss = TOKENS.read_text(encoding='utf-8')
    kmap = {'bg': 'bg', 'paper': 'paper', 'cream': 'cream', 'wash': 'wash', 'ink': 'ink', 'ink-strong': 'ink-2', 'line': 'sand', 'sub': 'sub',
            'teal': 'teal', 'coral': 'coral', 'yellow': 'yellow', 'marker': 'marker'}
    tokens = [(kmap[k], v) for k, v in re.findall(r'--k-([a-z-]+): (#[0-9a-f]{6});', kcss) if k in kmap]
    assert len(tokens) == len(kmap), '色見本のトークンが足りません'
    names = {'bg': '地：ページの背景（白）', 'paper': '紙：白い地に置く箱、フォーム', 'cream': 'クリーム：帯、囲み', 'wash': '淡いティール：帯', 'ink': '文字：見出し・本文、フッター', 'ink-2': '濃い文字：強調', 'sand': '罫線', 'sand-d': '補足の線', 'sub': '補足の文字（黒50%）', 'red': '配信中・必須の印（珊瑚）', 'teal': 'ティール（主色）：目次の現在地・ボタン・診断・アイコン', 'teal-ink': 'ティール：地の上の文字', 'coral': '珊瑚：見積に進む・Q・番号', 'coral-ink': '珊瑚：見積に進むボタン', 'yellow': '黄：プラン診断・アイコン', 'marker': 'マーカー：要点の下線'}
    sw = ''.join(f'<li class="stack s-16"><span style="display:block;block-size:4rem;border-radius:6px;background:{v};box-shadow:inset 0 0 0 1px rgb(0 0 0 / .08)"></span><span class="t-note"><b>{v.upper()}</b><br>{names[k]}</span></li>' for k, v in tokens)
    type_rows = [('大見出し', '26 → 50', 'カメラ5台はいりません。'), ('セクション見出し', '26 → 44', '事例を公開しています'), ('囲みの見出し', '18 → 28', '日程と会場だけ'),
                 ('小見出し', '18 → 26', '持ち込む機材の内訳'), ('カードの題・質問', '16 → 20', '登壇者は何人ですか'), ('リード', '14 → 18', '登壇者を迎え、進行を見守る。'),
                 ('本文', '14 → 16', 'マイク音声を直接取り込みます。'), ('補足', '12 → 14', '相見積にそのまま使えます')]
    ty = ''.join(f'<tr><th scope="row">{a}</th><td data-l="大きさ（px）">{b}</td><td data-l="見本">{c}</td></tr>' for a, b, c in type_rows)
    return (head(f'デザインルール｜{NAME}', 'カルラライブのサイトのデザインルールと、使っている Web 標準の一覧です。')
            + header('rules.html') + f'''<main id="main"><div class="wrap ph-head stack s-48" id="rules-top">{lab('Design rules')}<h1 class="t-h1">白い地に、<br>ティールで道しるべを置く。</h1>
<p class="t-lead">C案を元に、スマホを基本に組み直したサイトのルールです。色・影・目印は recruit.handy.school の仕組みを参考にしています。文字と余白は、幅390pxのスマホから1200pxのPCまで、段差なく大きくなります。</p></div>
<section class="sec-3" id="layout"><div class="wrap g57"><div class="stk">{lab('Layout')}</div><div class="stack s-48"><h2 class="t-h2">スマホは1段、PCは左のレール＋1段</h2>
<ul class="rows"><li>スマホを基本に書き、幅1024px以上で広げます</li><li>PCは左に幅200pxの固定レールを置きます。上からロゴ、メニュー（7項目まで。単語ではなく「何が書いてあるか」がわかる言葉で）、2つの行動（黄＝8問でプラン診断、珊瑚＝見積を依頼する。どちらもアイコンつき）、ページの切り替え。トップの中の項目には現在地が付き、右端の細い線がページを読み進めた量です</li><li>スマホでは上のバーとメニューの横並びが一緒に追従し、下部に追従ボタン（プラン診断／見積を依頼する）を置きます。メニューの中身はPCのレールと同じです</li><li>本文はレールの右で1段。セクションの頭にタグ・見出し・リードを置き、その下に中身を置きます。左に見出しだけの列を作りません</li><li>トップに置くのは、メインビジュアル、費用の内訳、料金プラン、オプション、対応事例、よくある質問まで。当日の体制、受付と道具、コーチング、発注の手続きは下層のページに分けます</li><li>プラン診断はページに埋め込まず、どのページのどこからでもボタンでモーダル（dialog）を開きます。スマホでは全画面、PCでは画面の中央に出ます。JSが動かないときは、ページの下に置いた診断へ移動します</li></ul></div></div></section>
<section class="sec-3" id="type"><div class="wrap g57"><div class="stk">{lab('Type')}</div><div class="stack s-48"><h2 class="t-h2">1書体、1つの太さ</h2>
<table class="tbl"><thead><tr><th scope="col">役割</th><th scope="col">大きさ（px、スマホ → PC）</th><th scope="col">見本</th></tr></thead><tbody>{ty}</tbody></table>
<p class="t-note t-sub">和文：Zen Kaku Gothic New の Medium（使う文字だけに絞って同梱）／英字・数字：Helvetica Neue。入力欄の文字はスマホでも16px。字間は大きさの2%、本文とリードの行送りは1.8、見出しは1.45。</p></div></div></section>
<section class="sec-3" id="color"><div class="wrap g57"><div class="stk">{lab('Color')}</div><div class="stack s-48"><h2 class="t-h2">白の地に、主色のティール</h2>
<ul class="logos" style="grid-template-columns:repeat(auto-fill,minmax(9rem,1fr))">{sw}</ul>
<ul class="rows"><li>主色はティール。目次の現在地、見出しのタグ、アイコンの四角、一覧の見出しの下線、手順の番号、診断で選んだ答え、プラン名の帯、そのほかの行動のボタンに使います</li>
<li>珊瑚は「見積を依頼する」だけ：見積に進むボタン（どこにあっても同じ色）。ほかに、よくある質問のQと、送信後の流れの「いまここ」</li>
<li>黄（#FACA00）は「プラン診断をはじめる」だけ：左レール、スマホの入口、下部の追従ボタン、メニューの中。ほかの場所では使いません。要点のマーカーは別の淡い黄（#FFEB78）で、本文の要点だけに引きます</li>
<li>同じ意味のボタンは同じ色：黄＝プラン診断をはじめる、珊瑚＝見積を依頼する、ティール＝そのほかの行動（次へ、相談する、ひな形を受け取る）、線だけ＝資料や補助</li>
<li>地は白。セクションの面はクリーム（#F8F6F3）とティールの淡い色（#F2FBFC）の2つだけで、どちらも参考サイトの半透明の色を白に重ねた値です</li>
<li>差し色は小さな面にだけ使い、大きな面は白・クリーム・淡いティールのまま。ボタンやラベルの四角は参考サイトどおり、差し色の上に白い文字を乗せます</li>
<li>キーボードで操作しているときの枠は濃い文字色（#333333）。暗い面の上では白</li>
<li>色・影・角丸・文字・動きの値は、design/karura-tokens.css の1つのファイルが元です。このサイトと、進行管理の「タイムキーパー」・質疑応答の「FAQ」（紹介ページ・管理画面・閲覧画面）が同じファイルを読むので、そこを直せば全体に反映されます</li></ul></div></div></section>
<section class="sec-3" id="marks"><div class="wrap g57"><div class="stk">{lab('Marks &amp; Shadow')}</div><div class="stack s-48"><h2 class="t-h2">目が滑らないための目印</h2>
<p class="t-lead">長いページでも読む場所を見失わないよう、4つの目印を決まった場所にだけ置きます。</p>
<ul class="reasons">
<li class="reason">{ico('check')}<div class="stack s-16"><h3 class="t-ct">{mk('要点のマーカー')}</h3><p class="t-body">各セクションのリードで、いちばん伝えたい一文にだけ引きます。1つのセクションに1か所まで。文字の下半分を黄色（#FFEB78）にし、画面に入ったときに左から引かれます</p></div></li>
<li class="reason">{ico('doc')}<div class="stack s-16"><h3 class="t-ct">影は重ねない</h3><p class="t-body">影が付くのは、いちばん外側の面だけ。影の付いた面の中に置くものは、線で区切ります。ボタンには影を付けません。強さは2つ：置いてあるもの（カード、白い箱、左レール）は 0 0 30px 黒8%、物として見せるもの（見積書の見本、暗い囲み）は 0 5px 40px 黒20%</p></div></li>
<li class="reason">{ico('switch')}<div class="stack s-16"><h3 class="t-ct">見出しのタグと、章の切れ目</h3><p class="t-body">各章の頭に、目次と同じ言葉のタグ（白地にティールの線の丸い札）を付けます。スマホでは、章の頭に端から端までティールの線を引き、その線の上にタグを乗せて切れ目を示します。線画のアイコンはティールの角丸の四角（44px、角丸10px）に入れ、飾りなので読み上げからは外します</p></div></li>
<li class="reason">{ico('backup')}<div class="stack s-16"><h3 class="t-ct">QとA</h3><p class="t-body">よくある質問は珊瑚のQとティールのA。読む前に、問いと答えの区別がつくようにします</p></div></li>
</ul>
<p class="t-note t-sub">穴埋め（［ ］）はマーカーと見分けがつくよう、灰色の斜線にしています。</p></div></div></section>
<section class="sec-3" id="motion"><div class="wrap g57"><div class="stk">{lab('Motion')}</div><div class="stack s-48"><h2 class="t-h2">動きは、減らせる</h2>
<ul class="rows"><li>押せるものの反応は 0.3秒、cubic-bezier(0.4, 0.4, 0, 1) にそろえます</li><li>要点のマーカーは 0.8秒で引きます。幕や出現の動きは cubic-bezier(0.19, 1, 0.22, 1)</li><li>読み込みの幕は、その回の最初の1回だけ。2回目からは出ません</li><li>カメラの自動切り替えには「切り替えを止める」ボタンをつけています</li><li>端末で「視差効果を減らす」を選んでいる人には、幕・自動切り替え・出現の動き・マーカーの動きをすべて止めます（マーカーは最初から引いた状態）</li></ul></div></div></section>
<section class="sec-3" id="platform"><div class="wrap g57"><div class="stk">{lab('Platform')}</div><div class="stack s-48"><h2 class="t-h2">使っている Web 標準と、使えないときの形</h2>
<p class="t-lead">基準は Baseline Widely available（主要ブラウザで30か月以上使えるもの）。それより新しい機能は、無くても見た目と操作が壊れない場所にだけ使っています。</p>
<table class="tbl"><thead><tr><th scope="col">機能</th><th scope="col">Baseline（2026年11月）</th><th scope="col">使っている場所</th><th scope="col">使えないとき</th></tr></thead><tbody>{tr}</tbody></table>
<p class="t-note t-sub">「Widely」は主要ブラウザで30か月以上、「Newly」は主要ブラウザの最新版で使えるもの、「Limited」は一部のブラウザだけ。</p></div></div></section>
</main>''' + footer('rules.html'))

PAGES = {'index.html': index, 'service.html': service, 'reception.html': reception, 'coaching.html': coaching, 'public.html': public,
         'contact.html': contact, 'thanks.html': thanks, 'rules.html': rules, 'mvs.html': mvs}
def subset_font(text):
    """ページで使っている文字だけの書体ファイルを作る（元の書体は約1MB、切り出すと数十KB）"""
    from fontTools import subset
    chars = ''.join(sorted(set(text) | {chr(i) for i in range(0x20, 0x7f)}))
    options = subset.Options(flavor='woff2', layout_features=['*'])
    font = subset.load_font(str(FONT_SRC), options)
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=chars)
    subsetter.subset(font)
    subset.save_font(font, str(OUT / 'assets' / 'fonts' / 'zkgn-500.woff2'), options)


if __name__ == '__main__':
    # docs/ を作り直す（生成物だけを置く）
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'assets' / 'fonts').mkdir(parents=True)
    shutil.copytree(HERE / 'img', OUT / 'img')
    for name in ('site.css', 'site.js'):
        shutil.copyfile(HERE / name, OUT / 'assets' / name)
    shutil.copyfile(TOKENS, OUT / 'assets' / 'karura-tokens.css')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')

    used = (HERE / 'site.css').read_text(encoding='utf-8') + (HERE / 'site.js').read_text(encoding='utf-8')
    for name, fn in PAGES.items():
        html = mark(tag_sections(fn(), getattr(fn, 'sub', [])))
        (OUT / name).write_text(html, encoding='utf-8')
        used += html
        print(name, len(html), 'holes', len(ANA.findall(re.sub(r'<[^>]+>', ' ', html))))
    subset_font(used)
