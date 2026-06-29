#!/usr/bin/env python3
"""stage-adfirst.py , staget den ad-first Feed (14 Posts) in den Auto-Cloud-Poster.
Carousels (Spektrum/Transform) = fertige 1080x1350 Slides. Stills = brand-* PNG -> JPG 4:5.
Reels = story-* + kinetic-* MP4. 1 Post/Tag ab 2026-06-30, 12:30 Berlin.
Backup der alten queue, nicht-destruktiv ausser bewusstem Queue-Ersatz."""
import os, json, shutil, subprocess
from datetime import datetime, timedelta

SRC = os.path.expanduser("~/dev/sola-instagram")
REPO = os.path.expanduser("~/dev/sola-auto-cloud")
ASSETS = os.path.join(REPO, "assets")
BERLIN = "+02:00"
BASE = datetime(2026, 6, 30)  # morgen
TAGS_IMG = "#aiproductphotography #produktfotografie #beautyeditorial #d2cmarketing #aicreative #kiwerbung"
TAGS_VID = "#aivideo #adcreative #kiwerbung #contentcreation #marketingdeutschland #aiugc"

S = lambda p: os.path.join(SRC, p)
SP = "produkt-ads/spektrum/slides/"
TR = "produkt-ads/transform/slides/"
PB = "reel-engine/public/"
RN = "reel-engine/out/nacht/"
KN = "reel-engine/out/kinetic/"

# (typ, title, [quellen], caption, crop45?)
PLAN = [
 ("carousel","spektrum , jede farbe",
  [SP+f"{i:02d}.png" for i in range(9)],
  "eine ki, jede farbwelt. von rosé bis gold, von serum bis sneaker.\n\nswipe und sag mir welche farbe zu deiner marke passt.", False),
 ("carousel","vorher , nachher",
  [TR+f"{i:02d}.png" for i in range(5)],
  "produktfoto rein, ad raus. swipe für drei verwandlungen.\n\ndein produkt könnte das nächste sein. schreib mir.", False),
 ("reel","energy , bewegt",[KN+"kinetic-energy.mp4"],
  "aus einem standbild wird ein bewegter spot. wörter, licht, tempo.\n\nso wird aus deinem produktfoto ein reel das stoppt.", False),
 ("image","emerald serum",[PB+"brand-emerald.png"],
  "sattes grün, klares serum. so sieht ein hero aus der im feed stoppt.\n\nwelche farbe hätte dein produkt verdient?", True),
 ("reel","parfum , lichtmoment",[RN+"story-parfum.mp4"],
  "ein flacon, ein lichtmoment, das gefühl von einem teuren spot.\n\nproduktvideo das wirkt , wo würdest du sowas einsetzen?", False),
 ("image","rosé lippenstift",[PB+"brand-lilac.png"],
  "rosé auf flieder. zart, und trotzdem laut.\n\nnicht jede ad muss schreien um gesehen zu werden.", True),
 ("reel","sneaker , bewegung",[RN+"story-sneaker.mp4"],
  "sneaker, bewegung, kante. produktvideo geht auch hart und fashion, nicht nur soft.\n\nwelcher vibe ist deine marke?", False),
 ("image","energy , splash",[PB+"brand-energy.png"],
  "schwarz, gold, splash. volle wucht.\n\nmanche marken brauchen genau diese energie im feed.", True),
 ("reel","cobalt , bewegt",[KN+"kinetic-cobalt.mp4"],
  "kleines budget, grosse wirkung. ein still, in bewegung gesetzt.\n\nruhig, teuer, und trotzdem ein scroll-stopper.", False),
 ("image","cobalt flacon",[PB+"brand-cobalt.png"],
  "milchglas auf tiefem blau. ruhig, teuer, sofort premium.\n\nswipe-stopper ganz ohne grelle farbe.", True),
 ("reel","lippenstift , detail",[RN+"story-lipstick.mp4"],
  "es ist nie nur ein lippenstift. ein detail, groß inszeniert, und es verkauft.\n\nmagst du sowas für dein produkt?", False),
 ("image","amber , warm",[PB+"brand-serum.png"],
  "goldenes licht, weiche tiefe, fast zum anfassen.\n\nwarme produkte verdienen warmes licht.", True),
 ("reel","uhr , macro",[RN+"story-uhr.mp4"],
  "macro, mechanik, ruhe. selbst ein kleines detail wird zur ad.\n\nwas ist das besondere detail an deinem produkt?", False),
 ("image","tech , nicht nur beauty",[PB+"brand-tech.png"],
  "nicht nur beauty. auch hartes produkt sitzt sauber im licht.\n\nwelche kategorie ist deine?", True),
]

def to_jpg(src,dst,crop45):
    subprocess.run(["sips","-s","format","jpeg","-s","formatOptions","90",src,"--out",dst],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if crop45:
        subprocess.run(["sips","--resampleWidth","1080",dst],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(["sips","-c","1350","1080",dst],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def main():
    qp=os.path.join(REPO,"queue.json")
    if os.path.exists(qp):
        n=1
        while os.path.exists(os.path.join(REPO,f"queue.backup-{n}.json")): n+=1
        shutil.copy(qp,os.path.join(REPO,f"queue.backup-{n}.json")); print(f"backup queue.backup-{n}.json")
    os.makedirs(ASSETS,exist_ok=True)
    queue=[]
    for i,(typ,title,srcs,cap,crop45) in enumerate(PLAN,start=1):
        dt=(BASE+timedelta(days=i-1)).replace(hour=12,minute=30)
        iso=dt.strftime("%Y-%m-%dT%H:%M:00")+BERLIN
        out=[]
        for j,s in enumerate(srcs,start=1):
            sp=S(s)
            if not os.path.exists(sp): raise SystemExit(f"FEHLT: {sp}")
            if s.lower().endswith(".mp4"):
                name=f"a{i:02d}_{j}.mp4"; shutil.copy(sp,os.path.join(ASSETS,name))
            else:
                name=f"a{i:02d}_{j}.jpg"; to_jpg(sp,os.path.join(ASSETS,name),crop45)
            out.append(f"assets/{name}")
        tags=TAGS_VID if typ=="reel" else TAGS_IMG
        queue.append({"id":i,"datetime":iso,"type":typ,"title":title,
                      "assets":out,"caption":cap+"\n\n"+tags,"approved":True,"posted":False})
        print(f"#{i:02d} {typ:8} {title}  ({len(out)} asset/s)")
    json.dump(queue,open(qp,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print(f"\nqueue.json: {len(queue)} posts, 1/Tag ab {BASE.date()} 12:30")

if __name__=="__main__": main()
