#!/usr/bin/env python3
"""
stage-assets.py — bereitet die Woche-1-Posts fuer die Instagram-API auf.
- konvertiert PNG -> JPG (IG Content-Publishing akzeptiert nur JPEG-Bilder)
- kopiert Videos (MP4) unveraendert
- legt assets/ + queue.json an (queue = Quelle der Wahrheit fuer den Cloud-Poster)

Quelle = die QUEUE aus dem Entwuerfe-Builder (keine Doppelpflege).
"""
import os, sys, json, shutil
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS = os.path.join(REPO, "assets")
SOLA = os.path.expanduser("~/dev/sola-instagram")
DRAFTS = os.path.join(SOLA, "posting", "drafts-system")

sys.path.insert(0, DRAFTS)
from build import QUEUE  # noqa  (import fuehrt main() nicht aus)

TZ = "+02:00"  # Berlin Sommerzeit (CEST). Im Winter auf +01:00 stellen.

def to_jpg(src, dst):
    im = Image.open(src).convert("RGB")
    im.save(dst, "JPEG", quality=92)

def main():
    if os.path.isdir(ASSETS): shutil.rmtree(ASSETS)
    os.makedirs(ASSETS, exist_ok=True)
    queue = []
    for i, it in enumerate(QUEUE, 1):
        files = []
        for n, a in enumerate(it["assets"], 1):
            src = os.path.join(SOLA, a)
            ext = os.path.splitext(a)[1].lower()
            if ext in (".png", ".jpg", ".jpeg"):
                out = f"{i:02d}_{n}.jpg"
                to_jpg(src, os.path.join(ASSETS, out))
            elif ext in (".mp4", ".mov"):
                out = f"{i:02d}_{n}.mp4"
                shutil.copy2(src, os.path.join(ASSETS, out))
            else:
                continue
            files.append("assets/" + out)
        # Typ bestimmen
        if any(f.endswith(".mp4") for f in files):
            mtype = "reel"
        elif len(files) > 1:
            mtype = "carousel"
        else:
            mtype = "image"
        queue.append({
            "id": i,
            "datetime": f"{it['date']}T{it['time']}:00{TZ}",
            "weekday": it["wd"],
            "slot": it["slot"],
            "type": mtype,
            "pillar": it["pillar"],
            "hero": bool(it.get("hero")),
            "title": it["title"],
            "assets": files,
            "caption": it["caption"].strip() + "\n\n" + it["hashtags"].strip(),
            "approved": True,      # diese Woche ist von Saskia in der Session freigegeben
            "posted": False,
            "posted_at": None,
            "ig_id": None,
            "error": None,
        })
    with open(os.path.join(REPO, "queue.json"), "w") as f:
        json.dump(queue, f, ensure_ascii=False, indent=1)
    sizes = sum(os.path.getsize(os.path.join(ASSETS, x)) for x in os.listdir(ASSETS))
    print(f"staged: {len(queue)} posts, {len(os.listdir(ASSETS))} assets, {sizes/1024/1024:.0f} MB")
    print("typen:", {t: sum(1 for q in queue if q['type']==t) for t in ('image','carousel','reel')})

if __name__ == "__main__":
    main()
