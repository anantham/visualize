#!/usr/bin/env python3
"""Reopen a provider's most-recent conversation from history and extract its
text (for Deep Research reports the live poller couldn't read). Saves the
longest text block on the page. Usage:
    uv run --with playwright grab_chat.py --provider chatgpt --output OUT.md
        [--match "History of Ideas"] [--timeout 600] [--headless]
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
STATE = Path.home()/".atlas"/"browser-state"
URLS = {"chatgpt":("chatgpt.com","https://chatgpt.com/"),
        "gemini":("gemini.google.com","https://gemini.google.com/app"),
        "grok":("grok.com","https://grok.com/")}
def log(*a): print(*a, file=sys.stderr, flush=True)

# Robust extractor: the longest innerText among likely answer containers.
BEST = """() => {
  const sel = '[data-message-author-role="assistant"], .markdown, [data-testid*="conversation-turn"], article, main, model-response';
  let best='';
  for (const c of document.querySelectorAll(sel)) {
    const t = c.innerText || '';
    if (t.length > best.length) best = t;
  }
  const researching = /researching|is researching|working on it|i'?m on it/i.test(document.body.innerText.slice(0,4000));
  return { text: best, researching };
}"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, choices=list(URLS))
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--match", default="", help="substring to pick a specific history chat")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--headless", action="store_true")
    a = ap.parse_args()
    site, url = URLS[a.provider]
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(STATE/site), headless=a.headless, channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded"); time.sleep(4)
            convo_sel = {"chatgpt":'a[href*="/c/"]', "gemini":'a[href*="/app/"], [data-test-id*="conversation"]',
                         "grok":'a[href*="/chat/"], a[href*="/c/"]'}[a.provider]
            def list_convos():
                return page.eval_on_selector_all(convo_sel,
                    "els => els.map(e => ({href: e.getAttribute('href'), text: (e.innerText||'').trim().slice(0,70)}))")
            convos = list_convos()
            if not convos:  # sidebar may be collapsed
                for nm in ("Open sidebar","Show sidebar","Toggle sidebar","Open menu"):
                    try:
                        page.get_by_role("button", name=nm).first.click(timeout=1500); time.sleep(1.2); break
                    except Exception: pass
                convos = list_convos()
            log(f"  found {len(convos)} conversations; first: {[c['text'] for c in convos[:4]]}")
            target = None
            if a.match:
                for c in convos:
                    if a.match.lower() in (c["text"] or "").lower(): target = c; break
            if not target and convos: target = convos[0]
            if target and target.get("href"):
                href = target["href"]; full = href if href.startswith("http") else url.split("/app")[0].rstrip("/") + href
                log(f"  opening: {target['text']!r} -> {full}")
                page.goto(full, wait_until="domcontentloaded"); time.sleep(5)
            else:
                log("  WARNING: no conversation link found")
                try:
                    anchors = page.eval_on_selector_all('a', "els=>els.slice(0,25).map(e=>({h:e.getAttribute('href'),t:(e.innerText||'').trim().slice(0,40)}))")
                    log("  anchors: "+str(anchors))
                    log("  body[:300]: "+(page.inner_text('body')[:300].replace(chr(10),' ')))
                    page.screenshot(path=str(a.output.parent/'debug_chatgpt.png'))
                    log("  screenshot -> out/debug_chatgpt.png")
                except Exception as e: log("  debug dump failed:", repr(e))
            log("  waiting for content…")
            # poll for stable, substantial text
            deadline = time.time()+a.timeout; prev=""; stable=None; t0=time.time(); lastlog=0
            while time.time() < deadline:
                info = page.evaluate(BEST); txt = info["text"].strip()
                if time.time()-lastlog >= 15:
                    log(f"  t={int(time.time()-t0)}s len={len(txt)} researching={info['researching']}"); lastlog=time.time()
                if len(txt) > 800 and not info["researching"] and txt == prev:
                    if stable is None: stable=time.time()
                    elif time.time()-stable >= 8:
                        break
                else:
                    if txt != prev: stable=None; prev=txt
                time.sleep(3)
            final = page.evaluate(BEST)["text"].strip()
            if not final: log("error: no text extracted"); return 1
            a.output.parent.mkdir(parents=True, exist_ok=True)
            a.output.write_text(final)
            log(f"  wrote {len(final)} chars -> {a.output}")
            log(f"  FILE markers: {final.count('===FILE:')}")
            return 0
        finally:
            try: ctx.close()
            except Exception: pass
if __name__ == "__main__": raise SystemExit(main())
