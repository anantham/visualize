#!/usr/bin/env python3
"""Open the Gemini browser-state profile headed so the user can sign in once.
Polls until signed-in (or the window is closed / timeout), then closes cleanly
so the persisted session is reusable by deep_research.py."""
from __future__ import annotations
import sys, time
from pathlib import Path
STATE = Path.home()/".atlas"/"browser-state"/"gemini.google.com"
def log(*a): print(*a, file=sys.stderr, flush=True)

SIG = """() => {
  const url = location.href;
  const onChooser = /accounts\\.google\\.com|signin|ServiceLogin/i.test(url);
  // Strong logged-in signal: the Google account avatar button on the Gemini app.
  const acct = document.querySelector('a[aria-label*="Google Account"], [aria-label*="@gmail.com"], img[alt*="@gmail.com"]');
  const signin = Array.from(document.querySelectorAll('a,button')).some(e =>
     /^sign ?in$/i.test((e.innerText||'').trim()) || /\\bsign ?in\\b/i.test(e.getAttribute('aria-label')||''));
  const onGeminiApp = /gemini\\.google\\.com\\/app/.test(url);
  return { signedIn: !!acct && !onChooser && onGeminiApp && !signin, onChooser, signin, acct: !!acct, url };
}"""

def main():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(STATE), headless=False, channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
            log(">>> A Chrome window is open on Gemini.")
            log(">>> Complete the FULL Google sign-in (pick account + password/2FA).")
            log(">>> I will NOT close the window until your account avatar appears.")
            ok = 0
            GRACE = 5   # ignore first ~15s so a loading page can't false-positive
            for i in range(320):              # ~960s
                try:
                    if page.is_closed():
                        log("window closed by user; saving whatever session exists."); break
                    sig = page.evaluate(SIG)
                    if i >= GRACE and sig.get("signedIn"):
                        ok += 1
                    else:
                        ok = 0
                    if i % 6 == 0:
                        log(f"  t={i*3}s signedIn={sig.get('signedIn')} acct={sig.get('acct')} "
                            f"signin={sig.get('signin')} url={sig.get('url')[:60]}")
                    if ok >= 3:   # stable ~9s of a real logged-in app state
                        log("LOGIN CONFIRMED — avatar present on Gemini app. Saving session.")
                        time.sleep(3); break
                except Exception:
                    pass
                time.sleep(3)
            else:
                log("timeout (15+ min) waiting for sign-in.")
            return 0
        finally:
            try: ctx.close()
            except Exception: pass
if __name__ == "__main__": sys.exit(main())
