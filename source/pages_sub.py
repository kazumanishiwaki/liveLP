import re
from build import *
from pages_top import pricing_block, options_block, coaching_stairs, public_flow, public_docs

def price():
    return (page_head([('料金・体制・機材', '')], '料金・体制・機材',
                      'カルラライブの基本プラン「スタンダード」は、カメラ3台・スタッフ2名・マイク5本までで25万円（税別）です。誰が来て、何を持ち込み、何をするかを、このページにすべて載せています。')
            + subnav([('std', '料金'), ('staff', '体制'), ('gear', '機材'), ('extra', '追加料金'), ('options', '同じ日に'), ('pay', '支払い')])
            + sec(pricing_block(full=True), sid='std', h2='<span class="nb">25万円に</span><span class="nb">含まれるものすべて</span>', lead='見積書にも、ここに書いてあるとおりの内容を記載します。「配信業務一式」の1行だけの見積書はお出ししません。')
            + sec(options_block(), sid='options', band='sheet', h2='同じ日に頼めること', lead='記録写真も、記録映像も、同じ日にまとめてご依頼いただけます。見積も請求も打ち合わせも1回で済みます。')
            + sec(f'''<div class="cols cols--2 start"><div class="box"><h3 class="h4">書類と支払い</h3>{ticks(['見積書・納品書・請求書の3点を発行します', '請求書払い（後払い）に対応しています', 'インボイス登録番号：［T0000000000000］', '相見積のための見積依頼も歓迎します'])}
<p style="margin-top:16px"><a class="tlink" href="@public">大学・公共機関の発注の流れを見る</a></p></div>
<div>{faq([FAQ_TOP[2], FAQ_TOP[3], FAQ_TOP[4], FAQ_TOP[5]])}</div></div>''', sid='pay', h2='支払いと、料金についてよくある質問')
            + cta('この内容で、見積書をお送りします', '日程と会場だけ教えてください。1営業日以内に、宛名入りの見積書PDFをメールでお送りします。', '見積書を受け取る'))

def works():
    return (page_head([('事例', '')], '<span class="nb">事例：人数も、機材も、</span><span class="nb">金額も公開しています</span>',
                      'どの事例も、会の規模、当日の体制、使用機材、金額、当日起きたことの5項目で掲載しています。ご自身の会に近いものを探してみてください。')
            + sec(cases() + VOICE, band='mist')
            + sec('''<table class="tbl" style="max-width:820px"><thead><tr><th>項目</th><th>載せている内容</th></tr></thead><tbody>
<tr><th>会の規模</th><td>登壇者、会場の来場者、オンライン視聴者の人数と、配信した時間</td></tr>
<tr><th>当日の体制</th><td>伺ったスタッフの人数と、それぞれの役割</td></tr>
<tr><th>使用機材</th><td>カメラとマイクの数、予備機材の有無</td></tr>
<tr><th>金額</th><td>実際にお支払いいただいた金額の幅</td></tr>
<tr><th>当日起きたこと</th><td>うまくいかなかったことと、それをどう戻したか</td></tr></tbody></table>''', h2='すべての事例を、同じ5項目で載せています', lead='うまくいった話だけを選んで載せることはしません。当日に起きたトラブルと、その戻し方も書きます。')
            + cta('近い事例の内容で、見積書をお送りします', '日程と会場だけ教えてください。1営業日以内に、宛名入りの見積書PDFをメールでお送りします。', '近い事例で見積書を受け取る'))

