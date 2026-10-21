> Die folgenden Deployment-Notizen beschreiben den früheren Prototyp. Für die aktuelle Ordnerstruktur muss der **vollständige Quellbaum** im genannten Staging-Verzeichnis liegen, einschließlich `src/`, `docker/`, `config/`, `web/`, `catalog/`, `trust/` und `scripts/copy-runtime.sh`. Selektive Dateilisten unten sind historisch. Dies ist kein allgemeiner RC1-Updater.

# Farberweiterung – erfolgreicher RGB-Test

17.10.2026. Auf LoxBerry installiert und vom Nutzer aus dem Loxone-Lichtbaustein
mit Farben und Helligkeit erfolgreich live getestet. Die Mock-Tests waren die Vorprüfung.

## Eingabe

Bestehender authentisierter PUT /hue-go/state:

- Direkte Farbe: `{"rgb":{"r":255,"g":0,"b":0},"brightness":35}`.
- RGB-Kanäle: 0–255, endliche Zahlen. Helligkeit getrennt in Prozent.
- Ohne brightness bleibt der gespeicherte Hue-Dimmwert unverändert.
- Schwarz (0,0,0) bedeutet Aus. Widersprüchliche Werte werden abgelehnt.
- Klassischer Loxone-RGB-Wert: `{"loxone_rgb":100}` (Rot 100 %).
- Format R + 1000*G + 1000000*B, Kanäle jeweils ganzzahlig 0–100 %.
- Maximum der Loxone-Kanäle bestimmt die Hue-Helligkeit; die relativen,
  auf 255 normierten Kanäle bestimmen die Chromatizität nach Gammakorrektur.
- Das ist eine bewusste Dimmer-Abbildung, keine farbmetrische Garantie identischer
  Leuchtdichte für alle Farben. Helligkeit/Farben müssen später sichtbar getestet werden.
- Smart-Aktor-, Tunable-White- und Sonderwerte werden nicht interpretiert.
  Das tatsächliche Ausgangsformat des RGB-Lichtkreises in Config 17 muss geprüft werden.

Umrechnung: Gamma linearisiert RGB, Hue-Wide-RGB-D65-Matrix bildet xy,
Seit 20.10.2026 wird das Farbdreieck der jeweiligen Lampe aus `color.gamut`
verwendet. Farben außerhalb dieses Dreiecks werden auf die nächste Kante begrenzt.
Kein Nullteiler bei Schwarz. Inventuren speichern die validierten Geräteparameter.
Bei bestehenden Inventaren ohne diese Angaben liest der erste Farbbefehl sie per
GET von der Bridge; ein begrenzter Cache hält sie fünf Minuten vor. Scheitert
bereits dieser GET, wird kein PUT gesendet. Ein/Aus und Dimmen benötigen ihn nicht.
Fehlt ein gültiges Farbdreieck in der Antwort, dient Hue-Gamut-C als definierter
Kompatibilitätsersatz. Dies ist keine Garantie passender Farbwiedergabe für jedes
unbekannte Modell. Tokens und Schlüssel werden dabei weder gespeichert noch geloggt.

GET /hue-go/status ergänzt rohe xy-Farbwerte und color_temperature mit mirek_valid.
Es wird kein scheinbar exakter RGB-Rückwert erfunden: Hue xy und Helligkeit
lassen sich nicht verlustfrei in den ursprünglichen Loxone-Wert zurückwandeln.

## Aktivierung und Installation

HUE_COLOR_ENABLED=0 in Compose sperrt beide Farbformate zusätzlich zur vorhandenen
Schreibsperre/Tokenprüfung. Ein/Aus und Dimmen bleiben davon unabhängig.
Kein Token und kein privater Schlüssel wird für diese Erweiterung neu erzeugt.
Die Farbversion läuft inzwischen; Farbe und Schreiben sind im lokalen Override freigegeben.
Die Basisdatei bleibt für frische Installationen standardmäßig gesperrt.

