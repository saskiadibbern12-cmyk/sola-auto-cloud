#!/usr/bin/env python3
"""
ig-auth.py — Facebook-LOGIN-Weg (graph.facebook.com) mit NIE-ablaufendem Token.

Tauscht den Kurz-Token (aus dem Graph API Explorer) gegen einen Long-Lived
User-Token, holt darueber den Page-Access-Token (der laeuft NICHT ab) und
deine Instagram-Business-ID. Schreibt beides in .env.

    ! python3 ~/dev/sola-auto-cloud/scripts/ig-auth.py

Du brauchst drei Werte (zeige ich dir im Chat wo):
  1. App-ID      (App-Dashboard -> Einstellungen -> Allgemein -> App-ID)
  2. App-Secret  (ebd., hinter "Anzeigen")
  3. Kurz-Token  (Graph API Explorer -> Generate Access Token -> der lange Text)
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
        print(f"❌ HTTP {e.code}: {e.read().decode()}")
        print("   Tipp: Kurz-Token frisch im Graph API Explorer generieren"
              " (er ist nur ~1-2 Stunden gueltig) und App-ID/App-Secret pruefen.")
        sys.exit(1)


def ask(label, envname):
    v = os.environ.get(envname)
    if v:
        return v.strip()
    return input(f"{label}: ").strip()


def main():
    app_id = ask("App-ID", "FB_APP_ID")
    app_secret = ask("App-Secret", "FB_APP_SECRET")
    short = ask("Kurz-Token (Graph API Explorer)", "FB_SHORT_TOKEN")

    print("\n🔄 Tausche Kurz-Token gegen Long-Lived-Token ...")
    res = g("oauth/access_token", {
        "grant_type": "fb_exchange_token",
        "client_id": app_id, "client_secret": app_secret,
        "fb_exchange_token": short})
    long_user = res["access_token"]
    print("✅ Long-Lived-User-Token erhalten")

    print("🔎 Suche deine Facebook-Seite + Instagram-Business-Account ...")
    pages = g("me/accounts", {
        "fields": "name,access_token,instagram_business_account",
        "access_token": long_user}).get("data", [])
    ig_id = page_token = page_name = None
    for p in pages:
        iba = p.get("instagram_business_account")
        if iba:
            ig_id = iba["id"]
            page_token = p.get("access_token")  # vom long-lived User abgeleitet = laeuft nicht ab
            page_name = p.get("name")
            break
    if not ig_id or not page_token:
        print("❌ Keine mit Instagram verbundene Facebook-Seite gefunden.")
        print(f"   Gefundene Seiten: {[p.get('name') for p in pages] or 'keine'}")
        print("   Pruefe: @sola.makes auf Business/Creator UND in der IG-App unter"
              " Einstellungen -> Verknuepfte Konten mit DIESER Seite verbunden.")
        sys.exit(1)
    print(f"✅ Seite '{page_name}', Instagram-Business-ID {ig_id}")

    with open(ENV, "w") as f:
        f.write(f"IG_ACCESS_TOKEN={page_token}\n")
        f.write(f"IG_USER_ID={ig_id}\n")
        f.write(f"FB_APP_ID={app_id}\n")
        f.write(f"FB_APP_SECRET={app_secret}\n")
    print("\n✅ In .env gespeichert (Token laeuft nicht ab).")
    print("👉 Naechster Schritt (mache ich gleich fuer dich):")
    print("   python3 ~/dev/sola-auto-cloud/scripts/push-secrets.py")


if __name__ == "__main__":
    main()