def check():
    rows = [('登壇者の人数', '2人以上なら、話す人に合わせてカメラを切り替える必要があります。7人以上は、私たちの体制より大きな会です'),
            ('会場に来る人数', '100人を超えると、会場の音響設備との接続と、客席後方からの撮影が必要になります'),
            ('オンラインからの登壇', '会場とオンラインの声を行き来させる必要があり、音声担当の手が足りなくなります。スタッフを1名追加します'),
            ('会場の質問を届けるか', '配信に入るのは、マイクを通った音だけです。質問用のマイクと、音の経路の設計が必要です'),
            ('配信する時間', '3時間を超える場合は、延長料金がかかります'),
            ('録画の公開・学外の視聴者', 'やり直しがきかない会です。予備の録画と予備の回線が欠かせません'),
            ('同じ日に頼みたいもの', '2つ以上なら、写真・編集・ダイジェスト・文字起こしがすべて入った「まるごと」のほうが割安です'),
            ('自分たちで配信したいか', '依頼する会でも、コーチング（同行）を組み合わせると、次の会から自分たちで回せるようになります')]
    tr = ''.join(f'<tr><th style="white-space:normal">{q}</th><td>{a}</td></tr>' for q, a in rows)
    res = [('iPhoneで足ります', '登壇者1人で、質疑を配信に乗せない小さな会。費用はかかりません', '@iphone-streaming', '自前でやるときの機材'),
           ('配信コーチング：相談', '機材と接続を一度整理すれば、ご自身で配信できる会。［3万円］', '@coaching', '配信コーチング'),
           ('スタンダード', 'カメラ3台・スタッフ2名・マイク5本。25万円（税別）', '@price', '料金・体制・機材'),
           ('まるごと', 'スタンダードに、記録写真・記録映像の編集・ダイジェスト・文字起こしを加えたもの。［40］万円（税別）', '@price#options', '同じ日に頼めること'),
           ('大手の制作会社', '登壇者7人以上、または会場300人以上の会。私たちの体制より大きな会です', '@contact#consult', '15分のオンライン相談')]
    cards = ''.join(f'<div class="box"><h3 class="h4">{t}</h3><p>{d}</p><p><a class="tlink" href="{h}">{l}</a></p></div>' for t, d, h, l in res)
    return (page_head([('プラン診断', '')], 'あなたの会に合うプランを、8問で診断します',
                      '登壇者の人数、会場の規模、質疑や録画の予定など8問に答えると、おすすめのプランと、追加になる費用までわかります。iPhoneで足りる会なら、そうお伝えします。')
            + subnav([('plan', '診断'), ('results', '結果の種類'), ('why', '質問の意味')])
            + sec(f'<div class="dg-wrap">{diag()}</div>', sid='plan', band='mist', tight=True)
            + sec(f'<div class="cols cols--3" style="gap:16px">{cards}</div>', sid='results', h2='結果は、この5つのどれかです', lead='どの結果でも、そのまま見積のご依頼に進めます。診断の内容は、見積のフォームに入った状態で始まります。')
            + sec(f'<table class="tbl tbl--stack" style="max-width:920px"><thead><tr><th style="width:32%">質問</th><th>なぜ聞くのか</th></tr></thead><tbody>{tr}</tbody></table>',
                  sid='why', band='sheet', h2='8つの質問で、何を見ているか', lead='当日に同時にやることが増えるほど、1人では見きれなくなります。その境目を確かめています。')
            + cta('結果を見ても迷うときは', '15分のオンライン相談で、iPhoneで足りるかどうかから一緒にお話しします。', 'オンライン相談について見る', '@contact#consult'))

def demo():
    return (page_head([('ツールデモ', '')], '配信を支えるツールを、触ってみる',
                      '当日の質疑応答と進行、記録映像の作成に使っている道具です。このページで動きを試せます。当日は、私たちが用意して操作します。')
            + subnav([('qa', '質疑応答'), ('que', '進行管理'), ('switcher', '記録映像')])
            + sec(f'''<div class="body"><p>会場とオンラインからの質問を1か所に集め、選んだ質問だけを登壇者の画面に表示します。</p></div>
{ticks(['会場の来場者も、オンラインの視聴者も、同じ画面から質問を送れます', '届いた質問は、まずスタッフと司会だけに見えます', '司会が選んだ質問だけが、登壇者の画面に大きく表示されます'])}
{qa_demo()}<p class="cap">当日は、会場に掲示したコードをスマホで読み取ると質問を送れます。体験用のコード：［000］</p>''', sid='qa', h2='質疑応答：QA Board')
            + sec(f'''<div class="body"><p>残り時間と合図を、登壇者とスタッフのスマホに表示します。進行の遅れを防ぎます。</p></div>
{ticks(['登壇者は、自分のスマホで残り時間を確認できます', 'スタッフが送った合図が、登壇者のスマホに大きく表示されます', '声をかけたり紙を掲げたりせずに、進行を伝えられます'])}
{que_demo()}''', sid='que', band='sheet', h2='進行管理：Que')
            + sec(f'''<div class="cols cols--57" style="align-items:center"><div><div class="body"><p>3台のカメラの映像から、話している人に合わせて切り替えた記録映像と字幕を作ります。</p></div>
{ticks(['話している人のアップ、登壇者全体、会場全体を自動で切り替えます', '発言に合わせた字幕をつけます', '報告用の記録映像（アーカイブ）として納品します'])}
<p class="cap">右の画面は、切り替えと字幕の動きを示したイラストです。小さい画面を押すと、手動でも切り替えられます。［3カメの素材と完成した映像の比較動画。30秒］</p></div>
<div>{switcher(sub=True)}</div></div>''', sid='switcher', band='board', h2='記録映像の作成：Movie Switcher')
            + sec('''<div class="cols cols--2"><div class="box"><h3 class="h4">当日は、私たちが用意して操作します</h3><p>ご担当者や登壇者に、事前の設定をお願いすることはありません。登壇者には、スマホで見る画面だけをご案内します。</p></div>
<div class="box"><h3 class="h4">ご自身で使えるようになりたい方へ</h3><p>配信コーチングで、道具の使い方も含めてお伝えします。</p><p><a class="tlink" href="@coaching">配信コーチングを見る</a></p></div></div>''')
            + cta())

