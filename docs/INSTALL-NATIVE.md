# Native Linux-Installation ohne Docker

[English](INSTALL-NATIVE.en.md) · [Dockerinstallation](../INSTALL.de.md)

Dieser zusätzliche Betriebsweg auf main verwendet denselben Anwendungskern und dieselbe Oberfläche wie Docker. RC1 bleibt unverändert. Es gibt noch kein veröffentlichtes natives Releasepaket. **Der native Weg ist experimentell.** Explizite Testziele sind Debian 12/13, Ubuntu 24.04/26.04 und DietPi auf Debian 12/13, derzeit nur amd64. Ein Testziel ist keine bestätigte Hardwarefreigabe.

## Gemeinsamer interaktiver Installer (Entwicklung)

RC5 bleibt unverändert und enthält diesen nativen Installer nicht. Verwende einen sauberen, geprüften Git-Checkout von PR #18 und notiere die genaue Commit-ID. Kein veränderlicher main-Download gilt als freigegebenes natives Paket. Den vorhandenen Assistenten als root starten (`su -`, auf Ubuntu gegebenenfalls `sudo -i`):

```sh
bash /absoluter/pfad/zu/hue2lox/install-assistant.sh
```

Nach der Sprachwahl **Mit Docker** oder **Nativ, ohne Docker** wählen. Der Dockerweg behält seine vorhandene HTTP-/HTTPS- und Proxy-Auswahl. Das native Menü bietet:

1. Plattform und Voraussetzungen nur lesend anzeigen.
2. SSH bei Bedarf einrichten.
3. Grundpakete ausdrücklich installieren (kein Docker-Repository und keine Docker-Installation).
4. Entwicklungspaket lokal aus dem sauberen Git-Checkout vorbereiten. Der Assistent erfasst den Commit, berechnet und prüft die Paketprüfsumme und entfernt sein temporäres Paketverzeichnis beim Beenden.
5. Nach IP-/HTTPS-Port-Auswahl und Bestätigung nativ installieren. Für direkten Browserzugriff die LAN-Adresse des Servers verwenden; Loopback ist über die manuelle Adresseingabe möglich. Ein Tunnel ist nur für Fernzugriff auf einen Loopback-Listener erforderlich.
6. HTTPS des vorhandenen nativen Dienstes mit Zertifikatsprüfung testen (keine Gerätekopplung).
7. Wartung: Update mit Sicherung, Wiederinstallation mit Datenerhalt, ausdrückliches Rollback oder Deinstallation mit Datenerhalt. Rollback stellt auch den früheren Passwortstand wieder her. Das Menü bietet keine vollständige Datenlöschung an.

Für ein separat erhaltenes natives Archiv dessen unabhängig geprüfte SHA-256 übergeben:

```sh
bash /absoluter/pfad/zu/hue2lox/install-assistant.sh --deployment native \
  --native-package /absoluter/pfad/native.tar.gz --native-sha256 GEPRUEFTER_SHA256
```

Ein Quell-ZIP ohne Git-Identität erfindet keinen Commit und lädt kein main nach. Der native Paketschritt fragt stattdessen nach einem geprüften Archiv und dessen SHA-256. Es gibt noch kein veröffentlichtes natives Release-Asset. Ein vorbereitetes Entwicklungspaket heißt `0.0.0-dev.<commit>`; es ist kein Release. Bei einem Codeupdate den Assistenten aus dem neu geprüften Checkout neu starten. Wiederinstallation benötigt dieselbe Paketidentität wie der erhaltene Datenstand; gegebenenfalls das frühere geprüfte Archiv verwenden. Native Datenpfade bleiben fest und sind unabhängig vom Docker-Installationsordner.

Die optionale Auswahl `--check --deployment native` ist nur lesend. Backend-Auswahl und Statusanzeige allein ändern keine Installation. Echte Ubuntu-/DietPi-VM-Abnahmen und native Hardwaretests bleiben offen; Plattform-Fixtures und systemd-Container-CI ersetzen sie nicht.

## Voraussetzungen und Grenzen

Verwende eine frische, isolierte Testinstanz mit systemd, System-Python ab 3.11, OpenSSL und Rootzugriff. Native Testziele: Debian 12/13, Ubuntu 24.04/26.04 und DietPi auf Debian 12/13, nur amd64. Ubuntu 22.04, unbekannte Ableitungen, Raspberry Pi OS, ARM und 32-Bit-Systeme werden nativ derzeit abgelehnt. Für Docker gilt weiterhin dessen eigene Plattformliste. Python und OpenSSL kommen vom Betriebssystem; eine virtuelle Python-Umgebung ersetzt keine passende TLS-Laufzeit. Die Anwendung benötigt keine pip-Pakete. Der Installer prüft Voraussetzungen, führt aber kein Betriebssystemupgrade aus.

