#!/usr/bin/env python3
"""C案（採用案）の書き出し： python3 build_c.py
   ../../c/ に index.html、contact.html、thanks.html、rules.html を書き出す。
   文言はすべてこのファイルの中。CSS と JS は c/assets/ を直接編集する。"""
import re
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / 'c'
NAME, NAME_EN = 'カルラライブ', 'KARURA LIVE'
SIZES = {f.stem: Image.open(f).size for f in (OUT / 'img').glob('*.webp')}

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
}
def ico(name, tone='teal', size=''):
    """色の角丸チップに入った線画アイコン（飾りなので読み上げない）"""
    return (f'<span class="chipi chipi--{tone}{" chipi--" + size if size else ""}" aria-hidden="true">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg></span>')

def mk(t):
    """要点に引く黄色のマーカー"""
    return f'<mark class="mk">{t}</mark>'

def lab(t):
    return f'<p class="t-lab">{t}</p>'

# ------------------------------------------------------------------ 共通
def subnav_html(items):
    """現在地つきの目次。スマホではヘッダー下の横並び、PCでは左レールの縦並び。items = [(セクションのid, 短い名前)]"""
    li = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items)
    return f'<nav class="subnav" aria-label="このページの目次"><ol>{li}</ol><span class="subnav-meter" aria-hidden="true"></span></nav>'

NAV = [('#plan', 'プラン診断'), ('#price', '料金・体制・機材'), ('#works', '事例'), ('#demo', 'ツールデモ'), ('#public', '大学・公共機関の方へ'), ('#faq', 'よくある質問')]

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
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%232c2c2e'/%3E%3Ccircle cx='16' cy='16' r='5' fill='%23d7281e'/%3E%3C/svg%3E">
<script>document.documentElement.classList.add('js');{intro}</script>
<link rel="preload" href="assets/fonts/zkgn-500.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/site.css">
<script type="module" src="assets/site.js"></script>{extra}
</head>
<body>
'''

def header(home, sub=None):
    """スマホ：上のバー＋現在地のサブナビ（いっしょに追従）。PC：左の固定レール（ロゴ・目次・2つの行動）"""
    pre = '' if home else 'index.html'
    items = ''.join(f'<li><a href="{pre}{h}">{t}<span aria-hidden="true">›</span></a></li>' for h, t in NAV)
    toc = subnav_html(sub) if sub else ('<nav class="railnav" aria-label="メインメニュー"><ol>'
            + ''.join(f'<li><a href="{pre}{h}">{t}</a></li>' for h, t in NAV) + '</ol></nav>')
    pages = [('index.html', 'トップ'), ('contact.html', 'お問い合わせ'), ('rules.html', 'デザインルール')]
    pg = ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in pages)
    return f'''<a class="skip" href="#main">本文へ移動</a>
<header class="hdr">
<div class="hdr-bar">
<a class="logo" href="index.html" aria-label="{NAME} トップページ">{NAME_EN}<small>{NAME}</small></a>
<button type="button" class="menu-btn" data-open-menu aria-haspopup="dialog" aria-controls="menu"><span class="vh">メニューを開く</span><i></i><i></i></button>
<a class="menu-fallback t-note" href="#fnav">メニュー</a>
</div>
{toc}
<div class="rail-foot">
<a class="tile tile--plan" href="{pre}#plan">8問で<br>プラン診断<span aria-hidden="true">↓</span></a>
<a class="tile tile--quote" href="contact.html">見積を<br>依頼する<span aria-hidden="true">→</span></a>
<nav aria-label="ページ"><ul class="rail-pages">{pg}</ul></nav>
</div>
</header>
<dialog id="menu" class="menu" aria-label="メニュー">
<div class="menu-head"><span class="logo">{NAME_EN}<small>{NAME}</small></span><form method="dialog"><button class="menu-close">閉じる</button></form></div>
<nav aria-label="メニュー"><ul>{items}<li><a href="contact.html">お問い合わせ・お見積<span aria-hidden="true">›</span></a></li></ul>{btn('8問でプランを診断する', pre + '#plan', 'full')}</nav>
</dialog>
'''

def footer(home, form=True):
    pre = '' if home else 'index.html'
    contact = ''
    if form:
        contact = f'''<section id="contact" class="boxg stack s-48" aria-labelledby="contact-title" style="color:var(--ink)">
<div class="g57">
<div class="stack">{lab('Contact')}<h2 id="contact-title" class="t-h2">日程と会場だけ、<br>教えてください</h2>
<p class="t-lead">{mk('1営業日以内に、宛名入りの見積書PDF')}をメールでお送りします。詳しい内容は、その後のやりとりで詰めていきます。</p>
<p class="t-note">［年度末（2〜3月）の空き日程：残り〇日］</p>
<p class="t-note" id="tel">お電話でも受け付けています　［電話番号］　［受付時間］</p></div>
{quote_form('f')}
</div></section>'''
    links = [(pre + '#plan', 'プラン診断'), (pre + '#price', '料金・体制・機材'), (pre + '#works', '事例'), (pre + '#demo', 'ツールデモ'),
             (pre + '#coaching', '配信コーチング'), (pre + '#public', '大学・公共機関の方へ'), (pre + '#faq', 'よくある質問'),
             ('contact.html', 'お問い合わせ・お見積'), ('rules.html', 'デザインルール')]
    nav = ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in links)
    mq = ''.join('<span>LIVE STREAMING × HYBRID EVENTS</span>' for _ in range(4))
    return f'''<div class="mq" aria-hidden="true"><div class="mq-t">{mq}</div></div>
<footer class="foot">
{contact}
<nav class="{"mtl" if form else ""}" aria-label="フッターメニュー" id="fnav"><ul class="fnav">{nav}</ul></nav>
<p class="copy">© 2026 {NAME_EN}　対応エリア：新宿から90分圏内　［運営者名］</p>
</footer>
<nav class="spbar" aria-label="よく使う操作"><a href="{pre}#plan">プラン診断</a><a href="contact.html">見積を依頼する</a></nav>
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
        plans = ''.join(f'<label><input type="checkbox" name="plan" value="{v}">{v}</label>' for v in ['スタンダード（25万円）', 'まるごと（写真・編集つき）', 'コーチング', 'まだわからない'])
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
<button class="btn full" type="submit">見積書を受け取る</button>
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

