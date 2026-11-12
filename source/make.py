#!/usr/bin/env python3
"""書き出し本体： python3 make.py
   dist/     公開用（ページごとの HTML、robots.txt、sitemap.xml）
   preview/  確認用（index.html 1ファイルで全ページを切り替え）
   穴埋めリスト.md  ［ ］で残っている箇所の一覧"""
import json, re, shutil, subprocess, sys
from pathlib import Path
import build as B
from build import CFG, ROOT
import pages_top as T, pages_sub as S

THEME = sys.argv[1] if len(sys.argv) > 1 else ''
B.THEME[0] = THEME
SUF = f'-{THEME}' if THEME else ''
N = CFG['name']
P = lambda **k: k
PAGES = [
    P(id='home', path='/', fn=T.top, title=f'シンポジウム・講演会のハイブリッド配信代行｜3カメ・2名・25万円〜｜{N}',
      desc='大学や公共機関のシンポジウム、公開講座をハイブリッドで配信します。3カメラ・スタッフ2名・マイク5本までで25万円（税別）から。会場とオンライン、両方の聞こえ方まで面倒を見ます。', ld='service'),
    P(id='price', path='/price/', fn=S.price, name='料金・体制・機材', title=f'料金・体制・機材の内訳｜ハイブリッド配信は25万円（税別）から｜{N}',
      desc='基本プランは3カメラ・スタッフ2名・マイク5本まで、25万円（税別）。当日の人の配置、持ち込む機材の一覧、追加になる条件をすべて載せています。見積の前に予算感をつかめます。', ld='service'),
    P(id='works', path='/works/', fn=S.works, name='事例', title=f'配信の事例｜大学・自治体のシンポジウムと講演会｜{N}',
      desc='これまで担当したシンポジウム、講演会、公開講座の配信事例です。会の規模、スタッフの体制、使った機材、金額、当日起きたことを、すべて同じ項目で一件ずつ載せています。'),
    P(id='check', path='/check/', fn=S.check, name='プラン診断', title=f'プラン診断｜8問で、合う配信プランと費用がわかる｜{N}',
      desc='登壇者の人数、会場の規模、質疑や録画の予定など8問から、おすすめのプランと追加になる費用を判定します。iPhoneで足りる会なら、そう答えます。結果はそのまま見積のご依頼に使えます。'),
    P(id='demo', path='/demo/', fn=S.demo, name='ツールデモ', title=f'配信支援ツールのデモ｜質問ボード・進行管理・記録映像｜{N}',
      desc='会場とオンラインの質問をまとめるQA Board、残り時間と合図を共有するQue、話している人に合わせて記録映像を作るMovie Switcher。当日使う道具の動きを、このページで試せます。'),
    P(id='coaching', path='/coaching/', fn=S.coaching, name='配信コーチング', title=f'配信コーチング｜次から自分たちで配信できる体制づくり｜{N}',
      desc='当日の配信を任せるだけでなく、職員の方が次回から自分たちで回せるように、手順と機材の選び方を伝えます。相談、同行、伴走、卒業の4段階で、現場に入りながら覚えられます。'),
    P(id='public', path='/public/', fn=S.public, name='大学・公共機関の方へ', title=f'大学・公共機関の方へ｜仕様書のひな形・見積・請求書払いに対応｜{N}',
      desc='稟議や相見積に必要な仕様書のひな形、内訳つきの見積書、請求書払いと適格請求書に対応しています。発注の手続きで詰まりやすいところを、お問い合わせの前にまとめました。'),
    P(id='faq', path='/faq/', fn=S.faq_page, name='よくある質問', title=f'よくある質問｜ハイブリッド配信の準備・当日・費用｜{N}',
      desc='何日前に頼めばいいか、会場の下見は必要か、録画データは残るか、対応エリアはどこまでか。ハイブリッド配信を依頼する前によく聞かれることに、一つずつ、具体的に答えています。', ld='faq'),
    P(id='contact', path='/contact/', fn=S.contact, name='お問い合わせ・お見積', title=f'お問い合わせ・お見積｜ハイブリッド配信のご相談｜{N}', nobar=True,
      desc='日程と会場、登壇者の人数がわかれば見積書をお出しします。まだ決まっていないことが多くても大丈夫です。1営業日以内に、宛名入りの見積書PDFをメールでお送りします。'),
    P(id='thanks', path='/contact/thanks/', fn=S.thanks, name='送信完了', title=f'送信が完了しました｜{N}', desc='', noindex=True, nobar=True, parent='contact'),
    P(id='articles', path='/articles/', fn=S.articles, name='配信の手引き', title=f'配信の手引き｜シンポジウム・講演会の担当者のための記事｜{N}',
      desc='自前で配信するか業者に頼むかの判断、ハイブリッドの音の失敗、仕様書の書き方。シンポジウムの担当者が最初に知っておくと楽になることを、現場の経験からまとめています。'),
    P(id='iphone-streaming', path='/articles/iphone-streaming/', fn=S.a_iphone, name=S.ARTICLES[0][1], title=f'iPhoneでシンポジウムを配信して大丈夫な条件、だめな条件｜{N}', parent='articles', ld='article',
      desc='登壇者が1〜2人で、会場の質疑をオンラインに届けなくてよい会ならiPhoneで足ります。足りる条件と足りない条件の表、自前でやるときの最小限の機材、1人だと抜けやすいことをまとめました。'),
    P(id='hybrid-audio', path='/articles/hybrid-audio/', fn=S.a_audio, name=S.ARTICLES[1][1], title=f'ハイブリッド開催で音が聞こえない、ハウリングする原因と対策｜{N}', parent='articles', ld='article',
      desc='原因のほとんどは、会場のスピーカーから出た音をマイクが拾って配信に戻っていること。ハウリング、オンラインの声が会場に出ない、会場の質問が配信に入らない、の3つを図で解説します。'),
    P(id='streaming-spec', path='/articles/streaming-spec/', fn=S.a_spec, name=S.ARTICLES[2][1], title=f'ライブ配信を業者に頼むときの仕様書の書き方（ひな形つき）｜{N}', parent='articles', ld='article',
      desc='仕様書に必要なのは、日時、会場、登壇者の人数、配信先、質疑の有無、録画の扱いの6つ。項目ごとの書き方の例、相見積で比べるところ、そのまま使えるWordのひな形を用意しました。'),
    P(id='about', path='/about/', fn=S.about, name='運営者情報', title=f'運営者情報｜{N}', desc='カルラライブの運営者、所在地、連絡先、インボイス登録番号、対応エリア（新宿から90分圏内）、事業内容を掲載しています。ライブ配信とハイブリッド配信のご依頼はこちらから。'),
    P(id='privacy', path='/privacy/', fn=S.privacy, name='プライバシーポリシー', title=f'プライバシーポリシー｜{N}', desc='カルラライブが、お問い合わせや見積のご依頼でお預かりする個人情報の取り扱いについて定めています。利用する目的、第三者への提供、お問い合わせの窓口を掲載しています。'),
]
BY = {p['id']: p for p in PAGES}

