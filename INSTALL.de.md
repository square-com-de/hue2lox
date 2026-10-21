# Hue2Lox auf Linux installieren

[English installation guide](INSTALL.md) · [RC3-Download](https://github.com/square-com-de/hue2lox/releases/tag/v1.0.0-rc.3)

- [Option 1: Einfach und komfortabel – der Installer](#option-1-einfach-und-komfortabel--der-installer)
- [Option 2: Entwicklungsstand main — Manuelle Installation Schritt für Schritt](#option-2-entwicklungsstand-main--manuelle-installation-schritt-für-schritt)

Option 1 installiert **RC3** direkt auf dem Linux-Server. Option 2 ist der getrennte Entwicklungsweg von `main`. [Version, Paket und Prüfsumme](docs/DOWNLOADS.md) gehören immer zusammen; für den normalen Einstieg Option 1 verwenden.

Hue2Lox ist für **Linux-Systeme mit Docker Engine und Docker Compose** vorgesehen – auf einem eigenen Rechner, in einer virtuellen Maschine oder auf einem Raspberry Pi. Als Plattformen kommen beispielsweise Ubuntu, Debian, DietPi oder Raspberry Pi OS (früher Raspbian) infrage, sofern Betriebssystemversion und CPU-Architektur die benötigten Pakete und Container unterstützen.

**Für den einfachen Einstieg empfehlen wir Option 1: den Installer.** Er erkennt die unterstützten Systeme und wählt die passende Paketquelle. Die manuelle Anleitung unter Option 2 verwendet Ubuntu 24.04 als Beispiel.

Du lädst die Hue2Lox-Quelldateien herunter. Der Installer lädt das benötigte Basisimage und baut daraus das Hue2Lox-Image direkt auf deinem Server. Ein fertiges Hue2Lox-Image musst du nicht separat herunterladen.

| System (64 Bit) | Automatische Einrichtung | Praktischer Teststatus |
|---|---|---|
| Ubuntu 22.04 / 24.04 / 26.04 LTS | amd64 und arm64 | Ubuntu 26.04 amd64: Installer bis HTTPS-Healthcheck erfolgreich; übrige Varianten noch offen |
| Debian 12 Bookworm / 13 Trixie | amd64 und arm64 | Debian 13 in Proxmox: Installation, Login, Bridge-Kopplung, Inventar und VM-Neustart vom Nutzer bestätigt (20.10.2026); Debian 12 und ARM noch offen |
| Raspberry Pi OS auf Debian 12 / 13 | arm64; Debian-Paketquelle | Erkennung automatisiert geprüft; Raspberry-Pi-Test noch offen |
| DietPi auf Debian 12 / 13 | amd64 und arm64; Debian-Basis automatisch erkannt | Erkennung automatisiert geprüft; DietPi-Test noch offen |
| Andere Linux-Systeme | Voraussetzungen manuell; vorhandenes Docker + Compose nutzbar | Kein allgemeines Funktionsversprechen |

**64 Bit bezieht sich auf das installierte Betriebssystem**, nicht nur auf den Prozessor. 32-Bit-Systeme und unbekannte Versionen werden bei der automatischen Paketinstallation abgelehnt. Der Installer ersetzt keine unvollständige Docker-Installation und entfernt keine vorhandenen Pakete. Läuft Docker mit Compose bereits, überspringt er die Docker-Installation auch auf anderen Distributionen. Für Hue2Lox muss Docker lokal auf dem Linux-Server laufen.

Paketquellen nach den offiziellen Anleitungen für [Ubuntu](https://docs.docker.com/engine/install/ubuntu/), [Debian](https://docs.docker.com/engine/install/debian/) und [Raspberry Pi OS 64 Bit](https://docs.docker.com/engine/install/raspberry-pi-os/). DietPi wird über seine Systemdateien erkannt und nur einer unterstützten Debian-Basis zugeordnet.

Alle Schritte der Reihe nach ausführen. Bei einem Fehler zunächst stoppen und die Ursache klären. Die alten `install-*.sh`-Dateien sind Prototyp-Updater und **nicht für diese Neuinstallation** geeignet.

# Option 1: Einfach und komfortabel – der Installer

Der Installer führt dich über ein Menü durch die Einrichtung. Er prüft vorhandene Software und kann fehlende Pakete installieren. **Du brauchst einen Linux-Server, seinen Benutzernamen und seine IP-Adresse sowie Root-Zugang oder vorhandene sudo-Rechte.** Der Installer erkennt die Systeme aus der Tabelle oben, zeigt die erkannte Basis an und wählt die passende Docker-Paketquelle. Mit einem Root-Konto kannst du die Befehle ohne `sudo` ausführen.

### A. Am Server anmelden

**Auf deinem Mac im Terminal oder unter Windows in PowerShell:** `anna` durch deinen Server-Benutzernamen und `192.0.2.50` durch dessen IP ersetzen.

```sh
ssh anna@192.0.2.50
```

Benutzer und IP findest du bei Bedarf in der Server-Konsole mit `whoami` und `hostname -I`. Alternativ kannst du PuTTY oder direkt die lokale Server-Konsole verwenden. Wenn SSH noch fehlt, zuerst den Abschnitt [Server-IP herausfinden und anmelden](#2-server-ip-herausfinden-und-anmelden) nutzen. Der Installer kann keinen noch fehlenden Fernzugang herstellen.

### B. Root verwenden und Download-Werkzeuge bereitstellen

**Die folgenden Befehle auf dem Linux-Server als Root ausführen.** Falls du noch nicht als Root angemeldet bist:

- **Debian:** `su -` → Root-Passwort eingeben.
- **Ubuntu:** `sudo -i` → dein Benutzerpasswort eingeben.

Danach in derselben Root-Sitzung fortfahren:

```sh
apt update &&
apt install -y --no-install-recommends ca-certificates curl unzip
```

Das gilt für die oben genannten Ubuntu-/Debian-basierten Systeme. Auf anderen Systemen diese drei Werkzeuge mit dem dortigen Paketmanager bereitstellen. Bei einem Fehler stoppen; bei „Not live until“ zuerst die Uhrzeit prüfen.

### C. RC3 direkt herunterladen, prüfen und starten

**Weiterhin auf dem Server als Root.** Diesen Block vollständig kopieren. Er erstellt einen neuen Downloadordner, lädt das feste RC3-Paket samt SHA-256-Prüfsumme, prüft und entpackt es und startet danach den Installer. Bestehende Ordner werden nicht überschrieben.

```sh
HUE2LOX_DOWNLOAD_DIR=$(mktemp -d "$HOME/hue2lox-rc3-XXXXXXXX") &&
cd "$HUE2LOX_DOWNLOAD_DIR" &&
curl --fail --location --output hue2lox-v1.0.0-rc.3.zip \
  https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.3/hue2lox-v1.0.0-rc.3.zip &&
curl --fail --location --output SHA256SUMS.txt \
  https://github.com/square-com-de/hue2lox/releases/download/v1.0.0-rc.3/SHA256SUMS.txt &&
sha256sum --check SHA256SUMS.txt &&
unzip -tq hue2lox-v1.0.0-rc.3.zip &&
unzip -q hue2lox-v1.0.0-rc.3.zip &&
bash "$HUE2LOX_DOWNLOAD_DIR/hue2lox-v1.0.0-rc.3/install-assistant.sh"
```

Nur bei erfolgreicher Prüfung geht es weiter. Bei `FAILED`, Downloadfehler oder Entpackfehler stoppen; den Installer nicht separat starten. Die Prüfsumme gehört zum ZIP aus demselben Release. `Code → Download ZIP` lädt dagegen den Entwicklungsstand.

**Erneut öffnen:** In derselben Root-Sitzung kannst du den letzten `bash`-Befehl wiederholen. Nach einer neuen Anmeldung den tatsächlich erstellten Downloadordner verwenden; `ls -d /root/hue2lox-rc3-*` zeigt die Standardpfade. Der Entpackordner ist nicht das spätere Installationsziel, etwa `/opt/hue2lox-test`.

### D. Im Installer weiter

Der Installer zeigt den Fortschritt mit einem kleinen animierten Oktopus. Ausführliche
Paket- und Build-Ausgaben landen in geschützten Protokolldateien; deren Pfad wird
angezeigt. Bei Fehlern erscheint der letzte Ausgabeabschnitt. Rückfragen werden
sichtbar eingeblendet. Auch wenn Python noch fehlt, zeigt der Installer bereits den Oktopus.
Fehler beim Laden oder Prüfen der Paketlisten stoppen den Schritt; bei Hinweisen
wie „Not live until“ zuerst Datum und Zeitsynchronisation des Servers prüfen. Ohne geeignetes Terminal werden einfache Statuszeilen angezeigt.

Für die vollständige direkte Ausgabe in derselben Root-Sitzung:

```sh
bash "$HUE2LOX_DOWNLOAD_DIR/hue2lox-v1.0.0-rc.3/install-assistant.sh" --verbose
```

Die kompakten Protokolle filtern erkennbare Zugangsdaten; vor dem Teilen trotzdem
auf persönliche Angaben prüfen. Linux-Pakete werden ohne optionale Empfehlungen
installiert; benötigte Abhängigkeiten bleiben enthalten.


Wähle zuerst **1 – System prüfen**. Danach kannst du die benötigten Schritte einzeln auswählen. Bereits eingerichtete Dienste musst du nicht erneut installieren.

Das Menü bietet:

1. **System prüfen:** vorhandene Software, Docker-/SSH-Zustand und Serveradressen anzeigen, ohne Änderungen.
2. **SSH prüfen/einrichten:** optional, etwa bei Arbeit an der lokalen Konsole. Bereits aktives SSH wird übersprungen; kein Root-SSH wird freigeschaltet.
3. **Grundpakete installieren:** Python, OpenSSL, curl, CA-Zertifikate und unzip.
4. **Docker prüfen/einrichten:** vorhandenes funktionierendes Docker/Compose bleibt bestehen. Unvollständige oder widersprüchliche Installationen werden nicht automatisch entfernt.
5. **Hue2Lox vorbereiten:** aus den gefundenen IPv4-Adressen die im Heimnetz erreichbare Serveradresse per Nummer auswählen (z. B. `1`); `0` erlaubt die manuelle Eingabe, `q` bricht ab. Danach freien Port abfragen, IP und Port prüfen und bestätigen; vorhandene Installationsordner werden nicht überschrieben.
6. **Starten und prüfen:** Container bauen/starten und HTTPS-Healthcheck durchführen.
7. **Zielordner wählen:** Standard `/opt/hue2lox-test`. Jede neue Installation bekommt einen zufälligen Namen, beispielsweise `hue2lox-jollyjumper-1`. Weitere Instanzen benötigen einen anderen Zielordner und freien Port.

Beim Start **Deutsch oder English** auswählen. Jeder verändernde Schritt fragt vorher nach Bestätigung: **Enter bestätigt mit Ja**, ebenso `j`/`ja` oder `y`/`yes`. Die Anzeige `[J/n]` beziehungsweise `[Y/n]` markiert diesen Standard. `n`/`nein`/`no` brechen ab. Groß- und Kleinschreibung sind egal. Bei einem Fehler stoppt der ausgewählte Schritt und kehrt zum Menü zurück; erst die Ursache klären. Mit `0` beenden. Die unterstützten Systeme und den Teststatus findest du in der Tabelle oben. Bereits funktionierendes Docker und Compose werden weiterverwendet. Der Assistent koppelt keine Bridge und aktiviert bei einer Neuinstallation keine Lampensteuerung.

**Sobald `Installation ready` erscheint, öffne die angezeigte Webadresse.** Weiter geht es bei [Webinterface öffnen und anmelden](#9-webinterface-öffnen-und-anmelden). Die folgenden nummerierten Abschnitte sind die manuelle Alternative zum Installer.

# Option 2: Entwicklungsstand main — Manuelle Installation Schritt für Schritt

## 1. Voraussetzungen

| Was? | Was du brauchst |
| --- | --- |
| Server | Linux-Rechner, VM oder Raspberry Pi mit passender Docker-Unterstützung. **Für die Befehle dieser Anleitung:** frische Ubuntu Server 24.04 LTS VM, beispielsweise in Proxmox. Vorschlag: 2 CPU-Kerne, 2 GB RAM, 20 GB Speicher; noch keine gemessene Mindestanforderung. [Ubuntu-ISO](https://releases.ubuntu.com/24.04/) → Server install image, 64-bit PC (AMD64). |
| Anmeldung | Bei der Ubuntu-Installation OpenSSH Server aktivieren. Ubuntu-Benutzername und Passwort bereithalten. Der Benutzer braucht `sudo`-Rechte; Root-SSH ist nicht erforderlich. |
| Netzwerk | Eigene lokale IPv4-Adresse der VM, erreichbar vom Mac/PC und den Bridges; möglichst feste DHCP-Zuordnung im Router. Internetzugang für Downloads. Keine Router-Portweiterleitung. |
| Arbeitsgerät | Mac mit Browser und Terminal oder Windows mit PowerShell/OpenSSH. |
| Download | [square-com-de/hue2lox](https://github.com/square-com-de/hue2lox) ist öffentlich; kein GitHub-Konto erforderlich. |
| Software auf Ubuntu | Python 3.9+, OpenSSL, curl, CA-Zertifikate, unzip, Docker Engine und Compose-Plugin. Die Installation steht unten. Git ist für den ZIP-Weg nicht nötig. |
| Für spätere Funktionstests | Hue Bridge mit erreichbarer Link-Taste und Testlampe. Loxone Miniserver und Loxone Config für den Steuerungstest. Für den ersten Login noch nicht erforderlich. |

In Proxmox nach der Ubuntu-Grundeinrichtung einen Snapshot `vor-hue2lox` erstellen, um den Test wiederholen zu können.

### Wo gehören die Befehle hin?

- **MAC:** Terminal auf deinem Mac, ohne aktive SSH-Verbindung.
- **SERVER:** Proxmox-Konsole der Ubuntu-VM oder ein Terminal nach erfolgreicher SSH-Anmeldung.
- Nur den Inhalt der Codeblöcke kopieren, keine Eingabeaufforderung wie `user@server:~$`.
- Beim Eingeben eines Passworts erscheinen im Terminal keine Zeichen. Das ist normal.

Durchgehendes **Beispiel**: Benutzer `anna`, VM-IP `192.0.2.50`. **Beides durch deine Werte ersetzen.** Die IP gehört zur neuen Ubuntu-VM, nicht zum bisherigen LoxBerry, zur Hue Bridge oder zum Miniserver.

### Netzwerkmodus der Linux-Installation

Hue2Lox verwendet standardmäßig **Host-Netzwerk** auf Linux. Dadurch kann die lokale Hue-/Miniserver-Suche direkt das Netzwerk der VM nutzen. Kein privilegierter Container ist nötig; die getrennte Docker-Netzwerkisolation entfällt. Der HTTPS-Dienst bindet nur an die bei der Vorbereitung gewählte VM-IP und den gewählten Port (hier 18443). Dieser Port muss auf der VM frei sein. Es gibt keine Docker-Portweiterleitung mehr; auch der Healthcheck verwendet die konfigurierte IP und den konfigurierten Port.

VM und Bridges müssen im gleichen erreichbaren LAN liegen. VLANs, Proxmox-/Host-Firewalls oder Multicast-Filter können die Suche weiterhin verhindern. Für Hue nutzt die Suche mDNS (UDP 5353, mit Antworten an einen temporären Port). Die manuelle IP-Eingabe bleibt verfügbar. Bei aktiver Host-Firewall HTTPS auf dem gewählten Port nur aus dem eigenen LAN erlauben. Docker Desktop auf Mac/Windows ist nicht Ziel dieses Installationswegs.

## 2. Server-IP herausfinden und anmelden

**SERVER – in der Proxmox-Konsole:**

```sh
whoami
hostname -I
```

Notiere den Benutzernamen und die IPv4-Adresse deines Heimnetzes. Eine Docker-IP wie `172.17.0.1` nicht verwenden.

**MAC – Terminal · WINDOWS – PowerShell oder PuTTY:**

Im Mac-Terminal oder in Windows PowerShell (mit installiertem OpenSSH-Client):

```sh
ssh anna@192.0.2.50
```

Alternativ mit **PuTTY unter Windows**: Bei „Host Name (or IP address)“ die Server-IP eintragen, Port `22` und Verbindungstyp `SSH` wählen, dann auf „Open“ klicken. Bei „login as“ den Ubuntu-Benutzernamen eingeben.

Beim ersten Verbinden den angezeigten Fingerabdruck mit der Ubuntu-Konsole vergleichen (`sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`) und bei Übereinstimmung `yes` eingeben beziehungsweise in PuTTY bestätigen. Anschließend das Ubuntu-Passwort eingeben. Dieses Terminal arbeitet jetzt **auf dem Server**.

### Optional: SSH-Server installieren oder starten

Je nach Auswahl bei der Ubuntu-Installation ist möglicherweise noch **kein SSH-Server installiert** oder der Dienst läuft nicht. Das ist eine mögliche Ursache für „Connection refused“. Wenn die SSH-Anmeldung bereits funktioniert, kannst du diesen Abschnitt überspringen.

Falls SSH fehlt oder nicht läuft, die folgenden Befehle **direkt in der Konsole des Ubuntu-Servers** ausführen (bei einer VM beispielsweise über die Proxmox-Konsole), nicht im Mac-Terminal:

```sh
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

Danach die SSH-Anmeldung vom Mac erneut versuchen. Falls weiterhin „Connection refused“ erscheint, mit `sudo systemctl status ssh` den Dienst prüfen und sicherstellen, dass die richtige Server-IP verwendet wird.

Bei Zeitüberschreitung IP und Netzwerk-/Proxmox-Firewall prüfen. SSH braucht TCP-Port 22 aus deinem LAN.

## 3. Grundpakete installieren

**SERVER:**

```sh
sudo apt update
sudo apt install -y python3 openssl curl ca-certificates unzip
python3 --version
openssl version
```

Ubuntu 24.04 liefert eine geeignete Python-Version und OpenSSL mit der benötigten Zertifikatsfunktion `req -addext`.

## 4. Docker installieren

**SERVER.** Dieser Abschnitt gilt für eine **frische Ubuntu-24.04-VM ohne Docker**. Ist Docker bereits installiert, zuerst `sudo docker version` und `sudo docker compose version` prüfen. Funktioniert beides, Abschnitt überspringen. Vorhandene Docker-/Snap-/containerd-Pakete nicht ungeprüft ersetzen.

Wir verwenden das [offizielle Docker-Repository für Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

```sh
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Diesen Block **vollständig bis einschließlich `EOF`** kopieren:

```sh
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```

`noble` gilt für Ubuntu **24.04**; auf anderen Ubuntu-Versionen nicht unverändert verwenden.

```sh
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker run --rm hello-world
sudo docker compose version
```

Erwartet: `Hello from Docker!` und eine Compose-Versionsnummer. Wir verwenden stets `sudo docker compose` mit Leerzeichen, nicht das alte `docker-compose`.

> **Nur Entwicklung:** Die folgenden manuellen Downloads und Dateipfade gelten für `main`, nicht für RC3. Für einen veröffentlichten Kandidaten Option 1 und [DOWNLOADS](docs/DOWNLOADS.md) verwenden.

## 5. Hue2Lox herunterladen

### Direktdownload mit curl

**SERVER – direkt im SSH-Terminal:**

```sh
curl --fail --location --output "$HOME/hue2lox-main.zip" \
  https://github.com/square-com-de/hue2lox/archive/refs/heads/main.zip
```

Die Datei wird direkt im persönlichen Ordner auf dem Server gespeichert; eine dort vorhandene Datei gleichen Namens wird ersetzt. **Kein Kopieren nötig:** Nach erfolgreichem Download direkt mit Schritt 6 „ZIP entpacken“ fortfahren.


### Alternativ: Download im Browser

**MAC oder WINDOWS – im Browser:**

1. [Hue2Lox auf GitHub öffnen](https://github.com/square-com-de/hue2lox).
2. Branch **main** auswählen. Auf **Code → Download ZIP** klicken.
3. Die Datei `hue2lox-main.zip` im Ordner `Downloads` speichern.

[Direktdownload des main-ZIP](https://github.com/square-com-de/hue2lox/archive/refs/heads/main.zip) – ohne Anmeldung.

**Nicht auf dem Mac entpacken.** Falls Safari automatisch entpackt: „Sichere Dateien nach dem Laden öffnen“ deaktivieren und erneut herunterladen. Bei mehrfachen Downloads auf Namenszusätze wie `(1)` achten; dann den Dateinamen im Kopierbefehl anpassen.

`main` ist ein Entwicklungsstand. Für den Test die aktuelle Commit-ID auf GitHub notieren. Ein ZIP eines bestimmten Commits hat einen anderen Datei-/Ordnernamen; die folgenden Beispiele beziehen sich auf das main-ZIP.

#### Nur beim Browser-Download: ZIP auf den Server kopieren

**MAC – ein zweites, neues Terminalfenster öffnen**. Nicht im bereits mit Ubuntu verbundenen SSH-Terminal ausführen:

```sh
scp ~/Downloads/hue2lox-main.zip anna@192.0.2.50:~/hue2lox-main.zip
```

Benutzer und IP ersetzen, dann das Ubuntu-Passwort eingeben. Das ZIP landet im persönlichen Ordner des Benutzers auf dem Server. Root-Rechte sind dafür nicht nötig.

Unter Windows stattdessen in PowerShell:

```powershell
scp "$env:USERPROFILE\Downloads\hue2lox-main.zip" anna@192.0.2.50:~/hue2lox-main.zip
```

Danach mit Schritt 6 im SSH-Terminal auf dem Server fortfahren.

## 6. ZIP prüfen und entpacken

**SERVER:**

```sh
unzip -tq ~/hue2lox-main.zip &&
mkdir ~/hue2lox-source &&
unzip -q ~/hue2lox-main.zip -d ~/hue2lox-source &&
cd ~/hue2lox-source/hue2lox-main &&
ls scripts/prepare-install.py scripts/start-install.py docker/compose.install.yaml
```

Die ZIP wird zuerst geprüft und nur bei Erfolg entpackt. Am Ende müssen die drei genannten Dateien erscheinen. Durch `&&` stoppt die Befehlsfolge bei einem Fehler.

„No such file“: Dateiname und Download-/Kopierziel prüfen. „Not a zipfile“: Download prüfen; möglicherweise wurde eine Anmelde- oder Fehlerseite gespeichert.

Falls `hue2lox-source` schon existiert, einen neuen Ordnernamen wählen, nichts überschreiben. Bei einem Commit-ZIP den tatsächlichen Unterordner mit `ls ~/hue2lox-source` prüfen und den `cd`-Befehl anpassen.

Das ist der **Quellordner**. Die eigentliche Installation erzeugen wir im nächsten Schritt separat unter `/opt/hue2lox-test`.

## 7. Installation vorbereiten

**SERVER – weiterhin im entpackten Quellordner.** Hier wird keine Beispiel-IP mehr vorgegeben. Zuerst die verfügbaren Adressen anzeigen:

```sh
hostname -I
```

Dann diesen Block ausführen. Gib bei der Abfrage die **IPv4-Adresse dieser Ubuntu-VM im Heimnetz** ein (nicht die der Bridge oder des bisherigen LoxBerry). Bestätige die angezeigte Adresse mit `ja`; jede andere Antwort bricht ab.

```sh
printf 'IPv4-Adresse dieser Ubuntu-VM: '
read -r HUE2LOX_TEST_IP
printf 'Neue Installation für https://%s:18443 anlegen? (ja/nein): ' "$HUE2LOX_TEST_IP"
read -r HUE2LOX_CONFIRM
if [ "$HUE2LOX_CONFIRM" = ja ] && [ -n "$HUE2LOX_TEST_IP" ]; then
    sudo mkdir -p /opt
    sudo python3 scripts/prepare-install.py --destination /opt/hue2lox-test --host "$HUE2LOX_TEST_IP" --port 18443
else
    printf 'Abgebrochen. Keine Installation angelegt.\n'
fi
```

 Port `18443` verwenden wir für diesen Test. Der Zielordner darf noch nicht existieren. Bei „Destination already exists“ nichts löschen: prüfen, ob dort eine Installation liegt. Für einen weiteren Test einen anderen Zielordner, freien Port und Compose-Projektnamen verwenden.

Erwartet: `Fresh installation prepared at /opt/hue2lox-test`.

Das Skript erzeugt eigene Schlüssel, einen zufälligen Loxone-Token, Login `admin` / `admin` und eine leere Bridge-Liste. Keine alten Konfigurationen oder Schlüssel kopieren. Noch läuft kein Container und die Lampensteuerung ist deaktiviert.

## 8. Starten und prüfen

**SERVER:** Der folgende Befehl funktioniert unabhängig vom aktuellen Terminalordner. Verwende den **frisch heruntergeladenen Quellstand**, der `scripts/start-install.py` enthält; bei älteren ZIPs zuerst die neuen Quellen in einen separaten Ordner entpacken. Eine geänderte Anleitung auf GitHub aktualisiert dein bereits heruntergeladenes ZIP nicht.

```sh
sudo python3 "$HOME/hue2lox-source/hue2lox-main/scripts/start-install.py" --destination /opt/hue2lox-test
```

Der Start kann einige Minuten dauern. Sobald `Installation ready` erscheint, öffne die angezeigte Webadresse. Bei einer Fehlermeldung findest du Hilfe am Ende unter „Fehlerbehebung“.

## 9. Webinterface öffnen und anmelden

**MAC – Browser:** Die in Schritt 8 unter `Installation ready:` ausgegebene Adresse öffnen. **https** verwenden, nicht http.

Bei „Verbindung nicht möglich“ zuerst den Healthcheck auf Ubuntu, danach IP, Port und Netzwerk-/Proxmox-Firewall prüfen. Im Host-Netzwerk gelten die Firewall-Regeln der Ubuntu-VM; der gewählte HTTPS-Port muss aus dem LAN erreichbar sein. Für den Test nur das lokale Netz verwenden, keine Router-Portweiterleitung.

Beim ersten Öffnen kann eine Zertifikatswarnung erscheinen. Hilfe dazu findest du unten unter [Zertifikat prüfen und optional dauerhaft vertrauen](#zertifikat-prüfen-und-optional-dauerhaft-vertrauen). Das dauerhafte Einrichten des Vertrauens ist optional.

### Deine Zugangsdaten beim ersten Start

| | Eingabe |
| --- | --- |
| **Benutzername** | **`admin`** |
| **Passwort** | **`admin`** |

1. Gib diese Zugangsdaten im Anmeldefenster ein und melde dich an.
2. **Ändere anschließend das Standardpasswort im Webinterface in dein eigenes Passwort.**
3. Wähle bei Bedarf **Deutsch oder Englisch** als Sprache.

**Die Übersicht ist am Anfang leer – das ist richtig.** Deine Bridges, Lampen und Szenen erscheinen erst, nachdem du im nächsten Schritt eine Hue Bridge hinzugefügt und gekoppelt hast.

**Du bist jetzt angemeldet.** Als Nächstes verbindest du deine Hue Bridge.

## 10. Danach: Bridge und eine Testlampe

1. Bridge im Webinterface suchen oder per IP hinzufügen, Link-Taste drücken und koppeln. Falls Discovery trotz Host-Netzwerk nicht funktioniert, LAN/VLAN und Firewall prüfen oder die IP manuell verwenden.
2. Inventar, Fähigkeiten und Icons prüfen. Einlesen allein schaltet keine Lampe.
3. Erst für einen gewollten Steuerungstest auf dem SERVER öffnen:

```sh
sudo nano /opt/hue2lox-test/.env
```

Diese vorhandenen Zeilen von `0` auf `1` ändern:

```text
HUE_WRITES_ENABLED=1
HUE_COLOR_ENABLED=1
HUE_WHITE_ENABLED=1
```

In nano: **Ctrl+O**, Enter zum Speichern; **Ctrl+X** zum Schließen. Anschließend:

```sh
sudo docker compose --project-directory /opt/hue2lox-test --env-file /opt/hue2lox-test/.env -f /opt/hue2lox-test/compose.yaml up -d
```

4. Eine Testlampe auswählen; gleichzeitige Steuerung durch die bestehende Anlage vermeiden. Befehle/XML nach der [Loxone-Anleitung](docs/TUTORIAL.de.md) einrichten.
5. Mit `sudo docker compose --project-directory /opt/hue2lox-test --env-file /opt/hue2lox-test/.env -f /opt/hue2lox-test/compose.yaml restart` neu starten. Kopplung, geändertes Passwort und gespeicherte Einstellungen müssen erhalten bleiben. Erneute Anmeldung kann nötig sein.

Weitere Prüfpunkte: [Abnahmeplan](docs/ACCEPTANCE.md). Der Linux-Test bestätigt noch keine frische LoxBerry-Installation.

## Stoppen und erneut starten

**SERVER:**

```sh
sudo docker compose --project-directory /opt/hue2lox-test --env-file /opt/hue2lox-test/.env -f /opt/hue2lox-test/compose.yaml down
```

Die Testinstanz stoppt, ihre Dateien bleiben erhalten. Wieder starten:

```sh
sudo docker compose --project-directory /opt/hue2lox-test --env-file /opt/hue2lox-test/.env -f /opt/hue2lox-test/compose.yaml up -d
```

Vor Änderungen die gesamte Installation einschließlich `.env`, `data`, `certs` und `secrets` geschützt sichern. Backups enthalten Zugangsdaten und gehören nicht in GitHub. Für einen wirklich leeren Wiederholungstest den VM-Snapshot zurücksetzen oder eine neue getrennte Installation anlegen.

## Alternativen und Entwicklertests

[KI-Installationsprompt](docs/AI-INSTALL.de.md) · [English AI prompt](docs/AI-INSTALL.md).

Erfahrene Nutzer können statt ZIP einen separaten Git-Klon verwenden: Git mit `sudo apt install git` installieren, dann `git clone https://github.com/square-com-de/hue2lox.git`. Für den öffentlichen Download ist keine GitHub-Anmeldung nötig. Ab Schritt 7 im geklonten Repository fortfahren.

Für Entwickler, aus dem Quellordner mit Python, OpenSSL und Node.js (nicht für die normale Installation erforderlich):

```sh
python3 -m unittest discover -s tests -t . -p 'test_*.py'
python3 scripts/smoke-install.py
```

Diese automatischen Tests ersetzen nicht den echten Linux-/Docker-/Loxone-Test.

## Bestehende frische Testinstallation auf Host-Netzwerk umstellen

Nur für die nach dieser Anleitung angelegte Linux-Testinstallation `/opt/hue2lox-test`, **nicht** für den produktiven LoxBerry-Prototyp. Aktuelles ZIP in einen neuen Quellordner herunterladen und entpacken. Hier verwenden wir `~/hue2lox-source-neu/hue2lox-main`; bei einem anderen Ordner den Pfad anpassen. **Schritt 7 nicht wiederholen.** Token, Zertifikate und gespeicherte Einrichtung bleiben erhalten.

SERVER: Zuerst die bisherige Compose-Datei geschützt sichern:

```sh
HUE2LOX_NET_BACKUP=$(sudo mktemp -d /opt/hue2lox-network-backup-XXXXXXXX) &&
sudo cp -p /opt/hue2lox-test/compose.yaml "$HUE2LOX_NET_BACKUP/compose.yaml" &&
printf 'Sicherung: %s/compose.yaml\n' "$HUE2LOX_NET_BACKUP"
```

Diese Umstellung setzt bereits die Verzeichnisstruktur mit `src/` und `docker/` im Installationsziel voraus. Für ältere Installationen einschließlich RC1 die Anleitung der installierten Version verwenden; nicht nur eine Compose-Datei aus einer neueren Version übernehmen.

Bei Fehler stoppen. Dann den bisherigen Container stoppen, ausschließlich die neue Compose-Datei übernehmen und mit dem geprüften Startskript starten:

```sh
test -f /opt/hue2lox-test/docker/Dockerfile.status &&
test -f /opt/hue2lox-test/src/app.py &&
test -f "$HOME/hue2lox-source-neu/hue2lox-main/docker/compose.install.yaml" &&
test -f "$HOME/hue2lox-source-neu/hue2lox-main/scripts/start-install.py" &&
sudo docker compose --project-directory /opt/hue2lox-test --env-file /opt/hue2lox-test/.env -f /opt/hue2lox-test/compose.yaml down &&
sudo install -m 644 "$HOME/hue2lox-source-neu/hue2lox-main/docker/compose.install.yaml" /opt/hue2lox-test/compose.yaml &&
sudo python3 "$HOME/hue2lox-source-neu/hue2lox-main/scripts/start-install.py" --destination /opt/hue2lox-test
```

Erfolg erst bei `Installation ready`. Die bisherige Webadresse bleibt unverändert. Danach im Webinterface **Bridges → Hue Bridges suchen** testen. Eine erfolgreiche Containerprüfung bestätigt noch nicht, dass Multicast im jeweiligen LAN funktioniert.

Zurück zum vorherigen Netzwerkmodus: die gesicherte `compose.yaml` nach `/opt/hue2lox-test/compose.yaml` zurückkopieren und das Startskript erneut ausführen. Den ausgegebenen Sicherungspfad verwenden. Die Datenordner weder löschen noch überschreiben.

## Zertifikat prüfen und optional dauerhaft vertrauen

Wenn du Option 1 als Root ausgeführt hast, bei den folgenden Serverbefehlen `sudo` weglassen. Bei einem anderen Installationsziel die Pfade anpassen.

Das lokal erzeugte Zertifikat ist dem Browser noch nicht bekannt. Auf dem **SERVER** den Fingerabdruck ablesen:

```sh
sudo openssl x509 -in /opt/hue2lox-test/certs/server.crt -noout -fingerprint -sha256
```

Mit dem Zertifikat vergleichen, das der Browser für diese Adresse anzeigt. Nach erfolgreichem Vergleich für einen vorübergehenden Test eine angebotene Browser-Ausnahme nutzen. Nicht die Zertifikatsprüfung des gesamten Browsers deaktivieren.

Für dauerhaftes Vertrauen das **öffentliche Zertifikat** kopieren, im **MAC-Terminal**:

```sh
scp anna@192.0.2.50:/opt/hue2lox-test/health-test.crt ~/Downloads/hue2lox-test.crt
```

`health-test.crt` ist eine Kopie des öffentlichen Serverzertifikats. In der macOS-Schlüsselbundverwaltung importieren, Fingerabdruck prüfen und für SSL als vertrauenswürdig einstellen. Browser neu öffnen. Niemals `certs/server.key` weitergeben. Jede Installation erzeugt eigene Zertifikate; diese gelten 365 Tage und müssen rechtzeitig erneuert werden. HTTPS mit dem Miniserver prüfen wir separat.

## Fehlerbehebung

### Zurück zu Schritt 7: falsche IP, auch nach dem Containerstart

Dieser Rückweg gilt für die **frische Testinstallation dieser Anleitung**, solange noch keine Bridge gekoppelt und keine Einrichtung gespeichert wurde. Er stoppt nur das in diesem Installationsordner konfigurierte Compose-Projekt. Bei bereits eingerichteten Geräten oder abweichenden Pfaden zuerst den Zustand prüfen, statt die Einrichtung zurückzusetzen.

**SERVER – im SSH-Terminal.** Zuerst den Testcontainer stoppen und entfernen. Die Installationsdateien bleiben erhalten:

```sh
sudo docker compose --project-directory /opt/hue2lox-test --env-file /opt/hue2lox-test/.env -f /opt/hue2lox-test/compose.yaml down
```

Das funktioniert auch, wenn der Start wegen der falschen IP gescheitert ist oder noch kein Container läuft. **Bei einem Fehler hier stoppen.** Nicht den Docker-Dienst abschalten und kein `docker system prune` verwenden: Andere Container sollen weiterlaufen.

Danach aus dem Installationsordner herauswechseln und die fehlerhafte Vorbereitung unter einem eindeutigen Namen sichern:

```sh
cd ~
HUE2LOX_BACKUP=$(sudo mktemp -d /opt/hue2lox-test-backup-XXXXXXXX) &&
sudo mv -T /opt/hue2lox-test "$HUE2LOX_BACKUP/installation" &&
printf 'Alte Vorbereitung gesichert unter: %s/installation\n' "$HUE2LOX_BACKUP"
```

Erst bei erfolgreicher Sicherungsmeldung weitergehen. Jetzt **zurück in den entpackten Quellordner**, nicht in den alten Installationsordner:

```sh
cd ~/hue2lox-source/hue2lox-main
ls scripts/prepare-install.py docker/compose.install.yaml
```

Beide Dateien müssen erscheinen. Falls du ein Commit-ZIP oder einen anderen Quellordner verwendet hast, den Pfad entsprechend anpassen; `ls ~/hue2lox-source` zeigt die vorhandenen Unterordner.

**Nun den Abfrageblock aus Schritt 7 mit der richtigen VM-IP erneut ausführen, danach Schritt 8.** Das ZIP muss nicht erneut entpackt und Docker nicht erneut installiert werden. Die neue Vorbereitung erzeugt neue Zertifikate und einen neuen Token. Eventuell bereits eingerichtetes Zertifikatsvertrauen muss danach aktualisiert werden. Die Sicherung enthält die bisherigen privaten Dateien und gehört nicht in GitHub.

Nur die IP in `.env` zu ändern reicht wegen des Zertifikats nicht. Falls der Installationsordner bereits verschoben wurde, die obigen Befehle nicht blind wiederholen: zuerst den tatsächlichen Ordner und Containerzustand klären.

### Der Start schlägt fehl

Auf dem Server kannst du den Zustand und die letzten Meldungen anzeigen:

```sh
sudo docker compose --project-directory /opt/hue2lox-test --env-file /opt/hue2lox-test/.env -f /opt/hue2lox-test/compose.yaml ps
sudo docker compose --project-directory /opt/hue2lox-test --env-file /opt/hue2lox-test/.env -f /opt/hue2lox-test/compose.yaml logs --tail=60
```

Wenn du Hilfe brauchst, nenne den Schritt und die Fehlermeldung. Zugangsdaten vor dem Teilen entfernen.

### Dauerhafter Installationsname

Neue Installationen speichern `COMPOSE_PROJECT_NAME` und `HUE2LOX_CONTAINER_NAME`
in ihrer `.env`. Der Container heißt zum Beispiel `hue2lox-jollyjumper-1`.
Diese Datei bei Updates behalten: Starten, Neustarten und erneutes Bauen erzeugen
keinen neuen Namen. Der Vorbereitungsassistent überschreibt bestehende Installationen
nicht. Ältere Installationen behalten ihren bisherigen Projektnamen `hue2lox-test`.
Bei Wartungsbefehlen immer die Compose-Datei und `.env` der gewünschten Installation
verwenden; keinen festen Projektnamen mit `-p` darüberlegen.

## Maintenance / Wartung

[Certificate renewal, IP change, backup and restore / Zertifikat, IP-Wechsel und Sicherung](docs/MAINTENANCE.de.md)