Der native Installer richtet einen Systemdienst und Systemverzeichnisse ein. Nicht auf einem Arbeitsplatzrechner oder einer produktiven Installation ausprobieren. Docker wird weder benötigt noch verändert. Bestehende Dockerdaten werden nicht automatisch übernommen. Paralleler Betrieb erfordert getrennte Daten, Namen und Ports; verwende beispielsweise Port 18443 für den nativen Test.

## Paket vorbereiten

Bis ein natives Release verfügbar ist, erstellt ein Entwickler aus einem geprüften Checkout ein Paket:

```sh
python3 scripts/build-native-package.py --version VERSION --output /tmp/hue2lox-native-package
```

`VERSION` durch die geplante Paketversion ersetzen. Commit und Paketinhalt werden im Manifest erfasst. Ein Paket aus einem veränderten Arbeitsbaum ist kein unveränderliches Tag-Release. Das Paket enthält Anwendung, Oberfläche, Katalog, Vertrauensanker, Konfigurationsvorlage, Lizenztexte und native Werkzeuge; keine produktiven Daten.

Paket und SHA-256 müssen aus einem vertrauenswürdigen, unabhängig überprüfbaren Übergabeweg stammen. Ein selbst berechneter Hash allein beweist keine Herkunft. Niemals einen veränderlichen main-Download als freigegebenes natives Release behandeln.

## Neuinstallation

Paket in ein temporäres Arbeitsverzeichnis entpacken. Im entpackten Paket zeigt folgender Aufruf die Optionen, ohne zu installieren:

```sh
bash deployment/native/install.sh --help
```

Danach auf der isolierten Zielinstanz installieren; Pfade, Hash und IP ersetzen:

```sh
sudo bash deployment/native/install.sh \
  --package /tmp/hue2lox-native.tar.gz \
  --sha256 GEPRUEFTER_SHA256 \
  --host 192.168.1.50 --port 18443
```

`192.168.1.50` ist nur eine Beispieladresse, nicht automatisch die Adresse deines Servers. Verwende dessen feste LAN-IP. Der Installer akzeptiert derzeit nur lokale IPv4-Adressen und Ports ab 1024. Er verweigert eine Neuinitialisierung vorhandener Daten. Er erstellt eigene Zugangsdaten und ein Zertifikat, startet den Dienst und prüft HTTPS mit Zertifikatsprüfung. Er sucht keine Bridge und schaltet keine Lampen. Schlägt der erste HTTPS-Test fehl, bleiben Dateien zur Diagnose erhalten; die Installation gilt dann nicht als erfolgreich. Nicht erneut initialisieren, sondern Ursache beheben oder ausdrücklich deinstallieren.

Nach erfolgreicher Einrichtung die ausgegebene HTTPS-Adresse öffnen, Zertifikatsfingerabdruck über einen vertrauenswürdigen Weg prüfen und mit `admin` / `admin` anmelden. Passwort in der Oberfläche ändern. Schreib-, Farb- und Weißsteuerung sind bei Neuinstallation zunächst deaktiviert. Pairing und Loxone-Einrichtung gehören zu einer separat freigegebenen Hardwareabnahme, siehe [Abnahmeplan](ACCEPTANCE.md).

## Dateien und Betrieb

| Pfad | Zweck |
| --- | --- |
| `/opt/hue2lox/releases/<version>-<commit>-<id>/` | Root-eigener, für den Dienst nicht beschreibbarer Anwendungscode |
| `/opt/hue2lox/current` | Aktive Anwendungsversion |
| `/etc/hue2lox/settings.env` | Explizit von systemd geladene Betriebseinstellungen |
| `/etc/hue2lox/` | Geschützte Zertifikate und Steuerungstoken |
| `/var/lib/hue2lox/` | Registry, Passwortdatei und Bridge-Keys |
| `/var/backups/hue2lox/` | Geschützte Updatesicherungen |

Der Dienst läuft als eigener Benutzer `hue2lox` ohne interaktiven Login. Konfiguration und private Dateien sind nicht allgemein lesbar; der Dienst darf seinen Zustand schreiben, aber weder Anwendung noch Systemkonfiguration ändern. Keine feste Container-UID wird verwendet.