ANA = re.compile(r'［[^］]*］')
def mark_ana(h):
    """タグの外にある［ ］に印をつける"""
    parts = re.split(r'(<[^>]+>)', h)
    return ''.join(p if p.startswith('<') else ANA.sub(lambda m: f'<span class="ana">{m.group(0)}</span>', p) for p in parts)

def resolve(h, mode):
    def link(m):
        pid, a = m.group(1), m.group(2)
        if pid not in BY: raise SystemExit(f'リンク先がありません: @{pid}')
        if mode == 'prod':
            return f'href="{BY[pid]["path"]}' + (f'#{a}' if a else '') + '"'
        return f'href="#{pid}"' + (f' data-a="{a}"' if a else '')
    h = re.sub(r'href="@([a-z0-9-]+)(?:#([a-z0-9-]+))?"', link, h)
    h = re.sub(r'"@@page:([a-z0-9-]+)"', lambda m: '"' + (BY[m.group(1)]['path'] if mode == 'prod' else '#' + m.group(1)) + '"', h)
    return h.replace('@@/', '/assets/' if mode == 'prod' else 'assets/')

# ------------------------------------------------------------------ 構造化データ
U = CFG['url']
def jsonld(p):
    g = [{'@type': 'ProfessionalService', '@id': f'{U}/#org', 'name': N, 'alternateName': CFG['alt'], 'url': f'{U}/', 'logo': f'{U}/assets/logo.png',
          'areaServed': CFG['area'], 'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer service', 'url': f'{U}/contact/'}},
         {'@type': 'WebSite', '@id': f'{U}/#website', 'url': f'{U}/', 'name': N, 'alternateName': CFG['alt'], 'publisher': {'@id': f'{U}/#org'}}]
    if p.get('ld') == 'service':
        g.append({'@type': 'Service', '@id': f'{U}/#basic', 'name': 'ハイブリッド配信 スタンダード', 'serviceType': 'シンポジウム・講演会のライブ配信代行',
                  'provider': {'@id': f'{U}/#org'}, 'areaServed': CFG['area'], 'description': 'カメラ3台、スタッフ2名、マイク5本までで、会場とオンラインに配信します。配信3時間まで、事前の打ち合わせと会場の下見、録画データの納品を含みます。',
                  'offers': {'@type': 'Offer', 'price': '250000', 'priceCurrency': 'JPY', 'url': f'{U}/price/',
                             'priceSpecification': {'@type': 'PriceSpecification', 'price': '250000', 'priceCurrency': 'JPY', 'valueAddedTaxIncluded': False}}})
    if p['id'] != 'home':
        chain = [('トップ', '/')] + ([(BY[p['parent']]['name'], BY[p['parent']]['path'])] if p.get('parent') else []) + [(p['name'], p['path'])]
        g.append({'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': U + u} for i, (n, u) in enumerate(chain)]})
    if p.get('ld') == 'article':
        g.append({'@type': 'Article', 'headline': p['name'], 'description': p['desc'], 'mainEntityOfPage': U + p['path'], 'inLanguage': 'ja',
                  'author': {'@type': 'Person', 'name': '［氏名］'}, 'publisher': {'@id': f'{U}/#org'}, 'datePublished': '［公開日 YYYY-MM-DD］', 'dateModified': '［更新日 YYYY-MM-DD］'})
    if p.get('ld') == 'faq':
        strip = lambda s: re.sub(r'<[^>]+>', '', s)
        g.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in B.FAQ_TOP + B.FAQ_MORE if '［' not in a]})
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': g}, ensure_ascii=False) + '</script>'

