import asyncio, json, sys, time, re
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).parent; SHOTS=ROOT/"shots"; SHOTS.mkdir(exist_ok=True)
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
JS=r"""
() => {
 const cs=(el)=>el?getComputedStyle(el):null;
 const f=(el)=>{const c=cs(el); if(!c) return null; return {family:c.fontFamily.split(',')[0].replace(/["']/g,'').trim(), weight:c.fontWeight, size:Math.round(parseFloat(c.fontSize)), ls:c.letterSpacing, tt:c.textTransform, style:c.fontStyle, color:c.color, lh:c.lineHeight, text:(el.innerText||'').trim().slice(0,90)}};
 const vis=(el)=>{const r=el.getBoundingClientRect(); return r.width>0&&r.height>0;};
 const h1=[...document.querySelectorAll('h1')].find(vis)||document.querySelector('h1');
 const h2=[...document.querySelectorAll('h2')].find(vis);
 const p=[...document.querySelectorAll('main p, section p, p')].find(e=>vis(e)&&(e.innerText||'').length>80);
 const body=cs(document.body);
 const header=document.querySelector('header, nav, [class*="header"], [class*="nav"]');
 const navLinks=header?[...header.querySelectorAll('a')].filter(vis).map(a=>a.innerText.trim()).filter(t=>t&&t.length<30).slice(0,14):[];
 const imgs=[...document.images]; const vids=[...document.querySelectorAll('video')];
 const big=[...imgs,...vids].filter(vis).map(e=>({tag:e.tagName,r:e.getBoundingClientRect()})).filter(o=>o.r.width>=600).sort((a,b)=>a.r.top-b.r.top);
 const hero=big[0]?{tag:big[0].tag,w:Math.round(big[0].r.width),h:Math.round(big[0].r.height),top:Math.round(big[0].r.top)}:null;
 // also elements with background-image
 let bgHero=null; for(const el of document.querySelectorAll('div,section,header')){const c=cs(el); if(c.backgroundImage&&c.backgroundImage.startsWith('url')){const r=el.getBoundingClientRect(); if(r.width>=900&&r.height>=300&&r.top<400){bgHero={w:Math.round(r.width),h:Math.round(r.height),top:Math.round(r.top)};break;}}}
 const fonts=new Set(); document.fonts.forEach(ff=>{if(ff.status==='loaded') fonts.add(ff.family.replace(/["']/g,''))});
 const ctas=[...document.querySelectorAll('a,button')].filter(vis).map(e=>e.innerText.trim()).filter(t=>/inquir|enquir|tour|contact|availab|book|request|plan|rsvp|proposal|brochure|pricing|rates/i.test(t)&&t.length<40);
 const txt=document.body.innerText||'';
 const html=document.documentElement.outerHTML;
 const libs={swiper:/swiper/i.test(html),slick:/slick/i.test(html),flickity:/flickity/i.test(html),gsap:/gsap|ScrollTrigger/i.test(html),lenis:/lenis/i.test(html),locomotive:/locomotive/i.test(html),aos:/aos\.js|data-aos/i.test(html),lottie:/lottie/i.test(html),webgl:/three\.js|three\.min|webgl/i.test(html)};
 const badges=(html.match(/theknot|weddingwire|couples.?choice|best of weddings|zola|junebug/gi)||[]).length;
 const platform=/squarespace/i.test(html)?'squarespace':/wp-content/i.test(html)?'wordpress':/wixstatic|wix\.com/i.test(html)?'wix':/website-files\.com|webflow/i.test(html)?'webflow':/showit/i.test(html)?'showit':/shopify/i.test(html)?'shopify':/framer/i.test(html)?'framer':'custom/other';
 const svgCount=document.querySelectorAll('svg').length;
 const scriptFont=[...fonts].filter(f=>/script|hand|brush|signature|allura|great vibes|pinyon|parisienne/i.test(f));
 const caps=[...document.querySelectorAll('h1,h2,h3,a,span')].filter(vis).slice(0,300).filter(e=>cs(e).textTransform==='uppercase').length;
 return {title:document.title.slice(0,100),h1:f(h1),h2:f(h2),p:f(p),bodyBg:body.backgroundColor,bodyColor:body.color,bodyFont:body.fontFamily.split(',')[0].replace(/["']/g,''),navLinks,navCount:navLinks.length,imgCount:imgs.length,videoCount:vids.length,hero,bgHero,fonts:[...fonts].slice(0,12),scriptFont,ctas:[...new Set(ctas)].slice(0,8),libs,badges,platform,svgCount,capsCount:caps,docH:document.documentElement.scrollHeight,capacityMention:/\b\d{2,3}\s*(guests|seated|people)/i.test(txt),priceMention:/\$\s?\d{1,3},\d{3}|starting at|pricing|rates/i.test(txt),textLen:txt.length};
}
"""
async def shoot(sem, browser, row):
    id_, typ, place, url = row
    async with sem:
        rec={"id":id_,"type":typ,"place":place,"url":url}
        for vw,label in ((1440,"d"),(390,"m")):
            ctx=await browser.new_context(viewport={"width":vw,"height":900 if vw==1440 else 844},user_agent=UA,device_scale_factor=1,is_mobile=(vw==390),has_touch=(vw==390),locale="en-US")
            page=await ctx.new_page()
            try:
                resp=await page.goto(url,wait_until="domcontentloaded",timeout=45000)
                rec[f"status_{label}"]=resp.status if resp else None
                rec[f"final_{label}"]=page.url
                await page.wait_for_timeout(3500)
                for sel in ["button:has-text('Accept All')","button:has-text('Accept all')","button:has-text('ACCEPT ALL')","button:has-text('Allow all')","button:has-text('Allow All')","button:has-text('Accept Cookies')","button:has-text('Accept')","button:has-text('ACCEPT')","a:has-text('Accept')","button:has-text('OK')","button:has-text('Ok got it')","button:has-text('I agree')","button:has-text('Got it')","button:has-text('Yes')","button:has-text('CLOSE')","button:has-text('Close')","[aria-label='Close']","button:has-text('Ignore')"]:
                    try:
                        loc=page.locator(sel).first
                        if await loc.is_visible(timeout=400): await loc.click(timeout=1500); await page.wait_for_timeout(500)
                    except Exception: pass
                # scroll through to trigger lazy loads
                h=await page.evaluate("document.documentElement.scrollHeight")
                y=0
                while y<min(h,6000):
                    y+=700; await page.evaluate(f"window.scrollTo(0,{y})"); await page.wait_for_timeout(250)
                await page.evaluate("window.scrollTo(0,0)"); await page.wait_for_timeout(1200)
                await page.screenshot(path=str(SHOTS/f"{id_}-{vw}-fold.png"))
                h=await page.evaluate("document.documentElement.scrollHeight")
                await page.screenshot(path=str(SHOTS/f"{id_}-{vw}-full.png"),full_page=True,clip={"x":0,"y":0,"width":vw,"height":min(h,7000)} if h>7000 else None)
                if label=="d":
                    rec["facts"]=await page.evaluate(JS)
                else:
                    rec["mobile"]=await page.evaluate("()=>({docH:document.documentElement.scrollHeight,overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,h1Size:(()=>{const e=document.querySelector('h1');return e?Math.round(parseFloat(getComputedStyle(e).fontSize)):null})(),burger:!!document.querySelector('[class*=burger],[class*=hamburger],[aria-label*=menu i],[class*=menu-toggle],[class*=mobile-nav]')})")
            except Exception as e:
                rec[f"error_{label}"]=str(e)[:160]
            await ctx.close()
        print(id_, rec.get("status_d"), "ERR" if "error_d" in rec else "ok", flush=True)
        return rec
async def main():
    rows=[l.strip().split("|") for l in open(ROOT/"candidates.txt") if l.strip()]
    if len(sys.argv)>1: rows=[r for r in rows if r[0] in sys.argv[1:]]
    sem=asyncio.Semaphore(4)
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        res=await asyncio.gather(*[shoot(sem,browser,r) for r in rows])
        await browser.close()
    old={}
    fp=ROOT/"style-facts.json"
    if fp.exists() and len(sys.argv)>1:
        old={r["id"]:r for r in json.load(open(fp))}
    for r in res: old[r["id"]]=r
    json.dump(list(old.values()),open(fp,"w"),indent=1)
    print("done",len(old))
asyncio.run(main())
