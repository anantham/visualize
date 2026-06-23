#!/usr/bin/env python3
"""Parse the multi-model Deep Research outputs (out/<provider>_batch*.md) and
merge them into clean vault notes, cross-verifying across providers.

The web UIs render markdown to HTML, so .innerText strips the literal `---`,
`#`, `##`, `-` syntax — but `===FILE:` markers, `key: value` fields, `[[links]]`
and `::` cruxes survive. This parser is tolerant of the de-markdowned shape.

Merge policy:
- numeric (born/died/*_lat/*_lon): median; flagged in conflicts.md if providers
  disagree beyond tolerance (dates >40y, coords >2°).
- text (thesis/desc/key_work/region/tradition): longest / majority.
- edges & cruxes & idea-travel: union across providers, with an agreement count.

Usage: uv run merge_research.py [--glob out/*_batchA.md] [--out vault-research]
"""
from __future__ import annotations
import argparse, glob, re, statistics
from pathlib import Path
HERE = Path(__file__).parent

FIELD_KEYS = {"name","born","died","uncertain","birth_place","birth_lat","birth_lon",
    "active_place","active_lat","active_lon","region","tradition","wikipedia","portrait",
    "key_work","thesis"}
SECTIONS = {  # normalized header -> (edge_type, direction) ; or special
    "influenced by":("influence","in"), "teachers":("influence","in"), "teacher":("influence","in"),
    "develops":("derivation","in"), "derives from":("derivation","in"), "builds on":("derivation","in"),
    "systematizes":("derivation","in"), "extends":("derivation","in"),
    "disagreed with":("disagreement","sym"), "critiques":("disagreement","sym"),
    "rejects":("disagreement","sym"), "opposes":("disagreement","sym"),
    "revives":("revival","in"), "revival of":("revival","in"), "reinterprets":("revival","in"),
    "cruxes":("__crux__",""), "idea travel":("__travel__","")}

def canon(name):
    n = name.strip()
    n = re.sub(r"\.md$","",n,flags=re.I)
    n = n.replace("_"," ")
    n = re.sub(r"\(.*?\)","",n)            # drop parentheticals
    n = re.sub(r"^the\s+","",n,flags=re.I)
    n = n.strip().strip(",")
    fix = {"buddha":"Buddha","siddhartha gautama":"Buddha","diogenes of sinope":"Diogenes of Sinope",
           "laozi":"Laozi","lao tzu":"Laozi","kong":"Confucius","kongzi":"Confucius"}
    return fix.get(n.lower(), n)

def num(v):
    if v is None: return None
    m = re.search(r"-?\d+(\.\d+)?", str(v))
    return float(m.group()) if m else None

def parse_link_item(line):
    lm = re.search(r"\[\[([^\]]+)\]\]", line)
    if not lm: return None
    target = lm.group(1).split("|")[0].strip()
    rest = line[line.index("]]")+2:]
    crux=None; note=None
    parts = re.split(r"\s[—–-]\s", rest, maxsplit=1)
    head = parts[0]
    if len(parts)>1: note = parts[1].strip()
    if "::" in head: crux = head.split("::",1)[1].strip()
    return {"target":target,"crux":crux,"note":note,"conjecture":"(?)" in line}