# ------------------------------------------------------------------ トップ
def tbl_gear():
    rows = [('カメラ', '［機種名］', '3台', '話している人のアップ、登壇者全体、会場全体'),
            ('マイク', '［機種名］', '5本', '登壇者4人分と、会場の質問用1本'),
            ('画面の切り替え機', '［機種名］', '［数］', '発表スライドとカメラ映像の切り替え'),
            ('録画機', '［機種名］', '2系統', '片方が止まっても、もう片方で記録を残します'),
            ('回線', '［機種名・回線種別］', '2系統', '会場の回線が切れても、予備回線で配信を続けます')]
    tr = ''.join(f'<tr><td class="k">{a}</td><td class="m" data-l="機種">{b}</td><td class="k" data-l="数">{c}</td><td data-l="用途">{d}</td></tr>' for a, b, c, d in rows)
    return f'<table class="tbl"><caption class="vh">持ち込む機材の内訳</caption><thead><tr><th scope="col">種類</th><th scope="col">機種</th><th scope="col">数</th><th scope="col">用途</th></tr></thead><tbody>{tr}</tbody></table>'

def tbl_extra():
    rows = [('配信時間を1時間延長する', '［金額］'), ('スタッフを1名追加する（オンライン登壇者がいる場合、マイク6本以上の場合）', '［金額］'),
            ('カメラを1台追加する', '［金額］'), ('会場に使えるインターネット回線がない', '［金額］'), ('対応エリア（新宿から90分圏内）外の交通費・宿泊費', '実費')]
    tr = ''.join(f'<tr><td>{a}</td><td class="r" data-l="追加料金（税別）">{b}</td></tr>' for a, b in rows)
    return f'<table class="tbl"><caption class="vh">追加料金がかかる条件</caption><thead><tr><th scope="col">条件</th><th scope="col" class="r">追加料金（税別）</th></tr></thead><tbody>{tr}</tbody></table>'

def tip(tid, label, body):
    """「?」で開く補足。popover 未対応では、本文の下に注記として出る"""
    return (f'<span class="tip"><button type="button" class="tip-btn" popovertarget="{tid}" aria-label="{label}" style="anchor-name:--{tid}">?</button>'
            f'<span id="{tid}" popover class="tip-body" style="position-anchor:--{tid}">{body}</span></span>')

def case(n, org, bg, imgs, extra_size):
    gallery = ''.join(img(c, a) for c, a in imgs)
    return f'''<article class="case" aria-labelledby="case{n}-t"><div class="case-l">{img(bg, '', 'case-bg')}
<p class="t-note">Case #0{n}　|　［主催機関名］</p>
<div class="case-tags"><span class="pill">［大学］</span><span class="pill">［シンポジウム］</span></div>
<h3 class="t-ct" id="case{n}-t">［会の名称：課題と成果を一文で］</h3>
<p class="t-body">［当日起きたことと、どう戻したか。2〜3行］</p>
<dl class="chips"><div class="chip"><dt>会の規模</dt><dd>登壇［ ］人、会場［ ］人</dd></div><div class="chip"><dt>当日の体制</dt><dd>スタッフ［ ］名{extra_size}</dd></div>
<div class="chip"><dt>使用機材</dt><dd>カメラ［ ］台、マイク［ ］本</dd></div><div class="chip"><dt>金額</dt><dd>［25万〜30万円］</dd></div></dl></div>
<div class="case-r">{gallery}</div></article>'''

FAQ = [
    ('何日前までに頼めば間に合いますか', '［最短の日数と、繁忙期の目安］'),
    ('Zoom、YouTube、Teamsのどれに対応していますか', '［対応している配信先］'),
    ('登壇者の一部がオンラインから参加します', '対応できます。スタッフを1名追加します（［金額］）。'),
    ('会場にインターネット回線がありません', '配信用の回線を持ち込みます（［金額］）。事前に会場で電波状況を確認します。'),
    ('配信が止まった場合、料金はどうなりますか', '［返金・減額の規定］'),
    ('対応エリアはどこまでですか', '新宿駅からおおむね90分以内で伺える会場が対応エリアです。エリア内は、会場の下見も交通費も25万円に含まれます。エリア外の会場は、交通費と宿泊費の実費で伺います。'),
    ('iPhoneで足りる会かどうか、先に知りたい', '<a href="#plan">8問のプラン診断</a>でご確認いただけます。iPhoneで足りる会なら、そうお伝えします。'),
    ('相見積のための見積依頼でもかまいませんか', '歓迎します。<a href="#spec">仕様書のひな形</a>と見積書の見本もお送りしますので、他社への依頼にもそのままお使いください。'),
    ('支払い方法を教えてください', '請求書払い（後払い）に対応しています。見積書・納品書・請求書の3点を発行します。'),
]

