# SOLA Instagram Auto-Cloud

Postet @sola.makes automatisch 3x taeglich (09:00 / 12:30 / 18:30) ueber GitHub Actions,
Mac-unabhaengig. Gespiegelt vom funktionierenden LinkedIn-Auto-Cloud-System.

## Wie es laeuft
1. `queue.json` = alle Posts (Zeitpunkt, Typ, Assets, Caption, approved/posted).
2. Assets liegen in `assets/` und sind ueber `raw.githubusercontent.com` oeffentlich
   abrufbar (die IG-API braucht oeffentliche image_url/video_url). Bilder als JPG, Reels als MP4.
3. GitHub Actions (`.github/workflows/daily-post.yml`) laeuft per Cron, postet den
   faelligen freigegebenen Slot und committet den `posted`-Status zurueck (kein Doppel-Post).
4. Fehler => Workflow schlaegt fehl => GitHub schickt dir automatisch eine Mail.

## Einmaliges Setup (das was nur Saskia kann)
Brauchst du eine Meta-App + einen Token. Schritt fuer Schritt:

### 1. Meta-App (einmal, ~3 Min)
- developers.facebook.com -> "Meine Apps" -> App erstellen -> Typ "Business".
- In der App: Produkt "Instagram" / "Instagram Graph API" hinzufuegen.
- App-ID und App-Secret notieren (Einstellungen -> Allgemein).

### 2. Kurz-Token holen (Graph API Explorer, ~1 Min)
- developers.facebook.com/tools/explorer
- App oben auswaehlen, dann "Generate Access Token".
- Berechtigungen anhaken: `instagram_basic`, `instagram_content_publish`,
  `pages_show_list`, `pages_read_engagement`, `business_management`.
- Token kopieren (das ist der Kurz-Token, ~1-2 h gueltig, wird gleich getauscht).

### 3. Long-Lived-Token + IG-ID erzeugen und hochladen
```
! python3 ~/dev/sola-auto-cloud/scripts/ig-auth.py        # fragt App-ID, App-Secret, Kurz-Token
! python3 ~/dev/sola-auto-cloud/scripts/push-secrets.py   # laedt beides verschluesselt zu GitHub
```
Fertig. Ab dann postet die Cloud von selbst.

## Test ohne aufs Datum zu warten
Im Repo auf GitHub: Actions -> "SOLA Instagram Auto-Post" -> "Run workflow" ->
bei `force_id` z.B. `2` eintragen -> postet sofort Post 2.

## Neue Woche
Im Hauptworkspace `~/dev/sola-instagram/posting/drafts-system/build.py` Inhalte aendern,
dann hier `python3 scripts/stage-assets.py` und committen/pushen.

## 60-Tage-Routine
Token laeuft nach 60 Tagen ab. Dann einmal neu:
```
! python3 ~/dev/sola-auto-cloud/scripts/ig-auth.py
! python3 ~/dev/sola-auto-cloud/scripts/push-secrets.py
```
