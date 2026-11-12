#!/usr/bin/env python3
"""カルラライブ サービスサイトの書き出し。

  python3 build.py            -> dist/（公開用の複数ページ）と preview/（1ファイルの確認用）
設定は下の CFG だけ。ドメインやフォームの送信先が決まったら、ここを書き換えて作り直す。
"""
import json, re, shutil, html
from pathlib import Path

ROOT = Path(__file__).parent
CFG = dict(
    name='カルラライブ',
    alt='Karura Live',
    url='https://example.jp',          # ドメインが決まったら差し替える
    area='新宿から90分圏内（東京都・神奈川県・埼玉県・千葉県ほか）',
    form_endpoint='',                  # 見積フォームの送信先（空のあいだは何も送信しない）
    template_endpoint='',              # 仕様書ひな形フォームの送信先
)

THEME = ['']   # '' = 標準、'rondo' = 前のデザイン寄りの見た目
LABS = {'price': 'Price', 'safety': 'On the day', 'demo': 'Tools', 'works': 'Works', 'check': 'Check', 'options': 'Options', 'coaching': 'Coaching', 'public': 'For universities', 'faq': 'FAQ'}
_uid = [0]
def uid(p='f'):
    _uid[0] += 1
    return f'{p}{_uid[0]}'

# ------------------------------------------------------------------ 小さな部品
def btn(text, href, cls=''):
    return f'<a class="btn {cls}" href="{href}">{text}</a>'

def img(code, alt, ratio='3/2', lazy=True):
    w, h = {'16/10': (1600, 1000), '4/5': (800, 1000), '3/2': (1200, 800)}[ratio]
    l = ' loading="lazy" decoding="async"' if lazy else ''
    return f'<img src="@@/img/{code}.webp" alt="{alt}" width="{w}" height="{h}"{l}>'

def ticks(items, cls=''):
    return f'<ul class="ticks {cls}">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'

def sec(body, sid='', band='', h2='', lead='', tight=False):
    i = f' id="{sid}"' if sid else ''
    b = f' band--{band}' if band else ''
    t = ' band--tight' if tight else ''
    lab = f'<p class="lab">{LABS[sid]}</p>' if (THEME[0] == 'rondo' and sid in LABS) else ''
    head = (f'<h2 class="h2">{h2}</h2>' if h2 else '') + (f'<p class="lead">{lead}</p>' if lead else '')
    inner = (f'<div class="sec-head">{lab}{head}</div><div class="sec-body">{body}</div>' if head else body)
    return f'<section class="band{b}{t}"{i}><div class="wrap">{inner}</div></section>'

def field(label, ph='', typ='text', name='', req=True, hint='', err=''):
    i = uid()
    r = ' data-req required' if req else ''
    mark = '' if req else ' <small>（任意）</small>'
    e = f'<p class="err" id="{i}e">{err}</p>' if err else ''
    ac = {'email': ' autocomplete="email" inputmode="email"'}.get(typ, '')
    return (f'<div class="field"><label for="{i}">{label}{mark}</label>'
            f'<input id="{i}" name="{name}" type="{typ}" placeholder="{ph}"{r}{ac}>{e}</div>')

FOUR = lambda: (
    field('開催日 <small>（未定でも可）</small>', '例：2027年2月20日', name='開催日', err='開催日を入力してください（「未定」でもかまいません）')
    + field('会場', '例：〇〇大学 △△ホール', name='会場', err='会場を入力してください')
    + field('登壇者と来場者のおおよその人数', '例：登壇4人、来場150人', name='人数', err='おおよその人数を入力してください')
    + field('メールアドレス', 'name@example.ac.jp', typ='email', name='メールアドレス', err='メールアドレスを正しく入力してください'))

def quote_form(strip=False, title='日程と会場だけで、見積書をお送りします',
               text='1営業日以内に、宛名入りの見積書PDFをメールでお送りします。相見積のためのご依頼も歓迎します。'):
    c = ' qform--strip' if strip else ''
    return f'''<form class="qform{c}" data-form="quote" data-endpoint="{CFG['form_endpoint']}" data-thanks="@@page:thanks" aria-label="見積依頼">
<h2 class="qform-h">{title}</h2><p class="qform-p">{text}</p>
<div class="qform-row">{FOUR()}<button class="btn" type="submit">見積書を受け取る</button></div>
<div class="qform-foot"><p class="note">まだ何も決まっていない方は、<a href="@contact#consult">15分のオンライン相談</a>をご利用ください</p></div>
<p class="form-msg" role="status" hidden></p></form>'''

