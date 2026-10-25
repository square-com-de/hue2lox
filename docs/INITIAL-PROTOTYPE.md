> **Historischer Stand / Historical record:** Aussagen, Befehle und offene Punkte unten gelten ausschließlich für den genannten damaligen Stand, nicht als aktuelle Installationsanleitung oder 1.0.3-Abnahme. / Statements, commands and pending checks below apply only to the recorded revision. [Aktuelle Dokumentation / current documentation](INDEX.md) · [1.0.3-Vorbereitung / preparation](PREPARATION-1.0.3.md).

# Hue2Lox – minimaler HTTPS-Prototyp

> Für die Veröffentlichung anonymisiert: Adressen, Geräte-IDs und Lampennamen sind Beispiele.

Ausschließlich `GET /health` → HTTP 200, `Content-Type: application/json`, Body exakt `{"status":"ok"}`. Keine Hue-Anbindung, API-Keys, XML-Erzeugung oder Änderungen an Loxone. Andere Pfade liefern 404. Python-Standardbibliothek, TLS ab 1.2, Port 8443.

## Voraussetzung und Zertifikat

Docker Engine mit Compose-Plugin und OpenSSL mit `req -addext` müssen bereits verfügbar sein. Docker wurde in der Entwicklungsumgebung nicht vorgefunden; ein Container-Build konnte dort nicht ausgeführt werden. ARM/ARM64-Unterstützung des Basisimages muss zum Betriebssystem passen; ein altes 32-Bit-DietPi gegebenenfalls vorab prüfen.

Das Zertifikat ist selbstsigniert, 365 Tage gültig und enthält SANs für `192.0.2.96`, `127.0.0.1`, `localhost`, `hue2lox.local`. Der DNS-Name wird damit nicht automatisch im Netzwerk registriert. Der Schlüssel bleibt im lokalen, ignorierten Verzeichnis `certs/`, wird weder ins Image kopiert noch bei Updates neu erzeugt. Keine Schlüssel weitergeben. Das Script überschreibt vorhandene Zertifikate nicht. Bei Erneuerung Dienst stoppen, alte Dateien geschützt sichern, neue erstellen und Dienst neu starten.

## Betrieb auf LoxBerry / DietPi (192.0.2.96)

Diese Schritte sind manuell auszuführen; es wurde nichts remote installiert oder gestartet. Docker-Verfügbarkeit zuerst auf dem Ziel prüfen:

```sh
docker version
docker compose version
openssl version
```

Nur diesen Projektordner übertragen, niemals die übergeordnete Hue-Inventur oder deren `.env`. Beispiel vom Mac, mit dem tatsächlichen SSH-Benutzer und einem bestehenden Zielpfad:

```sh
rsync -av --exclude=certs --exclude=.env --exclude=__pycache__ \
  ~/Projects/Loxone/hue/hue2lox/ BENUTZER@192.0.2.96:~/hue2lox/
```

Auf dem Ziel:

```sh
cd ~/hue2lox
cp .env.example .env
# In .env setzen: HUE2LOX_BIND_IP=192.0.2.96
sh scripts/create-cert.sh
# Öffentliches Zertifikat für spätere curl-Prüfung verfügbar halten:
cp certs/server.crt ./health-test.crt
# Container läuft als UID 10001; Schlüsselverzeichnis nur für diesen Benutzer:
sudo chown -R 10001:10001 certs
sudo chmod 700 certs
sudo chmod 600 certs/server.key
sudo chmod 644 certs/server.crt
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs --tail=50 hue2lox
curl --fail --show-error --cacert ./health-test.crt https://192.0.2.96:8443/health
```

Erwartung: `{"status":"ok"}`, Compose meldet nach spätestens rund 35 Sekunden `healthy`. Bei fehlenden Docker-Rechten die Docker-Befehle entsprechend mit `sudo` ausführen. Keine Router-Portfreigabe einrichten. Host-Firewall muss TCP 8443 vom Miniserver 192.0.2.10 und gegebenenfalls vom Test-Mac zulassen. Stoppen: `docker compose down` (Zertifikate bleiben erhalten).

Vom Mac dasselbe öffentliche `health-test.crt` verwenden und denselben curl-Aufruf ausführen. `curl -k` kann einmalig zur Eingrenzung dienen, prüft aber die Identität des Servers nicht. Ohne explizites Vertrauen muss normales curl das selbstsignierte Zertifikat ablehnen.

