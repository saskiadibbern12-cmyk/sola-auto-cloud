#!/usr/bin/env python3
"""
push-secrets.py — laedt IG_ACCESS_TOKEN + IG_USER_ID verschluesselt als
GitHub-Actions-Secrets ins sola-auto-cloud-Repo. Gespiegelt vom LinkedIn-System.
Holt das GitHub-Credential aus dem Mac-Schluesselbund (kein gh-CLI noetig).

    python3 scripts/push-secrets.py
"""
import os, json, base64, subprocess, urllib.request, urllib.error
from nacl import encoding, public

REPO = "saskiadibbern12-cmyk/sola-auto-cloud"
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
SECRETS = ["IG_ACCESS_TOKEN", "IG_USER_ID"]


def read_env(key):
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    raise SystemExit(f"❌ {key} nicht in .env gefunden (erst ig-auth.py laufen lassen)")


def github_pat():
    cred = subprocess.run(["git", "credential", "fill"],
                          input="protocol=https\nhost=github.com\n\n",
                          capture_output=True, text=True).stdout
    for line in cred.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    raise SystemExit("❌ Kein GitHub-Credential im Schluesselbund")


def api(method, path, pat, data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"https://api.github.com{path}", data=body, method=method, headers={
        "Authorization": f"Bearer {pat}", "Accept": "application/vnd.github+json",
        "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, (json.loads(r.read()) if r.status != 204 else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()}


def encrypt(pub_b64, val):
    pk = public.PublicKey(pub_b64.encode(), encoding.Base64Encoder())
    return base64.b64encode(public.SealedBox(pk).encrypt(val.encode())).decode()


def main():
    pat = github_pat()
    st, key = api("GET", f"/repos/{REPO}/actions/secrets/public-key", pat)
    if st != 200:
        raise SystemExit(f"❌ Public-Key holen fehlgeschlagen: {key}")
    for name in SECRETS:
        val = read_env(name)
        st, resp = api("PUT", f"/repos/{REPO}/actions/secrets/{name}", pat, {
            "encrypted_value": encrypt(key["key"], val), "key_id": key["key_id"]})
        print(f"{'✅' if st in (201,204) else '❌'} Secret {name} ({st})")


if __name__ == "__main__":
    main()