# ------------------------------------------------------------------ 配信画面のイラスト
SPK = [520, 730, 940, 1150]
def person(i, cx):
    cloth = ['#30475e', '#6d5a48', '#3f5f54', '#4b4559'][i]
    hair = ['#2b2623', '#8f9290', '#3a2e27', '#1f1f22'][i]
    skin = ['#ecd2bb', '#e6c7ab', '#f0d9c4', '#e1c2a4'][i]
    if i == 2:
        h = f'<path d="M{cx-35} 506C{cx-44} 424 {cx+44} 424 {cx+35} 506L{cx+30} 468C{cx+16} 450 {cx-16} 450 {cx-30} 468Z" fill="{hair}"/>'
    else:
        h = f'<path d="M{cx-32} 472C{cx-36} 430 {cx+36} 430 {cx+32} 472C{cx+20} 452 {cx-18} 450 {cx-32} 472Z" fill="{hair}"/>'
    glasses = (f'<g fill="none" stroke="#2b2623" stroke-width="2"><circle cx="{cx-11}" cy="478" r="7"/><circle cx="{cx+11}" cy="478" r="7"/><path d="M{cx-4} 478h8"/></g>' if i == 1 else '')
    return f'''<g>
<path d="M{cx-72} 616C{cx-72} 548 {cx-42} 528 {cx} 528C{cx+42} 528 {cx+72} 548 {cx+72} 616Z" fill="{cloth}"/>
<path d="M{cx-17} 529L{cx} 558L{cx+17} 529Z" fill="#f4f5f2"/>
<rect x="{cx-11}" y="500" width="22" height="32" fill="{skin}"/>
<ellipse cx="{cx}" cy="474" rx="31" ry="35" fill="{skin}"/>
{h}<circle cx="{cx-11}" cy="478" r="2.6" fill="#2b2623"/><circle cx="{cx+11}" cy="478" r="2.6" fill="#2b2623"/>{glasses}
<g class="talk t{i}" fill="none" stroke="#cf3a26" stroke-width="4" stroke-linecap="round"><path d="M{cx+46} 470q9 11 0 22"/><path d="M{cx+58} 461q17 20 0 40"/></g>
</g>'''

def desk_items(cx):
    return f'''<rect x="{cx-36}" y="570" width="72" height="21" fill="#fff" stroke="#c4cac5"/><path d="M{cx-22} 581h44" stroke="#8a948f" stroke-width="3"/>
<path d="M{cx+50} 591Q{cx+52} 560 {cx+33} 549" stroke="#2b2f2d" stroke-width="3.5" fill="none"/><rect x="{cx+20}" y="540" width="16" height="10" rx="5" fill="#2b2f2d" transform="rotate(-28 {cx+28} 545)"/>'''

