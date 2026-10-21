# Aktueller Installationstest – 20.10.2026

Vom Nutzer auf einer frisch installierten Debian-13-VM unter Proxmox bestätigt:
- Interaktiver Installer erfolgreich abgeschlossen; Weblogin funktioniert.
- Hue Bridge gefunden und gekoppelt.
- 1 Bridge, 27 Lampen und 3 Szenen angezeigt.
- Vollständiger VM-Neustart: Webinterface wieder erreichbar, Bridge und Lampen weiterhin vorhanden.

Dieser Test bestätigt Installation, automatischen Start und gespeicherte Einrichtung. Er ist keine vollständige Loxone-Funktionsabnahme und kein Test jeder unterstützten Distribution.

## Historische Testprotokolle

# Testprotokoll – 17.10.2026

> Für die Veröffentlichung anonymisiert: Adressen, Geräte-IDs und Lampennamen sind Beispiele. Dokumentation verwendet TEST-NET-Adressen (192.0.2.0/24); automatisierte Tests verwenden synthetische private Adressen (10.200.0.0/24), weil die Bridge-Validierung private Netze voraussetzt.

Aktueller Stand (18.10.2026): Lumitech mit Warm-/Kaltweiß, RGB, Helligkeit
und Ein/Aus aus dem Lichtsteuerungsbaustein vom Nutzer bestätigt.
Die folgenden Abschnitte halten auch frühere Entwicklungsphasen fest; Aussagen
wie „noch nicht getestet“ beziehen sich jeweils auf diese Phase.


## Erfolgreich

- Container-Build und Start auf DietPi/LoxBerry (linux/amd64, Python 3.12 Alpine).
- Ursprünglicher Container wurde als healthy bestätigt; Status unmittelbar nach
  dem letzten Update: health: starting. Späteres healthy noch nicht separat belegt.
- `/health`: HTTP 200, application/json, exakt `{"status":"ok"}`.
- `/hue-go/status`: HTTP 200, „Beispiellampe“, on=true, brightness=47.04
  zum Testzeitpunkt, tls_verified=true.
- Beide Endpunkte vom Mac mit explizitem Serverzertifikatsvertrauen erreicht.
- Ohne dieses Vertrauen lehnt curl das selbstsignierte Serverzertifikat ab.
- Miniserver-HTTP-Monitor: Hue2Lox HTTPS Test Response, HTTP/1.0 200 OK.
- Bridge-Zugriff mit CA-Kette und Bridge-ID erfolgreich: Zielhost Python 3.11
  und anschließend echter Python-3.12-Container beim Update.
- Falsche Bridge-ID und falscher Vertrauensanker: SSLCertVerificationError.
- Drei Endpunkttests auf Mac und LoxBerry bestanden: Health ohne Bridge-Zugriff,
  Status und generischer 502-Fehler, 404 und Ablehnung von PUT.
- Separater HTTPS-Testserver auf Loopback des LoxBerry mit geprüftem Testzertifikat:
  beide Endpunkte HTTP 200, Status dabei live von der Bridge gelesen.
- Compose-Konfiguration und Shell-Syntax des Updatescripts geprüft.

## Hinweise

- Erster curl-Versuch während Containerneustart: Verbindung abgelehnt;
  automatische Wiederholung und folgende Prüfungen erfolgreich.
- Buildx fehlt; klassischer Docker-Builder baut erfolgreich.
- Mac Python 3.9/LibreSSL lehnt Datumsformat des Bridge-Zertifikats ab;
  das ist kein Grund, die Zertifikatsprüfung im Betriebscontainer abzuschalten.
- Laufende Dateien: /opt/loxberry/hue2lox-prototype/.
- Rückrollkopie vor Status-Update:
  /opt/loxberry/hue2lox-backups/20261017-224551/.
- Kein Schalten, kein Dimmen, keine Farbe und keine bestehenden Loxone-Einstellungen geändert.
- Noch kein Steuerausgang oder Loxone-Statusmapping eingerichtet.

Historische Ersttests: INITIAL-TEST-RESULTS.md.

## Vorbereitung Ein/Aus und Dimmen