```sh
sudo systemctl status hue2lox
sudo journalctl -u hue2lox --since today
sudo systemctl restart hue2lox
```

Logs vor einer Weitergabe auf private Angaben prüfen. Tokens, Schlüssel, Passworthashes und vollständige Backups niemals in Issues hochladen.

## Aktualisieren und Rückweg

Nur ein festes natives Paket verwenden. Aus dessen entpacktem Verzeichnis:

```sh
sudo bash deployment/native/update.sh \
  --package /tmp/hue2lox-native-neu.tar.gz \
  --sha256 GEPRUEFTER_SHA256
```

Der Updater prüft und bereitet die neue Anwendung vor, stoppt den Dienst, sichert privaten Zustand und vollständigen bisherigen Anwendungscode und schaltet anschließend um. Passwort, Token, Zertifikat und Inventar bleiben erhalten. Schlägt der Start-/HTTPS-Test fehl, stellt der Rückweg bisherigen Code und dazugehörigen Zustand wieder her. Aktuell wird nur Registry-Schema 1 unterstützt; andere Schemata werden vor dem Umschalten abgelehnt, es gibt keine automatische Migration. Die Abschlussmeldung und das angegebene Backup prüfen. Bleibt ein Fehler bestehen, Dienst stoppen und die Sicherung erhalten; nicht durch eine Neuinstallation ersetzen.

Es gibt keinen unbeaufsichtigten Updatetimer und keine automatische Aktualisierung auf main. Datenmigrationen benötigen einen ausdrücklich unterstützten Migrations- und Rückweg; nicht beliebige ältere Versionen über neuere Daten starten.


### Späteres Rollback nach zunächst erfolgreichem Update

Die neuen Updatesicherungen enthalten vollständigen Code, Konfiguration und Zustand samt Prüfsummen. Den bei einem Update ausgegebenen Sicherungsordner ausdrücklich auswählen:

```sh
sudo sh deployment/native/rollback.sh --backup /var/backups/hue2lox/ZEITSTEMPEL-ID
```

Der Rückweg prüft die Sicherung vor dem Stoppen, sichert den aktuellen Stand und stellt Code **und den damaligen privaten Datenstand** wieder her. Änderungen an Passwort, Inventar und Schlüsseln seit dieser Sicherung gehen dabei auf den damaligen Stand zurück. Bei Startfehlern wird die Sicherung des unmittelbar vorherigen Stands wiederhergestellt. Scheitert auch das, bleibt eine ausdrückliche Fehlermeldung mit Sicherungspfad; Dienst und Logs prüfen. Ein Stromausfall während des Austauschs erfordert gegebenenfalls manuelle Wiederherstellung. Alte Sicherungen ohne vollständigen Code und `snapshot.json` werden abgelehnt. Der Dienst wird nach erfolgreichem Update/Rollback für den Systemstart aktiviert.

## Sicherung und Wiederherstellung

Für eine konsistente manuelle Sicherung den Dienst stoppen. `/etc/hue2lox` und `/var/lib/hue2lox` mit Eigentümern und Rechten sichern und Version/Commit des aktiven Pakets notieren. Dienst danach wieder starten. Backup verschlüsselt oder nur für root zugänglich auf einem getrennten Speichermedium aufbewahren. Es enthält Geheimnisse und ermöglicht die Steuerung der eingerichteten Geräte.

Wiederherstellung zunächst isoliert testen: passenden Anwendungsstand bereitstellen, Dienst stoppen, Konfiguration und Zustand mit den ursprünglichen Rechten zurückspielen und anschließend Dienst/HTTPS prüfen. Nicht gleichzeitig zwei wiederhergestellte Instanzen mit echten Bridges betreiben. Ein erfolgreicher lokaler Start ist keine bestätigte Hardwarewiederherstellung.

## Zertifikatserneuerung und IP-Wechsel

Das Zertifikat muss die öffentliche IP beziehungsweise den verwendeten Namen als Subject Alternative Name enthalten. Bei Ablauf oder Adresswechsel zuerst vollständiges Backup erstellen und den Dienst stoppen. Zertifikat und Schlüssel gemeinsam für die neue Adresse erzeugen; die in `settings.env` eingetragenen Pfade beibehalten und gegebenenfalls öffentliche Adresse/Bindadresse korrigieren. Die private Schlüsseldatei muss weiter nur für root und die Dienstgruppe lesbar sein. Danach Dienst starten und HTTPS mit dem neuen Zertifikat prüfen, bevor Browser- und Miniserververtrauen erneuert werden. TLS-Prüfung nicht dauerhaft abschalten.