def scene_defs():
    people = ''.join(person(i, cx) for i, cx in enumerate(SPK))
    items = ''.join(desk_items(cx) for cx in SPK)
    row1 = ''.join(f'<g transform="translate({x} 0)"><ellipse cx="0" cy="812" rx="27" ry="30"/><path d="M-52 900C-52 850 52 850 52 900Z"/></g>' for x in range(30, 1640, 92))
    row2 = ''.join(f'<g transform="translate({x} 0)"><ellipse cx="0" cy="868" rx="34" ry="38"/><path d="M-66 960C-66 900 66 900 66 960Z"/></g>' for x in range(84, 1700, 118))
    return f'''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<g id="sld"><rect width="1600" height="900" fill="#fff"/><rect width="1600" height="28" fill="#153b33"/>
<text x="110" y="196" font-size="76" font-weight="900" fill="#1c2220">地域連携の成果と課題</text><rect x="110" y="246" width="420" height="10" fill="#cf3a26"/>
<g fill="#aab3ad"><rect x="110" y="344" width="560" height="26" rx="3"/><rect x="110" y="414" width="470" height="26" rx="3"/><rect x="110" y="484" width="520" height="26" rx="3"/><rect x="110" y="554" width="350" height="26" rx="3"/></g>
<g fill="#153b33"><rect x="870" y="580" width="92" height="180"/><rect x="1000" y="500" width="92" height="260"/><rect x="1130" y="540" width="92" height="220"/><rect x="1260" y="380" width="92" height="380"/></g><rect x="1390" y="290" width="92" height="470" fill="#cf3a26"/>
<rect x="840" y="760" width="670" height="5" fill="#1c2220"/><text x="110" y="826" font-size="32" fill="#8a948f">第3回 公開シンポジウム</text></g>
<g id="scn" class="spk-0">
<rect width="1600" height="900" fill="#dde4de"/><rect y="452" width="1600" height="200" fill="#cdd7cf"/><rect width="150" height="652" fill="#bcc8bf"/><rect x="1450" width="150" height="652" fill="#bcc8bf"/>
<rect x="490" y="86" width="620" height="358" fill="#2b2f2d"/><g transform="translate(500 96) scale(.375)"><use href="#sld"/></g>
<rect y="640" width="1600" height="110" fill="#bfa983"/><rect y="742" width="1600" height="10" fill="#a08a64"/>
<g><path d="M186 700C186 560 206 528 250 528C294 528 314 560 314 700Z" fill="#55605a"/><path d="M234 529L250 556L266 529Z" fill="#f4f5f2"/><rect x="239" y="500" width="22" height="32" fill="#e8cdb5"/><ellipse cx="250" cy="474" rx="31" ry="35" fill="#e8cdb5"/><path d="M218 472C214 430 286 430 282 472C270 452 232 450 218 472Z" fill="#4a3d35"/><circle cx="239" cy="478" r="2.6" fill="#2b2623"/><circle cx="261" cy="478" r="2.6" fill="#2b2623"/></g>
<rect x="184" y="566" width="132" height="14" fill="#7d6a4b"/><path d="M194 580h112l-9 160h-94z" fill="#8f7a58"/>
{people}
<rect x="400" y="590" width="870" height="17" fill="#fbfcfa"/><rect x="406" y="607" width="858" height="120" fill="#eceee9"/><path d="M620 607v120M835 607v120M1050 607v120" stroke="#dfe2dc" stroke-width="3"/>
{items}
<rect y="752" width="1600" height="148" fill="#26403a"/><g fill="#16282a">{row1}</g><g fill="#0d1c1c">{row2}</g>
</g></defs></svg>'''

def switcher(sub=False):
    def tile(src, vb, a, b, use='scn'):
        return (f'<button type="button" class="sw-tile" data-src="{src}" aria-pressed="false" aria-label="{a} {b}に切り替える">'
                f'<svg viewBox="{vb}" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><use href="#{use}"/></svg><span><b>{a}</b><i>{b}</i></span></button>')
    s = '<p class="sw-sub" aria-hidden="true"></p>' if sub else ''
    return f'''<div class="sw" data-sw>
<div class="sw-top"><p>配信画面のイメージ</p><div class="seg" role="group" aria-label="カメラの台数を切り替える"><button type="button" data-cams="1" aria-pressed="false">カメラ1台だと</button><button type="button" data-cams="3" aria-pressed="true">カメラ3台だと</button></div></div>
<div class="sw-pgm" role="img" aria-label="パネルディスカッションの配信画面のイラスト。話している人に合わせてカメラが切り替わる">
<svg class="sw-main" viewBox="320 400 400 225" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><use href="#scn"/></svg>
<svg class="sw-slide is-hid" viewBox="0 0 1600 900" aria-hidden="true"><use href="#sld"/></svg>
<div class="sw-pip" hidden><svg viewBox="320 400 400 225" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><use href="#scn"/></svg></div>
<span class="sw-onair">配信中</span><span class="sw-shot"><b>CAM 1</b>話している人のアップ</span>{s}</div>
<div class="sw-tiles">{tile(1, '320 400 400 225', 'CAM 1', 'アップ')}{tile(2, '360 300 960 540', 'CAM 2', '登壇者')}{tile(3, '0 0 1600 900', 'CAM 3', '会場')}{tile('s', '0 0 1600 900', 'SLIDE', 'スライド', 'sld')}</div>
<p class="sw-cap" aria-live="polite">話す人が替わるたびに、映像担当がカメラ1を向け直して切り替えます。表情まで届きます。</p>
</div>'''