def coaching():
    return (page_head([('配信コーチング', '')], '次は、自分たちで配信できるように',
                      '小さい会はご自身で、大きい会だけ私たちにお任せください。相談から卒業までの4段階で、配信を自分たちで回せる体制をつくります。手順書とチェックリストが残るので、担当者が替わっても引き継げます。')
            + subnav([('steps', '4つの段階'), ('left', '残るもの'), ('plan', '診断')])
            + sec(coaching_stairs(detail=True) + '<p class="note" style="margin-top:20px;font-size:15px">必要な段階だけを選べます。相談だけで終える方もいます。</p>', sid='steps', band='mist', h2='相談から卒業まで、4つの段階', lead='段階が進むごとに、操作する人が私たちからご担当者に移ります。')
            + sec(f'''<div class="cols cols--2 start"><div><h3 class="h4">手元に残るもの</h3>{ticks(['機材と接続の図：どの機材を、どの順番でつなぐか', '当日のチェックリスト：開場前、本番中、終了後に確かめること', '手順書：担当者が替わっても、同じ手順で配信できます'])}</div>
<div><h3 class="h4">こういう機関に向いています</h3>{ticks(['年に何度か、30人ほどの勉強会や研究会を開いている', '担当者が数年で替わり、やり方が引き継がれない', 'すべての会を外注する予算はないが、大きい会は任せたい'])}</div></div>''', sid='left', h2='配信のたびに、人に頼らなくて済むように')
            + sec(f'<div class="dg-wrap">{diag()}</div>', sid='plan', band='sheet', h2='まず、自分たちでできる会かを確かめる', lead='8問のプラン診断で、ご自身で配信できるか、相談だけで済むか、依頼したほうがよいかがわかります。')
            + cta('コーチングについて相談する', 'いまの機材と、開いている会の規模を教えてください。どの段階から始めるのがよいかをお答えします。', 'コーチングについて相談する'))

def public():
    docs = '''<table class="tbl" style="max-width:880px"><thead><tr><th>書類</th><th>内容</th><th></th></tr></thead><tbody>
<tr><th>見積書</th><td>宛名入りのPDF。スタッフ2名の役割と機材の内訳を記載します</td><td class="r"><a class="tlink" href="@contact">依頼する</a></td></tr>
<tr><th>仕様書のひな形</th><td>A4 1枚、Word形式。他社への相見積にもそのまま使えます</td><td class="r"><a class="tlink" href="@public#template">受け取る</a></td></tr>
<tr><th>料金表と見積書見本</th><td>PDF。上司への説明にそのまま使えます</td><td class="r"><a class="tlink" href="@price#sample" data-todo="料金表と見積書見本（PDF）">見る</a></td></tr>
<tr><th>当日のチェックリスト</th><td>PDF。ご担当者が当日に確かめることをまとめています</td><td class="r"><a class="tlink" href="@public" data-todo="当日のチェックリスト（PDF）">見る</a></td></tr></tbody></table>'''
    return (page_head([('大学・公共機関の方へ', '')], '大学・公共機関の方へ',
                      '稟議や相見積に必要な書類を、お問い合わせの前からご用意しています。見積書・納品書・請求書の3点を発行し、請求書払い（後払い）に対応しています。')
            + subnav([('flow', '発注の流れ'), ('docs', '書類'), ('pfaq', '質問')])
            + sec(public_flow() + public_docs(), sid='flow', h2='大学・公共機関の発注手続きに合わせます', lead='お問い合わせから請求まで、5つの手順で進みます。決まっているのは日程と会場だけでかまいません。')
            + sec(docs + '<p style="margin-top:28px"><a class="tlink" href="@streaming-spec">仕様書に何を書けばいいか、書き方の記事を読む</a></p>', sid='docs', band='sheet', h2='稟議と相見積に使える書類')
            + sec(faq([FAQ_MORE[3], FAQ_MORE[4], FAQ_TOP[0], FAQ_TOP[4], FAQ_TOP[5]]), sid='pfaq', h2='発注についてよくある質問')
            + cta())