10 Tests bestanden: bisherige 3 Endpunkttests plus 7 Steuer-/Clienttests.
Ausschließlich Mock-Bridge; kein echter Hue-PUT, kein Lampenschalten.
Standardmäßig gesperrt, Tokenprüfung für spätere Aktivierung.
Container-Build dieser Erweiterung und echter Schalt-/Dimmtest stehen noch aus.
Details: CONTROL.md.

## Nutzerbestätigte Live-Ergebnisse und Farbvorbereitung

- Root-Live-Test: Aus/Ein, 25 % (24,9), 70 % (69,96), Wiederherstellung Ein/47,04 %.
- Ein/Aus und Dimmen aus Loxone Config 17.2.8.28 vom Nutzer bestätigt.
- Status bei externem Ausschalten: on=false, Helligkeit bleibt gespeichert.
- Farberweiterung nur mit Mock-Bridge getestet; kein echter Farb-PUT, kein Deployment.
- 18 Tests insgesamt bestanden, einschließlich bestehender Kontrollfunktionen.

## Erfolgreicher RGB-Live-Test aus Loxone

Datum: 17.10.2026. Nachweis: vom Nutzer bereitgestelltes Root-Installationsprotokoll
und anschließende ausdrückliche Bestätigung „es gehen alle farben und helligkeit
aus dem lichtbaustein heraus als rgb test“.

- Loxone Config: 17.2.8.28; Miniserver-HTTPS-Steuerweg zuvor erfolgreich bestätigt.
- Hue Go: Beispiellampe, light 00000000-0000-4000-8000-000000000001, Bridge EG1.
- Farb-Image e0c6bc3a9f08 erfolgreich auf LoxBerry gebaut und gestartet.
- Rollback-Dateien: /opt/loxberry/hue2lox-backups/color-20261017-234517/.
- Lesender Container-Test erfolgreich, tls_verified=true; Health und Status HTTP 200.
- Kurzer Verbindungsfehler beim Neustart; anschließender Wiederholungsversuch erfolgreich.
- HUE_COLOR_ENABLED=1 wurde im bestehenden lokalen Override ergänzt und der Dienst neu gestartet.
- Im RGB-Lichtkreis wird Farbe samt Helligkeit über PUT /hue-go/state und
  {"loxone_rgb":<v>} übertragen; numerischer Ausgang, RGB-Aktortyp.
- Der Nutzer bestätigt alle Farben und Dimmen aus dem Lichtbaustein als funktionierend.
- Keine einzelnen Farb-Messwerte und kein eigener HTTP-Monitor-Auszug des RGB-Tests vorhanden;
  daher keine Behauptung einer farbmetrischen Prüfung oder separat belegter RGB-Statuscodes.
- Vorheriger Root-Schalttest stellte Ein/47,04 % wieder her. Für den späteren manuellen
  Farbtest wurde keine Wiederherstellung protokolliert.
- Container wurde nach dem Farb-Update zunächst mit health: starting angezeigt;
  ein späterer Docker-Status healthy wurde nicht erneut übermittelt.
- 18 Mock-/Endpunkttests der Farberweiterung zuvor bestanden; bei dieser reinen
  Dokumentationsänderung keine neuen Lampenbefehle oder unnötigen Testwiederholungen.

Nicht umgesetzt: separate Weiß-/Farbtemperatursteuerung und Statussynchronisierung
in den Lichtsteuerungsbaustein. Letztere ist aktuell ausdrücklich nicht gewünscht.

## Warm-/Kaltweiß und Lumitech vorbereitet

25 Tests bestanden, ausschließlich mit Mock-Bridge. 2000/2700/4000/6500 K
und Lumitech-Weißcodierung geprüft; bestehende RGB-Zuordnung bleibt erhalten.
Keine Lampe verändert. Container-Build und Lumitech-Live-Test stehen noch aus.
WHITE.md dokumentiert die Grenze zwischen implementiert und live bestätigt.

## Erfolgreicher Lumitech-Test – 18.10.2026

