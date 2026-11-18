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
# 読み込むファイルの版（中身が変わると変わる）。ブラウザに古い CSS が残らないようにする
import hashlib as _h
ASSET_V = _h.sha1(b''.join(f.read_bytes() for f in (TOKENS, Path(__file__).parent / 'site.css', Path(__file__).parent / 'site.js'))).hexdigest()[:8]
# 本文の書体は Noto Sans JP（2026-11-18 決定）。元は @fontsource/noto-sans-jp の分割ファイルを、太さごとに1つにまとめたもの
FONT_SRC = {400: HERE / 'fonts' / 'NotoSansJP-400.woff2', 500: HERE / 'fonts' / 'NotoSansJP-500.woff2'}
NAME, NAME_EN = 'カルラライブ', 'KARURA LIVE'
SIZES = {f.stem: Image.open(f).size for f in (HERE / 'img').glob('*.webp')}

ANA = re.compile(r'［[^］]*］')
def mark(h):
    """タグの外にある［ ］を黄色の穴埋め表示にする"""
    return ''.join(p if p.startswith('<') else ANA.sub(lambda m: f'<span class="ana">{m.group(0)}</span>', p)
                   for p in re.split(r'(<[^>]+>)', h))

GRAY = '%23e6e6e6'  # 写真・図はすべて無地のグレーで置く（2026-11-18 決定）。本物が届いたら src/img から差し替える

def img(code, alt, cls='', lazy=True, eager_high=False):
    """写真の枠。いまは元の写真と同じ縦横比の、無地のグレー"""
    w, h = SIZES[code]
    c = f' class="{cls}"' if cls else ''
    alt = alt.replace('（ダミー）', '')
    src = f"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}'%3E%3Crect width='{w}' height='{h}' fill='{GRAY}'/%3E%3C/svg%3E"
    return f'<img{c} src="{src}" alt="{alt}" width="{w}" height="{h}">'

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
    """青の角丸チップに入った線画アイコン（飾りなので読み上げない）"""
    return (f'<span class="chipi{" chipi--" + size if size else ""}" aria-hidden="true">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg></span>')

def mk(t):
    """要点に引く淡い青のマーカー"""
    return f'<mark class="mk">{t}</mark>'

def lab(t):
    """見出しのタグ（ ● 文字 ）"""
    return f'<p class="t-lab"><span class="dot" aria-hidden="true"></span>{t}</p>'

def tag_sections(body, items):
    """各セクションの頭のタグを、目次（サブナビ）と同じ言葉にする"""
    for i, t in items:
        at = body.find(f'id="{i}"')
        if at < 0: continue
        nxt = body.find('<section', at + 1)
        m = re.compile(r'<p class="t-lab">.*?</p>').search(body, at, nxt if nxt > 0 else len(body))
        if m: body = body[:m.start()] + lab(t) + body[m.end():]
    return body

# ------------------------------------------------------------------ 共通
# メニューは7項目まで（2026-11-16 決定）。ほかに「プラン診断」と「見積を依頼する」を、どのページにも置く。
# トップの中の項目は、トップではページ内リンク（現在地つき）、ほかのページからは index.html# へ。
MENU = [('index.html#cost', 'サービス内訳'), ('index.html#price', '料金プラン'), ('index.html#works', '対応事例'),
        ('service.html', '当日の体制と流れ'), ('reception.html', '配信支援ツール'), ('coaching.html', '内製化支援')]
# 「大学・公共機関の方へ」はメニューに入れず、バナーとしてレールとメニューの下に置く（2026-11-18）
PUBLIC_BANNER = ('public.html', '大学・公共機関の方へ', '稟議・相見積・請求書払いに対応します')

def banner(page):
    h, t, sub = PUBLIC_BANNER
    cur = ' aria-current="page"' if page == h else ''
    return f'<a class="banner" href="{h}"{cur}><span class="banner-t">{t}</span><span class="banner-s">{sub}</span>{go()}</a>'

def menu_href(h, page):
    """トップにいるときは #cost のようなページ内リンクにする（現在地の計算に使う）"""
    return h[len('index.html'):] if page == 'index.html' and h.startswith('index.html#') else h

def menu_items(page, cls_a=''):
    out = ''
    for h, t in MENU:
        cur = ' aria-current="page"' if h == page else ''
        out += f'<li><a href="{menu_href(h, page)}"{cur}>{t}</a></li>'
    return out

LOGO_MARK = ('<svg class="logo-mark" viewBox="0 0 32 32" aria-hidden="true" focusable="false"><rect width="32" height="32" rx="7" fill="#385ea7"/>'
             '<circle cx="16" cy="16" r="5.5" fill="#fff"/><circle cx="16" cy="16" r="10" fill="none" stroke="#fff" stroke-width="1.6" opacity=".55"/></svg>')

def logo_html():
    # #34 ヘッダーのロゴは文字だけ（マークは使わない。ファビコンには残す）
    return f'<span class="logo-t">{NAME_EN}<small>{NAME}</small></span>'

BICON = {
    'diag': '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 3h6v3H9zM8.5 13.5l2.5 2.5 4.5-5"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5 12 13l8.5-6.5"/>',
    'arrow': '<path d="M5 12h13M13 6.5 18.5 12 13 17.5"/>',
    'person': '<circle cx="12" cy="8.5" r="3.5"/><path d="M5 20c.8-4 3.8-6 7-6s6.2 2 7 6"/>',
}
def bico(name):
    """ボタンの頭に付ける線画アイコン（飾りなので読み上げない）"""
    return (f'<svg class="bico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true" focusable="false">{BICON[name]}</svg>')

def go():
    """別の節やページへ移るリンクの印（下線の代わりの、背景なしのグレーの矢印）"""
    return f'<span class="go">{bico("arrow")}</span>'

def diag_btn(text='プラン診断をはじめる', cls=''):
    """どこからでもプラン診断のモーダルを開くボタン。JS が動かないときは、ページ下に置いた診断へ移動するリンク"""
    return f'<a class="btn plan {cls}" href="#diag" data-open-diag aria-haspopup="dialog">{bico("diag")}<span>{text}</span></a>'

def quote_btn(text='見積を依頼する', cls=''):
    return f'<a class="btn quote {cls}" href="contact.html">{bico("mail")}<span>{text}</span></a>'

def sec(sid, tag, title, body, lead='', tone=''):
    """1段のセクション。上にタグ・見出し・リード、その下に中身。tone：''＝白、'band'＝淡い青、'bandg'＝クリーム"""
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
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23385ea7'/%3E%3Ccircle cx='16' cy='16' r='5' fill='%23ffffff'/%3E%3C/svg%3E">
<script>document.documentElement.classList.add('js');{intro}</script>
<link rel="preload" href="assets/fonts/noto-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/karura-tokens.css?v={ASSET_V}">
<link rel="stylesheet" href="assets/site.css?v={ASSET_V}">
<script type="module" src="assets/site.js?v={ASSET_V}"></script>{extra}
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
<a class="logo" href="index.html" aria-label="{NAME} トップページ">{logo_html()}</a>
<button type="button" class="menu-btn" data-open-menu aria-haspopup="dialog" aria-controls="menu"><span class="vh">メニューを開く</span><i></i><i></i></button>
<a class="menu-fallback t-note" href="#fnav">メニュー</a>
</div>
<nav class="subnav" aria-label="メニュー"><ol>{menu_items(page)}</ol></nav>
<div class="rail-foot">
{banner(page)}
<a class="tile tile--plan" href="#diag" data-open-diag aria-haspopup="dialog">{bico("diag")}8問でプラン診断</a>
<a class="tile tile--quote" href="contact.html">{bico("mail")}見積を依頼する</a>
<nav aria-label="ページ"><ul class="rail-pages">{pg}</ul></nav>
</div>
</header>
<dialog id="menu" class="menu" aria-label="メニュー">
<div class="menu-head"><span class="logo">{logo_html()}</span><form method="dialog"><button class="menu-close">閉じる</button></form></div>
<nav aria-label="メニュー"><ul>{items}<li><a href="index.html#faq">よくある質問<span aria-hidden="true">›</span></a></li><li><a href="contact.html">お問い合わせ・お見積<span aria-hidden="true">›</span></a></li></ul>
{banner(page)}
<div class="stack s-16 menu-acts">{diag_btn("8問でプランを診断する", "full")}{quote_btn("見積を依頼する", "full")}</div></nav>
</dialog>
'''

def footer(page, form=False):
    contact = ''
    if form:
        contact = f'''<section id="contact" class="boxg stack s-48" aria-labelledby="contact-title" style="color:var(--ink)">
