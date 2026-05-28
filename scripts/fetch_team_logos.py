import json, subprocess, base64, sys, urllib.parse

UA = "dota-digest/1.0 (vitaliy.babenko.ua@gmail.com) static-site-generator"
API = "https://liquipedia.net/dota2/api.php"

def curl(url, binary=False):
    out = "/tmp/_dl.bin" if binary else "/tmp/_dl.txt"
    r = subprocess.run(["curl","-sS","-L","--compressed","-A",UA,"--max-time","30",url,"-o",out])
    if r.returncode != 0:
        return None
    return open(out,"rb").read() if binary else open(out,"r",encoding="utf-8",errors="replace").read()

def api(params):
    return json.loads(curl(API+"?"+urllib.parse.urlencode(params)))

# team page title -> (short tag, distinctive keyword that must appear in the logo filename)
teams = {
    "Team Falcons":("FLCN","falcons"),"Team Liquid":("TL","liquid"),
    "Tundra Esports":("TUN","tundra"),"BetBoom Team":("BB","betboom"),
    "Team Spirit":("TS","spirit"),"PARIVISION":("PARI","parivision"),
    "Team Yandex":("YDX","yandex"),"GLYPH":("GLY","glyph"),
    "Xtreme Gaming":("XG","xtreme"),"LGD Gaming":("LGD","lgd gaming"),
    "Aurora Gaming":("AUR","aurora"),"OG":("OG","og "),
}

def pick_logo(title, kw):
    d = api({"action":"query","titles":title,"prop":"images","imlimit":"100","format":"json"})
    pages = d.get("query",{}).get("pages",{})
    page = list(pages.values())[0]
    if "missing" in page:
        return None, "page-missing"
    imgs = [i["title"] for i in page.get("images",[])]
    # filename must contain the distinctive keyword (after stripping "File:")
    cands = [t for t in imgs if t.lower().endswith(".png") and kw in t[5:].lower()]
    # also accept exact-ish
    def score(name):
        n = name.lower(); s=0
        if "allmode" in n: s+=3
        if "darkmode" in n: s+=2
        if "lightmode" in n: s+=1
        # prefer files without 'win'/'icon'/event words
        if any(w in n for w in ["win ","dacha","one ","international","major","slam","tournament"]): s-=5
        # prefer newer year
        for y in ["2026","2025","2024","2023","2022"]:
            if y in n: s+=int(y[-2:])/100; break
        return s
    cands.sort(key=score, reverse=True)
    return (cands[0] if cands else None), ("ok" if cands else "no-logo-file")

def thumb_datauri(filetitle, width=40):
    d = api({"action":"query","titles":filetitle,"prop":"imageinfo",
             "iiprop":"url","iiurlwidth":str(width),"format":"json"})
    page = list(d["query"]["pages"].values())[0]
    info = page["imageinfo"][0]
    url = info.get("thumburl") or info["url"]
    data = curl(url, binary=True)
    if not data or data[:4] != b"\x89PNG":
        return None
    if len(data) > 20000:  # keep it small
        return None
    return "data:image/png;base64,"+base64.b64encode(data).decode()

result = {}
for title, (tag, kw) in teams.items():
    logo, status = pick_logo(title, kw)
    if not logo:
        print(f"{tag:5} {title:18} -> FALLBACK ({status})", file=sys.stderr)
        result[tag] = None
        continue
    uri = thumb_datauri(logo)
    if not uri:
        print(f"{tag:5} {title:18} -> FALLBACK (thumb-failed) [{logo}]", file=sys.stderr)
        result[tag] = None
    else:
        print(f"{tag:5} {title:18} -> OK ({len(uri)} chars) [{logo}]", file=sys.stderr)
        result[tag] = uri

json.dump(result, open("/tmp/logos.json","w"))
print("DONE", file=sys.stderr)