def floor_plan():
    seats = ''
    for r, y in enumerate(range(196, 380, 30)):
        for x in list(range(110, 330, 30)) + list(range(400, 620, 30)):
            seats += f'<rect x="{x}" y="{y}" width="20" height="16" rx="3"/>'
    return f'''<svg viewBox="0 0 720 500" role="img" aria-label="会場の配置図。客席の後ろにカメラ2台と映像担当、後方の端にカメラ1台、配信卓に音声・配信担当。登壇者の机にマイク4本、客席に質問用マイク1本">
<g fill="none" stroke="#eef2ee" stroke-width="1.5"><rect x="14" y="14" width="692" height="472" rx="2"/><rect x="100" y="34" width="520" height="118"/><rect x="250" y="98" width="220" height="24"/><rect x="150" y="96" width="44" height="28"/></g>
<path d="M270 40h180" stroke="#eef2ee" stroke-width="6"/>
<g fill="#eef2ee"><circle cx="280" cy="84" r="9"/><circle cx="333" cy="84" r="9"/><circle cx="387" cy="84" r="9"/><circle cx="440" cy="84" r="9"/><circle cx="172" cy="84" r="9"/></g>
<g fill="#f08a78"><circle cx="280" cy="110" r="5"/><circle cx="333" cy="110" r="5"/><circle cx="387" cy="110" r="5"/><circle cx="440" cy="110" r="5"/><circle cx="360" cy="286" r="6"/></g>
<g fill="#34635a">{seats}</g>
<g stroke="#a8beb5" stroke-width="1.2" stroke-dasharray="5 5" fill="none"><path d="M330 428L333 96"/><path d="M392 428L255 124M392 428L466 124"/><path d="M628 412L104 150M628 412L560 40"/></g>
<g fill="#eef2ee"><path d="M318 446h24l-5-20h-14z"/><path d="M380 446h24l-5-20h-14z"/><path d="M618 430l22-8-16-14z"/></g>
<rect x="452" y="440" width="120" height="28" fill="none" stroke="#eef2ee" stroke-width="1.5"/>
<g><circle cx="361" cy="462" r="13" fill="#cf3a26"/><circle cx="512" cy="424" r="13" fill="#cf3a26"/><g fill="#fff" font-family="Barlow Condensed,sans-serif" font-weight="600" font-size="17" text-anchor="middle"><text x="361" y="468">1</text><text x="512" y="430">2</text></g></g>
<g fill="#eef2ee" font-size="12.5" font-weight="500"><text x="460" y="48">スクリーン</text><text x="482" y="115">登壇者の机</text><text x="126" y="140">司会</text><text x="374" y="291">質問用マイク</text>
<text x="246" y="476" text-anchor="end">カメラ1・2</text><text x="648" y="446">カメラ3</text><text x="512" y="459" text-anchor="middle">配信卓</text><text x="110" y="420">客席</text></g></svg>'''

# ------------------------------------------------------------------ 書類の見本
def quote_doc():
    rows = [
        ('映像担当　1名', 'カメラ3台の操作、配信画面の切り替え'),
        ('音声・配信担当　1名', 'マイクと音量の調整、配信の監視、登壇者PCの接続'),
        ('カメラ　3台', '発表スライドの映像取り込みを含む'),
        ('マイク　5本まで', '会場設備のマイク音声の取り込みを含む'),
        ('予備の録画機・予備のインターネット回線', '録画、回線とも2系統'),
        ('事前の打ち合わせ、会場の下見', ''),
        ('録画データの納品', ''),
    ]
    tr = ''.join(f'<tr><td>{a}<small>{b}</small></td><td class="r">一式に含む</td></tr>' for a, b in rows)
    return f'''<div class="doc">
<span class="doc-stamp">見本</span><p class="doc-title">御見積書</p>
<div class="doc-meta"><p><span class="doc-to">〇〇大学 △△研究科　御中</span><br>件名：公開シンポジウム ハイブリッド配信業務</p><p>カルラライブ<br>登録番号 ［T0000000000000］</p></div>
<div class="doc-sum"><span>お見積金額（税込）</span><b>¥275,000</b></div>
<table><thead><tr><th>内容</th><th class="r">金額（税別）</th></tr></thead>
<tbody><tr><td><b>ハイブリッド配信 スタンダード</b><small>配信3時間まで、会場での作業6時間まで</small></td><td class="r">250,000</td></tr>{tr}</tbody>
<tfoot><tr><td>小計</td><td class="r">250,000</td></tr><tr><td>消費税（10%）</td><td class="r">25,000</td></tr><tr><td>合計</td><td class="r">275,000</td></tr></tfoot></table>
<p class="doc-note">追加料金が発生する条件：配信時間の延長、スタッフの追加、カメラの追加、会場に回線がない場合、対応エリア外の交通費・宿泊費</p></div>'''