<div class="contact-1col stack s-48">
<div class="stack">{lab('見積を依頼する')}<h2 id="contact-title" class="t-h2">日程と会場だけ、<br>教えてください</h2>
<p class="t-lead">{mk('1営業日以内に、宛名入りの見積書PDF')}をメールでお送りします。詳しい内容は、その後のやりとりで詰めていきます。</p>
<p class="t-note">［年度末（2〜3月）の空き日程：残り〇日］</p>
<p class="t-note" id="tel">お電話でも受け付けています　［電話番号］　［受付時間］</p></div>
{quote_form('f')}
</div></section>'''
    links = MENU + [PUBLIC_BANNER[:2], ('index.html#option', 'オプション'), ('index.html#faq', 'よくある質問'), ('contact.html', 'お問い合わせ・お見積'), ('rules.html', 'デザインルール')]
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
           + fld('venue', '会場', '例：〇〇会館 △△ホール', err='会場を入力してください')
           + fld('size', '登壇者と来場者のおおよその人数', '例：登壇4人、来場150人', err='おおよその人数を入力してください')
           + fld('email', 'メールアドレス', 'name@example.ac.jp', 'email', err='メールアドレスの形で入力してください（例：name@example.ac.jp）'))
    opt = ''
    if full:
        plans = ''.join(f'<label><input type="checkbox" name="plan" value="{v}">{v}</label>' for v in ['スタンダード（25万円）', 'ワイド（35万円）', 'オーダー（ロケ配信・台本制作など）', '内製化支援', 'まだわからない'])
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
    ('pub', '録画を公開する予定や、外部の視聴者・来賓はありますか', 'どちらかに当てはまれば「ある」', [('y', 'ある'), ('n', 'ない')]),
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
            ('予備回線', 'オプション', '会場の回線が切れても、配信を続けます')]
    tr = ''.join(f'<tr><td class="k">{a}</td><td class="k" data-l="数">{c}</td><td data-l="用途">{d}</td></tr>' for a, c, d in rows)
    return f'<table class="tbl"><caption class="vh">持ち込む機材（スタンダード）</caption><thead><tr><th scope="col">種類</th><th scope="col">数</th><th scope="col">用途</th></tr></thead><tbody>{tr}</tbody></table>'

def option_list():
    """オプション。編集と記録撮影は写真つきのカードで目立たせ、残りは意味ごとにまとめて名前と料金だけ並べる"""
    feature = [('P13', '記録撮影', [('記録写真（専任のカメラマン）', '［金額］')], '数枚の記録撮影は、基本プランで対応できます'),
               ('P14', '編集', [('記録映像の編集（字幕つき）', '［金額］'), ('2分のダイジェスト映像', '［金額］')], '')]
    groups = [('体制を足す', [('スタッフの追加', '［金額］'), ('カメラとカメラマンの追加（5台目から）', '［金額］'), ('配信時間の延長（1時間ごと）', '［金額］')]),
              ('回線と下見', [('予備回線', '［金額］'), ('回線の持ち込み', '［金額］'), ('ロケハン（実地の下見）', '［金額］')]),
              ('納品と受付', [('録画データの納品', '［金額］'), ('文字起こし', '［金額］'), ('LINEで申し込む受付', '［金額］')]),
              ('交通と宿泊', [('交通費・前入りの宿泊費', '別途お見積り')])]
    def yen(v):
        return v if v == '別途お見積り' else f'<span class="yen"><b>{v}</b><small>円</small><span class="tax">（税別）</span></span>'
    def name(n):
        main, _, note = n.partition('（')
        return f'{main}<small>{note[:-1]}</small>' if note else main
    rows = lambda xs: '<ul class="opt-rows">' + ''.join(f'<li><span class="n">{name(n)}</span><span class="r">{yen(v)}</span></li>' for n, v in xs) + '</ul>'
    fc = ''.join(f'''<li class="opt-card"><div class="zoom">{img(pid, f'（ダミー）{t}の写真')}</div><div class="stack s-16"><h3 class="t-h3">{t}</h3>{rows(xs)}{f'<p class="t-note t-sub">{n}</p>' if n else ''}</div></li>''' for pid, t, xs, n in feature)
    gc = ''.join(f'<li class="opt-group"><h3 class="sub">{g}</h3>{rows(xs)}</li>' for g, xs in groups)
    return f'<ul class="opt-cards">{fc}</ul><ul class="opt-groups">{gc}</ul>'

def tbl_plans():
    """プランの違いだけを並べる表。どのプランにも含まれるものは、表の下に1回だけ書く（COMMON）。スマホでは横にスクロール"""
    Y = '<span class="yes" role="img" aria-label="含む">○</span>'
    N = '<span class="no" role="img" aria-label="含まない">—</span>'
    rows = [('料金（税別）', '<b class="cmp-price">250,000<small>円〜</small></b>', '<b class="cmp-price">350,000<small>円〜</small></b>', '<b class="cmp-price">ASK</b>'),
            ('向いている会', '登壇者2〜6人<br>会場50〜300人', '登壇者7人以上<br>会場300人を超える', '会場の外からの中継<br>複数の会場・複数日'),
            ('スタッフ', '3人', '4人', '内容に合わせて'),
            ('カメラ', '3台', '5台', '内容に合わせて'),
            ('マイクの持ち込み', f'5本まで{tip("tip-mic", "マイクが5本の理由", "登壇者4人分と、会場の質問用1本です。6本以上必要な会は、スタッフを1人追加します。")}', '［本数］まで', '内容に合わせて'),
            ('配信の時間／会場での作業', f'3時間／6時間まで{tip("tip-time", "作業時間の内訳", "設営2時間、配信3時間、撤収1時間が目安です。")}', '［時間］', '内容に合わせて'),
            ('オンラインからの登壇', 'スタッフ1人の追加で対応', Y, Y),
            ('ロケ配信（会場の外からの中継）', N, N, Y),
            ('進行台本の制作', N, N, Y)]
    tr = ''.join(f'<tr><th scope="row">{a}</th><td class="is-main">{b}</td><td>{c}</td><td class="is-ask">{d}</td></tr>' for a, b, c, d in rows)
    return (f'<div class="cmp-wrap" tabindex="0" role="region" aria-label="プランの違い（横にスクロールできます）"><table class="cmp"><caption class="vh">プランの違い</caption>'
            f'<thead><tr><td></td><th scope="col" class="is-main"><span class="cmp-badge">基本のプラン</span>スタンダード</th><th scope="col">ワイド</th><th scope="col" class="is-ask">オーダー</th></tr></thead><tbody>{tr}</tbody></table></div>')

PRECHECK = [('Zoomでのオンライン下見', '会場をスマホで映していただき、カメラとマイクを置く場所、電源、客席からの見え方を一緒に確かめます'),
            ('回線の診断', '会場のインターネット回線が、配信に足りる速さと安定さかを確かめます'),
            ('会場診断ツール', '会場でスマホやPCから開くだけで、回線の速さと安定さを測れるツールをお渡しします［準備中］')]

COMMON = ['事前の打ち合わせ', '会場のオンライン下見（実地のロケハンはオプション）', '予備の録画機（録画は2系統）', '受付用のデジタルチケット（来場300人まで）']

def tip(tid, label, body):
    """「?」で開く補足。popover 未対応では、本文の下に注記として出る"""
    return (f'<span class="tip"><button type="button" class="tip-btn" popovertarget="{tid}" aria-label="{label}" style="anchor-name:--{tid}">?</button>'
            f'<span id="{tid}" popover class="tip-body" style="position-anchor:--{tid}">{body}</span></span>')

def case(n, photo, alt, size_note=''):
    """事例のカード（横スクロールの1枚）。どの事例も同じ項目で並べる"""
    return f'''<li class="case-card stack s-16"><div class="zoom">{img(photo, alt)}</div>
