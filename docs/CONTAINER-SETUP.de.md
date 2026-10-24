# Container einrichten: Anmeldung, Speicher, Netzwerk und HTTPS

Bevorzugter Weg: **Docker Compose innerhalb einer Linux-VM**, etwa auf Proxmox. [Belegter Runtime-Status](RUNTIME-SUPPORT.de.md); die neu angeforderte saubere Proxmox-Abnahme ist noch offen und wird nicht durch den Mac-Podman-Test ersetzt.

[English](CONTAINER-SETUP.md) · [Container-Anleitung](DOCKER.md) · [Linux-Installer](../INSTALL.de.md)

Diese Hinweise gelten für das veröffentlichte Hue2Lox-Image ab **1.0.1**. Sie unterscheiden einen schnellen Desktop-Test vom dauerhaften Betrieb. Ein Image-Download allein aktualisiert keinen vorhandenen Container.

## Vor dem Start

| Einstellung | Was eintragen? |
|---|---|
| Image | `docker.io/dubctrl/hue2lox:1.0.1` oder `ghcr.io/square-com-de/hue2lox:1.0.1` |
| Speicher | Benanntes Volume `hue2lox-data` → Containerpfad `/data`, schreibbar |
| Port | Linux-Compose: Dienst direkt auf Host-Port `18443` (Host-Netzwerk); Desktop-Portmapping separat konfigurieren |
| Browser | Ohne TLS zunächst `http://SERVER-IP:18443`; auf demselben Computer auch `http://localhost:18443` |
| Erste Anmeldung | `admin` / `admin` bei neuen Daten; anschließend Passwort in der Oberfläche ändern |
| Browseradresse | Für direkte localhost/private-IP-Zugriffe keine `HUE_PUBLIC_URL` nötig; bei eigenem DNS-Namen/Reverse Proxy die genaue Browseradresse setzen |

**Portnummern aktivieren kein HTTPS.** Auch Port 8443 spricht ohne TLS-Konfiguration HTTP. `localhost` meint immer den Computer, auf dem der Browser läuft; ein Loxone-Miniserver benötigt eine von ihm erreichbare Serveradresse.

## Schnellstart mit Docker Compose auf Linux

Voraussetzung: Docker Engine und Compose-Plugin laufen auf deiner Linux-VM; Port **18443** ist frei. Die [Compose-Datei dieses Checkouts](../docker/compose.image.yaml) als **compose.yaml** in einem neuen eigenen Ordner speichern. In diesem Ordner ausführen (bei fehlenden Docker-Rechten mit `su -` zu root wechseln und anschließend wieder in diesen Ordner gehen):

```sh
docker compose up -d --wait
docker compose ps
```

**http://SERVER-IP:18443** mit der tatsächlichen LAN-IP der Linux-VM öffnen, mit **admin/admin** anmelden und Passwort ändern. Der Container muss gesund sein; zusätzlich den Browserlogin prüfen. Speicher wird automatisch angelegt, keine Ordnerrechte oder Browseradresse nachtragen. Für Updates denselben Ordner/Projektnamen und dasselbe Volume behalten.

Dieses Profil verwendet unverschlüsseltes HTTP im vertrauenswürdigen LAN. Für HTTPS den geführten Installer oder die TLS-/Proxy-Einrichtung unten verwenden. Automatische Suche kann durch VLANs/Firewall begrenzt sein; direkter Bridge-Zugriff bleibt eine eigene Prüfung. Diese überarbeitete Vorlage benötigt noch die Clean-VM-Abnahme und ist nicht die unveränderte Datei aus dem veröffentlichten `v1.0.1`-Archiv.

## Wo bleiben meine Daten?

Das Image schreibt seine Daten nach **`/data`**: unter anderem Bridge-Registry und Kopplungsdaten, Admin-Zugangsdaten (Passworthash), Steuerungstoken und gespeicherte Einstellungen. Nicht nur eine einzelne Datei sichern, sondern das gesamte Volume. Separat eingebundene TLS-Dateien und Deployment-Konfiguration ebenfalls sichern.

Das Image deklariert `VOLUME /data`. Wenn du nur Start drückst und keinen Speicher auswählst, erzeugt die Engine normalerweise ein **anonymes Volume** mit zufälligem Namen. Die Daten sind also nicht zwangsläufig weg, wenn du den Container stoppst oder neu startest. Ein neu erstellter Container verwendet dieses Volume aber nicht automatisch. Dann sieht die Anwendung trotz noch vorhandener alter Daten wie eine Neuinstallation aus. Volume-Löschen, Bereinigung und automatische Entfernung können diese Daten endgültig entfernen.