def recovery_doc():
    rows = [
        ('会場のインターネット回線が切れた', '音声・配信担当', '予備回線に切り替えて配信を続ける', '［　］分'),
        ('録画機が止まった', '映像担当', 'もう1台の録画機で記録を続ける（常に2系統で録画）', '中断なし'),
        ('マイクの音が出ない', '音声・配信担当', '予備のマイクに交換する。会場設備の音声にも切り替えられる', '［　］分'),
        ('登壇者PCの画面が映らない', '音声・配信担当', '予備のケーブルと変換器に交換する', '［　］分'),
    ]
    tr = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in rows)
    return f'''<div class="doc doc--rec"><span class="doc-stamp">見本</span><p class="doc-title">復旧手順書</p>
<table><thead><tr><th>何が止まったら</th><th>誰が</th><th>どう戻すか</th><th>目安</th></tr></thead><tbody>{tr}</tbody></table>
<p class="doc-note">実物は、会場の設備と回線に合わせて会ごとに作成し、事前にお渡しします。</p></div>'''

# ------------------------------------------------------------------ 診断・デモ
QUIZ_Q = ['登壇者は2人以上いますか', '会場でマイクとスピーカーを使いますか', '会場からの質問を、オンラインの視聴者にも届けたいですか',
          '配信時間は2時間を超えますか', '終了後に録画データ（アーカイブ）を公開しますか', '学外の視聴者や来賓がいますか']
def quiz():
    g = uid('q')
    li = ''
    for n, q in enumerate(QUIZ_Q, 1):
        li += (f'<li><p id="{g}p{n}">{q}</p><div class="yn" role="radiogroup" aria-labelledby="{g}p{n}">'
               f'<label><input type="radio" name="{g}_{n}" value="y"><span>はい</span></label>'
               f'<label><input type="radio" name="{g}_{n}" value="n"><span>いいえ</span></label></div></li>')
    return f'''<div class="quiz"><ol>{li}</ol>
<div class="quiz-foot"><button type="button" class="btn quiz-go">診断結果を見る</button><p class="note quiz-warn" role="alert" hidden>6問すべてにお答えください</p></div>
<div class="quiz-res" tabindex="-1" role="status" hidden>
<div data-res="self"><h3>iPhoneやPCで足ります</h3><p>この条件なら、ご自身で配信できます。業者に頼む必要はありません。</p>
<div class="btns"><a class="btn btn--ghost" href="@iphone-streaming">自分で配信するときの機材と注意点を読む</a></div></div>
<div data-res="consult"><h3>相談だけで済みそうです</h3><p>機材と接続を一度整理すれば、ご自身で配信できる可能性が高い会です。60分の相談で、接続の図と当日のチェックリストを作成します。</p>
<div class="btns"><a class="btn" href="@coaching">コーチングについて見る</a><a class="btn btn--ghost" href="@contact#consult">15分のオンライン相談</a></div></div>
<div data-res="order"><h3>ご依頼をおすすめします</h3><p>ご担当者が配信にかかりきりになる条件がそろっています。カメラ3台・スタッフ2名の体制が合う会です。</p>
<div class="btns"><a class="btn" href="@contact">見積書を受け取る</a><a class="btn btn--ghost" href="@price">料金・体制・機材を見る</a></div></div>
<p class="h4 quiz-why-h" style="margin-top:24px">「はい」と答えた項目で、気をつけること</p><ul class="ticks quiz-why"></ul></div></div>'''