def faq_page():
    return (page_head([('よくある質問', '')], 'よくある質問', '依頼の前によく聞かれることに答えています。ここにない質問は、見積のご依頼と一緒にお書きください。')
            + sec(faq(FAQ_TOP + FAQ_MORE))
            + cta())

def contact():
    plans = ''.join(f'<label><input type="checkbox" name="気になっているプラン" value="{p}">{p}</label>' for p in ['スタンダード（25万円）', 'まるごと（写真・編集つき）', 'コーチング', 'まだわからない'])
    t = uid()
    form = f'''<form class="qform" data-form="quote" data-endpoint="{CFG['form_endpoint']}" data-thanks="@@page:thanks" aria-label="見積依頼">
<h2 class="qform-h">必須（4項目）</h2><div class="qform-row">{FOUR()}</div>
<h2 class="qform-h" style="margin-top:36px">わかる範囲でご記入ください（任意）</h2>
<div class="qform-row">{field('お名前', name='お名前', req=False)}{field('ご所属 <small>見積書の宛名になります</small>', name='ご所属', req=False)}
<div class="field"><fieldset><legend>気になっているプラン <small>（任意）</small></legend><div class="checks">{plans}</div></fieldset></div>
<div class="field"><div class="checks"><label><input type="checkbox" name="相見積" value="はい">相見積のための依頼です（仕様書のひな形も一緒にお送りします）</label></div></div>
<div class="field"><label for="{t}">気になっていること、前回の配信で困ったこと <small>（任意）</small></label><textarea id="{t}" name="気になっていること"></textarea></div></div>
<div class="btns" style="margin-top:24px"><button class="btn" type="submit">見積書を受け取る</button></div>
<p class="note" style="margin-top:12px">送信いただいても、こちらから電話での営業はいたしません。<a href="@privacy">プライバシーポリシー</a></p>
<p class="form-msg" role="status" hidden></p></form>'''
    side = f'''<div class="side">
<div class="box"><h2 class="h4">送信したあとの流れ</h2><div class="prose" style="margin-top:10px;font-size:15px"><ol><li>1営業日以内に、見積書PDFがメールで届きます</li><li>必要に応じて、オンラインで30分ほど打ち合わせをします</li><li>ご発注が決まったら、事前に会場を下見します</li></ol></div></div>
<div><h2 class="h4" style="margin-bottom:12px">届く見積書の見本</h2>{quote_doc()}</div>
<div class="box" id="consult"><h2 class="h4">まだ何も決まっていない方へ</h2><p>15分のオンライン相談で、iPhoneで足りるかどうかから一緒にお話しします。</p><p style="margin-top:14px"><a class="btn btn--ghost btn--s" href="@contact" data-todo="オンライン相談の予約ページ">相談の日時を選ぶ</a></p></div>
<div class="box" id="tel"><h2 class="h4">お電話でも受け付けています</h2><p style="font-size:15px"><b class="n" style="font-size:30px;display:block;line-height:1.3">［電話番号］</b>［受付時間］</p></div>
<blockquote class="voice" style="margin-top:8px"><p style="font-size:16px">［担当者の声を1件。頼む前の不安に触れているもの］</p><footer>［所属・役職］</footer></blockquote></div>'''
    return (page_head([('お問い合わせ・お見積', '')], '見積書をお送りします', '必須の4項目だけで送信できます。1営業日以内に、宛名入りの見積書PDFをメールでお送りします。', paper=True)
            + f'<section class="band band--tight"><div class="wrap cols cols--75 start">{form}{side}</div></section>')

def thanks():
    pv = '' if CFG['form_endpoint'] else '<p class="pv-note">これは送信完了ページの見本です。フォームの送信先がまだ設定されていないため、実際には何も送信されていません。</p>'
    return (pv + page_head([('お問い合わせ・お見積', '@contact'), ('送信完了', '')], 'ご依頼を受け付けました',
                           '1営業日以内に、宛名入りの見積書PDFをメールでお送りします。確認メールが届かない場合は、［電話番号］までご連絡ください。', paper=True)
            + sec('''<ol class="flow flow--3"><li class="now"><h3>いまここ</h3><p>見積のご依頼を受け付けました</p></li><li><h3>1営業日以内</h3><p>見積書PDFがメールで届きます</p></li><li><h3>そのあと</h3><p>必要に応じて30分の打ち合わせを行い、ご発注後に会場を下見します</p></li></ol>''', tight=True)
            + sec(f'''<div class="btns" style="margin-top:0"><a class="btn btn--ghost" href="@public#template" data-todo="仕様書のひな形（Word）">仕様書のひな形（Word）をダウンロードする</a>
<a class="btn btn--ghost" href="@price#sample" data-todo="料金表と見積書見本（PDF）">料金表と見積書見本（PDF）を見る</a>
<a class="btn btn--ghost" href="@public" data-todo="当日のチェックリスト（PDF）">当日のチェックリスト（PDF）を見る</a></div>''',
                  band='sheet', h2='お待ちいただく間に、稟議の準備にお使いください', lead='上司への説明や相見積にそのまま使える書類です。どれも登録なしでダウンロードできます。', tight=True)
            + sec(cases() + '<p style="margin-top:32px"><a class="tlink" href="@home">トップページへ戻る</a></p>', band='mist', h2='近い規模の事例'))

