#!/usr/bin/env python3
"""Drive ChatGPT / Gemini / Grok Deep Research in their logged-in web UIs.

Reuses the persistent browser sessions at ~/.atlas/browser-state/<site>/
(see ~/Documents/Ongoing Local/AFFORDANCES.md — "Browser automation against
logged-in frontier-model accounts"). Inherits the user's authenticated session,
so account features (Deep Research) are available. Selectors adapted from
pramana/runner/atlas_runner/browser_chat.py + LexiconForge gemini_research.py.

Usage:
    uv run --with playwright deep_research.py \
        --provider chatgpt|gemini|grok \
        --prompt-file PROMPT.md --output OUT.md \
        [--mode deep|chat] [--timeout 2400] [--headless]
    uv run --with playwright deep_research.py --provider gemini --test   # plumbing check

Writes the assistant's final markdown to --output. Run HEADED (default) for
Deep Research — the flows can need a one-click nudge and you can watch progress.
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path

STATE_ROOT = Path.home() / ".atlas" / "browser-state"

PROVIDERS = {
    "chatgpt": {"site": "chatgpt.com", "url": "https://chatgpt.com/"},
    "gemini":  {"site": "gemini.google.com", "url": "https://gemini.google.com/app"},
    "grok":    {"site": "grok.com", "url": "https://grok.com/"},
}

def log(*a): print(*a, file=sys.stderr, flush=True)

# ---------------------------------------------------------------- input typing
def type_prompt(page, text):
    """Insert a long multi-line prompt fast; Shift+Enter for newlines so it
    doesn't submit early. Then Enter to send."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if i:
            page.keyboard.press("Shift+Enter")
        if line:
            page.keyboard.insert_text(line)
    time.sleep(1.0)
    page.keyboard.press("Enter")

# ---------------------------------------------------------------- per provider
def focus_input(page, provider):
    if provider == "chatgpt":
        tb = page.get_by_role("textbox").first
        tb.click(); return
    if provider == "gemini":
        tb = page.get_by_role("textbox", name="Enter a prompt for Gemini")
        tb.click(); return
    if provider == "grok":
        page.wait_for_selector('[contenteditable="true"]', timeout=25000)
        page.evaluate("""() => { const e=document.querySelector('[contenteditable=\"true\"]'); if(!e) throw new Error('no input'); e.focus(); }""")

def enable_deep(page, provider):
    """Turn on Deep Research where the UI exposes it. Returns True if engaged.
    Selectors validated against the live UIs 2026-06-22."""
    if provider == "chatgpt":
        # Deep Research is a menu item under the composer "Add" (+) button.
        opened = False
        for opener in ("Add", "Add files and more", "More"):
            try:
                b = page.get_by_role("button", name=opener).first
                if b.is_visible(timeout=1500):
                    b.click(timeout=2500); time.sleep(0.9); opened = True; break
            except Exception: pass
        if not opened:
            try:
                page.locator('[data-testid="composer-plus-btn"], button[aria-label*="Add"]').first.click(timeout=2500)
                time.sleep(0.9); opened = True
            except Exception: pass
        for finder in (lambda: page.get_by_role("menuitem", name="Deep research"),
                       lambda: page.get_by_text("Deep research", exact=True)):
            try:
                el = finder().first
                if el.is_visible(timeout=1500):
                    el.click(timeout=2500); time.sleep(1.0)
                    log("  ENABLED ChatGPT Deep research"); return True
            except Exception: pass
        log("  WARNING: ChatGPT Deep research item not found; using current mode"); return False
    if provider == "grok":
        # Grok Expert mode already web-searches; DeepSearch toggle is unreliable.
        for name in ("DeepSearch", "DeeperSearch", "Deep Search"):
            try:
                el = page.get_by_role("button", name=name).first
                if el.is_visible(timeout=1000):
                    el.click(timeout=2000); time.sleep(0.6); log(f"  ENABLED Grok {name}"); return True
            except Exception: pass
        log("  (Grok DeepSearch not found; Expert mode web-searches by default)"); return False
    if provider == "gemini":
        # Nested menu: "+" (Upload & tools) -> "More tools" -> "Deep research".
        opened = False
        for nm in ("Upload & tools", "New", "Open menu"):
            try:
                b = page.get_by_role("button", name=nm).first
                if b.is_visible(timeout=1500):
                    b.click(timeout=2500); time.sleep(0.9); opened = True; break
            except Exception: pass
        if not opened:
            log("  WARNING: Gemini '+' (Upload & tools) not found; logged in?"); return False
        for act in (lambda: page.get_by_role("button", name="More tools").first.click(timeout=2500),
                    lambda: page.get_by_text("More tools", exact=True).first.click(timeout=2500),
                    lambda: page.get_by_text("More tools", exact=True).first.hover()):
            try: act(); time.sleep(0.9); break
            except Exception: pass
        for finder in (lambda: page.get_by_role("menuitem", name="Deep research"),
                       lambda: page.get_by_text("Deep research", exact=True)):
            try:
                el = finder().first
                if el.is_visible(timeout=2000):
                    el.click(timeout=2500); time.sleep(1.0); log("  ENABLED Gemini Deep research"); return True
            except Exception: pass
        log("  WARNING: Gemini Deep research item not found"); return False