## Lokaler Test ohne Docker

```sh
cd ~/Projects/Loxone/hue/hue2lox
sh scripts/create-cert.sh
TLS_CERT=certs/server.crt TLS_KEY=certs/server.key BIND_HOST=127.0.0.1 python3 app.py
```

In einem zweiten Terminal:

```sh
cd ~/Projects/Loxone/hue/hue2lox
curl --fail --cacert certs/server.crt https://127.0.0.1:8443/health
```

Beenden mit Strg+C. Für lokalen Docker-Betrieb gilt dieselbe UID-/Zertifikats-Berechtigungsvoraussetzung wie oben; Standardbindung ist ausschließlich 127.0.0.1. Vor dem Eigentümerwechsel Host-Tests abschließen.

## Loxone Miniserver Gen2 (192.0.2.10) – manueller Entscheidungstest

Die offizielle Dokumentation bestätigt HTTP(S)-URLs bei virtuellen HTTP-Eingängen. Sie dokumentiert dort jedoch weder die Akzeptanz selbstsignierter Serverzertifikate noch einen passenden Vertrauensimport. Daher ist die Kompatibilität mit diesem Zertifikat **offen**. Die Zertifikatseinstellungen für eingehende Verbindungen zum Miniserver belegen nichts über dessen ausgehende HTTPS-Verbindungen.

Quelle, geprüft am 17.10.2026: https://www.loxone.com/dede/kb/virtueller-http-eingang/

1. Zunächst den obigen curl-Test vom LAN aus erfolgreich abschließen.
2. Loxone Config und Firmware-Version notieren, aktuelle Konfiguration sichern. Separates Testprojekt bzw. eine Kopie vorbereiten. Nichts ungeprüft in die produktive Konfiguration schreiben.
3. Unter „Virtuelle Eingänge“ einen „Virtueller HTTP Eingang“ anlegen. URL `https://192.0.2.96:8443/health`, Abfragezyklus 10 Sekunden, Timeout 5000 ms. Keine Benutzer-/Passwortangaben.
4. Den Antwort-/Befehlserkennungsdialog zur Kontrolle öffnen. Ein erfolgreicher Abruf durch Loxone Config am PC beweist noch keinen Abruf durch den Miniserver. Der JSON-Wert `ok` ist Text; für diesen Transporttest ist kein numerischer Eingangs-Befehl nötig.
5. Ein tatsächlicher Miniserver-Test erfordert die spätere, bewusst freigegebene Übertragung der Testkonfiguration. Das kann die laufende Anlage beeinflussen und ist nicht Teil der hier ausgeführten Arbeiten. Nach Freigabe HTTP-Monitor/Diagnose in Loxone Config und parallel `docker compose logs -f hue2lox` prüfen. Erwartet werden wiederholte GET /health mit 200 im Serverprotokoll und die korrekte Antwort in der Diagnose. Monitor-Verfügbarkeit hängt von der Config-Version ab.
6. Ergebnis mit Config-/Firmware-Version und Uhrzeit protokollieren. Ein TLS-Handshakefehler erzeugt eventuell keinen HTTP-Zugriffslog. Bei Fehlschlag erst Erreichbarkeit, Portbindung, Firewall und dann TLS-Diagnose prüfen. Ein erfolgreicher curl-Test mit `--cacert` oder `-k` beweist keine Zertifikatsakzeptanz des Miniservers.

Bei Zertifikatsablehnung ist dieser Test gescheitert. Nicht ungeprüft Zertifikatsprüfung abschalten. Als nächsten Schritt die für diese Firmware unterstützte Vertrauenskette mit Loxone klären; eventuell einen gültigen DNS-Namen und ein vom Miniserver akzeptiertes CA-Zertifikat verwenden. Ein öffentlich vertrauenswürdiges Zertifikat für die private IP 192.0.2.96 ist dabei kein üblicher Lösungsweg.

## Nach erfolgreichem HTTPS-Test

Erst Ergebnis dokumentieren und den Transport festlegen. Danach separat Hue-v2-Zugriff für eine Hue Go, Pairing per Bridge-Knopf bzw. manuelle Eingabe in einer eigenen `.env`, persistente Zugangsdaten und Loxone-XML-Export planen. Dieser Prototyp liest keine `.env` der Inventur und implementiert keinen dieser Schritte.