def about():
    rows = [('サービス名', 'カルラライブ（Karura Live）'), ('運営者', '［運営者名］'), ('代表者', '［代表者名］'), ('所在地', '［所在地］'),
            ('電話', '［電話番号］（［受付時間］）'), ('インボイス登録番号', '［T0000000000000］'), ('対応エリア', '新宿駅からおおむね90分以内で伺える会場（東京都・神奈川県・埼玉県・千葉県ほか）。エリア外は交通費・宿泊費の実費で伺います'),
            ('事業内容', 'シンポジウム・講演会・公開講座のライブ配信とハイブリッド配信、記録写真、記録映像の編集、文字起こし、配信コーチング')]
    return (page_head([('運営者情報', '')], '運営者情報', paper=True)
            + sec('<dl class="dl">' + ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in rows) + '</dl>'))

def privacy():
    return (page_head([('プライバシーポリシー', '')], 'プライバシーポリシー', paper=True)
            + sec('''<div class="prose"><p>［この文面は下書きです。公開前に、運営の実態に合わせて確認してください］</p>
<p>カルラライブ（以下「当サービス」）は、お問い合わせや見積のご依頼でお預かりした個人情報を、次のとおり取り扱います。</p>
<h2>お預かりする情報</h2><p>フォームにご記入いただいた、開催日、会場、人数、メールアドレス、お名前、ご所属、ご相談の内容。</p>
<h2>利用する目的</h2><ul><li>見積書や仕様書のひな形をお送りするため</li><li>お問い合わせにお答えするため</li><li>ご依頼いただいた業務を行い、納品と請求を行うため</li></ul>
<p>フォームを送信いただいても、こちらから電話での営業はいたしません。</p>
<h2>第三者への提供</h2><p>法令にもとづく場合を除き、ご本人の同意なく第三者に提供することはありません。</p>
<h2>アクセスの解析</h2><p>サイトの改善のために、［利用する解析ツール］を使ってアクセスの状況を集計しています。個人を特定する情報は含みません。</p>
<h2>お問い合わせの窓口</h2><p>［運営者名］　［連絡先］</p>
<p>［制定日］</p></div>'''))

# ------------------------------------------------------------------ 記事
def article(title, answer, body, nexts, pid):
    heads = []
    def _id(m):
        i = f'h{len(heads) + 1}'; heads.append((i, m.group(1)))
        return f'<h2 id="{i}">{m.group(1)}</h2>'
    body = re.sub(r'<h2>(.*?)</h2>', _id, body)
    short = lambda x: x if len(x) <= 9 else x[:8] + '…'
    sn = subnav([('answer', '答え')] + [(i, short(re.sub('<[^>]+>', '', h))) for i, h in heads])
    n = ''.join(f'<li><a class="tlink" href="{h}">{t}</a></li>' for t, h in nexts)
    return (page_head([('配信の手引き', '@articles'), (title, '')], title, meta='<p class="meta"><span>公開日：［公開日］</span><span>書いた人：［氏名・経歴一行］</span></p>')
            + sn + f'<section class="band"><div class="wrap"><article class="prose"><p class="answer" id="answer">{answer}</p>{body}</article>'
            + f'<aside class="next"><h2>次に読むページ</h2><ul>{n}</ul></aside></div></section>' + cta())