Nachweise: Nutzerprotokoll der Installation, Screenshots/Bestätigung der Loxone-
Bedienung und eigener lesender HTTPS-Statusabruf. Keine neuen Lampenbefehle
für diese Dokumentation ausgeführt.

- Weiß-Image 030f3ca5b9f5 erfolgreich gebaut und gestartet.
- Rollback-Dateien: /opt/loxberry/hue2lox-backups/white-20261017-235832/.
- Installationsscript prüfte nur lesend und beließ Weiß zunächst gesperrt.
- Nach HUE_WHITE_ENABLED=1 funktionierten auch Ein/Aus, RGB und Dimmen über
  das neue Feld loxone_lumitech. Nutzer bestätigt anschließend Warm-/Kaltweiß.
- Lichtbaustein: Lumitech; PUT /hue-go/state, {"loxone_lumitech":<v>},
  bestehende Bearer-Authentisierung. Kein Tokenwert dokumentiert.
- Eigener HTTPS-Statusabruf mit geprüftem Serverzertifikat: status=ok,
  on=true, brightness=58.1, color_temperature.mirek=370,
  mirek_valid=true, tls_verified=true. Das entspricht rund 2703 K.
- Screenshot zuvor: 58 % / 4847 K. Der spätere Istwert 370 Mirek bestätigt
  diesen konkreten Sollwert NICHT (erwartet wären rund 206 Mirek).
  Kein synchroner Soll-/Ist-Trace; daher keine abschließende Aussage zur Ursache.
- Kaltweiß funktional vom Nutzer bestätigt; kein separater Kaltweiß-Status-Snapshot.
- Keine optische Präzisionsmessung und keine Prüfung aller Kelvin-Grenzwerte.
- 25 automatisierte Mock-/Endpunkttests waren vor Deployment erfolgreich.
  Kein erneuter Testlauf für diese reine Dokumentationsänderung erforderlich.
- Docker-Status beim Start: health: starting; späterer healthy-Status nicht erneut belegt.
- Keine automatische Zustandswiederherstellung für den manuellen Lumitech-Test protokolliert.
- Statussynchronisierung in den Lichtbaustein bleibt ausdrücklich außerhalb des Umfangs.

## Web-Interface vorbereitet – 18.10.2026

31 Tests bestanden. Browser-Vorschau mit simulierten Daten visuell geprüft;
Navigation, Lampensuche und Loxone-Seite funktionsfähig. Keine Lampe verändert.
Statische Dateien nur per Allowlist; Übersicht ohne Keys oder private Schlüssel.
Mehrere Bridges/Lampen mit Mock-Daten geprüft; weitere echte Bridges bleiben deaktiviert.
Build/Live-Deployment dieser UI steht noch aus. Details: WEB.md.

## Login und Loxone-Export – 18.10.2026

- 36 Tests bestanden, einschließlich bestehender Status-/Steuerungs-/Farbtests.
- Ohne Session kein Admin-Token, kein Export und keine Übersicht; Bearer-Token allein reicht nicht für Verwaltung.
- CSRF-, Origin-, Host- und Fetch-Site-Sperren, Session-Cookie-Flags, Ablauf, Logout und Login-Versuchsbegrenzung geprüft.
- XML mit zwei simulierten Lampen, Sonderzeichen, Header-Zeilenumbrüchen, Token/Platzhalter und mehreren Steuerarten geprüft. Export sendet keinen Hue-PUT.
- UI mit ausschließlich Testzugangsdaten: Anmeldung, Token einblenden/verbergen, Headerkopie, Auswahl und XML-Download erfolgreich.
- Container-Build/Betrieb dieser Version und echter Import in Loxone Config 17.2 bleiben bis zur Installation/importseitigen Prüfung offen.

## Bridge-Verwaltung – 18.10.2026

