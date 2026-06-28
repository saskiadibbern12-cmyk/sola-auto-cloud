#!/usr/bin/env python3
"""
post-instagram.py — Cloud-Poster fuer @sola.makes (Spiegel des LinkedIn-Systems).
Laeuft in GitHub Actions 3x taeglich. Liest queue.json, postet den faelligen,
freigegebenen, noch-nicht-geposteten Slot ueber die Instagram Graph API.

Assets liegen oeffentlich im selben Repo (raw.githubusercontent.com), weil die
IG-API oeffentliche image_url/video_url braucht.

ENV (GitHub Secrets/Vars):
  IG_USER_ID         Instagram-Business-Account-ID (Zahl)
  IG_ACCESS_TOKEN    Long-Lived Token (60 Tage) mit instagram_content_publish
  GITHUB_REPOSITORY  "owner/repo"  (von Actions automatisch gesetzt)
  GITHUB_REF_NAME    Branch (von Actions gesetzt, Fallback "main")
  WINDOW_MIN         optional, Faelligkeitsfenster in Min (default 50)
  FORCE_ID           optional, postet genau diese Post-id (Test via workflow_dispatch)

Fehler -> Exit 1 -> GitHub schickt Fehler-Mail (keine lautlose Stille).
"""
import os, json, time, ssl, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta, timezone

# Facebook-LOGIN-Weg: Publishing ueber graph.facebook.com mit dem Page-Token.
GRAPH = "https://graph.facebook.com/v21.0"
CTX = ssl.create_default_context()
REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUEUE_PATH = os.path.join(REPO_DIR, "queue.json")
BERLIN = timezone(timedelta(hours=2))  # CEST; Winter = +1


def env(name, required=True, default=None):
    v = os.environ.get(name, default)
    if not v and required:
        print(f"❌ ENV {name} fehlt"); raise SystemExit(1)
    return v.strip() if isinstance(v, str) else v


def graph(method, path, params):
    url = f"{GRAPH}/{path}"
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        url = url + "?" + data.decode(); data = None
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, context=CTX) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Graph {method} {path} -> HTTP {e.code}: {body}")


def raw_url(asset):
    repo = env("GITHUB_REPOSITORY", required=False, default="saskiadibbern12-cmyk/sola-auto-cloud")
    branch = env("GITHUB_REF_NAME", required=False, default="main")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{urllib.parse.quote(asset)}"


def publish_image(ig, token, asset, caption):
    c = graph("POST", f"{ig}/media", {"image_url": raw_url(asset), "caption": caption, "access_token": token})
    return _publish(ig, token, c["id"])


def publish_carousel(ig, token, assets, caption):
    children = []
    for a in assets:
        ch = graph("POST", f"{ig}/media", {"image_url": raw_url(a), "is_carousel_item": "true", "access_token": token})
        children.append(ch["id"])
    parent = graph("POST", f"{ig}/media", {
        "media_type": "CAROUSEL", "children": ",".join(children),
        "caption": caption, "access_token": token})
    return _publish(ig, token, parent["id"])


def publish_reel(ig, token, asset, caption):
    c = graph("POST", f"{ig}/media", {
        "media_type": "REELS", "video_url": raw_url(asset),
        "caption": caption, "access_token": token})
    cid = c["id"]
    # Video wird serverseitig verarbeitet -> warten bis FINISHED
    for _ in range(60):  # max ~5 min
        st = graph("GET", cid, {"fields": "status_code,status", "access_token": token})
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            raise RuntimeError(f"Reel-Verarbeitung fehlgeschlagen: {st}")
        time.sleep(6)
    else:
        raise RuntimeError("Reel-Verarbeitung Timeout (>5min)")
    return _publish(ig, token, cid)


def _publish(ig, token, creation_id):
    res = graph("POST", f"{ig}/media_publish", {"creation_id": creation_id, "access_token": token})
    return res["id"]


def main():
    ig = env("IG_USER_ID")
    token = env("IG_ACCESS_TOKEN")
    window = int(env("WINDOW_MIN", required=False, default="50"))
    force = env("FORCE_ID", required=False)

    queue = json.load(open(QUEUE_PATH, encoding="utf-8"))
    now = datetime.now(BERLIN)

    if force:
        due = [q for q in queue if str(q["id"]) == str(force)]
        if not due:
            print(f"❌ FORCE_ID {force} nicht gefunden"); raise SystemExit(1)
    else:
        due = [q for q in queue
               if q["approved"] and not q["posted"]
               and datetime.fromisoformat(q["datetime"]) <= now
               and (now - datetime.fromisoformat(q["datetime"])) <= timedelta(minutes=window)]

    if not due:
        print("nichts faellig. ok."); return

    failed = False
    for q in due:
        try:
            print(f"poste #{q['id']} ({q['type']}) {q['title']} ...")
            if q["type"] == "image":
                ig_id = publish_image(ig, token, q["assets"][0], q["caption"])
            elif q["type"] == "carousel":
                ig_id = publish_carousel(ig, token, q["assets"], q["caption"])
            elif q["type"] == "reel":
                ig_id = publish_reel(ig, token, q["assets"][0], q["caption"])
            else:
                raise RuntimeError(f"unbekannter typ {q['type']}")
            q["posted"] = True
            q["posted_at"] = now.isoformat()
            q["ig_id"] = ig_id
            q["error"] = None
            print(f"✅ gepostet, IG-Media {ig_id}")
        except Exception as e:
            q["error"] = str(e)[:500]
            failed = True
            print(f"❌ #{q['id']}: {e}")

    json.dump(queue, open(QUEUE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