def parse_block(block, provider):
    lines = block.split("\n")
    rec = {"fields":{}, "sources":[], "desc":"", "edges":[], "cruxes":[], "travel":[], "provider":provider}
    i = 0; n = len(lines)
    # skip leading blanks
    while i<n and not lines[i].strip(): i+=1
    # frontmatter
    in_sources=False
    while i<n:
        s = lines[i].strip()
        if not s: i+=1; continue
        m = re.match(r"^([a-z_]+):\s*(.*)$", s)
        if m and m.group(1) in FIELD_KEYS:
            rec["fields"][m.group(1)] = m.group(2).strip().strip('"'); in_sources=False; i+=1; continue
        if re.match(r"^sources?:", s):
            in_sources=True
            u = re.search(r"https?://\S+", s)
            if u: rec["sources"].append(u.group())
            i+=1; continue
        if in_sources and re.match(r"^https?://", s):
            rec["sources"].append(s); i+=1; continue
        break  # body starts
    # body: first non-empty line is the (de-#'d) name heading -> skip
    while i<n and not lines[i].strip(): i+=1
    if i<n: i+=1  # skip name heading
    cur=None; desc=[]
    while i<n:
        s = lines[i].strip()
        key = re.sub(r"[:#].*$","",s).strip().lower()
        if key in SECTIONS:
            cur = SECTIONS[key]; i+=1; continue
        if s:
            if cur is None:
                desc.append(s)
            elif cur[0]=="__crux__":
                it = parse_link_item(s)
                if it: rec["cruxes"].append({"crux":it["target"],"stance":it["note"] or ""})
            elif cur[0]=="__travel__":
                tm = re.match(r"^[-•]?\s*(-?\d{1,4})\s*[—–-]\s*(.*)$", s)
                if tm: rec["travel"].append({"year":int(tm.group(1)),"text":tm.group(2).strip()})
            else:
                it = parse_link_item(s)
                if it:
                    etype,d = cur
                    rec["edges"].append({"type":etype,"dir":d,**it})
        i+=1
    rec["desc"] = " ".join(desc).strip()
    return rec

def parse_file(path, provider):
    text = Path(path).read_text()
    out = {}
    parts = re.split(r"^===FILE:\s*(.+?)\s*===\s*$", text, flags=re.M)
    # parts: [pre, name1, body1, name2, body2, ...]
    for k in range(1, len(parts), 2):
        name = canon(parts[k]); body = parts[k+1]
        if not name or name.lower() in ("name", "<name>"): continue
        rec = parse_block(body, provider)
        if not rec["fields"].get("name"): rec["fields"]["name"] = name
        out[name] = rec
    return out

def merge(records):  # records: list of recs for ONE thinker
    out = {"providers":[r["provider"] for r in records]}
    def collect(key): return [r["fields"].get(key) for r in records if r["fields"].get(key)]
    conflicts = []
    for key,tol in (("born",40),("died",40),("birth_lat",2),("birth_lon",2),("active_lat",2),("active_lon",2)):
        pairs = [(r["provider"], num(r["fields"].get(key))) for r in records if num(r["fields"].get(key)) is not None]
        vals = [v for _,v in pairs]
        if not vals: continue
        is_coord = ("lat" in key or "lon" in key)
        if max(vals)-min(vals) > tol:
            out[key] = pairs[0][1]   # divergent → first provider's value (deterministic), flagged below
            conflicts.append(f"{key}: " + str({r['provider']: r['fields'].get(key) for r in records if r['fields'].get(key)}))
        else:
            out[key] = round(statistics.median(vals), 2) if is_coord else int(round(statistics.median(vals)))
    for key in ("name","region","tradition","key_work","wikipedia","portrait","birth_place","active_place"):
        vals = collect(key)
        if vals: out[key] = max(vals, key=len) if key in ("key_work","birth_place","active_place") else vals[0]
    # thesis/desc: longest
    out["thesis"] = max((r["fields"].get("thesis","") for r in records), key=len, default="")
    out["desc"]   = max((r["desc"] for r in records), key=len, default="")
    out["uncertain"] = any(str(r["fields"].get("uncertain","")).lower()=="true" for r in records)
    # edges: union by (target,type); agreement count
    em={}
    for r in records:
        for e in r["edges"]:
            tgt=canon(e["target"]); k=(tgt,e["type"])
            if k not in em: em[k]={"target":tgt,"type":e["type"],"crux":e.get("crux"),"note":e.get("note"),"n":0,"by":[]}
            em[k]["n"]+=1; em[k]["by"].append(r["provider"])
            if not em[k]["crux"] and e.get("crux"): em[k]["crux"]=e["crux"]
            if (not em[k]["note"] or len(e.get("note") or "")>len(em[k]["note"] or "")): em[k]["note"]=e.get("note")
    out["edges"]=list(em.values())
    # cruxes union by text
    cm={}
    for r in records:
        for c in r["cruxes"]:
            k=c["crux"].lower().strip()
            if k not in cm: cm[k]=c
            elif len(c["stance"])>len(cm[k]["stance"]): cm[k]=c
    out["cruxes"]=list(cm.values())
    # travel union by (year, first 20 chars)
    tm={}
    for r in records:
        for t in r["travel"]:
            k=(t["year"], t["text"][:24].lower())
            if k not in tm: tm[k]=t
    out["travel"]=sorted(tm.values(), key=lambda t:t["year"])
    out["conflicts"]=conflicts
    return out