<p class="t-note t-sub">事例 {n}　|　［主催機関名］</p>
<div class="case-tags"><span class="pill">［主催の種類］</span><span class="pill">［シンポジウム］</span></div>
<h3 class="t-ct">［会の名称：課題と成果を一文で］</h3>
<p class="t-body">［当日起きたことと、どう戻したか。2〜3行］</p>
<dl class="chips"><div class="chip"><dt>会の規模</dt><dd>登壇［ ］人、会場［ ］人</dd></div><div class="chip"><dt>当日の体制</dt><dd>スタッフ［ ］人{size_note}</dd></div>
<div class="chip"><dt>使用機材</dt><dd>カメラ［ ］台、マイク［ ］本</dd></div><div class="chip"><dt>金額</dt><dd>［25万〜35万円］</dd></div></dl></li>'''

FAQ = [
    ('何日前までに頼めば間に合いますか', '［最短の日数と、繁忙期の目安］'),
    ('Zoom、YouTube、Teamsのどれに対応していますか', '［対応している配信先］'),
    ('登壇者の一部がオンラインから参加します', '対応できます。スタッフを1人追加します（［金額］）。'),
    ('会場にインターネット回線がありません', '配信用の回線を持ち込みます（［金額］）。事前に会場で電波状況を確認します。'),
    ('配信が止まった場合、料金はどうなりますか', '［返金・減額の規定］'),
    ('対応エリアはどこまでですか', '新宿駅からおおむね90分以内で伺える会場が対応エリアです。エリア外の会場もご相談ください。交通費と、前入りが必要な場合の宿泊費は、どの会場でも別途お見積りします。'),
    ('登壇者が1人の講演や、30人ほどの勉強会でも頼めますか', 'お受けします。ただ、カメラ1台とお手持ちのiPhoneやPCで十分に伝わる会でもあります。<a href="#diag" data-open-diag>8問のプラン診断</a>で、ご自身で配信できるかどうかを確かめられます。'),
    ('屋外や複数の会場からの中継、同時通訳はできますか', 'オーダーでお見積りします。会場の下見をしてから、必要な人と機材をご提案します。'),
    ('依頼する前に、その会場で配信できるか確かめられますか', '確かめられます。Zoomでのオンライン下見と回線の診断を、無料で行います。会場で開くだけで回線を測れる会場診断ツールもお渡しします（［準備中］）。'),
    ('毎月のセミナーなど、定期的な配信の割引はありますか', 'あります。回数に応じて割引します。年間の予定がわかれば、まとめてお見積りします。'),
    ('参加者の受付や名簿の管理もお願いできますか', '対応できます。どのプランにも受付用のデジタルチケットが含まれます。申込の受付、当日の入場、終了後の来場者数の報告までを引き受けます。詳しくは<a href="reception.html">配信支援ツール</a>をご覧ください。'),
    ('有料の会のチケット販売はできますか', '販売と決済は行っていません。参加費がある会は、お使いのチケット販売サービスや請求書で集金いただき、申込者の名簿（CSV）をお預かりして、当日の入場だけを引き受けます。'),
    ('参加者の個人情報は、どう扱いますか', '名簿は受付と報告のためだけに使い、会の終了から30日で自動的に削除します。委託契約書や情報セキュリティのチェックシートが必要な場合は、ご相談ください。'),
    ('相見積のための見積依頼でもかまいませんか', '歓迎します。<a href="public.html#spec">仕様書のひな形</a>と見積書の見本もお送りしますので、他社への依頼にもそのままお使いください。'),
    ('支払い方法を教えてください', '請求書払い（後払い）に対応しています。見積書・納品書・請求書の3点を発行します。'),
]

# ------------------------------------------------------------------ メインビジュアル（リードと箇条書きは3案を比べる。採用中は MV_USE）
# 箇条書きは、それぞれの中身が書いてある場所へのリンクにする（href はトップから見た場所。ほかのページでは index.html を付ける）
MV_KIND = 'シンポジウム・講演会・セミナーのライブ配信／ハイブリッド配信（会場＋オンライン）'
MV = {
    'A': {'name': '案A：必要なぶんだけ',
          'h1': '必要なぶんの機材と人で、<br>会場とオンラインに届けます。',
          'lead': 'シンポジウムと講演会を、ハイブリッドで配信します。',
          'kind': 'list',
          'items': [('カメラ3台・スタッフ3人・マイク5本で、25万円（税別）から', '#price'), ('見積書に、スタッフの役割と機材の内訳をすべて書きます', '#cost'),
                    ('カメラ1台で足りる会なら、そうお伝えします', '#faq')]},
    'B': {'name': '案B：見積の中身から',
          'h1': '配信の見積を、<br>中身から読めるものに。',
          'lead': '誰が来て、何を持ち込み、何時間いるか。見積書にすべて書きます。',
          'kind': 'list',
          'items': [('スタンダード 25万円：カメラ3台・スタッフ3人', '#price'), ('ワイド 35万円：カメラ5台・スタッフ4人', '#price'),
                    ('オプションの料金も、表で公開しています', '#option')]},
    'C': {'name': '案C：いまの見出し＋対象・体制・費用',
          'h1': 'ここにメインコピーが入ります。<br>2行ほどのダミーテキストです。',
          'lead': '配信規模に合った体制で、会場の様子をそのままオンラインに届けます。',
          'kind': 'facts',
          'items': [('対象', '登壇者2〜6人、会場50〜300人のシンポジウム・講演会', '#works'), ('体制', 'カメラ3台、スタッフ3人、マイク5本まで', 'service.html#team'),
                    ('費用', '25万円（税別）から。内訳はすべて見積書に書きます', '#price')]},
}
MV['D'] = {'name': '案D：大手と個人の間',
           'h1': '大手は大げさ。個人は不安。<br>その間の配信代行です。',
           'lead': 'シンポジウムと講演会を、会の大きさに合った体制でハイブリッド配信します。',
           'kind': 'facts', 'items': MV['C']['items']}
MV_USE = 'C'

def mv(key, page='index.html', tag='h1', hid='mv-title'):
    """写真の上には、種類・見出し・リードだけを重ねる。写真の下の縁に、プラン診断のバッジを半分かけて置く（箇条書きは置かない）。
       写真はまだ穴埋め（ダミーの会場写真を暗くして敷いている）"""
    v = MV[key]
    return f'''<section class="mv" aria-labelledby="{hid}"><div class="mv-bg">{img('P03', '', lazy=False, eager_high=True)}</div>
<div class="wrap mv-in"><div class="mv-copy stack">
<p class="hero-kind">{MV_KIND}</p>
<{tag} class="t-h1" id="{hid}">{v['h1']}</{tag}>
<p class="t-lead">{v['lead']}</p>
</div></div></section>
<div class="wrap mv-after"><a class="badge" href="#diag" data-open-diag aria-haspopup="dialog"><span class="badge-sh" aria-hidden="true"><span class="badge-bg"></span></span><span class="badge-t"><span class="badge-emoji" aria-hidden="true">📋</span>8問で<br>プラン診断</span></a></div>'''

# ------------------------------------------------------------------ トップ
def index():
    intro = '<div class="intro" aria-hidden="true"><p>' + ''.join(f'<span style="--i:{i}">{c}</span>' for i, c in enumerate(NAME_EN)) + '</p></div>'
    hero = mv(MV_USE)
    voices = [('総務・広報のご担当', '今年からシンポジウムをハイブリッドで、と言われました。Zoomで足りるのかも分からないし、失敗したら自分の責任です。大手の見積は桁が違いました。', '#price', '料金プランは、すべて公開しています'),
              ('イベントを主催するご担当', 'セミナーの企画と運営は自分たちでできます。配信だけを切り出して頼みたい。でも当日、誰が来て何をするのかは先に知っておきたいです。', 'service.html#team', '当日のスタッフ表を、見積と一緒にお渡しします'),
              ('式典や記念の会のご担当', '来賓も関係者も見ている、やり直しのきかない会です。「大丈夫です」ではなく、何がどう大丈夫なのかを説明できないと、決裁が通りません。', 'service.html#trouble', '起きがちなトラブルと、その予防を書いています')]
    vc = ''.join(f'<li class="voice"><blockquote class="voice-q"><p>{q}</p></blockquote><p class="voice-who t-note t-sub"><span class="avatar">{bico("person")}</span>{w}</p>'
                 f'<a class="tlink" href="{h}">{t}{go()}</a></li>' for w, q, h, t in voices)
    worries = sec('worries', 'よくあるお悩み', 'こんなことで、<br>困っていませんか', f'<ul class="voices">{vc}</ul>',
                  lead='初めて配信を任された方から、よく伺うお悩みです。どれも、ご依頼の前にお答えできます。')

    kinds = [('face', 'パネルディスカッションのあるシンポジウム', '登壇者2〜6人。話す人が替わるたびに、カメラを切り替えます'),
             ('mic', '講演会・セミナー', '会場に50〜300人。会場の質問も、オンラインの視聴者に届けます'),
             ('backup', '来賓や関係者、外部の方が見る会', 'やり直しのきかない配信。予備の録画機を用意し、予備回線も付けられます'),
             ('switch', '遠隔地の講師が登壇する会', '会場とオンラインの登壇者が、同じ画面で話せるようにします')]
    shots = ['P02', 'P10', 'P03', 'P09']
    items = lambda dup: ''.join(f'<li class="cs-item" data-i="{i}"{" aria-hidden=\"true\"" if dup else ""}>{img(shots[i], "" if dup else f"（ダミー）{t}の写真")}</li>' for i, (k, t, b) in enumerate(kinds))
    caps = ''.join(f'<div class="cs-cap" data-i="{i}"{"" if i == 0 else " hidden"}>{ico(k)}<div class="stack s-16"><h4 class="t-ct">{t}</h4><p class="t-body">{b}</p></div></div>' for i, (k, t, b) in enumerate(kinds))
    kd = f'''<div class="cs" data-cs><ul class="cs-track" aria-label="ケーススタディの写真（自動で横に流れます）">{items(False)}{items(True)}</ul></div>