- Vollständiger finaler Testlauf: 45 Tests bestanden.
- Neue Tests prüfen private Zieladressen, TLS-Identitätslernen ohne unsicheren Fallback, Link-Tasten-Antwort, Schlüsselrechte und -redaktion, Wiederkopplung, Inventur, erhaltene Aliase und fehlende Lampen.
- Browserprüfung mit Testdaten: Bridge hinzufügen, Kopplung, drei Lampen/Schaltaktoren erkennen und in die Loxone-Liste übernehmen. Keine produktiven Hue-Schlüssel verwendet.
- Echte EG-Bridge rein lesend per neuem Probe-Modul auf LoxBerry geprüft: BSB002, Bridge-ID 001788FFFE000001, Firmware 1978418030, tls_verified=true.
- Realer Kopplungsschlüssel wurde nicht angelegt; reale Vollinventur und Container-Build/Betrieb dieses Ausbaus bleiben bis zur Root-Installation offen.

## Einfaches Standardpasswort und Web-Passwortwechsel – 18.10.2026

- Standard admin/admin bei Neuinstallation oder ausdrücklich gesetztem Installer-Parameter `--reset-admin`. Normale Updates erhalten individuelle Passwörter.
- Mindestlänge 5 Zeichen; gesalzener PBKDF2-Hash bleibt bestehen.
- Tests für Passwortwechsel mit aktuellem Passwort, CSRF-/Session-Pflicht, Fehlversuchsbegrenzung, abgewiesene kurze Passwörter, Sitzungssperre und Fehler beim Speichern.
- Individuelle Zugangsdaten und Runtime-Hashes bleiben aus Git und Image ausgeschlossen.

- Alle 45 bisherigen Tests ohne Fehler im gemeinsamen Lauf; nach Korrektur der Zwei-Client-Testanordnung alle 5 neuen Passworttests bestanden. Browser: Formular öffnen, Mindestlänge und Eingabefelder geprüft; keine reale Zugangsdatenänderung über Browserautomation.


## Lampenverwaltung – 18.10.2026

Automatische Gesamtsuite erfolgreich: 68 Testausführungen einschließlich fünf
neuer Tests für persistentes Ignorieren, Wiederherstellen, lokale Entfernung,
Wiederentdeckung mit erhaltenem Hue-Go-Alias, Export-/Steuerungssperren,
Validierung, konkurrierende Inventur und Anmeldung/CSRF/Origin-Schutz. In diesem
Lauf wurden durch importierte Testklassen einige bestehende Tests doppelt
ausgeführt; die Einbindung wurde anschließend bereinigt.
Die fünf neuen Tests danach erneut separat bestanden.
Browserprüfung ausschließlich mit lokalen Testdaten: ignorieren, ignorierte
anzeigen, wieder einblenden und bestätigtes Entfernen erfolgreich.
Keine echte Lampe geschaltet oder von einer Bridge gelöscht.
Remote-Containerbetrieb nach Installation noch durch Nutzer zu bestätigen.


## Szenen – 18.10.2026

Gesamtsuite abschließend: 64 Tests bestanden. Neun neue Szenentests prüfen
Raum-/Zonen-Zuordnung, Rescan/Umbenennung/Löschung, Erhalt bei fehlerhafter
Inventur, Bridge-Zuordnung, Hinweise für ignorierte Lampen, XML-Escaping und
EIN-only-Befehle, exakten Hue-Recall, Hue-Fehler, ungültige Ressourcendaten,
Sitzung/CSRF, Bearer-Token, Schreibfreigabe und strikte Body-Validierung.
Ein fehlerhafter Duplikat-Testdatensatz wurde vor dem abschließenden Lauf korrigiert.
Browserprüfung mit lokalen Testdaten: Einlesen, Mehrfachauswahl, Aufklappen und
XML-Download erfolgreich. Keine echte Szene aktiviert; echter XML-Import und
Loxone-Aufruf nach Installation noch offen.


## Szenensynchronisierung und lokale Auswahl – 18.10.2026

69 Tests bestanden. Fünf zusätzliche Tests prüfen persistentes Ignorieren und
Wiederherstellen samt Aufruf-/Exportsperre, lokale Entfernung und Wiederfinden,
leere erfolgreiche Inventur mit Entfernung alter Einträge, fehlerhafte Angaben
und Bridge-Sperre sowie Sitzung/CSRF/Origin-Schutz der Verwaltungsendpunkte.
Der bestehende Löschtest erwartet jetzt die vollständige Entfernung statt eines
ausgegrauten alten Eintrags. Fehlgeschlagene Inventuren erhalten weiterhin Daten.
Browserprüfung mit ausschließlich Testdaten: eine simulierte Hue-App-Löschung
wird über den oberen Aktualisieren-Button übernommen; Ignorieren, Anzeige der
ignorierten Szene, Wiederherstellen und bestätigtes lokales Entfernen bestanden.
Keine echte Szene aktiviert, verändert oder von einer Hue Bridge gelöscht.


