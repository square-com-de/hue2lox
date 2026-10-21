# Temporärer HTTP-Monitor

## Loxone-Ausgänge testen

1. Im angemeldeten Webinterface **HTTP-Monitor** öffnen.
2. **Testprotokoll starten · 10 Minuten** wählen. Dabei wird der vorherige Lauf geleert.
3. Den zu prüfenden Ausgang in Loxone auslösen.
4. Anfrage, geprüfte Werte und HTTP-Ergebnis im Monitor vergleichen.
5. Nach dem Test **Stoppen**, ggf. **Protokoll kopieren**, anschließend **Leeren**.

Die Anzeige aktualisiert sich bei sichtbarer Monitorseite etwa alle zwei Sekunden.
Es werden maximal die letzten 200 Anfragen gespeichert, ausschließlich im
Arbeitsspeicher des Hue2Lox-Prozesses. Nach zehn Minuten endet die Aufzeichnung
automatisch. Seitenwechsel oder Abmelden verlängern die Laufzeit nicht und stoppen
einen aktiven Lauf nicht vorzeitig. Alle angemeldeten Administrator-Sitzungen
sehen denselben Lauf; ohne Sitzung sind die Daten nicht abrufbar.

Stoppen oder Ablauf erhalten die bereinigten Einträge zum Auswerten. **Leeren**,
der nächste Start oder ein Container-Neustart entfernen sie. Leeren während eines
aktiven Laufs beendet die Aufzeichnung nicht. Anfragen, die erst nach Ablauf
ankommen, werden nicht gespeichert. Endet die Aufzeichnung während einer Anfrage,
wird eine noch nicht aufgezeichnete Antwort ausdrücklich als solche gekennzeichnet.

## Angezeigte Daten

- UTC-Zeitpunkt (im Browser lokale Uhrzeit), HTTP-Methode und Absender-IP des
  Socket-Peers. Bei NAT/Proxy kann das die Adresse des vorgeschalteten Systems sein;
  ein unbestätigter `X-Forwarded-For`-Header wird nicht übernommen.
- Bereinigter Steuerungspfad. Unbekannte Pfade und frei eingetragene IDs erscheinen
  als Platzhalter, ohne Query-Parameter. Registrierte Standard-Hue-UUID-Pfade
  können vollständig angezeigt werden. Der feste Hue-Go-Pfad bleibt sichtbar.
- Ausschließlich typgeprüfte Steuerungswerte: `on`, `brightness`, `rgb`, `kelvin`,
  `loxone_rgb`, `loxone_lumitech` oder `recall`.
- HTTP-Status, Verarbeitungszeit und fest definierte Ergebnisse: z. B. von Hue
  bestätigt, ungültiges Token, falscher Body, gesperrte Steuerung oder Hue-Fehler.

Es werden **keine Header, Authorization-Werte, Cookies, Tokens, Hue-Schlüssel,
Roh-Bodies, ungeprüfte Zeichenketten oder Hue-Fehlertexte** in den Monitor
übernommen. Bei ungültigem Token werden keine Body-Werte angezeigt. Nach erfolgreicher
Authentifizierung erscheint auch bei HTTP 400 ein bereinigter Body: bekannte
Steuerungsfelder mit Zahlen, Booleschen Werten, null, numerischen Zeichenketten
oder dem Platzhalter `<v>`. Zahlen bis einschließlich Betrag 10 Milliarden werden
angezeigt; größere Zahlen, fremde Felder, beliebige Texte und komplexe Datentypen
werden ausgeblendet. Anführungszeichen bleiben erkennbar. Bei ungültigem JSON
erscheinen eine bereinigte Struktur sowie Zeile und Spalte des Parserfehlers.
Die Vorschau ist kein originalgetreuer Roh-Body. „JSON lesbar“ bedeutet noch
nicht, dass ein Wert für die gewählte Steuerungsart gültig ist. Der Kopiertext enthält nur dieselben bereinigten Daten.
Der Monitor lädt keine Docker-Logs und schreibt keine Protokolldatei.