def index():
    sub = [('plan', '8問でプラン診断'), ('switching', '配信画面の切り替え'), ('scope', 'お引き受けする会'), ('price', '25万円に含まれるもの'),
           ('team', '当日の体制と機材'), ('day', '当日の流れ'), ('demo', '現場の道具を試す'), ('works', '事例と金額'),
           ('option', '写真・映像の追加'), ('coaching', '自分たちで配信する'), ('public', '大学・公共機関の発注'), ('faq', 'よくある質問'),
           ('contact', '見積を依頼する')]
    intro = '<div class="intro" aria-hidden="true"><p>' + ''.join(f'<span style="--i:{i}">{c}</span>' for i, c in enumerate(NAME_EN)) + '</p></div>'

    hero = f'''<section class="hero" aria-labelledby="hero-title"><div class="wrap">
<p class="hero-kind">シンポジウム・講演会・公開講座のライブ配信／ハイブリッド配信（会場＋オンライン）</p>
<h1 class="t-h1" id="hero-title">カメラ5台はいりません。<br>でも1台では、パネルディスカッションは撮れません。</h1>
<div class="g75 hero-grid">
<section id="plan" class="hero-plan stack s-16" aria-labelledby="plan-title">
<div class="dg-top">{lab('Plan check')}<p class="t-note t-sub">1分ほどで終わります</p></div>
<h2 class="t-ct" id="plan-title">8問で、あなたの会に合うプランと費用がわかります</h2>
<button type="button" class="dg-launch" data-open-diag aria-haspopup="dialog" aria-controls="diag-modal"><span class="dg-launch-t">プラン診断をはじめる</span><span class="dg-launch-s">8問・1分ほど。答えると、プランと費用が出ます</span><span class="dg-launch-a" aria-hidden="true">→</span></button>
<dialog id="diag-modal" class="dg-modal" aria-label="プラン診断">
<div class="dg-modal-head"><p class="t-ct">プラン診断</p><form method="dialog"><button class="menu-close">閉じる</button></form></div>
{diag()}
</dialog>
</section>
<div class="hero-side stack">
<ul class="ticklist hero-text">
<li>{ico('check', 'teal', 's')}<span>{mk('登壇者2〜6人、会場50〜300人')}の会を専門にしています</span></li>
<li>{ico('check', 'coral', 's')}<span>見積書に、{mk('スタッフ2名の役割と機材の内訳')}をすべて明記します</span></li>
<li>{ico('check', 'yellow', 's')}<span>{mk('iPhoneで足りる会なら、そうお伝えします')}</span></li>
</ul>
<p class="hero-price">カメラ3台・スタッフ2名・マイク5本。<br><span class="t-big2">25<small>万円（税別）</small></span></p>
<div class="btns">{btn('見積を依頼する', 'contact.html', 'line')}<a class="tlink" href="#price">25万円に含まれるもの</a></div>
</div>
</div></div>
<div class="sd" aria-hidden="true"><span>Scroll Down</span><i></i></div>
</section>'''

    switching = f'''<section id="switching" class="band sec-2" aria-labelledby="sw-title"><div class="wrap pad-band"><div class="g57 sw" data-sw>
<div class="stack s-48"><div class="stack">{lab('Switching')}<h2 class="t-h3" id="sw-title" data-rv>カメラを選ぶと、<br>配信中の画面が切り替わります</h2>
<p class="t-body">3台あると、話す人が替わるたびに映像を切り替えられます。</p></div>
<fieldset class="cams"><legend class="vh">映すカメラを選ぶ</legend>
<label class="cam"><input type="radio" name="cam" id="cam-1" value="1" checked><b>カメラ1</b><span>話している人</span></label>
<label class="cam"><input type="radio" name="cam" id="cam-2" value="2"><b>カメラ2</b><span>登壇者全体</span></label>
<label class="cam"><input type="radio" name="cam" id="cam-3" value="3"><b>カメラ3</b><span>会場全体</span></label></fieldset>
<p class="t-note t-sub">写真は同じ会の3枚（ダミー：P01・P02・P03）</p></div>
<div class="screen" data-rv="media">
{img('P01', '（ダミー）カメラ1：話している人のアップ', 'shot shot-1')}{img('P02', '（ダミー）カメラ2：パネルディスカッション全体', 'shot shot-2')}{img('P03', '（ダミー）カメラ3：会場全体、客席とスクリーン', 'shot shot-3')}
<p class="onair"><i></i>配信中の画面</p>
<button type="button" class="sw-pause" aria-pressed="false" hidden>切り替えを止める</button>
</div>
</div></div></section>'''

    clients = f'''<section class="sec" aria-labelledby="clients-title"><div class="wrap stack s-48">
<div class="stack s-16">{lab('Clients')}<h2 class="t-note" id="clients-title">これまでに配信・記録を担当した機関　［配信した会の件数、継続して依頼いただいている機関の数］</h2></div>
<ul class="logos">{''.join('<li><div class="ph">［ロゴ］</div></li>' for _ in range(6))}</ul>
</div></section>'''

    scope = f'''<section id="scope" class="sec" aria-labelledby="scope-title"><div class="wrap"><div class="g57"><div class="stk">{lab('Scope')}</div>
<div class="stack s-56">
<h2 class="t-h2" id="scope-title" data-rv>このような会を<br>お引き受けしています</h2>
<div class="stack"><h3 class="sub">お引き受けする会</h3><ul class="rows rows--ok"><li>登壇者が2〜6人で、パネルディスカッションや対談がある会</li><li>会場に50〜300人が集まり、オンラインにも同時に配信したい会</li><li>配信は3時間まで、半日で終わる会</li><li>来賓や助成元、学外の視聴者がいて、配信を止められない会</li></ul></div>
<div class="stack"><h3 class="sub">ほかの方法をおすすめする会</h3><ul class="rows rows--ng"><li>登壇者が1人の講演：スタッフ1名で来る業者で十分です</li><li>30人以下の勉強会：お手持ちのiPhoneやPCで足ります</li><li>複数会場や同時通訳：大手の制作会社が向いています</li><li>迷った方は、<a href="#plan">8問のプラン診断</a>でご確認いただけます</li></ul></div>
</div></div></div></section>'''

    tiles = ['スタッフ2名', 'カメラ3台と、発表スライドの映像取り込み',
             f'マイク5本までの持ち込み{tip("tip-mic", "マイクが5本の理由", "登壇者4人分と、会場の質問用1本です。6本以上必要な会は、スタッフを1名追加します。")}',
             '会場設備のマイク音声も直接取り込みます', '予備の録画機と、予備のインターネット回線',
             f'配信3時間まで、会場での作業6時間まで{tip("tip-time", "作業時間の内訳", "設営2時間、配信3時間、撤収1時間が目安です。")}',
             '事前の打ち合わせと会場の下見', '録画データの納品']
    price = f'''<div class="mq sec-2" aria-hidden="true"><div class="mq-t">{''.join('<span>LIVE STREAMING × HYBRID EVENTS</span>' for _ in range(4))}</div></div>
<section id="price" class="bandg" aria-labelledby="price-title"><div class="wrap pad-band"><div class="g57">
<div class="stk stack s-56"><div class="stack s-48">{lab('Price')}<h2 class="t-h2" id="price-title" data-rv>25万円に<br>含まれるもの<br>すべて</h2>
<p class="t-lead">誰が来て、何を持ち込み、何をするか。<br>{mk('見積書にも同じ内容を記載します。')}</p></div>
<div class="pc-only">{btn('この内容で見積書を受け取る', 'contact.html')}</div></div>
<div class="stack s-48">
<h3 class="t-bar">スタンダード</h3>
<p class="t-big">25<small>万円（税別）</small></p>
<div class="stack"><p class="sub">含まれるもの</p><ul class="tiles">{''.join(f'<li><span>{t}</span></li>' for t in tiles)}</ul></div>
<div class="sp-only">{btn('この内容で見積書を受け取る', 'contact.html', 'full')}</div>
</div></div></div></section>'''

    team = f'''<section id="team" class="sec" aria-labelledby="team-title"><div class="wrap"><div class="g57"><div class="stk">{lab('Team &amp; Equipment')}</div>
<div class="stack s-64">
<h2 class="t-h2" id="team-title" data-rv>当日の体制：<br>立っているだけのスタッフは<br>連れていきません</h2>
<div class="staff-wrap"><ul class="staff">
<li class="staff-card"><div class="zoom">{img('P04', '（ダミー）映像担当のスタッフ')}</div><div><h3 class="t-ct">1人目：映像担当</h3><p class="t-body">カメラ3台の操作と、配信画面の切り替え</p><p class="t-note t-sub">［氏名・経歴一行］</p></div></li>
<li class="staff-card"><div class="zoom">{img('P05', '（ダミー）音声・配信担当のスタッフ')}</div><div><h3 class="t-ct">2人目：音声・配信担当</h3><p class="t-body">マイクと音量の調整、配信の監視、登壇者PCの接続</p><p class="t-note t-sub">［氏名・経歴一行］</p></div></li></ul></div>
<figure data-rv="media"><div class="ph" style="aspect-ratio:16/9">［図：会場の見取り図に、カメラ3台・スタッフ2名・マイクの位置を置いた配置図］</div></figure>
<div class="stack"><h3 class="t-h3">持ち込む機材の内訳</h3>{tbl_gear()}</div>
<div class="stack"><h3 class="t-h3">追加料金がかかるのは、<br>この5つだけです</h3>{tbl_extra()}</div>
<div class="btns">{btn('見積を依頼する', 'contact.html')}<a class="tlink" href="contact.html">料金表と見積書見本（PDF）を見る</a><span class="t-note t-sub">上司への説明や、相見積にそのまま使えます</span></div>
</div></div></div></section>
<section class="sec-3" aria-label="見積の依頼"><div class="wrap"><div class="boxd cta-in"><div class="stack"><p class="t-h2s">この体制で、見積書を受け取る</p>
<p class="t-note">日程と会場だけで、2名の役割と機材の内訳が入った見積書をお送りします。1営業日以内に、宛名入りのPDFでお届けします。</p></div>
<div>{btn('見積書を受け取る', 'contact.html', 'xl')}</div></div></div></section>'''

    reasons = [('聞き取りやすい音', '会場のマイク音声を配信機材に直接取り込みます。会場にマイクがなければ5本まで持ち込みます。音が悪いと、研究まで低く見られます（<a href="https://researchportalplus.anu.edu.au/en/publications/good-sound-good-research-how-audio-quality-influences-perceptions/">Newman &amp; Schwarz 2018</a>）。'),
               ('表情がわかるアップの映像', '客席の後ろから、話している人の表情を撮ります。来場者の視界をふさぎません。'),
               ('見やすい画面の切り替え', '発表スライド、登壇者、会場全体の映像を状況に合わせて切り替えます。スライドの隅に登壇者の顔を出すこともできます。'),
               ('万が一に備える予備機材', '録画機もインターネット回線も2系統ずつ用意します。どれか1つが止まっても、配信と記録は続きます。')]
    marks = [('mic', 'teal'), ('face', 'coral'), ('switch', 'yellow'), ('backup', 'teal')]
    rs = ''.join(f'<li class="reason">{ico(*marks[i - 1])}<div class="stack s-16"><h3 class="t-ct"><span class="t-num">0{i}</span>{t}</h3><p class="t-body">{b}</p></div></li>' for i, (t, b) in enumerate(reasons, 1))
    day = f'''<section id="day" class="band sec-2" aria-labelledby="day-title"><div class="wrap pad-band"><div class="g57">
<div class="stk">{lab('On the day')}</div>
<div class="stack s-48">
<h2 class="t-h2" id="day-title" data-rv>当日、ご担当者は配信に<br>かかりきりにならずに済みます</h2>
<p class="t-lead">登壇者を迎え、進行を見守り、来賓に挨拶する。<br>{mk('配信の実務はスタッフ2名にお任せください。')}</p>
<ul class="reasons">{rs}</ul>
<div class="boxg stack" style="color:var(--ink)"><h3 class="t-h2s">止まらないとは言いません。止まったときにどう戻すかを、事前にお渡しします</h3>
<p class="t-note">事前に「復旧手順書」を1枚お渡しします。何が止まったら、誰が、何分で、どう復旧するかを明記しています。</p>
<div class="ph" style="background:var(--paper)">［画像：復旧手順書の実物　穴埋め08］</div></div>
</div></div></div></section>'''

    tools = [('S01', 'QA Board の画面', '質疑応答：QA Board', '会場とオンラインからの質問を1か所に集め、選んだ質問だけを登壇者の画面に表示します。', 'コード ［000］　質問を送ると、上の画面に表示されます'),
             ('S02', 'Que の画面', '進行管理：Que', '残り時間と合図を、登壇者とスタッフのスマホに表示します。進行の遅れを防ぎます。', '読み取ると、デモの進行表が開きます'),
             ('S03', 'Movie Switcher の画面', '記録映像の作成：Movie Switcher', '3台のカメラの映像から、話している人に合わせて切り替えた記録映像と字幕を作ります。', '')]
    tl = ''.join(f'<li class="hi stack s-16"><div class="zoom">{img(c, "（ダミー）" + a)}</div><h3 class="t-ct">{t}</h3><p class="t-body">{b}</p>'
                 + (f'<p class="t-note t-sub">［QR］　{n}</p>' if n else '') + '</li>' for c, a, t, b, n in tools)
    demo = f'''<section id="demo" class="sec" aria-labelledby="demo-title"><div class="wrap"><div class="g57"><div class="stk">{lab('Demo')}</div>
<div class="stack s-48"><h2 class="t-h2" id="demo-title" data-rv>現場で使っている道具を、<br>いま試せます</h2><p class="t-lead">お手元のスマホでお試しください。<br>当日の質疑応答と進行がどう進むかを確認できます。</p></div></div>
<ul class="hs mtl" aria-label="道具の一覧">{tl}</ul>
<p class="t-note t-sub mtl">これらの道具は、当日私たちが用意して操作します。ご自身で使えるようになりたい方には、<a href="#coaching">コーチング</a>をご用意しています。　［穴埋め09：デモ環境］</p>
</div></section>'''

    works = f'''<section id="works" class="sec" aria-labelledby="works-title"><div class="wrap"><div class="g57"><div class="stk">{lab('Case Study')}</div>
<div class="stack s-48"><h2 class="t-h2" id="works-title" data-rv>事例：人数も、機材も、<br>金額も公開しています</h2><p class="t-lead">{mk('すべての事例を同じ項目で掲載しています。')}<br>ご自身の会に近いものを探してみてください。</p></div></div></div>
<div class="mtl">
{case(1, '', 'P02', [('P02', '（ダミー）パネルディスカッション全体'), ('P06', '（ダミー）客席後方のカメラ'), ('P07', '（ダミー）ミキサーとマイク'), ('P08', '（ダミー）配信卓とモニター'), ('P10', '（ダミー）会場からの質問'), ('P11', '（ダミー）受付と案内表示'), ('P12', '（ダミー）開場前の設営')], '（映像1名、音声・配信1名）')}
{case(2, '', 'P03', [('P03', '（ダミー）会場全体'), ('P01', '（ダミー）話している人のアップ'), ('P09', '（ダミー）オンライン登壇者の映る画面'), ('P07', '（ダミー）ミキサーとマイク'), ('P06', '（ダミー）客席後方のカメラ'), ('P12', '（ダミー）開場前の設営'), ('P10', '（ダミー）会場からの質問')], '')}
{case(3, '', 'P10', [('P10', '（ダミー）会場からの質問'), ('P02', '（ダミー）パネルディスカッション全体'), ('P08', '（ダミー）配信卓とモニター'), ('P11', '（ダミー）受付と案内表示'), ('P01', '（ダミー）話している人のアップ'), ('P06', '（ダミー）客席後方のカメラ'), ('P03', '（ダミー）会場全体')], '')}
</div>
<div class="wrap mtl"><blockquote class="boxw stack" style="max-width:48rem"><p class="t-lead">［頼む前に不安だったこと、当日どうだったか。2〜3行］</p><footer class="t-note t-sub">［所属・役職・氏名（掲載できる範囲）］</footer></blockquote></div>
</section>'''

    opts = [('P13', '記録写真の撮影', '記録写真', '報告書や広報に使える写真を、専任カメラマン1名が撮影します'),
            ('P14', '記録映像の編集', '記録映像の編集（アーカイブ編集）', '話している人に合わせて画面を切り替えた記録映像を、字幕つきで作成します'),
            ('P15', 'ダイジェスト映像', '2分のダイジェスト映像', '次回の告知や、成果報告に使える短いまとめ映像を作ります'),
            ('P16', '文字起こしと報告書', '文字起こし', '報告書の下書きにそのまま使えるテキストデータを作成します')]
    ol = ''.join(f'<li class="hi stack s-16"><p class="t-num">0{i}</p><h3 class="t-ct">{t}</h3><div class="zoom">{img(c, "（ダミー）" + a)}</div><p class="t-body">{b}</p></li>' for i, (c, a, t, b) in enumerate(opts, 1))
    option = f'''<section id="option" class="bandg sec-2" aria-labelledby="option-title"><div class="wrap pad-band"><div class="g57"><div class="stk">{lab('Option')}</div>
<div class="stack s-48"><h2 class="t-h2" id="option-title" data-rv>カメラマンは、<br>すでに会場にいます</h2><p class="t-lead">記録写真も、記録映像も、同じ日にまとめてご依頼いただけます。<br>見積も請求も打ち合わせも1回で済みます。</p></div></div>
<ul class="hs w40 mtl" aria-label="同じ日に頼めること">{ol}</ul>
<div class="g57 mtl"><div class="stack s-48"><h3 class="t-bar">まるごと</h3><p class="t-big2">［40<small>万円］（税別）</small></p></div>
<div class="stack s-56"><p class="t-lead">スタンダードに上の4つを加えて、スタッフ3名で伺います。<br>一回の現場で、報告書の素材まで揃います。</p>{btn('まるごとプランで見積書を受け取る', 'contact.html')}</div></div>
</div></section>'''

    steps = [('相談', '［3万円］', 'オンライン60分。機材と接続の図、当日のチェックリストを作成します'), ('同行', '［代行＋3万円］', '私たちの配信現場に入り、実際の動きを横で見て覚えます'),
             ('伴走', '［12万円］', 'ご自身で配信を操作し、私たちは横で待機します'), ('卒業', '［5万円］', '事前の機材点検と、当日のオンライン待機だけで見守ります')]
    st = ''.join(f'<li><span class="n">0{i}</span><span class="a">{a} <small>{f}</small></span><span class="b">{b}</span></li>' for i, (a, f, b) in enumerate(steps, 1))
    coaching = f'''<section id="coaching" class="sec" aria-labelledby="coaching-title"><div class="wrap"><div class="g57"><div class="stk">{lab('Coaching')}</div>
<div class="stack s-48"><h2 class="t-h2" id="coaching-title" data-rv>来年度からは<br>自分たちで配信する</h2><p class="t-lead">小さい会はご自身で、大きい会だけ私たちにお任せください。<br>{mk('手順書とチェックリストが残る')}ので、担当者が替わっても引き継げます。</p>
<ol class="steps">{st}</ol>
<div class="btns">{btn('コーチングについて相談する', 'contact.html', 'line')}</div></div></div></div></section>
<section class="sec-3" aria-label="オンライン相談"><div class="wrap"><div class="boxd cta-in"><div class="stack"><p class="t-h2s">まだ何も決まっていない方へ</p>
<p class="t-note">15分のオンライン相談で、iPhoneで足りるかどうかから一緒にお話しします。決まっているのが日程だけでもかまいません。</p></div>
<div>{btn('相談の日時を選ぶ', 'contact.html#consult', 'xl')}</div></div></div></section>'''

    flow = [('問い合わせ', '決まっているのは日程と会場だけでかまいません'), ('見積書', '1営業日以内に、宛名入りのPDFでお送りします'), ('打ち合わせと会場確認', 'オンラインで30分の打ち合わせと、会場の下見を行います'),
            ('本番', '当日、スタッフ2名で会場に伺います'), ('納品と請求', '完了報告書、納品書、請求書をまとめてお送りします')]
    fl = ''.join(f'<li><span class="n">0{i}</span><span class="a">{a}</span><span class="b">{b}</span></li>' for i, (a, b) in enumerate(flow, 1))
    public = f'''<section id="public" class="band sec-2" aria-labelledby="public-title"><div class="wrap pad-band"><div class="g57"><div class="stk">{lab('For public sector')}</div>
<div class="stack s-64"><div class="stack s-48"><h2 class="t-h2" id="public-title" data-rv>大学・公共機関の<br>発注手続きに合わせます</h2><p class="t-lead">稟議や相見積に必要な書類を、<br>{mk('お問い合わせの前からご用意しています。')}</p></div>
<ol class="steps">{fl}</ol>
<div class="stack"><h3 class="sub">書類と支払い</h3><ul class="rows"><li>見積書・納品書・請求書の3点を発行します</li><li>請求書払い（後払い）に対応しています</li><li>インボイス登録番号：［T0000000000000］</li><li>相見積のための見積依頼も歓迎します</li></ul></div>
<form id="spec" class="boxg stack" style="color:var(--ink)" data-form="spec" data-endpoint="" aria-labelledby="spec-title">
<h3 class="t-h2s" id="spec-title">仕様書のひな形を、そのまま使えます</h3>
<p class="t-note">配信業務の仕様書（A4 1枚、Word形式）と、見積書の見本をお送りします。他社への相見積にもそのままお使いください。</p>
<div class="fld"><label for="spec-mail">メールアドレス<span class="req">必須</span></label><input id="spec-mail" name="email" type="email" placeholder="name@example.ac.jp" required autocomplete="email" aria-describedby="spec-mail-e"><p class="err" id="spec-mail-e">メールアドレスの形で入力してください</p></div>
<button class="btn full" type="submit">ひな形を受け取る</button>
<p class="form-msg" role="status" hidden></p></form>
</div></div></div></section>'''

    fq = ''.join(f'<details name="faq"><summary><span class="qa-mk qa-mk--q" aria-hidden="true">Q</span>{q}</summary><div class="ans"><span class="qa-mk qa-mk--a" aria-hidden="true">A</span><p class="t-body">{a}</p></div></details>' for q, a in FAQ)
    faq = f'''<section id="faq" class="sec" aria-labelledby="faq-title"><div class="wrap"><div class="g57"><div class="stk">{lab('FAQ')}</div>
<div class="stack s-48"><h2 class="t-h2" id="faq-title" data-rv>よくある質問</h2><div class="faq">{fq}</div></div></div></div></section>'''

    body = (head(f'シンポジウム・講演会のハイブリッド配信代行｜3カメ・2名・25万円〜｜{NAME}',
                 '大学や公共機関のシンポジウム、公開講座をハイブリッドで配信します。3カメラ・スタッフ2名・マイク5本までで25万円（税別）から。8問のプラン診断で、合うプランと費用がわかります。', home=True)
            + intro + header(True, sub) + '<main id="main">' + hero + switching + clients + scope + price + team + day + demo + works + option + coaching + public + faq + '</main>'
            + footer(True))
    return body