<div class="cs-foot"><div class="cs-caps">{caps}</div><div class="cs-ctl"><p class="t-note cs-count"><span data-cs-now>1</span> / {len(kinds)}</p>
<button class="cs-pause" type="button" aria-pressed="false" data-cs-pause>止める</button></div></div>'''
    factors = [('face', '当日の人数', 'スタッフの人数。ディレクター・配信管理、カメラ・音声、2台目のカメラの3人が基本です。オンライン登壇やマイク6本以上の会では1人増えます。'),
               ('switch', '機材', 'カメラとマイクの数、予備の機材。カメラの台数は、登壇者の人数と会場の広さで決まります。'),
               ('report', 'オプション', '録画データの納品、予備回線、ロケハン、記録写真など、当日の配信のほかに頼める仕事です。必要なものだけを足します。')]
    fc = ''.join(f'<li class="reason">{ico(k)}<div class="stack s-16"><h3 class="t-ct">{t}</h3><p class="t-body">{b}</p></div></li>' for k, t, b in factors)
    lean = [('全員に持ち場があります', 'スタッフは3人。ディレクター・配信管理、カメラ・音声、2台目のカメラの持ち場に1人ずつです。持ち場のない人の費用はいただきません。'),
            ('機材は、会に合わせて選びます', '登壇者2〜6人の会にはカメラ3台。5台を持ち込むのは、登壇者が多い会や会場が広い会だけです。'),
            ('予備は、止まると取り返しがつかないものだけ', '録画機は2系統。予備回線はオプションで付けられます。'),
            ('見積書にすべて書きます', '人・機材・オプションの内訳を明記します。あとから増えるのは、オプションの一覧にあるものだけです。')]
    ln = ''.join(f'<li><span class="a">{a}</span><span class="b">{b}</span></li>' for a, b in lean)
    cost = sec('cost', 'サービス内訳', '配信の費用は、<br>人と機材とオプションで決まります', f'''<div class="stack"><h3 class="sub">ケーススタディ</h3>{kd}</div>
<div class="stack"><h3 class="sub">費用を決める3つ</h3><ul class="reasons reasons--3">{fc}</ul></div>
<div class="boxc stack s-48"><div class="stack s-16">{lab('コラム')}<h3 class="t-h2s">無駄のない配信とは</h3>
<p class="t-body">引っ越しと同じです。単身の荷物に10トントラックはいりませんが、冷蔵庫を友人の軽トラックで運ぶのは不安です。配信も、会の大きさに合った人と機材を選ぶのがいちばん安く、いちばん確かです。</p></div><ul class="lean">{ln}</ul></div>''',
               lead='配信代行の見積は、当日のスタッフの人数、持ち込む機材、必要なときだけ足すオプションの3つで、ほぼ決まります。カルラライブは、会の大きさに必要なぶんだけを組み合わせます。')

    price = sec('price', '料金プラン', 'シンプルな料金プラン', f'''<div class="stack">{tbl_plans()}
<p class="t-note t-sub">定期的に配信する会（毎月のセミナーなど）は、回数に応じて割引があります。交通費と、前入りが必要な場合の宿泊費は別途お見積りします。</p></div>
<div class="to-diag"><p class="t-ct">どのプランが合うか分からないときは</p><p class="t-note">登壇者の人数や会場の大きさなど、8つの質問に答えると、合うプランと費用の目安が出ます。</p>{diag_btn('8問でプラン診断')}</div>
<div class="stack"><h3 class="sub">どのプランにも含まれるもの</h3><ul class="incl">{''.join(f'<li>{ico("check", "s")}<span>{t}</span></li>' for t in COMMON)}</ul></div>
<div class="boxw stack" id="precheck"><h3 class="t-h3">ご依頼の前に、無料でできること</h3>
<ul class="incl incl--2">{''.join(f'<li>{ico("check", "s")}<span><b>{a}</b><br><span class="t-note">{b}</span></span></li>' for a, b in PRECHECK)}</ul>
<p class="t-note t-sub">見積を依頼するときに「事前の確認を希望」と書いてください。依頼しないと決めた会でも、費用はかかりません。</p></div>
<div class="btns btns--center">{quote_btn('見積を依頼する', 'lg')}</div>
<p class="t-note t-sub t-center">見積書の見本は、上司への説明や相見積にそのまま使えます。　<a class="tlink" href="contact.html#sample">見積書の見本を見る{go()}</a></p>''',
                lead=f'どのプランにも、事前の打ち合わせ、会場のオンライン下見、予備の録画機、受付用のデジタルチケットが含まれます。{mk("見積書にも同じ内容を書きます。")}', tone='bandg')

    option = sec('option', 'オプション', '必要なときだけ、足せるもの', f'''{option_list()}
<p class="t-note t-sub">料金はすべて税別です。プラン診断で選んだものは、見積のご依頼にそのまま入ります。</p>''',
                 lead='どのプランにも付けられます。見積書には1行ずつ書き、請求は配信とまとめて1回です。')

    works = f'''<section id="works" class="sec" aria-labelledby="works-title"><div class="wrap stack s-56">
<div class="sec-head stack">{lab('対応事例')}<h2 class="t-h2" id="works-title" data-rv>これまでに配信した会</h2>
<p class="t-lead">{mk('すべての事例を、人数・体制・機材・金額の同じ項目で載せています。')}ご自身の会に近いものを探してください。</p></div>
<div class="stack"><h3 class="sub">これまでに配信・記録を担当した機関</h3><p class="t-note">［配信した会の件数、継続して依頼いただいている機関の数］</p>
<ul class="logos">{''.join('<li><div class="ph" style="aspect-ratio:5/2;padding:0"></div></li>' for _ in range(6))}</ul></div>
</div>
<div class="cases-head wrap"><p class="cases-count t-note" aria-live="polite" hidden><span data-cases-now>1</span> / <span data-cases-all>4</span></p></div>
<ul class="cases" aria-label="事例の一覧（横にスクロールできます）">
{case(1, 'P02', '（ダミー）パネルディスカッション全体', '（スタッフ3人）')}
{case(2, 'P09', '（ダミー）オンライン登壇者の映る画面')}
{case(3, 'P10', '（ダミー）会場からの質問')}
{case(4, 'P03', '（ダミー）会場全体')}
</ul>
</section>'''

    fq = ''.join(f'<details open><summary><span class="qa-mk qa-mk--q" aria-hidden="true">Q</span>{q}</summary><div class="ans"><span class="qa-mk qa-mk--a" aria-hidden="true">A</span><p class="t-body">{a}</p></div></details>' for q, a in FAQ)
    faq = sec('faq', 'よくある質問', 'よくある質問', f'<div class="faq">{fq}</div>', tone='band')

    return (head(f'シンポジウム・講演会のハイブリッド配信代行｜3カメ・3人・25万円〜｜{NAME}',
                 'シンポジウム、講演会、セミナーをハイブリッドで配信します。カメラ3台・スタッフ3人・マイク5本までで25万円（税別）から。8問のプラン診断で、合うプランと費用がわかります。', home=True)
            + intro + header('index.html') + '<main id="main">' + hero + strengths() + worries + cost + price + option + works + faq + '</main>'
            + footer('index.html', form=True))

# ------------------------------------------------------------------ 強み（トップの MV のすぐ下）
def strengths():
    items = [('P05', 'doc', 'わかりやすい料金体系', 'スタッフ3人・カメラ3台・マイク5本で25万円（税別）。機材費も込みです。全員に持ち場がある、無駄のない体制で伺います。', '#price', '料金プランを見る'),
             ('P11', 'qr', 'ツールで運営費を圧縮', '配信支援ツール（受付のデジタルチケット、質疑応答、進行管理）で、当日の受付や運営に立つ人を減らせます。', 'reception.html', '配信支援ツールを見る'),
             ('P12', 'list', '配信体制と内製化', '小さな会はご自身で、大きな会は私たちに。内製化の基準づくりから、独り立ちまで並走します。', 'coaching.html', '内製化支援を見る')]
    li = ''.join(f'''<li class="reason"><div class="reason-ph zoom">{img(pid, f'（ダミー）{t}の写真')}</div>{ico(k)}<div class="stack s-16"><h3 class="t-ct">{t}</h3><p class="t-body">{b}</p>{btn(l, h, 'soft s')}</div></li>''' for pid, k, t, b, h, l in items)
    return sec('strengths', 'カルラライブの強み', '配信の費用を、<br>読めるものにします', f'<ul class="reasons reasons--3 reasons--card">{li}</ul>',
               lead='配信当日だけでなく、運営の手間と、その先の体制づくりまで支えます。')

# ------------------------------------------------------------------ 当日の体制と流れ
def service():
    staff = [('P04', 'ディレクター・配信管理', '進行の確認、画面の切り替え、配信の見守り。ご担当者との連絡もこの1人が受けます', '配信卓（会場の音響卓の隣）'),
             ('P05', 'カメラ・音声', '登壇者を撮るカメラの操作と、マイク・音量の調整、登壇者のPCの接続', '客席の後ろ、カメラの横'),
             ('P06', 'カメラ②', '2台目のカメラで、登壇者全体や会場からの質問を撮ります', '客席の横か後ろ')]
    sc = ''.join(f'''<li class="staff-card"><div class="zoom">{img(pid, f'（ダミー）{t}のスタッフ')}</div><div class="stack s-16"><h3 class="t-ct">{t}</h3><p class="t-body">{b}</p><p class="t-note">当日いる場所：{w}</p><p class="t-note t-sub">［氏名・経歴一行］</p></div></li>''' for pid, t, b, w in staff)
    team = sec('team', '当日の体制', 'スタッフ3人、<br>それぞれに持ち場があります', f'''<ul class="staff">{sc}</ul>