## Gerätesuche und neues Dashboard – 18.10.2026

Abschließende Gesamtsuite: 79 Tests bestanden. Zehn neue Tests prüfen
Miniserver-UDP/SSDP, mDNS-Auswertung und ungültige DNS-Kompression, lokale
URL-Validierung und unveränderte Speicherung bei Fehlern, Suchsperre und
Fehlermeldungen, Speicherung/Entfernung des Links, Szenenzählung sowie
Sitzung/CSRF/Origin. Ein anfangs zu breiter Socket-Mock wurde korrigiert.
Reale Suchläufe vom Mac und vom LoxBerry-Host fanden jeweils den Miniserver
192.0.2.10 und drei Bridges (.253, .136, .137). Browserprüfung mit Testdaten:
Suche, Übernahme beider Gerätetypen, Speichern und Dashboard-Link erfolgreich.
Keine Geräte gekoppelt, keine Miniserver-Konfiguration geändert, keine Lampen
geschaltet. Suche im tatsächlichen Docker-Netz und Installation bleiben durch
den Root-Benutzer zu prüfen; Host-Sucherfolg ist dafür kein Nachweis.


## Temporärer HTTP-Monitor – 18.10.2026

87 Tests bestanden. Acht neue Tests prüfen: ausgeschalteten Standardzustand,
Ablauf mit simulierter Zeit, 200-Einträge-Limit, Generationstrennung und Leeren
während laufender Requests, strikte Daten-Allowlist, Stop-Verhalten, Anmeldung/
Origin/CSRF, Erfolgs- und Fehlerantworten sowie Ausschluss von Tokens, Schlüsseln,
fehlerhaften Body-Zeichenketten und Query-Parametern. Ein bestehender Kontrolltest
wurde für die beabsichtigte 405-Antwort bei falscher Methode angepasst.
Browserprüfung ausschließlich lokal mit simuliertem Hue-Schreiben: Start,
HTTP 200/401/400/405-Anzeigen, Stoppen, Kopieren und Leeren bestanden.
Keine echte Lampe geschaltet. Containerinstallation und echter Loxone-Aufruf
bleiben nach dem Root-Update durch den Benutzer zu prüfen.


## Bridge- und Raumfilter – 18.10.2026

Reine Browseränderung; mit lokalen Testdaten für zwei aktive Bridges, mehrere
Räume und eine Hue-Zone geprüft. Lampen: Bridge einschränken, Raum auswählen,
Namenssuche kombinieren und nicht mehr passenden Raum beim Bridgewechsel
zurücksetzen erfolgreich. Szenen: Bridge, Zone und Suchtext kombinieren sowie
nur gefilterten Treffer für XML auswählen erfolgreich (Auswahlzähler 1).
Dropdown-Optionen werden bei unveränderten Daten nicht neu aufgebaut, damit
die laufende Statusaktualisierung die Bedienung nicht unterbricht.
Keine Backend- oder Steuerungsänderung, keine echte Lampe geschaltet.


## Lampenbefehle in gemeinsamer Ansicht – 18.10.2026

Browserprüfung mit lokalen Testdaten erfolgreich: Suche auf Hue Go, Auswahl
des gefilterten Treffers (XML-Zähler 1), aufklappbare Befehle mit Ein/Aus,
Dimmen, RGB und Lumitech direkt in der Lampenkarte, XML-Download aus Lampen.
Loxone-Einstellungen ohne doppelte Lampenliste bestätigt: nur Miniserver und
Zugriffstoken. Szenenbereich mit Bridge- und Raum-/Zonenfiltern vorhanden.
Keine Backend- oder Steuerungsänderungen; keine echte Lampe geschaltet.


