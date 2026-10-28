import sys,json
from playwright.sync_api import sync_playwright
U=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8765/"
OUT=sys.argv[2] if len(sys.argv)>2 else "."
rep={}
def check(pg,name):
    pg.wait_for_timeout(300)
    # scroll through to trigger lazy/reveal
    h=pg.evaluate("document.body.scrollHeight")
    for y in range(0,h,400):
        pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(120)
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(1800)
    rep[name]=pg.evaluate("""()=>({broken:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src),
      docW:document.documentElement.scrollWidth,vw:innerWidth,
      wide:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.right>innerWidth+1&&!e.closest('.clips')&&getComputedStyle(e).position!=='fixed'}).slice(0,8).map(e=>e.tagName+'.'+e.className),
      fonts:[...document.fonts].map(f=>f.family+':'+f.status)})""")
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    errs=[]
    m=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    m.on("console",lambda msg: msg.type in("error","warning") and errs.append("phone:"+msg.text))
    m.on("pageerror",lambda e: errs.append("phone pageerror:"+str(e)))
    m.on("requestfailed",lambda r: errs.append("phone reqfail:"+r.url))
    m.goto(U,wait_until="networkidle"); m.wait_for_timeout(2500)
    m.screenshot(path=f"{OUT}/phone-v2-fold.png")
    check(m,"phone")
    m.screenshot(path=f"{OUT}/phone-v2-390x844-full.png",full_page=True)
    d=b.new_page(viewport={"width":1440,"height":900})
    d.on("console",lambda msg: msg.type in("error","warning") and errs.append("desk:"+msg.text))
    d.on("pageerror",lambda e: errs.append("desk pageerror:"+str(e)))
    d.on("requestfailed",lambda r: errs.append("desk reqfail:"+r.url))
    d.goto(U,wait_until="networkidle"); d.wait_for_timeout(2500)
    d.screenshot(path=f"{OUT}/desktop-v2-1440x900.png")
    check(d,"desk")
    d.screenshot(path=f"{OUT}/desktop-v2-1440-full.png",full_page=True)
    # toast test
    d.locator(".vid").first.scroll_into_view_if_needed(); d.locator(".vid").first.click(timeout=5000); d.wait_for_timeout(400); rep["toast"]=d.inner_text("#toast")
    b.close()
print(json.dumps(rep,indent=1)); print("ERRORS:",errs)
