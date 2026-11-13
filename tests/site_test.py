"""サイトの動作確認： python3 tests/site_test.py（先に python3 src/build.py で docs/ を作る）
   スマホ幅で、診断・メニュー・フォームの入力確認・JSなしの表示を通しで確かめる。
   画面の写しは tests/shots/ に残す（Git には入れない）。"""
import pathlib, subprocess, sys, time
from playwright.sync_api import sync_playwright
port=8813
ROOT = pathlib.Path(__file__).resolve().parent.parent
(ROOT / 'tests' / 'shots').mkdir(exist_ok=True)
srv = subprocess.Popen([sys.executable,'-m','http.server',str(port),'-d',str(ROOT / 'docs')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
U=f'http://localhost:{port}/'
S=str(ROOT / 'tests' / 'shots') + '/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce'); pg=ctx.new_page(); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.goto(U,wait_until='networkidle')
    # --- スマホ：診断はボタンからモーダルで開く（キーボード）
    pg.focus('.dg-launch'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    print('modal open:', pg.evaluate("document.querySelector('#diag-modal').open"))
    # --- キーボードだけで診断
    pg.focus('.dg-q.is-cur input')            # 1問目の最初の選択肢
    pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(300)   # 2-3人 を選ぶ（自動で進まないこと）
    print('kbd: still Q1?', pg.evaluate("document.querySelector('.dg-q.is-cur').dataset.key"), 'checked', pg.evaluate("document.querySelector('.dg-q.is-cur input:checked')?.value"))
    pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(100)    # 4-6
    pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    print('after Enter:', pg.evaluate("document.querySelector('.dg-q.is-cur').dataset.key"), 'focus:', pg.evaluate("document.activeElement.name+'='+document.activeElement.value"))
    # 残りはタップで
    def tap(sel):
        l=pg.locator(sel); l.evaluate("e=>e.scrollIntoView({block:'center'})"); pg.wait_for_timeout(60); l.click()
    for v in ['100-300','n','y','2-3','y']:
        tap(f'.dg-q.is-cur .dg-opt:has(input[value="{v}"])'); pg.wait_for_timeout(300)
    tap('.dg-q.is-cur .dg-opt:has(input[value="photo"])'); tap('.dg-q.is-cur .dg-opt:has(input[value="edit"])'); tap('.dg-next'); pg.wait_for_timeout(250)
    tap('.dg-q.is-cur .dg-opt:has(input[value="n"])'); pg.wait_for_timeout(400)
    print('result:', pg.inner_text('#dg-result-title'), '| focus on result:', pg.evaluate("document.activeElement.classList.contains('dg-res')"))
    print('sum:', pg.inner_text('.dg-sum').replace('\n',' / '))
    pg.locator('.dg').scroll_into_view_if_needed(); pg.evaluate('scrollBy(0,-110)'); pg.wait_for_timeout(200); pg.screenshot(path=S+'ct_res.png')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    print('modal closed:', not pg.evaluate("document.querySelector('#diag-modal').open"), 'focus back:', pg.evaluate("document.activeElement.className"))
    # --- サブナビ
    pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(200)
    print('subnav at top:', pg.evaluate("document.querySelector('.subnav a[aria-current]')?.textContent"))
    pg.click('.subnav a[href="#plan"]'); pg.wait_for_timeout(300)
    print('subnav #plan opens modal:', pg.evaluate("document.querySelector('#diag-modal').open")); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    for k in ['price','works','faq']:
        pg.click(f'.subnav a[href="#{k}"]'); pg.wait_for_timeout(400)
        print(' jump', k, '->', pg.evaluate("document.querySelector('.subnav a[aria-current]')?.textContent"), 'top', pg.evaluate(f"Math.round(document.getElementById('{k}').getBoundingClientRect().top)"))
    # --- FAQ（1つだけ開く）
    pg.click('#faq details:nth-of-type(1) summary'); pg.click('#faq details:nth-of-type(2) summary'); pg.wait_for_timeout(100)
    print('faq open count:', pg.evaluate("document.querySelectorAll('#faq details[open]').length"))
    # --- メニュー（dialog）
    pg.evaluate('scrollTo(0,0)'); pg.click('.menu-btn'); pg.wait_for_timeout(300)
    print('menu open:', pg.evaluate("document.getElementById('menu').open"), 'focus in dialog:', pg.evaluate("document.getElementById('menu').contains(document.activeElement)"))
    pg.screenshot(path=S+'ct_menu.png')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    print('menu after Esc:', pg.evaluate("document.getElementById('menu').open"), 'focus back:', pg.evaluate("document.activeElement.classList.contains('menu-btn')"))
    # --- カメラ（ラジオ）
    pg.locator('#switching').scroll_into_view_if_needed(); pg.click('label.cam:has(#cam-3)'); pg.wait_for_timeout(100)
    print('cam3 shown:', pg.evaluate("getComputedStyle(document.querySelector('.shot-3')).display"), pg.evaluate("getComputedStyle(document.querySelector('.shot-1')).display"))
    print('pause btn visible (reduce):', pg.evaluate("!document.querySelector('.sw-pause').hidden"), pg.inner_text('.sw-pause'))
    # --- popover
    pg.locator('#price').scroll_into_view_if_needed(); pg.click('button[popovertarget="tip-mic"]'); pg.wait_for_timeout(200)
    print('popover open:', pg.evaluate("document.getElementById('tip-mic').matches(':popover-open')"))
    r=pg.evaluate("(()=>{const b=document.querySelector('[popovertarget=tip-mic]').getBoundingClientRect(),p=document.getElementById('tip-mic').getBoundingClientRect();return [Math.round(b.top),Math.round(p.bottom),Math.round(p.left),Math.round(p.right)]})()")
    print('  btn.top / pop.bottom / pop.left-right:', r)
    pg.screenshot(path=S+'ct_pop.png'); pg.keyboard.press('Escape')
    # --- フォーム：空で送信 → エラー表示、正しく入れて → 完了ページ
    pg.goto(U+'contact.html',wait_until='networkidle')
    print('prefill note:', pg.inner_text('.prefill')[:30], '| textarea:', pg.input_value('textarea')[:40].replace('\n',' / '), '| checked:', pg.evaluate("[...document.querySelectorAll('input[name=plan]:checked')].map(c=>c.value)"))
    pg.click('form[data-prefill] button[type=submit]'); pg.wait_for_timeout(200)
    print('invalid shown:', pg.evaluate("document.querySelectorAll('form[data-prefill] :user-invalid').length"), pg.evaluate("[...document.querySelectorAll('form[data-prefill] .err')].filter(e=>getComputedStyle(e).display!=='none').length"), 'url', pg.url[-14:])
    pg.screenshot(path=S+'ct_err.png')
    for n,v in [('date','未定'),('venue','〇〇大学'),('size','4人、100人'),('email','a@b.jp')]: pg.fill(f'form[data-prefill] input[name={n}]', v)
    pg.click('form[data-prefill] button[type=submit]'); pg.wait_for_load_state('networkidle'); print('after submit:', pg.url[-11:])
    print('errors', errs)
    # --- JS なし
    ctx2=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False); q=ctx2.new_page(); q.goto(U,wait_until='networkidle')
    print('nojs: questions visible', q.evaluate("[...document.querySelectorAll('.dg-q')].filter(e=>getComputedStyle(e).display!=='none').length"), 'menu fallback', q.evaluate("getComputedStyle(document.querySelector('.menu-fallback')).display"), 'menu btn', q.evaluate("getComputedStyle(document.querySelector('.menu-btn')).display"), 'shot1', q.evaluate("getComputedStyle(document.querySelector('.shot-1')).display"))
    q.screenshot(path=S+'ct_nojs.png', full_page=False)
    b.close()
srv.terminate()