def contact():
    flow = [('1営業日以内', '見積書PDFがメールで届きます'), ('必要に応じて', 'オンラインで30分ほど打ち合わせをします'), ('ご発注後', '事前に会場を下見します')]
    fl = ''.join(f'<li><span class="n">0{i}</span><span class="a">{a}</span><span class="b">{b}</span></li>' for i, (a, b) in enumerate(flow, 1))
    doc = '''<div class="doc-sample"><table><caption>御見積書（見本）</caption>
<tr><th>ハイブリッド配信 スタンダード<br><small>配信3時間まで、会場での作業6時間まで</small></th><td class="r">250,000</td></tr>
<tr><th>映像担当 1名／音声・配信担当 1名</th><td class="r">含む</td></tr><tr><th>カメラ3台／マイク5本まで</th><td class="r">含む</td></tr>
<tr><th>予備の録画機・予備の回線</th><td class="r">含む</td></tr><tr><th>打ち合わせ・会場の下見・録画データの納品</th><td class="r">含む</td></tr>
<tr><th>消費税（10%）</th><td class="r">25,000</td></tr><tr><th>合計</th><td class="r">275,000</td></tr></table></div>'''
    return (head(f'お問い合わせ・お見積｜ハイブリッド配信のご相談｜{NAME}', '日程と会場、登壇者の人数がわかれば見積書をお出しします。1営業日以内に、宛名入りの見積書PDFをメールでお送りします。')
            + header(False, [('top', '見積を依頼する'), ('flow', '送信後の流れ'), ('sample', '見積書の見本'), ('consult', '見積の前に相談する'), ('tel', '電話で問い合わせる')]) + f'''<main id="main">
<div class="wrap ph-head stack s-48" id="top"><nav aria-label="パンくず"><ol class="crumb"><li><a href="index.html">トップ</a></li><li aria-current="page">お問い合わせ・お見積</li></ol></nav>
{lab('Contact')}<h1 class="t-h1">見積書をお送りします</h1><p class="t-lead">{mk('必須の4項目だけ')}で送信できます。1営業日以内に、宛名入りの見積書PDFをメールでお送りします。</p></div>
<div class="wrap g75">
{quote_form('c', prefill=True, full=True)}
<aside class="stack s-48" aria-label="補足">
<section class="stack" id="flow"><h2 class="sub">送信したあとの流れ</h2><ol class="steps">{fl}</ol></section>
<section class="stack" id="sample"><h2 class="sub">届く見積書の見本</h2>{doc}</section>
<section id="consult" class="boxd stack"><h2 class="t-h2s">まだ何も決まっていない方へ</h2><p class="t-note">15分のオンライン相談で、iPhoneで足りるかどうかから一緒にお話しします。</p>{btn('相談の日時を選ぶ', '#consult', 'light')}</section>
<section id="tel" class="stack s-16"><h2 class="sub">お電話でも受け付けています</h2><p class="t-ct">［電話番号］</p><p class="t-note t-sub">［受付時間］</p></section>
<blockquote class="boxw stack"><p class="t-body">［担当者の声を1件。頼む前の不安に触れているもの］</p><footer class="t-note t-sub">［所属・役職］</footer></blockquote>
</aside></div>
</main>''' + footer(False, form=False))