DEMO_TAG = '<p class="demo-tag">動きを体験するための簡易版です。実物は、当日スタッフが用意して操作します。</p>'
def qa_demo():
    i = uid()
    return f'''<div class="demo">{DEMO_TAG}<div class="qa">
<div class="qa-pane"><h4>スタッフの画面：届いた質問</h4>
<form class="qa-in"><label class="vh" for="{i}">質問を入力</label><input id="{i}" type="text" maxlength="80" placeholder="質問を送ってみてください"><button type="submit">送る</button></form>
<ul class="qa-list"><li><div><small>会場</small><span>録画は後日公開されますか。</span></div><button type="button">表示する</button></li>
<li><div><small>オンライン</small><span>調査の対象になった自治体の数を教えてください。</span></div><button type="button">表示する</button></li></ul></div>
<div class="qa-pane"><h4>登壇者に見える画面</h4><div class="qa-screen" aria-live="polite"><p class="is-empty">選んだ質問だけが、ここに表示されます</p></div></div>
</div></div>'''

def que_demo():
    return f'''<div class="demo">{DEMO_TAG}<div class="que">
<div class="phone"><div class="phone-in" aria-live="polite"><small>登壇者のスマホ　残り時間</small><span class="n">5:00</span><p></p></div></div>
<div class="que-ctl"><h4>スタッフの操作</h4><div><button type="button" data-que="start">スタート</button><button type="button" data-que="reset">リセット</button></div>
<h4 style="margin-top:18px">登壇者に合図を送る</h4><div><button type="button" data-que="cue">あと5分です</button><button type="button" data-que="cue">あと1分です</button><button type="button" data-que="cue">まとめに入ってください</button><button type="button" data-que="cue">質疑に移ります</button></div>
<p>合図を押すと、登壇者のスマホに大きく表示されます。声をかけずに進行を伝えられます。</p></div></div></div>'''

# ------------------------------------------------------------------ 事例・FAQ・CTA
def cases():
    out = ''
    for code, alt in [('P02', 'パネルディスカッションの様子'), ('P03', '会場全体の様子'), ('P10', '会場からの質問の様子')]:
        out += f'''<article class="case">{img(code, alt)}<div class="case-in"><h3>［主催機関名］［会の名称］</h3>
<dl><div><dt>会の規模</dt><dd>登壇［　］人、会場［　］人、オンライン視聴［　］人、［　］時間</dd></div>
<div><dt>当日の体制</dt><dd>スタッフ［　］名（映像1名、音声・配信1名）</dd></div>
<div><dt>使用機材</dt><dd>カメラ［　］台、マイク［　］本、予備機材あり</dd></div>
<div><dt>金額</dt><dd>［25万〜30万円］</dd></div>
<div><dt>当日起きたこと</dt><dd>［トラブルと、どう戻したか］</dd></div></dl></div></article>'''
    return f'<div class="cases">{out}</div>'

VOICE = '<blockquote class="voice"><p>［頼む前に不安だったこと、当日どうだったか。2〜3行］</p><footer>［所属・役職・氏名（掲載できる範囲）］</footer></blockquote>'