Für dauerhaften Betrieb ein **benanntes Volume** verwenden und bei Updates erneut dasselbe Volume an `/data` einhängen. Niemals zwei Hue2Lox-Instanzen gleichzeitig auf dieselben Daten schreiben lassen. Ein Volume ersetzt kein Backup.

### Portainer (Docker Standalone)

1. Die **Docker-Standalone-Umgebung auf dem Linux-Server** auswählen, dann **Stacks → Add stack** öffnen; Stackname `hue2lox`.
2. Die [Compose-Datei dieses Checkouts](../docker/compose.image.yaml) vollständig in den Webeditor kopieren und **Deploy the stack** wählen. Port **18443** muss frei sein. Kein zusätzliches Volume und keine Portfreigabe anlegen: die Datei enthält Speicher und Linux-Host-Netzwerk bereits.
3. **http://SERVER-IP:18443** mit der LAN-IP dieses Docker-Servers öffnen. Frische Daten: **admin/admin**, danach Passwort ändern. Das ist HTTP im vertrauenswürdigen LAN; für HTTPS siehe unten.
4. Unter **Inspect → Mounts** prüfen: `Destination: /data`, Typ `volume`, `RW: true`. Container muss gesund sein; Browserlogin zusätzlich prüfen.

Bei Updates denselben Stack und dessen Volume behalten. Ein anderer Stackname kann einen neuen Datenbestand erzeugen. Die Daten liegen auf dem **Docker-Server der ausgewählten Umgebung**, nicht auf dem Browser-PC. Das ist kein Swarm- oder Docker-Desktop-Profil. Die genaue Portainer-Oberfläche und dieser aktualisierte Stackweg benötigen noch eine unabhängige Abnahme; die Compose-Datei des veröffentlichten Tags `v1.0.1` bleibt unverändert.

### Podman Desktop und eigener Ordner