<p class="t-note">ワイド（35万円）では、4人目が［4人目の役割］を受け持ちます。</p>
<p class="t-body">見積書と一緒に「当日のスタッフ表」をお渡しします。来る人の名前、持ち場、当日いる場所を1枚にまとめたものです。会場の方や来賓に「あの人は何をしている人か」を聞かれても、すぐにお答えいただけます。</p>
<figure data-rv="media"><div class="ph" style="aspect-ratio:16/9"></div></figure>
<div class="stack"><h3 class="t-h3">持ち込む機材（スタンダード）</h3>{tbl_gear()}</div>''',
               lead='ディレクター・配信管理、カメラ・音声、2台目のカメラ。3つの持ち場に1人ずつで伺います。どれも本番中ずっと手を動かす仕事です。人数を増やして見積を大きくすることはしません。')

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
               ('万が一に備える予備機材', '録画機は2系統。予備回線（オプション）を付ければ、会場の回線が切れても配信を続けられます。')]
    marks = ['mic', 'face', 'switch', 'backup']
    rs = ''.join(f'<li class="reason">{ico(marks[i - 1])}<div class="stack s-16"><h3 class="t-ct"><span class="t-num">0{i}</span>{t}</h3><p class="t-body">{b}</p></div></li>' for i, (t, b) in enumerate(reasons, 1))
    day = sec('day', '当日の流れ', '当日、ご担当者は配信に<br>かかりきりにならずに済みます', f'''<ul class="reasons">{rs}</ul>
<div class="boxg stack" style="color:var(--ink)"><h3 class="t-h2s">止まらないとは言いません。止まったときにどう戻すかを、事前にお渡しします</h3>
<p class="t-note">事前に「復旧手順書」を1枚お渡しします。何が止まったら、誰が、何分で、どう復旧するかを明記しています。</p>
<div class="ph" style="aspect-ratio:3/2"></div></div>''',
              lead=f'登壇者を迎え、進行を見守り、来賓に挨拶する。<br>{mk("配信の実務はスタッフにお任せください。")}')
    work = [('準備', '打ち合わせと下見', 'オンラインで30分の打ち合わせ、会場のオンライン下見、配信先（Zoom・YouTubeなど）の設定'),
            ('設営', '約2時間', 'カメラ・マイク・回線を置いて、音と映像を確かめます'),
            ('本番', '配信3時間まで', '撮影、音声の調整、画面の切り替え、配信の見守り'),
            ('撤収', '約1時間', '機材を片づけます。録画データの納品はオプションです')]
    wk = ''.join(f'<li><span class="n">0{i}</span><span class="a">{a} <small>{t}</small></span><span class="b">{b}</span></li>' for i, (a, t, b) in enumerate(work, 1))
    tl = [('10:30', '搬入・設営', 'カメラ・マイク・回線を置き、音と映像を確かめます'),
          ('12:00', 'リハーサル', '登壇者のPCをつなぎ、マイクの音量と、スライドの映り方を全員分確かめます'),
          ('12:30', '開場・配信の待機', '待機画面で配信を始めておき、視聴者が入れるかを確かめます'),
          ('13:00', '本番', '撮影、音声の調整、画面の切り替え、配信の見守り（3時間まで）'),
          ('16:00', '撤収', '機材を片づけ、録画が残っているかを確かめます'),
          ('17:00', '退館', '録画データの納品（オプション）は後日お送りします')]
    tls = ''.join(f'<li><span class="tl-time">{t}</span><span class="a">{a}</span><span class="b">{b}</span></li>' for t, a, b in tl)
    timeline = sec('timeline', '当日のタイムライン', '13時に始まる会なら、<br>10時半に伺います', f'''<div class="stack"><h3 class="sub">配信の仕事の内訳</h3><ol class="steps">{wk}</ol></div>
<div class="stack"><h3 class="sub">当日の時刻の例</h3><ol class="tl">{tls}</ol></div>''',
                   lead='時刻は一例です。会場の入れる時間と開始の時刻に合わせて、打ち合わせのときに決めます。', tone='band')
    trouble = [('声が小さい、聞こえない', '会場の音響卓から音を直接取り込み、配信の音を音声担当がヘッドホンで聞き続けます'),
               ('回線が切れる', '予備回線（オプション）を用意しておけば、切れてもすぐに切り替えます'),
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
    return (head(f'当日の体制と流れ｜{NAME}', 'スタッフ3人の持ち場、持ち込む機材、当日の流れと、止まったときの戻し方です。')
            + header('service.html') + '<main id="main">'
            + page_head('当日の体制と流れ', '当日の体制と流れ', '誰が来て、何を持ち込み、当日どう動くか。見積書にも同じ内容を書きます。')
            + team + timeline + switching + day + trouble_sec + cta_box() + '</main>' + footer('service.html'))

# ------------------------------------------------------------------ 受付と現場の道具
def reception():
    ways = [('qr', 'QRコードで入場', '参加者のスマホに表示されたQRコードを、受付のスマホで読み取ります。専用の読み取り機はいりません。'),
            ('touch', 'タッチで入場', '受付に置いたタグにスマホをかざすか、受付でお伝えする4桁のコードを入れると、入場済みになります。受付に立つ人を減らせます。'),
            ('list', '紙の名簿も用意します', '同じ名簿を紙でもお持ちします。スマホを持っていない方や、会場の通信が不安定なときも、受付は止まりません。'),
            ('report', '終了後の報告を1枚で', '申込数、来場者数、オンライン視聴者数を1枚にまとめてお渡しします。上司や関係先への報告にそのまま使えます。')]
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
    tl = ''.join(f'<li class="hi stack s-16"><div class="zoom">{img(c, "（ダミー）" + a) if c else "<div class=ph style='aspect-ratio:3/2'></div>"}</div><h3 class="t-ct">{t}</h3><p class="t-body">{b}</p>'
                 + (f'<p class="t-note t-sub">{"" if n.startswith("［準備中") else "［QR］　"}{n}</p>' if n else '') + '</li>' for c, a, t, b, n in tools)
    demo = sec('demo', '現場の道具', '現場で使っている道具を、<br>いま試せます', f'''<ul class="tools" aria-label="道具の一覧">{tl}</ul>