Selektiv nach /opt/loxberry/hue2lox-color-staging/ übertragen: app.py, hue_client.py,
color.py, compose.yaml, .dockerignore, docker/Dockerfile.status, scripts/install-color.sh.
Das Root-Script sichert bestehende Laufzeitdateien, behält compose.override.yaml
und bestehende Credentials bei und prüft vor Start, dass Farbe gesperrt bleibt.
Es sendet ausschließlich lesende Requests. Ein Container-Neustart verursacht eine
kurze Unterbrechung. Der anschließende manuelle Live-Farbtest wurde ausdrücklich
freigegeben und erfolgreich durchgeführt. Keine Wiederherstellung danach protokolliert.

## Rückmeldung an Loxone

Die eingerichteten virtuellen HTTP-Eingänge zeigen den Ist-Zustand der Bridge und
können Diagnose, eigene Ist-Anzeigen und gesondert geplante Logik versorgen.
Sie synchronisieren den Lichtsteuerungsbaustein nicht automatisch.
Die dokumentierten normalen Eingänge enthalten keinen allgemeinen Istwert-Eingang
pro Lichtkreis; Br ist Raumhelligkeit in Lux, MBr eine Steuervorgabe.
Den tatsächlichen Lampenstatus daher nicht einfach auf diese Eingänge zurückführen.
API-Connector-/Webservice-Möglichkeiten wären getrennt zu prüfen, einschließlich
Schleifenvermeidung und Verhalten bei Änderungen durch Hue-App und Automatik.

## Quellen und Grenzen

Loxone klassische RGB-Codierung:
https://www.loxone.com/dede/kb/rgb_lichtszene/
Dokumentierte Eingänge der Lichtsteuerung:
https://www.loxone.com/dede/kb/lichtsteuerung/
Gamma/Matrix gegen primäre Client-Implementierung abgeglichen:
https://raw.githubusercontent.com/raycast/extensions/eb2e5bff8a2ed8b12208f0835827d9bd35027692/extensions/hue/src/helpers/colors.ts
Hue-Herstelleranleitung beim Abruf nicht zugänglich:
https://developers.meethue.com/develop/application-design-guidance/color-conversion-formulas-rgb-to-xy-and-back/

Tests: Farbprimärwerte, bekannte Mischfarbe, Gamut-Begrenzung, Schwarz, Zahlenbereiche,
Loxone-Kanalreihenfolge und Helligkeit, gesperrte/aktivierte Farbrouten mit Mock,
Status-Farbfelder und bestehende Ein/Aus-/Dimmtests. Kein echter Hue-PUT.

## Reproduzierbarer aktiver Betrieb ohne Secrets im Repository

Der laufende LoxBerry verwendet compose.override.yaml mit beiden Freigaben und
bestehendem read-only Token-Mount. Diese lokale Datei enthält keinen Tokenwert,
wurde aber nicht als produktive Datei übernommen.

Für eine separate Neuinstallation liegen versionierte Overrides vor:

```sh
# Benötigt vorher sicher bereitgestellte certs/, secrets/hue_key und secrets/control_token.
docker compose -f compose.yaml -f docker/compose.control.yaml -f docker/compose.color.yaml config --quiet
docker compose -f compose.yaml -f docker/compose.control.yaml -f docker/compose.color.yaml up -d --build
```

Diese Befehle aktivieren Steuerung und Farbe; sie wurden für die Dokumentation nicht
auf dem laufenden System ausgeführt. Die Dateien stellen den aktivierten Betriebsmodus
nach, ohne einen Schlüsselwert zu enthalten. `docker compose up` nur mit der Basisdatei
aktiviert Farbe nicht. Auf dem aktuellen LoxBerry übernimmt das bereits vorhandene
compose.override.yaml diese Aktivierung automatisch.

Die Rückmeldung an den Lichtsteuerungsbaustein wird auf Nutzerwunsch nicht weiterverfolgt.
