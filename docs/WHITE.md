> Die folgenden Deployment-Notizen beschreiben den früheren Prototyp. Für die aktuelle Ordnerstruktur muss der **vollständige Quellbaum** im genannten Staging-Verzeichnis liegen, einschließlich `src/`, `docker/`, `config/`, `web/`, `catalog/`, `trust/` und `scripts/copy-runtime.sh`. Selektive Dateilisten unten sind historisch. Dies ist kein allgemeiner RC1-Updater.

# Warm-/Kaltweiß und Lumitech – live getestet

Aktualisiert am 18.10.2026. Erweiterung installiert und freigeschaltet.
Der Nutzer bestätigt Warm-/Kaltweiß, RGB, Helligkeit und Ein/Aus über Lumitech.
Die frühere Mock-Vorbereitung und die Live-Nachweise sind in TEST-RESULTS.md getrennt dokumentiert.

## Direkte Farbtemperatur

PUT /hue-go/state mit vorhandenem Bearer-Token und Content-Type application/json:

- {"kelvin":2700}: echtes warmes Weiß, gespeicherte Helligkeit beibehalten.
- {"kelvin":6500,"brightness":30}: kaltes Weiß bei 30 Prozent.
- {"kelvin":4000,"brightness":0}: Aus, keine Temperaturänderung senden.

Seit 20.10.2026 verwendet jede Lampe ihren eigenen Bereich aus
`color_temperature.mirek_schema` der Bridge. Direkte Kelvinwerte von 1000–20000 K
werden angenommen, als 1000000/Kelvin gerundet und auf den unterstützten
Mirek-Bereich der Ziellampe begrenzt. Lumitech enthält durch sein Zahlenformat
höchstens vier Kelvin-Ziffern. Es findet keine Streckung des Temperaturbereichs statt.
Fehlen gültige Geräteangaben, gilt der Kompatibilitätsersatz 153–500 Mirek.
Bestehende Inventare laden fehlende Parameter automatisch wie in COLOR.md beschrieben.
Für den bisherigen Hue-Go-Bereich ergeben sich unverändert folgende Werte. Beispiele: 2000 K = 500, 2700 K = 370, 4000 K = 250,
6500 K = 154. Es findet KEINE Streckung von 2700 K auf 2000 K statt.
Hue-Rundung verhindert eine exakt ganzzahlige Kelvin-Rückmeldung.
Ungültige Zahlen, Mischungen von RGB und Kelvin und widersprüchliches off
werden vor jedem Bridge-Zugriff abgelehnt. on/off und Helligkeit bleiben getrennt.

## Lumitech-Anbindung für Loxone Config 17.2.8.28

Neues JSON-Feld: {"loxone_lumitech":<v>}.
Erwartetes klassisches Weißformat:
200000000 + Helligkeit_in_Prozent * 10000 + Kelvin.
201002700 = 100 Prozent, 2700 K; 200306500 = 30 Prozent, 6500 K.
Weiß mit Helligkeit 0 wird auf Aus abgebildet; RGB-Teil und Wert 0 entsprechen
exakt der bereits getesteten RGB-Abbildung. Kein neues Verhalten für niedrige
RGB-Werte: z.B. 100 bleibt Rot und wird nicht als reiner Dimmbefehl umgedeutet.

Das Weißformat wurde mit der primären Implementierung von loxHueBridge
(pforrmi/loxhuebridge, server.js, executeCommand) abgeglichen:
https://github.com/pforrmi/loxhuebridge/blob/main/server.js
Eine eindeutige öffentliche Herstellerbeschreibung des numerischen Formats
war nicht auffindbar. Die Anbindung wurde inzwischen aus Config 17.2.8.28
vom Nutzer funktional live bestätigt. Ein aufgezeichnetes Request-Payload
mit gleichzeitigem Soll-/Ist-Vergleich jeder Kelvin-Einstellung liegt nicht vor.

Konfiguration des vorhandenen Lichtkreises:
- Aktortyp RGB auf Lumitech umstellen.
- Denselben numerischen Ausgang verwenden; JSON von loxone_rgb auf
  {"loxone_lumitech":<v>} ändern.
- Methode PUT, Pfad /hue-go/state, bestehende Header unverändert.
- AUS-Felder leer; keine weiteren parallelen Steuerbefehle anschließen.
- Farbtemperaturgrenzen passend setzen: 2000 K warm, 6500 K kalt.
  Falls der verwendete Dialog 2000 K nicht anbietet, zunächst 2700–6500 K
  verwenden; das sind dann die tatsächlichen Kelvinwerte.
