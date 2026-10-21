# Login, Tokenanzeige und Loxone-Export

## Historische, zielgebundene Prototypwartung

Dieser Abschnitt ist kein RC1-Updater und keine Neuinstallation. Reguläre Nutzer beginnen mit [INSTALL.md](../INSTALL.de.md). Nur für den damaligen LoxBerry-Prototyp: vollständigen geprüften Quellbaum einschließlich `scripts/copy-runtime.sh`, `src/`, `docker/`, `config/` und Assets unter dem Staging-Pfad bereitstellen, Ziel und Sicherung prüfen. `HUE_PUBLIC_URL` muss der tatsächlichen bestehenden HTTPS-Adresse entsprechen; das Beispiel unten ist anzupassen. Nicht auf andere Installationen anwenden.

Im bestehenden Root-Terminal auf LoxBerry:

```sh
export HUE_PUBLIC_URL=https://192.0.2.96:8443
sh /opt/loxberry/hue2lox-web-staging/scripts/install-web.sh
```

Bei einer neuen Installation gilt standardmäßig **admin / admin**. Ein vorhandenes Passwort wird bei normalen Updates nicht verändert. Zur ausdrücklich gewünschten Rücksetzung einer bestehenden Installation:

```sh
export HUE_PUBLIC_URL=https://192.0.2.96:8443
sh /opt/loxberry/hue2lox-web-staging/scripts/install-web.sh --reset-admin
```

Gespeichert wird ausschließlich ein zufällig gesalzener PBKDF2-SHA256-Hash mit 600.000 Iterationen in `data/admin_auth.json` (UID/GID 10001, Modus 600). Die Datei liegt auf dem geschützten persistenten `/data`-Mount, damit sie im Web geändert werden kann. Ein bisheriger Hash aus `secrets/admin_auth.json` wird einmal übernommen, wenn noch keine Runtime-Datei vorhanden ist. Das öffentliche Standardpasswort ist absichtlich bekannt; individuelle Passwortwerte/Hashes, Hue-Keys und Tokens werden nicht versioniert.

Danach https://192.0.2.96:8443/ vollständig neu laden und anmelden. Persönliche Zertifikats-Vertrauensregel bleibt Voraussetzung für eine warnungsfreie Browseranzeige. Es werden keine Lampenbefehle durch Login oder Export gesendet.

Das Installationsscript sichert Quellcode, Compose und Webdateien unter `/opt/loxberry/hue2lox-backups/web-<Zeitstempel>`. Bestehende `compose.override.yaml`, Registry und Hue-/Steuerungsschlüssel bleiben erhalten. Basis-Compose bekommt den zusätzlichen Read-only-Mount für die Admin-Datei. Beim Wiederherstellen einer Sicherung die gesicherten Dateien an ihre alten Orte kopieren und `docker compose up -d --build` ausführen.

## Verwendung

Unter „Loxone“:

- Token anzeigen (30 Sekunden, bei Fokusverlust verborgen).
- HTTP-Header einschließlich Bearer-Token und Content-Type kopieren, bei EIN und bei digitalen Befehlen auch AUS einsetzen.
- Befehle je Lampe: Ein/Aus, Dimmen und je Fähigkeit/Freischaltung RGB und Lumitech.
- XML pro Lampe oder eine gemeinsame XML für ausgewählte/alle eingerichteten Lampen.
- Standardmäßig enthalten XML-Dateien einen Token-Platzhalter. „Token in XML aufnehmen“ erstellt eine Datei mit Zugangsdaten; entsprechend privat aufbewahren.

Es gibt derzeit ein gemeinsames Hue2Lox-Steuerungstoken für alle eingerichteten Lampen. Der Hue-Bridge-Key wird niemals ausgegeben. Die Lampenliste zeigt die Runtime-Registry. Neue Bridges, Link-Tasten-Kopplung und automatische Inventur sind unter „Bridges“ verfügbar; siehe BRIDGES.md. Disabled Bridges sind nicht exportierbar. Weitere registrierte Lampen erhalten einen kontrollierten Endpunkt `/api/lights/<bridge-id>/<light-id>/state`. Bestehendes `/hue-go/state` bleibt kompatibel.

In Loxone Config: XML unter virtuelle Ausgänge importieren. Ein/Aus ist digital, Dimmen numerisch. RGB-/Lumitech-Ausgänge nach dem Import mit dem entsprechenden Aktortyp verbinden/prüfen. Der Export ändert und speichert keine bestehende Miniserver-Konfiguration. Nicht parallel mehrere der exportierten Steuerarten auf dieselbe Lampe senden, wenn nur der Lumitech-Kreis genutzt werden soll.

## Sicherheit und Grenzen

Die Web-Verwaltung und Übersicht verlangen einen Login. `/health`, bestehendes `/hue-go/status` und die mit Bearer-Token geschützte Loxone-Steuerung behalten ihre bisherige Verwendung.

