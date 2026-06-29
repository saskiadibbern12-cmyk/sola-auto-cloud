#!/usr/bin/env python3
"""
stage-feed-week1.py , staged den neuen @sola.makes Feed-Plan (Woche 1, 14 Posts)
aus dem ECHTEN Material in ~/dev/sola-instagram/ in den Auto-Cloud-Poster.

Macht:
  1) Backup der alten queue.json (queue.backup-<n>.json)
  2) PNG -> JPG (via sips), MP4 kopieren, sauber benannt nach id, in assets/
  3) neue queue.json schreiben (Liste, approved=true, posted=false,
     caption = text + hashtags, datetime mit Berlin-Offset +02:00)
Nicht-destruktiv ausser dem bewussten Ersetzen der queue + dem Aufraeumen
verwaister alter assets (werden vorher gelistet).
"""
import os, json, shutil, subprocess
from datetime import datetime, timedelta, timezone

SRC = os.path.expanduser("~/dev/sola-instagram")
REPO = os.path.expanduser("~/dev/sola-auto-cloud")
ASSETS = os.path.join(REPO, "assets")
BERLIN = "+02:00"  # CEST (Sommer)
BASE = datetime(2026, 6, 29)  # Montag
DAYOFF = {"Mo":0,"Di":1,"Mi":2,"Do":3,"Fr":4,"Sa":5,"So":6}

# (wd, time, type, title, [quell-assets relativ zu SRC], caption, hashtags)
PLAN = [
 ("Mo","12:30","image","amber hero",
  ["produkt-ads/kampagne-1/01-hero.png"],
  "manchmal fehlt einem produkt nur das richtige licht.\n\ndiese flasche im goldlicht ist komplett mit ki gebaut. kein studio, kein fotograf, ein nachmittag.\n\nwürde dein produkt so im feed auffallen?",
  "#aiproductphotography #produktfotografie #beautyeditorial #d2cmarketing #aicreative #skincare"),
 ("Mo","18:30","reel","stoff im wind",
  ["outputs/REELS/reel-3-stoff-wind.mp4"],
  "nur stoff der im wind atmet und goldenes licht.\n\nso eine einstellung kostet normal einen ganzen drehtag. die hier ist in minuten entstanden.\n\nwürdest du den unterschied sehen?",
  "#aivideo #fashionfilm #editorial #aicreative #slowmotion #aesthetic"),
 ("Di","12:30","image","serum auf der haut",
  ["produkt-ads/kampagne-1/03-in-use.png"],
  "produkt auf der haut, dewy, dieses greifbare gefühl. und doch ist niemand hier echt.\n\ngenau dieser in-use-look verkauft, weil er nah und menschlich wirkt.\n\nwürdest du es kaufen?",
  "#aiugc #inusephoto #beautymarketing #produktfotografie #aicreative #skincare"),
 ("Di","18:30","reel","botanik",
  ["outputs/REELS/reel-7-botanik.mp4"],
  "pflanzen, licht, ruhe. ein moment der wirkt als hätte jemand stundenlang gewartet.\n\nkein set, kein dreh, alles ki.\n\nwo würdest du so einen vibe einsetzen?",
  "#aivideo #botanical #editorial #aicreative #wellness #aesthetic"),
 ("Mi","12:30","image","flatlay mit botanik",
  ["produkt-ads/kampagne-1/04-flatlay.png"],
  "ein sauberes flatlay für shop oder feed, lavendel und eukalyptus dazu, alles auf travertin.\n\nkein tisch-styling, kein studio-nachmittag. mit ki in minuten fertig statt in tagen.\n\nwie viele produktbilder bräuchtest du diesen monat?",
  "#flatlay #aiproductphotography #produktfotografie #ecommercedeutschland #aicreative #contentbatch"),
 ("Mi","18:30","reel","wasser & haut",
  ["outputs/REELS/reel-5-wasser-haut.mp4"],
  "wasser auf der haut, langsam, in nahaufnahme. so eine textur einzufangen kostet normal einen profi-dreh.\n\nich teile diese tests offen, weil ich glaube dass marken bald genau so arbeiten.\n\nwürdest du es dir auf einem produkt vorstellen?",
  "#aivideo #beautyreel #buildinginpublic #aicreative #contentcreation #aesthetic"),
 ("Do","12:30","image","öltropfen macro",
  ["produkt-ads/kampagne-1/02-macro-drop.png"],
  "kein produkt verkauft sich über die flasche, sondern über textur und licht.\n\ndiesen goldenen tropfen hat nie ein makro-objektiv gesehen, das ist alles ki.\n\nworauf fällt dein blick zuerst?",
  "#aiproductphotography #makrofotografie #beautyeditorial #produktdesign #aicreative #skincare"),
 ("Do","18:30","carousel","real oder ki?",
  ["outputs/soft-feminine/frau-veil-1.png","outputs/soft-feminine/frau-curls-1.png",
   "outputs/soft-feminine/frau-fabric-1.png","outputs/soft-feminine/frau-curls-3.png",
   "outputs/soft-feminine/frau-veil-2.png"],
  "real oder ki? schau genau hin.\n\nkeine dieser frauen hat je existiert. kein casting, kein shooting, nur ein nachmittag mit ki. genau so können kampagnengesichter für deine marke aussehen, ohne gage.\n\nwelche hätte dich am meisten getäuscht? schreibs in die kommentare.",
  "#aiugc #aigeneratedimages #kiwerbung #marketingdeutschland #adcreative #aimodel"),
 ("Fr","12:30","image","cremetextur",
  ["produkt-ads/kampagne-1/06-texture.png"],
  "ein strich creme auf stein, weiches licht. mehr braucht eine textur-anzeige nicht.\n\nkein food-stylist, kein set, alles ki an einem nachmittag.\n\nwelche textur würde dein produkt verkaufen?",
  "#texture #aiproductphotography #beautyeditorial #produktdesign #aicreative #skincare"),
 ("Fr","18:30","reel","strand & sonne",
  ["outputs/REELS/reel-8-strand-sonne.mp4"],
  "diese leichtigkeit sieht aus wie ein teurer reisedreh. in echt hat niemand einen flieger genommen.\n\nwenn deine marke diesen sommer-vibe braucht, weißt du jetzt dass er auch ohne reise geht.\n\nspeicher dirs fürs nächste sommer-briefing.",
  "#aivideo #summervibes #travelaesthetic #aicreative #beautyreel #editorial"),
 ("Sa","12:30","image","badezimmer-szene",
  ["produkt-ads/kampagne-1/05-environmental.png"],
  "produkt im echten raum, morgenlicht am fenster, handtuch daneben. so ein lifestyle-shot macht eine marke greifbar.\n\nkein location-scout, keine crew, alles ki.\n\nwürdest du in diesem moment dein produkt benutzen?",
  "#lifestylephotography #aiproductphotography #beautyeditorial #d2cmarketing #aicreative #wellness"),
 ("Sa","18:30","reel","haar & licht",
  ["outputs/REELS/reel-6-haar-licht.mp4"],
  "ein ganz ruhiger moment, licht das langsam durchs haar zieht.\n\nkein model war hier, kein set. genau so ruhig kann ki wirken.\n\nwo würdest du es zuerst einsetzen?",
  "#aivideo #beautyreel #aicreative #contentcreation #aesthetic #slowmotion"),
 ("So","12:30","image","flasche im wasser",
  ["produkt-ads/kampagne-1/08-water.png"],
  "flasche im wasser, ringe die sich ausbreiten, warmes licht drin gefangen.\n\nso ein hero-shot wäre normal ein halber drehtag. hier waren es minuten.\n\nwürde der dich im feed stoppen?",
  "#aiproductphotography #heroshot #beautyeditorial #produktdesign #aicreative #skincare"),
 ("So","18:30","reel","schönheit, ganz ruhig",
  ["outputs/REELS/reel-1-schoenheit.mp4"],
  "zum wochenende ein ruhiger, schöner take. nichts lautes, nur licht und stimmung.\n\nalles ki, kein dreh. ich bau diese welt sonntags abends einfach so.\n\nwas davon würdest du nie für ki halten?",
  "#aivideo #beautyreel #aicreative #contentcreation #aesthetic #editorial"),
]

