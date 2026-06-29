#!/usr/bin/env python3
"""
ig-auth.py , Instagram-LOGIN-Weg (graph.instagram.com).

Tauscht den kurzlebigen Instagram-Token (steht schon in der .env) gegen einen
60-Tage-Token und schreibt ihn zurueck in die .env. Danach laeuft das Posten
60 Tage ohne neuen Login.

    ! python3 ~/dev/sola-auto-cloud/scripts/ig-auth.py

Du brauchst dafuer EINEN Wert:
  - Instagram-App-Geheimcode
    (App-Dashboard -> API-Einrichtung mit Instagram-Login -> Instagram-App-Geheimcode -> Anzeigen)
"""
import os, sys, json, urllib.request, urllib.parse, urllib.error, ssl

IG = "https://graph.instagram.com"
CTX = ssl.create_default_context()
ENV = os.path.join(os.path.dirname(__file__), "..", ".env")


def load_env():
    vals = {}
    if os.path.exists(ENV):
        for line in open(ENV, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                vals[k] = v
    return vals


def g(path, params):
    url = f"{IG}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, context=CTX) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode()}")
        print("   Tipp: ist der kurze Token noch frisch (haelt nur ~1 Std)?"
              " Sonst im App-Dashboard neu generieren und in die .env setzen.")
        sys.exit(1)


def main():
    env = load_env()
    short = os.environ.get("IG_SHORT_TOKEN") or env.get("IG_ACCESS_TOKEN")
    if not short:
        short = input("Kurzer Instagram-Token: ").strip()
    app_secret = os.environ.get("INSTAGRAM_APP_SECRET") or env.get("INSTAGRAM_APP_SECRET")
    if not app_secret:
        app_secret = input("Instagram-App-Geheimcode: ").strip()

    print("\n🔄 Tausche gegen 60-Tage-Token ...")
    res = g("access_token", {
        "grant_type": "ig_exchange_token",
        "client_secret": app_secret,
        "access_token": short})
    long_token = res["access_token"]
    days = res.get("expires_in", 5184000) // 86400
    print(f"✅ 60-Tage-Token erhalten ({days} Tage gueltig)")

    me = g("me", {"fields": "user_id,username", "access_token": long_token})
    ig_id = me.get("user_id") or me.get("id")
    print(f"✅ Konto @{me.get('username')}, Instagram-User-ID {ig_id}")

    # .env aktualisieren (Token + ID + Secret), restliche Zeilen behalten
    env["IG_ACCESS_TOKEN"] = long_token
    env["IG_USER_ID"] = str(ig_id)
    env["INSTAGRAM_APP_SECRET"] = app_secret
    with open(ENV, "w", encoding="utf-8") as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")
    print("\n✅ .env aktualisiert , der Token haelt jetzt 60 Tage.")
    print("👉 Danach (fuer die Cloud-Automatik):")
    print("   ! python3 ~/dev/sola-auto-cloud/scripts/push-secrets.py")


if __name__ == "__main__":
    main()