<p class="t-note t-sub">これらの道具は、当日私たちが用意して操作します。ご自身で使えるようになりたい方には、<a href="coaching.html">内製化支援</a>をご用意しています。　［穴埋め09：デモ環境］</p>''',
               lead='お手元のスマホでお試しください。当日の質疑応答と進行がどう進むかを確認できます。', tone='band')
    return (head(f'配信支援ツール｜{NAME}', '受付用のデジタルチケットと、当日使う質疑応答・進行管理・会場診断のツールです。')
            + header('reception.html') + '<main id="main">'
            + page_head('配信支援ツール', '配信支援ツール', '受付の名簿と、当日の質疑応答・進行も、配信と一緒に引き受けます。')
            + ticket + demo + cta_box() + '</main>' + footer('reception.html'))

# ------------------------------------------------------------------ 内製化支援
def coaching():
    # #43 内製化の基準と、私たちが並走すること
    crit = [('自分たちで配信できる会', ['登壇者が1〜3人で、話す人があまり替わらない', 'カメラ1〜2台、マイク3本までで足りる', '会場の回線を事前に試せる', '配信の担当を2人置ける', 'うまくいかなくても、録画を後から公開すれば済む']),
            ('私たちにお任せいただきたい会', ['パネルディスカッションがあり、カメラの切り替えが多い', 'オンラインから登壇する人がいる', '来賓や関係者が見る、やり直しのきかない会', '会場が広く、300人を超える', '担当者が1人しか置けない'])]
    cr = ''.join(f'''<div class="crit stack s-16"><h3 class="t-h3">{t}</h3><ul class="checks">{''.join(f'<li>{x}</li>' for x in xs)}</ul></div>''' for t, xs in crit)
    criteria = sec('criteria', '内製化の基準', '自分たちで配信できる会と、<br>任せたほうがよい会', f'''<div class="crits">{cr}</div>
<p class="t-note">どちらにも当てはまる会は、最初の打ち合わせで一緒に判断します。1年のうち小さな会はご自身で、大きな会だけ私たちに、という分け方もできます。</p>''',
                   lead='すべての会を内製にする必要はありません。会の大きさと、失敗したときの影響で分けます。')
    steps = [('相談', '［3万円］', 'オンライン60分。機材と接続の図、当日のチェックリストを作成します'), ('同行', '［代行＋3万円］', '私たちの配信現場に入り、実際の動きを横で見て覚えます'),
             ('並走', '［12万円］', 'ご自身で配信を操作し、私たちは同じ現場で横に付きます。困ったらその場で代わります'), ('卒業', '［5万円］', '事前の機材点検と、当日のオンライン待機だけで見守ります')]
    st = ''.join(f'<li><span class="n">0{i}</span><span class="a">{a} <small>{f}</small></span><span class="b">{b}</span></li>' for i, (a, f, b) in enumerate(steps, 1))
    body = sec('coaching', '内製化支援', '独り立ちするまで、<br>私たちが並走します', f'''<ol class="steps">{st}</ol>
<div class="btns"><a class="btn" href="contact.html#consult">内製化について相談する</a></div>
<p class="t-note">配信の前に確かめることをまとめた<a class="tlink" href="service.html#checklist">事前チェックリスト（無料）{go()}</a></p>''',
               lead=f'教えて終わりにはしません。最初は私たちが操作し、次は横で見守り、最後はオンラインで待機する。4つの段階で少しずつ手を離します。{mk("手順書とチェックリストが残る")}ので、担当者が替わっても引き継げます。', tone='band')
    return (head(f'内製化支援｜{NAME}', '来年度から配信を内製化したい方へ。内製化の基準を一緒に決め、相談・同行・並走・卒業の4段階で独り立ちまで並走します。')
            + header('coaching.html') + '<main id="main">'
            + page_head('内製化支援', '来年度からは、<br>内製化したい', '小さな会なら、お手持ちの機材で配信できます。どの会を自分たちで回すか、その基準づくりから一緒に始めます。')
            + criteria + body + cta_box('まだ何も決まっていない方へ', '15分のオンライン相談で、iPhoneで足りるかどうかから一緒にお話しします。決まっているのが日程だけでもかまいません。') + '</main>' + footer('coaching.html'))

# ------------------------------------------------------------------ 大学・公共機関の方へ
def public():
    flow = [('問い合わせ', '決まっているのは日程と会場だけでかまいません'), ('見積書', '1営業日以内に、宛名入りのPDFでお送りします'), ('打ち合わせと会場確認', 'オンラインで30分の打ち合わせと、会場のオンライン下見を行います'),
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
    blocks = ''.join(f'<div class="mv-cmp"><div class="wrap"><p class="t-lab" id="mv-{k}"><span class="dot" aria-hidden="true"></span>{v["name"]}{"（いま使っている案）" if k == MV_USE else ""}</p></div>'
                     f'{mv(k, "mvs.html", "p", f"mv-{k}-h")}</div>' for k, v in MV.items())
    return (head(f'メインビジュアルの比較｜{NAME}', 'トップのリード文と箇条書きの案を並べて比べるページです。')
            + header('mvs.html') + '<main id="main">'
            + page_head('メインビジュアルの比較', 'リード文と箇条書きを比べる', f'トップの最初の画面に置く文の案です。src/build.py の MV_USE を変えると、トップの文が入れ替わります。いまは「{MV[MV_USE]["name"]}」を使っています。')
            + blocks + '</main>' + footer('mvs.html'))

def contact():
    sub = contact.sub = [('top', '見積を依頼する'), ('flow', '送信後の流れ'), ('sample', '見積書の見本'), ('consult', '見積の前に相談する'), ('tel', '電話で問い合わせる')]
    flow = [('1営業日以内', '見積書PDFがメールで届きます'), ('必要に応じて', 'オンラインで30分ほど打ち合わせをします'), ('ご発注後', '会場をオンラインで下見します（実地のロケハンはオプション）')]
    fl = ''.join(f'<li><span class="n">0{i}</span><span class="a">{a}</span><span class="b">{b}</span></li>' for i, (a, b) in enumerate(flow, 1))
    doc = '''<div class="doc-sample"><table><caption>御見積書（見本）</caption>
