#!/usr/bin/env python3
"""
ig-auth.py — holt den Long-Lived-Token (60 Tage) + findet deine IG-Business-Account-ID.
Einmalig (und alle 60 Tage erneut) ausfuehren:

    ! python3 ~/dev/sola-auto-cloud/scripts/ig-auth.py

Du brauchst dafuer drei Werte (zeige ich dir im Chat wo):
  1. App-ID        (aus deiner Meta-App, developers.facebook.com)
  2. App-Secret    (ebd.)
  3. Kurz-Token    (aus dem Graph API Explorer, mit Rechten instagram_basic,
                    instagram_content_publish, pages_show_list, business_management)

Das Script tauscht den Kurz-Token gegen einen 60-Tage-Token, sucht deine
IG-Business-ID, schreibt beides in .env und sagt dir den naechsten Befehl.
"""
import os, sys, json, urllib.request, urllib.parse, urllib.error, ssl

GRAPH = "https://graph.facebook.com/v21.0"
CTX = ssl.create_default_context()
ENV = os.path.join(os.path.dirname(__file__), "..", ".env")


def g(path, params):
    url = f"{GRAPH}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, context=CTX) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode()}"); sys.exit(1)


def ask(label, envname):
    v = os.environ.get(envname)
    if v: return v.strip()
    return input(f"{label}: ").strip()


def main():
    app_id = ask("App-ID", "FB_APP_ID")
    app_secret = ask("App-Secret", "FB_APP_SECRET")
    short = ask("Kurz-Token (Graph API Explorer)", "FB_SHORT_TOKEN")

    print("\n🔄 Tausche Kurz-Token gegen 60-Tage-Token ...")
    res = g("oauth/access_token", {
        "grant_type": "fb_exchange_token",
        "client_id": app_id, "client_secret": app_secret,
        "fb_exchange_token": short})
    long_token = res["access_token"]
    print(f"✅ Long-Lived-Token erhalten ({res.get('expires_in', 5184000)//86400} Tage)")

    print("🔎 Suche deine Instagram-Business-Account-ID ...")
    pages = g("me/accounts", {"access_token": long_token}).get("data", [])
    ig_id = None
    for p in pages:
        info = g(p["id"], {"fields": "instagram_business_account,name", "access_token": long_token})
        iba = info.get("instagram_business_account")
        if iba:
            ig_id = iba["id"]
            print(f"✅ IG-Business-Account gefunden ueber Seite '{info.get('name')}': {ig_id}")
            break
    if not ig_id:
        print("❌ Keine IG-Business-Account-ID gefunden. Ist @sola.makes auf Business UND mit der Seite verbunden?")
        sys.exit(1)

    with open(ENV, "w") as f:
        f.write(f"IG_ACCESS_TOKEN={long_token}\n")
        f.write(f"IG_USER_ID={ig_id}\n")
        f.write(f"FB_APP_ID={app_id}\n")
        f.write(f"FB_APP_SECRET={app_secret}\n")
    print(f"\n✅ In .env gespeichert.")
    print("👉 Naechster Befehl, um beides verschluesselt zu GitHub zu laden:")
    print("   ! python3 ~/dev/sola-auto-cloud/scripts/push-secrets.py")


if __name__ == "__main__":
    main()