Sitzungen verwenden zufällige 256-Bit-Tokens, serverseitig nur als SHA256-Schlüssel im Speicher. Cookie `__Host-hue2lox_session`, Secure, HttpOnly, SameSite=Strict. 30 Minuten Inaktivität oder maximal 12 Stunden; Neustart beendet alle Sitzungen. Auch ein Passwortreset im Server-Terminal entwertet bestehende Sitzungen bei der nächsten Anfrage ohne Neustart. Passwortversuche werden auf fünf je Quell-IP pro fünf Minuten und global 100 begrenzt. Admin-Abrufe prüfen den Host gegen `HUE_PUBLIC_URL`; POST-Aufrufe außerdem Origin/Fetch-Site und nach Login ein CSRF-Token. Kein Vertrauen in Proxy-Forwarded-Header. Antworten mit Zugangsdaten: no-store, no-referrer, nosniff. Keine Tokens in URLs oder localStorage.

Für eine andere Installationsadresse `HUE_PUBLIC_URL=https://<Host>:<Port>` in `.env` setzen, Compose neu erstellen und den passenden Zertifikatsnamen verwenden. Die Browseradresse muss exakt zu dieser URL passen. Passwortwechsel ist oben im Webinterface über „Passwort ändern“ möglich: aktuelles Passwort, neues Passwort (mindestens 5 Zeichen) und Bestätigung eingeben. Danach werden alle Sitzungen beendet und eine neue Anmeldung ist nötig. Reverse Proxy, mehrere Nutzer und dauerhaft gespeicherte Sitzungen sind nicht enthalten.

Passwort zurücksetzen (Root, vorhandener Benutzer admin):

```sh
cd /opt/loxberry/hue2lox-prototype
python3 src/admin_auth.py data/admin_auth.json --username admin
docker compose up -d --force-recreate
```

## XML-Format und Prüfung

Struktur: `VirtualOut` / `Info templateType=3` / `VirtualOutCmd`, PUT, Header, JSON-Bodies, Analog-Flags und Wiederholung 0. XML-Sonderzeichen werden escaped. Der Header enthält die wörtlichen Zeichenfolgen `\r\n` statt echter CR/LF-Zeichen; GUI-Anzeige, Kopierfunktion und XML stimmen überein. Formatabgleich mit dem veröffentlichten Template des Autors:
https://github.com/wkulhanek/loxone-shelly/blob/main/VirtualOut/VO_shelly_powerstrip_4_gen_4.xml

Historischer Prüfstand vom 18.10.2026 (keine aktuelle Release-Abnahme): 36 lokale Tests bestanden: Zugriffssperren, CSRF/Origin/Host, Cookie-Flags, Ablauf/Logout, Rate-Limit, Token-Platzhalter, Einzel-/Mehrfachauswahl, XML-Escaping, kontrollierte Lampenpfade und bisherige Steuerung. UI mit simulierten Daten geprüft: Login, Token anzeigen/verbergen, Headerkopie, Auswahl und XML-Download. Der tatsächliche Import in Loxone Config 17.2 sowie Container-Build und Betrieb dieser Version auf LoxBerry sind bis zur Installation noch nicht bestätigt.

## Bridge-Ausbau

Bridges hinzufügen/koppeln und automatische Lampeninventur sind in BRIDGES.md beschrieben. Die aktive Registry liegt nun auf `/data/registry.json`; neue Hue-Keys liegen geschützt auf demselben persistenten Mount. Nicht ins Git- oder Image-Backup aufnehmen. Bestehende Benutzer- und Steuerungstoken-Dateien bleiben erhalten.

Für ein explizites Zurücksetzen auf admin/admin ohne interaktive Passwortwahl kann der CLI-Aufruf um `--default` ergänzt werden. Ein normales Update ruft diese Rücksetzung nicht auf.

## Navigation

Zentrale Miniserver- und Tokenverwaltung: **Loxone-Einstellungen**.
Lampenbefehle, Kopierfunktionen und Einzel-/Mehrfach-XML stehen direkt unter
**Lampen**. Dort gelten Bridge-/Raumfilter und Suche auch für die sichtbaren
Treffer von **Gefilterte auswählen**. Bei **Szenen** bleibt der entsprechende
Aufbau mit eigenen Filtern erhalten.

Lampenausgaben enthalten `recommended_mode`, `enabled_modes`, Lampentyp und
Fähigkeiten. `POST /api/admin/lights/usage` akzeptiert `bridge_id`, `light_id`,
`modes` (nicht leere Liste unterstützter IDs); Sitzung, Same-Origin und CSRF gelten.
Gespeichert werden nur lokale Nutzungspräferenzen; keine Hue-Schreibzugriffe.

Der XML-Endpunkt akzeptiert optional `variants` als Zuordnung von Lampenschlüssel
zu einer Modus-ID oder einer Liste davon: `switch`, `dim`, `tw`, `rgb`, `lumitech`.
Ohne Varianten werden die gespeicherten Checkboxen oder die Empfehlung verwendet.
Ungültige/unsupported IDs und doppelte/leer gewählte Listen werden abgewiesen.
Szenenexport bleibt unverändert. `tw` verwendet Weißtemperatur über den
Lumitech-Body; die Bridge meldet dabei keine RGB-Fähigkeit.