def thanks():
    flow = [('いまここ', '見積のご依頼を受け付けました'), ('1営業日以内', '見積書PDFがメールで届きます'), ('そのあと', '必要に応じて30分の打ち合わせを行い、ご発注後に会場を下見します')]
    fl = ''.join(f'<li{" class=\"now\"" if i == 0 else ""}><span class="a">{a}</span><span class="b">{b}</span></li>' for i, (a, b) in enumerate(flow))
    return (head(f'送信が完了しました｜{NAME}', 'お見積のご依頼を受け付けました。')
            + header(False) + f'''<main id="main">
<p class="form-msg" style="text-align:center">これは送信完了ページの見本です。フォームの送信先がまだ設定されていないため、実際には何も送信されていません。</p>
<div class="wrap ph-head stack s-48">{lab('Thanks')}<h1 class="t-h1">ご依頼を受け付けました</h1>
<p class="t-lead">1営業日以内に、宛名入りの見積書PDFをメールでお送りします。確認メールが届かない場合は、［電話番号］までご連絡ください。</p>
<ol class="flow">{fl}</ol></div>
<section class="bandg sec-2" aria-labelledby="dl-title"><div class="wrap pad-band stack s-48"><h2 class="t-h2" id="dl-title">お待ちいただく間に、<br>稟議の準備にお使いください</h2>
<p class="t-lead">上司への説明や相見積にそのまま使える書類です。どれも登録なしでダウンロードできます。</p>
<ul class="stack s-16"><li>{btn('仕様書のひな形（Word）［ファイル準備中］', 'thanks.html', 'line')}</li><li>{btn('料金表と見積書見本（PDF）［ファイル準備中］', 'thanks.html', 'line')}</li><li>{btn('当日のチェックリスト（PDF）［ファイル準備中］', 'thanks.html', 'line')}</li></ul></div></section>
<div class="wrap sec-3"><a class="tlink" href="index.html">トップページへ戻る</a></div>
</main>''' + footer(False, form=False))