def png_to_jpg(src, dst):
    subprocess.run(["sips","-s","format","jpeg","-s","formatOptions","90",src,"--out",dst],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    # 1) Backup alte queue
    qp = os.path.join(REPO, "queue.json")
    if os.path.exists(qp):
        n = 1
        while os.path.exists(os.path.join(REPO, f"queue.backup-{n}.json")): n += 1
        shutil.copy(qp, os.path.join(REPO, f"queue.backup-{n}.json"))
        print(f"backup -> queue.backup-{n}.json")

    # 2) alte assets merken (zum spaeteren Aufraeumen)
    old = set(os.listdir(ASSETS)) if os.path.isdir(ASSETS) else set()
    os.makedirs(ASSETS, exist_ok=True)

    queue = []
    used = set()
    for i,(wd,tm,typ,title,srcs,cap,tags) in enumerate(PLAN, start=1):
        hh,mm = tm.split(":")
        dt = (BASE + timedelta(days=DAYOFF[wd])).replace(hour=int(hh), minute=int(mm))
        iso = dt.strftime("%Y-%m-%dT%H:%M:00") + BERLIN
        out_assets = []
        for j,s in enumerate(srcs, start=1):
            sp = os.path.join(SRC, s)
            if not os.path.exists(sp):
                raise SystemExit(f"FEHLT: {sp}")
            ext = ".mp4" if s.lower().endswith(".mp4") else ".jpg"
            name = f"{i:02d}_{j}{ext}"
            dp = os.path.join(ASSETS, name)
            if ext == ".mp4":
                shutil.copy(sp, dp)
            else:
                png_to_jpg(sp, dp)
            out_assets.append(f"assets/{name}")
            used.add(name)
            print(f"#{i:02d} {name}  <-  {s}")
        queue.append({
            "id": i, "datetime": iso, "type": typ, "title": title,
            "assets": out_assets,
            "caption": cap + "\n\n" + tags,
            "approved": True, "posted": False,
        })

    # 3) queue schreiben
    json.dump(queue, open(qp,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nqueue.json geschrieben: {len(queue)} posts")

    # 4) verwaiste alte assets listen (nicht autom. loeschen -> Sicherheit)
    orphan = sorted(old - used)
    if orphan:
        print(f"\n{len(orphan)} alte, jetzt ungenutzte assets (manuell loeschbar):")
        print("  " + " ".join(orphan))

if __name__ == "__main__":
    main()