Bei Podman Desktop auf macOS/Windows lebt ein verwaltetes Volume in der **Podman-Linux-VM**, nicht automatisch in deinem Dokumente-Ordner. Die VM nicht zurücksetzen/löschen, ohne die Daten vorher zu sichern. Für einen ausdrücklich benannten Speicher kann der [Podman-Befehl](DOCKER.md#podman-desktop-on-macos) verwendet werden.

Ein eigener Host-Ordner ist optional: beispielsweise `/srv/hue2lox/data:/data`. Auf einem Linux-Server den Ordner vorher anlegen und für UID/GID **10001:10001** schreibbar machen. Kein `chmod 777`. Bei SELinux müssen zusätzlich passende Mount-Labels gesetzt werden; bei Desktop-VMs gelten deren Freigabe- und Berechtigungsregeln. Ein benanntes Volume vermeidet die manuelle Ordnerberechtigung.

## Vom Linux-Installer angelegte Installation

Der Docker-Installer legt im gewählten Installationsordner `data/`, `secrets/` und bei direktem HTTPS `certs/` an und bindet sie über Compose ein. Diese Ordner sowie `.env`, Compose-Konfiguration und das bisherige Image zusammen sichern. Der Download-/Entpackordner ist nicht automatisch der Datenordner. Für nativ gelten andere Pfade: siehe [native Installation](INSTALL-NATIVE.md).

## Anmeldung

`admin/admin` gilt nur, wenn im eingebundenen Datenbestand noch keine Zugangsdaten existieren. Ein schon geändertes Passwort bleibt bei Neustart, Update und Wiederverwendung des Volumes erhalten. `HUE2LOX_ADMIN_PASSWORD` ist ebenfalls nur ein Startwert für neue Zugangsdaten, kein Passwort-Reset.

Bei „Browseradresse passt nicht zur Serverkonfiguration“ die genaue URL einschließlich `http`/`https` und Port mit `HUE_PUBLIC_URL` vergleichen. Variablen stehen bei Portainer in der Container-/Stack-Konfiguration, bei Podman Desktop beim Erstellen unter **Environment variables**, in Compose unter `environment`. Änderungen an der Container-Konfiguration erfordern meist ein Neuerstellen mit demselben Datenvolume. Nicht die Daten löschen, um einen Adressfehler zu beheben.

## HTTP oder HTTPS?

- **Lokaler Test über HTTP:** Keine TLS-Variablen setzen. Der Browser verwendet `http://...`. Zugangsdaten sind auf dieser Verbindung unverschlüsselt; nur im passenden vertrauenswürdigen Testnetz verwenden.
- **HTTPS über Traefik oder anderen Reverse Proxy:** Der Proxy verwaltet das Browser-Zertifikat und leitet intern an Hue2Lox-HTTP weiter. In Hue2Lox `HUE_PUBLIC_URL=https://hue2lox.example.de` auf die echte Adresse setzen. Der Proxy muss den ursprünglichen `Host`-Header weitergeben. Im Container `TLS_CERT` und `TLS_KEY` weglassen. Kein Zertifikatsschlüssel muss in diesem Fall in den Hue2Lox-Container.
- **HTTPS direkt in Hue2Lox:** Zertifikat und Schlüssel schreibgeschützt einbinden, z. B. unter `/certs`. `TLS_CERT=/certs/server.crt` und `TLS_KEY=/certs/server.key` setzen. Beide Dateien müssen für Container-UID 10001 lesbar sein; der Schlüssel bleibt privat. Das Zertifikat muss zur verwendeten Adresse passen, vom Client als vertrauenswürdig anerkannt und rechtzeitig erneuert werden. Der Linux-Installer bietet die direkte Zertifikatseinrichtung an; ein selbstsigniertes Zertifikat wird nicht automatisch von jedem Browser vertraut.

Beide TLS-Variablen setzen oder beide weglassen. Leere Werte sind keine Deaktivierung; unvollständige Konfiguration führt zum Startfehler. Nach Zertifikatstausch muss der Dienst das neue Zertifikat laden, etwa durch Neustart.

**Das Zertifikat der Hue Bridge ist ein anderes Thema.** Hue2Lox bringt die Hue-CA zur Prüfung der Bridge-Verbindung mit. Für eine fehlgeschlagene Bridge-Suche weder Zertifikatsprüfung deaktivieren noch Browserzertifikate austauschen.

## Bridge-Suche und direkter Zugriff sind zwei verschiedene Tests

- **Automatische Suche** verwendet lokales Multicast (mDNS UDP 5353 und SSDP UDP 1900). Antworten müssen den Container erreichen. Beim Docker-Installer/Compose auf einem Linux-Host wird Host-Netzwerk verwendet; auch dort können VLANs, Gastnetz oder Firewall die Suche begrenzen.
- **Manuelles Hinzufügen** benötigt eine direkte Netzwerkroute zur Bridge-IP. Die HTTP-/HTTPS-Verbindung zur Bridge (TCP 80/443, je nach Prüfschritt) muss aus dem Container erreichbar sein. Ein veröffentlichter GUI-Port allein stellt das nicht sicher.
- **Podman Desktop auf Mac/Windows** verwendet eine Linux-VM. Die Bridge-Suche aus dieser VM kann scheitern, obwohl manueller Zugriff funktioniert. `host` bedeutet dort nicht automatisch das physische Mac-/Windows-LAN. Funktionierender Browser-Login beweist noch keinen Bridge-Zugriff.

Wenn nur die Suche scheitert: die lokale Suchhilfe in **Bridges** auf dem Computer ausführen oder die Bridge-IP im Router ablesen und manuell eintragen. Keine Onlinedienste nötig.

Wenn auch die manuelle IP scheitert: genaue Fehlermeldung sichern und Erreichbarkeit derselben IP vom Host **und** aus dem Container vergleichen. VPN, Gast-WLAN, VLAN-Routing, VM-Netz und lokale Netzwerkfreigaben/Firewall prüfen. Nur erforderliche Verbindungen erlauben, nicht pauschal die Firewall abschalten. Ein Zertifikats- oder Kopplungsfehler bei erreichbarer Bridge ist gesondert zu untersuchen. Eine manuelle IP-Eingabe umgeht keine Netzwerksperre.

## Update und Kontrolle

Vor dem Update Datenvolume, Konfiguration, eigene Zertifikate und bisheriges Image sichern. Neues Image mit **demselben** Volume starten; nicht `down -v` verwenden. Danach vorhandenes Passwort, Bridge-Inventar und gespeicherte Einstellungen prüfen. Details: [Update und Wiederherstellung](UPDATE-DOCKER.de.md).

Quellen: [Docker-Volumes](https://docs.docker.com/engine/storage/volumes/), [Podman-Machine](https://podman-desktop.io/docs/podman/creating-a-podman-machine).