## Erfasste Anfragen und Aussagekraft

PUT-Steuerungsanfragen werden ab Ankunft im Handler erfasst, einschließlich
unbekannter Ziele und abgelehnter Anfragen. Falsche GET-/POST-/PATCH-/DELETE-/HEAD-
Methoden an erkennbaren Steuerungspfaden werden als HTTP 405 mit `Allow: PUT`
beantwortet. Normale Healthchecks, Statusabfragen, Anmeldungen und Admin-Anfragen
erscheinen nicht im Testprotokoll.

HTTP 200 bedeutet eine erfolgreiche API-Antwort für den Steuerungsaufruf. Es ist
kein unabhängiger Nachweis, dass eine Lampe sichtbar leuchtet. TLS-Handshake-Fehler,
fehlgeschlagene Netzwerkverbindungen vor HTTP und ungültige Requests vor Eintritt
in den Handler können hier nicht gezeigt werden. Bei leerem Monitor zusätzlich
Loxone-HTTP-Monitor, Adresse, Port und Zertifikatsverbindung prüfen.

Der Monitor selbst schaltet keine Lampe. Ein echter Loxone-Steuerungsbefehl wird
bei laufendem Monitor unverändert nach den bisherigen Berechtigungen verarbeitet.
Die Entwicklungstests verwenden ausschließlich simulierte Hue-Schreibantworten.

## Schnittstellen und Betrieb

- `GET /api/admin/monitor`: angemeldete Sitzung und gleicher Ursprung erforderlich.
- `POST /api/admin/monitor/start`, `/stop`, `/clear`: zusätzlich CSRF-Token,
  JSON-Body `{}`. Start hat eine feste Laufzeit von 600 Sekunden.
- Threadgeschützter Ringpuffer in `request_monitor.py`, maximal 200 Einträge.
- Neue Testläufe besitzen getrennte Generationen; verspätete Antworten aus einem
  alten Lauf oder nach Leeren tauchen nicht erneut auf.
- `web/monitor.js` zeigt Daten und kopiert das bereinigte Protokoll.
- Keine zusätzliche Abhängigkeit, kein neuer Container, Port oder Mount.
- Nach Update startet der Monitor ausgeschaltet und leer.

## Byte-Diagnose bei abgeschnittenem JSON

Der Monitor zeigt Content-Length als Zahl, tatsächlich gelesene Bytes, führenden
und abschließenden Whitespace mit CR/LF-Anzahl sowie eine abschließende Objektklammer.
Bei unvollständigem JSON prüft er ausschließlich während einer Aufzeichnung bis
zu 64 zusätzliche Bytes mit maximal 150 ms Wartezeit. Angezeigt werden nur deren
Anzahl und ob sie das JSON vervollständigen, niemals ihr Rohinhalt. Die Verbindung
wird danach geschlossen; Zusatzbytes werden nicht für Steuerungsbefehle verwendet.
Bei kurzen Reads werden EOF, Timeout oder Lesefehler mit der gelesenen Länge erfasst.

- Gelesen = angekündigt, Zusatzbytes vervollständigen JSON: Die deklarierte Grenze
  liegt vor dem JSON-Ende; kein Abschneiden innerhalb der gelesenen Bytes.
- Gelesen < angekündigt: Übertragung vorzeitig beendet oder Lesen fehlgeschlagen.
- Gelesen = angekündigt, kein vollständiges JSON auch mit Zusatzbytes: Body bereits
  fehlerhaft oder innerhalb des kurzen Diagnosefensters unvollständig; ohne
  weitere Messung ist die genaue Ursache nicht bewiesen.

Ein lokaler Test mit zwei zusätzlichen führenden CR/LF-Bytes reproduziert das
Abschneiden am Content-Length-Limit. Das ist noch kein Nachweis für den echten
Miniserver. Nach Installation Aufzeichnung starten und den Loxone-Befehl auslösen.