def a_iphone():
    body = '''<h2>足りる会、足りない会</h2>
<table class="tbl tbl--stack"><thead><tr><th>条件</th><th>iPhoneで足りる</th><th>足りない</th></tr></thead><tbody>
<tr><th>登壇者</th><td data-l="足りる">1〜2人で、立ち位置が変わらない</td><td data-l="足りない">3人以上、または席が離れている</td></tr>
<tr><th>質疑</th><td data-l="足りる">会場の中だけで完結する</td><td data-l="足りない">会場の質問をオンラインにも届けたい</td></tr>
<tr><th>映すもの</th><td data-l="足りる">話し手だけ、またはスライドだけ</td><td data-l="足りない">スライドと話し手を切り替えたい</td></tr>
<tr><th>時間</th><td data-l="足りる">2時間以内</td><td data-l="足りない">2時間を超える</td></tr>
<tr><th>視聴者</th><td data-l="足りる">学内や関係者だけ</td><td data-l="足りない">学外の視聴者、来賓、助成元がいる</td></tr>
<tr><th>録画</th><td data-l="足りる">残さない、または内部の記録用</td><td data-l="足りない">アーカイブとして公開する</td></tr></tbody></table>
<p>右の列に1つ当てはまるだけなら、工夫で乗り切れることもあります。2つ以上当てはまると、当日に同時にやることが増えて、1人では見きれなくなります。</p>
<h2>自前でやるときの、いちばん小さい機材</h2>
<ul><li><strong>iPhone</strong>：配信専用にします。通知を切り、着信が入らない設定にしておきます</li>
<li><strong>三脚とスマホホルダー</strong>：話し手の目の高さに合わせます。机に立てかけると、見上げる画になります</li>
<li><strong>外付けのマイク</strong>：ピンマイクかワイヤレスマイクを話し手につけます。内蔵マイクは、話し手から離れると会場の反響ばかり拾います</li>
<li><strong>電源</strong>：充電しながら配信できるケーブルと、予備のモバイルバッテリー</li>
<li><strong>回線</strong>：会場の有線LANか、配信専用のモバイルルーター。来場者と同じWi-Fiは、人が集まると遅くなります</li>
<li><strong>確認用の端末とイヤホン</strong>：配信がどう見えて、どう聞こえているかを、別の端末で確かめます</li></ul>
<h2>1人でやると抜けやすいこと</h2>
<ol><li><strong>音を誰も聞いていない。</strong>映像は目に入りますが、音は聞こうとしないと気づけません。確認用の端末で、イヤホンをつけて聞き続けます</li>
<li><strong>バッテリーと発熱。</strong>長時間の配信では本体が熱くなり、止まることがあります。充電しながら、日の当たらない場所に置きます</li>
<li><strong>着信と通知。</strong>配信中に電話がかかってくると、配信が止まることがあります</li>
<li><strong>録画の押し忘れ。</strong>配信を始めても、録画は別のボタンになっていることがあります</li>
<li><strong>オンラインからの質問を見る人がいない。</strong>配信を操作している人は、文字の質問まで見られません。見る人を別に決めておきます</li>
<li><strong>画面の向き。</strong>横向きに固定して、回転しない設定にしておきます</li></ol>
<h2>迷ったら</h2>
<p>ご自身の会がどちらに当たるかは、<a href="@check">8問のプラン診断</a>で確かめられます。自分たちで続けていきたい場合は、機材と接続の図、当日のチェックリストを一緒に作る<a href="@coaching">配信コーチング</a>があります。</p>'''
    return article('iPhoneでシンポジウムを配信して大丈夫な条件、だめな条件',
                   '登壇者が1〜2人で、会場からの質疑をオンラインに届けなくてよい会なら、iPhone1台と外付けマイク1本で配信できます。登壇者が3人以上いる、会場の質問をオンラインにも届けたい、スライドと話し手の両方を映したい。このどれかに当てはまると、1人では回らなくなります。',
                   body, [('8問のプラン診断', '@check'), ('配信コーチング', '@coaching'), ('料金・体制・機材', '@price')], 'iphone-streaming')

