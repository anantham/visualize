#!/usr/bin/env python3
"""Inspect a logged-in chat UI to find the Deep Research control's selector.
Dumps interactive elements (+ anything matching deep/research/search), tries
opening composer menus, screenshots. Usage:
    uv run --with playwright inspect_ui.py --provider gemini|chatgpt|grok
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
STATE = Path.home()/".atlas"/"browser-state"
URLS = {"chatgpt":("chatgpt.com","https://chatgpt.com/"),
        "gemini":("gemini.google.com","https://gemini.google.com/app"),
        "grok":("grok.com","https://grok.com/")}
def log(*a): print(*a, file=sys.stderr, flush=True)

DUMP = """() => {
  const norm = s => (s||'').replace(/\\s+/g,' ').trim().slice(0,50);
  const out = [];
  const els = document.querySelectorAll('button,[role=button],[role=menuitem],[role=switch],[role=option],a,[contenteditable=true]');
  for (const e of els) {
    const r = e.getBoundingClientRect();
    const vis = r.width>0 && r.height>0;
    out.push({tag:e.tagName.toLowerCase(), role:e.getAttribute('role')||'', vis,
      text:norm(e.innerText||e.textContent), aria:norm(e.getAttribute('aria-label')),
      testid:e.getAttribute('data-testid')||'', title:norm(e.getAttribute('title'))});
  }
  // anything mentioning deep/research/search anywhere
  const hits=[];
  for (const e of document.querySelectorAll('*')) {
    const t=(e.getAttribute&&(e.getAttribute('aria-label')||'')+' '+(e.getAttribute('data-testid')||''))+' '+norm(e.innerText);
    if (/deep ?research|deep ?search|deepersearch/i.test(t) && e.children.length<3) {
      hits.push({tag:e.tagName.toLowerCase(), text:norm(e.innerText), aria:norm(e.getAttribute&&e.getAttribute('aria-label')), testid:e.getAttribute&&e.getAttribute('data-testid')});
    }
  }
  return {out, hits};
}"""

def show(d, label):
    log(f"\n===== {label} =====")
    log("-- elements matching deep/research/search --")
    seen=set()
    for h in d["hits"]:
        k=str(h)
        if k in seen: continue
        seen.add(k); log("  ", h)
    log("-- visible buttons/menuitems --")
    for e in d["out"]:
        if not e["vis"]: continue
        if e["text"] or e["aria"] or e["testid"]:
            log(f"   [{e['tag']}/{e['role']}] text={e['text']!r} aria={e['aria']!r} testid={e['testid']!r}")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--provider",required=True,choices=list(URLS))
    ap.add_argument("--site", help="override browser-state profile dir (e.g. gemini.google.com-2)")
    a=ap.parse_args(); site,url=URLS[a.provider]
    if a.site: site=a.site
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        ctx=pw.chromium.launch_persistent_context(user_data_dir=str(STATE/site),headless=False,
            channel="chrome",args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"])
        page=ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            page.goto(url,wait_until="domcontentloaded"); time.sleep(4)
            show(page.evaluate(DUMP), f"{a.provider} INITIAL")
            # try opening composer menus
            for opener in ["Add","Tools","Choose tool","More","Attach","Plus","Add photos & files"]:
                try:
                    b=page.get_by_role("button",name=opener).first
                    if b.is_visible(timeout=800):
                        b.click(timeout=2000); time.sleep(1.2)
                        show(page.evaluate(DUMP), f"after opening '{opener}'")
                        page.keyboard.press("Escape"); time.sleep(0.4)
                except Exception: pass
            outdir=Path(__file__).parent/"out"; outdir.mkdir(exist_ok=True)
            page.screenshot(path=str(outdir/f"inspect_{a.provider}.png"))
            log(f"\nscreenshot -> out/inspect_{a.provider}.png")
        finally:
            try: ctx.close()
            except Exception: pass
if __name__=="__main__": sys.exit(main())