def maybe_start_research(page, provider):
    """Gemini shows a research PLAN with a 'Start research' button before it
    actually runs. Click it if it appears within ~70s."""
    if provider != "gemini": return
    for _ in range(35):
        for nm in ("Start research", "Start Research"):
            try:
                b = page.get_by_role("button", name=nm).first
                if b.is_visible(timeout=800):
                    b.click(timeout=2500); log("  clicked 'Start research'"); return
            except Exception: pass
        time.sleep(2)

def extract(page, provider):
    js = {
        "chatgpt": """() => { const m=document.querySelectorAll('[data-message-author-role="assistant"]'); const l=m[m.length-1]; return l? (l.innerText||''):''; }""",
        "gemini":  """() => { const m=document.querySelectorAll('model-response'); const l=m[m.length-1]; return l? (l.querySelector('.markdown')?.innerText || l.innerText || ''):''; }""",
        "grok":    """() => { const m=document.querySelectorAll('[data-testid="assistant-message"]'); const l=m[m.length-1]; return l? (l.innerText||''):''; }""",
    }[provider]
    try: return (page.evaluate(js) or "").strip()
    except Exception: return ""

def is_streaming(page, provider):
    js = {
        "chatgpt": """() => !!document.querySelector('button[aria-label="Stop answering"], button[data-testid="stop-button"], button[aria-label*="Stop"]')""",
        "gemini":  """() => !!document.querySelector('button[aria-label*="Stop"], button[aria-label*="stop"]')""",
        "grok":    """() => !!document.querySelector('button[aria-label*="Stop"], button[aria-label*="stop"]')""",
    }[provider]
    try: return bool(page.evaluate(js))
    except Exception: return False

# ---------------------------------------------------------------- wait/extract
def wait_for_answer(page, provider, timeout, deep):
    """Poll until the answer stabilizes. Deep Research can browse for many
    minutes with no stop-button, so we lean on text stability + min length."""
    MIN_LEN = 800 if deep else 3
    STABLE = 18.0 if deep else 4.0
    deadline = time.time() + timeout
    prev = ""; stable_since = None; started = False; last_log = 0; t0 = time.time()
    while time.time() < deadline:
        txt = extract(page, provider); streaming = is_streaming(page, provider)
        if time.time() - last_log >= 15:
            log(f"  t={int(time.time()-t0)}s len={len(txt)} streaming={streaming}")
            last_log = time.time()
        if len(txt) >= MIN_LEN and not started:
            started = True; log(f"  answer started (len {len(txt)})")
        if started and not streaming and txt == prev and txt:
            if stable_since is None: stable_since = time.time()
            elif time.time() - stable_since >= STABLE:
                log(f"  complete (stable {STABLE:.0f}s, len {len(txt)})"); return txt
        else:
            if txt != prev: stable_since = None; prev = txt
        time.sleep(2)
    log(f"  TIMEOUT after {timeout}s; returning len={len(prev)}"); return prev

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, choices=list(PROVIDERS))
    ap.add_argument("--prompt-file", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--mode", choices=["deep", "chat"], default="deep")
    ap.add_argument("--timeout", type=int, default=2400)
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--test", action="store_true", help="quick plumbing check (chat mode, trivial prompt)")
    args = ap.parse_args()

    cfg = PROVIDERS[args.provider]
    state_dir = STATE_ROOT / cfg["site"]
    if not state_dir.exists():
        log(f"error: no session at {state_dir}"); return 1

    if args.test:
        prompt = "Reply with exactly one word: PONG"; args.mode = "chat"; args.timeout = 90
    else:
        if not args.prompt_file or not args.output:
            log("error: --prompt-file and --output required (unless --test)"); return 1
        prompt = args.prompt_file.read_text().strip()
        if not prompt: log("error: empty prompt"); return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log("error: playwright missing. use: uv run --with playwright deep_research.py ..."); return 1

    deep = (args.mode == "deep")
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(state_dir), headless=args.headless, channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            log(f"[{args.provider}] navigating {cfg['url']}")
            page.goto(cfg["url"], wait_until="domcontentloaded"); time.sleep(3.0)
            if "accounts.google.com" in page.url or "auth" in page.url.lower() or "login" in page.url.lower():
                log(f"error: looks like a sign-in page ({page.url}); session expired"); return 1
            log(f"  title: {page.title()!r}")

            if deep:
                enable_deep(page, args.provider)
            focus_input(page, args.provider)
            log(f"  typing prompt ({len(prompt)} chars)…")
            type_prompt(page, prompt)
            log("  submitted.")
            if deep:
                maybe_start_research(page, args.provider)

            ans = wait_for_answer(page, args.provider, args.timeout, deep)
            if not ans:
                log("error: empty answer"); return 1
            if args.test:
                log(f"  TEST RESULT: {ans[:120]!r}"); return 0
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(ans)
            log(f"  wrote {len(ans)} chars -> {args.output}")
            return 0
        finally:
            try: ctx.close()
            except Exception: pass

if __name__ == "__main__":
    sys.exit(main())