def y(v): return v if v is None else int(v)
def write_note(m, outdir):
    f=outdir/(re.sub(r'[\\/]', '-', m["name"])+".md")
    L=["---", f'name: {m["name"]}']
    for k in ("born","died"):
        if m.get(k) is not None: L.append(f"{k}: {y(m[k])}")
    if m.get("uncertain"): L.append("uncertain: true")
    for k in ("birth_place","birth_lat","birth_lon","active_place","active_lat","active_lon","region","tradition","wikipedia","portrait","key_work"):
        if m.get(k) not in (None,""): L.append(f"{k}: {m[k]}")
    if m.get("thesis"): L.append(f"thesis: {m['thesis']}")
    L.append(f"verified_by: {', '.join(sorted(set(m['providers'])))}")
    L.append("---\n")
    L.append(f"# {m['name']}\n")
    if m.get("desc"): L.append(m["desc"]+"\n")
    groups=[("Influenced by","influence"),("Develops","derivation"),("Disagreed with","disagreement"),("Revives","revival")]
    for title,et in groups:
        es=[e for e in m["edges"] if e["type"]==et]
        if es:
            L.append(f"## {title}")
            for e in es:
                line=f"- [[{e['target']}]]"
                if e.get("crux"): line+=f" :: {e['crux']}"
                if e.get("note"): line+=f" — {e['note']}"
                if e["n"]>1: line+=f"  _(✓{e['n']})_"
                L.append(line)
            L.append("")
    if m["cruxes"]:
        L.append("## Cruxes")
        for c in m["cruxes"]: L.append(f"- [[{c['crux']}]]"+(f" — {c['stance']}" if c['stance'] else ""))
        L.append("")
    if m["travel"]:
        L.append("## Idea travel")
        for t in m["travel"]: L.append(f"- {t['year']} — {t['text']}")
        L.append("")
    f.write_text("\n".join(L))
    return f.name

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--glob", default=str(HERE/"out"/"*_batch*.md"))
    ap.add_argument("--out", default=str(HERE.parent/"vault-research"))
    a=ap.parse_args()
    files=sorted(glob.glob(a.glob))
    if not files: print("no provider files match", a.glob); return 1
    print("parsing:", [Path(f).name for f in files])
    byThinker={}
    for f in files:
        prov=Path(f).name.split("_")[0]
        recs=parse_file(f, prov)
        for name,rec in recs.items(): byThinker.setdefault(name,[]).append(rec)
    outdir=Path(a.out); outdir.mkdir(exist_ok=True)
    conflicts=[]
    for name,recs in sorted(byThinker.items()):
        m=merge(recs); m["name"]=name; fn=write_note(m, outdir)   # canonical name (fixes links + filenames)
        if m["conflicts"]: conflicts.append((name,m["providers"],m["conflicts"]))
    # report
    rep=[f"# Cross-verification report\n", f"{len(byThinker)} thinkers from {len(files)} provider file(s).\n"]
    rep.append("## Coverage\n")
    for name,recs in sorted(byThinker.items()):
        rep.append(f"- **{name}** — {', '.join(r['provider'] for r in recs)}")
    rep.append("\n## Conflicts (providers disagree)\n")
    if not conflicts: rep.append("_None beyond tolerance._")
    for name,provs,cs in conflicts:
        rep.append(f"### {name} ({', '.join(provs)})")
        for c in cs: rep.append(f"- {c}")
    (outdir/"_conflicts.md").write_text("\n".join(rep))
    print(f"wrote {len(byThinker)} notes -> {outdir}")
    print(f"conflicts: {len(conflicts)} (see {outdir.name}/_conflicts.md)")
    return 0
if __name__=="__main__": raise SystemExit(main())