- Erst 2700 K und 6500 K bei 30 Prozent prüfen; dann Dimmen, Aus und RGB-Wechsel.
Die Umstellung auf Lumitech und den neuen Body wurde ausgeführt;
der Nutzer bestätigt die Bedienung über den Lichtbaustein. Die Grenzen oben
sind Konfigurationshinweise, keine protokollierte Prüfung aller Grenzwerte.

## Sichere Installation

HUE_WHITE_ENABLED=0 in Basis-Compose; fehlt der Wert, bleibt Weiß ebenfalls gesperrt.
Direkte Kelvinbefehle und das neue Lumitech-Feld liefern zunächst 403/white_disabled.
Die vorhandenen RGB-, Ein/Aus- und Dimmfelder bleiben unabhängig nutzbar.
Lumitech-RGB benötigt zusätzlich die bestehende Farbfreigabe; keine Umgehung.

Selektiv nach /opt/loxberry/hue2lox-white-staging/ übertragen:
app.py, hue_client.py, color.py, compose.yaml, .dockerignore, docker/Dockerfile.status,
scripts/install-white.sh. Root-Script sichert Laufzeitdateien, behält vorhandene Overrides
und Tokens bei und installiert erst nach Prüfung der Weißsperre. Es sendet keinen PUT.
Build und Installation im echten Container erfolgreich; Live-Weißtest vom Nutzer bestätigt.

docker/compose.white.yaml enthält ausschließlich die Freigabe HUE_WHITE_ENABLED=1.
Es kann zusätzlich zu den Control-/Color-Overrides geladen werden. Auf dem
laufenden LoxBerry wurde HUE_WHITE_ENABLED=1 in compose.override.yaml ergänzt.
Kein Token und kein privater Schlüssel wird ins Repository kopiert.

## Tests

25 Tests bestanden (7 neue Weiß-/Lumitechtests plus 18 vorhandene Tests).
Kelvin-Referenzwerte, echte Hue-Payloads, Lumitech-Weißformat und Nullhelligkeit,
RGB-Kompatibilität, Ablehnung ungültiger Eingaben ohne Netzwerkzugriff,
Weißsperre und Schutz gegen Umgehung der RGB-Sperre getestet.
Diese 25 automatisierten Tests verwendeten ausschließlich simulierte Steuerantworten.
Die anschließenden echten Live-Tests sind gesondert dokumentiert.

## Nachweis und Grenzen des Live-Tests (18.10.2026)

- Nutzer bestätigt Warm-/Kaltweiß und weiterhin RGB/Helligkeit aus dem Lichtbaustein.
- Eigener lesender HTTPS-Abruf mit explizitem Serverzertifikatsvertrauen erfolgreich:
  on=true, brightness=58.1, mirek=370, mirek_valid=true, tls_verified=true.
- 370 Mirek entspricht rund 2703 K und belegt aktiven Farbtemperaturbetrieb.
- Der zuvor gezeigte Loxone-Screenshot enthielt 58 % / 4847 K. Dieser konkrete
  Sollwert wurde durch die spätere Statusabfrage NICHT bestätigt: dafür wären
  etwa 206 Mirek zu erwarten. Zwischen Screenshot und Abruf lagen Bedienungen;
  Ursache und exakte zeitliche Zuordnung sind nicht abschließend geprüft.
- Kein eigener aufgezeichneter Kaltweiß-Mirek-Messwert vorhanden; Kaltweiß ist
  nutzerbestätigt, nicht durch einen separaten Status-Snapshot belegt.
- Kein kalibriertes Farb-/Temperaturmessgerät verwendet. Keine Behauptung einer
  Prüfung sämtlicher Kelvinwerte oder exakter optischer Farbtemperatur.

Aktiver Modus ohne Secrets reproduzierbar (nach sicherem Bereitstellen der Key-Dateien):

```sh
docker compose -f compose.yaml -f docker/compose.control.yaml -f docker/compose.color.yaml -f docker/compose.white.yaml config --quiet
docker compose -f compose.yaml -f docker/compose.control.yaml -f docker/compose.color.yaml -f docker/compose.white.yaml up -d --build
```

Diese Befehle dokumentieren die Betriebsart und wurden beim Dokumentationsupdate
nicht ausgeführt. Basis-Compose bleibt standardmäßig gesperrt. Kein Tokenwert,
Hue-Key oder privater TLS-Schlüssel ist Teil der versionierten Overrides.