AUDIO_FIG = '''<figure><svg viewBox="0 0 760 330" role="img" aria-label="音の流れの図。会場のマイクの音はミキサーから会場のスピーカーと配信PCの両方へ送る。オンライン参加者の声は配信PCからミキサーに入れ、会場のスピーカーだけに出す">
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#eef2ee"/></marker><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#f08a78"/></marker></defs>
<g fill="none" stroke="#eef2ee" stroke-width="1.6"><rect x="30" y="56" width="150" height="56" rx="3"/><rect x="290" y="56" width="180" height="56" rx="3"/><rect x="580" y="56" width="150" height="56" rx="3"/><rect x="290" y="226" width="180" height="56" rx="3"/><rect x="580" y="226" width="150" height="56" rx="3"/></g>
<g fill="#eef2ee" font-size="15" font-weight="700" text-anchor="middle"><text x="105" y="90">会場のマイク</text><text x="380" y="90">ミキサー</text><text x="655" y="90">会場のスピーカー</text><text x="380" y="260">配信PC</text><text x="655" y="260">オンライン参加者</text></g>
<g stroke="#eef2ee" stroke-width="2" fill="none"><path d="M180 84H284" marker-end="url(#ah)"/><path d="M470 84H574" marker-end="url(#ah)"/><path d="M420 226V118" marker-end="url(#ah)"/><path d="M470 254H574" marker-end="url(#ah)" marker-start="url(#ah)"/></g>
<path d="M340 112V220" stroke="#f08a78" stroke-width="2.5" fill="none" marker-end="url(#ar)"/>
<g font-size="12.5" fill="#a8beb5"><text x="525" y="40" text-anchor="middle">会場に流す音：マイク＋オンラインの声</text><text x="434" y="176">オンラインの声</text></g>
<text x="328" y="162" font-size="12.5" fill="#f08a78" font-weight="700" text-anchor="end">配信に送る音は</text><text x="328" y="180" font-size="12.5" fill="#f08a78" font-weight="700" text-anchor="end">会場のマイクだけ</text>
</svg><figcaption class="cap">赤い線が要点です。配信PCに送る音に、オンライン参加者の声を混ぜません。混ぜると、相手に自分の声が遅れて返ります。</figcaption></figure>'''

def a_audio():
    body = f'''<h2>よくある3つの失敗</h2>
<h3>1. ハウリングする、声が二重に聞こえる</h3>
<p>オンライン参加者の声が会場のスピーカーから出て、それを会場のマイクが拾い、またオンライン側に戻っています。配信用のPCの内蔵マイクと内蔵スピーカーをそのまま使っていると、ほぼ確実に起きます。</p>
<ul><li>PCの内蔵マイクは使いません。会場のマイクの音を、ミキサーからPCにケーブルで直接入れます</li>
<li>オンライン参加者の声は、会場のスピーカーには出しますが、配信に送る音には混ぜません。ミキサーの「AUX」という出力を使うと、送り先ごとに混ぜる音を選べます</li></ul>
<h3>2. オンライン参加者の声が、会場に聞こえない</h3>
<p>配信用のPCの音が、会場の音響設備につながっていません。PCの音声出力からミキサーへ、ケーブルを1本つなぎます。会議アプリの「スピーカー」の設定が、その出力になっているかも確かめます。</p>
<h3>3. 会場の質問が、配信に入らない</h3>
<p>質問する人が、マイクを使わずに話しています。会場では聞こえても、配信に入るのはマイクを通った音だけです。</p>
<ul><li>質問用のマイクを1本用意して、係が質問者のところまで持っていきます</li>
<li>それが難しければ、司会がマイクで質問を繰り返してから、登壇者が答えます</li></ul>
<h2>音の流れを図にすると</h2>
<p>「会場に流す音」と「配信に送る音」を分けて考えると、3つの失敗はまとめて防げます。</p>
{AUDIO_FIG}
<h2>本番の前に確かめること</h2>
<ol><li>会場で、実際にスピーカーから音を出した状態でテストします。スピーカーを切ったテストでは、ハウリングは見つかりません</li>
<li>オンライン側に1人入ってもらい、会場の声とオンラインの声を、互いに聞いて確かめます</li>
<li>質問用マイクを誰が運ぶかを決めておきます</li>
<li>会議アプリのマイクとスピーカーの設定に、PCの内蔵マイクと内蔵スピーカーが選ばれていないかを見ます</li></ol>
<h2>マイクが5本ある理由</h2>
<p>カルラライブのスタンダードは、マイクを5本まで持ち込みます。登壇者4人分と、会場の質問用の1本です。会場設備のマイクがあれば、その音も配信機材に直接取り込みます。音声と配信の担当が1名つき、本番中は音を聞き続けます。</p>'''
    return article('ハイブリッド開催で音が聞こえない、ハウリングする原因と対策',
                   '原因のほとんどは、会場のスピーカーから出た音をマイクが拾い、もう一度配信に戻っていることです。「会場に流す音」と「配信に送る音」を分けて管理すれば止まります。',
                   body, [('料金・体制・機材（マイク5本の内訳）', '@price'), ('会場とオンラインの質問をまとめる QA Board を試す', '@demo#qa'), ('8問のプラン診断', '@check')], 'hybrid-audio')