FONT_PRELOAD = ''.join(f'<link rel="preload" href="@@/fonts/{f}.woff2" as="font" type="font/woff2" crossorigin>' for f in (['zkgn-500'] if THEME else ['zkgn-900', 'zkgn-400']))
def head(p, mode):
    if mode == 'prod':
        robots = '<meta name="robots" content="noindex">' if p.get('noindex') else ''
        desc = f'<meta name="description" content="{p["desc"]}">' if p['desc'] else ''
        og = (f'<meta property="og:type" content="{"website" if p["id"] == "home" else "article"}"><meta property="og:site_name" content="{N}"><meta property="og:locale" content="ja_JP">'
              f'<meta property="og:title" content="{p["title"]}"><meta property="og:description" content="{p["desc"]}"><meta property="og:url" content="{U}{p["path"]}">'
              f'<meta property="og:image" content="{U}/assets/ogp.png"><meta name="twitter:card" content="summary_large_image">')
        extra = f'{desc}{robots}<link rel="canonical" href="{U}{p["path"]}">{og}{jsonld(p)}'
    else:
        extra = '<meta name="robots" content="noindex">'
    return f'''<!DOCTYPE html>
<html lang="ja"{' data-mode="preview"' if mode == 'preview' else ''}{f' data-theme="{THEME}"' if THEME else ''}>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{p['title']}</title><script>document.documentElement.classList.add('js')</script>{extra}
<link rel="icon" href="@@/favicon.svg" type="image/svg+xml">{FONT_PRELOAD}
<link rel="stylesheet" href="@@/site.css"></head>
<body>'''

def main_html(p):
    B._uid[0] = 1000 * (PAGES.index(p) + 1)
    return mark_ana(p['fn']())

def chrome_top(cur): return mark_ana(B.header(cur))
def chrome_bottom(p, mode): return mark_ana(B.footer()) + ('' if (mode == 'prod' and p.get('nobar')) else B.MBAR) + '<script src="@@/site.js" defer></script></body></html>'

