import json

logos = json.load(open("/tmp/logos.json"))
colors = {
 "FLCN":"#1b9e4b","TL":"#2a6fb0","TUN":"#00b3c4","BB":"#f5c518","TS":"#d32f2f",
 "PARI":"#ff6a00","YDX":"#ff5a3c","GLY":"#6b7280","XG":"#d4a017","LGD":"#b5179e",
 "AUR":"#7c4dff","OG":"#2e7d5b",
}
names = {
 "FLCN":"Team Falcons","TL":"Team Liquid","TUN":"Tundra Esports","BB":"BetBoom Team",
 "TS":"Team Spirit","PARI":"PARIVISION","YDX":"Team Yandex","GLY":"GLYPH",
 "XG":"Xtreme Gaming","LGD":"LGD Gaming","AUR":"Aurora Gaming","OG":"OG",
}
schedule = [
 ("10:00","FLCN","TL"),("10:00","TUN","BB"),
 ("11:10","TS","PARI"),("11:10","YDX","GLY"),
 ("12:20","XG","LGD"),("13:30","FLCN","BB"),
 ("14:40","TS","OG"),("15:50","AUR","XG"),
 ("15:50","YDX","LGD"),("17:00","FLCN","PARI"),
 ("17:00","BB","GLY"),("18:10","TUN","LGD"),
 ("18:10","TL","OG"),
]

def mark(tag):
    uri = logos.get(tag)
    if uri:
        return f'<img class="logo" src="{uri}" alt="{tag}" loading="lazy">'
    return f'<span class="badge" style="background:{colors[tag]}">{tag}</span>'

def left(tag):  # name then logo (logo toward centre)
    return f'<span class="side left"><span class="name">{names[tag]}</span> {mark(tag)}</span>'
def right(tag): # logo then name
    return f'<span class="side right">{mark(tag)} <span class="name">{names[tag]}</span></span>'

rows = []
for t,a,b in schedule:
    rows.append(
f'''    <div class="match">
      <span class="time">{t}</span>
      {left(a)}
      <span class="mid">vs</span>
      {right(b)}
    </div>''')
block = "\n".join(rows)

html = open("/home/user/dota-digest/index.html").read()
start = "blastdotab</a>).</p>\n"
end = "\n    <p class=\"note\">⚠️ Розклад за Liquipedia"
i = html.index(start)+len(start)
j = html.index(end)
html = html[:i] + "\n" + block + html[j:]
open("/home/user/dota-digest/index.html","w").write(html)
print("ok, size", len(html))