Für das unveränderte Standardlayout lässt sich das Zertifikat nach der Sicherung so erneuern. Die Beispiel-IP ersetzen. Den Block in einer Root-Shell (`sudo -i`) ausführen:

```sh
set -eu
umask 077
systemctl stop hue2lox
renew_dir=$(mktemp -d /etc/hue2lox/certs/.renew-XXXXXX)
trap 'rm -rf "$renew_dir"' EXIT
openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 365 \
  -keyout "$renew_dir/server.key" -out "$renew_dir/server.crt" \
  -subj /CN=hue2lox.local \
  -addext 'subjectAltName=IP:192.168.1.50,IP:127.0.0.1,DNS:localhost' \
  -addext extendedKeyUsage=serverAuth
install -o root -g hue2lox -m 0640 "$renew_dir/server.key" /etc/hue2lox/certs/server.key
install -o root -g hue2lox -m 0640 "$renew_dir/server.crt" /etc/hue2lox/certs/server.crt
# Bei IP-Wechsel vor dem Start BIND_HOST und HUE_PUBLIC_URL in settings.env anpassen.
systemctl start hue2lox
openssl x509 -in /etc/hue2lox/certs/server.crt -noout -fingerprint -sha256
```

Bei einem Fehler bleibt der Dienst gegebenenfalls gestoppt; ursprüngliches Zertifikat/Schlüssel aus der Sicherung zurückspielen und die Ursache prüfen. Die native Verwaltung erwartet weiterhin eine IPv4-Adresse in `BIND_HOST` und `HUE_PUBLIC_URL`. Eigene DNS-basierte Betriebsmodelle sind derzeit nicht vorgesehen.

Dieser Wartungsablauf erfordert einen gesonderten Test auf dem Zielsystem. Nicht den Neuinstaller erneut aufrufen: Passwort, Token, Registry und Bridge-Keys müssen erhalten bleiben.

## Deinstallation

```sh
sudo bash deployment/native/uninstall.sh
```

Entfernt den eigenen Dienst und native Programmdateien. Private Konfiguration, Zustand und Sicherungen bleiben standardmäßig erhalten. Nur wenn diese Daten bewusst verworfen werden sollen:

```sh
sudo bash deployment/native/uninstall.sh --purge-data
```

Sicherungen und der Systembenutzer bleiben auch mit `--purge-data` erhalten. Aufbewahrte Daten verhindern eine erneute frische Installation; nicht mit dem Neuinstaller überschreiben. Vorher ein getrenntes Backup erstellen. Die Löschung privater Daten ist nicht rückgängig zu machen. Dockerinstallationen werden nicht entfernt.


### Wiederinstallation mit erhaltenen Daten

Nach einer Deinstallation ohne `--purge-data` das **gleiche geprüfte Paket** (Version, Commit und Dirty-Kennzeichen) wie vor der Deinstallation verwenden. IP und Port müssen den erhaltenen Einstellungen entsprechen:

```sh
sudo sh deployment/native/install.sh --keep-data \
  --package /tmp/hue2lox-native.tar.gz --sha256 GEPRUEFTER_SHA256 \
  --host 192.168.1.50 --port 18443
```

Dabei werden keine Zugangsdaten, Zertifikate oder Registry neu erzeugt. Anschließend sind reguläre Updates möglich. Ohne `--keep-data` bleibt vorhandener Zustand geschützt. Eine unterbrochene Deinstallation lässt sich mit demselben Deinstallationsaufruf fortsetzen; fremde Dienstdateien und Symlinks werden vor Änderungen abgelehnt.

## Teststand und offene Abnahmen

Lokale Tests und CI gelten nur für die jeweils dokumentierten Prüfungen. Ein echter Debian-Systemstart, systemd-Rechte und Wiederherstellung benötigen Tests auf einer Wegwerfinstanz. Discovery, Pairing, Bridge-TLS, Loxone-HTTPS/XML und tatsächliche Lampenwirkung bleiben separate Hardwareabnahmen. Nicht getestete Plattformen sind nicht unterstützt.

Das spätere LoxBerry-Plugin kann gemeinsame Zustandsvorbereitung und Anwendung verwenden. Seine Verzeichnisse, Dienstintegration und Update-Hooks sind ein eigenes Arbeitspaket.

[Manuelle VM-Abnahme und offene Nachweise](NATIVE-VM-ACCEPTANCE.md).
