# Anmeldung, Zugriffstoken und Loxone-Export

Aktueller Funktionsumfang für den 1.0.3-Kandidaten; [English user manual](MANUAL.md) · [Handbuch](MANUAL.de.md) · [Installation](../INSTALL.de.md).

## Anmeldung und Passwort

Frische Daten beginnen mit **admin/admin**. Danach oben **Passwort ändern** wählen: aktuelles Passwort, neues Passwort (mindestens fünf Zeichen) und Bestätigung. Ein Update oder eine Wiederinstallation mit Datenerhalt übernimmt das bisherige Passwort; `HUE2LOX_ADMIN_PASSWORD` ist nur ein Startwert für neue Zugangsdaten und kein Reset.

Gespeichert wird ein zufällig gesalzener PBKDF2-SHA256-Hash mit 600.000 Iterationen, im Standardcontainer unter `/data/admin_auth.json`, nativ unter `/var/lib/hue2lox/admin_auth.json`. Passwörter, Keys und Tokens gehören nicht in Git oder öffentliche Ausgaben. [Speicher und Sicherung](CONTAINER.md#persistente-dateien).

## Sitzung und Browseradresse

Sitzungen verwenden zufällige 256-Bit-Tokens, serverseitig nur als SHA256-Schlüssel im Arbeitsspeicher. Sie enden nach 30 Minuten Inaktivität oder maximal zwölf Stunden; Neustart beendet sie. Passwortwechsel beendet alle Sitzungen. Cookies sind HttpOnly, SameSite=Strict und an `/` gebunden. Bei HTTPS heißt das Secure-Cookie `__Host-hue2lox_session`; reines HTTP verwendet `hue2lox_session` ohne Secure und überträgt Zugangsdaten unverschlüsselt.

Verwaltungszugriffe prüfen Host/Origin; Änderungen benötigen zusätzlich CSRF. Bei expliziter `HUE_PUBLIC_URL` ist diese Adresse maßgeblich. Ohne sie wird direkter localhost-/privater IP-Zugriff aus der tatsächlichen Anfrage abgeleitet. Beliebige DNS-Namen und Proxy-Forwarded-Header ersetzen keine ausdrückliche Proxykonfiguration. [Konfigurationsort und Traefik](CONTAINER-SETUP.de.md#http-oder-https).

Loginversuche werden je Quell-IP und global begrenzt. Hinter einem Proxy können mehrere Nutzer denselben Socket-Absender teilen. Antworten mit Zugangsdaten sind `no-store`; Tokens werden weder in URLs noch in localStorage abgelegt. Es gibt ein gemeinsames Administratorkonto, keine Mehrbenutzer-/Rollenverwaltung und keine dauerhaft gespeicherten Sitzungen.

## Token und virtuelle Ausgänge

Unter **Loxone-Einstellungen** lässt sich das Hue2Lox-Steuerungstoken kurz anzeigen oder als vollständiger HTTP-Header kopieren. Es ist nicht der Hue-Bridge-Key. Neue Bridge-Schlüssel bleiben intern.

Befehle und Einzel-/Mehrfach-XML stehen direkt bei **Lampen** und **Szenen**. XML enthält standardmäßig einen Token-Platzhalter. **Token in XML** fügt echte Zugangsdaten ein; die Datei entsprechend geschützt aufbewahren. Header sind eine Zeile mit der sichtbaren Zeichenfolge `\r\n` zwischen Authorization und Content-Type, ohne abschließende Leerzeile.

Der XML-Import erfolgt in Loxone Config unter virtuellen Ausgängen. Basisadresse, Aktortyp, Token und EIN-/AUS-Felder prüfen; [DE-Anleitung](TUTORIAL.de.md) · [EN guide](TUTORIAL.md). Export speichert keine Miniserver-Konfiguration und schaltet keine Lampen. Bestehende importierte Ausgänge werden durch ein Hue2Lox-Update nicht automatisch angepasst. Szenen besitzen [Ein/Aus und Nur aktivieren](features/SCENE-SWITCH.de.md).

## Schnittstellen und Betrieb

- `GET /health`: Dienstprüfung ohne Hue-Abfrage.
- `/api/admin/*` und `/api/overview`: geschützte Verwaltungsdaten, abgesehen von den erforderlichen Login-/Sitzungseinstiegen.
- `PUT /<bridge>/<lampe>/state`: registrierte Lampensteuerung mit Bearer-Token; alte lange Pfade bleiben kompatibel.
- `PUT /api/scenes/<bridge>/<scene>/state`: digitaler Szenen-Ein/Aus-Weg; `/recall` bleibt getrennt verfügbar.
- `recommended_mode` und `enabled_modes`: lokale Lampennutzungsarten, keine Änderung an Hue. Nutzungsänderungen erfordern Sitzung und CSRF.

Zugangsdaten vergessen? Einen ausdrücklichen Passwortreset am Server mit geschütztem Backup und dem zum Installationsweg passenden Dateipfad durchführen. Container- und native Benutzer/Rechte unterscheiden sich; keine Container-UID auf native Dateien anwenden. Nicht die Daten löschen oder neu koppeln, um eine falsche Browseradresse zu beheben.

Historische Prototyp-Updater und ihre zielgebundenen Staging-Pfade sind keine allgemeinen Installations- oder Passwortreset-Anleitungen. Ihre damaligen Ergebnisse bleiben in [historischen Testprotokollen](TEST-RESULTS.md) erhalten.
