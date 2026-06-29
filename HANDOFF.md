# SOLA Auto-Post , System-Übergabe (für Cowork-Claude)

Diese Datei erklärt das automatische Instagram-Posting für **@sola.makes**, damit ein
anderer Workspace/Claude es verbinden und Content organisieren kann.

## 1. Account + Verbindung (so hängt es an Instagram)

- **Instagram:** @sola.makes , Business-Account
- **Instagram-User-ID:** `17841415310956725` (das ist die ID, an die gepostet wird)
- **API-Weg:** Instagram API mit **Instagram-Login** , Host **`https://graph.instagram.com`**
  (NICHT graph.facebook.com , es gibt keine verknüpfte Facebook-Seite über die App)
- **Posting-Berechtigung:** `instagram_business_content_publish` ✓ (granted)
- **Meta-App:** `sola-makes-autopost` , App-ID `1694270748477530` , Status **Live**
- **Instagram-App-ID:** `1637622153965135`

### Geheimnisse (NICHT in diese Datei, liegen lokal)
- **Access-Token + IG-User-ID:** in `~/dev/sola-auto-cloud/.env`
  (Felder `IG_ACCESS_TOKEN`, `IG_USER_ID`). Diese Datei ist in `.gitignore`, also nie im Repo.
- **Meta-App-Geheimcode** und **Instagram-App-Geheimcode:** im Meta-Dashboard
  (developers.facebook.com → App `sola-makes-autopost`). Nur bei Token-Erneuerung nötig.

## 2. Wie das System aufgebaut ist

- **Workspace:** `~/dev/sola-auto-cloud/`
- **GitHub-Repo:** `github.com/saskiadibbern12-cmyk/sola-auto-cloud` (public, damit IG die Bild-URLs laden kann)
- **Automatik:** GitHub Actions (`.github/workflows/daily-post.yml`) postet **3x täglich**
  (09:00 / 12:30 / 18:30 CEST) den fälligen, freigegebenen Slot aus `queue.json`.
- **Scripts** (`scripts/`):
  - `post-instagram.py` , der Poster (läuft in der Cloud + lokal; lädt lokal die `.env`)
  - `ig-auth.py` , Token holen/erneuern
  - `push-secrets.py` , Token + ID verschlüsselt als GitHub-Secrets hochladen
  - `stage-assets.py` , neue Woche aus dem Draft-System importieren
- **Content:** `queue.json` (aktuell 21 Posts) + Bilder/Videos in `assets/`

## 3. Content reinbringen (das „Organisieren")

**Architektur (so hängt Content + Poster zusammen):**
```
~/dev/sola-instagram/                  <- Content-Workspace (Cowork, hier entsteht Content)
  posting/drafts-system/build.py       <- QUEUE = menschenlesbare Post-Liste (Quelle der Wahrheit)
  produkt-ads/, outputs/REELS/, ...     <- die echten Bild-/Video-Dateien
        |
        |  stage-assets.py  (Bruecke: PNG->JPG, kopiert Assets, baut queue.json)
        v
~/dev/sola-auto-cloud/                  <- Poster (dieses Repo)
  queue.json + assets/                  <- daraus postet post-instagram.py
```

**Empfohlener Weg fuer neuen Content (keine Doppelpflege):**
1. Post in `~/dev/sola-instagram/posting/drafts-system/build.py` in die `QUEUE` eintragen.
   Ein Eintrag hat: `date` (YYYY-MM-DD), `time` ("09:00"), `slot`, `type`, `pillar`, `title`,
   `hook`, `assets` (Pfade relativ zu `~/dev/sola-instagram/`, .png/.jpg/.mp4),
   `caption`, `hashtags`.
2. `python3 ~/dev/sola-auto-cloud/scripts/stage-assets.py`
   → konvertiert/kopiert nach `assets/`, schreibt `queue.json` (alles `approved: true`).
3. In `~/dev/sola-auto-cloud/` committen + pushen → die Cloud postet automatisch zur Zeit.

**Direkter Weg (falls man queue.json selbst schreibt statt build.py):**
Ein Post in `queue.json`:
```json
{ "id": 22, "datetime": "2026-07-01T09:00:00+02:00",
  "type": "image",                // image | carousel | reel
  "title": "…", "assets": ["assets/22_1.jpg"],
  "caption": "…", "approved": true, "posted": false }
```
Regeln dabei:
- Bilder müssen **JPG** sein (IG-API frisst kein PNG), Reels **MP4**, Hochformat 9:16.
- Asset-Dateien nach `assets/` legen, dann committen + pushen (sonst sind die URLs nicht erreichbar).
- `approved: false` = wird übersprungen (Freigabe-Schalter).

## 4. Noch offen (Stand der Übergabe)

1. **Test-Post** steht noch aus: `! FORCE_ID=1 python3 scripts/post-instagram.py`
2. **Token ist noch kurzlebig (~1 Std).** Für Dauerbetrieb gegen 60-Tage-Token tauschen:
   `GET https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=<INSTAGRAM-APP-GEHEIMCODE>&access_token=<kurzer Token>`
   → das Ergebnis als `IG_ACCESS_TOKEN` in die `.env` schreiben.
   Erneuern (alle ~50 Tage): `GET https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=<60-Tage-Token>`
3. **Secrets zu GitHub pushen** (für die Cloud-Automatik): `python3 scripts/push-secrets.py`
   , danach läuft das Posten Mac-unabhängig über GitHub Actions.

## 5. Schnell-Check „läuft es?"
- Token gültig + richtiges Konto: `GET https://graph.instagram.com/me?fields=user_id,username,account_type&access_token=<Token>`
  → muss `username: sola.makes`, `account_type: BUSINESS` zeigen.
