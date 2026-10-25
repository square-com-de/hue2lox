# Hue2Lox installieren

[English](INSTALL.md)

Wähle einen der drei Wege. Für Container wird kein Hue2Lox-Installer benötigt; der geführte Installer ist der Einstieg für die native Installation.

| Weg | Verwendung | Anleitung |
| --- | --- | --- |
| Docker | Empfohlen auf einem Linux-Server mit Docker Engine und Compose. | [Docker starten](docs/CONTAINER-SETUP.de.md#schnellstart-docker-auf-einem-linux-server) |
| Podman | Container mit dauerhaftem Volume; Desktop-Netzwerkgrenzen beachten. | [Podman starten](docs/DOCKER.md#podman-desktop-on-macos) |
| Nativ | Experimentell, systemd und ausdrücklich geprüfte amd64-Systeme. | [Nativer Installer](#nativer-installer) |

## HTTP oder HTTPS?

Docker-/Podman-Images starten ohne TLS-Variablen mit **HTTP**, auch am internen Port 8443. Der Docker-Schnellstart veröffentlicht `http://SERVER-IP:18443`. Nativ richtet der Installer **HTTPS mit einem selbstsignierten Zertifikat** ein. Bei **Traefik** spricht der Browser HTTPS und Traefik intern HTTP zu Hue2Lox. `HUE_PUBLIC_URL` allein aktiviert kein TLS. [Konfigurationsort und vollständiges Traefik-Beispiel](docs/CONTAINER-SETUP.de.md#http-oder-https).

## Nativer Installer

Voraussetzungen: Debian 12/13, Ubuntu 24.04/26.04 oder DietPi auf Debian 12/13, **amd64**, systemd, Rootzugriff. ARM/Raspberry Pi OS sind nativ derzeit nicht freigegeben. [Details und Wartung](docs/INSTALL-NATIVE.md).

Auf dem Linux-Server zuerst `su -` ausführen und das Rootpasswort eingeben (Ubuntu alternativ `sudo -i`). **Erst danach** die folgenden Befehle in der Root-Shell ausführen. Der Downloadordner darf noch nicht existieren.

```sh
apt update &&
apt install -y --no-install-recommends ca-certificates curl unzip python3 openssl &&
mkdir /root/hue2lox-native-1.0.2 &&
cd /root/hue2lox-native-1.0.2 &&
curl --fail --location --output hue2lox-v1.0.2.zip https://github.com/square-com-de/hue2lox/releases/download/v1.0.2/hue2lox-v1.0.2.zip &&
curl --fail --location --output hue2lox-1.0.2-native.tar.gz https://github.com/square-com-de/hue2lox/releases/download/v1.0.2/hue2lox-1.0.2-native.tar.gz &&
curl --fail --location --output SHA256SUMS.txt https://github.com/square-com-de/hue2lox/releases/download/v1.0.2/SHA256SUMS.txt &&
grep '  hue2lox-v1.0.2.zip$' SHA256SUMS.txt | sha256sum --check - &&
grep '  hue2lox-1.0.2-native.tar.gz$' SHA256SUMS.txt | sha256sum --check - &&
unzip -q hue2lox-v1.0.2.zip &&
cd hue2lox-v1.0.2 &&
bash install-assistant.sh --deployment native \
  --native-package /root/hue2lox-native-1.0.2/hue2lox-1.0.2-native.tar.gz \
  --native-sha256 "$(sha256sum /root/hue2lox-native-1.0.2/hue2lox-1.0.2-native.tar.gz | cut -d ' ' -f1)"
```

Beide Dateien müssen vor dem Start `OK` anzeigen. Im Menü Voraussetzungen prüfen, Grundpakete bei Bedarf installieren, Paket prüfen und nativ mit der LAN-IP des Servers sowie einem freien Port installieren. Die ausgegebene HTTPS-Adresse öffnen, Zertifikatsfingerabdruck prüfen, mit `admin/admin` anmelden und das Passwort ändern. Erhaltene Daten behalten das bisherige Passwort.

## Bestehende Installation

Keine Neuinstallation zum Aktualisieren verwenden. [Docker-Update und Rollback](docs/UPDATE-DOCKER.de.md) · [Native Wartung, Rollback und Datenerhalt](docs/INSTALL-NATIVE.md#aktualisieren-und-rückweg). Vorhandene Docker-Installer-Installationen werden weiter über ihren dokumentierten Wartungsweg betreut.
