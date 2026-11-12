from build import *

ICONS = [
    '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="18" y="5" width="12" height="23" rx="6"/><path d="M11 22a13 13 0 0 0 26 0M24 35v8M16 43h16"/></svg>',
    '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M6 15V7h8M34 7h8v8M42 33v8h-8M14 41H6v-8"/><circle class="accent" cx="24" cy="20" r="6"/><path class="accent" d="M13 36c2-8 20-8 22 0"/></svg>',
    '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="5" y="8" width="27" height="19"/><rect class="accent" x="16" y="21" width="27" height="19"/></svg>',
    '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="6" y="7" width="36" height="13" rx="2"/><rect class="accent" x="6" y="28" width="36" height="13" rx="2"/><circle cx="14" cy="13.5" r="2"/><circle class="accent" cx="14" cy="34.5" r="2"/></svg>',
]

def pricing_block(full=False):
    """料金・体制・機材。トップと料金ページで共通。"""
    plan = f'''<div class="plan"><p class="plan-name">スタンダード</p>
<p class="plan-price"><b class="n">25</b>万円<small>（税別）</small></p>
{ticks(['スタッフ2名', 'カメラ3台と、発表スライドの映像取り込み', 'マイク5本までの持ち込み', '会場設備のマイク音声も直接取り込みます',
        '予備の録画機と、予備のインターネット回線', '配信3時間まで、会場での作業6時間まで', '事前の打ち合わせと会場の下見', '録画データの納品'])}
<div class="btns">{btn('この内容で見積書を受け取る', '@contact')}</div></div>'''
    doc = f'<figure>{quote_doc()}<figcaption class="cap">お送りする見積書の見本です。スタッフ2名の役割と機材の内訳を、1行ずつ記載します。</figcaption></figure>'
    staff = f'''<ul class="staff">
<li>{img('P04', '映像担当のスタッフ', '4/5')}<div><h4>1人目：映像担当</h4><p>カメラ3台の操作と、配信画面の切り替え</p><p class="note">［氏名・経歴一行］</p></div></li>
<li>{img('P05', '音声・配信担当のスタッフ', '4/5')}<div><h4>2人目：音声・配信担当</h4><p>マイクと音量の調整、配信の監視、登壇者PCの接続</p><p class="note">［氏名・経歴一行］</p></div></li></ul>'''
    fig = f'<figure><div class="plan-fig">{floor_plan()}</div><figcaption class="cap">赤い丸がスタッフです。1は映像担当、2は音声・配信担当。カメラは客席の後ろに置き、来場者の視界をふさぎません。</figcaption></figure>'
    gear = '''<table class="tbl tbl--stack"><thead><tr><th>種類</th><th>機種</th><th>数</th><th>用途</th></tr></thead><tbody>
<tr><th>カメラ</th><td data-l="機種">［機種名］</td><td data-l="数">3台</td><td data-l="用途">話している人のアップ、登壇者全体、会場全体</td></tr>
<tr><th>マイク</th><td data-l="機種">［機種名］</td><td data-l="数">5本</td><td data-l="用途">登壇者4人分と、会場の質問用1本</td></tr>
<tr><th>画面の切り替え機</th><td data-l="機種">［機種名］</td><td data-l="数">1台</td><td data-l="用途">発表スライドとカメラ映像の切り替え</td></tr>
<tr><th>録画機</th><td data-l="機種">［機種名］</td><td data-l="数">2系統</td><td data-l="用途">片方が止まっても、もう片方で記録を残します</td></tr>
<tr><th>回線</th><td data-l="機種">［回線の種類］</td><td data-l="数">2系統</td><td data-l="用途">会場の回線が切れても、予備回線で配信を続けます</td></tr></tbody></table>'''
    extra = '''<table class="tbl"><thead><tr><th>条件</th><th style="text-align:right">追加料金（税別）</th></tr></thead><tbody>
<tr><td>配信時間を1時間延長する</td><td class="r">［金額］</td></tr>
<tr><td>スタッフを1名追加する<br><span class="note">オンライン登壇者がいる場合、マイク6本以上の場合</span></td><td class="r">［金額］</td></tr>
<tr><td>カメラを1台追加する</td><td class="r">［金額］</td></tr>
<tr><td>会場に使えるインターネット回線がない</td><td class="r">［金額］</td></tr>
<tr><td>対応エリア外の交通費・宿泊費<br><span class="note">対応エリアは新宿から90分圏内です</span></td><td class="r">実費</td></tr></tbody></table>'''
    tail = '' if full else f'''<div class="btns">{btn('見積を依頼する', '@contact')}<a class="btn btn--ghost" href="@price#sample" data-todo="料金表と見積書見本（PDF）">料金表と見積書見本（PDF）を見る</a></div>
<p class="note" style="margin-top:12px">上司への説明や、相見積にそのまま使えます</p>'''
    return f'''<div class="cols cols--75 start" id="sample">{doc}{plan}</div>
<h3 class="h3">当日の体制：立っているだけのスタッフは連れていきません</h3>
<div class="cols cols--2 start" style="margin-top:28px">{fig}{staff}</div>
<div class="cols cols--75 start" style="margin-top:clamp(56px,7vw,96px)"><div><h3 class="h3">持ち込む機材の内訳</h3>{gear}</div><div><h3 class="h3">追加料金がかかるのは、この5つだけです</h3>{extra}</div></div>{tail}'''