## Kopierfelder in Loxone-Reihenfolge – 18.10.2026

Browserprüfung mit lokalen Testdaten erfolgreich: Szenen und Lampen zeigen
Befehlsname, EIN-Pfad, EIN-Header, EIN-Body und EIN-Methode in dieser Reihenfolge.
Ein/Aus zeigt zusätzlich die AUS-Felder, Lumitech die passenden Analogwerte.
Der Befehlsname entspricht dem bestehenden XML-Titel. Header-Anzeige mit
Platzhalter und separater Kopierfunktion; Basisadresse separat aufklappbar.
Reine Darstellung geändert; keine echte Lampe geschaltet.


## Bebilderte Anleitung – 18.10.2026

Drei gezielte Webtests bestanden, einschließlich HTTP 200 und Sicherheitsheader
für die neue Hilfeseite, deren CSS und alle drei Screenshot-Endpunkte.
Browserprüfung: verständliche Überschriften, Tabellen, dargestellter numerischer
Platzhalter <v> und eingebundene Bilder geprüft. Der Config-Screenshot enthält
leere Header; die Hue2Lox-Screenshots nur Testdaten und Platzhalter.
Kein Zugriff auf eine produktive Loxone Config, keine Lampensteuerung und kein
realer XML-Import durch die Dokumentationserstellung.

## Steuerungsart und kompakter Export (18.10.2026)

- 91 automatisierte Tests erfolgreich: Vorauswahl anhand der Fähigkeiten und
  Freigaben, genau eine Variante je Lampe, unterschiedliche Varianten im
  Mehrfach-XML, Ablehnung ungültiger Auswahlen, Authentifizierung und bestehende
  Szenen-/Bridge-/Steuerungsfunktionen.
- Browserprüfung mit simulierten Bridges: Hue Go empfiehlt Lumitech, dimmbare
  Weißlampe Dimmen und Steckdose Ein/Aus. Wechsel auf Ein/Aus zeigt EIN/AUS-Felder;
  Rückwechsel zeigt nur den Lumitech-Body. Keine echten Hue-Schreibzugriffe.
- Anleitung gekürzt und Befehlsabbildung durch die neue Auswahl ersetzt.
- Runtime-Installation auf LoxBerry weiterhin über install-web.sh als root;
  diese lokalen Tests bestätigen keinen bereits aktualisierten Container.

## Bereinigte Diagnose abgelehnter Bodies (18.10.2026)

94 Tests erfolgreich. Neue Prüfungen decken abgelehnte RGB-/Helligkeitswerte,
numerische Zeichenketten, nicht ersetztes <v>, JSON-Fehlerpositionen sowie
Geheimnisfilterung bei gültigen und kaputten Bodies ab. HTTP-Tests bestätigen
sichtbare Fehler-Bodies ohne Hue-Schreibzugriffe. Browserprüfung mit simulierten
HTTP-400-Einträgen bestätigt Anzeige von Zahl, Zeichenkette und JSON-Fehler.
Unauthentifizierte Anfragen erhalten keine Body-Diagnose; die zehnminütige,
begrenzte Speicherung im Arbeitsspeicher bleibt bestehen.

## HTTP-Body-Grenzen (18.10.2026)

Lokaler HTTP-Test vergleicht korrekte Länge, zwei zusätzliche führende CR/LF-Bytes,
fehlende Schlussklammer und vorzeitiges EOF. Falsch begrenzte Anfragen bleiben
abgelehnt und lösen keinen Hue-Aufruf aus. Zusatzbytes werden nur gezählt und
auf JSON-Vollständigkeit geprüft, ohne Rohinhalt zu protokollieren. Der echte
Miniserver muss nach Installation erneut bei aktiver Aufzeichnung getestet werden.

Gesamte Testsuite: 95 Tests erfolgreich. JavaScript-Syntax geprüft.

## Persistente Lampen-Kurzpfade (18.10.2026)