FAQ_TOP = [
    ('何日前までに頼めば間に合いますか', '［最短の日数と、繁忙期の目安］'),
    ('Zoom、YouTube、Teamsのどれに対応していますか', '［対応している配信先］'),
    ('登壇者の一部がオンラインから参加します', '対応できます。スタッフを1名追加します（［金額］）。'),
    ('会場にインターネット回線がありません', '配信用の回線を持ち込みます（［金額］）。事前に会場で電波状況を確認します。'),
    ('配信が止まった場合、料金はどうなりますか', '［返金・減額の規定］'),
    ('対応エリアはどこまでですか', '新宿駅からおおむね90分以内で伺える会場が対応エリアです。エリア内は、会場の下見も交通費も25万円に含まれます。エリア外の会場は、交通費と宿泊費の実費で伺います。'),
]
FAQ_MORE = [
    ('会場の下見は必要ですか', '必要です。スタンダードに含まれています。電源、回線、会場設備のマイク、カメラを置く位置を事前に確認します。'),
    ('録画データはもらえますか', 'はい。録画データの納品はスタンダードに含まれています。話している人に合わせて切り替えた記録映像や字幕が必要な場合は、オプションの「記録映像の編集」をご利用ください。'),
    ('iPhoneで足りる会かどうか、先に知りたい', '<a href="@check">6問の診断</a>でご確認いただけます。iPhoneで足りる会なら、そうお伝えします。'),
    ('相見積のための見積依頼でもかまいませんか', '歓迎します。<a href="@public#template">仕様書のひな形</a>と見積書の見本もお送りしますので、他社への依頼にもそのままお使いください。'),
    ('支払い方法を教えてください', '請求書払い（後払い）に対応しています。見積書・納品書・請求書の3点を発行します。'),
    ('小さい会は自分たちで配信できるようになりたい', '<a href="@coaching">配信コーチング</a>をご用意しています。相談、同行、伴走、卒業の4段階で、手順書とチェックリストが手元に残ります。'),
]
def faq(items):
    return '<div class="faq">' + ''.join(f'<details><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in items) + '</div>'

def cta(title='日程と会場だけ、教えてください', text='1営業日以内に、宛名入りの見積書PDFをメールでお送りします。', label='見積を依頼する', href='@contact'):
    return f'<section class="cta"><div class="wrap cta-in"><div><h2>{title}</h2><p>{text}</p></div>{btn(label, href)}</div></section>'

def page_head(crumbs, h1, lead='', meta='', paper=False):
    c = '<li><a href="@home">トップ</a></li>' + ''.join(
        (f'<li><a href="{h}">{t}</a></li>' if h else f'<li aria-current="page">{t}</li>') for t, h in crumbs)
    p = ' ph--paper' if paper else ''
    return (f'<div class="ph{p}"><div class="wrap"><nav aria-label="パンくず"><ol class="crumb">{c}</ol></nav>'
            f'<h1>{h1}</h1>' + (f'<p class="lead">{lead}</p>' if lead else '') + meta + '</div></div>')

# ------------------------------------------------------------------ 共通の枠
LOGO = lambda: ('KARURA LIVE<small>カルラライブ</small>' if THEME[0] == 'rondo' else '<i></i>カルラライブ<small>KARURA LIVE</small>')
MQ = '<div class="mq" aria-hidden="true"><div>' + '<span>KARURA LIVE / Hybrid streaming for symposiums and lectures /</span>' * 4 + '</div></div>'
NAV = [('price', '料金・体制・機材'), ('works', '事例'), ('demo', 'ツールデモ'), ('public', '大学・公共機関の方へ'), ('faq', 'よくある質問')]
def header(cur):
    links = ''.join(f'<a href="@{i}" data-nav="{i}"' + (' aria-current="page"' if i == cur else '') + f'>{t}</a>' for i, t in NAV)
    return f'''<a class="skip" href="#main">本文へ移動</a>
<header class="head"><div class="wrap head-in">
<a class="logo" href="@home" aria-label="カルラライブ トップページ">{LOGO()}</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="gnav">メニュー</button>
<nav class="nav" id="gnav" aria-label="メインメニュー">{links}<a href="@contact" class="nav-sp" data-nav="contact">見積を依頼する</a></nav>
<p class="head-tel"><b>［電話番号］</b>［受付時間］</p>
{btn('見積を依頼する', '@contact', 'btn--s')}
</div></header>'''

FOOT_NAV = [('price', '料金・体制・機材'), ('works', '事例'), ('demo', 'ツールデモ'), ('check', 'iPhone診断'), ('coaching', '配信コーチング'),
            ('public', '大学・公共機関の方へ'), ('faq', 'よくある質問'), ('articles', '配信の手引き'), ('contact', 'お問い合わせ・お見積'),
            ('about', '運営者情報'), ('privacy', 'プライバシーポリシー')]
def footer():
    links = ''.join(f'<li><a href="@{i}">{t}</a></li>' for i, t in FOOT_NAV)
    mq = MQ if THEME[0] == 'rondo' else ''
    return f'''{mq}<footer class="foot"><div class="wrap"><div class="foot-in">
<div><a class="logo" href="@home">{LOGO()}</a>
<p class="foot-org">シンポジウム・講演会・公開講座のライブ配信／ハイブリッド配信<br>対応エリア：新宿から90分圏内<br>［運営者名・所在地］</p></div>
<nav aria-label="フッターメニュー"><ul class="foot-nav">{links}</ul></nav></div>
<p class="copy">© 2026 KARURA LIVE</p></div></footer>'''

MBAR = '<div class="mbar"><a class="btn btn--ghost" href="@contact#tel">電話する</a><a class="btn" href="@contact">見積を依頼する</a></div>'