def options_block():
    o = [('P13', '記録写真の撮影', '記録写真', '報告書や広報に使える写真を、専任カメラマン1名が撮影します'),
         ('P14', '記録映像の編集', '記録映像の編集（アーカイブ編集）', '話している人に合わせて画面を切り替えた記録映像を、字幕つきで作成します'),
         ('P15', 'ダイジェスト映像', '2分のダイジェスト映像', '次回の告知や、成果報告に使える短いまとめ映像を作ります'),
         ('P16', '文字起こしと報告書', '文字起こし', '報告書の下書きにそのまま使えるテキストデータを作成します')]
    cards = ''.join(f'<li>{img(c, a)}<h3>{t}</h3><p>{p}</p></li>' for c, a, t, p in o)
    return f'''<ul class="opts">{cards}</ul>
<div class="marugoto"><div><p class="plan-name">まるごと</p><p class="plan-price"><b class="n">［40］</b>万円<small>（税別）</small></p></div>
<p>スタンダードに上の4つを加えて、スタッフ3名で伺います。一回の現場で、報告書の素材まで揃います。</p>
{btn('まるごとプランで見積書を受け取る', '@contact')}</div>'''

def coaching_stairs(detail=False):
    s = [('相談', '［3万円］', 'オンライン60分。機材と接続の図、当日のチェックリストを作成します', '操作する人：まだ決めなくて大丈夫です'),
         ('同行', '［代行＋3万円］', '私たちの配信現場に入り、実際の動きを横で見て覚えます', '操作する人：私たち。ご担当者は横で見ます'),
         ('伴走', '［12万円］', 'ご自身で配信を操作し、私たちは横で待機します', '操作する人：ご担当者。私たちは会場で待機します'),
         ('卒業', '［5万円］', '事前の機材点検と、当日のオンライン待機だけで見守ります', '操作する人：ご担当者。私たちはオンラインで待機します')]
    return '<ol class="stairs">' + ''.join(
        f'<li><h3>{t}</h3><p class="fee">{f}</p><p>{p}</p>' + (f'<p class="who">{w}</p>' if detail else '') + '</li>' for t, f, p, w in s) + '</ol>'

def public_flow():
    f = [('問い合わせ', '決まっているのは日程と会場だけでかまいません'), ('見積書', '1営業日以内に、宛名入りのPDFでお送りします'),
         ('打ち合わせと会場確認', 'オンラインで30分の打ち合わせと、会場の下見を行います'), ('本番', '当日、スタッフ2名で会場に伺います'),
         ('納品と請求', '完了報告書、納品書、請求書をまとめてお送りします')]
    return '<ol class="flow">' + ''.join(f'<li><h3>{t}</h3><p>{p}</p></li>' for t, p in f) + '</ol>'

def public_docs():
    return f'''<div class="cols cols--2 start" style="margin-top:clamp(40px,5vw,72px)">
<div class="box"><h3 class="h4">書類と支払い</h3>{ticks(['見積書・納品書・請求書の3点を発行します', '請求書払い（後払い）に対応しています', 'インボイス登録番号：［T0000000000000］', '相見積のための見積依頼も歓迎します'])}</div>
<div class="box" id="template"><h3 class="h4">仕様書のひな形を、そのまま使えます</h3>
<p>配信業務の仕様書（A4 1枚、Word形式）と、見積書の見本をお送りします。他社への相見積にもそのままお使いください。</p>
<form class="inline-form" data-form="template" data-endpoint="{CFG['template_endpoint']}" aria-label="仕様書ひな形の請求">
{field('メールアドレス', 'name@example.ac.jp', typ='email', name='メールアドレス', err='メールアドレスを正しく入力してください')}
<button class="btn" type="submit" style="align-self:flex-end">ひな形を受け取る</button><p class="form-msg" role="status" hidden style="flex-basis:100%"></p></form></div></div>'''