GUI-Metadaten und XML verwenden /<bridge>/<lampe>/state, je Name maximal acht
URL-taugliche Zeichen. Geprüft: Normalisierung, Kollisionsauflösung, reservierter
API-Namensraum, Persistierung, Umbenennen, Entfernen und erneutes Einlesen sowie
alte UUID-Pfade. HTTP-Test bestätigt Ziel-ID, Authentifizierung, falsche Methode
und korrekten Pfad im Monitor ohne echte Hue-Zugriffe. Für die bestehenden Tests
wird die einmalige Registry-Migration vor Zustandsvergleichen abgeschlossen.
Der Miniserver-Livevergleich kurzer/langer Pfad steht nach Installation noch aus;
eine Behebung der CR/LF-Verschiebung wird nicht behauptet.

Finaler Stand: alle 99 Tests erfolgreich; JavaScript-Syntax geprüft.

## Einheitliches Loxone-Headerformat (18.10.2026)

Bisherige Inkonsistenz: Anzeige mit LF, Clipboard und XML mit echten CR/LF.
Korrigiert auf eine Zeile mit wörtlichem \r\n, ohne reale Zeilenumbrüche und ohne
zusätzlichen Abschluss. Gleicher Helper für Lampen-/Szenenansicht und zentrale
Headerkopie; XML verwendet identische Zeichen. Regressionstest führt den echten
JavaScript-Helper mit Testtoken in Node aus und vergleicht dessen Ergebnis mit
XML-Roundtrips für Ein/Aus, Dimmen, RGB und Lumitech einschließlich AUS-Header.
100 Tests erfolgreich. Keine echten Tokens oder Hue-Schreibzugriffe verwendet.
Die unveränderte HTTP-Validierung bleibt aktiv; es werden keine zusätzlichen
Bytes für Steuerung akzeptiert. Bestehende Loxone-Header müssen nach Installation
neu eingesetzt werden. Die vollständige Behebung der CR/LF-Verschiebung am echten
Miniserver ist erst nach dessen neuem Testprotokoll bestätigt.

## Lampentypen, Nutzungsarten und Tunable White (18.10.2026)

Die Bridge meldete Weißtemperatur bereits; im Export fehlte ein eigener Modus
für reine Tunable-White-Lampen. Neue TW-Variante verwendet Lumitech im Weißmodus,
inklusive Ausschalten bei deaktiviertem RGB-Feature. Fähigkeiten-Badges und Typ
kommen von der Bridge; Modellreferenzen ergänzen nur Produktnamen.

Geprüft sind alle Typen, Modell-Fallback, gespeicherte Nutzungsarten, Ablehnung
unpassender/leer gewählter Modi, Erhalt bei Inventur, Einzel-/Mehrfachmodus-XML,
Admin-/CSRF-Schutz sowie unveränderte Header-/Kurzpfad-Verarbeitung. Browserprüfung
mit simulierten Lampen bestätigt TW-Vorauswahl, Fähigkeits-Badges, Speichern einer
zusätzlichen Checkbox und Vorschau des passenden Bodys. Keine echte Lampe geschaltet.

Modellreferenz: 949 eindeutige IDs aus dem Philips-Gerätekatalog von
zigbee-herdsman-converters, Quelle/SHA-256 und Lizenz enthalten; kein offizielles
vollständiges weltweites Herstellerverzeichnis. Daten bleiben lokal im Image.

Finaler Stand: 106 Tests erfolgreich, JavaScript-Syntax und Installer-Syntax geprüft.
Der CSV-Download enthält nur öffentliche Katalogdaten, keine Installationsdaten.

## CSV-Download (18.10.2026)

Am laufenden LoxBerry geprüft: HTTPS-Abruf mit explizit vertrautem Serverzertifikat,
HTTP 200, 169369 Bytes, SHA-256 identisch zur lokalen CSV. Die gemeldeten Browser-
Downloadabbrüche lassen sich damit nicht auf fehlende oder abgeschnittene CSV-Daten
zurückführen; die genaue Browserursache ist nicht bewiesen.

