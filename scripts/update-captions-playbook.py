#!/usr/bin/env python3
"""update-captions-playbook.py , schreibt Captions #2-14 auf die Playbook-Hooks um
(Outcome/Pain/Wert + Funnel-CTA Gratis-Sample). #1 (schon gepostet) bleibt unberuehrt."""
import json, os
REPO = os.path.expanduser("~/dev/sola-auto-cloud")
qp = os.path.join(REPO, "queue.json")
TAGS_IMG = "#aiproductphotography #produktfotografie #beautyeditorial #d2cmarketing #aicreative #kiwerbung"
TAGS_VID = "#aivideo #adcreative #kiwerbung #contentcreation #marketingdeutschland #aiugc"

# id -> neue Caption (ohne Hashtags). Playbook-Hooks, Funnel-CTA = gratis sample per DM.
CAPS = {
 2: "links dein altes produktfoto. rechts was wir draus machen.\n\ngleiches produkt, anderer wert. schick mir deins, ich zeig dir was geht , gratis.",
 3: "dein produkt, aber es bewegt sich wie ein grosser spot.\n\nkein dreh, kein team, ein nachmittag. sowas fuer deine marke? schreib mir.",
 4: "dein produkt, aber es sieht aus wie eine grosse kampagne.\n\nauch wenn das budget noch klein ist. schick mir ein produktfoto, ich bau dir ein gratis frame.",
 5: "produktwerbung im vogue-niveau. ohne studio, ohne model-gage.\n\nja, wirklich. magst du sowas fuer dein produkt? schreib mir.",
 6: "deine marke verdient werbung die nach geld aussieht.\n\nauch mit kleinem budget. schick mir dein produkt, ich zeig dir die richtung , gratis.",
 7: "stop scrollen wenn deine produktwerbung aussieht wie 2019.\n\nkein vorwurf, es geht nur besser und schneller. schreib mir, ich zeig dirs an deinem produkt.",
 8: "klassisch: zwei wochen, viertausend euro. so: zwei tage.\n\ndie rechnung macht gerade jede d2c-marke neu. willst du sie auch? schreib mir.",
 9: "nie wieder dreitausend euro fuer ein shooting das in zwei wochen veraltet ist.\n\ncontent der mitwaechst statt einmal teuer. schick mir dein produkt, ich mach dir eine probe.",
 10: "ruhig, teuer, premium , so sieht deine marke aus wenn sie nach geld aussieht.\n\nund das geht auch klein. schreib mir, ich bau dir ein gratis frame.",
 11: "alle denken werbung ohne shooting sieht billig aus. schau hin.\n\ndas gegenteil stimmt, wenn mans richtig macht. magst du den beweis an deinem produkt? schreib mir.",
 12: "produktwerbung im kampagnen-niveau. an einem nachmittag.\n\nkein hexenwerk, nur ein anderer weg. schick mir dein produktfoto fuer ein gratis frame.",
 13: "selbst ein kleines detail wird zur grossen ad.\n\nlicht, material, geduld , mehr nicht. was ist das detail an deinem produkt? schreib mir.",
 14: "nicht nur beauty. jedes produkt sitzt sauber im licht.\n\nwelche kategorie ist deine? schick mir ein produktfoto, ich zeig dir was geht.",
}

q = json.load(open(qp, encoding="utf-8"))
changed = 0
for post in q:
    i = post["id"]
    if i in CAPS:
        tags = TAGS_VID if post["type"] == "reel" else TAGS_IMG
        post["caption"] = CAPS[i] + "\n\n" + tags
        changed += 1
json.dump(q, open(qp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
posted = [p["id"] for p in q if p.get("posted")]
print(f"{changed} Captions aktualisiert. Schon gepostet (unberuehrt): {posted}")