def rules():
    css = (OUT / 'assets/site.css').read_text(encoding='utf-8')
    apis = [
        ('&lt;dialog&gt;（showModal）', 'Widely', 'スマホのメニュー。フォーカスを閉じ込め、Esc で閉じる', '— （JS が動かないときは、ヘッダーの「メニュー」がフッターのメニューへ移動）'),
        ('&lt;details&gt; / &lt;summary&gt;', 'Widely', 'よくある質問の開閉', '—'),
        ('details[name]（1つだけ開く）', 'Newly（2024-09）', '開いた質問以外を閉じる', '未対応では、複数同時に開けるだけ'),
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
    tokens = re.findall(r'--(bg|paper|cream|wash|ink|ink-2|sand|sub|teal|coral|yellow|marker): (#[0-9a-f]{6});', css)
    names = {'bg': '地：ページの背景（白）', 'paper': '紙：白い地に置く箱、フォーム', 'cream': 'クリーム：帯、囲み', 'wash': '淡いティール：帯', 'ink': '文字：見出し・本文、フッター', 'ink-2': '濃い文字：強調', 'sand': '罫線', 'sand-d': '補足の線', 'sub': '補足の文字（黒50%）', 'red': '配信中・必須の印（珊瑚）', 'teal': 'ティール（主色）：目次の現在地・ボタン・診断・アイコン', 'teal-ink': 'ティール：地の上の文字', 'coral': '珊瑚：見積に進む・Q・番号', 'coral-ink': '珊瑚：見積に進むボタン', 'yellow': '黄：プラン診断・アイコン', 'marker': 'マーカー：要点の下線'}
    sw = ''.join(f'<li class="stack s-16"><span style="display:block;block-size:4rem;border-radius:6px;background:{v};box-shadow:inset 0 0 0 1px rgb(0 0 0 / .08)"></span><span class="t-note"><b>{v.upper()}</b><br>{names[k]}</span></li>' for k, v in tokens)
    type_rows = [('大見出し', '26 → 50', 'カメラ5台はいりません。'), ('セクション見出し', '26 → 44', '事例を公開しています'), ('囲みの見出し', '18 → 28', '日程と会場だけ'),
                 ('小見出し', '18 → 26', '持ち込む機材の内訳'), ('カードの題・質問', '16 → 20', '登壇者は何人ですか'), ('リード', '14 → 18', '登壇者を迎え、進行を見守る。'),
                 ('本文', '14 → 16', 'マイク音声を直接取り込みます。'), ('補足', '12 → 14', '相見積にそのまま使えます')]
    ty = ''.join(f'<tr><th scope="row">{a}</th><td data-l="大きさ（px）">{b}</td><td data-l="見本">{c}</td></tr>' for a, b, c in type_rows)
    return (head(f'デザインルール｜{NAME}', 'カルラライブのサイトのデザインルールと、使っている Web 標準の一覧です。')
            + header(False, [('rules-top', 'このページについて'), ('layout', '画面の組み方'), ('type', '文字の大きさと字間'), ('color', '色の役割'), ('marks', '目印と影'), ('motion', '動きの決まり'), ('platform', '使っているWeb標準')]) + f'''<main id="main"><div class="wrap ph-head stack s-48" id="rules-top">{lab('Design rules')}<h1 class="t-h1">白い地に、<br>ティールで道しるべを置く。</h1>
<p class="t-lead">C案を元に、スマホを基本に組み直したサイトのルールです。色・影・目印は recruit.handy.school の仕組みを参考にしています。文字と余白は、幅390pxのスマホから1200pxのPCまで、段差なく大きくなります。</p></div>
<section class="sec-3" id="layout"><div class="wrap g57"><div class="stk">{lab('Layout')}</div><div class="stack s-48"><h2 class="t-h2">スマホは1段、PCは左のレール＋2段</h2>
<ul class="rows"><li>スマホを基本に書き、幅1024px以上で広げます</li><li>PCは左に幅200pxの固定レールを置きます。上からロゴ、現在地つきの目次（単語ではなく「何が書いてあるか」がわかる言葉で）、2つの行動（黄＝8問でプラン診断、濃い珊瑚＝見積を依頼する）、ページの切り替え。右端の細い線が、ページを読み進めた量です</li><li>スマホでは上のバーと現在地つきのサブナビが一緒に追従し、下部に追従ボタン（プラン診断／見積を依頼する）を置きます。目次の中身はPCのレールと同じです</li><li>本文はレールの右で、左5：右7の2段</li><li>プラン診断はトップの最初の画面に置きます。PCでは見出しの右でその場で答え、スマホでは見出しのすぐ下の黄色いボタンから全画面のモーダル（dialog）で開きます。サブナビや下部の「プラン診断」からも同じモーダルが開きます</li></ul></div></div></section>
<section class="sec-3" id="type"><div class="wrap g57"><div class="stk">{lab('Type')}</div><div class="stack s-48"><h2 class="t-h2">1書体、1つの太さ</h2>
<table class="tbl"><thead><tr><th scope="col">役割</th><th scope="col">大きさ（px、スマホ → PC）</th><th scope="col">見本</th></tr></thead><tbody>{ty}</tbody></table>
<p class="t-note t-sub">和文：Zen Kaku Gothic New の Medium（使う文字だけに絞って同梱）／英字・数字：Helvetica Neue。入力欄の文字はスマホでも16px。字間は大きさの2%、本文とリードの行送りは1.8、見出しは1.45。</p></div></div></section>
<section class="sec-3" id="color"><div class="wrap g57"><div class="stk">{lab('Color')}</div><div class="stack s-48"><h2 class="t-h2">白の地に、主色のティール</h2>
<ul class="logos" style="grid-template-columns:repeat(auto-fill,minmax(9rem,1fr))">{sw}</ul>
<ul class="rows"><li>主色はティール。目次の現在地、ラベルの四角、一覧の見出しの下線、手順の番号、診断で選んだ答え、プラン名の帯に使います</li>
<li>珊瑚は「行動」と「数える」もの：見積に進むボタン、よくある質問のQ、送信後の流れの「いまここ」</li>
<li>黄は「気軽さ」と「要点」：プラン診断のボタン、要点のマーカー</li>
<li>地は白。セクションの面はクリーム（#F8F6F3）とティールの淡い色（#F2FBFC）の2つだけで、どちらも参考サイトの半透明の色を白に重ねた値です</li>
<li>差し色は小さな面にだけ使い、大きな面は白・クリーム・淡いティールのまま。ボタンやラベルの四角は参考サイトどおり、差し色の上に白い文字を乗せます</li>
<li>キーボードで操作しているときの枠は、見落とさないよう黄色（#FACA00）</li></ul></div></div></section>
<section class="sec-3" id="marks"><div class="wrap g57"><div class="stk">{lab('Marks &amp; Shadow')}</div><div class="stack s-48"><h2 class="t-h2">目が滑らないための目印</h2>
<p class="t-lead">長いページでも読む場所を見失わないよう、4つの目印を決まった場所にだけ置きます。</p>
<ul class="reasons">
<li class="reason">{ico('check', 'teal')}<div class="stack s-16"><h3 class="t-ct">{mk('要点のマーカー')}</h3><p class="t-body">各セクションのリードで、いちばん伝えたい一文にだけ引きます。1つのセクションに1か所まで。文字の下半分を黄色（#FFEB78）にし、画面に入ったときに左から引かれます</p></div></li>
<li class="reason">{ico('doc', 'coral')}<div class="stack s-16"><h3 class="t-ct">影は3段だけ</h3><p class="t-body">ずらさずに広げる影：置いてあるもの（カード、白い箱）は 0 0 30px 黒8%、色の面（レールの行動ボタン、開いた質問）は 0 0 30px 黒10%、物として見せるもの（見積書の見本、暗い囲み）は 0 5px 40px 黒20%。ボタンには影を付けません</p></div></li>
<li class="reason">{ico('switch', 'yellow')}<div class="stack s-16"><h3 class="t-ct">色の角丸アイコン</h3><p class="t-body">線画のアイコンを、差し色の角丸の四角（44px、角丸10px）に入れます。一覧の頭や、要点のチェックに使います。飾りなので、読み上げからは外します。英字の小さなラベルは付けません</p></div></li>
<li class="reason">{ico('backup', 'teal')}<div class="stack s-16"><h3 class="t-ct">QとA、○と—</h3><p class="t-body">よくある質問は珊瑚のQとティールのA。お引き受けする会はティールの○、ほかの方法をおすすめする会は灰色の—で、読む前に種類がわかるようにします</p></div></li>
</ul>
<p class="t-note t-sub">穴埋め（［ ］）はマーカーと見分けがつくよう、灰色の斜線にしています。</p></div></div></section>
<section class="sec-3" id="motion"><div class="wrap g57"><div class="stk">{lab('Motion')}</div><div class="stack s-48"><h2 class="t-h2">動きは、減らせる</h2>
<ul class="rows"><li>押せるものの反応は 0.3秒、cubic-bezier(0.4, 0.4, 0, 1) にそろえます</li><li>要点のマーカーは 0.8秒で引きます。幕や出現の動きは cubic-bezier(0.19, 1, 0.22, 1)</li><li>読み込みの幕は、その回の最初の1回だけ。2回目からは出ません</li><li>カメラの自動切り替えには「切り替えを止める」ボタンをつけています</li><li>端末で「視差効果を減らす」を選んでいる人には、幕・自動切り替え・流れる英字・出現の動き・マーカーの動きをすべて止めます（マーカーは最初から引いた状態）</li></ul></div></div></section>
<section class="sec-3" id="platform"><div class="wrap g57"><div class="stk">{lab('Platform')}</div><div class="stack s-48"><h2 class="t-h2">使っている Web 標準と、使えないときの形</h2>
<p class="t-lead">基準は Baseline Widely available（主要ブラウザで30か月以上使えるもの）。それより新しい機能は、無くても見た目と操作が壊れない場所にだけ使っています。</p>
<table class="tbl"><thead><tr><th scope="col">機能</th><th scope="col">Baseline（2026年11月）</th><th scope="col">使っている場所</th><th scope="col">使えないとき</th></tr></thead><tbody>{tr}</tbody></table>
<p class="t-note t-sub">「Widely」は主要ブラウザで30か月以上、「Newly」は主要ブラウザの最新版で使えるもの、「Limited」は一部のブラウザだけ。</p></div></div></section>
</main>''' + footer(False, form=False))

PAGES = {'index.html': index, 'contact.html': contact, 'thanks.html': thanks, 'rules.html': rules}
if __name__ == '__main__':
    for name, fn in PAGES.items():
        html = mark(fn())
        (OUT / name).write_text(html, encoding='utf-8')
        print(name, len(html), 'holes', len(ANA.findall(re.sub(r'<[^>]+>', ' ', html))))