def a_spec():
    body = f'''<h2>仕様書に書く6つの項目</h2>
<table class="tbl tbl--stack"><thead><tr><th>項目</th><th>書くこと</th><th>書き方の例</th></tr></thead><tbody>
<tr><th>日時</th><td data-l="書くこと">開催日、配信の開始と終了、会場に入れる時刻</td><td data-l="例">2027年2月20日（土）13:00〜16:00。会場には10:00から入れる</td></tr>
<tr><th>会場</th><td data-l="書くこと">建物と部屋の名前、定員、使える設備</td><td data-l="例">〇〇大学 △△ホール（定員200人）。有線LANとワイヤレスマイク4本あり</td></tr>
<tr><th>登壇者の人数</th><td data-l="書くこと">人数と形式、オンラインからの登壇があるか</td><td data-l="例">基調講演1人、パネルディスカッション4人。うち1人はオンラインから参加</td></tr>
<tr><th>配信先</th><td data-l="書くこと">使うサービスと、公開する範囲</td><td data-l="例">Zoomウェビナー。事前に登録した人だけが視聴する</td></tr>
<tr><th>質疑の有無</th><td data-l="書くこと">会場とオンラインの、どちらから受けるか</td><td data-l="例">会場はマイクで、オンラインは文字で受け付ける</td></tr>
<tr><th>録画の扱い</th><td data-l="書くこと">納品の形式、編集の有無、公開の予定</td><td data-l="例">録画データをMP4で納品。後日、大学のサイトで公開する</td></tr></tbody></table>
<p>まだ決まっていない項目は、「未定」と書いてかまいません。空欄にするより、未定と書いてあるほうが、業者は前提をそろえて見積を出せます。</p>
<h2>相見積で比べるところ</h2>
<ul><li><strong>スタッフの人数と、それぞれの役割。</strong>同じ金額でも、1名で来る業者と2名で来る業者があります</li>
<li><strong>カメラとマイクの数。</strong>登壇者の人数に対して足りているか</li>
<li><strong>会場の下見が含まれているか。</strong>別料金のこともあります</li>
<li><strong>予備の録画と、予備の回線があるか。</strong>止まったときにどうするかが書いてあるか</li>
<li><strong>録画データの納品形式と、納期</strong></li>
<li><strong>追加料金がかかる条件。</strong>時間の延長、機材の追加、交通費</li></ul>
<h2>金額だけで比べないために</h2>
<p>見積書が「配信業務一式」の1行だけだと、何が含まれているかを比べられません。仕様書に次の一文を入れておくと、内訳のそろった見積書が集まります。</p>
<p class="answer" style="font-size:16px">見積書には、スタッフの人数と役割、持ち込む機材の内訳を記載すること。</p>
<h2>ひな形を受け取る</h2>
<p>ここに挙げた6項目を並べた、A4 1枚のひな形（Word形式）を用意しています。見積書の見本と一緒にお送りします。他社への相見積にもそのままお使いください。</p>
<p>{btn('仕様書のひな形を受け取る', '@public#template')}</p>'''
    return article('ライブ配信を業者に頼むときの仕様書の書き方（ひな形つき）',
                   '仕様書に必要なのは、日時、会場、登壇者の人数、配信先、質疑の有無、録画の扱いの6つです。この6つがそろえば、業者ごとの見積を同じ条件で比べられます。',
                   body, [('大学・公共機関の方へ：発注の流れと書類', '@public'), ('料金・体制・機材', '@price'), ('見積書を受け取る', '@contact')], 'streaming-spec')

ARTICLES = [
    ('iphone-streaming', 'iPhoneでシンポジウムを配信して大丈夫な条件、だめな条件', '登壇者1〜2人で質疑を届けなくてよい会なら、iPhoneで足ります。足りる条件と足りない条件、自前でやるときの機材。'),
    ('hybrid-audio', 'ハイブリッド開催で音が聞こえない、ハウリングする原因と対策', '原因のほとんどは、会場のスピーカーの音がマイクに戻っていること。よくある3つの失敗と、音の流れの図。'),
    ('streaming-spec', 'ライブ配信を業者に頼むときの仕様書の書き方（ひな形つき）', '仕様書に必要なのは6項目。相見積で比べるところと、そのまま使えるひな形。'),
]
def articles():
    li = ''.join(f'<li><a href="@{i}"><h2>{t}</h2><p>{d}</p></a></li>' for i, t, d in ARTICLES)
    return (page_head([('配信の手引き', '')], '配信の手引き', '自前で配信するか業者に頼むかの判断、ハイブリッドの音の失敗、仕様書の書き方。シンポジウムの担当者が、最初に知っておくと楽になることをまとめています。')
            + sec(f'<ul class="alist">{li}</ul>') + cta())