GUI lädt die CSV nun wie XML über Fetch/Blob statt direktem Download-Link. Expliziter
Attachment-Dateiname ergänzt. Gezielter HTTP-Test prüft Bytegleichheit, Content-
Length und Content-Disposition; JavaScript-Syntax geprüft. CSV enthält nur öffentliche
Modelldaten, keine Tokens, Keys oder Installationsdaten.
Browserprüfung mit lokalem Testkonto: CSV-Button ruft die Datei erfolgreich ab und
startet den Blob-Download. Der konkrete Chrome-/Zertifikatskontext des Nutzers
muss nach Installation erneut geprüft werden.

## Kompakte Exportleiste (18.10.2026)

Browserprüfung mit simulierten Lampen: Standardansicht zeigt bei 1280x720 bereits
die erste Lampe. Hilfe/Modelltabelle klappt auf und zu; gefilterte Auswahl wählt
vier Fixture-Lampen und „Auswahl leeren“ setzt die Auswahl zurück. Bestehende IDs
und Bedienelemente vollständig erhalten und eindeutig, JavaScript-Syntax geprüft.
Keine Änderungen an API, Lampensteuerung, Zugangsdaten oder XML-Format.

## Verdichtete Lampenkarten (18.10.2026)

Browserprüfung mit simulierten Lampen bei 1280x720: drei vollständige Karten
sichtbar. Aufklappen der Nutzungsarten, Öffnen der Befehle mit Modusvorschau und
Erhalt des offenen Verwaltungsbereichs nach Rendern bestätigt. Ignorieren und
Wiedereinblenden der lokalen Testlampe funktionieren auch ohne Export-Metadaten
für ignorierte Lampen. Keine echte Hue-Schaltung. JavaScript-Syntax und Diff geprüft.
API, Header, Pfade, gespeicherte Nutzungsarten und XML-Erzeugung unverändert.

### 2026-10-18 – Kompakte Szenenkarten
- JavaScript-Syntax geprüft.
- Lokale Browser-Vorschau mit Testdaten bei 1280×720: drei vollständige Szenenkarten sichtbar.
- Befehle und Verwaltung geöffnet/geschlossen; Verwaltung bleibt beim Öffnen der Befehle offen.
- Gefilterte Auswahl und Auswahl leeren geprüft (3 → 0). Keine realen Hue-Befehle gesendet.

### 2026-10-19 – Deutsch/Englisch und Release-Vorbereitung

- Vollständige Suite: 112 Tests bestanden. Nach Ergänzung der nur bei Neuinstallation deaktivierten Legacy-Hue-Go-Endpunkte 17 betroffene Tests erneut bestanden.
- `scripts/smoke-install.py`: echte separate lokale HTTPS-Instanz aus neu erzeugtem Installationsverzeichnis, Zertifikatsprüfung aktiv, Health, unauthentifiziert 401, admin/admin, CSRF-Ablehnung, leere Registry, DE/EN-Assets, englische Anleitung, Quellenhinweise und Neustart mit gleichem Token/Zertifikat bestanden. Keine Docker- oder Hue-Aufrufe.
- Neuinstallation erzeugt unabhängige Schlüssel/Token, verweigert vorhandene Zielverzeichnisse, validiert IP/Port und setzt private Dateirechte. Bestehende Einrichtung nicht verändert.
- Browser mit Testdaten: Login auf Englisch, Lampen/Befehle/Empfehlung und Szenen/Filter auf Englisch, unveränderte deutsche Gerätenamen, Rückwechsel auf Deutsch auf derselben Seite mit bestehender Sitzung geprüft. Screenshots in der Anleitung bleiben deutsch und sind in der englischen Fassung entsprechend beschriftet.
- XML-Test: nur generierte Beschriftungen übersetzt; Gerätename, Pfad, Methode, Body und tatsächliche Headerzeichen bleiben identisch. Keine Tokens/Keys in Übersetzungen oder Testsicherungen.
- Noch offen: Docker-Build/Start, UID/Mounts, Netzwerksuche und echter Miniserver auf einem frischen Linux-Testsystem; keine vollständige Release-Freigabe. Auf dem ausführenden Mac ist kein Docker verfügbar.
- Quellenhinweise ergänzt. Eigene Projektlizenz auf Wunsch noch nicht festgelegt; Repository bleibt privat.