<tr><th>ハイブリッド配信 スタンダード<br><small>配信3時間まで、会場での作業6時間まで</small></th><td class="r">250,000</td></tr>
<tr><th>ディレクター・配信管理／カメラ・音声／カメラ② 各1人</th><td class="r">含む</td></tr><tr><th>カメラ3台／マイク5本まで</th><td class="r">含む</td></tr>
<tr><th>予備の録画機</th><td class="r">含む</td></tr><tr><th>打ち合わせ・会場のオンライン下見</th><td class="r">含む</td></tr>
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
    """デザインルール＝アセットの一覧（文字・色・余白・ボタン・パーツ・動き）。案件ごとの決まりは書かない（AGENTS.md へ）。
    見本は build.py の部品関数で描くので、部品を直せばここも変わる"""
    rules.sub = [('type', '文字'), ('color', '色'), ('shape', '余白・角丸・影'), ('buttons', 'ボタン'),
                 ('heads', '見出しまわり'), ('boxes', '入れ物'), ('lists', '一覧と表'), ('aids', '補助'), ('motion', '動き')]

    type_rows = [('H1', 'ページの見出し', '.t-h1', 26, 50, '1.45', 500),
                 ('H2', '節の見出し', '.t-h2', 26, 44, '1.45', 500),
                 ('H3', '節の中の見出し', '.t-h3', 18, 26, '1.6', 500),
                 ('H4', 'カードの題、質問', '.t-ct', 16, 20, '1.5', 500),
                 ('リード', '見出しの下の1〜2文', '.t-lead', 14, 18, '1.8', 400),
                 ('本文', '説明の文', '.t-body', 14, 16, '1.8', 400),
                 ('注釈', '補足、表の注', '.t-note', 12, 14, '1.7', 400)]
    ty = ''.join(f'<tr><th scope="row"><b>{a}</b><br><span class="t-note t-sub">{r}</span></th><td data-l="クラス"><code>{c}</code></td><td data-l="スマホ" class="r">{sp}px</td><td data-l="PC" class="r">{pc}px</td>'
                 f'<td data-l="行送り" class="r">{l}</td><td data-l="太さ" class="r">{w}</td><td data-l="見本"><span class="{c[1:]} type-sample">配信の費用</span></td></tr>'
                 for a, r, c, sp, pc, l, w in type_rows)

    kcss = TOKENS.read_text(encoding='utf-8')
    names = {'bg': ('地', 'ページの背景（真っ白）'), 'paper': ('紙', '箱、カード、フォーム'), 'cream': ('帯', '帯、囲み（無彩色のグレー）'), 'wash': ('淡い青', '帯、淡い面のボタン'),
             'ink': ('墨', '見出し・本文、塗りの面'), 'ink-strong': ('濃い墨', '強調、キーボードの枠'), 'sub': ('補足', '注釈、文字リンクの矢印'),
             'line': ('罫線', '表の区切り、箱の線'), 'line-strong': ('網点のグレー', '点線、ヒーローの網点の地'), 'main': ('青（主色）', 'タグ、アイコン、標準のボタン、白い文字を載せる面'),
             'red': ('赤', '申し込み・依頼のボタン、エラー、必須'), 'yellow': ('黄', 'いちばん押してほしいボタン、バッジ'), 'marker': ('マーカー', '要点の下線')}
    tokens = [(k, v) for k, v in re.findall(r'--k-([a-z-]+): (#[0-9a-f]{6});', kcss) if k in names]
    assert len(tokens) == len(names), '色見本のトークンが足りません'
    sw = ''.join(f'<li class="swatch"><span style="background:{v}"></span><p class="t-note"><b>{names[k][0]}</b>　{v.upper()}<br><span class="t-sub">{names[k][1]}</span></p></li>' for k, v in tokens)

    shape_rows = [('ページの左右', '--pad', '16 → 80px'), ('節と節の間、帯の上下の内側', '--sec', '64 → 96px（ヒーローの後もふくめ、どこも同じ）'),
                  ('見出しと中身の間', '--gap-56', '28 → 56px'), ('ブロックの間', '--gap-48 / --gap-64', '16 → 48px ／ 40 → 64px'),
                  ('ボタンの高さ', '--btn-h', '48 → 60px（小は 44px）')]
    sh = ''.join(f'<tr><th scope="row">{a}</th><td data-l="トークン"><code>{b}</code></td><td data-l="値（スマホ → PC）">{c}</td></tr>' for a, b, c in shape_rows)

    def part(name, cls, demo, rule):
        return (f'<li class="part"><div class="part-demo">{demo}</div><div class="stack s-16"><h4 class="t-ct">{name}　<code>{cls}</code></h4>'
                f'<p class="t-body">{rule}</p></div></li>')
    def group(sid, tag, title, items, lead=''):
        return sec(sid, tag, title, f'<ul class="parts">{"".join(items)}</ul>', lead)

    # ボタン：種類 × 大きさ
    kinds = [('塗り・黄', 'plan', 'いちばん押してほしい行動。1画面に1つ'), ('塗り・赤', 'quote', '申し込み・依頼の行動'), ('塗り・青', '', 'そのほかの行動'),
             ('線', 'line', '資料など、補助の行動'), ('淡い面', 'soft', 'カードの中など、並べて置く行動'), ('白いピル＋丸', 'dot', '色の地の上や、軽く誘う行動。丸の色は .dot-red ／ .dot-yellow ／ .dot-ink')]
    bt = ''.join(f'<tr><th scope="row">{n}<br><code>.btn{("." + c) if c else ""}</code><br><span class="t-note t-sub">{u}</span></th>'
                 f'<td data-l="大">{btn("ボタン", "#buttons", (c + " lg").strip())}</td><td data-l="標準">{btn("ボタン", "#buttons", c)}</td><td data-l="小">{btn("ボタン", "#buttons", (c + " s").strip())}</td></tr>' for n, c, u in kinds)
    buttons = sec('buttons', 'ボタン', '種類と大きさ', f'''<table class="tbl tbl--btns"><thead><tr><th scope="col">種類</th><th scope="col">大 <code>.lg</code></th><th scope="col">標準</th><th scope="col">小 <code>.s</code></th></tr></thead><tbody>{bt}</tbody></table>
<ul class="parts">{part('文字リンク', '.tlink ＋ .go', f'<a class="tlink" href="#buttons">一覧を見る{go()}</a>', '別の節やページへ移る。下線は引かず、右に背景なしのグレーの矢印')}
{part('白いピル＋丸', '.btn.dot', '<div class="part-dots">' + btn('デモを見る', '#buttons', 'dot dot-red') + btn('制作について相談する', '#buttons', 'dot dot-ink') + '</div>', '角を丸く切った白い面の頭に、色の丸。矢印は付けない。地が白いときは使わず、帯やグレーの地の上に置く')}
{part('アイコンつき', '.btn ＋ .bico', f'<a class="btn plan" href="#buttons">{bico("diag")}アイコンつき</a>', 'ボタンの頭に線のアイコン。左に寄せ、矢印は右端')}</ul>
<ul class="rows"><li>押せるものだけを、ボタンの形にする。タグや札には枠や面を付けない</li><li>ボタンに影は付けない。右端に小さな矢印。スマホでは横いっぱい</li><li>同じ意味の行動は、どこでも同じ色・同じ名前</li></ul>''')

    heads = group('heads', '見出しまわり', 'タグ、小見出し、札', [
        part('タグ', '.t-lab', lab('よくあるお悩み'), '節の頭。細く大きなカッコの中に、青い丸と濃い文字。枠や面は付けない'),
        part('節の頭', 'sec()', '<div class="sec-head stack">' + lab('タグ') + '<p class="t-h2s">見出しは2行まで</p><p class="t-note">リードは1〜2文</p></div>', 'タグ → 見出し → リード の順に縦に積む。左に見出しだけの列は作らない'),
        part('小見出し', '.sub', '<p class="sub" style="inline-size:100%">ケーススタディ</p>', '節の中の区切り。青い小さな丸と濃い文字、右へ点線を伸ばす'),
        part('札', '.pill', '<span class="pill">シンポジウム</span><span class="pill">講演会</span>', '分類。点線の丸い枠。押せるものには使わない'),
    ])
    boxes = group('boxes', '入れ物', 'カード、吹き出し、囲み', [
        part('アイコンと文', '.reason', f'<ul class="reasons"><li class="reason">{ico("doc")}<div class="stack s-16"><h3 class="t-ct">カードの題</h3><p class="t-body">アイコンと題を横に並べ、本文はアイコンの下まで広げる</p></div></li></ul>',
             '3つ並べるときは PC で3列。カードの題は1行に収まる字数（3列なら全角10字まで）'),
        part('写真つきのカード', '.reasons--card', f'<ul class="reasons reasons--card"><li class="reason"><div class="reason-ph zoom">{img("P05", "（ダミー）写真")}</div>{ico("doc")}<div class="stack s-16"><h3 class="t-ct">カードの題</h3><p class="t-body">本文</p>{btn("詳しく見る", "#boxes", "soft s")}</div></li></ul>',
             '写真 → アイコンと題 → 本文 → 小さい淡い面のボタン。並べたときはボタンを下端にそろえる'),
        part('吹き出し', '.voice', f'<ul class="voices"><li class="voice"><blockquote class="voice-q"><p>お客さまの声は、吹き出しに入れます。</p></blockquote><p class="voice-who t-note t-sub"><span class="avatar">{bico("person")}</span>話している人の肩書き</p></li></ul>',
             '青のベタに白い文字。しっぽは人のアイコンを指す。並べたときは高さをそろえる'),
        part('線のカード', '.opt-card', '<ul class="opt-cards" style="inline-size:100%;grid-template-columns:1fr"><li class="opt-card"><div class="stack s-16"><p class="t-ct">カードの題</p><p class="t-note">影を付けず、細い実線で囲む</p></div></li></ul>',
             '写真と料金の行を入れるカード。白い地の上でも帯の上でも、影でなく1pxの実線（--line）で囲む'),
        part('白い箱・帯・暗い囲み', '.boxw ／ .boxg ／ .boxd', '<div class="boxw" style="padding:1rem">白い箱</div><div class="boxg" style="padding:1rem">グレーの面</div><div class="boxd" style="padding:1rem;box-shadow:none">暗い囲み</div>',
             '白い箱は細い線で、グレーの面は面だけで区切る。暗い囲みはページの終わりの行動に。フッターの見積フォームは白い箱'),
        part('コラム', '.boxc', '<div class="boxc stack s-16" style="inline-size:100%">' + lab('コラム') + '<p class="t-ct">本筋から少し外れた読みもの</p></div>', '青の点線と、大きな角丸で囲む。頭に「コラム」のタグ'),
        part('バッジ', '.badge', '<a class="badge" href="#diag" data-open-diag aria-haspopup="dialog" style="--badge:9rem"><span class="badge-sh" aria-hidden="true"><span class="badge-bg"></span></span>'
             '<span class="badge-t"><span class="badge-emoji" aria-hidden="true">📋</span>バッジ</span></a>', '黄の細かいギザギザに、薄いドロップシャドウ。頭は線のアイコンでなく絵文字。縁だけがゆっくり回り、文字は回さない。ヒーローの縁に半分かけて置く'),
        part('バナー', '.banner', '<a class="banner" href="#boxes"><span class="banner-t">バナーの題</span><span class="banner-s">ひとこと</span>' + go() + '</a>', '特設ページへの入口。淡い青の面に、左の帯と矢印'),
    ])
    lists = group('lists', '一覧と表', '並べ方', [
        part('行の一覧', '.rows', '<ul class="rows" style="inline-size:100%"><li>1行に1つ</li><li>罫線で区切る</li></ul>', '決まりや条件。点線で区切り、番号は付けない'),
        part('手順', '.steps', '<ol class="steps" style="inline-size:100%"><li><span class="n">01</span><span class="a">相談</span><span class="b">順番に意味があるときだけ番号を付ける</span></li></ol>', '番号は青の英数字'),
        part('チェックの一覧', '.incl', f'<ul class="incl" style="inline-size:100%"><li>{ico("check", "s")}<span>含まれるもの</span></li><li>{ico("check", "s")}<span>確かめること</span></li></ul>', '題と説明があるときは、題を太字にして改行'),
        part('名前と料金の行', '.opt-rows ＋ .yen', '<ul class="opt-rows" style="inline-size:100%"><li><span class="n">項目の名前<small>ひとこと</small></span><span class="r"><span class="yen"><b>38,500</b><small>円</small><span class="tax">（税別）</span></span></span></li></ul>', '左に名前（下に小さくひとこと）、右に大きな英数字の金額と小さな「円」「（税別）」。行は細い線で区切り、意味ごとに小見出しでまとめる'),
        part('表', '.tbl ／ .cmp', '<table class="tbl" style="inline-size:100%"><tbody><tr><th scope="row">スタッフ</th><td class="r">3人</td></tr><tr><th scope="row">カメラ</th><td class="r">3台</td></tr></tbody></table>', '同じ意味の値は、同じ行・同じ縦位置にそろえる。スマホでは1行ずつ縦に積む（比較表は横スクロール）'),
        part('スライダー', '.cases ＋ .cases-count', '<p class="t-note"><span style="font-size:1.25rem">1</span> / 4</p>', '手で横にスクロールする。右上に「1 / 4」で今の位置'),
        part('流れる写真のスライダー', '.cs', '<p class="t-note"><span style="font-size:1.25rem">2</span> / 4　<button class="cs-pause" type="button">止める</button></p>', '画面の端まで突き抜け、写真は流れ続ける。下の文は左端（主役）の写真の説明で、主役以外の写真は薄くする。止めるボタンを付け、触っている間と「視差効果を減らす」では止める'),
    ])
    aids = group('aids', '補助', 'アイコン、マーカー、穴埋め', [
        part('アイコン', '.chipi ／ .bico', ico('mic') + ico('check', 's') + f'<span style="color:var(--ink)">{bico("diag")}</span>', '四角に入れたもの（.chipi）は内容の目印、線だけのもの（.bico）はボタンの頭。飾りなので読み上げない'),
        part('要点のマーカー', '.mk', f'<p class="t-body">{mk("いちばん伝えたい一文")}にだけ引く</p>', '1つの節に1か所まで'),
        part('補足の「?」', '.tip', '<p class="t-body">マイク5本まで' + tip('tip-rules', 'マイク5本の理由', '補足の文が、ここに出ます。') + '</p>', '読まなくても困らない補足。使えないブラウザでは本文の下に注記として出す'),
        part('穴埋め', '.ana', '<p class="t-body">［金額］</p>', 'まだ決まっていない値。［ ］で囲むと自動で灰色の斜線になる'),
        part('画像の仮置き', 'img()', f'<div style="inline-size:8rem">{img("P04", "（ダミー）画像の仮置き")}</div>', '写真・図は、本物が届くまで無地のグレー'),
    ])

    body = (sec('type', '文字', 'H1〜H4、本文、注釈', f'''<table class="tbl tbl--type"><thead><tr><th scope="col">見出し・本文</th><th scope="col">クラス</th><th scope="col" class="r">スマホ</th><th scope="col" class="r">PC</th><th scope="col" class="r">行送り</th><th scope="col" class="r">太さ</th><th scope="col">見本</th></tr></thead><tbody>{ty}</tbody></table>
<ul class="rows"><li>和文は Noto Sans JP（Regular 400／Medium 500）。英字と数字は Helvetica Neue（Windows では Arial）</li>
<li>スマホは幅375px、PC は幅1440px 以上での大きさ。その間は画面の幅に合わせて変わる。囲みの中の見出しは <code>.t-h2s</code>（18 → 28px）</li>
<li>見出しは文節で改行。入力欄の文字はスマホでも16px</li></ul>''')
            + sec('color', '色', '白の地に、青・赤・黄・墨', f'''<ul class="swatches">{sw}</ul>
<ul class="rows"><li>色は意味で決める。同じ意味のものは同じ色</li><li>大きな面は地・帯・淡い青・青だけ。赤と黄は行動とバッジに、網点のグレーはヒーローの地（写真が届くまで）に</li>
<li>青の上の文字は白。値の元は design/karura-tokens.css（ツールと共通）</li></ul>''')
            + sec('shape', '余白・角丸・影', '余白は幅に合わせて伸びる', f'''<table class="tbl"><thead><tr><th scope="col">場所</th><th scope="col">トークン</th><th scope="col">値（スマホ → PC）</th></tr></thead><tbody>{sh}</tbody></table>
<ul class="rows"><li>節と節の間は1つの値（<code>--sec</code>）にそろえる。ヒーロー（MV）の後も同じ。帯は外も内側も同じ値</li>
<li>角丸：ボタン・入力欄 6px、カード・アイコンの四角 10px、コラム 28px、タグや札は丸</li>
<li>囲みは3種類。カードや箱は細い実線（<code>--line</code>、1px）、区切りと強調の囲み（小見出し・一覧の行・コラム）は点線、影は大事なものだけ</li><li>影は大事なところだけ：比較表とプラン診断（0 0 30px 黒8%）、書類の見本と暗い囲み（0 5px 40px 黒20%）、バッジ（薄いドロップシャドウ）。オプションのカードやよくある質問には付けない</li></ul>''')
            + buttons + heads + boxes + lists + aids
            + sec('motion', '動き', '動きは、減らせる', '''<ul class="rows"><li>押せるものの反応は 0.3秒、cubic-bezier(0.4, 0.4, 0, 1)。幕や出現は cubic-bezier(0.19, 1, 0.22, 1)</li>
<li>ずっと動くのは、バッジの縁（24秒で1周）と、写真の自動切り替え（止めるボタンつき）だけ</li>
<li>「視差効果を減らす」を選んでいる人には、自動の動きをすべて止める</li></ul>'''))
    return (head(f'デザインルール｜{NAME}', 'サイトで使う文字・色・余白・ボタン・パーツの一覧です。')
            + header('rules.html') + '<main id="main">'
            + page_head('デザインルール', 'サイトで使う<br>アセットの一覧', '文字、色、余白、ボタン、パーツの見本と使い方です。見本は、サイトで使っている部品そのものを置いています。')
            + body + '</main>' + footer('rules.html'))


PAGES = {'index.html': index, 'service.html': service, 'reception.html': reception, 'coaching.html': coaching, 'public.html': public,
         'contact.html': contact, 'thanks.html': thanks, 'rules.html': rules, 'mvs.html': mvs}
def subset_font(text):
    """ページで使っている文字だけの書体ファイルを、太さごとに作る（元は約2.4MB、切り出すと数百KB）"""
    from fontTools import subset
    chars = ''.join(sorted(set(text) | {chr(i) for i in range(0x20, 0x7f)}))
    for weight, src in FONT_SRC.items():
        options = subset.Options(flavor='woff2', layout_features=['*'])
        font = subset.load_font(str(src), options)
        subsetter = subset.Subsetter(options)
        subsetter.populate(text=chars)
        subsetter.subset(font)
        subset.save_font(font, str(OUT / 'assets' / 'fonts' / f'noto-{weight}.woff2'), options)


if __name__ == '__main__':
    # docs/ を作り直す（生成物だけを置く）
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'assets' / 'fonts').mkdir(parents=True)
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