def build():
    dist, pv = ROOT / f'dist{SUF}', ROOT / f'preview{SUF}'
    for d in (dist, pv):
        shutil.rmtree(d, ignore_errors=True); (d / 'assets/fonts').mkdir(parents=True); (d / 'assets/img').mkdir(parents=True)
    mains, holes, alltext = {}, [], ''
    for p in PAGES:
        m = main_html(p); mains[p['id']] = m
        found = ANA.findall(re.sub(r'<[^>]+>', ' ', m))
        holes.append((p, found))
        nav_cur = p['id'] if p['id'] in dict(B.NAV) else p.get('parent', '')
        page = head(p, 'prod') + (B.scene_defs() if 'data-sw' in m else '') + chrome_top(nav_cur) + f'<main id="main">{m}</main>' + chrome_bottom(p, 'prod')
        page = resolve(page, 'prod')
        out = dist / p['path'].strip('/') / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True); out.write_text(page, encoding='utf-8')
        alltext += page
    # 確認用：全ページを1ファイルに
    note = '<p class="pv-note">確認用のプレビューです。黄色い［　］は、これから入れる情報です。フォームはまだどこにも送信されません。</p>'
    body = ''.join(f'<main data-page="{p["id"]}" data-title="{p["title"]}"' + (' data-nobar' if p.get('nobar') else '') + f'>{mains[p["id"]]}</main>' for p in PAGES)
    one = head(BY['home'], 'preview') + note + B.scene_defs() + chrome_top('') + '<div id="main">' + body + '</div>' + chrome_bottom(BY['home'], 'preview')
    (pv / 'index.html').write_text(resolve(one, 'preview'), encoding='utf-8')
    # 素材
    js = (ROOT / 'src/site.js').read_text(encoding='utf-8'); css = (ROOT / 'src/site.css').read_text(encoding='utf-8') + ((ROOT / f'src/theme-{THEME}.css').read_text(encoding='utf-8') if THEME else '')
    fav = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#153b33"/><rect x="9" y="9" width="14" height="14" rx="3" fill="#cf3a26"/></svg>'
    for d in (dist, pv):
        for extra in ('ogp.png', 'logo.png'):
            if (ROOT / 'src' / extra).exists() and d is dist: shutil.copy(ROOT / 'src' / extra, d / 'assets' / extra)
        (d / 'assets/site.css').write_text(css, encoding='utf-8'); (d / 'assets/site.js').write_text(js, encoding='utf-8'); (d / 'assets/favicon.svg').write_text(fav)
        for f in sorted((ROOT / 'img-src').glob('*.webp')):
            shutil.copy(f, d / 'assets/img' / f.name)
    used = {f.stem for f in (dist / 'assets/img').glob('*.webp') if f'/img/{f.stem}.webp' in alltext}
    for d in (dist, pv):
        for f in (d / 'assets/img').glob('*.webp'):
            if f.stem not in used: f.unlink()
    # 書体：使っている文字だけに絞る
    chars = ''.join(sorted(set(re.sub(r'\s', '', alltext + js + css)))) + ' 　'
    (ROOT / 'chars.txt').write_text(chars, encoding='utf-8')
    src = ROOT / 'fonts-src'
    jobs = [(src / f'zen-kaku-gothic-new-japanese-{w}-normal.woff2', f'zkgn-{w}', chars) for w in (400, 500, 700, 900)]
    jobs += [(src / f'barlow-condensed-latin-{w}-normal.woff2', f'barlow-{w}', '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:.,/¥〜-©[] ') for w in (500, 600)]
    for f, name, text in jobs:
        o = dist / f'assets/fonts/{name}.woff2'
        subprocess.run([sys.executable, '-m', 'fontTools.subset', str(f), f'--text={text}', '--flavor=woff2', f'--output-file={o}', '--layout-features=*', '--no-hinting'], check=True, capture_output=True)
        shutil.copy(o, pv / f'assets/fonts/{name}.woff2')
    # robots.txt と sitemap.xml
    (dist / 'robots.txt').write_text(f'# 検索用もAI学習用も、クローラーはすべて許可する\nUser-agent: *\nAllow: /\nDisallow: /contact/thanks/\n\nSitemap: {U}/sitemap.xml\n')
    urls = ''.join(f'<url><loc>{U}{p["path"]}</loc></url>' for p in PAGES if not p.get('noindex'))
    (dist / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    # 穴埋めリスト
    md = ['# 穴埋めリスト', '', 'サイトの中で ［ ］ のまま残っている箇所です。黄色く表示されています。中身が決まったら教えてください。', '']
    common = sorted(set(ANA.findall(re.sub(r'<[^>]+>', ' ', B.header('') + B.footer()))))
    md += ['## 全ページ共通（ヘッダーとフッター）', ''] + [f'- {c}' for c in common] + ['']
    for p, found in holes:
        if not found: continue
        md += [f'## {p.get("name", "トップ")}（{p["path"]}）', '']
        seen = {}
        for f in found: seen[f] = seen.get(f, 0) + 1
        md += [f'- {k}' + (f'　×{v}' if v > 1 else '') for k, v in seen.items()] + ['']
    if not THEME: (ROOT / '穴埋めリスト.md').write_text('\n'.join(md), encoding='utf-8')
    print('pages', len(PAGES), '| preview kb', (pv / 'index.html').stat().st_size // 1024, '| fonts kb', sum(f.stat().st_size for f in (dist / 'assets/fonts').glob('*')) // 1024, '| imgs', len(used), '| holes', sum(len(f) for _, f in holes))
    for p in PAGES:
        t, d = len(p['title']), len(p['desc'])
        flag = ('' if 30 <= t <= 60 or p.get('noindex') or p['id'] in ('about', 'privacy') else ' <-- title') + ('' if 80 <= d <= 120 or p.get('noindex') else ' <-- desc')
        print(f'  {p["path"]:34} title {t:3} desc {d:3}{flag}')

if __name__ == '__main__':
    build()