def top():
    hero = f'''<section class="hero"><div class="wrap hero-grid">
<div><p class="hero-kind"><span class="pc">シンポジウム・講演会・公開講座のライブ配信／ハイブリッド配信<span class="nb">（会場＋オンライン）</span></span><span class="sp">シンポジウム・講演会のライブ配信／ハイブリッド配信<span class="nb">（会場＋オンライン）</span></span></p>
<h1><span>カメラ5台は</span><span>いりません。</span> <span>でも1台では、</span> <span>パネルディスカッションは</span> <span>撮れません。</span></h1>
<p class="hero-price">カメラ<b class="n">3</b>台・スタッフ<b class="n">2</b>名・マイク<b class="n">5</b>本。<em><b class="n">25</b>万円（税別）。</em></p>
{ticks(['登壇者2〜6人、会場50〜300人の会を専門にしています', '見積書に、スタッフ2名の役割と機材の内訳をすべて明記します', 'iPhoneで足りる会なら、そうお伝えします'])}
<div class="hero-sp">{btn('日程と会場だけで見積書を受け取る', '@contact', 'btn--wide')}<p class="note">1営業日以内に、宛名入りの見積書PDFをメールでお送りします</p></div></div>
<div>{switcher()}</div></div>
<div class="wrap"><div class="strip">{quote_form(strip=True)}</div></div></section>'''

    t03 = sec(f'''<h2 class="h4">これまでに配信・記録を担当した機関</h2>
<ul class="logos" style="margin-top:18px">{'<li>［取引先ロゴ］</li>' * 8}</ul>
<dl class="figs"><div><dt>配信した会</dt><dd>［　］件</dd></div><div><dt>継続して依頼いただいている機関</dt><dd>［　］機関</dd></div></dl>''', tight=True)

    t04 = sec(f'''<div class="axis">
<div><p class="axis-size">登壇1人／30人以下</p><h3>ほかの方法をおすすめする会</h3><ul class="outs"><li><b>登壇者が1人の講演</b><span>スタッフ1名で来る業者で十分です</span></li><li><b>30人以下の勉強会</b><span>お手持ちのiPhoneやPCで足ります</span></li></ul></div>
<div class="axis-us"><p class="axis-size">登壇2〜6人／会場50〜300人</p><h3>お引き受けする会</h3>{ticks(['登壇者が2〜6人で、パネルディスカッションや対談がある会', '会場に50〜300人が集まり、オンラインにも同時に配信したい会', '配信は3時間まで、半日で終わる会', '来賓や助成元、学外の視聴者がいて、配信を止められない会'])}</div>
<div><p class="axis-size">複数会場／同時通訳</p><h3>ほかの方法をおすすめする会</h3><ul class="outs"><li><b>複数会場や同時通訳</b><span>大手の制作会社が向いています</span></li></ul></div></div>
<p class="note" style="margin-top:20px;font-size:15px">迷った方は、<a href="@home#check">6問の診断</a>でご確認いただけます</p>''',
              band='sheet', h2='このような会をお引き受けしています')

    t05 = sec(pricing_block(), sid='price', h2='<span class="nb">25万円に</span><span class="nb">含まれるものすべて</span>',
              lead='誰が来て、何を持ち込み、何をするか。見積書にも同じ内容を記載します。')

    r = [('聞き取りやすい音', '会場のマイク音声を配信機材に直接取り込みます。会場にマイクがなければ5本まで持ち込みます。音が悪いと、研究まで低く見られます<cite>（Newman &amp; Schwarz 2018）</cite>。'),
         ('表情がわかるアップの映像', '客席の後ろから、話している人の表情を撮ります。来場者の視界をふさぎません。'),
         ('見やすい画面の切り替え', '発表スライド、登壇者、会場全体の映像を状況に合わせて切り替えます。スライドの隅に登壇者の顔を出すこともできます。'),
         ('万が一に備える予備機材', '録画機もインターネット回線も2系統ずつ用意します。どれか1つが止まっても、配信と記録は続きます。')]
    t06 = sec('<ul class="reasons">' + ''.join(f'<li>{ICONS[i]}<div><h3>{t}</h3><p>{p}</p></div></li>' for i, (t, p) in enumerate(r)) + f'''</ul>
<div class="cols cols--57" style="margin-top:clamp(56px,7vw,104px);align-items:center"><div>
<h3 class="h3" style="margin-top:0">止まらないとは言いません。止まったときにどう戻すかを、事前にお渡しします</h3>
<p class="lead" style="font-size:16px">事前に「復旧手順書」を1枚お渡しします。何が止まったら、誰が、何分で、どう復旧するかを明記しています。</p></div>
<figure>{recovery_doc()}</figure></div>''', sid='safety', band='board',
              h2='<span class="nb">当日、ご担当者は</span><span class="nb">配信にかかりきりに</span><span class="nb">ならずに済みます</span>', lead='登壇者を迎え、進行を見守り、来賓に挨拶する。配信の実務はスタッフ2名にお任せください。')

    t07 = sec(f'''<div class="tool" style="border-top:0;padding-top:0"><h3><small>質疑応答</small>QA Board</h3><p class="body">会場とオンラインからの質問を1か所に集め、選んだ質問だけを登壇者の画面に表示します。下の画面に質問を送ると、スタッフの一覧に届きます。</p>{qa_demo()}</div>
<div class="cols cols--2" style="margin-top:40px">
<div class="tool"><h3><small>進行管理</small>Que</h3><p>残り時間と合図を、登壇者とスタッフのスマホに表示します。進行の遅れを防ぎます。</p><p><a class="tlink" href="@demo#que">Queを試す</a></p></div>
<div class="tool"><h3><small>記録映像の作成</small>Movie Switcher</h3><p>3台のカメラの映像から、話している人に合わせて切り替えた記録映像と字幕を作ります。</p><p><a class="tlink" href="@demo#switcher">Movie Switcherを試す</a></p></div></div>
<p class="note" style="margin-top:36px;font-size:15px;max-width:44em">これらの道具は、当日私たちが用意して操作します。ご自身で使えるようになりたい方には、<a href="@coaching">コーチング</a>をご用意しています。</p>''',
              sid='demo', band='sheet', h2='現場で使っている道具を、いま試せます', lead='お手元のスマホでお試しください。当日の質疑応答と進行がどう進むかを確認できます。')

    t08 = sec(f'''{cases()}{VOICE}<div class="btns">{btn('近い事例で見積書を受け取る', '@contact')}<a class="btn btn--ghost" href="@works">事例をすべて見る</a></div>''',
              sid='works', band='mist', h2='<span class="nb">事例：人数も、機材も、</span><span class="nb">金額も公開しています</span>', lead='すべての事例を同じ項目で掲載しています。ご自身の会に近いものを探してみてください。')

    t09 = sec(f'<div style="max-width:920px">{quiz()}</div>', sid='check', h2='iPhoneで足りるなら、そうお伝えします',
              lead='6問に答えるだけで、ご自身で配信できるか、相談だけで済むか、依頼したほうがよいかがわかります。')

    t10 = sec(options_block(), sid='options', band='sheet', h2='カメラマンは、すでに会場にいます',
              lead='記録写真も、記録映像も、同じ日にまとめてご依頼いただけます。見積も請求も打ち合わせも1回で済みます。')

    t11 = sec(f'''{coaching_stairs()}<div class="btns">{btn('コーチングについて相談する', '@contact')}<a class="btn btn--ghost" href="@coaching">4つの段階を詳しく見る</a></div>''',
              sid='coaching', band='mist', h2='<span class="nb">来年度からは</span><span class="nb">自分たちで配信する：</span><span class="nb">配信コーチング</span>',
              lead='小さい会はご自身で、大きい会だけ私たちにお任せください。手順書とチェックリストが残るので、担当者が替わっても引き継げます。')

    t12 = sec(public_flow() + public_docs(), sid='public', h2='大学・公共機関の発注手続きに合わせます', lead='稟議や相見積に必要な書類を、お問い合わせの前からご用意しています。')

    t13 = sec(faq(FAQ_TOP) + '<p style="margin-top:28px"><a class="tlink" href="@faq">よくある質問をすべて見る</a></p>', sid='faq', band='sheet', h2='よくある質問')

    t14 = f'''<section class="band band--board" id="form"><div class="wrap last"><div>
<h2 class="h2">日程と会場だけ、教えてください</h2>
<p class="lead">1営業日以内に、宛名入りの見積書PDFをメールでお送りします。詳しい内容は、その後のやりとりで詰めていきます。</p>
<p class="avail">［年度末（2〜3月）の空き日程：残り〇日］</p>
<p class="last-tel">お電話でも受け付けています<b>［電話番号］</b>［受付時間］</p></div>
{quote_form(title='見積書を受け取る', text='必須の4項目だけで送信できます。')}</div></section>'''
    return hero + t03 + t04 + t05 + t06 + t07 + t08 + t09 + t10 + t11 + t12 + t13 + t14
