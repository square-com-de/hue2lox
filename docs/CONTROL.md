> Die folgenden Deployment-Notizen beschreiben den früheren Prototyp. Für die aktuelle Ordnerstruktur muss der **vollständige Quellbaum** im genannten Staging-Verzeichnis liegen, einschließlich `src/`, `docker/`, `config/`, `web/`, `catalog/`, `trust/` und `scripts/copy-runtime.sh`. Selektive Dateilisten unten sind historisch. Dies ist kein allgemeiner RC1-Updater.

# Ein/Aus- und Dimmsteuerung

Stand: 17.10.2026. Ein/Aus und Dimmen sind inzwischen auf LoxBerry aktiviert
und live sowie aus Loxone erfolgreich getestet. Die folgenden Vorbereitungshinweise
beschreiben die ursprüngliche sichere Aktivierung; aktueller Nachweis: TEST-RESULTS.md.

## API

`PUT /hue-go/state`, `Content-Type: application/json`, JSON-Body:

| Body | Gewünschte Wirkung nach separater Aktivierung |
|---|---|
| `{"on":true}` | Einschalten, gespeicherte Hue-Helligkeit beibehalten |
| `{"on":false}` | Ausschalten |
| `{"brightness":35}` | Einschalten und 35 Prozent setzen |
| `{"brightness":0}` | Ausschalten, keinen Dimmwert 0 an Hue senden |

Helligkeit: endliche Zahl von 0 bis 100, auch Nachkommastellen. Boolean-Werte,
Strings, NaN/Infinity, unbekannte Felder und widersprüchliche Kombinationen
(z.B. on=false mit brightness=50) werden vor Bridge-Zugriff abgelehnt.
Nur die konfigurierte Hue Go ist adressierbar; keine frei wählbare Ressourcen-URL.
Ein erfolgreicher Befehl liefert `status: accepted`: das ist die Bestätigung der
Bridge, noch kein Nachweis einer physischen Zustandsänderung. Danach Status lesen.
HTTP-200-Antworten der Bridge werden zusätzlich auf API-Fehler und Ziel-ID geprüft.
Bei Timeout/Fehler wird der PUT nicht automatisch wiederholt; eine Änderung kann
bereits stattgefunden haben. Vor einem erneuten Befehl Status prüfen.

## Standardmäßig gesperrt

Die normale Compose-Datei setzt HUE_WRITES_ENABLED=0 fest.
Steueraufrufe liefern 403/writes_disabled, ohne auf die Bridge zuzugreifen.
GET /health und GET /hue-go/status funktionieren weiterhin.
GET auf den Steuerpfad schaltet nichts. Kein Steuerbefehl steht im Healthcheck,
Startcode oder Installationsscript.

Für eine spätere freigegebene Aktivierung sind beide Voraussetzungen nötig:
- Compose-Override `docker/compose.control.yaml` zusätzlich laden.
- Eigenen zufälligen Steuer-Token (mindestens 32 Zeichen) als
  secrets/control_token bereitstellen, UID/GID 10001, Modus 0400.

Der Token wird als `Authorization: Bearer ...` gesendet, niemals in einer URL.
Fehlende/falsche Tokens werden vor Lesen des Bodys bzw. Bridge-Zugriff abgelehnt.
Token-Dateien bleiben aus Git und Docker-Build ausgeschlossen. Kein Token wurde
bei der Vorbereitung erzeugt. Bestehender Hue-Key und TLS-Zertifikate bleiben.
Aktivierung und echter Schalt-/Dimmtest sind erfolgreich erfolgt; siehe TEST-RESULTS.md.

## Update vorbereiten

Quellcode selektiv nach /opt/loxberry/hue2lox-control-staging/ übertragen:
app.py, hue_client.py, compose.yaml, docker/compose.control.yaml, .dockerignore,
docker/Dockerfile.status. Kein Kopieren von .env, certs oder secrets nötig.
Dann scripts/install-control.sh als root ausführen, nachdem es ebenfalls übertragen wurde.
Das Script sichert die bisherigen Laufzeitdateien, baut und installiert den Code
mit Steuerung AUS. Build und Live-Test im tatsächlichen Container sind inzwischen erfolgreich erfolgt.
Es aktiviert keine Loxone-Ausgänge und sendet keinen Hue-PUT.

## Prüfungen

10 automatisierte Tests bestanden (nur Mock-Bridge und lokaler HTTP-Testserver):
- Ein/Aus, Dimmen, Null und obere Grenze.
- Ungültige und widersprüchliche Werte ohne Bridge-Zugriff.
- Hue-PUT-Payload und Zielbestätigung.
- Hue-API-Fehler trotz HTTP 200.
- Standardsperre und Tokenprüfung ohne Schreibzugriff.
- Fehlerantworten ohne interne Fehlertexte oder Zugangsdaten.
- Vorhandene Health-/Status-Funktion und unbekannte Pfade.

Die offizielle Hue-v2-API-Referenz war beim Abruf mit HTTP 403 gesperrt.
PUT-/Antwortformat folgen dem vorhandenen Hue-v2-Integrationsentwurf;
ein echter Schreibtest gegen diese Bridge wurde bewusst noch nicht durchgeführt.
Loxone-Befehlsformat, Tokenübermittlung und Statusrückmeldung müssen vor der
Anbindung eines virtuellen Ausgangs in der verwendeten Config-Version geprüft werden.
